"""
Second amendment pass: make law 3 actually computable.

Running the contact oracle against the first-pass graph produced 22 findings.
They had three causes, all real:

  1. `batch` is a legal scope in HANDOFF §3's grammar
     (none < single < batch < index < window < delta < query < full) but was
     missing from the legend comment in team-graph.html, which is what the first
     SCOPES tuple was copied from. Doc-vs-doc drift, found mechanically.
     -> fixed in rota/graph.py, not here.

  2. `backlog` is one node with three writers, so deriving contacts at artefact
     granularity gave Critic a channel to all of Vision, Domain and Architect
     merely for reading criteria. Law 1 means one writer per *row*; the schema
     splits the backlog into tickets/criteria/batches, and the graph must match
     or the derivation stays too coarse.
     -> split the node here.

  3. Deriving "contacts = writers of what I read" covers only questions. Two
     other things exist:
       * fact artefacts — transcript, code, decisions, ledger. Reading them
         yields facts, not judgement; there is nobody to ask, because the answer
         is in the artefact. Marked `contact: false`.
       * pushes — a role informing a role that reads what it writes (brief,
         relay, reopen). Derived by the mirrored clause.
     One edge resists both and is a deliberate exception: architect -> critic
     `finding`. Critic must not read the system model (that is its starvation),
     so the conclusion is pushed to it precisely because it cannot fetch it.
     Exceptions are listed with reasons rather than silently permitted.
"""
from __future__ import annotations

import json
from pathlib import Path

DESIGN = Path(__file__).resolve().parents[1] / "design"
GRAPH = DESIGN / "graph.json"
LAYOUT = DESIGN / "layout.json"

# Which of the old `backlog` edges belong to which split table.
BACKLOG_SPLIT = {
    ("vision", "writes", "slice"): "tickets",
    ("vision", "writes", "prioritize"): "batches",
    ("domain", "writes", "specify"): "criteria",
    ("architect", "writes", "batch"): "batches",
    ("vision", "reads", "consult"): "tickets",
    ("domain", "reads", "consult"): "criteria",
    ("domain", "reads", "scan"): "tickets",
    ("architect", "reads", "consult"): "batches",
    ("architect", "reads", "scan"): "tickets",
    ("developer", "reads", "load"): "criteria",
    ("critic", "reads", "load"): "criteria",
    ("tester", "reads", "load"): "criteria",
}

FACT_ARTEFACTS = {
    "transcript": "verbatim record; read to recover emphasis, never to ask its recorder",
    "code": "self-describing; a question about the codebase is answered by probing it",
    "decisions": "append-only journal; entries carry authors but are read as evidence",
    "ledger": "append-only journal; open assumptions are facts to present, not questions",
}

EXCEPTIONS = [
    {
        "s": "architect", "t": "critic", "v": "finding",
        "why": (
            "Critic must not read the system model — that starvation is what makes "
            "its verdict independent. The conclusion is therefore pushed to it "
            "precisely because it cannot fetch it. Underivable by construction."
        ),
    },
]


def main() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    nodes, edges = graph["nodes"], graph["edges"]

    # ---- 2. split backlog into its three single-writer tables ----------------
    backlog_note = next(n["note"] for n in nodes if n["id"] == "backlog")
    nodes = [n for n in nodes if n["id"] != "backlog"]
    nodes += [
        {"id": "tickets", "label": "Tickets", "type": "artefact",
         "note": "Sliced by Vision from approved items. One writer. " + backlog_note},
        {"id": "criteria", "label": "Criteria", "type": "artefact",
         "note": "Written by Domain in glossary terms, one set per ticket. One writer."},
        {"id": "batches", "label": "Batches", "type": "artefact",
         "note": ("Ticket groups formed by Architect on collision judgement. Complete "
                  "feature sets, immutable once formed: priority moves them whole, and "
                  "only a scope change may recompose one. One worktree and one PR per "
                  "batch, tracing to exactly one approved item.")},
    ]
    bx, by = layout.pop("backlog", {"x": 980, "y": 230}).values()
    layout["tickets"] = {"x": bx - 60, "y": by}
    layout["criteria"] = {"x": bx + 90, "y": by - 60}
    layout["batches"] = {"x": bx + 90, "y": by + 60}

    # refs are structural relations between artefacts, not role access; they map
    # by the *other* endpoint rather than by verb.
    REFS_FROM_BACKLOG = {"problem": "tickets", "glossary": "criteria", "model": "batches"}
    REFS_TO_BACKLOG = {"code": "batches", "verdicts": "criteria",
                       "schedule": "batches", "tests": "criteria"}

    remapped = []
    for e in edges:
        if e["type"] == "refs":
            if e["s"] == "backlog":
                e = {**e, "s": REFS_FROM_BACKLOG.get(e["t"], "tickets")}
            elif e["t"] == "backlog":
                e = {**e, "t": REFS_TO_BACKLOG.get(e["s"], "criteria")}
        elif e["t"] == "backlog":
            key = (e["s"], e["type"], e.get("v", ""))
            target = BACKLOG_SPLIT.get(key)
            if target is None:
                raise SystemExit(f"unmapped backlog edge: {key} ({e})")
            e = {**e, "t": target}
        remapped.append(e)
    edges = remapped

    # ---- 4. two read edges the oracle proved missing -------------------------
    # Running the contact check with the split backlog left exactly four
    # underivable message edges (developer->vision, tester->vision,
    # vision->developer, critic->developer). All four resolve to omissions in the
    # original graph rather than needing exceptions:
    #
    #   * Developer and Tester read criteria but not the *ticket* those criteria
    #     serve. The original edge's noun was "batch of tickets + criteria" — the
    #     tickets half had no edge of its own. Without it, Dev1 is impossible:
    #     a role cannot recognise a criterion as a *scope gap* if it cannot see
    #     the scope.
    #   * Developer could not read the verdict against its own batch, so a failed
    #     review had no way to reach it.
    edges += [
        {"s": "developer", "t": "tickets", "type": "reads", "v": "load",
         "n": "tickets for batch", "a": "batch",
         "label": "criteria are meaningless without the ticket they serve"},
        {"s": "tester", "t": "tickets", "type": "reads", "v": "load",
         "n": "tickets for batch", "a": "batch"},
        {"s": "developer", "t": "verdicts", "type": "reads", "v": "load",
         "n": "verdict for own batch", "a": "batch"},

        # ---- 5. two more the implementation check proved missing -------------
        # Architect had no way to record a survey, yet survey records are what
        # starve constraint zero — the mechanism the whole onboarding story rests
        # on had no edge. And its scan reached tickets but not criteria, though
        # collision judgement needs both.
        {"s": "architect", "t": "model", "type": "writes", "v": "survey",
         "n": "survey record + citations", "a": "single",
         "label": "citations validated against the index"},
        {"s": "architect", "t": "criteria", "type": "reads", "v": "scan",
         "n": "criteria", "a": "index"},

        # ---- 6. reply paths -------------------------------------------------
        # Auditing ask-vs-reply found eleven ask edges and almost no reply edges:
        # the design specified asking thoroughly and never drew the answering
        # half. Most are fine, because the answer *is* a write and the cascade
        # carries it — Architect resolves an escalation by amending the model,
        # Vision resolves a challenge by amending an item, and the receipt wakes
        # the asker.
        #
        # The rule: **an ask needs a reply edge exactly when answering it writes
        # nothing.** D3 is explicit that answering a term question is not
        # amending the glossary — so it produces no receipt, so no cascade, so
        # without an edge the answer has nowhere to go and the asker waits
        # forever on a question that was in fact answered.
        {"s": "domain", "t": "developer", "type": "messages", "v": "answer",
         "n": "term sense", "a": "single", "label": "answering is not amending"},
        {"s": "vision", "t": "developer", "type": "messages", "v": "answer",
         "n": "criterion or scope clarification", "a": "single"},
        {"s": "architect", "t": "developer", "type": "messages", "v": "answer",
         "n": "constraint clarification", "a": "single"},
        {"s": "domain", "t": "tester", "type": "messages", "v": "answer",
         "n": "term sense", "a": "single"},
        {"s": "vision", "t": "tester", "type": "messages", "v": "answer",
         "n": "criterion clarification", "a": "single"},
        {"s": "tester", "t": "developer", "type": "messages", "v": "answer",
         "n": "test intent", "a": "single"},
    ]

    # ---- 3. mark fact artefacts --------------------------------------------
    for n in nodes:
        if n["id"] in FACT_ARTEFACTS:
            n["contact"] = False
            n["contact_why"] = FACT_ARTEFACTS[n["id"]]

    graph["nodes"], graph["edges"] = nodes, edges
    graph["contact_exceptions"] = EXCEPTIONS

    GRAPH.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    LAYOUT.write_text(json.dumps(layout, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"nodes={len(nodes)} edges={len(edges)} exceptions={len(EXCEPTIONS)}")
    print("artefacts:", sorted(n["id"] for n in nodes if n["type"] == "artefact"))


if __name__ == "__main__":
    main()
