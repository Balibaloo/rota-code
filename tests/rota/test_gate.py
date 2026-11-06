"""
The gate reads a run correctly, and says only what moved.

Nothing here starts pytest as a child and nothing here opens
`tests/rota/cassettes.db`. The gate takes its external calls as module-level
functions, so each test replaces them with `monkeypatch` and hands the gate a
canned log, a canned cache and a canned baseline. `main` takes the root, so the
log, the pytest cache and the baseline all live in `tmp_path`.
"""
from __future__ import annotations

import json

import pytest

from rota.tools import gate

# The shapes the gate has to read. Under `-q` the last line has no `=` padding.
LOG_MIXED = ("bringing up nodes...\n"
             "..F..E.\n"
             "FAILED tests/rota/test_delivery.py::test_a_door[<lambda>-no verdict]\n"
             "3 failed, 1 passed, 1 error in 22.59s\n")
LOG_GREEN = "..\n1 passed in 2.67s\n"

# A node id with a space and one with brackets. A regex over `\S+` drops the
# first, which is why the red set comes from pytest's cache.
SPACED = "tests/rota/test_delivery.py::test_a_door[<lambda>-no verdict]"
BRACKET = "tests/rota/test_l1.py::test_l1_case[L1-DV-fix-the-code-not-the-test]"

HEAD = "5412022aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
OTHER = "62d5a2accccccccccccccccccccccccccccccccc"


def _write(path, text):
    # `newline=""` keeps the file at LF under Windows.
    with path.open("w", encoding="utf-8", newline="") as out:
        out.write(text)


def _cache(root, ids, files=None):
    """Write the cache, and make the test files the ids name."""
    for node in (ids if files is None else files):
        name = node.split("::", 1)[0]
        if name:
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).touch()
    path = root / gate.LASTFAILED
    path.parent.mkdir(parents=True, exist_ok=True)
    _write(path, json.dumps({node: True for node in ids}))


def _baseline(root, **fields):
    record = {"commit": HEAD, "dirty": False, "when": "2026-09-17 04:00",
              "model": "qwen3:8b", "summary": "1 passed", "failed": [],
              "stale": [], "seconds": 1.0}
    record.update(fields)
    _write(root / gate.BASELINE_NAME, json.dumps(record, indent=2))
    return record


@pytest.fixture
def stage(tmp_path, monkeypatch):
    """The gate with every external call replaced, and a dial for each."""
    state = {"root": tmp_path, "log": LOG_GREEN, "code": 0, "failed": set(),
             "stale": set(), "head": HEAD, "dirty": False, "stale_model": None,
             "rerun": "", "after": None, "env": None, "reran": [],
             "rerecorded": [], "keeps": set()}

    def run_suite(env, log):
        state["env"] = env
        # The cache is cumulative, so the gate deletes it before every run.
        assert not (tmp_path / gate.LASTFAILED).exists(), (
            "the gate must hand pytest an empty cache")
        _write(log, state["log"])
        if state["failed"] is not None:
            _cache(tmp_path, state["failed"])
        return state["code"]

    def rerun(env, ids):
        state["reran"].append(list(ids))
        if state["after"] is not None:
            _cache(tmp_path, state["after"])
        return state["rerun"]

    def stale(model):
        state["stale_model"] = model
        return None if state["stale"] is None else set(state["stale"])

    def rerecord(env, case_id, log):
        # A re-record greens its case, unless the dial `keeps` holds the case.
        # The suite's log exists already, because the re-records append to it.
        assert log.exists(), "the re-records append to the suite's log"
        state["rerecorded"].append((env["ROTA_MODEL"], case_id))
        if case_id in state["keeps"]:
            return None
        state["stale"].discard(case_id)
        return _node(case_id)

    def states(model):
        stale_now = state["stale"] or set()
        return {case: "STALE" if case in stale_now else "green 5/5"
                for case in ("case-a", "case-b", "case-c")}

    monkeypatch.setattr(gate, "TEMP_ROOT", tmp_path / "gatetmp")
    monkeypatch.setattr(gate, "_rerecord", rerecord)
    monkeypatch.setattr(gate, "_states", states)
    monkeypatch.setattr(gate, "_run_suite", run_suite)
    monkeypatch.setattr(gate, "_rerun", rerun)
    monkeypatch.setattr(gate, "_stale", stale)
    # `main` prepares `paths.DEV_DB`. On the checkout that is the live
    # register, and a suite worker must never build its indexes (frame 362).
    monkeypatch.setattr(gate, "prepare_register", lambda: [])
    monkeypatch.setattr(gate, "_head", lambda: state["head"])
    monkeypatch.setattr(gate, "_dirty", lambda: state["dirty"])
    # No test reaches a server. The main card reads free unless a test holds
    # it with `_held`.
    monkeypatch.setattr(gate, "_get_json", lambda url: {"models": []})
    return state


def _node(case_id):
    return f"tests/rota/test_l1.py::test_l1_case[{case_id}]"


def _run(stage, *argv, rerecord=False):
    # The compare tests read the five lines by index. The re-record lines come
    # before them, so only the re-record tests turn the flow on.
    extra = [] if rerecord else ["--no-rerecord"]
    return gate.main(list(argv) + extra, root=stage["root"])


def _lines(capsys):
    return capsys.readouterr().out.splitlines()


def test_the_summary_is_the_last_line_that_carries_a_duration():
    assert gate.summary_of(LOG_MIXED) == "3 failed, 1 passed, 1 error"
    assert gate.summary_of(LOG_GREEN) == "1 passed"


def test_a_log_with_no_summary_reads_as_no_summary():
    """A usage error or an xdist crash writes neither a summary nor a FAILED."""
    assert gate.summary_of("") is None
    assert gate.summary_of("ERROR: file or directory not found: tests/rot\n") is None


def test_the_red_set_keeps_a_node_id_with_a_space(tmp_path):
    _cache(tmp_path, [SPACED, BRACKET])
    assert gate.red_ids(tmp_path) == {SPACED, BRACKET}


def test_no_cache_file_reads_as_no_red_set(tmp_path):
    assert gate.red_ids(tmp_path) is None


def test_an_id_from_another_pytest_run_is_not_a_red_of_this_run(tmp_path):
    """
    The cache is shared, and pytest never drops an id the tree does not collect.

    A review probe on a temp file left six ids like `::test_bad` in the repo's
    cache, and the first gate run read 29 ids for 23 reds.
    """
    gone = "tests/rota/test_gone.py::test_x"
    _cache(tmp_path, [SPACED, "::test_bad", gone], files=[SPACED])
    assert gate.red_ids(tmp_path) == {SPACED}


def test_the_cumulative_cache_is_deleted_before_the_run(stage):
    """
    Pytest drops only the ids it ran, so the cache keeps a dead id for ever.

    A parametrised id that no longer exists, or a collection error that is
    fixed, is never collected again under xdist. The `_run_suite` stub asserts
    the file is gone when the gate calls it.
    """
    ghost = "tests/rota/test_l1.py::test_l1_case[L1-DV-a-case-that-was-renamed]"
    _cache(stage["root"], [ghost])
    stage["failed"] = {BRACKET}

    assert _run(stage) == 0
    stored = json.loads((stage["root"] / gate.BASELINE_NAME).read_text("utf-8"))
    assert stored["failed"] == [BRACKET], "the dead id is not a red of this run"


def test_a_child_that_did_not_run_says_so_and_exits_one(stage, capsys):
    stage["code"], stage["log"], stage["failed"] = 4, "", None
    assert _run(stage) == 1

    out = _lines(capsys)
    assert out[0] == "suite: did not run (pytest exit 4)"
    assert not (stage["root"] / gate.BASELINE_NAME).exists(), (
        "a run that did not measure anything must not become the baseline")


def test_the_did_not_run_line_carries_the_last_twenty_lines_of_the_log(stage, capsys):
    stage["code"] = 4
    stage["log"] = "".join(f"line {n}\n" for n in range(1, 31))
    stage["failed"] = None

    assert _run(stage) == 1
    out = _lines(capsys)
    assert out[0] == "suite: did not run (pytest exit 4)"
    assert out[1:] == [f"line {n}" for n in range(11, 31)]


def test_a_code_zero_run_with_no_summary_still_reads_as_did_not_run(stage, capsys):
    """
    Exit 0 and no summary line is a run that collected nothing.

    A gate that trusted the code alone would call that green, which is the one
    shape the gate exists to refuse.
    """
    stage["code"] = 0
    stage["log"] = "no tests ran\n"
    stage["failed"] = None

    assert _run(stage) == 1
    assert _lines(capsys)[0] == "suite: did not run (pytest exit 0)"


def test_reds_with_no_cache_file_exit_one(stage, capsys):
    stage["log"], stage["failed"] = LOG_MIXED, None
    assert _run(stage) == 1
    assert "cache is off" in capsys.readouterr().out


def test_the_compare_shows_new_reds_reds_gone_and_the_stale_delta(stage, capsys):
    _baseline(stage["root"], failed=[BRACKET], stale=["case-a", "case-b"])
    stage["log"] = LOG_MIXED
    stage["failed"] = {SPACED}
    stage["stale"] = {"case-a", "case-c"}

    assert _run(stage) == 1
    out = _lines(capsys)
    assert out[0] == "suite: 3 failed, 1 passed, 1 error (baseline: 1 passed)"
    assert out[1] == f"new reds (1): {SPACED}"
    assert out[2] == f"reds gone (1): {BRACKET}"
    assert out[3] == "stale (2): case-a, case-c (+1 -1 against baseline)"


def test_a_stale_set_that_did_not_move_carries_no_delta(stage, capsys):
    _baseline(stage["root"], stale=["case-a"])
    stage["stale"] = {"case-a"}

    assert _run(stage) == 0
    assert _lines(capsys)[3] == "stale (1): case-a"


def test_an_absent_register_is_read_without_creating_one(tmp_path, monkeypatch):
    """
    `open_dev_db` makes an empty database from a missing file.

    The empty file then reports 127 cases as NEW, and it stops
    `ensure_for_tests` from ever fetching the real register (observed: the diff
    review of 2026-09-17). So the gate looks at the path first.
    """
    from rota import paths

    missing = tmp_path / "absent" / "cassettes.db"
    monkeypatch.setattr(paths, "DEV_DB", missing)

    assert gate._stale("qwen3:8b") is None
    assert not missing.exists()
    assert not missing.parent.exists()


def test_an_absent_register_says_so_and_skips_the_stale_compare(
        stage, capsys, monkeypatch):
    from rota import paths

    missing = stage["root"] / "absent.db"
    monkeypatch.setattr(paths, "DEV_DB", missing)
    _baseline(stage["root"], stale=["case-a"])
    stage["stale"] = None

    assert _run(stage) == 0, "an absent register changes no exit code"
    assert _lines(capsys)[3] == f"stale: the register is absent ({missing})"

    assert _run(stage, "--baseline") == 0
    stored = json.loads((stage["root"] / gate.BASELINE_NAME).read_text("utf-8"))
    assert stored["stale"] is None, "an unmeasured set is null, not empty"

    # The baseline holds no stale set, so the next run reports its own and
    # compares nothing.
    capsys.readouterr()
    stage["stale"] = {"case-a"}
    assert _run(stage) == 0
    assert _lines(capsys)[3] == "stale (1): case-a (no stale baseline)"


def test_a_baseline_with_no_stale_set_says_the_compare_did_not_happen(
        stage, capsys):
    """
    A null stale baseline never regains a delta on its own.

    The register comes back, the gate reports a set again, and the compare stays
    skipped. The line says so, so the reader knows to store a new baseline.
    """
    _baseline(stage["root"], stale=None)
    stage["stale"] = {"case-a"}

    assert _run(stage) == 0
    assert _lines(capsys)[3] == "stale (1): case-a (no stale baseline)"

    _baseline(stage["root"], stale=["case-b"])
    assert _run(stage) == 0
    assert _lines(capsys)[3] == "stale (1): case-a (+1 -1 against baseline)"


def test_the_first_line_carries_the_baselines_summary(stage, capsys):
    """
    A change that stops 300 tests from collecting reads as green on reds alone.

    The reader has no other reference number, so the baseline's summary sits on
    the same line, and a fall in the passed count gets its own note.
    """
    _baseline(stage["root"], summary="22 failed, 1819 passed, 27 skipped")
    stage["log"] = "..\n22 failed, 1519 passed, 27 skipped in 400.00s\n"

    assert _run(stage) == 0
    out = _lines(capsys)
    assert out[0] == ("suite: 22 failed, 1519 passed, 27 skipped "
                      "(baseline: 22 failed, 1819 passed, 27 skipped)")
    assert out[-1] == "note: passed fell from 1819 to 1519"


def test_a_passed_count_that_held_or_rose_gets_no_note(stage, capsys):
    _baseline(stage["root"], summary="22 failed, 1819 passed")
    stage["log"] = "..\n22 failed, 1820 passed in 400.00s\n"

    assert _run(stage) == 0
    assert "passed fell" not in capsys.readouterr().out


def test_a_baseline_that_does_not_parse_stops_the_run(stage, capsys):
    """Never replaced in silence: a rewrite would drop the reds it held."""
    path = stage["root"] / gate.BASELINE_NAME
    _write(path, "{ half a file")

    assert _run(stage) == 1
    assert capsys.readouterr().out.strip() == (
        f"baseline: did not parse ({path}); delete it or pass --baseline")
    assert path.read_text("utf-8") == "{ half a file"
    assert stage["env"] is None, "the refusal comes before the eight minutes"

    assert _run(stage, "--baseline") == 0, "--baseline replaces it"
    assert json.loads(path.read_text("utf-8"))["commit"] == HEAD


def test_the_first_run_stores_the_baseline_and_prints_no_traceback(stage, capsys):
    stage["log"], stage["failed"] = LOG_MIXED, {SPACED, BRACKET}
    stage["stale"] = {"case-a"}

    # With no baseline every known red is new, and the first run would print
    # every traceback. The run compares itself against itself instead.
    assert _run(stage) == 0
    out = _lines(capsys)
    assert out[1] == "new reds (0): none"
    assert out[2] == "reds gone (0): none"
    assert stage["reran"] == []

    stored = json.loads((stage["root"] / gate.BASELINE_NAME).read_text("utf-8"))
    assert stored["failed"] == sorted([SPACED, BRACKET])
    assert stored["stale"] == ["case-a"]
    assert stored["commit"] == HEAD
    assert stored["model"] == "qwen3:8b"


def test_a_later_run_leaves_the_baseline_alone_until_baseline_is_asked_for(stage):
    stage["failed"] = {BRACKET}
    assert _run(stage) == 0
    first = (stage["root"] / gate.BASELINE_NAME).read_text("utf-8")

    stage["failed"] = {BRACKET, SPACED}
    assert _run(stage) == 1, "the second run has a new red"
    assert (stage["root"] / gate.BASELINE_NAME).read_text("utf-8") == first, (
        "a plain run never overwrites the baseline")

    assert _run(stage, "--baseline") == 0, "the rewritten baseline holds both"
    second = json.loads((stage["root"] / gate.BASELINE_NAME).read_text("utf-8"))
    assert second["failed"] == sorted([BRACKET, SPACED])


def test_the_five_lines_and_the_note_about_the_stored_baseline(stage, capsys):
    stage["log"] = LOG_MIXED
    stage["failed"] = {SPACED}
    stage["stale"] = {"case-a"}

    assert _run(stage, "--baseline") == 0
    out = _lines(capsys)
    assert out[0] == "suite: 3 failed, 1 passed, 1 error"
    assert out[1] == "new reds (0): none"
    assert out[2] == "reds gone (0): none"
    assert out[3] == "stale (1): case-a"
    assert out[4].startswith("time: ")
    assert "model qwen3:8b" in out[4]
    assert str(stage["root"] / "gatetmp") in out[4]
    assert "baseline 5412022 " in out[4]
    assert out[5] == "note: baseline stored at 5412022"


def test_a_moved_tree_and_a_dirty_baseline_each_get_a_note(stage, capsys):
    _baseline(stage["root"], commit=OTHER, dirty=True)
    stage["head"] = HEAD

    assert _run(stage) == 0
    out = _lines(capsys)
    assert out[4].endswith("baseline 62d5a2a 2026-09-17 04:00")
    assert out[5] == ("note: the tree moved past the baseline "
                      "(62d5a2a -> 5412022)")
    assert out[6] == ("note: the baseline was taken on an uncommitted tree at "
                      "62d5a2a, so the compare is not commit to commit")


def test_a_new_red_gets_a_traceback_and_exit_one(stage, capsys):
    _baseline(stage["root"], failed=[BRACKET])
    stage["log"], stage["failed"] = LOG_MIXED, {BRACKET, SPACED}
    stage["after"] = {BRACKET, SPACED}
    stage["rerun"] = "E   AssertionError: the door opened\n1 failed in 3.10s\n"

    assert _run(stage) == 1
    assert stage["reran"] == [[SPACED]], "only the new red is run again"
    out = capsys.readouterr().out
    assert "AssertionError: the door opened" in out
    assert "flaky:" not in out
    assert out.strip().splitlines()[-1] == "exit 1: 1 new reds, 0 of them flaky"


def test_a_new_red_that_passes_on_the_rerun_is_called_flaky(stage, capsys):
    _baseline(stage["root"], failed=[])
    stage["log"], stage["failed"] = LOG_MIXED, {SPACED}
    stage["after"] = set()          # the re-run dropped it from the cache
    stage["rerun"] = "1 passed in 2.20s\n"

    # A test that fails under load and passes alone is a defect, not noise
    # (ruled: the diff review of 2026-09-17, point 7).
    assert _run(stage) == 1, "a new red still closes the gate"
    out = capsys.readouterr().out
    assert f"flaky: {SPACED}" in out
    assert out.strip().splitlines()[-1] == "exit 1: 1 new reds, 1 of them flaky"


def test_a_run_with_no_new_red_exits_zero(stage):
    _baseline(stage["root"], failed=[BRACKET, SPACED])
    stage["log"], stage["failed"] = LOG_MIXED, {BRACKET}
    assert _run(stage) == 0


def test_the_child_environment_drops_the_recording_switches(stage, monkeypatch):
    monkeypatch.setenv("ROTA_L1", "1")
    monkeypatch.setenv("ROTA_T1", "1")
    monkeypatch.setenv("ROTA_REFRESH", "1")
    monkeypatch.setenv("ROTA_MODEL_FORCE", "llama3.1:8b")
    monkeypatch.setenv("ROTA_MODEL", "qwen3:8b")

    _run(stage)
    env = stage["env"]
    for name in gate.RECORDING_NAMES:
        assert name not in env, f"{name} turns the gate into a recording run"
    assert env["ROTA_MODEL"] == "qwen3:8b"


def test_the_child_environment_drops_pytest_addopts(stage, monkeypatch):
    """`-x` truncates the run and `-p no:cacheprovider` removes the red set."""
    monkeypatch.setenv("PYTEST_ADDOPTS", "-x -p no:cacheprovider")

    _run(stage)
    assert "PYTEST_ADDOPTS" not in stage["env"]


def test_the_child_gets_the_temp_root_under_all_three_names(stage):
    _run(stage)
    root = str(stage["root"] / "gatetmp")
    # `tempfile.gettempdir()` reads the three in this order, and the git
    # fixture's guard follows `gettempdir()`.
    assert [stage["env"][n] for n in ("TMPDIR", "TEMP", "TMP")] == [root] * 3
    assert (stage["root"] / "gatetmp").is_dir()


def test_the_model_comes_from_the_argument_then_the_environment(stage, monkeypatch):
    monkeypatch.delenv("ROTA_MODEL", raising=False)
    _run(stage)
    assert stage["env"]["ROTA_MODEL"] == gate.FALLBACK_MODEL, (
        "never llama: under llama the stale line names 62 qwen-green cases")

    _run(stage, "--model", "qwen3:14b")
    assert stage["env"]["ROTA_MODEL"] == "qwen3:14b"


def test_the_stale_set_is_read_under_the_model_the_run_used(stage, monkeypatch):
    """One model, one reading: a llama stale line names 62 qwen-green cases."""
    monkeypatch.delenv("ROTA_MODEL", raising=False)
    _run(stage)
    assert stage["stale_model"] == gate.FALLBACK_MODEL

    _run(stage, "--model", "qwen3:14b")
    assert stage["stale_model"] == "qwen3:14b"


def test_the_gate_rerecords_each_stale_case_in_order(stage, capsys):
    """
    One case at a time, in sorted order, and the baseline holds the set after.

    Two writers on the cassette file lost a run to `database is locked`
    (observed: frame 86, 2026-09-25), so no call overlaps another.
    """
    stage["stale"] = {"case-c", "case-a", "case-b"}
    stage["keeps"] = {"case-b"}

    assert _run(stage, "--baseline", rerecord=True) == 0
    assert stage["rerecorded"] == [("qwen3:8b", "case-a"), ("qwen3:8b", "case-b"),
                                   ("qwen3:8b", "case-c")]
    out = _lines(capsys)
    assert out[:4] == ["rerecording 3 stale cases, five live runs each, on qwen3:8b",
                       "rerecorded case-a: STALE -> green 5/5",
                       "rerecorded case-b: STALE -> STALE",
                       "rerecorded case-c: STALE -> green 5/5"]
    # The five lines come after the re-record lines.
    assert out[4].startswith("suite: ")
    assert out[7] == "stale (1): case-b"
    stored = json.loads((stage["root"] / gate.BASELINE_NAME).read_text("utf-8"))
    assert stored["stale"] == ["case-b"], "the baseline stores the set after"


def test_a_green_rerecord_clears_the_red_of_its_case(stage, capsys):
    """
    A stale case fails its replay, so the suite run counts it as a red.

    A re-record that greens the case clears that red. A case whose plain run
    still fails stays a red like any other.
    """
    stage["log"] = "..F.F\n2 failed, 3 passed in 1.00s\n"
    stage["failed"] = {_node("case-a"), _node("case-b")}
    stage["stale"] = {"case-a", "case-b"}
    stage["keeps"] = {"case-b"}

    assert _run(stage, "--baseline", rerecord=True) == 0
    out = _lines(capsys)
    assert out[:4] == ["rerecording 2 stale cases, five live runs each, on qwen3:8b",
                       "rerecorded case-a: STALE -> green 5/5, red cleared",
                       "rerecorded case-b: STALE -> STALE",
                       "note: 1 reds cleared by re-record. "
                       "The suite line still counts them."]
    # The note comes before the five lines, so `suite:` stays in the last five.
    assert out[4].startswith("suite: ")
    stored = json.loads((stage["root"] / gate.BASELINE_NAME).read_text("utf-8"))
    assert stored["failed"] == [_node("case-b")]


def test_a_red_that_failed_stale_is_rerecorded_and_its_red_clears(
        stage, capsys):
    """
    `status` can read a case green while the suite fails it `STALE`.

    The failure text in the log names it (observed: frame 89, 2026-09-29,
    `L1-DV-give-the-new-parameters-defaults`). A red without `STALE` is a red.
    """
    stage["log"] = (
        "..FF\n"
        f"FAILED {_node('case-a')} - Failed: STALE case-a: no recording for "
        "the current prompt\n"
        f"FAILED {_node('case-b')} - AssertionError: wrong verb\n"
        f"FAILED {_node('case-c')} - AssertionError: said STALE too early\n"
        "3 failed, 2 passed in 1.00s\n")
    stage["failed"] = {_node("case-a"), _node("case-b"), _node("case-c")}

    assert _run(stage, "--baseline", rerecord=True) == 0
    assert stage["rerecorded"] == [("qwen3:8b", "case-a")]
    out = _lines(capsys)
    assert out[:3] == [
        "rerecording 1 stale cases, five live runs each, on qwen3:8b",
        "rerecorded case-a: green 5/5 -> green 5/5, stale by its failure, "
        "red cleared",
        "note: 1 reds cleared by re-record. The suite line still counts them."]
    assert out[6] == "stale (0): none"
    stored = json.loads((stage["root"] / gate.BASELINE_NAME).read_text("utf-8"))
    assert stored["failed"] == [_node("case-b"), _node("case-c")], (
        "a message that quotes the word later is a red, not a stale case")

    # Under the flag nothing runs, and the stale line names the case and why.
    capsys.readouterr()
    stage["rerecorded"].clear()
    assert _run(stage, "--baseline") == 0
    assert stage["rerecorded"] == []
    assert _lines(capsys)[3] == "stale (1): case-a (stale by its failure)"


def test_a_stale_failure_whose_plain_run_fails_is_a_measured_red(stage, capsys):
    """After a re-record ran, the case is a red, so the next gate spends nothing."""
    stage["log"] = (
        "..F\n"
        f"FAILED {_node('case-a')} - Failed: STALE case-a: no recording for "
        "the current prompt\n"
        "1 failed, 2 passed in 1.00s\n")
    stage["failed"] = {_node("case-a")}
    stage["keeps"] = {"case-a"}

    assert _run(stage, "--baseline", rerecord=True) == 0
    assert stage["rerecorded"] == [("qwen3:8b", "case-a")]
    out = _lines(capsys)
    assert out[1] == ("rerecorded case-a: green 5/5 -> green 5/5, "
                      "stale by its failure")
    assert out[5] == "stale (0): none"
    stored = json.loads((stage["root"] / gate.BASELINE_NAME).read_text("utf-8"))
    assert stored["failed"] == [_node("case-a")]
    assert stored["stale"] == []


def test_a_read_that_raises_after_the_rerecords_keeps_what_they_earned(
        stage, capsys, monkeypatch):
    """
    The suite run is spent, so a broken read keeps the gate's report.

    Every re-record already ran, so its cleared red stays cleared.
    """
    first_read = gate._states
    reads = []

    def states(model):
        reads.append(model)
        if len(reads) > 1:
            raise RuntimeError("database is locked")
        return first_read(model)

    monkeypatch.setattr(gate, "_states", states)
    stage["log"] = "..F\n1 failed, 2 passed in 1.00s\n"
    stage["failed"] = {_node("case-a")}
    stage["stale"] = {"case-a"}

    assert _run(stage, "--baseline", rerecord=True) == 0
    out = _lines(capsys)
    assert out[1:4] == [
        "note: re-record stopped: RuntimeError('database is locked')",
        "rerecorded case-a: STALE -> unread, red cleared",
        "note: 1 reds cleared by re-record. The suite line still counts them."]
    assert out[4].startswith("suite: ")
    assert out[7] == "stale (1): case-a", "the set from before the re-record"
    stored = json.loads((stage["root"] / gate.BASELINE_NAME).read_text("utf-8"))
    assert stored["stale"] == ["case-a"]
    assert stored["failed"] == [], "the red the re-record earned stays cleared"


def test_a_rerecord_that_raises_still_prints_the_five_lines(
        stage, capsys, monkeypatch):
    def broken(env, case_id, log):
        raise RuntimeError("database is locked")

    monkeypatch.setattr(gate, "_rerecord", broken)
    stage["stale"] = {"case-a", "case-b"}

    assert _run(stage, "--baseline", rerecord=True) == 0
    out = _lines(capsys)
    assert out[1:3] == [
        "note: re-record stopped: RuntimeError('database is locked')",
        "note: not rerecorded: case-a, case-b"]
    assert out[3].startswith("suite: ")
    assert out[6] == "stale (2): case-a, case-b"


def test_the_real_rerecord_runs_refresh_then_plain(tmp_path, monkeypatch):
    """The body of `_rerecord`, with `subprocess.run` and `node_of` stubbed."""
    node = _node("case-a")
    runs = []
    codes = []
    cwds = []

    class Done:
        def __init__(self, code):
            self.returncode = code

    def run(argv, cwd, env, stdout, stderr):
        runs.append((list(argv), dict(env)))
        cwds.append(cwd)
        stdout.write(f"pytest output {len(runs)}\n")
        return Done(codes.pop(0))

    monkeypatch.delenv("ROTA_PROFILE", raising=False)
    monkeypatch.setattr(gate.subprocess, "run", run)
    monkeypatch.setattr(gate, "node_of",
                        lambda case_id: node if case_id == "case-a" else None)
    log = tmp_path / "gate.log"
    _write(log, "suite\n")
    env = {"ROTA_MODEL": "qwen3:8b", "KEEP": "1"}

    codes[:] = [1, 0]
    assert gate._rerecord(env, "case-a", log) == node
    assert len(runs) == 2
    (first_argv, first), (second_argv, second) = runs
    assert first_argv == second_argv and node in first_argv
    # One process, and the suite's `lastfailed` stays for the flaky check.
    assert "-n0" in first_argv
    assert first_argv[first_argv.index("-p") + 1] == "no:cacheprovider"
    assert cwds == [str(gate.repo_root())] * 2
    assert first["ROTA_REFRESH"] == "1"
    assert "ROTA_REFRESH" not in second
    for run_env in (first, second):
        assert run_env["ROTA_L1"] == "1" and run_env["ROTA_MODEL"] == "qwen3:8b"
        assert "ROTA_NUM_CTX" in run_env and run_env["KEEP"] == "1"
    text = log.read_text("utf-8")
    assert text.index("case-a: refresh run") < text.index("pytest output 1")
    assert text.index("case-a: plain run") < text.index("pytest output 2")
    assert text.index("pytest output 1") < text.index("case-a: plain run")

    runs.clear()
    codes[:] = [0, 1]
    assert gate._rerecord(env, "case-a", log) is None, "the plain run decides"

    runs.clear()
    assert gate._rerecord(env, "case-z", log) is None
    assert runs == []
    assert "== rerecord case-z: no test holds the case" in log.read_text("utf-8")


def test_the_flag_turns_the_rerecord_off(stage, capsys):
    stage["stale"] = {"case-a"}

    assert _run(stage, "--baseline") == 0
    assert stage["rerecorded"] == []
    assert not any(line.startswith("rerecorded") for line in _lines(capsys))


def test_an_absent_register_makes_no_rerecord(stage, capsys):
    stage["stale"] = None

    assert _run(stage, "--baseline", rerecord=True) == 0
    assert stage["rerecorded"] == []
    assert not any(line.startswith("rerecorded") for line in _lines(capsys))


def test_the_rerecord_command_is_the_one_casestatus_prints(monkeypatch):
    """The gate runs the reader's line, so the key it records is the key shown."""
    monkeypatch.delenv("ROTA_PROFILE", raising=False)
    node = "tests/rota/test_l1.py::test_l1_case[L1-DV-a-case]"
    names, argv = gate.rerecord_argv(
        f"ROTA_L1=1 ROTA_MODEL=qwen3:8b ROTA_NUM_CTX=8192 python -m pytest "
        f"'{node}' -q")
    assert names == {"ROTA_L1": "1", "ROTA_MODEL": "qwen3:8b",
                     "ROTA_NUM_CTX": "8192"}
    assert argv[1:] == ["-m", "pytest", node, "-q"]


WHEN = "2026-10-04T05:00:00+01:00"
HELD = {"models": [{"name": "qwen3.5:9b", "expires_at": WHEN}]}


def _held(monkeypatch, ps):
    """Fake the main card's `/api/ps`. Return the list of the URLs asked."""
    asked = []

    def get_json(url):
        asked.append(url)
        return ps

    monkeypatch.setattr(gate, "_get_json", get_json)
    return asked


def test_a_held_card_names_each_model_with_its_expiry(monkeypatch):
    asked = _held(monkeypatch, {"models": [
        {"name": "qwen3.5:9b", "expires_at": WHEN}, {"name": "qwen3:8b"}]})
    assert gate.main_card_held({}) == [f"qwen3.5:9b until {WHEN}", "qwen3:8b"]
    assert asked == ["http://127.0.0.1:11434/api/ps"]


def test_the_probe_asks_the_server_the_children_use(monkeypatch):
    asked = _held(monkeypatch, HELD)
    gate.main_card_held({"OLLAMA_HOST": "http://elsewhere:7/"})
    assert asked == ["http://elsewhere:7/api/ps"]


@pytest.mark.parametrize("ps", [
    None,
    {"models": []},
    {"models": {"name": "qwen3.5:9b"}},
    {"models": [{"name": None}, "qwen3.5:9b", None]},
], ids=["no answer", "empty", "models not a list", "no usable entry"])
def test_a_free_or_malformed_reply_reads_as_free(monkeypatch, ps):
    _held(monkeypatch, ps)
    assert gate.main_card_held({}) == []


def test_a_reply_cut_short_reads_as_no_answer(monkeypatch):
    import http.client
    import urllib.request

    class Cut:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            raise http.client.IncompleteRead(b"{\"mod")

    monkeypatch.setattr(urllib.request, "urlopen", lambda url, timeout: Cut())
    assert gate._get_json("http://127.0.0.1:1/api/ps") is None


def test_a_free_card_rerecords_and_prints_no_card_line(stage, capsys):
    stage["stale"] = {"case-a"}
    assert _run(stage, "--baseline", rerecord=True) == 0
    assert stage["rerecorded"] == [("qwen3:8b", "case-a")]
    out = _lines(capsys)
    assert not any(line.startswith("main card: ") for line in out)
    assert out[0].startswith("rerecording 1 stale cases")


def test_a_held_card_makes_the_rerecords_wait(stage, monkeypatch, capsys):
    """
    The stale cases stay on the stale line, their replay reds are not new
    reds, and the last line and the exit code say they wait.
    """
    _held(monkeypatch, HELD)
    _baseline(stage["root"])
    stage["stale"] = {"case-a", "case-b"}
    stage["log"] = _stale_log("case-a")
    stage["failed"] = {_node("case-a")}
    assert _run(stage, rerecord=True) == gate.WAIT_EXIT
    assert stage["rerecorded"] == []
    assert stage["reran"] == []
    out = _lines(capsys)
    assert out[0] == (f"main card: held by qwen3.5:9b until {WHEN}, "
                      "re-records wait")
    assert out[1].startswith("suite: ")
    assert out[2] == "new reds (0): none"
    assert out[4] == "stale (2): case-a, case-b (+2 -0 against baseline)"
    assert out[-1] == "exit 3: 2 stale cases wait for the main card"


def _stale_log(case_id):
    return (f"FAILED {_node(case_id)} - Failed: STALE no cassette\n"
            "1 failed, 1 passed in 2.00s\n")


def test_a_held_card_stores_no_baseline(stage, monkeypatch, capsys):
    """A waiting run holds no red for its stale cases, so it is no baseline."""
    _held(monkeypatch, HELD)
    stage["stale"] = {"case-a"}
    stage["log"] = _stale_log("case-a")
    stage["failed"] = {_node("case-a")}
    assert _run(stage, "--baseline", rerecord=True) == gate.WAIT_EXIT
    assert not (stage["root"] / gate.BASELINE_NAME).exists()
    out = _lines(capsys)
    assert ("note: baseline not stored, because stale cases wait for the "
            "main card") in out
    assert not any(line.startswith("note: baseline stored") for line in out)


def test_a_known_red_of_a_stale_case_stays_a_red(stage, monkeypatch, capsys):
    """Only a `STALE` red waits. A red for another reason is not gone."""
    _held(monkeypatch, HELD)
    _baseline(stage["root"], failed=[_node("case-a")], summary="1 failed")
    stage["stale"] = {"case-a"}
    stage["log"] = (f"FAILED {_node('case-a')} - AssertionError: wrong\n"
                    "1 failed, 1 passed in 2.00s\n")
    stage["failed"] = {_node("case-a")}
    assert _run(stage, rerecord=True) == gate.WAIT_EXIT
    out = _lines(capsys)
    assert out[2] == "new reds (0): none"
    assert out[3] == "reds gone (0): none"


def test_a_new_red_keeps_exit_one_beside_the_wait(stage, monkeypatch, capsys):
    _held(monkeypatch, HELD)
    _baseline(stage["root"])
    stage["stale"] = {"case-a"}
    stage["log"] = LOG_MIXED
    stage["failed"] = {SPACED}
    stage["after"] = {SPACED}
    assert _run(stage, rerecord=True) == 1
    out = _lines(capsys)
    assert out[-2] == "note: 1 stale cases wait for the main card"
    assert out[-1] == "exit 1: 1 new reds, 0 of them flaky"


def test_rerecord_now_rerecords_on_a_held_card(stage, monkeypatch, capsys):
    _held(monkeypatch, HELD)
    stage["stale"] = {"case-a"}
    assert _run(stage, "--baseline", "--rerecord-now", rerecord=True) == 0
    assert stage["rerecorded"] == [("qwen3:8b", "case-a")]
    out = _lines(capsys)
    assert out[0] == (f"main card: held by qwen3.5:9b until {WHEN}, "
                      "re-records run on --rerecord-now")


def test_the_gate_moves_no_child_to_another_server(stage, monkeypatch):
    _held(monkeypatch, HELD)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    monkeypatch.delenv("ROTA_LLM_TIMEOUT", raising=False)
    _run(stage, rerecord=True)
    assert "OLLAMA_HOST" not in stage["env"]
    assert "ROTA_LLM_TIMEOUT" not in stage["env"]


