"""
Fact F15: one reader says which request owns a row.

The audit of 2026-10-27 counts nine rules for the fact. `request_of` and
`off_page` disagree on a description (`plans/closed-reach-c.md`, frame
274). `request_of` gave the request that a description cites. `off_page`
gave the description no request. Night 133's account item and the reviews
of 61a0f41d, e406e976 and a1bd448f each needed the second answer. So the
one reader gives a description no request, and `request_of` reads every
row: an item, a criterion, a ticket, a test, a ledger row or a page ref.
"""
from __future__ import annotations

import ast
import pathlib
import re

import pytest

from rota.core.db import init_db
from rota.roles.principal import (
    _is_request_item, off_page, page_request, request_of, requests_of)
from rota.testkit.fixtures import seed_provenance, seed_ref


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    for n, (entry, order) in enumerate((("e_a", 8), ("e_b", 16), ("e_c", 24)), start=1):
        conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
                     "(?, 'principal', ?, ?)", (entry, order, f"request {n}"))
        conn.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
                     "text, status) VALUES (?, ?, 0, 10, ?, 'ratified')",
                     (f"s{n}", entry, f"request {n}"))
    # x_a cites s1 and s2, so it is request a's. d_b is the account and
    # cites s2. z_c is request c's.
    # s4 is request c's second statement. x_a and z_c both cite it.
    conn.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
                 "text, status) VALUES ('s4', 'e_c', 11, 20, 'more', 'ratified')")
    # Night 161's s1 reaches `echo_json` and the account `how_it_works`.
    for item, stmts, described in (("x_a", ("s1", "s2", "s4"), 0), ("d_b", ("s2",), 1),
                                   ("z_c", ("s3", "s4"), 0), ("echo_json", ("s1",), 0),
                                   ("how_it_works", ("s1",), 1)):
        conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                     "version, is_description) VALUES (?, ?, 'in_scope', "
                     "'approved', 1, 1, ?)", (item, f"the {item} item", described))
        for s in stmts:
            seed_ref(conn, "items", item, "statement", s)
        seed_provenance(conn, "items", item, "decided")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_x', 'x_a', 't')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                 "VALUES ('c_x', 'tk_x', 'a criterion', '[]')")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES ('b_x', 'x_a', 'running')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
                 "('tst_x', 'b_x', 'c_x', 'tests/test_x.py', '')")
    conn.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, kind, "
                 "status, author) VALUES ('l_x', 'tst_x', 'tests', 'a note', "
                 "'default', 'open', 'tester')")
    # Request c is the newest boundary, so a page has a request.
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq, "
                 "status, body_refs) VALUES ('m_c', 't1', 'principal', 'liaison', "
                 "'converse', 3, 'answered','[\"e_c\"]')")
    conn.commit()
    return conn


def test_a_description_belongs_to_no_request(db):
    # The old rule gave e_b, the request that d_b cites.
    assert request_of(db, "d_b") is None
    assert request_of(db, "x_a") == "e_a"


def test_off_page_keeps_a_row_that_reaches_the_account(db):
    # s2 reaches d_b and x_a. The old `off_page` read d_b as request b's,
    # so every item was another request's and the row left page c.
    assert "s2" not in off_page(db, ["z_c", "s2"])
    assert requests_of(db, "s2") == {None, "e_a"}


def test_a_criterion_and_a_ticket_belong_to_their_item_request(db):
    # The old `request_of` read an item id only and gave None (frame 316).
    assert request_of(db, "c_x") == "e_a"
    assert request_of(db, "tk_x") == "e_a"


def test_a_test_and_its_note_belong_to_the_criterion_request(db):
    # `_items_reached` has no tests lookup, so the old reader gave None.
    assert request_of(db, "tst_x") == "e_a"
    assert request_of(db, "l_x") == "e_a"


def test_a_row_of_two_requests_has_no_single_owner(db):
    assert request_of(db, "s4") is None


# Pass 1b closes the five findings of `plans/f15-review-p1.md`.

def test_a_row_of_one_request_and_the_account_is_that_request(db):
    # Finding 2: night 161's s1 gave None, because the account counted.
    assert request_of(db, "s1") == "e_a"
    assert request_of(db, "s2") == "e_a"


def test_a_note_about_another_request_test_leaves_the_page(db):
    # Finding 1: `off_page` read `_items_reached`, which has no tests
    # lookup, so the page numbered l_x while `land` read it as elsewhere.
    assert "l_x" in off_page(db, ["z_c", "l_x"])
    assert "tst_x" in off_page(db, ["z_c", "tst_x"])


def test_a_test_ref_reaches_its_request_on_the_page(db):
    # Finding 1: `page_request` read no item for a test.
    assert page_request(db, ["tst_x"]) == "e_a"


def test_a_description_is_no_request_item(db):
    # Finding 4 is open. The swap to `_item_request` turns 119 tests red,
    # because their items cite no statement. This test guards the answer.
    assert not _is_request_item(db, "d_b")
    assert _is_request_item(db, "x_a")


# The one-reader pin. A function that reads a row's owner, or walks a row
# to its items, and also reads the description mark makes a second rule
# for the fact. A raw SQL walk from a ref to its statement's entry is a
# second owner too. Each allowed site carries its reason.
OWNER_CALLS = {"request_of", "requests_of", "_item_request",
               "_items_reached", "_reached", "row_items"}
DESCRIPTION_READS = {"_is_description", "not_described"}
READER_SITES = {
    # The one reader.
    "_item_request",
    # The items a ledger row is about, for the agenda and the park. An
    # observed item has a page and no request, so the items cannot be
    # filtered by `_item_request` (F15 review 1, finding 3).
    "ledger_items",
}
RAW_SITES = {
    "_item_request",
    # The wake pushes the principal's words of the item's entries. It
    # reads text, not the owner of a row.
    "push_working_set",
}
ROOT_SITES = {"_item_request", "_root_statement", "uncovered_statements"}


def _functions():
    root = pathlib.Path(__file__).resolve().parents[2] / "rota"
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_bytes().decode("utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                yield path.relative_to(root.parent).as_posix(), node


def _names(node):
    out = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            f = sub.func
            out.add(f.id if isinstance(f, ast.Name) else getattr(f, "attr", None))
        elif isinstance(sub, ast.Constant) and isinstance(sub.value, str) \
                and "is_description" in sub.value:
            out.add("_is_description")
    return out


def _raw_owner(node):
    # One SQL text that joins `refs` to a statement's `span_entry`. The
    # docstring is prose and does not count.
    doc = ast.get_docstring(node, clean=False)
    return any(isinstance(sub, ast.Constant) and isinstance(sub.value, str)
               and sub.value != doc and "span_entry" in sub.value
               and re.search(r"\b(FROM|JOIN)\s+refs\b", sub.value)
               for sub in ast.walk(node))


def test_one_reader_owns_the_request_of_a_row():
    second = []
    for path, fn in _functions():
        names = _names(fn)
        if fn.name in READER_SITES:
            continue
        if names & OWNER_CALLS and names & DESCRIPTION_READS:
            second.append(f"{path}::{fn.name}")
    assert second == []


def test_no_raw_sql_walks_a_row_to_its_request():
    raw = [f"{path}::{fn.name}" for path, fn in _functions()
           if _raw_owner(fn) and fn.name not in RAW_SITES]
    assert raw == []


def test_one_walk_from_a_statement_to_its_request():
    walks = [f"{path}::{fn.name}" for path, fn in _functions()
             if "_root_statement" in _names(fn) and fn.name not in ROOT_SITES]
    assert walks == []


# Two readers of the review's probe 3 passed both pins of pass 1.
PLANTED = '''
def p5(conn, item):
    if _is_description(conn, item):
        return None
    return conn.execute(
        "SELECT e.id FROM refs r JOIN statements s ON s.id = r.target "
        "JOIN entries e ON e.id = s.span_entry WHERE r.src_id = ?", (item,))

def p6(conn, ref):
    return [i for i in _items_reached(conn, ref) if not _is_description(conn, i)]
'''


def test_the_pins_catch_the_planted_readers():
    fns = {n.name: n for n in ast.walk(ast.parse(PLANTED))
           if isinstance(n, ast.FunctionDef)}
    assert _raw_owner(fns["p5"])
    assert _names(fns["p6"]) & OWNER_CALLS and _names(fns["p6"]) & DESCRIPTION_READS
