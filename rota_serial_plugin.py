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

**The door's rule lives here, and the four tier files call it** (frame 54,
2026-09-21). Three ambient variables join the cassette key without saying so:
`ROTA_MODEL`, `ROTA_NUM_CTX` and `ROTA_PROFILE`. A replay under a key the
register does not hold misses every cassette, and the register then reports
the previous greens with no stale and no new red, while the suite goes loudly
red. A warning is what this repository had. The door refuses instead.

**Who calls the door, and why it is not a hook here** (frame 54's fix pass,
2026-09-21). It was called from `pytest_load_initial_conftests`, before
anything was collected, so it refused every pytest command in the repository:
`pytest tests/rota/test_bounds.py` calls no model and was refused for the
ambient model's sake. All 99 test files were refused, and that showed only
because the register happens to hold 11 models, one of them the bare default.
Roman approved a full re-record in this frame, and a register of one model
would have failed every bare `pytest` command.

Two placements were measured and one reports (observed: 2026-09-21).
`pytest_collection_modifyitems` runs on the xdist workers, because the
controller does not collect, and a `UsageError` there ends the run in
`INTERNALERROR: assert not crashitem` with the reason nowhere in the output.
A call at the tier file's module scope is a collect error, which xdist
reports with its message, once per worker that collected the file. So the
four files that open `paths.DEV_DB` call the door themselves, and
`tests/rota/test_register_key.py` pins that every such file does. Guessing
from `args` at the early hook was rejected: that is the silent-failure shape
this whole plugin exists to avoid.
"""
from __future__ import annotations

import os

import pytest

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


def _think_values_held(conn, pins) -> list[str]:
    """
    The think values the register holds for this model, said in words.

    The field tuple cannot answer for `think`, for the reason above, so each
    row's key is rebuilt once per candidate value. A row keyed before frame 65
    carries no think field at all, and this reads as `unset`: it is what the
    register holds, and a re-record is the only way to move it to a value.

    The cost is paid once, because the caller refuses and the run stops.
    """
    import dataclasses

    from rota.llm.cassettes import key_for

    said = {True: "True", False: "False", None: "unset"}
    found: list[str] = []
    for row in conn.execute(
            "SELECT key, system, user FROM cassettes "
            "WHERE model = ? AND num_ctx = ? AND temperature = ?",
            (pins.model, pins.num_ctx, pins.temperature)):
        for value, word in said.items():
            if word in found:
                continue
            if key_for(row["system"], row["user"],
                       dataclasses.replace(pins, think=value)) == row["key"]:
                found.append(word)
        if len(found) == len(said):
            break
    return [word for word in said.values() if word in found]


def _set_by(name: str) -> str:
    """
    Where a value came from, named so the reader knows what to change.

    An unset variable is said as unset. A refusal that reads `ROTA_MODEL is
    llama3.1:8b` when nobody set `ROTA_MODEL` sends the reader to look for a
    variable that is not there.
    """
    value = os.environ.get(name)
    return f"{name}={value}" if value else f"{name} is unset, so it defaults"


def _remedy(name: str, held: str) -> str:
    """
    What to change, said differently for a set variable and an unset one.

    "unset the variable" moves nothing when nobody set the variable, and that
    is what this refusal used to say for the commonest case of all: no
    `ROTA_MODEL`, so the model defaults to one the register does not hold. A
    remedy that does not move the run is worse than no remedy. The reader
    follows it, sees the same refusal, and stops believing the message.
    """
    if os.environ.get(name):
        return f"unset {name}, or set it to {held}"
    return f"set {name} to {held}"


def _refusal(conn, pins) -> tuple[str, str]:
    """
    The reason this key is not in the register and the remedy, or two ''.

    The comparison is the field tuple and never the key (observed: the design
    review's finding 6). The system and the user text do not exist yet at any
    pin site, so no key can be built there.

    Each answer names four things: the variable, the value it holds, what the
    register does hold, and what to change. A refusal that names only the
    fault sends the reader to a document, and `rota/HARDWARE_GUIDE.md:159` is
    the document that told them to set the variable.
    """
    import sqlite3

    conn.row_factory = sqlite3.Row
    held = list(conn.execute(
        "SELECT DISTINCT model, num_ctx, temperature FROM cassettes"))
    if not held:
        return "", ""                  # an empty register gates nothing

    models = sorted({row["model"] for row in held})
    if pins.model not in models:
        return ((f"the model is {pins.model} ({_set_by('ROTA_MODEL')}), and "
                 f"the register holds no cassette for it.\n"
                 f"  the register holds: {', '.join(models)}"),
                _remedy("ROTA_MODEL", "a model the register holds"))

    windows = sorted({row["num_ctx"] for row in held
                      if row["model"] == pins.model})
    if pins.num_ctx not in windows:
        return ((f"the window is {pins.num_ctx} ({_set_by('ROTA_NUM_CTX')}), "
                 f"and no cassette for {pins.model} was recorded at it.\n"
                 f"  the register holds: "
                 f"{', '.join(str(w) for w in windows)}"),
                _remedy("ROTA_NUM_CTX", "a window the register holds"))

    temperatures = sorted({row["temperature"] for row in held
                           if row["model"] == pins.model
                           and row["num_ctx"] == pins.num_ctx})
    if pins.temperature not in temperatures:
        return ((f"the temperature is {pins.temperature}, and no cassette for "
                 f"{pins.model} was recorded at it.\n"
                 f"  the register holds: "
                 f"{', '.join(str(t) for t in temperatures)}"),
                "record at this temperature with ROTA_L1=1")

    # The pin in both directions (frame 54's fix pass, 2026-09-21). The check
    # fired only when a profile set the pin, so a register whose cassettes for
    # this model were all recorded at `think=True` passed a run with the pin
    # unset, and then every cassette missed. The door exists to stop exactly
    # that, and it was blind to one half of it.
    if not _a_recording_with_the_pin(conn, pins):
        # The values held, in the form the three refusals above use. `think`
        # is in the key's hash and in no column, so each value is recovered by
        # rebuilding the key from the row's own text (frame 65, 2026-09-23).
        # The older text named "the pin unset", which no run sends any more,
        # and told the reader to unset it, which no profile can do.
        held_pins = (", ".join(_think_values_held(conn, pins))
                     or "no value this door can rebuild")
        return ((f"the think pin is {pins.think} "
                 f"({_set_by('ROTA_PROFILE')}), and no cassette for "
                 f"{pins.model} was recorded with it.\n"
                 f"  the register holds: {held_pins}"),
                _remedy("ROTA_PROFILE",
                        "a profile that pins think to one of the values held"))
    return "", ""


def refuse_a_key_the_register_does_not_hold() -> None:
    """
    Stop a replay that would miss every cassette, before it collects anything.

    It refuses and it does not warn. A warning leaves the run going: every
    cassette misses, and `record_case_run` writes no result because the run
    measured nothing. It writes one `key_misses` row instead, so the register
    now says that somebody looked and the key missed (frame 64, 2026-09-22).
    The report reads that row and stales the case. A warning would still cost
    a whole replay pass to say what this door says before anything collects.
    """
    if not is_a_replay():
        return
    from rota import paths

    if not paths.DEV_DB.exists():
        return                         # no register, nothing to be wrong about
    # Outside the guard below. `ambient_pins` reads the profile, and a profile
    # the loader cannot find raises. That is a run nobody can key, so it must
    # be a traceback. Inside the guard it opened the whole suite in silence
    # (frame 65's diff review, 2026-09-23).
    pins = ambient_pins()
    try:
        import sqlite3

        # Read-only, so the door can never migrate the register or leave a
        # journal behind it.
        uri = "file:" + str(paths.DEV_DB).replace("\\", "/") + "?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        try:
            reason, remedy = _refusal(conn, pins)
        finally:
            conn.close()
    except Exception:                                       # pragma: no cover
        # A register that will not open is not a reason to stop a run. The
        # door is a guard on a key, not a health check on a file.
        return
    if not reason:
        return

    raise pytest.UsageError(
        f"this run would replay at a key the register does not hold.\n"
        f"  {reason}\n"
        f"  the register is {paths.DEV_DB}\n"
        f"Record at this key with ROTA_L1=1, or {remedy}. A replay at a key "
        f"nothing was recorded at misses every cassette, and the register "
        f"then reports the previous greens.")


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
