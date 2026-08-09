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
import typing
from typing import Any, Callable

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


def schema_for(dotted: str, fn: Callable) -> dict[str, Any]:
    from .sandbox import ENUMS

    sig = inspect.signature(fn)
    properties: dict[str, Any] = {}
    required: list[str] = []

    for name, param in sig.parameters.items():
        prop = _json_type(param.annotation)
        # Constrained columns become enums so the model is told the legal values
        # rather than discovering them through a rejected call.
        if name in ENUMS:
            prop = {"type": "string", "enum": list(ENUMS[name])}
        properties[name] = prop
        if param.default is inspect.Parameter.empty:
            required.append(name)

    doc = inspect.getdoc(fn) or ""
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
    out = []
    for dotted in sb.functions():
        artefact, fn_name = dotted.split(".", 1)
        out.append(schema_for(dotted, getattr(sb[artefact], fn_name)))
    return out
