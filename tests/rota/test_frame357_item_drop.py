"""
Frame 357, pass 2: a landed drop on a request line ends the item.

Dry1's turn 13: the seat answered the present m90 with "Drop 1 and 3. They
are not requests." The request menu had no `drop`, so the Liaison ruled
`other`, `land` wrote `contested`, and the Vision Keeper amended line 1 with
his words and defended both items. The fixture copies dry1's rows by hand,
from the dry1w7 copy, so no database file travels.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.predicates import contested
from rota.roles.api import line_menu
from rota.roles.principal import apply_rulings, off_page

S1 = ("Make click.pause() return True when it waited for a key and False when "
      "it skipped because stdin or stdout is not a terminal.")
E70 = "Write the tests again. The surface is click.pause in src/click/termui.py."
M101 = ("Drop 1 and 3. They are not requests. I dropped them once already, and "
        "the team asked again.")
SURFACE = "The surface is click.pause in src/click/termui.py."
TESTS = "Write the tests again."
ITEMS = ["surface_is_click_pause", "write_tests_again"]
M90 = ["surface_is_click_pause", "guess:surface_is_click_pause",
       "write_tests_again", "guess:write_tests_again", "reading:m78"]


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _msg(db, mid, seq, frm, to, verb, refs, *, cause=None, thread=None,
         status="answered", text=None):
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, body_text, seq, status) VALUES "
               "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (mid, cause, thread or mid, frm, to, verb, json.dumps(refs),
                text, seq, status))


def _ruling(db, rid, ask, reply, per_item, words, rows):
    """A Liaison ruling, read and not landed, with its reading rows."""
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words) "
               "VALUES (?, ?, ?, ?, ?)", (rid, ask, reply, json.dumps(per_item),
                                          words))
    for line, ref, verdict, act in rows:
        db.execute("INSERT INTO ruled_refs (id, ruling_id, ref, line, verdict, "
                   "act, target_kind, words, words_from, source) VALUES "
                   "(?, ?, ?, ?, ?, ?, ?, ?, ?, 'reading')",
                   (f"rr_{rid}_{line}", rid, ref, line, verdict, act,
                    "row" if act else None, words, reply))


def _dry1_turn13(db, act="drop"):
    """Dry1's rows up to m101, with r_m101 read as the new menu reads it."""
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m1', 'principal', ?, 1), ('e_m70', 'principal', ?, 26)",
               (S1, E70))
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1', 'e_m1', 0, 124, ?, 'ratified'), "
               "('s2', 'e_m70', 0, 22, ?, 'ratified'), "
               "('s3', 'e_m70', 23, 73, ?, 'ratified')", (S1, TESTS, SURFACE))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('click_pause_returns_true_on_key', ?, "
               "'in_scope', 'approved', 1, 1), ('write_tests_again', ?, "
               "'in_scope', 'draft', 1, 1), ('surface_is_click_pause', ?, "
               "'in_scope', 'draft', 1, 1)", (S1, TESTS, SURFACE))
    for item, sid in (("click_pause_returns_true_on_key", "s1"),
                      ("write_tests_again", "s2"), ("write_tests_again", "s3"),
                      ("surface_is_click_pause", "s2"),
                      ("surface_is_click_pause", "s3")):
        db.execute("INSERT INTO refs (src_table, src_id, kind, target) VALUES "
                   "('items', ?, 'statement', ?)", (item, sid))
    _msg(db, "m1", 1, "principal", "liaison", "converse", ["e_m1"], text=S1)
    _msg(db, "m70", 70, "principal", "liaison", "converse", ["e_m70"], text=E70)
    _msg(db, "m89", 92, "vision_keeper", "liaison", "submit", ITEMS)
    _msg(db, "m90", 94, "liaison", "principal", "present", M90, cause="m89",
         thread="m89", status="open")
    _msg(db, "m101", 104, "principal", "liaison", "converse", M90, cause="m90",
         thread="m89", text=M101)
    _ruling(db, "r_m101", "m90", "m101",
            {"surface_is_click_pause": "contest",
             "guess:surface_is_click_pause": "approve",
             "write_tests_again": "contest",
             "guess:write_tests_again": "approve", "reading:m78": "contest"},
            M101, [(1, "surface_is_click_pause", "contest", act),
                   (3, "write_tests_again", "contest", act),
                   (5, "reading:m78", "contest", "drop")])
    db.commit()


def _item(db, iid):
    return db.execute("SELECT text, approval, version FROM items WHERE id = ?",
                      (iid,)).fetchone()


def test_a_request_line_offers_drop(db):
    _dry1_turn13(db)
    kind, options = line_menu(db, "write_tests_again", M90, "")
    assert kind == "request"
    assert "drop" in options


def test_the_drop_on_lines_1_and_3_lands_as_dropped(db):
    _dry1_turn13(db)
    apply_rulings(db)
    db.commit()
    for iid, text in (("surface_is_click_pause", SURFACE),
                      ("write_tests_again", TESTS)):
        row = _item(db, iid)
        assert (row["approval"], row["text"], row["version"]) == (
            "dropped", text, 1)
    assert _item(db, "click_pause_returns_true_on_key")["approval"] == "approved"
    # The verdict names no dropped item, so no relay takes it to an owner.
    verdict = db.execute("SELECT body_refs, status FROM messages WHERE "
                         "cause_id = 'm90' AND verb = 'verdict'").fetchone()
    assert json.loads(verdict["body_refs"]) == []
    assert verdict["status"] == "answered"


def test_contested_wakes_nobody_for_the_dropped_items(db):
    _dry1_turn13(db)
    apply_rulings(db)
    db.commit()
    assert contested(db) == []


def test_no_page_carries_a_row_of_a_dropped_item(db):
    _dry1_turn13(db)
    apply_rulings(db)
    db.commit()
    rows = ITEMS + ["guess:surface_is_click_pause", "guess:write_tests_again"]
    assert off_page(db, rows) == set(rows)
    assert off_page(db, rows, confirm=True) == set(rows)


def _sandbox(db, role, trigger, mode):
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = build(role, db, mode=mode, session_id="sess_357b",
               allow=prompts.mode_tools(role, mode))
    sb.ctx.trigger = trigger
    return sb


def test_an_approve_after_the_drop_revives_nothing(db):
    """Dry1's m122 put both items on a page again. An "ok" there, ruled
    approve, leaves them dropped, and no seat writes them again."""
    _dry1_turn13(db)
    apply_rulings(db)
    _msg(db, "m122", 125, "liaison", "principal", "present", ITEMS,
         status="open")
    _msg(db, "m123", 126, "principal", "liaison", "converse", ITEMS,
         cause="m122", thread="m122", text="ok")
    _ruling(db, "r_m123", "m122", "m123",
            {"surface_is_click_pause": "approve", "write_tests_again": "approve"},
            "ok", [(1, "surface_is_click_pause", "approve", None),
                   (2, "write_tests_again", "approve", None)])
    db.commit()
    apply_rulings(db)
    db.commit()
    assert [_item(db, i)["approval"] for i in ITEMS] == ["dropped", "dropped"]
    # The two doors of the Vision Keeper's amend, called as the ops.
    from types import SimpleNamespace

    from rota.roles.api import problem_assert, problem_set_approval

    vk = SimpleNamespace(conn=db, writes=[], session_id="sess_357b",
                         role="vision_keeper", trigger=None)
    with pytest.raises(ValueError, match="dropped surface_is_click_pause"):
        problem_assert(vk, id="surface_is_click_pause",
                       text=SURFACE + " " + M101)
    with pytest.raises(ValueError, match="dropped write_tests_again"):
        problem_set_approval(vk, id="write_tests_again", approval="contested")
    assert not vk.writes
    liaison = _sandbox(db, "liaison", "m123", "normal")
    with pytest.raises(ValueError, match="dropped write_tests_again"):
        liaison.call("msg.clarify_principal", refs=["write_tests_again"],
                     question="Write the tests again: what should change?")


def test_a_contest_with_no_drop_keeps_todays_path(db):
    _dry1_turn13(db, act=None)
    apply_rulings(db)
    db.commit()
    assert [_item(db, i)["approval"] for i in ITEMS] == ["contested",
                                                         "contested"]
    assert sorted(w.refs[0] for w in contested(db)) == sorted(ITEMS)
    assert off_page(db, ITEMS) == set()
