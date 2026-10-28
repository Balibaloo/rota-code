"""
Frame 190, pass 1: the request's own lines lead every page.

Each test rebuilds one night's rows inline, from the night databases read
with `mode=ro&immutable=1` on 2026-10-09: night 133's m118 and m122, and
night 136's bg_2 touch note (m84), its quarantined page (m96) and the agenda
page m399. The night databases are ignored by git. The design is
`plans/frame190-design.md`, sections 2.1, 2.2.3, 2.5 and 2.F.
"""
from __future__ import annotations

import json

import pytest

from rota.core import predicates as P
from rota.core.db import backfill_ruled_refs, init_db
from rota.core.runner import run_session
from rota.core.scheduler import open_tips, tick_agenda, verdict_rows
from rota.llm.llm import Pins, ScriptedBackend
from rota.roles.principal import (
    ACCOUNT_TODAY, TEAM_NOTES, parse_reply, land, pending_asks, render_page,
    request_rows,
)
from rota.testkit.fixtures import seed_provenance, seed_ref
from rota.roles.principal import verdict_for
from rota.testkit.fixtures import seed_verdict

PINS = Pins(model="stub", temperature=0.0)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _statement(db, sid: str, text: str) -> None:
    db.execute("INSERT OR IGNORE INTO entries (id, author, text, ts_order) "
               "VALUES (?, 'principal', ?, 1)", (f"e_{sid}", text))
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
               "status) VALUES (?, ?, 0, ?, ?, 'ratified')",
               (sid, f"e_{sid}", len(text), text))


def _item(db, iid: str, text: str, *, version: int, approval: str = "approved",
          statement: str | None = None, priority: int = 1,
          described: int = 0, provenance: str = "decided") -> None:
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version, "
               "priority, is_description) VALUES (?, ?, 'in_scope', ?, ?, ?, ?, ?)",
               (iid, text, approval, version, version, priority, described))
    seed_provenance(db, "items", iid, provenance)
    if statement:
        seed_ref(db, "items", iid, "statement", statement)


def _criteria(db, item: str, ticket: str, rows) -> None:
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, 'the ticket')",
               (ticket, item))
    for cid, text in rows:
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, ?, ?)",
                   (cid, ticket, text))


def _dispatch(db, wake, call: str) -> str:
    """The wake, run as a Liaison session with a scripted model. Returns
    the id of the present it sent."""
    db.commit()
    out = run_session(db, wake, backend=ScriptedBackend([call, "done"]),
                      pins=PINS, instructions="present")
    assert out.committed, out.errors
    (row,) = db.execute("SELECT id FROM messages WHERE verb = 'present' "
                        "ORDER BY seq DESC LIMIT 1").fetchall()
    return row["id"]


def _reply(db, mid: str, text: str) -> str:
    (ask,) = [a for a in pending_asks(db) if a.message_id == mid]
    reply = land(db, ask, parse_reply(ask, text))
    db.commit()
    return reply


def _landing(db, reply: str, ruling: dict, words: str):
    (wake,) = [w for w in open_tips(db) if w.message_id == reply]
    call = f"TOOL: rulings.rule(rulings={json.dumps(ruling)}, words={words!r})"
    out = run_session(db, wake, backend=ScriptedBackend([call, "done"]),
                      pins=PINS, instructions="land")
    assert out.committed, out.errors
    return out


def _verdict(db, mid: str):
    row = db.execute("SELECT id, status, body_refs FROM messages WHERE cause_id = ? "
                     "AND verb = 'verdict'", (mid,)).fetchone()
    return row, verdict_for(db, row["id"])


# ---------------------------------------------------------------------------
# Night 133: m122, the agenda page of seven seat rows, and m118.
# ---------------------------------------------------------------------------

ITEM_133 = "confirm_default_on_eof"
TEXT_133 = ("Let confirm() take a default_on_eof flag: when stdin is closed it "
            "returns the default instead of aborting. The flag is optional and "
            "defaults to False.")
CRIT_133 = [
    ("cr_1_confirm_eof_default", "When confirm() receives default_on_eof=True and "
     "stdin reaches EOF, it must return the provided default value rather than "
     "raising an exception or aborting."),
    ("cr_2_confirm_eof_stdin_state", "The confirm() function must detect stdin "
     "closure (EOF) when default_on_eof=True and treat this state as a valid input "
     "condition equivalent to user acceptance of the default."),
    ("cr_3_confirm_eof_no_abort", "When stdin is closed with default_on_eof=True, "
     "confirm() must not trigger an abort or error state; it must complete the "
     "confirmation flow by returning the default."),
]
# m122's seven rows, in its ref order: (id, about_ref, about_table, words, author).
M122 = [
    ("l_0941d2316c", "@term:time", "model_areas", "term", "liaison"),
    ("l_102cd4dc7c", "docs/commands.md", "docs/commands.md",
     "Line 2 still shows a short label where the README wording should be", "architect"),
    ("l_29abbd4ce5", "@term:range", "model_areas", "term", "liaison"),
    ("l_4e4997e16b", "@term:shell", "model_areas", "term", "liaison"),
    ("l_4f96b4223f", "docs/commands.md", "docs/commands.md",
     "Line 3 is wrong to say the code doesn't show how users define commands and "
     "options with decorators", "architect"),
    ("l_c8628f6824", "src/click", "model_areas", "source", "liaison"),
    ("l_f2889961f0", "@term:which", "model_areas", "term", "liaison"),
]
M123 = ("I can't approve this page, because none of the seven lines is about my "
        "request and most of them are just single words like \"term\" and \"source\" "
        "that mean nothing to me. Please drop all seven lines. Replace them with one "
        "line saying the confirm prompt gets a new flag that makes it return its "
        "default when stdin is closed instead of aborting, and one line saying the "
        "flag is off by default so nothing changes for people who already use the "
        "prompt.")
S1 = ("Add an echo_json(obj) helper next to echo that prints an object as compact "
      "JSON on one line, followed by a newline.")


@pytest.fixture
def n133(db):
    """Night 133 at s228: bg_1 merged with `delivered:echo_json`, the confirm
    item open at version 2 (its `resliced:` row) with its ticket and three
    criteria, the description `defines_commands_and_options`, and m122's
    seven open rows."""
    _statement(db, "s1", S1)
    _statement(db, "s2", "Let confirm() take a default_on_eof flag: when stdin is "
                         "closed it returns the default instead of aborting.")
    _item(db, "echo_json", S1, version=1, statement="s1")
    _item(db, "defines_commands_and_options", "Users define commands and options "
          "using decorators in Python functions, which Click then uses to parse and "
          "execute command-line inputs.", version=3, statement="s1", described=1)
    _item(db, ITEM_133, TEXT_133, version=2, statement="s2")
    _criteria(db, ITEM_133, "tk_1_confirm_default_on_eof", CRIT_133)
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('bg_1', 'echo_json', "
               "'merged')")
    db.execute("INSERT INTO config (key, value) VALUES ('delivered:echo_json', '1')")
    for lid, about, table, words, author in M122:
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
                   "status, author) VALUES (?, ?, ?, ?, 'open', ?)",
                   (lid, about, table, words, author))
    db.commit()
    return db


def test_the_agenda_page_numbers_the_open_request_first_and_the_seat_rows_after(n133):
    """Night 133, s228's dispatch and s229's turn on m122: seven seat rows
    and no line of the request. m123 asked for the request and could not
    name it. The description and the delivered item are no open request."""
    seven = [r[0] for r in M122]
    want = [ITEM_133] + [c for c, _ in CRIT_133]
    assert request_rows(n133, seven) == want

    (wake,) = tick_agenda(n133, principal_present=True)
    assert list(wake.refs) == seven
    mid = _dispatch(n133, wake, f"TOOL: msg.present_principal(refs={json.dumps(seven)})")
    refs = json.loads(n133.execute("SELECT body_refs FROM messages WHERE id = ?",
                                   (mid,)).fetchone()["body_refs"])
    assert refs == seven + want, "added, never substituted"

    (ask,) = pending_asks(n133)
    page = ask.rendered
    assert ask.order == want + seven
    assert len(set(ask.order)) == len(ask.order), "no row is numbered twice"
    lines = page.splitlines()
    assert lines[:3] == ["Here is what I understand you want, on one page.",
                         "You asked:", f"  1. {TEXT_133}"]
    # No guess exists, so the item's code line is the unnumbered "not
    # guessed" line (frame 298's design, 2.3).
    assert lines[3] == "     The team has not guessed the code this touches yet."
    assert lines[4] == "It must:" and page.count("check: none yet.") == 3
    assert page.index("  4. When stdin is closed") < page.index(TEAM_NOTES) \
        < page.index("  5. term")
    assert "Users define commands" not in page, "a description is no request line"
    assert page.endswith("To change what you asked for, name line 1."), page

    reply = _reply(n133, mid, M123)
    # Every line takes a ruling. The criteria lines approve, and off the
    # sign-off page an approve of a request line travels nowhere.
    ruling = {"1": "revise", "2": "approve", "3": "approve", "4": "approve",
              **{str(n): "contest" for n in range(5, 12)}}
    _landing(n133, reply, ruling, M123)
    verdict, ruled = _verdict(n133, mid)
    assert ruled[ITEM_133] == "revise", "the words land on the item"
    assert not any(c in ruled for c, _ in CRIT_133)
    # A contested note still goes back to the desk that assumed it, by its
    # `about_ref` (ruled: 2026-09-03).
    assert ruled["src/click"] == "contest"
    assert n133.execute("SELECT approval FROM items WHERE id = ?",
                        (ITEM_133,)).fetchone()["approval"] == "contested"
    assert n133.execute("SELECT COUNT(*) n FROM ledger WHERE status = 'open'"
                        ).fetchone()["n"] == 0


def test_the_account_has_its_own_heading_and_no_request_heading(db):
    """Night 133's m118: the account and one row about it, before any
    request. The account stands under its own heading, never under "You
    asked:" (frame 190's design, 2.F, amendment 5)."""
    _item(db, "how_it_works", "The program is a command-line interface toolkit "
          "called Click.", version=5, approval="contested", described=1,
          provenance="observed")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, "
               "author) VALUES ('l_d9ab308557', 'how_it_works', 'items', 'The account "
               "describes how Click works for users, and it is the foundation for all "
               "behaviours.', 'open', 'vision_keeper')")
    db.commit()
    refs = ["how_it_works", "l_d9ab308557"]
    assert request_rows(db, refs) == ["how_it_works"]
    page, order = render_page(db, "present", refs)
    assert ACCOUNT_TODAY in page and "You asked:" not in page
    assert order == refs
    assert page.index(ACCOUNT_TODAY) < page.index(TEAM_NOTES)
    assert "To change what you asked for" not in page


def test_m354_the_observed_account_is_the_project_today(db):
    """Night 150's m354: he contested the account row as the work, "Line 3
    describes Click in general and should instead say what we build". The
    summary stays on the page under a heading that says it is the project
    today (ruled: Roman, 2026-10-17 04:33, frame 264)."""
    _statement(db, "s1", "Add a show_python flag to version_option.")
    _item(db, "show_python", "version_option takes a show_python flag.",
          version=1, approval="draft", statement="s1")
    _item(db, "how_it_works", "Click is a toolkit for command-line "
          "interfaces in Python.", version=2, described=1,
          provenance="observed")
    db.commit()
    page, _ = render_page(db, "present", ["show_python", "how_it_works"])
    assert "What we are building:" not in page, page
    head = page.index(ACCOUNT_TODAY)
    assert page.index("You asked:") < head < page.index("Click is a toolkit")


# ---------------------------------------------------------------------------
# Night 136: bg_2's touch note m84, its quarantined page m96, and m399.
# ---------------------------------------------------------------------------

ITEM_136 = "confirm_with_default_on_eof"
TEXT_136 = ("Let confirm() take a default_on_eof flag: when stdin is closed it returns "
            "the default instead of aborting. The new flag is off by default, so "
            "nothing changes for people who already call confirm.")
CRIT_136 = [
    ("cr_1_confirm_eof_default", "When confirm() is invoked and stdin is closed (EOF), "
     "it must return the provided default value rather than raising an error or "
     "aborting."),
    ("cr_2_confirm_eof_default_behavior", "The confirm() callable must accept a new "
     "keyword argument default_on_eof (boolean) that, when True, enables the "
     "EOF-return-default behavior described in cr_1."),
    ("cr_3_confirm_eof_default_off", "When confirm() is invoked with "
     "default_on_eof=False (or omitted, if False is the default), it must retain its "
     "existing behavior of aborting on EOF."),
]
ITEM_VO = "version_option_show_python"
TEXT_VO = ("Give version_option a show_python flag that appends the running Python "
           "version to the message.")
CRIT_VO = [
    ("c1_version_option_show_python", "When `version_option` is invoked, if the "
     "`show_python` flag is present, the output message must include the running "
     "Python version string."),
    ("c2_version_option_show_python", "The `version_option` callable must accept a "
     "`show_python` boolean parameter that controls whether the Python version is "
     "appended."),
    ("c3_version_option_show_python", "If `show_python` is false or absent, the output "
     "message must not include the running Python version string."),
]
M85 = ("Line 2 names the wrong tests: the confirm prompt's tests live in the terminal "
       "UI test file, not the defaults test file, and that \"might touch\" item is an "
       "unrelated test about default lookup overrides. Everything else looks right.")


@pytest.fixture
def bg2(db):
    """Night 136 at s184: bg_2 pending with no head commit, its item, its
    three criteria, no test, and its three `batch_touch` rows."""
    _statement(db, "s2", "Let confirm() take a default_on_eof flag: when stdin is "
                         "closed it returns the default instead of aborting.")
    _item(db, ITEM_136, TEXT_136, version=2, statement="s2")
    _criteria(db, ITEM_136, "tk_1_confirm_with_default_on_eof", CRIT_136)
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('bg_2', ?, 'pending')",
               (ITEM_136,))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_2', "
               "'tk_1_confirm_with_default_on_eof')")
    for grain, kind, confidence in (
            ("src/click/termui.py", "path", "expected"),
            ("test_lookup_default_override_respected", "symbol", "possible"),
            ("tests/test_defaults.py", "path", "expected")):
        db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, confidence) "
                   "VALUES ('bg_2', ?, ?, ?)", (grain, kind, confidence))
    for grain in ("src/click/termui.py", "tests/test_defaults.py"):
        db.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, 'path')", (grain,))
    db.commit()
    return db


def test_the_touch_note_numbers_the_criteria_and_the_prediction_after_them(bg2):
    """Night 136, s184's dispatch and s185's turn on m85. The note named the
    batch line and no criterion, so the principal could not say that a
    criterion had no test."""
    (wake,) = P.REGISTRY["touch_note"].fn(bg2)
    mid = _dispatch(bg2, wake, f'TOOL: msg.present_principal(refs=["bg_2", "{ITEM_136}"])')
    (ask,) = pending_asks(bg2)
    page = ask.rendered
    crits = [c for c, _ in CRIT_136]
    assert ask.order == [ITEM_136] + crits + ["bg_2"]
    lines = page.splitlines()
    assert lines[:3] == ["Before I build this, here is what I expect to touch.",
                         "You asked:", f"  1. {TEXT_136}"]
    assert page.count("     check: none yet.") == 3
    assert page.index("  4. When confirm() is invoked with") \
        < page.index("The team expects to touch:") < page.index("  5. the work for:")
    assert "(a new file)" not in page, "both predicted files are in the index"
    assert page.endswith("To change what you asked for, name line 1."), page

    # A predicted test file that the index does not hold is marked.
    bg2.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, confidence) "
                "VALUES ('bg_2', 'tests/test_termui_eof.py', 'path', 'expected')")
    page = pending_asks(bg2)[0].rendered
    assert "tests/test_termui_eof.py (a new file)" in page
    assert "src/click/termui.py (a new file)" not in page

    # An "ok" on the note approves no line and wakes nobody.
    reply = _reply(bg2, mid, M85)
    _landing(bg2, reply, {str(n): "approve" for n in range(1, 6)}, M85)
    assert bg2.execute("SELECT status FROM messages WHERE id = ?",
                       (mid,)).fetchone()["status"] == "answered"
    assert bg2.execute("SELECT 1 FROM messages WHERE cause_id = ? AND verb = 'verdict'",
                       (mid,)).fetchone() is None


def test_the_quarantined_page_says_the_team_gave_up_on_a_criterions_test(bg2):
    """Night 136, s200's dispatch on m96: `tests_missing` for bg_2 was
    quarantined at 3 attempts with tests for cr_1 and cr_2 only. The page
    said "Before I build this" and nothing of cr_3."""
    bg2.execute("UPDATE batches SET head_commit = 'aa28d1dcf069c1a776a5f7de5fec6cbc9a1cc03d' "
                "WHERE id = 'bg_2'")
    # m84 went before. A batch is put to the principal once.
    bg2.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, "
                "status, seq) VALUES ('m84', 'm84', 'liaison', 'principal', 'present', ?, "
                "'answered', 1)", (json.dumps(["bg_2", ITEM_136]),))
    for tid, cid, path in (
            ("tst_confirm_eof_returns_default_when_enabled", "cr_1_confirm_eof_default",
             "tests/test_utils/test_confirm_eof.py"),
            ("tst_confirm_eof_returns_default_when_default_on_eof_true",
             "cr_2_confirm_eof_default_behavior",
             "tests/test_utils/test_confirm_eof_behavior.py")):
        bg2.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
                    "(?, 'bg_2', ?, ?, ?)", (tid, cid, path,
                                             "def test_x():\n    assert confirm()\n"))
    bg2.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, reported) "
                "VALUES ('tester|tick:tests_missing|bg_2', 3, 1, 0)")
    (wake,) = P.REGISTRY["quarantined"].fn(bg2)
    assert wake.refs == ("bg_2",)
    mid = _dispatch(bg2, wake, 'TOOL: msg.present_principal(refs=["bg_2"])')
    refs = json.loads(bg2.execute("SELECT body_refs FROM messages WHERE id = ?",
                                  (mid,)).fetchone()["body_refs"])
    assert refs == ["bg_2", ITEM_136] + [c for c, _ in CRIT_136]

    (ask,) = [a for a in pending_asks(bg2) if a.message_id == mid]
    page = ask.rendered
    assert not page.startswith("Before I build this"), page
    assert "The team gave up: the team could not write the tests after 3 attempts." in page
    cr3 = page.index("  6. When confirm() is invoked with")
    assert page[cr3:].splitlines()[1] == (
        "     check: none. The team gave up writing it after 3 tries.")
    assert page.count("check: x, expects confirm(). Not run yet.") == 2
    assert page.index("The team gave up:") < page.index("The team expects to touch:") \
        < page.index("  7. the work for:")
    tests = {"cr_1_confirm_eof_default": "tst_confirm_eof_returns_default_when_enabled",
             "cr_2_confirm_eof_default_behavior":
                 "tst_confirm_eof_returns_default_when_default_on_eof_true"}
    assert ask.order == [ITEM_136] + [r for c, _ in CRIT_136
                                      for r in (c, tests.get(c)) if r] + ["bg_2"]
    # The input names the keys too, and an empty list is no stalled page.
    assert render_page(bg2, "present", refs, stalled=[])[0].startswith("Before I build this")


@pytest.fixture
def m399(db):
    """Night 136 at s537: the constraint row `l_d24f6997d1` open, bg_1 merged
    with `delivered:echo_json`, and two requests open. bg_3 had not merged,
    so the confirm item had no `delivered:` row yet."""
    _statement(db, "s1", S1)
    _statement(db, "s2", "Let confirm() take a default_on_eof flag: when stdin is "
                         "closed it returns the default instead of aborting.")
    _statement(db, "s3", TEXT_VO)
    _item(db, "echo_json", S1, version=3, priority=3, statement="s1")
    db.execute("INSERT INTO config (key, value) VALUES ('delivered:echo_json', '3')")
    _item(db, ITEM_136, TEXT_136, version=2, statement="s2")
    _criteria(db, ITEM_136, "tk_1_confirm_with_default_on_eof", CRIT_136)
    _item(db, ITEM_VO, TEXT_VO, version=4, statement="s3")
    _criteria(db, ITEM_VO, "tk_1_version_option_show_python", CRIT_VO)
    db.execute("INSERT INTO constraints (id, headline, text) VALUES "
               "('parametersource_commandline', 'ParameterSource.COMMANDLINE', "
               "'a value given on the command line')")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, "
               "author) VALUES ('l_d24f6997d1', 'parametersource_commandline', "
               "'constraints', 'The principal contested the constraint due to unclear "
               "requirements, and the approved line refers to a new show python flag on "
               "the version option.', 'open', 'architect')")
    db.commit()
    return db


def test_a_note_about_an_inherited_test_reaches_no_request(db):
    """Night 141's s198 logged two `default` notes about inherited tests.
    An inherited test has no criterion, so the agenda's swap made the ref
    None, and every `frontier` call after that raised (frame 209). The notes
    reach no request, so they ride after the row that does."""
    _statement(db, "s1", "confirm takes a default on EOF")
    _item(db, "i_req", "confirm takes a default on EOF", version=1, statement="s1")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) "
               "VALUES ('bg_2', 'i_req', 'running', 'abc')")
    for tid, path in (("inh_022b8a87", "tests/test_utils/test_confirm.py"),
                      ("inh_c95b73db", "tests/test_defaults.py")):
        db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                   "VALUES (?, 'bg_2', NULL, ?, 'def test_x(): pass')", (tid, path))
    rows = [("l_a94d65762d", "inh_022b8a87", "tests",
             "The test inh_022b8a87 is a project-owned test that passed before "
             "this batch. It has no criterion_id and therefore cannot be challenged."),
            ("l_96c403d182", "inh_c95b73db", "tests",
             "The test inh_c95b73db tests default_map behavior and does not "
             "exercise confirm() with EOF, so it is unaffected by the new parameter."),
            ("l_req", "i_req", "items", "EOF takes the default the caller gave.")]
    for lid, ref, table, text in rows:
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
                   "kind, status, author) VALUES (?, ?, ?, ?, 'default', 'open', "
                   "'developer')", (lid, ref, table, text))
    # s198 was bg_2's Developer. The notes reach no request even through
    # the writer's batch (frame 316's review 2, finding 4).
    db.execute("INSERT INTO sessions (id, role, seq) VALUES ('s198', 'developer', 1)")
    db.execute("INSERT INTO checkpoints (session_id, role, batch_id, working_set) "
               "VALUES ('s198', 'developer', 'bg_2', '[]')")
    for lid in ("l_a94d65762d", "l_96c403d182"):
        db.execute("INSERT INTO receipts (session_id, table_name, row_id, new_version) "
                   "VALUES ('s198', 'ledger', ?, 1)", (lid,))
    db.commit()
    (wake,) = tick_agenda(db, principal_present=True)
    assert wake.refs == ("l_req", "l_a94d65762d", "l_96c403d182")


def test_every_open_request_has_its_own_line(m399):
    """Night 136's m399 held one constraint row. Every open request is
    numbered with its criteria, and the closing sentence names each request
    line (frame 190's design, 2.F, amendment 2)."""
    (wake,) = tick_agenda(m399, principal_present=True)
    mid = _dispatch(m399, wake, 'TOOL: msg.present_principal(refs=["l_d24f6997d1"])')
    (ask,) = [a for a in pending_asks(m399) if a.message_id == mid]
    page = ask.rendered
    assert ask.order == ([ITEM_136] + [c for c, _ in CRIT_136] + [ITEM_VO]
                         + [c for c, _ in CRIT_VO] + ["l_d24f6997d1"])
    assert f"  1. {TEXT_136}" in page and f"  5. {TEXT_VO}" in page
    assert page.count("You asked:") == 1 and "You also asked:" in page
    assert page.index("  8. If `show_python`") < page.index(TEAM_NOTES) \
        < page.index("  9. The principal contested")
    assert page.endswith("To change what you asked for, name its line, 1 or 5."), page


def test_an_ok_off_the_sign_off_page_approves_no_request_line(m399):
    """Night 136's m399 rows with both items contested. An "ok" on an agenda
    page approved the contested item before its owner amended it, night
    133's wall 5. The verdict carries no item and no approved criterion
    (frame 190's design, 2.F, amendment 1)."""
    m399.execute("UPDATE items SET approval = 'contested' WHERE id = ?", (ITEM_VO,))
    m399.execute("UPDATE items SET approval = 'contested' WHERE id = ?", (ITEM_136,))
    (wake,) = tick_agenda(m399, principal_present=True)
    mid = _dispatch(m399, wake, 'TOOL: msg.present_principal(refs=["l_d24f6997d1"])')
    reply = _reply(m399, mid, "ok")
    _landing(m399, reply, {str(n): "approve" for n in range(1, 10)}, "ok")
    verdict, ruled = _verdict(m399, mid)
    assert ruled == {}, ruled
    assert verdict["status"] == "answered", "nothing is left to relay"
    for item in (ITEM_VO, ITEM_136):
        assert m399.execute("SELECT approval FROM items WHERE id = ?",
                            (item,)).fetchone()["approval"] == "contested"
    assert m399.execute("SELECT status FROM ledger WHERE id = 'l_d24f6997d1'"
                        ).fetchone()["status"] == "resolved"


def test_a_contested_criterion_travels_and_an_approved_one_does_not(m399):
    """A contest of one criterion line and approves of the rest. The relay
    carries the contested criterion and no approved one, on a page that is
    no park page (frame 190's design, 2.F, amendment 1)."""
    (wake,) = tick_agenda(m399, principal_present=True)
    mid = _dispatch(m399, wake, 'TOOL: msg.present_principal(refs=["l_d24f6997d1"])')
    words = "line 6 is wrong: the flag prints the version only when it is set"
    reply = _reply(m399, mid, words)
    ruling = {str(n): "approve" for n in range(1, 10)}
    ruling["6"] = "contest"
    _landing(m399, reply, ruling, words)
    verdict, ruled = _verdict(m399, mid)
    assert ruled == {"c1_version_option_show_python": "contest"}
    assert verdict_rows(m399, verdict["id"]) == ["c1_version_option_show_python"]
    assert m399.execute("SELECT approval FROM items WHERE id = ?",
                        (ITEM_VO,)).fetchone()["approval"] == "approved"

    # The criterion goes to its writer, the Terminologist, from a page that
    # is no park page, and keys the repair mode (frame 190's design, 2.2.7;
    # the diff review of 358fed11, finding 3).
    from rota.core.runner import _mode_key
    from rota.core.scheduler import Wake, park_criterion_relay

    (wake,) = [w for w in open_tips(m399) if w.message_id == verdict["id"]]
    call = ('TOOL: msg.relay_terminologist(refs=["c1_version_option_show_python", '
            '"c2_version_option_show_python"])')
    out = run_session(m399, wake, backend=ScriptedBackend([call, "done"]),
                      pins=PINS, instructions="relay")
    assert out.committed, out.errors
    relays = [(r["id"], r["to_role"], json.loads(r["body_refs"])) for r in m399.execute(
        "SELECT id, to_role, body_refs FROM messages WHERE cause_id = ? AND verb = 'relay'",
        (verdict["id"],))]
    assert [(to, refs) for _, to, refs in relays] == [
        ("terminologist", ["c1_version_option_show_python"])]
    assert park_criterion_relay(m399, relays[0][0])
    repair = Wake("terminologist", "message", refs=(), detail="relay",
                  message_id=relays[0][0])
    assert _mode_key(repair, m399) == "criterion_repair"


def test_the_account_page_approves_the_account_and_no_stamped_request(db):
    """Night 133's m212, the account's sign-off page, re-opened with the
    account at draft. The door stamped the open confirm item and its
    criteria, and an "ok" approved the contested item (the diff review of
    358fed11, finding 1). An approve lands on the wake's own rows only."""
    from rota.core.scheduler import Wake

    _statement(db, "s2", "Let confirm() take a default_on_eof flag: when stdin is "
                         "closed it returns the default instead of aborting.")
    _item(db, "how_it_works", "The program is a command-line interface toolkit "
          "called Click.", version=5, approval="draft", described=1,
          provenance="observed")
    _item(db, ITEM_133, TEXT_133, version=8, approval="contested", statement="s2")
    _criteria(db, ITEM_133, "tk_1_confirm_default_on_eof", CRIT_133)
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, "
               "author) VALUES ('l_e7c6ed5501', 'how_it_works', 'items', 'The program "
               "is a command-line interface toolkit called Click.', 'open', "
               "'vision_keeper')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, "
               "status, seq) VALUES ('m211', 'm211', 'vision_keeper', 'liaison', "
               "'submit', ?, 'open', 1)", (json.dumps(["how_it_works"]),))
    wake = Wake("liaison", "message", refs=(), detail="submit", message_id="m211")
    mid = _dispatch(db, wake, 'TOOL: msg.present_principal(refs=["how_it_works"])')
    stamped = [ITEM_133] + [c for c, _ in CRIT_133]
    refs = json.loads(db.execute("SELECT body_refs FROM messages WHERE id = ?",
                                 (mid,)).fetchone()["body_refs"])
    assert refs == ["how_it_works", "l_e7c6ed5501"] + stamped
    assert json.loads(db.execute("SELECT value FROM config WHERE key = ?",
                                 (f"stamped:{mid}",)).fetchone()["value"]) == stamped

    reply = _reply(db, mid, "ok")
    _landing(db, reply, {str(n): "approve" for n in range(1, 7)}, "ok")
    verdict, ruled = _verdict(db, mid)
    assert not set(ruled) & set(stamped), ruled
    row = db.execute("SELECT approval, version FROM items WHERE id = ?",
                     (ITEM_133,)).fetchone()
    assert (row["approval"], row["version"]) == ("contested", 8)
    assert db.execute("SELECT approval FROM items WHERE id = 'how_it_works'"
                      ).fetchone()["approval"] == "approved"


def test_an_items_own_present_approves_it_and_not_its_stamped_criteria(m399):
    """Night 136's m128: the amended echo_json put to the principal with no
    `submit` cause. The item is the wake's own row, so its approve lands,
    and `tick_signoff` does not ask again. Its criteria were stamped, so
    their approve does not (the diff review of 358fed11, finding 2)."""
    from rota.core.scheduler import Wake

    m399.execute("UPDATE items SET version = 4, approval = 'draft' WHERE id = 'echo_json'")
    _criteria(m399, "echo_json", "tk_1", [("c_echo_1", "echo_json prints one line.")])
    wake = Wake("liaison", "tick:agenda", refs=("echo_json",), detail="ledger=1")
    mid = _dispatch(m399, wake, 'TOOL: msg.present_principal(refs=["echo_json"])')
    assert json.loads(m399.execute("SELECT value FROM config WHERE key = ?",
                                   (f"stamped:{mid}",)).fetchone()["value"]) == ["c_echo_1"]
    reply = _reply(m399, mid, "ok")
    (ask,) = [a for a in pending_asks(m399) if a.message_id == mid]
    ruling = {str(n): "approve" for n in range(1, len(ask.order) + 1)}
    _landing(m399, reply, ruling, "ok")
    verdict, ruled = _verdict(m399, mid)
    assert ruled.get("echo_json") == "approve" and "c_echo_1" not in ruled
    row = m399.execute("SELECT approval, approval_ver FROM items "
                       "WHERE id = 'echo_json'").fetchone()
    assert (row["approval"], row["approval_ver"]) == ("approved", 4)


def test_an_open_touch_note_stays_a_touch_note_after_a_key_is_quarantined(bg2):
    """Night 136's m84, the open touch note on bg_2. A key quarantined after
    the send turned the page into the stopped page (the diff review of
    358fed11, finding 4). The page reads the keys its own wake sent."""
    (wake,) = P.REGISTRY["touch_note"].fn(bg2)
    mid = _dispatch(bg2, wake, f'TOOL: msg.present_principal(refs=["bg_2", "{ITEM_136}"])')
    bg2.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, reported) "
                "VALUES ('tester|tick:tests_missing|bg_2', 3, 1, 0)")
    (ask,) = [a for a in pending_asks(bg2) if a.message_id == mid]
    assert ask.rendered.startswith("Before I build this"), ask.rendered
    assert bg2.execute("SELECT 1 FROM config WHERE key = ?",
                       (f"stalled:{mid}",)).fetchone() is None
    # The check lines read the page's keys too. A live read put "gave up"
    # under each criterion (the delta review of 2c602d1b, finding 3).
    assert ask.rendered.count("     check: none yet.") == 3, ask.rendered
    assert "gave up" not in ask.rendered


# ---------------------------------------------------------------------------
# Frame 190, pass 2: the route to the item, the Architect's reply, the slice.
# Rows rebuilt inline from night 136 and night 133, read with
# `mode=ro&immutable=1` on 2026-10-09.
# ---------------------------------------------------------------------------

M400 = ("I can't approve this page. Line one still talks about my complaint and only "
        "mentions the approved line, so it still doesn't say what to build. Please make "
        "line one exactly this: a new show python flag on the version option adds the "
        "running Python version, as major.minor.micro from the interpreter's version "
        "info, to the end of the version message.")
M421_WORDS = ("I can't approve this page. Line one is still about my complaint and says "
              "nothing about what to build. Please replace line one with exactly this: a "
              "new show python flag on the version option adds the running Python version "
              "to the end of the version message, as major.minor.micro from the "
              "interpreter's version info.")


def _sandbox(db, role: str, mode: str, trigger: str):
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = build(role, db, mode=mode, allow=prompts.mode_tools(role, mode))
    sb.ctx.trigger = trigger
    return sb


def _message(db, mid: str, sender: str, to: str, verb: str, refs, cause=None,
             status: str = "answered") -> None:
    seq = db.execute("SELECT COALESCE(MAX(seq), 0) + 1 n FROM messages").fetchone()["n"]
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, verb, "
               "body_refs, status, seq) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (mid, cause, cause or mid, sender, to, verb, json.dumps(refs), status, seq))


def test_a_revise_of_the_item_line_lands_with_the_words_on_the_item(m399):
    """Night 136, s537 on m400. The words named line one, and the page had
    no line of the request, so they landed on a constraint row. The item
    line is now on the page, and a revise of it reaches the Vision Keeper's
    contested wake with the words (frame 190's design, 2.2.1 and 2.2.2)."""
    from rota.core.runner import _resolve_contest

    (wake,) = tick_agenda(m399, principal_present=True)
    mid = _dispatch(m399, wake, 'TOOL: msg.present_principal(refs=["l_d24f6997d1"])')
    reply = _reply(m399, mid, M400)

    # A revise of the team's note is refused. The refusal names the drop
    # first, and names a request line only when the words name it by number
    # or quote it (frame 190's design, 2.F, amendment 2, and frame 296).
    # The words do not name line 9, so the refusal also names the change
    # route of the note (frame 305).
    sb = _sandbox(m399, "liaison", "landing", reply)
    ruling = {str(n): "approve" for n in range(1, 10)}
    ruling["9"] = "revise"
    with pytest.raises(ValueError) as refused:
        sb.call("rulings.rule", rulings=ruling, words=M400)
    assert str(refused.value) == (
        "line 9 is the team's note, not your request. To drop the note, contest "
        "it. To change the note, revise it only on words that name line 9 by number "
        "and say the change. A revise of the request rewrites a line of what the "
        "principal asked for. The words "
        "name no line of the request, and a revise of the request needs the principal's words "
        "on the request.")

    ruling = {str(n): "approve" for n in range(1, 10)}
    ruling["5"], ruling["9"] = "revise", "contest"
    _landing(m399, reply, ruling, M400)
    verdict, ruled = _verdict(m399, mid)
    assert ruled[ITEM_VO] == "revise"
    row = m399.execute("SELECT approval, version FROM items WHERE id = ?",
                       (ITEM_VO,)).fetchone()
    assert (row["approval"], row["version"]) == ("contested", 4)
    woke = _resolve_contest(m399, ITEM_VO)
    assert woke["principal_verdict"] == {ITEM_VO: "revise"}
    assert woke["principal_said"] == M400


def test_the_vision_keepers_relay_cannot_undo_a_revise(m399):
    """Night 136, s172 on m76. The principal revised the confirm item, land
    wrote `contested`, and the relay session set it `approved` twice
    (frame 190's design, 2.2.4)."""
    m399.execute("UPDATE items SET approval = 'contested' WHERE id = ?", (ITEM_136,))
    _message(m399, "m73", "liaison", "principal", "present", [ITEM_136, "echo_json"])
    _message(m399, "m75", "principal", "liaison", "verdict", [ITEM_136, "echo_json"],
             cause="m73")
    seed_verdict(m399, "m75", json.dumps({ITEM_136: "revise", "echo_json": "contest"}))
    _message(m399, "m76", "liaison", "vision_keeper", "relay", [ITEM_136, "echo_json"],
             cause="m75", status="open")
    m399.commit()
    sb = _sandbox(m399, "vision_keeper", "relay", "m76")
    with pytest.raises(ValueError) as refused:
        sb.call("problem.set_approval", id=ITEM_136, approval="approved")
    assert str(refused.value) == (
        f"the principal ruled {ITEM_136} revise. land wrote `contested`, and the "
        "contested wake carries the words. Leave it")
    assert sb.call("problem.set_approval", id=ITEM_136, approval="contested")


def test_a_contest_of_the_prediction_reaches_the_architects_annotate(bg2):
    """Night 136, s185 on m85: "Line 2 names the wrong tests". The door
    refused the batch line five times, and bg_2 built from the wrong
    prediction. Before the build the contest lands, the relay goes to the
    Architect in `annotate`, the touch set is replaced, and the Tester sees
    the corrected path (frame 190's design, 2.2 and question 5.2)."""
    from rota.core.runner import _mode_key, push_working_set, resolve_inbound
    from rota.core.sandbox import build
    from rota.roles import prompts

    (wake,) = P.REGISTRY["touch_note"].fn(bg2)
    mid = _dispatch(bg2, wake, f'TOOL: msg.present_principal(refs=["bg_2", "{ITEM_136}"])')
    reply = _reply(bg2, mid, M85)
    # The Liaison's object form names the file his words call wrong (the
    # seam design, pass 4, P10).
    _landing(bg2, reply, {"1": "approve", "2": "approve", "3": "approve",
                          "4": "approve", "5": {
                              "verdict": "contest", "act": "remove",
                              "target": "tests/test_defaults.py",
                              "words": "Line 2 names the wrong tests"}}, M85)
    verdict, ruled = _verdict(bg2, mid)
    # An approve of the item leaves a touch note's verdict, so the contest
    # of the prediction cannot carry it (the diff review of 2dace61b,
    # finding 4).
    assert ruled == {"bg_2": "contest"}, ruled

    (wake,) = [w for w in open_tips(bg2) if w.message_id == verdict["id"]]
    out = run_session(bg2, wake, backend=ScriptedBackend(
        ['TOOL: msg.relay_architect(refs=["bg_2"])', "done"]), pins=PINS,
        instructions="relay")
    assert out.committed, out.errors
    (relay,) = bg2.execute("SELECT id, to_role, body_refs FROM messages "
                           "WHERE cause_id = ? AND verb = 'relay' "
                           "AND to_role = 'architect'", (verdict["id"],))
    assert (relay["to_role"], json.loads(relay["body_refs"])) == ("architect", ["bg_2"])
    (wake,) = [w for w in open_tips(bg2) if w.message_id == relay["id"]]
    assert _mode_key(wake, bg2) == "annotate"
    shown = resolve_inbound(bg2, wake)
    assert shown["principal_verdict"] == {"bg_2": "contest"}
    # The path his ruling removes leaves `expected`, and the test files of
    # the index are in front of the seat (plans/frame190-interview.md).
    assert shown["touch"]["bg_2"]["expected"] == ["src/click/termui.py"]
    assert shown["touch"]["bg_2"]["disputed"] == ["tests/test_defaults.py"]
    bg2.execute("INSERT INTO code_index (grain, grain_kind) VALUES "
                "('tests/test_termui.py', 'path')")
    sb = build("architect", bg2, mode="annotate",
               allow=prompts.mode_tools("architect", "annotate"))
    sb.ctx.trigger = relay["id"]
    assert push_working_set("architect", sb, wake)["the index's test files"] == [
        "tests/test_defaults.py", "tests/test_termui.py"]

    out = run_session(bg2, wake, backend=ScriptedBackend(
        ['TOOL: batches.annotate(batch_id="bg_2", paths=["src/click/termui.py", '
         '"tests/test_termui.py"])', "done"]), pins=PINS, instructions="annotate")
    assert out.committed, out.errors
    assert {r["grain"] for r in bg2.execute(
        "SELECT grain FROM batch_touch WHERE batch_id = 'bg_2'")} == {
        "src/click/termui.py", "tests/test_termui.py"}

    # The Tester's wake shows the path the principal expects the tests in.
    bg2.execute("UPDATE batches SET status = 'running', head_commit = 'aa28d1d' "
                "WHERE id = 'bg_2'")
    (wake,) = P.REGISTRY["tests_missing"].fn(bg2)
    sb = build("tester", bg2, mode="tests_missing", batch_id="bg_2",
               allow=prompts.mode_tools("tester", "tests_missing"))
    assert push_working_set("tester", sb, wake)["touch"] == ["tests/test_termui.py"]


def test_a_touch_note_approves_no_item_and_a_closed_batch_line_is_refused(bg2):
    """The diff review of 2dace61b, finding 4: on a touch note a contest of
    the batch line kept the verdict, and the approve of the draft item then
    set it approved off the sign-off page. An abandoned batch has no line
    to correct."""
    bg2.execute("UPDATE items SET approval = 'draft' WHERE id = ?", (ITEM_136,))
    (wake,) = P.REGISTRY["touch_note"].fn(bg2)
    mid = _dispatch(bg2, wake, f'TOOL: msg.present_principal(refs=["bg_2", "{ITEM_136}"])')
    reply = _reply(bg2, mid, M85)
    bg2.execute("UPDATE batches SET status = 'abandoned' WHERE id = 'bg_2'")
    sb = _sandbox(bg2, "liaison", "landing", reply)
    ruling = {"1": "approve", "2": "approve", "3": "approve", "4": "approve",
              "5": "contest"}
    with pytest.raises(ValueError, match="bg_2 is the change's line, and the change "
                                         "is abandoned.*contest the item "
                                         f"{ITEM_136}, line 1"):
        sb.call("rulings.rule", rulings=ruling, words=M85)
    bg2.execute("UPDATE batches SET status = 'pending' WHERE id = 'bg_2'")
    _landing(bg2, reply, ruling, M85)
    verdict, ruled = _verdict(bg2, mid)
    assert ruled == {"bg_2": "contest"}, ruled
    assert bg2.execute("SELECT approval FROM items WHERE id = ?",
                       (ITEM_136,)).fetchone()["approval"] == "draft"


def test_a_stalled_key_marks_only_the_criteria_of_its_batch(bg2):
    """The diff review of 2dace61b, finding 5: with the page's batch given,
    every criterion on the page read as given up, another item's
    included."""
    from rota.roles.principal import _gave_up_tries

    _item(bg2, ITEM_VO, TEXT_VO, version=4)
    _criteria(bg2, ITEM_VO, "tk_1_version_option_show_python", CRIT_VO)
    key = "tester|tick:tests_missing|bg_2"
    bg2.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, reported) "
                "VALUES (?, 3, 1, 0)", (key,))
    assert _gave_up_tries(bg2, "cr_3_confirm_eof_default_off", "bg_2", [key]) == 3
    assert _gave_up_tries(bg2, "c1_version_option_show_python", "bg_2", [key]) is None


def test_a_relay_of_a_report_cannot_approve_a_contested_item(db):
    """Night 133's wall 5: s505 on m372, a relay of the Vision Keeper's own
    report m370, set the contested confirm item approved at v8. A relay of
    a principal verdict that approved it at that version still may (the
    diff review of 2dace61b, finding 3)."""
    _statement(db, "s2", "Let confirm() take a default_on_eof flag: when stdin is "
                         "closed it returns the default instead of aborting.")
    _item(db, ITEM_133, TEXT_133, version=8, approval="contested", statement="s2")
    _message(db, "m370", "vision_keeper", "liaison", "report", [ITEM_133])
    _message(db, "m372", "liaison", "vision_keeper", "relay", [ITEM_133], cause="m370",
             status="open")
    db.commit()
    sb = _sandbox(db, "vision_keeper", "relay", "m372")
    with pytest.raises(ValueError, match=f"{ITEM_133} is contested at version 8, and no "
                                         "verdict of the principal approved it"):
        sb.call("problem.set_approval", id=ITEM_133, approval="approved")
    assert sb.call("problem.set_approval", id=ITEM_133, approval="contested")

    _message(db, "m380", "liaison", "principal", "present", [ITEM_133])
    _message(db, "m381", "principal", "liaison", "verdict", [ITEM_133], cause="m380")
    seed_verdict(db, "m381", json.dumps({ITEM_133: "approve"}))
    _message(db, "m382", "liaison", "vision_keeper", "relay", [ITEM_133], cause="m381",
             status="open")
    db.commit()
    sb = _sandbox(db, "vision_keeper", "relay", "m382")
    assert sb.call("problem.set_approval", id=ITEM_133, approval="approved")


ITEM_DEF = "defines_commands_and_options"
CONSTRAINTS_147 = ["constraints:click_context", "constraints:click_log"]


def _night147_relay(db, relay_verdict: dict, relay_refs) -> None:
    """Night 147, walk 2: ruling r_6b1268aa4d on ask m131 approves the item,
    and relay m136 carries only the rows of `relay_verdict`."""
    _item(db, ITEM_133, TEXT_133, version=3)
    _item(db, ITEM_DEF, "Define the commands and the options.", version=1)
    _message(db, "m131", "liaison", "principal", "present",
             [ITEM_133, "challenge_constraints_click_context"])
    _message(db, "m132", "principal", "liaison", "reply", [], cause="m131")
    _message(db, "m133", "principal", "liaison", "verdict", relay_refs, cause="m131")
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, status, "
               "verdict_id) VALUES ('r_6b1268aa4d', 'm131', 'm132', ?, 'landed', "
               "'m133')", (json.dumps({
                   ITEM_133: "approve",
                   "challenge_constraints_click_context": "contest",
                   "challenge_constraints_click_log": "contest"}),))
    backfill_ruled_refs(db)
    # The verdict m133 on the landed ruling, the old `verdict:m133` map
    # (fact F1).
    seed_verdict(db, "m133", json.dumps(relay_verdict), ruling="r_6b1268aa4d")
    _message(db, "m136", "liaison", "vision_keeper", "relay", relay_refs,
             cause="m133", status="open")
    db.commit()


def test_a_relay_cannot_contest_an_item_the_landed_ruling_approved(db):
    """Night 147, s285 on m136. The relay named two constraints. The seat
    contested the approved confirm item, and the scheduler abandoned bg_2
    (frame 238)."""
    _night147_relay(db, {c: "contest" for c in CONSTRAINTS_147}, CONSTRAINTS_147)
    sb = _sandbox(db, "vision_keeper", "relay", "m136")
    with pytest.raises(ValueError) as refused:
        sb.call("problem.set_approval", id=ITEM_133, approval="contested")
    assert str(refused.value) == (
        f"the principal approved {ITEM_133} on m131, ruling r_6b1268aa4d, and this "
        "relay does not name it. Leave it.")
    assert not [w for w in sb.ctx.writes if w[0] == "items"]
    assert db.execute("SELECT approval FROM items WHERE id = ?",
                      (ITEM_133,)).fetchone()["approval"] == "approved"


def test_a_relay_that_names_the_item_with_contest_still_contests_it(db):
    """The relay's own verdict on the id still wins over an older ruling."""
    _night147_relay(db, {ITEM_133: "contest"}, [ITEM_133])
    sb = _sandbox(db, "vision_keeper", "relay", "m136")
    assert sb.call("problem.set_approval", id=ITEM_133, approval="contested") == {
        "id": ITEM_133, "approval": "contested"}


def test_a_wake_that_is_not_a_relay_still_contests_an_approved_item(db):
    """The door reads a relay. A wake of another kind keeps the old rule,
    because no mode but the relay offers the call and names a route."""
    _night147_relay(db, {c: "contest" for c in CONSTRAINTS_147}, CONSTRAINTS_147)
    sb = _sandbox(db, "vision_keeper", "normal", None)
    sb.ctx.wake_kind = "tick"
    sb.ctx.wake_refs = (ITEM_133,)
    assert sb.call("problem.set_approval", id=ITEM_133, approval="contested") == {
        "id": ITEM_133, "approval": "contested"}


def _ruling(db, rid: str, ask: str, per_item: dict, rowid: int | None = None) -> None:
    _message(db, ask, "liaison", "principal", "present", list(per_item))
    db.execute("INSERT INTO rulings (rowid, id, ask_id, per_item, status) "
               "VALUES (?, ?, ?, ?, 'landed')", (rowid, rid, ask, json.dumps(per_item)))
    backfill_ruled_refs(db)
    db.commit()


def test_an_older_ruling_decides_when_the_chains_ruling_does_not_name_the_item(db):
    """Night 147, s285's second call: r_6b1268aa4d does not name the item,
    and the older r_fc68f68228 on m86 approved it (the review of 252feb0e,
    finding 3)."""
    _night147_relay(db, {c: "contest" for c in CONSTRAINTS_147}, CONSTRAINTS_147)
    _ruling(db, "r_fc68f68228", "m86", {ITEM_DEF: "approve"}, rowid=0)
    sb = _sandbox(db, "vision_keeper", "relay", "m136")
    with pytest.raises(ValueError) as refused:
        sb.call("problem.set_approval", id=ITEM_DEF, approval="contested")
    assert str(refused.value) == (
        f"the principal approved {ITEM_DEF} on m86, ruling r_fc68f68228, and this "
        "relay does not name it. Leave it.")


def test_a_newer_ruling_that_contests_the_item_wins_over_the_chains_approve(db):
    """The principal's latest word on the item decides, in rowid order (the
    review of 252feb0e, finding 2)."""
    _night147_relay(db, {c: "contest" for c in CONSTRAINTS_147}, CONSTRAINTS_147)
    _ruling(db, "r_newer", "m150", {ITEM_133: "contest"})
    sb = _sandbox(db, "vision_keeper", "relay", "m136")
    assert sb.call("problem.set_approval", id=ITEM_133, approval="contested") == {
        "id": ITEM_133, "approval": "contested"}


def test_a_relay_with_no_cause_reads_the_newest_landed_ruling(db):
    """A relay with a null cause has no chain, so the newest landed ruling
    on the item decides (the review of 252feb0e, finding 3)."""
    _night147_relay(db, {c: "contest" for c in CONSTRAINTS_147}, CONSTRAINTS_147)
    _message(db, "m137", "liaison", "vision_keeper", "relay", CONSTRAINTS_147,
             status="open")
    db.commit()
    sb = _sandbox(db, "vision_keeper", "relay", "m137")
    with pytest.raises(ValueError) as refused:
        sb.call("problem.set_approval", id=ITEM_133, approval="contested")
    assert str(refused.value) == (
        f"the principal approved {ITEM_133} on m131, ruling r_6b1268aa4d, and this "
        "relay does not name it. Leave it.")


def test_a_relay_that_names_the_item_with_no_ruling_says_so(db):
    """Relay m147 names the item, and its verdict holds no word on it. The
    refusal says what the relay holds (the review of 252feb0e, finding 1)."""
    refs = [ITEM_133, *CONSTRAINTS_147]
    _night147_relay(db, {c: "contest" for c in CONSTRAINTS_147}, refs)
    sb = _sandbox(db, "vision_keeper", "relay", "m136")
    with pytest.raises(ValueError) as refused:
        sb.call("problem.set_approval", id=ITEM_133, approval="contested")
    assert str(refused.value) == (
        f"the principal approved {ITEM_133} on m131, ruling r_6b1268aa4d, and this "
        "relay names it with no ruling of its own. Leave it.")


def test_a_missing_row_on_a_relay_names_the_relays_items_rows(db):
    """When the relay names an item and the call names another id, the
    refusal shows the item (the review of 252feb0e, finding 3)."""
    refs = [ITEM_133, *CONSTRAINTS_147]
    _night147_relay(db, {c: "contest" for c in CONSTRAINTS_147}, refs)
    sb = _sandbox(db, "vision_keeper", "relay", "m136")
    with pytest.raises(ValueError) as refused:
        sb.call("problem.set_approval", id="confirm", approval="contested")
    assert str(refused.value) == (
        "no items row with id='confirm'; this changes an existing row, so the id "
        f"has to be one you were given; the relay names {refs}, and the items rows "
        f"among them are [{ITEM_133!r}]")


def test_a_missing_row_on_a_relay_lists_the_relays_refs(db):
    """Night 147, s285 turn 2 took the first two ids of the table's list.
    On a relay the list names what the relay names (frame 238)."""
    _night147_relay(db, {c: "contest" for c in CONSTRAINTS_147}, CONSTRAINTS_147)
    sb = _sandbox(db, "vision_keeper", "relay", "m136")
    with pytest.raises(ValueError) as refused:
        sb.call("problem.set_approval", id=CONSTRAINTS_147[0], approval="contested")
    assert str(refused.value) == (
        f"no items row with id={CONSTRAINTS_147[0]!r}; this changes an existing row, "
        f"so the id has to be one you were given; the relay names {CONSTRAINTS_147}, "
        "and they are not items rows. Answer what the relay names, or end the session")
    assert ITEM_133 not in str(refused.value)


def test_after_the_head_commit_the_batch_line_is_refused_with_the_item(bg2):
    """Frame 142's door holds after the build for words that do not fault
    the batch line. M85 faults line 2, so the contest of line 5 is refused
    (frame 255)."""
    (wake,) = P.REGISTRY["touch_note"].fn(bg2)
    mid = _dispatch(bg2, wake, f'TOOL: msg.present_principal(refs=["bg_2", "{ITEM_136}"])')
    reply = _reply(bg2, mid, M85)
    bg2.execute("UPDATE batches SET head_commit = 'aa28d1d' WHERE id = 'bg_2'")
    sb = _sandbox(bg2, "liaison", "landing", reply)
    with pytest.raises(ValueError, match="line 5: the words do not fault bg_2's files"):
        sb.call("rulings.rule", rulings={"1": "approve", "2": "approve", "3": "approve",
                                         "4": "approve", "5": "contest"}, words=M85)


@pytest.mark.parametrize("word", ["default", "blocked", "fault"])
def test_a_relay_of_a_ruling_logs_no_row_about_the_ruled_row(m399, word):
    """Night 136, s559 on m422. The Architect logged `l_758e5d392a` about the
    constraint the principal had just contested, and the row was the next
    page. Its `model.adopt` read the id by character (frame 190's design,
    2.3)."""
    seed_provenance(m399, "constraints", "parametersource_commandline", "observed")
    _message(m399, "m419", "liaison", "principal", "present", ["l_d24f6997d1"])
    _message(m399, "m421", "principal", "liaison", "verdict",
             ["parametersource_commandline"], cause="m419")
    seed_verdict(m399, "m421", json.dumps({"l_d24f6997d1": "revise",
                              "parametersource_commandline": "contest"}))
    m399.execute("INSERT INTO config (key, value) VALUES ('entry:m421', ?)",
                 (json.dumps(M421_WORDS),))
    m399.execute("INSERT INTO rulings (id, ask_id, per_item, words, status, verdict_id) "
                 "VALUES ('r_a9da44d357', 'm419', ?, ?, 'landed', 'm421')",
                 (json.dumps({"l_d24f6997d1": "revise"}), M421_WORDS))
    backfill_ruled_refs(m399)
    _message(m399, "m422", "liaison", "architect", "relay",
             ["parametersource_commandline"], cause="m421", status="open")
    m399.commit()
    from rota.core.sandbox import build

    sb = _sandbox(m399, "architect", "relay", "m422")
    # Frame 204: the relay mode no longer offers the call. The door stays
    # as the guard, so a sandbox with the role's whole set still meets it.
    assert "ledger.log" not in sb.functions()
    full = build("architect", m399, mode="relay")
    full.ctx.trigger = "m422"
    with pytest.raises(ValueError) as refused:
        full.call("ledger.log", about_ref="parametersource_commandline",
                  about_table="constraints", kind=word,
                  assumption="The principal's contest on parametersource_commandline "
                             "requires a refactor to align with the new show python "
                             "flag behavior.")
    assert str(refused.value) == (
        "the principal ruled on parametersource_commandline in the relay that woke "
        "you, and their words are on file as their decision. A new assumption about "
        "the same row goes back on their page as your reading of their words. Adopt "
        "what they approved, and stop.")
    assert sb.call("model.adopt", ids="parametersource_commandline") == {
        "adopted": [], "skipped": ["parametersource_commandline"]}

    # Night 136's l_6b81c7417e named the message m145 as its row.
    with pytest.raises(ValueError, match="m419 is a message. An assumption is about "
                                         "a row of the project, never about a message"):
        full.call("ledger.log", about_ref="m419", about_table="principal_verdict",
                  kind=word,
                  assumption="The principal's verdict contests all six observed terms.")
    # Frame 204's review 1, finding L2: a fault or a block met neither guard,
    # so an echo moved to the faults table.
    assert [w for w in full.ctx.writes if w[0] in ("ledger", "faults")] == []


def test_a_one_word_assumption_is_refused(db):
    """Night 136, s87: 53 `ledger.log` calls whose words were one label left
    16 rows on the pages (frame 190's design, 2.3.2)."""
    from rota.core.sandbox import build

    db.execute("INSERT INTO glossary_terms (id, term, sense_short) VALUES "
               "('g_time', 'time', 'the clock')")
    db.commit()
    sb = build("liaison", db, mode="normal")
    with pytest.raises(ValueError) as refused:
        sb.call("ledger.log", about_ref="@term:time", about_table="model_areas",
                assumption="term", kind="gap")
    assert str(refused.value) == (
        "an assumption is a sentence a reader learns from. Name what went unread, "
        "why, and what a reader would get wrong.")


# Frame 204, pass 1: the kinds at the door. The seat names the note's word,
# and the door writes it, refuses it, or routes it (design, sections 7, 8).
NOTE = "the criterion is silent on the separator, so the code takes a comma"


def _log_db(db):
    """One item, ticket, criterion, batch and test for a note to be about."""
    db.execute("INSERT INTO items (id, text, kind) VALUES ('i1', 'print JSON', 'in_scope')")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1', 'i1', 'the ticket')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c1', 'tk1', 'echo_json prints compact JSON')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1', 'i1', 'running')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('tst_1', 'b1', 'c1', 'tests/test_j.py', 'def test_j():\n    assert 1')")
    db.commit()
    return db


def _logs(sb, table="ledger"):
    return [w for w in sb.ctx.writes if w[0] == table]


@pytest.mark.parametrize("word", ["invented", "default", "scope",
                                  "gap", "finding", "other"])
def test_each_word_of_the_grid_is_written_as_its_kind(db, word):
    from rota.core.sandbox import build
    from rota.roles import prompts

    # A mode with `msg.question_vision_keeper` turns a bare `scope` log into
    # that question (frame 204's pass 2), so this mode has no such call.
    sb = build("developer", _log_db(db), mode="normal",
               allow=prompts.mode_tools("developer", "tests_failing"))
    out = sb.call("ledger.log", about_ref="c1", about_table="criteria",
                  assumption=NOTE, kind=word)
    (row,) = _logs(sb)
    assert out == {"id": row[1]}
    assert (row[2]["kind"], row[2]["about_ref"], row[2]["author"]) == (word, "c1", "developer")
    assert _logs(sb, "faults") == []


@pytest.mark.parametrize("word", ["fault", "blocked"])
def test_a_fault_or_a_block_writes_faults_and_no_ledger_row(db, word):
    """95 tool faults and blocks reached the pages on nights 120 to 139, and
    the principal contested 38 of them as assumptions (design, section 1)."""
    from rota.core.db import _apply_write
    from rota.core.runner import _as_write
    from rota.core.sandbox import build
    from rota.roles.api import FAULT_REPLY

    sb = build("terminologist", _log_db(db), mode="normal", session_id="s9")
    sb.ctx.refusals.append(("glossary.adopt", "the row is not yet there", "ValueError"))
    out = sb.call("ledger.log", about_ref="c_missing", about_table="glossary_terms",
                  assumption="the ruling names c_missing and the glossary holds no such row",
                  kind=word)
    assert out["note"] == FAULT_REPLY and out["call"] == "glossary.adopt"
    assert _logs(sb) == []
    (fault,) = _logs(sb, "faults")
    assert fault[2]["kind"] == word and fault[2]["session_id"] == "s9"
    # A ref that names a call is that call.
    out = sb.call("ledger.log", about_ref="model.adopt", about_table="constraints",
                  assumption="the adopt door refused a row that the relay names", kind=word)
    assert out["call"] == "model.adopt"
    for w in _logs(sb, "faults"):
        _apply_write(db, _as_write(w), sb.ctx.role)
    rows = db.execute("SELECT call, status, closed_by, seq FROM faults ORDER BY seq").fetchall()
    assert [tuple(r) for r in rows] == [("glossary.adopt", "open", None, 1),
                                        ("model.adopt", "open", None, 2)]
    assert db.execute("SELECT COUNT(*) FROM ledger").fetchone()[0] == 0


def test_a_conflict_is_offered_as_the_owners_message_when_the_mode_holds_it(db):
    """The two builders story (ruled: Roman, 2026-10-11 15:00): the owner of
    the row answers a conflict before a page does."""
    from rota.core.sandbox import build

    sb = build("developer", _log_db(db), mode="normal")
    with pytest.raises(ValueError) as refused:
        sb.call("ledger.log", about_ref="c1", about_table="criteria",
                assumption="the criterion says compact and the item says pretty-printed",
                kind="conflict")
    assert str(refused.value).startswith(
        "a conflict with c1 is a question for the row's owner, and the owner "
        "answers it before a page does. Send msg.question_terminologist(refs=['c1']")
    assert sb.ctx.offers[0].op == "msg.question_terminologist"
    assert _logs(sb) == []


def test_a_conflict_is_a_row_when_the_mode_holds_no_owners_call(db):
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = build("developer", _log_db(db), mode="normal",
               allow=prompts.mode_tools("developer", "tests_failing"))
    assert "msg.question_terminologist" not in sb.functions()
    sb.call("ledger.log", about_ref="c1", about_table="criteria",
            assumption="the criterion says compact and the item says pretty-printed",
            kind="conflict")
    (row,) = _logs(sb)
    assert row[2]["kind"] == "conflict"


def test_two_words_keep_the_first_by_the_tie_break(db):
    """Section 8: a cell that holds the merge, then a row's owner, then the
    principal, then nobody."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    # No `msg.question_vision_keeper` here, so `scope` stays a row.
    sb = build("developer", _log_db(db), mode="normal",
               allow=prompts.mode_tools("developer", "tests_failing"))
    out = sb.call("ledger.log", about_ref="c1", about_table="criteria",
                  assumption=NOTE, kind="default, invented")
    assert out["kind"] == "invented"
    out = sb.call("ledger.log", about_ref="i1", about_table="items",
                  assumption="the batch leaves out the pretty-print half of the item",
                  kind=["default", "scope"])
    assert out["kind"] == "scope"
    assert [w[2]["kind"] for w in _logs(sb)] == ["invented", "scope"]


def test_a_missing_or_unknown_word_gets_the_three_questions(db):
    from rota.core.sandbox import build
    from rota.roles.api import KIND_QUESTIONS

    sb = build("developer", _log_db(db), mode="normal")
    with pytest.raises(Exception) as missing:
        sb.call("ledger.log", about_ref="c1", about_table="criteria", assumption=NOTE)
    assert KIND_QUESTIONS in str(missing.value)
    with pytest.raises(ValueError) as unknown:
        sb.call("ledger.log", about_ref="c1", about_table="criteria",
                assumption="Adding a parameter to the confirm function signature now",
                kind="trace")
    assert str(unknown.value).startswith("kind='trace' is no word this mode offers. ")
    assert KIND_QUESTIONS in str(unknown.value)
    assert _logs(sb) == []


def test_a_word_the_mode_does_not_offer_is_refused_with_the_modes_words(db):
    from rota.core.sandbox import build
    from rota.roles import prompts

    kinds = prompts.mode_kinds("developer", "batch_start")
    assert kinds == ("invented", "default", "scope", "conflict", "blocked", "fault", "other")
    sb = build("developer", _log_db(db), mode="normal")
    sb.ctx.log_kinds = kinds
    with pytest.raises(ValueError) as refused:
        sb.call("ledger.log", about_ref="c1", about_table="criteria",
                assumption=NOTE, kind="gap")
    assert str(refused.value).startswith("kind='gap' is no word this mode offers.")
    assert str(refused.value).endswith(
        "This mode offers: conflict, scope, invented, default, blocked, fault, other.")
    assert prompts.mode_kinds("liaison", "blindspot") == ("gap", "blocked", "fault", "other")


@pytest.mark.parametrize("word", ["blocked", "fault"])
def test_the_ledger_refuses_a_fault_word(db, word):
    """Frame 204's review 1, finding L5: `blocked` and `fault` live in
    `faults` alone, so a raw writer cannot put a fault on a page."""
    import sqlite3

    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
                   "kind, author) VALUES ('l_x', 'c1', 'criteria', ?, ?, 'developer')",
                   (NOTE, word))


@pytest.mark.parametrize("word", ["blocked", "fault"])
def test_a_fault_names_a_call_and_never_a_row(db, word):
    """Frame 204's review 1, finding L2: a fault with no refusal before it
    wrote the criterion id `c1` as its call."""
    from rota.core.sandbox import build

    sb = build("terminologist", _log_db(db), mode="normal")
    out = sb.call("ledger.log", about_ref="c1", about_table="criteria",
                  assumption="the door failed and the session cannot go on", kind=word)
    assert out["call"] == "unknown"
    (fault,) = _logs(sb, "faults")
    assert fault[2]["call"] == "unknown"


def test_a_second_word_the_mode_does_not_offer_is_dropped_with_a_note(db):
    """Frame 204's review 1, finding L3, in `developer/batch_start`. The
    first word goes through by the tie-break, and the seat hears what the
    door dropped."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = build("developer", _log_db(db), mode="normal")
    sb.ctx.log_kinds = prompts.mode_kinds("developer", "batch_start")
    out = sb.call("ledger.log", about_ref="c1", about_table="criteria",
                  assumption=NOTE, kind="invented, gap")
    assert out["kind"] == "invented"
    assert out["dropped"].startswith("kind='gap' is no word this mode offers")
    out = sb.call("ledger.log", about_ref="i1", about_table="items",
                  assumption="the batch leaves out the pretty-print half of the item",
                  kind="default, banana")
    assert out["kind"] == "default" and "'banana'" in out["dropped"]
    assert [w[2]["kind"] for w in _logs(sb)] == ["invented", "default"]
    # No offered word left: the whole call is refused.
    with pytest.raises(ValueError, match="kind='gap' is no word this mode offers"):
        sb.call("ledger.log", about_ref="c1", about_table="criteria",
                assumption=NOTE, kind="gap, banana")


def test_the_door_text_names_only_the_words_the_mode_offers(db):
    """Frame 204's review 1, finding L4: the questions mapped a Developer to
    `gap` and `finding`, which its mode refuses."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = build("developer", _log_db(db), mode="normal")
    sb.ctx.log_kinds = prompts.mode_kinds("developer", "batch_start")
    with pytest.raises(ValueError) as refused:
        sb.call("ledger.log", about_ref="c1", about_table="criteria",
                assumption=NOTE, kind="trace")
    said = str(refused.value)
    assert "'gap'" not in said and "'finding'" not in said
    assert "'invented'" in said and "'default'" in said


def test_the_tool_schema_carries_the_words_of_the_mode(db):
    """Frame 204's review 1, finding H1: the native schema showed `kind` as
    a bare string."""
    from rota.core.sandbox import build
    from rota.llm.toolschema import schemas_for_sandbox
    from rota.roles import prompts

    sb = build("liaison", db, mode="blindspot",
               allow=prompts.mode_tools("liaison", "blindspot"))
    sb.ctx.log_kinds = prompts.mode_kinds("liaison", "blindspot")
    (log,) = [s for s in schemas_for_sandbox(sb)
              if s["function"]["name"] == "ledger__log"]
    assert log["function"]["parameters"]["properties"]["kind"] == {
        "type": "string", "enum": ["gap", "blocked", "fault", "other"]}


def test_the_relay_modes_offer_no_log_and_the_brief_asks_for_none():
    """221 of 583 notes on nights 120 to 139 were relay wakes that echoed a
    ruling (frame 204's design, section 7)."""
    from rota.roles import prompts

    for role in ("architect", "terminologist"):
        assert "ledger.log" not in prompts.mode_tools(role, "relay"), role
    assert "ledger.log" not in prompts.piece("terminologist", "relay")


def test_an_amended_item_that_is_not_delivered_is_sliced_again(db):
    """Night 133, `confirm_default_on_eof` at version 8 with its one ticket
    from version 2. The amended item kept its old ticket and criteria, and
    `grouping` built from them (frame 190's design, 2.F, amendment 4)."""
    from rota.core.scheduler import tick_criteria, tick_slicing

    _statement(db, "s2", "Let confirm() take a default_on_eof flag: when stdin is "
                         "closed it returns the default instead of aborting.")
    _item(db, ITEM_133, TEXT_133, version=8, statement="s2")
    _criteria(db, ITEM_133, "tk_1_confirm_default_on_eof", CRIT_133)
    db.execute("UPDATE tickets SET item_ver = 2")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('bg_8', ?, 'pending')",
               (ITEM_133,))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_8', "
               "'tk_1_confirm_default_on_eof')")
    db.commit()
    # The live batch goes first: the cancel takes it while the item is not
    # approved, by the ruling of 2026-09-12.
    assert tick_slicing(db) == []
    db.execute("UPDATE batches SET status = 'abandoned' WHERE id = 'bg_8'")
    db.commit()
    (wake,) = tick_slicing(db)
    assert wake.refs == (ITEM_133,)
    out = run_session(db, wake, backend=ScriptedBackend(
        [f'TOOL: tickets.slice(id="tk_2_confirm_default_on_eof", item_id="{ITEM_133}", '
         'text="confirm() returns its default at EOF when default_on_eof is set")',
         "done"]), pins=PINS, instructions="slice")
    assert out.committed, out.errors
    assert db.execute("SELECT item_ver FROM tickets WHERE id = "
                      "'tk_2_confirm_default_on_eof'").fetchone()["item_ver"] == 8
    assert tick_slicing(db) == []
    (wake,) = tick_criteria(db)
    assert wake.refs == (ITEM_133,)
    # The criteria wake sees the live ticket alone, and a criterion on the
    # retired ticket is refused with the live one named (the diff review of
    # 2dace61b, finding 2).
    sb = _sandbox(db, "terminologist", "criteria", None)
    assert [r["id"] for r in sb.call("tickets.scan", item_id=ITEM_133)] == [
        "tk_2_confirm_default_on_eof"]
    with pytest.raises(ValueError, match="tk_1_confirm_default_on_eof is retired.*"
                                         "tk_2_confirm_default_on_eof"):
        sb.call("criteria.specify", id="cr_9", ticket_id="tk_1_confirm_default_on_eof",
                text="confirm() returns the default value when stdin is closed.",
                term_refs=[], surface_refs=[])
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('cr_4', 'tk_2_confirm_default_on_eof', 'confirm() returns the default')")
    assert tick_criteria(db) == []
    (wake,) = P.REGISTRY["grouping"].fn(db)
    assert wake.refs == ("tk_2_confirm_default_on_eof",)
    # The page numbers the new criterion alone (finding 1).
    assert request_rows(db, [ITEM_133]) == [ITEM_133, "cr_4"]
    page, _ = render_page(db, "present", request_rows(db, [ITEM_133]))
    assert "confirm() returns the default" in page
    assert not any(text in page for _, text in CRIT_133), page


def test_a_note_contest_never_overwrites_an_approve_of_a_stamped_criterion(m399):
    """The delta review of 2c602d1b, finding 1, case E: a Terminologist's
    note about c1, every line approved and the note contested. The note's
    contest turned the approve of c1 into a contest."""
    from rota.core.scheduler import Wake

    m399.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, "
                 "author) VALUES ('l_probe_e', 'c1_version_option_show_python', "
                 "'criteria', 'The flag name is taken as show_python.', 'open', "
                 "'terminologist')")
    m399.commit()
    wake = Wake("liaison", "tick:agenda", refs=("l_probe_e",), detail="ledger=1")
    mid = _dispatch(m399, wake, 'TOOL: msg.present_principal(refs=["l_probe_e"])')
    words = "the last line is wrong, the team should not assume the flag name"
    reply = _reply(m399, mid, words)
    (ask,) = [a for a in pending_asks(m399) if a.message_id == mid]
    ruling = {str(n): "approve" for n in range(1, len(ask.order) + 1)}
    ruling[str(ask.order.index("l_probe_e") + 1)] = "contest"
    _landing(m399, reply, ruling, words)
    verdict, ruled = _verdict(m399, mid)
    assert "c1_version_option_show_python" not in ruled, ruled


def test_a_row_the_model_names_is_stamped_and_a_quarantined_batch_is_recorded(bg2):
    """The delta review of 2c602d1b, findings 2 and 4. A contested item the
    model named on an agenda page is no row of the wake, so an approve of
    it lands nothing. A quarantined batch put to the principal by another
    wake records its keys."""
    from rota.core.scheduler import Wake

    bg2.execute("UPDATE items SET approval = 'contested' WHERE id = ?", (ITEM_136,))
    bg2.execute("UPDATE batches SET head_commit = 'aa28d1d' WHERE id = 'bg_2'")
    bg2.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, reported) "
                "VALUES ('tester|tick:tests_missing|bg_2', 3, 1, 0)")
    bg2.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, "
                "author) VALUES ('l_1', 'src/click/termui.py', 'items', 'The prompt "
                "reads one line from stdin.', 'open', 'architect')")
    bg2.commit()
    wake = Wake("liaison", "tick:agenda", refs=("l_1",), detail="ledger=1")
    mid = _dispatch(bg2, wake, f'TOOL: msg.present_principal(refs=["l_1", "{ITEM_136}", '
                               '"bg_2"])')
    stamped = json.loads(bg2.execute("SELECT value FROM config WHERE key = ?",
                                     (f"stamped:{mid}",)).fetchone()["value"])
    assert ITEM_136 in stamped
    assert json.loads(bg2.execute("SELECT value FROM config WHERE key = ?",
                                  (f"stalled:{mid}",)).fetchone()["value"]) == [
        "tester|tick:tests_missing|bg_2"]
    (ask,) = [a for a in pending_asks(bg2) if a.message_id == mid]
    assert not ask.rendered.startswith("Before I build this"), ask.rendered


def test_a_delivered_item_is_no_request_line(m399):
    """The delta review of 2c602d1b, finding 7: a note about a delivered
    criterion put echo_json, delivered at v3, under "You asked:"."""
    _criteria(m399, "echo_json", "tk_1", [("c2", "echo_json prints one line.")])
    assert "echo_json" not in request_rows(m399, ["c2"])


def test_a_repaired_criterion_reaches_the_tester_only_after_a_commit(m399):
    """The delta review of 2c602d1b, finding 5, case G: off the park page the
    batch had not started, and the Tester woke for a question it never
    asked."""
    m399.execute("INSERT INTO batches (id, item_id, status) VALUES ('bg_4', ?, 'pending')",
                 (ITEM_VO,))
    m399.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_4', "
                 "'tk_1_version_option_show_python')")
    _message(m399, "m500", "liaison", "principal", "present",
             [ITEM_VO, "c1_version_option_show_python"])
    _message(m399, "m501", "principal", "liaison", "verdict",
             ["c1_version_option_show_python"], cause="m500")
    seed_verdict(m399, "m501", json.dumps({"c1_version_option_show_python": "contest"}))
    _message(m399, "m502", "liaison", "terminologist", "relay",
             ["c1_version_option_show_python"], cause="m501", status="open")
    m399.commit()
    sb = _sandbox(m399, "terminologist", "criterion_repair", "m502")
    with pytest.raises(ValueError, match="no change built from this criterion has a commit"):
        sb.call("msg.answer_tester", refs=["c1_version_option_show_python"])


# ---------------------------------------------------------------------------
# Frame 213, pass 1: the principal's words about a test reach the Tester
# (`plans/frame213-scope.md`, sections 1 to 3). The rows copy night 144's
# m399 page and night 145's m141 page.
# ---------------------------------------------------------------------------

C1_VO = "c1_version_option_show_python"
TST_VO = "tst_ver_opt_show_py_01"
TST_VO_BODY = ("from click.decorators import version_option\n\n"
               "def test_ver_opt_show_py_01():\n"
               "    result = version_option(show_python=True)\n"
               "    assert result is not None\n")
# Night 145's m142, the principal's words on the m141 page.
M142_WORDS = ("I want this fixed, not dropped. Line 3's check only shows the option "
              "exists, so it should run the version option with the flag on and check "
              "that the message ends with the Python version written as "
              "major.minor.micro.")
# Night 144's m400, the principal's words on the m399 clarify.
M400_WORDS = ("Change the test so it calls the normal version flag, because show_python "
              "is a setting the developer passes to the decorator and not a new flag "
              "that users type.")


def _vo_test(db, batch: str, status: str, head: str | None) -> None:
    """One batch of the version option request with its one test of c1."""
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES (?, ?, ?, ?)",
               (batch, ITEM_VO, status, head))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES (?, "
               "'tk_1_version_option_show_python')", (batch,))
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body, version) "
               "VALUES (?, ?, ?, 'tests/test_ver_opt_show_py_01.py', ?, 1)",
               (TST_VO, batch, C1_VO, TST_VO_BODY))


def _criterion_relay(db, words: str) -> None:
    """Night 145's route A: the m141 page, the verdict m143 that contests c1
    with the principal's words, and the Liaison's relay m144."""
    _message(db, "m141", "liaison", "principal", "present", [ITEM_VO, C1_VO])
    _message(db, "m143", "principal", "liaison", "verdict", [C1_VO], cause="m141")
    seed_verdict(db, "m143", json.dumps({C1_VO: "contest"}))
    n = db.execute("SELECT COALESCE(MAX(ts_order), 0) + 1 n FROM entries").fetchone()["n"]
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m143', 'principal', ?, ?)", (words, n))
    _message(db, "m144", "liaison", "terminologist", "relay", [C1_VO], cause="m143",
             status="open")


def test_the_testers_wake_on_a_repaired_criterion_carries_the_principals_words(m399):
    """Route A, night 145: s272 respecified the criteria and answered the
    Tester with refs alone (m145). The Tester s273 woke with no
    `principal_said` and rewrote the test from the criterion text."""
    from rota.core.runner import resolve_inbound
    from rota.core.scheduler import Wake

    _vo_test(m399, "bg_3", "deferred", "aa28d1d")
    _criterion_relay(m399, M142_WORDS)
    sb = _sandbox(m399, "terminologist", "criterion_repair", "m144")
    # s272 respecified c1 before its answer. Frame 308's door refuses an
    # answer under a contest of the words while no respecify has landed.
    m399.execute("INSERT OR IGNORE INTO code_index (grain, grain_kind, sym_kind) "
                 "VALUES ('src/click/decorators.py::version_option', 'symbol', "
                 "'function')")
    assert sb.call("criteria.respecify", id=C1_VO,
                   text="With show_python on, version_option prints a message "
                        "that ends with the Python version written as "
                        "major.minor.micro.",
                   surface_refs=["src/click/decorators.py::version_option"]
                   ).get("respecified")
    assert sb.call("msg.answer_tester", refs=[C1_VO])["to"] == "tester"
    _message(m399, "m145", "terminologist", "tester", "answer", [C1_VO], cause="m144",
             status="open")
    m399.commit()
    inbound = resolve_inbound(m399, Wake("tester", "message", refs=(), detail="answer",
                                         message_id="m145"))
    assert inbound.get("principal_said") == M142_WORDS
    assert inbound.get("principal_verdict") == {C1_VO: "contest"}
    # The Tester's brief says whose words they are.
    from pathlib import Path

    import rota.roles

    brief = Path(rota.roles.__file__).parent / "prompts" / "tester" / "answer.md"
    assert "principal_said" in brief.read_text(encoding="utf-8")


def test_a_revise_of_a_test_row_travels_to_the_criterions_writer(m399):
    """Route B, night 144's m400: the principal revised the test row of a
    clarify. The relay split knew no owner of a `tests` row, so s577's relay
    went to the Vision Keeper, and no Tester woke."""
    _vo_test(m399, "bg_4", "running", "aa28d1d")
    _message(m399, "m399", "liaison", "principal", "clarify", [C1_VO, TST_VO])
    _message(m399, "m400", "principal", "liaison", "converse", [], cause="m399",
             status="open")
    m399.commit()
    sb = _sandbox(m399, "liaison", "answering", "m400")
    sb.call("rulings.rule", rulings={C1_VO: "approve", TST_VO: "revise"},
            words=M400_WORDS)
    sb.call("msg.relay_vision_keeper", refs=[TST_VO])
    routed = {m["to_role"]: m["body_refs"] for m in sb.ctx.outbound}
    assert routed == {"terminologist": [C1_VO]}


def test_a_revised_test_row_wakes_the_terminologist_in_the_repair_mode(m399):
    """Route B end to end, night 144's m400 (frame 213, pass 1b). The relay's
    cause is the principal's `converse` reply, not a verdict, so the
    Terminologist woke in `relay`, which holds no `criteria.respecify` and
    no `msg.answer_tester`."""
    from rota.core.runner import _mode_key
    from rota.core.scheduler import Wake
    from rota.roles import prompts

    _vo_test(m399, "bg_4", "running", "aa28d1d")
    _message(m399, "m399", "liaison", "principal", "clarify", [C1_VO, TST_VO])
    _message(m399, "m400", "principal", "liaison", "converse", [], cause="m399",
             status="open")
    m399.commit()
    (wake,) = [w for w in open_tips(m399) if w.message_id == "m400"]
    calls = [f"TOOL: rulings.rule(rulings={json.dumps({C1_VO: 'approve', TST_VO: 'revise'})}, "
             f"words={M400_WORDS!r})",
             f'TOOL: msg.relay_vision_keeper(refs=["{TST_VO}"])', "done"]
    out = run_session(m399, wake, backend=ScriptedBackend(calls), pins=PINS,
                      instructions="answering")
    assert out.committed, out.errors
    (relay,) = m399.execute("SELECT id, to_role, body_refs FROM messages WHERE "
                            "cause_id = 'm400' AND verb = 'relay'").fetchall()
    assert (relay["to_role"], json.loads(relay["body_refs"])) == ("terminologist", [C1_VO])
    mode = _mode_key(Wake("terminologist", "message", refs=(), detail="relay",
                          message_id=relay["id"]), m399)
    assert mode == "criterion_repair"
    assert {"criteria.respecify", "msg.answer_tester"} <= set(
        prompts.mode_tools("terminologist", mode))


def _m400_relay(m399) -> str:
    """Night 144's m400: the Liaison rules c1 approved and its test revised,
    and relays the test row. The id of the relay to the Terminologist."""
    _vo_test(m399, "bg_4", "running", "aa28d1d")
    _message(m399, "m399", "liaison", "principal", "clarify", [C1_VO, TST_VO])
    _message(m399, "m400", "principal", "liaison", "converse", [], cause="m399",
             status="open")
    n = m399.execute("SELECT COALESCE(MAX(ts_order), 0) + 1 n FROM entries").fetchone()["n"]
    m399.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
                 "('e_m400', 'principal', ?, ?)", (M400_WORDS, n))
    m399.commit()
    (wake,) = [w for w in open_tips(m399) if w.message_id == "m400"]
    calls = [f"TOOL: rulings.rule(rulings={json.dumps({C1_VO: 'approve', TST_VO: 'revise'})}, "
             f"words={M400_WORDS!r})",
             f'TOOL: msg.relay_vision_keeper(refs=["{TST_VO}"])', "done"]
    out = run_session(m399, wake, backend=ScriptedBackend(calls), pins=PINS,
                      instructions="answering")
    assert out.committed, out.errors
    (relay,) = m399.execute("SELECT id FROM messages WHERE cause_id = 'm400' "
                            "AND verb = 'relay'").fetchall()
    return relay["id"]


def test_an_approved_criterion_keeps_its_verdict_beside_its_revised_test(m399):
    """The review of f252df24, finding 1: on m400's shape the wake read
    `{c1: revise}`, though the principal approved c1 and revised its test.
    The repair brief then told the seat to rewrite his approved words."""
    from pathlib import Path

    import rota.roles
    from rota.core.runner import resolve_inbound
    from rota.core.scheduler import Wake

    relay = {"id": _m400_relay(m399)}
    inbound = resolve_inbound(m399, Wake("terminologist", "message", refs=(),
                                         detail="relay", message_id=relay["id"]))
    assert inbound.get("principal_verdict", {}).get(C1_VO) == "approve"
    assert inbound.get("principal_test_verdict") == {TST_VO: "revise"}
    assert inbound.get("principal_said") == M400_WORDS
    brief = (Path(rota.roles.__file__).parent / "prompts" / "terminologist"
             / "criterion_repair.md").read_text(encoding="utf-8")
    assert "`principal_test_verdict`" in brief
    # The seat answers the Tester with the criterion and no rewrite.
    sb = _sandbox(m399, "terminologist", "criterion_repair", relay["id"])
    assert sb.call("msg.answer_tester", refs=[C1_VO])["to"] == "tester"


def test_an_approved_criterion_with_a_ruled_test_refuses_a_respecify(m399):
    """The review of 126b8c4e, finding 2: on m400's shape the door admitted a
    `criteria.respecify` of the approved c1, and the text of c1 changed. The
    brief paragraph alone stopped the rewrite of approved words."""
    relay = _m400_relay(m399)
    sb = _sandbox(m399, "terminologist", "criterion_repair", relay)
    with pytest.raises(ValueError, match="msg.answer_tester"):
        sb.call("criteria.respecify", id=C1_VO,
                text="The version option prints the Python version.")


def test_the_repair_brief_reads_the_test_ruling_before_an_approved_criterion(m399):
    """The review of 126b8c4e, findings 3 and 4: "An approved criterion
    needs nothing." came first, and "approved" named no field the seat
    reads when the Liaison rules the test row alone."""
    from pathlib import Path

    import rota.roles

    brief = " ".join((Path(rota.roles.__file__).parent / "prompts" / "terminologist"
                      / "criterion_repair.md").read_text(encoding="utf-8").split())
    condition = ("If `principal_verdict` holds no contest or revise for the "
                 "criterion and the message holds `principal_test_verdict`")
    assert condition in brief
    assert brief.index(condition) < brief.index("An approved criterion needs nothing.")


def test_the_testers_answer_brief_says_the_test_checks_the_principals_words(m399):
    """The review of 126b8c4e, finding 6: the Tester's line on
    `principal_said` had no test. The line says the words rule the test or
    its criterion, and the test checks what the words ask."""
    from pathlib import Path

    import rota.roles

    brief = (Path(rota.roles.__file__).parent / "prompts" / "tester"
             / "answer.md").read_text(encoding="utf-8")
    (line,) = [ln for ln in brief.splitlines() if "`principal_said`" in ln]
    assert "ruling on this criterion or its test" in line
    assert "the test checks what the words ask" in line


@pytest.mark.parametrize("status", ["abandoned", "deferred"])
def test_a_criterion_whose_test_waits_on_a_stopped_batch_reaches_the_tester(m399, status):
    """Night 142, walk 1: the test of `uses_stdlib` sat in the abandoned
    batch, and the refusal said the Tester had written no test of it
    (s210, s218, s238, s274)."""
    _vo_test(m399, "bg_3", status, None)
    _criterion_relay(m399, M142_WORDS)
    m399.commit()
    sb = _sandbox(m399, "terminologist", "criterion_repair", "m144")
    assert sb.call("msg.answer_tester", refs=[C1_VO])["to"] == "tester"


def test_a_refusal_over_a_written_test_names_the_test_and_its_batch(m399):
    """The refusal reads `tests` first. A test of a merged batch exists, so
    the sentence names it and never says that no test was written."""
    _vo_test(m399, "bg_1", "merged", "aa28d1d")
    _criterion_relay(m399, M142_WORDS)
    m399.commit()
    sb = _sandbox(m399, "terminologist", "criterion_repair", "m144")
    with pytest.raises(ValueError) as refused:
        sb.call("msg.answer_tester", refs=[C1_VO])
    assert TST_VO in str(refused.value) and "merged" in str(refused.value)
    assert "has written no test" not in str(refused.value)


def test_a_test_of_an_abandoned_batch_is_no_check_line(m399):
    """Night 142, walk 1: the pages m109, m128, m159 and m191 showed the
    test of the abandoned batch as the criterion's check. A page about that
    batch still shows the test."""
    from rota.roles.principal import check_line, request_block

    _vo_test(m399, "bg_3", "abandoned", "aa28d1d")
    m399.commit()
    line = f"     3. check: {check_line(m399, TST_VO)}"
    out: list[str] = []
    request_block(m399, [ITEM_VO, C1_VO], [], out)
    assert not any(check_line(m399, TST_VO) in o for o in out)
    assert "     check: none yet." in out
    out = []
    request_block(m399, [ITEM_VO, C1_VO], [], out, batch="bg_3")
    assert line in out


# ---------------------------------------------------------------------------
# Pass 3, night 136 after s514: the next page (frame 190's design, 2.4 and
# 2.F, amendment 3).
# ---------------------------------------------------------------------------

REPLY_62 = ("The principal's contest on parametersource_commandline requires a "
            "refactor to align line one with the exact wording provided.")
RECONCILE_A9 = ("the README says: Users define commands and options using decorators "
                "in Python functions, which Click then uses to parse and execute "
                "command-line inputs; the code shows: The API reference lists "
                "decorators like command, option, and argument which are used to "
                "define commands and options in Click")


def _ledger(db, lid: str, about: str, table: str, words: str, author: str,
            session: str | None = None) -> None:
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, "
               "author) VALUES (?, ?, ?, ?, 'open', ?)", (lid, about, table, words, author))
    if session:
        db.execute("INSERT INTO receipts (session_id, table_name, row_id, new_version) "
                   "VALUES (?, 'ledger', ?, 1)", (session, lid))


def _session(db, sid: str, role: str, trigger: str | None, kind: str) -> None:
    seq = db.execute("SELECT COALESCE(MAX(seq), 0) + 1 n FROM sessions").fetchone()["n"]
    db.execute("INSERT INTO sessions (id, role, trigger_msg, seq, wake_kind) "
               "VALUES (?, ?, ?, ?, ?)", (sid, role, trigger, seq, kind))


@pytest.fixture
def bg4(db, monkeypatch):
    """Night 136 after s514 and s567: bg_4 grouped and `pending`, with no
    `batch_touch` row, its item approved at version 4, and the open reply
    row `l_62ca6652d9`. s567 woke on the relay m430, which the principal's
    verdict m429 caused, and m430 named `parametersource_commandline`."""
    from rota.core import scheduler

    monkeypatch.setattr(scheduler, "onboarding_phase", lambda conn: "done")
    _statement(db, "s3", TEXT_VO)
    _item(db, ITEM_VO, TEXT_VO, version=4, statement="s3")
    _criteria(db, ITEM_VO, "tk_1_version_option_show_python", CRIT_VO)
    _item(db, "defines_commands_and_options", "Users define commands and options "
          "using decorators in Python functions.", version=3, described=1)
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('bg_4', ?, 'pending')",
               (ITEM_VO,))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_4', "
               "'tk_1_version_option_show_python')")
    db.execute("INSERT INTO constraints (id, headline, text) VALUES "
               "('parametersource_commandline', 'ParameterSource.COMMANDLINE', "
               "'a value given on the command line')")
    _message(db, "m427", "liaison", "principal", "present", ["parametersource_commandline"])
    _message(db, "m429", "principal", "liaison", "verdict",
             ["parametersource_commandline"], cause="m427")
    seed_verdict(db, "m429", json.dumps({"l_a599c55837": "contest",
                            "parametersource_commandline": "contest"}))
    _message(db, "m430", "liaison", "architect", "relay",
             ["parametersource_commandline"], cause="m429")
    _session(db, "s567", "architect", "m430", "message")
    _ledger(db, "l_62ca6652d9", "parametersource_commandline", "constraints",
            REPLY_62, "architect", session="s567")
    db.commit()
    return db


def test_the_agenda_wakes_for_a_seat_row_and_carries_the_reply_row(bg4):
    """Night 136 after s514: each round left one reply row, the agenda fired
    13 times, and bg_4 was never annotated. A reply row alone wakes no page.
    A `reconcile` row wakes it, the reply row rides after it, `annotate`
    runs first, and one ruling closes both (frame 190's design, 2.4 and
    2.F, amendment 3)."""
    from rota.core.scheduler import frontier, reply_rows

    assert reply_rows(bg4) == {"l_62ca6652d9"}
    assert tick_agenda(bg4, principal_present=True) == []

    _session(bg4, "s11", "vision_keeper", None, "tick:reconcile")
    _ledger(bg4, "l_a9c0ca7d82", "defines_commands_and_options", "items",
            RECONCILE_A9, "vision_keeper", session="s11")
    bg4.commit()
    (wake,) = tick_agenda(bg4, principal_present=True)
    assert list(wake.refs) == ["l_a9c0ca7d82", "l_62ca6652d9"]

    # The start work goes first: `annotate` for bg_4, and its touch note.
    kinds = [w.kind for w in frontier(bg4, principal_present=True)]
    assert kinds.index("tick:annotate") < kinds.index("tick:agenda"), kinds
    bg4.execute("INSERT INTO code_index (grain, grain_kind) VALUES "
                "('src/click/decorators.py', 'path')")
    (annotate,) = P.REGISTRY["annotate"].fn(bg4)
    bg4.commit()
    out = run_session(bg4, annotate, backend=ScriptedBackend(
        ['TOOL: batches.annotate(batch_id="bg_4", paths=["src/click/decorators.py"])',
         "done"]), pins=PINS, instructions="annotate")
    assert out.committed, out.errors
    kinds = [w.kind for w in frontier(bg4, principal_present=True)]
    assert "tick:annotate" not in kinds
    assert kinds.index("tick:touch_note") < kinds.index("tick:agenda"), kinds

    (wake,) = tick_agenda(bg4, principal_present=True)
    mid = _dispatch(bg4, wake, 'TOOL: msg.present_principal(refs=["l_a9c0ca7d82"])')
    (ask,) = [a for a in pending_asks(bg4) if a.message_id == mid]
    # bg_4 is live and holds a plan, so the send stamps it as the item's
    # code line, line 2 (frame 298's design, 2.1).
    assert ask.order == ([ITEM_VO, f"guess:{ITEM_VO}"] + [c for c, _ in CRIT_VO]
                         + ["l_a9c0ca7d82", "l_62ca6652d9"])
    page = ask.rendered
    assert "  2. The team's plan of the code this touches: expected to touch " \
           "src/click/decorators.py" in page, page
    assert page.index(TEAM_NOTES) < page.index("  7. The principal's contest"), page

    reply = _reply(bg4, mid, "ok")
    _landing(bg4, reply, {str(n): "approve" for n in range(1, 8)}, "ok")
    assert bg4.execute("SELECT COUNT(*) n FROM ledger WHERE status = 'open'"
                       ).fetchone()["n"] == 0


def test_reply_rows_alone_draw_no_agenda_and_ride_the_next_page(bg4):
    """Night 136 ended with one open row, `l_62ca6652d9`, a reply row. A row
    about a message is a reply row too (2.F, amendment 7). Neither raises a
    page. The next row from any other writer wakes the agenda, the
    request's own row leads, and the reply rows ride after the chosen rows
    (frame 190's design, 2.F, amendment 3)."""
    _ledger(bg4, "l_6b81c7417e", "m427", "principal_verdict",
            "The principal's verdict contests all six observed terms because the "
            "onboarding page failed to describe them.", "terminologist")
    bg4.commit()
    assert tick_agenda(bg4, principal_present=True) == []
    assert P.REGISTRY["agenda"].fn(bg4) == []

    # An older row about a description, then a newer one about the request.
    _ledger(bg4, "l_a9c0ca7d82", "defines_commands_and_options", "items",
            RECONCILE_A9, "vision_keeper")
    _ledger(bg4, "l_796a449208", "c2_version_option_show_python", "criteria",
            "The show_python flag is a keyword argument of version_option that "
            "defaults to False.", "architect")
    bg4.commit()
    (wake,) = P.REGISTRY["agenda"].fn(bg4)
    assert list(wake.refs) == ["l_796a449208", "l_a9c0ca7d82",
                               "l_62ca6652d9", "l_6b81c7417e"]
    mid = _dispatch(bg4, wake, 'TOOL: msg.present_principal(refs=["l_796a449208"])')
    refs = json.loads(bg4.execute("SELECT body_refs FROM messages WHERE id = ?",
                                  (mid,)).fetchone()["body_refs"])
    assert {"l_62ca6652d9", "l_6b81c7417e"} <= set(refs)
