"""Frame 164's replay: the count's calls through the binder of one tree.

    D:/repos/rota/.venv/Scripts/python.exe probes/frame164/replay.py <tree> <out.json>
    D:/repos/rota/.venv/Scripts/python.exe probes/frame164/replay.py --compare <a.json> <b.json>

The first form imports `rota` from <tree>, reads `probes/frame164/calls.json`
of this tree, and sends each call's arguments through that tree's
`validate_args`, with the op's own signature as the binder exposes it. It
writes the problem and the arguments after the check. The second form
prints how many calls differ between two trees, and how.
"""
from __future__ import annotations

import ast
import inspect
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(tree: str, out: str) -> None:
    sys.path.insert(0, tree)
    from rota.core import sandbox
    from rota.roles import api
    assert Path(sandbox.__file__).resolve().is_relative_to(Path(tree).resolve())

    seen, rows = set(), []
    for c in json.loads((HERE / "calls.json").read_text(encoding="utf-8")):
        key = (c["night"], c["session"], c["seq"], c["op"], c["args"])
        if key in seen:
            continue
        seen.add(key)
        fn = api.REGISTRY[(c["art"], c["verb"])]
        try:
            sig = inspect.signature(fn, eval_str=True)
        except (NameError, TypeError):
            sig = inspect.signature(fn)

        def target(**_):
            pass
        target.__signature__ = sig.replace(
            parameters=[p for n, p in sig.parameters.items() if n != "ctx"])
        kw = ast.literal_eval(c["args"])
        problem = sandbox.validate_args(target, kw, op=(c["art"], c["verb"]))
        rows.append({"key": list(key), "problem": problem, "after": repr(kw),
                     "text": any(isinstance(v, str) and k in fn.__annotations__
                                 and fn.__annotations__[k] in ("int", "bool",
                                                               "float", int,
                                                               bool, float)
                                 for k, v in kw.items())})
    Path(out).write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print(f"{tree}: {len(rows)} calls")


def compare(a: str, b: str) -> None:
    ra = json.loads(Path(a).read_text(encoding="utf-8"))
    rb = json.loads(Path(b).read_text(encoding="utf-8"))
    assert [r["key"] for r in ra] == [r["key"] for r in rb]
    diff = [(x, y) for x, y in zip(ra, rb)
            if (x["problem"], x["after"]) != (y["problem"], y["after"])]
    print(f"{len(ra)} calls, {len(diff)} differ, "
          f"{sum(x['text'] for x, _ in diff)} of them carry text for a typed scalar, "
          f"{sum(x['text'] for x in ra)} calls carry such text in all")
    for x, y in diff:
        n, s, seq, op, _ = x["key"]
        what = (f"refused: {y['problem']}" if y["problem"] != x["problem"]
                else f"converted: {y['after']}")
        print(f"  night {n} {s} turn {seq} {op}: {what}")


if __name__ == "__main__":
    if sys.argv[1] == "--compare":
        compare(sys.argv[2], sys.argv[3])
    else:
        run(sys.argv[1], sys.argv[2])
