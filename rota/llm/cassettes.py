"""
Cassette recording and replay.

Every real completion is recorded with its pins and its exact prompt. That buys
three things:

  * **Deterministic replay of real model output.** T0 can drive the plumbing with
    completions an actual model produced, rather than ones I invented — the
    difference matters, because hand-written scripts encode my assumptions about
    what a model does, and cassettes encode what one actually did.
  * **Prompt iteration without spending model time.** Editing a *validator* or a
    parser and re-running against cassettes is instant.
  * **Evidence.** "This case passed on this prompt with this model" is a claim
    you can re-check later instead of a memory.

Cassettes live in `.rota/dev.db`, a **separate file** from the framework
database. That separation is not fussiness: T0-S1 asserts a failed session leaves
zero rows in any table, and instrumentation sharing the artefact store would make
that assertion ambiguous. Artefacts are the system's world; cassettes are ours.

Keying: (model, temperature, num_ctx, system, user) hashed. Change the prompt and
you get a miss, which is correct — a recording made against a different prompt is
not evidence about this one.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from .llm import Backend, Completion, LLMUnavailable, Pins

DEV_SCHEMA = """
CREATE TABLE IF NOT EXISTS cassettes (
    key          TEXT PRIMARY KEY,
    model        TEXT NOT NULL,
    temperature  REAL NOT NULL,
    num_ctx      INTEGER NOT NULL,
    prompt_hash  TEXT NOT NULL,
    system       TEXT NOT NULL,
    user         TEXT NOT NULL,
    completion   TEXT NOT NULL,
    tool_calls   TEXT NOT NULL DEFAULT '[]',   -- native calls, as JSON
    backend      TEXT NOT NULL,
    hits         INTEGER NOT NULL DEFAULT 0
);

-- Pass-rate history per (case, model, prompt version). A case that passed 5/5
-- for weeks and now passes 3/5 is a prompt regression signal, so the history is
-- itself an artefact rather than a number printed once and lost.
CREATE TABLE IF NOT EXISTS case_runs (
    case_id      TEXT NOT NULL,
    model        TEXT NOT NULL,
    prompt_hash  TEXT NOT NULL,
    run_no       INTEGER NOT NULL,
    passed       INTEGER NOT NULL,
    problems     TEXT NOT NULL DEFAULT '[]',
    seq          INTEGER NOT NULL,
    PRIMARY KEY (case_id, model, prompt_hash, run_no, seq)
);
"""


def open_dev_db(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript(DEV_SCHEMA)
    return conn


def key_for(system: str, user: str, pins: Pins, protocol: str = "text") -> str:
    """
    A recording is evidence about one prompt, one model, and one *protocol*.

    Native tool calling and the `TOOL:` text protocol produce different replies
    to the same prompt and fail in different ways. Keying them together would
    let a text-protocol recording answer for a native run, which is not evidence
    about it.
    """
    blob = json.dumps(
        [pins.model, pins.temperature, pins.num_ctx, protocol, system, user],
        sort_keys=True,
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32]




def _calls_to(calls) -> str:
    """Native calls, as JSON. A cassette that dropped them would replay an empty
    completion — with native tool calling the text is usually blank and every
    instruction is in the structure."""
    return json.dumps([{"name": c.name, "args": c.args} for c in calls or []])


def _calls_from(blob: str):
    from .llm import NativeCall

    return [NativeCall(name=c["name"], args=c["args"])
            for c in json.loads(blob or "[]")]




class RecordingBackend:
    """
    Wraps a real backend and records everything it returns.

    On a hit it replays instead of calling out, so a re-run of a green suite
    costs nothing. Pass `refresh=True` to force live calls and overwrite.
    """

    name = "recording"

    def __init__(self, inner: Backend, dev_conn: sqlite3.Connection,
                 *, replay: bool = True, refresh: bool = False):
        self.inner = inner
        self.conn = dev_conn
        self.replay = replay
        self.refresh = refresh
        self.hits = 0
        self.misses = 0

    def complete(self, system: str, user: str, pins: Pins,
                 tools: list | None = None) -> Completion:
        protocol = "native" if tools else "text"
        key = key_for(system, user, pins, protocol)

        if self.replay and not self.refresh:
            row = self.conn.execute(
                "SELECT completion, backend, tool_calls FROM cassettes "
                "WHERE key = ?", (key,)).fetchone()
            if row:
                self.hits += 1
                self.conn.execute(
                    "UPDATE cassettes SET hits = hits + 1 WHERE key = ?", (key,))
                return Completion(
                    text=row["completion"], pins=pins,
                    backend=f"cassette:{row['backend']}",
                    tool_calls=_calls_from(row["tool_calls"]))

        self.misses += 1
        result = self.inner.complete(system, user, pins, tools=tools)
        self.conn.execute(
            "INSERT OR REPLACE INTO cassettes "
            "(key, model, temperature, num_ctx, prompt_hash, system, user, "
            " completion, tool_calls, backend, hits) VALUES (?,?,?,?,?,?,?,?,?,?,0)",
            (key, pins.model, pins.temperature, pins.num_ctx, pins.prompt_hash,
             system, user, result.text, _calls_to(result.tool_calls),
             result.backend),
        )
        return result


class ReplayOnlyBackend:
    """
    Cassettes or nothing.

    Used where a test must never touch a model: a miss is a hard failure rather
    than a silent fallback, because a suite that quietly calls out when its
    recording is stale is no longer deterministic and will fail differently on
    someone else's machine.
    """

    name = "replay"

    def __init__(self, dev_conn: sqlite3.Connection):
        self.conn = dev_conn

    def complete(self, system: str, user: str, pins: Pins,
                 tools: list | None = None) -> Completion:
        key = key_for(system, user, pins, "native" if tools else "text")
        row = self.conn.execute(
            "SELECT completion, backend, tool_calls FROM cassettes WHERE key = ?",
            (key,)
        ).fetchone()
        if not row:
            raise LLMUnavailable(
                f"no cassette for {pins.model} key={key[:12]}… — record one with "
                f"RecordingBackend, or the prompt changed since it was made"
            )
        return Completion(text=row["completion"], pins=pins,
                          backend=f"cassette:{row['backend']}",
                          tool_calls=_calls_from(row["tool_calls"]))


def record_case_run(conn: sqlite3.Connection, case_id: str, pins: Pins,
                    run_no: int, passed: bool, problems: list[str]) -> None:
    seq = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) + 1 n FROM case_runs").fetchone()["n"]
    conn.execute(
        "INSERT INTO case_runs (case_id, model, prompt_hash, run_no, passed, "
        "problems, seq) VALUES (?,?,?,?,?,?,?)",
        (case_id, pins.model, pins.prompt_hash, run_no, int(passed),
         json.dumps(problems), seq),
    )


def pass_rate_history(conn: sqlite3.Connection, case_id: str) -> list[dict]:
    """Pass rate per (model, prompt_hash), newest first. The regression signal."""
    return [dict(r) for r in conn.execute(
        "SELECT model, prompt_hash, COUNT(*) AS runs, SUM(passed) AS passed, "
        "       MAX(seq) AS last_seq "
        "FROM case_runs WHERE case_id = ? "
        "GROUP BY model, prompt_hash ORDER BY last_seq DESC", (case_id,))]
