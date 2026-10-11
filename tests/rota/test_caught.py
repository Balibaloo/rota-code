"""Frame 195: the red row carries the exception a `CliRunner` caught.

Night 138 (2026-10-10): every b_3 commit used `sys.version` with no
`import sys`. click's `CliRunner` caught the `NameError`, the test asserted
on the empty `result.output`, and the Developer read the assertion alone
for eight attempts. The harness now loads a pytest plugin that adds a
section with the caught exception. The plugin must never change a result.

Every test here runs a real pytest child on a stub `click` package. No
test calls a model.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from rota.core import harness

NL = chr(10)

# A stub of click's runner: it catches what the command raises and keeps
# `exc_info`, as `click.testing.CliRunner.invoke` does.
TESTING = NL.join([
    "import sys",
    "",
    "",
    "class Result:",
    "    def __init__(self, output, exc_info):",
    "        self.output = output",
    "        self.exc_info = exc_info",
    "        self.exception = exc_info[1] if exc_info else None",
    "",
    "",
    "class CliRunner:",
    "    def invoke(self, cli, args=None, catch_exceptions=True):",
    "        try:",
    "            out = cli(*(args or []))",
    "        except SystemExit:",
    "            return Result('', sys.exc_info())",
    "        except Exception:",
    "            if not catch_exceptions:",
    "                raise",
    "            return Result('', sys.exc_info())",
    "        return Result(out or '', None)",
    "",
])

# Night 138's shape: the option's callback reads `sys.version` with no
# `import sys`, three frames below the runner.
CORE = NL.join([
    "from click.decorators import callback",
    "",
    "",
    "def process_value(value):",
    "    return invoke_param(value)",
    "",
    "",
    "def invoke_param(value):",
    "    return callback(value)",
    "",
])
DECORATORS = NL.join([
    "def callback(value):",
    "    python_version = sys.version.split()[0]",
    "    return 'Python ' + python_version",
    "",
])
V3 = NL.join([
    "import re",
    "",
    "from click.core import process_value",
    "from click.testing import CliRunner",
    "",
    "",
    "def cli(*args):",
    "    return process_value('--version')",
    "",
    "",
    "def test_version_option_appends_python_version():",
    "    runner = CliRunner()",
    "    result = runner.invoke(cli, ['--version'])",
    "    match = re.search(r'Python (\\d+\\.\\d+\\.\\d+)', result.output)",
    "    assert match is not None, f'Expected Python version string in output: {result.output}'",
    "",
])


def _tree(root: Path, files: dict[str, str]) -> Path:
    base = {"pytest.ini": "[pytest]" + NL, "click/__init__.py": "",
            "click/testing.py": TESTING}
    base.update(files)
    for rel, text in base.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return root


def _pytest(root: Path, path: str, plugin: bool = True) -> subprocess.CompletedProcess:
    """One pytest child, with or without the plugin, as the harness runs it."""
    argv = [sys.executable, "-m", "pytest", path, "-q", "--no-header",
            "-p", "no:cacheprovider"]
    env = {k: v for k, v in os.environ.items()
           if k not in ("PYTEST_ADDOPTS", "PYTHONPATH")}
    if plugin:
        argv += ["-p", harness.PLUGIN, "--show-capture=all", "--tb=auto"]
        env["PYTHONPATH"] = str(harness.PLUGIN_DIR)
    return subprocess.run(argv, cwd=root, capture_output=True, text=True,
                          timeout=120, env=env)


def _final(text: str) -> list[str]:
    return [line for line in text.splitlines()
            if line.startswith("caught by CliRunner at ")]


# ---------------------------------------------------------------------------
# The plugin
# ---------------------------------------------------------------------------

def test_a_caught_name_error_on_a_failing_test_prints_the_section(tmp_path):
    root = _tree(tmp_path, {"click/core.py": CORE, "click/decorators.py": DECORATORS,
                            "tests/test_v3.py": V3})
    out = _pytest(root, "tests/test_v3.py")
    assert out.returncode == 1, out.stdout
    assert "CliRunner caught an exception" in out.stdout
    assert "NameError: name 'sys' is not defined" in out.stdout
    assert "output: empty" in out.stdout
    final = _final(out.stdout)
    assert final == [f"caught by CliRunner at {os.path.join('click', 'decorators.py')}:2: NameError"], out.stdout
    # The paths are relative to the project's root, never absolute.
    assert str(tmp_path) not in out.stdout.split("CliRunner caught an exception")[1]


def test_a_passing_test_prints_no_section(tmp_path):
    root = _tree(tmp_path, {"click/core.py": CORE, "click/decorators.py": DECORATORS,
                            "tests/test_ok.py": NL.join([
                                "from click.core import process_value",
                                "from click.testing import CliRunner",
                                "",
                                "def test_the_error_is_asserted():",
                                "    r = CliRunner().invoke(lambda *a: process_value('x'))",
                                "    assert isinstance(r.exception, NameError)",
                                ""])})
    out = _pytest(root, "tests/test_ok.py")
    assert out.returncode == 0, out.stdout
    assert "CliRunner caught" not in out.stdout and not _final(out.stdout)


def test_a_system_exit_prints_no_section(tmp_path):
    """click exits with `SystemExit` on purpose."""
    root = _tree(tmp_path, {"tests/test_exit.py": NL.join([
        "import sys",
        "from click.testing import CliRunner",
        "",
        "def test_exit():",
        "    r = CliRunner().invoke(lambda *a: sys.exit(2))",
        "    assert r.output == 'x'",
        ""])})
    out = _pytest(root, "tests/test_exit.py")
    assert out.returncode == 1, out.stdout
    assert "CliRunner caught" not in out.stdout and not _final(out.stdout)


def test_a_test_that_imports_the_runner_inside_its_body_is_reported(tmp_path):
    """66 of 104 Tester bodies import click inside the body (the review of
    878c2352). No module and no conftest imports click before the call, so
    only the finder on `sys.meta_path` can wrap the runner."""
    root = _tree(tmp_path, {"tests/test_body.py": NL.join([
        "# click is imported inside the test body alone.",
        "",
        "class Boom(Exception):",
        "    pass",
        "",
        "def boom(*args):",
        "    raise Boom('no')",
        "",
        "def test_body():",
        "    import click",
        "    from click.testing import CliRunner",
        "    r = CliRunner().invoke(boom)",
        "    assert r.output == 'yes'",
        ""])})
    out = _pytest(root, "tests/test_body.py")
    assert out.returncode == 1, out.stdout
    # A custom exception: the regex of `raised at` missed one, and the final
    # line's own prefix does not.
    assert _final(out.stdout) == [
        f"caught by CliRunner at {os.path.join('tests', 'test_body.py')}:7: Boom"], out.stdout


def test_a_runner_reloaded_inside_the_test_body_is_reported(tmp_path):
    """The call-time wrap runs before the body, so the class that a reload
    in the body makes is wrapped by the finder alone (the review of
    89fd9027, finding 2)."""
    root = _tree(tmp_path, {"tests/test_reload.py": NL.join([
        "import importlib",
        "",
        "import click.testing",
        "",
        "def boom(*args):",
        "    raise KeyError('no')",
        "",
        "def test_reload():",
        "    importlib.reload(click.testing)",
        "    r = click.testing.CliRunner().invoke(boom)",
        "    assert r.output == 'yes'",
        ""])})
    out = _pytest(root, "tests/test_reload.py")
    assert out.returncode == 1, out.stdout
    assert _final(out.stdout) == [
        f"caught by CliRunner at {os.path.join('tests', 'test_reload.py')}:6: KeyError"], out.stdout


def test_the_finder_leaves_a_legacy_finder_its_turn(monkeypatch):
    """Python 3.11 asks a `find_module` finder in its place on `sys.meta_path`.
    The finder skipped it and took the next spec (the review of 89fd9027,
    finding 1). Python 3.12 ignores such a finder, so the test calls
    `find_spec` directly."""
    import importlib.machinery
    import importlib.util

    # The module installs its finder at load. The copy keeps the suite's own
    # `sys.meta_path` clean.
    monkeypatch.setattr(sys, "meta_path", list(sys.meta_path))
    spec = importlib.util.spec_from_file_location(
        "_rota_caught_legacy_probe", harness.PLUGIN_DIR / (harness.PLUGIN + ".py"))
    plugin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plugin)

    served = importlib.machinery.ModuleSpec("click.testing", None)

    class Legacy:
        def find_module(self, name, path=None):
            return None

    class Modern:
        def find_spec(self, name, path=None, target=None):
            return served if name == "click.testing" else None

    monkeypatch.setattr(sys, "meta_path", [plugin._finder, Modern()])
    assert plugin._finder.find_spec("click.testing") is served
    monkeypatch.setattr(sys, "meta_path", [plugin._finder, Legacy(), Modern()])
    assert plugin._finder.find_spec("click.testing") is None


def test_a_project_with_no_click_runs_unchanged(tmp_path):
    (tmp_path / "pytest.ini").write_text("[pytest]" + NL, encoding="utf-8")
    (tmp_path / "test_plain.py").write_text(
        "def test_plain():" + NL + "    assert 1 + 1 == 3" + NL, encoding="utf-8")
    out = _pytest(tmp_path, "test_plain.py")
    assert out.returncode == 1 and "1 failed" in out.stdout
    assert "CliRunner caught" not in out.stdout


# ---------------------------------------------------------------------------
# The review's reproduced failures: the plugin never changes a result
# ---------------------------------------------------------------------------

def _same_result(root: Path, path: str) -> subprocess.CompletedProcess:
    without = _pytest(root, path, plugin=False)
    with_ = _pytest(root, path, plugin=True)
    assert with_.returncode == without.returncode, (without.stdout, with_.stdout)
    assert "INTERNALERROR" not in with_.stdout + with_.stderr, with_.stdout
    return with_


def test_a_runner_module_that_raises_at_import_changes_no_result(tmp_path):
    root = _tree(tmp_path, {
        "pytest.ini": "[pytest]" + NL + "filterwarnings =" + NL + "    error" + NL,
        "click/testing.py": "undefined_name" + NL + "class CliRunner:" + NL + "    pass" + NL,
        "tests/test_plain.py": "import click" + NL + NL + "def test_plain():" + NL
                               + "    assert 1 + 1 == 2" + NL})
    out = _same_result(root, "tests/test_plain.py")
    assert out.returncode == 0, out.stdout


def test_a_runner_module_that_warns_under_filterwarnings_error_changes_no_result(tmp_path):
    root = _tree(tmp_path, {
        "pytest.ini": "[pytest]" + NL + "filterwarnings =" + NL + "    error" + NL,
        "click/testing.py": NL.join([
            "import warnings",
            "warnings.warn('old', DeprecationWarning)",
            "class CliRunner:",
            "    def invoke(self):",
            "        pass",
            ""]),
        "tests/test_plain.py": "import click" + NL + NL + "def test_plain():" + NL
                               + "    assert 1 + 1 == 2" + NL})
    out = _same_result(root, "tests/test_plain.py")
    assert out.returncode == 0, out.stdout


STUB_RES = NL.join([
    "class Result:",
    "    def __init__(self, exc):",
    "        self.exception = exc",
    "        self.exc_info = exc",
    "",
    "",
    "class CliRunner:",
    "    def invoke(self, cli, args=None, catch_exceptions=True):",
    "        try:",
    "            cli()",
    "        except Exception as e:",
    "            return Result(e)",
    "        return Result(None)",
    "",
])


def test_an_exc_info_that_is_not_a_tuple_changes_no_result(tmp_path):
    root = _tree(tmp_path, {"click/testing.py": STUB_RES, "tests/test_res.py": NL.join([
        "from click.testing import CliRunner",
        "",
        "def boom():",
        "    raise ValueError('x')",
        "",
        "def test_caught_exception_is_asserted():",
        "    r = CliRunner().invoke(boom)",
        "    assert isinstance(r.exception, ValueError)",
        ""])})
    out = _same_result(root, "tests/test_res.py")
    assert out.returncode == 0, out.stdout


def test_a_check_on_the_runner_signature_changes_no_result(tmp_path):
    root = _tree(tmp_path, {"tests/test_sig.py": NL.join([
        "import inspect",
        "from click.testing import CliRunner",
        "",
        "def test_first():",
        "    CliRunner().invoke(lambda *a: None)",
        "",
        "def test_signature():",
        "    assert 'catch_exceptions' in inspect.signature(CliRunner.invoke).parameters",
        ""])})
    out = _same_result(root, "tests/test_sig.py")
    assert out.returncode == 0, out.stdout


def test_four_raising_calls_keep_the_assertion_and_the_final_line_in_the_tail(tmp_path):
    """Four calls pushed the assertion out of the 2000-character tail."""
    root = _tree(tmp_path, {"click/core.py": CORE, "click/decorators.py": DECORATORS,
                            "tests/test_four.py": NL.join([
                                "from click.core import process_value",
                                "from click.testing import CliRunner",
                                "",
                                "def other(*args):",
                                "    raise KeyError('k')",
                                "",
                                "def test_four():",
                                "    runner = CliRunner()",
                                "    outs = [runner.invoke(lambda *a: process_value('x')).output",
                                "            for _ in range(3)]",
                                "    outs.append(runner.invoke(other).output)",
                                "    assert ''.join(outs) == 'Python 3', 'Expected output'",
                                ""])})
    _same_result(root, "tests/test_four.py")
    verdict, said = harness._run_one(root, "tests/test_four.py", 120)
    assert verdict == "fail", said
    assert "AssertionError: Expected output" in said
    assert "and 3 more in this test, 1 of them at another place" in said
    assert said.count("NameError: name 'sys' is not defined") == 1, said
    lines = said.splitlines()
    summary = next(i for i, line in enumerate(lines) if "short test summary info" in line)
    assert lines[summary - 1].startswith("caught by CliRunner at "), said


def test_a_frame_on_another_drive_keeps_the_result_and_the_absolute_path(tmp_path):
    """`relpath` refuses two drives: base Python on C:, the worktrees on D:."""
    conftest = NL.join([
        "import os",
        "import sys",
        "import types",
        "",
        "",
        "class _Path:",
        "    def __getattr__(self, name):",
        "        return getattr(os.path, name)",
        "",
        "    def relpath(self, *args, **kwargs):",
        "        raise ValueError(\"path is on mount 'C:', start on mount 'D:'\")",
        "",
        "",
        "_plugin = sys.modules.get('_rota_caught')",
        "if _plugin is not None:",
        "    _plugin.os = types.SimpleNamespace(path=_Path())",
        ""])
    root = _tree(tmp_path, {"click/core.py": CORE, "click/decorators.py": DECORATORS,
                            "tests/conftest.py": conftest, "tests/test_v3.py": V3})
    out = _same_result(root, "tests/test_v3.py")
    assert out.returncode == 1, out.stdout
    final = _final(out.stdout)
    assert len(final) == 1 and os.path.isabs(final[0][len("caught by CliRunner at "):].rsplit(":", 2)[0]), out.stdout


# ---------------------------------------------------------------------------
# The harness
# ---------------------------------------------------------------------------

def test_the_harness_carries_the_section_into_the_test_run(tmp_path):
    from rota.core.db import init_db

    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('i1','ship it','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i1','do it')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c1','t1','it works')")
    wt = _tree(tmp_path / "wt", {"click/core.py": CORE, "click/decorators.py": DECORATORS})
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit, worktree) "
                 "VALUES ('b1','i1','running','abc123',?)", (str(wt),))
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES ('tst_v3','b1','c1','tests/test_version_option_version_format.py',?)",
                 (V3,))
    assert harness.run(conn, "b1") == [("tst_v3", "fail")]
    said = conn.execute("SELECT output FROM test_runs").fetchone()["output"]
    # Night 138's shape: the 2000-character tail holds both the assertion
    # and the caught exception.
    assert "AssertionError: Expected Python version string in output: " in said
    assert "test_version_option_version_format.py:15: AssertionError" in said
    assert "CliRunner caught an exception" in said
    assert _final(said) == [
        f"caught by CliRunner at {os.path.join('click', 'decorators.py')}:2: NameError"]
    section = said.split("CliRunner caught an exception")[1].split("short test summary")[0]
    assert len(section) < 700, section


# ---------------------------------------------------------------------------
# tests.load: the `raised at` words
# ---------------------------------------------------------------------------

# tr532 on night 138, verbatim from `test_runs.output`.
TR532 = (
    "F                                                                        [100%]\n"
    "================================== FAILURES ===================================\n"
    "_________________ test_version_option_appends_python_version __________________\n"
    "\n"
    "    def test_version_option_appends_python_version():\n"
    "        runner = CliRunner()\n"
    "        result = runner.invoke(cli, [\"--version\"])\n"
    "        # The output should contain the Python version string in the format '3.10.5'\n"
    "        import re\n"
    "        match = re.search(r\"Python (\\d+\\.\\d+\\.\\d+)\", result.output)\n"
    ">       assert match is not None, f\"Expected Python version string in output: {result.output}\"\n"
    "E       AssertionError: Expected Python version string in output: \n"
    "E       assert None is not None\n"
    "\n"
    "tests\\test_version_option_version_format.py:17: AssertionError\n"
)
TR532_TAIL = (
    "=========================== short test summary info ===========================\n"
    "FAILED tests/test_version_option_version_format.py::test_version_option_appends_python_version\n"
    "1 failed in 0.11s"
)
# The section the plugin adds on night 138's shape (the review's probe,
# `rv195d/one.txt`), with the fact line and the fixed final line.
SECTION = (
    "------------------------ CliRunner caught an exception ------------------------\n"
    "  File \"src\\click\\core.py\", line 3660, in process_value\n"
    "    return super().process_value(ctx, value)\n"
    "  File \"src\\click\\core.py\", line 2640, in process_value\n"
    "    value = self.callback(ctx, self, value)\n"
    "  File \"src\\click\\decorators.py\", line 508, in callback\n"
    "    python_version = sys.version.split()[0] if show_python else None\n"
    "NameError: name 'sys' is not defined. Did you forget to import 'sys'?\n"
    "output: empty\n"
    "caught by CliRunner at src\\click\\decorators.py:508: NameError\n"
)


@pytest.fixture
def loaded(tmp_path):
    from rota.core.db import init_db
    from rota.core.sandbox import build

    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('i1','ship it','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i1','do it')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c1','t1','it works')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('b1','i1','running','abc123')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','t1')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
                 "('tst_v3','b1','c1','tests/test_version_option_version_format.py','x')")

    def load(output: str) -> str | None:
        conn.execute("DELETE FROM test_runs")
        conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
                     "output, attempt) VALUES ('tr532','b1','tst_v3','abc123','fail',?,1)",
                     (output,))
        rows = build("developer", conn, batch_id="b1").call("tests.load")
        return next(r for r in rows if r["id"] == "tst_v3").get("raised at")

    return load


def test_the_raised_at_words_name_the_caught_exception(loaded):
    raised = loaded(TR532 + SECTION + TR532_TAIL)
    assert raised == (
        "src/click/decorators.py:508 (NameError), caught by CliRunner inside the "
        "command, in a file your diff did not touch. The command's output was "
        "empty. The test's own assertion then failed at "
        "tests/test_version_option_version_format.py:17."), raised
    assert "before any assertion ran" not in raised and " so " not in raised


def test_the_raised_at_words_say_when_the_diff_touched_the_file(loaded, monkeypatch, tmp_path):
    """The fixture has no worktree, so `touched` is empty unless patched
    (the review of 878c2352, probe p4)."""
    from rota.core import worktrees
    from rota.roles import api

    monkeypatch.setattr(worktrees, "batch_files", lambda conn, bid: ["src/click/decorators.py"])
    monkeypatch.setattr(worktrees, "changed_since", lambda root, sha: [])
    monkeypatch.setattr(api, "_worktree_of", lambda ctx, bid: tmp_path)
    raised = loaded(TR532 + SECTION + TR532_TAIL)
    assert "src/click/decorators.py:508 (NameError)" in raised, raised
    assert "in a file your diff touched." in raised, raised


def test_the_raised_at_words_on_the_text_alone_stay(loaded):
    assert loaded(TR532 + TR532_TAIL) == (
        "tests/test_version_option_version_format.py:17, the test's own assertion")


def test_the_raised_at_words_on_a_non_assertion_error_stay(loaded):
    said = ("E   ModuleNotFoundError: No module named 'foo'\n"
            "src\\app.py:3: ModuleNotFoundError\n1 failed in 0.1s")
    assert loaded(said) == ("src/app.py:3 (ModuleNotFoundError) before any assertion "
                            "ran, in a file your diff did not touch")
