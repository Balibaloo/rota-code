"""
T0-S9 — the sandbox surface *is* the working set.

The claim under test is structural: a role cannot reach outside its edges because
the capability was never built, not because a check refused it.
"""
from __future__ import annotations

import pytest

from rota.design import graph as graph_mod
from rota.roles.api import Ctx
from rota.core.db import init_db
from rota.core.sandbox import (
    ArgumentError, NotInWorkingSet, build, check_implementations,
    check_no_orphan_implementations,
)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def test_s9_every_edge_has_an_implementation():
    """Boot assertion: the graph cannot declare what the code cannot do."""
    assert check_implementations() == []


def test_s9_no_capability_exists_without_an_edge():
    """The mirror: an implementation no edge grants is dead capability."""
    assert check_no_orphan_implementations() == []


def test_s9_critic_namespace_is_exactly_criteria_tests_diff_and_verdict(db):
    """
    The richest fixture in the suite paired with the narrowest permitted surface.

    Spec note: TESTS.md says Critic's module contains exactly `criteria.*` and
    `diff.*`. Two additions, both agreed: `tests.*`, because Critic judges the
    diff *given* the tests; and `verdicts.emit`, which is its only write and was
    always implied by the graph.
    """
    sb = build("critic", db)
    artefact_fns = {f for f in sb.functions() if not f.startswith("msg.")}
    assert artefact_fns == {
        "criteria.load", "tests.load", "code.read", "verdicts.emit",
    }
    # Its only outbound channels are the two disputes it is entitled to raise.
    assert {f for f in sb.functions() if f.startswith("msg.")} == {
        "msg.challenge_developer", "msg.challenge_tester",
    }


def test_s9_out_of_edge_access_raises(db):
    sb = build("critic", db)
    with pytest.raises(NotInWorkingSet):
        sb["model"]                     # the reasoning it must never see
    with pytest.raises(NotInWorkingSet):
        sb["decisions"]                 # nor the record of why
    with pytest.raises(NotInWorkingSet):
        sb["ledger"]


def test_s9_unknown_verb_on_a_permitted_artefact_raises(db):
    sb = build("critic", db)
    with pytest.raises(NotInWorkingSet):
        sb["criteria"].specify          # Terminologist's write, not Critic's


def test_s9_developer_cannot_write_the_model(db):
    """Dev2: a constraint conflict must escalate, and self-serving is impossible."""
    sb = build("developer", db)
    assert "model.load" in sb.functions()
    with pytest.raises(NotInWorkingSet):
        sb["model"].amend


def test_s9_liaison_never_gains_an_interpreting_write(db):
    """Liaison records and broadcasts; it does not interpret."""
    sb = build("liaison", db)
    for artefact in ("problem", "glossary", "model", "tickets", "criteria"):
        with pytest.raises(NotInWorkingSet):
            sb[artefact]


def test_s9_consult_mode_has_no_writers(db):
    """
    Read-only inquiry is free — and cannot cost anything, because a consult
    sandbox has no write functions at all.
    """
    normal = build("gatekeeper", db)
    consult = build("gatekeeper", db, mode="readonly")

    assert "problem.assert" in normal.functions()
    assert "problem.consult" in consult.functions()
    assert not [f for f in consult.functions()
                if f.split(".")[1] in {"assert", "slice", "log", "author",
                                       "set_approval", "prioritize"}]


def test_s9_every_role_can_be_built(db):
    g = graph_mod.load()
    for role in g.roles:
        sb = build(role, db)
        assert sb.functions(), f"{role} has an empty working set"


def test_s9_tool_calls_are_recorded_as_evidence(db):
    """
    The tool_calls log is an assertion target, not decoration: "Developer re-read
    exactly the receipt-touched entries" is a query over it.
    """
    from rota.core.sandbox import drain_calls

    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('t1','account','login identity','decided')")
    sb = build("developer", db)
    sb.call("glossary.lookup", term="account")

    calls = drain_calls(sb.ctx)
    assert [c[0] for c in calls] == ["glossary.lookup"]
    assert "term='account'" in calls[0][1]


def test_s9_writes_are_staged_not_applied(db):
    """
    A sandbox write goes into the session's pending set, never straight to the
    table — atomicity is not optional and cannot be bypassed by a tool.
    """
    sb = build("gatekeeper", db)
    sb.call("problem.assert", id="i1", text="delete account", kind="in_scope")

    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 0
    assert sb.ctx.writes == [("items", "i1", {
        "text": "delete account", "kind": "in_scope",
        "provenance": "decided", "approval": "draft"})]


def test_s9_positional_arguments_are_bound_by_signature(db):
    """
    `problem.assert('i1', 'delete account')` is not informal, it is complete.

    The parser used to reject positional calls, which was the parser enforcing a
    rule it had no standing to enforce — whether the call is well formed depends
    on the signature, and only this layer knows the signature.
    """
    sb = build("gatekeeper", db)
    sb.call("problem.assert", "i1", "delete account")

    assert sb.ctx.writes == [("items", "i1", {
        "text": "delete account", "kind": "in_scope",
        "provenance": "decided", "approval": "draft"})]


def test_s9_positional_and_keyword_for_the_same_argument_is_an_error(db):
    """Informality is tolerated; ambiguity is not."""
    sb = build("gatekeeper", db)
    with pytest.raises(ArgumentError, match="both by position and by name"):
        sb.call("problem.assert", "i1", id="i2", text="delete account")


def test_s9_too_many_positional_arguments_is_an_error(db):
    sb = build("gatekeeper", db)
    with pytest.raises(ArgumentError, match="positional arguments"):
        sb.call("problem.assert", "i1", "text", "in_scope", "spare")


def test_s9_the_ledger_says_what_to_write_instead_of_id(db):
    """
    `id` means "this row's own id" everywhere else, and the ledger derives its
    own — so the model is not misreading the signature, it is reading a word
    that means something different here. Rejected 170 times before the error
    named the substitute.
    """
    sb = build("gatekeeper", db)
    with pytest.raises(ArgumentError, match="about_ref"):
        sb.call("ledger.log", id="i1", about_table="items", default_taken="yes")


def test_s9_a_container_where_a_scalar_was_declared_is_a_tool_error(db):
    """
    `type 'dict' is not supported`, raised by SQLite inside the transaction,
    took three cases' sessions down on every run. It passes the name check and
    the enum check and stages perfectly; only the database objects, and by then
    the session is lost rather than corrected.

    The annotation is the authority. `text: str` means a single value.
    """
    sb = build("gatekeeper", db)
    with pytest.raises(ArgumentError, match="takes a single value"):
        sb.call("problem.assert", id="i1", text={"was": "a dict"}, kind="in_scope")


def test_s9_a_list_argument_still_takes_a_list(db):
    """The check reads the annotation, so it does not break the ones that mean it."""
    sb = build("terminologist", db)
    db.execute("INSERT INTO items (id, text, kind, provenance) "
               "VALUES ('i1','x','in_scope','decided')")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','x')")
    sb.call("criteria.specify", id="c1", ticket_id="tk1", text="it works",
            term_refs=["g1", "g2"])
    assert sb.ctx.writes[0][2]["term_refs"] == '["g1", "g2"]'


def test_the_declaration_takes_no_id_and_finds_the_question_it_answers(db):
    """
    `schedule.reask` is the register's one declared transition.

    It deliberately takes no message id. The role is telling us it read an
    answer and is still blocked; asking it to name a row in that same session is
    a way to be told about the wrong question, and the causal chain already
    knows which one it is.
    """
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq, status) VALUES "
               "('m1','t1','developer','gatekeeper','question','[]','?',1,'answered')")
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES "
               "('m2','m1','t1','gatekeeper','developer','answer','[]',2,'open')")

    sb = build("developer", db)
    sb.ctx.trigger = "m2"
    sb.call("schedule.reask", what_is_missing="the criteria do not cover partial")

    assert sb.ctx.writes == [("messages", "m1", {
        "status": "unresolved",
        "unresolved_note": "the criteria do not cover partial"}, False)], \
        "the declaration must land on the question, not on the answer"


def test_only_the_asker_can_say_the_answer_did_not_land(db):
    """
    The whole content of the declaration is one role's private knowledge, so
    nobody else is in a position to make it. Being woken by an answer that
    settles somebody else's question is not a licence to reopen it.
    """
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq, status) VALUES "
               "('m1','t1','tester','gatekeeper','question','[]','?',1,'answered')")
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES "
               "('m2','m1','t1','gatekeeper','tester','answer','[]',2,'open')")

    sb = build("developer", db)
    sb.ctx.trigger = "m2"
    with pytest.raises(ValueError, match="tester"):
        sb.call("schedule.reask", what_is_missing="not mine to say")
    assert sb.ctx.writes == []


def _a_criterion(db, text: str) -> None:
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('i1','export for finance','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) "
               "VALUES ('tk1','i1','export for finance')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) "
               "VALUES ('c1','tk1',?,'[]')", (text,))
    db.execute("INSERT INTO batches (id, item_id, status) "
               "VALUES ('b1','i1','running')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) "
               "VALUES ('b1','tk1')")


def test_a_test_that_restates_its_criterion_is_not_an_encoding(db):
    """
    The trivially-passing test, refused where it is written.

    Tester's brief already says it: "writing a test that passes trivially is
    worse than writing none, because it reports as coverage". Two cases measured
    what that sentence achieves on its own. Both criteria were deliberately
    unencodable — one asks for something no machine can check, one needs a fact
    about somebody else's spec — and in ten runs out of ten the session opened
    by saving the criterion's own sentence back as the test body, before it had
    looked anything up. Having 'written the test' it then had nothing left to
    do, and the question it owed went out to whichever role was nearest.

    A body that says no more than the criterion says has added nothing. That is
    checkable, so it is checked, rather than asked for a third time.
    """
    _a_criterion(db, "the exported file is easy for the finance team to work with")
    sb = build("tester", db, mode="tests_missing")
    sb.ctx.batch_id = "b1"

    with pytest.raises(ValueError) as exc:
        sb.call("tests.encode", id="t1", criterion_id="c1", path="tests/export.py",
                body="The exported file is easy for the finance team to work with")

    assert "criterion" in str(exc.value).lower()
    assert sb.ctx.writes == [], "a refused encode must stage nothing"


def test_the_check_is_on_substance_not_on_wording(db):
    """
    The line, and the reason this is narrow.

    `L1-TS-apply-a-term-and-write-the-test` passes with a body that is a
    sentence rather than code -- "the billing entity that owes money, not the
    login identity" -- and that test is doing real work: it applies a sense the
    criterion left open. A guard demanding syntax would fail it. The failure
    being caught is the *copy*, so a copy is what is detected.
    """
    _a_criterion(db, "prorating a mid-month upgrade charges the unused remainder")
    sb = build("tester", db, mode="tests_missing")
    sb.ctx.batch_id = "b1"

    sb.call("tests.encode", id="t1", criterion_id="c1", path="tests/prorate.py",
            body="assert prorate(999, 1, 3) == 333")
    assert sb.ctx.writes, "an encoding that adds something must go through"


def test_punctuation_and_case_do_not_launder_a_copy(db):
    """
    The obvious way round it, closed at the same time as the door.

    A guard that a capital letter defeats is a guard that teaches the model to
    capitalise. Both measured sessions had already changed the case of the first
    word without meaning anything by it.
    """
    _a_criterion(db, "each webhook carries a signature header in the format the "
                     "receiving spec requires")
    sb = build("tester", db, mode="tests_missing")
    sb.ctx.batch_id = "b1"

    with pytest.raises(ValueError):
        sb.call("tests.encode", id="t1", criterion_id="c1", path="tests/hooks.py",
                body="Each webhook carries a signature header in the format "
                     "the receiving spec requires.")


def test_one_criterion_gets_one_test_in_a_session(db):
    """
    "One test per criterion" is the brief's first line, and nothing held it.

    Measured: a session that could not encode a criterion honestly wrote a
    paraphrase, then wrote the same paraphrase again under `t_3`, then again
    under `t_4`, narrating each as a fresh test that "considers the term
    webhook". Two of the four landed. Four rows pointing at one criterion is
    not coverage of it four times over; it is one unanswered question wearing
    four hats, and Critic downstream has no way to tell.

    Reported rather than refused, like the byte-identical re-encode above: the
    session has already said what it has to say about this criterion, and an
    error would only invite it to say it a fifth way.
    """
    _a_criterion(db, "prorating a mid-month upgrade charges the unused remainder")
    sb = build("tester", db, mode="tests_missing")
    sb.ctx.batch_id = "b1"

    sb.call("tests.encode", id="t1", criterion_id="c1", path="tests/prorate.py",
            body="assert prorate(999, 1, 3) == 333")
    again = sb.call("tests.encode", id="t2", criterion_id="c1",
                    path="tests/prorate.py",
                    body="assert prorate(999, 1, 3) == 333 # again")

    assert again.get("unchanged") or "already" in str(again).lower(), again
    assert [w[1] for w in sb.ctx.writes] == ["t1"], \
        "the second test for the same criterion must not land"


def test_a_second_criterion_is_a_second_test(db):
    """The bound is per criterion, not per session: a batch has several."""
    _a_criterion(db, "prorating a mid-month upgrade charges the unused remainder")
    db.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) "
               "VALUES ('c2','tk1','a downgrade takes effect next period','[]')")
    sb = build("tester", db, mode="tests_missing")
    sb.ctx.batch_id = "b1"

    sb.call("tests.encode", id="t1", criterion_id="c1", path="p",
            body="assert prorate(999, 1, 3) == 333")
    sb.call("tests.encode", id="t2", criterion_id="c2", path="p",
            body="assert effective_from(downgrade) == next_period_start")
    assert [w[1] for w in sb.ctx.writes] == ["t1", "t2"]


def test_changing_your_mind_about_who_owns_a_block_is_allowed(db):
    """
    One question leaves the session. It does not have to be the first one.

    The guard was written because two models asked several roles about one
    block and neither picked — and it picked *for* them, by taking the first.
    A session's first tool call is its reflex: measured on this very case, the
    Tester looked a whole clause up in the glossary, got nothing, read that as
    an undefined word and asked Terminologist on turn two. Three turns later it
    worked out the sentence was the problem, called `msg.question_gatekeeper`,
    and was refused for a decision it had already improved on.

    Nothing else staged in a session is append-only. A write can be superseded,
    a re-encode is reported and dropped, and the commit is atomic — so the
    outbound set is the session's final state, not its first draft. One question
    still goes out, and the one that goes is the one it settled on.
    """
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('i1','export for finance','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) "
               "VALUES ('tk1','i1','export for finance')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) VALUES "
               "('c1','tk1','the export is easy for finance to work with','[]')")

    sb = build("tester", db, mode="tests_missing")
    sb.call("msg.question_terminologist", refs=["c1"],
            question="what does 'easy to work with' mean?")
    sb.call("msg.question_gatekeeper", refs=["c1"],
            question="no machine can check this; is it a criterion?")

    asked = [(m["to_role"], m["verb"]) for m in sb.ctx.outbound]
    assert asked == [("gatekeeper", "question")], \
        f"one question, and the one it settled on: got {asked}"


def test_it_is_still_one_question_however_many_times_it_turns(db):
    """
    Replacement, not accumulation. The principle the guard exists for is that a
    block has one owner and three answers to reconcile is three sessions wasted;
    that is untouched. What changed is which of the session's answers counts.
    """
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('i1','sign webhooks','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) "
               "VALUES ('tk1','i1','sign outgoing webhooks')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) VALUES "
               "('c1','tk1','webhooks carry the signature the spec requires','[]')")

    sb = build("tester", db, mode="tests_missing")
    for who in ("terminologist", "gatekeeper", "researcher", "gatekeeper"):
        sb.call(f"msg.question_{who}", refs=["c1"], question="which of you owns this?")

    assert len(sb.ctx.outbound) == 1, sb.ctx.outbound
    assert sb.ctx.outbound[0]["to_role"] == "gatekeeper"


def test_asking_about_a_criterion_does_not_destroy_a_test_already_written(db):
    """
    A rule that lived for one measurement, kept as the reason it cannot come back.

    Asking who owns a criterion and encoding it are contradictory claims about
    one row, and a session that makes both leaves a test on file reporting as
    coverage of the thing it just called unencodable. That much is true, and a
    guard here withdrew the staged test when a question named its criterion.

    It resolved the contradiction by *order*, and order is not the
    discriminator. In the two Tester cases it was written for, the encode was a
    reflex on turn one -- before a single lookup -- and the question was what
    the session reached having read something; the question deserved to win. In
    `L1-TS-encode-a-criterion` the encode was `assert prorate(999, 1, 3) == 333`,
    correct and complete, and the trailing question was the noise. The rule
    destroyed the work and took a case that had been green for months to 0/5.

    Which one to keep turns on whether the test is any good, and that is exactly
    the judgement this system cannot make here. So neither is discarded, and
    this test pins that: the session's work survives its own second thoughts.
    """
    _a_criterion(db, "prorating a mid-month upgrade charges the unused remainder")
    sb = build("tester", db, mode="tests_missing")
    sb.ctx.batch_id = "b1"

    sb.call("tests.encode", id="t1", criterion_id="c1", path="tests/prorate.py",
            body="assert prorate(999, 1, 3) == 333")
    sb.call("msg.question_gatekeeper", refs=["c1"], question="is this in scope?")

    assert [w[1] for w in sb.ctx.writes if w[0] == "tests"] == ["t1"],         "a question must not withdraw work the session had already done"


def test_a_lookup_miss_says_how_big_the_glossary_is(db):
    """
    An empty result read as a strong signal when it was a vacuous one.

    Two Tester sessions looked a whole clause up in a glossary with no rows in
    it, got `[]` back, concluded the criterion turned on an undefined word and
    sent the sentence's problem to the wrong desk. Nothing was undefined; there
    was nothing to be defined against, and the system knew the number and did
    not say it.

    A *hit* is untouched — it returns the rows and only the rows, so every
    session that finds what it looked for sees exactly what it saw before.
    """
    sb = build("tester", db, mode="tests_missing")
    miss = sb.call("glossary.lookup", term="easy for the finance team to work with")
    assert miss["senses"] == []
    assert miss["glossary_size"] == 0
    assert "says nothing" in miss["note"]

    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','account','the billing entity','decided')")
    hit = sb.call("glossary.lookup", term="account")
    assert isinstance(hit, list) and hit[0]["term"] == "account", \
        "a hit must keep returning the rows and nothing else"

    still = sb.call("glossary.lookup", term="webhook")
    assert still["glossary_size"] == 1
    assert "says nothing" not in still["note"], \
        "a miss against a populated glossary is real evidence and reads as it"
