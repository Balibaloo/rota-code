"""W10: the answer door reads the batch fact on every wake.

Night 173 (`plans/w5-w10-count-2026-10-28.md`, section 2). The Terminologist
s112 woke in mode `normal` with no trigger, on `tick:criteria`. It sent
`msg.answer_tester` m29 for c_1 to c_4 before any batch held tk_1. The
door checked the batch only on a park relay, so m29 landed. The Tester s113
woke on m29, and `tests.encode` refused it 12 times: "belongs to no batch".
The rows below are the night's, copied from `.rota/clickI_night173.db`.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import api, prompts

ITEM = "get_app_dir_windows"
TICKET = "tk_1"
CR = "c_1"
SURFACE = "src/click/utils.py::get_app_dir"
C1 = ("When get_app_dir is called on Windows with roaming=True and only "
      "APPDATA is unset (LOCALAPPDATA may be set or unset), it must return "
      "the AppData Roaming folder under the home directory.")
NO_COMMIT = "no change built from this criterion has a commit yet"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES (?, 'in get_app_dir on windows, use the "
                 "appdata folders under the user profile', 'in_scope', "
                 "'approved', 1, 1)", (ITEM,))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, "
                 "'in get_app_dir on windows, when appdata or localappdata is "
                 "not set, use the appdata roaming or appdata local folder "
                 "under the user profile')", (TICKET, ITEM))
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs, "
                 "version) VALUES (?, ?, ?, ?, 1)",
                 (CR, TICKET, C1, json.dumps([SURFACE])))
    conn.commit()
    return conn


def _batch(conn, head_commit):
    conn.execute("INSERT INTO batches (id, item_id, head_commit, status) "
                 "VALUES ('bg_1', ?, ?, 'running')", (ITEM, head_commit))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_1', ?)", (TICKET,))
    conn.commit()


def _s112(conn):
    """A criteria wake: mode `normal` and no trigger, as s112 had."""
    sb = build("terminologist", conn, mode="normal", session_id="s112",
               allow=prompts.mode_tools("terminologist", "normal"))
    sb.ctx.trigger = None
    return sb


def _answers(sb):
    return [m for m in sb.ctx.outbound
            if m["to_role"] == "tester" and m["verb"] == "answer"]


def test_an_answer_before_any_batch_is_refused_on_a_criteria_wake(db):
    sb = _s112(db)
    with pytest.raises(ValueError) as refused:
        sb.call("msg.answer_tester", refs=[CR], round_no=0)
    assert NO_COMMIT in str(refused.value), refused.value
    assert _answers(sb) == []


def test_an_answer_before_the_batch_has_a_commit_is_refused(db):
    _batch(db, None)
    sb = _s112(db)
    with pytest.raises(ValueError) as refused:
        sb.call("msg.answer_tester", refs=[CR], round_no=0)
    assert NO_COMMIT in str(refused.value), refused.value


def test_the_same_answer_lands_once_the_batch_has_a_commit(db):
    _batch(db, "4ad48df87d7782e4b23f9be505fd58b2b03f4f6c")
    sb = _s112(db)
    sb.call("msg.answer_tester", refs=[CR], round_no=0)
    assert [json.loads(m["body_refs"]) if isinstance(m["body_refs"], str)
            else m["body_refs"] for m in _answers(sb)] == [[CR]]


def test_both_doors_read_one_reader(db):
    """`tests.encode` and the answer door read the batch of a criterion
    through `api.criterion_batches`, so they cannot disagree."""
    assert api.criterion_batches(db, CR) == []
    _batch(db, "4ad48df8")
    assert [b["id"] for b in api.criterion_batches(db, CR)] == ["bg_1"]
    assert api._batch_of_criterion(type("C", (), {"conn": db})(), CR) == "bg_1"
