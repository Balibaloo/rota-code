"""
A batch's own environment: an interpreter that has what the project declares.

The harness ran `sys.executable -m pytest`: rota's own interpreter, rota's own
packages. A project that imported anything rota did not have could not be
tested, and nothing said why. The floor made tests runnable in the file-system
sense. This makes them runnable in the import sense.

Mechanical and best-effort. `ensure_env` lays `<worktree>/.venv` once, installs
`pytest` and the dependencies the project declares in `pyproject.toml`, and
returns the interpreter. Any failure returns None with a note, and the harness
falls back to rota's interpreter, which is what it always did. A network that is
down or a package that does not exist is the project's problem to surface, not
a reason for the run to stop.

Python only, like the floor. The seam for a second language is `python_for`:
whatever answers "which interpreter runs this worktree's tests".
"""
from __future__ import annotations

import subprocess

from . import execute
import sys
from pathlib import Path

VENV = ".venv"


def venv_python(root: Path) -> Path:
    """Where the environment's interpreter lives, made or not."""
    if sys.platform == "win32":
        return root / VENV / "Scripts" / "python.exe"
    return root / VENV / "bin" / "python"


def python_for(root: Path) -> str:
    """The interpreter that runs this worktree's tests."""
    made = venv_python(root)
    return str(made) if made.exists() else sys.executable


def declared_dependencies(root: Path) -> list[str]:
    """`[project].dependencies` from pyproject.toml, or nothing."""
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return []
    try:
        import tomllib
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except Exception:
        return []
    deps = (data.get("project") or {}).get("dependencies") or []
    return [d for d in deps if isinstance(d, str) and d.strip()]


def project_installable(root: Path) -> bool:
    """
    The project itself is a package the tests import: a `[project]` table
    in pyproject.toml or a setup.py. clickI (2026-09-11): a src layout,
    every test errored at the conftest on `No module named 'click'`, and
    the batch's only test never ran. The dependencies were installed; the
    project was not.
    """
    root = Path(root)
    if (root / "setup.py").exists():
        return True
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return False
    try:
        import tomllib
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except Exception:
        return False
    # A project that says how it is built. A bare `[project]` table, the
    # scaffold's shape, builds under setuptools' auto-discovery and that
    # discovery is a guess about a flat layout; the arc suite's scaffolded
    # repository went from green to a harness error on it.
    if not data.get("build-system"):
        return False
    return bool(data.get("project")) or bool((data.get("tool") or {}).get("poetry"))


def ensure_env(root: Path, *, timeout: int = 600) -> tuple[Path | None, str]:
    """
    Lay the environment if it is missing. Returns (interpreter, note).

    Idempotent: an existing `.venv` is kept and only the dependency install is
    repeated, which pip makes a no-op when nothing changed.
    """
    root = Path(root)
    py = venv_python(root)
    notes: list[str] = []
    if not py.exists():
        try:
            made = execute.run(root, [sys.executable, "-m", "venv", str(root / VENV)],
                               timeout=timeout)
            if made.error or made.returncode != 0:
                raise OSError(made.error or made.stderr.strip()[-200:])
        except (KeyError, OSError) as exc:
            return None, f"could not create {VENV}: {exc}"
        notes.append(f"made {VENV}")
    wanted = ["pytest", *declared_dependencies(root)]
    try:
        out = execute.run(root, [str(py), "-m", "pip", "install", "-q",
                                 "--disable-pip-version-check", *wanted],
                          timeout=timeout)
        if out.error:
            raise OSError(out.error)
    except (KeyError, OSError) as exc:
        return py, f"{'; '.join(notes)}; pip did not run: {exc}"
    if out.returncode != 0:
        tail = (out.stderr or out.stdout).strip().splitlines()[-1:] or ["no output"]
        return py, f"{'; '.join(notes)}; pip install failed: {tail[0]}"
    notes.append(f"installed {', '.join(wanted)}")
    # The project itself, editable and without its dependencies, which are
    # above. Its build backend runs here: the project's own manifest, the
    # same trust as its dependencies (AUDIT item 1).
    if project_installable(root):
        try:
            out = execute.run(root, [str(py), "-m", "pip", "install", "-q",
                                     "--disable-pip-version-check", "--no-deps",
                                     "-e", "."], timeout=timeout)
            if out.error or out.returncode != 0:
                tail = (out.error or out.stderr or out.stdout).strip().splitlines()[-1:] or ["no output"]
                notes.append(f"project install failed: {tail[0][:160]}")
            else:
                notes.append("installed the project (editable)")
        except KeyError as exc:
            notes.append(f"project install did not run: {exc}")
    return py, "; ".join(notes)
