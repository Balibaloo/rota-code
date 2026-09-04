"""
A1 at intent-time: the signoff page carries the lineage's open assumptions.

Law 8 said it from the start -- "a lineage's open assumptions are presented at
its gates: nothing ships whose assumptions the principal never saw" -- and no
ledger row had ever reached the page: the present did not carry them and
`render_refs` could not read one out. Ruled 2026-09-03 (A1, "a usability
priority"): the signoff page is the seed interview's first moment. What is
pinned here is the mechanics under the ruling loop the principal already has:
the assumption rides on the present beside the row it is about; approving it
takes the default at the keypress, as a decision under the principal's name
that resolves the entry; contesting it goes back to the desk that assumed it.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.runner import run_session
from rota.core.sandbox import _owner_of_ref
from rota.llm.llm import Pins, ScriptedBackend
from rota.roles.principal import Answer, Ask, land, pending_asks, render_refs, verdict_for

PINS = Pins(model="stub", temperature=0.0)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _an_item_with_an_assumption(db):
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('how_it_works',"
               "'The user types the bill and a tip percentage; the program prints the tip',"
               "'in_scope','decided','draft',0,1)")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('t9','unrelated','in_scope',"
               "'decided','draft',0,1)")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "status, author) VALUES ('L1','how_it_works','items',"
               "'the percentage is typed each time, not a fixed tier',"
               "'open','vision_keeper')")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "status, author) VALUES ('L2','t9','items','something about t9',"
               "'open','vision_keeper')")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "status, author) VALUES ('L3','how_it_works','items',"
               "'already settled','resolved','vision_keeper')")
    db.commit()


def test_the_present_carries_the_lineage_s_open_assumptions(db):
    """
    Vision Keeper submits the account; Liaison presents it. The open ledger row
    about the account rides on the present, added never substituted; the row
    about another item does not, nor does the resolved one. And the principal
    reads it as words: "assumed: ...".
    """
    _an_item_with_an_assumption(db)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m8','th','vision_keeper',"
               "'liaison','submit',?,1,'open')", (json.dumps(["how_it_works"]),))
    db.commit()

    out = run_session(
        db, Wake("liaison", "message", message_id="m8", detail="submit"),
        backend=ScriptedBackend(["TOOL: msg.present_principal(refs=['how_it_works'])",
                                 "done"]),
        pins=PINS, instructions="present it")
    assert out.committed, out.errors
    present = db.execute("SELECT id, body_refs FROM messages WHERE verb = 'present'"
                         ).fetchone()
    refs = json.loads(present["body_refs"])
    assert "L1" in refs, refs
    assert "L2" not in refs and "L3" not in refs, refs
    assert refs.index("how_it_works") < refs.index("L1"), "the row, then what was assumed about it"

    shown = render_refs(db, refs)
    assert "assumed: the percentage is typed each time" in shown, shown
    asks = pending_asks(db)
    assert asks and asks[0].message_id == present["id"]
    assert "assumed:" in asks[0].rendered


def test_an_assumption_s_owner_is_its_author(db):
    _an_item_with_an_assumption(db)
    assert _owner_of_ref(db, "L1") == "vision_keeper"
    assert _owner_of_ref(db, "how_it_works") == "vision_keeper"
    assert _owner_of_ref(db, "nope") is None


def _a_present_of(db, refs):
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m9','th','liaison','principal',"
               "'present',?,1,'open')", (json.dumps(refs),))
    db.commit()
    return pending_asks(db)[0]


def test_approving_an_assumption_takes_the_default_at_the_keypress(db):
    """
    Approve is the keypress that lets a decided row into the record: a decision
    under the principal's name that resolves the ledger entry, the two writes
    `decisions.author` makes. The taken default leaves the relay's refs -- the
    owner has nothing to apply -- while the item ruling travels as before.
    """
    _an_item_with_an_assumption(db)
    ask = _a_present_of(db, ["how_it_works", "L1"])
    mid = land(db, ask, Answer(verb="verdict",
                               per_item={"how_it_works": "approve", "L1": "approve"}))
    db.commit()
    assert mid

    row = db.execute("SELECT status FROM ledger WHERE id = 'L1'").fetchone()
    assert row["status"] == "resolved"
    dec = db.execute("SELECT author, text, refs, resolves_ledger FROM decisions "
                     "WHERE resolves_ledger = 'L1'").fetchone()
    assert dec and dec["author"] == "principal"
    assert "typed each time" in dec["text"]
    assert json.loads(dec["refs"]) == ["how_it_works"]

    sent = db.execute("SELECT body_refs FROM messages WHERE id = ?", (mid,)).fetchone()
    assert json.loads(sent["body_refs"]) == ["how_it_works"], "the taken default is not relayed"
    assert verdict_for(db, mid) == {"how_it_works": "approve", "L1": "approve"}, (
        "the ruling itself is recorded whole")


def test_contesting_an_assumption_overrules_it_and_contests_its_row(db):
    """
    Contest with words closes the entry at the keypress too -- a decision under
    the principal's name carrying the words -- and contests the row the
    assumption was about, even where the principal approved that row in the
    same breath: they rejected the reading, so the owner amends it through the
    contested loop with `principal_said` in front of it. The ledger id leaves
    the relay's refs; the owner has nothing to apply to it.

    Measured first the other way (2026-09-03): `decisions.author` handed to
    the relay mode drew fourteen decisions a session, five of five, on the
    plain approve case too. The tool in the list was the invitation.
    """
    _an_item_with_an_assumption(db)
    ask = _a_present_of(db, ["how_it_works", "L1"])
    mid = land(db, ask, Answer(verb="verdict",
                               per_item={"how_it_works": "approve", "L1": "contest"},
                               text="no, a fixed 15 percent, always"))
    db.commit()
    assert mid
    assert db.execute("SELECT status FROM ledger WHERE id = 'L1'").fetchone()["status"] == "resolved"
    dec = db.execute("SELECT author, text, resolves_ledger FROM decisions").fetchall()
    assert len(dec) == 1 and dec[0]["author"] == "principal"
    assert dec[0]["resolves_ledger"] == "L1"
    assert "fixed 15 percent" in dec[0]["text"] and "typed each time" in dec[0]["text"]
    assert json.loads(db.execute("SELECT body_refs FROM messages WHERE id = ?",
                                 (mid,)).fetchone()["body_refs"]) == ["how_it_works"]
    assert verdict_for(db, mid) == {"how_it_works": "contest", "L1": "contest"}, (
        "contesting what was assumed about a row contests the row")
    assert _owner_of_ref(db, "L1") == "vision_keeper"
