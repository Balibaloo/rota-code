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

from rota.core.db import (REQUEST_NOTHING, OutboundMessage, SessionResult,
                          Write, init_db,
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
    # The ask to him was refused, so the line says so and quotes nothing
    # (review 1, finding 3).
    assert line == (
        "Your request did not reach the team. The team tried to ask you about "
        "it, and the ask was refused: the question is your own sentence, "
        "pasted back to you. Reply to this line to send it again.")
    for word in ("msg.", "clarify", "principal", "m_p2", "e_p2", "appdata",
                 "'"):
        assert word not in line


def _resend(db, attempts):
    """His reply to the line, as `rota sign --say` or the walk sends it."""
    (line,) = [t for t in _told(db) if t["from_role"] == "liaison"]
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_text, seq, status, attempts) VALUES "
               "('m_p3', ?, 't_p1', 'principal', 'liaison', 'converse', ?, "
               "90, 'open', ?)", (line["id"], E_P2, attempts))


def test_his_resend_after_the_line_takes_the_retry_and_the_line(db):
    """Review 1, finding 1: his resend is a reply to the Liaison line. A
    barren session on it keeps it open, and the second miss tells him."""
    _commit(db, "s145", attempts=2)
    _resend(db, attempts=1)
    session_commit(db, SessionResult(
        session_id="s150", role="liaison", trigger_msg="m_p3",
        wake_kind="message", wake_detail="converse",
        refusals=[("msg.clarify_principal", S145_REFUSAL, "ValueError")]))
    assert _row(db, "m_p3")["status"] == "open"
    wake = Wake(role="liaison", kind="message", message_id="m_p3",
                detail="converse")
    assert _missed_reply_line(db, wake).startswith(
        "A session on this request ended with nothing landed.")
    db.execute("UPDATE messages SET attempts = 2 WHERE id = 'm_p3'")
    session_commit(db, SessionResult(
        session_id="s151", role="liaison", trigger_msg="m_p3",
        wake_kind="message", wake_detail="converse"))
    # Review 1, finding 7: the resend closes with its note and sends no
    # new line, so the chain ends.
    assert _row(db, "m_p3") == {"status": "answered",
                                "unresolved_note": REQUEST_NOTHING}
    assert [t for t in _told(db) if t["cause_id"] == "m_p3"] == []


def test_a_walk_that_replies_to_every_line_stops(db):
    """Review 1, finding 7: the walk replies to every Liaison line. A
    request that never lands sends him one line and then stops."""
    from rota.roles.principal import pending_replies

    _commit(db, "s160", attempts=2)
    asked, sent = ["m_p2"], 0
    for k in range(4):
        open_lines = [a for a in pending_replies(db)]
        if not open_lines:
            break
        for line in open_lines:
            db.execute("UPDATE messages SET status = 'answered' WHERE id = ?",
                       (line.message_id,))
            rid = f"m_r{k}"
            db.execute("INSERT INTO messages (id, cause_id, thread_id, "
                       "from_role, to_role, verb, body_text, seq, status, "
                       "attempts) VALUES (?, ?, 't_p1', 'principal', "
                       "'liaison', 'converse', ?, ?, 'open', 2)",
                       (rid, line.message_id, E_P2, 100 + k))
            sent += 1
            session_commit(db, SessionResult(
                session_id=f"s16{k + 1}", role="liaison", trigger_msg=rid,
                wake_kind="message", wake_detail="converse"))
            asked.append(rid)
    lines = [t for t in _told(db) if t["from_role"] == "liaison"]
    assert len(lines) == 1 and sent == 1, (lines, asked)
    assert pending_replies(db) == []


def test_an_empty_session_on_a_chat_reply_raises_no_alarm(db):
    """Review 1, finding 8: "Noted, I filed it." asks for nothing. Only a
    reply to the line of `unread_line` is a request."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_text, seq, status) VALUES ('m52','t_p1','liaison',"
               "'principal','converse','I filed it for you.',52,'answered')")
    db.execute("UPDATE messages SET cause_id = 'm52', body_text = 'Noted, "
               "I filed it.' WHERE id = 'm_p2'")
    _commit(db, "s170", attempts=2, refusals=[])
    assert _row(db, "m_p2")["status"] == "answered"
    assert [t for t in _told(db) if t["cause_id"] == "m_p2"] == []


def test_a_glossary_write_does_not_land_a_request(db):
    """Review 1, finding 2: only a statement or an item lands a request."""
    db.execute("INSERT INTO glossary_terms (id, term, sense_short) "
               "VALUES ('g1','app dir','a folder')")
    _commit(db, "s152", attempts=1, writes=[Write(
        "glossary_terms", "g1", {"sense_short": "the folder of the app"})])
    assert _row(db, "m_p2")["status"] == "open"
    assert _row(db, "m_p2")["unresolved_note"].startswith(
        "msg.clarify_principal: ")


def test_a_miss_with_no_fault_has_its_own_note_and_line(db):
    """Review 1, finding 5: a request owes no ruling."""
    from rota.core.db import REQUEST_NOTHING

    _commit(db, "s153", attempts=2, refusals=[])
    assert _row(db, "m_p2")["unresolved_note"] == REQUEST_NOTHING
    line = [t for t in _told(db) if t["from_role"] == "liaison"][0]["body_text"]
    assert line == ("Your request did not reach the team. The team tried "
                    "twice and landed nothing. Reply to this line to send it "
                    "again.")


def test_the_paste_refusal_names_segment_only_where_the_mode_holds_it(
        db, monkeypatch):
    """Review 1, finding 4: four Liaison modes hold the paste door and not
    brief.segment."""
    from rota.roles import api

    monkeypatch.setattr(api, "_wake_mode_tools", lambda ctx: [])
    wake = Wake(role="liaison", kind="message", message_id="m_p2",
                detail="converse")
    backend = ScriptedBackend([S145_TURN_1] * 6)
    run_session(db, wake, backend=backend, pins=Pins(model="scripted"))
    assert "pasted back to them" in backend.calls[1][1]
    assert "brief.segment, not a clarify" not in backend.calls[1][1]


def test_the_agenda_prints_the_line_under_its_own_heading(
        tmp_path, monkeypatch, capsys):
    """Review 1, finding 6: the line asks him to act."""
    from rota import cli

    monkeypatch.setattr(cli, "RUNS", tmp_path)
    conn = init_db(tmp_path / "run.db")
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('e_p2','principal',?,2)", (E_P2,))
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                 "verb, body_refs, seq, status, attempts) VALUES ('m_p2',"
                 "'t_p1','principal','liaison','converse','[\"e_p2\"]',44,"
                 "'open',2)")
    conn.commit()
    _commit(conn, "s145", attempts=2)
    conn.commit()
    conn.close()
    assert cli.main(["agenda", "run"]) == 0
    out = capsys.readouterr().out
    head = out.index("not reached the team")
    assert out.index("Your request did not reach the team.") > head
    assert "no answer needed" not in out


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
    """A reply to an ordinary Liaison chat line keeps today's path. Only a
    reply to the line of `unread_line` is a request (review 1, finding 8)."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_text, seq, status) VALUES ('m50','t_p1','liaison',"
               "'principal','converse','hello',50,'answered')")
    db.execute("UPDATE messages SET cause_id = 'm50' WHERE id = 'm_p2'")
    _commit(db, "s148", attempts=1)
    assert _row(db, "m_p2")["status"] == "answered"


def test_a_barren_reply_to_another_role_is_answered_as_before(db):
    """A principal converse whose cause is not a page and not a Liaison
    line keeps today's path."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "seq, status) VALUES ('m51','t_p1','principal','liaison',"
               "'converse',51,'answered')")
    db.execute("UPDATE messages SET cause_id = 'm51' WHERE id = 'm_p2'")
    _commit(db, "s149", attempts=1)
    assert _row(db, "m_p2")["status"] == "answered"


def test_the_agenda_lists_a_closed_resend_until_a_request_lands(
        tmp_path, monkeypatch, capsys):
    """Finding 9: his resend's second miss sends no line, so the agenda
    shows the closed request with its note. A later request that lands
    clears the list."""
    from rota import cli

    monkeypatch.setattr(cli, "RUNS", tmp_path)
    conn = init_db(tmp_path / "run.db")
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('e_p2','principal',?,2)", (E_P2,))
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                 "verb, body_refs, seq, status, attempts) VALUES ('m_p2',"
                 "'t_p1','principal','liaison','converse','[\"e_p2\"]',44,"
                 "'open',2)")
    _commit(conn, "s145", attempts=2)
    _resend(conn, attempts=2)
    conn.execute("UPDATE messages SET status = 'answered' "
                 "WHERE from_role = 'liaison'")
    session_commit(conn, SessionResult(
        session_id="s180", role="liaison", trigger_msg="m_p3",
        wake_kind="message", wake_detail="converse"))
    conn.commit()
    assert cli.main(["agenda", "run"]) == 0
    out = capsys.readouterr().out
    assert "not reached the team" in out
    assert f"[m_p3] closed with nothing landed: {REQUEST_NOTHING}" in out
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                 "verb, seq, status) VALUES ('m_p4','t_p4','principal',"
                 "'liaison','converse',200,'open')")
    session_commit(conn, SessionResult(
        session_id="s181", role="liaison", trigger_msg="m_p4",
        wake_kind="message", wake_detail="converse",
        messages=[OutboundMessage(id="m201", to_role="principal",
                                  verb="clarify", cause_id="m_p4")]))
    conn.execute("UPDATE messages SET status = 'answered' WHERE id = 'm201'")
    conn.commit()
    conn.close()
    assert cli.main(["agenda", "run"]) == 0
    assert "closed with nothing landed" not in capsys.readouterr().out
