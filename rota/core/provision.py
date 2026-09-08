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
            subprocess.run([sys.executable, "-m", "venv", str(root / VENV)],
                           check=True, capture_output=True, text=True,
                           timeout=timeout)
        except (subprocess.SubprocessError, OSError) as exc:
            return None, f"could not create {VENV}: {exc}"
        notes.append(f"made {VENV}")
    wanted = ["pytest", *declared_dependencies(root)]
    try:
        out = subprocess.run([str(py), "-m", "pip", "install", "-q",
                              "--disable-pip-version-check", *wanted],
                             cwd=root, capture_output=True, text=True,
                             timeout=timeout)
    except (subprocess.SubprocessError, OSError) as exc:
        return py, f"{'; '.join(notes)}; pip did not run: {exc}"
    if out.returncode != 0:
        tail = (out.stderr or out.stdout).strip().splitlines()[-1:] or ["no output"]
        return py, f"{'; '.join(notes)}; pip install failed: {tail[0]}"
    notes.append(f"installed {', '.join(wanted)}")
    return py, "; ".join(notes)
