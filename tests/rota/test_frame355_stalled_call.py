"""Frame 355: a stalled model call is not an attempt, a quarantined message
closes and is said once, and an approved page is not sent again.

Dry1 run 2 (2026-10-31): sessions s38 to s45 ended with no answer from
Ollama in 300 s, and m4 and m5 spent their caps on the instrument. The
lift of the wake's key then re-presented s1 three times, and m17 re-sent
how_it_works after r_m10 approved it.
"""
import time

from rota.core import db as db_mod
from rota.core import loop, predicates
from rota.core.db import init_db
from rota.core.runner import RunOutcome
from rota.core.scheduler import Wake, tick_key
from rota.llm.llm import LLMUnavailable, Pins
from rota.roles import principal


class Stalled:
    """A model server that never answers."""
    name = "stalled"

    def complete(self, system, user, pins, tools=None):
        raise LLMUnavailable("ollama at test: no answer in 300s")


def _seed_entry(db):
    db.execute("INSERT INTO entries (id, author, text, ts_order) "
               "VALUES ('u1','principal','let users delete their account',1)")


def test_a_session_with_no_answer_spends_no_attempt_and_the_wake_is_sent_again(
        tmp_path, monkeypatch):
    """Three ends with no answer in a row leave the message open at zero
    attempts. The loop waits `model_wait_s` after each end."""
    waits = []
    monkeypatch.setattr(time, "sleep", waits.append)
    db = init_db(tmp_path / "rota.db")
    _seed_entry(db)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m1','t1','liaison','vision_keeper','deliver',1)")
    db.commit()

    seen = []
    for _ in range(4):
        s = loop.step(db, backend=Stalled(), pins=Pins(model="scripted"))
        assert s.outcome is not None and not s.outcome.committed, str(s)
        assert s.outcome.unavailable, s.outcome.errors
        seen.append(s.wake.message_id)

    row = db.execute("SELECT status, attempts FROM messages WHERE id = 'm1'").fetchone()
    assert (row["status"], row["attempts"]) == ("open", 0), dict(row)
    assert seen == ["m1"] * 4, seen
    assert waits == [60] * 4, waits


def test_a_tick_session_with_no_answer_leaves_its_key_count_where_it_was(
        tmp_path, monkeypatch):
    """Dry1's s44 and s45 spent two attempts of `liaison|tick:quarantined|s1`."""
    monkeypatch.setattr(time, "sleep", lambda s: None)
    db = init_db(tmp_path / "rota.db")
    _seed_entry(db)
    db.commit()
    tick = Wake("liaison", "tick:quarantined", refs=("s1",), detail="1 abandoned")
    monkeypatch.setattr(loop, "frontier", lambda conn, **kw: [tick])

    first = loop.step(db, backend=Stalled(), pins=Pins(model="scripted"))
    assert first.wake is not None and first.wake.kind.startswith("tick:"), str(first)
    key = tick_key(first.wake)
    for _ in range(3):
        s = loop.step(db, backend=Stalled(), pins=Pins(model="scripted"))
        assert tick_key(s.wake) == key, f"the wake was not sent again: {s}"
    row = db.execute("SELECT attempts, quarantined FROM tick_attempts "
                     "WHERE tick_key = ?", (key,)).fetchone()
    assert (row["attempts"], row["quarantined"]) == (0, 0), dict(row)


def test_a_replay_miss_still_spends_its_attempt(tmp_path):
    """A cassette miss repeats on every retry, so it is not an outage."""
    class Miss:
        name = "replay"

        def complete(self, system, user, pins, tools=None):
            raise LLMUnavailable("no cassette for scripted", replay_miss=True)

    db = init_db(tmp_path / "rota.db")
    _seed_entry(db)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m1','t1','liaison','vision_keeper','deliver',1)")
    db.commit()
    s = loop.step(db, backend=Miss(), pins=Pins(model="scripted"))
    assert not s.outcome.unavailable
    assert db.execute("SELECT attempts FROM messages WHERE id = 'm1'"
                      ).fetchone()["attempts"] == 1


def _quarantined_pair(db):
    """m4 a verdict on s1 whose ruling landed, m5 a converse with none."""
    _seed_entry(db)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m2','t1','liaison','principal','present',1)")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq, "
               "body_refs, attempts, status) VALUES ('m4','t1','principal','liaison',"
               "'verdict',2,'[\"s1\"]',3,'quarantined')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq, "
               "body_refs, attempts, status) VALUES ('m5','t2','principal','liaison',"
               "'converse',3,'[]',3,'quarantined')")
    db.execute("INSERT INTO rulings (id, ask_id, per_item, status, verdict_id) "
               "VALUES ('r_m4','m2','{\"s1\": \"approve\"}','landed','m4')")


def test_a_quarantined_message_with_a_landed_verdict_closes_when_its_row_moves(tmp_path):
    db = init_db(tmp_path / "rota.db")
    _quarantined_pair(db)

    db_mod._lift_quarantines(db, db_mod.Write(table="statements", row_id="s2",
                                              values={"status": "ratified"}),
                             moved=True)
    assert db.execute("SELECT status FROM messages WHERE id = 'm4'"
                      ).fetchone()["status"] == "quarantined", "s2 is not m4's row"
    db_mod._lift_quarantines(db, db_mod.Write(table="statements", row_id="s1",
                                              values={"status": "ratified"}),
                             moved=False)
    assert db.execute("SELECT status FROM messages WHERE id = 'm4'"
                      ).fetchone()["status"] == "quarantined", "a write that moves nothing"

    db_mod._lift_quarantines(db, db_mod.Write(table="statements", row_id="s1",
                                              values={"status": "ratified"}),
                             moved=True)
    status = {r["id"]: r["status"] for r in db.execute(
        "SELECT id, status FROM messages WHERE id IN ('m4','m5')")}
    assert status == {"m4": "answered", "m5": "quarantined"}, status


def test_a_quarantined_message_is_reported_once(tmp_path, monkeypatch):
    db = init_db(tmp_path / "rota.db")
    _quarantined_pair(db)
    db.commit()
    wake = predicates.quarantined(db)
    assert wake and wake[0].detail.startswith("2 abandoned"), wake

    monkeypatch.setattr(loop, "frontier", lambda conn, **kw: list(wake))
    monkeypatch.setattr(loop, "run_session", lambda conn, w, **kw: RunOutcome(
        session_id="s9", committed=True, iterations=1))
    s = loop.step(db, backend=Stalled(), pins=Pins(model="scripted"))
    assert s.outcome.committed and s.wake.kind == "tick:quarantined", str(s)

    assert predicates.quarantined(db) == [], "the report was said twice"
    told = {r["id"]: r["told"] for r in db.execute(
        "SELECT id, told FROM messages WHERE id IN ('m4','m5')")}
    assert told == {"m4": 1, "m5": 1}, told


def _item(db, item_id, version, approval_ver):
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES (?, 'how rota works here', 'in_scope', 'approved', ?, ?)",
               (item_id, approval_ver, version))


def test_the_account_page_drops_a_row_approved_at_its_version(tmp_path):
    db = init_db(tmp_path / "rota.db")
    _item(db, "how_it_works", 1, 1)
    _item(db, "d_old", 2, 1)
    db.commit()

    assert principal.account_page_refs(db, ["how_it_works"]) == []
    assert principal.account_rows(db, ["how_it_works", "d_old"]) == ["d_old"]
    assert principal.account_page_refs(db, ["d_old"]) == ["d_old"], (
        "an approve at an older version does not answer the row")
