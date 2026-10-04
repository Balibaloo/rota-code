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
    conn.execute("INSERT INTO items (id, text, kind, approval, "
                 "approval_ver, version) VALUES ('i1','recipes export to csv',"
                 "'in_scope','approved',1,1)")
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


def test_a_surface_names_the_callable_the_item_names(db):
    """A4 (2026-09-10): the item said "a new function named split_bill" and
    both local judges named calculate_tip as the surface, 0/5 each. A fact
    about three texts and the index."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i9', ?, 'in_scope', 'approved', 1, 1)",
               ("Each share is the total with tip divided by the people. "
                "The share lives in a new function named split_bill.",))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk9','i9','split the bill')")
    db.execute("INSERT OR IGNORE INTO code_index (grain, grain_kind, area, fan_in, sym_kind, "
               "content_hash) VALUES ('main.py::calculate_tip','symbol','main',0,'function','x')")
    db.commit()
    sb = build("terminologist", db, mode="normal",
               allow=prompts.mode_tools("terminologist", "criteria"))
    with pytest.raises(ValueError, match="the item names split_bill.*Name split_bill as the surface"):
        sb.call("criteria.specify", id="c_9", ticket_id="tk9",
                text="each share is the total with tip divided by the people",
                surface_refs=["main.py::calculate_tip"])
    out = sb.call("criteria.specify", id="c_9", ticket_id="tk9",
                  text="each share is the total with tip divided by the people",
                  surface_refs=["main.py::split_bill"])
    assert out["id"] == "c_9"


def test_a_call_with_arguments_names_the_callable(db):
    """clickI night 11 (2026-09-11): "an echo_json(obj, indent=2) helper" did
    not match the door's X() shape, and echo_json was refused as invented."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i8', 'Add an echo_json(obj, indent=2) helper next to echo.', "
               "'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk8','i8','add echo_json')")
    db.commit()
    sb = build("terminologist", db, mode="normal",
               allow=prompts.mode_tools("terminologist", "criteria"))
    assert sb.call("criteria.specify", id="c_8", ticket_id="tk8",
                   text="echo_json prints the object as JSON",
                   surface_refs=["echo_json"])["id"] == "c_8"


def test_an_english_word_after_function_is_not_a_name(db):
    """clickI night 116 (2026-10-04): the item said "The confirm() function
    already takes", and the door read `already` as the callable the item
    names. Three Terminologists were refused on every turn with "the item
    names already", and the night gave up on the criteria for the item."""
    _index(db, "src/click/termui.py::confirm")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('confirm_default_on_eof_resolved', ?, "
               "'in_scope', 'approved', 1, 1)",
               ("The confirm() function already takes a default_on_eof flag as "
                "described in s2. The challenge is resolved as the item is "
                "ratified and in scope.",))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk_1_confirm_default_on_eof_resolved', "
               "'confirm_default_on_eof_resolved', ?)",
               ("the confirm() function already takes a default_on_eof flag as "
                "described in s2",))
    db.commit()
    sb = build("terminologist", db, mode="normal",
               allow=prompts.mode_tools("terminologist", "criteria"))
    out = sb.call("criteria.specify", id="cr_1",
                  ticket_id="tk_1_confirm_default_on_eof_resolved",
                  text="confirm returns the default when stdin is closed",
                  surface_refs=["confirm"])
    assert out["id"] == "cr_1"


def _named(db, text):
    from rota.roles.api import _named_new_callables
    _index(db, "src/click/termui.py::confirm", "src/click/utils.py::echo")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i7', ?, 'in_scope', 'approved', 1, 1)", (text,))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk7','i7','')")
    db.commit()
    return _named_new_callables(build("terminologist", db, mode="criteria").ctx, "tk7")


@pytest.mark.parametrize("text", [
    # clickI night 116, the item a Vision Keeper asserted from a decision.
    "The confirm() function already takes a default_on_eof flag.",
    # clickI nights 113 to 117, the echo_json item: `next` on every night.
    "Add a helper next to echo that prints an object as compact JSON.",
    # clickI nights 87 and 96.
    "The function must return the default on EOF.",
    "A function that returns the default, a helper which prints it.",
    # An underscore alone is not an identifier.
    "A helper _ and a function __ are not names.",
    # A kind word before "(" is a plural, not a call.
    "The function(s) of the module return the default.",
])
def test_a_plain_word_after_function_is_not_a_new_callable(db, text):
    assert _named(db, text) == []


@pytest.mark.parametrize("text, name", [
    # clickI nights 113 to 117, and night 11: the call form.
    ("Add an echo_json(obj) helper next to echo.", "echo_json"),
    # A4: the words name it.
    ("The share lives in a new function named split_bill.", "split_bill"),
    ("Add a helper called render.", "render"),
    ("Add the helper `render` to the module.", "render"),
    ("Add a function split_bill to main.", "split_bill"),
    ("Add a method splitBill to the class.", "splitBill"),
    ("Add a function click.echo_json beside echo.", "echo_json"),
    # A leading underscore is a private callable's form.
    ("Add a helper _private to main.", "_private"),
    ("Give the class a method __init__ that takes a name.", "__init__"),
])
def test_a_callable_form_after_function_is_a_new_callable(db, text, name):
    assert _named(db, text) == [name]


def test_a_bare_lowercase_name_after_helper_is_lost_by_decision(db):
    """Frame 125's review (2026-10-04) keeps the form rule. A bare lowercase
    word reads like English, and no night text names a callable that way.
    A rule on "not an English word" would be a stop list under another name."""
    assert _named(db, "add a helper slugify that lowers a title") == []
