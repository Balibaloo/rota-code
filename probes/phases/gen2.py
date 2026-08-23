"""
Generation two. What generation one established:

  * question-first (D) was the only structure with no *poor* answer -- a
    maintainer's question forces "where does this live" to be answered, and no
    artefact-shaped or area-shaped phase ever asks it
  * the spiral (E) removed wrongness and added no insight
  * nobody got `variable`, `variable_type` or `filter_set`, because every
    pipeline *sampled lines* from the file that decides instead of opening it
  * every failure describes code structure where the key describes product
    meaning: "a recipe for making a note", "a value asked of the user"

So:

  F  declaring-file   D's questions, and the define step opens the file that
                      declares the word rather than citing lines from it
  H  challenge        define, try to falsify it against the code, redefine
  I  user-surface     approach from what a *user writes*. `intentsSchema.yaml`
                      is the authoring surface -- the thing users type into
                      their own notes -- and every sense in the answer key is
                      written from that side
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import harness as h

DEFINE = ("You own one word of a project's glossary. You are woken once, act, and end.\n\n"
 "Finish this sentence and write nothing else:\n\n    In this project, {a} {t} is ...\n\n"
 "It is a thing in the code, not the program itself and not the user's goal. "
 "Say what kind of thing it is, where it is written down, and what it is for. "
 "Thirty words at most.")


def declaring_file(conn, term: str) -> tuple[str, str]:
    """The file that declares the word, opened whole. Not lines about it."""
    con = h.concordance(conn, term)
    for line in con.splitlines():
        m = re.match(r"\s+(\S+?):(\d+)\s", line)
        if m and "declared" not in line:
            rel = m.group(1)
            if (h.ROOT / rel).is_file():
                return rel, h.source(rel, 3200)
    return "", ""


def pipeline_f(conn):
    answers = (h.OUT / "D_question_first" / "answers.md").read_text(encoding="utf-8")
    lines = []
    for t in h.REQUIRED:
        rel, body = declaring_file(conn, t)
        art = "an" if t[0] in "aeiou" else "a"
        user = (f"[what a maintainer needed to know]\n{answers}\n\n"
                f"[{rel or 'no declaring file'}]\n{body}\n\n"
                f"[concordance]\n{h.concordance(conn, t)[:1400]}")
        lines.append(f"### {t}  (opened {rel})\n"
                     f"{' '.join(h.ask(DEFINE.format(a=art, t=t.replace('_',' ')), user).split())}\n")
        print(f"    {t}  <- {rel}")
    h.write("F_declaring_file", "glossary.md", "\n".join(lines))


def pipeline_h(conn):
    """Define, falsify, redefine. Per term, not per account."""
    base = (h.OUT / "D_question_first" / "answers.md").read_text(encoding="utf-8")
    lines = []
    for t in h.REQUIRED:
        art = "an" if t[0] in "aeiou" else "a"
        con = h.concordance(conn, t)
        first = h.ask(DEFINE.format(a=art, t=t.replace("_", " ")),
                      f"[understanding]\n{base}\n\n[concordance]\n{con}")
        attack = h.ask(
            "You are trying to prove one sentence wrong using the code below. "
            "You are woken once, act, and end.\n\nName the single most important "
            "thing it gets wrong or leaves out, in one sentence, quoting the line "
            "that shows it. If it is right, say RIGHT. Nothing else.",
            f"sentence: {first}\n\n[code]\n{con}")
        final = h.ask(
            DEFINE.format(a=art, t=t.replace("_", " ")) +
            "\n\nA reader has objected to your first attempt. Take the objection "
            "seriously if the code supports it.",
            f"[your first attempt]\n{first}\n\n[objection]\n{attack}\n\n"
            f"[concordance]\n{con}")
        lines.append(f"### {t}\nfirst: {' '.join(first.split())}\n"
                     f"objection: {' '.join(attack.split())[:200]}\n"
                     f"final: {' '.join(final.split())}\n")
        print(f"    {t}")
    h.write("H_challenge", "glossary.md", "\n".join(lines))


def pipeline_i(conn):
    """From the authoring surface: what does a *user* write, and what happens."""
    schema = h.source("intentsSchema.yaml", 2500)
    surface = h.ask(
        "You are reading the file that defines what a user is allowed to write, "
        "in their own notes, to drive this program. You are woken once, act, and "
        "end.\n\nExplain in five sentences what a user writes and what the "
        "program does with each part of it. Use the key names exactly as they "
        "appear. No lists.",
        f"[intentsSchema.yaml -- the authoring surface]\n{schema}\n\n"
        f"[manifest.json]\n{h.source('manifest.json', 500)}")
    h.write("I_user_surface", "surface.md", surface)
    lines = []
    for t in h.REQUIRED:
        art = "an" if t[0] in "aeiou" else "a"
        user = (f"[what a user writes, and what happens to it]\n{surface}\n\n"
                f"[concordance]\n{h.concordance(conn, t)}")
        lines.append(f"### {t}\n"
                     f"{' '.join(h.ask(DEFINE.format(a=art, t=t.replace('_',' ')), user).split())}\n")
        print(f"    {t}")
    h.write("I_user_surface", "glossary.md", "\n".join(lines))
