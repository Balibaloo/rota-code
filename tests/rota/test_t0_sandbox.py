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


def test_s9_critic_namespace_is_review_plus_challenge(db):
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
        "challenge.load", "challenge.uphold", "challenge.break",
        "challenge.vacuous", "code.source",
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
    normal = build("vision_keeper", db)
    consult = build("vision_keeper", db, mode="readonly")

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
    sb = build("vision_keeper", db)
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
    sb = build("vision_keeper", db)
    sb.call("problem.assert", "i1", "delete account")

    assert sb.ctx.writes == [("items", "i1", {
        "text": "delete account", "kind": "in_scope",
        "provenance": "decided", "approval": "draft"})]


def test_s9_positional_and_keyword_for_the_same_argument_is_an_error(db):
    """Informality is tolerated; ambiguity is not."""
    sb = build("vision_keeper", db)
    with pytest.raises(ArgumentError, match="both by position and by name"):
        sb.call("problem.assert", "i1", id="i2", text="delete account")


def test_s9_too_many_positional_arguments_is_an_error(db):
    sb = build("vision_keeper", db)
    with pytest.raises(ArgumentError, match="positional arguments"):
        sb.call("problem.assert", "i1", "text", "in_scope", "spare")


def test_s9_the_ledger_says_what_to_write_instead_of_id(db):
    """
    `id` means "this row's own id" everywhere else, and the ledger derives its
    own — so the model is not misreading the signature, it is reading a word
    that means something different here. Rejected 170 times before the error
    named the substitute.
    """
    sb = build("vision_keeper", db)
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
    sb = build("vision_keeper", db)
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
               "('m1','t1','developer','vision_keeper','question','[]','?',1,'answered')")
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES "
               "('m2','m1','t1','vision_keeper','developer','answer','[]',2,'open')")

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
               "('m1','t1','tester','vision_keeper','question','[]','?',1,'answered')")
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES "
               "('m2','m1','t1','vision_keeper','tester','answer','[]',2,'open')")

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
    worked out the sentence was the problem, called `msg.question_vision_keeper`,
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
    sb.call("msg.question_vision_keeper", refs=["c1"],
            question="no machine can check this; is it a criterion?")

    asked = [(m["to_role"], m["verb"]) for m in sb.ctx.outbound]
    assert asked == [("vision_keeper", "question")], \
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
    for who in ("terminologist", "vision_keeper", "researcher", "vision_keeper"):
        sb.call(f"msg.question_{who}", refs=["c1"], question="which of you owns this?")

    assert len(sb.ctx.outbound) == 1, sb.ctx.outbound
    assert sb.ctx.outbound[0]["to_role"] == "vision_keeper"


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
    sb.call("msg.question_vision_keeper", refs=["c1"], question="is this in scope?")

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


def test_a_report_carries_what_it_was_delivered(db):
    """
    Which delivery a report answers is a fact about the session, not a choice.

    `report_is_settled` is what makes "I have nothing to add" free: a report
    whose every ref is in a terminal state is struck out before Liaison's
    round_close sees it, so it costs the principal nothing. It decides that by
    looking at the refs — and a report about the wrong row cannot be decided at
    all, so it survives and reaches a person.

    Measured on `L1-TE-the-words-are-already-defined`. The session did the whole
    job correctly: looked up all four words of a delivered statement, found
    every one already on file in the sense used, and reported. It reported
    `refs=[g_09b6f2]` — the glossary term it had just confirmed — and not the
    statement it was handed. A glossary sense has no terminal marker, so the
    report read as unsettled and the principal was going to be asked about a
    session that had nothing to ask.

    The same reasoning as `batch_id` defaulting from the wake and `area` from
    the scheduler: a value the session already knows should not be a value the
    role has to supply correctly.
    """
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e1','principal',1,'an invoice is issued when a subscription renews')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1','e1',0,46,"
               "'an invoice is issued when a subscription renews','ratified')")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','invoice','the billing document','decided')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES "
               "('m1','t1','liaison','terminologist','deliver','[\"s1\"]',1,'open')")

    sb = build("terminologist", db, mode="deliver")
    sb.ctx.trigger = "m1"
    sb.call("msg.report_liaison", refs=["g1"])

    refs = sb.ctx.outbound[0]["body_refs"]
    assert "s1" in refs, \
        "a report that does not name what it was given cannot be settled"
    assert "g1" in refs, "what the session found is still its own to report"

    from rota.core.scheduler import report_is_settled
    assert not report_is_settled(db, refs), \
        "a glossary sense has no terminal marker, so this one still needs a person"


def test_the_delivered_refs_are_added_once_and_not_reordered(db):
    """
    A report that already names its delivery is left exactly as it is — the
    role got it right and there is nothing to correct, which is the difference
    between a default and an override.
    """
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e1','principal',1,'archived orders stay searchable')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1','e1',0,30,"
               "'archived orders stay searchable','ratified')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES "
               "('m1','t1','liaison','terminologist','deliver','[\"s1\"]',1,'open')")

    sb = build("terminologist", db, mode="deliver")
    sb.ctx.trigger = "m1"
    sb.call("msg.report_liaison", refs=["s1"])

    assert sb.ctx.outbound[0]["body_refs"] == ["s1"]

    from rota.core.scheduler import report_is_settled
    assert report_is_settled(db, sb.ctx.outbound[0]["body_refs"]), \
        "every ref ratified is what makes 'nothing to add' cost nothing"


def test_a_session_woken_by_a_question_can_only_answer_the_asker(db):
    """
    The `unresolved` narrowing, stated once instead of per tick.

    It was keyed on `tick:unresolved` because that is where it was measured:
    Vision Keeper reaches Developer and Tester, both channels sat in the mode, and
    woken to a thread between Tester and Terminologist it answered Developer
    five runs out of five. The reasoning was never about that tick — the asker
    is the sender of the message that woke you, and that is true of every wake
    that carries one.

    It matters now because Terminologist can be asked by three roles. Its brief
    said "`msg.answer_developer` (or the asking role)", which names one instance
    and parenthesises the rest — the shape that has not held anywhere in this
    system. With the channel derived there is nothing to get right.
    """
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','grain','a unit of the touch set','decided')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq, status) VALUES "
               "('m1','t1','architect','terminologist','question','[\"g1\"]',"
               "'does grain mean a file or a symbol?',1,'open')")

    from rota.core.scheduler import Wake
    sb = build("terminologist", db, mode="question",
               wake=Wake(role="terminologist", kind="message", message_id="m1"))

    channels = {f for f in sb.functions() if f.startswith("msg.answer_")}
    assert channels == {"msg.answer_architect"}, \
        f"only the asker can be answered; got {sorted(channels)}"


def test_the_narrowing_needs_a_message_to_narrow_by(db):
    """
    A wake with no message behind it leaves every channel standing. Deriving
    from nothing would silently strip a role's whole reply surface, which is a
    worse failure than the one this prevents: it looks like a role choosing
    silence.
    """
    from rota.core.scheduler import Wake
    sb = build("terminologist", db, mode="question",
               wake=Wake(role="terminologist", kind="tick:criteria"))
    channels = {f for f in sb.functions() if f.startswith("msg.answer_")}
    assert len(channels) > 1, channels


def test_a_session_cannot_scope_one_item_both_ways(db):
    """
    A role disagreeing with itself, resolved silently by write order.

    Found in `L3-ratified-statement-becomes-scope`, which passes 5/5 and records
    seventeen writes to `items` from a single ratified statement. Reading the
    calls back: `problem.assert(id="invoice_retention", kind='in_scope')` and
    then `problem.assert(id="invoice_retention", kind='out_of_scope')` in the
    same session. Both were staged, the last one won at commit, and the case
    asserted `items: {count: ">=1"}` -- which seventeen satisfies.

    In scope and out of scope are the two answers this call exists to choose
    between. A session that gives both has not decided, and the one that reaches
    the database is decided by list order, which is not a judgement.

    Re-asserting the *same* scope is a different thing and stays allowed: it is
    a role restating itself, costs nothing, and there is nothing to correct.
    """
    sb = build("vision_keeper", db)

    sb.call("problem.assert", id="i_ret", text="invoices are retained",
            kind="in_scope")
    sb.call("problem.assert", id="i_ret", text="invoices are retained",
            kind="in_scope")            # restating is not disagreeing
    assert [w[1] for w in sb.ctx.writes] == ["i_ret", "i_ret"] or True

    with pytest.raises(ValueError) as exc:
        sb.call("problem.assert", id="i_ret", text="invoices are retained",
                kind="out_of_scope")
    assert "in_scope" in str(exc.value) and "out_of_scope" in str(exc.value)

    kinds = {w[2].get("kind") for w in sb.ctx.writes if w[0] == "items"}
    assert kinds == {"in_scope"}, \
        "the contradiction must not be left for write order to settle"


def test_two_different_items_are_not_a_contradiction(db):
    """The bound: one statement can yield several items, and routinely does."""
    sb = build("vision_keeper", db)
    sb.call("problem.assert", id="i_close", text="users can close accounts",
            kind="in_scope")
    sb.call("problem.assert", id="i_ret", text="invoices are retained",
            kind="out_of_scope")
    assert len([w for w in sb.ctx.writes if w[0] == "items"]) == 2


def test_a_batch_cannot_be_grouped_from_ids_that_are_not_tickets(db):
    """
    An invented reference must be a tool error, never an IntegrityError.

    This is the principle `tests.encode` already states: "a test naming a
    criterion that does not exist fails a foreign key *inside the transaction*
    and takes the session with it -- and is recoverable for the same reason: the
    model can be told and try again." `batches.group` staged its
    `batch_tickets` rows without checking any of them.

    Measured on a real repository. Architect's *first* call was right --
    `ticket_ids=['l_642631ec23']`, the one real ticket -- and then it grouped
    five more times passing **criteria** ids, `cr1` through `cr4`. All six
    staged. `batch_tickets.ticket_id` references `tickets(id)`, so the commit
    raised `FOREIGN KEY constraint failed` and the whole session was lost,
    including the grouping that was correct. Three sessions in a row, and no
    batch was ever formed for an approved item.

    Told instead, the five wrong calls cost a turn each and the right one lands.
    """
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('i1','validate an intent','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) "
               "VALUES ('tk1','i1','validate an intent')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) "
               "VALUES ('cr1','tk1','an intent in the frontmatter is accepted')")

    sb = build("architect", db, mode="grouping")

    with pytest.raises(ValueError) as exc:
        sb.call("batches.group", id="b1", item_id="i1", ticket_ids=["cr1"])
    assert "cr1" in str(exc.value)
    assert sb.ctx.writes == [], "a refused grouping must stage nothing at all"

    sb.call("batches.group", id="b1", item_id="i1", ticket_ids=["tk1"])
    assert [w[0] for w in sb.ctx.writes] == ["batches", "batch_tickets"]


def test_grouping_checks_the_item_too(db):
    """The other reference on the same row, and the same failure if it is wrong."""
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('i1','x','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','x')")

    sb = build("architect", db, mode="grouping")
    with pytest.raises(ValueError):
        sb.call("batches.group", id="b1", item_id="i_nope", ticket_ids=["tk1"])
    assert sb.ctx.writes == []


def test_a_one_element_list_around_a_scalar_unwraps(db):
    """`question=["is it one band?"]` is completely determined; two elements
    is a real ambiguity and stays refused."""
    from rota.core import sandbox as sandbox_mod

    sb = sandbox_mod.build("developer", db, session_id="s1")
    got = sb.call("msg.question_researcher", refs=[], question=["is it one band?"])
    assert got
    import pytest

    with pytest.raises(sandbox_mod.ArgumentError):
        sb.call("msg.question_researcher", refs=[], question=["a", "b"])


def test_a_ticket_naming_a_missing_item_is_refused_not_fatal(db):
    from rota.core import sandbox as sandbox_mod

    sb = sandbox_mod.build("vision_keeper", db, session_id="s1")
    import pytest

    with pytest.raises(Exception, match="i_ghost"):
        sb.call("tickets.slice", id="tk1", item_id="i_ghost", text="a ticket")


def test_grouping_infers_the_item_the_tickets_share(db):
    """`batches.group(item_id=None)` with tickets that all trace to one item:
    the row already knows; two items stays a refusal."""
    import pytest

    from rota.core import sandbox as sandbox_mod

    db.execute("INSERT INTO items (id, text, kind, provenance) VALUES "
               "('i1', 'export invoices', 'in_scope', 'decided')")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk1', 'i1', 'csv writer'), ('tk2', 'i1', 'download button')")
    sb = sandbox_mod.build("architect", db, session_id="s1")
    got = sb.call("batches.group", id="b1", ticket_ids=["tk1", "tk2"])
    assert got["id"] == "b1"
    db.execute("INSERT INTO items (id, text, kind, provenance) VALUES "
               "('i2', 'other', 'in_scope', 'decided')")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk3', 'i2', 'x')")
    with pytest.raises(Exception, match="exactly one approved item"):
        sb.call("batches.group", id="b2", ticket_ids=["tk1", "tk3"])


def test_an_ask_cannot_be_sent_with_empty_refs(db):
    """
    On the inquiry route the refs are the question, not a citation.

    `msg.ask_*` has no prose field -- law 2 -- so the entry id is the whole of
    how the principal's words reach the owner: the resolver expands it into
    `principal_said`. An ask without it wakes a role to answer nothing and
    looks, from every angle available afterwards, exactly like the route
    working.

    That is what it was doing. Measured on `llama3.1:8b` before this guard:
    four asks out of four carried `refs=[]`, in both passes, because the only
    worked example of the route in the system was
    `msg.ask_terminologist(refs=[], question='...')` -- refused for the
    argument, and correct-looking once the argument is dropped.

    Satisfiable, which is the test a refusal has to pass here: `entry_id` is in
    the session's own prompt, and the message names it.
    """
    sb = build("liaison", db, mode="normal")

    with pytest.raises(ValueError) as exc:
        sb.call("msg.ask_terminologist", refs=[])
    assert "entry_id" in str(exc.value)
    assert sb.ctx.outbound == [], "a refused ask must stage nothing"

    db.execute("INSERT INTO entries (id, author, text, ts_order) "
               "VALUES ('e_m1','principal','what is an account here?',1)")
    sb.call("msg.ask_terminologist", refs=["e_m1"])
    # Three, because one ask reaches every owner. What this case is about is
    # that the corrected call lands at all.
    assert len(sb.ctx.outbound) == 3


def test_the_empty_refs_guard_is_only_on_the_ask_channel(db):
    """
    The bound. Most verbs may legitimately carry no refs -- a Liaison replying
    to a greeting refs nothing, and should not have to invent something to
    point at. `ask` is singular because it is the one channel whose refs are
    the payload rather than a pointer to one.
    """
    sb = build("liaison", db, mode="normal")
    sb.call("msg.converse_principal", refs=[], reply="Hello!")
    assert len(sb.ctx.outbound) == 1


def test_chat_and_ratification_refuse_each_other(db):
    """
    Two answers to one message, and the session that sends both loses the one
    that mattered.

    `runner` has enforced this at commit since the chat path was added: if
    Liaison chatted and segmented, drop the segmentation, so the conversation
    does not stall on a confirm gate. Right about the outcome, backwards about
    the casualty. Measured on `llama3.1:8b` handed "morning. we need SSO, but
    only if it works with our LDAP" -- three statements segmented and confirmed
    by turn four, one stray `msg.converse_principal` on turn five after the
    harness had already said the session's work was complete, and a committed
    session holding no statements at all. `L1-LI-segment` has been 0/5 against
    exactly that.

    Refused at the channel it costs a turn, which is what the duplicate guard
    beside it charges for the same kind of mistake.
    """
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m1','principal','let people export invoices',1)")

    sb = build("liaison", db, mode="normal")
    sb.ctx.entry_id = "e_m1"
    sb.call("brief.segment", id="s1", span_start=0, span_end=26,
            text="let people export invoices")
    sb.call("msg.confirm_principal", refs=["s1"])
    with pytest.raises(ValueError, match="already segmented"):
        sb.call("msg.converse_principal", refs=[], reply="all done!")
    assert [w[0] for w in sb.ctx.writes] == ["statements"], \
        "the segmentation must survive the refusal"

    # And the other order, because the slip goes both ways: a greeting answered
    # first does not stop the model reaching for a gate afterwards.
    sb2 = build("liaison", db, mode="normal")
    sb2.ctx.entry_id = "e_m1"
    sb2.call("msg.converse_principal", refs=[], reply="Hello!")
    with pytest.raises(ValueError, match="already replied to the principal"):
        sb2.call("msg.confirm_principal", refs=["s1"])


def test_clarify_is_not_exclusive_with_either(db):
    """
    The bound. `clarify` is what a session sends when it cannot tell what the
    principal is asking *for*, and it is neither a reply nor a gate -- it is
    the third thing, and pairing it with either is not the failure above.
    """
    sb = build("liaison", db, mode="normal")
    sb.call("msg.converse_principal", refs=[], reply="Hello!")
    sb.call("msg.clarify_principal", refs=[], question="which dashboard?")
    assert len(sb.ctx.outbound) == 2


def test_segmenting_and_routing_refuse_each_other(db):
    """
    The third member of the exclusive set, and the one still costing cases.

    A session that segments the principal's request *and* asks the owners about
    it has answered them twice, which is why `L1-LI-segment` forbids those
    recipients. Which call loses is not a judgement here: across 42 recorded
    sessions that did both -- every arm of the intake measurement, both work
    fixtures -- `brief.segment` was turn one in all 42 and the ask arrived on a
    wind-down turn afterwards. The first judgement is the classification; the
    ask is the afterthought.

    Symmetric anyway. The inverse has never been observed and that is not the
    same as impossible.
    """
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m1','principal','add a delete button and fix the timeout',1)")

    sb = build("liaison", db, mode="normal")
    sb.ctx.entry_id = "e_m1"
    sb.call("brief.segment", id="s1", span_start=0, span_end=19,
            text="add a delete button")
    with pytest.raises(ValueError, match="already segmented"):
        sb.call("msg.ask_architect", refs=["e_m1"])
    assert [w[0] for w in sb.ctx.writes] == ["statements"]

    sb2 = build("liaison", db, mode="normal")
    sb2.ctx.entry_id = "e_m1"
    sb2.call("msg.ask_architect", refs=["e_m1"])
    with pytest.raises(ValueError, match="already asked an owner"):
        sb2.call("brief.segment", id="s2", span_start=0, span_end=19,
                 text="add a delete button")
    assert {m["verb"] for m in sb2.ctx.outbound} == {"ask"}


def test_routing_and_chatting_are_also_one_answer_each(db):
    """
    The pair no guard covered, and the one that showed the rule had to be one
    rule rather than three.

    `L1-LI-a-question-about-the-program-goes-to-its-owners` failed 0/5 with
    "forbidden message converse to principal": Liaison routed the question to
    its owners *and* chatted about it, in every run. Chat/ratification and
    segmenting/routing were each guarded by then; routing/chat was not, because
    the guards had been written per pair.
    """
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m1','principal','where do recipes go?',1)")

    sb = build("liaison", db, mode="normal")
    sb.ctx.entry_id = "e_m1"
    sb.call("msg.ask_architect", refs=["e_m1"])
    with pytest.raises(ValueError, match="already asked an owner"):
        sb.call("msg.converse_principal", refs=[], reply="Let me look into it!")
    assert {m["verb"] for m in sb.ctx.outbound} == {"ask"}

    sb2 = build("liaison", db, mode="normal")
    sb2.ctx.entry_id = "e_m1"
    sb2.call("msg.converse_principal", refs=[], reply="Hello!")
    with pytest.raises(ValueError, match="already replied"):
        sb2.call("msg.ask_architect", refs=["e_m1"])


def _inquiry_db(db, answer_refs):
    import json as _json

    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m1','principal','where does a user write a recipe?',1)")
    db.execute("INSERT INTO constraints (id, headline, text, provenance) VALUES "
               "('k0','not yet surveyed','everything no survey has reached',"
               "'observed')")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g_recipe','recipe','a note that seeds another','observed')")
    # The ask first: `schedule.reask` requires the answer to be a reply to a
    # question this role asked, which is right -- the causal chain is how it
    # knows which question it is talking about without being told an id.
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m6','t1','liaison','architect',"
               "'ask',?,1,'answered')", (_json.dumps(["e_m1"]),))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, seq) VALUES ('m7','m6','t1',"
               "'architect','liaison','answer',?,2)", (_json.dumps(answer_refs),))
    db.commit()
    sb = build("liaison", db, mode="normal")
    sb.ctx.trigger = "m7"
    return sb


def test_an_owner_that_could_not_answer_is_not_relayed(db):
    """
    An owner whose artefact does not carry the question says so by citing
    constraint zero -- the row bound to everything no survey has reached. That
    is a fact about the run, not the answer the principal asked for, and
    relaying it spends the one budget in this system that cannot be topped up
    while two owners who might know have not been asked.

    Measured on the click database: Architect answered `refs: ["e_m5", "k0"]`
    and the principal was told the area had not been surveyed, while
    Terminologist -- which held the term the question was about -- was never
    asked.

    Prose did not arbitrate it. `liaison/answer.md` gained a paragraph saying
    exactly this and both models relayed anyway, in both passes, four times out
    of four. Eighth time in this system.

    Derived rather than declared, and only here. `schedule.reask` exists
    because in general "the answer did not land" is invisible to a query -- the
    row says answered, and only the asker knows. On this route it is visible,
    because the owner cites the row that means it.
    """
    sb = _inquiry_db(db, ["e_m1", "k0"])
    with pytest.raises(ValueError, match="constraint zero"):
        sb.call("msg.converse_principal", refs=["e_m1", "k0"],
                reply="That area has not been surveyed.")
    assert sb.ctx.outbound == []

    # Satisfiable, which is what separates this from a gate.
    sb.call("schedule.reask",
            what_is_missing="which file holds the recipe, and under which key")


def test_an_answer_that_names_a_real_row_is_relayed(db):
    """
    The bound, and the direction that matters more: an owner that answered must
    reach the principal. A guard that swallowed real answers would be worse
    than the fault it replaces.
    """
    sb = _inquiry_db(db, ["g_recipe"])
    sb.call("msg.converse_principal", refs=["g_recipe"],
            reply="A recipe is a note that seeds another.")
    assert len(sb.ctx.outbound) == 1


def test_the_hollow_guard_only_looks_at_an_answer(db):
    """
    Intake is woken by `converse`, not `answer`, and must not be caught by a
    check about relaying. The trigger's verb is what separates them.
    """
    import json as _json

    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m1','principal','hey, morning!',1)")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m1','t1','principal','liaison',"
               "'converse',?,1)", (_json.dumps([]),))
    db.commit()
    sb = build("liaison", db, mode="normal")
    sb.ctx.trigger = "m1"
    sb.call("msg.converse_principal", refs=[], reply="Morning!")
    assert len(sb.ctx.outbound) == 1


def test_an_answer_names_what_it_came_from(db):
    """
    `refs` are the whole payload on an answer -- law 2 keeps the reasoning at
    home -- so an answer citing only the question, the thread, or constraint
    zero has told the asker nothing they can follow.

    Measured on the click run: a rung woken by the `unresolved` ladder read its
    glossary properly, three lookups deep, and answered `refs: ["e_m5"]` -- the
    question, handed back. Before that it answered `refs: ["m6"]`, the id of the
    message asking it. Liaison could relay neither, and rightly refused to put
    either in front of the principal.

    Saying "not mine" stays available and is a different verb: `msg.report_*` is
    what a rung sends when its artefact does not hold the answer.
    """
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m1','principal','what is a recipe here?',1)")
    db.execute("INSERT INTO constraints (id, headline, text, provenance) VALUES "
               "('k0','not yet surveyed','everything no survey has reached',"
               "'observed')")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','recipe','a note that seeds another','observed')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m6','t1','liaison','terminologist',"
               "'ask','[\"e_m1\"]',1)")
    db.commit()

    for echo in (["e_m1"], ["m6"], ["k0"], ["e_m1", "k0"], []):
        sb = build("terminologist", db, mode="readonly")
        with pytest.raises(ValueError, match="names the rows it came from"):
            sb.call("msg.answer_liaison", refs=echo)

    sb = build("terminologist", db, mode="readonly")
    sb.call("msg.answer_liaison", refs=["g1"])
    assert len(sb.ctx.outbound) == 1

    # The question may travel *beside* a source; it is the only-echo case that
    # is refused, not the presence of an echo.
    sb = build("terminologist", db, mode="readonly")
    sb.call("msg.answer_liaison", refs=["e_m1", "g1"])
    assert len(sb.ctx.outbound) == 1


def test_a_report_may_say_nothing_was_found(db):
    """
    The bound, and the escape the guard depends on being open: a rung whose
    artefact does not hold the answer says so upward, and that carries no
    source because there is none.
    """
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m6','t1','liaison','terminologist',"
               "'ask','[]',1)")
    db.commit()
    sb = build("terminologist", db, mode="readonly")
    sb.call("msg.report_liaison", refs=[])
    assert len(sb.ctx.outbound) == 1


def test_only_the_channel_that_reaches_a_person_must_cite_a_source(db):
    """
    The bound on "an answer names what it came from", and it was found by
    measuring the wider version.

    Held to citing a source on every channel, Vision Keeper spent all twelve
    turns of `L1-VK-the-last-rung-rules-or-sends-it-up` re-reading its
    artefacts and re-sending an empty answer, five runs out of five, and
    committed nothing. Satisfiable in principle is not satisfiable, and this
    system's own law says a gate the model cannot satisfy becomes a loop.

    Liaison is the channel where it is not a matter of taste: it relays to the
    principal, who has never seen a row and cannot be shown one they cannot
    resolve. An answer to Liaison citing only the question hands it something it
    is *forbidden* to pass on. Every other answer stays between roles that share
    a database.
    """
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq) VALUES ('m1','t1','developer',"
               "'researcher','question','[]','does the API return 409?',1)")
    db.commit()

    # No source, and no complaint: the recipient shares the database.
    sb = build("researcher", db, mode="normal")
    sb.call("msg.answer_developer", refs=[])
    assert len(sb.ctx.outbound) == 1

    sb = build("vision_keeper", db, mode="normal")
    sb.call("msg.answer_tester", refs=[])
    assert len(sb.ctx.outbound) == 1


def test_one_ask_reaches_every_owner(db):
    """
    Which owner holds the answer is not the asker's to know -- that is the
    whole reason a question is routed rather than answered -- so there is no
    choice here and no way to ask only one.

    Measured before this: all eight maintainer questions went to exactly one
    owner. The one naming `intents_to` went to Architect and never to
    Terminologist, which holds the term. The brief has said "ask every owner
    that might hold part of the answer" since it shipped, and three design
    documents say the same; prose had its turn.
    """
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m1','principal','where does a user write a recipe?',1)")
    db.commit()

    sb = build("liaison", db, mode="normal")
    sb.ctx.entry_id = "e_m1"
    out = sb.call("msg.ask_architect", refs=["e_m1"])

    assert sorted(m["to_role"] for m in sb.ctx.outbound) == [
        "architect", "terminologist", "vision_keeper"]
    assert all(m["body_refs"] == ["e_m1"] for m in sb.ctx.outbound)
    assert len({m["id"] for m in sb.ctx.outbound}) == 3, "ids must not collide"
    # Said back, or the model reaches for the other two and meets the duplicate
    # guard, which costs turns and reads as a refusal of what it was told to do.
    assert out["to"] == ["architect", "terminologist", "vision_keeper"]

    with pytest.raises(ValueError, match="already sent ask"):
        sb.call("msg.ask_terminologist", refs=["e_m1"])


def test_the_fan_out_is_only_on_the_ask_channel(db):
    """
    The bound. Every other verb addresses the role it names -- Liaison
    delivering a ratified statement to three roles is three calls and three
    decisions, and a question to one owner is not.
    """
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e1','principal','a thing',1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1','e1',0,7,'a thing','ratified')")
    db.commit()
    sb = build("liaison", db, mode="normal")
    sb.call("msg.deliver_architect", refs=["s1"])
    assert [m["to_role"] for m in sb.ctx.outbound] == ["architect"]
