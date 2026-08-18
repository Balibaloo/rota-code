"""
Keep the model tiers off the parallel workers.

`pytest.ini` asks for `-n auto` because the deterministic suite is pure CPU and
was running on one core of sixteen. L1 and L3 are the exception: with `ROTA_L1`
or `ROTA_T1` set they call a real 8B model on one GPU, and several workers doing
that at once thrash it -- the run gets slower, and the per-tier durations
`tests/rota/conftest.py` records stop being a fact about anything.

**Why a `-p` plugin and not a conftest.** Three attempts from conftests all
failed, and all three failed *silently*, which is worse than not trying. By the
time anything in a conftest can change `numprocesses`, xdist has read it and
booted its workers. A directory conftest is worse still: under xdist, collection
happens on the workers, so `tests/rota/conftest.py` never runs on the controller
at all. A root conftest is itself loaded during the phase whose hook it was
trying to implement. The result reported nothing wrong and put sixteen workers on
the GPU -- the failure looked exactly like the fix.

A `-p` plugin is registered at command-line parse time, before any conftest is
loaded, which is the only point early enough to edit the arguments rather than
argue with a decision already made.

Verified by the thing that caught the original failure: `bringing up nodes`
appears in the output when xdist is live, and `test_pytest_parallelism.py`
asserts it is absent when a model tier is.
"""
from __future__ import annotations

import os

#: Set by this plugin so a test can assert it ran, rather than inferring it.
FORCED_SERIAL = "ROTA_FORCED_SERIAL"


def uses_a_model() -> bool:
    return bool(os.environ.get("ROTA_L1") or os.environ.get("ROTA_T1"))


def pytest_load_initial_conftests(early_config, parser, args):
    if not uses_a_model():
        return

    # Both spellings, and both forms of each: `-n 4` and `-n4`, `--dist loadfile`
    # and `--dist=loadfile`. Dropping the flag and keeping its value is not a
    # tidiness slip -- a stray `loadfile` becomes a positional argument, pytest
    # reads it as a path, and the run collects nothing while reporting success.
    # That is the same silent shape this whole plugin exists to avoid, and it
    # happened here first.
    SEPARATE = {"-n", "--numprocesses", "--dist"}
    kept, skip_value = [], False
    for a in args:
        if skip_value:
            skip_value = False
            continue
        if a in SEPARATE:
            skip_value = True                    # its value is the next argument
            continue
        if a.startswith(("-n", "--numprocesses=", "--dist=")):
            continue
        kept.append(a)

    args[:] = kept + ["-n0"]
    os.environ[FORCED_SERIAL] = "1"
