"""
The code index: what exists, and what depends on what.

`code_index` and `code_edges` were in the schema from the beginning with nothing
that wrote to them. Everything downstream of onboarding needs them — areas are a
partition of the dependency graph, `code.probe` searches the index, and Architect
annotates a batch from grains that have to exist before they can be named.

**Nothing here interprets.** The index is a fact about the checkout: these files
exist, these symbols are in them, this file imports that one. What any of it
*means* is a survey's job, and a survey is a session with a role in it. Keeping
the mechanical half mechanical is what lets it re-run on any commit without
asking anybody anything.

Unresolved imports are counted rather than dropped in silence. An index that
quietly loses a third of its edges partitions the codebase wrongly and gives no
sign, and the partition is what every later area-scoped decision rests on.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from .languages import Language, for_path

SKIP_DIRS = {".git", ".rota", "node_modules", "__pycache__", ".venv", "venv",
             "dist", "build", ".mypy_cache", ".pytest_cache", "target"}

MAX_BYTES = 1_000_000            # a file larger than this is generated or data


class ParsersUnavailable(RuntimeError):
    """tree-sitter grammars are not installed. Onboarding needs them; nothing
    else does, so this is raised at use rather than at import."""


def _parser(language: str):
    try:
        from tree_sitter_language_pack import get_parser
    except ImportError as exc:                              # pragma: no cover
        raise ParsersUnavailable(
            "onboarding needs `tree-sitter-language-pack`") from exc
    return get_parser(language)


# ---------------------------------------------------------------------------
# Parsing one file
# ---------------------------------------------------------------------------

@dataclass
class FileFacts:
    path: str
    symbols: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)


def _text(node, source: bytes) -> str:
    return source[node.start_byte:node.end_byte].decode("utf-8", "replace")


# Where a grammar puts the thing being imported, in the order to try. Every
# language in the pack names it; they just disagree about what to call it —
# `module_name` in Python, `source` in JS, `path` in Go, `argument` in Rust.
MODULE_FIELDS = ("module_name", "source", "path", "argument", "name")

# Node types that *are* a module path rather than containing one. Reaching one
# ends the search: descending further into a Java `scoped_identifier` yields
# `Record` where the answer was `com.example.store.Record`.
PATH_TYPES = {
    "string", "string_literal", "interpreted_string_literal",
    "raw_string_literal", "dotted_name", "relative_import",
    "scoped_identifier", "package_identifier", "identifier",
}


def _targets(node, source: bytes) -> list[str]:
    """
    What an import node imports.

    The first version collected every string and dotted name below the node,
    which for `from ..store import Record, load, save` returned four targets —
    the module and the three names bound from it. Three quarters of the edges
    were then unresolvable, and the unresolved counter is the only reason that
    was visible rather than merely quiet.
    """
    if node.type in PATH_TYPES:
        return [_text(node, source).strip("\"'`")]

    for field in MODULE_FIELDS:
        child = node.child_by_field_name(field)
        if child is not None:
            return _targets(child, source)

    # A container: Go's `import_spec_list`, Java's bare declaration.
    out: list[str] = []
    for child in node.named_children:
        out.extend(_targets(child, source))
    return out


def parse_file(path: str, source: bytes, lang: Language) -> FileFacts:
    tree = _parser(lang.name).parse(source)
    facts = FileFacts(path=path)

    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        if node.type in lang.definitions:
            name = node.child_by_field_name("name")
            if name is not None:
                facts.symbols.append(_text(name, source))
            # Do not descend: a method inside a class is the class's business,
            # and indexing every nested closure turns the index into the parse
            # tree with extra steps.
            continue
        if node.type in lang.imports:
            # Ruby has no import node and CommonJS has no import statement —
            # `require` is an ordinary call in both, so the language table
            # points at the call node and the filter lives here.
            if node.type in ("call", "call_expression"):
                head = node.child_by_field_name("function")
                if head is None or _text(head, source) not in (
                        "require", "load", "autoload", "require_relative"):
                    stack.extend(node.children)
                    continue
                args = node.child_by_field_name("arguments")
                facts.imports.extend(_targets(args, source) if args else [])
            elif node.type == "export_statement":
                # An `export` is an import only when it re-exports:
                # `export { x } from "./y"` names another module, and
                # `export function money() {}` names a thing defined right
                # here. Both are `export_statement`, and only the first has a
                # `source`.
                #
                # Without this the bare form fell through `MODULE_FIELDS`,
                # recursed into the declaration, and came back with the
                # exported symbol's own name as an import target — which never
                # resolves, because it is not a module. Three JS/TS files
                # containing no import statement whatsoever reported three
                # unresolved imports.
                #
                # It does not fabricate edges: `resolve`'s tail never tries file
                # suffixes, so a bare name stays unresolved rather than
                # matching something. Noise, not corruption — but the
                # unresolved count is a tripwire, and one that reads 45% when
                # the truth is 0% will not be believed the day it is right.
                src = node.child_by_field_name("source")
                if src is not None:
                    facts.imports.extend(_targets(src, source))
                else:
                    stack.extend(node.children)
            else:
                facts.imports.extend(_targets(node, source))
            continue
        stack.extend(node.children)

    return facts


# ---------------------------------------------------------------------------
# Resolving an import to a file in the checkout
# ---------------------------------------------------------------------------

def resolve(target: str, importer: str, known: set[str]) -> str | None:
    """
    An import string against the paths that actually exist.

    Deliberately conservative: it resolves what it can prove and returns None
    for everything else, because an edge invented between two modules is worse
    than an edge missing. A missing edge understates coupling; an invented one
    puts two unrelated areas in the same partition.
    """
    if not target:
        return None

    target = target.replace("::", ".")          # rust says it with two colons
    here = Path(importer).parent

    # Relative, by leading dots (Python) or by an explicit ./ (JS, TS).
    if target.startswith("."):
        if target[:2] in ("./", "../"):
            base = (here / target).as_posix()
            candidates = [base]
        else:
            up = len(target) - len(target.lstrip("."))
            root = here
            for _ in range(up - 1):
                root = root.parent
            rest = target.lstrip(".").replace(".", "/")
            candidates = [(root / rest).as_posix() if rest else root.as_posix()]
    else:
        # Absolute-ish: a dotted or slashed path from some root. Try it as
        # written and as a suffix of a known path, which covers a package
        # imported by its top-level name.
        dotted = target.replace(".", "/")
        candidates = [dotted, target]

    for cand in candidates:
        cand = cand.strip("/")
        if not cand:
            continue
        for suffix in ("", ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs",
                       ".java", ".rb", "/__init__.py", "/index.js", "/mod.rs"):
            hit = cand + suffix
            if hit in known:
                return hit
        # A bare package name: `src/store` imported as `store`.
        tail = [p for p in known
                if p == cand or p.endswith("/" + cand)
                or p.endswith("/" + cand + "/__init__.py")]
        if len(tail) == 1:
            return tail[0]
    return None


# ---------------------------------------------------------------------------
# Indexing a checkout
# ---------------------------------------------------------------------------

@dataclass
class IndexReport:
    files: int = 0
    symbols: int = 0
    edges: int = 0
    unresolved: int = 0
    languages: dict[str, int] = field(default_factory=dict)
    skipped: list[str] = field(default_factory=list)


def tracked(root: Path) -> set[Path] | None:
    """
    What git considers part of this project, or `None` when it is not a checkout.

    The design story says the index respects `.gitignore` throughout, *"so build
    artefacts, dependencies, and the framework's own state folder never enter
    it"*. The implementation was a hardcoded eleven-name `SKIP_DIRS`. It covers
    the usual suspects and nothing else, so any project with generated or
    vendored code outside those names had it indexed, partitioned, and surveyed
    as if a person had written it — and a role reading generated code will
    faithfully report what it finds there.

    Asking git rather than reimplementing it. `.gitignore` is not a list of
    names: it has globs, negations, per-directory files, `.git/info/exclude` and
    a global excludes file, and a partial parser is the kind of thing that looks
    right on the repository it was written against.

    `--cached --others --exclude-standard` is tracked files plus untracked ones
    that are not ignored, which is exactly "authored". A tracked file that also
    matches an ignore rule stays, correctly: somebody committed it on purpose.
    """
    import subprocess

    try:
        got = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--cached", "--others",
             "--exclude-standard", "-z"],
            capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if got.returncode != 0:
        return None
    return {(root / name.decode("utf-8", "replace")).resolve()
            for name in got.stdout.split(b"\x00") if name}


def walk(root: Path) -> list[Path]:
    """
    Every authored source file under `root`.

    `SKIP_DIRS` stays as a floor even when git answers, because the two are not
    the same question. `.rota/` is *our* state directory inside somebody else's
    project: untracked, and nothing obliges them to have ignored it, so git
    would list it and it must never be indexed.
    """
    keep = tracked(root)
    out = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if keep is not None and path.resolve() not in keep:
            continue
        if for_path(path.name) is None:
            continue
        out.append(path)
    return out


def build(conn: sqlite3.Connection, root: str | Path) -> IndexReport:
    """
    Index a checkout into `code_index` and `code_edges`.

    Replaces both tables outright rather than merging. The index is a function of
    a commit — a file deleted upstream must leave the index, and a merge that
    keeps stale grains is how `code.probe` starts returning paths that are not
    there.
    """
    root = Path(root)
    report = IndexReport()

    facts: list[FileFacts] = []
    for path in walk(root):
        lang = for_path(path.name)
        assert lang is not None
        try:
            source = path.read_bytes()
        except OSError:                                     # pragma: no cover
            report.skipped.append(str(path))
            continue
        if len(source) > MAX_BYTES:
            report.skipped.append(path.relative_to(root).as_posix())
            continue
        rel = path.relative_to(root).as_posix()
        facts.append(parse_file(rel, source, lang))
        report.languages[lang.name] = report.languages.get(lang.name, 0) + 1

    known = {f.path for f in facts}

    edges: set[tuple[str, str]] = set()
    for f in facts:
        for target in f.imports:
            hit = resolve(target, f.path, known)
            if hit is None or hit == f.path:
                report.unresolved += 1
                continue
            edges.add((f.path, hit))

    fan_in: dict[str, int] = {}
    for _, dst in edges:
        fan_in[dst] = fan_in.get(dst, 0) + 1

    conn.execute("DELETE FROM code_edges")
    conn.execute("DELETE FROM code_index")
    for f in facts:
        conn.execute(
            "INSERT INTO code_index (grain, grain_kind, fan_in) VALUES (?, 'path', ?)",
            (f.path, fan_in.get(f.path, 0)))
        for symbol in f.symbols:
            conn.execute(
                "INSERT OR IGNORE INTO code_index (grain, grain_kind, fan_in) "
                "VALUES (?, 'symbol', 0)", (f"{f.path}::{symbol}",))
            report.symbols += 1
    conn.executemany("INSERT INTO code_edges (src, dst) VALUES (?, ?)",
                     sorted(edges))

    report.files = len(facts)
    report.edges = len(edges)
    return report
