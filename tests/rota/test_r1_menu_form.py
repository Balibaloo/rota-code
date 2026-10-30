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


def test_a_clause_key_on_a_clause_with_lines_rules_each_of_its_lines(
        db):  # noqa: F811
    """Pass R3b: one option per clause (design R), checked against the menu
    of each line that the clause names."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    sb.call("rulings.rule", rulings={"c1": "drop", "rest": "approve"})
    rows = _rows(sb)
    assert (rows["l_1"]["verdict"], rows["l_1"]["act"]) == ("contest", "drop")
    assert rows["l_1"]["words"] == "Drop line 3, because nobody types the " \
                                   "percentage."
    assert rows["s1"]["verdict"] == "approve"


def test_a_clause_key_and_a_line_key_that_agree_land_once(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    sb.call("rulings.rule", rulings={"c1": "drop", "3": "drop",
                                     "rest": "approve"})
    assert _rows(sb)["l_1"]["act"] == "drop"


def test_two_keys_that_land_one_read_back_row_agree(db):  # noqa: F811
    """Review p12, low 1: a clause drop on a read-back line lands the row
    of the line key "misread, drop"."""
    his = "Line 1 is a misread, so drop it."
    per_item, shapes = api.menu_ruling(
        db, {"c1": "drop", "1": "misread, drop", "rest": "approve"}, his,
        ["reading:m1"], "", set(), {})
    assert (per_item["reading:m1"], shapes["reading:m1"]["act"]) == (
        "contest", "drop")


def test_a_line_key_on_the_add_line_keeps_or_conflicts_with_the_add(
        db):  # noqa: F811
    """Review p12, low 2: an option that lands a row on the add line is
    refused once, then wins. An approve there lets the add ride, as
    test_a_clause_key_add_lands_on_the_one_add_line shows."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3. Line 2 should say per person. "
                  "The page leaves out the tax.")
    call = {"3": "drop", "2": "other per person",
            "c3": "add The page leaves out the tax.", "rest": "approve"}
    with pytest.raises(ValueError, match=r"line 2: two keys give line 2 two "
                       r"options. Clause c3 gives add, and the line key \"2\" "
                       r"gives other"):
        sb.call("rulings.rule", rulings=call)
    sb.call("rulings.rule", rulings=call)
    row = _rows(sb)["calculate_tip"]
    assert (row["verdict"], row.get("act")) == ("contest", None)


def test_a_clause_key_and_a_line_key_that_differ_are_refused_once(
        db):  # noqa: F811
    """Pass R3c: the refusal fires once per line, whatever the next call
    holds, and then the line key wins."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    with pytest.raises(ValueError, match=r"line 3: two keys give line 3 two "
                       r"options. Clause c1 gives drop, and the line key "
                       r"\"3\" gives rewrite"):
        sb.call("rulings.rule", rulings={"c1": "drop", "3": "rewrite",
                                         "rest": "approve"})
    sb.call("rulings.rule", rulings={"c1": "rewrite", "3": "drop",
                                     "rest": "approve"})
    assert _rows(sb)["l_1"]["act"] == "drop"


@pytest.mark.parametrize("option", ["none", "held"])
def test_a_clause_key_that_lands_nothing_gives_way_to_a_line_key(
        db, option):  # noqa: F811
    """Pass R3c: R3b refused none and held beside a line key 75 times in
    its top five refusals."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    sb.call("rulings.rule", rulings={"c1": option, "3": "drop",
                                     "rest": "approve"})
    assert _rows(sb)["l_1"]["act"] == "drop"


def test_a_clause_that_names_a_page_line_offers_no_add(db):  # noqa: F811
    """Pass R3b: his words about a line on the page cannot ask for something
    the page leaves out, so the binder's miss offers none only."""
    _page(db)
    his = "Drop line 3. Please finish this change with line 2 instead."
    menu = api.page_menus(db, ["s1", "calculate_tip", "l_1"], "")[1]
    got = api.page_clauses(his, 3, menu)
    assert got[1] == {"words": "Please finish this change with line 2 "
                      "instead.", "lines": [], "options": ["none"]}


QUESTION = "Line 3 is fine. Does each person pay an equal share?"


def test_a_question_clause_takes_ask_alone(db):  # noqa: F811
    """Pass R3d: the question mark, read as a character, gives the clause
    `ask` and no other option, whatever lines it names."""
    _page(db)
    menu = api.page_menus(db, ["s1", "calculate_tip", "l_1"], "")[1]
    got = api.page_clauses(QUESTION, 3, menu)
    assert got[1] == {"words": "Does each person pay an equal share?",
                      "lines": [], "options": ["ask"]}
    assert "options" not in got[0]
    named = api.page_clauses("Is line 2 right?", 3, menu)
    assert [c["options"] for c in named] == [["ask"]]
    # The L1 case's form: a question, then a statement, in one clause.
    one = api.page_clauses("Does it split by person? I mean equally.", 3, menu)
    assert [c["options"] for c in one] == [["ask"]]


def test_other_on_his_question_is_refused_once(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words=QUESTION)
    call = {"3": "approve",
            "1": "other \"Does each person pay an equal share?\"",
            "rest": "approve"}
    with pytest.raises(ValueError, match=r"clause c2 is his question, so his "
                       r"question is answered with rulings\.rule\(ask="):
        sb.call("rulings.rule", rulings=call)
    sb.call("rulings.rule", rulings=call)
    assert _rows(sb)


def test_a_question_and_an_approval_take_ask(db):  # noqa: F811
    """A clause key on his question is refused, and the ask goes out."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words=QUESTION)
    with pytest.raises(ValueError, match=r"clause c2 is his question"):
        sb.call("rulings.rule", rulings={"3": "approve", "c2": "none",
                                         "rest": "approve"})
    sb.call("rulings.rule", ask="Should each person pay an equal share?")
    assert not _rows(sb)


def test_a_clause_key_held_lands_nothing(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3. Only the docstring changes.")
    sb.call("rulings.rule", rulings={"3": "drop", "c2": "held",
                                     "rest": "approve"})
    rows = _rows(sb)
    assert rows["calculate_tip"]["verdict"] == "approve"
    assert rows["calculate_tip"].get("act") is None
    assert rows["l_1"]["act"] == "drop"


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


def test_a_line_no_clause_names_takes_approve_and_a_change_is_refused(
        db):  # noqa: F811
    """Review p9c: the same call twice in one session lands nothing on
    line 1, because the quote lies in a clause that names line 3."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3.")
    for call in ({"3": "drop", "1": "drop"},
                 {"1": "other \"Drop line 3.\"", "3": "drop"}):
        for _ in (1, 2):
            with pytest.raises(ValueError,
                               match="no clause of his names line 1"):
                sb.call("rulings.rule", rulings=call)
    assert not [w for w in sb.ctx.writes if w[0] == "ruled_refs"]
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
    with pytest.raises(ValueError, match=r"line 3: 'misread' is not an "
                       r"option of line 3. Line 3, kind other, takes "
                       r"approve; drop; rewrite; other <quote>"):
        sb.call("rulings.rule", rulings={"3": "misread", "rest": "approve"})
    assert not [w for w in sb.ctx.writes if w[0] == "rulings"]


def test_the_rest_defaults_to_approve(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3.")
    sb.call("rulings.rule", rulings={"3": "drop"})
    rows = _rows(sb)
    assert rows["l_1"]["act"] == "drop"
    assert rows["s1"]["verdict"] == rows["calculate_tip"]["verdict"] == "approve"


def test_rest_none_leaves_a_line_unruled_and_is_refused(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3.")
    with pytest.raises(ValueError, match="lines 1, 2 have no ruling"):
        sb.call("rulings.rule", rulings={"3": "drop", "rest": "none"})


def test_a_line_his_words_name_needs_an_option(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    # Review p9, finding 1: rest never rules a line that his clause names.
    with pytest.raises(ValueError, match="line 3: his words name the line"):
        sb.call("rulings.rule", rulings={"rest": "approve"})
    with pytest.raises(ValueError, match="line 3: his words name the line"):
        sb.call("rulings.rule", rulings={"1": "approve", "rest": "approve"})


def test_the_rest_gives_the_words_of_the_clause_that_names_the_line(
        db):  # noqa: F811
    """Review p9, finding 2: both keys give an approved line the same
    words."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words=DROP)
    sb.call("rulings.rule", rulings={"3": "drop", "rest": "approve"})
    assert _rows(sb)["s1"]["words"] == "The rest is fine."


def test_a_quote_from_a_clause_with_no_lines_on_a_line_key_is_refused_once(
        db):  # noqa: F811
    """Pass R3 narrows the quote branch of review p9b-2: the clause key is
    the place of the quote. The refusal names it and fires once."""
    ask = _page(db)
    words = "Drop line 3. The page leaves out the tax."
    call = {"3": "drop", "2": "add The page leaves out the tax.",
            "rest": "approve"}
    sb, _ = _seat(db, ask, words=words)
    with pytest.raises(ValueError, match=r"line 2: the quote lies in clause "
                       r"c2, and c2 names no page line. Key that clause "
                       r"instead: \"c2\": \"none\", or \"c2\": \"add <quote>\""):
        sb.call("rulings.rule", rulings=call)
    sb.call("rulings.rule", rulings=call)
    row = _rows(sb)["calculate_tip"]
    assert (row["verdict"], row["act"]) == ("approve", "add")
    assert row["words"] == "The page leaves out the tax."


def test_the_clauses_with_no_lines_carry_their_options(db):  # noqa: F811
    """Pass R3: a clause with no lines offers add only when one page line
    holds add, because code finds the line."""
    _page(db)
    his = "Drop line 3. The page leaves out the tax."
    one = api.page_menus(db, ["s1", "calculate_tip", "l_1"], "")[1]
    assert api.page_clauses(his, 3, one) == [
        {"words": "Drop line 3.", "lines": [3]},
        {"words": "The page leaves out the tax.", "lines": [],
         "options": ["none", "held", "add <quote>"]}]
    # No line holds add, or two lines do: the clause takes none.
    db.execute("UPDATE items SET is_description = 1 WHERE id = 'how_it_works'")
    for order in (["s1", "l_1", "l_1"],
                  ["how_it_works", "calculate_tip", "l_1"]):
        menu = api.page_menus(db, order, "")[1]
        assert api.page_clauses(his, 3, menu)[1]["options"] == ["none"]
    # Without the menu the payload is as before.
    assert "options" not in api.page_clauses(his, 3)[1]


def test_a_clause_key_add_lands_on_the_one_add_line(db):  # noqa: F811
    ask = _page(db)
    words = "Drop line 3. The page leaves out the tax."
    sb, _ = _seat(db, ask, words=words)
    sb.call("rulings.rule", rulings={
        "3": "drop", "2": "approve", "c2": "add The page leaves out the tax.",
        "rest": "approve"})
    rows = _rows(sb)
    # The same row as the line key "2": "add <quote>": a line key approve
    # on the add line keeps the add.
    row = rows["calculate_tip"]
    assert (row["verdict"], row["act"]) == ("approve", "add")
    assert row["words"] == "The page leaves out the tax."
    assert (rows["l_1"]["verdict"], rows["l_1"]["act"]) == ("contest", "drop")
    assert rows["s1"]["verdict"] == "approve"


def test_a_clause_key_none_lands_nothing(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3. Thanks.")
    sb.call("rulings.rule", rulings={"3": "drop", "c2": "none",
                                     "rest": "approve"})
    rows = _rows(sb)
    assert "act" not in rows["calculate_tip"] or rows["calculate_tip"].get(
        "act") is None
    assert rows["calculate_tip"]["verdict"] == "approve"
    assert rows["l_1"]["act"] == "drop"


def test_a_clause_key_approve_is_refused_once_and_then_lands_nothing(
        db):  # noqa: F811
    """Before pass R3 an approve of a clause with no lines landed nothing."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3. Thanks.")
    call = {"3": "drop", "c2": "approve", "rest": "approve"}
    with pytest.raises(ValueError, match=r"clause c2 names no page line, so it "
                       r"takes none or held or add <quote>, not 'approve'"):
        sb.call("rulings.rule", rulings=call)
    sb.call("rulings.rule", rulings=call)
    assert _rows(sb)["calculate_tip"].get("act") is None


def test_a_clause_with_no_lines_and_no_key_is_refused_once(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3. Thanks.")
    call = {"3": "drop", "rest": "approve"}
    with pytest.raises(ValueError, match=r"c2: the clause names no page line, "
                       r"and the call gives it no key. Key each such clause "
                       r"by its clause key: \"c2\": \"none\", or \"c2\": "
                       r"\"add <quote>\""):
        sb.call("rulings.rule", rulings=call)
    sb.call("rulings.rule", rulings=call)
    assert _rows(sb)["l_1"]["act"] == "drop"


def test_a_clause_key_add_with_two_add_lines_is_refused(db):  # noqa: F811
    ask = _page(db, refs=("calculate_tip", "how_it_works", "l_1"))
    db.execute("UPDATE items SET is_description = 1 WHERE id = 'how_it_works'")
    sb, _ = _seat(db, ask, words="Drop line 3. The page leaves out the tax.")
    order = api.page_menus(db, ["calculate_tip", "how_it_works", "l_1"], "")[1]
    assert len([n for n, (_, o) in order.items() if "add <quote>" in o]) == 2
    with pytest.raises(ValueError, match=r"clause c2 names no page line, so it "
                       r"takes none, not 'add The page leaves out the tax.'. "
                       r"Lines \d, \d take add <quote>"):
        sb.call("rulings.rule", rulings={
            "3": "drop", "c2": "add The page leaves out the tax.",
            "rest": "approve"})
    # The clause takes none alone, so no key for it is refused, and a line
    # key carries the quote with no refusal.
    sb.call("rulings.rule", rulings={
        "3": "drop", "1": "add The page leaves out the tax.",
        "rest": "approve"})
    assert any(r["act"] == "add" for r in _rows(sb).values())


def test_an_item_outside_the_request_offers_add(db):  # noqa: F811
    """Review p9, finding 3: the description line `how_it_works`."""
    _page(db)
    db.execute("UPDATE items SET is_description = 1 WHERE id = 'how_it_works'")
    kind, options = api.line_menu(db, "how_it_works", ["how_it_works"], "")
    assert kind == "other"
    assert options == ["approve", "add <quote>", "drop", "rewrite",
                       "other <quote>"]


def test_the_lines_correction_moves_the_option(db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Line 3 is fine. Please drop the first one.")
    # Clause c2 names no line, so it takes its clause options alone.
    with pytest.raises(ValueError, match=r"clause c2 names no page line, so "
                       r"it takes none or held or add <quote>, not 'drop'"):
        sb.call("rulings.rule", rulings={"3": "approve", "c2": "drop"})
    sb, _ = _seat(db, ask, words="Line 3 is fine. Please drop the first one.")
    sb.call("rulings.rule", rulings={
        "3": "approve", "c2": {"option": "drop", "lines": [1]}})
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
    with pytest.raises(ValueError, match="one option from landing.menus"):
        sb.call("rulings.rule", rulings={
            "1": {"verdict": "contest", "act": "drop"}, "2": "approve"})
    with pytest.raises(ValueError, match="'contest' is not an option"):
        sb.call("rulings.rule", rulings={"3": "contest", "rest": "approve"})
    with pytest.raises(ValueError, match="one option from landing.menus"):
        sb.call("rulings.rule", rulings={"3": "drop"},
                acts={"3": {"act": "drop"}})


def test_a_line_key_approve_on_an_unnamed_line_lands_with_rest_none(
        db):  # noqa: F811
    """Review p9b-1: the seat keyed every line approve and sent rest none,
    and the skipped lines met the "no ruling" door 27 times in R1c."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words="Drop line 3.")
    sb.call("rulings.rule", rulings={"1": "approve", "2": "ok", "3": "drop",
                                     "rest": "none"})
    rows = _rows(sb)
    assert rows["s1"]["verdict"] == rows["calculate_tip"]["verdict"] == "approve"
    assert rows["s1"]["words"] == "Drop line 3."


def test_a_quote_that_names_another_line_carries_no_change(db):  # noqa: F811
    """Review p9b-2: the quote must lie in a clause that names no line. Pass
    R3: that clause's key is the place of the quote."""
    ask = _page(db)
    words = "Drop line 3 and its tax. The page leaves out the tip."
    sb, _ = _seat(db, ask, words=words)
    for _ in (1, 2):
        with pytest.raises(ValueError, match="no clause of his names line 2"):
            sb.call("rulings.rule", rulings={
                "3": "drop", "2": "add Drop line 3 and its tax.",
                "rest": "approve"})
    sb, _ = _seat(db, ask, words=words)
    sb.call("rulings.rule", rulings={
        "3": "drop", "c2": "add The page leaves out the tip.",
        "rest": "approve"})
    assert _rows(sb)["calculate_tip"]["act"] == "add"

