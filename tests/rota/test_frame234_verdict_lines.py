"""
The verdict's contest lands only on a line the words fault.

Night 146 (frame 234): nine of 22 Liaison verdicts on numbered pages
contested lines the principal's words never faulted. s427 contested lines 1
to 4 when the words said they match, and s122 contested line 1, the request,
when the words faulted lines 3 and 5. Each cancelled a batch. The door
`rulings.rule` now reads the words for line references with a direction.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db

from .test_principal_reply import _landing, _present


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


S122_SHAPE = ("Line 3 isn't right: the user should not type the bill at all. "
              "Line 4 also goes too far, because I didn't ask for a typed "
              "percentage, so please drop it.")


def _rule(db, words, rulings):
    ask = _present(db)
    sb, _ = _landing(db, ask, words)
    return sb.call("rulings.rule", rulings=rulings, words=words)


def test_a_contest_on_lines_the_words_say_match_is_refused(db):
    words = "Ok, go ahead. Lines 1 to 4 match what I asked for."
    with pytest.raises(ValueError) as e:
        _rule(db, words, {"1": "contest", "2": "contest", "3": "contest",
                          "4": "contest"})
    assert "lines 1 to 4" in str(e.value) and "reverses" in str(e.value)
    assert "Approve lines 1 to 4." in str(e.value)


def test_the_refusal_names_only_the_matched_lines_contested(db):
    words = "Ok, go ahead. Lines 1 to 4 match what I asked for."
    with pytest.raises(ValueError, match=r"Approve lines 1 to 3\.$"):
        _rule(db, words, {"1": "contest", "2": "contest", "3": "contest",
                          "4": "approve"})


def test_a_contest_on_the_request_line_the_words_do_not_fault_is_refused(db):
    with pytest.raises(ValueError) as e:
        _rule(db, S122_SHAPE, {"1": "contest", "2": "approve", "3": "contest",
                               "4": "contest"})
    text = str(e.value)
    assert "Line 1 is the request" in text
    assert text.startswith("The words fault lines 3 and 4.")
    assert "Rule lines 3 and 4, and approve the rest." in text


def test_the_same_words_land_when_line_1_is_approved(db):
    out = _rule(db, S122_SHAPE, {"1": "approve", "2": "approve", "3": "contest",
                                 "4": "contest"})
    assert out["per_item"] == {"s1": "approve", "calculate_tip": "approve",
                               "how_it_works": "contest", "l_1": "contest"}


def test_words_that_fault_line_1_land_a_contest_on_it(db):
    words = "1 is wrong: the request should say json, not yaml"
    out = _rule(db, words, {"1": "contest", "2": "approve", "3": "approve",
                            "4": "approve"})
    assert out["per_item"]["s1"] == "contest"


def test_an_approval_and_a_named_fault_land_as_before(db):
    out = _rule(db, "fine", {"1": "approve", "2": "approve", "3": "approve",
                             "4": "approve"})
    assert set(out["per_item"].values()) == {"approve"}


def test_a_named_fault_on_line_4_lands(tmp_path):
    db = init_db(tmp_path / "rota.db")
    out = _rule(db, "4 is wrong", {"1": "approve", "2": "approve",
                                   "3": "approve", "4": "contest"})
    assert out["per_item"]["l_1"] == "contest"


def test_a_quote_of_line_1_lets_the_request_be_contested():
    from rota.roles.api import _quotes_line

    page = ('1. "Add an echo_json helper that prints compact JSON"\n'
            "2. The helper writes one newline.\n")
    assert _quotes_line("Please change add an echo_json helper that prints "
                        "pretty JSON instead.", page, 1)
    assert not _quotes_line("Line 2 is wrong.", page, 1)


# The recorded replies of night 146, verbatim from the `messages` table of
# `.rota/clickI_night146.db`.
RECORDED = {
    "s427": ("Ok, go ahead. Lines 1 to 4 match what I asked for, and the files "
             "in line 5 look reasonable for the change.",
             set(), {1, 2, 3, 4, 5}),
    "s122": ("Line 3 isn't right: I don't want any special conversion, so "
             "objects should go straight to the standard library json module "
             "and fail with its usual error when they can't be serialized. "
             "Line 5 also goes too far, because I didn't ask for anything about "
             "the pager, so please drop the pager test and keep the new test in "
             "the existing echo tests file.",
             {3, 5}, set()),
    "s245": ("Line 2 is wrong because the helper should write the compact JSON "
             "and one newline to the stream the way echo does, and return "
             "nothing. Line 4 is wrong because the helper should not catch "
             "errors and should let the usual json error through when an object "
             "can't be serialized. Line 5 names the wrong files, since shell "
             "completion has nothing to do with this, and the helper belongs in "
             "the utils module next to echo, with its test in the existing utils "
             "tests rather than in new files.",
             {2, 4, 5}, set()),
    "s307": ("Line 1 names the context, formatting and termui test files, but "
             "only the utils module and the existing echo tests file should "
             "change. Line 9 is wrong because the helper prints the compact JSON "
             "with one newline and does not return a string. Line 10 is also "
             "wrong because the helper should let the usual json error through, "
             "not return an error string.",
             {1, 9, 10}, set()),
    "s221": ("Line 1 names the wrong files. The context and formatting tests "
             "have nothing to do with this, and the new test belongs in the "
             "existing echo tests file, next to the helper in utils. Line 1 also "
             "no longer says to use only the standard library json module, or "
             "that the helper fails with the usual json error when it can't "
             "serialize an object, so please put both back.",
             {1}, set()),
}


@pytest.mark.parametrize("session", sorted(RECORDED))
def test_the_reader_on_the_recorded_replies(session):
    from rota.roles.api import _line_reading

    words, faulted, matched = RECORDED[session]
    assert _line_reading(words) == (faulted, matched)
