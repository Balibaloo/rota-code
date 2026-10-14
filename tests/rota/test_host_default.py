"""Frame 235: the default model hosts name an IPv4 address.

On Windows ``localhost`` resolves to ``::1`` first. Ollama listens on IPv4
alone, so every request paid a refused IPv6 connect of about two seconds
before the IPv4 retry: 2,410 turns and 83 minutes on night 146 (observed:
plans/night146-read.md, section 1.5, 2026-10-14).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "rota"
DEFAULTS = {
    ROOT / "llm" / "llm.py": "OLLAMA_HOST",
    ROOT / "llm" / "discover.py": "LLAMACPP",
    ROOT / "tools" / "gate.py": "DEFAULT_HOST",
    ROOT / "tools" / "probe_tools.py": "OLLAMA",
}
IPV4_URL = re.compile(r'"http://\d{1,3}(?:\.\d{1,3}){3}:\d+"')


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
