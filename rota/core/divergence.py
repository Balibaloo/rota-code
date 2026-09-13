"""
Detected divergence: where the material underdetermined the output.

The assumptions ruling (2026-08-30). Asking a session to enumerate its
assumptions fails because an assumption is invisible to its assumer -- one
ledger row in 134 production-model sessions is the measurement. So the trail
stops asking for introspection and detects instead: the points where a
session *chose* something its material never fixed. The claim weakens
honestly, from "every assumption a sentence" to "every detected divergence a
sentence" -- mechanical, auditable, and true.

Detector one: invented literals in tests. A test's fixture values --
`register('u1', 'A@B.co')`, `limit=72` -- are choices. Each literal that
appears nowhere in the criterion, the ticket, or the glossary senses in
reach is a value the Tester invented, and every invented value is an
assumption wearing a number. The detector locates; the sentence is written
mechanically; no model is asked to introspect at all -- which is also the
answer to the ledger-silence finding, because a ledger that fills itself
where mechanics can see does not depend on a model volunteering.
"""
from __future__ import annotations

import ast
import re

# Values whose choice carries no information: defaults every test reaches for
# that assert nothing about the domain.
_TRIVIAL = {"", "0", "1", "-1", "2", "true", "false", "none", "[]", "{}"}


def literals_in(body: str) -> list[str]:
    """String and number literals in a test body, best-effort.

    `ast` when the body parses as Python -- the honest extractor, immune to
    comments and format tricks. A body that does not parse (another language,
    a fragment) falls back to a regex over quoted strings and bare numbers,
    which errs toward finding more; the comparison step is what decides
    invented, so overcollection costs nothing.
    """
    out: list[str] = []
    try:
        tree = ast.parse(body)
    except SyntaxError:
        for m in re.finditer(r"'([^']*)'|\"([^\"]*)\"|(?<![\w.])(\d+\.?\d*)",
                             body):
            out.append(next(g for g in m.groups() if g is not None))
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(
                node.value, (str, int, float)) and not isinstance(
                node.value, bool):
            out.append(str(node.value))
    return out


def invented_literals(body: str, material: str) -> list[str]:
    """The literals the material never fixed, in first-seen order.

    A literal counts as given when its normalised form appears anywhere in
    the material blob (criterion, ticket, senses -- whatever the caller had
    in reach). Case-insensitive, because 'A@B.co' in the test and 'a@b.co'
    in the criterion are one choice, already made.
    """
    blob = " ".join((material or "").lower().split())
    seen: list[str] = []
    for lit in literals_in(body):
        norm = " ".join(lit.lower().split())
        if norm in _TRIVIAL or len(norm) < 2:
            continue
        if norm in blob:
            continue
        # Paths and dotted names are structure, not domain choices: the test
        # file's own module path is not an assumption about the feature.
        if "/" in norm or norm.endswith(".py"):
            continue
        if norm not in (s.lower() for s in seen):
            seen.append(lit)
    return seen


def sentence_for(test_id: str, invented: list[str]) -> str:
    """One row per test, not one per literal -- the over-production law."""
    shown = ", ".join(repr(x) for x in invented[:6])
    more = f" and {len(invented) - 6} more" if len(invented) > 6 else ""
    return (f"invented values in {test_id}: {shown}{more} -- the criterion "
            f"fixes none of these; each is a choice the test made")


# ---------------------------------------------------------------------------
# Detector two: diff grains outside the predicted touch set.
#
# The Architect writes `batch_touch` before a batch builds (paths always,
# symbols where confident) and law 12 keeps it a prediction: nothing rejects
# a diff for straying outside it. So this detector does not hold the door
# the way detector one does. The commit stands; the paths the diff reached
# that no predicted grain covers are the divergence; `code.commit` writes
# one `touch_strays` row per path in its own transaction; the Architect is
# woken to say foreseen or mistake; the merge waits for the word. First
# built 2026-09-03 on a branch the history rewrite left behind; ported
# 2026-09-13 after click merged `echo_json` in two files the prediction
# never named and nobody was asked.
# ---------------------------------------------------------------------------

def _norm(path: str) -> str:
    return (path or "").replace("\\", "/").strip().lstrip("./")


def under(path: str, area: str) -> bool:
    """A predicted path covers itself and everything beneath it. Backslashes
    fold: the prediction is written on one platform and the diff read on
    another."""
    p, a = _norm(path), _norm(area).rstrip("/")
    return bool(a) and (p == a or p.startswith(a + "/"))


def stray_paths(touched: list[str], predicted: list[str]) -> list[str]:
    """The touched paths no predicted grain covers, in diff order.

    An empty prediction yields nothing: with nothing predicted there is
    nothing to diverge from. A file-qualified symbol (`src/auth.py::login`)
    predicts its file. The caller drops bare symbols before this: a name
    alone is not ground, and only the caller knows a grain's kind.
    """
    areas = [a for a in (_norm(g.split("::", 1)[0]) for g in predicted if g) if a]
    if not areas:
        return []
    return [p for p in touched if not any(under(p, a) for a in areas)]
