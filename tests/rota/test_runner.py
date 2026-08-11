"""
Session runner: (fixture db, one message) -> (writes, messages, receipt).

Scripted backend throughout — these prove the *machine*, not the model.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db, version_of
from rota.llm.llm import Pins, ScriptedBackend
from rota.core.runner import run_session
from rota.core.scheduler import Wake


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('u1','principal','let users delete their account',1)")
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                 "VALUES ('m1','t1','liaison','gatekeeper','deliver',1)")
    return conn


def wake_gatekeeper():
    return Wake(role="gatekeeper", kind="message", message_id="m1", detail="deliver")


def test_session_writes_commit_atomically_with_receipts(db):
    backend = ScriptedBackend([
        "I will record the scope item.\n"
        "TOOL: problem.assert(id='i1', text='users can delete their account', kind='in_scope')",
        "Done.",
    ])
    outcome = run_session(db, wake_gatekeeper(), backend=backend, pins=Pins(model="scripted"))

    assert outcome.committed, outcome.errors
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 1
    assert version_of(db, "items") == 1
    receipts = db.execute("SELECT table_name, row_id FROM receipts").fetchall()
    assert [(r["table_name"], r["row_id"]) for r in receipts] == [("items", "i1")]


def test_trigger_message_is_answered_on_commit(db):
    backend = ScriptedBackend(["nothing to do"])
    run_session(db, wake_gatekeeper(), backend=backend, pins=Pins(model="scripted"))
    status = db.execute("SELECT status FROM messages WHERE id='m1'").fetchone()["status"]
    assert status == "answered"


def test_out_of_working_set_call_is_an_error_not_a_write(db):
    """Gatekeeper reaching for the system model gets told no and the session survives."""
    backend = ScriptedBackend([
        "TOOL: model.amend(id='c1', headline='no')",
        "Understood.",
    ])
    outcome = run_session(db, wake_gatekeeper(), backend=backend, pins=Pins(model="scripted"))

    assert outcome.committed
    assert any("working set" in e for e in outcome.errors)
    assert db.execute("SELECT COUNT(*) n FROM constraints").fetchone()["n"] == 0


def test_malformed_call_is_reported_back_not_misparsed(db):
    backend = ScriptedBackend([
        "TOOL: problem.assert(id='i1', text=",
        "Sorry. TOOL: problem.assert(id='i1', text='ok', kind='in_scope')",
        "Done.",
    ])
    outcome = run_session(db, wake_gatekeeper(), backend=backend, pins=Pins(model="scripted"))

    assert outcome.committed
    assert any("parse" in e or "unterminated" in e for e in outcome.errors)
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 1


def test_messages_route_only_to_derived_contacts(db):
    backend = ScriptedBackend([
        "TOOL: msg.report_liaison(refs=['u1'])",
        "Done.",
    ])
    outcome = run_session(db, wake_gatekeeper(), backend=backend, pins=Pins(model="scripted"))
    assert outcome.committed, outcome.errors

    rows = db.execute("SELECT from_role, to_role, verb, body_refs, cause_id FROM messages "
                      "WHERE from_role='gatekeeper'").fetchall()
    assert len(rows) == 1
    assert rows[0]["to_role"] == "liaison" and rows[0]["verb"] == "report"
    assert json.loads(rows[0]["body_refs"]) == ["u1"]
    assert rows[0]["cause_id"] == "m1", "message did not ref its cause"


def test_role_cannot_address_the_principal(db):
    """Only Liaison sees the principal. Gatekeeper has no such function to call."""
    backend = ScriptedBackend([
        "TOOL: msg.converse_principal(refs=[])",
        "Done.",
    ])
    outcome = run_session(db, wake_gatekeeper(), backend=backend, pins=Pins(model="scripted"))
    assert any("working set" in e for e in outcome.errors)
    assert db.execute(
        "SELECT COUNT(*) n FROM messages WHERE to_role='principal'").fetchone()["n"] == 0


def test_failed_session_never_happened_and_raises_attempts(db):
    """A session that dies mid-flight commits nothing and leaves its trigger open."""
    class Exploding:
        name = "exploding"

        def complete(self, system, user, pins):
            raise RuntimeError("model evicted")

    outcome = run_session(db, wake_gatekeeper(), backend=Exploding(), pins=Pins(model="x"))

    assert not outcome.committed
    assert db.execute("SELECT COUNT(*) n FROM sessions").fetchone()["n"] == 0
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 0
    row = db.execute("SELECT status, attempts FROM messages WHERE id='m1'").fetchone()
    assert row["status"] == "open", "trigger left the frontier despite failing"
    assert row["attempts"] == 1
    assert db.execute("SELECT COUNT(*) n FROM claims").fetchone()["n"] == 0, "claim not released"


def test_pins_are_recorded_on_the_session(db):
    backend = ScriptedBackend(["done"])
    outcome = run_session(db, wake_gatekeeper(), backend=backend,
                          pins=Pins(model="qwen3.5:9b", temperature=0.0, num_ctx=8192))
    row = db.execute("SELECT model, temperature, num_ctx, prompt_hash FROM sessions").fetchone()
    assert row["model"] == "qwen3.5:9b"
    assert row["num_ctx"] == 8192
    assert row["prompt_hash"], "a result without its pins is not a result"


def test_tool_calls_are_logged_for_assertion(db):
    backend = ScriptedBackend([
        "TOOL: problem.consult()",
        "Nothing there yet.",
    ])
    outcome = run_session(db, wake_gatekeeper(), backend=backend, pins=Pins(model="scripted"))
    calls = db.execute("SELECT fn FROM tool_calls WHERE session_id=? ORDER BY seq",
                       (outcome.session_id,)).fetchall()
    assert "problem.consult" in [c["fn"] for c in calls]


def test_readonly_mode_cannot_write(db):
    backend = ScriptedBackend([
        "TOOL: problem.assert(id='i9', text='x', kind='in_scope')",
        "ok",
    ])
    outcome = run_session(db, wake_gatekeeper(), backend=backend, mode="readonly",
                          pins=Pins(model="scripted"))
    assert any("working set" in e for e in outcome.errors)
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 0
    assert version_of(db, "items") == 0


def test_a_result_under_the_cap_arrives_whole(db):
    """No notice, no loss — the commonest case must be the boring one."""
    from rota.core.runner import RESULT_CHARS, _render

    text = _render({"path": "signature.py", "body": "x" * 100})
    assert "TRUNCATED" not in text
    assert "x" * 100 in text
    assert len(text) <= RESULT_CHARS


def test_a_cut_result_says_it_was_cut_and_by_how_much(db):
    """
    A silent cut is indistinguishable from a short answer. The model has no
    reason to ask for the rest of something it does not know was withheld —
    which is how an Architect came to survey a file it had read four hundred
    lines of and seen twenty of.
    """
    from rota.core.runner import RESULT_CHARS, _render

    full = "y" * (RESULT_CHARS * 2)
    text = _render({"body": full})

    assert "TRUNCATED" in text, "the cut is invisible to the model"
    assert str(RESULT_CHARS) in text and str(len(json.dumps({"body": full}))) in text, \
        "the notice must say how much was withheld, not merely that some was"
    assert "Ask for the next range" in text, "no way offered to get the rest"


def test_a_long_read_reaches_the_model_past_the_old_cap(db):
    """
    The regression this pins: results were cut to 1200 characters before the
    model saw them, so `code.source(start=0, end=400)` did its job and delivered
    a docstring. Nothing in the suite noticed, because every fixture's tool
    results were short.
    """
    for i in range(20):
        db.execute("INSERT INTO items (id, text, kind, provenance) VALUES (?,?,?,?)",
                   (f"i{i:02d}", f"scope item {i:02d} " + "detail " * 8,
                    "in_scope", "decided"))
    db.execute("UPDATE items SET text = text || ' CANARY_PAST_THE_OLD_CAP' "
               "WHERE id='i19'")

    backend = ScriptedBackend(["TOOL: problem.consult()", "Seen."])
    outcome = run_session(db, wake_gatekeeper(), backend=backend, pins=Pins(model="scripted"))
    assert outcome.committed, outcome.errors

    _, user = backend.calls[1]
    served = user[user.rindex("OK problem.consult ->"):]
    assert len(served) > 1200, "the old cap is still in force"
    assert "CANARY_PAST_THE_OLD_CAP" in served, \
        "the tail of the result never reached the model"


def test_working_set_is_pushed_not_only_offered(db):
    """A cold session should not have to fetch what it obviously needs."""
    db.execute("INSERT INTO items (id, text, kind, provenance) "
               "VALUES ('i_existing','prior scope','in_scope','decided')")
    backend = ScriptedBackend(["done"])
    run_session(db, wake_gatekeeper(), backend=backend, pins=Pins(model="scripted"))

    system, user = backend.calls[0]
    assert "i_existing" in user, "existing items were not pushed into the prompt"
    assert "problem.assert" in system, "working set functions not advertised"


# ---------------------------------------------------------------------------
# What the model tiers cost
# ---------------------------------------------------------------------------

def test_a_replay_and_a_recording_are_counted_separately(tmp_path, monkeypatch):
    """
    "How long do the cassettes take" had no answer: neither cassette table
    carries a duration, so the number that decides whether a prompt edit is
    affordable was repeated from memory. It was being quoted as 27 minutes, from
    a file that had also drifted 129 tests.

    Counted apart because they are different currencies. A replay costs
    microseconds and can be spent freely; a recording costs GPU seconds and is
    what a prompt edit actually bills you.
    """
    from rota.llm.cassettes import (RecordingBackend, ReplayOnlyBackend, Tally,
                                    open_dev_db)
    from rota.llm.llm import Completion

    class Slow:
        name = "slow"

        def complete(self, system, user, pins, tools=None):
            return Completion(text="hello", pins=pins, backend="slow")

    tally = Tally()
    monkeypatch.setattr("rota.llm.cassettes.TALLY", tally)
    conn = open_dev_db(tmp_path / "dev.db")
    pins = Pins(model="scripted", temperature=0.0)

    RecordingBackend(Slow(), conn).complete("sys", "usr", pins)
    assert (tally.records, tally.replays) == (1, 0), "a live call read as a replay"

    ReplayOnlyBackend(conn).complete("sys", "usr", pins)
    assert (tally.records, tally.replays) == (1, 1), "a cassette hit was not counted"
    assert tally.record_seconds >= 0 and tally.replay_seconds >= 0

    assert "1 recorded" in tally.line() and "1 replayed" in tally.line()


def test_timings_persist_per_machine_and_never_reach_the_cassettes(tmp_path,
                                                                   monkeypatch):
    """
    A duration is a fact about this GPU on this day at this thermal state.
    Filing it beside the recordings would make it look like evidence about the
    prompts, so it goes to a gitignored file instead — and the series is the
    point, because one number says how long this takes and a series says whether
    it is getting slower.
    """
    from rota.llm.cassettes import Tally, open_dev_db

    monkeypatch.setattr("rota.paths.TIMINGS_FILE", tmp_path / ".rota-timings.json")

    Tally(records=10, record_seconds=90.0).save(model="llama3.1:8b")
    Tally(records=10, record_seconds=140.0).save(model="llama3.1:8b")

    last = Tally.previous()
    assert last["record_seconds"] == 140.0, "the newest run is not the one returned"
    assert last["model"] == "llama3.1:8b"

    conn = open_dev_db(tmp_path / "dev.db")
    tables = {r["name"] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    assert not any("timing" in t for t in tables), \
        "timings leaked into the committed cassette database"


def test_a_run_that_touched_no_model_writes_no_timing(tmp_path, monkeypatch):
    """Otherwise every deterministic run appends a row of zeroes and the series
    stops being readable."""
    from rota.llm.cassettes import Tally

    path = tmp_path / ".rota-timings.json"
    monkeypatch.setattr("rota.paths.TIMINGS_FILE", path)
    Tally().save(model="llama3.1:8b")
    assert not path.exists()
