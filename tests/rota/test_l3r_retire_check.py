"""Sprint 35, row 3: the L3R runner counts the retire of a deleted criterion.

W14 retires a criterion when his landed ruling drops its row. The count of
that retire moved from nights to the 24 L3R cases (Roman, 2026-10-29). The
runner's `retire_problems` reads the retire through `criteria_page_acts`.
These tests seed night 175's clarify m102, with c_2 and c_3, from its case.
"""
from __future__ import annotations

import json

from rota.core.db import init_db
from rota.llm.llm import Pins, ScriptedBackend
from rota.testkit import fixtures

from .test_l3_rulings import CASES, landed_lines, retire_problems

CASE_ID = "L3R-n175-m102-m103"
C2, C3 = "c_2_format_filename_example", "c_3_format_filename_example"
WORDS = ("Drop both of those examples, because I asked for only one example "
         "in the docstring.")


def _case() -> dict:
    case = next(c for c in fixtures.load_case(CASES) if c["id"] == CASE_ID)
    return fixtures.for_run(case, 1)


def test_the_case_names_both_criteria_his_words_delete():
    assert _case()["expect_retired"] == [C2, C3]


def test_a_landed_drop_of_the_row_reads_as_the_retire(tmp_path):
    """A clarify numbers no line, so the seat rules each row by its id. The
    runner lands the ruling through the Liaison's door and `apply_rulings`."""
    case = _case()
    # The door asks each act to rest on his own words.
    drop = {"verdict": "contest", "act": "drop", "target_kind": "row",
            "words": "Drop both of those examples"}
    call = (f"TOOL: rulings.rule(rulings={json.dumps({C2: drop, C3: drop})}, "
            f"words={json.dumps(WORDS)})")
    db = tmp_path / "case.db"
    result = fixtures.run_case(case, db, ScriptedBackend([call, "done"]),
                               pins=Pins(model="stub", temperature=0.0))
    got = landed_lines(db, case["inbound"]["id"], by_ref=True)
    assert got is not None, result.problems
    assert {ref: (r["act"], r["target_kind"]) for ref, r in got.items()} == {
        C2: ("drop", "row"), C3: ("drop", "row")}
    assert retire_problems(db, case) == []


def test_no_landed_ruling_names_each_missing_retire(tmp_path):
    case = _case()
    db = tmp_path / "case.db"
    conn = init_db(db)
    fixtures.seed(conn, case["fixture"])
    fixtures.seed_inbound(conn, case)
    conn.commit()
    conn.close()
    assert retire_problems(db, case) == [
        f"criterion {C2}: not retired, expected a retire",
        f"criterion {C3}: not retired, expected a retire"]


def test_a_case_with_no_expect_retired_gets_no_problem(tmp_path):
    case = {k: v for k, v in _case().items() if k != "expect_retired"}
    assert retire_problems(tmp_path / "unused.db", case) == []
