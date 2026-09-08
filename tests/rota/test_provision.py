"""
A batch's own environment, so a test can import what the project declares.

The harness ran rota's own interpreter. A project that imported anything rota
did not have could not be tested, and nothing said why. `ensure_env` lays
`.venv` in the worktree with pytest and the declared dependencies, and
`python_for` names the interpreter the harness runs. Best effort: a failure
falls back to rota's interpreter, which is what always ran.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from rota.core import provision


def test_python_for_falls_back_to_rota_s_interpreter(tmp_path):
    assert provision.python_for(tmp_path) == sys.executable


def test_declared_dependencies_read_the_pyproject(tmp_path):
    assert provision.declared_dependencies(tmp_path) == []
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\nversion = "0.0.0"\ndependencies = ["rich"]\n',
        encoding="utf-8")
    assert provision.declared_dependencies(tmp_path) == ["rich"]


def test_ensure_env_lays_an_interpreter_that_has_pytest(tmp_path):
    """Slow by nature: a real venv and a real pip. Once per test run."""
    py, note = provision.ensure_env(tmp_path)
    assert py is not None, note
    assert py.exists(), note
    assert "made .venv" in note and "installed pytest" in note, note
    out = subprocess.run([str(py), "-c", "import pytest; print(pytest.__version__)"],
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    assert provision.python_for(tmp_path) == str(py)
    # Idempotent: the second call keeps the venv and repeats only the install.
    py2, note2 = provision.ensure_env(tmp_path)
    assert py2 == py and "made .venv" not in note2, note2
