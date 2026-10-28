"""Frame 235: the default model host names an IPv4 address.

On Windows ``localhost`` resolves to ``::1`` first. Ollama listens on IPv4
alone, so every request paid a refused IPv6 connect of about two seconds
before the IPv4 retry: 2,410 turns and 83 minutes on night 146 (observed:
plans/night146-read.md, section 1.5, 2026-10-14).

F29 (plans/rootfix-audit-2026-10-27-b.md): the model host has one reader,
``llm.OLLAMA_HOST``. The gate, the tool probe and the two litellm profiles
read it, so a second copy of the host cannot drift from it.
"""
import io
import json
import re
from pathlib import Path

from rota.llm import llm, profile
from rota.tools import gate, probe_tools

ROOT = Path(__file__).resolve().parents[2] / "rota"
DEFAULTS = {
    ROOT / "llm" / "llm.py": "OLLAMA_HOST",
    ROOT / "llm" / "discover.py": "LLAMACPP",
}
IPV4_URL = re.compile(r'"http://\d{1,3}(?:\.\d{1,3}){3}:\d+"')
ELSEWHERE = "http://elsewhere:9"
#: A read of the host from the environment in any form: `environ.get`,
#: `environ[...]` or `getenv` (review of F29 pass 1, finding 3).
ENV_READ = re.compile(r"""(?:environ\s*(?:\.get\s*\(|\[)|getenv\s*\()\s*['"]OLLAMA_HOST['"]""")


def _default_line(path, name):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{name} ="):
            return line
    raise AssertionError(f"{path.name} has no top-level {name} assignment")


def test_default_hosts_name_an_ipv4_address():
    for path, name in DEFAULTS.items():
        line = _default_line(path, name)
        assert "localhost" not in line, f"{path.name}: {line}"
        assert IPV4_URL.search(line), f"{path.name}: {line}"


def test_the_litellm_profiles_reach_the_model_host(monkeypatch):
    monkeypatch.setattr(llm, "OLLAMA_HOST", ELSEWHERE)
    for name in ("local-openai", "local-openai-native"):
        prof = profile.Profile.from_toml(ROOT / "llm" / "profiles" / f"{name}.toml")
        assert prof.endpoint == f"{ELSEWHERE}/v1", name


def test_the_gate_probe_falls_back_to_the_model_host(monkeypatch):
    asked = []
    monkeypatch.setattr(gate, "_get_json", lambda url, *a, **k: asked.append(url) or {})
    monkeypatch.setattr(llm, "OLLAMA_HOST", ELSEWHERE)
    gate.main_card_held({})
    assert asked == [f"{ELSEWHERE}/api/ps"]


def test_the_tool_probe_asks_the_model_host(monkeypatch):
    asked = []

    def urlopen(req, timeout=None):
        asked.append(getattr(req, "full_url", req))
        return io.BytesIO(json.dumps({"message": {}}).encode())

    monkeypatch.setattr(probe_tools.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(llm, "OLLAMA_HOST", ELSEWHERE)
    probe_tools.chat("m", "s", "u")
    assert asked == [f"{ELSEWHERE}/api/chat"]


def test_the_model_host_has_one_literal():
    """The port of the model host appears in the package at llm.py alone."""
    allowed = {ROOT / "llm" / "llm.py"}
    found = []
    for path in sorted(ROOT.rglob("*")):
        if path.suffix not in (".py", ".toml") or path in allowed:
            continue
        text = path.read_text(encoding="utf-8")
        if "11434" in text or ENV_READ.search(text):
            found.append(str(path.relative_to(ROOT)))
    assert found == []
