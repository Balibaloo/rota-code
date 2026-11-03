"""
The harvest of commitment witnesses, deterministic, with no model.

Design B step 2 of `plans/design-onboarding-2026-11-03.md`: before any
request, a tool reads the tree for the lines where a project states a
promise to the outside. Each line becomes a candidate with its path, its
line number, its text copied from the file and its kind. The binding rule
of step 4 then binds each candidate to source files, by its kind.

The kinds are those of step 3, as the deep dive of the same date measured
them in section 1 (5 of 5 key commitments on icalendar, 2 of 5 on click):

    metadata          pyproject `name`, `description`, `requires-python`,
                      each dependency and each `[project.scripts]` entry
    doc_claim         a README or docs line that names a standard, or says
                      compatible, supports, conforms or complies
    preservation      a docs line, a comment or a docstring line that says
                      preserve, round trip or "for compatibility with existing"
    numeric_default   a numeric default in a signature of a module that cites
                      a standard, at the docstring line that names the number
    issue_comment     a comment that cites an issue or a pull request
    export            the public names of a top-level `__init__.py`, one
                      candidate for each file
    test_witness      a test file that names a symbol that holds a numeric
                      default or a preservation line, for the Tester

Two witnesses that state one number in two units of one family are kept
side by side: each one names the other in `contradicts`.

Only this module writes `commitment_candidates` and `candidate_bindings`
(law 1). The id derives from the content (law 14).
"""
from __future__ import annotations

import ast
import hashlib
import io
import json
import re
import sqlite3
import tokenize
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from . import indexer

KINDS = ("metadata", "doc_claim", "preservation", "numeric_default",
         "issue_comment", "export", "test_witness")

RULES = ("standard", "dependency", "entry_point", "exports", "witness_file",
         "symbol", "project_wide")

# The second form is the Sphinx role, as in ":rfc:`5545`".
STD = re.compile(r"\b(RFC|PEP|ISO|IEEE|ECMA|POSIX)(?:[\s-]?|:`)(\d+)", re.I)
CLAIM = re.compile(r"\b(compatib\w*|supports?|conform\w*|complian\w*|complies)\b",
                   re.I)
PRESERVE = re.compile(r"preserv\w*|round[- ]?trip\w*|for compatibility with existing",
                      re.I)
ISSUE = re.compile(r"\bissue\s*#?\d+|(?<![\w&])#\d{3,}\b|/issues/\d+|/pull/\d+",
                   re.I)
UNIT = re.compile(r"\b(\d+)[\s-]+(octets?|bytes?|characters?|chars?|code ?points?|"
                  r"seconds?|secs?|milliseconds?|ms|minutes?|days?|columns?)\b",
                  re.I)
# A unit's family. Two units of one family on one number state one fact two
# ways, so the pair is a contradiction to keep (the design, step 3).
FAMILY = {"octet": "size", "byte": "size", "character": "size", "char": "size",
          "codepoint": "size", "code point": "size", "column": "size",
          "second": "time", "sec": "time", "millisecond": "time", "ms": "time",
          "minute": "time", "day": "time"}
# A history file restates old behaviour. Its lines are not promises now.
HISTORY = re.compile(r"^(CHANGES|CHANGELOG|HISTORY|NEWS)", re.I)
TEST_DIRS = ("tests", "test", "testing")
# A symbol name this short or a dunder name matches too many test lines.
MIN_SYMBOL = 5


@dataclass
class Candidate:
    kind: str
    path: str
    line: int
    text: str
    symbol: str = ""
    detail: dict = field(default_factory=dict)
    contradicts: list = field(default_factory=list)

    @property
    def id(self) -> str:
        return candidate_id(self.kind, self.path, self.line, self.text)


def candidate_id(kind: str, path: str, line: int, text: str) -> str:
    """The id of a candidate. It hashes the witness, so the identity derives
    from the content (law 14), as `db.ruled_ref_id` does."""
    key = f"{kind}|{path}|{line}|{text}".encode("utf-8")
    return "cc_" + hashlib.sha256(key).hexdigest()[:12]


# ---- the tree ----------------------------------------------------------------

class Tree:
    """The authored files of one root, read once.

    The file list is the indexer's walk, so a bound path is a path the index
    holds."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.files: dict[str, Path] = {}
        if self.root.is_dir():
            for path in indexer.walk(self.root):
                self.files[path.relative_to(self.root).as_posix()] = path
        self._text: dict[str, str] = {}
        self._ast: dict[str, ast.Module | None] = {}

    def text(self, rel: str) -> str:
        if rel not in self._text:
            try:
                self._text[rel] = self.files[rel].read_text(encoding="utf-8",
                                                            errors="replace")
            except OSError:
                self._text[rel] = ""
        return self._text[rel]

    def lines(self, rel: str) -> list[str]:
        return self.text(rel).splitlines()

    def tree(self, rel: str) -> ast.Module | None:
        if rel not in self._ast:
            try:
                self._ast[rel] = ast.parse(self.text(rel))
            except (SyntaxError, ValueError):
                self._ast[rel] = None
        return self._ast[rel]

    def source(self) -> list[str]:
        """The package's Python files: no test, no docs, no example, and no
        file under a dot directory such as `.github`."""
        return [rel for rel in self.files if rel.endswith(".py")
                and not is_test(rel) and not rel.startswith(("docs/", "examples/"))
                and not any(p.startswith(".") for p in rel.split("/")[:-1])]

    def tests(self) -> list[str]:
        return [rel for rel in self.files if rel.endswith(".py") and is_test(rel)]

    def docs(self) -> list[str]:
        out = []
        for rel in self.files:
            name = rel.split("/")[-1]
            if HISTORY.match(name):
                continue
            if (name.lower().startswith("readme") and "/" not in rel) or (
                    rel.startswith("docs/") and name.endswith((".rst", ".md", ".txt"))):
                out.append(rel)
        return out

    def modules(self) -> dict[str, str]:
        """The dotted module name of each source file, to its path."""
        out = {}
        for rel in self.source():
            parts = rel[:-3].split("/")
            if parts[0] == "src":
                parts = parts[1:]
            if parts[-1] == "__init__":
                parts = parts[:-1]
            if parts:
                out[".".join(parts)] = rel
        return out


def is_test(rel: str) -> bool:
    parts = rel.split("/")
    return (any(p in TEST_DIRS for p in parts[:-1]) or parts[-1].startswith("test_")
            or parts[-1] == "conftest.py")


def _spans(module: ast.Module) -> list[tuple[int, int, str]]:
    """Each definition's first line, last line and dotted name."""
    out = []

    def visit(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = f"{prefix}{child.name}"
                out.append((child.lineno, child.end_lineno or child.lineno, name))
                visit(child, name + ".")
    visit(module, "")
    return out


def holder(spans: list[tuple[int, int, str]], line: int) -> str:
    """The dotted name of the innermost definition that holds `line`."""
    held = [s for s in spans if s[0] <= line <= s[1]]
    return min(held, key=lambda s: s[1] - s[0])[2] if held else ""


def _prose_lines(module: ast.Module | None, src: str) -> list[tuple[int, str]]:
    """The line numbers of the comments and the docstrings of one file."""
    comments: set[int] = set()
    found: set[int] = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                comments.add(tok.start[0])
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    if module is not None:
        for node in ast.walk(module):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)):
                body = node.body
                if (body and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Constant)
                        and isinstance(body[0].value.value, str)):
                    found.update(range(body[0].lineno,
                                       (body[0].end_lineno or body[0].lineno) + 1))
    return sorted([(n, "comment") for n in comments]
                  + [(n, "docstring") for n in found - comments])


# ---- the kinds -----------------------------------------------------------------

def _metadata(tree: Tree, out: list[Candidate]) -> None:
    if "pyproject.toml" not in tree.files:
        return
    lines = tree.lines("pyproject.toml")
    try:
        project = tomllib.loads(tree.text("pyproject.toml")).get("project", {})
    except tomllib.TOMLDecodeError:
        return

    def find(pattern: str) -> int:
        rx = re.compile(pattern)
        return next((i for i, text in enumerate(lines, 1) if rx.search(text)), 0)

    def add(n: int, **detail) -> None:
        if n:
            out.append(Candidate("metadata", "pyproject.toml", n, lines[n - 1],
                                 detail=detail))
    for key in ("name", "description", "requires-python"):
        if isinstance(project.get(key), str):
            add(find(r"^\s*" + re.escape(key) + r"\s*="), field=key)
    for dep in project.get("dependencies", []) or []:
        name = re.split(r"[<>=!~;\[ ]", dep, maxsplit=1)[0].strip()
        add(find(r"[\"']" + re.escape(dep) + r"[\"']") or find(re.escape(name)),
            field="dependency", dep=name)
    for script, target in (project.get("scripts", {}) or {}).items():
        add(find(r"^\s*[\"']?" + re.escape(script) + r"[\"']?\s*="),
            field="script", script=script, target=target)


def _docs(tree: Tree, out: list[Candidate]) -> None:
    for rel in tree.docs():
        lines = tree.lines(rel)
        for n, text in enumerate(lines, 1):
            if STD.search(text) or CLAIM.search(text):
                out.append(Candidate("doc_claim", rel, n, text))
            if PRESERVE.search(text):
                first, last = _paragraph(lines, n)
                out.append(Candidate("preservation", rel, first,
                                     "\n".join(lines[first - 1:last]),
                                     detail={"match_line": n, "last_line": last}))


# A preservation sentence often names its subject in the line before, as
# "This preserves the raw value" at `parse-errors.rst` 47 names `vBroken` at
# 46. So the docs witness quotes its paragraph, at most this many lines on
# each side of the line that matched.
PARAGRAPH_REACH = 2


def _paragraph(lines: list[str], n: int) -> tuple[int, int]:
    first = n
    while first > 1 and n - first < PARAGRAPH_REACH and lines[first - 2].strip():
        first -= 1
    last = n
    while last < len(lines) and last - n < PARAGRAPH_REACH and lines[last].strip():
        last += 1
    return first, last


def _source(tree: Tree, out: list[Candidate]) -> None:
    for rel in tree.source():
        src, module = tree.text(rel), tree.tree(rel)
        lines = src.splitlines()
        spans = _spans(module) if module is not None else []
        for n, where in _prose_lines(module, src):
            text = lines[n - 1] if n <= len(lines) else ""
            if PRESERVE.search(text):
                out.append(Candidate("preservation", rel, n, text,
                                     symbol=holder(spans, n), detail={"where": where}))
            if where == "comment" and ISSUE.search(text):
                out.append(Candidate("issue_comment", rel, n, text,
                                     symbol=holder(spans, n)))
        if module is not None and STD.search(src):
            _numeric_defaults(rel, module, lines, out)


def _numeric_defaults(rel: str, module: ast.Module, lines: list[str],
                      out: list[Candidate]) -> None:
    for node in ast.walk(module):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        args = node.args
        pos = args.posonlyargs + args.args
        pairs = list(zip(pos[len(pos) - len(args.defaults):], args.defaults))
        pairs += [(a, d) for a, d in zip(args.kwonlyargs, args.kw_defaults)
                  if d is not None]
        doc = node.body[0] if node.body else None
        doc_span = ((doc.lineno, doc.end_lineno or doc.lineno)
                    if isinstance(doc, ast.Expr) and isinstance(doc.value, ast.Constant)
                    and isinstance(doc.value.value, str) else (0, -1))
        for arg, default in pairs:
            value = default.value if isinstance(default, ast.Constant) else None
            # A bool is an int in Python, and 0, 1 and -1 are sentinels.
            if type(value) not in (int, float) or value in (0, 1, -1):
                continue
            word = re.compile(r"(?<![\w.])%s(?![\w.])" % re.escape(str(value)))
            beside = next((n for n in range(doc_span[0], doc_span[1] + 1)
                           if word.search(lines[n - 1])), 0)
            # The docstring line carries the unit, so it is the witness. The
            # signature line stays in the detail.
            n = beside or default.lineno
            out.append(Candidate(
                "numeric_default", rel, n, lines[n - 1], symbol=node.name,
                detail={"arg": arg.arg, "value": value,
                        "signature_line": default.lineno,
                        "signature": lines[default.lineno - 1]}))


def _exports(tree: Tree, out: list[Candidate]) -> None:
    for rel in tree.source():
        parts = rel.split("/")
        # The top-level package only: <pkg>/__init__.py or src/<pkg>/__init__.py.
        if parts[-1] != "__init__.py" or not (
                len(parts) == 2 or (len(parts) == 3 and parts[0] == "src")):
            continue
        module = tree.tree(rel)
        if module is None:
            continue
        names, line = [], 0
        for node in module.body:
            if isinstance(node, ast.Assign) and any(
                    getattr(t, "id", "") == "__all__" for t in node.targets):
                try:
                    names, line = list(ast.literal_eval(node.value)), node.lineno
                except (ValueError, SyntaxError):
                    pass
        if not names:
            # The explicit re-export form, `from .x import A as A`.
            for node in module.body:
                if isinstance(node, ast.ImportFrom) and node.level >= 1:
                    for alias in node.names:
                        if alias.asname and alias.asname == alias.name:
                            names.append(alias.name)
                            line = line or node.lineno
        if names:
            out.append(Candidate("export", rel, line, tree.lines(rel)[line - 1],
                                 detail={"names": sorted(set(map(str, names)))}))


def _test_witnesses(tree: Tree, out: list[Candidate]) -> None:
    """A test file that names a symbol holding a witness. The deep dive found
    104 rows when the words came from the quotes, 76 of them `to_ical`. Tied to
    the holding symbol, the kind names few files (the dive, section 1)."""
    held: dict[str, str] = {}
    for c in out:
        if c.kind in ("numeric_default", "preservation") and c.symbol:
            # Only a module-level definition counts. A method name such as
            # `value` or `parts` names many unrelated test lines.
            name = c.symbol
            if "." not in name and len(name) >= MIN_SYMBOL and not name.startswith("__"):
                held.setdefault(name, c.path)
    if not held:
        return
    for rel in sorted(tree.tests()):
        seen: dict[str, int] = {}
        lines = tree.lines(rel)
        # A name token, not a word in a string: "VALUE=DATE" in a test's
        # data does not name the `VALUE` enum.
        try:
            for tok in tokenize.generate_tokens(io.StringIO(tree.text(rel)).readline):
                if tok.type == tokenize.NAME and tok.string in held:
                    seen.setdefault(tok.string, tok.start[0])
        except (tokenize.TokenError, IndentationError, SyntaxError):
            continue
        for symbol, n in sorted(seen.items()):
            out.append(Candidate("test_witness", rel, n, lines[n - 1], symbol=symbol,
                                 detail={"held_by": held[symbol]}))


def _contradictions(tree: Tree, out: list[Candidate]) -> None:
    """Pair a numeric default's line with each line that states its number in
    another unit of one family, for example "75 octets" at `parser/string.py`
    122 and "75 characters" at `docs/explanation/api-design.rst` 61 (the
    review, finding 5). A line that is no candidate yet joins with the seed's
    kind, so both sides can be quoted."""
    by_place = {(c.path, c.line): c for c in out}
    pool = tree.docs() + tree.source()
    for seed in [c for c in out if c.kind == "numeric_default"]:
        value = str(seed.detail.get("value"))
        units = {_unit(m) for m in UNIT.finditer(seed.text) if m.group(1) == value}
        families = {FAMILY[u] for u in units if u in FAMILY}
        if not families:
            continue
        for rel in pool:
            for n, text in enumerate(tree.lines(rel), 1):
                if (rel, n) == (seed.path, seed.line):
                    continue
                other = {_unit(m) for m in UNIT.finditer(text) if m.group(1) == value}
                if not any(FAMILY.get(u) in families and u not in units for u in other):
                    continue
                twin = by_place.get((rel, n))
                if twin is None:
                    spans = _spans(tree.tree(rel)) if rel.endswith(".py") and \
                        tree.tree(rel) is not None else []
                    twin = Candidate(seed.kind, rel, n, text, symbol=holder(spans, n),
                                     detail={"value": seed.detail.get("value"),
                                             "counterpart": True})
                    out.append(twin)
                    by_place[(rel, n)] = twin
                if twin.id not in seed.contradicts:
                    seed.contradicts.append(twin.id)
                if seed.id not in twin.contradicts:
                    twin.contradicts.append(seed.id)


def _unit(m: re.Match) -> str:
    unit = m.group(2).lower().replace(" ", "")
    return unit[:-1] if unit.endswith("s") and unit != "ms" else unit


def harvest(root: str | Path, tree: Tree | None = None) -> list[Candidate]:
    """Every candidate of one root, in a stable order. A root with no
    pyproject, no README, no docs and no Python yields none."""
    tree = tree or Tree(root)
    out: list[Candidate] = []
    _metadata(tree, out)
    _docs(tree, out)
    _source(tree, out)
    _exports(tree, out)
    _test_witnesses(tree, out)
    _contradictions(tree, out)
    unique = {}
    for c in out:
        unique.setdefault(c.id, c)
    return sorted(unique.values(), key=lambda c: (c.path, c.line, c.kind))


# ---- the binding rule ------------------------------------------------------------

def _cites(tree: Tree, kind: str, number: str) -> set[str]:
    rx = re.compile(r"%s\W{0,3}%s\b" % (re.escape(kind), number), re.I)
    return {rel for rel in tree.source() if rx.search(tree.text(rel))}


def _importers(tree: Tree, dep: str) -> set[str]:
    """The source files that import a dependency. A distribution name and its
    import name can differ, so the rule tries the common forms."""
    base = dep.lower().replace("-", "_").replace(".", "_")
    names = {base, base.removeprefix("python_"), base.removeprefix("py")}
    rx = re.compile(r"^\s*(from|import)\s+(%s)\b" % "|".join(
        sorted(map(re.escape, filter(None, names)))), re.M)
    return {rel for rel in tree.source() if rx.search(tree.text(rel))}


def _reexported(tree: Tree, init: str) -> set[str]:
    module = tree.tree(init)
    if module is None:
        return set()
    mods = tree.modules()
    package = next((m for m, p in mods.items() if p == init), "")
    out = set()
    for node in module.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        # The relative form and the absolute form inside the package both
        # re-export. icalendar's `__init__.py` uses the absolute form.
        if node.level >= 1:
            name = package + ("." + node.module if node.module else "")
        elif node.module and (node.module + ".").startswith(package + "."):
            name = node.module
        else:
            continue
        if name in mods and mods[name] != init:
            out.add(mods[name])
    return out


def bind(tree: Tree, c: Candidate) -> tuple[str, set[str]]:
    """The rule of design B step 4, and the source files it binds."""
    source = set(tree.source())
    if c.kind == "export":
        return "exports", {c.path} | _reexported(tree, c.path)
    if c.kind == "test_witness":
        held = c.detail.get("held_by", "")
        return ("symbol", {held}) if held in source else ("project_wide", source)
    if c.path in source:
        # A witness in a source file binds that file. The ranked callers of
        # step 5 come with the caller rule, a later slice.
        return "witness_file", {c.path}
    if c.kind == "metadata" and c.detail.get("field") == "script":
        target = str(c.detail.get("target", "")).split(":")[0]
        mod = tree.modules().get(target)
        return "entry_point", ({mod} if mod else set()) | {"pyproject.toml"}
    if c.kind == "metadata" and c.detail.get("field") == "dependency":
        got = _importers(tree, c.detail.get("dep", ""))
        if got:
            return "dependency", got
    cited = set()
    for m in STD.finditer(c.text):
        cited |= _cites(tree, m.group(1), m.group(2))
    if cited:
        return "standard", cited
    # A docs claim that cites no standard is mostly the docs' own tooling,
    # such as "Sphinx supports". Bound project-wide, 56 such rows gave
    # `parser/string.py` 7,096 characters of push (the review, low 3). The
    # row stays for the Architect, and binds no file.
    if c.kind == "doc_claim":
        return "", set()
    return "project_wide", source


# ---- the record --------------------------------------------------------------------

def record(conn: sqlite3.Connection, root: str | Path, commit: str) -> int:
    """Harvest `root` at `commit` into the record, and return the count of
    candidate rows written.

    A record that holds rows of this commit already is current, so the call
    writes nothing. A row of an older commit that the new harvest finds again
    takes the new commit. A row it does not find keeps its old commit, so a
    reader can tell it is stale, and it keeps no binding.

    The bindings are the new harvest's only, so a rule that changed with the
    tree does not leave the old rows beside the new ones (the review, high 2).
    All the writes and the commit stamp land in one transaction, as
    `indexer.build` does. A fault part way then leaves nothing, and the next
    run harvests again (the review, high 1: 15.9 s in autocommit)."""
    if commit and conn.execute(
            "SELECT 1 FROM commitment_candidates WHERE commit_sha = ? LIMIT 1",
            (commit,)).fetchone():
        return 0
    tree = Tree(root)
    # A caller inside its own transaction gets a savepoint instead.
    own = not conn.in_transaction
    conn.execute("BEGIN IMMEDIATE" if own else "SAVEPOINT harvest")
    try:
        written = _write(conn, tree, root, commit)
    except BaseException:
        conn.execute("ROLLBACK" if own else "ROLLBACK TO harvest")
        if not own:
            conn.execute("RELEASE harvest")
        raise
    conn.execute("COMMIT" if own else "RELEASE harvest")
    return written


def _write(conn: sqlite3.Connection, tree: Tree, root: str | Path,
           commit: str) -> int:
    conn.execute("DELETE FROM candidate_bindings")
    written = 0
    for c in harvest(root, tree):
        cur = conn.execute(
            "INSERT INTO commitment_candidates (id, kind, path, line, text, symbol, "
            "detail, contradicts, commit_sha) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET commit_sha = excluded.commit_sha, "
            "contradicts = excluded.contradicts, detail = excluded.detail "
            "WHERE commit_sha IS NOT excluded.commit_sha "
            "OR contradicts IS NOT excluded.contradicts "
            "OR detail IS NOT excluded.detail",
            (c.id, c.kind, c.path, c.line, c.text, c.symbol,
             json.dumps(c.detail, sort_keys=True), json.dumps(sorted(c.contradicts)),
             commit))
        written += cur.rowcount
        rule, paths = bind(tree, c)
        conn.executemany(
            "INSERT INTO candidate_bindings (witness_id, path, rule) "
            "VALUES (?, ?, ?)", [(c.id, p, rule) for p in sorted(paths)])
    return written
