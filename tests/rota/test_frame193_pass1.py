"""
Frame 193, pass 1: the grouping gate and the words door, on night 137's turns.

The rows are copied from `.rota/clickI_night137.db` and rebuilt inline, as
frame 190's tests do. The design is `plans/frame193-design.md`, sections 2.4,
2.5, 2.F.5 and 2.F.8.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.predicates import Wake, grouping
from rota.core.runner import run_session
from rota.llm.llm import Pins, ScriptedBackend

PINS = Pins(model="stub", temperature=0.0)

ITEM = "confirm_with_default_on_eof"
TICKET = "tk_1_confirm_with_default_on_eof"
CRITERIA = (
    ("cr_1_confirm_eof_default",
     "When show_python=True is set on a command's version option, the version "
     "message must include the running Python interpreter's version as "
     "major.minor.micro. When show_python=False (or omitted), the version "
     "message must remain unchanged."),
    ("cr_2_confirm_eof_default_false",
     "When show_python=False (or omitted) is set on a command's version option, "
     "the version message must not include any Python version information."),
    ("cr_2_confirm_eof_default_value_type",
     "When show_python=True is set on a command's version option, the Python "
     "version string must be of type str and formatted as major.minor.micro."),
    ("cr_3_confirm_eof_default_value_type",
     "When show_python=True is set on a command's version option, the Python "
     "version string must be usable by the caller without type coercion or "
     "error handling."),
    ("cr_4_confirm_eof_default_value_type",
     "When show_python=False (or omitted) is set on a command's version option, "
     "the version message must not raise any exception related to Python "
     "version formatting."),
)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _confirm_item(db, approval="contested"):
    """Night 137 at s321's dispatch: the confirm item, its ticket, its criteria."""
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, priority, "
               "version) VALUES (?, ?, 'in_scope', ?, 1, 1, 1)",
               (ITEM, "Let confirm() take a default_on_eof flag: when stdin is "
                      "closed it returns the default instead of aborting.", approval))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('echo_json', 'echo json', 'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO tickets (id, item_id, text, version, item_ver) "
               "VALUES (?, ?, ?, 1, 1)",
               (TICKET, ITEM, "let confirm() take a default_on_eof flag: when stdin "
                              "is closed it returns the default instead of aborting"))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk_1', 'echo_json', 'echo json')")
    for cid, text in CRITERIA:
        db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                   "VALUES (?, ?, ?, ?)",
                   (cid, TICKET, text,
                    '["src/click/decorators.py::custom_version_option"]'))
    db.execute("INSERT INTO batches (id, item_id, head_commit, status) VALUES "
               "('batch_1_confirm_eof_default', ?, "
               "'34a5e21020937c4548f6e98cce918136d7ee3397', 'abandoned')", (ITEM,))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('batch_1_confirm_eof_default', ?)", (TICKET,))
    db.execute("INSERT INTO batches (id, item_id, head_commit, status) VALUES "
               "('echo_json_group', 'echo_json', "
               "'724dd5c0e82053da6844fbf706993fee340f8a3a', 'merged')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('echo_json_group', 'tk_1')")
    db.commit()


def test_a_contested_items_ticket_takes_no_grouping_wake(db):
    _confirm_item(db)
    assert grouping(db) == []
    # Approved at its version, the item's ticket is offered again.
    db.execute("UPDATE items SET approval = 'approved' WHERE id = ?", (ITEM,))
    db.commit()
    wakes = grouping(db)
    assert len(wakes) == 1 and wakes[0].refs == (TICKET,)
    # An approval of an older version does not cover the amended item.
    db.execute("UPDATE items SET version = 2 WHERE id = ?", (ITEM,))
    db.commit()
    assert grouping(db) == []


S321_CALL = ("TOOL: batches.group(id='batch_1_confirm_eof_default_new', "
             "item_id='confirm_with_default_on_eof', "
             "ticket_ids=['tk_1_confirm_with_default_on_eof'])")


def test_s321s_group_call_on_a_contested_item_is_refused(db):
    _confirm_item(db)
    out = run_session(db, Wake("architect", "tick:grouping", refs=(TICKET,)),
                      backend=ScriptedBackend([S321_CALL, "done"]), pins=PINS,
                      instructions="group")
    want = (f"{ITEM} is contested at version 1, so no batch can run it. "
            f"Group nothing, and stop.")
    assert any(want in e for e in out.errors), out.errors
    assert db.execute("SELECT COUNT(*) FROM batches WHERE id = "
                      "'batch_1_confirm_eof_default_new'").fetchone()[0] == 0


def test_the_refusal_names_the_other_tickets_of_the_wake(db):
    _confirm_item(db)
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('version_option', 'show python', 'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk_1_version_option', 'version_option', 'show python')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('cr_v', 'tk_1_version_option', 'it shows python')")
    db.commit()
    # The real wake: the predicate leaves the contested ticket out.
    wakes = grouping(db)
    assert len(wakes) == 1 and wakes[0].refs == ("tk_1_version_option",)
    out = run_session(db, wakes[0],
                      backend=ScriptedBackend([S321_CALL, "done"]), pins=PINS,
                      instructions="group")
    want = (f"{ITEM} is contested at version 1, so no batch can run it. Group the "
            f"other tickets of your wake, tk_1_version_option, and leave {ITEM}'s.")
    assert any(want in e for e in out.errors), out.errors


def test_a_ticket_grouped_this_session_is_not_named_again(db):
    _confirm_item(db)
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('version_option', 'show python', 'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk_1_version_option', 'version_option', 'show python')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('cr_v', 'tk_1_version_option', 'it shows python')")
    db.commit()
    good = ("TOOL: batches.group(id='b_v', item_id='version_option', "
            "ticket_ids=['tk_1_version_option'])")
    out = run_session(db, grouping(db)[0],
                      backend=ScriptedBackend([good, S321_CALL, "done"]),
                      pins=PINS, instructions="group")
    want = (f"{ITEM} is contested at version 1, so no batch can run it. "
            f"Group nothing, and stop.")
    assert any(want in e for e in out.errors), out.errors


# Night 137's m62: a present of eight lines, the description item first and
# seven ledger rows after it, as s159 saw it.
M62_LEDGER = (
    ("l_dd34f7bf9d", "defines_commands_and_options",
     "the README says: Users define commands and options using decorators in "
     "Python functions, which Click then uses to parse and execute command-line "
     "inputs; the code shows: Click provides a module to test command-line "
     "applications by invoking commands and checking their behavior"),
    ("l_2810ea0153", "how_it_works",
     "the README says: The program is a command-line interface toolkit called "
     "Click. Users write scripts that define commands and options, and Click "
     "handles parsing and executing them; the code shows: Click provides a module "
     "to test command-line applications by invoking commands and checking their "
     "behavior"),
    ("l_599430780f", "parses_and_executes_inputs",
     "the README says: Click parses command-line arguments and options, then "
     "executes the corresponding Python functions with the provided inputs; the "
     "code shows: Click provides a module to test command-line applications by "
     "invoking commands and checking their behavior"),
    ("l_7da9ccdbdf", "provides_command_line_interface",
     "the README says: Click provides a command-line interface that users can "
     "interact with by running scripts that define commands and options; the code "
     "shows: Click provides a module to test command-line applications by invoking "
     "commands and checking their behavior"),
    ("l_eeaaf7a124", "docs/upgrade-guides.md",
     "The README (upgrade-guides.md) mentions deprecations and removals in Click "
     "9.0, but the baseline account does not mention these details. The code does "
     "not show these changes, and the README is stale."),
    ("l_1ca0a576a2", "docs/virtualenv.md",
     "the README says: Users define commands and options using decorators in "
     "Python functions, which Click then uses to parse and execute command-line "
     "inputs.; the code shows: Virtualenv is used to create isolated Python "
     "environments for project dependencies."),
    ("l_5349d29e40", "docs/virtualenv.md",
     "the README says: The program is a command-line interface toolkit called "
     "Click. Users write scripts that define commands and options, and Click "
     "handles parsing and executing them.; the code shows: Virtualenv is used to "
     "create isolated Python environments for project dependencies."),
)
M63 = ("Lines 2 to 5 all use the same code sentence about the testing module, and "
       "that sentence doesn't back any of them, so please match each one to code "
       "that does or drop it. Line 5 also brings back the wording I already "
       "corrected, line 6 calls the README stale without showing why, and lines 7 "
       "and 8 are about virtualenv, which has nothing to do with Click, so please "
       "drop those three. Line 1 is fine.")


def _landing(db, page_id, refs, reply_id, words, seq):
    from rota.core.sandbox import build
    from rota.roles import prompts

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES (?, ?, 'liaison', 'principal', "
               "'present', ?, ?, 'open')", (page_id, page_id, json.dumps(refs), seq))
    db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, "
               "verb, body_refs, body_text, seq, status) VALUES (?, ?, ?, "
               "'principal', 'liaison', 'converse', ?, ?, ?, 'open')",
               (reply_id, page_id, page_id, json.dumps(refs), words, seq + 1))
    db.commit()
    sb = build("liaison", db, mode="normal", session_id="sess_land",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = reply_id
    return sb


def _m62(db):
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, priority, "
               "version, is_description) VALUES ('how_it_works', ?, 'in_scope', "
               "'approved', 2, 1, 2, 1)",
               ("The program is a command-line interface toolkit called Click. "
                "Users write scripts that define commands and options, and Click "
                "parses command-line arguments and options, then executes the "
                "corresponding Python functions with the provided input.",))
    for lid, about, text in M62_LEDGER:
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
                   "kind, status, author) VALUES (?, ?, 'items', ?, 'default', "
                   "'open', 'vision_keeper')", (lid, about, text))
    refs = [lid for lid, _, _ in M62_LEDGER] + ["how_it_works"]
    return _landing(db, "m62", refs, "m63", M63, 62)


@pytest.mark.skip(reason="frame 345 R2: word form, re-pin on the menu form")
def test_s159s_drop_on_lines_2_to_8_lands_as_contest(db):
    sb = _m62(db)
    rulings = {1: "approve", **{n: "drop" for n in range(2, 9)}}
    out = sb.call("rulings.rule", rulings=rulings, words=M63)
    assert out["per_item"]["how_it_works"] == "approve"
    assert {out["per_item"][lid] for lid, _, _ in M62_LEDGER} == {"contest"}
    row = next(w[2] for w in sb.ctx.writes if w[0] == "rulings")
    stored = json.loads(row["per_item"])
    assert [stored[lid] for lid, _, _ in M62_LEDGER] == ["contest"] * 7
    assert "drop" not in stored.values()


@pytest.mark.skip(reason="frame 345 R2: word form, re-pin on the menu form")
def test_a_phrase_maps_by_its_first_word(db):
    sb = _m62(db)
    rulings = {1: "Approve", 2: " drop it ", **{n: "contest" for n in range(3, 9)}}
    out = sb.call("rulings.rule", rulings=rulings, words=M63)
    assert out["per_item"]["how_it_works"] == "approve"
    assert out["per_item"]["l_dd34f7bf9d"] == "contest"


# Night 137's m161: the confirm item, its five criteria and seven ledger rows.
M161_LEDGER = (
    ("l_20da18da15", "cr_3_confirm_eof_default_value_type", "criteria", "tester",
     "the test assumes key where the material is silent"),
    ("l_356b6156e0", "batch_1_confirm_eof_default", "src/click/termui.py::confirm",
     "developer",
     "Preserved existing 'one-retry' behavior by restoring the break statement, "
     "as criteria are silent on this edge case and legacy tests expect it."),
    ("l_6e604ad102", "cr_2_confirm_eof_default_value_type", "criteria", "tester",
     "the test assumes Expected str, got  and Expected int, got  where the "
     "material is silent"),
    ("l_8be6bffe47", "batch_1_confirm_eof_default", "src/click/termui.py",
     "developer",
     "The file currently contains dead code after confirm() (lines 358-360) that "
     "was added by a previous attempt. This dead code must be removed before any "
     "new logic can be safely appended."),
    ("l_a0c7f980d8", "cr_2_confirm_eof_default_false", "criteria", "tester",
     "the test assumes 'Expected Abort exception' and 'Are you sure?' and "
     "'Expected Abort exception, got ' where the material is silent"),
    ("l_ad90d81d32", "cr_4_confirm_eof_default_value_type", "criteria", "tester",
     "the test assumes Expected Abort exception, got  where the material is "
     "silent"),
    ("l_e748ee49a7", "cr_4_confirm_eof_default_value_type", "criteria", "tester",
     "the test assumes 'raise an exception' and that a mock stdin with "
     "closed=True triggers it, where the material is silent"),
)
M162 = ("Line 2's check leaves out the default, and confirm's default is already "
        "no, so it should pass yes as the default and expect yes back. Lines 4 and "
        "5 still pass the word \"yes\" as text, but confirm's default can only be "
        "yes or no, so those checks should pass one of those and expect the same "
        "answer back. Line 6 still repeats line 3, so please drop it. Also, what "
        "does the retry in line 8 mean, and does it change what happens on a "
        "normal prompt?")


def _m161(db):
    _confirm_item(db, approval="pending")
    for lid, about, table, author, text in M161_LEDGER:
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
                   "kind, status, author) VALUES (?, ?, ?, ?, 'default', 'open', ?)",
                   (lid, about, table, text, author))
    refs = [lid for lid, *_ in M161_LEDGER] + [ITEM] + [c for c, _ in CRITERIA]
    return _landing(db, "m161", refs, "m162", M162, 163)


# Frame 197: night 138's m11, a present of eight lines, seven ledger rows and
# the description item, as s94 saw it. m12 is the principal's reply.
M11_LEDGER = (
    ("l_125a8d70dc", "docs/arguments.md",
     "the README says how_it_works; the code shows Click provides a command-line "
     "interface toolkit"),
    ("l_12e747e99d", "docs/arguments.md",
     "the README says defines_commands_and_options; the code shows arguments are "
     "positional and can take nargs=-1"),
    ("l_551dc809f0", "parses_and_executes_inputs",
     "the README says: Click parses command-line arguments and options, then "
     "executes the corresponding Python functions with the provided inputs; the "
     "code shows: The API reference includes functions for parsing and executing "
     "command-line inputs"),
    ("l_8cac936cd4", "how_it_works",
     "the README says: The program is a command-line interface toolkit called "
     "Click. Users write scripts that define commands and options, and Click "
     "handles parsing and executing them; the code shows: The API reference lists "
     "classes and functions for building command-line interfaces, including "
     "commands, options, and utilities"),
    ("l_a9c0ca7d82", "defines_commands_and_options",
     "the README says: Users define commands and options using decorators in "
     "Python functions, which Click then uses to parse and execute command-line "
     "inputs; the code shows: The API reference lists decorators like command, "
     "option, and argument which are used to define commands and options in Click"),
    ("l_ae1ec6ade4", "provides_command_line_interface",
     "the README says: Click provides a command-line interface that users can "
     "interact with by running scripts that define commands and options; the code "
     "shows: The API reference includes classes and functions for building and "
     "interacting with command-line interfaces"),
    ("l_d5f508f6e9", "docs/arguments.md",
     "the README says parses_and_executes_inputs; the code shows Click parses "
     "command-line arguments and executes Python functions"),
)
M12 = ("Lines 2 and 8 are wrong, because on the README side they show a short label "
       "instead of what the README actually says. Please put the README's own words "
       "there. The rest is fine.")


def _m11(db):
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, priority, "
               "version, is_description) VALUES ('how_it_works', ?, 'in_scope', "
               "'approved', 4, 1, 4, 1)",
               ("The program is a command-line interface toolkit called Click. "
                "Users write scripts that define commands and options, and Click "
                "parses command-line arguments and options, then executes the "
                "corresponding Python functions with the provided inputs.",))
    for lid, about, text in M11_LEDGER:
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
                   "kind, status, author) VALUES (?, ?, 'items', ?, 'default', "
                   "'open', 'vision_keeper')", (lid, about, text))
    refs = [lid for lid, _, _ in M11_LEDGER] + ["how_it_works"]
    return _landing(db, "m11", refs, "m12", M12, 11)


# Night 139's m141: the item, its three criteria and the running change bg_3,
# which the page numbers line 5. m142 is the principal's reply.
ITEM_139 = "version_option_show_python"
CRITERIA_139 = (
    ("c1_version_option_show_python",
     "When `version_option` is invoked with `show_python=True`, the output message "
     "must append the running Python version formatted exactly as "
     "`{major}.{minor}.{micro}` (e.g., '3.10.4'), derived from `sys.version_info`."),
    ("c2_version_option_show_python",
     "The `show_python` flag must be a boolean parameter that controls whether the "
     "Python version is appended to the standard version message, defaulting to "
     "False when not explicitly set."),
    ("c3_version_option_show_python",
     "The `show_python` flag must default to False when not explicitly set, "
     "preserving existing behavior where only the package version is shown."),
)
M142 = ("Please don't drop this change; I want the team to fix it. The check for "
        "line 2 seems to call the custom version helper without its callback, so it "
        "should test the real version option instead. The check for line 3 shows "
        "the flag changes nothing yet, so the Python version still needs to be "
        "appended to the message when the flag is on.")


def _m141(db):
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, priority, "
               "version) VALUES (?, ?, 'in_scope', 'approved', 4, 1, 4)",
               (ITEM_139, "Give version_option a show_python flag that appends the "
                          "running Python version to the message."))
    db.execute("INSERT INTO tickets (id, item_id, text, version, item_ver) "
               "VALUES ('tk_1_version_option_show_python', ?, ?, 1, 4)",
               (ITEM_139, "give version_option a show_python flag that appends the "
                          "running Python version to the message"))
    for cid, text in CRITERIA_139:
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                   "(?, 'tk_1_version_option_show_python', ?)", (cid, text))
    db.execute("INSERT INTO batches (id, item_id, head_commit, status, version) "
               "VALUES ('bg_3', ?, '5b04c4ae5c6d02fa81198bd919f9ff152b2850b6', "
               "'running', 1)", (ITEM_139,))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('bg_3', 'tk_1_version_option_show_python')")
    refs = ["bg_3", ITEM_139] + [c for c, _ in CRITERIA_139]
    return _landing(db, "m141", refs, "m142", M142, 144)


# The F2 review of pass 2, findings 1 and 2: a sentence with no number
# spares a criterion line only when it names the line and faults it. No
# recorded reply of nights 170 to 172 has this shape, so the reply below is
# M142 with one sentence added. Line 4 is c3, whose text names `show_python`.
def _s263_with(db, added):
    sb = _m141(db)
    reply = M142 + " " + added
    sb.ctx.conn.execute("UPDATE messages SET body_text = ? WHERE id = 'm142'",
                        (reply,))
    rulings = {"1": "approve", "2": "contest", "3": "revise", "4": "contest",
               "5": "approve"}
    return sb.call("rulings.rule", rulings=rulings, words=reply)


@pytest.mark.skip(reason="frame 345 R2: word form, re-pin on the menu form")
def test_a_sentence_that_names_and_faults_a_criterion_spares_its_contest(db):
    out = _s263_with(db, "The `show_python` default must also hold when the "
                         "flag is passed as None.")
    assert out["per_item"]["c3_version_option_show_python"] == "contest"


@pytest.mark.skip(reason="frame 345 R2: word form, re-pin on the menu form")
def test_a_sentence_that_names_and_agrees_spares_no_contest(db):
    with pytest.raises(ValueError) as e:
        _s263_with(db, "The `show_python` default is fine as it is.")
    assert str(e.value).startswith(
        "The words name lines 2 and 3 and do not name line 4.")
