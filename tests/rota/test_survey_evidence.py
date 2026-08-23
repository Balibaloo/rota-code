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
    """The slice of a session context `attest` actually reads.

    `read=` seeds `opened` the way `code.source` would, so a test about the
    *citation* rules does not have to stage a file read to get to them.
    """

    def __init__(self, conn, role="architect", area="src/auth", read=()):
        self.conn, self.role, self.area = conn, role, area
        self.writes: list = []
        # What `code.source` has opened this session. The real `Ctx` has
        # carried this since Law 12; the stub has to as well or it is a
        # different object with the same name.
        self.opened: set = set(read)
        self.read_words: set = set()
        self.batch_id = None
        self.provenance = "observed"


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
        surveys_attest(Ctx(db, read=["docs/one.py"]), outcome="none_found",
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
    ctx = Ctx(db, read=["src/auth/one.py"])
    got = surveys_attest(ctx, outcome="none_found",
                         citations=["src/auth/one.py", "src/auth/typo.py"])

    assert got["unresolved_citations"] == ["src/auth/typo.py"]
    staged = [(t, i, v) for t, i, v in ctx.writes if t == "survey_records"]
    assert [(i, v["area"], v["outcome"]) for _, i, v in staged] == [
        ("architect:src/auth", "src/auth", "none_found")]


def test_the_validator_that_was_never_a_gate_now_agrees_with_the_gate(db):
    """
    `check_survey_citations` was correct and uncalled — a test-suite assertion
    over synthetic rows while the running system let the same thing through.
    What it flags and what `attest` refuses are now the same condition, which is
    the only way they cannot drift.
    """
    ctx = Ctx(db, read=["src/auth/one.py"])
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


def test_a_survey_of_an_area_that_no_longer_exists_is_flagged(db):
    """
    Re-indexing strands survey records and nothing noticed.

    `check_bindings_resolve` checks bindings and `check_survey_citations`
    checks citations; a record whose *area* has ceased to exist passes both.
    Shrink a directory below the fold floor, re-index, and the partition no
    longer has it — while the record still says that area was surveyed.

    Constraint zero rebinds correctly regardless, because it is derived from
    what is unsurveyed rather than accumulated. That is the design working. The
    record counting as a survey of something absent is the part that was
    invisible.
    """
    surveys_attest(Ctx(db, read=["src/auth/one.py"]), outcome="none_found",
                   citations=["src/auth/one.py"])
    db.execute("INSERT INTO survey_records (id, area, outcome) "
               "VALUES ('architect:src/auth','src/auth','none_found')")
    assert validators.check_survey_areas(db) == []

    db.execute("DELETE FROM code_index WHERE area = 'src/auth'")

    problems = validators.check_survey_areas(db)
    assert len(problems) == 1
    assert "src/auth" in problems[0]


# ---------------------------------------------------------------------------
# What a survey was a survey *of*
# ---------------------------------------------------------------------------

def test_a_survey_records_the_commit_it_surveyed(db):
    """
    `DECISIONS.md` names this as the one blocker on re-surveying, verbatim:
    *"a survey recording the commit it surveyed — settled above, not yet built.
    The predicate cannot be written before the column exists."*

    `tick_survey` fires on areas with no record. Nothing fires on an area whose
    code changed since its record, and over a project's lifetime that is what
    decides whether the model of the codebase stays true. The predicate is not
    written here — the column it needs is.

    The commit is read from `config`, not from git, and that is the correct
    semantics rather than the cheap one: a survey reads grains from
    `code_index`, and `code_index` was built at `project_commit`. Asking git
    now would record where the tree happens to be, which is not what was
    surveyed.
    """
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
               "('project_commit', '9961924abc')")

    ctx = Ctx(db, read=["src/auth/one.py"])
    surveys_attest(ctx, outcome="none_found", citations=["src/auth/one.py"])

    record = [v for t, _, v in ctx.writes if t == "survey_records"][0]
    assert record["commit_sha"] == "9961924abc"


def test_a_survey_of_an_unversioned_tree_records_no_commit(db):
    """
    A tree can be onboarded without being a repository. The record then says so
    by being empty rather than by carrying something invented — and a
    re-survey predicate reading it can tell "surveyed at an unknown commit"
    from "surveyed at this one".
    """
    ctx = Ctx(db, read=["src/auth/one.py"])
    surveys_attest(ctx, outcome="none_found", citations=["src/auth/one.py"])

    record = [v for t, _, v in ctx.writes if t == "survey_records"][0]
    assert record["commit_sha"] == ""


# ---------------------------------------------------------------------------
# Citing what you read, rather than what you were listed
# ---------------------------------------------------------------------------

def test_a_survey_must_have_opened_one_of_the_files_it_cites(db):
    """
    Measured, not argued. The survey prompt hands a Terminologist
    `[code.survey]` — a file list with fan-in counts — and, across 6,315
    characters, not one `def`, `class`, `import` or `return`. Then one survey
    session in three wrote **six glossary terms having called `code.source`
    zero times**: the vocabulary of an area, decided from paths.

    That is where `Alarm: an event that triggers an action` comes from, and
    `folder: directory in file system` before it. Both are readings of a *name*.

    Citing was already required, and citing is not reading — the list of grains
    is in the prompt, so naming one costs nothing. The bar is the same as
    everywhere else here: the cheap answer must show what it looked at.
    """
    ctx = Ctx(db)
    with pytest.raises(ValueError) as exc:
        surveys_attest(ctx, outcome="none_found", citations=["src/auth/one.py"])

    assert "read" in str(exc.value).lower()


def test_having_read_one_of_them_is_enough(db):
    """
    One file, not all of them. A survey that opened something and formed a view
    is the behaviour wanted; requiring every citation to be read would make
    citing widely *cost* more than citing narrowly, which is backwards.
    """
    ctx = Ctx(db, read=["src/auth/one.py"])

    got = surveys_attest(ctx, outcome="none_found",
                         citations=["src/auth/one.py", "src/auth/two.py"])

    assert got["id"] == "architect:src/auth"


def test_a_symbol_counts_as_having_read_its_file(db):
    """
    `code_index` holds files *and* symbols — `a.py` and `a.py::run` are both
    grains — so a session that read `a.py` and cited the symbol in it has read
    what it cited. Matching them as different strings would refuse the most
    precise citation available.
    """
    db.execute("INSERT INTO code_index (grain, grain_kind, area) "
               "VALUES ('src/auth/one.py::login','symbol','src/auth')")
    ctx = Ctx(db, read=["src/auth/one.py"])

    got = surveys_attest(ctx, outcome="none_found",
                         citations=["src/auth/one.py::login"])

    assert got["id"] == "architect:src/auth"


def test_reading_a_file_records_it_on_the_session(db, tmp_path):
    """
    `ctx.opened` already exists and `code.source` already fills it — the field
    carries its own reasoning: "a constraint is a commitment to something
    outside the codebase; you cannot have found one in a file you did not read,
    and the first foreign repo produced twenty-four constraints from sessions
    that had opened almost nothing."

    The rule was written, implemented, and applied to constraint *bindings*
    only. A survey citation is the same claim about the same act.
    """
    from rota.roles.api import code_source

    root = tmp_path / "proj"
    (root / "src" / "auth").mkdir(parents=True)
    (root / "src" / "auth" / "one.py").write_text("def login():\n    pass\n")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
               "('project_root', ?)", (str(root),))

    ctx = Ctx(db)
    code_source(ctx, path="src/auth/one.py")

    assert "src/auth/one.py" in ctx.opened


def test_a_bare_symbol_resolves_to_its_grain(db):
    """
    The gate's precondition, stated in its own comment, is that `code.survey`
    has just handed the session the grain list. A design that hands over the
    *source* instead has no such list, and the session cites what source shows
    it: declarations.

    Measured on `cnt_d`, whose terminologist working set is `code.area` and
    `code.source` with no `code.survey` at all. Three sessions cited
    `["TemplateVariableType", "TemplateVariableVariables"]`, were refused three
    times, hit the attempt bound, and `src/variables` and
    `src/variables/providers` were both quarantined — the two richest areas in
    the repository, and the only ones holding `variable_type`, `provider` and
    the five prompt types. Thirty-six turns, and the reading had been done.

    Resolving costs the gate nothing it was built for: a session that did not
    look cannot name `TemplateVariableType`, and the index is still what
    decides.
    """
    db.execute("INSERT INTO code_index (grain, grain_kind, area) "
               "VALUES ('src/auth/one.py::TokenStore','symbol','src/auth')")

    ctx = Ctx(db, read=["src/auth/one.py"])
    surveys_attest(ctx, outcome="none_found", citations=["TokenStore"])

    rec = [v for t, _id, v in ctx.writes if t == "survey_records"]
    assert rec and rec[0]["outcome"] == "none_found", "the area closes"

    cites = {v["grain"]: v["resolves"] for t, _id, v in ctx.writes
             if t == "survey_citations"}
    assert cites == {"src/auth/one.py::TokenStore": 1}, (
        "the citation is recorded as the grain it resolved to, not as the bare "
        "symbol -- the record has to be traceable back to the index")


def test_an_ambiguous_symbol_is_not_guessed_at(db):
    """
    Two grains ending in the same symbol is the index failing to decide, and
    picking one for the session produces a citation nobody can trace back.
    Unresolved is the honest answer; the refusal still names it.
    """
    for f in ("one.py", "two.py"):
        db.execute("INSERT INTO code_index (grain, grain_kind, area) "
                   "VALUES (?,'symbol','src/auth')", (f"src/auth/{f}::Shared",))

    with pytest.raises(ValueError) as exc:
        surveys_attest(Ctx(db, read=["src/auth/one.py"]), outcome="none_found",
                       citations=["Shared"])

    assert "Shared" in str(exc.value)


def test_a_symbol_from_another_area_still_does_not_count(db):
    """Resolution is scoped to the area being closed, not to the whole index."""
    db.execute("INSERT INTO code_index (grain, grain_kind, area) "
               "VALUES ('src/api/one.py::Router','symbol','src/api')")

    with pytest.raises(ValueError) as exc:
        surveys_attest(Ctx(db, read=["src/auth/one.py"]), outcome="none_found",
                       citations=["Router"])

    assert "src/auth" in str(exc.value)


def test_an_import_the_area_was_shown_counts_as_evidence(db):
    """
    `code.area` hands over "the area's own files, and the ones it imports",
    deliberately: *"a file the area imports is part of what the area means,
    wherever it sits."* This gate required every citation to sit under the
    area's path — two tools disagreeing about what belongs to an area, and the
    gate winning.

    Measured on `cnt_i`: the session woken for `src/variables/providers` was
    shown `src/variables/index.ts`, read it, cited it, and was refused twelve
    times across three sessions. The area was quarantined — the one holding
    `variable_type`, `provider` and the five prompt types, lost for the second
    run running and not for the reason the first one lost it.
    """
    db.execute("INSERT INTO code_edges (src, dst) VALUES "
               "('src/auth/one.py','src/api/one.py')")

    ctx = Ctx(db, read=["src/api/one.py"])
    surveys_attest(ctx, outcome="none_found", citations=["src/api/one.py"])

    rec = [v for t, _id, v in ctx.writes if t == "survey_records"]
    assert rec and rec[0]["area"] == "src/auth", (
        "the area closes on a file it imports and the session opened")


def test_an_unrelated_area_is_still_not_evidence(db):
    """
    The edge is what makes an import evidence, and it comes from the index. A
    file in another area that nothing here imports is still somebody else's.
    """
    with pytest.raises(ValueError) as exc:
        surveys_attest(Ctx(db, read=["src/api/two.py"]), outcome="none_found",
                       citations=["src/api/two.py"])

    assert "src/auth" in str(exc.value)


def test_an_item_named_after_a_grain_is_refused(db):
    """
    `items.yaml` in the cnt key states the test: *"it says something about the
    product that a reader could act on, and it would still be true if every
    identifier were renamed"* — and names the failure outright: *"A sentence
    about a function is not an item."* The vision_keeper brief says the same in its
    own words. Prose, and nothing held it.

    Measured on `cnt_i`, the first run in nine to reach the Vision Keeper at all:
    of eight items, `id='src/variables/index.ts'` and `id='getRelativePath'`
    ("Returns the relative path of a given path"). Both are grains. The other
    six — `release_workflow`, `settings_behaviour`, `intent-processing` — are
    not, and all six are about the product.

    Renaming does not catch it: rename `getRelativePath` to anything and
    "returns the relative path" stays true, which is exactly why it says nothing
    about *this* product. Naming the item after the code is the tell.
    """
    from rota.roles.api import problem_assert

    db.execute("INSERT INTO code_index (grain, grain_kind, area) "
               "VALUES ('src/auth/one.py::getRelativePath','symbol','src/auth')")

    ctx = Ctx(db, role="vision_keeper")
    with pytest.raises(ValueError) as exc:
        problem_assert(ctx, id="getRelativePath",
                       text="Returns the relative path of a given path")
    assert "sentence about a file or a function" in str(exc.value)

    with pytest.raises(ValueError):
        problem_assert(ctx, id="src/auth/one.py", text="This file exports things")


def test_an_item_about_the_product_still_lands(db):
    """The six good ones from the same run go through untouched."""
    from rota.roles.api import problem_assert

    ctx = Ctx(db, role="vision_keeper")
    out = problem_assert(
        ctx, id="release_workflow",
        text="The workflow creates a release on GitHub when a tag is pushed.")

    assert out["id"] == "release_workflow"
    assert [v["text"] for t, _id, v in ctx.writes if t == "items"]
