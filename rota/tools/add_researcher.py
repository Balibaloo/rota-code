"""
Amendment 5: the Researcher.

Separate from `amend_graph.py` because that script applies the amendments agreed
in the session before implementation and re-running it would double-apply them.
Same discipline though — a script rather than a hand-edit, so the change set is
reviewable as code and re-runnable. This one is idempotent: it strips its own
nodes and edges before adding them.

**Why a role and not a tool.** A new role is justified by a trust boundary, not
by a capability. Git history is local, hermetic and replayable, so it is read
tools on the roles that need it. The internet is none of those, so it is
contained: one role, one artefact, no execution edge, and nothing it writes
enters the model unless a role that owns an artefact chooses to cite it.

**What it is answerable for.** Whether a source is authoritative and whether it
actually says what it is claimed to say. That is a judgement no other role can
make, which is the test a role has to pass to exist.

**The contact list is not written here.** Law 3 derives it: a role may message
the Researcher because it reads `references`, and the Researcher may message back
because it writes what they read. The five askers are exactly the roles that can
cite an external source into an artefact they own. Critic is not among them — it
judges against internal criteria and owns nothing to cite into — and neither is
Liaison, whose outside is the principal.

**`web` is a fact artefact.** Reading it yields evidence, not judgement, so it
generates no contact and nobody can "ask the web". That is the same treatment
`code`, `transcript`, `decisions` and `ledger` already get.
"""
from __future__ import annotations

import json

from .. import paths

GRAPH = paths.DESIGN / "graph.json"
LAYOUT = paths.DESIGN / "layout.json"

NEW_NODES = ("researcher", "references", "web")

# The roles that can cite an external source into an artefact they own. This
# list is not the contact list -- law 3 derives that from the read edges below.
ASKERS = ("terminologist", "architect", "vision_keeper", "developer", "tester")


def main() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))

    # Idempotent: strip anything this script previously added.
    nodes = [n for n in graph["nodes"] if n["id"] not in NEW_NODES]
    edges = [e for e in graph["edges"]
             if e["s"] not in NEW_NODES and e["t"] not in NEW_NODES]

    nodes.extend([
        {
            "id": "researcher",
            "label": "Researcher",
            "type": "role",
            "note": (
                "Answers questions of fact about things outside this repository, "
                "with sources. Does not judge, implement, or set scope. Owns no "
                "shared artefact: it writes references and the asking role decides "
                "whether to cite them, so nothing enters the model unless a role "
                "with ownership put it there. Never woken by a predicate -- it "
                "drains nothing, so a predicate waking it would fire forever; "
                "external push arrives through the owner of whatever cited the "
                "stale reference. Knows nothing of batches, criteria or "
                "constraints: questions from roles, answers with sources."
            ),
        },
        {
            "id": "references",
            "label": "References",
            "type": "artefact",
            "note": (
                "What an outside source says, and where. One row per source: the "
                "URL, the passage, the claim it supports, and a content hash that "
                "makes the page changing a drift event rather than a silent lie. "
                "The quote is not decoration -- everywhere else conclusions travel "
                "and reasoning stays home, but for an external source the passage "
                "IS the evidence, and without it nobody can check whether the "
                "Researcher read it correctly."
            ),
        },
        {
            "id": "web",
            "label": "The open web",
            "type": "artefact",
            "owner": "world",
            "contact": False,
            "contact_why": (
                "a fact artefact, and the only one outside the engagement: reading "
                "it yields evidence, not judgement, and there is nobody in this "
                "system to ask about it"
            ),
            "note": (
                "Reachable only from the Researcher, and only within the domain "
                "allowlist the principal configures. Queries are constructed from "
                "the question, never forwarded: the asker may put whatever context "
                "it likes into a question, and that context must not reach the wire."
            ),
        },
    ])

    edges.extend([
        {"s": "researcher", "t": "references", "type": "writes", "v": "record",
         "n": "source, passage, claim", "rows": "single"},
        # An owner reads what it owns. Also the cheapest possible answer: a
        # question about a source already recorded needs no fetch at all.
        {"s": "researcher", "t": "references", "type": "reads", "v": "load",
         "n": "what has already been looked up", "rows": "delta",
         "depth": "index"},
        # Fetch, and no search. A search verb would need a search engine, a key,
        # and a second trust boundary — and it turns out not to be needed for the
        # thing this exists to do. Source URLs arrive two ways that are both
        # better than a query: the asker supplies one, or the codebase does.
        # oauthlib's modules cite their own specification inline, down to
        # `#section-3.4.1.3.2`, so Architect reads a docstring and asks what the
        # clause it already names actually says. The repository is the index.
        {"s": "researcher", "t": "web", "type": "reads", "v": "fetch",
         "n": "one passage", "label": "bounded extract, allowlisted domains only",
         "rows": "single", "depth": "body"},
    ])

    for role in ASKERS:
        edges.extend([
            {"s": role, "t": "references", "type": "reads", "v": "load",
             "n": "sources cited or offered", "rows": "delta", "depth": "body"},
            # `prose` is the one declared exception to law 2's no-words rule,
            # and it is structural rather than a convenience: every other
            # message travels between roles sharing a database, where an id
            # means something at both ends. The Researcher shares nothing, so
            # refs carry no meaning to it and a question with no words is no
            # question. Declared on the edge so it is one fact in one place.
            {"s": role, "t": "researcher", "type": "messages", "v": "question",
             "n": "a question of fact about something outside this repository",
             "prose": "question", "rows": "single"},
            {"s": "researcher", "t": role, "type": "messages", "v": "answer",
             "n": "the answer, with sources — or what was tried and failed",
             "rows": "single"},
        ])

    graph["nodes"], graph["edges"] = nodes, edges
    GRAPH.write_text(json.dumps(graph, indent=1) + "\n", encoding="utf-8")

    # Off to the right of Developer, clear of the delivery loop: the Researcher
    # touches no artefact any other role writes, so nothing crosses to reach it.
    layout.update({
        "researcher": {"x": 1986, "y": 992},
        "references": {"x": 1986, "y": 1073},
        "web": {"x": 2320, "y": 992},
    })
    LAYOUT.write_text(json.dumps(layout, indent=1, sort_keys=True) + "\n",
                      encoding="utf-8")

    print(f"nodes {len(nodes)}  edges {len(edges)}  askers {list(ASKERS)}")


if __name__ == "__main__":
    main()
