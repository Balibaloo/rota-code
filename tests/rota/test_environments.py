"""
Environments — the reservation, and the two facts that make a kill safe.

Nothing here spawns a process. That is deliberate and it is the build order:
the reaper was written before the spawner, which is why nothing has been
orphaned yet, and these are the two pieces that can be finished without
changing that.
"""
from __future__ import annotations

import os
import pathlib

import pytest

from rota.core import environments as env
from rota.core.db import init_db


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "env.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance) "
                 "VALUES ('i1','x','in_scope','decided')")
    for b in ("b1", "b2", "b3"):
        conn.execute("INSERT INTO batches (id, item_id) VALUES (?, 'i1')", (b,))
    return conn


# ---------------------------------------------------------------------------
# Reservation
# ---------------------------------------------------------------------------

def test_two_batches_never_share_a_port(db):
    """
    The reason allocation is the scheduler's and not the batch's: a batch
    cannot see the other one, so it cannot promise this.
    """
    a, b = env.reserve(db, "b1"), env.reserve(db, "b2")
    assert a != b
    assert not set(env.ports_of(db, "b1")) & set(env.ports_of(db, "b2"))


def test_a_reservation_is_the_same_every_time_it_is_asked_for(db):
    """
    Idempotent, which is what makes resuming a deferred batch *continuing*:
    its tests were written against these ports and they are still these ports.
    """
    first = env.reserve(db, "b1")
    assert env.reserve(db, "b1") == first
    assert env.ports_of(db, "b1")[0] == first


def test_a_released_range_is_handed_to_the_next_batch(db):
    """A terminal batch's ports are not held for ever, or the range walks."""
    a = env.reserve(db, "b1")
    env.reserve(db, "b2")
    env.release(db, "b1")

    assert env.ports_of(db, "b1") == []
    assert env.reserve(db, "b3") == a, "the freed range should be reused"


def test_reserving_for_a_batch_that_does_not_exist_is_refused(db):
    """A port range is about a batch; there is no such thing as a loose one."""
    with pytest.raises(env.EnvironmentError_):
        env.reserve(db, "b_nope")


# ---------------------------------------------------------------------------
# Ownership — the two facts
# ---------------------------------------------------------------------------

def test_our_own_process_is_recognised(db):
    """The happy case, against a pid that certainly exists: this one."""
    pid = os.getpid()
    env.record(db, "b1", pid, "pytest")

    assert db.execute("SELECT started_at FROM runtime_processes WHERE pid=?",
                      (pid,)).fetchone()["started_at"], \
        "recording without the second fact records something we cannot stop"
    assert env.is_still_ours(db, pid)


def test_a_reused_pid_is_not_ours(db):
    """
    The defect this replaces, made concrete.

    `boot.reap_processes` sent SIGTERM to every recorded pid. Pids are reused,
    so after a crash and a reboot a recorded pid is overwhelmingly likely to
    belong to something else entirely -- and the only guard was an `except`
    that could not tell "not ours" from "already gone".

    Here the pid is real and the recorded start time is not its own, which is
    exactly the shape a reused pid has.
    """
    pid = os.getpid()
    env.record(db, "b1", pid, "pytest", started_at="an-earlier-boot")
    assert not env.is_still_ours(db, pid), \
        "same pid, different process — this is the one that must not be killed"


def test_a_process_we_never_recorded_is_not_ours(db):
    assert not env.is_still_ours(db, os.getpid())


def test_unknown_is_not_ownership(db):
    """
    A check that passes when it cannot check is not a check, and this one
    guards a kill. Refusing leaves a process running and boot reports it;
    accepting kills something unidentified. Only one of those is recoverable.
    """
    pid = os.getpid()
    env.record(db, "b1", pid, "pytest", started_at="")
    assert not env.is_still_ours(db, pid)

    env.forget(db, pid)
    assert db.execute("SELECT COUNT(*) n FROM runtime_processes").fetchone()["n"] == 0


def test_a_start_time_is_unavailable_rather_than_wrong(db):
    """
    `start_time_of` answers None for a process it cannot see, and None must
    never compare equal to a recorded value.
    """
    assert env.start_time_of(999_999) is None
    env.record(db, "b1", 999_999, "ghost", started_at=None)
    assert not env.is_still_ours(db, 999_999)


# ---------------------------------------------------------------------------
# The reaper, which is where the two facts are spent
# ---------------------------------------------------------------------------

def test_boot_does_not_kill_a_process_it_cannot_claim(db, capsys):
    """
    The whole point of the second fact, at the place it protects.

    A recorded pid that now belongs to something else is the normal state after
    a crash and a reboot, and `reap_processes` used to SIGTERM it. It is dropped
    from the table -- it is certainly not ours to track -- and it is *reported*,
    because a process left running is recoverable and visible, and one killed
    unidentified is neither.
    """
    from rota.core import boot

    killed = []
    import rota.core.boot as boot_mod
    real_kill = boot_mod.os.kill
    boot_mod.os.kill = lambda pid, sig: killed.append(pid)
    try:
        env.record(db, "b1", os.getpid(), "pytest", started_at="an-earlier-boot")
        reaped = boot.reap_processes(db)
    finally:
        boot_mod.os.kill = real_kill

    assert killed == [], "a pid we cannot identify must never be signalled"
    assert reaped == [], "and it is not reported as reaped, because it was not"
    assert db.execute("SELECT COUNT(*) n FROM runtime_processes").fetchone()["n"] == 0
    assert "could not be identified" in capsys.readouterr().out


def test_boot_does_kill_what_it_can_claim(db):
    """The other half: a guard that never lets anything through is not a guard."""
    from rota.core import boot
    import rota.core.boot as boot_mod

    killed = []
    real_kill = boot_mod.os.kill
    boot_mod.os.kill = lambda pid, sig: killed.append(pid)
    try:
        env.record(db, "b1", os.getpid(), "pytest")     # real start time
        reaped = boot.reap_processes(db)
    finally:
        boot_mod.os.kill = real_kill

    assert killed == [os.getpid()]
    assert reaped == [os.getpid()]


# ---------------------------------------------------------------------------
# Spawn and teardown — the first code here that starts anything
# ---------------------------------------------------------------------------

SLEEPER = "import time; time.sleep(30)"


@pytest.fixture
def spawned(db):
    """A real child process, always cleaned up even when a test fails."""
    import sys

    started: list[int] = []

    def go(batch_id="b1", script=SLEEPER):
        pid = env.spawn(db, batch_id, [sys.executable, "-c", script])
        started.append(pid)
        return pid

    yield go

    import contextlib
    import os
    import signal
    for pid in started:
        with contextlib.suppress(OSError):
            os.kill(pid, getattr(signal, "SIGTERM", 15))


def test_a_spawned_process_is_recorded_with_both_facts(db, spawned):
    """
    The window between "it is running" and "we know it is running" is how an
    orphan is made. The row carries the start time as well as the pid, so a
    crash after this point leaves something boot can identify and stop.
    """
    pid = spawned()

    row = db.execute("SELECT batch_id, command, started_at FROM runtime_processes "
                     "WHERE pid = ?", (pid,)).fetchone()
    assert row is not None, "a process nobody recorded is an orphan already"
    assert row["batch_id"] == "b1"
    assert row["started_at"], "a row without the second fact is one we cannot stop"
    assert env.is_still_ours(db, pid)


def test_a_string_command_is_refused(db):
    """
    A string would need a shell, and a shell here would be the only injection
    surface in the system. There is no argument that turns one on.
    """
    with pytest.raises(env.EnvironmentError_) as exc:
        env.spawn(db, "b1", "python -c 'print(1)'")
    assert "shell" in str(exc.value)


def test_teardown_stops_this_batch_and_leaves_the_others(db, spawned):
    """
    The capability to reach another batch's environment does not exist rather
    than being refused, and teardown is where that would show if it did.
    """
    mine, theirs = spawned("b1"), spawned("b2")

    stopped = env.teardown(db, "b1")
    assert stopped == [mine]
    assert env.is_still_ours(db, theirs), "b2's process is not b1's to stop"
    assert db.execute("SELECT COUNT(*) n FROM runtime_processes WHERE batch_id='b2'"
                      ).fetchone()["n"] == 1


def test_a_deferral_keeps_the_ports_and_an_ending_gives_them_back(db, spawned):
    """
    The ruling, exercised. Processes are derived state and die either way; the
    reservation is a number in a row and survives a deferral, because the tests
    were written against those ports and resuming should be continuing.
    """
    base = env.reserve(db, "b1")
    spawned("b1")

    env.teardown(db, "b1")                       # deferred
    assert env.ports_of(db, "b1") == list(range(base, base + env.PORTS_PER_BATCH))
    assert db.execute("SELECT COUNT(*) n FROM runtime_processes WHERE batch_id='b1'"
                      ).fetchone()["n"] == 0, "the processes go regardless"

    env.teardown(db, "b1", release_ports=True)   # merged or abandoned
    assert env.ports_of(db, "b1") == []


def test_teardown_will_not_stop_what_it_cannot_claim(db):
    """
    Same care as boot, and for the same reason: a recorded pid whose start time
    does not match is a stranger. Teardown differs from the reaper only in when
    it runs.
    """
    env.record(db, "b1", os.getpid(), "pytest", started_at="an-earlier-boot")

    import rota.core.environments as env_mod
    killed = []
    real = env_mod.os.kill if hasattr(env_mod, "os") else None
    import os as _os
    orig = _os.kill
    _os.kill = lambda pid, sig: killed.append(pid)
    try:
        stopped = env.teardown(db, "b1")
    finally:
        _os.kill = orig

    assert killed == [] and stopped == []
    assert db.execute("SELECT COUNT(*) n FROM runtime_processes").fetchone()["n"] == 0


def test_the_child_is_told_its_port_range(db, spawned):
    """
    A port range is a fact about where it may listen, not a decision the child
    makes -- the same reasoning as `batch_id` arriving on a wake rather than
    being asked for.
    """
    import sys
    import tempfile

    out = pathlib.Path(tempfile.mkdtemp()) / "seen.txt"
    script = (f"import os, pathlib; pathlib.Path(r'{out}').write_text("
              f"os.environ.get('ROTA_PORT_BASE','') + '|' + "
              f"os.environ.get('ROTA_BATCH',''))")
    pid = env.spawn(db, "b1", [sys.executable, "-c", script])

    import time
    for _ in range(100):
        if out.exists():
            break
        time.sleep(0.05)

    assert out.exists(), "the child never ran"
    base, batch = out.read_text().split("|")
    assert int(base) == env.ports_of(db, "b1")[0]
    assert batch == "b1"


# ---------------------------------------------------------------------------
# The lifecycle hooks — where the ruling actually takes effect
# ---------------------------------------------------------------------------

def test_deferring_a_batch_stops_it_and_keeps_its_ports(db, spawned):
    """
    Law 9's split, applied to a third thing. The checkpoint dies and the
    worktree lives; the processes go with the checkpoint and the reservation
    stays with the worktree.
    """
    from rota.core import lifecycle

    base = env.reserve(db, "b1")
    pid = spawned("b1")
    db.execute("UPDATE batches SET status='running' WHERE id='b1'")

    lifecycle.defer(db, "b1")

    assert db.execute("SELECT status FROM batches WHERE id='b1'"
                      ).fetchone()["status"] == "deferred"
    assert db.execute("SELECT COUNT(*) n FROM runtime_processes WHERE batch_id='b1'"
                      ).fetchone()["n"] == 0, "a deferred batch leaves nothing running"
    assert env.ports_of(db, "b1")[0] == base, \
        "resuming has to be continuing, and the tests name these ports"


def test_merging_a_batch_gives_the_ports_back(db, spawned):
    """A delivered batch has no further claim; holding one walks the range."""
    from rota.core import lifecycle

    env.reserve(db, "b1")
    spawned("b1")
    db.execute("UPDATE batches SET status='running' WHERE id='b1'")

    lifecycle.merge(db, "b1")

    assert db.execute("SELECT COUNT(*) n FROM runtime_processes").fetchone()["n"] == 0
    assert env.ports_of(db, "b1") == []


def test_dispatch_reserves_before_anything_can_ask_for_a_port(db):
    """
    The range exists from the moment the batch is dispatched, not from the
    first spawn -- a value the system knows should never be one a role has to
    get right, and never one that appears halfway through.
    """
    from rota.core import lifecycle

    assert env.ports_of(db, "b1") == []
    lifecycle.start(db, "b1")
    assert len(env.ports_of(db, "b1")) == env.PORTS_PER_BATCH
