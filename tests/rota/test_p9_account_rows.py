"""P9: the account's rows leave a request's page.

Night 172 (`plans/f1-f15-f21-night172-read.md`, W9). s179, woken by
`tick:observed_entries`, sent 19 glossary and constraint rows, and the send
door added the open request, so m71 put them under clear(). s272, woken by
`tick:agenda`, sent 7 claims about constraints, and m130 put them under
format_filename. `row_items` gives no item for those rows, `off_page` kept a
row of no item, and `request_rows` added the open request (frame 190's
design, 2.1).

Roman ruled on 2026-10-28 at 09:10, "Yeah that's right": the account's own
rows, the glossary terms, the constraints and the claims, go on their own
page and never on a request's page (frame 344, frame 241's mechanism).
"""
from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

import pytest

from rota.core.predicates import Wake
from rota.core.sandbox import build
from rota.roles import prompts
from rota.roles.principal import READING_REF, _page_body, off_page, request_rows

NIGHT = Path(__file__).resolve().parents[2] / ".rota" / "clickI_night172.db"
if not NIGHT.exists():
    NIGHT = Path("D:/repos/rota/.rota/clickI_night172.db")

ACCOUNT = "What the project does today. This is not your request:"
REQUESTS = ("clear_returns_status", "format_filename_example")


@pytest.fixture
def night(tmp_path):
    """A copy of the night 172 register. The night's file is never opened in
    place. The deliveries are undone, so a request is open at each send."""
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


def _wake_refs(conn, session):
    return json.loads(conn.execute("SELECT wake_refs FROM sessions WHERE id = ?",
                                   (session,)).fetchone()[0])


@pytest.mark.parametrize("session, kind, n", [
    ("s179", "tick:observed_entries", 19),
    ("s272", "tick:agenda", 7),
])
def test_rows_of_no_request_make_the_account_page(night, session, kind, n):
    refs = _wake_refs(night, session)
    assert len(refs) == n
    sb = build("liaison", night, mode="normal", session_id=f"{session}_again",
               allow=prompts.mode_tools("liaison", "normal"),
               wake=Wake("liaison", kind, refs=tuple(refs)))
    sb.call("msg.present_principal", refs=refs, round_no=0)
    sent = [r for r in sb.ctx.outbound[-1]["body_refs"]
            if not r.startswith(READING_REF)]
    assert sent == refs + ["how_it_works"], sent
    page, order = _page_body(night, "present", sent, ask_id="m_again")
    assert order == ["how_it_works"] + refs
    assert ACCOUNT in page
    assert "It must:" not in page
    assert not any(r in page for r in REQUESTS)


def test_request_rows_give_the_account_for_rows_of_no_request(night):
    for session in ("s179", "s272"):
        assert request_rows(night, _wake_refs(night, session)) == ["how_it_works"]


@pytest.mark.parametrize("mid, session", [("m71", "s179"), ("m130", "s272")])
def test_a_request_page_numbers_no_row_of_no_request(night, mid, session):
    stored = json.loads(night.execute("SELECT body_refs FROM messages WHERE id = ?",
                                      (mid,)).fetchone()[0])
    rows = set(_wake_refs(night, session))
    assert rows <= set(stored)
    assert rows <= off_page(night, stored)
    _, order = _page_body(night, "present", stored, ask_id=mid)
    assert not rows & set(order)
    assert any(r in order for r in REQUESTS)


def test_a_note_about_the_request_statement_stays_on_its_page(tmp_path):
    """A seat's note about a statement that no item cites yet is the
    request's row, and a note about a code area is the account's."""
    from rota.core.db import init_db
    from rota.roles.principal import request_of

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e1', 'principal', 'print a receipt', 1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1', 'e1', 0, 15, 'print a receipt', "
               "'ratified')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m1', 'm1', 'principal', "
               "'liaison', 'converse', '[\"e1\"]', 1, 'answered')")
    for lid, about, table in (("l_1", "s1", "statements"),
                              ("l_2", "src/click", "areas")):
        db.execute("INSERT INTO ledger (id, about_ref, about_table, "
                   "default_taken, status, author) VALUES (?, ?, ?, "
                   "'a guess', 'open', 'terminologist')", (lid, about, table))
    db.commit()
    assert request_of(db, "l_1") == "e1"
    assert request_of(db, "l_2") is None
    assert off_page(db, ["s1", "l_1", "l_2"]) == {"l_2"}


def test_a_row_about_the_account_item_alone_is_off_a_request_page(night):
    """The review's probe p1: a claim, a ledger note, a glossary term and a
    constraint that reach only how_it_works were lines 4 to 7 of e_p3's
    page."""
    night.execute("INSERT INTO ledger (id, about_ref, about_table, "
                  "default_taken, kind, status, author) VALUES "
                  "('challenge_items_how_it_works', 'items:how_it_works', "
                  "'items', 'the account holds', 'default', 'open', 'critic')")
    for target in ("command", "argument"):
        night.execute("INSERT INTO refs (src_table, src_id, kind, target, "
                      "resolves) VALUES ('items', 'how_it_works', 'statement', "
                      "?, 1)", (target,))
    account = ["command", "argument", "challenge_items_how_it_works",
               "l_e7c6ed5501"]
    refs = ["format_filename_example", "c_1_format_filename_example"] + account
    assert off_page(night, refs) == set(account)
    _, order = _page_body(night, "present", refs, ask_id="m_probe")
    assert not set(account) & set(order)
    assert "format_filename_example" in order


@pytest.mark.parametrize("session, kind, n", [
    ("s179", "tick:observed_entries", 19),
    ("s272", "tick:agenda", 7),
])
def test_the_account_page_needs_no_account_row(night, session, kind, n):
    """The review's probe p5: with no how_it_works row, the door added the
    open request and then dropped every row the wake named."""
    night.execute("DELETE FROM items WHERE id = 'how_it_works'")
    refs = _wake_refs(night, session)
    sb = build("liaison", night, mode="normal", session_id=f"{session}_bare",
               allow=prompts.mode_tools("liaison", "normal"),
               wake=Wake("liaison", kind, refs=tuple(refs)))
    sb.call("msg.present_principal", refs=refs, round_no=0)
    sent = [r for r in sb.ctx.outbound[-1]["body_refs"]
            if not r.startswith(READING_REF)]
    assert sent == refs, sent
    page, order = _page_body(night, "present", sent, ask_id="m_bare")
    assert order == refs and len(order) == n
    assert "You asked:" not in page
    assert not any(r in page for r in REQUESTS)
