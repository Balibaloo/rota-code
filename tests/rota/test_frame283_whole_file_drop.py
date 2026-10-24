"""
A whole-file write that drops a statement inside a kept definition opens
a note (frame 283, pass 5).

Review 3 of frame 306, "High 2, pinned": the span branch of `code.write`
calls `_drop_note`, which reads each statement of the span. The
whole-file branch called only `_whole_drop` and `_tail_drop`. So a first
whole-file write that dropped `ctx.exit()` inside the kept
`version_option` opened no note, and the commit landed. Frame 283's
mechanism refuses a commit that removes a statement no landed note names,
whatever reply wrote it.
"""
from __future__ import annotations

from tests.rota.test_frame283_removal_on_ruling import (  # noqa: F401
    BASE, FIRST, MESSAGE, PATH, _call, _developer, _git, _staged, db)
import subprocess

from rota.core.sandbox import build
from rota.roles import api, prompts

TEXT = BASE.decode("utf-8")
EXIT = "        ctx.exit()\n"
# The first `ctx.exit()` of the file is the one in `version_option`'s
# callback, at line 551 of the fixture.
assert TEXT.splitlines()[550] == EXIT.rstrip("\n")
NESTED = TEXT.replace(EXIT, "", 1)
NOTE = ("This write removes 1 statement that your text does not hold: "
        "`ctx.exit()` at line 550.")


def _git_init(root) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)


def _lines(sb) -> list:
    return api._open_notes(sb.ctx)[PATH]["lines"]


def test_a_whole_file_write_that_drops_a_nested_statement_opens_a_note(db, tmp_path):
    sb, root = _developer(db, tmp_path)
    head = _git(root, "rev-parse", "HEAD")
    out = _call(sb, "code.write", path=PATH, text=NESTED)
    assert out["dropped"] == NOTE
    assert [x[1] for x in _lines(sb)] == ["ctx.exit()"]
    assert [v["status"] for v in _staged(sb)] == ["open"]
    sb.begin_reply()
    assert _call(sb, "code.commit", message=MESSAGE) == {"refused": FIRST}
    assert _git(root, "rev-parse", "HEAD") == head


def test_the_whole_file_drop_lands_when_a_criterion_asks_for_it(db, tmp_path):
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('cr_4','tk1',"
               "'After --version, the callback must no longer call ctx.exit(), so "
               "the command body runs.')")
    db.commit()
    sb, _root = _developer(db, tmp_path)
    assert _call(sb, "code.write", path=PATH, text=NESTED)["dropped"] == NOTE
    sb.begin_reply()
    assert _call(sb, "code.commit", message=MESSAGE)["committed"] is True


def test_a_whole_file_write_that_keeps_every_statement_opens_no_note(db, tmp_path):
    sb, _root = _developer(db, tmp_path)
    out = _call(sb, "code.write", path=PATH, text=TEXT + "\n\nEXTRA = 1\n")
    assert "dropped" not in out
    assert PATH not in api._open_notes(sb.ctx)
    assert not _staged(sb)


def test_a_top_level_and_a_nested_drop_give_one_note_with_both_lines(db, tmp_path):
    """Every top-level name of the night's file is used, and the use door
    refuses its drop. So this case uses a small file with a free name."""
    root = tmp_path / "wt"
    (root / PATH).parent.mkdir(parents=True)
    _git_init(root)
    small = ("import sys\n\nUNUSED = 1\n\n\ndef version_option(x):\n"
             "    if x:\n        print(x)\n        sys.exit()\n    return x\n")
    for msg in ("fork", "head"):
        (root / PATH).write_text(small, encoding="utf-8", newline="")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "--allow-empty", "-m", msg)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'bg_3'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="bg_3", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    text = small.replace("UNUSED = 1\n", "").replace("        sys.exit()\n", "")
    out = _call(sb, "code.write", path=PATH, text=text)
    assert out["dropped"] == (
        "This write drops 1 line of the old file, from `UNUSED = 1`; write the "
        "whole file again with those lines kept. This write removes 1 statement "
        "that your text does not hold: `sys.exit()` at line 8.")
    got = [x[1] for x in _lines(sb)]
    assert got == ["UNUSED = 1", "sys.exit()"]
    assert [v["status"] for v in _staged(sb)] == ["open"]


def test_a_later_write_that_puts_the_nested_line_back_closes_the_note(db, tmp_path):
    sb, root = _developer(db, tmp_path)
    _call(sb, "code.write", path=PATH, text=NESTED)
    sb.begin_reply()
    assert "dropped" not in _call(sb, "code.write", path=PATH, text=TEXT)
    sb.begin_reply()
    assert _call(sb, "code.commit", message=MESSAGE).get("committed") is not True
    assert [v["status"] for v in _staged(sb)][-1] == "restored"
