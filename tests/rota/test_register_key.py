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
import time

import pytest

import rota_serial_plugin
from rota import paths
from rota.llm import llm
from rota.llm.cassettes import (KEY_COLUMNS, MISS_MARKERS, UNBUILT, key_for,
                                open_dev_db, record_case_run, system_hash)
from rota.llm.llm import DEFAULT_NUM_CTX, Pins
from rota.roles import prompts
from rota.testkit import fixtures
from rota.tools import casestatus, migrate_register

#: One real role and one real mode, so `instructions_for` composes the same
#: brief the tier would and the hash is earned rather than invented.
#:
#: The inbound message is what makes the case composable. The brief is keyed
#: by `mode_of`, which reads `prompt:`, and the working set is keyed by
#: `_mode_key`, which reads the verb off the wake. A case with no message
#: wakes with an empty verb, and the two rules then pick two modes.
CASE = {"id": "L1-LI-the-register-key", "role": "liaison", "prompt": "converse",
        "runs": 1, "pass": 1,
        "inbound": {"from": "principal", "to": "liaison", "verb": "converse"}}
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
    """
    One run of the case, stamped the way the tier stamps it.

    The system text is the case's own, composed, because the report now
    matches on its digest. A stand-in string here would read stale for the
    reason the test is not about.
    """
    stamp = pins.with_prompt(fixtures.instructions_for(CASE))
    kw.setdefault("system", fixtures.system_text_for(CASE))
    record_case_run(db, CASE["id"], stamp, 1, True, [],
                    [{"say": "ok"}], **kw)


def _row(model: str = MODEL) -> dict:
    """The report's one line about the case this file records."""
    rows = casestatus.status(model)
    assert len(rows) == 1
    return rows[0]


def _state(model: str = MODEL) -> str:
    return _row(model)["state"]


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
    _record(register, Pins(model=MODEL, temperature=0.0))
    assert _state() == "green"


def test_a_window_change_makes_a_case_read_stale(register):
    """`num_ctx` is in the cassette key, so a recording at another window is
    not evidence about this run. It was the largest cause of a false state:
    `ROTA_NUM_CTX=16384` misses every cassette in the register and the report
    still read the old greens."""
    _record(register, Pins(model=MODEL, temperature=0.0, num_ctx=8192))
    assert DEFAULT_NUM_CTX != 8192, "the ambient window is what the report wants"
    assert _state() == "STALE"


def test_a_think_pin_change_makes_a_case_read_stale(register, monkeypatch):
    """`ROTA_PROFILE` sets the think pin per model, and a set pin keys the
    recording. One run under a profile and one without it measure two
    different things, so the report must not read one as the other."""
    thinking_model = "qwen3.5:9b"
    _record(register, Pins(model=thinking_model, temperature=0.0))
    assert _state(thinking_model) == "green", "recorded and read with no profile"

    # The profile ships with the repository and sets `think` for this model.
    monkeypatch.setenv("ROTA_PROFILE", "local-gemma-critic")
    assert _state(thinking_model) == "STALE"


def test_a_native_recording_does_not_answer_for_a_text_run(register):
    """Native tool calling and the `TOOL:` text protocol get different replies
    to one prompt and fail in different ways. 18570 of the register's 18604
    cassettes key as text and none as native."""
    _record(register, Pins(model=MODEL, temperature=0.0), protocol="native")
    assert _state() == "STALE"


def test_the_match_keeps_reading_across_a_second_load(register):
    """`load_id` stays out of the match. It is `model@epoch//7200`, so matching
    on it would stale every case two hours after its recording."""
    pins = Pins(model=MODEL, temperature=0.0)
    _record(register, pins)
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
    looks exactly like a door that passed. These run real files, so
    `pytest.ini` and the `-p` plugin both apply.

    **And the other half, which the diff review found.** The door fired
    before collection, so it refused every pytest command in the repository:
    99 of the 99 test files at a window the register lacks, against 4 after
    the repair (observed: frame 54's fix pass, 2026-09-21). A file that calls
    no model must run.
    """
    register = _small_register(
        tmp_path, [Pins(model="llama3.1:8b", temperature=0.0, num_ctx=12288)])
    env = {**os.environ, "ROTA_DEV_DB": str(register), "ROTA_MODEL": "llama3.1:8b"}
    env.pop("ROTA_PROFILE", None)
    for switch in ("ROTA_L1", "ROTA_T1", "ROTA_REFRESH"):
        env.pop(switch, None)

    def run(path, extra):
        return subprocess.run(
            [sys.executable, "-m", "pytest", path, "-q"],
            capture_output=True, text=True, cwd=".", env={**env, **extra})

    # A file that reads the register, at a window nothing was recorded at.
    refused = run("tests/rota/test_t1_liaison.py", {"ROTA_NUM_CTX": "16384"})
    said = refused.stdout + refused.stderr
    assert "ROTA_NUM_CTX" in said, said[:800]
    assert "16384" in said and "12288" in said, said[:800]
    assert refused.returncode != 0, "the run must not proceed"

    # The same window, and a file that calls no model. This is the fix.
    quiet = run("tests/rota/test_bounds.py", {"ROTA_NUM_CTX": "16384"})
    assert "2 passed" in quiet.stdout, quiet.stdout[:800]

    # And the tier itself runs once the window matches what was recorded.
    allowed = run("tests/rota/test_t1_liaison.py", {"ROTA_NUM_CTX": "12288"})
    assert "ROTA_NUM_CTX" not in allowed.stdout + allowed.stderr, \
        allowed.stdout[:800]


def test_every_file_that_opens_the_register_calls_the_door():
    """
    A file that opens `paths.DEV_DB` replays, so it asks the door first.

    The door is called from the four tier files and not from a pytest hook,
    and that is measured rather than preferred. A hook that raises after
    collection runs on an xdist worker, because the controller does not
    collect, and the run ends in `INTERNALERROR: assert not crashitem` with
    the reason nowhere in the output (observed: frame 54's fix pass,
    2026-09-21). A tier added later without the call is a door that never
    opens for it, and nothing else would say so.
    """
    import pathlib

    here = pathlib.Path(__file__).parent
    readers, silent = [], []
    for path in sorted(here.glob("test_*.py")):
        text = path.read_text(encoding="utf-8")
        if "open_dev_db(paths.DEV_DB)" not in text:
            continue
        readers.append(path.name)
        if "refuse_a_key_the_register_does_not_hold()" not in text:
            silent.append(path.name)
    assert len(readers) >= 4, f"the pin found only {readers}"
    assert not silent, f"these read the register and never ask the door: {silent}"


def test_the_remedy_names_a_variable_to_set_when_nobody_set_one(door):
    """
    "unset the variable" moves nothing when nobody set the variable, and that
    was the remedy for the commonest refusal of all: no `ROTA_MODEL`, so the
    model defaults to one the register does not hold. A remedy that does not
    move the run is worse than none.
    """
    door.setattr(llm, "DEFAULT_MODEL", "mistral:7b")
    door.delenv("ROTA_MODEL", raising=False)
    with pytest.raises(pytest.UsageError) as caught:
        rota_serial_plugin.refuse_a_key_the_register_does_not_hold()
    said = str(caught.value)
    assert "set ROTA_MODEL to a model the register holds" in said
    assert "unset ROTA_MODEL" not in said, "it was never set"

    # And the other way, where unsetting it does move the run.
    door.setenv("ROTA_MODEL", "mistral:7b")
    with pytest.raises(pytest.UsageError) as caught:
        rota_serial_plugin.refuse_a_key_the_register_does_not_hold()
    assert "unset ROTA_MODEL, or set it to" in str(caught.value)


def test_a_register_recorded_only_with_the_pin_refuses_a_run_without_it(
        tmp_path, monkeypatch):
    """
    The think pin, guarded in both directions.

    The check fired only when a profile set the pin, so a register whose
    cassettes for the ambient model were all recorded at `think=True` passed
    a run with the pin unset, and then every cassette missed. That is the one
    failure the door exists to stop, and it was blind to half of it.
    """
    monkeypatch.setattr(paths, "DEV_DB", _small_register(tmp_path, [
        Pins(model=THINKING_MODEL, temperature=0.0, num_ctx=12288, think=True)]))
    for name in ("ROTA_L1", "ROTA_T1", "ROTA_REFRESH", "ROTA_PROFILE"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(llm, "DEFAULT_MODEL", THINKING_MODEL)
    monkeypatch.setattr(llm, "DEFAULT_NUM_CTX", 12288)

    with pytest.raises(pytest.UsageError) as caught:
        rota_serial_plugin.refuse_a_key_the_register_does_not_hold()
    said = str(caught.value)
    assert "think pin is unset" in said
    assert "set ROTA_PROFILE to a profile that sets the think pin" in said


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


# ---------------------------------------------------------------------------
# The migration out of the legacy clone
# ---------------------------------------------------------------------------


def _legacy(tmp_path, rows, cassettes, name="legacy.db"):
    """
    A source register: cassettes, and results earned under them.

    Built with `open_dev_db` rather than a second copy of the old DDL. The
    migration reads nine named columns from the source, so a source with the
    new columns behaves as the clone does, and the schema stays defined once.
    """
    path = tmp_path / name
    db = open_dev_db(path)
    for pins, system, user, completion, protocol in cassettes:
        db.execute(
            "INSERT INTO cassettes (key, model, temperature, num_ctx, "
            "prompt_hash, system, user, completion, backend) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (key_for(system, user, pins, protocol), pins.model,
             pins.temperature, pins.num_ctx, "h", system, user, completion,
             "test"))
    for seq, (case_id, model, transcript) in enumerate(rows, start=1):
        db.execute(
            "INSERT INTO case_runs (case_id, model, prompt_hash, run_no, "
            "passed, problems, transcript, seq) VALUES (?,?,?,1,1,'[]',?,?)",
            (case_id, model, "h", json.dumps(transcript), seq))
    db.close()
    return path


def _run(source, target):
    src = migrate_register.open_source(source)
    result = migrate_register.migrate(src, target)
    src.close()
    return result["tally"]


def _landed(target):
    db = sqlite3.connect(str(target))
    db.row_factory = sqlite3.Row
    rows = [dict(r) for r in db.execute("SELECT * FROM case_runs ORDER BY seq")]
    db.close()
    return rows


def test_a_row_lands_with_the_five_values_of_the_cassette_it_used(tmp_path):
    """
    The whole point of the migration. The four pins and the system hash come
    off the cassette that earned the row, so a migrated green is a green about
    a named key rather than about a default.
    """
    pins = Pins(model=MODEL, temperature=0.0, num_ctx=8192, think=True)
    source = _legacy(
        tmp_path,
        rows=[("L1-LI-the-register-key", MODEL, [{"say": "the reply"}])],
        cassettes=[(pins, "the system text", "the user text", "the reply",
                    "text")])
    tally = _run(source, tmp_path / "new.db")

    assert tally["migrated"] == 1
    row = _landed(tmp_path / "new.db")[0]
    assert (row["num_ctx"], row["temperature"], row["protocol"]) == (
        8192, 0.0, "text")
    assert row["extras"] == json.dumps({"think": True}, sort_keys=True)
    assert row["system_hash"] == system_hash("the system text")


def test_a_row_with_no_identifiable_cassette_does_not_land(tmp_path):
    """
    It stays in the clone, which is history. Guessing its window would write a
    measurement that nobody made, and a default reads exactly like one.
    """
    pins = Pins(model=MODEL, temperature=0.0)
    source = _legacy(
        tmp_path,
        rows=[("L1-LI-the-register-key", MODEL, [{"say": "never recorded"}]),
              ("L1-LI-the-register-key", MODEL, [])],
        cassettes=[(pins, "the system text", "the user text", "the reply",
                    "text")])
    tally = _run(source, tmp_path / "new.db")

    assert tally["migrated"] == 0
    assert tally["rows"] == 2
    assert _landed(tmp_path / "new.db") == []


def test_one_reply_under_two_system_texts_needs_a_second_reply(tmp_path):
    """
    The join is the intersection and not the union. A short reply is recorded
    under many system texts, so one reply rarely names one cassette. A
    session's replies all came from one system text, so two replies do.
    """
    pins = Pins(model=MODEL, temperature=0.0)
    cassettes = [(pins, "system one", "user one", "yes", "text"),
                 (pins, "system two", "user two", "yes", "text"),
                 (pins, "system one", "user three", "and here is why", "text")]
    source = _legacy(
        tmp_path,
        rows=[("L1-LI-the-register-key", MODEL, [{"say": "yes"}]),
              ("L1-LI-the-register-key", MODEL,
               [{"say": "yes"}, {"say": "and here is why"}])],
        cassettes=cassettes)
    tally = _run(source, tmp_path / "new.db")

    assert tally["migrated"] == 1, "the ambiguous row stays behind"
    assert tally["left: the replies name more than one cassette"] == 1
    assert _landed(tmp_path / "new.db")[0]["system_hash"] == system_hash(
        "system one")


def test_a_chains_rows_do_not_migrate(tmp_path):
    """
    A chain runs two sessions and its transcript holds only leg two's replies,
    so leg one's system text cannot be identified. Two rules were measured and
    both failed: leg one's brief as a prefix names only the system the tree
    composes today, and the recording order names the right cassette for 2781
    of 9184 chain rows (observed: frame 54's pass 3, 2026-09-21).
    """
    chain = sorted(migrate_register.chain_ids())[0]
    pins = Pins(model=MODEL, temperature=0.0)
    source = _legacy(
        tmp_path,
        rows=[(chain, MODEL, [{"say": "leg two spoke"}])],
        cassettes=[(pins, "leg two's system", "u", "leg two spoke", "text")])
    tally = _run(source, tmp_path / "new.db")

    assert tally["migrated"] == 0
    assert tally["left: a chain runs two sessions"] == 1


def test_a_chains_system_hash_joins_both_legs():
    """
    Both legs, joined by a blank line, the way `instructions_for` joins a
    chain's two briefs. Either leg can be why a chain stopped working, so
    either leg's text must be able to stale it. A hash over leg two alone
    would leave a rewritten leg one invisible.
    """
    result = fixtures.CaseResult(case_id="c", run=1, passed=True,
                                 systems=["leg one's system",
                                          "leg two's system"])
    assert result.system_text() == "leg one's system\n\nleg two's system"
    assert system_hash(result.system_text()) != system_hash("leg two's system")

    # The same join, in the one place the register already agreed on it.
    case = next(c for c in fixtures.load_case(
        paths.CASES / "l3_handoffs.yaml") if c.get("first"))
    legs = [case["first"], case["then"]]
    assert fixtures.instructions_for(case) == "\n\n".join(
        prompts.compose(leg["role"],
                        leg.get("prompt") or leg.get("verb") or leg.get("tick", ""))
        for leg in legs)


def test_the_migration_is_idempotent(tmp_path):
    """
    Run it twice and the target is the same register. The tool writes a new
    file and the caller swaps it in, so a second run after a failed swap must
    not double a row or refuse to start.
    """
    pins = Pins(model=MODEL, temperature=0.0)
    source = _legacy(
        tmp_path,
        rows=[("L1-LI-the-register-key", MODEL, [{"say": "the reply"}])],
        cassettes=[(pins, "the system text", "u", "the reply", "text")])
    target = tmp_path / "new.db"

    first = _run(source, target)
    once = _landed(target)
    second = _run(source, target)

    assert first["migrated"] == second["migrated"] == 1
    assert _landed(target) == once
    db = sqlite3.connect(str(target))
    assert db.execute("SELECT COUNT(*) FROM cassettes").fetchone()[0] == 1
    db.close()


def test_the_migration_refuses_a_source_that_has_moved(tmp_path):
    """
    The clone is the only copy of the pre-migration evidence. A source whose
    shape differs from the shape that was cloned is a source something has
    written to, and the whole point of the clone is that nothing did.
    """
    source = _legacy(tmp_path, rows=[], cassettes=[])
    src = migrate_register.open_source(source)
    with pytest.raises(SystemExit):
        migrate_register.check_source(src, runs=204058)
    src.close()


def test_the_migration_never_writes_to_its_source(tmp_path):
    """`mode=ro` and nothing else. SQLite refuses the write at the handle."""
    source = _legacy(tmp_path, rows=[], cassettes=[])
    src = migrate_register.open_source(source)
    with pytest.raises(sqlite3.OperationalError):
        src.execute("DELETE FROM case_runs")
    src.close()


def test_the_migration_refuses_a_target_that_already_holds_results(tmp_path):
    """
    The tool writes with `INSERT OR REPLACE`, which is what makes a second
    run over one target a no-op. It also meant a target named by mistake was
    written into rather than refused, and the register is 780 MB of evidence
    with no copy but the clone.
    """
    pins = Pins(model=MODEL, temperature=0.0)
    source = _legacy(
        tmp_path,
        rows=[("L1-LI-the-register-key", MODEL, [{"say": "the reply"}])],
        cassettes=[(pins, "the system text", "u", "the reply", "text")])
    target = tmp_path / "new.db"

    migrate_register.check_target(target)            # absent, so nothing to lose
    _run(source, target)
    with pytest.raises(SystemExit) as caught:
        migrate_register.check_target(target)
    assert "already holds 1 results" in str(caught.value)
    assert "--force" in str(caught.value), "the message names the way through"

    migrate_register.check_target(target, force=True)


# ---------------------------------------------------------------------------
# The other three writers, and the reader the cockpit shares
# ---------------------------------------------------------------------------


def test_a_session_that_never_built_a_prompt_says_unbuilt(tmp_path, monkeypatch):
    """
    Three values, and a reader can tell them apart. `''` means the row was
    written before the column existed. `unbuilt` means the session died
    before it had a prompt. A digest means a model was sent that text.

    Without the sentinel a crash writes `''`, and the register then calls it
    a legacy write-off, which is a row saying the wrong thing rather than
    nothing.
    """
    from rota.core import runner
    from rota.core.db import init_db
    from rota.core.scheduler import Wake
    from rota.llm.llm import ScriptedBackend

    assert system_hash(UNBUILT) == UNBUILT, "the sentinel is not digested"
    assert system_hash("") == ""
    assert system_hash("real text") not in (UNBUILT, "")

    def explode(*args, **kwargs):
        raise RuntimeError("the working set could not be pushed")

    monkeypatch.setattr(runner, "build_prompt", explode)
    conn = init_db(tmp_path / "w.db")
    out = runner.run_session(
        conn, Wake(role="liaison", kind="tick:converse", detail="converse"),
        backend=ScriptedBackend(["done"]),
        pins=Pins(model="scripted", temperature=0.0, num_ctx=4096))

    assert not out.committed, "the session failed, which is the point"
    assert out.system == UNBUILT
    assert system_hash(out.system) == UNBUILT


def test_the_profile_writer_stamps_the_whole_key(tmp_path, monkeypatch):
    """
    The fourth writer, and the last one with no test.

    `rota/cli.py` records a toolcheck as two rows, one per protocol, because
    the check sends one system text twice and the two replies fail in
    different ways. A native result must never answer for a text run, and
    only the `protocol` column can say so.
    """
    import argparse

    from rota import cli
    from rota.llm import profile as profile_mod, toolcheck

    class _Profile:
        name = "stub"
        default_model = "stub:1b"
        roles: dict = {}

        def backend(self):
            return None

        def pins_for(self, role):
            return Pins(model=self.default_model, temperature=0.0,
                        num_ctx=8192, think=True)

    monkeypatch.setattr(paths, "DEV_DB", tmp_path / "dev.db")
    monkeypatch.setattr(cli, "resolve", lambda name: tmp_path / "no-such-run.db")
    monkeypatch.setattr(profile_mod, "find", lambda name, root=None: _Profile())
    monkeypatch.setattr(toolcheck, "check", lambda backend, pins: toolcheck.Result(
        tool_line=True, native_call=True,
        tool_line_said="TOOL: ledger.log(...)", native_said=""))

    cli.cmd_profile(argparse.Namespace(action="toolcheck", target="stub",
                                       root=None, assignment=None))

    db = sqlite3.connect(str(tmp_path / "dev.db"))
    db.row_factory = sqlite3.Row
    rows = {r["protocol"]: dict(r) for r in db.execute(
        "SELECT * FROM case_runs ORDER BY seq")}
    db.close()

    assert set(rows) == {"text", "native"}, "one row per protocol"
    for row in rows.values():
        assert row["num_ctx"] == 8192
        assert row["temperature"] == 0.0
        assert row["extras"] == json.dumps({"think": True}, sort_keys=True)
        assert row["system_hash"] == system_hash(toolcheck.SYSTEM)


def _panel(monkeypatch):
    """The cockpit's L1 panel over the one case this file records."""
    from rota.cockpit import progress

    monkeypatch.setattr(progress, "_cases", lambda: [dict(CASE)])
    monkeypatch.setenv("ROTA_MODEL", MODEL)
    return progress.l1(paths.DEV_DB)


def test_the_cockpit_and_the_report_agree_on_a_green(register, monkeypatch):
    """
    Two instruments over one table gave two answers. The panel matched on
    `prompt_hash` alone and took the model from the first row it happened to
    read, so on the migrated register it said `llama3.1:8b` with 98 pass and
    19 fail while the report said 20 failing and 103 green under `qwen3:8b`
    (observed: frame 54's diff review, 2026-09-21). The panel is the one a
    person reads.
    """
    _record(register, Pins(model=MODEL, temperature=0.0))
    panel = _panel(monkeypatch)

    assert panel["model"] == MODEL, "the panel names the model the report does"
    assert panel["cases"][0]["state"] == "pass"
    assert _state() == "green"


def test_the_cockpit_and_the_report_agree_on_a_wrong_window(register,
                                                            monkeypatch):
    """
    The widened match, in the panel. A recording at another window is not
    evidence about this run, and the panel used to call it fresh because
    `prompt_hash` does not carry the window.
    """
    _record(register, Pins(model=MODEL, temperature=0.0, num_ctx=8192))
    panel = _panel(monkeypatch)

    assert panel["cases"][0]["state"] == "stale"
    assert _state() == "STALE"


def test_the_cockpit_tolerates_a_register_without_the_key(tmp_path):
    """
    The panel connects with a raw `sqlite3.connect` and so never migrates.
    A checkout can hold a register written before frame 54, and a reader that
    widens the match against it would raise rather than report.
    """
    path = tmp_path / "old.db"
    raw = sqlite3.connect(str(path))
    raw.executescript(OLD_SCHEMA)
    raw.commit()
    raw.close()

    conn = sqlite3.connect(str(path))
    assert not casestatus.carries_the_key(conn)
    case = dict(CASE)
    want = casestatus.wanted_pins(case, MODEL)
    assert casestatus.matching_runs(conn, case, want, keyed=False) == []
    with pytest.raises(sqlite3.OperationalError):
        casestatus.matching_runs(conn, case, want, keyed=True)
    conn.close()


# ---------------------------------------------------------------------------
# One composition of the system text (frame 63)
# ---------------------------------------------------------------------------


def test_one_function_builds_the_sandbox_a_prompt_advertises():
    """
    Four call sites reach a prompt's sandbox: `run_session`, `run_chain`
    through it, `system_text_for` and the cockpit's prompt preview. All four
    go through `runner.session_sandbox`.

    A second `sandbox.build` beside it is a second working set and therefore a
    second system text, which is the fault this frame removes. The preview
    held one, and its tool list differed from the runner's for 18 of 121 cases
    (observed: frame 63's design review, 2026-09-22).
    """
    import ast
    import pathlib

    from rota.cockpit import progress
    from rota.core import runner

    def builds_a_sandbox(node) -> bool:
        # The two spellings the tree uses: `sandbox_mod.build` in the runner,
        # and `build_sandbox` where the name is imported. `indexer.build` and
        # `lexicon_mod.build` are other functions with the same verb.
        func = node.func
        if isinstance(func, ast.Attribute):
            return (func.attr == "build"
                    and "sandbox" in getattr(func.value, "id", ""))
        return getattr(func, "id", "") == "build_sandbox"

    def builders(module) -> list[str]:
        tree = ast.parse(pathlib.Path(module.__file__).read_text(encoding="utf-8"))
        return [node.name for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
                and any(isinstance(call, ast.Call) and builds_a_sandbox(call)
                        for call in ast.walk(node))]

    assert builders(runner) == ["session_sandbox"]
    assert builders(progress) == [], "the preview composes through the runner"
    assert builders(fixtures) == [], "the testkit composes through the runner"


def test_the_preview_and_the_runner_advertise_one_working_set():
    """
    The cockpit's prompt preview is the text a person reads to answer "what is
    this session told", so a preview of another working set is worse than no
    preview. It passed no mode, no wake and no tool order, and its area rule
    named `survey` alone.

    The brief is held constant here, so the sandbox is the only variable.
    """
    from rota.cockpit import progress
    from rota.core.runner import compose_system

    cases = [c for c in progress._cases() if not c.get("first")]
    assert len(cases) > 100, "the panel reads every L1 case"

    # The flag changes the last paragraph of the system text, and the reader
    # takes it from the environment. Holding it False here compared one text
    # under the flag with one without it, and every case differed under
    # `ROTA_ONESHOT=1` (observed: frame 63's diff review, 2026-09-22).
    oneshot = bool(os.environ.get("ROTA_ONESHOT"))

    differ = []
    for case in cases:
        conn, _wake, sb = progress.preview_sandbox(case)
        try:
            preview = compose_system(case["role"], sb, oneshot=oneshot,
                                     instructions=fixtures.instructions_for(case))
        finally:
            conn.close()
        if preview != fixtures.system_text_for(case):
            differ.append(case["id"])
    assert not differ, f"the preview advertises another working set for {differ}"


def test_the_runner_and_the_reader_build_one_sandbox(tmp_path, monkeypatch):
    """
    Acceptance 1 names the runner's sandbox, and no other test holds one. The
    reader's is `system_text_for`'s and the preview's is the panel's, so both
    of those could agree with each other and disagree with the session.

    The sandbox is taken from `run_session`'s own path, by a scripted session
    that reaches the model with a word. The four cases are the shapes that
    reach the sandbox by another route: a declared `mode: readonly`, an
    onboarding tick that names an area, a mode whose `.tools` file declares an
    order, and a plain message wake.
    """
    from rota.core import runner
    from rota.llm.llm import ScriptedBackend

    seen: list[list[str]] = []
    real = runner.session_sandbox

    def remember(*args, **kw):
        sb = real(*args, **kw)
        seen.append(sb.signatures())
        return sb

    monkeypatch.setattr(runner, "session_sandbox", remember)
    by_id = {c["id"]: c for c in casestatus._cases()}

    for case_id in ("L1-TE-challenge-an-unusable-item",
                    "L1-VK-survey-an-area-for-what-it-does",
                    "L1-LI-plain-agreement-approves-every-line",
                    "L1-LI-a-reply-reaches-the-desk-that-asked"):
        case = by_id[case_id]
        seen.clear()
        fixtures.system_text_for(case)
        reader = seen[-1]

        seen.clear()
        fixtures.run_case(case, tmp_path / f"{case_id}.db",
                          ScriptedBackend(["done"]),
                          pins=Pins(model="scripted", temperature=0.0,
                                    num_ctx=4096))
        assert seen, f"{case_id} never reached the one setup"
        assert seen[0] == reader, f"{case_id}: the session and the reader differ"


def test_a_case_that_runs_in_a_worktree_still_previews(monkeypatch):
    """
    The preview makes no worktree, because an HTTP request must not shell out
    to git. So the push raises for a `repo:` case, and it raised for 10 of
    121. This frame's corrected wake took two of them from previewing to
    raising (observed: frame 63's pass 1, 2026-09-22).

    A panel that raises shows a person nothing at all. The system text needs
    no worktree, and it is the half that answers "what is this session told".
    """
    from rota.cockpit import progress

    # The run history is the rest of the endpoint, and it reads every row of
    # the register. This test is about the prompt.
    monkeypatch.setattr(progress, "_runs", lambda *a, **k: {})

    for case_id in ("L1-CR-challenge-a-claim",
                    "L1-AR-a-boundary-file-read-outside-in"):
        preview = progress.message_text(case_id)
        assert "  TOOL: " in preview["system"], f"{case_id} advertises its tools"
        assert "could not push the working set" in preview["push_error"]
        assert "worktree" in preview["push_error"], "and says why"
        assert preview["partial"] is True, "the size is a floor and says so"
        assert preview["push_error"] in preview["user"], \
            "the sentence reaches the panel a person reads"

    # And the other way, or the catch would hide a push that never ran.
    whole = progress.message_text("L1-LI-a-reply-reaches-the-desk-that-asked")
    assert whole["push_error"] == "", "a case with no worktree pushes"
    assert whole["partial"] is False, "and the size is the whole prompt"
    assert "could not push" not in whole["user"], "and the panel says nothing"


def test_a_tools_edit_makes_a_case_read_stale(register, monkeypatch):
    """
    The fault, in one test. A `.tools` file names the functions a mode
    narrows to, and those functions are the `TOOL:` lines of the system text.
    The cassette key covers that text, so an edit to the file moves the key
    and the suite can no longer replay the case.

    `prompt_hash` covers the composed brief and does not move, which is why
    the case read green through the whole of it.
    """
    from rota.roles import prompts as prompts_mod

    real = prompts_mod.mode_tools
    assert real("liaison", "converse"), "the mode narrows to a named list"

    _record(register, Pins(model=MODEL, temperature=0.0))
    assert _state() == "green"
    before = casestatus.wanted_pins(CASE, MODEL).prompt_hash

    # One function dropped, which is the commonest edit such a file takes.
    monkeypatch.setattr(prompts_mod, "mode_tools",
                        lambda role, mode: (real(role, mode) or [])[:-1])
    assert _state() == "STALE"
    assert casestatus.wanted_pins(CASE, MODEL).prompt_hash == before, \
        "the brief did not move, and that is the point"


def test_a_register_that_carries_no_system_hash_keeps_the_narrow_match(register):
    """
    `carries_the_key` is not the guard for the widened match, and using it
    would report every case stale.

    It asks whether the columns exist. `open_dev_db` adds them with
    `DEFAULT ''` and backfills nothing, and `tests/rota/cassettes.db` is
    gitignored and pulled from a published snapshot that carries no schema
    version. So this register is the one a fresh checkout reads.
    """
    _record(register, Pins(model=MODEL, temperature=0.0), system="")

    assert casestatus.carries_the_key(register), "the columns are there"
    assert not casestatus.holds_a_system_hash(register), "and no row carries one"
    assert _state() == "green"


def test_an_unbuilt_row_never_turns_the_widened_match_on(register):
    """
    A crashed session stamps `unbuilt`, which says the session died before it
    had a prompt. It is not a digest and it is not evidence, so a register
    holding nothing else stays on the narrow match.
    """
    _record(register, Pins(model=MODEL, temperature=0.0), system=UNBUILT)

    assert register.execute(
        "SELECT system_hash FROM case_runs").fetchone()["system_hash"] == UNBUILT
    assert not casestatus.holds_a_system_hash(register)
    assert _state() == "green"


def test_a_mixed_register_stales_the_cases_that_carry_only_legacy_rows(
        tmp_path, monkeypatch):
    """
    The guard is global, so one real hash anywhere turns the match on for
    every case. A case whose rows are all legacy then matches nothing and
    reads stale.

    That is the honest answer and it is emergent, which is why it is pinned
    here. A legacy row cannot say what text it measured, so it is not evidence
    about the text the tree composes now. Reading it as evidence is the fault
    this frame repairs, in a new place.
    """
    monkeypatch.delenv("ROTA_PROFILE", raising=False)
    monkeypatch.setattr(paths, "DEV_DB", tmp_path / "mixed.db")
    legacy = dict(CASE, id="L1-LI-a-row-from-before-the-column")
    current = dict(CASE, id="L1-LI-a-row-that-says-what-it-measured")
    monkeypatch.setattr(casestatus, "_cases", lambda: [legacy, current])

    db = open_dev_db(tmp_path / "mixed.db")
    stamp = Pins(model=MODEL, temperature=0.0).with_prompt(
        fixtures.instructions_for(CASE))
    record_case_run(db, legacy["id"], stamp, 1, True, [], [{"say": "ok"}],
                    system="")
    record_case_run(db, current["id"], stamp, 1, True, [], [{"say": "ok"}],
                    system=fixtures.system_text_for(current))

    assert casestatus.holds_a_system_hash(db), "one real hash turns it on"
    state = {r["id"]: r["state"] for r in casestatus.status(MODEL)}
    assert state[current["id"]] == "green"
    assert state[legacy["id"]] == "STALE", "unmeasured, and not bad"


def test_a_partly_migrated_case_reads_stale_and_never_fails(tmp_path,
                                                            monkeypatch):
    """
    A shrunk denominator is unmeasured, and never a failure.

    One case can hold both kinds of row. The widened match then keeps fewer
    rows than the threshold, and the count renders as a red: 3 legacy rows and
    2 current ones read FAIL on 2 of 2 against a threshold of 3 (observed:
    frame 63's diff review, 2026-09-22). That is the distinction frame 54
    exists for. Stale means nobody has looked since the text moved. Failing
    means somebody looked and the role got it wrong.
    """
    monkeypatch.delenv("ROTA_PROFILE", raising=False)
    monkeypatch.setattr(paths, "DEV_DB", tmp_path / "half.db")
    case = dict(CASE, runs=5, **{"pass": 3})
    monkeypatch.setattr(casestatus, "_cases", lambda: [case])

    db = open_dev_db(tmp_path / "half.db")
    stamp = Pins(model=MODEL, temperature=0.0).with_prompt(
        fixtures.instructions_for(case))
    text = fixtures.system_text_for(case)
    for run in (1, 2, 3):
        record_case_run(db, case["id"], stamp, run, True, [], [{"say": "ok"}],
                        system="")
    for run in (4, 5):
        record_case_run(db, case["id"], stamp, run, True, [], [{"say": "ok"}],
                        system=text)

    row = casestatus.status(MODEL)[0]
    assert row["state"] == "STALE", "two of five rows is not a measurement"
    assert row["passed"] is None, "and it carries no score to quote"


def test_a_chain_that_cannot_replay_reads_stale_and_says_why(tmp_path,
                                                             monkeypatch):
    """
    The first version fell back to the narrow match when the replay died, so a
    chain that nothing could replay read green and the gate's stale set stayed
    empty (observed: frame 63's diff review, 2026-09-22). The silence was the
    fault, and the fallback was what made it silent.
    """
    monkeypatch.delenv("ROTA_PROFILE", raising=False)
    monkeypatch.setattr(paths, "DEV_DB", tmp_path / "chain.db")
    # One row is the whole measurement here, so the threshold is one. The
    # chain's own threshold is five runs of a model this test never calls.
    chain = dict(next(c for c in casestatus._cases() if c.get("first")),
                 runs=1, **{"pass": 1})
    monkeypatch.setattr(casestatus, "_cases", lambda: [chain])
    recorded = "the text the run recorded"

    db = open_dev_db(tmp_path / "chain.db")
    record_case_run(db, chain["id"], casestatus.wanted_pins(chain, MODEL), 1,
                    True, [], [{"say": "ok"}], system=recorded)

    # The control first, or a stale reading below could come from the stub.
    monkeypatch.setattr(fixtures, "run_chain",
                        lambda *a, **k: fixtures.CaseResult(
                            case_id=chain["id"], run=1, passed=True,
                            systems=[recorded]))
    assert casestatus.status(MODEL)[0]["state"] == "green"

    def refuses(*args, **kwargs):
        raise RuntimeError("no cassette for the first leg")

    monkeypatch.setattr(fixtures, "run_chain", refuses)
    row = casestatus.status(MODEL)[0]
    assert row["state"] == "STALE", "a chain nothing can replay is unmeasured"
    assert "could not be replayed" in row["why"], "and the report says so"
    assert "no cassette for the first leg" in row["why"], "and names the reason"


# ---------------------------------------------------------------------------
# A look that measured nothing (frame 64)
# ---------------------------------------------------------------------------

#: A problem string as the runner writes one when the replay finds no
#: cassette. `check` writes its complaints first, so the marker is never in
#: `problems[0]`, and the reason must be the string that carries it.
MISS_PROBLEM = ('session did not commit: ["session failed: LLMUnavailable('
                "'no cassette for qwen3:8b key=a23c90151fcc… — record one "
                'with RecordingBackend\')"]')


def _a_real_miss(db, tmp_path, pins: Pins | None = None):
    """
    One replay against an empty cassettes table, recorded as the tier records
    it.

    The miss is driven and never typed: `ReplayOnlyBackend` raises, the runner
    catches it, and the writer sees the text a real run produces.
    """
    from rota.llm.cassettes import ReplayOnlyBackend

    pins = pins or Pins(model=MODEL, temperature=0.0)
    result = fixtures.run_case(dict(CASE), tmp_path / "miss.db",
                               ReplayOnlyBackend(db), pins=pins,
                               instructions=fixtures.instructions_for(CASE))
    record_case_run(db, CASE["id"],
                    pins.with_prompt(fixtures.instructions_for(CASE)), 1,
                    result.passed, result.problems, result.transcript(),
                    system=result.system_text())
    return result


def _miss(db, pins: Pins, **kw) -> None:
    """One look that measured nothing, through the writer the tier uses."""
    stamp = pins.with_prompt(fixtures.instructions_for(CASE))
    kw.setdefault("system", fixtures.system_text_for(CASE))
    record_case_run(db, CASE["id"], stamp, 1, False,
                    ["expected a call to ledger.log", MISS_PROBLEM],
                    [{"say": ""}], **kw)


def test_a_replay_that_misses_the_key_writes_a_look_and_no_run(register,
                                                                tmp_path):
    """
    The fault frame 64 repairs. A replay that found no cassette wrote nothing
    at all, so the report read the older rows at the same hashes and the case
    read green while the suite could not replay it.

    The miss is not a run. A `passed = 0` row would turn an unmeasured case
    into a hard red, and 15 of the 25 readers of `case_runs` would misread it
    (observed: frame 64's scope report, 2026-09-22).
    """
    result = _a_real_miss(register, tmp_path)

    assert not result.passed and any("no cassette for" in p
                                     for p in result.problems)
    assert register.execute(
        "SELECT COUNT(*) n FROM case_runs").fetchone()["n"] == 0, \
        "the run measured nothing and is not a result"

    rows = register.execute("SELECT * FROM key_misses").fetchall()
    assert len(rows) == 1, "one row per unmeasured run"
    assert rows[0]["kind"] == "no cassette", "a replay never reaches a server"
    assert "no cassette for" in rows[0]["reason"]
    assert rows[0]["reason"] != result.problems[0], \
        "the string that carries the marker, and not the first complaint"
    assert rows[0]["system_hash"] == system_hash(fixtures.system_text_for(CASE)), \
        "the miss carries the whole key the run tried"


def test_a_look_newer_than_the_evidence_stales_a_green(register, tmp_path):
    """
    The rule. Whatever state the rows reached, nobody has measured this case
    at the key the tree composes now.

    The two instruments contradicted each other before this: the gate's stale
    line read zero while its red count carried a case nobody had measured.
    """
    _record(register, Pins(model=MODEL, temperature=0.0))
    assert _state() == "green", "the control, before anybody looks again"

    _a_real_miss(register, tmp_path)
    row = _row()
    assert row["state"] == "STALE"
    assert row["passed"] is None, "a stale line carries no score to quote"

    miss = register.execute("SELECT * FROM key_misses").fetchone()
    assert row["why"].startswith(f"looked {miss['at']}, no cassette: "), \
        "the time and the kind lead, because render cuts the line at 96"
    assert "no cassette for" in row["why"], "and the reason follows"


def test_a_look_older_than_the_evidence_is_history(register, tmp_path):
    """Somebody looked, missed, and then re-recorded. The green is the newer
    fact and the miss says nothing about it."""
    _a_real_miss(register, tmp_path)
    _record(register, Pins(model=MODEL, temperature=0.0))

    row = _row()
    assert row["state"] == "green"
    assert row["why"] == "", "an old miss is not a reason"


def test_a_case_with_only_a_look_stays_never_measured(register, tmp_path):
    """
    `NEW` keeps its meaning: nobody has measured this case. `ever` counts
    `case_runs` only, so the gate's set does not move for such a case, and it
    already holds `NEW`.
    """
    _a_real_miss(register, tmp_path)

    row = _row()
    assert row["state"] == "NEW" and row["ever"] == 0
    assert "no cassette" in row["why"], "and the report says who looked"


def test_a_look_under_another_key_stales_nothing(register):
    """
    A miss must match the key the runs match.

    A narrower filter reads a false `STALE` twice. After a person reverts a
    system-half edit the old runs match again while a miss at the other
    `system_hash` is newer. And a local run under another window writes misses
    that would stale the suite's own read.
    """
    _record(register, Pins(model=MODEL, temperature=0.0))

    _miss(register, Pins(model=MODEL, temperature=0.0, num_ctx=8192))
    assert _state() == "green", "another window is another key"

    _miss(register, Pins(model=MODEL, temperature=0.0), system="another text")
    assert _state() == "green", "and another system text is another key"

    assert register.execute(
        "SELECT COUNT(*) n FROM key_misses").fetchone()["n"] == 2, \
        "both looks are recorded, and neither one answers for this key"


def test_a_register_from_before_the_miss_table_reads_as_today(tmp_path,
                                                               monkeypatch):
    """
    The panel connects raw and never migrates, and its `except sqlite3.Error`
    would turn a missing table into `never run` for every case, in silence.
    So the table is asked for by name.
    """
    monkeypatch.delenv("ROTA_PROFILE", raising=False)
    path = tmp_path / "old.db"
    monkeypatch.setattr(paths, "DEV_DB", path)
    monkeypatch.setattr(casestatus, "_cases", lambda: [dict(CASE)])

    raw = sqlite3.connect(str(path))
    raw.executescript(OLD_SCHEMA)
    raw.execute("INSERT INTO case_runs (case_id, model, prompt_hash, run_no, "
                "passed, seq) VALUES (?,?,?,1,1,1)",
                (CASE["id"], MODEL, casestatus.wanted_pins(
                    CASE, MODEL).prompt_hash))
    raw.commit()
    raw.close()

    conn = sqlite3.connect(str(path))
    assert not casestatus.records_misses(conn), "the table arrives with frame 64"
    assert casestatus.latest_miss is not None, "and the reader is guarded by it"
    conn.close()

    assert [c["state"] for c in _panel(monkeypatch)["cases"]] == ["pass"], \
        "the missing table silences no case"
    # The report opens through `open_dev_db`, which is the table's only
    # creator, so it reads its own register and raises nothing.
    assert _state() == "green"
    conn = sqlite3.connect(str(path))
    assert casestatus.records_misses(conn), "and the opener created the table"
    conn.close()


def test_the_gates_stale_set_holds_a_case_whose_last_look_missed(register,
                                                                  tmp_path):
    """
    The acceptance line "zero stale" held while a case was unmeasured, and the
    red count carried that same case. The stale set is where such a case
    belongs.
    """
    from rota.tools import gate

    _record(register, Pins(model=MODEL, temperature=0.0))
    assert gate._stale(MODEL) == set(), "the control"

    _a_real_miss(register, tmp_path)
    assert gate._stale(MODEL) == {CASE["id"]}


#: The child of the race test. One register, four processes, and the writer
#: the tier uses. Half the runs measure nothing, so both tables are written.
_RACE_CHILD = """
import sys

from rota.llm.cassettes import open_dev_db, record_case_run
from rota.llm.llm import Pins

path, worker, rounds = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
conn = open_dev_db(path)
# The tier runs under `-n auto`, so a writer waits for the write lock rather
# than raising. The default timeout is 5 seconds and four writers share one
# file here.
conn.execute("PRAGMA busy_timeout = 30000")
pins = Pins(model="m", temperature=0.0).with_prompt("p")
for run in range(1, rounds + 1):
    ok = run % 2 == 0
    record_case_run(conn, "case-%d" % worker, pins, run, ok,
                    [] if ok else ["no cassette for m key=abc"])
conn.close()
"""


@pytest.mark.timeout(120)
def test_four_writers_never_allocate_one_sequence_twice(tmp_path):
    """
    `seq` is one counter across two tables, and it is read inside the insert
    that uses it.

    Two statements race: four processes and 400 inserts each gave 2 duplicate
    `seq` values (observed: frame 64's design review, 2026-09-22). A duplicate
    would make a miss and a run tie, and the rule above compares them.

    The size below has teeth. The same four processes over the two-statement
    allocation gave 1 to 2 duplicates in each of three runs, and the one
    statement gave none in three (observed: this machine, 2026-09-22). One run
    costs 0.2 seconds. The timeout marker is here so a flaky run fails
    visibly rather than hangs.
    """
    path = tmp_path / "race.db"
    open_dev_db(path).close()             # the parent creates it, once

    started = time.perf_counter()
    children = [subprocess.Popen(
        [sys.executable, "-c", _RACE_CHILD, str(path), str(worker), "25"],
        cwd=str(paths.REPO)) for worker in range(4)]
    for child in children:
        assert child.wait(timeout=90) == 0, "a writer died"
    elapsed = time.perf_counter() - started

    conn = open_dev_db(path)
    seqs = [r["seq"] for r in conn.execute(
        "SELECT seq FROM case_runs UNION ALL SELECT seq FROM key_misses")]
    conn.close()
    assert len(seqs) == 100, f"every write landed, in {elapsed:.1f}s"
    assert len(set(seqs)) == 100, "two writers took one number"


def test_the_guard_reads_one_constant_for_both_markers(register):
    """
    The rule had a second copy: the writer matched both markers and the
    report's exclusion clause named one of them by hand. A run that could not
    reach the model then entered the report's window and read as a red.

    The rows below are written raw on purpose. No writer can make one now, and
    the register holds thousands from before the guard existed.
    """
    from rota.llm.cassettes import _is_unmeasured

    assert set(MISS_MARKERS) == {"no cassette", "unreachable"}
    for marker in MISS_MARKERS.values():
        assert _is_unmeasured([f"session did not commit: [{marker} x]"], [])
        assert _is_unmeasured([], [{"errors": [f"{marker} x"]}]), "or in the text"
    assert not _is_unmeasured(["expected a call to ledger.log"], [{"say": "ok"}])

    want = casestatus.wanted_pins(CASE, MODEL)
    for seq, marker in enumerate(MISS_MARKERS.values(), 1):
        register.execute(
            "INSERT INTO case_runs (case_id, model, prompt_hash, run_no, "
            "passed, problems, transcript, seq) VALUES (?,?,?,?,0,?,'[]',?)",
            (CASE["id"], MODEL, want.prompt_hash, seq,
             json.dumps([f"session did not commit: [{marker} x]"]), seq))
    assert casestatus.matching_runs(register, CASE, want, limit=9) == [], \
        "neither marker enters the window"


def test_the_cockpit_shows_the_look_that_measured_nothing(register, tmp_path,
                                                           monkeypatch):
    """
    The panel never calls `status`, so the rule is applied here as well. Two
    instruments over one table that disagree about one case is the fault frame
    54 repaired, and the panel is the one a person reads.
    """
    _record(register, Pins(model=MODEL, temperature=0.0))
    assert _panel(monkeypatch)["cases"][0]["state"] == "pass", "the control"

    _a_real_miss(register, tmp_path)
    entry = _panel(monkeypatch)["cases"][0]
    assert entry["state"] == "stale" and entry["passed"] is None
    assert entry["problems"], "the panel shows the miss"
    assert entry["problems"][0].startswith("looked ")
    assert "no cassette" in entry["problems"][0]
    assert _state() == "STALE", "and the report reads the case the same way"


def _cases_with_a_row() -> list[dict]:
    """
    Every single-session case the register holds evidence about, under the
    model the report reads.

    Collected at import, because the parameter list is the acceptance. The
    design review sent this line back once for passing on one easy case. A
    machine with no register collects nothing, and the tests below skip.
    """
    if not paths.DEV_DB.exists():
        return []
    conn = open_dev_db(paths.DEV_DB)
    model = casestatus.model_for()
    out = [case for case in casestatus._cases()
           if not case.get("first")
           and casestatus.matching_runs(
               conn, case, casestatus.wanted_pins(case, model), limit=1)]
    conn.close()
    return out


WITH_A_ROW = _cases_with_a_row()
NO_REGISTER = "the register is not on this machine"


@pytest.fixture(scope="module")
def registered():
    """The real register, opened the way the report opens it."""
    conn = open_dev_db(paths.DEV_DB)
    yield conn
    conn.close()


@pytest.mark.skipif(not WITH_A_ROW, reason=NO_REGISTER)
@pytest.mark.parametrize("case", WITH_A_ROW or [{}],
                         ids=[c["id"] for c in WITH_A_ROW] or ["none"])
def test_the_composed_system_text_is_the_one_the_run_recorded(case, registered):
    """
    The widened match drops no row it should keep, case by case.

    The composition is a second definition of something the runner already
    builds, and a second definition that agrees on the easy cases is the
    danger. A hand-rolled composition that skipped the fixture agreed on 102
    of 121 cases: 13 raised on a foreign key and 6 gave a different hash
    (observed: frame 63's first read, 2026-09-22).
    """
    want = casestatus.wanted_pins(case, casestatus.model_for())
    text = fixtures.system_text_for(case)
    narrow = casestatus.matching_runs(registered, case, want, limit=99)
    wide = casestatus.matching_runs(registered, case, want, limit=99,
                                    system=text)

    assert narrow, "the parameter set holds only cases that have a row"
    assert len(wide) == len(narrow), (
        f"the tree composes {system_hash(text)}, and "
        f"{len(narrow) - len(wide)} of {len(narrow)} rows carry another hash")


@pytest.mark.skipif(not WITH_A_ROW, reason=NO_REGISTER)
def test_the_parameter_set_holds_the_shapes_that_would_break_it():
    """
    Four shapes reach the composition by a different route, and a set without
    them would pass while the report was wrong about the hard cases.

    `mode: readonly` builds no write functions at all. A `repo:` case runs in
    a worktree the reader never makes. An area case names its subject in the
    sandbox. A mode with a `.tools` order lists its functions in the order of
    the job rather than alphabetically.
    """
    assert len(WITH_A_ROW) > 100, "the register holds the whole tier"
    ids = {c["id"] for c in WITH_A_ROW}

    assert "L1-TE-challenge-an-unusable-item" in ids, "the readonly case"
    assert any(c.get("mode") == "readonly" for c in WITH_A_ROW)
    assert any(c.get("repo") for c in WITH_A_ROW), "a case with a worktree"
    assert any(c.get("tick") in ("survey", "orient", "define")
               for c in WITH_A_ROW), "an area case"
    assert any(prompts.mode_order(c["role"], fixtures.mode_of(c))
               for c in WITH_A_ROW), "a mode that declares a tool order"
