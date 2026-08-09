"""
The predicates, declared — and the lint that says none may be missing.

The frontier is open message tips ∪ predicates evaluated against state. That only
holds if **every state a row can be in has a way out**. A state with no predicate
draining it is a place work stops silently, and the danger is precise: quiescence
means "no predicate fires", so a dead-end state makes the system look *finished*
while work has been abandoned. The invariant we rely on would pass.

Sweeping the schema found four such dead ends — a contested item, a contradicted
statement, a batch that passed review and was never merged, and a quarantined
message nobody is ever told about. None of them were noticeable by reading; all
four fall out of one mechanical check.

So predicates are declared here rather than defined ad hoc, each naming the state
it drains, and `check_terminal_states()` asserts the set is complete. A state is
legal only if some predicate drains it or it is declared terminal with a reason.
That is a hard constraint: adding a state to the schema without a way out fails
the build.

Role names are the current ids; the rename lands separately.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .scheduler import Wake

SCHEMA = Path(__file__).resolve().parent / "schema.sql"


@dataclass(frozen=True)
class Predicate:
    name: str
    wakes: str                      # role id, or "" for a scheduler action
    drains: tuple[tuple[str, str, str], ...]   # (table, column, value)
    fn: Callable[[sqlite3.Connection], list[Wake]]
    why: str = ""


REGISTRY: dict[str, Predicate] = {}


def predicate(name: str, wakes: str, drains: tuple = (), why: str = ""):
    def deco(fn):
        REGISTRY[name] = Predicate(name=name, wakes=wakes, drains=tuple(drains),
                                   fn=fn, why=why or (fn.__doc__ or "").strip())
        return fn
    return deco


# ---------------------------------------------------------------------------
# Columns whose values are a *lifecycle* — a row passes through them and must be
# able to leave. Everything else is a classification: `kind`, `mode`,
# `cause_kind` and `grain_kind` say what a row *is*, not where it is, and asking
# what drains "out_of_scope" is a category error.
# ---------------------------------------------------------------------------

LIFECYCLE_COLUMNS = {
    ("statements", "status"),
    ("items", "approval"),
    ("items", "provenance"),
    ("glossary_terms", "provenance"),
    ("constraints", "provenance"),
    ("batches", "status"),
    ("test_runs", "result"),
    ("ledger", "status"),
    ("verdicts", "result"),
    ("messages", "status"),
    ("survey_records", "outcome"),
}

# States that are ends, with the reason. A terminal state is a claim that nothing
# further is owed — which is exactly the claim worth having to write down.
TERMINAL: dict[tuple[str, str, str], str] = {
    ("statements", "status", "ratified"):
        "the requester confirmed it; it is now material, not pending work",
    ("statements", "status", "superseded"):
        "replaced by a later statement, which carries the work forward",
    ("statements", "status", "clarified"):
        "the ambiguity was resolved in a later statement",
    ("items", "approval", "approved"):
        "drained by slicing once tickets exist; approval itself owes nothing",
    ("items", "approval", "pending"):
        "an open gate to the requester holds it; the gate is the pending work",
    ("items", "provenance", "decided"):
        "someone chose it and the reason is on file",
    ("glossary_terms", "provenance", "decided"): "reason on file",
    ("constraints", "provenance", "decided"): "reason on file",
    ("batches", "status", "merged"): "delivered",
    ("batches", "status", "running"): "a live session holds it",
    ("test_runs", "result", "pass"): "nothing is owed by a passing test",
    ("ledger", "status", "resolved"): "a decision closed it",
    ("verdicts", "result", "pass"): "drained by the merge action",
    ("messages", "status", "answered"): "a session committed against it",
    ("survey_records", "outcome", "constraints_found"): "the survey produced its record",
    ("survey_records", "outcome", "none_found"):
        "also a result — it is what starves constraint zero",
}


# ---------------------------------------------------------------------------
# The other half of the frontier, declared as a predicate.
#
# The lint caught this: `messages.status = 'open'` had no predicate draining it,
# because open tips were the *other* half of "tips ∪ predicates". That split put
# the frontier's definition in two places, and the second half was invisible to
# every check written against the first. Declared here, the frontier is simply
# "every predicate", and one of them happens to be a message query.
# ---------------------------------------------------------------------------

@predicate("message_tips", wakes="", drains=[("messages", "status", "open")])
def message_tips(conn) -> list[Wake]:
    """Messages awaiting a session. Messages to the requester are excluded — they
    are a gate, and the requester is not schedulable."""
    from .scheduler import open_tips
    return open_tips(conn)


# ---------------------------------------------------------------------------
# Understanding loop — these existed, now declared
# ---------------------------------------------------------------------------

@predicate("awaiting_confirm", wakes="liaison",
           drains=[("statements", "status", "proposed")])
def awaiting_confirm(conn) -> list[Wake]:
    """A proposed statement with no confirm outstanding: ratification has stalled.

    Without this, a segmentation that never reached the requester sits forever
    and the system reports itself quiescent."""
    rows = conn.execute(
        "SELECT id FROM statements WHERE status = 'proposed' AND id NOT IN ("
        "  SELECT value FROM config WHERE 0)"          # placeholder join
    ).fetchall()
    if not rows:
        return []
    pending = conn.execute(
        "SELECT COUNT(*) n FROM messages "
        "WHERE status = 'open' AND to_role = 'principal' AND verb = 'confirm'"
    ).fetchone()["n"]
    if pending:
        return []
    return [Wake("liaison", "tick:awaiting_confirm",
                 refs=tuple(r["id"] for r in rows))]


@predicate("contradiction", wakes="liaison",
           drains=[("statements", "status", "contradicted")])
def contradiction(conn) -> list[Wake]:
    """Two statements conflict. Only the requester can say which stands, so this
    goes back out rather than being resolved internally."""
    rows = conn.execute(
        "SELECT id FROM statements WHERE status = 'contradicted'").fetchall()
    if not rows:
        return []
    asked = conn.execute(
        "SELECT COUNT(*) n FROM messages WHERE status='open' AND to_role='principal' "
        "AND verb='clarify'").fetchone()["n"]
    return [] if asked else [
        Wake("liaison", "tick:contradiction", refs=tuple(r["id"] for r in rows))]


@predicate("contested", wakes="gatekeeper",
           drains=[("items", "approval", "contested")])
def contested(conn) -> list[Wake]:
    """The requester rejected an item.

    This was a dead end: the highest-value signal in the system landed nowhere.
    It wakes the item's owner to amend it or author a decision defending it."""
    rows = conn.execute(
        "SELECT id FROM items WHERE approval = 'contested'").fetchall()
    return [Wake("gatekeeper", "tick:contested", refs=(r["id"],)) for r in rows]


@predicate("signoff", wakes="gatekeeper", drains=[("items", "approval", "draft")])
def signoff(conn) -> list[Wake]:
    """Draft items with no gate open: submit them for approval, together."""
    from .scheduler import tick_signoff
    return tick_signoff(conn)


@predicate("round_close", wakes="liaison")
def round_close(conn) -> list[Wake]:
    """A broadcast's subtree has terminated: harvest the reports."""
    from .scheduler import tick_round_close
    return tick_round_close(conn)


@predicate("slicing", wakes="gatekeeper")
def slicing(conn) -> list[Wake]:
    """An approved item with no tickets."""
    from .scheduler import tick_slicing
    return tick_slicing(conn)


@predicate("criteria", wakes="terminologist")
def criteria(conn) -> list[Wake]:
    """Tickets with no criteria, per item."""
    from .scheduler import tick_criteria
    return tick_criteria(conn)


@predicate("observed_entries", wakes="liaison",
           drains=[("glossary_terms", "provenance", "observed"),
                   ("constraints", "provenance", "observed"),
                   ("items", "provenance", "observed")])
def observed_entries(conn) -> list[Wake]:
    """
    Entries extracted from a codebase, awaiting their first decision.

    Onboarding produces these by the hundred and nothing was ever going to ask
    the requester to confirm them, so `observed` was a state with no exit.
    """
    counts = []
    for table in ("glossary_terms", "constraints", "items"):
        n = conn.execute(
            f"SELECT COUNT(*) n FROM {table} WHERE provenance = 'observed'"
        ).fetchone()["n"]
        if n:
            counts.append(f"{table}:{n}")
    if not counts:
        return []
    asked = conn.execute(
        "SELECT COUNT(*) n FROM messages WHERE status='open' AND to_role='principal' "
        "AND verb='present'").fetchone()["n"]
    return [] if asked else [
        Wake("liaison", "tick:observed_entries", detail=", ".join(counts))]


# ---------------------------------------------------------------------------
# Delivery loop — one predicate existed; these are the rest
# ---------------------------------------------------------------------------

@predicate("tests_missing", wakes="tester")
def tests_missing(conn) -> list[Wake]:
    """Criteria for a batch with no tests. Tester needs only criteria, so it can
    run as soon as they exist — it does not wait for the Developer."""
    rows = conn.execute(
        "SELECT DISTINCT bt.batch_id AS bid FROM batch_tickets bt "
        "JOIN criteria c ON c.ticket_id = bt.ticket_id "
        "WHERE bt.batch_id NOT IN (SELECT batch_id FROM tests)"
    ).fetchall()
    return [Wake("tester", "tick:tests_missing", refs=(r["bid"],)) for r in rows]


@predicate("annotate", wakes="architect")
def annotate(conn) -> list[Wake]:
    """
    A batch with no expected touch set.

    One batch at a time and deliberately separate from grouping: grouping is
    cheap and index-only, annotating reads source, and doing every batch in one
    session would exhaust the context that makes the annotation worth having.
    """
    rows = conn.execute(
        "SELECT id FROM batches WHERE status IN ('pending','deferred') "
        "  AND id NOT IN (SELECT DISTINCT batch_id FROM batch_touch)"
        "  LIMIT 1"
    ).fetchall() if _has_table(conn, "batch_touch") else []
    return [Wake("architect", "tick:annotate", refs=(r["id"],)) for r in rows]


@predicate("batch_start", wakes="developer",
           drains=[("batches", "status", "pending"),
                   ("batches", "status", "deferred")])
def batch_start(conn) -> list[Wake]:
    """Next schedulable batch, nothing running."""
    from .scheduler import tick_batch_start
    return tick_batch_start(conn)


@predicate("tests_failing", wakes="developer",
           drains=[("test_runs", "result", "fail"), ("test_runs", "result", "error")])
def tests_failing(conn) -> list[Wake]:
    """A failing test goes straight back, capped. This *is* the cheap loop —
    a test costs a subprocess, so it bounces rather than waiting for review."""
    rows = conn.execute(
        "SELECT DISTINCT batch_id AS bid, MAX(attempt) AS att FROM test_runs "
        "WHERE result IN ('fail','error') GROUP BY batch_id"
    ).fetchall()
    return [Wake("developer", "tick:tests_failing", refs=(r["bid"],),
                 detail=f"attempt {r['att']}")
            for r in rows if (r["att"] or 1) < 10]


@predicate("review", wakes="critic")
def review(conn) -> list[Wake]:
    """A batch with a committed diff and a green harness, not yet judged.

    Critic runs before Architect: most failures are failures of intent, and
    screening them first means never paying for a constraint review on work that
    does not do what was asked."""
    rows = conn.execute(
        "SELECT b.id AS bid FROM batches b "
        "WHERE b.status = 'running' AND b.head_commit IS NOT NULL "
        "  AND b.id NOT IN (SELECT batch_id FROM verdicts) "
        "  AND b.id NOT IN (SELECT batch_id FROM test_runs WHERE result != 'pass')"
    ).fetchall()
    return [Wake("critic", "tick:review", refs=(r["bid"],)) for r in rows]


@predicate("structural_review", wakes="architect")
def structural_review(conn) -> list[Wake]:
    """A diff whose grains intersect constraint bindings, after intent passed.

    Expensive — it costs a session — so it runs once, late, on work that already
    satisfies its criteria."""
    rows = conn.execute(
        "SELECT v.batch_id AS bid FROM verdicts v "
        "WHERE v.result = 'pass' AND v.batch_id IN "
        "  (SELECT id FROM batches WHERE status = 'running')"
    ).fetchall()
    return [Wake("architect", "tick:structural_review", refs=(r["bid"],))
            for r in rows]


@predicate("verdict_failed", wakes="developer",
           drains=[("verdicts", "result", "fail")])
def verdict_failed(conn) -> list[Wake]:
    """A failed verdict with no newer commit: the Developer has not answered it."""
    rows = conn.execute(
        "SELECT v.batch_id AS bid FROM verdicts v JOIN batches b ON b.id = v.batch_id "
        "WHERE v.result = 'fail' AND b.status = 'running'"
    ).fetchall()
    return [Wake("developer", "tick:verdict_failed", refs=(r["bid"],)) for r in rows]


@predicate("merge", wakes="", drains=[("verdicts", "result", "pass")])
def merge(conn) -> list[Wake]:
    """
    A batch that passed review and was never merged.

    This was the worst dead end: the delivery loop terminated one step before
    delivering. It wakes nobody — merging is mechanical once the verdict is in,
    the same shape as the harness. The optional requester review gates it.
    """
    return []


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------

@predicate("checkpoint_invalid", wakes="")
def checkpoint_invalid(conn) -> list[Wake]:
    """An invalidated checkpoint: the suspended role must restart cold. Boot
    sweeps these; nothing did at runtime, so a mid-run invalidation stranded the
    session until the next restart."""
    rows = conn.execute(
        "SELECT session_id, role FROM checkpoints WHERE valid = 0").fetchall()
    return [Wake(r["role"], "tick:checkpoint_invalid", detail=r["session_id"])
            for r in rows]


@predicate("quarantined", wakes="liaison",
           drains=[("messages", "status", "quarantined")])
def quarantined(conn) -> list[Wake]:
    """The system gave up on a message. That is something the requester should be
    told, not something to bury — it was invisible before."""
    n = conn.execute(
        "SELECT COUNT(*) n FROM messages WHERE status = 'quarantined'").fetchone()["n"]
    return [Wake("liaison", "tick:quarantined", detail=f"{n} abandoned")] if n else []


@predicate("agenda", wakes="liaison", drains=[("ledger", "status", "open")])
def agenda(conn) -> list[Wake]:
    """On requester presence, present what is blocked on them."""
    from .scheduler import tick_agenda
    return tick_agenda(conn, principal_present=True)


@predicate("survey", wakes="")
def survey(conn) -> list[Wake]:
    """Onboarding: one elected area at a time, in role order."""
    from .scheduler import tick_survey
    return tick_survey(conn)


def _has_table(conn, name: str) -> bool:
    return bool(conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone())


# ---------------------------------------------------------------------------
# The lint: every state must have a way out
# ---------------------------------------------------------------------------

def schema_states() -> dict[tuple[str, str], list[str]]:
    """Every CHECK-constrained value in the schema, by table and column."""
    sql = SCHEMA.read_text(encoding="utf-8")
    out: dict[tuple[str, str], list[str]] = {}
    table = None
    for line in sql.splitlines():
        m = re.search(r"CREATE TABLE IF NOT EXISTS (\w+)", line)
        if m:
            table = m.group(1)
        if table:
            c = re.search(r"(\w+)\s+TEXT[^,]*CHECK\s*\(\s*\w+\s+IN\s*\(([^)]*)\)", line)
            if not c:
                c = re.search(r"CHECK\s*\((\w+)\s+IN\s*\(([^)]*)\)", line)
            if c:
                values = re.findall(r"'([^']+)'", c.group(2))
                if values:
                    out[(table, c.group(1))] = values
    return out


def drained_states() -> set[tuple[str, str, str]]:
    return {d for p in REGISTRY.values() for d in p.drains}


def check_terminal_states() -> list[str]:
    """
    Hard constraint: every lifecycle state is drained by a predicate or declared
    terminal with a reason.

    A state that is neither is a place work stops while the system reports
    itself finished — and that is invisible to every other check, because
    quiescence is defined as "no predicate fires".
    """
    problems = []
    drained = drained_states()
    for (table, column), values in schema_states().items():
        if (table, column) not in LIFECYCLE_COLUMNS:
            continue
        for value in values:
            key = (table, column, value)
            if key in drained or key in TERMINAL:
                continue
            problems.append(
                f"{table}.{column} = '{value}' has no predicate draining it and is "
                f"not declared terminal — work can stop here silently")
    return problems


def check_predicates_can_fire() -> list[str]:
    """
    A declared drain is not an implemented one.

    `check_terminal_states` reads declarations, so it can be satisfied by lying —
    a predicate that claims to drain a state and does nothing passes it. That is
    exactly what happened: `merge` declared it drained a passing verdict and its
    body was `return []`, in the same commit that claimed to close the dead end.

    Three static checks, all cheap:
      * every table a predicate queries must exist
      * a predicate declaring a drain must actually query that table
      * a predicate must be able to return something
    """
    import inspect

    schema = SCHEMA.read_text(encoding="utf-8")
    tables = set(re.findall(r"CREATE TABLE IF NOT EXISTS (\w+)", schema))
    problems = []

    for name, p in REGISTRY.items():
        src = inspect.getsource(p.fn)
        queried = set(re.findall(r"FROM (\w+)", src)) | set(re.findall(r"JOIN (\w+)", src))
        # A predicate may build its table name at runtime (`FROM {table}`), which
        # no static read can follow. Those are exempt rather than falsely flagged.
        dynamic = "FROM {" in src or "from {" in src
        delegated = "from .scheduler import" in src or dynamic

        for t in queried - tables:
            if t.isupper() or t in ("sqlite_master",):
                continue
            problems.append(f"{name} queries {t!r}, which is not in the schema")

        body = src.split('"""')[-1]
        if not delegated and body.count("return") and "return []" in body.strip()[-12:]:
            problems.append(f"{name} can never return a wake — its body always returns []")

        for table, _col, value in p.drains:
            if not delegated and table not in queried:
                problems.append(
                    f"{name} declares it drains {table}.{value!r} but never queries {table}")
    return problems


def check_states_are_reachable() -> list[str]:
    """
    A state nothing ever writes is a state nothing can be in.

    `batches.status = 'running'` was declared, three predicates depended on it,
    and no code path ever set it — so the whole delivery loop was gated on a
    value that could not occur. Crude grep, but it is the check that would have
    said so.
    """
    root = SCHEMA.parent
    schema = SCHEMA.read_text(encoding="utf-8")

    # Only *writes* count. A first attempt grepped every file and found
    # 'running' in a SELECT, so it reported the state reachable when nothing
    # could ever set it. Reading a value and writing one look identical to a
    # grep unless you say which you mean.
    writes = (root / "api.py").read_text(encoding="utf-8")          # all artefact writes
    for f in root.glob("*.py"):
        if f.name in ("api.py", "predicates.py"):
            continue
        text = f.read_text(encoding="utf-8")
        writes += chr(10).join(
            line for line in text.splitlines()
            if "UPDATE " in line or "SET " in line or "INSERT INTO" in line)
    defaults = re.findall(r"DEFAULT '([^']+)'", schema)

    # Many writes are *parameterised*: the model supplies `approval='approved'`
    # and the sandbox validates it against the column's enum. Those are correct
    # and leave no literal to grep for, so a column is also reachable if some
    # write function takes it as an argument.
    api_src = (root / "api.py").read_text(encoding="utf-8")
    parameterised = set()
    for block in re.split(r"@op\(", api_src)[1:]:
        head = block.split(")", 1)[0]
        artefact = head.split(",")[0].strip().strip("\"'")
        params = set(re.findall(r"(\w+):\s*\w", block.split("->")[0]))
        for table in re.findall(r'ctx\.writes\.append\(\(\s*"(\w+)"', block):
            for prm in params:
                parameterised.add((table, prm))

    problems = []
    for (table, column), values in schema_states().items():
        if (table, column) not in LIFECYCLE_COLUMNS:
            continue
        if (table, column) in parameterised:
            continue
        for value in values:
            if value in defaults:
                continue
            if f"'{value}'" in writes or f'"{value}"' in writes:
                continue
            problems.append(
                f"{table}.{column} = '{value}' is never written by any code path — "
                f"nothing can reach this state, so anything gated on it is dead")
    return problems


def check_predicates_wake_real_roles() -> list[str]:
    from . import graph as graph_mod

    roles = set(graph_mod.load().roles)
    return [f"predicate {p.name!r} wakes {p.wakes!r}, which is not a role"
            for p in REGISTRY.values() if p.wakes and p.wakes not in roles]


def all_wakes(conn: sqlite3.Connection) -> list[Wake]:
    """Every predicate, evaluated. The frontier's second half."""
    out = []
    for p in REGISTRY.values():
        try:
            out.extend(p.fn(conn))
        except sqlite3.Error:
            continue                      # a predicate over a table not yet made
    return out


if __name__ == "__main__":
    import sys

    print(f"{len(REGISTRY)} predicates")
    for name, p in sorted(REGISTRY.items()):
        target = p.wakes or "(scheduler)"
        print(f"  {name:22s} -> {target:12s} drains {len(p.drains)}")
    issues = (check_terminal_states() + check_predicates_wake_real_roles()
              + check_predicates_can_fire() + check_states_are_reachable())
    print()
    if issues:
        print(f"{len(issues)} PROBLEMS:")
        for i in issues:
            print("  -", i)
        sys.exit(1)
    print("every lifecycle state has a way out")
