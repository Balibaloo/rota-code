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

from rota.core import config
from rota.core import harness
from rota.core import lifecycle
from rota.core import loop
from rota.core import predicates as P
from rota.core.db import init_db
from rota.llm.llm import Pins, ScriptedBackend
from rota.core.scheduler import frontier


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, "
                 "approval_ver, version) "
                 "VALUES ('i1','ship it','in_scope','approved',1,1)")
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


HEAD = "abc123"


def committed(conn, worktree=None):
    """A batch that has started and has a diff to judge."""
    conn.execute("UPDATE batches SET status='running', head_commit=?, "
                 "worktree=? WHERE id='b1'",
                 (HEAD, str(worktree) if worktree else None))


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
    # And the tests exist first: the frontier's declared order offers
    # `tests_missing` ahead of `batch_start`, because the Tester writes
    # before the Developer's diff exists -- its whole charter. The
    # alphabetical placeholder happened to dispatch the batch first, this
    # test encoded the accident, and the ordering fix surfaced it.
    add_test(db, "tst1", "tests/test_it.py", PASSES)

    ready = [w for w in frontier(db) if w.kind == "tick:batch_start"]
    assert ready, "the batch was never offered"

    # The touch note comes first (P4, 2026-09-03): the predicted set is put
    # to the principal before the batch builds, and the batch is dispatched
    # on the step after. The note's session presents; the Developer's says
    # nothing.
    backend = ScriptedBackend(["TOOL: msg.present_principal(refs=[])", "done",
                               "done."])
    loop.step(db, backend=backend, pins=Pins(model="scripted"))
    assert frontier(db)[0].kind == "tick:batch_start"
    loop.step(db, backend=backend, pins=Pins(model="scripted"))
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
    """Judgements carry the commit they judged — one against a different diff is
    not evidence about this one."""
    conn.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) "
                 "VALUES ('v1','b1',?,?)", (HEAD, verdict))
    conn.execute("INSERT INTO constraints (id, headline) "
                 "VALUES ('k1','no data loss')")
    conn.execute("INSERT INTO findings (id, batch_id, constraint_id, commit_sha, "
                 "status, grain) VALUES ('f1','b1','k1',?,?,'src/db.py')",
                 (HEAD, finding))


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
    # A constraint has to exist for a review to be owed. Without one this said
    # "no structural review yet" -- and it was right that the gate said it, and
    # wrong that the gate could ever open: `findings.find` needs a
    # `constraint_id` and there was none to give, so the batch was finished and
    # unmergeable forever. `needs_structural_review` is now the one place that
    # decides, and both the gate and the predicate ask it.
    (lambda c: (c.execute("INSERT INTO verdicts (id, batch_id, commit_sha, "
                          "result) VALUES ('v1','b1','abc123','pass')"),
                c.execute("INSERT INTO constraints (id, headline) "
                          "VALUES ('k1','no data loss')")),
     "no structural review yet"),
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
    db.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) "
               "VALUES ('v1','b1',?,'pass')", (HEAD,))

    # The constraint comes first now. It always had to exist for the review to
    # mean anything -- a finding references one -- and this test used to fire
    # the tick before creating it, which is the state that could never resolve.
    db.execute("INSERT INTO constraints (id, headline) "
               "VALUES ('k1','no data loss')")
    assert [w for w in frontier(db) if w.kind == "tick:structural_review"]

    db.execute("INSERT INTO findings (id, batch_id, constraint_id, commit_sha, "
               "status, grain) VALUES ('f1','b1','k1',?,'satisfied','src/db.py')",
               (HEAD,))
    assert not [w for w in frontier(db) if w.kind == "tick:structural_review"]


def test_a_project_with_no_constraints_does_not_wait_for_a_review(db):
    """
    The deadlock the seam arc found, from the gate's side.

    Every part of it looked like it was working. The batch is finished, tested
    and judged; `structural_review` fires; Architect is woken and has no legal
    call to make, because `findings.find` requires a `constraint_id` and the
    column is `NOT NULL REFERENCES constraints(id)`. No finding lands, so the
    gate says "no structural review yet", so the tick fires again -- and what
    finally stops it is the livelock guard, reporting a role that did its job.

    On a project with no constraints, which is every project until Architect has
    written a model, no batch could ever merge.
    """
    committed(db)
    db.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) "
               "VALUES ('v1','b1',?,'pass')", (HEAD,))

    assert db.execute("SELECT COUNT(*) n FROM constraints").fetchone()["n"] == 0
    assert not [w for w in frontier(db) if w.kind == "tick:structural_review"],         "nobody should be woken to find against nothing"
    assert lifecycle.mergeable(db, "b1") is None,         "there is nothing to review, so there is nothing to wait for"


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


def test_a_batch_with_no_worktree_records_that_it_could_not_run(db):
    """
    Not "all tests passed" — and not nothing, either. Recording nothing was
    the right distinction with the wrong consequence: the harness predicate
    fires on "this commit has no test_runs row", so a batch with tests and no
    worktree was re-offered every pass, forever. Measured live on cnt_v2r --
    forty harness actions printing "0 test(s)" while a 91-row ruling sat
    undispatched behind them.

    Could not run is a result. An error row per test is the drain the
    predicate already declares, and it flows into `tests_failing`, where a
    Developer is woken to a batch whose state says exactly what is wrong.
    """
    from rota.core.predicates import harness as harness_pred

    committed(db)
    add_test(db, "tst1", "test_x.py", PASSES)
    assert harness_pred(db), "the batch is offered"

    results = harness.run(db, "b1")
    assert results == [("tst1", "error")]
    row = db.execute("SELECT result, output FROM test_runs").fetchone()
    assert row["result"] == "error"
    assert "no worktree" in row["output"]
    assert harness_pred(db) == [], "recorded, so no longer offered"


def test_a_batch_with_no_tests_still_records_nothing(db):
    """The half that stays: no tests is a batch the harness has no business
    with, and `tests_missing` owns that state. The predicate cannot offer it
    either, so recording nothing livelocks nothing."""
    committed(db)
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


# ---------------------------------------------------------------------------
# Exhaustion escalates, never abandons
# ---------------------------------------------------------------------------

def exhaust(conn, attempt=None):
    """Push the batch past loop_cap."""
    cap = attempt or config.get(conn, "loop_cap")
    add_test(conn, "tst_no", "test_no.py", FAILS)
    conn.execute("INSERT INTO test_runs (id, batch_id, test_id, result, attempt) "
                 "VALUES ('r1','b1','tst_no','fail',?)", (cap,))


def test_below_the_cap_it_bounces(db):
    committed(db)
    exhaust(db, attempt=2)
    kinds = {w.kind for w in frontier(db)}
    assert "tick:tests_failing" in kinds
    assert "tick:exhausted" not in kinds


def test_at_the_cap_it_escalates_rather_than_going_quiet(db):
    """
    `tests_failing` stops firing above the cap, which on its own is abandonment
    wearing the clothes of a budget: the work is undone, nothing fires, and the
    system reports itself quiescent.
    """
    committed(db)
    exhaust(db)

    kinds = {w.kind for w in frontier(db)}
    assert "tick:tests_failing" not in kinds, "it should have stopped bouncing"
    assert "tick:exhausted" in kinds, "and it went quiet instead of escalating"


def test_the_ladder_climbs_one_rung_at_a_time(db):
    """
    The usual reason a loop exhausts itself is not knowing who to ask, so
    handing it straight to the principal skips the two people who could have
    answered it.
    """
    committed(db)
    exhaust(db)

    def waiting_on():
        return [w.role for w in frontier(db) if w.kind == "tick:exhausted"]

    assert waiting_on() == ["developer"]

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES "
               "('m1','t1','developer','architect','escalate','[\"b1\"]',1)")
    assert waiting_on() == ["architect"]

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES "
               "('m2','t1','architect','vision_keeper','challenge','[\"b1\"]',2)")
    assert waiting_on() == ["vision_keeper"]


def test_the_ladder_stops_at_vision_keeper(db):
    """
    Above Vision Keeper is the principal, and nothing wakes a person. Reaching them
    is Liaison's `report`, sent by Vision Keeper's own session.
    """
    committed(db)
    exhaust(db)
    for i, (frm, to, verb) in enumerate([
            ("developer", "architect", "escalate"),
            ("architect", "vision_keeper", "challenge"),
            ("vision_keeper", "liaison", "report")], start=1):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                   "body_refs, seq) VALUES (?,'t1',?,?,?,'[\"b1\"]',?)",
                   (f"m{i}", frm, to, verb, i))

    assert not [w for w in frontier(db) if w.kind == "tick:exhausted"]


def test_the_cap_is_the_principals(db):
    """Raising loop_cap buys more bounces before the escalation, which is the
    whole point of it being a setting."""
    committed(db)
    exhaust(db, attempt=10)
    assert [w for w in frontier(db) if w.kind == "tick:exhausted"]

    config.set(db, "loop_cap", 40)
    assert not [w for w in frontier(db) if w.kind == "tick:exhausted"]
    assert [w for w in frontier(db) if w.kind == "tick:tests_failing"]


# ---------------------------------------------------------------------------
# The loop is a loop
# ---------------------------------------------------------------------------

def judged(conn, commit, *, verdict="pass", finding="satisfied", tests="pass"):
    """One full round of judgement against one commit."""
    conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) "
                 "VALUES (?,'b1','tst1',?,?)", (f"r_{commit}", commit, tests))
    conn.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) "
                 "VALUES (?,'b1',?,?)", (f"v_{commit}", commit, verdict))
    if finding:
        conn.execute("INSERT INTO findings (id, batch_id, constraint_id, commit_sha, "
                     "status, grain) VALUES (?,'b1','k1',?,?,'src/db.py')",
                     (f"f_{commit}", commit, finding))


def test_a_failed_batch_can_still_pass(db):
    """
    Fail, fix, pass. The case that would have caught the whole class.

    Each gate guarded itself with "does a row exist for this batch", so each
    fired once per batch ever: after one failed verdict `review` never re-fired,
    the harness never re-ran, and the Developer bounced on `verdict_failed`
    until the livelock guard tripped. The batch could not converge.
    """
    committed(db)                                   # head_commit = abc123
    add_test(db, "tst1", "test_it.py", PASSES)
    db.execute("INSERT INTO constraints (id, headline) "
               "VALUES ('k1','no data loss')")

    judged(db, "abc123", verdict="fail", finding=None)
    assert lifecycle.mergeable(db, "b1") == "verdict fail"

    # The Developer fixes it and commits.
    db.execute("UPDATE batches SET head_commit='def456' WHERE id='b1'")

    kinds = {w.kind for w in frontier(db)}
    assert "do:harness" in kinds, f"the fix was never re-tested: {kinds}"

    judged(db, "def456", verdict="pass", finding="satisfied")
    assert lifecycle.mergeable(db, "b1") is None
    assert [w.kind for w in frontier(db) if w.kind == "do:merge"]


def test_each_gate_re_fires_on_a_new_commit(db):
    """Named individually, so a regression says which gate went back to
    once-per-batch."""
    committed(db)
    add_test(db, "tst1", "test_it.py", PASSES)
    db.execute("INSERT INTO constraints (id, headline) "
               "VALUES ('k1','no data loss')")

    for gate, setup in (
        ("do:harness", lambda: None),
        ("tick:review", lambda: db.execute(
            "INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) "
            "VALUES ('r2','b1','tst1','xyz789','pass')")),
        ("tick:structural_review", lambda: db.execute(
            "INSERT INTO verdicts (id, batch_id, commit_sha, result) "
            "VALUES ('v2','b1','xyz789','pass')")),
    ):
        db.execute("UPDATE batches SET head_commit='xyz789' WHERE id='b1'")
        setup()
        assert gate in {w.kind for w in frontier(db)}, \
            f"{gate} did not fire for a commit it had not judged"


def test_a_stale_pass_does_not_merge(db):
    """
    A verdict against an older diff is not evidence about the one on disk.
    Without the commit stamp this merges a change nobody judged, which is worse
    than not merging at all.
    """
    committed(db)
    add_test(db, "tst1", "test_it.py", PASSES)
    db.execute("INSERT INTO constraints (id, headline) "
               "VALUES ('k1','no data loss')")
    judged(db, "abc123")
    assert lifecycle.mergeable(db, "b1") is None

    db.execute("UPDATE batches SET head_commit='newer' WHERE id='b1'")
    assert lifecycle.mergeable(db, "b1") == "no verdict"
    assert not [w for w in frontier(db) if w.kind == "do:merge"]


def test_the_judgement_records_what_it_judged(db):
    """Filled by the system. Critic judges a diff and has no reason to know its
    sha; asking would add an argument it could get wrong."""
    from rota.core.sandbox import build

    committed(db)
    sb = build("critic", db)
    sb.call("verdicts.emit", batch_id="b1", result="pass")

    values = sb.ctx.writes[-1][2]
    assert values["commit_sha"] == "abc123"


# ---------------------------------------------------------------------------
# Revocation, the half that was missing
# ---------------------------------------------------------------------------

def _revoked_wakes(db):
    from rota.core.predicates import reopen
    return reopen(db)


def test_a_running_batch_whose_item_lost_approval_reopens(tmp_path):
    """
    `batch_start` refused to start a batch whose item was no longer approved,
    and nothing touched one already running. The Developer went on building
    against a withdrawn specification and Critic judged it against withdrawn
    criteria — the one case where work is actively being done against something
    nobody wants.
    """
    from rota.core.db import init_db

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) "
               "VALUES ('i1','x','in_scope','approved',1,1)")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','running')")
    assert not _revoked_wakes(db), "an approved item is not a revocation"

    db.execute("UPDATE items SET approval='draft', version=2 WHERE id='i1'")

    wakes = _revoked_wakes(db)
    assert [w.role for w in wakes] == ["developer"]
    assert wakes[0].kind == "tick:reopen"
    assert set(wakes[0].refs) == {"b1", "i1"}


def test_an_approval_that_predates_the_amendment_also_reopens(tmp_path):
    """Approved, then amended, then never re-approved: `approval` still reads
    'approved' and means nothing, because it approved an older version."""
    from rota.core.db import init_db

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) "
               "VALUES ('i1','x','in_scope','approved',1,3)")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','running')")

    assert _revoked_wakes(db), "approval_ver behind version is a stale approval"


def test_it_goes_quiet_once_the_election_is_in_flight(tmp_path):
    """The Developer answers with `msg.elect_vision_keeper`. Asking again while
    that message is unread would put the same decision on the frontier every
    pass, which is how a fix band becomes a spin."""
    from rota.core.db import init_db

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) "
               "VALUES ('i1','x','in_scope','draft',1,2)")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','running')")
    assert _revoked_wakes(db)

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES "
               "('m1','t1','developer','vision_keeper','elect','[\"b1\"]',1)")
    assert not _revoked_wakes(db)

def test_a_finding_against_an_id_that_is_no_constraint_is_a_tool_error(db):
    """
    Night 64 (2026-09-14): the Architect filed findings against inherited
    test ids as constraints. The tool said OK and the foreign key refused the
    whole session at commit, three times. Law 14 belongs at the door.
    """
    from rota.core.sandbox import build
    db.execute("INSERT INTO constraints (id, headline) VALUES ('k1','no data loss')")
    db.commit()
    sb = build("architect", db, batch_id="b1")
    with pytest.raises(ValueError, match="constraints"):
        sb.call("findings.find", id="f1", batch_id="b1",
                constraint_id="inh_51d478df", status="violated", grain="src/x.py")
    out = sb.call("findings.find", id="f1", batch_id="b1",
                  constraint_id="k1", status="violated", grain="src/x.py")
    assert out["id"] == "f1"
