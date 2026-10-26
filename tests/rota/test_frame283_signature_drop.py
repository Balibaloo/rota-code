"""
A write that drops a parameter or a decorator opens a note (frame 283, W-D
of night 164).

Night 164, bg_2, s229, call 11: a span write on `src/click/utils.py` lines
439 to 483 rewrote `format_filename`'s header and dropped `shorten: bool =
False,` at line 441. The body kept `if shorten:`. `_drop_note` returned
None, commit 63c65435 landed, and the red count went from 2 to 5. Both
walks read a function's body only. Repair B of `plans/frame283-wd-read.md`
makes each parameter and each decorator a statement under its definition.

Line numbers in a note are code.source numbers, 0-based. Frame 339: the
commit after the note lands, and the dropped parameter or decorator is an
open stray for the Architect.
"""
from __future__ import annotations

from tests.rota.test_frame283_removal_on_ruling import (  # noqa: F401
    MESSAGE, PATH, _call, _git, _staged, _strays, db)
from tests.rota.test_frame283_whole_file_drop import _l, _lines, _small
import ast
import subprocess

from rota.roles import api

CLICK = "D:/repos/_AI/sample_repos/clickI"

SIG = _l("import os", "", "", "def format_filename(", "    filename,",
         "    shorten: bool = False,", ") -> str:", '    """Format a filename."""',
         "    if shorten:", "        filename = os.path.basename(filename)",
         "    return os.fspath(filename)")
# The span of `format_filename`, lines 3 to 10, as code.write reads it.
START, END = 3, 11
DROPPED = SIG.replace("    shorten: bool = False," + chr(10), "")
DOC = SIG.replace("Format a filename.", "Format a filename for display.")
NOTE = ("This write removes or rewrites 1 statement that your text does not hold: "
        "`shorten: bool = False,` at line 5.")


def _span(text: str) -> str:
    """The text of `format_filename` alone, lines 3 to 10."""
    return chr(10).join(text.splitlines()[START:END]) + chr(10)


def test_s229s_span_write_that_drops_a_parameter_opens_a_note(db, tmp_path):
    sb, root = _small(db, tmp_path, SIG)
    head = _git(root, "rev-parse", "HEAD")
    out = _call(sb, "code.write", path=PATH, text=_span(DROPPED), start=START, end=END)
    assert out["dropped"] == NOTE
    assert [x[:2] for x in _lines(sb)] == [["format_filename", "shorten: bool = False,"]]
    assert [v["status"] for v in _staged(sb)] == ["open"]
    sb.begin_reply()
    assert _call(sb, "code.commit", message=MESSAGE)["committed"] is True
    assert _git(root, "rev-parse", "HEAD") != head
    rows = _strays(sb)
    assert [r[:2] for r in rows] == [(f"{PATH}::format_filename", "open")]
    assert "`shorten: bool = False,`" in rows[0][2]


def test_the_commit_lands_after_a_write_puts_the_parameter_back(db, tmp_path):
    sb, root = _small(db, tmp_path, SIG)
    head = _git(root, "rev-parse", "HEAD")
    _call(sb, "code.write", path=PATH, text=_span(DROPPED), start=START, end=END)
    sb.begin_reply()
    assert "dropped" not in _call(sb, "code.write", path=PATH, text=_span(DOC),
                                  start=START, end=END)
    sb.begin_reply()
    assert _call(sb, "code.commit", message=MESSAGE)["committed"] is True
    assert _git(root, "rev-parse", "HEAD") != head
    assert [v["status"] for v in _staged(sb)][-1] == "restored"


def test_a_whole_file_write_that_drops_a_parameter_opens_a_note(db, tmp_path):
    sb, root = _small(db, tmp_path, SIG)
    head = _git(root, "rev-parse", "HEAD")
    out = _call(sb, "code.write", path=PATH, text=DROPPED)
    assert out["dropped"] == NOTE
    assert [x[:2] for x in _lines(sb)] == [["format_filename", "shorten: bool = False,"]]
    sb.begin_reply()
    assert _call(sb, "code.commit", message=MESSAGE)["committed"] is True
    assert _git(root, "rev-parse", "HEAD") != head
    assert [r[0] for r in _strays(sb)] == [f"{PATH}::format_filename"]


def test_a_span_write_that_changes_only_the_docstring_opens_no_note(db, tmp_path):
    """The night's 57 other commits kept every parameter, and still land."""
    sb, root = _small(db, tmp_path, SIG)
    head = _git(root, "rev-parse", "HEAD")
    out = _call(sb, "code.write", path=PATH, text=_span(DOC), start=START, end=END)
    assert "dropped" not in out
    assert PATH not in api._open_notes(sb.ctx)
    sb.begin_reply()
    assert _call(sb, "code.commit", message=MESSAGE)["committed"] is True
    assert _git(root, "rev-parse", "HEAD") != head


def test_a_new_default_of_the_same_parameter_opens_no_note(db, tmp_path):
    sb, _root = _small(db, tmp_path, SIG)
    text = _span(SIG.replace("shorten: bool = False,", "shorten: bool = True,"))
    assert "dropped" not in _call(sb, "code.write", path=PATH, text=text,
                                  start=START, end=END)


DEC = _l("import functools", "", "", "@functools.lru_cache()", "def f(x):", "    return x")


def test_a_dropped_decorator_opens_a_note(db, tmp_path):
    sb, root = _small(db, tmp_path, DEC)
    head = _git(root, "rev-parse", "HEAD")
    out = _call(sb, "code.write", path=PATH, text=_l("def f(x):", "    return x"),
                start=3, end=6)
    assert out["dropped"] == ("This write removes or rewrites 1 statement that your "
                              "text does not hold: `@functools.lru_cache()` at line 3.")
    assert [x[:2] for x in _lines(sb)] == [["f", "@functools.lru_cache()"]]
    sb.begin_reply()
    assert _call(sb, "code.commit", message=MESSAGE)["committed"] is True
    assert _git(root, "rev-parse", "HEAD") != head
    assert [r[0] for r in _strays(sb)] == [f"{PATH}::f"]


def test_a_kept_decorator_opens_no_note(db, tmp_path):
    sb, _root = _small(db, tmp_path, DEC)
    text = _l("@functools.lru_cache()", "def f(x):", "    return x + 1")
    out = _call(sb, "code.write", path=PATH, text=text, start=3, end=6)
    assert "refused" not in out, out
    assert "dropped" not in out
    assert PATH not in api._open_notes(sb.ctx)


ONE = _l('"""One line."""', "def f(a, b=1):", "    return a")


def test_a_one_line_signature_that_loses_a_parameter_names_its_line(db, tmp_path):
    sb, _root = _small(db, tmp_path, ONE)
    out = _call(sb, "code.write", path=PATH, text=_l("def f(a):", "    return a"),
                start=1, end=3)
    assert out["dropped"] == ("This write removes or rewrites 1 statement that your "
                              "text does not hold: `def f(a, b=1):` at line 1.")
    assert [x[:2] for x in _lines(sb)] == [["f", "def f(a, b=1):"]]


def test_a_renamed_parameter_opens_a_note(db, tmp_path):
    """The old key is gone, so a rename is a removal until a write puts the
    name back or a `ledger.log` names it."""
    sb, _root = _small(db, tmp_path, SIG)
    text = _span(SIG.replace("shorten: bool", "short: bool").replace("if shorten:", "if short:"))
    out = _call(sb, "code.write", path=PATH, text=text, start=START, end=END)
    assert "`shorten: bool = False,` at line 5" in out["dropped"]


def _night() -> tuple[list[str], int, int, str]:
    """The night's before text, the span of `format_filename` in it, and
    the text of call 11, from clickI's git when it is readable. Else a
    small copy of the header and the body."""
    def show(rev: str) -> str:
        return subprocess.run(["git", "-C", CLICK, "show", f"{rev}:src/click/utils.py"],
                              capture_output=True, check=True).stdout.decode("utf-8")

    def span(lines: list[str]) -> tuple[int, int]:
        tree = ast.parse(chr(10).join(lines))
        n = next(x for x in tree.body if getattr(x, "name", "") == "format_filename")
        return n.lineno - 1, n.end_lineno
    try:
        old, new = show("63c65435^").splitlines(), show("63c65435").splitlines()
    except (OSError, subprocess.CalledProcessError):
        old, new = SIG.splitlines(), DROPPED.splitlines()
    a, b = span(old)
    c, d = span(new)
    return old, a, b, chr(10).join(new[c:d])


def test_the_nights_texts_open_a_note_on_both_doors():
    old, a, b, text = _night()
    i = next(k for k in range(a, b) if old[k].strip() == "shorten: bool = False,")
    want = ("This write removes or rewrites 1 statement that your text does not hold: "
            f"`shorten: bool = False,` at line {i}.")
    assert api._drop_note(old, a, b, text) == want
    merged = chr(10).join(old[:a] + text.splitlines() + old[b:]) + chr(10)
    assert api._whole_lost(old, merged, None, []) == want


# Pass 2, the review of 07887a4b (`plans/frame283-review-wd.md`).
NOTE1 = "This write removes or rewrites 1 statement that your text does not hold: "


def test_a_new_parameter_beside_a_body_rewrite_opens_no_note(db, tmp_path):
    """Finding 1: the parts of a signature sat in the place index of
    `_rewritten_heads`, so an added parameter made a rewrite a removal."""
    old = _l("def f(a):", "    return")
    sb, _root = _small(db, tmp_path, old)
    out = _call(sb, "code.write", path=PATH, text=_l("def f(a, b=None):", "    return False"),
                start=0, end=2)
    assert "dropped" not in out


def test_a_new_decorator_beside_a_body_rewrite_opens_no_note(db, tmp_path):
    old = _l("from functools import cache", "", "", "def f(a):", "    go(a)")
    sb, _root = _small(db, tmp_path, old)
    out = _call(sb, "code.write", path=PATH, text=_l("@cache", "def f(a):", "    go(a, 1)"),
                start=3, end=5)
    assert "dropped" not in out


TWO = _l("import click", "", "", "@click.option(", '    "--a",', ")", "@click.option(",
         '    "--b",', ")", "def f(a, b):", "    return a")


def test_one_of_two_multi_line_decorators_dropped_is_named(db, tmp_path):
    """Finding 2: two decorators with the same first line shared one key."""
    sb, _root = _small(db, tmp_path, TWO)
    text = _l("@click.option(", '    "--a",', ")", "def f(a, b):", "    return a")
    out = _call(sb, "code.write", path=PATH, text=text, start=3, end=11)
    assert out["dropped"] == NOTE1 + "`@click.option(` at line 6."


def test_a_renamed_definition_over_its_header_names_the_old_header():
    """Finding 3: a span over the header alone holds no whole statement, so
    the walk named nothing when the merged file lost the owner."""
    old = ["def f(", "    a,", "    b,", "):", "    return a"]
    note = api._drop_note(old, 0, 4, _l("def g(", "    a,", "):"))
    assert note == NOTE1 + "`def f(` at line 0."


def test_a_whole_file_write_that_drops_two_parameters_of_one_line_names_it_once():
    """Finding 4: the bound `x <= a <= y` of `_whole_lost`."""
    old = ["def f(a, b):", "    return 1"]
    note = api._whole_lost(old, _l("def f():", "    return 1"), None, [])
    assert note == NOTE1 + "`def f(a, b):` at line 0."


# Pass 2b, finding 5 of the review: a decorator keyed on its whole text made
# each edit of its arguments a removal (probe p8).
OPT = _l("import click", "", "", "@click.option(", '    "--name",', '    default="a",', ")",
         "def f(name):", "    return name")


def test_an_edited_argument_inside_a_multi_line_decorator_opens_no_note(db, tmp_path):
    sb, _root = _small(db, tmp_path, OPT)
    text = _l(*OPT.splitlines()[3:]).replace('default="a"', 'default="b"')
    out = _call(sb, "code.write", path=PATH, text=text, start=3, end=9)
    assert "refused" not in out
    assert "dropped" not in out


def test_an_added_argument_of_a_one_line_decorator_opens_no_note(db, tmp_path):
    old = _l("import click", "", "", '@click.option("--name")', "def f(name):", "    return name")
    sb, _root = _small(db, tmp_path, old)
    text = _l('@click.option("--name", default="x")', "def f(name):", "    return name")
    out = _call(sb, "code.write", path=PATH, text=text, start=3, end=6)
    assert "refused" not in out, out
    assert "dropped" not in out


def test_an_added_argument_of_a_one_line_decorator_is_a_rewrite_at_the_note():
    """Pass 2c: the note itself reads the decorator as rewritten in place,
    not only the floor of `_changed_kept` in `code.write`."""
    old = ["import click", "", "", '@click.option("--name")', "def f(name):", "    return name"]
    text = _l('@click.option("--name", default="x")', "def f(name):", "    return name")
    assert api._drop_note(old, 3, 6, text) is None
