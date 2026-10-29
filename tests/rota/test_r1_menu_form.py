"""
Frame 345, pass R1: a menu per line from the row kind, one choice per clause.

Roman ruled on 2026-10-29 10:29: "Yes do R". Code offers the clauses of his
reply and, per page line, the options that its row kind allows. The seat
chooses one option per clause, and code fills the row
(`plans/design-moment-seam-2026-10-29.md`, section R).
"""
from __future__ import annotations

import pytest

from rota.roles import api

from .test_ruled_refs import _page, _seat, db  # noqa: F401

TOUCH = "1. The change touches:\n   src/a.py\n   tests/test_a.py\n"
DROP = "Drop line 3, because nobody types the percentage. The rest is fine."
OTHER = ["approve", "drop", "rewrite", "other <quote>"]


def _rows(sb) -> dict:
    return {w[2]["ref"]: w[2] for w in sb.ctx.writes if w[0] == "ruled_refs"}


def test_each_row_kind_offers_its_menu(db):  # noqa: F811
    _page(db)
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('t1', 'calculate_tip', 'do it')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c_1', 't1', 'The tip shows two decimals.')")
    order = ["guess:calculate_tip", "c_1", "reading:m1", "l_1", "c_1"]
    menus, per_line = api.page_menus(db, order, TOUCH)
    assert per_line[1] == ("touch", ["approve", "exclude src/a.py",
                                     "exclude tests/test_a.py", "rewrite",
                                     "other <quote>"])
    assert per_line[2] == ("criterion", OTHER)
    assert per_line[3] == ("read-back", ["ok", "misread", "misread, drop",
                                         "slightly off", "rewrite",
                                         "other <quote>"])
    assert per_line[4] == ("other", OTHER)
    # One entry per kind and option list, with its lines.
    assert {"kind": "criterion", "lines": [2, 5], "options": OTHER} in menus
    assert len(menus) == 4


def test_the_request_line_offers_add(db):  # noqa: F811
    _page(db)
    assert api.line_menu(db, "calculate_tip", ["calculate_tip"], "") == (
        "request", ["approve", "add <quote>", "other <quote>"])


def test_the_clauses_carry_his_words_and_their_lines():
    got = api.page_clauses(DROP, 3)
    assert got == [
        {"words": "Drop line 3, because nobody types the percentage.",
         "lines": [3]},
        {"words": "The rest is fine.", "lines": [1, 2]}]
    # A clause that names a line and the rest is two clauses.
    assert api.page_clauses("please drop line 3, the rest is fine", 3) == [
        {"words": "please drop line 3, the rest is fine", "lines": [3]},
        {"words": "the rest is fine", "lines": [1, 2]}]
    # A clause that names no line is listed with no lines.
    got = api.page_clauses("Line 2 is wrong. Please keep it short.", 3)
    assert got == [{"words": "Line 2 is wrong.", "lines": [2]},
                   {"words": "Please keep it short.", "lines": []}]


def test_a_clause_key_lands_its_rows_with_the_clause_as_the_span(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    sb.call("rulings.rule", rulings={"c1": "drop", "c2": "approve"})
    rows = _rows(sb)
    row = rows["l_1"]
    assert (row["verdict"], row["act"], row["target_kind"]) == (
        "contest", "drop", "row")
    assert row["words"] == "Drop line 3, because nobody types the percentage."
    assert rows["s1"]["verdict"] == rows["calculate_tip"]["verdict"] == "approve"


def test_a_line_key_lands_its_line_with_its_clauses_words(db):  # noqa: F811
    """Pass R1b: 30 of 101 refusals of R1 keyed the call by line."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    sb.call("rulings.rule", rulings={"3": "drop", "rest": "approve"})
    rows = _rows(sb)
    assert (rows["l_1"]["verdict"], rows["l_1"]["act"]) == ("contest", "drop")
    assert rows["l_1"]["words"] == (
        "Drop line 3, because nobody types the percentage.")
    assert rows["s1"]["verdict"] == "approve"


def test_a_line_key_wins_over_its_clause_key(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Lines 1 and 3 are wrong, so drop them.")
    sb.call("rulings.rule", rulings={"c1": "drop", "1": "approve"})
    rows = _rows(sb)
    assert rows["s1"]["verdict"] == "approve"
    assert rows["l_1"]["act"] == "drop"


def test_a_line_no_clause_names_takes_approve_and_a_change_is_refused_once(
        db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3.")
    with pytest.raises(ValueError, match="no clause of his names line 1"):
        sb.call("rulings.rule", rulings={"3": "drop", "1": "drop"})
    # The repeat rests the change on his whole reply.
    sb.call("rulings.rule", rulings={"3": "drop", "1": "drop"})
    rows = _rows(sb)
    assert (rows["s1"]["act"], rows["s1"]["words"]) == ("drop", "Drop line 3.")
    # approve needs no words.
    sb, _ = _seat(db, ask, words="Drop line 3.")
    sb.call("rulings.rule", rulings={"3": "drop", "1": "approve"})
    assert _rows(sb)["s1"]["verdict"] == "approve"


def test_a_words_field_on_an_option_is_not_read(db):  # noqa: F811
    """The menu form runs before `_words_outside`, and the clause gives the
    words (pass R1b)."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    sb.call("rulings.rule", words="words he never said",
            rulings={"3": {"option": "drop", "words": "not his words"},
                     "rest": "approve"})
    rows = _rows(sb)
    assert rows["l_1"]["words"] == (
        "Drop line 3, because nobody types the percentage.")
    ruling = [w[2] for w in sb.ctx.writes if w[0] == "rulings"][0]
    assert ruling["words"] == DROP


def test_an_option_off_the_menu_is_refused_with_the_lines_menu(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    with pytest.raises(ValueError, match=r"clause c1: 'misread' is not an "
                       r"option of line 3. Line 3, kind other, takes "
                       r"approve; drop; rewrite; other <quote>"):
        sb.call("rulings.rule", rulings={"c1": "misread", "c2": "approve"})
    assert not [w for w in sb.ctx.writes if w[0] == "rulings"]


def test_the_rest_defaults_to_approve(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3.")
    sb.call("rulings.rule", rulings={"c1": "drop"})
    rows = _rows(sb)
    assert rows["l_1"]["act"] == "drop"
    assert rows["s1"]["verdict"] == rows["calculate_tip"]["verdict"] == "approve"


def test_rest_none_leaves_a_line_unruled_and_is_refused(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3.")
    with pytest.raises(ValueError, match="lines 1, 2 have no ruling"):
        sb.call("rulings.rule", rulings={"c1": "drop", "rest": "none"})


def test_a_line_his_words_name_needs_an_option(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    with pytest.raises(ValueError, match=r"line 3 \(clause c1\)"):
        sb.call("rulings.rule", rulings={"c2": "approve"})


def test_the_lines_correction_moves_the_option(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Line 3 is fine. Please drop the first one.")
    # Clause c2 names no line, so its option needs lines.
    with pytest.raises(ValueError, match="clause c2 names no page line"):
        sb.call("rulings.rule", rulings={"c1": "approve", "c2": "drop"})
    sb, _ = _seat(db, ask, words="Line 3 is fine. Please drop the first one.")
    sb.call("rulings.rule", rulings={
        "c1": "approve", "c2": {"option": "drop", "lines": [1]}})
    rows = _rows(sb)
    assert (rows["s1"]["verdict"], rows["s1"]["act"]) == ("contest", "drop")
    assert rows["s1"]["words"] == "Please drop the first one."
    assert rows["l_1"]["verdict"] == "approve"


def test_the_read_back_options_land_their_rows(db):  # noqa: F811
    his = ("Line 1 reads me right. Line 2 is slightly off. Line 3 is a "
           "misread, so drop it. Line 4 misreads me. Line 5 is fine.")
    order = ["reading:m1", "reading:m2", "reading:m3", "reading:m4", "l_9",
             "reading:m6"]
    per_item, shapes = api.menu_ruling(
        db, {"1": "ok", "2": "slightly off", "c3": "misread, drop",
             "4": "misread", "5": "ok"}, his, order, "", set(), {})
    assert per_item["reading:m1"] == "approve"
    assert per_item["reading:m2"] == "revise"
    assert (per_item["reading:m3"], shapes["reading:m3"]["act"],
            shapes["reading:m3"]["target_kind"]) == ("contest", "drop", "row")
    assert per_item["reading:m4"] == "contest"
    assert "act" not in shapes["reading:m4"]
    # ok on another line is approve.
    assert per_item["l_9"] == "approve"
    # The rest never rules a read-back line.
    assert "reading:m6" not in per_item


def test_the_old_forms_are_refused_with_the_menu_form_named(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    with pytest.raises(ValueError, match="one option from landing.menus"):
        sb.call("rulings.rule", rulings={
            "1": {"verdict": "contest", "act": "drop"}, "2": "approve"})
    with pytest.raises(ValueError, match="'contest' is not an option"):
        sb.call("rulings.rule", rulings={"3": "contest", "rest": "approve"})
    with pytest.raises(ValueError, match="one option from landing.menus"):
        sb.call("rulings.rule", rulings={"3": "drop"},
                acts={"3": {"act": "drop"}})

