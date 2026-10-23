"""
Every harness run leaves a row in `test_run_journal`.

`test_runs` holds the live run per test. Two deletes keep it so: a new run
at one commit replaces the run before it (`harness.py`), and a re-encoded
body removes the runs of the old body (`db.py`). On night 159 the log
printed 987 results in 27 runs, and the table held 287 (frame 307, section
c). The journal keeps each run, and the night report counts both tables.
"""
from __future__ import annotations

import sqlite3

from rota.core import harness, lifecycle
from rota.core.db import Write, _lift_quarantines, init_db
from rota.tools import nightreport

HEAD = "c" * 40
BODY = "def test_ok():\n    assert True\n"


def _db(tmp_path, worktree=None):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('i1','ship it','in_scope','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit, worktree) "
                 "VALUES ('b1','i1','running',?,?)",
                 (HEAD, str(worktree) if worktree else None))
    conn.execute("INSERT INTO tests (id, batch_id, path, body) "
                 "VALUES ('tst1','b1','tests/test_ok.py',?)", (BODY,))
    conn.commit()
    return conn


def _count(conn, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table} WHERE test_id = 'tst1'").fetchone()[0]


def test_two_runs_at_one_commit_leave_one_live_row_and_two_journal_rows(tmp_path):
    wt = tmp_path / "wt"
    wt.mkdir()
    conn = _db(tmp_path, wt)
    assert harness.run(conn, "b1") == [("tst1", "pass")]
    assert harness.run(conn, "b1") == [("tst1", "pass")]
    assert _count(conn, "test_runs") == 1
    assert _count(conn, "test_run_journal") == 2
    attempts = [r[0] for r in conn.execute(
        "SELECT attempt FROM test_run_journal ORDER BY seq")]
    assert attempts == [1, 2]


def test_a_re_encode_removes_the_live_run_and_keeps_the_journal_row(tmp_path):
    conn = _db(tmp_path)
    lifecycle.record_test_run(conn, "tr_1", "b1", "tst1", "fail", 1,
                              commit_sha=HEAD, output="E  assert 0")
    _lift_quarantines(conn, Write(table="tests", row_id="tst1",
                                  values={"body": BODY + "# new\n"}), moved=True)
    assert _count(conn, "test_runs") == 0
    row = conn.execute("SELECT id, result, commit_sha, output, recorded_at "
                       "FROM test_run_journal WHERE test_id = 'tst1'").fetchall()
    assert len(row) == 1
    assert (row[0]["id"], row[0]["result"], row[0]["commit_sha"]) == ("tr_1", "fail", HEAD)
    assert row[0]["output"] == "E  assert 0" and row[0]["recorded_at"]


def _report(path) -> list[str]:
    conn = nightreport.open_ro(path)
    try:
        lines = nightreport.build(conn)
    finally:
        conn.close()
    start = lines.index("== test runs")
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("== "))
    return lines[start + 1:end]


def test_the_night_report_prints_the_live_and_the_journal_counts(tmp_path):
    conn = _db(tmp_path)
    lifecycle.record_test_run(conn, "tr_1", "b1", "tst1", "fail", 1, commit_sha=HEAD)
    conn.execute("DELETE FROM test_runs WHERE batch_id = 'b1'")
    lifecycle.record_test_run(conn, "tr_2", "b1", "tst1", "pass", 2, commit_sha=HEAD)
    conn.commit()
    conn.close()
    section = _report(tmp_path / "rota.db")
    assert f"b1 {HEAD[:10]} head runs=1 journal=2 not_pass=0 journal_not_pass=1" in section


def test_the_night_report_prints_journal_absent_on_an_old_database(tmp_path):
    conn = _db(tmp_path)
    lifecycle.record_test_run(conn, "tr_1", "b1", "tst1", "fail", 1, commit_sha=HEAD)
    conn.commit()
    conn.close()
    raw = sqlite3.connect(tmp_path / "rota.db")
    raw.execute("DROP TABLE test_run_journal")
    raw.commit()
    raw.close()
    section = _report(tmp_path / "rota.db")
    assert "absent: test_run_journal" in section
    assert (f"b1 {HEAD[:10]} head runs=1 journal=absent not_pass=1 "
            f"journal_not_pass=absent") in section
