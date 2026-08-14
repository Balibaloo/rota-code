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
