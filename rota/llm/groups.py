"""
Capability groups, derived from the graph and the modes, never hand-written.
plans/model-setup.md, step 7.

`obligations.l2` lists every mode a role can be woken into, and each mode's
`.tools` file narrows the functions it may call. The shape of those
functions is the group: a mode that reads or writes code or tests is
`code`; one that speaks to the principal, quotes the transcript or segments
the brief is `prose`; the rest read rows and write rows, `rows`. A mode may
sit in a different group from its role: the Architect's survey reads code,
its grouping reads rows. The partition is the graph's; the ranking within
a group comes from the benchmark, and a group whose modes disagree on the
best model splits (step 7's rule, applied when the table has per-mode rows).
"""
from __future__ import annotations

from collections import Counter, defaultdict

CODE = ("code.", "tests.encode", "tests.load", "findings.", "verdicts.emit", "challenge.")
PROSE = ("transcript.", "brief.", "rulings.", "msg.clarify_principal", "msg.confirm_principal",
         "msg.present_principal", "msg.converse_principal", "entries.")


def group_of(tools: list[str] | None) -> str:
    fns = tools or []
    if any(f.startswith(CODE) for f in fns):
        return "code"
    if any(f.startswith(PROSE) for f in fns):
        return "prose"
    return "rows"


def by_mode() -> dict[tuple[str, str], str]:
    """(role, mode) -> group, for every mode the graph knows."""
    from ..roles import prompts
    from ..testkit import obligations
    out: dict[tuple[str, str], str] = {}
    for o in obligations.l2():
        out[(o.role, o.what)] = group_of(prompts.mode_tools(o.role, o.what))
    return out


def groups() -> dict[str, list[tuple[str, str]]]:
    """group -> the (role, mode) pairs in it."""
    out: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for key, g in sorted(by_mode().items()):
        out[g].append(key)
    return dict(out)


def group_of_role(role: str) -> str:
    """The group most of a role's modes sit in: the capability a per-role
    benchmark row speaks for, until the table has per-mode rows."""
    counts = Counter(g for (r, _m), g in by_mode().items() if r == role)
    return counts.most_common(1)[0][0] if counts else "rows"
