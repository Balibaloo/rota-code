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

import pytest

from rota.core.db import init_db

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


def test_s212s_approve_of_faulted_lines_is_refused(db):
    with pytest.raises(ValueError) as e:
        _rule11(db, M105, S212)
    said = str(e.value)
    assert said.startswith('The words fault line 6, "wrong", and line 7, '
                           '"wrong".'), said
    assert "Rule lines 6 and 7 contest or revise" in said


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
    assert {n: c for n, (c, _) in cues.items()} == {
        n: "wrong" for n in (2, 3, 5, 6, 7)} and matched == set()
    assert _line_cues("Line 4 doesn't match what I asked for.")[0][4][0] == (
        "doesn't match")


# Frame 256's review 1: a range word in any case, and a range in the words
# fault reading.
def test_a_range_word_in_any_case_reads_as_a_range():
    from rota.roles.api import _line_reading

    assert _line_reading("lines 2 Through 7 are wrong") == (
        set(range(2, 8)), set())


@pytest.mark.parametrize("words", [
    "Lines 2 through 4 are wrong, because their checks call plain echo.",
    "Lines 2-4 are also wrong.",
])
def test_the_words_fault_a_range_of_checks(words):
    from rota.roles.api import _WORDS_FAULT

    assert _WORDS_FAULT.search(words)


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


@pytest.mark.xfail(strict=True, reason=(
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
