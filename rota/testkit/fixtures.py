"""
Fixture loader and case runner.

The shape every role test takes: **seed rows -> inject message -> run session ->
assert on deltas.** This module is the machinery for that, and it deliberately
arrives before any role exists, because it needs only the schema — which also
makes it the tool for inspecting anything the scheduler does.

Case format (YAML, per TESTS.md §5):

    id: V2
    tier: T1
    role: vision_keeper
    runs: 5
    pass: 4
    fixture:
      decisions: [{id: R1, text: "deletion rejected: billing history must survive"}]
    inbound: {from: liaison, to: vision_keeper, verb: brief, body_refs: [s2, s3]}
    expect:
      writes:
        items: [{kind: scope, count: ">=1"}]
      messages: []
      calls: [transcript.quote]
    forbidden:
      writes: [glossary_terms, constraints]
      rows: ["items:i_seeded"]
      recipients: [principal, developer, critic]
      calls: [code.write]
    same_session: [items, decisions]

`forbidden:` is not optional garnish. Most laws here are prohibitions, and a case
with no forbidden block is presumed incomplete — so an empty one must be written
deliberately rather than omitted.
"""
from __future__ import annotations

import os

import json
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..core.db import ARTEFACT_TABLES, JUNCTION_TABLES, init_db
from ..llm.llm import Pins
from ..core.runner import RunOutcome, run_session
from ..roles import prompts as prompts_mod
from ..core.scheduler import Wake


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

def seed(conn: sqlite3.Connection, fixture: dict[str, list[dict]]) -> None:
    """
    Insert fixture rows verbatim.

    Fixtures should be tiny — three to five rows, turning on exactly one
    judgement. A nine-billion-parameter model will not fail a structural
    assertion, but it will drown in twenty statements with three plausible
    readings, and then the pass rate measures the fixture rather than the role.
    """
    if "web_cache" in fixture:
        # Not in `schema.sql`, and deliberately: law 13 forbids a timestamp
        # column there, and a fetch record wants one for whoever reads it later.
        # It is evidence like the cassettes rather than an artefact, so it is
        # created on demand — which means a fixture that seeds pages has to ask
        # for the table first.
        from ..core import web
        web.ensure_cache(conn)

    for table, rows in fixture.items():
        if table in ("item_statements", "keypress_verdicts"):
            # A relation that folded into `refs`: `_seed_refs` translates it.
            # His verdict is rows of `rulings` and `ruled_refs`:
            # `_seed_verdict_rulings` writes them. The key is not `verdicts`,
            # because `verdicts` is the Critic's table.
            continue
        dropped = _DROPPED_KEYS.get(table, ())
        for row in rows:
            payload = {k: _encode(v) for k, v in row.items() if k not in dropped}
            cols = ", ".join(payload)
            marks = ", ".join("?" for _ in payload)
            conn.execute(
                f"INSERT INTO {table} ({cols}) VALUES ({marks})",
                list(payload.values()),
            )
    _seed_verdict_rulings(conn, fixture)
    _seed_refs(conn, fixture)


def _seed_verdict_rulings(conn: sqlite3.Connection,
                          fixture: dict[str, list[dict]]) -> None:
    """A landed `rulings` row for each seeded verdict: a message with the
    `verdict` verb, or a row of the fixture key `keypress_verdicts`. That row
    is `{id: <verdict message>, per_item: {ref: verdict}}`, and it gets the
    rows of `seed_verdict`. `principal.land` writes the same rows for a live
    verdict, and `verdict_for` reads them (fact F1). The ask is the
    verdict's cause and `rulings.ask_id` is a foreign key, so a verdict
    with no seeded cause gets no row."""
    for row in fixture.get("messages") or []:
        if not (row.get("verb") == "verdict" and row.get("id")):
            continue
        cause = conn.execute("SELECT cause_id FROM messages WHERE id = ?",
                             (row["id"],)).fetchone()
        if not cause or not cause["cause_id"]:
            continue
        conn.execute(
            "INSERT OR IGNORE INTO rulings (id, ask_id, per_item, words, "
            "status, verdict_id) VALUES (?, ?, '{}', 'seeded verdict', "
            "'landed', ?)", (f"r_{row['id']}", cause["cause_id"], row["id"]))
    # A seeded ruling of another shape names rows the case may not seed, so
    # its rows come from the back-fill, which refuses no ref (the seam
    # design, 1.4).
    from ..core.db import backfill_ruled_refs

    backfill_ruled_refs(conn)
    # After the back-fill, because a verdict on a ruling from his words
    # derives its rows from that ruling's rows.
    for row in fixture.get("keypress_verdicts") or []:
        # A verdict that is the case's inbound message has no row yet, and
        # `rulings.ask_id` is a foreign key. `seed_inbound` seeds it.
        if conn.execute("SELECT 1 FROM messages WHERE id = ?",
                        (row["id"],)).fetchone():
            seed_verdict(conn, row["id"], row.get("per_item") or {})


def seed_verdict(conn: sqlite3.Connection, message_id: str,
                 per_item: dict | str, *, ruling: str | None = None) -> str:
    """Seed his verdict `per_item` in message `message_id` in the shapes
    that `land` writes. A second call replaces the rows. Returns the ruling
    id. Each shape ends with the `landed` rows of `per_item`.

    - A ruling on the ask that his words landed and no verdict names: the
      `apply_rulings` path. No key was pressed, so no keypress row (law 11).
    - An open ruling on the ask, or the ruling `ruling` names: his key
      lands it, with keypress rows beside the reading's rows.
    - Else a landed ruling `r_<message_id>` with keypress rows.

    The ask is the message's cause, or the message itself, because
    `rulings.ask_id` is a foreign key. Like the back-fill, the keypress
    rows refuse no ref, so a test can rule a row that no table holds."""
    # The builders of `land` read rows by name. A test may open its
    # connection with no row factory.
    factory, conn.row_factory = conn.row_factory, sqlite3.Row
    try:
        return _seed_verdict(conn, message_id, per_item, ruling)
    finally:
        conn.row_factory = factory


def _seed_verdict(conn: sqlite3.Connection, message_id: str,
                  per_item: dict | str, ruling: str | None) -> str:
    from types import SimpleNamespace

    from ..core.db import ruled_ref_id
    from ..roles.principal import _insert_landed_rows

    ruled = json.loads(per_item) if isinstance(per_item, str) else dict(per_item)
    rid, words = ruling, False
    if ruling is None:
        msg = conn.execute("SELECT cause_id FROM messages WHERE id = ?",
                           (message_id,)).fetchone()
        if msg is None:
            raise ValueError(f"seed_verdict: seed message {message_id} first")
        ask = msg[0] or message_id
        found = conn.execute(
            "SELECT id, status, reply_id FROM rulings WHERE verdict_id = ? "
            "OR (ask_id = ? AND verdict_id IS NULL "
            "AND status IN ('open', 'landed')) "
            "ORDER BY verdict_id IS NULL, rowid DESC LIMIT 1",
            (message_id, ask)).fetchone()
        if found is not None:
            rid = found["id"]
            words = found["status"] == "landed" and found["reply_id"] is not None
        else:
            rid = f"r_{message_id}"
            conn.execute(
                "INSERT INTO rulings (id, ask_id, per_item, words, status, "
                "verdict_id) VALUES (?, ?, ?, 'seeded verdict', 'landed', ?)",
                (rid, ask, json.dumps(ruled), message_id))
        conn.execute("UPDATE rulings SET status = 'landed', verdict_id = ? "
                     "WHERE id = ?", (message_id, rid))
        conn.execute("UPDATE rulings SET per_item = ? WHERE id = ? "
                     "AND per_item IN ('{}', '')", (json.dumps(ruled), rid))
    conn.execute("DELETE FROM ruled_refs WHERE ruling_id = ? "
                 "AND source IN ('keypress', 'landed')", (rid,))
    if not words:
        for ref, verdict in ruled.items():
            conn.execute(
                "INSERT INTO ruled_refs (id, ruling_id, ref, verdict, words, "
                "source) VALUES (?, ?, ?, ?, 'seeded verdict', 'keypress')",
                (ruled_ref_id(rid, f"keypress:{ref}"), rid, ref, verdict))
    _insert_landed_rows(conn, rid, SimpleNamespace(order=None), message_id,
                        ruled, {}, "")
    return rid


def seed_acts(conn: sqlite3.Connection, ruling_id: str, acts: dict) -> None:
    """Give the rows of a seeded ruling the act, the target kind, the target
    and the words of the object form of `rulings.rule`.

    A seeded ruling gets its rows from the back-fill, and a back-filled row
    has no act. A test of what his ruling permits seeds the act the Liaison
    writes. A row never changes after its insert, so the helper deletes the
    back-filled row and inserts the row again through the one builder (the
    seam design, 1.3 and pass 4). The row keeps its page line, its old text,
    its version and its source. A value can give the page line as `line`."""
    from ..roles.principal import insert_ruling_rows, ruling_rows

    ruling = conn.execute("SELECT per_item, words FROM rulings WHERE id = ?",
                          (ruling_id,)).fetchone()
    per_item = json.loads(ruling["per_item"] or "{}") if ruling else {}
    for ref, value in acts.items():
        old = conn.execute(
            "SELECT verdict, line, old_text, ref_version, source FROM ruled_refs "
            "WHERE ruling_id = ? AND ref = ?",
            (ruling_id, ref)).fetchone()
        value = dict(value)
        line = value.pop("line", None)
        value.setdefault("verdict", old["verdict"] if old else per_item.get(ref))
        conn.execute("DELETE FROM ruled_refs WHERE ruling_id = ? AND ref = ?",
                     (ruling_id, ref))
        rows = ruling_rows(conn, ruling_id, None, {ref: value},
                           words=ruling["words"] if ruling else "")
        for row in rows:
            if line is not None:
                row["line"] = line
            if old is not None:
                row["line"] = row["line"] if row["line"] is not None else old["line"]
                row["old_text"] = old["old_text"]
                row["ref_version"] = old["ref_version"]
                row["source"] = old["source"]
        insert_ruling_rows(conn, rows)
    conn.commit()


def _encode(value: Any) -> Any:
    return json.dumps(value) if isinstance(value, (list, dict)) else value


# The refs relation from the words a case seeds (frame 21).
#
# A case file seeds `provenance:`, `source_refs:`, `term_refs:` and
# `item_statements:` the way the columns took them. The columns and the
# table are gone. The loader translates each seed into refs rows, so the
# view derives the word the case names and the case files do not change.
# The INSERT leaves the seeds out. A seeded `decided` row rests on one landed
# fixture ruling. A seeded `observed` row rests on one fixture grain. A
# seeded `cited` row with no reference on file rests on one fixture
# reference. The fixture ruling needs an ask: `rulings.ask_id` is a foreign
# key, so one answered message is seeded with it, in a thread of its own,
# and the settled verdict that answers it: the audit reads "answered means
# an answer exists".
FIXTURE_GRAIN = "@fixture"
FIXTURE_RULING = "r_fixture"
FIXTURE_ASK = "m_fixture_ruling"
FIXTURE_VERDICT = "m_fixture_verdict"
FIXTURE_REFERENCE = "ref_fixture"

_PROVENANCE_TABLES = ("items", "glossary_terms", "constraints", "model_areas",
                      "frame_rulings")
_SOURCE_REF_TABLES = ("glossary_terms", "constraints", "model_areas")
_TERM_REF_TABLES = ("criteria", "business_rules")

# The keys a case seeds that no column takes. `_seed_refs` reads them.
_DROPPED_KEYS = {
    **{t: ("provenance", "source_refs") for t in _SOURCE_REF_TABLES},
    "items": ("provenance",),
    "frame_rulings": ("provenance",),
    **{t: ("term_refs",) for t in _TERM_REF_TABLES},
}


def _id_list(value: Any) -> list[str]:
    """A seeded JSON list column, as ids. A string is JSON text."""
    if isinstance(value, str):
        try:
            value = json.loads(value) if value.strip().startswith("[") else []
        except ValueError:
            return []
    if not isinstance(value, list):
        return []
    return [v for v in value if isinstance(v, str)]


def _is_row(conn: sqlite3.Connection, table: str, ref: str) -> bool:
    return conn.execute(f"SELECT 1 FROM {table} WHERE id = ?",
                        (ref,)).fetchone() is not None


def _source_kind(conn: sqlite3.Connection, ref: str) -> str:
    """What a `source_refs` id names: a reference, a statement, or a grain."""
    if _is_row(conn, "references_", ref):
        return "reference"
    if _is_row(conn, "statements", ref):
        return "statement"
    return "grain"


def _seed_refs(conn: sqlite3.Connection, fixture: dict[str, list[dict]]) -> None:
    refs: list[tuple[str, str, str, str]] = []
    need_ruling = need_reference = False
    for table in _PROVENANCE_TABLES:
        for row in fixture.get(table) or []:
            rid = row.get("id")
            if rid is None:
                continue
            # A `model_areas` seed with no word is observed, as the column's
            # default was.
            word = row.get("provenance",
                           "observed" if table == "model_areas" else None)
            if word == "observed":
                refs.append((table, rid, "grain", FIXTURE_GRAIN))
            elif word in ("decided", "ratified"):
                refs.append((table, rid, "ruling", FIXTURE_RULING))
                need_ruling = True
            elif word == "cited":
                cited = [r for r in _id_list(row.get("source_refs"))
                         if _is_row(conn, "references_", r)]
                if not cited:
                    refs.append((table, rid, "reference", FIXTURE_REFERENCE))
                    need_reference = True
    for table in _SOURCE_REF_TABLES:
        for row in fixture.get(table) or []:
            rid = row.get("id")
            for ref in _id_list(row.get("source_refs")) if rid else []:
                refs.append((table, rid, _source_kind(conn, ref), ref))
    for table in _TERM_REF_TABLES:
        for row in fixture.get(table) or []:
            rid = row.get("id")
            for ref in _id_list(row.get("term_refs")) if rid else []:
                refs.append((table, rid, "term", ref))
    for row in fixture.get("item_statements") or []:
        if row.get("item_id") and row.get("statement_id"):
            refs.append(("items", row["item_id"], "statement", row["statement_id"]))
    if not refs:
        return
    if need_ruling:
        # The ask, and the verdict that answers it, as `principal.land`
        # writes a settled verdict. No prompt, wake or predicate reads
        # either row: `status = 'answered'`, `to_role = 'liaison'`,
        # `body_text IS NULL`, `body_refs = '[]'`, and a thread of their
        # own. The ask has no cause. The verdict's cause is the ask, and a
        # reader follows a cause from a wake's own message only.
        conn.execute(
            "INSERT OR IGNORE INTO messages (id, cause_kind, thread_id, "
            "from_role, to_role, verb, body_refs, seq, status) VALUES "
            "(?, 'conversation', ?, 'principal', 'liaison', 'converse', '[]', "
            "0, 'answered')", (FIXTURE_ASK, FIXTURE_ASK))
        conn.execute(
            "INSERT OR IGNORE INTO messages (id, cause_id, cause_kind, "
            "thread_id, from_role, to_role, verb, body_refs, seq, status) "
            "VALUES (?, ?, 'message', ?, 'principal', 'liaison', 'verdict', "
            "'[]', 0, 'answered')", (FIXTURE_VERDICT, FIXTURE_ASK, FIXTURE_ASK))
        conn.execute(
            "INSERT OR IGNORE INTO rulings (id, ask_id, per_item, words, "
            "status, verdict_id) VALUES (?, ?, '{}', 'seeded as decided', "
            "'landed', ?)", (FIXTURE_RULING, FIXTURE_ASK, FIXTURE_VERDICT))
    if need_reference:
        conn.execute(
            "INSERT OR IGNORE INTO references_ (id, url, claim, asked_by) "
            "VALUES (?, 'fixture://cited', 'seeded as cited', 'fixture')",
            (FIXTURE_REFERENCE,))
    conn.executemany(
        "INSERT OR IGNORE INTO refs (src_table, src_id, kind, target) "
        "VALUES (?, ?, ?, ?)", refs)


def seed_provenance(conn: sqlite3.Connection, table: str, row_id: str,
                    word: str) -> None:
    """
    The refs rows the loader writes for a `provenance:` seed, for a test
    that seeds by SQL.

    The same translation `seed` gives a case file: a `decided` row rests on
    the fixture ruling, an `observed` row on the fixture grain, a `cited`
    row on the fixture reference. No owner table carries the word, so this
    is the one way a test seeds it. Idempotent.
    """
    _seed_refs(conn, {table: [{"id": row_id, "provenance": word}]})


def seed_ref(conn: sqlite3.Connection, src_table: str, src_id: str,
             kind: str, target: str) -> None:
    """
    One refs row, for a test that seeds by SQL: a `term` ref where a test
    once seeded `term_refs`, a `statement` ref where it once seeded
    `item_statements`. Idempotent.
    """
    conn.execute(
        "INSERT OR IGNORE INTO refs (src_table, src_id, kind, target) "
        "VALUES (?, ?, ?, ?)", (src_table, src_id, kind, target))


#: Each case's unfilled block, by case id, with the parser its file needed.
#: `for_run` fills the block again under a run number, so the five runs of a
#: case are five problems (frame 66, 2026-09-23). The block is gone once the
#: case is parsed, so `load_case` keeps it here. No caller mutates a loaded
#: case, so one registry serves every reader (observed: frame 66's second
#: look, 2026-09-23).
_RAW: dict[str, tuple[str, object]] = {}


def for_run(case: dict, run_no: int) -> dict:
    """
    The case as run `run_no` composes it, with every hole salted by the number.

    A case a test builds by hand carries no registered block, and it comes
    back unchanged. So the hand-built case runs exactly as it runs today.
    """
    entry = _RAW.get(case.get("id", ""))
    if entry is None:
        return case
    text, parse = entry
    return parse(fill(text, case["id"], run_no))[0]


def load_case(path: str | Path, *, raw: bool = False) -> dict:
    """
    Parse a case file, filling its `{{holes}}` unless `raw`.

    Filling happens per case rather than per file, so two cases in one file
    cannot end up sharing an id and a model cannot learn one mapping and apply
    it to the next case. That means parsing twice: once to find the boundaries,
    once with each case's own substitution applied.
    """
    text = Path(path).read_text(encoding="utf-8")
    if str(path).endswith((".yaml", ".yml")):
        try:
            import yaml
        except ImportError as exc:                      # pragma: no cover
            raise RuntimeError("PyYAML needed for .yaml cases") from exc
        parse = yaml.safe_load
    else:
        parse = json.loads

    if raw or "<" not in text:
        return parse(text)

    # Split on the top-level `- id:` boundaries so each case fills alone.
    out, buffer, current = [], [], None
    def flush():
        if current is not None:
            block = chr(10).join(buffer)
            _RAW[current] = (block, parse)
            out.append(parse(fill(block, current))[0])
    for line in text.splitlines():
        if line.startswith("- id: "):
            flush()
            current = fill(line[6:].strip(), "")   # the id itself holds no holes
            buffer = [line]
        elif current is not None:
            buffer.append(line)
    flush()
    return out


# ---------------------------------------------------------------------------
# Delta capture
# ---------------------------------------------------------------------------

@dataclass
class Delta:
    """What one session changed. The assertion target for every role test."""
    session_id: str
    committed: bool
    writes: dict[str, list[str]] = field(default_factory=dict)
    messages: list[dict] = field(default_factory=list)
    tool_calls: list[str] = field(default_factory=list)
    versions_moved: dict[str, int] = field(default_factory=dict)
    rows: dict[str, list[dict]] = field(default_factory=dict)   # the written rows' content

    def tables_written(self) -> set[str]:
        return set(self.writes)

    def recipients(self) -> set[str]:
        return {m["to_role"] for m in self.messages}


# The key columns a junction table's writer joins with ":" into the receipt
# label. Each entry copies the writer's f-string: `batches_group`,
# `model_amend`, `surveys_attest`, `batches_annotate`, `batches_guess`,
# `code_commit`, `batches_judge_touch` and `api.stage_ref`.
_JUNCTION_LABELS: dict[str, tuple[str, ...]] = {
    "batch_tickets": ("batch_id", "ticket_id"),
    "constraint_bindings": ("constraint_id", "grain"),
    "survey_citations": ("survey_id", "grain"),
    "batch_touch": ("batch_id", "grain"),
    "touch_guesses": ("item_id", "item_ver", "ruling_id", "grain"),
    "touch_strays": ("batch_id", "commit_sha", "path"),
    "drop_notes": ("batch_id", "path"),
    "batch_dep_facts": ("before_batch", "after_batch"),
    "schedule_deps": ("before_batch", "after_batch"),
    "refs": ("src_table", "src_id", "kind", "target"),
}


def _junction_rows(conn: sqlite3.Connection, table: str,
                   labels: list[str]) -> list[dict]:
    """
    The rows a session's receipt labels name in a junction table.

    A label names the row whose key columns, joined with ":", equal the label.
    A label that names no row, a ":*" clear among them, loads nothing.

    `SELECT ... WHERE id IN` raised on these tables, which have no `id`, and
    the except gave an empty list. So a `text_excludes` on `batch_touch`
    passed on no rows (frame 190, pass 3c, the re-annotate case). A parent's
    rows for a label that names no row were the rows of other sessions (the
    delta review of afecf14a, finding 4).
    """
    cols = _JUNCTION_LABELS.get(table)
    out: list[dict] = []
    seen: set[tuple] = set()
    for label in labels:
        if label.endswith(":*") or not cols:
            continue
        found: list[dict] = []
        try:
            joined = " || ':' || ".join(f'"{c}"' for c in cols)
            found = [dict(r) for r in conn.execute(
                f"SELECT * FROM {table} WHERE {joined} = ?", (label,))]
        except sqlite3.Error:
            found = []
        for row in found:
            key = tuple(sorted((k, str(v)) for k, v in row.items()))
            if key not in seen:
                seen.add(key)
                out.append(row)
    return out


def capture(conn: sqlite3.Connection, session_id: str,
            versions_before: dict[str, int],
            messages_before: set[str] | None = None) -> Delta:
    writes: dict[str, list[str]] = {}
    for r in conn.execute(
        "SELECT table_name, row_id FROM receipts WHERE session_id = ? ORDER BY table_name",
        (session_id,),
    ):
        writes.setdefault(r["table_name"], []).append(r["row_id"])
    # `session_commit` writes no receipt for a ruled_refs row, because
    # ruled_refs is not an artefact table (review p5, finding 1). The rows
    # of a reading hang off the session's rulings receipts, so count them
    # through those receipts. A case that expects ruled_refs writes then
    # measures the rows that landed.
    refs = [r[0] for r in conn.execute(
        "SELECT id FROM ruled_refs WHERE source = 'reading' AND ruling_id IN "
        "(SELECT row_id FROM receipts WHERE session_id = ? AND table_name = 'rulings') "
        "ORDER BY id",
        (session_id,),
    )]
    if refs:
        writes["ruled_refs"] = refs

    # Everything this role sent *in this session*, and nothing else.
    #
    # This was "every message from this role", which quietly included the ones
    # the fixture seeded. A case that seeds a quarantined Liaison->Terminologist
    # message and then forbids messaging Terminologist failed 0/5 against a
    # session whose entire trace was one call to `msg.present_principal`: the
    # forbidden message was in the fixture, put there by the case itself.
    #
    # Messages carry no session id — they are addressed, not owned — so the
    # boundary is drawn by what existed before the session started.
    before = messages_before if messages_before is not None else set()
    messages = [dict(r) for r in conn.execute(
        "SELECT id, to_role, verb, body_refs, body_text, cause_id, status FROM messages "
        "WHERE from_role = (SELECT role FROM sessions WHERE id = ?) "
        "ORDER BY seq", (session_id,),
    ) if r["id"] not in before]

    tool_calls = [r["fn"] for r in conn.execute(
        "SELECT fn FROM tool_calls WHERE session_id = ? ORDER BY seq", (session_id,))]

    committed = bool(conn.execute(
        "SELECT committed FROM sessions WHERE id = ?", (session_id,)).fetchone() or [0])

    moved = {}
    for r in conn.execute("SELECT table_name, version FROM artefact_versions"):
        before = versions_before.get(r["table_name"], 0)
        if r["version"] != before:
            moved[r["table_name"]] = r["version"] - before

    # The rows themselves, for a case that asserts on a column: the surface a
    # criterion names is a value, not an id (2026-09-09).
    rows: dict[str, list[dict]] = {}
    for table, ids in writes.items():
        if not ids:
            continue
        if table in JUNCTION_TABLES:
            rows[table] = _junction_rows(conn, table, ids)
            continue
        try:
            marks = ",".join("?" * len(ids))
            rows[table] = [dict(r) for r in conn.execute(
                f"SELECT * FROM {table} WHERE id IN ({marks})", tuple(ids))]
        except sqlite3.Error:
            rows[table] = []

    return Delta(session_id=session_id, committed=committed, writes=writes,
                 messages=messages, tool_calls=tool_calls, versions_moved=moved,
                 rows=rows)


def snapshot_versions(conn: sqlite3.Connection) -> dict[str, int]:
    return {r["table_name"]: r["version"]
            for r in conn.execute("SELECT table_name, version FROM artefact_versions")}


# ---------------------------------------------------------------------------
# Assertions
# ---------------------------------------------------------------------------

_COUNT = re.compile(r"^(>=|<=|==|>|<)?\s*(\d+)$")


def _count_ok(actual: int, spec: Any) -> bool:
    """
    A comparator, or a range.

    Ranges exist because `">=1"` was the only thing most expectations said, and
    a lower bound alone measures that something happened rather than that it was
    right. `L1-LI-segment` asserted `statements: {count: ">=1"}` and was green at
    5/5 while turning one short sentence into fourteen statements -- every one of
    which the roles downstream would have had to carry.
    """
    if spec is None:
        return actual > 0
    text = str(spec).strip()
    if ".." in text:
        lo, _, hi = text.partition("..")
        return int(lo) <= actual <= int(hi)
    m = _COUNT.match(text)
    if not m:
        return False
    op, n = m.group(1) or "==", int(m.group(2))
    return {
        "==": actual == n, ">=": actual >= n, "<=": actual <= n,
        ">": actual > n, "<": actual < n,
    }[op]


def check(case: dict, delta: Delta, refused: dict[str, int] | None = None,
          notes: list[str] | None = None) -> list[str]:
    """
    Structural assertions only. Never on prose.

    Which tables changed, which rows appeared, who received which message type,
    what refs a row carries — those are checkable. Whether the wording is good is
    not, and pretending otherwise is how a suite starts measuring the model's
    prose style instead of the law.

    `refused` counts the calls a guard threw out, per function. It exists because
    the two halves of one `forbidden:` block were scoring different things:
    `writes` reads the committed database, so a refused write never counted,
    while `calls` reads the tool log, which records the attempt — `_CALL_LOG`
    appends before the implementation runs. So `forbidden: writes: [decisions]`
    meant "did not write one" and `forbidden: calls: [decisions.author]` meant
    "did not reach for one", in the same block, with nothing saying so.

    Effects win, matching `writes`: a guard that fires is the system working, and
    scoring it as a violation marks a role down for something that did not
    happen. The reach is still worth knowing — a brief that steers into a wall is
    a weak brief — so it is reported rather than dropped.
    """
    problems: list[str] = []
    # Out-param rather than a second return value: everything in `problems`
    # fails the case, and a refused reach must not, but it must also not vanish.
    notes = notes if notes is not None else []
    expect = case.get("expect", {})
    forbidden = case.get("forbidden", {})

    # Several modes have two right answers and no third. Vision Keeper handed a
    # refactor proposal either asserts it as an item or authors a decision
    # refusing it; what it must not do is nothing, because Architect is blocked
    # and will not ask twice. Written as two separate cases that would be two
    # fixtures pretending to be different situations, so the alternation lives
    # here instead: at least one branch must hold, and "neither" is the failure
    # the case exists to catch.
    branches = expect.get("any_of") or []
    if branches:
        if all(check({"expect": b, "forbidden": {}}, delta) for b in branches):
            problems.append(
                "none of the permitted answers was given; "
                f"wrote {sorted(delta.writes)}, sent "
                f"{[(m['to_role'], m['verb']) for m in delta.messages]}")

    for table, specs in (expect.get("writes") or {}).items():
        rows = delta.writes.get(table, [])
        for spec in (specs if isinstance(specs, list) else [specs]):
            want = spec.get("count") if isinstance(spec, dict) else None
            if not _count_ok(len(rows), want):
                problems.append(
                    f"expected writes to {table} ({want or '>0'}), got {len(rows)}")
            # A row the case names, the way a message spec names refs. The
            # account case needs it: the count alone cannot tell "the whole,
            # then the behaviours" from three behaviours.
            need = set(spec.get("ids_include") or []) if isinstance(spec, dict) else set()
            if need and not need <= set(rows):
                problems.append(
                    f"expected writes to {table} to include {sorted(need)}, "
                    f"got {sorted(rows)}")
            # A value the written rows must carry, as a substring of the row's
            # JSON: the surface a criterion names, the sense a term gets.
            words = spec.get("text_includes") or [] if isinstance(spec, dict) else []
            if words:
                # The rows as JSON, and every string value verbatim after
                # it: a column that holds JSON of its own (`rulings.per_item`)
                # is escaped inside the dump and a case cannot spell that.
                written = delta.rows.get(table, [])
                blob = json.dumps(written, default=str) + " " + " ".join(
                    v for row in written for v in row.values() if isinstance(v, str))
                missing = [w for w in words if w not in blob]
                if missing:
                    problems.append(
                        f"expected writes to {table} to carry {missing}; "
                        f"the rows carry {blob[:200]}")
            # A field every written row must carry non-empty: the survey
            # spike (2026-09-15) scores a constraint by whether it cites a
            # source line, so a row with source_refs '[]' is noise.
            fields = spec.get("fields_nonempty") or [] if isinstance(spec, dict) else []
            if fields:
                written = delta.rows.get(table, [])
                for row in written:
                    for f in fields:
                        v = row.get(f)
                        if v in (None, "", "[]", "{}", []):
                            problems.append(
                                f"a {table} row without {f}: "
                                f"{json.dumps(row, default=str)[:160]}")
            # One of several values the rows must carry: the survey spike
            # accepts any called symbol of the area as the surface, not one.
            anyw = spec.get("text_includes_any") or [] if isinstance(spec, dict) else []
            if anyw:
                written = delta.rows.get(table, [])
                blob = json.dumps(written, default=str) + " " + " ".join(
                    v for row in written for v in row.values() if isinstance(v, str))
                if not any(w in blob for w in anyw):
                    problems.append(
                        f"expected writes to {table} to carry one of {anyw}; "
                        f"the rows carry {blob[:200]}")
            # One of several words in each row's own `text`, case folded.
            # The blob above passes when one row or one id holds a word, so
            # s185's two behaviour criteria passed beside its docstring one
            # (frame 322, review 2, finding 2).
            each = (spec.get("each_text_includes_any") or []
                    if isinstance(spec, dict) else [])
            if each:
                folded = [w.casefold() for w in each]
                for row in delta.rows.get(table, []):
                    said = str(row.get("text") or "")
                    if not any(w in said.casefold() for w in folded):
                        problems.append(
                            f"a {table} row {row.get('id')} names none of "
                            f"{each}: {said[:160]!r}")
            banned = spec.get("text_excludes") or [] if isinstance(spec, dict) else []
            if banned:
                written = delta.rows.get(table, [])
                blob = json.dumps(written, default=str) + " " + " ".join(
                    v for row in written for v in row.values() if isinstance(v, str))
                present = [w for w in banned if w in blob]
                if present:
                    problems.append(
                        f"expected writes to {table} not to carry {present}; "
                        f"the rows carry {blob[:200]}")

    for spec in expect.get("messages") or []:
        matches = [
            m for m in delta.messages
            if m["to_role"] == spec.get("to", m["to_role"])
            and m["verb"] == spec.get("verb", m["verb"])
            # A question born unresolved differs from `cannot`'s open one
            # only here (frame 81).
            and m.get("status") == spec.get("status", m.get("status"))
        ]
        if not _count_ok(len(matches), spec.get("count")):
            problems.append(f"expected message {spec}, got {len(matches)} match(es)")
        for m in matches:
            need = set(spec.get("refs_include") or [])
            if need and not need <= set(json.loads(m["body_refs"])):
                problems.append(f"message {m['id']} missing refs {need}")
            # The refs whole, when a door fixes them: the park ask carries
            # the item alone (frame 87).
            if "refs_equal" in spec and json.loads(m["body_refs"]) != spec["refs_equal"]:
                problems.append(f"message {m['id']} carries refs "
                                f"{json.loads(m['body_refs'])}, not {spec['refs_equal']}")
            # A fact the words must name, as for written rows: an id or a
            # key the reader needs, never a phrasing (frame 87, the park ask).
            said = m.get("body_text") or ""
            missing = [w for w in spec.get("text_includes") or [] if w not in said]
            if missing:
                problems.append(f"message {m['id']} does not name {missing}: "
                                f"{said[:200]!r}")
            anyw = spec.get("text_includes_any") or []
            if anyw and not any(w in said for w in anyw):
                problems.append(f"message {m['id']} names none of {anyw}: "
                                f"{said[:200]!r}")

    # A judgement is only as good as what it was grounded in. Two thirds of the
    # L1 obligation set are reads — `code.read`, `criteria.load`, `model.load` —
    # and none of them deserves a case of its own, because reading is a means,
    # never an end. They ride here instead: a verdict emitted without loading the
    # criterion it judges against is a guess that happened to be checkable.
    called = delta.tool_calls
    for fn in expect.get("calls") or []:
        if fn not in called:
            problems.append(f"expected a call to {fn}; called {sorted(set(called))}")

    # --- the negative half ---------------------------------------------------
    if "forbidden" not in case:
        problems.append("case declares no `forbidden:` block and is presumed incomplete")

    for table in forbidden.get("writes") or []:
        if table in delta.writes:
            problems.append(f"forbidden write to {table}: {delta.writes[table]}")

    # Row-granular, because table-granular cannot say what the seat's
    # wrong-answer intake needs: answering correctly *writes* to the table,
    # and amending the seeded row is the failure. `receipts` records every
    # artefact write with its row id -- inserts and updates alike -- so
    # "this row, untouched" is a fact the committed database already holds.
    # Spelled `table:row_id`, the same way a citation names a row.
    # A value no written row may carry: the tip function as a split's surface.
    for word in forbidden.get("text_in_writes") or []:
        blob = json.dumps(delta.rows, default=str)
        if word in blob:
            problems.append(f"forbidden text {word!r} in a written row")
    for ref in forbidden.get("rows") or []:
        table, _, row_id = ref.partition(":")
        if row_id in delta.writes.get(table, []):
            problems.append(f"forbidden change to {ref}")

    for role in forbidden.get("recipients") or []:
        if role in delta.recipients():
            problems.append(f"forbidden message to {role}")

    # Verb-granular, because role-granular could not say what several cases
    # need. Liaison confirming a segmentation to the principal is required;
    # Liaison *clarifying* to them unprompted is the failure. Forbidding the
    # recipient forbids both, and a case that cannot separate them either
    # passes a real fault or fails correct behaviour.
    for spec in forbidden.get("messages") or []:
        for m in delta.messages:
            if (m["to_role"] == spec.get("to", m["to_role"])
                    and m["verb"] == spec.get("verb", m["verb"])):
                problems.append(
                    f"forbidden message {m['verb']} to {m['to_role']}")

    for fn in forbidden.get("calls") or []:
        # Counted, not tested for membership. A call can be thrown out on one
        # turn and land on the next with corrected arguments, so "it appears in
        # the errors" is not the same as "it never happened". The log holds
        # every reach, refused or landed: `_bind` logs a tool call before its
        # guards and `stage` logs a send before its guards (2026-09-14; until
        # then a refused send was not logged, and qwen2.5:14b's landed
        # forbidden challenge, refused twice after, scored as none).
        landed = called.count(fn) - (refused or {}).get(fn, 0)
        if landed > 0:
            problems.append(f"forbidden call to {fn}")
        elif fn in called:
            notes.append(f"reached for forbidden {fn}; the guard refused it")

    for table in forbidden.get("versions") or []:
        if table in delta.versions_moved:
            problems.append(f"forbidden version bump on {table}")

    if expect.get("messages") == [] and delta.messages:
        problems.append(f"expected no messages, got {[m['verb'] for m in delta.messages]}")

    return problems


def check_same_session(conn: sqlite3.Connection, tables: list[str],
                       session_id: str) -> list[str]:
    """Law 11: several laws are *about* what happens inside a single commit."""
    written = {r["table_name"] for r in conn.execute(
        "SELECT DISTINCT table_name FROM receipts WHERE session_id = ?", (session_id,))}
    return [f"{t} not written in the same session" for t in tables if t not in written]


# ---------------------------------------------------------------------------
# Running a case
# ---------------------------------------------------------------------------

@dataclass
class CaseResult:
    case_id: str
    run: int
    passed: bool
    problems: list[str] = field(default_factory=list)
    delta: Delta | None = None
    outcome: RunOutcome | None = None
    # Things worth knowing that are not failures -- a forbidden call the guard
    # threw out, which says the brief steered into a wall while the system held.
    notes: list[str] = field(default_factory=list)
    # Every system text the model received, one per session. A chain has two,
    # and `outcome` keeps only the leg the chain is scored against. The
    # register records a run against this, so kept here rather than derived.
    systems: list[str] = field(default_factory=list)
    # How many calls reached the model. `RecordingBackend.misses` counts
    # exactly the calls that reach its inner backend, and a chain sums its
    # legs. The register writes `live = 1` when this is above zero, because a
    # replay and a first-seen transcript looked the same in the table (frame
    # 66, 2026-09-23).
    live_calls: int = 0
    # How many of the first completions came from the case's `replies:` and
    # not from the model. The transcript marks them.
    scripted: int = 0

    def system_text(self) -> str:
        """
        What the model was told, whole, and both legs of a chain.

        Joined the way `instructions_for` joins a chain's two briefs, because
        the two must agree: either leg can be why a chain stopped working, so
        either leg's text must be able to stale it.
        """
        return "\n\n".join(self.systems)

    def transcript(self) -> list[dict]:
        """What the model said and what came back, turn by turn.

        A pass rate says a case is failing. Only this says whether the case was
        unfair, the role under-briefed, or the model out of its depth — which is
        all of the remaining work, so it is kept with the verdict rather than
        printed once and lost."""
        # The same string the history shows: the text, then one line per
        # native call. A native turn's text is empty, and a refused native
        # call reaches no `tool_calls` row (frame 323).
        from ..core.runner import _with_native_lines

        said = self.outcome.completions if self.outcome else []
        native = (getattr(self.outcome, "native", None) or []) if self.outcome else []
        said = [_with_native_lines(t, native[i] if i < len(native) else [])
                for i, t in enumerate(said)]
        out = [{"say": t, "scripted": True} if i < self.scripted else {"say": t}
               for i, t in enumerate(said)]
        if self.delta:
            out.append({"called": self.delta.tool_calls,
                        "wrote": {k: len(v) for k, v in self.delta.writes.items()},
                        "sent": [(m["to_role"], m["verb"]) for m in self.delta.messages]})
        if self.outcome and self.outcome.errors:
            out.append({"errors": self.outcome.errors})
        return out


def _with_repo(conn, case: dict, db_path: Path, run_no: int = 1):
    """
    A real checkout, a worktree for the batch, and a diff to judge.

    Critic reads a diff; Architect reads source; Developer writes files. A case
    for any of them against a database with no repository is a case where the
    role correctly declines to act, and reads as a failure. The first Critic
    cases failed exactly that way — no worktree, so `code.read` returned an
    empty diff, and refusing to judge what it cannot see is the right answer.
    """
    from . import gitfixture

    spec = case["repo"]
    root = Path(db_path).parent
    # Per *run*, not per case. Five runs of a chain share one temporary
    # directory, so a repo named for the case alone is the same path each
    # time -- and a second `create` over an existing checkout commits nothing,
    # which git calls an error. The failure surfaced as "nothing to commit,
    # working tree clean" from a fixture that builds perfectly on its own.
    repo = gitfixture.make(root, name=f"{case.get('id', 'case')}_{run_no}_repo")
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
                 "('project_root', ?)", (str(repo.root),))

    # A survey case needs the mechanical half of onboarding to have happened:
    # an index to survey, areas to survey one of, and constraint zero over the
    # rest. Requested rather than automatic — it costs a tree-sitter parse of
    # the whole checkout, and only three modes need it.
    if spec.get("onboard"):
        from ..onboarding import boot

        boot.onboard(conn, repo.root)

        # Loop 5's shape, requested by two keys. `surveyed:` stamps areas as
        # surveyed at the tree onboarding just indexed -- a record the way
        # attest writes one, hash and all, so the fixture means "this area
        # was closed". `change:` then moves the tree: root edits, committed,
        # re-indexed the way `rota refresh` does it -- so the freshness view
        # reopens exactly the areas whose content moved, and a re-survey
        # session can be recorded rather than hand-waved.
        for role, area in (spec.get("surveyed") or []):
            from ..roles.api import area_content_hash

            conn.execute(
                "INSERT INTO survey_records (id, area, outcome, area_hash) "
                "VALUES (?, ?, 'found', ?)",
                (f"{role}:{area}", area, area_content_hash(conn, area)))
        if spec.get("change"):
            from ..onboarding import indexer

            for rel, body in spec["change"].items():
                repo.edit(repo.root, rel, body)
            moved = repo.commit_in(repo.root, "the tree moved past the survey")
            indexer.build(conn, repo.root)
            boot.repin(conn, repo.root)
            # `rota refresh` harvests the moved tree after its index (the
            # review of frame 362, low 9). Without this run a line that the
            # change adds is no witness (frame 362, pass 4d).
            from ..onboarding import harvest

            harvest.record(conn, repo.root, moved)

    batch_id = spec.get("batch") if isinstance(spec, dict) else None
    if batch_id:
        tree = repo.worktree(batch_id)
        conn.execute("UPDATE batches SET worktree = ? WHERE id = ?",
                     (str(tree), batch_id))
        for rel, body in (spec.get("edit") or {}).items():
            repo.edit(tree, rel, body)
        if spec.get("edit"):
            sha = repo.commit_in(tree, spec.get("message", "the batch's work"))
            conn.execute("UPDATE batches SET head_commit = ? WHERE id = ?",
                         (sha, batch_id))
            # A stray row a case seeds against `HEAD` names the commit the
            # fixture just made; the case cannot know the sha.
            conn.execute("UPDATE touch_strays SET commit_sha = ? "
                         "WHERE batch_id = ? AND commit_sha = 'HEAD'", (sha, batch_id))
            # A red run seeded against `HEAD` names the edit commit, so
            # `tests.load` can say what changed since the run (observed: the
            # ten-reds record, 2026-09-24).
            conn.execute("UPDATE test_runs SET commit_sha = ? "
                         "WHERE batch_id = ? AND commit_sha = 'HEAD'", (sha, batch_id))
        # `index_batch:` leaves the run in the state a delivery night has.
        # `onboard:` alone indexes the main checkout before the worktree
        # exists, so a probe of a name the batch wrote came back empty
        # (frame 326, review 1, finding 1).
        if spec.get("index_batch"):
            _delivery_index(conn, repo.root, tree, batch_id,
                            onboarded=bool(spec.get("onboard")))
    return repo


def _delivery_index(conn, root: Path, tree: Path, batch_id: str, *,
                    onboarded: bool) -> None:
    """
    The index and the onboarding record of a night at delivery.

    A night pins the partition over main, finishes onboarding, and then
    re-indexes the batch worktree after each Developer commit. The index
    alone left every row in area `.` and the phase at `frame`, which holds
    delivery and offered `tick:frame` and `tick:constraint_zero` to a chain
    (frame 326, review 1b, finding 1). So this writes the end state of each
    phase as a record, and not by `boot.onboard`. No lexicon is built, and
    no constraint zero row is written, so a case's seeded constraints stay
    the only ones.
    """
    from ..core import scheduler as S
    from ..onboarding import areas as areas_mod, indexer
    from ..roles.api import area_content_hash

    if not onboarded:
        indexer.build(conn, root)
        areas_mod.pin(conn, areas_mod.propose(conn))
        indexer.stamp_area_hashes(conn)
    # The call `runner._refresh_index` makes after a Developer commit.
    indexer.refresh(conn, tree, main=False, batch_id=batch_id)

    def record(rid: str, area: str, area_hash: str = "") -> None:
        conn.execute("INSERT OR IGNORE INTO survey_records (id, area, outcome, "
                     "area_hash) VALUES (?, ?, 'none_found', ?)",
                     (rid, area, area_hash))

    # The frame was judged, and its re-pin already ran: a second re-pin
    # would rebuild the lexicon and constraint zero over main.
    record(f"system:{S.FRAME}", S.FRAME)
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
                 "('frame_repinned', '1')")
    for area in (S.PROGRAM, S.REORIENT, S.BLINDSPOTS, *S.prose_areas(conn)):
        record(f"system:{area}", area)
    # With `onboard:` too, the lexicon exists and its words are owed. A
    # night settles each one before delivery.
    for word in S.pending_terms(conn):
        record(f"terminologist:{S.TERM_PREFIX}{word}", S.TERM_PREFIX + word)
    # A survey per area and role, at the area's content now. Constraint
    # zero then binds no grain, and `tick:constraint_zero` stays quiet.
    areas = [r["area"] for r in conn.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL")]
    for area in areas:
        for role in S.survey_order():
            record(f"{role}:{area}", area, area_content_hash(conn, area))
    if onboarded:
        # `boot.onboard` bound constraint zero to every coded area, and the
        # surveys above now cover each one.
        from ..onboarding import boot

        boot.refresh_constraint_zero(conn)
    for rel in S.boundary_subjects(conn):
        record(f"architect:{S.SURFACE_PREFIX}{rel}", S.SURFACE_PREFIX + rel)
    # The Critic challenged every load-bearing claim during onboarding. Only
    # the Critic's onboarding ops read the table, so no delivery seat sees it.
    for subject in S.challenge_subjects(conn):
        conn.execute("INSERT OR IGNORE INTO challenges (id, verdict) "
                     "VALUES (?, 'stands')", (subject,))


# ---------------------------------------------------------------------------
# Unguessable ids
# ---------------------------------------------------------------------------

_HOLE = re.compile(r"<([A-Za-z0-9_]+)>")

# CPython's own angle names. Case text quotes them from tracebacks and
# docstrings, and they name no row. A filled `option.<locals>.decorator()`
# showed the model a traceback that Python never printed (frame 353, wall 2).
NOT_HOLES = frozenset({
    "locals", "module", "lambda", "listcomp", "dictcomp", "setcomp",
    "genexpr", "string", "stdin", "stdout", "stderr",
})


def fill(text: str, case_id: str, run_no: int = 1) -> str:
    """
    Replace every `<name>` with an id the model cannot guess. A name of
    `NOT_HOLES` is Python's own text, and it stays as the case wrote it.

    Cases are written with `i1`, `tk1`, `b1` because they have to be readable
    and diffable. The cost is that they are also *predictable*: in a fixture
    with one item, `problem.set_approval(id='i1')` is right every time without
    reading anything — so a case that ought to fail can pass, and running it
    more times will never say which happened.

    **Declared holes rather than inferred ids.** The first version worked out
    which strings looked like ids and rewrote those, which cannot see a
    convention: `e_m_in` is an entry id that *encodes* a message id, because the
    runtime looks up `f"e_{message_id}"`. Inference renamed the entry and left
    the message alone, `ctx.entry_id` came back None, and Liaison — which had
    passed for weeks — silently stopped being able to segment anything. Written
    as `e_{{m_in}}` the two move together, because the author said they were the
    same thing and nothing had to guess.

    Substitution is textual and happens before the YAML is parsed, so a hole
    works anywhere: a row id, a foreign key, a ref list, a config key, half of a
    derived id.

    Angle brackets rather than `{{...}}`, and the reason is not taste. Fixture
    rows are YAML *flow* mappings — `- {id: X, text: "..."}` — and in flow
    context `{ } [ ] ,` are indicators, so a plain scalar cannot contain them.
    `{{i1}}` makes the file invalid YAML that happens to parse once the holes
    are filled, which costs editor validation, `--raw` loading, and every tool
    that reads a case without going through this function. `<i1>` is an ordinary
    plain scalar and the file stays a YAML file.

    Deterministic per run, and salted across runs (frame 66, 2026-09-23). Run 1
    keeps the unsalted digest, byte for byte, so every cassette and every
    register row recorded before the salt stays evidence about run 1. Every
    other run mixes the run number into the digest, so the five runs of a case
    are five different problems. Without the salt run 1 recorded and runs 2 to
    5 replayed it inside one process, and the threshold counted one reply five
    times.
    """
    import hashlib

    def one(match: re.Match) -> str:
        name = match.group(1)
        if name in NOT_HOLES:
            return match.group(0)
        prefix = name.rstrip("0123456789") or "x"
        seed = f"{case_id}:{name}" if run_no == 1 else f"{case_id}:{name}:{run_no}"
        digest = hashlib.sha1(seed.encode()).hexdigest()[:6]
        return f"{prefix}_{digest}"

    return _HOLE.sub(one, text)


def holes(text: str) -> set[str]:
    return set(_HOLE.findall(text)) - NOT_HOLES


def mode_of(case: dict) -> str:
    """
    Which prompt piece the case exercises.

    Normally derivable — a message case is keyed by its verb, a tick case by the
    tick — and `prompt:` exists for the one shape that is not. Liaison's
    `verdict_signoff` is the principal's `verdict` verb keyed by what it answers,
    so deriving it from the verb alone loads the ratification prompt and grades
    the wrong mode. Writing that out is better than a case that silently tests
    something other than what its id says.
    """
    if case.get("prompt"):
        return case["prompt"]
    return (case.get("inbound") or {}).get("verb") or case.get("tick", "")


def rerecord_command(pins: Pins, test_file: str) -> str:
    """
    The command that re-earns a case, carrying the key it would run under.

    The message said `ROTA_L1=1 python -m pytest <file> -q` and named no
    model, so a reader who followed the repository's own instruction
    re-recorded against whatever was ambient. Two cases flipped from fail to
    pass on the model alone, both scoring 0 of 5 on the wrong one (observed:
    frame 60, the same 20 case ids run twice, 2026-09-21).

    The window is named for the same reason, and `ROTA_PROFILE` is named when
    it is set, because it sets the think pin and a set pin keys the recording.

    The profile this names is the ambient one, read from the environment here.
    A think pin carried in `pins` reaches nothing, so no caller passes one.
    """
    parts = ["ROTA_L1=1", f"ROTA_MODEL={pins.model}",
             f"ROTA_NUM_CTX={pins.num_ctx}"]
    profile = os.environ.get("ROTA_PROFILE")
    if profile:
        parts.append(f"ROTA_PROFILE={profile}")
    return " ".join(parts) + f" python -m pytest {test_file} -q"


def instructions_for(case: dict) -> str:
    """
    The prompt text a result is evidence *about*, for stamping.

    One definition because two consumers must not drift: the tier records a run
    against it, and anything reading the results back recomputes it to ask
    whether a green result is still about the prompt in the tree. That question
    is the whole difference between "stale" and "failing", and getting it wrong
    reports unmeasured cases as broken ones.

    A chain's answer is *both* legs. `run_chain` composes each leg's brief
    itself, and L3 recorded its runs against bare pins with no prompt hash at
    all -- so five chains could go green against briefs that had since been
    rewritten and nothing anywhere could tell. Editing either brief must make
    the chain stale, because either one can be the reason it stopped working.

    Byte-identical to what `test_l1.py` already composes for the single-session
    case, deliberately: a different string here is a different hash, and every
    cassette in the repository is keyed to the old one.
    """
    if case.get("first"):
        legs = [case["first"], case["then"]]
        return "\n\n".join(
            prompts_mod.compose(
                leg["role"],
                leg.get("prompt") or leg.get("verb") or leg.get("tick", ""))
            for leg in legs)
    return prompts_mod.compose(case["role"], mode_of(case))


def seed_inbound(conn: sqlite3.Connection, case: dict) -> str | None:
    """
    The one message a case wakes on, or None for a tick case.

    One definition, because a reader that composes the prompt must seed the
    same row the run seeded. A message this reader did not write is a message
    `resolve_inbound` and `_mode_key` cannot read, and the mode keyed by a
    cause then picks another brief.
    """
    inbound = case.get("inbound") or {}
    if not inbound:
        return None
    msg_id = inbound.get("id", "m_in")
    # `body_text` too, or a case cannot seed the one message that carries
    # words. Law 2 keeps prose off messages because sender and recipient
    # share a database and an id means something at both ends -- except for
    # the Researcher, which has never seen an artefact, so refs are
    # meaningless to it and the schema says outright that a question with no
    # words is no question.
    #
    # The loader dropped the field silently, so
    # `L1-RS-answer-from-the-clause-not-from-memory` woke its Researcher with
    # an empty question and the session said so: "the architect's question
    # was empty and there were no references to load". It then answered from
    # memory, which is the exact failure the case exists to catch, and it had
    # no way to do anything else.
    conn.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
        "body_refs, body_text, cause_id, seq) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 99)",
        (msg_id, inbound.get("thread", "t1"), inbound["from"], inbound["to"],
         inbound["verb"], json.dumps(inbound.get("body_refs", [])),
         inbound.get("body_text"), inbound.get("cause")),
    )
    # A verdict seeded on the inbound message gets its rows now that the
    # message exists (fact F1).
    for row in (case.get("fixture") or {}).get("keypress_verdicts") or []:
        if row.get("id") == msg_id:
            seed_verdict(conn, msg_id, row.get("per_item") or {})
    return msg_id


def live_detail(conn, wake: Wake) -> Wake:
    """
    The wake with the detail its predicate builds in a live run.

    A criteria wake carries the empty and the covered tickets of its item
    (frame 322). A case wake built from the case file carried the tick's
    name, which `build_prompt` drops. So the register never measured the
    line a live seat reads (frame 322, review 1, finding 1).
    """
    if wake.kind != "tick:criteria" or not wake.refs:
        return wake
    from dataclasses import replace

    from ..core.scheduler import criteria_detail

    # The L1 criteria cases name a ticket in `refs`, and the live wake names
    # the item. The detail reads the item either way. The refs stay as the
    # case wrote them, so the rest of the prompt does not move.
    row = conn.execute("SELECT item_id FROM tickets WHERE id = ?",
                       (wake.refs[0],)).fetchone()
    item = row[0] if row else wake.refs[0]
    return replace(wake, detail=criteria_detail(conn, item) or wake.detail)


def wake_for(case: dict, msg_id: str | None) -> Wake:
    """
    The wake a case declares, built once for the run and for the reader.

    A tick case must wake as a tick. `kind` was hardcoded to "message" and the
    declared tick reached `detail` only, which picks the right brief and then
    takes a different path through everything keyed on the kind itself:
    `round_close` resolves the whole round in `resolve_inbound` and got `{}`,
    so Liaison was told to compose what came back while being shown none of
    it -- 0/220, and correctly so, because `t1` was the only id it held.
    `tick:survey` writes with `observed` provenance and was writing `decided`.
    """
    inbound = case.get("inbound") or {}
    tick = case.get("tick")
    return Wake(role=case["role"], kind=f"tick:{tick}" if tick else "message",
                message_id=msg_id,
                refs=tuple(case.get("refs") or ()),
                detail=inbound.get("verb", case.get("detail") or tick or ""))


def leg_wake(spec: dict, message_id: str | None) -> Wake:
    """
    The wake one leg of a chain gets, which is not the wake a case gets.

    A leg names its verb directly, and the second leg wakes on the message the
    first leg sent, so a declared tick yields to a message id. The cockpit's
    prompt preview reads this rule too, or it previews leg one under a wake
    the chain never runs.
    """
    tick = spec.get("tick")
    return Wake(role=spec["role"],
                kind=f"tick:{tick}" if tick and not message_id else "message",
                message_id=message_id,
                refs=tuple(spec.get("refs") or ()),
                detail=spec.get("verb") or spec.get("detail") or tick or "")


def area_for(case: dict, wake: Wake) -> str | None:
    """
    The subject an onboarding tick reads, which the sandbox advertises.

    The area reaches the system text through the tools the sandbox builds, so
    the reader of a prompt applies the same rule the run applied.
    """
    return (wake.refs[0]
            if case.get("tick") in ("survey", "commitments", "orient", "define") else None)


def system_text_for(case: dict) -> str:
    """
    What the model is told for this case, composed without running it.

    The cassette key covers this text, so the register's report matches on its
    digest. The composition needs the sandbox and not the session: with
    `push_working_set` and `resolve_inbound` left out, the text is
    byte-identical to the run's for 121 of 121 single-session cases, and all
    121 cost 1.01 seconds over an in-memory database (observed: frame 63's
    first read, 2026-09-22).

    **Two mode rules meet here, and they are still two.** The brief comes from
    `instructions_for`, which keys on `mode_of(case)`. The allow list comes
    from `_mode_key(wake, conn)` inside `session_sandbox`. The two agree on
    every single-session case today (observed: frame 63's design review,
    2026-09-22).

    No worktree and no model. A case that declares `repo:` composes the same
    text without one, and building one for a report would shell out to git
    once per case.
    """
    from ..core.loop import _batch_of
    from ..core.runner import compose_system, native_default, session_sandbox

    conn = init_db(":memory:")
    try:
        seed(conn, case.get("fixture") or {})
        wake = live_detail(conn, wake_for(case, seed_inbound(conn, case)))
        sb = session_sandbox(conn, wake, mode=case.get("mode"),
                             batch_id=_batch_of(conn, wake),
                             area=area_for(case, wake))
        # The same variable `run_session` reads, because the flag changes the
        # last paragraph of the system text. The native flag changes the
        # call paragraph, and `run_session` resolves it the same way.
        return compose_system(case["role"], sb,
                              instructions=instructions_for(case),
                              oneshot=bool(os.environ.get("ROTA_ONESHOT")),
                              native=native_default(conn))
    finally:
        conn.close()


class _Replied:
    """The seat's own earlier replies first, then the model.

    A case's `replies:` holds what the seat said on its first turns, copied
    from a night. The runner answers each reply as it answered the night's,
    and the model then judges the turn after them. So the case measures one
    judgement on a transcript, and the cassette keys on that turn's prompt
    (frame 152, night 125: the nudge after a test written into a reply).
    """

    def __init__(self, replies: list[str], inner):
        from ..llm.llm import Completion

        self._make = Completion
        self.replies = list(replies)
        self.scripted = len(self.replies)
        self.inner = inner
        self.name = getattr(inner, "name", "")
        # How often the model was asked. A case whose replies end the session
        # judged nothing, and passes on the script alone (frame 152's review
        # of 9684e3c, point 5).
        self.asked = 0

    @property
    def misses(self) -> int:
        return getattr(self.inner, "misses", 0)

    def complete(self, system: str, user: str, pins: Pins, tools=None):
        if self.replies:
            return self._make(text=self.replies.pop(0), pins=pins,
                              backend="replies")
        self.asked += 1
        return self.inner.complete(system, user, pins, tools=tools)


def _replies_of(case: dict) -> list[str]:
    """
    The case's `replies:`, each a string or `{file: <name>}`.

    A file is read as bytes from `tests/rota/fixtures`, so a night's reply
    keeps every byte, and a test can share the copy (frame 165).
    """
    from .. import paths

    out = []
    for reply in case["replies"]:
        if isinstance(reply, dict):
            path = paths.CASES.parent / "fixtures" / reply["file"]
            reply = path.read_bytes().decode("utf-8")
        out.append(reply)
    return out


def _no_call(case: dict, outcome: RunOutcome, scripted: int) -> list[str]:
    """The case's `no_call:` against the model's first reply after the
    scripted ones. The reply holds no `TOOL:` line and no call that the
    parser reads (frame 165: a reply that takes the step to end)."""
    if not (case.get("expect") or {}).get("no_call"):
        return []
    from ..llm import toolproto

    if len(outcome.completions) <= scripted:
        return ["expected a reply with no call; the model made none"]
    text = outcome.completions[scripted]
    if re.search(r"^\s*TOOL:", text, re.M):
        return ["expected a reply with no call; the reply holds a TOOL: line"]
    if _reply_calls(outcome, scripted, toolproto):
        return ["expected a reply with no call; the reply holds a call"]
    return []


def _reply_calls(outcome: RunOutcome, n: int, toolproto) -> list:
    """
    The calls of reply `n`: its native calls when it made any, else the
    calls the parser reads in its text.

    The offered set comes from the `TOOL:` lines of the system text, as it
    always has. A native prompt has no such line, so the set then comes
    from the functions the session offered (frame 323).
    """
    native = getattr(outcome, "native", None) or []
    if n < len(native) and native[n]:
        return list(native[n])
    allowed = set(re.findall(r"^\s*TOOL: ([a-z_]+\.[a-z_]+)\(",
                             outcome.system, re.M))
    allowed = allowed or set(getattr(outcome, "offered", None) or [])
    return toolproto.extract_lenient(outcome.completions[n], allowed)


def _first_call(case: dict, outcome: RunOutcome, scripted: int) -> list[str]:
    """The case's `first_call:` against the model's first reply after the
    scripted ones. Its keys are the function and the arguments it must
    name, so a case can judge the first act alone."""
    want = (case.get("expect") or {}).get("first_call")
    if not want:
        return []
    from ..llm import toolproto

    if len(outcome.completions) <= scripted:
        return [f"expected a first call to {want['fn']}; the model made none"]
    calls = _reply_calls(outcome, scripted, toolproto)
    if not calls:
        return [f"expected a first call to {want['fn']}; the reply holds no call"]
    first = calls[0]
    # A refused call has no name. The grader names the refusal, because an
    # `AttributeError` here ended the case with no verdict (frame 323).
    if isinstance(first, toolproto.ToolError):
        return [f"expected a first call to {want['fn']}; the first call "
                f"was refused: {first.raw[:120]} ({first.reason})"]
    if first.name != want["fn"]:
        return [f"expected a first call to {want['fn']}; got {first.name}"]
    wrong = {k: first.args.get(k) for k, v in (want.get("args") or {}).items()
             if first.args.get(k) != v}
    return [f"the first {want['fn']} names {wrong}, not "
            f"{ {k: want['args'][k] for k in wrong} }"] if wrong else []


def _normal_code(text: str) -> str:
    """One statement or expression as `ast.unparse` writes it, so the quote
    style and the spacing do not decide a match. Text that does not parse
    stays as it is."""
    import ast

    try:
        return ast.unparse(ast.parse(text.strip()))
    except SyntaxError:
        return text.strip()


def _body_code(source: str, name: str) -> str | None:
    """The statements of definition `name` in `source`, or of the module
    when `name` is empty, as `ast.unparse` writes them. A docstring and a
    comment are not statements, so neither is in the text. None when the
    source does not parse or holds no such definition."""
    import ast

    try:
        node: ast.AST = ast.parse(source)
    except SyntaxError:
        return None
    for part in [p for p in name.split(".") if p]:
        node = next((n for n in ast.walk(node)
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                                       ast.ClassDef)) and n.name == part), None)
        if node is None:
            return None
    body = list(node.body)
    if (body and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)):
        body = body[1:]
    return "\n".join(ast.unparse(s) for s in body)


def _witnesses_stated(case: dict, conn: sqlite3.Connection, wake,
                      refused: dict[str, int]) -> list[str]:
    """The key `witnesses: {stated: all, refused: 0}` of a commitments case.

    A run that stated 1 of 5 pushed lines passed the row count, and the store
    case passed 5 of 5 with 3 refused calls in each run (the review of pass
    4b, low 2). So the key counts each pushed line that no row states, and
    each refused `model.amend`."""
    spec = (case.get("expect") or {}).get("witnesses")
    if not isinstance(spec, dict):
        return []
    from ..roles.api import witness_push

    problems = []
    area = wake.refs[0] if wake.refs else ""
    if spec.get("stated") == "all":
        pushed = witness_push(conn, area)[0]
        missing = [w["id"] for w in pushed if not w["stated"]]
        if missing or not pushed:
            problems.append(f"stated {len(pushed) - len(missing)} of the "
                            f"{len(pushed)} pushed witness lines; no row states "
                            f"{missing}")
    cap = spec.get("refused")
    got = refused.get("model.amend", 0)
    if cap is not None and got > int(cap):
        problems.append(f"{got} model.amend calls were refused, and the key "
                        f"allows {cap}")
    return problems


def _write_includes(case: dict, conn: sqlite3.Connection,
                    batch_id: str | None) -> list[str]:
    """
    The case's `write_includes:` against the file at the batch head.

    Each keyed line must be code in the body of a grain that a `mistake` row
    of the batch names, in the commit the worktree's HEAD holds after the
    run. A line in a docstring or a comment is no code. A write the door
    refuses, an uncommitted write and a write to another path leave the
    head without the line, so each fails. The text of a call proved
    nothing: night 172's s264 and s267 sent `surrogateescape` in the
    docstring and the head's body (F7 review p3, findings 1 and 2).
    """
    lines = (case.get("expect") or {}).get("write_includes")
    if not lines:
        return []
    import subprocess

    from ..core.worktrees import grain_path

    row = conn.execute("SELECT worktree FROM batches WHERE id = ?",
                       (batch_id,)).fetchone() if batch_id else None
    if not row or not row["worktree"]:
        return ["write_includes: the batch has no worktree"]
    grains = [r[0] for r in conn.execute(
        "SELECT DISTINCT path FROM touch_strays WHERE batch_id = ? "
        "AND status = 'mistake' ORDER BY path", (batch_id,))]
    if not grains:
        return ["write_includes: the batch has no mistake row"]
    want = [_normal_code(line) for line in lines]
    seen: list[str] = []
    for grain in grains:
        # F11: the path half goes through the one reader.
        path = grain_path(grain)
        _, _, name = grain.partition("::")
        shown = subprocess.run(["git", "-C", row["worktree"], "show",
                                f"HEAD:{path}"], capture_output=True)
        body = (_body_code(shown.stdout.decode("utf-8", "replace"), name)
                if shown.returncode == 0 else None)
        if body is None:
            seen.append(f"{grain}: not in the head commit")
            continue
        missing = [w for w in want if w not in body]
        if not missing:
            return []
        seen.append(f"{grain}: lacks {missing}")
    return [f"expected the head commit to hold {lines} as code; "
            + "; ".join(seen)]


def run_case(case: dict, db_path: str | Path, backend, *, pins: Pins | None = None,
             instructions: str = "", run_no: int = 1) -> CaseResult:
    conn = init_db(db_path)
    seed(conn, case.get("fixture") or {})
    repo = (_with_repo(conn, case, Path(db_path), run_no)
            if case.get("repo") else None)

    msg_id = seed_inbound(conn, case)

    before = snapshot_versions(conn)
    seeded = {r["id"] for r in conn.execute("SELECT id FROM messages")}
    wake = live_detail(conn, wake_for(case, msg_id))

    # The same resolution the loop does, for the same reason: a role that works
    # in a worktree needs to be told which one, and it is never the role's to
    # choose. Without this a Developer case ran with no batch and could not
    # write a line of the code it was woken for.
    from ..core.loop import _batch_of

    if case.get("replies"):
        backend = _Replied(_replies_of(case), backend)
    with _page_as_seen(case):
        outcome = _run_session(conn, wake, backend, pins, instructions, case)
    return _case_result(case, conn, db_path, backend, outcome, wake, before,
                        seeded, repo, run_no)


def _page_as_seen(case: dict):
    """
    The page of a case with `page.lines`, as the principal saw it.

    A real page from a night cannot come back from its rows: a row can move
    after his reply, and the records keep the lines and not the section
    heads. The case then tests the reading, not the renderer (frame 345).
    The seat's wake and the door read the same text. The order stays the
    record's, through `seen_order`.
    """
    import contextlib
    from unittest import mock

    lines = (case.get("page") or {}).get("lines")
    if not lines:
        return contextlib.nullcontext()
    from ..roles import principal

    real = principal.render_page
    ask_id = (case.get("inbound") or {}).get("cause")
    text = "\n".join([case["page"].get("header") or ""]
                     + [f"  {n}. {line}" for n, line in enumerate(lines, 1)])

    reply_id = (case.get("inbound") or {}).get("id")

    def seen(conn, verb, refs, question=None, **kw):
        page, order = real(conn, verb, refs, question, **kw)
        if kw.get("ask_id") != ask_id:
            return page, order
        # The seeded order, because a fresh render orders the rows its own
        # way, and 12 of 24 cases differ (the review of 5b525a72, low 3).
        # Through `seen_order`, the one reader of the record (fact F28).
        # With no ask it reads the record only.
        return text, principal.seen_order(conn, reply_id, None) or order

    return mock.patch.object(principal, "render_page", seen)


def _run_session(conn, wake, backend, pins, instructions, case):
    from ..core.loop import _batch_of

    return run_session(conn, wake, backend=backend, pins=pins,
                          instructions=instructions,
                          batch_id=_batch_of(conn, wake),
                          area=area_for(case, wake),
                          # None, not "normal": a case that does not declare a
                          # mode gets the one the wake derives, which is what
                          # production would give it.
                          mode=case.get("mode"))


def _case_result(case, conn, db_path, backend, outcome, wake, before, seeded,
                 repo, run_no) -> CaseResult:
    from ..core.loop import _batch_of

    delta = capture(conn, outcome.session_id, before, messages_before=seeded)

    # `runner` records a thrown-out call as f"{call.name}: {exc}", so the
    # function name is always the prefix. Counted, because the same function can
    # be refused once and land later with corrected arguments.
    refused: dict[str, int] = {}
    for err in outcome.errors:
        fn = err.split(":", 1)[0].strip()
        if "." in fn:
            refused[fn] = refused.get(fn, 0) + 1

    notes: list[str] = []
    problems = check(case, delta, refused=refused, notes=notes)
    if case.get("same_session"):
        problems += check_same_session(conn, case["same_session"], outcome.session_id)
    if not outcome.committed and case.get("expect_commit", True):
        problems.append(f"session did not commit: {outcome.errors}")
    scripted = backend.scripted if isinstance(backend, _Replied) else 0
    if isinstance(backend, _Replied) and not backend.asked:
        problems.append("the model made no completion after the scripted "
                        "replies, so the case judged nothing")
    problems += _first_call(case, outcome, scripted)
    problems += _no_call(case, outcome, scripted)
    problems += _write_includes(case, conn, _batch_of(conn, wake))
    problems += _witnesses_stated(case, conn, wake, refused)

    if repo is not None:
        from . import gitfixture
        gitfixture.cleanup(repo)

    return CaseResult(case_id=case.get("id", "?"), run=run_no,
                      passed=not problems, problems=problems,
                      delta=delta, outcome=outcome, notes=notes,
                      systems=[outcome.system], scripted=scripted,
                      # A backend without the counter made no live call: a
                      # replay-only backend never reaches a model.
                      live_calls=getattr(backend, "misses", 0))


def run_chain(case: dict, db_path: str | Path, backend_factory, *,
              pins: Pins | None = None, run_no: int = 1) -> CaseResult:
    """
    Two sessions, joined by the message the first one actually sent.

    This is the whole point of the tier and the reason it cannot be faked with
    two independent cases. Every other test hands a role a message somebody
    wrote by hand, which measures whether the role can act on a *well-formed*
    message. L3 asks the question the design rests on: **does the message
    vocabulary carry enough for a stranger to act on it?**

    So the second session is woken by the first session's own outbound row —
    same refs, same verb, nothing rewritten in between. If the first role never
    messaged the second, the chain stops there and says so, because that is the
    finding: the handoff the graph draws does not happen.

    The roles share only the database. No context, no history, no prose channel
    — which is the arrangement being tested, not an implementation detail.
    """
    from ..core.loop import _batch_of

    # A chain does not serve scripted replies. A key it ignored would make
    # the chain's first leg judge a turn the case did not mean.
    if any("replies" in spec for spec in (case, case.get("first") or {},
                                          case.get("then") or {})):
        raise ValueError(f"{case.get('id', '?')}: `replies:` is for a case of "
                         f"one session; run_chain does not serve it")
    conn = init_db(db_path)
    seed(conn, case.get("fixture") or {})
    repo = (_with_repo(conn, case, Path(db_path), run_no)
            if case.get("repo") else None)

    first, then = case["first"], case["then"]
    problems: list[str] = []
    # Every backend a leg used, because the factory makes one per leg and the
    # chain's live count is the sum over its legs (frame 66, 2026-09-23).
    backends: list = []

    def _live() -> int:
        return sum(getattr(b, "misses", 0) for b in backends)

    def _one(spec: dict, message_id: str | None) -> tuple[RunOutcome, Delta]:
        mode = spec.get("prompt") or spec.get("verb") or spec.get("tick", "")
        # Same as the L1 path: a leg declaring a tick has to wake as one, or the
        # handoff under test starts from a wake shape production never produces.
        wake = live_detail(conn, leg_wake(spec, message_id))
        seen = {r["id"] for r in conn.execute("SELECT id FROM messages")}
        versions = snapshot_versions(conn)
        backends.append(backend_factory())
        out = run_session(
            conn, wake, backend=backends[-1], pins=pins,
            instructions=prompts_mod.compose(spec["role"], mode),
            batch_id=_batch_of(conn, wake),
            area=wake.refs[0] if spec.get("tick") in ("survey", "commitments", "orient", "define") else None)
        return out, capture(conn, out.session_id, versions, messages_before=seen)

    # A first leg may name a message the fixture seeded, and one kind of chain
    # cannot start without it. Liaison's `converse` reads the principal's words
    # through the *message*: the entry is found as `e_{message_id}` and expanded
    # into `principal_said`. Woken with no message, the mode that turns a
    # sentence into work or a question is handed no sentence, and the chain that
    # begins at intake -- which is every chain the principal starts -- could not
    # be written here at all.
    a_out, a_delta = _one(first, first.get("inbound"))
    if not a_out.committed:
        problems.append(f"{first['role']} did not commit: {a_out.errors}")

    # Two kinds of handoff, and only one of them was ever runnable here.
    #
    # `l3a` has said so since it was written: "most of this system does not
    # coordinate by message. Vision Keeper never messages Terminologist -- it
    # writes a ticket and the `criteria` predicate wakes them. There is a chain
    # case for exactly that, and it scored as covering nothing." The denominator
    # was built; the harness was not, so that case demanded a message the design
    # does not send and had never passed in 235 recorded runs.
    #
    # A `tick` on the second leg is the declaration: the handoff is the artefact
    # and the frontier, not a message. Leg one writes; the predicates are
    # re-derived from the committed state exactly as the loop derives them; the
    # wake either appears or it does not. When it does not, *that* is the
    # finding, and it is a sharper one than a missing message -- it means a role
    # did its job and left the next one asleep.
    wants_tick = then.get("tick")
    handoff = next((m for m in a_delta.messages if m["to_role"] == then["role"]), None)

    if wants_tick and handoff is None:
        from ..core.scheduler import predicate_wakes

        woken = [w for w in predicate_wakes(conn)
                 if w.role == then["role"] and w.kind == f"tick:{wants_tick}"]
        # A conditional leg: some ticks are stall-catchers, and the happy path
        # never produces them. `awaiting_confirm` fires only when ratification
        # stalled -- a leg one that already confirmed leaves it correctly
        # silent, and demanding the wake anyway failed five runs of a chain
        # whose first leg had done everything right. `if_needed` says: if the
        # gate has nothing to catch, the chain is leg one alone, judged whole.
        if not woken and then.get("if_needed"):
            problems += check(case, a_delta, refused={}, notes=[])
            if repo is not None:
                from . import gitfixture as _gf
                _gf.cleanup(repo)
            # Closed before every return, because the caller deletes the
            # directory this database sits in. Windows refuses to delete an
            # open file, and `casestatus` leaked a directory per chain on
            # every report and every gate (observed: frame 63's diff review,
            # 2026-09-22). The result below holds no row of it.
            conn.close()
            return CaseResult(case_id=case.get("id", "?"), run=run_no,
                              passed=not problems, problems=problems,
                              delta=a_delta, outcome=a_out,
                              # Leg one is the whole chain here, so it is the
                              # whole of what the model was told.
                              systems=[a_out.system], live_calls=_live())
        if not woken:
            others = sorted({w.kind for w in predicate_wakes(conn)})
            problems.append(
                f"{first['role']} committed, but nothing woke {then['role']} "
                f"for {wants_tick}; the frontier offers {others or 'nothing'}")
            if repo is not None:
                from . import gitfixture as _gf
                _gf.cleanup(repo)
            conn.close()
            return CaseResult(case_id=case.get("id", "?"), run=run_no,
                              passed=False, problems=problems,
                              delta=a_delta, outcome=a_out,
                              systems=[a_out.system], live_calls=_live())
        b_spec = dict(then)
        b_spec["refs"] = list(woken[0].refs)
        b_out, b_delta = _one(b_spec, None)
    elif handoff is None:
        problems.append(
            f"{first['role']} never messaged {then['role']}; sent "
            f"{[(m['to_role'], m['verb']) for m in a_delta.messages] or 'nothing'}")
        if repo is not None:
            from . import gitfixture as _gf
            _gf.cleanup(repo)
        conn.close()
        return CaseResult(case_id=case.get("id", "?"), run=run_no, passed=False,
                          problems=problems, delta=a_delta, outcome=a_out,
                          systems=[a_out.system], live_calls=_live())
    else:
        b_spec = dict(then)
        b_spec.setdefault("verb", handoff["verb"])
        b_out, b_delta = _one(b_spec, handoff["id"])
    if not b_out.committed:
        problems.append(f"{then['role']} did not commit: {b_out.errors}")

    # Scored against the second leg, so the refusals that matter are its own.
    b_refused: dict[str, int] = {}
    for err in b_out.errors:
        fn = err.split(":", 1)[0].strip()
        if "." in fn:
            b_refused[fn] = b_refused.get(fn, 0) + 1
    notes: list[str] = []
    scored = b_delta
    if then.get("if_needed"):
        # The conditional gate ran, so the pipeline's work is split across the
        # legs -- the statement in one, the confirm in the other -- and judging
        # leg two alone would fail a chain that succeeded. Judged merged.
        scored = Delta(
            session_id=b_delta.session_id, committed=b_delta.committed,
            writes={t: a_delta.writes.get(t, []) + b_delta.writes.get(t, [])
                    for t in {*a_delta.writes, *b_delta.writes}},
            messages=a_delta.messages + b_delta.messages,
            tool_calls=a_delta.tool_calls + b_delta.tool_calls,
            versions_moved={**a_delta.versions_moved, **b_delta.versions_moved})
    problems += check(case, scored, refused=b_refused, notes=notes)
    if repo is not None:
        from . import gitfixture
        gitfixture.cleanup(repo)

    conn.close()
    return CaseResult(case_id=case.get("id", "?"), run=run_no,
                      passed=not problems, problems=problems,
                      delta=b_delta, outcome=b_out, notes=notes,
                      systems=[a_out.system, b_out.system], live_calls=_live())


def run_sampled(case: dict, tmpdir: Path, backend_factory, *, pins: Pins | None = None,
                instructions: str = "") -> tuple[int, int, list[CaseResult]]:
    """
    Run a case `runs` times and compare against its `pass` threshold.

    LLM output is stochastic; the harness treats that as a measured quantity
    rather than an excuse. A case that passed 5/5 for weeks and now passes 3/5 is
    a prompt regression signal, which is why the count is returned rather than a
    bare boolean.

    Each run gets its own problem, through `for_run` (frame 66, 2026-09-23).
    The ids are salted with the run number, so run 2 composes a prompt run 1
    never sent and the model answers it again. Run 1 keeps today's ids.
    """
    # ROTA_RUNS overrides the case for a smoke run of a new column; the
    # threshold is the case's, so a smoke reads its rows, not its verdict.
    runs = int(os.environ.get("ROTA_RUNS") or case.get("runs", 1))
    threshold = int(case.get("pass", runs))
    results = []
    for i in range(1, runs + 1):
        path = tmpdir / f"{case.get('id','case')}_{i}.db"
        problem = for_run(case, i)
        if problem.get("first"):
            results.append(run_chain(problem, path, backend_factory,
                                     pins=pins, run_no=i))
        else:
            results.append(run_case(problem, path, backend_factory(), pins=pins,
                                    instructions=instructions, run_no=i))
    passed = sum(1 for r in results if r.passed)
    return passed, threshold, results
