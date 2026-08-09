"""
Edge coverage: the graph generates the obligation.

Every read, write and message edge must be exercised somewhere in the suite. The
point is not the number — it is that **drawing an edge creates a red row**. A new
capability cannot be added without something being obliged to test it, and the
obligation cannot drift from the design because the design generates it.

Run the suite with coverage recording on:

    ROTA_COVERAGE_ON=1 python -m pytest tests/rota -q
    python -m rota.testkit.coverage          # the matrix
"""
from __future__ import annotations

import os

import pytest

from rota.testkit import coverage
from rota.design import graph as graph_mod


def test_every_declared_edge_is_enumerable():
    """Sanity: the obligation set is derived from the graph, not hand-listed."""
    edges = coverage.all_edges()
    g = graph_mod.load()
    assert edges, "no edges enumerated"
    assert {e.role for e in edges} <= set(g.roles)
    # every role owns at least one edge, or it is a role that cannot act
    for role in g.roles:
        assert any(e.role == role for e in edges), f"{role} has no edges"


@pytest.mark.skipif(
    not os.environ.get("ROTA_COVERAGE_ON"),
    reason="coverage accumulates across the suite; set ROTA_COVERAGE_ON=1",
)
def test_edge_coverage_is_complete():
    rep = coverage.report()
    assert not rep.missing, "\n" + coverage.render(rep)
