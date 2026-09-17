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
             "stale": set(), "head": HEAD, "dirty": False,
             "rerun": "", "after": None, "env": None, "reran": []}

    def run_suite(env, log):
        state["env"] = env
        _write(log, state["log"])
        if state["failed"] is not None:
            _cache(tmp_path, state["failed"])
        return state["code"]

    def rerun(env, ids):
        state["reran"].append(list(ids))
        if state["after"] is not None:
            _cache(tmp_path, state["after"])
        return state["rerun"]

    monkeypatch.setattr(gate, "TEMP_ROOT", tmp_path / "gatetmp")
    monkeypatch.setattr(gate, "_run_suite", run_suite)
    monkeypatch.setattr(gate, "_rerun", rerun)
    monkeypatch.setattr(gate, "_stale", lambda model: set(state["stale"]))
    monkeypatch.setattr(gate, "_head", lambda: state["head"])
    monkeypatch.setattr(gate, "_dirty", lambda: state["dirty"])
    return state


def _run(stage, *argv):
    return gate.main(list(argv), root=stage["root"])


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


def test_a_child_that_did_not_run_says_so_and_exits_one(stage, capsys):
    stage["code"], stage["log"], stage["failed"] = 4, "", None
    assert _run(stage) == 1

    out = _lines(capsys)
    assert out[0] == "suite: did not run (pytest exit 4)"
    assert not (stage["root"] / gate.BASELINE_NAME).exists(), (
        "a run that did not measure anything must not become the baseline")


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
    assert out[0] == "suite: 3 failed, 1 passed, 1 error"
    assert out[1] == f"new reds (1): {SPACED}"
    assert out[2] == f"reds gone (1): {BRACKET}"
    assert out[3] == "stale (2): case-a, case-c (+1 -1 against baseline)"


def test_a_stale_set_that_did_not_move_carries_no_delta(stage, capsys):
    _baseline(stage["root"], stale=["case-a"])
    stage["stale"] = {"case-a"}

    assert _run(stage) == 0
    assert _lines(capsys)[3] == "stale (1): case-a"


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


def test_a_new_red_that_passes_on_the_rerun_is_called_flaky(stage, capsys):
    _baseline(stage["root"], failed=[])
    stage["log"], stage["failed"] = LOG_MIXED, {SPACED}
    stage["after"] = set()          # the re-run dropped it from the cache
    stage["rerun"] = "1 passed in 2.20s\n"

    assert _run(stage) == 1, "a new red still closes the gate"
    assert f"flaky: {SPACED}" in capsys.readouterr().out


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
