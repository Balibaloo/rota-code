"""
Third amendment: the edges the onboarding phases need.

Onboarding became three phases -- orient, define, survey -- and each is written
with the previous phase's artefact in front of it. That is four read edges the
graph did not have, because the per-area survey never handed one role's output
to another:

    vision_keeper    reads code     front     the program's front, for the orientation
    terminologist reads problem  baseline  the observed account, whole, for defining
    architect     reads problem  baseline  the same, for the counterfactual
    architect     reads code     area      source, not a grain list, for a constraint

Law 3 is unchanged by any of them. `code` is a fact artefact and generates no
contact. `problem` is a judgement artefact written by Vision Keeper, so reading it
derives a contact to Vision Keeper for Terminologist and for Architect -- and both
already hold one (`challenge`, and for Architect `propose` as well), so the
declared set still equals the derived set and `check_contacts` stays green.

A script rather than a hand edit, like the two before it, so the change set is
reviewable as code and survives a re-extraction.

    python -m rota.tools.amend_graph3
"""
from __future__ import annotations

import json

from .. import paths

GRAPH = paths.DESIGN / "graph.json"

EDGES = [
    {"s": "vision_keeper", "t": "code", "type": "reads", "v": "front",
     "n": "the program's front: manifest, README, authoring surface, entry point",
     "actor": "role", "rows": "query", "depth": "body",
     "label": "orientation: what a person opening the repository reads first, "
              "and no area ever showed together"},
    {"s": "terminologist", "t": "problem", "type": "reads", "v": "baseline",
     "n": "what the program does, as observed",
     "actor": "role", "rows": "query", "depth": "body",
     "label": "the account of the program is the one context that displaces "
              "the everyday reading of a word"},
    {"s": "architect", "t": "problem", "type": "reads", "v": "baseline",
     "n": "what the program does, as observed",
     "actor": "role", "rows": "query", "depth": "body",
     "label": "a commitment is to someone outside; the account says who uses this"},
    {"s": "architect", "t": "code", "type": "reads", "v": "area",
     "n": "the area's source",
     "actor": "role", "rows": "query", "depth": "body",
     "label": "a constraint is found in source, not composed from a grain list"},
]


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    have = {(e["s"], e["t"], e["type"], e.get("v", "")) for e in graph["edges"]}
    added = 0
    for edge in EDGES:
        key = (edge["s"], edge["t"], edge["type"], edge["v"])
        if key in have:
            continue
        graph["edges"].append(edge)
        added += 1
    GRAPH.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")
    print(f"{added} edge(s) added, {len(graph['edges'])} total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
