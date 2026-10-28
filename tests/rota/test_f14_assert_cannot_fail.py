"""Fact F14: one reader answers whether an assert can fail.

`assert_cannot_fail` in `rota/roles/api.py` holds every rule. The encode
door reads it. The pin test goes red when a second copy of a rule appears.
"""
import ast
import pathlib

from rota.roles import api

ROOT = pathlib.Path(api.__file__).resolve().parents[1]


def _kinds(body: str) -> list[list[str]]:
    tree = ast.parse(body)
    return [[k for k, _ in api.assert_cannot_fail(a.test, tree, body)]
            for a in ast.walk(tree) if isinstance(a, ast.Assert)]


def test_a_constant_and_an_or_true_cannot_fail():
    body = ("def test_a():\n"
            "    assert True\n"
            "    assert f() or True\n"
            "    assert f() or 0\n")
    assert _kinds(body) == [["constant"], ["or_constant"], []]


def test_an_operand_on_the_interpreter_alone_cannot_fail():
    body = ("import sys\n"
            "def test_a():\n"
            "    assert out() or sys.version_info[0] == 3\n"
            "    assert out() or sys.version_info[0] == 2\n")
    tree = ast.parse(body)
    first = [a for a in ast.walk(tree) if isinstance(a, ast.Assert)][0]
    why = api.assert_cannot_fail(first.test, tree, body)
    assert why == [("interpreter",
                    "the operand `sys.version_info[0] == 3` reads only the "
                    "Python interpreter, so its value is the same whatever "
                    "the call did")]
    # A false operand can fail, so the door admits the second assert.
    assert _kinds(body)[1] == []


def test_a_rebound_sys_is_not_the_interpreter():
    body = ("import os as sys\n"
            "def test_a():\n"
            "    assert out() or sys.version_info[0] == 3\n")
    assert _kinds(body) == [[]]


def test_opposite_operands_cannot_fail():
    body = ("def test_a():\n"
            "    r = f()\n"
            "    assert r is not None or r is None\n"
            "    assert r == 1 or not r == 1\n"
            "    assert r == 1 or r != 2\n")
    assert _kinds(body) == [["opposites"], ["opposites"], []]


def test_an_invented_mock_method_cannot_fail():
    body = ("from unittest import mock\n"
            "def test_a():\n"
            "    m = mock.MagicMock()\n"
            "    with mock.patch('builtins.print') as p:\n"
            "        run(m)\n"
            "    assert m.called_with(1)\n"
            "    assert p.was_called_with('x')\n"
            "    assert m.assert_called_with(1) is None\n"
            "    assert other.called_with(1)\n")
    assert _kinds(body) == [["mock_method"], ["mock_method"], [], []]
    tree = ast.parse(body)
    first = [a for a in ast.walk(tree) if isinstance(a, ast.Assert)][0]
    (_, why), = api.assert_cannot_fail(first.test, tree, body)
    assert why.startswith("m.called_with(...) is not a real Mock method")
    assert "The real check is m.assert_called_with(...)" in why


def test_a_raise_is_a_check():
    assert api.body_checks_by_raise(ast.parse(
        "def test_a():\n    raise AssertionError('x')\n"))
    assert api.body_checks_by_raise(ast.parse(
        "import pytest\ndef test_a():\n    pytest.fail('x')\n"))
    assert not api.body_checks_by_raise(ast.parse(
        "def test_a():\n    raise ValueError('x')\n"))


# The rules' own markers. Each appears at one site alone.
_OLD_HELPERS = {"_vacuous", "_only_reads", "_reads_interpreter_alone",
                "_cannot_fail_because", "_complementary", "_raises_a_check"}
_MARKERS = {
    '"assert_not_called"': "_REAL_MOCK_METHODS",
    '"python_version_tuple"': "_INTERP_PLATFORM",
    '"hexversion"': "_INTERP_SYS",
    '"NonCallableMagicMock"': "_MOCK_CTORS",
    "_ast.IsNot), (_ast.IsNot, _ast.Is)": "_OPPOSITE_OPS",
}


def test_no_second_reader_of_whether_an_assert_can_fail():
    nested, markers = [], []
    for path in sorted(ROOT.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for sub in ast.walk(fn):
                if (sub is not fn
                        and isinstance(sub, (ast.FunctionDef,
                                             ast.AsyncFunctionDef))
                        and sub.name in _OLD_HELPERS):
                    nested.append(f"{path.name}:{fn.name}.{sub.name}")
            if fn.name in _OLD_HELPERS:
                nested.append(f"{path.name}:{fn.name}")
        for marker in _MARKERS:
            for i, line in enumerate(text.splitlines(), 1):
                if marker in line:
                    markers.append((path.name, marker))
    assert nested == [], nested
    # Each marker sits once, in the constant that the predicate reads.
    assert sorted(markers) == sorted(("api.py", m) for m in _MARKERS), markers
    src = pathlib.Path(api.__file__).read_text(encoding="utf-8")
    for marker, const in _MARKERS.items():
        at = src.index(marker)
        assert src.rfind("\n" + const + " = ", 0, at) != -1, const
    # The encode door reads the predicate and holds no rule of its own.
    door = next(n for n in ast.parse(src).body
                if isinstance(n, ast.FunctionDef) and n.name == "tests_encode")
    called = {n.func.id for n in ast.walk(door)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert {"assert_cannot_fail", "body_checks_by_raise"} <= called
    readers = sorted(n.name for n in ast.parse(src).body
                     if isinstance(n, ast.FunctionDef)
                     and any(isinstance(c, ast.Call)
                             and isinstance(c.func, ast.Name)
                             and c.func.id == "assert_cannot_fail"
                             for c in ast.walk(n)))
    assert readers == ["tests_encode"], readers
