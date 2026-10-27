"""
F22: the table an id lives in has one reader, `db.table_of`.

Night 170's W13 found two seats that repeated a refused call on an id of the
wrong table. s209 sent the batch b_3 to `model.adopt` three times. s200 sent
the test tst_c1 to `tests.encode` as a batch. Each refusal said what the id
was not, and never which table holds the id. Five helpers each kept their own
list of tables (plans/rootfix-audit-2026-10-27-b.md, F22).
"""
from __future__ import annotations

import ast
import re
import types
from pathlib import Path

import pytest

import rota
from rota.core import db
from rota.core.db import init_db
from rota.core.sandbox import _owner_of_ref
from rota.roles import api
from rota.roles.principal import ruled_ref_home


@pytest.fixture
def conn(tmp_path):
    c = init_db(tmp_path / "f22.db")
    c.execute("PRAGMA foreign_keys = OFF")
    c.execute("INSERT INTO items (id, text, kind) VALUES ('i1', 'x', 'in_scope')")
    c.execute("INSERT INTO batches (id, item_id) VALUES ('b_1', 'i1')")
    c.execute("INSERT INTO batches (id, item_id) VALUES ('b_3', 'i1')")
    c.execute("INSERT INTO tests (id, batch_id, path, body) "
              "VALUES ('tst_c1', 'b_1', 't.py', 'def test(): pass')")
    c.execute("INSERT INTO constraints (id, headline) VALUES ('k_one', 'h')")
    c.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
              "seq) VALUES ('m97', 't', 'principal', 'liaison', 'reply', 1)")
    c.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
              "author) VALUES ('l_1', 'i1', 'items', 'x', 'architect')")
    c.commit()
    yield c
    c.close()


def test_the_register_derives_from_identity(conn):
    """Every table of the register declares its sameness rule, and every
    table with an id column is in the register except the run journal."""
    from rota.core.identity import NATURAL_KEYS

    tables = db.id_tables(conn)
    assert tables == [t for t in NATURAL_KEYS if t in tables]
    assert "test_run_journal" not in tables
    assert {"batches", "tests", "messages", "ledger", "items"} <= set(tables)


def test_table_of_reads_the_prefixes(conn):
    assert db.table_of(conn, "reading:m97") == "messages"
    assert db.table_of(conn, "reading:m0") is None
    assert db.table_of(conn, "guess:i1") == "items"
    assert db.table_of(conn, "guess:i0") is None
    assert db.table_of(conn, "") is None
    assert db.table_of(conn, None) is None


def test_runner_labels_a_batch_line(conn):
    """The old runner list held no `batches`, so a batch line read as no
    table. Red on the parent: the reader did not exist."""
    assert db.table_of(conn, "b_1") == "batches"


def test_must_exist_names_the_table_that_holds_the_id(conn):
    """s200: a test id sent where a batch was wanted."""
    ctx = types.SimpleNamespace(conn=conn, trigger=None)
    with pytest.raises(ValueError) as e:
        api._must_exist(ctx, "batches", "tst_c1")
    assert "'tst_c1' is a row of tests" in str(e.value)


def test_must_exist_says_nothing_more_for_an_unknown_id(conn):
    ctx = types.SimpleNamespace(conn=conn, trigger=None)
    with pytest.raises(ValueError) as e:
        api._must_exist(ctx, "batches", "nothing")
    assert "is a row of" not in str(e.value)


def test_adopt_names_the_table_that_holds_the_id(conn):
    """s209: the batch b_3 sent to `model.adopt`. `_adopt_rows` adds these
    words to its miss. A landed ruling comes first, so this test reads the
    words alone."""
    assert db.elsewhere(conn, "b_3", "model_areas") == (
        "; 'b_3' is a row of batches")
    assert db.elsewhere(conn, "b_3", "batches") == ""
    assert db.elsewhere(conn, "nothing", "batches") == ""


def test_the_helpers_keep_their_rules(conn):
    """The helpers find the row through `table_of` and keep their own rule
    of which tables they accept."""
    assert api._table_of_ref(conn, "i1") == "items"
    assert api._table_of_ref(conn, "reading:m97") == "messages"
    assert api._table_of_ref(conn, "m97") is None
    assert api._table_of_ref(conn, "guess:i1") is None
    assert api._table_of_ref(conn, "b_1") is None
    assert ruled_ref_home(conn, "b_1") == "batches"
    assert ruled_ref_home(conn, "guess:i1") == "items"
    assert ruled_ref_home(conn, "reading:m97") == "messages"
    assert ruled_ref_home(conn, "m97") is None
    assert _owner_of_ref(conn, "guess:i1") == "architect"
    assert _owner_of_ref(conn, "i1") == "vision_keeper"
    assert _owner_of_ref(conn, "b_1") == "architect"
    assert _owner_of_ref(conn, "l_1") == "architect"
    assert _owner_of_ref(conn, "tst_c1") is None


def test_the_rules_name_tables_of_the_register(conn):
    """A rule of accepted tables names only tables the register holds."""
    from rota.core.sandbox import RULED_TABLES
    from rota.roles.principal import RULED_HOMES

    register = set(db.id_tables(conn))
    for rule in (api.LEDGER_HOMES, RULED_HOMES, set(RULED_TABLES)):
        assert set(rule) <= register, set(rule) - register


# A lookup of one id across a list of tables. Each site here is the residue of
# pass 1 of F22, or a lookup of a different fact. A new site goes red.
LOOKUP = re.compile(r"FROM \{\w+\} WHERE id = \?")
ALLOWED = {
    # The one reader of F22.
    ("rota/core/db.py", "table_of"),
    # One named table, not a search: the caller names the table it wants.
    ("rota/roles/api.py", "_must_exist"),
    ("rota/roles/api.py", "_ref_target_on_file"),
    ("rota/roles/api.py", "_adopt_rows"),
    ("rota/roles/api.py", "has"),
    ("rota/roles/api.py", "challenge_load"),
    ("rota/core/sandbox.py", "_item_of"),
    ("rota/roles/principal.py", "ruling_rows"),
    ("rota/testkit/fixtures.py", "_is_row"),
    ("rota/testkit/samplerepo.py", ""),
    # A row's columns per table, once the table is known.
    ("rota/core/runner.py", "_resolve_refs"),
    # Law 14 at the id: a new id must be free in every artefact table. This
    # checks a writer's id, not where a ref lives.
    ("rota/core/sandbox.py", "_scalar_id_fault"),
    ("rota/core/sandbox.py", "wrapper"),
    ("rota/roles/api.py", "_id_taken"),
    # The residue of pass 1: searches over a few tables, named in the report.
    ("rota/core/lifecycle.py", "_batch_notes"),
    ("rota/core/loop.py", "_perform"),
    ("rota/core/sandbox.py", "_quoted_rows"),
    ("rota/roles/api.py", "cite"),
    ("rota/roles/api.py", "_reply_sentence_fault"),
    ("rota/roles/api.py", "findings_find"),
    ("rota/roles/api.py", "_is_team_note"),
    ("rota/roles/api.py", "_owner_call"),
    ("rota/roles/api.py", "_misplaced_conflict"),
}


def _lookup_sites() -> set[tuple[str, str]]:
    root = Path(rota.__file__).parent
    out = set()
    for path in root.rglob("*.py"):
        src = path.read_text(encoding="utf-8")
        if not LOOKUP.search(src):
            continue
        rel = "rota/" + path.relative_to(root).as_posix()
        tree = ast.parse(src)
        spans = [(n.lineno, n.end_lineno, n.name) for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for no, line in enumerate(src.splitlines(), 1):
            if LOOKUP.search(line):
                inner = [s for s in spans if s[0] <= no <= s[1]]
                name = min(inner, key=lambda s: s[1] - s[0])[2] if inner else ""
                out.add((rel, name))
    return out


def test_one_reader_finds_the_table_of_an_id():
    extra = _lookup_sites() - ALLOWED
    assert not extra, (
        f"{sorted(extra)} look an id up across tables. Call db.table_of "
        f"(F22), or name the site in ALLOWED with its reason")
