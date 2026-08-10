"""
L1 — every action a role can take, against a real model.

The tier that gives the vocabulary rework its verdict. Everything below it
proves the machine; this asks whether a role, told what it is answerable for and
handed a state where exactly one action is right, takes that action.

Cassettes make it affordable: the first run pays model time, every run after it
replays for nothing, and a prompt edit produces a miss — which is correct,
because a recording made against a different prompt is not evidence about this
one.

    ROTA_L1=1 python -m pytest tests/rota/test_l1.py -q        # record or replay
    ROTA_L1=1 ROTA_REFRESH=1 python -m pytest tests/rota/test_l1.py -q   # re-record

Serialised on purpose: no `xdist` here. Parallel model calls thrash the GPU and
the timings stop meaning anything.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from rota import paths
from rota.llm.cassettes import RecordingBackend, open_dev_db, record_case_run
from rota.llm.llm import OllamaBackend, Pins
from rota.roles import prompts
from rota.testkit import fixtures, obligations

CASES = Path(__file__).parent / "cases"
MODEL = os.environ.get("ROTA_MODEL", "llama3.1:8b")
# num_ctx comes from `DEFAULT_NUM_CTX` and is deliberately not pinned here.
# It was pinned, at 8192, and stayed there when the default was raised to
# 12288 to stop the largest prompts being clipped -- so the fix reached
# everything except the suites that measure whether anything works. Two
# cases were still reporting `8192 tokens evaluated against a 8192 window`
# long after that was supposed to be impossible, and a prompt is truncated
# from the front, where the role is told who it is.
PINS = Pins(model=MODEL, temperature=0.0)

pytestmark = pytest.mark.skipif(
    not os.environ.get("ROTA_L1"),
    reason="L1 hits a real model or its cassettes; set ROTA_L1=1 to run",
)


def _cases() -> list[dict]:
    out = []
    for path in sorted(CASES.glob("l*.yaml")):
        out.extend(c for c in (fixtures.load_case(path) or [])
                   if not c.get("first"))     # chains are L3's, in test_l3.py
    return out


def _ids(cases) -> list[str]:
    return [c["id"] for c in cases]


@pytest.fixture(scope="session")
def dev_db():
    paths.DEV_DB.parent.mkdir(parents=True, exist_ok=True)
    return open_dev_db(paths.DEV_DB)


@pytest.fixture
def backend_factory(dev_db):
    refresh = bool(os.environ.get("ROTA_REFRESH"))
    return lambda: RecordingBackend(
        OllamaBackend(timeout=300), dev_db, refresh=refresh)


@pytest.mark.parametrize("case", _cases(), ids=_ids(_cases()))
def test_l1_case(case, tmp_path, backend_factory, dev_db):
    """
    Sampled, with a threshold. The count is kept rather than a bare boolean so a
    drift from 5/5 to 3/5 is visible as the regression it is.
    """
    instructions = prompts.compose(case["role"], fixtures.mode_of(case))

    passed, threshold, results = fixtures.run_sampled(
        case, tmp_path, backend_factory, pins=PINS, instructions=instructions)

    # Recorded against the instructions rather than the bare pins, so the
    # cockpit can tell a green result from a green result about a prompt that
    # has since been edited. Instructions only — the full prompt includes the
    # fixture, which would make every case's hash unique and staleness
    # meaningless.
    stamp = PINS.with_prompt(instructions)
    for r in results:
        record_case_run(dev_db, case["id"], stamp, r.run, r.passed,
                        r.problems, r.transcript())

    assert passed >= threshold, (
        f"{case['id']}: {passed}/{len(results)} passed, needs {threshold}\n"
        + "\n".join(f"  run {r.run}: {'; '.join(r.problems)}"
                    for r in results if r.problems))


# ---------------------------------------------------------------------------
# The obligation set — which of them have a case
# ---------------------------------------------------------------------------

def test_the_obligation_set_comes_from_the_graph():
    """Drawing an edge creates a red row. The map cannot drift from the design,
    because the design emits it."""
    counts = obligations.summary()
    assert counts["L1"] > 100 and counts["L2"] > 40 and counts["L3"] > 200


def test_every_mode_has_a_case():
    """
    One case per prompt piece, which is the unit a pass-rate drop is
    attributable to.

    Stronger than it looks: a mode is a role plus what woke it, and the modes are
    enumerable from the graph rather than from a list somebody maintains. Adding
    a mode file with no case turns this red, which is the point — the modes that
    went longest without one were Developer's, and both of them had tool lists
    that could not do what the prose asked.
    """
    from rota.design import graph as graph_mod

    covered = {(c["role"], fixtures.mode_of(c)) for c in _cases()}
    missing = sorted(
        f"{role}/{mode}"
        for role in graph_mod.load().roles
        for mode in prompts.available(role)
        if (role, mode) not in covered)
    assert not missing, f"{len(missing)} mode(s) with no L1 case: {missing}"


@pytest.mark.skipif(True, reason="the obligation set is not yet fully covered")
def test_every_l1_obligation_has_a_case():
    """
    The target. Skipped rather than deleted: a red row you can see is worth more
    than an obligation nobody wrote down, and this is the one that says how far
    there is to go.
    """
    covered = set()
    for case in _cases():
        for table in ((case.get("expect") or {}).get("writes") or {}):
            covered.add(f"{case['role']}:{table}")
    missing = [o.id for o in obligations.l1()
               if f"{o.role}:{o.what.split('.')[0]}" not in covered]
    assert not missing, f"{len(missing)} L1 obligations with no case"
