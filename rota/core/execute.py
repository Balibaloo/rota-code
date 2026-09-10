"""
The runner seam: every command the harness runs inside a worktree goes
through `run`. Audit item 2 (rota/AUDIT.md, 2026-09-10).

One function, one registry. `local` runs the command on this machine
with the user's rights, which is what rota has always done. A container
or a WSL runner plugs in as another name and nothing above this line
changes. The name comes from the `runner` setting, or `ROTA_RUNNER` when
no run is at hand (provisioning runs before the batch's first session).
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class Result:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
    error: str = ""


Runner = Callable[[Path, list[str], int], Result]


def _local(worktree: Path, argv: list[str], timeout: int) -> Result:
    try:
        out = subprocess.run(argv, cwd=worktree, capture_output=True,
                             text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return Result(-1, "", "", timed_out=True, error=f"timed out after {timeout}s")
    except OSError as exc:
        return Result(-1, "", "", error=str(exc))
    return Result(out.returncode, out.stdout or "", out.stderr or "")


RUNNERS: dict[str, Runner] = {"local": _local}


def chosen(name: str | None = None) -> str:
    name = name or os.environ.get("ROTA_RUNNER") or "local"
    if name not in RUNNERS:
        raise KeyError(f"no runner named {name!r}; known: {sorted(RUNNERS)}")
    return name


def run(worktree: Path | str, argv: list[str], *, timeout: int,
        runner: str | None = None) -> Result:
    """Run `argv` inside `worktree` on the chosen runner."""
    return RUNNERS[chosen(runner)](Path(worktree), list(argv), timeout)
