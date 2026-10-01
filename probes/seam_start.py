"""The seam start: a night that begins at the state under test.

A seam is a run database at the state under test, paired with the commit
the batch's worktree stood at. Night 101's database at its end is the first
pair (plans/frame104-seam-start.md, 2026-10-01). A warm start cannot carry
it: `warm_stamp.relocate` refuses a snapshot that holds a batch, and
`restore_click` removes every worktree and every `batch/*` branch.

`pair(db)` prints each running or deferred batch with its head commit. The
launcher command is then written from a fact, not from memory.

`restore(run, db, commit, root)` checks the door first and writes nothing
when the door refuses. The door refuses a snapshot behind the schema mark
and a commit that no running or deferred batch heads at. It refuses a head
that is not a commit in the checkout, a batch branch that a worktree holds,
a worktree path that exists and a run database that a process holds open.
The restore then adds a worktree for each running or deferred batch at the
batch's own head. Last, it replaces `$ROTA_RUNS/<run>.db` with the
snapshot, points the copy at the checkout and lays each batch's environment
and test files. A failure part way removes what the restore added and puts
the old run database back.

    python probes/seam_start.py pair .rota/clickI_night101.db
    python probes/seam_start.py restore clickI <db> <commit> <click_root> [--no-env]
"""
import gc
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from rota.core.worktrees import GIT, WorktreeError  # noqa: E402

LIVE = ("running", "deferred")
SUFFIXES = ("", "-wal", "-shm")


def _live(conn) -> list[tuple[str, str, str]]:
    return [(r[0], r[1], r[2] or "") for r in conn.execute(
        "SELECT id, status, head_commit FROM batches WHERE status IN (?, ?) ORDER BY id",
        LIVE)]


def _git(root, *args) -> subprocess.CompletedProcess:
    # Rota's git runs with no hooks (rota/core/worktrees.py, audit item 3).
    return subprocess.run([*GIT, "-C", str(root), *args], capture_output=True, text=True)


def _open_ro(db) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{Path(db).as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _checked_out(root: Path) -> set[str]:
    """The branches that a worktree of the checkout holds."""
    out = _git(root, "worktree", "list", "--porcelain").stdout
    return {line.split(" ", 1)[1].removeprefix("refs/heads/")
            for line in out.splitlines() if line.startswith("branch ")}


def pair(db_path) -> int:
    """Print one line per running or deferred batch. Return 1 when none."""
    conn = _open_ro(db_path)
    try:
        rows = _live(conn)
    finally:
        conn.close()
    if not rows:
        print("no running or deferred batch")
        return 1
    for bid, status, head in rows:
        print(f"{bid} {status} {head}")
    return 0


def _door(conn, commit: str, root: Path, home: Path) -> tuple[str | None, list]:
    """The sentence that refuses the pair, or None and the batches to
    restore as (id, head, headless). The door only reads. A refusal leaves
    the checkout and the runs as they were."""
    from rota.core.db import schema_stale
    stale = schema_stale(conn)
    if stale:
        return stale, []
    rows = _live(conn)
    if not rows:
        return "the snapshot holds no running or deferred batch", []
    if len(commit) < 7:
        return f"the commit {commit!r} is shorter than 7 characters", []
    # `lifecycle.start` leaves the head NULL until the first `code.commit`.
    # Such a batch has no commits to lose, so it comes back at the
    # checkout's HEAD.
    # The door reads the snapshot's own heads. The tip stands in for a
    # missing head only at the restore, so it never opens the door.
    if not any(head and (head == commit or head.startswith(commit)) for _, _, head in rows):
        held = ", ".join(f"{bid}@{head or 'none'}" for bid, _, head in rows)
        return f"no running or deferred batch heads at {commit}; the snapshot holds {held}", []
    tip = _git(root, "rev-parse", "HEAD").stdout.strip()
    picked = [(bid, head or tip, not head) for bid, _, head in rows]
    # Every running or deferred batch comes back at its own head. A batch
    # left out keeps the old night's path, and `worktrees.create` then cuts
    # its branch from main and loses its commits.
    held = _checked_out(root)
    for bid, head, _ in picked:
        if not head or _git(root, "cat-file", "-e", f"{head}^{{commit}}").returncode != 0:
            return f"{head or 'HEAD'} is not a commit in {root}", []
        if f"batch/{bid}" in held:
            return f"batch/{bid} is checked out in a worktree of {root}", []
        if (home / bid).exists():
            return f"{home / bid} exists already", []
    return None, picked


def _add(root: Path, home: Path, bid: str, head: str) -> None:
    """Add the batch's worktree on a new `batch/<id>` branch at its head."""
    branch = f"batch/{bid}"
    # `restore_click` deletes every batch branch, and the door saw that no
    # worktree holds this one. A branch that stands is stale.
    if _git(root, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}").returncode == 0:
        out = _git(root, "branch", "-D", branch)
        if out.returncode != 0:
            raise WorktreeError(f"git branch -D {branch}: {out.stderr.strip()}")
    out = _git(root, "worktree", "add", "-q", "-b", branch, str(home / bid), head)
    if out.returncode != 0:
        raise WorktreeError(f"git worktree add {branch}: {out.stderr.strip()}")


def _undo(root: Path, home: Path, added: list[str]) -> None:
    """Remove the worktrees and branches that this restore added."""
    for bid in added:
        _git(root, "worktree", "remove", "--force", str(home / bid))
        shutil.rmtree(home / bid, ignore_errors=True)
        _git(root, "branch", "-D", f"batch/{bid}")
    _git(root, "worktree", "prune")
    for d in (home, home.parent):
        try:
            d.rmdir()
        except OSError:
            pass


def _aside(target: Path) -> list[tuple[Path, Path]]:
    """Move the old run database and its journal files to one side.
    Windows refuses the move of a file that a process holds open, so the
    move is also the held-open check. Raise PermissionError and move
    nothing when the check fails."""
    moved: list[tuple[Path, Path]] = []
    try:
        for suffix in SUFFIXES:
            old = Path(f"{target}{suffix}")
            if old.exists():
                side = Path(f"{target}.seam-old{suffix}")
                side.unlink(missing_ok=True)
                old.rename(side)
                moved.append((old, side))
    except PermissionError:
        # The files that did not move are still the old ones. Only the
        # moved files go back, and nothing is deleted.
        _back(target, moved, created=False)
        raise
    return moved


def _back(target: Path, moved: list[tuple[Path, Path]], created: bool = True) -> None:
    """Put the old run database back where it was. With `created`, the
    restore wrote the files at the target path, because `_aside` moved
    every old file away first. Those files go."""
    if created:
        for suffix in SUFFIXES:
            Path(f"{target}{suffix}").unlink(missing_ok=True)
    for old, side in moved:
        side.rename(old)


def _reopen(target: Path) -> None:
    """Open the target once through `init_db`, which adds the columns the
    schema mark does not cover. A failure is raised again with no
    traceback. A traceback keeps the failed frame's connection open, and
    Windows then refuses the delete in `_back` (WinError 32)."""
    from rota.core import db as rota_db
    failed = None
    try:
        fresh = rota_db.init_db(target)
        fresh.commit()
        fresh.close()
    except BaseException as exc:                           # noqa: BLE001
        failed = exc.with_traceback(None)
    if failed is not None:
        gc.collect()
        raise failed


def restore(run: str, db_path, commit: str, click_root, env: bool = True) -> int:
    """Check the door, then restore the pair. Print one line. Return 0 or 1."""
    db = Path(db_path)
    root = Path(click_root)
    home = root / ".rota" / "worktrees"
    target = Path(os.environ.get("ROTA_RUNS", REPO / ".rota")) / f"{run}.db"
    if not db.is_file():
        print(f"SEAM REFUSED: {db} is not a file")
        return 1
    # The restore replaces the target, so a snapshot at the target path
    # would replace itself.
    if target.exists() and target.resolve() == db.resolve():
        print(f"SEAM REFUSED: the snapshot {db} is the run database it replaces")
        return 1
    src = _open_ro(db)
    try:
        refused, rows = _door(src, commit, root, home)
        if refused:
            print(f"SEAM REFUSED: {refused}")
            return 1
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            moved = _aside(target)
        except PermissionError as exc:
            print(f"SEAM REFUSED: {run}.db is held open: {exc}")
            return 1
        # The worktrees come first and the database comes last. Any failure
        # removes the added worktrees and puts the old database back, so no
        # run database names a missing worktree.
        added: list[str] = []
        dst = None
        try:
            home.mkdir(parents=True, exist_ok=True)
            # A worktree entry whose directory is gone blocks a new add at its path.
            _git(root, "worktree", "prune")
            for bid, head, _ in rows:
                _add(root, home, bid, head)
                added.append(bid)
            dst = sqlite3.connect(target)
            src.backup(dst)
            # The schema mark does not cover the columns that `init_db` adds
            # in place. Night 103 run 1 (2026-10-01) failed its first Critic
            # session on `verdicts.reason`. One open through `init_db` adds them.
            _reopen(target)
            dst.execute("UPDATE config SET value = ? WHERE key = 'project_root'", (str(root),))
            for bid, _, _ in rows:
                dst.execute("UPDATE batches SET worktree = ? WHERE id = ?", (str(home / bid), bid))
            # The snapshot's processes belong to the night that wrote it.
            # None of them runs in this night.
            dst.execute("DELETE FROM runtime_processes")
            dst.commit()
        except BaseException as exc:
            if dst is not None:
                dst.close()
            _undo(root, home, added)
            _back(target, moved)
            if isinstance(exc, WorktreeError):
                print(f"SEAM REFUSED: {exc}")
                return 1
            raise
        for _, side in moved:
            side.unlink(missing_ok=True)
    finally:
        src.close()
    notes: list[str] = []
    tests = 0
    try:
        dst.row_factory = sqlite3.Row
        if env:
            from rota.core import harness, provision
            for bid, _, _ in rows:
                _, note = provision.ensure_env(home / bid)
                dst.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                            (f"env:{bid}", note))
                notes.append(note)
                # The harness writes the Tester's files only when it runs,
                # and the seam commit need not hold them.
                tests += len(harness.materialise(home / bid, harness.tests_for(dst, bid)))
            dst.commit()
    finally:
        dst.close()
    line = f"SEAM: {run} at {commit[:8]} from {db}, {len(rows)} batch(es) restored in {root}"
    headless = [bid for bid, _, at_tip in rows if at_tip]
    if headless:
        line += "; " + ", ".join(f"{bid}@HEAD" for bid in headless)
    if env:
        line += f"; env: {' | '.join(notes)}; tests: {tests}"
    print(line)
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == "pair":
        sys.exit(pair(args[1]))
    if args and args[0] == "restore":
        rest = [a for a in args[1:] if a != "--no-env"]
        if len(rest) == 4:
            sys.exit(restore(*rest, env="--no-env" not in args))
    print(__doc__)
    sys.exit(2)
