"""
Frame 165, night 126 (2026-10-06): the door said "End the session with no
call.", and the seats sent a call anyway in 10 of 11 turns.

Interviewed in its own context, s172 read the step right and had no form to
send for it. s168 gave the refused challenge as the way to end. In the same
prompt, a refusal that named its reply, `send refs=[...]`, was taken in one
turn. So the refusal now names the reply that takes the step, with the
refused challenge's test id. These tests drive the real door and the real
loop on s172's state, with s172's turn 2 copied from the night's `turns`
table into `fixtures/night126_s172_t2.txt`.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from rota.core import sandbox
from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.runner import run_session
from rota.llm.llm import Pins, ScriptedBackend
from rota.roles import api, prompts

HERE = Path(__file__).parent / "fixtures"

CRIT = ('The callable `echo_json` accepts any Python object and writes its '
        'JSON representation to the stream using `json.dumps(obj, '
        'separators=(",", ":"))`, followed by a single newline.')
# Version 1 of inh_echo_json_01, the body that s172's wake shows.
TEST = ("def test_echo_json_compact():\n    from click.testing import "
        "CliRunner\n    from src.click.utils import echo_json\n    \n    "
        "runner = CliRunner()\n    result = runner.invoke(echo_json, "
        "['{\"key\": \"value\"}'], catch_exceptions=False)\n    assert "
        "result.exit_code == 0\n    assert result.output.strip() == "
        "'{\"key\": \"value\"}'\n    # Check for single newline at end\n    "
        "assert result.output.endswith('\\n')\n    # Check no extra "
        "newlines\n    assert result.output.count('\\n') == 1")
REFS = ["echo_json_compact", "inh_echo_json_01"]
# The night's step, then the reply that takes it. Written out, so a new
# wording turns these red.
ENDS = ("End the session with no call. Your whole next reply is this one "
        "line, and no TOOL: line: Nothing more is owed on inh_echo_json_01 "
        "in this session.")
REASON = ("you sent challenge to tester on exactly these refs already (m76, "
          "then m77), and the Tester answered neither and did not change the "
          "test. " + ENDS)
REFUSED = "ERROR msg.challenge_tester: " + REASON
ONE_LINE = "Nothing more is owed on inh_echo_json_01 in this session."
# The errors of every nudge that can answer a reply with no call.
NUDGES = ("ended a tick with nothing done", "named an act and did not "
          "perform it", "wrote code into its reply",
          "wrote a test into its reply")


def _turn2() -> str:
    return (HERE / "night126_s172_t2.txt").read_bytes().decode("utf-8")


def _night(path, root):
    """Night 126's rows at s172: the challenges m76 and m77 closed with no
    answer from the Tester, the Architect's answer m83 to m76, and the
    escalation m78 closed, so the door offers no escalation."""
    conn = init_db(path)
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('echo_json', 'Add an echo_json(obj) helper "
                 "next to echo that prints an object as compact JSON on one "
                 "line, followed by a newline.', 'in_scope', 'approved', 3, "
                 "3)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk_1', 'echo_json', 'add echo_json')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('echo_json_compact', 'tk_1', ?)", (CRIT,))
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit, "
                 "worktree) VALUES ('bg_1', 'echo_json', 'running', "
                 "'10e3fa7', ?)", (str(root),))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_1', 'tk_1')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body, "
                 "version) VALUES ('inh_echo_json_01', 'bg_1', "
                 "'echo_json_compact', "
                 "'tests/test_utils/test_echo_json_compact.py', ?, 1)", (TEST,))
    for mid, seq, frm, to, verb, cause in (
            ("m76", 77, "developer", "tester", "challenge", None),
            ("m77", 78, "developer", "tester", "challenge", None),
            ("m78", 79, "developer", "architect", "escalate", None),
            ("m83", 84, "architect", "developer", "answer", "m76")):
        conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                     "verb, body_refs, seq, status, cause_id) VALUES "
                     "(?, ?, ?, ?, ?, ?, ?, 'answered', ?)",
                     (mid, cause or mid, frm, to, verb, json.dumps(REFS), seq,
                      cause))
    conn.commit()
    return conn


@pytest.fixture
def root(tmp_path):
    wt = tmp_path / "wt"
    wt.mkdir()
    return wt


def _s172(conn, script: list[str], kind: str = "tick:exhausted"):
    backend = ScriptedBackend(script)
    out = run_session(conn, Wake("developer", kind, refs=("bg_1",),
                                 detail="attempt 10 of 10"),
                      backend=backend, pins=Pins(model="scripted"))
    return out, backend


def test_the_step_on_s172s_state_names_the_test(tmp_path, root):
    """s172's turn 2 meets the door. The step now names the reply that
    takes it, with the test id of the refused challenge."""
    conn = _night(tmp_path / "rota.db", root)
    out, backend = _s172(conn, [_turn2(), ONE_LINE, "Done."])
    _, user = backend.calls[1]
    assert user.endswith(_turn2() + "\n\n" + REFUSED), user[-700:]


@pytest.mark.parametrize("kind", ["tick:exhausted", "tick:tests_failing"])
def test_the_one_line_reply_ends_the_session_with_no_nudge(tmp_path, root,
                                                           kind):
    """The reply that the step names ends the session. No nudge of any kind
    answers it: s172's mode holds no `code.write`, and s168's mode holds
    it, so the fence nudge and the named-act nudge are both in reach."""
    conn = _night(tmp_path / "rota.db", root)
    out, backend = _s172(conn, [_turn2(), ONE_LINE, "Done."], kind=kind)
    assert len(backend.calls) == 2, "the one-line reply is the end"
    _, user = backend.calls[1]
    assert user.endswith(ENDS)
    assert not [e for e in out.errors if e.startswith(NUDGES)], out.errors
    assert out.errors == ["msg.challenge_tester: " + REASON]
    assert out.committed, out.errors


def test_the_step_is_still_an_end_refusal(tmp_path, root):
    """The door raises the step as `api.EndRefusal`, and frame 144's fact
    check admits the test id that the sentence names."""
    conn = _night(tmp_path / "rota.db", root)
    sb = sandbox.build("developer", conn, batch_id="bg_1", mode="exhausted",
                       allow=prompts.mode_tools("developer", "exhausted"))
    with pytest.raises(api.EndRefusal) as exc:
        sb.call("msg.challenge_tester", refs=REFS,
                quotes=[CRIT, "result = runner.invoke(echo_json, "
                              "['{\"key\": \"value\"}'], "
                              "catch_exceptions=False)"])
    assert str(exc.value) == REASON
    rows = [r for r in sandbox.check_facts(sb, sb.ctx.facts)
            if r["kind"] == "row" and r["value"] == "inh_echo_json_01"]
    assert rows and all(r["ok"] for r in rows), rows


# The recorded cases, run with a scripted model. The case runner's keys
# `replies: [{file: ...}]` and `no_call:` are frame 165's.

CASE_ID = "L1-DV-end-the-session-when-the-door-says-end"


class _Seen:
    """A scripted model that keeps each prompt it gets."""

    name = "seen"
    misses = 0

    def __init__(self, replies):
        self.replies, self.users = list(replies), []

    def complete(self, system, user, pins, tools=None):
        from rota.llm.llm import Completion
        self.users.append(user)
        return Completion(text=self.replies.pop(0) if self.replies else "",
                          pins=pins, backend="seen")


def _case(case_id, run_no=1):
    from rota import paths
    from rota.testkit import fixtures
    case = next(c for c in fixtures.load_case(paths.CASES / "l1_developer.yaml")
                if c["id"] == case_id)
    return fixtures.for_run(case, run_no)


def _run_case(problem, backend, tmp_path):
    from rota.testkit import fixtures
    return fixtures.run_case(problem, tmp_path / "c.db", backend,
                             pins=Pins(model="scripted"),
                             instructions=fixtures.instructions_for(problem))


def test_the_case_serves_the_nights_reply_and_the_real_door(tmp_path):
    """The case's turn 1 is the fixture file's bytes, and the model gets the
    real door's refusal with the form. The one line passes the case."""
    model = _Seen([ONE_LINE])
    r = _run_case(_case(CASE_ID), model, tmp_path)
    assert r.passed, r.problems
    assert r.outcome.completions[0] == _turn2()
    assert len(model.users) == 1
    last = model.users[0].rstrip().splitlines()[-1]
    assert last.startswith("ERROR msg.challenge_tester: you sent challenge to "
                           "tester on exactly these refs already (m_")
    assert last.endswith("and the Tester answered neither and did not change "
                         "the test. " + ENDS), last


@pytest.mark.parametrize("reply, problem", [
    (None, "expected a reply with no call; the reply holds a TOOL: line"),
    ("I am done.\nmsg.challenge_tester(refs=['echo_json_compact', "
     "'inh_echo_json_01'], quotes=['x', 'y'])",
     "expected a reply with no call; the reply holds a call"),
])
def test_a_reply_with_a_call_fails_the_case(tmp_path, reply, problem):
    r = _run_case(_case(CASE_ID), _Seen([reply or _turn2()]), tmp_path)
    assert not r.passed
    assert problem in r.problems, r.problems


# The review of 04407eff, finding 2: the form on other shapes of refs.
@pytest.mark.parametrize("refs, on", [
    (["echo_json_compact", "inh_echo_json_01", "inh_echo_json_02"],
     "inh_echo_json_01, inh_echo_json_02"),
    (["echo_json_compact"], "echo_json_compact"),
    (["echo_json_compact", "inh_echo_json_01", "inh_echo_json_01"],
     "inh_echo_json_01"),
], ids=["two tests", "no test", "a repeated ref"])
def test_the_form_names_the_tests_of_each_shape_of_refs(tmp_path, root,
                                                        monkeypatch, refs,
                                                        on):
    """Two tests are both named. Refs with no test name every ref. A
    repeated ref is named once. Each id is a fact whose site is the
    function that names it."""
    conn = _night(tmp_path / "rota.db", root)
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body, "
                 "version) VALUES ('inh_echo_json_02', 'bg_1', "
                 "'echo_json_compact', 'tests/test_utils/test_two.py', "
                 "'def test_two():\n    assert True', 1)")
    conn.commit()
    sb = sandbox.build("developer", conn, batch_id="bg_1", mode="exhausted",
                       allow=prompts.mode_tools("developer", "exhausted"))
    # The door offers no escalation, so the step is the end.
    monkeypatch.setattr(sandbox, "_escalation_admitted", lambda ctx, r: False)
    del sb.ctx.facts[:]
    said = sandbox._escalation_or_step(sb.ctx, refs, "A fact.",
                                       sandbox.END_STEP)
    assert said == ("A fact. End the session with no call. Your whole next "
                    "reply is this one line, and no TOOL: line: Nothing more "
                    f"is owed on {on} in this session.")
    assert [f.value for f in sb.ctx.facts] == on.split(", ")
    assert all(f.site.endswith(" in _end_form") for f in sb.ctx.facts), \
        [f.site for f in sb.ctx.facts]
