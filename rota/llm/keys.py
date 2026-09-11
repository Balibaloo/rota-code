"""
Provider keys, outside every profile. plans/model-setup.md, step 3.

A profile names the variable that holds a key, `key_env = "NAME"`, and never
the key. The key lives in the environment, or in `~/.rota/keys.env`
(`ROTA_HOME` moves the home), one `NAME=value` per line, restricted to the
user. The environment wins over the file. Local providers usually need none;
litellm wants one for the OpenAI shape, and any word does for Ollama.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path


def keys_path() -> Path:
    return Path(os.environ.get("ROTA_HOME", str(Path.home() / ".rota"))) / "keys.env"


def load(path: Path | None = None) -> dict[str, str]:
    """The file's keys, name to value. Missing file, no keys."""
    p = path or keys_path()
    out: dict[str, str] = {}
    if not p.is_file():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        out[name.strip()] = value.strip().strip("'\"")
    return out


def get(name: str, path: Path | None = None) -> str | None:
    """The environment first, then the file."""
    if not name:
        return None
    value = os.environ.get(name)
    if value:
        return value
    return load(path).get(name)


def set_key(name: str, value: str, path: Path | None = None) -> Path:
    """Write one key to the file, replacing a line of the same name, and keep
    the file readable by this user only."""
    p = path or keys_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    rows = load(p)
    rows[name] = value
    body = "".join(f"{k}={v}\n" for k, v in sorted(rows.items()))
    p.write_text(body, encoding="utf-8")
    _restrict(p)
    return p


def _restrict(p: Path) -> None:
    try:
        os.chmod(p, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
    if os.name == "nt":
        import subprocess
        try:
            user = os.environ.get("USERNAME", "")
            subprocess.run(["icacls", str(p), "/inheritance:r", "/grant:r", f"{user}:F"],
                           capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            pass


def export(name: str, path: Path | None = None) -> bool:
    """Put the file's key into the environment when the environment lacks
    it, so a provider library that reads the environment finds it."""
    if not name or os.environ.get(name):
        return bool(name and os.environ.get(name))
    value = load(path).get(name)
    if value:
        os.environ[name] = value
        return True
    return False
