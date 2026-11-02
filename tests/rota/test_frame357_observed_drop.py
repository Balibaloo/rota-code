"""
Frame 357, pass 3: his drop on a row the team observed is his objection on
file (ruled: Roman, 2026-11-02 11:43, shape B of
`plans/design-drop-observed-row-2026-11-02.md`).

Dry1's turn 17: the seat answered m145 with "Drop every note and build
nothing." `land` wrote `contested` on `how_it_works`, the Vision Keeper
defended it three times, the Liaison asked three clarifies, and the key went
to quarantine. The fixture copies the shape of dry1's rows by hand, from the
dry1w10 copy, so no database file travels. Each ruling lands through
`apply_rulings`, the path the wall came through.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.predicates import contested
from rota.core.scheduler import constraints_for_grains
from rota.roles.principal import (NOT_MINE, account_page_refs, apply_rulings,
                                  principal_objects, render_page, render_state)

HIW = "how_it_works"
NOTE = "get_current_context"
M147 = ("I asked for none of these notes. The change is merged and the work "
        "is done. Drop every note and build nothing.")


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _msg(db, mid, seq, frm, to, verb, refs, *, cause=None, status="answered",
         text=None):
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, body_text, seq, status) VALUES "
               "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (mid, cause, mid, frm, to, verb, json.dumps(refs), text, seq,
                status))


def _ruling(db, rid, ask, reply, per_item, words, act):
    """A Liaison ruling, read and not landed, with its reading rows."""
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words) "
               "VALUES (?, ?, ?, ?, ?)", (rid, ask, reply, json.dumps(per_item),
                                          words))
    for line, (ref, verdict) in enumerate(per_item.items(), 1):
        db.execute("INSERT INTO ruled_refs (id, ruling_id, ref, line, verdict, "
                   "act, target_kind, words, words_from, source) VALUES "
                   "(?, ?, ?, ?, ?, ?, ?, ?, ?, 'reading')",
                   (f"rr_{rid}_{line}", rid, ref, line, verdict, act,
                    "row" if act else None, words, reply))


def _dry1_turn17(db):
    """The description, one re-survey note, the page m145, an open clarify
    m144 about the note, and his reply m147 read as a drop of both lines."""
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES (?, 'Click builds command line interfaces.', "
               "'in_scope', 'approved', 1, 1)", (HIW,))
    db.execute("INSERT INTO constraints (id, headline, text, is_global) "
               "VALUES (?, ?, 'Programs import click.get_current_context.', 1)",
               (NOTE, NOTE))
    _msg(db, "m144", 140, "liaison", "principal", "clarify", [NOTE],
         status="open", text="Is this note right?")
    _msg(db, "m145", 141, "liaison", "principal", "present", [HIW, NOTE],
         status="open")
    _msg(db, "m147", 143, "principal", "liaison", "converse", [HIW, NOTE],
         cause="m145", text=M147)
    _ruling(db, "r_m147", "m145", "m147", {HIW: "contest", NOTE: "contest"},
            M147, "drop")


def test_a_drop_on_the_team_rows_writes_no_contest(db):
    _dry1_turn17(db)
    [verdict] = apply_rulings(db)
    assert db.execute("SELECT approval FROM items WHERE id = ?",
                      (HIW,)).fetchone()[0] == "approved"
    assert contested(db) == []
    row = db.execute("SELECT status, body_refs FROM messages WHERE id = ?",
                     (verdict,)).fetchone()
    assert (row["status"], json.loads(row["body_refs"])) == ("answered", [])


def test_the_objection_closes_the_asks_and_owes_no_page(db):
    _dry1_turn17(db)
    apply_rulings(db)
    assert principal_objects(db, HIW) and principal_objects(db, NOTE)
    assert [r[0] for r in db.execute(
        "SELECT id FROM messages WHERE to_role = 'principal' "
        "AND status = 'open'")] == []
    assert account_page_refs(db, [HIW, NOTE]) == []


def test_the_note_still_loads_into_structural_review(db):
    _dry1_turn17(db)
    apply_rulings(db)
    assert NOTE in constraints_for_grains(db, [])


def test_the_state_view_and_the_page_show_his_objection(db):
    _dry1_turn17(db)
    apply_rulings(db)
    state = render_state(db)
    assert f"click.get_current_context. ({NOT_MINE})" in state
    page = render_page(db, "present", [NOTE])[0]
    assert NOT_MINE in page


def test_a_later_approve_takes_the_objection_back(db):
    _dry1_turn17(db)
    apply_rulings(db)
    _msg(db, "m159", 150, "liaison", "principal", "present", [NOTE],
         status="open")
    _msg(db, "m160", 151, "principal", "liaison", "converse", [NOTE],
         cause="m159", text="ok")
    _ruling(db, "r_m160", "m159", "m160", {NOTE: "approve"}, "ok", None)
    apply_rulings(db)
    assert not principal_objects(db, NOTE)
    assert f"click.get_current_context. ({NOT_MINE})" not in render_state(db)


def test_a_drop_on_a_request_item_still_ends_it(db):
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('ask_one', 'Make pause return True.', "
               "'in_scope', 'draft', 1, 1)")
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m1', 'principal', 'Make pause return True.', 1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1', 'e_m1', 0, 23, "
               "'Make pause return True.', 'ratified')")
    db.execute("INSERT INTO refs (src_table, src_id, kind, target) VALUES "
               "('items', 'ask_one', 'statement', 's1')")
    _msg(db, "m90", 90, "liaison", "principal", "present", ["ask_one"],
         status="open")
    _msg(db, "m91", 91, "principal", "liaison", "converse", ["ask_one"],
         cause="m90", text="Drop 1.")
    _ruling(db, "r_m91", "m90", "m91", {"ask_one": "contest"}, "Drop 1.",
            "drop")
    apply_rulings(db)
    assert not principal_objects(db, "ask_one")
    assert db.execute("SELECT approval FROM items WHERE id = 'ask_one'"
                      ).fetchone()[0] == "dropped"
