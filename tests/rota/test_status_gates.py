"""
The status tool writes a pass line and a close whatever the Reach line reads.

Rule C76 of `plans/method/reference.md` says an issue is read before it
is fixed. The session applies the rule, and the tool refuses no body for
its Reach line: "No don't make it a hard rule, the model should be smart
enough to do it" (ruled: Roman, 2026-10-26 about 22:5x). The fixture
holds two frames: frame 20 has no Reach line, and frame 21 has
`Reach: 1 of 10`. Every body that the two gates of d1c934ae refused must
land on its frame unchanged.

The live bodies of 2026-10-26 are a copy in
`fixtures/status_gates_2026-10-26.json`, so no test reads `plans/stack.md`.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from rota.tools import state, status

STACK = """# The stack

## Stack

### 20. A frame with no reach line (2026-10-26) (aaaa1111)

- **Site: `rota/tools/status.py`.** Meta workflow. A story.
- Ends when: the line lands.
- Waits on: nothing.
- Pointer: `plans/x.md`.
- Status 2026-10-26 10:00 (rota-01): the first line.

### 21. A frame that reaches one place of ten (2026-10-26) (aaaa1111)

- **Site: `rota/roles/api.py`.** Rota workflow. A story.
- Ends when: the door refuses.
- Waits on: nothing.
- Reach: 1 of 10, the other nine doors take the same text.
- Pointer: `plans/y.md`.
- Status 2026-10-26 11:00 (rota-01): the first line.
"""

LIVE = json.loads((Path(__file__).parent / "fixtures" / "status_gates_2026-10-26.json")
                  .read_bytes().decode("utf-8"))


@pytest.fixture
def stack(tmp_path, monkeypatch):
    """The fixture stack in a temp `plans/`, and a fixed clock."""
    monkeypatch.setattr(status, "_clock", lambda: datetime(2031, 1, 2, 3, 4))
    (tmp_path / "plans").mkdir()
    path = tmp_path / "plans" / "stack.md"
    path.write_bytes(STACK.encode("utf-8"))
    return path


def append(path: Path, *argv: str) -> int:
    return status.main(["--stack", str(path), "--sid", "aaaa1111",
                        "--no-commit", *argv])


def lands(path: Path, frame: str, body: str) -> None:
    """Assert that the body lands on the frame as one line, unchanged."""
    assert append(path, frame, "--text", body) == 0
    frames = {f.number: f for f in state.parse(
        path.read_bytes().decode("utf-8").split("\n"), bounded=False)}
    wanted = "- Status 2031-01-02 03:04 (aaaa1111): %s" % body
    assert wanted in frames[frame].lines, body


# The reader stays, because `state` prints the Reach line.

def test_the_reader_returns_the_text_after_reach_or_none():
    frames = {f.number: f for f in state.parse(STACK.split("\n"), bounded=False)}
    assert state.reach_line(frames["20"].lines) is None
    assert state.reach_line(frames["21"].lines) == \
        "1 of 10, the other nine doors take the same text."


def test_the_reader_returns_the_last_reach_line():
    block = ["### 21. A frame", "- Reach: 10 of 10, first.", "- Reach: 1 of 10, a recount."]
    assert state.reach_line(block) == "1 of 10, a recount."


# A pass line on a frame with no Reach line.

@pytest.mark.parametrize("body", [
    "Pass 1 runs on a fresh implementer.",
    "pass 2b built, 4 files.",
    "Pass 1 is at the gate.",
    "The review of pass 1 runs on Opus.",
    "The implementer of frame 20 runs now.",
    "The read runs on one agent.",
])
def test_a_pass_body_on_a_frame_with_no_reach_line_lands(stack, body):
    lands(stack, "20", body)


def test_every_live_pass_line_of_2026_10_26_lands(stack):
    """Frame 330's line of 18:20 was the red test of the gate. It now lands."""
    lines = [row["line"] for row in LIVE["pass"]]
    assert 1288 in lines and len(lines) == 29
    for row in LIVE["pass"] + LIVE["not_pass"]:
        lands(stack, "20", row["body"])


# A close below the Reach count, or with no Reach line.

@pytest.mark.parametrize("body", [
    "Closed. The door refuses.",
    "**Popped.** The door refuses.",
    "**Met on night 3 of 3: 0 refusals.**",
    "Met, the door refuses.",
    "Pops on the count.",
    "The door refuses, and the frame closes on night 170.",
    "Moved to plans/archive/stack-2026-10-27.md.",
])
def test_a_close_below_the_count_lands(stack, body):
    lands(stack, "21", body)


def test_the_live_met_closes_of_2026_10_26_land(stack):
    assert [row["line"] for row in LIVE["met"]] == [16, 241]
    for row in LIVE["met"]:
        lands(stack, "21", row["body"])
        lands(stack, "20", row["body"])


def test_a_close_with_a_reach_line_that_has_no_count_lands(stack):
    stack.write_bytes(STACK.replace("Reach: 1 of 10,", "Reach: every door,")
                      .encode("utf-8"))
    lands(stack, "21", "Closed. The door refuses.")


# The flag that forced the close gate is gone.

def test_force_close_is_an_unknown_argument(stack, capsys):
    before = stack.read_bytes()
    with pytest.raises(SystemExit) as exit_:
        append(stack, "21", "--text", "Closed. The door refuses.",
               "--force-close", "frame 22 holds the other nine")
    assert exit_.value.code == 2
    assert "unrecognized arguments: --force-close" in capsys.readouterr().err
    assert stack.read_bytes() == before


# The ruling.

def test_a_ruling_lands_on_either_frame(stack):
    assert append(stack, "20", "--ruling", "closed, pass 1 runs now",
                  "--at", "02:35") == 0
    assert append(stack, "21", "--ruling", "Met on night 3, pass 1 runs now",
                  "--at", "02:36") == 0


# The put-down warns where it can hurt, and it refuses nothing for a warning
# (ruled: Roman, 2026-10-18 02:25, "enabling not inhibiting").

def put_down(path: Path, frame: str, sid: str = "aaaa1111") -> int:
    return status.main(["--stack", str(path), "--sid", sid, "--no-commit",
                        frame, "--put-down", "no longer needed"])


def gone(path: Path, frame: str) -> bool:
    return frame not in {f.number for f in state.parse(
        state.read_lines(path), bounded=False)}


def test_a_frame_of_another_session_is_put_down_with_one_line(stack, capsys):
    assert put_down(stack, "20", sid="cccc3333") == 0
    out = capsys.readouterr().out
    assert "WARNING: session aaaa1111 holds frame 20, and session cccc3333 puts it down." in out
    assert gone(stack, "20")


@pytest.fixture
def f33(stack, monkeypatch):
    """The suite's reader of `open_frames`, pointed at the fixture stack."""
    from tests.rota import test_f33_debts_name_open_frames as reader
    monkeypatch.setattr(reader, "STACK", stack)
    return reader


def test_a_debt_that_names_the_frame_gets_one_line_and_the_put_down_runs(
        stack, f33, monkeypatch, capsys):
    monkeypatch.setattr(f33, "debts", lambda: [
        ("tests/rota/test_x.py:9", "held by frame 21: a wall"),
        ("tests/rota/test_y.py:4", "held by frame 20"),
        ("tests/rota/test_z.py:5", "held by frame 99")])
    assert put_down(stack, "21") == 0
    lines = [x for x in capsys.readouterr().out.splitlines() if "open_frames" in x]
    assert lines == [
        "WARNING: tests/rota/test_f33_debts_name_open_frames.py::"
        "test_each_debt_names_an_open_frame reads state.open_frames, and it turns "
        "red on 1 debts that name frame 21: tests/rota/test_x.py:9 (frame 21)."]
    assert gone(stack, "21")


def test_the_live_owed_debt_is_found_by_the_real_reader(stack, f33, capsys):
    """The real `debts()` runs, on a stack that holds the owed set's frame."""
    from tests.rota.test_case_reachability import OWED_FRAME
    owed = OWED_FRAME.split()[-1]
    stack.write_bytes(STACK.replace("### 21.", "### %s." % owed).encode("utf-8"))
    assert put_down(stack, owed) == 0
    out = capsys.readouterr().out
    assert "turns red on" in out and "OWED (" in out
    assert gone(stack, owed)


def test_a_reader_of_another_stack_and_a_broken_reader_refuse_nothing(
        stack, f33, monkeypatch, capsys):
    monkeypatch.setattr(f33, "STACK", stack.parent / "other.md")
    assert put_down(stack, "20") == 0
    assert "open_frames" not in capsys.readouterr().out

    def broken():
        raise RuntimeError("no cases")

    monkeypatch.setattr(f33, "STACK", stack)
    monkeypatch.setattr(f33, "debts", broken)
    assert put_down(stack, "21") == 0
    assert "did not run (no cases)" in capsys.readouterr().out
    assert gone(stack, "21")
