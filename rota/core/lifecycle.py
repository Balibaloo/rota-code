"""
A batch's runtime state, and the only place that writes it.

`batches.status` is not artefact content. Architect owns what a batch *is* — the
tickets in it, the constraints it touches — and that composition is immutable
once formed. Whether it is running, deferred or merged is something the
scheduler observes about the world, the same kind of fact as a claim or a
checkpoint, and it carries no judgement at all.

Keeping it on the `batches` row is a convenience: it belongs in its own table
alongside `claims` and `checkpoints`, and the reason it is not there yet is that
moving it touches every query in the scheduler for no behavioural gain. What
matters is that it has exactly one writer, which is this module. That is what
law 1 is protecting; the table layout is how the protection is implemented, not
what it is.

None of these transitions produce receipts. A receipt says a role decided
something, and nothing here is decided — starting the next batch is what the
schedule already said, and merging is what a passing verdict already meant.
"""
from __future__ import annotations

import sqlite3

from . import config


def start(conn: sqlite3.Connection, batch_id: str) -> None:
    """
    Dispatch. Only reachable through `batch_start`, which already refused if
    anything else was running.

    The worktree is made here, not by the Developer. Law 9 puts every decision
    about a worktree's life outside the role — a role that could create its own
    would be deciding where its work lives, which is a scheduling question
    wearing a tool. A deferred batch keeps the one it had, which is what makes
    resuming it a cold session in surviving work rather than a fresh start.
    """
    from . import worktrees

    conn.execute("UPDATE batches SET status = 'running' WHERE id = ?", (batch_id,))

    # A port range, from the scheduler and not from the batch: two batches must
    # never reach each other's ports and a batch cannot promise that, because it
    # cannot see the other one. Same reasoning that puts the worktree here.
    # Idempotent, so a resumed batch gets back the ports its tests name.
    from . import environments
    environments.reserve(conn, batch_id)

    # A folder with no repository gets one first: the principal's own trial
    # was a plain folder, and a batch there had nowhere to build.
    from . import scaffold
    root_row = conn.execute("SELECT value FROM config WHERE key = 'project_root'").fetchone()
    if root_row and (root_row["value"] or "").strip():
        from pathlib import Path as _Path
        scaffold.ensure_repo(_Path(root_row["value"].strip('"')))

    try:
        worktrees.create(conn, batch_id)
    except worktrees.WorktreeError as exc:
        # No git, or no project root: the batch still runs. Boot reconciles a
        # missing worktree the same way it reconciles a diverged one. The
        # reason is on record, because a swallowed one let a Developer write
        # on the project's master for 160 steps (tipsP, 2026-09-09).
        conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                     (f"worktree:{batch_id}", str(exc)[:300]))
    else:
        # Greenfield gets its floor before anyone works: the pyproject that
        # makes the harness's pytest invocation deterministic and the tests/
        # directory the Tester's paths need. A repository with its own test
        # configuration is left entirely alone.
        scaffold.ensure_floor(conn, batch_id)
        # The batch's own interpreter, with what the project declares. Best
        # effort: a failure is noted and the harness falls back to rota's own
        # interpreter, which is what it always ran.
        from . import provision
        row = conn.execute("SELECT worktree FROM batches WHERE id = ?",
                           (batch_id,)).fetchone()
        if row and row["worktree"]:
            _, note = provision.ensure_env(_Path(row["worktree"]))
            conn.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                (f"env:{batch_id}", note))
            # The repository's own tests join the batch. A merge must not
            # break what the tree already proved (tipsY, 2026-09-09).
            from . import harness
            harness.inherit(conn, batch_id, _Path(row["worktree"]))


def defer(conn: sqlite3.Connection, batch_id: str) -> None:
    """
    Preemption: a higher-priority batch arrived.

    The worktree and its commits survive — commit-first is what bounds the loss,
    because an uncommitted change never existed. The checkpoint does not: a
    deferred batch resumes cold, in the worktree it left behind.

    **The environment goes with the checkpoint, and the ports stay with the
    worktree.** That split is not a new decision; it is this one applied to a
    third thing. What survives a deferral is what cannot be recomputed, and
    everything a running process holds — a seeded database, a warm cache, a
    bound port — is reproducible by starting it again from the worktree. So the
    processes are checkpoint-like and die. The reservation is a number in a row,
    it holds nothing, and keeping it is what makes resuming *continuing*: the
    tests were written against those ports and they are still those ports.
    """
    from . import environments

    conn.execute("UPDATE batches SET status = 'deferred' WHERE id = ?", (batch_id,))
    conn.execute("UPDATE checkpoints SET valid = 0 WHERE batch_id = ?", (batch_id,))
    environments.teardown(conn, batch_id, release_ports=False)


def abandon(conn: sqlite3.Connection, batch_id: str) -> None:
    """
    Cancelled by ruling. The other terminal state, and the work did not happen.

    Deferral is a pause and this is not: an abandoned batch is never offered
    again, which is the whole difference -- `batch_start` re-offers deferred
    work the moment it is schedulable, so a batch whose item was revoked
    needed a state that is out of the game rather than waiting in it.

    The worktree stays. A ruling can be appealed, an abandoned diff is
    evidence about what was attempted, and deleting it would make cancelled
    work less inspectable than delivered work. The ports go: abandoned work
    has no further claim on a number in a row.
    """
    from . import environments

    conn.execute("UPDATE batches SET status = 'abandoned' WHERE id = ?",
                 (batch_id,))
    conn.execute("UPDATE checkpoints SET valid = 0 WHERE batch_id = ?",
                 (batch_id,))
    environments.teardown(conn, batch_id, release_ports=True)


def merge(conn: sqlite3.Connection, batch_id: str) -> None:
    """
    Delivered. The end of the line for a batch, and the only terminal state that
    means the work happened.

    The worktree goes; the branch stays. Deleting the branch would make a merged
    batch harder to inspect than an abandoned one.

    The environment goes too, and this time so does the reservation: a delivered
    batch has no further claim on a port, and holding one would walk the range
    forward for the lifetime of the project.
    """
    from . import environments, worktrees

    # The merge merges. A conflict leaves the batch deferred -- paused, its
    # worktree and commits intact -- rather than marked delivered.
    try:
        worktrees.integrate(conn, batch_id)
    except worktrees.WorktreeError as exc:
        if "not clean" in str(exc):
            conn.execute("UPDATE batches SET status = 'deferred' WHERE id = ?",
                         (batch_id,))
            raise
        # No git, no branch: the degraded mode the rest of the loop already
        # tolerates -- the batch is still delivered as far as the database
        # can know.
    conn.execute("UPDATE batches SET status = 'merged' WHERE id = ?", (batch_id,))
    environments.teardown(conn, batch_id, release_ports=True)
    try:
        worktrees.destroy(conn, batch_id)
    except worktrees.WorktreeError:
        pass


def head_of(conn: sqlite3.Connection, batch_id: str) -> str | None:
    row = conn.execute(
        "SELECT head_commit FROM batches WHERE id = ?", (batch_id,)).fetchone()
    return row["head_commit"] if row else None


def record_test_run(conn: sqlite3.Connection, run_id: str, batch_id: str,
                    test_id: str, result: str, attempt: int = 1,
                    commit_sha: str | None = None, output: str = "") -> None:
    """
    One test, one outcome.

    Mechanical, like recording an entry: the harness ran the test and the test
    said what it said. Routing that through a model would introduce a paraphrase
    risk over a boolean.
    """
    conn.execute(
        "INSERT OR REPLACE INTO test_runs "
        "(id, batch_id, test_id, commit_sha, result, attempt, output) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (run_id, batch_id, test_id,
         commit_sha if commit_sha is not None else head_of(conn, batch_id),
         result, attempt, output))


def next_attempt(conn: sqlite3.Connection, batch_id: str) -> int:
    row = conn.execute(
        "SELECT COALESCE(MAX(attempt), 0) + 1 AS n FROM test_runs WHERE batch_id = ?",
        (batch_id,)).fetchone()
    return row["n"]


# ---------------------------------------------------------------------------
# The merge gate
# ---------------------------------------------------------------------------

def needs_structural_review(conn: sqlite3.Connection, batch_id: str) -> bool:
    """
    Whether there is anything for Architect to check this batch against.

    Stated once, because the gate and the predicate were each deciding it
    separately and disagreed. `structural_review`'s docstring says "a diff whose
    grains intersect constraint bindings" and its query said no such thing: it
    fired for any batch with a passing verdict and no findings. `mergeable`
    then demanded a finding before merging. On a project with no constraints --
    which is every project until Architect has written a model -- those two
    combine into a deadlock, and it is a quiet one, because every part of it
    looks like it is working.

    The batch is finished. Tests pass, the verdict passes. `structural_review`
    fires, Architect is woken, and there is nothing it can legally do:
    `findings.find` requires a `constraint_id` and the column is `NOT NULL
    REFERENCES constraints(id)`, so with no constraints there is no finding to
    record. No finding lands, so the gate still says "no structural review yet",
    so the predicate fires again. The work never merges, and what eventually
    stops it is the livelock guard -- an escalation reporting a role that did
    its job perfectly.

    The rule is the schema's own, quoted from `constraint_bindings`: "a
    constraint with zero bindings is global -- missing bindings must always
    mean *always visible*, never *invisible*." So:

      * no constraints at all -> nothing to review, and nothing to wait for
      * any global constraint -> review, whatever the batch touches
      * otherwise -> review if the batch's touch set meets a binding

    Unknown touch set counts as needing review. Erring toward a review costs one
    session; erring away from it merges a change nobody checked.
    """
    n = conn.execute("SELECT COUNT(*) AS n FROM constraints").fetchone()["n"]
    if not n:
        return False

    globals_ = conn.execute(
        "SELECT COUNT(*) AS n FROM constraints c WHERE c.is_global = 1 "
        "   OR NOT EXISTS (SELECT 1 FROM constraint_bindings b "
        "                  WHERE b.constraint_id = c.id)").fetchone()["n"]
    if globals_:
        return True

    touched = conn.execute(
        "SELECT COUNT(*) AS n FROM batch_touch WHERE batch_id = ?",
        (batch_id,)).fetchone()["n"]
    if not touched:
        return True                 # nothing predicted; do not assume nothing hit

    return bool(conn.execute(
        "SELECT COUNT(*) AS n FROM batch_touch t "
        "JOIN constraint_bindings b ON b.grain = t.grain "
        "                          AND b.grain_kind = t.grain_kind "
        "WHERE t.batch_id = ? AND b.resolves = 1", (batch_id,)).fetchone()["n"])


def touch_set(conn: sqlite3.Connection, batch_id: str) -> dict:
    """
    One batch's predicted touch, read out for the seat.

    P4 (ruled R16/R17, 2026-09-03): the modification scope is put to the
    principal as a sense check -- never time, never effort -- and it has four
    parts, all of them mechanical. `expected` and `possible` are the
    Architect's own rows (`batches.annotate`: paths always, symbols only where
    confident). `unsurveyed` is the intersection with constraint zero -- the
    register's account of what nobody has read -- taken by path prefix,
    because an area covers the files under it. `commitments` are the other
    constraints bound to a touched grain: exact on the grain, or by the same
    prefix rule for a path. A global constraint is bound to nothing and so is
    everybody's business, not this batch's.
    """
    from ..onboarding.boot import ZERO

    row = conn.execute(
        "SELECT b.id AS id, b.item_id AS item_id, b.status AS status, "
        "       i.text AS item_text FROM batches b "
        "LEFT JOIN items i ON i.id = b.item_id WHERE b.id = ?",
        (batch_id,)).fetchone()
    if row is None:
        return {}
    touch = [dict(t) for t in conn.execute(
        "SELECT grain, grain_kind, confidence FROM batch_touch "
        "WHERE batch_id = ? ORDER BY grain", (batch_id,))]
    paths = [t["grain"] for t in touch if t["grain_kind"] == "path"]

    def under(path: str, area: str) -> bool:
        area = area.rstrip("/")
        return path == area or path.startswith(area + "/")

    unsurveyed = sorted({
        b["grain"] for b in conn.execute(
            "SELECT grain FROM constraint_bindings "
            "WHERE constraint_id = ? AND resolves = 1", (ZERO,))
        if any(under(p, b["grain"]) for p in paths)})

    commitments: list[dict] = []
    for b in conn.execute(
            "SELECT b.constraint_id AS cid, b.grain AS grain, "
            "       b.grain_kind AS kind, c.headline AS headline "
            "FROM constraint_bindings b "
            "JOIN constraints c ON c.id = b.constraint_id "
            "WHERE b.constraint_id != ? AND b.resolves = 1 "
            "ORDER BY b.constraint_id, b.grain", (ZERO,)):
        hit = any(t["grain"] == b["grain"] and t["grain_kind"] == b["kind"]
                  for t in touch)
        if not hit and b["kind"] == "path":
            hit = any(under(p, b["grain"]) for p in paths)
        if hit:
            commitments.append({"id": b["cid"], "headline": b["headline"],
                                "bound_to": b["grain"]})

    return {
        "batch": row["id"], "status": row["status"],
        "item": {"id": row["item_id"], "text": row["item_text"]},
        "expected": [t["grain"] for t in touch if t["confidence"] == "expected"],
        "possible": [t["grain"] for t in touch if t["confidence"] != "expected"],
        "unsurveyed": unsurveyed,
        "commitments": commitments,
    }


def touch_notes(conn: sqlite3.Connection, status: str | None = "open") -> set[str]:
    """
    The presents that are touch notes: a `present` carrying a batch's ref.

    Derived, not declared. A message carries no flag saying which kind of
    present it is, and the one table a touch note's refs name and a signoff's
    never do is `batches`. The gates that ask "is anything open to the
    principal" -- `tick_signoff`, `tick_agenda`, `observed_entries` -- set
    these aside, because a note nobody has to answer (R7: non-blocking) must
    not freeze a gate that waits on a ruling.
    """
    from .db import refs_of

    batches = {r["id"] for r in conn.execute("SELECT id FROM batches")}
    if not batches:
        return set()
    where = "verb = 'present'" + (" AND status = ?" if status else "")
    args = (status,) if status else ()
    return {r["id"] for r in conn.execute(
                f"SELECT id, body_refs FROM messages WHERE {where}", args)
            if batches & set(refs_of(r["body_refs"]))}


def mergeable(conn: sqlite3.Connection, batch_id: str) -> str | None:
    """
    Why this batch cannot merge, or None if it can.

    Three conditions, and the order is the review order: the harness passed, the
    Critic passed, the Architect found nothing violated. Returning the *reason*
    rather than a boolean is what lets the loop say why a batch is sitting there
    instead of leaving it to be inferred from its absence.
    """
    # Every question is about *this* commit. A verdict against an older diff is
    # not evidence about the one on disk, and treating it as such would merge a
    # change nobody judged — the precise failure the commit stamps exist for.
    head = head_of(conn, batch_id)
    if head is None:
        return "nothing committed"

    verdict = conn.execute(
        "SELECT result FROM verdicts WHERE batch_id = ? AND commit_sha = ? "
        "ORDER BY rowid DESC LIMIT 1", (batch_id, head)).fetchone()
    if not verdict:
        return "no verdict"
    if verdict["result"] != "pass":
        return f"verdict {verdict['result']}"

    failing = conn.execute(
        "SELECT COUNT(*) AS n FROM test_runs "
        "WHERE batch_id = ? AND commit_sha = ? AND result != 'pass'",
        (batch_id, head)).fetchone()["n"]
    if failing:
        return f"{failing} test(s) not passing"

    reviewed = conn.execute(
        "SELECT COUNT(*) AS n FROM findings WHERE batch_id = ? AND commit_sha = ?",
        (batch_id, head)).fetchone()["n"]
    if not reviewed and needs_structural_review(conn, batch_id):
        return "no structural review yet"

    violated = conn.execute(
        "SELECT COUNT(*) AS n FROM findings WHERE batch_id = ? AND commit_sha = ? "
        "  AND status = 'violated'", (batch_id, head)).fetchone()["n"]
    if violated:
        return f"{violated} constraint(s) violated"

    if config.get(conn, "merge_gate") == "review":
        return "waiting on the principal's review"

    return None
