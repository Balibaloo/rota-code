"""
Frame 303: a request item needs the principal's words as its cause.

Night 157: the Architect sent the textless `propose` m94 with refs
`["bg_1"]`. The Vision Keeper's s205 asserted `bg_1_item`, kind
`in_scope`, and the page showed the team's row under "You asked". The
rows below are copied from `.rota/clickI_night157.db` (plans/frame303-
provenance.md, sections 3, 4 and 6).
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import (OutboundMessage, SessionResult, Write, init_db,
                          session_commit)
from rota.core.predicates import Wake
from rota.core.sandbox import build
from rota.roles import prompts

# The text of `bg_1_item` in the night 157 database.
BG_1_ITEM = (
    "The software is a command-line interface toolkit called Click. It "
    "allows users to define commands and options using Python decorators, "
    "which Click uses to parse and execute inputs. The program provides a "
    "structured way to handle command-line interactions, including parsing "
    "arguments, executing functions, and handling input streams. It also "
    "includes helpers like echo and echo_json for output formatting. The "
    "software does not provide a graphical user interface, does not handle "
    "web requests, and does not manage database connections. confirm() "
    "takes a default_on_eof flag: when stdin is closed, it returns the "
    "default instead of aborting. The flag is off by default so existing "
    "callers see no change. The Python version comes from sys.version_info "
    "written as major.minor.micro.")

UNRECEIVED = ("unresolved: the woken session sent nothing and wrote no row "
              "that cites this message")


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    # bg_1 is the batch the proposal names, on the item default_on_eof.
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('default_on_eof', 'confirm() takes a "
                 "default_on_eof flag', 'in_scope', 'approved', 1, 1)")
    conn.execute("INSERT INTO batches (id, item_id, status) "
                 "VALUES ('bg_1', 'default_on_eof', 'running')")
    # m94 as night 157 holds it: no cause, no text, refs ["bg_1"].
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                 "verb, body_refs, seq, status) VALUES ('m94', 'm94', "
                 "'architect', 'vision_keeper', 'propose', ?, 97, 'open')",
                 (json.dumps(["bg_1"]),))
    conn.commit()
    return conn


def _woken(conn, trigger, verb):
    sb = build("vision_keeper", conn, mode=verb,
               allow=prompts.mode_tools("vision_keeper", verb),
               wake=Wake("vision_keeper", "message", message_id=trigger,
                         detail=verb))
    sb.ctx.trigger = trigger
    return sb


def _item_writes(sb):
    return [w for w in sb.ctx.writes if w[0] == "items"]


def test_s205_a_propose_wake_asserts_no_request_item(db):
    sb = _woken(db, "m94", "propose")
    with pytest.raises(ValueError) as err:
        sb.call("problem.assert", id="bg_1_item", kind="in_scope",
                text=BG_1_ITEM)
    msg = str(err.value)
    assert "only the principal asks for work" in msg
    assert "The cause of this call is m94, a propose from the architect" in msg
    assert 'Send msg.report_liaison with the refs ["bg_1"]' in msg
    assert not _item_writes(sb)
    # The route the refusal names lands in the same mode.
    sb.call("msg.report_liaison", refs=["bg_1"])


S2 = ("Let confirm() take a default_on_eof flag: when stdin is closed it "
      "returns the default instead of aborting.")


def test_s194_a_propose_that_refs_a_statement_asserts_no_request_item(db):
    # Night 151's rows: the principal's verdict m73 on s2, the Liaison's
    # deliver m76 to the Architect, and the Architect's propose m80 with
    # refs ["s2"]. s194 asserted confirm_default_on_eof_flag from m80
    # (frame 303, review 1, finding H1).
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_p2', 'principal', ?, 2)", (S2,))
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s2', 'e_p2', 0, 104, ?, 'ratified')",
               (S2,))
    for mid, cause, frm, to, verb in (
            ("m73", None, "principal", "liaison", "verdict"),
            ("m76", "m73", "liaison", "architect", "deliver"),
            ("m80", "m76", "architect", "vision_keeper", "propose")):
        db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
                   "to_role, verb, body_refs, seq) VALUES (?, ?, 't_p1', ?, ?, "
                   "?, ?, ?)", (mid, cause, frm, to, verb,
                                json.dumps(["s2"]), int(mid[1:])))
    db.commit()
    sb = _woken(db, "m80", "propose")
    with pytest.raises(ValueError) as err:
        sb.call("problem.assert", id="confirm_default_on_eof_flag",
                kind="in_scope", text=S2)
    msg = str(err.value)
    assert "The cause of this call is m80, a propose from the architect" in msg
    assert 'Send msg.report_liaison with the refs ["s2"]' in msg
    assert not _item_writes(sb)


def test_a_propose_that_refs_a_principal_entry_asserts_no_request_item(db):
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m155', 'principal', 'add echo_json', 1)")
    db.execute("UPDATE messages SET body_refs = ? WHERE id = 'm94'",
               (json.dumps(["bg_1", "e_m155"]),))
    db.commit()
    sb = _woken(db, "m94", "propose")
    with pytest.raises(ValueError, match="only the principal asks for work"):
        sb.call("problem.assert", id="bg_1_item", kind="in_scope",
                text=BG_1_ITEM)


def test_the_same_item_with_a_principal_message_as_its_cause_lands(db):
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
               "verb, body_refs, body_text, seq) VALUES ('m90', 'm90', "
               "'principal', 'liaison', 'converse', '[]', 'add echo_json', 90)")
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, seq) VALUES ('m91', 'm90', 'm90', "
               "'liaison', 'vision_keeper', 'deliver', '[]', 91)")
    db.commit()
    sb = _woken(db, "m91", "deliver")
    assert sb.call("problem.assert", id="bg_1_item", kind="in_scope",
                   text=BG_1_ITEM) == {"id": "bg_1_item"}
    assert _item_writes(sb)


def test_the_same_item_with_a_statement_as_its_cause_lands(db):
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e1', 'principal', 'add echo_json', 1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('st1', 'e1', 0, 13, 'add echo_json', "
               "'ratified')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
               "verb, body_refs, seq) VALUES ('m92', 'm92', 'liaison', "
               "'vision_keeper', 'deliver', ?, 92)", (json.dumps(["st1"]),))
    db.commit()
    sb = _woken(db, "m92", "deliver")
    assert sb.call("problem.assert", id="bg_1_item", kind="in_scope",
                   text=BG_1_ITEM) == {"id": "bg_1_item"}


def test_a_relay_that_refs_the_principals_entry_is_his_cause(db):
    # Night 155's m67: the Liaison relayed `["echo_json", "e_m63"]`, caused
    # by the Vision Keeper's own report m66.
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m63', 'principal', 'add echo_json', 1)")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
               "verb, body_refs, seq) VALUES ('m66', 'm66', 'vision_keeper', "
               "'liaison', 'report', '[\"bg_1\"]', 66)")
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, seq) VALUES ('m67', 'm66', 'm66', "
               "'liaison', 'vision_keeper', 'relay', ?, 67)",
               (json.dumps(["bg_1", "e_m63"]),))
    db.commit()
    sb = _woken(db, "m67", "deliver")
    assert sb.call("problem.assert", id="bg_1_item", kind="in_scope",
                   text=BG_1_ITEM) == {"id": "bg_1_item"}


def test_an_item_of_another_kind_with_a_team_cause_lands(db):
    sb = _woken(db, "m94", "propose")
    assert sb.call("problem.assert", id="no_gui", kind="out_of_scope",
                   text="The software does not provide a graphical user "
                        "interface.") == {"id": "no_gui"}


def _commit(conn, sid, writes=(), messages=()):
    session_commit(conn, SessionResult(
        session_id=sid, role="vision_keeper", trigger_msg="m94",
        wake_kind="message", writes=list(writes), messages=list(messages)))


def _status(conn, mid):
    row = conn.execute("SELECT status, unresolved_note FROM messages "
                       "WHERE id = ?", (mid,)).fetchone()
    return row["status"], row["unresolved_note"]


def test_a_report_with_the_proposals_refs_answers_the_proposal(db):
    _commit(db, "s205", messages=[OutboundMessage(
        id="m95", to_role="liaison", verb="report", body_refs=["bg_1"],
        cause_id="m94", thread_id="m94")])
    assert _status(db, "m94") == ("answered", None)


def test_an_items_write_does_not_answer_the_proposal(db):
    _commit(db, "s205", writes=[Write(
        "items", "bg_1_item", {"text": BG_1_ITEM, "kind": "in_scope",
                               "approval": "draft"})])
    assert _status(db, "m94") == ("unresolved", UNRECEIVED)
