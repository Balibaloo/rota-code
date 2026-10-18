"""
The refusal of a revise on a team's note names the drop first.

Night 156, m125 (frame 296): the principal answered a question about a team
note. s239 ruled the note line `revise`. The refusal named line 1 as the one
revise target, and s239 moved the `revise` there. Line 1 is the request, so
the item went contested and the scheduler abandoned bg_2. No sentence of the
reply named line 1. Over nights 139 to 156 the refusal fired 19 times, and
7 of the next calls moved the revise to line 1, none on words that name it.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db

from .test_frame234_verdict_lines import _rule_request


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


# The principal's words at m125, verbatim (`.rota/clickI_night156.db`).
M125 = ("As far as I know, that code doesn't do this. Click's version message "
        "today shows only the program name and its version, not the Python "
        "version, so please build the flag as new work. The Python version "
        "should come from sys.version_info as major.minor.micro.")


def test_s239s_revise_of_a_note_is_not_steered_to_line_1(db):
    # s239's call 1 shape: the note line revised, the request line approved.
    # Line 1 is calculate_tip and line 3 is the note l_1.
    with pytest.raises(ValueError) as refused:
        _rule_request(db, M125, {"1": "approve", "2": "approve", "3": "revise"})
    text = str(refused.value)
    assert text.startswith("line 3 is the team's note, not your request. "
                           "To drop the note, contest it.")
    assert "line 1" not in text and "calculate_tip" not in text
    assert "needs the principal's words on the request" in text


def test_words_that_name_line_1_keep_it_as_the_revise_target(db):
    words = ("Line 1 should say that the tip rounds up to the cent. Line 3 is "
             "not needed.")
    with pytest.raises(ValueError) as refused:
        _rule_request(db, words, {"1": "approve", "2": "approve", "3": "revise"})
    text = str(refused.value)
    assert text.startswith("line 3 is the team's note, not your request. "
                           "To drop the note, contest it.")
    assert "line 1, calculate_tip" in text


def test_the_contest_of_the_note_lands(db):
    out = _rule_request(db, M125, {"1": "approve", "2": "approve", "3": "contest"})
    assert out["per_item"]["l_1"] == "contest"
