"""
A whole-file write that drops a statement inside a kept definition opens
a note (frame 283, pass 5).

Review 3 of frame 306, "High 2, pinned": the span branch of `code.write`
calls `_drop_note`, which reads each statement of the span. The
whole-file branch called only `_whole_drop` and `_tail_drop`. So a first
whole-file write that dropped `ctx.exit()` inside the kept
`version_option` opened no note, and the commit landed. Frame 283's
mechanism refused a commit that removes a statement no landed note names,
whatever reply wrote it. Frame 339: the commit lands, and the removal is an
open stray for the Architect.
"""
from __future__ import annotations

from tests.rota.test_frame283_removal_on_ruling import (  # noqa: F401
    BASE, MESSAGE, PATH, _call, _developer, _git, _staged, _strays, db)
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
    out = _call(sb, "code.commit", message=MESSAGE)
    assert out["committed"] is True, out
    assert _git(root, "rev-parse", "HEAD") != head
    assert _strays(sb) == [(f"{PATH}::version_option.callback", "open",
                            "removal: `ctx.exit()` at line 550")]


def test_the_whole_file_drop_lands_when_a_criterion_asks_for_it(db, tmp_path):
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('cr_4','tk1',"
               "'After --version, the callback must no longer call ctx.exit(), so "
               "the command body runs.')")
    db.commit()
    sb, _root = _developer(db, tmp_path)
    assert _call(sb, "code.write", path=PATH, text=NESTED)["dropped"] == NOTE
    sb.begin_reply()
    assert _call(sb, "code.commit", message=MESSAGE)["committed"] is True
    assert _strays(sb) == []


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
def test_review_5s_shapes_open_a_note_and_land_as_a_stray(db, tmp_path, name):
    old, new, (owner, line) = SHAPES[name]
    sb, root = _small(db, tmp_path, old)
    out = _call(sb, "code.write", path=PATH, text=new)
    assert _quote_in(line, out["dropped"])
    assert [x[:2] for x in _lines(sb)] == [[owner, line]]
    sb.begin_reply()
    assert _call(sb, "code.commit", message=MESSAGE)["committed"] is True
    rows = _strays(sb)
    assert [r[:2] for r in rows] == [(f"{PATH}::{owner}" if owner else PATH, "open")]
    assert _quote_in(line, rows[0][2]) and rows[0][2].startswith("removal: ")


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


def test_a_rewrite_of_one_statement_with_the_same_kind_opens_no_note(db, tmp_path):
    """Pass 6, the kind count: `return x` to `return x + 1` keeps one Return
    under `keep`, so the write is a rewrite and the commit lands. Review 5
    named this shape `price`, and finding 3 of the count page accepts it."""
    old = _l("def keep(x):", "    y = x", "    return x")
    sb, root = _small(db, tmp_path, old)
    head = _git(root, "rev-parse", "HEAD")
    out = _call(sb, "code.write", path=PATH, text=old.replace("return x", "return x + 1"))
    assert "dropped" not in out
    assert PATH not in api._open_notes(sb.ctx)
    sb.begin_reply()
    assert _call(sb, "code.commit", message=MESSAGE)["committed"] is True
    assert _git(root, "rev-parse", "HEAD") != head


def test_the_s340_shape_names_each_dropped_statement_and_lands_as_strays(db, tmp_path):
    """Night 154's s340 dropped `ctx.exit()` and the tail of the kept
    `version_option`, and put nothing of those kinds in their place. The
    commit lands with one stray per owner (frame 339)."""
    lines = TEXT.splitlines(keepends=True)
    assert lines[556].strip() == "if not param_decls:"
    assert lines[564].strip() == "return option(*param_decls, **kwargs)"
    text = "".join(lines[:550] + lines[551:556] + lines[565:])
    sb, root = _developer(db, tmp_path)
    head = _git(root, "rev-parse", "HEAD")
    out = _call(sb, "code.write", path=PATH, text=text)
    assert "8 statements" in out["dropped"]
    assert [x[1] for x in _lines(sb)] == [
        "ctx.exit()", "if not param_decls:", 'kwargs.setdefault("is_flag", True)',
        'kwargs.setdefault("expose_value", False)', 'kwargs.setdefault("is_eager", True)',
        'kwargs.setdefault("help", _("Show the version and exit."))',
        'kwargs["callback"] = callback', "return option(*param_decls, **kwargs)"]
    sb.begin_reply()
    assert _call(sb, "code.commit", message=MESSAGE)["committed"] is True
    assert _git(root, "rev-parse", "HEAD") != head
    assert sorted(r[0] for r in _strays(sb)) == [
        f"{PATH}::version_option", f"{PATH}::version_option.callback"]


def test_one_of_two_statements_of_a_kind_kept_names_the_one_gone(db, tmp_path):
    old = _l("def keep():", "    return 0", "", "", "def f(x):", "    go()", "    stop()")
    sb, _root = _small(db, tmp_path, old)
    out = _call(sb, "code.write", path=PATH, text=old.replace("    go()" + NL, ""))
    assert out["dropped"] == ("This write removes or rewrites 1 statement that your "
                              "text does not hold: `go()` at line 5.")
    assert [x[:2] for x in _lines(sb)] == [["f", "go()"]]


def test_a_top_level_drop_beside_a_nested_rewrite_names_the_top_level_line(db, tmp_path):
    old = _l("import sys", "go()", "stop()", "", "", "def keep(x):", "    return x")
    new = old.replace("stop()" + NL, "").replace("return x", "return x + 1")
    sb, _root = _small(db, tmp_path, old)
    out = _call(sb, "code.write", path=PATH, text=new)
    # `_whole_drop` names the top-level line, so `_whole_lost` names it not twice.
    assert out["dropped"] == ("This write drops 1 line of the old file, from `stop()`; "
                              "write the whole file again with those lines kept.")
    assert [x[1] for x in _lines(sb)] == ["stop()"]


def test_the_refused_commit_names_both_routes_for_a_rewrite(db, tmp_path):
    """Pass 5c: the re-probe of review 5. "Put the line back" alone undoes a
    wanted edit, so the refusal says how to undo it and how to keep it.
    Pass 6: the whole-file branch admits a same-kind rewrite, and the span
    branch keeps its line-key rule. So a span write carries the rewrite.
    Pass 8b: the span branch admits a rewrite whose new statement at the
    same place holds the old tokens. `print(x)` at the place of `return x`
    does not hold `return`, so the rewrite still opens a note. Frame 339:
    the refusal of the write's own reply names the commit of the next reply
    as the route to keep it, and that commit lands."""
    old = _l("def keep(x):", "    y = x", "    return x")
    sb, _root = _small(db, tmp_path, old)
    out = _call(sb, "code.write", path=PATH, text="    print(x)" + NL, start=2, end=3)
    assert _quote_in("return x", out["dropped"])
    got = _call(sb, "code.commit", message=MESSAGE)["refused"]
    assert got.endswith(
        "A note does not close a removal. To undo the change, put "
        "the lines back with code.write, then commit in your next reply. To keep "
        "the change, commit in your next reply. The Architect then judges the "
        "removal before the batch merges.")
    sb.begin_reply()
    assert _call(sb, "code.commit", message=MESSAGE)["committed"] is True
