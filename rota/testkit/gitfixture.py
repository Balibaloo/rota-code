"""
A real git repository per test, and a teardown that cannot reach a real one.

Five roles need this, not only Developer: Architect reads source and diffs,
Terminologist and Vision Keeper survey code, Critic reads the batch diff. The
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

import atexit
import shutil
import stat
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .samplerepo import GIT_ENV, PLANTED, create


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
    # Under the same pinned identity and clock the sample repo is built with --
    # see `samplerepo.GIT_ENV`. A commit made here with the ambient clock would
    # be as unreplayable as one made there, and worse for being the exception.
    import os

    out = subprocess.run(["git", "-C", str(root), *args],
                         capture_output=True, text=True,
                         env={**os.environ, **GIT_ENV})
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

        `<root>/.rota/worktrees/<name>` is where `worktrees.worktree_home` puts
        a batch's tree in production. Beside the root, as this was until
        2026-09-17, a test walked a layout no run has: `.rota` is in the
        indexer's skip set, so a worktree inside the project is the case that
        has to work.
        """
        path = self.root / ".rota" / "worktrees" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if not is_temp_rooted(path):
            raise RuntimeError(
                f"refusing to create a worktree outside a temp directory: {path}")
        git(self.root, "worktree", "add", "-q", "-b", f"batch/{name}", str(path))
        self._worktrees.append(path)
        return path

    def commit_in(self, worktree: Path, message: str) -> str:
        git(worktree, "add", "-A")
        if not git(worktree, "diff", "--cached", "--name-only").strip():
            # `git commit` on an unchanged tree exits 1 with nothing on stderr,
            # which surfaces as a bare `RuntimeError: git commit -q -m ...:` and
            # says nothing about the cause. The cause is always the same: a
            # case whose `edit:` is byte-identical to the file it replaces, so
            # the role it is meant to test would be handed an empty diff.
            raise RuntimeError(
                f"nothing to commit in {worktree.name}: the edit matches what "
                f"was already there, so there is no diff to judge")
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


# key -> (the base directory, the value its builder returned)
_TEMPLATES: dict[object, tuple[Path, object]] = {}


def template(key, build) -> tuple[Path, object]:
    """
    The tree `build(base)` makes under a new `base`, built once per process
    for each `key`, and the value `build` returned.

    The sample project and every other per-test repository share this one
    mechanism (frame 203). A fixture that runs `git init` and seed commits
    per test pays one process spawn per git call, and a copy pays none.
    """
    entry = _TEMPLATES.get(key)
    if entry is None or not entry[0].exists():
        base = Path(tempfile.mkdtemp(prefix="rota_template_"))
        # One per process, and under xdist that is one per worker. Left behind
        # they accumulate in the temp directory a run at a time, which is how a
        # test suite quietly becomes something that fills a disk.
        #
        # It did. `shutil.rmtree(..., ignore_errors=True)` cannot delete a
        # read-only file, git marks every object read-only, and 1435 of these
        # templates were on this machine holding 86150 files (observed: frame
        # 63's pass 3, 2026-09-22). The bit is cleared first now.
        atexit.register(_drop_template, base)
        entry = (base, build(base))
        _TEMPLATES[key] = entry
    return entry


def copy_template(key, build, dest: Path):
    """
    Copy each child of the template for `key` into `dest`, and return the
    value its builder returned.

    A linked worktree names its repository by an absolute path, and the
    repository names the worktree the same way. Both point into the template
    until `_relink` moves them to `dest`.
    """
    if not is_temp_rooted(dest):
        raise RuntimeError(
            f"a template is only copied under a temp directory, not {dest}")
    base, value = template(key, build)
    dest.mkdir(parents=True, exist_ok=True)
    for child in base.iterdir():
        if child.is_dir():
            shutil.copytree(child, dest / child.name)
        else:
            shutil.copyfile(child, dest / child.name)
    _relink(base, dest)
    return value


def _relink(old: Path, new: Path) -> None:
    """Point each copied worktree link at the copy, not at the template."""
    links = [p for p in new.glob("*/.git") if p.is_file()]
    links += new.glob("*/.git/worktrees/*/gitdir")
    pairs = [(str(old).encode(), str(new).encode()),
             (old.as_posix().encode(), new.as_posix().encode())]
    for link in links:
        body = link.read_bytes()
        for before, after in pairs:
            body = body.replace(before, after)
        # Git on Windows marks a worktree's `.git` file hidden, and Windows
        # refuses to create over a hidden file. So the file is opened in place.
        with link.open("r+b") as handle:
            handle.write(body)
            handle.truncate()


def _template() -> Path:
    """
    The sample project, built once per process and copied thereafter.

    `create` spends its time in seventeen `git` subprocess spawns — init, two
    configs, and seven staged commits — which is 1.9s on Windows, where process
    creation costs far more than the work inside it. Function-scoped, that was
    55 seconds of `test_onboarding.py` alone, for twenty-nine tests of which
    exactly zero read a commit. The suite was not compute-bound and never looked
    it: the CPU sat idle waiting on `CreateProcess`.

    Copied rather than shared, because the tests write to their checkout. A copy
    of a small repository is ~50ms and preserves the history the few tests that
    do want it depend on, which `create(commits=False)` would have thrown away.
    """
    base, _ = template("sample", lambda b: create(b / "sample"))
    return base / "sample"


def make(tmp_path: Path, *, name: str = "sample") -> SampleRepo:
    """Build the sample project under `tmp_path` and hand back a handle."""
    if not is_temp_rooted(tmp_path):
        raise RuntimeError(
            f"the git fixture only builds under a temp directory, not {tmp_path}")
    root = tmp_path / name
    shutil.copytree(_template(), root)
    # `.rota/` out of this checkout's git. A batch worktree lives at
    # `<root>/.rota/worktrees/<name>`, and without this `commit_in(root)` runs
    # `git add -A` over it and records a gitlink, with git's embedded-repository
    # warning. In `.git/info/exclude` rather than in the sample's `.gitignore`
    # because the exclude file is not part of the tree: no case's prompt moves,
    # so no recording goes stale.
    exclude = root / ".git" / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    exclude.write_text(".rota/\n", encoding="utf-8", newline="\n")
    repo = SampleRepo(root=root)
    repo._before = registered_worktrees(root)
    return repo


def _drop_template(base: Path) -> None:
    """The process's sample template, deleted at exit. It is a git repository,
    so the read-only bits come off first."""
    _unlock(base)
    shutil.rmtree(base, ignore_errors=True)


def _unlock(root: Path) -> None:
    """
    Clear the read-only bit git puts on the files in `.git/objects`.

    Windows refuses to delete a read-only file, so the whole `.git` survived
    every cleanup and `ignore_errors=True` hid the refusal. One chain left a
    git checkout in the temp directory on every report and every gate
    (observed: frame 63's pass 3, 2026-09-22).
    """
    for path in root.rglob("*"):
        try:
            path.chmod(stat.S_IWRITE | stat.S_IREAD)
        except OSError:                                     # pragma: no cover
            # A file something else holds. The delete below reports it.
            pass


def cleanup(repo: SampleRepo) -> list[str]:
    removed = repo.remove_worktrees()
    if is_temp_rooted(repo.root):
        _unlock(repo.root)
        # Teardown never fails a run. A residue that survives this is
        # reported by whoever deletes the directory above it.
        shutil.rmtree(repo.root, ignore_errors=True)
    return removed
