"""Frame 345, pass 2: the seat gets the match and gives one word per line.

The seam read of 2026-10-29 (`plans/seam-general-solution-2026-10-29.md`,
option (d)) found that the seat left the act out on 241 line rulings and
looped on the span door. Code now binds each page line to the words of his
that name it, and the landing block shows that match beside each line. The
seat gives each line one word. `WORD_ACTS` turns the word into the verdict
and the act, and code copies the matched words into the act. The match says
which words name a line, never what they rule.
"""
from __future__ import annotations

import pytest

from rota.core.runner import resolve_inbound
from rota.core.scheduler import Wake
from rota.roles import api

from .test_ruled_refs import _commit, _page, _seat, db  # noqa: F401


def _verbatim(his: str, got: dict) -> None:
    """Every matched run is a run of whole clauses of his reply."""
    for words in got.values():
        if words is not None:
            assert words in his
            assert api._holds_clauses(his, words)


def test_a_numbered_clause_and_its_tail_name_the_line():
    his = "Line 3 is wrong, so drop it. The rest is fine."
    got = api.line_words(his, 4)
    assert got[3] == "Line 3 is wrong, so drop it."
    assert got[1] == got[2] == got[4] == "The rest is fine."
    _verbatim(his, got)


def test_a_range_names_each_line_it_holds():
    his = "Lines 2 to 4 are fine. Drop line 5."
    got = api.line_words(his, 5)
    assert got[2] == got[3] == got[4] == "Lines 2 to 4 are fine."
    assert got[5] == "Drop line 5."
    assert got[1] is None
    _verbatim(his, got)


def test_an_ordinal_names_its_line():
    his = "The second line is wrong, please drop it."
    got = api.line_words(his, 3)
    assert got[2] == his
    assert got[1] is None and got[3] is None


def test_the_other_lines_name_every_line_no_clause_names():
    his = "Removing lines 7 and 8 is right, and the other lines are approved."
    got = api.line_words(his, 9)
    assert got[7] == got[8] == "Removing lines 7 and 8 is right"
    assert got[1] == got[9] == "the other lines are approved."
    _verbatim(his, got)


def test_a_clause_can_name_a_line_and_the_rest():
    """Night 170's m7 names line 1 and the rest in one clause."""
    his = ("Lines 3 to 4 are wrong, so please drop them. Line 1 and the rest "
           "of the word notes are fine with me.")
    got = api.line_words(his, 5)
    assert got[1] == got[2] == got[5] == (
        "Line 1 and the rest of the word notes are fine with me.")
    assert got[3] == "Lines 3 to 4 are wrong, so please drop them."


def test_every_line_names_them_all():
    his = "Ok, every line matches what I asked for."
    assert set(api.line_words(his, 3).values()) == {his}


def test_a_reply_that_approves_the_page_names_each_line_with_the_whole_reply():
    assert api.line_words("Ok, I approve.", 2) == {1: "Ok, I approve.",
                                                   2: "Ok, I approve."}
    assert api.line_words("yes", 1) == {1: "yes"}


def test_a_reply_that_names_no_line_names_each_line_with_the_whole_reply():
    his = "Drop both of those examples, because I asked for only one."
    assert api.line_words(his, 2) == {1: his, 2: his}


def test_a_line_that_no_words_name_gets_none():
    got = api.line_words("Line 2 is wrong.", 3)
    assert got == {1: None, 2: "Line 2 is wrong.", 3: None}


def test_his_report_of_an_earlier_answer_names_no_line_of_this_page():
    his = "Line 2 is wrong, because I approved lines 1 and 4, not one."
    got = api.line_words(his, 4)
    assert got[1] is None and got[4] is None
    assert got[2] == his


def test_the_cue_clauses_keep_their_cuts():
    """`_cue_clauses` now reads the spans of `_clause_spans`. Its clauses
    are the same strings as before."""
    words = "Line 3 is wrong: drop it, but keep line 4. Fine, so go ahead."
    assert [c for c, _, _ in api._cue_clauses(words)] == [
        "Line 3 is wrong", "drop it", "keep line 4.", "Fine", "go ahead."]


def test_the_word_table_gives_a_verdict_and_an_act():
    assert api.WORD_ACTS["drop"] == ("contest", "drop")
    assert api.WORD_ACTS["remove"] == ("contest", "remove")
    assert api.WORD_ACTS["rewrite"] == ("contest", "rewrite")
    assert api.WORD_ACTS["exclude"] == ("contest", "exclude")
    assert api.WORD_ACTS["keep"] == ("revise", "keep")
    assert api.WORD_ACTS["add"] == ("approve", "add")


def test_the_word_shape_fills_words_and_the_target_kind(db):  # noqa: F811
    page = "1. The change touches:\n   src/click/utils.py\n   tests/test_utils.py\n"
    for act, kind in (("drop", "row"), ("rewrite", "row"), ("keep", "check"),
                      ("remove", "row"), ("add", None)):
        shape = api._word_shape(db, "c_1", {"act": act}, "Line 1 is wrong",
                                ["c_1"], page)
        assert shape.get("target_kind") == kind
        assert shape["words"] == "Line 1 is wrong"
    shape = api._word_shape(db, "c_1", {"act": "exclude"},
                            "drop the utils file from line 1", ["c_1"], page)
    assert shape == {"act": "exclude", "target_kind": "path",
                     "words": "drop the utils file from line 1",
                     "target": "src/click/utils.py"}
    # A remove on a code line takes a source line.
    shape = api._word_shape(db, "guess:calc", {"act": "remove"}, "x",
                            ["guess:calc"], page)
    assert shape["target_kind"] == "source_line"


DROP = "Drop line 3, because nobody types the percentage. The rest is fine."


def test_one_word_lands_the_act_with_his_words(db):  # noqa: F811
    """`"3": "drop"` lands a contest with the act drop on the row, and its
    words are his clause that names line 3."""
    ask = _page(db)
    sb, reply = _seat(db, ask, words=DROP)
    sb.call("rulings.rule", rulings={"1": "approve", "2": "approve", "3": "drop"})
    rows = {w[2]["ref"]: w[2] for w in sb.ctx.writes if w[0] == "ruled_refs"}
    row = rows["l_1"]
    assert (row["verdict"], row["act"], row["target_kind"]) == (
        "contest", "drop", "row")
    assert row["words"] == "Drop line 3, because nobody types the percentage."


def test_the_landing_block_shows_his_words_beside_each_line(db):  # noqa: F811
    ask = _page(db)
    _sb, reply = _seat(db, ask, words=DROP)
    wake = Wake(role="liaison", kind="message", message_id=reply,
                detail="converse")
    landing = resolve_inbound(db, wake)["landing"]
    assert landing["his_words"] == {
        "1": "The rest is fine.", "2": "The rest is fine.",
        "3": "Drop line 3, because nobody types the percentage."}


def test_the_flat_acts_map_is_refused_with_the_one_word_form(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    with pytest.raises(ValueError) as e:
        sb.call("rulings.rule", rulings={"1": "approve", "2": "approve",
                                         "3": "contest"},
                acts={"3": {"act": "drop", "words": "Drop line 3"}})
    assert str(e.value).endswith(
        "rulings.rule takes no acts: give each line one word in rulings, "
        "such as {\"5\": \"drop\"}.")
    assert not sb.ctx.writes
