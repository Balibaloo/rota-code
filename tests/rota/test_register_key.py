"""
The register's key: what a result was earned under, and what the report
matches on.

Frame 54 (2026-09-21). A recording is identified by seven things and a result
was identified by three, so `casestatus` could not match what the cassette key
covers. One narrow key gave two opposite symptoms: a green case read stale,
and a case the suite could not replay read green.

These pin the five columns, the writer that stamps them, the match that reads
them, the model the report reads under, and the door that refuses a replay at
a key the register does not hold. Every test builds its own small register in
`tmp_path`: the real one is 780 MB of evidence and no test writes to it.
"""
from __future__ import annotations

import json
import os
import subprocess
import sqlite3
import sys

import pytest

import rota_serial_plugin
from rota import paths
from rota.llm import llm
from rota.llm.cassettes import (KEY_COLUMNS, key_for, open_dev_db,
                                record_case_run)
from rota.llm.llm import DEFAULT_NUM_CTX, Pins
from rota.testkit import fixtures
from rota.tools import casestatus

#: One real role and one real mode, so `instructions_for` composes the same
#: brief the tier would and the hash is earned rather than invented.
CASE = {"id": "L1-LI-the-register-key", "role": "liaison", "prompt": "converse",
        "runs": 1, "pass": 1}
MODEL = "qwen3:8b"

#: `case_runs` before frame 54. The migration has to reach a register that was
#: recorded against this shape, because the committed one was.
OLD_SCHEMA = """
CREATE TABLE case_runs (
    case_id      TEXT NOT NULL,
    model        TEXT NOT NULL,
    prompt_hash  TEXT NOT NULL,
    run_no       INTEGER NOT NULL,
    load_id      TEXT NOT NULL DEFAULT '',
    passed       INTEGER NOT NULL,
    problems     TEXT NOT NULL DEFAULT '[]',
    transcript   TEXT NOT NULL DEFAULT '[]',
    seq          INTEGER NOT NULL,
    PRIMARY KEY (case_id, model, prompt_hash, run_no, seq)
);
"""


@pytest.fixture
def register(tmp_path, monkeypatch):
    """A register of one case, read by `casestatus` as the real one is."""
    monkeypatch.delenv("ROTA_PROFILE", raising=False)
    monkeypatch.setattr(paths, "DEV_DB", tmp_path / "dev.db")
    monkeypatch.setattr(casestatus, "_cases", lambda: [dict(CASE)])
    return open_dev_db(tmp_path / "dev.db")


def _record(db, pins: Pins, **kw) -> None:
    """One run of the case, stamped the way the tier stamps it."""
    stamp = pins.with_prompt(fixtures.instructions_for(CASE))
    record_case_run(db, CASE["id"], stamp, 1, True, [],
                    [{"say": "ok"}], **kw)


def _state(model: str = MODEL) -> str:
    rows = casestatus.status(model)
    assert len(rows) == 1
    return rows[0]["state"]


def test_the_writer_stamps_the_whole_key(register):
    """Five columns, from the pins the run used and the text it was sent."""
    pins = Pins(model=MODEL, temperature=0.0, num_ctx=8192, think=True)
    _record(register, pins, system="the system text", protocol="native")

    row = register.execute(
        "SELECT num_ctx, temperature, protocol, extras, system_hash "
        "FROM case_runs").fetchone()
    assert (row["num_ctx"], row["temperature"], row["protocol"]) == (
        8192, 0.0, "native")
    assert row["extras"] == json.dumps({"think": True}, sort_keys=True)
    assert row["system_hash"] and row["system_hash"] != ""


def test_a_recording_at_the_ambient_window_reads_green(register):
    """The control. Without it every test below could pass for the wrong
    reason, because a case id that never matches also reads stale."""
    _record(register, Pins(model=MODEL, temperature=0.0), system="s")
    assert _state() == "green"


def test_a_window_change_makes_a_case_read_stale(register):
    """`num_ctx` is in the cassette key, so a recording at another window is
    not evidence about this run. It was the largest cause of a false state:
    `ROTA_NUM_CTX=16384` misses every cassette in the register and the report
    still read the old greens."""
    _record(register, Pins(model=MODEL, temperature=0.0, num_ctx=8192),
            system="s")
    assert DEFAULT_NUM_CTX != 8192, "the ambient window is what the report wants"
    assert _state() == "STALE"


def test_a_think_pin_change_makes_a_case_read_stale(register, monkeypatch):
    """`ROTA_PROFILE` sets the think pin per model, and a set pin keys the
    recording. One run under a profile and one without it measure two
    different things, so the report must not read one as the other."""
    thinking_model = "qwen3.5:9b"
    _record(register, Pins(model=thinking_model, temperature=0.0), system="s")
    assert _state(thinking_model) == "green", "recorded and read with no profile"

    # The profile ships with the repository and sets `think` for this model.
    monkeypatch.setenv("ROTA_PROFILE", "local-gemma-critic")
    assert _state(thinking_model) == "STALE"


def test_a_native_recording_does_not_answer_for_a_text_run(register):
    """Native tool calling and the `TOOL:` text protocol get different replies
    to one prompt and fail in different ways. 18570 of the register's 18604
    cassettes key as text and none as native."""
    _record(register, Pins(model=MODEL, temperature=0.0), system="s",
            protocol="native")
    assert _state() == "STALE"


def test_the_match_keeps_reading_across_a_second_load(register):
    """`load_id` stays out of the match. It is `model@epoch//7200`, so matching
    on it would stale every case two hours after its recording."""
    pins = Pins(model=MODEL, temperature=0.0)
    _record(register, pins, system="s")
    register.execute("UPDATE case_runs SET load_id = 'qwen3:8b@1'")
    assert _state() == "green"


def test_open_dev_db_migrates_an_old_register_and_twice_is_a_no_op(tmp_path):
    """The committed register predates the columns, so the opener adds them.
    A default is a write-off and not a measurement: an old row reads 12288,
    0.0, text and no extras, and its system text is unknown."""
    path = tmp_path / "old.db"
    raw = sqlite3.connect(str(path))
    raw.executescript(OLD_SCHEMA)
    raw.execute("INSERT INTO case_runs (case_id, model, prompt_hash, run_no, "
                "passed, seq) VALUES ('c', 'm', 'h', 1, 1, 1)")
    raw.commit()
    raw.close()

    conn = open_dev_db(path)
    row = conn.execute("SELECT * FROM case_runs").fetchone()
    assert (row["num_ctx"], row["temperature"], row["protocol"],
            row["extras"], row["system_hash"]) == (12288, 0.0, "text", "{}", "")
    conn.close()

    again = open_dev_db(path)
    have = {r["name"] for r in again.execute("PRAGMA table_info(case_runs)")}
    assert {name for name, _ in KEY_COLUMNS} <= have
    assert again.execute("SELECT COUNT(*) n FROM case_runs").fetchone()["n"] == 1
    assert again.execute("SELECT passed FROM case_runs").fetchone()["passed"] == 1


def test_every_case_result_says_what_the_model_was_told():
    """
    Found by measuring the rows a suite run wrote, not by reading the code.
    `run_chain` returns early on three paths, a chain that ends at leg one
    takes one of them, and those results stamped no system text at all. A
    result that cannot say what the model was told is the fault this frame
    repairs, in a new place.
    """
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path(fixtures.__file__).read_text(encoding="utf-8"))
    calls = [node for node in ast.walk(tree)
             if isinstance(node, ast.Call)
             and getattr(node.func, "id", "") == "CaseResult"]
    assert len(calls) >= 5, "the fixtures build a result on more paths than this"
    silent = [node.lineno for node in calls
              if "systems" not in {kw.arg for kw in node.keywords}]
    assert not silent, f"a result with no system text at lines {silent}"


def test_the_report_names_the_model_it_read(monkeypatch):
    """Frame 60's clause, moved here. The default was `llama3.1:8b` and the
    report read no environment, so the bare command said 67 stale and
    `--model qwen3:8b` said 0 stale on one register. Both were true."""
    from rota.tools.gate import FALLBACK_MODEL

    monkeypatch.delenv("ROTA_MODEL", raising=False)
    assert casestatus.model_for() == FALLBACK_MODEL, "the model the gate replays"

    monkeypatch.setenv("ROTA_MODEL", "qwen3.5:9b")
    assert casestatus.model_for() == "qwen3.5:9b", "the ambient model wins"
    assert casestatus.model_for("named:8b") == "named:8b", "a named model wins"

    # And the count says which model it is about, beside the count itself.
    line = casestatus.render([], model="qwen3:8b").splitlines()[1]
    assert "qwen3:8b" in line and str(DEFAULT_NUM_CTX) in line


# ---------------------------------------------------------------------------
# The door: a replay at a key the register does not hold
# ---------------------------------------------------------------------------

#: The model a shipped profile sets the think pin for, so the door's think
#: check runs the real rule and not a stand-in.
THINKING_MODEL = "qwen3.5:9b"
PROFILE = "local-gemma-critic"


def _small_register(tmp_path, recorded) -> "paths.Path":
    """
    A register of one cassette per pin set, keyed the way the runner keys one.

    The text is stored beside the key, as the real register stores it, because
    the door recomputes the key from that text to answer for the think pin.
    """
    path = tmp_path / "small.db"
    db = open_dev_db(path)
    for number, pins in enumerate(recorded):
        system, user = f"system {number}", f"user {number}"
        db.execute(
            "INSERT INTO cassettes (key, model, temperature, num_ctx, "
            "prompt_hash, system, user, completion, backend) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (key_for(system, user, pins), pins.model, pins.temperature,
             pins.num_ctx, "h", system, user, "ok", "test"))
    db.commit()
    db.close()
    return path


@pytest.fixture
def door(tmp_path, monkeypatch):
    """
    A replay, a register of one model at one window, and the ambient pins
    under control.

    `DEFAULT_MODEL` and `DEFAULT_NUM_CTX` are read once at import, so the test
    moves the constants rather than the environment. The environment still
    decides the think pin, because `think_for` reads it per call.
    """
    monkeypatch.setattr(paths, "DEV_DB", _small_register(
        tmp_path, [Pins(model=THINKING_MODEL, temperature=0.0, num_ctx=12288)]))
    for name in ("ROTA_L1", "ROTA_T1", "ROTA_REFRESH", "ROTA_PROFILE"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(llm, "DEFAULT_MODEL", THINKING_MODEL)
    monkeypatch.setattr(llm, "DEFAULT_NUM_CTX", 12288)
    return monkeypatch


def test_a_replay_at_the_registers_own_key_is_not_refused(door):
    """The control. A door that refused everything would pass every test
    below and stop the suite."""
    rota_serial_plugin.refuse_a_key_the_register_does_not_hold()


def test_a_replay_at_a_window_the_register_lacks_is_refused(door):
    """`rota/HARDWARE_GUIDE.md:159` tells the reader to set 16384, and no
    cassette in the register holds it."""
    door.setattr(llm, "DEFAULT_NUM_CTX", 16384)
    with pytest.raises(pytest.UsageError) as caught:
        rota_serial_plugin.refuse_a_key_the_register_does_not_hold()
    said = str(caught.value)
    assert "ROTA_NUM_CTX" in said, "the refusal names the variable"
    assert "16384" in said, "and the value it holds"
    assert "12288" in said, "and what the register does hold"


def test_a_replay_on_a_model_the_register_lacks_is_refused(door):
    """Frame 60's fault: the tag moved and nothing said so."""
    door.setattr(llm, "DEFAULT_MODEL", "mistral:7b")
    with pytest.raises(pytest.UsageError) as caught:
        rota_serial_plugin.refuse_a_key_the_register_does_not_hold()
    said = str(caught.value)
    assert "ROTA_MODEL" in said and "mistral:7b" in said
    assert THINKING_MODEL in said, "the models the register does hold"


def test_a_think_pin_the_register_never_recorded_is_refused(door):
    """The third variable. The pin is inside the key's hash and `cassettes`
    has no column for it, so the door recomputes the key from the row's own
    text. The register above holds this model with the pin unset."""
    door.setenv("ROTA_PROFILE", PROFILE)
    assert llm.think_for(THINKING_MODEL) is True, "the shipped profile's rule"
    with pytest.raises(pytest.UsageError) as caught:
        rota_serial_plugin.refuse_a_key_the_register_does_not_hold()
    said = str(caught.value)
    assert "ROTA_PROFILE" in said and PROFILE in said
    assert "think pin is True" in said


def test_a_think_pin_the_register_did_record_passes(tmp_path, monkeypatch):
    """And the other way, or the door refuses the 34 recordings the register
    holds at `think=True`. Measured on the real register, 2026-09-21."""
    monkeypatch.setattr(paths, "DEV_DB", _small_register(tmp_path, [
        Pins(model=THINKING_MODEL, temperature=0.0, num_ctx=12288, think=True)]))
    for name in ("ROTA_L1", "ROTA_T1", "ROTA_REFRESH"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("ROTA_PROFILE", PROFILE)
    monkeypatch.setattr(llm, "DEFAULT_MODEL", THINKING_MODEL)
    monkeypatch.setattr(llm, "DEFAULT_NUM_CTX", 12288)
    rota_serial_plugin.refuse_a_key_the_register_does_not_hold()


@pytest.mark.parametrize("switch", ["ROTA_L1", "ROTA_T1", "ROTA_REFRESH"])
def test_a_recording_run_is_not_refused(door, switch):
    """`ROTA_L1=1 ROTA_MODEL=<new model>` is how a benchmark column is
    recorded, and the register holds 11 models first recorded that way. A door
    that refused an unheld tuple would refuse every first recording."""
    door.setattr(llm, "DEFAULT_NUM_CTX", 16384)
    door.setenv(switch, "1")
    rota_serial_plugin.refuse_a_key_the_register_does_not_hold()


def test_an_absent_register_gates_nothing(tmp_path, monkeypatch):
    """A fresh checkout has no cassettes. The tiers skip themselves there, and
    the door has nothing to compare against."""
    monkeypatch.setattr(paths, "DEV_DB", tmp_path / "nothing.db")
    for name in ("ROTA_L1", "ROTA_T1", "ROTA_REFRESH"):
        monkeypatch.delenv(name, raising=False)
    rota_serial_plugin.refuse_a_key_the_register_does_not_hold()


def test_end_to_end_the_door_stops_a_real_run(tmp_path):
    """
    The wiring, not the function.

    The same reason `test_pytest_parallelism.py` runs a child: three conftest
    attempts at that mechanism failed silently, and a door that never fires
    looks exactly like a door that passed. This runs the cheapest real file in
    the repository, so `pytest.ini` and the `-p` plugin both apply.
    """
    register = _small_register(
        tmp_path, [Pins(model="llama3.1:8b", temperature=0.0, num_ctx=12288)])
    env = {**os.environ, "ROTA_DEV_DB": str(register), "ROTA_MODEL": "llama3.1:8b"}
    env.pop("ROTA_PROFILE", None)
    for switch in ("ROTA_L1", "ROTA_T1", "ROTA_REFRESH"):
        env.pop(switch, None)

    def run(extra):
        return subprocess.run(
            [sys.executable, "-m", "pytest", "tests/rota/test_bounds.py", "-q"],
            capture_output=True, text=True, cwd=".", env={**env, **extra})

    refused = run({"ROTA_NUM_CTX": "16384"})
    assert "ROTA_NUM_CTX" in refused.stdout + refused.stderr, refused.stdout[:800]
    assert "2 passed" not in refused.stdout, "the run must not proceed"

    allowed = run({"ROTA_NUM_CTX": "12288"})
    assert "2 passed" in allowed.stdout, allowed.stdout[:800]


def test_the_stale_message_names_the_model_and_the_window():
    """
    Frame 60. The suite told the reader to re-earn a case with a command that
    named no model, so following the repository's own instruction re-recorded
    against whatever was ambient.
    """
    said = fixtures.rerecord_command(
        Pins(model="qwen3:8b", temperature=0.0, num_ctx=8192),
        "tests/rota/test_l1.py")
    assert said == ("ROTA_L1=1 ROTA_MODEL=qwen3:8b ROTA_NUM_CTX=8192 "
                    "python -m pytest tests/rota/test_l1.py -q")

    # And no tier prints the model-less form any more.
    import pathlib

    for name in ("test_l1.py", "test_l3.py", "test_gauntlet.py"):
        text = (pathlib.Path(fixtures.__file__).parent.parent.parent
                / "tests" / "rota" / name).read_text(encoding="utf-8")
        assert "ROTA_L1=1 python -m pytest" not in text, name


def test_the_stale_message_names_the_profile_when_one_is_set(monkeypatch):
    """A set think pin keys the recording, so a re-record without the profile
    earns a different key."""
    monkeypatch.setenv("ROTA_PROFILE", PROFILE)
    said = fixtures.rerecord_command(
        Pins(model=THINKING_MODEL, temperature=0.0), "tests/rota/test_l3.py")
    assert f"ROTA_PROFILE={PROFILE}" in said
