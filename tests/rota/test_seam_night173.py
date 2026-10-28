"""The rulings seam after night 173: W16 and W9.

W16: an act `remove` or `drop` on code lands only on his removal request.
On m62 he asked to name the clear function, and s179 landed `remove` on it.
W9: a line number in his report of an earlier answer names the earlier
page. On m35, "I approved two lines, lines 1 and 4, not one" faulted lines
1 and 4 of this page, and r_m35 landed a revise on c_3
(`plans/seam-night173-read.md`, sections 1, 4 and 6).

Each case replays one call on a copy of a night register, in the state of
that call. The registers are not tracked, so a clone without them skips
the cases that need them.
"""
from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

import pytest

from rota.roles import api

HOME = Path(__file__).resolve().parents[2] / ".rota"
if not (HOME / "clickI_night173.db").exists():
    HOME = Path("D:/repos/rota/.rota")

A = "approve"

# His replies, word for word from the nights' `messages`.
W62 = ("Lines 1 to 4 are fine. Line 5 is wrong: the change has to touch the "
       "clear function in the terminal UI file, so that function should be "
       "named as expected, not as nothing named. Line 6 read me right, so ok "
       "to that.")
S62 = ("the change has to touch the clear function in the terminal UI file, "
       "so that function should be named as expected, not as nothing named")
W52 = ("Line 2 is wrong: this change should only touch the clear function in "
       "the terminal UI file, not the string helper in the utils file. Line 3 "
       "is fine as long as the output stays the same and only the return "
       "value changes. Line 4 read me right, so ok to that.")
S52 = ("this change should only touch the clear function in the terminal UI "
       "file, not the string helper in the utils file")
W121 = ("Please fix the change instead of giving up: put back the two removed "
        "lines of code, because only the docstring changes and the code stays "
        "the same. Line 12 is wrong, because my last answer was not empty: I "
        "said the example shows both the input path and the short output, and "
        "the removed code must go back. The other lines are fine.")
W75 = ("Line 3 is wrong because only the docstring in the utils file changes, "
       "so please remove the five formatting tests from what you expect to "
       "touch. Lines 1 and 2 are right, and line 4 reads my last answer "
       "correctly.")
W97 = ("Line 2 is wrong because only the docstring in the utils file changes, "
       "so please drop all three formatting tests. Line 5 repeats line 4, and "
       "the check on line 3 can simply be that the docstring shows the "
       "example. Line 9 misread me, because I asked you to remove every "
       "formatting test, not just one.")
W35 = ("Lines 2 and 3 are wrong: with the roaming flag on, only the roaming "
       "app data variable being unset should matter, and with it off, only "
       "the local app data variable being unset should matter. Line 7 is "
       "slightly off, because I approved two lines, lines 1 and 4, not one. "
       "Line 8 is a misread, since I never sent an empty answer, so please "
       "drop it; the rest of the page is fine.")
FORMATTING = ("tests/test_formatting.py::test_global_show_default, "
              "tests/test_formatting.py::test_truncating_docstring, "
              "tests/test_formatting.py::test_truncating_docstring_no_help")


@pytest.fixture
def night(tmp_path):
    def at(n, trigger, merged=True):
        """A copy of night `n`'s register at the call on `trigger`: his
        rulings from `trigger` on gone, the asked page open, and his later
        answers gone. `merged` False puts bg_2 back before its build."""
        src = HOME / f"clickI_night{n}.db"
        if not src.exists():
            pytest.skip(f"the night {n} register is not on this machine")
        # The copy comes first, so the test never opens the night's file.
        for ext in ("db", "db-wal", "db-shm"):
            part = HOME / f"clickI_night{n}.{ext}"
            if part.exists():
                shutil.copy(part, tmp_path / f"n{n}.{ext}")
        conn = sqlite3.connect(tmp_path / f"n{n}.db")
        conn.row_factory = sqlite3.Row
        seq, cause = conn.execute(
            "SELECT seq, cause_id FROM messages WHERE id = ?",
            (trigger,)).fetchone()
        later = [r[0] for r in conn.execute(
            "SELECT id FROM messages WHERE from_role = 'principal' "
            "AND seq >= ?", (seq,))]
        for m in later:
            for (rid,) in conn.execute(
                    "SELECT id FROM rulings WHERE reply_id = ?", (m,)).fetchall():
                conn.execute("DELETE FROM ruled_refs WHERE ruling_id = ?", (rid,))
                conn.execute("DELETE FROM rulings WHERE id = ?", (rid,))
        conn.execute("UPDATE messages SET status = 'open' WHERE id = ?", (cause,))
        conn.execute("DELETE FROM messages WHERE from_role = 'principal' "
                     "AND seq > ?", (seq,))
        if not merged:
            conn.execute("UPDATE batches SET status = 'pending', "
                         "head_commit = NULL WHERE id = 'bg_2'")
        conn.commit()
        return api.Ctx(conn=conn, role="liaison", session_id="sX",
                       trigger=trigger, writes=[], outbound=[])
    return at


def _rows(ctx):
    return {w[2]["ref"]: w[2] for w in ctx.writes if w[0] == "ruled_refs"}


def _no_removal(line, span, target):
    return (f"line {line}: his words {span!r} ask no removal of {target}, so "
            f"leave the act out or copy his words that ask for it")


# W16: a removal of code lands only on his removal request.

def test_s179s_call_on_m62_is_refused_on_line_5s_act(night):
    """s179 call 1 landed r_m62: `remove` on the clear function, where m62
    asks to name it."""
    ctx = night(173, "m62", merged=False)
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={
            "1": A, "2": A, "3": A, "4": A, "6": A,
            "5": {"verdict": "contest", "act": "remove",
                  "target_kind": "source_line",
                  "target": "src/click/termui.py:clear", "words": S62}})
    assert str(e.value) == _no_removal(5, S62, "src/click/termui.py:clear")
    # One sentence under 25 words, beside the span it quotes.
    assert len(str(e.value).replace(repr(S62), "").split()) < 25


def test_s179s_call_without_the_act_lands_the_contest(night):
    ctx = night(173, "m62", merged=False)
    api.rulings_rule(ctx, rulings={"1": A, "2": A, "3": A, "4": A, "5": "contest",
                                   "6": A})
    row = _rows(ctx)["bg_2"]
    assert (row["verdict"], row.get("act")) == ("contest", None)


def test_s165s_call_on_m52_is_refused_on_line_2s_act(night):
    """s165 call 3 landed r_m52, `remove` on the string helper, where m52
    says the change does not touch it. Line 3 is a plain approve here: its
    act rests on a cut of his clause, and that door refuses it first."""
    ctx = night(173, "m52")
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={
            "1": A, "3": A, "4": A,
            "2": {"verdict": "contest", "act": "remove",
                  "target_kind": "source_line",
                  "target": "src/click/utils.py::make_str", "words": S52}},
            words=W52)
    assert str(e.value) == _no_removal(2, S52, "src/click/utils.py::make_str")


def test_r_m121s_call_is_refused_on_line_12s_act(night):
    """r_m121 put `remove` on line 12 on his whole reply, which asks to put
    the removed code back."""
    ctx = night(172, "m121")
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={
            **{str(i): A for i in range(1, 9)},
            "12": {"verdict": "contest", "act": "remove",
                   "target_kind": "source_line",
                   "target": "src/click/utils.py:12", "words": W121}},
            words=W121)
    assert str(e.value) == _no_removal(12, W121, "src/click/utils.py:12")


def test_s192s_call_on_m75_is_refused_on_line_3s_act(night):
    """m75 asks the plan to touch fewer tests. It asks to delete no test,
    so r_m75 grants nothing (the seam review of pass 1, finding 2)."""
    ctx = night(170, "m75")
    span = "remove the five formatting tests from what you expect to touch"
    target = ("tests/test_formatting.py::"
              "test_formatting_with_options_metavar_empty")
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={"1": A, "2": A, "3": "contest"},
                         words=W75,
                         acts={"3": {"verdict": "contest", "act": "remove",
                                     "target_kind": "source_line",
                                     "target": target, "words": span}})
    assert str(e.value) == _no_removal(3, span, target)


def test_s222s_call_on_m97_is_refused_on_line_2s_act(night):
    """m97 says only the docstring changes. "drop all three formatting
    tests" names no test of the target, so r_m97 grants nothing."""
    ctx = night(170, "m97")
    span = "please drop all three formatting tests"
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={
            "1": A, "2": "contest", "3": "contest", "4": A, "5": "contest",
            "6": A, "7": A, "9": "contest"}, words=W97,
            acts={"2": {"verdict": "contest", "act": "drop",
                        "target_kind": "path", "target": FORMATTING,
                        "words": span}})
    assert str(e.value) == _no_removal(2, span, FORMATTING)


@pytest.mark.parametrize("span, target, asks", [
    ("please remove make_str", "src/click/utils.py::make_str", True),
    ("please remove make_str", "src/click/termui.py:clear", False),
    ("Remove `echo` from the loop.", "src/click/termui.py:echo", True),
    ("Please remove the clear function.", "src/click/termui.py:clear", True),
    ("Please do not remove the clear function.", "src/click/termui.py:clear",
     False),
    ("only the docstring changes, so no new test is needed",
     "tests/test_formatting.py::test_global_show_default", False),
    # The review's probes of pass 1, findings 2 to 4.
    ("remove the five formatting tests from what you expect to touch",
     "tests/test_formatting.py::test_formatting_with_options_metavar_empty",
     False),
    ("remove the string helper, not the clear function",
     "src/click/termui.py::clear", False),
    ("please delete it", "src/click/termui.py::clear", False),
    ("keep the clear function, drop nothing", "src/click/termui.py::clear",
     False),
])
def test_a_removal_request_names_its_target(span, target, asks):
    assert api._asks_removal_of(span, target) is asks


# W9: a line number in his report of an earlier answer names the earlier page.

def test_s120s_call_on_m35_lands_with_c_3_approved(night):
    """s120 call 2 was refused on lines 1 and 4, and call 3 then revised
    c_3. His "lines 1 and 4" are lines of the page m24."""
    ctx = night(173, "m35")
    api.rulings_rule(ctx, rulings={"1": A, "2": "contest", "3": "contest",
                                   "4": A, "5": A, "6": A, "7": "contest",
                                   "8": "drop"}, words=W35)
    rows = _rows(ctx)
    assert rows["c_3"]["verdict"] == "approve"
    assert all(r["verdict"] != "revise" for r in rows.values())


def test_s120s_call_3_revise_of_c_3_is_refused(night):
    """s120 call 3 revised c_3, line 4, and his words fault no part of it
    (the seam review of pass 1, finding 7)."""
    ctx = night(173, "m35")
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={"1": A, "2": "contest", "3": "contest",
                                       "4": "revise", "5": A, "6": A,
                                       "7": "contest", "8": "drop"}, words=W35)
    assert str(e.value) == (
        "line 4: a revise rewrites the line, and his words do not fault line "
        "4. Approve line 4, or rule it as his words say")


def test_a_fault_after_the_report_clause_stays_on_this_page(night,
                                                            monkeypatch):
    """The review's probe: "line 4 adds a third" is a clause of this page,
    so the approve of line 4 is refused as at the parent. His reply comes
    through `said`, the one reader, so the probe replaces it there."""
    from rota.roles import principal

    said = W35.replace("I approved two lines, lines 1 and 4, not one.",
                       "I asked for two checks, line 4 adds a third.")
    orig = principal.said
    monkeypatch.setattr(principal, "said", lambda conn, mid, *a, **k: (
        said if mid == "m35" else orig(conn, mid, *a, **k)))
    ctx = night(173, "m35")
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={"1": A, "2": "contest", "3": "contest",
                                       "4": A, "5": A, "6": A, "7": "contest",
                                       "8": "drop"}, words=said)
    assert str(e.value).startswith('The words fault line 4, "adds"')


# The 10 sentences of the read's section 4, each with the page's line count
# and the numbers of the earlier page (`plans/seam-night173-read.md`). Night
# 171's m17 replays night 170's, and night 173's m12 replays night 172's, so
# 8 texts remain.
EARLIER = [
    # Line 18 sits after the report's clause end, so it is a line of this
    # page (the seam review of pass 1, finding 1).
    ("Line 6 is wrong because I said line 1 is fine, and only lines 18 to 28 "
     "were wrong.", 7, {1}),
    ("I asked to fix the file list in the old line 4, not to drop it, and the "
     "other lines here are right.", 7, {4}),
    ("Line 7 misses that I also said line 8 was wrong, but the rest of it "
     "reads me correctly.", 7, {8}),
    ("For line 7, add that I also said line 8 was wrong;", 7, {8}),
    ("On line 6, I meant that all of lines 13 to 20 don't belong on that page, "
     "and you still haven't told me why those user lines were there.", 6, {13}),
    ("Line 11 is wrong, because my last answer asked for that fix and did not "
     "say line 4 is wrong.", 11, {4}),
    ("Item 2 is a misread: I have not answered anything before this page, so "
     "I never said that line 3 or line 4 is wrong.", 2, {3, 4}),
    ("Line 7 is slightly off, because I approved two lines, lines 1 and 4, "
     "not one.", 8, {1, 4}),
]


@pytest.mark.parametrize("sentence, size, earlier", EARLIER)
def test_an_earlier_pages_number_faults_no_line(sentence, size, earlier):
    reading = api._line_reading(sentence, size)
    assert not earlier & (reading.faulted | reading.named | reading.matched)


@pytest.mark.parametrize("sentence, size, line", [
    ("Line 4 is wrong.", 8, 4),
    # The review's probes of pass 1, finding 1.
    ("I asked for two checks, line 4 adds a third.", 10, 4),
    ("I asked for one test, line 3 adds five.", 10, 3),
    ("I said line 1 is right and line 9 is a made-up answer.", 10, 9),
    ("As I said, line 4 is wrong.", 8, 4),
    ("I mean line 4 is wrong.", 8, 4),
    ("On line 6, I meant that all of lines 13 to 20 don't belong on that page.",
     6, 6),
    ("Line 7 is slightly off, because I approved two lines, lines 1 and 4, "
     "not one.", 8, 7),
    # Night 170's m36 and night 172's m72: the line after the report is a
    # read-back line of this page.
    ("Line 8 is close, but I approved three lines, not two, and line 9 quotes "
     "an empty answer I never gave, so please drop it.", 9, 9),
    ("Line 25 misreads me because I approved four lines and rejected one, and "
     "line 26 quotes an empty answer I never gave, so drop it.", 26, 26),
])
def test_a_line_of_this_page_keeps_its_fault(sentence, size, line):
    assert line in api._line_reading(sentence, size).faulted


def test_a_line_after_his_report_keeps_its_agreement():
    """Night 172's m129: the second "line 4" is this page's line."""
    reading = api._line_reading(
        "my answer asked for that fix and did not call line 4 wrong, so keep "
        "line 4 as it is.", 11)
    assert reading.matched == {4}
