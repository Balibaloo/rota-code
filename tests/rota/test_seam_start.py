"""probes/seam_start.py: the seam door and the restore."""
import importlib.util
import sqlite3
import subprocess
from pathlib import Path

from rota import paths
from rota.core.db import init_db
from rota.core.worktrees import GIT, WorktreeError

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


def _commit(path: Path, name: str) -> str:
    (path / name).write_bytes(b"a\n")
    _git(path, "add", name)
    _git(path, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", name)
    return _git(path, "rev-parse", "HEAD")


def _repo(path: Path, commit: bool = True) -> str:
    path.mkdir()
    _git(path, "init", "-q")
    return _commit(path, "a.txt") if commit else ""


def _batch(conn, bid: str, sha, status: str) -> None:
    conn.execute("INSERT INTO batches (id, item_id, worktree, head_commit, status, port_base, version) "
                 "VALUES (?, 'x', ?, ?, ?, 41000, 1)",
                 (bid, f"C:/elsewhere/.rota/worktrees/{bid}", sha, status))


def _snapshot(tmp_path: Path, sha: str) -> Path:
    db = tmp_path / "snap.db"
    conn = init_db(db)
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', 'C:/elsewhere')")
    conn.execute("INSERT INTO items (id, text, kind) VALUES ('x', 'an item', 'in_scope')")
    _batch(conn, "bg_1", sha, "running")
    # The old night's process, so the empty-after check reads a delete.
    conn.execute("INSERT INTO runtime_processes (pid, batch_id, command) VALUES (4242, 'bg_1', 'serve')")
    conn.commit()
    conn.close()
    return db


def _old_run(tmp_path: Path) -> bytes:
    """The last night's run database, which a refusal must leave as it was."""
    runs = tmp_path / "runs"
    runs.mkdir()
    conn = sqlite3.connect(runs / "clickI.db")
    conn.execute("CREATE TABLE old (night TEXT)")
    conn.execute("INSERT INTO old VALUES ('the last night')")
    conn.commit()
    conn.close()
    return (runs / "clickI.db").read_bytes()


def _setup(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    sha = _repo(repo)
    db = _snapshot(tmp_path, sha)
    old = _old_run(tmp_path)
    monkeypatch.setenv("ROTA_RUNS", str(tmp_path / "runs"))
    return repo, sha, db, old


def _unchanged(tmp_path: Path, repo: Path, old: bytes, branches: str = "", home: bool = False) -> None:
    assert (tmp_path / "runs" / "clickI.db").read_bytes() == old
    assert not list((tmp_path / "runs").glob("*.seam-old*"))
    assert _git(repo, "branch", "--list", "batch/*") == branches
    assert (repo / ".rota" / "worktrees").exists() == home


def _with_bg_2(db: Path, sha) -> None:
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys = ON")
    _batch(conn, "bg_2", sha, "deferred")
    conn.commit()
    conn.close()


def test_a_snapshot_behind_the_schema_mark_is_refused(tmp_path, monkeypatch, capsys):
    repo, sha, db, old = _setup(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    conn.execute("DELETE FROM config WHERE key = 'schema'")
    conn.commit()
    conn.close()
    assert _mod().restore("clickI", db, sha, repo, env=False) == 1
    assert "SEAM REFUSED" in capsys.readouterr().out
    _unchanged(tmp_path, repo, old)


def test_a_snapshot_with_the_provenance_column_is_refused(tmp_path, monkeypatch, capsys):
    repo, sha, db, old = _setup(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    conn.execute("ALTER TABLE items ADD COLUMN provenance TEXT")
    conn.commit()
    conn.close()
    assert _mod().restore("clickI", db, sha, repo, env=False) == 1
    assert "SEAM REFUSED" in capsys.readouterr().out
    _unchanged(tmp_path, repo, old)


def test_a_commit_no_batch_heads_at_is_refused(tmp_path, monkeypatch, capsys):
    repo, sha, db, old = _setup(tmp_path, monkeypatch)
    assert _mod().restore("clickI", db, "0123456789abcdef", repo, env=False) == 1
    out = capsys.readouterr().out
    assert "SEAM REFUSED: no running or deferred batch heads at" in out and "bg_1@" in out
    _unchanged(tmp_path, repo, old)


def test_a_head_not_in_the_checkout_is_refused(tmp_path, monkeypatch, capsys):
    repo, sha, db, old = _setup(tmp_path, monkeypatch)
    empty = tmp_path / "empty"
    _repo(empty, commit=False)
    assert _mod().restore("clickI", db, sha[:8], empty, env=False) == 1
    assert "is not a commit in" in capsys.readouterr().out
    _unchanged(tmp_path, empty, old)
    _unchanged(tmp_path, repo, old)


def test_a_branch_a_worktree_holds_is_refused(tmp_path, monkeypatch, capsys):
    repo, sha, db, old = _setup(tmp_path, monkeypatch)
    _git(repo, "worktree", "add", "-q", "-b", "batch/bg_1", str(tmp_path / "held"), sha)
    assert _mod().restore("clickI", db, sha, repo, env=False) == 1
    assert "batch/bg_1 is checked out" in capsys.readouterr().out
    _unchanged(tmp_path, repo, old, branches="+ batch/bg_1")


def test_a_worktree_path_that_exists_is_refused(tmp_path, monkeypatch, capsys):
    repo, sha, db, old = _setup(tmp_path, monkeypatch)
    (repo / ".rota" / "worktrees" / "bg_1").mkdir(parents=True)
    assert _mod().restore("clickI", db, sha, repo, env=False) == 1
    assert "exists already" in capsys.readouterr().out
    _unchanged(tmp_path, repo, old, home=True)
    assert [p.name for p in (repo / ".rota" / "worktrees").iterdir()] == ["bg_1"]


def test_a_run_database_held_open_is_refused(tmp_path, monkeypatch, capsys):
    repo, sha, db, old = _setup(tmp_path, monkeypatch)
    held = sqlite3.connect(tmp_path / "runs" / "clickI.db", isolation_level=None)
    held.execute("BEGIN IMMEDIATE")
    try:
        assert _mod().restore("clickI", db, sha, repo, env=False) == 1
    finally:
        held.execute("ROLLBACK")
        held.close()
    assert "SEAM REFUSED: clickI.db is held open" in capsys.readouterr().out
    _unchanged(tmp_path, repo, old)


def test_a_failed_add_removes_what_the_restore_added(tmp_path, monkeypatch, capsys):
    repo, sha, db, old = _setup(tmp_path, monkeypatch)
    runs = tmp_path / "runs"
    (runs / "clickI.db-wal").write_bytes(b"old wal")
    (runs / "clickI.db-shm").write_bytes(b"old shm")
    _with_bg_2(db, sha)
    mod = _mod()
    real = mod._add

    def add(root, home, bid, head):
        if bid == "bg_2":
            raise WorktreeError("git worktree add batch/bg_2: refused by the test")
        real(root, home, bid, head)

    monkeypatch.setattr(mod, "_add", add)
    assert mod.restore("clickI", db, sha, repo, env=False) == 1
    assert "SEAM REFUSED: git worktree add batch/bg_2" in capsys.readouterr().out
    _unchanged(tmp_path, repo, old)
    assert (runs / "clickI.db-wal").read_bytes() == b"old wal"
    assert (runs / "clickI.db-shm").read_bytes() == b"old shm"
    assert "bg_1" not in _git(repo, "worktree", "list")


def test_a_failed_reopen_puts_the_old_database_back(tmp_path, monkeypatch, capsys):
    """Pass 4 of frame 104: a connection that `init_db` left open in the
    traceback held the new file, and the old one stayed at `.seam-old`."""
    import pytest
    from rota.core import db as rota_db
    repo, sha, db, old = _setup(tmp_path, monkeypatch)

    def broken(path):
        rota_db.connect(path)
        raise sqlite3.OperationalError("broken by the test")

    monkeypatch.setattr(rota_db, "init_db", broken)
    with pytest.raises(sqlite3.OperationalError, match="broken by the test"):
        _mod().restore("clickI", db, sha, repo, env=False)
    _unchanged(tmp_path, repo, old)
    assert [p.name for p in (tmp_path / "runs").iterdir()] == ["clickI.db"]


def test_a_commit_only_the_tip_matches_is_refused(tmp_path, monkeypatch, capsys):
    """A batch with no head comes back at the tip. The tip still never
    opens the door."""
    repo, sha1, db, old = _setup(tmp_path, monkeypatch)
    tip = _commit(repo, "b.txt")
    _with_bg_2(db, None)
    assert _mod().restore("clickI", db, tip, repo, env=False) == 1
    assert "SEAM REFUSED: no running or deferred batch heads at" in capsys.readouterr().out
    _unchanged(tmp_path, repo, old)


def test_the_restore_rebuilds_the_batch_at_its_head(tmp_path, monkeypatch, capsys):
    repo, sha, db, _ = _setup(tmp_path, monkeypatch)
    mod = _mod()
    assert mod.pair(db) == 0
    assert f"bg_1 running {sha}" in capsys.readouterr().out
    assert mod.restore("clickI", db, sha[:8], repo, env=False) == 0, capsys.readouterr().out
    assert "SEAM: clickI at" in capsys.readouterr().out
    target = tmp_path / "runs" / "clickI.db"
    assert target.exists()
    assert not list((tmp_path / "runs").glob("*.seam-old*"))
    conn = sqlite3.connect(target)
    root = conn.execute("SELECT value FROM config WHERE key = 'project_root'").fetchone()[0]
    assert Path(root) == repo
    wt = Path(conn.execute("SELECT worktree FROM batches WHERE id = 'bg_1'").fetchone()[0])
    assert wt == repo / ".rota" / "worktrees" / "bg_1"
    assert conn.execute("SELECT COUNT(*) FROM runtime_processes").fetchone()[0] == 0
    conn.close()
    assert _git(wt, "rev-parse", "HEAD") == sha
    assert _git(repo, "branch", "--list", "batch/bg_1")


def test_every_live_batch_comes_back_at_its_own_head(tmp_path, monkeypatch, capsys):
    repo, sha1, db, _ = _setup(tmp_path, monkeypatch)
    sha2 = _commit(repo, "b.txt")
    _with_bg_2(db, sha2)
    assert _mod().restore("clickI", db, sha2, repo, env=False) == 0, capsys.readouterr().out
    assert "2 batch(es) restored" in capsys.readouterr().out
    conn = sqlite3.connect(tmp_path / "runs" / "clickI.db")
    for bid, sha in (("bg_1", sha1), ("bg_2", sha2)):
        wt = Path(conn.execute("SELECT worktree FROM batches WHERE id = ?", (bid,)).fetchone()[0])
        assert wt == repo / ".rota" / "worktrees" / bid
        assert _git(wt, "rev-parse", "HEAD") == sha
        assert _git(repo, "rev-parse", f"batch/{bid}") == sha
    conn.close()


def test_a_batch_with_no_head_comes_back_at_the_checkout_head(tmp_path, monkeypatch, capsys):
    repo, sha1, db, _ = _setup(tmp_path, monkeypatch)
    tip = _commit(repo, "b.txt")
    _with_bg_2(db, None)
    assert _mod().restore("clickI", db, sha1, repo, env=False) == 0, capsys.readouterr().out
    assert "bg_2@HEAD" in capsys.readouterr().out
    assert _git(repo / ".rota" / "worktrees" / "bg_2", "rev-parse", "HEAD") == tip
    assert _git(repo / ".rota" / "worktrees" / "bg_1", "rev-parse", "HEAD") == sha1
    conn = sqlite3.connect(tmp_path / "runs" / "clickI.db")
    assert conn.execute("SELECT head_commit FROM batches WHERE id = 'bg_2'").fetchone()[0] is None
    conn.close()


def test_the_restore_adds_the_columns_init_db_adds_in_place(tmp_path, monkeypatch, capsys):
    """Night 103 run 1 (2026-10-01): the restored snapshot had the schema
    mark and no `verdicts.reason`, and the first Critic session failed."""
    repo, sha, db, _ = _setup(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    conn.execute("ALTER TABLE verdicts DROP COLUMN reason")
    conn.commit()
    conn.close()
    assert _mod().restore("clickI", db, sha, repo, env=False) == 0, capsys.readouterr().out
    conn = sqlite3.connect(tmp_path / "runs" / "clickI.db")
    columns = {r[1] for r in conn.execute("PRAGMA table_info(verdicts)")}
    conn.close()
    assert "reason" in columns


def test_the_env_step_records_the_note_and_writes_the_tests(tmp_path, monkeypatch, capsys):
    repo, sha, db, _ = _setup(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    conn.execute("INSERT INTO tests (id, batch_id, path, body) "
                 "VALUES ('t_1', 'bg_1', 'tests/test_seam.py', 'def test_x():\n    pass\n')")
    conn.commit()
    conn.close()
    from rota.core import provision
    monkeypatch.setattr(provision, "ensure_env", lambda path: (None, "stub"))
    assert _mod().restore("clickI", db, sha, repo, env=True) == 0, capsys.readouterr().out
    assert "env: stub; tests: 1" in capsys.readouterr().out
    conn = sqlite3.connect(tmp_path / "runs" / "clickI.db")
    note = conn.execute("SELECT value FROM config WHERE key = 'env:bg_1'").fetchone()[0]
    conn.close()
    assert note == "stub"
    written = repo / ".rota" / "worktrees" / "bg_1" / "tests" / "test_seam.py"
    assert written.read_text(encoding="utf-8") == "def test_x():\n    pass\n"
