"""Frame 306, W-A: his drop of a check line retires that test.

Night 164's m121 said "Remove the second check under line 2, the one that
reads printed output". The words landed on the criterion, no act retired a
test, and `tst_format_filename_shorten_example` stayed at v2 to the end.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import SessionResult, backfill_ruled_refs, init_db, session_commit
from rota.core.predicates import tests_failing as failing_wakes
from rota.core.runner import _as_write
from rota.core.sandbox import build
from rota.roles import prompts
from rota.roles.principal import request_block
from rota.testkit.fixtures import seed_acts

ITEM = "format_filename_doc"
TICKET = "tk_1_format_filename_doc"
CRIT = "cr_1"
GREEN = "tst_format_filename_doc"
RED = "tst_format_filename_shorten_example"
WORDS = ("Remove line 4, the one that reads printed output, because "
         "format_filename prints nothing and only the docstring changes.")


def _message(conn, mid, cause, sender, to, verb, refs, seq, text=None):
    conn.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
                 "to_role, verb, body_refs, body_text, seq) VALUES "
                 "(?, ?, 'm120', ?, ?, ?, ?, ?, ?)",
                 (mid, cause, sender, to, verb, json.dumps(refs), text, seq))


# The Liaison's reading of WORDS: the act `drop` on the red check's row
# (the seam design, pass 4, P6).
DROP_RED = {"act": "drop", "target_kind": "check"}


def _ruling(conn, per_item, words, acts=None):
    conn.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
                 "status) VALUES ('r_m121', 'm120', 'm121', ?, ?, 'landed')",
                 (json.dumps(per_item), words))
    backfill_ruled_refs(conn)
    if acts:
        seed_acts(conn, "r_m121", acts)


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES (?, 'The docstring of format_filename shows "
                 "an example.', 'in_scope', 'approved', 1, 1)", (ITEM,))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, "
                 "'docstring example')", (TICKET, ITEM))
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, ?, "
                 "'the docstring shows a/b/c.txt as c.txt')", (CRIT, TICKET))
    conn.execute("INSERT INTO batches (id, item_id, head_commit, status) "
                 "VALUES ('bg_1', ?, 'abc123', 'running')", (ITEM,))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_1', ?)", (TICKET,))
    for tid, result in ((GREEN, "pass"), (RED, "fail")):
        conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, "
                     "body, version) VALUES (?, 'bg_1', ?, 'tests/test_f.py', "
                     "'assert True', 2)", (tid, CRIT))
        conn.execute("INSERT INTO test_runs (test_id, batch_id, result, "
                     "output, commit_sha) VALUES (?, 'bg_1', ?, 'E out', "
                     "'abc123')", (tid, result))
    page = [ITEM, CRIT, GREEN, RED]
    _message(conn, "m120", None, "liaison", "principal", "present", page, 120)
    _message(conn, "m121", "m120", "principal", "liaison", "converse", page,
             121, WORDS)
    _message(conn, "m122", "m121", "liaison", "terminologist", "relay",
             [CRIT], 122)
    _message(conn, "m123", "m122", "terminologist", "tester", "answer",
             [CRIT, RED], 123)
    # The order his reply saw is the order the page renders: the check
    # lines hold lines 3 and 4.
    order: list[str] = []
    request_block(conn, [ITEM, CRIT], order, [])
    assert order == page
    conn.execute("INSERT INTO config (key, value) VALUES ('order:m121', ?)",
                 (json.dumps(order),))
    conn.commit()
    return conn


def _tester(conn, trigger="m123"):
    sb = build("tester", conn, mode="answer", session_id="s244",
               batch_id="bg_1", allow=prompts.mode_tools("tester", "answer"))
    sb.ctx.trigger = trigger
    return sb


def _commit(conn, sb):
    session_commit(conn, SessionResult(
        session_id="s244", role="tester",
        writes=[_as_write(w) for w in sb.ctx.writes]))


def _checks(conn):
    out: list[str] = []
    request_block(conn, [ITEM, CRIT], [], out)
    return [line for line in out if "check:" in line]


def _reds(conn):
    return [w for w in failing_wakes(conn)
            if "bg_1" in (w.refs or ()) or getattr(w, "batch_id", None) == "bg_1"]


def test_his_remove_of_the_red_check_retires_that_test(db):
    _ruling(db, {ITEM: "approve", CRIT: "approve", GREEN: "approve",
                 RED: "contest"}, WORDS, {RED: DROP_RED})
    db.commit()
    before = _checks(db)
    assert [c.split(".")[0].strip() for c in before] == ["3", "4"]
    assert _reds(db)
    sb = _tester(db)
    sb.call("tests.retire", id=RED)
    _commit(db, sb)
    rows = {r["id"]: (r["retired_by"], r["version"]) for r in db.execute(
        "SELECT id, retired_by, version FROM tests")}
    assert rows[RED] == ("r_m121", 2), "a retire moves no version"
    assert rows[GREEN] == (None, 2)
    assert _checks(db) == [before[0]], "one numbered check, the green one"
    assert _reds(db) == []


def test_a_drop_of_the_criterion_line_retires_no_test(db):
    _ruling(db, {ITEM: "approve", CRIT: "contest"},
            "Remove line 2, it is not what I asked for.")
    db.commit()
    sb = _tester(db)
    with pytest.raises(ValueError, match="no ruling of the principal names"):
        sb.call("tests.retire", id=RED)


def test_a_ruling_with_no_drop_retires_nothing_and_names_the_ruling(db):
    _ruling(db, {ITEM: "approve", CRIT: "approve", GREEN: "approve",
                 RED: "contest"}, "Line 4 should read the docstring instead.")
    db.commit()
    sb = _tester(db)
    with pytest.raises(ValueError, match="r_m121, does not drop its line"):
        sb.call("tests.retire", id=RED)


def test_a_retire_needs_the_wake_that_carries_the_ruling(db):
    _ruling(db, {ITEM: "approve", CRIT: "approve", GREEN: "approve",
                 RED: "contest"}, WORDS, {RED: DROP_RED})
    _message(db, "m130", None, "terminologist", "tester", "answer", [CRIT], 130)
    db.commit()
    sb = _tester(db, trigger="m130")
    with pytest.raises(ValueError, match="does not carry his ruling r_m121"):
        sb.call("tests.retire", id=RED)


def test_only_the_tester_retires_a_test(db):
    _ruling(db, {ITEM: "approve", CRIT: "approve", GREEN: "approve",
                 RED: "contest"}, WORDS, {RED: DROP_RED})
    db.commit()
    sb = build("terminologist", db, mode="criterion_repair", session_id="s243")
    sb.ctx.trigger = "m122"
    with pytest.raises(Exception, match="not in terminologist's working set"):
        sb.call("tests.retire", id=RED)


def _missing(conn):
    from rota.core.predicates import tests_missing

    return [w.detail for w in tests_missing(conn) if w.refs == ("bg_1",)]


def test_a_criterion_whose_only_test_he_retired_owes_a_test_again(db):
    """Review medium 2: a retired test encodes nothing."""
    db.execute("DELETE FROM test_runs WHERE test_id = ?", (GREEN,))
    db.execute("DELETE FROM tests WHERE id = ?", (GREEN,))
    db.commit()
    assert _missing(db) == []
    db.execute("UPDATE tests SET retired_by = 'r_m121' WHERE id = ?", (RED,))
    db.commit()
    assert _missing(db) == [f"without a test: {CRIT}"]


def test_one_live_test_left_owes_no_test(db):
    db.execute("UPDATE tests SET retired_by = 'r_m121' WHERE id = ?", (RED,))
    db.commit()
    assert _missing(db) == []


def test_a_retired_tests_old_red_is_no_red_before(db):
    """Review low 2."""
    from rota.core.db import red_before

    assert RED in red_before(db, "bg_1")
    db.execute("UPDATE tests SET retired_by = 'r_m121' WHERE id = ?", (RED,))
    db.commit()
    assert RED not in red_before(db, "bg_1")
