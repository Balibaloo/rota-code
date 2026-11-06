"""
Frame 362, pass 3: the second look at bd10fb23 found good tests that the
fixture door and the import door refuse with a false text, and four small
cases (plans/f362-test-doors-review-2026-11-06.md, "Second look").

One rule decides each case: a door refuses only what it is certain of.
In doubt it admits. The shapes are the reviewer's probes in
`scratchpad/rd362/probe_p2.py` and `test_probe_guard2.py`.
"""
from __future__ import annotations

import sys

import pytest

from rota.roles import api
from tests.rota.test_f362_consumers import _push, _state, proj  # noqa: F401
from tests.rota.test_f362_test_doors import (CHECKS_NOTHING, COLLECTS, _db,
                                             _encode, _tester)

NL = chr(10)
FIXTURE = "the harness has no such fixture"
NO_MODULE = "no module of that name exists"
CONSTANT = "every assertion here is on a constant"
ADD = {"script.py": "def add(a, b):" + NL + "    return a + b" + NL}


def B(*lines: str) -> str:
    return NL.join(list(lines) + [""])


def _add(tmp_path, body: str, files: dict | None = None,
         path: str = "tests/test_x.py") -> str:
    conn = _db(tmp_path, "add two numbers", "add returns a sum",
               [("c1", "add returns the sum of a and b", '["script.py::add"]')],
               {**ADD, **(files or {})})
    return _encode(_tester(conn, "c1"), "tst_1", "c1", path, body)


@pytest.fixture
def no_env(monkeypatch):
    """The harness environment holds no package, so a test reads the
    project's own sources alone."""
    monkeypatch.setattr(api, "_harness_site_dirs", lambda root: ([], False))


@pytest.fixture
def fake_env(tmp_path, monkeypatch):
    """A folder of installed packages: `numpy`, and a pytest plugin
    `fakeplug` whose module defines the fixture `widget`."""
    site = tmp_path / "site"
    (site / "numpy").mkdir(parents=True)
    (site / "numpy" / "__init__.py").write_bytes(b"")
    (site / "fakeplug").mkdir()
    (site / "fakeplug" / "__init__.py").write_bytes(b"")
    (site / "fakeplug" / "plugin.py").write_bytes(B(
        "import pytest", "@pytest.fixture", "def widget():", "    return 1").encode())
    info = site / "fakeplug-1.0.dist-info"
    info.mkdir()
    (info / "METADATA").write_bytes(b"Metadata-Version: 2.1\nName: fakeplug\nVersion: 1.0\n")
    (info / "entry_points.txt").write_bytes(b"[pytest11]\nfake = fakeplug.plugin\n")
    monkeypatch.setattr(api, "_harness_site_dirs", lambda root: ([site], False))
    return site


# --- S2. The fixture door ---------------------------------------------------

PAIR = B("import pytest", "@pytest.fixture", "def pair():", "    return (1, 2)")
USES_PAIR = B("from script import add", "def test_x(pair):",
              "    assert add(*pair) == 3")


def test_s2_a_fixture_of_the_project_conftest_is_given(tmp_path, no_env):
    """The reviewer's R6."""
    got = _add(tmp_path, USES_PAIR, {"tests/conftest.py": PAIR})
    assert got == "landed", got


def test_s2_a_conftest_beside_the_path_gives_nothing(tmp_path, no_env):
    """pytest reads a conftest.py only on the path from the test's folder
    to the root. A fixture of a sibling folder is certain to be absent."""
    got = _add(tmp_path, USES_PAIR, {"other/conftest.py": PAIR})
    assert FIXTURE in got, got


def test_s2_a_name_that_a_conftest_imports_is_given(tmp_path, no_env):
    """pytest registers every fixture that the conftest module holds, an
    imported one too."""
    got = _add(tmp_path, USES_PAIR, {
        "tests/conftest.py": B("from tests.helpers import pair"),
        "tests/helpers.py": PAIR})
    assert FIXTURE not in got, got


def test_s2_a_conftest_that_loads_plugins_puts_the_door_in_doubt(tmp_path, no_env):
    got = _add(tmp_path, USES_PAIR, {
        "tests/conftest.py": B("pytest_plugins = ['tests.more']")})
    assert FIXTURE not in got, got


def test_s2_a_class_level_parametrize_gives_its_argnames(tmp_path, no_env):
    """The reviewer's R7."""
    got = _add(tmp_path, B("import pytest", "from script import add",
                           "@pytest.mark.parametrize('a,b', [(1, 2)])",
                           "class TestAdd:", "    def test_x(self, a, b):",
                           "        assert add(a, b) == a + b"))
    assert got == "landed", got


def test_s2_a_module_pytestmark_parametrize_gives_its_argnames(tmp_path, no_env):
    got = _add(tmp_path, B("import pytest", "from script import add",
                           "pytestmark = pytest.mark.parametrize('a', [1, 2])",
                           "def test_x(a):", "    assert add(a, 1) == a + 1"))
    assert got == "landed", got


def test_s2_a_class_decorator_that_can_give_arguments_puts_the_door_in_doubt(
        tmp_path, no_env):
    got = _add(tmp_path, B("from unittest import mock", "from script import add",
                           "@mock.patch('script.add', return_value=3)",
                           "class TestAdd:", "    def test_x(self, m):",
                           "        assert add(1, 2) == 3"))
    assert FIXTURE not in got, got


def test_s2_an_argument_with_a_default_is_no_fixture(tmp_path, no_env):
    """pytest asks no fixture for an argument with a default value."""
    got = _add(tmp_path, B("from script import add", "def test_x(n=2):",
                           "    assert add(n, 1) == 3"))
    assert got == "landed", got


def test_s2_a_fixture_of_an_installed_plugin_is_given(tmp_path, fake_env):
    got = _add(tmp_path, B("from script import add", "def test_x(widget):",
                           "    assert add(widget, 1) == 2"))
    assert got == "landed", got


def test_s2_a_name_that_no_source_gives_is_still_refused(tmp_path, fake_env):
    """Walk twenty-nine: `mocker` is in no plugin of the environment, no
    conftest and no mark. The text names what the door read."""
    got = _add(tmp_path, B("from script import add", "def test_x(mocker):",
                           "    assert add(1, 2) == 3"), {"tests/conftest.py": PAIR})
    assert FIXTURE in got, got
    assert "plain pytest, nothing installed on top" not in got
    assert "conftest.py" in got and "plugin" in got, got


def test_s2_the_harness_site_dirs_are_the_worktree_venv(tmp_path):
    from rota.core.provision import venv_python

    root = tmp_path / "wt"
    py = venv_python(root)
    py.parent.mkdir(parents=True)
    py.write_bytes(b"")
    if sys.platform == "win32":
        site = root / ".venv" / "Lib" / "site-packages"
    else:
        site = root / ".venv" / "lib" / "python3.12" / "site-packages"
    site.mkdir(parents=True)
    (root / ".venv" / "pyvenv.cfg").write_bytes(b"include-system-site-packages = false\n")
    dirs, doubt = api._harness_site_dirs(root)
    assert [d.resolve() for d in dirs] == [site.resolve()] and not doubt
    (root / ".venv" / "pyvenv.cfg").write_bytes(b"include-system-site-packages = true\n")
    assert api._harness_site_dirs(root)[1]


# --- The import door ----------------------------------------------------------

NUMPY = B("import numpy", "from script import add", "def test_add():",
          "    numpy.testing.assert_allclose(add(1, 2), 3)")
HYPO = B("from hypothesis import given, strategies as st", "from script import add",
         "@given(st.integers(), st.integers())", "def test_add(a, b):",
         "    assert add(a, b) == a + b")
YAML = B("import yaml", "from script import add", "def test_add():",
         "    assert add(1, 2) == yaml.safe_load('3')")
BILLING = B("from billing import add", "def test_add():", "    assert add(1, 2) == 3")


@pytest.mark.parametrize("files,body", [
    ({"pyproject.toml": B("[project]", 'name = "adder"', 'dependencies = ["numpy>=1.20"]')},
     NUMPY),
    ({"pyproject.toml": B("[project]", 'name = "adder"', "",
                          "[project.optional-dependencies]", 'test = ["hypothesis"]')},
     HYPO),
    ({"pyproject.toml": B("[dependency-groups]", 'test = ["hypothesis"]')}, HYPO),
    ({"requirements-dev.txt": B("# test tools", "-r requirements.txt", "hypothesis==6.1")},
     HYPO),
    ({"setup.cfg": B("[options.extras_require]", "test =", "    numpy")}, NUMPY),
    ({"setup.py": B("from setuptools import setup",
                    "setup(name='adder', install_requires=['numpy'])")}, NUMPY),
    ({"pyproject.toml": B("[project]", 'name = "adder"', 'dependencies = ["PyYAML"]')},
     YAML),
])
def test_a_package_the_project_declares_passes_the_import_door(tmp_path, no_env,
                                                               files, body):
    got = _add(tmp_path, body, files)
    assert NO_MODULE not in got, got


def test_a_package_of_the_harness_environment_passes_the_import_door(tmp_path,
                                                                     fake_env):
    got = _add(tmp_path, NUMPY)
    assert got == "landed", got


def test_an_invented_module_is_still_refused_and_the_text_names_the_sources(
        tmp_path, no_env):
    """tipsU and clickI night 24: a model invents a module for a new
    function. No source holds `billing`."""
    got = _add(tmp_path, BILLING, {"pyproject.toml": B(
        "[project]", 'name = "adder"', 'dependencies = ["numpy"]')})
    assert NO_MODULE in got, got
    assert "pyproject.toml" in got and "environment" in got, got


def test_an_undeclared_package_is_refused(tmp_path, no_env):
    got = _add(tmp_path, NUMPY)
    assert NO_MODULE in got and "no dependency file" in got, got


# --- S1. The guard path reads the constant door ---------------------------------

def _guard(sb, body: str) -> str:
    try:
        sb.call("tests.encode", id="tst_octets", criterion_id="fold_octets",
                path="tests/test_fold_octets.py", body=body)
    except ValueError as exc:
        return str(exc)
    return "landed"


def test_s1_the_guard_path_refuses_a_constant_assert(proj):
    _, db = proj
    _state(db)
    sb, _ = _push(db, "tester", "tick:tests_missing")
    got = _guard(sb, B("def test_octets():", "    assert True"))
    assert CONSTANT in got, got
    got = _guard(sb, B("from pkg.fold import fold", "def test_octets():",
                       "    assert len(fold('a' * 80)) > 0"))
    assert got == "landed", got


# --- S3, S4 and S5 ----------------------------------------------------------------

def test_s3_a_nested_test_class_is_collected(tmp_path, no_env):
    """The reviewer's R9. A real pytest run collected the test."""
    got = _add(tmp_path, B("from script import add", "class TestOuter:",
                           "    class TestInner:", "        def test_x(self):",
                           "            assert add(1, 2) == 3"))
    assert COLLECTS not in got, got
    assert got == "landed", got


def test_s4_a_self_assert_on_constants_is_refused(tmp_path, no_env):
    """The reviewer's R5."""
    got = _add(tmp_path, B("import unittest", "from script import add",
                           "class TestA(unittest.TestCase):", "    def test_x(self):",
                           "        add(1, 2)", "        self.assertEqual(1, 1)"))
    assert CONSTANT in got, got


def test_s4_a_self_assert_on_a_call_still_lands(tmp_path, no_env):
    got = _add(tmp_path, B("import unittest", "from script import add",
                           "class TestA(unittest.TestCase):", "    def test_x(self):",
                           "        self.assertEqual(add(1, 2), 3)",
                           "        self.assertEqual(1, 1)"))
    assert got == "landed", got


def test_s5_a_name_that_holds_fail_inside_is_no_check(tmp_path, no_env):
    """The reviewer's R8: `fail_safe` is the surface, not a check."""
    conn = _db(tmp_path, "add two numbers", "add returns a sum",
               [("c1", "fail_safe returns its argument", '["script.py::fail_safe"]')],
               {"script.py": B("def fail_safe(a):", "    return a")})
    got = _encode(_tester(conn, "c1"), "tst_1", "c1", "tests/test_x.py",
                  B("from script import fail_safe", "def test_x():", "    fail_safe(1)"))
    assert CHECKS_NOTHING in got, got


@pytest.mark.parametrize("call", [
    "pytest.fail('no')", "pytest.raises(ValueError)", "pytest.warns(UserWarning)",
    "m.assert_called_once()", "assert_allclose(1, 1)",
])
def test_s5_a_check_name_still_counts(call):
    import ast
    assert api._holds_a_check(ast.parse(B("def test_x():", "    " + call)))


def test_s5_a_word_inside_a_name_does_not_count():
    import ast
    for call in ("fail_safe(1)", "unraises(1)", "x.prewarns()", "reassert(1)"):
        assert not api._holds_a_check(ast.parse(B("def test_x():", "    " + call))), call


# --- 7. The triage skip reads both directions ----------------------------------

def _triage(tmp_path, crit: str, ticket: str, files: dict, refs: str) -> str:
    from rota.core.sandbox import build

    conn = _db(tmp_path, "fold long lines", ticket, [("c1", crit, refs)], files)
    sb = build("tester", conn, batch_id="b1", mode="tests_missing")
    try:
        sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    except ValueError as exc:
        return str(exc)
    return "accepted"


def test_7_a_returns_criterion_against_writes_takes_encodable_when_the_code_gives_a_value(
        tmp_path):
    """The reviewer's T3: the request's "writes" is the serialization, and
    the surface `to_ical` returns a value in the tree."""
    from tests.rota.test_f362_test_doors import ICAL

    got = _triage(tmp_path, "q_split returns the folded line",
                  "When icalendar writes a long line, fold it at a space", ICAL,
                  '["to_ical"]')
    assert got == "accepted", got


def test_7_a_returns_criterion_against_prints_keeps_the_offer_when_the_code_prints(
        tmp_path):
    """Night 91's direction: the surface prints, so the contradiction
    stands, and the offer stays."""
    got = _triage(tmp_path, "echo_json returns a string of the JSON",
                  "Add an echo_json helper that prints an object as JSON",
                  {"script.py": B("import json", "def echo_json(obj):",
                                  "    print(json.dumps(obj))")},
                  '["script.py::echo_json"]')
    assert "contradicts_request" in got, got
