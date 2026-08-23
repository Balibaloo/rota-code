"""
An expectation with no upper bound measures that something happened.

`L1-LI-segment` asserted `statements: {count: ">=1"}` and passed five runs out
of five while Liaison turned one sentence into twenty-four statements -- three
statements issued eight times, one of them fabricated. Every one would have gone
to the principal to ratify and to three roles to work from, and the case
covering that exact behaviour was green throughout.

The bound is not the same fix as the guard. `brief.segment` now refuses a
repeated span and a text that is not in the entry, which makes the defect
impossible; the bound is what made it *visible*. Only segmentation has both.

This does not invent bounds. Picking numbers nobody has measured is how a bound
goes red for the wrong reason and gets loosened until it means nothing again --
so every ceiling here is a number some run actually produced. What this file
does on its own is stop the list growing: a new case cannot add an unbounded
write count without saying so.
"""
from __future__ import annotations

from rota import paths
from rota.testkit import fixtures


# Known debt, enumerated rather than estimated. A grep said thirty-three; the
# cases said twenty-five, because the grep counted message counts and `any_of`
# alternatives, and messages are bounded elsewhere -- the duplicate guard
# refuses a repeated verb to one recipient, and one question per session bounds
# the spray.
#
# Twenty-five became six, in two payments and neither of them a probe.
#
# Three fell out of a guard: `tests.encode` reports and drops a second test for
# a criterion it has already encoded, and those three cases have one criterion
# each, so `1..1` is derived rather than measured.
#
# The other sixteen were already measured and nobody had looked. Each has
# hundreds of runs recorded against the current prompt in `cassettes.db`, and
# every transcript carries the write count it produced. Filtered to the runs
# that *passed* -- a failing run's count is the defect, not the ceiling -- the
# highest is the bound. No probe rows were created, so there are none to purge,
# which is the part of that procedure that has gone wrong before.
#
# Six left, and held back for stated reasons rather than unexamined. Five write
# `items`, and `problem.assert` has just grown a guard against one session
# scoping an item both ways -- their recorded counts describe behaviour that no
# longer exists, so reading them now would bound the wrong thing. The sixth,
# `L1-LI-no-report-no-question`, has no passing run against the current prompt
# to read at all.
UNBOUNDED: set[tuple[str, str]] = {
    ('L1-VK-amend-a-contested-item', 'items'),
    ('L1-VK-assert', 'items'),
    ('L1-VK-relay-the-ruling', 'items'),
    ('L1-VK-survey-an-area-for-what-it-does', 'items'),
    ('L1-LI-no-report-no-question', 'statements'),
    ('L3-ratified-statement-becomes-scope', 'items'),
}


def _unbounded() -> set[tuple[str, str]]:
    found = set()
    for path in sorted(paths.CASES.glob("l*.yaml")):
        for case in fixtures.load_case(path) or []:
            writes = ((case.get("expect") or {}).get("writes")) or {}
            if not isinstance(writes, dict):
                continue
            for table, spec in writes.items():
                if isinstance(spec, dict) and str(spec.get("count", "")).startswith(">="):
                    found.add((case["id"], table))
    return found


def test_no_new_unbounded_write_expectation():
    """A lower bound alone is debt, and debt has to be declared to be paid."""
    new = sorted(_unbounded() - UNBOUNDED)
    assert not new, (
        f"{len(new)} write expectation(s) with no upper bound: {new}. Measure what "
        f"the case actually writes and say so -- `count: \"1..3\"` -- or add it "
        f"to UNBOUNDED with the reason it cannot be bounded yet")


def test_the_debt_shrinks_and_never_silently():
    """
    The other direction. Bounding one and leaving it listed here makes the list
    lie about how much is owed, which is how a debt register stops being read.
    """
    paid = sorted(UNBOUNDED - _unbounded())
    assert not paid, (
        f"bounded now, and still listed as debt: {paid}. Remove from UNBOUNDED")
