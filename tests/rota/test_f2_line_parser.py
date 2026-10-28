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
    # `said` reads the entry of a message first (wall W7), so the tables exist.
    conn.execute("CREATE TABLE entries (id TEXT, text TEXT)")
    conn.execute("CREATE TABLE config (key TEXT, value TEXT)")
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


# Fact F3, pass 1b. The reading carries what his words permit or ask of a
# named target. Each door reads it from the reading, not by its own list.


def test_reading_says_when_the_words_name_the_request():
    reading = api._line_reading("The version comes from the interpreter.")
    assert reading.names_request(("Take the version from the interpreter",))
    assert not reading.names_request(("Add a json flag",))


def test_reading_says_when_the_words_touch_files():
    assert api._line_reading("Line 2 names the wrong tests").touches_files
    assert not api._line_reading("Line 2 is wrong").touches_files
    # `_faulted_approve` reads the clause of each cue through the reading.
    cues = {2: ("wrong", "names the wrong tests"), 3: ("wrong", "is wrong")}
    got = api._faulted_approve(frozenset({2, 3}), cues, 5, False,
                               frozenset({5}))
    assert got and "line 3" in got and "line 2" not in got


def test_reading_says_what_the_words_ask_of_a_note():
    reading = api._line_reading("Note 7 is wrong, drop it.")
    assert reading.note_act(7, "") == api._note_words(
        "Note 7 is wrong, drop it.", 7, "")


# The pin. The names below are the parser's line rule and cue lists. Only
# the parser's own functions in api.py read them. A second reader goes red.
PARSER_NAMES = {
    "_LINE_REF", "_LINE_FAULT", "_LINE_WORD", "_BARE_FAULT_TAIL",
    "_PAGE_WORD", "_CHECK_AFTER", "_CHECK_BEFORE", "_ref_lines",
    "_line_refs", "_line_cues", "_live_cues",
    # The deleted cue lists stay deleted.
    "_PAGE_CUE", "_LINE_CHECK", "_CUE_BARE_FAULT",
    # Fact F3: the phrase lists of what his words permit or ask of a target.
    "_TOUCH_WORDS", "_BUILD_VERB", "_BATCH_TALK", "_NOTE_DROP",
    "_NOTE_SAYS", "_NOTE_NO_CHANGE", "_NOTE_CHANGE", "_names_request",
    "_note_words",
}
DELETED = {"_PAGE_CUE", "_LINE_CHECK", "_CUE_BARE_FAULT"}
PARSER_SITES = {
    "<module>", "_ref_lines", "_line_refs", "_line_reading", "LineReading",
    "_line_cues", "_live_cues", "_agreement", "_instruction_cue",
    "_contrast_cue", "_names_request", "_note_words",
    # The report span of W9 (the seam pass 2) is a part of the parser.
    "_reported",
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
    # The pin asserts by behaviour too, so a list under a new name fails.
    assert strays + _behaviour_strays() == []


# The behaviour pin (the F2 review, finding 1). A pin by name misses a new
# list under a new name. So every literal pattern of an `re` call is run on
# probe words. A pattern that reads a numbered line, two fault cues, or the
# files and tests words is a cue reader. It sits in the parser, or it is a
# named residue below.
_RE_CALLS = {"compile", "search", "match", "fullmatch", "findall",
             "finditer", "sub", "split"}
_REF_PROBES = ("line 3", "lines 2 and 3", "Note 7")
_CUE_PROBES = ("wrong", "drop", "remove", "strike")
_TOUCH_PROBES = ("files", "tests")
# Clause cues outside line references, kept by pass 1 and pass 1b.
CUE_RESIDUE = {
    ("roles/api.py", "_CUE_FILES"), ("roles/api.py", "_CUE_FAULT"),
    ("roles/api.py", "_FILES_TALK"), ("roles/api.py", "_CALLABLE_SPAN"),
    ("roles/api.py", "_CHECK_SUBJECT"), ("roles/api.py", "code_concordance"),
    ("roles/api.py", "_REMOVAL_WORDS"), ("roles/api.py", "_REQUEST_VERBS"),
    # These read a traceback's "line N" and a finding id, not his words.
    ("core/harness.py", "_E_LINE"), ("roles/api.py", "_free_finding_id"),
}


def _whole(rx: re.Pattern, word: str) -> bool:
    m = rx.search(word)
    return bool(m) and m.group(0).lower() == word


def _cue_reader(pattern: str) -> str | None:
    try:
        rx = re.compile(pattern, re.I)
    except re.error:
        return None
    # A pattern that reads any word or any number reads no cue.
    if rx.search("zebra quilt 9 zebra"):
        return None
    if any((m := rx.search(p)) and re.search(r"[a-z]", m.group(0), re.I)
           and re.search(r"\d", m.group(0)) for p in _REF_PROBES):
        return "line reference"
    if sum(_whole(rx, w) for w in _CUE_PROBES) >= 2:
        return "fault cues"
    if all(_whole(rx, w) for w in _TOUCH_PROBES):
        return "files words"
    return None


def _patterns(path: Path):
    """Each literal pattern of an `re` call, with its module-level name or
    its function."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for top in tree.body:
        scope = (top.name if isinstance(top, (ast.FunctionDef, ast.ClassDef,
                                              ast.AsyncFunctionDef))
                 else top.targets[0].id if isinstance(top, ast.Assign)
                 and isinstance(top.targets[0], ast.Name) else "<module>")
        for node in ast.walk(top):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in _RE_CALLS and node.args
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "re"
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                yield scope, node.lineno, node.args[0].value


def _behaviour_strays() -> list[str]:
    api_path = PACKAGE / "roles" / "api.py"
    allowed = PARSER_SITES | {"_LINE_REF", "_LINE_FAULT", "_LINE_WORD",
                              "_FAULT_WORDS", "_TOUCH_WORDS", "_NOTE_DROP",
                              "_BARE_FAULT_TAIL", "_CHECK_AFTER"}
    strays = []
    for path in sorted(PACKAGE.rglob("*.py")):
        rel = path.relative_to(PACKAGE).as_posix()
        for scope, line, pattern in _patterns(path):
            kind = _cue_reader(pattern)
            if kind is None or (rel, scope) in CUE_RESIDUE:
                continue
            if path == api_path and scope in allowed:
                continue
            strays.append(f"{rel}:{line} {scope} {kind}")
    return strays


def test_page_cue_quotes_the_whole_reference_list():
    # The parser's page cue is the whole reference, where `_PAGE_CUE` gave
    # "Lines 3" alone (the F2 review, finding 3).
    got = api._page_reply_fault(None, "x", "Lines 3, 4 and 5 should say more.",
                                "Lines 3, 4 and 5 should say more.")
    assert got and "'Lines 3, 4 and 5'" in got


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
    # The pin asserts by behaviour too, so a list under a new name fails.
    assert strays + _behaviour_strays() == []
