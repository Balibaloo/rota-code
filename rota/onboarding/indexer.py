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

from ..core.worktrees import GIT

import posixpath
import sqlite3
from dataclasses import dataclass, field
import hashlib
from pathlib import Path

from .languages import Language, for_path

SKIP_DIRS = {".git", ".rota", "node_modules", "__pycache__", ".venv", "venv",
             "dist", "build", ".mypy_cache", ".pytest_cache", "target"}

MAX_BYTES = 1_000_000            # a file larger than this is generated or data

# Tracked, text, under the size cap -- and still nobody's work. A lockfile is a
# resolver's output and a minified bundle is a compiler's; indexing either puts
# thousands of grains in front of a role that can do nothing with them.
GENERATED = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json",
             "poetry.lock", "Pipfile.lock", "Cargo.lock", "go.sum", "composer.lock",
             "Gemfile.lock", "uv.lock", "flake.lock"}


def _minified(name: str) -> bool:
    return any(name.endswith(s) for s in (".min.js", ".min.css", ".map", ".lock"))


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
    symbols: list[tuple[str, str]] = field(default_factory=list)   # (name, kind)
    imports: list[str] = field(default_factory=list)
    # What the file held, so the index can say later whether it still does.
    content_hash: str = ""


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
                from .languages import kind_of

                facts.symbols.append((_text(name, source), kind_of(node.type)))
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
        # `target[:2]` against `"../"` is two characters tested against three,
        # so `../anything` never matched here and fell through to the Python
        # dotted-relative branch, which read `..` as a package separator and
        # produced `/variables` from `../variables`. Every `../` import in every
        # JS, TS, Go and Rust file in the repository took that path.
        if target.startswith("./") or target.startswith("../"):
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
        # `Path("src/intents") / "../variables"` is
        # `src/intents/../variables`, and `as_posix` does not collapse `..` --
        # only `.`. So every import written with a leading `../` produced a
        # candidate containing a literal `..`, which is in no index, in any
        # language. On the first Obsidian plugin that was 60 unresolved imports
        # against 10 resolved, and `code.survey` orders by fan-in, so the view
        # every survey session opens with was sorted by a number that was almost
        # always zero.
        cand = posixpath.normpath(cand).strip("/")
        if not cand or cand == "." or cand.startswith(".."):
            continue
        for suffix in ("", ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs",
                       ".java", ".rb", "/__init__.py", "/index.js", "/index.ts",
                       "/index.tsx", "/index.jsx", "/mod.rs"):
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
            [*GIT, "-C", str(root), "ls-files", "--cached", "--others",
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
    Every authored file under `root` — not only the ones with a parser.

    It used to keep a file only when `languages.for_path` recognised its suffix,
    which asks "can tree-sitter turn this into symbols" and was being used to
    answer "is this part of the project". On the first Obsidian plugin those are
    different questions by four files: `intentsSchema.yaml` defines every key an
    intent may carry *and is imported by the parser that reads them*,
    `README.md` says what the product is in its first line, and `manifest.json`
    and `versions.json` carry the two commitments to the plugin registry. None
    of them reached the index, so none reached a brief, so no session could cite
    or read one. The Architect woken for the top level saw a build script and a
    version bumper and wrote a constraint about the build script.

    A file with no parser still has a path and contents, and `code.source` opens
    it either way. It arrives as a path-kind grain with no symbols, which is a
    shape the index already holds — `esbuild.config.mjs` has been one all along.

    What stays out is what nobody authored: lockfiles, minified bundles, and
    anything that is not text. `MAX_BYTES` and `tracked()` already carried most
    of that and are still the first line.

    `SKIP_DIRS` stays as a floor even when git answers, because the two are not
    the same question. `.rota/` is *our* state directory inside somebody else's
    project: untracked, and nothing obliges them to have ignored it, so git
    would list it and it must never be indexed.

    The skip test reads the path **relative to `root`**, not the absolute path.
    A batch worktree is `<project>/.rota/worktrees/<batch>`, so every file in it
    carries `.rota` above the root, and the absolute test skipped all of them:
    the walk of a worktree returned nothing and a refresh of it would have
    emptied the index (the design review, 2026-09-17). What `root` itself sits
    under is the caller's business; what is inside it is this function's.
    """
    keep = tracked(root)
    out = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if keep is not None and path.resolve() not in keep:
            continue
        if path.name in GENERATED or _minified(path.name):
            continue
        out.append(path)
    return out


class IndexRefreshError(RuntimeError):
    """
    The tree cannot be indexed, so the old index stays.

    The swap empties both tables before it fills them. A root that is gone, or
    one whose walk returns nothing while git still lists files, would therefore
    replace the index with an empty one and report success. The caller keeps
    what it has and records the failure instead.
    """


def build(conn: sqlite3.Connection, root: str | Path) -> IndexReport:
    """
    Index a checkout into `code_index` and `code_edges`.

    Replaces both tables outright rather than merging. The index is a function of
    a commit — a file deleted upstream must leave the index, and a merge that
    keeps stale grains is how `code.probe` starts returning paths that are not
    there.

    Two refusals come before the swap, because the swap deletes first. A missing
    root is a destroyed worktree or a moved project. An empty walk of a root that
    git says holds files is a bug in the walk, and an index emptied by one is
    indistinguishable from a deleted codebase to every reader downstream.
    """
    root = Path(root)
    if not root.is_dir():
        raise IndexRefreshError(f"no tree to index at {root}")
    report = IndexReport()

    files = walk(root)
    if not files and tracked(root):
        raise IndexRefreshError(
            f"the walk of {root} found nothing while git lists tracked files")

    facts: list[FileFacts] = []
    for path in files:
        try:
            source = path.read_bytes()
        except OSError:                                     # pragma: no cover
            report.skipped.append(str(path))
            continue
        if len(source) > MAX_BYTES:
            report.skipped.append(path.relative_to(root).as_posix())
            continue
        rel = path.relative_to(root).as_posix()
        digest = hashlib.sha256(source).hexdigest()[:16]
        lang = for_path(path.name)
        if lang is None:
            # No parser, so no symbols and no imports -- but a path, which is
            # what a session needs to find it and `code.source` needs to open
            # it. Binary is the one thing excluded here rather than by name: a
            # decode failure is what "not authored text" actually means, and it
            # does not need a suffix list to be complete.
            try:
                source.decode("utf-8")
            except UnicodeDecodeError:
                report.skipped.append(rel)
                continue
            facts.append(FileFacts(path=rel, content_hash=digest))
            report.languages["text"] = report.languages.get("text", 0) + 1
            continue
        parsed = parse_file(rel, source, lang)
        parsed.content_hash = digest
        facts.append(parsed)
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

    # The swap is a transaction, not a hopeful sequence. The connection runs
    # autocommit, so without the explicit BEGIN the DELETE landed instantly
    # and a death during the inserts left a half-empty index -- a
    # mostly-deleted tree that would reopen every area at once. Chaos found
    # it: 93 grains before the kill, 3 after.
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute("DELETE FROM code_edges")
        conn.execute("DELETE FROM code_index")
        for f in facts:
            conn.execute(
                "INSERT INTO code_index (grain, grain_kind, fan_in, content_hash) "
                "VALUES (?, 'path', ?, ?)",
                (f.path, fan_in.get(f.path, 0), f.content_hash))
            for symbol, kind in f.symbols:
                conn.execute(
                    "INSERT OR IGNORE INTO code_index (grain, grain_kind, fan_in, sym_kind) "
                    "VALUES (?, 'symbol', 0, ?)", (f"{f.path}::{symbol}", kind))
                report.symbols += 1
        conn.executemany("INSERT INTO code_edges (src, dst) VALUES (?, ?)",
                         sorted(edges))
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise

    report.files = len(facts)
    report.edges = len(edges)
    return report


def stamp_area_hashes(conn: sqlite3.Connection) -> int:
    """
    Record each area's aggregate content, as the index stands now.

    The same aggregate `area_content_hash` computed live from path grains until
    2026-09-17: the area's `grain=content_hash` pairs, sorted, joined by `|`,
    sha256, sixteen characters. It moved into a table because the index no
    longer describes one tree for the whole run. Between a commit and the merge
    the index describes the batch's worktree, and a freshness rule that read the
    index live would reopen every touched area on every Developer commit.

    Stamped by onboarding and by every refresh of the main checkout, so the
    comparison answers "has main moved since the survey", which is the question
    the rule was written for. Rebuilt, never decided: no role writes it.
    """
    per: dict[str, list[str]] = {}
    for row in conn.execute(
            "SELECT area, grain, content_hash FROM code_index "
            "WHERE grain_kind = 'path' AND area IS NOT NULL "
            "AND content_hash != '' ORDER BY grain"):
        per.setdefault(row["area"], []).append(
            f"{row['grain']}={row['content_hash']}")
    stamped = [(area, hashlib.sha256("|".join(parts).encode()).hexdigest()[:16])
               for area, parts in per.items()]
    # Replaced whole, in one transaction, for the reason the index swap is one:
    # a half-written table reads as "these areas moved" and reopens them.
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute("DELETE FROM area_hashes")
        conn.executemany("INSERT INTO area_hashes (area, hash) VALUES (?, ?)",
                         stamped)
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    return len(stamped)


@dataclass
class RefreshReport:
    """What a refresh did, for an operator to print."""
    index: IndexReport
    branch: str = ""
    commit: str = ""


def refresh(conn: sqlite3.Connection, tree: str | Path, *,
            main: bool) -> RefreshReport:
    """
    Re-index a tree, and say which tree the index now describes.

    Two trees, two contracts.

    `main=True` is `rota refresh`: the main checkout at its new head. The
    partition, the lexicon and constraint zero are re-derived over it, the area
    hashes are stamped, and `config.project_commit` names the commit indexed.
    Every reader is then reading main again. The lifecycle calls this when a
    batch stops running -- merged, abandoned or deferred -- so the index never
    describes a worktree no batch owns.

    `main=False` is a batch's worktree after the Developer's commit landed. The
    grains change, the partition does not: each surviving grain keeps the area
    it had, and a new path takes the area of its nearest indexed ancestor. No
    re-pin, because a partition that moves under a half-finished survey strands
    the areas already done, and the batch's own files are no reason to move it.
    No area hashes and no `project_commit`: the config names main's head, and
    main did not move (the design review, 2026-09-17, points 1 and 3).
    """
    tree = Path(tree)
    if main:
        report = build(conn, tree)
        # Imported here: `boot` imports this module at its top.
        from . import boot

        boot.repin(conn, tree)                  # repin stamps the area hashes
        branch, commit = boot.checkout_of(tree)
        # Only over a value. A tree with no git answers empty, and an empty
        # value written over the real one would make the run describe no commit.
        for key, value in (("project_commit", commit), ("project_branch", branch)):
            if value:
                conn.execute("INSERT OR REPLACE INTO config (key, value) "
                             "VALUES (?, ?)", (key, value))
        return RefreshReport(index=report, branch=branch, commit=commit)

    from . import areas as areas_mod

    was = {row["grain"]: row["area"] for row in
           conn.execute("SELECT grain, area FROM code_index")}
    areas = {area for area in was.values() if area}
    report = build(conn, tree)
    # The build leaves `area` NULL, so the column is restored rather than
    # re-derived. A grain the build dropped is simply not updated.
    conn.executemany("UPDATE code_index SET area = ? WHERE grain = ?",
                     [(area, grain) for grain, area in was.items() if area])
    # A file the batch added. `areas.area_of` is the walk the partition uses
    # for a test path, so a new file lands in the area onboarding would have
    # given it. Deriving it keeps `code.survey` and every area-scoped reader
    # able to see the batch's new file.
    new_areas: dict[str, str] = {}
    for row in conn.execute(
            "SELECT grain FROM code_index WHERE grain_kind = 'path' "
            "AND area IS NULL").fetchall():
        grain = row["grain"]
        new_areas[grain] = areas_mod.area_of(posixpath.dirname(grain), areas)
    for grain, area in new_areas.items():
        conn.execute("UPDATE code_index SET area = ? WHERE grain = ?",
                     (area, grain))
    # A symbol is in the area of the file that defines it, as `areas.pin` has
    # it, so a new definition is not an area of its own.
    for row in conn.execute(
            "SELECT grain FROM code_index WHERE grain_kind = 'symbol' "
            "AND area IS NULL").fetchall():
        path = row["grain"].split("::", 1)[0]
        area = new_areas.get(path, was.get(path))
        if area:
            conn.execute("UPDATE code_index SET area = ? WHERE grain = ?",
                         (area, row["grain"]))
    return RefreshReport(index=report)
