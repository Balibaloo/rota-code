"""
The identity registry's trial run.

The principal's caution, verbatim: "the approach needs designing here, be
careful" -- and then "ok lets test it out". So the rule runs as an ordinary
test before it is a law: every table in the schema declares its sameness
rule, a new table fails the build until classified, and `unkeyed` is a legal
answer that stays visible instead of a gap that stays invisible. LAWS.md is
untouched; if this lint lives quietly, the law is just naming a fact.
"""
from __future__ import annotations

import re

from rota import paths
from rota.core.identity import NATURAL_KEYS
from rota.testkit.fixtures import seed_provenance

KINDS = {"words", "span", "term", "slug", "relation", "supersede", "content",
         "keyed", "journal", "ephemeral", "unkeyed"}


def _schema_tables() -> set[str]:
    sql = paths.SCHEMA.read_text(encoding="utf-8")
    return set(re.findall(r"CREATE TABLE IF NOT EXISTS (\w+)", sql))


def test_every_table_declares_what_makes_two_rows_the_same():
    """A new table fails here until it answers the question the four healed
    organs each learned by incident."""
    tables = _schema_tables()
    missing = sorted(tables - set(NATURAL_KEYS))
    assert not missing, (
        f"{missing} declare no sameness rule. Add each to NATURAL_KEYS -- "
        f"'unkeyed' with a reason is a legal answer; silence is not")


def test_the_registry_names_no_phantom_tables():
    stray = sorted(set(NATURAL_KEYS) - _schema_tables())
    assert not stray, f"NATURAL_KEYS classifies tables that do not exist: {stray}"


def test_every_kind_is_from_the_declared_vocabulary():
    bad = sorted((t, k) for t, (k, _) in NATURAL_KEYS.items() if k not in KINDS)
    assert not bad, bad


def test_every_entry_says_where_or_why():
    """A classification with no enforcement note is a label; the registry's
    value is that each row points at the door that holds its rule."""
    empty = sorted(t for t, (_, why) in NATURAL_KEYS.items()
                   if len(why.strip()) < 10)
    assert not empty, empty


def test_the_unkeyed_column_is_small_and_named():
    """The honest column stays visible: today it is exactly the two tables
    that have never produced an over-production incident. If this list grows,
    a new table took the easy answer -- make it argue its case here."""
    unkeyed = sorted(t for t, (k, _) in NATURAL_KEYS.items() if k == "unkeyed")
    assert unkeyed == ["business_rules", "items"], unkeyed


def test_the_lint_can_fail():
    """A fabricated table must trip the coverage check."""
    tables = _schema_tables() | {"widgets"}
    missing = sorted(tables - set(NATURAL_KEYS))
    assert "widgets" in missing


# --- the promise half: a ref must resolve ------------------------------------

def test_a_ref_that_names_no_row_is_refused(tmp_path):
    """The audit found 258 broken promises in the historical runs -- labels
    like 'work_stalled' in body_refs, composed in good faith and meaningless
    at the recipient. The door now demands resolution: a row that exists, a
    row staged this session, an entry, or an @-prefixed non-row subject."""
    import pytest as _pytest

    from rota.core.db import init_db
    from rota.core.sandbox import build

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short)"
               " VALUES ('g1','recipe','x')")
    seed_provenance(db, "glossary_terms", "g1", "observed")
    db.commit()
    sb = build("terminologist", db, mode="unresolved")
    with _pytest.raises(ValueError, match="names no row"):
        sb.call("msg.answer_liaison", refs=["work_stalled"])
    sb.call("msg.answer_liaison", refs=["g1"])
    assert sb.ctx.outbound


def test_an_at_ref_must_name_an_area_this_run_declared(tmp_path):
    """
    Night 85 (2026-09-18): a blindspot session copied a `code.gaps` fact line
    whole and logged a ledger row about `@constraint_zero` in `model_areas`,
    which held `.` and `src/click` and nothing else. The gap reached the page
    as an assumption and the signoff wrote a decision with a dangling ref. Any
    `@` string passed before; an area this run declared passes now.
    """
    import pytest as _pytest

    from rota.core.db import init_db
    from rota.core.sandbox import build

    db = init_db(tmp_path / "rota.db")
    for area in (".", "src/click"):
        db.execute("INSERT INTO model_areas (id, account) VALUES (?, 'x')",
                   (area,))
    db.commit()
    sb = build("liaison", db, mode="blindspot")

    with _pytest.raises(ValueError, match="names no row"):
        sb.call("ledger.log", about_ref="@constraint_zero",
                about_table="model_areas",
                assumption="no constraint binds the zero case")
    assert sb.call("ledger.log", about_ref="@src/click",
                   about_table="model_areas",
                   assumption="the decorators keep their names")["id"]
    # The onboarding subjects that are not directories stay legal: a survey of
    # `@program` has no area row and still has assumptions to log.
    assert sb.call("ledger.log", about_ref="@program", about_table="items",
                   assumption="the whole program is one command")["id"]


def test_an_assumption_is_about_an_artefact_never_about_an_assumption(tmp_path):
    """
    tipsQ, 2026-09-09: the Terminologist logged an assumption about a ledger
    row, under `about_table="glossary_terms"`, with a tool refusal as its
    text. The agenda put it to the principal and the approval woke the
    Terminologist, which logged the next one. 36 rounds.
    """
    import pytest as _pytest

    from rota.core.db import init_db
    from rota.core.sandbox import build

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short)"
               " VALUES ('g1','recipe','x')")
    seed_provenance(db, "glossary_terms", "g1", "observed")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "status, author) VALUES ('l_1','g1','glossary_terms','x','open','terminologist')")
    db.commit()
    sb = build("terminologist", db, mode="deliver")
    with _pytest.raises(ValueError, match="is a ledger row"):
        sb.call("ledger.log", about_ref="l_1", about_table="glossary_terms",
                assumption="The id 'l_1' is not a row in the glossary_terms table.")
    with _pytest.raises(ValueError, match="is a row of glossary_terms, not of items"):
        sb.call("ledger.log", about_ref="g1", about_table="items", assumption="x")
    assert sb.call("ledger.log", about_ref="g1", about_table="glossary_terms",
                   assumption="recipe means the written one")["id"]


def test_a_row_staged_this_session_is_a_legal_ref(tmp_path):
    """Sends and writes commit together, so a ref to a row written moments
    ago in the same session must pass -- refusing it would make the commonest
    honest flow (write, then point at what you wrote) illegal."""
    from rota.core.db import init_db
    from rota.core.sandbox import build

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e_m_in','principal',1,'people can export recipes as csv')")
    db.commit()
    sb = build("liaison", db, mode="converse", entry_id="e_m_in")
    sb.call("brief.segment", id="s_new1", span_start=0, span_end=33,
            text="people can export recipes as csv")
    sb.call("msg.confirm_principal", refs=["s_new1"])
    assert sb.ctx.outbound


def test_the_ledger_is_about_rows_not_tables(tmp_path):
    import pytest as _pytest

    from rota.core.db import init_db
    from rota.core.sandbox import build

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) VALUES ('i1','x','in_scope',"
               "'approved',1,1)")
    db.commit()
    sb = build("developer", db, mode="tests_failing")
    with _pytest.raises(ValueError, match="names no row"):
        sb.call("ledger.log", about_ref="glossary",
                about_table="glossary_terms", assumption="terms lowercase")
    out = sb.call("ledger.log", about_ref="i1", about_table="items",
                  assumption="closure includes soft delete")
    assert out["id"].startswith("l_")


def test_an_artefact_id_is_unique_across_tables(tmp_path):
    """Law 14 at the id level, walked live: tickets, criteria and tests all
    shared t1/t2/t3 -- each role copying the table before it -- and a
    challenge naming the test resolved to the criterion. Refused at birth."""
    import pytest as _pytest

    from rota.core.db import init_db
    from rota.core.sandbox import build

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) VALUES ('i1','x','in_scope',"
               "'approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('t1','i1','y')")
    db.commit()
    sb = build("terminologist", db, mode="criteria")
    with _pytest.raises(ValueError, match="already a row of tickets"):
        sb.call("criteria.specify", id="t1", ticket_id="t1", text="z",
                surface_refs=["run"])
    out = sb.call("criteria.specify", id="c1", ticket_id="t1", text="z",
                  surface_refs=["run"])
    assert out["id"] == "c1", "a distinct id lands"
