"""Frame 164's count: the ops with a typed scalar, and their calls on the nights.

Run from a tree root, with that tree's interpreter path:

    D:/repos/rota/.venv/Scripts/python.exe probes/frame164/count.py

It prints two tables and writes `probes/frame164/calls.json`, which the
replay reads. The night databases open read-only and immutable.
"""
from __future__ import annotations

import inspect
import json
import sqlite3
import sys
import types
import typing
import warnings
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from rota.core import sandbox  # noqa: E402  (fills the registry)
from rota.llm import toolproto  # noqa: E402
from rota.roles import api  # noqa: E402

NIGHTS = Path("D:/repos/rota/.rota")
# The parser's ast pass meets backslashes in the seats' prose. The warning
# says nothing about a call.
warnings.filterwarnings("ignore", category=SyntaxWarning)
SCALARS = (int, bool, float)


def scalar_of(ann):
    """The scalar type that `ann` declares, or None. `int | None` is int."""
    if ann in SCALARS:
        return ann
    if isinstance(ann, types.UnionType) or typing.get_origin(ann) is typing.Union:
        rest = [a for a in typing.get_args(ann) if a is not type(None)]
        if len(rest) == 1 and rest[0] in SCALARS:
            return rest[0]
    return None


def typed_ops() -> dict[str, dict]:
    """{dotted: {"art", "verb", "file", "params": {name: type name}, "order"}}."""
    out = {}
    for (art, verb), fn in sorted(api.REGISTRY.items()):
        try:
            sig = inspect.signature(fn, eval_str=True)
        except (NameError, TypeError):
            sig = inspect.signature(fn)
        order = [n for n in sig.parameters if n != "ctx"]
        params = {n: scalar_of(p.annotation).__name__
                  for n, p in sig.parameters.items()
                  if n != "ctx" and scalar_of(p.annotation) is not None}
        if params:
            code = fn.__code__
            out[f"{art}.{sandbox._verb_to_attr(verb)}"] = {
                "art": art, "verb": verb, "params": params, "order": order,
                "file": f"{Path(code.co_filename).name}:{code.co_firstlineno}"}
    return out


def all_param_sets() -> dict:
    out = {}
    for (art, verb), fn in api.REGISTRY.items():
        sig = inspect.signature(fn)
        names = [n for n in sig.parameters if n != "ctx"]
        req = {n for n in names
               if sig.parameters[n].default is inspect.Parameter.empty}
        out[f"{art}.{sandbox._verb_to_attr(verb)}"] = (req, set(names))
    return out


def judge(kind: str, v) -> dict:
    """Is `v` text, and does the conversion of frame 164 take it."""
    rec = {"value": repr(v)[:60], "pytype": type(v).__name__,
           "text": isinstance(v, str), "converts": None}
    if isinstance(v, str):
        s = v.strip()
        try:
            if kind == "int":
                int(s)
            elif kind == "float":
                float(s)
            elif s not in ("true", "false", "True", "False", "1", "0"):
                raise ValueError
            rec["converts"] = True
        except ValueError:
            rec["converts"] = False
    return rec


def main() -> None:
    ops = typed_ops()
    sets = all_param_sets()
    allowed = set(sets)
    print("| op | defined at | typed scalar parameters |")
    print("|---|---|---|")
    for dotted, o in ops.items():
        ps = ", ".join(f"`{n}: {t}`" for n, t in o["params"].items())
        print(f"| `{dotted}` | {o['file']} | {ps} |")
    print(f"\n{len(ops)} ops, "
          f"{sum(len(o['params']) for o in ops.values())} typed scalar parameters\n")

    calls = []
    for n in range(113, 127):
        db = NIGHTS / f"clickI_night{n}.db"
        if not db.exists():
            continue
        conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro&immutable=1", uri=True)
        for sid, seq, text in conn.execute(
                "SELECT session_id, seq, completion FROM turns ORDER BY rowid"):
            try:
                found = toolproto.extract_lenient(text, allowed, signatures=sets)
            except Exception as exc:                       # noqa: BLE001
                print(f"night {n} {sid} {seq}: parse crashed {exc!r}")
                continue
            for c in found:
                if not isinstance(c, toolproto.ToolCall) or c.name not in ops:
                    continue
                o = ops[c.name]
                kw = dict(c.args)
                kw.update({k: v for k, v in zip(o["order"], c.pos) if k not in kw})
                for p, kind in o["params"].items():
                    if p in kw:
                        calls.append({"night": n, "session": sid, "seq": seq,
                                      "op": c.name, "art": o["art"],
                                      "verb": o["verb"], "param": p,
                                      "kind": kind, "args": repr(kw),
                                      "pos": len(c.pos), **judge(kind, kw[p])})
        conn.close()
    (ROOT / "probes/frame164/calls.json").write_text(
        json.dumps(calls, indent=1), encoding="utf-8", newline="\n")

    agg = Counter((c["op"], c["param"], c["pytype"], c["converts"]) for c in calls)
    print("| op | parameter | arrived as | int()/float()/word converts | values |")
    print("|---|---|---|---|---|")
    for (op, p, t, conv), k in sorted(agg.items()):
        print(f"| `{op}` | `{p}` | {t} | {'' if conv is None else conv} | {k} |")
    text = [c for c in calls if c["text"]]
    distinct = {(c["night"], c["session"], c["seq"], c["op"], c["args"]) for c in calls}
    print(f"\n{len(calls)} typed scalar values in {len(distinct)} distinct calls, "
          f"{len(text)} values as text, "
          f"{sum(c['converts'] for c in text)} convert, "
          f"{sum(not c['converts'] for c in text)} do not")
    print("\nText values:")
    for c in text:
        print(f"  night {c['night']} {c['session']} turn {c['seq']} {c['op']} "
              f"{c['param']}={c['value']} converts={c['converts']}")


if __name__ == "__main__":
    main()
