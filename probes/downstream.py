"""
The downstream probe: can a cold role act on the repository from the artefacts
alone?

`ONBOARDING.md` states the goal as a test rather than an inventory -- "a
Developer who has read only the glossary writes the right thing" -- and the
answer key asks it in prose and never measures it. This is the measurement, at
probe grain: one model call per question, the run's artefacts as the whole
context, no code, no README. Scored by reading, against the answers a person
who knows the repository would give.

    python probes/downstream.py .rota/cnt_final.db
    python probes/downstream.py .rota/cnt_final.db --model llama3.1:8b

Deliberately not a session: the question is whether the *artefacts* carry the
understanding, and a session's tools would let the role go and read the code,
which is what onboarding exists to make unnecessary.
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rota.llm.llm import Pins, default_backend  # noqa: E402

# Questions a Developer or Tester would have to answer correctly before
# touching cnt, each with the answer the repository gives. Written from the
# answer key, before any run was probed.
QUESTIONS = [
    ("A user wants the plugin to create a note from a recipe. Where, exactly, "
     "do they write that recipe -- in which file, under which key?",
     "in a note's own frontmatter, under `intents_to`"),
    ("An intent declares a prompt with `of_type: note`. When the intent runs, "
     "what is the user asked for, and what answers it?",
     "a note from the vault, chosen through the filtered-opener plugin "
     "(narrowed by a filter set); not free text"),
    ("Which five kinds of prompt can an intent ask for?",
     "text, number, natural_date, note, folder"),
    ("A maintainer renames the frontmatter key `with_templates` to `templates` "
     "throughout the code and the build passes. Who is affected, and how do "
     "they find out?",
     "every user whose notes use `with_templates`; validateFmSchema lists the "
     "unrecognized property in a console warning, and a user-facing Notice "
     "fires only for four legacy key names -- with_templates is not one, so "
     "in the UI their templates are simply gone"),
    ("What is a 'template' here -- a string with placeholders, a class, or "
     "something else?",
     "a note whose contents seed the new note, named by an intent (at_path); "
     "it can override the intent's name, folder and prompts"),
    ("What is the difference between a global intent and one read from the "
     "active note?",
     "a global intent is loaded from the note at `globalIntentsNotePath` and "
     "is available everywhere; a local one is read from the note you are on"),
    # Asked in the code's own words, not the README's: without prose, "prompt"
    # is this plugin's modal class and the five kinds are the variable types.
    # A reader that lists them here but not above has read the code and not
    # the README, which for a no-prose run is the point.
    ("Which kinds of template variable can an intent declare, and where is "
     "the set of kinds declared?",
     "text, number, natural_date, note, folder -- the TemplateVariableType enum "
     "in src/variables/providers/index.ts"),
    ("What does a `provider` do in this codebase?",
     "one module per prompt type: a frontmatter parser and a value getter, "
     "registered in two lookup tables keyed by TemplateVariableType"),
]


def artefacts(conn: sqlite3.Connection) -> str:
    out = ["[what the program does -- observed items]"]
    for r in conn.execute("SELECT id, text FROM items ORDER BY id"):
        out.append(f"- {r['text']}")
    out.append("\n[glossary]")
    for r in conn.execute(
            "SELECT term, sense_short, sense_body FROM glossary_terms "
            "WHERE superseded_by IS NULL ORDER BY term"):
        out.append(f"- {r['term']}: {r['sense_short']}"
                   + (f" -- {r['sense_body']}" if r['sense_body'] else ""))
    try:
        rows = list(conn.execute(
            "SELECT id AS area, account FROM model_areas ORDER BY id"))
    except sqlite3.OperationalError:
        rows = []
    if rows:
        out.append("\n[what each area is for -- the model's accounts]")
        for r in rows:
            out.append(f"- {r['area']}: {r['account']}")
    out.append("\n[constraints -- commitments to things outside the repository]")
    for r in conn.execute("SELECT headline, text FROM constraints WHERE id != 'k0' ORDER BY id"):
        out.append(f"- {r['headline']}: {r['text'] or ''}")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("db")
    ap.add_argument("--model", default="llama3.1:8b")
    ap.add_argument("--num-ctx", type=int, default=12288,
        help="reader context window; the artefact dump grows with the writer")
    args = ap.parse_args(argv)
    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    context = artefacts(conn)
    backend, pins = default_backend(), Pins(model=args.model, temperature=0.0,
                                            num_ctx=args.num_ctx)
    system = ("You are a developer joining a project you have never seen. You "
              "have exactly the notes below and nothing else -- no code, no "
              "README. Answer the question from the notes in two sentences at "
              "most. If the notes do not say, say 'the notes do not say' and "
              "stop; do not guess from the ordinary meaning of the words.")
    print(f"=== {args.db}  ({len(context)} chars of artefacts)\n")
    for q, want in QUESTIONS:
        got = backend.complete(system, f"{context}\n\n[question]\n{q}", pins).text.strip()
        print(f"Q: {q}\n   expected: {want}\n   got:      {' '.join(got.split())[:400]}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
