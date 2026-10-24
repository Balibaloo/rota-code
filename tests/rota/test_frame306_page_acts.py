"""Frame 306, pass 1b: his drops and his added line on a criteria page land.

Night 163's m111 listed the criteria of `clear()`. His reply m112 said to
delete line 5, change line 6, delete line 7 and add a line. Six rounds
changed nothing: no op retired a criterion, and no route added one. The rows
below are the night's, copied from `.rota/clickI_night163.db`.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import SessionResult, init_db, session_commit
from rota.core.runner import _as_write, _page_act_lines, _wake_allow
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles import prompts
from rota.roles.principal import request_rows

ITEM = "clear_returns_bool"
TICKET = "tk_1_clear_returns_bool"
CRITERIA = {
    "c1_clear_terminal": "clear() returns True if the screen was cleared, "
                         "False otherwise.",
    "c1_clear_terminal_check": "clear() returns True if and only if the "
                               "current stdout is a terminal.",
    "c2_non_terminal_false": "clear() returns False when stdout is not a "
                             "terminal.",
    "c3_no_terminal_true": "clear() returns False when stdout is not a "
                           "terminal.",
    "c3_terminal_check": "clear() determines terminal status by inspecting "
                         "the underlying stream object passed to it.",
    "c3_terminal_failure_true": "clear() returns False when the clear "
                                "operation fails, provided no exception is "
                                "raised.",
    "c3_terminal_true": "clear() returns True when the current stdout is a "
                        "terminal and the clear operation succeeds.",
}
PAGE = [ITEM, *CRITERIA, "bg_2"]
WORDS = ("Please delete line 5, because it repeats line 4. Change line 6 to "
         "say that clear() checks the current stdout, since nothing is passed "
         "to it, and delete line 7, since a failed clear is not part of what I "
         "asked for. Also add a line that says the output stays exactly the "
         "same as today, and the rest is fine.")
CONTESTED = ["c3_no_terminal_true", "c3_terminal_check",
             "c3_terminal_failure_true"]
VERDICT = {"c3_no_terminal_true": "contest", "c3_terminal_check": "revise",
           "c3_terminal_failure_true": "contest"}
ADDED = "the output stays exactly the same as today"


def _message(conn, mid, cause, sender, to, verb, refs, seq, text=None):
    conn.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
                 "to_role, verb, body_refs, body_text, seq) VALUES "
                 "(?, ?, 'm111', ?, ?, ?, ?, ?, ?)",
                 (mid, cause, sender, to, verb, json.dumps(refs), text, seq))


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES (?, 'clear() returns True when it cleared "
                 "the screen and False when stdout is not a terminal.', "
                 "'in_scope', 'approved', 1, 1)", (ITEM,))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, "
                 "'clear returns a bool')", (TICKET, ITEM))
    for cid, text in CRITERIA.items():
        conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                     "(?, ?, ?)", (cid, TICKET, text))
    refs = ["bg_2", *CRITERIA, ITEM]
    _message(conn, "m111", None, "liaison", "principal", "present", refs, 111)
    _message(conn, "m112", "m111", "principal", "liaison", "converse", refs,
             112, WORDS)
    _message(conn, "m113", "m111", "principal", "liaison", "verdict",
             CONTESTED, 113)
    _message(conn, "m114", "m113", "liaison", "terminologist", "relay",
             CONTESTED, 114)
    conn.execute("INSERT INTO config (key, value) VALUES ('verdict:m113', ?)",
                 (json.dumps(VERDICT),))
    conn.execute("INSERT INTO config (key, value) VALUES ('order:m112', ?)",
                 (json.dumps(PAGE),))
    per_item = {r: VERDICT.get(r, "approve") for r in PAGE}
    conn.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
                 "status, verdict_id, texts) VALUES ('r_fae8c0a559', 'm111', "
                 "'m112', ?, ?, 'landed', 'm113', ?)",
                 (json.dumps(per_item), WORDS,
                  json.dumps({c: CRITERIA[c] for c in CONTESTED})))
    conn.commit()
    return conn


def _repair(conn):
    sb = build("terminologist", conn, mode="criterion_repair",
               session_id="s226", allow=_wake_allow(_wake(), conn))
    sb.ctx.trigger = "m114"
    return sb


def _wake():
    return Wake("terminologist", "message", message_id="m114",
                refs=tuple(CONTESTED), detail="relay")


def _commit(conn, sb, sid):
    session_commit(conn, SessionResult(
        session_id=sid, role="terminologist",
        writes=[_as_write(w) for w in sb.ctx.writes]))


def test_his_drop_of_lines_5_and_7_retires_both_rows(db):
    sb = _repair(db)
    sb.call("criteria.retire", id="c3_no_terminal_true")
    sb.call("criteria.retire", id="c3_terminal_failure_true")
    _commit(db, sb, "s226")
    rows = dict(db.execute("SELECT id, retired_by FROM criteria").fetchall())
    assert rows["c3_no_terminal_true"] == "r_fae8c0a559"
    assert rows["c3_terminal_failure_true"] == "r_fae8c0a559"
    assert rows["c3_terminal_check"] is None, "line 6 is a rewrite, no drop"
    shown = request_rows(db, [ITEM])
    assert "c3_no_terminal_true" not in shown
    assert "c3_terminal_failure_true" not in shown
    assert "c3_terminal_check" in shown


def test_a_criterion_he_did_not_drop_is_not_retired(db):
    sb = _repair(db)
    with pytest.raises(ValueError, match="no ruling of the principal drops"):
        sb.call("criteria.retire", id="c3_terminal_check")
    with pytest.raises(ValueError, match="no ruling of the principal drops"):
        sb.call("criteria.retire", id="c1_clear_terminal")


def test_six_criteria_with_one_retired_admit_a_seventh(db):
    """Six rows of which one is retired are five live criteria. The cap
    refuses a seventh live criterion, so it still counts live rows only."""
    db.execute("DELETE FROM criteria WHERE id = 'c3_terminal_true'")
    db.execute("UPDATE criteria SET retired_by = 'r_fae8c0a559' "
               "WHERE id = 'c3_no_terminal_true'")
    db.commit()
    live = db.execute("SELECT COUNT(*) FROM criteria WHERE ticket_id = ? AND "
                      "retired_by IS NULL", (TICKET,)).fetchone()[0]
    assert live == 5
    sb = build("terminologist", db, mode="criteria",
               allow=prompts.mode_tools("terminologist", "criteria"))
    sb.call("criteria.specify", id="c8_output_same", ticket_id=TICKET,
            text="The output of clear() stays exactly the same as today.")


def test_the_relay_wake_offers_specify_and_names_the_added_sentence(db):
    allow = _wake_allow(_wake(), db)
    assert "criteria.specify" in allow
    assert "criteria.retire" in allow
    lines = "\n".join(_page_act_lines(_wake(), db))
    assert ADDED in lines and TICKET in lines
    assert "c3_no_terminal_true" in lines and "c3_terminal_failure_true" in lines


def test_a_relay_with_no_drop_and_no_added_line_keeps_the_mode_tools(db):
    words = "Change line 6 to say that clear() checks the current stdout."
    db.execute("UPDATE rulings SET words = ?", (words,))
    db.commit()
    assert _wake_allow(_wake(), db) == prompts.mode_tools(
        "terminologist", "criterion_repair")
    assert _page_act_lines(_wake(), db) == []
