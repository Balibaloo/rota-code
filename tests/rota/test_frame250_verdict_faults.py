"""
The verdict takes no approve of a line the principal's words fault.

Night 149 (frame 250): s212 approved lines 6 and 7 of m91's page against
the reply m105, "Lines 2, 3, 5, 6 and 7 are also wrong", and the ruling
landed. cr_5 and cr_6 kept "instead of raising a UsageError" after five
contests. `_line_refusal` refused a contest of a matched line and had no
branch for an approve of a faulted line.

The clarify route of the frame is not built. Its predicate refused 40 of
69 right clarify approves over nights 143 to 149 (`f250/pass1-report.md`),
so m81's case stays an expected failure.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.roles.principal import land, parse_reply, pending_asks, render_page
from rota.testkit.fixtures import seed_provenance

from .test_frame234_verdict_lines import _rule11, _rule_request


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


# Night 149's m105, verbatim from the `rulings` table of
# `.rota/clickI_night149.db`, row r_80d30c50e6, ruled by s212.
M105 = ("Lines 3 and 5 can be checked simply: call confirm without the flag "
        "while stdin is closed, and expect it to abort the same way it does "
        "today. Lines 2, 3, 5, 6 and 7 are also wrong to say \"instead of "
        "raising a UsageError\", because confirm aborts on closed stdin and does "
        "not raise that error. Please fix those lines and keep going with the "
        "change, not drop it.")
# s212's landed map, lines 1 to 8. On night 149, line 8 was bg_2. On the
# fixture page, lines 8 to 11 are team notes that the words do not name.
S212 = {"1": "approve", "2": "contest", "3": "contest", "4": "approve",
        "5": "contest", "6": "approve", "7": "approve", "8": "approve",
        "9": "approve", "10": "approve", "11": "approve"}


def test_s212s_map_with_the_faulted_lines_contested_lands(db):
    rulings = dict(S212, **{"6": "contest", "7": "contest"})
    out = _rule11(db, M105, rulings)
    assert out["per_item"]["c1"] == "contest"
    assert out["per_item"]["l_2"] == "contest"


def test_a_right_approve_of_a_matched_line_lands(db):
    words = "Line 3 is wrong. Lines 2 and 4 match what I asked for."
    rulings = {str(n): "approve" for n in range(1, 12)}
    rulings["3"] = "contest"
    out = _rule11(db, words, rulings)
    assert out["per_item"]["c1"] == "approve"
    assert out["per_item"]["c2"] == "contest"


def test_an_approve_of_the_request_line_the_words_fault_lands(db):
    # Night 146's m164 faulted the code that line 1 names, not the request.
    words = ("Line 1 names the options, termui and basic test files, but only "
             "the utils module and the existing echo tests file should change.")
    rulings = {str(n): "approve" for n in range(1, 12)}
    out = _rule11(db, words, rulings)
    assert out["per_item"]["calculate_tip"] == "approve"


def test_the_cue_names_the_strong_word_of_the_clause():
    from rota.roles.api import _line_cues

    cues, matched = _line_cues(M105)
    # "Lines 3 and 5 can be checked simply" is an instruction, and the
    # inverted reader faults lines 3 and 5 there first (frame 305, pass 2).
    assert {n: c for n, (c, _) in cues.items()} == {
        2: "wrong", 3: "can be checked", 5: "can be checked", 6: "wrong",
        7: "wrong"} and matched == set()
    assert _line_cues("Line 4 doesn't match what I asked for.")[0][4][0] == (
        "doesn't match")


# Frame 256's review 1: a range word in any case, and a range in the words
# fault reading.
def test_a_range_word_in_any_case_reads_as_a_range():
    from rota.roles.api import _line_reading

    assert _line_reading("lines 2 Through 7 are wrong") == (
        set(range(2, 8)), set())


# Night 148's m81, verbatim from the `rulings` table of
# `.rota/clickI_night148.db`, row r_3340e1e9d9. The night's rows were
# d_f422882cbd, d_74_challenge_ver_opt_show_py, ver_opt_show_py and
# tst_ver_opt_show_py, all ruled approve. The fixture's rows stand in.
M81 = ("Yes. The test should expect the Python version at the end of the "
       "normal version message, written as major, minor and micro joined by "
       "dots, for example 3.12.4. It should not expect only the command name "
       "and the Python version. The error says no installed package was "
       "found, so I suggest the simple choice: give the test a fixed version "
       "string so it doesn't need to look up an installed package.")


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "frame 250: the clarify fault reading refused 40 of 69 right approves "
    "on nights 143 to 149, so the brief stops that route after the count"))
def test_m81s_clarify_approve_of_a_faulted_row_is_refused(db):
    with pytest.raises(ValueError, match="should not"):
        _rule_request(db, M81, {"calculate_tip": "approve",
                                "how_it_works": "approve"}, verb="clarify")


def test_a_clarify_reply_that_only_agrees_approves(db):
    out = _rule_request(db, "Yes, that is right.",
                        {"calculate_tip": "approve",
                         "how_it_works": "approve"}, verb="clarify")
    assert set(out["per_item"].values()) == {"approve"}


# Frame 250, review 1, finding 1: the approve door spared every batch line,
# and an open change's line the words fault landed approved. The scene is
# night 145's bg_4 page m245, rebuilt from `.rota/clickI_night145.db`, read
# with `mode=ro` on 2026-10-16. bg_4 runs at head commit 04d4368f.
B4_ITEM = "cr_3_show_python_append"
B4_CRITERIA = (
    ("cr_1_cr_3_show_python_append", "tk_1_cr_3_show_python_append",
     "When a command with a fixed Python version (e.g., 1.0) is invoked with "
     "the version option, the printed output must include the running Python "
     "interpreter's version string written as major.minor.micro."),
    ("cr_2_cr_3_show_python_append_format", "tk_1_cr_3_show_python_append",
     "The appended Python version string in the printed output must be "
     "formatted as major.minor.micro, taken from Python's own version info, "
     "and must not alter existing formatting or separators."),
    ("cr_3_cr_3_show_python_append_default", "tk_1_cr_3_show_python_append",
     "When `show_python` is False (default), the version message must behave "
     "exactly as it did before this feature was added."),
    ("cr_4_cr_3_show_python_append", "tk_2",
     "The `show_python` flag must be accepted by the `version_option` "
     "decorator without error."),
)
B4_TOUCH = (
    "src/click/decorators.py::custom_version_option",
    "src/click/decorators.py::version_option",
    "tests/test_basic.py::test_custom_version_option",
    "tests/test_basic.py::test_version_option_ambiguous_import_name_errors",
    "tests/test_basic.py::test_version_option_resolves_import_name_to_distribution",
    "tests/test_basic.py::test_version_option_unknown_package_errors",
    "tests/test_defaults.py::test_flag_default_map",
    "tests/test_defaults.py::test_flag_default_map_with_callable_flag_value",
    "tests/test_defaults.py::test_multiple_flag_default",
    "tests/test_options.py::test_flag_value_show_default",
)
# The words of ruling r_f38b69e7c3 on m245, reply m246, verbatim.
M246 = ("Please don't give up on this change. The tests in lines 2 to 4 are "
        "wrong because the version option never returns a message, so they "
        "should run a command that has a fixed version like 1.0 and has the "
        "version option, then check the printed output. Line 6 is also still "
        "wrong because the work should touch only the version option code and "
        "its tests in test_basic, not the tests for option flags and default "
        "maps.")
# The landed map of r_f38b69e7c3, by line. Line 6 is bg_4.
M245_MAP = {"1": "approve", "2": "contest", "3": "contest", "4": "approve",
            "5": "approve", "6": "approve"}


@pytest.fixture
def m245(db):
    """bg_4 at its head commit, running, and the open page m245."""
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version, priority) VALUES (?, ?, 'in_scope', 'approved', 2, 2, 1)",
               (B4_ITEM, "The `version_option` decorator must support a "
                         "`show_python` flag that appends the running Python "
                         "version to the version message without altering other "
                         "formatting or separators. This is a required feature "
                         "and is within scope."))
    seed_provenance(db, "items", B4_ITEM, "decided")
    db.execute("INSERT INTO batches (id, item_id, head_commit, status, version) "
               "VALUES ('bg_4', ?, '04d4368f1e3186bf173fd1a6f18bc0f9c0082e95', "
               "'running', 1)", (B4_ITEM,))
    for tid, text in (
            ("tk_1_cr_3_show_python_append",
             "the `version_option` decorator must support a `show_python` flag"),
            ("tk_2", "the `show_python` flag appends the running Python version "
                     "to the version")):
        db.execute("INSERT INTO tickets (id, item_id, text, version, item_ver) "
                   "VALUES (?, ?, ?, 1, 2)", (tid, B4_ITEM, text))
        db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) "
                   "VALUES ('bg_4', ?)", (tid,))
    for cid, tid, text in B4_CRITERIA:
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, ?, ?)",
                   (cid, tid, text))
    for grain in B4_TOUCH:
        db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, "
                   "confidence) VALUES ('bg_4', ?, 'path', 'expected')", (grain,))
        db.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, 'path')",
                   (grain,))
    refs = ["bg_4", B4_ITEM] + [c for c, _, _ in B4_CRITERIA]
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, status, seq) VALUES ('m245', 'm245', 'liaison', "
               "'principal', 'present', ?, 'open', 1)", (json.dumps(refs),))
    db.commit()
    return db


def _rule_m245(db, rulings):
    from rota.core.sandbox import build
    from rota.roles import prompts

    (ask,) = [a for a in pending_asks(db) if a.message_id == "m245"]
    reply = land(db, ask, parse_reply(ask, M246))
    db.commit()
    sb = build("liaison", db, mode="landing",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = reply
    return sb.call("rulings.rule", rulings=rulings, words=M246)


def test_the_m245_page_numbers_bg_4_as_line_6(m245):
    _, order = render_page(m245, "present", json.loads(m245.execute(
        "SELECT body_refs FROM messages WHERE id = 'm245'").fetchone()
        ["body_refs"]), ask_id="m245")
    assert order == [B4_ITEM] + [c for c, _, _ in B4_CRITERIA] + ["bg_4"]


def test_the_night_map_is_refused_for_lines_4_and_6(m245):
    with pytest.raises(ValueError) as e:
        _rule_m245(m245, M245_MAP)
    assert str(e.value).startswith(
        'The words fault line 4, "wrong", and line 6, "wrong".'), str(e.value)


def test_an_approve_of_the_open_change_line_is_refused(m245):
    """The seat fixes line 4 and keeps the approve of line 6. Before
    review 1's fix, the ruling landed and the files correction was lost."""
    with pytest.raises(ValueError) as e:
        _rule_m245(m245, dict(M245_MAP, **{"4": "contest"}))
    said = str(e.value)
    assert said.startswith('The words fault line 6, "wrong".'), said
    assert "Rule line 6 contest or revise" in said


def test_the_map_with_line_6_contested_lands(m245):
    out = _rule_m245(m245, dict(M245_MAP, **{"4": "contest", "6": "contest"}))
    assert out["per_item"]["bg_4"] == "contest"
    assert out["per_item"][B4_ITEM] == "approve"


# These tests pin the doors of the word form of a page call. Pass R2
# retires the doors and these pins (frame 345, the R1 brief, step 5).
pytestmark = pytest.mark.usefixtures("old_page_form")
