"""
Keep the model tiers off the parallel workers, and refuse a replay at a key
the register does not hold.

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

**The door lives here for the same reason** (frame 54, 2026-09-21). Three
ambient variables join the cassette key without saying so: `ROTA_MODEL`,
`ROTA_NUM_CTX` and `ROTA_PROFILE`. A replay under a key the register does not
hold misses every cassette, and the register then reports the previous greens
with no stale and no new red, while the suite goes loudly red. A warning is
what this repository had. The door refuses instead, and it refuses here
because a directory conftest never runs on the xdist controller.
"""
from __future__ import annotations

import os

#: Set by this plugin so a test can assert it ran, rather than inferring it.
FORCED_SERIAL = "ROTA_FORCED_SERIAL"

#: The switches that turn a replay into a recording run. The door stands aside
#: for all three, because a run that records is making new evidence and its key
#: is new by definition. The register already holds 11 models that were first
#: recorded exactly this way, so a door that refused an unheld tuple would
#: refuse every first recording (observed: the design review's finding 7,
#: 2026-09-21).
#:
#: `ROTA_MODEL_FORCE` is deliberately absent, although `rota/tools/gate.py:44`
#: lists it beside these three. It moves the key and records nothing, so a run
#: that sets it is a replay and still needs the door.
RECORDING_SWITCHES = ("ROTA_L1", "ROTA_T1", "ROTA_REFRESH")


def uses_a_model() -> bool:
    return bool(os.environ.get("ROTA_L1") or os.environ.get("ROTA_T1"))


def is_a_replay() -> bool:
    """A run that reads the register rather than adding to it."""
    return not any(os.environ.get(name) for name in RECORDING_SWITCHES)


def ambient_pins():
    """
    The pins a tier builds for a case that declares no model of its own.

    Read here rather than in the tiers, because the tiers build these pins at
    six sites in three files and the door has to stand in front of all six.
    """
    from rota.llm.llm import DEFAULT_MODEL, DEFAULT_NUM_CTX, Pins, think_for

    return Pins(model=DEFAULT_MODEL, temperature=0.0, num_ctx=DEFAULT_NUM_CTX,
                think=think_for(DEFAULT_MODEL))


def _a_recording_with_the_pin(conn, pins) -> bool:
    """
    Whether any recording was made with this optional pin set.

    The field tuple below cannot answer for `think`. An optional pin joins the
    key's hash and `cassettes` has no column for it, so the only exact answer
    is to recompute the key from the row's own text. The query reads one
    model's rows and stops at the first match: 0.118 s for the one model a
    shipped profile sets `think` for, and 0.858 s for the worst case, which is
    the largest model with no match at all (observed: the register,
    2026-09-21). The worst case ends in a refusal, so the run stops there.
    """
    from rota.llm.cassettes import key_for

    for row in conn.execute(
            "SELECT key, system, user FROM cassettes "
            "WHERE model = ? AND num_ctx = ? AND temperature = ?",
            (pins.model, pins.num_ctx, pins.temperature)):
        if key_for(row["system"], row["user"], pins) == row["key"]:
            return True
    return False


def _set_by(name: str) -> str:
    """
    Where a value came from, named so the reader knows what to change.

    An unset variable is said as unset. A refusal that reads `ROTA_MODEL is
    llama3.1:8b` when nobody set `ROTA_MODEL` sends the reader to look for a
    variable that is not there.
    """
    value = os.environ.get(name)
    return f"{name}={value}" if value else f"{name} is unset, so it defaults"


def _refusal(conn, pins) -> str:
    """
    The reason this key is not in the register, or '' when it is.

    The comparison is the field tuple and never the key (observed: the design
    review's finding 6). The system and the user text do not exist yet at any
    pin site, so no key can be built there.

    Each answer names three things: the variable, the value it holds, and what
    the register does hold. A refusal that names only the fault sends the
    reader to a document, and `rota/HARDWARE_GUIDE.md:159` is the document
    that told them to set the variable.
    """
    import sqlite3

    conn.row_factory = sqlite3.Row
    held = list(conn.execute(
        "SELECT DISTINCT model, num_ctx, temperature FROM cassettes"))
    if not held:
        return ""                      # an empty register gates nothing

    models = sorted({row["model"] for row in held})
    if pins.model not in models:
        return (f"the model is {pins.model} ({_set_by('ROTA_MODEL')}), and "
                f"the register holds no cassette for it.\n"
                f"  the register holds: {', '.join(models)}")

    windows = sorted({row["num_ctx"] for row in held
                      if row["model"] == pins.model})
    if pins.num_ctx not in windows:
        return (f"the window is {pins.num_ctx} ({_set_by('ROTA_NUM_CTX')}), "
                f"and no cassette for {pins.model} was recorded at it.\n"
                f"  the register holds: "
                f"{', '.join(str(w) for w in windows)}")

    temperatures = sorted({row["temperature"] for row in held
                           if row["model"] == pins.model
                           and row["num_ctx"] == pins.num_ctx})
    if pins.temperature not in temperatures:
        return (f"the temperature is {pins.temperature}, and no cassette for "
                f"{pins.model} was recorded at it.\n"
                f"  the register holds: "
                f"{', '.join(str(t) for t in temperatures)}")

    if pins.think is not None and not _a_recording_with_the_pin(conn, pins):
        return (f"the think pin is {pins.think} "
                f"({_set_by('ROTA_PROFILE')}), and no cassette for "
                f"{pins.model} was recorded with it.\n"
                f"  the register holds: {pins.model} at the provider's own "
                f"default, which is the pin unset")
    return ""


def refuse_a_key_the_register_does_not_hold() -> None:
    """
    Stop a replay that would miss every cassette, before it collects anything.

    It refuses and it does not warn. A warning leaves the run going: every
    cassette misses, `record_case_run` writes no row because the run measured
    nothing, and `casestatus` filters the same rows out of what it reads. So
    the register keeps reporting yesterday's greens while the suite is red,
    and the register is what an acceptance reads.
    """
    if not is_a_replay():
        return
    try:
        import sqlite3

        from rota import paths

        if not paths.DEV_DB.exists():
            return                     # no register, nothing to be wrong about
        pins = ambient_pins()
        # Read-only, so the door can never migrate the register or leave a
        # journal behind it.
        uri = "file:" + str(paths.DEV_DB).replace("\\", "/") + "?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        try:
            reason = _refusal(conn, pins)
        finally:
            conn.close()
    except Exception:                                       # pragma: no cover
        # A register that will not open is not a reason to stop a run. The
        # door is a guard on a key, not a health check on a file.
        return
    if not reason:
        return

    import pytest

    raise pytest.UsageError(
        f"this run would replay at a key the register does not hold.\n"
        f"  {reason}\n"
        f"  the register is {paths.DEV_DB}\n"
        f"Record at this key with ROTA_L1=1, or unset the variable. A replay "
        f"at a key nothing was recorded at misses every cassette, and the "
        f"register then reports the previous greens.")


def pytest_load_initial_conftests(early_config, parser, args):
    refuse_a_key_the_register_does_not_hold()
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
