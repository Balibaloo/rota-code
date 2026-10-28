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
}

_SPLITS = ("split", "rsplit", "partition", "rpartition")


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


def test_frame_assign_of_a_dot_directory_finds_its_rows(tmp_path):
    # Review pass 1, finding 1: `lstrip("./")` folded `.github` into
    # `github`, and the door said the path covers nothing in the index.
    from rota.core import sandbox as sandbox_mod

    db = tmp_path / "rota.db"
    conn = init_db(db)
    for g in (".github/workflows/ci.yml", "src/app.py"):
        conn.execute("INSERT INTO code_index (grain, grain_kind) "
                     "VALUES (?, 'path')", (g,))
    conn.commit()
    # The night databases record `/github` (the reviewer's probe4, f8rev).
    for typed in ("/github", "github", ".github"):
        sb = sandbox_mod.build("architect", conn, session_id="s1",
                               mode="frame", area="@frame")
        got = sb.call("frame.assign", path=typed, kind="ignore",
                      reason="the CI tool's own files")
        assert (got["id"], got["kind"]) == (".github", "ignore"), typed


# `_indexed_like` matches the dot-stripped spelling that old hints printed.
# Its strip is a match rule, not a fold, and a test in
# test_onboarding_phases.py holds it.
LSTRIP_ALLOWED = {("roles/api.py", "_indexed_like")}


def test_no_character_set_fold_of_a_path_in_roles():
    found = []
    for f in sorted((PACKAGE / "roles").rglob("*.py")):
        rel = f.relative_to(PACKAGE).as_posix()
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for n in _own_nodes(fn):
                if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                        and n.func.attr == "lstrip" and n.args
                        and isinstance(n.args[0], ast.Constant)
                        and n.args[0].value in ("./", "/.")
                        and (rel, fn.name) not in LSTRIP_ALLOWED):
                    found.append((rel, fn.name, n.lineno))
    assert found == [], found


def test_kind_of_reads_a_dot_slash_path_under_its_ruling(tmp_path):
    # The old rule kept `./`, so no ruling prefix covered the path, and the
    # heuristic said `attached` against the frame's word.
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO frame_rulings (id, kind) VALUES ('examples', 'program')")
    conn.commit()
    assert areas.kind_of(conn, "examples/app.py") == "program"
    assert areas.kind_of(conn, "./examples/app.py::main") == "program"
    assert areas.kind_of(conn, "/examples/app.py") == "program"
