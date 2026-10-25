"""
JSON-schema tool definitions, derived from the same functions the sandbox
dispatches to.

Provider-native function calling removes the single most expensive failure mode
observed with small local models: dropping the `TOOL:` marker, which turned a
session into a silent no-op that *committed empty* — success-shaped failure. With
native calling there is no marker to forget, because the model emits structured
arguments the runtime reads directly.

The schemas are generated from `inspect.signature`, so the advertisement cannot
drift from what is callable. Nothing here decides what a role may do; the graph
already did that, and this only describes it in a second dialect.

Name mangling: graph names are `artefact.verb`, and the OpenAI-compatible schema
most providers accept restricts function names to `[A-Za-z0-9_-]`. Dots become a
double underscore on the way out and back on the way in — a pure transport
concern that never reaches the graph or the database.
"""
from __future__ import annotations

import inspect
import logging
import re
import typing
from typing import Any, Callable

_log = logging.getLogger(__name__)

SEP = "__"


def mangle(dotted: str) -> str:
    return dotted.replace(".", SEP)


def demangle(name: str) -> str:
    return name.replace(SEP, ".", 1)


def _json_type(annotation: Any) -> dict[str, Any]:
    """Map a Python annotation onto a JSON-schema fragment. Unknown -> string."""
    if annotation is inspect.Parameter.empty:
        return {"type": "string"}

    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)

    # `list[str] | None` and friends: describe the non-None half.
    if origin is typing.Union or str(origin) == "<class 'types.UnionType'>":
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return _json_type(non_none[0])
        return {"type": "string"}

    if origin in (list, typing.List):
        item = args[0] if args else str
        return {"type": "array", "items": _json_type(item)}
    if origin in (dict, typing.Dict):
        return {"type": "object"}

    return {
        str: {"type": "string"},
        int: {"type": "integer"},
        float: {"type": "number"},
        bool: {"type": "boolean"},
        list: {"type": "array", "items": {"type": "string"}},
        dict: {"type": "object"},
    }.get(annotation, {"type": "string"})


#: The longest description one parameter gets. The schemas travel on every
#: turn, so the cap keeps a role's offered set inside the prompt budget.
PARAM_DESCRIPTION_CAP = 200


def _arguments_section(doc: str) -> dict[str, str]:
    """
    The `Arguments:` section of a docstring, as {name: text}.

    Each entry is `name: text` one indent in, and a deeper line continues it.
    """
    out: dict[str, str] = {}
    lines = doc.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines)
                     if ln.strip() in ("Arguments:", "Args:"))
    except StopIteration:
        return out
    indent = None
    current = None
    for ln in lines[start + 1:]:
        if not ln.strip():
            if out:
                break
            continue
        depth = len(ln) - len(ln.lstrip())
        if indent is None:
            indent = depth
        if depth < indent:
            break
        m = re.match(r"\s*(\w+):\s*(.*)$", ln)
        if depth == indent and m:
            current = m.group(1)
            out[current] = m.group(2).strip()
        elif current:
            out[current] = f"{out[current]} {ln.strip()}".strip()
    return out


def param_description(doc: str, name: str) -> str:
    """
    What one parameter holds, for its schema.

    The docstring's `Arguments:` entry, else the bare name. A sentence
    fallback picked design history and dotted text calls such as
    `verdicts.emit(fail, ...)`, which teach the text form (frame 323,
    review 2).
    """
    text = _arguments_section(doc).get(name, "") or name
    return text[:PARAM_DESCRIPTION_CAP]


def schema_for(dotted: str, fn: Callable) -> dict[str, Any]:
    from ..core.sandbox import ENUMS, ENUMS_BY_OP

    # The future import makes every annotation a string, and `_json_type`
    # reads `'list[str]'` as a string. A native seat then sent a list as a
    # JSON string (frame 327). An annotation that does not evaluate keeps
    # the old reading, so no tool loses its schema.
    # The fallback turns every list and int of the function back into a
    # string, so it names the function (frame 327, review 1, L1).
    try:
        sig = inspect.signature(fn, eval_str=True)
    except Exception as exc:
        _log.warning("schema for %s falls back to string annotations: %s: %s",
                     dotted, type(exc).__name__, exc)
        sig = inspect.signature(fn)
    properties: dict[str, Any] = {}
    required: list[str] = []
    # An argument that its op's own door reads carries no flat enum (frame
    # 204: `ledger.log`'s `kind` is not the backlog's `kind`).
    artefact, _, verb = dotted.partition(".")
    own = {k for k, v in (ENUMS_BY_OP.get((artefact, verb.replace("_", " ")))
                          or {}).items() if v is None}

    for name, param in sig.parameters.items():
        prop = _json_type(param.annotation)
        # Constrained columns become enums so the model is told the legal values
        # rather than discovering them through a rejected call.
        if name in ENUMS and name not in own:
            prop = {"type": "string", "enum": list(ENUMS[name])}
        properties[name] = prop
        if param.default is inspect.Parameter.empty:
            required.append(name)

    doc = inspect.getdoc(fn) or ""
    # A type alone does not say what a parameter holds. On frame 323's trial
    # Gemma put a meaning into `sense`, because the schema gave no prose.
    for name, prop in properties.items():
        prop["description"] = param_description(doc, name)
    return {
        "type": "function",
        "function": {
            "name": mangle(dotted),
            "description": doc.strip().split("\n\n")[0][:400] or dotted,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def schemas_for_sandbox(sb) -> list[dict[str, Any]]:
    """Every function in this role's (possibly mode-narrowed) working set."""
    from ..roles.api import _offered_kinds

    out = []
    for dotted in sb.functions():
        artefact, fn_name = dotted.split(".", 1)
        schema = schema_for(dotted, getattr(sb[artefact], fn_name))
        # `ledger.log`'s `kind` takes the words of this session's mode. A
        # bare string taught a seat the words only through a refusal (frame
        # 204's review 1, finding H1).
        if dotted == "ledger.log":
            schema["function"]["parameters"]["properties"]["kind"] = {
                "type": "string", "enum": list(_offered_kinds(sb.ctx))}
        out.append(schema)
    return out
