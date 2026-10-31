"""
Cassette recording and replay.

Every real completion is recorded with its pins and its exact prompt. That buys
three things:

  * **Deterministic replay of real model output.** T0 can drive the plumbing with
    completions an actual model produced, rather than ones I invented — the
    difference matters, because hand-written scripts encode my assumptions about
    what a model does, and cassettes encode what one actually did.
  * **Prompt iteration without spending model time.** Editing a *validator* or a
    parser and re-running against cassettes is instant.
  * **Evidence.** "This case passed on this prompt with this model" is a claim
    you can re-check later instead of a memory.

Cassettes live in `.rota/dev.db`, a **separate file** from the framework
database. That separation is not fussiness: T0-S1 asserts a failed session leaves
zero rows in any table, and instrumentation sharing the artefact store would make
that assertion ambiguous. Artefacts are the system's world; cassettes are ours.

Keying: (model, temperature, num_ctx, system, user) hashed. Change the prompt and
you get a miss, which is correct — a recording made against a different prompt is
not evidence about this one.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from .llm import Backend, Completion, LLMUnavailable, Pins

DEV_SCHEMA = """
CREATE TABLE IF NOT EXISTS cassettes (
    key          TEXT PRIMARY KEY,
    model        TEXT NOT NULL,
    temperature  REAL NOT NULL,
    num_ctx      INTEGER NOT NULL,
    prompt_hash  TEXT NOT NULL,
    system       TEXT NOT NULL,
    user         TEXT NOT NULL,
    completion   TEXT NOT NULL,
    tool_calls   TEXT NOT NULL DEFAULT '[]',   -- native calls, as JSON
    backend      TEXT NOT NULL,
    hits         INTEGER NOT NULL DEFAULT 0,
    done_reason  TEXT NOT NULL DEFAULT ''      -- why the stream stopped
);

-- Pass-rate history per (case, model, prompt version). A case that passed 5/5
-- for weeks and now passes 3/5 is a prompt regression signal, so the history is
-- itself an artefact rather than a number printed once and lost.
CREATE TABLE IF NOT EXISTS case_runs (
    case_id      TEXT NOT NULL,
    model        TEXT NOT NULL,
    prompt_hash  TEXT NOT NULL,
    run_no       INTEGER NOT NULL,
    -- Which residency of the model produced this run: model @ two-hour
    -- window. Ollama's determinism is per-load, so two recording passes
    -- hours apart are different experiments and the register must be able
    -- to say so. '' is a run from before the column existed.
    load_id      TEXT NOT NULL DEFAULT '',
    passed       INTEGER NOT NULL,
    problems     TEXT NOT NULL DEFAULT '[]',
    -- What the model actually said and did, kept with the verdict on it.
    -- A pass rate tells you a case is failing; only the transcript tells you
    -- whether the case was unfair, the role under-briefed, or the model out of
    -- its depth -- which is the whole of the remaining work.
    transcript   TEXT NOT NULL DEFAULT '[]',
    -- The rest of the cassette key, so a reader can ask whether a result is
    -- still evidence about what the tree sends today (frame 54, 2026-09-21).
    -- A recording is keyed by seven things and a result was keyed by three, so
    -- the report could not match what the key covers. One narrow key gives two
    -- opposite symptoms: a green case reads stale, and a case the suite cannot
    -- replay reads green.
    num_ctx      INTEGER NOT NULL DEFAULT 12288,
    temperature  REAL NOT NULL DEFAULT 0.0,
    -- Text or native. Native tool calling and the `TOOL:` text protocol get
    -- different replies to one prompt, so a native recording is not evidence
    -- about a text run.
    protocol     TEXT NOT NULL DEFAULT 'text',
    -- The optional pins that are set, as `Pins.extras()` builds them. `think`
    -- is the live one.
    extras       TEXT NOT NULL DEFAULT '{}',
    -- The whole system text the model received, hashed. `prompt_hash` covers
    -- the composed brief only: the runner's session prose and the working
    -- set's `TOOL:` lines sit outside it, and both move the cassette key.
    system_hash  TEXT NOT NULL DEFAULT '',
    -- Whether a call reached the model, and the clock at the write (frame 66,
    -- 2026-09-23). The register held 167,844 copies and 2,591 first-seen
    -- transcripts, and no reader could tell the two apart: a replay under a
    -- new load looked like a second experiment and `trust` banked it.
    live         INTEGER NOT NULL DEFAULT 0,
    at           TEXT NOT NULL DEFAULT '',
    seq          INTEGER NOT NULL,
    PRIMARY KEY (case_id, model, prompt_hash, run_no, seq)
);

-- A look that measured nothing (frame 64, 2026-09-22). A replay that finds no
-- cassette at the current key wrote nothing at all, so the report read the
-- older rows and the case read green while the suite could not replay it. The
-- miss is not a run and it does not go in `case_runs`: every reader of that
-- table reads it as "what has been measured". The row carries the whole key
-- the run tried, so a reader can ask whether the last look tried the key the
-- tree composes now.
CREATE TABLE IF NOT EXISTS key_misses (
    case_id      TEXT NOT NULL,
    model        TEXT NOT NULL,
    prompt_hash  TEXT NOT NULL,
    run_no       INTEGER NOT NULL,
    system_hash  TEXT NOT NULL,
    num_ctx      INTEGER NOT NULL,
    temperature  REAL NOT NULL,
    protocol     TEXT NOT NULL,
    extras       TEXT NOT NULL,
    load_id      TEXT NOT NULL,
    -- `no cassette` or `unreachable`, and the problem string that carries the
    -- marker. `at` is the clock, because a miss is an observation and an
    -- observation ages.
    kind         TEXT NOT NULL,
    reason       TEXT NOT NULL,
    at           TEXT NOT NULL,
    seq          INTEGER NOT NULL,
    -- The shape of `case_runs`'s own key, and the index the reader walks.
    -- `seq` alone would refuse the second insert when two xdist workers
    -- allocate one number, and the gate would count a new red.
    PRIMARY KEY (case_id, model, prompt_hash, run_no, seq)
);
"""

#: The five columns frame 54 adds, and the value an old row takes. A default
#: is a write-off and not a measurement: every row written before 2026-09-21
#: reads as 12288, 0.0, text and no extras, and its system text is unknown.
KEY_COLUMNS = (
    ("num_ctx", "INTEGER NOT NULL DEFAULT 12288"),
    ("temperature", "REAL NOT NULL DEFAULT 0.0"),
    ("protocol", "TEXT NOT NULL DEFAULT 'text'"),
    ("extras", "TEXT NOT NULL DEFAULT '{}'"),
    ("system_hash", "TEXT NOT NULL DEFAULT ''"),
)

#: The two columns frame 66 adds, a sibling of `KEY_COLUMNS` and never inside
#: it. `casestatus.carries_the_key` tests the whole of `KEY_COLUMNS` against
#: the schema, so a register that carries the five and not these two would
#: read as unkeyed, in silence (frame 66's design review, finding 5).
#: An old row keeps `live = 0`: it is a run of unknown provenance, and 0 says
#: so rather than claiming a call that nobody can prove.
LIVE_COLUMNS = (
    ("live", "INTEGER NOT NULL DEFAULT 0"),
    ("at", "TEXT NOT NULL DEFAULT ''"),
)


def open_dev_db(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), isolation_level=None)
    conn.row_factory = sqlite3.Row
    # Autocommit with the default rollback journal cost a journal create and
    # two fsyncs per recorded turn -- measured maxing out the spinning drive
    # for a whole recording pass. WAL batches the syncs; NORMAL is safe here
    # because this database is evidence, re-earnable by re-recording, not the
    # artefact store the durability rules exist for.
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.executescript(DEV_SCHEMA)
    # `CREATE TABLE IF NOT EXISTS` will not add a column to a table that already
    # exists, and this database is committed — so a schema that grows has to say
    # how the recordings already in the repository catch up.
    have = {r["name"] for r in conn.execute("PRAGMA table_info(case_runs)")}
    if "transcript" not in have:
        conn.execute("ALTER TABLE case_runs ADD COLUMN transcript TEXT "
                     "NOT NULL DEFAULT '[]'")
    if "load_id" not in have:
        # Which residency of the model produced the run. Temp-0 is stable
        # within a model load and not across (measured), so a score is a fact
        # about a load -- and the register could not say which. '' is every
        # run recorded before the column existed: one indistinct old load.
        conn.execute("ALTER TABLE case_runs ADD COLUMN load_id TEXT "
                     "NOT NULL DEFAULT ''")
    # The cassette key's own fields. SQLite adds a column without rewriting
    # the table, so the five cost 0.004 seconds in total (observed: the design
    # review's probe 11, 2026-09-21). Nothing is backfilled here: one UPDATE
    # over 178901 rows takes 4.72 seconds against sqlite3's 5.0 second busy
    # timeout, and `pytest.ini` runs the suite with `-n auto`, so a second
    # worker opening this database would raise `database is locked`.
    for column, spec in KEY_COLUMNS:
        if column not in have:
            conn.execute(f"ALTER TABLE case_runs ADD COLUMN {column} {spec}")
    # Whether the run reached the model, and when. The same loop and the same
    # reasoning as the five above: no backfill, and the default is the true
    # statement about a row nobody measured (frame 66, 2026-09-23).
    for column, spec in LIVE_COLUMNS:
        if column not in have:
            conn.execute(f"ALTER TABLE case_runs ADD COLUMN {column} {spec}")
    _reason_column(conn)
    return conn


def _reason_column(conn: sqlite3.Connection) -> None:
    """Give an older `cassettes` table its `done_reason` column, and move a
    night file's `done_reasons` side table onto the column.

    One store holds the stop reason, so a replay through any backend fires
    the rules the live call fired (frame 233). The ALTER adds the column
    with no rewrite. `pytest.ini` runs `-n auto`, so a second worker can add
    the column first, and its duplicate is no fault."""
    held = {r["name"] for r in conn.execute("PRAGMA table_info(cassettes)")}
    if "done_reason" not in held:
        try:
            conn.execute("ALTER TABLE cassettes ADD COLUMN done_reason TEXT "
                         "NOT NULL DEFAULT ''")
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e):
                raise
    if not conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' "
                        "AND name = 'done_reasons'").fetchone():
        return
    # The copy and the drop go in one transaction, so a crash between them
    # leaves the side table whole for the next open.
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute(
            "UPDATE cassettes SET done_reason = (SELECT d.done_reason FROM "
            "done_reasons d WHERE d.key = cassettes.key) "
            "WHERE key IN (SELECT key FROM done_reasons)")
        conn.execute("DROP TABLE done_reasons")
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise


#: The stop reasons a cassette row stores. The runner reads `length` at the
#: cut note of `run_session` and `invented_result` at its stream line.
#: `llm.py` sets `repeating`, and no reader reads it yet. Any other reason,
#: Ollama's `stop` included, is the plain end, and the row stores "".
STORED_REASONS = ("length", "invented_result", "repeating")

#: The one read of a cassette row. Both replay backends read the row here.
_ROW = ("SELECT completion, backend, tool_calls, done_reason FROM cassettes "
        "WHERE key = ?")


def _replayed(row: sqlite3.Row, pins: Pins) -> Completion:
    """The completion of one cassette row. The stop reason goes back into
    `raw`, where the live backend puts it, so `Completion.done_reason` reads
    a replay as it reads a live call (frame 233)."""
    reason = row["done_reason"] or ""
    return Completion(text=row["completion"], pins=pins,
                      backend=f"cassette:{row['backend']}",
                      tool_calls=_calls_from(row["tool_calls"]),
                      raw={"done_reason": reason} if reason else {})


def stored_reason(result: Completion) -> str:
    """The `done_reason` value of a recording of `result`."""
    reason = result.done_reason
    return reason if reason in STORED_REASONS else ""


def mark_reason(conn: sqlite3.Connection, key: str, reason: str) -> int:
    """Set the stop reason of the row `key` when the row holds none, and
    return the count of rows changed. The night seed infers a cut from the
    next prompt, so the seed writes the reason here (frame 233, pass 4b)."""
    if reason not in STORED_REASONS:
        raise ValueError(f"{reason!r} is not a stored stop reason")
    return conn.execute(
        "UPDATE cassettes SET done_reason = ? WHERE key = ? AND done_reason = ''",
        (reason, key)).rowcount


def key_for(system: str, user: str, pins: Pins, protocol: str = "text",
            tools: list | None = None) -> str:
    """
    A recording is evidence about one prompt, one model, and one *protocol*.

    Native tool calling and the `TOOL:` text protocol produce different replies
    to the same prompt and fail in different ways. Keying them together would
    let a text-protocol recording answer for a native run, which is not evidence
    about it.
    """
    # The original six fields make the blob every existing recording was
    # keyed by. An optional pin that is set joins as a seventh element, so
    # a recording made under the provider's defaults keeps its key and a
    # recording made under a set pin gets its own.
    fields: list = [pins.model, pins.temperature, pins.num_ctx, protocol, system, user]
    extras = pins.extras()
    if extras:
        fields.append(extras)
    # The schemas a native run offered. The prompt text does not hold them,
    # so a schema change replayed an old native recording (frame 323). A
    # text key never takes this element, so no text key moves.
    if protocol == "native" and tools:
        offered = json.dumps(tools, sort_keys=True)
        fields.append({"tools": hashlib.sha256(
            offered.encode("utf-8")).hexdigest()[:16]})
    blob = json.dumps(fields, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32]




def _calls_to(calls) -> str:
    """Native calls, as JSON. A cassette that dropped them would replay an empty
    completion — with native tool calling the text is usually blank and every
    instruction is in the structure."""
    return json.dumps([{"name": c.name, "args": c.args} for c in calls or []])


def _calls_from(blob: str):
    from .llm import NativeCall

    return [NativeCall(name=c["name"], args=c["args"])
            for c in json.loads(blob or "[]")]


@dataclass
class Tally:
    """
    What the model tiers cost, measured rather than remembered.

    "How long do the cassettes take" had no answer anywhere: neither table
    carries a duration, so the one number you need in order to decide whether a
    prompt edit is affordable was a thing people repeated from memory. It was
    being quoted as 27 minutes, from a file that had also drifted 129 tests.

    Kept per machine and never committed, in `.rota-timings.json` beside
    `.rota-coverage.json`, which is where instrumentation already lives. A
    duration is a fact about this GPU on this day at this thermal state, and
    writing it into the same database as the recordings would make it look like
    evidence about the prompts. One run's number answers "how long will this
    take"; the series answers the better question, which is whether it is
    getting slower.
    """

    replays: int = 0
    records: int = 0
    replay_seconds: float = 0.0
    record_seconds: float = 0.0

    def merge(self, other: dict) -> None:
        self.replays += other.get("replays", 0)
        self.records += other.get("records", 0)
        self.replay_seconds += other.get("replay_seconds", 0.0)
        self.record_seconds += other.get("record_seconds", 0.0)

    def as_dict(self) -> dict:
        return {"replays": self.replays, "records": self.records,
                "replay_seconds": round(self.replay_seconds, 2),
                "record_seconds": round(self.record_seconds, 2)}

    def save(self, model: str = "", keep: int = 40) -> None:
        """Append this run, keeping the recent tail. Never fails a test run."""
        from .. import paths

        if not (self.records or self.replays):
            return
        try:
            path = paths.TIMINGS_FILE
            runs = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
            if not isinstance(runs, list):
                runs = []
            runs.append({"model": model, "when": time.strftime("%Y-%m-%d %H:%M"),
                         **self.as_dict()})
            path.write_text(json.dumps(runs[-keep:], indent=1), encoding="utf-8")
        except (OSError, ValueError):                       # pragma: no cover
            pass

    @staticmethod
    def previous() -> dict | None:
        """The last recorded run, for an estimate before this one starts."""
        from .. import paths

        try:
            runs = json.loads(paths.TIMINGS_FILE.read_text(encoding="utf-8"))
            return next((r for r in reversed(runs) if r.get("records")), None)
        except (OSError, ValueError):
            return None

    def line(self) -> str:
        parts = []
        if self.records:
            each = self.record_seconds / self.records
            parts.append(f"{self.records} recorded in "
                         f"{_clock(self.record_seconds)} ({each:.1f}s each)")
        if self.replays:
            rate = self.replays / self.replay_seconds if self.replay_seconds else 0
            parts.append(f"{self.replays} replayed in "
                         f"{_clock(self.replay_seconds)} ({rate:,.0f}/s)")
        return "cassettes: " + ", ".join(parts) if parts else ""


def _clock(seconds: float) -> str:
    if seconds < 90:
        return f"{seconds:.1f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m{s:02d}s" if m < 60 else f"{m // 60}h{m % 60:02d}m"


TALLY = Tally()


class RecordingBackend:
    """
    Wraps a real backend and records everything it returns.

    On a hit it replays instead of calling out, so a re-run of a green suite
    costs nothing. Pass `refresh=True` to force live calls and overwrite.
    """

    name = "recording"

    def __init__(self, inner: Backend, dev_conn: sqlite3.Connection,
                 *, replay: bool = True, refresh: bool = False):
        self.inner = inner
        self.conn = dev_conn
        self.replay = replay
        self.refresh = refresh
        self.hits = 0
        self.misses = 0

    def complete(self, system: str, user: str, pins: Pins,
                 tools: list | None = None) -> Completion:
        protocol = "native" if tools else "text"
        key = key_for(system, user, pins, protocol, tools)

        started = time.perf_counter()
        if self.replay and not self.refresh:
            row = self.conn.execute(_ROW, (key,)).fetchone()
            if row:
                self.hits += 1
                TALLY.replays += 1
                TALLY.replay_seconds += time.perf_counter() - started
                self.conn.execute(
                    "UPDATE cassettes SET hits = hits + 1 WHERE key = ?", (key,))
                return _replayed(row, pins)

        self.misses += 1
        started = time.perf_counter()
        result = self.inner.complete(system, user, pins, tools=tools)
        TALLY.records += 1
        TALLY.record_seconds += time.perf_counter() - started
        self.conn.execute(
            "INSERT OR REPLACE INTO cassettes "
            "(key, model, temperature, num_ctx, prompt_hash, system, user, "
            " completion, tool_calls, backend, hits, done_reason) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,0,?)",
            (key, pins.model, pins.temperature, pins.num_ctx, pins.prompt_hash,
             system, user, result.text, _calls_to(result.tool_calls),
             result.backend, stored_reason(result)),
        )
        return result


class ReplayOnlyBackend:
    """
    Cassettes or nothing.

    Used where a test must never touch a model: a miss is a hard failure rather
    than a silent fallback, because a suite that quietly calls out when its
    recording is stale is no longer deterministic and will fail differently on
    someone else's machine.
    """

    name = "replay"

    def __init__(self, dev_conn: sqlite3.Connection):
        self.conn = dev_conn

    def complete(self, system: str, user: str, pins: Pins,
                 tools: list | None = None) -> Completion:
        started = time.perf_counter()
        key = key_for(system, user, pins, "native" if tools else "text", tools)
        row = self.conn.execute(_ROW, (key,)).fetchone()
        if row:
            TALLY.replays += 1
            TALLY.replay_seconds += time.perf_counter() - started
        if not row:
            raise LLMUnavailable(
                f"no cassette for {pins.model} key={key[:12]}… — record one with "
                f"RecordingBackend, or the prompt changed since it was made",
                replay_miss=True,
            )
        return _replayed(row, pins)


#: The two markers of a look that measured nothing, and the kind each one
#: names. One constant, because the rule had a second copy: the writer matched
#: both markers and `casestatus.matching_runs` matched one of them by hand.
#: Frame 60 and frame 54 both record what a second copy of a match costs.
#:
#: The order decides the kind. `ReplayOnlyBackend` raises `LLMUnavailable("no
#: cassette for ...")`, so a replay miss carries both markers, and a replay
#: never reaches a server. So `no cassette` is asked first and `unreachable`
#: names a stopped server only.
MISS_MARKERS = {"no cassette": "no cassette for", "unreachable": "LLMUnavailable"}


def _is_unmeasured(problems: list[str], transcript: list | None) -> bool:
    """
    A run that died for want of a cassette is not a result.

    `case_runs` is read as "what has been measured", by `casestatus` and by
    anyone asking whether a change cost a case. A replay with no recording
    against the current prompt measured nothing -- the role never spoke -- and
    writing it down as `passed = 0` turns an unmeasured case into a hard red
    that looks exactly like a regression. Editing five `answer.md` files
    produced five of those in one run, and the whole reason `casestatus` exists
    is that stale read as failing once before.

    Matched on the message rather than the exception type because the failure
    reaches here as text, having already been caught and recorded by the
    session that hit it.
    """
    # A model that could not be reached measured nothing either. Found when a
    # recording pass ran against a stopped ollama and wrote ten hard-looking
    # reds -- every one a connection refused, not a role getting it wrong.
    return _miss_of(problems, transcript) is not None


#: The transcript's key for the session's own error lines. A marker is read
#: from these lines and from `problems`, and never from the model's prose: a
#: role that writes the word `LLMUnavailable` in an answer is talking about a
#: failure, and that run measured the role (observed: frame 64's diff review,
#: 2026-09-22).
ERRORS_KEY = "errors"


def _looked_at(problems: list[str], transcript: list | None) -> list[str]:
    """The lines a marker may be read from, in the order they are asked."""
    lines = list(problems)
    for item in transcript or []:
        if isinstance(item, dict):
            lines += [str(error) for error in item.get(ERRORS_KEY) or []]
    return lines


def _miss_of(problems: list[str], transcript: list | None) -> tuple[str, str] | None:
    """
    The kind and the reason of a look that measured nothing, or None.

    The reason is the line that carries the marker, and not `problems[0]`.
    `check` writes its complaints first and `session did not commit: [...]`
    last, so the first problem is `expected a call to X` and never the miss.
    A case that expects no commit carries the marker in its error lines alone.
    """
    lines = _looked_at(problems, transcript)
    for kind, marker in MISS_MARKERS.items():
        for line in lines:
            if marker in line:
                return kind, line
    return None


def current_load(pins: Pins) -> str:
    """Model plus two-hour window: the coarse name of one residency.

    Coarse on purpose. The true boundary is ollama unloading the model, which
    nothing here can see; two passes inside one window very likely share a
    residency (keep_alive holds the model warm between them), and passes
    hours apart very likely do not. A pass straddling a window edge reads as
    two loads, which errs toward demanding the extra confirmation.
    """
    import time

    return f"{pins.model}@{int(time.time()) // 7200}"


#: The system text of a session that died before `build_prompt` ran. `''`
#: already means "written before the column existed", so a crash needed a
#: third value: a row reading `unbuilt` measured nothing, and a row reading
#: `''` is a legacy write-off (frame 54's fix pass, 2026-09-21). Without it
#: the two are one value and a reader cannot tell a crash from history.
UNBUILT = "unbuilt"


def system_hash(system: str) -> str:
    """
    The whole system text the model received, hashed.

    `prompt_hash` is not this, and the difference is the fault frame 54
    repairs. `prompt_hash` covers the composed brief, which
    `fixtures.instructions_for` rebuilds from the tree. The brief is a strict
    prefix of the system text for 117 of the suite's 117 single-session cases,
    and exact for none (observed: frame 54's measurement over the register,
    2026-09-21). The tail is the runner's session prose and the working set's
    `TOOL:` lines. Both move the cassette key, and both leave `prompt_hash`
    alone, so a tools edit made a case read green that the suite could no
    longer replay.

    '' means the writer had no system text to give. The migration leaves the
    same '' on every row written before the column existed, so '' reads as
    unknown and never as "the model was sent nothing".

    `UNBUILT` passes through as itself rather than as a digest, so a crash
    before the prompt was built reads as a crash. A digest of the word would
    look like a measurement of a real system text.
    """
    if system == UNBUILT:
        return UNBUILT
    if not system:
        return ""
    return hashlib.sha256(system.encode("utf-8")).hexdigest()[:16]


#: One counter across both tables, read inside the insert that uses it.
#: `key_misses` and `case_runs` share it, so "newer" is a comparison on `seq`
#: and never on the clock. The allocation is one statement, so SQLite holds
#: the write lock while the maximum is read: two statements race, and four
#: xdist workers writing the live register allocated one number twice
#: (observed: the design review's probe, 2026-09-22).
_NEXT_SEQ = ("(SELECT COALESCE(MAX(s), 0) + 1 FROM "
             "(SELECT MAX(seq) AS s FROM case_runs "
             "UNION ALL SELECT MAX(seq) FROM key_misses))")


def record_case_run(conn: sqlite3.Connection, case_id: str, pins: Pins,
                    run_no: int, passed: bool, problems: list[str],
                    transcript: list | None = None, *, live: bool,
                    system: str = "", protocol: str = "text") -> None:
    """
    One run of one case, with the whole key it was earned under.

    `system` is the system text the model received, not the composed brief.
    `protocol` is `'text'` or `'native'`, and it is the caller's because the
    pins do not carry it: the runner offers native schemas per session.

    Both are keyword-only. A caller that has no system text gets '' and says
    so, rather than passing a brief that is only a prefix of what was sent.

    `live` says whether a call reached the model, and it has no default. Every
    caller must answer, because a copy and a first-seen transcript are the
    same fourteen columns and the register could not tell them apart (frame
    66, 2026-09-23). `at` is the clock here, as `key_misses` writes it: a run
    is an observation and an observation ages.

    A run that measured nothing writes one `key_misses` row and no `case_runs`
    row. The look is evidence about the key and never about the role, so the
    two live in two tables (frame 64, 2026-09-22).
    """
    key = (case_id, pins.model, pins.prompt_hash, run_no,
           current_load(pins), pins.num_ctx, pins.temperature, protocol,
           json.dumps(pins.extras(), sort_keys=True), system_hash(system))
    miss = _miss_of(problems, transcript) if not passed else None
    if miss is not None:
        # The look is written down and the run is not. A `passed = 0` row
        # would turn an unmeasured case into a hard red that looks exactly
        # like a regression, and that is what the guard exists to stop.
        kind, reason = miss
        conn.execute(
            "INSERT INTO key_misses (case_id, model, prompt_hash, run_no, "
            "load_id, num_ctx, temperature, protocol, extras, system_hash, "
            f"kind, reason, at, seq) SELECT ?,?,?,?,?,?,?,?,?,?,?,?,?,{_NEXT_SEQ}",
            (*key, kind, reason, time.strftime("%Y-%m-%dT%H:%M:%S")),
        )
        return
    conn.execute(
        "INSERT INTO case_runs (case_id, model, prompt_hash, run_no, "
        "load_id, num_ctx, temperature, protocol, extras, system_hash, "
        "passed, problems, transcript, live, at, seq) "
        f"SELECT ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,{_NEXT_SEQ}",
        (*key, int(passed), json.dumps(problems), json.dumps(transcript or []),
         int(live), time.strftime("%Y-%m-%dT%H:%M:%S")),
    )


def flip_history(conn: sqlite3.Connection, case_id: str,
                 bar: float = 0.8) -> list[dict]:
    """
    The case's verdict per (prompt, load) group, oldest first, with flips.

    Derived, never stored -- the runs are the record and this is a reading of
    them. A group's verdict is the register's own bar (4 of 5). A flip is a
    verdict differing from the previous group's, whatever changed in between:
    a prompt edit, a fresh load, or nothing visible at all -- the last kind
    is the chronically marginal case this exists to make visible.

    Live rows only (frame 66, 2026-09-23). A replay under a new `load_id` is
    not a second experiment, and the 2026-08-27 ruling asks for two loads. A
    group is now the live runs of one load, so the bar reads real runs.
    """
    rows = conn.execute(
        "SELECT prompt_hash, load_id, MIN(seq) AS first_seq, COUNT(*) AS n, "
        "       SUM(passed) AS ok "
        "FROM case_runs WHERE case_id = ? AND live = 1 "
        "GROUP BY prompt_hash, load_id ORDER BY first_seq", (case_id,)).fetchall()
    out, prev = [], None
    for r in rows:
        verdict = (r["ok"] / r["n"]) >= bar
        out.append({"prompt_hash": r["prompt_hash"], "load_id": r["load_id"],
                    "runs": r["n"], "passed": r["ok"], "verdict": verdict,
                    "flip": prev is not None and verdict != prev})
        prev = verdict
    return out


def trust(conn: sqlite3.Connection, case_id: str) -> str:
    """
    'earned', 'provisional', 'red', or 'unmeasured' -- the ruling
    (2026-08-27): a case that flips red to green counts as fixed only after
    passing on two separate loads. A green that never flipped is earned on
    one: it has no history of being wrong to live down.
    """
    groups = flip_history(conn, case_id)
    if not groups:
        return "unmeasured"
    latest = groups[-1]
    if not latest["verdict"]:
        return "red"
    if not latest["flip"]:
        return "earned"
    # Only the trailing green streak confirms: a green load from *before*
    # the red is the flip-flop itself, not evidence the fix took.
    confirming = set()
    for g in reversed(groups):
        if not g["verdict"]:
            break
        confirming.add(g["load_id"])
    return "earned" if len(confirming) >= 2 else "provisional"


def provisional_cases(conn: sqlite3.Connection) -> list[str]:
    """The greens the register may not bank yet."""
    ids = [r["case_id"] for r in conn.execute(
        "SELECT DISTINCT case_id FROM case_runs ORDER BY case_id")]
    return [c for c in ids if trust(conn, c) == "provisional"]


def pass_rate_history(conn: sqlite3.Connection, case_id: str) -> list[dict]:
    """Pass rate per (model, prompt_hash), newest first. The regression signal.

    Live rows only, as `flip_history` reads them (frame 66, 2026-09-23). A
    rate over copies counts one reply many times.
    """
    return [dict(r) for r in conn.execute(
        "SELECT model, prompt_hash, COUNT(*) AS runs, SUM(passed) AS passed, "
        "       MAX(seq) AS last_seq "
        "FROM case_runs WHERE case_id = ? AND live = 1 "
        "GROUP BY model, prompt_hash ORDER BY last_seq DESC", (case_id,))]
