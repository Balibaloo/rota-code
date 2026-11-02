"""
The invariants of frame 144, item 4, over any database.

    python -m rota.tools.invariants PATH            # a night's database, read-only
    python -m rota.tools.invariants PATH --root DIR # the project, for I2's bodies

Each invariant is a proposition about rows that every state of rota must
hold (`plans/frame144-design.md`, section 1, change 2). The scene tests run
the checker on each scene's end, and a night's database is checked by path,
read-only and immutable, so a check never moves the night it reads.

The audit (`rota/tools/audit.py`) checks refs and identity. This checker
names the states a batch, a test, a key and an ask may be in. I7 and I8
repeat the audit's group 3 and group 2 under the design's names. I9 is the
audit's group 5 with the rows that are answered by design removed. I10 is
not in the design: night 126 wrote the text `'high'` into the integer
column `items.priority`, and the next `loop.step` crashed in `next_batch`
(`plans/night126-read.md`, section 6).
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
from dataclasses import dataclass
from pathlib import Path

# The sentence of each invariant, by its name in the design.
INVARIANTS = {
    "I1": "a criterion holds at most one test",
    "I2": "an inh_ row has no criterion, and its body is the project file at the batch's base",
    "I3": "a merged batch's latest run of each of its own tests at its head is a pass",
    "I4": "a run row's test is a test of the run's batch",
    "I5": "a parked batch the team gave up on holds one open park ask, and an open park "
          "ask names such a batch",
    "I6": "a quarantined key never names a merged or abandoned batch",
    "I7": "at most one batch runs",
    "I8": "one open batch per item",
    "I9": "an answered message has an answer, except the rows answered by design "
          "(the rest are seat faults, frame 174)",
    "I10": "an integer column holds integers",
}

def _carries(verb: str) -> bool:
    """
    Whether the verb carries material and asks for no reply.

    The session that reads such a message answers it when it commits
    (`db.session_commit`), and no reply row follows by design. On night 119,
    68 of the audit's 72 findings were rows of this kind
    (`plans/frame144-inventory.md`, section 2). A carrier is a verb outside
    `db.OWED_A_REPLY` and outside the pages, which his reply answers. This
    is the one list of the owed verbs (fact F16, review 1, finding 6).
    """
    from ..core.db import OWED_A_REPLY, PAGE_VERBS

    return verb not in OWED_A_REPLY and verb not in PAGE_VERBS


@dataclass(frozen=True)
class Finding:
    invariant: str
    text: str

    def __str__(self) -> str:
        return f"{self.invariant}: {self.text}"


def _rows(conn: sqlite3.Connection, sql: str, args: tuple = ()) -> list:
    try:
        return conn.execute(sql, args).fetchall()
    except sqlite3.OperationalError:
        return []          # a database from before the column existed


def i1(conn) -> list[Finding]:
    return [Finding("I1", f"criterion {r[0]} holds {r[1]} tests: {r[2]}")
            for r in _rows(conn, "SELECT criterion_id, COUNT(*), group_concat(id) FROM tests "
                                 "WHERE criterion_id IS NOT NULL GROUP BY criterion_id "
                                 "HAVING COUNT(*) > 1")]


def _git(root: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                             timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", errors="replace")


def _base(root: Path, conn, batch: str) -> str | None:
    """The commit that the batch forked from, as `worktrees.base` reads it:
    the merge base of the batch's head with the project's HEAD. A merged
    batch's head is on HEAD, so its base is not read here."""
    row = _rows(conn, "SELECT status, head_commit FROM batches WHERE id = ?", (batch,))
    if not row or row[0][0] == "merged":
        return None
    head = (_git(root, "rev-parse", "HEAD") or "").strip()
    if not head:
        return None
    # A batch with no commit forks from HEAD when it starts.
    tip = row[0][1] or head
    return (_git(root, "merge-base", head, tip) or "").strip() or None


def i2(conn, root: Path | None) -> list[Finding]:
    out = []
    for r in _rows(conn, "SELECT id, batch_id, criterion_id, path, body FROM tests "
                         "WHERE id LIKE 'inh\\_%' ESCAPE '\\' ORDER BY id"):
        if r[2] is not None:
            out.append(Finding("I2", f"{r[0]} holds criterion {r[2]}"))
        if root is None:
            continue
        base = _base(root, conn, r[1])
        if base is None:
            continue
        found = _git(root, "show", f"{base}:{r[3]}")
        if found is None:
            out.append(Finding("I2", f"{r[0]}: {r[3]} is not in {r[1]}'s base {base[:10]}"))
        elif found.replace("\r\n", "\n") != r[4].replace("\r\n", "\n"):
            out.append(Finding("I2", f"{r[0]}: its body is not {r[3]} at {r[1]}'s base "
                                     f"{base[:10]}"))
    return out


def i3(conn) -> list[Finding]:
    out = []
    for b in _rows(conn, "SELECT id, head_commit FROM batches WHERE status = 'merged' "
                         "ORDER BY id"):
        for t in _rows(conn, "SELECT id FROM tests WHERE batch_id = ? ORDER BY id", (b[0],)):
            run = _rows(conn, "SELECT result FROM latest_runs WHERE batch_id = ? AND test_id = ? "
                              "AND commit_sha = ?", (b[0], t[0], b[1]))
            if not run:
                out.append(Finding("I3", f"merged {b[0]}: {t[0]} has no run at its head "
                                         f"{str(b[1])[:10]}"))
            elif run[0][0] != "pass":
                out.append(Finding("I3", f"merged {b[0]}: {t[0]}'s latest run at its head "
                                         f"is {run[0][0]}"))
    return out


def i4(conn) -> list[Finding]:
    # Fact F4 leaves this read on `test_runs`: it counts every run that names
    # a test of another batch, not the newest run.
    out = []
    for r in _rows(conn, "SELECT r.test_id, r.batch_id, t.batch_id, COUNT(*) FROM test_runs r "
                         "LEFT JOIN tests t ON t.id = r.test_id "
                         "WHERE t.id IS NULL OR t.batch_id != r.batch_id "
                         "GROUP BY r.test_id, r.batch_id, t.batch_id ORDER BY r.test_id, r.batch_id"):
        whose = f"a test of {r[2]}" if r[2] is not None else "no tests row"
        out.append(Finding("I4", f"{r[3]} run(s) of {r[1]} name {r[0]}, which is {whose}"))
    return out


def _owes_ask(conn, batch: str, status: str, approval, approval_ver, version) -> bool:
    """The park that `predicates.park_ask` asks about: a deferred batch the team
    gave up on (`scheduler.gave_up`), on an item that is not contested.

    A batch at or past `loop_cap` with a red run at its head owes the ask too,
    since frame 330's pass 3 (d959c33f): point 3 of the ruling of 2026-10-08
    sends the page when a criterion's own test is red, and dry1 turn 14
    parked at the cap with no page. Before that pass the loop-cap park
    climbed the ladder and owed no ask (the delta review of b43b99d6,
    2026-10-07, on night 126's bg_1). A batch past the cap whose head is
    green is not parked and owes none.

    A park whose message rests owes no open ask: a note is written closed,
    and a page approved whole is the ceiling (ruled: Roman, 2026-10-08,
    points 3 and 5). `scheduler.park_owns` is the test that `park_ask` and
    the quarantined wake read too."""
    from ..core import scheduler

    return (scheduler.park_owns(conn, batch)
            and not scheduler.park_rests(conn, batch))


def i5(conn) -> list[Finding]:
    from ..core import scheduler

    out = []
    asks = [r[0] for r in _rows(conn, "SELECT id FROM messages WHERE status = 'open' "
                                      "AND substr(id, 1, ?) = ?",
                                (len(scheduler.PARK_ASK), scheduler.PARK_ASK))]
    by_batch: dict[str, list[str]] = {}
    for a in asks:
        by_batch.setdefault(scheduler.park_ask_batch(a) or "", []).append(a)
    for b, status, approval, approval_ver, version in _rows(
            conn, "SELECT b.id, b.status, i.approval, i.approval_ver, i.version "
                  "FROM batches b JOIN items i ON i.id = b.item_id ORDER BY b.id"):
        try:
            owes = _owes_ask(conn, b, status, approval, approval_ver, version)
        except (sqlite3.Error, KeyError, ValueError) as e:
            out.append(Finding("I5", f"{b}: the park cannot be read ({e})"))
            continue
        held = by_batch.pop(b, [])
        if owes and len(held) != 1:
            out.append(Finding("I5", f"{b}, parked and given up on, holds {len(held)} "
                                     f"open park asks"))
        elif held and not owes:
            out.append(Finding("I5", f"open park ask {held[0]} names {b}, which owes no ask"))
    for b, held in by_batch.items():
        out.append(Finding("I5", f"open park ask {held[0]} names {b!r}, which is no batch"))
    return out


def i6(conn) -> list[Finding]:
    gone = {r[0]: r[1] for r in _rows(conn, "SELECT id, status FROM batches "
                                            "WHERE status IN ('merged', 'abandoned')")}
    from ..core.scheduler import key_parts, quarantined_keys

    try:
        keys = quarantined_keys(conn)
    except sqlite3.OperationalError:
        keys = []          # a database from before the table existed
    out = []
    for key in keys:
        # The one parse of a tick key (fact F20, review of pass 1, finding 6).
        for ref in key_parts(key)[2]:
            if ref in gone:
                out.append(Finding("I6", f"quarantined {key} names {gone[ref]} {ref}"))
    return out


def i7(conn) -> list[Finding]:
    running = [r[0] for r in _rows(conn, "SELECT id FROM batches WHERE status = 'running' "
                                         "ORDER BY id")]
    return [Finding("I7", f"{len(running)} batches run: {running}")] if len(running) > 1 else []


def i8(conn) -> list[Finding]:
    return [Finding("I8", f"item {r[0]} has {r[1]} open batches: {r[2]}")
            for r in _rows(conn, "SELECT item_id, COUNT(*), group_concat(id) FROM batches "
                                 "WHERE status IN ('pending', 'running', 'deferred') "
                                 "GROUP BY item_id HAVING COUNT(*) > 1")]


def i9(conn) -> list[Finding]:
    """The audit's group 5, less three kinds of row that are answered by
    design:

    - A message whose verb carries material is answered by the session that
      reads it (`_carries`).
    - A present to the principal whose refs hold a batch, a touch note or a
      quarantine report, closes at the keypress when the principal approves
      it, and no verdict row follows (`principal.land`: "A touch note is
      read, not ruled on (P4, R7: nothing waits on it)").
    - A challenge to the Tester is answered by a new version of a test that
      it names, written by the session that the challenge woke
      (`_replaced`). The Tester's replace is the answer, and no reply row
      follows (ruled: the judging session, 2026-10-05, frame 132's question
      4, `sandbox._same_refs_refusal`)."""
    batches = {r[0] for r in _rows(conn, "SELECT id FROM batches")}
    out = []
    for r in _rows(conn, "SELECT m.id, m.from_role, m.to_role, m.verb, m.body_refs "
                         "FROM messages m WHERE m.status = 'answered' AND NOT EXISTS "
                         "(SELECT 1 FROM messages a WHERE a.cause_id = m.id) ORDER BY m.seq"):
        if _carries(r[3]):
            continue
        if r[3] == "present" and r[2] == "principal" and batches & set(_refs(r[4])):
            continue
        if r[3] == "challenge" and r[2] == "tester" and _replaced(conn, r[0], r[4]):
            continue
        # A drop on the shift page closes the earlier request's asks, and its
        # `closed:` row names the verdict that closed each one (frame 193's
        # design, 2.F.9, finding 8).
        if _rows(conn, "SELECT 1 FROM config WHERE key = ?", (f"closed:{r[0]}",)):
            continue
        out.append(Finding("I9", f"{r[0]}, {r[1]} to {r[2]} {r[3]}, is answered and "
                                 f"nothing answers it"))
    return out


def _refs(refs: str) -> list[str]:
    try:
        loaded = json.loads(refs or "[]")
    except ValueError:
        return []
    return [x for x in loaded if isinstance(x, str)] if isinstance(loaded, list) else []


def _replaced(conn, msg_id: str, refs: str) -> bool:
    """The challenge woke a committed session, and that session wrote a new
    version of a test that the challenge names.

    A version above 1 alone does not say which came first. A second
    challenge on a test at version 2 with no reply then read as answered
    (the delta review of b43b99d6, its third low). The session's receipt
    on the test is the write that follows the challenge.

    The current `tests.version` does not say that this write was a replace.
    A woken session can create the test, and a later session can replace
    it. `receipts.new_version` is the table's version at the write
    (`db.bump_version`), not the row's, so an earlier receipt on the same
    row says that the row stood before the woken write (the review of
    96fe3425, its fourth low)."""
    return any(_rows(conn, "SELECT 1 FROM receipts r JOIN sessions s ON s.id = r.session_id "
                           "WHERE s.trigger_msg = ? AND s.committed = 1 "
                           "AND r.table_name = 'tests' AND r.row_id = ? "
                           "AND EXISTS (SELECT 1 FROM receipts e WHERE e.table_name = 'tests' "
                           "AND e.row_id = r.row_id AND e.new_version < r.new_version)",
                     (msg_id, i))
               for i in _refs(refs))


def i10(conn) -> list[Finding]:
    out = []
    for (t,) in _rows(conn, "SELECT name FROM sqlite_master WHERE type = 'table' "
                            "AND name NOT LIKE 'sqlite_%' ORDER BY name"):
        for c in _rows(conn, f"PRAGMA table_info({t})"):
            name, decl = c[1], (c[2] or "").upper()
            if "INT" not in decl:
                continue
            for r in _rows(conn, f"SELECT rowid, {name}, typeof({name}) FROM {t} "
                                 f"WHERE typeof({name}) NOT IN ('integer', 'null')"):
                out.append(Finding("I10", f"{t}.{name} rowid {r[0]} holds {r[2]} {r[1]!r}"))
    return out


def project_root(conn) -> Path | None:
    row = _rows(conn, "SELECT value FROM config WHERE key = 'project_root'")
    root = Path(row[0][0]) if row and row[0][0] else None
    return root if root is not None and (root / ".git").exists() else None


def check(conn: sqlite3.Connection, root: Path | None = None) -> list[Finding]:
    """Every finding of I1 to I10, in order. Empty is the claim. The check
    only reads. I2 reads the project's files through git, at `root` or at
    the database's `project_root`, and skips the bodies when neither is a
    repository."""
    root = root or project_root(conn)
    return [*i1(conn), *i2(conn, root), *i3(conn), *i4(conn), *i5(conn), *i6(conn),
            *i7(conn), *i8(conn), *i9(conn), *i10(conn)]


def open_readonly(path: str | Path) -> sqlite3.Connection:
    """A night's database, read-only and immutable, so no read writes a
    journal beside the copy."""
    p = Path(path).resolve().as_posix()
    conn = sqlite3.connect(f"file:{p}?mode=ro&immutable=1", uri=True)
    # `scheduler.parked` reads its rows by name, as every rota connection does.
    conn.row_factory = sqlite3.Row
    # A night's file from before fact F4 has no `latest_runs` view.
    from ..core.db import latest_runs_view
    latest_runs_view(conn)
    return conn


def main(argv: list[str]) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="python -m rota.tools.invariants")
    ap.add_argument("db")
    ap.add_argument("--root", default=None)
    ap.add_argument("--all", action="store_true", help="print every finding")
    a = ap.parse_args(argv)
    conn = open_readonly(a.db)
    found = check(conn, Path(a.root) if a.root else None)
    for name, sentence in INVARIANTS.items():
        mine = [f for f in found if f.invariant == name]
        print(f"{name:4} {len(mine):4}  {sentence}")
        for f in (mine if a.all else mine[:5]):
            print(f"           {f.text}")
        if len(mine) > 5 and not a.all:
            print(f"           ... {len(mine) - 5} more")
    print(f"{len(found)} finding(s)")
    return 1 if found else 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
