"""
Model setup, the backend the screen and the cockpit share.
plans/model-setup.md, step 6. One call, `plan()`, returns everything the
screen shows: the providers found, the models each can serve with their fit
and score, a recommendation per capability, and the machine. The screen's
product is a profile file, written by `write()` from a shipped one.

Discovery refuses to run while a run is driving. One GPU: a load evicts the
walk's models and per-load determinism resets. The caller passes
`driving`; this module does not open a run.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import benchmarks as B
from . import discover as D
from . import profile as profile_mod


class Driving(RuntimeError):
    """Discovery asked for while a run drives."""


@dataclass(frozen=True)
class Row:
    provider: str
    model: str
    fit: str                      # in_vram | spills | does_not_fit | unknown
    need_mib: int | None
    scores: dict = field(default_factory=dict)   # capability -> score, recorded only
    recorded: bool = False        # any benchmark row with three or more cases


@dataclass(frozen=True)
class Plan:
    providers: list[D.Provider]
    machine: D.System
    rows: list[Row]
    recommendation: dict          # capability -> model name, or None
    groups: list[str]


def plan(driving: bool = False, num_ctx: int = 12288, table: list[dict] | None = None) -> Plan:
    if driving:
        raise Driving("a run is driving; discovery would evict its models. "
                      "Pause the run first")
    table = B.load() if table is None else table
    providers = D.providers()
    machine = D.system()
    held = D.loaded()
    found: list[D.Model] = []
    for p in providers:
        try:
            found += D.models(p)
        except Exception:
            continue
    scores: dict[str, dict[str, float]] = {}
    recorded: set[str] = set()
    for r in table:
        cap = r["capability"]
        if cap.startswith(("transport:", "walk:")):
            continue
        scores.setdefault(r["model"], {})[cap] = float(r["score"])
        if int(r.get("cases", 0) or 0) >= 3:
            recorded.add(r["model"])
    rows = []
    for m in found:
        lb = held.get(m.name, (0, 0))[0] or None
        f = D.fit_of(m, machine, num_ctx, loaded_bytes=lb)
        rows.append(Row(m.provider, m.name, f.fit, (f.need_bytes or 0) >> 20 or None,
                        scores.get(m.name, {}), m.name in recorded))
    # The derived groups when the table has them (step 7), the roles before.
    groups = sorted({r["capability"] for r in table if r["capability"].startswith("group:")})
    if not groups:
        groups = sorted({r["capability"] for r in table
                         if not r["capability"].startswith(("transport:", "walk:"))})
    rec = D.recommend(found, machine, table, groups, num_ctx=num_ctx, resident=1)
    recommendation = {g: (fit.model if fit else None) for g, fit in rec.items()}
    return Plan(providers, machine, rows, recommendation, groups)


def choose(plan_: Plan) -> tuple[str, dict[str, str]]:
    """A default and per-desk overrides from the recommendation: the model
    recommended most often is the default; a desk whose model differs is an
    override. Capabilities are roles until step 7."""
    picks = {g: m for g, m in plan_.recommendation.items() if m}
    if not picks:
        return "", {}
    counts: dict[str, int] = {}
    for m in picks.values():
        counts[m] = counts.get(m, 0) + 1
    default = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    roles: dict[str, str] = {}
    for g, m in picks.items():
        if m == default:
            continue
        if g in ROLE_OF:
            roles[ROLE_OF[g]] = m
        elif g.startswith("group:"):
            # A group's model reaches every role whose modes mostly sit in it.
            from . import groups as groups_mod
            for role in ROLE_OF.values():
                if groups_mod.group_of_role(role) == g.split(":", 1)[1]:
                    roles[role] = m
    return default, roles


ROLE_OF = {"LI": "liaison", "VK": "vision_keeper", "TE": "terminologist", "AR": "architect",
           "DV": "developer", "TS": "tester", "CR": "critic", "RS": "researcher"}


def write(name: str, base_name: str, default_model: str, roles: dict[str, str]):
    base = profile_mod.find(base_name)
    return profile_mod.write_user_profile(name, base, default_model, roles)
