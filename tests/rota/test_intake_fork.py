"""
The intake fork: chat or work, never both silently.

S0's blocker, measured live: handed "Hello, Please build a python script
that asks for the users name...", the converse session answered the greeting
and closed -- zero statements, the request gone politely. The brief patch
tried before ("Improove greeting handling") was prose, and prose lost for
the fourth measured time. Same cure as the Tester's triage fork: the
judgment becomes an act, two verdicts only (the taxonomy lesson), and the
reply channel enforces the claimed branch.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import ArgumentError, build
from rota.roles import prompts

HELLO = ('Hello, Please build a python script that asks for the users name, '
         'and then shows "Hellow User!"')


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
                 "('e_m_in','principal',1,?)", (HELLO,))
    conn.commit()
    return conn


def _intake(db):
    return build("liaison", db, mode="converse", entry_id="e_m_in",
                 allow=prompts.mode_tools("liaison", "converse"))


def test_an_unclaimed_reply_is_refused(db):
    """The exact S0 shape: reply first, claim never. Refused naming the
    fork, because an unclaimed reply is how a request dies politely."""
    sb = _intake(db)
    with pytest.raises(ValueError, match="brief.intake"):
        sb.call("msg.converse_principal", refs=[], reply="Hi! How can I help?")


def test_work_claimed_means_the_reply_carries_refs(db):
    sb = _intake(db)
    sb.call("brief.intake", verdict="work")
    with pytest.raises(ValueError, match="carries refs"):
        sb.call("msg.converse_principal", refs=[], reply="On it!")
    sb.call("brief.segment", id="s1", span_start=7, span_end=90,
            text='Please build a python script that asks for the users name, '
                 'and then shows "Hellow User!"')
    sb.call("msg.confirm_principal", refs=["s1"])
    assert sb.ctx.outbound


def test_work_claimed_with_the_entry_as_its_ref_is_still_nothing(db):
    """
    tipsI, 2026-09-09: a second sentence into a merged run. The Liaison
    claimed work, ref'd the entry, replied "Got it, anything else?", and the
    request died with the refs door satisfied. An entry is not a statement.
    """
    sb = _intake(db)
    sb.call("brief.intake", verdict="work")
    with pytest.raises(ValueError, match="segmented nothing"):
        sb.call("msg.converse_principal", refs=["e_m_in"], reply="Got it!")
    sb.call("brief.segment", id="s1", span_start=7, span_end=90,
            text='Please build a python script that asks for the users name, '
                 'and then shows "Hellow User!"')
    sb.call("msg.confirm_principal", refs=["s1"])
    assert sb.ctx.outbound


def test_chat_claimed_means_a_bare_reply_is_legal(db):
    sb = _intake(db)
    sb.call("brief.intake", verdict="chat")
    sb.call("msg.converse_principal", refs=[], reply="Hello to you too!")
    assert sb.ctx.outbound


def test_the_verdict_vocabulary_is_two_words(db):
    """Never three: the fork taxonomy lesson, applied at intake."""
    sb = _intake(db)
    with pytest.raises(ArgumentError, match="not one of"):
        sb.call("brief.intake", verdict="question")


def test_modes_without_the_fork_are_untouched(db):
    """Liaison's answer-relay replies to the principal without an intake
    claim -- the gate arms only where the mode offers the claim."""
    sb = build("liaison", db, mode="answer",
               allow=prompts.mode_tools("liaison", "answer"))
    assert getattr(sb.ctx, "intake", "unarmed") == "unarmed"


def test_the_entry_to_segment_is_the_one_the_message_carries(tmp_path):
    """clickI night 17 (2026-09-12): the runner derived the entry by name,
    `e_<message id>`, and a message named otherwise left `entry_id` empty;
    every brief.segment was refused and the sentence never became a
    statement. The message's refs are the fact."""
    from rota.core.runner import run_session
    from rota.core.scheduler import frontier
    from rota.llm.llm import ScriptedBackend

    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
                 "('e_p1','principal',1,'Add an echo helper that prints an object as JSON.')")
    conn.execute("INSERT INTO messages (id, cause_kind, thread_id, from_role, to_role, verb, "
                 "body_refs, seq) VALUES ('m_p1','message','t_p1','principal','liaison',"
                 "'converse','[\"e_p1\"]',1)")
    conn.commit()
    wake = next(w for w in frontier(conn) if w.role == "liaison" and w.message_id == "m_p1")
    out = run_session(conn, wake, backend=ScriptedBackend([
        "TOOL: brief.intake(verdict='work')",
        "TOOL: brief.segment(id='s1', span_start=0, span_end=49, "
        "text='Add an echo helper that prints an object as JSON.')",
        "TOOL: msg.confirm_principal(refs=['s1'])",
        "done", "done",
    ]))
    assert out.committed, out.errors
    assert not [e for e in out.errors if "no entry to segment" in e], out.errors
    assert conn.execute("SELECT COUNT(*) FROM statements WHERE id = 's1'").fetchone()[0] == 1
