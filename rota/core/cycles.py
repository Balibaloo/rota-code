"""
The cycle alert: the committed sessions repeat a round and move nothing.

Night 92 (observed, 2026-09-24): the Developer woke on `tick:batch_start`
for `b_2` nineteen times, `s283` to `s301`. Each session made the same calls
and changed nothing, and no counter saw it, because two rules erased each
other's counts. Night 91 ran a round of ten sessions the same way.

The alert reads the rows only. It quarantines nothing and writes no row. It
is for the session that watches the night. That session reads and tunes its
false positives before the alert gates (ruled: Roman, 2026-09-24, an alert
first).
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Cycle:
    """A round of `period` sessions, repeated `rounds` times at the end."""
    period: int
    rounds: int
    keys: tuple[str, ...]           # the last round's wake keys, in order
    identity: tuple[str, ...]       # the sorted set of keys

    def line(self) -> str:
        return (f"CYCLE: period {self.period}, rounds {self.rounds}, "
                f"wakes: {', '.join(self.keys)}")


def _key(s, verbs: dict) -> str:
    # The detail is in the key, because a tick's detail carries the attempt.
    # An honest retry at attempt n+1 is then a new key, not a round. A
    # message's detail is its verb (ruled: Roman, 2026-09-24, revision 2).
    detail = (str(verbs.get(s["trigger_msg"]) or "") if s["wake_kind"] == "message"
              else (s["wake_detail"] or ""))
    return f"{s['role']}|{s['wake_kind']}|{detail}|{s['wake_refs'] or ''}"


def cycle(conn: sqlite3.Connection, cap: int = 16,
          last: str | None = None) -> Cycle | None:
    """
    The smallest period, up to `cap`, whose last rounds repeat, or None.

    Rounds repeat when their key sequences are equal and their receipt
    signatures are equal. A signature names each existing row as
    `(table, row_id)` and each new row as `(table, new)`. The version is not
    in it, because `receipts.new_version` counts per table and not per row.

    `last` names the session to read up to, so a pin can ask about a moment
    of a night. None reads every committed session.
    """
    from . import config

    verbs = {r["id"]: r["verb"] for r in conn.execute("SELECT id, verb FROM messages")}
    sessions = conn.execute(
        "SELECT id, seq, role, wake_kind, wake_detail, wake_refs, trigger_msg "
        "FROM sessions WHERE committed = 1 ORDER BY seq").fetchall()
    if last is not None:
        ids = [s["id"] for s in sessions]
        if last not in ids:
            return None
        sessions = sessions[:ids.index(last) + 1]
    if len(sessions) < 2:
        return None

    wrote: dict[str, list[tuple[str, str]]] = {}
    for r in conn.execute("SELECT session_id, table_name, row_id FROM receipts "
                          "ORDER BY new_version"):
        wrote.setdefault(r["session_id"], []).append((r["table_name"], r["row_id"]))
    first: dict[tuple[str, str], int] = {}
    for s in sessions:
        for row in wrote.get(s["id"], ()):
            first.setdefault(row, s["seq"])

    keys = [_key(s, verbs) for s in sessions]

    def signature(lo: int, hi: int) -> list[tuple[str, str]]:
        start = sessions[lo]["seq"]
        return sorted((t, rid if first[(t, rid)] < start else "new")
                      for s in sessions[lo:hi] for t, rid in wrote.get(s["id"], ()))

    def committed_code(lo: int, hi: int) -> bool:
        # Only a commit updates an existing batch row, and a commit is a move.
        # A detail with no attempt otherwise reads a fix loop as a round
        # (observed: the diff review of frame 83, 2026-09-24).
        start = sessions[lo]["seq"]
        return any(t == "batches" and first[(t, rid)] < start
                   for s in sessions[lo:hi] for t, rid in wrote.get(s["id"], ()))

    # The run of the last key at the end, not its count over the night. Four
    # honest firings spread over a night are not a stall (observed: the diff
    # review of frame 83, 2026-09-24).
    run = 1
    while run < len(keys) and keys[-run - 1] == keys[-1]:
        run += 1
    attempt_cap = int(config.get(conn, "tick_attempt_cap"))
    n_all = len(sessions)
    for n in range(1, cap + 1):
        # Three rounds, or two for a period of one whose key already ran
        # past the tick cap (ruled: Roman, 2026-09-24, revision 2).
        rounds = 2 if n == 1 and run > attempt_cap else 3
        if rounds * n > n_all:
            continue
        spans = [(n_all - (k + 1) * n, n_all - k * n) for k in range(rounds)]
        if len({tuple(keys[lo:hi]) for lo, hi in spans}) != 1:
            continue
        if any(committed_code(lo, hi) for lo, hi in spans):
            continue
        if len({tuple(signature(lo, hi)) for lo, hi in spans}) != 1:
            continue
        found = tuple(keys[spans[0][0]:spans[0][1]])
        return Cycle(period=n, rounds=rounds, keys=found,
                     identity=tuple(sorted(set(found))))
    return None


def walk_lines(step, seen: set) -> list[str]:
    """
    Return the lines the walk prints for one step. The walk prints every
    scheduler action's note, and the cycle line once per identity.

    The walk printed `do:harness` and `do:merge` only, so night 92's
    preempts left no line in the log (observed: night 92, 2026-09-24).
    This function holds the lines because the walk runs on import. A test
    cannot import the walk.
    """
    out: list[str] = []
    wake = getattr(step, "wake", None)
    if wake is not None and wake.kind.startswith("do:"):
        out.append(f"  {wake.kind}: {step.note}")
    found = getattr(step, "cycle", None)
    if found is not None and found.identity not in seen:
        seen.add(found.identity)
        out.append(found.line())
    return out
