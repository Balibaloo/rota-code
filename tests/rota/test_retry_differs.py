"""Frame 58: a retried tick says which attempt it is.

Night 88 (2026-09-23): four tick wakes ran three times each, and every
turn of each triple was identical. A retry at temperature zero repeats
the first session, because the prompt never says the attempt. The
dispatcher now marks the wake, and the prompt says the number.
"""
from dataclasses import replace

import pytest

from rota.core import loop
from rota.core.db import init_db
from rota.core.runner import build_prompt
from rota.core.sandbox import build
from rota.core.scheduler import CLAIM_PREFIX, SURFACE_PREFIX, Wake
from rota.llm.llm import Pins, ScriptedBackend
from rota.roles import prompts

from tests.rota.test_night46_context import db  # noqa: F401

# One wake per kind the frame names. The refs carry the shape each
# predicate builds: a batch id, a surfaced file, a claim subject.
KINDS = [
    ("developer", "batch_start",
     Wake("developer", "tick:batch_start", refs=("b1",))),
    ("tester", "tests_missing",
     Wake("tester", "tick:tests_missing", refs=("b1",),
          detail="without a test: c2")),
    ("architect", "boundary",
     Wake("architect", "tick:boundary", refs=(SURFACE_PREFIX + "setup.py",))),
    ("critic", "challenge",
     Wake("critic", "tick:challenge", refs=(CLAIM_PREFIX + "model_areas:a1",))),
]


@pytest.mark.parametrize("role,mode,wake", KINDS,
                         ids=[k[2].kind for k in KINDS])
def test_a_retried_tick_prompt_differs_from_the_first_attempt(db, role, mode, wake):  # noqa: F811
    """The second attempt of a tick reads differently from the first.

    The sentence sits outside `DETAIL_SHOWN`, so it reaches every tick
    kind. A first attempt keeps the prompt it has today, so no cassette
    key moves.
    """
    sb = build(role, db, batch_id="b1" if role in ("developer", "tester") else None,
               mode=mode, allow=prompts.mode_tools(role, mode))
    _system, first = build_prompt(role, sb, wake, {}, f"MODE: {mode}")
    _system, second = build_prompt(role, sb, replace(wake, attempt=2), {},
                                   f"MODE: {mode}")

    assert first != second, "the retry reproduces the first session"
    assert "This is attempt 2 of 3 on this wake." in second
    assert "attempt" not in first, first


def _delivery_db(conn):
    """Seed one batch whose only test fails at the head commit.

    The Developer's `tests_failing` wake is then undrained, because a
    session that writes nothing leaves the test red.
    """
    conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
                 "result, output, attempt) VALUES "
                 "('r1','b1','tst1','abc123','fail','AssertionError',1)")
    conn.commit()
    return conn


def test_the_dispatcher_marks_the_second_dispatch_of_one_wake(db):  # noqa: F811
    """Two steps of the loop on one undrained wake, and the second says so.

    The door is in `loop.step`, at the count that feeds the quarantine.
    The number the role reads is the number the quarantine counts.
    """
    conn = _delivery_db(db)
    backend = ScriptedBackend([])

    first = loop.step(conn, backend=backend, pins=Pins(model="scripted"))
    second = loop.step(conn, backend=backend, pins=Pins(model="scripted"))

    assert first.wake.kind == "tick:tests_failing"
    assert second.wake.kind == "tick:tests_failing"
    assert first.wake.attempt == 1
    assert second.wake.attempt == 2

    opening = [r["user"] for r in conn.execute(
        "SELECT t.user AS user FROM turns t JOIN sessions s ON s.id = t.session_id "
        "WHERE t.seq = 1 ORDER BY s.seq")]
    assert len(opening) == 2, opening
    assert "attempt" not in opening[0], opening[0]
    assert "This is attempt 2 of 3 on this wake." in opening[1], opening[1]
