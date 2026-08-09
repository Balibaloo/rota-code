"""
The frontier is one definition, and it is ordered.

Two properties, both of which were false until the predicates were declared.

**One definition.** It used to be `open_tips(conn) + predicate_wakes(...)` — the
∪ in "tips ∪ predicates" written literally, which put the frontier in two places
and made the tips half invisible to every check written against the other. The
terminal-state lint could not see that `messages.status = 'open'` had a way out,
because the way out was in a different function.

**Fix before start.** A failed verdict outranks a new batch. Every role is
single-instance, so starting new work is precisely how a fix gets starved.
"""
from __future__ import annotations

import pytest

from rota import predicates as P
from rota.db import init_db
from rota.scheduler import frontier


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


@pytest.fixture
def broken_and_ready(db):
    """
    Something known-wrong, and something ready to start.

    A contested item rather than a failed verdict, because `tick_batch_start`
    refuses outright while any batch is running — a *structural* fix-before-start
    that leaves nothing for the ordering to demonstrate. The contested item is
    the honest case: both predicates genuinely fire, and the order is what
    decides which is offered first.
    """
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('i1','the principal rejected this','in_scope','decided','contested',1,1), "
               "('i2','new work','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t2','i2','build it')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b_new','i2','pending')")
    return db


def test_the_frontier_is_every_predicate(db):
    """
    Not tips plus something else. If this ever splits again, the half that is
    not in the registry stops being checkable by the terminal-state lint.
    """
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m1','t1','liaison','gatekeeper','deliver',1)")

    assert "message_tips" in P.REGISTRY
    assert ("messages", "status", "open") in P.drained_states()
    assert [w.message_id for w in frontier(db)] == ["m1"]


def test_fix_outranks_start(broken_and_ready):
    ready = frontier(broken_and_ready)
    kinds = [w.kind for w in ready]

    assert "tick:contested" in kinds, kinds
    assert "tick:batch_start" in kinds, kinds
    assert kinds.index("tick:contested") < kinds.index("tick:batch_start"), \
        "new work was offered before the principal's rejection was dealt with"


def test_traffic_outranks_everything(broken_and_ready):
    """
    A message is work already in flight with somebody waiting on the other end.
    It goes first — not because it is more important, but because it is already
    started, and the system's whole discipline is finishing before starting.
    """
    broken_and_ready.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
        "VALUES ('m1','t1','liaison','gatekeeper','deliver',1)")

    assert frontier(broken_and_ready)[0].kind == "message"


def test_every_band_has_an_order():
    assert P.check_bands_are_declared() == []


def test_a_wake_target_is_a_role_or_says_why_not():
    """
    `wakes=""` used to mean both "computed per row" and "no role at all", so a
    lint over the field could not tell a typo from a deliberate blank. Now they
    are distinct sentinels and the check covers every predicate rather than
    skipping the empty ones.
    """
    assert P.check_predicates_wake_real_roles() == []
    assert P.REGISTRY["merge"].wakes == P.SCHEDULER
    assert P.REGISTRY["message_tips"].wakes == P.DERIVED


def test_a_typo_in_wakes_is_caught(monkeypatch):
    original = P.REGISTRY["contested"]
    monkeypatch.setitem(P.REGISTRY, "contested",
                        P.Predicate(name="contested", wakes="gatekeper",
                                    drains=original.drains, fn=original.fn))
    assert P.check_predicates_wake_real_roles()


def test_the_agenda_only_fires_when_the_principal_is_there(db):
    """Presenting an agenda to an empty room is not a wake, it is a no-op that
    keeps firing."""
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, author) "
               "VALUES ('l1','i1','items','assumed soft delete','developer')")

    assert not [w for w in frontier(db, principal_present=False)
                if w.kind == "tick:agenda"]
    assert [w for w in frontier(db, principal_present=True)
            if w.kind == "tick:agenda"]


def test_a_broken_predicate_is_not_swallowed(db, monkeypatch):
    """
    `all_wakes` caught sqlite3.Error and carried on, for predicates over tables
    that did not exist yet. They all exist. A predicate silently contributing
    nothing now looks identical to one correctly finding nothing, which is the
    worst possible failure for something the frontier is derived from.
    """
    import sqlite3

    def explode(conn):
        raise sqlite3.OperationalError("no such table: imaginary")

    original = P.REGISTRY["contested"]
    monkeypatch.setitem(P.REGISTRY, "contested",
                        P.Predicate(name="contested", wakes=original.wakes,
                                    drains=original.drains, fn=explode))

    with pytest.raises(sqlite3.OperationalError):
        P.all_wakes(db)
