"""Frame 303, the case (night 162, 2026-10-24): the Architect s228 sent a
textless report m108 with refs `["b_2"]`. The report edge carries refs only
(ruled 2026-08-15, `rota/SYSTEM.md` line 64). The runner resolved no batch
row, so the Liaison s232 read `["b_2"]` and nothing about it. s232 wrote
the invoice example of its own brief as the question m110.

The fixture holds night 162's rows in the same shape: the item, the merged
batch b_2, the critic's pass verdict, and the messages m106 and m108."""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.runner import build_prompt, resolve_inbound
from rota.core.sandbox import build
from rota.core.scheduler import Wake

ITEM = ("Let confirm() take a default_on_eof flag: when stdin is closed it "
        "returns the default instead of aborting. The flag defaults to False, "
        "so nothing changes for existing callers.")
HEAD = "8717098b9704d2d09bb7ae417709bbfa79ab3e27"


@pytest.fixture
def night(tmp_path):
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('confirm_default_on_eof',?,'in_scope',"
               "'approved',2,2)", (ITEM,))
    db.execute("INSERT INTO batches (id, item_id, head_commit, status) "
               "VALUES ('b_2','confirm_default_on_eof',?,'merged')", (HEAD,))
    db.execute("INSERT INTO verdicts (id, batch_id, commit_sha, diff_ref, "
               "result, reason, lines) VALUES (?, 'b_2', ?, '', 'pass', '', "
               "'{}')", (f"critic:b_2:{HEAD}", HEAD))
    for mid, to, verb in (("m106", "developer", "answer"),
                          ("m108", "liaison", "report")):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                   "verb, body_refs, seq) VALUES (?,?,'architect',?,?,"
                   "'[\"b_2\"]',?)", (mid, mid, to, verb, int(mid[1:])))
    db.commit()
    return db


def _user(db, role, message_id, verb):
    wake = Wake(role=role, kind="message", message_id=message_id,
                detail=verb)
    sb = build(role, db)
    _system, user = build_prompt(role, sb, wake, {}, f"MODE: {verb}",
                                 resolve_inbound(db, wake))
    return user


def test_s232_s_wake_carries_b_2_s_item_text(night):
    # s228's shape: a textless report that names the batch only.
    user = _user(night, "liaison", "m108", "report")
    assert ITEM in user
    assert '"status": "merged"' in user


def test_the_batch_row_holds_its_state_and_last_verdict(night):
    wake = Wake(role="liaison", kind="message", message_id="m108",
                detail="report")
    row = resolve_inbound(night, wake)["resolved_refs"]["b_2"]
    assert row["table"] == "batches"
    assert row["item_id"] == "confirm_default_on_eof"
    assert row["item_text"] == ITEM
    assert row["status"] == "merged"
    assert row["head_commit"] == HEAD
    assert row["last_verdict"] == {"result": "pass", "commit_sha": HEAD}


def test_a_pass_on_an_older_commit_names_that_commit(night):
    # Review 1, finding 2: a pass on an older commit is no pass on the head.
    night.execute("UPDATE batches SET head_commit = 'f00d' WHERE id = 'b_2'")
    wake = Wake(role="liaison", kind="message", message_id="m108",
                detail="report")
    row = resolve_inbound(night, wake)["resolved_refs"]["b_2"]
    assert row["head_commit"] == "f00d"
    assert row["last_verdict"]["commit_sha"] == HEAD


def test_a_later_verdict_is_the_last_verdict(night):
    night.execute("INSERT INTO verdicts (id, batch_id, commit_sha, diff_ref, "
                  "result, reason, lines) VALUES "
                  "('v2','b_2','abc','','fail','the default is lost','{}')")
    wake = Wake(role="liaison", kind="message", message_id="m108",
                detail="report")
    row = resolve_inbound(night, wake)["resolved_refs"]["b_2"]
    assert row["last_verdict"] == {"result": "fail", "commit_sha": "abc",
                                   "reason": "the default is lost"}


def test_a_developer_wake_on_the_batch_is_unchanged(night):
    # m106 woke the Developer with the same refs. Its prompt keeps its shape,
    # so its recordings stay green.
    wake = Wake(role="developer", kind="message", message_id="m106",
                detail="answer")
    assert "b_2" not in resolve_inbound(night, wake).get("resolved_refs", {})
