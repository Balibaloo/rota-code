"""
The delivery loop, end to end — and it is all machine, no model.

Everything from a committed diff to a merged batch is mechanical: run the tests,
judge intent, check the constraints, merge. The only judgement in it belongs to
Critic and Architect, and both arrive as rows the loop reads rather than as
decisions the loop makes.

That is why this file has no backend in it. If any of these steps needed a model
call, the design would be wrong.
"""
from __future__ import annotations

import pytest

from rota import config, harness, lifecycle, loop
from rota import predicates as P
from rota.db import init_db
from rota.llm import Pins, ScriptedBackend
from rota.scheduler import frontier


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance, approval, "
                 "approval_ver, version) "
                 "VALUES ('i1','ship it','in_scope','decided','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i1','do it')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) "
                 "VALUES ('c1','t1','it does the thing')")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','pending')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','t1')")
    return conn


PASSES = "def test_it():\n    assert True\n"
FAILS = "def test_it():\n    assert False\n"


def add_test(conn, test_id, path, body):
    r"""
    Parameterised, because SQLite does not interpret `\n` in a string literal.

    The first version of these cases inlined the bodies in SQL and wrote files
    containing a literal backslash-n, so every test came back `error` — which is
    at least the right word for it, and is the distinction `_run_one` exists to
    draw: `fail` says the code is wrong, `error` says the test could not answer.
    """
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES (?, 'b1', 'c1', ?, ?)", (test_id, path, body))


def committed(conn, worktree=None):
    """A batch that has started and has a diff to judge."""
    conn.execute("UPDATE batches SET status='running', head_commit='abc123', "
                 "worktree=? WHERE id='b1'", (str(worktree) if worktree else None,))


# ---------------------------------------------------------------------------
# The states that could not be reached
# ---------------------------------------------------------------------------

def test_dispatching_a_batch_marks_it_running(db):
    """
    It was declared, three predicates waited on it, and nothing set it — the
    delivery loop was gated on a value that could not occur.

    The loop sets it at *dispatch*, not from inside the session: `batch_start`
    refuses while anything is running, so leaving it to the session would let a
    second batch start in the gap.
    """
    # Annotating comes first: a batch is predicted before it is started, so the
    # touch set exists by the time there is a diff to compare it against.
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
               "VALUES ('b1','src/thing.py','path')")

    ready = [w for w in frontier(db) if w.kind == "tick:batch_start"]
    assert ready, "the batch was never offered"

    loop.step(db, backend=ScriptedBackend(["done."]), pins=Pins(model="scripted"))
    assert db.execute(
        "SELECT status FROM batches WHERE id='b1'").fetchone()["status"] == "running"


def test_deferring_keeps_the_worktree_and_drops_the_checkpoint(db):
    """
    Commit-first is what bounds the loss on preemption: an uncommitted change
    never existed, and a committed one survives as deferred work. The checkpoint
    does not survive — a deferred batch resumes cold.
    """
    committed(db)
    db.execute("INSERT INTO sessions (id, role, seq) VALUES ('s1','developer',1)")
    db.execute("INSERT INTO checkpoints (session_id, role, batch_id, working_set, valid) "
               "VALUES ('s1','developer','b1','[]',1)")

    lifecycle.defer(db, "b1")

    row = db.execute("SELECT status, worktree, head_commit FROM batches "
                     "WHERE id='b1'").fetchone()
    assert row["status"] == "deferred"
    assert row["head_commit"] == "abc123", "the commits went with the checkpoint"
    assert db.execute(
        "SELECT valid FROM checkpoints WHERE session_id='s1'").fetchone()["valid"] == 0


# ---------------------------------------------------------------------------
# The merge gate
# ---------------------------------------------------------------------------

def reviewed(conn, *, verdict="pass", finding="satisfied"):
    conn.execute("INSERT INTO verdicts (id, batch_id, result) VALUES ('v1','b1',?)",
                 (verdict,))
    conn.execute("INSERT INTO constraints (id, headline, provenance) "
                 "VALUES ('k1','no data loss','decided')")
    conn.execute("INSERT INTO findings (id, batch_id, constraint_id, status, grain) "
                 "VALUES ('f1','b1','k1',?,'src/db.py')", (finding,))


def test_a_clean_batch_merges_without_waking_anyone(db):
    """
    Merging is not a judgement. The verdict already made it and the findings
    already cleared it, so dispatching a session to press the button would be
    inventing a decision to have.
    """
    committed(db)
    reviewed(db)

    assert lifecycle.mergeable(db, "b1") is None
    actions = [w for w in frontier(db) if w.kind == "do:merge"]
    assert actions and actions[0].role == "", "a merge should wake nobody"

    s = loop.step(db, backend=ScriptedBackend([]), pins=Pins(model="scripted"))
    assert "merged" in s.note
    assert db.execute(
        "SELECT status FROM batches WHERE id='b1'").fetchone()["status"] == "merged"


@pytest.mark.parametrize("setup,reason", [
    (lambda c: None, "no verdict"),
    (lambda c: reviewed(c, verdict="fail"), "verdict fail"),
    (lambda c: c.execute("INSERT INTO verdicts (id, batch_id, result) "
                         "VALUES ('v1','b1','pass')"), "no structural review yet"),
    (lambda c: reviewed(c, finding="violated"), "1 constraint(s) violated"),
])
def test_the_gate_says_why_it_is_shut(db, setup, reason):
    """
    A reason rather than a boolean, so the loop can report why a finished-looking
    batch is sitting there instead of leaving it to be inferred from absence.
    """
    committed(db)
    setup(db)
    assert lifecycle.mergeable(db, "b1") == reason


def test_review_mode_holds_a_clean_batch(db):
    """The principal's setting, not a phase: trust should not increase on a
    schedule."""
    committed(db)
    reviewed(db)
    config.set(db, "merge_gate", "review")

    assert lifecycle.mergeable(db, "b1") == "waiting on the principal's review"
    assert not [w for w in frontier(db) if w.kind == "do:merge"]

    config.set(db, "merge_gate", "auto")
    assert [w for w in frontier(db) if w.kind == "do:merge"]


def test_structural_review_runs_once(db):
    """
    It fired on every reviewed batch forever, because nothing excluded batches
    that already carried findings. The loop guard catches that — after two
    wasted sessions, and only if someone reads the trace.
    """
    committed(db)
    db.execute("INSERT INTO verdicts (id, batch_id, result) VALUES ('v1','b1','pass')")
    assert [w for w in frontier(db) if w.kind == "tick:structural_review"]

    db.execute("INSERT INTO constraints (id, headline, provenance) "
               "VALUES ('k1','no data loss','decided')")
    db.execute("INSERT INTO findings (id, batch_id, constraint_id, status, grain) "
               "VALUES ('f1','b1','k1','satisfied','src/db.py')")
    assert not [w for w in frontier(db) if w.kind == "tick:structural_review"]


# ---------------------------------------------------------------------------
# The harness
# ---------------------------------------------------------------------------

def test_the_harness_records_what_the_tests_said(db, tmp_path):
    """
    Mechanical, like recording an entry. Routing a boolean through a model would
    introduce a paraphrase risk over the one thing in the system that cannot be
    wrong about itself.
    """
    worktree = tmp_path / "wt"
    worktree.mkdir()
    committed(db, worktree)
    add_test(db, "tst_ok", "test_ok.py", PASSES)
    add_test(db, "tst_no", "test_no.py", FAILS)

    results = dict(harness.run(db, "b1"))
    assert results == {"tst_ok": "pass", "tst_no": "fail"}

    rows = {r["test_id"]: r["result"] for r in
            db.execute("SELECT test_id, result FROM test_runs")}
    assert rows == {"tst_ok": "pass", "tst_no": "fail"}


def test_a_batch_with_no_worktree_records_nothing(db):
    """
    Not "all tests passed" — a batch that has not started. Every predicate
    downstream reads that difference, and an empty result set that means "green"
    is how a system ships untested code.
    """
    committed(db)
    add_test(db, "tst1", "test_x.py", PASSES)

    assert harness.run(db, "b1") == []
    assert db.execute("SELECT COUNT(*) n FROM test_runs").fetchone()["n"] == 0


def test_a_failing_harness_blocks_the_merge(db, tmp_path):
    """The cheapest gate, and the first. It runs before anything costs a model
    call, which is what makes loop_cap bounces affordable."""
    worktree = tmp_path / "wt"
    worktree.mkdir()
    committed(db, worktree)
    add_test(db, "tst_no", "test_no.py", FAILS)
    reviewed(db)

    harness.run(db, "b1")
    assert lifecycle.mergeable(db, "b1") == "1 test(s) not passing"


def test_the_harness_is_an_action_not_a_wake(db, tmp_path):
    worktree = tmp_path / "wt"
    worktree.mkdir()
    committed(db, worktree)
    add_test(db, "tst_ok", "test_ok.py", PASSES)

    assert P.REGISTRY["harness"].wakes == P.SCHEDULER
    s = loop.step(db, backend=ScriptedBackend([]), pins=Pins(model="scripted"))
    assert s.wake.kind == "do:harness" and s.wake.role == ""
    assert "1 test(s), 0 not passing" in s.note
