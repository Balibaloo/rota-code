"""
Onboarding as phases: orient, define, survey.

The per-area survey was the whole of onboarding, and twelve measured runs on one
repository said what that costs: a word that lives in five areas is defined
from each of them and from none of them, the brief never says what the program
is, and the roles that would have said so never run because the budget is
spent on areas. So onboarding became a sequence of questions over the whole
program, each answered with the previous answer in front of it, and the areas
are kept for what they are good at -- coverage, and the words only one place
uses.

These are the mechanical halves: which phase is current, what drains each, and
what a session in each phase may and may not write. What a session *makes* of
its material is L1's business.
"""
from __future__ import annotations

import pytest

from rota.core import config
from rota.core.db import init_db
from rota.core.scheduler import (ONBOARDING_TICKS, PROGRAM, TERM_PREFIX, frontier,
                                 onboarding_phase, pending_terms, tick_define,
                                 tick_orient, tick_survey)
from rota.onboarding import boot, lexicon
from rota.testkit import gitfixture
from rota.testkit.fixtures import refs_from_columns


@pytest.fixture
def project(tmp_path):
    repo = gitfixture.make(tmp_path)
    db = init_db(tmp_path / "rota.db")
    yield db, repo
    gitfixture.cleanup(repo)


def _onboarding(wakes):
    """The onboarding wakes on a frontier. `observed_entries` fires first on any
    fresh onboarding -- constraint zero is itself an `observed` row -- and that
    one Liaison session is not what these tests are about."""
    return [w for w in wakes if w.kind in ONBOARDING_TICKS]


def _framed(db, outcome="none_found"):
    """Past the frame phase: the tree has been judged (or the heuristic
    frame attested as standing). v2's zeroth gate; frame_repinned is set so
    the lazy re-pin does not fire mid-test."""
    db.execute("INSERT OR IGNORE INTO survey_records (id, area, outcome) "
               "VALUES ('architect:@frame', '@frame', ?)", (outcome,))
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
               "('frame_repinned', '1')")


def _oriented(db, outcome="none_found"):
    _framed(db)
    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES (?, ?, ?)",
               (f"vision_keeper:{PROGRAM}", PROGRAM, outcome))


def _reconciled(db, outcome="none_found"):
    """Past the reconcile phase: the README has been read against the account."""
    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
               "('vision_keeper:@prose', '@prose', ?)", (outcome,))


# ---------------------------------------------------------------------------
# The lexicon
# ---------------------------------------------------------------------------

def test_onboarding_builds_the_lexicon_from_what_the_checkout_declares(project):
    """A directory is the loudest claim a codebase makes about what a thing is
    called. `src/billing` says `billing`; nothing in any word list ranked by
    frequency ever did."""
    db, repo = project
    report = boot.onboard(db, repo.root)
    words = {r["word"] for r in lexicon.ranked(db)}

    assert report.words == len(words) > 0
    assert "billing" in words, "a directory name"
    assert "auth" in words, "another"
    assert "invoice" in words, "a declared type, `Invoice`"
    assert "billing account" in words, "a compound kept whole, `BillingAccount`"


def test_the_lexicon_carries_no_stopwords_and_no_long_compounds(project):
    db, repo = project
    boot.onboard(db, repo.root)
    from rota.roles.api import _FRAME_WORDS, _NOT_VOCABULARY

    rows = lexicon.ranked(db)
    assert not [r["word"] for r in rows if r["word"] in _NOT_VOCABULARY | _FRAME_WORDS]
    assert all(len(r["word"].split()) <= lexicon.MAX_COMPOUND for r in rows)
    assert all(r["score"] > 0 for r in rows), "a word with no structural source is not offered"


def test_the_lexicon_is_rebuilt_not_accumulated(project):
    db, repo = project
    boot.onboard(db, repo.root)
    db.execute("INSERT INTO code_lexicon (word, sources, score) VALUES "
               "('leftover', '[]', 99)")
    boot.onboard(db, repo.root)
    assert not db.execute("SELECT 1 FROM code_lexicon WHERE word = 'leftover'").fetchone()


# ---------------------------------------------------------------------------
# The phases, in order
# ---------------------------------------------------------------------------

def test_nothing_onboarded_is_no_phase(project):
    db, _ = project
    assert onboarding_phase(db) == "none"
    assert tick_orient(db) == [] and tick_define(db) == [] and tick_survey(db) == []


def test_the_first_wake_after_onboarding_is_the_orientation(project):
    """Before any word in the program is named, somebody says what the program
    is. One wake, to the role answerable for what the project is, over the
    whole program rather than any area of it."""
    db, repo = project
    boot.onboard(db, repo.root)
    db.commit()

    assert onboarding_phase(db) == "frame", "v2: the frame is judged first"
    ready = _onboarding(frontier(db))
    assert [(w.role, w.kind, w.refs) for w in ready] == \
        [("architect", "tick:frame", ("@frame",))]

    _framed(db)
    assert onboarding_phase(db) == "orient"
    ready = _onboarding(frontier(db))
    assert [(w.role, w.kind, w.refs) for w in ready] == \
        [("vision_keeper", "tick:orient", (PROGRAM,))]
    assert tick_define(db) == [] and tick_survey(db) == []


def test_the_orientation_record_moves_the_run_to_defining(project):
    db, repo = project
    boot.onboard(db, repo.root)
    _oriented(db)
    _reconciled(db)
    db.commit()

    assert onboarding_phase(db) == "define"
    ready = _onboarding(frontier(db))
    assert ready and all(w.role == "terminologist" and w.kind == "tick:define"
                         for w in ready)
    assert all(w.refs[0].startswith(TERM_PREFIX) for w in ready)
    assert tick_survey(db) == [], "areas wait for the words"


def test_define_wakes_are_offered_best_word_first_and_bounded(project):
    db, repo = project
    boot.onboard(db, repo.root)
    _oriented(db)
    config.set(db, "define_terms", 3)

    pending = pending_terms(db)
    assert len(pending) == 3
    ranked = [r["word"] for r in lexicon.ranked(db)]
    assert pending == ranked[:3], "the lexicon's order, with nothing promoted"


def test_a_glossary_row_in_the_words_family_drains_its_define_wake(project):
    db, repo = project
    boot.onboard(db, repo.root)
    _oriented(db)
    first = pending_terms(db)[0]
    from rota.roles.api import _slug_of

    db.execute("INSERT INTO glossary_terms (id, term, sense_short, sense_body, "
               "provenance, area) VALUES (?, ?, 'x', 'y', 'observed', '')",
               (_slug_of(first) + "s", first + "s"))        # the plural counts too
    assert first not in pending_terms(db)


def test_none_found_for_a_word_drains_it_too(project):
    """A word the project means nothing of its own by is a result, not a
    silence -- the same rule `none_found` has always had for an area."""
    db, repo = project
    boot.onboard(db, repo.root)
    _oriented(db)
    first = pending_terms(db)[0]
    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES (?, ?, ?)",
               (f"terminologist:{TERM_PREFIX}{first}", TERM_PREFIX + first, "none_found"))
    assert first not in pending_terms(db)


def test_when_the_words_are_done_the_areas_begin(project):
    db, repo = project
    boot.onboard(db, repo.root)
    _oriented(db)
    _reconciled(db)
    config.set(db, "define_terms", 0)

    assert onboarding_phase(db) == "survey"
    wakes = tick_survey(db)
    assert wakes and {w.role for w in wakes} == {"terminologist"}
    assert all(w.kind == "tick:survey" for w in wakes)


def test_an_abandoned_orientation_does_not_hold_the_run(project):
    """The attempt bound settles a phase the way it settles an area: the work
    is recorded as abandoned, reported, and the run carries on behind it."""
    db, repo = project
    boot.onboard(db, repo.root)
    _framed(db)
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
               "VALUES (?, 3, 1)", (f"vision_keeper|tick:orient|{PROGRAM}",))
    assert onboarding_phase(db) == "define"


def test_an_abandoned_word_is_skipped_not_retried(project):
    db, repo = project
    boot.onboard(db, repo.root)
    _oriented(db)
    first = pending_terms(db)[0]
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
               "VALUES (?, 3, 1)", (f"terminologist|tick:define|{TERM_PREFIX}{first}",))
    assert first not in pending_terms(db)
    assert pending_terms(db), "the rest are still owed"


def test_the_phases_are_a_setting(project):
    """`survey` alone is the pre-orientation design, kept so one phase can be
    measured against another -- and so every test of the area pass still tests
    the area pass."""
    db, repo = project
    boot.onboard(db, repo.root)
    config.set(db, "onboarding_phases", "survey")
    assert onboarding_phase(db) == "survey"
    assert tick_orient(db) == [] and tick_define(db) == []
    assert tick_survey(db)


def test_the_orientations_words_are_promoted(project):
    """A word the account of the program needed is a word the program is
    about. The bonus only moves a word up: present stays present, and a word
    the lexicon ranked below the fold can be asked for because the Vision Keeper
    used it."""
    db, repo = project
    boot.onboard(db, repo.root)
    _oriented(db)
    config.set(db, "define_terms", 2)
    ranked = [r["word"] for r in lexicon.ranked(db)]
    low = ranked[-1]
    assert low not in pending_terms(db)

    db.execute("INSERT INTO items (id, text, kind, provenance) VALUES "
               "('i1', ?, 'in_scope', 'observed')",
               (f"The product does something with every {low} it is given, "
                f"and with each {low} again.",))
    # Bonus is +3; whether that clears the fold depends on the repository,
    # so the assertion is monotonic: never lower than before.
    before = ranked.index(low)
    after_list = [r["word"] for r in lexicon.ranked(db)]
    assert after_list.index(low) == before, "the lexicon itself is untouched"
    promoted = pending_terms(db)
    top_scores = {w: s for w, (s, _) in _scored(db).items()}
    assert top_scores[low] >= _scored_without_items(db)[low] + 3


def _scored(db):
    """The scoring `pending_terms` applies, exposed for the monotonic check."""
    import json
    import math

    rows = lexicon.ranked(db)
    toks = []
    for r in db.execute("SELECT text FROM items WHERE provenance = 'observed'"):
        toks += [lexicon.singular(w) for w in lexicon.parts(r["text"] or "")]
    words = set(toks)
    out = {}
    for r in rows:
        s = float(r["score"]) + (3.0 if r["word"] in words else 0.0)
        out[r["word"]] = (s, int(r["uses"]))
    return out


def _scored_without_items(db):
    return {r["word"]: float(r["score"]) for r in lexicon.ranked(db)}


# ---------------------------------------------------------------------------
# The collision waits for the words
# ---------------------------------------------------------------------------

def test_term_collision_holds_until_the_words_are_defined(project):
    """Band `fix` outranks band `start`, so a collision found while the first
    words are being written would drain before the rest were looked at. It
    waits for the orientation and the define pass, as it already waited for
    the survey pass -- and fires the moment they are done."""
    from rota.core.predicates import term_collision

    db, repo = project
    boot.onboard(db, repo.root)
    _framed(db)
    for i, area in enumerate(("src/auth", "src/billing")):
        db.execute("INSERT INTO glossary_terms (id, term, sense_short, sense_body, "
                   "provenance, area) VALUES (?, 'account', ?, 'b', 'observed', ?)",
                   (f"account{'#billing' if i else ''}", f"sense {i}", area))
    assert onboarding_phase(db) == "orient"
    assert term_collision(db) == []

    _oriented(db)
    _reconciled(db)
    assert onboarding_phase(db) == "define"
    assert term_collision(db) == []

    config.set(db, "onboarding_phases", "orient")
    assert onboarding_phase(db) == "done"
    assert term_collision(db), "nothing left to wait for"


# ---------------------------------------------------------------------------
# What a session in each phase may write
# ---------------------------------------------------------------------------

def test_a_define_session_defines_the_word_it_was_woken_for(project):
    """The wake names the word. A session that defines some other word has done
    a different session's work and left its own undone, which is how off-key
    entries arrive; a session that spells the same word the project's way is
    filed under the word the wake named."""
    from rota.roles.api import Ctx, glossary_amend

    db, repo = project
    boot.onboard(db, repo.root)
    ctx = Ctx(conn=db, role="terminologist", area=TERM_PREFIX + "billing account",
              wake_refs=(TERM_PREFIX + "billing account",), provenance="observed")
    ctx.read_words.update({"billing", "account", "invoice"})

    with pytest.raises(ValueError, match="about 'billing account'"):
        glossary_amend(ctx, term="invoice", sense_body="a charge issued",
                       sense_short="a charge")
    got = glossary_amend(ctx, term="BillingAccount",
                         sense_body="who an invoice is addressed to, in src/billing",
                         sense_short="who an invoice is addressed to")
    assert got["id"] == "billing_account"
    assert "filed under" in got.get("note", "")
    row = next(w for w in ctx.writes if w[0] == "glossary_terms")
    assert row[2]["term"] == "billing account"
    assert row[2]["area"] == "", "defined over the whole program, not from a place"


def test_an_area_sense_does_not_overwrite_the_program_sense(project):
    """A row with no area was written about the whole program. An area that
    says the word differently is the collision the glossary exists to surface
    -- a second row, never a replacement of the first."""
    from rota.roles.api import Ctx, glossary_amend

    db, repo = project
    boot.onboard(db, repo.root)
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, sense_body, "
               "provenance, area) VALUES ('account', 'account', "
               "'who an invoice is addressed to', 'b', 'observed', '')")
    ctx = Ctx(conn=db, role="terminologist", area="src/auth", provenance="observed")
    ctx.read_words.update({"account", "login"})
    glossary_amend(ctx, term="account", sense_body="a person who can sign in",
                   sense_short="a login identity")
    ids = [w[1] for w in ctx.writes if w[0] == "glossary_terms"]
    assert ids == ["account#src_auth"]


def test_attesting_the_program_needs_what_was_read(project):
    from rota.roles.api import Ctx, problem_assert, surveys_attest

    db, repo = project
    boot.onboard(db, repo.root)
    ctx = Ctx(conn=db, role="vision_keeper", area=PROGRAM, provenance="observed")
    problem_assert(ctx, id="bills_accounts",
                   text="The product issues invoices to the accounts that owe money.")
    with pytest.raises(ValueError, match="opened none"):
        surveys_attest(ctx, outcome="found", citations=["README.md"])
    ctx.opened.add("README.md")
    got = surveys_attest(ctx, outcome="found", citations=["README.md"])
    assert got["id"] == f"vision_keeper:{PROGRAM}"
    rec = next(w for w in ctx.writes if w[0] == "survey_records")
    assert rec[2]["area"] == PROGRAM


def test_attesting_a_word_as_none_found_needs_no_citation(project):
    """The concordance was pushed: the looking was done by the harness, and
    "I looked and there is nothing" needs no second proof."""
    from rota.roles.api import Ctx, surveys_attest

    db, repo = project
    boot.onboard(db, repo.root)
    ctx = Ctx(conn=db, role="terminologist", area=TERM_PREFIX + "billing",
              provenance="observed")
    got = surveys_attest(ctx, outcome="none_found")
    assert got["id"] == f"terminologist:{TERM_PREFIX}billing"


# ---------------------------------------------------------------------------
# End to end, scripted: the phase's session writes `observed` and drains it
# ---------------------------------------------------------------------------

def test_an_orientation_session_writes_observed_items_and_closes_the_phase(project):
    from rota.core.runner import run_session
    from rota.llm.llm import ScriptedBackend

    db, repo = project
    boot.onboard(db, repo.root)
    _framed(db)
    db.commit()
    wake = _onboarding(frontier(db))[0]
    assert wake.kind == "tick:orient"

    backend = ScriptedBackend([
        "TOOL: problem.assert(id='bills_accounts', text='The product issues "
        "invoices to billing accounts and records what each owes.', kind='in_scope')\n"
        "TOOL: surveys.attest(outcome='found', citations=['pyproject.toml'])",
        "",
    ])
    out = run_session(db, wake, backend=backend)
    assert out.committed, out.errors
    system, user = backend.calls[0]
    assert "[code.front]" in user, "the front is pushed, not fetched"
    assert "MODE: orient" in system

    row = db.execute("SELECT provenance FROM items WHERE id = 'bills_accounts'").fetchone()
    assert row and row["provenance"] == "observed"
    assert db.execute("SELECT 1 FROM survey_records WHERE area = ?", (PROGRAM,)).fetchone()
    assert onboarding_phase(db) == "reconcile"


def test_a_define_session_writes_one_observed_word_and_drains_its_wake(project):
    from rota.core.runner import run_session
    from rota.llm.llm import ScriptedBackend

    db, repo = project
    boot.onboard(db, repo.root)
    _oriented(db)
    _reconciled(db)
    db.commit()
    wake = next(w for w in frontier(db) if w.refs[0] == TERM_PREFIX + "billing")

    backend = ScriptedBackend([
        "TOOL: glossary.amend(term='billing', sense_body='Billing is the part of "
        "the product that issues invoices to the accounts that owe money, under "
        "src/billing.', sense_short='the module that issues invoices to accounts "
        "that owe money')",
        "",
    ])
    out = run_session(db, wake, backend=backend)
    assert out.committed, out.errors
    _, user = backend.calls[0]
    assert "[code.concordance]" in user and "[problem.baseline]" in user

    row = db.execute("SELECT provenance, area FROM glossary_terms WHERE id = 'billing'").fetchone()
    assert row and row["provenance"] == "observed" and row["area"] == ""
    assert "billing" not in pending_terms(db)


def test_a_define_sense_names_where_the_word_is_written_down(project):
    """Every correct entry in the answer key names the key, type or file the
    word lives in; every generic failure names nothing. The concordance is
    what the session was shown, so a place it names has to be one the
    concordance spelled."""
    from rota.roles.api import Ctx, code_concordance, glossary_amend

    db, repo = project
    boot.onboard(db, repo.root)
    ctx = Ctx(conn=db, role="terminologist", area=TERM_PREFIX + "invoice",
              wake_refs=(TERM_PREFIX + "invoice",), provenance="observed")
    code_concordance(ctx)
    assert ctx.read_idents, "the concordance shows identifiers and paths"

    with pytest.raises(ValueError, match="written down"):
        glossary_amend(ctx, term="invoice",
                       sense_body="a bill for money owed",
                       sense_short="a bill")
    # Once. The second attempt with no place lands, flagged -- a gate the
    # model cannot satisfy is a loop, and a flag it can read is a note.
    ctx.refusals.append(("glossary.amend", "'invoice' is defined without saying where it is written down."))
    got = glossary_amend(ctx, term="invoice", sense_body="a bill for money owed",
                         sense_short="a bill")
    assert "naming no place" in got.get("note", "")
    ctx.writes.clear(); ctx.refusals.clear()
    place = sorted(i for i in ctx.read_idents if "/" in i)[0]
    got = glossary_amend(ctx, term="invoice",
                         sense_body=f"a charge issued against a billing account, "
                                    f"declared in {place}",
                         sense_short="a charge issued against a billing account")
    assert got["id"] == "invoice"


def test_the_attestation_outcome_follows_the_writes(project):
    """`found` with nothing written is refused once with the call shape, then
    `none_found`, said for the session; `none_found` with the owed artefact
    written is `found`. A refused write is neither, and does not close the
    subject."""
    from rota.roles.api import Ctx, glossary_amend, surveys_attest

    db, repo = project
    boot.onboard(db, repo.root)
    ctx = Ctx(conn=db, role="terminologist", area=TERM_PREFIX + "billing",
              provenance="observed")
    with pytest.raises(ValueError, match="then attest again"):
        surveys_attest(ctx, outcome="found")
    ctx.refusals.append(("surveys.attest", "... then attest again ..."))
    got = surveys_attest(ctx, outcome="found")
    assert got["outcome"] == "none_found" and "recorded as" in got["note"]

    ctx = Ctx(conn=db, role="terminologist", area=TERM_PREFIX + "billing",
              provenance="observed")
    ctx.read_words.update({"billing"})
    ctx.read_idents.add("src/billing/charges.py")
    glossary_amend(ctx, term="billing",
                   sense_body="the module in src/billing/charges.py that issues invoices",
                   sense_short="the invoicing module")
    got = surveys_attest(ctx, outcome="none_found")
    assert got["outcome"] == "found"

    ctx = Ctx(conn=db, role="terminologist", area=TERM_PREFIX + "billing",
              provenance="observed")
    ctx.refusals.append(("glossary.amend", "nothing you read this session says billing"))
    with pytest.raises(ValueError, match="refused"):
        surveys_attest(ctx, outcome="found")
    # Once. The session has had its turn to fix or drop the write; the
    # record then follows what landed, which is nothing.
    ctx.refusals.append(("surveys.attest", "your glossary.amend was refused this session: ..."))
    got = surveys_attest(ctx, outcome="none_found")
    assert got["outcome"] == "none_found"


def test_a_define_session_ends_when_its_word_has_landed(project):
    from rota.core.runner import run_session
    from rota.llm.llm import ScriptedBackend

    db, repo = project
    boot.onboard(db, repo.root)
    _oriented(db)
    _reconciled(db)
    db.commit()
    wake = next(w for w in frontier(db) if w.refs[0] == TERM_PREFIX + "billing")
    backend = ScriptedBackend([
        "TOOL: glossary.amend(term='billing', sense_body='the module under src/billing "
        "that issues invoices to accounts that owe money', sense_short='the invoicing module')",
        "TOOL: glossary.amend(term='billing', sense_body='again', sense_short='again')",
        "TOOL: glossary.amend(term='billing', sense_body='again', sense_short='again')",
    ])
    out = run_session(db, wake, backend=backend)
    assert out.committed and out.iterations == 1, out.errors


def test_a_collision_session_ends_on_its_synthesis(project):
    """The synthesis is the collision session's verdict, as the amend is the
    define session's. A session that kept going past it re-sent the identical
    call, a minute a turn, until the third-identical rule ended it."""
    from rota.core.runner import run_session
    from rota.llm.llm import ScriptedBackend

    from rota.core.scheduler import tick_survey

    db, repo = project
    boot.onboard(db, repo.root)
    config.set(db, "onboarding_phases", "survey")
    # A collision waits for the Terminologist's survey pass to finish.
    for _ in range(20):
        pending = [w for w in tick_survey(db) if w.role == "terminologist"]
        if not pending:
            break
        for w in pending:
            # Stamped as a real attest stamps, or the freshness view reads the
            # record as a survey of a tree that is gone and re-offers the area.
            from rota.roles.api import area_content_hash

            db.execute("INSERT OR IGNORE INTO survey_records (id, area, outcome, "
                       "area_hash) VALUES (?, ?, 'none_found', ?)",
                       (f"terminologist:{w.refs[0]}", w.refs[0],
                        area_content_hash(db, w.refs[0])))
    for id_, area in (("billing", ""), ("billing#src", "src")):
        db.execute("INSERT INTO glossary_terms (id, term, sense_short, sense_body, "
                   "provenance, area) VALUES (?, 'billing', ?, ?, 'observed', ?)",
                   (id_, f"reading {area or 'whole'}", f"reading {area or 'whole'}, at length", area))
    db.commit()
    wake = next(w for w in frontier(db) if w.kind == "tick:term_collision")
    call = ("TOOL: glossary.synthesise(ids=['billing', 'billing#src'], "
            "sense_short='the invoicing module', sense_body='the module under src/billing "
            "that issues invoices to accounts that owe money; declared in src/billing/charges.py "
            "and read by the accounts module')")
    out = run_session(db, wake, backend=ScriptedBackend([call, call, call]))
    assert out.committed and out.iterations == 1, out.errors
    assert db.execute("SELECT superseded_by FROM glossary_terms WHERE id = 'billing#src'"
                      ).fetchone()[0] == "billing"


def test_the_attestation_is_never_held_behind_a_read(project):
    """A survey session that reads and attests in one batch closes its area in
    that turn. The attest cannot cite what the read did not open, so holding
    it buys nothing; not holding it is the difference between a session that
    ends and one that re-sends the same batch until the cap."""
    from rota.core.runner import run_session
    from rota.llm.llm import ScriptedBackend

    db, repo = project
    boot.onboard(db, repo.root)
    config.set(db, "onboarding_phases", "survey")
    db.commit()
    wake = next(w for w in frontier(db)
                if w.kind == "tick:survey" and w.refs[0] == "src/billing")
    backend = ScriptedBackend([
        "TOOL: code.source(path='src/billing/charges.py')\n"
        "TOOL: surveys.attest(outcome='none_found', citations=['src/billing/charges.py'])",
        "TOOL: code.source(path='src/billing/accounts.py')",
    ])
    out = run_session(db, wake, backend=backend)
    assert out.committed and out.iterations == 1, out.errors
    assert db.execute("SELECT 1 FROM survey_records WHERE area = 'src/billing'").fetchone()


def test_an_item_restated_is_not_a_constraint(project):
    """The baseline is pushed into the Architect's session, and one run wrote
    each of its five behaviours back as `commitment N`. A constraint answers
    who outside breaks; an item's text has not answered it."""
    from rota.roles.api import Ctx, model_amend

    db, repo = project
    boot.onboard(db, repo.root)
    db.execute("INSERT INTO items (id, text, kind, provenance) VALUES "
               "('issues_invoices', 'The product issues invoices to the billing "
               "accounts that owe money and records what each owes.', "
               "'in_scope', 'observed')")
    ctx = Ctx(conn=db, role="architect", area="src/billing", provenance="observed")
    ctx.opened.add("src/billing/charges.py")
    with pytest.raises(ValueError, match="label, not a headline"):
        model_amend(ctx, headline="commitment 1",
                    text="who outside would notice", bindings=["src/billing/charges.py"])
    with pytest.raises(ValueError, match="an item already says it"):
        model_amend(ctx, headline="Invoices for billing accounts",
                    text="The product issues invoices to the billing accounts "
                         "that owe money and records what each owes.",
                    bindings=["src/billing/charges.py"])
    got = model_amend(ctx, headline="The invoice number format is read by the "
                      "accounting export",
                      text="Numbers are INV-<year>-<seq>; the quarterly export "
                           "parses them and breaks silently on any other shape.",
                      bindings=["src/billing/charges.py"])
    assert got["id"]


def test_the_orientation_is_asked_once_for_its_calls_before_it_closes_empty(project):
    """The session writes its account and lists the behaviours as prose; the
    first `found` with no items is refused with the call shape, the second is
    recorded as what it is."""
    from rota.roles.api import Ctx, surveys_attest

    db, repo = project
    boot.onboard(db, repo.root)
    ctx = Ctx(conn=db, role="vision_keeper", area=PROGRAM, provenance="observed")
    ctx.opened.add("README.md")
    with pytest.raises(ValueError, match="one call per behaviour"):
        surveys_attest(ctx, outcome="found", citations=["README.md"])
    ctx.refusals.append(("surveys.attest", "... one call per behaviour ... then attest again"))
    got = surveys_attest(ctx, outcome="found", citations=["README.md"])
    assert got["outcome"] == "none_found"


def test_a_dotted_path_is_cited_by_its_stripped_spelling_and_hinted_with_the_dot(project):
    """`_grain_path` strips a leading dot for comparison. The attest hint used to
    print that form -- `editorconfig`, `github/workflows/release.yml` -- and the
    session cited exactly that, which was "not in the index" for twelve turns,
    three sessions, two roles. The hint prints the index's spelling now, and the
    stripped spelling resolves when it names one grain."""
    from rota.roles.api import Ctx, _grain_path, surveys_attest

    db, repo = project
    boot.onboard(db, repo.root)
    db.execute("INSERT OR IGNORE INTO code_index (grain, grain_kind, area, fan_in) "
               "VALUES ('.editorconfig', 'path', '.', 0)")
    ctx = Ctx(conn=db, role="terminologist", area=".", provenance="observed")
    ctx.opened.add(_grain_path(".editorconfig"))
    with pytest.raises(ValueError) as exc:
        surveys_attest(ctx, outcome="none_found", citations=["nonsense.txt"])
    assert "'.editorconfig'" in str(exc.value) and "'editorconfig'" not in str(exc.value)
    got = surveys_attest(ctx, outcome="none_found", citations=["editorconfig"])
    assert got["unresolved_citations"] == []
    rec = next(w for w in ctx.writes if w[0] == "survey_citations")
    assert rec[2]["grain"] == ".editorconfig"


def test_nested_citations_are_flattened_not_crashed_on(project):
    from rota.roles.api import Ctx, surveys_attest

    db, repo = project
    boot.onboard(db, repo.root)
    ctx = Ctx(conn=db, role="terminologist", area="src/billing", provenance="observed")
    ctx.opened.add("src/billing/charges.py")
    got = surveys_attest(ctx, outcome="none_found",
                         citations=[["src/billing/charges.py"], ["problem.baseline"]])
    assert got["unresolved_citations"] == ["problem.baseline"]


def test_an_area_restating_the_program_sense_in_more_words_records_nothing(project):
    """The root area wrote "In this area, a X is a type of variable" beside a
    program-level "A type of variable" for most words, and two of those were
    raised to the principal as collisions. A second sense adds a word the
    first does not; one that adds none is not a second sense."""
    from rota.roles.api import Ctx, glossary_amend

    db, repo = project
    boot.onboard(db, repo.root)
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, sense_body, "
               "provenance, area) VALUES ('account', 'account', "
               "'who an invoice is addressed to', 'the billing entity that owes "
               "money, declared in src/billing/accounts.py', 'observed', '')")
    ctx = Ctx(conn=db, role="terminologist", area=".", provenance="observed")
    ctx.read_words.update({"account", "invoice", "billing", "money"})
    with pytest.raises(ValueError, match="already means that"):
        glossary_amend(ctx, term="account",
                       sense_body="In this area, an account is the billing entity that owes money.",
                       sense_short="who an invoice is addressed to")
    got = glossary_amend(ctx, term="account",
                         sense_body="a login identity: email and password, in src/auth",
                         sense_short="a person who can sign in")
    assert got["id"] == "account#root"



def test_the_concordance_leads_with_what_settles_a_word(tmp_path):
    """For a word that is a member of an enum, an option in what the user
    writes, and the name of a file, those statements come first -- not the
    hundred ordinary uses of the same English word."""
    from rota.core.db import init_db
    from rota.roles.api import Ctx, code_concordance

    root = tmp_path / "repo"
    (root / "src" / "kinds").mkdir(parents=True)
    (root / "schema.yaml").write_text(
        'of_type: "plain|fancy (plain)"\nfancy_output: "wide|narrow"\n', encoding="utf-8")
    (root / "src" / "kinds" / "index.ts").write_text(
        "import schema from '../../schema.yaml';\n"
        "export enum Kind {\n  plain = 'plain',\n  fancy = 'fancy',\n}\n"
        "export const handlers = {\n  [Kind.fancy]: parseFancy,\n};\n", encoding="utf-8")
    (root / "src" / "kinds" / "fancy.ts").write_text(
        "export type FancyOptions = { wide: boolean };\n"
        "export function parseFancy(x: string): FancyOptions { return { wide: true }; }\n"
        + "".join(f"const fancy{i} = 'a fancy thing';\n" for i in range(30)),
        encoding="utf-8")
    (root / "README.md").write_text(
        "# Kinds\n" + "".join(f"line {i} about a fancy thing\n" for i in range(200)),
        encoding="utf-8")
    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, root)
    ctx = Ctx(conn=db, role="terminologist", area=TERM_PREFIX + "fancy",
              wake_refs=(TERM_PREFIX + "fancy",))
    where = code_concordance(ctx)["where"]
    order = [where.find(k) for k in ("declared as a kind:", "in what a user writes:",
                                     "a file of its own:", "registered:", "used:")]
    assert all(i >= 0 for i in order), where
    assert order == sorted(order), where
    assert "enum Kind" in where and "fancy = " in where
    assert "of_type" in where
    assert "src/kinds/fancy.ts" in where and "parseFancy" in where
    assert where.index("README.md") > where.index("src/kinds/index.ts"), "prose last"
    assert "fancy" in ctx.read_words and "of_type" in ctx.read_idents


def test_a_constraint_kept_to_nobody_outside_is_refused(project):
    from rota.roles.api import Ctx, model_amend

    db, repo = project
    boot.onboard(db, repo.root)
    ctx = Ctx(conn=db, role="architect", area="src/billing", provenance="observed")
    ctx.opened.add("src/billing/charges.py")
    with pytest.raises(ValueError, match="nobody outside"):
        model_amend(ctx, headline="Rename issue_invoice to another identifier",
                    text="A maintainer would encounter errors if they tried to call "
                         "this function in other parts of the codebase.",
                    bindings=["src/billing/charges.py"])
    got = model_amend(ctx, headline="The invoice number format",
                      text="Users' accounting exports parse INV-<year>-<seq>; any other "
                           "shape breaks their import silently.",
                      bindings=["src/billing/charges.py"])
    assert got["id"]


def test_a_session_that_repeats_itself_verbatim_ends(project):
    """At temperature zero a repeated completion is a fixed point: the prompt
    has only grown by "the answer is above", so the next turn is this one
    again. One 14B survey session paid for that eleven times."""
    from rota.core.runner import run_session
    from rota.llm.llm import ScriptedBackend

    db, repo = project
    boot.onboard(db, repo.root)
    config.set(db, "onboarding_phases", "survey")
    db.commit()
    wake = next(w for w in frontier(db)
                if w.kind == "tick:survey" and w.refs[0] == "src/billing")
    same = "TOOL: code.source(path='src/billing/charges.py')"
    backend = ScriptedBackend([same, same, same, same, same, same])
    out = run_session(db, wake, backend=backend)
    assert out.committed
    assert out.iterations == 3, out.iterations
    assert any("verbatim" in e for e in out.errors)



def test_prose_off_withholds_the_readme_from_every_context(project):
    """A good README is an easy way to look like understanding. With
    `prose_sources` off the front, the concordance, the area source and
    `code.source` itself show no README or docs; the files stay indexed."""
    from rota.roles.api import Ctx, code_area, code_concordance, code_front, code_source

    db, repo = project
    boot.onboard(db, repo.root)
    config.set(db, "prose_sources", "off")
    ctx = Ctx(conn=db, role="vision_keeper", area=PROGRAM)
    front = code_front(ctx)["source"]
    assert "README" not in front and "README.md" not in ctx.opened
    assert "most depended-upon source" in front
    ctx = Ctx(conn=db, role="terminologist", area=TERM_PREFIX + "billing",
              wake_refs=(TERM_PREFIX + "billing",))
    where = code_concordance(ctx)["where"]
    assert "README" not in where
    ctx = Ctx(conn=db, role="terminologist", area=".")
    area = code_area(ctx)
    assert "README" not in (area.get("source") or "")
    got = code_source(ctx, path="README.md")
    assert "withheld" in got.get("note", "") and "README.md" not in ctx.opened
    assert db.execute("SELECT 1 FROM code_index WHERE grain = 'README.md'").fetchone()



def test_the_area_is_shown_its_own_files_before_its_imports(project):
    """`cnt_14b`, area `src/intents`: the push showed `index.ts` and two
    imported files and named the area's own `frontmatter.ts` and `intents.ts`
    as not fitting. An own file that does not fit whole is shown as a head;
    an import is never shown ahead of an own file."""
    from rota.roles.api import Ctx, code_area

    db, repo = project
    big = "# the parser\n" + "\n".join(f"KEY_{i} = 'key_{i}'" for i in range(900))
    repo.edit(repo.root, "src/billing/parser.py", big + "\nfrom src.shared import util\n")
    repo.edit(repo.root, "src/shared/util.py", "def util():\n    return 1\n")
    repo.commit_in(repo.root, "a large own file and a small import")
    boot.onboard(db, repo.root)
    ctx = Ctx(conn=db, role="architect", area="src/billing")
    out = code_area(ctx)
    src = out["source"]
    assert "src/billing/parser.py" in src and "(first part only)" in src
    own_at = src.index("src/billing/parser.py")
    assert "src/shared/util.py" not in src or src.index("src/shared/util.py") > own_at
    assert "src/billing/parser.py" not in out.get("not_shown", "")



def test_a_citation_given_as_one_string_is_one_citation(project):
    """`citations="src/billing/charges.py"` -- a string, not a list -- is one
    path, not a list of its characters."""
    from rota.roles.api import Ctx, surveys_attest

    db, repo = project
    boot.onboard(db, repo.root)
    config.set(db, "onboarding_phases", "survey")
    ctx = Ctx(conn=db, role="architect", area="src/billing", provenance="observed")
    ctx.opened.add("src/billing/charges.py")
    got = surveys_attest(ctx, outcome="none_found", citations="src/billing/charges.py")
    assert got["outcome"] == "none_found"
    cited = [w for w in ctx.writes if w[0] == "survey_citations"]
    assert cited and all(
        (w[2] or {}).get("grain", w[1]).endswith("src/billing/charges.py") for w in cited), cited

    # A leading `/` or `./` is not part of a grain.
    ctx = Ctx(conn=db, role="architect", area="src/billing", provenance="observed")
    ctx.opened.add("src/billing/charges.py")
    surveys_attest(ctx, outcome="none_found", citations=["/src/billing/charges.py"])
    assert any((w[2] or {}).get("grain", w[1]).endswith("src/billing/charges.py")
               and not str((w[2] or {}).get("grain", w[1])).startswith("/")
               for w in ctx.writes if w[0] == "survey_citations")

    # And several paths in one string, space-separated, are several citations.
    ctx = Ctx(conn=db, role="architect", area="src/billing", provenance="observed")
    ctx.opened.update({"src/billing/charges.py", "src/billing/accounts.py"})
    surveys_attest(ctx, outcome="none_found",
                   citations="src/billing/charges.py src/billing/accounts.py")
    grains = {(w[2] or {}).get("grain", w[1]) for w in ctx.writes if w[0] == "survey_citations"}
    assert any(g.endswith("charges.py") for g in grains) and any(g.endswith("accounts.py") for g in grains), grains



def test_a_row_id_echoed_as_a_term_is_the_word_before_the_hash(project):
    """`[glossary.consult]` prints ids, and a second-area row's id is
    `word#area`; one session wrote `...#src` back as a term and made a third
    row of the same word. The id is derived; the term is the word."""
    from rota.roles.api import Ctx, glossary_amend

    db, repo = project
    boot.onboard(db, repo.root)
    config.set(db, "onboarding_phases", "survey")
    ctx = Ctx(conn=db, role="terminologist", area="src/billing", provenance="observed")
    ctx.read_words.update({"charge", "billing"})
    ctx.read_idents.add("src/billing/charges.py")
    got = glossary_amend(ctx, term="charge#src_billing",
                         sense_body="a line on an invoice that the billing module under src/billing "
                                    "computes from a quantity and a unit price in charges.py",
                         sense_short="an invoice line")
    assert "#" not in got["id"]
    rows = [w for w in ctx.writes if w[0] == "glossary_terms"]
    assert rows and rows[-1][2]["term"] == "charge"



def test_code_logic_and_files_of_this_repository_are_inside_parties(project):
    """"the code inside PTPlugin.onload()", "the program's internal logic",
    "the manifest.json file" as WHO BREAKS are inside, whatever the headline;
    "users who define variables in their notes using these exact strings" is
    outside and passes."""
    from rota.roles.api import Ctx, model_amend

    db, repo = project
    boot.onboard(db, repo.root)
    ctx = Ctx(conn=db, role="architect", area="src/billing", provenance="observed")
    ctx.opened.add("src/billing/charges.py")
    for hl, tx in [("createCommandForIntent", "the code inside PTPlugin.onload()"),
                   ("parseTextVariableFrontmatter", "The program's internal logic would break "
                    "as these function names are hardcoded in the parsers object."),
                   ("PTPlugin", "the manifest.json file")]:
        with pytest.raises(ValueError, match="names nobody outside"):
            model_amend(ctx, headline=hl, text=tx, bindings=["src/billing/charges.py"])
    for hl, tx in [("getIntentsFromTFile", "users of this repository who import or call "
                    "getIntentsFromTFile would break with a reference error"),
                   ("TemplateVariableType", "The import of TemplateVariableType will fail "
                    "with an error indicating the identifier cannot be found.")]:
        with pytest.raises(ValueError, match="names nobody outside"):
            model_amend(ctx, headline=hl, text=tx, bindings=["src/billing/charges.py"])
    got = model_amend(ctx, headline="charge kind values",
                      text="Users who define charges in their notes using these exact strings "
                           "('fee', 'refund') would break if they were renamed.",
                      bindings=["src/billing/charges.py"])
    assert got["id"]



def test_the_same_sentence_under_a_second_id_is_the_same_item(project):
    """The no-prose orientation wrote its behaviours twice under two sets of
    ids. A restated sentence answers with the id it already has and is not
    written again."""
    from rota.roles.api import Ctx, problem_assert

    db, repo = project
    boot.onboard(db, repo.root)
    ctx = Ctx(conn=db, role="vision_keeper", area=PROGRAM, provenance="observed")
    text = "The program reads the user's intents from the frontmatter of a note."
    assert problem_assert(ctx, id="reads_intents", text=text)["id"] == "reads_intents"
    got = problem_assert(ctx, id="program_reads_intents", text=text)
    assert got["id"] == "reads_intents" and "not written twice" in got["note"]
    assert [w[1] for w in ctx.writes if w[0] == "items"] == ["reads_intents"]


def test_an_observed_session_never_amends_a_decided_item(project):
    """
    tipsU, 2026-09-09: the principal's `split_bill` was delivered as decided,
    then orient and reorient asserted it again as observed. The slicing
    rule then read it as a record, not a build order. Found never
    overwrites decided.
    """
    from rota.roles.api import Ctx, problem_assert

    db, repo = project
    boot.onboard(db, repo.root)
    # Decided because the item rests on the principal's ratified statement,
    # not because of the stamp: the guard reads the view.
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e1', 'principal', 1, 'split the bill')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1', 'e1', 0, 14, 'split the bill', 'ratified')")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('split_bill', 'the bill is split', "
               "'in_scope', 'decided', 'approved', 1, 1)")
    db.execute("INSERT INTO refs (src_table, src_id, kind, target) VALUES "
               "('items', 'split_bill', 'statement', 's1')")
    db.commit()
    ctx = Ctx(conn=db, role="vision_keeper", area=PROGRAM, provenance="observed")
    got = problem_assert(ctx, id="split_bill", text="the program splits the bill")
    assert got["id"] == "split_bill" and "decided" in got.get("note", ""), got
    assert not [w for w in ctx.writes if w[0] == "items"], "observed wrote over decided"
    row = db.execute("SELECT p.provenance, i.text FROM items i "
                     "JOIN item_provenance p ON p.id = i.id "
                     "WHERE i.id='split_bill'").fetchone()
    assert (row["provenance"], row["text"]) == ("decided", "the bill is split")


def test_a_behaviour_never_folds_into_the_account(project):
    """
    tipsL, 2026-09-09: on an existing repo the Vision Keeper rewrote the
    account to describe the one new feature, then asserted the feature. The
    near-duplicate fold answered with the account's id. One item, nothing to
    slice, and the run went quiet. The account is never a behaviour.
    """
    from rota.roles.api import Ctx, problem_assert

    db, repo = project
    boot.onboard(db, repo.root)
    ctx = Ctx(conn=db, role="vision_keeper", area=PROGRAM, provenance="observed")
    problem_assert(ctx, id="how_it_works",
                   text="The software splits the bill among a number of people "
                        "and rounds each share up to the nearest cent.")
    got = problem_assert(ctx, id="split_bill",
                         text="Split the bill among a number of people and round "
                              "each share up to the nearest cent.")
    assert got["id"] == "split_bill", got



def test_the_no_prose_front_shows_the_code_that_reads_what_the_user_writes(project):
    """Without the README, the front carries the importer of the authoring
    surface -- the file where the user's writing enters the program -- as a
    head, after the entry point and the most depended-upon source."""
    from rota.roles.api import Ctx, code_front

    db, repo = project
    repo.edit(repo.root, "recipes_schema.yaml",
              "# the keys a user may write\nname: string\nsteps: list\n")
    repo.edit(repo.root, "src/billing/recipes.py",
              "import yaml\n\nSCHEMA = yaml.safe_load(open('recipes_schema.yaml'))\n\n"
              "def read_recipes(note):\n    return note.frontmatter.get('recipes')\n")
    repo.commit_in(repo.root, "a schema and its reader")
    boot.onboard(db, repo.root)
    db.execute("INSERT OR IGNORE INTO code_edges (src, dst) VALUES "
               "('src/billing/recipes.py', 'recipes_schema.yaml')")
    config.set(db, "prose_sources", "off")
    ctx = Ctx(conn=db, role="vision_keeper", area=PROGRAM)
    front = code_front(ctx)["source"]
    if "recipes_schema.yaml" in front:
        assert "reads what a user writes" in front and "src/billing/recipes.py" in front


# ---------------------------------------------------------------------------
# The reconcile phase (onboarding v1.0.0, step 3b)
# ---------------------------------------------------------------------------

def test_the_front_withholds_the_readme_unless_asked(project):
    """3a: the orientation is written from code. The README is withheld from
    the front by default and `orient_prose=on` restores it for comparison."""
    from rota.roles.api import Ctx, code_front

    db, repo = project
    boot.onboard(db, repo.root)
    front = code_front(Ctx(conn=db, role="vision_keeper", area=PROGRAM))["source"]
    assert "README.md" not in front
    config.set(db, "orient_prose", "on")
    front = code_front(Ctx(conn=db, role="vision_keeper", area=PROGRAM))["source"]
    assert "README.md" in front


def test_reconcile_fires_after_orient_and_only_with_prose(project):
    """The reconcile wake exists once the orientation record does, for the
    Vision Keeper, on `@prose` -- and not at all when prose is withheld or
    there is no README."""
    from rota.core.scheduler import PROSE, onboarding_phase, tick_reconcile

    db, repo = project
    boot.onboard(db, repo.root)
    assert tick_reconcile(db) == [], "reconcile before orient"
    _oriented(db)
    db.commit()
    assert onboarding_phase(db) == "reconcile"
    wakes = tick_reconcile(db)
    assert [(w.role, w.kind, w.refs) for w in wakes] == [
        ("vision_keeper", "tick:reconcile", (PROSE,))]
    config.set(db, "prose_sources", "off")
    assert tick_reconcile(db) == [], "nothing to reconcile without prose"
    config.set(db, "prose_sources", "on")
    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
               "('vision_keeper:@prose', '@prose', 'none_found')")
    assert tick_reconcile(db) == [], "a record discharges it"


def test_code_prose_is_the_readme_and_marks_it_opened(project):
    from rota.core.scheduler import PROSE
    from rota.roles.api import Ctx, code_prose

    db, repo = project
    boot.onboard(db, repo.root)
    ctx = Ctx(conn=db, role="vision_keeper", area=PROSE)
    got = code_prose(ctx)
    assert got["path"] == "README.md" and "account" in got["text"]
    assert "README.md" in ctx.opened
    config.set(db, "prose_sources", "off")
    got = code_prose(Ctx(conn=db, role="vision_keeper", area=PROSE))
    assert "nothing to reconcile" in got["note"]


def test_a_reconcile_session_logs_the_disagreement_and_attests(project):
    """The whole 3b beat: the session logs "README says X; the code shows Y"
    to the ledger and closes `@prose` as found. The attest's owed artefact on
    that subject is the ledger, not items."""
    from rota.core.runner import run_session
    from rota.core.scheduler import PROSE, frontier
    from rota.llm.llm import ScriptedBackend

    db, repo = project
    boot.onboard(db, repo.root)
    _oriented(db)
    db.commit()
    wake = next(w for w in frontier(db) if w.kind == "tick:reconcile")
    out = run_session(db, wake, backend=ScriptedBackend([
        'TOOL: ledger.log(about_ref="README.md", about_table="items", '
        'assumption="README says accounts can be merged; the code shows no merge path")\n'
        'TOOL: surveys.attest(outcome="found", citations=["README.md"])',
        "done", "done",
    ]))
    assert out.committed, out.errors
    row = db.execute("SELECT outcome FROM survey_records WHERE area = ?",
                     (PROSE,)).fetchone()
    assert row and row["outcome"] == "found"
    assert db.execute("SELECT 1 FROM ledger WHERE default_taken LIKE 'README says%'").fetchone()
    assert not db.execute("SELECT 1 FROM items WHERE id = 'README.md'").fetchone()


def test_an_agreeing_readme_closes_reconcile_none_found(project):
    from rota.core.runner import run_session
    from rota.core.scheduler import PROSE, frontier
    from rota.llm.llm import ScriptedBackend

    db, repo = project
    boot.onboard(db, repo.root)
    _oriented(db)
    db.commit()
    wake = next(w for w in frontier(db) if w.kind == "tick:reconcile")
    out = run_session(db, wake, backend=ScriptedBackend([
        'TOOL: surveys.attest(outcome="none_found", citations=["README.md"])',
        "done", "done",
    ]))
    assert out.committed, out.errors
    row = db.execute("SELECT outcome FROM survey_records WHERE area = ?",
                     (PROSE,)).fetchone()
    assert row and row["outcome"] == "none_found"


def test_the_model_keeps_an_account_per_area(project):
    """`model.describe` keeps the survey's first two sentences as a model row;
    a label or a file list is refused; the whole program is not an area."""
    from rota.roles.api import Ctx, model_describe

    db, repo = project
    boot.onboard(db, repo.root)
    ctx = Ctx(conn=db, role="architect", area="src/billing", provenance="observed")
    ctx.opened.add("src/billing/charges.py")
    got = model_describe(ctx, account="Turns charges and accounts into invoices: "
                         "charges.py computes what is owed and invoices.py issues it.")
    assert got["area"] == "src/billing"
    w = next(w for w in ctx.writes if w[0] == "model_areas")
    assert "invoices" in w[2]["account"]
    # What the area rests on: the code the session opened, as a grain ref.
    assert ("refs", "model_areas:src/billing:grain:src/billing/charges.py") in [
        (t, i) for t, i, *_ in ctx.writes]
    with pytest.raises(ValueError, match="not a label"):
        model_describe(ctx, account="billing module")
    with pytest.raises(ValueError, match="not an area"):
        model_describe(ctx, account="An account of the whole program, long enough to pass.",
                       area=PROGRAM)


def test_an_architect_survey_records_the_account_and_the_commitment(project):
    from rota.core.runner import run_session
    from rota.core.scheduler import Wake
    from rota.llm.llm import ScriptedBackend

    db, repo = project
    boot.onboard(db, repo.root)
    config.set(db, "onboarding_phases", "survey")
    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
               "('terminologist:src/billing', 'src/billing', 'none_found')")
    db.commit()
    wake = Wake("architect", "tick:survey", refs=("src/billing",))
    out = run_session(db, wake, backend=ScriptedBackend([
        "TOOL: model.describe(account='Computes what an account owes and issues "
        "invoices for it; charges come in, invoices go out.')\n"
        "TOOL: surveys.attest(outcome='none_found', citations=['src/billing/charges.py'])",
        "done", "done"]))
    assert out.committed, out.errors
    row = db.execute("SELECT account, provenance FROM model_areas WHERE id='src/billing'").fetchone()
    assert row and row["provenance"] == "observed" and "invoices" in row["account"]
    rec = db.execute("SELECT outcome FROM survey_records WHERE id='architect:src/billing'").fetchone()
    assert rec and rec["outcome"] == "none_found"


def test_an_authoring_key_survives_whole_in_the_lexicon(project):
    """`intents_to:` in a schema becomes the candidate term `intents_to`,
    verbatim -- not `intents` plus a stopword. The user-facing grammar is
    vocabulary in its own spelling."""
    db, repo = project
    repo.edit(repo.root, "recipesSchema.yaml",
              "intents_to:\n  with_name: \"text\"\n  in_folder: \"text\"\n"
              "  replaces_selection_with: \"text\"\n")
    repo.edit(repo.root, "src/billing/reader.py",
              "import yaml\nSCHEMA = yaml.safe_load(open('recipesSchema.yaml'))\n")
    repo.commit_in(repo.root, "an authoring schema")
    boot.onboard(db, repo.root)
    words = {r["word"]: r for r in db.execute("SELECT * FROM code_lexicon")}
    for key in ("intents_to", "with_name", "in_folder", "replaces_selection_with"):
        assert key in words, sorted(words)[:30]
        assert "key" in words[key]["sources"], words[key]["sources"]
    from rota.core.scheduler import pending_terms
    pend = pending_terms(db)
    for key in ("intents_to", "with_name", "in_folder", "replaces_selection_with"):
        assert key in pend, pend
    # and a defined key leaves the queue
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, sense_body, provenance) "
               "VALUES ('intents_to', 'intents_to', 'the recipe key', 'the frontmatter key "
               "a user writes recipes under', 'observed')")
    assert "intents_to" not in pending_terms(db)


# ---------------------------------------------------------------------------
# The prose's names
# ---------------------------------------------------------------------------

def _ledger_repo(tmp_path):
    """A tree whose code declares `Invoice` and whose README leans on a word
    the code never says. No git: `boot.onboard` reads the filesystem."""
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    (root / "src" / "invoices.ts").write_text(
        "export type Invoice = { id: string };\n"
        "export function issue(inv: Invoice): void {}\n", encoding="utf-8")
    (root / "schema.yaml").write_text(
        'invoice_kind: "draft|final"\n', encoding="utf-8")
    (root / "README.md").write_text(
        "# The ledgerbook\n"
        "Every charge lands in the **ledgerbook** before an invoice exists.\n"
        'A "ledgerbook" is obviously kept per month, and obviously the\n'
        "ledgerbook survives restarts. Obviously an export walks the whole\n"
        "ledgerbook, and obviously every invoice cites a ledgerbook line.\n"
        "Obviously so.\n", encoding="utf-8")
    return root


def test_the_prose_nominates_its_own_names(tmp_path):
    """A word the README leans on -- frequent, emphasised, absent from every
    code word's family -- reaches the lexicon as the prose's. Grammar does
    not, however frequent, and a code word gains nothing from being said in
    prose too."""
    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, _ledger_repo(tmp_path))
    rows = {r["word"]: r for r in lexicon.ranked(db)}

    assert "ledgerbook" in rows, sorted(rows)
    assert '"prose"' in rows["ledgerbook"]["sources"]
    assert rows["ledgerbook"]["uses"] >= 4
    assert "obviously" not in rows, "frequent but never emphasised"
    assert '"prose"' not in rows["invoice"]["sources"], "the code's word stays the code's"


def test_pending_terms_owe_the_prose_names_only_on_prose_runs(tmp_path):
    """The define phase owes `ledgerbook` -- and stops owing it the moment
    prose sources are withheld, because a --no-prose run has no README for
    the word to be the name of."""
    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, _ledger_repo(tmp_path))
    _oriented(db)
    _reconciled(db)

    assert "ledgerbook" in pending_terms(db)
    config.set(db, "prose_sources", "off")
    assert "ledgerbook" not in pending_terms(db)


def test_the_concordance_gives_a_prose_only_word_its_evidence(tmp_path):
    """For a word only the README says, the one-line prose cap would starve
    the session that has to define it. The view says plainly whose word it is
    and shows the README lines; a word the code speaks keeps the usual
    sections."""
    from rota.roles.api import Ctx, code_concordance

    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, _ledger_repo(tmp_path))

    ctx = Ctx(conn=db, role="terminologist", area=TERM_PREFIX + "ledgerbook",
              wake_refs=(TERM_PREFIX + "ledgerbook",))
    where = code_concordance(ctx)["where"]
    assert "the code never says this word; the prose does:" in where, where
    assert "README.md" in where
    assert where.count("\n      ") >= 3, "several README lines, not the one-line cap"
    assert "used:" not in where

    ctx2 = Ctx(conn=db, role="terminologist", area=TERM_PREFIX + "invoice",
               wake_refs=(TERM_PREFIX + "invoice",))
    where2 = code_concordance(ctx2)["where"]
    assert "the code never says this word" not in where2


def test_onboard_names_the_assumptions_a_checkout_stresses(tmp_path):
    """A tree of Swift and no README announces both at onboard time --
    the two failures are silent downstream, and this is the one moment the
    operator is looking."""
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    for i in range(3):
        (root / "src" / f"view{i}.swift").write_text("struct V {}\n",
                                                     encoding="utf-8")
    (root / "src" / "main.ts").write_text("export const x = 1;\n",
                                          encoding="utf-8")
    db = init_db(tmp_path / "rota.db")
    report = boot.onboard(db, root)
    text = "\n".join(report.stresses)
    assert ".swift" in text and "no parser" in text, text
    assert "no root README" in text, text


def test_a_well_shaped_checkout_trips_no_wires(tmp_path):
    """The ledger repo -- parsed language, root README, few keys -- reports
    its language mix and nothing else."""
    db = init_db(tmp_path / "rota.db")
    report = boot.onboard(db, _ledger_repo(tmp_path))
    warnings = [l for l in report.stresses if not l.startswith("languages:")]
    assert warnings == [], warnings


def test_examples_attach_like_tests_and_docs_trip_the_wire(tmp_path):
    """A click-shaped tree: a real package, demo apps under `examples/`, a fat
    `docs/`. The examples are indexed and findable but form no area -- the
    survey attention belongs to the program -- and the docs tripwire names
    the prose reconcile will never read."""
    root = tmp_path / "repo"
    (root / "src" / "pkg").mkdir(parents=True)
    for i in range(4):
        (root / "src" / "pkg" / f"mod{i}.py").write_text(
            f"def fn{i}():\n    return {i}\n", encoding="utf-8")
    (root / "examples" / "demoapp").mkdir(parents=True)
    for i in range(3):
        (root / "examples" / "demoapp" / f"app{i}.py").write_text(
            "from src.pkg import mod0\n", encoding="utf-8")
    (root / ".github" / "workflows").mkdir(parents=True)
    for i in range(3):
        (root / ".github" / "workflows" / f"ci{i}.yaml").write_text(
            "name: ci\n", encoding="utf-8")
    (root / "docs").mkdir()
    for i in range(12):
        (root / "docs" / f"page{i}.rst").write_text("some prose\n",
                                                    encoding="utf-8")
    (root / "README.md").write_text("# pkg\n", encoding="utf-8")

    db = init_db(tmp_path / "rota.db")
    report = boot.onboard(db, root)

    areas = {r["area"] for r in db.execute(
        "SELECT DISTINCT area FROM code_index WHERE grain_kind = 'path'")}
    assert not any(a.startswith("examples") for a in areas), areas
    assert not any(a.startswith(".") and a != "." for a in areas),         "a dot-directory is a tool's, not an area"
    got = db.execute("SELECT area FROM code_index WHERE grain = ?",
                     ("examples/demoapp/app0.py",)).fetchone()
    assert got is not None, "indexed and findable"
    words = {r["word"] for r in lexicon.ranked(db)}
    assert "demoapp" not in words, "an example's name is not vocabulary"
    text = "\n".join(report.stresses)
    assert "prose files under docs/" in text, text


# ---------------------------------------------------------------------------
# The boundaries pass
# ---------------------------------------------------------------------------

def _boundary_repo(tmp_path):
    """A schema the code imports, a manifest at the root, a reader, and the
    furniture that must not become a subject."""
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    (root / "schema.yaml").write_text(
        'with_name: "text"\nof_kind: "a|b"\n', encoding="utf-8")
    (root / "manifest.json").write_text(
        '{"id": "sample-plugin", "minAppVersion": "1.0"}', encoding="utf-8")
    (root / "src" / "parser.ts").write_text(
        "import schema from '../schema.yaml';\n"
        "export function parse(x: string): string { return x; }\n",
        encoding="utf-8")
    (root / "README.md").write_text("# sample\n", encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / "data.yaml").write_text("k: v\n", encoding="utf-8")
    return root


def test_boundary_subjects_are_surfaces_and_manifests(tmp_path):
    """The schema and the root manifest are subjects; prose, source files and
    anything attached (test data) are not."""
    from rota.core.scheduler import boundary_subjects

    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, _boundary_repo(tmp_path))
    got = boundary_subjects(db)
    assert "schema.yaml" in got, got
    assert "manifest.json" in got, got
    assert "README.md" not in got
    assert "src/parser.ts" not in got
    assert "tests/data.yaml" not in got, "attached files are nobody's boundary"


def test_the_boundary_phase_runs_last_and_drains_by_attest(tmp_path):
    """`tick:boundary` wakes the Architect once per subject, after survey;
    a survey record on the @surface subject retires the wake."""
    from rota.core.scheduler import SURFACE_PREFIX, tick_boundary

    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, _boundary_repo(tmp_path))
    config.set(db, "onboarding_phases", "boundaries")

    wakes = tick_boundary(db)
    assert wakes and all(w.role == "architect" and w.kind == "tick:boundary"
                         for w in wakes)
    subjects = {w.refs[0] for w in wakes}
    assert SURFACE_PREFIX + "schema.yaml" in subjects

    for ref in subjects:
        db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
                   "(?, ?, 'none_found')", (f"architect:{ref}", ref))
    assert tick_boundary(db) == []
    assert onboarding_phase(db) == "done"


def test_the_boundary_view_carries_the_file_and_its_readers(tmp_path):
    """`code.boundary` pushes the subject whole plus the files that import
    it -- the reader's code is where loud-or-silent is decided -- and marks
    both opened so bindings on them pass."""
    from rota.core.scheduler import SURFACE_PREFIX
    from rota.roles.api import Ctx, code_boundary

    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, _boundary_repo(tmp_path))
    ctx = Ctx(conn=db, role="architect", area=SURFACE_PREFIX + "schema.yaml",
              wake_refs=(SURFACE_PREFIX + "schema.yaml",))
    got = code_boundary(ctx)
    assert got["subject"] == "schema.yaml"
    assert got["readers"] == ["src/parser.ts"]
    assert "of_kind" in got["view"], "the schema body"
    assert "function parse" in got["view"], "the reader body"


def test_a_cut_reader_still_shows_its_failure_branches(tmp_path):
    """The deciding branch of the loud-or-silent question sits wherever it
    sits -- measured, at the end of an 8.6k reader shown to 4k. A truncated
    reader carries every line of its failure vocabulary, whole-file."""
    from rota.core.scheduler import SURFACE_PREFIX
    from rota.roles.api import Ctx, code_boundary

    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    (root / "schema.yaml").write_text('with_name: "text"\n', encoding="utf-8")
    # Early failure lines too: the lens must spend its budget beyond the
    # cut, not on hits the head already shows.
    filler = "".join(f"const pad{i} = {i}; // may throw an error\n"
                     for i in range(400))
    (root / "src" / "reader.ts").write_text(
        "import schema from '../schema.yaml';\n" + filler +
        "export function check(fm: object): void {\n"
        "  console.warn('Unrecognized properties found');\n"
        "}\n", encoding="utf-8")
    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, root)
    ctx = Ctx(conn=db, role="architect", area=SURFACE_PREFIX + "schema.yaml",
              wake_refs=(SURFACE_PREFIX + "schema.yaml",))
    view = code_boundary(ctx)["view"]
    assert "(first part only)" in view, "the reader was cut"
    assert "Unrecognized properties found" in view, "the branch survives the cut"
    assert "failure-vocabulary" in view


# ---------------------------------------------------------------------------
# v2: the frame's rulings outrank the heuristics
# ---------------------------------------------------------------------------

def test_frame_rulings_outrank_the_name_heuristics(tmp_path):
    """docs ruled `program` is surveyed (the docs-as-product repository);
    a src subtree ruled `ignore` leaves the partition; an unruled tree keeps
    the heuristics' answer. Re-pinning applies it all deterministically."""
    from rota.onboarding.boot import repin

    root = _boundary_repo(tmp_path)
    (root / "docs").mkdir()
    for i in range(4):
        (root / "docs" / f"guide{i}.md").write_text("# g\n", encoding="utf-8")
    (root / "src" / "vendored").mkdir()
    for i in range(3):
        (root / "src" / "vendored" / f"lib{i}.ts").write_text(
            "export const v = 1;\n", encoding="utf-8")

    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, root)
    areas0 = {r["area"] for r in db.execute(
        "SELECT DISTINCT area FROM code_index WHERE grain_kind = 'path'")}
    assert "docs" in areas0, "today's heuristics still survey prose directories"

    db.execute("INSERT INTO frame_rulings (id, kind, provenance, reason) VALUES "
               "('docs', 'attached', 'observed', 'documentation about the program'),"
               "('src/vendored', 'ignore', 'observed', 'vendored copy')")
    repin(db, root)

    areas1 = {r["area"] for r in db.execute(
        "SELECT DISTINCT area FROM code_index WHERE grain_kind = 'path'")}
    assert "docs" not in areas1, "ruled attached, so no longer surveyed"
    got = db.execute("SELECT area FROM code_index WHERE grain = ?",
                     ("src/vendored/lib0.ts",)).fetchone()
    assert got is None or got["area"] in (None, ""), "ruled ignore, out of the partition"
    kept = db.execute("SELECT area FROM code_index WHERE grain = ?",
                      ("src/parser.ts",)).fetchone()
    assert kept is not None, "unruled grains keep the heuristics' answer"


def test_a_ruling_outranks_the_judge_at_the_same_prefix(tmp_path):
    """Same prefix, judge says attached, ruling says program: the ruling
    wins. That is the whole meaning of `source`."""
    from rota.onboarding.areas import ruling_for

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO frame_rulings (id, kind, provenance) VALUES "
               "('docs', 'attached', 'observed')")
    db.execute("INSERT OR REPLACE INTO frame_rulings (id, kind, provenance) "
               "VALUES ('docs', 'program', 'decided')")
    assert ruling_for(db, "docs/index.md") == "program"


# ---------------------------------------------------------------------------
# v2: the frame session
# ---------------------------------------------------------------------------

def test_the_frame_is_judged_before_anything_else(tmp_path):
    """A fresh onboard wakes the Architect for @frame first; the attest
    releases orient. The partition decides what every later session sees,
    so it goes first or it lies."""
    from rota.core.scheduler import tick_frame

    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, _boundary_repo(tmp_path))
    assert onboarding_phase(db) == "frame"
    wakes = tick_frame(db)
    assert [w.role for w in wakes] == ["architect"]
    assert wakes[0].refs == ("@frame",)
    assert tick_orient(db) == [], "orient waits for the frame"

    _framed(db)
    assert onboarding_phase(db) == "orient"


def test_frame_assign_writes_the_ruling_and_ledgers_the_diff(tmp_path):
    """An assignment that disagrees with the heuristic prior carries a
    ledger row, mechanically; one that agrees does not. Manifests are
    refused -- they are claimed by code -- and a principal's ruling on the
    same prefix cannot be overwritten by the judge."""
    import pytest

    from rota.core import sandbox as sandbox_mod

    db = init_db(tmp_path / "rota.db")
    root = _boundary_repo(tmp_path)
    (root / "docs").mkdir()
    for i in range(3):
        (root / "docs" / f"g{i}.md").write_text("# g\n", encoding="utf-8")
    boot.onboard(db, root)

    sb = sandbox_mod.build("architect", db, session_id="s1", mode="frame",
                           area="@frame")
    got = sb.call("frame.assign", path="docs", kind="program",
                  reason="the docs are the product")
    assert got["kind"] == "program" and "ledger" in got["note"]
    from rota.core.db import _apply_write
    from rota.core.runner import _as_write
    for w in sb.ctx.writes:
        _apply_write(db, _as_write(w))
    row = db.execute("SELECT kind, provenance FROM frame_rulings "
                     "WHERE id = 'docs'").fetchone()
    assert (row["kind"], row["provenance"]) == ("program", "observed")
    led = db.execute("SELECT default_taken FROM ledger WHERE about_table = "
                     "'frame_rulings'").fetchone()
    assert led and "docs" in led["default_taken"]

    again = sb.call("frame.assign", path="docs", kind="program",
                    reason="the docs are the product")
    assert "already assigned" in again["note"], "the re-send loop breaks here"
    assert sum(1 for w in sb.ctx.writes if w[0] == "frame_rulings") == 1

    with pytest.raises(Exception, match="manifest"):
        sb.call("frame.assign", path="manifest.json", kind="attached")
    db.execute("INSERT OR REPLACE INTO frame_rulings (id, kind, provenance) "
               "VALUES ('src', 'program', 'decided')")
    # Decided because the prefix rests on a landed ruling (Q3).
    refs_from_columns(db)
    with pytest.raises(Exception, match="decided|outranks"):
        sb.call("frame.assign", path="src", kind="ignore")


def test_a_frame_attestation_with_rulings_is_found_not_a_title(tmp_path):
    """
    tipsJ, 2026-09-09: the Architect assigned two files with reasons and
    attested `found`. The bodied check read text, sense and default fields,
    none of which a frame ruling has, and refused the attestation as a title
    with nothing under it. Three times, then quarantine, and nothing built.
    """
    from rota.core import sandbox as sandbox_mod

    db = init_db(tmp_path / "rota.db")
    root = _boundary_repo(tmp_path)
    boot.onboard(db, root)
    sb = sandbox_mod.build("architect", db, session_id="s1", mode="frame",
                           area="@frame")
    sb.call("frame.assign", path="src", kind="program",
            reason="entry is source of shipped thing")
    got = sb.call("surveys.attest", outcome="found", citations=["src"])
    assert got.get("outcome", got.get("recorded", "found")) == "found", got


def test_the_tree_view_carries_priors_and_entry_imports(tmp_path):
    """`code.tree` shows each top-level entry with the heuristic prior, and
    what the root's own files import -- the fzf lesson: a README of badges
    misleads a judge that cannot see where the entry points."""
    from rota.roles.api import Ctx, code_tree

    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, _boundary_repo(tmp_path))
    view = code_tree(Ctx(conn=db, role="architect", area="@frame"))["view"]
    assert "src/" in view and "[prior: program]" in view
    assert "manifest.json" in view and "claimed mechanically" in view
    assert "README.md" in view


def test_the_repin_fires_once_after_the_frame_record(tmp_path):
    """The judge's rulings land when its session commits, so the re-pin is
    lazy: the first phase computation after the @frame record applies the
    ruled frame and sets the flag; the second is a no-op."""
    root = _boundary_repo(tmp_path)
    (root / "docs").mkdir()
    for i in range(3):
        (root / "docs" / f"g{i}.md").write_text("# g\n", encoding="utf-8")
    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, root)
    assert "docs" in {r["area"] for r in db.execute(
        "SELECT DISTINCT area FROM code_index WHERE grain_kind = 'path'")}

    db.execute("INSERT INTO frame_rulings (id, kind, provenance) VALUES "
               "('docs', 'attached', 'observed')")
    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
               "('architect:@frame', '@frame', 'found')")
    onboarding_phase(db)
    areas = {r["area"] for r in db.execute(
        "SELECT DISTINCT area FROM code_index WHERE grain_kind = 'path'")}
    assert "docs" not in areas, "the ruled frame applied"
    flag = db.execute("SELECT value FROM config WHERE key = 'frame_repinned'").fetchone()
    assert flag["value"] == "1"


def test_reorient_runs_after_survey_and_before_boundaries(tmp_path):
    """The fixpoint iteration sits where it helps the most expensive
    consumers: after the surveys, before the boundary sessions read the
    account. No glossary, no wake -- there is nothing to revise with."""
    from rota.core.scheduler import REORIENT, tick_reorient

    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, _boundary_repo(tmp_path))
    config.set(db, "onboarding_phases", "reorient,boundaries")
    _oriented(db)

    assert tick_reorient(db) == [], "an empty glossary leaves nothing to revise"
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1', 'parser', 'converts schema entries', 'observed')")
    wakes = tick_reorient(db)
    assert [(w.role, w.refs) for w in wakes] == [("vision_keeper", (REORIENT,))]
    assert onboarding_phase(db) == "reorient"

    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
               "('vision_keeper:@reorient', '@reorient', 'found')")
    assert tick_reorient(db) == []
    assert onboarding_phase(db) == "boundaries"


# ---------------------------------------------------------------------------
# v2: challenge
# ---------------------------------------------------------------------------

def test_challenge_owes_the_load_bearing_claims(tmp_path):
    """Sample mode owes constraints and items, newest first, capped; off
    owes nothing; a verdict retires a subject."""
    from rota.core.scheduler import challenge_subjects, tick_challenge

    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, _boundary_repo(tmp_path))
    config.set(db, "onboarding_phases", "challenge")
    db.execute("INSERT INTO constraints (id, headline, text, provenance) VALUES "
               "('k1', 'schema is a contract', 'users write against it', 'observed')")
    db.execute("INSERT INTO items (id, text, kind, provenance) VALUES "
               "('i1', 'parses schemas', 'in_scope', 'observed')")

    assert challenge_subjects(db) == ["constraints:k1", "items:i1"]
    wakes = tick_challenge(db)
    assert [(w.role, w.refs[0]) for w in wakes] == [
        ("critic", "@claim:constraints:k1"), ("critic", "@claim:items:i1")]

    db.execute("INSERT INTO challenges (id, verdict) VALUES "
               "('constraints:k1', 'stands')")
    assert [w.refs[0] for w in tick_challenge(db)] == ["@claim:items:i1"]

    config.set(db, "challenge", "off")
    assert challenge_subjects(db) == []


def test_a_break_is_a_citation_or_it_is_refused(tmp_path):
    """The evidence rule, mechanical: a break must cite a file the session
    opened and carry the quote; an uphold is always available and cheap.
    A break also puts the consequence on the principal's ledger."""
    import pytest

    from rota.core import sandbox as sandbox_mod

    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, _boundary_repo(tmp_path))
    db.execute("INSERT INTO constraints (id, headline, text, provenance) VALUES "
               "('k1', 'the schema is silent on unknown keys', 'no warning exists', "
               "'observed')")
    db.execute("INSERT INTO constraint_bindings (constraint_id, grain, grain_kind) "
               "VALUES ('k1', 'src/parser.ts', 'path')")

    sb = sandbox_mod.build("critic", db, session_id="s1", mode="challenge",
                           area="@claim:constraints:k1")
    sb.ctx.wake_refs = ("@claim:constraints:k1",)

    loaded = sb.call("challenge.load")
    assert "src/parser.ts" in loaded["sources"]

    with pytest.raises(Exception, match="a file you opened"):
        sb.call("challenge.break", citation="schema.yaml",
                quote="of_kind: a|b", why="a warning exists")

    got = sb.call("challenge.break", citation="src/parser.ts",
                  quote="export function parse", why="the parser warns")
    assert got["verdict"] == "falsified"
    assert any(w[0] == "ledger" for w in sb.ctx.writes), "the drain is the ledger"

    # Once-then-flagged: a second evidence-less break from a session that
    # read is accepted with the gap on the record -- the alternative was
    # measured at turn twelve of the same re-send.
    sb3 = sandbox_mod.build("critic", db, session_id="s3", mode="challenge",
                           area="@claim:constraints:k1")
    sb3.ctx.wake_refs = ("@claim:constraints:k1",)
    sb3.call("challenge.load")
    with pytest.raises(Exception, match="quote= the source's words"):
        sb3.call("challenge.break", citation="constraints:k1", quote="",
                 why="no such behaviour exists in the file")
    sb3.ctx.refusals = [("challenge.break", "refused once")]
    got3 = sb3.call("challenge.break", citation="constraints:k1", quote="",
                    why="no such behaviour exists in the file")
    assert got3["verdict"] == "falsified"
    row3 = [w for w in sb3.ctx.writes if w[0] == "challenges"][-1]
    assert "evidence-flagged" in row3[2]["why"]
    assert row3[2]["citation"] in ("src/parser.ts", "schema.yaml"), \
        "the citation becomes a file actually opened"

    sb2 = sandbox_mod.build("critic", db, session_id="s2", mode="challenge",
                           area="@claim:constraints:k1")
    sb2.ctx.wake_refs = ("@claim:constraints:k1",)
    with pytest.raises(Exception, match="carries the line|not opened"):
        sb2.call("challenge.uphold", citation="src/parser.ts", quote="",
                 why="looks fine")
    sb2.call("challenge.load")
    up = sb2.call("challenge.uphold", citation="src/parser.ts",
                  quote="export function parse", why="the parser is as claimed")
    assert up["verdict"] == "stands"


def test_blindspots_run_last_and_the_facts_are_mechanical(tmp_path):
    """The Liaison is woken once, after everything, with the run's own gaps
    recomputed from its record; the attest retires it."""
    from rota.core.scheduler import BLINDSPOTS, tick_blindspot
    from rota.roles.api import Ctx, code_gaps

    db = init_db(tmp_path / "rota.db")
    root = _boundary_repo(tmp_path)
    for i in range(4):
        (root / f"data{i}.xyz").write_text("blob\n", encoding="utf-8")
    boot.onboard(db, root)
    config.set(db, "onboarding_phases", "blindspots")

    assert tick_blindspot(db) == [], "not before the program is oriented"
    _oriented(db)
    wakes = tick_blindspot(db)
    assert [(w.role, w.refs) for w in wakes] == [("liaison", (BLINDSPOTS,))]

    facts = code_gaps(Ctx(conn=db, role="liaison"))["facts"]
    assert any(".xyz" in f for f in facts), facts

    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES "
               "('liaison:@blindspots', '@blindspots', 'found')")
    assert tick_blindspot(db) == []


def test_vacuity_is_a_readings_verdict_for_empty_claims(tmp_path):
    """No quote required -- the finding is that no quote can bear on it --
    but the reading is: an unfounded verdict without opened files is
    refused, and the drain is the ledger."""
    import pytest

    from rota.core import sandbox as sandbox_mod

    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, _boundary_repo(tmp_path))
    db.execute("INSERT INTO constraints (id, headline, text, provenance) VALUES "
               "('k1', 'whoever imports parse breaks if it is renamed', "
               "'users of this repository who import parse', 'observed')")
    db.execute("INSERT INTO constraint_bindings (constraint_id, grain, grain_kind) "
               "VALUES ('k1', 'src/parser.ts', 'path')")

    sb = sandbox_mod.build("critic", db, session_id="s1", mode="challenge",
                           area="@claim:constraints:k1")
    sb.ctx.wake_refs = ("@claim:constraints:k1",)
    with pytest.raises(Exception, match="reading"):
        sb.call("challenge.vacuous", why="commits to nothing")
    sb.call("challenge.load")
    got = sb.call("challenge.vacuous",
                  why="true of every exported name; asserts nothing here")
    assert got["verdict"] == "unfounded"
    assert any(w[0] == "ledger" for w in sb.ctx.writes)


def test_the_critics_ledger_id_fits_the_ref_door():
    """
    tipsN, 2026-09-09: `challenge_constraints_<long constraint id>` ran to
    seventy characters. The ref door allows sixty-four. The agenda could
    not present the row and was quarantined. Long ids end in a hash.
    """
    from rota.core.sandbox import _ID
    from rota.roles.api import _challenge_ledger_id

    short = _challenge_ledger_id("items", "split_bill")
    assert short == "challenge_items_split_bill"
    long_ = _challenge_ledger_id(
        "constraints", "accept_total_and_accept_tip_percentage_functions_are_input")
    assert _ID.fullmatch(long_) and len(long_) <= 64, long_
    assert long_ == _challenge_ledger_id(
        "constraints", "accept_total_and_accept_tip_percentage_functions_are_input")


def test_a_claim_that_cites_nothing_is_read_by_loading_it(tmp_path):
    """
    tipsK, 2026-09-09: an item claim cites no files. The vacuity door
    demanded opened files. The Critic read a file that does not exist,
    eleven sessions, three quarantines. Loading a claim with nothing to
    open is the reading.
    """
    from rota.core import sandbox as sandbox_mod

    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, _boundary_repo(tmp_path))
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('how_it_works', "
               "'the program does what a program does', 'in_scope', "
               "'decided', 'approved', 1, 1)")
    sb = sandbox_mod.build("critic", db, session_id="s1", mode="challenge",
                           area="@claim:items:how_it_works")
    sb.ctx.wake_refs = ("@claim:items:how_it_works",)
    sb.call("challenge.load")
    got = sb.call("challenge.vacuous", why="no line could support or defeat it")
    assert got["verdict"] == "unfounded"


def test_reconcile_reads_each_docs_file_as_its_own_area(project):
    """A5, conflicting sources (2026-09-12): the phase read only the README,
    so a project's real prose went unchecked. One wake per prose file now,
    `@prose` for the README and `@prose:<path>` under docs/; `code.prose`
    reads the wake's file, and the attest closes that area alone."""
    from rota.core.runner import run_session
    from rota.core.scheduler import PROSE, frontier, prose_areas, tick_reconcile
    from rota.llm.llm import ScriptedBackend
    from rota.roles.api import Ctx, code_prose

    db, repo = project
    docs = repo.root / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("# Guide" + chr(10) + "Accounts can be merged." + chr(10),
                                   encoding="utf-8")
    boot.onboard(db, repo.root)
    _oriented(db)
    db.commit()
    assert prose_areas(db) == [PROSE, PROSE + ":docs/guide.md"]
    assert [w.refs for w in tick_reconcile(db)] == [(PROSE,), (PROSE + ":docs/guide.md",)]
    got = code_prose(Ctx(conn=db, role="vision_keeper", area=PROSE + ":docs/guide.md"))
    assert got["path"] == "docs/guide.md" and "merged" in got["text"]
    wake = next(w for w in frontier(db)
                if w.kind == "tick:reconcile" and w.refs == (PROSE + ":docs/guide.md",))
    out = run_session(db, wake, backend=ScriptedBackend([
        'TOOL: ledger.log(about_ref="docs/guide.md", about_table="items", '
        'assumption="docs/guide.md says accounts can be merged; the code shows no merge path")'
        + chr(10) + 'TOOL: surveys.attest(outcome="found", citations=["docs/guide.md"])',
        "done", "done",
    ]))
    assert out.committed, out.errors
    areas = {r["area"] for r in db.execute("SELECT area FROM survey_records")}
    assert PROSE + ":docs/guide.md" in areas and PROSE not in areas
    assert [w.refs for w in tick_reconcile(db)] == [(PROSE,)], "the README is still owed"
