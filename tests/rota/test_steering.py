"""
Loop 6's two missing acts: interrupt and cancel.

Preemption was rung one (law 9's reorder). These are the other two ways a
batch stops early, and they are deliberately different states: an interrupt
is a pause -- deferred work re-offers the moment it is schedulable -- and a
cancellation is terminal, because the approval the batch delivers against
has been withdrawn. Before `cancel` existed, a revoked item's batch simply
fell out of `batch_start`'s candidacy and waited in the game forever:
pending, deferred, or running against a dead approval. A state with no exit,
one loop along from where that phrase was coined.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core import lifecycle
from rota.core.loop import step
from rota.core.predicates import cancel
from rota.core.scheduler import frontier_readonly, tick_batch_start
from rota.llm.llm import Pins, ScriptedBackend


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance, approval, "
                 "approval_ver, version) VALUES ('i1','ship it','in_scope',"
                 "'decided','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('t1','i1','do it')")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES "
                 "('b1','i1','running')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','t1')")
    conn.commit()
    return conn


def _revoke(db):
    """An amendment past the approval: the revocation predicate's trigger."""
    db.execute("UPDATE items SET version = 2 WHERE id = 'i1'")
    db.commit()


def test_a_revoked_items_batch_is_offered_for_cancellation(db):
    assert cancel(db) == [], "an approved item's batch is nobody's business"
    _revoke(db)
    (wake,) = cancel(db)
    assert wake.refs == ("b1",)


def test_the_scheduler_ends_it_and_the_state_is_terminal(db):
    _revoke(db)
    s = step(db, backend=ScriptedBackend(["done"]),
             pins=Pins(model="stub", temperature=0.0))
    assert "abandoned b1" in (s.note or ""), s
    row = db.execute("SELECT status FROM batches WHERE id='b1'").fetchone()
    assert row["status"] == "abandoned"
    assert cancel(db) == [], "the predicate drained"
    assert not tick_batch_start(db), "abandoned work is never offered again"


def test_re_approval_does_not_resurrect_an_abandoned_batch(db):
    """The difference between the two stops, held from the other side: a
    deferral resumes on schedulability, an abandonment does not -- the item
    can come back, and its work starts as a new batch, grouped fresh against
    whatever the scope now says."""
    _revoke(db)
    lifecycle.abandon(db, "b1")
    db.execute("UPDATE items SET approval_ver = 2 WHERE id = 'i1'")
    db.commit()
    assert not tick_batch_start(db)
    assert cancel(db) == []


def test_an_interrupt_is_a_pause_not_a_verdict(db):
    """The brake pedal: defer keeps the worktree and the batch re-offers the
    moment nothing outranks it."""
    lifecycle.defer(db, "b1")
    row = db.execute("SELECT status FROM batches WHERE id='b1'").fetchone()
    assert row["status"] == "deferred"
    (wake,) = tick_batch_start(db)
    assert wake.refs == ("b1",), "deferred work resumes by being scheduled"


def test_a_running_batch_beats_a_pending_twin_to_the_cancellation(db):
    """Two batches revoked at once cancel deterministically, oldest id first
    -- the frontier's purity claim extends to the newest predicate."""
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('i2','also','in_scope',"
               "'decided','approved',1,2)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('t2','i2','more')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES "
               "('b2','i2','pending')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('b2','t2')")
    _revoke(db)
    wakes = cancel(db)
    assert [w.refs[0] for w in wakes] == ["b1", "b2"]
    first = [str(w) for w in frontier_readonly(db)]
    assert first == [str(w) for w in frontier_readonly(db)]


def test_a_quarantine_lifts_when_its_subject_moves(db):
    """The never-delete rule had no "the world moved" case: a repaired
    criterion could never wake the Tester that gave up on it, and every S0
    walk died permanently at its first quarantine even after the cause was
    fixed. A commit that writes a row a quarantined tick is about -- or
    writes criteria/tests into the batch its refs name -- is the exit; an
    unrelated quarantine survives."""
    from rota.core.db import _lift_quarantines
    from rota.core.scheduler import tick_key
    from rota.core.predicates import Wake

    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c1','t1','old words')")
    key = tick_key(Wake("tester", "tick:tests_missing", refs=("b1",)))
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
               "VALUES (?, 5, 1)", (key,))
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
               "VALUES ('architect|tick:survey|src/other', 5, 1)")
    db.commit()

    class W:
        table = "criteria"
        row_id = "c1"

    _lift_quarantines(db, W)
    assert not db.execute("SELECT 1 FROM tick_attempts WHERE tick_key=?",
                          (key,)).fetchone(), "the moved subject revives"
    assert db.execute("SELECT 1 FROM tick_attempts WHERE tick_key LIKE "
                      "'%other%'").fetchone(), "an unrelated debt survives"


def test_an_amended_delivered_item_owes_new_tickets_and_keeps_its_merged_batch(db):
    """Amendment level 2, the merged half (plans/amendment-and-conflicts.md,
    2026-09-12): an item delivered at version 1, amended to version 2 and
    re-approved, is sliced again. Its old tickets stay with the merged
    batch, which is never cancelled, and the new tickets group fresh."""
    from rota.core.scheduler import tick_slicing

    db.execute("UPDATE batches SET status = 'merged' WHERE id = 'b1'")
    db.execute("INSERT INTO config (key, value) VALUES ('delivered:i1', '1')")
    db.commit()
    assert tick_slicing(db) == [], "a delivered item at its delivered version owes nothing"
    db.execute("UPDATE items SET version = 2, approval_ver = 2 WHERE id = 'i1'")
    db.commit()
    (wake,) = tick_slicing(db)
    assert wake.refs[0] == "i1"
    assert cancel(db) == [], "a merged batch is not live; nothing to cancel"
    row = db.execute("SELECT batch_id FROM batch_tickets WHERE ticket_id = 't1'").fetchone()
    assert row["batch_id"] == "b1"
