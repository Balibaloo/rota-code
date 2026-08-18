"""
Environments: the first thing here that outlives the session that made it.

Everything else in this system is a pure function -- wake, act, commit, end. A
process is not. It is still running when the session that started it has been
collected, it holds a port another batch will want, and it can survive the crash
of the thing that was meant to clean it up. That asymmetry is the whole of why
this module is careful in a way the rest of the codebase does not need to be.

**Nothing here is durable, and that is the design rather than a limitation.**
Law 9 already splits a batch's belongings into durable product and derived
state: the worktree and its commits survive a deferral because they cannot be
recomputed, and the checkpoint does not because it can. A running process is
derived state by that test -- a seeded database, a warm cache, a bound port are
all reproducible by starting it again from the worktree. So an environment is a
checkpoint, not a worktree, and the ruling already existed.

What survives is the **reservation**: `batches.port_base`, a number in a row.
Re-spawning onto the same ports is what makes resuming a deferred batch
continuing rather than starting over, and it costs nothing to hold.

**Stateful projects.** The state a project under test needs -- a database with
tables in it, a queue, a seeded fixture -- lives *inside* the environment and is
built at spawn. It is never carried across a teardown, and a test that only
passes because of state a previous run left behind is precisely the failure this
system exists to prevent: it reports as coverage and is evidence about nothing.
The line is ownership, not proximity. A database this batch started is inside; a
database the whole machine shares was running before the batch and will be
running after, and connecting to one is not owning it.

**Nothing stops what it did not start.** Proof of ownership is two independent
facts, never one, because either alone can be satisfied by an accident -- the
same rule `worktrees.py` states before removing a directory. Here it is the pid
*and* the process start time: the OS reuses pids, so a recorded pid after a
reboot is very likely a stranger, and a pid alone is a licence to kill one.
"""
from __future__ import annotations

import sqlite3

# How many ports one batch may hold. A web server, a database and something to
# talk to them is three; five leaves room without pretending to know.
PORTS_PER_BATCH = 5

# Where the range starts. Above the ephemeral range most systems hand out, below
# anything a person is likely to have chosen by hand.
FIRST_PORT = 41000


class EnvironmentError_(RuntimeError):
    """Refused: the request was for something this system does not own."""


# ---------------------------------------------------------------------------
# Reservation
# ---------------------------------------------------------------------------

def reserve(conn: sqlite3.Connection, batch_id: str) -> int:
    """
    Give this batch a port range, and give it the same one every time.

    The scheduler assigns it, not the batch: two batches must never reach each
    other's ports, and a batch cannot guarantee that because it cannot see the
    other one. This is the reasoning that already puts the worktree outside the
    role's hands.

    Idempotent on purpose. A deferred batch keeps its reservation, so resuming
    re-spawns onto the ports its tests were written against.
    """
    row = conn.execute(
        "SELECT port_base FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if row is None:
        raise EnvironmentError_(f"no batch {batch_id!r} to reserve ports for")
    if row["port_base"]:
        return int(row["port_base"])

    taken = {int(r["port_base"]) for r in conn.execute(
        "SELECT port_base FROM batches WHERE port_base IS NOT NULL")}
    base = FIRST_PORT
    while base in taken:
        base += PORTS_PER_BATCH
    conn.execute("UPDATE batches SET port_base = ? WHERE id = ?", (base, batch_id))
    return base


def ports_of(conn: sqlite3.Connection, batch_id: str) -> list[int]:
    """The range, as the numbers a session may actually bind."""
    row = conn.execute(
        "SELECT port_base FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if row is None or not row["port_base"]:
        return []
    base = int(row["port_base"])
    return list(range(base, base + PORTS_PER_BATCH))


def release(conn: sqlite3.Connection, batch_id: str) -> None:
    """
    Hand the range back, on a terminal state only.

    Not on deferral. A deferred batch has not finished and its tests still name
    those ports; releasing them there would make resuming a different operation
    from continuing, which is the distinction Law 9 draws about the worktree.
    """
    conn.execute("UPDATE batches SET port_base = NULL WHERE id = ?", (batch_id,))


# ---------------------------------------------------------------------------
# Ownership
# ---------------------------------------------------------------------------

def start_time_of(pid: int) -> str | None:
    """
    When the OS says this process started, or None if it cannot be asked.

    The second of the two facts. `psutil` is not a dependency here and this must
    work without it, so it shells out to what each platform ships: `wmic`-free
    PowerShell on Windows, `ps -o lstart=` elsewhere. A `None` means *unknown*,
    never *matches* -- an identity check that passes when it cannot check is not
    a check, and this one guards a kill.
    """
    import subprocess
    import sys

    try:
        if sys.platform == "win32":
            out = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"(Get-Process -Id {int(pid)} -ErrorAction Stop).StartTime.Ticks"],
                capture_output=True, text=True, timeout=10)
        else:
            out = subprocess.run(
                ["ps", "-o", "lstart=", "-p", str(int(pid))],
                capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None                       # gone, or not visible to us
    return (out.stdout or "").strip() or None


def is_still_ours(conn: sqlite3.Connection, pid: int) -> bool:
    """
    Whether the process at `pid` is the one we recorded.

    Two facts, and both must hold. The pid is on file, *and* the process
    currently at that pid started when the one we recorded started. A pid is
    reused by the operating system, so after a crash and a reboot a recorded pid
    is overwhelmingly likely to belong to something else -- and the code this
    replaces sent that stranger a SIGTERM, guarded only by an `except` that
    could not tell "not ours" from "already gone".

    Unknown is not ownership. If the start time was never recorded, or cannot be
    read now, the answer is no: refusing to kill something we cannot identify
    leaves a process running, and killing something we cannot identify is
    unbounded. Only one of those two is recoverable, and boot says which are
    left.
    """
    row = conn.execute(
        "SELECT started_at FROM runtime_processes WHERE pid = ?", (pid,)).fetchone()
    if row is None or not row["started_at"]:
        return False
    now = start_time_of(pid)
    return bool(now) and now == row["started_at"]


def record(conn: sqlite3.Connection, batch_id: str, pid: int,
           command: str, started_at: str | None = None) -> None:
    """
    Note a process as ours, with both facts or neither.

    A row with no `started_at` can never be claimed later -- `is_still_ours`
    refuses it -- so recording one is recording something this system will not
    stop. That is honest rather than convenient: boot reports it as
    unidentifiable instead of killing a stranger on its behalf.
    """
    conn.execute(
        "INSERT OR REPLACE INTO runtime_processes (pid, batch_id, command, "
        "started_at) VALUES (?, ?, ?, ?)",
        (int(pid), batch_id, command,
         started_at if started_at is not None else start_time_of(pid)))


def forget(conn: sqlite3.Connection, pid: int) -> None:
    conn.execute("DELETE FROM runtime_processes WHERE pid = ?", (int(pid),))


# ---------------------------------------------------------------------------
# Spawn and teardown
# ---------------------------------------------------------------------------

def spawn(conn: sqlite3.Connection, batch_id: str, command: list[str],
          cwd: str | None = None) -> int:
    """
    Start a process inside this batch's environment, and record it before it can
    be lost.

    `command` is a list and never a string: a string means a shell, a shell
    means quoting, and quoting means the one place in this system that starts
    processes would be the one place with an injection surface. There is no
    `shell=True` here and there is no argument that would enable one.

    **Recorded first, then returned.** The window between "it is running" and
    "we know it is running" is the whole of how an orphan is made, and it is
    made by crashing inside it. The row is written with both facts before this
    function hands the pid back, so a crash anywhere after `Popen` leaves a
    process boot can identify and stop.

    `PORT_BASE` reaches the child through its environment because a port range
    is a fact about where it may listen, not a decision it gets to make -- the
    same reasoning as `batch_id` on a wake.
    """
    import os
    import subprocess

    if isinstance(command, str) or not command:
        raise EnvironmentError_(
            "command is a list of arguments -- a string would need a shell, and "
            "a shell here would be the one injection surface in the system")

    base = reserve(conn, batch_id)
    worktree = conn.execute(
        "SELECT worktree FROM batches WHERE id = ?", (batch_id,)).fetchone()
    root = cwd or (worktree["worktree"] if worktree else None)

    child = subprocess.Popen(
        list(command), cwd=root,
        env={**os.environ,
             "ROTA_PORT_BASE": str(base),
             "ROTA_BATCH": batch_id},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    record(conn, batch_id, child.pid, " ".join(command))
    return child.pid


def teardown(conn: sqlite3.Connection, batch_id: str, *,
             release_ports: bool = False) -> list[int]:
    """
    Stop this batch's processes. Nothing else, and nothing it cannot claim.

    `release_ports` is the whole difference between a deferral and an ending,
    and it is the caller's to say because only the caller knows which happened.
    A deferred batch keeps its range: its tests name those ports, and handing
    them to somebody else would make resuming a different operation from
    continuing. A merged or abandoned batch has no further claim on anything.

    Returns the pids actually stopped. A row it cannot identify is dropped and
    left alone, exactly as at boot -- the difference between the two is only
    when they run, never how careful they are.
    """
    import os
    import signal

    stopped = []
    rows = conn.execute(
        "SELECT pid FROM runtime_processes WHERE batch_id = ?",
        (batch_id,)).fetchall()
    for r in rows:
        pid = r["pid"]
        if is_still_ours(conn, pid):
            try:
                os.kill(pid, getattr(signal, "SIGTERM", 15))
                stopped.append(pid)
            except (ProcessLookupError, PermissionError, OSError):
                pass                  # gone between the check and the signal
        forget(conn, pid)

    if release_ports:
        release(conn, batch_id)
    return stopped
