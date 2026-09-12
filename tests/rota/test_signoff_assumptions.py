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
    assert "Where you did not say, I assumed:" in asks[0].rendered, asks[0].rendered
    assert "the percentage is typed each time" in asks[0].rendered


def test_the_other_desks_assumptions_about_the_words_ride_the_page(db):
    """
    Level 2 (2026-09-09): the Terminologist and the Architect log against
    the ratified statement, the lineage's root. Once items cover it the
    statement is not on the page, so its rows ride by lineage: the word
    taken one way and the shape assumed reach the principal before slicing.
    """
    _an_item_with_an_assumption(db)
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e1','principal',1,'archive the invoices older than a year')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, status) "
               "VALUES ('s1','e1',0,39,'archive the invoices older than a year','ratified')")
    db.execute("INSERT INTO item_statements (item_id, statement_id) VALUES ('how_it_works','s1')")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, author) "
               "VALUES ('L4','s1','statements','archive: took move to cold storage; if it "
               "means delete, the invoices are gone','open','terminologist')")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, author) "
               "VALUES ('L5','s1','statements','settled','resolved','architect')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m8','th','vision_keeper',"
               "'liaison','submit',?,1,'open')", (json.dumps(["how_it_works"]),))
    db.commit()
    out = run_session(
        db, Wake("liaison", "message", message_id="m8", detail="submit"),
        backend=ScriptedBackend(["TOOL: msg.present_principal(refs=['how_it_works'])", "done"]),
        pins=PINS, instructions="present it")
    assert out.committed, out.errors
    refs = json.loads(db.execute("SELECT body_refs FROM messages WHERE verb='present'").fetchone()["body_refs"])
    assert "L4" in refs and "L5" not in refs, refs
    assert "archive: took move to cold storage" in render_refs(db, refs)
    assert _owner_of_ref(db, "L4") == "terminologist"


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
    # The item ruling lands at the keypress too. The owner used to apply it
    # and dropped rows (tips7, tips8, 2026-09-04): the account stayed draft
    # and the same page came back without end.
    item = db.execute("SELECT approval, approval_ver, version FROM items "
                      "WHERE id = 'how_it_works'").fetchone()
    assert item["approval"] == "approved"
    assert item["approval_ver"] == item["version"]
    # The closed row is a decision now, and it leaves the recorded ruling as
    # it leaves the refs: relayed, the owner acted on a done row (tipsQ,
    # 2026-09-09: 36 rounds).
    assert verdict_for(db, mid) == {"how_it_works": "approve"}, (
        "the ruling still to relay is recorded; the closed row is a decision")


def test_a_page_of_only_assumptions_lands_answered(db):
    """
    tipsQ, 2026-09-09: the agenda presented one ledger row, the principal
    approved, the verdict woke the Liaison, the Liaison relayed it to the
    row's author, the author adopted the ledger id, was refused, logged the
    refusal as a new assumption, and the agenda presented that. 36 rounds.
    A page whose every row closed at the keypress leaves nothing to relay.
    """
    _an_item_with_an_assumption(db)
    ask = _a_present_of(db, ["L1"])
    mid = land(db, ask, Answer(verb="verdict", per_item={"L1": "approve"}))
    db.commit()
    sent = db.execute("SELECT status, body_refs FROM messages WHERE id = ?", (mid,)).fetchone()
    assert sent["status"] == "answered", "nothing remains for an owner"
    assert json.loads(sent["body_refs"]) == []
    assert verdict_for(db, mid) == {}
    assert db.execute("SELECT status FROM ledger WHERE id = 'L1'").fetchone()["status"] == "resolved"


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
    assert db.execute("SELECT approval FROM items WHERE id = 'how_it_works'"
                      ).fetchone()["approval"] == "contested", (
        "the contest lands on the row at the keypress, so the contested tick fires")
    assert _owner_of_ref(db, "L1") == "vision_keeper"


def test_the_signoff_page_names_the_code_that_carries_each_items_words(db):
    """P4 piece 2 in its mechanical form (2026-09-12): beside each item, the
    files whose symbols carry a word of the item's text, read from the
    index and labelled as that. Not a prediction; the touch note is."""
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('i1',"
               "'users can export their invoices as CSV','in_scope','decided','draft',0,1)")
    for grain in ("src/billing/invoice.py::Invoice", "src/billing/export.py::export_csv",
                  "src/billing/export.py::ExportError", "src/auth/login.py::login"):
        db.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, 'symbol')", (grain,))
    db.commit()
    from rota.roles.principal import render_ask
    page = render_ask(db, "present", ["i1"])
    assert "1. users can export their invoices as CSV" in page
    assert "code that names these words: src/billing/export.py, src/billing/invoice.py" in page
    assert "login" not in page


def test_a_page_carries_at_most_seven_open_assumptions(db):
    """clickI night 17 (2026-09-12): 27 assumptions on one page. The
    interview is iterative by ruling; the count is the door's, the choice
    of seven is the brief's. The rest stay open for the next page."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('i1','ship it','in_scope','decided','draft',0,1)")
    for n in range(9):
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
                   "status, author) VALUES (?, 'i1', 'items', ?, 'open', 'vision_keeper')",
                   (f"L{n}", f"assumption {n}"))
    db.commit()
    sb = build("liaison", db, mode="submit", allow=prompts.mode_tools("liaison", "submit"))
    with pytest.raises(ValueError, match="at most 7 open assumptions"):
        sb.call("msg.present_principal", refs=["i1"] + [f"L{n}" for n in range(9)])
    sb.call("msg.present_principal", refs=["i1"] + [f"L{n}" for n in range(7)])
