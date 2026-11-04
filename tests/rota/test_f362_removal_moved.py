"""
A statement that moves word for word into a block nested in its own block
is not lost (frame 362, dry run 4, wall 13).

Dry run 4, turn 8 (2026-11-03): s206 edited `_foldline` of icalendar's
`src/icalendar/parser/string.py` at `8e706696`. The three statements of an
`else` block moved into `if not found_boundary:` inside the same block,
word for word. The compare read the three statements as lost. The
Architect's `touch_strayed` judged the edit a mistake, and the right change
stopped (`plans/dry4-read-2026-11-03.md`, section 8, wall 13).

A move out of a block, or to a sibling block, stays a removal. The frame 7
shapes "12 else arm gone" and "14 guard gone" rule that a statement that
leaves its guard is a removal.
"""
from __future__ import annotations

import pytest

from rota.roles import api

# `_foldline` at 8e706696^ and at 8e706696, word for word, except that the
# escape `" \-"` is written `" \\-"`. The invalid escape gives a
# SyntaxWarning at the parse, and the compare does not read the text.
FOLD_BASE = r'''
def _foldline(line: str, limit: int = 75, fold_sep: str = "\r\n ") -> str:
    """Make a string folded as defined in RFC5545."""
    assert isinstance(line, str)
    assert "\n" not in line

    folded_lines: list[str] = []
    current_chars: list[str] = []
    byte_count = 0
    for char in line:
        char_byte_len = len(char.encode(DEFAULT_ENCODING))
        if current_chars and byte_count + char_byte_len >= limit:
            if len(current_chars) > 1 and current_chars[-1] in r"\^":
                escaped_prefix = current_chars.pop()
                folded_lines.append("".join(current_chars))
                current_chars = [escaped_prefix]
                byte_count = len(escaped_prefix.encode(DEFAULT_ENCODING))
            else:
                folded_lines.append("".join(current_chars))
                current_chars = []
                byte_count = 0
        current_chars.append(char)
        byte_count += char_byte_len

    if current_chars:
        folded_lines.append("".join(current_chars))

    return fold_sep.join(folded_lines)
'''
FOLD_HEAD = r'''
def _foldline(line: str, limit: int = 75, fold_sep: str = "\r\n ") -> str:
    """Make a string folded as defined in RFC5545."""
    assert isinstance(line, str)
    assert "\n" not in line

    folded_lines: list[str] = []
    current_chars: list[str] = []
    byte_count = 0
    for char in line:
        char_byte_len = len(char.encode(DEFAULT_ENCODING))
        if current_chars and byte_count + char_byte_len >= limit:
            if len(current_chars) > 1 and current_chars[-1] in r"\^":
                escaped_prefix = current_chars.pop()
                folded_lines.append("".join(current_chars))
                current_chars = [escaped_prefix]
                byte_count = len(escaped_prefix.encode(DEFAULT_ENCODING))
            else:
                # Find a valid word boundary (space or hyphen) to fold at.
                # If no valid boundary exists, do not fold this line.
                found_boundary = False
                for i in range(len(current_chars) - 1, -1, -1):
                    if current_chars[i] in " \\-":
                        folded_lines.append("".join(current_chars[:i+1]))
                        current_chars = current_chars[i+1:]
                        byte_count = len(current_chars[0].encode(DEFAULT_ENCODING)) if current_chars else 0
                        found_boundary = True
                        break
                if not found_boundary:
                    # No valid boundary found; keep the line as-is.
                    folded_lines.append("".join(current_chars))
                    current_chars = []
                    byte_count = 0
        current_chars.append(char)
        byte_count += char_byte_len

    if current_chars:
        folded_lines.append("".join(current_chars))

    return fold_sep.join(folded_lines)
'''


def test_the_foldline_edit_of_dry_run_4_removes_nothing():
    assert api._removal_entry(FOLD_BASE, FOLD_HEAD) is None


def test_the_foldline_edit_with_one_statement_dropped_names_that_statement():
    """The fix keeps recall: a moved block that lacks one statement still
    names the statement it lacks."""
    head = FOLD_HEAD.replace("                    current_chars = []\n", "", 1)
    assert head != FOLD_HEAD
    e = api._removal_entry(FOLD_BASE, head)
    assert [g["shown"] for g in api._gone_statements(head, e)] == [
        "`current_chars = []` at line 19"]


# The shapes of a move, word for word, into a block nested in the old
# statement's own block. Before frame 362 the compare named each one lost.
MOVED_IN = {
    "a new if with no else": (
        "def f(c):\n    go()\n    stop()\n",
        "def f(c):\n    if c:\n        go()\n    stop()\n"),
    "the else arm of a new if": (
        "def f(c):\n    go()\n",
        "def f(c):\n    if c:\n        raise ValueError()\n    else:\n        go()\n"),
    "a new elif arm": (
        "def f(a, b):\n    go()\n",
        "def f(a, b):\n    if a:\n        log()\n    elif b:\n        go()\n"),
    "a new loop over many items": (
        "def f(ps):\n    go()\n",
        "def f(ps):\n    for p in ps:\n        go()\n"),
    "a new while loop": (
        "def f(n):\n    go()\n",
        "def f(n):\n    while n:\n        go()\n        n -= 1\n"),
    "a new except handler": (
        "def f():\n    go()\n",
        "def f():\n    try:\n        run()\n    except OSError:\n        go()\n"),
    "a new finally": (
        "def f():\n    go()\n",
        "def f():\n    try:\n        run()\n    finally:\n        go()\n"),
    "a new match case": (
        "def f(x):\n    go()\n",
        "def f(x):\n    match x:\n        case 1:\n            go()\n"),
    "a block that the old text holds already": (
        "def f(c):\n    if c:\n        one()\n    go()\n",
        "def f(c):\n    if c:\n        one()\n        go()\n"),
    "two levels deep": (
        "def f(ps, c):\n    go()\n",
        "def f(ps, c):\n    for p in ps:\n        if c:\n            go()\n"),
    "a compound statement under a new guard": (
        "def f(a, c):\n    if a:\n        go()\n",
        "def f(a, c):\n    if c:\n        if a:\n            go()\n"),
    "a renamed local under a new guard": (
        "def f(c):\n    tmp = load()\n    go(tmp)\n",
        "def f(c):\n    data = load()\n    if c:\n        go(data)\n"),
}


@pytest.mark.parametrize("name", sorted(MOVED_IN))
def test_a_move_into_a_nested_block_is_no_removal(name):
    base, now = MOVED_IN[name]
    assert api._removal_entry(base, now) is None, name


def test_a_reorder_inside_one_block_is_no_removal():
    """The compare reads a block with no order. Frame 362 keeps that."""
    assert api._removal_entry("def f():\n    one()\n    two()\n",
                              "def f():\n    two()\n    one()\n") is None


# A statement that leaves its block runs on paths that its guard excluded.
# Each shape stays a removal.
STILL_LOST = {
    "out of an if whose header stays": (
        "def f(c):\n    if c:\n        one()\n        two()\n",
        "def f(c):\n    if c:\n        one()\n    two()\n",
        ["`two()` at line 3"]),
    "to a sibling block": (
        "def f(a, b):\n    if a:\n        one()\n    if b:\n        two()\n",
        "def f(a, b):\n    if a:\n        pass\n    if b:\n        two()\n        one()\n",
        ["`one()` at line 2"]),
    "into a nested definition": (
        "def f():\n    go()\n",
        "def f():\n    def g():\n        go()\n    return g\n",
        ["`go()` at line 1"]),
    "a repeated statement whose nested copy stays": (
        "def f(c):\n    go()\n    if c:\n        go()\n",
        "def f(c):\n    if c:\n        go()\n",
        ["`go()` at line 1"]),
    "a rewrite under a new guard": (
        "def f(c):\n    go(1)\n",
        "def f(c):\n    if c:\n        go(2)\n",
        ["`go(1)` at line 1"]),
}


@pytest.mark.parametrize("name", sorted(STILL_LOST))
def test_a_move_out_of_a_block_stays_a_removal(name):
    base, now, shown = STILL_LOST[name]
    e = api._removal_entry(base, now)
    assert e, name
    assert [g["shown"] for g in api._gone_statements(now, e)] == shown
