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


def test_every_message_edge_is_exercised_or_on_the_backlog():
    """
    Ten edges no case touches, pinned by name (2026-08-28). The pin cuts both
    ways: drawing a new message edge without a case fails here, and writing a
    case for a backlog edge fails here too -- the list must shrink in the
    same commit, so the backlog cannot silently rot in either direction.
    The two genuinely distinct flows came off the list first
    (critic->tester challenge; architect->liaison report -- the latter found
    a door the graph drew and the exhausted mode never offered). Three more
    came off 2026-09-01: tester->terminologist question is the nearest desk
    the collapsed triage routes to, and two answer edges had been covered by
    `any_of` arms all along -- the counter was blind to arms until then. The
    five remaining are answer/question flavours of covered machinery.
    """
    import json
    from pathlib import Path as _P

    import yaml as _yaml

    g = json.load(open(_P("rota/design/graph.json")))
    edges = {(e["s"], e["t"], e["v"]) for e in g["edges"]
             if e.get("type") == "messages"}

    touched = set()
    for path in _P("tests/rota/cases").glob("*.yaml"):
        for c in _yaml.safe_load(path.read_text(encoding="utf-8")) or []:
            inb = c.get("inbound") or {}
            if isinstance(inb, dict) and inb.get("verb"):
                touched.add((inb.get("from"), inb.get("to"), inb["verb"]))
            first, then = c.get("first") or {}, c.get("then") or {}
            if first.get("verb") and then.get("role"):
                touched.add((first.get("role"), then["role"], first["verb"]))
            actor = c.get("role") or first.get("role")
            # An `any_of` arm is an expectation the case can pass on, so it
            # exercises its edge exactly as a flat expect does -- the two
            # routing cases became any_of (nearest desk or sharp desk) on
            # the 2026-09-01 collapse and would otherwise read as uncovered.
            expect = c.get("expect") or {}
            for body in (expect, *(expect.get("any_of") or [])):
                for m in (body.get("messages") or []):
                    if m.get("verb"):
                        touched.add((actor, m.get("to"), m["verb"]))

    BACKLOG = {
        ("researcher", "tester", "answer"),
        ("terminologist", "architect", "answer"),
        ("architect", "terminologist", "question"),
        ("terminologist", "researcher", "question"),
        ("vision_keeper", "researcher", "question"),
    }
    untouched = edges - touched
    assert untouched == BACKLOG, (
        f"newly uncovered: {sorted(untouched - BACKLOG)}; "
        f"covered but still on the backlog: {sorted(BACKLOG - untouched)}")
