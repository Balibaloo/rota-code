"""
Prompt composition.

A role's instructions are a **base** (who it is, standing law) plus a **piece**
selected by what woke it. Interface has the most pieces because it has the most
verbs; every other role has one or two.

Two properties this arrangement buys:

  * The pieces are enumerable from the graph — one per verb a role emits or
    receives — so "which modes does this role have" is answerable rather than a
    matter of reading prose.
  * Each T1 case exercises exactly one piece, which is what makes a pass-rate
    drop attributable.

Prompts carry no authority. A piece that instructs a role to do something it has
no edge for cannot succeed: the function was never built into its namespace. That
is deliberate — it means prompt text can be tuned freely without widening what a
role can do.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


class MissingPrompt(FileNotFoundError):
    pass


@lru_cache(maxsize=128)
def _read(path: Path) -> str:
    if not path.exists():
        raise MissingPrompt(str(path))
    return path.read_text(encoding="utf-8").strip()


def base(role: str) -> str:
    return _read(PROMPT_DIR / role / "base.md")


def piece(role: str, verb: str) -> str:
    """The mode-specific instructions, or empty if the role has no piece for it."""
    try:
        return _read(PROMPT_DIR / role / f"{verb}.md")
    except MissingPrompt:
        return ""


def compose(role: str, verb: str = "") -> str:
    """base + piece(verb). The piece is what makes the session's job specific."""
    parts = [base(role)]
    extra = piece(role, verb) if verb else ""
    if extra:
        parts.append(extra)
    return "\n\n".join(parts)


def available(role: str) -> list[str]:
    d = PROMPT_DIR / role
    if not d.exists():
        return []
    return sorted(p.stem for p in d.glob("*.md") if p.stem != "base")


def check_coverage() -> list[str]:
    """
    Every role in the graph needs a base; every inbound verb wants a piece.

    Missing pieces are reported, not fatal — a role can run on its base alone,
    and forcing a file per verb before the verb is exercised would be ceremony.
    """
    from . import graph as graph_mod

    g = graph_mod.load()
    problems = []
    for role in sorted(g.roles):
        try:
            base(role)
        except MissingPrompt:
            problems.append(f"{role}: no base prompt")
    return problems


def inbound_verbs(role: str) -> set[str]:
    """Verbs this role can be woken by — the enumeration of its modes."""
    from . import graph as graph_mod

    g = graph_mod.load()
    return {e.v for e in g.of_type("messages") if e.t == role}
