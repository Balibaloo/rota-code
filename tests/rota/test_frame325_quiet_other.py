"""
A ledger row of kind `other` is a quiet count line on the page, not an
assumption (frame 325, repair K, first step).

Night 165's m172 showed the Developer's account of its own state, ledger
row l_0553f217b1 of kind `other`, as line 6 under "Where you did not say,
I assumed:". The principal asked three times to take it off the page. Frame
204's design, section 8, ruled on 2026-10-11 15:44: "An `other` row goes to
the quiet section". The page read no kind, so that pass was never built.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.roles.principal import render_page

DEFAULT_TEXT = "the percentage is typed each time, not a fixed tier"
OTHER_TEXT = ("The commit system is blocked by a stale note, but the "
              "implementation is correct")

# The page of `_no_other` at 7ebf2612, before this frame. A page with no
# `other` row keeps these bytes.
BEFORE = (
    "Here is what I understand you want, on one page.\n"
    "You asked:\n"
    "  1. \"tip calculator pls\"\n"
    "The team's notes. A seat wrote each of these where your words were "
    "silent. They are not your request.\n"
    "Where you did not say, I assumed:\n"
    "  2. the percentage is typed each time, not a fixed tier\n"
    "Reply in your own words. 'ok' approves all of this and starts building. "
    "Name a line to correct only that line. Ask, if something here is unclear."
)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _seed(db, with_other: bool) -> list[str]:
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e1','principal','tip calculator pls',1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1','e1',0,18,'tip calculator pls',"
               "'ratified')")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "kind, status, author) VALUES ('l_a69ad6edd4','s1','statements',"
               "?,'default','open','vision_keeper')", (DEFAULT_TEXT,))
    refs = ["s1", "l_a69ad6edd4"]
    if with_other:
        db.execute("INSERT INTO ledger (id, about_ref, about_table, "
                   "default_taken, kind, status, author) VALUES "
                   "('l_0553f217b1','s1','statements',?,'other','open',"
                   "'developer')", (OTHER_TEXT,))
        refs.append("l_0553f217b1")
    db.commit()
    return refs


def test_an_other_row_is_a_count_line_with_no_number(db):
    refs = _seed(db, with_other=True)
    page, order = render_page(db, "present", refs, ask_id="m172",
                              returned=False)
    assert OTHER_TEXT not in page, page
    assert "l_0553f217b1" not in order, "a reply cannot land a ruling on it"
    assert "Not shown: 1 note from the Developer that fits no category." in page
    line = next(x for x in page.splitlines() if x.startswith("Not shown:"))
    assert not line.lstrip()[0].isdigit(), line


def test_the_default_row_keeps_its_number_and_its_words(db):
    refs = _seed(db, with_other=True)
    page, order = render_page(db, "present", refs, ask_id="m172",
                              returned=False)
    assert order == ["s1", "l_a69ad6edd4"]
    assert f"  2. {DEFAULT_TEXT}" in page, page
    # The count line follows the notes.
    assert (page.index("Where you did not say, I assumed:")
            < page.index(DEFAULT_TEXT) < page.index("Not shown:")
            < page.index("Reply in your own words.")), page


def test_a_page_with_no_other_row_is_byte_equal_to_before(db):
    refs = _seed(db, with_other=False)
    page, order = render_page(db, "present", refs, ask_id="m9",
                              returned=False)
    assert page.encode() == BEFORE.encode(), page
    assert order == ["s1", "l_a69ad6edd4"]


def test_two_other_rows_from_two_seats_make_one_line(db):
    refs = _seed(db, with_other=True)
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "kind, status, author) VALUES ('l_8fd20d7618','s1','statements',"
               "'the test and the code disagree','other','open','tester')")
    db.commit()
    page, order = render_page(db, "present", refs + ["l_8fd20d7618"],
                              ask_id="m172", returned=False)
    assert ("Not shown: 2 notes from the Developer and the Tester that fit "
            "no category.") in page, page
    assert page.count("Not shown:") == 1
    assert order == ["s1", "l_a69ad6edd4"]
