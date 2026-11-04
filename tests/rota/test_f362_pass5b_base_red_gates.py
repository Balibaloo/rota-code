"""
Frame 362, pass 5b, section 1: the review and merge gates read the base run.

The review of pass 5 (plans/f362-review-pass5.md, high 1): on icalendar 5
inherited test files are red at the base. The review predicate and
`mergeable` counted every red run at the head, so no batch reached the
Critic or the merge. A test the tree never proved is not one the batch
broke. A Tester's test, and an inherited test with no red base record,
hold both gates as before.
"""
from __future__ import annotations

import json

import pytest

from rota.core import harness, lifecycle, predicates
from rota.core.db import init_db
from rota.roles.principal import touch_words

PROJECT = "src/pkg/tests/test_old.py"


@pytest.fixture
def db(tmp_path):
    """Batch `b1` at head `h1`: one Tester test green, one inherited red."""
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','ship it','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i1','do it')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) "
                 "VALUES ('c1','t1','it works')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('b1','i1','running','h1')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','t1')")
    conn.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, "
                 "confidence) VALUES ('b1','src/pkg/mod.py','path','expected')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES ('own1','b1','c1','src/pkg/tests/test_new.py','x')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES (?, 'b1', NULL, ?, 'x')",
                 (harness.inherited_id(PROJECT), PROJECT))
    _run(conn, "own1", "pass")
    _run(conn, harness.inherited_id(PROJECT), "fail")
    return conn


def _run(conn, tid, result):
    conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
                 "result) VALUES (?, 'b1', ?, 'h1', ?)", (f"r_{tid}", tid, result))


def _base(conn, record):
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                 ("base_run:b1", json.dumps(record)))


def _pass_verdict(conn):
    conn.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) "
                 "VALUES ('v1','b1','h1','pass')")


def _reviewed(conn):
    return any(w.refs == ("b1",) for w in predicates.review(conn))


def test_a_test_red_at_the_base_holds_no_gate(db):
    _base(db, {harness.inherited_id(PROJECT): {"result": "fail", "output": "E"}})
    assert _reviewed(db)
    _pass_verdict(db)
    assert "not passing" not in (lifecycle.mergeable(db, "b1") or "")


def test_an_inherited_test_with_no_base_record_holds_both(db):
    assert not _reviewed(db)
    _pass_verdict(db)
    assert lifecycle.mergeable(db, "b1") == "1 test(s) not passing"


def test_an_inherited_test_green_at_the_base_holds_both(db):
    _base(db, {harness.inherited_id(PROJECT): {"result": "pass"}})
    assert not _reviewed(db)
    _pass_verdict(db)
    assert lifecycle.mergeable(db, "b1") == "1 test(s) not passing"


def test_a_tester_test_red_holds_both(db):
    _base(db, {harness.inherited_id(PROJECT): {"result": "fail"},
               "own1": {"result": "fail"}})
    db.execute("UPDATE test_runs SET result = 'fail' WHERE test_id = 'own1'")
    assert not _reviewed(db)
    _pass_verdict(db)
    assert lifecycle.mergeable(db, "b1") == "1 test(s) not passing"


def test_the_touch_line_names_the_tests_red_at_the_base(db):
    _base(db, {harness.inherited_id(PROJECT): {"result": "fail", "output": "E"}})
    words = touch_words(db, "b1")
    assert ("1 of the repository's tests were red before this change: "
            f"{PROJECT}.") in words
