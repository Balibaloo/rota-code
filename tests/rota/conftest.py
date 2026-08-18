"""
What the model tiers cost, reported at the end of a run.

"How long do the cassettes take" had no answer anywhere. Neither cassette table
carries a duration, so the number you need in order to decide whether a prompt
edit is affordable — a prompt edit invalidates every recording made against it —
was something repeated from memory. It was being quoted as 27 minutes, from a
file that had also drifted 129 tests.

Persisted per machine in `.rota-timings.json`, gitignored, beside
`.rota-coverage.json` where instrumentation already lives. Not in the cassette
database and not committed: a duration is a fact about this GPU on this day at
this thermal state, and filing it with the recordings would make it look like
evidence about the prompts. Kept at all because one run answers "how long will
this take" and the series answers the better question, which is whether it is
getting slower.
"""
from __future__ import annotations

import os

from rota.llm.cassettes import TALLY


def pytest_configure(config):
    """
    The model tiers run on one worker, and nobody has to remember why.

    `pytest.ini` turns on `-n auto` because the deterministic suite is pure CPU
    and was using one core of sixteen. L1 and L3 are the exception: they call a
    real 8B model on one GPU when `ROTA_L1` is set, and two workers doing that
    at once thrash it -- the run gets slower, and the per-tier durations this
    file exists to record stop being a fact about anything.

    Enforced here instead of in a flag, because a flag is a thing to forget and
    the cost of forgetting is a number that looks real and is not.
    """
    if os.environ.get("ROTA_L1") or os.environ.get("ROTA_T1"):
        if getattr(config.option, "numprocesses", None):
            config.option.numprocesses = 0
            config.option.dist = "no"
from rota.llm.llm import DEFAULT_MODEL


def pytest_configure(config):
    """
    Pin git's identity and clock for the whole test process.

    `samplerepo.GIT_ENV` covers commits the *fixture* makes. It cannot cover the
    ones the system under test makes: `code.commit` runs `worktrees.commit`,
    production code that rightly uses the ambient environment, and its return
    value carries `head_commit` straight back to the model as a tool result.

    That put a fresh sha in the transcript mid-session, so the next turn's
    prompt was unique and its cassette could never be found. Five Developer
    cases and one L3 chain stayed STALE through every re-recording, each one
    replaying ten calls and missing the eleventh.

    Set here rather than in `worktrees` because determinism is a property this
    harness needs, not one the product should pretend to have. Only this
    process is affected, and every repository it touches is under a temp root.
    """
    import os

    from rota.testkit.samplerepo import GIT_ENV

    os.environ.update(GIT_ENV)


def pytest_report_header(config):
    """An estimate before the run, from the last one on this machine."""
    from rota.llm.cassettes import Tally, _clock

    last = Tally.previous()
    if not last or not last.get("records"):
        return []
    each = last["record_seconds"] / last["records"]
    return [f"cassettes: last recording ran {last['records']} completions in "
            f"{_clock(last['record_seconds'])} ({each:.1f}s each) on "
            f"{last.get('model') or 'an unnamed model'}, {last.get('when', '')}"]


def pytest_sessionfinish(session, exitstatus):
    """
    Workers hand their tally up; the controller adds them together.

    Under xdist every worker is its own process with its own module state, so a
    summary printed from the controller alone would report zero and a summary
    printed per worker would report a fraction. `workeroutput` is the seam xdist
    provides for exactly this.
    """
    out = getattr(session.config, "workeroutput", None)
    if out is not None:                      # this process is a worker
        out["rota_tally"] = TALLY.as_dict()


def pytest_testnodedown(node, error):
    """Controller side: fold each finished worker's tally into ours."""
    tally = getattr(node, "workeroutput", {}).get("rota_tally")
    if tally:
        TALLY.merge(tally)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    line = TALLY.line()
    if line:
        terminalreporter.write_line("")
        terminalreporter.write_line(line, bold=True)
        TALLY.save(model=DEFAULT_MODEL)
