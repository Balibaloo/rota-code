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
from rota.core import runner as runner_mod
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


def test_a_replay_miss_still_spends_its_attempt(tmp_path, monkeypatch):
    """A cassette miss repeats on every retry, so it is not an outage.
    No probe runs under replay."""
    calls = _probe(monkeypatch, False)

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
    assert calls == [], "a probe ran under replay"
    assert db.execute("SELECT attempts FROM messages WHERE id = 'm1'"
                      ).fetchone()["attempts"] == 1


def test_the_probe_goes_past_a_recorder_with_the_smallest_call(tmp_path):
    """The probe writes no cassette, and it asks the session's model for one
    token at the session's window, in 30 s."""
    from rota.llm.cassettes import RecordingBackend, ReplayOnlyBackend

    class Live:
        name = "live"
        timeout = 300.0

        def __init__(self):
            self.seen = []

        def complete(self, system, user, pins, tools=None):
            self.seen.append((self.timeout, pins))
            from rota.llm.llm import Completion
            return Completion(text="OK", pins=pins, backend=self.name)

    live = Live()
    rec = RecordingBackend(live, dev_conn=None)
    assert runner_mod.probe_model(rec, Pins(model="qwen3:8b", num_ctx=16384))
    (timeout, pins), = [(t, p) for t, p in live.seen]
    assert timeout == runner_mod.PROBE_TIMEOUT_S == 30.0
    # The session's own window, so the server keeps the model loaded.
    assert (pins.model, pins.max_tokens, pins.num_ctx) == ("qwen3:8b", 1, 16384)
    assert live.timeout == 300.0, "the session's backend keeps its timeout"
    assert not runner_mod.probe_model(Stalled(), Pins(model="qwen3:8b"))
    assert runner_mod.probe_model(ReplayOnlyBackend(None), Pins())


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


def _m1(db):
    return dict(db.execute("SELECT status, attempts FROM messages WHERE id = 'm1'"
                           ).fetchone())


def _probe(monkeypatch, answers):
    """The probe call, mocked. Return the list of the probe's pins."""
    calls = []

    def probe(backend, pins):
        calls.append(pins)
        if isinstance(answers, tuple):
            return answers
        return ((runner_mod.PROBE_UP, "") if answers
                else (runner_mod.PROBE_SILENT, "no answer in 30s"))

    monkeypatch.setattr(runner_mod, "probe_result", probe)
    return calls


class NoSuchModel:
    """A live Ollama that has no model of the name, as `OllamaBackend`
    raises it."""
    name = "no-model"
    timeout = 300.0

    def complete(self, system, user, pins, tools=None):
        import io
        import urllib.error

        try:
            raise urllib.error.HTTPError("http://test/api/chat", 404,
                                         "Not Found", {}, io.BytesIO(b""))
        except urllib.error.URLError as exc:
            raise LLMUnavailable(f"ollama at test: {exc}") from exc


def test_a_wrong_model_name_on_a_live_server_is_the_wakes_own_end(
        tmp_path, monkeypatch):
    """Review p3, finding 1: the probe read a 404 as a down server, and the
    stop line said to start the server that was up."""
    monkeypatch.setattr(time, "sleep", lambda s: None)
    db = init_db(tmp_path / "rota.db")
    _seed_message(db)

    s = loop.step(db, backend=NoSuchModel(), pins=Pins(model="qwen9:1b"))
    assert s.outcome.probe == runner_mod.PROBE_NO_MODEL, s.outcome.errors
    assert not s.outcome.unavailable and _m1(db)["attempts"] == 1, _m1(db)
    assert "no model qwen9:1b" in s.outcome.errors[-1], s.outcome.errors
    refused = loop.Step(wake=s.wake, outcome=RunOutcome(
        session_id=s.outcome.session_id, committed=False, iterations=0,
        unavailable=True, probe=runner_mod.PROBE_REFUSED,
        probe_error="HTTP Error 500: out of memory"))
    _, line = loop.model_stop(db, 2, refused)
    assert "out of memory" in line and "Start the model server" not in line
    silent = loop.Step(wake=s.wake, outcome=RunOutcome(
        session_id=s.outcome.session_id, committed=False, iterations=0,
        unavailable=True, probe=runner_mod.PROBE_SILENT))
    assert "Start the model server" in loop.model_stop(db, 2, silent)[1]


def test_a_probe_that_answers_clears_an_old_stop(tmp_path):
    """Review p3, finding 3: an end whose probe answered kept the stop."""
    db = init_db(tmp_path / "rota.db")
    db_mod.set_config(db, loop.MODEL_DOWN, "Stopped at then: old")
    own = loop.Step(outcome=RunOutcome(session_id="s8", committed=False,
                                       iterations=0,
                                       probe=runner_mod.PROBE_UP))
    assert loop.model_stop(db, 2, own) == (0, "")
    assert db_mod.get_config(db, loop.MODEL_DOWN) is None


def test_rota_run_exits_2_after_a_model_down_stop(tmp_path, monkeypatch):
    """Review p3, finding 4: a night launcher read the stop as a quiet run."""
    import argparse

    from rota import cli
    from rota.llm import profile as profile_mod
    from rota.tools import onboard_run

    path = tmp_path / "rota.db"
    init_db(path).close()
    monkeypatch.setattr(cli, "require", lambda name: path)
    monkeypatch.setattr(profile_mod, "of_run", lambda conn: type(
        "P", (), {"default_model": "qwen3:8b"})())
    args = argparse.Namespace(name="x", until=None, role=[], model=None,
                              limit=1, all=False)
    monkeypatch.setattr(onboard_run, "drive", lambda *a, **k: "Stopped at now")
    assert cli.cmd_run(args) == cli.MODEL_DOWN_EXIT == 2
    monkeypatch.setattr(onboard_run, "drive", lambda *a, **k: None)
    assert cli.cmd_run(args) == 0


def test_a_no_answer_end_whose_probe_answers_spends_the_attempt(
        tmp_path, monkeypatch):
    """A prompt too large for the window fails the same way every time,
    and the model answers a probe. Such a wake reaches quarantine."""
    monkeypatch.setattr(time, "sleep", lambda s: None)
    calls = _probe(monkeypatch, True)
    db = init_db(tmp_path / "rota.db")
    _seed_message(db)

    for n in (1, 2, 3):
        s = loop.step(db, backend=Stalled(), pins=Pins(model="scripted"))
        assert s.wake.message_id == "m1", str(s)
        assert not s.outcome.unavailable, f"end {n} is the wake's own"
        assert runner_mod.PROBE_ANSWERED in s.outcome.errors[-1], s.outcome.errors
    assert len(calls) == 3 and calls[0].model == "scripted", calls
    assert _m1(db) == {"status": "quarantined", "attempts": 3}, _m1(db)
    text = db.execute("SELECT completion FROM turns WHERE completion LIKE "
                      "'SESSION FAILED:%' ORDER BY rowid DESC LIMIT 1"
                      ).fetchone()["completion"]
    assert runner_mod.PROBE_ANSWERED in text, text


def test_a_no_answer_end_whose_probe_fails_gives_its_attempt_back(
        tmp_path, monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
    _probe(monkeypatch, False)
    db = init_db(tmp_path / "rota.db")
    _seed_message(db)

    for _ in range(2):
        s = loop.step(db, backend=Stalled(), pins=Pins(model="scripted"))
        assert s.outcome.unavailable, s.outcome.errors
        assert runner_mod.PROBE_ANSWERED not in s.outcome.errors[-1]
    assert _m1(db) == {"status": "open", "attempts": 0}, _m1(db)


class AnswersThenStalls:
    """A model that answers turns 1 and 2, then stalls on turn 3."""
    name = "stalls-late"

    def __init__(self):
        self.n = 0

    def complete(self, system, user, pins, tools=None):
        from rota.llm.llm import Completion

        self.n += 1
        if self.n >= 3:
            raise LLMUnavailable("ollama at test: no answer in 300s")
        # A refused call keeps the session in its loop for another turn.
        return Completion(text="TOOL: no.such_call()", pins=pins,
                          backend=self.name)


def test_a_session_that_answered_then_stalled_spends_the_attempt(
        tmp_path, monkeypatch):
    """Review 2, finding 1: the turn the session kept gave its attempt back
    on every retry. The probe answers, so the end is the wake's own."""
    monkeypatch.setattr(time, "sleep", lambda s: None)
    calls = _probe(monkeypatch, True)
    db = init_db(tmp_path / "rota.db")
    _seed_message(db)

    backend = AnswersThenStalls()
    s = loop.step(db, backend=backend, pins=Pins(model="scripted"))
    assert backend.n == 3, f"the session stalled on turn {backend.n}"
    assert not s.outcome.unavailable and len(calls) == 1, s.outcome.errors
    kept = db.execute("SELECT COUNT(*) FROM turns WHERE session_id = ? "
                      "AND system != ''", (s.outcome.session_id,)).fetchone()[0]
    assert kept >= 1, "the session kept its model turns"
    assert _m1(db)["attempts"] == 1, _m1(db)


def test_three_failed_probes_stop_the_run_with_the_model_name(
        tmp_path, monkeypatch):
    waits = []
    monkeypatch.setattr(time, "sleep", waits.append)
    calls = _probe(monkeypatch, False)
    db = init_db(tmp_path / "rota.db")
    _seed_message(db)

    trace = loop.run(db, backend=Stalled(), pins=Pins(model="stalled-8b"),
                     principal_present=False, max_steps=10)
    assert len(trace.steps) == 3 and len(calls) == 3, trace.render()
    model = db.execute("SELECT model FROM sessions ORDER BY seq DESC LIMIT 1"
                       ).fetchone()["model"]
    assert model and f"the model {model} does not answer" in trace.down, trace.down
    assert trace.down.startswith("Stopped at "), trace.down
    assert "60s apart" in trace.down, trace.down
    assert db_mod.get_config(db, loop.MODEL_DOWN) == trace.down
    assert principal.render_state(db).startswith(trace.down), "agenda says the stop"

    answered = loop.Step(outcome=RunOutcome(session_id="s9", committed=True,
                                            iterations=1))
    assert loop.model_stop(db, 3, answered) == (0, "")
    assert db_mod.get_config(db, loop.MODEL_DOWN) is None, "an answer clears it"


def test_a_session_that_keeps_a_model_turn_clears_the_stop(tmp_path):
    """Review 2, finding 6: a session that answers and fails on its own
    shows the model is back."""
    db = init_db(tmp_path / "rota.db")
    db_mod.set_config(db, loop.MODEL_DOWN, "Stopped at then: old")
    db.execute("INSERT INTO sessions (id, role, committed, seq) "
               "VALUES ('s7', 'liaison', 0, 1)")
    db.execute("INSERT INTO turns (session_id, seq, system, user, completion) "
               "VALUES ('s7', 0, 'the brief', 'the wake', 'a reply')")
    failed = loop.Step(outcome=RunOutcome(session_id="s7", committed=False,
                                          iterations=1))
    assert loop.model_stop(db, 2, failed) == (0, "")
    assert db_mod.get_config(db, loop.MODEL_DOWN) is None


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


def test_a_move_before_the_quarantine_counts_from_the_landing_on(tmp_path):
    """Review 2, finding 4: m97's s1 moved while m97 was unresolved, and
    the move was lost."""
    db = init_db(tmp_path / "rota.db")
    _quarantined_pair(db)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq, "
               "body_refs, attempts, status) VALUES ('m97','t1','principal','liaison',"
               "'verdict',5,'[\"s1\", \"s2\"]',1,'unresolved')")
    db.execute("INSERT INTO rulings (id, ask_id, per_item, status, verdict_id) "
               "VALUES ('r_m97','m2','{\"s1\": \"approve\"}','landed','m97')")

    def move(ref):
        db_mod._lift_quarantines(db, db_mod.Write(
            table="statements", row_id=ref, values={"status": "ratified"}),
            moved=True)
        return dict(db.execute("SELECT status, moved_refs FROM messages "
                               "WHERE id = 'm97'").fetchone())

    assert move("s1") == {"status": "unresolved", "moved_refs": '["s1"]'}
    db.execute("UPDATE messages SET status = 'quarantined' WHERE id = 'm97'")
    assert move("s2")["status"] == "answered"


def _dry1(tmp_path):
    import shutil

    import pytest

    from rota import paths

    src = paths.REPO / ".rota" / "dry1.db"
    if not src.exists():
        pytest.skip("dry1.db is a local run file")
    shutil.copy(src, tmp_path / "dry1.db")
    return tmp_path / "dry1.db"


def test_a_read_only_open_of_an_old_database_reads_the_quarantined(tmp_path):
    """Review 2, finding 5: `rota ls` and the cockpit's overlay open with
    `connect_readonly`, which adds no `told` column."""
    path = _dry1(tmp_path)
    db = db_mod.connect_readonly(path)
    assert not db_mod._has_column(db, "messages", "told"), "dry1 is old"
    assert predicates.quarantined(db), "m4 and m5 are quarantined"
    db.close()


def test_the_agenda_says_the_stop_first_with_five_questions_waiting(
        tmp_path, capsys):
    """Review 2, finding 3: the agenda printed the five asks of dry1 and no
    stop line."""
    import argparse

    from rota import cli

    path = _dry1(tmp_path)
    db = db_mod.connect(path)
    line = "Stopped at 2026-10-31 20:00: the model qwen3:8b does not answer."
    db_mod.set_config(db, loop.MODEL_DOWN, line)
    db.commit()
    asks = len(principal.pending_asks(db))
    db.close()
    assert asks == 5, asks

    cli.cmd_agenda(argparse.Namespace(name=str(path), limit=3))
    out = capsys.readouterr().out.splitlines()
    assert out[0] == line, out[:3]
    assert out.count(line) == 1, "the stop prints once"
    assert sum(1 for x in out if x.startswith("[")) == 5, out
