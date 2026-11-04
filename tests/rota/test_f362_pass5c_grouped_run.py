"""
Frame 362, pass 5c, section 1: `harness.run` runs the inherited group in one call.

The review of pass 5 (plans/f362-review-pass5.md, low 4): one pytest child
per file cost 263 s per run on icalendar. The project's tests now run in
one call. Each file that the call names red runs again alone, so each red
row keeps its own output. The Tester's tests run one by one, as before.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from rota.core import execute, harness
from rota.core.db import init_db

FILES = ("tests/test_a.py", "tests/test_b.py", "tests/test_c.py")


@pytest.fixture
def conn(tmp_path):
    tree = tmp_path / "tree"
    tree.mkdir()
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','ship it','in_scope','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status, worktree, head_commit) "
                 "VALUES ('b1','i1','running',?,'h1')", (str(tree),))
    for rel in FILES:
        conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                     "VALUES (?, 'b1', NULL, ?, 'def test_x():\n    pass\n')",
                     (harness.inherited_id(rel), rel))
    return conn


def _stub(monkeypatch, group_out, alone):
    """`execute.run` answers a grouped call with `group_out`, and one file
    from `alone`. The list holds the paths of each call."""
    calls: list[list[str]] = []

    def run(root, argv, **kw):
        paths = [a for a in argv if a in FILES]
        calls.append(sorted(paths))
        if len(paths) > 1:
            return SimpleNamespace(error=None, stdout=group_out[1], stderr="",
                                   returncode=group_out[0])
        code, said = alone[paths[0]]
        return SimpleNamespace(error=None, stdout=said, stderr="", returncode=code)

    monkeypatch.setattr(execute, "run", run)
    return calls


def _rows(conn):
    return {r["path"]: (r["result"], r["output"]) for r in conn.execute(
        "SELECT t.path, r.result, r.output FROM test_runs r "
        "JOIN tests t ON t.id = r.test_id WHERE r.batch_id = 'b1'")}


def test_one_red_file_makes_two_calls_and_keeps_its_own_output(conn, monkeypatch):
    summary = ("PASSED tests/test_a.py::test_x\n"
               "FAILED tests/test_b.py::test_x - assert 1 == 2\n"
               "PASSED tests/test_c.py::test_x\n1 failed, 2 passed\n")
    calls = _stub(monkeypatch, (harness.EXIT_FAILED, summary),
                  {"tests/test_b.py": (harness.EXIT_FAILED, "E   assert 1 == 2")})
    harness.run(conn, "b1")
    assert calls == [list(FILES), ["tests/test_b.py"]]
    rows = _rows(conn)
    assert [rows[f][0] for f in FILES] == ["pass", "fail", "pass"]
    assert "E   assert 1 == 2" in rows["tests/test_b.py"][1]


def test_a_green_group_makes_one_call(conn, monkeypatch):
    summary = "".join(f"PASSED {f}::test_x\n" for f in FILES)
    calls = _stub(monkeypatch, (harness.EXIT_OK, summary), {})
    harness.run(conn, "b1")
    assert calls == [list(FILES)]
    assert {r for r, _ in _rows(conn).values()} == {"pass"}


def test_a_collection_error_leaves_the_others_green(conn, monkeypatch):
    summary = ("PASSED tests/test_a.py::test_x\n"
               "ERROR tests/test_c.py - ImportError: no module\n"
               "PASSED tests/test_b.py::test_x\n1 passed, 1 error\n")
    calls = _stub(monkeypatch, (harness.EXIT_FAILED, summary),
                  {"tests/test_c.py": (2, "E   ImportError: no module")})
    harness.run(conn, "b1")
    assert calls == [list(FILES), ["tests/test_c.py"]]
    rows = _rows(conn)
    assert [rows[f][0] for f in FILES] == ["pass", "pass", "error"]


def test_a_file_the_summary_does_not_name_runs_alone(conn, monkeypatch):
    # A file with no test gives `error` alone, and the grouped call is silent
    # about it, so the call cannot give it a pass.
    summary = "PASSED tests/test_a.py::test_x\nPASSED tests/test_b.py::test_x\n"
    calls = _stub(monkeypatch, (harness.EXIT_OK, summary),
                  {"tests/test_c.py": (5, "no tests ran")})
    harness.run(conn, "b1")
    assert calls == [list(FILES), ["tests/test_c.py"]]
    assert _rows(conn)["tests/test_c.py"][0] == "error"


def test_the_tester_tests_run_one_by_one(conn, monkeypatch):
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i2','x','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i2','x')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c1','t1','x')")
    conn.execute("UPDATE tests SET criterion_id = 'c1' WHERE path != ?", (FILES[0],))
    calls = _stub(monkeypatch, (harness.EXIT_OK, ""),
                  {f: (harness.EXIT_OK, "1 passed") for f in FILES})
    harness.run(conn, "b1")
    assert sorted(calls) == [[f] for f in FILES]
