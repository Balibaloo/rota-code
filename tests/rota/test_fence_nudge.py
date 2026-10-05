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
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.runner import run_session
from rota.llm.llm import Pins, ScriptedBackend

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
NUDGE = ("You wrote a test into your reply, and a reply is not a stored test "
         "-- nothing landed. Send it as a call: tests.encode("
         "id='inh_echo_json_01', criterion_id='echo_json_compact', "
         "path='tests/test_utils/test_echo_json_compact.py', body='...').")
DEVELOPER = ("You wrote code into your reply, and a reply is not a file -- "
             "nothing landed. Send it as a call: "
             "code.write(path='...', text='...') and then code.commit.")


def _reply(name: str) -> str:
    return (HERE / f"night125_{name}.txt").read_bytes().decode("utf-8")


@pytest.fixture
def db(tmp_path):
    """Night 125's rows for m68 and m69: one criterion, its test at version
    2, and the Developer's challenge on both."""
    conn = init_db(tmp_path / "rota.db")
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
    assert user.endswith(NUDGE)
    assert "named an act and did not perform it" not in out.errors


def test_the_call_the_nudge_names_lands_with_s149s_body(db):
    """The call copied from the nudge, with the body from s149's fence,
    passes the encode doors and replaces version 2."""
    reply = _reply("s149_t1")
    body = reply.split("```python\n", 1)[1].split("```", 1)[0]
    call = NUDGE.split("Send it as a call: ", 1)[1].rstrip(".")
    call = "TOOL: " + call.replace("body='...'", f"body={body!r}")
    out, backend = _tester(db, "m69", [reply, call, ""])
    assert out.committed, out.errors
    assert not [e for e in out.errors if e.startswith("tests.encode")], out.errors
    row = db.execute("SELECT body, version FROM tests "
                     "WHERE id = 'inh_echo_json_01'").fetchone()
    assert "redirect_stdout" in row["body"] and row["version"] > 2


def test_s147s_fenced_repair_meets_the_test_nudge_before_the_named_act(db):
    """s147 met the named-act nudge at turn 1 and closed at turn 2. Now
    turn 1 meets the test nudge, and turn 2, fenced again, is the stop."""
    out, backend = _tester(db, "m68", [_reply("s147_t1"), _reply("s147_t2"),
                                       "Done."])
    assert out.errors.count("wrote a test into its reply") == 1
    assert len(backend.calls) == 2, "the second fenced reply is the stop"
    _, user = backend.calls[1]
    assert user.endswith(NUDGE)
    assert "You said what you would do" not in user
    assert "named an act and did not perform it" not in out.errors


def test_a_tick_wake_names_the_one_criterion_it_holds(db):
    """A wake with no test in its refs keeps '...' for what it lacks."""
    db.execute("DELETE FROM tests")
    db.commit()
    backend = ScriptedBackend([_reply("s149_t1"), _reply("s149_t1")])
    out = run_session(db, Wake("tester", "tick:tests_missing",
                               refs=("echo_json_compact",)),
                      backend=backend, pins=Pins(model="scripted"))
    assert out.errors.count("wrote a test into its reply") == 1
    _, user = backend.calls[1]
    assert user.endswith(
        "Send it as a call: tests.encode(id='...', "
        "criterion_id='echo_json_compact', path='...', body='...').")
    # The second fenced reply is the stop, and the owed-call nudge does not
    # answer it.
    assert len(backend.calls) == 2
    assert "ended a tick with nothing done" not in out.errors


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
    assert user.endswith(DEVELOPER)
