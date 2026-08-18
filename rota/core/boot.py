"""
Boot. Not special — after the reaps, "continue" is the same loop steady state runs.

There is nothing to resume, because the frontier *is* the state: reconstructing it
is the entire recovery. That is what makes the scheduler disposable.

Seven steps, in this order. Assertions come before state is touched: if the code
and the graph disagree, do not start.

  0. graph assertions        namespace exports == edges; contacts == declared
  1. folder present/absent   boot vs onboarding initiation
  2. reap stale claims       a session live when the process died still holds one
  3. reap orphan processes   spawned runtimes outlive the session that made them
  4. reconcile worktrees     git commits are outside the SQLite transaction
  5. sweep checkpoints       version stamps vs artefact_versions
  6. skip quarantined        a poison message must not resume its loop
  7. continue                enter the ordinary scheduler loop
"""
from __future__ import annotations

import os
import signal
import sqlite3
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import config
from ..design import graph as graph_mod
from .db import init_db
from .scheduler import sweep_checkpoints


@dataclass
class BootReport:
    onboarding: bool = False
    claims_reaped: list[str] = field(default_factory=list)
    processes_reaped: list[int] = field(default_factory=list)
    worktrees_reconciled: list[tuple[str, str, str]] = field(default_factory=list)
    checkpoints_invalidated: list[str] = field(default_factory=list)
    quarantined: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"onboarding={self.onboarding} claims={len(self.claims_reaped)} "
            f"procs={len(self.processes_reaped)} worktrees={len(self.worktrees_reconciled)} "
            f"checkpoints={len(self.checkpoints_invalidated)} "
            f"quarantined={len(self.quarantined)}"
        )


def state_dir(project_root: str | Path) -> Path:
    """All framework state lives in a subfolder of the project the tool opens in.

    The tool attaches to a project; it is never pointed at a repo from outside.
    `.architect/` belongs to the previous generation of this idea and is left
    alone.
    """
    return Path(project_root) / ".rota"


def reap_claims(conn: sqlite3.Connection) -> list[str]:
    """
    A session that was live when the process died still holds its claim.

    "The session never happened" is true for rows — it rolled back — but not for
    the claim, which was written before the session ran. Any claim whose session
    never committed is stale by definition.
    """
    rows = conn.execute(
        "SELECT c.role AS role, c.session_id AS sid FROM claims c "
        "LEFT JOIN sessions s ON s.id = c.session_id "
        "LEFT JOIN checkpoints k ON k.session_id = c.session_id "
        "WHERE (s.id IS NULL OR s.committed = 0) AND k.session_id IS NULL"
    ).fetchall()
    reaped = []
    for r in rows:
        conn.execute("DELETE FROM claims WHERE role = ?", (r["role"],))
        reaped.append(f"{r['role']}:{r['sid']}")
    return reaped


def reap_processes(conn: sqlite3.Connection, kill=True) -> list[int]:
    """
    Processes spawned by a batch's environment outlive the session that made them.

    §9 forbids half-dead environments: on restart, anything recorded here is an
    orphan.

    **It kills only what it can prove is ours.** This used to SIGTERM every
    recorded pid, and a pid is not an identity -- the operating system reuses
    them, so after a crash and a reboot a recorded pid overwhelmingly belongs to
    something else. All that stood between that and killing a stranger was an
    `except` treating "not ours" and "already gone" as one outcome, which is the
    one pair it could not afford to conflate.

    `environments.is_still_ours` wants two facts, the pid and the start time the
    OS reports for it now, on the rule `worktrees.py` states before removing a
    directory: either fact alone can be satisfied by an accident.

    A row it cannot claim is dropped and *reported*, never killed. A process
    left running is recoverable and visible; an unidentified one killed is
    neither.
    """
    from . import environments

    reaped, unclaimed = [], []
    for r in conn.execute("SELECT pid FROM runtime_processes").fetchall():
        pid = r["pid"]
        ours = environments.is_still_ours(conn, pid)
        if kill and ours:
            try:
                os.kill(pid, signal.SIGTERM)
            except (ProcessLookupError, PermissionError, OSError):
                pass                  # it went away between the check and here
        conn.execute("DELETE FROM runtime_processes WHERE pid = ?", (pid,))
        (reaped if ours else unclaimed).append(pid)

    if unclaimed:
        # Reported, not raised: boot has to finish. A number here is what makes
        # an orphan something somebody can act on rather than one nobody hears.
        print(f"boot: {len(unclaimed)} recorded process(es) could not be "
              f"identified and were left alone: {unclaimed}", flush=True)
    return reaped


def _git_head(worktree: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", worktree, "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=15,
        )
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None


def reconcile_worktrees(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    """
    Compare each batch's recorded head_commit against its worktree's real HEAD.

    Git commits are outside the transaction, so a session that committed code and
    then died leaves the worktree ahead of the database. This is not corruption:
    the batch's trigger is still on the frontier, so the Developer wakes again.
    What it must not do is wake *blind* — a cold role reads criteria and probes
    code; it has no reason to run `git log` and would happily duplicate work.
    So the divergence is recorded and handed to it in the wake payload.
    """
    diverged = []
    for r in conn.execute(
        "SELECT id, worktree, head_commit FROM batches "
        "WHERE worktree IS NOT NULL AND status IN ('running','deferred')"
    ):
        actual = _git_head(r["worktree"])
        if actual and actual != (r["head_commit"] or ""):
            diverged.append((r["id"], r["head_commit"] or "<none>", actual))
    return diverged


def quarantine_exhausted(conn: sqlite3.Connection,
                         cap: int | None = None) -> list[str]:
    """
    A message past its attempt cap stops being schedulable.

    Semantic failures resolve; these are infrastructure ones — model eviction
    mid-session, a tool call that hangs, a stream that dies after retries are
    exhausted. Without a bound the scheduler wakes the same role with the same
    message forever, and across restarts too.
    """
    if cap is None:
        cap = config.get(conn, "message_attempt_cap")
    rows = conn.execute(
        "SELECT id FROM messages WHERE status = 'open' AND attempts >= ?", (cap,)
    ).fetchall()
    ids = [r["id"] for r in rows]
    for mid in ids:
        conn.execute("UPDATE messages SET status = 'quarantined' WHERE id = ?", (mid,))
    return ids


def boot(project_root: str | Path, *, kill_processes: bool = True,
         attempt_cap: int | None = None) -> tuple[sqlite3.Connection, BootReport]:
    """Run the full sequence and hand back a live connection."""
    report = BootReport()

    # 0. Graph assertions, before any state is touched.
    graph_mod.assert_consistent()

    # 1. Folder present -> boot; absent -> onboarding initiation.
    sdir = state_dir(project_root)
    report.onboarding = not sdir.exists()
    sdir.mkdir(parents=True, exist_ok=True)
    conn = init_db(sdir / "rota.db")

    # 2-6.
    report.claims_reaped = reap_claims(conn)
    report.processes_reaped = reap_processes(conn, kill=kill_processes)
    report.worktrees_reconciled = reconcile_worktrees(conn)
    report.checkpoints_invalidated = sweep_checkpoints(conn)
    report.quarantined = quarantine_exhausted(conn, attempt_cap)

    # 7. continue — the caller enters the ordinary loop. There is no separate
    #    resume path to be special about.
    return conn, report
