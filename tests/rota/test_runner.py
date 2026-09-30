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
from rota.testkit.fixtures import seed_provenance


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('u1','principal','let users delete their account',1)")
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                 "VALUES ('m1','t1','liaison','vision_keeper','deliver',1)")
    return conn


def wake_vision_keeper():
    return Wake(role="vision_keeper", kind="message", message_id="m1", detail="deliver")


def test_session_writes_commit_atomically_with_receipts(db):
    backend = ScriptedBackend([
        "I will record the scope item.\n"
        "TOOL: problem.assert(id='i1', text='users can delete their account', kind='in_scope')",
        "Done.",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))

    assert outcome.committed, outcome.errors
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 1
    assert version_of(db, "items") == 1
    receipts = db.execute("SELECT table_name, row_id FROM receipts").fetchall()
    assert [(r["table_name"], r["row_id"]) for r in receipts] == [("items", "i1")]


def test_on_completion_fires_once_per_llm_turn(db):
    """The single-step hook: one call per completion, tool call or not."""
    backend = ScriptedBackend([
        "TOOL: problem.assert(id='i1', text='x', kind='in_scope')",
        "Done.",
    ])
    calls = []
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted"),
                          on_completion=lambda: calls.append(None))

    assert outcome.committed, outcome.errors
    assert len(calls) == 2, "one hook call per completion, including the last"


def test_trigger_message_is_answered_on_commit(db):
    backend = ScriptedBackend(["nothing to do"])
    run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))
    status = db.execute("SELECT status FROM messages WHERE id='m1'").fetchone()["status"]
    assert status == "answered"


def test_out_of_working_set_call_is_an_error_not_a_write(db):
    """Vision Keeper reaching for the system model gets told no and the session survives."""
    backend = ScriptedBackend([
        "TOOL: model.amend(id='c1', headline='no')",
        "Understood.",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))

    assert outcome.committed
    assert any("working set" in e for e in outcome.errors)
    assert db.execute("SELECT COUNT(*) n FROM constraints").fetchone()["n"] == 0


def test_malformed_call_is_reported_back_not_misparsed(db):
    backend = ScriptedBackend([
        "TOOL: problem.assert(id='i1', text=",
        "Sorry. TOOL: problem.assert(id='i1', text='ok', kind='in_scope')",
        "Done.",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))

    assert outcome.committed
    assert any("parse" in e or "unterminated" in e for e in outcome.errors)
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 1


def test_messages_route_only_to_derived_contacts(db):
    backend = ScriptedBackend([
        "TOOL: msg.report_liaison(refs=['u1'])",
        "Done.",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))
    assert outcome.committed, outcome.errors

    rows = db.execute("SELECT from_role, to_role, verb, body_refs, cause_id FROM messages "
                      "WHERE from_role='vision_keeper'").fetchall()
    assert len(rows) == 1
    assert rows[0]["to_role"] == "liaison" and rows[0]["verb"] == "report"
    assert json.loads(rows[0]["body_refs"]) == ["u1"]
    assert rows[0]["cause_id"] == "m1", "message did not ref its cause"


def test_role_cannot_address_the_principal(db):
    """Only Liaison sees the principal. Vision Keeper has no such function to call."""
    backend = ScriptedBackend([
        "TOOL: msg.converse_principal(refs=[])",
        "Done.",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))
    assert any("working set" in e for e in outcome.errors)
    assert db.execute(
        "SELECT COUNT(*) n FROM messages WHERE to_role='principal'").fetchone()["n"] == 0


def test_failed_session_commits_nothing_but_leaves_its_row_and_raises_attempts(db):
    """A session that dies mid-flight commits nothing and leaves its trigger
    open. Since night 31 (2026-09-13) it leaves its own row, `committed = 0`,
    with the error as its last turn: 69 deaths on one error had left nothing
    to read."""
    class Exploding:
        name = "exploding"

        def complete(self, system, user, pins):
            raise RuntimeError("model evicted")

    outcome = run_session(db, wake_vision_keeper(), backend=Exploding(), pins=Pins(model="x"))

    assert not outcome.committed
    rows = db.execute("SELECT committed FROM sessions").fetchall()
    assert [r["committed"] for r in rows] == [0]
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 0
    row = db.execute("SELECT status, attempts FROM messages WHERE id='m1'").fetchone()
    assert row["status"] == "open", "trigger left the frontier despite failing"
    assert row["attempts"] == 1
    assert db.execute("SELECT COUNT(*) n FROM claims").fetchone()["n"] == 0, "claim not released"


def test_pins_are_recorded_on_the_session(db):
    backend = ScriptedBackend(["done"])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="qwen3.5:9b", temperature=0.0, num_ctx=8192))
    row = db.execute("SELECT model, temperature, num_ctx, prompt_hash, pins_json, backend "
                     "FROM sessions").fetchone()
    assert row["model"] == "qwen3.5:9b"
    assert row["num_ctx"] == 8192
    assert row["prompt_hash"], "a result without its pins is not a result"
    # The whole pin set and the adapter, so a new pin is additive and a
    # provider is on record (2026-09-09).
    import json as _json
    whole = _json.loads(row["pins_json"])
    assert whole["model"] == "qwen3.5:9b" and "max_tokens" in whole
    assert row["backend"] == "scripted"


def test_tool_calls_are_logged_for_assertion(db):
    backend = ScriptedBackend([
        "TOOL: problem.consult()",
        "Nothing there yet.",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))
    calls = db.execute("SELECT fn FROM tool_calls WHERE session_id=? ORDER BY seq",
                       (outcome.session_id,)).fetchall()
    assert "problem.consult" in [c["fn"] for c in calls]


def test_readonly_mode_cannot_write(db):
    backend = ScriptedBackend([
        "TOOL: problem.assert(id='i9', text='x', kind='in_scope')",
        "ok",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend, mode="readonly",
                          pins=Pins(model="scripted"))
    assert any("working set" in e for e in outcome.errors)
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 0
    assert version_of(db, "items") == 0


def test_a_result_under_the_cap_arrives_whole(db):
    """No notice, no loss — the commonest case must be the boring one."""
    from rota.core.runner import RESULT_CHARS, _render

    text = _render({"path": "signature.py", "body": "x" * 100})
    assert "CUT " not in text
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

    assert "CUT the result" in text, "the cut is invisible to the model"
    # Against the rendered length, not the JSON-encoded one. A dict carrying
    # long text now renders as text -- `code.area` and `code.source` handed
    # source to the model as an escaped JSON string, every newline a literal
    # `\n` -- so the total the notice reports is the size of what the
    # model would actually have been shown.
    shown = len(full) + len(chr(10) + "[body]" + chr(10))
    assert f"{shown - RESULT_CHARS:,} of {shown:,}" in text, \
        "the notice must say how much was withheld, not merely that some was"
    assert "Nothing returns the rest of this result" in text, \
        "a result with no next range must say so rather than name one"


def test_a_long_read_reaches_the_model_past_the_old_cap(db):
    """
    The regression this pins: results were cut to 1200 characters before the
    model saw them, so `code.source(start=0, end=400)` did its job and delivered
    a docstring. Nothing in the suite noticed, because every fixture's tool
    results were short.
    """
    # A read the session has to ask for. `problem.consult` takes no arguments,
    # so it arrives pushed, and a pushed read is already-run by the time the
    # model speaks -- which is the right answer to a different question than
    # this one. The cap on a *fetched* result needs a fetch.
    for i in range(20):
        db.execute("INSERT INTO decisions (id, author, text) VALUES (?,?,?)",
                   (f"d{i:02d}", "vision_keeper", f"scope ruling {i:02d} " + "detail " * 20))
    db.execute("UPDATE decisions SET text = 'CANARY_PAST_THE_OLD_CAP ' || text "
               "WHERE id='d19'")

    backend = ScriptedBackend(["TOOL: decisions.search(query='scope')", "Seen."])
    outcome = run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))
    assert outcome.committed, outcome.errors

    _, user = backend.calls[1]
    served = user[user.rindex("OK decisions.search ->"):]
    assert len(served) > 1200, "the old cap is still in force"
    assert "CANARY_PAST_THE_OLD_CAP" in served, \
        "the tail of the result never reached the model"


def test_working_set_is_pushed_not_only_offered(db):
    """A cold session should not have to fetch what it obviously needs."""
    db.execute("INSERT INTO items (id, text, kind) "
               "VALUES ('i_existing','prior scope','in_scope')")
    backend = ScriptedBackend(["done"])
    run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))

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


def test_a_session_that_writes_its_own_tool_results_is_told(db):
    """
    The model writing the harness's half of the conversation.

    An Architect woken to constrain an external commitment produced this and
    then reasoned from it:

        TOOL: model.load(ids=['s_4976a0'])
        OK model.load -> [{'id': 's_4976a0', 'text': 'invoices have to ...'}]
        TOOL: model.consult(grains=None)
        OK model.consult -> []

    Nothing ran. It predicted the feedback, believed itself and carried on, and
    the inventions were plausible because it had seen real ones earlier in the
    same transcript. A harness fault rather than a judgement one: the reply and
    the results are the same kind of text in the same stream.

    The parser only ever took the `TOOL:` lines, so this never became a call —
    which is exactly why it was invisible. The session went on believing them.
    """
    backend = ScriptedBackend([
        "TOOL: problem.consult()\n"
        "OK problem.consult -> [{'id': 'i_invented', 'text': 'made up'}]\n"
        "TOOL: problem.assert(id='i1', text='ok', kind='in_scope')",
        "Done.",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))

    assert "wrote its own tool results" in outcome.errors
    _, user = backend.calls[1]
    assert "did not come from me" in user, "the session was never told"


def test_a_real_result_in_the_transcript_is_not_mistaken_for_a_fabrication(db):
    """
    The harness's own feedback is echoed back in the next prompt, so a check
    looking for `OK x.y ->` anywhere would fire on every turn after the first.
    Only what the *model* said is examined.
    """
    backend = ScriptedBackend([
        "TOOL: problem.consult()",
        "Nothing there. TOOL: problem.assert(id='i1', text='ok', kind='in_scope')",
        "Done.",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))

    assert "wrote its own tool results" not in outcome.errors
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 1


def test_the_calls_after_an_invented_result_never_run(db, worktree):
    """
    Night 86's s145, turn 6: a source call, a result the seat wrote for
    itself, and then the write and the commit it built on that result. The
    runner flagged the reply and ran all three (frame 75, 2026-09-23).

    Rule 1 of frame 77: the turn's calls run up to the first invented result,
    and every call after it is dropped. The calls behind the invention were
    built on it, so the seat decides them again with the real result in view.
    The write it sends next turn runs.
    """
    (worktree / "src" / "acct.py").write_text("def delete(x):\n    return x\n")
    backend = ScriptedBackend([
        "TOOL: code.source(path='src/acct.py')\n"
        "OK code.source -> def delete(x): return x\n"
        "TOOL: code.write(path='src/acct.py', text='def delete(x):"
        "\n    return \"from memory\"\n')\n"
        "TOOL: code.commit(message='tombstone the account')",
        "TOOL: code.write(path='src/acct.py', text='VALUE = 1\n')",
        "Done.",
    ])
    outcome = run_session(db, wake_developer(), backend=backend,
                          pins=Pins(model="scripted"), batch_id="b1")

    assert "wrote its own tool results" in outcome.errors
    after = backend.calls[1][1]                  # the prompt of the next turn
    assert "OK code.source -> path: src/acct.py" in after, \
        "the call before the invention did not run"
    named = after.split("NOT RUN")[-1]           # the line that names the tail
    assert "code.write(path='src/acct.py'" in named, "the write is not named"
    assert "code.commit(message=" in named, "the commit is not named"
    assert (worktree / "src" / "acct.py").read_text() == "VALUE = 1\n", \
        "the write behind the invention landed, or the next turn's did not"


def test_an_invented_result_before_any_call_holds_every_call(db):
    """
    The edge of rule 1: the invention comes first, so no call of the turn is
    dispatched. Every one of them was built on a result the runner never
    sent.
    """
    backend = ScriptedBackend([
        "OK problem.consult -> [{'id': 'i_invented', 'text': 'made up'}]\n"
        "TOOL: problem.assert(id='i1', text='ok', kind='in_scope')",
        "Done.",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted"))

    assert "wrote its own tool results" in outcome.errors
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 0, \
        "a call after the invention ran"
    block = backend.calls[1][1].split("\n\n")[-1]
    assert "NOT RUN" in block and "problem.assert(id='i1'" in block, \
        f"the call was not named as unrun: {block}"


def test_a_rewritten_call_after_an_invention_is_held(db, worktree):
    """
    The parser rewrites two shapes before it scans: a `[text]` block becomes a
    quoted value, and a bare `refs=a, b` becomes a list. The call's raw is then
    not in the completion. The fallback used the offset in the rewritten text,
    and a rewrite that shortened the text put a commit written after the
    invention ahead of it, so the commit ran (the diff review of frame 77,
    2026-09-23). The marker locates the call now, and a call nothing locates
    goes last.
    """
    # Three one-line blocks shorten the scanned text by 5 characters, and the
    # invented line is 10 long. The old fallback put the escalation at 143
    # against the invention's 144, and it ran.
    backend = ScriptedBackend([
        "TOOL: code.write(path='a.py', text=[text]\nA = 1\n"
        "TOOL: code.write(path='b.py', text=[text]\nB = 2\n"
        "TOOL: code.write(path='c.py', text=[text]\nC = 3\n"
        "OK a.b: x\n"
        "TOOL: msg.escalate_architect(refs=b1, a, round_no=0)",
        "Done.",
        "Nothing is owed.",
    ])
    outcome = run_session(db, wake_developer(), backend=backend,
                          pins=Pins(model="scripted"), batch_id="b1")

    assert "wrote its own tool results" in outcome.errors
    # The third block runs to the next `TOOL:` line, so it carries the invented
    # line and its write is refused as invalid Python. The first two landed.
    assert (worktree / "b.py").exists(), \
        f"the writes before the invention did not run: {outcome.errors}"
    after = backend.calls[1][1]
    at = after.find("NOT RUN, because you wrote a tool result of your own")
    assert at >= 0, "no call was held for the invention"
    assert "msg.escalate_architect(" in after[at:at + 400], \
        f"the call after the invention is not named: {after[at:at + 400]}"
    # Dispatched, the escalation fails or sends, and either leaves a trace.
    assert not any("msg.escalate_architect" in e for e in outcome.errors), \
        f"the escalation after the invention was dispatched: {outcome.errors}"
    sent = db.execute("SELECT COUNT(*) n FROM messages "
                      "WHERE from_role='developer'").fetchone()["n"]
    assert sent == 0, "the escalation after the invention was sent"


def test_a_prose_turn_after_an_invention_lands_nothing(db, worktree):
    """
    The stood-by path runs a held call when the seat replies with prose,
    because a hold the seat never revised is the seat standing by it. An
    invented tail is not a hold of that kind: the seat stood by a plan it
    built on a result nothing returned (the design review of frame 77,
    finding 1).

    So "Done." after an invention lands nothing, and the session is barren.
    """
    (worktree / "src" / "acct.py").write_text("def delete(x):\n    return x\n")
    backend = ScriptedBackend([
        "OK code.source -> def delete(x): return x\n"
        "TOOL: code.write(path='src/acct.py', text='from memory\n')",
        "Done.",
        "Nothing is owed.",
    ])
    outcome = run_session(db, wake_developer(), backend=backend,
                          pins=Pins(model="scripted"), batch_id="b1")

    assert "wrote its own tool results" in outcome.errors
    assert (worktree / "src" / "acct.py").read_text() == \
        "def delete(x):\n    return x\n", "the from-memory write landed"
    assert "ended a tick with nothing done" in outcome.errors, \
        "the session wrote something after all"


def test_a_read_already_answered_does_not_hold_the_action_again(db):
    """
    The livelock the read boundary caused, which cost a case 3/5 -> 0/5.

    A Terminologist asked five `glossary.lookup`s and then sent its answer. The
    answer was held behind the reads, correctly, and the session was told to
    send it again. It re-sent the batch intact — the five lookups *and* the
    answer — so the hold fired on the same five reads, and again, and again.
    Twelve turns and no message, from a model that had chosen the right action
    in the first completion.

    A repeated read is not an outstanding question. The boundary exists so that
    nobody acts on something unseen, and by the second time round it has been
    seen.
    """
    db.execute("INSERT INTO glossary_terms (id, term, sense_short) "
               "VALUES ('t1','account','a customer record')")
    seed_provenance(db, "glossary_terms", "t1", "observed")
    batch = ("TOOL: problem.consult()\n"
             "TOOL: msg.report_liaison(refs=['u1'])")
    backend = ScriptedBackend([batch, batch, "Done."])

    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted"))

    assert outcome.committed, outcome.errors
    sent = db.execute("SELECT COUNT(*) n FROM messages WHERE from_role='vision_keeper'"
                      ).fetchone()["n"]
    assert sent == 1, "the action was held behind a read the session had already seen"


def test_a_new_read_holds_the_action_which_executes_if_stood_by(db):
    """
    The boundary is a deferral, not a veto. Acting on a read you have not seen
    was the commonest fault in the suite — 309 of 598 multi-call completions —
    and a first-time read still stops the write behind it *that turn*. But S0
    walk seven measured the other failure: four valid encodes held, the model
    declaring the work done, the session ending clean, and nothing written. A
    session that ends with the read's answer and the NOT RUN notice in view,
    without revising, has said the plan stands — the held tail executes.
    """
    db.execute("INSERT INTO decisions (id, author, text) "
               "VALUES ('d1','vision_keeper','scope ruling on closing an account')")

    backend = ScriptedBackend([
        "TOOL: decisions.search(query='scope')\n"
        "TOOL: problem.assert(id='i1', text='premature', kind='in_scope')",
        "Done.",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted"))

    _, user = backend.calls[1]
    assert "NOT RUN" in user, \
        "the write must not run in the same turn as an unseen read"
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 1, \
        (f"ending without revising is standing by the plan: {outcome.errors}")


def test_stood_by_refusals_get_one_answering_turn(db):
    """
    Walk twenty-one: seven encodes held, the model declared them done, the
    stood-by execution refused every one, and the session was over before
    the refusals could be read. A refusal is the door's half of a
    conversation; once, the model gets to answer it.
    """
    db.execute("INSERT INTO decisions (id, author, text) "
               "VALUES ('d1','vision_keeper','scope ruling on closing an account')")

    backend = ScriptedBackend([
        "TOOL: decisions.search(query='scope')\n"
        "TOOL: problem.assert(id='i1', text='premature', kind='nonsense')",
        "Done.",
        "TOOL: problem.assert(id='i1', text='premature', kind='in_scope')",
        "Done.",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted"))

    _, user = backend.calls[2]
    assert "these were refused" in user
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 1, \
        outcome.errors


def test_a_revising_turn_clears_the_held_tail(db):
    """
    The other half of standing by: any tool call in a later turn is the model's
    revised will, and the held tail behind it is dead. Only the revision lands.
    """
    db.execute("INSERT INTO decisions (id, author, text) "
               "VALUES ('d1','vision_keeper','scope ruling on closing an account')")

    backend = ScriptedBackend([
        "TOOL: decisions.search(query='scope')\n"
        "TOOL: problem.assert(id='i1', text='premature', kind='in_scope')",
        "TOOL: problem.assert(id='i1', text='the ruling says close it', "
        "kind='in_scope')",
        "Done.",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted"))

    rows = db.execute("SELECT text FROM items").fetchall()
    assert [r["text"] for r in rows] == ["the ruling says close it"], \
        (f"the held original must not also run: {outcome.errors}")


def test_the_transcript_is_trimmed_from_the_middle_not_the_front(db):
    """
    Raising the result cap fixed one turn and broke several.

    One round of an Architect's four survey reads is 12,947 characters and the
    opening prompt is another 13,500, so by the third round the transcript
    passed a 12,288-token window. An overflowing prompt is cut *from the front*,
    which is where the brief lives: "you must attest before the session ends"
    was the first thing evicted. Ten of twelve areas closed and two spun for
    sixty sessions, reading and never attesting.

    The wake and the latest exchange are what a session needs; the middle is
    what it has already acted on.
    """
    from rota.core.runner import _fit

    wake = "WAKE: you are surveying src/billing"
    blocks = [wake] + [f"turn {i} " + "x" * 4000 for i in range(1, 7)]
    fitted = _fit(blocks, budget=12000)

    assert fitted[0] == wake, "the wake was evicted; the role no longer knows its job"
    assert fitted[-2:] == blocks[-2:], "the latest exchange was dropped"
    assert any("dropped to fit" in b for b in fitted), "the loss is silent"
    assert sum(len(b) + 2 for b in fitted) <= 12000 + len(fitted[1])


def test_a_transcript_that_fits_is_left_exactly_alone(db):
    from rota.core.runner import _fit

    blocks = ["wake", "a", "b", "c"]
    assert _fit(blocks, budget=100_000) == blocks


def test_asking_the_same_read_twice_does_not_pay_twice(db):
    """
    The stalled sessions called `surveys.consult` three times and
    `glossary.consult` twice, each copy paying full freight into a transcript
    that was already overflowing. Nothing the session did could have changed the
    answer, so the second telling is a line, not four thousand characters.
    """
    for i in range(20):
        db.execute("INSERT INTO decisions (id, author, text) VALUES (?,?,?)",
                   (f"d{i:02d}", "vision_keeper", "scope " + "detail " * 20))

    backend = ScriptedBackend([
        "TOOL: decisions.search(query='scope')",
        "TOOL: decisions.search(query='scope')",
        "Done.",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))
    assert outcome.committed, outcome.errors

    first = backend.calls[1][1]
    second = backend.calls[2][1]
    assert "unchanged since you asked" in second, "the repeat was re-rendered in full"
    assert len(second) - len(first) < 400, "the repeat cost nearly as much as the first"


def _seed_decisions(db, n=20):
    """Rows whose text every query below matches, so two keys answer alike."""
    for i in range(n):
        db.execute("INSERT INTO decisions (id, author, text) VALUES (?,?,?)",
                   (f"d{i:02d}", "vision_keeper", "scope " + "detail " * 20))


def test_the_repeat_line_does_not_point_at_an_evicted_answer(db):
    """
    Two notices in one prompt said opposite things. The eviction notice says the
    earlier exchanges were dropped and to re-read what you need. The repeat line
    said the answer is above. Once the eviction has taken the block that held
    the answer, the answer is not above, and the seat was sent to read a turn
    that is not there. Measured on 8 of 8,183 recorded prompts, all 8 of those
    that could carry both (frame 46's design record, section 2.6).

    The eviction notice is true as written, so the repeat line gives way: the
    result is served again and says why. A window this small floors the budget
    at 2,000 characters, so turn 3 evicts the middle, which is where turn 1's
    answer lives.
    """
    from rota.core.runner import _EVICTED_PHRASE

    _seed_decisions(db)
    ask = "TOOL: decisions.search(query='scope')"
    backend = ScriptedBackend([ask,
                               "thinking. " * 300 + "\nTOOL: decisions.search(query='detail')",
                               ask, "Done."])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted", temperature=0.0, num_ctx=512))

    assert outcome.committed, outcome.errors
    served = backend.calls[3][1]                 # turn 3's results, as turn 4 saw them
    assert _EVICTED_PHRASE in served, "the eviction is not in this prompt at all"
    assert "the answer is above" not in served, \
        "the seat was sent to read a turn the eviction took"
    assert f"the earlier answer was {_EVICTED_PHRASE}" in served, \
        "the repeat said nothing about the eviction"
    assert "decisions.search ran again" in served, "the line names no call"


def test_the_repeat_line_claims_nothing_about_this_prompt(db):
    """
    The line is read one turn after it is written, and the eviction runs in
    between. "The answer is above" was true when the guard wrote it and false
    when the seat read it: night 88's s137 saw the span at turns 3, 4 and 5,
    saw it gone at turn 6, and was told at turn 6 that the answer was above.

    So the line names the call that returned the answer and says nothing about
    where the answer sits. A line that makes no claim about this prompt cannot
    be one turn early. Both wordings survive, one for a pushed answer and one
    for an answer the seat asked for: 4,907 of 18,435 cassettes carry the
    asked-for line and 572 carry the pushed twin (measured 2026-09-20).
    """
    from rota.core.runner import _EVICTED_PHRASE

    _seed_decisions(db)
    ask = "TOOL: decisions.search(query='scope')"
    backend = ScriptedBackend([ask, ask, "Done."])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted", temperature=0.0, num_ctx=12288))

    assert outcome.committed, outcome.errors
    second = backend.calls[2][1]
    line = [ln for ln in second.splitlines()
            if ln.startswith("OK decisions.search ->")][-1]
    assert "unchanged since you asked earlier this session" in line, \
        "the repeat was re-rendered in full with nothing evicted"
    assert "What decisions.search returned then still stands" in line, \
        f"the line names no call: {line}"
    assert "above" not in line, f"the line still points at a block: {line}"
    assert _EVICTED_PHRASE not in second, "nothing was evicted in this session"


def test_the_pushed_repeat_line_also_claims_nothing_about_this_prompt(db):
    """
    The pushed twin. A read the wake already ran is served when the seat asks
    for it, because "you already have this" reads to an 8B model as "there is
    nothing here for you" -- see the note at `fresh_read`. The second asking is
    a line, and the line carries the same claim the asked-for one carries: the
    call that returned the answer, and nothing about where the answer sits.
    """
    db.execute("INSERT INTO items (id, text, kind) VALUES (?,?,?)",
               ("i01", "people can close their account", "in_scope"))

    ask = "TOOL: problem.consult()"
    backend = ScriptedBackend([ask, f"Again.\n{ask}", "Done."])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted", temperature=0.0, num_ctx=12288))

    assert outcome.committed, outcome.errors
    second = backend.calls[2][1]
    line = [ln for ln in second.splitlines()
            if ln.startswith("OK problem.consult ->")][-1]
    assert "was run for you before you started" in line, \
        f"the pushed wording is gone: {line}"
    assert "What problem.consult returned then still stands" in line, \
        f"the line names no call: {line}"
    assert "above" not in line, f"the line still points at a block: {line}"


def test_repeats_inside_one_reply_are_suppressed_after_an_eviction(db):
    """
    The case the range never had: the eviction is in the prompt, and the repeats
    are in one reply. An answer made this turn cannot be in this turn's prompt,
    so the eviction test read every such repeat as evicted and served it again.
    Three identical `decisions.search` calls came back as 14,189 characters with
    three full results and no refusal, against 242 characters, one line and one
    refusal before the test existed (the diff review of 0cc624b, finding 1).

    That is the s71 storm the refusal stops, so the turn a key was answered in
    is what decides: an earlier turn's answer can be evicted, and this turn's
    cannot.
    """
    from rota.core.runner import _EVICTED_PHRASE

    _seed_decisions(db, 60)
    ask = "TOOL: decisions.search(query='scope')"
    backend = ScriptedBackend([ask,
                               "thinking. " * 1200 + "\nTOOL: decisions.search(query='detail')",
                               f"{ask}\n{ask}", "Done."])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted", temperature=0.0, num_ctx=12288))

    assert outcome.committed, outcome.errors
    assert _EVICTED_PHRASE in backend.calls[2][1], \
        "nothing was evicted, so this shape proves nothing"
    block = backend.calls[3][1].split("\n\n")[-1]        # this turn's results

    assert block.count("OK decisions.search ->") == 1, \
        f"one result, not one per asking: {len(block):,} characters"
    assert block.count("the earlier answer was") == 1, \
        "the eviction is named once, for the asking that earned it"
    assert any("asked three times" in e for e in outcome.errors), \
        "the second asking in the same reply was not refused"
    assert len(block) < 9_000, \
        f"the repeats paid full freight: {len(block):,} characters"


def _evicting_repeats(ask: str, askings: int = 3) -> list[str]:
    """
    A script whose eviction still stands when the next asking arrives.

    Turn 2 is long enough to push turn 1 out of a 2,000 character budget, and
    every later result is cut to the floor, so the answer never comes back
    into the prompt whole. The prose varies because three identical turns end
    a session, and the count here is of callings, not of turns.
    """
    prose = ["Again.", "Once more.", "Last time.", "And again."]
    return ([ask, "thinking. " * 300 + "\nTOOL: decisions.search(query='detail')"]
            + [f"{prose[i]}\n{ask}" for i in range(askings - 1)]
            + ["Done."])


def test_an_evicted_answer_is_served_again_and_a_present_one_is_a_line(db):
    """
    Rule 2 of frame 77. A refusal that points at a deleted answer is what the
    seat answers by writing the result itself: every local model on the box
    invents under that pointer (frame 75, 2026-09-23). So the bound is on the
    renders and not on the askings, and the eviction decides which the seat
    gets.

    The asking after the eviction is served in full, with no refusal. The
    asking after that reads its own answer in the prompt, so it gets the line.
    """
    from rota.core.runner import _EVICTED_PHRASE

    _seed_decisions(db, 60)
    ask = "TOOL: decisions.search(query='scope')"
    backend = ScriptedBackend([
        ask,
        "thinking. " * 1200 + "\nTOOL: decisions.search(query='detail')",
        f"Again.\n{ask}", f"Once more.\n{ask}", "Done."])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted", temperature=0.0, num_ctx=12288))

    assert outcome.committed, outcome.errors
    evicted = backend.calls[3][1].split("\n\n")[-1]   # the asking after the eviction
    assert _EVICTED_PHRASE in backend.calls[2][1], \
        "nothing was evicted, so this shape proves nothing"
    assert evicted.count("the earlier answer was") == 1, \
        "the evicted answer was not served again"
    assert "not answered again" not in evicted, \
        f"an evicted answer met a refusal: {evicted[:200]}"
    present = backend.calls[4][1].split("\n\n")[-1]   # the asking with the block
    assert "unchanged since you asked" in present, \
        f"the answer is in this prompt, so the line is owed: {present[:200]}"
    assert not any("repeat refused" in e for e in outcome.errors), \
        outcome.errors


def test_a_key_is_served_three_times_and_then_the_room_refuses(db):
    """
    The bound on the re-serve. A result larger than the room the exchange
    leaves is evicted on every turn, so serving it on every asking is night
    88's s137 again: served in full at turns 7, 8 and 9, dead on the
    identical-turn stop with nothing written (the design review of frame 77,
    finding 3).

    Three serves a key a session. The fourth asking is refused by the room,
    and the refusal asks for a span that fits. It never says to use what the
    call returned earlier, because the window took that answer.
    """
    _seed_decisions(db)
    ask = "TOOL: decisions.search(query='scope')"
    backend = ScriptedBackend(_evicting_repeats(ask, askings=4))
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted", temperature=0.0, num_ctx=512))

    assert outcome.committed, outcome.errors
    served = [backend.calls[i][1].split("\n\n")[-1] for i in (1, 3, 4, 5)]
    assert served[0].count("OK decisions.search ->") == 1, \
        "the first asking was not served"
    assert served[1].count("the earlier answer was") == 1, \
        "the second serve did not say the earlier answer was taken"
    assert served[2].count("the earlier answer was") == 1, \
        "the third serve did not happen"
    assert served[3].count("OK decisions.search ->") == 0, \
        f"the result was served a fourth time: {served[3][:200]}"
    assert "does not fit the room" in served[3], \
        f"the refusal does not name the room: {served[3][:200]}"
    assert "narrower span" in served[3], "the refusal asks for nothing"
    assert "returned earlier" not in served[3], \
        "the refusal points at an answer the window took"
    assert any("repeat refused" in e for e in outcome.errors), \
        "the fourth asking was never refused"


def test_three_identical_calls_in_one_reply_meet_the_refusal(db):
    """
    The s71 storm, in its own reply. Session s71 sent 331 calls in one reply on
    both nights and 327 came back as the repeat line, about 90,000 characters
    that became turn 2's whole prompt. An answer made this turn cannot be in
    this turn's prompt, so membership alone read every such repeat as evicted
    and served it again: three identical calls came back as 14,189 characters
    and no refusal (the diff review of 0cc624b, finding 1). The turn a key was
    answered in is what separates the two cases, and this shape must stay
    closed.
    """
    _seed_decisions(db)
    ask = "TOOL: decisions.search(query='scope')"
    backend = ScriptedBackend(["\n".join([ask] * 3), "Done."])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted", temperature=0.0, num_ctx=12288))

    assert outcome.committed, outcome.errors
    block = backend.calls[1][1].split("\n\n")[-1]        # this turn's results
    assert block.count("OK decisions.search ->") == 2, \
        "one result and one line, not one result per calling"
    assert block.count("unchanged since you asked") == 1, "the second copy is the line"
    assert block.count("asked three times") == 1, "the third copy is the refusal"
    assert len([e for e in outcome.errors if "repeat refused" in e]) == 1, \
        outcome.errors
    assert len(block) < 9_000, \
        f"the repeats paid full freight: {len(block):,} characters"


def test_a_pushed_read_does_not_hold_the_action_behind_it(db):
    """
    Asking for what you were already handed is not asking a question.

    The hold exists so nobody acts on a read they have not seen, and a pushed
    read has been seen -- it is in the opening prompt, above the sentence saying
    so. But the detector started empty, so re-requesting one counted as a fresh
    question and held the write behind it for a turn. Spelling a default out
    loud is the normal thing for a small model to do, which is why the key is
    canonical: `problem.consult()` and `problem.consult(...)` with a default are
    one call.

    The result is still served. Withholding it as well was measured and cost two
    cases -- see the note at `fresh_read` -- because "you already have this"
    reads to an 8B model as "there is nothing here for you".
    """
    db.execute("INSERT INTO items (id, text, kind) VALUES (?,?,?)",
               ("i01", "people can close their account", "in_scope"))

    backend = ScriptedBackend([
        "TOOL: problem.consult()\n"
        "TOOL: problem.assert(id='i2', text='and export them', kind='in_scope')",
        "Done.",
    ])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted"))

    assert outcome.committed, outcome.errors
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 2, \
        "the write was held behind a read the session had already been given"
    _, second = backend.calls[1]
    assert "NOT RUN" not in second


def test_the_pushed_working_set_obeys_the_same_cap_as_a_fetched_one(db):
    """
    The push was raw while every requested result was capped.

    `code.survey` on icalendar's `src/icalendar` — 1,357 of that repository's
    1,731 grains in a single area — arrived in the opening prompt as 198,366
    characters, about 49,000 tokens against a 12,288 window. The prompt was four
    times the context before the session took a turn; Ollama cut it from the
    front, the brief went with it, and twenty-five sessions read three things
    and stopped without ever attempting to attest.

    The identical call costs 6,086 characters when the model asks for it. One
    rule for how much of anything a session sees, and this is the path where it
    matters more, because nobody chose to fetch it.

    The push has its own cap now, `PUSH_CHARS`, a page above the pushes' own
    budgets: a pushed read is the wake, and `code.area` repacked to show an
    area its own files was being cut back to the fetched-result cap with "ask
    for the next range", which a push cannot. Capped still, and announced.
    """
    from rota.core.runner import PUSH_CHARS, build_prompt
    from rota.core.sandbox import build as build_sandbox

    huge = {"grains": [f"src/pkg/module_{i:04d}.py" for i in range(4000)]}
    sb = build_sandbox("vision_keeper", db)
    _, user = build_prompt("vision_keeper", sb, wake_vision_keeper(),
                           {"code.survey": huge}, "brief")

    assert len(user) < PUSH_CHARS + 2000, \
        f"the pushed working set is uncapped: {len(user):,} characters"
    assert "CUT the result" in user, "it was cut without saying so"


def test_a_wake_too_big_for_the_window_is_cut_rather_than_protected(db):
    """
    `_fit` kept `transcript[0]` whole unconditionally — and the wake is where
    the pushed working set lives, so the one block that could overflow the
    window on its own was the one block never trimmed. Protecting it is right
    until it is the problem.
    """
    from rota.core.runner import _fit

    fitted = _fit(["WAKE " + "x" * 50_000, "turn 1", "turn 2", "turn 3"],
                  budget=12_000)

    assert sum(len(b) + 2 for b in fitted) <= 12_000, "still overflowing"
    assert fitted[0].startswith("WAKE "), "the wake lost its head, not its tail"
    assert "CUT your wake" in fitted[0], "the wake was cut silently"
    assert fitted[-1] == "turn 3", "the latest exchange was dropped instead"


def test_a_single_oversized_block_is_cut(db):
    """
    The cut sat behind an early return on a transcript of fewer than four
    blocks, and turn one holds one block. Night 85 (2026-09-18): two landing
    sessions were sent a 17,220 token wake into a 12,288 window, the server
    kept the tail, and each seat answered as a generic assistant with no tool
    call. The wake is cut on every turn now.
    """
    from rota.core.runner import _fit

    for blocks in (["WAKE " + "x" * 50_000],
                   ["WAKE " + "x" * 50_000, "turn 1"],
                   ["WAKE " + "x" * 50_000, "turn 1", "turn 2"]):
        fitted = _fit(list(blocks), budget=12_000)
        assert len(fitted[0]) < 12_000, f"{len(blocks)} block(s) went uncut"
        assert fitted[0].startswith("WAKE "), "the wake lost its head"
        assert "CUT your wake" in fitted[0], "the wake was cut silently"
        assert fitted[1:] == blocks[1:], "a later exchange was dropped"


def test_the_fit_budget_is_half_the_window(db):
    """
    `_fit` is the backstop, and it was measuring the wrong window. Two thirds
    of `num_ctx` is about 8,250 tokens on a 12,288 window, well above the 6,146
    a session gets when the server cuts it, so `_fit` never fired on a wake the
    server would collapse (the diff review of 8ebbae1). Half the window, at the
    measured 3.97 characters to the token.
    """
    from rota.core.runner import _fit_budget

    system = 4133                             # a landing system prompt, measured
    budget = _fit_budget(12288, system)

    assert (budget + system) / 3.97 <= 12288 / 2, \
        f"{budget} characters is more than half a 12,288 window"
    assert budget > 12_000, "a budget this small would cut every ordinary wake"
    # A small window still leaves a floor, and a huge system prompt cannot
    # drive the budget negative.
    assert _fit_budget(2048, 9_000) == 2000


def _seed(path):
    """The `db` fixture's rows, on a path of the caller's choosing. Two runs of
    one session need two databases seeded the same way."""
    conn = init_db(path)
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('u1','principal','let users delete their account',1)")
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                 "VALUES ('m1','t1','liaison','vision_keeper','deliver',1)")
    return conn


def _replayed(tmp_path, script, pins):
    """
    One session recorded, then the same session replayed from the cassette.

    The check under test has to fire on the path the register runs on.
    `truncated` is assigned in `OllamaBackend` alone, so a whole-prompt check
    placed beside it was dead for every recorded case, and frame 43 shipped
    that fault once. Two fresh databases seeded alike give both runs the same
    prompt, so the cassette hits and `ReplayOnlyBackend` never calls a model.
    """
    from rota.llm.cassettes import (RecordingBackend, ReplayOnlyBackend,
                                    open_dev_db)

    dev = open_dev_db(tmp_path / "dev.db")
    run_session(_seed(tmp_path / "recorded.db"), wake_vision_keeper(),
                backend=RecordingBackend(ScriptedBackend(list(script)), dev),
                pins=pins)
    outcome = run_session(_seed(tmp_path / "replayed.db"), wake_vision_keeper(),
                          backend=ReplayOnlyBackend(dev), pins=pins)
    assert outcome.result is not None and outcome.result.turns, outcome.errors
    return outcome


def _overruns(turns, num_ctx):
    """
    Each turn's prompt, and how far past its limit the prompt went.

    Two limits, and the smaller binds: `_fit`'s promise, which is the budget
    plus the system prompt it was charged for, and half the window at 3.97
    characters to the token. `len(system)` cancels out of the first, so the
    first alone was blind at the `max(2000, ...)` floor (the diff review of
    0cc624b, finding 3).
    """
    from rota.core.runner import _fit_budget

    return [(t, (len(t.system) + len(t.user))
             - min(len(t.system) + _fit_budget(num_ctx, len(t.system)),
                   int(num_ctx / 2 * 3.97))) for t in turns]


def test_the_assembled_prompt_of_a_replayed_turn_is_inside_the_budget(tmp_path):
    """
    Nothing measured the assembled prompt before the send. The only
    whole-prompt number came back with the reply, and the budget the prompt was
    built against was never checked against the prompt itself.

    The invariant is `_fit`'s promise, and it holds for the shape the runner
    builds: a wake, then a reply and a results block on every turn. Two shapes
    break it, and the runner reaches neither. `_cap_exchange` returns a
    two-block transcript untouched, and at the `max(2000, ...)` floor it lends
    room the budget does not hold.
    """
    from rota.core.runner import _prompt_overrun

    pins = Pins(model="scripted", temperature=0.0, num_ctx=12288)
    outcome = _replayed(tmp_path, [
        "TOOL: problem.assert(id='i1', text='users can delete their account', "
        "kind='in_scope')", "Done."], pins)

    assert outcome.committed, outcome.errors
    from rota.core.runner import _fit_budget

    for turn, over in _overruns(outcome.result.turns, 12288):
        assert over <= 0, f"turn {turn.seq} is {over} characters over its budget"
        assert _prompt_overrun(turn.system, turn.user,
                               _fit_budget(12288, len(turn.system)), 12288) == ""
    assert not [e for e in outcome.errors if "over budget" in e], outcome.errors


def test_an_over_budget_prompt_is_named_before_it_is_sent(tmp_path):
    """
    The line a session leaves when the prompt outgrew its limit. The shape is
    the `max(2000, ...)` floor: a window this small floors the budget at 2,000
    characters, `_cap_exchange` then lends each block of the latest exchange
    its own floor of 1,000, and the wake rides on top. The runner does not
    reach this window, and the check is what says so when it does.

    Half the window binds here, not the budget. A system prompt of about 6,900
    characters is already past a 512-token window's half, so the floor cannot
    hide the overrun (the diff review of 0cc624b, finding 3).
    """
    pins = Pins(model="scripted", temperature=0.0, num_ctx=512)
    outcome = _replayed(tmp_path, [
        "TOOL: problem.assert(id='i1', text='users can delete their account', "
        "kind='in_scope')\n" + "saying it again. " * 400, "Done."], pins)

    lines = [e for e in outcome.errors if e.startswith("prompt over budget")]
    over_turns = [(t, n) for t, n in _overruns(outcome.result.turns, 512) if n > 0]
    assert over_turns, "nothing overran, so the line proves nothing"
    assert len(lines) == len(over_turns), (lines, [n for _t, n in over_turns])
    for line, (turn, over) in zip(lines, over_turns):
        assert f"by {over} characters" in line, line
        part, size = max(("the system prompt", len(turn.system)),
                         ("the transcript", len(turn.user)), key=lambda p: p[1])
        assert f"{part} is the largest part at {size}" in line, line


def test_an_index_read_is_a_table_not_repeated_field_names(db):
    """
    JSON repeats every field name on every row, and an index read is nothing but
    rows. `glossary.consult` spent 989 of its 4,151 characters restating "id",
    "term", "sense_short" and "provenance" twenty-three times — 24% of the
    payload, and 35% of `surveys.consult`.

    Strictly better than raising the cap, which buys the same headroom by losing
    information. Transposing loses none.
    """
    from rota.core.runner import _render

    rows = [{"id": f"t{i}", "term": f"term_{i}", "sense_short": "a short sense",
             "provenance": "observed"} for i in range(23)]
    table = _render(rows)
    as_json = json.dumps(rows, default=str)

    assert len(table) < len(as_json) * 0.8, \
        f"no saving: {len(table)} vs {len(as_json)}"
    assert table.count("sense_short") == 1, "the field name is still repeated"
    for r in rows:
        assert r["term"] in table, "a value was lost, not just the scaffolding"


def test_a_ragged_or_scalar_result_stays_json(db):
    """
    A header only means anything if every row has the same shape. Ragged rows
    under one header would mis-align silently, which is worse than verbose.
    """
    from rota.core.runner import _render

    assert _render({"path": "x.py", "text": "..."}).startswith("{")
    assert _render([{"a": 1}, {"b": 2}]).startswith("[")
    assert _render([{"a": 1}]).startswith("["), "one row is not a table"
    assert _render(["plain", "strings"]).startswith("[")


def test_a_pipe_in_a_value_cannot_forge_a_column(db):
    from rota.core.runner import _render

    out = _render([{"term": "a|b", "sense": "x"}, {"term": "c", "sense": "y"}])
    assert r"a\|b" in out


def test_reports_about_one_thing_arrive_as_one_group():
    """
    Dedupe was Liaison's judgement and is a join.

    The brief said what makes two reports one question -- both point back at the
    same statement -- and then asked the model to work it out anyway. Liaison
    does not make decisions; its responsibility is lossless communication, so
    the grouping arrives done and what is left is turning each group into words.

    Connected components, not pairs: A and B share a statement, B and C share a
    term, and all three are one question in three vocabularies. Pairwise
    grouping would put two questions to the principal.
    """
    from rota.core.runner import _group_by_shared_refs

    reports = [
        {"id": "m1", "from": "terminologist", "refs": ["g1", "g2", "s1"]},
        {"id": "m2", "from": "vision_keeper", "refs": ["i1", "s1"]},
        {"id": "m3", "from": "architect", "refs": ["g2", "k1"]},
        {"id": "m4", "from": "tester", "refs": ["c9"]},
    ]
    assert _group_by_shared_refs(reports) == [["m1", "m2", "m3"], ["m4"]]

    # Nothing shared is nothing merged, which is the case that must not regress:
    # a round of unrelated blockers is several questions and merging them would
    # lose one.
    apart = [{"id": "m1", "from": "a", "refs": ["x"]},
             {"id": "m2", "from": "b", "refs": ["y"]}]
    assert _group_by_shared_refs(apart) == [["m1"], ["m2"]]

    # A report carrying no refs is its own group rather than joining everything.
    bare = [{"id": "m1", "from": "a", "refs": []},
            {"id": "m2", "from": "b", "refs": []}]
    assert _group_by_shared_refs(bare) == [["m1"], ["m2"]]



def test_the_streamed_chunks_join_into_the_old_body_and_feed_the_live_view(tmp_path):
    """`stream: True` for the live view; the Completion is the same as before."""
    import json

    from rota.llm import llm as L

    class View:
        def __init__(self):
            self.got = []

        def token(self, t):
            self.got.append(t)

    chunks = [
        json.dumps({"message": {"role": "assistant", "content": "TOOL: "}, "done": False}),
        json.dumps({"message": {"role": "assistant", "content": "x.y(a=1)"}, "done": False}),
        json.dumps({"message": {"role": "assistant", "content": "",
                                "tool_calls": [{"function": {"name": "x.y", "arguments": {"a": 1}}}]},
                    "done": False}),
        json.dumps({"message": {"role": "assistant", "content": ""}, "done": True,
                    "prompt_eval_count": 123}),
    ]
    view = View()
    body = L._consume_stream(iter(chunks), view)
    assert body["message"]["content"] == "TOOL: x.y(a=1)"
    assert body["message"]["tool_calls"][0]["function"]["name"] == "x.y"
    assert body["prompt_eval_count"] == 123 and body["done"] is True
    assert "".join(view.got).startswith("TOOL: x.y(a=1)")


def test_the_live_view_is_one_file_overwritten_per_call(tmp_path, monkeypatch):
    from rota.llm import llm as L

    monkeypatch.setattr(L, "LIVE_PATH", str(tmp_path / "live.md"))
    v = L.LiveView.open(L.Pins(model="m"), "SYS", "USER")
    v.token("hello "); v.token("world\n"); v.close("done")
    text = (tmp_path / "live.md").read_text(encoding="utf-8")
    assert "## system prompt" in text and "SYS" in text and "USER" in text
    assert "hello world" in text and "[done]" in text
    v2 = L.LiveView.open(L.Pins(model="m"), "SYS2", "USER2"); v2.close("done")
    text2 = (tmp_path / "live.md").read_text(encoding="utf-8")
    assert "USER2" in text2 and "USER\n" not in text2.replace("USER2", "")



def test_a_pushed_read_is_not_cut_at_the_result_cap():
    """A pushed read is the wake. `cnt_14b` showed 5,900 of `code.area`'s
    13,726 characters with "ask for the next range", which a push cannot."""
    from rota.core import runner

    big = {"area": "src/x", "source": "x" * 12000}
    assert "CUT the result" in runner._render(big)
    assert "CUT the result" not in runner._render(big, runner.PUSH_CHARS)
    assert "CUT the result" in runner._render({"source": "x" * (runner.PUSH_CHARS + 10)},
                                         runner.PUSH_CHARS)



def test_a_stream_that_repeats_the_same_line_three_times_is_stopped_there():
    """One 14B turn wrote the same amend line nineteen times to the token cap,
    623 seconds. The third identical line is enough; the stream is left there
    and the connection's close stops the generation."""
    import json

    from rota.llm import llm

    line = 'glossary.amend(term="x", sense_body="a long enough body to count as a line", sense_short="s")'
    pulled = []

    def chunks():
        for i in range(40):
            piece = line + "\n"
            pulled.append(i)
            yield json.dumps({"message": {"role": "assistant", "content": piece}, "done": False}).encode()
        yield json.dumps({"message": {"role": "assistant", "content": ""}, "done": True}).encode()

    class Quiet:
        def token(self, *_): pass

    out = llm._consume_stream(chunks(), Quiet())
    assert out.get("done_reason") == "repeating"
    assert len(pulled) == 3, pulled
    assert out["message"]["content"].count(line) == 3


def test_a_cut_reply_with_no_call_is_shown_the_cut_once_and_the_session_commits(db):
    """clickI night 31 (2026-09-13): a first reply ran to the output cap with
    no call in it. The cut note went to a list the loop had not made yet,
    the session died on the NameError, and the same wake was dispatched 69
    times. The model reads what it sent, bounded, and the cut, once."""
    from rota.llm.llm import Completion

    class Cut(ScriptedBackend):
        def complete(self, system, user, pins, tools=None):
            c = super().complete(system, user, pins, tools)
            if len(self.calls) == 1:
                return Completion(text=c.text, pins=pins, backend=self.name,
                                  raw={"done_reason": "length"})
            return c

    backend = Cut(["I keep thinking about the stream. " * 400, "Nothing to add."])
    outcome = run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))

    assert outcome.committed, outcome.errors
    assert len(backend.calls) == 2, "the cut reply must be answered once, not ended on"
    second = backend.calls[1][1]
    assert "reply cut" in second
    assert len(second) - len(backend.calls[0][1]) < 6000, "the cut reply goes back bounded"


def test_a_barren_session_on_a_challenge_leaves_it_unresolved(db):
    """clickI night 33 (2026-09-13): the Tester's answers were all refused,
    the session committed with nothing, and the challenge read as answered.
    A challenge nobody answered goes to the ladder, not to 'answered'."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m2','t1','developer','tester','challenge',2)")
    db.commit()
    wake = Wake(role="tester", kind="message", message_id="m2", detail="challenge")
    outcome = run_session(db, wake, backend=ScriptedBackend(["I have nothing to add."]),
                          pins=Pins(model="scripted"))
    assert outcome.committed, outcome.errors
    row = db.execute("SELECT status, unresolved_note FROM messages WHERE id='m2'").fetchone()
    assert row["status"] == "unresolved", dict(row)
    assert row["unresolved_note"]


def test_the_same_refusal_three_times_ends_the_session(db):
    """clickI night 42 (2026-09-13): six encodes a turn against the same six
    refusals for twenty-two turns. The third identical refusal of the same
    call ends the session, and the note says so."""
    calls = [f"TOOL: problem.assert(id='i1', text='attempt {k}', kind='sideways')" for k in range(8)]
    backend = ScriptedBackend(calls + ["Done."])
    outcome = run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))
    assert outcome.committed, outcome.errors
    assert outcome.iterations == 4, outcome.iterations
    assert any("refused the same way in four turns" in e for e in outcome.errors)
    assert "will not be accepted again" in backend.calls[3][1], "the third turn is told once"


def test_two_refusals_in_one_turn_are_noted_in_a_stable_order(db):
    """Frame 71 (2026-09-23): `turn_refusals` is a set of tuples, and a set
    iterates in the process's hash-seed order. A turn that noted two refusals
    rendered them one way in the process that recorded the cassette and the
    other way in a fresh process, and `ACT-DV-edit-inside-the-function`
    missed on that turn alone. The seat reads these lines and the cassette
    key hashes them, so the order is sorted and not the set's."""
    turns = [("TOOL: ledger.log(about_ref='c_nowhere', about_table='criteria')\n"
              f"TOOL: problem.assert(id='i1', text='attempt {k}', kind='sideways')")
             for k in range(8)]
    backend = ScriptedBackend(turns + ["Done."])
    outcome = run_session(db, wake_vision_keeper(), backend=backend, pins=Pins(model="scripted"))
    assert outcome.committed, outcome.errors
    assert len(backend.calls) >= 4, (len(backend.calls), outcome.iterations,
                                     outcome.errors, backend.calls[-1][1][-2500:])
    told = backend.calls[3][1]
    first = told.find("NOTE ledger.log has been refused")
    second = told.find("NOTE problem.assert has been refused")
    assert first >= 0 and second >= 0, told[-1500:]
    assert first < second, "the notes come in name order, whatever the hash seed"


# --- the repeat memory (frame 43) -------------------------------------------
#
# `already_run` was a set built once a session and cleared by nothing, and the
# key went in before the call ran. Three faults came out of that, and each test
# below pins one of them. The fourth test pins the bound the repeats needed.


@pytest.fixture
def worktree(db, tmp_path):
    """A Developer with somewhere to write. No git: only the commit needs it."""
    root = tmp_path / "wt"
    (root / "src").mkdir(parents=True)
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('i1','delete an account','in_scope','approved',1,1)")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) "
               "VALUES ('b1','i1','running',?)", (str(root),))
    db.commit()
    return root


def wake_developer():
    return Wake(role="developer", kind="tick:batch_start", refs=("b1",))


def test_a_read_after_a_write_is_not_told_the_file_is_unchanged(db, worktree):
    """
    Night 86's s145 read `src/click/termui.py` at 1014 lines, wrote it,
    committed it, and was then answered "unchanged since you asked earlier this
    session". Its next read proves the file was 998 lines by then. The repeated
    read had already run, and the new content was thrown away on the way to the
    line that denied it.

    The answers are compared, so this needs no read-after-write case of its own.
    """
    (worktree / "src" / "acct.py").write_text("def delete(x):\n    return x\n")
    backend = ScriptedBackend([
        "TOOL: code.source(path='src/acct.py')",
        "TOOL: code.write(path='src/acct.py', text='def delete(x):"
        "\n    return \"tombstoned\"\n')",
        "TOOL: code.source(path='src/acct.py')",
        "Done.",
    ])
    outcome = run_session(db, wake_developer(), backend=backend,
                          pins=Pins(model="scripted"), batch_id="b1")

    assert outcome.committed, outcome.errors
    third = backend.calls[3][1]
    assert "tombstoned" in third, "the read came back with the file it had been shown before"
    assert "unchanged since you asked" not in third, "the session was told a lie"


def test_a_call_that_failed_and_then_worked_is_served_not_swallowed(db, worktree):
    """
    The key was registered before the call ran, so a call that failed and was
    sent again unchanged had its success answered with "unchanged since you
    asked earlier this session". The result was gone and no turn could get it
    back. No night recorded it; the adversary of 2026-09-19 found it by reading.

    The file arrives between the two turns and not from a tool, so this pins the
    registration alone and not the invalidation a write does.
    """
    seen = []

    def between_turns():
        seen.append(1)
        if len(seen) == 2:
            (worktree / "src" / "acct.py").write_text("VALUE = 1\n\ndef delete(x):\n    return x\n")

    line = "TOOL: code.write(path='src/acct.py', text='VALUE = 2\n', start=0, end=1)"
    backend = ScriptedBackend([line, line, "Done."])
    outcome = run_session(db, wake_developer(), backend=backend,
                          pins=Pins(model="scripted"), batch_id="b1",
                          on_completion=between_turns)

    assert outcome.committed, outcome.errors
    assert "does not exist" in backend.calls[1][1], "the first write was meant to fail"
    assert "unchanged since you asked" not in backend.calls[2][1], \
        "the retry succeeded and the session was told it had changed nothing"
    assert (worktree / "src" / "acct.py").read_text().startswith("VALUE = 2")


def test_a_repeated_write_is_the_same_act_and_is_answered_as_one(db, worktree):
    """
    A write is not indexed by the path it writes, so no invalidation reaches
    it. Indexed, a commit dropped the key of the write in its own reply and the
    next identical write paid full freight again: two full results where the
    old code had two lines (frame 43, pass 2). A commit changes what a read of
    a path returns. It does not change what the write that landed it returns.
    """
    (worktree / "src" / "acct.py").write_text("def delete(x):\n    return x\n")
    write = ("TOOL: code.write(path='src/acct.py', text='def delete(x):"
             "\n    return \"tombstoned\"\n')")
    backend = ScriptedBackend([write, f"Writing it again.\n{write}", "Done."])
    outcome = run_session(db, wake_developer(), backend=backend,
                          pins=Pins(model="scripted"), batch_id="b1")

    assert outcome.committed, outcome.errors
    assert "bytes" in backend.calls[1][1], "the first write was not served in full"
    assert "unchanged since you asked" in backend.calls[2][1], \
        "the second write paid full freight for an answer that had not changed"
    # Frame 93's sentence rides in the repeat line: the file holds the text.
    assert "already holds this text, so this write changed nothing" in backend.calls[2][1]


def test_two_spans_of_one_file_are_both_served_in_full(db, worktree):
    """
    The memory is keyed by the call and never by the path. Keyed by the path,
    every page after the first of a walked file would be answered "unchanged":
    667 disjoint reads across nights 85 and 86, against a false hold that costs
    three batches.
    """
    (worktree / "src" / "big.py").write_text(
        "".join(f"VALUE_{i} = {i}\n" for i in range(20)))
    backend = ScriptedBackend([
        "TOOL: code.source(path='src/big.py', start=0, end=5)",
        "TOOL: code.source(path='src/big.py', start=10, end=15)",
        "Done.",
    ])
    outcome = run_session(db, wake_developer(), backend=backend,
                          pins=Pins(model="scripted"), batch_id="b1")

    assert outcome.committed, outcome.errors
    assert "VALUE_0 = 0" in backend.calls[1][1]
    second = backend.calls[2][1]
    assert "VALUE_12 = 12" in second, "the second page was suppressed as a repeat"
    assert "unchanged since you asked" not in second


def test_the_third_identical_call_is_refused_and_the_session_runs_on(db):
    """
    Session s71 sent 331 calls in one reply on both nights and 327 came back as
    the repeat line, about 90,000 characters that became turn 2's whole prompt.
    The second asking is answered with the line. The third is refused, counted
    like any other refusal, and the session goes on.
    """
    for i in range(20):
        db.execute("INSERT INTO decisions (id, author, text) VALUES (?,?,?)",
                   (f"d{i:02d}", "vision_keeper", "scope " + "detail " * 20))

    # The prose varies and the call does not, which is the case the counter
    # exists for: a reply that repeats verbatim is already stopped a turn later.
    ask = "TOOL: decisions.search(query='scope')"
    backend = ScriptedBackend([f"Reading.\n{ask}", f"Again.\n{ask}",
                               f"Once more.\n{ask}", "Done."])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted"))

    assert outcome.committed, outcome.errors
    assert outcome.iterations == 4, "the refusal ended the session"
    assert "unchanged since you asked" in backend.calls[2][1], "the second asking is answered"
    assert "asked three times" in backend.calls[3][1], "the third asking was answered again"
    counted = [e for e in outcome.errors if "asked three times" in e]
    assert counted, \
        "the refusal is not counted, so a seat can repeat it while varying its prose"
    # `rota/testkit/fixtures.py:913` reads a dotted prefix as a call a guard
    # threw out and takes it off the forbidden-call score. This call ran, so
    # the name goes after the colon and the prefix carries no dot.
    assert "." not in counted[0].split(":", 1)[0], counted[0]


def test_an_action_is_held_behind_a_fresh_read_and_not_behind_a_repeat(db):
    """
    `already_run` drives the hold as well as the repeat line, and the hold keeps
    the semantics it has today: the call is the key. A read the session has
    already been answered asks nothing outstanding, so it holds nothing.
    """
    ask = ("TOOL: decisions.search(query='scope')\n"
           "TOOL: problem.assert(id='i9', text='and export them', kind='in_scope')")
    backend = ScriptedBackend([ask, ask, "Done."])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted"))

    assert outcome.committed, outcome.errors
    assert "NOT RUN" in backend.calls[1][1], "the action ran on a read the session had not seen"
    # The transcript carries the first hold forward, so the count is the test.
    assert backend.calls[2][1].count("NOT RUN") == 1, "the repeated read held the action again"
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 1, \
        "the write never landed"


# --- the per-turn total, and the cap on the latest exchange (frame 43) ------
#
# The caps were per result, per push and per page. Nothing added a turn up, and
# `_fit` was forbidden to touch the two blocks that are usually the problem.


def _wide_file(lines: int) -> str:
    """A file whose every line is wide enough that a 400-line read is over
    `SOURCE_CHARS`."""
    return "".join(f"VALUE_{i:04d} = {'x' * 48!r}\n" for i in range(lines))


def test_two_source_reads_in_one_turn_are_capped_as_a_turn(db, worktree):
    """
    `SOURCE_CHARS` is 14,000 and `_fit_budget(12288, 4000)` is 20,391, so two
    capped source reads in one reply are 28,000 characters: more than the whole
    session may hold, and nothing added them up.

    The first read keeps its own cap. The second takes what is left and says
    where it was cut, in the sentence the per-result cap already says.
    """
    from rota.core.runner import TURN_RESULT_CHARS

    (worktree / "src" / "big.py").write_text(_wide_file(900))
    reply = ("TOOL: code.source(path='src/big.py', start=0, end=400)\n"
             "TOOL: code.source(path='src/big.py', start=400, end=800)")
    backend = ScriptedBackend([reply, "Done."])
    outcome = run_session(db, wake_developer(), backend=backend,
                          pins=Pins(model="scripted"), batch_id="b1")

    assert outcome.committed, outcome.errors
    block = backend.calls[1][1].split(reply)[-1]      # this turn's results
    assert "VALUE_0000" in block, "the first read lost its head"
    assert "VALUE_0400" in block, "the second read was withheld whole"
    assert len(block) <= TURN_RESULT_CHARS, f"the turn was not summed: {len(block)}"
    # Both cuts say where they fell and which call fetches the rest, which is
    # the sentence the per-result cap already says.
    assert block.count("CUT the result") == 2, block.count("CUT the result")
    assert "start=216, end=400" in block, "the first cut names no continuation"
    assert "end=800" in block and "start=4" in block, \
        "the second cut names no continuation"


def test_a_result_with_no_room_left_is_named_rather_than_stubbed(db, worktree):
    """
    A result cut to nothing is worse than no result: it looks like a short
    answer, and the seat has no reason to ask again for something it does not
    know was cut. So the last call of a full turn is told it ran and told when
    to ask again.
    """
    (worktree / "src" / "big.py").write_text(_wide_file(1300))
    reply = "\n".join(
        f"TOOL: code.source(path='src/big.py', start={s}, end={s + 400})"
        for s in (0, 400, 800))
    backend = ScriptedBackend([reply, "Done."])
    outcome = run_session(db, wake_developer(), backend=backend,
                          pins=Pins(model="scripted"), batch_id="b1")

    assert outcome.committed, outcome.errors
    block = backend.calls[1][1].split(reply)[-1]
    assert "no room left" in block, "the third read vanished in silence"
    assert "Ask for it again in your next turn" in block, \
        "the seat is not told how to get it"
    assert "VALUE_0800" not in block, "the withheld result was served anyway"


def test_a_withheld_result_is_not_remembered_as_an_answer(db, worktree):
    """
    The withholding sentence is the same sentence for every call, so a key
    withheld twice compared equal to itself and the seat was told the answer
    was unchanged since it asked -- about a result it had never been shown.
    The same registration cleared `fresh_read`, so the hold stopped holding
    (the diff review of 34c3e72, F1).
    """
    (worktree / "src" / "big.py").write_text(_wide_file(1300))
    # The two reads move each turn, so each turn fills its own room and the
    # third call is withheld twice. A repeated read costs a line, which would
    # leave room the second time and hide the fault.
    def reply(at):
        return (f"TOOL: code.source(path='src/big.py', start={at}, end={at + 400})\n"
                f"TOOL: code.source(path='src/big.py', start={at + 400}, "
                f"end={at + 800})\n"
                f"TOOL: criteria.load(batch_id='b1')")

    backend = ScriptedBackend([reply(0), reply(100), "Done."])
    outcome = run_session(db, wake_developer(), backend=backend,
                          pins=Pins(model="scripted"), batch_id="b1")

    assert outcome.committed, outcome.errors
    first = backend.calls[1][1].split(reply(0))[-1]
    second = backend.calls[2][1].split(reply(100))[-1]
    assert "OK criteria.load -> ran, and this turn has no room left" in first, first[-400:]
    assert "OK criteria.load -> ran, and this turn has no room left" in second, \
        "the second withholding was answered as an unchanged result"
    assert "OK criteria.load -> unchanged" not in second, \
        "the seat was told a result it has never seen has not changed"


def test_a_read_after_a_write_still_holds_nothing(db, worktree):
    """
    `forget` discarded the key from `already_run` too, and `already_run` drives
    `fresh_read`. So the read of a written path became outstanding again and
    the next [read, write] batch held the write that used to run. A seat
    re-sending that batch oscillates: run, held, run, held (the diff review of
    34c3e72, F3).
    """
    (worktree / "src" / "acct.py").write_text("def delete(x):\n    return x\n")
    write = ("TOOL: code.write(path='src/acct.py', text='def delete(x):"
             "\n    return \"one\"\n')")
    again = ("TOOL: code.source(path='src/acct.py')\n"
             "TOOL: code.write(path='src/acct.py', text='def delete(x):"
             "\n    return \"two\"\n')")
    backend = ScriptedBackend([
        "TOOL: code.source(path='src/acct.py')", write, again, "Done."])
    outcome = run_session(db, wake_developer(), backend=backend,
                          pins=Pins(model="scripted"), batch_id="b1")

    assert outcome.committed, outcome.errors
    assert backend.calls[3][1].count("NOT RUN") == 0, \
        "the write was held behind a read the session had already been answered"
    assert '"two"' in (worktree / "src" / "acct.py").read_text(), \
        "the second write never ran"


def test_one_repeat_refusal_a_turn_however_many_copies_arrive(db):
    """
    The refusal is longer than the line it replaces: 149 characters against 90
    for `surveys.consult`. Session s71 sent 331 calls in one reply, so 327
    copies of it grew the prompt both repairs exist to shrink (the diff review
    of 34c3e72, F4). One sentence is the warning.
    """
    for i in range(20):
        db.execute("INSERT INTO decisions (id, author, text) VALUES (?,?,?)",
                   (f"d{i:02d}", "vision_keeper", "scope " + "detail " * 20))
    ask = "TOOL: decisions.search(query='scope')"
    backend = ScriptedBackend(["\n".join([ask] * 5), "Done."])
    outcome = run_session(db, wake_vision_keeper(), backend=backend,
                          pins=Pins(model="scripted"))

    assert outcome.committed, outcome.errors
    block = backend.calls[1][1]
    assert block.count("asked three times") == 1, block.count("asked three times")
    assert block.count("unchanged since you asked") == 1, "the second copy is the line"
    assert len([e for e in outcome.errors if "repeat refused" in e]) == 1, \
        outcome.errors


def test_fit_pays_for_the_notice_it_inserts(db):
    """
    The packing loop reserved nothing for its own eviction notice, so the
    transcript came back over the budget and `_cap_exchange` read the deficit
    as room it could lend. `_exchange_cut` promises a number a test can assert
    (the diff review of 34c3e72, F5).
    """
    from rota.core.runner import _fit

    # Sized so the packing fills its room exactly: the middle blocks divide it
    # with two characters to spare, and the latest exchange is small enough
    # that `_cap_exchange` lends its floor rather than cutting. That is the
    # shape the 116-character overrun was measured on.
    tight = (["W" * 500] + ["m" * 420 for _ in range(12)]
             + ["r" * 48, "r" * 48])
    fitted = _fit(list(tight), budget=4000)
    assert sum(len(b) + 2 for b in fitted) <= 4000, \
        f"over the budget by {sum(len(b) + 2 for b in fitted) - 4000}"
    assert any("dropped to fit" in b for b in fitted), "nothing was evicted"
    assert fitted[-2:] == tight[-2:], "the latest exchange was cut instead"

    for budget in (4000, 6000, 12000):
        blocks = ["WAKE " + "w" * 900] + [f"turn {i} " + "x" * 1200
                                          for i in range(1, 21)]
        fitted = _fit(blocks, budget=budget)
        assert sum(len(b) + 2 for b in fitted) <= budget, \
            f"over the budget at {budget}: {sum(len(b) + 2 for b in fitted)}"
        assert any("dropped to fit" in b for b in fitted), "nothing was evicted"
        assert fitted[-1] == blocks[-1], "the latest results went instead"


def test_a_probe_and_a_source_read_both_survive_one_turn(db, worktree):
    """
    The case the total is sized around. A probe of 60 rows renders about 2,200
    characters and a source span up to 14,000, so probe-then-read is about
    16,200 and has to fit whole. A cut span is re-asked and never read (night
    79), which is the failure a smaller total would cause.
    """
    (worktree / "src" / "mid.py").write_text(_wide_file(190))
    for i in range(60):
        db.execute("INSERT INTO code_index (grain, grain_kind, sym_kind, "
                   "line_start, line_end) VALUES (?, 'symbol', 'function', ?, ?)",
                   (f"src/pkg/mod_{i:03d}.py::render_{i:03d}", i, i + 9))
    db.commit()
    backend = ScriptedBackend([
        "TOOL: code.probe(pattern='render_')\n"
        "TOOL: code.source(path='src/mid.py', start=0, end=400)",
        "Done.",
    ])
    outcome = run_session(db, wake_developer(), backend=backend,
                          pins=Pins(model="scripted"), batch_id="b1")

    assert outcome.committed, outcome.errors
    block = backend.calls[1][1]
    assert "render_000" in block and "render_059" in block, "the probe was cut"
    assert "VALUE_0000" in block and "VALUE_0189" in block, "the read was cut"
    assert "CUT the result" not in block, "the turn cut what it had room for"
    assert "no room left" not in block, "a result was withheld with room to spare"


def test_a_latest_exchange_over_the_budget_is_cut_to_fit(db):
    """
    `_fit` kept the first block and the last two, capped the first, and neither
    capped the last two nor checked their sum -- so it could not get under the
    budget when the latest exchange was itself over it, and it did not try.
    Turn 2 is three blocks, which is where this bites.
    """
    from rota.core.runner import _fit

    fitted = _fit(["WAKE: survey src/billing", "reply " * 3000, "results " * 3000],
                  budget=12_000)

    assert sum(len(b) + 2 for b in fitted) <= 12_000, "still over the budget"
    assert len(fitted) == 3, "a block was dropped instead of cut"
    assert fitted[0] == "WAKE: survey src/billing", "the wake was touched"
    assert fitted[1].startswith("reply "), "the reply lost its head"
    assert fitted[2].startswith("results "), "the results lost their head"
    assert all("CUT this exchange" in b for b in fitted[1:]), \
        "the exchange was cut in silence"


def test_the_exchange_cap_leaves_a_short_block_whole(db):
    """Half each, and a block under its half lends the rest to the other. A
    seat's one-line reply must not cost its results half the window."""
    from rota.core.runner import _fit

    fitted = _fit(["WAKE", "ok", "results " * 3000], budget=12_000)

    assert fitted[1] == "ok", "the short reply was cut for no gain"
    assert len(fitted[2]) > 11_000, "the results did not take the room the reply left"
    assert sum(len(b) + 2 for b in fitted) <= 12_000


def test_one_and_two_block_transcripts_keep_their_shape(db):
    """
    The guard stays at three. Below it `head = transcript[:1]` and `tail =
    transcript[-2:]` overlap, so the wake would be emitted twice and `dropped`
    would go negative (the design review of 2026-09-19, section 9.2).
    """
    from rota.core.runner import _fit

    one = _fit(["WAKE " + "x" * 50_000], budget=12_000)
    assert len(one) == 1 and one[0].startswith("WAKE ")
    assert one[0].count("WAKE ") == 1, "the wake was emitted twice"

    two = _fit(["WAKE " + "x" * 50_000, "turn 1"], budget=12_000)
    assert len(two) == 2 and two[1] == "turn 1", "the reply was cut at two blocks"
    assert two[0].count("WAKE ") == 1, "the wake was emitted twice"
