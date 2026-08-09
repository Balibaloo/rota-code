"""
One name, one job — as a constraint rather than a report.

The analyser found seven words carrying two meanings each. Fixing them is worth
little if the eighth can arrive unremarked, and it would: the cost of a collision
is that nobody notices it, which is exactly why it cannot be left to noticing.
"""
from __future__ import annotations

from rota.tools import vocabulary as V


def test_no_word_carries_two_jobs():
    """
    The hard constraint.

    Composition is excluded by `collisions` itself — `verdicts` the artefact and
    `verdicts` the table are one referent reached two ways, and renaming them
    apart would make the system harder to read, not easier. What is left is
    genuine ambiguity.
    """
    found = V.collisions(V.harvest())
    assert found == [], "\n".join(
        f"{w}: {', '.join(sorted({s.split('.')[-1] for s in srcs}))}"
        for w, srcs in found)


def test_the_check_can_fail():
    """
    A lint nobody has proved can fail is a lint you are trusting rather than
    using. Inventing a word that is both an operation and a state must trip it.
    """
    terms = V.harvest()
    word = "consult"
    t = terms.setdefault(word, V.Term(word=word, level="L3"))
    t.sources = {"graph.operation", "schema.state"}

    assert any(w == word for w, _ in V.collisions(terms))


def test_composition_is_not_reported_as_collision():
    """
    The first sweep reported 17 findings, 10 of which were the system being
    consistent with itself. A check with that signal-to-noise gets ignored, and
    an ignored check is worse than none — it looks like coverage.
    """
    terms = V.harvest()
    t = V.Term(word="verdicts", level="L2")
    t.sources = {"graph.node", "schema.table"}
    terms["verdicts"] = t

    assert not any(w == "verdicts" for w, _ in V.collisions(terms))


def test_the_seven_split_senses_stay_split():
    """
    Named individually so a regression says which one came back, and what it
    collided with. The reach values `index` and `batch` deliberately survive —
    only the operations moved.
    """
    terms = V.harvest()
    for word in ("consult", "brief", "index", "batch", "scope", "entry", "amend"):
        t = terms.get(word)
        if t is None:
            continue
        kinds = {s.split(".")[-1] for s in t.sources
                 if s.split(".")[0] in ("graph", "schema")}
        assert len(kinds) <= 1 or frozenset(kinds) in V.COMPOSITION, \
            f"{word!r} carries {sorted(kinds)} again"


def test_the_new_names_are_actually_in_use():
    """
    A rename that only deletes the old word leaves a system with a hole in it.
    Each replacement must appear where the original did.
    """
    terms = V.harvest()
    for word, where in (("ask", "graph.verb"), ("deliver", "graph.verb"),
                        ("group", "graph.operation"), ("list", "graph.operation"),
                        ("revise", None)):
        assert word in terms, f"{word!r} was agreed but appears nowhere"
        if where:
            assert where in terms[word].sources, \
                f"{word!r} exists but not as {where}: {sorted(terms[word].sources)}"


# ---------------------------------------------------------------------------
# L0 — the level every other source presupposed and none stated
# ---------------------------------------------------------------------------

def test_every_l0_term_is_actually_defined_somewhere():
    """
    The top level is *declared* in the tool rather than harvested, because there
    was no source to harvest it from — which is exactly the problem. Now there
    is one, and a declared term with no prose behind it is a term nobody has had
    to mean anything by.
    """
    import pathlib

    laws = (pathlib.Path(V.ROTA) / "LAWS.md").read_text(encoding="utf-8").lower()
    missing = [t for t in V.L0_TERMS if t not in laws]
    assert not missing, f"declared at L0 but never stated: {missing}"


def test_the_laws_name_every_role():
    import pathlib

    from rota import graph as graph_mod

    laws = (pathlib.Path(V.ROTA) / "LAWS.md").read_text(encoding="utf-8").lower()
    missing = [r for r in graph_mod.load().roles if r not in laws]
    assert not missing, f"a role the laws never mention: {missing}"


def test_the_laws_carry_no_legacy_names():
    """
    The document the prompts hang from is the last place a stale name can hide,
    because it is the one nobody re-reads once it looks finished.
    """
    import pathlib
    import re

    laws = (pathlib.Path(V.ROTA) / "LAWS.md").read_text(encoding="utf-8")
    found = re.findall(r"\b(client|interface|vision|domain|utterance|non_goal)\b",
                       laws, re.I)
    assert not found, f"legacy vocabulary in LAWS.md: {sorted(set(found))}"
