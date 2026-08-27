"""
A score is a fact about a load, and the register can now say which.

The ruling (2026-08-27, "yes -- and track flips"): a case that flips from red
to green counts as fixed only after passing on two separate recording loads,
and every flip is visible so the chronically marginal become a class rather
than a series of surprises. Measured cause: temp-0 is stable within a model
residency and not across; `fix-the-code` greened on one load and went 0/5 on
the next with the same prompts.

Everything here is derived from `case_runs` -- the runs are the record, and
`flip_history`/`trust` are readings of them, so there is no second source of
truth to drift.
"""
from __future__ import annotations

import json

import pytest

from rota.llm.cassettes import (flip_history, open_dev_db, provisional_cases,
                                trust)


@pytest.fixture
def db(tmp_path):
    return open_dev_db(tmp_path / "dev.db")


def _runs(db, case_id, prompt, load, results, seq0):
    for i, ok in enumerate(results, 1):
        db.execute(
            "INSERT INTO case_runs (case_id, model, prompt_hash, run_no, "
            "passed, problems, transcript, seq, load_id) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (case_id, "m", prompt, i, int(ok), "[]", "[]", seq0 + i, load))
    db.commit()


def test_a_green_that_never_flipped_is_earned_on_one_load(db):
    """No history of being wrong to live down."""
    _runs(db, "c", "p1", "m@1", [1, 1, 1, 1, 1], 0)
    assert trust(db, "c") == "earned"


def test_a_flip_to_green_is_provisional_until_a_second_load(db):
    _runs(db, "c", "p1", "m@1", [0, 0, 0, 0, 0], 0)
    _runs(db, "c", "p2", "m@2", [1, 1, 1, 1, 1], 10)
    assert trust(db, "c") == "provisional"
    assert provisional_cases(db) == ["c"]

    _runs(db, "c", "p2", "m@3", [1, 1, 1, 1, 1], 20)
    assert trust(db, "c") == "earned", "the second load confirms"
    assert provisional_cases(db) == []


def test_the_marginal_case_shows_its_flips(db):
    """`fix-the-code`'s shape: green one load, red the next, same prompts."""
    _runs(db, "c", "p1", "m@1", [1, 1, 1, 1, 1], 0)
    _runs(db, "c", "p1", "m@2", [0, 0, 0, 0, 0], 10)
    _runs(db, "c", "p1", "m@3", [1, 1, 1, 1, 1], 20)
    flips = [g for g in flip_history(db, "c") if g["flip"]]
    assert len(flips) == 2, "chronic marginality is a visible count"
    assert trust(db, "c") == "provisional", \
        "its latest green flipped and only one load says so"


def test_a_red_is_red_whatever_its_history(db):
    _runs(db, "c", "p1", "m@1", [1, 1, 1, 1, 1], 0)
    _runs(db, "c", "p1", "m@2", [0, 0, 1, 0, 0], 10)
    assert trust(db, "c") == "red"


def test_the_bar_is_the_registers_own(db):
    """4 of 5 passes; 3 of 5 does not."""
    _runs(db, "c", "p1", "m@1", [1, 1, 1, 1, 0], 0)
    assert trust(db, "c") == "earned"
    _runs(db, "d", "p1", "m@1", [1, 1, 1, 0, 0], 10)
    assert trust(db, "d") == "red"


def test_legacy_rows_read_as_one_indistinct_load(db):
    """Runs from before the column exist with load_id '' -- one old load,
    which can seed a flip but never confirm a new green."""
    _runs(db, "c", "p1", "", [0, 0, 0, 0, 0], 0)
    _runs(db, "c", "p2", "m@2", [1, 1, 1, 1, 1], 10)
    assert trust(db, "c") == "provisional"


def test_recording_stamps_the_current_load(db, monkeypatch):
    from rota.llm import cassettes as C
    from rota.llm.llm import Pins

    pins = Pins(model="m", temperature=0.0).with_prompt("x")
    C.record_case_run(db, "c", pins, 1, True, [])
    row = db.execute("SELECT load_id FROM case_runs").fetchone()
    assert row["load_id"].startswith("m@")
    assert row["load_id"] == C.current_load(pins)
