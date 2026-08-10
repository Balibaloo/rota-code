"""
Reach, as two axes.

`a:` was one word answering two questions — which rows, and how much of each —
and the proof is that `full` and `index` both existed while `problem.consult`'s
own docstring said "Full scope = the full index". What `full` was really carrying
was authority, so it became a rule instead of a value.
"""
from __future__ import annotations

import pytest

from rota.design import graph as graph_mod
from rota.design.graph import DEPTH, ROWS, Edge, check_structure


@pytest.fixture
def g():
    return graph_mod.load()


def test_every_edge_declares_legal_reach(g):
    assert check_structure(g) == []


def test_full_is_gone(g):
    """It named a permission, not a reach, and returned the same rows as `index`."""
    assert "full" not in ROWS and "full" not in DEPTH
    assert not [e for e in g.edges if e.rows == "full" or e.depth == "full"]


def test_depth_is_a_read_concept_only(g):
    """
    A message carries refs, never bodies — that is a law, not a setting. Giving
    non-read edges a depth field would be inventing data to fill a column.
    """
    wrong = [f"{e.s}->{e.t} ({e.type})" for e in g.edges
             if e.depth and e.type != "reads"]
    assert not wrong, wrong


def test_every_read_declares_both_axes(g):
    missing = [f"{e.s}->{e.t}" for e in g.of_type("reads")
               if not e.rows or not e.depth]
    assert not missing, missing


def test_the_authority_rule_can_fail(g):
    """
    Nothing violates it today, which is what a green lint means — but a lint
    nobody has watched fail is one you are trusting rather than using.

    The shape it forbids: a role taking every row of an artefact it does not own,
    bodies and all.
    """
    trespass = Edge(s="critic", t="model", type="reads", v="consult",
                    rows="all", depth="body")
    bad = graph_mod.Graph(list(g.nodes.values()), g.edges + [trespass],
                          g.contact_exceptions)

    problems = check_structure(bad)
    assert any("takes model whole" in p for p in problems), problems


def test_owning_it_makes_the_same_read_legal(g):
    """The rule is about authority. Architect owns the model; same reach, allowed."""
    owned = Edge(s="architect", t="model", type="reads", v="consult",
                 rows="all", depth="body")
    ok = graph_mod.Graph(list(g.nodes.values()), g.edges + [owned],
                         g.contact_exceptions)
    assert check_structure(ok) == []


def test_an_unknown_reach_value_is_caught(g):
    bad = graph_mod.Graph(
        list(g.nodes.values()),
        g.edges + [Edge(s="critic", t="tests", type="reads", v="load",
                        rows="most", depth="body")],
        g.contact_exceptions)
    assert any("unknown rows 'most'" in p for p in check_structure(bad))


# ---------------------------------------------------------------------------
# The cascade — P2
# ---------------------------------------------------------------------------

def test_the_refs_graph_is_acyclic(g):
    """
    It is called a DAG in three docstrings and in law 9, and it was not one:
    `model → code → batches → model`. Nothing asserted it, and `cascade_order`
    swallowed the cycle and returned alphabetical order — so the documented
    behaviour never ran and looked exactly like it had.
    """
    assert graph_mod.check_refs_acyclic(g) == []


def test_every_artefact_crossing_foreign_key_has_a_refs_edge(g):
    """
    Nothing referenced `tickets`, so re-slicing one cascaded to nothing while
    its criteria, its batch and its tests kept working from wording that no
    longer existed. Seven crossings had no edge — the refs graph was drawn
    around the understanding artefacts and left thin around the delivery ones.
    """
    assert graph_mod.check_refs_cover_the_schema(g) == []


def test_cascade_order_is_not_alphabetical():
    """The tell that the fallback was running. Law 9 promises model → backlog →
    schedule; alphabetical order gives batches first."""
    from rota.core.scheduler import cascade_order

    order = cascade_order()
    assert order != sorted(order)
    assert order.index("model") < order.index("batches") < order.index("schedule")


def test_a_cycle_is_raised_not_swallowed(g):
    """
    A fallback that silently changes documented behaviour is worse than the
    failure it hides: every cascade fired in the wrong order for the life of the
    system and nothing said so.
    """
    from rota.core.scheduler import UnorderableCascade, cascade_order

    looped = graph_mod.Graph(
        list(g.nodes.values()),
        g.edges + [Edge(s="model", t="verdicts", type="refs", v="loop")],
        g.contact_exceptions)
    with pytest.raises(UnorderableCascade):
        cascade_order(looped)


def test_a_non_cascading_ref_is_excluded_from_the_order(g):
    """`model → code` is a binding — the mechanical intersection that triggers
    structural review — not a path a change propagates along. Keeping it in the
    order is what closed the cycle."""
    binding = [e for e in g.of_type("refs")
               if e.s == "model" and e.t == "code"]
    assert binding and binding[0].cascade is False


def test_amending_a_ticket_reaches_its_criteria_batch_and_tests():
    from rota.cockpit.inspect_api import blast_radius

    woken = {w["artefact"] for w in blast_radius("tickets")["wakes"]}
    assert {"criteria", "batches", "tests"} <= woken, woken


def test_a_clean_finding_wakes_nobody(tmp_path):
    """
    Binding `findings` to `model` meant one *satisfied* finding — a review
    saying nothing is wrong — cascaded as though the system model had changed,
    waking the whole delivery chain including the role that had just written it.
    """
    from rota.core.db import SessionResult, Write, init_db, session_commit
    from rota.core.scheduler import cascade_wakes

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id,text,kind,provenance) "
               "VALUES ('i1','x','in_scope','decided')")
    db.execute("INSERT INTO batches (id,item_id) VALUES ('b1','i1')")
    db.execute("INSERT INTO constraints (id,headline,provenance) "
               "VALUES ('k1','x','decided')")

    session_commit(db, SessionResult(session_id="s1", role="architect", writes=[
        Write("findings", "f1", {"batch_id": "b1", "constraint_id": "k1",
                                 "status": "satisfied", "grain": "g"})]))

    assert cascade_wakes(db, "s1") == []
