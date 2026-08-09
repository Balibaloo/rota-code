"""
Checkable judgement: LLM proposes, code verifies.

Where a role's output is a *choice inside a legal space*, the legality is
mechanically decidable even though the choice is not. That is the pattern this
module implements, and it is what keeps the suite from degenerating into judging
prose:

  * Interface's segmentation must cover the utterance — spans exist, do not
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


def check_segmentation(conn: sqlite3.Connection, utterance_id: str) -> list[str]:
    """
    Statements cut from an utterance must quote it, not summarise it.

    Three properties, all decidable:
      1. every statement's text appears in the utterance (modulo whitespace);
      2. spans are within bounds and do not overlap;
      3. the union of spans is reported, so uncovered substance is visible for
         review rather than silently dropped.
    """
    row = conn.execute(
        "SELECT text FROM utterances WHERE id = ?", (utterance_id,)).fetchone()
    if not row:
        return [f"no utterance {utterance_id}"]
    utterance = row["text"]
    haystack = _norm(utterance)

    problems: list[str] = []
    spans: list[tuple[int, int, str]] = []

    for s in conn.execute(
        "SELECT id, text, span_start, span_end FROM statements "
        "WHERE span_utterance = ? ORDER BY span_start", (utterance_id,)
    ):
        if _norm(s["text"]) not in haystack:
            problems.append(
                f"{s['id']} paraphrases: {s['text']!r} is not in the utterance")
        start, end = s["span_start"], s["span_end"]
        if start < 0 or end > len(utterance) or start >= end:
            problems.append(
                f"{s['id']} span [{start},{end}] out of bounds for "
                f"{len(utterance)}-char utterance")
        else:
            spans.append((start, end, s["id"]))

    spans.sort()
    for (a_start, a_end, a_id), (b_start, b_end, b_id) in zip(spans, spans[1:]):
        if b_start < a_end:
            problems.append(f"spans overlap: {a_id} [{a_start},{a_end}] and "
                            f"{b_id} [{b_start},{b_end}]")

    return problems


def uncovered_spans(conn: sqlite3.Connection, utterance_id: str) -> list[tuple[int, int]]:
    """Regions of the utterance no statement claims. Not an error — a review flag."""
    row = conn.execute(
        "SELECT text FROM utterances WHERE id = ?", (utterance_id,)).fetchone()
    if not row:
        return []
    length = len(row["text"])
    spans = sorted(
        (r["span_start"], r["span_end"]) for r in conn.execute(
            "SELECT span_start, span_end FROM statements WHERE span_utterance = ?",
            (utterance_id,))
    )
    gaps, cursor = [], 0
    for start, end in spans:
        if start > cursor:
            gaps.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < length:
        gaps.append((cursor, length))
    return [(a, b) for a, b in gaps if row["text"][a:b].strip()]


def check_statement_count(conn: sqlite3.Connection, utterance_id: str,
                          expected: int) -> list[str]:
    """
    Client granularity is a *count* assertion, which is why it is checkable.

    "we need SSO, but only if it works with our LDAP" is one statement, not two:
    the condition is part of the ask. Over-segmentation is the failure mode worth
    catching, because it looks like diligence.
    """
    n = conn.execute(
        "SELECT COUNT(*) c FROM statements WHERE span_utterance = ?",
        (utterance_id,)).fetchone()["c"]
    if n != expected:
        return [f"expected {expected} statement(s) at client granularity, got {n}"]
    return []


def check_bindings_resolve(conn: sqlite3.Connection) -> list[str]:
    """Every binding must name a grain that exists in the code index."""
    problems = []
    for r in conn.execute(
        "SELECT b.constraint_id AS cid, b.grain AS grain FROM constraint_bindings b "
        "LEFT JOIN code_index i ON i.grain = b.grain "
        "WHERE i.grain IS NULL AND b.resolves = 1"
    ):
        problems.append(f"{r['cid']} binds {r['grain']!r}, which is not in the index")
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


def check_criteria_terms(conn: sqlite3.Connection) -> list[str]:
    """Criteria are written in glossary terms; term_refs must exist and be used."""
    known = {r["id"] for r in conn.execute("SELECT id FROM glossary_terms")}
    problems = []
    for r in conn.execute("SELECT id, term_refs FROM criteria"):
        refs = json.loads(r["term_refs"] or "[]")
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

    Interface never invents questions, and this is how that is asserted rather
    than trusted — an empty ref set means the question came from nowhere.
    """
    problems = []
    for r in conn.execute(
        "SELECT id, body_refs FROM messages WHERE verb = ?", (verb,)
    ):
        if not json.loads(r["body_refs"] or "[]"):
            problems.append(f"{verb} message {r['id']} carries no refs — invented")
    return problems
