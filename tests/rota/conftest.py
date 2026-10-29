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

import pytest

from rota.llm.cassettes import TALLY
# The model tiers run on one worker. `rota_serial_plugin.py` holds that rule,
# because xdist reads `numprocesses` before a conftest can change it. A
# second `pytest_configure` here replaced the first, so the rule that stood
# here was dead (frame 144's review of c888968, point 10).
from rota.llm.llm import DEFAULT_MODEL
from rota.testkit import dbtemplate

# A new database per test is a copy of one built per process. A fresh
# `init_db` cost 140ms a setup and about 20% of the worker time (frame 203's
# count, 2026-10-11). Bound here, before any test module imports `init_db`.
dbtemplate.install()


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

    # The cassette database is not tracked. A checkout that lacks it fetches
    # the published one, once, on the controller, before xdist spawns workers
    # that would each try. A present file is never touched: it may hold
    # recordings nobody has published (rota/testkit/cassette_store.py).
    if not hasattr(config, "workerinput"):
        from rota.testkit import cassette_store

        config._rota_cassette_note = cassette_store.ensure_for_tests()


def pytest_report_header(config):
    """An estimate before the run, from the last one on this machine."""
    from rota.llm.cassettes import Tally, _clock

    lines = []
    note = getattr(config, "_rota_cassette_note", None)
    if note:
        lines.append(note)
    last = Tally.previous()
    if last and last.get("records"):
        each = last["record_seconds"] / last["records"]
        lines.append(
            f"cassettes: last recording ran {last['records']} completions in "
            f"{_clock(last['record_seconds'])} ({each:.1f}s each) on "
            f"{last.get('model') or 'an unnamed model'}, {last.get('when', '')}")
    return lines


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


# The offers that the doors refuse today: the test, and the first words of
# the second refusal. Any other refused offer fails its test, even at a
# known door (frame 144's review of c888968, point 2). Each line is a
# finding, and a strict xfail in `test_offers_followed.py` holds it. The
# judge makes frames of them. Remove a line when its door is fixed.
# The doors record their offers and facts under pytest only. A session
# leaves `api.RECORD` off and does no instrument work (the review of
# fed7c58, low 2).
from rota.roles import api as _api  # noqa: E402

_api.RECORD = True

_SB = "tests/rota/test_t0_sandbox.py::"
_DG = "tests/rota/test_desk_guards.py::"
_OF = "tests/rota/test_offers_followed.py::"
# Finding 1, the project-id door, is fixed by frame 343: an offer at a file
# that a project test holds names a new file beside it.
# Finding 2, the cut door: "To add after it send start=, end=." The seat's
# text replaces the def, so the text after it does not compile or defines a
# name twice.
_TWICE, _INVALID = "m.py defines f twice", "m.py is not valid Python"
# Findings 3 and 4, the invented-literal door, are fixed by frame 204: the
# door stages its own `invented` row and refuses no encode.
# Finding 6, code.write at an insert: a text that ast.parse cannot hold, such
# as 200000 nested minus signs, raises MemoryError from `_future_door`, and
# the session crashes. The cut door's "To add after it" offer meets it.
_CRASH = "MemoryError"
# Each line names the frame that owes its door fix, and the F33 test reads
# the frame against the open frames of the stack. Findings 2 and 6 are frame
# 144's, by the strict xfails of `test_offers_followed.py`. The s317 lines
# are frame 313's, by the docstring of `test_span_holding.py`.
_F144, _F313 = "frame 144", "frame 313"
KNOWN_REFUSED_OFFERS: dict[tuple[str, str], str] = {
    (_OF + "test_a_text_that_breaks_the_parser_gets_the_cut_refusal", _CRASH): _F144,
    (_OF + "test_a_crash_of_one_offer_keeps_the_records_of_the_others", _CRASH): _F144,
    (_OF + "test_a_session_records_no_offer_and_a_test_records_frames", _INVALID): _F144,
    (_DG + "test_a_span_from_the_top_into_the_first_statement_gets_no_moved_boundary",
     _INVALID): _F144,
    (_DG + "test_a_start_on_a_decorated_def_line_names_the_decorators", _TWICE): _F144,
    (_DG + "test_a_span_from_a_blank_line_before_else_is_refused_with_an_offer",
     _INVALID): _F144,
    (_OF + "test_the_add_after_offer_of_a_cut_span_is_admitted", _TWICE): _F144,
    **{(_OF + f"test_a_cut_at_deep_decorators_gets_the_refusal_of_b2ed55b[{k}]",
        "m.py defines a twice"): _F144 for k in ("minus400", "attr2000", "spaced")},
    (_OF + "test_a_decorator_line_off_by_one_reads_false_on_a_twin_decorator",
     "m.py defines a twice"): _F144,
    (_OF + "test_a_cut_refusal_quotes_lines_that_are_true", _INVALID): _F144,
    # Finding 2 on s317's own text, which starts with `) from None` (frame 313).
    ("tests/rota/test_span_holding.py::"
     "test_s317_takes_the_offered_span_and_its_text_lands[540]", _INVALID): _F313,
    ("tests/rota/test_span_holding.py::"
     "test_a_cut_at_the_end_of_a_def_is_offered_the_statement_once", _INVALID): _F313,
}

# The facts that a refusal quotes and the state contradicts today: the test,
# the kind, and words of the refusal's sentence. Kept like the list above.
# The function was the key before, and all the fact sites of code.write share
# `_code_write`, so a false fact of another door hid behind this one (the
# review of fed7c58, low 11).
# Finding 5, the defines-twice door of code.write, is fixed: its numbers
# count from 0, as code.source counts (design 200 pass 2b).
KNOWN_FALSE_FACTS: set[tuple[str, str, str]] = set()


def _problems(nodeid: str, found: list[dict]) -> list[str]:
    """What the follow check and the fact check found wrong, one line each,
    less the known findings."""
    out = []
    for r in found:
        if "kind" in r:
            said = r.get("refusal") or ""
            if not r["ok"] and not any(nodeid == t and r["kind"] == k and w in said
                                       for t, k, w in KNOWN_FALSE_FACTS):
                out.append(f"fact {r['kind']} {r['value']!r} {r['where']} at {r['site']}: "
                           f"{r['why']}")
            continue
        second = (r.get("second") or "").split(": ", 1)[-1]
        if r.get("second") and not any(nodeid == t and second.startswith(s)
                                       for t, s in KNOWN_REFUSED_OFFERS):
            out.append(f"door {r['door']}\n  refusal: {r['refusal']}\n  offer: "
                       f"{r['offer']}\n  second refusal: {r['second']} "
                       f"(at {r.get('second_at')})")
        if r.get("said") and r.get("said_in_refusal") is False:
            out.append(f"door {r['door']}: the offer's sentence {r['said']!r} is not "
                       f"in the refusal {r['refusal']!r}")
        if r.get("bad_args"):
            out.append(f"door {r['door']}: the offer names no such argument: "
                       f"{r['bad_args']}")
        if r.get("not_in_mode"):
            out.append(f"door {r['door']}: the offer names "
                       f"{', '.join(r['not_in_mode'])}, and the mode "
                       f"{r.get('mode')!r} does not hold it")
    return out


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item):
    """
    The follow check and the fact check of frame 144, on every test of this
    directory.

    A refusal records the calls it names in `ctx.offers` and the facts it
    quotes in `ctx.facts`. When a test's call meets such a refusal through
    `Sandbox.call`, this hook sends each offer through `sandbox.dry_run` and
    checks each fact with `sandbox.check_facts`. A test that passes fails
    when an offer is refused or a fact is false, unless a list above names
    the finding. A test that fails keeps its own failure, and the findings
    go into its report. `ROTA_OFFER_LOG` names a file that takes one JSON
    line per offer and per fact.
    """
    import json

    from rota.core import sandbox

    found: list[dict] = []

    def hook(sb, dotted, kwargs, exc, offers, facts=()):
        sandbox._ON_REFUSAL = None      # a dry run's own refusals are not followed
        try:
            if facts:
                # The refusal's sentence keys the known false facts.
                found.extend({**r, "refusal": str(exc)}
                             for r in sandbox.check_facts(sb, facts))
            if offers:
                found.extend(sandbox.follow(sb, dotted, kwargs, exc, offers))
        except Exception as crash:                         # noqa: BLE001
            found.append({"door": dotted, "call": dotted, "refusal": str(exc),
                          "offer": "?", "second": f"the check crashed: {crash!r}"})
        finally:
            sandbox._ON_REFUSAL = hook

    sandbox._ON_REFUSAL = hook
    failed = True
    try:
        result = yield
        failed = False
    finally:
        # Here and not after the yield, so a test that fails still writes its
        # log and shows its findings (the review of c888968, point 3).
        sandbox._ON_REFUSAL = None
        log = os.environ.get("ROTA_OFFER_LOG")
        if log and found:
            with open(log, "a", encoding="utf-8", newline="") as fh:
                for rec in found:
                    fh.write(json.dumps({"test": item.nodeid, **rec}, default=repr) + "\n")
        bad = _problems(item.nodeid, found)
        if bad and failed:
            item.add_report_section("call", "frame 144 follow check", "\n".join(bad))
        # A strict xfail catches every failure of its test. So a new finding
        # in such a test turns its report red below (the review of 8726a13,
        # low 3).
        item.stash[_FINDINGS] = bad
    if bad:
        raise AssertionError("the follow check found:\n" + "\n".join(bad))
    return result


_FINDINGS = pytest.StashKey[list]()


@pytest.fixture(autouse=True)
def _empty_call_log():
    """Empty `sandbox._CALL_LOG` after each test.

    The log keys on `id(ctx)`, and a test that never drains leaves its
    entry. A new `ctx` can take the id of a freed one and then drains calls
    it never made (the review of ee17f70, low 5). The key dates from
    231afe4, and a session's own behaviour does not change in frame 144.
    """
    yield
    from rota.core import sandbox
    sandbox._CALL_LOG.clear()


def unhide(report, bad: list[str]) -> None:
    """Turn an xfailed report red when the hook found something that no
    list above names. An xfail mark holds one known finding, and a new
    finding in the same test is not that finding. A test that calls
    `pytest.skip` after the finding is red too (the review of fed7c58,
    low 9)."""
    if not bad or report.when != "call":
        return
    if hasattr(report, "wasxfail"):
        del report.wasxfail
    elif report.outcome != "skipped":
        return
    report.outcome = "failed"
    report.longrepr = ("the follow check found, in a test marked xfail or "
                       "skipped:\n" + "\n".join(bad))


# tryfirst makes this wrapper the outer one, so it reads the report after
# pytest's own xfail wrapper has marked it.
@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    report = yield
    unhide(report, item.stash.get(_FINDINGS, []))
    return report


@pytest.fixture
def old_page_form(monkeypatch):
    """The word form of a page call, for the tests that pin its doors. The
    menu form replaced it on pages (frame 345, pass R1), and pass R2 retires
    the doors with these tests."""
    from rota.roles import api

    monkeypatch.setattr(api, "MENU_PAGES", False)
