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

from pathlib import Path

import pytest
import yaml

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


def test_a_tail_clause_in_the_same_sentence_takes_the_sentences_lines():
    """Pass 2c, the review's narrower fix of finding 3: a clause with no
    number takes the lines of the clause before it in the same sentence."""
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
    assert api.WORD_ACTS["add"] == ("approve", "add")
    # Pass 5: the seat gave `keep` on approve words in 18 of 18 Gemma runs,
    # so keep is the verdict approve and no act word.
    assert "keep" not in api.WORD_ACTS
    assert api.RULING_WORDS["keep"] == "approve"


def test_the_word_shape_fills_words_and_the_target_kind(db):  # noqa: F811
    page = "1. The change touches:\n   src/click/utils.py\n   tests/test_utils.py\n"
    for act, kind in (("drop", "row"), ("rewrite", "row"), ("remove", "row"),
                      ("add", None)):
        shape = api._word_shape(db, "c_1", {"act": act}, "Line 1 is wrong",
                                ["c_1"], page)
        assert shape.get("target_kind") == kind
        assert shape["words"] == "Line 1 is wrong"
    # The seat names the path after the word, and code finds it on the line
    # (pass 7).
    shape = api._word_shape(db, "guess:calc", {"act": "exclude",
                                               "given": "utils.py"},
                            "drop the utils file from line 1", ["guess:calc"],
                            page, "1")
    assert shape == {"act": "exclude", "target_kind": "path",
                     "words": "drop the utils file from line 1",
                     "target": "src/click/utils.py",
                     "paths": ["src/click/utils.py"]}
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


# Pass 2b: the review p3 of 27291602 (`plans/f345-review-p3.md`).
CASES = Path(__file__).parent / "cases" / "l3_rulings.yaml"


def _reply(case_id: str) -> tuple[str, int]:
    """His reply of one L3 case, verbatim, and the page's line count."""
    for case in yaml.safe_load(CASES.read_text(encoding="utf-8")):
        if case["id"] == case_id:
            return (case["inbound"]["body_text"],
                    len(case["inbound"]["body_refs"]))
    raise KeyError(case_id)


def test_a_number_inside_a_reason_names_no_line():
    """Finding 1: "about lines 1 to 5" sits in his reason, so line 1 does
    not take "drop it"."""
    his, size = _reply("L3R-n172-m80-m81")
    got = api.line_words(his, size)
    assert "drop it" not in (got[1] or "")
    assert got[2].startswith("The second line is wrong")
    _verbatim(his, got)


def test_a_number_inside_a_quote_names_no_line():
    """Finding 1: the quote "also remove lines 17, 18" names no line, so
    lines 17 and 18 do not take the line 68 complaint."""
    his, size = _reply("L3R-n174-m47-m48")
    got = api.line_words(his, size)
    for n in (17, 18):
        assert "Line 68" not in (got[n] or "")
        assert got[n].startswith("Lines 8 to 67")
    assert got[68].startswith("Line 68 misreads me")
    _verbatim(his, got)


def test_a_number_deep_in_a_clause_names_no_line():
    """Finding 1: "added to line 3" is no subject, so line 3 keeps its own
    clause and takes neither "Change line 7" nor "Change line 9"."""
    his, size = _reply("L3R-n174-m53-m55")
    got = api.line_words(his, size)
    assert "Change line 7" not in got[3]
    assert "Change line 9" not in got[3]
    assert got[3] == "Keep lines 2 to 6 and line 8 as they are."
    assert got[8] == got[3]
    assert got[7].startswith("Change line 7")
    assert got[9].startswith("Change line 9")
    _verbatim(his, got)


def test_a_place_in_code_names_no_line():
    """Finding 1: a number after "at", "in", "see", a path or a code name
    with a colon names no page line."""
    for his in ("You can remove the line at 518 in get_app_dir.",
                "See line 3 of the old page, it is fine.",
                "The bug sits in line 4 of src/click/termui.py.",
                "Look at get_app_dir:518 again."):
        got = api.line_words(his, 9)
        assert set(got.values()) == {his}, his


def test_a_clause_with_no_number_takes_no_line_before_it():
    """Finding 3: in n170-m58-m59, "keep what clear() prints" lands on no
    line by the match alone."""
    his, size = _reply("L3R-n170-m58-m59")
    got = api.line_words(his, size)
    assert not any("keep what clear() prints" in (w or "")
                   for w in got.values())
    _verbatim(his, got)


@pytest.mark.parametrize("case_id, line, tail", [
    ("L3R-n175-m44-m45", 2,
     "the change touches only clear in src/click/termui.py and its tests"),
    ("L3R-n170-m74-m75", 3,
     "so please remove the five formatting tests from what you expect"),
])
def test_a_tail_clause_gives_the_exclude_its_path_words(case_id, line, tail):
    """Pass 2c: pass 2b cut the tail clause, and the exclude lost the words
    that name its path. The tail stands in the same sentence as the line."""
    his, size = _reply(case_id)
    got = api.line_words(his, size)
    assert tail in got[line]
    _verbatim(his, got)


def test_one_word_on_a_line_with_no_words_lands_on_the_whole_reply(db):  # noqa: F811
    """Finding 2: a one-word drop on a line that shows "no words" lands
    with his whole reply as its words. The span check refused it before,
    and the one word has no place for words. "on line 3" is no subject of
    its clause, so the match names no words for line 3. Pass 2c refuses the
    drop once with the sentence of the match, and the repeat lands."""
    his = "Line 1 is right. Nobody needs the note on line 3, so drop it."
    ask = _page(db)
    sb, reply = _seat(db, ask, words=his)
    assert api.line_words(his, 3)[3] is None
    call = {"1": "approve", "2": "approve", "3": "drop"}
    with pytest.raises(ValueError) as e:
        sb.call("rulings.rule", rulings=dict(call))
    assert str(e.value) == (
        "line 3: no words of his name line 3. Rule the lines his words name, "
        "and approve or leave out line 3")
    sb.call("rulings.rule", rulings=dict(call))
    rows = {w[2]["ref"]: w[2] for w in sb.ctx.writes if w[0] == "ruled_refs"}
    row = rows["l_1"]
    assert (row["verdict"], row["act"], row["target_kind"]) == (
        "contest", "drop", "row")
    assert row["words"] == his


# Pass 3: a subject that lists bare numbers. L1 approve-one-line-only.
ONE_LINE = ("1 is fine, go ahead with it. 2 and 3 say the same sentence twice "
            "each; I am not reading those. approve 1 only.")


@pytest.mark.parametrize("his, named", [
    (ONE_LINE, {1, 2, 3}),
    ("1 is fine, 2 and 3 are wrong", {1, 2, 3}),
    ("2, 3 and 4 are wrong.", {2, 3, 4}),
    ("2 to 4 are wrong.", {2, 3, 4}),
    ("Line 1 is right, 4 is wrong.", {1, 4}),
])
def test_a_subject_that_lists_numbers_names_each_line(his, named):
    """A list with "and", a comma or "to" that opens a clause, or follows a
    comma, names each line it holds."""
    got = api.line_words(his, 5)
    assert {n for n, w in got.items() if w} == named
    _verbatim(his, got)


def test_the_conjoined_subject_binds_its_own_clause():
    got = api.line_words(ONE_LINE, 3)
    assert got[1] == "1 is fine, go ahead with it."
    assert got[2] == got[3] == ("2 and 3 say the same sentence twice each; I "
                                "am not reading those.")


@pytest.mark.parametrize("his", [
    "I want 2 examples, 3 at most.",
    "The values 1, 2 and 3 are printed.",
    "You can remove the line at 518 in get_app_dir.",
])
def test_a_number_list_inside_a_clause_names_no_line(his):
    """A list deep in a clause, or a single number with no "is" or "are",
    is no subject. Such a reply names no line, so each line takes it whole."""
    got = api.line_words(his, 5)
    assert set(got.values()) == {his}


def test_the_drops_of_a_conjoined_subject_land(db):  # noqa: F811
    """L1 approve-one-line-only: the seat wrote 1 approve, 2 and 3 drop, and
    the no-words refusal took all three runs, because the match gave lines
    2 and 3 no words."""
    ask = _page(db)
    sb, _ = _seat(db, ask, words=ONE_LINE)
    sb.call("rulings.rule", rulings={"1": "approve", "2": "drop", "3": "drop"})
    rulings = [w for w in sb.ctx.writes if w[0] == "rulings"]
    assert len(rulings) == 1


def test_a_row_on_two_lines_of_the_page_lands_a_word_on_each(db):  # noqa: F811
    """L3R-n174-m47-m48: the page showed the term `parameter` on lines 8 and
    47, and the landing wrote the row on line 8 alone. The judge read "line
    47: no ruling" though the call gave a word for every line. Each line of
    the row now lands its own row, keyed by the line number (pass 5)."""
    ask = _page(db, refs=("calculate_tip", "s1", "l_1", "l_1"))
    order = list(ask.order)
    assert order.count("l_1") == 2, order
    lines = [n for n, r in enumerate(order, 1) if r == "l_1"]
    sb, _ = _seat(db, ask, words="Drop the note, both times. The rest is fine.")
    call = {str(n): "approve" for n in range(1, len(order) + 1)}
    call.update({str(n): "drop" for n in lines})
    sb.call("rulings.rule", rulings=call)
    rows = [w[2] for w in sb.ctx.writes if w[0] == "ruled_refs"
            and w[2]["ref"] == "l_1"]
    assert sorted(r["line"] for r in rows) == lines
    assert {(r["verdict"], r["act"]) for r in rows} == {("contest", "drop")}
    assert len({r["id"] for r in rows}) == 2
    _commit(db, sb)
    landed = db.execute("SELECT line FROM ruled_refs WHERE ref = 'l_1' AND "
                        "source = 'reading'").fetchall()
    assert sorted(r[0] for r in landed) == lines


# Pass 7: on a touch line the seat writes `exclude` and the paths to take
# off. On "keep line 5 to the terminal module" his words name the paths he
# keeps, so code reads no path from his words. Code checks each seat path
# against the line, a fact.
M77 = "L3R-n172-m76-m77"
M77_OTHERS = {"1": "approve", "2": "approve", "3": "approve", "4": "approve",
              "6": "approve"}


def _case_seat(tmp_path, case_id: str):
    """The seat of one L3 case, woken on his reply, with the page he saw."""
    from rota.core.db import init_db
    from rota.core.sandbox import build
    from rota.roles import prompts
    from rota.testkit import fixtures

    case = fixtures.for_run(
        {c["id"]: c for c in fixtures.load_case(CASES)}[case_id], 1)
    conn = init_db(tmp_path / "case.db")
    fixtures.seed(conn, case["fixture"])
    reply = fixtures.seed_inbound(conn, case)
    conn.commit()
    sb = build("liaison", conn, mode="normal", session_id="s_seam",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = reply
    return sb, fixtures._page_as_seen(case)


def test_the_exclude_suffix_names_paths_of_the_line():
    shown = ["src/click/utils.py", "tests/test_utils.py", "src/click/termui.py"]
    assert api._excluded_paths("utils.py", shown) == ["src/click/utils.py"]
    assert api._excluded_paths("src/click/termui.py, tests/test_utils.py",
                               shown) == ["src/click/termui.py",
                                          "tests/test_utils.py"]
    assert api._excluded_paths("`termui.py` and test_utils.py", shown) == [
        "src/click/termui.py", "tests/test_utils.py"]
    # A path that ends no shown path, or that two end with, names none.
    assert api._excluded_paths("core.py", shown) is None
    assert api._excluded_paths("utils.py", shown + ["src/x/utils.py"]) is None


def test_a_path_off_the_line_is_refused_with_the_lines_paths(tmp_path):
    sb, page = _case_seat(tmp_path, M77)
    for given, said in (("exclude src/click/core.py",
                         "'src/click/core.py' is not a path of line 5"),
                        ("exclude", "exclude names the paths to take off")):
        with page, pytest.raises(ValueError) as e:
            sb.call("rulings.rule", rulings={**M77_OTHERS, "5": given})
        assert said in str(e.value)
        assert ("Line 5 lists src/click/_compat.py, src/click/termui.py, "
                "tests/test_basic.py") in str(e.value)
    assert not [w for w in sb.ctx.writes if w[0] == "rulings"]


def test_two_paths_land_two_excludes_with_his_words(tmp_path):
    """"keep line 5 to the terminal module" names the paths he keeps. The
    seat names the others, and each one lands its own exclude."""
    sb, page = _case_seat(tmp_path, M77)
    with page:
        sb.call("rulings.rule", rulings={
            **M77_OTHERS, "5": "exclude tests/test_defaults.py, test_options.py"})
    rows = [w[2] for w in sb.ctx.writes if w[0] == "ruled_refs"
            and w[2]["ref"] == "bg_2"]
    assert [(r["verdict"], r["act"], r["target_kind"], r["target"], r["line"])
            for r in rows] == [
        ("contest", "exclude", "path", "tests/test_defaults.py", 5),
        ("contest", "exclude", "path", "tests/test_options.py", 5)]
    assert len({r["id"] for r in rows}) == 2
    assert all("keep line 5 to the terminal module" in r["words"] for r in rows)


def test_exclude_on_a_criterion_line_is_refused_with_its_kind(tmp_path):
    sb, page = _case_seat(tmp_path, M77)
    with page, pytest.raises(ValueError) as e:
        sb.call("rulings.rule", rulings={
            "1": "approve", "2": "exclude", "3": "approve", "4": "approve",
            "5": "approve", "6": "approve"})
    assert str(e.value).startswith("line 2 is a criterion, and it lists no files")


def test_two_excludes_on_one_line_both_count_after_the_land(tmp_path):
    """Pass 7b: the readers kept one row per ref, so after the land only
    the last path counted as excluded. An exclude now keeps a row per path."""
    from rota.core.runner import disputed_paths
    from rota.roles.principal import apply_rulings, ruled

    sb, page = _case_seat(tmp_path, M77)
    with page:
        sb.call("rulings.rule", rulings={
            **M77_OTHERS, "5": "exclude tests/test_defaults.py, test_options.py"})
    conn = sb.ctx.conn
    _commit(conn, sb)
    apply_rulings(conn)
    conn.commit()
    landed = conn.execute("SELECT act, target FROM ruled_refs WHERE ref = "
                          "'bg_2' AND source = 'landed' ORDER BY rowid")
    assert [tuple(r) for r in landed] == [
        ("exclude", "tests/test_options.py"),
        ("exclude", "tests/test_defaults.py")]
    assert sorted(r["target"] for r in ruled(conn, ["bg_2"])) == [
        "tests/test_defaults.py", "tests/test_options.py"]
    assert sorted(r["target"] for r in ruled(conn, ["bg_2"], newest=True)) == [
        "tests/test_defaults.py", "tests/test_options.py"]
    assert disputed_paths(conn, "bg_2", ["tests/test_defaults.py",
                                         "tests/test_options.py",
                                         "tests/test_termui.py"]) == [
        "tests/test_defaults.py", "tests/test_options.py"]


def test_two_words_on_one_ref_of_another_act_keep_one_row(db):  # noqa: F811
    """A drop on two lines of one row still reads as one row per ref."""
    from rota.roles.principal import apply_rulings, ruled

    ask = _page(db, refs=("calculate_tip", "s1", "l_1", "l_1"))
    lines = [n for n, r in enumerate(ask.order, 1) if r == "l_1"]
    sb, _ = _seat(db, ask, words="Drop the note, both times. The rest is fine.")
    call = {str(n): "approve" for n in range(1, len(ask.order) + 1)}
    call.update({str(n): "drop" for n in lines})
    sb.call("rulings.rule", rulings=call)
    _commit(db, sb)
    apply_rulings(db)
    db.commit()
    rows = ruled(db, ["l_1"])
    assert [(r["verdict"], r["act"]) for r in rows] == [("contest", "drop")]


def test_a_path_name_entry_matches_in_both_forms():
    """Pass 7c: the seat copied `path::name` entries in 12 of 34 refusals.
    `exclude path::name` names that entry, and `exclude path` names its
    file."""
    shown = ["src/click/utils.py", "tests/test_formatting.py"]
    entries = ["src/click/utils.py::make_str",
               "tests/test_formatting.py::test_global_show_default"]
    assert api._excluded_paths("src/click/utils.py::make_str", shown,
                               entries) == ["src/click/utils.py::make_str"]
    assert api._excluded_paths("test_formatting.py::test_global_show_default",
                               shown, entries) == [
        "tests/test_formatting.py::test_global_show_default"]
    assert api._excluded_paths("src/click/utils.py, src/click/utils.py::make_str",
                               shown, entries) == [
        "src/click/utils.py", "src/click/utils.py::make_str"]
    # A name that the line does not show names no entry.
    assert api._excluded_paths("src/click/utils.py::other", shown,
                               entries) is None


def test_both_forms_land_on_a_line_of_path_name_entries(tmp_path):
    """L3R-n170-m74-m75: line 3 lists tests/test_formatting.py by its
    test entries."""
    for given, target in (
            ("exclude tests/test_formatting.py::test_global_show_default",
             "tests/test_formatting.py::test_global_show_default"),
            ("exclude tests/test_formatting.py", "tests/test_formatting.py")):
        sb, page = _case_seat(tmp_path / target.replace(":", "_").replace("/", "_"),
                              "L3R-n170-m74-m75")
        with page:
            sb.call("rulings.rule", rulings={"1": "approve", "2": "approve",
                                             "3": given, "4": "approve"})
        rows = [w[2] for w in sb.ctx.writes if w[0] == "ruled_refs"
                and w[2]["ref"] == "b_3"]
        assert [(r["act"], r["target"]) for r in rows] == [("exclude", target)]


# These tests pin the doors of the word form of a page call. Pass R2
# retires the doors and these pins (frame 345, the R1 brief, step 5).
pytestmark = pytest.mark.usefixtures("old_page_form")
