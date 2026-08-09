"""
Apply the agreed design amendments to the extracted graph.

This runs once, after extract_graph.js, and rewrites rota/design/graph.json in
place. It is deliberately a script rather than a hand-edit so the change set is
reviewable as code and re-runnable if the HTML is re-extracted.

Amendments (all agreed in the design session preceding implementation):

  1. Planner dissolved. Ordering is a topological sort in scheduler code, not an
     LLM role. Its schedule artefact survives (the scheduler reads it); Interface
     gains a schedule read so client ordering questions can still be answered.
  2. Tester added, between Domain/Vision and Critic. Reads criteria + glossary,
     writes tests. Starved of the diff on purpose: tests written after seeing an
     implementation encode the implementation.
  3. Developer reads tests; Critic reads tests. Critic judges the diff *given*
     the tests and may challenge Tester; Developer may challenge Tester too.
  4. Backlog read edges for its three writers. They previously wrote an artefact
     none of them could read — Domain specified criteria for tickets it could not
     see, Architect batched tickets it could not read.
"""
from __future__ import annotations

import json
from pathlib import Path

DESIGN = Path(__file__).resolve().parents[1] / "design"
GRAPH = DESIGN / "graph.json"
LAYOUT = DESIGN / "layout.json"


def main() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    nodes, edges = graph["nodes"], graph["edges"]

    # ---- 1. Planner dissolved -------------------------------------------------
    nodes = [n for n in nodes if n["id"] != "planner"]
    edges = [e for e in edges if e["s"] != "planner" and e["t"] != "planner"]
    layout.pop("planner", None)

    # The schedule artefact survives as scheduler-owned derived state.
    for n in nodes:
        if n["id"] == "schedule":
            n["note"] = (
                "Order between batches, derived by the scheduler as a topological "
                "sort of Architect's declared dependency facts. No dates. Not owned "
                "by any role: ordering carries no judgement beyond the deps, so "
                "there is nothing for a role to decide. Unsatisfiable deps (a cycle) "
                "wake Architect with the conflicting facts."
            )
            n["owner"] = "scheduler"

    # Interface answers client ordering questions from the schedule directly.
    edges.append(
        {"s": "interface", "t": "schedule", "type": "reads", "v": "consult",
         "n": "batch order", "a": "index", "label": "client ordering questions"}
    )

    # ---- 2. Tester ------------------------------------------------------------
    nodes.append({
        "id": "tester", "label": "Tester", "type": "role",
        "note": (
            "Writes executable tests from criteria, before the Developer's diff "
            "exists and without ever seeing it. Its isolation is temporal, not "
            "informational: Critic can read everything Tester reads, so the only "
            "thing that makes these tests intent rather than description is that "
            "they were written first. Do not merge this role into Critic."
        ),
    })
    nodes.append({
        "id": "tests", "label": "Test suite", "type": "artefact",
        "note": (
            "Criteria made executable. Machine-ratified intent: outranks all prose "
            "in the repo as evidence. One suite per batch, refs the criteria it "
            "encodes."
        ),
    })
    layout["tester"] = {"x": 1320, "y": 850}
    layout["tests"] = {"x": 1420, "y": 400}

    edges += [
        {"s": "tester", "t": "tests", "type": "writes", "v": "author",
         "n": "executable tests", "a": "batch"},
        {"s": "tester", "t": "backlog", "type": "reads", "v": "load",
         "n": "criteria for batch", "a": "batch", "label": "criteria only — no diff"},
        {"s": "tester", "t": "glossary", "type": "reads", "v": "lookup",
         "n": "term", "a": "single"},
        {"s": "tester", "t": "tests", "type": "reads", "v": "consult",
         "n": "own suite", "a": "full", "label": "before amending"},

        # 3. Developer and Critic both read tests; both may dispute them.
        {"s": "developer", "t": "tests", "type": "reads", "v": "load",
         "n": "tests for batch", "a": "batch"},
        {"s": "critic", "t": "tests", "type": "reads", "v": "load",
         "n": "tests for batch", "a": "batch"},
        {"s": "developer", "t": "tester", "type": "messages", "v": "challenge",
         "n": "test disputes criterion", "a": "single"},
        {"s": "critic", "t": "tester", "type": "messages", "v": "challenge",
         "n": "test does not encode criterion", "a": "single"},
        {"s": "tester", "t": "vision", "type": "messages", "v": "question",
         "n": "criterion or scope gap", "a": "single"},
        {"s": "tester", "t": "domain", "type": "messages", "v": "question",
         "n": "term ambiguity", "a": "single"},

        # refs
        {"s": "tests", "t": "backlog", "type": "refs", "v": "encodes criterion",
         "card": "n:1"},
        {"s": "verdicts", "t": "tests", "type": "refs", "v": "cites result",
         "card": "n:n"},

        # ---- 4. Backlog reads for its three writers --------------------------
        {"s": "vision", "t": "backlog", "type": "reads", "v": "consult",
         "n": "own tickets", "a": "full", "label": "before amending"},
        {"s": "domain", "t": "backlog", "type": "reads", "v": "consult",
         "n": "own criteria", "a": "full", "label": "before amending"},
        {"s": "domain", "t": "backlog", "type": "reads", "v": "scan",
         "n": "tickets", "a": "index", "label": "cannot specify for unseen tickets"},
        {"s": "architect", "t": "backlog", "type": "reads", "v": "consult",
         "n": "own batches", "a": "full", "label": "before amending"},
        {"s": "architect", "t": "backlog", "type": "reads", "v": "scan",
         "n": "tickets + criteria", "a": "index", "label": "collision judgement needs touch sets"},
    ]

    # Backlog note no longer hedges on ownership: the table split resolves it.
    for n in nodes:
        if n["id"] == "backlog":
            n["note"] = (
                "Tickets (Vision), criteria (Domain), batches (Architect) — one "
                "writer per table, which is what law 1 means by single writer: one "
                "writer per row. Batches are complete feature sets, immutable once "
                "formed: priority moves them whole; only a scope change may "
                "recompose one. One worktree and one PR per batch, tracing to "
                "exactly one approved item."
            )

    graph["nodes"], graph["edges"] = nodes, edges
    GRAPH.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    LAYOUT.write_text(json.dumps(layout, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    roles = [n["id"] for n in nodes if n["type"] == "role"]
    print(f"nodes={len(nodes)} edges={len(edges)}")
    print(f"roles({len(roles)})={roles}")


if __name__ == "__main__":
    main()
