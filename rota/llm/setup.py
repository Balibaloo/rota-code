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
from . import llm as llm_mod
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


def default_window() -> int:
    """
    The window the shipped profiles pin, which is what a run uses.

    Read from the profile, never written here as a literal. The screens
    answered for 12288 while the profile they write pins 16384, so the fit
    column and the pick described a run nobody starts. `DEFAULT_NUM_CTX`
    stays at 12288 because it keys every live recording, so it is not the
    number to compare against either.
    """
    try:
        pinned = profile_mod.Profile.from_toml(
            profile_mod.SHIPPED / "local.toml").pins.get("num_ctx")
        return int(pinned) if pinned else llm_mod.DEFAULT_NUM_CTX
    except Exception:
        return llm_mod.DEFAULT_NUM_CTX


def plan(driving: bool = False, num_ctx: int | None = None,
         table: list[dict] | None = None) -> Plan:
    if driving:
        raise Driving("a run is driving; discovery would evict its models. "
                      "Pause the run first")
    # The window a run uses, not a literal. The refusal above comes first,
    # so a driving call reads no file.
    num_ctx = default_window() if num_ctx is None else num_ctx
    table = B.load() if table is None else table
    providers = D.providers()
    machine = D.system()
    # `loaded` says None when the server did not answer, and the plan reads
    # that as "nothing measured": the arithmetic still gives every row.
    held = D.loaded() or {}
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
        # The measurement belongs to the model that was loaded, so it is per
        # row. `/api/ps` reports the window the server allocated, and that
        # window is what lets `fit_of` answer for another one. A model the
        # card does not hold has no measurement, and the metadata answers
        # (observed: probes/frame43/p_window.py, 2026-09-19).
        f = D.fit_of(m, machine, num_ctx, **D.measured_of(held, m.name))
        rows.append(Row(m.provider, m.name, f.fit, (f.need_bytes or 0) >> 20 or None,
                        scores.get(m.name, {}), m.name in recorded))
    # The derived groups when the table has them (step 7), the roles before.
    groups = sorted({r["capability"] for r in table if r["capability"].startswith("group:")})
    if not groups:
        groups = sorted({r["capability"] for r in table
                         if not r["capability"].startswith(("transport:", "walk:"))})
    # The same measurements the table above used. The pick read the weights
    # alone before, so one screen could say `spills` in the row and
    # `in_vram` in the recommendation for one model.
    rec = D.recommend(found, machine, table, groups, num_ctx=num_ctx,
                      resident=1, held=held)
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
