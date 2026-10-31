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


# Pass 2: a down model stops the run with its name, and a bad wake still
# counts (review 1 of frame 355, findings 1 to 5).

def _seed_message(db):
    _seed_entry(db)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m1','t1','liaison','vision_keeper','deliver',1)")
    db.commit()


def _answered_session(db, sid="s_ok"):
    """A session of another wake that had an answer from the model."""
    seq = db.execute("SELECT COALESCE(MAX(seq), 0) + 1 FROM sessions").fetchone()[0]
    db.execute("INSERT INTO sessions (id, role, committed, seq, wake_kind) "
               "VALUES (?, 'architect', 1, ?, 'tick:survey')", (sid, seq))
    db.commit()


def _m1(db):
    return dict(db.execute("SELECT status, attempts FROM messages WHERE id = 'm1'"
                           ).fetchone())


def test_a_wake_that_fails_while_another_session_answers_reaches_quarantine(
        tmp_path, monkeypatch):
    """A prompt too large for the window fails the same way every time,
    and other sessions answer. Such a wake spends its attempts."""
    monkeypatch.setattr(time, "sleep", lambda s: None)
    db = init_db(tmp_path / "rota.db")
    _seed_message(db)

    first = loop.step(db, backend=Stalled(), pins=Pins(model="scripted"))
    assert first.outcome.unavailable, "the first end has no answer to compare"
    assert _m1(db) == {"status": "open", "attempts": 0}

    _answered_session(db)
    for n in (1, 2, 3):
        s = loop.step(db, backend=Stalled(), pins=Pins(model="scripted"))
        assert s.wake.message_id == "m1", str(s)
        assert not s.outcome.unavailable, f"end {n} is the wake's own"
    assert _m1(db) == {"status": "quarantined", "attempts": 3}, _m1(db)


def test_a_wake_that_fails_while_no_session_answers_gives_its_attempt_back(
        tmp_path, monkeypatch):
    """An answer before the wake's first end does not make the end its own."""
    monkeypatch.setattr(time, "sleep", lambda s: None)
    db = init_db(tmp_path / "rota.db")
    _seed_message(db)
    _answered_session(db)

    for _ in range(2):
        s = loop.step(db, backend=Stalled(), pins=Pins(model="scripted"))
        assert s.outcome.unavailable, s.outcome.errors
    assert _m1(db) == {"status": "open", "attempts": 0}, _m1(db)


def test_three_ends_with_no_answer_stop_the_run_with_the_model_name(
        tmp_path, monkeypatch):
    waits = []
    monkeypatch.setattr(time, "sleep", waits.append)
    db = init_db(tmp_path / "rota.db")
    _seed_message(db)

    trace = loop.run(db, backend=Stalled(), pins=Pins(model="stalled-8b"),
                     principal_present=False, max_steps=10)
    assert len(trace.steps) == 3, trace.render()
    model = db.execute("SELECT model FROM sessions ORDER BY seq DESC LIMIT 1"
                       ).fetchone()["model"]
    assert model and f"the model {model} does not answer" in trace.down, trace.down
    assert "60s apart" in trace.down, trace.down
    assert db_mod.get_config(db, loop.MODEL_DOWN) == trace.down
    assert principal.render_state(db).startswith(trace.down), "agenda says the stop"

    answered = loop.Step(outcome=RunOutcome(session_id="s9", committed=True,
                                            iterations=1))
    assert loop.model_stop(db, 3, answered) == (0, "")
    assert db_mod.get_config(db, loop.MODEL_DOWN) is None, "an answer clears it"


def test_a_message_on_two_rows_closes_only_when_both_moved(tmp_path):
    db = init_db(tmp_path / "rota.db")
    _quarantined_pair(db)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq, "
               "body_refs, attempts, status) VALUES ('m6','t1','principal','liaison',"
               "'verdict',4,'[\"s1\", \"s2\"]',3,'quarantined')")
    db.execute("INSERT INTO rulings (id, ask_id, per_item, status, verdict_id) "
               "VALUES ('r_m6','m2','{\"s1\": \"approve\"}','landed','m6')")

    def move(ref):
        db_mod._lift_quarantines(db, db_mod.Write(
            table="statements", row_id=ref, values={"status": "ratified"}),
            moved=True)
        return db.execute("SELECT status FROM messages WHERE id = 'm6'"
                          ).fetchone()["status"]

    assert move("s2") == "quarantined", "s1 has not moved"
    assert move("s2") == "quarantined", "a second move of s2 is still one row"
    assert move("s1") == "answered"


def test_an_old_database_opened_with_connect_alone_reads_told(tmp_path):
    import shutil

    import pytest

    from rota import paths

    src = paths.REPO / ".rota" / "dry1.db"
    if not src.exists():
        pytest.skip("dry1.db is a local run file")
    shutil.copy(src, tmp_path / "dry1.db")
    db = db_mod.connect(tmp_path / "dry1.db")
    row = db.execute("SELECT told, moved_refs FROM messages WHERE id = 'm4'").fetchone()
    assert (row["told"], row["moved_refs"]) == (0, "[]"), dict(row)
    assert predicates.quarantined(db), "m4 and m5 are untold"
    db.close()


def test_a_report_marks_told_only_the_messages_its_wake_counted(
        tmp_path, monkeypatch):
    """m5 is quarantined after the wake was built, so the report did not
    say it."""
    db = init_db(tmp_path / "rota.db")
    _quarantined_pair(db)
    db.execute("UPDATE messages SET status = 'open' WHERE id = 'm5'")
    db.commit()
    wake = predicates.quarantined(db)
    assert wake and wake[0].refs == ("s1",) and wake[0].message_ids == ("m4",), wake

    def report(conn, w, **kw):
        conn.execute("UPDATE messages SET status = 'quarantined' WHERE id = 'm5'")
        return RunOutcome(session_id="s9", committed=True, iterations=1)

    monkeypatch.setattr(loop, "frontier", lambda conn, **kw: list(wake))
    monkeypatch.setattr(loop, "run_session", report)
    s = loop.step(db, backend=Stalled(), pins=Pins(model="scripted"))
    assert s.outcome.committed, str(s)

    told = {r["id"]: r["told"] for r in db.execute(
        "SELECT id, told FROM messages WHERE id IN ('m4','m5')")}
    assert told == {"m4": 1, "m5": 0}, told
    again = predicates.quarantined(db)
    assert again and again[0].message_ids == ("m5",), again


def test_a_direct_session_gives_back_no_count_it_did_not_make(
        tmp_path, monkeypatch):
    """No `note_dispatch` ran, so the key's count is an earlier dispatch's."""
    from rota.core.runner import run_session

    db = init_db(tmp_path / "rota.db")
    _seed_entry(db)
    tick = Wake("liaison", "tick:quarantined", refs=("s1",), detail="1 abandoned")
    db.execute("INSERT INTO tick_attempts (tick_key, attempts) VALUES (?, 2)",
               (tick_key(tick),))
    db.commit()

    out = run_session(db, tick, backend=Stalled(), pins=Pins(model="scripted"))
    assert out.unavailable, out.errors
    assert db.execute("SELECT attempts FROM tick_attempts WHERE tick_key = ?",
                      (tick_key(tick),)).fetchone()["attempts"] == 2
