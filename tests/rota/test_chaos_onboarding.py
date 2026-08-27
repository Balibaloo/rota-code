"""
Loop 1's chaos: the understanding loop, hurt the ways LOOPS.md names.

The core's three injuries are the floor (`test_chaos.py`); these are the
survey-shaped ones. What must survive is always the same claim: the database
is the world before or the world after, never in between, and the frontier
re-derives from whichever it is.
"""
from __future__ import annotations

import pytest

from rota.core import config
from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.runner import run_session
from rota.core.scheduler import tick_survey
from rota.llm.llm import Completion, Pins, ScriptedBackend
from rota.onboarding import boot
from rota.testkit import gitfixture

PINS = Pins(model="stub", temperature=0.0)


@pytest.fixture
def world(tmp_path):
    db = init_db(tmp_path / "rota.db")
    config.set(db, "onboarding_phases", "survey")
    repo = gitfixture.make(tmp_path, name="chaos_onboarding")
    boot.onboard(db, repo.root)
    yield db, repo
    gitfixture.cleanup(repo)


class DiesAfter:
    """Answers n times, then dies the way a network does."""

    name = "chaos"

    def __init__(self, answers: list[str]):
        self.answers = answers
        self.calls = 0

    def complete(self, system, user, pins):
        self.calls += 1
        if self.calls <= len(self.answers):
            return Completion(text=self.answers[self.calls - 1])
        raise ConnectionError("the model went away mid-survey")


def test_a_survey_killed_mid_area_never_happened(world):
    """The first injury: the session stages a real glossary write, then the
    model dies. No records, no terms, the area still offered to the same
    role, and the frontier identical to before the attempt."""
    db, repo = world
    (wake, *_) = tick_survey(db)
    before = [str(w) for w in tick_survey(db)]

    out = run_session(
        db, wake,
        backend=DiesAfter(["TOOL: glossary.amend(term='prorate', "
                           "sense_short='a partial-period charge')"]),
        pins=PINS, instructions="survey it", area=wake.refs[0])

    assert not out.committed
    assert db.execute("SELECT COUNT(*) n FROM survey_records"
                      ).fetchone()["n"] == 0
    assert db.execute("SELECT COUNT(*) n FROM glossary_terms"
                      ).fetchone()["n"] == 0
    assert [str(w) for w in tick_survey(db)] == before, \
        "the area is still owed, to the same role, in the same order"


def test_a_corrupted_attest_reopens_rather_than_sealing(world):
    """The second injury: an attest's stored area view is damaged after
    commit. The freshness rule already treats a mismatched hash as a survey
    of a tree that is gone -- corruption must land in that bucket, reopening
    the area, and never in the closed bucket, where a damaged row would seal
    an area forever with a lie."""
    db, repo = world
    (wake, *_) = tick_survey(db)
    area = wake.refs[0]

    from rota.roles.api import area_content_hash

    db.execute("INSERT INTO survey_records (id, area, outcome, area_hash) "
               "VALUES (?, ?, 'none_found', ?)",
               (f"{wake.role}:{area}", area, area_content_hash(db, area)))
    db.commit()
    assert area not in {w.refs[0] for w in tick_survey(db)
                        if w.role == wake.role}, "attested closes it"

    db.execute("UPDATE survey_records SET area_hash = 'corrupt!' "
               "WHERE area = ?", (area,))
    db.commit()
    assert area in {w.refs[0] for w in tick_survey(db)
                    if w.role == wake.role}, \
        "a damaged record reads as unread, never as sealed"


def test_two_onboardings_share_a_checkout_without_touching_it(tmp_path):
    """The third injury: two runs onboard the same checkout at once. The
    checkout is shared state and onboarding's whole licence there is to
    *read* -- so both runs must end with identical indexes and the checkout
    byte-identical to before either began."""
    import hashlib
    import threading

    repo = gitfixture.make(tmp_path, name="shared_checkout")

    def snapshot() -> dict[str, str]:
        out = {}
        for f in sorted(repo.root.rglob("*")):
            if f.is_file() and ".git" not in f.parts:
                out[str(f.relative_to(repo.root))] = hashlib.sha256(
                    f.read_bytes()).hexdigest()
        return out

    before = snapshot()
    errors: list[BaseException] = []

    def onboard(i):
        # The connection is born and dies in its own thread -- SQLite objects
        # are thread-bound, and each run owns its database anyway.
        try:
            db = init_db(tmp_path / f"run{i}.db")
            config.set(db, "onboarding_phases", "survey")
            boot.onboard(db, repo.root)
            db.close()
        except BaseException as e:                         # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=onboard, args=(i,)) for i in (1, 2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors, errors

    assert snapshot() == before, "onboarding wrote into the shared checkout"
    import sqlite3 as _sq

    index = []
    for i in (1, 2):
        db = _sq.connect(tmp_path / f"run{i}.db")
        db.row_factory = _sq.Row
        index.append(sorted((r["grain"], r["grain_kind"]) for r in db.execute(
            "SELECT grain, grain_kind FROM code_index")))
        db.close()
    assert index[0] == index[1], "two readers of one tree saw one tree"
    gitfixture.cleanup(repo)
