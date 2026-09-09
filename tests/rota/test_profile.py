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
