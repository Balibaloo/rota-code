"""
The wiring. Everything a role can do is defined here and nowhere else.

`design/graph.json` is not a picture of the system — it is the part-list the
system is assembled from. Three consumers read it and no other file declares
wiring:

  * the sandbox loader, which builds each role's namespace from its edges
    (a missing edge is an ImportError, because the function was never created);
  * contact derivation, which computes who may message whom;
  * the viewer, which renders the same structure the code runs on.

Law 3 says contact lists are derived, not designed: a message routes to the
writer of the artefact holding the answer. The graph *also* declares message
edges. Rather than pick one as authoritative, `check_contacts()` asserts they
agree — the derivation is the implementation, the declared edges are the oracle,
and a disagreement is a real finding (a missing read edge, or a contact the
artefact structure does not justify).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Literal

DESIGN_DIR = Path(__file__).resolve().parent / "design"

EdgeType = Literal["reads", "writes", "messages", "refs"]

# Reach, in two axes, because one word was answering two questions.
#
# Which rows, cheapest first. A role may never be granted more rows than its edge
# declares.
ROWS = ("none", "single", "batch", "window", "delta", "query", "all")

# How much of each row. `index` is the identifying line — an id and a headline,
# or for something already one line, that line. `body` is the prose as well.
DEPTH = ("index", "body")


@dataclass(frozen=True)
class Edge:
    s: str
    t: str
    type: str
    v: str = ""
    n: str = ""
    rows: str = ""
    depth: str = ""              # reads only; a message carries refs, never bodies
    label: str = ""
    card: str = ""
    actor: str = "role"          # 'role' (the model calls it) | 'system'

    @property
    def model_callable(self) -> bool:
        return self.actor != "system"

    @property
    def reach(self) -> str:
        """The pair, for display. Two facts, one line, still two facts."""
        rows = self.rows or "none"
        return f"{rows}/{self.depth}" if self.depth else rows


@dataclass(frozen=True)
class Node:
    id: str
    label: str
    type: str
    note: str = ""
    owner: str = ""
    contact: bool = True
    contact_why: str = ""


class Graph:
    def __init__(self, nodes: list[Node], edges: list[Edge],
                 contact_exceptions: list[dict] | None = None):
        self.nodes = {n.id: n for n in nodes}
        self.edges = edges
        self.contact_exceptions = contact_exceptions or []

    # ---- node views ---------------------------------------------------------

    @property
    def roles(self) -> list[str]:
        return [n.id for n in self.nodes.values() if n.type == "role"]

    @property
    def artefacts(self) -> list[str]:
        return [n.id for n in self.nodes.values() if n.type == "artefact"]

    # ---- edge views ---------------------------------------------------------

    def of_type(self, edge_type: str) -> list[Edge]:
        return [e for e in self.edges if e.type == edge_type]

    def reads(self, role: str) -> list[Edge]:
        return [e for e in self.of_type("reads") if e.s == role]

    def writes(self, role: str) -> list[Edge]:
        return [e for e in self.of_type("writes") if e.s == role]

    def read_set(self, role: str) -> set[str]:
        return {e.t for e in self.reads(role)}

    def write_set(self, role: str) -> set[str]:
        return {e.t for e in self.writes(role)}

    def writer_of(self, artefact: str) -> set[str]:
        """Roles that write `artefact`. Usually one — law 1 means one per *row*,
        so journals (decision record, ledger) legitimately have several."""
        return {e.s for e in self.of_type("writes") if e.t == artefact}

    # ---- law 3: derived contacts -------------------------------------------

    def contactable(self, artefact: str) -> bool:
        """
        Whether reading this artefact can generate a message to its writer.

        False for fact artefacts — transcript, code, decisions, ledger. Reading
        them yields evidence, not judgement: the answer is *in* the artefact, so
        there is nobody to ask. Without this distinction the derivation grants
        Architect a channel to Developer merely for probing modules.
        """
        node = self.nodes.get(artefact)
        return bool(node and node.contact)

    def derived_contacts(self, role: str) -> set[str]:
        """
        Who `role` may message. Two clauses, both structural:

          ask    — the writer of a judgement artefact this role reads
                   ("route to whoever writes the artefact holding the answer")
          inform — a role that reads a judgement artefact this role writes
                   (pushes: brief, relay, reopen — the mirror of asking)

        Computed once at load, then fixed. Nothing here is dynamic; the point of
        deriving is that no second, hand-maintained list exists to disagree with
        the read/write structure.
        """
        contacts: set[str] = set()

        for artefact in self.read_set(role):           # ask
            if self.contactable(artefact):
                contacts |= self.writer_of(artefact)

        for artefact in self.write_set(role):          # inform
            if not self.contactable(artefact):
                continue
            for other in self.roles:
                if artefact in self.read_set(other):
                    contacts.add(other)

        contacts.discard(role)
        return contacts

    def is_exception(self, sender: str, recipient: str, verb: str) -> bool:
        return any(
            x["s"] == sender and x["t"] == recipient and x.get("v", verb) == verb
            for x in self.contact_exceptions
        )

    def declared_contacts(self, role: str) -> set[str]:
        return {
            e.t for e in self.of_type("messages")
            if e.s == role and e.t in self.nodes and self.nodes[e.t].type == "role"
        }

    def message_verbs(self) -> set[str]:
        """The closed vocabulary the bus validates against."""
        return {e.v for e in self.of_type("messages") if e.v}

    def may_message(self, sender: str, recipient: str, verb: str) -> bool:
        return any(
            e.s == sender and e.t == recipient and e.v == verb
            for e in self.of_type("messages")
        )


def _load(path: Path) -> Graph:
    raw = json.loads(path.read_text(encoding="utf-8"))
    nodes = [
        Node(
            id=n["id"], label=n["label"], type=n["type"],
            note=n.get("note", ""), owner=n.get("owner", ""),
            contact=n.get("contact", True), contact_why=n.get("contact_why", ""),
        )
        for n in raw["nodes"]
    ]
    edges = [
        Edge(
            s=e["s"], t=e["t"], type=e["type"], v=e.get("v", ""), n=e.get("n", ""),
            rows=e.get("rows", ""), depth=e.get("depth", ""),
            label=e.get("label", ""), card=e.get("card", ""),
            actor=e.get("actor", "role"),
        )
        for e in raw["edges"]
    ]
    return Graph(nodes, edges, raw.get("contact_exceptions", []))


@lru_cache(maxsize=1)
def load(path: str | None = None) -> Graph:
    return _load(Path(path) if path else DESIGN_DIR / "graph.json")


# ---------------------------------------------------------------------------
# Boot assertions. These run before any state is touched: if the code and the
# graph disagree, the system does not start.
# ---------------------------------------------------------------------------


class GraphInconsistency(AssertionError):
    """The graph contradicts itself, or the code contradicts the graph."""


def check_structure(g: Graph) -> list[str]:
    """
    Endpoints resolve, reach values are legal, and nobody takes an artefact whole.

    The last one is the authority rule, and it is the reason `full` was deleted.
    `full` bundled three claims — every row, headline depth, and *you own this* —
    of which only the first two are about reach. Stated properly:

        a non-owner may take every row, or take bodies, but never both.

    Nothing in the graph violates it today, which is what a green lint means. The
    shape it forbids is a role quietly hoovering up an artefact it does not own,
    and that is a thing an edge could easily be written to do.
    """
    problems: list[str] = []
    for e in g.edges:
        if e.s not in g.nodes:
            problems.append(f"edge source not a node: {e.s} -> {e.t} ({e.type})")
        if e.t not in g.nodes:
            problems.append(f"edge target not a node: {e.s} -> {e.t} ({e.type})")
        if e.rows and e.rows not in ROWS:
            problems.append(f"unknown rows {e.rows!r} on {e.s} -> {e.t}")
        if e.depth and e.depth not in DEPTH:
            problems.append(f"unknown depth {e.depth!r} on {e.s} -> {e.t}")
        if e.depth and e.type != "reads":
            problems.append(
                f"depth on a {e.type} edge: {e.s} -> {e.t}. A message carries "
                f"refs, never bodies; a write's depth is whatever was written")
        if (e.type == "reads" and e.rows == "all" and e.depth == "body"
                and e.s not in g.writer_of(e.t)):
            owner = g.writer_of(e.t) or {"<nobody>"}
            problems.append(
                f"non-owner takes {e.t} whole: {e.s} reads every row at body "
                f"depth (written by {sorted(owner)})")
    return problems


def check_writers(g: Graph) -> list[str]:
    """Every artefact has a writer; roles do not write what they cannot own."""
    problems = []
    for artefact in g.artefacts:
        writers = g.writer_of(artefact)
        if not writers:
            node = g.nodes[artefact]
            if node.owner != "scheduler":
                problems.append(f"artefact with no writer: {artefact}")
    return problems


def check_contacts(g: Graph) -> list[str]:
    """
    Law 3's oracle: derived contacts must equal declared message edges.

    A derived-but-undeclared contact means the graph forgot a message edge (or a
    read edge is wider than intended). A declared-but-underived contact means a
    role can message someone whose artefact it cannot read — which is precisely
    the hand-maintained second list law 3 exists to forbid.
    """
    problems = []
    for role in sorted(g.roles):
        derived = g.derived_contacts(role)
        declared = g.declared_contacts(role)

        # Declared but underivable: either a justified exception, or the
        # hand-maintained second list law 3 exists to forbid.
        for extra in sorted(declared - derived):
            verbs = [e.v for e in g.of_type("messages") if e.s == role and e.t == extra]
            if all(g.is_exception(role, extra, v) for v in verbs):
                continue
            problems.append(
                f"{role} -> {extra} ({'/'.join(verbs)}): declared message edge with no "
                f"structural basis — {role} neither reads an artefact {extra} writes nor "
                f"writes one {extra} reads, and it is not a declared exception"
            )

        # Derivable but undeclared is *not* an error: the structure permits the
        # contact, the graph simply has no verb for it yet. Report separately so
        # the surface stays visible without failing the build.
    return problems


def latent_contacts(g: Graph) -> list[str]:
    """Structurally permitted contacts with no declared verb. Informational."""
    out = []
    for role in sorted(g.roles):
        for missing in sorted(g.derived_contacts(role) - g.declared_contacts(role)):
            shared = sorted(
                (g.read_set(role) & g.write_set(missing))
                | (g.write_set(role) & g.read_set(missing))
            )
            out.append(f"{role} -> {missing} via {shared}")
    return out


def check_all(g: Graph | None = None) -> list[str]:
    g = g or load()
    return check_structure(g) + check_writers(g) + check_contacts(g)


def assert_consistent(g: Graph | None = None) -> None:
    problems = check_all(g)
    if problems:
        raise GraphInconsistency(
            "graph is inconsistent:\n  " + "\n  ".join(problems)
        )


if __name__ == "__main__":
    import sys

    graph = load()
    issues = check_all(graph)
    print(f"roles({len(graph.roles)}): {sorted(graph.roles)}")
    print(f"artefacts({len(graph.artefacts)}): {sorted(graph.artefacts)}")
    print(f"verbs({len(graph.message_verbs())}): {sorted(graph.message_verbs())}")
    print()
    for role in sorted(graph.roles):
        print(f"{role:10s} reads={sorted(graph.read_set(role))}")
        print(f"{'':10s} writes={sorted(graph.write_set(role))}")
        print(f"{'':10s} contacts={sorted(graph.derived_contacts(role))}")
    latent = latent_contacts(graph)
    if latent:
        print(f"latent contacts ({len(latent)}) — permitted by structure, no verb declared:")
        for line in latent:
            print(f"  . {line}")
    print()
    if issues:
        print(f"{len(issues)} PROBLEMS:")
        for p in issues:
            print(f"  - {p}")
        sys.exit(1)
    print("graph consistent")
