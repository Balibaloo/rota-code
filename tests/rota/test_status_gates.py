"""
The two gates of rule C76 in the status tool, tested on a stack the test writes.

Rule C76 of `plans/method/reference.md` says an issue is read before it
is fixed. The status tool refuses a pass line on a frame with no Reach
line. It refuses a close while the Reach line covers fewer places than
its count. The fixture holds two frames: frame 20 has no Reach line, and
frame 21 has `Reach: 1 of 10`.
"""
from __future__ import annotations

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


def test_the_reader_returns_the_text_after_reach_or_none():
    lines = STACK.split("\n")
    frames = {f.number: f for f in state.parse(lines, bounded=False)}
    assert state.reach_line(frames["20"].lines) is None
    assert state.reach_line(frames["21"].lines) == \
        "1 of 10, the other nine doors take the same text."


@pytest.mark.parametrize("body", [
    "Pass 1 runs on a fresh implementer.",
    "pass 2b built, 4 files.",
    "Pass 3 is at its second cycle.",
    "The implementer of frame 20 runs now.",
])
def test_a_pass_body_on_a_frame_with_no_reach_line_is_refused(stack, capsys, body):
    before = stack.read_bytes()
    assert append(stack, "20", "--text", body) == 2
    assert stack.read_bytes() == before
    err = capsys.readouterr().err
    assert ('frame 20 has no Reach line. Write "- Reach: <k> of <N>, '
            '<where the gap is>" after the Waits on line before any pass.') in err


@pytest.mark.parametrize("body", [
    "The read of pass 1 runs on one agent.",
    "The review of pass 1 runs on Opus.",
    "Pass 1 is at the gate.",
])
def test_a_read_a_review_or_a_gate_is_not_a_pass_line(stack, body):
    assert append(stack, "20", "--text", body) == 0
    assert body in stack.read_bytes().decode()


def test_a_pass_body_on_a_frame_with_a_reach_line_is_accepted(stack):
    assert append(stack, "21", "--text", "Pass 1 runs on a fresh implementer.") == 0


def test_force_close_never_bypasses_the_pass_gate(stack):
    before = stack.read_bytes()
    assert append(stack, "20", "--text", "Pass 1 runs.",
                  "--force-close", "no reason") == 2
    assert stack.read_bytes() == before


@pytest.mark.parametrize("body", [
    "Closed. The door refuses.",
    "**Popped.** The door refuses.",
    "Pass 1 landed. **closes** on the night count.",
])
def test_a_close_below_the_count_is_refused_and_names_the_count(stack, capsys, body):
    before = stack.read_bytes()
    assert append(stack, "21", "--text", body) == 2
    assert stack.read_bytes() == before
    assert "1 of 10" in capsys.readouterr().err


def test_a_close_on_a_frame_with_no_reach_line_is_refused(stack, capsys):
    before = stack.read_bytes()
    assert append(stack, "20", "--text", "Closed. The gate refuses.") == 2
    assert stack.read_bytes() == before
    assert "frame 20 has no Reach line" in capsys.readouterr().err


def test_force_close_writes_its_reason_into_the_line(stack):
    assert append(stack, "21", "--text", "Closed. The door refuses.",
                  "--force-close", "frame 22 holds the other nine") == 0
    assert ("- Status 2031-01-02 03:04 (aaaa1111): Closed. The door refuses. "
            "(forced: frame 22 holds the other nine)") in stack.read_bytes().decode()


def test_a_close_at_the_full_count_is_accepted(stack):
    stack.write_bytes(STACK.replace("Reach: 1 of 10", "Reach: 1 of 1")
                      .encode("utf-8"))
    assert append(stack, "21", "--text", "**Closed.** The door refuses.") == 0


def test_a_word_inside_the_body_is_not_a_close(stack):
    assert append(stack, "21", "--text", "Pass 1 runs. Frame 9 closed last week.") == 0


def test_a_ruling_is_never_refused(stack):
    assert append(stack, "20", "--ruling", "closed, pass 1 runs now",
                  "--at", "02:35") == 0
    assert append(stack, "21", "--ruling", "closed, pass 1 runs now",
                  "--at", "02:36") == 0
