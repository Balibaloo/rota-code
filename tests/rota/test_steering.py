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
    conn.execute("INSERT INTO items (id, text, kind, approval, "
                 "approval_ver, version) VALUES ('i1','ship it','in_scope',"
                 "'approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('t1','i1','do it')")
    # A reopen follows a built change, so the batch has a commit (W10).
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
                 "('b1','i1','running','c0ffee1')")
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
    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) VALUES ('i2','also','in_scope',"
               "'approved',1,2)")
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
    fixed. A commit that moves a row a quarantined tick is about -- or
    moves criteria/tests in the batch its refs name -- is the exit; an
    unrelated quarantine survives. The move is a respecify: new words, and
    the criterion's version moves (frame 80)."""
    from rota.core.db import Write
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

    _commit(db, "s_re", "terminologist",
            Write("criteria", "c1", {"text": "new words",
                                     "surface_refs": '["run"]'}))
    assert not db.execute("SELECT 1 FROM tick_attempts WHERE tick_key=?",
                          (key,)).fetchone(), "the moved subject revives"
    assert db.execute("SELECT 1 FROM tick_attempts WHERE tick_key LIKE "
                      "'%other%'").fetchone(), "an unrelated debt survives"


def _commit(db, session_id, role, *writes):
    """Land writes the way the runner does, through the one commit path."""
    from rota.core.db import SessionResult, session_commit

    session_commit(db, SessionResult(session_id=session_id, role=role,
                                     writes=list(writes)))


def _quarantine(db, key, attempts=3):
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
               "reported) VALUES (?, ?, 1, 1)", (key, attempts))
    db.commit()


def _held(db, key):
    return db.execute("SELECT 1 FROM tick_attempts WHERE tick_key = ?",
                      (key,)).fetchone() is not None


def _summary_criteria_wakes(db):
    """The criteria wakes on `bg_1_summary` that `frontier` offers.

    `frontier` writes the quarantine as it reads, so it runs in a
    transaction rolled back after. `frontier_readonly` skips
    `quarantine_stalled` and would list the dropped wake."""
    from rota.core.scheduler import frontier

    db.execute("BEGIN")
    try:
        return [w for w in frontier(db) if w.kind == "tick:criteria"
                and "bg_1_summary" in w.refs]
    finally:
        db.execute("ROLLBACK")


def test_a_verdict_that_changes_nothing_revives_nothing(db):
    """clickI night 91 (2026-09-24): the Terminologist gave up on the
    summary's ticket, and the relay of the principal's verdict approved an
    approved item. Each write revived the tick, five rounds of ten sessions."""
    from rota.core.db import Write

    key = "terminologist|tick:criteria|bg_1_summary"
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('bg_1_summary','Click is a toolkit',"
               "'in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk_1_bg_1_summary','bg_1_summary',"
               "'the software is a command-line interface toolkit called Click')")
    _quarantine(db, key)

    approve = {"approval": "approved", "approval_ver": 1}
    _commit(db, "s258", "vision_keeper",
            Write("items", "bg_1_summary", approve, amends=False),
            Write("items", "bg_1_summary", {"priority": 1}, amends=False),
            Write("items", "bg_1_summary", approve, amends=False))
    row = db.execute("SELECT attempts, quarantined, reported FROM tick_attempts "
                     "WHERE tick_key = ?", (key,)).fetchone()
    assert tuple(row) == (3, 1, 1), "a yes that changes nothing changes nothing"
    assert _summary_criteria_wakes(db) == [], "the give-up stands"

    _commit(db, "s_amend", "vision_keeper",
            Write("items", "bg_1_summary", {"text": "Click echoes json"}))
    assert not _held(db, key), "new words revive the tick"
    assert len(_summary_criteria_wakes(db)) == 1, "the wake is back"


def test_an_approval_change_moves_the_item(db):
    """The reopen predicate reads the item's approval, so a withdrawal is a
    move. An approval written over the same approval, night 91's relay, is
    not (frame 80)."""
    from rota.core.db import Write

    key = "developer|tick:reopen|b1,i1"
    _quarantine(db, key)
    _commit(db, "s_same", "vision_keeper",
            Write("items", "i1", {"approval": "approved", "approval_ver": 1},
                  amends=False))
    assert _held(db, key), "the same approval moves nothing"
    _commit(db, "s_contest", "vision_keeper",
            Write("items", "i1", {"approval": "contested", "approval_ver": 1},
                  amends=False))
    assert not _held(db, key), "a changed approval revives the tick"


def test_a_write_to_c_1_leaves_a_key_on_c_10(db):
    """The pattern `%,c_1%` had no end anchor, so a write to `c_1` revived
    a key whose refs hold `c_10` (frame 80's review, finding 7)."""
    from rota.core.db import Write

    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c_1','t1','old words')")
    for key in ("tester|tick:x|b9,c_10", "tester|tick:x|b9,c_1",
                "tester|tick:x|b9,c_1,g1"):
        _quarantine(db, key)
    _commit(db, "s_c1", "terminologist",
            Write("criteria", "c_1", {"text": "new words"}))
    assert _held(db, "tester|tick:x|b9,c_10"), "another row's key survives"
    assert not _held(db, "tester|tick:x|b9,c_1"), "refs that end in c_1 revive"
    assert not _held(db, "tester|tick:x|b9,c_1,g1"), "refs that hold c_1 revive"


def test_a_status_change_moves_its_subject(db):
    """A ledger entry's status is its state. Before frame 80 any write revived
    a quarantine; the first half kept the status case (frame 80's review)."""
    from rota.core.db import Write

    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "status, author) VALUES ('L1','i1','items','keep invoices',"
               "'open','vision_keeper')")
    key = "liaison|tick:x|L1"
    _quarantine(db, key)
    _commit(db, "s_same", "vision_keeper",
            Write("ledger", "L1", {"status": "open"}, amends=False))
    assert _held(db, key), "the same status moves nothing"
    _commit(db, "s_done", "vision_keeper",
            Write("ledger", "L1", {"status": "resolved"}, amends=False))
    assert not _held(db, key), "a changed status revives the tick"


def test_an_update_on_a_missing_row_revives_nothing(db):
    """An update on a row that is not on file writes nothing. A new row is a
    move only when a row appears (frame 80's review)."""
    from rota.core.db import Write

    key = "liaison|tick:x|L9"
    _quarantine(db, key)
    _commit(db, "s_none", "vision_keeper",
            Write("ledger", "L9", {"status": "resolved"}, op="update",
                  amends=False))
    assert _held(db, key), "no row appeared, so nothing moved"


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


def test_a_reopen_needs_an_amendment_behind_it(db):
    """tipsAT (2026-09-12): the Vision Keeper, woken by a challenge, authored
    a decision that the item was already built and sent reopen for it. The
    Developer was woken to elect on an amendment that never happened. A
    reopen follows a risen version, a fact in the items table."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = build("vision_keeper", db, mode="challenge",
               allow=prompts.mode_tools("vision_keeper", "challenge"))
    with pytest.raises(ValueError, match="nothing to reopen"):
        sb.call("msg.reopen_developer", refs=["i1"])
    _revoke(db)
    sb.call("msg.reopen_developer", refs=["i1"])


def test_a_reopen_names_an_item_not_a_statement(db):
    """clickI night 22 (2026-09-12): reopen sent for a statement id, and the
    Developer was woken to elect on a batch with no amended item under it."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES ('e1','principal',1,'x')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, status) "
               "VALUES ('s2','e1',0,1,'x','ratified')")
    db.commit()
    sb = build("vision_keeper", db, mode="challenge",
               allow=prompts.mode_tools("vision_keeper", "challenge"))
    with pytest.raises(ValueError, match="is not an item"):
        sb.call("msg.reopen_developer", refs=["s2"])
