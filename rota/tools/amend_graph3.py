"""
Third amendment pass: `question` means one thing.

There are ten question channels. Five carry words and five do not, and which
half a channel falls in depends on the recipient: every question to the
Researcher has a `question=` field, and every question to a role inside the
project has refs and nothing else.

So a Terminologist woken by `developer -> terminologist: question` is shown
this, in full:

    {"from": "developer", "verb": "question", "refs": ["g_851c9a"],
     "resolved_refs": {"g_851c9a": {"term": "account",
                                    "sense_short": "the login identity"}}}

Developer asks you about the term "account", whose sense is "the login
identity". *What question?* There is none. The role has to invent one, answer
it, and the Developer receives an answer to something it never asked.

The justification for the Researcher's exception is real but incomplete: it
shares no database, so an id means nothing at the far end. True — and
`developer -> terminologist` shares the entire database and still cannot ask a
question, because a question is definitionally about something no artefact
holds. That is what makes it a question. Refs name the subject; they cannot
name the uncertainty.

This is an inconsistency under a law the repository already keeps rather than a
new position. One meaning per word was enforced across the whole vocabulary,
and `question` still means two things. Law 2 is untouched: conclusions travel
and reasoning stays home governs *telling*, and every pointing channel --
deliver, relay, reopen, elect, submit, verdict -- keeps refs and nothing else,
which is where prose would genuinely let a wrong conclusion outrun the row it
came from. Asking is not telling.

`challenge`, `propose` and `escalate` have the same shape and are deliberately
not touched here. They are a design decision about disputes rather than a
vocabulary inconsistency, and they are open in ROLES.md.

    python -m rota.tools.amend_graph3
"""
from __future__ import annotations

import json

from .. import paths

GRAPH = paths.DESIGN / "graph.json"

# The five that could not ask. Listed rather than derived so the change is
# reviewable as a change, and so a sixth appearing later is a diff.
WORDLESS = {
    ("architect", "terminologist"),
    ("developer", "gatekeeper"),
    ("developer", "terminologist"),
    ("tester", "gatekeeper"),
    ("tester", "terminologist"),
}


def main() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    edges = graph["edges"]

    changed = []
    for e in edges:
        if e.get("type") != "messages" or e.get("v") != "question":
            continue
        if (e["s"], e["t"]) not in WORDLESS:
            continue
        e["prose"] = "question"
        e["n"] = (e.get("n") or "a question").rstrip(".") + \
            ", in words; the refs say what it is about"
        changed.append(f"{e['s']} -> {e['t']}")

    GRAPH.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")

    every = [e for e in edges
             if e.get("type") == "messages" and e.get("v") == "question"]
    with_words = [e for e in every if e.get("prose")]
    print(f"amended {len(changed)}: {', '.join(sorted(changed))}")
    print(f"question channels: {len(with_words)}/{len(every)} carry words")
    assert len(with_words) == len(every), "question still means two things"


if __name__ == "__main__":
    main()
