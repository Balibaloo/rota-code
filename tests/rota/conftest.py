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

from rota.llm.cassettes import TALLY
from rota.llm.llm import DEFAULT_MODEL


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
