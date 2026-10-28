"""
F13 of the rootfix audit of 2026-10-27: the module that defines a name.

Rule C76: one reader answers the fact. `module_of` reads the code index's
symbol rows, and `areas.kind_of` keeps the program files. Each test below
holds a case where an old door rule and the reader disagree.
"""
from __future__ import annotations

import pathlib
import re

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import api


def _db(tmp_path, files, symbols, surface, rulings=()):
    root = tmp_path / "wt"
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(text.encode())
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1', 'charge', 'in_scope', 'approved', 1, 1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1', 'i1', 'x')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                 "VALUES ('c1', 'tk1', 'a charge is billed once', ?)", (surface,))
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit, "
                 "worktree) VALUES ('b1', 'i1', 'running', 'abc123', ?)", (str(root),))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1', 'tk1')")
    for rel in files:
        conn.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, 'path')",
                     (rel,))
    for grain in symbols:
        conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) "
                     "VALUES (?, 'symbol', 'function')", (grain,))
    for prefix, kind in rulings:
        conn.execute("INSERT INTO frame_rulings (id, kind) VALUES (?, ?)",
                     (prefix, kind))
    conn.commit()
    return conn


def _encode(conn, body):
    sb = build("tester", conn, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    try:
        sb.call("tests.encode", id="tst_new", criterion_id="c1",
                path="tests/test_bill.py", body=body)
    except Exception as e:                                   # noqa: BLE001
        return str(e)
    return ""


_CLICK = {"src/click/__init__.py": "",
          "src/click/decorators.py": "def version_option():\n    return None\n"}


def test_the_misplaced_import_door_names_no_example_module(tmp_path):
    """The old regex skipped `tests` only, and named an example's module."""
    files = dict(_CLICK, **{"examples/demo/app.py": "def charge():\n    pass\n"})
    conn = _db(tmp_path, files,
               ["src/click/decorators.py::version_option", "examples/demo/app.py::charge"],
               '["src/click/decorators.py::charge"]')
    said = _encode(conn, "from src.click.decorators import charge\n"
                         "def test_x():\n    assert charge() is None\n")
    assert "examples.demo.app" not in said
    assert "Nothing in the tree defines it yet" in said


def test_the_missing_module_hint_names_no_test_helper(tmp_path):
    """The old regex read the folder name `tests` only, and offered
    `test.helpers`. The frame marks a file under `test/` attached."""
    files = dict(_CLICK, **{"test/helpers.py": "def charge():\n    pass\n"})
    conn = _db(tmp_path, files,
               ["src/click/decorators.py::version_option", "test/helpers.py::charge"],
               '["charge"]')
    said = _encode(conn, "from nowhere import charge\n"
                         "def test_x():\n    assert charge() is None\n")
    assert "no module of" in said
    assert "test.helpers" not in said


def test_a_method_is_no_module_definer(tmp_path):
    """The old regex allowed an indent, so a method named a module. The
    index holds top-level definitions only."""
    files = dict(_CLICK, **{"src/click/core.py":
                            "class Context:\n    def charge(self):\n        pass\n"})
    conn = _db(tmp_path, files,
               ["src/click/decorators.py::version_option", "src/click/core.py::Context"],
               '["src/click/decorators.py::charge"]')
    said = _encode(conn, "from src.click.decorators import charge\n"
                         "def test_x():\n    assert charge() is None\n")
    assert "click.core" not in said
    assert "Nothing in the tree defines it yet" in said


def test_the_shape_4_reader_reads_the_frames_ruling(tmp_path):
    """`_project_module_of` walked every package on disk. A file the frame
    rules ignore defines no name a test reaches."""
    files = {"src/bank/__init__.py": "", "src/bank/legacy.py": "def charge():\n    pass\n",
             "src/bank/core.py": "def charge():\n    pass\n"}
    conn = _db(tmp_path, files, ["src/bank/legacy.py::charge", "src/bank/core.py::charge"],
               "[]", rulings=[("src/bank/core.py", "ignore")])
    assert api.module_of(conn, "charge") == ("bank.legacy", "src/bank/legacy.py")
    assert api.module_of(conn, "charge", keep_root=True) == (
        "src.bank.legacy", "src/bank/legacy.py")
    assert api.module_of(conn, "src/bank/core.py::charge") == ("bank.core", "src/bank/core.py")
    assert api.definers_of(conn, "charge") == ["src/bank/legacy.py"]


def test_the_surface_vet_reads_the_program_definers(tmp_path):
    """`_vet_surface` read `_defined_in_tree`, a regex over the disk. A
    definition only in an example is no program definer."""
    conn = _db(tmp_path, {"examples/demo/app.py": "def charge():\n    pass\n"},
               ["examples/demo/app.py::charge"], "[]")
    assert api.definers_of(conn, "charge") == []


_ROOT = pathlib.Path(api.__file__).resolve().parents[1]

# The one reader, and the write-time residue that reads the disk because the
# index lags the session's own writes (the report of F13 names them).
_ALLOWED = {
    ("rota/roles/api.py", "module_of"),
}


def test_one_reader_answers_which_module_defines_a_name():
    """No door outside the named sites converts a path to a module or greps
    the tree for a definition. A second reader turns this test red."""
    import ast

    regex = re.compile(r"\(\?:def\|class\)|\(def\|class\)|async\\s\+def\|def\|class")
    offenders = []
    for py in sorted(_ROOT.rglob("*.py")):
        rel = py.relative_to(_ROOT.parent).as_posix()
        text = py.read_text(encoding="utf-8")
        tree = ast.parse(text)
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(fn):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                        and node.func.id in ("_dotted_module", "_project_module_of")
                        and (rel, fn.name) not in _ALLOWED):
                    offenders.append(f"{rel}:{node.lineno} {fn.name}")
    # A regex for a definition: known commit-time residue lines are counted.
    hits = [f"{py.relative_to(_ROOT.parent).as_posix()}:{n}"
            for py in sorted(_ROOT.rglob("*.py"))
            for n, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1)
            if regex.search(line) and "rf\"" in line]
    assert not offenders, offenders
    # Pass 1b: the staged writes cover the index's lag, so no door greps.
    assert not hits, hits
    for gone in ("_project_module_of", "_defined_in_tree", "_package_definers"):
        assert not hasattr(api, gone), gone


# Pass 1b: the four disk readers call `definers_of` with the session's
# staged writes. Each case is a staged file where the old disk rule and the
# reader disagree.

def _staged_db(tmp_path):
    return _db(tmp_path, {}, [], "[]")


def test_the_copy_door_reads_no_definition_in_a_docstring(tmp_path):
    """`_defined_in_tree` matched `def money` at column 0 in a string. A
    docstring defines nothing, so the copy door names no first definition."""
    conn = _staged_db(tmp_path)
    staged = (("src/shop/notes.py", '"""\ndef money(x):\n    pass\n"""\n'),)
    assert api.definers_of(conn, "money", staged, defs_only=True) == []


def test_the_cycle_hint_reads_the_session_s_new_module(tmp_path):
    """`_package_definers` read the disk beside the package's `__init__`.
    The index lacks the session's new module, and the staged text holds it."""
    conn = _staged_db(tmp_path)
    staged = (("src/click/shell.py", "class Command:\n    pass\n"),)
    assert api.definers_of(conn, "Command", staged) == ["src/click/shell.py"]


def test_the_commit_door_counts_a_top_level_assignment(tmp_path):
    """The commit door's regex counted a def or a class. A surface bound by
    an assignment imports, so the commit door finds its definer."""
    conn = _staged_db(tmp_path)
    staged = (("src/app/cli.py", "echo_json = _make_echo()\n"),)
    assert api.definers_of(conn, "echo_json", staged) == ["src/app/cli.py"]


def test_the_finding_door_counts_an_all_entry_and_no_method(tmp_path):
    """The sandbox's regex allowed an indent, so a method kept a removed
    grain defined. An `__all__` entry binds the name, and a method does not."""
    conn = _staged_db(tmp_path)
    method = (("src/app/a.py", "class A:\n    def total(self):\n        pass\n"),)
    assert api.definers_of(conn, "total", method) == []
    exported = (("src/app/b.py", "__all__ = ['total']\nfrom .c import total\n"),)
    assert api.definers_of(conn, "total", exported) == ["src/app/b.py"]


def test_a_staged_file_replaces_its_index_rows(tmp_path):
    """A staged file is the session's text. Its stale index rows and a
    removed file define nothing."""
    conn = _db(tmp_path, {}, ["src/app/a.py::total", "src/app/b.py::total"], "[]")
    staged = (("src/app/a.py", "x = 1\n"), ("src/app/b.py", None))
    assert api.definers_of(conn, "total", staged) == []


def test_the_indexer_writes_an_assignment_and_an_all_entry():
    """The index's definer rows take an assignment and an `__all__` entry."""
    from rota.onboarding import indexer, languages
    src = b"VERSION = '1'\n__all__ = ['run']\nfrom .core import run\n"
    facts = indexer.parse_file("pkg/__init__.py", src, languages.for_path("x.py"))
    kinds = {(n, k) for n, k, *_ in facts.symbols}
    assert {("VERSION", "variable"), ("run", "export")} <= kinds


def _tree_walks_for_a_definer(rel: str, text: str) -> list[str]:
    """The functions in `text` that walk a tree's `.py` files and read a def
    or a class, by a regex or by an ast parse. Pass 1d, review finding 3:
    the regex scan alone passed an ast walk."""
    import ast

    out = []
    for fn in ast.walk(ast.parse(text)):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        src = ast.get_source_segment(text, fn) or ""
        walks = 'glob("*.py")' in src or "os.walk(" in src
        by_regex = "(?:def|class)" in src or "(def|class)" in src
        by_ast = (".parse(" in src
                  and ("FunctionDef" in src or "ClassDef" in src))
        if walks and (by_regex or by_ast):
            out.append(f"{rel}:{fn.lineno} {fn.name}")
    return out


_PLANTED_WALK = '''
import ast
def defined_somewhere(root, name):
    for py in root.rglob("*.py"):
        tree = ast.parse(py.read_text())
        if any(isinstance(n, ast.FunctionDef) and n.name == name
               for n in tree.body):
            return True
    return False
'''


def test_a_bare_import_hint_names_the_module_that_defines_the_name(tmp_path):
    """Night 162: `import echo_json` met "no module of that name" 20 times.
    The bare surface `echo_json` is defined in a module, and the hint names
    that module (pass 1d, review finding 2)."""
    files = {"src/shop/__init__.py": "",
             "src/shop/utils.py": "def echo_json(obj):\n    return obj\n"}
    conn = _db(tmp_path, files, ["src/shop/utils.py::echo_json"], '["echo_json"]')
    said = _encode(conn, "import echo_json\n"
                         "def test_x():\n    assert echo_json.echo_json(1) == 1\n")
    assert "no module of that name exists" in said, said
    assert "`from shop.utils import echo_json`" in said, said


def test_the_walk_pin_finds_a_planted_ast_walk():
    assert _tree_walks_for_a_definer("plant.py", _PLANTED_WALK) == [
        "plant.py:3 defined_somewhere"]


# The ast walks over a tree that answer another fact. Each reads the
# bodies of the functions, not which file defines a name.
_OTHER_WALKS = {
    "rota/core/predicates.py _parameterised_writes",  # the writes a test makes
    "rota/roles/api.py tests_encode",       # which program function reads stdin
    "rota/roles/api.py _conftest_fixtures",  # the fixtures of each conftest.py
    "rota/roles/api.py _code_write",        # the files that import the target
}


def test_no_door_walks_the_tree_for_a_definer():
    """A function that globs the tree's `.py` files and reads a definition
    is a second reader of the definer. The staged writes replace it."""
    offenders = []
    for py in sorted(_ROOT.rglob("*.py")):
        rel = py.relative_to(_ROOT.parent).as_posix()
        offenders += [o for o in _tree_walks_for_a_definer(
                          rel, py.read_text(encoding="utf-8"))
                      if f"{rel} {o.split(' ', 1)[1]}" not in _OTHER_WALKS]
    assert not offenders, offenders


# Pass 1c, decision b: a binding row has its own grain kind, so a reader of
# `symbol` rows keeps its answer, and decision a: the commit door keeps its
# old acceptance (its door test is in test_desk_guards.py).

def _indexed(tmp_path, files):
    from rota.onboarding import indexer
    root = tmp_path / "tree"
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(text.encode())
    conn = init_db(tmp_path / "idx.db")
    indexer.build(conn, root)
    return conn, root


def test_a_symbol_listing_shows_no_variable(tmp_path):
    """At bfcd31af the indexer wrote `VERSION_NAME` as a `symbol` row, so
    `code.callables` listed a variable. A binding row is a `variable` now."""
    from types import SimpleNamespace
    conn, _ = _indexed(tmp_path, {"pkg/core.py":
                                  "VERSION_NAME = '1'\n__all__ = ['version_text']\n"
                                  "def version_text():\n    return VERSION_NAME\n"})
    listed = [r["grain"] for r in api.code_callables(SimpleNamespace(conn=conn),
                                                     hint="version name text")]
    assert listed == ["pkg/core.py::version_text"], listed
    kinds = dict(conn.execute("SELECT grain, grain_kind FROM code_index "
                              "WHERE grain LIKE '%::%'").fetchall())
    # The def comes after its `__all__` entry, and the def keeps the grain.
    assert kinds == {"pkg/core.py::VERSION_NAME": "variable",
                     "pkg/core.py::__all__": "variable",
                     "pkg/core.py::version_text": "symbol"}, kinds


def test_the_definer_reader_reads_the_binding_kinds(tmp_path):
    conn, _ = _indexed(tmp_path, {"pkg/__init__.py": "__all__ = ['run']\n",
                                  "pkg/cli.py": "echo = make()\n"})
    assert api.definers_of(conn, "echo") == ["pkg/cli.py"]
    assert api.definers_of(conn, "run") == ["pkg/__init__.py"]
    assert api.definers_of(conn, "echo", defs_only=True) == []


def test_the_commit_reader_keeps_the_old_leniency(tmp_path):
    """The old commit regex read a def or a class at any indent, in any file
    outside `tests`. The strict reader reads neither a method nor a test."""
    conn, root = _indexed(tmp_path, {
        "pkg/core.py": "class A:\n    def total(self):\n        pass\n",
        "tests/test_a.py": "def charge():\n    pass\n"})
    assert api.definers_of(conn, "total") == []
    assert api.definers_of(conn, "total", lenient_root=root) == ["pkg/core.py"]
    assert api.definers_of(conn, "charge", lenient_root=root) == []


def test_an_older_index_takes_the_binding_kinds(tmp_path):
    """A run database from before pass 1c holds the four grain kinds in the
    CHECK of `code_index`. `init_db` builds the table again, and a pass 1b
    binding row takes its kind."""
    import sqlite3
    path = tmp_path / "old.db"
    init_db(path).close()
    raw = sqlite3.connect(path)
    sql = raw.execute("SELECT sql FROM sqlite_master WHERE name = 'code_index'").fetchone()[0]
    old = sql.replace(",\n                                                    'variable','export')", ")")
    assert "'variable'" not in old
    raw.execute("DROP TABLE code_index")
    raw.execute(old)
    raw.execute("INSERT INTO code_index (grain, grain_kind, sym_kind, area) VALUES "
                "('a.py', 'path', '', 'a'), ('a.py::X', 'symbol', 'variable', 'a'), "
                "('a.py::f', 'symbol', 'function', 'a')")
    raw.commit()
    raw.close()
    conn = init_db(path)
    rows = dict(conn.execute("SELECT grain, grain_kind FROM code_index").fetchall())
    assert rows == {"a.py": "path", "a.py::X": "variable", "a.py::f": "symbol"}
    conn.execute("INSERT INTO code_index (grain, grain_kind) VALUES ('a.py::Y', 'export')")
    assert init_db(path).execute("SELECT count(*) FROM code_index").fetchone()[0] == 4


def test_one_lenient_definer_regex():
    """The old commit rule lives in one constant. Each line of the package
    that holds a def-or-class regex is a named site."""
    # The second site reads the names a written text defines, for the
    # removed-statement check. It reads no surface's definer.
    hits = sorted(f"{py.relative_to(_ROOT.parent).as_posix()}:"
                  f"{line.strip().split(' ', 1)[0]}"
                  for py in _ROOT.rglob("*.py")
                  for line in py.read_text(encoding="utf-8").splitlines()
                  if "(?:def|class)" in line or "(def|class)" in line)
    assert hits == ["rota/roles/api.py:_LENIENT_DEFINER",
                    "rota/roles/api.py:m"], hits


def test_the_tree_beyond_the_index_is_what_the_next_build_reads(tmp_path):
    """The F13 gate reds (2026-10-28): a batch commit defined `echo_json`
    ahead of the index, and the definer reader read the index alone. The
    texts beyond the index come from the refresh's own walk and hash."""
    from rota.onboarding import indexer
    conn, root = _indexed(tmp_path, {"pkg/core.py": "def run():\n    pass\n",
                                     "pkg/old.py": "def gone():\n    pass\n"})
    assert indexer.unindexed(conn, root) == {}
    (root / "pkg" / "utils.py").write_bytes(b"def echo_json(o):\n    print(o)\n")
    (root / "pkg" / "old.py").unlink()
    beyond = indexer.unindexed(conn, root)
    assert beyond == {"pkg/utils.py": "def echo_json(o):\n    print(o)\n",
                      "pkg/old.py": None}, beyond
    assert api.definers_of(conn, "echo_json", tuple(beyond.items())) == ["pkg/utils.py"]
    assert api.definers_of(conn, "gone", tuple(beyond.items())) == []
    indexer.build(conn, root)
    assert indexer.unindexed(conn, root) == {}
