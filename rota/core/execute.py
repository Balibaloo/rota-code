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
from typing import Callable, Mapping


@dataclass(frozen=True)
class Result:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
    error: str = ""


Runner = Callable[[Path, list[str], int, Mapping[str, str] | None], Result]


def _local(worktree: Path, argv: list[str], timeout: int,
           env: Mapping[str, str] | None = None) -> Result:
    # The mapping goes over the process environment and never replaces it,
    # because the child still needs PATH and the venv's own variables.
    full = None if env is None else {**os.environ, **env}
    # The child's output is decoded as UTF-8, and a byte that is not UTF-8
    # becomes U+FFFD. With `text=True` alone the decode runs in the console
    # codepage, cp1252 here, and byte 0x8d in a pytest output killed the
    # reader thread six times on dry run 7 (observed:
    # `plans/dry7-read-2026-11-07.md`, question G, 2026-11-07).
    try:
        out = subprocess.run(argv, cwd=worktree, capture_output=True,
                             encoding="utf-8", errors="replace",
                             timeout=timeout, env=full)
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
        runner: str | None = None,
        env: Mapping[str, str] | None = None) -> Result:
    """Run `argv` inside `worktree` on the chosen runner.

    `env` is merged over the process environment. The harness uses it to
    put rota's pytest plugin on `PYTHONPATH` (frame 195).
    """
    return RUNNERS[chosen(runner)](Path(worktree), list(argv), timeout,
                                   None if env is None else dict(env))
