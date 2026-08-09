"""
T0-S9 — the sandbox surface *is* the working set.

The claim under test is structural: a role cannot reach outside its edges because
the capability was never built, not because a check refused it.
"""
from __future__ import annotations

import pytest

from rota import graph as graph_mod
from rota.api import Ctx
from rota.db import init_db
from rota.sandbox import (
    NotInWorkingSet, build, check_implementations, check_no_orphan_implementations,
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
    consult = build("gatekeeper", db, mode="consult")

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
    from rota.sandbox import drain_calls

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
    sb.call("problem.assert", id="i1", text="delete account", kind="scope")

    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 0
    assert sb.ctx.writes == [("items", "i1", {
        "text": "delete account", "kind": "scope",
        "provenance": "decided", "approval": "draft"})]
