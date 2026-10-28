"""
A held tail that holds a `ToolError` reaches the stand-by path.

Night 173, s130 (`plans/night173-read.md`, W11): the Tester's turn 5 echoed
its prompt's working set after a fresh read. The hold kept the tail of that
turn, and the tail held the parse error of "`TOOL:` is a literal marker".
Turns 6 and 7 held no call, so the runner ran the held calls. It read
`.name` on the `ToolError` and the session died on "'ToolError' object has
no attribute 'name'". The stand-by path now answers a held parse error as
the turn loop answers one: an `ERROR raw: reason` line, and the reason in the
runner's account of the session.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.runner import run_session
from rota.llm import toolcheck, toolproto
from rota.llm.llm import Completion, Pins, ScriptedBackend

CRIT = ("When get_app_dir is called on Windows with roaming=False and "
        "LOCALAPPDATA is set, it must return the value of LOCALAPPDATA.")
# s130's turn 5, cut to the lines that matter: a fresh read, a write that the
# read holds, and the prompt line that the parser reads as a call.
TURN_5 = "\n".join([
    "TOOL: code.source(path='src/click/utils.py')",
    "TOOL: msg.answer_developer(refs=['c_4', 'tst_c4'], quotes=['the path'])",
    "Call one per line. `TOOL:` is a literal marker — write those five "
    "characters, then the function name from the list above.",
])
NO_CALL = ("I think the developer is wrong: the test should assert the "
           "appended path, because that's what the function does.")


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1', 'get_app_dir reads LOCALAPPDATA', "
                 "'in_scope', 'approved', 1, 1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk_1', 'i1', 'the LOCALAPPDATA branch')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c_4', 'tk_1', ?)", (CRIT,))
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('bg_1', 'i1', 'running', 'a7045de')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_1', 'tk_1')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body, "
                 "version) VALUES ('tst_c4', 'bg_1', 'c_4', "
                 "'tests/test_utils/test_get_app_dir_local.py', "
                 "'def test_x():\n    assert True\n', 1)")
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                 "verb, body_refs, seq, status) VALUES ('m40', 'm40', "
                 "'developer', 'tester', 'challenge', ?, 40, 'open')",
                 (json.dumps(["c_4", "tst_c4"]),))
    conn.commit()
    return conn


def _tester(db, script: list[str]):
    backend = ScriptedBackend(script)
    out = run_session(db, Wake("tester", "message", message_id="m40",
                               detail="challenge"),
                      backend=backend, pins=Pins(model="scripted"))
    return out, [c[1] for c in backend.calls]


def test_the_held_tail_of_s130_holds_a_tool_error():
    """The shape itself: the parser reads the prompt line as a `ToolError`,
    and it comes after the write that the read holds."""
    calls = toolproto.extract_lenient(
        TURN_5, {"code.source", "msg.answer_developer"})
    assert [type(c).__name__ for c in calls] == [
        "ToolCall", "ToolCall", "ToolError"]
    assert calls[2].reason == "no function name after TOOL:"


def test_s130_a_held_tool_error_does_not_fail_the_session(db):
    """Before the fix the stand-by path read `hc.name` and the session
    failed. Now the hold step answers the parse error on the next turn, and
    the stand-by path never meets it."""
    out, prompts = _tester(db, [TURN_5, NO_CALL, NO_CALL, NO_CALL, NO_CALL])
    failed = [e for e in out.errors if e.startswith("session failed:")]
    assert not failed, failed
    assert out.errors.count("no function name after TOOL:") == 1
    turn_2 = _results(prompts[1])
    assert "ERROR TOOL:` is a literal marker" in turn_2
    assert ": no function name after TOOL:" in turn_2
    for p in prompts:
        if "The calls you stood by ran" in p:
            assert "literal marker" not in p.rsplit("The calls you stood by", 1)[1]


def _results(prompt: str) -> str:
    """The results of turn 1: the text after the last line of `TURN_5`."""
    return prompt.rsplit("from the list above.", 1)[-1]


def test_s130_the_hold_note_names_no_parse_error_to_resend(db):
    """The W11 review, finding 2: the turn 2 note told the seat to send the
    prompt line again. The note now names the held write alone."""
    _, prompts = _tester(db, [TURN_5, NO_CALL, NO_CALL, NO_CALL, NO_CALL])
    note = next(ln for ln in _results(prompts[1]).splitlines()
                if ln.startswith("NOT RUN"))
    assert "msg.answer_developer" in note
    assert "literal marker" not in note
    assert "TOOL:`" not in note


def test_s130_a_later_call_keeps_the_parse_error(db):
    """The W11 review, finding 3: a turn with a call cleared the held tail,
    and the parse error went with no line. It is answered at the hold now."""
    out, _ = _tester(db, [TURN_5, "TOOL: tests.consult()", NO_CALL, NO_CALL])
    assert "no function name after TOOL:" in out.errors


INVENTED = "\n".join([
    "TOOL: tests.consult()",
    "OK tests.consult -> nothing to consult",
    "TOOL: msg.answer_developer(refs=['c_4', 'tst_c4'], quotes=['the path'])",
    "Call one per line. `TOOL:` is a literal marker.",
])


def test_a_dropped_list_after_an_invented_result_holds_real_calls_only(db):
    """The W11 review, p2-2: the calls after an invented result are dropped
    and named. A parse error among them is answered, never named to resend."""
    out, prompts = _tester(db, [INVENTED, NO_CALL, NO_CALL, NO_CALL])
    assert "wrote its own tool results" in out.errors, out.errors
    assert "no function name after TOOL:" in out.errors
    turn_2 = prompts[1].rsplit("is a literal marker.", 1)[-1]
    assert ": no function name after TOOL:" in turn_2
    note = next(ln for ln in turn_2.splitlines()
                if ln.startswith("NOT RUN, because you wrote a tool result"))
    assert "msg.answer_developer" in note
    assert "TOOL:`" not in note


def test_s130_the_night_print_counts_the_ending(db):
    """The W11 review, finding 1: the night print showed only the wake line.
    The failures section counts the session and names the reason."""
    from rota.tools import nightreport

    _tester(db, [TURN_5, NO_CALL, NO_CALL, NO_CALL, NO_CALL])
    lines = nightreport.build(db)
    at = lines.index("== failures")
    section = lines[at + 1:lines.index("== open faults")]
    counted = [ln for ln in section if ln.startswith(
        "committed sessions that ended with refusals in the runner's account: 1,")]
    assert counted, section
    assert counted[0].endswith("parse errors 1 lines in 1 sessions"), counted


def test_s130_the_account_turn_records_the_refusal(db):
    """The rule for a committed session: the runner's account is its last
    turn, `SESSION ENDED`, and the night report reads that prefix
    (`nightreport.RUNNER_PREFIXES`). The parse error is a line of it."""
    from rota.tools import nightreport

    out, _ = _tester(db, [TURN_5, NO_CALL, NO_CALL, NO_CALL, NO_CALL])
    row = db.execute("SELECT id, committed FROM sessions WHERE role='tester' "
                     "ORDER BY seq DESC LIMIT 1").fetchone()
    assert row[1] == 1, out.errors
    last = db.execute("SELECT completion FROM turns WHERE session_id = ? "
                      "ORDER BY seq DESC LIMIT 1", (row[0],)).fetchone()[0]
    assert last.startswith(nightreport.RUNNER_PREFIXES)
    assert "SESSION FAILED" not in last
    assert "- no function name after TOOL:" in last


class _Echo:
    """A backend whose plain reply holds a parse error before the call."""

    def __init__(self, text: str):
        self.text = text

    def complete(self, system, user, pins, tools=None):
        if tools is not None:
            raise TypeError("no tools")
        return Completion(text=self.text, pins=pins)


def test_toolcheck_reads_past_a_tool_error():
    """`toolcheck.check` read `.name` on every parsed line, so a reply with a
    parse error before its `ledger.log` line failed the probe."""
    text = ("TOOL: `x`\nTOOL: ledger.log(about_ref='i1', about_table='items', "
            "assumption='a', kind='default')")
    assert isinstance(toolproto.extract(text)[0], toolproto.ToolError)
    result = toolcheck.check(_Echo(text), Pins(model="scripted"))
    assert result.tool_line
