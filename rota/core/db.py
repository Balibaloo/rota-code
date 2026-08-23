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
    "problem":    ("items", "item_statements"),
    "glossary":   ("glossary_terms", "business_rules"),
    "model":      ("constraints", "constraint_bindings", "model_areas"),
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
    "tickets":    ("tickets",),
    "criteria":   ("criteria",),
    "batches":    ("batches", "batch_tickets", "batch_dep_facts", "batch_touch"),
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


def init_db(path: str | Path) -> sqlite3.Connection:
    conn = connect(path)
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
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
    "batch_tickets", "constraint_bindings", "survey_citations", "item_statements",
    "batch_dep_facts", "schedule_deps", "batch_touch",
}


def _apply_write(conn: sqlite3.Connection, w: Write) -> None:
    if w.table in JUNCTION_TABLES:
        cols = list(w.values.keys())
        marks = ", ".join("?" for _ in cols)
        conn.execute(
            f"INSERT OR REPLACE INTO {w.table} ({', '.join(cols)}) VALUES ({marks})",
            list(w.values.values()),
        )
        return

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
        return

    payload = {"id": w.row_id, **w.values} if "id" not in w.values else dict(w.values)
    cols = list(payload.keys())
    placeholders = ", ".join("?" for _ in cols)
    conn.execute(
        f"INSERT INTO {w.table} ({', '.join(cols)}) VALUES ({placeholders})",
        list(payload.values()),
    )


def _has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    return any(r[1] == column for r in conn.execute(f"PRAGMA table_info({table})"))


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
            "wake_refs, briefs_hash) "
            "VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                result.session_id, result.role, result.trigger_msg, result.mode,
                _next_seq(conn, "sessions"),
                result.pins.get("model"), result.pins.get("temperature"),
                result.pins.get("num_ctx"), result.pins.get("prompt_hash"),
                result.wake_kind, result.wake_detail,
                json.dumps(list(result.wake_refs)), result.briefs_hash,
            ),
        )

        for w in result.writes:
            _apply_write(conn, w)
            if w.table in ARTEFACT_TABLES:
                new_version = bump_version(conn, w.table)
                conn.execute(
                    "INSERT OR REPLACE INTO receipts "
                    "(session_id, table_name, row_id, new_version) VALUES (?, ?, ?, ?)",
                    (result.session_id, w.table, w.row_id, new_version),
                )

        for m in result.messages:
            conn.execute(
                "INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, "
                "to_role, verb, body_refs, body_text, round_no, seq) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    m.id, m.cause_id, m.cause_kind,
                    m.thread_id or m.cause_id or m.id,
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
        for thread in {m.thread_id or m.cause_id or m.id for m in result.messages}:
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

        # The trigger message is answered once its session commits.
        if result.trigger_msg:
            conn.execute(
                "UPDATE messages SET status = 'answered' WHERE id = ?",
                (result.trigger_msg,),
            )

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


def get_config(conn: sqlite3.Connection, key: str, default: Any = None) -> Any:
    row = conn.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
    return json.loads(row["value"]) if row else default


def set_config(conn: sqlite3.Connection, key: str, value: Any) -> None:
    conn.execute(
        "INSERT INTO config(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, json.dumps(value)),
    )
