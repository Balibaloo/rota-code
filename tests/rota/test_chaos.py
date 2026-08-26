"""
Chaos: the system, hurt on purpose.

`LOOPS.md`'s headline when this file was born: nothing is at G3, because no
loop had ever been hurt on purpose. The scheduler's module docstring has
claimed from the start that it is "stateless, disposable ... killing and
restarting it at any moment loses nothing", and `run_session`'s contract that
"on any failure the session never happened". Claims of that shape are exactly
what a suite exists to hold, and until here they were docstrings.

Each test hurts one thing the way operations would: a model dying mid-turn, a
process killed between steps, a backend that answers garbage. What must
survive is always the same: the database is either the world before or the
world after -- never a world in between -- and the frontier re-derives from
whichever it is.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.loop import step
from rota.core.predicates import Wake
from rota.core.runner import run_session
from rota.core.scheduler import frontier_readonly
from rota.llm.llm import Pins, ScriptedBackend

PINS = Pins(model="stub", temperature=0.0)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


class DiesMidSession:
    """A backend that answers once, then dies the way a network does."""

    name = "chaos"

    def __init__(self, first: str):
        self.first = first
        self.calls = 0

    def complete(self, system, user, pins):
        self.calls += 1
        if self.calls == 1:
            from rota.llm.llm import Completion

            return Completion(text=self.first)
        raise ConnectionError("the model went away mid-session")


def _one_open_question(db):
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','recipe','a seed note','observed')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m1','t1','liaison','terminologist',"
               "'ask','[\"g1\"]',1)")
    db.commit()


def test_a_session_that_dies_mid_flight_never_happened(db):
    """
    `run_session`'s contract, held under an actual death rather than a tidy
    error: the first turn stages a real write, the second turn never returns,
    and the world must be the one from before -- no writes, no messages, the
    trigger open with its attempt count raised, and the same wake back on the
    frontier for the retry.
    """
    _one_open_question(db)
    before_frontier = [str(w) for w in frontier_readonly(db)]

    out = run_session(
        db, Wake("terminologist", "message", message_id="m1", detail="ask"),
        backend=DiesMidSession("TOOL: glossary.lookup(term='recipe')"),
        pins=PINS, instructions="answer it")

    assert not out.committed
    assert db.execute("SELECT COUNT(*) n FROM receipts").fetchone()["n"] == 0
    assert db.execute("SELECT COUNT(*) n FROM messages WHERE from_role="
                      "'terminologist'").fetchone()["n"] == 0
    row = db.execute("SELECT status, attempts FROM messages WHERE id='m1'"
                     ).fetchone()
    assert row["status"] == "open", "the question survives the death"
    assert row["attempts"] == 1, "and the death was counted"
    assert [str(w) for w in frontier_readonly(db)] == before_frontier, \
        "the frontier re-derives the same world"


def test_the_scheduler_killed_between_steps_loses_nothing(db):
    """
    The module docstring's boast, as an outcome. A pass is interrupted by the
    bluntest possible means -- we stop calling it, throw the in-memory state
    away, and 'restart' by evaluating a fresh frontier on the same database.
    Restarting must offer exactly what the killed scheduler would have.
    """
    _one_open_question(db)
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g2','intent','a config','observed')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m2','t2','liaison','architect','ask',"
               "'[\"g2\"]',2)")
    db.commit()

    s = step(db, backend=ScriptedBackend(
        ["TOOL: msg.answer_liaison(refs=['g1'])", "done"]), pins=PINS)
    assert s.outcome and s.outcome.committed

    # The kill: no shutdown, no handoff. A "new scheduler" is only a new call,
    # because there is nothing else a scheduler is.
    offered = {str(w) for w in frontier_readonly(db)}
    again = {str(w) for w in frontier_readonly(db)}
    assert offered == again, "evaluation is pure; a restart sees the same world"
    assert any("m2" in w for w in offered), "the un-run work is still offered"
    assert not any("m1" in w and "ask" in w for w in offered), \
        "the finished work is not offered again"


def test_a_backend_speaking_garbage_costs_turns_not_worlds(db):
    """
    A model that answers static must burn its turns and leave the world
    unwritten -- committed-but-empty is acceptable, half-written is not.
    """
    _one_open_question(db)
    out = run_session(
        db, Wake("terminologist", "message", message_id="m1", detail="ask"),
        backend=ScriptedBackend(["%%% ::: not a call :::", "]]]][[[", "done"]),
        pins=PINS, instructions="answer it")

    assert db.execute("SELECT COUNT(*) n FROM receipts").fetchone()["n"] == 0
    assert db.execute(
        "SELECT COUNT(*) n FROM messages WHERE from_role='terminologist'"
    ).fetchone()["n"] == 0
    # Whether the empty session commits is the runner's call; what it must
    # not do is write anything on the way to deciding.
    assert out.result is None or not out.result.writes
