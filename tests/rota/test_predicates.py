"""
Predicates, and the hard constraint that none may be missing.

The load-bearing case is `test_lint_catches_a_dead_end`: a lint nobody has proved
can fail is a lint you are trusting rather than using.
"""
from __future__ import annotations

import pytest

from rota import predicates as P
from rota.db import init_db


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def test_every_lifecycle_state_has_a_way_out():
    """
    The hard constraint.

    A state that is neither drained nor declared terminal is a place work stops
    while the system reports itself finished — invisible to every other check,
    because quiescence is defined as "no predicate fires".
    """
    assert P.check_terminal_states() == []


def test_lint_catches_a_dead_end(monkeypatch):
    """Remove a predicate's drain and the lint must notice."""
    original = P.REGISTRY["contested"]
    monkeypatch.setitem(
        P.REGISTRY, "contested",
        P.Predicate(name="contested", wakes=original.wakes, drains=(),
                    fn=original.fn))

    problems = P.check_terminal_states()
    assert any("items.approval = 'contested'" in p for p in problems), problems


def test_lint_catches_a_new_state_with_no_exit(monkeypatch):
    """Adding a state to the schema without a way out fails the build."""
    monkeypatch.setattr(
        P, "schema_states",
        lambda: {("batches", "status"): ["pending", "running", "deferred",
                                         "merged", "abandoned"]})
    problems = P.check_terminal_states()
    assert any("'abandoned'" in p for p in problems), problems


def test_every_predicate_wakes_a_real_role():
    assert P.check_predicates_wake_real_roles() == []


def test_the_four_dead_ends_are_drained():
    """
    The specific holes the sweep found. Named individually so a regression says
    which one came back.
    """
    drained = P.drained_states()
    for state in [
        ("items", "approval", "contested"),          # the requester's rejection
        ("statements", "status", "contradicted"),    # two statements conflict
        ("verdicts", "result", "pass"),              # nothing merged it
        ("messages", "status", "quarantined"),       # the system gave up, silently
    ]:
        assert state in drained or state in P.TERMINAL, f"{state} is a dead end again"


def test_open_messages_are_drained_by_a_declared_predicate():
    """
    The frontier used to be "tips ∪ predicates", which put its definition in two
    places and made the tips half invisible to checks written against the other.
    """
    assert ("messages", "status", "open") in P.drained_states()


def test_terminal_states_carry_a_reason():
    """A terminal state is a claim that nothing further is owed. Claims need
    reasons; an unexplained one is usually an oversight wearing a decision."""
    missing = [k for k, why in P.TERMINAL.items() if not why.strip()]
    assert not missing, missing


def test_delivery_loop_is_predicated(db):
    """
    It had one predicate — batch_start — and four dead ends. The second half of
    the system could not turn without a message arriving from somewhere.
    """
    names = set(P.REGISTRY)
    for needed in ("tests_missing", "annotate", "review", "structural_review",
                   "tests_failing", "verdict_failed", "merge"):
        assert needed in names, f"delivery loop still missing {needed}"


def test_all_wakes_runs_clean_on_an_empty_database(db):
    """Every predicate must survive an empty database — boot evaluates them all
    before anything exists."""
    assert P.all_wakes(db) == []


def test_predicates_are_pure(db):
    """
    Evaluating the frontier must not change it.

    A predicate that writes would make the frontier depend on how often it was
    computed, and the scheduler computes it constantly.
    """
    db.execute("INSERT INTO items (id, text, kind, provenance, approval) "
               "VALUES ('i1','x','scope','decided','contested')")
    before = [dict(r) for r in db.execute("SELECT * FROM items")]

    P.all_wakes(db)
    P.all_wakes(db)

    after = [dict(r) for r in db.execute("SELECT * FROM items")]
    assert before == after
    assert db.execute("SELECT COUNT(*) n FROM messages").fetchone()["n"] == 0
    assert db.execute("SELECT COUNT(*) n FROM sessions").fetchone()["n"] == 0


def test_contested_wakes_the_items_owner(db):
    db.execute("INSERT INTO items (id, text, kind, provenance, approval) "
               "VALUES ('i1','delete accounts','scope','decided','contested')")
    wakes = P.REGISTRY["contested"].fn(db)
    assert [w.role for w in wakes] == ["vision"]
    assert wakes[0].refs == ("i1",)


def test_tests_failing_stops_at_the_cap(db):
    db.execute("INSERT INTO items (id, text, kind, provenance) "
               "VALUES ('i1','x','scope','decided')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','running')")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c1','t1','x')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst1','b1','c1','p','b')")

    db.execute("INSERT INTO test_runs (id, batch_id, test_id, result, attempt) "
               "VALUES ('r1','b1','tst1','fail',3)")
    assert P.REGISTRY["tests_failing"].fn(db), "should bounce below the cap"

    db.execute("UPDATE test_runs SET attempt = 10")
    assert not P.REGISTRY["tests_failing"].fn(db), "should stop at the cap"
