"""W14, pass 1: a `remove` on a criterion's own row takes the row away.

On nights 170 to 175 he deleted a criterion 15 times in landed rulings. 3
carried the act `drop` and retired the row. 6 carried `remove` with the kind
`row`, and nothing read them. Night 175 stopped on two such rows: c_2 and c_3
stayed live with no test, and the walk gave up (the W14 read, question 1).
The one reader is `_dropped_line`, so every door that asks "does his ruling
take this row away" reads the same answer.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import backfill_ruled_refs, init_db
from rota.core.runner import _wake_allow
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles.api import _dropped_line, criteria_page_acts
from rota.testkit.fixtures import seed_acts, seed_verdict

ITEM = "format_filename_example"
TICKET = "tk_1_format_filename_example"
CRITERIA = {
    "c_1_format_filename_example": "The docstring for format_filename must "
        "include an example showing that when shorten=True, the path a/b/c.txt "
        "is displayed as c.txt.",
    "c_2_format_filename_example": "The docstring for format_filename must "
        "include exactly one example showing that when shorten=True, the path "
        "a/b/c.txt is displayed as c.txt.",
}
C1, C2 = CRITERIA
PAGE = [ITEM, C1, C2, "bg_3"]
WORDS = "Remove line 3, because I asked for only one example."


def _message(conn, mid, cause, sender, to, verb, refs, seq, text=None):
    conn.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
                 "to_role, verb, body_refs, body_text, seq) VALUES "
                 "(?, ?, 'm116', ?, ?, ?, ?, ?, ?)",
                 (mid, cause, sender, to, verb, json.dumps(refs), text, seq))


def _page(tmp_path, act: dict):
    """Night 175's page, his contest of line 3 and the seat's `act` on it."""
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES (?, 'Give format_filename one example in "
                 "its docstring.', 'in_scope', 'approved', 1, 1)", (ITEM,))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, "
                 "'one docstring example')", (TICKET, ITEM))
    for cid, text in CRITERIA.items():
        conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                     "(?, ?, ?)", (cid, TICKET, text))
    _message(conn, "m116", None, "liaison", "principal", "present", PAGE, 116)
    _message(conn, "m118", "m116", "principal", "liaison", "converse", PAGE,
             118, WORDS)
    _message(conn, "m119", "m116", "principal", "liaison", "verdict", [C2],
             119)
    _message(conn, "m120", "m119", "liaison", "terminologist", "relay", [C2],
             120)
    seed_verdict(conn, "m119", json.dumps({C2: "contest"}))
    conn.execute("INSERT INTO config (key, value) VALUES ('order:m118', ?)",
                 (json.dumps(PAGE),))
    per_item = {r: ("contest" if r == C2 else "approve") for r in PAGE}
    conn.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
                 "status, verdict_id, texts) VALUES ('r_m118', 'm116', 'm118', "
                 "?, ?, 'landed', 'm119', ?)",
                 (json.dumps(per_item), WORDS, json.dumps({C2: CRITERIA[C2]})))
    backfill_ruled_refs(conn)
    seed_acts(conn, "r_m118", {C2: {"words": WORDS, **act}})
    return conn


def _repair(conn, door: bool = False):
    """The relay wake. `door` offers `criteria.retire` on every ruling, so a
    test reaches the door's own refusal."""
    wake = Wake("terminologist", "message", message_id="m120", refs=(C2,),
                detail="relay")
    allow = _wake_allow(wake, conn)
    if door and "criteria.retire" not in allow:
        allow = allow + ["criteria.retire"]
    sb = build("terminologist", conn, mode="criterion_repair",
               session_id="s285", allow=allow)
    sb.ctx.trigger = "m120"
    return sb


@pytest.mark.parametrize("act", [
    {"act": "remove", "target_kind": "row"},
    {"act": "drop", "target_kind": "row"},
], ids=["remove-row", "drop-row"])
def test_a_delete_of_the_row_retires_the_criterion(tmp_path, act):
    conn = _page(tmp_path, act)
    assert _dropped_line(conn, C2) == 3, "the line he saw"
    assert criteria_page_acts(conn, [C2])["retire"] == [C2]
    sb = _repair(conn)
    sb.call("criteria.retire", id=C2)
    assert sb.ctx.writes, "the retire stages a write"


@pytest.mark.parametrize("act", [
    # Night 175's r_m118 carried `remove` on c_1 against his words. A target
    # that names the criterion itself is not a delete of its page line.
    {"act": "remove", "target_kind": "row", "target": C2},
    # A source line is code. Its delete leaves the criterion on the page.
    {"act": "remove", "target_kind": "source_line", "target": C2},
    {"act": "remove", "target_kind": "source_line",
     "target": "format_filename:12"},
    # A remove with no kind names no row.
    {"act": "remove"},
], ids=["remove-row-on-its-own-id", "remove-source-line-on-its-id",
        "remove-source-line", "remove-no-kind"])
def test_a_remove_that_names_no_page_line_retires_nothing(tmp_path, act):
    conn = _page(tmp_path, act)
    assert _dropped_line(conn, C2) is None
    assert criteria_page_acts(conn, [C2])["retire"] == []
    sb = _repair(conn, door=True)
    with pytest.raises(ValueError, match="no ruling of the principal drops"):
        sb.call("criteria.retire", id=C2)


def test_a_row_with_no_act_stays_no_act(tmp_path):
    conn = _page(tmp_path, {})
    assert criteria_page_acts(conn, [C2])["retire"] == []
