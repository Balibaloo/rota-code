"""
G — seat-flow segments. The gauntlet's case tier.

The refined spec (LOOPS.md, "The gauntlet"): the principal says one thing and
the segment pins the pipeline it must travel — verified against the tables,
escalated to the role that owns it, brought back to the seat, never just
accepted. Both failure directions are cases: silent overreach and punting.

Mechanically this is the L1/L3 machinery pointed at `g*.yaml` — same fixtures,
same recording, same bar — because a segment *is* a case: a realistic table
state with one trap in it and expectations for what the system should do.
Composed flows and full stories build on these; a segment that fails is a
specification, not a broken test, which is the same stance `test_l3.py` takes
on a handoff that says too little.

    ROTA_L1=1 python -m pytest tests/rota/test_gauntlet.py -q
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from rota import paths
from rota.llm.cassettes import (RecordingBackend, ReplayOnlyBackend,
                               open_dev_db, record_case_run)
from rota.llm.llm import OllamaBackend, Pins
from rota.testkit import fixtures

CASES = Path(__file__).parent / "cases"
MODEL = os.environ.get("ROTA_MODEL", "llama3.1:8b")
PINS = Pins(model=MODEL, temperature=0.0)

pytestmark = pytest.mark.skipif(
    not (os.environ.get("ROTA_L1") or paths.DEV_DB.exists()),
    reason="no cassettes recorded; set ROTA_L1=1 to run against a model",
)


def _segments() -> list[dict]:
    out = []
    for path in sorted(CASES.glob("g*.yaml")):
        out.extend(fixtures.load_case(path) or [])
    return out


@pytest.fixture(scope="session")
def dev_db():
    paths.DEV_DB.parent.mkdir(parents=True, exist_ok=True)
    return open_dev_db(paths.DEV_DB)


@pytest.fixture
def backend_factory(dev_db):
    if not os.environ.get("ROTA_L1"):
        return lambda: ReplayOnlyBackend(dev_db)
    refresh = bool(os.environ.get("ROTA_REFRESH"))
    return lambda: RecordingBackend(
        OllamaBackend(timeout=300), dev_db, refresh=refresh)


@pytest.mark.parametrize("case", _segments(), ids=[c["id"] for c in _segments()])
def test_seat_flow_segment(case, tmp_path, backend_factory, dev_db):
    passed, threshold, results = fixtures.run_sampled(
        case, tmp_path, backend_factory,
        # The ruling (2026-08-29): we are not locked to a model --
        # one model carrying the capability is enough. A case that
        # declares `model:` is held by that model; the default stays
        # the recording reference.
        pins=Pins(model=case.get("model", MODEL), temperature=0.0))

    stamp = Pins(model=case.get("model", MODEL), temperature=0.0).with_prompt(fixtures.instructions_for(case))
    for r in results:
        record_case_run(dev_db, case["id"], stamp, r.run, r.passed,
                        r.problems, r.transcript())

    if any("no cassette" in p for r in results for p in r.problems):
        pytest.fail(
            f"STALE {case['id']}: no recording for the current prompt — this "
            f"result is unknown, not bad. Re-earn it with\n"
            f"    ROTA_L1=1 python -m pytest tests/rota/test_gauntlet.py -q")

    assert passed >= threshold, (
        f"{case['id']}: {passed}/{len(results)} passed, needs {threshold}\n"
        + "\n".join(f"  run {r.run}: {'; '.join(r.problems) or 'ok'}"
                    for r in results))


def test_a_question_is_never_a_statement_to_ratify(tmp_path):
    """Deterministic pin for the segment guard the punting fixture surfaced:
    handed a question, intake segmented it into statements and sent the
    principal their own words back to confirm, five runs of five. A span
    whose sentence ends in a question mark asks; asking is answered or
    routed, never proposed for ratification."""
    from rota.core.db import init_db
    from rota.core.sandbox import build

    import pytest as _pytest

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e1','principal',1,"
               "'remind me, what did we decide about invoice retention?')")
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e2','principal',2,"
               "'people should be able to export recipes as csv. fast enough?')")
    db.commit()

    sb = build("liaison", db, mode="converse", entry_id="e1")
    with _pytest.raises(ValueError, match="never a statement to ratify"):
        sb.call("brief.segment", id="s1", span_start=11, span_end=53,
                text="what did we decide about invoice retention")

    sb2 = build("liaison", db, mode="converse", entry_id="e2")
    out = sb2.call("brief.segment", id="s2", span_start=0, span_end=46,
                   text="people should be able to export recipes as csv")
    assert out["id"] == "s2", "the statement half of a mixed entry still lands"
