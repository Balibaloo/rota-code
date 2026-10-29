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
    # Frame 303: a deliver has the principal's message as its cause, as on
    # a night. A statement ref would join the refs of every report.
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                 "VALUES ('m0','t1','principal','liaison','converse',0)")
    conn.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
                 "verb, seq) VALUES ('m1','m0','t1','liaison','vision_keeper',"
                 "'deliver',1)")
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


def test_a_stream_stopped_at_an_invented_result_says_where_and_runs_the_call(db, worktree):
    """
    Frame 232: the stream ends at the head of the first invented result line.
    The account keeps "wrote its own tool results" for the count across
    nights, and one more line says where the stream stopped. The call before
    the head runs, as rule 1 of frame 77 runs it on the full text.
    """
    from rota.llm.llm import Completion

    class Stopped(ScriptedBackend):
        def complete(self, system, user, pins, tools=None):
            c = super().complete(system, user, pins, tools)
            if len(self.calls) == 1:
                return Completion(text=c.text, pins=pins, backend=self.name,
                                  raw={"done_reason": "invented_result"})
            return c

    (worktree / "src" / "acct.py").write_text("def delete(x):\n    return x\n")
    backend = Stopped([
        "TOOL: code.source(path='src/acct.py')\n\nOK code.source ->",
        "Done.",
    ])
    outcome = run_session(db, wake_developer(), backend=backend,
                          pins=Pins(model="scripted"), batch_id="b1")

    assert "wrote its own tool results" in outcome.errors
    assert ('the stream stopped at the invented result "OK code.source ->" on '
            'line 3 of the reply, so nothing after it was generated') in outcome.errors
    after = backend.calls[1][1]
    assert "OK code.source -> path: src/acct.py" in after, \
        "the call before the invented head did not run"


def test_a_cut_after_a_whole_write_never_says_nothing_was_written(db, worktree):
    """
    Frame 121's diff review, finding 2. A reply whose last call is a whole
    `code.write` and whose prose after it reaches the output budget: the
    write lands, and the line says that the cut broke no call. "Nothing was
    written" was false there.
    """
    backend = _CutFirst([
        "TOOL: code.write(path='src/acct.py', text='VALUE = 1\n')\n"
        "Now I explain the change at length, because the account",
        "Done.",
    ])
    run_session(db, wake_developer(), backend=backend,
                pins=Pins(model="scripted"), batch_id="b1")
    after = backend.calls[1][1]
    assert _CUT_AFTER in after, after[-1500:]
    assert "nothing was written" not in after
    assert "OK code.write" in after, after[-1500:]
    assert (worktree / "src" / "acct.py").read_text() == "VALUE = 1\n"


class _CutFirst(ScriptedBackend):
    """The first reply stops at the output budget."""

    def complete(self, system, user, pins, tools=None):
        from rota.llm.llm import Completion
        c = super().complete(system, user, pins, tools)
        if len(self.calls) == 1:
            return Completion(text=c.text, pins=pins, backend=self.name,
                              raw={"done_reason": "length"})
        return c


_CUT_HEAD = "ERROR reply cut: your reply was cut at the output budget before it ended. "
_CUT_AFTER = (_CUT_HEAD + "The cut fell after the last call, so it broke no "
              "call. The results of the calls that ran follow. Send less")
_CUT_INSIDE = (_CUT_HEAD + "The cut fell inside the last call, so that call "
               "did not run. The results of the calls before it that ran "
               "follow. Send less")
_SRC = "TOOL: code.source(path='src/acct.py')"
_WRITE = "TOOL: code.write(path='src/acct.py', text='VALUE = 1')"


@pytest.mark.parametrize("reply,line,shows,hides", [
    # Case A: a whole call with a parse error, then prose, then the cut. The
    # cut broke no call, and the parse error keeps its own line.
    (_SRC[:-1] + ", 5)\nNow I explain the plan at length, because the acc",
     _CUT_AFTER, ["ERROR TOOL: code.source(path='src/acct.py', 5): could not parse"],
     []),
    # Case B, night 113's s32 seq 10 and night 119's s157 seq 8: an
    # invented result drops the call after it, which gets a NOT RUN line.
    (_SRC + "\nOK code.source -> VALUE = 0\n" + _WRITE + "\nThen I explain at len",
     _CUT_AFTER, ["OK code.source ->", "NOT RUN, because you wrote a tool result"],
     []),
    # Case C: the write is held behind the read in the same reply.
    (_SRC + "\n" + _WRITE + "\nThen I explain at len",
     _CUT_AFTER, ["OK code.source ->", "NOT RUN, because you wrote them before"],
     []),
    # Case D1: a fragment with a name that is no function of the role.
    (_SRC + "\nTOOL: code.wr", _CUT_INSIDE, ["OK code.source ->"], ["code.wr'"]),
    # Night 117's s150 seq 14: a call before the cut call is dropped by an
    # invented result, and the last call is cut inside its argument list.
    (_SRC + "\nOK code.source -> VALUE = 0\n" + _WRITE + "\n"
     "TOOL: code.write(path='src/acct.py', text='def f():\n    return",
     _CUT_INSIDE, ["OK code.source ->", "NOT RUN, because you wrote a tool result"],
     ["unterminated argument list"]),
], ids=["A parse error then prose", "B invented result", "C held write",
        "D1 cut name", "night 117 s150 inside with NOT RUN"])
def test_the_cut_line_is_true_beside_held_and_broken_calls(db, worktree, reply,
                                                          line, shows, hides):
    """
    Frame 121's second diff review. The line promises results only for the
    calls that ran, because the runner holds or drops some: 11 of 39 night
    events stood beside a NOT RUN line. A parse error is a cut only when the
    call runs to the end of the reply.
    """
    (worktree / "src" / "acct.py").write_text("VALUE = 0\n")
    backend = _CutFirst([reply, "Done."])
    run_session(db, wake_developer(), backend=backend,
                pins=Pins(model="scripted"), batch_id="b1")
    after = backend.calls[1][1]
    tail = after[after.rfind("ERROR reply cut"):]
    assert line in tail, tail[:1500]
    for text in shows:
        assert text in tail, (text, tail[:1500])
    for text in hides:
        assert text not in tail, (text, tail[:1500])
    assert "nothing was written" not in tail


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
    fitted, _ = _fit(blocks, _paired(blocks), budget=12000)

    assert fitted[0] == wake, "the wake was evicted; the role no longer knows its job"
    assert fitted[-2:] == blocks[-2:], "the latest exchange was dropped"
    assert any("dropped to fit" in b for b in fitted), "the loss is silent"
    assert sum(len(b) + 2 for b in fitted) <= 12000 + len(fitted[1])


def test_a_transcript_that_fits_is_left_exactly_alone(db):
    from rota.core.runner import _fit

    blocks = ["wake", "a", "b", "c"]
    assert _fit(blocks, _paired(blocks), budget=100_000) == (
        blocks, _paired(blocks))


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
    assert "the window took it each time" in served[3], \
        f"the refusal does not name the window: {served[3][:200]}"
    # `decisions.search` takes no span, so the refusal names no span.
    assert ("ERROR decisions.search: served three times this session, and "
            "the window took it each time; not served again. Your prompt does "
            "not hold this result, and the window cannot hold it. Act without "
            "it, or finish.") in served[3], served[3][:300]
    assert "narrower span" not in served[3], \
        "the refusal names a span the call does not take"
    assert "returned earlier" not in served[3], \
        "the refusal points at an answer the window took"
    assert any("repeat refused" in e for e in outcome.errors), \
        "the fourth asking was never refused"


@pytest.mark.parametrize("bound", ["a narrower span", "a smaller limit"])
def test_the_serve_cap_names_a_bound_only_to_a_call_that_takes_one(db, monkeypatch, bound):
    """
    Frame 121's interview, D, and its diff review, finding 5. Night 119's
    s260 was told to ask `tests.load` for a narrower span, and `tests.load`
    takes `batch_id` only. The refusal reads the signature: `code.source`
    takes `start` and `end`, `code.concordance` and `code.prose` take
    `limit`, and `tests.load` and `decisions.search` take neither. The
    `code.source` wording stays byte for byte.
    """
    from rota.core import runner
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = build("developer", db, batch_id=None, mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    assert runner._bound_of(sb, "code.source") == "a narrower span"
    assert runner._bound_of(sb, "code.write") == "a narrower span"
    assert runner._bound_of(sb, "tests.load") is None
    assert runner._bound_of(sb, "criteria.load") is None
    concordance = runner._bound_of(build("terminologist", db), "code.concordance")
    assert concordance == "a smaller limit"
    assert runner._bound_of(build("vision_keeper", db), "code.prose") == "a smaller limit"

    # The session below asks `decisions.search`. Its signature is pinned
    # to the bound here, so each branch runs on the same eviction shape.
    monkeypatch.setattr(runner, "_bound_of", lambda sb, name: bound)
    _seed_decisions(db)
    ask = "TOOL: decisions.search(query='scope')"
    backend = ScriptedBackend(_evicting_repeats(ask, askings=4))
    run_session(db, wake_vision_keeper(), backend=backend,
                pins=Pins(model="scripted", temperature=0.0, num_ctx=512))
    refused = backend.calls[5][1].split("\n\n")[-1]
    line = ("ERROR decisions.search: served three times this session, and "
            "the window took it each time; not served again. Ask "
            f"decisions.search for {bound}, or finish without it.")
    assert line in refused, refused[:300]


def _third_asking_in(db, num_ctx: int) -> ScriptedBackend:
    """
    Night 126's s159, turns 19 and 20, in a scripted session (frame 169).

    The seat asks one key three times, so the third asking meets the repeat
    refusal. The same reply reads a second, different result. In a window of
    8,192 tokens the next fit drops the block of the first answer. In 12,288
    the first answer stands. Turn 4 asks once more.
    """
    _seed_decisions(db)
    for i in range(60):
        db.execute("INSERT INTO decisions (id, author, text) VALUES (?,?,?)",
                   (f"b{i:02d}", "vision_keeper", "billing " + "ledger " * 20))
    ask = "TOOL: decisions.search(query='scope')"
    backend = ScriptedBackend([
        ask, f"Again.\n{ask}",
        f"Once more.\n{ask}\nTOOL: decisions.search(query='billing')",
        f"Last time.\n{ask}", "Done."])
    run_session(db, wake_vision_keeper(), backend=backend,
                pins=Pins(model="scripted", temperature=0.0, num_ctx=num_ctx))
    return backend


def test_the_repeat_refusal_says_the_window_dropped_the_answer(db):
    """
    Frame 169. The repeat refusal said `The answer is in this prompt`. The
    claim was true in the prompt the runner tested, and the fit for the next
    turn then dropped the answer. Night 126's s159 read the claim at turn 20,
    and the span 688 to 705 was not in that prompt. 2 of 6 such refusal lines
    on night 126 were false.

    The runner checks the claim after the fit. Where the answer is gone, the
    line says so, and it gives the step that rule 2 of frame 77 makes true.
    """
    from rota.core.runner import _EVICTED_PHRASE

    backend = _third_asking_in(db, 8192)
    read = backend.calls[3][1]                   # turn 4, the refusal's reader
    assert _EVICTED_PHRASE in read, \
        "nothing was evicted, so this shape proves nothing"
    line = [ln for ln in read.splitlines() if "asked three times" in ln]
    assert line == [
        "ERROR decisions.search: asked three times this session and the "
        "answer has not changed; not answered again. The window dropped the "
        "answer after this line, so ask once more and it is served again."
    ], line
    assert "The answer is in this prompt" not in read, \
        "the refusal points at an answer the window took"
    # The sentence is a promise, and turn 4's asking is served again.
    served = backend.calls[4][1].split("\n\n")[-1]
    assert (f"OK decisions.search -> the earlier answer was {_EVICTED_PHRASE}"
            in served), served[:300]


def test_the_repeat_refusal_keeps_its_pointer_where_the_answer_stands(db):
    """
    Frame 169's other half. Frame 119 removed the pointer everywhere on
    2026-10-04, and night 115's s33 to s35 then repeated ten calls, so
    4d5757db put the pointer back. Where the answer stands, the line is true
    and stays word for word.
    """
    from rota.core.runner import _EVICTED_PHRASE

    backend = _third_asking_in(db, 12288)
    read = backend.calls[3][1]
    assert _EVICTED_PHRASE not in read, "the answer was evicted"
    line = [ln for ln in read.splitlines() if "asked three times" in ln]
    assert line == [
        "ERROR decisions.search: asked three times this session and the "
        "answer has not changed; not answered again. The answer is in this "
        "prompt."
    ], line
    assert "The window dropped the answer" not in read


def test_the_repeat_refusal_is_checked_after_every_fit(db):
    """
    Frame 169's review, finding 1 and probe F. The runner checked a refusal
    after one fit only. A refusal from turn N still said `The answer is in
    this prompt.` at turn N+2, where that fit had dropped the answer.

    Turn 3 meets the refusal, and the fit for turn 4 keeps the first answer.
    Turn 4 reads a second large result and does not ask again. The fit for
    turn 5 then drops the first answer, and the line says so.
    """
    from rota.core.runner import _EVICTED_PHRASE

    _seed_decisions(db)
    for i in range(60):
        db.execute("INSERT INTO decisions (id, author, text) VALUES (?,?,?)",
                   (f"b{i:02d}", "vision_keeper", "billing " + "ledger " * 20))
    ask = "TOOL: decisions.search(query='scope')"
    backend = ScriptedBackend([
        ask, f"Again.\n{ask}",
        f"Once more.\n{ask}\nTOOL: decisions.search(query='billing')",
        "Read more.\nTOOL: decisions.search(query='ledger')", "Done."])
    run_session(db, wake_vision_keeper(), backend=backend,
                pins=Pins(model="scripted", temperature=0.0, num_ctx=11264))

    kept = backend.calls[3][1]                   # turn 4, the fit at N+1
    assert _EVICTED_PHRASE not in kept, "the fit at N+1 dropped the answer"
    assert ("not answered again. The answer is in this prompt."
            in kept), "the refusal never landed, so this shape proves nothing"
    read = backend.calls[4][1]                   # turn 5, the fit at N+2
    assert _EVICTED_PHRASE in read, \
        "nothing was evicted at N+2, so this shape proves nothing"
    line = [ln for ln in read.splitlines() if "asked three times" in ln]
    assert line == [
        "ERROR decisions.search: asked three times this session and the "
        "answer has not changed; not answered again. The window dropped the "
        "answer after this line, so ask once more and it is served again."
    ], line
    assert "The answer is in this prompt" not in read, \
        "the refusal points at an answer the window took"


def test_every_copy_of_a_repeated_refusal_line_is_corrected(db):
    """
    Frame 169's second look, probe B, on parent commit ef96f550. The seat
    asks one key four times, so turns 4 and 5 read the same refusal line.
    The runner keeps one pointer for the two copies. The fit for turn 6
    drops the answer, and `_repoint` replaced the newest copy only. The
    older copy kept `The answer is in this prompt.` beside the corrected one.
    """
    from rota.core.runner import _EVICTED_PHRASE

    _seed_decisions(db)
    for i in range(60):
        db.execute("INSERT INTO decisions (id, author, text) VALUES (?,?,?)",
                   (f"b{i:02d}", "vision_keeper", "billing " + "ledger " * 20))
    ask = "TOOL: decisions.search(query='scope')"
    backend = ScriptedBackend([
        ask, f"Again.\n{ask}", f"Once more.\n{ask}",
        f"Four.\n{ask}\nTOOL: decisions.search(query='billing')",
        "Read more.\nTOOL: decisions.search(query='ledger')", "Done.",
        "Done."])
    run_session(db, wake_vision_keeper(), backend=backend,
                pins=Pins(model="scripted", temperature=0.0, num_ctx=11264))

    read = backend.calls[5][1]                   # turn 6, after the drop
    assert _EVICTED_PHRASE in read, \
        "nothing was evicted, so this shape proves nothing"
    lines = [ln for ln in read.splitlines() if "asked three times" in ln]
    assert len(lines) == 2, "the two copies of the line are not both there"
    dropped = ("ERROR decisions.search: asked three times this session and "
               "the answer has not changed; not answered again. The window "
               "dropped the answer after this line, so ask once more and it "
               "is served again.")
    assert lines == [dropped, dropped], lines
    assert "The answer is in this prompt" not in read, \
        "the older copy points at an answer the window took"


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


def test_the_critic_wake_keeps_the_criteria_and_tests_in_front_of_the_diff(db):
    """
    Frame 101. The cut keeps the front of the wake, and the push rendered
    `code.read` first. A long diff then pushed the criteria and the tests
    behind the cut (frame 97's review of `ff0f692`, probe p3).
    """
    from types import SimpleNamespace

    from rota.core import runner
    from rota.core.sandbox import build as build_sandbox

    diff = "d" * (runner.PUSH_CHARS + 5000)
    results = {"code.read": diff, "criteria.load": [{"id": "c1"}],
               "tests.load": [{"id": "t1"}]}

    class Stub:
        # The push reads the retired note through the sandbox's context
        # (frame 306, W-C1). No batch means no retired criteria.
        ctx = SimpleNamespace(conn=db, batch_id=None)

        def functions(self):
            return ["code.read", "criteria.load", "tests.load"]

        def call(self, name, **kw):
            return results[name]

    graph = SimpleNamespace(of_type=lambda _t: [
        SimpleNamespace(s="critic", t=k.split(".")[0], v=k.split(".")[1])
        for k in results])
    pushed = runner.push_working_set("critic", Stub(), None, g=graph)
    assert list(pushed) == ["criteria.load", "tests.load", "code.read"]

    sb = build_sandbox("vision_keeper", db)
    _, user = runner.build_prompt("vision_keeper", sb, wake_vision_keeper(),
                                  pushed, "brief")
    at = {k: user.index(f"[{k}]") for k in pushed}
    assert at["criteria.load"] < at["code.read"]
    assert at["tests.load"] < at["code.read"]
    kept = runner._render_cut(user, len(user) // 2)
    assert "[criteria.load]" in kept and "[tests.load]" in kept


def test_a_wake_too_big_for_the_window_is_cut_rather_than_protected(db):
    """
    `_fit` kept `transcript[0]` whole unconditionally — and the wake is where
    the pushed working set lives, so the one block that could overflow the
    window on its own was the one block never trimmed. Protecting it is right
    until it is the problem.
    """
    from rota.core.runner import _fit

    blocks = ["WAKE " + "x" * 50_000, "turn 1", "turn 2", "turn 3"]
    fitted, _ = _fit(blocks, _paired(blocks), budget=12_000)

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
        fitted, _ = _fit(list(blocks), _paired(blocks), budget=12_000)
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


# --- a reply that lands no ruling (frame 267) -------------------------------
#
# Night 151's s336 woke on m178, the principal's reply to the page m177. It
# met this refusal three times, the repeat door ended it, and the commit
# marked m178 answered. m177 stayed open and nothing woke on it.

S336_REFUSAL = ("line 11: 'ask' is a question back, and a question is its own "
                "call: rulings.rule(ask=\"<one sentence about line 11>\") with "
                "no rulings.")
# s336's turn 1 completion on night 151, verbatim. Turns 2 and 3 repeat it.
S336_TURN_1 = (
    'TOOL: rulings.rule(rulings={"1": "approve", "2": "contest", "3": "contest", '
    '"4": "contest", "5": "contest", "6": "approve", "7": "contest", "8": '
    '"approve", "9": "approve", "10": "approve", "11": "ask", "12": "approve"}, '
    'words="Lines 4 and 5 are wrong because their checks still pass a plain '
    'string to the decorator, when they should run a small command with the '
    'flag on and ask for its version. Lines 2 and 3 never turn the flag on, '
    'and line 3 also needs to check that the Python version stays hidden when '
    "the flag is off. Line 7 should say the version comes from the "
    "interpreter's version info as major, minor and micro and not the full "
    "version string, and line 11 is about the JSON change, so it doesn't "
    'belong on this page.")')
# Night 151's m178, his reply, from `.rota/clickI_night151.db` with `mode=ro`.
# s336's words copy it whole, and the door refuses words outside his reply.
S336_M178 = S336_TURN_1.split('words="', 1)[1][:-len('")')]


def _page_and_reply(db, attempts):
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES "
               "('m177','t9','liaison','principal','present','[]',177,'open')")
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_text, seq, status, attempts) VALUES "
               "('m178','m177','t9','principal','liaison','converse',"
               "'1 ok, 11 is not about this page',178,'open',?)", (attempts,))
    db.commit()


def _commit_reply_session(db, sid, **kw):
    # No `errors=` here: the field is new, and the tests of the unchanged
    # paths must run at the commit before it (review 1, finding 5).
    from rota.core.db import SessionResult, session_commit

    kw.setdefault("refusals", [("rulings.rule", S336_REFUSAL, "ValueError")])
    session_commit(db, SessionResult(
        session_id=sid, role="liaison", trigger_msg="m178",
        wake_kind="message", wake_detail="converse", **kw))


# s226's account on night 151, verbatim: one refusal the seat fixed at turn
# 2, then four parse errors on an unbalanced quote, then the repeat door.
S226_REFUSAL = ("lines 1, 5 have no ruling. Every line of the page takes one: "
                "the ask closes when the ruling lands. A line the reply does "
                "not contest is approve")
S226_PARSE = ("unterminated argument list: a quote inside a quoted argument "
              "ended the string early, or a bracket is unbalanced. Source has "
              "quotes of its own: put it between triple quotes, "
              "text='''...''', with the lines as they are, no escaping")


def _status(db, mid):
    return dict(db.execute("SELECT status, unresolved_note FROM messages "
                           "WHERE id = ?", (mid,)).fetchone())


def test_a_reply_that_lands_no_ruling_stays_open_with_the_refusal(db):
    """The first session on the reply lands nothing, so the reply stays open
    and keeps the last refusal for the next wake (frame 267, 5.1)."""
    _page_and_reply(db, attempts=1)
    _commit_reply_session(db, "s336")
    reply = _status(db, "m178")
    assert reply["status"] == "open", reply
    assert reply["unresolved_note"] == "rulings.rule: " + S336_REFUSAL
    assert _status(db, "m177") == {"status": "open", "unresolved_note": None}


def test_the_second_wake_on_a_missed_reply_says_the_last_refusal(db):
    """The same prompt at temperature zero gives the same calls, so the
    second wake carries the reason line, and only that wake does."""
    from rota.core.runner import _missed_reply_line

    _page_and_reply(db, attempts=1)
    wake = Wake(role="liaison", kind="message", message_id="m178", detail="converse")
    assert _missed_reply_line(db, wake) == ""
    _commit_reply_session(db, "s336")
    assert _missed_reply_line(db, wake) == (
        "A session on this reply ended with no ruling. Its last refusal or "
        "error: rulings.rule: " + S336_REFUSAL)
    assert _missed_reply_line(db, wake_vision_keeper()) == ""


def test_the_note_names_the_newest_fault_not_a_fixed_refusal(db):
    """Night 151's m108: s226 fixed its refusal at turn 2 and failed four
    turns on a quote. The note names the parse error, and never the repeat
    door's end line (frame 267, review 1, finding 1)."""
    _page_and_reply(db, attempts=1)
    _commit_reply_session(
        db, "s226", refusals=[("rulings.rule", S226_REFUSAL, "ValueError")],
        errors=["rulings.rule: " + S226_REFUSAL] + [S226_PARSE] * 4
        + ["repeated its previous turn verbatim twice; ended"])
    assert _status(db, "m178") == {"status": "open", "unresolved_note": S226_PARSE}


def test_the_note_skips_the_refusal_doors_end_line(db):
    """The refusal door ends a session with its own end line. The line says
    how the session ended, so the note is the refusal before it (frame 267,
    review 2, finding 1)."""
    _page_and_reply(db, attempts=1)
    _commit_reply_session(
        db, "s341", errors=["rulings.rule: " + S336_REFUSAL] * 4
        + ["rulings.rule was refused the same way in four turns; the session "
           "ended on it"])
    assert _status(db, "m178") == {"status": "open",
                                   "unresolved_note": "rulings.rule: " + S336_REFUSAL}


def test_a_page_comes_back_once_and_a_later_miss_closes_the_reply(db):
    """A page goes back to the principal once per ask. A miss on a reply to
    a returned page closes the reply and leaves the note as it was, so no
    driver answers the page again (review 1, finding 6)."""
    _page_and_reply(db, attempts=1)
    db.execute("UPDATE messages SET unresolved_note = 'm150: rulings.rule: "
               "line 3: no' WHERE id = 'm177'")
    db.commit()
    _commit_reply_session(db, "s340")
    assert _status(db, "m178") == {"status": "answered", "unresolved_note": None}
    assert _status(db, "m177") == {"status": "open",
                                   "unresolved_note": "m150: rulings.rule: line 3: no"}


def test_the_landing_wake_shows_the_page_without_the_returned_line(db):
    """The returned line is the principal's. The Liaison's landing wake is
    the seat's view of the page, so the line stays out of it."""
    from rota.core.runner import resolve_inbound
    from rota.roles.principal import pending_asks

    _page_and_reply(db, attempts=0)
    db.execute("UPDATE messages SET unresolved_note = 'm150: rulings.rule: "
               "line 3: no' WHERE id = 'm177'")
    db.commit()
    wake = Wake(role="liaison", kind="message", message_id="m178", detail="converse")
    page = resolve_inbound(db, wake)["landing"]["page"]
    assert "did not reach the team" not in page
    assert pending_asks(db)[0].rendered.startswith(
        "Your last answer to this page did not reach the team.")


def test_a_second_reply_that_lands_no_ruling_returns_the_page(db):
    """The second session closes the reply and puts the reason on the page.
    The page shows one line about it, with no id and no tool name (5.2)."""
    from rota.roles.principal import pending_asks

    _page_and_reply(db, attempts=2)
    _commit_reply_session(db, "s337")
    assert _status(db, "m178")["status"] == "answered"
    page = _status(db, "m177")
    assert page["status"] == "open"
    assert page["unresolved_note"] == "m178: rulings.rule: " + S336_REFUSAL
    rendered = {a.message_id: a.rendered for a in pending_asks(db)}["m177"]
    first = rendered.splitlines()[0]
    # The number comes from his reply, not the refusal. The reply names no
    # "line N", so the line names none (frame 305).
    assert first == (
        "Your last answer to this page did not reach the team. The team could "
        "not turn your words into a ruling. Answer the page "
        "again, and say for each line you want changed what to do with it.")
    for word in ("m178", "rulings", "refus", "lead"):
        assert word not in first


def test_s336s_end_through_the_runner_keeps_then_returns_the_page(db):
    """The replay of s336's end: one refused call three times, the repeat
    door, a barren commit. The first run keeps the reply open, and the
    second run's wake says why and returns the page (frame 267, 5.4). The
    completion is s336's turn 1 on night 151, verbatim, on a page of twelve
    lines as m177 had (review 1, finding 4)."""
    for k in range(1, 13):
        db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                   "version) VALUES (?,?,'in_scope','pending',0,1)",
                   (f"i{k}", f"the change does thing {k}"))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES "
               "('m177','t9','liaison','principal','present',?,177,'open')",
               (json.dumps([f"i{k}" for k in range(1, 13)]),))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_text, seq, status) VALUES "
               "('m178','m177','t9','principal','liaison','converse',"
               "?,178,'open')", (S336_M178,))
    db.commit()
    call = S336_TURN_1
    wake = Wake(role="liaison", kind="message", message_id="m178", detail="converse")
    shown = []
    for _ in range(2):
        backend = ScriptedBackend([call] * 5)
        outcome = run_session(db, wake, backend=backend, pins=Pins(model="scripted"))
        assert outcome.committed, outcome.errors
        assert outcome.errors[-1] == "repeated its previous turn verbatim twice; ended"
        shown.append(backend.calls[0][1])
        if len(shown) == 1:
            assert _status(db, "m178")["status"] == "open"
            assert _status(db, "m178")["unresolved_note"] == "rulings.rule: " + S336_REFUSAL
    assert "ended with no ruling" not in shown[0]
    assert ("A session on this reply ended with no ruling. Its last refusal or "
            "error: rulings.rule: " + S336_REFUSAL) in shown[1]
    assert _status(db, "m178")["status"] == "answered"
    assert _status(db, "m177") == {"status": "open",
                                   "unresolved_note": "m178: rulings.rule: " + S336_REFUSAL}


def test_a_reply_that_stages_a_ruling_is_answered_as_before(db):
    from rota.core.db import Write

    _page_and_reply(db, attempts=1)
    _commit_reply_session(db, "s338", writes=[Write(
        "rulings", "r_1", {"ask_id": "m177", "reply_id": "m178",
                           "per_item": "{}", "words": "ok"})])
    assert _status(db, "m178") == {"status": "answered", "unresolved_note": None}
    assert _status(db, "m177")["unresolved_note"] is None


def test_a_reply_answered_with_an_ask_back_is_answered_as_before(db):
    from rota.core.db import OutboundMessage

    _page_and_reply(db, attempts=1)
    _commit_reply_session(db, "s339", messages=[OutboundMessage(
        id="m179", to_role="principal", verb="converse",
        body_text="What should line 11 say?", cause_id="m178")])
    assert _status(db, "m178") == {"status": "answered", "unresolved_note": None}
    assert _status(db, "m177")["unresolved_note"] is None


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


def _third_asking(db) -> str:
    """The prompt after the third identical `decisions.search`."""
    for i in range(20):
        db.execute("INSERT INTO decisions (id, author, text) VALUES (?,?,?)",
                   (f"d{i:02d}", "vision_keeper", "scope " + "detail " * 20))
    ask = "TOOL: decisions.search(query='scope')"
    backend = ScriptedBackend([f"Reading.\n{ask}", f"Again.\n{ask}",
                               f"Once more.\n{ask}", "Done."])
    run_session(db, wake_vision_keeper(), backend=backend,
                pins=Pins(model="scripted"))
    return backend.calls[3][1]


@pytest.mark.parametrize("cap", [3, 1])
def test_the_refusal_keeps_the_wording_of_6ba9fcc(db, monkeypatch, cap):
    """
    Frame 119, pass 3. "If the window dropped it, ask once more and it is
    served again." invited a repeat: night 115, s33 to s35, repeated ten
    calls where night 113 attested. The line keeps the wording of 6ba9fcc,
    under SERVE_CAP and at it.
    """
    from rota.core import runner

    monkeypatch.setattr(runner, "SERVE_CAP", cap)
    prompt = _third_asking(db)
    line = ("ERROR decisions.search: asked three times this session and the "
            "answer has not changed; not answered again. The answer is in "
            "this prompt.")
    assert line in prompt, prompt[-400:]
    assert "served again" not in prompt


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
    # Results blocks only in the middle, so no stub frees room and the
    # packing still fills it exactly (frame 100).
    fitted, _ = _fit(list(tight), ["wake"] + ["results"] * 12
                     + ["reply", "results"], budget=4000)
    assert sum(len(b) + 2 for b in fitted) <= 4000, \
        f"over the budget by {sum(len(b) + 2 for b in fitted) - 4000}"
    assert any("dropped to fit" in b for b in fitted), "nothing was evicted"
    assert fitted[-2:] == tight[-2:], "the latest exchange was cut instead"

    for budget in (4000, 6000, 12000):
        blocks = ["WAKE " + "w" * 900] + [f"turn {i} " + "x" * 1200
                                          for i in range(1, 21)]
        fitted, _ = _fit(blocks, _paired(blocks), budget=budget)
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

    blocks = ["WAKE: survey src/billing", "reply " * 3000, "results " * 3000]
    fitted, _ = _fit(blocks, _paired(blocks), budget=12_000)

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

    blocks = ["WAKE", "ok", "results " * 3000]
    fitted, _ = _fit(blocks, _paired(blocks), budget=12_000)

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

    one, _ = _fit(["WAKE " + "x" * 50_000], ["wake"], budget=12_000)
    assert len(one) == 1 and one[0].startswith("WAKE ")
    assert one[0].count("WAKE ") == 1, "the wake was emitted twice"

    two, _ = _fit(["WAKE " + "x" * 50_000, "turn 1"], ["wake", "reply"],
                  budget=12_000)
    assert len(two) == 2 and two[1] == "turn 1", "the reply was cut at two blocks"
    assert two[0].count("WAKE ") == 1, "the wake was emitted twice"


def _paired(blocks: list[str]) -> list[str]:
    """The kinds of a transcript the runner built as reply and results pairs."""
    return ["wake"] + ["reply" if i % 2 else "results"
                       for i in range(1, len(blocks))]


def _source(path: str, start: int, end: int, size: int, fill: str = "s",
            prefix: str = "", cut_at: int | None = None) -> str:
    """A `code.source` result line the size of `size`, as the runner writes it."""
    head = (f"OK code.source -> {prefix}path: {path}, start: {start}, "
            f"end: {end}, lines: 688\n\n[text]\n")
    tail = ("" if cut_at is None else
            f"\nCUT the result: 9,000 of 12,000 characters are not shown. "
            f"The cut fell at line {cut_at}: code.source(path='{path}', "
            f"start={cut_at}, end={end}) returns the rest.")
    return head + fill * (size - len(head) - len(tail)) + tail


def _held(blocks: list[str]) -> int:
    return sum(len(b) + 2 for b in blocks)


def test_old_replies_become_stubs_before_a_read_goes(db):
    """
    Frame 100, night 99, s132. Age alone dropped the reads and kept the
    replies: results of 2,186 to 8,642 characters went, and replies of 7,373
    to 21,121 characters stayed. The seat read span 346-390 eight times.

    The s132 shape: a wake, a 2,000 character source result, and three 8,000
    character replies. The old replies become stubs, and the read survives.
    """
    from rota.core.runner import _fit

    call_1 = "TOOL: code.source(path='src/click/utils.py', start=346, end=390)"
    call_2 = "TOOL: code.probe(pattern='echo')"
    read = _source("src/click/utils.py", 346, 390, 2000)
    blocks = ["WAKE " + "w" * 995,
              call_1 + "\n" + "plan one. " * 793,
              read,
              call_2 + "\n" + "plan two. " * 797,
              "OK code.probe -> []",
              "TOOL: code.write(path='src/click/utils.py')\n" + "plan. " * 1320,
              "OK code.write -> written"]
    kinds = _paired(blocks)
    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget=14_000)

    assert read in fitted, "the read went, and the old replies stayed"
    assert fitted[1] == call_1 and fitted[3] == call_2, \
        f"the old replies are not stubs of their calls: {fitted[1][:80]}"
    assert fitted[-2:] == blocks[-2:], "the latest exchange was touched"
    assert fitted_kinds == kinds, "a stub changed the kinds"
    assert not any("dropped to fit" in b for b in fitted), \
        "a stub drops no block, so no notice is owed"
    assert _held(fitted) <= 14_000


def test_after_an_eviction_a_results_block_is_not_taken_for_a_reply(db):
    """
    Frame 100, night 99, s132, turns 9, 10, 11 and 13. After the first
    eviction a results block follows the notice, so a kind read from the
    position is false. The kinds list states the kind.

    Wake, notice, an older 2,000 character source result, a newer 8,000
    character reply. The reply becomes a stub, and the result survives.
    """
    from rota.core.runner import _dropped_note, _fit

    read = _source("src/click/utils.py", 251, 346, 2000)
    reply = ("TOOL: code.source(path='src/click/utils.py', start=346, end=390)"
             "\n" + "plan. " * 1323)
    blocks = ["WAKE " + "w" * 995, _dropped_note(2), read, reply,
              "TOOL: code.write(path='src/click/utils.py')",
              "OK code.write -> written"]
    kinds = ["wake", "notice", "results", "reply", "reply", "results"]
    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget=10_000)

    assert read in fitted, "the read went, and the newer reply stayed"
    assert reply not in fitted, "the old reply was kept whole"
    assert fitted[1] == _dropped_note(2), "the notice changed with no drop"
    assert fitted_kinds == kinds
    assert _held(fitted) <= 10_000


def test_a_result_invented_in_a_reply_is_not_a_read(db):
    """
    Frame 100, night 99, s132: turns 5, 8, 19, 21 and 23 wrote results of
    their own into the reply. A span in a reply never ran, so it covers no
    read. And a tail too large for the window is cut as before frame 100.
    """
    from rota.core.runner import _fit

    read = _source("a.py", 10, 20, 2000, fill="r")
    probe = "OK code.probe -> " + "p" * 1983
    invented = ("TOOL: code.source(path='a.py', start=0, end=100)\n"
                "OK code.source -> path: a.py, start: 0, end: 100, "
                "lines: 100\n\n[text]\n")
    tail = invented + "i" * (6000 - len(invented))
    blocks = ["WAKE " + "w" * 995,
              "TOOL: code.probe(pattern='x')", probe,
              "TOOL: code.source(path='a.py', start=10, end=20)\n" + "t" * 7950,
              read, tail, "NOT RUN, because you wrote a tool result."]
    kinds = _paired(blocks)
    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget=10_000)

    assert read in fitted, "a span the reply invented covered a real read"
    assert probe not in fitted, "the older results block stayed"
    # The probe's results and the stub of its reply go together.
    assert "[2 earlier exchange(s) dropped to fit the window." in fitted[1]
    assert len(fitted_kinds) == len(fitted)
    assert _held(fitted) <= 10_000

    huge = invented + "i" * (22_000 - len(invented))
    blocks = blocks[:-2] + [huge, blocks[-1]]
    fitted, fitted_kinds = _fit(list(blocks), _paired(blocks), budget=10_000)
    assert "CUT this exchange" in fitted[-2], "the tail was not cut"
    assert fitted[0] == blocks[0], "the wake was touched"
    assert len(fitted_kinds) == len(fitted)
    assert _held(fitted) <= 10_000, f"over the budget: {_held(fitted)}"


def test_a_span_a_newer_read_holds_goes_first(db):
    """
    Frame 100, night 99, s132, turn 19. A tier that only keeps the newest
    read of a path lets distinct spans go, and turn 20 then re-read 251-346.
    An older copy of a span goes before any distinct span.

    A newer read covers an older span only up to the line where it was cut.
    s132's read of 0-688 at turn 12 was cut at line 457.
    """
    from rota.core.runner import _fit

    def shape(other: str, older: str, newer: str) -> list[str]:
        return ["WAKE " + "w" * 995,
                "TOOL: code.source(path='b.py')", other,
                "TOOL: code.source(path='a.py')", older,
                "TOOL: code.source(path='a.py')", newer,
                "TOOL: code.write(path='a.py')", "OK code.write -> written"]

    other = _source("b.py", 0, 50, 2000, fill="b")
    older = _source("a.py", 346, 390, 2000, fill="o")
    again = _source("a.py", 346, 390, 2000, fill="n", prefix=(
        "the earlier answer was dropped to fit the window, so this prompt "
        "does not hold it. code.source ran again: "))
    fitted, _ = _fit(shape(other, older, again), _paired(shape(other, older, again)),
                     budget=6000)
    assert older not in fitted, "the older copy of the span stayed"
    assert other in fitted, "a distinct span went before a copy"
    assert _held(fitted) <= 6000

    probe = "OK code.probe -> " + "p" * 1983
    whole = _source("a.py", 0, 688, 2000, fill="n")
    blocks = shape(probe, older, whole)
    fitted, _ = _fit(blocks, _paired(blocks), budget=6000)
    assert older not in fitted and probe in fitted, \
        "a span inside a newer whole read stayed"

    cut = _source("a.py", 0, 688, 2000, fill="n", cut_at=300)
    blocks = shape(probe, older, cut)
    fitted, _ = _fit(blocks, _paired(blocks), budget=6000)
    assert older in fitted and probe not in fitted, \
        "a read cut at line 300 was taken to hold lines 346 to 390"


def test_the_kinds_stay_aligned_with_the_blocks(db):
    """
    Frame 100. `_fit` returns the transcript and its kinds, and the runner
    stores both, so a stub or a drop must keep them in step. Checked with
    and without a notice, and with an earlier notice that the new one folds.
    """
    from rota.core.runner import _EVICTED_PHRASE, _dropped_note, _fit

    def check(blocks: list[str], kinds: list[str], budget: int) -> list[str]:
        fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget=budget)
        assert len(fitted_kinds) == len(fitted)
        assert fitted_kinds[0] == "wake" and fitted_kinds[-2:] == kinds[-2:]
        for block, kind in zip(fitted, fitted_kinds):
            if kind == "notice":
                assert _EVICTED_PHRASE in block, block[:80]
            elif block in blocks:
                assert kinds[blocks.index(block)] == kind, block[:80]
            else:
                assert kind == "reply", f"a {kind} block changed: {block[:80]}"
        return fitted

    blocks = ["WAKE " + "w" * 995] + [
        f"TOOL: code.probe(pattern='{i}')\n" + "r" * 3000 if i % 2 else
        f"OK code.probe -> {i} " + "x" * 3000 for i in range(1, 11)]
    kinds = _paired(blocks)

    fitted = check(blocks, kinds, budget=20_000)
    assert not any(_EVICTED_PHRASE in b for b in fitted), "stubs alone fit"

    fitted = check(blocks, kinds, budget=9_000)
    assert _EVICTED_PHRASE in fitted[1], "nothing was dropped"

    noted = [blocks[0], _dropped_note(3)] + blocks[2:]
    noted_kinds = ["wake", "notice"] + kinds[2:]
    fitted = check(noted, noted_kinds, budget=9_000)
    assert sum(_EVICTED_PHRASE in b for b in fitted) == 1, "two notices"

    with pytest.raises(ValueError):
        _fit(blocks, kinds[:-1], budget=9_000)


def test_the_fit_keeps_its_budget_promise(db):
    """
    Frame 100. The tiers change what goes, not how much. The output fits the
    budget for the s132 sizes: a 4,743 character wake, replies to 21,121
    characters, and source results to 14,179, in a 26,309 budget (night 99).
    """
    from rota.core.runner import _fit

    sizes = [21_121, 14_179, 8_173, 2_186, 7_373, 8_642, 3_000, 4_105,
             12_000, 2_811, 8_000, 12_409]
    for budget in (8_000, 12_000, 26_309):
        for turns in range(2, len(sizes) + 1, 2):
            blocks = ["WAKE " + "w" * 4738]
            for i, size in enumerate(sizes[:turns]):
                blocks.append(
                    f"TOOL: code.source(path='a.py', start={i}, end={i + 9})\n"
                    + "r" * size if i % 2 == 0 else
                    _source("a.py", i - 1, i + 8, size))
            fitted, kinds = _fit(blocks, _paired(blocks), budget=budget)
            assert _held(fitted) <= budget, \
                f"{turns} blocks over {budget} by {_held(fitted) - budget}"
            assert fitted[0] == blocks[0] and len(kinds) == len(fitted)


def test_a_read_cut_before_its_text_covers_no_span(db):
    """
    The diff review of frame 100's pass 1, finding 1. `_render` cuts before
    the `[text]` marker when a long `defs` head takes the cap. The head still
    names 346-390, but the block holds no source, so it covers nothing. Else
    tier 2 drops an older real read of that span as a copy.
    """
    from rota.core.runner import _render, _source_spans

    result = {"path": "src/click/utils.py", "start": 346, "end": 390,
              "text": "line\n" * 44, "lines": 688,
              "defs": {f"fn_{i:02d}": [i * 10, i * 10 + 9] for i in range(40)}}
    block = "OK code.source -> " + _render(result, 600)
    assert "[text]" not in block, "the shape needs a cut before the text"
    assert "start: 346, end: 390" in block, "the head no longer names the span"
    assert _source_spans(block) == [], "a head with no source covered a span"
    whole = "OK code.source -> " + _render(result, 6000)
    assert _source_spans(whole) == [("src/click/utils.py", 346, 390)]


def test_a_stub_keeps_calls_the_parser_finds_inside_a_line(db):
    """
    The diff review of frame 100's pass 1, finding 2. The parser finds
    `TOOL:` anywhere in a line, so a call in a list item or in backticks ran.
    The stub keeps it, and does not fall back to the empty stub.
    """
    from rota.core.runner import _stub

    reply = ("My plan:\n"
             "1. TOOL: code.source(path='a.py', start=346, end=390) first\n"
             "2. `TOOL: code.probe(pattern='echo')` then\n"
             + "I will read both. " * 200)
    assert _stub(reply) == ("TOOL: code.source(path='a.py', start=346, end=390)"
                            "\nTOOL: code.probe(pattern='echo')")


def test_a_dropped_result_takes_the_stub_of_its_turn(db):
    """
    The diff review of frame 100's pass 1, finding 3. A results block went
    before the stub of its own reply, so the seat saw `TOOL: code.write(...)`
    with no refusal beside it, and could believe the write landed. The pair
    goes together, N counts both, and the kinds stay aligned.
    """
    from rota.core.runner import _fit

    write = "TOOL: code.write(path='src/click/utils.py', text='x')"
    refused = "ERROR code.write: the write drops 8 names. " + "e" * 1957
    read = _source("src/click/utils.py", 346, 390, 2000)
    blocks = ["WAKE " + "w" * 995,
              write + "\n" + "plan one. " * 793, refused,
              "TOOL: code.source(path='src/click/utils.py', start=346, end=390)"
              "\n" + "plan two. " * 797, read,
              "TOOL: code.probe(pattern='echo')\n" + "plan. " * 1320,
              "OK code.probe -> []"]
    kinds = _paired(blocks)
    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget=11_500)

    assert refused not in fitted, "the shape needs the refusal to go"
    assert not any(b.startswith(write) for b in fitted), \
        "the stub of the write stayed after its refusal went"
    assert "[2 earlier exchange(s) dropped to fit the window." in fitted[1]
    assert read in fitted
    assert fitted_kinds == ["wake", "notice", "reply", "results", "reply",
                            "results"]
    assert _held(fitted) <= 11_500


def test_each_distinct_span_of_one_file_is_pinned(db):
    """
    The diff review of frame 100's pass 1, finding 4. A pin per path let one
    file's distinct spans go by age. Night 99, s132, turn 8, under 26,309:
    spans 390-450 and 450-688 went, and turns 16 to 18 read them again.

    Four distinct spans of one file and a probe. The probe goes first. When
    one more must go, the oldest pinned span goes, and the other three stay.
    """
    from rota.core.runner import _fit

    spans = [_source("src/click/utils.py", s, e, 2000, fill=f)
             for (s, e), f in zip([(251, 346), (346, 390), (390, 450),
                                   (450, 688)], "abcd")]
    probe = "OK code.probe -> " + "p" * 1983
    reads = spans[:3] + [probe, spans[3]]
    blocks = ["WAKE " + "w" * 995]
    for i, block in enumerate(reads):
        blocks += [f"TOOL: code.source(path='src/click/utils.py', at={i})", block]
    blocks += ["TOOL: code.write(path='src/click/utils.py')",
               "OK code.write -> written"]
    kinds = _paired(blocks)

    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget=10_000)
    assert probe not in fitted, "the probe stayed and a span went"
    assert all(s in fitted for s in spans), "a distinct span went by age"
    assert len(fitted_kinds) == len(fitted)

    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget=8_000)
    assert probe not in fitted and spans[0] not in fitted, \
        "the oldest pinned span did not go first"
    assert all(s in fitted for s in spans[1:]), "a newer span went"
    assert _held(fitted) <= 8_000 and len(fitted_kinds) == len(fitted)


_S132_BUDGET = 26_309


def _s132_turn_13(reply_chars: int, results: str) -> list[str]:
    """
    Night 99, s132, turn 13: a wake of about 13,500 characters, four reads of
    distinct spans in the middle with their replies, and the latest exchange.
    """
    blocks = ["WAKE " + "w" * 13_495]
    for (s, e), fill in zip([(251, 346), (346, 390), (390, 450), (450, 688)],
                            "abcd"):
        blocks += [f"TOOL: code.source(path='src/click/utils.py', start={s}, "
                   f"end={e})\n" + "plan. " * 90,
                   _source("src/click/utils.py", s, e, 3000, fill=fill)]
    call = "TOOL: code.write(path='src/click/utils.py')\n"
    blocks += [call + "r" * (reply_chars - len(call)), results]
    return blocks


def _parent_fit(rev: str = "032c71c"):
    """
    `_fit` as it was at `rev`. The default is 032c71c, before the tail cap of
    frame 108. Frame 119 compares against 6ba9fcc, before the wake's share
    yields.
    """
    return _parent_runner(rev)._fit


def _parent_runner(rev: str):
    """The runner module as it was at `rev`, or a skip without git history."""
    import importlib.util
    import subprocess
    import sys
    import tempfile
    from pathlib import Path

    try:
        text = subprocess.run(["git", "show", f"{rev}:rota/core/runner.py"],
                              capture_output=True, check=True,
                              cwd=Path(__file__).resolve().parents[2]).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip(f"the parent commit {rev} is not in this checkout")
    path = Path(tempfile.mkdtemp()) / f"runner_{rev}.py"
    path.write_bytes(text)
    name = f"rota.core._runner_{rev}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_a_tail_larger_than_the_budget_leaves_a_middle_read(db):
    """
    Frame 108. Night 99, s132, turn 13: a 30,894-character reply against a
    26,309 budget left negative room, and every middle block went. Turns 15
    to 18 read four spans again. The reply is cut before the tiers run, so
    the packing keeps a read.
    """
    from rota.core.runner import _fit

    results = "OK code.write -> " + "o" * 1983
    blocks = _s132_turn_13(30_894, results)
    kinds = _paired(blocks)
    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget=_S132_BUDGET)

    third = _S132_BUDGET // 3
    reply_room = max(third, _S132_BUDGET - (len(blocks[0]) + 2) - third) \
        - 4 - len(results)
    assert any(b in fitted for b in blocks[2:-2:2]), "every middle read went"
    assert len(fitted[-2]) <= reply_room, "the reply is over its room"
    assert "CUT this exchange" in fitted[-2], "the reply was cut in silence"
    assert fitted[-1] == results, "the cap touched the results"
    assert _held(fitted) <= _S132_BUDGET
    assert len(fitted_kinds) == len(fitted)
    assert fitted_kinds[0] == "wake" and fitted_kinds[-2:] == kinds[-2:]


def test_a_tail_that_leaves_a_middle_block_room_packs_as_before(db):
    """
    Frame 108, revision 2. The cap fires only when no middle block can fit
    beside the tail. Any other transcript packs to the bytes of the parent.
    The second shape leaves no block room, but a cut of its reply frees no
    block, so the reply stays whole.
    """
    from rota.core.runner import _fit

    parent = _parent_fit()
    s132 = _s132_turn_13(2000, "OK code.write -> " + "o" * 1983)
    trimmed = (["WAKE: you are surveying src/billing"]
               + [f"turn {i} " + "x" * 4000 for i in range(1, 7)])
    pinned = ["WAKE " + "w" * 995]
    for i in range(5):
        pinned += [f"TOOL: code.source(path='src/click/utils.py', at={i})",
                   _source("src/click/utils.py", 100 * i, 100 * i + 50, 2000)]
    for blocks, budget in ((s132, _S132_BUDGET), (trimmed, 12_000),
                           (pinned, 8_000)):
        kinds = _paired(blocks)
        assert _fit(list(blocks), list(kinds), budget) == \
            parent(list(blocks), list(kinds), budget), blocks[0][:40]


def test_a_short_reply_keeps_its_length_beside_large_results(db):
    """
    Frame 108, revision 2. The cap cuts the reply only. The runner sizes the
    results block, and its cut names the call that fetches the rest. Here
    the cap fires, the reply is under the floor, and both blocks stay whole.
    """
    from rota.core.runner import _fit

    reply = "TOOL: code.source(path='src/click/utils.py', start=1, end=688)"
    results = _source("src/click/utils.py", 1, 688, 12_400)
    blocks = _s132_turn_13(2000, results)
    blocks[-2] = reply
    kinds = _paired(blocks)
    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget=_S132_BUDGET)

    assert fitted[-2:] == [reply, results], "the cap cut the latest exchange"
    assert _held(fitted) <= _S132_BUDGET
    assert len(fitted_kinds) == len(fitted)


def test_the_cap_sizes_the_middle_by_a_results_unit(db):
    """
    The diff review of frame 108's pass 1, finding 1. The trigger read the
    smallest middle block, and a 62-character call line passed for room. The
    packing never keeps a reply alone, so no read fit and the cap stayed
    off. The unit is a results block plus the stub of its reply.
    """
    from rota.core.runner import _dropped_note, _fit

    blocks = ["WAKE " + "w" * 1995]
    for i in range(4):
        call = f"TOOL: code.source(path='src/click/utils.py', start={i}, end=9)"
        blocks += [call.ljust(60), _source("src/click/utils.py", i, 9, 1071)]
    tail_results = "OK code.write -> " + "o" * 983
    call = "TOOL: code.write(path='src/click/utils.py')\n"
    blocks += [call + "r" * (4700 - len(call)), tail_results]
    kinds = _paired(blocks)
    budget = 8_000

    # The shape: the old unit fits beside the uncut tail, and a results unit
    # does not.
    room = (budget - _held([blocks[0]] + blocks[-2:])
            - len(_dropped_note(len(blocks))) - 2)
    assert 62 <= room < 1071 + 2 + 60 + 2, room

    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget=budget)
    assert "CUT this exchange" in fitted[-2], "the cap did not fire"
    assert any(b in fitted for b in blocks[2:-2:2]), "every middle read went"
    assert fitted[-1] == tail_results
    assert _held(fitted) <= budget and len(fitted_kinds) == len(fitted)


def test_a_cut_reply_keeps_its_call_in_its_stub(db):
    """
    The diff review of frame 108's pass 1, finding 2. `_exchange_cut` keeps
    a prefix, so a call after the prose fell outside it. The reply then
    stubbed to no call on a later turn. The cut reply starts with its stub.
    """
    from rota.core.runner import _fit, _stub

    call = "TOOL: code.write(path='src/click/utils.py', text='x')"
    blocks = _s132_turn_13(2000, "OK code.write -> " + "o" * 1983)
    blocks[-2] = "I reason about the fix. " * 1285 + "\n" + call
    kinds = _paired(blocks)
    fitted, _ = _fit(list(blocks), list(kinds), budget=_S132_BUDGET)

    assert "CUT this exchange" in fitted[-2], "the cap did not fire"
    assert fitted[-2].startswith(call + "\n"), fitted[-2][:120]
    assert _stub(fitted[-2]) == call, "the stub of the cut reply lost its call"


def test_a_middle_that_fits_once_stubbed_leaves_the_tail_whole(db):
    """
    The diff review of frame 108's pass 2, finding 1. The trigger charged
    the notice, but the packing charges it only when a block drops. Here
    tier 1 stubs the old reply, the middle fits whole, and no block drops.
    The tail stays whole, and the output is the parent's bytes.
    """
    from rota.core.runner import _dropped_note, _fit

    call = "TOOL: code.source(path='src/click/utils.py', start=1, end=9)"
    tail_call = "TOOL: code.write(path='src/click/utils.py')"
    blocks = ["WAKE " + "w" * 995,
              call + "\n" + "plan. " * 400,
              _source("src/click/utils.py", 1, 9, 1759),
              "r" * (3927 - len(tail_call) - 1) + "\n" + tail_call,
              "OK code.write -> " + "o" * 483]
    kinds = _paired(blocks)
    fixed = _held([blocks[0]] + blocks[-2:])
    unit = len(blocks[2]) + 2 + len(call) + 2
    budget = fixed + unit + 50
    # The shape: the old trigger fired, because it charged the notice.
    assert budget - fixed - len(_dropped_note(len(blocks))) - 2 < unit

    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget=budget)
    assert fitted[-2] == blocks[-2], "the cap cut a tail that left room"
    assert (fitted, fitted_kinds) == _parent_fit()(
        list(blocks), list(kinds), budget)


def test_a_reply_shorter_than_its_stub_counts_at_its_own_length(db):
    """
    The diff review of frame 108's pass 2, finding 2. Tier 1 puts a stub in
    place of a reply only when the stub is shorter. An "ok" reply stays "ok",
    so its unit is the read plus two characters. Counted as a stub, the unit
    did not fit, and the cap cut a tail that left a unit room.
    """
    from rota.core.runner import _dropped_note, _fit

    tail_call = "TOOL: code.write(path='src/click/utils.py')"
    blocks = ["WAKE " + "w" * 995]
    for i in range(3):
        blocks += ["ok", _source("src/click/utils.py", i, 9, 1000,
                                 fill="abc"[i])]
    blocks += ["r" * (5000 - len(tail_call) - 1) + "\n" + tail_call,
               "OK code.write -> " + "o" * 183]
    kinds = _paired(blocks)
    fixed = _held([blocks[0]] + blocks[-2:])
    note_room = len(_dropped_note(len(blocks))) + 2
    budget = fixed + note_room + 1016
    # The shape: the true unit fits, and a unit with an "ok" stub does not.
    assert 1000 + 2 + 2 + 2 <= 1016 < 1000 + 2 + 31 + 2

    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget=budget)
    assert fitted[-2] == blocks[-2], "the cap cut a tail that left room"
    assert (fitted, fitted_kinds) == _parent_fit()(
        list(blocks), list(kinds), budget)


def test_a_reply_that_starts_with_its_call_shows_the_call_once(db):
    """
    The diff review of frame 108's pass 2, finding 3. A reply whose first
    line is its call already starts with its stub. A stub prefix showed the
    call twice. The reply takes the plain cut.
    """
    from rota.core.runner import _fit

    call = "TOOL: code.write(path='src/click/utils.py', text='x')"
    blocks = _s132_turn_13(2000, "OK code.write -> " + "o" * 1983)
    blocks[-2] = call + "\n" + "I reason about the fix. " * 1285
    kinds = _paired(blocks)
    fitted, _ = _fit(list(blocks), list(kinds), budget=_S132_BUDGET)

    assert "CUT this exchange" in fitted[-2], "the cap did not fire"
    assert fitted[-2].startswith(call + "\n"), fitted[-2][:120]
    assert fitted[-2].count(call) == 1, "the call shows twice"


def test_a_cut_that_keeps_no_read_leaves_the_tail_whole(db):
    """
    The diff review of frame 108's pass 3, finding 1. The cut landed when
    the room passed the smallest unit. The packing drops oldest first, so
    the smallest unit went, the next did not fit, and the middle emptied
    with the reply cut. The cut now lands only when a trial pack keeps a
    read. No cut keeps one here, so the output is the parent's bytes.
    """
    from rota.core.runner import _fit

    def call(i: int) -> str:
        return f"TOOL: code.source(path='src/click/u.py', start={i}, end=9)"

    blocks = ["WAKE " + "w" * 5000,
              call(1) + "\n" + "plan. " * 50,
              _source("src/click/u.py", 1, 9, 298, fill="a"),
              call(2) + "\n" + "plan. " * 50,
              _source("src/click/u.py", 2, 9, 2998, fill="b"),
              call(3) + "\n" + "plan. " * 1222,
              _source("src/click/u.py", 3, 9, 4639, fill="c")]
    tail_call = "TOOL: code.write(path='src/click/u.py')"
    blocks += ["r" * (30_894 - len(tail_call) - 1) + "\n" + tail_call,
               "OK code.write -> " + "o" * 1983]
    kinds = _paired(blocks)
    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget=12_000)

    assert not any(b in fitted for b in blocks[2:-2:2]), \
        "the shape needs every middle read to go"
    assert (fitted, fitted_kinds) == _parent_fit()(
        list(blocks), list(kinds), 12_000), "a cut landed and kept no read"


def test_a_call_inside_the_kept_prefix_shows_once(db):
    """
    The diff review of frame 108's pass 3, finding 2. A call in the middle
    of the prose fell inside the kept prefix, and the stub prefix repeated
    it. The plain cut serves when its own stub still lists every call.
    """
    from rota.core.runner import _fit, _stub

    call = "TOOL: code.write(path='src/click/utils.py', text='x')"
    blocks = _s132_turn_13(2000, "OK code.write -> " + "o" * 1983)
    blocks[-2] = ("I reason about the fix. " * 100 + "\n" + call + "\n"
                  + "I check the result. " * 1400)
    kinds = _paired(blocks)
    fitted, _ = _fit(list(blocks), list(kinds), budget=_S132_BUDGET)

    assert "CUT this exchange" in fitted[-2], "the cap did not fire"
    assert fitted[-2].count(call) == 1, "the call shows twice"
    assert _stub(fitted[-2]) == call, "the stub of the cut reply lost its call"


# Night 113, s153: the budget, and the wake before the window cut it.
_S153_BUDGET = 27_096
_S153_WAKE = 47_547
# The commit before frame 119, where the wake took two thirds on every turn.
_F119_PARENT = "6ba9fcc"


def _s153_turn_16() -> list[str]:
    """
    Night 113, s153, turn 16: the uncut wake, two older reads, the newest
    middle read of utils.py 670-710 at about 1,937 characters with its stub,
    and the latest exchange of a 10,928 reply and 8,566 of results.
    """
    blocks = ["WAKE " + "w" * (_S153_WAKE - 5)]
    for (s, e), size, fill in (((1, 20), 1200, "a"), ((1, 50), 2400, "b"),
                               ((670, 710), 1860, "c")):
        blocks += [f"TOOL: code.source(path='src/click/utils.py', start={s}, "
                   f"end={e})\n" + "plan. " * 300,
                   _source("src/click/utils.py", s, e, size, fill=fill)]
    call = "TOOL: batches.expect(batch_id='bg_1')\n"
    blocks += [call + "r" * (10_928 - len(call)),
               "OK batches.expect -> " + "e" * (8_566 - 21)]
    return blocks


def test_a_wake_yields_half_the_budget_to_keep_a_middle_read(db):
    """
    Frame 119. Night 113, s153, turn 16: the wake at two thirds and the tail
    at a third left the middle no room, so the read of utils.py 670-710 went
    and the seat read it again. With a middle read, the wake takes half the
    budget, and the cap keeps the read beside the tail.
    """
    from rota.core.runner import _fit, _stub

    blocks = _s153_turn_16()
    kinds = _paired(blocks)
    newest = blocks[-3]
    # The shape: the middle unit is about 1,937, as on night 113.
    assert 1_900 <= len(newest) + 2 + len(_stub(blocks[-4])) + 2 <= 1_950

    fitted, fitted_kinds = _fit(list(blocks), list(kinds), _S153_BUDGET)
    assert newest in fitted, "the newest middle read went"
    assert len(fitted[0]) <= _S153_BUDGET // 2 + 200, "the wake kept two thirds"
    assert "CUT your wake" in fitted[0], "the wake was cut in silence"
    assert _held(fitted) <= _S153_BUDGET
    assert len(fitted_kinds) == len(fitted)

    parent, parent_kinds = _parent_fit(_F119_PARENT)(
        list(blocks), list(kinds), _S153_BUDGET)
    assert newest not in parent, "the shape does not fail on the parent"


def test_a_first_turn_wake_keeps_two_thirds(db):
    """
    Frame 119. A transcript with no middle read keeps the wake's two thirds,
    the case of b8c18fe. A first turn and a transcript of three blocks pack
    to the bytes of the parent.
    """
    from rota.core.runner import _fit

    parent = _parent_fit(_F119_PARENT)
    wake = "WAKE " + "w" * (_S153_WAKE - 5)
    shapes = ([wake],
              [wake, "TOOL: code.source(path='src/click/utils.py', start=1, "
                     "end=50)\n" + "plan. " * 300,
               _source("src/click/utils.py", 1, 50, 2400)])
    for blocks in shapes:
        kinds = _paired(blocks)
        fitted, fitted_kinds = _fit(list(blocks), list(kinds), _S153_BUDGET)
        assert len(fitted[0]) > _S153_BUDGET * 2 // 3, "the wake lost its share"
        assert (fitted, fitted_kinds) == parent(
            list(blocks), list(kinds), _S153_BUDGET), len(blocks)
        assert _held(fitted) <= _S153_BUDGET


def test_a_wake_under_half_packs_as_before(db):
    """
    Frame 119. A later turn whose wake is under half the budget takes no
    cut, so the share changes nothing and the bytes are the parent's.
    """
    from rota.core.runner import _fit

    parent = _parent_fit(_F119_PARENT)
    blocks = _s153_turn_16()
    blocks[0] = "WAKE " + "w" * 12_000
    kinds = _paired(blocks)
    fitted, fitted_kinds = _fit(list(blocks), list(kinds), _S153_BUDGET)
    assert fitted[0] == blocks[0]
    assert (fitted, fitted_kinds) == parent(
        list(blocks), list(kinds), _S153_BUDGET)
    assert _held(fitted) <= _S153_BUDGET


def test_a_wake_cut_again_names_the_uncut_total(db):
    """
    Frame 119's diff review, finding 2. The runner stores the cut wake, so a
    second cut printed `4,634 of 18,182` where the wake was 47,547. The note
    keeps the uncut total. A cut wake inside its room comes back as it is.
    """
    from rota.core.runner import _fit

    blocks = _s153_turn_16()
    first, _ = _fit([blocks[0]], ["wake"], _S153_BUDGET)
    keep = _S153_BUDGET * 2 // 3
    assert f"CUT your wake: {_S153_WAKE - keep:,} of {_S153_WAKE:,} " in first[0]
    again, _ = _fit([first[0]], ["wake"], _S153_BUDGET)
    assert again == first, "a cut wake inside its room was cut again"

    blocks[0] = first[0]
    fitted, _ = _fit(list(blocks), _paired(blocks), _S153_BUDGET)
    half = _S153_BUDGET // 2
    assert fitted[0].startswith(blocks[0][:half] + "\nCUT your wake: "
                                f"{_S153_WAKE - half:,} of {_S153_WAKE:,} ")
    assert fitted[0].count("CUT your wake") == 1
    assert _held(fitted) <= _S153_BUDGET


def test_a_reply_with_no_results_is_no_middle_unit(db):
    """
    Frame 119's diff review, finding 3. A reply stub with no results after
    it passed for the smallest unit, so the cap stayed off and the middle
    kept stubs and no read. Units are results blocks only.
    """
    from rota.core.runner import _dropped_note, _fit

    read_call = "TOOL: code.source(path='src/click/utils.py', start=1, end=9)"
    read = _source("src/click/utils.py", 1, 9, 1500)
    probe = "TOOL: code.probe(pattern='echo')"
    tail_call = "TOOL: code.write(path='src/click/utils.py')"
    blocks = ["WAKE " + "w" * 995,
              read_call + "\n" + "plan. " * 100, read,
              probe + "\n" + "plan. " * 100,
              tail_call + "\n" + "r" * (5000 - len(tail_call) - 1),
              "OK code.write -> " + "o" * 983]
    kinds = ["wake", "reply", "results", "reply", "reply", "results"]
    budget = 8_000
    room = (budget - _held([blocks[0]] + blocks[-2:])
            - len(_dropped_note(len(blocks))) - 2)
    # The shape: the probe's stub fits beside the tail, and the read does not.
    assert len(probe) + 2 <= room < len(read) + 2 + len(read_call) + 2, room

    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget)
    assert read in fitted, "the middle kept stubs and no read"
    assert "CUT this exchange" in fitted[-2], "the cap did not fire"
    assert _held(fitted) <= budget and len(fitted_kinds) == len(fitted)


def test_a_runner_note_is_no_read_for_the_wake_share(db):
    """
    Frame 119, pass 3. Night 115, s73, turns 6 to 13: the only middle
    results block was the runner's reply-cut note, and the wake took half
    and lost 4,707 characters of source for it. A results block with no
    `OK <fn>` line is no read, so the wake keeps two thirds.
    """
    from rota.core.runner import _fit

    budget = 28_242
    assert (budget * 2 // 3, budget // 2) == (18_828, 14_121)
    note = "ERROR reply cut: your reply was cut at the output budget. "
    blocks = ["WAKE " + "w" * (18_920 - 5),
              "[your reply of an earlier turn]",
              note + "n" * (332 - len(note)),
              "I survey the area. " * 105,
              "OK code.area -> " + "a" * (9_500 - 16)]
    kinds = _paired(blocks)
    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget)
    assert fitted[0].startswith(blocks[0][:budget * 2 // 3] + "\nCUT your wake")
    assert (fitted, fitted_kinds) == _parent_fit(_F119_PARENT)(
        list(blocks), list(kinds), budget)
    assert _held(fitted) <= budget


def test_a_block_of_repeat_lines_is_no_read_for_the_wake_share(db):
    """
    Frame 119, pass 4. The runner's repeat lines point at an earlier answer
    and hold none. On night 115, 53 of 507 tail blocks held only such lines.
    A middle whose only results block holds them leaves the wake its two
    thirds, and the bytes are those of 6ba9fcc.
    """
    from rota.core.runner import _fit

    budget = 28_242
    repeats = chr(10).join([
        "OK code.area -> was run for you before you started. What code.area "
        "returned then still stands.",
        "OK code.source -> unchanged since you asked earlier this session. "
        "What code.source returned then still stands."])
    blocks = ["WAKE " + "w" * (18_920 - 5),
              "TOOL: code.area()\nTOOL: code.source(path='a.py')",
              repeats,
              "I survey the area. " * 105,
              "OK code.area -> " + "a" * (9_500 - 16)]
    kinds = _paired(blocks)
    fitted, fitted_kinds = _fit(list(blocks), list(kinds), budget)
    assert fitted[0].startswith(blocks[0][:budget * 2 // 3] + "\nCUT your wake")
    assert (fitted, fitted_kinds) == _parent_fit(_F119_PARENT)(
        list(blocks), list(kinds), budget)
    assert _held(fitted) <= budget


def test_a_runner_note_buys_no_cut_of_the_tail_reply(db):
    """
    Frame 119, pass 4. The tail cap landed when its trial kept any middle
    results block, and a reply-cut note alone is no read. The reply stays
    whole, and the bytes are those of 032c71c, before the cap: 6ba9fcc
    already cut the reply for the note.
    """
    from rota.core.runner import _fit

    note = "ERROR reply cut: your reply was cut at the output budget. "
    tail_call = "TOOL: code.write(path='a.py')"
    blocks = ["WAKE " + "w" * 995,
              "[your reply of an earlier turn]",
              note + "n" * (332 - len(note)),
              "r" * (7_000 - len(tail_call) - 1) + "\n" + tail_call,
              "OK code.write -> " + "o" * 483]
    kinds = _paired(blocks)
    fitted, fitted_kinds = _fit(list(blocks), list(kinds), 8_000)
    # The cap would cut the reply to 3,828. `_cap_exchange` still trims it
    # to the room the note leaves, as before the cap.
    assert len(fitted[-2]) > 6_000, "a note bought a reply cut"
    assert (fitted, fitted_kinds) == _parent_fit()(
        list(blocks), list(kinds), 8_000)
    assert _held(fitted) <= 8_000


def test_a_tester_reads_the_whole_failure_and_a_developer_reads_the_tail(db):
    """Frame 110, night 106: the 700 tail of `_03`'s run held parser frames
    and not the test's own call line. A Tester challenge gets the whole stored
    output. Every other wake keeps the tail, so its prompt does not move. A
    Tester answer puts the raising line before the tail (frame 317)."""
    from rota.core.runner import resolve_inbound

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i1','export JSON','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk1','i1','print JSON')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c1','tk1','echo_json prints one line')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES "
               "('b1','i1','running')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst1','b1','c1','test_export.py','assert True')")
    call = ">       asyncio.run(echo_json({'a': 1}))"
    output = (call + " ").ljust(1999, "x")
    assert len(output) == 1999
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, attempt, output) VALUES ('r1','b1','tst1','abc123',"
               "'fail',1,?)", (output,))
    for mid, to, verb in (("m2", "tester", "challenge"),
                          ("m3", "developer", "challenge"),
                          ("m4", "tester", "answer")):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                   "verb, body_refs, seq) VALUES (?,'t2','developer',?,"
                   "?,'[\"tst1\", \"c1\"]',2)", (mid, to, verb))
    db.commit()

    tester = resolve_inbound(db, Wake(role="tester", kind="message",
                                      message_id="m2", detail="challenge"))
    seen = tester["resolved_refs"]["tst1"]["last_run"]["output_tail"]
    assert seen == output and seen.index(call) < 10

    developer = resolve_inbound(db, Wake(role="developer", kind="message",
                                         message_id="m3", detail="challenge"))
    tail = developer["resolved_refs"]["tst1"]["last_run"]["output_tail"]
    assert tail == output[-700:] and call not in tail

    # Challenge mode only: a Tester woken by an answer keeps the tail.
    answer = resolve_inbound(db, Wake(role="tester", kind="message",
                                      message_id="m4", detail="answer"))
    assert answer["resolved_refs"]["tst1"]["last_run"]["output_tail"] \
        == output[-700:]

    # Frame 317, pass 1b: a raising line outside the tail comes first, with
    # its two neighbours, once.
    raised = "before\nE   KeyError: 'prog_name'\nafter\n" + output
    db.execute("UPDATE test_runs SET output = ? WHERE id = 'r1'", (raised,))
    db.commit()
    answer = resolve_inbound(db, Wake(role="tester", kind="message",
                                      message_id="m4", detail="answer"))
    run = answer["resolved_refs"]["tst1"]["last_run"]
    assert run["output_tail"] == raised[-700:]
    assert run["raising_line"] == "before\nE   KeyError: 'prog_name'\nafter\n...\n"
    developer = resolve_inbound(db, Wake(role="developer", kind="message",
                                         message_id="m3", detail="challenge"))
    assert developer["resolved_refs"]["tst1"]["last_run"]["output_tail"] \
        == raised[-700:]


def test_a_tester_challenge_shows_the_failed_run_as_text_above_the_json(db):
    """Frame 110's interview: the seat missed a failure that sat inside an
    escaped JSON string. A Tester challenge now shows the body and the
    failure as plain text above the JSON. Other wakes stay as they were."""
    from rota.core.runner import _failed_before_assertion, build_prompt
    from rota.core.sandbox import build
    from rota.roles import prompts

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i1','a report','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk1','i1','make a report')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c1','tk1','a report carries its title')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES "
               "('b1','i1','running')")
    body = ("from report import make_report\n\n\n"
            "def test_report_has_title():\n"
            "    result = make_report('q3')\n"
            "    assert result.title == 'q3'\n")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst1','b1','c1','test_report.py',?)", (body,))
    error = ("E       TypeError: make_report() takes 0 positional arguments "
             "but 1 was given")
    output = ("    def test_report_has_title():\n"
              ">       result = make_report('q3')\n"
              f"{error}\n\n"
              "test_report.py:5: TypeError\n"
              "1 failed in 0.02s\n")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, attempt, output) VALUES ('r1','b1','tst1','abc123',"
               "'fail',1,?)", (output,))
    for mid, to in (("m2", "tester"), ("m3", "developer")):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                   "verb, body_refs, seq) VALUES (?,'t2','developer',?,"
                   "'challenge','[\"tst1\", \"c1\"]',2)", (mid, to))
    db.commit()

    from rota.core.runner import resolve_inbound

    wake = Wake(role="tester", kind="message", message_id="m2",
                detail="challenge")
    sb = build("tester", db, batch_id="b1", mode="challenge",
               allow=prompts.mode_tools("tester", "challenge"))
    _system, user = build_prompt("tester", sb, wake, {}, "MODE: challenge",
                                 resolve_inbound(db, wake))
    head = user.index("[last run of tst1: failed before any assertion]")
    assert head < user.index("The message that woke you:")
    block = user[head:user.index("The message that woke you:")]
    assert "    result = make_report('q3')" in block
    assert error in block and "\\n" not in block

    wake = Wake(role="developer", kind="message", message_id="m3",
                detail="challenge")
    sb = build("developer", db, batch_id="b1")
    _system, user = build_prompt("developer", sb, wake, {}, "MODE: challenge",
                                 resolve_inbound(db, wake))
    assert "[last run of" not in user

    # An assertion that ran shows its own line before the error.
    ran = ("    def test_report_has_title():\n"
           "        result = make_report('q3')\n"
           ">       assert result.title == 'q3'\n"
           "E       AssertionError\n")
    assert not _failed_before_assertion(body, ran)
    assert _failed_before_assertion(body, output)

    # Night 107, s151: a chained traceback prints the cause's `E ` line
    # above the test's own assert. The last section decides.
    chained = ("E       TypeError: Object of type function is not JSON "
               "serializable\n\n"
               "json/encoder.py:182: TypeError\n\n"
               "During handling of the above exception, another exception "
               "occurred:\n\n"
               "    def test_report_has_title():\n"
               "        result = make_report('q3')\n"
               ">       assert result.title == 'q3'\n"
               "E       AssertionError\n")
    assert not _failed_before_assertion(body, chained)


# Frame 120. The parent is the commit before the red rows group by output.
_F120_PARENT = "aefd1f9"

# Night 113's traceback, 726 characters as the harness wrote it.
_F120_TRACEBACK = (
    "ImportError while loading conftest 'D:\\repos\\_AI\\sample_repos\\clickI"
    "\\.rota\\worktrees\\bg_1\\tests\\conftest.py'.\n"
    "tests\\conftest.py:3: in <module>\n"
    "    from click.testing import CliRunner\n"
    "src\\click\\__init__.py:10: in <module>\n"
    "    from .core import Argument as Argument\n"
    "src\\click\\core.py:23: in <module>\n"
    "    from . import types\n"
    "src\\click\\types.py:17: in <module>\n"
    "    from .exceptions import BadParameter\n"
    "src\\click\\exceptions.py:10: in <module>\n"
    "    from .utils import echo\n"
    "src\\click\\utils.py:1: in <module>\n"
    "    from . import click\n"
    "E   ImportError: cannot import name 'click' from partially initialized "
    "module 'click' (most likely due to a circular import) "
    "(D:\\repos\\_AI\\sample_repos\\clickI\\.rota\\worktrees\\bg_1\\src\\click"
    "\\__init__.py)")


def _f120_db(tmp_path, own: list[str], project: list[str]):
    """
    A batch whose own tests and project tests are red with the given outputs.
    Own row i has criterion c{i}, and project row i has no criterion.
    """
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('echo_json','Add echo_json','in_scope',"
                 "'approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','echo_json','add echo_json')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
                 "('b1','echo_json','running','abc123')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    rows = ([(f"own_{i}", f"c{i}", f"tests/test_utils/test_echo_json_{i}.py", said)
             for i, said in enumerate(own)]
            + [(f"inh_{i:08x}", None, f"tests/test_mod_{i}.py", said)
               for i, said in enumerate(project)])
    for n, (tid, crit, path, said) in enumerate(rows):
        if crit:
            conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                         "(?, 'tk1', ?)", (crit, f"echo_json case {crit}"))
        body = (f"def test_{tid}():\n    from click.utils import echo_json\n"
                f"    assert echo_json({n}) == {n}\n" + "    # case\n" * 30)
        conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                     "VALUES (?, 'b1', ?, ?, ?)", (tid, crit, path, body))
        conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
                     "result, output, attempt) VALUES (?, 'b1', ?, 'abc123', "
                     "'error', ?, 1)", (f"r{n}", tid, said))
    # Frame 207: the base run found every project test green, so the
    # doors say "passed before this batch".
    conn.execute("INSERT INTO config (key, value) VALUES ('base_run:b1', ?)",
                 (json.dumps({tid: {"result": "pass"}
                              for tid, crit, _, _ in rows if not crit}),))
    conn.commit()
    return conn


def _f120_push(conn, module=None):
    """The `tick:tests_failing` push of the Developer, by `module`'s runner."""
    from rota.core import runner
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = build("developer", conn, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    wake = Wake("developer", "tick:tests_failing", refs=("b1",))
    return sb, wake, (module or runner).push_working_set("developer", sb, wake)


_F120_PROJECT_KEY = "the project's own tests, not passing at your commit"


def test_red_rows_with_one_output_show_it_once_and_the_source_survives(tmp_path):
    """
    Frame 120. Night 113, s153: 34 project rows held one traceback, the push
    showed ten copies, and the window cut removed all of `code.source`. The
    traceback now shows once with the 34 tests, and the source is kept.
    """
    from rota.core.runner import _fit, _render, build_prompt, PUSH_CHARS

    own = [f"own failure {i}: " + f"line {i}\n" * 90 for i in range(3)]
    conn = _f120_db(tmp_path, own, [_F120_TRACEBACK] * 34)
    sb, wake, pushed = _f120_push(conn)

    shown = pushed["tests.load"]
    assert [r["said"] for r in shown["the batch's tests, not passing"]] == own
    block = shown[_F120_PROJECT_KEY]
    assert len(block) == 1, block
    assert block[0]["said"] == _F120_TRACEBACK
    assert block[0]["count"] == 34
    assert block[0]["tests that gave this output"] == [
        f"inh_{i:08x} tests/test_mod_{i}.py" for i in range(34)]
    assert list(block[0]) == ["said", "count", "tests that gave this output"]
    rendered = _render(shown, PUSH_CHARS)
    assert (rendered.index('"count": 34')
            < rendered.index('"tests that gave this output"')), \
        "a cut inside the id list would hide the count"
    assert rendered.count("partially initialized") == 1
    assert "34 test(s) with no criterion" in shown["what that means"]

    # The wake around it, at night 113's sizes (frame 119's design, table 1).
    parent = _f120_push(conn, _parent_runner(_F120_PARENT))[2]["tests.load"]

    def wake_of(tests_load):
        body = {"batches.expect": "e" * 3_913, "code.diff": "d" * 2_167,
                "criteria.load": "c" * 839, "references.load": "r" * 22,
                "tests.load": tests_load,
                "code.source": {"path": "src/click/utils.py", "start": 0,
                                "end": 400, "text": "def echo():\n" * 1_670}}
        user = build_prompt("developer", sb, wake, body, instructions="")[1]
        return _fit([user], ["wake"], budget=27_096)[0][0]

    kept = wake_of(shown)
    assert "\n[code.source]\npath: src/click/utils.py" in kept
    assert "def echo():" in kept.split("\n[code.source]\n", 1)[1]
    assert "[code.source]" not in wake_of(parent), "the parent kept the source"


def test_red_rows_with_distinct_outputs_push_the_parents_bytes(tmp_path):
    """
    Frame 120. A wake whose red rows each say something else pushes what the
    parent pushed, byte for byte, so its recordings stay.
    """
    from rota.core.runner import _render, PUSH_CHARS

    own = [f"own {i}\nE   AssertionError: {i}" for i in range(2)]
    project = [f"tests/test_mod_{i}.py:{10 + i}: in test_{i}\nE   KeyError: {i}"
               for i in range(5)] + [_F120_TRACEBACK]
    conn = _f120_db(tmp_path, own, project)
    pushed = _f120_push(conn)[2]
    parent = _f120_push(conn, _parent_runner(_F120_PARENT))[2]

    assert pushed == parent
    for key in pushed:
        assert _render(pushed[key], PUSH_CHARS) == _render(parent[key], PUSH_CHARS)


def test_red_row_groups_keep_the_order_of_their_first_row():
    """
    Frame 120. Two shared outputs and one unique output: the unique row keeps
    today's form, and each group stands where its first row stood.
    """
    from rota.core.runner import _red_rows_by_output

    rows = [{"id": "u1", "path": "tests/u.py", "said": "X", "body": "b"},
            {"id": "a1", "path": "tests/a1.py", "said": "A"},
            {"id": "b1", "path": "tests/b1.py", "said": "B"},
            {"id": "a2", "path": "tests/a2.py", "said": "A"},
            {"id": "b2", "path": "tests/b2.py", "said": "B"},
            {"id": "b3", "path": "tests/b3.py", "said": "B"}]
    assert _red_rows_by_output(rows) == [
        {"id": "u1", "path": "tests/u.py", "said": "X"},
        {"said": "A", "count": 2, "tests that gave this output":
            ["a1 tests/a1.py", "a2 tests/a2.py"]},
        {"said": "B", "count": 3, "tests that gave this output":
            ["b1 tests/b1.py", "b2 tests/b2.py", "b3 tests/b3.py"]},
    ]
    assert [list(r) for r in _red_rows_by_output(rows)[1:]] == [
        ["said", "count", "tests that gave this output"]] * 2


def test_red_rows_merge_on_byte_identical_outputs_only():
    """
    Frame 120. An output that differs in the test's own name or in one line
    number is another fact, so it keeps its own row.
    """
    from rota.core.runner import _red_rows_by_output

    said = "tests/test_a.py:12: in test_a\nE   AssertionError"
    rows = [{"id": "a", "path": "tests/test_a.py", "said": said},
            {"id": "b", "path": "tests/test_b.py",
             "said": said.replace("test_a", "test_b")},
            {"id": "c", "path": "tests/test_a.py",
             "said": said.replace(":12:", ":13:")},
            {"id": "d", "path": "tests/test_d.py", "said": said + " "}]
    assert _red_rows_by_output(rows) == [
        {k: r[k] for k in ("id", "path", "said")} for r in rows]


# Frame 207. Night 140's red line for `inh_f3b0c3db` at bg_2's base 3901a51.
_F207_SAID = (
    "tests/test_utils/test_confirm_closed_stdin.py:8: in test_confirm\n"
    "    with runner.isolated_filesystem():\n"
    "E   DeprecationWarning: 'isolated_filesystem' is deprecated and will be "
    "removed in Click 9.0.\n"
    "1 failed in 0.15s")
_F207_QUOTE = ("DeprecationWarning: 'isolated_filesystem' is deprecated and "
               "will be removed in Click 9.0")
_F207_FACT = (
    "the base run at this batch's start found inh_00000000 red too. The "
    "base run said: " + _F207_QUOTE + ". Your diff did not break it, and "
    "the fix is not yours. Send msg.escalate_architect(refs=['inh_00000000'])")


def _f207_db(tmp_path, own: list[str], result: str):
    """Frame 120's batch with one red project test, and a base run that
    found that test `result`."""
    conn = _f120_db(tmp_path, own, [_F207_SAID])
    row = {"result": result}
    if result != "pass":
        row["output"] = _F207_SAID
    conn.execute("INSERT OR REPLACE INTO config (key, value) "
                 "VALUES ('base_run:b1', ?)",
                 (json.dumps({"inh_00000000": row}),))
    conn.commit()
    return conn


def test_the_fix_wake_quotes_the_base_run_of_a_project_test_red_at_the_base(tmp_path):
    """Frame 207, night 140: the push said "they passed before this batch"
    from a constant, and the test was red at bg_2's base."""
    conn = _f207_db(tmp_path, [], "fail")
    sb, wake, pushed = _f120_push(conn)
    assert pushed["tests.load"]["what that means"] == (
        "1 test(s) with no criterion are the project's, and " + _F207_FACT)


def test_the_fix_wake_keeps_its_sentence_when_the_base_run_passed(tmp_path):
    conn = _f207_db(tmp_path, [], "pass")
    sb, wake, pushed = _f120_push(conn)
    assert pushed["tests.load"]["what that means"] == (
        "1 test(s) with no criterion are the project's, and they passed "
        "before this batch. Your diff broke them. Read code.diff below and "
        "restore what it changed; a challenge has no side here")


def test_a_challenge_on_a_base_red_project_test_is_offered_an_admitted_escalation(tmp_path):
    """Frame 207, night 140: s322 challenged `inh_f3b0c3db` and the door
    said it passed before this batch. The door now quotes the base run and
    names the escalation, and the doors admit that call."""
    from rota.core.sandbox import dry_run

    conn = _f207_db(tmp_path, [], "fail")
    sb, _, _ = _f120_push(conn)
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["inh_00000000"],
                quotes=["with runner.isolated_filesystem():"])
    assert str(exc.value) == (
        "a challenge to the tester names both sides of the conflict in refs "
        "-- the criterion and the test -- and yours names no criterion. "
        "inh_00000000 has no criterion: it is the project's own test and "
        + _F207_FACT)
    offers = [o for o in sb.ctx.offers if o.op == "msg.escalate_architect"]
    assert [o.args for o in offers] == [{"refs": ["inh_00000000"]}]
    res = dry_run(sb, offers[0].op, offers[0].args, offers[0].then)
    assert res.admitted, res.refusal


def test_a_challenge_pairing_a_criterion_with_a_base_red_project_test_quotes_the_base_run(tmp_path):
    """The second door of the same challenge: a criterion of this batch
    beside the project's test."""
    conn = _f207_db(tmp_path, ["own failure"], "fail")
    sb, _, _ = _f120_push(conn)
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["c0", "inh_00000000"],
                quotes=["echo_json case c0", "with runner.isolated_filesystem():"])
    assert str(exc.value) == (
        "inh_00000000 has no criterion: it is the project's own test and "
        + _F207_FACT)


# These tests pin the doors of the word form of a page call. Pass R2
# retires the doors and these pins (frame 345, the R1 brief, step 5).
pytestmark = pytest.mark.usefixtures("old_page_form")
