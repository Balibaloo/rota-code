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


def _split_bill(db):
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i7', ?, 'in_scope', 'approved', 1, 1)",
               ("Each share is the total with tip divided by the people. "
                "The share lives in a new function named split_bill.",))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk7','i7','split the bill')")
    _index(db, "main.py::calculate_tip")
    return build("terminologist", db, mode="normal",
                 allow=prompts.mode_tools("terminologist", "criteria"))


def test_an_existing_callable_beside_the_new_one_is_refused(db):
    """Frame 257, night 160's gate: c_004 named calculate_tip beside
    split_bill, the door admitted it, and the row held the old callable."""
    sb = _split_bill(db)
    with pytest.raises(ValueError) as err:
        sb.call("criteria.specify", id="c_7", ticket_id="tk7",
                text="split_bill divides the total with tip by the people",
                surface_refs=["main.py::calculate_tip", "split_bill"])
    said = str(err.value)
    assert "split_bill" in said and "calculate_tip" in said
    assert "The surface is what the test calls." in said
    assert 'surface_refs=["split_bill"]' in said
    assert len(said.split()) < 60


def test_the_route_repeats_the_seats_own_ref(db):
    sb = _split_bill(db)
    with pytest.raises(ValueError, match=r'surface_refs=\["main.py::split_bill"\]'):
        sb.call("criteria.specify", id="c_7", ticket_id="tk7",
                text="split_bill divides the total with tip by the people",
                surface_refs=["main.py::split_bill", "calculate_tip"])


def test_the_new_callable_beside_its_own_file_is_admitted(db):
    """Review 2 of pass 1c: a file row is not an old behaviour."""
    sb = _split_bill(db)
    db.execute("INSERT INTO code_index (grain, grain_kind) VALUES ('main.py', 'path')")
    db.commit()
    assert sb.call("criteria.specify", id="c_7", ticket_id="tk7",
                   text="split_bill divides the total with tip by the people",
                   surface_refs=["split_bill", "main.py"])["id"] == "c_7"


def test_the_new_callable_alone_is_admitted(db):
    sb = _split_bill(db)
    assert sb.call("criteria.specify", id="c_7", ticket_id="tk7",
                   text="split_bill divides the total with tip by the people",
                   surface_refs=["split_bill"])["id"] == "c_7"


def test_an_item_with_no_new_callable_keeps_a_mixed_surface(db):
    """The rule reads only an item that names a new callable."""
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i6', 'give calculate_tip a rounding flag', "
               "'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk6','i6','round the tip')")
    _index(db, "main.py::calculate_tip", "main.py::display_results")
    sb = build("terminologist", db, mode="normal",
               allow=prompts.mode_tools("terminologist", "criteria"))
    assert sb.call("criteria.specify", id="c_6", ticket_id="tk6",
                   text="calculate_tip rounds the tip",
                   surface_refs=["main.py::calculate_tip",
                                 "main.py::display_results"])["id"] == "c_6"


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
    from rota.roles.api import item_callables
    _index(db, "src/click/termui.py::confirm", "src/click/utils.py::echo")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i7', ?, 'in_scope', 'approved', 1, 1)", (text,))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk7','i7','')")
    db.commit()
    return item_callables(build("terminologist", db, mode="criteria").ctx, "tk7").new


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


_N142_TEXT = ("When show_python=True, the command's output when --version is used "
              "must include a line containing the Python version string derived "
              "from sys.version_info.")
_IMAGEPIPE = "examples/imagepipe/imagepipe.py::process_commands"
# Night 142's text with the new callable in backticks, for frame 202's door.
_N142_TEXT_NAMED = ("When show_python=True, the output of `process_commands` "
                    "names the Python version from sys.version_info.")


def _night142(db):
    """Night 142's rows for `tk_2` and `batch_3`. The criterion's text before
    s536 is not on record, so the old text here is a stand-in."""
    _index(db,"examples/imagepipe/imagepipe.py::process_commands",
           "src/click/decorators.py::version_option")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('show_python_version_flag', ?, 'in_scope', "
               "'approved', 1, 1)",
               ("Give version_option a show_python flag that appends the running "
                "Python version to the message. The version should come from the "
                "running interpreter's version info as major.minor.micro. The "
                "check should confirm that the Python version is in the output "
                "and not just look at the exit code. The tests should put the "
                "version option on a real command, not on a plain function.",))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_2', "
               "'show_python_version_flag', 'give version_option a show_python "
               "flag that appends the running Python, version to the message')")
    # Night 142's statement and its link, from the night's database copy.
    db.execute("INSERT INTO entries (id, author, text, ts_order, version) VALUES "
               "('e_p4', 'principal', ?, 83, 1)",
               ("Give version_option a show_python flag that appends the running "
                "Python version to the message.",))
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
               "status, version) VALUES ('s4', 'e_p4', 0, 94, ?, 'ratified', 1)",
               ("Give version_option a show_python flag that appends the running "
                "Python version to the message.",))
    db.execute("INSERT INTO refs (src_table, src_id, kind, target, resolves) VALUES "
               "('items', 'show_python_version_flag', 'statement', 's4', 1)")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES "
               "('c_show_python_version', 'tk_2', 'The --version output names "
               "the Python version.', '[\"src/click/decorators.py::version_option\"]')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES "
               "('batch_3_show_python_version_flag', 'show_python_version_flag', 'running')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('batch_3_show_python_version_flag', 'tk_2')")
    for grain, kind, conf in (("src/click/decorators.py", "path", "expected"),
                              ("tests/test_basic.py", "path", "expected"),
                              ("custom_version_option", "symbol", "possible"),
                              ("version_option", "symbol", "possible")):
        db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, confidence) "
                   "VALUES ('batch_3_show_python_version_flag', ?, ?, ?)",
                   (grain, kind, conf))
    db.commit()


def _repair(db):
    return build("terminologist", db, mode="criterion_repair",
                 allow=prompts.mode_tools("terminologist", "criterion_repair"))


def test_a_repair_surface_outside_the_batch_files_is_refused(db):
    """
    Frame 215, night 142's s536 (seq 15 to 19): the relay of the principal's
    m376 woke the repair. s536 set the surface of `tk_2`'s criteria to the
    first row of `[code.callables]`, a module in `examples/` that imports
    `PIL`. The batch expected `src/click/decorators.py` and
    `tests/test_basic.py`, and no word of the request or the criterion
    names `process_commands`. The rows are night 142's.
    """
    _night142(db)
    text = _N142_TEXT
    sb = build("terminologist", db, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    with pytest.raises(ValueError) as refused:
        sb.call("criteria.respecify", id="c_show_python_version", text=text,
                term_refs=["show_python"],
                surface_refs=["examples/imagepipe/imagepipe.py::process_commands"])
    said = str(refused.value)
    assert "src/click/decorators.py" in said and "tests/test_basic.py" in said
    assert "process_commands" in said
    # The callable in the expected file lands, as today.
    out = sb.call("criteria.respecify", id="c_show_python_version", text=text,
                  term_refs=["show_python"],
                  surface_refs=["src/click/decorators.py::version_option"])
    assert out["respecified"]
    # A ticket in no batch passes as today.
    db.execute("DELETE FROM batch_tickets")
    db.commit()
    sb2 = build("terminologist", db, mode="criterion_repair",
                allow=prompts.mode_tools("terminologist", "criterion_repair"))
    # Frame 202's request rule refuses a move that drops `version_option`
    # unless the text names the new callable, so this text names it.
    assert sb2.call("criteria.respecify", id="c_show_python_version",
                    text=_N142_TEXT_NAMED,
                    surface_refs=["examples/imagepipe/imagepipe.py::process_commands"]
                    )["respecified"]


def test_a_name_the_seat_writes_into_its_own_text_does_not_admit_the_surface(db):
    """
    Frame 215's review 1, finding 1, probe p1 case e2: the door read its
    words from the new text, so `process_commands` in the rewrite admitted
    the imagepipe surface, and the refusal told the seat how. The words
    come from the item, its statements and the ticket.
    """
    _night142(db)
    with pytest.raises(ValueError, match="tests/test_basic.py"):
        _repair(db).call(
            "criteria.respecify", id="c_show_python_version",
            text="When show_python=True, process_commands output names the Python version.",
            surface_refs=[_IMAGEPIPE])


def test_an_abandoned_batch_neither_admits_nor_names_a_surface(db):
    """
    Frame 215's review 1, finding 6, probe p1 case g: `tk_2` also sat in
    the abandoned `batch_2`, whose touch rows held imagepipe.py, and the
    union admitted the surface. An abandoned batch's prediction is not
    the work's.
    """
    _night142(db)
    db.execute("INSERT INTO batches (id, item_id, status) VALUES "
               "('batch_2_show_python_version_flag', 'show_python_version_flag', 'abandoned')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('batch_2_show_python_version_flag', 'tk_2')")
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, confidence) VALUES "
               "('batch_2_show_python_version_flag', 'examples/imagepipe/imagepipe.py', "
               "'path', 'expected')")
    db.commit()
    with pytest.raises(ValueError) as refused:
        _repair(db).call("criteria.respecify", id="c_show_python_version",
                         text=_N142_TEXT, surface_refs=[_IMAGEPIPE])
    named = str(refused.value).split("expects to touch", 1)[1].split(". No word", 1)[0]
    assert named.strip() == "src/click/decorators.py, tests/test_basic.py"


def test_only_the_statement_names_the_callable_and_the_surface_is_admitted(db):
    """
    Frame 215's review 1b, finding 2, probe q1 case e5: the item, the
    ticket and the new text do not name `process_commands`. Statement `s4`
    names it, and the door reads the item's statements, so the surface lands.
    """
    _night142(db)
    db.execute("UPDATE statements SET text = text || ' process_commands' WHERE id = 's4'")
    db.commit()
    # Frame 202's request rule needs the new callable in the text. A name in
    # the text does not admit frame 215's door, so the statement still decides.
    out = _repair(db).call("criteria.respecify", id="c_show_python_version",
                           text=_N142_TEXT_NAMED, surface_refs=[_IMAGEPIPE])
    assert out["respecified"]


def test_a_cleared_load_cache_sees_a_dependency_installed_at_the_same_head(db, tmp_path):
    """
    Frame 215's review 1b, finding 1, probe q2 `pkg.late`: a deferred batch
    resumes at the same head, and `provision.ensure_env` installs what the
    module imports. The cached failure outlived the install until
    `lifecycle.start` cleared the worktree's keys.
    """
    import types

    from rota.roles import api
    root = tmp_path / "wt"
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "__init__.py").write_bytes(b"")
    (root / "pkg" / "late.py").write_bytes(b"import rota_late_dep\ndef f(): pass\n")
    db.execute("INSERT INTO batches (id, item_id, status, worktree, head_commit) "
               "VALUES ('b_late', 'i1', 'running', ?, 'abc123')", (str(root),))
    db.commit()
    ctx = types.SimpleNamespace(conn=db, batch_id="b_late")
    first = api._module_load_error(ctx, "pkg.late", "pkg/late.py")
    assert first and "rota_late_dep" in first
    # The install: the dependency becomes importable with no commit.
    (root / "rota_late_dep.py").write_bytes(b"X = 1\n")
    api.clear_load_cache(root)
    assert api._module_load_error(ctx, "pkg.late", "pkg/late.py") is None
