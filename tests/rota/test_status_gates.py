"""
The two gates of rule C76 in the status tool, tested on a stack the test writes.

Rule C76 of `plans/method/reference.md` says an issue is read before it
is fixed. The status tool refuses a pass line on a frame with no Reach
line. It refuses a close while the last Reach line covers fewer places
than its count, or carries no count. The fixture holds two frames: frame
20 has no Reach line, and frame 21 has `Reach: 1 of 10`.

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
- Ends when: the gate refuses.
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


def refused(path: Path, capsys, frame: str, *argv: str) -> str:
    """Assert a refusal that writes nothing, and return its stderr."""
    before = path.read_bytes()
    assert append(path, frame, *argv) == 2
    assert path.read_bytes() == before
    return capsys.readouterr().err


# The reader.

def test_the_reader_returns_the_text_after_reach_or_none():
    frames = {f.number: f for f in state.parse(STACK.split("\n"), bounded=False)}
    assert state.reach_line(frames["20"].lines) is None
    assert state.reach_line(frames["21"].lines) == \
        "1 of 10, the other nine doors take the same text."


def test_the_reader_returns_the_last_reach_line():
    block = ["### 21. A frame", "- Reach: 10 of 10, first.", "- Reach: 1 of 10, a recount."]
    assert state.reach_line(block) == "1 of 10, a recount."


# The pass gate.

@pytest.mark.parametrize("body", [
    "Pass 1 runs on a fresh implementer.",
    "pass 2b built, 4 files.",
    "Pass 1 is at the gate.",
    "The review of pass 1 runs on Opus.",
    "The implementer of frame 20 runs now.",
])
def test_a_pass_body_on_a_frame_with_no_reach_line_is_refused(stack, capsys, body):
    assert "frame 20 has no Reach line" in refused(stack, capsys, "20", "--text", body)


@pytest.mark.parametrize("body", [
    "The read runs on one agent.",
    "The gate on 24fd4638: 5 new reds, the known five.",
    "Passes 1 and 1b are on the branch.",
])
def test_a_body_with_no_pass_and_no_implementer_run_is_accepted(stack, body):
    assert append(stack, "20", "--text", body) == 0
    assert body in stack.read_bytes().decode()


def test_every_live_pass_line_of_2026_10_26_is_refused(stack, capsys):
    """Frame 330's line of 18:20 is the red test of frame 340's Ends when."""
    lines = [row["line"] for row in LIVE["pass"]]
    assert 1288 in lines and len(lines) == 29
    for row in LIVE["pass"]:
        err = refused(stack, capsys, "20", "--text", row["body"])
        assert "has no Reach line" in err, row["line"]


def test_every_live_line_with_no_pass_is_accepted(stack):
    assert len(LIVE["not_pass"]) == 2
    for row in LIVE["not_pass"]:
        assert append(stack, "20", "--text", row["body"]) == 0, row["line"]


def test_a_pass_body_on_a_frame_with_a_reach_line_is_accepted(stack):
    assert append(stack, "21", "--text", "Pass 1 runs on a fresh implementer.") == 0


def test_force_close_never_bypasses_the_pass_gate(stack, capsys):
    err = refused(stack, capsys, "20", "--text", "Closed. Pass 2 built.",
                  "--force-close", "no reason")
    assert "has no Reach line" in err


# The close gate.

@pytest.mark.parametrize("body", [
    "Closed. The door refuses.",
    "**Popped.** The door refuses.",
    "**Met on night 3 of 3: 0 refusals.**",
    "Met, the door refuses.",
    "Pops on the count.",
    "The door refuses, and the frame closes on night 170.",
    "Moved to plans/archive/stack-2026-10-27.md.",
])
def test_a_close_below_the_count_is_refused_and_names_the_count(stack, capsys, body):
    err = refused(stack, capsys, "21", "--text", body)
    assert "1 of 10" in err and "night count" in err


def test_the_live_met_closes_of_2026_10_26_are_refused(stack, capsys):
    assert [row["line"] for row in LIVE["met"]] == [16, 241]
    for row in LIVE["met"]:
        assert "1 of 10" in refused(stack, capsys, "21", "--text", row["body"])
        assert "has no Reach line" in refused(stack, capsys, "20", "--text", row["body"])


def test_a_close_on_a_frame_with_no_reach_line_is_refused(stack, capsys):
    err = refused(stack, capsys, "20", "--text", "Closed. The gate refuses.")
    assert "frame 20 has no Reach line" in err


def test_a_reach_line_with_no_count_refuses_the_close(stack, capsys):
    stack.write_bytes(STACK.replace("Reach: 1 of 10,", "Reach: every door,")
                      .encode("utf-8"))
    err = refused(stack, capsys, "21", "--text", "Closed. The door refuses.")
    assert "the Reach line carries no count" in err


def test_the_last_reach_line_decides_the_close(stack, capsys):
    stack.write_bytes(STACK.replace(
        "- Reach: 1 of 10, the other nine doors take the same text.\n",
        "- Reach: 10 of 10, every door.\n- Reach: 1 of 10, a recount.\n")
        .encode("utf-8"))
    assert "1 of 10" in refused(stack, capsys, "21", "--text", "Closed. Done.")


def test_force_close_writes_its_reason_into_the_line(stack):
    assert append(stack, "21", "--text", "Closed. The door refuses.",
                  "--force-close", "frame 22 holds the other nine") == 0
    assert "(forced: frame 22 holds the other nine)" in stack.read_bytes().decode()


def test_force_close_on_a_body_the_gate_passes_writes_no_stamp(stack):
    assert append(stack, "21", "--text", "A plain note.",
                  "--force-close", "no reason") == 0
    assert "forced" not in stack.read_bytes().decode()


def test_force_close_with_a_ruling_is_refused(stack, capsys):
    refused(stack, capsys, "21", "--ruling", "closed", "--at", "02:35",
            "--force-close", "no reason")


def test_a_close_at_the_full_count_is_accepted(stack):
    stack.write_bytes(STACK.replace("Reach: 1 of 10", "Reach: 1 of 1")
                      .encode("utf-8"))
    assert append(stack, "21", "--text", "**Closed.** The door refuses.") == 0


def test_a_word_inside_the_body_is_not_a_close(stack):
    assert append(stack, "21", "--text", "Pass 1 runs. Frame 9 closed last week.") == 0


# The ruling.

def test_a_ruling_is_never_refused(stack):
    assert append(stack, "20", "--ruling", "closed, pass 1 runs now",
                  "--at", "02:35") == 0
    assert append(stack, "21", "--ruling", "Met on night 3, pass 1 runs now",
                  "--at", "02:36") == 0
