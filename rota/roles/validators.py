"""
Checkable judgement: LLM proposes, code verifies.

Where a role's output is a *choice inside a legal space*, the legality is
mechanically decidable even though the choice is not. That is the pattern this
module implements, and it is what keeps the suite from degenerating into judging
prose:

  * Liaison's segmentation must cover the entry — spans exist, do not
    overlap, and quote rather than paraphrase.
  * Architect's bindings must name grains that exist in the code index.
  * An ordering must be a valid topological sort of declared deps.

None of these say the choice was *good*. They say it was legal, which is the part
code can own. A judge-LLM is the last resort, never the only test of a law.
"""
from __future__ import annotations

import json
import re
import sqlite3


def _norm(text: str) -> str:
    """Whitespace-insensitive comparison — the one liberty segmentation may take."""
    return re.sub(r"\s+", " ", text).strip().lower()


def check_segmentation(conn: sqlite3.Connection, entry_id: str) -> list[str]:
    """
    Statements cut from an entry must quote it, not summarise it.

    Three properties, all decidable:
      1. every statement's text appears in the entry (modulo whitespace);
      2. spans are within bounds and do not overlap;
      3. the union of spans is reported, so uncovered substance is visible for
         review rather than silently dropped.
    """
    row = conn.execute(
        "SELECT text FROM entries WHERE id = ?", (entry_id,)).fetchone()
    if not row:
        return [f"no entry {entry_id}"]
    entry = row["text"]
    haystack = _norm(entry)

    problems: list[str] = []
    spans: list[tuple[int, int, str]] = []

    for s in conn.execute(
        "SELECT id, text, span_start, span_end FROM statements "
        "WHERE span_entry = ? ORDER BY span_start", (entry_id,)
    ):
        if _norm(s["text"]) not in haystack:
            problems.append(
                f"{s['id']} paraphrases: {s['text']!r} is not in the entry")
        start, end = s["span_start"], s["span_end"]
        if start < 0 or end > len(entry) or start >= end:
            problems.append(
                f"{s['id']} span [{start},{end}] out of bounds for "
                f"{len(entry)}-char entry")
        else:
            spans.append((start, end, s["id"]))

    spans.sort()
    for (a_start, a_end, a_id), (b_start, b_end, b_id) in zip(spans, spans[1:]):
        if b_start < a_end:
            problems.append(f"spans overlap: {a_id} [{a_start},{a_end}] and "
                            f"{b_id} [{b_start},{b_end}]")

    return problems


def uncovered_spans(conn: sqlite3.Connection, entry_id: str) -> list[tuple[int, int]]:
    """Regions of the entry no statement claims. Not an error — a review flag."""
    row = conn.execute(
        "SELECT text FROM entries WHERE id = ?", (entry_id,)).fetchone()
    if not row:
        return []
    length = len(row["text"])
    spans = sorted(
        (r["span_start"], r["span_end"]) for r in conn.execute(
            "SELECT span_start, span_end FROM statements WHERE span_entry = ?",
            (entry_id,))
    )
    gaps, cursor = [], 0
    for start, end in spans:
        if start > cursor:
            gaps.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < length:
        gaps.append((cursor, length))
    return [(a, b) for a, b in gaps if row["text"][a:b].strip()]


def check_statement_count(conn: sqlite3.Connection, entry_id: str,
                          expected: int) -> list[str]:
    """
    Principal granularity is a *count* assertion, which is why it is checkable.

    "we need SSO, but only if it works with our LDAP" is one statement, not two:
    the condition is part of the ask. Over-segmentation is the failure mode worth
    catching, because it looks like diligence.
    """
    n = conn.execute(
        "SELECT COUNT(*) c FROM statements WHERE span_entry = ?",
        (entry_id,)).fetchone()["c"]
    if n != expected:
        return [f"expected {expected} statement(s) at principal granularity, got {n}"]
    return []


def check_bindings_resolve(conn: sqlite3.Connection) -> list[str]:
    """
    Every binding must name a place the index knows: a grain, or an area.

    Grains only, until this was pointed at a real onboarded repository and
    rejected constraint zero -- the one constraint the system creates itself.
    Zero binds *areas* (`.`, `src/auth`, `src/billing`) because it is the
    statement "nobody has looked here yet", and looking is per area; it shrinks
    an area at a time as surveys land. Every one of its bindings failed a check
    whose docstring says every binding must pass.

    It had never run against data. That is the whole reason a validator needs a
    home: an assertion nothing evaluates is a sentence, and this one was wrong.
    """
    known = {r["grain"] for r in conn.execute("SELECT grain FROM code_index")}
    known |= {r["area"] for r in conn.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL")}

    problems = []
    for r in conn.execute(
        "SELECT constraint_id AS cid, grain FROM constraint_bindings "
        "WHERE resolves = 1"
    ):
        if r["grain"] not in known:
            problems.append(
                f"{r['cid']} binds {r['grain']!r}, which is neither a grain nor "
                f"an area in the index")
    return problems


def check_survey_citations(conn: sqlite3.Connection) -> list[str]:
    """
    A survey record's citations must resolve.

    This is what makes "surveyed, none found" evidence rather than a claim — a
    surveyor that never read the area cannot produce grains that exist in it.
    """
    problems = []
    for r in conn.execute(
        "SELECT s.id AS sid, s.area AS area, COUNT(c.grain) AS n "
        "FROM survey_records s LEFT JOIN survey_citations c ON c.survey_id = s.id "
        "GROUP BY s.id"
    ):
        if r["n"] == 0:
            problems.append(f"survey {r['sid']} ({r['area']}) cites nothing")
    for r in conn.execute(
        "SELECT survey_id, grain FROM survey_citations WHERE resolves = 0"
    ):
        problems.append(
            f"survey {r['survey_id']} cites {r['grain']!r}, not in the index")
    return problems


def check_survey_areas(conn: sqlite3.Connection) -> list[str]:
    """
    A survey record must be about an area the partition still has.

    Neither neighbour covered this: `check_bindings_resolve` checks bindings and
    `check_survey_citations` checks citations, and a record whose *area* has
    ceased to exist passes both. Re-indexing is what strands one —
    `areas.pin`'s docstring names the hazard, "a partition that changes
    underneath a half-finished survey would strand the areas already done" —
    and the seat can trigger it on demand.

    Constraint zero rebinds correctly either way, because it is derived from
    what is unsurveyed rather than accumulated. That is the design holding up.
    The stranded record is the part nothing noticed: it counts as a survey of
    something that is not there.
    """
    return [f"survey {r['id']} is about area {r['area']!r}, which the index "
            f"no longer has"
            for r in conn.execute(
                "SELECT id, area FROM survey_records WHERE area NOT LIKE '@%' "
                "AND area NOT IN "
                "(SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL)")]


def check_criteria_terms(conn: sqlite3.Connection) -> list[str]:
    """Criteria are written in glossary terms; term refs must exist and be used."""
    known = {r["id"] for r in conn.execute("SELECT id FROM glossary_terms")}
    refs_of: dict[str, list[str]] = {}
    for r in conn.execute("SELECT src_id, target FROM refs "
                          "WHERE src_table = 'criteria' AND kind = 'term' "
                          "ORDER BY rowid"):
        refs_of.setdefault(r["src_id"], []).append(r["target"])
    problems = []
    for r in conn.execute("SELECT id FROM criteria"):
        refs = refs_of.get(r["id"], [])
        if not refs:
            problems.append(f"criterion {r['id']} has no term_refs")
            continue
        for ref in refs:
            if ref not in known:
                problems.append(f"criterion {r['id']} refs undefined term {ref!r}")
    return problems


def check_no_time_content(conn: sqlite3.Connection, tables: list[str]) -> list[str]:
    """
    Time is not a concept. Greps structured text fields for date/duration content.

    Deliberately crude: it catches "by Friday" and "within 2 weeks" landing in an
    artefact, which is the failure that matters. Ordering words are fine.
    """
    banned = re.compile(
        r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
        r"jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec|"
        r"deadline|due date|\d+\s*(day|week|month|hour|minute)s?)\b",
        re.IGNORECASE,
    )
    problems = []
    for table in tables:
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")
                if r[2].upper().startswith("TEXT")]
        for row in conn.execute(f"SELECT id, {', '.join(cols)} FROM {table}"):
            for col in cols:
                value = row[col]
                if isinstance(value, str) and banned.search(value):
                    problems.append(
                        f"{table}.{row['id']}.{col} contains time content: {value[:60]!r}")
    return problems


def check_messages_carry_refs(conn: sqlite3.Connection, verb: str) -> list[str]:
    """
    Structural traceability: a question must point at what raised it.

    Liaison never invents questions, and this is how that is asserted rather
    than trusted — an empty ref set means the question came from nowhere.
    """
    problems = []
    for r in conn.execute(
        "SELECT id, body_refs FROM messages WHERE verb = ?", (verb,)
    ):
        if not json.loads(r["body_refs"] or "[]"):
            problems.append(f"{verb} message {r['id']} carries no refs — invented")
    return problems
