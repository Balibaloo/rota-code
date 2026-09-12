"""
P4, piece 1: a batch's predicted touch is put to the principal before it builds.

Ruled 2026-09-03 (R16/R17): what the seat needs before work proceeds is the
modification scope -- the paths the Architect expects, the symbols it only
guesses, the touched ground nobody surveyed, the commitments bound to it --
never time or effort. Non-blocking by R7: the note is a sense check, nothing
waits on the answer, and the steering loop is the lever if the scope smells
wrong.

Everything here is machine. The note is owed until presented and once only
(register-shaped, derived from the presents themselves); the set is computed
by mechanics and rendered as words at the edge, where ids stop working; the
gates that wait on a ruling set the note aside; and the door treats an
approval as an acknowledgement that wakes nobody, while a contest on the item
lands as any ruling does.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.lifecycle import touch_notes, touch_set
from rota.core.predicates import observed_entries, touch_note
from rota.core.runner import run_session
from rota.core.scheduler import frontier_readonly, tick_agenda, tick_signoff
from rota.llm.llm import Pins, ScriptedBackend
from rota.roles.principal import Answer, Ask, land, render_refs, touch_words


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _world(db, status: str = "pending") -> None:
    """One approved item, its batch, three predicted grains, a commitment on
    one of them, and constraint zero over the area of another."""
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('i1', "
               "'users can export their invoices', 'in_scope', 'decided', "
               "'approved', 1, 1)")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1',?)",
               (status,))
    for grain, kind, confidence in (
            ("src/invoices/export.py", "path", "expected"),
            ("src/store/db.py", "path", "expected"),
            ("render_invoice", "symbol", "possible")):
        db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, "
                   "confidence) VALUES ('b1', ?, ?, ?)", (grain, kind, confidence))
    db.execute("INSERT INTO constraints (id, headline, text, provenance) VALUES "
               "('k1', 'the store layer is synchronous', "
               "'every call into src/store blocks', 'decided')")
    db.execute("INSERT INTO constraint_bindings (constraint_id, grain, grain_kind) "
               "VALUES ('k1', 'src/store', 'path')")
    db.execute("INSERT INTO constraints (id, headline, provenance) VALUES "
               "('k0', 'this area has not been surveyed', 'decided')")
    db.execute("INSERT INTO constraint_bindings (constraint_id, grain, grain_kind) "
               "VALUES ('k0', 'src/invoices', 'path')")
    db.commit()


_SEQ = [100]


def _present(db, mid: str, refs: list[str], status: str = "open") -> None:
    _SEQ[0] += 1
    db.execute("INSERT INTO messages (id, cause_kind, thread_id, from_role, "
               "to_role, verb, body_refs, seq, status) VALUES (?, 'tick', 't1', "
               "'liaison', 'principal', 'present', ?, ?, ?)",
               (mid, json.dumps(refs), _SEQ[0], status))
    db.commit()


def test_the_note_is_owed_once_and_carries_the_batch_and_its_item(db):
    """The predicate names the batch and its item; the present carries both
    whatever the session typed; and a batch is put to them once."""
    _world(db)
    wakes = touch_note(db)
    assert [(w.role, w.kind, w.refs) for w in wakes] == [
        ("liaison", "tick:touch_note", ("b1", "i1"))]
    assert "expected 2" in wakes[0].detail and "possible 1" in wakes[0].detail

    out = run_session(
        db, wakes[0],
        backend=ScriptedBackend(["TOOL: msg.present_principal(refs=[])", "done"]),
        pins=Pins(model="stub", temperature=0.0), instructions="present it")
    assert out.committed, out.errors

    sent = db.execute(
        "SELECT to_role, body_refs FROM messages WHERE verb = 'present'").fetchall()
    assert len(sent) == 1 and sent[0]["to_role"] == "principal"
    assert {"b1", "i1"} <= set(json.loads(sent[0]["body_refs"]))
    assert touch_note(db) == [], "presented once, whatever came of it"
    assert touch_notes(db) == {sent and db.execute(
        "SELECT id FROM messages WHERE verb = 'present'").fetchone()["id"]}


def test_the_set_is_read_out_at_the_edge(db):
    """Four parts, all mechanical: expected, possible, the unsurveyed ground
    by area prefix, and the commitment bound to a touched path."""
    _world(db)
    t = touch_set(db, "b1")
    assert t["item"] == {"id": "i1", "text": "users can export their invoices"}
    assert t["expected"] == ["src/invoices/export.py", "src/store/db.py"]
    assert t["possible"] == ["render_invoice"]
    assert t["unsurveyed"] == ["src/invoices"]
    assert [(c["id"], c["bound_to"]) for c in t["commitments"]] == [("k1", "src/store")]

    words = render_refs(db, ["b1", "i1"])
    for needle in ("src/invoices/export.py", "might touch render_invoice",
                   "unsurveyed ground: src/invoices",
                   "the store layer is synchronous",
                   "users can export their invoices"):
        assert needle in words, words
    assert touch_set(db, "nope") == {}
    assert touch_words(db, "i1") == "", "an item has words of its own"


def test_the_note_is_offered_before_the_batch_starts(db):
    """Within the band, the file order offers the note first; the batch does
    not wait on the answer, only on its turn."""
    _world(db)
    kinds = [w.kind for w in frontier_readonly(db)]
    assert kinds.index("tick:touch_note") < kinds.index("tick:batch_start")


def test_a_batch_that_got_ahead_is_still_owed_its_note(db):
    """The levers -- reorder, interrupt, contest -- act on a running batch, so
    a note that lost its turn is still owed; a finished batch owes nothing."""
    _world(db, status="running")
    assert [w.refs for w in touch_note(db)] == [("b1", "i1")]
    db.execute("UPDATE batches SET status = 'merged' WHERE id = 'b1'")
    db.commit()
    assert touch_note(db) == []


def test_a_note_nobody_answered_freezes_no_gate(db):
    """The jam the design named: `tick_signoff` refused to submit while any
    present was open, so a note left open would have frozen every later
    signoff. Each gate that reads "is anything open to the principal" sets
    the note aside -- and still holds on a present that is a ruling."""
    _world(db)
    _present(db, "m_note", ["b1", "i1"])
    db.execute("INSERT INTO items (id, text, kind, provenance) VALUES "
               "('i2', 'archive old invoices', 'in_scope', 'decided')")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1', 'invoice', 'a bill', 'observed')")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "author) VALUES ('a1', 'i1', 'items', 'assumed monthly', "
               "'vision_keeper')")
    db.commit()

    assert touch_notes(db) == {"m_note"}
    assert [w.kind for w in tick_signoff(db)] == ["tick:signoff"]
    assert [w.kind for w in observed_entries(db)] == ["tick:observed_entries"]
    assert [w.kind for w in tick_agenda(db, principal_present=True)] == ["tick:agenda"]

    _present(db, "m_sign", ["i2"])
    assert tick_signoff(db) == []
    assert observed_entries(db) == []
    assert tick_agenda(db, principal_present=True) == []


def test_an_acknowledged_note_wakes_nobody_and_a_contest_lands(db):
    """The door: approve is an acknowledgement, the batch is never a ruled
    row, and a contest on the item is a ruling like any other."""
    _world(db)
    _present(db, "m_note", ["b1", "i1"])
    ask = Ask(message_id="m_note", verb="present", refs=["b1", "i1"], rendered="")
    assert land(db, ask, Answer(verb="verdict",
                                per_item={"b1": "approve", "i1": "approve"})) is None
    assert db.execute("SELECT status FROM messages WHERE id = 'm_note'"
                      ).fetchone()["status"] == "answered"
    assert db.execute("SELECT COUNT(*) n FROM messages WHERE verb = 'verdict'"
                      ).fetchone()["n"] == 0
    assert not [w for w in frontier_readonly(db) if w.role == "liaison"]
    assert land(db, ask, Answer(verb="verdict", per_item={"i1": "contest"})) is None, \
        "closed is closed"

    _present(db, "m_note2", ["b1", "i1"])
    ask = Ask(message_id="m_note2", verb="present", refs=["b1", "i1"], rendered="")
    mid = land(db, ask, Answer(verb="verdict",
                               per_item={"b1": "contest", "i1": "contest"}))
    assert mid
    row = db.execute("SELECT verb, body_refs, cause_id FROM messages WHERE id = ?",
                     (mid,)).fetchone()
    assert (row["verb"], json.loads(row["body_refs"]), row["cause_id"]) == (
        "verdict", ["i1"], "m_note2")
    ruling = db.execute("SELECT value FROM config WHERE key = ?",
                        (f"verdict:{mid}",)).fetchone()
    assert json.loads(ruling["value"]) == {"i1": "contest"}


def test_an_answered_note_is_not_a_deferred_baseline(db):
    """`observed_entries` reads an answered present with no verdict as a
    deferral of the observed rows it carried. An acknowledged note lands no
    verdict on purpose, and the item it names was ruled on long ago."""
    _world(db)
    db.execute("UPDATE items SET provenance = 'observed' WHERE id = 'i1'")
    _present(db, "m_note", ["b1", "i1"], status="answered")
    assert not [w for w in observed_entries(db) if w.kind == "do:defer_baseline"]


def test_a_predicted_path_lives_where_the_tree_has_paths(db):
    """seat1 (2026-09-12): the touch note put src/split_bill.py to the person
    at the seat on a repository with no src/. The index is the fact."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    db.execute("INSERT OR IGNORE INTO code_index (grain, grain_kind) VALUES ('main.py', 'path')")
    db.execute("INSERT OR IGNORE INTO code_index (grain, grain_kind) VALUES ('tests/test_main.py', 'path')")
    db.commit()
    sb = build("architect", db, mode="annotate", batch_id="b1",
               allow=prompts.mode_tools("architect", "annotate"))
    with pytest.raises(ValueError, match="src/split_bill.py is under a directory the tree does not have"):
        sb.call("batches.annotate", batch_id="b1", paths=["src/split_bill.py"])
    out = sb.call("batches.annotate", batch_id="b1", paths=["split_bill.py", "main.py", "tests/test_split.py"])
    assert out["grains"] == 3
