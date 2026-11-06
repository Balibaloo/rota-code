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

import re

import pytest

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


# Pass 2, the review of c91c9a5b, finding 2: the join follows his reply.
TWO = "Drop line 3. The page leaves out the tax, and it leaves out the rounding."
JOINED = "The page leaves out the tax, and it leaves out the rounding."


def _add_row(db, words, keys) -> dict:  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words=words)
    sb.call("rulings.rule", rulings={"3": "drop", **keys, "rest": "approve"})
    return {**_rows(sb)["calculate_tip"], "reply": sb.ctx.trigger}


def test_a_repeated_quote_is_refused_once_then_each_clause_lands(
        db):  # noqa: F811
    """Probe A of the review. One n175 recording keys c2 and c3 with the
    same sentence. Pass 4: the quote of c2 lies in c3, so the door names c3
    once. The repeat lands the words of each clause that the seat keys add."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words=TWO)
    keys = {"3": "drop", "c2": "add it leaves out the rounding.",
            "c3": "add it leaves out the rounding.", "rest": "approve"}
    with pytest.raises(ValueError, match=r"^clause c2: the quote lies in "
                                         r"clause c3, not in c2"):
        sb.call("rulings.rule", rulings=keys)
    sb.call("rulings.rule", rulings=keys)
    row = _rows(sb)["calculate_tip"]
    assert (row["words"], row["words_from"]) == (JOINED, sb.ctx.trigger)


def test_an_overlapping_quote_stands_once(db):  # noqa: F811
    """Probe B of the review: the quote of c2 holds the quote of c3."""
    row = _add_row(db, TWO, {"c2": "add " + JOINED,
                             "c3": "add it leaves out the rounding."})
    assert (row["words"], row["words_from"]) == (JOINED, row["reply"])


def test_turned_quotes_are_refused_and_name_the_clause(db):  # noqa: F811
    """Probe C of the review: the keys give the second clause first. Pass 4:
    the quote of c2 lies in c3, so no order of the two quotes is his order
    for the keys. The door names the clause that holds the quote, as the
    line key refusal does."""
    with pytest.raises(ValueError, match=r"^clause c2: the quote lies in "
                                         r"clause c3, not in c2"):
        _add_row(db, TWO, {"c2": "add it leaves out the rounding.",
                           "c3": "add The page leaves out the tax"})


def test_a_double_space_in_his_clause_keeps_his_text_between(
        db):  # noqa: F811
    words = ("Drop line 3. The page leaves out  the tax, and it leaves out "
             "the rounding.")
    row = _add_row(db, words, {"c2": "add The page leaves out  the tax",
                               "c3": "add it leaves out the rounding."})
    assert row["words"] == ("The page leaves out  the tax, and it leaves out "
                            "the rounding.")
    assert row["words_from"] == row["reply"]


# Pass 3, the review of ede08a30.
def test_a_part_is_found_from_its_own_clause(db):  # noqa: F811
    """Item 1: the first place in the whole reply took "add tests." from his
    "Do not add tests." and turned the order. In the review's reply "Use the
    tax, and add tests." `page_clauses` gives "add tests." no clause, so the
    door case puts it in a sentence of its own."""
    words = "Do not add tests. Drop line 3. Use the tax. Add tests."
    row = _add_row(db, words, {"c1": "none", "c3": "add Use the tax.",
                               "c4": "add Add tests."})
    assert (row["words"], row["words_from"]) == (
        "Use the tax. Add tests.", row["reply"])
    # The review's own reply, at the level of the join.
    his = "Do not add tests. Drop line 3. Use the tax, and add tests."
    at = his.index("Use the tax")
    assert api._joined_add(his, [(at, "Use the tax"), (at, "add tests.")]) == (
        "Use the tax, and add tests.", ["Use the tax, and add tests."])


def test_adds_that_do_not_touch_name_his_reply(db):  # noqa: F811
    """Item 4: each run is a span of his reply, so the row names it, as a
    single add does."""
    words = ("The page leaves out the tax. Drop line 3. The page leaves out "
             "the rounding.")
    row = _add_row(db, words, {"c1": "add The page leaves out the tax.",
                               "c3": "add The page leaves out the rounding."})
    assert (row["words"], row["words_from"]) == (
        "The page leaves out the tax. The page leaves out the rounding.",
        row["reply"])


# Pass 4: the rule. Each clause that the seat keys add is on the record
# once, in his spelling and in his order, and `words_from` names his reply
# only then. When the keys cannot give that, the door refuses and names the
# clause. The four known breaks are cases A to D of the frame 362 brief.
REPEATED_PIECE = "Do not add tests. Drop line 3. Use the tax, and add tests."
FIRST_PLACE = ("Keep the rounding. Drop line 3. The page leaves out the tax, "
               "and the rounding.")
P3 = ("The page leaves out the tax. Drop line 3. The page leaves out the "
      "fee. The page leaves out the rounding.")


@pytest.mark.parametrize("words, piece", [
    (REPEATED_PIECE, "add tests."), (FIRST_PLACE, "the rounding.")])
def test_a_piece_that_an_earlier_clause_also_holds_is_a_clause(
        db, words, piece):  # noqa: F811
    """Case A, review 3 finding 3. The cut dropped a piece when an earlier
    clause held its text anywhere, so the seat had no key for his add."""
    ask = _page(db)
    menu = api.page_menus(db, ["s1", "calculate_tip", "l_1"], "")[1]
    clauses = api.page_clauses(words, 3, menu)
    assert clauses[-1]["words"] == piece
    assert "add <quote>" in clauses[-1]["options"]
    sb, _ = _seat(db, ask, words=words)
    last = words.rindex(piece)
    sb.call("rulings.rule", rulings={
        "3": "drop", "c1": "none", "c3": "add " + clauses[2]["words"],
        "c4": "add " + piece, "rest": "approve"})
    row = _rows(sb)["calculate_tip"]
    assert (row["words"], row["words_from"]) == (
        words[words.index(clauses[2]["words"]):last + len(piece)],
        sb.ctx.trigger)


@pytest.mark.parametrize("words, keys, line_key, add_key", [
    ("Line 2 should say per person. The page leaves out the tax.",
     {"c1": "other per person", "c2": "add The page leaves out the tax."},
     "clause c1", "clause c2"),
    ("The page leaves out the tax. Line 2 should say per person.",
     {"c1": "add The page leaves out the tax.", "c2": "other per person"},
     "clause c2", "clause c1")])
def test_a_contest_and_an_add_on_one_line_are_refused(
        db, words, keys, line_key, add_key):  # noqa: F811
    """Case B, review 1 point 4. One row holds one verdict per ruling and
    ref, so the later of the two overwrote the other, in both orders."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words=words)
    with pytest.raises(ValueError, match=(
            rf"^line 2: {line_key} gives .* and {add_key} gives .*one "
            rf"option per line")):
        sb.call("rulings.rule", rulings={**keys, "rest": "approve"})
    # The refusal fires on every call, because no repeat can keep both.
    with pytest.raises(ValueError, match=r"^line 2: "):
        sb.call("rulings.rule", rulings={**keys, "rest": "approve"})
    # The way out that the refusal names keeps his words of both clauses.
    sb.call("rulings.rule", rulings={"2": "other " + words,
                                     "c1": "none" if add_key == "clause c1"
                                     else keys["c1"],
                                     "c2": "none" if add_key == "clause c2"
                                     else keys["c2"], "rest": "approve"})
    row = _rows(sb)["calculate_tip"]
    assert (row["verdict"], row["words"]) == ("contest", words)


@pytest.mark.parametrize("line_value", ["drop", "other Line 2 is wrong."])
def test_a_line_key_that_lands_a_row_beside_clause_adds_is_refused(
        db, line_value):  # noqa: F811
    """Case C, review 1 finding 5. A `drop` or an `other` key on the add line
    made every clause add land nothing, with no refusal. The n174
    recordings key line 11 so."""
    ask = _page(db)
    words = ("Line 2 is wrong. The page leaves out the tax, and it leaves out "
             "the rounding.")
    sb, _ = _seat(db, ask, words=words)
    keys = {"2": line_value, "c2": "add", "c3": "add", "rest": "approve"}
    # Pass 2: one refusal names every clause add of the line, and its way
    # out lands in one call (review of 0c5e4a4d, finding 3).
    # Pass 3: the key faults line 2, so the text offers the ask and no
    # approve (second look, finding B).
    with pytest.raises(ValueError, match=(
            r"^line 2: the line key gives '(drop|other)', and c2, c3 add to "
            r"line 2\. One ruling holds one option per line, and the key "
            r"faults line 2\. Call rulings\.rule\(ask=\.\.\.\)")) as refusal:
        sb.call("rulings.rule", rulings=keys)
    assert "approve" not in str(refusal.value)
    sb.call("rulings.rule", ask="Line 2 is wrong, and the page leaves out "
                                "the tax. Which one do you mean?")
    assert not _rows(sb)


@pytest.mark.parametrize("words, quote, row", [
    ("Use the follow-up rule.", "up rule.", "follow-up rule."),
    ("Use the follow-up rule.", "Use the follow", "Use the follow-up"),
    ("Don't round the tax.", "t round the tax.", "Don't round the tax."),
    ("Don’t round the tax.", "t round the tax.",
     "Don’t round the tax."),
    ("The fold is in string.py now.", "py now.", "string.py now."),
    ("The fold is in string.py now.", "The fold is in string.",
     "The fold is in string.py"),
    ("The fold is in string.py now.", "ring.p", "string.py"),
    ("The fold is _foldline here.", "foldline here.", "_foldline here."),
    ("Call parse_args first.", "args first.", "parse_args first."),
    ("Round to 3.14 always.", "14 always.", "3.14 always."),
    ("Cap the tip at 1,000 dollars.", "000 dollars.", "1,000 dollars."),
    ("Add a note “Tax” to it.", "Tax” to it.",
     "“Tax” to it."),
    ("The page leaves out the tax", "The page leaves out the ta",
     "The page leaves out the tax")])
def test_a_quote_runs_to_the_white_space_of_his_word(
        db, words, quote, row):  # noqa: F811
    """Second look, finding A. The word stopped at a hyphen, an apostrophe,
    an underscore, a dot, a comma and a curly quote."""
    got = _add_row(db, "Drop line 3. " + words, {"c2": "add " + quote})
    assert got["words"] == row


def test_a_quote_of_the_first_word_runs_to_the_start_of_his_reply(
        db):  # noqa: F811
    ask = _page(db)
    sb, _ = _seat(db, ask, words="The page leaves out the tax. Drop line 3.")
    sb.call("rulings.rule", rulings={
        "3": "drop", "c1": "add he page leaves out the tax.",
        "rest": "approve"})
    assert _rows(sb)["calculate_tip"]["words"] == "The page leaves out the tax."


def test_a_line_add_and_a_clause_add_on_one_line_join(db):  # noqa: F811
    """Case C by the add key. A line key `add` on the add line dropped every
    clause add, as a contest did. Both adds hold his words, so they join."""
    ask = _page(db)
    words = ("Line 2 is fine. The page leaves out the tax, and it leaves out "
             "the rounding.")
    sb, _ = _seat(db, ask, words=words)
    sb.call("rulings.rule", rulings={"2": "add Line 2 is fine.", "c2": "none",
                                     "c3": "add", "rest": "approve"})
    row = _rows(sb)["calculate_tip"]
    assert row["words"] == ("Line 2 is fine. it leaves out the rounding.")


def test_a_quote_from_an_earlier_clause_is_refused_by_name(
        db):  # noqa: F811
    """Case D, review 3 finding 1. The quote of c4 lies in c1, and the row
    joined it after c3 with `words_from` set."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words=P3)
    keys = {"3": "drop", "c1": "none", "c3": "add The page leaves out the fee.",
            "c4": "add The page leaves out the tax.", "rest": "approve"}
    with pytest.raises(ValueError, match=(
            r"^clause c4: the quote lies in clause c1, not in c4\. ")):
        sb.call("rulings.rule", rulings=keys)
    # The refusal fires once. The repeat lands each keyed clause's own words.
    sb.call("rulings.rule", rulings=keys)
    row = _rows(sb)["calculate_tip"]
    assert (row["words"], row["words_from"]) == (
        "The page leaves out the fee. The page leaves out the rounding.",
        sb.ctx.trigger)


def test_a_quote_in_the_seats_case_lands_in_his_spelling(db):  # noqa: F811
    """Case D, review 3 finding 2. The row kept the seat's lower case."""
    row = _add_row(db, TWO, {"c2": "add the page leaves out the tax",
                             "c3": "none"})
    assert (row["words"], row["words_from"]) == (
        "The page leaves out the tax", row["reply"])


def _in_his_order(his: str, words: str) -> bool:
    """True when each word of `words` is a word of `his`, in his spelling and
    in his order."""
    at = 0
    for tok in words.split():
        at = his.find(tok, at)
        if at < 0:
            return False
        at += len(tok)
    return True


def _his_text(his: str, quote: str, clause: str) -> str:
    """His own text of a quote, found case-folded inside the clause. A
    quote from another clause lands the clause's own words, after the
    refusal that fires once."""
    pat = re.compile(r"\s+".join(map(re.escape, quote.split())), re.I)
    m = pat.search(clause)
    return m.group(0) if m else clause


# The built replies of the rule test. Each one holds a shape that broke the
# record before: a repeated sentence, a repeated piece, mixed shapes on one
# line, a mis-keyed quote, a quote in the seat's case, bare adds, and a
# quote that runs past its clause.
RULE_REPLIES = [
    ("Add the tax. Drop line 3. Add the tax.",
     {"c1": "add Add the tax.", "c3": "add Add the tax."}),
    (REPEATED_PIECE, {"c1": "none", "c3": "add Use the tax",
                      "c4": "add add tests."}),
    (REPEATED_PIECE, {"c1": "add add tests.", "c3": "add Use the tax"}),
    (FIRST_PLACE, {"c1": "none", "c3": "add The page leaves out the tax",
                   "c4": "add the rounding."}),
    ("Line 2 should say per person. The page leaves out the tax.",
     {"c1": "other per person", "c2": "add The page leaves out the tax."}),
    ("The page leaves out the tax. Line 2 should say per person.",
     {"c1": "add The page leaves out the tax.", "c2": "other per person"}),
    ("Line 2 is wrong. The page leaves out the tax, and it leaves out the "
     "rounding.", {"2": "drop", "c2": "add", "c3": "add"}),
    (P3, {"c1": "none", "c3": "add The page leaves out the fee.",
          "c4": "add The page leaves out the tax."}),
    (TWO, {"c2": "add it leaves out the rounding.",
           "c3": "add the page leaves out the tax"}),
    (TWO, {"c2": "add the page leaves out the tax", "c3": "add"}),
    (TWO, {"c2": "add", "c3": "add"}),
    (TWO, {"c2": "add " + JOINED, "c3": "none"}),
    (TWO, {"c2": "add " + JOINED, "c3": "add it leaves out the rounding."}),
    ("Drop line 3. The page leaves out the tax.\nAlso the page leaves out "
     "the rounding.", {"c2": "add", "c3": "add"}),
    # Pass 2: adjacent repeats, probes Q1 and Q4 of the review of 0c5e4a4d.
    ("Drop line 3. Add the tax. Add the tax.", {"c2": "add", "c3": "add"}),
    ("Drop line 3. Use the tax. Use the tax. Use the fee.",
     {"c2": "add", "c3": "add", "c4": "add"}),
    (TWO, {"c2": "add he page leaves out the t", "c3": "none"}),
]


@pytest.mark.parametrize("words, keys", RULE_REPLIES)
def test_every_clause_add_is_on_the_record_or_the_door_names_a_clause(
        db, words, keys):  # noqa: F811
    ask = _page(db)
    menu = api.page_menus(db, ["s1", "calculate_tip", "l_1"], "")[1]
    clauses = [c["words"] for c in api.page_clauses(words, 3, menu)]
    sb, _ = _seat(db, ask, words=words)
    rulings = {"3": "drop", **keys, "rest": "approve"}
    if "Drop line 3." not in words:
        rulings.pop("3")
    try:
        sb.call("rulings.rule", rulings=rulings)
    except ValueError as e:
        assert re.match(r"(clause c\d+|line \d+|c\d+(, c\d+)*): ",
                        str(e)), str(e)
        # A refusal that fires once lets the repeat land, so the repeat's
        # row must keep the rule too (review of 0c5e4a4d, finding 6). Each
        # repeat can meet the once refusal of the next clause.
        last = str(e)
        for _ in range(4):
            try:
                sb.call("rulings.rule", rulings=rulings)
                break
            except ValueError as again:
                if str(again) == last:
                    return
                last = str(again)
    row = _rows(sb)["calculate_tip"]
    adds = [(int(k[1:]), v) for k, v in sorted(keys.items())
            if k.startswith("c") and v.startswith("add")]
    want = [_his_text(words, v[4:] or clauses[k - 1], clauses[k - 1])
            for k, v in adds]
    at = 0
    for text in want:
        # Each add clause in his spelling, after the one before it.
        at = row["words"].find(text, at)
        assert at >= 0, (row["words"], want)
        at += 1
    assert _in_his_order(words, row["words"]), row["words"]
    assert row["words_from"] in (sb.ctx.trigger, None)


# Pass 2, the review of 0c5e4a4d.
@pytest.mark.parametrize("words, keys, joined", [
    ("Drop line 3. Add the tax. Add the tax.", {"c2": "add", "c3": "add"},
     "Add the tax. Add the tax."),
    ("Drop line 3. Use the tax. Use the tax. Use the fee.",
     {"c2": "add", "c3": "add", "c4": "add"},
     "Use the tax. Use the tax. Use the fee.")])
def test_adjacent_clauses_with_the_same_words_land_each(
        db, words, keys, joined):  # noqa: F811
    """Finding 1, high. A second search gave the second clause the offset
    of the first, so his repeat landed once with no refusal."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words=words)
    rulings = {**keys, "rest": "approve"}
    if words.startswith("Drop line 3."):
        rulings["3"] = "drop"
    sb.call("rulings.rule", rulings=rulings)
    row = _rows(sb)["calculate_tip"]
    assert (row["words"], row["words_from"]) == (joined, sb.ctx.trigger)


def test_the_stamp_reads_the_place_of_the_words(db):  # noqa: F811
    """Finding 4. "add tests." taken from c1 "Do not add tests." took the
    stamp, because c4 holds the same text as a whole clause."""
    row = _add_row(db, REPEATED_PIECE, {"c1": "add add tests.",
                                        "c3": "add Use the tax",
                                        "c4": "none"})
    assert (row["words"], row["words_from"]) == ("add tests. Use the tax",
                                                 None)


def test_a_quote_that_cuts_a_word_lands_with_the_whole_word(
        db):  # noqa: F811
    """Finding 2, the mechanical part. A part of whole words stays a part,
    as 84 of 189 recorded clause adds are."""
    row = _add_row(db, TWO, {"c2": "add he page leaves out the t",
                             "c3": "none"})
    assert (row["words"], row["words_from"]) == (
        "The page leaves out the tax", row["reply"])


def test_the_named_way_out_lands_in_one_call_on_n174_m53_m58(tmp_path):
    """Finding 3. The C refusal named one clause add, and its way out met
    a second refusal for c3. The case expects an ask, and the ask lands."""
    from pathlib import Path

    from rota.core.db import init_db
    from rota.core.sandbox import build
    from rota.roles import prompts
    from rota.testkit import fixtures

    case = next(c for c in fixtures.load_case(
        Path("tests/rota/cases/l3_rulings.yaml"))
        if c["id"] == "L3R-n174-m53-m58")
    c2 = ("The docstring gains an example where, with shorten set to true, "
          "the path a/b/c.txt shows as c.txt.")
    c3 = ("Only the docstring in the termui file changes and the code stays "
          "the same.")
    keys = {**{str(n): "drop" for n in range(1, 11)}, "12": "approve",
            "rest": "none", "11": "drop", "c2": "add " + c2, "c3": "add " + c3}
    conn = init_db(tmp_path / "rota.db")
    fixtures.seed(conn, case.get("fixture") or {})
    msg = fixtures.seed_inbound(conn, case)
    conn.commit()
    with fixtures._page_as_seen(case):
        sb = build("liaison", conn, mode="normal", session_id="s_w",
                   allow=prompts.mode_tools("liaison", "landing"))
        sb.ctx.trigger = msg
        with pytest.raises(ValueError, match=(
                r"^line 11: the line key gives 'drop', and c2, c3 add to "
                r"line 11\. ")) as refusal:
            sb.call("rulings.rule", rulings=keys)
        assert len(str(refusal.value)) < 250
        assert "approve" not in str(refusal.value)
        # Pass 3: the way out is the ask, which the case expects.
        out = sb.call("rulings.rule", ask="Do you want lines 1 to 12 "
                                          "dropped, or the docstring example "
                                          "added?")
    assert out is not None
    assert not [w for w in sb.ctx.writes if w[0] == "ruled_refs"]
