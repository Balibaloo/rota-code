"""Draw the flow of records through seats as two Mermaid charts.

Frame 314 probe, pass 2. The tool reads six sources and imports none:

- `rota/design/graph.json`: the seats, the tools (`writes` edges) and the
  messages (`messages` edges).
- `rota/core/predicates.py`: the ticks, their wakes, bands and drains.
- `rota/core/scheduler.py`: the SQL of the `tick_*` functions that a tick
  delegates to.
- `rota/core/lifecycle.py`: the states that a scheduler action writes.
- `rota/roles/api.py`: the `@op(artefact, verb)` functions, which write the
  states a seat's session can leave behind.
- `rota/core/schema.sql`: which columns are states (`CHECK (col IN ...)`),
  and their defaults.

It parses the Python with `ast` and the SQL with regular expressions, so no
database and no scheduler code runs.

Run from the repository root:

    python probes/flowchart/flowchart.py

It writes `probes/flowchart/flowchart.mmd` (the full chart) and
`probes/flowchart/path.mmd` (the delivery path of one change). Every list
is sorted, so the output is the same on every run.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRAPH = ROOT / "rota" / "design" / "graph.json"
PREDICATES = ROOT / "rota" / "core" / "predicates.py"
SCHEDULER_PY = ROOT / "rota" / "core" / "scheduler.py"
LIFECYCLE_PY = ROOT / "rota" / "core" / "lifecycle.py"
API_PY = ROOT / "rota" / "roles" / "api.py"
SCHEMA = ROOT / "rota" / "core" / "schema.sql"
OUT_FULL = ROOT / "probes" / "flowchart" / "flowchart.mmd"
OUT_PATH = ROOT / "probes" / "flowchart" / "path.mmd"

# The two sentinels are read from predicates.py by value below. These
# names are only the lane names the chart gives them.
LANE_SCHEDULER = "scheduler"
LANE_ANY = "any_seat"
NOT_DERIVED = "not_derived"

# The delivery path runs from an item's first state to the merged batch.
# The first state is the schema DEFAULT of `items.approval`, read below.
PATH_START_COL = ("items", "approval")
PATH_END = ("batches", "status", "merged")

# A scheduler action `do:<name>` joins the lifecycle function of the same
# name. No hand table joins the others (Roman's rule, 2026-10-24 14:10):
# an action with no equal name is drawn to "not derived".


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

def read_graph() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def _split_top(body: str) -> list[str]:
    """Split a CREATE TABLE body on the commas outside parentheses."""
    parts, depth, cur = [], 0, []
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return parts


def read_schema() -> dict[tuple[str, str], dict]:
    """Return {(table, col): {"values": [...], "default": str | None}}.

    A state column is one that a `CHECK (col IN (...))` constrains."""
    text = re.sub(r"--[^\n]*", "", SCHEMA.read_text(encoding="utf-8"))
    cols: dict[tuple[str, str], dict] = {}
    for m in re.finditer(r"CREATE TABLE (?:IF NOT EXISTS )?(\w+)\s*\(", text):
        i, depth = m.end(), 1
        while depth and i < len(text):
            depth += {"(": 1, ")": -1}.get(text[i], 0)
            i += 1
        for seg in _split_top(text[m.end():i - 1]):
            words = seg.split()
            if not words:
                continue
            col = words[0]
            check = re.search(rf"CHECK\s*\(\s*{re.escape(col)}\s+IN\s*\(([^)]*)\)", seg)
            if not check:
                continue
            default = re.search(r"DEFAULT\s+'([^']*)'", seg)
            cols[(m.group(1), col)] = {
                "values": re.findall(r"'([^']*)'", check.group(1)),
                "default": default.group(1) if default else None,
            }
    return cols


def _literal(node):
    try:
        return ast.literal_eval(node)
    except (ValueError, SyntaxError):
        return None


def _names(node, constants: dict) -> list:
    """Resolve a `derives` value to role ids.

    A name defined in predicates.py resolves. A name imported from the
    scheduler, such as SURVEY_ORDER, stays unresolved.
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


def read_functions(path: Path) -> dict[str, ast.FunctionDef]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def _returns_str(fn: ast.FunctionDef) -> bool:
    return isinstance(fn.returns, ast.Name) and fn.returns.id == "str"


def closure(fns: dict[str, ast.FunctionDef], roots: list[str],
            skip_fragments: bool = False) -> list[str]:
    """The functions of one module that the roots reach by a plain call.

    With `skip_fragments`, a callee annotated `-> str` is left out. In the
    scheduler such a function returns a piece of SQL that the caller splices
    into its WHERE, `not_parked` for one, and its pieces are split across
    string constants, so the tool cannot see the exclusion around them."""
    seen: set[str] = set()
    todo = [r for r in roots if r in fns]
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        for n in ast.walk(fns[name]):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id in fns and n.func.id not in seen \
                    and not (skip_fragments and _returns_str(fns[n.func.id])):
                todo.append(n.func.id)
    return sorted(seen)


def ctx_writes(fn: ast.FunctionDef, state_cols: dict) -> set[tuple[str, str, str, str]]:
    """The states an api function stages with `ctx.writes.append((table, id, values))`.

    The api does not run SQL for a write. It stages a row, and the door
    writes it. A quoted value is "literal". Any other value is "bound".
    A values dict held in a name is read from its assignment in the function.
    A staged row in a table with no state column is "a new row", (t, *, *).
    A state column the dict leaves out is not drawn: an upsert keeps it."""
    dicts: dict[str, list[ast.Dict]] = {}
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Dict):
            for tg in n.targets:
                if isinstance(tg, ast.Name):
                    dicts.setdefault(tg.id, []).append(n.value)
    out: set[tuple[str, str, str, str]] = set()
    for n in ast.walk(fn):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "append" and isinstance(n.func.value, ast.Attribute)
                and n.func.value.attr == "writes" and n.args
                and isinstance(n.args[0], ast.Tuple) and len(n.args[0].elts) >= 3):
            continue
        t = _literal(n.args[0].elts[0])
        if not isinstance(t, str):
            continue
        vals = n.args[0].elts[2]
        found = [vals] if isinstance(vals, ast.Dict) else \
            dicts.get(vals.id, []) if isinstance(vals, ast.Name) else []
        mine = sorted(c for (tt, c) in state_cols if tt == t)
        if not mine:
            out.add((t, "*", "*", "new row"))
            continue
        for d in found:
            for k, v in zip(d.keys, d.values):
                col = _literal(k) if k is not None else None
                if (t, col) not in state_cols:
                    continue
                lit = _literal(v)
                if isinstance(lit, str):
                    out.add((t, col, lit, "literal"))
                else:
                    # GUESS 2 again: a bound value is any value the CHECK allows.
                    for x in state_cols[(t, col)]["values"]:
                        out.add((t, col, x, "bound"))
    return out


def _imports(fn: ast.FunctionDef, module: str) -> list[str]:
    """The names a function imports from `.<module>` inside its body."""
    out: list[str] = []
    for n in ast.walk(fn):
        if isinstance(n, ast.ImportFrom) and n.level == 1 and n.module == module:
            out += [a.name for a in n.names]
    return sorted(out)


def read_predicates(sched_fns: dict) -> tuple[list[dict], dict, dict]:
    """Return the predicates in file order, the sentinels and TERMINAL."""
    tree = ast.parse(PREDICATES.read_text(encoding="utf-8"))
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
            wakes_val = "@" + wakes.id if isinstance(wakes, ast.Name) else _literal(wakes)
            body = _sql_of(node)
            # A tick that delegates gets the SQL of the scheduler's tick_*
            # function it imports, and of every scheduler function that one calls.
            ticks = [n for n in _imports(node, "scheduler") if n.startswith("tick_")]
            sched = closure(sched_fns, ticks, skip_fragments=True)
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
                "body": body,
                "sched_body": " ".join(_sql_of(sched_fns[f]) for f in sched),
                "delegates": ticks,
                "actions": sorted(set(re.findall(r"^do:(\w+)$", "\n".join(
                    n.value for n in ast.walk(node)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)),
                    re.M))),
            })
    for p in preds:
        if isinstance(p["wakes"], str) and p["wakes"].startswith("@"):
            p["wakes"] = sentinels[p["wakes"][1:]]
    return preds, sentinels, terminal


def read_ops() -> dict[tuple[str, str], str]:
    """Return {(artefact, verb): function name} from `@op(...)` in api.py."""
    tree = ast.parse(API_PY.read_text(encoding="utf-8"))
    ops: dict[tuple[str, str], str] = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and getattr(dec.func, "id", "") == "op" \
                    and len(dec.args) == 2:
                ops[(_literal(dec.args[0]), _literal(dec.args[1]))] = node.name
    return ops


# ---------------------------------------------------------------------------
# SQL reading
# ---------------------------------------------------------------------------

_EXCL = re.compile(r"\bNOT\s+(?:EXISTS|IN)\s*\(", re.I)


def strip_exclusions(sql: str) -> tuple[str, int]:
    """Cut every `NOT EXISTS (...)` and `NOT IN (...)` out of the SQL.

    An exclusion names the rows a tick does not fire on, so it draws no
    trigger arrow. Return the rest and the count cut."""
    out, i, cut = [], 0, 0
    while True:
        m = _EXCL.search(sql, i)
        if not m:
            out.append(sql[i:])
            break
        out.append(sql[i:m.start()])
        j, depth = m.end(), 1
        while j < len(sql) and depth:
            depth += {"(": 1, ")": -1}.get(sql[j], 0)
            j += 1
        i, cut = j, cut + 1
    return " ".join(out), cut


# GUESS 1: a tick with no drains fires on the states its SQL tests with a
# literal: `alias.col = 'value'` and `alias.col IN ('a', 'b')`, the alias
# resolved through `FROM table alias`. Only a state column counts. Any other
# literal is a filter. `!=` is ignored.
_FROM = re.compile(r"\b(?:FROM|JOIN)\s+(\w+)(?:\s+(?:AS\s+)?(\w+))?")
_EQ = re.compile(r"(?:(\w+)\.)?(\w+)\s*=\s*'([\w-]+)'")
_IN = re.compile(r"(?:(\w+)\.)?(\w+)\s+IN\s*\(\s*('[^)]*')\s*\)", re.I)
_SQL_WORDS = {"where", "and", "or", "on", "not", "select", "group", "order",
              "limit", "join", "left", "inner", "exists", "as", "union"}


def body_states(body: str, state_cols: dict) -> tuple[list, list, list, int]:
    """Return (states, filters, tables, exclusions cut) of one SQL text."""
    body, cut = strip_exclusions(body)
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
    found = set()
    for m in _EQ.finditer(body):
        a, col, val = m.groups()
        t = alias.get(a) if a else (tables[0] if len(set(tables)) == 1 else None)
        if t:
            found.add((t, col, val))
    for m in _IN.finditer(body):
        a, col, vals = m.groups()
        t = alias.get(a) if a else (tables[0] if len(set(tables)) == 1 else None)
        if t:
            for v in re.findall(r"'([\w-]+)'", vals):
                found.add((t, col, v))
    states = sorted(s for s in found if (s[0], s[1]) in state_cols)
    filters = sorted(s for s in found if (s[0], s[1]) not in state_cols)
    return states, filters, sorted(set(tables)), cut


_UPD = re.compile(r"\bUPDATE\s+(\w+)\s+SET\s+(.*?)(?=\bWHERE\b|\bUPDATE\b|"
                  r"\bINSERT\b|\bSELECT\b|\bDELETE\b|$)", re.I | re.S)
_SET = re.compile(r"(\w+)\s*=\s*('([^']*)'|\?|:\w+|[\w.]+)")
_INS = re.compile(r"\bINSERT\s+(?:OR\s+\w+\s+)?INTO\s+(\w+)\s*(\(([^)]*)\))?\s*"
                  r"(VALUES\s*\(|SELECT\b)?", re.I)


def _values_list(sql: str, start: int) -> list[str]:
    """The comma-separated items of `VALUES (...)`, from just inside `(`."""
    j, depth = start, 1
    while j < len(sql) and depth:
        depth += {"(": 1, ")": -1}.get(sql[j], 0)
        j += 1
    return [v.strip() for v in _split_top(sql[start:j - 1])]


def written_states(sql: str, state_cols: dict) -> set[tuple[str, str, str, str]]:
    """The states one SQL text writes, as (table, col, value, how).

    `how` is "literal" for a quoted value, "default" for the schema DEFAULT
    of a column an INSERT leaves out, and "bound" for a parameter.
    An INSERT into a table with no state column writes "a new row", (t, *, *).
    """
    out: set[tuple[str, str, str, str]] = set()
    for m in _UPD.finditer(sql):
        t = m.group(1)
        for a in _SET.finditer(m.group(2)):
            col = a.group(1)
            if (t, col) not in state_cols:
                continue
            if a.group(3) is not None:
                out.add((t, col, a.group(3), "literal"))
            else:
                # GUESS 2: a bound value can be any value the CHECK allows.
                for v in state_cols[(t, col)]["values"]:
                    out.add((t, col, v, "bound"))
    for m in _INS.finditer(sql):
        t = m.group(1)
        mine = sorted(c for (tt, c) in state_cols if tt == t)
        if not mine:
            out.add((t, "*", "*", "new row"))
            continue
        cols = [c.strip() for c in m.group(3).split(",")] if m.group(3) else None
        vals = _values_list(sql, m.end()) if (m.group(4) or "").upper().startswith("VALUES") \
            else None
        for col in mine:
            info = state_cols[(t, col)]
            if cols is not None and col not in cols:
                if info["default"] is not None:
                    out.add((t, col, info["default"], "default"))
                continue
            v = vals[cols.index(col)] if cols is not None and vals is not None \
                and cols.index(col) < len(vals) else "?"
            lit = re.fullmatch(r"'([^']*)'", v)
            if lit:
                out.add((t, col, lit.group(1), "literal"))
            else:
                for x in info["values"]:
                    out.add((t, col, x, "bound"))
    return out


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def ident(*parts: str) -> str:
    return "_".join(re.sub(r"\W", "_", p) for p in parts)


def label(text: str) -> str:
    return text.replace('"', "'")


def sid(t: str, c: str, v: str) -> str:
    return ident("s", t, c, v)


def build() -> dict:
    graph = read_graph()
    state_cols = read_schema()
    sched_fns = read_functions(SCHEDULER_PY)
    life_fns = read_functions(LIFECYCLE_PY)
    api_fns = read_functions(API_PY)
    ops = read_ops()
    preds, sentinels, terminal = read_predicates(sched_fns)
    derived, scheduler = sentinels["DERIVED"], sentinels["SCHEDULER"]

    # A column the lifecycle module sets with a literal is a state as well.
    for f in life_fns.values():
        for m in _UPD.finditer(_sql_of(f)):
            for a in _SET.finditer(m.group(2)):
                if a.group(3) is not None:
                    state_cols.setdefault((m.group(1), a.group(1)),
                                          {"values": [a.group(3)], "default": None})

    seats = sorted(n["id"] for n in graph["nodes"] if n["type"] in ("role", "principal"))
    seat_label = {n["id"]: n["label"] for n in graph["nodes"]}

    # End states of a seat: the states its tools write, through the graph's
    # writes edges and the @op registry, and its messages (schema DEFAULT).
    seat_end: dict[str, set[tuple[str, str, str, str]]] = {s: set() for s in seats}
    tool_end: dict[str, list] = {}
    no_op: set[str] = set()
    sends: dict[str, set[str]] = {}               # seat -> verbs
    receivers: dict[str, set[str]] = {}           # verb -> seats
    msg_default = state_cols.get(("messages", "status"), {}).get("default")
    for e in graph["edges"]:
        if e["s"] not in seats:
            continue
        if e["type"] == "writes":
            key = (e["t"], e.get("v") or "")
            fn = ops.get(key)
            if fn is None:
                no_op.add(f"{e['t']}.{key[1]}")
                continue
            if fn not in tool_end:
                reach = closure(api_fns, [fn])
                sql = " ".join(_sql_of(api_fns[f]) for f in reach)
                found = written_states(sql, state_cols)
                for f in reach:
                    found |= ctx_writes(api_fns[f], state_cols)
                tool_end[fn] = sorted(found)
            seat_end[e["s"]].update(tool_end[fn])
        elif e["type"] == "messages":
            sends.setdefault(e["s"], set()).add(e.get("v") or "?")
            receivers.setdefault(e.get("v") or "?", set()).add(e["t"])
            if msg_default:
                seat_end[e["s"]].add(("messages", "status", msg_default, "default"))

    ticks: dict[str, list[tuple[str, dict]]] = {}
    triggers: list[tuple[str, str, str]] = []     # (state id, tick id, how)
    ends: list[tuple[str, str, str, str]] = []    # (from id, state id, how, style)
    states: dict[str, set[tuple[str, str]]] = {}  # table -> {(col, val)}
    stats = {"exclusions": 0, "filters": set(), "left_behind": [],
             "not_derived": [], "derived": [], "no_trigger": [], "scheduler_sql": []}
    tick_lane: dict[str, str] = {}
    for p in preds:
        if p["wakes"] == scheduler:
            lanes = [LANE_SCHEDULER]
        elif p["wakes"] == derived:
            # GUESS 3: a DERIVED tick gets one node in each seat its `derives`
            # names. With no `derives`, it goes to one "any seat" lane.
            lanes = sorted(p["derives"]) or [LANE_ANY]
        else:
            lanes = [p["wakes"]]
        # The end states of an action come from lifecycle.py.
        act_end: set[tuple[str, str, str, str]] = set()
        if p["wakes"] == scheduler:
            for a in p["actions"]:
                fn = a
                if fn in life_fns:
                    sql = " ".join(_sql_of(life_fns[f]) for f in closure(life_fns, [fn]))
                    act_end |= written_states(sql, state_cols)
        act_keys = {(t, c, v) for (t, c, v, _) in act_end}
        on, how = [], "drains"
        for d in sorted(set(p["drains"])):
            if d in act_keys:
                stats["left_behind"].append(f"{p['name']}: {'.'.join(d)}")
            else:
                on.append(d)
        if not on:
            on, filters, tables, cut = body_states(p["body"], state_cols)
            stats["exclusions"] += cut
            stats["filters"] |= set(filters)
            how = "sql"
            if not on and p["sched_body"]:
                on, filters, tables2, cut = body_states(p["sched_body"], state_cols)
                stats["exclusions"] += cut
                stats["filters"] |= set(filters)
                tables = sorted(set(tables) | set(tables2)) if not on else tables
                how = "scheduler sql"
                if on or tables2:
                    stats["scheduler_sql"].append(p["name"])
            if not on:
                # GUESS 4: no state literal, so the tick fires on a table as a
                # whole: "any row".
                on = [(t, "*", "*") for t in tables]
                how = how + ", any row"
        if not on:
            stats["no_trigger"].append(p["name"])
        for lane in lanes:
            tid = ident("t", p["name"], lane)
            tick_lane[tid] = lane
            ticks.setdefault(lane, []).append((tid, p))
            for (t, c, v) in on:
                states.setdefault(t, set()).add((c, v))
                triggers.append((sid(t, c, v), tid, how))
            if p["wakes"] == scheduler:
                if act_end:
                    stats["derived"].append(p["name"])
                    for (t, c, v, h) in sorted(act_end):
                        states.setdefault(t, set()).add((c, v))
                        ends.append((tid, sid(t, c, v), h, "end"))
                else:
                    stats["not_derived"].append(p["name"])
                    ends.append((tid, NOT_DERIVED, "", "dashed"))
            elif seat_end.get(lane):
                stats["derived"].append(f"{p['name']} ({lane})")
            else:
                stats["not_derived"].append(f"{p['name']} ({lane})")
                ends.append((tid, NOT_DERIVED, "", "dashed"))
    for (t, c, v) in terminal:
        states.setdefault(t, set()).add((c, v))

    # A new row in a table with no state is drawn only where a tick waits on it.
    waited = {s for (s, _, _) in triggers}
    for seat in seats:
        for (t, c, v, h) in sorted(seat_end[seat]):
            if c == "*" and sid(t, c, v) not in waited:
                continue
            states.setdefault(t, set()).add((c, v))
            ends.append((f"lane_{ident(seat)}", sid(t, c, v), h, "end"))

    start_col = state_cols[PATH_START_COL]
    return {
        "graph": graph, "seats": seats, "seat_label": seat_label, "ticks": ticks,
        "tick_lane": tick_lane, "triggers": sorted(set(triggers)),
        "ends": sorted(set(ends)), "states": states, "terminal": terminal,
        "stats": stats, "no_op": sorted(no_op), "sends": sends,
        "receivers": receivers, "msg_default": msg_default,
        "start": sid(PATH_START_COL[0], PATH_START_COL[1], start_col["default"]),
        "end": sid(*PATH_END),
    }


def state_marks(b: dict) -> dict[str, str]:
    """A state nothing leaves is "final". A TERMINAL state left by a tick is "held"."""
    leaves = {s for (s, _, _) in b["triggers"]}
    marks: dict[str, str] = {}
    for t, cv in b["states"].items():
        for (c, v) in cv:
            s = sid(t, c, v)
            if s not in leaves:
                marks[s] = " (final)"
            elif (t, c, v) in b["terminal"]:
                marks[s] = " (held)"
    return marks


def _tick_node(tid: str, p: dict, flag_none: bool) -> str:
    flag = " (principal present)" if p["needs_principal"] else ""
    if flag_none:
        flag += " (no trigger found)"
    return f'{tid}(["{p["band"]}: {p["name"]}{flag}"])'


def _end_arrow(src: str, dst: str, how: str, style: str) -> str:
    if style == "dashed":
        return f"  {src} -.-> {dst}"
    return f"  {src} ==>|{how}| {dst}"


def draw_full(b: dict) -> list[str]:
    marks = state_marks(b)
    st = b["stats"]
    out = ["flowchart LR", "  %% generated by probes/flowchart/flowchart.py; do not edit",
           "  %% thin arrow: a state wakes a tick. thick arrow: a session or an action",
           "  %% ends in a state. dashed arrow: the sources do not give the end state."]
    for lane in sorted(set(b["seats"]) | set(b["ticks"])):
        out.append(f'  subgraph lane_{ident(lane)}["{label(b["seat_label"].get(lane, lane))}"]')
        for tid, p in sorted(b["ticks"].get(lane, []), key=lambda x: x[1]["seq"]):
            out.append("    " + _tick_node(tid, p, p["name"] in st["no_trigger"]))
        if not b["ticks"].get(lane):
            out.append(f'    {ident("idle", lane)}["no tick wakes this seat"]')
        out.append("  end")
    out.append('  subgraph records["records"]')
    for t in sorted(b["states"]):
        out.append(f'    subgraph tbl_{ident(t)}["{t}"]')
        for (c, v) in sorted(b["states"][t]):
            s = sid(t, c, v)
            text = f"{t} (any row)" if c == "*" else f"{c} = {v}"
            out.append(f'      {s}["{label(text + marks.get(s, ""))}"]')
        out.append("    end")
    out.append("  end")
    out.append(f'  {NOT_DERIVED}["not derived"]')
    for (s, tid, how) in b["triggers"]:
        out.append(f"  {s} -->|{how}| {tid}")
    for (src, dst, how, style) in b["ends"]:
        out.append(_end_arrow(src, dst, how, style))
    out.append(f"  %% ticks with no trigger found: {', '.join(sorted(st['no_trigger'])) or 'none'}")
    out.append(f"  %% graph tools with no @op function: {', '.join(b['no_op']) or 'none'}")
    return out


def draw_path(b: dict) -> list[str]:
    """The nodes on some walk from the item's first state to the merged batch.

    The `messages` hub is folded into one box per verb: a seat that sends the
    verb points at the box, and the box points at the seats that receive it.
    """
    msg_open = sid("messages", "status", b["msg_default"] or "")
    edges: set[tuple[str, str, str]] = set()      # (src, dst, kind)
    for (s, tid, how) in b["triggers"]:
        if s != msg_open:
            edges.add((s, tid, how))
    for tid, lane in b["tick_lane"].items():
        if lane != LANE_SCHEDULER:
            edges.add((tid, f"lane_{ident(lane)}", "wakes"))
    for (src, dst, how, style) in b["ends"]:
        if style == "end" and dst != msg_open:
            edges.add((src, dst, how))
    for seat, verbs in b["sends"].items():
        for v in verbs:
            edges.add((f"lane_{ident(seat)}", ident("msg", v), "sends"))
    for v, seats in b["receivers"].items():
        for r in seats:
            edges.add((ident("msg", v), f"lane_{ident(r)}", "receives"))

    def reach(start: str, forward: bool) -> set[str]:
        nxt: dict[str, set[str]] = {}
        for (a, z, _) in edges:
            (nxt.setdefault(a, set()).add(z)) if forward else nxt.setdefault(z, set()).add(a)
        seen, todo = set(), [start]
        while todo:
            n = todo.pop()
            if n not in seen:
                seen.add(n)
                todo += sorted(nxt.get(n, ()))
        return seen

    on = reach(b["start"], True) & reach(b["end"], False)
    marks = state_marks(b)
    out = ["flowchart LR",
           "  %% generated by probes/flowchart/flowchart.py; do not edit",
           "  %% the delivery path of one change, from the item's first state to the merge"]
    if b["end"] not in on:
        out.append("  %% the merged batch is not reachable from the item's first state")
    for lane in sorted(set(b["seats"]) | set(b["ticks"])):
        lid = f"lane_{ident(lane)}"
        mine = [(tid, p) for tid, p in b["ticks"].get(lane, []) if tid in on]
        if lid not in on and not mine:
            continue
        out.append(f'  subgraph {lid}["{label(b["seat_label"].get(lane, lane))}"]')
        for tid, p in sorted(mine, key=lambda x: x[1]["seq"]):
            out.append("    " + _tick_node(tid, p, False))
        if not mine:
            out.append(f'    {ident("idle", lane)}["no tick on the path"]')
        out.append("  end")
    for t in sorted(b["states"]):
        rows = [(c, v) for (c, v) in sorted(b["states"][t]) if sid(t, c, v) in on]
        if not rows:
            continue
        out.append(f'  subgraph tbl_{ident(t)}["{t}"]')
        for (c, v) in rows:
            s = sid(t, c, v)
            text = f"{t} (new row)" if c == "*" else f"{c} = {v}"
            out.append(f'    {s}["{label(text + marks.get(s, ""))}"]')
        out.append("  end")
    for v in sorted(b["receivers"]):
        m = ident("msg", v)
        if m in on:
            out.append(f'  {m}[/"message: {label(v)}"/]')
    for (a, z, how) in sorted(edges):
        if a in on and z in on:
            arrow = "-->" if how not in ("literal", "default", "bound", "new row") else "==>"
            out.append(f"  {a} {arrow}|{how}| {z}")
    return out


def main() -> int:
    b = build()
    OUT_FULL.write_bytes(("\n".join(draw_full(b)) + "\n").encode("utf-8"))
    OUT_PATH.write_bytes(("\n".join(draw_path(b)) + "\n").encode("utf-8"))
    st = b["stats"]
    print(f"ticks derived {len(st['derived'])}, not derived {len(st['not_derived'])}")
    print("not derived: " + ", ".join(sorted(st["not_derived"])))
    print("no trigger: " + ", ".join(sorted(st["no_trigger"])))
    print("scheduler sql: " + ", ".join(sorted(st["scheduler_sql"])))
    print("left behind: " + ", ".join(sorted(st["left_behind"])))
    print(f"exclusions cut {st['exclusions']}; filters dropped: "
          + ", ".join(".".join(f) for f in sorted(st["filters"])))
    print("graph tools with no @op: " + ", ".join(b["no_op"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
