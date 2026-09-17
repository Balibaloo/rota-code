"""
The map: where a thing is, and who touches it.

    python -m rota.tools.map fn stage_ref
    python -m rota.tools.map table refs --column resolves
    python -m rota.tools.map mode terminologist/unresolved
    python -m rota.tools.map file rota/core/db.py

Frame 21's scope agent made 96 tool calls and most of them found where
things were. `rota/roles/api.py` holds 8993 lines and a quarter of the
`execute` sites of the package, so an agent that asks who writes `refs`
reads 500 lines to find one call. This answers that question in one run.

The answer is not a regex over SQL. Forty-eight sites append a literal
table name to `ctx.writes`, and one generic f-string in `rota/core/db.py`
executes all of them, so SQL alone names `db.py` as the writer of every
table. The map joins five sources: the AST of the package, the schema,
the design graph, the `.tools` files and `REGISTRY`.

There is no cache. One run parses 87 files in about 0.7 s, which is under
the two-second budget, and the obvious cache key, the hash of the staged
tree, misses the unstaged edit that every implementing pass holds. The
`mode` query reads two files and builds no index.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .. import paths

# A fixture project's schema is not this system's schema. The map itself
# holds the patterns that name SQL, and a pattern is not a statement.
# Every other tool of this directory reads the database and belongs here:
# `rota/tools/audit.py` is a reader of `refs`.
SKIP_FILES = frozenset({"rota/testkit/samplerepo.py", "rota/tools/map.py"})

# The write pipeline. A raw statement here serves every table, so it is
# internal to the pipeline and not a second writer of one table.
PIPELINE_FILE = "rota/core/db.py"
VIEW_DICT = "PROVENANCE_VIEW_OF_TABLE"

SLOTS = frozenset({"FROM", "JOIN", "INTO", "UPDATE", "TABLE", "VIEW"})
# The verb is case-sensitive. A docstring that starts with "Update the
# brief" is prose, not a write.
WRITE_VERBS = frozenset({"INSERT", "UPDATE", "DELETE", "REPLACE"})
SQL_STARTS = ("SELECT", "INSERT", "UPDATE", "DELETE", "REPLACE", "WITH",
              "CREATE", "DROP", "ALTER", "PRAGMA")

_WORDS = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")
_SLOT_HINT = re.compile(r"\b(FROM|JOIN|INTO|UPDATE|TABLE|VIEW)\b", re.IGNORECASE)
# The name must be an identifier and an open bracket must follow it. Nine
# regex patterns in the package read `CREATE TABLE IF NOT EXISTS (\w+)`,
# and this is what keeps them out of the table set.
_CREATE_TABLE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(", re.IGNORECASE)
_CREATE_VIEW = re.compile(
    r"CREATE\s+VIEW\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s+AS\b", re.IGNORECASE)
_NOT_A_COLUMN = frozenset({"PRIMARY", "FOREIGN", "UNIQUE", "CHECK", "CONSTRAINT"})


# ---------------------------------------------------------------------------
# The records
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Definition:
    qual: str
    file: str
    first: int
    last: int
    deco: int

    @property
    def bare(self) -> str:
        return self.qual.rsplit(".", 1)[-1]


@dataclass(frozen=True)
class Call:
    bare: str
    chain: str
    file: str
    line: int
    where: str


@dataclass(frozen=True)
class Site:
    table: str
    role: str          # reads | writes
    kind: str          # pipeline | raw | indirect | dynamic | pipeline internal
    file: str
    line: int
    where: str
    verb: str = ""
    text: str = ""
    columns: tuple[str, ...] = ()


@dataclass(frozen=True)
class Table:
    file: str
    line: int
    columns: tuple[str, ...]
    view: bool


@dataclass
class Index:
    files: tuple[str, ...]
    defs: tuple[Definition, ...]
    calls: tuple[Call, ...]
    sites: tuple[Site, ...]
    tables: dict[str, Table]
    ops: dict[tuple[str, str], Definition | None] | None = None
    ops_by_line: frozenset[tuple[str, str]] = frozenset()


# ---------------------------------------------------------------------------
# One pass over the package
# ---------------------------------------------------------------------------

def _chain(node: ast.Attribute) -> str:
    """The dotted source text of a callee, `ctx.stage_ref` or `api.stage_ref`."""
    parts, cur = [], node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    parts.append(cur.id if isinstance(cur, ast.Name) else "<expr>")
    return ".".join(reversed(parts))


def _slot_open(parts: list[str]) -> bool:
    """True when a literal part ends on a slot keyword, so a slot holds the
    table name and the statement serves every table."""
    for part in parts:
        words = part.replace("(", " ").replace(",", " ").split()
        if words and words[-1].upper() in SLOTS:
            return True
    return False


def _view_aliases(tree: ast.AST) -> set[str]:
    names = {VIEW_DICT}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == VIEW_DICT and alias.asname:
                    names.add(alias.asname)
    return names


class _Reader(ast.NodeVisitor):
    """Everything one file says, before the tables are known."""

    def __init__(self, rel: str, aliases: set[str]) -> None:
        self.rel = rel
        self.aliases = aliases
        self.stack: list[str] = []
        self.fns: list[str] = []
        self.defs: list[Definition] = []
        self.calls: list[Call] = []
        self.statements: list[tuple[str, int, bool, str]] = []
        self.pipeline: list[tuple[str, int, tuple[str, ...], str]] = []
        self.indirect: list[tuple[int, str]] = []
        self.creates: list[tuple[str, int]] = []
        self.docstrings: set[int] = set()

    @property
    def where(self) -> str:
        return self.fns[-1] if self.fns else "<module>"

    def _docstring(self, node) -> None:
        """Mark the docstring of a body. Prose that says "from items" is not
        a reader of `items`, and twelve docstrings read as one."""
        body = getattr(node, "body", None)
        if body and isinstance(body[0], ast.Expr):
            first = body[0].value
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                self.docstrings.add(id(first))

    def visit_Module(self, node: ast.Module) -> None:
        self._docstring(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._docstring(node)
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def _function(self, node) -> None:
        self._docstring(node)
        self.stack.append(node.name)
        qual = ".".join(self.stack)
        lines = [d.lineno for d in node.decorator_list] + [node.lineno]
        self.defs.append(Definition(qual, self.rel, node.lineno,
                                    getattr(node, "end_lineno", node.lineno),
                                    min(lines)))
        self.fns.append(qual)
        self.generic_visit(node)
        self.fns.pop()
        self.stack.pop()

    visit_FunctionDef = _function
    visit_AsyncFunctionDef = _function

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Name):
            self.calls.append(Call(func.id, func.id, self.rel, node.lineno, self.where))
        elif isinstance(func, ast.Attribute):
            self.calls.append(
                Call(func.attr, _chain(func), self.rel, node.lineno, self.where))
            self._pipeline_write(node, func)
        self.generic_visit(node)

    def _pipeline_write(self, node: ast.Call, func: ast.Attribute) -> None:
        # `ctx.writes.append(("refs", row_id, {...}))` is the write path.
        # Forty-eight of these carry a literal table name.
        if func.attr != "append" or not isinstance(func.value, ast.Attribute):
            return
        if func.value.attr != "writes" or not node.args:
            return
        first = node.args[0]
        if not isinstance(first, ast.Tuple) or not first.elts:
            return
        head = first.elts[0]
        if not (isinstance(head, ast.Constant) and isinstance(head.value, str)):
            return
        columns: tuple[str, ...] = ()
        for part in first.elts[1:]:
            if isinstance(part, ast.Dict):
                columns = tuple(k.value for k in part.keys
                                if isinstance(k, ast.Constant)
                                and isinstance(k.value, str))
                break      # the first dict holds the values, the record says so
        self.pipeline.append((head.value, node.lineno, columns, self.where))

    def visit_Name(self, node: ast.Name) -> None:
        # A read of the view dict is a read of every view it names.
        if isinstance(node.ctx, ast.Load) and node.id in self.aliases and self.fns:
            self.indirect.append((node.lineno, self.where))

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str) and id(node) not in self.docstrings:
            self._text(node.value, node.lineno, False)

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        parts = [p.value for p in node.values
                 if isinstance(p, ast.Constant) and isinstance(p.value, str)]
        if parts:
            self._text("".join(parts), node.lineno, _slot_open(parts))
        # The literal parts are read above. Only the slots hold calls.
        for value in node.values:
            if isinstance(value, ast.FormattedValue):
                self.visit(value)

    def _text(self, text: str, line: int, dynamic: bool) -> None:
        if _CREATE_TABLE.search(text):
            self.creates.append((text, line))
        if dynamic or _SLOT_HINT.search(text):
            self.statements.append((text, line, dynamic, self.where))


# ---------------------------------------------------------------------------
# The schema
# ---------------------------------------------------------------------------

def _depths(text: str) -> list[int]:
    """The bracket depth at each character, with quoted text held flat."""
    out, depth, quote = [], 0, ""
    for ch in text:
        if quote:
            out.append(depth)
            if ch == quote:
                quote = ""
            continue
        if ch == ")":
            depth -= 1
        out.append(depth)
        if ch in "'\"":
            quote = ch
        elif ch == "(":
            depth += 1
    return out


def _body(text: str, start: int) -> str:
    """The text inside the first bracket pair at or after `start`."""
    depth, quote, begin = 0, "", -1
    for i in range(start, len(text)):
        ch = text[i]
        if quote:
            if ch == quote:
                quote = ""
            continue
        if ch in "'\"":
            quote = ch
        elif ch == "(":
            depth += 1
            if depth == 1:
                begin = i + 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and begin >= 0:
                return text[begin:i]
    return text[begin:] if begin >= 0 else ""


def _items(body: str) -> list[str]:
    """The comma-separated items of a bracket body, at the top level only."""
    out, depth, start, quote = [], 0, 0, ""
    for i, ch in enumerate(body):
        if quote:
            if ch == quote:
                quote = ""
            continue
        if ch in "'\"":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            out.append(body[start:i])
            start = i + 1
    out.append(body[start:])
    return [s.strip() for s in out if s.strip()]


def _table_columns(body: str) -> tuple[str, ...]:
    columns = []
    for item in _items(body):
        words = _WORDS.findall(item)
        if words and words[0].upper() not in _NOT_A_COLUMN:
            columns.append(words[0])
    return tuple(columns)


def _view_columns(body: str) -> tuple[str, ...]:
    """The output names of the last top-level SELECT of a view."""
    depth = _depths(body)
    heads = [m.start() for m in re.finditer(r"\bSELECT\b", body, re.IGNORECASE)
             if depth[m.start()] == 0]
    if not heads:
        return ()
    head = heads[-1]
    tails = [m.start() for m in re.finditer(r"\bFROM\b", body, re.IGNORECASE)
             if depth[m.start()] == 0 and m.start() > head]
    columns = []
    for item in _items(body[head + len("SELECT"):tails[0] if tails else len(body)]):
        alias = re.search(r"\bAS\s+(\w+)\s*$", item, re.IGNORECASE)
        name = alias.group(1) if alias else item.split(".")[-1].strip()
        if name.isidentifier():
            columns.append(name)
    return tuple(columns)


def _schema_tables(path: Path, rel: str) -> dict[str, Table]:
    text = path.read_text(encoding="utf-8")
    out: dict[str, Table] = {}
    for match in _CREATE_TABLE.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        out[match.group(1)] = Table(
            rel, line, _table_columns(_body(text, match.end() - 1)), False)
    for match in _CREATE_VIEW.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        end = text.find(";", match.end())
        body = text[match.end():end if end > 0 else len(text)]
        out[match.group(1)] = Table(rel, line, _view_columns(body), True)
    return out


# ---------------------------------------------------------------------------
# The index
# ---------------------------------------------------------------------------

def _named(text: str, known: dict[str, Table]) -> list[str]:
    """The known tables a statement names, each after a slot keyword."""
    words = _WORDS.findall(text)
    statement = text.strip().upper().startswith(SQL_STARTS)
    out = []
    for i, word in enumerate(words[:-1]):
        if word.upper() not in SLOTS or words[i + 1] not in known:
            continue
        # An upper-case slot word is SQL wherever it sits, which is how a
        # column fragment that starts with `id,` keeps its table. A
        # lower-case one is prose unless the text is a statement.
        if word != word.upper() and not statement:
            continue
        if words[i + 1] not in out:
            out.append(words[i + 1])
    return out


def _verb(text: str) -> str:
    head = text.strip().split(None, 1)
    return head[0] if head else ""


def _statement_sites(rel: str, text: str, line: int, dynamic: bool,
                     where: str, tables: dict[str, Table]) -> list[Site]:
    """The table sites of one string constant."""
    verb = _verb(text)
    role = "writes" if verb in WRITE_VERBS else "reads"
    out = []
    # A slot holds the table name, so the statement serves every table.
    # The statement can still name a second table beside the slot.
    if dynamic and text.strip().upper().startswith(SQL_STARTS):
        out.append(Site("", role, "dynamic", rel, line, where, verb=verb))
    kind = "pipeline internal" if rel == PIPELINE_FILE else "raw"
    out.extend(Site(table, role, kind, rel, line, where, verb=verb, text=text)
               for table in _named(text, tables))
    return out


def build_index(root: Path | None = None) -> Index:
    """Parse the package once. About 0.7 s for 87 files."""
    root = Path(root) if root else paths.REPO
    files: list[str] = []
    defs: list[Definition] = []
    calls: list[Call] = []
    statements: list[tuple[str, str, int, bool, str]] = []
    pipeline: list[tuple[str, str, int, tuple[str, ...], str]] = []
    indirect: list[tuple[str, int, str]] = []
    creates: list[tuple[str, str, int]] = []
    views: tuple[str, ...] = ()

    for path in sorted((root / "rota").rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        if rel in SKIP_FILES:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        reader = _Reader(rel, _view_aliases(tree))
        reader.visit(tree)
        files.append(rel)
        defs.extend(reader.defs)
        calls.extend(reader.calls)
        statements.extend((rel, *s) for s in reader.statements)
        pipeline.extend((rel, *p) for p in reader.pipeline)
        indirect.extend((rel, *i) for i in reader.indirect)
        creates.extend((rel, *c) for c in reader.creates)
        if rel == PIPELINE_FILE:
            views = _dict_values(tree, VIEW_DICT)

    schema = paths.SCHEMA.relative_to(paths.REPO)
    tables = _schema_tables(root / schema, schema.as_posix())
    for rel, text, line in creates:
        match = _CREATE_TABLE.search(text)
        if match and match.group(1) not in tables:
            tables[match.group(1)] = Table(
                rel, line, _table_columns(_body(text, match.end() - 1)), False)

    sites: list[Site] = []
    for rel, table, line, columns, where in pipeline:
        sites.append(Site(table, "writes", "pipeline", rel, line, where,
                          columns=columns))
    for rel, text, line, dynamic, where in statements:
        sites.extend(_statement_sites(rel, text, line, dynamic, where, tables))
    for rel, line, where in indirect:
        for view in views:
            sites.append(Site(view, "reads", "indirect", rel, line, where))

    sites.sort(key=lambda s: (s.file, s.line, s.table))
    return Index(tuple(files), tuple(defs), tuple(calls), tuple(sites), tables)


def _dict_values(tree: ast.AST, name: str) -> tuple[str, ...]:
    """The string values of one module-level dict literal, read by `ast`.
    The map never imports `rota.core.db`, which opens nothing but pulls in
    the whole write pipeline."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Dict):
            continue
        if any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return tuple(v.value for v in node.value.values
                         if isinstance(v, ast.Constant) and isinstance(v.value, str))
    return ()


def _rel(path: str | Path) -> str:
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(paths.REPO).as_posix()
    except ValueError:
        return candidate.as_posix()


def ops(index: Index) -> dict[tuple[str, str], Definition | None]:
    """Every registered op, with the definition that implements it. The five
    `cite` ops register in a loop with no decorator, so `REGISTRY` is the
    list and the source is not."""
    if index.ops is None:
        from ..roles import api      # no file open, no database, 0.04 s

        out: dict[tuple[str, str], Definition | None] = {}
        by_line = set()
        for pair, fn in api.REGISTRY.items():
            rel = _rel(fn.__code__.co_filename)
            line = fn.__code__.co_firstlineno
            covers = [d for d in index.defs
                      if d.file == rel and d.deco <= line <= d.last]
            # The five `cite` ops carry the name of the artefact and the
            # source calls them `cite`, so the line decides when the name
            # does not: the innermost definition is the implementation.
            named = next((d for d in covers if d.bare == fn.__name__), None)
            if named is None and covers:
                by_line.add(pair)
            out[pair] = named or (
                min(covers, key=lambda d: d.last - d.first) if covers else None)
        index.ops, index.ops_by_line = out, frozenset(by_line)
    return index.ops


def _by_line(index: Index, pair: tuple[str, str]) -> str:
    """The mark of a join that the line made and the name did not. The
    function `REGISTRY` holds is then not the definition, and a wrapper
    that hides the implementation must stay visible."""
    return " (by line)" if pair in index.ops_by_line else ""


def _edges(kinds: tuple[str, ...], root: Path | None) -> list[dict]:
    """The design graph, read by `json`. `rota.design.graph` validates the
    file and the map only reads it."""
    design = Path(root) / "rota" / "design" if root else paths.DESIGN
    data = json.loads((design / "graph.json").read_text(encoding="utf-8"))
    return [e for e in data["edges"] if e.get("type") in kinds]


def op_table(root: Path | None = None) -> list[tuple[str, str]]:
    """The (artefact, verb) pairs of the design graph."""
    return sorted({(e["t"], e["v"]) for e in _edges(("reads", "writes"), root)})


def message_edges(root: Path | None = None) -> list[tuple[str, str, str]]:
    """The (sender, verb, recipient) triples of the design graph. The 119
    `msg.` lines of the `.tools` files join here, never to `REGISTRY`."""
    return sorted({(e["s"], e["v"], e["t"]) for e in _edges(("messages",), root)})


# ---------------------------------------------------------------------------
# The queries
# ---------------------------------------------------------------------------

def _word(column: str, text: str) -> bool:
    return bool(re.search(rf"\b{re.escape(column)}\b", text))


def _site_line(site: Site, column: str | None) -> str:
    if site.kind == "pipeline":
        mark = "pipeline cols: " + ", ".join(site.columns) if site.columns else "pipeline"
    elif site.kind == "indirect":
        mark = f"indirect via {VIEW_DICT}"
    else:
        mark = site.kind
        if column and site.text and _word(column, site.text):
            mark += ", word match"
    return f"{site.file}:{site.line} {site.where} ({mark})"


def _names_column(site: Site, column: str) -> bool:
    if site.kind == "pipeline":
        return column in site.columns
    return bool(site.text) and _word(column, site.text)


def query_fn(index: Index, name: str, callers: int = 20) -> str:
    found = sorted((d for d in index.defs if d.bare == name or d.qual == name),
                   key=lambda d: (d.file, d.first))
    if not found:
        raise LookupError(name)
    shared = len(found) > 1
    out = []
    if shared:
        out.append(f"{len(found)} definitions share the name")
    # Each definition carries its own ops and tables. A merged answer says
    # `reads config` and names no definition that reads it.
    for definition in found:
        out.extend(_fn_block(index, definition, callers, not shared))
    if shared:
        # One list for all of them: a call is matched by the bare name and
        # never resolved, so no fact splits it between the definitions.
        total, lines = _callers(index, {d.bare for d in found}, callers)
        out.append(f"callers ({total}) by name, shared by {len(found)} definitions")
        out.extend(lines)
    return "\n".join(out)


def _callers(index: Index, names: set[str], limit: int) -> tuple[int, list[str]]:
    hits = sorted((c for c in index.calls if c.bare in names),
                  key=lambda c: (c.file, c.line))
    lines = [f"{c.file}:{c.line} {c.chain} in {c.where}" for c in hits[:limit]]
    if len(hits) > limit:
        lines.append(f"... {len(hits) - limit} more, --callers <n> to see them")
    return len(hits), lines


def _fn_block(index: Index, definition: Definition, callers: int,
              with_callers: bool) -> list[str]:
    out = [f"def {definition.qual} {definition.file}:"
           f"{definition.first}-{definition.last}"]
    out.extend(f"op {pair[0]}.{pair[1]}{_by_line(index, pair)}"
               for pair, implementation in sorted(ops(index).items())
               if implementation == definition)
    seen = []
    for site in index.sites:
        if site.file != definition.file or site.where != definition.qual:
            continue
        if site.table and (site.role, site.table, site.kind) not in seen:
            seen.append((site.role, site.table, site.kind))
    out.extend(f"{role} {table} ({kind})" for role, table, kind in sorted(seen))
    if with_callers:
        total, lines = _callers(index, {definition.bare}, callers)
        out.append(f"callers ({total})")
        out.extend(lines)
    return out


def query_table(index: Index, name: str, column: str | None = None) -> str:
    table = index.tables.get(name)
    if table is None:
        raise LookupError(name)
    out = [f"{'view' if table.view else 'schema'} {table.file}:{table.line}"]
    if table.columns:
        out.append("columns " + ", ".join(table.columns))
    sites = [s for s in index.sites if s.table == name]
    if column:
        sites = [s for s in sites if _names_column(s, column)]
    for role, header in (("writes", "writers"), ("reads", "readers")):
        rows = [s for s in sites if s.role == role]
        out.append(f"{header} ({len(rows)})")
        out.extend(_site_line(s, column) for s in rows)
    return "\n".join(out)


def _tool_line(entry: str, role: str, registry, messages) -> str:
    artefact, _, attr = entry.partition(".")
    if artefact == "msg":
        for sender, verb, recipient in messages:
            if sender == role and f"{verb}_{recipient}" == attr:
                return f"{entry} -> message {verb} to {recipient}"
        return f"{entry} -> no messages edge"
    # `batches.judge_touch` keeps its underscore, two other multi-word
    # verbs carry a space, so the plain name is tried first.
    fn = registry.get((artefact, attr)) or registry.get((artefact, attr.replace("_", " ")))
    if fn is None:
        return f"{entry} -> not in REGISTRY"
    return (f"{entry} -> {fn.__name__} "
            f"{_rel(fn.__code__.co_filename)}:{fn.__code__.co_firstlineno}")


def query_mode(spec: str) -> str:
    """The ops of one mode. This query reads the `.tools` files and
    `REGISTRY` only, so it never builds the index."""
    role, _, mode = spec.partition("/")
    base = paths.PROMPTS / role / f"{mode}.tools"
    if not mode or not base.exists():
        raise LookupError(spec)
    out = [f"tools {_rel(base)}"]
    # A variant file overrides the base. The map lists it and never
    # resolves it: the resolution belongs to `prompts.mode_tools()`.
    out.extend(f"override {_rel(p)}"
               for p in sorted((paths.PROMPTS / role).glob(f"*/{mode}.tools")))
    from ..roles import api

    messages = message_edges()
    for line in base.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if entry and not entry.startswith("#"):
            out.append(_tool_line(entry, role, api.REGISTRY, messages))
    return "\n".join(out)


def query_file(index: Index, path: str) -> str:
    rel = str(path).replace("\\", "/")
    if rel not in index.files:
        raise LookupError(path)
    out = [f"def {d.qual} {d.first}-{d.last}"
           for d in sorted((d for d in index.defs
                            if d.file == rel and "." not in d.qual),
                           key=lambda d: d.first)]
    sites = [s for s in index.sites if s.file == rel]
    counts = Counter((s.role, s.table) for s in sites if s.table)
    out.extend(f"{role} {table} ({n})" for (role, table), n in sorted(counts.items()))
    out.extend(f"{s.role} dynamic {s.verb} {s.where}:{s.line}"
               for s in sites if s.kind == "dynamic")
    for pair, definition in sorted(ops(index).items()):
        if definition is not None and definition.file == rel:
            out.append(f"op {pair[0]}.{pair[1]} -> {definition.qual} "
                       f"{definition.first}{_by_line(index, pair)}")
    return "\n".join(out)


QUERIES = ("file", "fn", "mode", "table")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m rota.tools.map",
        description="Where a thing is, and who touches it.",
        epilog="A caller is one hop. A caller that reaches the function "
               "through a helper is not in the list, so ask for the helper "
               "as well. A variant `.tools` file is listed, not resolved.")
    parser.add_argument("query", nargs="?", choices=QUERIES)
    parser.add_argument("name", nargs="?",
                        help="a function, a table or a view, <role>/<mode>, or a path")
    parser.add_argument("--column", help="keep the sites that name this column")
    parser.add_argument("--callers", type=int, default=20,
                        help="how many callers to list, 0 hides the list")
    args = parser.parse_args(argv)
    if not args.query or not args.name:
        parser.print_help()
        return 2
    try:
        # `mode` reads two files. The other three need the whole tree.
        if args.query == "mode":
            text = query_mode(args.name)
        elif args.query == "table":
            text = query_table(build_index(), args.name, args.column)
        elif args.query == "fn":
            text = query_fn(build_index(), args.name, args.callers)
        else:
            text = query_file(build_index(), args.name)
    except LookupError:
        print(f"no {args.query} named {args.name}")
        return 1
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
