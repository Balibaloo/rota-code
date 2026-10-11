"""
Frame 203: a test's database and repositories are copies of templates built
once per process. A copy must give a test what the old build gave it.
"""
from __future__ import annotations

import sqlite3
import subprocess

from rota.core import db as rota_db
from rota.core.worktrees import GIT
from rota.testkit import dbtemplate
from rota.testkit.gitfixture import copy_template
from tests.rota.test_findings_doors import _night_repos
from tests.rota.test_verdict_lines import _s279_repo


def _shape(conn: sqlite3.Connection) -> dict:
    """The schema text, the user version and each table's row count."""
    sql = sorted((r[0], r[1], r[2]) for r in conn.execute(
        "SELECT type, name, COALESCE(sql, '') FROM sqlite_master"))
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")]
    rows = {t: conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            for t in tables}
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    return {"sql": sql, "rows": rows, "version": version}


def test_conftest_binds_the_wrapper():
    assert rota_db.init_db is dbtemplate.init_db


def test_a_copied_database_equals_a_fresh_one(tmp_path):
    fresh = dbtemplate._REAL(tmp_path / "fresh.db")
    copied = dbtemplate.init_db(tmp_path / "copied.db")
    try:
        assert _shape(copied) == _shape(fresh)
        assert _shape(fresh)["rows"]["config"] > 0
        # An empty `-wal` file reads as a text file to the indexer.
        assert (tmp_path / "copied.db-wal").stat().st_size > 0
    finally:
        fresh.close()
        copied.close()


def test_an_existing_file_goes_to_the_real_init_db(tmp_path):
    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE mine (x)")
    conn.execute("INSERT INTO mine VALUES (1)")
    conn.commit()
    conn.close()
    opened = dbtemplate.init_db(path)
    try:
        assert opened.execute("SELECT x FROM mine").fetchall()[0][0] == 1
        assert opened.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0
    finally:
        opened.close()


def test_a_schema_change_rebuilds_the_template(tmp_path, monkeypatch):
    before = dbtemplate.template_path()
    schema = tmp_path / "schema.sql"
    schema.write_bytes(rota_db.SCHEMA_PATH.read_bytes()
                       + b"\nCREATE TABLE IF NOT EXISTS frame203 (x);\n")
    monkeypatch.setattr(rota_db, "SCHEMA_PATH", schema)
    after = dbtemplate.template_path()
    assert after != before
    conn = dbtemplate.init_db(tmp_path / "new.db")
    try:
        names = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")}
        assert "frame203" in names
    finally:
        conn.close()
    monkeypatch.undo()
    assert dbtemplate.template_path() == before


def _git(path, *args) -> str:
    return subprocess.run([*GIT, "-C", str(path), *args], check=True,
                          capture_output=True, text=True).stdout


def _history(repo) -> tuple[str, str, str]:
    return (_git(repo, "log", "--format=%H %s"),
            _git(repo, "rev-parse", "HEAD").strip(),
            _git(repo, "status", "--porcelain"))


def test_a_copied_repository_has_the_built_commits(tmp_path):
    built = tmp_path / "built"
    built.mkdir()
    head = _s279_repo(built)
    copied = tmp_path / "copied"
    assert copy_template("s279", _s279_repo, copied) == head
    assert _history(copied / "repo") == _history(built / "repo")
    assert _history(copied / "repo")[2] == ""


def test_a_copied_worktree_points_at_its_copy(tmp_path):
    built = tmp_path / "built"
    built.mkdir()
    changed = ["src/click/termui.py"]
    head = _night_repos(built, "bg_2", changed)
    copied = tmp_path / "copied"
    got = copy_template(("a_night", "bg_2", tuple(changed)),
                        lambda base: _night_repos(base, "bg_2", changed), copied)
    assert got == head
    tree = copied / "batch"
    assert _history(tree) == _history(built / "batch")
    assert _history(copied / "root") == _history(built / "root")
    listed = _git(copied / "root", "worktree", "list", "--porcelain")
    assert tree.as_posix() in listed
    assert "built" not in listed and "rota_template_" not in listed
    top = _git(tree, "rev-parse", "--show-toplevel").strip()
    assert top == tree.as_posix()
