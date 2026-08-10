"""
Which local models honour native tool calls, and what they cost.

The question is not "does the model card claim tool support" — all four claim it.
It is whether, given a role's actual brief and a fixture where exactly one call
is right, the model emits a structured call rather than prose about calling.

Spill is acceptable: correctness first, latency recorded. The same fixture is
put to every model, and to each model twice — once with native tools, once with
the `TOOL:` text protocol — because those are different evidence about different
things and a cassette of one is not evidence about the other.

    python -m rota.tools.probe_tools [--runs 3]
"""
from __future__ import annotations

import json
import statistics
import sys
import time
import urllib.error
import urllib.request

OLLAMA = "http://localhost:11434"

# One real operation, with the enum the sandbox validates. Gatekeeper asserting
# a scope item is the simplest thing any role does.
TOOLS = [{
    "type": "function",
    "function": {
        "name": "problem_assert",
        "description": "Record one item in the problem statement.",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "the item id to use"},
                "text": {"type": "string", "description": "what the software must do"},
                "kind": {"type": "string", "enum": ["in_scope", "out_of_scope"]},
            },
            "required": ["id", "text", "kind"],
        },
    },
}]

SYSTEM_NATIVE = (
    "You are Gatekeeper. You own the problem statement: what this software is "
    "for and what it is not for.\n\n"
    "A ratified statement has arrived. Record what it means for scope using the "
    "tool provided. Use the tool — do not describe what you would do."
)

SYSTEM_TEXT = (
    "You are Gatekeeper. You own the problem statement: what this software is "
    "for and what it is not for.\n\n"
    "A ratified statement has arrived. Record what it means for scope.\n\n"
    "Your working set is exactly these functions. Nothing else exists:\n"
    "  TOOL: problem.assert(id, text, kind='in_scope')\n\n"
    "Call one per line, in this form:\n"
    "  TOOL: artefact.verb(key='value')\n"
    "Emit no tool calls when you are done."
)

USER = ("Ratified statement s1: \"users can delete their account\".\n"
        "Record it as item i1.")


def chat(model: str, system: str, user: str, *, tools=None, num_ctx=8192,
         timeout=900) -> tuple[dict, float]:
    body = {
        "model": model, "stream": False,
        "options": {"temperature": 0, "num_ctx": num_ctx},
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
    }
    if tools:
        body["tools"] = tools
    req = urllib.request.Request(
        f"{OLLAMA}/api/chat", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read()), time.time() - t0


def graded_native(reply: dict) -> tuple[bool, str]:
    """A structured call, named right, with a legal enum."""
    calls = (reply.get("message") or {}).get("tool_calls") or []
    if not calls:
        return False, "no tool_calls"
    fn = calls[0].get("function", {})
    if fn.get("name") != "problem_assert":
        return False, f"called {fn.get('name')!r}"
    args = fn.get("arguments") or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            return False, "arguments not JSON"
    if args.get("kind") not in ("in_scope", "out_of_scope"):
        return False, f"kind={args.get('kind')!r}"
    if not args.get("id") or not args.get("text"):
        return False, "missing id or text"
    return True, "ok"


def graded_text(reply: dict) -> tuple[bool, str]:
    """The same judgement against the `TOOL:` protocol, using the real parser."""
    from ..llm.toolproto import extract

    from ..llm.toolproto import ToolCall

    text = (reply.get("message") or {}).get("content") or ""
    calls = [c for c in extract(text) if isinstance(c, ToolCall)]
    if not calls:
        return False, "no TOOL: line"
    call = calls[0]
    if call.name != "problem.assert":
        return False, f"called {call.name!r}"
    if call.args.get("kind") not in ("in_scope", "out_of_scope", None):
        return False, f"kind={call.args.get('kind')!r}"
    if not call.args.get("id") or not call.args.get("text"):
        return False, "missing id or text"
    return True, "ok"


def probe(model: str, runs: int) -> list[dict]:
    out = []
    for protocol, system, tools, grade in (
        ("native", SYSTEM_NATIVE, TOOLS, graded_native),
        ("text", SYSTEM_TEXT, None, graded_text),
    ):
        oks, secs, notes = 0, [], []
        for _ in range(runs):
            try:
                reply, dt = chat(model, system, USER, tools=tools)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                notes.append(str(exc)[:40])
                continue
            ok, why = grade(reply)
            oks += ok
            secs.append(dt)
            if not ok:
                notes.append(why)
        out.append({
            "model": model, "protocol": protocol,
            "honoured": f"{oks}/{runs}",
            "median_s": round(statistics.median(secs), 1) if secs else None,
            "notes": "; ".join(sorted(set(notes))[:2]),
        })
    return out


def main() -> None:
    runs = 3
    if "--runs" in sys.argv:
        runs = int(sys.argv[sys.argv.index("--runs") + 1])

    with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=10) as r:
        tags = json.loads(r.read())
    models = [m["name"] for m in sorted(tags["models"], key=lambda m: m["size"])
              if "embed" not in m["name"]]

    print(f"{runs} runs per model per protocol, same fixture throughout\n")
    print(f"{'model':22} {'protocol':9} {'honoured':9} {'median':>8}  notes")
    print("-" * 74)
    rows = []
    for model in models:
        for row in probe(model, runs):
            rows.append(row)
            median = f"{row['median_s']}s" if row["median_s"] else "-"
            print(f"{row['model']:22} {row['protocol']:9} {row['honoured']:9} "
                  f"{median:>8}  {row['notes']}")
    print()
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    sys.exit(main())
