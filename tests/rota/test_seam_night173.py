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
WORKTREE = Path(__file__).resolve().parents[2] / ".rota"


def _home(n):
    """The store that holds night `n`'s register: the main one, or the
    worktree's own, where a newer night's copy can sit."""
    return HOME if (HOME / f"clickI_night{n}.db").exists() else WORKTREE

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
FORMATTING = ("tests/test_formatting.py::test_global_show_default, "
              "tests/test_formatting.py::test_truncating_docstring, "
              "tests/test_formatting.py::test_truncating_docstring_no_help")


@pytest.fixture
def night(tmp_path):
    def at(n, trigger, merged=True):
        """A copy of night `n`'s register at the call on `trigger`: his
        rulings from `trigger` on gone, the asked page open, and his later
        answers gone. `merged` False puts bg_2 back before its build."""
        src = _home(n) / f"clickI_night{n}.db"
        if not src.exists():
            pytest.skip(f"the night {n} register is not on this machine")
        # The copy comes first, so the test never opens the night's file.
        for ext in ("db", "db-wal", "db-shm"):
            part = _home(n) / f"clickI_night{n}.{ext}"
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


# W16: a removal of code lands only on his removal request.

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


# Seam pass 3b: a touch-list correction is its own act, `exclude`.

def _landed(conn, ref, acts):
    from rota.core.db import backfill_ruled_refs
    from rota.testkit.fixtures import seed_acts
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                 "verb, body_refs, seq) VALUES ('ask_x', 'th', 'liaison', "
                 "'principal', 'present', ?, 1)", (f'["{ref}"]',))
    conn.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) "
                 "VALUES ('r_x', 'ask_x', ?, 'Line 2 names the wrong tests', "
                 "'landed')", (f'{{"{ref}": "contest"}}',))
    backfill_ruled_refs(conn)
    seed_acts(conn, "r_x", acts)
    conn.commit()


def test_an_exclude_row_grants_no_removal_of_the_path(tmp_path):
    from rota.core.db import init_db
    from rota.core.runner import disputed_paths
    from rota.roles.principal import granted
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind) VALUES ('it_1', "
                 "'confirm reads its default', 'in_scope')")
    conn.execute("INSERT INTO batches (id, item_id) VALUES ('bg_2', 'it_1')")
    path = "tests/test_defaults.py"
    _landed(conn, "bg_2", {"bg_2": {"act": "exclude", "target_kind": "path",
                                    "target": path,
                                    "words": "Line 2 names the wrong tests"}})
    assert granted(conn, "bg_2", "exclude", path)
    assert not granted(conn, "bg_2", "remove", path)
    assert disputed_paths(conn, "bg_2", [path, "src/click/termui.py"]) == [path]


def test_an_older_register_takes_the_act_exclude(night):
    """`init_db` widens the CHECK of a register built before the act."""
    from rota.core.db import _widen_ruled_ref_acts
    conn = night(173, "m62").conn
    before = conn.execute("SELECT COUNT(*) FROM ruled_refs").fetchone()[0]
    _widen_ruled_ref_acts(conn)
    sql = conn.execute("SELECT sql FROM sqlite_master WHERE name = "
                       "'ruled_refs'").fetchone()[0]
    assert "'exclude'" in sql
    assert conn.execute("SELECT COUNT(*) FROM ruled_refs").fetchone()[0] == before
    assert {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE tbl_name = 'ruled_refs'")} >= {
        "ruled_refs", "ruled_refs_by_ref", "ruled_refs_never_change"}
    conn.execute("SELECT COUNT(*) FROM ruled_refs_live").fetchone()


# Night 174's m55, his reply on page m53, and s175 call 3's span, copied
# here so the test reads no register (the seam review, p4-3).
M55 = ("Line 9 misreads me: I asked to remove the string helper in the utils "
       "file and keep the clear function, and I asked to add to line 3, not "
       "to remove it. Line 7 should say the change touches the clear function "
       "in the terminal UI file for certain, not only that it might. Lines 2 "
       "to 6 and line 8 are fine.")
S175_3 = ("the change touches the clear function in the terminal UI file for "
          "certain, not only that it might")


def test_a_clause_starts_after_should_say():
    """s175 call 3 copied his words after "Line 7 should say" to the
    clause end, and the door refused them."""
    assert api._holds_clauses(M55, S175_3)


@pytest.mark.parametrize("target, span, stems", [
    ("tests/test_options.py", "the options and defaults test files", True),
    ("tests/test_defaults.py", "not the defaults test file", True),
    ("tests/test_defaults.py", "Lines 2 to 4 are still wrong", False),
    ("clear", "the clear function", False),
    # The review's p5-2: a stem names a path only beside a kind word.
    ("src/click/termui.py", "the termui tests", False),
    ("tests/test_termui.py", "the termui source must change", False),
    ("src/click/core.py", "the core of the change is the flag", False),
    ("src/click/utils.py", "put the new tests with the other utils tests",
     False),
])
def test_an_exclude_needs_the_path_in_his_words(target, span, stems):
    """p4-2, p4-4 and p5-2: the span names the file, and the target is a
    path."""
    assert api._names_path(span, target) is stems


@pytest.mark.parametrize("text, span, holds", [
    ("Line 7 should say the change is certain.", "the change is certain", True),
    ("Change line 7 to say X runs.", "X runs", True),
    ("I did not say the change is certain.", "the change is certain", False),
    ("Line 7 should say the change is certain.", "change is certain", False),
])
def test_a_report_verb_starts_a_clause(text, span, holds):
    assert api._holds_clauses(text, span) is holds


def test_the_span_refusal_names_the_nearest_clause():
    assert api._clause_start_near(
        "Line 7 should say the change is certain, not only that it might.",
        "the change is") == "the change is certain"


# Frame 345, pass 2c: the revise door and the read-back door read the match,
# the words of his that name each line, never a cue of his reply.

def test_the_read_back_line_named_by_the_other_lines_takes_an_approve(night):
    """n173-m90-m91: "The other lines are fine" names line 23, the read-back
    line. The door refused its approve 21 times at 1eb5c557."""
    ctx = night(173, "m91")
    words = api.line_words(principal_said(ctx), 24)
    assert words[23] == "The other lines are fine, and the code stays the same."
    rulings = {str(n): A for n in range(1, 24)}
    rulings.update({str(n): "drop" for n in range(11, 23)})
    # The menu form (frame 345, R6): line 23 is the read-back line.
    rulings["23"] = "ok"
    rulings["24"] = "rewrite"
    api.rulings_rule(ctx, rulings=rulings)
    assert any(r["line"] == 23 and r["verdict"] == "approve"
               for r in _rows(ctx).values())


def principal_said(ctx):
    from rota.roles.principal import said
    return said(ctx.conn, ctx.trigger)


def test_s179s_call_without_the_act_lands_the_contest(night):
    """Night 173, m62: the contest of the change's line 5 lands on bg_2. The
    menu form keys it rewrite, so the row carries that act (frame 345,
    R6b)."""
    ctx = night(173, "m62", merged=False)
    api.rulings_rule(ctx, rulings={"1": A, "2": A, "3": A, "4": A,
                                   "5": "rewrite", "6": A})
    row = _rows(ctx)["bg_2"]
    assert (row["verdict"], row.get("act")) == ("contest", "rewrite")


def test_a_revise_on_a_line_with_no_words_is_refused_once(night):
    """n174-m53-m55: no words of m55 name line 1. The menu form refuses a
    change of line 1 on every call, not once (frame 345, R6b; review p9c)."""
    ctx = night(174, "m55", merged=False)
    assert api.line_words(principal_said(ctx), 9)[1] is None
    ctx.refusals = []
    for _ in range(2):
        with pytest.raises(ValueError) as e:
            api.rulings_rule(ctx, rulings={"1": "rewrite", "rest": "approve"})
        assert str(e.value).startswith("line 1: no clause of his names line 1")
        ctx.refusals.append(("rulings.rule", str(e.value), "ValueError"))
