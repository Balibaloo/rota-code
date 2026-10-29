"""Frame 345, review p5: the landing count, the remove word and the match.

The review of ac900593 found that the three drop cases of l1_landing.yaml
land their rows and still count 0 writes (finding 1). It found that the
prompt calls `remove` on a page line that is no code line a drop, and the
code did not (finding 2). It found that "1 is fine, 2 and 3 are wrong"
bound line 1 to the whole sentence (finding 4).
"""
from __future__ import annotations

import json
import pathlib
import sqlite3

import pytest

from rota.llm.llm import Pins, ScriptedBackend
from rota.roles.api import line_words
from rota.testkit import fixtures

CASES = str(pathlib.Path(__file__).resolve().parent / "cases" / "l1_landing.yaml")
# The three drop cases, with the page size and the lines of c2 and c3.
DROPS = [
    ("L1-LI-remove-lines-on-a-criteria-page-is-a-drop", 9, (7, 8)),
    ("L1-LI-drop-both-examples-is-a-drop-of-both-rows", 2, (1, 2)),
    ("L1-LI-removing-lines-is-right-is-a-drop", 9, (7, 8)),
]


def _run(tmp_path, case_id: str, size: int, word: str, lines: tuple):
    case = fixtures.for_run(
        next(c for c in fixtures.load_case(CASES) if c["id"] == case_id), 1)
    rulings = {str(n): (word if n in lines else "approve")
               for n in range(1, size + 1)}
    call = f"TOOL: rulings.rule(rulings={json.dumps(rulings)})"
    db = tmp_path / "case.db"
    res = fixtures.run_case(case, db, ScriptedBackend([call, "done"]),
                            pins=Pins(model="stub", temperature=0.0))
    return res, sqlite3.connect(db)


@pytest.mark.parametrize("case_id, size, lines", DROPS)
def test_a_landing_counts_its_ruled_refs_rows_as_writes(tmp_path, case_id,
                                                        size, lines):
    """`session_commit` writes no receipt for a ruled_refs row, so the
    runner counts the reading's rows through the rulings receipts."""
    res, conn = _run(tmp_path, case_id, size, "drop", lines)
    refs = res.delta.writes.get("ruled_refs", [])
    assert len(refs) >= 2
    reading = {r[0] for r in conn.execute(
        "SELECT id FROM ruled_refs WHERE source = 'reading'")}
    assert set(refs) == reading
    assert not [p for p in res.problems if "ruled_refs" in p]


@pytest.mark.parametrize("case_id, size, lines", DROPS)
def test_remove_on_a_line_that_is_no_code_lands_as_a_drop(tmp_path, case_id,
                                                          size, lines):
    """The call of the review's probe 5, the word remove on c2 and c3."""
    res, conn = _run(tmp_path, case_id, size, "remove", lines)
    got = conn.execute(
        "SELECT DISTINCT line, verdict, act, target_kind FROM ruled_refs "
        "WHERE source = 'reading' AND act IS NOT NULL ORDER BY line").fetchall()
    assert got == [(n, "contest", "drop", "row") for n in lines]
    assert not [p for p in res.problems if "ruled_refs" in p]


def test_a_bare_subject_after_a_comma_binds_its_own_clause():
    assert line_words("1 is fine, 2 and 3 are wrong", 3) == {
        1: "1 is fine", 2: "2 and 3 are wrong", 3: "2 and 3 are wrong"}


def test_a_line_list_in_one_reference_keeps_its_whole_clause():
    words = "lines 7, 8 and 9 go"
    got = line_words(words, 9)
    assert [got[n] for n in (7, 8, 9)] == [words] * 3
    assert all(got[n] is None for n in range(1, 7))
