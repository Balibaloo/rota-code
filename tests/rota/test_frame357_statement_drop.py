"""
Frame 357: a landed drop on a statement ends it.

Dry1's turn 11: the confirm m71 asked about `s2` and `s3`, and the seat
answered m75, "Drop both". The Liaison ruled `drop` on both and r_m75
landed. Nothing wrote an end status, so `awaiting_confirm` asked again as
m77, the seat's "ok" was ruled approve, and `brief_ratify` admitted the
request he had dropped. The fixture copies dry1's rows by hand, from the
dry1w6 copy, so no database file travels.
"""
from __future__ import annotations

import json
import sqlite3

import pytest

from rota.core.db import init_db
from rota.core.predicates import awaiting_confirm
from rota.roles.principal import (apply_rulings, contested_statement,
                                  off_page)

S1 = ("Make click.pause() return True when it waited for a key and False when "
      "it skipped because stdin or stdout is not a terminal.")
E70 = "Write the tests again. The surface is click.pause in src/click/termui.py."
M75 = ("No. Those two sentences were not new requests. Drop both. I was telling "
       "you to write the tests for the change you stopped.")


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _msg(db, mid, seq, frm, to, verb, refs, *, cause=None, thread=None,
         status="answered", text=None):
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, body_text, seq, status) VALUES "
               "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (mid, cause, thread or mid, frm, to, verb, json.dumps(refs),
                text, seq, status))


def _dry1_turn11(db):
    """Dry1's rows up to m75, with r_m75 read and not yet landed."""
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m1', 'principal', ?, 1), ('e_m70', 'principal', ?, 26)",
               (S1, E70))
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1', 'e_m1', 0, 124, ?, 'ratified'), "
               "('s2', 'e_m70', 0, 22, 'Write the tests again.', 'proposed'), "
               "('s3', 'e_m70', 23, 73, "
               "'The surface is click.pause in src/click/termui.py.', 'proposed')",
               (S1,))
    _msg(db, "m1", 1, "principal", "liaison", "converse", ["e_m1"], text=S1)
    _msg(db, "m70", 70, "principal", "liaison", "converse", ["e_m70"], text=E70)
    _msg(db, "m71", 71, "liaison", "principal", "confirm", ["s2", "s3"],
         cause="m70", thread="m70", status="open")
    _msg(db, "m75", 77, "principal", "liaison", "converse", ["s2", "s3"],
         cause="m71", thread="m70", text=M75)
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words) "
               "VALUES ('r_m75', 'm71', 'm75', ?, ?)",
               (json.dumps({"s2": "contest", "s3": "contest"}), M75))
    for line, sid in ((1, "s2"), (2, "s3")):
        db.execute("INSERT INTO ruled_refs (id, ruling_id, ref, line, verdict, "
                   "act, target_kind, words, words_from, ref_version, source) "
                   "VALUES (?, 'r_m75', ?, ?, 'contest', 'drop', 'row', ?, "
                   "'m75', 1, 'reading')", (f"rr_read_{sid}", sid, line, M75))
    db.commit()


def _status(db, sid):
    return db.execute("SELECT status FROM statements WHERE id = ?",
                      (sid,)).fetchone()["status"]


def _sandbox(db, mode, trigger):
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = build("liaison", db, mode="normal", session_id="sess_357",
               allow=prompts.mode_tools("liaison", mode))
    sb.ctx.trigger = trigger
    return sb


def test_the_landed_drop_writes_dropped_on_s2_and_s3(db):
    _dry1_turn11(db)
    apply_rulings(db)
    db.commit()
    assert db.execute("SELECT status FROM rulings WHERE id = 'r_m75'"
                      ).fetchone()["status"] == "landed"
    assert [_status(db, s) for s in ("s1", "s2", "s3")] == [
        "ratified", "dropped", "dropped"]


def test_awaiting_confirm_wakes_nobody_for_the_dropped_statements(db):
    _dry1_turn11(db)
    apply_rulings(db)
    db.commit()
    # m71 closed at the landing, so no confirm is outstanding. Dry1's s177
    # woke here and sent m77.
    assert not db.execute("SELECT 1 FROM messages WHERE status = 'open' "
                          "AND to_role = 'principal'").fetchone()
    assert awaiting_confirm(db) == []


def test_brief_ratify_refuses_an_approve_on_a_dropped_statement(db):
    """Dry1's m77 and m78: a second confirm and his "ok", ruled approve. The
    approve is the newest ruling, and the drop still holds."""
    _dry1_turn11(db)
    apply_rulings(db)
    _msg(db, "m77", 80, "liaison", "principal", "confirm",
         ["s2", "s3", "reading:m75"], status="open")
    _msg(db, "m78", 81, "principal", "liaison", "converse",
         ["s2", "s3", "reading:m75"], cause="m77", thread="m77", text="ok")
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words) "
               "VALUES ('r_m78', 'm77', 'm78', ?, 'ok')",
               (json.dumps({"s2": "approve", "s3": "approve",
                            "reading:m75": "approve"}),))
    db.commit()
    apply_rulings(db)
    db.commit()
    assert [_status(db, s) for s in ("s2", "s3")] == ["dropped", "dropped"]
    assert contested_statement(db, "s2", confirm_only=True) == "r_m75"
    sb = _sandbox(db, "verdict", "m78")
    with pytest.raises(ValueError, match="contested s2 in r_m75"):
        sb.call("brief.ratify", id="s2")
    assert not sb.ctx.writes


def test_a_confirm_page_carries_no_dropped_statement(db):
    _dry1_turn11(db)
    apply_rulings(db)
    db.commit()
    assert off_page(db, ["s2", "s3"], confirm=True) == {"s2", "s3"}


def test_a_statement_with_no_drop_keeps_todays_path(db):
    """A contest with no drop act leaves the statement proposed, and the
    contest refuses the ratify as before."""
    _dry1_turn11(db)
    db.execute("DELETE FROM ruled_refs")
    db.execute("INSERT INTO ruled_refs (id, ruling_id, ref, line, verdict, "
               "words, words_from, ref_version, source) VALUES "
               "('rr_read_s2', 'r_m75', 's2', 1, 'contest', 'not this', 'm75', "
               "1, 'reading')")
    db.execute("UPDATE rulings SET per_item = ? WHERE id = 'r_m75'",
               (json.dumps({"s2": "contest", "s3": "approve"}),))
    db.commit()
    apply_rulings(db)
    db.commit()
    assert [_status(db, s) for s in ("s2", "s3")] == ["proposed", "proposed"]
    assert off_page(db, ["s2", "s3"], confirm=True) == set()
    sb = _sandbox(db, "verdict", "m75")
    with pytest.raises(ValueError, match="contested s2 in r_m75"):
        sb.call("brief.ratify", id="s2")
    sb.call("brief.ratify", id="s3")
    assert sb.ctx.writes[-1][1:3] == ("s3", {"status": "ratified"})


def test_an_older_statements_table_takes_the_new_status(tmp_path):
    """A live run's file has the old CHECK. `init_db` builds the table again
    and keeps its rows."""
    path = tmp_path / "old.db"
    init_db(path).close()
    raw = sqlite3.connect(path)
    sql = raw.execute("SELECT sql FROM sqlite_master WHERE name = 'statements'"
                      ).fetchone()[0]
    old = sql.replace(",\n                         'dropped'", "")
    assert "'dropped'" not in old
    raw.execute("PRAGMA foreign_keys = OFF")
    raw.execute("DROP TABLE statements")
    raw.execute(old)
    raw.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
                "('e1', 'principal', 'x y', 1)")
    raw.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
                "text, status) VALUES ('s1', 'e1', 0, 1, 'x', 'proposed'), "
                "('s2', 'e1', 2, 3, 'y', 'ratified')")
    raw.execute("UPDATE statements SET supersedes = 's1' WHERE id = 's2'")
    raw.commit()
    raw.close()
    conn = init_db(path)
    conn.execute("UPDATE statements SET status = 'dropped' WHERE id = 's1'")
    assert [tuple(r) for r in conn.execute(
        "SELECT id, status, supersedes FROM statements ORDER BY id")] == [
        ("s1", "dropped", None), ("s2", "ratified", "s1")]
    assert conn.execute("SELECT 1 FROM sqlite_master WHERE name = "
                        "'ix_statements_status'").fetchone()
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
