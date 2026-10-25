"""
Native tool calls, end to end (frame 323, 2026-10-25).

The runner handed schemas to the backend and never read the calls that came
back, so a native reply ran no tool. These tests hold the four parts of the
wiring: the calls run, an empty list falls back to the text parse, the
profile decides the default, and the prompt teaches the protocol in use.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.runner import compose_system, native_default, run_session
from rota.core.scheduler import Wake
from rota.llm import cassettes, llm, profile as profile_mod, toolschema
from rota.llm.llm import Completion, NativeCall, Pins


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('u1','principal','let users delete their account',1)")
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                 "VALUES ('m0','t1','principal','liaison','converse',0)")
    conn.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
                 "verb, seq) VALUES ('m1','m0','t1','liaison','vision_keeper',"
                 "'deliver',1)")
    return conn


def _wake():
    return Wake(role="vision_keeper", kind="message", message_id="m1",
                detail="deliver")


class Stub:
    """Replies in order. Each reply is a text and a list of native calls."""

    name = "scripted"

    def __init__(self, replies):
        self.replies = list(replies)
        self.tools = []
        self.systems = []

    def complete(self, system, user, pins, tools=None):
        self.tools.append(tools)
        self.systems.append(system)
        text, calls = self.replies.pop(0) if self.replies else ("Done.", [])
        return Completion(text=text, pins=pins, backend=self.name, raw={},
                          tool_calls=calls)


def _fns(db, sid):
    return [r["fn"] for r in db.execute(
        "SELECT fn FROM tool_calls WHERE session_id=? ORDER BY seq", (sid,))]


def test_a_native_call_runs_the_named_tool(db):
    stub = Stub([("", [NativeCall(toolschema.mangle("problem.consult"), {})]),
                 ("Nothing there yet.", [])])
    out = run_session(db, _wake(), backend=stub, pins=Pins("stub"),
                      native_tools=True)
    assert "problem.consult" in _fns(db, out.session_id)
    assert stub.tools[0], "the schemas must reach the backend"


def test_an_empty_native_list_falls_back_to_the_text_parse(db):
    stub = Stub([("TOOL: problem.consult()", []), ("Nothing there yet.", [])])
    out = run_session(db, _wake(), backend=stub, pins=Pins("stub"),
                      native_tools=True)
    assert "problem.consult" in _fns(db, out.session_id)


def test_the_plain_default_leaves_native_off(db, monkeypatch):
    monkeypatch.delenv("ROTA_PROFILE", raising=False)
    assert native_default(db) is False
    stub = Stub([("Nothing to do.", [])])
    run_session(db, _wake(), backend=stub, pins=Pins("stub"))
    assert all(t is None for t in stub.tools)
    assert "TOOL: artefact.verb" in stub.systems[0]


def test_the_environment_profile_turns_native_on(db, monkeypatch):
    monkeypatch.setenv("ROTA_PROFILE", "local-native-trial")
    assert native_default(db) is True
    monkeypatch.setenv("ROTA_PROFILE", "local")
    assert native_default(db) is False


def test_the_bound_profile_wins_over_the_environment(db, monkeypatch):
    monkeypatch.setenv("ROTA_PROFILE", "local")
    profile_mod.bind(db, profile_mod.find("local-native-trial"))
    assert native_default(db) is True
    stub = Stub([("Nothing to do.", [])])
    run_session(db, _wake(), backend=stub, pins=Pins("stub"))
    assert stub.tools[0], "the bound profile opts the run in"


def test_the_prompt_block_switches_with_the_protocol(db):
    from rota.core.runner import session_sandbox
    sb = session_sandbox(db, _wake())
    text = compose_system("vision_keeper", sb, instructions="x")
    native = compose_system("vision_keeper", sb, instructions="x", native=True)
    assert "TOOL: artefact.verb" in text and "TOOL: problem.consult" in text
    assert "TOOL: artefact.verb" not in native
    assert "Call the offered tools directly" in native
    assert "  problem.consult" in native, "the signatures list stays"


def test_the_trial_profile_carries_its_settings():
    p = profile_mod.find("local-native-trial")
    assert p.native_tools is True
    assert p.pins["max_tokens"] == 2048 and p.timeout == 300
    assert p.think == {"gemma4:12b-it-qat": False}
    assert p.roles == profile_mod.find("local").roles


def test_a_native_recording_replays_its_calls_under_the_native_key(tmp_path):
    dev = cassettes.open_dev_db(tmp_path / "dev.db")
    pins = Pins("stub")
    tools = [{"type": "function", "function": {"name": "problem__consult"}}]
    inner = Stub([("", [NativeCall("problem__consult", {"a": 1})])])
    rec = cassettes.RecordingBackend(inner, dev)
    first = rec.complete("s", "u", pins, tools=tools)
    assert inner.tools == [tools], "the recorder forwards the tools"
    assert first.tool_calls[0].name == "problem__consult"
    again = cassettes.ReplayOnlyBackend(dev).complete("s", "u", pins, tools=tools)
    assert [(c.name, c.args) for c in again.tool_calls] == [
        ("problem__consult", {"a": 1})]
    with pytest.raises(llm.LLMUnavailable):
        cassettes.ReplayOnlyBackend(dev).complete("s", "u", pins)
