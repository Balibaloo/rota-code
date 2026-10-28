"""F2 pass 2: the rulings door reads his words from the record.

Night 172 (`plans/f2-night172-read.md`, sections 1 and 6). s271 put his
words in `acts` and passed no top-level `words`, and the door refused the
contest with "words is empty". s258's landed call contested line 4 on a
reply that names line 12 only, and its act on line 12 rested on the whole
reply. Each case replays one call of the night on a copy of the night's
register, in the state of that call. The register is not tracked, so a
clone without `.rota/clickI_night172.db` skips every test here.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from rota.roles import api

NIGHT = Path(__file__).resolve().parents[2] / ".rota" / "clickI_night172.db"
if not NIGHT.exists():
    NIGHT = Path("D:/repos/rota/.rota/clickI_night172.db")

# His replies, word for word from the night's `messages`.
W121 = ("Please fix the change instead of giving up: put back the two removed "
        "lines of code, because only the docstring changes and the code stays "
        "the same. Line 12 is wrong, because my last answer was not empty: I "
        "said the example shows both the input path and the short output, and "
        "the removed code must go back. The other lines are fine.")
W131 = ("Put back the two removed lines of code, because only the docstring "
        "changes and the code stays the same. Drop lines 9 to 15, because they "
        "are about other parts of click that this change does not touch. Line "
        "18 is wrong because that answer asked for the fix and did not call "
        "line 4 wrong, and lines 1 to 8, 16 and 17 are fine.")
LATE = ["m121", "m128", "m129", "m131", "m132"]
A = "approve"
R8 = {str(i): A for i in range(1, 9)}
R18 = {**R8, **{str(i): "contest" for i in range(9, 16)}, "16": A, "17": A}
S271_SPAN = ("Fix the change instead of giving up by putting back the two "
             "removed lines of code, because only the docstring changes and "
             "the code stays the same.")
S274_ACTS = {"18": {"verdict": "contest", "act": "remove", "target_kind": "row",
                    "words": "Line 18 is wrong because that answer asked for "
                             "the fix and did not call line 4 wrong"}}
REVERSAL = ("The words say line 4 matches what the principal asked for, and a "
            "contest reverses the principal. Approve line 4.")


@pytest.fixture
def night(tmp_path):
    if not NIGHT.exists():
        pytest.skip("the night 172 database is not on this machine")

    def at(trigger, drop):
        """The register at the call on `trigger`: the rulings of `drop`
        gone, the asked page open, and his later answers gone."""
        src = sqlite3.connect(f"file:{NIGHT.as_posix()}?mode=ro", uri=True)
        conn = sqlite3.connect(tmp_path / f"{trigger}.db")
        src.backup(conn)
        src.close()
        conn.row_factory = sqlite3.Row
        marks = ",".join("?" * len(drop))
        for (rid,) in conn.execute(
                f"SELECT id FROM rulings WHERE reply_id IN ({marks})",
                drop).fetchall():
            conn.execute("DELETE FROM ruled_refs WHERE ruling_id = ?", (rid,))
            conn.execute("DELETE FROM rulings WHERE id = ?", (rid,))
        seq, cause = conn.execute("SELECT seq, cause_id FROM messages WHERE id = ?",
                                  (trigger,)).fetchone()
        conn.execute("UPDATE messages SET status = 'open' WHERE id = ?", (cause,))
        conn.execute("DELETE FROM messages WHERE from_role = 'principal' "
                     "AND seq > ?", (seq,))
        conn.commit()
        return api.Ctx(conn=conn, role="liaison", session_id="sX",
                       trigger=trigger, writes=[], outbound=[])
    return at


def _rows(ctx):
    return {w[2]["ref"]: w[2] for w in ctx.writes if w[0] == "ruled_refs"}


def test_s271s_acts_call_lands_on_his_reply(night):
    """s271 call 1 on m127 with m129: the words sit in `acts` only."""
    ctx = night("m129", LATE[2:])
    api.rulings_rule(ctx, rulings={**R8, "9": A, "10": A, "11": "contest"},
                     acts={"11": {"verdict": "contest", "act": "remove",
                                  "target_kind": "row", "words": S271_SPAN}})
    row = _rows(ctx)["reading:m121"]
    assert (row["line"], row["verdict"], row["act"]) == (11, "contest", "remove")
    assert row["words"] == S271_SPAN


def test_s275s_acts_call_lands_on_his_reply(night):
    """s275 call 1 on m130 with m132: drops and a rewrite, no `words`."""
    ctx = night("m132", ["m132"])
    acts = {**{str(i): {"act": "drop", "target_kind": "row", "target": str(i),
                        "words": "Drop lines 9 to 15"} for i in range(9, 16)},
            "18": {"act": "rewrite", "target_kind": "row", "target": "18",
                   "words": "Correct line 18 to say that my answer asked to put "
                            "the removed code back and did not call line 4 "
                            "wrong"}}
    api.rulings_rule(ctx, rulings={**R18, "18": "revise"}, acts=acts)
    rows = _rows(ctx)
    assert rows["reading:m121"]["act"] == "rewrite"
    assert rows["challenge_constraints_sentinel"]["act"] == "drop"


def test_s258s_landed_call_is_refused_on_line_12s_act(night):
    """s258 call 8 on m120 with m121 landed r_m121. Line 12's act carries no
    words of its own, so it rested on the whole reply."""
    ctx = night("m121", LATE)
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={
            **R8, "4": "contest",
            "12": {"verdict": "contest", "act": "remove",
                   "target_kind": "source_line",
                   "target": "src/click/utils.py:12"}}, words=W121)
    assert str(e.value) == (
        "line 12: the act remove rests on '', and his words do not hold it. "
        "Copy the words of his reply that ask for the change, or leave the "
        "act out")


def test_s258s_call_without_the_act_is_refused_on_line_4(night):
    """m121 numbers line 12 only. "The other lines are fine." spares no
    criterion line it never numbers."""
    ctx = night("m121", LATE)
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={**R8, "4": "contest", "12": "contest"},
                         words=W121)
    assert str(e.value) == (
        "The words name line 12 and do not name line 4. A contest rests on "
        "the principal's words. Approve the lines the words do not name, or "
        "rule them as the words say.")


def test_words_the_seat_adds_to_his_reply_are_refused(night):
    """The F2 review of pass 2, finding 8: the seat's words with "Line 4 is
    wrong too." landed a contest of line 4 that m121 never makes. The
    naming door reads m121, so the contest has no words of his."""
    ctx = night("m121", LATE)
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={**R8, "4": "contest", "12": "contest"},
                         words=W121 + " Line 4 is wrong too.")
    assert str(e.value).startswith(
        "The words name line 12 and do not name line 4.")


def test_s258s_call_with_line_4_approved_lands(night):
    ctx = night("m121", LATE)
    api.rulings_rule(ctx, rulings={**R8, "12": "contest"}, words=W121)
    assert _rows(ctx)["reading:m118"]["verdict"] == "contest"


def test_s274s_reversal_on_line_4_stays_refused(night):
    ctx = night("m131", LATE[3:])
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={**R18, "4": "contest", "18": "contest"},
                         words=W131, acts=S274_ACTS)
    assert str(e.value) == REVERSAL


def test_s274s_call_with_no_words_meets_the_reversal(night):
    """s274 call 3 passed no `words`. The door reads m131, and m131 says
    that line 4 is fine."""
    ctx = night("m131", LATE[3:])
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={**R18, "4": "contest", "18": "contest"},
                         acts=S274_ACTS)
    assert str(e.value) == REVERSAL
