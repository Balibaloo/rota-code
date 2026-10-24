"""Draw the flow of records through seats as two Mermaid charts.

Frame 314 probe, passes 2 to 4. The tool reads these sources and imports none.
Pass 3 added `rota/core/loop.py` (the dispatch joins, and the modules its
dispatch imports). Pass 4 added `rota/roles/prompts/<seat>/<mode>.tools`
(the tools of one tick or one message mode, joined by the shared name):

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
LOOP_PY = ROOT / "rota" / "core" / "loop.py"
API_PY = ROOT / "rota" / "roles" / "api.py"
PROMPTS = ROOT / "rota" / "roles" / "prompts"
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
        # A staged column that is not a state is kept as "set". The chart
        # draws it only where a tick's SQL compares a row against it.
        for d in found:
            for k in d.keys:
                col = _literal(k) if k is not None else None
                if isinstance(col, str) and (t, col) not in state_cols:
                    out.add((t, col, "", "set"))
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


def _module_file(base: Path, level: int, module: str | None, name: str) -> Path:
    """The file of `from <dots><module> import <name>`, seen from `base`."""
    root = base.parent
    for _ in range(level - 1):
        root = root.parent
    parts = (module.split(".") if module else []) + [name]
    return root.joinpath(*parts).with_suffix(".py")


def read_loop_joins() -> dict[str, list[tuple[Path, str]]]:
    """Return {wake kind literal: [(module file, function)]} from loop.py.

    The loop dispatches on `kind == "tick:<name>"` and on `action == "<name>"`.
    Inside each such `if` body the tool collects the calls `lifecycle.<fn>(...)`
    and `<module>.<fn>(...)` of a module the body imports with `from . import`.
    The tool follows the import to the module's file. A literal that starts
    with "tick:" names a tick; any other names a `do:` action."""
    tree = ast.parse(LOOP_PY.read_text(encoding="utf-8"))
    joins: dict[str, set[tuple[Path, str]]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        lits = [c.value for cmp in ast.walk(node.test) if isinstance(cmp, ast.Compare)
                and all(isinstance(o, ast.Eq) for o in cmp.ops)
                for c in [cmp.left, *cmp.comparators]
                if isinstance(c, ast.Constant) and isinstance(c.value, str)]
        if len(lits) != 1:
            continue
        mods = {"lifecycle": LIFECYCLE_PY}
        body = ast.Module(body=node.body, type_ignores=[])
        for n in ast.walk(body):
            if isinstance(n, ast.ImportFrom) and n.level >= 1:
                for a in n.names:
                    mods[a.asname or a.name] = _module_file(LOOP_PY, n.level, n.module, a.name)
        for n in ast.walk(body):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)                     and isinstance(n.func.value, ast.Name) and n.func.value.id in mods:
                joins.setdefault(lits[0], set()).add((mods[n.func.value.id], n.func.attr))
    return {k: sorted(v) for k, v in joins.items()}


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


_SUBQ = re.compile(r"\b(NOT\s+)?EXISTS\s*\(", re.I)


def _subqueries(sql: str) -> tuple[list[tuple[bool, str]], str]:
    """The top-level EXISTS and NOT EXISTS subqueries, and the SQL without them.

    Each subquery is (negated, inner text). A subquery nested in another one
    stays inside its parent's text."""
    out, rest, i = [], [], 0
    while True:
        m = _SUBQ.search(sql, i)
        if not m:
            rest.append(sql[i:])
            break
        rest.append(sql[i:m.start()])
        j, depth = m.end(), 1
        while j < len(sql) and depth:
            depth += {"(": 1, ")": -1}.get(sql[j], 0)
            j += 1
        out.append((bool(m.group(1)), sql[m.end():j - 1]))
        i = j
    return out, " ".join(rest)


def conditions(sql: str, state_cols: dict) -> tuple[list[tuple], list[str]]:
    """Read the ordering conditions of a tick from its subqueries.

    GUESS 5: what a head subquery means, as the three kinds below.

    A subquery that compares a column with `<alias>.head_commit` asks about
    the rows at the head commit of the outer row. It gives one condition:

    - ("exists", T, "", "", outer table, outer col): an EXISTS. Some row of T
      at the head exists.
    - ("all", T, col, v, ...): a NOT EXISTS with `col != 'v'`. Every row of T
      at the head has col = v.
    - ("none", T, "", "", ...): any other NOT EXISTS. No row of T is at the
      head yet. A new head makes it true.

    A subquery with no head compare draws nothing, except a positive EXISTS
    on a table with no state column, which is returned with the main query's
    JOIN tables as a needed table."""
    subs, main = _subqueries(sql)
    outer = {}
    for m in _FROM.finditer(main):
        if m.group(1).lower() not in _SQL_WORDS:
            outer[m.group(1)] = m.group(1)
            if m.group(2) and m.group(2).lower() not in _SQL_WORDS:
                outer[m.group(2)] = m.group(1)
    found, needs = [], []
    for neg, inner in subs:
        f = _FROM.search(inner)
        if not f:
            continue
        t = f.group(1)
        head = re.search(r"=\s*(\w+)\.head_commit\b", inner)
        if not head:
            if not neg and not any(tt == t for (tt, _) in state_cols):
                needs.append(t)
            continue
        ot = outer.get(head.group(1))
        if not ot:
            continue
        ne = [(c, v) for (_, c, v) in re.findall(r"(?:(\w+)\.)?(\w+)\s*!=\s*'([\w-]+)'", inner)
              if (t, c) in state_cols]
        if not neg:
            found.append(("exists", t, "", "", ot, "head_commit"))
        elif ne:
            for (c, v) in ne:
                found.append(("all", t, c, v, ot, "head_commit"))
        else:
            found.append(("none", t, "", "", ot, "head_commit"))
    for m in re.finditer(r"\bJOIN\s+(\w+)", main):
        t = m.group(1)
        if not any(tt == t for (tt, _) in state_cols):
            needs.append(t)
    return sorted(set(found)), sorted(set(needs))


def cond_id(c: tuple) -> str:
    return ident("q", c[0], c[1], c[2], c[3])


def cond_label(c: tuple) -> str:
    kind, t, col, v = c[:4]
    if kind == "exists":
        return f"{t} at head: some row"
    if kind == "all":
        return f"{t} at head: every {col} = {v}"
    return f"{t} at head: no row yet"


def read_tick_tools(lane: str, name: str, seats: list[str]) -> list[tuple[str, str]] | None:
    """The tools of one tick, from `rota/roles/prompts/<seat>/<tick>.tools`.

    The tick's name and the mode file's name are the same name. A line is
    `artefact.verb`, or `msg.<verb>_<seat>` for a message. None when no file."""
    path = PROMPTS / lane / f"{name}.tools"
    if not path.exists():
        return None
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "." not in line:
            continue
        a, v = line.split(".", 1)
        if a == "msg":
            to = [s for s in seats if v.endswith("_" + s)]
            out.append(("msg", v[:-len(to[0]) - 1] + ">" + to[0] if to else v))
        else:
            out.append((a, v))
    return sorted(set(out))


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


def cid(t: str, c: str) -> str:
    return ident("c", t, c)


def end_of(src: str, t: str, c: str, v: str, how: str) -> tuple[str, str, str, str]:
    """One end arrow. A bound value is folded: it points at the column's box,
    labelled "table.col = <bound>", not at each value the CHECK allows."""
    if how == "bound":
        return (src, cid(t, c), f"{t}.{c} = bound", "end")
    if how == "set":
        return (src, ident("h", t, c), f"sets {t}.{c}", "end")
    return (src, sid(t, c, v), how, "end")


def build() -> dict:
    graph = read_graph()
    state_cols = read_schema()
    sched_fns = read_functions(SCHEDULER_PY)
    life_fns = read_functions(LIFECYCLE_PY)
    api_fns = read_functions(API_PY)
    ops = read_ops()
    preds, sentinels, terminal = read_predicates(sched_fns)
    loop_joins = read_loop_joins()
    file_fns: dict[Path, dict] = {LIFECYCLE_PY: life_fns}

    def joined_end(kind: str) -> set[tuple[str, str, str, str]]:
        """The states the loop's dispatch of one wake kind writes.

        A lifecycle function gives its closure's SQL. A function of another
        module gives its own SQL and the lifecycle functions it calls."""
        found: set[tuple[str, str, str, str]] = set()
        for (path, fn) in loop_joins.get(kind, []):
            fns = file_fns.setdefault(path, read_functions(path) if path.exists() else {})
            if fn not in fns:
                continue
            names = closure(fns, [fn])
            sql = " ".join(_sql_of(fns[f]) for f in names)
            if path != LIFECYCLE_PY:
                called = sorted({n.func.attr for f in names for n in ast.walk(fns[f])
                                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                                 and isinstance(n.func.value, ast.Name)
                                 and n.func.value.id == "lifecycle"})
                sql += " " + " ".join(_sql_of(life_fns[f])
                                      for f in closure(life_fns, called))
            found |= written_states(sql, state_cols)
        return found
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

    def end_of_tool(fn: str) -> list:
        if fn not in tool_end:
            reach = closure(api_fns, [fn])
            sql = " ".join(_sql_of(api_fns[f]) for f in reach)
            found = written_states(sql, state_cols)
            for f in reach:
                found |= ctx_writes(api_fns[f], state_cols)
            tool_end[fn] = sorted(found)
        return tool_end[fn]

    def end_of_tick(tools: list[tuple[str, str]]) -> set:
        found: set = set()
        for (a, v) in tools:
            if a == "msg":
                if msg_default:
                    found.add(("messages", "status", msg_default, "default"))
                continue
            fn = ops.get((a, v)) or ops.get((a, v.replace("_", " ")))
            if fn:
                found |= set(end_of_tool(fn))
        return found
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
            seat_end[e["s"]].update(end_of_tool(fn))
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
             "not_derived": [], "derived": [], "loop_ticks": set(), "finer": [], "tools_ticks": [], "lane_ends": [], "no_trigger": [], "scheduler_sql": []}
    tick_lane: dict[str, str] = {}
    all_conds: set[tuple] = set()
    pending_needs: list[tuple[str, str]] = []
    fallback: set[str] = set()
    node_tools: dict[str, list] = {}

    def add_state(t: str, c: str, v: str, how: str) -> None:
        if how not in ("set", "new row"):
            states.setdefault(t, set()).add((c, v))
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
                act_end |= joined_end(a)
                if a in life_fns and a not in loop_joins:
                    sql = " ".join(_sql_of(life_fns[f]) for f in closure(life_fns, [a]))
                    act_end |= written_states(sql, state_cols)
        tick_end = joined_end("tick:" + p["name"]) if p["wakes"] != scheduler else set()
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
        # The subqueries give finer triggers. A head condition replaces the
        # plain trigger on the outer table's state, `running` for one.
        conds, needs = conditions(p["body"] + " " + p["sched_body"], state_cols)
        if conds:
            outer_tables = {c[4] for c in conds}
            dropped = [x for x in on if x[0] in outer_tables]
            if dropped:
                stats["finer"].append(p["name"])
            on = [x for x in on if x[0] not in outer_tables]
        if not on and not conds:
            stats["no_trigger"].append(p["name"])
        for lane in lanes:
            tid0 = ident("t", p["name"], lane)
            for c in conds:
                all_conds.add(c)
                triggers.append((cond_id(c), tid0, "at head"))
            for t in needs:
                pending_needs.append((t, tid0))
            tools = read_tick_tools(lane, p["name"], seats) \
                if lane in seats and p["wakes"] != scheduler else None
            tick_tools_end = end_of_tick(tools) if tools is not None else set()
            if tools is None and lane in seats:
                fallback.add(lane)
            if tools is not None:
                stats["tools_ticks"].append(p["name"])
                node_tools[tid0] = tools
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
                        add_state(t, c, v, h)
                        ends.append(end_of(tid, t, c, v, h))
                else:
                    stats["not_derived"].append(p["name"])
                    ends.append((tid, NOT_DERIVED, "", "dashed"))
            elif (seat_end.get(lane) if tools is None else tick_tools_end) or tick_end:
                stats["derived"].append(f"{p['name']} ({lane})")
                if tick_end:
                    stats["loop_ticks"].add(p["name"])
                for (t, c, v, h) in sorted(tick_end | tick_tools_end):
                    add_state(t, c, v, h)
                    ends.append(end_of(tid, t, c, v, h))
            else:
                stats["not_derived"].append(f"{p['name']} ({lane})")
                ends.append((tid, NOT_DERIVED, "", "dashed"))
    for (t, c, v) in terminal:
        states.setdefault(t, set()).add((c, v))

    # A seat keeps a lane-level end only where a tick of it has no .tools
    # file, or where no tick wakes it.
    for seat in seats:
        if seat in fallback or not ticks.get(seat):
            stats["lane_ends"].append(seat)
            for (t, c, v, h) in sorted(seat_end[seat]):
                add_state(t, c, v, h)
                ends.append(end_of(f"lane_{ident(seat)}", t, c, v, h))

    # A message wakes its receiver in the mode named by its verb: the file
    # `rota/roles/prompts/<seat>/<verb>.tools`. The principal is one node.
    # A sender's .tools line `msg.<verb>_<seat>` points at the message.
    people = {n["id"] for n in graph["nodes"] if n["type"] == "principal"}
    modes: dict[str, tuple[str, str]] = {}
    msg_links: set[tuple[str, str, str]] = set()
    msg_nodes: dict[str, tuple[str, str]] = {}
    pairs = sorted({(e["s"], e["t"], e.get("v") or "?") for e in graph["edges"]
                    if e["type"] == "messages"})

    def mode_of(to: str, verb: str) -> str | None:
        if to in people:
            modes[ident("m", to)] = (to, "")
            return ident("m", to)
        mid = ident("m", to, verb)
        if mid not in modes:
            tools = read_tick_tools(to, verb, seats)
            if tools is None:
                return None
            modes[mid] = (to, verb)
            node_tools[mid] = tools
            for (t, c, v, h) in sorted(end_of_tick(tools)):
                add_state(t, c, v, h)
                ends.append(end_of(mid, t, c, v, h))
        return mid

    for (src, to, verb) in pairs:
        mode_of(to, verb)
        if src in people:
            msg_links.add((ident("m", src), ident("msg", verb, to), "sends"))
            msg_nodes[ident("msg", verb, to)] = (verb, to)
    for node, tools in sorted(node_tools.items()):
        for (a, x) in tools:
            if a == "msg" and ">" in x:
                verb, to = x.split(">", 1)
                msg_links.add((node, ident("msg", verb, to), "sends"))
                msg_nodes[ident("msg", verb, to)] = (verb, to)
    for m, (verb, to) in sorted(msg_nodes.items()):
        mid = mode_of(to, verb)
        if mid:
            msg_links.add((m, mid, "wakes"))
    for m, (verb, to) in sorted(msg_nodes.items()):
        if (verb, to) and m not in {a for (a, _, _) in msg_links}:
            pass

    # A needed table (a JOIN, or a bare EXISTS) gives a trigger from its new row,
    # where some tick or seat writes a new row of it.
    new_rows = {d for (_, d, h, _) in ends if h == "new row"}
    for (t, tid) in pending_needs:
        if sid(t, "*", "*") in new_rows:
            triggers.append((sid(t, "*", "*"), tid, "joins"))

    # A condition's inputs: what makes it true.
    head_cols = {(c[4], c[5]) for c in all_conds}
    cond_edges: set[tuple[str, str, str]] = set()
    for c in sorted(all_conds):
        kind, t, col, v, ot, oc = c
        if kind == "exists":
            for (_, d, h, _) in ends:
                if d.startswith(ident("s", t) + "_") or d.startswith(ident("c", t) + "_"):
                    cond_edges.add((d, cond_id(c), "row at head"))
        elif kind == "all":
            states.setdefault(t, set()).add((col, v))
            cond_edges.add((sid(t, col, v), cond_id(c), "all at head"))
        else:
            cond_edges.add((ident("h", ot, oc), cond_id(c), "new head"))

    # A new row in a table with no state is drawn only where a tick waits on it.
    # A staged column that is not a state is drawn only where a condition reads it.
    waited = {s for (s, _, _) in triggers}
    kept = []
    for (src, dst, how, style) in ends:
        if how == "new row" and dst not in waited:
            continue
        if how.startswith("sets ") and tuple(how[5:].split(".")) not in head_cols:
            continue
        kept.append((src, dst, how, style))
    ends = kept
    for (_, d, h, _) in ends:
        if h == "new row":
            t = d[2:-4]
            states.setdefault(t, set()).add(("*", "*"))

    start_col = state_cols[PATH_START_COL]
    return {
        "graph": graph, "seats": seats, "seat_label": seat_label, "ticks": ticks,
        "tick_lane": tick_lane, "triggers": sorted(set(triggers)),
        "ends": sorted(set(ends)), "states": states, "terminal": terminal,
        "stats": stats, "no_op": sorted(no_op), "sends": sends,
        "receivers": receivers, "msg_default": msg_default,
        "start": sid(PATH_START_COL[0], PATH_START_COL[1], start_col["default"]),
        "end": sid(*PATH_END), "loop_joins": loop_joins,
        "modes": modes, "msg_links": sorted(msg_links), "msg_nodes": msg_nodes,
        "conds": sorted(all_conds), "cond_edges": sorted(cond_edges),
        "head_nodes": sorted({ident("h", t, c) for (t, c) in head_cols}),
        "preds": {ident("t", p["name"], lane): p
                  for lane, lst in ticks.items() for (_, p) in lst},
    }


def state_marks(b: dict) -> dict[str, str]:
    """A state nothing leaves is "final". A TERMINAL state left by a tick is "held"."""
    leaves = {s for (s, _, _) in b["triggers"]}
    marks: dict[str, str] = {}
    for t, cv in b["states"].items():
        for (c, v) in cv:
            s = sid(t, c, v)
            if s not in leaves:
                marks[s] = ", final"
            elif (t, c, v) in b["terminal"]:
                marks[s] = ", held"
    return marks


def _mode_node(m: str, b: dict) -> str:
    seat, verb = b["modes"][m]
    return f'{m}(["message: {label(verb)}"])' if verb else f'{m}(["answers when present"])'


def _msg_node(m: str, b: dict) -> str:
    verb, to = b["msg_nodes"][m]
    return f'{m}[["{label(verb)} to {label(b["seat_label"].get(to, to))}"]]'


def _tick_node(tid: str, p: dict, flag_none: bool) -> str:
    flag = ", principal present" if p["needs_principal"] else ""
    if flag_none:
        flag += ", no trigger found"
    return f'{tid}(["{p["band"]}: {p["name"]}{flag}"])'


def _end_arrow(src: str, dst: str, how: str, style: str) -> str:
    if style == "dashed":
        return f"  {src} -.-> {dst}"
    return f'  {src} ==>|"{label(how)}"| {dst}'


def _bound_cols(b: dict) -> set[str]:
    """The column nodes some folded bound arrow or condition points from or at."""
    return {d for (_, d, _, _) in b["ends"] if d.startswith("c_")} \
        | {x for (x, _, _) in b["cond_edges"] if x.startswith("c_")}


def _records(b: dict, marks: dict, keep, pad: str) -> list[str]:
    """The record boxes: one box per table, with its states inside. A column
    that a folded bound arrow writes is one more node, "table.col, bound",
    with a dotted arrow to each of its values. `keep` picks the nodes."""
    out: list[str] = []
    cols = _bound_cols(b)
    for t in sorted(b["states"]):
        rows = sorted(b["states"][t])
        shown = [(c, v) for (c, v) in rows if keep(sid(t, c, v))]
        mine = sorted({c for (c, _) in rows if c != "*" and cid(t, c) in cols
                       and keep(cid(t, c))})
        if not shown and not mine:
            continue
        out.append(f'{pad}subgraph tbl_{ident(t)}["{t}"]')
        for c in mine:
            out.append(f'{pad}  {cid(t, c)}["{label(t + "." + c)}, bound"]')
        for (c, v) in shown:
            s_ = sid(t, c, v)
            text = f"{t}, new row" if c == "*" else f"{c} = {v}"
            out.append(f'{pad}  {s_}["{label(text + marks.get(s_, ""))}"]')
        out.append(f"{pad}end")
    for t in sorted(b["states"]):
        for (c, v) in sorted(b["states"][t]):
            if c != "*" and cid(t, c) in cols and keep(cid(t, c)) and keep(sid(t, c, v)):
                out.append(f"{pad}{cid(t, c)} -.-> {sid(t, c, v)}")
    return out


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
        out += ["    " + _mode_node(m, b) for m in sorted(b["modes"]) if b["modes"][m][0] == lane]
        if not b["ticks"].get(lane) and not any(v[0] == lane for v in b["modes"].values()):
            out.append(f'    {ident("idle", lane)}["no tick wakes this seat"]')
        out.append("  end")
    out.append('  subgraph records["records"]')
    out += _records(b, marks, lambda n: True, "    ")
    out.append("  end")
    out.append(f'  {NOT_DERIVED}["not derived"]')
    for c in b["conds"]:
        out.append(f'  {cond_id(c)}(("{label(cond_label(c))}"))')
    for h in b["head_nodes"]:
        out.append(f'  {h}[("{label(h[2:].replace("_", ".", 1))}, new value")]')
    for (s, d, how) in b["cond_edges"]:
        out.append(f'  {s} -->|"{label(how)}"| {d}')
    out += ["  " + _msg_node(m, b) for m in sorted(b["msg_nodes"])]
    for (s, d, how) in b["msg_links"]:
        out.append(f'  {s} -->|"{how}"| {d}')
    for (s, tid, how) in b["triggers"]:
        out.append(f'  {s} -->|"{label(how)}"| {tid}')
    for (src, dst, how, style) in b["ends"]:
        out.append(_end_arrow(src, dst, how, style))
    out.append(f"  %% ticks with no trigger found: {', '.join(sorted(st['no_trigger'])) or 'none'}")
    out.append(f"  %% graph tools with no @op function: {', '.join(b['no_op']) or 'none'}")
    return out


def _read_targets(b: dict) -> set[str]:
    """The nodes some tick or condition reads: trigger sources, the column
    boxes that hold one, and the inputs of the conditions."""
    read = {s for (s, _, _) in b["triggers"]} | {s for (s, _, _) in b["cond_edges"]}
    for t, cv in b["states"].items():
        for (c, v) in cv:
            if c != "*" and sid(t, c, v) in read:
                read.add(cid(t, c))
    return read


def path_edges(b: dict) -> tuple[set, set, set]:
    """The edges of the path chart: (trigger and condition, end, member).

    No lane is a node. An end arrow goes from the tick to a node that some
    tick or condition reads. A column box reaches each of its values."""
    read = _read_targets(b)
    hub = sid("messages", "status", b["msg_default"] or "")
    trig = {(s, t, h) for (s, t, h) in b["triggers"] if s != hub} \
        | set(b["cond_edges"]) | set(b["msg_links"])
    ends = {(a, z, h) for (a, z, h, st) in b["ends"]
            if st == "end" and not a.startswith("lane_")
            and (z in read or z == b["end"]) and z != hub}
    member = set()
    for t, cv in b["states"].items():
        for (c, v) in cv:
            if c != "*":
                member.add((cid(t, c), sid(t, c, v), "member"))
    return trig, ends, member


def _w(edge: tuple) -> tuple[int, int]:
    """GUESS 6: the cost of one edge: (message hops, edges). A walk with fewer message
    hops wins, then a shorter walk. The scheduler's state-driven order comes
    first, and a message is a hop the chart takes only where no state leads on."""
    return (1 if edge[2] == "wakes" and edge[0].startswith("msg_") else 0, 1)


def _dist(edges: set, start: str, forward: bool) -> dict[str, tuple[int, int]]:
    """Least costs from `start`, along or against the edges (Dijkstra)."""
    import heapq
    nxt: dict[str, list[tuple]] = {}
    for e in sorted(edges):
        a, z = (e[0], e[1]) if forward else (e[1], e[0])
        nxt.setdefault(a, []).append((z, _w(e)))
    dist: dict[str, tuple[int, int]] = {start: (0, 0)}
    heap = [((0, 0), start)]
    while heap:
        d, n = heapq.heappop(heap)
        if d > dist.get(n, d):
            continue
        for (m, w) in nxt.get(n, ()):
            nd = (d[0] + w[0], d[1] + w[1])
            if m not in dist or nd < dist[m]:
                dist[m] = nd
                heapq.heappush(heap, (nd, m))
    return dist


def _shortest(edges: set, ds: dict, goal: str) -> set:
    """The edges on every least-cost walk from the start to `goal`."""
    dg = _dist(edges, goal, False)
    if goal not in ds:
        return set()
    d = ds[goal]
    out = set()
    for e in edges:
        a, z = e[0], e[1]
        if a in ds and z in dg:
            w = _w(e)
            if (ds[a][0] + w[0] + dg[z][0], ds[a][1] + w[1] + dg[z][1]) == d:
                out.add(e)
    return out


def path_nodes(b: dict, walk_only: bool = True) -> tuple[set[str], set]:
    """The nodes and edges of the delivery path.

    The main path is every shortest walk from the item's first state to the
    merged batch. A tick on it that waits on a head condition needs every
    one of its conditions, so the shortest walk to each condition is added,
    until nothing changes. A fix loop is a tick of band "fix" that a node on
    the path triggers and that ends back on the path. It is kept with that
    trigger and with its end arrows back to the path. With `walk_only` False, the chart keeps every node and
    edge the start reaches."""
    trig, ends, member = path_edges(b)
    edges = trig | ends | member
    ds = _dist(edges, b["start"], True)
    if not walk_only:
        keep = {e for e in edges if e[0] in ds}
        return set(ds), keep
    keep = _shortest(edges, ds, b["end"])
    # A tick's SQL is one WHERE: its literal triggers on different columns,
    # its JOINs and its head conditions all hold at once. A `drains` list is
    # any one of its states. So a tick on the path needs one walk into each
    # group: one group per (table, column) of its SQL states, one per JOIN,
    # one per head condition. Drains and message wakes are one group.
    groups: dict[str, dict[str, list[str]]] = {}
    for (src, t, h) in sorted(trig):
        if h == "drains" or h in ("wakes", "sends"):
            key = "any"
        elif src.startswith("s_"):
            key = src.rsplit("_", 1)[0] if h.startswith(("sql", "scheduler sql"))                 and not h.endswith("any row") else src
        else:
            key = src
        groups.setdefault(t, {}).setdefault(key, []).append(src)
    while True:
        on = {a for (a, _, _) in keep} | {z for (_, z, _) in keep}
        add = set()
        for t in sorted(on):
            for key, srcs in sorted(groups.get(t, {}).items()):
                if key == "any" or any(x in on for x in srcs):
                    continue
                best = min((x for x in srcs if x in ds), key=lambda x: ds[x], default=None)
                if best is not None:
                    add |= _shortest(edges, ds, best) | {e for e in trig if e[0] == best and e[1] == t}
        if not add - keep:
            break
        keep |= add
    on = {a for (a, _, _) in keep} | {z for (_, z, _) in keep}
    # A column box on the path brings its values.
    keep |= {e for e in member if e[0] in on}
    on = {a for (a, _, _) in keep} | {z for (_, z, _) in keep}
    loops = set()
    for (s, t, h) in sorted(trig):
        p = b["preds"].get(t)
        if s in on and p is not None and p["band"] == "fix" and t not in on:
            back = {(a, z, hh) for (a, z, hh) in edges if a == t and z in on}
            if back:
                loops |= back | {(s, t, h)}
    keep |= loops
    on = {a for (a, _, _) in keep} | {z for (_, z, _) in keep}
    return on, keep


def draw_path(b: dict, walk_only: bool = True) -> list[str]:
    """The delivery path of one change, from the item's first state to the merge."""
    on, keep = path_nodes(b, walk_only)
    _, ends, member = path_edges(b)
    marks = state_marks(b)
    out = ["flowchart LR",
           "  %% generated by probes/flowchart/flowchart.py; do not edit",
           "  %% the delivery path of one change, from the item's first state to the merge"]
    if b["end"] not in on:
        out.append("  %% the merged batch is not reachable from the item's first state")
    for lane in sorted(set(b["seats"]) | set(b["ticks"])):
        mine = [(tid, p) for tid, p in b["ticks"].get(lane, []) if tid in on]
        mm = sorted(m for m, (seat, _) in b["modes"].items() if seat == lane and m in on)
        if not mine and not mm:
            continue
        out.append(f'  subgraph lane_{ident(lane)}["{label(b["seat_label"].get(lane, lane))}"]')
        for tid, p in sorted(mine, key=lambda x: x[1]["seq"]):
            out.append("    " + _tick_node(tid, p, False))
        out += ["    " + _mode_node(m, b) for m in mm]
        out.append("  end")
    for m in sorted(b["msg_nodes"]):
        if m in on:
            out.append("  " + _msg_node(m, b))
    out += _records(b, marks, lambda n: n in on, "  ")
    for c in b["conds"]:
        if cond_id(c) in on:
            out.append(f'  {cond_id(c)}(("{label(cond_label(c))}"))')
    for h in b["head_nodes"]:
        if h in on:
            out.append(f'  {h}[("{label(h[2:].replace("_", ".", 1))}, new value")]')
    member_ids = {(a, z) for (a, z, _) in member}
    for (a, z, how) in sorted(e for e in keep if (e[0], e[1]) not in member_ids):
        arrow = "==>" if (a, z, how) in ends else "-->"
        out.append(f'  {a} {arrow}|"{label(how)}"| {z}')
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
    print("loop joins: " + "; ".join(f"{k} -> " + ", ".join(
        f"{p.relative_to(ROOT).as_posix()}:{f}" for (p, f) in v)
        for k, v in sorted(b["loop_joins"].items())))
    print("ticks with a loop end: " + ", ".join(sorted(st["loop_ticks"])))
    print("finer triggers replace the plain one: " + ", ".join(sorted(st["finer"])))
    print(f"ticks with a .tools file: {len(st['tools_ticks'])}; lanes with lane ends: "
          + ", ".join(sorted(st["lane_ends"])))
    print("conditions: " + "; ".join(cond_label(c) for c in b["conds"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
