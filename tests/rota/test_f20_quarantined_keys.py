"""Facts F20 and F21: one reader for quarantined keys, and words for a person.

The root-cause audit of 2026-10-27 counted ten readers that split a tick key
by their own rule, a lift that matched `_` as a wildcard, and raw ledger
writes that skipped the lift (frame 242). Night 170 ended with
`tester|tick:tests_missing|b_3` quarantined, and the principal's page said
"tests_missing for b_3".
"""
from __future__ import annotations

import pytest

from rota.core.db import Write, _lift_quarantines, init_db


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _quarantine(db, key: str, attempts: int = 3) -> None:
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
               "reported) VALUES (?, ?, 1, 0)", (key, attempts))


def _keys(db) -> set[str]:
    return {r["tick_key"] for r in db.execute("SELECT tick_key FROM tick_attempts")}


def test_night_170s_page_says_the_tests_missing_key_in_his_words(db):
    from rota.roles.principal import render_state

    _quarantine(db, "tester|tick:tests_missing|b_3")
    page = render_state(db)
    assert "tests_missing" not in page and "tick:" not in page, page
    assert ("Stuck. The team gave up: the team could not write the tests for "
            "b_3 after 3 attempts.") in page, page


def test_a_parked_ledger_entry_lifts_the_keys_about_it(db):
    """`park_merged` set a ledger status through a raw write, and the lift
    never ran (frame 242)."""
    from rota.core.lifecycle import park_merged

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('i_1', 'the tool prints JSON', 'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b_1', 'i_1', 'merged')")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "author) VALUES ('l_1', 'i_1', 'items', 'JSON on stdout', 'architect')")
    _quarantine(db, "liaison|tick:agenda|l_1")
    assert park_merged(db, "b_1") == ["l_1"]
    assert "liaison|tick:agenda|l_1" not in _keys(db)


def test_the_lift_matches_a_ref_whole_and_never_as_a_pattern(db):
    """The LIKE of the lift read `_` as a wildcard and ignored case (frame
    242, a probe of frame 240's review)."""
    for ref in ("a_b", "aXb", "A_B"):
        _quarantine(db, f"vision_keeper|tick:contested|{ref}")
    _lift_quarantines(db, Write("items", "a_b", {"approval": "approved"},
                                op="update", amends=False), True)
    assert _keys(db) == {"vision_keeper|tick:contested|aXb",
                         "vision_keeper|tick:contested|A_B"}


def test_an_area_both_survey_roles_gave_up_on_is_settled_for_both(db):
    """`_survey_wakes` kept the given-up area in a map of area to role, so
    the second role's key hid the first role's."""
    from rota.core.scheduler import _survey_wakes

    db.execute("INSERT INTO code_index (grain, grain_kind, area) "
               "VALUES ('src/a.py', 'path', 'src')")
    _quarantine(db, "terminologist|tick:survey|src")
    _quarantine(db, "architect|tick:survey|src")
    assert _survey_wakes(db) == []


def test_the_keys_of_a_batch_are_its_one_ref_keys_and_a_page_reads_pairs(db):
    from rota.core.scheduler import given_up, key_parts, quarantined_keys

    assert key_parts("critic|tick:finding_review|b_1,f_2") == (
        "critic", "tick:finding_review", ("b_1", "f_2"))
    assert key_parts("-|tick:constraint_zero|") == ("-", "tick:constraint_zero", ())
    _quarantine(db, "developer|tick:tests_failing|b_1")
    _quarantine(db, "critic|tick:finding_review|b_1,f_2")
    _quarantine(db, "-|do:park|b_1")
    _quarantine(db, "-|tick:constraint_zero|")
    assert given_up(db, "b_1") == ["developer|tick:tests_failing|b_1"]
    assert quarantined_keys(db, ["b_1"], pairs=True, constraint_zero=False) == [
        "-|do:park|b_1", "critic|tick:finding_review|b_1,f_2",
        "developer|tick:tests_failing|b_1"]
