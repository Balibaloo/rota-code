"""
The suite runs on sixteen cores, except where it must not.

This exists because the exemption failed silently three times. `-n auto` in
`pytest.ini` takes the deterministic suite from eight minutes to two and a half;
the model tiers must stay serial, because L1 and L3 call one 8B model on one GPU
and concurrent workers thrash it -- the run gets slower and the per-tier timings
stop being a fact about anything.

Every failed attempt reported success. A directory conftest never runs on the
xdist controller at all (collection happens on the workers), and a root conftest
is loaded during the very phase whose hook it was implementing. What caught it
was `bringing up nodes` appearing twice in a log somebody happened to read,
after sixteen workers had already been on the GPU.

So the mechanism is asserted rather than trusted.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

import rota_serial_plugin


def _args_after(monkeypatch, env: dict, args: list[str]) -> list[str]:
    for k in ("ROTA_L1", "ROTA_T1"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    out = list(args)
    rota_serial_plugin.pytest_load_initial_conftests(None, None, out)
    return out


def test_a_model_tier_is_forced_serial(monkeypatch):
    """Whatever `-n` was asked for, and however it was spelled."""
    for given in (["-n", "auto"], ["-n16"], ["--numprocesses=8"],
                  ["--numprocesses", "auto"], ["-n", "auto", "--dist", "loadfile"]):
        got = _args_after(monkeypatch, {"ROTA_L1": "1"}, ["tests/rota", *given])
        assert got[-1] == "-n0", f"{given} -> {got}"
        assert not any(a.startswith(("--dist", "--numprocesses")) or
                       (a.startswith("-n") and a != "-n0") for a in got[:-1]), got
        assert "tests/rota" in got, "the actual target must survive"


def test_the_deterministic_suite_is_left_alone(monkeypatch):
    """No model in play, no reason to serialise: the flags pass through."""
    got = _args_after(monkeypatch, {}, ["tests/rota", "-n", "auto",
                                       "--dist", "loadfile"])
    assert got == ["tests/rota", "-n", "auto", "--dist", "loadfile"]


def test_t1_counts_as_a_model_tier(monkeypatch):
    """`ROTA_T1` drives the live vertical slice and hits the same one GPU."""
    got = _args_after(monkeypatch, {"ROTA_T1": "1"}, ["tests/rota", "-n", "auto"])
    assert got[-1] == "-n0"


@pytest.mark.slow
def test_end_to_end_no_workers_come_up_for_a_model_tier():
    """
    The assertion the silent failures would have failed.

    Everything above tests the function. This tests the wiring -- that the
    plugin is loaded, that it is early enough, and that xdist does not boot.
    `bringing up nodes` is xdist announcing its workers, and it is the string
    that exposed the original bug.

    It runs a real file inside the repository, because `pytest.ini` and the
    plugin only apply under the rootdir -- a scratch file elsewhere would prove
    nothing. `test_bounds.py` is the cheapest one that exists.
    """
    import os

    def run(env):
        return subprocess.run(
            [sys.executable, "-m", "pytest", "tests/rota/test_bounds.py", "-q"],
            capture_output=True, text=True, cwd=".",
            env={**os.environ, **env}).stdout

    serial = run({"ROTA_L1": "1"})
    assert "bringing up nodes" not in serial, serial[:1500]
    # Both halves, always. The first version of the plugin dropped `--dist` and
    # kept `loadfile`, which pytest read as a path: zero tests collected, and
    # "no workers came up" was true for the wrong reason. A serial run that ran
    # nothing looks exactly like a serial run that worked.
    assert "2 passed" in serial, serial[:1500]

    # And the other half: without a model tier the workers *do* come up, or
    # `-n auto` is doing nothing and the eight-minute suite is back.
    parallel = run({"ROTA_L1": "", "ROTA_T1": ""})
    assert "bringing up nodes" in parallel, parallel[:1500]
    assert "2 passed" in parallel, parallel[:1500]
