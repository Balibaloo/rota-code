"""
Frame 318, row 6: a criteria move lifts only the keys it can change.

Night 163: three Developers met the same note refusal at termui.py line 609,
and `developer|tick:batch_start|bg_2` was quarantined at 3. Each
Terminologist respecify of c3_no_terminal_true moved a criteria row of bg_2.
The batch-wide lift deleted the key, and three more Developers met the same
note. The loop ran five rounds (s226 to s265).
"""
from __future__ import annotations

import pytest

from rota.core.db import SessionResult, Write, init_db, session_commit

START = "developer|tick:batch_start|bg_2"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i2','confirm on a terminal','in_scope',"
                 "'approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk2','i2','confirm reads the terminal')")
    for cid in ("c3_no_terminal_true", "c3_terminal_failure_true"):
        conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                     "(?, 'tk2', 'confirm returns True')", (cid,))
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES "
                 "('bg_2','i2','running')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_2','tk2')")
    conn.commit()
    return conn


def _quarantine(conn, key: str) -> None:
    conn.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
                 "reported) VALUES (?, 3, 1, 1)", (key,))
    conn.commit()


def _key(conn, key: str):
    row = conn.execute("SELECT attempts, quarantined FROM tick_attempts "
                       "WHERE tick_key = ?", (key,)).fetchone()
    return (row["attempts"], row["quarantined"]) if row else None


def _respecify(conn, cid: str = "c3_no_terminal_true", text: str = "v2") -> None:
    """s226's shape: a Terminologist relay session moves a bg_2 criterion."""
    seq = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    session_commit(conn, SessionResult(
        session_id=f"s{seq}", role="terminologist",
        writes=[Write("criteria", cid, {"text": text}, op="update")]))


def test_a_respecify_keeps_the_developers_start_key_quarantined(db):
    """The note refusal came from the code tree. A criteria move cannot
    change it, so the key stays at 3 attempts quarantined."""
    _quarantine(db, START)
    _respecify(db)
    assert _key(db, START) == (3, 1)
    _respecify(db, "c3_terminal_failure_true")
    assert _key(db, START) == (3, 1), "the second round stays too"


def test_a_respecify_keeps_the_developers_verdict_failed_key(db):
    key = "developer|tick:verdict_failed|bg_2"
    _quarantine(db, key)
    _respecify(db)
    assert _key(db, key) == (3, 1)


def test_a_respecify_still_lifts_the_seats_that_read_the_criteria(db):
    """The Critic's verdict, the Tester's encode and the Developer's red
    read the criteria or their tests, so a criteria move lifts them as
    before. A Terminologist key that names the criterion lifts too."""
    lifted = ("critic|tick:review|bg_2", "tester|tick:tests_missing|bg_2",
              "developer|tick:tests_failing|bg_2",
              "terminologist|tick:criterion_repair|c3_no_terminal_true")
    for key in lifted:
        _quarantine(db, key)
    _respecify(db)
    assert {k: _key(db, k) for k in lifted} == dict.fromkeys(lifted)

