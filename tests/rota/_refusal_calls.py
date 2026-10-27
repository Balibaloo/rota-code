"""
The calls that the refusal texts name, against the modes that meet them.

Frame 135's law: a refusal names only a call the doors admit. The follower
in `rota/core/sandbox.py` checks each call that a door records through
`api._offer`. A refusal text that names a call without that record is never
followed (the audit of 2026-10-27, F25). This module reads every such text
in the source, so a test can hold each one to the law.

The reading is static. A text names a call when it holds `artefact.verb(`
and the artefact is one of `api.REGISTRY` or `msg`. A text sits in one
top-level function. The ops that reach that function, by the names that
the functions of the two files call, are the ops that can meet the text.
A mode meets the text when it holds one of those ops. A text inside an
`if` whose test names the call as a string is guarded: the door asks the
mode first, so the text reaches only a mode that holds the call. A text
that a shared door reaches, `_bind` or `_bind_send`, is checked for its
name only, because the static reading cannot tell which op meets it.
"""
from __future__ import annotations

import ast
import re
import tempfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from rota import paths

FILES = ("rota/roles/api.py", "rota/core/sandbox.py")
CALL = re.compile(r"\b([a-z_]+)\.([a-z_]+)\(")
DOTTED = re.compile(r"^[a-z_]+\.[a-z_]+$")

# The functions that every op passes through. A text there meets every mode.
EVERY_OP = frozenset({"validate_args", "_bind", "Sandbox.call"})
# The function that builds every message send. A text there meets every mode
# that holds a `msg` call.
EVERY_SEND = frozenset({"_bind_send"})


@dataclass(frozen=True)
class Named:
    """One call that one refusal text names."""
    file: str
    line: int
    unit: str            # the top-level function, or "" at module level
    call: str            # `artefact.attr`
    text: str            # the literal parts of the text, `{}` per value
    guarded: bool
    ops: frozenset       # the ops that can meet the text

    @property
    def key(self) -> str:
        return f"{self.unit or '<module>'}:{self.call}"


def _artefacts() -> set[str]:
    from rota.roles import api

    return {a for a, _ in api.REGISTRY} | {"msg"}


def _attr(verb: str) -> str:
    return verb.replace(" ", "_").replace("-", "_")


@lru_cache(maxsize=1)
def _ops() -> dict[str, str]:
    """The function name of each op's implementation, to the op."""
    from rota.roles import api

    return {fn.__name__: f"{art}.{_attr(verb)}"
            for (art, verb), fn in api.REGISTRY.items()}


def _units(tree: ast.Module) -> dict[str, ast.AST]:
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[node.name] = node
        elif isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out[f"{node.name}.{sub.name}"] = sub
    return out


def _callees(unit: ast.AST, names: set[str]) -> set[str]:
    out = set()
    for node in ast.walk(unit):
        if isinstance(node, ast.Call):
            f = node.func
            name = (f.id if isinstance(f, ast.Name) else
                    f.attr if isinstance(f, ast.Attribute) else None)
            if name in names:
                out.add(name)
    return out


@lru_cache(maxsize=1)
def _trees() -> dict[str, ast.Module]:
    return {f: ast.parse((paths.REPO / f).read_text(encoding="utf-8"))
            for f in FILES}


@lru_cache(maxsize=1)
def reach() -> dict[str, frozenset]:
    """Each top-level function of the two files, to the ops that reach it.
    `*` stands for every op and `msg.*` for every send."""
    units: dict[str, ast.AST] = {}
    for tree in _trees().values():
        units.update(_units(tree))
    names = set(units)
    calls = {u: _callees(node, names) for u, node in units.items()}
    roots = {fn: {op} for fn, op in _ops().items() if fn in units}
    for fn in EVERY_OP:
        roots.setdefault(fn, set()).add("*")
    for fn in EVERY_SEND:
        roots.setdefault(fn, set()).add("msg.*")
    out: dict[str, set] = {u: set() for u in units}
    for root, ops in roots.items():
        seen, todo = set(), [root]
        while todo:
            u = todo.pop()
            if u in seen:
                continue
            seen.add(u)
            out[u] |= ops
            todo.extend(calls.get(u, ()))
    return {u: frozenset(v) for u, v in out.items()}


def _docstrings(tree: ast.Module) -> set[int]:
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef, ast.Module)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)):
                out.add(id(body[0].value))
    return out


def _flat(node: ast.AST) -> str:
    if isinstance(node, ast.Constant):
        return node.value
    return "".join(v.value if isinstance(v, ast.Constant) else "{}"
                   for v in node.values)


def _guards(chain: list[ast.AST]) -> set[str]:
    """The dotted names that an enclosing test holds as strings."""
    out = set()
    for node in chain:
        tests = []
        if isinstance(node, (ast.If, ast.IfExp, ast.While)):
            tests.append(node.test)
        elif isinstance(node, ast.comprehension):
            tests.extend(node.ifs)
        for test in tests:
            out |= {c.value for c in ast.walk(test)
                    if isinstance(c, ast.Constant) and isinstance(c.value, str)
                    and DOTTED.match(c.value)}
    return out


def _table_op(chain: list[ast.AST], node: ast.AST) -> str | None:
    """The op of a module table entry keyed `(artefact, verb, ...)`."""
    for parent in reversed(chain):
        if isinstance(parent, ast.Dict):
            for k, v in zip(parent.keys, parent.values):
                if v is node or any(n is node for n in ast.walk(v)):
                    if (isinstance(k, ast.Tuple) and len(k.elts) >= 2
                            and all(isinstance(e, ast.Constant)
                                    for e in k.elts[:2])):
                        return f"{k.elts[0].value}.{_attr(k.elts[1].value)}"
            return None
    return None


def named_calls() -> list[Named]:
    """Every call that a refusal text of the two files names."""
    arts = _artefacts()
    hits = reach()
    out = []
    for file, tree in _trees().items():
        docs = _docstrings(tree)

        def walk(node, chain, unit):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not unit:
                unit = node.name
                cls = next((c for c in reversed(chain)
                            if isinstance(c, ast.ClassDef)), None)
                if cls is not None:
                    unit = f"{cls.name}.{node.name}"
            if isinstance(node, ast.JoinedStr) or (
                    isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and id(node) not in docs
                    and not (chain and isinstance(chain[-1], ast.JoinedStr))):
                text = _flat(node)
                calls = sorted({f"{m.group(1)}.{m.group(2)}"
                                for m in CALL.finditer(text)
                                if m.group(1) in arts})
                if calls:
                    guards = _guards(chain)
                    if unit:
                        ops = hits.get(unit, frozenset())
                    else:
                        op = _table_op(chain, node)
                        ops = frozenset({op} if op else ())
                    for call in calls:
                        out.append(Named(file, node.lineno, unit, call, text,
                                         call in guards, ops))
                if isinstance(node, ast.JoinedStr):
                    return
            for child in ast.iter_child_nodes(node):
                walk(child, chain + [node], unit)

        walk(tree, [], "")
    return out


@lru_cache(maxsize=1)
def modes() -> dict[str, frozenset]:
    """Each `role/mode` to the calls it holds: the role's graph narrowed by
    the mode's `.tools` file, as `sandbox.build` narrows it."""
    from rota.core.db import init_db
    from rota.core.sandbox import build
    from rota.design import graph as graph_mod
    from rota.roles import prompts

    conn = init_db(Path(tempfile.mkdtemp()) / "rota.db")
    out = {}
    try:
        for role in sorted(graph_mod.load().roles):
            have = set(build(role, conn).functions())
            d = prompts.PROMPT_DIR / role
            stems = {p.stem for p in d.glob("*.tools")} if d.exists() else set()
            for mode in sorted(set(prompts.available(role)) | stems):
                tools = prompts.mode_tools(role, mode)
                out[f"{role}/{mode}"] = frozenset(
                    have if tools is None else have & set(tools))
    finally:
        conn.close()
    return out


def exists(call: str) -> bool:
    """True when a door admits the name: an op of `REGISTRY`, or a send that
    some role of the graph holds."""
    return any(call in held for held in modes().values()) or _registered(call)


def _registered(call: str) -> bool:
    from rota.roles import api

    art, _, attr = call.partition(".")
    return any(a == art and _attr(v) == attr for a, v in api.REGISTRY)


def meets(named: Named, held: frozenset) -> bool:
    """True when a mode that holds `held` can meet the text of `named`."""
    if "*" in named.ops:
        return True
    if "msg.*" in named.ops and any(c.startswith("msg.") for c in held):
        return True
    return bool(named.ops & held)


def shared(named: Named) -> bool:
    """True when a shared door reaches the text: every op, or every send.
    The static reading cannot tell which op of those meets the text, so
    the lint checks the name of such a call and not its modes."""
    return bool({"*", "msg.*"} & named.ops)


def findings() -> dict[str, list[str]]:
    """Each named call that breaks the law, keyed `unit:call`, to the
    reasons: the call does not exist, or a mode that meets the text does
    not hold it."""
    out: dict[str, list[str]] = {}
    for n in named_calls():
        why = []
        if not exists(n.call):
            why.append("no door admits the name")
        elif not n.guarded and not shared(n):
            lack = sorted(m for m, held in modes().items()
                          if meets(n, held) and n.call not in held)
            if lack:
                why.append(f"not held by {', '.join(lack)}")
        if why:
            out.setdefault(n.key, []).extend(
                f"{Path(n.file).name}:{n.line} {w}" for w in why)
    return out

