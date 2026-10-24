"""
Frame 320: a new request whose Liaison session lands nothing is retried
once, then reported to the principal in one line.

Night 163's s145 woke on m_p2, his `get_app_dir` sentence. The paste door
refused its clarifies, the session ended with nothing, and the commit
marked m_p2 answered. Frame 267's retry took only a reply to a page, so
nothing woke on the request and the walk read quiet.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import (OutboundMessage, SessionResult, Write, init_db,
                          session_commit)
from rota.core.runner import _missed_reply_line, run_session
from rota.core.scheduler import Wake
from rota.llm.llm import Pins, ScriptedBackend

E_P2 = ("In get_app_dir on Windows, when APPDATA or LOCALAPPDATA is not set, "
        "use the AppData Roaming or AppData Local folder under the home "
        "folder instead of the bare home folder.")
# s145's turn 1 completion on night 163, verbatim.
S145_TURN_1 = (
    'TOOL: msg.clarify_principal(refs=["e_p2"], question="In get_app_dir on '
    'Windows, when APPDATA or LOCALAPPDATA is not set, use the AppData Roaming '
    'or AppData Local folder under the home folder instead of the bare home '
    'folder. Is this still the correct approach?")')
# s145's first refusal on night 163, before frame 320 named brief.segment.
S145_REFUSAL = (
    "'in get app dir on windows when appdata ...' is the principal's own "
    "sentence, pasted back to them. They know what they said, and reading it "
    "to them again is not an answer to it. Ask the one thing you do not know, "
    "in your words. If the reply was an answer to a role, that role reads it, "
    "not the principal")


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('e_p2','principal',?,2)", (E_P2,))
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, seq, status, attempts) VALUES ('m_p2','t_p1',"
                 "'principal','liaison','converse','[\"e_p2\"]',44,'open',0)")
    conn.commit()
    return conn


def _row(db, mid):
    return dict(db.execute("SELECT status, unresolved_note FROM messages "
                           "WHERE id = ?", (mid,)).fetchone())


def _told(db):
    return [dict(r) for r in db.execute(
        "SELECT id, cause_id, from_role, verb, body_refs, body_text, status "
        "FROM messages WHERE to_role = 'principal'")]


def _commit(db, sid, attempts, **kw):
    db.execute("UPDATE messages SET attempts = ? WHERE id = 'm_p2'", (attempts,))
    kw.setdefault("refusals", [("msg.clarify_principal", S145_REFUSAL,
                                "ValueError")])
    session_commit(db, SessionResult(
        session_id=sid, role="liaison", trigger_msg="m_p2",
        wake_kind="message", wake_detail="converse", **kw))


def test_s145_on_m_p2_retries_once_then_tells_him(db):
    """The replay of s145's end, twice through the runner. The first run
    leaves m_p2 open with the refusal. The second wake carries the refusal
    in its head, and its miss sends him one line."""
    from rota.roles.principal import pending_replies

    wake = Wake(role="liaison", kind="message", message_id="m_p2",
                detail="converse")
    shown = []
    for run in range(2):
        backend = ScriptedBackend([S145_TURN_1] * 6)
        outcome = run_session(db, wake, backend=backend,
                              pins=Pins(model="scripted"))
        assert outcome.committed, outcome.errors
        shown.append(backend.calls[0][1])
        # Cause 9: the paste door names the route the mode holds.
        assert "segment it with brief.segment" in backend.calls[1][1]
        if run == 0:
            first = _row(db, "m_p2")
            assert first["status"] == "open", first
            assert "is the principal's own sentence" in first["unresolved_note"]
            assert _told(db) == []
    assert "ended with nothing landed" not in shown[0]
    assert ("A session on this request ended with nothing landed. Its last "
            "refusal or error: msg.clarify_principal: 'in get app dir")[:60] \
        in shown[1]
    assert _row(db, "m_p2")["status"] == "answered"
    told = _told(db)
    assert len(told) == 1, told
    assert told[0]["cause_id"] == "m_p2"
    assert told[0]["from_role"] == "liaison" and told[0]["verb"] == "converse"
    assert told[0]["status"] == "open"
    assert json.loads(told[0]["body_refs"]) == ["e_p2"]
    assert [a.rendered for a in pending_replies(db)] == [told[0]["body_text"]]


def test_the_line_he_sees_holds_no_op_name_and_names_him_as_you(db):
    from rota.core.db import unread_line

    _commit(db, "s145", attempts=2)
    line = _told(db)[0]["body_text"]
    assert line == unread_line("msg.clarify_principal: " + S145_REFUSAL)
    assert line == (
        "The team could not read your request, and it did not reach the work. "
        "The last try stopped on this: 'in get app dir on windows when appdata "
        "...' is your own sentence, pasted back to you. Send the request "
        "again in other words.")
    for word in ("msg.", "clarify", "principal", "m_p2", "e_p2"):
        assert word not in line


def test_the_first_miss_keeps_the_request_open_with_the_note(db):
    _commit(db, "s145", attempts=1)
    assert _row(db, "m_p2") == {
        "status": "open",
        "unresolved_note": "msg.clarify_principal: " + S145_REFUSAL}
    assert _told(db) == []
    wake = Wake(role="liaison", kind="message", message_id="m_p2",
                detail="converse")
    assert _missed_reply_line(db, wake).startswith(
        "A session on this request ended with nothing landed.")


def test_a_request_that_lands_a_statement_is_answered_as_before(db):
    _commit(db, "s146", attempts=1, refusals=[], writes=[Write(
        "statements", "s2", {"text": E_P2, "span_entry": "e_p2",
                             "span_start": 0, "span_end": len(E_P2),
                             "status": "proposed"})])
    assert _row(db, "m_p2") == {"status": "answered", "unresolved_note": None}
    assert _told(db) == []


def test_a_request_answered_with_a_message_is_answered_as_before(db):
    _commit(db, "s147", attempts=1, messages=[OutboundMessage(
        id="m45", to_role="principal", verb="clarify", body_refs=["e_p2"],
        body_text="Which folder do you mean?", cause_id="m_p2")])
    assert _row(db, "m_p2") == {"status": "answered", "unresolved_note": None}


def test_a_barren_reply_to_a_chat_line_is_answered_as_before(db):
    """Frame 320 widens the retry to a request with no cause. A reply to a
    Liaison chat line has a cause and no page, so it keeps today's path."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_text, seq, status) VALUES ('m50','t_p1','liaison',"
               "'principal','converse','hello',50,'answered')")
    db.execute("UPDATE messages SET cause_id = 'm50' WHERE id = 'm_p2'")
    _commit(db, "s148", attempts=1)
    assert _row(db, "m_p2")["status"] == "answered"
