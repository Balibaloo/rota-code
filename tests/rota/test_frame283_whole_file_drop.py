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

import pytest

from rota.core.sandbox import build
from rota.roles import api, prompts

TEXT = BASE.decode("utf-8")
EXIT = "        ctx.exit()\n"
# The first `ctx.exit()` of the file is the one in `version_option`'s
# callback, at line 551 of the fixture.
assert TEXT.splitlines()[550] == EXIT.rstrip("\n")
NESTED = TEXT.replace(EXIT, "", 1)
NOTE = ("This write removes or rewrites 1 statement that your text does not hold: "
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
        "whole file again with those lines kept. This write removes or rewrites 1 statement "
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


# Review 5 of frame 283, probe `r5/test_p5r.py`: the shapes that opened no
# note at 05fd6976, each on a small two-commit worktree.
NL = chr(10)


def _l(*xs: str) -> str:
    return NL.join(xs) + NL


def _small(db, tmp_path, old: str):
    root = tmp_path / "wt"
    (root / PATH).parent.mkdir(parents=True)
    _git_init(root)
    for msg in ("fork", "head"):
        (root / PATH).write_text(old, encoding="utf-8", newline="")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "--allow-empty", "-m", msg)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'bg_3'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="bg_3", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    return sb, root


CLS = _l("class Box:", "    def a(self):", "        self.n = 1", "        return self.v",
         "", "    def b(self):", "        return self.v")
DUP = _l("def f(x):", "    if x:", "        go()", "        return 1", "    go()",
         "    return 2")
NEST = _l("def f(x):", "    def inner():", "        go()", "        stop()", "    stop()",
          "    return inner")
IFB = _l("import sys", "", "", "def keep():", "    return 0", "", "", "if sys.argv:",
         "    go()", "    stop()")
IFD = _l("import sys", "", "", "def keep():", "    return 0", "", "", "if sys.argv:",
         "    def h():", "        go()", "        stop()")
NODEF = _l("import sys", "go()", "stop()", "sys.exit(0)")
SHAPES = {
    # A copy in another method hid the drop (finding 1).
    "class_shared_line": (CLS, CLS.replace(_l("        self.n = 1", "        return self.v"),
                                           _l("        self.n = 1")),
                          ("Box.a", "return self.v")),
    # One of two copies in one definition (finding 1).
    "dup_inside_one_def": (DUP, DUP.replace(_l("        go()", "        return 1"),
                                            _l("        return 1")), ("f", "go()")),
    # A copy in the outer body hid the inner drop (finding 1).
    "nested_inner_shared_with_outer": (NEST, NEST.replace(_l("        go()", "        stop()"),
                                                          _l("        go()")),
                                       ("f.inner", "stop()")),
    # A statement under a top-level `if` (finding 2).
    "toplevel_if_block": (IFB, IFB.replace(_l("    stop()"), ""), ("", "stop()")),
    # A def under a top-level `if` (finding 2).
    "def_inside_if_block": (IFD, IFD.replace(_l("        stop()"), ""), ("h", "stop()")),
    # A file with no definition (finding 2).
    "no_def_file_middle": (NODEF, NODEF.replace(_l("stop()"), ""), ("", "stop()")),
}


@pytest.mark.parametrize("name", sorted(SHAPES))
def test_review_5s_shapes_open_a_note_and_hold_the_commit(db, tmp_path, name):
    old, new, (owner, line) = SHAPES[name]
    sb, root = _small(db, tmp_path, old)
    out = _call(sb, "code.write", path=PATH, text=new)
    assert _quote_in(line, out["dropped"])
    assert [x[:2] for x in _lines(sb)] == [[owner, line]]
    sb.begin_reply()
    head = _git(root, "rev-parse", "HEAD")
    assert "refused" in _call(sb, "code.commit", message=MESSAGE)
    assert _git(root, "rev-parse", "HEAD") == head


def _quote_in(line: str, note: str) -> bool:
    return f"`{line}`" in note


def test_a_definition_moved_under_a_class_is_named_in_the_note(db, tmp_path):
    """Finding 3: the note stores `defs: ["f"]`, so its text names `f`, and
    a top-level `f` again restores the note."""
    old = _l("def keep():", "    return 0", "", "", "def f(x):", "    go()", "    stop()")
    new = _l("def keep():", "    return 0", "", "", "class C:", "    def f(self, x):",
             "        go()")
    sb, root = _small(db, tmp_path, old)
    out = _call(sb, "code.write", path=PATH, text=new)
    assert api._open_notes(sb.ctx)[PATH]["defs"] == ["f"]
    assert "`f`" in out["dropped"]
    assert api._restored(old, api._open_notes(sb.ctx)[PATH])


def test_an_edited_line_is_named_as_removed_or_rewritten(db, tmp_path):
    """Finding 4: `return x` to `return x + 1` is a rewrite, and the note
    and the refusal say so in both branches' words."""
    old = _l("def keep(x):", "    y = x", "    return x")
    sb, _root = _small(db, tmp_path, old)
    out = _call(sb, "code.write", path=PATH, text=old.replace("return x", "return x + 1"))
    assert out["dropped"] == ("This write removes or rewrites 1 statement that your "
                              "text does not hold: `return x` at line 2.")
    sb.begin_reply()
    got = _call(sb, "code.commit", message=MESSAGE)["refused"]
    assert "removal or a rewrite" in got and "name the change" in got


def test_the_refused_commit_names_both_routes_for_a_rewrite(db, tmp_path):
    """Pass 5c: the re-probe of review 5. "Put the line back" alone undoes a
    wanted edit, so the refusal says how to undo it and how to keep it."""
    old = _l("def keep(x):", "    y = x", "    return x")
    sb, _root = _small(db, tmp_path, old)
    _call(sb, "code.write", path=PATH, text=old.replace("return x", "return x + 1"))
    sb.begin_reply()
    got = _call(sb, "code.commit", message=MESSAGE)["refused"]
    assert got.endswith(
        "A note does not allow a removal or a rewrite. To undo the change, put "
        "the line back with code.write, then commit in your next reply. To keep "
        "the change, send msg.escalate_architect and name the change to the "
        "Architect.")
