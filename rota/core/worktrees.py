"""
A worktree per batch. Created, kept, and destroyed by the scheduler.

The Developer never makes one. Law 9 puts every decision about a worktree's life
outside the role: one is created when a batch is dispatched, it survives
deferral with its commits intact, and it is destroyed only when the batch
merges. A role that could create its own would be deciding where its work lives,
which is a scheduling question wearing a tool.

**Nothing here removes a worktree it did not create.** The rule is the one the
test fixture uses and it exists for the same reason: this repository has 107
live worktrees. A removal is refused unless the path is recorded on the batch
*and* is under the state directory — two conditions, because either alone can be
satisfied by an accident.
"""
from __future__ import annotations

import shutil
import sqlite3
import subprocess

# Every git command rota runs. Hooks are the repository's code, and a
# checkout's hooks run on commit and merge with the user's rights; rota
# commits and merges what a model wrote, so its git runs with no hooks.
# The path names a directory that does not exist, which git treats as no
# hooks at all. Audit item 3 (rota/AUDIT.md, 2026-09-10).
GIT = ["git", "-c", "core.hooksPath=.rota/hooks-off"]
from pathlib import Path


class WorktreeError(RuntimeError):
    """Git refused, or the path was not ours to touch."""


def _git(root: Path, *args: str, check: bool = True) -> str:
    out = subprocess.run([*GIT, "-C", str(root), *args],
                         capture_output=True, text=True)
    if check and out.returncode != 0:
        raise WorktreeError(f"git {' '.join(args)}: {out.stderr.strip()}")
    return out.stdout


def project_root(conn: sqlite3.Connection) -> Path:
    """
    The project this database is about. **No default.**

    It used to fall back to `Path(".")`, which means the current working
    directory — so any session run without a configured root created a git
    worktree *in whatever repository the process happened to be started from*.
    That is exactly what happened: a test called `lifecycle.start` with no
    config and left a `batch/b1` worktree inside this repo, alongside the 107
    real ones.

    A missing root is a configuration error, and creating a worktree is not the
    kind of operation that gets to guess.
    """
    row = conn.execute(
        "SELECT value FROM config WHERE key = 'project_root'").fetchone()
    if not row or not (row["value"] or "").strip():
        raise WorktreeError(
            "no project_root in config: refusing to guess which repository to "
            "create a worktree in")
    return Path(row["value"].strip('"'))


def worktree_home(conn: sqlite3.Connection) -> Path:
    """
    Where batch worktrees live: `<project>/.rota/worktrees`.

    Inside the state directory rather than beside the project, so everything the
    system created is in one place and the boundary of "ours" is a path prefix
    rather than a naming convention.
    """
    return project_root(conn) / ".rota" / "worktrees"


def is_ours(conn: sqlite3.Connection, path: str | Path) -> bool:
    home = worktree_home(conn).resolve()
    try:
        target = Path(path).resolve()
    except OSError:
        return False
    return home == target or home in target.parents


def create(conn: sqlite3.Connection, batch_id: str) -> Path:
    """
    A branch and a worktree for one batch.

    A batch that already has one keeps it — that is what makes resuming a
    deferred batch a cold session in its *surviving* worktree rather than a
    fresh start, which is the whole reason commit-first bounds the loss.
    """
    row = conn.execute(
        "SELECT worktree FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if row is None:
        raise WorktreeError(f"no such batch: {batch_id}")
    if row["worktree"] and Path(row["worktree"]).is_dir():
        return Path(row["worktree"])

    root = project_root(conn)
    path = worktree_home(conn) / batch_id
    path.parent.mkdir(parents=True, exist_ok=True)

    branch = f"batch/{batch_id}"
    # A batch with no worktree on record never had one, so whatever stands
    # at its path is another run's. Two runs on one root name their first
    # batch b_1: the second's `worktree add` failed on the first's
    # directory, the failure was swallowed, and the Developer wrote and
    # committed on the project's master (tipsP, 2026-09-09). The stale
    # worktree goes; its branch is kept under a dated name as the record.
    if path.exists():
        _git(root, "worktree", "remove", "--force", str(path), check=False)
        shutil.rmtree(path, ignore_errors=True)
        _git(root, "worktree", "prune", check=False)
        old_sha = _git(root, "rev-parse", "--short", branch, check=False).strip()
        if old_sha:
            _git(root, "branch", "-m", branch, f"{branch}@{old_sha}", check=False)
    existing = _git(root, "branch", "--list", branch, check=False).strip()
    args = ["worktree", "add", "-q"]
    args += [str(path), branch] if existing else ["-b", branch, str(path)]
    _git(root, *args)

    conn.execute("UPDATE batches SET worktree = ? WHERE id = ?",
                 (str(path), batch_id))
    return path


def destroy(conn: sqlite3.Connection, batch_id: str) -> bool:
    """
    Remove a merged batch's worktree. Refused for anything not ours.

    The branch is left behind on purpose: it is the record of what was built,
    and deleting it would make a merged batch harder to inspect than an
    abandoned one.
    """
    row = conn.execute(
        "SELECT worktree FROM batches WHERE id = ?", (batch_id,)).fetchone()
    path = row and row["worktree"]
    if not path:
        return False
    if not is_ours(conn, path):
        raise WorktreeError(
            f"refusing to remove a worktree outside {worktree_home(conn)}: {path}")

    _git(project_root(conn), "worktree", "remove", "--force", str(path), check=False)
    shutil.rmtree(path, ignore_errors=True)
    conn.execute("UPDATE batches SET worktree = NULL WHERE id = ?", (batch_id,))
    return True


def head(path: str | Path) -> str | None:
    out = subprocess.run([*GIT, "-C", str(path), "rev-parse", "HEAD"],
                         capture_output=True, text=True)
    return out.stdout.strip() or None if out.returncode == 0 else None


def commit(path: str | Path, message: str) -> str | None:
    """
    Stage everything and commit. Returns the sha, or None if nothing changed.

    None is not a failure. A Developer session that reasoned, read and concluded
    the code was already right has nothing to commit, and inventing an empty
    commit to have something to report would be worse than saying so.
    """
    # Everything but the harness's own furniture. The batch's venv and the
    # run's state live inside the worktree and are not the project's:
    # under WSL (2026-09-10) `add -A` staged 952 files of `.venv` into the
    # first commit and the Critic reviewed them as the diff.
    subprocess.run([*GIT, "-C", str(path), "add", "-A", "--", ".",
                    ":(exclude).venv", ":(exclude).rota"],
                   capture_output=True, text=True)
    staged = subprocess.run([*GIT, "-C", str(path), "diff", "--cached", "--name-only"],
                            capture_output=True, text=True).stdout.strip()
    if not staged:
        return None
    out = subprocess.run([*GIT, "-C", str(path), "commit", "-q", "-m", message],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise WorktreeError(f"commit failed: {out.stderr.strip()}")
    return head(path)


def diff(path: str | Path, against: str = "HEAD~1") -> str:
    out = subprocess.run([*GIT, "-C", str(path), "diff", against, "HEAD"],
                         capture_output=True, text=True)
    return out.stdout


def touched(path: str | Path, against: str = "HEAD~1") -> list[str]:
    """The paths a batch's diff changed — the grains structural review joins on."""
    out = subprocess.run(
        [*GIT, "-C", str(path), "diff", "--name-only", against, "HEAD"],
        capture_output=True, text=True)
    return [line for line in out.stdout.splitlines() if line.strip()]


def integrate(conn: sqlite3.Connection, batch_id: str) -> str:
    """
    Merge the batch's branch into the branch the project is on.

    S0 walk thirty-seven: the first batch the story ever delivered was
    marked merged, its worktree removed, and the project's main branch still
    held only the initial commit -- `merge` had never merged anything. The
    branch is the record; the base branch is the deliverable. A clean merge
    returns the new head. An unclean one is aborted and raised, because a
    conflict is a wake, never a silent resolution.
    """
    root = project_root(conn)
    branch = f"batch/{batch_id}"
    if not _git(root, "branch", "--list", branch, check=False).strip():
        raise WorktreeError(f"no branch {branch} to merge")
    out = subprocess.run(
        [*GIT, "-C", str(root), "-c", "user.email=rota@local", "-c", "user.name=rota",
         "merge", "--no-ff", "--no-edit", "-m", f"rota: deliver {batch_id}", branch],
        capture_output=True, text=True)
    if out.returncode != 0:
        subprocess.run([*GIT, "-C", str(root), "merge", "--abort"],
                       capture_output=True, text=True)
        raise WorktreeError(f"merge of {branch} is not clean: {out.stderr.strip()[:300]}")
    return _git(root, "rev-parse", "HEAD").strip()

