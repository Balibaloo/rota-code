"""
Vocabulary extraction — Domain's job, run on ourselves.

The system's whole thesis is that meaning must be canonical: the Domain role
exists because a term quietly meaning two things is the most expensive kind of
bug. Building it in sloppy vocabulary is not ironic, it is the same failure one
level up — our terms leak into every prompt, and the roles reason in them.

So: harvest every term actually in use, from every source that defines one, and
sort them by **level of abstraction** rather than alphabetically. Naming decisions
made bottom-up produce a consistent-looking dictionary describing an incoherent
system; made top-down they produce a system whose lower levels have somewhere to
hang from.

Levels, highest first:

    L0  the engagement   what the whole thing is, and its relationship to a client
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

ROOT = Path(__file__).resolve().parents[2]
ROTA = ROOT / "rota"
DESIGN = ROTA / "design"
PROMPTS = ROTA / "prompts"
DOCS = ROOT / "rota_tui"

# The top level is *declared*, not harvested: these are the concepts the whole
# thing rests on, and there is no source to extract them from because they are
# what every other source presupposes.
L0_TERMS = {
    "engagement": "the whole relationship with one client, from first ask to milestone",
    "client": "the single technical person who holds final authority",
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
    "test", "suite", "scope", "non-goal", "signoff", "gate", "escalate",
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
        level = {"role": "L1", "artefact": "L2", "client": "L0"}.get(n["type"], "L2")
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
        if e.get("a"):
            _add(terms, e["a"], "L6", "graph.scope", "scope adjective")
        for noun in re.split(r"[+,/]| and ", e.get("n", "")):
            noun = noun.strip()
            if noun and len(noun.split()) <= 2:
                _add(terms, noun, "L2", "graph.noun")

    # ---- schema: the record, and the states ---------------------------------
    sql = (ROTA / "schema.sql").read_text(encoding="utf-8")
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
    for path in sorted(ROTA.glob("*.py")):
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
# The findings
# ---------------------------------------------------------------------------

def collisions(terms: dict[str, Term]) -> list[tuple[str, list[str]]]:
    """
    One word carrying more than one job.

    This is exactly what D1 asks Domain to catch, and it is the finding that
    matters most: a word meaning two things costs more than a word that is merely
    ugly, because nobody notices it going wrong.
    """
    out = []
    for word, t in sorted(terms.items()):
        kinds = {s.split(".")[0] + ":" + s.split(".")[-1] for s in t.sources}
        distinct = {s.split(".")[-1] for s in t.sources
                    if s.split(".")[0] in ("graph", "schema")}
        if len(distinct) > 1:
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
    terms = harvest()
    if "--json" in sys.argv:
        print(json.dumps([t.as_dict() for t in terms.values()], indent=2))
    else:
        print(render(terms))


if __name__ == "__main__":
    main()
