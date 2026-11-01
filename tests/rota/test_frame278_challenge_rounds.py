"""
Frame 278, pass 2: a count of challenge rounds on one red test bounds the
Developer loop.

The rows copy dry1 after turn 12. `bg_1` runs at head 4fcd6d73, and its one
red test `tst_waited` fails at attempt 8 with `assert False is True`. The
Developer challenged the Tester on `tst_waited` once per session, and the
Tester answered each challenge with a new body. Each re-encode reset the
`tests_failing` key (frame 318), so no key reached its cap. The fixture
holds the rows and not the database file.
"""
from __future__ import annotations

import json

import pytest

from rota.core import predicates as P
from rota.core.db import init_db
from rota.core import scheduler
from rota.core.scheduler import parked, stopped_bouncing

HEAD = "4fcd6d73f6fc05cdcb9fda0770f6cb6928335956"
ITEM = "click_pause_returns_true_on_key"
WAITED = ["tk_1_criteria_waited", "tst_waited", "d_1"]


@pytest.fixture
def dry1(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version, priority) VALUES (?, 'x', 'in_scope', 'approved', "
                 "1, 1, 1)", (ITEM,))
    conn.execute("INSERT INTO batches (id, item_id, status, worktree, head_commit) "
                 "VALUES ('bg_1', ?, 'running', 'wt/bg_1', ?)", (ITEM, HEAD))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_1', ?, 'x')",
                 (ITEM,))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_1', 'tk_1')")
    for crit, test, path in (
            ("tk_1_criteria_waited", "tst_waited",
             "tests/test_termui_tk_1_criteria_waited.py"),
            ("tk_1_criteria_terminal_check", "inh_03a1b2c3",
             "tests/test_termui_tk_1_criteria_terminal_check.py"),
            ("tk_1_criteria_skipped", "tst_skipped",
             "tests/test_termui_tk_1_criteria_skipped.py")):
        conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, 'tk_1', 'x')",
                     (crit,))
        conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                     "VALUES (?, 'bg_1', ?, ?, 'b')", (test, crit, path))
        red = test == "tst_waited"
        conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
                     "result, output, attempt) VALUES (?, 'bg_1', ?, ?, ?, ?, 8)",
                     (f"r_{test}", test, HEAD, "fail" if red else "pass",
                      "E           assert False is True" if red else ""))
    conn.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
                 "reported) VALUES ('developer|tick:batch_start|bg_1', 1, 0, 0)")
    # m93 and its answer m94: the Architect's decision d_1 on `tst_waited`.
    _message(conn, "m93", "developer", "architect", "escalate",
             ["tk_1_criteria_waited", "tst_waited"])
    _message(conn, "m94", "architect", "developer", "answer",
             ["d_1", "tk_1_criteria_waited", "tst_waited"], cause="m93")
    conn.commit()
    return conn


def _message(conn, mid, frm, to, verb, refs, status="answered", cause=None):
    seq = conn.execute("SELECT COALESCE(MAX(seq), 0) + 1 AS n FROM messages"
                       ).fetchone()["n"]
    conn.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
                 "verb, body_refs, round_no, seq, status) "
                 "VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)",
                 (mid, cause, cause or mid, frm, to, verb, json.dumps(refs), seq,
                  status))


def _rounds(conn, n: int, refs=WAITED, first: int = 95) -> None:
    """`n` challenges on `refs`, each answered by a Tester re-encode, as
    m95 to m97 and s200 to s204 on dry1."""
    for k in range(n):
        _message(conn, f"m{first + k}", "developer", "tester", "challenge", refs)
        sid = f"s{200 + 2 * (first - 95 + k)}"
        conn.execute("INSERT INTO sessions (id, role, committed, seq) "
                     "VALUES (?, 'tester', 1, ?)", (sid, 200 + first - 95 + k))
        conn.execute("INSERT INTO receipts (session_id, table_name, row_id, "
                     "new_version) VALUES (?, 'tests', ?, ?)",
                     (sid, refs[1], 5 + first - 95 + k))


def _ladder(conn) -> list[tuple]:
    return [(w.role, w.kind, w.refs) for w in P.exhausted(conn)]


def test_three_challenges_on_the_red_test_climb_the_ladder(dry1):
    """Law 6 says "Budget exhaustion escalates one rung". Three rounds on
    `tst_waited` reach `tick_attempt_cap`, and the first rung names them."""
    _rounds(dry1, 3)
    assert stopped_bouncing(dry1, "bg_1")
    assert _ladder(dry1) == [("developer", "tick:exhausted", ("bg_1",))]
    (wake,) = P.exhausted(dry1)
    # Review p1, L2: below the cap the attempt clause is not the cause.
    assert wake.detail == ("the Developer challenged tst_waited "
                           "3 times, and the Tester wrote versions 5, 6 and 7")


def test_at_the_cap_the_attempt_clause_stays(dry1):
    _rounds(dry1, 3)
    dry1.execute("UPDATE test_runs SET attempt = 10")
    (wake,) = P.exhausted(dry1)
    assert wake.detail == ("attempt 10 of 10; the Developer challenged tst_waited "
                           "3 times, and the Tester wrote versions 5, 6 and 7")


def test_the_count_ends_the_tests_failing_wake(dry1):
    """Review p1, H1: the Developer's wake held the frontier, so
    `quiet_park` never fired below the cap."""
    _rounds(dry1, 2)
    assert [w.refs for w in P.tests_failing(dry1)] == [("bg_1",)]
    _message(dry1, "m97", "developer", "tester", "challenge", WAITED)
    assert P.tests_failing(dry1) == []


def test_a_batch_deferred_on_the_count_stays_parked(dry1):
    """Review p1, H2: `parked` read `given_up` only, so `next_batch` chose
    the deferred batch again."""
    from rota.core.scheduler import next_batch

    _rounds(dry1, 3)
    dry1.execute("UPDATE batches SET status = 'deferred'")
    assert parked(dry1, "bg_1")
    assert scheduler.park_owns(dry1, "bg_1")
    assert "bg_1" not in [r["id"] for r in next_batch(dry1)]
    # A new head commit ends the park, as it lifts a key.
    dry1.execute("UPDATE batches SET head_commit = 'f00dfeed'")
    assert not parked(dry1, "bg_1")
    assert "bg_1" in [r["id"] for r in next_batch(dry1)]


def test_two_challenges_are_below_the_cap(dry1):
    _rounds(dry1, 2)
    assert scheduler.challenged_reds(dry1, "bg_1") == []
    assert not stopped_bouncing(dry1, "bg_1")
    assert _ladder(dry1) == []


def test_a_challenge_on_a_second_test_does_not_count_toward_the_first(dry1):
    """m92 challenged `inh_03a1b2c3`, not `tst_waited`."""
    dry1.execute("UPDATE test_runs SET result = 'fail' WHERE test_id = 'inh_03a1b2c3'")
    _rounds(dry1, 2)
    _rounds(dry1, 1, refs=["tk_1_criteria_terminal_check", "inh_03a1b2c3"], first=92)
    assert not stopped_bouncing(dry1, "bg_1")
    assert _ladder(dry1) == []


def test_an_open_challenge_waits_for_its_round(dry1):
    """The third challenge has no Tester round yet, so it does not count."""
    _rounds(dry1, 2)
    _message(dry1, "m97", "developer", "tester", "challenge", WAITED, status="open")
    assert not stopped_bouncing(dry1, "bg_1")


def test_a_quarantined_key_still_stops_the_batch(dry1):
    """Frame 330's bound holds beside the count."""
    dry1.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
                 "reported) VALUES ('developer|tick:tests_failing|bg_1', 3, 1, 1)")
    assert scheduler.challenged_reds(dry1, "bg_1") == []
    assert stopped_bouncing(dry1, "bg_1")
    assert _ladder(dry1) == [("developer", "tick:exhausted", ("bg_1",))]


def test_the_count_parks_a_running_batch_only(dry1):
    """A deferred batch waits for the principal, and the ladder does not
    wake on it (frame 87)."""
    _rounds(dry1, 3)
    assert parked(dry1, "bg_1")
    dry1.execute("UPDATE batches SET status = 'deferred'")
    assert not stopped_bouncing(dry1, "bg_1")


def test_the_park_page_names_the_looped_check(dry1):
    from rota.roles.principal import _park_page

    _rounds(dry1, 3)
    dry1.execute("UPDATE batches SET status = 'deferred'")
    text, _ = _park_page(dry1, "bg_1", [ITEM])
    assert ("The team challenged the check tests/test_termui_tk_1_criteria_waited.py "
            "3 times, and wrote versions 5, 6 and 7 of it.") in text
