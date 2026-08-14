"""
Predicates, and the hard constraint that none may be missing.

The load-bearing case is `test_lint_catches_a_dead_end`: a lint nobody has proved
can fail is a lint you are trusting rather than using.
"""
from __future__ import annotations

import pytest

from rota.core import predicates as P
from rota.core.db import init_db


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
    """Adding a state to the schema without a way out fails the build."""
    monkeypatch.setattr(
        P, "schema_states",
        lambda: {("batches", "status"): ["pending", "running", "deferred",
                                         "merged", "abandoned"]})
    problems = P.check_terminal_states()
    assert any("'abandoned'" in p for p in problems), problems


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
    assert [w.role for w in wakes] == ["gatekeeper"]
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
    monkeypatch.setattr(
        P, "schema_states",
        lambda: {("batches", "status"): ["pending", "running", "abandoned"]})
    monkeypatch.setattr(P, "LIFECYCLE_COLUMNS", {("batches", "status")})

    found = {p.split(" is never")[0] for p in P.check_states_are_reachable()}
    assert "batches.status = 'abandoned'" in found, found


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
               "VALUES ('m1','t1','liaison','gatekeeper','deliver','[]',1,'answered')")
    assert P.REGISTRY["round_close"].fn(db) == []

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) "
               "VALUES ('m2','t1','gatekeeper','liaison','report','[]',2,'open')")
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
               "VALUES ('m1','t1','liaison','gatekeeper','deliver','[]',1,'answered')")
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
               "VALUES ('m2','t1','gatekeeper','liaison','report','[\"i1\"]',2,'open')")
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

    `l3` enumerates message chains. Gatekeeper never messages Terminologist — it
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

    assert any(w.role == "gatekeeper" and w.kind == "tick:slicing"
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
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','running')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) VALUES "
               "('c1','tk1','archived orders come back from search','[\"g1\"]')")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','archived','flagged inactive, row stays','decided')")

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


def test_a_dead_answer_climbs_to_somebody_who_has_not_spoken(db):
    """
    The register's one declared entry, and everything after it derived.

    Developer asks Gatekeeper, Gatekeeper answers, and the answer does not
    land. Nothing in the rows can tell that from a good answer -- the question
    says `answered` and a reply exists -- so the asker says so, and from there
    who hears about it is a function of who has already spoken in the thread.

    What this replaces is a role being told to spend attempts it knows are
    wasted so a cap can notice what it already knows.
    """
    from rota.core.scheduler import frontier

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq, status) VALUES "
               "('m1','t1','developer','gatekeeper','question','[]',"
               "'does partial reconciliation count as done?',1,'answered')")
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES "
               "('m2','m1','t1','gatekeeper','developer','answer','[]',2,'answered')")

    assert not any(w.kind == "tick:unresolved" for w in frontier(db)), \
        "an answered question is discharged until the asker says otherwise"

    db.execute("UPDATE messages SET status = 'unresolved', unresolved_note = "
               "'the criteria do not cover partial' WHERE id = 'm1'")

    wakes = [w for w in frontier(db) if w.kind == "tick:unresolved"]
    assert [w.role for w in wakes] == ["architect"], \
        "Gatekeeper has spoken; the climb must reach somebody who has not"
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
               "('m1','t1','developer','gatekeeper','question','[]','?',1,"
               "'unresolved','still no rule for partial')")
    for i, role in enumerate(("gatekeeper", "architect"), start=2):
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
    assert [w.role for w in wakes] == ["gatekeeper"], \
        "Architect cannot answer Tester; the climb must skip to one that can"
