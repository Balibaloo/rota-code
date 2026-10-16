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
from rota.testkit.fixtures import seed_provenance, seed_ref

PINS = Pins(model="stub", temperature=0.0)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _an_item_with_an_assumption(db):
    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) VALUES ('how_it_works',"
               "'The user types the bill and a tip percentage; the program prints the tip',"
               "'in_scope','draft',0,1)")
    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) VALUES ('t9','unrelated','in_scope',"
               "'draft',0,1)")
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
    seed_ref(db, "items", "how_it_works", "statement", "s1")
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
    # The sign-off page: a present caused by the Vision Keeper's `submit`.
    # Only that page approves an item (frame 190's design, 2.F, amendment 1).
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m8','th','vision_keeper','liaison',"
               "'submit',?,0,'answered')", (json.dumps(refs),))
    db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m9','th','m8','liaison','principal',"
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
    assumption was about when the answer gives no ruling on that row: the owner
    amends it through the contested loop with `principal_said` in front of it.
    An approve of the row in the same answer wins, because no ruling of Roman
    says otherwise (plans/frame225-history-read.md). The ledger id leaves the
    relay's refs; the owner has nothing to apply to it.

    Measured first the other way (2026-09-03): `decisions.author` handed to
    the relay mode drew fourteen decisions a session, five of five, on the
    plain approve case too. The tool in the list was the invitation.
    """
    _an_item_with_an_assumption(db)
    ask = _a_present_of(db, ["how_it_works", "L1"])
    mid = land(db, ask, Answer(verb="verdict",
                               per_item={"L1": "contest"},
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


def test_an_approve_of_the_item_wins_over_a_contest_of_its_default(db):
    """
    Night 146, m190 (2026-10-13): the principal approved line 1 and added a
    detail to the default on line 2. The fold wrote a contest over the
    approve, and on m250 the contested wake s399 cancelled bg_6. The item
    keeps the approve. The words reach its owner as `principal_said` on the
    relay of the approve, and the decision row keeps them
    (plans/frame225-history-read.md).
    """
    from rota.roles.principal import entry_for

    _an_item_with_an_assumption(db)
    ask = _a_present_of(db, ["how_it_works", "L1"])
    said = ("Ok, approved. One thing to add to line 2: the flag should "
            "default to False, so nothing changes for people who already call confirm.")
    mid = land(db, ask, Answer(verb="verdict",
                               per_item={"how_it_works": "approve", "L1": "contest"},
                               text=said))
    db.commit()
    assert verdict_for(db, mid) == {"how_it_works": "approve", "L1": "contest"}
    item = db.execute("SELECT approval, approval_ver, version FROM items "
                      "WHERE id = 'how_it_works'").fetchone()
    assert item["approval"] == "approved"
    assert item["approval_ver"] == item["version"]
    assert db.execute("SELECT status FROM ledger WHERE id = 'L1'"
                      ).fetchone()["status"] == "resolved"
    dec = db.execute("SELECT text, refs FROM decisions WHERE resolves_ledger = 'L1'"
                     ).fetchone()
    assert dec["text"].startswith("overruled at signoff") and "default to False" in dec["text"]
    assert json.loads(dec["refs"]) == ["how_it_works"]
    # The carrier: the verdict stays open with the item in its refs, so the
    # Liaison relays the approve to the item's owner with the words.
    sent = db.execute("SELECT status, body_refs FROM messages WHERE id = ?",
                      (mid,)).fetchone()
    assert sent["status"] == "open"
    assert json.loads(sent["body_refs"]) == ["how_it_works"]
    assert "default to False" in (entry_for(db, mid) or "")


def _a_decided_item_with_a_note(db, kind):
    # Night 144, walk 1, 2026-10-13: page m101 carried echo_json and a
    # Terminologist's scope note about it.
    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) VALUES ('echo_json',"
               "'The program echoes its input as JSON','in_scope','draft',0,1)")
    seed_provenance(db, "items", "echo_json", "decided")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "kind, status, author) VALUES ('L9','echo_json','items',"
               "'The function echo_json already exists as an artefact row.',"
               "?,'open','terminologist')", (kind,))
    db.commit()


def test_a_scope_note_s_contest_stays_on_the_note(db):
    """
    Night 144, walk 1 (2026-10-13): the principal approved echo_json and
    contested a scope note about it. The fold turned the approve into a
    contest. The scheduler then abandoned the batch before a build.
    """
    _a_decided_item_with_a_note(db, "scope")
    ask = _a_present_of(db, ["echo_json", "L9"])
    mid = land(db, ask, Answer(verb="verdict",
                               per_item={"echo_json": "approve", "L9": "contest"},
                               text="the note is wrong"))
    db.commit()
    assert verdict_for(db, mid).get("echo_json") == "approve"
    assert db.execute("SELECT approval FROM items WHERE id = 'echo_json'"
                      ).fetchone()["approval"] != "contested"
    assert db.execute("SELECT status FROM ledger WHERE id = 'L9'"
                      ).fetchone()["status"] == "resolved"
    dec = db.execute("SELECT text FROM decisions WHERE resolves_ledger = 'L9'"
                     ).fetchone()
    assert dec is not None and dec["text"].startswith("overruled at signoff")


def test_a_scope_note_s_contest_on_a_batch_page_leaves_the_approved_item_alone(db):
    """
    The batch filter drops an item's approve before the fold. The review of
    df474208 found that the scope note's contest then contested the item.
    """
    _a_decided_item_with_a_note(db, "scope")
    db.execute("INSERT INTO batches (id, item_id, status) "
               "VALUES ('b1','echo_json','running')")
    db.commit()
    ask = _a_present_of(db, ["b1", "echo_json", "L9"])
    mid = land(db, ask, Answer(verb="verdict",
                               per_item={"echo_json": "approve", "L9": "contest"},
                               text="the note is wrong"))
    db.commit()
    assert verdict_for(db, mid).get("echo_json") != "contest"
    assert db.execute("SELECT approval FROM items WHERE id = 'echo_json'"
                      ).fetchone()["approval"] != "contested"


def test_a_default_s_contest_reaches_its_item_the_ruling_does_not_name(db):
    """A contested default with no ruling on its item contests the item (the
    build session's carrier of 2026-09-04, kept by frame 225's pass 2)."""
    _a_decided_item_with_a_note(db, "default")
    ask = _a_present_of(db, ["echo_json", "L9"])
    mid = land(db, ask, Answer(verb="verdict", per_item={"L9": "contest"},
                               text="the note is wrong"))
    db.commit()
    assert verdict_for(db, mid).get("echo_json") == "contest"


def test_a_conflict_note_s_contest_reaches_an_item_the_ruling_does_not_name(db):
    """The test is green on the parent of fca24dbc and red on fca24dbc."""
    _a_decided_item_with_a_note(db, "conflict")
    ask = _a_present_of(db, ["echo_json", "L9"])
    mid = land(db, ask, Answer(verb="verdict", per_item={"L9": "contest"},
                               text="the note is wrong"))
    db.commit()
    assert verdict_for(db, mid).get("echo_json") == "contest"
    assert db.execute("SELECT approval FROM items WHERE id = 'echo_json'"
                      ).fetchone()["approval"] == "contested"


def test_a_conflict_note_s_contest_never_overwrites_the_principal_s_approve_of_its_item(db):
    """The principal's own ruling on the item wins over the note's contest."""
    _a_decided_item_with_a_note(db, "conflict")
    ask = _a_present_of(db, ["echo_json", "L9"])
    mid = land(db, ask, Answer(verb="verdict",
                               per_item={"echo_json": "approve", "L9": "contest"},
                               text="the note is wrong"))
    db.commit()
    assert verdict_for(db, mid).get("echo_json") == "approve"


def _two_requests(db):
    # Night 152's rows at m59: the echo_json request e_p1, merged as bg_1,
    # and the confirm request e_p2, with the account citing both.
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e_p1','principal',8,'Add an echo_json(obj) helper next to echo')")
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e_p2','principal',16,'Let confirm() take a default_on_eof flag')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, status) "
               "VALUES ('s1','e_p1',0,41,'Add an echo_json(obj) helper next to echo','ratified')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, status) "
               "VALUES ('s2','e_p2',0,40,'Let confirm() take a default_on_eof flag','ratified')")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('echo_json','Add an echo_json(obj) helper next to echo',"
               "'in_scope','approved',1,1)")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('confirm_default_on_eof','Let confirm() take a new "
               "default_on_eof flag that is off by default','in_scope','draft',0,1)")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version, "
               "is_description) VALUES ('how_it_works','The program is a "
               "command-line interface toolkit called Click','in_scope','draft',0,1,1)")
    seed_ref(db, "items", "echo_json", "statement", "s1")
    seed_ref(db, "items", "confirm_default_on_eof", "statement", "s2")
    seed_ref(db, "items", "how_it_works", "statement", "s1")
    seed_ref(db, "items", "how_it_works", "statement", "s2")
    seed_provenance(db, "items", "echo_json", "decided")
    seed_provenance(db, "items", "confirm_default_on_eof", "decided")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) "
               "VALUES ('bg_1','echo_json','merged','0d65f7b9')")
    db.commit()


def test_a_note_s_contest_never_reaches_an_item_of_another_request(db):
    """
    Night 152, m59 and m60 (2026-10-16): the confirm page carried a
    Developer note about the merged echo_json, and he faulted it as "my
    first change, not this one". The carrier contested echo_json, and three
    asks followed. The contest stays on the note, which relays to the
    Developer (frame 274, `plans/frame274-count.md`).
    """
    _two_requests(db)
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "kind, status, author) VALUES ('l_a5ef6d4cd8','echo_json','items',"
               "'Placing echo_json immediately after echo keeps it in the same module.',"
               "'default','open','developer')")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "kind, status, author) VALUES ('l_c4271ef944','confirm_default_on_eof',"
               "'items','The confirm() function will now take a default_on_eof flag.',"
               "'default','open','vision_keeper')")
    db.commit()
    ask = _a_present_of(db, ["confirm_default_on_eof", "how_it_works",
                             "l_a5ef6d4cd8", "l_c4271ef944"])
    said = ("Line 3 is wrong: echo_json is my first change, not this one, and lines "
            "4, 6 and 8 have the same problem. This page should only cover the "
            "confirm flag. Line 7 also needs to say the flag is off by default, so "
            "existing callers see no change.")
    mid = land(db, ask, Answer(verb="verdict", text=said, per_item={
        "confirm_default_on_eof": "revise", "how_it_works": "approve",
        "l_a5ef6d4cd8": "contest", "l_c4271ef944": "contest"}))
    db.commit()
    assert db.execute("SELECT approval FROM items WHERE id = 'echo_json'"
                      ).fetchone()["approval"] == "approved"
    sent = db.execute("SELECT status, body_refs FROM messages WHERE id = ?",
                      (mid,)).fetchone()
    assert "echo_json" not in json.loads(sent["body_refs"]), sent["body_refs"]
    assert "echo_json" not in verdict_for(db, mid)
    assert db.execute("SELECT status FROM ledger WHERE id = 'l_a5ef6d4cd8'"
                      ).fetchone()["status"] == "resolved"
    dec = db.execute("SELECT text FROM decisions WHERE resolves_ledger = 'l_a5ef6d4cd8'"
                     ).fetchone()
    assert dec is not None and dec["text"].startswith("overruled at signoff")
    # The relay: the verdict stays open and carries the note's contest to
    # the note's owner.
    assert sent["status"] == "open"
    assert verdict_for(db, mid).get("l_a5ef6d4cd8") == "contest"
    assert _owner_of_ref(db, "l_a5ef6d4cd8") == "developer"
    assert db.execute("SELECT approval FROM items WHERE id = 'confirm_default_on_eof'"
                      ).fetchone()["approval"] == "contested"


def test_a_note_s_contest_reaches_the_page_s_own_request_item(db):
    """Night 136, m165 (2026-10-11): a note about the confirm item on the
    confirm page, and he faulted it. The item goes contested. A challenge
    of the other request's item names it as `items:echo_json`."""
    _two_requests(db)
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "kind, status, author) VALUES ('challenge_items_echo_json',"
               "'items:echo_json','items','echo_json is out of this page',"
               "'default','open','critic')")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "kind, status, author) VALUES ('l_fbbef84c1e','confirm_default_on_eof',"
               "'items','confirm() takes a default_on_eof flag','default','open',"
               "'vision_keeper')")
    db.commit()
    ask = _a_present_of(db, ["challenge_items_echo_json", "l_fbbef84c1e"])
    mid = land(db, ask, Answer(verb="verdict", per_item={
        "challenge_items_echo_json": "contest", "l_fbbef84c1e": "contest"},
        text="I also contest line six because it leaves out that the new "
             "flag is off by default."))
    db.commit()
    assert verdict_for(db, mid).get("confirm_default_on_eof") == "contest"
    assert db.execute("SELECT approval FROM items WHERE id = 'confirm_default_on_eof'"
                      ).fetchone()["approval"] == "contested"
    assert db.execute("SELECT approval FROM items WHERE id = 'echo_json'"
                      ).fetchone()["approval"] == "approved"


def test_a_note_s_contest_reaches_a_description_on_a_page_with_no_request(db):
    """Night 143, m11 (2026-10-13): the account page, with conflict notes
    about descriptions. The page has no request, so the carrier stays."""
    for item in ("how_it_works", "defines_commands_and_options"):
        db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                   "version, is_description) VALUES (?, 'Click is a toolkit',"
                   "'in_scope','draft',0,1,1)", (item,))
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "kind, status, author) VALUES ('l_21cb695fbf',"
               "'defines_commands_and_options','items','the README description',"
               "'conflict','open','vision_keeper')")
    db.commit()
    ask = _a_present_of(db, ["l_21cb695fbf", "how_it_works"])
    mid = land(db, ask, Answer(verb="verdict", per_item={
        "how_it_works": "approve", "l_21cb695fbf": "contest"},
        text="Lines 2 to 8 are wrong. Line 1 is fine."))
    db.commit()
    assert verdict_for(db, mid).get("defines_commands_and_options") == "contest"
    assert db.execute("SELECT approval FROM items WHERE id = "
                      "'defines_commands_and_options'").fetchone()["approval"] == "contested"


def test_the_signoff_page_names_the_code_that_carries_each_items_words(db):
    """P4 piece 2 in its mechanical form (2026-09-12): beside each item, the
    files whose symbols carry a word of the item's text, read from the
    index and labelled as that. Not a prediction; the touch note is."""
    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) VALUES ('i1',"
               "'users can export their invoices as CSV','in_scope','draft',0,1)")
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

    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) VALUES ('i1','ship it','in_scope','draft',0,1)")
    for n in range(9):
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
                   "status, author) VALUES (?, 'i1', 'items', ?, 'open', 'vision_keeper')",
                   (f"L{n}", f"assumption {n}"))
    db.commit()
    sb = build("liaison", db, mode="submit", allow=prompts.mode_tools("liaison", "submit"))
    with pytest.raises(ValueError, match="at most 7 open assumptions"):
        sb.call("msg.present_principal", refs=["i1"] + [f"L{n}" for n in range(9)])
    sb.call("msg.present_principal", refs=["i1"] + [f"L{n}" for n in range(7)])


def test_observed_behaviour_is_not_shown_as_a_plan(db):
    """seat1 (2026-09-12): the signoff page put the account's observed
    behaviours under "It would:", and the person at the seat read "calculate
    the tip" as new work. Provenance is the fact; the heading follows it."""
    from rota.roles.principal import render_ask

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('seen', 'the program calculates the tip', 'in_scope', "
               "'approved', 1, 1)")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('new', 'the program splits the bill', 'in_scope', "
               "'draft', 0, 1)")
    seed_provenance(db, "items", "seen", "observed")
    seed_provenance(db, "items", "new", "decided")
    db.commit()
    page = render_ask(db, "present", ["seen", "new"])
    # The request comes first, under "You asked:" (frame 190's design, 2.1).
    assert "You asked:" in page and "It does today:" in page
    assert page.index("You asked:") < page.index("the program splits the bill") \
        < page.index("It does today:") < page.index("the program calculates the tip")


def test_a_description_has_its_own_heading(db):
    """clickI night 91 (2026-09-24): the seat's summary said Click "includes
    a helper function echo_json", which was the running request. A seat's
    description is neither a plan nor what the code does today (frame 80)."""
    from rota.core.runner import _resolve_refs
    from rota.roles.principal import render_ask

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version, is_description) VALUES ('bg_1_summary', 'Click is a "
               "toolkit that includes echo_json', 'in_scope', 'draft', 1, 1, 1)")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('new', 'the program splits the bill', 'in_scope', "
               "'draft', 0, 1)")
    seed_provenance(db, "items", "new", "decided")
    db.commit()
    assert _resolve_refs(db, ["bg_1_summary"])["bg_1_summary"]["is_description"] == 1
    assert "is_description" not in _resolve_refs(db, ["new"])["new"], \
        "a request's row keeps the text the recordings hash"
    page = render_ask(db, "present", ["bg_1_summary", "new"])
    # The request first, and a description is never a request line (frame
    # 190's design, 2.F, amendment 5).
    heading = page.index("How it is described:")
    assert page.index("You asked:") < page.index("the program splits the bill") \
        < heading < page.index("includes echo_json")
    assert page.count("includes echo_json") == 1
    assert "It does today:" not in page


def test_the_signoff_hook_adds_at_most_seven_assumptions(db):
    """seat2 on click (2026-09-12): the hook put nineteen reconcile rows under
    one signoff page, past the seven-a-page door the model is held to. The
    hook obeys the same rule; the rest wait for the next page."""
    _an_item_with_an_assumption(db)
    for n in range(10):
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
                   "status, author) VALUES (?, 'how_it_works', 'items', ?, 'open', 'vision_keeper')",
                   (f"LX{n:02d}", f"assumption {n}"))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m8','th','vision_keeper',"
               "'liaison','submit',?,1,'open')", (json.dumps(["how_it_works"]),))
    db.commit()
    out = run_session(
        db, Wake("liaison", "message", message_id="m8", detail="submit"),
        backend=ScriptedBackend(["TOOL: msg.present_principal(refs=['how_it_works'])", "done"]),
        pins=PINS, instructions="present it")
    assert out.committed, out.errors
    refs = json.loads(db.execute("SELECT body_refs FROM messages WHERE verb = 'present'").fetchone()["body_refs"])
    open_rows = [r for r in refs if db.execute("SELECT 1 FROM ledger WHERE id = ? AND status = 'open'", (r,)).fetchone()]
    assert len(open_rows) == 7, refs
