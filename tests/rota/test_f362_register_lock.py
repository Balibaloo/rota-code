"""
A writer of the register waits for the write lock, and `seq` is cheap to
allocate (frame 362 residue, 2026-11-06).

Under `pytest -n auto` the gate's workers write one register. The first
insert of a gate read the whole key index for `MAX(seq)` with the write lock
held, 81 to 195 s on a cold cache. Every other writer raised `database is
locked` after the default 5 s, and the gate showed new reds that passed on
the rerun (observed: `plans/l3r-load-reds-read-2026-11-06.md`).
"""
from __future__ import annotations

import sqlite3
import threading
import time

import pytest

from rota.core import config
from rota.llm import cassettes
from rota.llm.cassettes import _NEXT_SEQ, open_dev_db, record_case_run
from rota.llm.llm import Pins

PINS = Pins(model="m", temperature=0.0).with_prompt("p")

#: Longer than the 5 s default timeout, short enough for a unit test.
HOLD_S = 7.0


def _hold_the_write_lock(path, held: threading.Event, seconds: float) -> None:
    conn = sqlite3.connect(str(path), isolation_level=None)
    conn.execute("BEGIN IMMEDIATE")
    held.set()
    time.sleep(seconds)
    conn.execute("COMMIT")
    conn.close()


@pytest.mark.timeout(60)
def test_a_writer_waits_for_a_long_hold_and_its_row_lands(tmp_path):
    """
    One connection holds the write lock for longer than 5 s. Before the fix,
    `record_case_run` raised `sqlite3.OperationalError: database is locked`
    at its `case_runs` insert.
    """
    path = tmp_path / "register.db"
    conn = open_dev_db(path)
    held = threading.Event()
    holder = threading.Thread(target=_hold_the_write_lock,
                              args=(path, held, HOLD_S))
    holder.start()
    assert held.wait(10), "the holder never took the lock"
    started = time.perf_counter()
    try:
        record_case_run(conn, "case-1", PINS, 1, True, [], live=True)
    finally:
        holder.join()
    waited = time.perf_counter() - started
    rows = conn.execute("SELECT case_id, seq FROM case_runs").fetchall()
    conn.close()
    assert [tuple(r) for r in rows] == [("case-1", 1)]
    assert waited > 5.0, f"the insert waited {waited:.1f}s for the holder"


def test_the_wait_is_declared_with_its_reason_and_outlasts_the_hold():
    """The wait is a cap, so `rota/core/config.py` declares it (law 7). The
    read measured holds up to 195 s, and the wait must outlast them."""
    wait = config.REGISTER_WAIT
    assert wait.key == "register_wait_s"
    assert wait.default > 195
    assert "195" in wait.why


def _plans(conn: sqlite3.Connection) -> list[str]:
    inner = _NEXT_SEQ[1:-1]                     # the bare SELECT
    return [r[3] for r in conn.execute(f"EXPLAIN QUERY PLAN {inner}")]


def _reads_each_seq_index(plans: list[str]) -> None:
    """The old plan reads `SEARCH case_runs USING COVERING INDEX
    sqlite_autoindex_case_runs_1`, the whole key index (observed: the copy of
    the register, 2026-11-06). So the check names the index, not the verb."""
    for name, table in cassettes.SEQ_INDEXES.items():
        want = f"{table} USING COVERING INDEX {name}"
        assert any(line.endswith(want) for line in plans), plans
    assert not any("sqlite_autoindex" in line for line in plans), plans


def test_a_new_register_answers_each_max_seq_from_its_own_index(tmp_path):
    conn = open_dev_db(tmp_path / "new.db")
    plans = _plans(conn)
    conn.close()
    _reads_each_seq_index(plans)


def _an_old_register(path, rows: int = 50) -> None:
    """A register with rows in both tables and no `seq` index, as every
    register made before frame 362 is."""
    conn = open_dev_db(path)
    for name in cassettes.SEQ_INDEXES:
        conn.execute(f"DROP INDEX {name}")
    for run in range(1, rows + 1):
        record_case_run(conn, f"case-{run % 7}", PINS, run, run % 3 != 0,
                        [] if run % 3 else ["no cassette for m key=abc"],
                        live=True)
    conn.close()


def _indexes(path) -> set[str]:
    conn = sqlite3.connect(str(path))
    names = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'index' "
        "AND sql IS NOT NULL")}
    conn.close()
    return names


def _rows(path) -> tuple[list, list]:
    conn = sqlite3.connect(str(path))
    runs = conn.execute("SELECT * FROM case_runs ORDER BY seq").fetchall()
    misses = conn.execute("SELECT * FROM key_misses ORDER BY seq").fetchall()
    conn.close()
    return runs, misses


def test_open_dev_db_builds_no_index_on_a_register_that_holds_rows(tmp_path):
    """A build on 2.1 GB holds the write lock for every worker, so the opener
    never builds on a table that holds rows."""
    path = tmp_path / "old.db"
    _an_old_register(path)
    assert _indexes(path) == set(), "the control"
    conn = open_dev_db(path)
    plans = _plans(conn)
    conn.close()
    assert _indexes(path) == set()
    with pytest.raises(AssertionError):
        _reads_each_seq_index(plans)


def test_the_tool_adds_the_indexes_keeps_every_row_and_runs_once(
        tmp_path, capsys):
    from rota.tools import index_register

    path = tmp_path / "old.db"
    _an_old_register(path)
    before = _rows(path)
    assert before[0] and before[1], "the control: both tables hold rows"

    built = index_register.build(path)
    assert [name for name, _ in built] == list(cassettes.SEQ_INDEXES)
    assert _indexes(path) == set(cassettes.SEQ_INDEXES)
    assert _rows(path) == before
    out = capsys.readouterr().out
    for name in cassettes.SEQ_INDEXES:
        assert f"built {name}" in out
    assert "total" in out

    assert index_register.build(path) == []
    assert _indexes(path) == set(cassettes.SEQ_INDEXES)
    assert _rows(path) == before
    again = capsys.readouterr().out.splitlines()
    assert not [line for line in again if line.startswith("built ")], again
    assert again[-1].endswith("0 of 2 indexes built"), again

    conn = open_dev_db(path)
    plans = _plans(conn)
    conn.close()
    _reads_each_seq_index(plans)


# --- Pass 2: the journal mode switch, and the indexes after a pull ---------

#: One opener of the register, started at one moment by several processes.
_OPEN_CHILD = """
import sys, time

from rota.llm.cassettes import open_dev_db, record_case_run
from rota.llm.llm import Pins

path, worker, go = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
pins = Pins(model="m", temperature=0.0).with_prompt("p")
while time.time() < go:
    time.sleep(0.005)
try:
    conn = open_dev_db(path)
    record_case_run(conn, "case-%d" % worker, pins, 1, True, [], live=True)
    conn.close()
except Exception as e:
    import traceback
    frame = traceback.extract_tb(e.__traceback__)[-1]
    print("ERR %s at %s:%s %s" % (e, frame.filename, frame.lineno, frame.line))
    sys.exit(1)
"""


def _a_delete_mode_register(path) -> None:
    """A register in delete mode, as a pulled snapshot and a new file are."""
    open_dev_db(path).close()
    conn = sqlite3.connect(str(path), isolation_level=None)
    conn.execute("PRAGMA journal_mode = DELETE")
    conn.close()


@pytest.mark.timeout(60)
def test_processes_that_open_a_delete_mode_register_at_once_all_land(
        tmp_path):
    """
    `PRAGMA journal_mode = WAL` needs the exclusive lock, and it raises at
    once when another connection holds a lock. It does not wait for the busy
    handler (observed: the review of 4aceb1ea, probe `swarm.py`).

    The holder makes the race certain. It holds the reserved lock while six
    processes open the register at one moment, so each switch meets a lock.
    On the parent 4aceb1ea every process raised at the switch.
    """
    import subprocess
    import sys

    from rota import paths

    path = tmp_path / "pulled.db"
    _a_delete_mode_register(path)
    go = time.time() + 3.0
    held = threading.Event()
    holder = threading.Thread(target=_hold_the_write_lock,
                              args=(path, held, 4.5))
    holder.start()
    assert held.wait(10), "the holder never took the lock"
    children = [subprocess.Popen(
        [sys.executable, "-c", _OPEN_CHILD, str(path), str(worker), str(go)],
        cwd=str(paths.REPO), stdout=subprocess.PIPE, text=True)
        for worker in range(6)]
    outs = [child.communicate(timeout=45)[0].strip() for child in children]
    holder.join()
    assert [o for o in outs if o] == [], outs
    conn = sqlite3.connect(str(path))
    seqs = sorted(r[0] for r in conn.execute("SELECT seq FROM case_runs"))
    mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    conn.close()
    assert seqs == [1, 2, 3, 4, 5, 6]
    assert mode == "wal"


def _mode(path) -> str:
    conn = sqlite3.connect(str(path))
    mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    conn.close()
    return mode


def _a_pulled_register(path) -> None:
    """Rows in both tables, no `seq` index and delete mode: the shape of the
    published snapshot (`cassette_store.pack` sets delete mode)."""
    _an_old_register(path)
    conn = sqlite3.connect(str(path), isolation_level=None)
    conn.execute("PRAGMA journal_mode = DELETE")
    conn.close()


def test_the_gate_prepares_the_register_before_its_workers(
        tmp_path, monkeypatch, capsys):
    from rota import paths
    from rota.tools import gate

    path = tmp_path / "cassettes.db"
    _a_pulled_register(path)
    before = _rows(path)
    monkeypatch.setattr(paths, "DEV_DB", path)

    built = gate.prepare_register()
    assert [name for name, _ in built] == list(cassettes.SEQ_INDEXES)
    out = capsys.readouterr().out.splitlines()
    assert len(out) == 1 and out[0].startswith("register: built "), out
    for name in cassettes.SEQ_INDEXES:
        assert name in out[0]
    assert _indexes(path) == set(cassettes.SEQ_INDEXES)
    assert _mode(path) == "wal"
    assert _rows(path) == before

    assert gate.prepare_register() == []
    assert capsys.readouterr().out == "", "a second call says nothing"


def test_a_gate_with_no_register_prepares_nothing(tmp_path, monkeypatch,
                                                  capsys):
    from rota import paths
    from rota.tools import gate

    missing = tmp_path / "absent" / "cassettes.db"
    monkeypatch.setattr(paths, "DEV_DB", missing)
    assert gate.prepare_register() == []
    assert not missing.exists() and not missing.parent.exists()
    assert capsys.readouterr().out == ""


def _packed(tmp_path, monkeypatch, db):
    """`pack` of `db`, with the tracked manifest moved out of the tree."""
    from rota.testkit import cassette_store

    monkeypatch.setattr(cassette_store, "MANIFEST", tmp_path / "manifest.json")
    return cassette_store.pack(db, out_dir=tmp_path / "packed", tag="t")


def test_a_pull_places_a_wal_register_with_both_indexes(
        tmp_path, monkeypatch, capsys):
    import shutil

    from rota.testkit import cassette_store
    from rota.tools import index_register

    source = tmp_path / "source.db"
    _an_old_register(source)
    gz, manifest = _packed(tmp_path, monkeypatch, source)
    monkeypatch.setattr(cassette_store, "_download",
                        lambda url, dest, *a, **k: shutil.copyfile(gz, dest))
    dest = tmp_path / "checkout" / "cassettes.db"

    cassette_store.pull(dest, manifest)
    err = [line for line in capsys.readouterr().err.splitlines()
           if "register: built" in line]
    assert len(err) == 1, err
    assert _indexes(dest) == set(cassettes.SEQ_INDEXES)
    assert _mode(dest) == "wal"
    assert _rows(dest) == _rows(source)
    leftovers = sorted(p.name for p in dest.parent.iterdir())
    assert leftovers == ["cassettes.db"], leftovers

    assert index_register.prepare(dest) == [], "a second call builds nothing"
    assert capsys.readouterr().out == ""


def test_a_published_snapshot_of_an_indexed_register_carries_the_indexes(
        tmp_path, monkeypatch):
    """`pack` copies every page through the backup API, so a register that
    holds the indexes publishes them."""
    import gzip
    import shutil

    from rota.tools import index_register

    source = tmp_path / "source.db"
    _an_old_register(source)
    index_register.prepare(source)
    gz, _ = _packed(tmp_path, monkeypatch, source)
    snap = tmp_path / "snap.db"
    with gzip.open(gz, "rb") as g, open(snap, "wb") as f:
        shutil.copyfileobj(g, f)
    assert _indexes(snap) == set(cassettes.SEQ_INDEXES)
    assert _mode(snap) == "delete"
