"""
Frame 142, pass 2e: night 135's loop on a row id the principal cannot see.

The Liaison's s209 segmented the ratified s1's words seven times with a
span of 0 to 6, was told to ask about "that row" with a clarify, and asked
the principal "What is the content of the row with id 's1'?" (m119). The
landing sessions s220 to s224 asked it again after each answer, and s223
overwrote s1 by segmenting another entry under its id.

Each test rebuilds the rows inline from the night's database, read with
`mode=ro` on 2026-10-09. The night databases are ignored by git.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.runner import resolve_inbound
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles import prompts
from rota.roles.api import answered_question

E_M51 = ("Describe the repo and the code as click, the Python library for building "
         "command-line tools with decorators, and drop every mention of Briefcase from "
         "lines 13 to 15. To remove the repeats, delete line 2 and lines 6 to 8, and keep "
         "line 1 and lines 3 to 5.")
E_P1 = ("Add an echo_json(obj) helper next to echo that prints an object as compact JSON "
        "on one line, followed by a newline.")
ASK = "What is the content of the row with id 's1'?"
PAGE_REFS = ["l_11113fad2c", "l_24b7b97140"]


def _msg(conn, mid, cause, thread, from_role, to_role, verb, refs, seq, text=None):
    conn.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, verb, "
                 "body_refs, body_text, status, seq) VALUES (?, ?, ?, ?, ?, ?, ?, ?, "
                 "'answered', ?)", (mid, thread, cause, from_role, to_role, verb,
                                    json.dumps(refs), text, seq))


@pytest.fixture
def n135(tmp_path):
    """e_m51 ratified as s1 at version 1, and e_p1 still unsegmented."""
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('e_m51', 'principal', ?, 1)", (E_M51,))
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('e_p1', 'principal', ?, 2)", (E_P1,))
    conn.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
                 "status, version) VALUES ('s1', 'e_m51', 0, ?, ?, 'ratified', 1)",
                 (len(E_M51), E_M51))
    conn.commit()
    return conn


def _segmenter(conn, entry):
    sb = build("liaison", conn, mode="normal", entry_id=entry,
               allow=prompts.mode_tools("liaison", "converse"))
    return sb


def test_the_words_of_a_ratified_statement_are_cited_and_never_asked_about(n135):
    """Fix 1. s209 was told to send a clarify that named s1, and asked the
    principal about a row id. A ratified row is cited, and nothing is asked."""
    sb = _segmenter(n135, "e_m51")
    with pytest.raises(ValueError) as refused:
        sb.call("brief.segment", id="l_0941d2316c", span_entry="e_m51",
                span_start=0, span_end=len(E_M51), text=E_M51)
    said = str(refused.value)
    assert said == ("these words are s1, which the principal ratified. Cite s1. "
                    "There is nothing to segment or ask")
    assert "clarify" not in said and "msg." not in said
    # A proposed row names the confirm that it waits for.
    n135.execute("UPDATE statements SET status = 'proposed' WHERE id = 's1'")
    with pytest.raises(ValueError, match=r"msg\.confirm_principal\(refs=\['s1'\]\)"):
        sb.call("brief.segment", id="l_0941d2316c", span_entry="e_m51",
                span_start=0, span_end=len(E_M51), text=E_M51)


def test_a_span_that_does_not_hold_the_text_is_set_from_the_text(n135):
    """Fix 2. s209's call: span 0 to 6 with the entry's 254 characters. The
    door sets the span from where the words are, so the row's span holds
    its text. With s1 on file, the same call meets the ratified refusal."""
    with pytest.raises(ValueError, match="which the principal ratified"):
        _segmenter(n135, "e_m51").call(
            "brief.segment", id="l_0941d2316c", span_entry="e_m51",
            span_start=0, span_end=6, text=E_M51)
    n135.execute("DELETE FROM statements")
    sb = _segmenter(n135, "e_m51")
    sb.call("brief.segment", id="l_0941d2316c", span_entry="e_m51",
            span_start=0, span_end=6, text=E_M51)
    sb.call("brief.segment", id="l_2", span_entry="e_m51",
            span_start=0, span_end=300, text="keep line 1 and lines 3 to 5.")
    spans = {w[1]: (w[2]["span_start"], w[2]["span_end"]) for w in sb.ctx.writes}
    assert spans == {"l_0941d2316c": (0, 254), "l_2": (225, 254)}
    assert E_M51[225:254] == "keep line 1 and lines 3 to 5."


def test_a_segment_under_an_id_on_file_is_refused_and_the_row_stays(n135):
    """Fix 3. s223 segmented e_p1 as s1, and the write overwrote the
    ratified s1 at version 2 with span_end 223."""
    sb = _segmenter(n135, "e_p1")
    with pytest.raises(ValueError) as refused:
        sb.call("brief.segment", id="s1", span_start=0, span_end=223, text=E_P1)
    # The refusal names the next free id, and the same call with it lands
    # (the review of eee89bc8, fix 1: s267's shape).
    assert str(refused.value) == ("s1 is on file; a statement keeps its id. Segment "
                                  "these words as s2")
    assert sb.ctx.writes == []
    row = n135.execute("SELECT span_entry, version FROM statements WHERE id = 's1'").fetchone()
    assert (row["span_entry"], row["version"]) == ("e_m51", 1)
    out = sb.call("brief.segment", id="s2", span_start=0, span_end=223, text=E_P1)
    assert out["id"] == "s2" and out["span"] == [0, len(E_P1)]
    # Words on file meet the words refusal alone, never the id refusal first.
    with pytest.raises(ValueError, match="these words are s1, which the principal"):
        _segmenter(n135, "e_m51").call("brief.segment", id="s1", span_start=0,
                                       span_end=len(E_M51), text=E_M51)


def test_a_moved_span_is_said_in_the_result(n135):
    """The review of eee89bc8, fix 3: the move was silent, and with the
    words twice in the entry the door picks the nearer copy."""
    n135.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
                 "('e_x', 'principal', 'Drop line 2. Keep line 3. Drop line 2.', 3)")
    sb = _segmenter(n135, "e_x")
    out = sb.call("brief.segment", id="s9", span_start=10, span_end=22, text="Drop line 2.")
    assert out == {"id": "s9", "span_entry": "e_x", "span": [0, 12],
                   "note": "span set from the text"}
    # A span that holds the words is not moved, and says nothing.
    assert "note" not in sb.call("brief.segment", id="s8", span_start=13, span_end=25,
                                 text="Keep line 3.")


def _page(conn, upto):
    """Night 135's rows from m119 to `upto`: the clarify on s1 and its reply,
    then the page m127, its replies and the Liaison's asks under them."""
    rows = [
        # m119's cause, the self-relay m116, is a frame of its own.
        ("m119", None, "m113", "liaison", "principal", "clarify", ["s1"], 119, ASK),
        ("m120", "m119", "m113", "principal", "liaison", "converse", ["s1"], 120, None),
        ("m127", None, "m127", "liaison", "principal", "present", PAGE_REFS, 127, None),
        ("m128", "m127", "m127", "principal", "liaison", "converse", PAGE_REFS, 128,
         "I can't approve this page, because none of the seven lines says what you mean."),
        ("m129", "m128", "m127", "liaison", "principal", "converse", PAGE_REFS, 129, ASK),
        ("m130", "m127", "m127", "principal", "liaison", "converse", PAGE_REFS, 130,
         'I don\'t know of any row called "s1".'),
        ("m131", "m130", "m127", "liaison", "principal", "converse", PAGE_REFS, 131, ASK),
        ("m132", "m127", "m127", "principal", "liaison", "converse", PAGE_REFS, 132,
         "I still don't know of any row by that name."),
        ("m133", "m132", "m127", "liaison", "principal", "converse", PAGE_REFS, 133, ASK),
        ("m134", "m127", "m127", "principal", "liaison", "converse", PAGE_REFS, 134,
         "I can't approve this. Line 1 is wrong."),
    ]
    for mid, cause, thread, frm, to, verb, refs, seq, text in rows:
        _msg(conn, mid, cause, thread, frm, to, verb, refs, seq, text)
        if mid == upto:
            break
    conn.execute("UPDATE messages SET status = 'open' WHERE id = 'm127'")
    conn.commit()


@pytest.mark.parametrize("upto,earlier", [("m128", ("m119", "m120")),
                                          ("m130", ("m129", "m130"))])
def test_a_question_the_principal_answered_is_not_asked_again(n135, upto, earlier):
    """Fix 4. s220 asked m129 after m119 drew m120, and s222 asked m131
    after m129 drew m130. m130's cause is the page, so a cause key misses it."""
    _page(n135, upto)
    assert answered_question(n135, ASK) == earlier
    wake = Wake("liaison", "message", refs=tuple(PAGE_REFS), detail="converse",
                message_id=upto)
    sb = build("liaison", n135, mode="normal", session_id="s220", wake=wake,
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = upto
    question, reply = earlier
    with pytest.raises(ValueError, match=f"you asked this in {question}, and the "
                                         f"principal answered it in {reply}"):
        sb.call("rulings.rule", ask=ASK)
    assert sb.ctx.outbound == []
    # A clarify to the principal gets the same step. The older door on the
    # clarify's words fires first, and it now gives the answered door's
    # message (the review of eee89bc8, fix 2).
    other = build("liaison", n135, mode="normal", session_id="s_c",
                  allow=prompts.mode_tools("liaison", "converse"))
    with pytest.raises(ValueError, match=f"you asked this in {question}, and the "
                                         f"principal answered it in {reply}"):
        other.call("msg.clarify_principal", refs=["s1"], question=ASK)
    # A converse to the principal meets the new door, as in the `answer` mode.
    from rota.roles import api
    other.ctx.trigger = upto
    with pytest.raises(ValueError, match=f"you asked this in {question}"):
        api.refuse_answered_question(other.ctx, ASK)


def test_the_landing_exchange_shows_the_liaisons_own_asks(n135):
    """Fix 5. s224, woken by m134, saw four answers and no question."""
    _page(n135, "m134")
    wake = Wake("liaison", "message", refs=tuple(PAGE_REFS), detail="converse",
                message_id="m134")
    earlier = resolve_inbound(n135, wake)["landing"]["earlier_exchange"]
    assert [(t["from_role"], t.get("asked", False)) for t in earlier] == [
        ("principal", False), ("liaison", True), ("principal", False),
        ("liaison", True), ("principal", False), ("liaison", True)]
    assert [t["body_text"] for t in earlier if t.get("asked")] == [ASK, ASK, ASK]


def test_a_span_entry_that_names_a_statement_is_refused_and_the_session_commits(n135):
    """Fix 6. s247, s248 and s249 sent span_entry='s1', a statement id, on
    the self-relay m156 that carried one ledger id and no entry. The row was
    staged, and the session died at commit on the foreign key."""
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend

    sb = build("liaison", n135, mode="normal", entry_id=None,
               allow=prompts.mode_tools("liaison", "converse"))
    with pytest.raises(ValueError) as refused:
        sb.call("brief.segment", id="l_0cfe6f462c", span_start=0, span_end=45,
                text=E_M51[:45], span_entry="s1")
    assert str(refused.value) == ("s1 is a statement, and a statement is not an entry. "
                                  "This session has no entry to segment against")
    assert sb.ctx.writes == []

    _msg(n135, "m156", None, "m156", "liaison", "liaison", "relay", ["l_0cfe6f462c"], 156)
    n135.execute("UPDATE messages SET status = 'open' WHERE id = 'm156'")
    n135.commit()
    wake = Wake("liaison", "message", refs=("l_0cfe6f462c",), detail="relay",
                message_id="m156")
    call = (f"TOOL: brief.segment(id='l_0cfe6f462c', span_start=0, span_end=45, "
            f"text='{E_M51[:45]}', span_entry='s1')")
    out = run_session(n135, wake, backend=ScriptedBackend([call, "done"]),
                      pins=Pins(model="stub", temperature=0.0), instructions="x")
    assert out.committed, out.errors
    assert [r["id"] for r in n135.execute("SELECT id FROM statements")] == ["s1"]
