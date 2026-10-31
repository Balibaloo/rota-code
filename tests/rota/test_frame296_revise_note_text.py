"""
The refusal of a revise on a team's note names the drop first.

Night 156, m125 (frame 296): the principal answered a question about a team
note. s239 ruled the note line `revise`. The refusal named line 1 as the one
revise target, and s239 moved the `revise` there. Line 1 is the request, so
the item went contested and the scheduler abandoned bg_2. No sentence of the
reply named line 1. Over nights 139 to 156 the refusal fired 19 times, and
7 of the next calls moved the revise to line 1, none on words that name it.

Retired by frame 353: the two tests of the team-note revise refusal text.
Frame 345 pass R2 (f5487759) retired that reader, so the text is gone.
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


def test_the_drop_of_the_note_lands(db):
    # Frame 345 passes R1 and R2 (e810eb77, f5487759): the menu of a note
    # line offers `drop`, not `contest`. The drop lands as a contest.
    out = _rule_request(db, M125, {"1": "approve", "2": "approve", "3": "drop"})
    assert out["per_item"]["l_1"] == "contest"
