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

from ..core.db import ARTEFACT_TABLES, init_db
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
        if table == "item_statements":
            # A relation that folded into `refs`: `_seed_refs` translates it.
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
    `verdict` verb, or a `verdict:<message>` config key whose message is
    seeded. `principal.land` writes the row for a live verdict, and an
    adopt needs it on the cause chain. The ask is the verdict's cause and
    `rulings.ask_id` is a foreign key, so a verdict with no seeded cause
    gets no row. No prompt, wake or predicate reads the row."""
    per_item: dict[str, str] = {}
    for row in fixture.get("messages") or []:
        if row.get("verb") == "verdict" and row.get("id"):
            per_item.setdefault(row["id"], "{}")
    for row in fixture.get("config") or []:
        key = str(row.get("key") or "")
        if key.startswith("verdict:"):
            value = row.get("value")
            per_item[key[len("verdict:"):]] = (
                value if isinstance(value, str) else json.dumps(value or {}))
    for mid, ruled in per_item.items():
        cause = conn.execute("SELECT cause_id FROM messages WHERE id = ?",
                             (mid,)).fetchone()
        if not cause or not cause["cause_id"]:
            continue
        conn.execute(
            "INSERT OR IGNORE INTO rulings (id, ask_id, per_item, words, "
            "status, verdict_id) VALUES (?, ?, ?, 'seeded verdict', 'landed', ?)",
            (f"r_{mid}", cause["cause_id"], ruled, mid))


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
            out.append(parse(fill(chr(10).join(buffer), current))[0])
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


def capture(conn: sqlite3.Connection, session_id: str,
            versions_before: dict[str, int],
            messages_before: set[str] | None = None) -> Delta:
    writes: dict[str, list[str]] = {}
    for r in conn.execute(
        "SELECT table_name, row_id FROM receipts WHERE session_id = ? ORDER BY table_name",
        (session_id,),
    ):
        writes.setdefault(r["table_name"], []).append(r["row_id"])

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
        "SELECT id, to_role, verb, body_refs, cause_id FROM messages "
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
        ]
        if not _count_ok(len(matches), spec.get("count")):
            problems.append(f"expected message {spec}, got {len(matches)} match(es)")
        for m in matches:
            need = set(spec.get("refs_include") or [])
            if need and not need <= set(json.loads(m["body_refs"])):
                problems.append(f"message {m['id']} missing refs {need}")

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

    def transcript(self) -> list[dict]:
        """What the model said and what came back, turn by turn.

        A pass rate says a case is failing. Only this says whether the case was
        unfair, the role under-briefed, or the model out of its depth — which is
        all of the remaining work, so it is kept with the verdict rather than
        printed once and lost."""
        out = [{"say": t} for t in (self.outcome.completions if self.outcome else [])]
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
            repo.commit_in(repo.root, "the tree moved past the survey")
            indexer.build(conn, repo.root)
            boot.repin(conn, repo.root)

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
    return repo


# ---------------------------------------------------------------------------
# Unguessable ids
# ---------------------------------------------------------------------------

_HOLE = re.compile(r"<([A-Za-z0-9_]+)>")


def fill(text: str, case_id: str) -> str:
    """
    Replace every `<name>` with an id the model cannot guess.

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

    Deterministic on purpose — the same case yields the same ids every run, so
    the prompt is byte-identical and a cassette recorded against it stays valid.
    """
    import hashlib

    def one(match: re.Match) -> str:
        name = match.group(1)
        prefix = name.rstrip("0123456789") or "x"
        digest = hashlib.sha1(f"{case_id}:{name}".encode()).hexdigest()[:6]
        return f"{prefix}_{digest}"

    return _HOLE.sub(one, text)


def holes(text: str) -> set[str]:
    return set(_HOLE.findall(text))


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


def run_case(case: dict, db_path: str | Path, backend, *, pins: Pins | None = None,
             instructions: str = "", run_no: int = 1) -> CaseResult:
    conn = init_db(db_path)
    seed(conn, case.get("fixture") or {})
    repo = (_with_repo(conn, case, Path(db_path), run_no)
            if case.get("repo") else None)

    inbound = case.get("inbound") or {}
    msg_id = inbound.get("id", "m_in")
    if inbound:
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

    before = snapshot_versions(conn)
    seeded = {r["id"] for r in conn.execute("SELECT id FROM messages")}
    # A tick case must wake as a tick. `kind` was hardcoded to "message" and the
    # declared tick reached `detail` only, which picks the right brief and then
    # takes a different path through everything keyed on the kind itself:
    # `round_close` resolves the whole round in `resolve_inbound` and got `{}`,
    # so Liaison was told to compose what came back while being shown none of
    # it -- 0/220, and correctly so, because `t1` was the only id it held.
    # `tick:survey` writes with `observed` provenance and was writing `decided`.
    tick = case.get("tick")
    wake = Wake(role=case["role"], kind=f"tick:{tick}" if tick else "message",
                message_id=msg_id if inbound else None,
                refs=tuple(case.get("refs") or ()),
                detail=inbound.get("verb", case.get("detail") or tick or ""))

    # The same resolution the loop does, for the same reason: a role that works
    # in a worktree needs to be told which one, and it is never the role's to
    # choose. Without this a Developer case ran with no batch and could not
    # write a line of the code it was woken for.
    from ..core.loop import _batch_of

    outcome = run_session(conn, wake, backend=backend, pins=pins,
                          instructions=instructions,
                          batch_id=_batch_of(conn, wake),
                          area=wake.refs[0] if case.get("tick") in ("survey", "orient", "define") else None,
                          # None, not "normal": a case that does not declare a
                          # mode gets the one the wake derives, which is what
                          # production would give it.
                          mode=case.get("mode"))
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

    if repo is not None:
        from . import gitfixture
        gitfixture.cleanup(repo)

    return CaseResult(case_id=case.get("id", "?"), run=run_no,
                      passed=not problems, problems=problems,
                      delta=delta, outcome=outcome, notes=notes)


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

    conn = init_db(db_path)
    seed(conn, case.get("fixture") or {})
    repo = (_with_repo(conn, case, Path(db_path), run_no)
            if case.get("repo") else None)

    first, then = case["first"], case["then"]
    problems: list[str] = []

    def _one(spec: dict, message_id: str | None) -> tuple[RunOutcome, Delta]:
        mode = spec.get("prompt") or spec.get("verb") or spec.get("tick", "")
        # Same as the L1 path: a leg declaring a tick has to wake as one, or the
        # handoff under test starts from a wake shape production never produces.
        tick = spec.get("tick")
        wake = Wake(role=spec["role"],
                    kind=f"tick:{tick}" if tick and not message_id else "message",
                    message_id=message_id,
                    refs=tuple(spec.get("refs") or ()),
                    detail=spec.get("verb") or spec.get("detail") or tick or "")
        seen = {r["id"] for r in conn.execute("SELECT id FROM messages")}
        versions = snapshot_versions(conn)
        out = run_session(
            conn, wake, backend=backend_factory(), pins=pins,
            instructions=prompts_mod.compose(spec["role"], mode),
            batch_id=_batch_of(conn, wake),
            area=wake.refs[0] if spec.get("tick") in ("survey", "orient", "define") else None)
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
            return CaseResult(case_id=case.get("id", "?"), run=run_no,
                              passed=not problems, problems=problems,
                              delta=a_delta, outcome=a_out)
        if not woken:
            others = sorted({w.kind for w in predicate_wakes(conn)})
            problems.append(
                f"{first['role']} committed, but nothing woke {then['role']} "
                f"for {wants_tick}; the frontier offers {others or 'nothing'}")
            if repo is not None:
                from . import gitfixture as _gf
                _gf.cleanup(repo)
            return CaseResult(case_id=case.get("id", "?"), run=run_no,
                              passed=False, problems=problems,
                              delta=a_delta, outcome=a_out)
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
        return CaseResult(case_id=case.get("id", "?"), run=run_no, passed=False,
                          problems=problems, delta=a_delta, outcome=a_out)
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

    return CaseResult(case_id=case.get("id", "?"), run=run_no,
                      passed=not problems, problems=problems,
                      delta=b_delta, outcome=b_out, notes=notes)


def run_sampled(case: dict, tmpdir: Path, backend_factory, *, pins: Pins | None = None,
                instructions: str = "") -> tuple[int, int, list[CaseResult]]:
    """
    Run a case `runs` times and compare against its `pass` threshold.

    LLM output is stochastic; the harness treats that as a measured quantity
    rather than an excuse. A case that passed 5/5 for weeks and now passes 3/5 is
    a prompt regression signal, which is why the count is returned rather than a
    bare boolean.
    """
    # ROTA_RUNS overrides the case for a smoke run of a new column; the
    # threshold is the case's, so a smoke reads its rows, not its verdict.
    runs = int(os.environ.get("ROTA_RUNS") or case.get("runs", 1))
    threshold = int(case.get("pass", runs))
    results = []
    for i in range(1, runs + 1):
        path = tmpdir / f"{case.get('id','case')}_{i}.db"
        if case.get("first"):
            results.append(run_chain(case, path, backend_factory,
                                     pins=pins, run_no=i))
        else:
            results.append(run_case(case, path, backend_factory(), pins=pins,
                                    instructions=instructions, run_no=i))
    passed = sum(1 for r in results if r.passed)
    return passed, threshold, results
