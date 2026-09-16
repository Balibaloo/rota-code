"""
Track D's push-scoping debt (`COMPLETION.md`): `tickets.scan` and
`criteria.consult` are pushed with no arguments, and "no arguments" meant
"every row" -- fine at four tickets, the glossary incident again at fifty
items. The rule under test is the house rule the survey already lives by:
the subject is the wake's, never the role's. A delivery session reads its
batch; a session woken about an item reads that item; only a wake with no
subject at all still reads the world, because a survey has no item to scope
by and starving it would be a different bug.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.roles.api import (Ctx, criteria_consult, criteria_scan,
                            tickets_consult, tickets_scan)


@pytest.fixture
def world(tmp_path):
    """Two items with a ticket and a criterion each; a batch over the first."""
    conn = init_db(tmp_path / "rota.db")
    for i in ("i1", "i2"):
        conn.execute(
            "INSERT INTO items (id, text, kind, approval, "
            "approval_ver, version) VALUES (?,?,'in_scope',"
            "'approved',1,1)", (i, f"ship {i}"))
    conn.execute("INSERT INTO tickets (id, item_id, text) "
                 "VALUES ('t1','i1','do the first thing')")
    conn.execute("INSERT INTO tickets (id, item_id, text) "
                 "VALUES ('t2','i2','do the other thing')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) "
                 "VALUES ('c1','t1','the first thing works')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) "
                 "VALUES ('c2','t2','the other thing works')")
    conn.execute("INSERT INTO batches (id, item_id, status) "
                 "VALUES ('b1','i1','running')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) "
                 "VALUES ('b1','t1')")
    return conn


def test_a_delivery_session_reads_its_batch_not_the_world(world):
    ctx = Ctx(conn=world, role="developer", batch_id="b1")
    assert [r["id"] for r in tickets_scan(ctx)] == ["t1"]
    assert [r["id"] for r in criteria_consult(ctx)] == ["c1"]


def test_a_session_woken_about_an_item_reads_that_item(world):
    ctx = Ctx(conn=world, role="architect", wake_refs=("i2",))
    assert [r["id"] for r in tickets_scan(ctx)] == ["t2"]
    assert [r["id"] for r in criteria_consult(ctx)] == ["c2"]


def test_a_wake_with_no_subject_still_reads_the_world(world):
    ctx = Ctx(conn=world, role="terminologist")
    assert [r["id"] for r in tickets_scan(ctx)] == ["t1", "t2"]
    assert [r["id"] for r in criteria_consult(ctx)] == ["c1", "c2"]


def test_refs_that_are_not_items_do_not_scope(world):
    # A term_collision wake carries term refs; they name no item and must
    # not shrink the read to nothing.
    ctx = Ctx(conn=world, role="terminologist", wake_refs=("template", "tick"))
    assert [r["id"] for r in tickets_scan(ctx)] == ["t1", "t2"]
    assert [r["id"] for r in criteria_consult(ctx)] == ["c1", "c2"]


def test_an_explicit_item_argument_outranks_the_wake(world):
    # `push_working_set` builds the code.callables hint through
    # `tickets.scan(item_id=...)`; the caller's subject wins over the
    # session's own scope.
    ctx = Ctx(conn=world, role="architect", batch_id="b1")
    assert [r["id"] for r in tickets_scan(ctx, item_id="i2")] == ["t2"]


def test_both_spellings_scope_the_same(world):
    ctx = Ctx(conn=world, role="developer", batch_id="b1")
    assert tickets_consult(ctx) == tickets_scan(ctx)
    assert criteria_scan(ctx) == criteria_consult(ctx)
