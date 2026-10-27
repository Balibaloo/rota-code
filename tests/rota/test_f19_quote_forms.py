"""F19, sprint 28: the quote door reads a quote at the escape level of the
seat's call and each view of the row that `runner._render` shows.

Roman ruled on 2026-08-26 that a quote is "a contiguous span of the
disputed row, verbatim, whitespace-normalised" (`DECISIONS.md` near 1294).
Three hand rules read the call syntax before this change: `_seat_forms`,
`_one_backslash` and `_unescaped`. The two cases marked red were refused
on 9827e38a. A seat's text through the call stored the row, or the seat
copied a view that `runner._render` shows, and no hand rule held the form.
"""
from __future__ import annotations

from rota.core import sandbox

BS = chr(92)

# Night 168 W2, s147: the test row holds one backslash, and the quote holds
# two, as the JSON of `tests.load` shows it.
TST_W2 = ("def test_format_filename_keeps_a_windows_path():\n"
          "    result = format_filename(\"C:/AppData" + BS + "Roaming\")\n"
          "    assert \"AppData" + BS + "Roaming\" in result\n")


def test_night_168_w2_a_quote_with_two_backslashes_for_one_reads():
    quote = "assert \"AppData" + BS * 2 + "Roaming\" in result"
    assert sandbox._quote_reads(quote, TST_W2, "tests")


def test_red_a_quote_with_the_escape_of_a_letter_reads_the_letter():
    """Red on 9827e38a: `_unescaped` read only a control character. The
    call stores `é` from the seat's `\\u00e9` on the strict path, so the
    door reads the same value from the text that the lenient path kept."""
    row = ("def test_shorten_keeps_an_accent():\n"
           "    assert shorten(\"caf\u00e9.txt\") == \"caf\u00e9.txt\"\n")
    quote = ("assert shorten(\"caf" + BS + "u00e9.txt\") == \"caf" + BS
             + "u00e9.txt\"")
    assert sandbox._quote_reads(quote, row, "tests")


def test_red_a_quote_of_the_table_view_reads_the_row():
    """Red on 9827e38a: `runner._render` shows a row of a list as a table
    cell, and a cell shows each `|` as `\\|`. The hand list of views held
    no table view."""
    row = "The command joins the names with a pipe, as in a | b | c."
    quote = "joins the names with a pipe, as in a " + BS + "| b " + BS + "| c"
    assert sandbox._quote_reads(quote, row, "criteria")


def test_a_quote_with_both_marks_escaped_reads_the_criterion():
    row = "format_filename returns 'c.txt' for \"a/b/c.txt\" when shorten=True."
    quote = ("returns " + BS + "'c.txt" + BS + "' for \"a/b/c.txt\" when "
             "shorten=True")
    assert sandbox._quote_reads(quote, row, "criteria")


def test_an_escape_read_on_both_sides_is_no_span():
    """The review of frame 328 pass 3, finding 1: a quote is read through
    the call once. `\\033` and `\\x1b` give one byte, and neither is a
    span of the other's text."""
    raw = "def t():\n    assert r\"" + BS + "x1b[2J\" in out\n"
    assert not sandbox._quote_reads(
        "assert r\"" + BS + "033[2J\" in out", raw, "tests")
    data = "def t():\n    assert b\"" + BS + "u001b[2J\" in out\n"
    assert not sandbox._quote_reads(
        "assert b\"" + BS + "x1b[2J\" in out", data, "tests")


def test_an_escaped_line_break_meets_only_a_line_break():
    """Pass 1b, the review's finding 1: the rule of frame 328 review 1,
    finding 4, holds at the door, after `_call_values` decodes `\\n`."""
    quote = "assert r == \"a" + BS + "nb is the text\""
    assert not sandbox._quote_reads(quote, "assert r == \"a b is the text\"",
                                    "tests")
    row = "The first line\nthe second line holds the text."
    quote = "The first line" + BS + "nthe second line holds"
    assert sandbox._quote_reads(quote, row, "criteria")
    assert not sandbox._quote_reads(quote, row.replace("\n", " "), "criteria")


def test_a_verbatim_copy_of_a_raw_escape_reads_the_raw_row():
    """Pass 1c, the review's finding 3: a seat that copies `r"\\x1b[2J"`
    verbatim into its call gets ESC on the strict path. The copy is a
    verbatim span (ruled: Roman, 2026-08-26), so it reads the row. The
    ESC of a seat's `r"\\033[2J"` reads too, as in the parent: both spell
    the same escape, and the door sees only the stored value."""
    row = "def t():\n    assert r\"" + BS + "x1b[2J\" in out\n"
    assert sandbox._quote_reads("assert r\"\x1b[2J\" in out", row, "tests")
    # A row whose literal is not raw holds ESC through the call.
    plain = "def t():\n    assert \"" + BS + "x1b[2J\" in out\n"
    assert sandbox._quote_reads("assert \"\x1b[2J\" in out", plain, "tests")


def test_a_quote_with_both_marks_bare_reads_through_the_call():
    """Pass 1b, the review's finding 4: only the decoder of `_span_of`
    read this quote, and `_call_values` now carries it."""
    row = "It's 'c.txt' for \"a/b\" now, as the criterion says."
    quote = "It's " + BS + "'c.txt" + BS + "' for \"a/b\" now"
    assert sandbox._quote_reads(quote, row, "criteria")


def test_the_lenient_value_of_an_escaped_backslash_is_no_form():
    """Pass 1b, the review's finding 6: the lenient path stores `\\\\n` as a
    backslash and a line break, a value that no seat meant."""
    row = "The path C:" + BS + "\new folder holds the file."
    quote = "The path C:" + BS * 2 + "new folder holds the file"
    assert not sandbox._quote_reads(quote, row, "criteria")


def test_the_views_come_from_the_render():
    views = sandbox._shown_views("a" + BS + "b\nc | d")
    assert "a" + BS + "b\nc | d" in views
    assert "a" + BS * 2 + "b" + BS + "nc | d" in views
    assert "a" + BS + "b c " + BS + "| d" in views


def test_the_refusal_names_the_form_that_the_call_stores():
    quote = "assert \"AppData" + BS * 2 + "Local\" in result"
    said = sandbox._quote_refusal("tst_crit_1", "tests", quote, "crit_1",
                                  "tst_crit_1")
    assert ("The door also reads the quote as the call stores it from your "
            "text, with each escape read as Python reads it. Read that way, "
            "the quote is `assert \"AppData" + BS + "Local\" in result`, and "
            "the code of tst_crit_1 holds no such span.") in said
