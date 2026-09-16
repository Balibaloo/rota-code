"""
Chaos, loop 3: the confirm loop, hurt the ways operations would hurt it.

`LOOPS.md` names three injuries for this loop: two principals ruling at once;
a verdict for a present that was re-presented meanwhile; and the owner's
adopt session killed after the relay. The third is here first, and it is also
the chaos form of the relay's cause-hop: the owner is woken by Liaison's
relay, the ruling lives one hop back on the principal's own message, and a
death after the relay must leave the ruling where it was -- on file,
undelivered, and offered again -- never half-applied and never lost. The
2026-09-03 tips run showed the ruling failing to arrive at all; this holds
that once it arrives, a death cannot make it arrive twice or by halves.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.runner import resolve_inbound, run_session
from rota.core.scheduler import frontier_readonly
from rota.llm.llm import Pins, ScriptedBackend

PINS = Pins(model="stub", temperature=0.0)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


class DiesAfterStaging:
    """Answers once with a real write staged, then dies the way a network does."""

    name = "chaos"

    def __init__(self, first: str):
        self.first = first
        self.calls = 0

    def complete(self, system, user, pins):
        self.calls += 1
        if self.calls == 1:
            from rota.llm.llm import Completion

            return Completion(text=self.first)
        raise ConnectionError("the model went away after the relay")


def _a_relayed_ruling(db):
    """A present, the principal's approval of it, and Liaison's relay to the owner."""
    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) VALUES ('t1',"
               "'users can close their account','in_scope','draft',0,1)")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m9','th','liaison','principal',"
               "'present',?,1,'answered')", (json.dumps(["t1"]),))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES ('m10','m9','th','principal',"
               "'liaison','verdict',?,2,'answered')", (json.dumps(["t1"]),))
    db.execute("INSERT INTO config (key, value) VALUES ('verdict:m10', ?)",
               (json.dumps({"t1": "approve"}),))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES ('m11','m10','th','liaison',"
               "'vision_keeper','relay',?,3,'open')", (json.dumps(["t1"]),))
    db.commit()


def test_the_adopt_session_killed_after_the_relay_never_happened(db):
    """
    The relay is sent, the owner wakes, stages the approval the ruling asks
    for, and dies before it can commit. The world must be the one from before:
    the item still draft, the relay still open with the death counted, the
    ruling still on file one hop back, and the same wake back on the frontier.
    Then the retry lands it, once.
    """
    _a_relayed_ruling(db)
    wake = Wake("vision_keeper", "message", message_id="m11", detail="relay")
    assert resolve_inbound(db, wake)["principal_verdict"] == {"t1": "approve"}, (
        "the ruling reaches the owner through the relay's cause")
    before = [str(w) for w in frontier_readonly(db)]

    out = run_session(
        db, wake,
        backend=DiesAfterStaging(
            "TOOL: problem.set_approval(id='t1', approval='approved')"),
        pins=PINS, instructions="apply the ruling")

    assert not out.committed
    assert db.execute("SELECT approval FROM items WHERE id='t1'"
                      ).fetchone()["approval"] == "draft", "not half-applied"
    row = db.execute("SELECT status, attempts FROM messages WHERE id='m11'"
                     ).fetchone()
    assert row["status"] == "open", "the relay survives the death"
    assert row["attempts"] == 1, "and the death was counted"
    assert db.execute("SELECT 1 FROM config WHERE key='verdict:m10'"
                      ).fetchone(), "the ruling is still on file"
    assert [str(w) for w in frontier_readonly(db)] == before, (
        "the frontier re-derives the same world")

    # The retry: woken again by the same relay, the owner is handed the same
    # ruling and lands it.
    assert resolve_inbound(db, wake)["principal_verdict"] == {"t1": "approve"}
    again = run_session(
        db, wake,
        backend=ScriptedBackend(
            ["TOOL: problem.set_approval(id='t1', approval='approved')", "done"]),
        pins=PINS, instructions="apply the ruling")
    assert again.committed
    assert db.execute("SELECT approval, approval_ver FROM items WHERE id='t1'"
                      ).fetchone()["approval"] == "approved"


def _an_open_present(db):
    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) VALUES ('t1',"
               "'users can close their account','in_scope','draft',0,1)")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m9','th','liaison','principal',"
               "'present',?,1,'open')", (json.dumps(["t1"]),))
    db.commit()


def test_two_principals_ruling_at_once_land_one_ruling(db, tmp_path):
    """
    Two consoles on one checkout both read the present open and both answer
    it. The first to land wins; the second is refused at the door, not
    stacked -- two rulings on one present would relay two rulings to the
    owner, and which one it applied would be decided by arrival order.
    """
    from rota.core.db import connect
    from rota.roles.principal import Answer, land, pending_asks, verdict_for

    _an_open_present(db)
    a = connect(tmp_path / "rota.db")
    b = connect(tmp_path / "rota.db")
    ask_a = pending_asks(a)[0]
    ask_b = pending_asks(b)[0]
    assert ask_a.message_id == ask_b.message_id == "m9", "both read it open"

    first = land(a, ask_a, Answer(verb="verdict", per_item={"t1": "approve"}))
    a.commit()
    second = land(b, ask_b, Answer(verb="verdict", per_item={"t1": "contest"}))
    b.commit()

    assert first, "the first ruling lands"
    assert second is None, "the second is refused, not stacked"
    assert verdict_for(a, first) == {"t1": "approve"}
    assert a.execute("SELECT COUNT(*) n FROM messages WHERE verb = 'verdict'"
                     ).fetchone()["n"] == 1
    assert a.execute("SELECT COUNT(*) n FROM config WHERE key LIKE 'verdict:%'"
                     ).fetchone()["n"] == 1
    assert pending_asks(a) == [], "nothing is left to answer"


@pytest.mark.xfail(strict=True, reason=(
    "owed on a vocabulary decision: retiring a superseded present needs a "
    "message status the CHECK at schema.sql:482 does not have -- "
    "open|answered|unresolved|quarantined. The door mechanic is written and "
    "held back (plans/superseded-present.md); COMPLETION.md, questions for the "
    "seat"))
def test_a_verdict_for_a_present_re_presented_meanwhile_lands_nothing(db):
    """
    The principal's screen shows a present of the item at version one. The
    world moves: the item is amended and Liaison presents it again. What must
    hold: the first present is retired -- not open, because it must not be put
    to them again and an open ask silences the agenda and the baseline offer;
    not answered, because an answered present with no verdict is a deferral.
    Only the latest present is put to the principal, and a ruling for the
    first from a screen that never refreshed lands nothing, because it would
    approve a version of the item the principal never saw.

    Reproduced as it stands (2026-09-03): the first present stays open, both
    are put to the principal, and the stale ruling lands and approves version
    two. Strict, so the day the retired state exists this fails loudly and
    the mark comes off.
    """
    from rota.roles.principal import Answer, Ask, land, pending_asks, verdict_for

    _an_open_present(db)
    # Meanwhile: the item is amended, and Vision Keeper submits it again.
    db.execute("UPDATE items SET text = 'users can close, not delete, their "
               "account', version = 2 WHERE id = 't1'")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m8','th','vision_keeper',"
               "'liaison','submit',?,2,'open')", (json.dumps(["t1"]),))
    db.commit()
    out = run_session(
        db, Wake("liaison", "message", message_id="m8", detail="submit"),
        backend=ScriptedBackend(["TOOL: msg.present_principal(refs=['t1'])",
                                 "done"]),
        pins=PINS, instructions="present it")
    assert out.committed
    new = db.execute("SELECT id FROM messages WHERE verb = 'present' AND id != 'm9'"
                     ).fetchone()
    assert new, "Liaison presented the amended item"

    # Retired, by whatever name the seat gives the state.
    old = db.execute("SELECT status FROM messages WHERE id = 'm9'"
                     ).fetchone()["status"]
    assert old not in ("open", "answered"), (
        "the first present is retired: not open, not a deferral")
    assert [x.message_id for x in pending_asks(db)] == [new["id"]], (
        "only the latest present of the item is put to the principal")

    stale = Ask(message_id="m9", verb="present", refs=["t1"])
    assert land(db, stale, Answer(verb="verdict", per_item={"t1": "approve"})) is None
    assert db.execute("SELECT approval FROM items WHERE id = 't1'"
                      ).fetchone()["approval"] == "draft"
    assert db.execute("SELECT COUNT(*) n FROM messages WHERE verb = 'verdict'"
                      ).fetchone()["n"] == 0

    # The ruling on the latest present is the ruling.
    mid = land(db, pending_asks(db)[0],
               Answer(verb="verdict", per_item={"t1": "approve"}))
    db.commit()
    assert mid and verdict_for(db, mid) == {"t1": "approve"}
    assert db.execute("SELECT status FROM messages WHERE id = ?", (new["id"],)
                      ).fetchone()["status"] == "answered"
