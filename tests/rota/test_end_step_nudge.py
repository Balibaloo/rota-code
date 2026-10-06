"""
Frame 153, night 125 (2026-10-05): the door said "end", and the runner said
"act".

The Developer s158 sent a challenge that the same-refs door refused with the
step `End the session with no call.` s158 obeyed with a reply that held no
call. The runner's owed-call nudge then told it to act with a call, and s158
sent the refused challenge again. These tests drive the real loop with
s158's own replies, copied from the night's `turns` table into
`fixtures/night125_s158_t*.txt`.
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

HERE = Path(__file__).parent / "fixtures"

CRIT = ('The callable `echo_json` accepts any Python object and writes its '
        'JSON representation to the stream using `json.dumps(obj, '
        'separators=(",", ":"))`, followed by a single newline.')
# Version 2 of inh_echo_json_01, the body that s158's wake shows.
TEST = ('def test_echo_json_compact():\n    import sys\n    from io import '
        'StringIO\n    from src.click.utils import echo_json\n    \n    '
        'old_stdout = sys.stdout\n    sys.stdout = StringIO()\n    try:\n'
        '        echo_json({"key": "value"})\n    finally:\n        '
        'sys.stdout = old_stdout\n    \n    output = sys.stdout.getvalue()\n'
        '    assert output.strip() == "{\\"key\\": \\"value\\"}"\n    # Check '
        'for single newline at end\n    assert output.endswith("\\n")\n    '
        '# Check no extra newlines\n    assert output.count("\\n") == 1')
# The owed-call nudge as the parent 8838632 writes it, byte for byte.
OWED = ("You were woken because something is owed here, and this session has "
        "written nothing and sent nothing -- the same wake will fire again "
        "with the same material. Act on your conclusion with a call: fix it, "
        "dispute it with the evidence quoted, or escalate it. If truly "
        "nothing is owed, say so and stop.")
REFS = ["echo_json_compact", "inh_echo_json_01"]
# The step and the reply that takes it, on the refused challenge's test
# (frame 165). Written out, so a new wording turns these red.
ENDS = ("End the session with no call. Your whole next reply is this one "
        "line, and no TOOL: line: Nothing more is owed on inh_echo_json_01 "
        "in this session.")
# The refusal that s158 met at turns 1 and 3, with frame 165's form.
REASON = ("you sent challenge to tester on exactly these refs already (m68, "
          "then m69), and the Tester answered neither and did not change the "
          "test. " + ENDS)
REFUSED = "ERROR msg.challenge_tester: " + REASON


def _reply(name: str) -> str:
    return (HERE / f"night125_{name}.txt").read_bytes().decode("utf-8")


def _night(path, root, escalated: bool = True):
    """Night 125's rows at s158: the test at version 2, the challenges m68
    and m69 closed with no answer row, and the escalation m70 closed."""
    conn = init_db(path)
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1', 'print an object as compact JSON', "
                 "'in_scope', 'approved', 1, 1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk_1', 'i1', 'add echo_json')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('echo_json_compact', 'tk_1', ?)", (CRIT,))
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit, "
                 "worktree) VALUES ('bg_1', 'i1', 'running', 'a7045de', ?)",
                 (str(root),))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_1', 'tk_1')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body, "
                 "version) VALUES ('inh_echo_json_01', 'bg_1', "
                 "'echo_json_compact', "
                 "'tests/test_utils/test_echo_json_compact.py', ?, 2)", (TEST,))
    sent = [("m68", 68, "tester", "challenge", "unresolved"),
            ("m69", 69, "tester", "challenge", "unresolved")]
    if escalated:
        sent.append(("m70", 70, "architect", "escalate", "answered"))
    for mid, seq, to, verb, status in sent:
        conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                     "verb, body_refs, seq, status) VALUES (?, ?, 'developer', "
                     "?, ?, ?, ?, ?)",
                     (mid, mid, to, verb, json.dumps(REFS), seq, status))
    conn.commit()
    return conn


@pytest.fixture
def root(tmp_path):
    wt = tmp_path / "wt"
    wt.mkdir()
    return wt


def _s158(conn, script: list[str], kind: str = "tick:tests_failing",
          batch_id: str | None = None):
    backend = ScriptedBackend(script)
    out = run_session(conn, Wake("developer", kind,
                                 refs=("bg_1",), detail="attempt 6"),
                      backend=backend, pins=Pins(model="scripted"),
                      batch_id=batch_id)
    return out, backend


def _escalate() -> str:
    """s157's turn 2: the escalation on the same refs, which the door refuses
    with no step to end, because m70 is closed."""
    return _reply("s157_t2")


def test_s158_ends_when_the_door_says_end(tmp_path, root):
    """s158 met the step at turn 1 and obeyed at turn 2. The night then
    nudged it, and it sent the refused challenge at turn 3. Now turn 2 is
    the end of the session."""
    conn = _night(tmp_path / "rota.db", root)
    out, backend = _s158(conn, [_reply(f"s158_t{n}") for n in (1, 2, 3, 4)])
    assert len(backend.calls) == 2, "the reply with no call is the end"
    _, user = backend.calls[1]
    assert user.endswith(REFUSED), "the door's refusal is the night's"
    assert "ended a tick with nothing done" not in out.errors
    assert out.errors.count("msg.challenge_tester: " + REASON) == 1
    assert out.committed, out.errors


def test_a_refusal_with_another_step_keeps_the_nudge(tmp_path, root):
    """s150's shape: with no escalation yet, the door offers it and gives
    no step to end. The reply with no call gets the parent's nudge, to the
    byte. The same turns with the step get no nudge, so the step is the one
    thing that moves it."""
    conn = _night(tmp_path / "a.db", root, escalated=False)
    prose = _reply("s158_t2")
    out, backend = _s158(conn, [_reply("s158_t1"), prose, "Done."])
    assert len(backend.calls) == 3
    _, user = backend.calls[1]
    assert user.endswith("Send msg.escalate_architect on the same refs.")
    _, user = backend.calls[2]
    assert user.endswith(prose + "\n\n" + OWED)
    assert "ended a tick with nothing done" in out.errors

    conn = _night(tmp_path / "b.db", root)
    out, backend = _s158(conn, [_reply("s158_t1"), prose, "Done."])
    assert len(backend.calls) == 2
    assert "ended a tick with nothing done" not in out.errors


def test_only_the_newest_refusal_counts(tmp_path, root):
    """The step, then a refusal with another step: the nudge comes back.
    The other refusal, then the step: no nudge."""
    prose = _reply("s158_t2")
    conn = _night(tmp_path / "a.db", root)
    out, backend = _s158(conn, [_reply("s158_t1"), _escalate(), prose,
                                "Done."])
    assert len(backend.calls) == 4
    _, user = backend.calls[2]
    assert "you sent escalate to architect on exactly these refs already " \
           "(m70)" in user
    _, user = backend.calls[3]
    assert user.endswith(prose + "\n\n" + OWED)

    conn = _night(tmp_path / "b.db", root)
    out, backend = _s158(conn, [_escalate(), _reply("s158_t1"), prose,
                                "Done."])
    assert len(backend.calls) == 3, "the step is the newest refusal"
    _, user = backend.calls[2]
    assert user.endswith(REFUSED)
    assert "ended a tick with nothing done" not in out.errors


# The pass 2 tests come from the diff review of d77bdec (2026-10-05). The
# rule: the flag is true only while the newest answer to any call is the
# door's refusal with the step to end.
SOURCE = "TOOL: code.source(path='src/click/utils.py', start=0, end=2)"
WRITE = ("TOOL: code.write(path='src/click/utils.py', text='import json\n"
         "def echo_json(obj):\n    print(json.dumps(obj))\n')")


def _with_code(conn, root):
    """The file that the challenged test calls, so a read and a write land."""
    (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "utils.py").write_text(
        "def echo_json(obj):\n    pass\n", encoding="utf-8", newline="")
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
                 "('project_root', ?)", (str(root),))
    conn.commit()
    return conn


def test_a_write_after_the_step_brings_the_nudge_back(tmp_path, root):
    """Case C2: the step, then a `code.write` that lands, then prose. The
    write is the newest answer, so the step no longer stands. The parent
    nudged here, and without the reset the session ended with the write
    uncommitted."""
    conn = _with_code(_night(tmp_path / "rota.db", root), root)
    prose = _reply("s158_t2")
    out, backend = _s158(conn, [_reply("s158_t1"), WRITE, prose, prose,
                                "Done."], batch_id="bg_1")
    assert len(backend.calls) == 4
    _, user = backend.calls[2]
    assert "\nOK code.write -> " in user, user[-600:]
    _, user = backend.calls[3]
    assert user.endswith(prose + "\n\n" + OWED)


def test_a_held_challenge_that_meets_the_step_ends(tmp_path, root):
    """Case C5: a fresh read holds the challenge, and the challenge runs
    when the reply holds no call. The door's step then ends the session
    after the stood-by refusal is read, and no nudge comes."""
    conn = _with_code(_night(tmp_path / "rota.db", root), root)
    prose = _reply("s158_t2")
    out, backend = _s158(conn, [SOURCE + "\n" + _reply("s158_t1"), prose,
                                prose, prose, "Done."])
    assert len(backend.calls) == 3
    _, user = backend.calls[2]
    assert "The calls you stood by ran, and these were refused:" in user
    assert REFUSED in user
    assert "ended a tick with nothing done" not in out.errors


def test_a_held_write_after_the_held_step_brings_the_nudge_back(tmp_path,
                                                                root):
    """The held challenge meets the step, and the held write behind it
    lands. The write is the newest answer, so the nudge comes."""
    conn = _with_code(_night(tmp_path / "rota.db", root), root)
    prose = _reply("s158_t2")
    out, backend = _s158(conn, [
        SOURCE + "\n" + _reply("s158_t1") + "\n" + WRITE, prose, prose,
        prose, "Done."], batch_id="bg_1")
    assert len(backend.calls) == 4
    _, user = backend.calls[2]
    assert REFUSED in user
    assert "code.write" not in user.rsplit("these were refused:", 1)[1], \
        "the held write landed"
    assert (root / "src" / "click" / "utils.py").read_text(
        encoding="utf-8").startswith("import json\n")
    _, user = backend.calls[3]
    assert user.endswith(prose + "\n\n" + OWED)


@pytest.mark.parametrize("bad", [
    # The parser's error: an argument with no value.
    "TOOL: criteria.load(batch_id=)",
    # The argument check's error: the Developer holds no `tests.encode`.
    "TOOL: tests.encode(id='t', criterion_id='c', path='p.py', body='x')",
])
def test_a_call_error_after_the_step_brings_the_nudge_back(tmp_path, root,
                                                           bad):
    """An ERROR line from the parser or the argument check answers a call
    too, and it is newer than the step."""
    conn = _night(tmp_path / "rota.db", root)
    prose = _reply("s158_t2")
    out, backend = _s158(conn, [_reply("s158_t1"), bad, prose, prose,
                                "Done."])
    assert len(backend.calls) == 4
    _, user = backend.calls[2]
    assert user.rstrip().splitlines()[-1].startswith("ERROR ")
    assert "OK " not in user.rsplit(REFUSED, 1)[1]
    _, user = backend.calls[3]
    assert user.endswith(prose + "\n\n" + OWED)


def test_a_session_with_no_refusal_gets_the_nudge(tmp_path, root):
    """The flag starts false: no call has been answered yet."""
    conn = _night(tmp_path / "rota.db", root)
    prose = _reply("s158_t2")
    out, backend = _s158(conn, [prose, prose, "Done."])
    assert len(backend.calls) == 2
    _, user = backend.calls[1]
    assert user.endswith(prose + "\n\n" + OWED)


def _judged(conn):
    """The Tester answered m69, so the door says "they answered" and takes
    its step from the mode. m70 is closed, so no escalation is offered."""
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                 "verb, body_refs, seq, status, cause_id) VALUES ('m71', "
                 "'m69', 'tester', 'developer', 'answer', ?, 71, 'answered', "
                 "'m69')", (json.dumps(REFS),))
    conn.commit()
    return conn


def test_mode_exhausted_ends_on_the_code_step(tmp_path, root):
    """Mode `exhausted` holds no `code.write`, so the step toward the code
    is the step to end (`sandbox._code_step`). The session ends there."""
    conn = _judged(_night(tmp_path / "rota.db", root))
    prose = _reply("s158_t2")
    out, backend = _s158(conn, [_reply("s158_t1"), prose, prose, "Done."],
                         kind="tick:exhausted")
    assert len(backend.calls) == 2
    _, user = backend.calls[1]
    assert user.endswith("they answered (m71). Sending it again is the same "
                         "argument again. " + ENDS)
    assert "ended a tick with nothing done" not in out.errors


def test_the_step_toward_the_code_keeps_the_nudge(tmp_path, root):
    """The same refusal in a mode that holds `code.write` asks for a change
    to the code. That step is no end, so the nudge comes."""
    conn = _judged(_night(tmp_path / "rota.db", root))
    prose = _reply("s158_t2")
    out, backend = _s158(conn, [_reply("s158_t1"), prose, prose, "Done."])
    assert len(backend.calls) == 3
    _, user = backend.calls[1]
    assert user.endswith("Make one real change to the code the test calls.")
    _, user = backend.calls[2]
    assert user.endswith(prose + "\n\n" + OWED)
