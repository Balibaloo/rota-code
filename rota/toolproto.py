"""
The `TOOL:` text protocol.

Salvaged from Custom_AI_TUI's ChatController (the scanner's quote/paren tracking
is sound and hard-won) and rewritten around dotted names, pydantic validation and
explicit error results.

Doctrine: a malformed call must produce an *error*, never a misparse. A model that
writes garbage should be told so and given another turn; a model whose garbage is
silently reinterpreted as a different valid call is how a role writes something
nobody asked for.

Form:
    TOOL: artefact.verb(key='value', other=3)
    TOOL: artefact.verb({"key": "value"})

Both are accepted because small local models drift between them mid-session.
"""
from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from typing import Any

MARKER = "TOOL:"


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: dict[str, Any]
    raw: str = ""


@dataclass(frozen=True)
class ToolError:
    raw: str
    reason: str


def parse_args(args_str: str) -> dict[str, Any]:
    """
    Parse the argument list. JSON object form, or Python keyword form.

    Keyword form goes through `ast.literal_eval`, never `eval`: the argument list
    of an LLM-authored tool call is untrusted input.
    """
    args_str = args_str.strip()
    if not args_str:
        return {}

    if args_str.startswith("{"):
        parsed = json.loads(args_str)
        if not isinstance(parsed, dict):
            raise ValueError("JSON tool arguments must be an object")
        return parsed

    # Newlines inside an unquoted argument list would break the expression, so
    # they are escaped before parsing and restored by literal_eval.
    safe = args_str.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")
    expr = ast.parse(f"_f({safe})", mode="eval")
    call = expr.body
    if not isinstance(call, ast.Call):
        raise ValueError("not a call expression")
    if call.args:
        raise ValueError("positional arguments are not supported; use key=value")

    out: dict[str, Any] = {}
    for kw in call.keywords:
        if kw.arg is None:
            raise ValueError("**kwargs is not supported")
        out[kw.arg] = ast.literal_eval(kw.value)
    return out


def _scan_name(text: str, i: int) -> tuple[str, int]:
    start = i
    while i < len(text) and (text[i].isalnum() or text[i] in "_."):
        i += 1
    return text[start:i], i


def extract(text: str) -> list[ToolCall | ToolError]:
    """
    Find every `TOOL:` call in a completion, in order.

    Quote- and paren-aware, so an argument containing `)` or a nested call does
    not truncate the scan. Anything that cannot be parsed becomes a ToolError
    carrying the raw text — the model sees its own mistake.
    """
    results: list[ToolCall | ToolError] = []
    cursor = 0

    while True:
        marker = text.find(MARKER, cursor)
        if marker == -1:
            return results

        i = marker + len(MARKER)
        while i < len(text) and text[i].isspace():
            i += 1

        name, i = _scan_name(text, i)
        if not name:
            results.append(ToolError(text[marker:marker + 60], "no function name after TOOL:"))
            cursor = marker + len(MARKER)
            continue

        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text) or text[i] != "(":
            results.append(ToolError(f"{MARKER} {name}", "missing argument list"))
            cursor = i if i > cursor else cursor + len(MARKER)
            continue

        depth = 0
        in_single = in_double = escaped = False
        args_start = i + 1
        args_end = None
        while i < len(text):
            ch = text[i]
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif in_single:
                if ch == "'":
                    in_single = False
            elif in_double:
                if ch == '"':
                    in_double = False
            else:
                if ch == "'":
                    in_single = True
                elif ch == '"':
                    in_double = True
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        args_end = i
                        break
            i += 1

        if args_end is None:
            results.append(ToolError(f"{MARKER} {name}(...", "unterminated argument list"))
            cursor = marker + len(MARKER)
            continue

        raw_args = text[args_start:args_end]
        try:
            args = parse_args(raw_args)
        except Exception as exc:
            results.append(ToolError(f"{MARKER} {name}({raw_args[:80]})",
                                     f"could not parse arguments: {exc}"))
        else:
            results.append(ToolCall(name=name, args=args, raw=f"{name}({raw_args})"))
        cursor = args_end + 1


def extract_lenient(text: str, allowed: set[str]) -> list[ToolCall | ToolError]:
    """
    `extract`, plus a fallback for completions that drop the `TOOL:` marker.

    Small local models omit the prefix constantly — they emit a bare
    `transcript.append(id='u1', ...)` on its own line. Strict parsing turns that
    into a silent no-op session: nothing parses, nothing is written, and the
    session commits empty, which is the worst possible failure because it looks
    like success.

    The fallback is narrow enough to stay safe: a bare call is only recognised if
    its name is **already in the role's working set**. Prose cannot accidentally
    match `criteria.load(...)`, and a hallucinated function still fails
    validation rather than sneaking through. Marker-prefixed calls always win; the
    fallback only runs when the completion has no markers at all.
    """
    marked = extract(text)
    if marked:
        return marked

    # Collect with positions and sort by them: call order is semantic. An intake
    # session must append the entry before segmenting it, so returning calls
    # in name order would invert the only sequence that matters.
    found: list[tuple[int, ToolCall]] = []
    for name in sorted(allowed, key=len, reverse=True):
        start = 0
        while True:
            idx = text.find(name + "(", start)
            if idx == -1:
                break
            if idx > 0 and (text[idx - 1].isalnum() or text[idx - 1] in "_."):
                start = idx + 1                      # part of a longer identifier
                continue
            parsed = extract(f"{MARKER} {text[idx:]}")
            if parsed and isinstance(parsed[0], ToolCall):
                found.append((idx, parsed[0]))
                start = idx + len(parsed[0].raw)
            else:
                start = idx + 1

    return [call for _, call in sorted(found, key=lambda pair: pair[0])]


def validate(call: ToolCall, allowed: set[str]) -> ToolError | None:
    """Reject anything outside the role's namespace before dispatch."""
    if "." not in call.name:
        return ToolError(call.raw, f"{call.name!r} is not an artefact.verb name")
    if call.name not in allowed:
        return ToolError(
            call.raw,
            f"{call.name!r} is not in this role's working set; "
            f"available: {', '.join(sorted(allowed))}",
        )
    return None
