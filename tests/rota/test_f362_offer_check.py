"""Frame 362, pass 4d: a door checks its offer through the checks that follow.

Frame 211 (2026-10-12): "the door offers no call it refused in the same
reply". The gate of 2026-11-04 found two follow-check reds. The encode door
offered a body with `import sys` added, and the run check of the same door
refused that body. The scalar door offered the seat's placeholder
`criterion_id='criterion_id'`, and `_must_exist` refused it. Each test sends
the case's own call on the case's own fixture. The conftest follow check
sends each recorded offer through the doors again.
"""
from __future__ import annotations

import pathlib
import sqlite3

from rota.llm.llm import Pins, ScriptedBackend
from rota.testkit import fixtures
from tests.rota.test_night46_context import db  # noqa: F401

CASES = pathlib.Path(__file__).resolve().parent / "cases"


def _case(name: str, case_id: str) -> dict:
    case = next(c for c in fixtures.load_case(CASES / name)
                if c["id"] == case_id)
    return fixtures.for_run(case, 1)


def _run(tmp_path, case: dict, calls: list[str]):
    seat = ScriptedBackend([*calls, "done"])
    db = tmp_path / "case.db"
    fixtures.run_case(case, db, seat, pins=Pins(model="scripted"),
                      instructions=fixtures.instructions_for(case))
    return seat, sqlite3.connect(db)


def test_the_scalar_door_offers_the_one_criterion_and_not_the_placeholder(
        tmp_path):
    """The gemma3:12b turn of L1-CR-a-test-that-encodes-nothing-is-a-challenge
    on 2026-11-04. The offer carries the one criteria row, so the resend
    meets no `_must_exist` refusal."""
    case = _case("l1_judgement.yaml",
                 "L1-CR-a-test-that-encodes-nothing-is-a-challenge")
    seat, conn = _run(tmp_path, case, [
        "TOOL: verdicts.claim_encodes(criterion_id='criterion_id', "
        "encodes='encodes')"])
    (crit,), = conn.execute("SELECT id FROM criteria").fetchall()
    said = seat.calls[1][1]
    assert "encodes='encodes' is a word where" in said, said
    assert "'criterion_id' is no row of criteria" in said, said
    assert f"Send criterion_id={crit!r}" in said, said


# The qwen3.5:9b body of ACT-TS-give-the-prompt-a-stream on 2026-11-04, word
# for word. It uses `sys` with no import, and it calls `confirm` with no
# `text`.
STREAM_BODY = (
    'import io\nfrom src.ui import confirm\n\n'
    'def test_confirm_returns_default_when_stdin_is_closed():\n'
    '    sys.stdin = io.StringIO("")\n'
    '    default_value = "default_answer"\n'
    '    result = confirm(default_on_eof=True, default=default_value)\n'
    '    assert result == default_value')


def test_the_import_door_names_the_fault_that_the_run_finds_in_its_body(
        tmp_path):
    """The import door runs the body it would offer. The run fails in the
    arrange step, so the refusal names both faults and offers no call."""
    case = _case("l1_acts.yaml", "ACT-TS-give-the-prompt-a-stream")
    (crit,) = [c["id"] for c in case["fixture"]["criteria"]]
    batch = case["repo"]["batch"]
    seat, _ = _run(tmp_path, case, [
        f"TOOL: tests.triage(criterion_id={crit!r}, verdict='encodable')\n"
        f"TOOL: tests.encode(id='tst_eof_default', criterion_id={crit!r}, "
        f"path='tests/test_confirm_eof.py', body={STREAM_BODY!r}, "
        f"batch_id={batch!r})"])
    said = seat.calls[1][1]
    assert "the test uses sys and never imports it" in said, said
    assert "Before you send it, fix a second fault." in said, said
    assert "The test fails in its own arrange step" in said, said


def test_the_scalar_door_reads_every_word_before_it_offers(db, tmp_path):
    """The second look at passes 4c to 4e, low D. The offer fixed `start`
    only, and the same door refused `end` on resend."""
    import pytest

    from rota.core import sandbox
    from rota.testkit import gitfixture

    repo = gitfixture.make(tmp_path, name="scalar_repo")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
               "('project_root', ?)", (str(repo.root),))
    sb = sandbox.build("architect", db)
    sb.ctx.offers = []
    with pytest.raises(sandbox.ArgumentError) as got:
        sb.call("code.source", path="src/store/records.py", start="top",
                end="bottom")
    said = str(got.value)
    assert "start='top' is a word" in said and "end='bottom' is a word" in said
    (offer,) = sb.ctx.offers
    assert offer.args["start"] == 1 and offer.args["end"] == 1
