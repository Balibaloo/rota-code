"""
Candidate phase structures. Each builds understanding a different way and ends
with the same deliverable -- a definition of every required term -- so the
outputs can be read side by side.

    A  per-area          what rota does today: define a word from the area it
                         appears in, with no picture of the program
    B  account-first     one whole-repo account, then define each word from it
    C  bottom-up         one line per file, the union standing in for an account
    D  question-first    ask what a maintainer needs to know, answer that, then
                         define from the answers
    E  spiral            account, define, re-account using the definitions,
                         define again

The definition step is held identical everywhere except D, whose whole point is
that the question is different. What varies is the context the phases built.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import harness as h

DEFINE_SYS = (
    "You own one word of a project's glossary. You are woken once, act, and end.\n\n"
    "Finish this sentence and write nothing else:\n\n    In this project, {article} "
    "{term} is ...\n\n"
    "Say what kind of thing it is, where it is written down, and what it is for. "
    "Thirty words at most.")


def define_all(conn, pipeline, context, label="understanding"):
    lines = []
    for t in h.REQUIRED:
        art = "an" if t[0] in "aeiou" else "a"
        sysp = DEFINE_SYS.format(article=art, term=t.replace("_", " "))
        user = f"[{label}]\n{context}\n\n[concordance]\n{h.concordance(conn, t)}"
        lines.append(f"### {t}\n{h.ask(sysp, user)}\n")
        print(f"    {t}")
    h.write(pipeline, "glossary.md", "\n".join(lines))


# ------------------------------------------------------------------- A ------

def pipeline_a(conn):
    """Today: the word defined from the area it lives in. No program picture."""
    areas = h.areas(conn)
    per_area = []
    for area, fs in sorted(areas.items()):
        body = "\n\n".join(f"[{f}]\n{h.source(f, 1800)}" for f in fs[:3])
        if not body.strip():
            continue
        acct = h.ask(
            "You are surveying one area of a codebase. You are woken once, act, "
            "and end.\n\nIn two or three sentences, say what this area does and "
            "what it calls the things it works with. Nothing else.",
            f"area: {area}\n\n{body}")
        per_area.append(f"### {area}\n{acct}\n")
        print(f"    area {area}")
    h.write("A_per_area", "areas.md", "\n".join(per_area))
    define_all(conn, "A_per_area", "\n".join(per_area), "area accounts")


# ------------------------------------------------------------------- B ------

def pipeline_b(conn):
    """Account first: one whole-repo pass, from the declared entry point."""
    eps = h.entry_points(conn)
    decls = sorted({r["grain"] for r in conn.execute(
        "SELECT grain FROM code_index WHERE grain LIKE '%::%'")})
    schema = h.source("intentsSchema.yaml", 1500)
    manifest = h.source("manifest.json", 600)
    acct = h.ask(
        "You are reading one small program to say how it works.\n\nYou are woken "
        "once, act, and end.\n\nBelow are its declared entry point, its manifest, "
        "its schema, and every symbol its index holds. Write four or five "
        "sentences saying what this program does for its user, and how the pieces "
        "reach each other: what is read first, what it turns into, what comes "
        "out. Name things by the names the code gives them. No lists.",
        f"[entry point: {eps[0]}]\n{h.source(eps[0], 3000)}\n\n"
        f"[manifest.json]\n{manifest}\n\n[intentsSchema.yaml]\n{schema}\n\n"
        f"[symbols]\n{', '.join(decls[:70])}")
    h.write("B_account_first", "account.md", acct)
    define_all(conn, "B_account_first", acct, "what the program does")


# ------------------------------------------------------------------- C ------

def pipeline_c(conn):
    """Bottom-up: one line per file, their union standing in for an account.
    Tests whether the picture must be top-down -- which matters when no entry
    point is declared."""
    lines = []
    for f in h.files(conn):
        body = h.source(f, 2000)
        if not body.strip():
            continue
        one = h.ask(
            "You are reading one file. You are woken once, act, and end.\n\n"
            "One sentence: what is this file for, in this program? Name the "
            "things it works with by the names the code gives them. Nothing else.",
            f"[{f}]\n{body}")
        lines.append(f"- {f}: {one}")
        print(f"    {f}")
    digest = "\n".join(lines)
    h.write("C_bottom_up", "files.md", digest)
    define_all(conn, "C_bottom_up", digest, "what each file is for")


# ------------------------------------------------------------------- D ------

def pipeline_d(conn):
    """Question-first: decompose by what a maintainer needs to know, not by
    artefact or directory. The only candidate whose unit of work is a question."""
    eps = h.entry_points(conn)
    seed = (f"[entry point: {eps[0]}]\n{h.source(eps[0], 2500)}\n\n"
            f"[manifest.json]\n{h.source('manifest.json', 600)}\n\n"
            f"[files]\n{', '.join(h.files(conn))}")
    qs = h.ask(
        "You are about to maintain a program you have never seen. You are woken "
        "once, act, and end.\n\nWrite the five questions you would need answered "
        "before you could change it safely. One per line, numbered, nothing else. "
        "Questions about what it does and what its parts are -- not about tests, "
        "builds or style.",
        seed)
    h.write("D_question_first", "questions.md", qs)
    print("    questions asked")

    answers = []
    for q in [l for l in qs.splitlines() if l.strip() and l.strip()[0].isdigit()][:5]:
        term = " ".join(w for w in h._words_in(q))[:40] or "intent"
        con = h.concordance(conn, q.split()[1] if len(q.split()) > 1 else "intent")
        a = h.ask(
            "You are answering one question about a program by reading it. You "
            "are woken once, act, and end.\n\nThree sentences at most, from the "
            "code below. If the code does not answer it, say so. Nothing else.",
            f"question: {q}\n\n[entry point]\n{h.source(eps[0], 2000)}\n\n"
            f"[concordance]\n{con[:2500]}")
        answers.append(f"### {q}\n{a}\n")
        print(f"    answered {q[:48]}")
    body = "\n".join(answers)
    h.write("D_question_first", "answers.md", body)
    define_all(conn, "D_question_first", body, "what a maintainer needed to know")


# ------------------------------------------------------------------- E ------

def pipeline_e(conn):
    """Spiral: account, define, re-account knowing the terms, define again.
    Tests whether a second pass adds anything a first cannot."""
    acct = (h.OUT / "B_account_first" / "account.md").read_text(encoding="utf-8")
    first = (h.OUT / "B_account_first" / "glossary.md").read_text(encoding="utf-8")
    acct2 = h.ask(
        "You are re-reading an account of a program now that its words have been "
        "defined. You are woken once, act, and end.\n\nRewrite the account in "
        "four or five sentences, using the defined words precisely and correcting "
        "anything the definitions show was wrong. Nothing else.",
        f"[first account]\n{acct}\n\n[definitions]\n{first}")
    h.write("E_spiral", "account2.md", acct2)
    define_all(conn, "E_spiral", acct2, "what the program does")
