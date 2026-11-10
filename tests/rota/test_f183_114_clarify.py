"""Frames 183 and 114, build 2: three pages of dry run 8 that a row answered.

The rows are dry run 8's, copied by id from `dry8/copies/final.db` of
session 13b7eef8 (plans/f183-114-clarify-read-2026-11-10.md).
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.runner import resolve_inbound
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles import prompts

M30 = ("The requirement for folding long lines in icalendar specifies folding at "
       "a space to avoid splitting words. Does this rule apply to all lines "
       "regardless of length, or is there a minimum character threshold before "
       "folding is triggered?")
M52 = ("The requirement for folding long lines in icalendar specifies folding at "
       "a space to avoid splitting words. The current code folds lines longer "
       "than 75 octets and ensures the line does not already contain a newline. "
       "Does the requirement to fold at a space apply only to these lines longer "
       "than 75 octets, or should it be applied to all lines regardless of length?")
R_M45 = ("Fold only a line longer than 75 octets, as the code does today, and keep "
         "the line assert \"\\n\" not in line in _foldline.")


def _msg(conn, mid, seq, from_role, to_role, verb, refs, text=None, cause=None,
         thread=None, status="answered"):
    conn.execute(
        "INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, verb, "
        "body_refs, body_text, status, seq) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (mid, thread or mid, cause, from_role, to_role, verb, json.dumps(refs),
         text, status, seq))


@pytest.fixture
def w3(tmp_path):
    """m30, his reply m45, r_m45_2 and rr_997d2888b831, and the report m51."""
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval) VALUES "
                 "('folds_long_lines', 'When icalendar writes a long line, fold "
                 "it at a space.', 'in_scope', 'approved')")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES "
                 "('bg_1', 'folds_long_lines', 'running')")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_1', "
                 "'folds_long_lines', 'fold long lines in the _foldline function "
                 "at src/icalendar/parser/string.py')")
    _msg(conn, "m30", 30, "liaison", "principal", "clarify", ["bg_1"], M30,
         thread="m29")
    _msg(conn, "m45", 45, "principal", "liaison", "converse", ["bg_1"],
         cause="m30", thread="m29")
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('e_m45', 'principal', ?, 45)", (R_M45,))
    conn.execute(
        "INSERT INTO rulings (id, ask_id, reply_id, per_item, words, status) "
        "VALUES ('r_m45_2', 'm30', 'm45', '{\"bg_1\": \"approve\"}', ?, 'landed')",
        (R_M45,))
    conn.execute(
        "INSERT INTO ruled_refs (id, ruling_id, ref, verdict, words, words_from, "
        "source) VALUES ('rr_997d2888b831', 'r_m45_2', 'bg_1', 'approve', ?, "
        "'m45', 'reading')", (R_M45,))
    _msg(conn, "m51", 51, "vision_keeper", "liaison", "report", ["bg_1", "tk_1"])
    conn.commit()
    return conn


def _liaison(conn, sid="s187"):
    wake = Wake("liaison", "message", refs=("bg_1", "tk_1"), message_id="m51")
    sb = build("liaison", conn, mode="normal", session_id=sid, wake=wake,
               allow=prompts.mode_tools("liaison", "report"))
    sb.ctx.trigger = "m51"
    return sb


def test_a_clarify_on_rows_he_ruled_meets_his_words_first(w3):
    """W3. s187 call 4 sent m52 on bg_1 and tk_1, and r_m45_2 held his answer."""
    sb = _liaison(w3)
    with pytest.raises(ValueError) as got:
        sb.call("msg.clarify_principal", refs=["bg_1", "tk_1"], question=M52)
    said = str(got.value)
    assert "r_m45_2 on bg_1, approve" in said
    assert "Fold only a line longer than 75 octets, as the code does today" in said
    assert sb.ctx.outbound == []
    # The second call names the ruling it read, and it lands.
    sb.call("msg.clarify_principal", refs=["bg_1", "tk_1", "r_m45_2"],
            question=M52)
    assert [m["verb"] for m in sb.ctx.outbound] == ["clarify"]


def test_the_refusal_fires_once_per_session_per_ruling(w3):
    sb = _liaison(w3)
    with pytest.raises(ValueError, match="r_m45_2"):
        sb.call("msg.clarify_principal", refs=["bg_1", "tk_1"], question=M52)
    sb.call("msg.clarify_principal", refs=["bg_1", "tk_1"], question=M52)
    assert len(sb.ctx.outbound) == 1


def test_a_clarify_on_rows_with_no_landed_ruling_lands_at_once(w3):
    sb = _liaison(w3)
    sb.call("msg.clarify_principal", refs=["tk_1"], question=M52)
    assert len(sb.ctx.outbound) == 1
    # A ruling that has not landed covers nothing.
    w3.execute("UPDATE rulings SET status = 'open' WHERE id = 'r_m45_2'")
    other = _liaison(w3, sid="s188")
    other.call("msg.clarify_principal", refs=["bg_1"], question=M52)
    assert len(other.ctx.outbound) == 1


def test_a_liaison_tick_that_can_clarify_sees_his_answers(w3):
    """W3's reach: s190 on `tick:unresolved` had no `prior_answers`."""
    _msg(w3, "m34", 34, "developer", "architect", "escalate", ["bg_1"])
    wake = Wake("liaison", "tick:unresolved", refs=("m34",))
    got = resolve_inbound(w3, wake)
    assert got["prior_answers"][0]["question"] == M30
