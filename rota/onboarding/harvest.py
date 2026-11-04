"""
The harvest of commitment witnesses, deterministic, with no model.

Design B step 2 of `plans/design-onboarding-2026-11-03.md`: before any
request, a tool reads the tree for the lines where a project states a
promise to the outside. Each line becomes a candidate with its path, its
line number, its text copied from the file and its kind. The binding rule
of step 4 then binds each candidate to source files, by its kind.

The kinds are those of step 3, as the deep dive of the same date measured
them in section 1 (5 of 5 key commitments on icalendar, 2 of 5 on click):

    metadata          pyproject `name`, `description`, `requires-python`
                      and each dependency
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
    entry_point       a file that a program run starts in: a script target
                      of pyproject, a `__main__` guard that runs the file's
                      own function, a `__main__.py`, a README run line
    contribution      where the project takes a change in: the configured
                      test paths, and the change-log rule

The last two kinds are those of section 3.4 of
`plans/design-onboarding-shape-2026-11-04.md`. The design names the second
kind `intake`. That word is a mode of the brief role, so the kind takes
`contribution` (one word, one job: `tests/rota/test_vocabulary.py`).

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
         "issue_comment", "export", "test_witness", "entry_point", "contribution")

RULES = ("standard", "dependency", "entry_point", "exports", "witness_file",
         "symbol", "project_wide", "contribution")

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


def witness_key(kind: str, path: str, text: str) -> str:
    """The tie from a stated commitment to its candidate, with no line.

    The candidate id holds the line, so an edit above the witness gives the
    same witness a new id (the review, low 8). This key holds the kind, the
    path and the copied text only, so an unrelated edit keeps the tie. An
    edit of the witness line itself breaks the tie, and that is correct:
    the promise then needs a new statement. Two equal lines of one kind in
    one file share a key, and a reader takes the first."""
    key = f"{kind}|{path}|{text}".encode("utf-8")
    return "wk_" + hashlib.sha256(key).hexdigest()[:12]


def latest_commit(conn: sqlite3.Connection) -> str | None:
    """The commit of the latest harvest, or None when no harvest bound a row.

    `_write` replaces every binding on each harvest, so a bound candidate
    always carries the latest commit. A rowid cannot say this, because an
    upsert keeps the rowid of a row that an older harvest wrote (the review
    of pass 2, finding 2)."""
    row = conn.execute(
        "SELECT c.commit_sha FROM candidate_bindings b "
        "JOIN commitment_candidates c ON c.id = b.witness_id LIMIT 1").fetchone()
    return row["commit_sha"] if row else None


def current_keys(conn: sqlite3.Connection) -> set[str]:
    """The witness keys of the candidates of the latest harvest."""
    commit = latest_commit(conn)
    if commit is None:
        return set()
    return {witness_key(r["kind"], r["path"], r["text"]) for r in conn.execute(
        "SELECT kind, path, text FROM commitment_candidates WHERE commit_sha = ?",
        (commit,))}


def witnessed(conn: sqlite3.Connection, key: str) -> dict | None:
    """The candidate row of the latest harvest that `key` ties to, or None.
    None means the tie is broken: an edit or a move of the witness line
    changed its text or its path. Of two equal lines, the lower one wins."""
    commit = latest_commit(conn)
    if not key or commit is None:
        return None
    for r in conn.execute(
            "SELECT id, kind, path, line, text, commit_sha FROM commitment_candidates "
            "WHERE commit_sha = ? ORDER BY path, line, id", (commit,)):
        if witness_key(r["kind"], r["path"], r["text"]) == key:
            return dict(r)
    return None


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
        self._modules: dict[str, str] | None = None
        self._scans: dict[str, tuple[set[str], dict, dict]] = {}

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
        if self._modules is None:
            self._modules = {}
            for rel in self.source():
                name = _dotted(rel)
                if name:
                    self._modules[name] = rel
        return self._modules

    # ---- the call resolver ------------------------------------------------
    # The binding rule and the indexer's `code_calls` read one module map and
    # one import rule, so the two cannot disagree on one package (the shape
    # design, section 3.2, the review, finding 10).

    def absolute(self, rel: str, module: str | None, level: int) -> str:
        """The dotted name that an import in `rel` names. A relative import
        counts its dots up from the package of `rel`."""
        if level == 0:
            return module or ""
        package = _dotted(rel).split(".") if _dotted(rel) else []
        if not rel.endswith("__init__.py"):
            package = package[:-1]
        if level > 1:
            package = package[:max(0, len(package) - (level - 1))]
        return ".".join([*package, module] if module else package)

    def _imports(self, rel: str) -> tuple[set[str], dict, dict]:
        """The top-level names that `rel` defines, the names it binds by
        `from` import as (module path or None, name), and the module aliases
        it binds, each to a module path."""
        if rel in self._scans:
            return self._scans[rel]
        mods = self.modules()
        defs: set[str] = set()
        froms: dict[str, tuple[str | None, str]] = {}
        aliases: dict[str, str] = {}
        module = self.tree(rel)
        if module is not None:
            # The index holds a definition under a module-level `if` or `try`,
            # as click's `if WIN:` blocks. The resolver reads the same set, so
            # `code_calls` and the copies query agree (review of S1, medium 2).
            todo = list(module.body)
            while todo:
                node = todo.pop()
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                     ast.ClassDef)):
                    defs.add(node.name)
                elif isinstance(node, ast.If):
                    todo += node.body + node.orelse
                elif isinstance(node, ast.Try):
                    todo += node.body + node.orelse + node.finalbody
                    todo += [s for h in node.handlers for s in h.body]
            for node in ast.walk(module):
                if isinstance(node, ast.ImportFrom):
                    base = self.absolute(rel, node.module, node.level)
                    for a in node.names:
                        sub = f"{base}.{a.name}" if base else a.name
                        if sub in mods:
                            aliases[a.asname or a.name] = mods[sub]
                        else:
                            froms[a.asname or a.name] = (mods.get(base), a.name)
                elif isinstance(node, ast.Import):
                    for a in node.names:
                        if a.name not in mods:
                            continue
                        if a.asname:
                            aliases[a.asname] = mods[a.name]
                        else:
                            head = a.name.split(".")[0]
                            aliases[head] = mods.get(head, mods[a.name])
        self._scans[rel] = (defs, froms, aliases)
        return self._scans[rel]

    def definer(self, rel: str | None, name: str, depth: int = 0) -> str | None:
        """The file that defines `name` as module `rel` sees it, through the
        re-exports of each `__init__.py` on the way. The depth cap stops an
        import cycle."""
        if rel is None or depth > 6:
            return None
        defs, froms, _ = self._imports(rel)
        if name in defs:
            return rel
        hop = froms.get(name)
        return self.definer(hop[0], hop[1], depth + 1) if hop else None

    def calls(self, rel: str) -> set[tuple[str, str]]:
        """The top-level definitions in other files that `rel` calls, as
        (path, name). A call by a bare name and a call through a module
        alias resolve. A call on `self`, on an instance or by a string does
        not, so the set states less than the program does."""
        module = self.tree(rel)
        if module is None:
            return set()
        defs, froms, aliases = self._imports(rel)
        mods = self.modules()
        # A `from` import inside a function binds the name in that function
        # only, so a call there reads it first. click's `termui.raw_terminal`
        # calls the work through such an import (review of S1, medium 2 and
        # low 4). The walk visits an outer function first, so the innermost
        # scope wins.
        scoped: dict[int, dict] = {}
        for fn in ast.walk(module):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            scope = {a.asname or a.name: (mods.get(self.absolute(
                rel, n.module, n.level)), a.name) for n in ast.walk(fn)
                if isinstance(n, ast.ImportFrom) for a in n.names}
            if scope:
                scoped.update({id(c): scope for c in ast.walk(fn)
                               if isinstance(c, ast.Call)})
        out: set[tuple[str, str]] = set()
        for node in ast.walk(module):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Name):
                local = scoped.get(id(node), {})
                if func.id in local:
                    path, name = local[func.id]
                    got = self.definer(path, name)
                    if got:
                        out.add((got, name))
                    continue
                # A name the file defines is its own, as Python reads it.
                if func.id in froms and func.id not in defs:
                    path, name = froms[func.id]
                    got = self.definer(path, name)
                    if got:
                        out.add((got, name))
                continue
            chain = []
            while isinstance(func, ast.Attribute):
                chain.append(func.attr)
                func = func.value
            if not chain or not isinstance(func, ast.Name):
                continue
            chain.reverse()
            path, rest = aliases.get(func.id), chain
            while path and len(rest) > 1:
                sub = _dotted(path) + "." + rest[0]
                if sub not in mods:
                    break
                path, rest = mods[sub], rest[1:]
            if path and rest:
                got = self.definer(path, rest[0])
                if got:
                    out.add((got, rest[0]))
        return {(path, name) for path, name in out if path != rel}


def _dotted(rel: str) -> str:
    """The dotted module name of a Python path. A `src/` layout drops the
    `src` part, and a package's `__init__.py` is the package."""
    parts = rel[:-3].split("/")
    if parts[0] == "src":
        parts = parts[1:]
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


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


def _find(lines: list[str], pattern: str, start: int = 0) -> int:
    """The number of the first line at or after `start` that matches."""
    rx = re.compile(pattern)
    return next((i for i, text in enumerate(lines, 1)
                 if i > start and rx.search(text)), 0)


def _entry_points(tree: Tree, out: list[Candidate]) -> None:
    """The four forms of section 3.4, each at its witness line."""
    if "pyproject.toml" in tree.files:
        lines = tree.lines("pyproject.toml")
        try:
            project = tomllib.loads(tree.text("pyproject.toml")).get("project", {})
        except tomllib.TOMLDecodeError:
            project = {}
        groups = [("scripts", project.get("scripts")),
                  ("gui-scripts", project.get("gui-scripts"))]
        groups += [(f"entry-points.{name}", table) for name, table in
                   (project.get("entry-points", {}) or {}).items()]
        for group, table in groups:
            for script, target in (table or {}).items() if isinstance(
                    table, dict) else ():
                n = _find(lines, r"^\s*[\"']?" + re.escape(script) + r"[\"']?\s*=")
                if n:
                    out.append(Candidate("entry_point", "pyproject.toml", n,
                                         lines[n - 1], detail={
                                             "form": "script", "group": group,
                                             "script": script, "target": target,
                                             "doc": _target_doc(tree, target)}))
    for rel in tree.source():
        if rel.rsplit("/", 1)[-1] == "__main__.py":
            lines = tree.lines(rel)
            n = next((i for i, t in enumerate(lines, 1) if t.strip()), 0)
            if n:
                out.append(Candidate("entry_point", rel, n, lines[n - 1],
                                     detail={"form": "main_module"}))
            continue
        n = entry_guard(rel, tree.tree(rel))
        if n:
            out.append(Candidate("entry_point", rel, n, tree.lines(rel)[n - 1],
                                 detail={"form": "guard"}))
    for rel in tree.docs():
        if "/" in rel:
            continue
        for n, text in enumerate(tree.lines(rel), 1):
            for m in RUN_LINE.finditer(text):
                named = m.group(1).removeprefix("./")
                # A run line of a file that the tree does not hold is an
                # example, as `python hello.py` in click's README is.
                if named in tree.files:
                    out.append(Candidate("entry_point", rel, n, text,
                                         detail={"form": "readme", "file": named}))


# A README line that runs a file, as "Run it: `python main.py`".
RUN_LINE = re.compile(r"\bpython3?\s+(?:-\w+\s+)*([\w./-]+\.py)\b")
# A directory of fuzz harnesses, as icalendar's `fuzzing/`.
FUZZ_DIR = re.compile(r"^fuzz", re.I)


def _target_doc(tree: Tree, target: str) -> str:
    """The first docstring line of a script target, so a reader can say what
    the command does (the design, section 3.4)."""
    module, _, name = str(target).partition(":")
    rel = tree.modules().get(module.strip())
    parsed = tree.tree(rel) if rel else None
    if parsed is None:
        return ""
    for node in parsed.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                and node.name == name.strip().split(".")[0]:
            doc = ast.get_docstring(node) or ""
            return doc.strip().splitlines()[0] if doc.strip() else ""
    return ""


def _is_guard(node: ast.stmt) -> bool:
    if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
        return False
    test = node.test
    if len(test.comparators) != 1:
        return False
    # Both orders, as `"__main__" == __name__` also runs (review of S2, low 2).
    sides = {type(s).__name__: s for s in (test.left, test.comparators[0])}
    name, value = sides.get("Name"), sides.get("Constant")
    return (name is not None and value is not None and name.id == "__name__"
            and value.value == "__main__")


def entry_guard(rel: str, module: ast.Module | None) -> int:
    """The line of the `__main__` guard of `rel` when the guard is an entry
    point, else 0.

    The guard filter of section 6.1. A guard is an entry point when its body
    calls a function that the file defines at the top level. A module demo
    or a benchmark calls only imported names or names it defines in the
    guard, as `cal/lazy.py` of icalendar does. A fuzz harness is never an
    entry point: the file imports `atheris`, or a directory on its path
    starts with "fuzz"."""
    if module is None or any(FUZZ_DIR.match(p) for p in rel.split("/")[:-1]):
        return 0
    defs: set[str] = set()
    for node in module.body:
        # A top-level class runs the program too, as `App().run()` does, and
        # so does a name from a relative import (review of S2, low 2).
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs.add(node.name)
        if isinstance(node, ast.ImportFrom) and node.level:
            defs.update(a.asname or a.name for a in node.names)
        names =([a.name for a in node.names] if isinstance(node, ast.Import)
                 else [node.module or ""] if isinstance(node, ast.ImportFrom)
                 else [])
        if any(n.split(".")[0] == "atheris" for n in names):
            return 0
    for node in module.body:
        if not _is_guard(node):
            continue
        for sub in node.body:
            for call in ast.walk(sub):
                if (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
                        and call.func.id in defs):
                    return node.lineno
    return 0


# The pytest configuration files in the order pytest reads them, each with
# the section that holds `testpaths`.
PYTEST_CONFIGS = (("pytest.ini", "pytest"), ("pyproject.toml", ""),
                  ("tox.ini", "pytest"), ("setup.cfg", "tool:pytest"))
UNRELEASED = re.compile(r"\bunreleased\b", re.I)
# The lines of a change log that a heading search reads, from the top.
CHANGE_LOG_REACH = 40


def _contribution(tree: Tree, out: list[Candidate]) -> None:
    """The configured test paths and the change-log rule, of section 3.4."""
    for rel, section in PYTEST_CONFIGS:
        paths = _testpaths(tree, rel, section)
        if paths:
            lines = tree.lines(rel)
            n = _find(lines, r"^\s*testpaths\s*=")
            # A TOML array over several lines is quoted to its close.
            last = n
            if n and lines[n - 1].rstrip().endswith("["):
                last = _find(lines, r"^\s*\]", n) or n
            if n:
                out.append(Candidate("contribution", rel, n, "\n".join(lines[n - 1:last]),
                                     detail={"form": "testpaths", "paths": paths}))
            break
    for rel in ("pyproject.toml", "towncrier.toml"):
        if rel not in tree.files:
            continue
        try:
            towncrier = tomllib.loads(tree.text(rel)).get("tool", {}).get(
                "towncrier")
        except tomllib.TOMLDecodeError:
            continue
        if not isinstance(towncrier, dict):
            continue
        lines = tree.lines(rel)
        head = _find(lines, r"^\s*\[tool\.towncrier\]")
        n = _find(lines, r"^\s*directory\s*=", head) or head
        if n:
            out.append(Candidate("contribution", rel, n, lines[n - 1], detail={
                "form": "news_fragment",
                "directory": str(towncrier.get("directory", "")),
                "filename": str(towncrier.get("filename", "NEWS.rst"))}))
            # A project with fragments says its change log is built, so the
            # change-log file is not where a change goes.
            return
    for rel in sorted(r for r in tree.files if "/" not in r and HISTORY.match(r)):
        lines = tree.lines(rel)[:CHANGE_LOG_REACH]
        hit = next((i for i, t in enumerate(lines, 1) if UNRELEASED.search(t)), 0)
        if not hit:
            continue
        n = next((i for i in range(hit, 0, -1) if _heading(lines, i)), hit)
        out.append(Candidate("contribution", rel, n, lines[n - 1], detail={
            "form": "change_log", "unreleased_line": hit}))


def _heading(lines: list[str], n: int) -> bool:
    """A Markdown heading, or a reST title with its underline below it."""
    text = lines[n - 1]
    if text.startswith("#"):
        return True
    below = lines[n].strip() if n < len(lines) else ""
    return bool(text.strip()) and len(below) >= 3 and len(set(below)) == 1 \
        and below[0] in "=-~^*+"


def _testpaths(tree: Tree, rel: str, section: str) -> list[str]:
    if rel not in tree.files:
        return []
    if rel == "pyproject.toml":
        try:
            got = (tomllib.loads(tree.text(rel)).get("tool", {}).get("pytest", {})
                   .get("ini_options", {}).get("testpaths"))
        except tomllib.TOMLDecodeError:
            return []
    else:
        import configparser

        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read_string(tree.text(rel))
        except configparser.Error:
            return []
        got = parser.get(section, "testpaths", fallback="").split()
    if isinstance(got, str):
        got = got.split()
    return [str(p) for p in got or []]


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
    _entry_points(tree, out)
    _contribution(tree, out)
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
        # re-export. icalendar's `__init__.py` uses the absolute form. The
        # relative form reads the import rule of `code_calls`.
        if node.level >= 1:
            name = tree.absolute(init, node.module, node.level)
        elif node.module and (node.module + ".").startswith(package + "."):
            name = node.module
        else:
            continue
        if name in mods and mods[name] != init:
            out.add(mods[name])
    return out


def _under(rel: str, folder: str) -> bool:
    folder = folder.strip().strip("/").removeprefix("./")
    return not folder or folder == "." or rel == folder or rel.startswith(folder + "/")


def _contribution_files(tree: Tree, c: Candidate) -> set[str]:
    """The test files that a `testpaths` row collects, or the change-log
    files that a change-log row names."""
    form = c.detail.get("form")
    if form == "testpaths":
        return {rel for rel in tree.tests()
                if any(_under(rel, p) for p in c.detail.get("paths", []))}
    if form == "news_fragment":
        # A change adds a new fragment, so no change touches the old ones.
        # The row text names the directory (review of S2, low 3).
        return {c.detail.get("filename", "")} & set(tree.files)
    return {c.path}


def bind(tree: Tree, c: Candidate) -> tuple[str, set[str]]:
    """The rule of design B step 4, and the source files it binds."""
    source = set(tree.source())
    if c.kind == "export":
        return "exports", {c.path} | _reexported(tree, c.path)
    if c.kind == "test_witness":
        held = c.detail.get("held_by", "")
        return ("symbol", {held}) if held in source else ("project_wide", source)
    if c.kind == "entry_point":
        form = c.detail.get("form")
        if form == "script":
            target = str(c.detail.get("target", "")).split(":")[0].strip()
            mod = tree.modules().get(target)
            return "entry_point", ({mod} if mod else set()) | {c.path}
        if form == "readme":
            return "entry_point", {c.detail.get("file", "")} & set(tree.files)
        return "entry_point", {c.path}
    if c.kind == "contribution":
        return "contribution", _contribution_files(tree, c)
    if c.path in source:
        # A witness in a source file binds that file. The ranked callers of
        # step 5 come with the caller rule, a later slice.
        return "witness_file", {c.path}
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


def _standards(tree: Tree, c: Candidate) -> set[tuple[str, str]]:
    """The standards that `c` cites and that a source file cites too."""
    return {(m.group(1).upper(), m.group(2)) for m in STD.finditer(c.text)
            if _cites(tree, m.group(1), m.group(2))}


def bind_all(tree: Tree, cands: list[Candidate]) -> dict[str, tuple[str, set[str]]]:
    """The rule and the files of each candidate, with one bound candidate per
    cited standard.

    The docs restate a standard on many lines. In `src/icalendar/parser`, 22
    of 31 pushed lines were such restatements (the review of pass 1, low 4,
    and of pass 2, medium 4). So for each standard, the first candidate of a
    root file binds, the package metadata first. The other
    candidates of that standard bind no file. Each row stays for the
    Architect, as an unbound docs claim does."""
    bound = {c.id: bind(tree, c) for c in cands}
    first: dict[tuple[str, str], Candidate] = {}
    cited: dict[str, set[tuple[str, str]]] = {}
    for c in cands:
        if bound[c.id][0] != "standard":
            continue
        cited[c.id] = _standards(tree, c)
        for std in cited[c.id]:
            held = first.get(std)
            if held is None or _root_first(c) < _root_first(held):
                first[std] = c
    for c in cands:
        if c.id not in cited:
            continue
        won = {std for std in cited[c.id] if first[std].id == c.id}
        paths = set()
        for kind, number in won:
            paths |= _cites(tree, kind, number)
        bound[c.id] = ("standard", paths) if paths else ("", set())
    return bound


def _root_first(c: Candidate) -> tuple[bool, int, str, int]:
    """The order that picks the bound candidate of a standard. A root file
    goes first. Of two root files, the package metadata goes before the
    README, because it is the package's own statement."""
    return ("/" in c.path, KINDS.index(c.kind), c.path, c.line)


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
    cands = harvest(root, tree)
    bound = bind_all(tree, cands)
    for c in cands:
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
        rule, paths = bound[c.id]
        conn.executemany(
            "INSERT INTO candidate_bindings (witness_id, path, rule) "
            "VALUES (?, ?, ?)", [(c.id, p, rule) for p in sorted(paths)])
    return written
