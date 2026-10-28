"""Fact F4, the root-cause audit of 2026-10-27: the newest run of a test in
its batch. Night 170, W3 and W16: a door told the Developer s201 to restore
inh_fe7f4bfc, and that test passed 7 of 7 runs of b_3. Thirty-four readers
of `test_runs` kept three order rules: `rowid`, `attempt` then `rowid`, and
the newest attempt of the batch. The view `latest_runs` is the one reader
now, by `rowid`, per test and batch."""
import ast
import re
from pathlib import Path

import pytest

from rota.core import predicates, sandbox
from rota.core.db import connect_readonly, init_db
from rota.roles import api

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','a change','in_scope','approved',1,1)")
    for bid in ("b1", "b2"):
        conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                     "VALUES (?, 'i1', 'running', 'abc')", (bid,))
    conn.commit()
    return conn


def _test(db, tid, batch, criterion=None):
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES (?, ?, ?, ?, 'def test_x():\n    assert True')",
               (tid, batch, criterion, f"tests/test_{tid}.py"))


def _run(db, rid, batch, test, result, attempt=1, output=""):
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, output, attempt) VALUES (?, ?, ?, 'abc', ?, ?, ?)",
               (rid, batch, test, result, output, attempt))


def test_the_view_orders_by_insert_and_not_by_attempt(db):
    _test(db, "t1", "b1")
    _run(db, "tr1", "b1", "t1", "fail", attempt=3)
    _run(db, "tr2", "b1", "t1", "pass", attempt=1)
    _run(db, "tr3", "b2", "t1", "fail", attempt=1)
    rows = {(r["batch_id"], r["test_id"]): r["result"]
            for r in db.execute("SELECT * FROM latest_runs")}
    assert rows == {("b1", "t1"): "pass", ("b2", "t1"): "fail"}


def test_tests_failing_reads_the_newest_run_in_each_batch(db):
    # The old rule took the newest run per test across batches. A pass of
    # the inherited id in b2 hid its red in b1.
    _test(db, "inh_1", "b1")
    _run(db, "tr1", "b1", "inh_1", "fail")
    _run(db, "tr2", "b2", "inh_1", "pass")
    db.commit()
    assert "b1" in {w.refs[0] for w in predicates.tests_failing(db)}


def test_other_test_red_reads_the_newest_run_of_each_test(db):
    # The old rule read the newest attempt of the batch only. A test that
    # the newest attempt did not run kept its red, and the rule missed it.
    _test(db, "t1", "b1")
    _test(db, "t2", "b1")
    _run(db, "tr1", "b1", "t2", "fail", attempt=1)
    _run(db, "tr2", "b1", "t1", "pass", attempt=2)
    db.commit()
    assert sandbox._other_test_red(db, ["t1"]) is True


def _ctx(db, batch="b1"):
    return sandbox.build("developer", db, batch_id=batch, mode="tests_failing").ctx


def test_run_view_reads_the_tests_own_batch(db):
    # The old rule read the newest run of the id in any batch.
    _test(db, "inh_1", "b1")
    _run(db, "tr1", "b1", "inh_1", "fail", output="E   assert 1 == 2")
    _run(db, "tr2", "b2", "inh_1", "pass", output="1 passed")
    db.commit()
    assert sandbox._run_view(_ctx(db), "inh_1") == "assert 1 == 2"


def test_tests_load_reads_the_insert_order(db):
    # The old rule put `attempt` first. A run with a lower attempt and a
    # later insert is the newest run.
    _test(db, "t1", "b1")
    _run(db, "tr1", "b1", "t1", "fail", attempt=3, output="E   boom")
    _run(db, "tr2", "b1", "t1", "pass", attempt=1)
    db.commit()
    rows = api.tests_load(_ctx(db), "b1")
    assert [r["last_result"] for r in rows if r["id"] == "t1"] == ["pass"]


def test_night_170_a_green_project_test_is_broken_by_no_change(db):
    # s201's challenge on inh_fe7f4bfc met "restore what your change broke",
    # and its runs in b_3 passed 7 of 7.
    _test(db, "inh_fe7f4bfc", "b1")
    for n in range(7):
        _run(db, f"tr{n}", "b1", "inh_fe7f4bfc", "pass", attempt=n + 1)
    db.commit()
    said = sandbox.project_tests_fact(_ctx(db), ["inh_fe7f4bfc"])
    assert said is not None
    assert "inh_fe7f4bfc passed on its newest run in this batch" in said
    assert "restore" not in said and "broke nothing" in said


def test_a_read_only_file_without_the_view_gets_a_temp_view(tmp_path):
    import sqlite3
    path = tmp_path / "old.db"
    conn = init_db(path)
    conn.execute("DROP VIEW latest_runs")
    conn.commit()
    conn.close()
    ro = connect_readonly(path)
    assert ro.execute("SELECT COUNT(*) FROM latest_runs").fetchone()[0] == 0
    with pytest.raises(sqlite3.OperationalError):
        ro.execute("CREATE TEMP TABLE x (a)")


# The reads of `test_runs` that do not ask for the newest run. Each site
# carries a comment that names its reason. A new site goes red here.
ALLOWED = {
    ("rota/core/db.py", "red_before"),           # the newest run that ran code
    ("rota/core/harness.py", "run"),             # any run at the head
    ("rota/core/lifecycle.py", "next_attempt"),  # the attempt counter
    ("rota/core/sandbox.py", "_stored_runs"),    # a past commit, HEAD~1
    ("rota/roles/api.py", "_runs_at"),           # a past commit, HEAD~1
    ("rota/tools/invariants.py", "i4"),          # every run, counted
    ("rota/testkit/scenes.py", "ran"),           # the test kit
}
READ = re.compile(r"(?<!DELETE )\b(?:FROM|JOIN)\s+test_runs\b", re.I)


def _sites() -> set:
    found = set()
    for path in sorted((ROOT / "rota").rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        src = path.read_text(encoding="utf-8")
        if not READ.search(src):
            continue
        tree = ast.parse(src)
        funcs = [n for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and READ.search(node.value)):
                continue
            owner = min((f for f in funcs
                         if f.lineno <= node.lineno <= f.end_lineno),
                        key=lambda f: f.end_lineno - f.lineno, default=None)
            found.add((rel, owner.name if owner else "<module>"))
    return found


def test_latest_runs_is_the_one_reader_of_the_newest_run():
    assert _sites() == ALLOWED
