"""
Frame 272, pass 1: a reply in `recent_chat` names the page it answered.

The Liaison's converse wake carried his earlier replies as text alone. Their
line numbers belong to earlier pages, and the seat read them against the
present page. Night 159's s239 contested lines 1 to 3 of page m116 from m106,
which answered page m105. Night 158's s209 read m62's "Line 2 is wrong",
which answered page m61, against page m90 (`plans/frame305-interview.md`,
sections 5 and 6).

Each test rebuilds the night's shape inline, with ledger notes as the rows.
The night databases are ignored by git.
"""
from __future__ import annotations

import json
import re

import pytest

from rota.core.db import init_db
from rota.core.runner import _recent_chat, resolve_inbound
from rota.core.scheduler import Wake
from rota.roles import principal

M106 = ("Line 1 is wrong because this page should cover only the confirm flag. "
        "Line 2 should say that the flag defaults to False.")
M51 = "Line 2 is wrong: the change lives in confirm() itself."
M117 = "Line 3 is off: confirm aborts today."
SAID = "Here is the page."


def _msg(conn, mid, cause, from_role, to_role, verb, refs, seq, text=None):
    conn.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, verb, "
                 "body_refs, body_text, status, seq) VALUES (?, 't', ?, ?, ?, ?, ?, ?, "
                 "'open', ?)", (mid, cause, from_role, to_role, verb, json.dumps(refs),
                                text, seq))


def _notes(conn, *ids):
    for lid in ids:
        conn.execute("INSERT OR IGNORE INTO ledger (id, about_ref, about_table, "
                     "default_taken, status, author) VALUES (?, 'confirm', 'items', ?, "
                     "'open', 'developer')", (lid, f"the team assumed {lid}"))


def _shown(conn, reply, order):
    """The order of the page as the principal saw it at `reply`, as
    `principal.land` records it."""
    conn.execute("INSERT INTO config (key, value) VALUES (?, ?)",
                 (f"order:{reply}", json.dumps(order)))


@pytest.fixture
def s239(tmp_path):
    """Page m105 and his reply through `principal.land`, then page m116 with
    other rows and his reply m117, the wake. Page m105 showed bg_2_summary
    as line 1, and the row left the page before s239 woke (frame 272,
    review 1, finding 1)."""
    conn = init_db(tmp_path / "rota.db")
    old = ["l_bg2", "l_echo", "l_bg3"]
    new = ["l_n1", "l_n2", "l_n3", "l_n4"]
    _notes(conn, *old, *new)
    _msg(conn, "m105", None, "liaison", "principal", "present", old, 1)
    conn.commit()
    (ask,) = principal.pending_asks(conn)
    assert ask.order == old
    reply = principal.land(conn, ask, principal.Answer(verb="reply", text=M106))
    conn.execute("DELETE FROM ledger WHERE id = 'l_bg2'")
    _msg(conn, "m115", None, "liaison", "principal", "converse", [], 3, SAID)
    _msg(conn, "m116", "m115", "liaison", "principal", "present", new, 4)
    _msg(conn, "m117", "m116", "principal", "liaison", "converse", new, 5, M117)
    conn.commit()
    assert "l_bg2" not in principal.render_page(conn, "present", old)[1]
    return conn


def test_a_reply_to_an_earlier_page_names_the_rows_he_saw(s239):
    """s239's shape: m106's "Line 1" and "Line 2" are rows of m105 as he
    saw it, though bg_2_summary has left that page since."""
    wake = Wake(role="liaison", kind="message", message_id="m117", detail="converse")
    chat = resolve_inbound(s239, wake)["recent_chat"]
    (m106,) = [t for t in chat if t["from"] == "principal"]
    assert m106["page"] == "m105"
    assert m106["text"] == (
        "Row l_bg2 of page m105 is wrong because this page should cover only the "
        "confirm flag. Row l_echo of page m105 should say that the flag defaults "
        "to False.")
    assert not re.search(r"\bline\s+[12]\b", m106["text"], re.I)


def test_two_replies_to_one_page_each_read_the_list_he_saw(s239):
    """A second reply to the open page m105, after its line 1 left the page.
    Each reply names the rows of its own list (frame 272, review 2,
    finding 1)."""
    (ask,) = [a for a in principal.pending_asks(s239) if a.message_id == "m105"]
    assert ask.order == ["l_echo", "l_bg3"]
    principal.land(s239, ask, principal.Answer(verb="reply", text="Line 1 is wrong."))
    s239.execute("UPDATE messages SET seq = 9 WHERE id = 'm117'")
    s239.commit()
    replies = [t["text"] for t in _recent_chat(s239, "m117", page="m116")
               if t["from"] == "principal"]
    assert replies == [
        "Row l_bg2 of page m105 is wrong because this page should cover only the "
        "confirm flag. Row l_echo of page m105 should say that the flag defaults "
        "to False.",
        "Row l_echo of page m105 is wrong."]


def test_the_landing_carries_no_page_id(s239):
    """"Of page m105" in `recent_chat` names another page by itself, and a
    reply to this page keeps its numbers, so the landing block carries no
    page id. The key alone costs one run of five on one L1 Liaison case on
    qwen3:8b, 1 of 5 with it and 2 of 5 without on one load (frame 272,
    review 1, finding 2, read again at the gate of d6a36081, 2026-10-23)."""
    wake = Wake(role="liaison", kind="message", message_id="m117", detail="converse")
    out = resolve_inbound(s239, wake)
    assert "page_id" not in out["landing"]
    assert out["landing"]["page_kind"] == "present"
    (m106,) = [t for t in out["recent_chat"] if t["from"] == "principal"
               and t.get("page") == "m105"]
    assert "of page m105" in m106["text"]


def test_a_page_with_no_recorded_order_keeps_his_numbers(s239):
    """An earlier page is never rendered from today's rows."""
    s239.execute("DELETE FROM config WHERE key LIKE 'order:%'")
    (m106,) = [t for t in _recent_chat(s239, "m117", page="m116")
               if t["from"] == "principal"]
    assert m106 == {"from": "principal", "page": "m105", "text": M106}


def test_a_line_the_present_page_shows_too_names_the_old_page(tmp_path):
    """s209's shape with the m51 doubt: m51 faulted the guess line of page
    m50, and page m89 shows the same guess as its line 2. The row id alone
    names a row of m89, so the page travels with it."""
    conn = init_db(tmp_path / "rota.db")
    _notes(conn, "l_cdoe", "l_guess", "l_cmd")
    _msg(conn, "m50", None, "liaison", "principal", "present", ["l_cdoe", "l_guess"], 1)
    _msg(conn, "m51", "m50", "principal", "liaison", "converse",
         ["l_cdoe", "l_guess"], 2, M51)
    _shown(conn, "m51", ["l_cdoe", "l_guess"])
    _msg(conn, "m89", None, "liaison", "principal", "present", ["l_cmd", "l_guess"], 3)
    _msg(conn, "m90", "m89", "principal", "liaison", "converse",
         ["l_cmd", "l_guess"], 4, "Line 1 is wrong.")
    conn.commit()
    (m51,) = _recent_chat(conn, "m90", page="m89")
    assert m51 == {"from": "principal", "page": "m50",
                   "text": "Row l_guess of page m50 is wrong: the change lives in "
                           "confirm() itself."}


def test_a_reply_to_the_present_page_keeps_its_numbers(s239):
    """m106 and the wake answer one page, so its numbers are that page's."""
    s239.execute("UPDATE messages SET cause_id = 'm105' WHERE id = 'm117'")
    (m106,) = [t for t in _recent_chat(s239, "m117", page="m105")
               if t["from"] == "principal"]
    assert m106 == {"from": "principal", "page": "m105", "text": M106}


def test_a_liaison_turn_and_a_reply_with_no_page_are_unchanged(s239):
    """Only a principal reply to a page carries a page."""
    _msg(s239, "m118", None, "principal", "liaison", "converse", [], 6, "Line 4 again.")
    s239.commit()
    chat = _recent_chat(s239, "m117", page="m116")
    assert {"from": "liaison", "text": SAID} in chat
    assert chat[-1] == {"from": "principal", "text": "Line 4 again."}
