"""
Vocabulary extraction — Terminologist's job, run on ourselves.

The system's whole thesis is that meaning must be canonical: the Terminologist role
exists because a term quietly meaning two things is the most expensive kind of
bug. Building it in sloppy vocabulary is not ironic, it is the same failure one
level up — our terms leak into every prompt, and the roles reason in them.

So: harvest every term actually in use, from every source that defines one, and
sort them by **level of abstraction** rather than alphabetically. Naming decisions
made bottom-up produce a consistent-looking dictionary describing an incoherent
system; made top-down they produce a system whose lower levels have somewhere to
hang from.

Levels, highest first:

    L0  the engagement   what the whole thing is, and its relationship to a principal
    L1  the team         who exists, and why each one exists separately
    L2  the record       what is written down and who owns it
    L3  the work         operations performed on the record
    L4  the traffic      what crosses between people
    L5  the states       the words a thing can be in
    L6  the machinery    runtime concepts no role should ever need to name

The last level is the tell. Anything a *role* has to understand from L6 is a
mechanism that has leaked into the vocabulary, and that leak is what makes a
prompt read like configuration rather than like a brief.

Usage: python -m rota.tools.vocabulary [--json]
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .. import paths

ROOT = paths.REPO
DESIGN = paths.DESIGN
PROMPTS = paths.PROMPTS
DOCS = paths.DOCS

# The top level is *declared*, not harvested: these are the concepts the whole
# thing rests on, and there is no source to extract them from because they are
# what every other source presupposes.
L0_TERMS = {
    "engagement": "the whole relationship with one principal, from first ask to milestone",
    "principal": "the single technical person who holds final authority",
    "team": "the roles, which never share context and communicate only by artefact",
    "understanding loop": "hear, shape, agree — turning what was said into what is meant",
    "delivery loop": "plan, build, judge — turning what is meant into what exists",
    "reconcile": "re-running the first loop's discipline when the second finds the world changed",
    "milestone": "quiescence with an empty ledger; there is nothing to 'close'",
}

LEVELS = {
    "L0": "the engagement — what this is",
    "L1": "the team — who exists and why separately",
    "L2": "the record — what is written and who owns it",
    "L3": "the work — operations on the record",
    "L4": "the traffic — what crosses between people",
    "L5": "the states — what a thing can be in",
    "L6": "the machinery — runtime concepts a role should never name",
}


@dataclass
class Term:
    word: str
    level: str
    sense: str = ""
    sources: set[str] = field(default_factory=set)
    register: str = ""          # 'machine' | 'trade' | 'plain'

    def as_dict(self) -> dict:
        return {
            "term": self.word, "level": self.level, "sense": self.sense,
            "sources": sorted(self.sources), "register": self.register,
        }


# Words that are unmistakably machine vocabulary: if a role has to know one, a
# mechanism has leaked into the brief.
MACHINE_MARKERS = {
    "ref", "refs", "id", "ids", "row", "rows", "table", "commit", "transaction",
    "predicate", "frontier", "tick", "wake", "claim", "checkpoint", "receipt",
    "cascade", "session", "sandbox", "namespace", "schema", "artefact_versions",
    "quiescent", "quiescence", "dag", "index", "delta", "query", "scope",
    "atomic", "atomicity", "mangle", "seq", "enum", "fk", "upsert",
}

# Words with a real trade meaning outside this system — safe to use, they carry
# their meaning in.
TRADE_MARKERS = {
    "criteria", "criterion", "ticket", "batch", "backlog", "constraint",
    "glossary", "verdict", "review", "diff", "worktree", "branch", "commit",
    "test", "suite", "scope", "out-of-scope item", "signoff", "gate", "escalate",
    "brief", "transcript", "ledger", "assumption", "decision", "survey",
}


STOPWORDS = {
    "and", "or", "not", "is", "one", "two", "plus", "the", "a", "an", "at",
    "from", "this", "that", "it", "its", "fresh", "arcs", "proposal",
}

_NOISE = re.compile(r"^[\d\W]|^\[a\]|\d+\s*(s|ms|x|%)$|^t0|^t1|^t2", re.I)


def _admissible(word: str) -> bool:
    """
    A term is a word for a thing, not a sentence about one.

    The design docs bold whole clauses ("escalation only climbs", "inquiry is
    free") — those are *laws*, and a law is not a term. Harvesting them as
    vocabulary produces a dictionary of slogans.
    """
    if not word or word in STOPWORDS:
        return False
    if _NOISE.search(word):
        return False
    return len(word.split()) <= 3


def _add(terms: dict[str, Term], word: str, level: str, source: str,
         sense: str = "", enrich_only: bool = False) -> None:
    word = word.strip().lower().rstrip(".:,;")
    if not _admissible(word):
        return
    if enrich_only and word not in terms:
        return                    # low-confidence sources may enrich, not coin
    t = terms.setdefault(word, Term(word=word, level=level))
    t.sources.add(source)
    if sense and not t.sense:
        t.sense = sense
    # Highest level wins: a word used both as a role and as machinery is a
    # collision worth surfacing, not an averaging problem.
    if level < t.level:
        t.level = level


def harvest() -> dict[str, Term]:
    terms: dict[str, Term] = {}

    for word, sense in L0_TERMS.items():
        _add(terms, word, "L0", "declared", sense)

    # ---- graph: roles, artefacts, operations, traffic -----------------------
    graph = json.loads((DESIGN / "graph.json").read_text(encoding="utf-8"))
    for n in graph["nodes"]:
        level = {"role": "L1", "artefact": "L2", "principal": "L0"}.get(n["type"], "L2")
        _add(terms, n["id"], level, "graph.node",
             (n.get("note") or "").split(".")[0][:160])
        if n["label"].lower() != n["id"]:
            _add(terms, n["label"], level, "graph.label")

    for e in graph["edges"]:
        if e["type"] in ("reads", "writes"):
            _add(terms, e.get("v", ""), "L3", "graph.operation", e.get("n", ""))
        elif e["type"] == "messages":
            _add(terms, e.get("v", ""), "L4", "graph.verb", e.get("n", ""))
        elif e["type"] == "refs":
            _add(terms, e.get("v", ""), "L6", "graph.refs")
        if e.get("rows"):
            _add(terms, e["rows"], "L6", "graph.rows", "which rows")
        if e.get("depth"):
            _add(terms, e["depth"], "L6", "graph.depth", "how much of each row")
        for noun in re.split(r"[+,/]| and ", e.get("n", "")):
            noun = noun.strip()
            if noun and len(noun.split()) <= 2:
                _add(terms, noun, "L2", "graph.noun")

    # ---- schema: the record, and the states ---------------------------------
    sql = paths.SCHEMA.read_text(encoding="utf-8")
    for table in re.findall(r"CREATE TABLE IF NOT EXISTS (\w+)", sql):
        _add(terms, table, "L2", "schema.table")
    for enum_block in re.findall(r"CHECK \(\w+ IN \(([^)]+)\)\)", sql):
        for value in re.findall(r"'([^']+)'", enum_block):
            _add(terms, value, "L5", "schema.state")

    # ---- prompts: what roles are actually told ------------------------------
    for path in sorted(PROMPTS.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for bold in re.findall(r"\*\*(.+?)\*\*", text):
            _add(terms, bold, "L3", f"prompt.{path.parent.name}", enrich_only=True)
        # What a prompt actually names as a callable is a term by definition.
        for call in re.findall(r"`?([a-z_]+\.[a-z_]+)\(", text):
            _add(terms, call, "L3", f"prompt.{path.parent.name}")
        for mode in re.findall(r"MODE:\s*(.+)", text):
            _add(terms, mode.strip().rstrip("."), "L3", "prompt.mode")

    # ---- the design docs: the laws' own words -------------------------------
    for doc in ("HANDOFF.md", "TESTS.md"):
        path = DOCS / doc
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        # Docs are a *low-confidence* source: they bold laws and emphasis as
        # well as terms, so they may only enrich what the structured sources
        # already define.
        for bold in re.findall(r"\*\*(.+?)\*\*", text):
            _add(terms, bold, "L0", f"doc.{doc}", enrich_only=True)

    # ---- machinery: runtime concepts in the code ----------------------------
    # `rglob`, not `glob`: the package is grouped now, so a top-level scan finds
    # only `paths.py` and the harvest quietly loses every L6 term.
    for path in sorted(paths.PACKAGE.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for cls in re.findall(r"^class (\w+)", path.read_text(encoding="utf-8"), re.M):
            _add(terms, re.sub(r"(?<!^)(?=[A-Z])", " ", cls), "L6",
                 f"code.{path.stem}")

    for t in terms.values():
        t.register = _register(t.word)
    return terms


def _register(word: str) -> str:
    parts = set(re.split(r"[\s_\-]+", word.lower()))
    if parts & MACHINE_MARKERS:
        return "machine"
    if parts & TRADE_MARKERS:
        return "trade"
    return "plain"


# ---------------------------------------------------------------------------
# Steps 2-4 of the system-glossary pass: purpose, hierarchy, duplication.
#
# The method is from plans/system-prompt-fixer.md, which had five steps to my
# one and a half. Steps 2 and 4 (purpose, name synthesis) are judgement and stay
# judgement -- the tool surfaces candidates and structure; a person names things.
# Pretending otherwise produces a dictionary that is internally consistent and
# describes nothing.
# ---------------------------------------------------------------------------

def purposes() -> dict[str, str]:
    """Step 2: what each named thing is for, taken from where it was defined."""
    out: dict[str, str] = {}
    graph = json.loads((DESIGN / "graph.json").read_text(encoding="utf-8"))
    for n in graph["nodes"]:
        note = (n.get("note") or "").strip()
        if note:
            out[n["id"]] = note.split(".")[0][:150]

    # Schema comments sit above the table they explain.
    sql = paths.SCHEMA.read_text(encoding="utf-8").splitlines()
    comment: list[str] = []
    for line in sql:
        st = line.strip()
        if st.startswith("--"):
            comment.append(st.lstrip("- ").strip())
        elif st.startswith("CREATE TABLE"):
            m = re.search(r"CREATE TABLE IF NOT EXISTS (\w+)", st)
            if m and comment:
                out.setdefault(m.group(1), " ".join(comment)[:150])
            comment = []
        elif not st:
            comment = []
    return out


def aliases() -> list[tuple[str, tuple[str, ...], str]]:
    """
    Step 3, duplications: one referent carrying two names.

    The graph speaks in artefacts and the schema in tables, and the binding
    between them is deliberate -- but where the two names differ, a role reads
    one word and the database holds another. That is the same failure the
    Lexicon of Behavior would introduce by renaming for effect, except it is
    already here.
    """
    from rota.core.db import TABLES_OF_ARTEFACT

    out = []
    for artefact, tables in TABLES_OF_ARTEFACT.items():
        differing = tuple(t for t in tables if t != artefact)
        if differing:
            verdict = ("same referent, two names" if len(tables) == 1
                       else "one artefact spread over several tables")
            out.append((artefact, differing, verdict))
    return out


def hierarchy() -> list[dict]:
    """Step 3, relationships: what owns what, and what points at what."""
    from rota.design import graph as graph_mod

    g = graph_mod.load()
    rows = []
    for a in sorted(g.artefacts):
        node = g.nodes[a]
        rows.append({
            "term": a,
            "owner": ", ".join(sorted(g.writer_of(a))) or "(the system)",
            "readers": ", ".join(sorted(r for r in g.roles if a in g.read_set(r))) or "-",
            "refs": ", ".join(sorted(e.t for e in g.of_type("refs") if e.s == a)) or "-",
            "kind": "journal" if not node.contact else "record",
        })
    return rows


def render_analysis() -> str:
    """The top-down report: levels first, then structure, then the candidates."""
    terms = harvest()
    pur = purposes()
    lines = []

    lines.append("=" * 78)
    lines.append("STEP 1-2  every named thing, and what it is for — top down")
    lines.append("=" * 78)
    grouped = by_level(terms)
    for level, label in LEVELS.items():
        entries = grouped.get(level, [])
        if not entries or level in ("L5", "L6"):
            continue
        lines.append(f"\n--- {level}  {label}  ({len(entries)})")
        for t in entries:
            why = pur.get(t.word, t.sense)
            mark = {"machine": "!", "trade": "~", "plain": " "}[t.register]
            lines.append(f" {mark} {t.word:<24} {why[:88]}")

    lines.append("\n" + "=" * 78)
    lines.append("STEP 3  hierarchy — who owns what, who reads it, what it points at")
    lines.append("=" * 78)
    for r in hierarchy():
        lines.append(f"  {r['term']:<14} {r['kind']:<8} owner={r['owner']:<20} "
                     f"readers={r['readers'][:40]}")
        if r["refs"] != "-":
            lines.append(f"  {'':<14} {'':<8} refs -> {r['refs']}")

    lines.append("\n" + "=" * 78)
    lines.append("STEP 3  duplication — one referent, two names")
    lines.append("=" * 78)
    for artefact, tables, verdict in aliases():
        lines.append(f"  graph says {artefact:<12} schema says {', '.join(tables):<38} {verdict}")

    lines.append("\n" + "=" * 78)
    lines.append("STEP 3  collision — one name, two referents")
    lines.append("=" * 78)
    for word, sources in collisions(terms):
        kinds = sorted({s.split('.')[-1] for s in sources})
        if len(kinds) > 1:
            lines.append(f"  {word:<16} {', '.join(kinds)}")

    counts = defaultdict(int)
    for t in terms.values():
        counts[t.register] += 1
    lines.append(f"\nregister: {dict(counts)}   (! machine  ~ trade  · plain)")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# The findings
# ---------------------------------------------------------------------------

# Two senses that are the *same* referent seen from two sides. Reporting these
# as collisions is what made the first sweep unusable: 17 findings of which 10
# were the system being consistent. A collision is two referents; this is one
# referent named once and reached twice.
COMPOSITION = {
    frozenset({"node", "table"}),        # artefact and the table holding it
    frozenset({"noun", "table"}),        # a column and what it holds
    frozenset({"node", "noun", "table"}),
    frozenset({"noun", "operation"}),    # an operation and what it returns
}


def collisions(terms: dict[str, Term]) -> list[tuple[str, list[str]]]:
    """
    One word carrying more than one job.

    This is exactly what D1 asks Terminologist to catch, and it is the finding that
    matters most: a word meaning two things costs more than a word that is merely
    ugly, because nobody notices it going wrong.

    Composition is excluded — `verdicts` the artefact and `verdicts` the table
    are one thing, and `code.diff` returning a "batch diff" is an operation
    named after its result. Both would be *worse* renamed apart. What is left is
    genuine ambiguity, which is why the check can be a hard constraint.
    """
    out = []
    for word, t in sorted(terms.items()):
        distinct = {s.split(".")[-1] for s in t.sources
                    if s.split(".")[0] in ("graph", "schema")}
        if len(distinct) > 1 and frozenset(distinct) not in COMPOSITION:
            out.append((word, sorted(t.sources)))
    return out


def machine_words_facing_roles(terms: dict[str, Term]) -> list[Term]:
    """Machine register appearing in a prompt: a mechanism that has leaked."""
    return sorted(
        (t for t in terms.values()
         if t.register == "machine" and any(s.startswith("prompt.") for s in t.sources)),
        key=lambda t: t.word,
    )


def by_level(terms: dict[str, Term]) -> dict[str, list[Term]]:
    grouped: dict[str, list[Term]] = defaultdict(list)
    for t in terms.values():
        grouped[t.level].append(t)
    return {k: sorted(v, key=lambda t: t.word) for k, v in sorted(grouped.items())}


def render(terms: dict[str, Term]) -> str:
    lines = [f"{len(terms)} terms in use", ""]
    grouped = by_level(terms)

    for level, label in LEVELS.items():
        entries = grouped.get(level, [])
        if not entries:
            continue
        lines.append(f"=== {level}  {label}  ({len(entries)}) ".ljust(78, "="))
        for t in entries:
            mark = {"machine": "!", "trade": "~", "plain": " "}[t.register]
            sense = f"  — {t.sense[:70]}" if t.sense else ""
            lines.append(f" {mark} {t.word:<28}{sense}")
        lines.append("")

    coll = collisions(terms)
    lines.append(f"=== COLLISIONS ({len(coll)}) — one word, more than one job ".ljust(78, "="))
    for word, sources in coll:
        lines.append(f"   {word:<28} {', '.join(sources)}")
    lines.append("")

    leaked = machine_words_facing_roles(terms)
    lines.append(f"=== LEAKED MACHINERY ({len(leaked)}) — machine words in prompts ".ljust(78, "="))
    for t in leaked:
        lines.append(f"   {t.word:<28} {', '.join(sorted(t.sources))}")

    counts = defaultdict(int)
    for t in terms.values():
        counts[t.register] += 1
    lines += ["", f"register: {dict(counts)}"]
    return "\n".join(lines)


def main() -> None:
    if "--analyse" in sys.argv:
        print(render_analysis())
        return
    terms = harvest()
    if "--json" in sys.argv:
        print(json.dumps([t.as_dict() for t in terms.values()], indent=2))
    else:
        print(render(terms))


if __name__ == "__main__":
    main()
