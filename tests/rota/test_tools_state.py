"""
The state print and the status tool, tested against a stack the test writes.

The fixture holds three frames: one held by one session with two status
lines, one open frame that waits on Roman with a `[med]` rating, and one
frame under `## Parked` that must not print.
"""
from __future__ import annotations

import json
import os
import shlex
import stat
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
    assert "12. A parked" not in out and "parked words" not in out


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
        "- Waits on: Roman's ruling [low].\n\n" % (n, n) for n in range(20, 30))
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


def test_the_line_goes_after_a_wrapped_last_status(repo, clock):
    """A wrapped status keeps its continuation lines above the new line."""
    wrapped = STACK.replace(
        "- Status 2026-10-17 11:00 (rota-01): the second line.\n",
        "- Status 2026-10-17 11:00 (rota-01): the second line\n"
        "  continues here\n  and here.\n")
    write(repo, wrapped)
    append(repo, "10", "--sid", "aaaa1111", "--text", "x", "--no-commit")
    lines = (repo / "plans" / "stack.md").read_bytes().decode().split("\n")
    at = lines.index("  and here.")
    assert lines[at - 1] == "  continues here"
    assert lines[at + 1] == "- Status 2031-01-02 03:04 (aaaa1111): x"
    assert lines[at + 2] == ""


def test_order_waits_are_not_open_decisions(repo, capsys):
    """A frame carries no wait on his order (ruled: Roman, 2026-10-12 23:40)."""
    extra = "".join(
        "### %d. Order %d (2026-10-17)\n\n- **Site: x.** Meta workflow.\n"
        "- Waits on: %s\n\n" % (n, n, wait) for n, wait in (
            (20, "Roman's order. Recommended after frame 9."),
            (21, "frame 9's close, then the sprint order."),
            (22, "nothing. Roman orders it."),
            (23, "Roman's order, and Roman's ruling on the door.")))
    write(repo, STACK.replace("## Parked", extra + "## Parked"))
    out = page(repo, capsys=capsys)
    assert "20. Order" not in out and "21. Order" not in out
    assert "22. Order" not in out
    assert "23. Order 23" in out, "a decision beside an order still counts"
    assert "Live things: 3 of 10" in out


def test_a_cited_ruling_is_not_an_open_decision(repo, capsys):
    """A mark cites a word he gave, and a wait names a word he has not."""
    extra = "".join(
        "### %d. Cited %d (2026-10-17)\n\n- **Site: x.** Meta workflow.\n"
        "- Waits on: %s\n\n" % (n, n, wait) for n, wait in (
            (30, "the gate. The repair is ruled (ruled: Roman, 2026-10-24 "
                 "01:05, \"Yes\")."),
            (31, "night 9's end (reasoned: Roman's own price, and the facts "
                 "page)."),
            (32, "Roman's ruling on the cap (observed: frame 9's count).")))
    write(repo, STACK.replace("## Parked", extra + "## Parked"))
    out = page(repo, capsys=capsys)
    assert "30. Cited" not in out and "31. Cited" not in out
    assert "32. Cited 32" in out, "a wait beside a mark still counts"
    assert "Live things: 3 of 10" in out


def test_a_ruling_finds_the_workflow_on_another_bullet(repo, clock):
    old = STACK.replace("- **Site: the brief.** Meta workflow. A story.",
                        "- **Site: the brief.** A story.\n- Rota workflow.")
    write(repo, old)
    append(repo, "11", "--sid", "aaaa1111", "--ruling", "yes", "--at", "23:50",
           "--date", "2031-01-01", "--no-commit")
    text = (repo / "plans" / "stack.md").read_bytes().decode()
    assert ('**ruled. Roman, 2031-01-01 23:50, in the terminal: "yes"** '
            '(ruled: Roman, in his words). Rota workflow.') in text


def test_a_tag_after_the_sid_does_not_unhold_a_frame(repo, capsys):
    write(repo, STACK.replace("(Roman) (aaaa1111)", "(Roman) (aaaa1111) (parked)"))
    out = page(repo, "--sid", "aaaa1111", capsys=capsys)
    assert "10. The held frame changes a door (2026-10-17) (Roman) (parked)" in out


def test_an_unknown_frame_writes_nothing(repo, clock):
    before = (repo / "plans" / "stack.md").read_bytes()
    assert append(repo, "99", "--sid", "aaaa1111", "--text", "x") == 2
    assert (repo / "plans" / "stack.md").read_bytes() == before


# The print for Roman's return, `--since`.

SINCE_STACK = STACK.replace(
    "- Status 2026-10-17 11:00 (rota-01): the second line.\n",
    "- Status 2026-10-17 11:00 (rota-01): the second line.\n"
    "- Status 2026-10-18 01:00 (rota-01): taken by timeout at 01:00, "
    "Roman's low question on the door.\n"
    "- Status 2026-10-18 02:00 (rota-01): **ruled. Roman, 2026-10-18 01:58, "
    "in the terminal: \"yes\"** (ruled: Roman, in his words).\n"
    "- Status 2026-10-15 09:00 (rota-01): old (reasoned: Roman would agree) "
    "and (ruled: Roman, 2026-10-14 10:00).\n").replace(
    "- Pointer: `plans/y.md`.\n",
    "- Pointer: `plans/y.md`.\n"
    "- Status 2026-10-18 03:00 (rota-02): the ask stands (ruled: Roman, "
    "2026-10-17 22:00, on the scope).\n").replace(
    "### 11. The open ask",
    "### 13. A high ask (2026-10-17)\n\n- **Site: y.** Meta workflow.\n"
    "- Waits on: Roman's ruling [high].\n\n### 14. An order (2026-10-17)\n\n"
    "- **Site: y.** Meta workflow.\n- Waits on: Roman's order.\n\n"
    "### 11. The open ask")


def archive(repo: Path, day: str, text: str) -> None:
    path = repo / "plans" / "archive" / ("stack-%s.md" % day)
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


@pytest.fixture
def since_repo(repo):
    write(repo, SINCE_STACK)
    archive(repo, "2026-10-18", "# Archive\n\n### 7. A closed door frame "
            "(2026-10-10) (aaaa1111)\n\n- Status 2026-10-18 00:00 (x): closed.\n")
    archive(repo, "2026-10-16", "### 6. Closed too early (2026-10-01)\n")
    archive(repo, "head-rules-2026-10-18", "### 5. Not a stack archive\n")
    return repo


def test_since_prints_five_sections_and_nothing_else(since_repo, capsys):
    out = page(since_repo, "--since", "2026-10-17", capsys=capsys)
    heads = [x for x in out.splitlines() if x.startswith("## ")]
    assert heads == ["## Closed since 2026-10-17", "## Put down since 2026-10-17",
                     "## Decided under assumption since 2026-10-17",
                     "## Waits on Roman", "## Rulings since 2026-10-17"]
    assert "Held by" not in out and "Live things" not in out


def test_since_lists_the_archived_frames_from_the_date(since_repo, capsys):
    out = page(since_repo, "--since", "2026-10-17", capsys=capsys)
    assert "7. A closed door frame (2026-10-10) (archived 2026-10-18)" in out
    assert "6. Closed too early" not in out
    assert "5. Not a stack archive" not in out


def test_since_lists_assumptions_and_rulings_newest_first(since_repo, capsys):
    out = page(since_repo, "--since", "2026-10-17", capsys=capsys)
    section = out.split("## Decided under assumption")[1].split("## Waits")[0]
    assert "taken by timeout at 01:00" in section
    assert "old (reasoned" not in out, "a line before the date stays out"
    rulings = out.split("## Rulings since 2026-10-17")[1]
    rows = [x for x in rulings.splitlines() if x.strip() and "::" in x]
    assert rows[0].startswith("11. The open ask waits on him (2026-10-17) :: "
                              "- Status 2026-10-18 03:00")
    assert rows[1].startswith("10. The held frame") and '"yes"' in rows[1]
    assert len(rows) == 2


def test_since_ranks_the_waits_and_drops_the_order_waits(since_repo, capsys):
    out = page(since_repo, "--since", "2026-10-17", capsys=capsys)
    section = out.split("## Waits on Roman")[1].split("## Rulings")[0]
    rows = [x for x in section.splitlines() if x.startswith("[")]
    assert rows[0].startswith("[high] 13. A high ask")
    assert rows[1].startswith("[med] 11. The open ask")
    assert "14. An order" not in out


def test_since_cuts_the_oldest_rows_to_the_cap(since_repo, capsys):
    many = "".join("- Status 2026-10-18 %02d:%02d (rota-01): taken by timeout, "
                   "Roman's question %d %s.\n" % (h, m, h * 60 + m, "x" * 200)
                   for h in range(4, 10) for m in range(0, 60, 2))
    write(since_repo, SINCE_STACK.replace(
        "- Pointer: `plans/x.md`.\n", "- Pointer: `plans/x.md`.\n" + many))
    out = page(since_repo, "--since", "2026-10-17", capsys=capsys)
    assert len(out) <= 12000
    assert "older rows cut to keep the page under 12000 characters." in out
    assert "Roman's question 598" in out, "the newest row stays"
    assert "Roman's question 240 " not in out, "the oldest row goes"


def test_since_refuses_a_value_that_is_not_a_date(since_repo):
    assert state.main(["--stack", str(since_repo / "plans" / "stack.md"),
                       "--since", "yesterday"]) == 2


def with_statuses(repo: Path, *lines: str) -> None:
    """Add status lines to frame 10 of the --since fixture."""
    write(repo, SINCE_STACK.replace(
        "- Pointer: `plans/x.md`.\n",
        "- Pointer: `plans/x.md`.\n" + "".join(x + "\n" for x in lines)))


def rulings_of(out: str) -> list[str]:
    return [x for x in out.split("## Rulings since")[1].splitlines() if "::" in x]


def test_an_undated_ruling_mark_counts_by_the_status_date(since_repo, capsys):
    """Frame 114's status of 2026-10-17 16:51 carries his words and no mark date."""
    with_statuses(since_repo,
                  '- Status 2026-10-17 16:51 (rota-7d): **Roman, 2026-10-17 about '
                  '16:50, in the terminal: "File writes were always permitted"** '
                  '(ruled: Roman, in his words).',
                  "- Status 2026-10-16 09:00 (rota-7d): (ruled: Roman, in his words) "
                  "before the date.")
    out = page(since_repo, "--since", "2026-10-17", capsys=capsys)
    assert any("File writes were always permitted" in r for r in rulings_of(out))
    assert "before the date" not in out


def test_a_ruling_cited_again_is_folded_into_the_first(since_repo, capsys):
    with_statuses(since_repo,
                  "- Status 2026-10-18 05:00 (rota-01): as ruled (ruled: Roman, "
                  "2026-10-18 01:58, the same).",
                  "- Status 2026-10-18 06:00 (rota-01): again (ruled: Roman, "
                  "2026-10-18 01:58).")
    out = page(since_repo, "--since", "2026-10-17", capsys=capsys)
    rows = rulings_of(out)
    assert len(rows) == 2
    assert rows[1].startswith("10. The held frame") and '"yes"' in rows[1]
    assert rows[1].endswith("(cited again 2 times)")


def test_only_the_assumed_marks_count_as_assumptions(since_repo, capsys):
    with_statuses(since_repo,
                  "- Status 2026-10-18 05:00 (rota-01): pass 2 runs (assumed: he "
                  "would take the cheap fix).",
                  "- Status 2026-10-18 06:00 (rota-01): a plan step (reasoned: "
                  "Roman's design).")
    out = page(since_repo, "--since", "2026-10-17", capsys=capsys)
    section = out.split("## Decided under assumption")[1].split("## Waits")[0]
    assert "(assumed: he would take the cheap fix)" in section
    assert "taken by timeout at 01:00" in section
    assert "a plan step" not in section


def test_a_wait_of_nothing_is_no_decision_and_impact_words_rate(since_repo, capsys):
    text = SINCE_STACK.replace(
        "- Waits on: Roman's ruling [high].",
        "- Waits on: nothing. Roman ruled the shape [high].").replace(
        "- Waits on: Roman's ruling on the door [med].",
        "- Waits on: Roman's ruling, medium impact.")
    write(since_repo, text)
    out = page(since_repo, "--since", "2026-10-17", capsys=capsys)
    section = out.split("## Waits on Roman")[1].split("## Rulings")[0]
    rows = [x for x in section.splitlines() if x.startswith("[")]
    assert rows == ["[med] 11. The open ask waits on him (2026-10-17): "
                    "Roman's ruling, medium impact."]


def test_a_ruling_on_a_closed_frame_shows_from_the_archive(since_repo, capsys):
    archive(since_repo, "2026-10-18",
            "### 7. A closed door frame (2026-10-10) (aaaa1111)\n\n"
            "- Status 2026-10-18 00:30 (x): **ruled. Roman, 2026-10-18 00:29, in "
            'the terminal: "close it"** (ruled: Roman, in his words).\n'
            "- Status 2026-10-18 00:40 (x): closed (assumed: he wanted it closed).\n")
    out = page(since_repo, "--since", "2026-10-17", capsys=capsys)
    assert any(r.startswith("7. A closed door frame (2026-10-10) (closed) :: ")
               and "close it" in r for r in rulings_of(out))
    assert "(closed) :: - Status 2026-10-18 00:40" in out


def test_the_cap_cuts_closed_rows_and_never_the_waits(since_repo, capsys):
    many = "".join("### %d. A closed frame with a long name number %d %s (2026-10-10)\n"
                   % (n, n, "y" * 60) for n in range(300, 420))
    archive(since_repo, "2026-10-18", many)
    with_statuses(since_repo, *[
        "- Status 2026-10-18 %02d:%02d (rota-01): (ruled: Roman, 2026-10-18 "
        "%02d:%02d) words %s." % (h, m, h, m, "z" * 150)
        for h in range(4, 8) for m in range(0, 60, 6)])
    out = page(since_repo, "--since", "2026-10-17", capsys=capsys)
    assert len(out) <= 12000
    closed = out.split("## Closed since")[1].split("## Decided")[0]
    assert "older rows cut to keep the page under 12000 characters." in closed
    assert "300. A closed frame" in closed, "the first row of the newest file stays"
    assert "419. A closed frame" not in closed
    rulings = out.split("## Rulings since")[1]
    assert "older rows cut" in rulings
    assert "[high] 13. A high ask" in out and "[med] 11. The open ask" in out


# The put-down: a session puts a frame down with one reason (ruled: Roman,
# 2026-11-10 08:17).

BATCH = ("### 15. A batch frame (2026-10-20) (Roman) (aaaa1111)\n\n"
         "- **Site: y.** Meta workflow.\n- Waits on: nothing.\n"
         "- Status 2026-10-20 09:00 (rota-01): batched.\n\n")
PUT_STACK = STACK.replace("## Parked", "## The batches\n\n" + BATCH + "## Parked")
DAY = "2031-01-02"
ARCHIVE = "plans/archive/stack-%s.md" % DAY


def put(repo: Path, frame: str, reason: str, *argv: str) -> int:
    return append(repo, frame, "--sid", "aaaa1111", "--put-down", reason, *argv)


def row(frame: str, title: str, reason: str) -> str:
    stop = "" if reason.endswith((".", "?", "!")) else "."
    return "- %s. %s Put down %s 03:04 (rota-39): %s%s Block: %s." % (
        frame, title, DAY, reason, stop, ARCHIVE)


def frames_of(repo: Path) -> dict[str, state.Frame]:
    return {f.number: f for f in state.parse(
        state.read_lines(repo / "plans" / "stack.md"), bounded=False)}


@pytest.fixture
def put_repo(repo, clock):
    write(repo, PUT_STACK)
    enrol(repo, "aaaa1111", "rota-39")
    return repo


def test_a_put_down_under_the_batches_moves_the_block_whole(put_repo):
    assert put(put_repo, "15", "the batch ended", "--no-commit") == 0
    text = (put_repo / "plans" / "stack.md").read_bytes().decode("utf-8")
    assert text == (STACK + "\n## Put down\n\n" + status.PUT_DOWN_HEAD + "\n\n"
                    + row("15", "A batch frame (2026-10-20)", "the batch ended")
                    + "\n").replace("## Parked", "## The batches\n\n## Parked"), \
        "every other byte of the stack stays"
    last = "- Status %s 03:04 (rota-39): Put down by aaaa1111: the batch ended" % DAY
    assert (put_repo / ARCHIVE).read_bytes().decode("utf-8") == (
        "# Frames popped on %s\n\n" % DAY + BATCH.rstrip("\n") + "\n" + last + "\n")


def test_a_put_down_of_a_parked_frame_names_its_holder_and_continues(put_repo, capsys):
    assert put(put_repo, "12", "parked too long", "--no-commit") == 0
    out = capsys.readouterr().out
    assert "WARNING: session bbbb2222 holds frame 12, and session aaaa1111 puts it down." in out
    assert "12" not in frames_of(put_repo)
    archived = (put_repo / ARCHIVE).read_bytes().decode("utf-8")
    assert "### 12. A parked frame that must not print" in archived
    assert "parked words." in archived
    text = (put_repo / "plans" / "stack.md").read_bytes().decode("utf-8")
    assert "## Parked\n\n## Put down\n" in text
    assert row("12", "A parked frame that must not print (2026-10-01)",
               "parked too long") in text


def test_a_second_put_down_appends_and_its_line_stands_first(put_repo):
    assert put(put_repo, "15", "first", "--no-commit") == 0
    assert put(put_repo, "10", "second", "--no-commit") == 0
    archived = (put_repo / ARCHIVE).read_bytes().decode("utf-8")
    assert archived.count("# Frames popped on") == 1
    assert archived.index("### 15.") < archived.index("### 10.")
    assert "\n\n### 10. The held frame" in archived, "a blank line parts the blocks"
    text = (put_repo / "plans" / "stack.md").read_bytes().decode("utf-8")
    section = text.split("## Put down\n")[1].splitlines()
    rows = [x for x in section if x.startswith("- ")]
    assert rows == [row("10", "The held frame changes a door (2026-10-17)", "second"),
                    row("15", "A batch frame (2026-10-20)", "first")]


def test_the_put_down_section_is_not_part_of_the_last_parked_frame(put_repo):
    put(put_repo, "15", "done", "--no-commit")
    lines = frames_of(put_repo)["12"].lines
    assert not any("Put down" in x for x in lines)
    assert lines[-1] == "", "the frame ends at the line before the section"


def test_a_put_down_keeps_crlf_and_lf(put_repo):
    put(put_repo, "15", "lf", "--no-commit")
    for rel in ("plans/stack.md", ARCHIVE):
        assert b"\r" not in (put_repo / rel).read_bytes()
    (put_repo / ARCHIVE).unlink()
    write(put_repo, PUT_STACK, eol="\r\n")
    put(put_repo, "15", "crlf", "--no-commit")
    for rel in ("plans/stack.md", ARCHIVE):
        data = (put_repo / rel).read_bytes()
        assert data.count(b"\n") == data.count(b"\r\n"), rel
    assert b"Put down by aaaa1111: crlf\r\n" in (put_repo / ARCHIVE).read_bytes()


@pytest.mark.parametrize("frame, reason", [("15", ""), ("15", "  \n "), ("99", "why")])
def test_an_empty_reason_or_an_unknown_frame_changes_nothing(put_repo, frame, reason):
    before = (put_repo / "plans" / "stack.md").read_bytes()
    assert put(put_repo, frame, reason) == 2
    assert (put_repo / "plans" / "stack.md").read_bytes() == before
    assert not (put_repo / "plans" / "archive").exists()


def test_no_commit_commits_nothing(put_repo):
    head = git(put_repo, "rev-parse", "HEAD")
    assert put(put_repo, "15", "batch", "--no-commit") == 0
    assert git(put_repo, "rev-parse", "HEAD") == head


def test_the_commit_holds_the_stack_and_the_archive_alone(put_repo, capsys):
    git(put_repo, "commit", "-q", "-am", "the batch stack")
    (put_repo / "other.txt").write_bytes(b"two\n")
    git(put_repo, "add", "other.txt")
    assert put(put_repo, "15", "the batch ended") == 0
    assert "committed" in capsys.readouterr().out
    files = git(put_repo, "show", "--name-only", "--format=", "HEAD").split()
    assert sorted(files) == [ARCHIVE, "plans/stack.md"]
    assert git(put_repo, "log", "-1", "--format=%s") == \
        "docs(plans): frame 15, put down, the batch ended"
    assert git(put_repo, "diff", "--cached", "--name-only") == "other.txt"


def test_since_prints_the_put_down_line_and_not_a_close(put_repo, capsys):
    put(put_repo, "15", "the batch ended", "--no-commit")
    archive(put_repo, DAY, (put_repo / ARCHIVE).read_bytes().decode("utf-8")
            + "\n### 7. A closed door frame (2026-10-10)\n")
    out = page(put_repo, "--since", "2031-01-01", capsys=capsys)
    closed = out.split("## Closed since 2031-01-01")[1].split("## Put down since")[0]
    assert "7. A closed door frame (2026-10-10) (archived %s)" % DAY in closed
    assert "15." not in closed, "a put-down frame did not close"
    section = out.split("## Put down since 2031-01-01")[1].split("## Decided")[0]
    assert row("15", "A batch frame (2026-10-20)", "the batch ended") in section
    later = page(put_repo, "--since", "2031-01-03", capsys=capsys)
    assert later.split("## Put down since 2031-01-03\n")[1].startswith("None.")


def test_a_put_down_frame_leaves_open_frames_and_the_counts(put_repo, capsys):
    stack = put_repo / "plans" / "stack.md"
    assert 15 in state.open_frames(stack)
    assert "Live things: 3 of 10" in page(put_repo, capsys=capsys)
    put(put_repo, "15", "done", "--no-commit")
    assert state.open_frames(stack) == {10, 11, 12}
    assert "Live things: 2 of 10" in page(put_repo, capsys=capsys)


# The repairs of `plans/f363-putdown-review-p1.md`, pass 1b. Each test names
# its finding, and each one fails on 2ef34070.

def test_since_marks_each_row_of_a_put_down_frame_put_down(put_repo, capsys):
    """Finding 1: a ruling and an assumption on a put-down frame never read closed."""
    write(put_repo, PUT_STACK.replace(
        "- Status 2026-10-20 09:00 (rota-01): batched.\n",
        "- Status 2026-10-20 09:00 (rota-01): batched.\n"
        "- Status 2031-01-02 01:00 (rota-01): **ruled. Roman, 2031-01-02 00:59, "
        "in the terminal: \"drop it\"** (ruled: Roman, in his words).\n"
        "- Status 2031-01-02 02:00 (rota-01): dropped (assumed: he wanted it "
        "dropped).\n"))
    put(put_repo, "15", "he dropped it", "--no-commit")
    out = page(put_repo, "--since", "2031-01-01", capsys=capsys)
    rows = [x for x in out.splitlines() if x.startswith("15. ") and " :: " in x]
    assert len(rows) == 2, out
    assert all("(2026-10-20) (Roman) (put down) :: " in x for x in rows), rows
    assert "(closed)" not in out


def test_the_put_down_row_keeps_the_reason_and_cuts_the_title(put_repo, capsys):
    """Finding 4: the cut takes the title, never the reason or the block's path."""
    title = "A batch frame " + "with a long name " * 12
    write(put_repo, PUT_STACK.replace("A batch frame (2026-10-20)",
                                      title + "(2026-10-20)"))
    reason = "the reason runs long " * 15 + "and ends here."
    put(put_repo, "15", reason, "--no-commit")
    text = (put_repo / "plans" / "stack.md").read_bytes().decode("utf-8")
    stacked = [x for x in text.splitlines() if x.startswith("- 15. ")][0]
    assert stacked.startswith("- 15. " + state.cut(title + "(2026-10-20)",
                                                   state.NAME_LIMIT) + " Put down ")
    assert stacked.endswith(": %s Block: %s." % (reason, ARCHIVE))
    out = page(put_repo, "--since", "2031-01-01", capsys=capsys)
    section = out.split("## Put down since 2031-01-01\n")[1].split("\n\n")[0]
    assert section == stacked, "the print keeps the row the tool wrote"
    long_row = stacked.replace(state.cut(title + "(2026-10-20)", state.NAME_LIMIT),
                               title + "(2026-10-20)")
    write(put_repo, text.replace(stacked, long_row))
    out = page(put_repo, "--since", "2031-01-01", capsys=capsys)
    section = out.split("## Put down since 2031-01-01\n")[1].split("\n\n")[0]
    assert section == stacked, "the print cuts a long title the same way"


@pytest.mark.parametrize("reason, shown", [
    ("plain", "plain."), ("done.", "done."), ("why?", "why?"), ("now!", "now!")])
def test_a_reason_with_no_end_mark_gets_a_full_stop(put_repo, reason, shown):
    """The assistant's question 3 of pass 1."""
    put(put_repo, "15", reason, "--no-commit")
    text = (put_repo / "plans" / "stack.md").read_bytes().decode("utf-8")
    assert "(rota-39): %s Block: %s." % (shown, ARCHIVE) in text


def test_a_failed_stack_write_leaves_the_block_once_after_a_rerun(put_repo, capsys):
    """Finding 5: the rerun does not append the block to the archive again."""
    stack = put_repo / "plans" / "stack.md"
    before = stack.read_bytes()
    os.chmod(stack, stat.S_IREAD)
    try:
        assert put(put_repo, "15", "first try", "--no-commit") == 1
    finally:
        os.chmod(stack, stat.S_IREAD | stat.S_IWRITE)
    err = capsys.readouterr().err
    assert "the stack write failed" in err and ARCHIVE in err
    assert stack.read_bytes() == before
    assert (put_repo / ARCHIVE).read_bytes().decode("utf-8").count("### 15.") == 1
    assert put(put_repo, "15", "second try", "--no-commit") == 0
    assert "holds the block of frame 15 already" in capsys.readouterr().out
    assert (put_repo / ARCHIVE).read_bytes().decode("utf-8").count("### 15.") == 1
    assert "15" not in frames_of(put_repo)


def test_a_failed_archive_write_exits_1_and_keeps_the_stack(put_repo, capsys):
    """Finding 5: a directory at the archive path gives exit 1, no traceback."""
    (put_repo / ARCHIVE).mkdir(parents=True)
    before = (put_repo / "plans" / "stack.md").read_bytes()
    assert put(put_repo, "15", "no archive", "--no-commit") == 1
    assert "the archive write failed" in capsys.readouterr().err
    assert (put_repo / "plans" / "stack.md").read_bytes() == before


def test_a_failed_commit_prints_the_command_that_commits(put_repo, capsys):
    """Finding 6: the session can run the printed command, and it says whole."""
    git(put_repo, "commit", "-q", "-am", "the batch stack")
    hook = put_repo / ".git" / "hooks" / "pre-commit"
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_bytes(b"#!/bin/sh\nexit 1\n")
    assert put(put_repo, "15", "the batch ended") == 1
    line = [x for x in capsys.readouterr().err.splitlines() if "Run: " in x][0]
    assert "takes the archive file of the day whole" in line
    command = line.split("Run: ", 1)[1]
    assert command.endswith("-- %s %s" % (
        (put_repo / "plans" / "stack.md").resolve().as_posix(),
        (put_repo / ARCHIVE).resolve().as_posix()))
    hook.unlink()
    subprocess.run(shlex.split(command), check=True, capture_output=True)
    files = git(put_repo, "show", "--name-only", "--format=", "HEAD").split()
    assert sorted(files) == [ARCHIVE, "plans/stack.md"]


def test_the_archive_opens_to_append_and_never_to_rewrite(put_repo, monkeypatch):
    """Finding 8: a kill during the write cannot cut off an earlier block."""
    opened = []

    def recorded(path, mode="r", *args, **kwargs):
        opened.append((Path(path).name, mode))
        return open(path, mode, *args, **kwargs)

    monkeypatch.setattr(status, "open", recorded, raising=False)
    put(put_repo, "15", "first", "--no-commit")
    put(put_repo, "10", "second", "--no-commit")
    assert [m for name, m in opened if name == "stack-%s.md" % DAY] == ["ab", "ab"]
    archived = (put_repo / ARCHIVE).read_bytes().decode("utf-8")
    assert archived.startswith("# Frames popped on %s\n\n### 15." % DAY)
    assert "batched.\n- Status" in archived and "\n\n### 10. " in archived


def test_a_line_written_during_the_debt_check_survives(put_repo, monkeypatch):
    """Finding 2: the stack is read after the check of the debts, not before."""
    stack = put_repo / "plans" / "stack.md"

    def other_session(path, frame):
        text = path.read_bytes().decode("utf-8")
        path.write_bytes(text.replace(
            "- Pointer: `plans/y.md`.\n",
            "- Pointer: `plans/y.md`.\n- Status 2031-01-02 03:03 (rota-77): "
            "another session.\n").encode("utf-8"))
        return []

    monkeypatch.setattr(status, "suite_reds", other_session)
    assert put(put_repo, "15", "done", "--no-commit") == 0
    text = stack.read_bytes().decode("utf-8")
    assert "(rota-77): another session." in text
    assert "15" not in frames_of(put_repo)
