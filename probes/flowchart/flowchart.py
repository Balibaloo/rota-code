"""Draw the flow of records through seats as a Mermaid chart.

Frame 314 probe. The tool reads two sources and nothing else:
`rota/design/graph.json` (the role graph) and `rota/core/predicates.py`
(the tick predicates). It parses the predicates with `ast` and does not
import them, so no database and no scheduler code runs.

Run from the repository root:

    python probes/flowchart/flowchart.py > probes/flowchart/flowchart.mmd

Every list is sorted, so the output is the same on every run.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRAPH = ROOT / "rota" / "design" / "graph.json"
PREDICATES = ROOT / "rota" / "core" / "predicates.py"

# The two sentinels are read from predicates.py by value below. These
# names are only the lane names the chart gives them.
LANE_SCHEDULER = "scheduler"
LANE_ANY = "any_seat"

# GUESS 1: a graph artefact id maps to a database table. The graph names
# artefacts and the predicates name tables, and no source joins the two.
# A name that is equal in both sources joins by itself. The aliases below
# are the probe's guesses, each taken from the artefact's label or note.
ARTEFACT_TABLE_GUESS = {
    "brief": "statements",      # label "Brief (statements)"
    "problem": "items",         # writes "in-scope and out-of-scope items"
    "tests": "tests",
    "glossary": "glossary_terms",
    "model": "constraints",
    "surveys": "survey_records",
    "code": "batches",          # "commit branch + diff" sets batches.head_commit
}


def read_graph() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def _literal(node):
    try:
        return ast.literal_eval(node)
    except (ValueError, SyntaxError):
        return None


def _names(node, constants: dict) -> list:
    """Resolve a `derives` value to role ids.

    A name defined in predicates.py resolves. A name imported from the
    scheduler, such as SURVEY_ORDER, stays unresolved, because the brief
    lets the probe read only how the scheduler turns a predicate into a wake.
    """
    if isinstance(node, ast.Name):
        return list(constants.get(node.id, []))
    if isinstance(node, (ast.Tuple, ast.List)):
        out: list = []
        for el in node.elts:
            out += _names(el.value if isinstance(el, ast.Starred) else el, constants)
        return out
    value = _literal(node)
    return [value] if isinstance(value, str) else []


def _sql_of(fn: ast.FunctionDef) -> str:
    """Join the string constants of a function, without its docstring.

    The SQL lives in string constants. Prose in a docstring or a comment
    holds words like "from a" that a table pattern would read as a table.
    """
    doc = fn.body[0].value if fn.body and isinstance(fn.body[0], ast.Expr) else None
    parts = [n.value for n in ast.walk(fn)
             if isinstance(n, ast.Constant) and isinstance(n.value, str) and n is not doc]
    return " ".join(parts)


def read_predicates() -> tuple[list[dict], dict, dict]:
    """Return the predicates in file order, the sentinels and TERMINAL."""
    source = PREDICATES.read_text(encoding="utf-8")
    tree = ast.parse(source)
    sentinels: dict[str, str] = {}
    constants: dict[str, list] = {}
    terminal: dict = {}
    preds: list[dict] = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in ("DERIVED", "SCHEDULER"):
                sentinels[name] = _literal(node.value)
            value = _literal(node.value)
            if isinstance(value, tuple):
                constants[name] = list(value)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.target.id == "TERMINAL":
            terminal = _literal(node.value) or {}
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if not (isinstance(dec, ast.Call) and getattr(dec.func, "id", "") == "predicate"):
                continue
            kw = {k.arg: k.value for k in dec.keywords}
            wakes = kw.get("wakes")
            if isinstance(wakes, ast.Name):
                wakes_val = "@" + wakes.id      # resolved against sentinels below
            else:
                wakes_val = _literal(wakes)
            body = _sql_of(node)
            preds.append({
                "seq": len(preds),
                "name": _literal(dec.args[0]),
                "wakes": wakes_val,
                "band": _literal(kw["band"]) if "band" in kw else "start",
                "drains": [tuple(d) for d in (_literal(kw["drains"]) or [])]
                          if "drains" in kw else [],
                "derives": _names(kw["derives"], constants) if "derives" in kw else [],
                "needs_principal": bool(_literal(kw["needs_principal"]))
                                   if "needs_principal" in kw else False,
                "doc": ast.get_docstring(node) or "",
                "body": body,
            })
    for p in preds:
        if isinstance(p["wakes"], str) and p["wakes"].startswith("@"):
            p["wakes"] = sentinels[p["wakes"][1:]]
    return preds, sentinels, terminal


# GUESS 2: a predicate that declares no drains fires on the states its own
# SQL tests with a literal. The probe reads `alias.col = 'value'` and
# `alias.col IN ('a', 'b')` and resolves the alias through `FROM table alias`.
# It ignores `!=`, and it cannot tell a positive EXISTS from a NOT EXISTS.
_FROM = re.compile(r"\b(?:FROM|JOIN)\s+(\w+)(?:\s+(?:AS\s+)?(\w+))?")
_EQ = re.compile(r"(?:(\w+)\.)?(\w+)\s*=\s*'([\w-]+)'")
_IN = re.compile(r"(?:(\w+)\.)?(\w+)\s+IN\s*\(\s*('[^)]*')\s*\)", re.I)
_SQL_WORDS = {"where", "and", "or", "on", "not", "select", "group", "order",
              "limit", "join", "left", "inner", "exists", "as", "union"}


def body_states(body: str) -> tuple[list[tuple[str, str, str]], list[str]]:
    tables: list[str] = []
    alias: dict[str, str] = {}
    for m in _FROM.finditer(body):
        t, a = m.group(1), m.group(2)
        if t.lower() in _SQL_WORDS:
            continue
        tables.append(t)
        alias[t] = t
        if a and a.lower() not in _SQL_WORDS:
            alias[a] = t
    states = set()
    for m in _EQ.finditer(body):
        a, col, val = m.groups()
        t = alias.get(a) if a else (tables[0] if len(tables) == 1 else None)
        if t:
            states.add((t, col, val))
    for m in _IN.finditer(body):
        a, col, vals = m.groups()
        t = alias.get(a) if a else (tables[0] if len(tables) == 1 else None)
        if t:
            for v in re.findall(r"'([\w-]+)'", vals):
                states.add((t, col, v))
    return sorted(states), sorted(set(tables))


def ident(*parts: str) -> str:
    return "_".join(re.sub(r"\W", "_", p) for p in parts)


def label(text: str) -> str:
    return text.replace('"', "'")


def main() -> int:
    graph = read_graph()
    preds, sentinels, terminal = read_predicates()
    derived, scheduler = sentinels["DERIVED"], sentinels["SCHEDULER"]

    seats = sorted(n["id"] for n in graph["nodes"] if n["type"] in ("role", "principal"))
    seat_label = {n["id"]: n["label"] for n in graph["nodes"]}
    artefacts = sorted(n["id"] for n in graph["nodes"] if n["type"] == "artefact")

    def table_of(artefact: str) -> str:
        return ARTEFACT_TABLE_GUESS.get(artefact, artefact)

    # Tick nodes: (lane, predicate) pairs, and the tick arrows into them.
    ticks: dict[str, list[tuple[str, dict]]] = {}
    arrows: list[tuple[str, str, str]] = []           # (state id, tick id, label)
    states: dict[str, set[tuple[str, str]]] = {}      # table -> {(col, val)}
    no_source: list[str] = []
    for p in preds:
        if p["wakes"] == scheduler:
            lanes = [LANE_SCHEDULER]
        elif p["wakes"] == derived:
            # GUESS 3: a DERIVED predicate gets one node in each seat its
            # `derives` names. With no `derives`, it goes to one "any seat" lane.
            lanes = sorted(p["derives"]) or [LANE_ANY]
        else:
            lanes = [p["wakes"]]
        on = sorted(set(p["drains"]))
        how = "drains"
        if not on:
            on, tables = body_states(p["body"])
            how = "sql"
            if not on:
                # GUESS 4: no literal state, so the tick fires on the table as a
                # whole. A body that delegates to scheduler.tick_* names none.
                on = [(t, "*", "*") for t in tables]
                how = "table"
        if not on:
            no_source.append(p["name"])
        for lane in lanes:
            tid = ident("t", p["name"], lane)
            ticks.setdefault(lane, []).append((tid, p))
            for (t, c, v) in on:
                states.setdefault(t, set()).add((c, v))
                arrows.append((ident("s", t, c, v), tid, how))
    for (t, c, v) in terminal:
        states.setdefault(t, set()).add((c, v))

    # Seat writes from the graph: one arrow per (seat, table), verbs joined.
    writes: dict[tuple[str, str], set[str]] = {}
    for e in graph["edges"]:
        if e["type"] == "writes" and e["s"] in seats:
            t = table_of(e["t"])
            writes.setdefault((e["s"], t), set()).add(e.get("v") or "?")
        elif e["type"] == "messages" and e["s"] in seats:
            # GUESS 5: a graph `messages` edge writes a row of the messages table.
            writes.setdefault((e["s"], "messages"), set()).add(e.get("v") or "?")
    for (_, t) in writes:
        states.setdefault(t, set())
    unmapped = sorted({table_of(a) for a in artefacts} - set(states))

    out: list[str] = ["flowchart LR"]
    out.append("  %% generated by probes/flowchart/flowchart.py; do not edit")
    lanes = sorted(set(seats) | set(ticks))
    for lane in lanes:
        title = seat_label.get(lane, lane)
        out.append(f'  subgraph lane_{ident(lane)}["{label(title)}"]')
        for tid, p in sorted(ticks.get(lane, []), key=lambda x: x[1]["seq"]):
            flag = " (principal present)" if p["needs_principal"] else ""
            if p["name"] in no_source:
                flag += " (trigger in scheduler, not read)"
            out.append(f'    {tid}(["{p["band"]}: {p["name"]}{flag}"])')
        if not ticks.get(lane):
            out.append(f'    {ident("idle", lane)}["no tick wakes this seat"]')
        out.append("  end")
    out.append('  subgraph records["records"]')
    for t in sorted(states):
        out.append(f'    subgraph tbl_{ident(t)}["{t}"]')
        if not states[t]:
            out.append(f'      {ident("s", t, "*", "*")}["{t} (any row)"]')
        for (c, v) in sorted(states[t]):
            mark = " (end)" if (t, c, v) in terminal else ""
            text = f"{t} (any row)" if c == "*" else f"{c} = {v}{mark}"
            out.append(f'      {ident("s", t, c, v)}["{label(text)}"]')
        out.append("    end")
    out.append("  end")
    for (sid, tid, how) in sorted(arrows):
        out.append(f"  {sid} -->|{how}| {tid}")
    for (seat, t) in sorted(writes):
        verbs = ", ".join(sorted(writes[(seat, t)]))
        out.append(f'  lane_{ident(seat)} -.->|"{label(verbs)}"| tbl_{ident(t)}')
    out.append(f"  %% predicates with no source state: {', '.join(sorted(no_source)) or 'none'}")
    out.append(f"  %% artefacts with no table: {', '.join(unmapped) or 'none'}")
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
