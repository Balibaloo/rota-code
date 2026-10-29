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


def test_an_option_lands_its_row_with_the_clause_as_the_span(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    sb.call("rulings.rule", rulings={"1": "drop", "2": "approve"})
    rows = _rows(sb)
    row = rows["l_1"]
    assert (row["verdict"], row["act"], row["target_kind"]) == (
        "contest", "drop", "row")
    assert row["words"] == "Drop line 3, because nobody types the percentage."
    assert rows["s1"]["verdict"] == rows["calculate_tip"]["verdict"] == "approve"


def test_an_option_off_the_menu_is_refused_with_the_lines_menu(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    with pytest.raises(ValueError, match=r"clause 1: 'misread' is not an "
                       r"option of line 3. Line 3, kind other, takes "
                       r"approve; drop; rewrite; other <quote>"):
        sb.call("rulings.rule", rulings={"1": "misread", "2": "approve"})
    assert not [w for w in sb.ctx.writes if w[0] == "rulings"]


def test_the_rest_defaults_to_approve(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3.")
    sb.call("rulings.rule", rulings={"1": "drop"})
    rows = _rows(sb)
    assert rows["l_1"]["act"] == "drop"
    assert rows["s1"]["verdict"] == rows["calculate_tip"]["verdict"] == "approve"


def test_rest_none_leaves_a_line_unruled_and_is_refused(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3.")
    with pytest.raises(ValueError, match="lines 1, 2 have no ruling"):
        sb.call("rulings.rule", rulings={"1": "drop", "rest": "none"})


def test_the_lines_correction_moves_the_option(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Line 3 is fine. Please drop the first one.")
    # Clause 2 names no line, so its option needs lines.
    with pytest.raises(ValueError, match="clause 2 names no page line"):
        sb.call("rulings.rule", rulings={"1": "approve", "2": "drop"})
    sb, _ = _seat(db, ask, words="Line 3 is fine. Please drop the first one.")
    sb.call("rulings.rule", rulings={
        "1": "approve", "2": {"option": "drop", "lines": [1]}})
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
        db, {"1": "ok", "2": "slightly off", "3": "misread, drop",
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
    with pytest.raises(ValueError, match="one option per clause number"):
        sb.call("rulings.rule", rulings={
            "1": {"verdict": "contest", "act": "drop"}, "2": "approve"})
    with pytest.raises(ValueError, match="one option per clause number"):
        sb.call("rulings.rule", rulings={"1": "contest", "2": "approve",
                                         "3": "approve"})
    with pytest.raises(ValueError, match="one option per clause number"):
        sb.call("rulings.rule", rulings={"1": "drop"},
                acts={"1": {"act": "drop"}})
