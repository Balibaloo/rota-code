"""
Reach was two questions wearing one name.

Every edge carried an `a:` — a single word meant to say how much of the target it
touches. Eight values, one axis. But six of them answer *which rows* and two
answer *how much of each row*, and squashing those together is why `full` and
`index` both existed while returning the same thing:

    problem.consult()   "Full scope = the full index."   <- its own docstring

`full` never meant full text. It meant *every row, headline only, and you own
this artefact* — three claims in one word, of which the last is not about reach
at all. So:

    rows:   none | single | batch | window | delta | query | all
    depth:  index | body

`full` disappears. What it was really carrying was authority, which is now a
rule stated once rather than a value repeated on eight edges.

`depth` is only meaningful on read edges. A message carries refs, never bodies —
that is a law, not a setting — and a write's depth is whatever the writer wrote.
Putting a field on those edges to hold a constant would be inventing data.

Run once, from the repo root:

    python -m rota.tools.split_reach
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

GRAPH = Path("rota/design/graph.json")

# Which rows, for every edge.
ROWS = {
    "none": "none", "single": "single", "batch": "batch",
    "window": "window", "delta": "delta", "query": "query",
    "index": "all",      # the whole index is still the whole artefact
    "full": "all",
}

# How much of each row, for read edges. Taken from what the operation actually
# returns, not from what the old adjective implied:
#
#   scan / list / consult   ids and a headline        -> index
#   search / probe / survey matches, not prose        -> index
#   quote / source          the thing itself, verbatim -> body
#   load / lookup           the rows, in full          -> body
DEPTH_BY_VERB = {
    "list": "index", "scan": "index", "consult": "index",
    "search": "index", "probe": "index", "survey": "index",
    "quote": "body", "source": "body",
    "load": "body", "lookup": "body", "read": "body", "diff": "body",
}


def main() -> None:
    g = json.loads(GRAPH.read_text(encoding="utf-8"))

    unknown_verbs, converted = set(), 0
    for e in g["edges"]:
        old = e.pop("a", None)
        if old is None:
            continue
        if old not in ROWS:
            raise SystemExit(f"unmapped reach {old!r} on {e['s']} -> {e['t']}")

        e["rows"] = ROWS[old]
        if e["type"] == "reads":
            verb = e.get("v", "")
            if verb not in DEPTH_BY_VERB:
                unknown_verbs.add(verb)
            e["depth"] = DEPTH_BY_VERB.get(verb, "index")
        converted += 1

    GRAPH.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")
    print(f"{converted} edges converted")
    if unknown_verbs:
        print(f"defaulted to depth=index for unrecognised verbs: "
              f"{sorted(unknown_verbs)}")

    rows_all = [e for e in g["edges"]
                if e["type"] == "reads" and e.get("rows") == "all"]
    body = [e for e in rows_all if e.get("depth") == "body"]
    print(f"\n{len(rows_all)} reads take every row; {len(body)} of those at body "
          f"depth (each must be an owner read)")


if __name__ == "__main__":
    sys.exit(main())
