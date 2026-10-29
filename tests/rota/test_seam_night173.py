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


def _folded(rulings: dict, acts: dict) -> dict:
    """The object form of a night's call that kept its act in the flat
    `acts` map. Frame 345's pass 2 refuses that map, and the object form
    writes the same rows (the seam design, 2.1)."""
    return {**rulings, **{k: {"verdict": rulings[k], **v}
                          for k, v in acts.items()}}


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


def test_s179s_call_with_no_target_kind_is_refused(night):
    """The review's p2-2: the target's shape decides, never the kind."""
    ctx = night(173, "m62", merged=False)
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={
            "1": A, "2": A, "3": A, "4": A, "6": A,
            "5": {"verdict": "contest", "act": "remove",
                  "target": "src/click/termui.py:clear", "words": S62}})
    assert str(e.value) == _no_removal(5, S62, "src/click/termui.py:clear")


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
        api.rulings_rule(ctx, rulings=_folded(
            {"1": A, "2": A, "3": "contest"},
            {"3": {"act": "remove", "target_kind": "source_line",
                   "target": target, "words": span}}), words=W75)
    assert str(e.value) == _no_removal(3, span, target)


def test_s222s_call_on_m97_is_refused_on_line_2s_act(night):
    """m97 says only the docstring changes. "drop all three formatting
    tests" names no test of the target, so r_m97 grants nothing."""
    ctx = night(170, "m97")
    span = "please drop all three formatting tests"
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings=_folded({
            "1": A, "2": "contest", "3": "contest", "4": A, "5": "contest",
            "6": A, "7": A, "9": "contest"},
            {"2": {"act": "drop", "target_kind": "path", "target": FORMATTING,
                   "words": span}}), words=W97)
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


def test_a_change_request_backs_the_revise(night, monkeypatch):
    """The review's p2-1: "Replace Roaming in line 4 with Local." faults no
    line, and it asks to change line 4, so the revise lands."""
    from rota.roles import principal

    said = W35.replace(
        "because I approved two lines, lines 1 and 4, not one.",
        "because it misses a line. Replace Roaming in line 4 with Local.")
    orig = principal.said
    monkeypatch.setattr(principal, "said", lambda conn, mid, *a, **k: (
        said if mid == "m35" else orig(conn, mid, *a, **k)))
    ctx = night(173, "m35")
    api.rulings_rule(ctx, rulings={"1": A, "2": "contest", "3": "contest",
                                   "4": "revise", "5": A, "6": A,
                                   "7": "contest", "8": "drop"}, words=said)
    assert _rows(ctx)["c_3"]["verdict"] == "revise"


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


# Seam pass 3c: the review's p3-1, p3-4 and p3-5.

def test_s179s_call_with_no_target_is_refused(night):
    """A removal with no target skipped the removal rule, and `grant` with
    no target read the row as his permission (p3-1)."""
    from rota.roles.principal import grant
    ctx = night(173, "m62", merged=False)
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={
            "1": A, "2": A, "3": A, "4": A, "6": A,
            "5": {"verdict": "contest", "act": "remove",
                  "target_kind": "identifier", "words": S62}})
    msg = str(e.value)
    assert msg == ("line 5: a remove needs its target. Put in `target` the "
                   "code or the line that his words ask to remove")
    assert len(msg.split()) < 25
    assert not ctx.writes
    assert grant(ctx.conn, "bg_2", "remove") is None


@pytest.mark.parametrize("path", ["src/click/core.py", "src/click/termui.py"])
def test_an_exclude_on_a_path_the_line_does_not_show_is_refused(night, path):
    """The words name the terminal UI file, and an exclude still needs the
    contested line to show the path (p3-4)."""
    ctx = night(173, "m62", merged=False)
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings={
            "1": A, "2": A, "3": A, "4": A, "6": A,
            "5": {"verdict": "contest", "act": "exclude",
                  "target_kind": "path", "target": path,
                  "words": S62}})
    assert str(e.value).startswith("line 5: an exclude takes a path off")


# Seam pass 3d: night 174's walk 2, two fact checks of `rulings_rule`.

def _recorded_call(n, sid, k):
    """The trigger and the arguments of call `k` to rulings.rule in session
    `sid` of night `n`, read from a read-only copy of the register."""
    from rota.llm.toolproto import ToolCall, extract
    src = _home(n) / f"clickI_night{n}.db"
    if not src.exists():
        pytest.skip(f"the night {n} register is not on this machine")
    conn = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
    trigger = conn.execute("SELECT trigger_msg FROM sessions WHERE id = ?",
                           (sid,)).fetchone()[0]
    calls = [f.args for (comp,) in conn.execute(
        "SELECT completion FROM turns WHERE session_id = ? ORDER BY seq", (sid,))
        for f in extract(comp or "")
        if isinstance(f, ToolCall) and f.name == "rulings.rule"]
    conn.close()
    return trigger, calls[k - 1]


def test_a_ref_on_two_lines_takes_its_act_on_either_line(night):
    """m47 shows `parameter` on lines 8 and 47. s168 call 3 keys its act
    "8", and the door refused it as a key rulings did not hold. The call's
    flat `acts` map is folded into the object form (frame 345, pass 2)."""
    trigger, args = _recorded_call(174, "s168", 3)
    ctx = night(174, trigger)
    acts = args.pop("acts")
    args["rulings"] = _folded(args["rulings"], acts)
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, **args)
    assert "acts has the key" not in str(e.value)
    # The span check reads next, and "Drop lines 8 to 67" is not his.
    assert str(e.value).startswith("line 8: the act drop rests on")


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


L23 = ("Lines 2 and 3 are wrong: with the roaming flag on, only the roaming "
       "app data variable being unset should matter, and with it off, only "
       "the local app data variable being unset should matter. ")
L8 = (" Line 8 is a misread, since I never sent an empty answer, so please "
      "drop it.")


@pytest.mark.parametrize("middle, lands", [
    ("Line 7 is slightly off. Line 4 should say the local variable matters.",
     True),
    ("Line 7 is slightly off. I never said line 4 should say the local "
     "variable matters.", False),
    ("Line 7 is slightly off. Line 4 is fine, and it is wrong to say the "
     "local variable matters.", False),
    # The review's p5-1: the clause opens with "though some say".
    ("Line 7 is slightly off. Line 4 is fine, though some say line 4 has to "
     "say the local variable matters.", False),
])
def test_a_say_clause_follows_a_line_reference(night, monkeypatch, middle,
                                               lands):
    """The review's probe 6 on m35: a cut after "say" needs a named line
    and no negation or fault before it (p4-1)."""
    from rota.roles import principal

    said = L23 + middle + L8
    orig = principal.said
    monkeypatch.setattr(principal, "said", lambda conn, mid, *a, **k: (
        said if mid == "m35" else orig(conn, mid, *a, **k)))
    ctx = night(173, "m35")
    call = dict(rulings=_folded(
        {"1": A, "2": "contest", "3": "contest", "4": "revise", "5": A,
         "6": A, "7": "contest", "8": "drop"},
        {"4": {"act": "rewrite", "target_kind": "row",
               "words": "the local variable matters"}}), words=said)
    if lands:
        api.rulings_rule(ctx, **call)
        assert _rows(ctx)["c_3"]["act"] == "rewrite"
    else:
        with pytest.raises(ValueError):
            api.rulings_rule(ctx, **call)


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

M55_RULINGS = {"1": A, "2": A, "3": A, "4": A, "5": A, "6": A, "7": "revise",
               "8": A, "9": "revise"}


def test_a_revise_on_lines_his_words_name_passes(night):
    """n174-m53-m55: "Change line 7" and "Change line 9" name lines 7 and 9,
    so a revise of each passes the door."""
    ctx = night(174, "m55", merged=False)
    api.rulings_rule(ctx, rulings=dict(M55_RULINGS))
    rows = _rows(ctx)
    assert sorted(r["line"] for r in rows.values()
                  if r["verdict"] == "revise") == [7, 9]


def test_a_revise_on_a_line_with_no_words_is_refused_once(night):
    """No words of m55 name line 1, and his words name other lines. A revise
    of line 1 is refused once, and the same call then lands."""
    ctx = night(174, "m55", merged=False)
    assert api.line_words(principal_said(ctx), 9)[1] is None
    ctx.refusals = []
    call = {**M55_RULINGS, "1": "revise"}
    with pytest.raises(ValueError) as e:
        api.rulings_rule(ctx, rulings=dict(call))
    assert str(e.value) == (
        "line 1: no words of his name line 1. Rule the lines his words name, "
        "and approve or leave out line 1")
    ctx.refusals.append(("rulings.rule", str(e.value), "ValueError"))
    api.rulings_rule(ctx, rulings=dict(call))
    assert any(r["line"] == 1 and r["verdict"] == "revise"
               for r in _rows(ctx).values())


def test_the_read_back_line_named_by_the_other_lines_takes_an_approve(night):
    """n173-m90-m91: "The other lines are fine" names line 23, the read-back
    line. The door refused its approve 21 times at 1eb5c557."""
    ctx = night(173, "m91")
    words = api.line_words(principal_said(ctx), 24)
    assert words[23] == "The other lines are fine, and the code stays the same."
    rulings = {str(n): A for n in range(1, 24)}
    rulings.update({str(n): "drop" for n in range(11, 23)})
    rulings["24"] = "contest"
    api.rulings_rule(ctx, rulings=rulings)
    assert any(r["line"] == 23 and r["verdict"] == "approve"
               for r in _rows(ctx).values())


def principal_said(ctx):
    from rota.roles.principal import said
    return said(ctx.conn, ctx.trigger)


# These tests pin the doors of the word form of a page call. Pass R2
# retires the doors and these pins (frame 345, the R1 brief, step 5).
pytestmark = pytest.mark.usefixtures("old_page_form")
