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


def test_failed_session_never_happened_and_raises_attempts(db):
    """A session that dies mid-flight commits nothing and leaves its trigger open."""
    class Exploding:
        name = "exploding"

        def complete(self, system, user, pins):
            raise RuntimeError("model evicted")

    outcome = run_session(db, wake_vision_keeper(), backend=Exploding(), pins=Pins(model="x"))

    assert not outcome.committed
    assert db.execute("SELECT COUNT(*) n FROM sessions").fetchone()["n"] == 0
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
    # Against the rendered length, not the JSON-encoded one. A dict carrying
    # long text now renders as text -- `code.area` and `code.source` handed
    # source to the model as an escaped JSON string, every newline a literal
    # `\n` -- so the total the notice reports is the size of what the
    # model would actually have been shown.
    shown = len(full) + len(chr(10) + "[body]" + chr(10))
    assert str(RESULT_CHARS) in text and str(shown) in text, \
        "the notice must say how much was withheld, not merely that some was"
    assert "Ask for the next range" in text, "no way offered to get the rest"


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
    db.execute("INSERT INTO items (id, text, kind, provenance) "
               "VALUES ('i_existing','prior scope','in_scope','decided')")
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
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('t1','account','a customer record','observed')")
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
    db.execute("INSERT INTO items (id, text, kind, provenance) VALUES (?,?,?,?)",
               ("i01", "people can close their account", "in_scope", "decided"))

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
    assert "TRUNCATED" in user, "it was cut without saying so"


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

    assert sum(len(b) + 2 for b in fitted) <= 12_000 * 1.5, "still overflowing"
    assert fitted[0].startswith("WAKE "), "the wake lost its head, not its tail"
    assert "did not fit" in fitted[0], "the wake was cut silently"
    assert fitted[-1] == "turn 3", "the latest exchange was dropped instead"


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
    assert "TRUNCATED" in runner._render(big)
    assert "TRUNCATED" not in runner._render(big, runner.PUSH_CHARS)
    assert "TRUNCATED" in runner._render({"source": "x" * (runner.PUSH_CHARS + 10)},
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
