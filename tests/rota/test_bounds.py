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

This does not invent bounds for the rest. Picking numbers nobody has measured is
how a bound goes red for the wrong reason and gets loosened until it means
nothing again -- each of these wants one run and one judgement. What it does is
stop the list growing: a new case cannot add an unbounded write count without
saying so here.
"""
from __future__ import annotations

from rota import paths
from rota.testkit import fixtures


# Known debt, enumerated rather than estimated. A grep said thirty-three; the
# cases say twenty-five, because the grep counted message counts and `any_of`
# alternatives, and messages are bounded elsewhere -- the duplicate guard
# refuses a repeated verb to one recipient, and one question per session bounds
# the spray.
UNBOUNDED: set[tuple[str, str]] = {
    ('L1-AR-annotate-a-batch', 'batch_touch'),
    ('L1-AR-cite-the-clause-into-a-constraint', 'constraints'),
    ('L1-AR-constrain-an-external-commitment', 'constraints'),
    ('L1-AR-find-against-a-constraint', 'findings'),
    ('L1-AR-group-into-batches', 'batches'),
    ('L1-DV-build-a-clear-criterion', 'batches'),
    ('L1-DV-log-the-choice-the-criteria-did-not-make', 'ledger'),
    ('L1-GK-amend-a-contested-item', 'items'),
    ('L1-GK-assert', 'items'),
    ('L1-GK-relay-the-ruling', 'items'),
    ('L1-GK-slice', 'tickets'),
    ('L1-GK-survey-an-area-for-what-it-does', 'items'),
    ('L1-LI-no-report-no-question', 'statements'),
    ('L1-LI-ratify', 'statements'),
    ('L1-RS-answer-from-the-clause-not-from-memory', 'references_'),
    ('L1-TE-a-standard-definition-is-not-automatically-ours', 'glossary_terms'),
    ('L1-TE-amend-glossary', 'glossary_terms'),
    ('L1-TE-specify-criteria', 'criteria'),
    ('L1-TE-survey-an-area-for-its-terms', 'glossary_terms'),
    ('L1-TS-apply-a-term-and-write-the-test', 'tests'),
    ('L1-TS-encode-a-criterion', 'tests'),
    ('L1-TS-fix-a-test-that-asserts-more-than-its-criterion', 'tests'),
    ('L3-ratified-statement-becomes-a-term', 'glossary_terms'),
    ('L3-ratified-statement-becomes-scope', 'items'),
    ('L3-scope-becomes-a-ticket-with-criteria', 'criteria'),
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
