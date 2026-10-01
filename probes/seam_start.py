"""The seam start: a night that begins at the state under test.

A seam is a run database at the state under test, paired with the commit
the batch's worktree stood at. Night 101's database at its end is the first
pair (plans/frame104-seam-start.md, 2026-10-01). A warm start cannot carry
it: `warm_stamp.relocate` refuses a snapshot that holds a batch, and
`restore_click` removes every worktree and every `batch/*` branch.

`pair(db)` prints each running or deferred batch with its head commit. The
launcher command is then written from a fact, not from memory.

`restore(run, db, commit, root)` checks the door first and writes nothing
when the door refuses. The door refuses a snapshot behind the schema mark,
a commit that no running or deferred batch heads at, and a head that is not
a commit in the checkout. The restore then copies the snapshot to
`$ROTA_RUNS/<run>.db`, points the copy at the checkout, adds each batch's
worktree at its head and lays the batch's environment.

    python probes/seam_start.py pair .rota/clickI_night101.db
    python probes/seam_start.py restore clickI <db> <commit> <click_root> [--no-env]
"""
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LIVE = ("running", "deferred")


def _live(conn) -> list[tuple[str, str, str]]:
    return [(r[0], r[1], r[2] or "") for r in conn.execute(
        "SELECT id, status, head_commit FROM batches WHERE status IN (?, ?) ORDER BY id",
        LIVE)]


def _git(root, *args) -> subprocess.CompletedProcess:
    # Rota's git runs with no hooks (rota/core/worktrees.py, audit item 3).
    sys.path.insert(0, str(REPO))
    from rota.core.worktrees import GIT
    return subprocess.run([*GIT, "-C", str(root), *args], capture_output=True, text=True)


def _open_ro(db) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{Path(db).as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


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


def _door(conn, commit: str, root: Path) -> tuple[str | None, list]:
    """The sentence that refuses the pair, or None and the batches to restore."""
    sys.path.insert(0, str(REPO))
    from rota.core.db import schema_stale
    stale = schema_stale(conn)
    if stale:
        return stale, []
    rows = _live(conn)
    if not rows:
        return "the snapshot holds no running or deferred batch", []
    if len(commit) < 7:
        return f"the commit {commit!r} is shorter than 7 characters", []
    picked = [r for r in rows if r[2] and (r[2] == commit or r[2].startswith(commit))]
    if not picked:
        held = ", ".join(f"{bid}@{head or 'none'}" for bid, _, head in rows)
        return f"no running or deferred batch heads at {commit}; the snapshot holds {held}", []
    for _, _, head in picked:
        if _git(root, "cat-file", "-e", f"{head}^{{commit}}").returncode != 0:
            return f"{head} is not a commit in {root}", []
    return None, picked


def restore(run: str, db_path, commit: str, click_root, env: bool = True) -> int:
    """Check the door, then restore the pair. Print one line. Return 0 or 1."""
    db = Path(db_path)
    root = Path(click_root)
    target = Path(os.environ.get("ROTA_RUNS", REPO / ".rota")) / f"{run}.db"
    if not db.is_file():
        print(f"SEAM REFUSED: {db} is not a file")
        return 1
    # The restore deletes the target first, so a snapshot at the target
    # path would delete itself.
    if target.exists() and target.resolve() == db.resolve():
        print(f"SEAM REFUSED: the snapshot {db} is the run database it replaces")
        return 1
    src = _open_ro(db)
    try:
        refused, picked = _door(src, commit, root)
        if refused:
            print(f"SEAM REFUSED: {refused}")
            return 1
        target.parent.mkdir(parents=True, exist_ok=True)
        for suffix in ("", "-wal", "-shm"):
            Path(f"{target}{suffix}").unlink(missing_ok=True)
        dst = sqlite3.connect(target)
        src.backup(dst)
    finally:
        src.close()
    try:
        home = root / ".rota" / "worktrees"
        dst.execute("UPDATE config SET value = ? WHERE key = 'project_root'", (str(root),))
        for bid, _, _ in picked:
            dst.execute("UPDATE batches SET worktree = ? WHERE id = ?", (str(home / bid), bid))
        # The snapshot's processes belong to the night that wrote it. None
        # of them runs in this night.
        dst.execute("DELETE FROM runtime_processes")
        dst.commit()
        home.mkdir(parents=True, exist_ok=True)
        # A worktree entry whose directory is gone blocks a new add at its path.
        _git(root, "worktree", "prune")
        for bid, _, head in picked:
            branch = f"batch/{bid}"
            # `restore_click` deletes every batch branch, so a branch that
            # still stands here is stale.
            if _git(root, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}").returncode == 0:
                out = _git(root, "branch", "-D", branch)
                if out.returncode != 0:
                    print(f"SEAM REFUSED: git branch -D {branch}: {out.stderr.strip()}")
                    return 1
            out = _git(root, "worktree", "add", "-q", "-b", branch, str(home / bid), head)
            if out.returncode != 0:
                print(f"SEAM REFUSED: git worktree add {branch}: {out.stderr.strip()}")
                return 1
        notes = []
        if env:
            sys.path.insert(0, str(REPO))
            from rota.core import provision
            for bid, _, _ in picked:
                _, note = provision.ensure_env(home / bid)
                dst.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                            (f"env:{bid}", note))
                notes.append(note)
            dst.commit()
    finally:
        dst.close()
    short = picked[0][2][:8]
    line = f"SEAM: {run} at {short} from {db}, {len(picked)} batch(es) restored in {root}"
    if env:
        line += f"; env: {' | '.join(notes)}"
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
