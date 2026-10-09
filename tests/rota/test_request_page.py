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
from rota.core.db import init_db
from rota.core.runner import run_session
from rota.core.scheduler import open_tips, tick_agenda, verdict_rows
from rota.llm.llm import Pins, ScriptedBackend
from rota.roles.principal import (
    TEAM_NOTES, parse_reply, land, pending_asks, render_page,
    request_rows,
)
from rota.testkit.fixtures import seed_provenance, seed_ref

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
    ruled = db.execute("SELECT value FROM config WHERE key = ?",
                       (f"verdict:{row['id']}",)).fetchone()
    return row, (json.loads(ruled["value"]) if ruled else {})


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
    assert lines[3] == "It must:" and page.count("check: none yet.") == 3
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
    assert "What we are building:" in page and "You asked:" not in page
    assert order == refs
    assert page.index("What we are building:") < page.index(TEAM_NOTES)
    assert "To change what you asked for" not in page


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
    assert "The team gave up on: tests_missing for bg_2, 3 attempts." in page
    cr3 = page.index("  4. When confirm() is invoked with")
    assert page[cr3:].splitlines()[1] == (
        "     check: none. The team gave up writing it after 3 tries.")
    assert page.count("check: x, expects confirm(). Not run yet.") == 2
    assert page.index("The team gave up on:") < page.index("The team expects to touch:") \
        < page.index("  5. the work for:")
    assert ask.order == [ITEM_136] + [c for c, _ in CRIT_136] + ["bg_2"]
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
