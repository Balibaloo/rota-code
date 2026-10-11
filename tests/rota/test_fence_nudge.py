"""
Frame 152, night 125 (2026-10-05): a Tester wrote its repair in a fence.

The Tester s147 and s149, each woken by a challenge of inh_echo_json_01,
wrote the repaired test in a fenced block and sent no `tests.encode`. Each
session closed with nothing written. The runner's fence nudge needs
`code.write`, so it never fired for a Tester. These tests drive the real
loop with the seats' own replies, copied from the night's `turns` table
into `fixtures/night125_*.txt`.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.runner import _body_literal, run_session
from rota.llm import toolproto
from rota.llm.llm import Completion, Pins, ScriptedBackend

HERE = Path(__file__).parent / "fixtures"

CRIT = ('The callable `echo_json` accepts any Python object and writes its '
        'JSON representation to the stream using `json.dumps(obj, '
        'separators=(",", ":"))`, followed by a single newline.')
# Version 2 of inh_echo_json_01, the body that s149's wake shows.
TEST = ('def test_echo_json_compact():\n    import sys\n    from io import '
        'StringIO\n    from src.click.utils import echo_json\n    \n    '
        'old_stdout = sys.stdout\n    sys.stdout = StringIO()\n    try:\n'
        '        echo_json({"key": "value"})\n    finally:\n        '
        'sys.stdout = old_stdout\n    \n    output = sys.stdout.getvalue()\n'
        '    assert output.strip() == "{\\"key\\": \\"value\\"}"\n    # Check '
        'for single newline at end\n    assert output.endswith("\\n")\n    '
        '# Check no extra newlines\n    assert output.count("\\n") == 1')
# The runner's mark. Night 126's s154 read the sentence with no mark as the
# tail of its own reply (frame 152's interview, answers 2 and 9).
MARK = "ERROR no call: "
# The sentence up to the body. Pass 3 puts the body of the seat's own fence
# after `body=`.
HEAD = (MARK + "You wrote a test into your reply, and a reply is not a stored "
        "test -- nothing landed. Send it as a call: tests.encode("
        "id='inh_echo_json_01', criterion_id='echo_json_compact', "
        "path='tests/test_utils/test_echo_json_compact.py', body=")
NUDGE = HEAD + "'...')."
# A fence with no test function is code. The sentence offers the end, as the
# named-act nudge does (frame 152's review of 5e0dd71, F3).
CODE = (NUDGE.replace("You wrote a test", "You wrote code")[:-1]
        + ", or end by saying nothing is owed.")
# The Developer's sentence before pass 3, byte for byte. Pass 3 adds the mark
# and nothing else.
DEVELOPER_BEFORE = ("You wrote code into your reply, and a reply is not a file "
                    "-- nothing landed. Send it as a call: "
                    "code.write(path='...', text='...') and then code.commit.")
DEVELOPER = MARK + DEVELOPER_BEFORE


def _reply(name: str, night: int = 125) -> str:
    return (HERE / f"night{night}_{name}.txt").read_bytes().decode("utf-8")


def _fence(reply: str) -> str:
    """The text of the reply's last whole fence that holds a test."""
    return [b for b in re.findall(r"```[^\n]*\n(.*?)```", reply, re.S)
            if "def test" in b][-1]


def _sentence(user: str) -> str:
    """The runner's sentence, from its mark to the end of the prompt."""
    return user[user.rindex(MARK):]


def _encode_of(sentence: str) -> str:
    """The encode call of the sentence, as the seat copies it."""
    call = sentence.split("Send it as a call: ", 1)[1]
    call = call[:call.rindex(")") + 1].split(" and then ")[-1]
    return f"{toolproto.MARKER} {call}"


def _signatures() -> dict:
    """The parser's signature set for `tests.encode`, as `_param_sets` builds
    it from the bound function. The runner parses with it, so the tests do
    too (frame 152's review of 1cfbe704, finding 4)."""
    import inspect

    from rota.roles import api
    params = {n: p for n, p in inspect.signature(api.tests_encode)
              .parameters.items() if n != "ctx"}
    req = {n for n, p in params.items() if p.default is inspect.Parameter.empty}
    return {"tests.encode": (req, set(params))}


SIGS = _signatures()


def _parsed(sentence: str) -> dict:
    """The arguments that the real parser reads from the sentence's call."""
    calls = toolproto.extract_lenient(_encode_of(sentence), {"tests.encode"},
                                      SIGS)
    assert len(calls) == 1 and isinstance(calls[0], toolproto.ToolCall), calls
    return calls[0].args


@pytest.fixture
def db(tmp_path):
    return _night(tmp_path / "rota.db")


def _night(path):
    """Night 125's rows for m68 and m69: one criterion, its test at version
    2, and the Developer's challenge on both."""
    conn = init_db(path)
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1', 'print an object as compact JSON', "
                 "'in_scope', 'approved', 1, 1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk_1', 'i1', 'add echo_json')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('echo_json_compact', 'tk_1', ?)", (CRIT,))
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('bg_1', 'i1', 'running', 'a7045de')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_1', 'tk_1')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body, "
                 "version) VALUES ('inh_echo_json_01', 'bg_1', "
                 "'echo_json_compact', "
                 "'tests/test_utils/test_echo_json_compact.py', ?, 2)", (TEST,))
    # The night's row that covers the test's literal, so that the assumption
    # door admits the repair as it admitted version 2.
    conn.execute("INSERT INTO ledger (id, about_ref, about_table, "
                 "default_taken, status, author, version) VALUES "
                 "('l_a9da008d82', 'echo_json_compact', 'criteria', ?, "
                 "'resolved', 'tester', 2)",
                 ("the test assumes input string '{\"key\": \"value\"}' where "
                  "the material is silent",))
    for mid, seq in (("m68", 68), ("m69", 69)):
        conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                     "verb, body_refs, seq, status) VALUES (?, ?, 'developer', "
                     "'tester', 'challenge', ?, ?, 'open')",
                     (mid, mid, json.dumps(["echo_json_compact",
                                            "inh_echo_json_01"]), seq))
    conn.commit()
    return conn


def _tester(db, mid: str, script: list[str]):
    backend = ScriptedBackend(script)
    out = run_session(db, Wake("tester", "message", message_id=mid,
                               detail="challenge"),
                      backend=backend, pins=Pins(model="scripted"))
    return out, backend


def test_s149s_fenced_repair_is_told_to_send_tests_encode(db):
    """s149 closed after 1 turn with no reply from the runner. Now the
    nudge names the call with the challenged test's values, once, and the
    same fenced reply again is the session's real stop."""
    reply = _reply("s149_t1")
    out, backend = _tester(db, "m69", [reply, reply, "Done."])
    assert out.errors.count("wrote a test into its reply") == 1
    assert len(backend.calls) == 2, "the second fenced reply is the stop"
    _, user = backend.calls[1]
    assert _sentence(user).startswith(HEAD) and user.endswith("''').")
    assert _parsed(_sentence(user))["body"] == _fence(reply)
    assert "named an act and did not perform it" not in out.errors


@pytest.mark.parametrize("name, night", [("s149_t1", 125), ("s154_t1", 126)])
def test_the_call_the_nudge_names_lands_its_body_unchanged(db, name, night):
    """The seat copies the call of the sentence as it stands. The doors
    admit it, and the stored body is the text of the seat's fence."""
    reply = _reply(name, night)
    out, backend = _tester(db, "m69", [reply, ""])
    call = _encode_of(_sentence(backend.calls[1][1]))
    assert "'...'" not in call

    out, backend = _tester(db, "m69", [reply, call, ""])
    assert out.committed, out.errors
    assert not [e for e in out.errors if e.startswith("tests.encode")], out.errors
    row = db.execute("SELECT body, version FROM tests "
                     "WHERE id = 'inh_echo_json_01'").fetchone()
    assert row["body"] == _fence(reply) and row["version"] > 2


def test_s147s_fenced_repair_meets_the_test_nudge_before_the_named_act(db):
    """s147 met the named-act nudge at turn 1 and closed at turn 2. Now
    turn 1 meets the test nudge, and turn 2, fenced again, is the stop."""
    out, backend = _tester(db, "m68", [_reply("s147_t1"), _reply("s147_t2"),
                                       "Done."])
    assert out.errors.count("wrote a test into its reply") == 1
    assert len(backend.calls) == 2, "the second fenced reply is the stop"
    _, user = backend.calls[1]
    assert _sentence(user).startswith(HEAD)
    assert _parsed(_sentence(user))["body"] == _fence(_reply("s147_t1"))
    assert "You said what you would do" not in user
    assert "named an act and did not perform it" not in out.errors


def _answer(db, refs=("echo_json_compact",)):
    """A Terminologist's answer to the Tester. Its refs name the criterion."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m90', 'm90', 'terminologist', "
               "'tester', 'answer', ?, 90, 'open')", (json.dumps(list(refs)),))
    db.commit()
    return Wake("tester", "message", message_id="m90", detail="answer")


def _run(db, wake, script, batch="bg_1"):
    backend = ScriptedBackend(script)
    out = run_session(db, wake, backend=backend, pins=Pins(model="scripted"),
                      batch_id=batch)
    return out, backend


def _call_of(sentence: str, **values) -> str:
    """The call a seat copies from the sentence, with its own values."""
    call = sentence.split("Send it as a call: ", 1)[1].rstrip(".")
    for key, value in values.items():
        call = call.replace(f"{key}='...'", f"{key}={value!r}")
    return "TOOL: " + call.replace(" and then ", "\nTOOL: ")


def test_an_answer_naming_a_criterion_with_no_test_names_the_criterion(db):
    """A wake whose refs name one criterion and no test keeps '...' for the
    id and the path. The second fenced reply is the stop."""
    db.execute("DELETE FROM tests")
    db.commit()
    out, backend = _run(db, _answer(db), [_reply("s149_t1")] * 2)
    assert out.errors.count("wrote a test into its reply") == 1
    _, user = backend.calls[1]
    assert ("Send it as a call: tests.encode(id='...', "
            "criterion_id='echo_json_compact', path='...', body='''def test"
            in _sentence(user))
    assert len(backend.calls) == 2


def test_an_answer_naming_a_criterion_with_its_one_test_names_the_test(db):
    """The review of 9684e3c, G: the nudge printed id='...', and a new id
    stored a second test of the criterion."""
    out, backend = _run(db, _answer(db), [_reply("s149_t1"), ""])
    _, user = backend.calls[1]
    assert _sentence(user).startswith(HEAD)


def test_the_real_tests_missing_tick_names_the_triage_and_both_land(db, tmp_path):
    """The review of 9684e3c, F: the tick carries the batch, and the encode
    alone is refused for a criterion with no triage in the session. The
    sentence names both calls, and the calls copied from it land."""
    db.execute("DELETE FROM tests")
    db.commit()
    tick = Wake("tester", "tick:tests_missing", refs=("bg_1",),
                detail="without a test: echo_json_compact")
    reply = _reply("s149_t1")
    out, backend = _run(db, tick, [reply, reply])
    _, user = backend.calls[1]
    sentence = _sentence(user)
    assert sentence.startswith(
        MARK + "You wrote a test into your reply, and a reply is not a stored "
        "test -- nothing landed. Send it as a call: tests.triage(criterion_id="
        "'...', verdict='encodable') and then tests.encode(id='...', "
        "criterion_id='...', path='...', body='''def test")
    assert _parsed(sentence)["body"] == _fence(reply)
    # The second fenced reply is the stop, and the owed-call nudge does not
    # answer it.
    assert len(backend.calls) == 2
    assert "ended a tick with nothing done" not in out.errors

    db = _night(tmp_path / "second.db")
    db.execute("DELETE FROM tests")
    db.commit()
    call = _call_of(sentence, criterion_id="echo_json_compact", id="t_new",
                    path="tests/test_utils/test_echo_json_new.py")
    out, backend = _run(db, tick, [reply, call, ""])
    assert out.committed, out.errors
    assert [e for e in out.errors if not e.startswith("wrote")] == []
    row = db.execute("SELECT criterion_id FROM tests WHERE id = 't_new'").fetchone()
    assert row and row["criterion_id"] == "echo_json_compact"


def test_a_fence_with_no_test_function_is_code_in_the_sentence(db):
    """The review of 9684e3c, point 4: a fence that quotes an error is not
    a test."""
    reply = ("The run failed with this error:\n```\nAttributeError: "
             "'EncodedFile' object has no attribute 'getvalue'\n```\n"
             "The test reads the buffer too late.")
    out, backend = _tester(db, "m69", [reply, ""])
    _, user = backend.calls[1]
    assert user.endswith(CODE)
    # A test function named in the prose is not a test in a fence.
    reply = "The test def test_echo_json_compact() fails.\n" + reply
    out, backend = _tester(db, "m69", [reply, ""])
    assert backend.calls[1][1].endswith(CODE)


def test_a_fence_left_open_at_the_end_is_a_block(db):
    """The review of 5e0dd71, F5: a reply that ends inside its fence still
    holds the test, so the sentence says "a test"."""
    reply = ("The repair:\n```python\ndef test_echo_json_compact():\n"
             "    assert True\n")
    out, backend = _tester(db, "m69", [reply, ""])
    _, user = backend.calls[1]
    assert user.endswith(HEAD + "'def test_echo_json_compact():\n"
                         "    assert True\n').")


def test_a_ledger_entry_is_not_a_stored_test(db):
    """The review of 5e0dd71, F1: a `ledger.log` stores no test, so a fence
    after it is still told that nothing landed. The answer mode holds
    `ledger.log`."""
    log = ("TOOL: ledger.log(about_ref='echo_json_compact', "
           "about_table='criteria', assumption='the test assumes the key "
           "order of the dict where the material is silent', kind='invented')")
    out, backend = _run(db, _answer(db), [log, _reply("s149_t1"), ""])
    assert not [e for e in out.errors if e.startswith("ledger.log")], out.errors
    assert out.errors.count("wrote a test into its reply") == 1
    _, user = backend.calls[2]
    assert _sentence(user).startswith(HEAD)


def test_the_encode_door_refuses_the_dots_as_an_id(db):
    """The review of 5e0dd71, F2: a seat that keeps `id='...'` of the
    sentence stored a test row with the id `...`. The door asks for an id."""
    db.execute("DELETE FROM tests")
    db.commit()
    call = ("TOOL: tests.encode(id='...', criterion_id='echo_json_compact', "
            "path='tests/test_utils/test_echo_json_new.py', "
            "body='def test_new():\\n    assert True\\n')")
    out, backend = _run(db, _answer(db), [call, ""])
    _, user = backend.calls[1]
    assert ("id='...' is a placeholder, not an id. Give this test an id of "
            "its own, a short name for what it checks, and send the encode "
            "again") in user
    assert db.execute("SELECT COUNT(*) FROM tests").fetchone()[0] == 0


def test_a_session_that_wrote_is_not_told_nothing_landed(db):
    """Night 120's s140 landed its encodes and then showed the test in a
    fence. The review of 9684e3c, I: it was told "nothing landed"."""
    reply = _reply("s149_t1")
    body = reply.split("```python\n", 1)[1].split("```", 1)[0]
    call = "TOOL: " + NUDGE.split("Send it as a call: ", 1)[1].rstrip(".")
    call = call.replace("body='...'", f"body={body!r}")
    done = f"I have encoded the test:\n```python\n{body}```\nI am done."
    out, backend = _tester(db, "m69", [call, done, ""])
    assert "wrote a test into its reply" not in out.errors
    assert len(backend.calls) == 2
    assert all("a reply is not a stored test" not in user
               for _, user in backend.calls)


def test_a_wake_with_two_tests_names_neither(db):
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c2', 'tk_1', 'echo_json emits no ANSI codes')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('t2', 'bg_1', 'c2', 'tests/test_two.py', 'assert 1')")
    db.execute("UPDATE messages SET body_refs = ? WHERE id = 'm69'",
               (json.dumps(["echo_json_compact", "inh_echo_json_01", "t2"]),))
    db.commit()
    out, backend = _tester(db, "m69", [_reply("s149_t1"), ""])
    _, user = backend.calls[1]
    assert ("tests.encode(id='...', criterion_id='...', path='...', "
            "body='''def test") in _sentence(user)


def test_an_answer_naming_two_criteria_names_neither(db):
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c2', 'tk_1', 'echo_json emits no ANSI codes')")
    db.commit()
    out, backend = _run(db, _answer(db, ("echo_json_compact", "c2")),
                        [_reply("s149_t1"), ""])
    _, user = backend.calls[1]
    assert ("tests.encode(id='...', criterion_id='...', path='...', "
            "body='''def test") in _sentence(user)


def test_a_project_test_with_no_criterion_keeps_the_dots(db):
    """A test the repository had carries a NULL criterion. The sentence
    says '...' and never None."""
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('inh_1', 'bg_1', NULL, 'tests/test_echo.py', 'assert 1')")
    db.execute("UPDATE messages SET body_refs = ? WHERE id = 'm69'",
               (json.dumps(["inh_1"]),))
    db.commit()
    out, backend = _tester(db, "m69", [_reply("s149_t1"), ""])
    _, user = backend.calls[1]
    assert ("tests.encode(id='inh_1', criterion_id='...', "
            "path='tests/test_echo.py', body='''def test") in _sentence(user)


def test_an_architects_fenced_reply_gets_no_test_sentence(db):
    """The Architect holds neither tests.encode nor code.write."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m70', 'm70', 'developer', "
               "'architect', 'escalate', ?, 70, 'open')",
               (json.dumps(["echo_json_compact", "inh_echo_json_01"]),))
    db.commit()
    out, backend = _run(db, Wake("architect", "message", message_id="m70",
                                 detail="escalate"),
                        [_reply("s149_t1"), ""])
    assert "wrote a test into its reply" not in out.errors
    assert all("a reply is not a stored test" not in user
               for _, user in backend.calls)


def test_a_fence_beside_a_call_is_not_nudged(db):
    reply = _reply("s149_t1") + "\n\nTOOL: criteria.load()"
    out, backend = _tester(db, "m69", [reply, "Done."])
    assert "wrote a test into its reply" not in out.errors
    assert all("a reply is not a stored test" not in user
               for _, user in backend.calls)


def test_the_developers_fence_sentence_keeps_its_bytes(db, tmp_path):
    root = tmp_path / "wt"
    root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'bg_1'", (str(root),))
    db.commit()
    backend = ScriptedBackend([
        "Here is the fix:\n```python\ndef echo_json(o):\n    print(o)\n```",
        "Done.",
    ])
    out = run_session(db, Wake("developer", "tick:tests_failing",
                               refs=("bg_1",)),
                      backend=backend, pins=Pins(model="scripted"))
    assert "wrote code into its reply" in out.errors
    assert "wrote a test into its reply" not in out.errors
    _, user = backend.calls[1]
    # The whole block is the mark and the sentence of before, byte for byte.
    assert user.rsplit("\n\n", 1)[1] == MARK + DEVELOPER_BEFORE


def test_a_developers_second_fence_meets_the_owed_call_nudge(db, tmp_path):
    """The Developer's second fenced reply on a tick is answered as before
    this frame: the owed-call nudge, never the Tester's stop."""
    root = tmp_path / "wt"
    root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'bg_1'", (str(root),))
    db.commit()
    fence = "Here is the fix:\n```python\ndef echo_json(o):\n    print(o)\n```"
    out, backend = _run(db, Wake("developer", "tick:tests_failing",
                                 refs=("bg_1",)), [fence, fence, "Done."])
    assert out.errors[:2] == ["wrote code into its reply",
                              "ended a tick with nothing done"]
    _, user = backend.calls[2]
    assert "You were woken because something is owed here" in user


# Pass 3: night 126 (2026-10-06). The nudge fired for s154 and s156 and
# moved neither (frame 152's interview).

S154_SENTENCE = (
    "ERROR no call: You wrote a test into your reply, and a reply is not a "
    "stored test -- nothing landed. Send it as a call: tests.encode("
    "id='inh_echo_json_01', criterion_id='echo_json_compact', "
    "path='tests/test_utils/test_echo_json_compact.py', body='''def "
    "test_echo_json_compact():\n"
    "    from click.testing import CliRunner\n"
    "    from src.click.utils import echo_json\n"
    "    \n"
    "    runner = CliRunner()\n"
    "    result = runner.invoke(echo_json, ['{\"key\": \"value\"}'], "
    "catch_exceptions=False)\n"
    "    assert result.exit_code == 0\n"
    "    assert result.output.strip() == '{\"key\": \"value\"}'\n"
    "    # Check for single newline at end\n"
    "    assert result.output.endswith('\\\\n')\n"
    "    # Check no extra newlines\n"
    "    assert result.output.count('\\\\n') == 1\n"
    "''').")


def test_s154s_turn_1_meets_a_marked_sentence_that_holds_its_body(db):
    """s154 quoted the call line and read the sentence as the tail of its
    own reply. It said that the call had to carry the body (the interview,
    answers 2, 7 and 9). The sentence now stands as a block of its own with
    the runner's mark, and its call holds the body of s154's fence."""
    reply = _reply("s154_t1", 126)
    out, backend = _tester(db, "m69", [reply, ""])
    _, user = backend.calls[1]
    assert user.endswith(reply + "\n\n" + S154_SENTENCE)
    assert _parsed(S154_SENTENCE)["body"] == _fence(reply)


class _Cut(ScriptedBackend):
    """A backend whose first reply stopped at the output budget."""

    def complete(self, system, user, pins, tools=None):
        c = super().complete(system, user, pins, tools)
        if len(self.calls) == 1:
            return Completion(text=c.text, pins=pins, backend=self.name,
                              raw={"done_reason": "length"})
        return c


CUT_LINE = ("ERROR reply cut: your reply was cut at the output budget before "
            "it ended. It held no whole call, so no call ran and nothing was "
            "written. Send one call, or end with one sentence.")


def test_s156s_cut_turn_1_meets_the_nudge_after_the_cut_sentences(db):
    """s156's turn 1 was 34,236 characters with whole fences and no call.
    The budget cut it, and the cut sentences stood alone. The runner reads
    the fence from the whole reply, and the nudge follows the cut line."""
    reply = _reply("s156_t1", 126)
    backend = _Cut([reply, reply, ""])
    out = run_session(db, Wake("tester", "message", message_id="m69",
                               detail="challenge"),
                      backend=backend, pins=Pins(model="scripted"))
    assert out.errors.count("wrote a test into its reply") == 1
    _, user = backend.calls[1]
    shown, said = user.rsplit("\n\n", 1)
    assert shown.endswith("Send one call, and keep your prose short.")
    assert said.startswith(CUT_LINE + "\n" + HEAD)
    assert _parsed(said)["body"] == _fence(reply)
    # The fence is not in the 4,000 characters shown, so only the whole
    # reply could give it.
    assert _fence(reply) not in reply[:4000]
    # The second fenced reply is the session's stop, as after any nudge.
    assert len(backend.calls) == 2


def test_a_cut_reply_whose_fence_is_cut_gets_the_cut_line_alone(db):
    """A fence that the budget cut is not the seat's whole text."""
    reply = ("The repair:\n```python\ndef test_echo_json_compact():\n"
             "    assert out")
    backend = _Cut([reply, ""])
    out = run_session(db, Wake("tester", "message", message_id="m69",
                               detail="challenge"),
                      backend=backend, pins=Pins(model="scripted"))
    assert "wrote a test into its reply" not in out.errors
    assert backend.calls[1][1].endswith("\n\n" + CUT_LINE)


def test_a_cut_reply_gives_its_last_whole_test_and_not_the_cut_one(db):
    """s156's later turns held whole fences and ended inside another. The
    block that the budget cut is not offered as the body."""
    whole = "def test_a():\n    assert True\n"
    reply = (f"First:\n```python\n{whole}```\nThen:\n```python\n"
             "def test_b():\n    assert out")
    backend = _Cut([reply, ""])
    run_session(db, Wake("tester", "message", message_id="m69",
                         detail="challenge"),
                backend=backend, pins=Pins(model="scripted"))
    assert _parsed(_sentence(backend.calls[1][1]))["body"] == whole


TRICKY = ("def test_quotes():\n"
          "    single = 'it''s'\n"
          '    double = "say \\"hi\\""\n'
          "    path = 'C:\\\\tmp\\\\x'\n"
          "    doc = '''three'''\n"
          '    other = """three"""\n'
          "    assert single and double and path and doc and other\n")


@pytest.mark.parametrize("body", [
    pytest.param(_fence((HERE / "night126_s154_t1.txt").read_bytes()
                        .decode("utf-8")), id="s154"),
    pytest.param(_fence((HERE / "night126_s156_t1.txt").read_bytes()
                        .decode("utf-8")), id="s156"),
    pytest.param(TRICKY, id="every-quote-and-a-backslash"),
    pytest.param(TRICKY + "    tail = 'x'", id="ends-on-a-quote"),
])
def test_the_rendered_body_parses_back_to_the_fences_text(body):
    """Render, parse with the real parser, compare with the fence's text."""
    assert "\\" in TRICKY and "'''" in TRICKY and '"""' in TRICKY
    head = ("tests.encode(id='inh_echo_json_01', criterion_id='c1', "
            "path='tests/test_x.py'")
    assert SIGS["tests.encode"][0] == {"id", "criterion_id", "path", "body"}
    literal = _body_literal(body, {"tests.encode"}, SIGS, head)
    assert literal is not None
    calls = toolproto.extract_lenient(
        f"TOOL: {head}, body={literal})", {"tests.encode"}, SIGS)
    assert len(calls) == 1 and calls[0].args["body"] == body


def test_a_body_the_parser_cannot_return_falls_back_to_the_dots(db):
    """The lenient parse drops the backticks of a key before `=`, so no
    form returns this body whole. The call keeps body='...', and the
    sentence says to paste the fence's text there."""
    body = "def test_x():\n    # `n` = 1\n    assert True\n"
    assert _body_literal(body, {"tests.encode"}, SIGS, "tests.encode(id='t'") is None
    out, backend = _tester(db, "m69", [f"The test:\n```python\n{body}```", ""])
    assert backend.calls[1][1].endswith(
        NUDGE + " Put the text of your fenced test in place of the dots of body.")


# Pass 4: the review of 1cfbe704.

S154_SAME = (
    "ERROR no call: Your fenced test is the stored version 1, which failed. "
    "Change the test and send it as a call: tests.encode("
    "id='inh_echo_json_01', criterion_id='echo_json_compact', "
    "path='tests/test_utils/test_echo_json_compact.py', body='...'), or answer "
    "the challenge: msg.answer_developer(refs=['echo_json_compact', "
    "'inh_echo_json_01'], quotes=['...']).")


def _night126(path):
    """Night 126's state at m76: inh_echo_json_01 at version 1, which is
    s154's fence less one line break, and its failed run."""
    conn = _night(path)
    body = _fence(_reply("s154_t1", 126)).rstrip("\n")
    conn.execute("UPDATE tests SET body = ?, version = 1 "
                 "WHERE id = 'inh_echo_json_01'", (body,))
    conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
                 "result, output, attempt) VALUES ('tr326', 'bg_1', "
                 "'inh_echo_json_01', 'a7045de', 'fail', "
                 "'AttributeError: ''function'' object has no attribute "
                 "''name''', 11)")
    conn.commit()
    return conn, body


def test_s154s_fence_that_is_the_stored_test_is_told_so(tmp_path):
    """Finding 1: the sentence offered to store the failing test again. It
    now names the version and offers a change or an answer."""
    db, _ = _night126(tmp_path / "a.db")
    reply = _reply("s154_t1", 126)
    out, backend = _tester(db, "m69", [reply, ""])
    assert backend.calls[1][1].endswith(reply + "\n\n" + S154_SAME)


def test_both_calls_of_the_same_test_sentence_pass_the_doors(tmp_path):
    """The encode with a changed body lands, and the answer with a span of
    the criterion is sent."""
    reply = _reply("s154_t1", 126)
    encode = S154_SAME.split("as a call: ", 1)[1].split(", or answer", 1)[0]
    encode = "TOOL: " + encode.replace("body='...'",
                                       f"body={_fence(_reply('s149_t1'))!r}")
    db, _ = _night126(tmp_path / "a.db")
    out, _ = _tester(db, "m69", [reply, encode, ""])
    assert not [e for e in out.errors if e.startswith("tests.encode")], out.errors
    assert db.execute("SELECT version FROM tests WHERE id = "
                      "'inh_echo_json_01'").fetchone()[0] == 2

    answer = S154_SAME.split("or answer the challenge: ", 1)[1][:-1]
    answer = "TOOL: " + answer.replace(
        "quotes=['...']", "quotes=['followed by a single newline']")
    db, _ = _night126(tmp_path / "b.db")
    out, _ = _tester(db, "m69", [reply, answer, ""])
    assert not [e for e in out.errors if e.startswith("msg.")], out.errors
    assert db.execute("SELECT COUNT(*) FROM messages WHERE from_role = "
                      "'tester' AND verb = 'answer'").fetchone()[0] == 1


def test_an_encode_of_the_stored_body_with_a_line_break_is_unchanged(tmp_path):
    """Finding 5 of the review, the door: trailing whitespace is no change,
    so no version moves."""
    db, body = _night126(tmp_path / "a.db")
    call = ("TOOL: tests.encode(id='inh_echo_json_01', criterion_id="
            "'echo_json_compact', path='tests/test_utils/"
            f"test_echo_json_compact.py', body={body + chr(10)!r})")
    out, backend = _tester(db, "m69", [call, ""])
    assert "identical to what is already on file" in backend.calls[1][1]
    assert db.execute("SELECT version FROM tests WHERE id = "
                      "'inh_echo_json_01'").fetchone()[0] == 1


class _CutTwice(ScriptedBackend):
    """A backend whose first two replies stopped at the output budget."""

    def complete(self, system, user, pins, tools=None):
        c = super().complete(system, user, pins, tools)
        if len(self.calls) <= 2:
            return Completion(text=c.text, pins=pins, backend=self.name,
                              raw={"done_reason": "length"})
        return c


PROSE = "I will look at the failure first and explain it at length. " * 20


def test_a_second_cut_reply_gives_its_whole_test_and_not_the_cut_one(db):
    """Finding 2: the fence branch reads whole blocks only after a cut."""
    whole = "def test_a():\n    assert True\n"
    reply = (f"First:\n```python\n{whole}```\nThen:\n```python\n"
             "def test_b():\n    assert out")
    backend = _CutTwice([PROSE, reply, ""])
    run_session(db, Wake("tester", "message", message_id="m69",
                         detail="challenge"),
                backend=backend, pins=Pins(model="scripted"))
    assert _parsed(_sentence(backend.calls[2][1]))["body"] == whole


def test_a_second_cut_reply_whose_test_is_cut_keeps_the_test_form(db):
    """Finding 3, the review's probe p7: the sentence called a cut test
    code. It keeps the test form and the dots, and says the budget cut the
    test."""
    cut = ("Here is the repair:\n```python\ndef test_echo_json_compact():\n"
           "    assert resu")
    backend = _CutTwice([PROSE, cut, ""])
    run_session(db, Wake("tester", "message", message_id="m69",
                         detail="challenge"),
                backend=backend, pins=Pins(model="scripted"))
    assert backend.calls[2][1].endswith(
        HEAD.replace("nothing landed. Send", "nothing landed. The output "
                     "budget cut your fenced test before it ended. Send")
        + "'...'). Put the whole test in place of the dots of body.")


# The case runner's `replies:` key (the review of 9684e3c, point 5).

CASE_ID = "L1-TS-send-a-test-written-into-the-reply-as-tests-encode"


class _NoModel:
    """A model that must not be asked."""

    name = "none"
    misses = 0

    def complete(self, *a, **k):
        raise AssertionError("the model was asked")


def _case(run_no=1):
    from rota import paths
    from rota.testkit import fixtures
    case = next(c for c in fixtures.load_case(paths.CASES / "l1_tester.yaml")
                if c["id"] == CASE_ID)
    return fixtures.for_run(case, run_no)


def _right_call(problem) -> str:
    t = problem["fixture"]["tests"][0]
    body = problem["replies"][0].split("```python\n", 1)[1].split("```", 1)[0]
    return (f"TOOL: tests.encode(id={t['id']!r}, criterion_id="
            f"{t['criterion_id']!r}, path={t['path']!r}, body={body!r})")


def _run_case(problem, backend, tmp_path):
    from rota.testkit import fixtures
    return fixtures.run_case(problem, tmp_path / "c.db", backend,
                             pins=Pins(model="scripted"),
                             instructions=fixtures.instructions_for(problem))


def test_a_case_whose_replies_end_the_session_judged_nothing(tmp_path):
    """The passing call inside `replies:` passed the case with no model."""
    problem = _case()
    problem["replies"] = [problem["replies"][0], _right_call(problem), "Done."]
    r = _run_case(problem, _NoModel(), tmp_path)
    assert not r.passed
    assert ("the model made no completion after the scripted replies, so "
            "the case judged nothing") in r.problems
    assert [x.get("scripted") for x in r.transcript() if "say" in x] == [True] * 3


def test_the_case_judges_the_first_call_after_the_replies(tmp_path):
    problem = _case()
    r = _run_case(problem, ScriptedBackend([_right_call(problem), ""]), tmp_path)
    assert r.passed, r.problems
    says = [x for x in r.transcript() if "say" in x]
    assert says[0].get("scripted") and not says[1].get("scripted")

    problem = _case()
    wrong = _right_call(problem).replace(problem["fixture"]["tests"][0]["id"],
                                         "t_new", 1)
    r = _run_case(problem, ScriptedBackend([wrong, ""]), tmp_path / "x")
    assert not r.passed
    assert any(p.startswith("the first tests.encode names {'id': 't_new'}")
               for p in r.problems), r.problems

    r = _run_case(_case(), ScriptedBackend(["TOOL: criteria.load()", ""]),
                  tmp_path / "y")
    assert ("expected a first call to tests.encode; got criteria.load"
            in r.problems), r.problems


def test_the_case_judges_the_first_call_of_a_reply_with_two(tmp_path):
    """The review of 5e0dd71, F5: the first call is the act the case judges,
    even when the right call follows it in the same reply."""
    problem = _case()
    reply = "TOOL: criteria.load()\n" + _right_call(problem)
    r = _run_case(problem, ScriptedBackend([reply, ""]), tmp_path)
    assert ("expected a first call to tests.encode; got criteria.load"
            in r.problems), r.problems


def test_a_first_reply_with_no_call_fails_the_case(tmp_path):
    r = _run_case(_case(), ScriptedBackend(["I have nothing to send.", ""]),
                  tmp_path)
    assert not r.passed
    assert ("expected a first call to tests.encode; the reply holds no call"
            in r.problems), r.problems


def test_no_completion_after_the_replies_names_the_missing_call(tmp_path):
    problem = _case()
    problem["replies"] = [problem["replies"][0], _right_call(problem), "Done."]
    r = _run_case(problem, _NoModel(), tmp_path)
    assert ("expected a first call to tests.encode; the model made none"
            in r.problems), r.problems


def test_a_chain_refuses_scripted_replies(tmp_path):
    from rota.testkit import fixtures
    chain = {"id": "x", "first": {"role": "tester"}, "then": {"role": "developer"},
             "replies": ["text"]}
    with pytest.raises(ValueError, match="run_chain does not serve it"):
        fixtures.run_chain(chain, tmp_path / "c.db", lambda: _NoModel())
