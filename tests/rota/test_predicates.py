"""
Predicates, and the hard constraint that none may be missing.

The load-bearing case is `test_lint_catches_a_dead_end`: a lint nobody has proved
can fail is a lint you are trusting rather than using.
"""
from __future__ import annotations

import pytest

from rota.core import predicates as P
from rota.core.db import init_db
from rota.testkit.fixtures import refs_from_columns


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def test_every_lifecycle_state_has_a_way_out():
    """
    The hard constraint.

    A state that is neither drained nor declared terminal is a place work stops
    while the system reports itself finished — invisible to every other check,
    because quiescence is defined as "no predicate fires".
    """
    assert P.check_terminal_states() == []


def test_lint_catches_a_dead_end(monkeypatch):
    """Remove a predicate's drain and the lint must notice."""
    original = P.REGISTRY["contested"]
    monkeypatch.setitem(
        P.REGISTRY, "contested",
        P.Predicate(name="contested", wakes=original.wakes, drains=(),
                    fn=original.fn))

    problems = P.check_terminal_states()
    assert any("items.approval = 'contested'" in p for p in problems), problems


def test_lint_catches_a_new_state_with_no_exit(monkeypatch):
    """Adding a state to the schema without a way out fails the build.

    'abandoned' was the fabricated no-exit example until the cancel build
    made it a real, declared-terminal state -- the canary needs a state the
    build genuinely does not know."""
    monkeypatch.setattr(
        P, "schema_states",
        lambda: {("batches", "status"): ["pending", "running", "deferred",
                                         "merged", "limbo"]})
    problems = P.check_terminal_states()
    assert any("'limbo'" in p for p in problems), problems


def test_every_predicate_wakes_a_real_role():
    assert P.check_predicates_wake_real_roles() == []


def test_the_four_dead_ends_are_drained():
    """
    The specific holes the sweep found. Named individually so a regression says
    which one came back.
    """
    drained = P.drained_states()
    for state in [
        ("items", "approval", "contested"),          # the principal's rejection
        ("statements", "status", "contradicted"),    # two statements conflict
        ("verdicts", "result", "pass"),              # nothing merged it
        ("messages", "status", "quarantined"),       # the system gave up, silently
    ]:
        assert state in drained or state in P.TERMINAL, f"{state} is a dead end again"


def test_open_messages_are_drained_by_a_declared_predicate():
    """
    The frontier used to be "tips ∪ predicates", which put its definition in two
    places and made the tips half invisible to checks written against the other.
    """
    assert ("messages", "status", "open") in P.drained_states()


def test_terminal_states_carry_a_reason():
    """A terminal state is a claim that nothing further is owed. Claims need
    reasons; an unexplained one is usually an oversight wearing a decision."""
    missing = [k for k, why in P.TERMINAL.items() if not why.strip()]
    assert not missing, missing


def test_delivery_loop_is_predicated(db):
    """
    It had one predicate — batch_start — and four dead ends. The second half of
    the system could not turn without a message arriving from somewhere.
    """
    names = set(P.REGISTRY)
    for needed in ("tests_missing", "annotate", "review", "structural_review",
                   "tests_failing", "verdict_failed", "merge"):
        assert needed in names, f"delivery loop still missing {needed}"


def test_all_wakes_runs_clean_on_an_empty_database(db):
    """Every predicate must survive an empty database — boot evaluates them all
    before anything exists."""
    assert P.all_wakes(db) == []


def test_predicates_are_pure(db):
    """
    Evaluating the frontier must not change it.

    A predicate that writes would make the frontier depend on how often it was
    computed, and the scheduler computes it constantly.
    """
    db.execute("INSERT INTO items (id, text, kind, provenance, approval) "
               "VALUES ('i1','x','in_scope','decided','contested')")
    before = [dict(r) for r in db.execute("SELECT * FROM items")]

    P.all_wakes(db)
    P.all_wakes(db)

    after = [dict(r) for r in db.execute("SELECT * FROM items")]
    assert before == after
    assert db.execute("SELECT COUNT(*) n FROM messages").fetchone()["n"] == 0
    assert db.execute("SELECT COUNT(*) n FROM sessions").fetchone()["n"] == 0


def test_contested_wakes_the_items_owner(db):
    db.execute("INSERT INTO items (id, text, kind, provenance, approval) "
               "VALUES ('i1','delete accounts','in_scope','decided','contested')")
    wakes = P.REGISTRY["contested"].fn(db)
    assert [w.role for w in wakes] == ["vision_keeper"]
    assert wakes[0].refs == ("i1",)


def test_tests_failing_stops_at_the_cap(db):
    db.execute("INSERT INTO items (id, text, kind, provenance) "
               "VALUES ('i1','x','in_scope','decided')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','running')")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c1','t1','x')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst1','b1','c1','p','b')")

    db.execute("INSERT INTO test_runs (id, batch_id, test_id, result, attempt) "
               "VALUES ('r1','b1','tst1','fail',3)")
    assert P.REGISTRY["tests_failing"].fn(db), "should bounce below the cap"

    db.execute("UPDATE test_runs SET attempt = 10")
    assert not P.REGISTRY["tests_failing"].fn(db), "should stop at the cap"


# ---------------------------------------------------------------------------
# Declarations are not implementations
# ---------------------------------------------------------------------------

# Both known-gap lists are empty. They existed while the delivery loop did not:
# `merge` returned `[]`, `annotate` queried a table nobody had built, and six
# states were declared with nothing able to write them. Kept as empty sets
# rather than deleted, because the assertion they carry — *this list may not
# grow* — is the useful half, and it is easier to see that it is at zero than to
# notice that a check went missing.
KNOWN_GAPS_CAN_FIRE: set[str] = set()
KNOWN_GAPS_REACHABLE: set[str] = set()


def test_no_new_predicate_is_unfireable():
    """
    `check_terminal_states` reads *declarations*, so it can be satisfied by
    lying — and was: `merge` declared it drained a passing verdict with a body of
    `return []`, in the same commit that claimed to close that dead end.
    """
    found = set(P.check_predicates_can_fire())
    assert found <= KNOWN_GAPS_CAN_FIRE, f"new unfireable predicate: {found - KNOWN_GAPS_CAN_FIRE}"


def test_no_new_unreachable_state():
    """
    A state nothing writes is a state nothing can be in, and anything gated on it
    is dead. `batches.status = 'running'` was declared, three predicates waited on
    it, and no code path ever set it — so the delivery loop was gated on a value
    that could not occur.
    """
    found = {p.split(" is never")[0] for p in P.check_states_are_reachable()}
    assert found <= KNOWN_GAPS_REACHABLE, f"newly unreachable: {found - KNOWN_GAPS_REACHABLE}"


def test_the_reachability_check_distinguishes_reads_from_writes(monkeypatch):
    """
    Its first version grepped every file and found 'running' inside a SELECT, so
    it called the state reachable when nothing could set it. Reading a value and
    writing one look identical to a grep unless you say which you mean.

    Nothing is unreachable now, so the case is made rather than observed: a
    state that appears only in queries must still be reported.
    """
    # 'abandoned' was the fabricated example until `lifecycle.abandon`
    # started really writing it -- the canary needs a state nothing writes.
    monkeypatch.setattr(
        P, "schema_states",
        lambda: {("batches", "status"): ["pending", "running", "limbo"]})
    monkeypatch.setattr(P, "LIFECYCLE_COLUMNS", {("batches", "status")})

    found = {p.split(" is never")[0] for p in P.check_states_are_reachable()}
    assert "batches.status = 'limbo'" in found, found


def test_the_reachability_check_understands_parameterised_writes():
    """
    Most writes are parameterised — the model supplies `approval='approved'` and
    the sandbox validates it against the enum — so there is no literal to grep.
    Flagging those would bury the real holes in noise.
    """
    found = {p.split(" is never")[0] for p in P.check_states_are_reachable()}
    for parameterised in ("items.approval = 'approved'", "verdicts.result = 'pass'",
                          "items.provenance = 'observed'"):
        assert parameterised not in found


def test_round_close_does_not_fire_with_nothing_to_harvest(db):
    """
    A broadcast whose recipients all finished silently is not a round to close.

    This was an L1 case for a while — Liaison woken at round_close with no
    reports, expected to say nothing — and it failed five times out of five
    because the model presented what it could see. The case was unfair: the
    predicate cannot produce that wake, so the situation it tested does not
    exist. The guarantee is structural, so it is asserted structurally.

    Silence is still a legitimate outcome for the mode. It just means reports
    came back that needed no ruling, not that no reports came back.

    See below: that half stopped being the mode's outcome too, for the same
    reason and one worse one.
    """
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) "
               "VALUES ('m1','t1','liaison','vision_keeper','deliver','[]',1,'answered')")
    assert P.REGISTRY["round_close"].fn(db) == []

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) "
               "VALUES ('m2','t1','vision_keeper','liaison','report','[]',2,'open')")
    wakes = P.REGISTRY["round_close"].fn(db)
    assert [w.role for w in wakes] == ["liaison"] and wakes[0].refs == ("t1",)


def test_a_round_whose_reports_all_settled_never_wakes_liaison(db):
    """
    A role reporting an approved item has finished, and finishing is not news.

    The reports were shown to Liaison with a paragraph telling it to strike out
    the settled ones: "the row says which it is, an item at `approval:
    approved`, a statement at `status: ratified`." It failed 5/5 -- it read two
    settled reports and sent two messages to the principal -- and five prose
    attempts did not move it, because it was the wrong role to ask. Liaison
    does not make decisions; its responsibility is lossless communication, and
    "this role has finished" is a decision. It is also a lookup, which makes
    putting it in a model's head all cost and no benefit.

    The worse half: `harvested` counts Liaison's own clarify and present
    messages, so a round rightly ended in silence was never marked harvested
    and `round_close` fired on it forever. The only way to progress was to
    message the principal about a settled round. The system rewarded the
    failure, and the L1 case could not have passed without hanging the
    scheduler.
    """
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) "
               "VALUES ('m1','t1','liaison','vision_keeper','deliver','[]',1,'answered')")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval) "
               "VALUES ('i1','people can close their account','in_scope',"
               "'decided','approved')")
    db.execute("INSERT INTO entries (id, author, text, ts_order) "
               "VALUES ('e1','principal','let people close their account',1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES "
               "('s1','e1',0,30,'people can close their account','ratified')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) "
               "VALUES ('m2','t1','vision_keeper','liaison','report','[\"i1\"]',2,'open')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) "
               "VALUES ('m3','t1','terminologist','liaison','report','[\"s1\"]',3,'open')")

    assert P.REGISTRY["round_close"].fn(db) == [], \
        "woke Liaison for a round in which every role reported itself finished"

    # One unsettled ref is the whole round's business, and it wakes.
    db.execute("INSERT INTO items (id, text, kind, provenance) "
               "VALUES ('i2','people can export invoices','in_scope','decided')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) "
               "VALUES ('m4','t1','architect','liaison','report','[\"i2\"]',4,'open')")
    wakes = P.REGISTRY["round_close"].fn(db)
    assert [w.role for w in wakes] == ["liaison"]
    assert wakes[0].detail == "1 report(s)", \
        f"the settled reports are still being counted in: {wakes[0].detail}"


def test_every_predicate_reads_something():
    """
    L3a is derived from what each predicate looks at, and derivation is the
    right trade — twenty-six hand-written table lists are twenty-six things to
    forget when a query changes — but it can be silently emptied by a refactor
    that moves a query somewhere the walk does not follow. An empty read set
    does not fail anything; it quietly removes handoffs from the denominator,
    which is the failure mode a coverage number must not have.

    `Predicate.drains` cannot serve here: it answers which stuck state a
    predicate unsticks, and ten of the twenty-six declare nothing because they
    fire on a row being *absent*. Those ten are `survey`, `criteria`, `slicing`,
    `grouping`, `review` and friends — the entire forward pipeline.
    """
    from rota.core import predicates as P
    from rota.testkit.obligations import reads_of

    blind = sorted(p.name for p in P.REGISTRY.values() if not reads_of(p))
    assert not blind, (
        f"{len(blind)} predicate(s) read no table the walk can find: {blind}. "
        f"Every artefact handoff through them has left the L3a denominator.")


def test_the_artefact_handoffs_are_enumerated_at_all():
    """
    Twenty-six predicates are twenty-six wakes that no message caused, and the
    obligation set could not see one of them.

    `l3` enumerates message chains. Vision Keeper never messages Terminologist — it
    writes a ticket and `criteria` wakes them — so the one chain case testing an
    artefact handoff scored against the message pairs, matched nothing, and read
    as covering zero. The tier the whole onboarding loop runs in had no
    denominator.
    """
    from rota.testkit.obligations import l3, l3a

    handoffs = l3a()
    assert len(handoffs) > 20, f"only {len(handoffs)} artefact handoffs found"

    by_message = {o.what for o in l3()}
    assert not (by_message & {o.what for o in handoffs}), \
        "an artefact handoff is being counted twice, once as a message chain"

    assert any("-slicing->" in o.what or "-criteria->" in o.what
               for o in handoffs), \
        "the ticket-to-criteria handoff, which exposed this, is still invisible"


def test_a_role_waiting_on_its_own_question_is_not_offered_new_work(db):
    """
    Waiting had no representation, and the cost is in the predicates.

    `tests_failing` fires for any batch with a failing run and does not care
    that the Developer is waiting on a term it cannot proceed without. So the
    role was woken with identical state, asked again -- the duplicate guard
    refuses it -- hedged, and repeated until `loop_cap` was spent, at which
    point `exhausted` finally fired. The system's answer to "I am waiting" was
    spend the budget, then escalate.

    Derived, not declared: an open outbound `question` is what waiting *is*,
    and no role has to remember to say so.
    """
    from rota.core.scheduler import frontier, waiting_on

    db.execute("INSERT INTO items (id, text, kind, provenance, approval) "
               "VALUES ('i1','close an account','in_scope','decided','approved')")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) "
               "VALUES ('b1','i1','running','abc123')")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c1','t1','x')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst1','b1','c1','p','b')")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, result, attempt) "
               "VALUES ('r1','b1','tst1','fail',1)")

    assert any(w.role == "developer" and w.kind == "tick:tests_failing"
               for w in frontier(db)), "the failing batch should be offered"

    # The Developer asks what a word means and stops. Nothing about the batch
    # has changed: the tests still fail, and re-offering it achieves nothing
    # until somebody answers.
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq, status) VALUES "
               "('m1','t1','developer','terminologist','question','[]',"
               "'which sense of close?',1,'open')")

    assert waiting_on(db, "developer") == ["m1"]
    assert not any(w.role == "developer" and w.kind.startswith("tick:")
                   for w in frontier(db)), \
        "woken to redo work it is waiting on an answer for"

    # The answer must always get through, or waiting becomes a deadlock.
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES "
               "('m2','t1','terminologist','developer','answer','[]',2,'open')")
    assert any(w.role == "developer" and w.kind == "message"
               for w in frontier(db)), "the answer cannot reach a waiting role"

    # And once it is answered the work comes back on its own.
    db.execute("UPDATE messages SET status = 'answered' WHERE id = 'm1'")
    assert any(w.role == "developer" and w.kind == "tick:tests_failing"
               for w in frontier(db)), "the batch never returned"


def test_waiting_does_not_silence_a_different_role(db):
    """The register is per obligation, not a global pause."""
    from rota.core.scheduler import frontier

    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) "
               "VALUES ('i1','close an account','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq, status) VALUES "
               "('m1','t1','developer','terminologist','question','[]','?',1,'open')")

    assert any(w.role == "vision_keeper" and w.kind == "tick:slicing"
               for w in frontier(db)), \
        "one role's open question stopped another role's work"


def test_work_resting_on_an_unresolved_collision_is_not_offered(db):
    """
    Waiting, applied to somebody else's obligation rather than your own.

    A Tester woken to encode a criterion whose term has two live senses can
    only guess which to encode, and a test written from the wrong sense passes
    and pins the wrong promise -- worse than no test, because it reports as
    coverage. `term_collision` has already put the word to the principal, so
    offering the batch invites a second role to discover the same ambiguity
    independently and hedge, which is "two roles blocked on one ambiguity are
    two discoveries" seen from the other end.
    """
    from rota.core.scheduler import frontier, rests_on_a_collision

    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('i1','archived orders are searchable','in_scope','decided',"
               "'approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','search')")
    # A commit. The Tester now waits for one, because on a greenfield batch
    # there is nothing to call. This case is about collisions, not ordering.
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) "
               "VALUES ('b1','i1','running','deadbeef')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) VALUES "
               "('c1','tk1','archived orders come back from search','[\"g1\"]')")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','archived','flagged inactive, row stays','decided')")
    refs_from_columns(db)

    assert any(w.role == "tester" and w.kind == "tick:tests_missing"
               for w in frontier(db)), "one sense is no collision; encode it"

    # A second sense arrives. Nobody has ruled, so the criterion now rests on a
    # word that means two things.
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g2','archived','moved to cold storage','decided')")

    assert rests_on_a_collision(
        db, next(w for w in P.all_wakes(db) if w.role == "tester")) == ["c1"]
    assert not any(w.role == "tester" for w in frontier(db)), \
        "offered a criterion whose meaning is still an open question"
    assert any(w.role == "terminologist" and w.kind == "tick:term_collision"
               for w in frontier(db)), "the collision itself must still be raised"

    # Ruled on, and the work comes back without anyone asking.
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
               "('d1','terminologist','archived means flagged inactive',"
               "'[\"g1\",\"g2\"]')")
    assert any(w.role == "tester" and w.kind == "tick:tests_missing"
               for w in frontier(db)), "the ruling never released the work"


def test_observed_rows_wait_for_onboarding_to_finish(db, monkeypatch):
    """
    tipsM, 2026-09-09: the observed-entries wake fired while onboarding was
    still writing rows. Each wake carried one or two, and the principal saw
    the same page sixteen times. The page waits for the last row.
    """
    from rota.core import scheduler

    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','tip','the gratuity','observed')")
    refs_from_columns(db)
    monkeypatch.setattr(scheduler, "onboarding_phase", lambda conn: "survey")
    assert not any(w.kind == "tick:observed_entries" for w in P.all_wakes(db))
    monkeypatch.setattr(scheduler, "onboarding_phase", lambda conn: "done")
    assert any(w.kind == "tick:observed_entries" for w in P.all_wakes(db))


def test_review_and_merge_wait_for_every_criterions_test(db):
    """
    tipsZ, 2026-09-09: the repository's own test joined the batch, the
    harness ran it green, review ran, and the batch merged with no test of
    either criterion and no Tester session. A green harness no longer says
    the Tester has been here.
    """
    from rota.core import lifecycle

    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('i1','x','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','t')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) VALUES ('c1','tk1','the tip is right','[]')")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES ('b1','i1','running','abc123')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('inh_1','b1',NULL,'tests/test_old.py','def test_old(): pass')")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) VALUES "
               "('tr1','b1','inh_1','abc123','pass')")
    assert not any(w.kind == "tick:review" for w in P.all_wakes(db)), "review ran before the Tester"
    assert any(w.kind == "tick:tests_missing" for w in P.all_wakes(db))
    assert lifecycle.mergeable(db, "b1") == "criteria without a test: c1"
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('tst_1','b1','c1','tests/test_tip.py','def test_tip(): pass')")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) VALUES "
               "('tr2','b1','tst_1','abc123','pass')")
    assert any(w.kind == "tick:review" for w in P.all_wakes(db))


def test_the_agenda_waits_for_onboarding_to_finish(db, monkeypatch):
    """
    tipsV, 2026-09-09: each Critic challenge wrote one ledger row and the
    agenda raised a page for each before the next challenge ran. Thirteen
    pages. One page, once the rows are all there.
    """
    from rota.core import scheduler

    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('i1','x','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, "
               "author) VALUES ('l_1','i1','items','a default','open','critic')")
    monkeypatch.setattr(scheduler, "onboarding_phase", lambda conn: "survey")
    assert not any(w.kind == "tick:agenda" for w in P.all_wakes(db, principal_present=True))
    monkeypatch.setattr(scheduler, "onboarding_phase", lambda conn: "done")
    assert any(w.kind == "tick:agenda" for w in P.all_wakes(db, principal_present=True))


def test_an_item_amended_after_delivery_is_sliced_again(db):
    """
    tipsAH, 2026-09-09, from the seat: the split merged wrong, the principal
    said so, the item was amended and approved at version 9, and the run
    went quiet. Its one ticket had gone out in the merged batch, and an item
    with a ticket is never sliced. The merge records the delivered version;
    an approval of a later version is new work.
    """
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('split_bill','v1','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_1','split_bill','t')")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES ('b1','split_bill','merged','abc')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk_1')")
    db.execute("INSERT INTO config (key, value) VALUES ('delivered:split_bill', '1')")
    assert not any(w.kind == "tick:slicing" for w in P.all_wakes(db)), "delivered and unchanged"
    # The key was quarantined before the amendment; the new version forgets
    # it once, on record, and the frontier offers the work.
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) VALUES "
               "('vision_keeper|tick:slicing|split_bill', 3, 1)")
    db.execute("UPDATE items SET version = 2, approval_ver = 2, text = 'v2' WHERE id = 'split_bill'")
    from rota.core.scheduler import frontier
    wakes = [w for w in frontier(db) if w.kind == "tick:slicing"]
    assert wakes and wakes[0].refs == ("split_bill",), "amended after delivery is new work"
    assert db.execute("SELECT value FROM config WHERE key='resliced:split_bill'").fetchone()["value"] == "2"
    assert not db.execute("SELECT 1 FROM tick_attempts WHERE tick_key LIKE '%slicing%'").fetchone()
    # A running batch on the item holds it.
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_2','split_bill','t2')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b2','split_bill','running')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b2','tk_2')")
    assert not any(w.kind == "tick:slicing" for w in P.all_wakes(db))


def test_an_observed_item_is_a_record_not_a_build_order(db):
    """
    tipsK and tipsT, 2026-09-09: approving the observed items on the page
    sent them to slicing, and the Developer was sent to rewrite behaviour
    that exists. Found is not decided, and a description is not an order.
    """
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('accept_inputs','the program reads two numbers','in_scope',"
               "'observed','approved',1,1)")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('split_bill','the bill is split','in_scope','decided','approved',1,1)")
    refs_from_columns(db)
    wakes = [w for w in P.all_wakes(db) if w.kind == "tick:slicing"]
    assert wakes and wakes[0].refs == ("split_bill",), wakes


def test_a_merged_batch_never_wakes_the_tester_again(db):
    """
    tipsI, 2026-09-09: one criterion never got a test. The batch merged
    anyway. `tests_missing` fired on the merged batch, the Tester was
    quarantined, and the state said the team gave up. A merged batch is done.
    """
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('i1','the tip is shown','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','show')")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) "
               "VALUES ('b1','i1','merged','deadbeef')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) VALUES "
               "('c1','tk1','the tip is printed','[]')")
    assert not any(w.kind == "tick:tests_missing" for w in P.all_wakes(db))
    db.execute("UPDATE batches SET status = 'running' WHERE id = 'b1'")
    assert any(w.kind == "tick:tests_missing" for w in P.all_wakes(db))


def test_a_dead_answer_climbs_to_somebody_who_has_not_spoken(db):
    """
    The register's one declared entry, and everything after it derived.

    Developer asks Vision Keeper, Vision Keeper answers, and the answer does not
    land. Nothing in the rows can tell that from a good answer -- the question
    says `answered` and a reply exists -- so the asker says so, and from there
    who hears about it is a function of who has already spoken in the thread.

    What this replaces is a role being told to spend attempts it knows are
    wasted so a cap can notice what it already knows.
    """
    from rota.core.scheduler import frontier

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq, status) VALUES "
               "('m1','t1','developer','vision_keeper','question','[]',"
               "'does partial reconciliation count as done?',1,'answered')")
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES "
               "('m2','m1','t1','vision_keeper','developer','answer','[]',2,'answered')")

    assert not any(w.kind == "tick:unresolved" for w in frontier(db)), \
        "an answered question is discharged until the asker says otherwise"

    db.execute("UPDATE messages SET status = 'unresolved', unresolved_note = "
               "'the criteria do not cover partial' WHERE id = 'm1'")

    wakes = [w for w in frontier(db) if w.kind == "tick:unresolved"]
    assert [w.role for w in wakes] == ["architect"], \
        "Vision Keeper has spoken; the climb must reach somebody who has not"
    assert wakes[0].detail == "the criteria do not cover partial", \
        "the note is the only thing the next rung cannot re-derive"

    # The discharge is `session_commit`'s, because the climb must not walk
    # itself: a rung that answers becomes a role that has spoken, which would
    # derive the next rung, and one declaration would tour the whole ladder
    # without the asker ever saying the second answer missed too.
    from rota.core import db as db_mod

    db_mod.session_commit(db, db_mod.SessionResult(
        session_id="s1", role="architect",
        messages=[db_mod.OutboundMessage(
            id="m3", to_role="developer", verb="answer", thread_id="t1")]))

    assert not any(w.kind == "tick:unresolved" for w in frontier(db)), \
        "the climb repeated itself after the rung it woke had spoken"


def test_the_climb_ends_at_the_principal_rather_than_nowhere(db):
    """
    Everyone who could answer has, and it is still open.

    A ladder whose last rung is silence is the dead end this whole half exists
    to prevent, so Liaison is the final rung -- not because it can answer, but
    because it is how anything reaches the principal.
    """
    from rota.core.scheduler import frontier

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq, status, unresolved_note) VALUES "
               "('m1','t1','developer','vision_keeper','question','[]','?',1,"
               "'unresolved','still no rule for partial')")
    for i, role in enumerate(("vision_keeper", "architect"), start=2):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                   "body_refs, seq, status) VALUES "
                   f"('m{i}','t1','{role}','developer','answer','[]',{i},'answered')")

    wakes = [w for w in frontier(db) if w.kind == "tick:unresolved"]
    assert [w.role for w in wakes] == ["liaison"], \
        "the roles are exhausted and it must go to the principal, not go quiet"

    from rota.core import db as db_mod

    db_mod.session_commit(db, db_mod.SessionResult(
        session_id="s1", role="liaison",
        messages=[db_mod.OutboundMessage(
            id="m4", to_role="principal", verb="clarify", thread_id="t1",
            body_text="purchase or sequence?")]))

    assert not any(w.kind == "tick:unresolved" for w in frontier(db)), \
        "it is on the principal's agenda now, which has a drain of its own"


def test_a_rung_that_cannot_reply_to_the_asker_is_not_a_rung(db):
    """
    Reply-capability is read off the graph, not assumed.

    Architect can answer Developer and has no edge to Tester, so a Tester
    question that dies escalates straight past Architect. Waking a rung that
    cannot speak to the asker produces a session with nothing it can do, and
    that silence is indistinguishable from the answer having landed.
    """
    from rota.core.scheduler import frontier

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq, status, unresolved_note) VALUES "
               "('m1','t1','tester','terminologist','question','[]','?',1,"
               "'unresolved','which sense does the criterion take')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES "
               "('m2','t1','terminologist','tester','answer','[]',2,'answered')")

    wakes = [w for w in frontier(db) if w.kind == "tick:unresolved"]
    assert [w.role for w in wakes] == ["vision_keeper"], \
        "Architect cannot answer Tester; the climb must skip to one that can"


def test_a_reported_collision_stops_being_offered(db):
    """
    The mode has one productive verb, and using it did not stop the wake.

    `term_collision` was built as the glossary's `contradiction` -- its own
    docstring says so -- and `contradiction` has always ended with "return []
    if a clarify is already open to the principal". This copied the intent and
    not the check.

    Measured on an Obsidian plugin: a survey of `.github` wrote two senses of
    `issue_template`, correctly -- a bug-report template and a feature-request
    template are two things. The mode's whole working set is
    `glossary.consult`, `glossary.lookup`, `msg.report_liaison`; amending is
    forbidden there because collapsing two senses is a decision. So the session
    reported on turn 3, its first opportunity, exactly as briefed, and was woken
    again. Six sessions, three of them to the 12-turn cap, 44 of the run's 71
    turns. `fix` outranks `start`, so the survey wakes queued behind it were
    never reached and the run finished with no survey record at all.
    """
    from rota.core.scheduler import frontier

    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','issue_template','bug report template','observed')")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g2','issue_template','feature request template','observed')")
    refs_from_columns(db)

    assert any(w.kind == "tick:term_collision" for w in frontier(db)),         "two live senses, nobody told: it must be raised"

    # The one act the mode permits.
    db.execute("INSERT INTO messages (id, seq, thread_id, from_role, to_role, "
               "verb, status, body_refs) VALUES "
               "('m1',1,'t1','terminologist','liaison','report','open',"
               "'[\"g1\",\"g2\"]')")

    assert not any(w.kind == "tick:term_collision" for w in frontier(db)),         "it has been put to somebody; asking again costs a turn and adds nothing"

    # Parked, not discharged. The register still carries it.
    assert P.outstanding(db), "a wake-suppression is not a discharge"

    # A third sense joins the open case rather than opening a second one. This
    # happened in the measured run: a session tried to settle the word by
    # writing a merged third row, which under id-keyed matching would read as a
    # brand new collision.
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g3','issue_template','template for bugs and features',"
               "'observed')")
    assert not any(w.kind == "tick:term_collision" for w in frontier(db)),         "a third sense is more evidence for the open case, not a new one"

    # An unrelated word is still raised: the suppression is per-term, not
    # `contradiction`'s cruder "any open clarify exists at all".
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g4','intent','a note-creation recipe','observed')")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g5','intent','a specific action or task','observed')")
    assert [w.detail for w in frontier(db) if w.kind == "tick:term_collision"]         == ["intent"]

    # Answered and dropped without a ruling: it comes back, because nothing was
    # settled and nobody is holding it any more.
    db.execute("UPDATE messages SET status = 'answered' WHERE id = 'm1'")
    assert "issue_template" in [w.detail for w in frontier(db)
                                if w.kind == "tick:term_collision"]


def test_what_this_system_does_not_know_is_one_query(db):
    """
    The register's last item, and the one it kept describing as missing.

    Sixteen predicates each answered their own question and nothing answered
    "what is outstanding" -- every row existed and none of them were counted
    together. It is a fold over work already done, which is why it needed no
    artefact.
    """
    assert P.outstanding(db) == [], "an empty project owes nothing"

    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','order','a customer purchase','decided')")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g2','order','the sequence events arrive in','decided')")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('i1','reconcile late orders','in_scope','decided','contested',1,1)")

    rows = {r["obligation"]: r for r in P.outstanding(db)}
    assert "term_collision" in rows, "a word with two live senses is outstanding"
    assert "contested" in rows, "an item the principal rejected is outstanding"
    assert rows["term_collision"]["owners"] == ["terminologist"], \
        "an obligation nobody owns cannot be discharged"
    assert set(rows["term_collision"]["refs"]) == {"g1", "g2"}

    # Discharged by evidence, not by anyone declaring it settled.
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
               "('d1','terminologist','order means a purchase','[\"g1\",\"g2\"]')")
    assert "term_collision" not in {r["obligation"] for r in P.outstanding(db)}


def test_the_register_set_is_the_one_the_document_names():
    """
    The classification lives in code and the document is checked against it,
    rather than the document being the only place it exists.
    """
    assert P.REGISTER_ENTRIES <= set(P.REGISTRY), \
        "the register names a predicate that does not exist"
    # Sixteen, plus the onboarding phases, plus `criterion_repair` 2026-08-26,
    # plus `touch_note` 2026-09-03 (P4: a batch's predicted touch is owed to
    # the principal until presented).
    assert len(P.REGISTER_ENTRIES) == 27


def test_the_livelock_guard_does_not_pre_empt_the_escalation(db):
    """
    Two thresholds describing one situation, in the wrong order.

    A role that keeps being woken and keeps producing nothing is escalated
    already: `count_dispatch` bounds the wake, `quarantine_overrun` abandons it
    past `tick_attempt_cap`, and `quarantined` carries it to Liaison and on to
    the principal. That is the register entry for a role not doing its job, and
    it was unreachable from a loop run -- `loop.run` halted the whole thing at
    two barren repeats, one short of the cap of three.

    The guard is a last resort and has to sit above the mechanism it backs up,
    or it replaces it.
    """
    from rota import paths
    from rota.core import config

    cap = config.get(db, "tick_attempt_cap")
    assert cap >= 1

    src = (paths.PACKAGE / "core" / "loop.py").read_text(encoding="utf-8")
    assert 'barren[key] > _config.get(conn, "tick_attempt_cap")' in src, \
        "the livelock guard must derive its threshold from the cap it backs up"
    assert "barren[key] >= 2" not in src, \
        "a literal threshold beside a configured one is how the two drift"


def test_the_quarantine_wake_names_something_the_principal_can_be_shown(db):
    """
    A mode whose only tool refuses the only ref it is given.

    `quarantined` wakes Liaison to tell the principal that work has silently
    left the system. Its whole working set is `msg.present_principal`, and that
    channel refuses message ids on purpose -- the principal has never seen a
    message and cannot resolve one. Both halves are right. Together they starve
    the mode: the session is handed a dead message, has no tool that turns it
    into the item it was carrying, and the one call it can make is refused for
    naming the thing it was given.

    Measured, before this was fixed: five runs, five sessions spent arguing with
    the guard -- `present_principal(refs=['the quarantined message'])`, then
    'quarantined message', then 'the message that failed to reach the
    principal', then six attempts to call a tool it does not have. Nothing sent.
    That is not a role failing to do its job; it is a job that could not be
    done, and the brief asks for exactly the part that is unreachable: "name the
    work that is now stalled, not the mechanism".

    So the wake carries the payload, not the envelope. What stalled is the item
    the dead message was about, and that is the thing with a name at the
    principal's end.
    """
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('i1','search results are ranked by relevance','in_scope',"
               "'decided','approved',1,1)")
    db.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
        "body_refs, seq, attempts, status) VALUES "
        "('m_dead','t1','liaison','terminologist','deliver','[\"i1\"]',1,6,"
        "'quarantined')")

    wakes = P.quarantined(db)
    assert wakes, "a quarantined message must wake somebody"

    refs = set(wakes[0].refs)
    assert refs, (
        "the wake named nothing, so the session has to guess what stalled — "
        "and its one tool takes refs")
    assert "m_dead" not in refs, (
        "the envelope is the one id `msg.present_principal` refuses; handing it "
        "over is handing the session a call it cannot make")
    assert refs == {"i1"}, (
        f"the wake must carry what the dead message was about, got {refs}")


def test_a_quarantined_tick_still_wakes_without_refs_to_offer(db):
    """
    The other half of the predicate, which has no payload to carry.

    A stalled tick is not a message and was never about an item, so there is
    nothing to name -- and that is the honest answer rather than a hole. The
    wake still fires, because a tick that cannot drain is worse than a dead
    message: it is produced again every pass and quiescence never comes.
    """
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
               "reported) VALUES ('liaison|tick:unresolved|k1',4,1,0)")
    wakes = P.quarantined(db)
    assert wakes, "a stalled tick must still be reported"


def test_the_register_reports_what_the_principal_is_sitting_on(db):
    """
    The register said "nothing outstanding" while the whole run was parked.

    Found by onboarding a real repository: fifteen surveys, twenty-two scope
    items, quiescent in 125 seconds, an open `present` in front of the
    principal and an open assumption in the ledger -- and `outstanding()`
    returned an empty list. The pane the cockpit and the TUI render as *what
    the system owes* was blank at exactly the moment the answer was "you".

    The cause is a suppression borrowed from the wrong question. `tick_agenda`
    returns nothing when a message to the principal is already open, and it is
    right to: presenting again would tell them something they can already see,
    and it is what makes the tick terminate. But `outstanding()` folds the same
    predicate, so "there is no point waking Liaison" was read as "nothing is
    owed". A wake-suppression is not a discharge.

    So the register asks the state directly rather than asking a scheduler
    whether it would like to schedule something.
    """
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES "
               "('m1','t1','liaison','principal','present','[\"i1\"]',1,'open')")
    db.execute("INSERT INTO ledger (id, author, about_ref, about_table, "
               "default_taken, status) VALUES "
               "('l1','developer','i1','items','assumed UTC','open')")

    rows = {r["obligation"]: r for r in P.outstanding(db)}
    assert "awaiting_principal" in rows, \
        f"the principal is being waited on and the register does not say so: {sorted(rows)}"
    assert rows["awaiting_principal"]["count"] == 1
    assert rows["awaiting_principal"]["owners"] == ["principal"], \
        "an obligation nobody owns cannot be discharged"
    assert "i1" in rows["awaiting_principal"]["refs"], \
        "and it has to say what about, or it is a notification"


def test_an_answered_ask_stops_being_outstanding(db):
    """Discharged by the answer, not by anyone declaring it handled."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES "
               "('m1','t1','liaison','principal','present','[\"i1\"]',1,'answered')")
    assert "awaiting_principal" not in {r["obligation"] for r in P.outstanding(db)}


# ---------------------------------------------------------------------------
# A chain of messages that goes nowhere
# ---------------------------------------------------------------------------

def _chain(db, pairs, start_seq=1):
    """Seed a causal chain: each message caused by the one before it."""
    prev = None
    for i, (frm, to, verb) in enumerate(pairs, start_seq):
        mid = f"m{i}"
        db.execute(
            "INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, "
            "verb, body_refs, seq, status) VALUES (?,?,?,?,?,?,'[]',?,'open')",
            (mid, mid, prev, frm, to, verb, i))
        if prev:
            db.execute("UPDATE messages SET status='answered' WHERE id = ?", (prev,))
        prev = mid
    return prev


def test_two_roles_passing_one_thing_back_and_forth_is_bounded(db):
    """
    The livelock every existing bound misses.

    Found by driving delivery on a real repository. Vision Keeper reopened,
    Developer elected, Vision Keeper reopened, Developer elected -- four full round
    trips in fourteen sessions, no batch ever formed, and it was still going
    when the step limit stopped it.

    Nothing counted it. `quarantine_overrun` bounds `attempts` on *one* message
    and every link here is a new message with `attempts = 1`. The barren-tick
    guard counts sessions that produce nothing, and every one of these produced
    something: a message. `loop_cap` bounds Developer<->Tester bounces on a
    batch, and no batch exists. Each message is even its own thread, so nothing
    that counts a thread sees a chain either.

    What makes it a loop is not the length. It is the same ordered edge, with
    the same verb, arriving again as the consequence of itself -- which is
    exactly what `cause_id` records and nothing read.
    """
    from rota.core import scheduler

    from rota.core import config

    # Seeded from the cap rather than a number written here: two constants
    # describing one threshold is how they drift, and this file fixed that once
    # already for the livelock guard.
    cap = config.get(db, "loop_cap")
    pairs = [("terminologist", "vision_keeper", "challenge")]
    for _ in range(cap + 1):
        pairs += [("vision_keeper", "developer", "reopen"),
                  ("developer", "vision_keeper", "elect")]
    last = _chain(db, pairs[:-1])          # ending on a reopen, as the run did

    assert scheduler.edge_repeats(db, last) == cap + 1,         "vision_keeper->developer:reopen has caused itself past the cap"

    assert scheduler.quarantine_looping(db) == [last], \
        "a loop nothing can break has to leave the frontier"
    assert db.execute("SELECT status FROM messages WHERE id = ?",
                      (last,)).fetchone()["status"] == "quarantined"


def test_a_loop_that_is_stopped_reaches_the_principal(db):
    """
    Quarantining is not the end of it. `quarantined` already carries an
    abandoned message to Liaison and on to the principal, and this is the
    escalation the register was missing a detector for -- the mechanism existed
    and nothing could reach it.
    """
    from rota.core import scheduler

    from rota.core import config

    cap = config.get(db, "loop_cap")
    pairs = []
    for _ in range(cap + 1):
        pairs += [("vision_keeper", "developer", "reopen"),
                  ("developer", "vision_keeper", "elect")]
    _chain(db, pairs[:-1])
    scheduler.quarantine_looping(db)

    wakes = P.REGISTRY["quarantined"].fn(db)
    assert wakes and wakes[0].role == "liaison", \
        "a stopped loop that nobody is told about is the silence it replaced"


def test_a_chain_that_is_going_somewhere_is_left_alone(db):
    """
    The bound is on repetition, not on length. A question climbing the ladder
    touches several roles once each and must not be mistaken for a loop --
    that is the escalation working, and stopping it would be worse than the
    livelock.
    """
    from rota.core import scheduler

    last = _chain(db, [
        ("tester", "terminologist", "question"),
        ("terminologist", "tester", "answer"),
        ("tester", "vision_keeper", "question"),
        ("vision_keeper", "architect", "question"),
        ("architect", "vision_keeper", "answer"),
        ("vision_keeper", "tester", "answer"),
    ])
    assert scheduler.edge_repeats(db, last) == 1
    assert scheduler.quarantine_looping(db) == []


def _inquiry(conn):
    """A principal question routed to one owner, in one thread."""
    conn.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
                 "('e_m5','principal','where does a user write a recipe?',1)")
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, seq, status) VALUES ('m5','m5','principal',"
                 "'liaison','converse','[\"e_m5\"]',1,'answered')")
    conn.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
                 "to_role, verb, body_refs, seq, status) VALUES "
                 "('m6','m5','m5','liaison','architect','ask','[\"e_m5\"]',2,"
                 "'unresolved')")
    conn.commit()


def test_the_inquiry_ladder_ends_at_the_principal(db):
    """
    `unresolved` skips the asker, which is right for every role: the asker is
    blocked and cannot answer itself. Liaison is the exception the rule was
    never asked about -- it is the asker *and* the only way back to the person
    who asked -- so a principal's question that no owner could answer stopped in
    silence, which from their side is indistinguishable from the system losing
    it.

    `liaison/unresolved.md` already says the right thing for this wake and had
    no way to be reached for it: "every role that could have taken it next has
    already spoken in this thread ... this is the strongest kind of question you
    can put to the principal".
    """
    from rota.core.predicates import unresolved

    _inquiry(db)
    # Architect has answered; two owners left, so the ladder is still climbing.
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, seq) VALUES "
               "('m7','m6','m5','architect','liaison','answer','[\"e_m5\"]',3)")
    db.commit()
    assert [w.role for w in unresolved(db)] == ["terminologist"]

    for n, role in ((8, "terminologist"), (9, "vision_keeper")):
        db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
                   "to_role, verb, body_refs, seq) VALUES "
                   f"('m{n}','m6','m5','{role}','liaison','answer','[]',{n})")
    db.commit()

    # Everyone who could hold it has spoken. The person who asked is next.
    assert [w.role for w in unresolved(db)] == ["liaison"]


def test_a_role_asked_question_still_stops_when_the_ladder_runs_out(db):
    """
    The bound. A *role's* blocked question ends with Liaison as an ordinary
    rung, and once Liaison has spoken the thread is on the principal's agenda
    and has a drain of its own. Waking the asker there would be waking somebody
    to answer their own question.
    """
    from rota.core.predicates import unresolved

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m1','t1','developer',"
               "'vision_keeper','question','[]',1,'unresolved')")
    for n, role in ((2, "vision_keeper"), (3, "architect"), (4, "liaison")):
        db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
                   "to_role, verb, body_refs, seq) VALUES "
                   f"('m{n}','m1','t1','{role}','developer','answer','[]',{n})")
    db.commit()
    assert unresolved(db) == []


def test_a_report_answering_an_ask_marks_it_unresolved(db):
    """
    "Cannot determine" becomes a report, and a report answering an `ask` is the
    asker's declaration made by the answerer.

    `schedule.reask` has to be *declared* in general because the evidence
    disagrees with the truth -- the question's row says answered, a reply is on
    file, and only the asker knows it did not land. Here the answerer said so
    outright, in a verb that means it, so the transition is derived.

    Without this an owner saying "not mine" reached Liaison in `report` mode,
    whose brief opens "a role has run out of rungs ... everyone below has
    already looked", and the principal was asked about a question two untouched
    owners might have answered for free.
    """
    from rota.core.runner import run_session
    from rota.core.predicates import Wake
    from rota.core.scheduler import open_tips
    from rota.llm.llm import Pins, ScriptedBackend

    _inquiry(db)
    db.execute("UPDATE messages SET status = 'open' WHERE id = 'm6'")
    db.commit()

    out = run_session(
        db, Wake("architect", kind="message", message_id="m6", detail="ask"),
        backend=ScriptedBackend(["TOOL: msg.report_liaison(refs=[])", "done"]),
        pins=Pins(model="stub", temperature=0.0), instructions="not mine")
    assert out.committed, out.errors

    row = db.execute("SELECT status, unresolved_note FROM messages "
                     "WHERE id = 'm6'").fetchone()
    assert row["status"] == "unresolved"
    assert "architect" in row["unresolved_note"]

    # And it does not also tip: the ladder carries it from here, and Liaison
    # hearing about the same question twice is how the `report` brief ends up
    # telling it the ladder is exhausted when it has barely started.
    assert [w.message_id for w in open_tips(db)] == []


def test_a_report_that_answers_nothing_still_tips(db):
    """
    The bound. A report outside any thread is the top of the escalation ladder,
    which is the whole of what `report` mode is for.
    """
    from rota.core.scheduler import open_tips

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m1','t1','architect','liaison',"
               "'report','[]',1)")
    db.commit()
    assert [w.message_id for w in open_tips(db)] == ["m1"]


def test_a_question_put_to_the_principal_stops_waking_the_ladder(db):
    """
    The end of the inquiry ladder needed a drain and had none.

    `unresolved` wakes Liaison for its own question once every owner has
    spoken. Nothing marked the question resolved afterwards, so the next pass
    saw the same state and woke Liaison again -- three identical clarifications
    to the principal, on seven of the eight maintainer questions.

    The `answered` sweep skips messages from the asker's own role, which is
    right for every role: an asker sending in its own thread is not somebody
    picking the question up. Liaison sending to the *principal* is, because
    the principal is the only party left. `predicates.unresolved` has said so
    from the start -- "by then Liaison has sent, which means it is on the
    principal's agenda, and that has a drain of its own" -- and the drain was
    never written anywhere the code could read.
    """
    from rota.core.predicates import Wake, unresolved
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend

    _inquiry(db)
    for n, role in ((7, "architect"), (8, "terminologist"), (9, "vision_keeper")):
        db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
                   "to_role, verb, body_refs, seq) VALUES "
                   f"('m{n}','m6','m5','{role}','liaison','answer','[]',{n})")
    db.commit()

    assert [w.role for w in unresolved(db)] == ["liaison"], "the last rung"

    out = run_session(
        db, Wake("liaison", "tick:unresolved", refs=("m6",)),
        backend=ScriptedBackend([
            "TOOL: msg.clarify_principal(refs=['e_m5'], "
            "question='nobody here knows where a recipe is written')", "done"]),
        pins=Pins(model="stub", temperature=0.0), instructions="put it to them")
    assert out.committed, out.errors

    assert unresolved(db) == [], "asked once, and not again"


def test_the_observed_offer_names_its_rows(db):
    """
    Live on cnt_v2r, `observed_entries` woke Liaison with counts alone --
    "glossary_terms:72, constraints:13, model_areas:6" -- and the mode's whole
    toolset is `msg.present_principal`: no read enumerates those tables. Asked
    to name 91 rows it cannot see, the session invented a dict ref, was
    refused at the channel, and the present never went out.

    The predicate counted the rows, so the predicate names them; and the
    present carries its wake's refs, added never substituted, the same rule as
    the report's trigger and the relay's ruling.
    """
    from rota.core.predicates import Wake, observed_entries
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend

    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','recipe','a seed note','observed')")
    db.execute("INSERT INTO constraints (id, headline, text, provenance) VALUES "
               "('k1','schema','must match','observed')")
    refs_from_columns(db)
    db.commit()

    wakes = observed_entries(db)
    assert wakes and sorted(wakes[0].refs) == ["g1", "k1"]

    # The session presents with empty refs; the wake's rows travel anyway.
    out = run_session(
        db, wakes[0],
        backend=ScriptedBackend(["TOOL: msg.present_principal(refs=[])", "done"]),
        pins=Pins(model="stub", temperature=0.0), instructions="present them")
    assert out.committed, out.errors
    import json as _json

    sent = db.execute("SELECT body_refs FROM messages WHERE verb='present'").fetchone()
    assert sorted(_json.loads(sent["body_refs"])) == ["g1", "k1"]


def test_the_lazy_election_defers_the_baseline_to_the_ledger(db):
    """
    The election, from the stories: "confirm the whole baseline up front, or
    lazily as work first touches each area. The principal's call, not the
    system's." Literally here -- no model is in the path. The seat records the
    choice as config; under `lazy` the offer becomes a scheduler action; each
    observed row is logged in its own words as an assumption awaiting first
    touch, authored by the principal because the deferral is their election.

    Blocked until the ledger rename, and the block was real: mass-logging
    through a field answered `True` 87% of the time would have filled the
    agenda with a page of `True` and collapsed the ids that keep assumptions
    apart.
    """
    from rota.core.loop import step
    from rota.core.predicates import observed_entries
    from rota.llm.llm import Pins, ScriptedBackend

    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','recipe','a note that seeds another','observed')")
    db.execute("INSERT INTO constraints (id, headline, text, provenance) VALUES "
               "('k1','frontmatter must match the schema','x','observed')")
    db.execute("INSERT INTO config (key, value) VALUES "
               "('baseline_election','lazy')")
    refs_from_columns(db)
    db.commit()

    offer = observed_entries(db)
    assert [(w.kind, sorted(w.refs)) for w in offer] == \
        [("do:defer_baseline", ["g1", "k1"])]

    s = step(db, backend=ScriptedBackend(["done"]),
             pins=Pins(model="stub", temperature=0.0))
    assert "deferred 2" in (s.note or "")

    rows = {r["about_ref"]: r for r in db.execute(
        "SELECT about_ref, default_taken, author, status FROM ledger")}
    assert set(rows) == {"g1", "k1"}
    assert all(r["author"] == "principal" and r["status"] == "open"
               for r in rows.values())
    assert "a note that seeds another" in rows["g1"]["default_taken"], \
        "the assumption is the row's own words, not a flag"

    # Deferred once: the offer is quiet, and the agenda -- which drains open
    # ledger rows -- is what carries them from here.
    assert observed_entries(db) == []


def test_the_eager_default_is_unchanged(db):
    """The bound: with no election on file, the offer is the present it has
    always been."""
    from rota.core.predicates import observed_entries

    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','recipe','a seed note','observed')")
    refs_from_columns(db)
    db.commit()
    offer = observed_entries(db)
    assert [(w.role, w.kind) for w in offer] == \
        [("liaison", "tick:observed_entries")]


def _bad_criterion(db):
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('i1','emails are stored "
               "lowercased','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('t1','i1','store the email lowercased on registration')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) VALUES "
               "('c1','t1','store the email lowercased on registration','[]')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq, status, unresolved_note) VALUES "
               "('q1','th1','tester','terminologist','question','[\"c1\"]',"
               "'what would make this checkable?',1,'unresolved',"
               "'encoding it is parroting')")
    db.commit()


def test_a_criteria_ref_reask_routes_to_the_owner_in_repair_mode(db):
    """
    A question whose refs name a criterion is not climbing toward a ruling --
    it is a defect report about an artefact with one writer. Found live on
    delivery rung one: the Tester took the parroting guard's exit, the
    question landed in a mode whose own brief says "answering is not
    amending", and the pair looped to the budget, because `criteria.specify`
    is offered in one mode whose predicate fires per ticket *without*
    criteria. Once written, wrong stayed wrong -- and the delivery cluster's
    stable reds all sit downstream of that.
    """
    from rota.core.predicates import unresolved
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend
    from rota.roles import prompts

    _bad_criterion(db)
    from rota.core.predicates import criterion_repair

    wakes = criterion_repair(db)
    assert [(w.role, w.kind, w.refs) for w in wakes] == \
        [("terminologist", "tick:criterion_repair", ("q1",))]
    assert unresolved(db) == [], "ceded, not raced"

    out = run_session(
        db, wakes[0],
        backend=ScriptedBackend([
            "TOOL: criteria.respecify(id='c1', text=\"register stores "
            "'a@b.com' for input 'A@B.com'\")",
            "TOOL: msg.answer_tester(refs=['c1'])", "done"]),
        pins=Pins(model="stub", temperature=0.0),
        instructions=prompts.compose("terminologist", "criterion_repair"))
    assert out.committed, out.errors

    assert "a@b.com" in db.execute(
        "SELECT text FROM criteria WHERE id='c1'").fetchone()["text"]
    assert db.execute("SELECT status FROM messages WHERE id='q1'"
                      ).fetchone()["status"] == "answered"
    assert unresolved(db) == []


def test_a_repair_that_declines_hands_the_question_to_the_ladder(db):
    """
    The bound, and the escape the mode's brief names: a repair session that
    ends without respecifying has said the criterion is not what is wrong.
    Once per question -- the session row is the record -- and the ladder
    takes it from there instead of the repair re-firing forever.
    """
    from rota.core.predicates import unresolved
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend
    from rota.roles import prompts

    _bad_criterion(db)
    from rota.core.predicates import criterion_repair

    out = run_session(
        db, criterion_repair(db)[0],
        backend=ScriptedBackend(["TOOL: msg.challenge_vision_keeper(refs=['c1'], "
                                 "quotes='store the email lowercased on "
                                 "registration -- no observable store is named')",
                                 "done"]),
        pins=Pins(model="stub", temperature=0.0),
        instructions=prompts.compose("terminologist", "criterion_repair"))
    assert out.committed, out.errors

    # The decline-by-challenge carries the problem itself: Vision Keeper holds
    # a live tip naming the criterion, and the repair does not re-fire.
    from rota.core.scheduler import open_tips

    tips = [(w.role, w.detail) for w in open_tips(db)]
    assert ("vision_keeper", "challenge") in tips
    assert criterion_repair(db) == [], "once per question"


def test_a_barren_repair_leaves_the_question_to_the_ladder(db):
    """
    The hole the auto-answer line had: any committed session answered its
    trigger, so a repair that declined with *nothing* -- no rewrite, no
    challenge, no answer -- closed the question silently, and the once-guard
    then stopped the repair re-firing. Dead thread, no record. A barren
    session leaves an unresolved trigger unresolved, and the ladder resumes.
    """
    from rota.core.predicates import unresolved
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend
    from rota.roles import prompts

    _bad_criterion(db)
    from rota.core.predicates import criterion_repair

    out = run_session(
        db, criterion_repair(db)[0],
        backend=ScriptedBackend(["done"]),
        pins=Pins(model="stub", temperature=0.0),
        instructions=prompts.compose("terminologist", "criterion_repair"))
    assert out.committed, out.errors

    after = unresolved(db)
    assert after and after[0].kind == "tick:unresolved", "the ladder, not silence"
    assert after[0].role != "terminologist"


def test_a_present_deferred_without_ruling_takes_the_lazy_path(db):
    """
    The limbo the put-once rule made: a present answered without a verdict --
    the principal read it and moved on -- left its rows not decided, not
    ledgered, and never re-offered. The filed entry's own suggestion closes
    it: a deferral *is* an election, and those rows become ledger assumptions
    awaiting first touch, without re-spending the attention that was already
    declined.
    """
    import json as _json

    from rota.core.loop import step
    from rota.core.predicates import observed_entries
    from rota.llm.llm import Pins, ScriptedBackend

    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','recipe','a note that seeds another','observed')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('p1','t1','liaison',"
               "'principal','present',?, 1,'answered')",
               (_json.dumps(["g1"]),))
    refs_from_columns(db)
    db.commit()

    offer = observed_entries(db)
    assert [(w.kind, w.refs) for w in offer] == \
        [("do:defer_baseline", ("g1",))]

    s = step(db, backend=ScriptedBackend(["done"]),
             pins=Pins(model="stub", temperature=0.0))
    assert "deferred 1" in (s.note or "")
    row = db.execute("SELECT default_taken, author FROM ledger").fetchone()
    assert "a note that seeds another" in row["default_taken"]
    assert row["author"] == "principal"
    assert observed_entries(db) == []


def test_a_ruled_present_is_not_limbo(db):
    """The bound: a present with a verdict is the eager path working, and its
    contested rows are on file as contested -- not assumptions."""
    import json as _json

    from rota.core.predicates import observed_entries

    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','recipe','a seed note','observed')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('p1','t1','liaison',"
               "'principal','present',?,1,'answered')", (_json.dumps(["g1"]),))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, seq, status) VALUES ('v1','p1','t1',"
               "'principal','liaison','verdict',?,2,'answered')",
               (_json.dumps(["g1"]),))
    db.commit()
    assert observed_entries(db) == []


def _answered_criteria_question(db):
    import json as _json

    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('i1','emails lowercased',"
               "'in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('t1','i1','store lowered')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES "
               "('b1','i1','running')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('b1','t1')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) VALUES "
               "('c1','t1','store lowered','[]')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq, status) VALUES ('q1','th1','tester',"
               "'terminologist','question',?, 'make it checkable?',1,"
               "'answered')", (_json.dumps(["c1"]),))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, seq) VALUES ('a1','q1','th1',"
               "'terminologist','tester','answer',?,2)",
               (_json.dumps(["c1"]),))
    db.commit()


def test_a_demonstrated_non_landing_is_a_reask_nobody_declares(db):
    """
    `schedule.reask` is a declaration because in general only the asker knows
    an answer did not land. Three delivery passes running, the Tester took
    every questioning exit the guard named and never the declaring one -- so
    the repair sat unreachable behind a sentence the model does not say.

    On this one shape the not-landing is demonstrated, not private: the
    session was woken by the answer to its own criteria-question, reached for
    `tests.encode` on that criterion, met the parroting refusal again, and
    wrote no test. Asked, answered, tried, same wall -- every piece on the
    session record. Derived at commit, the same move as the
    report-answering-an-ask rule: the declaration exists for the general
    case, and this case proves itself.
    """
    from rota.core.predicates import criterion_repair
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend
    from rota.roles import prompts

    _answered_criteria_question(db)
    out = run_session(
        db, P.Wake("tester", "message", message_id="a1", detail="answer"),
        backend=ScriptedBackend(["TOOL: tests.encode(id='tst1', "
                                 "criterion_id='c1', path='t.py', "
                                 "body='store lowered')", "done"]),
        pins=Pins(model="stub", temperature=0.0),
        instructions=prompts.compose("tester", "answer"))
    assert out.committed, out.errors

    q = db.execute("SELECT status FROM messages WHERE id='q1'").fetchone()
    assert q["status"] == "unresolved"
    assert [(w.role, w.kind) for w in criterion_repair(db)] == \
        [("terminologist", "tick:criterion_repair")]


def test_an_answer_that_lands_stays_answered(db):
    """The bound: the same wake writing a real test is the answer working,
    and nothing reopens the question."""
    from rota.core.predicates import criterion_repair
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend
    from rota.roles import prompts

    _answered_criteria_question(db)
    out = run_session(
        db, P.Wake("tester", "message", message_id="a1", detail="answer"),
        backend=ScriptedBackend(["TOOL: tests.encode(id='tst1', "
                                 "criterion_id='c1', path='test_reg.py', "
                                 "body=\"from app import register\\n"
                                 "def test_lower():\\n    assert "
                                 "register('A@B.com').email == "
                                 "'a@b.com'\")", "done"]),
        pins=Pins(model="stub", temperature=0.0),
        instructions=prompts.compose("tester", "answer"))
    assert out.committed, out.errors
    assert db.execute("SELECT status FROM messages WHERE id='q1'"
                      ).fetchone()["status"] == "answered"
    assert criterion_repair(db) == []


def _two_batches(db, running_pri=0, challenger_pri=5):
    for iid, pri in (("i_low", running_pri), ("i_high", challenger_pri)):
        db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
                   "approval_ver, version, priority) VALUES (?, 'x', "
                   "'in_scope', 'decided', 'approved', 1, 1, ?)", (iid, pri))
    db.execute("INSERT INTO batches (id, item_id, status, worktree, "
               "head_commit) VALUES ('b_low','i_low','running','wt/b_low',"
               "'abc123')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES "
               "('b_high','i_high','pending')")
    # The checkpoint references a real session, per the schema's FK.
    db.execute("INSERT INTO sessions (id, role, mode, committed, seq) "
               "VALUES ('s1','developer','normal',1,1)")
    db.execute("INSERT INTO checkpoints (session_id, role, batch_id, "
               "working_set) VALUES ('s1','developer','b_low','[]')")
    db.commit()


def test_a_reorder_that_outranks_the_running_batch_preempts_it(db):
    """
    Law 9's sentence, connected: "if a reorder bumps a batch ahead of the
    running one, the scheduler kills the running batch's environment outright
    ... The worktree and its commits persist as deferred work." The lever
    (`problem.prioritize`), the mechanism (`lifecycle.defer`) and the ordering
    (`batch_start`'s priority sort) all existed; a priority raised mid-flight
    was inert anyway, because `batch_start` refuses while anything runs and
    nothing else looked. One predicate and one scheduler action connect them,
    and no session is woken to decide it -- which batch runs is a scheduling
    fact.
    """
    from rota.core.loop import step
    from rota.core.predicates import preempt
    from rota.core.scheduler import tick_batch_start
    from rota.llm.llm import Pins, ScriptedBackend

    _two_batches(db)
    assert [(w.kind, w.refs) for w in preempt(db)] == \
        [("do:preempt", ("b_low", "b_high"))]

    s = step(db, backend=ScriptedBackend(["done"]),
             pins=Pins(model="stub", temperature=0.0))
    assert "outranks" in (s.note or "")

    # Law 9's guarantees: deferred not dead, worktree and commits kept,
    # checkpoint discarded.
    row = db.execute("SELECT status, worktree, head_commit FROM batches "
                     "WHERE id='b_low'").fetchone()
    assert row["status"] == "deferred"
    assert row["worktree"] == "wt/b_low" and row["head_commit"] == "abc123"
    ck = db.execute("SELECT valid FROM checkpoints WHERE batch_id='b_low'"
                    ).fetchone()
    assert ck and ck["valid"] == 0,         "a deferred batch resumes cold: the checkpoint stays as a record, invalid"

    # And the winner is the next thing offered.
    assert [w.refs for w in tick_batch_start(db)] == [("b_high",)]


def test_equal_priority_never_preempts(db):
    """The bound: a preemption discards a checkpoint, and equal urgency does
    not pay for that. Deferral costs something; ties stand."""
    from rota.core.predicates import preempt

    _two_batches(db, running_pri=5, challenger_pri=5)
    assert preempt(db) == []


def test_the_account_is_never_sliced(db):
    """
    `how_it_works` is the whole program, not a behaviour. An approved account
    with no ticket is the normal state. On a cold walk (tipsE, 2026-09-08) the
    slicing predicate woke Vision Keeper for it fifty times, and Vision Keeper
    had nothing to slice each time.
    """
    from rota.core.scheduler import tick_slicing

    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('how_it_works','the user types the bill; the program prints the tip',"
               "'in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('calculate_tip','calculate the tip','in_scope','decided','approved',1,1)")
    refs_from_columns(db)
    db.commit()
    wakes = tick_slicing(db)
    assert len(wakes) == 1
    assert "calculate_tip" in wakes[0].refs
    assert "how_it_works" not in wakes[0].refs


def test_a_deliver_waits_for_onboarding(tmp_path):
    """
    tipsAI (2026-09-10): a sentence typed before orientation ran was
    ratified and delivered, the Vision Keeper found no account, and wrote
    the feature as the account. The deliver waits; the confirm does not.
    """
    from rota.core.db import init_db
    from rota.core.scheduler import open_tips

    conn = init_db(tmp_path / "r.db")
    conn.execute("INSERT INTO code_index (grain, grain_kind, area, fan_in, sym_kind, "
                 "content_hash) VALUES ('main.py', 'path', 'main', 0, '', 'x')")
    conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
                 "('e1','principal',1,'split the bill')")
    conn.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
                 "status) VALUES ('s1','e1',0,5,'split the bill','ratified')")
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, seq) VALUES ('m1','t','liaison','vision_keeper','deliver',"
                 "'[\"s1\"]',1)")
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, seq) VALUES ('m2','t','principal','liaison','converse',"
                 "'[\"e1\"]',2)")
    conn.commit()
    from rota.core.scheduler import onboarding_phase
    assert onboarding_phase(conn) not in ("done", "none")
    tips = open_tips(conn)
    assert [t.message_id for t in tips] == ["m2"]
    # Onboarding done: the deliver tips.
    conn.execute("DELETE FROM code_index")
    conn.commit()
    assert onboarding_phase(conn) == "none"
    assert {t.message_id for t in open_tips(conn)} == {"m1", "m2"}


def test_a_running_batch_with_no_commit_still_owes_its_start(tmp_path):
    """
    tipsAI (2026-09-10): the Developer's start session committed nothing,
    the batch stayed running with no commit, and nothing woke anyone.
    """
    from rota.core.db import init_db
    from rota.core.scheduler import tick_batch_start

    conn = init_db(tmp_path / "r.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, "
                 "version) VALUES ('i1','split the bill','in_scope','decided','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','running')")
    conn.commit()
    # Dispatched, no session yet: the Developer is in flight, single-instance.
    assert tick_batch_start(conn) == []
    conn.execute("INSERT INTO sessions (id, role, seq, wake_kind, wake_refs, committed) "
                 "VALUES ('s1','developer',1,'tick:batch_start','[\"b1\"]',1)")
    conn.commit()
    assert [(w.role, w.kind, w.refs) for w in tick_batch_start(conn)] == \
        [("developer", "tick:batch_start", ("b1",))]
    conn.execute("UPDATE batches SET head_commit = 'abc' WHERE id = 'b1'")
    conn.commit()
    assert tick_batch_start(conn) == []


def test_a_violated_finding_wakes_the_developer_until_answered(tmp_path):
    """
    tipsAJ (2026-09-10): every test passed, the Critic passed, the review
    found four constraints violated, and nothing woke anyone.
    """
    from rota.core.db import init_db
    from rota.core.predicates import REGISTRY

    conn = init_db(tmp_path / "r.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, "
                 "version) VALUES ('i1','split the bill','in_scope','decided','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('b1','i1','running','abc')")
    conn.execute("INSERT INTO constraints (id, headline, provenance) VALUES "
                 "('k1','calculate_tip is used by main','observed')")
    conn.execute("INSERT INTO findings (id, batch_id, constraint_id, commit_sha, status, grain) "
                 "VALUES ('f1','b1','k1','abc','violated','calculate_tip')")
    conn.commit()
    fn = REGISTRY["finding_violated"].fn
    assert [(w.role, w.kind, w.refs) for w in fn(conn)] == \
        [("developer", "tick:finding_violated", ("b1",))]
    # A newer commit answers it: the review reads that one.
    conn.execute("UPDATE batches SET head_commit = 'def' WHERE id = 'b1'")
    conn.commit()
    assert fn(conn) == []
    # A finding on the new commit, still violated, wakes again; an open
    # escalation to the Architect holds it.
    conn.execute("INSERT INTO findings (id, batch_id, constraint_id, commit_sha, status, grain) "
                 "VALUES ('f2','b1','k1','def','violated','calculate_tip')")
    conn.commit()
    assert fn(conn)[0].detail == "round 2"
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, "
                 "seq) VALUES ('m1','t','developer','architect','escalate','[\"b1\",\"f2\"]',1)")
    conn.commit()
    assert fn(conn) == []


def test_constraint_zero_cannot_be_violated(tmp_path):
    """tipsAN (2026-09-11): four k0 findings on the batch's own new files
    stood between green tests and the merge."""
    from rota.core.db import init_db
    from rota.core.predicates import REGISTRY
    from rota.core import lifecycle
    from rota.core.sandbox import build
    from rota.roles import prompts

    conn = init_db(tmp_path / "r.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, "
                 "version) VALUES ('i1','split the bill','in_scope','decided','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('b1','i1','running','abc')")
    conn.execute("INSERT INTO constraints (id, headline, provenance) VALUES "
                 "('k0','this area has not been surveyed','observed')")
    conn.execute("INSERT INTO findings (id, batch_id, constraint_id, commit_sha, status, grain) "
                 "VALUES ('f1','b1','k0','abc','violated','split_bill.py')")
    conn.commit()
    assert REGISTRY["finding_violated"].fn(conn) == []
    assert "violated" not in (lifecycle.mergeable(conn, "b1") or "")
    sb = build("architect", conn, batch_id="b1", mode="normal",
               allow=prompts.mode_tools("architect", "structural_review"))
    with pytest.raises(ValueError, match="constraint zero"):
        sb.call("findings.find", id="f2", batch_id="b1", constraint_id="k0",
                status="violated", grain="split_bill.py")
    assert sb.call("findings.find", id="f2", batch_id="b1", constraint_id="k0",
                   status="satisfied", grain="split_bill.py")["status"] == "satisfied"


def test_the_agenda_wake_carries_the_rows_a_page_may_hold(db):
    """clickI night 20 (2026-09-12): 66 open rows, and the Liaison counted
    its own ids up, none of them rows. The wake carries the first seven
    open ledger ids, oldest first, so there are real ids to copy; which
    lead the page stays the brief's."""
    from rota.core.sandbox import PAGE_ASSUMPTIONS
    from rota.core.scheduler import tick_agenda

    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, "
               "version) VALUES ('i1','x','in_scope','decided','approved',1,1)")
    for n in range(10):
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, author) "
                   "VALUES (?, 'i1', 'items', ?, 'open', 'vision_keeper')", (f"L{n:02d}", f"a{n}"))
    db.commit()
    (wake,) = tick_agenda(db, principal_present=True)
    assert wake.refs == tuple(f"L{n:02d}" for n in range(PAGE_ASSUMPTIONS))

def test_a_fail_a_later_pass_superseded_does_not_exhaust(db):
    """Found by reading (2026-09-16): `exhausted` took MAX(attempt) over every
    fail row, `tests_failing` over each test's latest run only. A batch whose
    fails a later pass superseded could climb the ladder while nothing failed."""
    from rota.core.predicates import exhausted
    db.execute("INSERT INTO items (id, text, kind, provenance, approval) VALUES ('i1','x','in_scope','decided','approved')")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES ('b1','i1','running','abc123')")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c1','t1','x')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES ('tst1','b1','c1','p','b')")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, result, attempt) VALUES ('r1','b1','tst1','fail',99)")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, result, attempt) VALUES ('r2','b1','tst1','pass',100)")
    db.commit()
    assert not [w for w in exhausted(db) if w.refs and "b1" in w.refs], "a passing batch climbed the ladder"
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, result, attempt) VALUES ('r3','b1','tst1','fail',101)")
    db.commit()
    assert [w for w in exhausted(db) if w.refs and "b1" in w.refs]

