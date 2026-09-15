"""
A run profile is chosen once and frozen into the run.

One file for provider, pins and the model per desk, replacing four places
the same facts used to live. Bound at onboarding; the routing string the
runner already understands is derived from it; a change is a new snapshot
with history.
"""
from __future__ import annotations

import json

import pytest

from rota.core import config
from rota.core.db import init_db
from rota.llm import profile as P
from rota.llm.llm import LiteLLMBackend, OllamaBackend


def test_the_shipped_local_profile_loads_and_names_a_judge_per_desk():
    p = P.find("local")
    assert p.provider == "ollama" and p.default_model == "qwen3:8b"
    assert p.model_for("tester") == "qwen3.5:9b" and p.model_for("liaison") == "qwen3:8b"
    assert p.routing() == "critic=qwen3.5:9b,developer=qwen3.5:9b,terminologist=qwen3.5:9b,tester=qwen3.5:9b"
    assert isinstance(p.backend(), OllamaBackend)
    pins = p.pins_for("critic")
    assert (pins.model, pins.temperature, pins.num_ctx) == ("qwen3.5:9b", 0.0, 12288)


def test_a_project_profile_wins_and_a_missing_one_says_where_it_looked(tmp_path):
    (tmp_path / ".rota" / "profiles").mkdir(parents=True)
    (tmp_path / ".rota" / "profiles" / "local.toml").write_text(
        'name = "local"\n[provider]\nkind = "litellm"\nendpoint = "http://localhost:8080/v1"\n'
        'api_key_env = "NOPE_KEY"\n[pins]\nmax_tokens = 512\n[models]\ndefault = "openai/gpt-x"\n'
        'critic = "anthropic/claude-sonnet-5"\n', encoding="utf-8")
    p = P.find("local", tmp_path)
    assert p.provider == "litellm" and p.source.endswith("local.toml")
    assert isinstance(p.backend(), LiteLLMBackend) and p.backend().api_base == "http://localhost:8080/v1"
    assert p.pins_for("critic").max_tokens == 512
    assert dict(P.available(tmp_path))["local"] == p.source
    with pytest.raises(FileNotFoundError, match="looked in"):
        P.find("nope", tmp_path)
    # check says the key is missing, before any database is touched
    assert any("NOPE_KEY" in line for line in p.check())


def test_a_bad_pin_or_provider_is_refused_at_load():
    with pytest.raises(ValueError, match="provider kind"):
        P.Profile.from_dict({"provider": {"kind": "carrier-pigeon"}})
    with pytest.raises(ValueError, match="unknown pins"):
        P.Profile.from_dict({"pins": {"temprature": 0.1}})
    with pytest.raises(ValueError, match="top_p"):
        P.Profile.from_dict({"pins": {"top_p": 7}})


def test_binding_freezes_the_profile_and_derives_the_routing(tmp_path):
    db = init_db(tmp_path / "rota.db")
    p = P.find("local")
    P.bind(db, p)
    assert config.get(db, "model_routing") == p.routing()
    again = P.of_run(db)
    assert again.to_dict() == p.to_dict() and again.source == "run"
    json.dumps(config.get(db, "profile"))


def test_set_writes_a_new_snapshot_and_an_override_keeps_the_rest(tmp_path):
    db = init_db(tmp_path / "rota.db")
    P.bind(db, P.find("local"))
    fresh = P.set_field(db, "models.tester", "qwen3.5:4b")
    assert fresh.model_for("tester") == "qwen3.5:4b" and fresh.model_for("critic") == "qwen3.5:9b"
    assert "tester=qwen3.5:4b" in config.get(db, "model_routing")
    fresh = P.set_field(db, "pins.max_tokens", "300")
    assert fresh.pins_for(None).max_tokens == 300
    over = fresh.with_override(model="qwen3:4b", roles={"critic": "qwen2.5:14b"})
    assert over.default_model == "qwen3:4b" and over.model_for("critic") == "qwen2.5:14b"
    assert over.model_for("tester") == "qwen3.5:4b"
    with pytest.raises(ValueError, match="no profile bound"):
        P.set_field(init_db(tmp_path / "other.db"), "models.tester", "x")


def test_keys_live_outside_the_profile(tmp_path, monkeypatch):
    """plans/model-setup.md step 3: key_env names a variable; the file fills
    the environment's gap; the environment wins; a remote profile says so."""
    from rota.llm import keys, profile

    monkeypatch.setenv("ROTA_HOME", str(tmp_path))
    monkeypatch.delenv("ACME_KEY", raising=False)
    assert keys.get("ACME_KEY") is None
    p = keys.set_key("ACME_KEY", "s3cret")
    assert p == tmp_path / "keys.env" and keys.get("ACME_KEY") == "s3cret"
    monkeypatch.setenv("ACME_KEY", "from-env")
    assert keys.get("ACME_KEY") == "from-env"
    monkeypatch.delenv("ACME_KEY", raising=False)
    prof = profile.Profile.from_dict({"name": "acme", "provider": {"kind": "litellm",
                                      "endpoint": "https://api.acme.test/v1", "key_env": "ACME_KEY"},
                                      "models": {"default": "openai/x"}})
    assert prof.api_key_env == "ACME_KEY" and prof.remote
    problems = prof.check()
    assert any("remote: prompts and the repository" in x for x in problems)
    assert not any("set neither" in x for x in problems)
    prof.backend()
    assert __import__("os").environ.get("ACME_KEY") == "s3cret"


def test_a_model_on_its_own_endpoint_is_reached_there_and_only_there():
    """
    2026-09-14: gemma-4 lives behind a llama-server while every other desk
    stays on Ollama. The profile maps the model to its endpoint; the backend
    sends each call where its model lives; the Ollama check does not ask
    Ollama for a model it does not serve.
    """
    from rota.llm import llm
    from rota.llm.profile import Profile
    p = Profile.from_dict({
        "provider": {"kind": "ollama"},
        "models": {"default": "qwen3:8b", "developer": "openai/big.gguf"},
        "endpoints": [{"model": "openai/big.gguf", "endpoint": "http://127.0.0.1:8080/v1",
                       "timeout": 900,
                       "extra_body": {"chat_template_kwargs": {"enable_thinking": False}}}],
    }, name="mixed")
    b = p.backend()
    assert isinstance(b, llm.RoutedBackend)
    assert isinstance(b.for_model("qwen3:8b"), llm.OllamaBackend)
    big = b.for_model("openai/big.gguf")
    assert isinstance(big, llm.LiteLLMBackend)
    kw = big.kwargs("s", "u", llm.Pins(model="openai/big.gguf"))
    assert kw["api_base"] == "http://127.0.0.1:8080/v1"
    assert kw["extra_body"] == {"chat_template_kwargs": {"enable_thinking": False}}
    # No key in the environment: LiteLLM still needs one for `openai/`, and
    # a local server checks none (night 61 died on "Missing credentials").
    import os
    if not os.environ.get("OPENAI_API_KEY"):
        assert kw["api_key"] == "local"
    assert kw["timeout"] == 900
    # Round trip: what the run stores loads back to the same profile.
    assert Profile.from_dict(p.to_dict(), name="mixed").endpoints == p.endpoints

def test_a_profile_can_turn_thinking_on_per_model():
    """Finding 81 (2026-09-15): qwen3.5:9b on the 3080 with thinking off wrote
    prose and no call; with thinking on it called. The [think] table sets it
    per model, and the pin keys the recording only when it is set."""
    from rota.llm.profile import Profile
    p = Profile.from_dict({"provider": {"kind": "ollama"},
                           "models": {"default": "qwen3:8b", "tester": "qwen3.5:9b"},
                           "think": {"qwen3.5:9b": True}}, name="t")
    assert p.pins_for("tester").think is True
    assert p.pins_for("liaison").think is None
    assert "think" in p.pins_for("tester").extras() and "think" not in p.pins_for("liaison").extras()
    assert p.to_dict()["think"] == {"qwen3.5:9b": True}

def test_a_wake_runs_with_the_profiles_think_for_its_model(tmp_path):
    """The runner rebuilt Pins from three fields and dropped the rest; the
    profile's think for the routed model reaches the session now."""
    from rota.core.runner import routed_pins
    from rota.core.scheduler import Wake
    from rota.llm import llm
    db = init_db(tmp_path / "r.db")
    P.bind(db, P.Profile.from_dict({"provider": {"kind": "ollama"},
                                    "models": {"default": "qwen3:8b", "tester": "qwen3.5:9b"},
                                    "think": {"qwen3.5:9b": True}}, name="t"))
    tester = routed_pins(db, llm.Pins(model="qwen3:8b"), Wake("tester", "tick:tests_missing"))
    liaison = routed_pins(db, llm.Pins(model="qwen3:8b"), Wake("liaison", "tick:agenda"))
    assert tester.model == "qwen3.5:9b" and tester.think is True
    assert liaison.model == "qwen3:8b" and liaison.think is None

