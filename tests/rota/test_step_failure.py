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


def test_a_failed_session_leaves_a_row_with_its_error(tmp_path):
    """Night 31: 69 deaths and nothing in the database to read. A failed
    session is `committed = 0`, and its error is its last turn."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, text, ts_order) "
               "VALUES ('u1','principal','let users delete their account',1)")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m1','t1','liaison','vision_keeper','deliver',1)")
    db.commit()

    s = loop.step(db, backend=Exploding(), pins=Pins(model="scripted"))
    assert s.outcome is not None and not s.outcome.committed

    row = db.execute("SELECT id, role, committed, wake_kind FROM sessions").fetchone()
    assert row is not None, "the failed session left no row"
    assert (row["committed"], row["role"]) == (0, "vision_keeper")
    last = db.execute("SELECT completion FROM turns WHERE session_id = ? "
                      "ORDER BY seq DESC LIMIT 1", (row["id"],)).fetchone()
    assert last["completion"].startswith("SESSION FAILED: RuntimeError('boom')")


def test_no_wake_is_dispatched_past_the_cap_when_every_session_fails(tmp_path):
    """The bound holds for ticks as well as messages: a run whose model
    always fails ends, it does not spin."""
    from collections import Counter
    from rota.core import config

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, text, ts_order) "
               "VALUES ('u1','principal','let users delete their account',1)")
    db.commit()
    cap = config.get(db, "tick_attempt_cap")

    seen = Counter()
    for _ in range(40):
        s = loop.step(db, backend=Exploding(), pins=Pins(model="scripted"))
        if s.wake is None:
            break
        seen[str(s.wake)] += 1
    worst = max(seen.values()) if seen else 0
    assert worst <= cap + 1, f"a wake was dispatched {worst} times: {seen.most_common(3)}"
