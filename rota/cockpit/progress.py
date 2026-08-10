"""
Progress: how far the build is, computed rather than reported.

Every number here is derived from something that already exists for another
reason — the milestone's own checkboxes, the graph, the case files, the case-run
log the L1 suite writes. Nothing is a figure somebody types in and forgets to
update, which is the only kind of progress dashboard worth having.

**The stale result is the point.** A case that passed 5/5 against a prompt that
has since been edited is not evidence about the prompt in the tree, and a green
row that quietly means "green last week" is worse than a grey one, because it is
the number you would stop checking. Every L1 result is keyed by the prompt hash
it ran against and compared to the hash now on disk; a mismatch shows as stale.
"""
from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .. import paths
from ..design import graph as graph_mod
from ..llm.llm import Pins
from ..roles import prompts
from ..testkit import fixtures, obligations

CASES = paths.REPO / "tests" / "rota" / "cases"
MILESTONE = paths.PACKAGE / "MILESTONE.md"

_STAGE = re.compile(r"^##\s+(\d+\S*)\s*[·.]?\s*(.*)$")
_BOX = re.compile(r"^\s*-\s*\[( |x|X)\]\s*(?:\*\*)?([^*\n]+)")


# ---------------------------------------------------------------------------
# The milestone, from its own checkboxes
# ---------------------------------------------------------------------------

@dataclass
class Stage:
    key: str
    title: str
    done: int = 0
    total: int = 0
    open_items: list[str] = field(default_factory=list)


def milestone() -> list[dict]:
    if not MILESTONE.exists():
        return []
    stages: list[Stage] = []
    for line in MILESTONE.read_text(encoding="utf-8").splitlines():
        head = _STAGE.match(line)
        if head:
            stages.append(Stage(key=head.group(1), title=head.group(2).strip()))
            continue
        box = _BOX.match(line)
        if box and stages:
            stages[-1].total += 1
            if box.group(1).lower() == "x":
                stages[-1].done += 1
            else:
                stages[-1].open_items.append(box.group(2).strip().rstrip(".").strip())
    return [asdict(s) for s in stages if s.total]


# ---------------------------------------------------------------------------
# Coverage: what has a case at all
# ---------------------------------------------------------------------------

def _cases() -> list[dict]:
    out = []
    for path in sorted(CASES.glob("l*.yaml")):
        out.extend(fixtures.load_case(path) or [])
    return out


def coverage() -> dict:
    """
    What has a case, per tier, credited from the cases themselves.

    L2 read zero for as long as the panel existed, which was flatly wrong: an L2
    obligation is *one per mode a role can be woken into*, and one case per mode
    is exactly what the case files are. The tier had been written down as not
    started while it was the only tier with any coverage at all — the numbers
    were being read off the plan rather than off the work.

    L1 is finer and is credited by side-effect: a case that asserts a write to
    `criteria` exercises whatever L1 obligations touch that artefact. Honest but
    generous, and stated as such — it is the reason L1 climbs without anybody
    writing an L1-specific case.

    L3 is counted in *pairs*, not in obligations. The obligation set names the
    verbs on both hops — 229 of them — but a chain case cannot declare the
    second verb in advance, because the message under test is whichever one the
    first role actually chose to send. Crediting all 229 obligations for a pair
    that has one case turned five cases into "39 covered", which is the kind of
    generous arithmetic this panel exists to avoid. A pair is what a chain case
    honestly establishes, so a pair is what is counted.
    """
    cases = _cases()
    # A chain case names two roles and no single mode; it is credited to L3.
    single = [c for c in cases if c.get("role")]
    cased_modes = {(c["role"], fixtures.mode_of(c)) for c in single}
    all_modes = {(role, mode)
                 for role in graph_mod.load().roles
                 for mode in prompts.available(role)}

    covered_actions = set()
    for case in single:
        for table in ((case.get("expect") or {}).get("writes") or {}):
            covered_actions.add(f"{case['role']}:{table}")
        for fn in (case.get("expect") or {}).get("calls") or []:
            covered_actions.add(f"{case['role']}:{fn.split('.')[0]}")
        for spec in (case.get("expect") or {}).get("messages") or []:
            if spec.get("to") and spec.get("verb"):
                covered_actions.add(
                    f"{case['role']}:msg.{spec['verb']}_{spec['to']}")

    l1 = obligations.l1()
    l1_done = sum(1 for o in l1
                  if f"{o.role}:{o.what.split('.')[0]}" in covered_actions
                  or f"{o.role}:{o.what}" in covered_actions)
    l2 = obligations.l2()
    l2_done = sum(1 for o in l2 if (o.role, o.what) in cased_modes)

    # A chain case is credited to the handoff it actually exercises: the first
    # role, the verb it sends, the second role. Which verb that is comes from
    # the case rather than from the graph, because the whole point of the tier
    # is that the message is the one A really sent.
    pairs = {(o.what.split(" -")[0].strip(), o.role) for o in obligations.l3()}
    chains = {(c["first"]["role"], c["then"]["role"])
              for c in cases if c.get("first")}
    l3_done, l3_total = len(chains & pairs), len(pairs)

    return {
        "modes": {"done": len(cased_modes & all_modes), "total": len(all_modes),
                  "missing": sorted(f"{r}/{m}" for r, m in all_modes - cased_modes)},
        "cases": len(cases),
        "tiers": [
            {"tier": "L1", "label": "actions", "done": l1_done, "total": len(l1)},
            {"tier": "L2", "label": "situations", "done": l2_done, "total": len(l2)},
            {"tier": "L3", "label": "handoff pairs", "done": l3_done,
             "total": l3_total},
        ],
    }


# ---------------------------------------------------------------------------
# L1 health, with staleness
# ---------------------------------------------------------------------------

def _prompt_hash(case: dict, model: str) -> str:
    """The hash the case *would* record against if it ran now."""
    instructions = prompts.compose(case["role"], fixtures.mode_of(case))
    return Pins(model=model, temperature=0.0, num_ctx=8192).with_prompt(
        instructions).prompt_hash


def l1(dev_db: Path | None = None) -> dict:
    """Latest recorded outcome per case, and whether it still means anything."""
    path = dev_db or paths.DEV_DB
    cases = {c["id"]: c for c in _cases() if c.get("role")}
    rows: list[dict] = []

    recorded = _runs(path)
    model = next((r["model"] for rows in recorded.values() for r in rows), "")

    for case_id, case in cases.items():
        runs = recorded.get(case_id, [])
        entry = {
            "id": case_id, "role": case["role"], "mode": fixtures.mode_of(case),
            "threshold": int(case.get("pass", case.get("runs", 1))),
            "runs": int(case.get("runs", 1)),
            "passed": None, "state": "never run", "problems": [],
        }
        if runs:
            latest_hash = runs[-1]["prompt_hash"]
            batch = [r for r in runs if r["prompt_hash"] == latest_hash][-entry["runs"]:]
            entry["passed"] = sum(r["passed"] for r in batch)
            entry["problems"] = sorted({
                p for r in batch for p in json.loads(r["problems"])})
            fresh = latest_hash == _prompt_hash(case, model or "llama3.1:8b")
            if not fresh:
                entry["state"] = "stale"
            elif entry["passed"] >= entry["threshold"]:
                entry["state"] = "pass"
            else:
                entry["state"] = "fail"
        rows.append(entry)

    rows.sort(key=lambda r: (r["role"], r["id"]))
    tally = {}
    for r in rows:
        tally[r["state"]] = tally.get(r["state"], 0) + 1
    return {"model": model, "cases": rows, "tally": tally}


# ---------------------------------------------------------------------------
# Onboarding readiness — the stage that was a predicate over an empty world
# ---------------------------------------------------------------------------

def onboarding(conn: sqlite3.Connection) -> dict:
    def one(sql, *args):
        row = conn.execute(sql, args).fetchone()
        return row[0] if row else 0

    try:
        indexed = one("SELECT COUNT(*) FROM code_index")
        return {
            "indexed": indexed,
            "edges": one("SELECT COUNT(*) FROM code_edges"),
            "areas": one("SELECT COUNT(DISTINCT area) FROM code_index "
                         "WHERE area IS NOT NULL"),
            "surveyed": one("SELECT COUNT(DISTINCT area) FROM survey_records"),
            "under_zero": one("SELECT COUNT(*) FROM constraint_bindings "
                              "WHERE constraint_id = 'k0'"),
        }
    except sqlite3.Error:                                   # pragma: no cover
        return {"indexed": 0, "edges": 0, "areas": 0, "surveyed": 0,
                "under_zero": 0}


# ---------------------------------------------------------------------------
# The cases themselves, with the wiring each one touches
# ---------------------------------------------------------------------------

_FKS: dict[str, list[tuple[str, str]]] | None = None


def _foreign_keys() -> dict[str, list[tuple[str, str]]]:
    """`table -> [(column, target table)]`, read off the DDL rather than listed."""
    global _FKS
    if _FKS is None:
        from ..core.db import SCHEMA_PATH

        _FKS = {}
        ddl = SCHEMA_PATH.read_text(encoding="utf-8")
        for block in re.finditer(
                r"CREATE TABLE IF NOT EXISTS (\w+)\s*\((.*?)\n\);", ddl, re.S):
            table, body = block.group(1), block.group(2)
            for line in body.splitlines():
                hit = re.match(r"\s*(\w+)\s+\w+.*?REFERENCES\s+(\w+)\s*\(", line)
                if hit:
                    _FKS.setdefault(table, []).append((hit.group(1), hit.group(2)))
    return _FKS


def _situation(case: dict, g) -> dict:
    """
    What the fixture actually instantiates, and how it hangs together.

    The first version of the case view lit the edges the *mode* offered, which
    is a picture of what the role could do rather than of the situation it was
    put in — the same picture for every case in that mode. What a case is
    actually about is the rows it seeds and the links between them: a batch with
    a ticket with a criterion with a failing test run is a shape you can read,
    and it is different for every case.

    Links are only drawn where the seeded data really references seeded data. A
    foreign key column pointing at a row nobody created is not a relationship
    the case established.
    """
    from ..core.db import ARTEFACT_OF_TABLE

    fixture = case.get("fixture") or {}
    ids: dict[str, set[str]] = {}
    for table, rows in fixture.items():
        ids[table] = {str(r.get("id")) for r in (rows or []) if r.get("id")}

    seeded, links = {}, []
    for table, rows in sorted(fixture.items()):
        artefact = ARTEFACT_OF_TABLE.get(table, table)
        entry = seeded.setdefault(artefact, {"artefact": artefact, "tables": [],
                                             "rows": 0, "sample": []})
        entry["tables"].append(table)
        entry["rows"] += len(rows or [])
        for row in (rows or [])[:6]:
            entry["sample"].append({"table": table, **{
                k: (str(v)[:110]) for k, v in row.items()}})

        for column, target in _foreign_keys().get(table, []):
            for row in rows or []:
                value = row.get(column)
                if value is not None and str(value) in ids.get(target, set()):
                    pair = [artefact, ARTEFACT_OF_TABLE.get(target, target),
                            f"{table}.{column}"]
                    if pair[0] != pair[1] and pair not in links:
                        links.append(pair)

    return {"seeded": sorted(seeded.values(), key=lambda e: e["artefact"]),
            "links": links, "roles": []}


def _edges_for(role: str, mode: str, case: dict, g) -> dict[str, list]:
    """
    Which graph edges a case is *about*, split by what the case says of them.

    `offered` is the mode's tool list — the role's whole world for this waking.
    `required` and `forbidden` are what the case asserts on top. Rendering all
    three is the point: a case is as much about the edges it forbids as the ones
    it demands, and on the graph that distinction is the readable one.
    """
    def edge(s, t, verb, kind):
        for e in g.of_type(kind):
            if e.s == s and e.t == t and e.v == verb:
                return [e.s, e.t, e.type, e.v]
        return None

    def artefact_edges(names, kinds=("reads", "writes")):
        out = []
        for name in names:
            if "." not in name:
                continue
            art, verb = name.split(".", 1)
            if art == "msg":
                recipient = verb.split("_", 1)[-1]
                hit = edge(role, recipient, verb.split("_", 1)[0], "messages")
            else:
                hit = next((e for k in kinds if (e := edge(role, art, verb, k))), None)
            if hit:
                out.append(hit)
        return out

    from ..core.db import ARTEFACT_OF_TABLE

    expect, forbidden = case.get("expect") or {}, case.get("forbidden") or {}
    branches = expect.get("any_of") or [expect]

    required, denied = [], []
    for branch in branches:
        for table in (branch.get("writes") or {}):
            art = ARTEFACT_OF_TABLE.get(table)
            hit = next((e for e in g.of_type("writes")
                        if e.s == role and e.t == art), None)
            if hit:
                required.append([hit.s, hit.t, hit.type, hit.v])
        for spec in branch.get("messages") or []:
            hit = edge(role, spec.get("to"), spec.get("verb"), "messages")
            if hit:
                required.append(hit)
    required += artefact_edges(expect.get("calls") or [])

    for table in forbidden.get("writes") or []:
        art = ARTEFACT_OF_TABLE.get(table)
        hit = next((e for e in g.of_type("writes")
                    if e.s == role and e.t == art), None)
        if hit:
            denied.append([hit.s, hit.t, hit.type, hit.v])
    for recipient in forbidden.get("recipients") or []:
        denied += [[e.s, e.t, e.type, e.v] for e in g.of_type("messages")
                   if e.s == role and e.t == recipient]
    denied += artefact_edges(forbidden.get("calls") or [])

    # A forbidden write the role has no edge for is not a risk the case is
    # guarding against — it is a belt on braces, and the graph already made it
    # impossible. Worth separating: the first kind is what the case is *for*,
    # the second is a note that a law is enforced structurally.
    offered = artefact_edges(prompts.mode_tools(role, mode) or [])
    writable = {e.t for e in g.of_type("writes") if e.s == role}
    contactable = {e.t for e in g.of_type("messages") if e.s == role}
    impossible = sorted(
        {f"write {t}" for t in (forbidden.get("writes") or [])
         if ARTEFACT_OF_TABLE.get(t, t) not in writable}
        | {f"message {r}" for r in (forbidden.get("recipients") or [])
           if r not in contactable})
    return {"offered": offered, "required": required, "forbidden": denied,
            "impossible": impossible}


def message_text(case_id: str) -> dict:
    """
    The prompt the session actually builds, for one case.

    Everything else in the panel is *about* the session — who it is, what mode,
    what it may call. This is the thing itself: the words placed in front of the
    model, assembled by the same functions a real session uses, against a
    database seeded from the case.

    Built on request rather than served with every case, because it costs a
    temporary database and a sandbox per case and almost nobody wants all
    fifty-nine at once.
    """
    import tempfile

    from ..core.db import init_db
    from ..core.loop import _batch_of
    from ..core.runner import build_prompt, push_working_set, resolve_inbound
    from ..core.sandbox import build as build_sandbox
    from ..core.scheduler import Wake

    case = next((c for c in _cases() if c["id"] == case_id), None)
    if case is None:
        return {}

    spec = case.get("first") or case
    role = spec["role"]
    mode = fixtures.mode_of(spec if case.get("first") else case)

    conn = init_db(Path(tempfile.mkdtemp()) / "rota.db")
    fixtures.seed(conn, case.get("fixture") or {})

    inbound = case.get("inbound") or {}
    msg_id = inbound.get("id", "m_in") if inbound else None
    if inbound:
        conn.execute(
            "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
            "body_refs, seq) VALUES (?,?,?,?,?,?,99)",
            (msg_id, "t1", inbound["from"], inbound["to"], inbound["verb"],
             json.dumps(inbound.get("body_refs", []))))

    wake = Wake(role=role, kind="message", message_id=msg_id,
                refs=tuple(case.get("refs") or ()),
                detail=inbound.get("verb") or case.get("tick", ""))
    sb = build_sandbox(role, conn, batch_id=_batch_of(conn, wake),
                       area=wake.refs[0] if case.get("tick") == "survey" else None,
                       allow=prompts.mode_tools(role, mode))
    pushed = push_working_set(role, sb, wake)
    system, user = build_prompt(role, sb, wake, pushed,
                                prompts.compose(role, mode),
                                resolve_inbound(conn, wake))
    conn.close()
    return {"system": system, "user": user,
            "chars": len(system) + len(user),
            "tokens": (len(system) + len(user)) // 4}


def _woken(case: dict) -> str:
    """One sentence saying what put this role in this mode.

    "woken by liaison — ask" is the system's own vocabulary read back at you.
    What happened is that Liaison sent an `ask` message, and that is a sentence
    about the world rather than about the wake record."""
    inbound = case.get("inbound") or (case.get("first") or {})
    if inbound.get("from"):
        return f"{inbound['from']} sends {inbound.get('verb', 'a')} message"
    tick = case.get("tick") or (case.get("first") or {}).get("tick")
    return f"the {tick} predicate fires" if tick else "woken with no trigger"


def cases(dev_db: Path | None = None) -> list[dict]:
    """
    Every case, in a shape the viewer can render and light the graph from.

    Cases were only ever visible by opening six YAML files, which made "what does
    this system actually check" a question you had to be inside the repository to
    ask. They are the most discussable artefact here and the least discoverable.
    """
    from ..core.db import ARTEFACT_OF_TABLE

    g = graph_mod.load()
    runs = _runs(dev_db)

    out = []
    for case in _cases():
        chain = bool(case.get("first"))
        role = case["first"]["role"] if chain else case["role"]
        mode = (fixtures.mode_of(case["first"]) if chain
                else fixtures.mode_of(case))
        second = case["then"]["role"] if chain else None

        situation = _situation(case, g)
        situation["roles"] = [r for r in (role, second) if r]
        # Three different things the picture has to keep apart: who is under
        # test, what they were *given*, and what is being *watched*. An artefact
        # can be all three, and which it is changes what a failure means.
        from ..core.db import ARTEFACT_OF_TABLE as _A

        watched = {_A.get(t, t) for branch in
                   ((case.get("expect") or {}).get("any_of")
                    or [case.get("expect") or {}])
                   for t in (branch.get("writes") or {})}
        situation["watched"] = sorted(watched)

        # Seeded is not the same as *visible*. A ticket has an `item_id`
        # foreign key, so a fixture cannot create one without an item — and
        # Developer has no read edge to `problem` at all, because scope is
        # Gatekeeper's. Those rows are there to make the fixture valid and the
        # scheduler able to find a batch, not because the role was handed them.
        #
        # Drawn as one colour they produced a disconnected subgraph and an
        # implied claim that the role could see it. They are scaffolding.
        reach = set()
        for kind in ("reads", "writes"):
            for e in g.of_type(kind):
                if e.s in situation["roles"]:
                    allowed = prompts.mode_tools(e.s, mode if e.s == role else "") 
                    if allowed is None or f"{e.t}.{e.v}" in allowed:
                        reach.add(e.t)
        seeded_arts = {e["artefact"] for e in situation["seeded"]}
        situation["given"] = sorted(seeded_arts & reach)
        situation["scaffolding"] = sorted(seeded_arts - reach)
        situation["fixtured"] = sorted(seeded_arts)

        # How the role reaches what it was given, and what it writes to what
        # is watched. Without these the role node sits unconnected: the picture
        # showed the situation and the assertions and nothing joining them, so
        # every case looked like a dimmed graph with a few islands lit.
        roles_here = set(situation["roles"])
        edges = _edges_for(role, mode, case, g)
        edges["reading"] = [[e.s, e.t, e.type, e.v] for e in g.of_type("reads")
                            if e.s in roles_here and e.t in situation["given"]]
        edges["writing"] = [[e.s, e.t, e.type, e.v] for e in g.of_type("writes")
                            if e.s in roles_here and e.t in situation["watched"]]
        if chain:
            second_mode = fixtures.mode_of({**case["then"],
                                            "tick": case["then"].get("tick", "")})
            for key, val in _edges_for(second, second_mode, case, g).items():
                edges[key] = edges[key] + val

        latest = (runs.get(case["id"]) or [])[-5:]
        out.append({
            "id": case["id"], "tier": case.get("tier", ""), "role": role,
            "second": second, "mode": mode,
            "runs": int(case.get("runs", 1)),
            "threshold": int(case.get("pass", case.get("runs", 1))),
            "repo": bool(case.get("repo")),
            "onboarded": bool((case.get("repo") or {}).get("onboard")),
            "refs": case.get("refs") or [],
            "inbound": case.get("inbound") or {},
            "situation": situation,
            "expect": case.get("expect") or {},
            "forbidden": case.get("forbidden") or {},
            "edges": edges,
            "source": _source_for(case["id"]),
            # What the role is actually told, assembled the way a session
            # assembles it. The markdown file is not the prompt; the
            # composition is, and the composition is what you read when a role
            # misbehaves.
            "brief": {
                "base": prompts.base(role),
                "mode": prompts.piece(role, mode),
                "tools": prompts.mode_tools(role, mode) or [],
            },
            "woken": _woken(case),
            "history": [{"run": r["run_no"], "passed": bool(r["passed"]),
                         "problems": json.loads(r["problems"] or "[]"),
                         "transcript": json.loads(r["transcript"] or "[]")}
                        for r in latest],
        })
    return out


_SOURCE: dict[str, str] | None = None


def _source_for(case_id: str) -> str:
    """
    The case exactly as written, comments and all.

    Every case here carries its reasoning inline — why this fixture, what
    failure it watches for, why the threshold is 3 and not 4 — and a YAML parser
    throws all of it away. Showing the parsed assertions without the argument for
    them would leave the panel displaying the *what* and hiding the *why*, which
    is the half worth discussing.
    """
    global _SOURCE
    if _SOURCE is None:
        _SOURCE = {}
        for path in sorted(CASES.glob("l*.yaml")):
            current, buffer = None, []
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("- id: "):
                    if current:
                        _SOURCE[current] = chr(10).join(buffer).rstrip()
                    current, buffer = line[6:].strip(), [line]
                elif current is not None:
                    buffer.append(line)
            if current:
                _SOURCE[current] = chr(10).join(buffer).rstrip()
    return _SOURCE.get(case_id, "")


def _runs(dev_db: Path | None = None) -> dict[str, list]:
    path = dev_db or paths.DEV_DB
    out: dict[str, list] = {}
    if not path.exists():
        return out
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        for r in conn.execute(
            "SELECT case_id, model, prompt_hash, run_no, passed, problems, "
            "transcript, seq FROM case_runs ORDER BY seq"
        ):
            out.setdefault(r["case_id"], []).append(dict(r))
    except sqlite3.Error:                                   # pragma: no cover
        return {}
    finally:
        conn.close()
    return out


def report(conn: sqlite3.Connection) -> dict:
    return {
        "milestone": milestone(),
        "coverage": coverage(),
        "l1": l1(),
        "onboarding": onboarding(conn),
    }
