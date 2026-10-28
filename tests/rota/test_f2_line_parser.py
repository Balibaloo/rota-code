"""Fact F2: one parser reads his words into page lines and acts.

Rule C76 builds a fix at its reach. `api._line_reading` is the one reader
of his line references and their cues. Each test below holds words where
a reader's old regex and the parser disagree, so it is red on 28873d55.
The last tests pin the one-reader property at the source.
"""
from __future__ import annotations

import ast
import re
import sqlite3
from pathlib import Path

import rota
from rota.roles import api

PACKAGE = Path(rota.__file__).parent

# A bare "3 is wrong" after a colon or a full stop is a line reference,
# because the parser cuts the sentences first (frame 305, review 1).
AFTER_COLON = "Fix this: 3 is wrong."
AFTER_STOP = "Line 2 is fine. 3 is wrong."


def test_reading_unpacks_as_the_pair_and_carries_the_refs():
    reading = api._line_reading("Please drop note 8. Note 9 is fine.")
    faulted, matched = reading
    assert (faulted, matched) == ({8}, {9})
    assert reading == ({8}, {9})
    assert [(r.word, set(r.lines)) for r in reading.refs] == [
        ("note", {8}), ("note", {9})]
    assert reading.named == {8, 9}


def test_item_sentences_reads_a_note_as_a_page_line():
    # The old page cue read "lines? N" only. The page calls lines 5 and up
    # the team's notes (frame 234, pass 2).
    rest, page = api._item_sentences("Note 7 should go. The flag is wrong.")
    assert page[:1] == ["Note 7 should go."]


def test_page_reply_fault_names_a_note_cue():
    got = api._page_reply_fault(None, "x", "Note 7 should go away.",
                                "Note 7 should go away.")
    assert got and "'Note 7'" in got


def test_about_a_check_reads_the_check_on_a_note():
    assert api._about_a_check("Please fix the check on note 7.")
    assert api._about_a_check("Note 7 is too weak.")
    assert not api._about_a_check("Line 3 of the summary is long.")


def test_pointer_fault_skips_a_bare_fault_with_through():
    words = "The tests touch the wrong file. Lines 2 through 4 are wrong."
    assert api.pointer_fault(words, 2) is True


def test_unnumbered_reads_a_bare_reference_after_a_colon():
    assert api._unnumbered([AFTER_COLON]) == []


def test_unnamed_contest_reads_a_bare_reference_after_a_colon():
    got = api._unnamed_contest([AFTER_COLON], {3, 4}, set(), 5)
    assert got is not None and "4" in got


def _messages(*bodies: str) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE messages (id TEXT, cause_id TEXT, verb TEXT, "
                 "from_role TEXT, body_text TEXT, seq INTEGER)")
    for i, body in enumerate(bodies):
        conn.execute("INSERT INTO messages VALUES (?, 'ask', 'converse', "
                     "'principal', ?, ?)", (f"m{i}", body, i))
    return conn


def test_earlier_sources_reads_a_bare_reference_after_a_colon():
    got = api._earlier_sources(_messages(AFTER_COLON), "ask", "reply", 5)
    assert got == {3: ("m0", AFTER_COLON)}


def test_earlier_reading_reads_a_bare_reference_after_a_full_stop():
    named, fine = api._earlier_reading(_messages(AFTER_STOP), "ask",
                                       "reply", 5)
    assert named == {2, 3}
    assert fine == {2}


# The pin. The names below are the parser's line rule and cue lists. Only
# the parser's own functions in api.py read them. A second reader goes red.
PARSER_NAMES = {
    "_LINE_REF", "_LINE_FAULT", "_LINE_WORD", "_BARE_FAULT_TAIL",
    "_PAGE_WORD", "_CHECK_AFTER", "_CHECK_BEFORE", "_ref_lines",
    "_line_refs", "_line_cues", "_live_cues",
    # The deleted cue lists stay deleted.
    "_PAGE_CUE", "_LINE_CHECK", "_CUE_BARE_FAULT",
}
DELETED = {"_PAGE_CUE", "_LINE_CHECK", "_CUE_BARE_FAULT"}
PARSER_SITES = {
    "<module>", "_ref_lines", "_line_refs", "_line_reading", "LineReading",
    "_line_cues", "_live_cues", "_agreement", "_instruction_cue",
    "_contrast_cue",
}
# A line-reference regex in a string literal: "lines?\s", "lines? \d" or
# "(?:lines?|notes?)".
LINE_REGEX = re.compile(r"lines\?(?:\\s|\s\\d)|lines\?\|notes\?")
LINE_REGEX_HOMES = {"_LINE_REF", "_LINE_WORD"}


def _hits(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))

    def walk(node, scope):
        for child in ast.iter_child_nodes(node):
            inner = scope
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.ClassDef)):
                inner = child.name if scope == "<module>" else scope
            name = (child.id if isinstance(child, ast.Name) else
                    child.attr if isinstance(child, ast.Attribute) else
                    child.name if isinstance(child, ast.alias) else None)
            if name in PARSER_NAMES:
                yield inner, name, getattr(child, "lineno", node.lineno)
            yield from walk(child, inner)

    return tree, list(walk(tree, "<module>"))


def test_no_second_reader_of_the_line_rule():
    api_path = PACKAGE / "roles" / "api.py"
    strays = []
    for path in sorted(PACKAGE.rglob("*.py")):
        _tree, hits = _hits(path)
        for scope, name, line in hits:
            if name in DELETED or path != api_path or scope not in PARSER_SITES:
                strays.append(f"{path.relative_to(PACKAGE)}:{line} {scope} {name}")
    assert strays == []


def test_no_second_line_reference_regex():
    api_path = PACKAGE / "roles" / "api.py"
    homes: set[int] = set()
    tree, _hits_api = _hits(api_path)
    for node in tree.body:
        if (isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id in LINE_REGEX_HOMES
                for t in node.targets)):
            homes |= set(range(node.lineno, node.end_lineno + 1))
    strays = []
    for path in sorted(PACKAGE.rglob("*.py")):
        for i, text in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            if text.lstrip().startswith("#"):
                continue
            if LINE_REGEX.search(text) and not (path == api_path and i in homes):
                strays.append(f"{path.relative_to(PACKAGE)}:{i}")
    assert strays == []
