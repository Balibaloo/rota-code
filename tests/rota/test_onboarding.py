"""
Onboarding: from a checkout to a schedulable world.

The whole `observed` half of the design was gated on a table nothing filled.
`code_index` had no writer, `code_edges` was referenced by no Python at all,
partitioning had no algorithm, and nothing created constraint zero — while
`tick_survey`, a working predicate, read all of it. A predicate over an empty
world fires zero wakes and looks exactly like a system with no work to do, which
is why no lint caught it: *"does anything produce the input this consumes"* is a
question about a sequence, and every check here is about a thing.

These are the mechanical halves. What a survey session then *makes* of an area is
L1's business, and the planted properties in the sample repo are what those cases
assert against.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.onboarding import areas, boot, indexer
from rota.testkit import gitfixture, samplerepo


@pytest.fixture
def project(tmp_path):
    repo = gitfixture.make(tmp_path)
    db = init_db(tmp_path / "rota.db")
    yield db, repo
    gitfixture.cleanup(repo)


# ---------------------------------------------------------------------------
# The index
# ---------------------------------------------------------------------------

def test_the_index_covers_both_languages(project):
    """Language-agnostic is not an aspiration here: the sample repo is Python
    and JavaScript precisely so a Python-only shortcut fails."""
    db, repo = project
    report = indexer.build(db, repo.root)

    assert set(report.languages) == {"python", "javascript"}
    assert report.files > 20 and report.symbols > 30

    paths = {r["grain"] for r in db.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path'")}
    assert "src/billing/charges.py" in paths
    assert "web/invoices.js" in paths


def test_symbols_are_indexed_under_the_file_that_defines_them(project):
    db, repo = project
    indexer.build(db, repo.root)

    assert db.execute(
        "SELECT 1 FROM code_index WHERE grain = 'src/billing/charges.py::prorate'"
    ).fetchone(), "a top-level function is a grain"


def test_the_planted_fan_in_module_is_the_most_depended_on(project):
    """The sample repo plants one: `src/store`, imported by auth, billing and
    catalog. If the import resolver is wrong, this is what says so."""
    db, repo = project
    indexer.build(db, repo.root)

    top = db.execute(
        "SELECT grain, fan_in FROM code_index WHERE grain_kind = 'path' "
        "ORDER BY fan_in DESC LIMIT 1").fetchone()
    assert top["grain"].startswith(samplerepo.PLANTED["fan_in"]["module"])

    importers = {r["src"].split("/")[1] for r in db.execute(
        "SELECT src FROM code_edges WHERE dst = ?", (top["grain"],))}
    assert {"auth", "billing", "catalog"} <= importers


def test_an_import_that_cannot_be_resolved_is_counted_not_invented(project):
    """
    Standard-library imports do not resolve to anything in the checkout, and
    that is correct. What matters is that they are counted: an index that
    quietly loses a third of its edges partitions the codebase wrongly and gives
    no sign, and the partition is what every later area-scoped decision rests on.
    """
    db, repo = project
    report = indexer.build(db, repo.root)

    assert report.unresolved > 0
    assert report.edges > report.unresolved / 2, (
        "most imports should resolve; a ratio this far off means the extractor "
        "is pulling imported names rather than module paths")

    known = {r["grain"] for r in db.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path'")}
    for row in db.execute("SELECT src, dst FROM code_edges"):
        assert row["src"] in known and row["dst"] in known, "an invented edge"


def test_reindexing_replaces_rather_than_accumulates(project):
    """The index is a function of a commit. A file deleted upstream must leave
    it, or `code.probe` starts returning paths that are not there."""
    db, repo = project
    indexer.build(db, repo.root)
    (repo.root / "src" / "notify" / "delivery.py").unlink()

    indexer.build(db, repo.root)

    assert not db.execute(
        "SELECT 1 FROM code_index WHERE grain = 'src/notify/delivery.py'"
    ).fetchone()


# ---------------------------------------------------------------------------
# Areas
# ---------------------------------------------------------------------------

def test_the_partition_follows_the_modules_somebody_already_chose(project):
    db, repo = project
    indexer.build(db, repo.root)

    proposal = areas.propose(db)

    assert {"src/auth", "src/billing", "src/catalog", "src/notify",
            "src/store"} <= set(proposal.sizes)


def test_a_directory_that_only_points_outward_is_reported_as_leaky(project):
    """
    `tests/` imports three areas and nothing imports it. That is a true and
    useful thing to notice before pinning: it is a directory, not a domain.

    Reported rather than repaired. An area coupled harder to its neighbour than
    to itself is the shape of two directories that are one thing wearing two
    names, and which of those it is, is not the partitioner's call.
    """
    db, repo = project
    indexer.build(db, repo.root)

    leaky = {row[0] for row in areas.propose(db).leaky()}
    assert "tests" in leaky


def test_pinning_gives_every_symbol_its_file_s_area(project):
    db, repo = project
    indexer.build(db, repo.root)
    areas.pin(db, areas.propose(db))

    row = db.execute(
        "SELECT area FROM code_index WHERE grain = "
        "'src/billing/charges.py::prorate'").fetchone()
    assert row["area"] == "src/billing"

    assert not db.execute(
        "SELECT 1 FROM code_index WHERE area IS NULL").fetchone()


# ---------------------------------------------------------------------------
# Constraint zero
# ---------------------------------------------------------------------------

def test_onboarding_puts_every_area_under_constraint_zero(project):
    db, repo = project

    report = boot.onboard(db, repo.root)

    bound = {r["grain"] for r in db.execute(
        "SELECT grain FROM constraint_bindings WHERE constraint_id = ?",
        (boot.ZERO,))}
    all_areas = {r["area"] for r in db.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL")}
    assert bound == all_areas
    assert report.unsurveyed == len(all_areas)

    zero = db.execute("SELECT provenance FROM constraints WHERE id = ?",
                      (boot.ZERO,)).fetchone()
    assert zero["provenance"] == "observed", "nobody decided this; it is the " \
        "absence of information, not a ruling"


def test_a_survey_shrinks_it_by_exactly_one_area(project):
    db, repo = project
    boot.onboard(db, repo.root)
    before = db.execute(
        "SELECT COUNT(*) n FROM constraint_bindings WHERE constraint_id = ?",
        (boot.ZERO,)).fetchone()["n"]

    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
               "('terminologist:s1', 'src/store', 'constraints_found')")
    boot.refresh_constraint_zero(db)

    bound = {r["grain"] for r in db.execute(
        "SELECT grain FROM constraint_bindings WHERE constraint_id = ?",
        (boot.ZERO,))}
    assert len(bound) == before - 1 and "src/store" not in bound


def test_finding_nothing_shrinks_it_too(project):
    """
    "Surveyed, nothing found" is a result. If it did not count, the cheapest way
    to keep an area under constraint zero forever would be to look at it and say
    so — and the surveyor who does the honest thing would be punished for it.
    """
    db, repo = project
    boot.onboard(db, repo.root)

    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
               "('architect:s1', 'src/notify', 'none_found')")
    boot.refresh_constraint_zero(db)

    bound = {r["grain"] for r in db.execute(
        "SELECT grain FROM constraint_bindings WHERE constraint_id = ?",
        (boot.ZERO,))}
    assert "src/notify" not in bound


def test_no_role_can_write_constraint_zero_smaller(project):
    """
    It is never removed by judgement. Architect owns the model and can amend any
    constraint in it, including this one — but the binding is recomputed from
    the survey records, so an amendment that shrank it would be undone by the
    next pass rather than argued with.
    """
    db, repo = project
    boot.onboard(db, repo.root)
    db.execute("DELETE FROM constraint_bindings WHERE constraint_id = ? "
               "AND grain = 'src/auth'", (boot.ZERO,))

    boot.refresh_constraint_zero(db)

    assert db.execute(
        "SELECT 1 FROM constraint_bindings WHERE constraint_id = ? AND "
        "grain = 'src/auth'", (boot.ZERO,)).fetchone()


# ---------------------------------------------------------------------------
# And the scheduler keeps them in step
# ---------------------------------------------------------------------------

def test_a_landed_survey_puts_the_shrink_on_the_frontier(project):
    from rota.core.predicates import constraint_zero

    db, repo = project
    boot.onboard(db, repo.root)
    assert not constraint_zero(db), "nothing surveyed, nothing to reconcile"

    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
               "('terminologist:s1', 'src/store', 'constraints_found')")

    wakes = constraint_zero(db)
    assert wakes and wakes[0].kind == "tick:constraint_zero"
    assert wakes[0].refs == ("src/store",)


def test_the_scheduler_performs_it_without_a_session(project):
    """A survey was read, so the area is no longer unread. There is no version
    of that fact a role could weigh."""
    from rota.core.loop import _perform
    from rota.core.scheduler import Wake

    db, repo = project
    boot.onboard(db, repo.root)
    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
               "('terminologist:s1', 'src/store', 'none_found')")

    note = _perform(db, Wake("-", "tick:constraint_zero", refs=("src/store",)))

    assert "unsurveyed area" in note
    assert not db.execute(
        "SELECT 1 FROM constraint_bindings WHERE constraint_id = ? AND "
        "grain = 'src/store'", (boot.ZERO,)).fetchone()


def test_onboarding_makes_the_survey_predicate_fire(project):
    """
    The sequence question, asserted directly: `tick_survey` reads `code_index`,
    and before onboarding existed it read an empty table and returned nothing —
    which is indistinguishable from a system with no work to do.
    """
    from rota.core.scheduler import tick_survey

    db, repo = project
    assert not tick_survey(db), "nothing indexed, so nothing to survey"

    boot.onboard(db, repo.root)

    wakes = tick_survey(db)
    assert wakes, "an onboarded repository has surveys owing"
    assert wakes[0].role == "terminologist", "terms first: everything the other" \
        " two write is written in them"
