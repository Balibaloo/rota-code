"""
A batch's `.venv`, copied from one built once per process.

`provision.ensure_env` runs `python -m venv` and then pip in each new
worktree. In `tests/rota/test_developer.py` that cost about 11s a test and
326s of the 466s that one xdist worker held the suite's tail (observed:
frame 206's count, 2026-10-11). A copy of a built venv cost 1.1s, and pip
on the copy, with nothing to install, cost 0.9s (observed: frame 206's
probe, 2026-10-11).

The wrapper copies the template into `<root>/.venv` and then calls the real
`ensure_env`. So pip still runs in the batch's own environment, through the
same `execute.run` seam, and the harness runs the batch's tests with the
copy's interpreter. A copied venv still runs, because `pyvenv.cfg` names the
base interpreter by `home`, and the copy keeps that line.

Two cases go to the real path untouched. A root with a `.venv` already has
its environment. A project that pip installs editable gets a link to its own
path, and a copy would carry a link to the template's path instead.

`rota/core/provision.py` stays as it is. A run lays one venv per batch, so a
template in production buys nothing.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from ..core import provision as _provision
from .gitfixture import is_temp_rooted, template

_REAL = _provision.ensure_env


def _key(root: Path) -> tuple:
    """The template's key: the base interpreter and what pip installs.
    A change to the declared dependencies makes a new template."""
    return ("venv", sys.executable,
            tuple(_provision.test_requirements(root)))


def _build(root: Path):
    def build(base: Path):
        # The template takes the root's own manifest, so that the real
        # `ensure_env` installs what the root declares.
        manifest = Path(root) / "pyproject.toml"
        if manifest.exists():
            shutil.copyfile(manifest, base / "pyproject.toml")
        return _REAL(base)
    return build


def ensure_env(root: Path, *, timeout: int = 600) -> tuple[Path | None, str]:
    """`ensure_env`, with a new `.venv` started as a copy of the template."""
    root = Path(root)
    dest = root / _provision.VENV
    if (dest.exists() or not is_temp_rooted(root)
            or _provision.project_installable(root)):
        return _REAL(root, timeout=timeout)
    base, (py, note) = template(_key(root), _build(root))
    # A template whose build failed is no template. The real path then
    # gives the test the failure note a run would give.
    if py is None or "installed" not in note:
        return _REAL(root, timeout=timeout)
    shutil.copytree(base / _provision.VENV, dest)
    made, rest = _REAL(root, timeout=timeout)
    # The real call found a `.venv`, so its note lacks the part that a
    # fresh run writes first. The note goes to config as a run writes it.
    return made, (f"made {_provision.VENV}; {rest.lstrip('; ')}" if rest else note)
