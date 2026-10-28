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
from pathlib import Path
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
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")

# Reasoning-by-default models (the qwen3 family) burn invisible tokens at the
# acting register's expense -- measured at 0.1 visible tok/s on the bench. The
# system speaks in acts, so thinking is off unless a profile turns it on. A
# template that ignores the flag is unharmed. This is the value the wire
# carries when nobody pins one, so it is also the value the key must carry.
THINK_DEFAULT = False


def think_for(model: str, root: Path | None = None) -> bool:
    """
    The think pin this run sends for this model: the profile's, or
    `THINK_DEFAULT`.

    `root` is the project root the profile is looked up under, and it reaches
    `profile.find` unchanged. `rota.cli` passes one, because a profile can
    live in `<project>/.rota/profiles`. A caller that passes none keeps the
    ambient lookup, which is what the tiers want.

    The key must carry the value the wire carries. Until frame 65 this
    returned None when no profile named the model, `extras()` dropped the None,
    and the key then recorded the field as absent while the backend still sent
    a value. Absent is not a value, so a recording made under one server
    default replayed against another and the register could not tell the two
    apart.

    `ROTA_MODEL` and `ROTA_NUM_CTX` above are read once at import. This third
    ambient variable is read per call, because a profile is a file the caller
    can name at any time.

    One definition, and it is the reason this lives here rather than in the
    tier that first wrote it. The tier stamps a recording with this pin and
    `rota.tools.casestatus` matches a recording on it. Two copies of the rule
    drift, and a drifted pin reads every case as stale.

    Finding 81 (2026-09-15): qwen3.5:9b answers a Tester wake with prose and no
    call when thinking is off, so the nights run that model with thinking on. A
    recording made under the profile measures that model, and a recording made
    without one keeps its old key.
    """
    name = os.environ.get("ROTA_PROFILE")
    if not name:
        return THINK_DEFAULT
    from . import profile as profile_mod

    pinned = (profile_mod.find(name, root).think or {}).get(model)
    return THINK_DEFAULT if pinned is None else pinned


def profile_pins(root: Path | None = None) -> dict:
    """
    The `ROTA_PROFILE` profile's pins that a register run carries.

    `max_tokens` always joins. `num_ctx` joins only when `ROTA_NUM_CTX` is
    unset, because the variable wins over the file. Frame 323's trial set
    `max_tokens = 2048` in its profile, and Ollama still got 8192, because
    the suite built its pins without the profile. Both pins are in the
    cassette key, so a capped recording never answers an uncapped run.
    """
    name = os.environ.get("ROTA_PROFILE")
    if not name:
        return {}
    from . import profile as profile_mod

    pins = profile_mod.find(name, root).pins or {}
    out: dict = {}
    if pins.get("max_tokens") is not None:
        out["max_tokens"] = int(pins["max_tokens"])
    if pins.get("num_ctx") is not None and not os.environ.get("ROTA_NUM_CTX"):
        out["num_ctx"] = int(pins["num_ctx"])
    return out


@dataclass(frozen=True)
class Pins:
    """
    Every setting that can change a model's reply, and nothing else.

    The first three are the original pins and key every recording ever
    made. The rest are optional: `None` means the provider's own default,
    and a pin at `None` stays out of the cassette key, so a recording made
    before the field existed keeps its key. A pin that is set changes the
    key, which is the point of a pin.

    `think` is the one exception, from frame 65 (2026-09-23). Both backends
    send `THINK_DEFAULT` for a `None`, so `None` is never the provider's own
    default on the wire. The tiers pass a value through `think_for` and never
    pass `None`, which keeps the key and the wire at one value.
    """
    model: str = DEFAULT_MODEL
    temperature: float = 0.0
    num_ctx: int = DEFAULT_NUM_CTX
    prompt_hash: str = ""
    max_tokens: int | None = None
    top_p: float | None = None
    seed: int | None = None
    repeat_penalty: float | None = None
    # Thinking on or off. The tiers never pass None here, because `think_for`
    # resolves the pin to a value. Any other caller may still pass None, and
    # the backend then sends `THINK_DEFAULT`.
    # Finding 81 (2026-09-15): qwen3.5:9b on the 3080 with thinking off
    # answered a Tester wake with 34k characters of prose and no call, and
    # with thinking on in ten calls; on the Titan it works either way.
    think: bool | None = None

    def with_prompt(self, prompt: str) -> "Pins":
        import dataclasses
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
        return dataclasses.replace(self, prompt_hash=digest)

    def as_dict(self) -> dict:
        return {
            "model": self.model, "temperature": self.temperature,
            "num_ctx": self.num_ctx, "prompt_hash": self.prompt_hash,
            "max_tokens": self.max_tokens, "top_p": self.top_p,
            "seed": self.seed, "repeat_penalty": self.repeat_penalty,
            "think": self.think,
        }

    def extras(self) -> dict:
        """The optional pins that are set. Empty for the original three."""
        return {k: v for k, v in (("max_tokens", self.max_tokens),
                                  ("top_p", self.top_p), ("seed", self.seed),
                                  ("repeat_penalty", self.repeat_penalty),
                                  ("think", self.think))
                if v is not None}

    def check(self) -> "Pins":
        """Refuse a value no provider could honour. Returns self."""
        if self.temperature < 0:
            raise ValueError(f"temperature must be >= 0, not {self.temperature}")
        if self.num_ctx <= 0:
            raise ValueError(f"num_ctx must be > 0, not {self.num_ctx}")
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError(f"max_tokens must be > 0, not {self.max_tokens}")
        if self.top_p is not None and not (0 < self.top_p <= 1):
            raise ValueError(f"top_p must satisfy 0 < top_p <= 1, not {self.top_p}")
        return self


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
    # What the prompt was before the server cut it, in tokens, estimated from
    # its characters. The evaluated count alone misleads: a cut prompt reports
    # half the window, which reads as comfortably inside it.
    prompt_estimate: int = 0

    @property
    def used_native_tools(self) -> bool:
        return bool(self.tool_calls)

    @property
    def done_reason(self) -> str:
        """Why the stream stopped: "length", "invented_result", "repeating",
        or "" when nobody recorded the reason.

        This is the one reader of the stop. A cassette replay carries the
        reason in `raw` as the live call does, so a replayed night fires the
        same rules as the live night (frame 233).
        """
        return str((self.raw or {}).get("done_reason") or "")


class Backend(Protocol):
    name: str

    def complete(self, system: str, user: str, pins: Pins,
                 tools: list | None = None) -> Completion: ...


# Where the live view is written. One file, overwritten at the start of every
# model call: the pins, the system prompt, the user prompt, then the completion
# as it streams in. `ROTA_LIVE=0` turns it off; `ROTA_LIVE=<path>` moves it.
# The historical record is the `turns` table; this is the present tense.
LIVE_PATH = os.environ.get("ROTA_LIVE", "")


class LiveView:
    """The current model call, as a file a person can keep open."""

    def __init__(self, path):
        self.path = path
        self._buf: list[str] = []
        self._since_flush = 0

    @classmethod
    def open(cls, pins: "Pins", system: str, user: str) -> "LiveView":
        import time

        if LIVE_PATH == "0":
            return cls(None)
        try:
            from .. import paths
            target = (Path(LIVE_PATH) if LIVE_PATH
                      else paths.REPO / ".rota" / "live.md")
            target.parent.mkdir(parents=True, exist_ok=True)
        except Exception:                                   # pragma: no cover
            return cls(None)
        view = cls(target)
        head = (f"# live — {time.strftime('%H:%M:%S')}  model={pins.model}  "
                f"temp={pins.temperature}  num_ctx={pins.num_ctx}\n\n"
                f"## system prompt\n\n{system}\n\n"
                f"## user prompt\n\n{user}\n\n"
                f"## completion (streaming)\n\n")
        view._write(head, mode="w")
        return view

    def _write(self, text: str, mode: str = "a") -> None:
        if self.path is None:
            return
        try:
            with open(self.path, mode, encoding="utf-8") as f:
                f.write(text)
        except OSError:                                     # pragma: no cover
            self.path = None

    def token(self, text: str) -> None:
        if self.path is None or not text:
            return
        self._buf.append(text)
        self._since_flush += len(text)
        if self._since_flush >= 80 or "\n" in text:
            self.flush()

    def flush(self) -> None:
        if self._buf:
            self._write("".join(self._buf))
            self._buf, self._since_flush = [], 0

    def close(self, how: str) -> None:
        if self.path is None:
            return
        self.flush()
        self._write(f"\n\n---\n[{how}]\n")


def _cycling(lines: list[str]) -> bool:
    """Three copies of one line, or of one cycle of two to sixteen lines, at
    the tail. Short lines (a bare bracket, a blank marker) never count."""
    for k in range(1, 17):
        if len(lines) < 3 * k:
            break
        tail = lines[-3 * k:]
        a, b, c = tail[:k], tail[k:2 * k], tail[2 * k:]
        if a == b == c and all(len(l) > (40 if k == 1 else 20) for l in a):
            return True
    return False


def _consume_stream(lines, live: "LiveView", deadline: float | None = None) -> dict:
    """
    Join Ollama's streamed `/api/chat` chunks into the one body the
    non-streaming form returned: the content concatenated, the tool calls
    collected, and the final chunk's counters kept. Each content chunk goes to
    the live view as it arrives.
    """
    content: list[str] = []
    tool_calls: list = []
    final: dict = {}
    # A completion that repeats itself line for line is a fixed point, and at
    # temperature zero it runs to `num_predict`. Measured on qwen2.5:14b,
    # partially offloaded: one survey turn wrote the same `glossary.amend(...)`
    # line nineteen times -- 9,843 characters, 623 seconds -- then attested on
    # the next turn as if nothing had happened. The third identical line is
    # enough to know; the stream is left there and the connection's close
    # stops the generation. What was produced is kept, and the parser sees
    # three identical calls, which dispatch as one write and two "unchanged".
    line_buf, last_lines, stopped = "", [], False
    # A reply that writes a call and then the call's result for itself has
    # stopped acting. Night 145 (frame 232): 20 such turns ran 104k tokens past
    # the invented line. The runner runs nothing after that line (rule 1 of
    # frame 77), so the stream ends at its head. The head is tested before the
    # line ends, because s117#4 wrote one result line of 8,269 tokens.
    saw_tool = False
    from .toolproto import INVENTED_RESULT, MARKER
    import time as _time
    for raw in lines:
        # The socket timeout guards a silent connection; a stream that keeps
        # trickling never trips it. Night 27 and seat1 (2026-09-12): one
        # generation held a card for two hours on the 3080 and twenty-five
        # minutes on the Titan. The wall clock is the other guard.
        if deadline is not None and _time.monotonic() > deadline:
            live.token("\n[stopped: the reply ran past the time allowed]\n")
            raise TimeoutError("the streamed reply ran past the time allowed")
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", "replace")
        raw = raw.strip()
        if not raw:
            continue
        try:
            chunk = json.loads(raw)
        except json.JSONDecodeError:
            continue
        msg = chunk.get("message") or {}
        piece = msg.get("content") or ""
        if piece:
            content.append(piece)
            live.token(piece)
            line_buf += piece
            invented = False
            while "\n" in line_buf:
                done_line, line_buf = line_buf.split("\n", 1)
                if done_line.strip():
                    last_lines = (last_lines + [done_line.strip()])[-48:]
                if saw_tool and INVENTED_RESULT.match(done_line):
                    invented = True
                    break
                if MARKER in done_line:
                    saw_tool = True
            if invented or (saw_tool and INVENTED_RESULT.match(line_buf)):
                stopped = "invented"
                live.token("\n[stopped: the reply wrote a tool result it was not given]\n")
                break
            # The same line three times, or the same cycle of up to eight
            # lines three times. clickI night 40 (2026-09-13): a reconcile
            # reply cycled five `code.source` calls for 84 seconds to the
            # output cap, 24,000 characters, and the cut note then blamed
            # the reply's length. A cycle of substantial lines repeated
            # three times is a fact about the stream.
            if _cycling(last_lines):
                stopped = "repeating"
                live.token("\n[stopped: the same lines three times over]\n")
                break
        for call in msg.get("tool_calls") or []:
            tool_calls.append(call)
            fn = (call.get("function") or {})
            live.token(f"\n[tool call] {fn.get('name', '')}({json.dumps(fn.get('arguments', {}))[:400]})\n")
        if chunk.get("done"):
            final = chunk
    final = dict(final)
    final["message"] = {"role": "assistant", "content": "".join(content),
                        "tool_calls": tool_calls}
    # Never "length" for a stop: the runner reads "length" as the output cap
    # and sends the seat a cut note.
    if stopped == "invented":
        final["done_reason"] = "invented_result"
    elif stopped:
        final["done_reason"] = "repeating"
    return final


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
    max_tokens = 8192

    def __init__(self, host: str = OLLAMA_HOST, timeout: float | None = None):
        self.host = host.rstrip("/")
        # The slow card cannot finish a cap-length reply in 300 s: at 27
        # tok/s, 8192 tokens is five minutes, and tipsBB and tipsBC lost
        # Tester turns to the timeout three times each (2026-09-13). The
        # walk that runs there sets ROTA_LLM_TIMEOUT.
        self.timeout = float(timeout if timeout is not None
                             else os.environ.get("ROTA_LLM_TIMEOUT") or 300.0)

    def options(self, pins: Pins) -> dict:
        """The request options from the pins. An unset pin is absent, so the
        request for the original three pins is byte-identical to before."""
        out = {"temperature": pins.temperature, "num_ctx": pins.num_ctx,
               "num_predict": pins.max_tokens or self.max_tokens}
        for key in ("top_p", "seed", "repeat_penalty"):
            value = getattr(pins, key)
            if value is not None:
                out[key] = value
        return out

    def complete(self, system: str, user: str, pins: Pins,
                 tools: list | None = None) -> Completion:
        payload = {
            "model": pins.model,
            # Streamed, so the live file can show the completion as it is
            # generated. The return value is unchanged: the chunks are joined
            # into the same `Completion` the non-streaming form produced.
            "stream": True,
            # `THINK_DEFAULT` carries the reason thinking is off by default.
            # A caller outside the tiers may pass None, so the value is
            # resolved here as well as in `think_for`.
            "think": pins.think if pins.think is not None else THINK_DEFAULT,
            "options": self.options(pins),
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
        live = LiveView.open(pins, system, user)
        try:
            import threading as _th
            import time as _time
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                # A watchdog from outside the reader. tipsAZ (2026-09-13):
                # a Tester turn held the Titan for seven hours with the
                # stream deadline in place, so the wait was not in the chunk
                # loop. Shutting the socket from another thread unblocks any
                # read, and the reader reports the timeout as before.
                def _cut():
                    try:
                        resp.fp.raw._sock.shutdown(2)  # noqa: SLF001 -- the only handle
                    except Exception:  # noqa: BLE001 -- already closed, or no socket
                        pass
                dog = _th.Timer(self.timeout * 2, _cut)
                dog.daemon = True
                dog.start()
                try:
                    body = _consume_stream(iter(resp), live,
                                           deadline=_time.monotonic() + self.timeout)
                finally:
                    dog.cancel()
        except TimeoutError as exc:
            # Raised bare by the socket layer rather than wrapped, so without
            # this it surfaced as `session failed: TimeoutError` — a bug report
            # against the system for something the model did.
            live.close("timed out")
            raise LLMUnavailable(
                f"ollama at {self.host}: no answer in {self.timeout:.0f}s") from exc
        except urllib.error.URLError as exc:
            live.close(f"unreachable: {exc}")
            raise LLMUnavailable(f"ollama at {self.host}: {exc}") from exc
        live.close("done")

        # Ollama reports how much of the prompt it actually evaluated. When that
        # reaches the window the rest was dropped, and nothing else here would
        # ever say so — the session just behaves as though it had been briefed
        # differently, which is indistinguishable from a role misbehaving.
        used = body.get("prompt_eval_count") or 0
        # The server can also cut from the front and report a count far below
        # the window. Ollama collapses any prompt over `num_ctx` to
        # `num_ctx / 2 + 2` and keeps the tail, so a 17,220 token prompt on a
        # 12,288 window reports 6,146 and the brief is the part that is gone
        # (measured 2026-09-18 on both servers at three window sizes; finding
        # 79 in `plans/operating-facts.md`). An estimate of the prompt's
        # tokens against the window catches that shape. The measured ratio is
        # 3.97 characters to the token for these models.
        estimate = int((len(system) + len(user)) / 3.97)
        truncated = used >= pins.num_ctx * 0.98 or estimate > pins.num_ctx

        message = body.get("message", {}) or {}
        native = []
        for call in message.get("tool_calls") or []:
            fn = call.get("function", {}) or {}
            args = fn.get("arguments")
            if isinstance(args, str):
                # Bad JSON stays a string, so the runner refuses the call by
                # name and does not run it with no arguments (frame 323).
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    pass
            native.append(NativeCall(name=fn.get("name", ""),
                                     args={} if args is None else args))

        return Completion(
            text=message.get("content", ""),
            pins=pins, backend=self.name, raw=body, tool_calls=native,
            truncated=truncated, prompt_tokens=used, prompt_estimate=estimate,
        )


class LiteLLMBackend:
    """
    Every provider that is not local Ollama: OpenAI, Anthropic, an
    OpenAI-compatible server such as llama.cpp, or Ollama through LiteLLM.

    Optional import, so its absence never breaks the runner. Portable pins
    only: `num_ctx` is an Ollama option and stays as provenance, and
    `repeat_penalty` is refused rather than dropped, because a setting that
    silently does nothing contaminates a comparison.
    """

    name = "litellm"
    default_max_tokens = 8192

    def __init__(self, api_base: str | None = None, timeout: float = 300.0,
                 extra_body: dict | None = None):
        self.api_base = api_base or None
        self.timeout = timeout
        # A profile's per-endpoint body, under the environment's (below).
        self.extra_body = dict(extra_body or {})

    def kwargs(self, system: str, user: str, pins: Pins,
               tools: list | None = None) -> dict:
        """The completion call, as keyword arguments. Testable without the library."""
        if pins.repeat_penalty is not None:
            raise ValueError(
                "repeat_penalty is an Ollama option and LiteLLM has no portable "
                "equivalent; unset it for this provider rather than have it "
                "silently ignored")
        out = {
            "model": f"ollama/{pins.model}" if "/" not in pins.model else pins.model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "temperature": pins.temperature,
            "max_tokens": pins.max_tokens or self.default_max_tokens,
            "timeout": self.timeout,
        }
        if pins.top_p is not None:
            out["top_p"] = pins.top_p
        if pins.seed is not None:
            out["seed"] = pins.seed
        if tools:
            out["tools"] = tools
        import os as _os
        if self.api_base:
            out["api_base"] = self.api_base
            # LiteLLM refuses an `openai/` call with no key even at a local
            # server that checks none. Night 61 (2026-09-14) died at the
            # Developer's first wake on "Missing credentials". A key in the
            # environment wins; a local endpoint gets a placeholder.
            if not _os.environ.get("OPENAI_API_KEY"):
                out["api_key"] = "local"
        # Provider-side knobs the API does not name: ROTA_LLM_EXTRA_BODY is a
        # JSON object merged into the request body. A llama-server takes
        # {"chat_template_kwargs": {"enable_thinking": false}} to keep a
        # thinking model's words in `content` (gemma-4, 2026-09-14: the
        # reply sat in `reasoning_content` and the runner read nothing).
        import os as _os
        named = {**self.extra_body,
                 **(json.loads(_os.environ.get("ROTA_LLM_EXTRA_BODY") or "{}"))}
        # The think pin, on the wire. The cassette key carries this value
        # (frame 65, 2026-09-23), so the body has to carry the same one or the
        # recording measures a server default nobody wrote down. The Ollama
        # backend sends `think`, and an OpenAI-shaped endpoint reads the same
        # switch under `chat_template_kwargs`.
        body: dict = {"chat_template_kwargs": {
            "enable_thinking": pins.think if pins.think is not None
            else THINK_DEFAULT}}
        # The caller's own body sits on top, key by key. A profile or
        # `ROTA_LLM_EXTRA_BODY` that names `enable_thinking` means it, and the
        # pin is only the value beneath it.
        for key, value in named.items():
            if key == "chat_template_kwargs" and isinstance(value, dict):
                body[key] = {**body[key], **value}
            else:
                body[key] = value
        out["extra_body"] = body
        return out

    def complete(self, system: str, user: str, pins: Pins,
                 tools: list | None = None) -> Completion:
        import litellm  # imported lazily: absence must not break the runner

        try:
            resp = litellm.completion(**self.kwargs(system, user, pins, tools))
        except Exception as exc:  # noqa: BLE001 -- the provider's own error class varies
            raise LLMUnavailable(f"litellm ({pins.model}): {exc}") from exc
        message = resp.choices[0].message
        calls = [NativeCall(name=c.function.name,
                            args=_native_args(c.function.arguments))
                 for c in (getattr(message, "tool_calls", None) or [])]
        return Completion(text=message.content or "", pins=pins,
                          backend=self.name, raw={}, tool_calls=calls)


def _native_args(text):
    """The arguments of a native call. Bad JSON stays a string, so the
    runner refuses the call by name and does not run it empty (frame 323)."""
    try:
        return json.loads(text or "{}")
    except (TypeError, ValueError):
        return text


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


class RoutedBackend:
    """
    One backend per model, chosen by the pins of each call.

    A profile names a model per desk, and until 2026-09-14 every desk had to
    reach its model through one server. The five-act benchmark put the
    Developer's act on gemma-4 behind a llama-server while the other desks
    stay on Ollama, so a profile now maps a model to its own endpoint and
    this backend sends each call where its model lives. The default takes
    every model the map does not name.
    """

    name = "routed"

    def __init__(self, default: Backend, by_model: dict[str, Backend]):
        self.default = default
        self.by_model = dict(by_model)

    def for_model(self, model: str) -> Backend:
        return self.by_model.get(model, self.default)

    def complete(self, system: str, user: str, pins: Pins,
                 tools: list | None = None) -> Completion:
        return self.for_model(pins.model).complete(system, user, pins, tools)


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
