"""
Frame 193, pass 2: the shift question, its three answers, and one request
per page, on night 137's and night 133's turns.

The rows are copied from `.rota/clickI_night137.db` and
`.rota/clickI_night133.db`, read with `mode=ro`, and rebuilt inline, as the
pass 1 tests do. The design is `plans/frame193-design.md`, section 2.F.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.predicates import cancel, grouping, request_shift
from rota.core.runner import run_session
from rota.core.scheduler import resume_behind, tick_agenda
from rota.llm.llm import Pins, ScriptedBackend
from rota.roles.principal import (
    Answer, Ask, _items_reached, apply_rulings, current_request, land,
    parse_reply, pending_asks, render_page,
)
from rota.testkit.fixtures import seed_provenance, seed_ref
from rota.tools.invariants import i9

PINS = Pins(model="stub", temperature=0.0)

CONFIRM = "confirm_with_default_on_eof"
VERSION = "version_option_show_python"
TICKET = "tk_1_confirm_with_default_on_eof"
BATCH = "batch_1_confirm_eof_default"
S1 = ("Add an echo_json(obj) helper next to echo that prints an object as compact "
      "JSON on one line, followed by a newline.")
S2 = ("Let confirm() take a default_on_eof flag: when stdin is closed it returns the "
      "default instead of aborting.")
S3 = ("Give version_option a show_python flag that appends the running Python "
      "version to the message.")
CRITERIA = ("cr_1_confirm_eof_default", "cr_2_confirm_eof_default_false",
            "cr_2_confirm_eof_default_value_type",
            "cr_3_confirm_eof_default_value_type",
            "cr_4_confirm_eof_default_value_type")
# m161's seven ledger rows: (id, about_ref, about_table, author).
M161_LEDGER = (
    ("l_20da18da15", "cr_3_confirm_eof_default_value_type", "criteria", "tester"),
    ("l_356b6156e0", BATCH, "src/click/termui.py::confirm", "developer"),
    ("l_6e604ad102", "cr_2_confirm_eof_default_value_type", "criteria", "tester"),
    ("l_8be6bffe47", BATCH, "src/click/termui.py", "developer"),
    ("l_a0c7f980d8", "cr_2_confirm_eof_default_false", "criteria", "tester"),
    ("l_ad90d81d32", "cr_4_confirm_eof_default_value_type", "criteria", "tester"),
    ("l_e748ee49a7", "cr_4_confirm_eof_default_value_type", "criteria", "tester"),
)
M161_REFS = ([lid for lid, *_ in M161_LEDGER] + [CONFIRM] + list(CRITERIA))
M163 = ("Line 1 is the wrong change. It describes the confirm() end-of-input flag, "
        "but the change I'm working on now is the show_python flag for "
        "version_option.")
SHIFT = f"m_shift_{CONFIRM}_m_p3"


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _request(db, n: int, ts: int, seq: int, text: str, status: str = "ratified",
             sid: str | None = None) -> None:
    """A walk's request: the entry, the uncaused converse, and its statement."""
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES (?, "
               "'principal', ?, ?)", (f"e_p{n}", text, ts))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES (?, 't_p1', 'principal', 'liaison', "
               "'converse', ?, ?, 'answered')", (f"m_p{n}", json.dumps([f"e_p{n}"]), seq))
    if status:
        db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
                   "text, status) VALUES (?, ?, 0, ?, ?, ?)",
                   (sid or f"s{n}", f"e_p{n}", len(text), text, status))


def _item(db, iid: str, text: str, statement: str | None, *, approval="approved",
          version=1, ver=1, described=0) -> None:
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version, "
               "priority, is_description) VALUES (?, ?, 'in_scope', ?, ?, ?, 1, ?)",
               (iid, text, approval, ver, version, described))
    seed_provenance(db, "items", iid, "decided")
    if statement:
        seed_ref(db, "items", iid, "statement", statement)


def _night137(db) -> None:
    """Night 137 at s292's commit: m161 open at seq 163, m_p3 answered with s3
    proposed and m164 open, the confirm item approved at version 1 with its
    change built to 34a5e21, and the 7 rows of m161."""
    _request(db, 1, 23, 64, S1)
    _request(db, 2, 32, 86, S2)
    _request(db, 3, 49, 165, S3, status="proposed")
    _item(db, "echo_json", S1, "s1", version=2, ver=2)
    db.execute("INSERT INTO config (key, value) VALUES ('delivered:echo_json', '2')")
    _item(db, "how_it_works", "Click is a toolkit.", None, version=2, ver=2,
          described=1)
    _item(db, CONFIRM, S2, "s2")
    db.execute("INSERT INTO tickets (id, item_id, text, version, item_ver) VALUES "
               "(?, ?, 'let confirm() take a default_on_eof flag', 1, 1)",
               (TICKET, CONFIRM))
    for cid in CRITERIA:
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, ?, ?)",
                   (cid, TICKET, f"the check {cid}"))
    db.execute("INSERT INTO batches (id, item_id, head_commit, status) VALUES "
               "(?, ?, '34a5e21020937c4548f6e98cce918136d7ee3397', 'running')",
               (BATCH, CONFIRM))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES (?, ?)",
               (BATCH, TICKET))
    for k in range(6):
        db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                   "VALUES (?, ?, ?, 'tests/test_termui.py', 'def test(): pass')",
                   (f"tst_{k}", BATCH, CRITERIA[k % 5]))
        db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) "
                   "VALUES (?, ?, ?, '34a5e21', ?)",
                   (f"tr_{k}", BATCH, f"tst_{k}", "fail" if k < 3 else "pass"))
    for lid, about, table, author in M161_LEDGER:
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
                   "kind, status, author) VALUES (?, ?, ?, ?, 'default', 'open', ?)",
                   (lid, about, table, f"the {author} assumed {lid}", author))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m161', 'm161', 'liaison', "
               "'principal', 'present', ?, 163, 'open')", (json.dumps(M161_REFS),))
    db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES ('m164', 'm_p3', 'm_p3', "
               "'liaison', 'principal', 'confirm', '[\"s3\"]', 167, 'open')")
    db.commit()


def _ask_shift(db) -> str:
    (wake,) = request_shift(db)
    out = run_session(db, wake, backend=ScriptedBackend(
        [f"TOOL: msg.present_principal(refs=['{CONFIRM}', 's3'])", "done"]),
        pins=PINS, instructions="shift")
    assert out.committed, out.errors
    return SHIFT


def _rule_shift(db, word: str) -> str:
    """The principal's words on the shift page, read by the Liaison as
    `{"1": word}`, and landed through `apply_rulings`."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    (ask,) = pending_asks(db)
    reply = land(db, ask, parse_reply(ask, M163))
    db.commit()
    sb = build("liaison", db, mode="normal", session_id="sess_shift",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = reply
    out = sb.call("rulings.rule", rulings={"1": word}, words=M163)
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words) "
               "VALUES ('r_shift', ?, ?, ?, ?)",
               (SHIFT, reply, json.dumps(out["per_item"]), M163))
    (verdict,) = apply_rulings(db)
    db.commit()
    return verdict


def test_s292s_commit_asks_which_request_goes_first(db):
    _night137(db)
    wakes = request_shift(db)
    assert [(w.kind, w.refs) for w in wakes] == [
        ("tick:request_shift", (CONFIRM, "s3"))]
    # Before the question is sent, m161 is held: the principal answered it
    # after m_p3 on night 137, at seq 166.
    assert [a.message_id for a in pending_asks(db)] == ["m164"]
    _ask_shift(db)
    asks = pending_asks(db)
    assert [a.message_id for a in asks] == [SHIFT]
    assert asks[0].rendered == "\n".join([
        f"You asked for something new: {S3}",
        "Before that you asked for this, and it is not finished:",
        f"  1. {S2}",
        f"     Where it stands: approved. The change {BATCH} is built, and 3 of "
        "its 6 tests fail.",
        # Six check lines now carry numbers (frame 306, W-A).
        "     What it waits on: one page to you with 19 lines, and 7 notes.",
        "Choose one for line 1:",
        "  - later: put it aside until the new request is merged. Nothing more "
        "about it reaches you until then.",
        "  - now: answer its open page first, then the new request.",
        "  - drop: stop it. Its change is abandoned.",
    ])
    assert asks[0].order == [CONFIRM]
    # Asked once: the predicate does not fire again for the pair.
    assert request_shift(db) == []


def test_later_parks_the_item_and_holds_its_page(db):
    _night137(db)
    _ask_shift(db)
    verdict = _rule_shift(db, "later")
    rows = db.execute("SELECT item_id, kind, by, cause_id FROM item_parks").fetchall()
    assert [tuple(r) for r in rows] == [(CONFIRM, "park", "shift", verdict)]
    assert db.execute("SELECT approval FROM items WHERE id = ?",
                      (CONFIRM,)).fetchone()[0] == "approved"
    # The verdict carries no ref, so no relay wakes a seat.
    v = db.execute("SELECT status, body_refs FROM messages WHERE id = ?",
                   (verdict,)).fetchone()
    assert (v["status"], v["body_refs"]) == ("answered", "[]")
    assert [a.message_id for a in pending_asks(db)] == ["m164"]
    db.execute("UPDATE messages SET status = 'answered' WHERE id = 'm164'")
    db.commit()
    # No page of the confirm rows, so s299's 13 contests are never asked for.
    assert tick_agenda(db, principal_present=True) == []
    # The live change of a parked item is deferred, not abandoned.
    assert cancel(db) == []
    from rota.core.loop import _perform
    from rota.core.predicates import preempt

    (wake,) = preempt(db)
    assert _perform(db, wake) == (f"deferred {BATCH}: {CONFIRM} is set aside "
                                  f"behind s3")
    from rota.roles.principal import aside_lines

    lines = aside_lines(db)
    assert not any("resume" in line for line in lines)
    assert lines[0] == f"Waiting behind {S3.rstrip('.')}:"
    assert lines[1].endswith("It comes back when that request is delivered or "
                             "dropped.")


def test_drop_closes_the_page_and_its_rows_and_abandons_the_change(db):
    _night137(db)
    _ask_shift(db)
    verdict = _rule_shift(db, "drop")
    assert db.execute("SELECT status FROM messages WHERE id = 'm161'").fetchone()[0] \
        == "answered"
    assert db.execute("SELECT value FROM config WHERE key = 'closed:m161'").fetchone()[0] \
        == verdict
    marks = ",".join("?" * len(M161_LEDGER))
    ids = tuple(lid for lid, *_ in M161_LEDGER)
    assert {r[0] for r in db.execute(
        f"SELECT status FROM ledger WHERE id IN ({marks})", ids)} == {"resolved"}
    assert db.execute(f"SELECT COUNT(*) FROM decisions WHERE resolves_ledger IN "
                      f"({marks}) AND text LIKE 'overruled at signoff:%'",
                      ids).fetchone()[0] == 7
    assert [w.refs for w in cancel(db)] == [(BATCH,)]
    assert not [f for f in i9(db) if "m161" in f.detail]


def test_now_shows_the_earlier_page_first(db):
    _night137(db)
    _ask_shift(db)
    _rule_shift(db, "now")
    assert [a.message_id for a in pending_asks(db)] == ["m161", "m164"]


def test_the_parked_item_comes_back_when_the_request_is_delivered(db):
    _night137(db)
    _ask_shift(db)
    _rule_shift(db, "later")
    db.execute("UPDATE messages SET status = 'answered' WHERE id = 'm164'")
    _item(db, VERSION, S3, "s3", version=3, ver=3)
    db.commit()
    assert resume_behind(db) == 0
    db.execute("INSERT INTO config (key, value) VALUES (?, '3')",
               (f"delivered:{VERSION}",))
    db.commit()
    assert resume_behind(db) == 1
    kinds = [r[0] for r in db.execute(
        "SELECT kind FROM item_parks WHERE item_id = ? ORDER BY seq, rowid", (CONFIRM,))]
    assert kinds == ["park", "resume"]
    assert db.execute("SELECT by, cause_id FROM item_parks WHERE kind = 'resume'"
                      ).fetchone()[:] == ("request", "m_p3")
    assert [a.message_id for a in pending_asks(db)] == ["m161"]


def test_night133s_later_leaves_the_version_ticket_alone_in_the_grouping(db):
    """Night 133 at s383's commit: m_p3 at seq 258, s3, the confirm item
    approved as s365 left it, its ticket, and the version item."""
    _request(db, 1, 19, 46, S1)
    _request(db, 2, 29, 71, S2)
    _request(db, 3, 80, 258, S3)
    _item(db, "echo_json", S1, "s1")
    db.execute("INSERT INTO config (key, value) VALUES ('delivered:echo_json', '1')")
    _item(db, "confirm_default_on_eof", S2, "s2")
    _item(db, VERSION, S3, "s3")
    for tk, item, crit in (
            ("tk_1_confirm_default_on_eof", "confirm_default_on_eof",
             ("cr_1_confirm_eof_default", "cr_2_confirm_eof_stdin_state",
              "cr_3_confirm_eof_no_abort")),
            ("tk_1_version_option_show_python", VERSION,
             ("c1_version_option_show_python", "c2_version_option_show_python",
              "c3_version_option_show_python"))):
        db.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, 'the ticket')",
                   (tk, item))
        for cid in crit:
            db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, ?, ?)",
                       (cid, tk, f"the check {cid}"))
    db.commit()
    assert [w.refs for w in request_shift(db)] == [("confirm_default_on_eof", "s3")]
    shift = "m_shift_confirm_default_on_eof_m_p3"
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES (?, ?, 'liaison', 'principal', "
               "'present', '[\"confirm_default_on_eof\", \"s3\"]', 259, 'open')",
               (shift, shift))
    db.commit()
    land(db, Ask(message_id=shift, verb="present",
                 refs=["confirm_default_on_eof", "s3"]),
         Answer("verdict", text="that is a separate request",
                per_item={"confirm_default_on_eof": "park"}))
    db.commit()
    assert [w.refs for w in grouping(db)] == [("tk_1_version_option_show_python",)]


def test_m192_numbers_no_line_of_a_parked_or_earlier_request(db):
    """Night 137's m192, the sign-off page of the version option, with the
    confirm item parked. The door keeps the refs equal to the numbered rows."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    _night137(db)
    _ask_shift(db)
    _rule_shift(db, "later")
    _item(db, VERSION, S3, "s3", approval="draft", version=3, ver=0)
    for iid in ("defines_commands_and_options", "parses_and_executes_inputs",
                "provides_command_line_interface"):
        _item(db, iid, f"the account says {iid}", None, described=1)
    for lid in ("l_97335075e8", "l_34daa6084e"):
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
                   "status, author) VALUES (?, 'echo_json', 'items', ?, 'open', "
                   "'developer')", (lid, f"echo_json note {lid}"))
    db.commit()
    m192 = [VERSION, CONFIRM, "defines_commands_and_options", "echo_json",
            "how_it_works", "parses_and_executes_inputs",
            "provides_command_line_interface", "l_97335075e8", "l_34daa6084e",
            *CRITERIA]
    page, order = render_page(db, "present", m192)
    assert CONFIRM not in order and not set(CRITERIA) & set(order)
    assert "echo_json" not in order
    assert order[0] == VERSION
    # A note about the delivered echo_json item stays a line, so a ruling
    # closes it.
    assert {"l_97335075e8", "l_34daa6084e"} <= set(order)
    sb = build("liaison", db, mode="normal", session_id="sess_m192",
               allow=prompts.mode_tools("liaison", "submit"))
    sb.call("msg.present_principal", refs=m192)
    (sent,) = [m for m in sb.ctx.outbound if m["verb"] == "present"]
    assert sorted(sent["body_refs"]) == sorted(
        render_page(db, "present", sent["body_refs"])[1])


def test_a_challenge_row_reaches_its_item(db):
    _item(db, CONFIRM, S2, None)
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "status, author) VALUES ('challenge_items_confirm_with_default_on_eof', "
               "'items:confirm_with_default_on_eof', 'items', 'the Critic falsified "
               "it', 'open', 'critic')")
    assert _items_reached(db, "challenge_items_confirm_with_default_on_eof") == [CONFIRM]


def test_a_follow_up_on_the_same_request_is_no_boundary(db):
    """An inline case, not a night turn: the version item is the current
    request, and a second uncaused converse says it again."""
    _request(db, 3, 49, 165, S3)
    _item(db, VERSION, S3, "s3")
    _request(db, 4, 50, 170, S3 + " Write it as major.minor.micro.", sid="s4")
    db.commit()
    # Without supersedes the follow-up is a new request, and it would ask.
    assert [w.refs for w in request_shift(db)] == [(VERSION, "s4")]
    db.execute("UPDATE statements SET supersedes = 's3' WHERE id = 's4'")
    db.commit()
    assert current_request(db)["id"] == "m_p3"
    assert request_shift(db) == []
    assert pending_asks(db) == []


FOLLOW_UP = "Write the version as major.minor.micro."


def _segment_session(db, status: str | None = "ratified", extra: tuple = ()):
    """A follow-up converse m_p4 behind request m_p3, whose s3 has `status`."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    _request(db, 3, 49, 165, S3, status=status)
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES ('e_p4', "
               "'principal', ?, 50)", (FOLLOW_UP,))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m_p4', 't_p1', 'principal', "
               "'liaison', 'converse', '[\"e_p4\"]', 170, 'open')")
    db.commit()
    sb = build("liaison", db, mode="normal", session_id="sess_seg",
               allow=prompts.mode_tools("liaison", "converse") + list(extra))
    sb.ctx.trigger = "m_p4"
    sb.ctx.entry_id = "e_p4"
    return sb


def _segment(sb, sid: str, supersedes: str):
    return sb.call("brief.segment", id=sid, span_start=0, span_end=len(FOLLOW_UP),
                   text=FOLLOW_UP, supersedes=supersedes)


def test_the_segment_door_admits_supersedes_on_the_current_request(db):
    sb = _segment_session(db)
    with pytest.raises(ValueError, match="supersedes names s9"):
        _segment(sb, "s4", "s9")
    out = _segment(sb, "s4", "s3")
    assert out["id"] == "s4"
    (row,) = [w for w in sb.ctx.writes if w[0] == "statements"]
    assert row[2]["supersedes"] == "s3"


def test_a_wrong_supersedes_is_told_the_earlier_statement(db):
    sb = _segment_session(db)
    with pytest.raises(ValueError) as err:
        _segment(sb, "s4", "s9")
    assert str(err.value) == ("supersedes names s9, and the current request's "
                              "earlier statement is s3. Pass that id, or leave "
                              "supersedes out.")
    assert not [w for w in sb.ctx.writes if w[0] == "statements"]


def test_a_supersedes_with_no_ratified_request_is_told_to_leave_it_out(db):
    """G1's shape: the earlier request's statement waits as proposed, so the
    page holds no request that a follow-up can say again (frame 193, pass 2b)."""
    sb = _segment_session(db, status="proposed")
    with pytest.raises(ValueError) as err:
        _segment(sb, "s4", "s3")
    assert str(err.value) == ("There is no earlier request on the page, so leave "
                              "supersedes out.")
    assert "s3" not in str(err.value)


def test_a_seat_that_names_its_own_new_id_is_refused(db):
    """G1's register line: the seat sent id and supersedes as one id. The door
    names that id once, and the earlier statement once."""
    sb = _segment_session(db)
    with pytest.raises(ValueError) as err:
        _segment(sb, "s4", "s4")
    msg = str(err.value)
    assert msg.startswith("supersedes names s4, and the current request's "
                          "earlier statement is s3.")
    assert msg.count("s4") == 1


def test_the_wake_offers_a_ratified_statement_only(db):
    from rota.core.runner import CURRENT_REQUEST_RELATION, resolve_inbound
    from rota.core.scheduler import Wake

    _segment_session(db, status="proposed")
    wake = Wake("liaison", "message", "m_p4")
    assert "current_request" not in resolve_inbound(db, wake)
    db.execute("UPDATE statements SET status = 'ratified' WHERE id = 's3'")
    db.commit()
    assert resolve_inbound(db, wake)["current_request"] == {
        "statement": "s3", "text": S3, "relation": CURRENT_REQUEST_RELATION}


def test_a_described_item_on_the_request_does_not_hold_the_resume(db):
    """The review of 61a0f41d, finding 1: night 133's account item cites s1,
    and it held every resume at 0."""
    _night137(db)
    _ask_shift(db)
    _rule_shift(db, "later")
    _item(db, VERSION, S3, "s3")
    _item(db, "defines_commands", "the account: defines commands", "s3",
          approval="draft", ver=0, described=1)
    db.execute("INSERT INTO config (key, value) VALUES "
               "('delivered:version_option_show_python', '1')")
    db.commit()
    assert resume_behind(db) == 1


def test_a_request_with_no_work_item_ends_the_park(db):
    """The review of e406e976, finding 2: B with only an out-of-scope item
    held A for ever. B with no item at all still waits."""
    _night137(db)
    _ask_shift(db)
    _rule_shift(db, "later")
    assert resume_behind(db) == 0
    _item(db, "out3", "not this", "s3", approval="contested")
    db.execute("UPDATE items SET kind = 'out_of_scope' WHERE id = 'out3'")
    db.commit()
    assert resume_behind(db) == 1


def test_a_description_on_the_newest_request_keeps_the_page_its_own(db):
    """The review of e406e976, finding 1: d3 describes the version request,
    and the confirm item keeps its line on its own page."""
    from rota.roles.principal import off_page, page_request

    _night137(db)
    db.execute("UPDATE statements SET status = 'ratified' WHERE id = 's3'")
    _item(db, "d3", "the account says version", "s3", described=1)
    db.commit()
    assert page_request(db, [CONFIRM, "d3"]) == "e_p2"
    assert CONFIRM not in off_page(db, [CONFIRM, "d3"])


def _m283(db) -> list[str]:
    """Night 133's m283 rebuild: three requests, and the account items."""
    _request(db, 1, 19, 46, S1)
    _request(db, 2, 29, 71, S2)
    _request(db, 3, 80, 258, S3)
    _item(db, "echo_json", S1, "s1")
    db.execute("INSERT INTO config (key, value) VALUES ('delivered:echo_json', '1')")
    _item(db, "confirm_default_on_eof", S2, "s2")
    _item(db, VERSION, S3, "s3", approval="draft", ver=0)
    _item(db, "defines_commands_and_options", "the account: defines commands",
          "s1", approval="draft", ver=0, described=1)
    for i in ("how_it_works", "parses_and_executes_inputs",
              "provides_command_line_interface"):
        _item(db, i, f"account {i}", None, approval="draft", ver=0, described=1)
    db.commit()
    return ["confirm_default_on_eof", "defines_commands_and_options", "echo_json",
            "how_it_works", "parses_and_executes_inputs",
            "provides_command_line_interface", VERSION]


def test_m283_keeps_the_account_item_that_cites_an_earlier_statement(db):
    """The review of 61a0f41d, finding 2."""
    from rota.roles.principal import off_page

    m283 = _m283(db)
    assert "defines_commands_and_options" not in off_page(db, m283)
    assert "defines_commands_and_options" in render_page(db, "present", m283)[1]


def test_a_ratified_follow_up_keeps_the_request_and_its_coverage(db):
    """The review of 61a0f41d, finding 3: s5 says s3 again. The item that
    cites s3 keeps its line, and s5 counts as covered."""
    from rota.roles.principal import open_requests, request_rows, uncovered_statements

    sb = _segment_session(db, extra=("brief.ratify",))
    _item(db, VERSION, S3, "s3")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status, supersedes) VALUES ('s5', 'e_p4', 0, ?, ?, "
               "'proposed', 's3')", (len(FOLLOW_UP), FOLLOW_UP))
    db.commit()
    sb.call("brief.ratify", id="s5")
    assert [w[:3] for w in sb.ctx.writes if w[0] == "statements"] == [
        ("statements", "s5", {"status": "ratified"})]
    db.execute("UPDATE statements SET status = 'ratified' WHERE id = 's5'")
    db.commit()
    assert open_requests(db) == [VERSION]
    # The follow-up s5 names the request, so its page keeps the item. A page
    # of no request is the account's (ruled: Roman, 2026-10-28 09:10).
    assert request_rows(db, ["s5"])[0] == VERSION
    assert "s5" not in [s["id"] for s in uncovered_statements(db)]
    assert request_shift(db) == []


def _shift_land(db, item: str, req: str, stmt: str, kind: str, seq: int) -> None:
    sid = f"m_shift_{item}_{req}"
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES (?, ?, 'liaison', 'principal', "
               "'present', ?, ?, 'open')", (sid, sid, json.dumps([item, stmt]), seq))
    db.commit()
    land(db, Ask(message_id=sid, verb="present", refs=[item, stmt]),
         Answer("verdict", text=kind, per_item={item: kind}))
    db.commit()


def test_a_chain_asks_nothing_once_the_last_request_is_delivered(db):
    """The review of 61a0f41d, finding 4: A behind B, B behind C. After C and
    B are delivered, no shift question asks about A against C."""
    _night137(db)
    _ask_shift(db)
    _rule_shift(db, "later")
    db.execute("UPDATE messages SET status = 'answered' WHERE id = 'm164'")
    _item(db, VERSION, S3, "s3")
    _request(db, 4, 60, 300, "Add a --color flag.", sid="s4")
    _item(db, "colorC", "Add a --color flag.", "s4")
    db.commit()
    _shift_land(db, VERSION, "m_p4", "s4", "park", 301)
    db.execute("INSERT INTO config (key, value) VALUES ('delivered:colorC', '1')")
    db.commit()
    assert resume_behind(db) == 1
    db.execute("INSERT INTO config (key, value) VALUES "
               "('delivered:version_option_show_python', '1')")
    db.commit()
    assert resume_behind(db) == 1
    db.commit()
    assert request_shift(db) == []


def test_the_shift_page_refuses_a_ruling_word(db):
    from rota.core.sandbox import build
    from rota.roles import prompts

    _night137(db)
    _ask_shift(db)
    (ask,) = pending_asks(db)
    reply = land(db, ask, parse_reply(ask, M163))
    db.commit()
    sb = build("liaison", db, mode="normal", session_id="sess_shift",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = reply
    with pytest.raises(ValueError) as e:
        sb.call("rulings.rule", rulings={"1": "approve"}, words=M163)
    assert str(e.value) == (
        "line 1 takes later, now or drop: the question is which request goes "
        "first, and nothing about the request itself changes here.")
    out = sb.call("rulings.rule", rulings={"1": "separate request"}, words=M163)
    assert out["per_item"] == {CONFIRM: "park"}
