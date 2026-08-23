"""
Prompt composition.

A role's instructions are a **base** (who it is, standing law) plus a **piece**
selected by what woke it. Liaison has the most pieces because it has the most
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

from .. import paths

PROMPT_DIR = paths.PROMPTS


class MissingPrompt(FileNotFoundError):
    pass


@lru_cache(maxsize=128)
def _read(path: Path) -> str:
    if not path.exists():
        raise MissingPrompt(str(path))
    return path.read_text(encoding="utf-8").strip()


def _variant(role: str) -> Path:
    """
    The prompt directory for this role, or a variant of it under A/B.

    `ROTA_PROMPTS=vocab` reads `<role>/vocab/` where a file exists there and
    falls back to `<role>/` where it does not, so a variant is only the files it
    actually changes. A subdirectory rather than a `survey_vocab.md` beside the
    original, because `available()` globs `*.md` to enumerate a role's modes and
    a variant is not a mode.

    Debug only, and one direction: a variant can replace a brief, never widen a
    role -- `mode_tools` still narrows what the graph granted and nothing here
    touches the graph.
    """
    import os

    name = (os.environ.get("ROTA_PROMPTS") or "").strip()
    return PROMPT_DIR / role / name if name else PROMPT_DIR / role


def _pick(role: str, filename: str) -> Path:
    """The variant's file if it has one, otherwise the role's own."""
    cand = _variant(role) / filename
    return cand if cand.exists() else PROMPT_DIR / role / filename


def base(role: str, verb: str = "") -> str:
    """
    Who the role is, for this mode.

    A mode may declare its own base in `<mode>.base.md`, and the onboarding
    modes do: the default base carries a role's standing doctrine for the
    delivery loop -- criteria, tickets, what it may never decide -- and a
    session woken to define one word of a program it has never seen needs
    none of it. Measured: the brief is what carries the recall, and the
    forty-five-line base was most of what the brief was.
    """
    if verb:
        own = _pick(role, f"{verb}.base.md")
        if own.exists():
            return _read(own)
    return _read(_pick(role, "base.md"))


def piece(role: str, verb: str) -> str:
    """The mode-specific instructions, or empty if the role has no piece for it."""
    try:
        return _read(_pick(role, f"{verb}.md"))
    except MissingPrompt:
        return ""


def compose(role: str, verb: str = "") -> str:
    """base + piece(verb). The piece is what makes the session's job specific."""
    parts = [base(role, verb)]
    extra = piece(role, verb) if verb else ""
    if extra:
        parts.append(extra)
    return "\n\n".join(parts)


def mode_tools(role: str, mode: str) -> list[str] | None:
    """
    The functions a mode narrows to, or None for "everything the role has".

    **The graph grants the ceiling; a mode can only narrow it.** That direction
    matters: a mode file cannot widen a role's power, so the graph stays the sole
    authority over what exists, and mode scoping is purely about not putting
    eleven functions in front of a model whose job needs four.

    This came from watching Liaison, in ratification mode, open with
    `ledger.list()` and wander until it ran out of turns. It had every function
    its role owns when it needed three.
    """
    path = _pick(role, f"{mode}.tools")
    if not path.exists():
        return None
    return [line.strip() for line in _read(path).splitlines()
            if line.strip() and not line.startswith("#")]


def available(role: str) -> list[str]:
    d = PROMPT_DIR / role
    if not d.exists():
        return []
    return sorted(p.stem for p in d.glob("*.md")
                  if p.stem != "base" and not p.stem.endswith(".base"))


def check_coverage() -> list[str]:
    """
    Every role in the graph needs a base; every inbound verb wants a piece.

    Missing pieces are reported, not fatal — a role can run on its base alone,
    and forcing a file per verb before the verb is exercised would be ceremony.
    """
    from ..design import graph as graph_mod

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
    from ..design import graph as graph_mod

    g = graph_mod.load()
    return {e.v for e in g.of_type("messages") if e.t == role}
