"""
A run profile: one file that says which provider, which pins, and which model
runs each desk.

The same facts used to live in four places: pins a caller built by hand, the
`model_routing` setting, the backend host constant, and the register's
environment variable. A profile holds all of them. It is chosen once, at
onboarding, and frozen into the run, so a run's settings do not drift between
sessions; a change is a new snapshot with history, and every session still
records the model that ran it.

No secrets. A profile names the environment variable that holds a key, never
its value.

Lookup order for a name: `<project>/.rota/profiles/<name>.toml`, then
`~/.rota/profiles/<name>.toml` (`ROTA_HOME` overrides the home), then the
profiles shipped with the package. Project wins on a clash, because a
repository can want a bigger context or a shared judge.
"""
from __future__ import annotations

import dataclasses
import json
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .. import paths
from . import llm

SHIPPED = paths.PROFILES
PROVIDERS = ("ollama", "litellm")
PIN_KEYS = ("temperature", "num_ctx", "max_tokens", "top_p", "seed", "repeat_penalty")


def user_dir() -> Path:
    return Path(os.environ.get("ROTA_HOME", str(Path.home() / ".rota"))) / "profiles"


@dataclass(frozen=True)
class Profile:
    name: str
    provider: str = "ollama"
    endpoint: str = ""
    api_key_env: str = ""
    timeout: float = 300.0
    keep_alive: str = ""
    budget_usd: float | None = None
    pins: dict = field(default_factory=dict)
    # Per-role context windows: {role: num_ctx}. Night 81 (2026-09-16): the
    # Developer's fix-loop wake on click sentence three ran 11480 tokens
    # against a 12288 window, the whole function and three tests.
    context: dict = field(default_factory=dict)
    default_model: str = llm.DEFAULT_MODEL
    roles: dict = field(default_factory=dict)
    # Thinking per model, `[think]` in the file: "qwen3.5:9b" = true. A
    # pin the model's sessions carry (finding 81, 2026-09-15).
    think: dict = field(default_factory=dict)
    native_tools: bool = False
    # Models that live on their own server: model -> {"endpoint", "timeout",
    # "extra_body"}. Each is reached through LiteLLM at that endpoint; every
    # other model goes to the provider above. Written in the file as
    # [[endpoints]] tables with a `model` key.
    endpoints: dict = field(default_factory=dict)
    source: str = ""

    # -- construction -------------------------------------------------------

    @classmethod
    def from_dict(cls, d: dict, *, name: str | None = None, source: str = "") -> "Profile":
        prov = dict(d.get("provider") or {})
        models = dict(d.get("models") or {})
        pins = {k: v for k, v in (d.get("pins") or {}).items() if k in PIN_KEYS}
        context = {str(k): int(v) for k, v in (d.get("context") or {}).items()}
        unknown = set(d.get("pins") or {}) - set(PIN_KEYS)
        if unknown:
            raise ValueError(f"unknown pins {sorted(unknown)}; the pins are {list(PIN_KEYS)}")
        kind = prov.get("kind", "ollama")
        if kind not in PROVIDERS:
            raise ValueError(f"provider kind {kind!r} is not one of {list(PROVIDERS)}")
        default = models.pop("default", None) or d.get("default_model") or llm.DEFAULT_MODEL
        roles = {k: v for k, v in models.items() if k != "default"}
        roles.update(d.get("roles") or {})
        p = cls(
            name=name or d.get("name") or "unnamed",
            provider=kind,
            endpoint=str(prov.get("endpoint") or ""),
            api_key_env=str(prov.get("api_key_env") or prov.get("key_env") or ""),
            timeout=float(prov.get("timeout", 300.0)),
            keep_alive=str(prov.get("keep_alive") or ""),
            budget_usd=(float(prov["budget_usd"]) if prov.get("budget_usd") is not None else None),
            pins=pins,
            context=context,
            default_model=str(default),
            roles={str(k): str(v) for k, v in roles.items()},
            think={str(k): bool(v) for k, v in (d.get("think") or {}).items()},
            native_tools=bool(d.get("native_tools", False)),
            endpoints=cls._endpoints_of(d),
            source=source,
        )
        p.pins_for(None)          # refuse a bad pin at load, not at the first session
        return p

    @staticmethod
    def _endpoints_of(d: dict) -> dict:
        raw = d.get("endpoints") or {}
        entries = raw if isinstance(raw, list) else [
            {"model": m, **(v if isinstance(v, dict) else {"endpoint": v})}
            for m, v in raw.items()]
        out = {}
        for e in entries:
            model = str(e.get("model") or "")
            if not model or not e.get("endpoint"):
                raise ValueError("an endpoints entry needs `model` and `endpoint`")
            out[model] = {"endpoint": str(e["endpoint"]),
                          "timeout": float(e["timeout"]) if e.get("timeout") is not None else None,
                          "extra_body": dict(e.get("extra_body") or {})}
        return out

    @classmethod
    def from_toml(cls, path: Path) -> "Profile":
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
        return cls.from_dict(data, name=data.get("name") or path.stem, source=str(path))

    def to_dict(self) -> dict:
        """JSON-serialisable and complete; what the run stores."""
        return {
            "name": self.name,
            "think": dict(self.think),
            "provider": {"kind": self.provider, "endpoint": self.endpoint,
                         "api_key_env": self.api_key_env, "timeout": self.timeout,
                         "keep_alive": self.keep_alive, "budget_usd": self.budget_usd},
            "pins": dict(self.pins),
            "context": dict(self.context),
            "models": {"default": self.default_model, **self.roles},
            "native_tools": self.native_tools,
            "endpoints": [{"model": m, **v} for m, v in self.endpoints.items()],
        }

    def with_override(self, *, model: str | None = None,
                      roles: dict | None = None) -> "Profile":
        """A flag on the command line: one field changed, the rest kept."""
        return dataclasses.replace(
            self,
            default_model=model or self.default_model,
            roles={**self.roles, **(roles or {})},
        )

    # -- what a run needs ---------------------------------------------------

    def model_for(self, role: str | None) -> str:
        return self.roles.get(role or "", self.default_model)

    def pins_for(self, role: str | None) -> llm.Pins:
        model = self.model_for(role)
        pins = dict(self.pins)
        if role and role in (self.context or {}):
            pins["num_ctx"] = self.context[role]
        think = (self.think or {}).get(model)
        if think is not None and "think" not in pins:
            pins["think"] = bool(think)
        return llm.Pins(model=model, **pins).check()

    def routing(self) -> str:
        """The `model_routing` string the runner already understands."""
        return ",".join(f"{r}={m}" for r, m in sorted(self.roles.items()))

    @property
    def remote(self) -> bool:
        """Prompts and the repository's code leave this machine."""
        e = (self.endpoint or "").lower()
        return bool(e) and "localhost" not in e and "127.0.0.1" not in e

    def backend(self) -> llm.Backend:
        from . import keys
        if self.api_key_env:
            # The environment wins; the keys file fills a gap, so a provider
            # library that reads the environment finds the key there.
            keys.export(self.api_key_env)
        # The environment wins over the profile's timeout, as it does for the
        # key: a walk on the slow card sets ROTA_LLM_TIMEOUT, and tipsBD
        # (2026-09-13) lost a Terminologist turn to the profile's 300 s
        # with the variable set.
        import os as _os
        timeout = float(_os.environ.get("ROTA_LLM_TIMEOUT") or self.timeout)
        if self.provider == "litellm":
            default = llm.LiteLLMBackend(api_base=self.endpoint or None, timeout=timeout)
        else:
            default = llm.OllamaBackend(host=self.endpoint or llm.OLLAMA_HOST, timeout=timeout)
        if not self.endpoints:
            return default
        return llm.RoutedBackend(default, {
            m: llm.LiteLLMBackend(
                api_base=e["endpoint"],
                timeout=float(_os.environ.get("ROTA_LLM_TIMEOUT") or e["timeout"] or timeout),
                extra_body=e["extra_body"])
            for m, e in self.endpoints.items()})

    def check(self) -> list[str]:
        """What would fail on the first session, said before any database is
        touched: a missing key variable, a model the server does not have."""
        from . import keys
        problems: list[str] = []
        if self.api_key_env and keys.get(self.api_key_env) is None:
            problems.append(f"{self.api_key_env} is set neither in the environment "
                            f"nor in {keys.keys_path()}")
        if self.remote:
            problems.append(f"remote: prompts and the repository's code are sent to "
                            f"{self.endpoint} (AUDIT items 8 and 9)")
        wanted = sorted({m for m in {self.default_model, *self.roles.values()}
                         if m not in self.endpoints})
        if self.provider == "ollama":
            host = self.endpoint or llm.OLLAMA_HOST
            have = llm.available_models(host)
            if not have:
                problems.append(f"no ollama at {host}, or it has no models")
            else:
                for m in wanted:
                    if m not in have and m.split(":")[0] not in {h.split(":")[0] for h in have}:
                        problems.append(f"{m} is not pulled at {host}")
        else:
            for m in wanted:
                if "/" not in m:
                    problems.append(f"{m} names no provider; litellm wants provider/model, "
                                    f"e.g. ollama/{m} or anthropic/{m}")
        return problems


# -- finding and binding ---------------------------------------------------

def places(project_root: Path | None = None) -> list[Path]:
    out: list[Path] = []
    if project_root:
        out.append(Path(project_root) / ".rota" / "profiles")
    out.append(user_dir())
    out.append(SHIPPED)
    return out


def available(project_root: Path | None = None) -> list[tuple[str, str]]:
    seen: dict[str, str] = {}
    for d in places(project_root):
        if d.is_dir():
            for f in sorted(d.glob("*.toml")):
                seen.setdefault(f.stem, str(f))
    return sorted(seen.items())


def find(name: str, project_root: Path | None = None) -> Profile:
    for d in places(project_root):
        f = d / f"{name}.toml"
        if f.is_file():
            return Profile.from_toml(f)
    looked = ", ".join(str(d) for d in places(project_root))
    raise FileNotFoundError(f"no profile {name!r}; looked in {looked}")


def default_name() -> str:
    return os.environ.get("ROTA_PROFILE", "local")


def bind(conn, profile: Profile, *, author: str = "principal") -> None:
    """Freeze the profile into the run. The routing string is derived, so the
    runner's existing per-wake model choice keeps working unchanged."""
    from ..core import config

    config.set(conn, "profile", profile.to_dict(), author=author)
    config.set(conn, "model_routing", profile.routing(), author=author)


def of_run(conn) -> Profile | None:
    from ..core import config

    stored = config.get(conn, "profile")
    if not stored:
        return None
    return Profile.from_dict(stored, source="run")


def set_field(conn, dotted: str, value: str, *, author: str = "principal") -> Profile:
    """`rota profile set <run> models.tester=ollama/x`: a new snapshot with
    history. Values parse as JSON when they can, so numbers stay numbers."""
    current = of_run(conn)
    if current is None:
        raise ValueError("this run has no profile bound; onboard with --profile")
    d = current.to_dict()
    node = d
    parts = dotted.split(".")
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        parsed = value
    node[parts[-1]] = parsed
    fresh = Profile.from_dict(d, name=current.name, source="run")
    bind(conn, fresh, author=author)
    return fresh


def to_toml(p: "Profile") -> str:
    """The file a profile is, written back. Keys never sit here."""
    lines = [f'name = "{p.name}"', "", "[provider]", f'kind = "{p.provider}"']
    if p.endpoint:
        lines.append(f'endpoint = "{p.endpoint}"')
    if p.api_key_env:
        lines.append(f'key_env = "{p.api_key_env}"')
    lines.append(f"timeout = {int(p.timeout)}")
    if p.remote:
        lines.append("remote = true")
    lines += ["", "[pins]"]
    for key in PIN_KEYS:
        if p.pins.get(key) is not None:
            lines.append(f"{key} = {p.pins[key]}")
    lines += ["", "[models]", f'default = "{p.default_model}"']
    for role, model in sorted(p.roles.items()):
        lines.append(f'{role} = "{model}"')
    return chr(10).join(lines) + chr(10)


def write_user_profile(name: str, base: "Profile", default_model: str,
                       roles: dict[str, str], provider: str | None = None,
                       endpoint: str | None = None, key_env: str | None = None) -> Path:
    """A user profile under ~/.rota/profiles, copied from a shipped one with
    the models the setup screen chose (plans/model-setup.md, step 6). The
    modal writes user profiles only."""
    import dataclasses
    new = dataclasses.replace(
        base, name=name, default_model=default_model, roles=dict(roles),
        provider=provider or base.provider,
        endpoint=base.endpoint if endpoint is None else endpoint,
        api_key_env=base.api_key_env if key_env is None else key_env)
    path = user_dir() / f"{name}.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_toml(new), encoding="utf-8")
    return path

