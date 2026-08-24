"""Consult-mode probe: the maintainer's questions, routed instead of dumped.

`downstream.py` hands one reader everything -- items, glossary, model -- and
at ~24k characters the reader answers what sits late in the dump and says
"the notes do not say" to the rest, at 12k and at 16k context alike. The
original design answers a question the other way: read-only sessions, one per
owner, each with *its own artefact* in front of it -- "Vision answers what was
promised, Domain what the terms mean, Architect what the index actually does"
-- and nothing else.

This probe measures exactly that split, with the same reader and the same
questions. The glossary is consulted the way its owner would consult it: the
index of short senses whole (a page), and full bodies only for the terms the
question's words name -- `glossary.lookup`, mechanically. An owner whose
artefact does not carry the answer says so and is dropped; what remains,
labelled, is the reply. No writes anywhere; this is the measurement for
validation 2 before the wiring.

    python probes/consult.py .rota/<run>.db [--model qwen2.5:14b]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from probes.downstream import QUESTIONS, default_backend  # noqa: E402
from rota.llm.llm import Pins  # noqa: E402


def _rows(conn, sql):
    try:
        return list(conn.execute(sql))
    except sqlite3.OperationalError:
        return []


def fixed_sections(conn) -> dict[str, str]:
    vision = ["[what the program does -- the Vision Keeper's observed items]"]
    for r in _rows(conn, "SELECT id, text FROM items ORDER BY id"):
        vision.append(f"- {r['id']}: {r['text']}")

    model = ["[the model -- what each area is for]"]
    for r in _rows(conn, "SELECT id AS area, account FROM model_areas ORDER BY id"):
        model.append(f"- {r['area']}: {r['account']}")
    model.append("")
    model.append("[constraints -- commitments to things outside the repository]")
    for r in _rows(conn, "SELECT headline, text FROM constraints WHERE id != 'k0' ORDER BY id"):
        model.append(f"- {r['headline']}: {r['text']}")

    return {"vision_keeper": "\n".join(vision), "architect": "\n".join(model)}


def glossary_for(conn, question: str) -> str:
    """The Terminologist consults its artefact by lookup, not by dump.

    Measured: the full glossary was 21k of the 24k characters, and the reader
    holding `intents_to`'s definition said "not mine" to the question that
    names recipes and keys. The index of short senses is a page; bodies travel
    only for the terms the question's words touch.
    """
    rows = _rows(conn, "SELECT term, sense_short, sense_body FROM glossary_terms "
                       "WHERE superseded_by IS NULL ORDER BY term")
    qwords = set()
    for w in question.split():
        w = w.strip("`'\".,?:;()").lower()
        if len(w) >= 3:
            qwords.add(w)
            qwords.add(w.rstrip("s"))
            qwords.update(p for p in w.split("_") if len(p) >= 3)
    out = ["[the glossary's index -- every term, one line]"]
    hits = []
    for r in rows:
        tokens = {r["term"].lower()}
        tokens.update(t for t in r["term"].lower().replace("_", " ").split())
        tokens.update(t.rstrip("s") for t in set(tokens))
        out.append(f"- {r['term']}: {r['sense_short']}")
        if tokens & qwords:
            hits.append(r)
    if hits:
        out.append("")
        out.append("[the terms the question names, in full]")
        for r in hits:
            body = f" -- {r['sense_body']}" if r["sense_body"] else ""
            out.append(f"- {r['term']}: {r['sense_short']}{body}")
    return "\n".join(out)


CHARTER = {
    "vision_keeper": "You are Vision Keeper. You know what this program does for "
                     "the person using it -- behaviours, not mechanisms.",
    "terminologist": "You are Terminologist. You know what every word of this "
                     "project means, and nothing else.",
    "architect": "You are Architect. You know what each area of the code is for "
                 "and what outside things depend on it.",
}

NOT_MINE = "NOT MINE"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("--model", default="llama3.1:8b")
    ap.add_argument("--num-ctx", type=int, default=12288)
    ap.add_argument("--questions", default="probes.downstream",
                    help="dotted module exporting QUESTIONS [(q, want), ...]")
    args = ap.parse_args(argv)

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    backend = default_backend()
    pins = Pins(model=args.model, temperature=0.0, num_ctx=args.num_ctx)

    import importlib

    questions = importlib.import_module(args.questions).QUESTIONS
    fixed = fixed_sections(conn)
    print(f"=== {args.db}  (consulted by owner; the glossary by lookup; "
          f"questions from {args.questions})\n")

    for q, want in questions:
        parts = dict(fixed)
        parts["terminologist"] = glossary_for(conn, q)
        answers = []
        for role in ("vision_keeper", "terminologist", "architect"):
            artefact = parts[role]
            system = (
                f"{CHARTER[role]}\n\n"
                "A maintainer asks a question. Below is your artefact -- the "
                "whole of what you know. Answer from it in two or three "
                "sentences, quoting its words where they answer. If your "
                f"artefact does not carry the answer, reply exactly: {NOT_MINE}."
            )
            user = artefact + "\n\nThe question: " + q
            got = backend.complete(system, user, pins).text.strip()
            if got and NOT_MINE not in got[:40]:
                answers.append((role, " ".join(got.split()), len(artefact)))
        print(f"Q: {q}\n   expected: {want}")
        if not answers:
            print("   got:      (every owner: not mine)")
        for role, a, n in answers:
            print(f"   {role:>13} ({n} chars): {a[:360]}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
