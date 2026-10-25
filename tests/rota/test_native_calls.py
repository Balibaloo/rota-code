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
        self.users = []

    def complete(self, system, user, pins, tools=None):
        self.tools.append(tools)
        self.systems.append(system)
        self.users.append(user)
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


# -- pass 2: what the trial of 2026-10-25 showed -------------------------------

def test_the_next_turn_shows_the_native_calls_with_their_arguments(db):
    """Gemma saw only result lines and sent the same three calls again."""
    stub = Stub([("", [NativeCall("problem__consult", {"id": "p1"})]),
                 ("Nothing there yet.", [])])
    run_session(db, _wake(), backend=stub, pins=Pins("stub"), native_tools=True)
    assert len(stub.systems) >= 2
    seen = stub.users[1]
    assert "problem.consult(id='p1')" in seen


def test_bad_native_arguments_are_refused_by_name(db):
    from rota.core.runner import _native_calls
    from rota.llm import toolproto
    done = Completion(text="", pins=Pins("stub"), tool_calls=[
        NativeCall("problem__consult", "{not json"),
        NativeCall("problem__consult", ["a"])])
    calls = _native_calls(done)
    assert all(isinstance(c, toolproto.ToolError) for c in calls)
    assert {c.reason for c in calls} == {"could not parse arguments"}


def test_a_native_call_behind_an_invented_result_is_dropped(db):
    write = NativeCall("problem__assert",
                       {"id": "i9", "text": "x", "kind": "in_scope"})
    stub = Stub([("OK problem.consult -> []\n", [write]),
                 ("Nothing there yet.", [])])
    out = run_session(db, _wake(), backend=stub, pins=Pins("stub"),
                      native_tools=True)
    assert "wrote its own tool results" in out.errors
    assert "problem.assert" not in _fns(db, out.session_id)


def test_glossary_amend_describes_each_parameter():
    from rota.roles import api
    schema = toolschema.schema_for("glossary.amend", api.glossary_amend)
    props = schema["function"]["parameters"]["properties"]
    assert props["sense"]["description"] != props["sense_body"]["description"]
    assert "meaning" in props["sense_body"]["description"]
    assert all(len(p["description"]) <= 200 for p in props.values())
    assert "\n\n" not in schema["function"]["description"]


def test_a_parameter_with_no_entry_takes_its_sentence_or_its_name():
    doc = "Do a thing.\n\nThe `alpha` value picks the row. Nothing else."
    assert toolschema.param_description(doc, "alpha") == (
        "The `alpha` value picks the row.")
    assert toolschema.param_description(doc, "beta") == "beta"


def test_the_profile_pins_reach_the_suite_and_the_key(tmp_path, monkeypatch):
    from rota.llm.llm import profile_pins
    home = tmp_path / "home"
    (home / "profiles").mkdir(parents=True)
    (home / "profiles" / "stub-capped.toml").write_text(
        'name = "stub-capped"\n[pins]\nnum_ctx = 4096\nmax_tokens = 512\n',
        encoding="utf-8")
    monkeypatch.setenv("ROTA_HOME", str(home))
    monkeypatch.setenv("ROTA_PROFILE", "stub-capped")
    monkeypatch.delenv("ROTA_NUM_CTX", raising=False)
    assert profile_pins() == {"max_tokens": 512, "num_ctx": 4096}
    monkeypatch.setenv("ROTA_NUM_CTX", "16384")
    assert profile_pins() == {"max_tokens": 512}, "the variable wins"
    capped = Pins("m", **profile_pins())
    assert (cassettes.key_for("s", "u", capped)
            != cassettes.key_for("s", "u", Pins("m")))
    monkeypatch.delenv("ROTA_PROFILE")
    assert profile_pins() == {}


def _graded(system, text, native=(), offered=()):
    from rota.core.runner import RunOutcome
    return RunOutcome("s1", True, 1, completions=[text], system=system,
                      native=[list(native)], offered=list(offered))


def test_the_graders_read_text_calls_as_before():
    from rota.testkit import fixtures
    out = _graded("  TOOL: problem.consult(id)\n", "TOOL: problem.consult(id='p1')")
    want = {"expect": {"first_call": {"fn": "problem.consult",
                                      "args": {"id": "p1"}}}}
    assert fixtures._first_call(want, out, 0) == []
    assert fixtures._no_call({"expect": {"no_call": True}}, out, 0)
    quiet = _graded("  TOOL: problem.consult(id)\n", "Nothing to do.")
    assert fixtures._no_call({"expect": {"no_call": True}}, quiet, 0) == []


def test_the_graders_read_native_calls():
    from rota.testkit import fixtures
    from rota.llm import toolproto
    call = toolproto.ToolCall("problem.consult", {"id": "p1"})
    out = _graded("  problem.consult(id)\n", "", native=[call],
                  offered=["problem.consult"])
    want = {"expect": {"first_call": {"fn": "problem.consult",
                                      "args": {"id": "p1"}}}}
    assert fixtures._first_call(want, out, 0) == []
    assert fixtures._no_call({"expect": {"no_call": True}}, out, 0)
    quiet = _graded("  problem.consult(id)\n", "Nothing to do.",
                    offered=["problem.consult"])
    assert fixtures._no_call({"expect": {"no_call": True}}, quiet, 0) == []
    assert fixtures._first_call(want, quiet, 0)
