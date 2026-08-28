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
    hits         INTEGER NOT NULL DEFAULT 0
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
    seq          INTEGER NOT NULL,
    PRIMARY KEY (case_id, model, prompt_hash, run_no, seq)
);
"""


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
    return conn


def key_for(system: str, user: str, pins: Pins, protocol: str = "text") -> str:
    """
    A recording is evidence about one prompt, one model, and one *protocol*.

    Native tool calling and the `TOOL:` text protocol produce different replies
    to the same prompt and fail in different ways. Keying them together would
    let a text-protocol recording answer for a native run, which is not evidence
    about it.
    """
    blob = json.dumps(
        [pins.model, pins.temperature, pins.num_ctx, protocol, system, user],
        sort_keys=True,
    )
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
        key = key_for(system, user, pins, protocol)

        started = time.perf_counter()
        if self.replay and not self.refresh:
            row = self.conn.execute(
                "SELECT completion, backend, tool_calls FROM cassettes "
                "WHERE key = ?", (key,)).fetchone()
            if row:
                self.hits += 1
                TALLY.replays += 1
                TALLY.replay_seconds += time.perf_counter() - started
                self.conn.execute(
                    "UPDATE cassettes SET hits = hits + 1 WHERE key = ?", (key,))
                return Completion(
                    text=row["completion"], pins=pins,
                    backend=f"cassette:{row['backend']}",
                    tool_calls=_calls_from(row["tool_calls"]))

        self.misses += 1
        started = time.perf_counter()
        result = self.inner.complete(system, user, pins, tools=tools)
        TALLY.records += 1
        TALLY.record_seconds += time.perf_counter() - started
        self.conn.execute(
            "INSERT OR REPLACE INTO cassettes "
            "(key, model, temperature, num_ctx, prompt_hash, system, user, "
            " completion, tool_calls, backend, hits) VALUES (?,?,?,?,?,?,?,?,?,?,0)",
            (key, pins.model, pins.temperature, pins.num_ctx, pins.prompt_hash,
             system, user, result.text, _calls_to(result.tool_calls),
             result.backend),
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
        key = key_for(system, user, pins, "native" if tools else "text")
        row = self.conn.execute(
            "SELECT completion, backend, tool_calls FROM cassettes WHERE key = ?",
            (key,)
        ).fetchone()
        if row:
            TALLY.replays += 1
            TALLY.replay_seconds += time.perf_counter() - started
        if not row:
            raise LLMUnavailable(
                f"no cassette for {pins.model} key={key[:12]}… — record one with "
                f"RecordingBackend, or the prompt changed since it was made"
            )
        return Completion(text=row["completion"], pins=pins,
                          backend=f"cassette:{row['backend']}",
                          tool_calls=_calls_from(row["tool_calls"]))


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
    haystack = " ".join(problems) + json.dumps(transcript or [])
    # A model that could not be reached measured nothing either. Found when a
    # recording pass ran against a stopped ollama and wrote ten hard-looking
    # reds -- every one a connection refused, not a role getting it wrong.
    return "no cassette for" in haystack or "LLMUnavailable" in haystack


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


def record_case_run(conn: sqlite3.Connection, case_id: str, pins: Pins,
                    run_no: int, passed: bool, problems: list[str],
                    transcript: list | None = None) -> None:
    if not passed and _is_unmeasured(problems, transcript):
        return
    seq = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) + 1 n FROM case_runs").fetchone()["n"]
    conn.execute(
        "INSERT INTO case_runs (case_id, model, prompt_hash, run_no, passed, "
        "problems, transcript, seq, load_id) VALUES (?,?,?,?,?,?,?,?,?)",
        (case_id, pins.model, pins.prompt_hash, run_no, int(passed),
         json.dumps(problems), json.dumps(transcript or []), seq,
         current_load(pins)),
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
    """
    rows = conn.execute(
        "SELECT prompt_hash, load_id, MIN(seq) AS first_seq, COUNT(*) AS n, "
        "       SUM(passed) AS ok "
        "FROM case_runs WHERE case_id = ? "
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
    """Pass rate per (model, prompt_hash), newest first. The regression signal."""
    return [dict(r) for r in conn.execute(
        "SELECT model, prompt_hash, COUNT(*) AS runs, SUM(passed) AS passed, "
        "       MAX(seq) AS last_seq "
        "FROM case_runs WHERE case_id = ? "
        "GROUP BY model, prompt_hash ORDER BY last_seq DESC", (case_id,))]
