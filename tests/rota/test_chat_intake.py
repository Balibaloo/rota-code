"""
Frame 142, pass 2: the chat intake for the principal's words goes (ruled:
Roman, 2026-10-08, `rota/DECISIONS.md`, "The park ask is a page with rows",
point 4; frame 142's design, 2.C and 2.F, amendment 3).

Each test rebuilds one night's rows inline: night 132's s220, woken by the
walk's stock sentence one turn after the same sentence drew a clarify, and
night 121's s284, which segmented that sentence as s5 a third time. The
night databases are ignored by git.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.runner import _mode_key, _recent_chat
from rota.core.sandbox import ArgumentError, build
from rota.core.scheduler import Wake
from rota.roles import prompts
from rota.roles.api import repeated_sentence

# The walk's stock sentence of night 132 (`plans/night132-read.md`).
WALK = "yes that all looks right, go ahead"
M119 = ("The Python version is captured from sys.version_info as major.minor.micro. "
        "Is there anything else I can assist with?")


def _msg(conn, mid, cause, from_role, to_role, verb, refs, seq, text=None):
    conn.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, verb, "
                 "body_refs, body_text, status, seq) VALUES (?, 't', ?, ?, ?, ?, ?, ?, "
                 "'open', ?)", (mid, cause, from_role, to_role, verb, json.dumps(refs),
                                text, seq))


@pytest.fixture
def s220(tmp_path):
    """e_p4 and e_p5 hold the walk's sentence. The Liaison asked about e_p4
    in m119. The walk writes each turn as an entry and a message with no
    `body_text`, so m_p5 carries the entry in its refs."""
    conn = init_db(tmp_path / "rota.db")
    for n, eid in ((4, "e_p4"), (5, "e_p5")):
        conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                     "VALUES (?, 'principal', ?, ?)", (eid, WALK, n))
    _msg(conn, "m_p4", None, "principal", "liaison", "converse", ["e_p4"], 4)
    _msg(conn, "m119", "m_p4", "liaison", "principal", "clarify", ["e_p4"], 5, M119)
    _msg(conn, "m_p5", None, "principal", "liaison", "converse", ["e_p5"], 6)
    conn.commit()
    return conn


def _converse(conn, trigger="m_p5", entry="e_p5"):
    sb = build("liaison", conn, mode="converse", entry_id=entry,
               allow=prompts.mode_tools("liaison", "converse"))
    sb.ctx.trigger = trigger
    return sb


def test_the_chat_verdict_is_refused_and_a_repeated_sentence_is_not_answered_twice(s220):
    """Night 132, s220: turn 2 claimed chat, and turn 3 sent m119's text
    again, word for word."""
    assert "msg.converse_principal" not in prompts.mode_tools("liaison", "converse")
    sb = _converse(s220)
    with pytest.raises(ArgumentError) as refused:
        sb.call("brief.intake", verdict="chat")
    assert str(refused.value).startswith(
        "brief.intake: the principal's words always land on a row. Words about a row: "
        "msg.clarify_principal(refs=[<the row>], question=...)")

    # The principal's own turn reaches `recent_chat` from its entry.
    chat = _recent_chat(s220, "m_p5")
    assert {"from": "principal", "text": WALK} in chat
    assert chat[-1] == {"from": "liaison", "text": M119, "asked": True}

    with pytest.raises(ValueError, match="you answered these words in m119, and the "
                                         "principal said them again"):
        sb.call("msg.clarify_principal", refs=["e_p5"], question="What would you like?")
    assert sb.ctx.outbound == []


def test_the_first_time_the_words_are_said_the_clarify_goes(s220):
    """The door keys on an earlier answer. The first sentence drew none."""
    s220.execute("DELETE FROM messages WHERE id = 'm119'")
    assert repeated_sentence(s220, "m_p5") is None
    sb = _converse(s220)
    out = sb.call("msg.clarify_principal", refs=["e_p5"], question="What would you like to build?")
    assert out["to"] == "principal"


def test_a_repeated_sentence_as_a_reply_to_the_clarify_is_refused_in_answering(s220):
    """The same rows with m_p5 as the reply to m119, which keys `answering`.
    `rulings.rule(ask=...)` writes a Liaison converse, and is refused the
    same way (frame 142's design, 2.F, amendment 3)."""
    s220.execute("UPDATE messages SET cause_id = 'm119' WHERE id = 'm_p5'")
    s220.commit()
    wake = Wake("liaison", "message", refs=("e_p5",), detail="converse", message_id="m_p5")
    assert _mode_key(wake, s220) == "answering"
    sb = build("liaison", s220, mode="normal", session_id="s220", wake=wake,
               allow=prompts.mode_tools("liaison", "answering"))
    sb.ctx.trigger = "m_p5"
    with pytest.raises(ValueError, match="you answered these words in m119"):
        sb.call("rulings.rule", ask="Is there anything else I can help with?")
    assert sb.ctx.outbound == []


def test_an_owners_answer_two_hops_below_the_repeated_words_is_refused(s220):
    """The `answer` mode keeps `msg.converse_principal`. Its trigger is an
    owner's answer, and the principal's words sit two hops above it."""
    _msg(s220, "m_ask", "m_p5", "liaison", "vision_keeper", "ask", ["e_p5"], 7)
    _msg(s220, "m_ans", "m_ask", "vision_keeper", "liaison", "answer", ["e_p5"], 8)
    s220.commit()
    assert repeated_sentence(s220, "m_ans") == "m119"
    sb = build("liaison", s220, mode="normal", session_id="s_ans",
               allow=prompts.mode_tools("liaison", "answer"))
    sb.ctx.trigger = "m_ans"
    with pytest.raises(ValueError, match="you answered these words in m119"):
        sb.call("msg.converse_principal", refs=["e_p5"], reply="It is done.")


def test_a_segment_of_a_statement_on_file_is_refused_and_names_it(tmp_path):
    """Night 121, s284: the walk's sentence became s4, s5 and s6, each a
    statement to ratify. s5 is on file, ratified."""
    conn = init_db(tmp_path / "rota.db")
    for n, eid in ((1, "e_p1"), (2, "e_p2")):
        conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                     "VALUES (?, 'principal', ?, ?)", (eid, WALK, n))
    conn.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
                 "status) VALUES ('s5', 'e_p1', 0, ?, ?, 'ratified')", (len(WALK), WALK))
    conn.commit()
    sb = build("liaison", conn, mode="converse", entry_id="e_p2",
               allow=prompts.mode_tools("liaison", "converse"))
    sb.call("brief.intake", verdict="work")
    with pytest.raises(ValueError) as refused:
        sb.call("brief.segment", id="s6", span_start=0, span_end=len(WALK), text=WALK)
    assert str(refused.value) == ("these words are s5, which is on file. Ask about that "
                                  "row with msg.clarify_principal(refs=['s5'], ...)")
    # A superseded statement is not on file.
    conn.execute("UPDATE statements SET status = 'superseded' WHERE id = 's5'")
    assert sb.call("brief.segment", id="s6", span_start=0, span_end=len(WALK),
                   text=WALK)["id"] == "s6"
