"""
Criteria carry their surface the way they already carry their terms.

The delivery wall, named after eight one-fault passes: the Tester is black-box
by charter, so the criterion is its only material -- and nothing required a
criterion to name an entry point a test could call. "The email stored is
lowercase" is true, checkable in principle, and untestable black-box: stored
where, reached how? `term_refs`' own docstring is the argument with two words
swapped: a criterion naming an unknown surface is a Tester guessing later.

Three pieces, pinned separately: the vetting at both doors, the candidate
lens (`code.surface`), and the push that supplies the wake's subject -- the
guard-without-an-exit shape is only avoided if the candidates arrive without
being asked for.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.runner import push_working_set
from rota.core.predicates import Wake
from rota.core.sandbox import build
from rota.roles import prompts


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance, approval, "
                 "approval_ver, version) VALUES ('i1','recipes export to csv',"
                 "'in_scope','decided','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('t1','i1','export the recipes as csv')")
    conn.commit()
    return conn


def _index(conn, *grains):
    for g in grains:
        conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) "
                     "VALUES (?, 'symbol', 'function')", (g,))
    conn.commit()


# --- the vetting, both doors -------------------------------------------------

def test_a_bare_name_resolves_to_the_grain_that_owns_it(db):
    _index(db, "src/export.py::export_recipe_csv")
    sb = build("terminologist", db, mode="criteria")
    sb.call("criteria.specify", id="c1", ticket_id="t1", text="x",
            surface_refs=["export_recipe_csv"])
    assert json.loads(sb.ctx.writes[-1][2]["surface_refs"]) == [
        "src/export.py::export_recipe_csv"]


def test_a_test_is_not_a_surface(db):
    """
    tipsS, 2026-09-09: the split's first criterion named a test function as
    its surface. The Tester then tested the split through the tip function
    the second criterion named, and the fix loop ran to the step cap.
    """
    _index(db, "tests/test_calculate_tip.py::test_calculate_tip",
           "src/export.py::export_recipe_csv")
    sb = build("terminologist", db, mode="criteria")
    with pytest.raises(ValueError, match="a test is not a surface"):
        sb.call("criteria.specify", id="c1", ticket_id="t1", text="x",
                surface_refs=["test_calculate_tip"])
    sb.call("criteria.specify", id="c1", ticket_id="t1", text="x",
            surface_refs=["export_recipe_csv"])


def test_a_typo_is_refused_with_its_neighbour_named(db):
    """'regster' is one dropped letter from a real symbol; LIKE cannot see
    that, which is why the scan is fuzzy rather than substring."""
    _index(db, "src/auth.py::register")
    sb = build("terminologist", db, mode="criteria")
    with pytest.raises(ValueError, match="register"):
        sb.call("criteria.specify", id="c1", ticket_id="t1", text="x",
                surface_refs=["regster"])


def test_a_name_with_no_neighbour_is_a_design_not_a_typo(db):
    """Greenfield-on-brownfield: the callable does not exist *yet*, and naming
    the intended entry point is exactly what a criterion is for. Refusing it
    would be a guard with no legal exit on every new-feature ticket."""
    _index(db, "src/auth.py::register")
    sb = build("terminologist", db, mode="criteria")
    sb.call("criteria.specify", id="c1", ticket_id="t1", text="x",
            surface_refs=["export_csv"])
    assert json.loads(sb.ctx.writes[-1][2]["surface_refs"]) == ["export_csv"]


def test_specify_without_a_surface_lands_but_says_so(db):
    _index(db, "src/auth.py::register")
    sb = build("terminologist", db, mode="criteria")
    out = sb.call("criteria.specify", id="c1", ticket_id="t1", text="x")
    assert "no surface named" in out.get("note", "")
    assert json.loads(sb.ctx.writes[-1][2]["surface_refs"]) == []


def test_respecify_without_a_surface_is_refused(db):
    """The repair exists because words alone could not be tested, so words
    alone cannot be the fix -- the one door where the surface is required."""
    _index(db, "src/auth.py::register")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c9','t1','vague words')")
    db.commit()
    sb = build("terminologist", db, mode="criterion_repair")
    with pytest.raises(ValueError, match="names no surface"):
        sb.call("criteria.respecify", id="c9", text="better words")
    sb.call("criteria.respecify", id="c9", text="register() stores lowered",
            surface_refs=["register"])
    assert json.loads(sb.ctx.writes[-1][2]["surface_refs"]) == [
        "src/auth.py::register"]


def test_an_empty_index_never_blocks_either_door(db):
    """A greenfield repository has no symbols to vet against, and the repair
    door must stay open there too."""
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c9','t1','vague')")
    db.commit()
    sb = build("terminologist", db, mode="criteria")
    sb.call("criteria.specify", id="c1", ticket_id="t1", text="x",
            surface_refs=["make_thing"])
    assert json.loads(sb.ctx.writes[-1][2]["surface_refs"]) == ["make_thing"]
    sb2 = build("terminologist", db, mode="criterion_repair")
    out = sb2.call("criteria.respecify", id="c9", text="better")
    assert out["respecified"]


# --- the lens ----------------------------------------------------------------

def test_the_lens_splits_identifiers_the_way_vocabulary_does(db):
    """'export the recipes' finds snake_case and CamelCase both, because the
    words live inside the identifiers."""
    _index(db, "src/export.py::export_recipe_csv",
           "src/export.py::RecipeExporter", "src/auth.py::register")
    sb = build("terminologist", db, mode="criteria")
    got = {r["grain"] for r in sb.call("code.callables",
                                       hint="export the recipes")}
    assert "src/export.py::export_recipe_csv" in got
    assert "src/export.py::RecipeExporter" in got
    assert "src/auth.py::register" not in got


def test_the_lens_says_when_there_is_nothing_to_match(db):
    sb = build("terminologist", db, mode="criteria")
    out = sb.call("code.callables", hint="anything")
    assert "no symbols" in out[0]["note"]


# --- the push ----------------------------------------------------------------

def test_the_candidates_arrive_without_being_asked_for(db):
    """The guard is only fair if the material to satisfy it is supplied. The
    hint is the wake's subject -- this item's ticket headlines -- never the
    role's to choose."""
    _index(db, "src/export.py::export_recipe_csv", "src/auth.py::register")
    sb = build("terminologist", db, mode="criteria",
               allow=prompts.mode_tools("terminologist", "criteria"))
    pushed = push_working_set(
        "terminologist", sb, Wake("terminologist", "tick:criteria",
                                  refs=("i1",)))
    grains = {r["grain"] for r in pushed["code.callables"]}
    assert "src/export.py::export_recipe_csv" in grains, \
        "the ticket says 'export the recipes as csv' and the push matched it"


def test_the_repair_push_matches_the_askers_note(db):
    _index(db, "src/export.py::export_recipe_csv", "src/auth.py::register")
    sb = build("terminologist", db, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    pushed = push_working_set(
        "terminologist", sb,
        Wake("terminologist", "tick:criterion_repair", refs=("m1",)),
        asked="how would a test reach the csv export?")
    grains = {r["grain"] for r in pushed["code.callables"]}
    assert "src/export.py::export_recipe_csv" in grains


# --- the delivery ------------------------------------------------------------

def test_the_tester_finally_sees_the_surface(db):
    """`criteria.load` is the Tester's whole material, and this row is the
    first code-shaped fact ever to reach the black-box role -- legally,
    because a name to call is intent's vocabulary, not implementation."""
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
               "VALUES ('c1','t1','exports land in out.csv',"
               "'[\"src/export.py::export_recipe_csv\"]')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES "
               "('b1','i1','running')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('b1','t1')")
    db.commit()
    sb = build("tester", db, batch_id="b1")
    rows = sb.call("criteria.load")
    assert json.loads(rows[0]["surface_refs"]) == [
        "src/export.py::export_recipe_csv"]
