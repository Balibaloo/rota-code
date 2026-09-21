"""
The register's key: what a result was earned under, and what the report
matches on.

Frame 54 (2026-09-21). A recording is identified by seven things and a result
was identified by three, so `casestatus` could not match what the cassette key
covers. One narrow key gave two opposite symptoms: a green case read stale,
and a case the suite could not replay read green.

These pin the five columns, the writer that stamps them, the match that reads
them, and the model the report reads under. Every test builds its own small
register in `tmp_path`: the real one is 780 MB of evidence and no test writes
to it.
"""
from __future__ import annotations

import json
import sqlite3

import pytest

from rota import paths
from rota.llm.cassettes import KEY_COLUMNS, open_dev_db, record_case_run
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
