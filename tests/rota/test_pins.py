"""
Pins are every setting that can change a reply, and the cassette key follows
them without moving for a recording made before a pin existed.

The provider work (2026-09-09) grows `Pins` from three fields to seven. The
one rule that keeps the register alive: a pin at its default stays out of
the key. A recording made under the provider's defaults keeps its key, and
a recording made under a set pin gets its own.
"""
from __future__ import annotations

import hashlib
import json

import pytest

from rota.llm import cassettes, llm
from rota.llm.llm import LiteLLMBackend, OllamaBackend, Pins


def test_with_prompt_keeps_every_pin():
    p = Pins("m", 0.1, 4096, max_tokens=300, top_p=0.9, seed=7, repeat_penalty=1.1)
    q = p.with_prompt("hello")
    assert q.prompt_hash and q.prompt_hash != p.prompt_hash
    assert (q.max_tokens, q.top_p, q.seed, q.repeat_penalty) == (300, 0.9, 7, 1.1)
    assert set(q.as_dict()) == {"model", "temperature", "num_ctx", "prompt_hash",
                                "max_tokens", "top_p", "seed", "repeat_penalty"}
    json.dumps(q.as_dict())


def test_a_bad_pin_is_refused_by_name():
    for bad, word in ((Pins(temperature=-1), "temperature"),
                      (Pins(num_ctx=0), "num_ctx"),
                      (Pins(max_tokens=0), "max_tokens"),
                      (Pins(top_p=1.5), "top_p")):
        with pytest.raises(ValueError, match=word):
            bad.check()
    assert Pins().check() is not None


def test_the_key_of_the_original_pins_has_not_moved():
    """The blob every existing recording was keyed by, computed here by
    hand. If this moves, the register is a day of GPU away."""
    p = Pins("llama3.1:8b", 0.0, 12288)
    old = hashlib.sha256(json.dumps(
        ["llama3.1:8b", 0.0, 12288, "text", "sys", "usr"], sort_keys=True
    ).encode("utf-8")).hexdigest()[:32]
    assert cassettes.key_for("sys", "usr", p) == old


def test_a_set_pin_makes_its_own_key_and_an_unset_one_does_not():
    base = Pins("m", 0.0, 4096)
    assert cassettes.key_for("s", "u", base) == cassettes.key_for("s", "u", Pins("m", 0.0, 4096, max_tokens=None))
    keys = {cassettes.key_for("s", "u", Pins("m", 0.0, 4096, **{k: v}))
            for k, v in (("max_tokens", 100), ("top_p", 0.5), ("seed", 1),
                         ("repeat_penalty", 1.2))}
    assert len(keys) == 4 and cassettes.key_for("s", "u", base) not in keys


def test_ollama_options_carry_only_set_pins():
    b = OllamaBackend()
    assert b.options(Pins("m", 0.2, 2048)) == {
        "temperature": 0.2, "num_ctx": 2048, "num_predict": OllamaBackend.max_tokens}
    assert b.options(Pins("m", 0.2, 2048, max_tokens=50, seed=3, top_p=0.7)) == {
        "temperature": 0.2, "num_ctx": 2048, "num_predict": 50, "seed": 3, "top_p": 0.7}


def test_litellm_maps_portable_pins_and_refuses_the_ollama_only_one():
    b = LiteLLMBackend(api_base="http://localhost:8080/v1", timeout=42)
    kw = b.kwargs("s", "u", Pins("qwen3:8b", 0.0, 4096, max_tokens=99, seed=5),
                  tools=[{"type": "function"}])
    assert kw["model"] == "ollama/qwen3:8b"
    assert kw["max_tokens"] == 99 and kw["seed"] == 5 and kw["timeout"] == 42
    assert kw["api_base"] == "http://localhost:8080/v1" and kw["tools"]
    assert "num_ctx" not in kw and "top_p" not in kw
    assert b.kwargs("s", "u", Pins("anthropic/claude-sonnet-5"))["model"] == "anthropic/claude-sonnet-5"
    with pytest.raises(ValueError, match="repeat_penalty"):
        b.kwargs("s", "u", Pins("m", repeat_penalty=1.1))


def test_native_tools_are_off_unless_asked_and_travel_when_asked(tmp_path):
    """The runner computed the schemas and never handed them over, so every
    run spoke the text protocol. Now: off by default, on by opt-in, and the
    schemas reach the backend when on."""
    from rota.core.db import init_db
    from rota.core.predicates import Wake
    from rota.core.runner import run_session

    class Spy:
        name = "scripted"
        def __init__(self):
            self.seen = []
        def complete(self, system, user, pins, tools=None):
            self.seen.append(tools)
            return llm.Completion(text="done", pins=pins, backend=self.name, raw={})

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES ('e_m1','principal',1,'hi')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, seq) "
               "VALUES ('m1','t1','principal','liaison','converse','[\"e_m1\"]',1)")
    db.commit()
    off = Spy()
    run_session(db, Wake("liaison", "message", message_id="m1", detail="converse"),
                backend=off, pins=Pins("stub"), instructions="x")
    assert off.seen and all(t is None for t in off.seen)
    on = Spy()
    run_session(db, Wake("liaison", "message", message_id="m1", detail="converse"),
                backend=on, pins=Pins("stub"), instructions="x", native_tools=True)
    assert on.seen and all(t for t in on.seen), "the schemas must reach the backend"
