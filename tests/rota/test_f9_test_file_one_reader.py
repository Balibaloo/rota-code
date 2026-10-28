"""
F9, the program partition of a path: every door asks `_is_test_file`, which
reads the basename shape through `_test_shaped` and the partition through
`areas.kind_of` (plans/rootfix-audit-2026-10-27-a.md, F9).

Roman ruled on 2026-10-26 20:37, frame 324: "the basename gives the shape of
a test file, and the frame's kind says whether the file is part of the
program". Before this fix, four sites read the partition by a path rule:
`_is_test_path`, the Developer's test-file rule in `_code_write`,
`push_working_set` by a `tests/` prefix and `harness.inherit` by globs.
"""
from __future__ import annotations

import re
from pathlib import Path

from rota.core import harness
from rota.core.db import init_db
from rota.core.runner import _index_test_files
from rota.roles import api

PACKAGE = Path(__file__).resolve().parents[2] / "rota"


def _conn(tmp_path, *rulings):
    conn = init_db(tmp_path / "rota.db")
    for prefix, kind in rulings:
        conn.execute("INSERT INTO frame_rulings (id, kind) VALUES (?, ?)",
                     (prefix, kind))
    conn.commit()
    return conn


def test_a_test_shaped_program_file_is_not_a_test_file(tmp_path):
    # The old rule said test by the `test_` prefix. The frame says program.
    conn = _conn(tmp_path, ("src", "program"))
    assert not api._is_test_file(conn, "src/pkg/test_utils.py")
    assert api._is_test_file(conn, "tests/test_utils.py")


def test_a_helper_under_tests_is_not_a_test_file(tmp_path):
    # The old rule said test for any file under `tests/`. The basename has
    # no test shape.
    conn = _conn(tmp_path)
    assert not api._is_test_file(conn, "tests/helpers.py")
    assert not api._is_test_file(conn, "tests/__init__.py")


def test_the_pushed_test_files_follow_the_partition(tmp_path):
    conn = _conn(tmp_path, ("tests", "attached"), ("testing", "attached"))
    for g in ("tests/helpers.py", "tests/test_a.py", "testing/test_b.py",
              "src/pkg/core.py"):
        conn.execute("INSERT INTO code_index (grain, grain_kind) "
                     "VALUES (?, 'path')", (g,))
    conn.commit()
    # The old `LIKE 'tests/%'` gave the helper and missed `testing/`.
    assert _index_test_files(conn) == ["testing/test_b.py", "tests/test_a.py"]


def test_inherit_finds_a_test_file_outside_a_tests_folder(tmp_path):
    tree = tmp_path / "tree"
    for rel in ("tests/test_a.py", "src/pkg/tests/test_b.py",
                "tests/helpers.py", ".venv/lib/test_c.py"):
        (tree / rel).parent.mkdir(parents=True, exist_ok=True)
        (tree / rel).write_text("def test_x():\n    pass\n", encoding="utf-8")
    conn = _conn(tmp_path)
    # The old globs missed `src/pkg/tests/test_b.py`.
    assert harness.project_tests(conn, tree) == [
        "src/pkg/tests/test_b.py", "tests/test_a.py"]


# The old rules by their source form. Only `onboarding/areas.py` keeps a path
# rule, because its heuristic is the fallback of `kind_of`.
OLD_RULES = (
    r"def _is_test_path\b",
    r"startswith\(\"tests/\"\)",
    r"LIKE 'tests/%'",
    r"\"tests/\*\*/",
    r"\"tests\" in \w+\.parts",
    r"\.name\.startswith\(\"test_\"\)",
)
SCOPE = ("core", "roles", "onboarding")
ALLOWED = {"onboarding/areas.py"}


def test_a_conftest_is_a_test_file_and_is_not_inherited(tmp_path):
    # Review pass 1, finding 2: pytest defines the conftest basename.
    conn = _conn(tmp_path)
    assert api._is_test_file(conn, "tests/conftest.py")
    tree = tmp_path / "tree"
    (tree / "tests").mkdir(parents=True)
    for name in ("conftest.py", "test_a.py"):
        (tree / "tests" / name).write_text("x = 1\n", encoding="utf-8")
    assert harness.project_tests(conn, tree) == ["tests/test_a.py"]


# `areas.is_test` reads test code, a test folder's helpers included. Only the
# two surface doors ask it, and each says why in a comment (finding 5).
IS_TEST_DOORS = {"_named_callables", "_vet_surface"}


def test_only_the_surface_doors_ask_is_test():
    import ast

    tree = ast.parse((PACKAGE / "roles" / "api.py").read_text(encoding="utf-8"))
    askers = {fn.name for fn in ast.walk(tree)
              if isinstance(fn, ast.FunctionDef)
              for n in ast.walk(fn)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
              and n.func.id == "is_test"}
    assert askers == IS_TEST_DOORS


def test_no_door_reads_the_test_partition_by_a_path_rule():
    found = []
    for part in SCOPE:
        for f in sorted((PACKAGE / part).rglob("*.py")):
            rel = f.relative_to(PACKAGE).as_posix()
            if rel in ALLOWED:
                continue
            for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if any(re.search(p, line) for p in OLD_RULES):
                    found.append(f"{rel}:{n}")
    assert found == [], found
