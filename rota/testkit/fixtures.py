"""
Fixture loader and case runner.

The shape every role test takes: **seed rows -> inject message -> run session ->
assert on deltas.** This module is the machinery for that, and it deliberately
arrives before any role exists, because it needs only the schema — which also
makes it the tool for inspecting anything the scheduler does.

Case format (YAML, per TESTS.md §5):

    id: V2
    tier: T1
    role: gatekeeper
    runs: 5
    pass: 4
    fixture:
      decisions: [{id: R1, text: "deletion rejected: billing history must survive"}]
    inbound: {from: liaison, to: gatekeeper, verb: brief, body_refs: [s2, s3]}
    expect:
      writes:
        items: [{kind: scope, count: ">=1"}]
      messages: []
      calls: [transcript.quote]
    forbidden:
      writes: [glossary_terms, constraints]
      recipients: [principal, developer, critic]
      calls: [code.write]
    same_session: [items, decisions]

`forbidden:` is not optional garnish. Most laws here are prohibitions, and a case
with no forbidden block is presumed incomplete — so an empty one must be written
deliberately rather than omitted.
"""
from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..core.db import ARTEFACT_TABLES, init_db
from ..llm.llm import Pins
from ..core.runner import RunOutcome, run_session
from ..core.scheduler import Wake


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

def seed(conn: sqlite3.Connection, fixture: dict[str, list[dict]]) -> None:
    """
    Insert fixture rows verbatim.

    Fixtures should be tiny — three to five rows, turning on exactly one
    judgement. A nine-billion-parameter model will not fail a structural
    assertion, but it will drown in twenty statements with three plausible
    readings, and then the pass rate measures the fixture rather than the role.
    """
    for table, rows in fixture.items():
        for row in rows:
            payload = {k: _encode(v) for k, v in row.items()}
            cols = ", ".join(payload)
            marks = ", ".join("?" for _ in payload)
            conn.execute(
                f"INSERT INTO {table} ({cols}) VALUES ({marks})",
                list(payload.values()),
            )


def _encode(value: Any) -> Any:
    return json.dumps(value) if isinstance(value, (list, dict)) else value


def load_case(path: str | Path) -> dict:
    """Parse a case file. YAML if available, else JSON."""
    text = Path(path).read_text(encoding="utf-8")
    if str(path).endswith((".yaml", ".yml")):
        try:
            import yaml
            return yaml.safe_load(text)
        except ImportError as exc:                      # pragma: no cover
            raise RuntimeError("PyYAML needed for .yaml cases") from exc
    return json.loads(text)


# ---------------------------------------------------------------------------
# Delta capture
# ---------------------------------------------------------------------------

@dataclass
class Delta:
    """What one session changed. The assertion target for every role test."""
    session_id: str
    committed: bool
    writes: dict[str, list[str]] = field(default_factory=dict)
    messages: list[dict] = field(default_factory=list)
    tool_calls: list[str] = field(default_factory=list)
    versions_moved: dict[str, int] = field(default_factory=dict)

    def tables_written(self) -> set[str]:
        return set(self.writes)

    def recipients(self) -> set[str]:
        return {m["to_role"] for m in self.messages}


def capture(conn: sqlite3.Connection, session_id: str,
            versions_before: dict[str, int]) -> Delta:
    writes: dict[str, list[str]] = {}
    for r in conn.execute(
        "SELECT table_name, row_id FROM receipts WHERE session_id = ? ORDER BY table_name",
        (session_id,),
    ):
        writes.setdefault(r["table_name"], []).append(r["row_id"])

    messages = [dict(r) for r in conn.execute(
        "SELECT id, to_role, verb, body_refs, cause_id FROM messages "
        "WHERE id IN (SELECT id FROM messages WHERE from_role = "
        "  (SELECT role FROM sessions WHERE id = ?)) ORDER BY seq", (session_id,),
    )]

    tool_calls = [r["fn"] for r in conn.execute(
        "SELECT fn FROM tool_calls WHERE session_id = ? ORDER BY seq", (session_id,))]

    committed = bool(conn.execute(
        "SELECT committed FROM sessions WHERE id = ?", (session_id,)).fetchone() or [0])

    moved = {}
    for r in conn.execute("SELECT table_name, version FROM artefact_versions"):
        before = versions_before.get(r["table_name"], 0)
        if r["version"] != before:
            moved[r["table_name"]] = r["version"] - before

    return Delta(session_id=session_id, committed=committed, writes=writes,
                 messages=messages, tool_calls=tool_calls, versions_moved=moved)


def snapshot_versions(conn: sqlite3.Connection) -> dict[str, int]:
    return {r["table_name"]: r["version"]
            for r in conn.execute("SELECT table_name, version FROM artefact_versions")}


# ---------------------------------------------------------------------------
# Assertions
# ---------------------------------------------------------------------------

_COUNT = re.compile(r"^(>=|<=|==|>|<)?\s*(\d+)$")


def _count_ok(actual: int, spec: Any) -> bool:
    if spec is None:
        return actual > 0
    m = _COUNT.match(str(spec).strip())
    if not m:
        return False
    op, n = m.group(1) or "==", int(m.group(2))
    return {
        "==": actual == n, ">=": actual >= n, "<=": actual <= n,
        ">": actual > n, "<": actual < n,
    }[op]


def check(case: dict, delta: Delta) -> list[str]:
    """
    Structural assertions only. Never on prose.

    Which tables changed, which rows appeared, who received which message type,
    what refs a row carries — those are checkable. Whether the wording is good is
    not, and pretending otherwise is how a suite starts measuring the model's
    prose style instead of the law.
    """
    problems: list[str] = []
    expect = case.get("expect", {})
    forbidden = case.get("forbidden", {})

    # Several modes have two right answers and no third. Gatekeeper handed a
    # refactor proposal either asserts it as an item or authors a decision
    # refusing it; what it must not do is nothing, because Architect is blocked
    # and will not ask twice. Written as two separate cases that would be two
    # fixtures pretending to be different situations, so the alternation lives
    # here instead: at least one branch must hold, and "neither" is the failure
    # the case exists to catch.
    branches = expect.get("any_of") or []
    if branches:
        if all(check({"expect": b, "forbidden": {}}, delta) for b in branches):
            problems.append(
                "none of the permitted answers was given; "
                f"wrote {sorted(delta.writes)}, sent "
                f"{[(m['to_role'], m['verb']) for m in delta.messages]}")

    for table, specs in (expect.get("writes") or {}).items():
        rows = delta.writes.get(table, [])
        for spec in (specs if isinstance(specs, list) else [specs]):
            want = spec.get("count") if isinstance(spec, dict) else None
            if not _count_ok(len(rows), want):
                problems.append(
                    f"expected writes to {table} ({want or '>0'}), got {len(rows)}")

    for spec in expect.get("messages") or []:
        matches = [
            m for m in delta.messages
            if m["to_role"] == spec.get("to", m["to_role"])
            and m["verb"] == spec.get("verb", m["verb"])
        ]
        if not _count_ok(len(matches), spec.get("count")):
            problems.append(f"expected message {spec}, got {len(matches)} match(es)")
        for m in matches:
            need = set(spec.get("refs_include") or [])
            if need and not need <= set(json.loads(m["body_refs"])):
                problems.append(f"message {m['id']} missing refs {need}")

    # A judgement is only as good as what it was grounded in. Two thirds of the
    # L1 obligation set are reads — `code.read`, `criteria.load`, `model.load` —
    # and none of them deserves a case of its own, because reading is a means,
    # never an end. They ride here instead: a verdict emitted without loading the
    # criterion it judges against is a guess that happened to be checkable.
    called = set(delta.tool_calls)
    for fn in expect.get("calls") or []:
        if fn not in called:
            problems.append(f"expected a call to {fn}; called {sorted(called)}")

    # --- the negative half ---------------------------------------------------
    if "forbidden" not in case:
        problems.append("case declares no `forbidden:` block and is presumed incomplete")

    for table in forbidden.get("writes") or []:
        if table in delta.writes:
            problems.append(f"forbidden write to {table}: {delta.writes[table]}")

    for role in forbidden.get("recipients") or []:
        if role in delta.recipients():
            problems.append(f"forbidden message to {role}")

    # Verb-granular, because role-granular could not say what several cases
    # need. Liaison confirming a segmentation to the principal is required;
    # Liaison *clarifying* to them unprompted is the failure. Forbidding the
    # recipient forbids both, and a case that cannot separate them either
    # passes a real fault or fails correct behaviour.
    for spec in forbidden.get("messages") or []:
        for m in delta.messages:
            if (m["to_role"] == spec.get("to", m["to_role"])
                    and m["verb"] == spec.get("verb", m["verb"])):
                problems.append(
                    f"forbidden message {m['verb']} to {m['to_role']}")

    for fn in forbidden.get("calls") or []:
        if fn in called:
            problems.append(f"forbidden call to {fn}")

    for table in forbidden.get("versions") or []:
        if table in delta.versions_moved:
            problems.append(f"forbidden version bump on {table}")

    if expect.get("messages") == [] and delta.messages:
        problems.append(f"expected no messages, got {[m['verb'] for m in delta.messages]}")

    return problems


def check_same_session(conn: sqlite3.Connection, tables: list[str],
                       session_id: str) -> list[str]:
    """Law 11: several laws are *about* what happens inside a single commit."""
    written = {r["table_name"] for r in conn.execute(
        "SELECT DISTINCT table_name FROM receipts WHERE session_id = ?", (session_id,))}
    return [f"{t} not written in the same session" for t in tables if t not in written]


# ---------------------------------------------------------------------------
# Running a case
# ---------------------------------------------------------------------------

@dataclass
class CaseResult:
    case_id: str
    run: int
    passed: bool
    problems: list[str] = field(default_factory=list)
    delta: Delta | None = None
    outcome: RunOutcome | None = None


def _with_repo(conn, case: dict, db_path: Path):
    """
    A real checkout, a worktree for the batch, and a diff to judge.

    Critic reads a diff; Architect reads source; Developer writes files. A case
    for any of them against a database with no repository is a case where the
    role correctly declines to act, and reads as a failure. The first Critic
    cases failed exactly that way — no worktree, so `code.read` returned an
    empty diff, and refusing to judge what it cannot see is the right answer.
    """
    from . import gitfixture

    spec = case["repo"]
    root = Path(db_path).parent
    repo = gitfixture.make(root, name=f"{case.get('id', 'case')}_repo")
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
                 "('project_root', ?)", (str(repo.root),))

    batch_id = spec.get("batch") if isinstance(spec, dict) else None
    if batch_id:
        tree = repo.worktree(batch_id)
        conn.execute("UPDATE batches SET worktree = ? WHERE id = ?",
                     (str(tree), batch_id))
        for rel, body in (spec.get("edit") or {}).items():
            repo.edit(tree, rel, body)
        if spec.get("edit"):
            sha = repo.commit_in(tree, spec.get("message", "the batch's work"))
            conn.execute("UPDATE batches SET head_commit = ? WHERE id = ?",
                         (sha, batch_id))
    return repo


def mode_of(case: dict) -> str:
    """
    Which prompt piece the case exercises.

    Normally derivable — a message case is keyed by its verb, a tick case by the
    tick — and `prompt:` exists for the one shape that is not. Liaison's
    `verdict_signoff` is the principal's `verdict` verb keyed by what it answers,
    so deriving it from the verb alone loads the ratification prompt and grades
    the wrong mode. Writing that out is better than a case that silently tests
    something other than what its id says.
    """
    if case.get("prompt"):
        return case["prompt"]
    return (case.get("inbound") or {}).get("verb") or case.get("tick", "")


def run_case(case: dict, db_path: str | Path, backend, *, pins: Pins | None = None,
             instructions: str = "", run_no: int = 1) -> CaseResult:
    conn = init_db(db_path)
    seed(conn, case.get("fixture") or {})
    repo = _with_repo(conn, case, Path(db_path)) if case.get("repo") else None

    inbound = case.get("inbound") or {}
    msg_id = inbound.get("id", "m_in")
    if inbound:
        conn.execute(
            "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
            "body_refs, cause_id, seq) VALUES (?, ?, ?, ?, ?, ?, ?, 99)",
            (msg_id, inbound.get("thread", "t1"), inbound["from"], inbound["to"],
             inbound["verb"], json.dumps(inbound.get("body_refs", [])),
             inbound.get("cause")),
        )

    before = snapshot_versions(conn)
    wake = Wake(role=case["role"], kind="message",
                message_id=msg_id if inbound else None,
                refs=tuple(case.get("refs") or ()),
                detail=inbound.get("verb", case.get("tick", "")))

    # The same resolution the loop does, for the same reason: a role that works
    # in a worktree needs to be told which one, and it is never the role's to
    # choose. Without this a Developer case ran with no batch and could not
    # write a line of the code it was woken for.
    from ..core.loop import _batch_of

    outcome = run_session(conn, wake, backend=backend, pins=pins,
                          instructions=instructions,
                          batch_id=_batch_of(conn, wake),
                          mode=case.get("mode", "normal"))
    delta = capture(conn, outcome.session_id, before)

    problems = check(case, delta)
    if case.get("same_session"):
        problems += check_same_session(conn, case["same_session"], outcome.session_id)
    if not outcome.committed and case.get("expect_commit", True):
        problems.append(f"session did not commit: {outcome.errors}")

    if repo is not None:
        from . import gitfixture
        gitfixture.cleanup(repo)

    return CaseResult(case_id=case.get("id", "?"), run=run_no,
                      passed=not problems, problems=problems,
                      delta=delta, outcome=outcome)


def run_sampled(case: dict, tmpdir: Path, backend_factory, *, pins: Pins | None = None,
                instructions: str = "") -> tuple[int, int, list[CaseResult]]:
    """
    Run a case `runs` times and compare against its `pass` threshold.

    LLM output is stochastic; the harness treats that as a measured quantity
    rather than an excuse. A case that passed 5/5 for weeks and now passes 3/5 is
    a prompt regression signal, which is why the count is returned rather than a
    bare boolean.
    """
    runs = int(case.get("runs", 1))
    threshold = int(case.get("pass", runs))
    results = []
    for i in range(1, runs + 1):
        results.append(run_case(case, tmpdir / f"{case.get('id','case')}_{i}.db",
                                backend_factory(), pins=pins,
                                instructions=instructions, run_no=i))
    passed = sum(1 for r in results if r.passed)
    return passed, threshold, results
