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
import re
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from .. import paths
from typing import Any, Iterable, Iterator

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
                   "touch_guesses", "touch_strays", "drop_notes"),
    "tests":      ("tests",),
    "ledger":     ("ledger",),
    "decisions":  ("decisions",),
    "verdicts":   ("verdicts", "finding_rulings"),
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
    # A file that no `init_db` of fact F4 opened has no `latest_runs` view.
    latest_runs_view(conn)
    return conn


def connect_readonly(path: str | Path) -> sqlite3.Connection:
    """Open the database in read-only mode for the cockpit and other viewers."""
    db_path = Path(path).expanduser().resolve()
    conn = sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    # `query_only` refuses a temp view too, so the view comes first.
    latest_runs_view(conn)
    conn.execute("PRAGMA query_only = ON")
    return conn


def latest_runs_view(conn: sqlite3.Connection) -> None:
    """Give a connection the `latest_runs` view when its file has none.

    A night's file from before fact F4 holds no such view, and every reader
    of the newest run reads the view. A temp view writes nothing to the
    file. The body is the schema's own, so the order rule stays one. Every
    opener of a rota file calls this helper: `connect`, `connect_readonly`,
    `invariants.open_readonly` and `nightreport.open_ro`. A read script
    opens a night through one of them (the F4 review, low 5)."""
    have = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE name IN ('latest_runs', 'test_runs')")}
    if have != {"test_runs"}:
        return
    body = re.search(r"CREATE VIEW IF NOT EXISTS latest_runs AS(.*?);",
                     SCHEMA_PATH.read_text(encoding="utf-8"), re.S).group(1)
    conn.execute(f"CREATE TEMP VIEW IF NOT EXISTS latest_runs AS{body}")


# The schema marker (frame 21). `init_db` writes it when it creates the
# tables. A run database from before the refs relation has the owner tables
# and no marker. Opened, it would read every gate as reasoned, so the door
# refuses it. A database at an older mark is refused for the same reason:
# `executescript` adds a table, never a column. Run databases are throwaway.
SCHEMA_KEY = "schema"
# Move the mark whenever a column is added to a table a run writes. The commit
# before this one added `ledger.kind` and left the mark alone, so an old
# database opened and then failed part way through the night on its first
# ledger write. The warm snapshot is such a database.
# Frame 204 widened both CHECKs of `ledger` and added `faults`.
# A new table needs no move: `init_db` adds it, and `cmd_run` calls
# `init_db` before `drive` (frame 309, review 1, finding 1). A new door that
# opens a run with `connect` alone must call `init_db` first.
# Frame 316, pass 2, widened the status CHECK of `ledger` with `parked`.
# Frame 306, pass 1b, added `criteria.retired_by`.
# Frame 306, W-A, added `tests.retired_by`.
# Fact F1 widened the source CHECK of `ruled_refs` with `landed` and added
# `ruled_refs.derived_from`. An older run keeps its verdicts in the config
# map, and no reader reads that map now.
SCHEMA_MARK = "ruled-refs-landed"
SCHEMA_STALE = ("the run database is behind the current schema, so it needs "
                "a fresh onboarding: wipe it, or onboard under a new name")


def schema_stale(conn: sqlite3.Connection) -> str | None:
    """The sentence that refuses a database behind the current schema.
    None for an empty database and for one that carries the current mark and
    no provenance column."""
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


def ruled_ref_id(ruling_id: str, ref: str) -> str:
    """The id of the `ruled_refs` row of one ruling and ref. It hashes the
    pair, so the identity derives from the content (law 14)."""
    import hashlib

    return "rr_" + hashlib.sha256(f"{ruling_id}|{ref}".encode()).hexdigest()[:12]


# The key of a request item's code line (frame 298's design, 2.1). It
# derives from the item id, so law 14 holds.
GUESS_REF = "guess:"
# The ref of the read-back line of one reply (the seam design, 2.3).
READING_REF = "reading:"
# The journal keeps the id of a run that `test_runs` deleted. A ref to that
# id names no live row, and no gate or guard reads the journal (frame 309,
# review 1, finding 2).
_NOT_REFFABLE = frozenset({"test_run_journal"})
# Keyed by the database file and its schema version. A key of `id(conn)`
# gave a new connection the register of a closed one at the same address
# (F22 review, finding 2).
_ID_TABLES_CACHE: dict[tuple, list[str]] = {}


def id_tables(conn: sqlite3.Connection) -> list[str]:
    """The register of the tables a ref can name, in the order of
    `identity.NATURAL_KEYS`.

    The register derives from `NATURAL_KEYS` and the schema, so no second
    list of tables exists (F22). A table is in it when the schema gives it an
    `id` column."""
    from .identity import NATURAL_KEYS

    file = conn.execute("PRAGMA database_list").fetchone()[2]
    version = conn.execute("PRAGMA schema_version").fetchone()[0]
    # An in-memory database has no file, so its key is the connection.
    key = (file or id(conn), version)
    if key not in _ID_TABLES_CACHE:
        out = []
        for table in NATURAL_KEYS:
            if table in _NOT_REFFABLE:
                continue
            cols = {c[1] for c in conn.execute(f"PRAGMA table_info({table})")}
            if "id" in cols:
                out.append(table)
        _ID_TABLES_CACHE[key] = out
    return _ID_TABLES_CACHE[key]


def guess_item(ref) -> str | None:
    """The item id a `guess:<item>` key names, or None. This is the one rule
    of the prefix (F22)."""
    if isinstance(ref, str) and ref.startswith(GUESS_REF) and len(ref) > len(GUESS_REF):
        return ref[len(GUESS_REF):]
    return None


def tables_of(conn: sqlite3.Connection, ref, among=None) -> list[str]:
    """Every table that holds `ref`. This is the one reader of the fact (F22).

    Night databases hold one id in two tables: `sentinel` is a constraint and
    a glossary term on nights 161 to 170. So the reader gives every table, and
    a caller with a scope rule passes it as `among`. The result then keeps the
    order of `among`, else the order of the register.

    A `reading:<reply>` ref names the reply in `messages`. A `guess:<item>`
    ref names the item in `items`. Any other ref is an id of a table in
    `id_tables`."""
    if not isinstance(ref, str) or not ref:
        return []
    if ref.startswith(READING_REF) and len(ref) > len(READING_REF):
        key, scope = ref[len(READING_REF):], ["messages"]
    elif guess_item(ref) is not None:
        key, scope = guess_item(ref), ["items"]
    else:
        key, scope = ref, id_tables(conn)
    order = scope if among is None else [t for t in among if t in scope]
    return [t for t in order if conn.execute(
        f"SELECT 1 FROM {t} WHERE id = ?", (key,)).fetchone()]


def table_of(conn: sqlite3.Connection, ref, among=None) -> str | None:
    """The first table of `tables_of`, or None."""
    held = tables_of(conn, ref, among)
    return held[0] if held else None


def elsewhere(conn: sqlite3.Connection, ref, wanted: str) -> str:
    """The words that name every table holding `ref`, when the caller wanted
    `wanted`. Empty when no table holds it, or when `wanted` holds it.

    Night 170's s209 sent the batch b_3 to `model.adopt` three times, and the
    refusal never said that b_3 is a batch (W13)."""
    held = tables_of(conn, ref)
    if not held or wanted in held:
        return ""
    return f"; {ref!r} is a row of {' and '.join(held)}"


# The verdicts a `ruled_refs` row stores. `principal.RULED_VERDICTS` holds
# the same list, and this module cannot import the roles.
_RULED_VERDICTS = frozenset(("approve", "contest", "revise", "resume", "park",
                             "now", "drop"))


def backfill_ruled_refs(conn: sqlite3.Connection) -> int:
    """
    Give each older `rulings` row its `ruled_refs` rows, from `per_item`.

    A database from before the table holds rulings with no rows, and the
    readers of the table would read no ruling on them. The rows carry no
    act and no target, because `per_item` holds none, and the whole reply as
    the words (the seam design, 1.4). A value that is not a stored verdict
    has no row, as `principal.ruling_rows` refuses it. Returns the count of
    rows.
    """
    count = 0
    for r in conn.execute(
            "SELECT id, per_item, words, texts FROM rulings u "
            "WHERE per_item NOT IN ('', '{}') AND NOT EXISTS ("
            "SELECT 1 FROM ruled_refs t WHERE t.ruling_id = u.id)").fetchall():
        try:
            ruled = json.loads(r["per_item"] or "{}")
            texts = json.loads(r["texts"] or "{}")
        except (TypeError, ValueError):
            continue
        if not isinstance(ruled, dict):
            continue
        texts = texts if isinstance(texts, dict) else {}
        for ref, verdict in ruled.items():
            if not (isinstance(ref, str) and isinstance(verdict, str)
                    and verdict in _RULED_VERDICTS):
                continue
            text = texts.get(ref)
            count += conn.execute(
                "INSERT OR IGNORE INTO ruled_refs (id, ruling_id, ref, verdict, "
                "words, old_text, source) VALUES (?, ?, ?, ?, ?, ?, 'backfill')",
                (ruled_ref_id(r["id"], ref), r["id"], ref, verdict,
                 r["words"] or "", text if isinstance(text, str) else None)
            ).rowcount
    return count


def init_db(path: str | Path) -> sqlite3.Connection:
    conn = connect(path)
    # A failure part way closes the file. An open connection that lives on in
    # the traceback holds the file on Windows (frame 104, pass 4).
    try:
        stale = schema_stale(conn)
        if stale:
            conn.close()
            raise RuntimeError(stale)
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        # The file holds the view now. The temp view of `connect` is no
        # longer needed, and only this connection sees it.
        conn.execute("DROP VIEW IF EXISTS temp.latest_runs")
        # `executescript` adds a table, never a column, and a run database under
        # `.rota/` outlives the schema. The symbol spans are added in place rather
        # than behind `SCHEMA_MARK`, because the mark refuses a database outright
        # and these two columns need no decision: the next refresh fills them, and
        # 0 and 0 until then means the same as a path grain's default, no span.
        for column in ("line_start", "line_end"):
            if not _has_column(conn, "code_index", column):
                conn.execute(f"ALTER TABLE code_index ADD COLUMN {column} "
                             f"INTEGER NOT NULL DEFAULT 0")
        _widen_code_index_kinds(conn)
        _widen_ruled_ref_acts(conn)
        # The same for the description flag: 0 is every older item's truth, since
        # no seat could describe an item before the column existed.
        if not _has_column(conn, "items", "is_description"):
            conn.execute("ALTER TABLE items ADD COLUMN is_description "
                         "INTEGER NOT NULL DEFAULT 0")
        # The same for the verdict's reason: NULL is every older verdict's truth,
        # since no Critic could give a reason before the column existed.
        if not _has_column(conn, "verdicts", "reason"):
            conn.execute("ALTER TABLE verdicts ADD COLUMN reason TEXT")
        # The same for the lines a pass names (frame 170): NULL is every
        # older verdict's truth, since no pass named a line before.
        if not _has_column(conn, "verdicts", "lines"):
            conn.execute("ALTER TABLE verdicts ADD COLUMN lines TEXT")
        # The same for the route of each criterion of a pass (sprint 35 row
        # 4): NULL is every older verdict's truth, since no other route existed.
        if not _has_column(conn, "verdicts", "routes"):
            conn.execute("ALTER TABLE verdicts ADD COLUMN routes TEXT")
        # The same for the item version a ticket was sliced from (frame 190):
        # NULL is unknown, so an older ticket is never retired and never
        # sliced again.
        if not _has_column(conn, "tickets", "item_ver"):
            conn.execute("ALTER TABLE tickets ADD COLUMN item_ver INTEGER")
        # The same for the contested texts of a ruling (frame 226): an empty
        # map is every older ruling's truth, since no ruling kept one before.
        if not _has_column(conn, "rulings", "texts"):
            conn.execute("ALTER TABLE rulings ADD COLUMN texts TEXT "
                         "NOT NULL DEFAULT '{}'")
        # The same for a retired test (frame 306, W-A): NULL is every older
        # test's truth, since no ruling retired a test before the column.
        if not _has_column(conn, "tests", "retired_by"):
            conn.execute("ALTER TABLE tests ADD COLUMN retired_by TEXT")
        # The same for the told mark of a message (frame 355): 0 is every
        # older message's truth, since no report marked a message before.
        if not _has_column(conn, "messages", "told"):
            conn.execute("ALTER TABLE messages ADD COLUMN told "
                         "INTEGER NOT NULL DEFAULT 0")
        backfill_ruled_refs(conn)
        conn.execute("INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)",
                     (SCHEMA_KEY, SCHEMA_MARK))
    except BaseException:
        conn.close()
        raise
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
    op: str = "upsert"          # 'upsert' | 'update' | 'clear'
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
    # A Tester's triage creates its question unresolved, with the note. The
    # asker has said what is missing already, so nobody owes a reply (frame 81).
    status: str = "open"
    unresolved_note: str | None = None
    # Config rows the send door wrote about this message, keyed by its id:
    # `stamped:<id>` and `stalled:<id>`. They land in the session's commit,
    # so a refused session leaves none (frame 190's pass 1b).
    config: dict[str, str] = field(default_factory=dict)


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
    # The runner's account of the session, the lines `session_note` writes.
    # A reply that lands no ruling keeps the last one when no refusal exists
    # (frame 267, a parse error is no refusal).
    errors: list = field(default_factory=list)


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
    "batch_dep_facts", "schedule_deps", "batch_touch", "touch_guesses",
    "touch_strays", "refs", "drop_notes",
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


class JournalAuthorError(ValueError):
    """A write of one role over a journal row that another role authored."""


# A status move is no new authorship. A decision of one role resolves the
# ledger row of another, and `test_laws` pins that resolve. The review of
# pass 1 found the exception wider than that reason. Pass 1b keeps it, and
# the report records the finding.
_STATUS_MOVE = frozenset({"status"})

# The author column of a journal table whose column is not `author`. The
# author of a message is its sender.
_AUTHOR_COLUMN = {"messages": "from_role"}

# `config_history` has an author column and no `id` column. Two rows of one
# key are two events, so no row key exists to read an author by.
_NO_ROW_KEY = frozenset({"config_history"})

# The author column of `entries` holds the speaker, not the writing role.
# The Liaison writes the principal's words with author "principal", so the
# staged value there is no claim of authorship by the writing role.
_SPEAKER_TABLES = frozenset({"entries"})


def author_column(conn: sqlite3.Connection, table: str) -> str | None:
    """The column that names the author of a row of `table`, or None when
    the rule does not cover the table. `identity.py` declares the journal
    tables."""
    from .identity import NATURAL_KEYS

    if NATURAL_KEYS.get(table, ("",))[0] != "journal" or table in _NO_ROW_KEY:
        return None
    column = _AUTHOR_COLUMN.get(table, "author")
    return column if _has_column(conn, table, column) else None


def journal_author(conn: sqlite3.Connection, table: str,
                   row_id: str) -> str | None:
    """
    The author on file of one journal row, or None.

    This function is the one reader of the fact. None means that the rule
    does not cover the table, or that the row or its author is absent.
    """
    column = author_column(conn, table)
    if column is None:
        return None
    row = conn.execute(f"SELECT {column} FROM {table} WHERE id = ?",
                       (row_id,)).fetchone()
    return (row[0] or None) if row is not None else None


def author_refusal(conn: sqlite3.Connection, table: str, row_id: str,
                   role: str, values: dict) -> str | None:
    """
    The refusal of a write of `values` by `role` on one journal row, or None.

    Law 1: a journal has "one author per entry". Roman ruled on 2026-10-27
    14:47 that the author is the role, so any session of that role may
    change the entry. A write also may not name another role as the author
    (law 6: nothing is written on the principal's behalf). The commit and
    the doors read this one rule.
    """
    column = author_column(conn, table)
    if column is None:
        return None
    author = journal_author(conn, table, row_id)
    if (author is not None and author != role
            and not set(values) <= _STATUS_MOVE):
        return (f"{row_id} is a {table} row by {author}, and you write as "
                f"{role}. A journal row is its author's record.")
    named = values.get(column)
    if table not in _SPEAKER_TABLES and named and named != role:
        return (f"the write names {named} as the author of {table} row "
                f"{row_id}, and you write as {role}. A journal row is its "
                f"author's record.")
    return None


def _apply_write(conn: sqlite3.Connection, w: Write, role: str) -> bool:
    """Apply one write by `role`. Returns False when the write changes no
    row. Raise JournalAuthorError when the write is over another role's
    journal row."""
    if w.table == REFS_TABLE:
        return _apply_ref(conn, w)
    # A junction row set that a session replaces whole. The Architect's touch
    # set, corrected by the principal's words, is the one writer: an upsert
    # kept the disputed path beside the new one (frame 190's design, 2.2,
    # the batch line, point 5).
    if w.op == "clear":
        if w.table not in JUNCTION_TABLES or not w.values:
            raise ValueError(f"a clear write names a junction table and its "
                             f"key columns, not {w.table!r}")
        cols = list(w.values.keys())
        conn.execute(
            f"DELETE FROM {w.table} WHERE "
            + " AND ".join(f"{c} = ?" for c in cols), list(w.values.values()))
        return True
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
    refused = author_refusal(conn, w.table, w.row_id, role, w.values)
    if refused:
        raise JournalAuthorError(refused)

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


def _widen_code_index_kinds(conn: sqlite3.Connection) -> None:
    """
    Give an older `code_index` the CHECK that holds `variable` and `export`.

    F13 pass 1c gives a binding row its own grain kind. SQLite cannot change
    a CHECK in place, so the table is built again from the schema file. The
    index is mechanical and no role decides a row, so the move needs no
    new mark. A row that pass 1b wrote as a `symbol` with a binding's
    `sym_kind` takes that kind as its grain kind.
    """
    import re as _re

    row = conn.execute("SELECT sql FROM sqlite_master WHERE type = 'table' "
                       "AND name = 'code_index'").fetchone()
    if row is None or "'variable'" in (row[0] or ""):
        return
    create = _re.search(r"CREATE TABLE IF NOT EXISTS code_index \(.*?\n\);",
                        SCHEMA_PATH.read_text(encoding="utf-8"), _re.S).group(0)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(code_index)")]
    names = ", ".join(cols)
    picked = ", ".join(
        "CASE WHEN grain_kind = 'symbol' AND sym_kind IN ('variable', 'export') "
        "THEN sym_kind ELSE grain_kind END" if c == "grain_kind" else c
        for c in cols)
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute(create.replace("IF NOT EXISTS code_index",
                                    "code_index_widened", 1))
        conn.execute(f"INSERT INTO code_index_widened ({names}) "
                     f"SELECT {picked} FROM code_index")
        conn.execute("DROP TABLE code_index")
        conn.execute("ALTER TABLE code_index_widened RENAME TO code_index")
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise


def _widen_ruled_ref_acts(conn: sqlite3.Connection) -> None:
    """
    Give an older `ruled_refs` the CHECK that holds the act `exclude`.

    Seam pass 3b gives a touch-list correction its own act. SQLite cannot
    change a CHECK in place, so the table is built again from the schema
    file, as `_widen_code_index_kinds` does. The rows copy as they are. The
    legacy rename keeps the views that read the table, and the drop takes
    the index and the trigger, so both are built again.
    """
    import re as _re

    row = conn.execute("SELECT sql FROM sqlite_master WHERE type = 'table' "
                       "AND name = 'ruled_refs'").fetchone()
    if row is None or "'exclude'" in (row[0] or ""):
        return
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    create = _re.search(r"CREATE TABLE IF NOT EXISTS ruled_refs \(.*?\n\);",
                        schema, _re.S).group(0)
    after = [_re.search(r"CREATE INDEX IF NOT EXISTS ruled_refs_by_ref .*?;",
                        schema).group(0),
             _re.search(r"CREATE TRIGGER IF NOT EXISTS ruled_refs_never_change"
                        r".*?\nEND;", schema, _re.S).group(0)]
    names = ", ".join(r[1] for r in conn.execute("PRAGMA table_info(ruled_refs)"))
    conn.execute("PRAGMA legacy_alter_table = ON")
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute(create.replace("IF NOT EXISTS ruled_refs",
                                    "ruled_refs_widened", 1))
        conn.execute(f"INSERT INTO ruled_refs_widened ({names}) "
                     f"SELECT {names} FROM ruled_refs")
        conn.execute("DROP TABLE ruled_refs")
        conn.execute("ALTER TABLE ruled_refs_widened RENAME TO ruled_refs")
        for sql in after:
            conn.execute(sql)
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.execute("PRAGMA legacy_alter_table = OFF")


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


_NO_ROW = ("no row",)


def _subject_state(conn: sqlite3.Connection, w: Write) -> tuple | None:
    """
    The row's version, approval and status, read before and after a write.

    None for a refs or junction write, which has no row of its own. The
    columns a table lacks are left out, so the compare reads only what exists.
    A statement's or a ledger entry's status is its state, and a change of it
    revived a quarantine before frame 80 too.
    """
    if w.table == REFS_TABLE or w.table in JUNCTION_TABLES:
        return None
    cols = [c for c in ("version", "approval", "status")
            if _has_column(conn, w.table, c)]
    row = conn.execute(
        f"SELECT {', '.join(['1', *cols])} FROM {w.table} WHERE id = ?",
        (w.row_id,)).fetchone()
    return _NO_ROW if row is None else tuple(row)


def _subject_moved(conn: sqlite3.Connection, w: Write, before) -> bool:
    """
    Whether a write moved its subject. A move is a new row, a changed
    version, approval or status, a head commit, or a junction write.

    A write that sets the values the row holds already moves nothing. Night
    91's relay approved an approved item three times, and each write revived
    a tick that had given up (frame 80).
    """
    if before is None:
        return True
    if before == _NO_ROW:
        # An update on a missing row writes nothing, so it moves nothing.
        return w.op != "update" or _subject_state(conn, w) != before
    if w.table == "batches" and "head_commit" in (w.values or {}):
        return True
    return _subject_state(conn, w) != before


def _lift_quarantines(conn: sqlite3.Connection, w, moved: bool) -> None:
    """
    A quarantine holds while its subject is unchanged. A write that moves
    the subject is the exit: a new row, a version change, an approval
    change, or a head commit. A write that changes nothing is not an exit.

    The never-delete rule is right for what it was written against -- a
    quarantine erasing its own evidence put icalendar through 131 sessions
    of one key -- but it had no "the world moved" case, so a repaired
    criterion could never wake the Tester that gave up on it: every S0 walk
    died permanently at its first quarantine even after the cause was
    fixed. A quarantined tick revives when a commit moves a row its refs
    name, or (for criteria and tests) moves a row in the batch its refs
    name, because those tables are what the batch-keyed ticks are about.
    """
    # Law 6: the attempt caps and the ladder bound a cycle, so only a move revives.
    if moved:
        # A commit is the park's own exit, so it never lifts the park's
        # quarantine. Otherwise park, commit and fail restart at one for ever
        # (observed: frame 86's pass 4 review, 2026-09-25).
        commit = w.table == "batches" and "head_commit" in (
            getattr(w, "values", None) or {})
        # Frame 318: on a running batch the harness run at the new head
        # judges the `tests_failing` key, in `lift_on_red_move`.
        failing = commit and _running(conn, w.row_id)
        # The keys come from the one reader, so a ref matches as a whole.
        # A LIKE read `_` as a wildcard and ignored case (frame 242).
        from .scheduler import key_parts, quarantined_keys

        kept = (({"do:park"} if commit else set())
                | ({"tick:tests_failing"} if failing else set()))
        lift_keys(conn, [k for k in quarantined_keys(conn, w.row_id, pairs=True)
                         if key_parts(k)[1] not in kept])
        # A quarantined message whose ruling landed is answered once the
        # row it names moves. The landing is not the close event: dry1's
        # r_m4 landed before s38 to s40 failed on m4 (frame 355). The
        # landed ruling is the fact, and `mark_answered` is the one writer
        # of the mark (fact F16).
        for r in conn.execute(
                "SELECT id FROM messages WHERE status = 'quarantined' "
                "AND id IN (SELECT verdict_id FROM rulings WHERE status = 'landed') "
                "AND EXISTS (SELECT 1 FROM json_each(CASE WHEN "
                "json_valid(messages.body_refs) THEN messages.body_refs "
                "ELSE '[]' END) WHERE value = ?)", (w.row_id,)).fetchall():
            mark_answered(conn, r["id"])
    # Progress is the red moving, and the bound is on dispatch *without*
    # progress. Walk seventeen: four, three, two tests failing across three
    # commits, and the third session was the quarantine. So a moved red
    # resets the key. Night 162: a docstring commit wiped the quarantine,
    # and the same red bought three more ticks. So a head move alone does
    # not reset it on a running batch (frame 318).
    fields = getattr(w, "values", None) or {}
    # Read the red before the re-encode below deletes the old body's runs.
    # A re-encoded red test replaces a red body, so its move reaches the red.
    reaches = (_moves_red(conn, w) if moved and w.table in ("criteria", "tests")
               else {})
    # A re-encoded test's runs describe a body that no longer exists. Walk
    # eighteen: the hold guard, the Developer's wake and the harness gate
    # all read the run of the old body after the new one landed.
    if w.table == "tests" and "body" in fields:
        conn.execute("DELETE FROM test_runs WHERE test_id = ?", (w.row_id,))
    if w.table == "batches" and "head_commit" in fields:
        running = _running(conn, w.row_id)
        # A parked batch gets no harness run until it resumes, so the commit
        # still lifts its key. The commit is the park's way out (frame 87).
        if not running:
            forget_keys(conn, batch_keys(conn, w.row_id, {"tick:tests_failing"}))
        # The commit is the way out the park ask names, so the ask closes
        # with the keys it asked about (frame 87).
        from .scheduler import close_park_asks

        close_park_asks(conn, w.row_id)
        # A missing test is not the code's debt, so a commit keeps its count.
        # A moved test of the batch resets it below. The park keeps its count
        # too: a commit is the park's own exit, so a reset would let park,
        # commit and fail loop without a bound (observed: frame 86's pass 3
        # review, 2026-09-25). Law 6 bounds the loop at the attempt cap.
        keep = ("%|tick:tests_missing|%", "%|do:park|%")
        if running:
            keep += ("%|tick:tests_failing|%",)
        _forget_batch_counts(conn, w.row_id, keep=keep)
    if moved and w.table in ("criteria", "tests"):
        for b, red_moved in reaches.items():
            if b:
                from .scheduler import quarantined_keys

                lift_keys(conn, [k for k in quarantined_keys(conn, b)
                                 if _row_move_reaches(k, red_moved)])
                # Review 2, finding 2: a reset count below the cap bought the
                # same refusal more ticks, so the refused keys keep it too.
                spared = tuple(r["tick_key"] for r in conn.execute(
                    "SELECT tick_key FROM tick_attempts WHERE quarantined = 0 "
                    "AND (tick_key LIKE ? OR tick_key LIKE ? OR tick_key LIKE ? "
                    "OR tick_key LIKE ?)",
                    (f"%|{b}", f"%|{b},%", f"%,{b}", f"%,{b},%"))
                    if not _row_move_reaches(r["tick_key"], red_moved))
                _forget_batch_counts(conn, b, keep=spared)


def lift_keys(conn: sqlite3.Connection, keys: Iterable[str]) -> None:
    """Lift the quarantine of each key. A key that is not quarantined stays."""
    # The one delete of a quarantined key. `land` deleted one by hand before
    # (fact F20, the root-cause audit of 2026-10-27). Law 6.
    conn.executemany("DELETE FROM tick_attempts WHERE tick_key = ? "
                     "AND quarantined = 1", [(k,) for k in keys])


def mark_ruled(conn: sqlite3.Connection, keys: Iterable[str]) -> None:
    """Mark each quarantined key as answered by the principal. The key stays
    quarantined, so the step does not run again, and no page shows it."""
    # Frame 354, pass 5: his 'ok' on a stopped step drops the step. Law 6
    # keeps the quarantine, and `scheduler.RULED` keeps the page quiet.
    from .scheduler import RULED

    conn.executemany("UPDATE tick_attempts SET reported = ? WHERE tick_key = ? "
                     "AND quarantined = 1", [(RULED, k) for k in keys])


def forget_keys(conn: sqlite3.Connection, keys: Iterable[str]) -> None:
    """Lift each key's quarantine and forget its live count."""
    keys = list(keys)
    lift_keys(conn, keys)
    conn.executemany("DELETE FROM tick_attempts WHERE tick_key = ? "
                     "AND quarantined = 0", [(k,) for k in keys])


def batch_keys(conn: sqlite3.Connection, batch_id: str,
               kinds: set[str]) -> list[str]:
    """The keys of these kinds about the batch alone, live or quarantined."""
    # A LIKE pattern read `_` in the batch id as a wildcard (frame 242).
    from .scheduler import key_parts

    return [r["tick_key"] for r in conn.execute("SELECT tick_key FROM tick_attempts")
            if key_parts(r["tick_key"])[1] in kinds
            and key_parts(r["tick_key"])[2] == (batch_id,)]


# The junction tables a batch's seats read for the batch: the touch set that
# `batches.expect` shows, and the tickets whose criteria the seats read.
BATCH_READS = ("batch_touch", "batch_tickets")


def lift_batch_seats(conn: sqlite3.Connection, batch_ids: Iterable[str]) -> None:
    """
    Lift the seats' quarantined keys of each batch, after a move of what the
    seats read for it: its touch set, its tickets, or a ruling on its rows.
    """
    # A scheduler key (`-|do:park|b`) is the park's own bound, and a commit
    # is its only exit (frame 86). Frame 318 keeps the Developer's red keys
    # until the red moves, so a move that reaches no red lifts none of them.
    # A deferred batch's given-up key waits for the principal's page (frame
    # 87, ruled 2026-09-27), so only a running batch's keys lift here.
    from .scheduler import key_parts, quarantined_keys

    running = [b for b in batch_ids if _running(conn, b)]
    if running:
        lift_keys(conn, [k for k in quarantined_keys(conn, running)
                         if key_parts(k)[0] != "-" and _row_move_reaches(k, False)])


def batch_reads(conn: sqlite3.Connection, writes) -> dict[str, tuple]:
    """The stored touch set and tickets of each batch these writes name."""
    batches = {str(w.values["batch_id"]) for w in writes
               if w.table in BATCH_READS and (w.values or {}).get("batch_id")}
    return {b: tuple(tuple(r) for t in BATCH_READS for r in conn.execute(
        f"SELECT * FROM {t} WHERE batch_id = ? ORDER BY 1, 2", (b,)))
        for b in sorted(batches)}


def lift_moved_reads(conn: sqlite3.Connection, before: dict[str, tuple]) -> None:
    """Lift the seat keys of each batch whose stored touch set or tickets moved."""
    # The touch set and the tickets are what a batch's seats read for it.
    # Night 170's s217 and s224 rewrote b_3's touch set, and the Tester's key
    # stayed (review of F20 pass 1, finding 1). The compare is on the stored
    # rows after the whole commit, so a clear and a rewrite of the same rows
    # lift nothing, as frame 318 rules for a commit (F20 pass 1c).
    after = batch_reads(conn, [Write(BATCH_READS[0], b, {"batch_id": b})
                               for b in before])
    lift_batch_seats(conn, [b for b in before if after[b] != before[b]])


def write_state(conn: sqlite3.Connection, table: str, row_id: str, sql: str,
                params: tuple = (), fields: dict | None = None) -> int:
    """
    Run one raw UPDATE of a subject's row, and lift its quarantines when the
    row moved. Returns the rowcount.

    `fields` names the columns the UPDATE sets when the lift reads them, as
    `head_commit` for a commit.
    """
    # A raw write of a ledger status skipped the lift, so a quarantined key
    # could outlive its closed entry (frame 242). A write that sets the value
    # the row holds moves nothing and lifts nothing (frame 80). Law 6.
    w = Write(table, row_id, dict(fields or {}), op="update", amends=False)
    before = _subject_state(conn, w)
    n = conn.execute(sql, params).rowcount
    if n:
        _lift_quarantines(conn, w, _subject_moved(conn, w, before))
    return n


def _moves_red(conn: sqlite3.Connection, w) -> dict[str, bool]:
    """
    Each batch a criteria or tests move touches, and whether the move
    reaches a test that is red at the batch's head.

    A tests move reaches the red when the moved test is red. A criteria
    move reaches it when a test of the criterion is red. The rule reads
    test ids, so a retire column that a later frame adds needs no change.
    """
    # Frame 318, night 164: s228 and s244 added a passing test, and s252
    # re-encoded one. Each lift restarted the same round on an unchanged red.
    if w.table == "criteria":
        rows = conn.execute(
            "SELECT bt.batch_id, t.id AS test_id FROM batch_tickets bt "
            "JOIN criteria c ON c.ticket_id = bt.ticket_id "
            "LEFT JOIN tests t ON t.criterion_id = c.id "
            "AND t.batch_id = bt.batch_id WHERE c.id = ?", (w.row_id,))
    else:
        rows = conn.execute(
            "SELECT batch_id, id AS test_id FROM tests WHERE id = ?", (w.row_id,))
    moved: dict[str, set[str]] = {}
    for r in rows:
        moved.setdefault(r["batch_id"], set()).add(r["test_id"])
    # The retire is applied already, so the red is read with retired tests in.
    return {b: bool(tests & set(red_before(conn, b, live=False)))
            for b, tests in moved.items() if b}


# The Developer's ticks that a criteria move can free. A criteria move
# retires or re-encodes the criterion's tests, so it can move the red (frame
# 306). A held failed verdict stays at the head, and `review` cannot fire
# again, so only this lift frees the batch (review 2, finding 1, night 160).
_RED_TICKS = ("tick:tests_failing", "tick:exhausted", "tick:verdict_failed")


def _row_move_reaches(key: str, red_moved: bool) -> bool:
    """
    Whether a criteria or tests move can change the cause of a batch's key.

    The other seats read the criteria or the tests at their wake, so a move
    can change their cause. The Developer's start, finding and touch ticks
    meet the code tree and the note door, and a criteria move changes
    neither. The red and exhausted ticks change only when the move reaches
    a test that is red at the head, which `red_moved` says.
    """
    # Frame 318, night 163: each respecify of a bg_2 criterion lifted
    # `developer|tick:batch_start|bg_2`. Three more Developers met the same
    # note refusal at termui.py line 609, five rounds.
    from .scheduler import key_parts

    role, tick, _ = key_parts(key)
    if role != "developer":
        return True
    # Night 164: a new passing test is not progress on the red (W-B).
    if tick in _RED_TICKS[:2]:
        return red_moved
    return tick in _RED_TICKS


def _forget_batch_counts(conn: sqlite3.Connection, batch_id: str,
                         keep: tuple[str, ...] = ()) -> None:
    """
    A move of the batch resets every live count that names it.

    `quarantine_stalled` keeps a batch's count while its wake is absent, so
    this move is the only reset it gets (observed: night 92, 2026-09-24).
    A quarantined key keeps the rules above. `keep` holds LIKE patterns for
    the keys this move is not about.
    """
    spare = "".join(" AND tick_key NOT LIKE ?" for _ in keep)
    conn.execute(
        f"DELETE FROM tick_attempts WHERE quarantined = 0{spare} "
        "AND (tick_key LIKE ? OR tick_key LIKE ? OR tick_key LIKE ? OR tick_key LIKE ?)",
        (*keep, f"%|{batch_id}", f"%|{batch_id},%", f"%,{batch_id}",
         f"%,{batch_id},%"))


def _running(conn: sqlite3.Connection, batch_id: str) -> bool:
    row = conn.execute("SELECT status FROM batches WHERE id = ?",
                       (batch_id,)).fetchone()
    return bool(row) and row["status"] == "running"


def _first_error(output: str) -> str:
    """The error line of a run, with object addresses blanked."""
    # Fact F5: `harness.error_line` is the one reader of the line. harness
    # imports this module, so the import waits for the call.
    from .harness import error_line

    # Night 160: the same red printed a new `0x...` address on each run.
    return re.sub(r"0x[0-9a-fA-F]+", "0x", error_line(output))


def _red_of(rows) -> dict[str, str]:
    return {r["test_id"]: _first_error(r["output"]) for r in rows
            if r["result"] in ("fail", "error")}


# The output of the error row that the harness records when no worktree
# exists. No code ran, so the row is no red and no run at its head.
NO_WORKTREE = "the batch has no worktree at "


def _real_run() -> str:
    return f" AND output NOT LIKE '{NO_WORKTREE}%'"


def red_before(conn: sqlite3.Connection, batch_id: str,
               live: bool = True) -> dict[str, str]:
    """
    The batch's red before a harness run, as test id to first error line.
    The newest run per test is the run at this head when one exists, and
    the run at the commit before otherwise. With `live`, a test of a
    retired criterion is in no red set.
    """
    # Frame 318, review 3, high 3: after a retire, the retired red test left
    # each run's red set, and every run lifted `tests_failing`.
    from .scheduler import live_tests

    alive = live_tests(conn, "test_id") if live else ""
    # Fact F4 leaves this read on the table. It needs the newest run that ran
    # code, and `latest_runs` can hold a no-worktree row that ran none.
    return _red_of(conn.execute(
        "SELECT test_id, result, output FROM test_runs WHERE rowid IN "
        f"(SELECT MAX(rowid) FROM test_runs WHERE batch_id = ?{_real_run()}"
        f"{alive} GROUP BY test_id)", (batch_id,)))


def lift_on_red_move(conn: sqlite3.Connection, batch_id: str,
                     head: str | None, before: dict[str, str],
                     same_head: bool = False) -> bool:
    """
    Reset the batch's `tests_failing` key when the red moved at `head`.

    The harness reads `before` with `red_before` and calls this after it
    records its runs. With no new red test, the red moved when a red test
    of `before` passes or raises another first error line. At an unchanged
    head (`same_head`), a new red test is a new cause, and the key lifts.
    After a new head, a new red test is the Developer's own breakage, and
    the key stays. The key remembers nothing: the last red is in
    `test_runs`. A test of a retired criterion is in neither red set.
    """
    # Frame 318, night 162: s315's docstring commit wiped the quarantine on
    # the same red. Law 6's attempt cap still bounds a red that moves.
    from .scheduler import live_tests

    now = _red_of(conn.execute(
        "SELECT test_id, result, output FROM latest_runs WHERE batch_id = ? "
        f"AND commit_sha = ?{live_tests(conn, 'test_id')}",
        (batch_id, head)))
    if now.keys() - before.keys():
        # Night 164: s229's commit 63c65435 cured one red and broke four, and
        # the cure reset the key (review 3, high 1). Pass 3b: at one head the
        # new red is the Tester's new test, so the Developer has a new cause.
        if not same_head:
            return False
        forget_keys(conn, batch_keys(conn, batch_id,
                                     {"tick:tests_failing", "tick:exhausted"}))
        return True
    if before.items() <= now.items():
        return False
    forget_keys(conn, batch_keys(conn, batch_id, {"tick:tests_failing"}))
    return True


# The verbs whose addressee owes a reply or work. This is the one list of
# that fact (fact F16, rule C76). `session_commit`, `waiting_on`,
# `waiting_on_a_seat` and `schedule_reask` read it. A woken session that
# sends nothing caused by one of these and writes no receipt for it leaves
# it unresolved (frame 174, design 200 change 5).
OWED_A_REPLY = (
    # `scheduler.waiting_on`: an open `question` is what waiting is.
    "question",
    # `schedule_reask`: Liaison's read-only inquiry leaves the asker blocked.
    "ask",
    # Frame 174 and frame 204's design, section 3.2: the challenger waits.
    "challenge",
    # `vision_keeper/propose.md` answers with msg.report_liaison (frame 303).
    "propose",
    # The escalate brief: "model.amend, and say so with msg.answer_developer".
    "escalate",
    # `liaison/submit.md`: "Send one `msg.present_principal`".
    "submit",
    # `developer/reopen.md`: "You elect, with `msg.elect_vision_keeper`".
    # A reopen caused by an elect hands the batch back and owes nothing
    # (`_owes_a_reply`).
    "reopen",
    # `vision_keeper/elect.md`: "Record it and unblock them" with a reopen.
    "elect",
)
# `verdict` owes nothing: `liaison/verdict.md` ends the session with no call
# when every statement is contested. A deliver, a relay, a report and an
# answer carry information, so the wake answers them.
UNRECEIVED_NOTE = ("unresolved: the woken session sent nothing and wrote no "
                   "row that cites this message")

# The receipt rule of an edge whose brief names a reply other than a message
# or a row of the trigger's refs. "none" owes no reply. "message" counts only
# a message caused by the trigger. A table name adds any write on that table
# to the default receipts.
RECEIPT_RULES = {
    # `developer/challenge.md`: "You have no message back to Critic" (review
    # of 8d090e2e, finding 1).
    ("critic", "developer", "challenge"): "none",
    # The proposal has no entry. `vision_keeper/propose.md` answers it with
    # msg.report_liaison with the refs, a message caused by the proposal, or
    # with a refusing decision on its refs. The default rules count both. An
    # `items` write is no answer, because only the principal asks for work
    # (frame 303, night 157's s205).
    # The escalate brief: "model.amend, and say so with msg.answer_developer".
    # An amend with no answer is night 127's m72 shape (review of pass 2c,
    # finding 2).
    ("developer", "architect", "escalate"): "message",
}


# The pages a principal reply answers with a ruling. A reply to one of them
# that lands no ruling is not consumed at once (frame 267).
PAGE_VERBS = ("confirm", "present", "clarify")
# The sessions a reply gets before its page goes back to the principal. The
# count is `messages.attempts`, which `run_session` raises at dispatch.
REPLY_SESSIONS = 2


def _page_under_reply(conn: sqlite3.Connection, trig: sqlite3.Row,
                      result: SessionResult) -> str | None:
    """
    The open page that `trig` replies to, when the session landed nothing on it.

    Night 151's s336 woke on m178, the reply to the page m177. It met one
    refusal three times and the repeat door ended it. No ruling was staged,
    and the commit marked m178 answered, so m177 waited on nobody (frame 267's
    scope read, sections 1 to 3). A `rulings` row or a message to the
    principal is an answer, as before.

    law 6: a question nobody answers climbs, so a barren session leaves it unresolved
    """
    if not (trig and trig["status"] == "open" and trig["verb"] == "converse"
            and trig["from_role"] == "principal" and trig["cause_id"]
            and result.checkpoint is None):
        return None
    if any(w.table == "rulings" for w in result.writes):
        return None
    if any(m.to_role == "principal" for m in result.messages):
        return None
    page = conn.execute(
        "SELECT id FROM messages WHERE id = ? AND status = 'open' "
        "AND to_role = 'principal' AND verb IN (?, ?, ?)",
        (trig["cause_id"], *PAGE_VERBS)).fetchone()
    return page["id"] if page else None


def _request_missed(conn: sqlite3.Connection, trig: sqlite3.Row,
                    result: SessionResult) -> bool:
    """
    Whether `trig` is a new request that its session landed nothing on.

    Night 163's s145 woke on m_p2, his new request. The paste door refused
    its four clarifies, and the session wrote nothing and sent nothing. The
    commit marked m_p2 answered, and the walk read quiet (frame 320). A new
    request has no `cause_id`, so `_page_under_reply` never saw it.

    His resend after the line of `unread_line` is a reply to a Liaison
    chat line, so a request whose cause is such a line is a request too.
    Only a statement or an item lands a request. A glossary row or a note
    does not intake it, so a retry cannot intake it twice (frame 320,
    review 1, findings 1 and 2).

    composition: nothing stops quietly, so a barren session leaves the request open
    """
    if not (trig and trig["status"] == "open" and trig["verb"] == "converse"
            and trig["from_role"] == "principal"
            and result.checkpoint is None and not result.messages):
        return False
    if any(w.table in REQUEST_LANDS for w in result.writes):
        return False
    if not trig["cause_id"]:
        return True
    return conn.execute(
        "SELECT 1 FROM messages WHERE id = ? AND from_role = 'liaison' "
        "AND to_role = 'principal' AND verb = 'converse' AND body_text LIKE ?",
        (trig["cause_id"], UNREAD_HEAD + "%")).fetchone() is not None


def _answers_unread(conn: sqlite3.Connection, trig: sqlite3.Row) -> bool:
    """
    Whether `trig` replies to a line of `unread_line`.

    The walk replies to every Liaison line. A resend that misses twice
    would send a new line, and the walk would reply again with no end. So
    the resend's second miss closes with its note and sends no line (frame
    320, review 1, finding 7).
    """
    return bool(trig["cause_id"]) and conn.execute(
        "SELECT 1 FROM messages WHERE id = ? AND from_role = 'liaison' "
        "AND body_text LIKE ?",
        (trig["cause_id"], UNREAD_HEAD + "%")).fetchone() is not None


def closed_requests(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    """
    The requests that closed with nothing landed, as (id, note), until a
    later request lands.

    His resend's second miss sends no line (finding 7). Without this list,
    nothing he looks at shows the closed request (frame 320, finding 9).
    A request that lands answers with no note.
    """
    return [(r["id"], r["unresolved_note"]) for r in conn.execute(
        "SELECT r.id, r.unresolved_note FROM messages r "
        "WHERE r.from_role = 'principal' AND r.verb = 'converse' "
        "AND r.status = 'answered' AND r.unresolved_note IS NOT NULL "
        "AND (r.cause_id IS NULL OR r.cause_id IN (SELECT id FROM messages "
        "WHERE from_role = 'liaison' AND body_text LIKE ?)) "
        "AND NOT EXISTS (SELECT 1 FROM messages l WHERE l.seq > r.seq "
        "AND l.from_role = 'principal' AND l.verb = 'converse' "
        "AND l.status = 'answered' AND l.unresolved_note IS NULL) "
        "ORDER BY r.seq", (UNREAD_HEAD + "%",))]


def _tell_unread(conn: sqlite3.Connection, trig: sqlite3.Row, request: str,
                 why: str) -> None:
    """Send him the line of `unread_line` as a Liaison chat line, the route
    `pending_replies` shows him (frame 320)."""
    from .runner import new_id

    told = OutboundMessage(
        id=new_id("m", conn), to_role="principal", verb="converse",
        body_refs=json.loads(trig["body_refs"] or "[]"),
        body_text=unread_line(why), cause_id=request)
    conn.execute(
        "INSERT INTO messages (id, cause_id, cause_kind, thread_id, "
        "from_role, to_role, verb, body_refs, body_text, round_no, "
        "seq, status) VALUES (?, ?, 'message', ?, 'liaison', "
        "'principal', 'converse', ?, ?, 0, ?, 'open')",
        (told.id, told.cause_id, _thread_of(conn, told),
         json.dumps(told.body_refs), told.body_text,
         _next_seq(conn, "messages")))


# The tables whose write lands a request (frame 320, review 1, finding 2).
REQUEST_LANDS = ("statements", "items")
# The tables whose write lands nothing. A fault row records a refused call,
# so a session whose every call was refused landed no row (fact F16).
NOT_LANDED = ("faults",)


def landed(result: SessionResult) -> bool:
    """
    Whether the session landed a row or sent a message.

    Night 170's W17 counted 21 sessions with no landed write and no
    message. s202 met three refusals and sent nothing. Its fault rows read
    as writes, so the old rule called the session not barren (fact F16).

    law 6: a question nobody answers climbs, so a barren session leaves it unresolved
    """
    return bool(result.messages) or any(w.table not in NOT_LANDED
                                        for w in result.writes)


def mark_answered(conn: sqlite3.Connection, message_id: str,
                  note: str | None = None, *, only_open: bool = False) -> int:
    """
    Set the answered mark of one message. Returns the count of rows set.

    This is the one writer of the mark (fact F16). A session sets it through
    `session_commit`. A trigger that asks for a reply needs `landed` first.
    A trigger that asks for nothing is answered by its wake. The principal's
    `land` and
    `_land_shift`, the park-ask sweeps and the cockpit set it on their own
    landed fact: his ruling, the batch's commit, the line he saw. A note
    stays on the row as the reason, and `None` keeps the note there.
    """
    if note is None:
        sql = "UPDATE messages SET status = 'answered' WHERE id = ?"
        args: tuple = (message_id,)
    else:
        sql = ("UPDATE messages SET status = 'answered', unresolved_note = ? "
               "WHERE id = ?")
        args = (note, message_id)
    if only_open:
        sql += " AND status = 'open'"
    return conn.execute(sql, args).rowcount or 0
# The note of a request miss with no refusal and no error. A request owes no
# ruling, so frame 267's note does not fit it (review 1, finding 5).
REQUEST_NOTHING = "the session landed nothing and sent nothing"
# The first sentence of the line to him. `rota agenda` keys its heading on it.
UNREAD_HEAD = "Your request did not reach the team."


def unread_line(note: str) -> str:
    """
    The line that tells the principal his request did not reach the team.

    Frame 320: two sessions on a request landed nothing. The note is the
    last refusal, and it speaks to the seat. The line says what happened in
    his terms: the team's question to him was refused, and why. It quotes
    no text, because the quote was his own words (review 1, finding 3).
    """
    note = (note or "").strip()
    op = re.match(r"^([a-z_]+\.[a-z_]+): ", note)
    why = note[op.end():] if op else ""
    why = re.split(r"(?<=[.!?])\s", why, maxsplit=1)[0].rstrip(".!? ")
    why = re.sub(r"'[^']*'", "the question", why)
    why = (why.replace("the principal's", "your")
           .replace("the principal", "you")
           .replace("back to them", "back to you"))
    if op and op.group(1) == "msg.clarify_principal" and why:
        said = f"The team tried to ask you about it, and the ask was refused: {why}."
    elif why:
        said = f"The team could not turn it into work: {why}."
    else:
        said = "The team tried twice and landed nothing."
    return f"{UNREAD_HEAD} {said} Reply to this line to send it again."


# The repeat door's end line. It says how the session ended, not what failed.
REPEAT_END = "repeated its previous turn verbatim twice; ended"
# The refusal door's end line, after its op name: "<op> was refused the same
# way in four turns; the session ended on it" (runner.py, `stop_reason`). It
# also says how the session ended, so the refusal before it is the fault
# (frame 267, review 2, finding 1).
REFUSED_END = " was refused the same way in four turns; the session ended on it"
# The copy door's end line. A turn that only sends again calls that landed
# earlier in the session has nothing more to do (night 170's W8).
COPIES_END = "sent again only calls that landed earlier in this session; ended"


def _is_end_line(line: str) -> bool:
    return (line in (REPEAT_END, COPIES_END)
            or line.endswith(REFUSED_END))


def _why_no_ruling(result: SessionResult,
                   nothing: str = "the session wrote no ruling and sent nothing"
                   ) -> str:
    """
    The newest fault of the session: its last error, else its last refusal.

    The errors come first because they hold every fault in order, parse
    errors included. Night 151's s226 fixed its first refusal at turn 2 and
    then failed four turns on a quote. The last refusal named the fixed
    fault (frame 267, review 1, finding 1). With no fault, the note is
    `nothing`. A request miss passes its own text (frame 320).
    """
    for e in reversed(result.errors or []):
        if e and not _is_end_line(str(e)):
            return str(e)
    for r in reversed(result.refusals or []):
        if len(r) > 1 and r[1]:
            return f"{r[0]}: {r[1]}"
    return nothing


def _receipt_rule(trig: sqlite3.Row) -> str | None:
    return RECEIPT_RULES.get((trig["from_role"], trig["to_role"], trig["verb"]))


def _owes_a_reply(conn: sqlite3.Connection, trig: sqlite3.Row) -> bool:
    """
    Whether `trig` has a verb of `OWED_A_REPLY` on a channel the graph
    declares. A test can seed a carrier on no channel, as the
    synthetic arc's Liaison challenge to the Critic. No session can send one.

    An edge whose rule in `RECEIPT_RULES` is "none" owes no reply.

    A `reopen` caused by an `elect` hands the batch back, and it owes no
    reply. `runner.py` reads the same key and gives it the `batch_start`
    mode, which builds and sends nothing. tipsAL's s75 woke on m37, such a
    reopen, and committed code (F16 review 1, finding 1).
    """
    if trig["verb"] not in OWED_A_REPLY:
        return False
    if _receipt_rule(trig) == "none":
        return False
    if trig["verb"] == "reopen" and trig["cause_id"] and conn.execute(
            "SELECT 1 FROM messages WHERE id = ? AND verb = 'elect'",
            (trig["cause_id"],)).fetchone():
        return False
    from ..design import graph as graph_mod
    return any(e.s == trig["from_role"] and e.t == trig["to_role"]
               and e.v == trig["verb"]
               for e in graph_mod.load().of_type("messages"))


def _answers_by_message(trig: sqlite3.Row) -> bool:
    """
    Whether the graph gives the addressee an `answer` edge to the asker.

    Such an addressee replies with a message, so its decision row is no
    receipt. Night 127's m72 shape: the Architect authors a decision, its
    answer never lands, and the escalation must stay owed (review of 8d090e2e,
    finding 2).

    law 6: a question nobody answers climbs, so a barren session leaves it unresolved
    """
    from ..design import graph as graph_mod
    return any(e.s == trig["to_role"] and e.t == trig["from_role"]
               and e.v == "answer"
               for e in graph_mod.load().of_type("messages"))


def _received(conn: sqlite3.Connection, result: SessionResult,
              trig: sqlite3.Row) -> bool:
    """
    Whether the session woken by `trig` replied to it or wrote a receipt for it.

    A reply is a message caused by the trigger. A receipt is a write on a row
    the trigger refs, such as a Tester's new version of the challenged test,
    which `tester/challenge.md` names as the answer to a right challenge. A
    decision whose refs hold the trigger's id or a row the trigger refs is a
    receipt too, because `vision_keeper/challenge.md` asks for that decision
    as the reply (design 200 pass 2b). The review of design 200 measured 8 Tester re-encodes on nights 138 and
    139 that the first text would have marked.

    A decision is no receipt when the addressee has an `answer` edge to the
    asker (finding 2 of the review of 8d090e2e). A decision that cites a
    message id is a receipt for that message only (finding 8).

    An edge in `RECEIPT_RULES` with "message" counts the reply alone. An edge
    with a table name adds a write on that table to the rules above. The
    propose brief also names a refusing decision as an answer.

    law 6: a question nobody answers climbs, so a barren session leaves it unresolved
    """
    if any(m.cause_id == result.trigger_msg for m in result.messages):
        return True
    rule = _receipt_rule(trig)
    if rule == "message":
        return False
    if rule not in (None, "none") and any(w.table == rule
                                          for w in result.writes):
        return True
    refs = {r for r in json.loads(trig["body_refs"] or "[]") if isinstance(r, str)}
    by_message = None
    for w in result.writes:
        if receipt_of(w)[1] in refs:
            return True
        if w.table == "decisions":
            if by_message is None:
                by_message = _answers_by_message(trig)
            if by_message:
                continue
            cited = w.values.get("refs") or "[]"
            if isinstance(cited, str):
                try:
                    cited = json.loads(cited)
                except ValueError:
                    cited = []
            cited = {c for c in (cited or []) if isinstance(c, str)}
            if result.trigger_msg in cited:
                return True
            if any(conn.execute("SELECT 1 FROM messages WHERE id = ?",
                                (c,)).fetchone() for c in cited):
                continue
            if refs & cited:
                return True
    return False


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

        reads_before = batch_reads(conn, result.writes)
        for w in result.writes:
            before = _subject_state(conn, w)
            changed = _apply_write(conn, w, result.role)
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
                _lift_quarantines(conn, w, _subject_moved(conn, w, before))
        lift_moved_reads(conn, reads_before)

        for m in result.messages:
            conn.execute(
                "INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, "
                "to_role, verb, body_refs, body_text, round_no, seq, status, "
                "unresolved_note) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    m.id, m.cause_id, m.cause_kind,
                    _thread_of(conn, m),
                    result.role, m.to_role, m.verb,
                    json.dumps(m.body_refs), m.body_text,
                    m.round_no, _next_seq(conn, "messages"),
                    m.status, m.unresolved_note,
                ),
            )
            for key, value in (m.config or {}).items():
                conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                             (key, value))

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
            for r in conn.execute(
                    "SELECT id FROM messages WHERE status = 'unresolved' "
                    "AND thread_id = ? AND from_role != ?",
                    (thread, result.role)).fetchall():
                mark_answered(conn, r["id"])


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
        # A session that landed no row and sent nothing did not answer an
        # open trigger that asks either. The trigger goes unresolved and
        # climbs (fact F16, night 170's W17).
        if result.trigger_msg:
            barren = not landed(result)
            trig = conn.execute(
                "SELECT status, verb, body_refs, from_role, to_role, "
                "cause_id, attempts FROM messages WHERE id = ?",
                (result.trigger_msg,)).fetchone()
            was_unresolved = bool(trig and trig["status"] == "unresolved")
            page = _page_under_reply(conn, trig, result)
            missed = _request_missed(conn, trig, result)
            returned = bool(page) and conn.execute(
                "SELECT unresolved_note FROM messages WHERE id = ?",
                (page,)).fetchone()["unresolved_note"] is not None
            # A suspended session keeps its claim and can still reply.
            if (trig and trig["status"] == "open"
                    and result.checkpoint is None
                    and _owes_a_reply(conn, trig)
                    and not (barren and trig["verb"] == "challenge")
                    and not _received(conn, result, trig)):
                # law 6: a question nobody answers climbs, so a barren session leaves it unresolved
                # Frame 174: a session that sent nothing caused by its trigger
                # and wrote no receipt for it did not answer it. Night 127's
                # m72 and m112 were escalations, and the Architect wrote
                # nothing and sent nothing. Invariant I9 found such rows that
                # read answered. Fact F16: the note names the refusal when a
                # call was refused, as night 170's s202.
                note = ": ".join(filter(None, (UNRECEIVED_NOTE,
                                               _why_no_ruling(result, ""))))
                conn.execute(
                    "UPDATE messages SET status = 'unresolved', "
                    "unresolved_note = COALESCE(unresolved_note, ?) WHERE id = ?",
                    (note, result.trigger_msg))
            elif barren and trig and trig["verb"] == "challenge" and trig["status"] == "open":
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
            elif page is not None and returned:
                # A page goes back to the principal once per ask. A miss on a
                # reply to a returned page closes the reply, and the page
                # keeps its note, so no driver answers it again (frame 267,
                # review 1, finding 6: a page the seat cannot land looped).
                mark_answered(conn, result.trigger_msg)
            elif page is not None and (trig["attempts"] or 0) < REPLY_SESSIONS:
                # Frame 267, the first miss: the reply stays open, so the
                # Liaison wakes on it again. The note goes into that wake's
                # head, because the same prompt at temperature zero gives
                # the same calls.
                conn.execute(
                    "UPDATE messages SET unresolved_note = ? WHERE id = ?",
                    (_why_no_ruling(result), result.trigger_msg))
            elif missed and (trig["attempts"] or 0) < REPLY_SESSIONS:
                # Frame 320, the first miss on a new request: frame 267's
                # retry. The request stays open, and its note goes into the
                # next wake's head.
                conn.execute(
                    "UPDATE messages SET unresolved_note = ? WHERE id = ?",
                    (_why_no_ruling(result, REQUEST_NOTHING),
                     result.trigger_msg))
            elif missed:
                # Frame 320, the second miss: the request stops, and one line
                # tells him why. The line goes out as a Liaison chat line,
                # the route `pending_replies` shows him. The request keeps
                # the reason, so the record says why it closed.
                why = _why_no_ruling(result, REQUEST_NOTHING)
                mark_answered(conn, result.trigger_msg, why)
                if not _answers_unread(conn, trig):
                    _tell_unread(conn, trig, result.trigger_msg, why)
            elif not (barren and was_unresolved):
                # A verb outside `OWED_A_REPLY` asks for nothing, so its wake
                # answers it (fact F16). His request takes frame 320's path
                # above, and a page reply takes frame 267's.
                mark_answered(conn, result.trigger_msg)
                # A request that lands after a first miss drops its note, so
                # `closed_requests` lists only the requests that closed
                # unlanded (frame 320, finding 9).
                conn.execute(
                    "UPDATE messages SET unresolved_note = NULL WHERE id = ? "
                    "AND from_role = 'principal' AND verb = 'converse' "
                    "AND (cause_id IS NULL OR cause_id IN (SELECT id FROM "
                    "messages WHERE body_text LIKE ?))",
                    (result.trigger_msg, UNREAD_HEAD + "%"))
                if page is not None:
                    # Frame 267, the second miss: the page goes back to the
                    # principal. It stays open, so `pending_asks` shows it,
                    # and the note puts the reason line on it.
                    conn.execute(
                        "UPDATE messages SET unresolved_note = ? WHERE id = ?",
                        (f"{result.trigger_msg}: {_why_no_ruling(result)}",
                         page))
            # And a compose wake answers its whole round: the trigger was the
            # harvest's carrier, and its siblings were never addressed to a
            # session of their own. Left open they would tip one by one after
            # the reply went out, and Liaison would relay a round it had
            # already relayed. The round's answers ask for nothing, so the
            # wake answers them, as it answers its trigger (fact F16).
            for r in conn.execute(
                    "SELECT id FROM messages "
                    "WHERE status = 'open' AND verb = 'answer' "
                    "  AND thread_id = (SELECT thread_id FROM messages WHERE id = ?) "
                    "  AND EXISTS (SELECT 1 FROM messages q "
                    "              WHERE q.id = (SELECT cause_id FROM messages "
                    "                            WHERE id = ?) AND q.verb = 'ask') "
                    "  AND cause_id IN (SELECT id FROM messages WHERE verb = 'ask')",
                    (result.trigger_msg, result.trigger_msg)).fetchall():
                mark_answered(conn, r["id"])

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
                for r in conn.execute(
                        "SELECT id FROM messages WHERE status = 'unresolved' "
                        "AND thread_id = ? AND from_role = ?",
                        (thread, result.role)).fetchall():
                    mark_answered(conn, r["id"])

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
                    f"  AND q.verb IN ({','.join('?' * len(OWED_A_REPLY))}) "
                    "  AND q.from_role = ?",
                    (result.trigger_msg, *OWED_A_REPLY, result.role)).fetchone()
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
