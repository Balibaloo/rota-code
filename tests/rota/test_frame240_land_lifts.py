"""Frame 240: the principal's approve lifts the item's quarantine.

Night 147, the rota workflow (`plans/frame240-scope.md`). The key
`vision_keeper|tick:contested|defines_commands_and_options` quarantined on
its third attempt. The principal then approved the item at m148. `land`
changed the row through a raw `UPDATE` and never called the lift. The walk's
end then told the principal twice that the team gave up on the item.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.roles.principal import Answer, land, pending_asks

ITEM = "defines_commands_and_options"
KEY = f"vision_keeper|tick:contested|{ITEM}"


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _a_page_on_a_quarantined_item(db, approval: str) -> None:
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES (?, 'the tool defines commands and options', "
               "'in_scope', ?, 1, 1)", (ITEM, approval))
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
               "reported) VALUES (?, 3, 1, 1)", (KEY,))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m8','th','vision_keeper',"
               "'liaison','submit',?,0,'answered')", (json.dumps([ITEM]),))
    db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, "
               "to_role, verb, body_refs, seq, status) VALUES ('m9','th','m8',"
               "'liaison','principal','present',?,1,'open')",
               (json.dumps([ITEM]),))
    db.commit()


def _approve(db) -> None:
    ask = pending_asks(db)[0]
    assert ask.message_id == "m9"
    assert land(db, ask, Answer(verb="verdict", per_item={ITEM: "approve"}))
    db.commit()


def _key_rows(db) -> int:
    return db.execute("SELECT COUNT(*) n FROM tick_attempts WHERE tick_key = ?",
                      (KEY,)).fetchone()["n"]


def test_an_approve_of_a_contested_item_lifts_its_quarantine(db):
    _a_page_on_a_quarantined_item(db, "contested")
    _approve(db)
    assert db.execute("SELECT approval FROM items WHERE id = ?",
                      (ITEM,)).fetchone()["approval"] == "approved"
    assert _key_rows(db) == 0, "the approve moved the item, so the key lifts"


def test_an_approve_of_an_approved_item_keeps_its_quarantine(db):
    # Frame 80: a write that sets the value the row holds moves nothing.
    _a_page_on_a_quarantined_item(db, "approved")
    _approve(db)
    assert _key_rows(db) == 1, "a same-value write revives nothing"
