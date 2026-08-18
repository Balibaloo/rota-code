"""
Environments — the reservation, and the two facts that make a kill safe.

Nothing here spawns a process. That is deliberate and it is the build order:
the reaper was written before the spawner, which is why nothing has been
orphaned yet, and these are the two pieces that can be finished without
changing that.
"""
from __future__ import annotations

import os

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
