"""
F11, the path form of a file a seat names: every path-half split of a grain
calls `_grain_path` (plans/rootfix-audit-2026-10-27-a.md, F11).

Rule C76 builds a fix at its reach. Before this fix, 18 functions took the
path half of a grain by their own `split("::")` at 36 sites. Some of them
kept a leading `./` that no index row holds. The one reader folds the backslash,
the space and the `./` and `/` prefixes.
"""
from __future__ import annotations

import ast
from pathlib import Path

from rota.core.db import init_db
from rota.onboarding import areas

PACKAGE = Path(__file__).resolve().parents[2] / "rota"

# The functions that may still split `::` and keep the path half by their own
# rule, with the reason for each.
ALLOWED = {
    # The reader itself.
    ("roles/api.py", "_grain_path"),
    # A pytest node id, not a grain.
    ("tools/gate.py", "of_the_suite"),
    # Residue: one split gives both halves of an index row. The indexer
    # writes the row in the folded form already.
    ("roles/api.py", "_callable_source"),
    ("roles/api.py", "_named_callables"),
    ("roles/api.py", "_vet_surface"),
    ("roles/api.py", "_refuse_unindexed_files"),
    ("roles/principal.py", "_removal_words"),
    # The head half goes through the reader on the next line.
    ("roles/api.py", "_fold"),
    # Residue: `rpartition` keeps the last `::`, so its left half is not the
    # file of a nested grain.
    ("roles/api.py", "_definition_of"),
}

_SPLITS = ("split", "partition", "rpartition")


def _is_grain_split(node) -> bool:
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr in _SPLITS and bool(node.args)
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == "::")


def _own_nodes(fn):
    """The nodes of a function, without the nodes of a function nested in it.
    The site belongs to the innermost function."""
    todo = list(ast.iter_child_nodes(fn))
    while todo:
        n = todo.pop()
        yield n
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            todo.extend(ast.iter_child_nodes(n))


def _path_half_sites():
    out = []
    for f in sorted(PACKAGE.rglob("*.py")):
        tree = ast.parse(f.read_text(encoding="utf-8"))
        rel = f.relative_to(PACKAGE).as_posix()
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for n in _own_nodes(fn):
                hit = None
                if (isinstance(n, ast.Subscript) and _is_grain_split(n.value)
                        and isinstance(n.slice, ast.Constant)
                        and n.slice.value == 0):
                    hit = n
                elif (isinstance(n, ast.Assign) and _is_grain_split(n.value)
                        and isinstance(n.targets[0], ast.Tuple)):
                    first = n.targets[0].elts[0]
                    if not (isinstance(first, ast.Name) and first.id == "_"):
                        hit = n
                if hit is not None:
                    out.append((rel, fn.name, hit.lineno))
    return out


def test_no_path_half_split_outside_the_reader():
    stray = sorted(s for s in _path_half_sites() if s[:2] not in ALLOWED)
    assert stray == [], stray


def test_kind_of_reads_a_dot_slash_path_under_its_ruling(tmp_path):
    # The old rule kept `./`, so no ruling prefix covered the path, and the
    # heuristic said `attached` against the frame's word.
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO frame_rulings (id, kind) VALUES ('examples', 'program')")
    conn.commit()
    assert areas.kind_of(conn, "examples/app.py") == "program"
    assert areas.kind_of(conn, "./examples/app.py::main") == "program"
    assert areas.kind_of(conn, "/examples/app.py") == "program"
