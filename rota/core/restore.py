"""
The structure puts a removed statement back, with no model session.

Frame 173, build 3. Roman, 2026-11-08 10:23: the restore of removed lines
is not a model limitation. The fork holds the statement, and
`removed_statements` names it at every commit. On dry run 8 a Developer on
qwen3.5:9b put the line back 27 minutes after the removal, not byte for
byte, and two more commits in the same wake broke two inherited files.

The restore runs in the scheduler's tick, before a `touch_mistaken` wake
reaches a seat, as `lifecycle.merge` runs for a `do:merge` wake. A door
stages its writes until the session lands, so the `mistake` row is not in
the database while `batches.judge_touch` runs.
"""
from __future__ import annotations

import ast
import sqlite3
import subprocess
from pathlib import Path


def restore_stray(conn: sqlite3.Connection, batch_id: str, grain: str,
                  act: str, *, only: set[int] | None = None,
                  row_head: str | None = None) -> dict:
    """Put back each fork statement of `grain` that the head lacks, and
    commit. `act` names who ordered the restore: his ruling id or the
    Architect's judgement. Returns {"restored": sha, "statements": [...]}
    or {"reason": one sentence}. A reason changes nothing. `only` names the
    base indexes to put back, as his keep names one statement. `row_head`
    names the head of the row to mark, when an earlier restore moved it."""
    from . import harness, worktrees
    from ..roles.api import _base_texts, removed_statements

    row = conn.execute("SELECT head_commit FROM batches WHERE id = ?",
                       (batch_id,)).fetchone()
    tree = harness.worktree_of(conn, batch_id)
    if row is None or not row["head_commit"] or not tree or not Path(tree).is_dir():
        return {"reason": f"{batch_id} has no worktree and head to restore in"}
    head = row["head_commit"]
    path, _sep, owner = grain.partition("::")
    try:
        root = worktrees.project_root(conn)
    except worktrees.WorktreeError:
        root = None
    try:
        fork = worktrees.base(tree, root)
    except worktrees.WorktreeError:
        return {"reason": "git cannot name the fork of the batch"}
    base = _base_texts(tree, fork, [path]).get(path)
    if not base:
        return {"reason": f"the fork does not hold {path}"}
    target = Path(tree) / path
    if not target.is_file():
        return {"reason": f"{path} is gone at the head"}
    # A restore commits its own path only, and a tracked change in the
    # tree could be in that path. So the restore waits for a tree that holds
    # only committed work (law 1: the structure writes no seat's change).
    furniture = set(worktrees.batch_furniture(conn, batch_id))
    dirty = [p for p in subprocess.run(
        [*worktrees.GIT, "-C", str(tree), "status", "--porcelain", "-z",
         "--untracked-files=no", "--", ".", ":(exclude).venv", ":(exclude).rota"],
        capture_output=True).stdout.decode("utf-8", "replace").split("\0")
        if p and p[3:] not in furniture]
    if dirty:
        return {"reason": "the worktree holds uncommitted changes"}
    raw = target.read_bytes()
    now = raw.decode("utf-8", "replace").replace("\r\n", "\n")
    got = removed_statements(base, now)
    if got is False:
        return {"reason": f"{path} does not parse at the fork or at the head"}
    lost = sorted({i for o, i in got[0] if (not owner or o == owner)
                   and (only is None or i in only)})
    if not lost:
        return {"reason": f"the head holds every statement of {grain}"}
    ol = base.splitlines(keepends=True)
    nl = now.splitlines(keepends=True)
    spans = _statement_spans(base)
    said: list[str] = []
    # The last statement first, so an insert does not move the next place.
    for i in sorted(lost, reverse=True):
        end = spans.get(i, i)
        at = _place(ol, nl, i, end)
        if isinstance(at, str):
            return {"reason": at}
        nl[at:at] = ol[i:end + 1]
        said.append(ol[i].strip())
    text = "".join(nl)
    if b"\r\n" in raw:
        text = text.replace("\n", "\r\n")
    target.write_bytes(text.encode("utf-8"))
    said.reverse()
    message = (f"rota: restore {'; '.join(s[:60] for s in said)} in {grain}, "
               f"ordered by {act}")
    try:
        sha = worktrees.commit(tree, message, only=(path,))
    except worktrees.WorktreeError as exc:
        target.write_bytes(raw)
        return {"reason": f"the commit failed: {exc}"}
    if sha is None:
        return {"reason": "the restore changed no byte"}
    claim = conn.execute("SELECT claimed_head FROM batches WHERE id = ?",
                         (batch_id,)).fetchone()
    conn.execute("UPDATE batches SET head_commit = ? WHERE id = ?", (sha, batch_id))
    if claim is not None and claim["claimed_head"]:
        conn.execute("UPDATE batches SET claimed_head = NULL WHERE id = ?",
                     (batch_id,))
    # The row at the old head reads closed, and the new head holds no row,
    # so `touch_mistaken` and `mergeable` both drain.
    conn.execute(
        "UPDATE touch_strays SET status = 'restored', "
        "note = COALESCE(note, '') || ? WHERE batch_id = ? AND commit_sha = ? "
        "AND path = ? AND status IN ('open', 'mistake')",
        (f" restored at {sha[:8]} by the structure, ordered by {act}",
         batch_id, row_head or head, grain))
    return {"restored": sha, "statements": said, "path": path}


def _statement_spans(text: str) -> dict[int, int]:
    """Each statement's first base index -> its last base index."""
    out: dict[int, int] = {}
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.stmt):
            first = min([node.lineno] + [d.lineno for d in
                                         getattr(node, "decorator_list", [])])
            out.setdefault(first - 1, (node.end_lineno or node.lineno) - 1)
    return out


def _place(ol: list[str], nl: list[str], i: int, end: int) -> int | str:
    """The head index where fork lines `i`..`end` go back, or a reason.

    The context rule: the nearest fork line before the statement and the
    nearest fork line after it that each stand once in the head, in order.
    A blank line or a repeated line is no anchor."""
    count: dict[str, int] = {}
    for line in nl:
        count[line] = count.get(line, 0) + 1

    def anchor(js) -> int | None:
        for j in js:
            if ol[j].strip() and count.get(ol[j]) == 1:
                return j
        return None

    jb = anchor(range(i - 1, -1, -1))
    ja = anchor(range(end + 1, len(ol)))
    if jb is None or ja is None:
        return "the fork's context around the statement is gone at the head"
    hb, ha = nl.index(ol[jb]), nl.index(ol[ja])
    if hb >= ha:
        return "the fork's context around the statement stands out of order at the head"
    # The head must hold the fork's lines from the before anchor to the
    # after anchor with only the statement gone. A far anchor with changed
    # lines between would put the statement in a place the fork never had.
    before, after = ol[jb:i], ol[end + 1:ja + 1]
    at = hb + len(before)
    if nl[hb:at] != before or nl[at:at + len(after)] != after \
            or at + len(after) - 1 != ha:
        return "the fork's context around the statement changed at the head"
    return at


def restore_wake(conn: sqlite3.Connection, batch_id: str) -> tuple[list, list]:
    """Try the restore of every `mistake` row at the head of `batch_id`.
    Returns (the restores, the reasons). The scheduler sends the wake to
    the Developer only when a reason stands."""
    head = conn.execute("SELECT head_commit FROM batches WHERE id = ?",
                        (batch_id,)).fetchone()
    if head is None or not head["head_commit"]:
        return [], []
    rows = conn.execute(
        "SELECT path FROM touch_strays WHERE batch_id = ? AND commit_sha = ? "
        "AND status = 'mistake' ORDER BY path",
        (batch_id, head["head_commit"])).fetchall()
    done, reasons = [], []
    # Pass 2, open question 2: the first restore moves the head, so each
    # row is marked at the head that holds it.
    for r in rows:
        out = restore_stray(conn, batch_id, r["path"], "the Architect's judgement",
                            row_head=head["head_commit"])
        (done if "restored" in out else reasons).append(
            out if "restored" in out else f"{r['path']}: {out['reason']}")
    return done, reasons


def restore_kept(conn: sqlite3.Connection) -> tuple[list, list]:
    """Restore each statement that his landed keep names on a removal line.

    His keep lands as a `ruled_refs` row with act `keep`, target kind
    `row` and the removal key as its ref (frame 173, pass 2). The tick
    runs this as it runs `restore_wake`, because the ruling lands in
    `principal.land` and a commit belongs to no door. A key whose stray
    row is closed or whose head moved past it restores nothing again."""
    from ..roles.principal import removal_key_parts

    try:
        rows = conn.execute(
            "SELECT rr.ruling_id, rr.ref FROM ruled_refs rr JOIN rulings r "
            "ON r.id = rr.ruling_id WHERE rr.act = 'keep' AND "
            "rr.target_kind = 'row' AND rr.ref LIKE 'removal|%' AND "
            "r.status = 'landed' ORDER BY rr.ruling_id").fetchall()
    except sqlite3.OperationalError:  # a database older than the tables
        return [], []
    done, reasons = [], []
    for r in rows:
        parts = removal_key_parts(r["ref"])
        if parts is None:
            continue
        batch_id, grain, index = parts
        head = conn.execute("SELECT head_commit FROM batches WHERE id = ?",
                            (batch_id,)).fetchone()
        if head is None or not head["head_commit"] or conn.execute(
                "SELECT 1 FROM touch_strays WHERE batch_id = ? AND "
                "commit_sha = ? AND path = ? AND status IN ('open', 'mistake')",
                (batch_id, head["head_commit"], grain)).fetchone() is None:
            continue
        out = restore_stray(conn, batch_id, grain, f"his ruling {r['ruling_id']}",
                            only={index})
        (done if "restored" in out else reasons).append(
            out if "restored" in out else f"{grain}: {out['reason']}")
    return done, reasons
