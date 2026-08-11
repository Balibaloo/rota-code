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

    sb = sandbox_mod.build("terminologist", db, session_id="s1", area="src/billing")
    sb.call("surveys.attest", outcome="none_found")

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
    assert [w.refs[0] for w in offered] == sorted(w.refs[0] for w in offered)

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
                bindings=["src/billing/charges.py"])

    sb.call("code.source", path="src/billing/charges.py")
    sb.call("model.amend", headline="Charges are idempotent per request id",
            bindings=["src/billing/charges.py"])
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
            bindings=["src/billing/charges.py::refund"])
    assert any(t == "constraint_bindings" for t, _, _ in sb.ctx.writes)


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
    for area in ("src/billing", "src/auth"):
        sb = sandbox_mod.build("terminologist", db, session_id=f"s-{area}", area=area)
        sb.call("glossary.amend", term="endpoint", sense_short=f"a path in {area}")
        for w in sb.ctx.writes:
            db.execute("INSERT OR REPLACE INTO glossary_terms "
                       "(id, term, sense_short, provenance) VALUES (?, ?, ?, 'observed')",
                       (w[1], w[2]["term"], w[2]["sense_short"]))

    rows = db.execute("SELECT id FROM glossary_terms WHERE term = 'endpoint'").fetchall()
    assert len(rows) == 1, f"one word, one row unless a sense is named: {[r[0] for r in rows]}"


def test_a_genuine_collision_is_still_two_rows(project):
    """`nonce` is a replay guard in one module and a session binding in another.
    That is two rows, and it takes a deliberate act to make them."""
    from rota.core import sandbox as sandbox_mod

    db, repo = project
    sb = sandbox_mod.build("terminologist", db, session_id="s1", area="src/auth")
    a = sb.call("glossary.amend", term="nonce", sense_short="replay guard",
                sense="server")
    b = sb.call("glossary.amend", term="nonce", sense_short="session binding",
                sense="client")

    assert a["id"] != b["id"], "two named senses are two rows"
    assert a["id"].startswith("nonce") and b["id"].startswith("nonce")


def test_the_survey_ledger_is_one_row_per_area(project):
    """Three roles survey every area, so this returned 3N rows — 3,900 characters
    of "role X did area Y" in every survey prompt on oauthlib, crowding out the
    material the session was woken to read."""
    from rota.core import sandbox as sandbox_mod

    db, repo = project
    for role in ("terminologist", "architect", "gatekeeper"):
        db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
                   "(?, 'src/billing', 'none_found')", (f"{role}:src/billing",))

    sb = sandbox_mod.build("terminologist", db, session_id="s1", area="src/auth")
    rows = sb.call("surveys.consult")

    assert len(rows) == 1, "one row per area, not per record"
    assert sorted(rows[0]["surveyed_by"]) == ["architect", "gatekeeper", "terminologist"]


def test_abandoning_an_area_does_not_end_onboarding_in_the_same_breath(project):
    """
    Quiescence that meant abandonment, which is the one failure this design is
    arranged against.

    Quarantining is a write, and the wake list is computed before it. On the pass
    where an area is abandoned, `all_wakes` still holds its wake — `tick_survey`
    could not know it was about to be quarantined — and `quarantine_stalled`
    then removes it and returns empty. Empty is exactly what quiescence looks
    like, so the run stopped: eleven of twelve areas surveyed by Architect, one
    abandoned, and Gatekeeper's entire pass of twelve never offered. The system
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
        db.execute("INSERT INTO survey_records (id, area, outcome) VALUES (?,?,?)",
                   (f"{first}:{area}", area, "none_found"))
    stuck = next(w for w in frontier(db) if w.kind == "tick:survey")
    assert stuck.role == first
    for _ in range(config.get(db, "tick_attempt_cap")):
        note_dispatch(db, stuck)

    ready = frontier(db)
    assert ready, "the frontier reported quiescence with a whole role's work undone"
    assert any(w.role == second for w in ready), \
        f"the next role was never offered its areas: {sorted({w.role for w in ready})}"


def test_a_genuinely_finished_onboarding_is_still_quiescent(project):
    """The recompute must not invent work. Two empty passes mean empty."""
    from rota.core.scheduler import SURVEY_ORDER, frontier

    db, repo = project
    boot.onboard(db, repo.root)
    areas = [r["area"] for r in db.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL")]
    for role in SURVEY_ORDER:
        for area in areas:
            db.execute("INSERT INTO survey_records (id, area, outcome) VALUES (?,?,?)",
                       (f"{role}:{area}", area, "none_found"))

    assert [w for w in frontier(db) if w.kind == "tick:survey"] == []
