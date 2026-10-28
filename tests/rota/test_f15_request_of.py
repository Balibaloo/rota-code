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

import pytest

from rota.core.db import init_db
from rota.roles.principal import off_page, request_of, requests_of
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
    for item, stmts, described in (("x_a", ("s1", "s2"), 0), ("d_b", ("s2",), 1),
                                   ("z_c", ("s3",), 0)):
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
    assert request_of(db, "s2") is None


# The one-reader pin. A function that reads a row's owner and also reads
# the description mark makes a second rule for the fact. Only the reader
# itself may do both. The statement walk to a request entry stays there too.
OWNER_CALLS = {"request_of", "requests_of", "_item_request"}
DESCRIPTION_READS = {"_is_description", "not_described"}
READER_SITES = {"_item_request"}
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


def test_one_reader_owns_the_request_of_a_row():
    second = []
    for path, fn in _functions():
        names = _names(fn)
        if fn.name in READER_SITES:
            continue
        if names & OWNER_CALLS and names & DESCRIPTION_READS:
            second.append(f"{path}::{fn.name}")
    assert second == []


def test_one_walk_from_a_statement_to_its_request():
    walks = [f"{path}::{fn.name}" for path, fn in _functions()
             if "_root_statement" in _names(fn) and fn.name not in ROOT_SITES]
    assert walks == []
