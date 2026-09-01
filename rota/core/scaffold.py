"""
The harness floor: what a greenfield worktree needs before tests can answer.

S0's measurement: on an empty project the Tester and Developer each invent
conventions -- test paths with no home, two files implementing one program,
imports that resolve only by accident of pytest's rootdir guessing. The
harness runs `pytest <path> -q` with the worktree as cwd, and the floor is
exactly what makes that invocation deterministic: a pyproject that pins
testpaths and puts the project root on the import path, and a tests/
directory that exists.

Mechanical and idempotent -- no model, no judgement, nothing overwritten. A
repository that already has any test configuration is left entirely alone:
the floor is for ground that has none, which is the one shape (per the
seat's ruling) a scaffold may assume, because there is nothing there to
assume wrongly about.

Python-first, honestly: the delivery loop already is (the harness runs
pytest; `tests.encode` refuses bodies that are not Python). `LANGUAGES` is
the seam -- a second language adds an entry, not a redesign.
"""
from __future__ import annotations

import re
import sqlite3
import subprocess
from pathlib import Path

# Files whose presence means the project already made its own choices.
_EXISTING_CONFIG = ("pyproject.toml", "setup.py", "setup.cfg", "pytest.ini",
                    "tox.ini", "conftest.py")

_PYPROJECT = """\
[project]
name = "{name}"
version = "0.0.0"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
"""


def _python_floor(root: Path) -> list[str]:
    made: list[str] = []
    if not any((root / f).exists() for f in _EXISTING_CONFIG):
        name = re.sub(r"[^a-z0-9_-]+", "-", root.name.lower()).strip("-") or "project"
        (root / "pyproject.toml").write_text(
            _PYPROJECT.format(name=name), encoding="utf-8")
        made.append("pyproject.toml")
    tests = root / "tests"
    if not tests.is_dir():
        tests.mkdir()
        (tests / ".gitkeep").write_text("", encoding="utf-8")
        made.append("tests/")
    return made


LANGUAGES = {"python": _python_floor}


def ensure_floor(conn: sqlite3.Connection, batch_id: str,
                 language: str = "python") -> list[str]:
    """Lay the missing floor in the batch's worktree; return what was made."""
    row = conn.execute("SELECT worktree FROM batches WHERE id = ?",
                       (batch_id,)).fetchone()
    if not row or not row["worktree"]:
        return []
    root = Path(row["worktree"])
    if not root.is_dir():
        return []
    made = LANGUAGES[language](root)
    if made:
        # Commit-first is what bounds every loss in this system; the floor is
        # the batch's first commit, so a deferral keeps it.
        try:
            subprocess.run(["git", "add", "-A"], cwd=root, check=True,
                           capture_output=True)
            subprocess.run(["git", "-c", "user.email=rota@local",
                            "-c", "user.name=rota", "commit", "-qm",
                            "the harness floor"], cwd=root, check=True,
                           capture_output=True)
        except (subprocess.CalledProcessError, OSError):
            pass          # no git is the worktree's existing degraded mode
    return made
