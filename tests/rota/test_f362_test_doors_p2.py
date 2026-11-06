"""
Frame 362, pass 2: the review of dc33edfb found more good tests that the
test doors refuse, and a few bodies that they admit with a false text
(plans/f362-test-doors-review-2026-11-06.md).

One rule decides each case: a door refuses only what it is certain of.
In doubt it admits. The shapes are the review's probes in
`scratchpad/rd362/`.
"""
from __future__ import annotations

import ast

import pytest

from tests.rota.test_f362_consumers import _push, _state, proj  # noqa: F401
from tests.rota.test_f362_test_doors import (CHECKS_NOTHING, COLLECTS,
                                             ICAL, PRINTS_SAYS, _db, _encode,
                                             _past_the_collect_door, _tester)

NL = chr(10)
FIXTURE = "the harness has no such fixture"


def B(*lines: str) -> str:
    return NL.join(list(lines) + [""])


def _script(*lines: str) -> dict[str, str]:
    return {"script.py": B("import json, sys, functools", *lines)}


def _run(tmp_path, files, body, crit="echo_json prints the object as JSON",
         refs='["echo_json"]', item="an echo_json helper", ticket="add echo_json"):
    conn = _db(tmp_path, item, ticket, [("c1", crit, refs)], files)
    return _encode(_tester(conn, "c1"), "tst_1", "c1", "tests/test_x.py", body)


USE = B("from script import echo_json", "def test_x():",
        "    result = echo_json({'a': 1})", "    assert result.startswith('{')")
MODULE_USE = B("import script", "def test_x():",
               "    result = script.echo_json({'a': 1})",
               "    assert result.startswith('{')")
METHOD_USE = B("from script import Printer", "def test_x():", "    p = Printer()",
               "    result = p.echo_json({'a': 1})", "    assert result.startswith('{')")


# --- 1. The guard path of tests.encode ------------------------------------

def _guard(sb, body: str) -> str:
    try:
        sb.call("tests.encode", id="tst_octets", criterion_id="fold_octets",
                path="tests/test_fold_octets.py", body=body)
    except ValueError as exc:
        return str(exc)
    return "landed"


def test_the_guard_path_has_the_same_collect_door(proj):
    """Finding 3: `_encode_guard` kept the old false text. A
    `pytest.raises` and a `TestCase` guard test are checks."""
    _, db = proj
    _state(db)
    sb, _ = _push(db, "tester", "tick:tests_missing")
    raises = B("import pytest", "from pkg.fold import fold", "def test_octets():",
               "    with pytest.raises(TypeError):", "        fold(None)")
    tcase = B("import unittest", "from pkg.fold import fold",
              "class TestFold(unittest.TestCase):", "    def test_octets(self):",
              "        self.assertTrue(all(len(p.encode()) <= 75 for p in [fold('a' * 80)]))")
    empty = B("from pkg.fold import fold", "def test_octets():", "    fold('a' * 80)")
    for body in (raises, tcase):
        assert _past_the_collect_door(_guard(sb, body))
    got = _guard(sb, empty)
    assert got.startswith("pytest collects this body, and " + CHECKS_NOTHING), got
    got = _guard(sb, "'fold folds at 75 octets'" + NL)
    assert got.startswith(COLLECTS), got


# --- 2. The fixture door --------------------------------------------------

ADD = {"script.py": B("def add(a, b):", "    return a + b")}


def _add(tmp_path, body: str) -> str:
    return _run(tmp_path, ADD, body, crit="add returns the sum of a and b",
                refs='["script.py::add"]', item="add two numbers",
                ticket="add returns a sum")


def test_a_parametrized_test_passes_the_fixture_door(tmp_path):
    """Finding 8: the argnames of `parametrize` are no fixtures."""
    got = _add(tmp_path, B("import pytest", "from script import add",
                           "@pytest.mark.parametrize('a,b,s', [(1, 2, 3), (2, 2, 4)])",
                           "def test_add(a, b, s):", "    assert add(a, b) == s"))
    assert got == "landed", got


def test_a_decorator_that_can_give_arguments_puts_the_test_in_doubt(tmp_path):
    """`given` and `patch` give a test its arguments. The door cannot tell
    which, so it admits."""
    got = _add(tmp_path, B("from hypothesis import given, strategies as st",
                           "from script import add",
                           "@given(st.integers(), st.integers())",
                           "def test_add(a, b):", "    assert add(a, b) == a + b"))
    assert FIXTURE not in got, got


def test_an_unknown_fixture_is_still_refused(tmp_path):
    """Walk twenty-nine: `mocker` is not installed."""
    got = _add(tmp_path, B("import pytest", "from script import add",
                           "@pytest.mark.slow", "def test_add(mocker):",
                           "    assert add(1, 2) == 3"))
    assert FIXTURE in got, got


# --- 3. and 4. The prints door ----------------------------------------------

@pytest.mark.parametrize("files,body", [
    # Finding 2: a base method with a `pass` body that a subclass overrides.
    (_script("class Base:", "    def echo_json(self, obj):", "        pass",
             "class Printer(Base):", "    def echo_json(self, obj):",
             "        return json.dumps(obj)"), METHOD_USE),
    # A decorator that keeps the value.
    (_script("@functools.lru_cache", "def echo_json(obj):",
             "    return json.dumps(obj)"), USE),
    # A call through `import script`.
    ({"script.py": B("import json", "def echo_json(obj):", "    return json.dumps(obj)"),
      "other.py": B("import json", "def echo_json(obj):", "    print(json.dumps(obj))")},
     MODULE_USE),
    # A re-export.
    ({"script.py": "from impl import echo_json" + NL,
      "impl.py": B("import json", "def echo_json(obj):", "    return json.dumps(obj)")},
     USE),
], ids=["pass-base", "lru_cache", "module-call", "re-export"])
def test_a_surface_that_gives_a_value_passes_the_prints_door(tmp_path, files, body):
    assert PRINTS_SAYS not in _run(tmp_path, files, body)


@pytest.mark.parametrize("files,body", [
    # Finding 1: these surfaces print, and give no value a test can use.
    (_script("def echo_json(obj):", "    return print(json.dumps(obj))"), USE),
    (_script("def echo_json(obj):", "    out = print(json.dumps(obj))",
             "    return out"), USE),
    (_script("def echo_json(obj):", "    return sys.stdout.write(json.dumps(obj))"), USE),
    (_script("def echo_json(obj, as_text=False):", "    if as_text:",
             "        return json.dumps(obj)", "    print(json.dumps(obj))"), USE),
    (_script("def echo_json(obj):", "    print(json.dumps(obj))", "    yield"), USE),
    # A module call of the printing one, and a re-export of a printing one.
    ({"script.py": B("import json", "def echo_json(obj):", "    print(json.dumps(obj))"),
      "other.py": B("import json", "def echo_json(obj):", "    return json.dumps(obj)")},
     MODULE_USE),
    ({"script.py": "from impl import echo_json" + NL,
      "impl.py": B("import json", "def echo_json(obj):", "    print(json.dumps(obj))")},
     USE),
], ids=["return-print", "bound-print", "return-write", "default-prints",
        "bare-yield", "module-call-prints", "re-export-prints"])
def test_a_surface_that_prints_keeps_the_word_rule(tmp_path, files, body):
    assert PRINTS_SAYS in _run(tmp_path, files, body)


def test_the_value_reader_needs_every_path_to_return():
    from rota.roles.api import _gives_a_value

    def first(src: str):
        return ast.parse(src).body[0]

    assert _gives_a_value(first(B("def f(x):", "    if x:", "        return 1",
                                  "    else:", "        return 2")))
    assert _gives_a_value(first(B("def f(x):", "    try:", "        return 1",
                                  "    except ValueError:", "        raise")))
    assert not _gives_a_value(first(B("def f(x):", "    if x:", "        return 1")))
    assert not _gives_a_value(first(B("def f(x):", "    return print(x)")))
    assert _gives_a_value(first(B("def f(x):", "    yield x")))


# --- 5., 6. and 7. The collect door ---------------------------------------

CANON = '["src/icalendar/caselessdict.py::canonsort_keys"]'
C1 = "The method raises ValueError if canonical_order contains duplicate keys."


def _canon(tmp_path, body: str) -> str:
    conn = _db(tmp_path, "canonsort_keys raises on a duplicate key",
               "canonsort_keys raises on a duplicate key", [("c1", C1, CANON)], ICAL)
    return _encode(_tester(conn, "c1"), "tst_1", "c1",
                   "src/icalendar/tests/test_c1.py", body)


IMP = "from icalendar.caselessdict import canonsort_keys"


@pytest.mark.parametrize("body", [
    B("from pytest import raises", IMP, "def test_bad():",
      "    with raises(ValueError):", "        canonsort_keys(['A'], ['A', 'A'])"),
    B("import pytest as pt", IMP, "def test_bad():",
      "    with pt.raises(ValueError):", "        canonsort_keys(['A'], ['A', 'A'])"),
    B("from numpy.testing import assert_equal", IMP, "def test_it():",
      "    assert_equal(canonsort_keys(['A']), ['A'])"),
    B(IMP, "def test_it():", "    if canonsort_keys(['A']) != ['A']:",
      "        raise AssertionError('order')"),
], ids=["from-pytest", "alias", "assert-name", "raise-assertion-error"])
def test_finding_4_checks_pass_the_collect_door(tmp_path, body):
    assert _past_the_collect_door(_canon(tmp_path, body))


def test_finding_5_self_assert_true_true_cannot_fail(tmp_path):
    got = _canon(tmp_path, B("import unittest", IMP,
                             "class TestSort(unittest.TestCase):",
                             "    def test_it(self):", "        canonsort_keys(['A'])",
                             "        self.assertTrue(True)"))
    assert got.startswith("every assertion here is on a constant"), got


def test_finding_5_a_real_self_assert_still_lands(tmp_path):
    got = _canon(tmp_path, B("import unittest", IMP,
                             "class TestSort(unittest.TestCase):",
                             "    def test_it(self):",
                             "        self.assertEqual(canonsort_keys(['A']), ['A'])"))
    assert got == "landed", got


@pytest.mark.parametrize("body", [
    # A class with no `Test` prefix and no base.
    B(IMP, "class SortChecks:", "    def test_it(self):",
      "        assert canonsort_keys(['A']) == ['A']"),
    # A fixture named `test_...`.
    B("import pytest", IMP, "@pytest.fixture", "def test_total():",
      "    v = canonsort_keys(['A'])", "    assert v == ['A']", "    return v"),
    # A `Test` class with an `__init__`.
    B(IMP, "class TestSort:", "    def __init__(self):", "        self.k = ['A']",
      "    def test_it(self):", "        assert canonsort_keys(self.k) == ['A']"),
], ids=["no-prefix", "fixture", "init"])
def test_finding_6_a_body_pytest_does_not_collect(tmp_path, body):
    assert _canon(tmp_path, body).startswith(COLLECTS)


@pytest.mark.parametrize("body", [
    B(IMP, "async def test_it():", "    assert canonsort_keys(['A']) == ['A']"),
    B(IMP, "class SortChecks(Base):", "    def test_it(self):",
      "        assert canonsort_keys(['A']) == ['A']"),
], ids=["async", "unknown-base"])
def test_finding_6_a_body_in_doubt_is_admitted(tmp_path, body):
    """A plugin decides an `async def` test, and an unknown base can be a
    `TestCase`. The door is not certain, so it admits."""
    assert not _canon(tmp_path, body).startswith(COLLECTS)


# --- 8. The triage door -----------------------------------------------------

def _triage(tmp_path, crit: str, item: str, ticket: str):
    from rota.core.sandbox import build

    conn = _db(tmp_path, item, ticket, [("c1", crit, '["to_ical"]')], ICAL)
    sb = build("tester", conn, batch_id="b1", mode="tests_missing")
    try:
        sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    except ValueError as exc:
        return str(exc)
    return "accepted"


def test_finding_7_triage_takes_encodable_when_the_surface_gives_a_value(tmp_path):
    """The review's T1: "the serialized output" and "returns" disagree in
    words only. `to_ical` returns a value in the tree."""
    got = _triage(tmp_path, "The serialized output of to_ical folds lines at 75 octets",
                  "to_ical returns the calendar as bytes",
                  "return the folded calendar from to_ical")
    assert got == "accepted", got


def test_finding_7_triage_keeps_the_offer_when_no_surface_gives_a_value(tmp_path):
    conn_files = {k: v for k, v in ICAL.items() if "cal.py" not in k
                  and "parameter.py" not in k}
    from rota.core.sandbox import build

    conn = _db(tmp_path, "to_ical returns the calendar as bytes",
               "return the folded calendar from to_ical",
               [("c1", "The serialized output of to_ical folds lines at 75 octets",
                 '["to_ical"]')], conn_files)
    sb = build("tester", conn, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match="contradicts_request"):
        sb.call("tests.triage", criterion_id="c1", verdict="encodable")
