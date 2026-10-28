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
    assert _owner_of_ref(conn, "guess:i0") is None


@pytest.fixture
def clash(conn):
    """Nights 161 to 170 hold `sentinel` as a constraint and a glossary term.
    Night 162 holds `echo_json` as an item and a glossary term."""
    for term in ("sentinel", "echo_json"):
        conn.execute("INSERT INTO glossary_terms (id, term, sense_short) "
                     "VALUES (?, ?, 'x')", (term, term))
    conn.execute("INSERT INTO constraints (id, headline) VALUES "
                 "('sentinel', 'h')")
    conn.execute("INSERT INTO items (id, text, kind) VALUES "
                 "('echo_json', 'x', 'in_scope')")
    conn.commit()
    return conn


def test_an_id_in_two_tables_keeps_the_scope_order(clash):
    """Review 1, finding 1: the register order gave `glossary_terms`. Each
    scope's own order gives the answer the helper gave before F22."""
    assert db.tables_of(clash, "sentinel") == ["glossary_terms", "constraints"]
    assert api._table_of_ref(clash, "sentinel") == "constraints"
    assert api._table_of_ref(clash, "echo_json") == "items"
    assert ruled_ref_home(clash, "sentinel") == "constraints"
    assert ruled_ref_home(clash, "echo_json") == "items"
    assert _owner_of_ref(clash, "sentinel") == "terminologist"
    assert db.table_of(clash, "sentinel", among=("constraints", "model_areas")
                       ) == "constraints"
    assert db.elsewhere(clash, "sentinel", "model_areas") == (
        "; 'sentinel' is a row of glossary_terms and constraints")
    assert db.elsewhere(clash, "sentinel", "constraints") == ""


def test_ledger_log_accepts_any_home_of_an_id(clash):
    """`ledger.log(about_ref='sentinel', about_table='constraints')` passed
    before F22, and pass 1 refused it."""
    homes = api._homes_of_ref(clash, "sentinel")
    assert homes == ["constraints", "glossary_terms"]
    assert "constraints" in homes and "glossary_terms" in homes


def test_the_register_cache_follows_the_database(tmp_path):
    """Review 1, finding 2: a cache keyed by `id(conn)` gave a new
    connection the register of a closed one."""
    first = init_db(tmp_path / "a.db")
    tables = db.id_tables(first)
    first.execute("DROP TABLE business_rules")
    assert "business_rules" in tables
    assert "business_rules" not in db.id_tables(first)
    first.close()


def test_one_rule_reads_the_guess_prefix(conn):
    assert db.guess_item("guess:i1") == "i1"
    assert db.guess_item("guess:") is None
    assert db.guess_item(None) is None
    assert db.table_of(conn, "guess:") is None


def test_the_rules_name_tables_of_the_register(conn):
    """A rule of accepted tables names only tables the register holds."""
    from rota.core.sandbox import RULED_TABLES
    from rota.roles.principal import RULED_HOMES

    register = set(db.id_tables(conn))
    for rule in (api.LEDGER_HOMES, RULED_HOMES, set(RULED_TABLES)):
        assert set(rule) <= register, set(rule) - register


# The one-reader pin (F22 review 1, finding 4). An ast walk scores each
# function under rota/. One point for each table name that a `SELECT 1`
# probe of an id names. One point for a call to an F22 reader. Two points for
# a probe whose table is a variable inside a loop or a comprehension. A score
# of 2 or more is a lookup over two or more tables. Adjacent string literals
# join in the ast, so a query split over lines is one string.
PROBE = re.compile(r"SELECT\s+1\s+FROM\s+(\w+|\{\})\s+(?:\w+\s+)?WHERE\s+"
                   r"(?:\w+\.)?id\s*=\s*\?")
DYNAMIC = re.compile(r"FROM\s+\{\}\s+(?:\w+\s+)?WHERE\s+(?:\w+\.)?id\s*=\s*\?")
READERS = {"table_of", "tables_of", "_table_of_ref", "_homes_of_ref",
           "ruled_ref_home", "_owner_of_ref"}
LOOPS = (ast.For, ast.While, ast.ListComp, ast.SetComp, ast.DictComp,
         ast.GeneratorExp)


def _text(node) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else "{}"
                       for v in node.values)
    return None


class _Scorer(ast.NodeVisitor):
    def __init__(self):
        self.stack: list[list] = []
        self.loops = 0
        self.out: dict[str, int] = {}

    def _function(self, node):
        self.stack.append([node.name, set(), False, False])
        loops, self.loops = self.loops, 0
        self.generic_visit(node)
        self.loops = loops
        name, tables, reads, dynamic = self.stack.pop()
        self.out[name] = max(self.out.get(name, 0),
                             len(tables) + reads + 2 * dynamic)

    visit_FunctionDef = visit_AsyncFunctionDef = _function

    def generic_visit(self, node):
        loop = isinstance(node, LOOPS)
        self.loops += loop
        if self.stack:
            frame = self.stack[-1]
            if isinstance(node, ast.JoinedStr):
                text = _text(node)
                for m in PROBE.finditer(text):
                    if m.group(1) != "{}":
                        frame[1].add(m.group(1))
                if self.loops and DYNAMIC.search(text):
                    frame[3] = True
                # The parts of an f-string are constants. They are read above.
                self.loops -= loop
                return
            text = _text(node)
            if text:
                frame[1] |= {m.group(1) for m in PROBE.finditer(text)
                             if m.group(1) != "{}"}
            if isinstance(node, ast.Call):
                f = node.func
                name = f.attr if isinstance(f, ast.Attribute) else getattr(
                    f, "id", "")
                frame[2] = frame[2] or name in READERS
        super().generic_visit(node)
        self.loops -= loop


def _scores(src: str) -> dict[str, int]:
    scorer = _Scorer()
    scorer.visit(ast.parse(src))
    return scorer.out


def _lookup_sites() -> set[tuple[str, str]]:
    root = Path(rota.__file__).parent
    out = set()
    for path in root.rglob("*.py"):
        rel = "rota/" + path.relative_to(root).as_posix()
        for name, score in _scores(path.read_text(encoding="utf-8")).items():
            if score >= 2:
                out.add((rel, name))
    return out


# The three lookups of review 1 that the first pin let pass, as they stood at
# e33bc142: the relay split, `findings_find` and `answer_about`.
REVIEW_FORMS = (
    '''
def split(conn, ref):
    if conn.execute("SELECT 1 FROM criteria WHERE id = ?", (ref,)).fetchone():
        return "terminologist"
    elif conn.execute("SELECT 1 FROM batches "
                      "WHERE id=?", (ref,)).fetchone():
        return "architect"
''',
    '''
def find(conn, cid):
    if conn.execute("SELECT 1 FROM constraints WHERE id = ?",
                    (cid,)).fetchone() is None:
        held = [t for t in ("criteria", "tests") if conn.execute(
            f"SELECT 1 FROM {t} WHERE id = ?", (cid,)).fetchone()]
''',
    '''
def about(conn, refs):
    return [r for r in refs if _table_of_ref(conn, r) or conn.execute(
        "SELECT 1 FROM batches b WHERE b.id = ?", (r,)).fetchone()]
''',
)


@pytest.mark.parametrize("src", REVIEW_FORMS)
def test_the_pin_catches_the_review_forms(src):
    assert max(_scores(src).values()) >= 2


# Each allowed function, with its reason. A new lookup goes red.
ALLOWED = {
    # The one reader of F22.
    ("rota/core/db.py", "tables_of"),
    # Law 14 at the id: a new id must be free in every artefact table. This
    # checks a writer's id, not where a ref lives.
    ("rota/core/sandbox.py", "_scalar_id_fault"),
    ("rota/core/sandbox.py", "wrapper"),
    ("rota/roles/api.py", "_id_taken"),
    # A row's columns per table, once the table is known.
    ("rota/core/runner.py", "_resolve_refs"),
    # Pass 1b stopped at its cap here. The wider pin scores these 22 sites at
    # 2 or more, and nobody has read them yet. Some test two different ids,
    # and some are second readers. Pass 2 reads each one and moves it or
    # gives it a reason.
    ("rota/core/lifecycle.py", "_batch_notes"),
    ("rota/core/loop.py", "_perform"),
    ("rota/core/predicates.py", "observed_entries"),
    ("rota/core/predicates.py", "quarantined"),
    ("rota/core/sandbox.py", "_challenge_sides"),
    ("rota/core/sandbox.py", "_names_no_source"),
    ("rota/core/sandbox.py", "_quoted_rows"),
    ("rota/core/sandbox.py", "stage"),
    ("rota/roles/api.py", "_adopt_rows"),
    ("rota/roles/api.py", "_assert_words_fault"),
    ("rota/roles/api.py", "_contested_elsewhere"),
    ("rota/roles/api.py", "_is_team_note"),
    ("rota/roles/api.py", "_misplaced_conflict"),
    ("rota/roles/api.py", "_owner_call"),
    ("rota/roles/api.py", "_reply_sentence_fault"),
    ("rota/roles/api.py", "brief_segment"),
    ("rota/roles/api.py", "cite"),
    ("rota/roles/api.py", "criteria_specify"),
    ("rota/roles/api.py", "decisions_author"),
    ("rota/roles/api.py", "ledger_log"),
    ("rota/roles/api.py", "rulings_rule"),
    ("rota/roles/principal.py", "ruling_rows"),
}


def test_one_reader_finds_the_table_of_an_id():
    extra = _lookup_sites() - ALLOWED
    assert not extra, (
        f"{sorted(extra)} look an id up across tables. Call db.tables_of "
        f"(F22) with a scope, or name the site in ALLOWED with its reason")
