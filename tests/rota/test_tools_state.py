"""
The state print and the status tool, tested against a stack the test writes.

The fixture holds three frames: one held by one session with two status
lines, one open frame that waits on Roman with a `[med]` rating, and one
frame under `## Parked` that must not print.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

from rota.tools import state, status

STACK = """# The stack

## Stack

### 10. The held frame changes a door (2026-10-17) (Roman) (aaaa1111)

- **Site: `rota/roles/api.py`.** Rota workflow. A story.
- Ends when: the door refuses.
- Waits on: nothing.
- Sprint: this sprint, after frame 9.
- Pointer: `plans/x.md`.
- Status 2026-10-17 10:00 (rota-01): the first line.
- Status 2026-10-17 11:00 (rota-01): the second line.

### 11. The open ask waits on him (2026-10-17)

- **Site: the brief.** Meta workflow. A story.
- Ends when: he rules.
- Waits on: Roman's ruling on the door [med].
- Sprint: next sprint, rank 1.
- Pointer: `plans/y.md`.

## Parked

### 12. A parked frame that must not print (2026-10-01) (bbbb2222)

- **Site: nowhere.** Rota workflow.
- Waits on: Roman's order.
- Status 2026-10-01 09:00 (rota-02): parked words.
"""

GIT_ENV = {
    "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.invalid",
    "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "commit.gpgsign",
    "GIT_CONFIG_VALUE_0": "false",
}


def git(repo: Path, *args: str) -> str:
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                         text=True, check=True)
    return out.stdout.strip()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A git repository that holds the fixture stack, committed."""
    for key, value in GIT_ENV.items():
        monkeypatch.setenv(key, value)
    git(tmp_path, "init", "-q")
    (tmp_path / "plans").mkdir()
    write(tmp_path, STACK)
    (tmp_path / "other.txt").write_bytes(b"one\n")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "seed")
    return tmp_path


def write(root: Path, text: str, eol: str = "\n") -> Path:
    path = root / "plans" / "stack.md"
    path.write_bytes(text.replace("\n", eol).encode("utf-8"))
    return path


def enrol(root: Path, sid: str, name: str) -> None:
    sessions = root / ".handover" / "sessions"
    sessions.mkdir(parents=True, exist_ok=True)
    (sessions / (sid + ".json")).write_bytes(
        json.dumps({"sid": sid, "name": name}).encode("utf-8"))


def page(repo: Path, *argv: str, capsys=None) -> str:
    assert state.main(["--stack", str(repo / "plans" / "stack.md"), *argv]) == 0
    return capsys.readouterr().out


# The state print.

def test_the_held_frame_prints_its_four_lines(repo, capsys):
    out = page(repo, "--sid", "aaaa1111", capsys=capsys)
    assert "## Held by aaaa1111" in out
    assert "10. The held frame changes a door (2026-10-17) (Roman)\n" in out
    assert "  Site: `rota/roles/api.py`. Rota workflow." in out
    assert "  Waits on: nothing. | Sprint: this sprint, after frame 9." in out
    assert "- Status 2026-10-17 11:00 (rota-01): the second line." in out
    assert "the first line" not in out, "only the last status line prints"


def test_without_a_sid_every_holder_prints(repo, capsys):
    out = page(repo, capsys=capsys)
    assert "## Held by aaaa1111" in out
    assert "bbbb2222" not in out, "a parked frame's holder is not live"


def test_the_parked_frame_never_prints(repo, capsys):
    out = page(repo, capsys=capsys)
    assert "12." not in out and "parked words" not in out


def test_the_open_decision_carries_its_rating(repo, capsys):
    out = page(repo, capsys=capsys)
    assert ("[med] 11. The open ask waits on him (2026-10-17): "
            "Roman's ruling on the door [med].") in out
    assert "Live things: 2 of 10" in out
    assert "Over the frame economy" not in out
    assert out.rstrip().endswith("Read the frame's Pointer before you act on it.")


def test_over_ten_live_things_prints_and_never_refuses(repo, capsys):
    extra = "".join(
        "### %d. Ask %d (2026-10-17)\n\n- **Site: x.** Meta workflow.\n"
        "- Waits on: Roman's order [low].\n\n" % (n, n) for n in range(20, 30))
    write(repo, STACK.replace("## Parked", extra + "## Parked"))
    out = page(repo, capsys=capsys)
    assert "Live things: 12 of 10" in out
    assert "Over the frame economy by 2: park or close before you push." in out
    assert "[low] 20. Ask 20 (2026-10-17)" in out


def test_a_long_status_line_keeps_its_time_and_name(repo, capsys):
    long = STACK.replace("the second line.", "word " * 200)
    write(repo, long)
    out = page(repo, "--sid", "aaaa1111", "--limit", "120", capsys=capsys)
    line = [x for x in out.splitlines() if "- Status" in x][0].strip()
    assert line.startswith("- Status 2026-10-17 11:00 (rota-01): word")
    assert line.endswith("...") and len(line) <= 120


def note(repo: Path, where: str, sender: str) -> None:
    path = repo / where / ("handoff-%s.md" % sender)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(("rota-77\n\n## What happened\n\nfacts\n\n"
                      "## What I believe, and what to doubt\n\nDoubt the door.\n\n"
                      "## Live things\n\nnone\n").encode("utf-8"))


def test_the_claim_names_the_sender_and_its_doubts_print(repo, capsys):
    claims = repo / ".handover" / "claims"
    claims.mkdir(parents=True)
    (claims / "aaaa1111.json").write_bytes(json.dumps(
        {"frame": "10", "from_sid": "cccc3333", "sender_name": "rota-77"}).encode())
    note(repo, "plans", "cccc3333")
    out = page(repo, "--sid", "aaaa1111", capsys=capsys)
    assert "From cccc3333 (rota-77)." in out
    assert "Doubt the door." in out
    assert "facts" not in out and "none" not in out, "only the doubts section prints"


def test_a_taken_claim_still_names_the_sender(repo, capsys):
    """`take` moves the claim into a receipt, and the peer state names it."""
    box = repo / ".handover"
    (box / "taken").mkdir(parents=True)
    (box / "peers").mkdir()
    (box / "taken" / "aaaa1111-frame-10.json").write_bytes(
        json.dumps({"frame": "10", "from_sid": "cccc3333"}).encode())
    (box / "peers" / "aaaa1111.json").write_bytes(json.dumps(
        {"sid": "aaaa1111", "state": "holding", "from_sid": "cccc3333",
         "receipt": "aaaa1111-frame-10.json"}).encode())
    enrol(repo, "cccc3333", "rota-55")
    note(repo, "plans/method", "cccc3333")
    out = page(repo, "--sid", "aaaa1111", capsys=capsys)
    assert "From cccc3333 (rota-55)." in out
    assert "Doubt the door." in out


def test_a_sender_with_no_note_says_so(repo, capsys):
    out = page(repo, "--from", "dddd4444", capsys=capsys)
    assert "No momentum note found for dddd4444." in out


def test_the_print_never_edits_the_stack(repo, capsys):
    before = (repo / "plans" / "stack.md").read_bytes()
    page(repo, capsys=capsys)
    assert (repo / "plans" / "stack.md").read_bytes() == before


# The status tool.

@pytest.fixture
def clock(monkeypatch):
    monkeypatch.setattr(status, "_clock", lambda: datetime(2031, 1, 2, 3, 4))


def append(repo: Path, *argv: str) -> int:
    return status.main(["--stack", str(repo / "plans" / "stack.md"), *argv])


def test_the_line_goes_after_the_last_status_and_reads_the_clock(repo, clock):
    enrol(repo, "aaaa1111", "rota-39")
    assert append(repo, "10", "--sid", "aaaa1111", "--text", "a new\nline",
                  "--no-commit") == 0
    lines = (repo / "plans" / "stack.md").read_bytes().decode().split("\n")
    at = lines.index("- Status 2026-10-17 11:00 (rota-01): the second line.")
    assert lines[at + 1] == "- Status 2031-01-02 03:04 (rota-39): a new line"


def test_lf_stays_lf(repo, clock):
    append(repo, "10", "--sid", "aaaa1111", "--text", "x", "--no-commit")
    assert b"\r" not in (repo / "plans" / "stack.md").read_bytes()


def test_crlf_stays_crlf(repo, clock):
    write(repo, STACK, eol="\r\n")
    append(repo, "10", "--sid", "aaaa1111", "--text", "x", "--no-commit")
    data = (repo / "plans" / "stack.md").read_bytes()
    assert data.count(b"\n") == data.count(b"\r\n")
    assert b"- Status 2031-01-02 03:04 (aaaa1111): x\r\n" in data


def test_a_frame_with_no_status_takes_the_line_after_its_pointer(repo, clock):
    append(repo, "11", "--sid", "aaaa1111", "--text", "x", "--no-commit")
    lines = (repo / "plans" / "stack.md").read_bytes().decode().split("\n")
    at = lines.index("- Pointer: `plans/y.md`.")
    assert lines[at + 1].startswith("- Status 2031-01-02 03:04 (")


def test_a_sid_with_no_enrolment_is_written_and_warned(repo, clock, capsys):
    assert append(repo, "10", "--sid", "eeee5555", "--text", "x",
                  "--no-commit") == 0
    assert "WARNING" in capsys.readouterr().out
    assert b"(eeee5555): x" in (repo / "plans" / "stack.md").read_bytes()


def test_a_ruling_carries_his_words_and_the_workflow(repo, clock):
    enrol(repo, "aaaa1111", "rota-39")
    append(repo, "11", "--sid", "aaaa1111", "--ruling", "yes do it",
           "--at", "02:35", "--no-commit")
    text = (repo / "plans" / "stack.md").read_bytes().decode()
    assert ('- Status 2031-01-02 03:04 (rota-39): **ruled. Roman, 2031-01-02 '
            '02:35, in the terminal: "yes do it"** (ruled: Roman, in his words). '
            'Meta workflow.') in text


def test_a_body_file_keeps_its_backslashes(repo, clock, tmp_path):
    body = tmp_path / "body.txt"
    body.write_bytes(b"C:\\Users\\x and \\n stay\n")
    append(repo, "10", "--sid", "aaaa1111", "--body", str(body), "--no-commit")
    assert b"C:\\Users\\x and \\n stay" in (repo / "plans" / "stack.md").read_bytes()


def test_the_commit_holds_the_stack_alone(repo, clock, capsys):
    (repo / "other.txt").write_bytes(b"two\n")
    git(repo, "add", "other.txt")
    assert append(repo, "10", "--sid", "aaaa1111", "--text",
                  "one two three four five six seven eight nine") == 0
    assert "committed" in capsys.readouterr().out
    files = git(repo, "show", "--name-only", "--format=", "HEAD").split()
    assert files == ["plans/stack.md"]
    assert git(repo, "log", "-1", "--format=%s") == \
        "docs(plans): frame 10, one two three four five six seven eight"
    assert git(repo, "diff", "--cached", "--name-only") == "other.txt", \
        "the other staged file stays staged and out of the commit"


def test_an_unknown_frame_writes_nothing(repo, clock):
    before = (repo / "plans" / "stack.md").read_bytes()
    assert append(repo, "99", "--sid", "aaaa1111", "--text", "x") == 2
    assert (repo / "plans" / "stack.md").read_bytes() == before
