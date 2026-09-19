"""
The spill monitor: what the card holds, and what it pushed into RAM.

A window rise is free until it is not. Ollama loads what it can into VRAM
and puts the rest in RAM, and the run keeps working -- every turn commits,
each one just takes eight times as long. Measured on the 3080: qwen3:8b
runs a turn in 12.5 s when it fits, over 100 s at a 27 per cent spill, and
153 s with three quarters of the model on the GPU.

`/api/ps` already reports `size` and `size_vram` per loaded model, so the
difference is the spill and nothing in the model path needs instrumenting.
The rules this file pins:

- `{}` and `None` are different answers. A server that did not answer must
  not read as a card with nothing loaded, because silence reads as good
  news and the monitor exists to break silence.
- The endpoint comes from the run. The recorder runs on 11435 and both
  servers answer on this box, so a fixed host measures the wrong card.
- The reading happens once per session, in the loop. `refresh_pulse` runs
  from five places on the render path and must make no HTTP call.
- The dismissal is per model and per spill size (ruled 2026-09-19), so an
  old dismissal can never hide a spill that grew.
"""
from __future__ import annotations

import json

import pytest

from rota.core import config
from rota.core import loop
from rota.core.db import init_db
from rota.llm import discover as D
from rota.llm.llm import Pins, ScriptedBackend


# ---------------------------------------------------------------------------
# Reading the card
# ---------------------------------------------------------------------------

def test_an_unreachable_server_and_an_empty_card_are_different_answers(monkeypatch):
    """
    Both used to be `{}`. The monitor then stayed silent when it could not
    see the card, which is the one failure that looks like success.
    """
    monkeypatch.setattr(D, "_get", lambda *a, **k: (_ for _ in ()).throw(OSError("refused")))
    assert D.loaded("http://localhost:1") is None

    monkeypatch.setattr(D, "_get", lambda *a, **k: {"models": []})
    assert D.loaded("http://localhost:1") == {}

    monkeypatch.setattr(D, "_get", lambda *a, **k: {
        "models": [{"name": "qwen3:8b", "size": 7947, "size_vram": 7947}]})
    assert D.loaded("http://localhost:1") == {"qwen3:8b": (7947, 7947)}


def test_loaded_reads_the_endpoint_it_is_given(monkeypatch):
    """The recorder runs on 11435. A bare literal measured the other card
    and the answer looked plausible rather than failing."""
    asked: list[str] = []

    def fake(url, *a, **k):
        asked.append(url)
        return {"models": []}

    monkeypatch.setattr(D, "_get", fake)
    D.loaded("http://localhost:11435")
    D.loaded()
    assert asked == ["http://localhost:11435/api/ps", f"{D.OLLAMA}/api/ps"]
    # The default is the environment's, like `rota/llm/llm.py:44`, and no
    # longer a literal.
    from rota.llm.llm import OLLAMA_HOST
    assert D.OLLAMA == OLLAMA_HOST


def test_the_spill_of_one_model_is_pure_arithmetic():
    gb = 1 << 30
    held = {"gemma3:12b": (11 * gb, 8 * gb), "qwen3:8b": (7 * gb, 7 * gb)}
    assert D.spill_of(held, "gemma3:12b") == {
        "model": "gemma3:12b", "size": 11 * gb, "size_vram": 8 * gb, "spill": 3 * gb}
    assert D.spill_of(held, "qwen3:8b")["spill"] == 0
    # A name the card does not hold falls back to the worst spill, so the
    # row never reports the wrong load as healthy.
    assert D.spill_of(held, "nothing:here")["model"] == "gemma3:12b"
    assert D.spill_of({}) == {"model": "", "size": 0, "size_vram": 0, "spill": 0}
    assert D.spill_of(None) is None


def test_fit_tells_one_window_from_another_without_the_kv_metadata():
    """
    qwen3.5:9b reports no `head_count_kv`, so `kv_cache_bytes` says None and
    the need was the weights alone -- every window passed by construction
    (observed: rota/llm/discover.py:132-144). The measurement fills the gap:
    what the server loaded above the weights is the cache at the window it
    loaded at, and the cache is linear in the window.
    """
    gb = 1 << 30
    m = D.Model("ollama", "qwen3.5:9b", size_bytes=5 * gb, meta={"block_count": 36})
    assert D.kv_cache_bytes(m.meta, 12288) is None

    machine = D.System("windows", ram_bytes=32 * gb, vram_total_bytes=6 * gb,
                       vram_free_bytes=1 * gb)
    # Measured: 5.77 GB resident at 12288, so the cache is 0.77 GB there.
    small = D.fit_of(m, machine, 12288, loaded_bytes=int(5.77 * gb), loaded_ctx=12288)
    big = D.fit_of(m, machine, 24576, loaded_bytes=int(5.77 * gb), loaded_ctx=12288)
    assert small.need_bytes < big.need_bytes, "the guard cannot tell the windows apart"
    assert small.fit == "in_vram" and big.fit == "spills"

    # Without the window of the measurement the old answer stands: the
    # number measured, and no claim about any other window.
    flat = D.fit_of(m, machine, 24576, loaded_bytes=int(5.77 * gb))
    assert flat.need_bytes == int(5.77 * gb)


# ---------------------------------------------------------------------------
# The loop writes the row
# ---------------------------------------------------------------------------

@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('i1','ship it','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i1','do it')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) "
                 "VALUES ('c1','t1','it does the thing')")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','pending')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','t1')")
    conn.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
                 "VALUES ('b1','src/thing.py','path')")
    # Parameterised: SQLite does not interpret `\n` in a string literal.
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES ('tst1','b1','c1',?,?)",
                 ("tests/test_it.py", "def test_it():\n    assert True\n"))
    return conn


def _backend(replies):
    """A scripted backend that names an Ollama host, like a real run's."""
    b = ScriptedBackend(replies)
    b.host = "http://localhost:11435"
    return b


def test_the_loop_reads_the_card_once_per_session(db):
    """One reading per session, taken after the session ends and while the
    model is still resident. No HTTP: the reader is passed in."""
    gb = 1 << 30
    calls: list[str] = []

    def reader(endpoint):
        calls.append(endpoint)
        return {"qwen3:8b": (8 * gb, 6 * gb)}

    s = loop.step(db, backend=_backend(["TOOL: msg.present_principal(refs=[])", "done"]),
                  pins=Pins(model="qwen3:8b", num_ctx=16384), spill_reader=reader)
    assert s.outcome is not None, f"no session ran: {s}"
    assert calls == ["http://localhost:11435"], "the run's own endpoint, once"

    row = config.get(db, "spill_seen")
    assert row["seen"] is True and row["model"] == "qwen3:8b"
    assert row["spill"] == 2 * gb and row["size"] == 8 * gb
    assert row["endpoint"] == "http://localhost:11435" and row["num_ctx"] == 16384
    assert row["at"]

    # The same reading twice writes no second history entry: the history
    # grows when the spill moves, not once a session.
    loop.step(db, backend=_backend(["done", "done"]),
              pins=Pins(model="qwen3:8b", num_ctx=16384), spill_reader=reader)
    assert len(calls) == 2
    assert len(config.history(db, "spill_seen")) == 1


def test_a_server_that_does_not_answer_writes_that_it_was_not_seen(db):
    s = loop.step(db, backend=_backend(["TOOL: msg.present_principal(refs=[])", "done"]),
                  pins=Pins(model="qwen3:8b", num_ctx=16384),
                  spill_reader=lambda endpoint: None)
    assert s.outcome is not None
    row = config.get(db, "spill_seen")
    assert row["seen"] is False and row["spill"] == 0, \
        "an unseen server is not the same as no spill"


def test_a_run_with_no_ollama_reads_nothing(db):
    """A replayed suite runs behind a cassette backend, holds no model, and
    must make no call. The endpoint comes from the backend, so there is
    nothing to read and nothing to say."""
    def explode(endpoint):
        raise AssertionError("the monitor called out on a run with no ollama")

    loop.step(db, backend=ScriptedBackend(["TOOL: msg.present_principal(refs=[])", "done"]),
              pins=Pins(model="scripted"), spill_reader=explode)
    assert config.get(db, "spill_seen") == {}
    assert loop._spill_endpoint(ScriptedBackend([])) is None
    assert loop._spill_endpoint(_backend([])) == "http://localhost:11435"


# ---------------------------------------------------------------------------
# What the pulse says, and when it stops saying it
# ---------------------------------------------------------------------------

def test_the_warning_stands_until_it_is_dismissed_and_returns_when_it_grows():
    """
    Per model and per spill size (ruled 2026-09-19). gemma3:12b spills at
    12288 today for reasons no window rise caused, so that desk is warned
    once. A single flag would let that dismissal hide the next rise, which
    is the one thing this monitor exists to catch.
    """
    from rota.cockpit.tui import spill_bit

    gb = 1 << 30
    seen = {"seen": True, "model": "gemma3:12b", "endpoint": "e", "num_ctx": 12288,
            "size": 11 * gb, "size_vram": 8 * gb, "spill": 3 * gb, "at": "now"}
    bit = spill_bit(seen, {})
    assert "gemma3:12b" in bit and "3.0 GB" in bit and "alt+s" in bit
    assert "100 s" in bit and "12.5 s" in bit, "the cost is the point of the bit"

    hushed = {"model": "gemma3:12b", "spill": 3 * gb}
    assert spill_bit(seen, hushed) == ""
    grown = dict(seen, spill=4 * gb, size_vram=7 * gb)
    assert spill_bit(grown, hushed), "a spill that grew must warn again"
    other = dict(seen, model="qwen3:8b")
    assert spill_bit(other, hushed), "a dismissal covers one model"

    # No spill, no bit. And no reading at all is not a claim either way.
    assert spill_bit(dict(seen, spill=0), {}) == ""
    assert spill_bit({}, {}) == ""
    assert spill_bit(None, None) == ""


def test_a_blind_monitor_says_so():
    from rota.cockpit.tui import spill_bit

    unseen = {"seen": False, "model": "qwen3:8b", "endpoint": "http://localhost:11435",
              "num_ctx": 16384, "size": 0, "size_vram": 0, "spill": 0, "at": "now"}
    bit = spill_bit(unseen, {})
    assert "11435" in bit and "blind" in bit
    assert spill_bit(unseen, {"model": "qwen3:8b", "spill": 0}) == ""


def test_the_settings_are_declared_and_the_row_is_json():
    """A machine-written setting, like the profile snapshot at
    rota/llm/profile.py:269. Declared, so nobody reads a default forever."""
    assert "spill_seen" in config.SETTINGS and "spill_dismissed" in config.SETTINGS
    for key in ("spill_seen", "spill_dismissed"):
        assert config.SETTINGS[key].default == {}
        assert json.dumps(config.SETTINGS[key].default) == "{}"
