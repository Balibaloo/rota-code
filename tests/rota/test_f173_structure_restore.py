"""
The structure puts a removed statement back with no model (frame 173,
build 3).

Dry run 8: a Developer removed `assert "\\n" not in line` from `_foldline`
at 67e0b2d0. The Architect judged the removal a mistake at a585c4ea, and
`touch_mistaken` woke s198 on qwen3.5:9b. s198 put the line back, not byte
for byte, and two more commits broke two inherited files. Roman,
2026-11-08 10:23: a restore of a statement the fork holds is not a model
limitation.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from rota.core import predicates as P
from rota.core.db import init_db
from rota.core.restore import restore_stray, restore_wake

PATH = "src/icalendar/parser/string.py"
GRAIN = f"{PATH}::_foldline"
FIX = Path(__file__).parent / "fixtures"
# icalendar's string.py at the fork 99619246 and at the head a585c4ea.
FORK = (FIX / "dry8_string_99619246.txt").read_bytes()
A585 = (FIX / "dry8_string_a585c4ea.txt").read_bytes()
GONE = b'    assert "\\n" not in line\n'
NOTE = 'removal: `assert "\\n" not in line` at line 129'


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t",
                           "-c", "user.email=t@t", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def run(tmp_path):
    """bg_1: the fork, a project root at the fork, a running batch."""
    root = tmp_path / "wt"
    (root / PATH).parent.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / PATH).write_bytes(FORK)
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "fork")
    proj = tmp_path / "proj"
    subprocess.run(["git", "clone", "-q", str(root), str(proj)], check=True)
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('fold','fold long lines','in_scope','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES "
                 "('bg_1','fold','running',?)", (str(root),))
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)",
                 (str(proj),))
    conn.commit()
    return conn, root


def _head(conn, root: Path, text: bytes, status: str = "mistake") -> str:
    """Commit `text` as the head and write the stray row at that head."""
    (root / PATH).write_bytes(text)
    _git(root, "commit", "-qam", "head")
    sha = _git(root, "rev-parse", "HEAD")
    conn.execute("UPDATE batches SET head_commit = ? WHERE id = 'bg_1'", (sha,))
    conn.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status, note) "
                 "VALUES ('bg_1', ?, ?, ?, ?)", (sha, GRAIN, status, NOTE))
    conn.commit()
    return sha


def test_the_mistake_row_is_restored_by_the_structure(run):
    """67e0b2d0 removed the one line. The restore puts the fork bytes back,
    commits, and closes the row, so `touch_mistaken` wakes nobody."""
    conn, root = run
    old = _head(conn, root, FORK.replace(GONE, b"", 1))
    assert [w.kind for w in P.touch_mistaken(conn)] == ["tick:touch_mistaken"]
    done, reasons = restore_wake(conn, "bg_1")
    conn.commit()
    assert reasons == [] and len(done) == 1, (done, reasons)
    assert (root / PATH).read_bytes() == FORK
    new = _git(root, "rev-parse", "HEAD")
    assert new == done[0]["restored"] != old
    assert "restore" in _git(root, "log", "-1", "--format=%s")
    assert "the Architect's judgement" in _git(root, "log", "-1", "--format=%s")
    assert conn.execute("SELECT head_commit FROM batches").fetchone()[0] == new
    row = conn.execute("SELECT status, note FROM touch_strays WHERE commit_sha = ?",
                       (old,)).fetchone()
    assert row["status"] == "restored" and new[:8] in row["note"]
    assert P.touch_mistaken(conn) == []


def test_the_replay_of_a585c4ea_restores_the_line_and_keeps_the_rest(run):
    """a585c4ea also added an escape branch in the fold. The restore puts
    the assert back in its fork place. The diff against the fork is the
    escape branch and its comments only."""
    conn, root = run
    _head(conn, root, A585)
    done, reasons = restore_wake(conn, "bg_1")
    assert reasons == [] and done, reasons
    diff = _git(root, "diff", "-U0", "HEAD~2", "HEAD", "--", PATH)
    assert "assert" not in diff, diff
    lines = (root / PATH).read_bytes().splitlines(keepends=True)
    at = lines.index(b"    assert isinstance(line, str)\n")
    assert lines[at + 1] == GONE and lines[at + 2] == b"\n"


def test_a_head_with_no_context_returns_the_reason_and_the_wake_runs(run):
    """The lines around the statement are rewritten at the head. Nothing
    changes, the row stays `mistake`, and `touch_mistaken` still wakes."""
    conn, root = run
    gone = FORK.replace(GONE, b"", 1).replace(
        b"    assert isinstance(line, str)\n", b"    line = str(line)\n", 1).replace(
        b"    folded_lines: list[str] = []\n", b"    folded_lines = []\n", 1)
    old = _head(conn, root, gone)
    done, reasons = restore_wake(conn, "bg_1")
    assert done == [] and len(reasons) == 1, reasons
    assert "context" in reasons[0]
    assert _git(root, "rev-parse", "HEAD") == old
    assert conn.execute("SELECT status FROM touch_strays").fetchone()[0] == "mistake"
    assert [w.kind for w in P.touch_mistaken(conn)] == ["tick:touch_mistaken"]


def test_a_head_without_the_file_returns_the_reason(run):
    conn, root = run
    _git(root, "rm", "-q", PATH)
    _git(root, "commit", "-qm", "gone")
    sha = _git(root, "rev-parse", "HEAD")
    conn.execute("UPDATE batches SET head_commit = ? WHERE id = 'bg_1'", (sha,))
    out = restore_stray(conn, "bg_1", GRAIN, "r_m45")
    assert "gone at the head" in out["reason"]
