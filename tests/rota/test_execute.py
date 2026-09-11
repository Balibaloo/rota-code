"""The runner seam: the harness runs commands through one door with a name."""
from __future__ import annotations

import pytest


def test_local_runs_and_names_a_timeout(tmp_path):
    import sys

    from rota.core import execute

    out = execute.run(tmp_path, [sys.executable, "-c", "print('hi')"], timeout=30)
    assert out.returncode == 0 and out.stdout.strip() == "hi" and not out.error
    slow = execute.run(tmp_path, [sys.executable, "-c", "import time; time.sleep(5)"],
                       timeout=1)
    assert slow.timed_out and "timed out" in slow.error


def test_an_unknown_runner_is_refused_by_name(tmp_path, monkeypatch):
    from rota.core import execute

    monkeypatch.setenv("ROTA_RUNNER", "container")
    with pytest.raises(KeyError, match="container"):
        execute.run(tmp_path, ["true"], timeout=1)


def test_the_harness_runs_its_tests_on_the_chosen_runner(tmp_path, monkeypatch):
    from rota.core import execute, harness

    seen = []

    def fake(worktree, argv, timeout):
        seen.append((worktree, argv[1:], timeout))
        return execute.Result(0, "1 passed", "")

    monkeypatch.setitem(execute.RUNNERS, "fake", fake)
    verdict, said = harness._run_one(tmp_path, "tests/test_x.py", 7, runner="fake")
    assert verdict == "pass" and said == "1 passed"
    assert seen[0][0] == tmp_path and seen[0][2] == 7
    assert seen[0][1][:2] == ["-m", "pytest"]


def test_a_packaged_project_is_installable(tmp_path):
    """clickI (2026-09-11): a src layout, every test errored on the conftest
    import of the project itself. Only a project that says how it is built."""
    from rota.core.provision import project_installable

    nl = chr(10)
    assert not project_installable(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[project]" + nl + "name='click'" + nl, encoding="utf-8")
    assert not project_installable(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        "[build-system]" + nl + "requires=['flit_core']" + nl + "build-backend='flit_core.buildapi'" + nl
        + "[project]" + nl + "name='click'" + nl, encoding="utf-8")
    assert project_installable(tmp_path)
