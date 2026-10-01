"""probes/seam_start.py: the seam door and the restore."""
import importlib.util
import sqlite3
import subprocess
from pathlib import Path

from rota import paths
from rota.core.db import init_db
from rota.core.worktrees import GIT

SEAM = paths.REPO / "probes" / "seam_start.py"


def _mod():
    spec = importlib.util.spec_from_file_location("seam_start", SEAM)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(root: Path, *args: str) -> str:
    out = subprocess.run([*GIT, "-C", str(root), *args], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    return out.stdout.strip()


def _repo(path: Path, commit: bool = True) -> str:
    path.mkdir()
    _git(path, "init", "-q")
    if not commit:
        return ""
    (path / "a.txt").write_bytes(b"a\n")
    _git(path, "add", "a.txt")
    _git(path, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "one")
    return _git(path, "rev-parse", "HEAD")


def _snapshot(tmp_path: Path, sha: str) -> Path:
    db = tmp_path / "snap.db"
    conn = init_db(db)
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', 'C:/elsewhere')")
    conn.execute("INSERT INTO items (id, text, kind) VALUES ('x', 'an item', 'in_scope')")
    conn.execute("INSERT INTO batches (id, item_id, worktree, head_commit, status, port_base, version) "
                 "VALUES ('bg_1', 'x', 'C:/elsewhere/.rota/worktrees/bg_1', ?, 'running', 41000, 1)",
                 (sha,))
    conn.commit()
    conn.close()
    return db


def _setup(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    sha = _repo(repo)
    db = _snapshot(tmp_path, sha)
    monkeypatch.setenv("ROTA_RUNS", str(tmp_path / "runs"))
    return repo, sha, db


def test_a_snapshot_behind_the_schema_mark_is_refused(tmp_path, monkeypatch, capsys):
    repo, sha, db = _setup(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    conn.execute("DELETE FROM config WHERE key = 'schema'")
    conn.commit()
    conn.close()
    assert _mod().restore("clickI", db, sha, repo, env=False) == 1
    assert "SEAM REFUSED" in capsys.readouterr().out
    assert not (tmp_path / "runs" / "clickI.db").exists()


def test_a_commit_no_batch_heads_at_is_refused(tmp_path, monkeypatch, capsys):
    repo, sha, db = _setup(tmp_path, monkeypatch)
    assert _mod().restore("clickI", db, "0123456789abcdef", repo, env=False) == 1
    out = capsys.readouterr().out
    assert "SEAM REFUSED: no running or deferred batch heads at" in out and "bg_1@" in out
    assert not (tmp_path / "runs" / "clickI.db").exists()


def test_a_head_not_in_the_checkout_is_refused(tmp_path, monkeypatch, capsys):
    _, sha, db = _setup(tmp_path, monkeypatch)
    empty = tmp_path / "empty"
    _repo(empty, commit=False)
    assert _mod().restore("clickI", db, sha[:8], empty, env=False) == 1
    assert "is not a commit in" in capsys.readouterr().out
    assert not (tmp_path / "runs" / "clickI.db").exists()


def test_the_restore_rebuilds_the_batch_at_its_head(tmp_path, monkeypatch, capsys):
    repo, sha, db = _setup(tmp_path, monkeypatch)
    mod = _mod()
    assert mod.pair(db) == 0
    assert f"bg_1 running {sha}" in capsys.readouterr().out
    assert mod.restore("clickI", db, sha[:8], repo, env=False) == 0, capsys.readouterr().out
    assert "SEAM: clickI at" in capsys.readouterr().out
    target = tmp_path / "runs" / "clickI.db"
    assert target.exists()
    conn = sqlite3.connect(target)
    root = conn.execute("SELECT value FROM config WHERE key = 'project_root'").fetchone()[0]
    assert Path(root) == repo
    wt = Path(conn.execute("SELECT worktree FROM batches WHERE id = 'bg_1'").fetchone()[0])
    assert wt == repo / ".rota" / "worktrees" / "bg_1"
    assert conn.execute("SELECT COUNT(*) FROM runtime_processes").fetchone()[0] == 0
    conn.close()
    assert _git(wt, "rev-parse", "HEAD") == sha
    assert _git(repo, "branch", "--list", "batch/bg_1")
