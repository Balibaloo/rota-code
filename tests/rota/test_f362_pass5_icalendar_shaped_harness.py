"""
Frame 362, pass 5: the harness on a tree shaped like icalendar.

Dry run 5's `b_1` inherited one test, `.github/workflows/test_generate_matrix.py`.
The judge ruled `src` as `program`, and that ruling covered
`src/icalendar/tests`, so `harness.project_tests` skipped every file in the
package's own test folder (plans/f362-dry5-walls-read.md, section 3).
"""
from __future__ import annotations

from types import SimpleNamespace

from rota.core import execute, harness
from rota.core.db import init_db
from rota.roles import api
from rota.testkit.fixtures import seed_provenance

TREE = {
    "src/pkg/__init__.py": "",
    "src/pkg/mod.py": "def f():\n    return 1\n",
    "src/pkg/tests/__init__.py": "",
    "src/pkg/tests/test_mod.py": "def test_f():\n    assert True\n",
    ".github/workflows/test_matrix.py": "def test_m():\n    assert True\n",
}
TESTS = [".github/workflows/test_matrix.py", "src/pkg/tests/test_mod.py"]


def _setup(tmp_path, monkeypatch):
    tree = tmp_path / "tree"
    for rel, body in TREE.items():
        (tree / rel).parent.mkdir(parents=True, exist_ok=True)
        (tree / rel).write_text(body, encoding="utf-8")
    conn = init_db(tmp_path / "rota.db")
    for rel in TREE:
        conn.execute("INSERT INTO code_index (grain, grain_kind) "
                     "VALUES (?, 'path')", (rel,))
    for prefix, kind in (("src", "program"), (".github", "attached")):
        conn.execute("INSERT INTO frame_rulings (id, kind) VALUES (?, ?)",
                     (prefix, kind))
        seed_provenance(conn, "frame_rulings", prefix, "observed")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','ship it','in_scope','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status, worktree) "
                 "VALUES ('b1','i1','running',?)", (str(tree),))
    conn.commit()
    # The base run would start pytest. A green stub keeps the test fast.
    monkeypatch.setattr(execute, "run", lambda *a, **k: SimpleNamespace(
        error=None, returncode=harness.EXIT_OK, stdout="", stderr=""))
    return conn, tree


def test_project_tests_lists_the_package_test_folder(tmp_path, monkeypatch):
    conn, tree = _setup(tmp_path, monkeypatch)
    assert harness.project_tests(conn, tree) == TESTS


def test_inherit_writes_a_row_per_test_file(tmp_path, monkeypatch):
    conn, tree = _setup(tmp_path, monkeypatch)
    assert sorted(harness.inherit(conn, "b1", tree)) == TESTS
    rows = conn.execute("SELECT id FROM tests WHERE batch_id = 'b1' "
                        "AND id LIKE 'inh_%'").fetchall()
    assert len(rows) == 2


def test_the_program_modules_hold_no_test_folder(tmp_path, monkeypatch):
    conn, _ = _setup(tmp_path, monkeypatch)
    assert "tests" not in api._program_modules(conn)
    assert "pkg" in api._program_modules(conn)
