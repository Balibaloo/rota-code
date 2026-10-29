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


def _folded(rulings: dict, acts: dict) -> dict:
    """The object form of a night's call that kept its act in the flat
    `acts` map. Frame 345's pass 2 refuses that map, and the object form
    writes the same rows (the seam design, 2.1)."""
    return {**rulings, **{k: {"verdict": rulings[k], **v}
                          for k, v in acts.items()}}


@pytest.mark.skip(reason="frame 345 R2: word form, re-pin on the menu form")
def test_s271s_call_lands_on_his_reply(night):
    """s271 call 1 on m127 with m129: the words sit in the act only."""
    ctx = night("m129", LATE[2:])
    api.rulings_rule(ctx, rulings=_folded(
        {**R8, "9": A, "10": A, "11": "contest"},
        {"11": {"act": "remove", "target_kind": "row", "words": S271_SPAN}}))
    row = _rows(ctx)["reading:m121"]
    assert (row["line"], row["verdict"], row["act"]) == (11, "contest", "remove")
    assert row["words"] == S271_SPAN


@pytest.mark.skip(reason="frame 345 R2: word form, re-pin on the menu form")
def test_s275s_call_lands_on_his_reply(night):
    """s275 call 1 on m130 with m132: drops and a rewrite, no `words`."""
    ctx = night("m132", ["m132"])
    acts = {**{str(i): {"act": "drop", "target_kind": "row", "target": str(i),
                        "words": "Drop lines 9 to 15"} for i in range(9, 16)},
            "18": {"act": "rewrite", "target_kind": "row", "target": "18",
                   "words": "Correct line 18 to say that my answer asked to put "
                            "the removed code back and did not call line 4 "
                            "wrong"}}
    api.rulings_rule(ctx, rulings=_folded({**R18, "18": "revise"}, acts))
    rows = _rows(ctx)
    assert rows["reading:m121"]["act"] == "rewrite"
    assert rows["challenge_constraints_sentinel"]["act"] == "drop"


# The refusal of `words` that are not a part of his reply (F2 passes 2f and
# 2g). It quotes the sentence that failed and his nearest sentence.
NOT_HIS = ("words must be his own words, and his reply does not hold 'Line 4 "
           "is wrong too.', and his nearest sentence is 'Line 12 is wrong, "
           "because my last answer was not empty: I said the example shows "
           "both the input path and the short output, and the removed code "
           "must go back.'")
# Night 172's m129, word for word from the night's `messages`.
W129 = ("Fix the change instead of giving up by putting back the two removed "
        "lines of code, because only the docstring changes and the code stays "
        "the same. Line 11 is wrong: my answer asked for that fix and did not "
        "call line 4 wrong, so keep line 4 as it is. Lines 9 and 10 are read "
        "right, and all the other lines are fine.")


@pytest.mark.skip(reason="frame 345 R2: word form, re-pin on the menu form")
def test_s271s_call_with_its_nested_words_as_words_lands(night):
    """s271's span sat in the act only. It is m129's first sentence, so the
    same call with that span as `words` is a part of his reply and lands."""
    ctx = night("m129", LATE[2:])
    api.rulings_rule(ctx, rulings=_folded(
        {**R8, "9": A, "10": A, "11": "contest"},
        {"11": {"act": "remove", "target_kind": "row", "words": S271_SPAN}}),
        words=S271_SPAN)
    row = _rows(ctx)["reading:m121"]
    assert (row["line"], row["verdict"], row["act"]) == (11, "contest", "remove")
    assert row["words"] == S271_SPAN


@pytest.mark.skip(reason="frame 345 R2: word form, re-pin on the menu form")
def test_a_line_objects_words_from_his_reply_land_on_the_row(night):
    ctx = night("m129", LATE[2:])
    api.rulings_rule(ctx, rulings={
        **R8, "9": A, "10": A,
        "11": {"verdict": "contest", "words": "Line 11 is wrong"}})
    assert _rows(ctx)["reading:m121"]["words"] == "Line 11 is wrong"


# F2 pass 2g, findings 2 and 3: the words match at clause edges, not at
# characters. One case per shape, on m129.
@pytest.mark.parametrize("words", [
    "No.",                                  # a word inside his sentence
    "I.",                                   # letters inside his words
    "call line 4 wrong.",                   # his "not" cut off
    "ne 4 wr.",                             # letters across his words
    "Put back the two removed lines.",      # a paraphrase
])
def test_a_cut_of_his_clause_is_refused(words):
    assert api._words_outside(words, W129) is not None


@pytest.mark.parametrize("words", [
    "did not call line 4 wrong",                    # a clause after "and"
    "Line 11 is wrong",                             # his full stop dropped
    "the code stays the same Line 11 is wrong",     # his stop between dropped
    "the code stays the same, Line 11 is wrong.",   # a comma for his stop
    "Line 11 is wrong,",                            # a comma for his colon
    "Lines 9 and 10 are read right;",               # a semicolon for his comma
    '"keep line 4 as it is"',                       # the seat adds quotes
])
def test_his_clauses_with_other_marks_land(words):
    assert api._words_outside(words, W129) is None


def test_a_curly_apostrophe_for_his_straight_one_lands():
    assert api._words_outside("I don’t understand line 11.",
                              "I don't understand line 11.") is None


def test_the_refusal_quotes_the_failed_sentence_and_his_nearest():
    """Finding 4: s214 copied his first sentence and cut his second. The
    refusal quotes the cut sentence, not his first."""
    his = ("Please keep the change. Only the docstring changes and the code "
           "stays the same.")
    assert api._words_outside(
        "Please keep the change. Only the doc, the code stays the same.",
        his) == (
        "words must be his own words, and his reply does not hold 'Only the "
        "doc, the code stays the same.', and his nearest sentence is 'Only the "
        "docstring changes and the code stays the same.'")


@pytest.mark.skip(reason="frame 345 R2: word form, re-pin on the menu form")
def test_s258s_call_with_line_4_approved_lands(night):
    ctx = night("m121", LATE)
    api.rulings_rule(ctx, rulings={**R8, "12": "contest"}, words=W121)
    assert _rows(ctx)["reading:m118"]["verdict"] == "contest"
