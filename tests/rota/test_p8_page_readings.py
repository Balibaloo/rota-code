"""P8: a read-back line rides the page of its own request.

Night 172 (`plans/f1-f15-f21-night172-read.md`, W8). The send door put every
owed reading on every present and confirm page. `request_of` gave None for a
`reading:` ref, because `row_items` did not walk a reading. So m47, e_p2's
confirm page, read back two answers of e_p1, and m17, e_p1's confirm page,
read back the onboarding answer m14.

Roman ruled on 2026-10-28 at 09:10, "Yeah that's right": a page is about one
request. A read-back goes on the next page of the same request, and on the
state view when that request is delivered (frame 344).
"""
from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

import pytest

from rota.core.db import _apply_write, init_db
from rota.core.runner import _as_write
from rota.roles.principal import (READING_REF, apply_rulings, land, page_readings,
                                  parse_reply, pending_asks, readings_owed,
                                  render_state, request_of)

NIGHT = Path(__file__).resolve().parents[2] / ".rota" / "clickI_night172.db"
if not NIGHT.exists():
    NIGHT = Path("D:/repos/rota/.rota/clickI_night172.db")


@pytest.fixture
def night(tmp_path):
    """A copy of the night 172 register. The night's file is never opened in
    place. The deliveries are undone, so each page reads as at its send."""
    if not NIGHT.exists():
        pytest.skip("the night 172 database is not on this machine")
    for tail in ("", "-wal", "-shm"):
        src = Path(str(NIGHT) + tail)
        if src.exists():
            shutil.copyfile(src, tmp_path / ("n172.db" + tail))
    conn = sqlite3.connect(tmp_path / "n172.db")
    conn.row_factory = sqlite3.Row
    conn.execute("DELETE FROM config WHERE key LIKE 'delivered:%'")
    return conn


def _page(conn, mid):
    refs = json.loads(conn.execute("SELECT body_refs FROM messages WHERE id = ?",
                                   (mid,)).fetchone()[0])
    return ([r for r in refs if not r.startswith(READING_REF)],
            [r for r in refs if r.startswith(READING_REF)])


def test_a_reading_has_the_request_of_the_rows_it_reads_back(night):
    assert request_of(night, "reading:m34") == "e_p1"
    assert request_of(night, "reading:m77") == "e_p2"
    assert request_of(night, "reading:m48") == "e_p2"
    # An onboarding answer and an account answer belong to no request.
    assert request_of(night, "reading:m14") is None
    assert request_of(night, "reading:m55") is None


@pytest.mark.parametrize("mid, gone", [
    ("m47", ["reading:m34", "reading:m44"]),
    ("m80", ["reading:m77"]),
])
def test_a_confirm_page_reads_back_no_answer_of_an_earlier_request(night, mid, gone):
    refs, readings = _page(night, mid)
    assert set(gone) <= set(readings)
    assert page_readings(night, refs, readings) == []


def test_a_confirm_page_before_any_item_reads_back_no_onboarding_answer(night):
    """m17 confirmed e_p1 before any item cited s1."""
    night.execute("DELETE FROM refs WHERE kind = 'statement' AND target = 's1'")
    refs, readings = _page(night, "m17")
    assert refs == ["s1"] and readings == ["reading:m14"]
    assert page_readings(night, refs, readings) == []


def test_a_present_keeps_the_reading_of_its_own_request(night):
    refs, readings = _page(night, "m62")
    assert readings == ["reading:m48", "reading:m55"]
    # m48 answered e_p2's page, and m55 answered the glossary clarify m54.
    assert page_readings(night, refs, readings) == ["reading:m48"]


# A seeded run of two requests: e1 asks for the tip, e2 for a receipt.


@pytest.fixture
def db(tmp_path):
    db = init_db(tmp_path / "rota.db")
    for n, (eid, sid, text) in enumerate((("e1", "s1", "tip calculator pls"),
                                          ("e2", "s2", "print a receipt"))):
        db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
                   "(?, 'principal', ?, ?)", (eid, text, n + 1))
        db.execute("INSERT INTO statements (id, span_entry, span_start, "
                   "span_end, text, status) VALUES (?, ?, 0, ?, ?, 'ratified')",
                   (sid, eid, len(text), text))
    for iid, text in (("how_it_works", "The user types the bill."),
                      ("calculate_tip", "The software calculates the tip.")):
        db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                   "version) VALUES (?, ?, 'in_scope', 'draft', 0, 1)",
                   (iid, text))
    db.execute("INSERT INTO refs (src_table, src_id, kind, target) VALUES "
               "('items', 'calculate_tip', 'statement', 's1')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m8', 'th', 'vision_keeper', "
               "'liaison', 'submit', '[]', 0, 'answered')")
    db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, "
               "to_role, verb, body_refs, seq, status) VALUES ('m9', 'th', "
               "'m8', 'liaison', 'principal', 'present', ?, 1, 'open')",
               (json.dumps(["calculate_tip", "s1"]),))
    db.commit()
    return db


def _first_reply(db):
    """His approve of e1's page, and the Liaison's reading of it."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    ask = next(a for a in pending_asks(db) if a.message_id == "m9")
    reply = land(db, ask, parse_reply(ask, "ok"))
    db.commit()
    sb = build("liaison", db, mode="normal", session_id=f"s_{reply}",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = reply
    sb.call("rulings.rule", rulings={"1": "approve", "2": "approve"}, words="ok")
    for w in sb.ctx.writes:
        _apply_write(db, _as_write(w), sb.ctx.role)
    db.commit()
    apply_rulings(db)
    # The two request messages make the boundaries: e2 is the current one.
    for mid, eid, seq in (("m1", "e1", -2), ("m50", "e2", 50)):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                   "verb, body_refs, seq, status) VALUES (?, ?, 'principal', "
                   "'liaison', 'converse', ?, ?, 'answered')",
                   (mid, f"th_{mid}", json.dumps([eid]), seq))
    db.commit()
    return READING_REF + reply


def _send(db, verb, refs):
    from rota.core.sandbox import build

    sb = build("liaison", db, mode="normal", session_id=f"s_send_{verb}")
    sb.ctx.trigger = "m8"
    sb.call(f"msg.{verb}_principal", refs=refs)
    return sb.ctx.outbound[-1]["body_refs"]


def test_the_send_door_puts_a_reading_on_its_own_request_page_only(db):
    ref = _first_reply(db)
    assert readings_owed(db) == [ref]
    assert request_of(db, ref) == "e1"
    # e2's confirm page has no item yet, and its statement names e2.
    assert ref not in _send(db, "confirm", ["s2"])
    assert readings_owed(db, ["s2"]) == []
    assert readings_owed(db, ["calculate_tip"]) == [ref]


def test_a_reading_of_a_delivered_request_shows_on_the_state_view(db):
    ref = _first_reply(db)
    db.execute("INSERT INTO config (key, value) VALUES "
               "('delivered:calculate_tip', '1')")
    db.commit()
    assert readings_owed(db, ["calculate_tip"]) == []
    state = render_state(db)
    assert "Your answers about delivered work, as the team read them:" in state
    assert 'Your answer "ok", as the team read it: 2 lines approved.' in state
    assert ref in readings_owed(db)
