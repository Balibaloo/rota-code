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
from rota.testkit.fixtures import seed_provenance


@pytest.fixture
def project(tmp_path):
    repo = gitfixture.make(tmp_path)
    db = init_db(tmp_path / "rota.db")
    # These tests are about the per-area pass. Onboarding now opens with the
    # orientation and the define phase (`test_onboarding_phases.py`), and the
    # survey pass waits for both; running the survey phase alone is a setting,
    # kept for exactly this -- measuring or testing one phase on its own.
    from rota.core import config
    config.set(db, "onboarding_phases", "survey")
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

    assert {"python", "javascript"} <= set(report.languages)
    assert report.files > 20 and report.symbols > 30

    paths = {r["grain"] for r in db.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path'")}
    assert "src/billing/charges.py" in paths
    assert "web/invoices.js" in paths


def test_a_file_with_no_parser_is_still_in_the_index(project):
    """
    The index answers "what is in this project", and it was answering "what can
    tree-sitter parse".

    On the first Obsidian plugin those differed by the four files that carried
    the domain: a YAML schema defining every key the product reads *and imported
    by the parser that reads them*, the README, and the two manifests holding the
    commitments to the plugin registry. None reached the index, so none reached a
    brief, and the Architect woken for the top level saw a build script and a
    version bumper and wrote a constraint about the build script.

    A file with no parser has no symbols and no imports. It still has a path, and
    `code.source` opens it either way.
    """
    db, repo = project
    report = indexer.build(db, repo.root)

    paths = {r["grain"] for r in db.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path'")}
    assert "README.md" in paths, "the file that says what the project is"
    assert "pyproject.toml" in paths
    assert "src/store/schema.sql" in paths, "not a parsed language, and the schema"

    symbols = {r["grain"] for r in db.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'symbol'")}
    assert not any(g.startswith(("README.md::", "pyproject.toml::"))
                   for g in symbols), "an unparsed file contributes no symbols"
    assert "text" in report.languages


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


def test_a_facade_directory_is_reported_as_leaky(tmp_path):
    """
    A package root that re-exports its submodules imports three areas and is
    imported by none. That is a true and useful thing to notice before pinning:
    it is a directory, not a domain.

    Reported rather than repaired. An area coupled harder to its neighbour than
    to itself is the shape of two directories that are one thing wearing two
    names, and which of those it is, is not the partitioner's call.

    Built from a synthetic index rather than the sample repo. This used to assert
    on `tests/`, which was the only leaky thing in the fixture -- and tests are
    no longer areas at all, so the mechanism lost its only case. The shape here
    is the one actually observed on oauthlib: `.` with four crossing edges into
    `oauth2/rfc6749` and zero internal.
    """
    db = init_db(tmp_path / "rota.db")
    for grain in ("__init__.py", "api.py",
                  "core/engine.py", "core/rules.py", "core/types.py"):
        db.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, 'path')",
                   (grain,))
    for src, dst in (("__init__.py", "core/engine.py"),
                     ("__init__.py", "core/rules.py"),
                     ("api.py", "core/engine.py"),
                     ("core/engine.py", "core/rules.py"),
                     ("core/rules.py", "core/types.py")):
        db.execute("INSERT INTO code_edges (src, dst) VALUES (?, ?)", (src, dst))

    leaky = areas.propose(db).leaky()

    assert leaky, "a root that only points outward should be reported"
    src, dst, crossing, internal = leaky[0]
    assert (src, dst) == (".", "core")
    assert crossing == 3 and internal == 0


# ---------------------------------------------------------------------------
# Tests are evidence, not a subsystem
# ---------------------------------------------------------------------------

def test_a_test_directory_never_becomes_an_area(project):
    """
    Measured on icalendar before this existed: six of fourteen proposed areas
    were `tests/*`, and `tests` alone was the largest area in the repository.
    Three roles would have surveyed the suite as though it were a subsystem.

    The sample repo only ever escaped by luck -- its `tests/` is small enough to
    look unremarkable -- and oauthlib escaped by putting its suite outside the
    package. Neither is a rule.
    """
    db, repo = project
    indexer.build(db, repo.root)

    proposal = areas.propose(db)

    assert not [a for a in proposal.sizes if areas.is_test(a + "/x.py")], \
        f"a test directory became an area: {sorted(proposal.sizes)}"


def test_a_test_is_still_indexed_and_still_reachable(project):
    """
    Excluded from the *partition*, not from the index. A role asked to say what
    the code does should not be blind to the suite that pins it -- and for a
    repository whose spec conformance lives in its tests, that is most of the
    evidence there is.
    """
    db, repo = project
    indexer.build(db, repo.root)
    areas.pin(db, areas.propose(db))

    tests = [r["grain"] for r in db.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path'")
        if areas.is_test(r["grain"])]
    assert tests, "the sample repo has tests; they should be indexed"

    assert not db.execute(
        "SELECT 1 FROM code_index WHERE area IS NULL").fetchone(), \
        "an unattached test is a test no area-scoped read can reach"


def test_a_test_attaches_to_the_area_it_exercises():
    """
    `tests/prop/test_recur.py` belongs with `prop`. Measured on icalendar: 22
    tests under `tests/prop` land on `prop`, and the 149 with no matching source
    directory fall back to the root rather than inventing areas for themselves.
    """
    assert areas._untest("tests/prop") == "prop"
    assert areas._untest("src/tests/prop/dt") == "src/prop/dt"
    assert areas._untest("tests") == ""

    # Not `"test" in path`: that catches source files and hides them from the
    # partition that decides what gets surveyed at all.
    assert not areas.is_test("src/latest.py")
    assert not areas.is_test("contest/manifest.go")
    assert areas.is_test("tests/prop/test_recur.py")
    assert areas.is_test("src/billing/charges_test.go")
    assert areas.is_test("web/app.spec.ts")
    assert areas.is_test("conftest.py")


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

    zero = db.execute("SELECT provenance FROM constraint_provenance WHERE id = ?",
                      (boot.ZERO,)).fetchone()
    assert zero["provenance"] == "observed", "nobody decided this; it is the " \
        "absence of information, not a ruling"


def test_empty_project_does_not_seed_constraint_zero(tmp_path):
    db = init_db(tmp_path / "rota.db")

    report = boot.onboard(db, tmp_path)

    assert report.areas == 0
    assert report.unsurveyed == 0
    assert db.execute(
        "SELECT 1 FROM constraints WHERE id = ?",
        (boot.ZERO,)).fetchone() is None
    assert db.execute(
        "SELECT 1 FROM constraint_bindings WHERE constraint_id = ?",
        (boot.ZERO,)).fetchone() is None


def test_a_survey_shrinks_it_by_exactly_one_area(project):
    db, repo = project
    boot.onboard(db, repo.root)
    before = db.execute(
        "SELECT COUNT(*) n FROM constraint_bindings WHERE constraint_id = ?",
        (boot.ZERO,)).fetchone()["n"]

    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
               "('terminologist:s1', 'src/store', 'found')")
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
               "('terminologist:s1', 'src/store', 'found')")

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


def test_a_survey_closes_the_area_it_was_woken_for(project):
    """
    Not the one it names. On the first foreign repository a Terminologist woken
    for area `.` attested `area='common.py'` — a file inside it. The record filed
    against an area that does not exist, `tick_survey` never saw its area close,
    and the same wake was produced until the attempt bound withdrew it. Twelve
    areas, one survey record, and the system reported itself quiescent.

    The scheduler runs one area at a time in role order and the wake says which.
    A role that named its own would be deciding what it had been asked to do.
    """
    from rota.core import sandbox as sandbox_mod

    db, repo = project
    indexer.build(db, repo.root)
    areas.pin(db, areas.propose(db))
    # `code.source` reads from the project root, and this test builds the index
    # directly rather than through `boot.onboard`, which is what records it.
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
               "('project_root', ?)", (str(repo.root),))

    sb = sandbox_mod.build("terminologist", db, session_id="s1", area="src/billing")
    # Citing is required now — closing an area means showing what you read in
    # it. This test is about *which* area the record lands against, so it cites
    # a real grain and carries on being about that.
    grain = db.execute(
        "SELECT grain FROM code_index WHERE area = 'src/billing' "
        "AND grain_kind = 'path' LIMIT 1").fetchone()["grain"]
    sb.call("code.source", path=grain)      # citing is not reading; see below
    sb.call("surveys.attest", outcome="none_found", citations=[grain])

    row = db.execute("SELECT id, area FROM survey_records").fetchone() or {}
    staged = [w for w in sb.ctx.writes if w[0] == "survey_records"]
    assert staged, "attesting should stage a survey record"
    assert staged[0][2]["area"] == "src/billing"
    assert staged[0][1] == "terminologist:src/billing"


def test_attesting_outside_a_survey_is_refused(project):
    """A session with no area was not woken to close one, and a record filed
    against nothing is worse than no record: it looks like evidence."""
    import pytest

    from rota.core import sandbox as sandbox_mod

    db, repo = project
    sb = sandbox_mod.build("terminologist", db, session_id="s1")
    with pytest.raises(ValueError, match="no area"):
        sb.call("surveys.attest", outcome="none_found")


def test_the_scheduler_action_is_reached_by_the_loop_not_just_callable(project):
    """
    The action had a test and the routing to it did not, because the test called
    `_perform` directly. A real onboarding produced a wake addressed to `-` that
    fell through to dispatch and died on `'-' is not a role in the graph`.

    Three ways to say "not a role" existed — `""`, `SCHEDULER`, and a `do:`
    prefix on the kind — and `step` checked only the prefix. `constraint_zero`
    uses the other two.
    """
    from rota.core.loop import step

    db, repo = project
    boot.onboard(db, repo.root)
    area = db.execute(
        "SELECT area FROM code_index WHERE area IS NOT NULL LIMIT 1").fetchone()["area"]
    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
               "(?, ?, 'none_found')", (f"terminologist:{area}", area))

    result = step(db, principal_present=False)

    assert result.wake is not None and result.wake.role in ("", "-"), \
        f"expected a scheduler action, got {result.wake}"
    assert result.productive
    assert not db.execute(
        "SELECT 1 FROM constraint_bindings WHERE constraint_id = ? AND grain = ?",
        (boot.ZERO, area)).fetchone(), "the surveyed area should have been released"


def test_one_stuck_area_does_not_block_the_rest(project):
    """
    `tick_survey` used to return exactly one wake and `break`, which enforced
    sequencing by leaving nothing else to pick — and meant an area that could not
    close stopped onboarding entirely. On oauthlib, `oauth2/rfc6749/endpoints`
    failed to attest three times, was quarantined by the attempt bound, and took
    the seven areas behind it with it: five of twelve surveyed, frontier empty,
    system reporting itself quiescent.

    A bound that withdraws one wake and thereby withdraws six others is not a
    bound, it is a stall with a counter on it.
    """
    from rota.core.scheduler import frontier, note_dispatch, tick_survey

    db, repo = project
    boot.onboard(db, repo.root)

    offered = tick_survey(db)
    assert len(offered) > 1, "every outstanding area should be offered, in order"
    # Alphabetical among the real areas, and `.` last. It sorts first, so the
    # first glossary session on any repository used to meet the fold-up bucket
    # — whatever belonged nowhere else — before a single domain module, and
    # every later session sees those terms. A stable order still matters, and
    # this is the order.
    names = [w.refs[0] for w in offered]
    assert names == sorted(names, key=lambda a: (a == ".", a)), names

    stuck = offered[0]
    for _ in range(9):
        note_dispatch(db, stuck)

    live = [w for w in frontier(db) if w.kind == "tick:survey"]
    assert live, "the areas behind a quarantined one must still be reachable"
    assert stuck.refs[0] not in {w.refs[0] for w in live}


def test_one_role_finishes_every_area_before_the_next_begins(project):
    """Terms first: constraints are written in glossary terms, and a baseline
    describes behaviour in those terms. Skipping a stuck area must not skip a
    stuck *role*."""
    from rota.core.scheduler import SURVEY_ORDER, tick_survey

    db, repo = project
    boot.onboard(db, repo.root)

    assert {w.role for w in tick_survey(db)} == {SURVEY_ORDER[0]}


def test_the_same_constraint_written_twice_is_one_gate(project):
    """
    24 constraints, 6 distinct headlines. "Retention period for client tokens"
    eight times, each from a different area's session, each a separate row.

    A duplicated glossary entry is clutter. A duplicated constraint is a
    duplicated *gate*: every one of them enters range at review, every one has to
    be satisfied or argued with, and satisfying the first does nothing for the
    other seven. This is the same fault as the glossary's and it lands somewhere
    that costs more.

    The id was the role's to invent, so twelve sessions invented one apiece.
    """
    from rota.core import sandbox as sandbox_mod
    from rota.core.db import _apply_write
    from rota.core.runner import _as_write

    db, repo = project
    boot.onboard(db, repo.root)

    headline = "Tokens expire after the issued lifetime"
    for i, area in enumerate(("src/billing", "src/api")):
        sb = sandbox_mod.build("architect", db, session_id=f"s{i}", area=area)
        sb.call("model.amend", headline=headline, text=f"seen from {area}")
        for staged in sb.ctx.writes:
            _apply_write(db, _as_write(staged))

    rows = db.execute("SELECT id, text FROM constraints WHERE headline=?",
                      (headline,)).fetchall()
    assert len(rows) == 1, f"one commitment, {len(rows)} gates: {[r['id'] for r in rows]}"
    assert rows[0]["text"] == "seen from src/api", "the second session did not amend"


def test_a_constraint_cannot_bind_a_file_the_session_never_opened(project):
    """
    The fabrication check that does not depend on a prompt asking nicely.

    oauthlib produced "Retention period for access tokens is 30 days" five
    times, against a repository containing no retention policy and no thirty.
    The sessions had called `code.survey` — which returns the *index*, the grain
    names and fan-in counts — and that index is exactly the material a
    fabricated constraint is made from. The brief said to open the files. The
    harness was cutting the result to a docstring, so opening them achieved
    nothing, and nothing checked either way.

    The truncation is fixed and the brief is rewritten, and both of those are
    prose that a future edit can undo. This is the part that stays: you cannot
    say a commitment lives in a file you did not read.
    """
    import pytest

    from rota.core import sandbox as sandbox_mod

    db, repo = project
    boot.onboard(db, repo.root)
    sb = sandbox_mod.build("architect", db, session_id="s1", area="src/billing")

    with pytest.raises(ValueError, match="not read"):
        sb.call("model.amend", headline="Charges are idempotent per request id",
                text="A commitment something outside this repository depends on, stated so it can be checked.", bindings=["src/billing/charges.py"])

    sb.call("code.source", path="src/billing/charges.py")
    sb.call("model.amend", headline="Charges are idempotent per request id",
            text="A commitment something outside this repository depends on, stated so it can be checked.", bindings=["src/billing/charges.py"])
    assert any(t == "constraints" for t, _, _ in sb.ctx.writes), \
        "reading the file did not make the constraint writable"


def test_reading_a_file_covers_the_symbols_inside_it(project):
    """A grain is `file.py` or `file.py::symbol`, and whoever read the file read
    the symbol. Otherwise the check would push roles into binding whole files
    when they mean one function."""
    from rota.core import sandbox as sandbox_mod

    db, repo = project
    boot.onboard(db, repo.root)
    sb = sandbox_mod.build("architect", db, session_id="s1", area="src/billing")

    sb.call("code.source", path="src/billing/charges.py")
    sb.call("model.amend", headline="The refund path is ordered",
            text="A commitment something outside this repository depends on, stated so it can be checked.", bindings=["src/billing/charges.py::refund"])
    assert any(t == "constraint_bindings" for t, _, _ in sb.ctx.writes)


def test_sourcing_an_area_names_its_files_instead_of_dead_ending(project):
    """
    A survey session is woken *for an area*, and the area is a directory. So the
    one path it holds without reading anything is the one path `code.source`
    could not read.

    On the second foreign repository this closed a loop that ran thirteen
    sessions. `read_text` on a directory raises `PermissionError`, and the
    directory passes the `exists()` guard ahead of it, so the model got back an
    errno and an absolute host path. `ctx.opened` stayed empty, `model.amend`
    refused the binding as unread and told it to `code.source` the file first,
    and the model did exactly that -- with the only path it had. Every attest
    then refused because nothing had been written. Forty rejected calls in one
    session, and each of the three refusals was individually correct.

    The dead end is the point: the instruction was followable and following it
    changed nothing. So a directory read answers the question the session is
    actually asking -- *what is in here* -- and hands back the names that make
    the next call possible.
    """
    from rota.core import sandbox as sandbox_mod

    db, repo = project
    boot.onboard(db, repo.root)
    sb = sandbox_mod.build("architect", db, session_id="s1", area="src/billing")

    result = sb.call("code.source", path="src/billing")

    assert "charges.py" in str(result), \
        "sourcing an area must name the files in it, or the session has no " \
        "way to reach a readable path from the one path it was given"

    blob = str(result)
    assert "Errno" not in blob and str(repo.root) not in blob, \
        "a directory read leaked an errno and the absolute host root instead " \
        "of answering"

    # Reading the directory is still not reading the file: the binding check
    # holds. What has changed is that the refusal is now escapable.
    import pytest

    with pytest.raises(ValueError, match="not read"):
        sb.call("model.amend", headline="Charges are idempotent per request id",
                text="A commitment something outside this repository depends on, stated so it can be checked.", bindings=["src/billing/charges.py"])

    sb.call("code.source", path="src/billing/charges.py")
    sb.call("model.amend", headline="Charges are idempotent per request id",
            text="A commitment something outside this repository depends on, stated so it can be checked.", bindings=["src/billing/charges.py"])
    assert any(t == "constraints" for t, _, _ in sb.ctx.writes)


def test_constraint_zero_is_unreachable_not_merely_refused(project):
    """
    Constraint zero's bindings are derived — exactly the areas nobody has
    surveyed — and the scheduler recomputes them whenever a survey lands, so the
    binding cannot drift from the evidence.

    Ignoring a role's write here produced a livelock nothing could see from
    inside a session: an Architect survey bound a grain onto constraint zero,
    `tick_constraint_zero` recomputed it away, the next Architect session bound
    it again, and the two alternated sixty times. Both committed. Both were
    productive. Nothing progressed.

    That was guarded by checking an id the model supplied. With the id derived
    there is no argument left to check, and the guard gets stronger for it:
    reaching `k0` would take a headline that slugs to it, and the seeded headline
    is refused by name. A check you cannot reach beats a check that says no.
    """
    import pytest

    from rota.core import sandbox as sandbox_mod

    db, repo = project
    boot.onboard(db, repo.root)
    sb = sandbox_mod.build("architect", db, session_id="s1", area="src/billing")

    advertised = next(s for s in sb.signatures() if s.startswith("model.amend("))
    assert "id" not in advertised, \
        f"the id is the model's again, which is how twelve sessions invented twelve: {advertised}"

    with pytest.raises(ValueError, match="derived"):
        sb.call("model.amend", headline=boot.ZERO_HEADLINE, bindings=["src/billing"])


def test_a_scheduler_action_is_bounded_like_any_other(project):
    """Returning early from the dispatch loop exempted scheduler actions from the
    attempt bound, and one of them promptly needed it."""
    from rota.core.loop import step
    from rota.core.scheduler import tick_key

    db, repo = project
    boot.onboard(db, repo.root)
    area = db.execute(
        "SELECT area FROM code_index WHERE area IS NOT NULL LIMIT 1").fetchone()["area"]
    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
               "(?, ?, 'none_found')", (f"terminologist:{area}", area))

    result = step(db, principal_present=False)

    assert result.wake.kind == "tick:constraint_zero"
    assert db.execute(
        "SELECT attempts FROM tick_attempts WHERE tick_key = ?",
        (tick_key(result.wake),)).fetchone()["attempts"] == 1


# ---------------------------------------------------------------------------
# One meaning per word — enforced, not requested
# ---------------------------------------------------------------------------

def test_the_same_word_twice_amends_rather_than_duplicates(project):
    """
    Twelve survey sessions on a real repository recorded `endpoint` five times,
    `client` three and `token` three — every one the same meaning written down
    again, by a session that had the whole glossary in front of it.

    The id was the role's to invent, so each session invented one. It derives
    from the term now: accidental duplication is impossible.
    """
    from rota.core import sandbox as sandbox_mod

    db, repo = project
    boot.onboard(db, repo.root)
    for area in ("src/billing", "src/auth"):
        sb = sandbox_mod.build("terminologist", db, session_id=f"s-{area}", area=area)
        sb.call("code.source", path=f"{area}/accounts.py")
        # `account` rather than `endpoint`: the sample repo plants this word as
        # its collision and says it nowhere else. The old spelling came from the
        # oauthlib story and appears in no file here, so the read gate refused
        # it -- correctly, and the test was the thing that was wrong.
        # The same meaning, twice, from two places -- which is the case this
        # test is about. Two *different* meanings from two areas are the
        # collision the area rule keeps as two rows, and that is the next test.
        sb.call("glossary.amend", term="account",
                sense_body="the account rows the module works with",
                sense_short="an account as the module means it")
        for w in sb.ctx.writes:
            # As `session_commit` would: the area travels with the row. A
            # fixture that dropped it was hiding the area rule from the test.
            db.execute("INSERT OR REPLACE INTO glossary_terms "
                       "(id, term, sense_short, area) "
                       "VALUES (?, ?, ?, ?)",
                       (w[1], w[2]["term"], w[2]["sense_short"], w[2]["area"]))
            seed_provenance(db, "glossary_terms", w[1], "observed")

    rows = db.execute("SELECT id FROM glossary_terms WHERE term = 'account'").fetchall()
    assert len(rows) == 1, f"one word, one row unless a sense is named: {[r[0] for r in rows]}"


def test_a_genuine_collision_is_still_two_rows(project):
    """`nonce` is a replay guard in one module and a session binding in another.
    That is two rows, and it takes a deliberate act to make them."""
    from rota.core import sandbox as sandbox_mod

    db, repo = project
    boot.onboard(db, repo.root)
    sb = sandbox_mod.build("terminologist", db, session_id="s1", area="src/auth")
    # The word this fixture actually plants a collision on, and the one its
    # files say. `nonce` was borrowed from the oauthlib story and appears in no
    # file here, so the read gate refused it and was right to.
    sb.call("code.source", path="src/auth/accounts.py")
    a = sb.call("glossary.amend", term="account",
                sense_body="one person, one email, one password",
                sense_short="the login identity", sense="login")
    b = sb.call("glossary.amend", term="account",
                sense_body="what an invoice is addressed to; may cover several logins",
                sense_short="the billing entity", sense="billing")

    assert a["id"] != b["id"], "two named senses are two rows"
    assert a["id"].startswith("account") and b["id"].startswith("account")


def test_the_survey_ledger_is_one_row_per_area(project):
    """Three roles survey every area, so this returned 3N rows — 3,900 characters
    of "role X did area Y" in every survey prompt on oauthlib, crowding out the
    material the session was woken to read."""
    from rota.core import sandbox as sandbox_mod

    db, repo = project
    for role in ("terminologist", "architect", "vision_keeper"):
        db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
                   "(?, 'src/billing', 'none_found')", (f"{role}:src/billing",))

    sb = sandbox_mod.build("terminologist", db, session_id="s1", area="src/auth")
    rows = sb.call("surveys.consult")

    assert len(rows) == 1, "one row per area, not per record"
    assert sorted(rows[0]["surveyed_by"]) == ["architect", "terminologist", "vision_keeper"]


def _stamped(db, sid, area, outcome="none_found"):
    """Seed a record the way attest writes one: carrying the area's view.

    A record with no `area_hash` in a hash-bearing index is the
    refresh-after-old-survey shape and re-fires the area -- correctly, and
    not what a fixture that says "this area is closed" means to say.
    """
    from rota.roles.api import area_content_hash

    db.execute("INSERT INTO survey_records (id, area, outcome, area_hash) "
               "VALUES (?,?,?,?)", (sid, area, outcome,
                                    area_content_hash(db, area)))


def test_abandoning_an_area_does_not_end_onboarding_in_the_same_breath(project):
    """
    Quiescence that meant abandonment, which is the one failure this design is
    arranged against.

    Quarantining is a write, and the wake list is computed before it. On the pass
    where an area is abandoned, `all_wakes` still holds its wake — `tick_survey`
    could not know it was about to be quarantined — and `quarantine_stalled`
    then removes it and returns empty. Empty is exactly what quiescence looks
    like, so the run stopped: eleven of twelve areas surveyed by Architect, one
    abandoned, and Vision Keeper's entire pass of twelve never offered. The system
    reported itself finished having done two thirds of the work.

    Calling `frontier` a second time returned thirteen wakes, which is both how
    it was found and what the fix does.
    """
    from rota.core import config
    from rota.core.scheduler import (SURVEY_ORDER, frontier, note_dispatch,
                                     tick_key)

    db, repo = project
    boot.onboard(db, repo.root)

    first, second = SURVEY_ORDER[0], SURVEY_ORDER[1]
    areas = [r["area"] for r in db.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL ORDER BY area")]
    assert len(areas) >= 2, "needs two areas to show one starving the next"

    # Close every area for the first role but one, then stall that one past the
    # bound so it is quarantined on the very next frontier call.
    for area in areas[1:]:
        _stamped(db, f"{first}:{area}", area)
    stuck = next(w for w in frontier(db) if w.kind == "tick:survey")
    assert stuck.role == first
    for _ in range(config.get(db, "tick_attempt_cap")):
        note_dispatch(db, stuck)

    ready = frontier(db)
    assert ready, "the frontier reported quiescence with a whole role's work undone"
    assert any(w.role == second for w in ready), \
        f"the next role was never offered its areas: {sorted({w.role for w in ready})}"


def test_quarantine_does_not_erase_its_own_evidence(project):
    """
    Three rules, each correct alone, forming a cycle that reset the counter to 1
    forever.

    Quarantining stops `tick_survey` producing the wake — it reads the table and
    skips what it finds there. `quarantine_stalled` then forgets counts for keys
    that are no longer in the ready list. And forgetting the count is what
    un-quarantines the wake, so the next call produces it again at one.

    icalendar spent 131 sessions in that cycle and stopped at the session limit
    rather than at quiescence. Its `tick_attempts` held a single row reading
    `attempts = 1` after roughly a hundred and twenty dispatches of that exact
    key: the counter was not stuck, it was being deleted and recreated. The
    bound built to stop this loop was the thing feeding it.

    The distinction the delete could not make: "no longer produced" and "no
    longer *allowed* to be produced" look identical from the ready list, and
    only the first is a reason to drop the debt.

    Asking once cannot see this, which is why the two tests above it did not.
    """
    from rota.core import config
    from rota.core.scheduler import (SURVEY_ORDER, frontier, note_dispatch,
                                     tick_key)

    db, repo = project
    boot.onboard(db, repo.root)

    first = SURVEY_ORDER[0]
    areas = [r["area"] for r in db.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL ORDER BY area")]
    for area in areas[1:]:
        _stamped(db, f"{first}:{area}", area)

    stuck = next(w for w in frontier(db) if w.kind == "tick:survey")
    for _ in range(config.get(db, "tick_attempt_cap")):
        note_dispatch(db, stuck)

    for _ in range(4):
        frontier(db)

    row = db.execute(
        "SELECT attempts, quarantined FROM tick_attempts WHERE tick_key = ?",
        (tick_key(stuck),)).fetchone()
    assert row, \
        "the debt was deleted, so the next frontier call re-offers the same " \
        "wake at attempts=1 and the bound can never be reached"
    assert row["quarantined"] == 1, "abandonment has to survive being looked at"

    assert not any(w == stuck for w in frontier(db)), \
        "an abandoned survey came back"


def test_a_genuinely_finished_onboarding_is_still_quiescent(project):
    """The recompute must not invent work. Two empty passes mean empty."""
    from rota.core.scheduler import SURVEY_ORDER, frontier

    db, repo = project
    boot.onboard(db, repo.root)
    areas = [r["area"] for r in db.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL")]
    for role in SURVEY_ORDER:
        for area in areas:
            _stamped(db, f"{role}:{area}", area)

    assert [w for w in frontier(db) if w.kind == "tick:survey"] == []


def test_the_outcome_names_what_this_role_was_looking_for(project):
    """
    `constraints_found` was the only way to say "found something", and two of the
    three surveying roles do not write constraints. Terminologist writes terms,
    Architect writes constraints, Vision Keeper writes items — so the evidence check
    had to accept any of the three, and accepting any of the three is what let a
    Terminologist attest `constraints_found` eleven times having written none.

    icalendar showed the cost once the fabrication cleared: eight of eleven areas
    came back `constraints_found` against a repository where the run wrote *zero*
    constraints. The word was not a lie the model told, it was the only word we
    gave it.

    So the outcome says `found`, which is true for whoever is speaking, and the
    evidence must be the artefact this role's mode exists to write. A
    Terminologist's terms cannot stand in for an Architect's constraints.
    """
    import pytest

    from rota.core import sandbox as sandbox_mod

    db, repo = project
    boot.onboard(db, repo.root)

    read = ["src/billing/charges.py"]        # citing is required; see below
    te = sandbox_mod.build("terminologist", db, session_id="s1", area="src/billing")
    te.call("code.source", path=read[0])
    te.call("glossary.amend", term="charge",
            sense_body="a captured authorisation; the gateway has taken the money",
            sense_short="an authorisation the gateway has already accepted")
    te.call("surveys.attest", outcome="found", citations=read)
    assert any(t == "survey_records" for t, _, _ in te.ctx.writes), \
        "a Terminologist that defined a term has found something, and used to " \
        "have to call it a constraint to say so"

    # The graph already stops an Architect writing a glossary term, so the leak
    # only ran one way: any of the three tables satisfied the claim, and a
    # Terminologist's terms were accepted as constraints found. The record now
    # follows what was written -- an Architect that wrote no constraints found
    # none, whatever it claimed -- and the correction names the artefact this
    # role owes, not merely that something is missing.
    ar = sandbox_mod.build("architect", db, session_id="s2", area="src/billing")
    ar.call("code.source", path=read[0])
    # Once, the claim is refused with the shape of the owed call; the turn
    # after, the record follows what was written.
    with pytest.raises(ValueError, match="model.amend.*then attest again"):
        ar.call("surveys.attest", outcome="found", citations=read)
    ar.ctx.refusals.append(("surveys.attest", "... then attest again ..."))
    got = ar.call("surveys.attest", outcome="found", citations=read)
    assert got["outcome"] == "none_found" and "constraints" in got["note"]


def test_finding_something_costs_more_than_finding_nothing(project):
    """
    The two outcomes used to cost exactly the same, and one of them looks more
    like work.

    Architect returned `constraints_found` for ten of eleven areas of a
    repository holding three or four real external commitments, and eight of
    those eleven constraints were a headline with no body. Not dishonesty: being
    woken *for an area* is a demand, the brief's "most code is not a constraint"
    is prose, and prose loses to structure every time.

    So the asymmetry becomes real. Claiming a finding means having written one,
    with a body on it. `none_found` stays free *of that*, because the honest
    answer is the one that has to be cheap.

    Free of producing a finding, not free of evidence — a distinction that went
    missing and let an area be closed on nothing. Both outcomes must cite what
    was read, because both close the area and both shrink constraint zero, and
    the cost of showing what you read is the same either way. See
    `test_survey_evidence.py`.
    """
    import pytest

    from rota.core import sandbox as sandbox_mod

    db, repo = project
    boot.onboard(db, repo.root)
    sb = sandbox_mod.build("architect", db, session_id="s1", area="src/billing")

    read = ["src/billing/charges.py"]
    sb.call("code.source", path=read[0])
    # Claimed `found`, wrote nothing, was not refused trying: that is a session
    # that read and found nothing, and the record says so for it. The claim
    # cost twelve-turn loops when it was refused instead -- the model re-sent
    # the same `found` over the same refusal -- and a refusal only stays where
    # a write of the owed artefact was itself refused this session.
    # -- once the claim has been refused with the shape of the call it owes.
    with pytest.raises(ValueError, match="then attest again"):
        sb.call("surveys.attest", outcome="found", citations=read)
    sb.ctx.refusals.append(("surveys.attest", "... then attest again ..."))
    got = sb.call("surveys.attest", outcome="found", citations=read)
    assert got["outcome"] == "none_found"
    assert any(t == "survey_records" for t, _, _ in sb.ctx.writes), \
        "finding nothing must still close the area"


def test_a_constraint_with_no_body_cannot_be_attested_as_a_finding(project):
    """A title is not a finding. Eight of eleven were titles."""
    import pytest

    from rota.core import sandbox as sandbox_mod

    db, repo = project
    boot.onboard(db, repo.root)
    sb = sandbox_mod.build("architect", db, session_id="s1", area="src/billing")
    sb.call("code.source", path="src/billing/charges.py")

    # The refusal moved earlier: a title cannot be *written*, not merely cannot
    # be attested. `attest` only checked on `outcome="found"`, so a session that
    # wrote two headlines and attested `none_found` walked past it — measured on
    # `cnt_j`, which recorded `intent_schema_validation` and
    # `intent_schema_validation_binds_to_the_intent_type`, both empty, and then
    # attested `architect:src none_found`. Same words, one step upstream, and
    # now a bodyless constraint does not reach the table at all.
    with pytest.raises(ValueError, match="nothing under it"):
        sb.call("model.amend", headline="Billing Commitment",
                bindings=["src/billing/charges.py"])

    sb.call("model.amend", headline="Billing Commitment",
            text="Charges are idempotent per request id; a payment processor "
                 "retrying a timeout must not be charged twice.",
            bindings=["src/billing/charges.py"])
    sb.call("surveys.attest", outcome="found",
            citations=["src/billing/charges.py"])


def test_a_surveyor_is_not_shown_what_its_peers_concluded(project):
    """
    By area nine a session was looking at eight siblings that all said
    `constraints_found`. That is not context, it is a norm, and the artefact
    built to let sessions compound was teaching each one the answer.

    What compounds legitimately is what was *found* — the constraints through
    `model.consult`, the terms through `glossary.consult`. "Nine other people
    concluded something" is not a finding.
    """
    from rota.core import sandbox as sandbox_mod

    db, repo = project
    boot.onboard(db, repo.root)
    for i, area in enumerate(("src/auth", "src/catalog")):
        db.execute("INSERT INTO survey_records (id, area, outcome) VALUES (?,?,?)",
                   (f"architect:{area}", area, "found"))

    sb = sandbox_mod.build("architect", db, session_id="s1", area="src/billing")
    rows = sb.call("surveys.consult")
    assert rows, "the surveyor should still see which areas are done"
    assert all("outcome" not in r for r in rows), \
        f"peer verdicts are still being shown: {rows[0]}"


# ---------------------------------------------------------------------------
# Two whole-database invariants that had no home
#
# `check_bindings_resolve` and `check_survey_citations` live in
# `rota/roles/validators.py` and were asserted nowhere. The arc test says why it
# declined them: it produces no constraint bindings and no survey records, so
# asserting them there would be two green checks over empty tables, which reads
# as covered and is worse than nothing. This is the database that has the rows.
#
# Homing the first one immediately found it was wrong -- see its docstring.
# ---------------------------------------------------------------------------

def test_every_binding_onboarding_creates_resolves(project):
    """
    Constraint zero is the only constraint the system writes for itself, and it
    binds every area in the repository. So the cheapest possible test of "a
    binding names something real" is to onboard and ask.

    That is exactly what had never been done. The validator looked for grains
    only, and constraint zero binds areas -- `.`, `src/auth`, `src/billing` --
    so all seven of its bindings failed a check whose docstring claims every
    binding passes it.
    """
    from rota.roles import validators

    db, repo = project
    boot.onboard(db, repo.root)

    assert db.execute(
        "SELECT COUNT(*) n FROM constraint_bindings WHERE resolves = 1"
    ).fetchone()["n"] > 0, "no bindings to check; this test has gone vacuous"
    assert validators.check_bindings_resolve(db) == []


def test_a_survey_that_cites_nothing_is_not_evidence(project):
    """
    "Surveyed, none found" shrinks constraint zero, which makes it a claim with
    consequences: the area stops being marked as unexamined. What stops that
    from being free is the citations -- a surveyor that never read the area
    cannot produce grains that exist in it.

    Both directions are asserted, because a validator that only ever sees
    passing data is not being tested either.
    """
    from rota.roles import validators

    db, repo = project
    boot.onboard(db, repo.root)
    grain = db.execute(
        "SELECT grain FROM code_index WHERE area = 'src/auth' LIMIT 1").fetchone()

    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
               "('architect:s1', 'src/auth', 'none_found')")
    assert validators.check_survey_citations(db), \
        "a survey citing nothing was accepted as evidence"

    db.execute("INSERT INTO survey_citations (survey_id, grain, resolves) "
               "VALUES ('architect:s1', ?, 1)", (grain["grain"],))
    assert validators.check_survey_citations(db) == []

    db.execute("INSERT INTO survey_citations (survey_id, grain, resolves) "
               "VALUES ('architect:s1', 'src/auth/nothing_here.py', 0)")
    assert validators.check_survey_citations(db), \
        "a citation that does not resolve was accepted"


def test_onboarding_records_the_commit_whoever_calls_it(tmp_path):
    """
    Which tree a run is about belongs to onboarding, not to one of its callers.

    It was written in `cli.onboard`, so `rota onboard` and the new-run form
    recorded it and the seat's own onboard key did not — `tui._do_onboard`,
    `fixtures` and `onboard_run` all call `onboarding.boot.onboard` directly.
    Two runs made different ways were differently identifiable, which is worse
    than neither recording it: the header of a comparison would be right
    sometimes.

    A fact about the operation belongs in the operation.
    """
    from rota.core.db import init_db
    from rota.testkit import gitfixture

    repo = gitfixture.make(tmp_path)
    conn = init_db(tmp_path / "direct.db")
    boot.onboard(conn, repo.root)

    got = {r["key"]: r["value"] for r in conn.execute(
        "SELECT key, value FROM config WHERE key LIKE 'project_%'")}
    assert got.get("project_commit"), "no commit recorded by boot.onboard"
    assert got.get("project_branch")
    assert got["project_root"] == str(repo.root)


def test_onboarding_a_tree_that_is_not_a_checkout_still_works(tmp_path):
    """
    A directory can be onboarded without being a repository — the run then
    honestly describes a tree rather than a commit, and says so by leaving the
    fields empty rather than by failing.
    """
    from rota.core.db import init_db

    root = tmp_path / "plain"
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "a.py").write_text("x = 1\n")
    conn = init_db(tmp_path / "plain.db")
    boot.onboard(conn, root)

    got = {r["key"]: r["value"] for r in conn.execute(
        "SELECT key, value FROM config WHERE key LIKE 'project_%'")}
    assert got.get("project_commit", "") == ""
    assert got["project_root"] == str(root)


def test_a_mistyped_path_is_resolved_against_the_index(project):
    """
    A path copied by hand out of a listing, copied wrong, was terminal.

    On the Obsidian plugin a session read `.github/ISSUE_TEMPLATE/bug_report.md`
    from `code.survey` and asked for `/github/ISSUE_TEMPLATE/bug_report.md` --
    the leading dot became a slash. `_within` refused it as escaping the
    worktree, which is right, and the refusal ended the area: the file could not
    be opened, so it could not be cited, so `surveys.attest` refused too. Eleven
    of that run's 88 turns died there, and `.github` sorts first.

    Nothing about it was specific to that directory. Any path transcribed wrong
    is unopenable, and "escapes the worktree" is not something a session can act
    on.
    """
    from rota.core import sandbox as sandbox_mod

    db, repo = project
    boot.onboard(db, repo.root)
    sb = sandbox_mod.build("terminologist", db, session_id="s1", area="src/auth")

    out = sb.call("code.source", path="/billing/charges.py")

    assert out["path"] == "src/billing/charges.py", "the grain it was reaching for"
    assert "Charge" in out["text"]
    assert "note" in out, "say which spelling was read, or the citation will not match"
    assert "src/billing/charges.py" in out["note"]

    # And `opened` carries the corrected spelling, or the citation check refuses
    # a file the session demonstrably read.
    assert "src/billing/charges.py" in sb.ctx.opened


def test_an_ambiguous_guess_is_still_refused(project):
    """
    One candidate or none. `indexer.resolve` applies the same rule to a bare
    package name, for the same reason: an ambiguous guess is a misread, and a
    misread is worse than an error -- it hands back a file nobody asked for and
    says nothing.
    """
    from rota.core import sandbox as sandbox_mod

    db, repo = project
    boot.onboard(db, repo.root)
    sb = sandbox_mod.build("terminologist", db, session_id="s1", area="src/auth")

    # `accounts.py` exists under both `src/auth` and `src/billing`.
    out = sb.call("code.source", path="accounts.py")
    assert "error" in out
    assert not sb.ctx.opened, "nothing was read, so nothing may be cited"

    out = sb.call("code.source", path="nowhere/at/all.py")
    assert "error" in out
    assert "code.survey" in out["error"], "name the call that lists real paths"


def test_the_index_keeps_each_symbols_kind(project):
    """The tree-sitter node type says what a symbol is; the index keeps it,
    so no consumer has to re-derive kinds by regex at push time."""
    db, repo = project
    repo.edit(repo.root, "src/billing/shapes.py",
              "class Charge:\n    pass\n\n\ndef total(charges):\n    return sum(charges)\n")
    repo.commit_in(repo.root, "a class and a function")
    boot.onboard(db, repo.root)
    kinds = {r["grain"].split("::")[-1]: r["sym_kind"] for r in db.execute(
        "SELECT grain, sym_kind FROM code_index WHERE grain LIKE 'src/billing/shapes.py::%'")}
    assert kinds == {"Charge": "class", "total": "function"}, kinds


def test_without_an_index_a_binding_is_a_file_the_session_read(tmp_path):
    """Delivery engagements never onboard; `model.amend` there binds what the
    session opened, and refuses a symbol by name instead of refusing
    everything."""
    import pytest

    from rota.core.db import init_db
    from rota.roles.api import Ctx, model_amend

    db = init_db(tmp_path / "delivery.db")
    ctx = Ctx(conn=db, role="architect")
    ctx.opened.add("src/billing/invoices.py")
    with pytest.raises(ValueError, match="INVOICE_FIELDS.*src/billing/invoices.py"):
        model_amend(ctx, headline="CSV column order",
                    text="Spreadsheets built by finance parse the export by position; "
                         "reordering INVOICE_FIELDS breaks them silently.",
                    bindings=["INVOICE_FIELDS"])
    got = model_amend(ctx, headline="CSV column order",
                      text="Spreadsheets built by finance parse the export by position; "
                           "reordering the columns breaks them silently.",
                      bindings=["src/billing/invoices.py"])
    assert got["id"]


def test_a_changed_file_reopens_exactly_its_area(project):
    """
    Loop "stay true", first breath. The DECISIONS entry said it for months:
    "`tick_survey` fires on areas with no record. Nothing fires on an area
    whose code changed since its record. Over a project's lifetime this is
    what decides whether the model of the codebase stays true."

    Every record here is stamped with the area's aggregate content as the
    index described it; a file changes; the index is rebuilt; and the survey
    machinery re-offers exactly the area whose view is gone -- through the
    same predicate, briefs and bounds as the first read, because staleness is
    expressed as the one thing that machinery already understands.
    """
    from rota.core import config
    from rota.core.scheduler import SURVEY_ORDER, tick_survey

    db, repo = project
    boot.onboard(db, repo.root)
    config.set(db, "onboarding_phases", "survey")

    areas = [r["area"] for r in db.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL "
        "ORDER BY area")]
    assert len(areas) >= 2
    for role in SURVEY_ORDER:
        for area in areas:
            _stamped(db, f"{role}:{area}", area)
    db.commit()
    assert tick_survey(db) == [], "every view is current; nothing re-fires"

    # A commit lands in one area.
    victim = db.execute(
        "SELECT grain, area FROM code_index WHERE grain_kind='path' "
        "AND area IS NOT NULL ORDER BY grain").fetchone()
    target = repo.root / victim["grain"]
    target.write_text(target.read_text(encoding="utf-8") +
                      "\n# a change the survey has not seen\n",
                      encoding="utf-8")
    # The refresh pair: a new tree's index, then the partition and
    # constraint zero re-derived over it. `rota refresh` is this.
    indexer.build(db, repo.root)
    boot.repin(db, repo.root)
    db.commit()

    reopened = {(w.role, w.refs[0]) for w in tick_survey(db)}
    assert reopened, "the changed area must come back"
    assert {a for _, a in reopened} == {victim["area"]}, \
        "and only the changed area"


def test_a_refresh_under_a_running_batch_disturbs_nothing_it_should_not(tmp_path):
    """Loop 5's second half. The tree moves while a batch is mid-flight and
    the operator refreshes. Four invariants, each a different way extended
    use could rot: the running batch survives untouched (its worktree is a
    different checkout and its head_commit is pinned history); freshness
    reopens exactly the changed area; a binding to a surviving grain still
    resolves; and a reference to a grain the rebuild dropped is *reported*,
    never silently disarmed -- the constraint tripwire and the batch's touch
    prediction are worthless precisely when nobody knows they are gone."""
    from rota.core.db import init_db
    from rota.core.scheduler import tick_survey
    from rota.onboarding import boot, indexer
    from rota.testkit import gitfixture
    from rota.tools.audit import orphaned_grain_refs

    db = init_db(tmp_path / "rota.db")
    from rota.core import config as config_mod
    config_mod.set(db, "onboarding_phases", "survey")
    repo = gitfixture.make(tmp_path, name="refresh_under_batch")
    boot.onboard(db, repo.root)

    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) VALUES ('i1','ship','in_scope',"
               "'approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('t1','i1','do it')")
    tree = repo.worktree("b1")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit, "
               "worktree) VALUES ('b1','i1','running','abc123',?)",
               (str(tree),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('b1','t1')")
    # A binding that survives, a binding that will not, and a touch that
    # will not: the file behind the second two is about to vanish upstream.
    db.execute("INSERT INTO constraints (id, headline) VALUES "
               "('cn1','auth stays reachable')")
    db.execute("INSERT INTO constraint_bindings (constraint_id, grain, "
               "grain_kind) VALUES ('cn1','src/auth/login.py','path')")
    db.execute("INSERT INTO constraint_bindings (constraint_id, grain, "
               "grain_kind) VALUES ('cn1','src/billing/charges.py','path')")
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
               "VALUES ('b1','src/billing/charges.py','path')")
    # Every area gets a current-hash survey record so only the *edited* area
    # reopens -- the same `_stamped` contract the freshness tests use.
    areas = [r["area"] for r in db.execute(
        "SELECT DISTINCT area FROM code_index WHERE area != ''")]
    for a in areas:
        _stamped(db, f"terminologist:{a}", a)
        _stamped(db, f"architect:{a}", a)
        _stamped(db, f"vision_keeper:{a}", a)
    db.commit()
    assert not [w for w in tick_survey(db)], "the world starts closed"

    # The tree moves: one file edited, one deleted.
    repo.edit(repo.root, "src/auth/login.py",
              "def login(u, p):\n    return check(u, p) and audit(u)\n")
    (repo.root / "src/billing/charges.py").unlink()
    repo.commit_in(repo.root, "upstream moved")

    indexer.build(db, repo.root)
    boot.repin(db, repo.root)
    db.commit()

    row = db.execute("SELECT status, head_commit, worktree FROM batches "
                     "WHERE id='b1'").fetchone()
    assert (row["status"], row["head_commit"]) == ("running", "abc123"),         "the running batch is not the refresh's business"
    assert row["worktree"] == str(tree)

    reopened = {w.refs[0] for w in tick_survey(db)}
    assert "src/auth" in reopened, "the edited area reopens"
    assert "src/catalog" not in reopened, "an untouched area stays closed"

    grains = {r["grain"] for r in db.execute("SELECT grain FROM code_index")}
    assert "src/auth/login.py" in grains, "the surviving binding resolves"

    orphans = orphaned_grain_refs(db)
    assert any("cn1" in o and "charges.py" in o for o in orphans),         "the disarmed tripwire is reported"
    assert any("b1" in o and "charges.py" in o for o in orphans),         "the stale touch prediction is reported"
