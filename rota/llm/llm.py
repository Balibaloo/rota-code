"""
The `complete()` seam.

Everything model-shaped lives behind this one function. litellm is a *backend*,
not a dependency of the design: if it is absent, or the user swaps providers, the
rest of the system does not notice. That is also what makes cassette replay and
the mock backend drop-in rather than special cases.

Pins travel with every call and are recorded on the session. A result without its
pins is not a result — model id, temperature, num_ctx and prompt hash together
are what make a pass-rate history mean anything.

num_ctx deserves its own note: Ollama defaults it to a small value regardless of
what the model supports, so a working set budgeted at 8k would be silently
truncated and the failure would look like bad reasoning. It is set explicitly and
recorded as a pin.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Protocol

# Measured on the target box (RTX 3080, 10 GB) rather than assumed. At
# num_ctx=8192, warm round-trip: llama3.1:8b 0.2s, qwen2.5:7b 0.3s, qwen3.5:9b
# >100s — the 9B spills ~27% to CPU once its KV cache is allocated and stops
# being usable in a test loop. `gemma4:31b` needs about 20 GB and simply swaps.
# Bigger is not better when it does not fit, and "does it fit" is a fact about
# this machine, so it is measured here rather than argued about.
DEFAULT_MODEL = os.environ.get("ROTA_MODEL", "llama3.1:8b")

# 12k rather than 8k. The working set is pushed rather than fetched, and pushing
# everything a role can read without being told anything — which is what makes
# Critic able to review at all — put the largest prompts at ~9.2k tokens,
# *above* the old window. They were being truncated from the front, silently,
# and the front is the system prompt: the role losing its instructions is the
# one failure that looks exactly like the role ignoring them.
DEFAULT_NUM_CTX = int(os.environ.get("ROTA_NUM_CTX", "12288"))
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


@dataclass(frozen=True)
class Pins:
    model: str = DEFAULT_MODEL
    temperature: float = 0.0
    num_ctx: int = DEFAULT_NUM_CTX
    prompt_hash: str = ""

    def with_prompt(self, prompt: str) -> "Pins":
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
        return Pins(self.model, self.temperature, self.num_ctx, digest)

    def as_dict(self) -> dict:
        return {
            "model": self.model, "temperature": self.temperature,
            "num_ctx": self.num_ctx, "prompt_hash": self.prompt_hash,
        }


@dataclass
class NativeCall:
    """A tool call the provider parsed for us. No marker to drop, no text to
    misparse — the failure class that cost the most with small models."""
    name: str
    args: dict


@dataclass
class Completion:
    text: str
    pins: Pins
    backend: str = ""
    raw: dict = field(default_factory=dict)
    tool_calls: list = field(default_factory=list)   # list[NativeCall]
    # The prompt did not fit and the provider dropped the overflow. Carried on
    # the completion because there is nowhere else it could be noticed: a
    # session briefed with half its instructions behaves exactly like a session
    # ignoring them, and no assertion can tell those apart.
    truncated: bool = False
    prompt_tokens: int = 0

    @property
    def used_native_tools(self) -> bool:
        return bool(self.tool_calls)


class Backend(Protocol):
    name: str

    def complete(self, system: str, user: str, pins: Pins,
                 tools: list | None = None) -> Completion: ...


class OllamaBackend:
    """
    Direct HTTP to Ollama.

    Deliberately not routed through litellm: this is a local, single-provider,
    no-auth call, and a dependency-free path means the runner still works when
    the optional backend is missing. litellm earns its place when a hosted
    provider appears.
    """

    name = "ollama"

    # A turn emits a handful of tool calls. Anything past this is a model that
    # has started narrating and will keep going until the context is full —
    # which presents as a 300-second hang rather than as a bad answer, and cost
    # two L1 cases their whole run before it was capped. Deliberately generous:
    # a cap that is never reached changes no output, and one that is reached has
    # already told you something went wrong.
    #
    # Not a `Pins` field on purpose. Pins identify what was asked, and every
    # cassette is keyed by them; a guard rail on runaway generation is a
    # property of the transport, and putting it in the key would invalidate
    # every recording in the repository to record the same completions again.
    max_tokens = 2048

    def __init__(self, host: str = OLLAMA_HOST, timeout: float = 300.0):
        self.host = host.rstrip("/")
        self.timeout = timeout

    def complete(self, system: str, user: str, pins: Pins,
                 tools: list | None = None) -> Completion:
        payload = {
            "model": pins.model,
            "stream": False,
            "options": {"temperature": pins.temperature, "num_ctx": pins.num_ctx,
                        "num_predict": self.max_tokens},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if tools:
            payload["tools"] = tools
        req = urllib.request.Request(
            f"{self.host}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except TimeoutError as exc:
            # Raised bare by the socket layer rather than wrapped, so without
            # this it surfaced as `session failed: TimeoutError` — a bug report
            # against the system for something the model did.
            raise LLMUnavailable(
                f"ollama at {self.host}: no answer in {self.timeout:.0f}s") from exc
        except urllib.error.URLError as exc:
            raise LLMUnavailable(f"ollama at {self.host}: {exc}") from exc

        # Ollama reports how much of the prompt it actually evaluated. When that
        # reaches the window the rest was dropped, and nothing else here would
        # ever say so — the session just behaves as though it had been briefed
        # differently, which is indistinguishable from a role misbehaving.
        used = body.get("prompt_eval_count") or 0
        truncated = used >= pins.num_ctx * 0.98

        message = body.get("message", {}) or {}
        native = []
        for call in message.get("tool_calls") or []:
            fn = call.get("function", {}) or {}
            args = fn.get("arguments")
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}
            native.append(NativeCall(name=fn.get("name", ""), args=args or {}))

        return Completion(
            text=message.get("content", ""),
            pins=pins, backend=self.name, raw=body, tool_calls=native,
            truncated=truncated, prompt_tokens=used,
        )


class LiteLLMBackend:
    """Optional. Present so swapping providers is a config change, not a rewrite."""

    name = "litellm"

    def complete(self, system: str, user: str, pins: Pins,
                 tools: list | None = None) -> Completion:
        import litellm  # imported lazily: absence must not break the runner

        resp = litellm.completion(
            model=f"ollama/{pins.model}" if "/" not in pins.model else pins.model,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            temperature=pins.temperature,
            num_ctx=pins.num_ctx,
        )
        return Completion(text=resp.choices[0].message.content, pins=pins,
                          backend=self.name, raw={})


class ScriptedBackend:
    """Canned completions for T0. Deterministic by construction."""

    name = "scripted"

    def __init__(self, script: list[str]):
        self.script = list(script)
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, user: str, pins: Pins,
                 tools: list | None = None) -> Completion:
        self.calls.append((system, user))
        self.tools_offered = tools
        text = self.script.pop(0) if self.script else ""
        return Completion(text=text, pins=pins, backend=self.name)


class LLMUnavailable(RuntimeError):
    """Infrastructure failure, not a semantic one — the caller counts an attempt."""


def default_backend() -> Backend:
    return OllamaBackend()


def supports_tools(model: str, host: str = OLLAMA_HOST) -> bool:
    """
    Whether this model advertises tool support.

    Asked rather than assumed: a model without it silently ignores the `tools`
    field and answers in prose, which would look like a reasoning failure. When
    it is absent we fall back to the `TOOL:` text protocol, which is exactly what
    that protocol is for.
    """
    try:
        req = urllib.request.Request(
            f"{host}/api/show",
            data=json.dumps({"model": model}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return "tools" in (body.get("capabilities") or [])
    except Exception:
        return False


def available_models(host: str = OLLAMA_HOST) -> list[str]:
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=5) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return [m["name"] for m in body.get("models", [])]
    except Exception:
        return []
