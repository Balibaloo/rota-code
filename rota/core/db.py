"""
Database access and the atomic session commit.

Law 4: a session emits its writes, messages and receipt, and all of it commits in
one SQLite transaction — or the session never happened. That is enforced here,
not by convention: `session_commit()` is the only sanctioned write path, and it
either lands everything or rolls back everything.

Two things are deliberately *not* atomic with it, and both are documented rather
than hidden:

  * git. The Developer commits into a worktree; those commits are outside the
    transaction. The database therefore *lags* the codebase, and boot reconciles
    the two (batches.head_commit vs the worktree's actual HEAD).
  * spawned processes. Recorded in runtime_processes so boot can reap orphans.
"""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from .. import paths
from typing import Any, Iterator

SCHEMA_PATH = paths.SCHEMA

# Which tables back which graph artefact.
#
# The graph speaks in artefacts ("model", "brief"); the schema speaks in tables
# ("constraints", "statements"). Receipts are written against tables, and the
# cascade walks the graph — so the two vocabularies must be bound somewhere, and
# this is the only place they are. A table missing from here has no artefact, so
# writes to it produce no receipt and trigger no cascade: that is correct for
# runtime bookkeeping and wrong for anything else.
TABLES_OF_ARTEFACT: dict[str, tuple[str, ...]] = {
    "transcript": ("entries",),
    "brief":      ("statements",),
    "problem":    ("items",),
    "glossary":   ("glossary_terms", "business_rules"),
    "model":      ("constraints", "constraint_bindings", "model_areas"),
    "frame":      ("frame_rulings",),
    "challenge":  ("challenges",),
    # Also not part of `model`, and for a second reason beyond the cascade.
    # Onboarding runs three roles over every area and each has to record its own
    # pass, which under `model` meant three writers on Architect's artefact --
    # so only Architect could attest, and `tick_survey`, which waits for a row
    # per role, woke the other two for the same area forever.
    "surveys":    ("survey_records", "survey_citations"),
    # Not part of `model`. A finding is a verdict on a batch, and binding it to
    # the model meant one *satisfied* finding -- a clean review saying nothing
    # is wrong -- cascaded as though the system model had changed, waking the
    # whole delivery chain including the role that had just written it.
    "findings":   ("findings",),
    # The Liaison's reading of a principal reply. Its own artefact: one
    # writer, one row per reply, landed mechanically after the commit.
    "rulings":    ("rulings",),
    "tickets":    ("tickets",),
    "criteria":   ("criteria",),
    "batches":    ("batches", "batch_tickets", "batch_dep_facts", "batch_touch",
                   "touch_strays"),
    "tests":      ("tests",),
    "ledger":     ("ledger",),
    "decisions":  ("decisions",),
    "verdicts":   ("verdicts",),
    # The Researcher's whole artefact, and the only one it may write. A row here
    # is inert until a role that owns something cites it, which is what makes
    # "the internet cannot widen the model" structural rather than a rule.
    "references": ("references_",),
    # "code" is git, not a table: the DB lags it and boot reconciles the two.
    # "schedule" is derived by the scheduler, so it carries no receipts.
    # "web" is the world: unwritable by anything in this system, which is why it
    # is read through one contained role rather than a tool on five.
}

ARTEFACT_OF_TABLE: dict[str, str] = {
    table: artefact
    for artefact, tables in TABLES_OF_ARTEFACT.items()
    for table in tables
}

# Tables that carry artefact state. Writes to these bump artefact_versions and
# generate receipts; everything else (runtime bookkeeping) does not.
ARTEFACT_TABLES = set(ARTEFACT_OF_TABLE)

# One relation, several writers. A refs row records what a source row rests
# on, and it belongs to the artefact of that source row. So `refs` is not in
# `TABLES_OF_ARTEFACT`: a write to it carries `src_table` and `src_id` in its
# values, and the receipt goes under that row. The cascade, the ruling relay
# and the writer check then see the source artefact and never the relation.
REFS_TABLE = "refs"

# The view that derives provenance for each owner table (frame 21). A
# reader joins the view on the row id. The owner tables carry no provenance
# column: the refs relation is the only record of what a row rests on.
PROVENANCE_VIEW_OF_TABLE = {
    "items": "item_provenance",
    "glossary_terms": "term_provenance",
    "constraints": "constraint_provenance",
    "model_areas": "area_provenance",
    "frame_rulings": "frame_provenance",
}

# The kind of ref that names a row of each table. The cascade walk follows
# a receipt on one of these tables to the rows whose refs name the row.
REF_KIND_OF_TABLE = {
    "statements": "statement",
    "references_": "reference",
    "glossary_terms": "term",
    "rulings": "ruling",
}


def shown_provenance(provenance: str, basis: str) -> str:
    """The word a result shows for a derived provenance.

    Today's word: `cited` for a row that rests on the world. The view says
    `observed` with `basis = 'world'` for that row. Stage 4 decides the
    rendered word."""
    return "cited" if basis == "world" else provenance


def receipt_of(w: "Write") -> tuple[str, str]:
    """The (table, row id) a write is receipted under.

    A refs write is receipted under its source row. The row's own write and
    its refs writes in one commit bump the version once, in any order:
    `session_commit` bumps once per receipt key."""
    if w.table == REFS_TABLE:
        return (str(w.values.get("src_table", "")),
                str(w.values.get("src_id", "")))
    return w.table, w.row_id


def connect(path: str | Path) -> sqlite3.Connection:
    db_path = Path(path).expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def connect_readonly(path: str | Path) -> sqlite3.Connection:
    """Open the database in read-only mode for the cockpit and other viewers."""
    db_path = Path(path).expanduser().resolve()
    conn = sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA query_only = ON")
    return conn


# The schema marker (frame 21). `init_db` writes it when it creates the
# tables. A run database from before the refs relation has the owner tables
# and no marker. Opened, it would read every gate as reasoned, so the door
# refuses it. Run databases are throwaway.
SCHEMA_KEY = "schema"
SCHEMA_MARK = "refs"
SCHEMA_STALE = ("the run database predates the refs relation, so it needs "
                "a fresh run: wipe it, or onboard under a new name")


def schema_stale(conn: sqlite3.Connection) -> str | None:
    """The sentence that refuses a database from before the refs relation.
    None for an empty database and for one that carries the marker and no
    provenance column."""
    tables = {r["name"] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    if "items" not in tables:
        return None
    # A database from the stages that wrote the column beside the relation
    # carries the marker too. The column is the second sign, beside the
    # marker: a run wrote its stamps there and its refs may be partial.
    if _has_column(conn, "items", "provenance"):
        return SCHEMA_STALE
    if "config" in tables and conn.execute(
            "SELECT 1 FROM config WHERE key = ? AND value = ?",
            (SCHEMA_KEY, SCHEMA_MARK)).fetchone():
        return None
    return SCHEMA_STALE


def open_for_viewing(path: str | Path) -> tuple[sqlite3.Connection, str | None]:
    """A connection for a viewer, and a note.

    A current database opens through `init_db`. A database from before the
    refs relation opens read-only, and the note is the sentence `init_db`
    refuses it with. The cockpit is how an old night run is read: a viewer
    shows the run and says the sentence. Only a run refuses."""
    conn = connect(path)
    stale = schema_stale(conn)
    conn.close()
    if stale:
        return connect_readonly(path), stale
    return init_db(path), None


def init_db(path: str | Path) -> sqlite3.Connection:
    conn = connect(path)
    stale = schema_stale(conn)
    if stale:
        conn.close()
        raise RuntimeError(stale)
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.execute("INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)",
                 (SCHEMA_KEY, SCHEMA_MARK))
    return conn


class ReadonlyWriteError(RuntimeError):
    """A readonly session attempted a write.

    Raised as an ordinary tool error, not a session-fatal condition: the write is
    *unavailable*, and the model gets that back and carries on. Consult-mode
    sandboxes simply do not export writers, so this is the belt to that braces.
    """


@dataclass
class Write:
    table: str
    row_id: str
    values: dict[str, Any]
    op: str = "upsert"          # 'upsert' | 'update'
    # Whether this write is an *amendment* to the row's content.
    #
    # Only amendments move the per-row version, because the revocation predicate
    # compares an item's approval_ver against its version: if granting approval
    # bumped the version, approval could never postdate the last amendment and no
    # batch would ever be schedulable. Approval, priority and status transitions
    # are state changes, not content changes.
    amends: bool = True


@dataclass
class OutboundMessage:
    id: str
    to_role: str
    verb: str
    body_refs: list[str] = field(default_factory=list)
    # Empty on every channel but the one the graph declares `prose` on. See the
    # column comment in schema.sql: the Researcher shares no artefact with
    # anyone, so an id means nothing at its end.
    body_text: str | None = None
    cause_id: str | None = None
    cause_kind: str = "message"
    thread_id: str | None = None
    round_no: int = 0


@dataclass(frozen=True)
class Turn:
    """One model round-trip: what it was shown, and what it said.

    `seq` counts from 1 within the session, so a transcript reads in the order
    it happened without joining anything.
    """
    seq: int
    system: str
    user: str
    completion: str
    ms: int = 0


@dataclass
class SessionResult:
    """Everything one session produced. Committed together or not at all."""
    session_id: str
    role: str
    trigger_msg: str | None = None
    # What woke it, for the sessions no message woke. `trigger_msg` is null for
    # every tick, which in an onboarding run is every session.
    wake_kind: str = ""
    wake_detail: str = ""
    wake_refs: tuple[str, ...] = ()
    briefs_hash: str = ""
    mode: str = "normal"
    writes: list[Write] = field(default_factory=list)
    messages: list[OutboundMessage] = field(default_factory=list)
    tool_calls: list[tuple[str, str]] = field(default_factory=list)
    # The conversation itself. Empty is legal and means a database written
    # before this existed, or a session that never reached the model.
    turns: list[Turn] = field(default_factory=list)
    checkpoint: dict | None = None
    pins: dict = field(default_factory=dict)
    backend: str = ""               # the adapter that ran it: ollama, litellm, scripted
    # (label, message) for every call a guard threw out. Evidence, not noise:
    # the derived reask below turns on a refusal the session met after being
    # answered, and the commit is the one place session and database meet.
    refusals: list = field(default_factory=list)


def _next_seq(conn: sqlite3.Connection, table: str) -> int:
    row = conn.execute(f"SELECT COALESCE(MAX(seq), 0) + 1 AS n FROM {table}").fetchone()
    return int(row["n"])


def bump_version(conn: sqlite3.Connection, table: str) -> int:
    conn.execute(
        "INSERT INTO artefact_versions(table_name, version) VALUES (?, 1) "
        "ON CONFLICT(table_name) DO UPDATE SET version = version + 1",
        (table,),
    )
    row = conn.execute(
        "SELECT version FROM artefact_versions WHERE table_name = ?", (table,)
    ).fetchone()
    return int(row["version"])


def version_of(conn: sqlite3.Connection, table: str) -> int:
    row = conn.execute(
        "SELECT version FROM artefact_versions WHERE table_name = ?", (table,)
    ).fetchone()
    return int(row["version"]) if row else 0


# Junction tables have composite primary keys and no `id` column. Their Write
# row_id is a synthetic label used only to key the receipt.
JUNCTION_TABLES = {
    "batch_tickets", "constraint_bindings", "survey_citations",
    "batch_dep_facts", "schedule_deps", "batch_touch", "touch_strays", "refs",
}


def refs_of(raw) -> list[str]:
    """
    A message's refs, or nothing.

    `body_refs` is JSON on disk and the one column every reader loads. A row
    that does not parse -- a bit flipped, a write cut short -- used to raise
    where it was read: inside a session that was "session failed", retried to
    quarantine with the round never composed; inside `open_reports` it was the
    frontier, every tick, the scheduler dead on one bad row. Loop 2's second
    injury (`test_chaos_inquiry.py`). A corrupted message says nothing now,
    which is what it has: no refs, set aside, and the audit names it.
    """
    try:
        loaded = json.loads(raw or "[]")
    except (TypeError, ValueError):
        return []
    if not isinstance(loaded, list):
        return []
    return [x for x in loaded if isinstance(x, str)]


def _apply_ref(conn: sqlite3.Connection, w: Write) -> bool:
    """
    Write one refs row in place, or retire it. Returns False when the
    write changes no row.

    The same row again is not a change: no version moves, no receipt is
    written, and the row keeps its rowid. `criteria.load` reads term refs
    in rowid order, and `INSERT OR REPLACE` gives a row a new rowid. A row
    whose `resolves` flips is a change, updated in place. A write whose
    values carry `retire` deletes the row: a change when the row was on
    file, receipted under the source row.
    """
    key = tuple(str(w.values.get(c, ""))
                for c in ("src_table", "src_id", "kind", "target"))
    if w.values.get("retire"):
        gone = conn.execute(
            "DELETE FROM refs WHERE src_table = ? AND src_id = ? "
            "AND kind = ? AND target = ?", key).rowcount
        return gone > 0
    resolves = int(w.values.get("resolves", 1))
    row = conn.execute(
        "SELECT resolves FROM refs WHERE src_table = ? AND src_id = ? "
        "AND kind = ? AND target = ?", key).fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO refs (src_table, src_id, kind, target, resolves) "
            "VALUES (?, ?, ?, ?, ?)", (*key, resolves))
        return True
    if int(row["resolves"]) == resolves:
        return False
    conn.execute(
        "UPDATE refs SET resolves = ? WHERE src_table = ? AND src_id = ? "
        "AND kind = ? AND target = ?", (resolves, *key))
    return True


def _apply_write(conn: sqlite3.Connection, w: Write) -> bool:
    """Apply one write. Returns False when the write changes no row."""
    if w.table == REFS_TABLE:
        return _apply_ref(conn, w)
    if w.table in JUNCTION_TABLES:
        cols = list(w.values.keys())
        marks = ", ".join("?" for _ in cols)
        conn.execute(
            f"INSERT OR REPLACE INTO {w.table} ({', '.join(cols)}) VALUES ({marks})",
            list(w.values.values()),
        )
        return True

    exists = conn.execute(
        f"SELECT 1 FROM {w.table} WHERE id = ?", (w.row_id,)
    ).fetchone() is not None

    # Existing row -> UPDATE, not upsert. SQLite checks NOT NULL against the
    # *proposed* row before it detects the conflict, so an upsert carrying only
    # the changed columns fails on every NOT NULL column it omits. Amending one
    # field of a statement must not require restating all of them.
    if exists or w.op == "update":
        cols = list(w.values.keys())
        assignments = ", ".join(f"{c} = ?" for c in cols)
        # Per-row version: an amendment is what the revocation predicate compares
        # approval against, so it must move.
        if w.amends and _has_column(conn, w.table, "version") and "version" not in w.values:
            assignments += ", version = version + 1"
        conn.execute(
            f"UPDATE {w.table} SET {assignments} WHERE id = ?",
            [*w.values.values(), w.row_id],
        )
        return True

    payload = {"id": w.row_id, **w.values} if "id" not in w.values else dict(w.values)
    cols = list(payload.keys())
    placeholders = ", ".join("?" for _ in cols)
    conn.execute(
        f"INSERT INTO {w.table} ({', '.join(cols)}) VALUES ({placeholders})",
        list(payload.values()),
    )
    return True


def _has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    return any(r[1] == column for r in conn.execute(f"PRAGMA table_info({table})"))


def _thread_of(conn: sqlite3.Connection, m) -> str:
    """
    The thread a message joins: its cause's thread, not its cause.

    This was `m.thread_id or m.cause_id or m.id`, which is right exactly one hop
    from the root and wrong at every hop after it. The first reply's cause *is*
    the thread root, so it lands correctly and the bug is invisible; the second
    reply names its parent and starts a thread of one.

    Measured on the inquiry route, which was the first three-hop conversation
    the system ever had. Liaison asked Architect (`m6`, thread `m5`, correct),
    Architect answered (`m7`, thread `m6`, wrong), and when the asker said the
    answer had not landed, `unresolved` looked for roles that had spoken in
    `m6`'s thread, found none -- the answer was in a thread of its own -- and
    woke Architect again. Three times, then quarantine.

    Everything keyed on `thread_id` reads the same way: `report_is_settled`,
    `round_close`'s harvest, `open_tips`' broadcast exclusion, and the
    `answered` sweep below.
    """
    if m.thread_id:
        return m.thread_id
    if m.cause_id:
        row = conn.execute("SELECT thread_id FROM messages WHERE id = ?",
                           (m.cause_id,)).fetchone()
        if row and row["thread_id"]:
            return row["thread_id"]
        return m.cause_id
    return m.id


def _lift_quarantines(conn: sqlite3.Connection, w) -> None:
    """
    A quarantine holds while its subject is unchanged; a write that changes
    the subject is the exit.

    The never-delete rule is right for what it was written against -- a
    quarantine erasing its own evidence put icalendar through 131 sessions
    of one key -- but it had no "the world moved" case, so a repaired
    criterion could never wake the Tester that gave up on it: every S0 walk
    died permanently at its first quarantine even after the cause was
    fixed. A quarantined tick revives when a commit writes a row its refs
    name, or (for criteria and tests) writes into the batch its refs name,
    because those tables are what the batch-keyed ticks are about.
    """
    conn.execute(
        "DELETE FROM tick_attempts WHERE quarantined = 1 "
        "AND (tick_key LIKE ? OR tick_key LIKE ? OR tick_key LIKE ?)",
        (f"%|{w.row_id}", f"%|{w.row_id},%", f"%,{w.row_id}%"))
    # A new head commit is progress, and the bound is on dispatch *without*
    # progress. Walk seventeen: four, three, two tests failing across three
    # commits, and the third session was the quarantine -- the key
    # `developer|tick:tests_failing|b1` never changed, so the counter never
    # saw the loop working. The commit is the wake stopping being produced.
    fields = getattr(w, "values", None) or {}
    # A re-encoded test's runs describe a body that no longer exists. Walk
    # eighteen: the hold guard, the Developer's wake and the harness gate
    # all read the run of the old body after the new one landed.
    if w.table == "tests" and "body" in fields:
        conn.execute("DELETE FROM test_runs WHERE test_id = ?", (w.row_id,))
    if w.table == "batches" and "head_commit" in fields:
        conn.execute("DELETE FROM tick_attempts WHERE tick_key LIKE ?",
                     (f"%|tick:tests_failing|{w.row_id}",))
    if w.table in ("criteria", "tests"):
        if w.table == "criteria":
            batches = [r["batch_id"] for r in conn.execute(
                "SELECT DISTINCT bt.batch_id FROM batch_tickets bt "
                "JOIN criteria c ON c.ticket_id = bt.ticket_id "
                "WHERE c.id = ?", (w.row_id,))]
        else:
            batches = [r["batch_id"] for r in conn.execute(
                "SELECT batch_id FROM tests WHERE id = ?", (w.row_id,))]
        for b in batches:
            if b:
                conn.execute(
                    "DELETE FROM tick_attempts WHERE quarantined = 1 "
                    "AND tick_key LIKE ?", (f"%|{b}",))


def session_commit(conn: sqlite3.Connection, result: SessionResult) -> None:
    """
    Commit a whole session atomically: session row, writes, receipts, version
    bumps, outbound messages, tool-call log and checkpoint.

    A readonly session may produce reads and messages but no writes and no
    version bumps — asserted here so the isolation holds even if a sandbox is
    misconfigured.
    """
    if result.mode == "readonly" and result.writes:
        raise ReadonlyWriteError(
            f"readonly session {result.session_id} attempted "
            f"{len(result.writes)} write(s): {[w.table for w in result.writes]}"
        )

    try:
        conn.execute("BEGIN IMMEDIATE")

        conn.execute(
            "INSERT INTO sessions (id, role, trigger_msg, mode, committed, seq, "
            "model, temperature, num_ctx, prompt_hash, wake_kind, wake_detail, "
            "wake_refs, briefs_hash, pins_json, backend) "
            "VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                result.session_id, result.role, result.trigger_msg, result.mode,
                _next_seq(conn, "sessions"),
                result.pins.get("model"), result.pins.get("temperature"),
                result.pins.get("num_ctx"), result.pins.get("prompt_hash"),
                result.wake_kind, result.wake_detail,
                json.dumps(list(result.wake_refs)), result.briefs_hash,
                json.dumps(result.pins, sort_keys=True), result.backend or None,
            ),
        )

        for w in result.writes:
            changed = _apply_write(conn, w)
            table, row_id = receipt_of(w)
            if table not in ARTEFACT_TABLES or not changed:
                continue
            # One version bump per receipt key per commit, in any order of
            # the writes. A refs write is receipted under its source row:
            # beside the row's own write it adds nothing, and on its own it
            # changes what the row rests on.
            on_file = conn.execute(
                "SELECT 1 FROM receipts WHERE session_id = ? "
                "AND table_name = ? AND row_id = ?",
                (result.session_id, table, row_id)).fetchone()
            if on_file is None:
                new_version = bump_version(conn, table)
                conn.execute(
                    "INSERT INTO receipts "
                    "(session_id, table_name, row_id, new_version) "
                    "VALUES (?, ?, ?, ?)",
                    (result.session_id, table, row_id, new_version),
                )
            if w.table != REFS_TABLE:
                _lift_quarantines(conn, w)

        for m in result.messages:
            conn.execute(
                "INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, "
                "to_role, verb, body_refs, body_text, round_no, seq) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    m.id, m.cause_id, m.cause_kind,
                    _thread_of(conn, m),
                    result.role, m.to_role, m.verb,
                    json.dumps(m.body_refs), m.body_text,
                    m.round_no, _next_seq(conn, "messages"),
                ),
            )

        # A dead answer is picked up by somebody speaking in its thread.
        #
        # The same shape as the trigger rule below and for the same reason: the
        # escalation is discharged by what a session did, not by anyone
        # remembering to close it. Without this the climb walked itself -- the
        # rung answered, which made it a role that had spoken, which derived the
        # *next* rung, and one declaration would have toured the whole ladder
        # without the asker ever saying the second answer missed too.
        #
        # Not messages this role sent itself: the asker can send in its own
        # thread while still blocked, and that is not somebody picking it up.
        for thread in {_thread_of(conn, m) for m in result.messages}:
            conn.execute(
                "UPDATE messages SET status = 'answered' "
                "WHERE status = 'unresolved' AND thread_id = ? AND from_role != ?",
                (thread, result.role),
            )


        for turn in result.turns:
            conn.execute(
                "INSERT INTO turns (session_id, seq, system, user, completion, "
                "ms) VALUES (?, ?, ?, ?, ?, ?)",
                (result.session_id, turn.seq, turn.system, turn.user,
                 turn.completion, turn.ms))

        for i, (fn, args) in enumerate(result.tool_calls, start=1):
            conn.execute(
                "INSERT INTO tool_calls (session_id, fn, args_summary, seq) "
                "VALUES (?, ?, ?, ?)",
                (result.session_id, fn, args, i),
            )

        if result.checkpoint is not None:
            conn.execute(
                "INSERT OR REPLACE INTO checkpoints "
                "(session_id, role, batch_id, working_set, valid) "
                "VALUES (?, ?, ?, ?, 1)",
                (result.session_id, result.role,
                 result.checkpoint.get("batch_id"),
                 json.dumps(result.checkpoint.get("working_set", []))),
            )
        else:
            # A completed session releases its claim; a suspended one keeps it.
            conn.execute("DELETE FROM claims WHERE session_id = ?", (result.session_id,))

        # The trigger message is answered once its session commits -- unless
        # the trigger was already declared unresolved and the session produced
        # nothing. An unresolved question is somebody saying they are stuck;
        # a barren session has not unstuck them, and answering it anyway is
        # how a repair that declined silently killed the thread: the question
        # closed, the once-guard stopped the repair re-firing, and nothing
        # remained to carry it. Left unresolved, the ladder resumes.
        if result.trigger_msg:
            barren = not result.writes and not result.messages
            trig = conn.execute(
                "SELECT status, verb FROM messages WHERE id = ?",
                (result.trigger_msg,)).fetchone()
            was_unresolved = bool(trig and trig["status"] == "unresolved")
            if barren and trig and trig["verb"] == "challenge" and trig["status"] == "open":
                # A barren session on a challenge is not an answer to it.
                # clickI night 33 (2026-09-13): the Tester's every answer was
                # refused as carrying nothing, the session committed with
                # nothing, the challenge read as answered, the Developer was
                # woken by the same failing test with the same prompt and
                # challenged again -- three rounds to quarantine, and the
                # ladder never saw a question nobody had answered.
                conn.execute(
                    "UPDATE messages SET status = 'unresolved', unresolved_note = "
                    "COALESCE(unresolved_note, 'the session woken by it wrote "
                    "nothing and sent nothing') WHERE id = ?",
                    (result.trigger_msg,))
            elif not (barren and was_unresolved):
                conn.execute(
                    "UPDATE messages SET status = 'answered' WHERE id = ?",
                    (result.trigger_msg,),
                )
            # And a compose wake answers its whole round: the trigger was the
            # harvest's carrier, and its siblings were never addressed to a
            # session of their own. Left open they would tip one by one after
            # the reply went out, and Liaison would relay a round it had
            # already relayed.
            conn.execute(
                "UPDATE messages SET status = 'answered' "
                "WHERE status = 'open' AND verb = 'answer' "
                "  AND thread_id = (SELECT thread_id FROM messages WHERE id = ?) "
                "  AND EXISTS (SELECT 1 FROM messages q "
                "              WHERE q.id = (SELECT cause_id FROM messages "
                "                            WHERE id = ?) AND q.verb = 'ask') "
                "  AND cause_id IN (SELECT id FROM messages WHERE verb = 'ask')",
                (result.trigger_msg, result.trigger_msg),
            )

        # The question reached the person who asked it, which is what the end
        # of the ladder is for.
        #
        # The sweep above skips messages from the asker's own role -- right for
        # every role, because an asker sending in its own thread is not
        # somebody picking the question up. Liaison is the exception: when it
        # sends to the *principal*, the question has been picked up by the only
        # party left, and `predicates.unresolved` has always said so -- "by then
        # Liaison has sent, which means it is on the principal's agenda, and
        # that has a drain of its own". The drain was never written anywhere the
        # code could read, so the predicate saw the same state next pass and
        # woke Liaison again: three identical clarifications to the principal,
        # on seven of eight questions.
        if any(m.to_role == "principal" for m in result.messages):
            for thread in {_thread_of(conn, m) for m in result.messages}:
                conn.execute(
                    "UPDATE messages SET status = 'answered' "
                    "WHERE status = 'unresolved' AND thread_id = ? "
                    "  AND from_role = ?",
                    (thread, result.role),
                )

        # A demonstrated non-landing is a reask nobody has to declare.
        #
        # `schedule.reask` is a declaration because in general only the asker
        # knows the answer did not help. On one shape the evidence is complete
        # and public: this session was woken by the answer to its own
        # criteria-question, reached for `tests.encode` on that criterion, met
        # the parroting refusal again, and wrote no test. Asked, answered,
        # tried, same wall. Measured three delivery passes running: the Tester
        # takes every questioning exit and never the declaring one, so the
        # repair sat unreachable behind a sentence the model does not say.
        if result.trigger_msg and not any(
                w.table == "tests" for w in result.writes):
            # Both walls demonstrate the same thing. The semantic guard
            # ("own sentence written back") catches a restatement that
            # parses; the executable guard catches the commoner prose parrot
            # before it -- a body that is the criterion in English is not
            # Python, and pytest collects nothing from it. Either refusal on
            # this wake, with no test written, is the answer not landing.
            # Widened on walk eleven: the Tester, woken by the answer, met
            # the constant-assert wall ("assert True" under a criterion
            # that is not a behaviour) and the stdin wall, wrote nothing,
            # and asked again -- five answered questions, the criterion
            # untouched. Every encode refusal that can be met with the
            # answer in view is the answer not landing.
            # Keyed on the refusal's class, not its wording: every wall
            # `tests.encode` raises is an `api.Wall`, and the messages are
            # rewritten freely.
            parroted = any(
                (len(r) > 2 and r[2] == "Wall")
                for r in (result.refusals or []))
            if parroted:
                q = conn.execute(
                    "SELECT q.id AS qid, q.body_refs AS refs FROM messages a "
                    "JOIN messages q ON q.id = a.cause_id "
                    "WHERE a.id = ? AND a.verb = 'answer' "
                    "  AND q.verb IN ('question', 'ask') "
                    "  AND q.from_role = ?",
                    (result.trigger_msg, result.role)).fetchone()
                if q and any(
                        conn.execute("SELECT 1 FROM criteria WHERE id = ?",
                                     (ref,)).fetchone()
                        for ref in json.loads(q["refs"] or "[]")
                        if isinstance(ref, str)):
                    conn.execute(
                        "UPDATE messages SET status = 'unresolved', "
                        "  unresolved_note = COALESCE(unresolved_note, ?) "
                        "WHERE id = ?",
                        ("the answer did not change the criterion; encoding "
                         "it still parrots", q["qid"]))

        # "Cannot determine" becomes a report, and a report answering an
        # `ask` is the asker's declaration made by the answerer.
        #
        # Last, and that is the point rather than an ordering detail. Two
        # writes above mark a question settled -- the sweep, for somebody
        # new speaking in the thread, and the line directly above, for the
        # session committing at all. A report saying "not mine" trips both
        # and contradicts both, so it is the one reply that has to survive
        # them.
        #
        # `schedule.reask` has to be declared in general because the evidence
        # disagrees with the truth -- the row says answered and only the asker
        # knows it did not land. Here the *answerer* said so, in a verb that
        # means it, so the transition is derived. Without this an owner saying
        # "not mine" reached Liaison in `report` mode, whose brief opens "a role
        # has run out of rungs", and the principal was asked about a question
        # two untouched owners might have answered for free.
        for m in result.messages:
            if m.verb != "report" or not m.cause_id:
                continue
            conn.execute(
                "UPDATE messages SET status = 'unresolved', "
                "  unresolved_note = COALESCE(unresolved_note, ?) "
                "WHERE id = ? AND verb = 'ask' AND status != 'unresolved'",
                (f"{result.role} reported that its artefact does not hold this",
                 m.cause_id))


        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise

    # Edge coverage is derived from evidence a committed session already leaves
    # behind, so any test running a session contributes without knowing this
    # exists. Nothing to annotate, nothing to forget.
    if os.environ.get("ROTA_COVERAGE_ON"):
        from ..testkit.coverage import record
        try:
            record(conn)
        except Exception:
            pass                       # instrumentation must never fail a commit


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise

    # Edge coverage is derived from evidence a committed session already leaves
    # behind, so any test running a session contributes without knowing this
    # exists. Nothing to annotate, nothing to forget.
    if os.environ.get("ROTA_COVERAGE_ON"):
        from ..testkit.coverage import record
        try:
            record(conn)
        except Exception:
            pass                       # instrumentation must never fail a commit


def mark_created(conn: sqlite3.Connection) -> None:
    """
    Stamp the moment this run was made. The first stamp is the one that keeps.

    `INSERT OR IGNORE`, because onboarding runs again on a run that already
    exists. A second onboarding of one run does not make a second run, so the
    date the list shows must not move.

    The value is `datetime('now')` text, in UTC, the same shape and the same
    clock as `config_history.at`. SQLite writes it, so no two callers can
    disagree about the format.
    """
    conn.execute("INSERT OR IGNORE INTO config (key, value) "
                 "VALUES ('created_at', datetime('now'))")


def mark_opened(conn: sqlite3.Connection) -> None:
    """
    Stamp the moment a seat opened this run. The last stamp is the one that
    keeps.

    Opening means the seat, and only the seat. The cockpit is a viewer and
    never changes state, so reading a run in the browser is not opening it.
    `rota ls` reads every run through `connect_readonly`, so listing them all
    cannot stamp them all.
    """
    conn.execute("INSERT OR REPLACE INTO config (key, value) "
                 "VALUES ('opened_at', datetime('now'))")


def get_config(conn: sqlite3.Connection, key: str, default: Any = None) -> Any:
    row = conn.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
    return json.loads(row["value"]) if row else default


def set_config(conn: sqlite3.Connection, key: str, value: Any) -> None:
    conn.execute(
        "INSERT INTO config(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, json.dumps(value)),
    )


def session_fail(conn: sqlite3.Connection, *, session_id: str, role: str,
                 trigger_msg: str | None, wake_kind: str, wake_detail: str,
                 wake_refs: list, pins: dict, turns: list, error: str) -> None:
    """
    A failed session leaves a row.

    clickI night 31 (2026-09-13): a session died on the same error 69 times
    in 98 minutes and the database held nothing, because only a committed
    session was written. A broken hop and no hop looked the same. The row
    is `committed = 0`, its turns are kept, and the error is the last turn,
    so `SELECT * FROM turns WHERE completion LIKE 'SESSION FAILED%'` is the
    question "what died, and on what".
    """
    conn.execute(
        "INSERT OR IGNORE INTO sessions (id, role, trigger_msg, mode, committed, "
        "seq, model, temperature, num_ctx, pins_json, wake_kind, wake_detail, "
        "wake_refs) VALUES (?, ?, ?, 'normal', 0, ?, ?, ?, ?, ?, ?, ?, ?)",
        (session_id, role, trigger_msg, _next_seq(conn, "sessions"),
         pins.get("model"), pins.get("temperature"), pins.get("num_ctx"),
         json.dumps(pins, sort_keys=True, default=str), wake_kind, wake_detail,
         json.dumps(list(wake_refs))))
    for turn in turns:
        conn.execute(
            "INSERT OR IGNORE INTO turns (session_id, seq, system, user, "
            "completion, ms) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, turn.seq, turn.system, turn.user, turn.completion, turn.ms))
    conn.execute(
        "INSERT OR IGNORE INTO turns (session_id, seq, system, user, completion, ms) "
        "VALUES (?, ?, '', '', ?, 0)",
        (session_id, len(turns) + 1, f"SESSION FAILED: {error}"))
    conn.commit()


def session_note(conn: sqlite3.Connection, session_id: str, errors: list[str]) -> None:
    """
    How a committed session ended, as its last turn.

    The refusals of a session's last turn live in the prompt of a turn that
    never came, so a session that ended right after a refused call showed
    nothing in the record (the wake audit, 2026-09-13). The runner's own
    account of the session, its errors and the reason it stopped, is
    written as one more turn, so the reader sees the end.
    """
    if not errors:
        return
    seq = (conn.execute("SELECT COALESCE(MAX(seq), 0) FROM turns WHERE session_id = ?",
                        (session_id,)).fetchone()[0] or 0) + 1
    conn.execute(
        "INSERT OR IGNORE INTO turns (session_id, seq, system, user, completion, ms) "
        "VALUES (?, ?, '', '', ?, 0)",
        (session_id, seq, "SESSION ENDED. The runner's account:\n" + "\n".join(f"- {e}" for e in errors)))
