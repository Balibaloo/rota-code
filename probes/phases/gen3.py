"""
Generation three: combine the mechanisms that each won something, rather than
pick a winner.

  from D  a maintainer's questions, which force "where does this live"
  from I  the *authoring surface* -- what a user writes -- which is the side
          every sense in the answer key is written from
  from H  a falsification pass, which is what produced the only naming of
          `TemplateVariableType`'s members in twenty attempts

  J  surface + questions + challenge

The one thing deliberately left out is the checker as a gate: it rejects correct
entries (item 22). The challenge here rewrites rather than refuses.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import harness as h

DEFINE = ("You own one word of a project's glossary. You are woken once, act, and end.\n\n"
 "Finish this sentence and write nothing else:\n\n    In this project, {a} {t} is ...\n\n"
 "It is a thing in the code, not the program itself and not the user's goal. "
 "Say what kind of thing it is, where a user or the code writes it down, and what "
 "it is for. Name the exact key or type if there is one. Thirty words at most.")


def pipeline_j(conn):
    surface = (h.OUT / "I_user_surface" / "surface.md").read_text(encoding="utf-8")
    answers = (h.OUT / "D_question_first" / "answers.md").read_text(encoding="utf-8")
    lines = []
    for t in h.REQUIRED:
        art = "an" if t[0] in "aeiou" else "a"
        con = h.concordance(conn, t)
        ctx = (f"[what a user writes in their own note]\n{surface}\n\n"
               f"[what a maintainer needed to know]\n{answers}\n\n"
               f"[concordance]\n{con}")
        first = h.ask(DEFINE.format(a=art, t=t.replace("_", " ")), ctx)
        attack = h.ask(
            "You are trying to prove one sentence wrong using the code below. You "
            "are woken once, act, and end.\n\nName the single most important thing "
            "it gets wrong or leaves out, in one sentence, quoting the line that "
            "shows it. Prefer objections about *what the thing is for* over "
            "objections about where it lives. If it is right, say RIGHT.",
            f"sentence: {first}\n\n[code]\n{con}")
        final = h.ask(
            DEFINE.format(a=art, t=t.replace("_", " ")) +
            "\n\nA reader has objected to your first attempt. Take it seriously "
            "where the code supports it.",
            f"[your first attempt]\n{first}\n\n[objection]\n{attack}\n\n{ctx}")
        lines.append(f"### {t}\n{' '.join(final.split())}\n")
        print(f"    {t}")
    h.write("J_combined", "glossary.md", "\n".join(lines))
