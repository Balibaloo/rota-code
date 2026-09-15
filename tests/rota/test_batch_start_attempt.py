"""A re-fired batch_start carries its attempt count (finding 76)."""
from rota.core.db import init_db
from rota.core.scheduler import tick_batch_start


def test_a_refired_batch_start_says_which_attempt_it_is(tmp_path):
    """Night 73 (2026-09-15): three identical Developer sessions at batch_start,
    no write, quarantined. At temperature zero the same wake is the same
    session; the attempt count is a fact of tick_attempts and the wake
    carries it, as tests_failing does."""
    conn = init_db(tmp_path / "r.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, version) VALUES ('i1','x','in_scope','decided','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','running')")
    conn.execute("INSERT INTO sessions (id, role, wake_kind, wake_refs, committed, seq, mode, model) VALUES ('s1','developer','tick:batch_start','[\"b1\"]',1,1,'normal','m')")
    conn.execute("INSERT INTO tick_attempts (tick_key, attempts) VALUES ('developer|tick:batch_start|b1', 1)")
    conn.commit()
    wakes = tick_batch_start(conn)
    assert wakes and wakes[0].refs == ("b1",)
    assert wakes[0].detail.startswith("attempt 2 of 3"), wakes[0].detail
