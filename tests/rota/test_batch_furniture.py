"""F27: one reader names the files of a batch that no commit owns.

`worktrees.batch_furniture` is the reader. It folds each test path by the
grain fold, so `code.diff`, `code.write` and the end-of-session discard keep
the same files. Before F27 the discard folded the backslash alone, and a
test path stored as `./tests/x.py` was deleted at the session's end while
`code.diff` counted it as furniture (plans/rootfix-audit-2026-10-27-b.md,
F27). Law 4 holds: an uncommitted change never existed.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from rota.core import lifecycle, worktrees
from rota.core.db import init_db

ROOT = Path(__file__).resolve().parents[2] / "rota"


def _git(root: Path, *args: str) -> str:
    return subprocess.run([*worktrees.GIT, "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def _batch(tmp_path: Path, test_path: str):
    root = tmp_path / "tree"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@t")
    _git(root, "config", "user.name", "t")
    (root / "app.py").write_bytes(b"x = 1\n")
    _git(root, "add", "app.py")
    _git(root, "commit", "-q", "-m", "base")
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','x','in_scope','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES "
                 "('b1','i1','running',?)", (str(root),))
    conn.execute("INSERT INTO tests (id, batch_id, path, body) VALUES "
                 "('t1','b1',?,'assert True')", (test_path,))
    conn.commit()
    return conn, root


def test_the_furniture_folds_each_test_path_by_the_grain_fold(tmp_path):
    conn, _root = _batch(tmp_path, ".\\tests\\test_x.py")
    assert worktrees.batch_furniture(conn, "b1") == {"tests/test_x.py"}


def test_the_discard_keeps_a_test_file_stored_with_a_dot_prefix(tmp_path):
    conn, root = _batch(tmp_path, "./tests/test_x.py")
    (root / "tests").mkdir()
    (root / "tests" / "test_x.py").write_bytes(b"assert True\n")
    (root / "app.py").write_bytes(b"x = 2\n")
    gone = lifecycle.discard_uncommitted(conn, "b1")
    assert gone == ["app.py"]
    assert (root / "tests" / "test_x.py").is_file()


def test_the_batch_files_leave_out_a_test_file_stored_with_a_dot_prefix(tmp_path):
    conn, root = _batch(tmp_path, "./tests/test_x.py")
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
                 (str(root),))
    (root / "tests").mkdir()
    (root / "tests" / "test_x.py").write_bytes(b"assert True\n")
    (root / "app.py").write_bytes(b"x = 2\n")
    assert worktrees.batch_files(conn, "b1") == ["app.py"]


def test_one_function_reads_the_test_paths_as_furniture():
    """No second reader selects a batch's test paths to set them aside."""
    allowed = {("core/worktrees.py", "batch_furniture")}
    pattern = re.compile(r"SELECT path FROM tests WHERE batch_id")
    found = []
    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        fn = None
        for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            head = re.match(r"\s*def (\w+)", line)
            if head and not line.startswith((" " * 8,)):
                fn = head.group(1)
            if pattern.search(line) and (rel, fn) not in allowed:
                found.append(f"{rel}:{no} {fn}")
    assert found == []
