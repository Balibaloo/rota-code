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
import re
from dataclasses import dataclass
from typing import Any

MARKER = "TOOL:"


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: dict[str, Any]
    raw: str = ""
    # Positional arguments, bound against the real signature at dispatch. The
    # parser cannot bind them itself because it does not know what it is
    # calling; rejecting them outright cost two cases every run.
    pos: tuple[Any, ...] = ()


@dataclass(frozen=True)
class ToolError:
    raw: str
    reason: str


# JSON's spelling of the three keywords, and Python's. Models blend the two
# syntaxes constantly — Python keyword arguments carrying `true` rather than
# `True` — because half the tool-calling world is JSON and nothing in the prompt
# says which dialect this is. It is not ambiguous, and it is not worth a fatal
# error: one `default_taken=true` poisoned an entire L3 chain. The Gatekeeper
# spent every remaining turn apologising for it and never sent the message the
# chain existed to test.
_WORDS = {"true": True, "false": False, "null": None,
          "True": True, "False": False, "None": None}


def _literal(node: ast.AST) -> Any:
    """
    `ast.literal_eval`, plus two tolerances, and nothing else.

    Still never `eval`: an LLM-authored argument list is untrusted input, so
    this walks a fixed set of node types and refuses everything else. A model
    writing `body=criteria.load(id='b1')[0]['body']` — which they do — gets a
    tool error, not a nested dispatch.
    """
    if isinstance(node, ast.Name):
        # A bare word. `true`/`false`/`null` mean what JSON means by them;
        # anything else is a string that lost its quotes, which is by far the
        # commonest way a small model malforms an id: `refs=m_dead_75b4f6`.
        return _WORDS[node.id] if node.id in _WORDS else node.id
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_literal(e) for e in node.elts]
    if isinstance(node, ast.Dict):
        if any(k is None for k in node.keys):
            raise ValueError("dict unpacking is not supported")
        return {_literal(k): _literal(v) for k, v in zip(node.keys, node.values)}

    value = ast.literal_eval(node)
    # `text=...` means "and so on", and `literal_eval` is delighted to hand back
    # Python's Ellipsis for it. It survives the sandbox, survives the write, and
    # dies at commit as `Object of type ellipsis is not JSON serializable` --
    # taking a session that was otherwise sound. A placeholder is not a value.
    if value is Ellipsis:
        raise ValueError("`...` is a placeholder, not a value; write the value")
    return value


def parse_args(args_str: str) -> tuple[dict[str, Any], tuple[Any, ...]]:
    """
    Parse the argument list. JSON object form, or Python keyword form.

    Returns the keyword arguments and any positional ones. Positionals used to
    be rejected here, which was the parser enforcing a rule it had no standing
    to enforce: whether `tests.encode('t1', 'c1', ...)` is well formed depends
    on the signature, and the parser does not know the signature. The sandbox
    does, so it binds them there.
    """
    args_str = args_str.strip()
    if not args_str:
        return {}, ()

    if args_str.startswith("{"):
        parsed = json.loads(args_str)
        if not isinstance(parsed, dict):
            raise ValueError("JSON tool arguments must be an object")
        return parsed, ()

    # Newlines inside an unquoted argument list would break the expression, so
    # they are escaped before parsing and restored by literal_eval.
    safe = args_str.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")
    try:
        expr = ast.parse(f"_f({safe})", mode="eval")
    except SyntaxError:
        # **A prose argument has to be able to carry code, and code is quotes.**
        #
        # The Developer's brief asks it to quote the test body it disputes, so
        # the argument it produces looks like
        #
        #     reason='"the criterion says ..." and "assert f('SKU-1', 25) == ..."'
        #
        # and `ast` stops at `'SKU-1'`, because the inner quote closes the outer
        # one. The call became a `ToolError`, the message was never sent, and
        # `L1-DV-fix-the-code-not-the-test` turned green *because the model
        # could not speak* — a case passing for an accident rather than a
        # reason, produced by an instruction this protocol could not carry.
        #
        # So the instruction stays sayable and the protocol widens. Strict
        # parsing is tried first and is unchanged; only what it rejects reaches
        # here, so nothing that parsed before parses differently now.
        return _parse_args_lenient(safe), ()
    call = expr.body
    if not isinstance(call, ast.Call):
        raise ValueError("not a call expression")

    out: dict[str, Any] = {}
    for kw in call.keywords:
        if kw.arg is None:
            raise ValueError("**kwargs is not supported")
        out[kw.arg] = _literal(kw.value)
    return out, tuple(_literal(a) for a in call.args)


def _parse_args_lenient(args_str: str) -> dict:
    """The quote-tolerant fallback. Lives in `_lenient` so the strict grammar
    here stays the thing you read first."""
    from ._lenient import parse_args_lenient

    return parse_args_lenient(args_str, _literal)


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
            # `TOOL: model.consult` with no parentheses is a call to a function
            # whose arguments are all optional, and it was a parse error. One
            # Architect session spent every one of its twelve turns on it: seven
            # rejections reading "missing argument list", for a call that needed
            # no arguments, and it never reached the write it was woken for.
            #
            # Parsed as `name()` now, so a genuinely incomplete call fails at
            # `validate` instead, which knows the signature and can say *which*
            # argument is missing. A format complaint that cannot name the thing
            # it wants teaches nothing, and the model duly did not learn.
            #
            # The dot is what keeps this honest. Every function here is
            # `artefact.verb`, and without the check `TOOL: TOOL: TOOL:` parsed
            # its own marker as a zero-argument call to `TOOL`.
            if "." in name:
                results.append(ToolCall(name=name, args={}, raw=f"{MARKER} {name}"))
            else:
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
            args, pos = parse_args(raw_args)
        except Exception as exc:
            results.append(ToolError(f"{MARKER} {name}({raw_args[:80]})",
                                     f"could not parse arguments: {exc}"))
        else:
            results.append(ToolCall(name=name, args=args, pos=pos,
                                    raw=f"{name}({raw_args})"))
        cursor = args_end + 1


def _labelled(text: str, allowed: set[str]) -> list[tuple[int, ToolCall]]:
    """
    `GLOSSARY.AMEND: id = 1 term = "Charge"` — the marker used as a label.

    A whole class of sessions committed empty like this, with no error logged
    anywhere, because the model read

        TOOL: artefact.verb(key='value')

    and took `TOOL:` for a slot to fill with the tool's name. On a line where
    every other token is a placeholder that is a fair reading, and the result is
    the worst failure shape there is: three well-formed intentions, none of them
    parsed, and a session that looks like a role deciding to do nothing.

    Arguments arrive without brackets or commas, as loose `key = value` pairs
    running to the next key or the end of the line. Values may be quoted or
    bare; a bare one runs until the next `word =`, because prose values are
    common here and `sense_short = billing entity` means both words.
    """
    out: list[tuple[int, ToolCall]] = []
    names = "|".join(sorted((re.escape(a) for a in allowed), key=len, reverse=True))
    if not names:
        return out

    # An argument list wraps across lines in real output, so a call runs from
    # its label to the next label or the next blank line — not to end of line.
    labels = [(m.start(), m.group(1).lower(), m.end())
              for m in re.finditer(rf"(?im)^[ \t]*({names})[ \t]*:", text)]

    for i, (start, name, from_) in enumerate(labels):
        if name not in allowed:                      # matched in another case
            continue
        to = labels[i + 1][0] if i + 1 < len(labels) else len(text)
        chunk = text[from_:to]
        if gap := re.search(r"\n[ \t]*\n", chunk):
            chunk = chunk[:gap.start()]

        args: dict[str, Any] = {}
        for a in re.finditer(
                r"""(?s)(\w+)[ \t]*=[ \t]*("[^"]*"|'[^']*'|.+?(?=\s+\w+[ \t]*=|\Z))""",
                chunk):
            raw = a.group(2).strip()
            if raw[:1] in "\"'" and raw[-1:] == raw[:1]:
                args[a.group(1)] = raw[1:-1]
            else:
                args[a.group(1)] = _WORDS.get(raw, raw)

        # A name followed by arguments is an intention; a name followed by a
        # sentence is the model narrating. Only the first may dispatch.
        if args:
            out.append((start, ToolCall(name=name, args=args,
                                        raw=f"{name}({' '.join(chunk.split())[:60]})")))
    return out


def extract_lenient(text: str, allowed: set[str]) -> list[ToolCall | ToolError]:
    """
    `extract`, plus fallbacks for completions that mishandle the marker.

    Small local models omit the prefix constantly — they emit a bare
    `transcript.append(id='u1', ...)` on its own line. Strict parsing turns that
    into a silent no-op session: nothing parses, nothing is written, and the
    session commits empty, which is the worst possible failure because it looks
    like success.

    The fallbacks are narrow enough to stay safe: a call is only recognised if
    its name is **already in the role's working set**. Prose cannot accidentally
    match `criteria.load(...)`, and a hallucinated function still fails
    validation rather than sneaking through. Marker-prefixed calls always win;
    the fallbacks only run when the completion has no markers at all.
    """
    marked = extract(text)
    if marked:
        return marked

    if labelled := _labelled(text, allowed):
        return [call for _, call in sorted(labelled, key=lambda p: p[0])]

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
