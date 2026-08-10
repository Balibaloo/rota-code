"""
A real git repository per test, and a teardown that cannot reach a real one.

Five roles need this, not only Developer: Architect reads source and diffs,
Terminologist and Gatekeeper survey code, Critic reads the batch diff. The
Developer is only the one that also *writes*.

**The safety rule is the load-bearing part.** This repository has 107 live
worktrees and none of them is under a temp directory. A teardown that removes by
name, or prunes on failure, could take out real work. So: everything is created
under `tmp_path`, the set of registered worktrees is snapshotted before, and
teardown removes only what is both **new** and **temp-rooted**. That is the rule
`tests/conftest.py` already uses to survive this repo, and it is copied here
deliberately rather than reinvented.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .samplerepo import PLANTED, create


def _temp_roots() -> list[Path]:
    return [Path(tempfile.gettempdir()).resolve()]


def is_temp_rooted(path: Path) -> bool:
    """True only if `path` sits under a system temp directory."""
    try:
        resolved = Path(path).resolve()
    except OSError:
        return False
    return any(root == resolved or root in resolved.parents for root in _temp_roots())


def git(root: Path, *args: str, check: bool = True) -> str:
    out = subprocess.run(["git", "-C", str(root), *args],
                         capture_output=True, text=True)
    if check and out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {out.stderr.strip()}")
    return out.stdout


def registered_worktrees(root: Path) -> set[str]:
    lines = git(root, "worktree", "list", "--porcelain", check=False).splitlines()
    return {line.split(" ", 1)[1] for line in lines if line.startswith("worktree ")}


@dataclass
class SampleRepo:
    """A checkout of the sample project, plus the worktrees a test made."""
    root: Path
    planted: dict = field(default_factory=lambda: dict(PLANTED))
    _worktrees: list[Path] = field(default_factory=list)
    _before: set[str] = field(default_factory=set)

    # ---- reading -----------------------------------------------------------

    def head(self, at: Path | None = None) -> str:
        return git(at or self.root, "rev-parse", "HEAD").strip()

    def log(self, n: int = 10) -> list[str]:
        return git(self.root, "log", f"-{n}", "--format=%h %s").strip().splitlines()

    def diff(self, at: Path | None = None) -> str:
        return git(at or self.root, "diff", "HEAD~1", "HEAD")

    # ---- worktrees ---------------------------------------------------------

    def worktree(self, name: str) -> Path:
        """
        A branch and a worktree, both under the temp root.

        The path is derived from the repo root rather than taken as an argument
        precisely so a caller cannot place one outside the sandbox.
        """
        path = self.root.parent / "worktrees" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if not is_temp_rooted(path):
            raise RuntimeError(
                f"refusing to create a worktree outside a temp directory: {path}")
        git(self.root, "worktree", "add", "-q", "-b", f"batch/{name}", str(path))
        self._worktrees.append(path)
        return path

    def commit_in(self, worktree: Path, message: str) -> str:
        git(worktree, "add", "-A")
        git(worktree, "commit", "-q", "-m", message)
        return self.head(worktree)

    def edit(self, worktree: Path, rel: str, body: str) -> Path:
        target = worktree / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        return target

    # ---- teardown ----------------------------------------------------------

    def remove_worktrees(self) -> list[str]:
        """
        Remove only what this fixture made, and only under temp.

        Two conditions, both required. New-but-not-temp is refused because the
        snapshot could be wrong; temp-but-not-new is refused because another
        test may still be using it.
        """
        removed = []
        for path in list(self._worktrees):
            if not is_temp_rooted(path):
                continue                       # never, under any circumstance
            if str(path) in self._before:
                continue                       # not ours
            git(self.root, "worktree", "remove", "--force", str(path), check=False)
            removed.append(str(path))
        return removed


def make(tmp_path: Path, *, name: str = "sample") -> SampleRepo:
    """Build the sample project under `tmp_path` and hand back a handle."""
    if not is_temp_rooted(tmp_path):
        raise RuntimeError(
            f"the git fixture only builds under a temp directory, not {tmp_path}")
    root = create(tmp_path / name)
    repo = SampleRepo(root=root)
    repo._before = registered_worktrees(root)
    return repo


def cleanup(repo: SampleRepo) -> list[str]:
    removed = repo.remove_worktrees()
    if is_temp_rooted(repo.root):
        shutil.rmtree(repo.root, ignore_errors=True)
    return removed
