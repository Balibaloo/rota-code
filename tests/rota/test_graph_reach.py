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
