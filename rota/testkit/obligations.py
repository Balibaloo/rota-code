"""
What must be validated, generated from the graph.

Edge coverage already works this way and it is the property worth copying:
**drawing an edge creates a red row.** A capability cannot be added without
something being obliged to exercise it, and the obligation cannot drift from the
design because the design emits it.

Four tiers, each asking a different question of the same wiring:

    L0  wiring       does the function exist and refuse nonsense     deterministic
    L1  action       given a state where this is the only right move,
                     does the role take it                           real model
    L2  situation    given this wake, does the role choose at all    real model
    L3  handoff      does A's message make B do the right thing      real model

L1 counts *model-callable* operations only. `transcript.append` is marked
`actor: system` — recorded mechanically, on Liaison's behalf — and asking a
model to do it was the thing that produced fabricated entries.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..design import graph as graph_mod


@dataclass(frozen=True)
class Obligation:
    tier: str
    role: str
    what: str          # `artefact.verb`, a mode name, or `verb -> role`
    why: str

    @property
    def id(self) -> str:
        return f"{self.tier}:{self.role}:{self.what}"


def l1(g: graph_mod.Graph | None = None) -> list[Obligation]:
    """One per operation a role can actually call."""
    g = g or graph_mod.load()
    out = []
    for e in g.of_type("reads") + g.of_type("writes"):
        if not e.model_callable or e.s not in g.roles:
            continue
        out.append(Obligation(
            "L1", e.s, f"{e.t}.{e.v}",
            f"{e.n or e.t} · {e.rows or 'none'}"
            + (f"/{e.depth}" if e.depth else "")))
    for e in g.of_type("messages"):
        if e.s not in g.roles:
            continue
        out.append(Obligation("L1", e.s, f"msg.{e.v}_{e.t}", e.n or ""))
    return sorted(set(out), key=lambda o: o.id)


def l2(g: graph_mod.Graph | None = None) -> list[Obligation]:
    """One per mode a role can be woken into: inbound verbs plus predicates."""
    from ..core import predicates as P

    g = g or graph_mod.load()
    out = []
    for e in g.of_type("messages"):
        if e.t in g.roles:
            out.append(Obligation("L2", e.t, e.v, f"woken by {e.s}"))
    for p in P.REGISTRY.values():
        if p.wakes in g.roles:
            out.append(Obligation("L2", p.wakes, p.name, "woken by a predicate"))
    return sorted(set(out), key=lambda o: o.id)


def l3(g: graph_mod.Graph | None = None, *, interesting_only: bool = True
       ) -> list[Obligation]:
    """
    One per two-edge chain: A sends to B, B then sends onward.

    `interesting_only` keeps the chains where B's own action *changes an
    artefact*. A chain that only relays tests the bus, which L1 already did;
    the tier exists to ask whether the message vocabulary carries enough meaning
    to coordinate strangers, and a relay carries none of it.
    """
    g = g or graph_mod.load()
    msgs = [e for e in g.of_type("messages") if e.s in g.roles or e.s == "principal"]
    writes_of = {r: {e.t for e in g.of_type("writes") if e.s == r} for r in g.roles}

    out = []
    for first in msgs:
        if first.t not in g.roles:
            continue
        for second in msgs:
            if second.s != first.t:
                continue
            if interesting_only and not writes_of.get(second.s):
                continue
            out.append(Obligation(
                "L3", first.t,
                f"{first.s} -{first.v}-> {first.t} -{second.v}-> {second.t}",
                f"does {first.v} make {first.t} {second.v}"))
    return sorted(set(out), key=lambda o: o.id)


def all_obligations(g: graph_mod.Graph | None = None) -> list[Obligation]:
    g = g or graph_mod.load()
    return l1(g) + l2(g) + l3(g)


def summary(g: graph_mod.Graph | None = None) -> dict[str, int]:
    g = g or graph_mod.load()
    return {"L1": len(l1(g)), "L2": len(l2(g)), "L3": len(l3(g))}


if __name__ == "__main__":
    counts = summary()
    print("obligations generated from the graph\n")
    for tier, n in counts.items():
        print(f"  {tier}  {n}")
    print(f"\n  total {sum(counts.values())}")
    print("\nby role, L1:")
    per: dict[str, int] = {}
    for o in l1():
        per[o.role] = per.get(o.role, 0) + 1
    for role, n in sorted(per.items()):
        print(f"  {role:15} {n}")
