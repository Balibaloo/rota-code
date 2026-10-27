"""
Frame 316 with 315, W3 of night 163: a contest of another item's rows.

Night 163 met the wall in three hops (`plans/night163-walk1-read.md`,
sections 3 and 4). The signoff s151 submitted six items beside the one
draft that woke it, so page m48 under item 3 carried item 1's item, guess
and criteria as lines 3 to 6. His m49 "take lines 3 to 6 off this page"
contested item 1, and the cancel predicate abandoned bg_1. On the contested
wake, s167 stored his m61 refusal as item 1's text, and pages m70 and m92
showed it under "You asked".

The fixture has the shape of night 163's rows: two requests, item 1
approved with a live batch, item 3 a draft.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import backfill_ruled_refs, init_db
from rota.core.predicates import Wake
from rota.core.sandbox import build
from rota.testkit.fixtures import seed_provenance, seed_ref

ITEM1 = "format_filename_example"
ITEM3 = "clear_returns_bool"
DESCRIPTIONS = ["defines_commands_and_options", "how_it_works",
                "parses_and_executes_inputs", "provides_command_line_interface"]
S151_SUBMIT = [ITEM3, "defines_commands_and_options", ITEM1, "how_it_works",
               "parses_and_executes_inputs", "provides_command_line_interface"]
M48_REFS = S151_SUBMIT + ["c_1", "c_2", f"guess:{ITEM3}", f"guess:{ITEM1}"]
M49 = ("Line 3 is about the format_filename docstring, which was my first "
       "change, not this one. Please take lines 3 to 6 off this page and keep "
       "only the clear() work. For clear(), the output stays the same and only "
       "the return value changes.")
M61 = ("I don't know whether that example is there, and it doesn't matter here "
       "because the format_filename docstring is my first change, not this one. "
       "Please drop format_filename from this page completely and plan only the "
       "clear() work, where the output stays the same and only the return value "
       "changes.")
M61_FIRST = M61.split(". ")[0] + "."


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    for n, (entry, order, item, approval, text) in enumerate((
            ("e_p1", 1, ITEM1, "approved",
             "Give format_filename one example in its docstring: with shorten "
             "set to True, the path a/b/c.txt shows as c.txt."),
            ("e_p3", 3, ITEM3, "draft",
             "Make clear() return True when it cleared the screen and False "
             "when stdout is not a terminal.")), start=1):
        conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
                     "(?, 'principal', ?, ?)", (entry, order, text))
        conn.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
                     "text, status) VALUES (?, ?, 0, 10, ?, 'ratified')",
                     (f"s{n}", entry, text))
        conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                     "version) VALUES (?, ?, 'in_scope', ?, 1, 1)",
                     (item, f"the {item} change", approval))
        seed_ref(conn, "items", item, "statement", f"s{n}")
        seed_provenance(conn, "items", item, "decided")
    for item in DESCRIPTIONS:
        conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                     "version, is_description) VALUES (?, ?, 'in_scope', "
                     "'approved', 1, 1, 1)", (item, f"Click {item}"))
        seed_provenance(conn, "items", item, "observed")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_1', ?, 'a ticket')",
                 (ITEM1,))
    for crit in ("c_1", "c_2"):
        conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                     "VALUES (?, 'tk_1', 'a criterion', '[]')", (crit,))
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES ('bg_1', ?, 'running')",
                 (ITEM1,))
    conn.commit()
    return conn


def _approval(db, item):
    return db.execute("SELECT approval FROM items WHERE id = ?", (item,)
                      ).fetchone()["approval"]


def test_s151_signoff_submit_carries_only_the_woken_draft(db):
    """Hop 1: s151 sent six refs on a wake that named item 3 only."""
    vk = build("vision_keeper", db, mode="normal",
               wake=Wake("vision_keeper", "tick:signoff", refs=(ITEM3,)))
    out = vk.call("msg.submit_liaison", refs=list(S151_SUBMIT))
    assert [m["body_refs"] for m in vk.ctx.outbound] == [[ITEM3]]
    # The drop is said, never silent (review finding 3).
    for ref in S151_SUBMIT[1:]:
        assert ref in out["note"], out


def test_m48_submit_page_shows_only_item_3s_rows(db):
    """Hop 1: s152 presented m48 on six items for a submit of item 3."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m47', 'th', 'vision_keeper', "
               "'liaison', 'submit', ?, 1, 'open')", (json.dumps([ITEM3]),))
    db.commit()
    li = build("liaison", db, mode="normal",
               wake=Wake("liaison", "message", "m47", refs=(ITEM3,), detail="submit"))
    # The runner sets the trigger after the build.
    li.ctx.trigger = "m47"
    li.call("msg.present_principal", refs=list(S151_SUBMIT))
    refs = li.ctx.outbound[0]["body_refs"]
    assert ITEM3 in refs
    for row in (ITEM1, "c_1", "c_2", f"guess:{ITEM1}", *DESCRIPTIONS):
        assert row not in refs, refs


E_P3 = ("Make clear() return True when it cleared the screen and False when "
        "stdout is not a terminal.")


def _requests(db):
    """His two request messages, as m_p1 and m_p3 on night 163."""
    for mid, entry, seq in (("m_p1", "e_p1", 17), ("m_p3", "e_p3", 45)):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                   "body_refs, seq, status) VALUES (?, ?, 'principal', 'liaison', "
                   "'converse', ?, ?, 'answered')",
                   (mid, f"t_{mid}", json.dumps([entry]), seq))
    db.commit()


def test_s146_segment_of_the_clear_request_takes_no_supersedes(db):
    """The cause of hop 2: s146 saved the clear() request as a follow-up of
    the format_filename request s1, so both items sat in request e_p1."""
    _requests(db)
    # At s146, e_p3 had no statement yet.
    db.execute("DELETE FROM refs WHERE target = 's2'")
    db.execute("DELETE FROM statements WHERE id = 's2'")
    db.commit()
    li = build("liaison", db, mode="normal", entry_id="e_p3",
               wake=Wake("liaison", "message", "m_p3", detail="converse"))
    li.ctx.trigger = "m_p3"
    with pytest.raises(ValueError) as err:
        li.call("brief.segment", id="s2", span_entry="e_p3", span_start=0,
                span_end=len(E_P3), text=E_P3, supersedes="s1")
    assert str(err.value) == (
        "`supersedes` names `s1`, which is about format_filename. These words "
        "name clear, so they are a new request. Leave `supersedes` out.")
    assert not [w for w in li.ctx.writes if w[0] == "statements"]
    # The same words with no supersedes land as a request of their own.
    li.call("brief.segment", id="s2", span_entry="e_p3", span_start=0,
            span_end=len(E_P3), text=E_P3)


def test_a_follow_up_on_the_same_function_keeps_supersedes(db):
    _requests(db)
    li = build("liaison", db, mode="normal", entry_id="e_p3",
               wake=Wake("liaison", "message", "m_p3", detail="converse"))
    li.ctx.trigger = "m_p3"
    said = "Give format_filename a second example for a path with no folder."
    db.execute("UPDATE entries SET text = ? WHERE id = 'e_p3'", (said,))
    db.commit()
    out = li.call("brief.segment", id="s9", span_entry="e_p3", span_start=0,
                  span_end=len(said), text=said, supersedes="s1")
    staged = [w for w in li.ctx.writes if w[0] == "statements" and w[1] == "s9"]
    assert staged[0][2].get("supersedes") == "s1", (staged, out)


def test_m48_with_no_supersede_link_holds_no_row_of_item_1(db):
    """With two requests, as the door now keeps them, `off_page` takes item
    1's rows off m48. With s146's link, the night's shape, it took none, and
    m49's contest of lines 3 to 6 reached item 1."""
    from rota.roles.principal import off_page

    _requests(db)
    rows = {ITEM1, "c_1", "c_2", f"guess:{ITEM1}"}
    assert rows <= off_page(db, M48_REFS), off_page(db, M48_REFS)
    db.execute("UPDATE statements SET supersedes = 's1' WHERE id = 's2'")
    db.commit()
    assert not rows & off_page(db, M48_REFS), off_page(db, M48_REFS)


def _contested_wake(db):
    for mid, seq, text in (("m49", 10, M49), ("m61", 20, M61)):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                   "body_refs, body_text, seq, status) VALUES (?, 'th', 'principal', "
                   "'liaison', 'converse', '[]', ?, ?, 'answered')", (mid, text, seq))
        db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
                   "(?, 'principal', ?, ?)", (f"e_{mid}", seq, text))
    db.execute("INSERT INTO config (key, value) VALUES ('verdict:m49', ?)",
               (json.dumps({ITEM1: "contest"}),))
    # The verdict lands as a ruling with its rows, the record that the
    # contest reader reads (the seam design, 3.4).
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('ask_m49', 'th', 'liaison', 'principal', "
               "'present', '[]', 9)")
    db.execute("INSERT INTO rulings (id, ask_id, per_item, words, status, "
               "verdict_id) VALUES ('r_m49', 'ask_m49', ?, ?, 'landed', 'm49')",
               (json.dumps({ITEM1: "contest"}), M49))
    backfill_ruled_refs(db)
    db.execute("UPDATE items SET approval = 'contested' WHERE id = ?", (ITEM1,))
    db.commit()
    return build("vision_keeper", db, mode="normal",
                 wake=Wake("vision_keeper", "tick:contested", refs=(ITEM1,)))


def test_s167_assert_of_his_m61_refusal_is_refused(db):
    """Hop 3: s167 turn 4 stored m61's first sentence as item 1's text."""
    vk = _contested_wake(db)
    with pytest.raises(ValueError) as exc:
        vk.call("problem.assert", id=ITEM1, text=M61_FIRST, kind="in_scope")
    assert "e_m61" in str(exc.value)
    assert M61_FIRST in str(exc.value)
    assert db.execute("SELECT text FROM items WHERE id = ?", (ITEM1,)
                      ).fetchone()["text"] == f"the {ITEM1} change"


def test_a_sentence_the_contest_carries_stays_an_amend(db):
    """The m49 sentence about the item is the words of the contest."""
    from rota.roles.api import _reply_sentence_fault

    vk = _contested_wake(db)
    said = ("For clear(), the output stays the same and only the return value "
            "changes.")
    assert _reply_sentence_fault(vk.ctx, ITEM1, said, None, [ITEM1]) is None


def test_a_word_before_a_spaced_bracket_is_not_a_function():
    """The re-check of 1b513c31: "the terminal (TERM=dumb)" named a
    function `terminal`, so a correction of clear() was refused."""
    from rota.roles.api import _named_surfaces

    said = "clear() prints nothing on the terminal (TERM=dumb)."
    assert "terminal" not in _named_surfaces(said)
    assert "clear" in _named_surfaces(said)
