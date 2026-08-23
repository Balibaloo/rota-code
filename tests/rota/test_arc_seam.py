"""
The seam: one sentence, one database, one merged batch.

Two end-to-end arcs already exist and neither crosses the join between them.
`test_vertical_slice` is explicitly "no Developer" and stops at an approved
item. `test_arc_synthetic` runs an understanding arc that ends by asserting
`tick:slicing` fires, then a delivery arc that begins by *hand-inserting* the
approved item and glossary term that arc would have produced -- so the edge
between the halves is asserted at one end, re-created at the other, and never
traversed. `test_delivery` starts later still, from a diff that already exists.

Everything in the middle is therefore covered a piece at a time and never as a
sequence: approved item -> ticket -> criteria -> batch -> tests -> code ->
commit -> harness -> verdict -> merge. On a real repository that sequence is
the product, and nothing here has ever run it.

Canned completions, real machine, real git. This is the wiring test for the
join, not a claim that any role reasons well -- the same division `test_arc_
synthetic` draws, extended over the part it stops short of.
"""
from __future__ import annotations

import pytest

from rota.core import lifecycle, predicates
from rota.core.db import init_db
from rota.core.runner import run_session
from rota.core.scheduler import Wake, frontier, predicate_wakes
from rota.llm.llm import Pins, ScriptedBackend
from rota.roles.principal import record_entry
from rota.testkit import gitfixture

PINS = Pins(model="scripted", temperature=0.0, num_ctx=4096)
SENTENCE = "add a button so people can delete their account"


def drive(conn, wake: Wake, script: list[str], **kw):
    outcome = run_session(conn, wake, backend=ScriptedBackend(script + ["done"]),
                          pins=PINS, **kw)
    assert outcome.committed, f"{wake} failed: {outcome.errors}"
    return outcome


def tick(conn, kind: str) -> Wake:
    """The next wake of a kind, or a failure that says the seam broke here."""
    wakes = [w for w in predicate_wakes(conn) if w.kind == kind]
    assert wakes, (
        f"{kind} never fired. The previous step committed and the state it "
        f"left did not derive the next one, which is the join this file exists "
        f"to check")
    return wakes[0]


@pytest.fixture
def repo(tmp_path):
    r = gitfixture.make(tmp_path, name="seam")
    yield r
    gitfixture.cleanup(r)


@pytest.fixture
def db(tmp_path, repo):
    conn = init_db(tmp_path / "rota.db")
    # Straight into the table: `project_root` is deliberately not a declared
    # setting, because it is a fact about which repository this database is
    # about rather than a cap the principal tunes.
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
                 (str(repo.root),))
    return conn


def test_one_sentence_becomes_a_merged_batch(db, repo):
    """
    The whole product, once, in order. Each step is a real session through the
    real scheduler; only the completions are canned.
    """
    # --- the principal says something ---------------------------------------
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "seq) VALUES ('m_in','t1','principal','liaison','converse',1)")
    record_entry(db, "m_in", SENTENCE)

    drive(db, Wake("liaison", "message", "m_in", detail="converse"), [
        f"TOOL: brief.segment(id='s1', span_entry='e_m_in', span_start=0, "
        f"span_end={len(SENTENCE)}, text='{SENTENCE}')",
        "TOOL: msg.confirm_principal(refs=['s1'])",
    ])

    # --- they approve it, and it goes out to the three shape roles -----------
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "seq) VALUES ('m_ok','t1','principal','liaison','verdict',3)")
    drive(db, Wake("liaison", "message", "m_ok", detail="verdict"), [
        "TOOL: brief.ratify(id='s1')",
        "TOOL: msg.deliver_vision_keeper(refs=['s1'])",
        "TOOL: msg.deliver_terminologist(refs=['s1'])",
        "TOOL: msg.deliver_architect(refs=['s1'])",
    ])

    gk = db.execute("SELECT id FROM messages WHERE to_role='vision_keeper' "
                    "AND verb='deliver'").fetchone()["id"]
    drive(db, Wake("vision_keeper", "message", gk, detail="deliver"), [
        "TOOL: problem.assert(id='i1', text='users can delete their account', "
        "kind='in_scope')",
    ])

    te = db.execute("SELECT id FROM messages WHERE to_role='terminologist' "
                    "AND verb='deliver'").fetchone()["id"]
    drive(db, Wake("terminologist", "message", te, detail="deliver"), [
        "TOOL: glossary.amend(id='g1', term='account', "
        "sense_short='the login identity')",
    ])

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "seq) VALUES ('m_sign','t1','liaison','vision_keeper','relay',20)")
    drive(db, Wake("vision_keeper", "message", "m_sign", detail="relay"), [
        "TOOL: problem.set_approval(id='i1', approval='approved')",
    ])

    # === the seam ===========================================================
    # Nothing is inserted from here on. Every wake below has to be *derived*
    # from what the step before it committed.

    drive(db, tick(db, "tick:slicing"), [
        "TOOL: tickets.slice(id='tk1', item_id='i1', text='add a delete button')",
    ])

    drive(db, tick(db, "tick:criteria"), [
        "TOOL: criteria.specify(id='c1', ticket_id='tk1', "
        "text='deleting an account tombstones it', term_refs=['g1'])",
    ])

    grouping = tick(db, "tick:grouping")
    drive(db, Wake("architect", "tick:grouping", refs=grouping.refs), [
        "TOOL: batches.group(id='b1', item_id='i1', ticket_ids=['tk1'])",
    ])

    # --- dispatch: the scheduler makes the worktree, not the role ------------
    start = tick(db, "tick:batch_start")
    lifecycle.start(db, "b1")
    worktree = db.execute(
        "SELECT worktree FROM batches WHERE id='b1'").fetchone()["worktree"]
    assert worktree, "a dispatched batch must have somewhere to work"

    # --- tests before code, which is the whole point of the ordering ---------
    drive(db, tick(db, "tick:tests_missing"), [
        "TOOL: tests.encode(id='t1', criterion_id='c1', path='test_delete.py', "
        "body='from seam import delete_account\n"
        "def test_tombstones():\n    assert delete_account(1) == \"tombstoned\"')",
    ], batch_id="b1")

    assert db.execute("SELECT COUNT(*) n FROM tests").fetchone()["n"] == 1

    # --- the Developer, woken by the same dispatch tick ----------------------
    # `batch_start` wakes Developer; the tests above were written by Tester in
    # `tests_missing`, which the same dispatch derived. Order matters and is
    # the design's: a test written after the code encodes what the code does.
    drive(db, Wake("developer", "tick:batch_start", refs=("b1",)), [
        "TOOL: code.write(path='seam.py', text='def delete_account(account_id):"
        "\n    return \"tombstoned\"\n')",
        "TOOL: code.commit(message='tombstone an account on delete')",
    ], batch_id="b1")

    head = db.execute(
        "SELECT head_commit FROM batches WHERE id='b1'").fetchone()["head_commit"]
    assert head, "code.commit must stamp the batch with what it committed"

    # --- the harness: the one gate with no judgement in it -------------------
    h = tick(db, "do:harness")
    from rota.core import harness
    results = harness.run(db, "b1")
    assert results, "the harness ran nothing"

    runs = db.execute(
        "SELECT result, commit_sha FROM test_runs WHERE batch_id='b1'").fetchall()
    assert runs, "a harness run must leave a row"
    assert all(r["commit_sha"] == head for r in runs), \
        "a test result is about a commit; unstamped it cannot gate anything"
    assert all(r["result"] == "pass" for r in runs), \
        f"the code satisfies the test: {[dict(r) for r in runs]}"

    # --- Critic judges, and it is judging *this* commit ----------------------
    review = tick(db, "tick:review")
    drive(db, Wake("critic", "tick:review", refs=("b1",)), [
        "TOOL: criteria.load(batch_id='b1')",
        "TOOL: tests.load(batch_id='b1')",
        "TOOL: verdicts.emit(batch_id='b1', result='pass')",
    ], batch_id="b1")

    verdict = db.execute(
        "SELECT result, commit_sha FROM verdicts WHERE batch_id='b1'").fetchone()
    assert verdict["result"] == "pass"
    assert verdict["commit_sha"] == head, \
        "a judgement is of a commit, or it is a judgement of nothing"

    # --- structural review, on a project that has no constraints ------------
    #
    # This is what the seam test was written to find, and it is only visible
    # from here: every earlier test either starts after the gate or never
    # reaches it.
    #
    # `structural_review` fires for any batch with a passing verdict and no
    # findings. It does not check whether there is anything to review -- its own
    # docstring says "a diff whose grains intersect constraint bindings", and
    # the query says no such thing. On a project with no constraints, which is
    # every project before Architect has written a model, there is nothing for
    # Architect to find *against*: `findings.find` requires a `constraint_id`
    # and the column is `NOT NULL REFERENCES constraints(id)`.
    #
    # So: the tick fires, Architect is woken, it has no legal call to make, no
    # finding lands, `mergeable` says "no structural review yet", and the tick
    # fires again. The work is finished, correct, tested, judged, and it cannot
    # land.
    assert db.execute("SELECT COUNT(*) n FROM constraints").fetchone()["n"] == 0

    from rota.core.lifecycle import needs_structural_review
    assert not needs_structural_review(db, "b1"), (
        "there are no constraints, so there is nothing this batch could "
        "violate and nothing for Architect to find")

    assert not [w for w in predicate_wakes(db)
                if w.kind == "tick:structural_review"], (
        "Architect must not be woken to record a finding it has no constraint "
        "to record against -- that wake used to fire forever")

    assert lifecycle.mergeable(db, "b1") is None, (
        f"green tests, a passing verdict, and no constraint in the project to "
        f"check against -- the gate must not wait for a review that cannot "
        f"happen: {lifecycle.mergeable(db, 'b1')}")

    lifecycle.merge(db, "b1")
    assert db.execute("SELECT status FROM batches WHERE id='b1'"
                      ).fetchone()["status"] == "merged"

    # --- and the system is finished ------------------------------------------
    assert not [w for w in predicate_wakes(db)
                if w.kind == "tick:structural_review"],         "a merged batch still being asked for a structural review"


# ---------------------------------------------------------------------------
# The other direction: the gate must still be a gate.
# ---------------------------------------------------------------------------

@pytest.fixture
def gated(tmp_path):
    """A batch that has passed its tests and its verdict, at a known commit."""
    conn = init_db(tmp_path / "gate.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance, approval, "
                 "approval_ver, version) VALUES "
                 "('i1','x','in_scope','decided','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('b1','i1','running','sha1')")
    conn.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) "
                 "VALUES ('v1','b1','sha1','pass')")
    return conn


def test_a_global_constraint_still_demands_a_review(gated):
    """
    Zero bindings means global, which the schema states outright: "missing
    bindings must always mean *always visible*, never *invisible*". A batch
    cannot skip a constraint by touching nothing it was bound to, because it
    was bound to nothing.
    """
    gated.execute("INSERT INTO constraints (id, headline, provenance) "
                  "VALUES ('k1','the store layer is synchronous','observed')")

    assert lifecycle.needs_structural_review(gated, "b1")
    assert lifecycle.mergeable(gated, "b1") == "no structural review yet"


def test_a_bound_constraint_demands_a_review_when_the_batch_meets_it(gated):
    """And does not, when it does not — which is the whole point of binding."""
    gated.execute("INSERT INTO constraints (id, headline, provenance, is_global) "
                  "VALUES ('k1','auth must go through the gateway','observed',0)")
    gated.execute("INSERT INTO constraint_bindings (constraint_id, grain, "
                  "grain_kind) VALUES ('k1','src/auth.py','path')")

    gated.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
                  "VALUES ('b1','src/billing.py','path')")
    assert not lifecycle.needs_structural_review(gated, "b1"), \
        "a constraint bound elsewhere is not this batch's business"

    gated.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
                  "VALUES ('b1','src/auth.py','path')")
    assert lifecycle.needs_structural_review(gated, "b1")
    assert lifecycle.mergeable(gated, "b1") == "no structural review yet"


def test_an_unknown_touch_set_is_reviewed_rather_than_assumed_clean(gated):
    """
    Erring toward a review costs one session. Erring away from it merges a
    change nobody checked, and `batch_touch` is a *prediction* — Architect may
    simply not have annotated this batch.
    """
    gated.execute("INSERT INTO constraints (id, headline, provenance, is_global) "
                  "VALUES ('k1','auth must go through the gateway','observed',0)")
    gated.execute("INSERT INTO constraint_bindings (constraint_id, grain, "
                  "grain_kind) VALUES ('k1','src/auth.py','path')")

    assert gated.execute("SELECT COUNT(*) n FROM batch_touch").fetchone()["n"] == 0
    assert lifecycle.needs_structural_review(gated, "b1"), \
        "nothing predicted is not the same as nothing touched"


def test_a_violated_finding_still_stops_the_merge(gated):
    """The fix touches when a review is *required*, never what one decides."""
    gated.execute("INSERT INTO constraints (id, headline, provenance) "
                  "VALUES ('k1','the store layer is synchronous','observed')")
    gated.execute("INSERT INTO findings (id, batch_id, constraint_id, "
                  "commit_sha, status, grain) VALUES "
                  "('f1','b1','k1','sha1','violated','src/store.py')")

    assert lifecycle.mergeable(gated, "b1") == "1 constraint(s) violated"


def test_a_failing_test_comes_back_and_the_second_commit_is_what_merges(db, repo):
    """
    The loop-back, which the happy path cannot show.

    Every arc in this suite goes forward. The delivery loop's whole shape is
    that it does not: a failing test bounces to the Developer without waiting
    for review, because a test costs a subprocess and a Critic session costs a
    model call. Nothing had ever run that bounce as a sequence, so nothing
    checked the part that makes it safe -- that the judgements which pass are
    about the commit that merges, and not about the one that failed.

    Written the same way as the arc above: nothing is inserted after the batch
    starts, and every wake has to be derived.
    """
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('i1','users can delete their account','in_scope','decided',"
               "'approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) "
               "VALUES ('tk1','i1','add a delete button')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) VALUES "
               "('c1','tk1','deleting an account tombstones it','[]')")
    db.execute("INSERT INTO batches (id, item_id, status) "
               "VALUES ('b1','i1','pending')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) "
               "VALUES ('b1','tk1')")
    lifecycle.start(db, "b1")

    drive(db, tick(db, "tick:tests_missing"), [
        "TOOL: tests.encode(id='t1', criterion_id='c1', path='test_delete.py', "
        "body='from seam import delete_account\n"
        "def test_tombstones():\n    assert delete_account(1) == \"tombstoned\"')",
    ], batch_id="b1")

    # --- a first attempt that does not satisfy it ---------------------------
    drive(db, Wake("developer", "tick:batch_start", refs=("b1",)), [
        "TOOL: code.write(path='seam.py', text='def delete_account(account_id):"
        "\n    return \"deleted\"\n')",
        "TOOL: code.commit(message='delete an account')",
    ], batch_id="b1")

    from rota.core import harness
    bad = db.execute(
        "SELECT head_commit FROM batches WHERE id='b1'").fetchone()["head_commit"]
    harness.run(db, "b1")
    assert db.execute(
        "SELECT result FROM test_runs WHERE batch_id='b1' AND commit_sha=?",
        (bad,)).fetchone()["result"] == "fail", "the code does not tombstone"

    # It goes back to the Developer, and it does *not* go to Critic: a model
    # call on a diff whose tests are red is spent knowing that already.
    assert tick(db, "tick:tests_failing").refs == ("b1",)
    assert not [w for w in predicate_wakes(db) if w.kind == "tick:review"], \
        "a red harness must not reach the expensive gate"

    # --- the fix -------------------------------------------------------------
    drive(db, tick(db, "tick:tests_failing"), [
        "TOOL: code.write(path='seam.py', text='def delete_account(account_id):"
        "\n    return \"tombstoned\"\n')",
        "TOOL: code.commit(message='tombstone rather than delete')",
    ], batch_id="b1")

    good = db.execute(
        "SELECT head_commit FROM batches WHERE id='b1'").fetchone()["head_commit"]
    assert good != bad, "the fix has to be a new commit or nothing has changed"

    harness.run(db, "b1")
    assert db.execute(
        "SELECT result FROM test_runs WHERE batch_id='b1' AND commit_sha=?",
        (good,)).fetchone()["result"] == "pass"

    # The failing run is still on file against the commit it judged, and does
    # not follow the batch forward. That is the whole reason results are stamped.
    assert lifecycle.mergeable(db, "b1") == "no verdict", \
        f"the old failure must not still be gating: {lifecycle.mergeable(db, 'b1')}"

    drive(db, tick(db, "tick:review"), [
        "TOOL: criteria.load(batch_id='b1')",
        "TOOL: tests.load(batch_id='b1')",
        "TOOL: verdicts.emit(batch_id='b1', result='pass')",
    ], batch_id="b1")

    assert db.execute(
        "SELECT commit_sha FROM verdicts WHERE batch_id='b1'"
    ).fetchone()["commit_sha"] == good, "the verdict must judge the fix"

    assert lifecycle.mergeable(db, "b1") is None
    lifecycle.merge(db, "b1")
    assert db.execute("SELECT status FROM batches WHERE id='b1'"
                      ).fetchone()["status"] == "merged"
