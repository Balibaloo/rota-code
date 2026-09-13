"""A session that fails spends its attempt inside the run, not only at boot."""
from rota.core import loop
from rota.core.db import init_db
from rota.llm.llm import Pins


class Exploding:
    name = "exploding"

    def complete(self, system, user, pins, tools=None):
        raise RuntimeError("boom")


def test_a_message_whose_session_fails_every_time_is_quarantined_at_the_cap(tmp_path):
    """clickI night 31 (2026-09-13): one message, one error, 69 dispatches
    in 98 minutes. The message attempt cap ran at boot only."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, text, ts_order) "
               "VALUES ('u1','principal','let users delete their account',1)")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m1','t1','liaison','vision_keeper','deliver',1)")
    db.commit()

    seen = []
    for _ in range(5):
        s = loop.step(db, backend=Exploding(), pins=Pins(model="scripted"))
        seen.append(str(s.wake) if s.wake else None)

    row = db.execute("SELECT status, attempts FROM messages WHERE id = 'm1'").fetchone()
    assert row["status"] == "quarantined", (dict(row), seen)
    assert "m1" not in (seen[-1] or ""), f"the quarantined message was dispatched again: {seen}"
