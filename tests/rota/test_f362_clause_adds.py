"""
Frame 362, dry run 6c wall 2, pass 1: each clause add on one line keeps
its words.

The Liaison s143 of dry run 6b keyed three clauses of m27 `add`. Code sends
each clause add to the one line whose menu holds add, and `menu_ruling` kept
one shape per ref. So each add overwrote the one before it, and the row of
line 1 held the last sentence alone (`plans/dry6c-wall2-correction-read-
2026-11-06.md`). The composition says that the wiring records his words
verbatim.
"""
from __future__ import annotations

from rota.roles import api

from .test_ruled_refs import _page, _seat, db  # noqa: F401

# m27 of dry run 6b, his reply to the guess page m26.
M27 = ("Line 2 is wrong. The fold is _foldline in "
       "src/icalendar/parser/string.py, and its tests are in "
       "src/icalendar/tests/test_icalendar.py. Do not touch parameter.py or "
       "property.py.")
# The call of s143 that landed, `turns.completion` seq 2, copied as is.
S143 = {"1": "approve", "2": "rewrite", "3": "approve", "4": "ok",
        "c2": "add The fold is _foldline in src/icalendar/parser/string.py",
        "c3": "add its tests are in src/icalendar/tests/test_icalendar.py.",
        "c4": "add Do not touch parameter.py or property.py.",
        "rest": "none"}
# The page of m26 by its row kinds: the request item, its guess of the
# files, a team note and a read-back line.
PAGE = ["calculate_tip", "guess:calculate_tip", "l_1", "reading:m5"]


def _rows(sb) -> dict:
    return {w[2]["ref"]: w[2] for w in sb.ctx.writes if w[0] == "ruled_refs"}


def test_three_clause_adds_on_one_line_keep_every_sentence_in_order(
        db):  # noqa: F811
    _page(db)
    menu = api.page_menus(db, PAGE, "")[1]
    assert [menu[n][0] for n in (1, 2, 3, 4)] == [
        "request", "touch", "other", "read-back"]
    assert [c["words"] for c in api.page_clauses(M27, 4, menu)][1:] == [
        "The fold is _foldline in src/icalendar/parser/string.py",
        "its tests are in src/icalendar/tests/test_icalendar.py.",
        "Do not touch parameter.py or property.py."]
    per_item, shapes = api.menu_ruling(db, S143, M27, PAGE, "", set(), {})
    assert (per_item["calculate_tip"], shapes["calculate_tip"]["act"]) == (
        "approve", "add")
    # The adds of adjacent clauses join with his own words between them, so
    # the row holds a run of his reply.
    assert shapes["calculate_tip"]["words"] == (
        "The fold is _foldline in src/icalendar/parser/string.py, and its "
        "tests are in src/icalendar/tests/test_icalendar.py. Do not touch "
        "parameter.py or property.py.")
    assert api._holds_span(M27, shapes["calculate_tip"]["words"])
    assert (per_item["guess:calculate_tip"],
            shapes["guess:calculate_tip"]["words"]) == ("contest",
                                                        "Line 2 is wrong.")
    assert shapes["l_1"]["words"] == M27


def test_a_single_clause_add_lands_as_before(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3. The page leaves out the tax.")
    sb.call("rulings.rule", rulings={
        "3": "drop", "c2": "add The page leaves out the tax.",
        "rest": "approve"})
    row = _rows(sb)["calculate_tip"]
    assert (row["verdict"], row["act"]) == ("approve", "add")
    assert row["words"] == "The page leaves out the tax."


def test_clause_adds_apart_in_his_reply_keep_each_clause_in_order(
        db):  # noqa: F811
    """A clause that is no add stands between two adds, so the row cannot
    hold one run of his reply. Each clause keeps its words, in his order.
    Dry run 5's m73 keyed four clause adds."""
    ask = _page(db)
    words = ("The page leaves out the tax. Drop line 3. The page leaves out "
             "the rounding. The page leaves out the split. The page leaves "
             "out the date.")
    sb, _ = _seat(db, ask, words=words)
    sb.call("rulings.rule", rulings={
        "3": "drop", "c1": "add The page leaves out the tax.",
        "c3": "add The page leaves out the rounding.",
        "c4": "add The page leaves out the split.",
        "c5": "add The page leaves out the date.", "rest": "approve"})
    rows = _rows(sb)
    assert rows["calculate_tip"]["words"] == (
        "The page leaves out the tax. The page leaves out the rounding. The "
        "page leaves out the split. The page leaves out the date.")
    assert rows["l_1"]["act"] == "drop"


def test_adjacent_clause_adds_through_the_door_keep_his_message(
        db):  # noqa: F811
    """The joined words are a run of whole clauses of his reply, so the
    row's `words_from` names the reply."""
    ask = _page(db)
    words = ("Drop line 3. The page leaves out the tax, and it leaves out "
             "the rounding.")
    sb, _ = _seat(db, ask, words=words)
    sb.call("rulings.rule", rulings={
        "3": "drop", "c2": "add The page leaves out the tax",
        "c3": "add it leaves out the rounding.", "rest": "approve"})
    row = _rows(sb)["calculate_tip"]
    assert row["words"] == ("The page leaves out the tax, and it leaves out "
                            "the rounding.")
    assert row["words_from"] == sb.ctx.trigger


def test_the_readers_of_the_row_read_every_clause_add(db):  # noqa: F811
    """`ruled_words` serves the start, criteria and slicing pushes and the
    removal door. It gives the joined row as one text. The read-back line
    reads the verdict and the act, so it says the same as before."""
    from rota.roles.principal import apply_rulings, reading_line, ruled_words

    from .test_ruled_refs import _commit

    ask = _page(db)
    words = ("Drop line 3. The page leaves out the tax, and it leaves out "
             "the rounding.")
    sb, reply = _seat(db, ask, words=words)
    sb.call("rulings.rule", rulings={
        "3": "drop", "c2": "add The page leaves out the tax",
        "c3": "add it leaves out the rounding.", "rest": "approve"})
    _commit(db, sb)
    apply_rulings(db)
    assert ruled_words(db, ["calculate_tip"], item="calculate_tip") == [
        "The page leaves out the tax, and it leaves out the rounding."]
    line = reading_line(db, f"reading:{reply}")
    assert '"The software calculates the tip." is approved: add;' in line
