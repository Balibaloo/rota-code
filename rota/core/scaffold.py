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


_MAIN = (
    '"""{name}: the program\'s entry point. Run it with `python main.py`."""',
    "import argparse",
    "",
    "",
    "def main(argv=None) -> int:",
    "    parser = argparse.ArgumentParser(prog={name!r})",
    "    parser.parse_args(argv)",
    "    print({name!r} + \": nothing to do yet\")",
    "    return 0",
    "",
    "",
    "if __name__ == \"__main__\":",
    "    raise SystemExit(main())",
    "",
)

_RUN_LINE = "Run it: `python main.py`"


def _program_floor(root: Path, name: str) -> list[str]:
    """
    An entry point, on ground that has no Python at all.

    The test floor made tests runnable. Nothing made the program runnable.
    Measured as the principal (tips4, 2026-09-04): "tip calculator pls" merged
    as one function in one file, with no `__main__`, no prompt, and no way to
    run it. The account said "the user types the bill and a tip percentage".
    Nobody could type anything.

    `main.py` is laid only where the tree has no test configuration and no
    `.py` file at all. A tree with either has an author's own idea of its
    shape, and the floor is for ground that has none. The stub parses `--help` and exits 0, so "the
    program starts" is true from the first commit, and the Developer wires
    the behaviour into `main()` rather than inventing a second entry point.
    The README gets the run line, so a person knows how to start it.
    """
    made: list[str] = []
    if any(root.rglob("*.py")):
        return made
    (root / "main.py").write_text(
        chr(10).join(line.format(name=name) for line in _MAIN), encoding="utf-8")
    made.append("main.py")
    readme = root / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        if "python main.py" not in text:
            readme.write_text(text.rstrip(chr(10)) + chr(10) * 2 + _RUN_LINE + chr(10),
                              encoding="utf-8")
            made.append("README.md")
    else:
        readme.write_text(f"# {name}" + chr(10) * 2 + _RUN_LINE + chr(10), encoding="utf-8")
        made.append("README.md")
    return made


def _python_floor(root: Path, name: str | None = None) -> list[str]:
    made: list[str] = []
    # Decided before anything is written: the pyproject this lays would
    # otherwise count as "existing config" one line later.
    bare = not any((root / f).exists() for f in _EXISTING_CONFIG)
    if bare:
        name = name or _slug(root.name)
        (root / "pyproject.toml").write_text(
            _PYPROJECT.format(name=name), encoding="utf-8")
        made.append("pyproject.toml")
    ignore = root / ".gitignore"
    if not ignore.exists():
        # Walk thirty-seven's delivered branch carried __pycache__: the
        # harness runs pytest in the worktree and the Developer commits -A.
        ignore.write_text(chr(10).join(["__pycache__/", "*.pyc", ".pytest_cache/", ""]),
                          encoding="utf-8")
        made.append(".gitignore")
    tests = root / "tests"
    if not tests.is_dir():
        tests.mkdir()
        (tests / ".gitkeep").write_text("", encoding="utf-8")
        made.append("tests/")
    if bare:
        name = name or _slug(root.name)
        made += _program_floor(root, name)
    return made


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", text.lower()).strip("-") or "project"


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
    # The project's name, not the worktree's. The worktree is named after the
    # batch, so the first merged program introduced itself as `bg_1` (tipsF,
    # 2026-09-08). The run records the project root; its name is the name.
    from .worktrees import project_root
    try:
        name = _slug(project_root(conn).name)
    except Exception:
        name = None
    made = LANGUAGES[language](root, name)
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


def ensure_repo(root: Path) -> bool:
    """A folder with no repository gets one, once, before the first worktree.

    The principal's own first trial: a plain folder, no `git init`. Onboarding
    tolerated it and batch start could not -- `git worktree add` needs a
    repository, the Developer had nowhere to build and the harness nothing to
    run, and nothing said so. Ground with no repository has nothing to assume
    wrongly about, which is the one shape the floor may lay (the seat's
    ruling); a folder that is already a repository is left entirely alone.
    Returns True when a repository was created.
    """
    if not root.is_dir() or (root / ".git").exists():
        return False
    probe = subprocess.run(["git", "-C", str(root), "rev-parse", "--git-dir"],
                           capture_output=True, text=True)
    if probe.returncode == 0:
        return False                       # inside some larger repository
    try:
        subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "-c", "user.email=rota@local", "-c", "user.name=rota",
                        "commit", "-qm", "the repository floor", "--allow-empty"],
                       cwd=root, check=True, capture_output=True)
    except (subprocess.CalledProcessError, OSError):
        return False
    return True

