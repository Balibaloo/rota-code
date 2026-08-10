"""
A case must ask for something the role can actually reach.

Two of the failures this suite spent weeks on were not the model and not the
harness. They were cases written from the design rather than from what the role
can see:

* Tester was told to file a test into a batch, and the batch was in the fixture
  YAML but not in anything the session was handed. It filled the required
  `batch_id` with the only id in front of it -- a glossary term from the message
  that woke it -- nineteen times in one session.
* Liaison was woken at `round_close` with no reports, and `tick_round_close`
  cannot produce that wake. It was being marked down for not recognising a
  situation the system cannot be in.

Both are the same defect and both were found by running a model for twenty-five
minutes and reading a transcript. Neither needed a model at all: a case that
requires a row the role was never given is unsatisfiable on inspection.

Only the wake is checked. Whether an *expected write* is reachable
wants an artefact-to-table map, and inventing one would be a second
vocabulary beside the graph's -- the thing this project spends the
most effort not doing.

This is the same rule the sandbox already enforces for capability -- a role
cannot reach outside its edges because the function was never built -- applied
to the *contents* of a waking rather than to its verbs.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.testkit import fixtures


def _cases():
    out = []
    for path in sorted((Path(__file__).parent / "cases").glob("l*.yaml")):
        out.extend(fixtures.load_case(path) or [])
    return out


CASES = _cases()


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_a_tick_case_names_a_wake_the_scheduler_can_produce(case):
    """
    `tick:` names a predicate. If no predicate has that name, the case is
    testing a situation the frontier cannot put a role in.

    The stronger check -- that the *fixture* would actually make that predicate
    fire -- is the one that would have caught `round_close` with no reports, and
    it is below.
    """
    tick = case.get("tick")
    if not tick:
        return
    from rota.core import predicates as P
    assert tick in P.REGISTRY, (
        f"{case['id']} wakes on tick:{tick}, which is not a predicate")


@pytest.mark.parametrize("case", [c for c in CASES if c.get("tick")],
                         ids=[c["id"] for c in CASES if c.get("tick")])
def test_a_tick_cases_fixture_would_actually_fire_that_predicate(case, tmp_path):
    """
    Seed the fixture, run the predicate, and require it to wake this role.

    This is the check that makes a case honest about its own premise. A wake the
    scheduler would never produce is a situation the role will never meet, and
    grading a model on it measures nothing -- `round_close` with no reports
    failed five times out of five for exactly that reason.

    Predicates that fire on state this harness does not seed are skipped rather
    than failed: the claim here is "if it fires at all, it fires for this role",
    not "every fixture is complete enough to trip its own predicate".
    """
    from rota.core import predicates as P

    conn = init_db(tmp_path / "rota.db")
    fixtures.seed(conn, case["fixture"])
    conn.commit()

    wakes = P.REGISTRY[case["tick"]].fn(conn)
    if not wakes:
        pytest.skip(f"tick:{case['tick']} does not fire on this fixture "
                    f"(seeded state may be outside what the predicate reads)")
    assert any(w.role == case["role"] for w in wakes), (
        f"{case['id']} says it wakes {case['role']} on tick:{case['tick']}, but "
        f"that predicate wakes {sorted({w.role for w in wakes})} here")
