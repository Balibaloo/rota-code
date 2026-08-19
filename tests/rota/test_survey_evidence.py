"""
Constraint zero shrinks only by evidence — which was prose, not a gate.

`REGISTER.md` calls constraint zero the best-designed thing in the repository
and names property 3: it shrinks only by evidence, a survey record whose
citations are validated against the code index. `surveys.attest`'s own docstring
repeats it: *"a lazy surveyor cannot starve constraint zero by asserting it
everywhere."*

It was not true of the running system. `attest(outcome="none_found")` with zero
citations raised nothing, wrote the record, and `refresh_constraint_zero` took
k0 from 7 to 6 — an area marked examined on no evidence at all. Measured, not
argued: that is exactly what it did.

`validators.check_survey_citations` is correct and flags this case precisely. It
had no caller outside the test suite: an assertion over synthetic rows, not a
gate on the running system.

**The asymmetry was inverted against the actual pressure.** `found` is gated
hard and well — you must have written your own role's artefact, and it must have
a body — and that gate was earned from the icalendar run. `none_found` was free,
and every survey brief pushes it: *"the commonest right one here"*, *"if your
budget is running short, attest with what you have."* The cheap path was the
ungated one.

The fix keeps the asymmetry that was earned and closes the hole. What the
icalendar lesson removed was the cost of *having to produce a finding*; those
two outcomes should not cost the same. What it never meant to remove is the cost
of *showing what you read*, which is the same for both and is what makes either
one evidence. Citing is nearly free for a session that looked — `code.survey`
has just handed it the list — and impossible to fake for one that did not,
because the grains are checked against the index and against the area.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.onboarding.boot import refresh_constraint_zero
from rota.roles import validators
from rota.roles.api import surveys_attest


class Ctx:
    """The slice of a session context `attest` actually reads."""

    def __init__(self, conn, role="architect", area="src/auth"):
        self.conn, self.role, self.area = conn, role, area
        self.writes: list = []


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "s.db")
    for area in ("src/auth", "src/api", "docs"):
        for name in ("one.py", "two.py"):
            conn.execute(
                "INSERT INTO code_index (grain, grain_kind, area) "
                "VALUES (?,'path',?)", (f"{area}/{name}", area))
    return conn


def test_none_found_without_citations_is_refused(db):
    """
    The hole, stated as the thing it let through: an area marked examined by a
    session that showed nothing it had read.
    """
    with pytest.raises(ValueError) as exc:
        surveys_attest(Ctx(db), outcome="none_found")

    assert "citations" in str(exc.value).lower()


def test_found_without_citations_is_refused_too(db):
    """
    Both outcomes close the area, so both shrink k0, so both need the evidence.
    Gating only one is how the hole opened in the first place — the ungated path
    became the cheap one, and the brief recommends it.
    """
    ctx = Ctx(db)
    ctx.writes.append(("constraints", "c1", {"headline": "x", "text": "a body"}))

    with pytest.raises(ValueError) as exc:
        surveys_attest(ctx, outcome="found")

    assert "citations" in str(exc.value).lower()


def test_a_citation_must_be_in_the_area_it_closes(db):
    """
    Reading `docs/one.py` is not evidence about `src/auth`. The area is a path
    prefix, so this is checkable rather than a matter of trust.
    """
    with pytest.raises(ValueError) as exc:
        surveys_attest(Ctx(db), outcome="none_found",
                       citations=["docs/one.py"])

    assert "src/auth" in str(exc.value)


def test_a_citation_that_is_not_in_the_index_does_not_count(db):
    """
    A grain nobody indexed is a grain nobody read. Invented paths were the
    failure mode `resolves` was added to record, and recording it was as far as
    it went.
    """
    with pytest.raises(ValueError) as exc:
        surveys_attest(Ctx(db), outcome="none_found",
                       citations=["src/auth/imaginary.py"])

    assert "citations" in str(exc.value).lower()


def test_one_real_citation_is_enough_and_typos_do_not_kill_the_session(db):
    """
    The bar is *showing what you read*, not spelling every path correctly. One
    resolving grain inside the area closes it; the rest are still reported, the
    way they always were, so a session can see what it got wrong.
    """
    ctx = Ctx(db)
    got = surveys_attest(ctx, outcome="none_found",
                         citations=["src/auth/one.py", "src/auth/typo.py"])

    assert got["unresolved_citations"] == ["src/auth/typo.py"]
    assert ("survey_records", "architect:src/auth",
            {"area": "src/auth", "outcome": "none_found"}) in ctx.writes


def test_the_validator_that_was_never_a_gate_now_agrees_with_the_gate(db):
    """
    `check_survey_citations` was correct and uncalled — a test-suite assertion
    over synthetic rows while the running system let the same thing through.
    What it flags and what `attest` refuses are now the same condition, which is
    the only way they cannot drift.
    """
    ctx = Ctx(db)
    surveys_attest(ctx, outcome="none_found", citations=["src/auth/one.py"])
    # `survey_citations` is keyed on (survey_id, grain) and has no `id`, so the
    # writes are applied the way the committer applies them rather than by a
    # generic insert that assumes every table looks the same.
    for table, row_id, values in ctx.writes:
        if table == "survey_records":
            db.execute("INSERT INTO survey_records (id, area, outcome) "
                       "VALUES (?,?,?)",
                       (row_id, values["area"], values["outcome"]))
        else:
            db.execute("INSERT INTO survey_citations (survey_id, grain, resolves) "
                       "VALUES (?,?,?)",
                       (values["survey_id"], values["grain"], values["resolves"]))

    assert validators.check_survey_citations(db) == []


def test_constraint_zero_no_longer_shrinks_on_nothing(db):
    """
    The measurement that opened this, run again. It went 7 to 6 on a bare
    `none_found`; the area may only leave the list now if something was read.
    """
    before = refresh_constraint_zero(db)

    with pytest.raises(ValueError):
        surveys_attest(Ctx(db), outcome="none_found")

    assert refresh_constraint_zero(db) == before, "k0 shrank on no evidence"
