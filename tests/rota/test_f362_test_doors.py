"""
Frame 362: two doors of `tests.encode` refused good tests, and one hint
named a folder the project does not have.

On dry runs 3 to 6c the doors refused 102 Tester calls, and 30 of them were
good tests (plans/dry6c-tests-refused-read-2026-11-06.md). The rule is
`rota/DECISIONS.md` lines 944 to 957: a door refuses a fact about the
harness that is certain whatever the criterion means.

- The prints door read words. "The serialized output" and "writes a long
  line" describe a return value on a library, and the door refused 18 tests
  that used the return value of `q_split` and `to_ical`.
- The collect door refused a body with no `assert` statement and said
  "pytest will collect nothing". That is false for a `pytest.raises` test
  and for a `unittest.TestCase` method. It refused 12 of 12 wrongly.
- The clash hint named `tests/test_<what it checks>.py`, a root folder that
  icalendar does not have.

The bodies are the Tester's calls, copied from the read's `pairs.json`.
Two copies drop the trailing spaces of a line, and no door reads them.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build

NL = chr(10)

# A small tree in icalendar's layout. `to_ical` is a method of `Component`
# and a stub of a Protocol, as in icalendar's `parser/parameter.py`.
ICAL = {
    "src/icalendar/__init__.py": NL.join([
        "from icalendar.cal import Calendar, Component, Event",
        "from icalendar.parser.parameter import q_split", ""]),
    "src/icalendar/cal.py": NL.join([
        "class Component:",
        "    def __init__(self):",
        "        self.lines = []",
        "",
        "    def add(self, name, value):",
        "        self.lines.append(name.upper() + ':' + value)",
        "",
        "    def add_component(self, c):",
        "        if isinstance(c, str):",
        "            c = Event()",
        "        self.lines.extend(c.lines)",
        "        return c",
        "",
        "    def to_ical(self):",
        "        return chr(13).join(self.lines).encode()",
        "",
        "",
        "class Calendar(Component):",
        "    pass",
        "",
        "",
        "class Event(Component):",
        "    pass", ""]),
    "src/icalendar/parser/__init__.py": "",
    "src/icalendar/parser/parameter.py": NL.join([
        "from typing import Protocol",
        "",
        "",
        "class HasToIcal(Protocol):",
        "    def to_ical(self) -> bytes:",
        '        """Convert to iCalendar format."""',
        "        ...",
        "",
        "",
        "def q_split(st, sep=',', maxsplit=-1):",
        "    result = st.split(sep, maxsplit)",
        "    return result", ""]),
    "src/icalendar/caselessdict.py": NL.join([
        "def canonsort_keys(keys, canonical_order=None):",
        "    return sorted(keys)", ""]),
    "src/icalendar/tests/__init__.py": "",
    "src/icalendar/tests/test_icalendar.py": NL.join([
        "def test_it():", "    assert 1 + 1 == 2", ""]),
}

STATEMENT = ("When icalendar writes a long line, fold it at a space where it "
             "can, so that a word is not split, and keep everything else as "
             "before.")
Q_SPLIT = '["src/icalendar/parser/parameter.py::q_split"]'

# dry4 s214 turn 2, `tst_fold_c4`. The criterion says "folded output".
DRY4_C4 = ("The maximum line length for folded output must conform to the "
           "iCalendar specification limit of 75 octets per line.")
DRY4_TICKET = ("when icalendar writes a long line, fold it at a space where it "
               "can, so that a word is not split")
TST_FOLD_C4 = r'''from icalendar.parser.parameter import q_split

def test_fold_respects_75_octet_limit():
    # Criterion c4: max line length is 75 octets
    long_text = "A" * 80  # force folding
    folded = q_split(long_text)
    lines = folded.split("\r\n")
    for line in lines:
        assert len(line.encode("utf-8")) <= 75'''

# dry6c s181 turn 1, `tst_c3_fold`. The surface ref is the bare method name.
C6_C3 = ("The folding behavior must not alter existing escape sequences or "
         "break them across lines.")
C6_TICKET = "fold long lines in iCalendar output at spaces to avoid splitting words"
TST_C3_FOLD = r'''from icalendar import Calendar

def test_long_line_folding():
    # Create a calendar with a very long line that needs folding
    cal = Calendar()

    # Add an event with a long summary
    from datetime import datetime
    ev = cal.add_component("VEVENT")
    ev.add("SUMMARY", "This is a very long summary text that should be folded at a space where it can so that a word is not split and keep everything else as before because the line is too long for the icalendar format specification which limits lines to 75 octets")

    # Serialize the calendar
    serialized = cal.to_ical()

    # Assert that no word is split across lines
    decoded = serialized.decode("utf-8")
    lines = decoded.split("\n")
    for line in lines:
        if line.strip():  # Skip empty lines
            words = line.split()
            assert all(word == decoded[decoded.find(line):line.find(line)+len(word)].split()[0] for word in words), f"Word split detected in: {line}"

def test_folding_at_space():
    # Verify that folding happens at spaces
    cal = Calendar()
    ev = cal.add_component("VEVENT")
    long_text = "A " * 20 + "B " * 20 + "C"
    ev.add("SUMMARY", long_text)

    serialized = cal.to_ical().decode("utf-8")
    # Check that there are no words split by newlines
    assert "\n" not in long_text or long_text.split("\n")[0].endswith(" ") or long_text.split("\n")[1].startswith(" ")
'''

# dry3 s183 turn 4, `tst_c1_raises_on_dup_keys`: a `pytest.raises` test.
DRY3_C1 = "The method raises ValueError if canonical_order contains duplicate keys."
DRY3_ITEM = ("The icalendar.caselessdict.canonsort_keys() method raises "
             "ValueError when canonical_order names the same key twice, and "
             "sorts the keys as before otherwise.")
CANONSORT = '["src/icalendar/caselessdict.py::canonsort_keys"]'
TST_C1_RAISES = r'''import pytest
from icalendar.caselessdict import canonsort_keys

def test_canonsort_keys_raises_value_error_on_duplicate_keys_in_canonical_order():
    """Criterion c1: The method raises ValueError if canonical_order contains duplicate keys."""
    canonical_order_with_dup = ["VERSION", "PRODID", "VERSION"]
    with pytest.raises(ValueError):
        canonsort_keys(keys=["VERSION", "PRODID"], canonical_order=canonical_order_with_dup)'''

# dry6c s177 turn 3, `inh_fold_word_split`: a `unittest.TestCase` method.
C6_C2 = ("No line in the serialized output may contain a hyphenated word "
         "broken across two lines.")
INH_FOLD_WORD_SPLIT = r'''import unittest
from icalendar import Calendar, Event

class TestHyphenatedWordSplit(unittest.TestCase):
    def test_no_hyphen_split(self):
        # Arrange: Create a calendar with a property name or value containing a hyphenated word
        cal = Calendar()
        event = Event()
        event.add("summary", "This is a test-event-with-hyphens-in-it")
        event.add("description", "A description for the test-event.")
        cal.add_component(event)

        # Act: Serialize to string
        output = cal.to_ical().decode("utf-8")

        # Assert: Split into lines and check no hyphenated word is broken
        lines = output.split("\n")
        for line in lines:
            # Check if a line ends with a hyphen (indicating a split)
            self.assertFalse(line.rstrip().endswith("-"),
                f"Line was split at a hyphen: {repr(line)}")'''

# dry6c s180 turn 1: `c_1_fold` landed, then `c_3_escape_preserved` met the
# clash at the same file.
C6_C1 = ("The serialized iCalendar output must fold lines at whitespace "
         "boundaries without splitting any word.")
C_1_FOLD = r'''def test_criterion_c_1_fold_at_whitespace():
    # Criterion c_1: "The serialized iCalendar output must fold lines at whitespace boundaries without splitting any word."
    from icalendar import Calendar, Event
    cal = Calendar()
    ev = Event()
    ev.add("summary", "This is a very long summary line that should be folded properly without breaking words")
    cal.add_component(ev)
    output = cal.to_ical().decode("utf-8")
    # Assert no word is split
    lines = output.split("\n")
    for line in lines:
        if line.strip():
            words = line.split()
            for w in words:
                assert not any(c == "\n" for c in w), f"Word was split: {w}"
    # Assert folding happened (line length < 75)
    assert all(len(line) <= 75 for line in lines if line.strip())'''
C_3_ESCAPE_PRESERVED = r'''def test_criterion_c_3_escape_preserved():
    # Criterion c_3: "The folding behavior must not alter existing escape sequences or break them across lines."
    from icalendar import Calendar, Event
    cal = Calendar()
    ev = Event()
    # Include a backslash-escaped newline in the summary
    ev.add("summary", "Line1\\\nLine2")
    cal.add_component(ev)
    output = cal.to_ical().decode("utf-8")
    lines = output.split("\n")
    for line in lines:
        if line.strip():
            # Ensure no backslash-newline sequence is split
            assert not (line.endswith("\\") and len(line) > 1), f"Escape sequence broken: {line}"'''

PRINTS_SAYS = "returns, and the criterion"
COLLECTS = "pytest collects nothing from this body"
CHECKS_NOTHING = "the test checks nothing"


def _db(tmp_path: Path, item: str, ticket: str,
        criteria: list[tuple[str, str, str]],
        files: dict[str, str] | None = None) -> sqlite3.Connection:
    """A batch whose worktree holds `files`, with each file a path row of
    the code index. With `files` None the batch has no worktree."""
    wt = tmp_path / "wt"
    for rel, text in (files or {}).items():
        (wt / rel).parent.mkdir(parents=True, exist_ok=True)
        (wt / rel).write_bytes(text.encode())
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1',?,'in_scope','approved',1,1)", (item,))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1',?)",
                 (ticket,))
    for cid, text, refs in criteria:
        conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                     "VALUES (?,'tk1',?,?)", (cid, text, refs))
    conn.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES "
                 "('b1','i1','running',?)", (str(wt) if files is not None else None,))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','tk1')")
    for rel in files or {}:
        conn.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, 'path')",
                     (rel,))
    conn.commit()
    return conn


def _encode(sb, test_id: str, criterion_id: str, path: str, body: str) -> str:
    """The door's answer: "landed" or the refusal. The literal door is
    another door, and the seat's next move is its offered ledger line, so
    each of its offers is logged and the encode is sent again."""
    for _ in range(12):
        try:
            sb.call("tests.encode", id=test_id, criterion_id=criterion_id,
                    path=path, body=body)
        except ValueError as exc:
            said = str(exc)
            m = re.search(r'assumption="(the test assumes [^"]+)"', said)
            if not (said.startswith("the test chooses ") and m):
                return said
            sb.call("ledger.log", about_ref=criterion_id, about_table="criteria",
                    assumption=m.group(1))
            continue
        return "landed"
    return said


def _tester(conn: sqlite3.Connection, *criteria: str):
    sb = build("tester", conn, batch_id="b1", mode="tests_missing")
    for cid in criteria:
        sb.call("tests.triage", criterion_id=cid, verdict="encodable")
    return sb


def _past_the_collect_door(got: str) -> bool:
    """No text of the collect door, the old one or the two new ones."""
    return not any(t in got for t in (COLLECTS, CHECKS_NOTHING,
                                      "pytest will collect nothing"))


# --- The prints door -------------------------------------------------------

def test_dry4_tst_fold_c4_lands_because_q_split_returns_a_value(tmp_path):
    """The criterion says "folded output", and the door refused this test
    three times on dry run 4. `q_split` returns a list in the tree, so the
    test that uses its return value is not refused for the words."""
    conn = _db(tmp_path, STATEMENT, DRY4_TICKET, [("c4", DRY4_C4, Q_SPLIT)], ICAL)
    got = _encode(_tester(conn, "c4"), "tst_fold_c4", "c4",
                  "src/icalendar/tests/test_fold_75_octets.py", TST_FOLD_C4)
    assert got == "landed"


def test_dry6c_tst_c3_fold_lands_because_every_to_ical_returns_a_value(tmp_path):
    """The ref is the bare method name `to_ical`, and the index holds no
    method row. Every `def to_ical` of the program returns a value, and the
    Protocol's stub declares one. So "writes a long line" does not refuse."""
    conn = _db(tmp_path, STATEMENT, C6_TICKET, [("c_3", C6_C3, '["to_ical"]')], ICAL)
    got = _encode(_tester(conn, "c_3"), "tst_c3_fold", "c_3",
                  "src/icalendar/tests/test_folding.py", TST_C3_FOLD)
    assert got == "landed"


def test_a_method_that_one_class_defines_with_no_value_keeps_the_door(tmp_path):
    """A name defined twice, and one definition returns nothing. The door
    cannot tell which one the test calls, so the words decide as before."""
    files = dict(ICAL)
    files["src/icalendar/writer.py"] = NL.join([
        "class Writer:", "    def to_ical(self):", "        print('BEGIN')", ""])
    conn = _db(tmp_path, STATEMENT, C6_TICKET, [("c_3", C6_C3, '["to_ical"]')], files)
    got = _encode(_tester(conn, "c_3"), "tst_c3_fold", "c_3",
                  "src/icalendar/tests/test_folding.py", TST_C3_FOLD)
    assert PRINTS_SAYS in got, got


def test_a_surface_that_prints_and_returns_nothing_keeps_the_door(tmp_path):
    """clickI night 28: `echo_json` printed and returned None. The code
    returns nothing, so the criterion's words decide as before."""
    files = {"script.py": NL.join([
        "import json", "def echo_json(obj, indent=None):",
        "    print(json.dumps(obj, indent=indent))", ""])}
    conn = _db(tmp_path, "an echo_json helper", "add echo_json",
               [("c1", "echo_json prints the object as JSON", '["echo_json"]')], files)
    body = NL.join(["from script import echo_json", "def test_x():",
                    "    result = echo_json({'a': 1})",
                    "    assert result.startswith('{')", ""])
    got = _encode(_tester(conn, "c1"), "tst_1", "c1", "tests/test_x.py", body)
    assert got == ("the test uses what echo_json returns, and the criterion c1 "
                   "says it prints: `echo_json` is a plain function in `script.py`")


def test_a_surface_not_in_the_tree_keeps_the_door(tmp_path):
    """clickI night 42: the batch has no tree with `echo_json` in it yet.
    No code shows a return value, so the criterion's words decide."""
    conn = _db(tmp_path, "an echo_json helper", "add echo_json next to echo",
               [("c1", "echo_json prints the object as JSON with the given indent",
                 '["echo_json"]')])
    body = NL.join(["from click.utils import echo_json", "",
                    "def test_echo_json_prints():",
                    "    assert echo_json({'a': 1}, indent=2) == 'x'", ""])
    got = _encode(_tester(conn, "c1"), "tst_1", "c1", "tests/test_echo_json.py", body)
    assert got.startswith("the test uses what echo_json returns, and the "
                          "criterion c1 says it prints"), got


def test_the_value_reader_counts_a_return_value_and_a_yield():
    import ast

    from rota.roles.api import _gives_a_value, _is_stub

    def first(src: str):
        return ast.parse(src).body[0]

    assert _gives_a_value(first("def f():\n    return 1\n"))
    assert _gives_a_value(first("def f():\n    yield 1\n"))
    assert not _gives_a_value(first("def f():\n    print(1)\n"))
    assert not _gives_a_value(first("def f():\n    return None\n"))
    assert not _gives_a_value(first("def f():\n    return\n"))
    # A nested `def` returns for itself, and not for `f`.
    assert not _gives_a_value(first("def f():\n    def g():\n        return 1\n"))
    # A decorator such as `click.command` decides what a call returns.
    assert not _gives_a_value(first("@command()\ndef f():\n    return 1\n"))
    assert _gives_a_value(first("@staticmethod\ndef f():\n    return 1\n"))
    assert _is_stub(first('def f():\n    """Doc."""\n    ...\n'))
    assert _is_stub(first("def f():\n    raise NotImplementedError\n"))
    assert not _is_stub(first("def f():\n    pass\n"))


# --- The collect door ------------------------------------------------------

def test_dry3_a_pytest_raises_test_lands(tmp_path):
    """dry3 s183: the door refused this body 9 times. A `pytest.raises`
    block is the check, and pytest collects the test."""
    conn = _db(tmp_path, DRY3_ITEM, DRY3_ITEM.lower(), [("c1", DRY3_C1, CANONSORT)], ICAL)
    got = _encode(_tester(conn, "c1"), "tst_c1_raises_on_dup_keys", "c1",
                  "src/icalendar/tests/test_caselessdict_c1.py", TST_C1_RAISES)
    assert _past_the_collect_door(got), got


def test_dry6c_a_unittest_testcase_method_lands(tmp_path):
    """dry6c s177: the door refused this body 3 times. pytest collects a
    `unittest.TestCase` method, and `self.assertFalse` is the check."""
    conn = _db(tmp_path, STATEMENT, C6_TICKET, [("c_2", C6_C2, '["to_ical"]')], ICAL)
    got = _encode(_tester(conn, "c_2"), "tst_c2_hyphen", "c_2",
                  "src/icalendar/tests/test_issue_long_line_hyphen.py",
                  INH_FOLD_WORD_SPLIT)
    assert _past_the_collect_door(got), got


CALLS = NL.join(["from icalendar.caselessdict import canonsort_keys",
                 "from unittest import mock", "import pytest", ""])


@pytest.mark.parametrize("check", [
    "    with pytest.warns(UserWarning):\n        canonsort_keys(['A'])",
    "    pytest.raises(ValueError, canonsort_keys, ['A'], ['A', 'A'])",
    "    if canonsort_keys(['A']) != ['A']:\n        pytest.fail('order')",
    "    m = mock.Mock(wraps=canonsort_keys)\n    m(['A'])\n"
    "    m.assert_called_once_with(['A'])",
])
def test_each_kind_of_check_passes_the_collect_door(tmp_path, check):
    conn = _db(tmp_path, DRY3_ITEM, DRY3_ITEM.lower(), [("c1", DRY3_C1, CANONSORT)], ICAL)
    body = CALLS + "def test_it():\n" + check + NL
    got = _encode(_tester(conn, "c1"), "tst_1", "c1",
                  "src/icalendar/tests/test_c1.py", body)
    assert _past_the_collect_door(got), got


def test_a_self_fail_in_a_testcase_passes_the_collect_door(tmp_path):
    conn = _db(tmp_path, DRY3_ITEM, DRY3_ITEM.lower(), [("c1", DRY3_C1, CANONSORT)], ICAL)
    body = CALLS + NL.join([
        "import unittest", "class TestSort(unittest.TestCase):",
        "    def test_it(self):",
        "        if canonsort_keys(['A']) != ['A']:",
        "            self.fail('order')", ""])
    got = _encode(_tester(conn, "c1"), "tst_1", "c1",
                  "src/icalendar/tests/test_c1.py", body)
    assert _past_the_collect_door(got), got


def test_a_test_that_checks_nothing_is_refused_with_its_own_text(tmp_path):
    """`def test_x(): pass` is collected and checks nothing."""
    conn = _db(tmp_path, DRY3_ITEM, DRY3_ITEM.lower(), [("c1", DRY3_C1, CANONSORT)], ICAL)
    got = _encode(_tester(conn, "c1"), "tst_1", "c1",
                  "src/icalendar/tests/test_c1.py", "def test_x(): pass" + NL)
    assert got.startswith("pytest collects this body, and " + CHECKS_NOTHING), got
    assert "collect nothing" not in got


def test_a_body_with_no_test_is_refused_as_collecting_nothing(tmp_path):
    """A string about the criterion parses, and pytest collects nothing."""
    conn = _db(tmp_path, DRY3_ITEM, DRY3_ITEM.lower(), [("c1", DRY3_C1, CANONSORT)], ICAL)
    got = _encode(_tester(conn, "c1"), "tst_1", "c1",
                  "src/icalendar/tests/test_c1.py",
                  "'canonsort_keys raises ValueError on a duplicate key'" + NL)
    assert got.startswith(COLLECTS), got


def test_an_english_sentence_is_still_refused(tmp_path):
    conn = _db(tmp_path, DRY3_ITEM, DRY3_ITEM.lower(), [("c1", DRY3_C1, CANONSORT)], ICAL)
    got = _encode(_tester(conn, "c1"), "tst_1", "c1",
                  "src/icalendar/tests/test_c1.py",
                  "The method raises ValueError if canonical_order contains "
                  "duplicate keys." + NL)
    assert got.startswith("the body is not Python"), got


# --- The clash hint --------------------------------------------------------

def test_dry6c_the_clash_hint_names_the_projects_test_folder(tmp_path):
    """s180: `c_1_fold` landed, and `c_3_escape_preserved` met the clash at
    the same file. The refusal stays, and its hint names the folder that
    holds the project's tests."""
    conn = _db(tmp_path, STATEMENT, C6_TICKET,
               [("c_1", C6_C1, '["to_ical"]'), ("c_3", C6_C3, '["to_ical"]')], ICAL)
    sb = _tester(conn, "c_1", "c_3")
    path = "src/icalendar/tests/test_folding.py"
    assert _encode(sb, "c_1_fold", "c_1", path, C_1_FOLD) == "landed"
    got = _encode(sb, "c_3_escape_preserved", "c_3", path, C_3_ESCAPE_PRESERVED)
    assert got.startswith(f"{path} is already c_1_fold's file; two tests in "
                          f"one file overwrite each other on disk."), got
    assert got.endswith("-- src/icalendar/tests/test_<what it checks>.py"), got
    assert "-- tests/" not in got


def test_the_clash_hint_names_a_root_tests_folder_where_the_project_has_one(tmp_path):
    files = {"calc.py": "def add(a, b):\n    return a + b\n",
             "tests/test_calc.py": "def test_it():\n    assert 1 == 1\n"}
    conn = _db(tmp_path, "an add helper", "add two numbers",
               [("c1", "add returns the sum", '["calc.py::add"]'),
                ("c2", "add returns an int on ints", '["calc.py::add"]')], files)
    sb = _tester(conn, "c1", "c2")
    one = NL.join(["from calc import add", "def test_sum():",
                   "    assert add(2, 3) == 5", ""])
    two = NL.join(["from calc import add", "def test_int():",
                   "    assert isinstance(add(2, 3), int)", ""])
    assert _encode(sb, "t1", "c1", "tests/test_add.py", one) == "landed"
    got = _encode(sb, "t2", "c2", "tests/test_add.py", two)
    assert got.endswith("-- tests/test_<what it checks>.py"), got


def test_the_clash_hint_moves_off_a_folder_that_holds_no_project_test(tmp_path):
    """dry3 s181: the Tester wrote at a root `tests/` folder that icalendar
    does not have. The hint names the largest test folder of the index."""
    conn = _db(tmp_path, DRY3_ITEM, DRY3_ITEM.lower(),
               [("c1", DRY3_C1, CANONSORT), ("c3", DRY3_C1, CANONSORT)], ICAL)
    sb = _tester(conn, "c1", "c3")
    assert _encode(sb, "t1", "c1", "tests/test_caselessdict.py",
                   TST_C1_RAISES) == "landed"
    got = _encode(sb, "t3", "c3", "tests/test_caselessdict.py",
                  TST_C1_RAISES.replace("def test_canonsort", "def test_c3_canonsort"))
    assert got.endswith("-- src/icalendar/tests/test_<what it checks>.py"), got
