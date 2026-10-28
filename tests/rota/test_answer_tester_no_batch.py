"""W10: a message to a Tester or a Developer lands only on a built batch.

Night 173 (`plans/w5-w10-count-2026-10-28.md`, section 2). The Terminologist
s112 woke in mode `normal` with no trigger, on `tick:criteria`. It sent
`msg.answer_tester` m29 for c_1 to c_4 before any batch held tk_1, and the
woken Tester s113 was refused 12 times: "belongs to no batch". Night 169's
s113 asked with no batch (m30), and the answer m31 woke s115 into the same
refusal (`plans/w10-review-p1.md`, findings 1 and 5). Night 147's s315 met a
ticket in two batches (finding 2). The rows are night 173's, copied from
`.rota/clickI_night173.db`.
"""
from __future__ import annotations

import ast
import inspect
import json

import pytest

from rota.core import sandbox
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
NO_COMMIT = "has a commit yet"


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


def _batch(conn, head_commit, bid="bg_1", status="running"):
    conn.execute("INSERT INTO batches (id, item_id, head_commit, status) "
                 "VALUES (?, ?, ?, ?)", (bid, ITEM, head_commit, status))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "(?, ?)", (bid, TICKET))
    conn.commit()


def _s112(conn):
    """A criteria wake: mode `normal` and no trigger, as s112 had."""
    sb = build("terminologist", conn, mode="normal", session_id="s112",
               allow=prompts.mode_tools("terminologist", "normal"))
    sb.ctx.trigger = None
    return sb


def _sent(sb, to):
    return [m for m in sb.ctx.outbound if m["to_role"] == to]


def test_an_answer_before_any_batch_is_refused_on_a_criteria_wake(db):
    sb = _s112(db)
    with pytest.raises(ValueError) as refused:
        sb.call("msg.answer_tester", refs=[CR], round_no=0)
    said = str(refused.value)
    assert NO_COMMIT in said and CR in said, said
    assert len(said.split()) < 25, said
    assert _sent(sb, "tester") == []


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
    assert len(_sent(sb, "tester")) == 1


def test_a_tester_with_no_batch_cannot_ask(db):
    """Night 169's m30 shape: a Tester woken by a message holds no batch."""
    sb = build("tester", db, mode="answer", session_id="s113",
               allow=prompts.mode_tools("tester", "answer"))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m29', 'm29', 'terminologist', 'tester', "
               "'answer', '[\"c_1\"]', 29)")
    sb.ctx.trigger = "m29"
    with pytest.raises(ValueError) as refused:
        sb.call("msg.question_terminologist", refs=[CR],
                question="what does roaming mean here?")
    assert NO_COMMIT in str(refused.value), refused.value
    assert _sent(sb, "terminologist") == []


def test_a_vision_keeper_answer_to_a_tester_with_no_batch_is_refused(db):
    """Night 169's m31 pair, `vision_keeper` to `tester`."""
    sb = build("vision_keeper", db, mode="normal", session_id="s114")
    sb.ctx.trigger = None
    with pytest.raises(ValueError) as refused:
        sb.call("msg.answer_tester", refs=[ITEM], round_no=0)
    assert NO_COMMIT in str(refused.value), refused.value


def test_a_ticket_in_two_batches_gives_both_doors_one_answer(db):
    """Night 147's s315 shape: one batch merged, one batch running."""
    _batch(db, "4ad48df8", "bg_1", "merged")
    _batch(db, "9f00aa11", "bg_9", "running")
    assert api.built_batch(db, CR)["id"] == "bg_9"
    ctx = type("C", (), {"conn": db})()
    assert api._batch_of_criterion(ctx, CR) == "bg_9"
    sb = _s112(db)
    sb.call("msg.answer_tester", refs=[CR], round_no=0)
    assert len(_sent(sb, "tester")) == 1


def test_a_merged_batch_is_built_and_an_abandoned_one_is_not(db):
    """Night 147's s315: bg_2 abandoned, bg_3 merged. Built means a commit,
    a merged batch included (the coordinator's ruling on pass 1b)."""
    _batch(db, "4ad48df8", "bg_2", "abandoned")
    assert api.built_batch(db, CR) is None
    _batch(db, "9f00aa11", "bg_3", "merged")
    assert api.built_batch(db, CR)["id"] == "bg_3"


def test_two_abandoned_batches_refuse(db):
    _batch(db, "4ad48df8", "bg_2", "abandoned")
    _batch(db, "9f00aa11", "bg_4", "abandoned")
    assert api.built_batch(db, CR) is None
    sb = _s112(db)
    with pytest.raises(ValueError):
        sb.call("msg.answer_tester", refs=[CR], round_no=0)


def test_one_reader_holds_the_criterion_to_batch_query():
    """A second query of a criterion's batches cannot return to either door."""
    for fn in (sandbox._unbuilt_refusal, api._batch_of_criterion,
               sandbox._ruling_answer_refusal):
        src = inspect.getsource(fn)
        assert "head_commit" not in src, fn
        calls = {getattr(n.func, "attr", getattr(n.func, "id", None))
                 for n in ast.walk(ast.parse(src.strip())) if isinstance(n, ast.Call)}
        assert "built_batch" in calls, fn
    assert "_unbuilt_refusal(ctx, recipient, verb" in inspect.getsource(sandbox._bind_send)


def test_a_refusal_over_many_refs_stays_under_25_words(db):
    for n in range(2, 6):
        db.execute("INSERT INTO criteria (id, ticket_id, text, version) "
                   "VALUES (?, ?, ?, 1)", (f"c_{n}", TICKET, C1))
    sb = _s112(db)
    with pytest.raises(ValueError) as refused:
        sb.call("msg.answer_tester", refs=[CR, "c_2", "c_3", "c_4", "c_5"], round_no=0)
    said = str(refused.value)
    assert "and 2 more" in said and len(said.split()) < 25, said
