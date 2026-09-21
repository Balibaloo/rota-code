"""
L3 — handoffs. Does A's message make B do the right thing?

The tier the design rests on, and the only one that cannot be assembled out of
two independent cases. Everywhere else a role is handed a message somebody wrote
by hand, which measures whether it can act on a *well-formed* message. Here the
second session is woken by the first session's own outbound row — same verb,
same refs, nothing rewritten in between.

What is under test is the claim the whole system makes: **that conclusions
travelling as refs, with the reasoning left at home, carry enough for a stranger
to act on.** A chain that fails because A said too little is not a bug in the
test; it is the finding.

    ROTA_L1=1 ROTA_MODEL=qwen3:8b python -m pytest tests/rota/test_l3.py -q

Name the model. Without `ROTA_MODEL` this tier records against `llama3.1:8b`,
which is not the model the gate replays, and two cases scored 0 of 5 on the
wrong model alone (observed: frame 60, 2026-09-21). A STALE failure prints the
whole command, with the window and the profile it would run under.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

import rota_serial_plugin

from rota import paths
from rota.llm.cassettes import (RecordingBackend, ReplayOnlyBackend,
                               open_dev_db, record_case_run)
from rota.llm.llm import OllamaBackend, Pins, think_for
from rota.testkit import fixtures

CASES = Path(__file__).parent / "cases"
MODEL = os.environ.get("ROTA_MODEL", "llama3.1:8b")
# num_ctx comes from `DEFAULT_NUM_CTX` and is deliberately not pinned here.
# It was pinned, at 8192, and stayed there when the default was raised to
# 12288 to stop the largest prompts being clipped -- so the fix reached
# everything except the suites that measure whether anything works. Two
# cases were still reporting `8192 tokens evaluated against a 8192 window`
# long after that was supposed to be impossible, and a prompt is truncated
# from the front, where the role is told who it is.
# The think pin comes from `ROTA_PROFILE`, through the one rule in
# `rota.llm.llm`. This tier read no profile while `test_l1.py` did, so one run
# under a profile recorded the same model at two keys (frame 54, 2026-09-21).
PINS = Pins(model=MODEL, temperature=0.0, think=think_for(MODEL))

# The door, called from the file that reads the register (frame 54,
# 2026-09-21). It refuses a replay whose ambient key the register does
# not hold. It is called here and not from a pytest hook: a hook that
# raises after collection runs on an xdist worker and ends the run in
# INTERNALERROR, with the reason nowhere in the output.
rota_serial_plugin.refuse_a_key_the_register_does_not_hold()

pytestmark = pytest.mark.skipif(
    not (os.environ.get("ROTA_L1") or paths.DEV_DB.exists()),
    reason="no cassettes recorded; set ROTA_L1=1 to run against a model",
)


def _chains() -> list[dict]:
    out = []
    for path in sorted(CASES.glob("l*.yaml")):
        out.extend(c for c in (fixtures.load_case(path) or []) if c.get("first"))
    # Same-model cases stay contiguous: each alternation of the
    # bar model is a full weight reload on a GPU that fits one.
    out.sort(key=lambda c: c.get("model", ""))
    return out


@pytest.fixture(scope="session")
def dev_db():
    paths.DEV_DB.parent.mkdir(parents=True, exist_ok=True)
    return open_dev_db(paths.DEV_DB)


@pytest.fixture
def backend_factory(dev_db):
    """Replay unless told otherwise — see the note in `test_l1.py`."""
    if not os.environ.get("ROTA_L1"):
        return lambda: ReplayOnlyBackend(dev_db)
    refresh = bool(os.environ.get("ROTA_REFRESH"))
    return lambda: RecordingBackend(
        OllamaBackend(), dev_db, refresh=refresh)


@pytest.mark.parametrize("case", _chains(), ids=[c["id"] for c in _chains()])
def test_l3_chain(case, tmp_path, backend_factory, dev_db):
    """
    Thresholds are lower here than at L2 and that is not a concession.

    A chain multiplies two sampled judgements, so 4-of-5 on each hop is 3-of-5
    on the pair before anything has gone wrong. Holding L3 to L2's bar would
    measure the product of two rates and report it as one.
    """
    # The ruling (2026-08-29): we are not locked to a model --
    # one model carrying the capability is enough. A case that
    # declares `model:` is held by that model; the default stays
    # the recording reference.
    pinned = case.get("model", MODEL)
    pins = Pins(model=pinned, temperature=0.0, think=think_for(pinned))
    passed, threshold, results = fixtures.run_sampled(
        case, tmp_path, backend_factory, pins=pins)

    # Both legs' briefs, because either one can be why the chain stopped
    # working. This tier recorded against bare pins with no prompt hash at all,
    # so a chain could stay green against briefs that had since been rewritten
    # and nothing could tell -- the distinction `test_l1.py` calls out as the
    # difference between a green result and a green result about a prompt that
    # has since been edited, missing from the tier that most needs it.
    stamp = pins.with_prompt(fixtures.instructions_for(case))
    for r in results:
        # Both legs' system texts, joined, for the same reason the stamp holds
        # both briefs: either leg can be why the chain stopped working.
        record_case_run(dev_db, case["id"], stamp, r.run, r.passed,
                        r.problems, r.transcript(), system=r.system_text())

    # Unknown is not wrong — see the note in `test_l1.py`.
    if any("no cassette" in p for r in results for p in r.problems):
        pytest.fail(
            f"STALE {case['id']}: no recording for the current prompt — this "
            f"result is unknown, not bad. Re-earn it with\n"
            f"    "
            + fixtures.rerecord_command(pins, "tests/rota/test_l3.py"))

    assert passed >= threshold, (
        f"{case['id']}: {passed}/{len(results)} passed, needs {threshold}\n"
        + "\n".join(f"  run {r.run}: {'; '.join(r.problems)}"
                    for r in results if r.problems))


def test_a_chain_case_declares_both_ends():
    """
    `first` and `then` are the whole shape. A chain missing either is a single
    session wearing a chain's id, and it would pass while testing nothing about
    the handoff it is named for.
    """
    bad = [c["id"] for c in _chains()
           if not (c.get("first") or {}).get("role")
           or not (c.get("then") or {}).get("role")]
    assert not bad, bad
