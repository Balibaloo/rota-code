"""Frame 233: the stop reason of a recorded reply, in one store.

The `done_reason` column of `cassettes` holds the reason, and both replay
backends return it in `raw`. `Completion.done_reason` is the one reader, so
a replayed session fires the rules that the live session fired (rule C76).
Every database here is a temporary file. No test opens the register.
"""
from __future__ import annotations

import ast
from pathlib import Path

from rota.core.runner import run_session
from rota.llm.cassettes import RecordingBackend, ReplayOnlyBackend, open_dev_db
from rota.llm.llm import Pins
from tests.rota.test_runner import (  # noqa: F401 -- the fixtures
    _CUT_AFTER, _CutFirst, db, wake_developer, worktree)

ROOT = Path(__file__).resolve().parents[2]


class _Taped:
    """Record each call, then answer it from the cassette alone. The runner
    sees only what the store gives back."""

    name = "taped"

    def __init__(self, inner, conn):
        self.inner = inner
        self.record = RecordingBackend(inner, conn, replay=False)
        self.replay = ReplayOnlyBackend(conn)

    def complete(self, system, user, pins, tools=None):
        self.record.complete(system, user, pins, tools=tools)
        return self.replay.complete(system, user, pins, tools=tools)


def test_a_replayed_length_stop_fires_the_length_rule(db, worktree, tmp_path):
    """The old store kept the text alone, so a replay of a cut reply read as
    whole, and the cut line never reached the next prompt (frame 233)."""
    inner = _CutFirst([
        "TOOL: code.write(path='src/acct.py', text='VALUE = 1\n')\n"
        "Now I explain the change at length, because the account",
        "Done.",
    ])
    run_session(db, wake_developer(), pins=Pins(model="scripted"), batch_id="b1",
                backend=_Taped(inner, open_dev_db(tmp_path / "cassettes.db")))
    assert _CUT_AFTER in inner.calls[1][1], inner.calls[1][1][-1500:]


def test_a_replay_returns_the_recorded_reason_and_a_plain_end_as_none(tmp_path):
    conn = open_dev_db(tmp_path / "cassettes.db")
    pins = Pins(model="scripted")
    inner = _CutFirst(["cut", "whole"])
    RecordingBackend(inner, conn).complete("sys", "a", pins)
    RecordingBackend(inner, conn).complete("sys", "b", pins)
    replay = ReplayOnlyBackend(conn)
    assert replay.complete("sys", "a", pins).done_reason == "length"
    assert replay.complete("sys", "b", pins).raw == {}
    assert dict(conn.execute("SELECT user, done_reason FROM cassettes")) == {
        "a": "length", "b": ""}


def _texts(scope=("rota", "probes")):
    """Each string constant of the package and the probes, with its file and
    the function that holds it."""
    for top in scope:
        for path in sorted((ROOT / top).rglob("*.py")):
            rel = path.relative_to(ROOT).as_posix()
            tree = ast.parse(path.read_bytes().decode("utf-8"))
            spans = sorted(((n.lineno, n.end_lineno or n.lineno, n.name)
                            for n in ast.walk(tree)
                            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))),
                           key=lambda s: s[1] - s[0])
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    owner = next((s[2] for s in spans
                                  if s[0] <= node.lineno <= s[1]), "<module>")
                    yield rel, owner, node.value


def test_one_reader_of_the_stop_reason():
    """`Completion.done_reason` alone reads the reason from `raw`, and `_ROW`
    alone reads the column. A second reader turns this red."""
    raw_readers, column_readers = set(), set()
    for top in ("rota", "probes"):
        for path in sorted((ROOT / top).rglob("*.py")):
            rel = path.relative_to(ROOT).as_posix()
            tree = ast.parse(path.read_bytes().decode("utf-8"))
            for fn in ast.walk(tree):
                if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for node in ast.walk(fn):
                    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                            and node.func.attr == "get" and node.args
                            and isinstance(node.args[0], ast.Constant)
                            and node.args[0].value == "done_reason"):
                        raw_readers.add((rel, fn.name))
    for rel, owner, text in _texts():
        if "SELECT" in text and "done_reason" in text:
            column_readers.add((rel, owner))
    assert raw_readers == {("rota/llm/llm.py", "done_reason")}
    # `_reason_column` reads the old side table once, to move it.
    assert column_readers == {("rota/llm/cassettes.py", "<module>"),
                              ("rota/llm/cassettes.py", "_reason_column")}


def test_one_store_of_the_stop_reason():
    """Only `cassettes.py` writes the column, and no side table exists. The
    migration of the night's old `done_reasons` table is the one place that
    names it."""
    writers, side = set(), set()
    for rel, owner, text in _texts():
        if "done_reason" in text and any(w in text for w in (
                "INSERT", "UPDATE", "ALTER", "CREATE")):
            writers.add((rel, owner))
        if "done_reasons" in text:
            side.add((rel, owner))
    assert writers == {("rota/llm/cassettes.py", "_reason_column"),
                       ("rota/llm/cassettes.py", "complete"),
                       ("rota/llm/cassettes.py", "mark_reason"),
                       ("rota/llm/cassettes.py", "<module>")}
    assert side == {("rota/llm/cassettes.py", "_reason_column")}
