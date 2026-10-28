"""Replay s145 turn 6 of night 86 through the runner's own backend.

The prior probe, `replay_turn.py`, sent one raw non-streamed `/api/chat`
call with no `num_predict`. `run_session` calls
`llm.OllamaBackend.complete(system, user, pins, tools=schemas)`, which
streams, sends `num_predict` from the pins, sends a resolved `think`, and
stops the stream on three repeated lines. This probe sends the runner's
call and compares the reply with the recorded completion.

Usage: replay_runner.py [recorded|think-on|no-num-predict|with-tools] ...
Each argument is one call. The default is one `recorded` call.
"""
import json
import os
import sqlite3
import sys
import time

# The live view writes a file, and this probe measures the request only.
os.environ.setdefault("ROTA_LIVE", "0")
# The brief allows 900 seconds per call. The backend reads this at build time.
os.environ.setdefault("ROTA_LLM_TIMEOUT", "900")
os.environ.setdefault("OLLAMA_HOST", "http://127.0.0.1:11434")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

import urllib.request  # noqa: E402

from rota.llm import llm  # noqa: E402

DB = ".rota/clickI_night86.db"
SID, SEQ = "s145", 6

# Every request body the backend sends, captured at `urllib.request.Request`.
SENT: list[dict] = []
_REAL_REQUEST = urllib.request.Request


class _Recording(_REAL_REQUEST):  # type: ignore[misc, valid-type]
    def __init__(self, url, data=None, *args, **kw):
        if data:
            try:
                SENT.append(json.loads(data.decode("utf-8")))
            except ValueError:
                pass
        super().__init__(url, data, *args, **kw)


urllib.request.Request = _Recording  # noqa: E305 -- the probe's whole point


class NoNumPredict(llm.OllamaBackend):
    """The runner's backend with `num_predict` left out of the options."""

    def options(self, pins):
        out = super().options(pins)
        out.pop("num_predict", None)
        return out


def load():
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    system, user, recorded = conn.execute(
        "select system, user, completion from turns where session_id=? and seq=?",
        (SID, SEQ)).fetchone()
    pins_json, model, temperature, num_ctx, prompt_hash, backend = conn.execute(
        "select pins_json, model, temperature, num_ctx, prompt_hash, backend "
        "from sessions where id=?", (SID,)).fetchone()
    return system, user, recorded, json.loads(pins_json), backend


def first_diff(a: str, b: str) -> int:
    """The first offset where the two texts differ, or -1 when one is a
    prefix of the other and the lengths match."""
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return -1 if len(a) == len(b) else min(len(a), len(b))


def show_diff(reply: str, recorded: str) -> None:
    off = first_diff(reply, recorded)
    if off < 0:
        print("  first differing offset: none, the reply equals the recording")
        return
    print(f"  first differing offset: {off}")
    lo, hi = max(0, off - 80), off + 80
    print(f"  reply   [{lo}:{hi}]: {reply[lo:hi]!r}")
    print(f"  record  [{lo}:{hi}]: {recorded[lo:hi]!r}")


def run(label: str, system: str, user: str, pins: llm.Pins, tools, backend) -> None:
    print(f"\n=== call: {label}")
    print(f"  pins: {pins.as_dict()}")
    print(f"  tools: {'none' if not tools else len(tools)}")
    before = len(SENT)
    t0 = time.time()
    try:
        completion = backend.complete(system, user, pins, tools=tools)
    except Exception as exc:  # noqa: BLE001 -- a probe reports every failure
        print(f"  ERROR {type(exc).__name__}: {str(exc)[:300]}")
        return
    elapsed = time.time() - t0
    body = SENT[before] if len(SENT) > before else {}
    print(f"  payload keys: {sorted(body)}")
    print(f"  payload think: {body.get('think')!r}  stream: {body.get('stream')!r}")
    print(f"  payload options: {body.get('options')}")
    raw = completion.raw or {}
    print(f"  reply chars: {len(completion.text)}  elapsed: {elapsed:.1f}s")
    print(f"  done_reason: {completion.done_reason!r}  done: {raw.get('done')!r}")
    print(f"  eval_count: {raw.get('eval_count')}  "
          f"prompt_eval_count: {raw.get('prompt_eval_count')}  "
          f"truncated: {completion.truncated}  "
          f"native tool calls: {len(completion.tool_calls)}")
    print(f"  first 200 chars: {completion.text[:200]!r}")
    show_diff(completion.text, RECORDED)
    text = completion.text
    print(f"  invented a result: {'OK code.source ->' in text or 'ERROR code.source ->' in text}  "
          f"wrote: {'TOOL: code.write' in text}  committed: {'TOOL: code.commit' in text}  "
          f"source calls: {text.count('TOOL: code.source')}  "
          f"says it cannot see: {any(w in text.lower() for w in ('cannot see', 'not visible', 'no longer', 'evicted', 'need to see', 'need the'))}")
    return text


system, user, RECORDED, pins_json, backend_name = load()
print(f"turn {SID} seq {SEQ}: system {len(system)} chars, user {len(user)} chars, "
      f"recorded completion {len(RECORDED)} chars, backend {backend_name!r}")
print(f"recorded pins_json: {pins_json}")
print(f"recorded completion head: {RECORDED[:200]!r}")

BASE = llm.Pins(
    model=pins_json["model"],
    temperature=pins_json["temperature"],
    num_ctx=pins_json["num_ctx"],
    prompt_hash=pins_json["prompt_hash"],
    max_tokens=pins_json["max_tokens"],
    top_p=pins_json["top_p"],
    seed=pins_json["seed"],
    repeat_penalty=pins_json["repeat_penalty"],
    think=pins_json["think"],
)
# The night's profile carried `native_tools: false`, so `run_session` built
# `schemas = None` and the backend sent no tools field.
TOOLS_AS_RECORDED = None

plain = llm.OllamaBackend()
print(f"backend host {plain.host}, timeout {plain.timeout:.0f}s, "
      f"max_tokens {plain.max_tokens}")

CALLS = {
    "recorded": lambda: run("recorded pins, think as pinned", system, user,
                            BASE, TOOLS_AS_RECORDED, plain),
    "think-on": lambda: run("think on", system, user,
                            __import__("dataclasses").replace(BASE, think=True),
                            TOOLS_AS_RECORDED, plain),
    "no-num-predict": lambda: run("no num_predict", system, user, BASE,
                                  TOOLS_AS_RECORDED, NoNumPredict()),
    # No "tools off" call: the night's profile set `native_tools: false`, so
    # the recorded call already carried no tools.
}

for name in (sys.argv[1:] or ["recorded"]):
    # `model=<name>` or `model=<name>:on|off` replays the same prompt on
    # another model through the same runner call, think as given or as pinned.
    if name.startswith("model="):
        spec = name[len("model="):]
        # An Ollama tag carries a colon, so only a trailing `:on` or `:off`
        # is the think flag. `gemma3:12b` is a model, `gemma3:12b:on` is a
        # model with thinking on.
        model, think = spec, BASE.think
        if spec.endswith((":on", ":off")):
            model, _, flag = spec.rpartition(":")
            think = flag == "on"
        pins = __import__("dataclasses").replace(BASE, model=model, think=think)
        run(f"model {model}, think {pins.think!r}", system, user, pins,
            TOOLS_AS_RECORDED, plain)
        continue
    CALLS[name]()
