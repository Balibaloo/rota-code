"""
Frame 318, W-B of night 164: a tests move lifts `tests_failing` only when
the failing test moves.

Night 164, bg_2: `developer|tick:tests_failing|bg_2` was quarantined four
times. Three lifts restarted the same round. s228 and s244 added a passing
test, and s252 re-encoded a passing test. The failing test
`tst_format_filename_shorten_example` never changed. Inside round 2, s229's
commit 63c65435 grew the red from 1 to 5, and the harness reset the key.
"""
from __future__ import annotations

import pytest

from rota.core.db import (SessionResult, Write, init_db, lift_on_red_move,
                          red_before, session_commit)

KEY = "developer|tick:tests_failing|bg_2"
TIRED = "developer|tick:exhausted|bg_2"
RED = "tst_format_filename_shorten_example"
SAME = "E       AssertionError: assert 'a...b' == 'ab...'\n"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i2','shorten a file name','in_scope',"
                 "'approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk2','i2','format_filename shortens')")
    for cid in ("c_shorten", "c_plain"):
        conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                     "(?, 'tk2', 'the name is shortened')", (cid,))
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('bg_2','i2','running','h1')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_2','tk2')")
    for tid, cid in ((RED, "c_shorten"), ("tst_plain", "c_plain")):
        conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                     "VALUES (?, 'bg_2', ?, ?, 'def test_x():\n    pass\n')",
                     (tid, cid, f"tests/{tid}.py"))
    _runs(conn, "h1", {RED: SAME, "tst_plain": None})
    conn.commit()
    return conn


def _runs(conn, sha: str, said: dict) -> None:
    """One harness result per test at `sha`. None is a pass."""
    for tid, out in said.items():
        n = conn.execute("SELECT COUNT(*) FROM test_runs").fetchone()[0]
        conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
                     "result, output) VALUES (?, 'bg_2', ?, ?, ?, ?)",
                     (f"tr{n}", tid, sha, "pass" if out is None else "fail",
                      out or "1 passed"))


def _quarantine(conn, key: str = KEY, attempts: int = 3, held: int = 1) -> None:
    conn.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
                 "reported) VALUES (?, ?, ?, ?)", (key, attempts, held, held))
    conn.commit()


def _key(conn, key: str = KEY):
    row = conn.execute("SELECT attempts, quarantined FROM tick_attempts "
                       "WHERE tick_key = ?", (key,)).fetchone()
    return (row["attempts"], row["quarantined"]) if row else None


def _session(conn, role: str, *writes: Write) -> None:
    seq = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    session_commit(conn, SessionResult(session_id=f"s{seq}", role=role,
                                       writes=list(writes)))


def test_a_new_passing_test_keeps_the_quarantine(db):
    """s228's shape: the red test is unchanged, and a new test lands."""
    _quarantine(db)
    _quarantine(db, TIRED)
    _session(db, "tester", Write("tests", "tst_new", {
        "batch_id": "bg_2", "criterion_id": "c_plain",
        "path": "tests/tst_new.py", "body": "def test_new():\n    pass\n"}))
    assert _key(db) == (3, 1), "a new test is not progress on the red"
    assert _key(db, TIRED) == (3, 1)


def test_a_new_passing_test_resets_no_count_of_the_red(db):
    _quarantine(db, attempts=2, held=0)
    _session(db, "tester", Write("tests", "tst_new", {
        "batch_id": "bg_2", "criterion_id": "c_plain",
        "path": "tests/tst_new.py", "body": "def test_new():\n    pass\n"}))
    assert _key(db) == (2, 0), "the count holds"


def test_a_re_encoded_passing_test_keeps_the_quarantine(db):
    """s252's shape: a passing test's body changes."""
    _quarantine(db)
    _session(db, "tester", Write("tests", "tst_plain",
                                 {"body": "def test_x():\n    assert 1\n"},
                                 op="update"))
    assert _key(db) == (3, 1)


def test_a_re_encoded_red_test_lifts_the_quarantine(db):
    _quarantine(db)
    _quarantine(db, TIRED)
    _session(db, "tester", Write("tests", RED,
                                 {"body": "def test_x():\n    assert 2\n"},
                                 op="update"))
    assert _key(db) is None, "the red test moved"
    assert _key(db, TIRED) is None


def test_a_retire_of_the_red_criterion_lifts_the_quarantine(db):
    _quarantine(db)
    _session(db, "terminologist", Write("criteria", "c_shorten",
                                        {"retired_by": "r1"}, op="update"))
    assert _key(db) is None, "the red set changed"


def test_a_respecify_of_a_green_criterion_keeps_the_quarantine(db):
    _quarantine(db)
    _session(db, "terminologist", Write("criteria", "c_plain",
                                        {"text": "v2"}, op="update"))
    assert _key(db) == (3, 1), "the red set is the same"


def test_a_respecify_of_a_green_criterion_still_lifts_verdict_failed(db):
    """Pass 2b's rule: the failed verdict stays at the head."""
    key = "developer|tick:verdict_failed|bg_2"
    _quarantine(db, key)
    _session(db, "terminologist", Write("criteria", "c_plain",
                                        {"text": "v2"}, op="update"))
    assert _key(db, key) is None


def _grow(conn, tests: int) -> None:
    for i in range(tests):
        conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                     "VALUES (?, 'bg_2', 'c_plain', ?, 'x')",
                     (f"tst_g{i}", f"tests/tst_g{i}.py"))


def test_a_head_that_grows_the_red_keeps_the_quarantine(db):
    """s229's shape: commit 63c65435 grew the red from 1 to 5."""
    _grow(db, 4)
    _quarantine(db)
    before = red_before(db, "bg_2")
    _runs(db, "63c6543", {RED: SAME, **{f"tst_g{i}": SAME for i in range(4)}})
    assert lift_on_red_move(db, "bg_2", "63c6543", before) is False
    assert _key(db) == (3, 1), "a grown red is not progress"


def test_a_head_that_cures_the_red_lifts_the_quarantine(db):
    _quarantine(db)
    before = red_before(db, "bg_2")
    _runs(db, "h2", {RED: None, "tst_plain": None})
    assert lift_on_red_move(db, "bg_2", "h2", before) is True
    assert _key(db) is None


def test_a_new_red_test_at_the_same_head_lifts_the_quarantine(db):
    """Pass 3b: the Tester's new red test is a new cause for the Developer.
    The head did not change, so the growth is not the Developer's commit."""
    _grow(db, 1)
    _quarantine(db)
    _quarantine(db, TIRED)
    before = red_before(db, "bg_2")
    _runs(db, "h1", {RED: SAME, "tst_plain": None, "tst_g0": SAME})
    assert lift_on_red_move(db, "bg_2", "h1", before, same_head=True) is True
    assert _key(db) is None
    assert _key(db, TIRED) is None


def test_the_same_red_at_the_same_head_keeps_the_quarantine(db):
    _quarantine(db)
    before = red_before(db, "bg_2")
    _runs(db, "h1", {RED: SAME, "tst_plain": None})
    assert lift_on_red_move(db, "bg_2", "h1", before, same_head=True) is False
    assert _key(db) == (3, 1)
