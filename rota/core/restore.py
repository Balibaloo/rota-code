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
                  act: str, *, only: set[int] | None = None) -> dict:
    """Put back each fork statement of `grain` that the head lacks, and
    commit. `act` names who ordered the restore: his ruling id or the
    Architect's judgement. Returns {"restored": sha, "statements": [...]}
    or {"reason": one sentence}. A reason changes nothing. `only` names the
    base indexes to put back, as his keep names one statement."""
    out = restore_head(conn, batch_id, [(grain, only, act)])
    return out["rows"][0] if "rows" in out else {"reason": out["reason"]}


def restore_head(conn: sqlite3.Connection, batch_id: str,
                 asks: list[tuple[str, set[int] | None, str]]) -> dict:
    """Put back the statements of every ask at the head in one commit, or
    put back none. An ask is (grain, `only`, act).

    Review p1 of frame 173, high 2: a partial restore moved the head, and
    the unrestored `mistake` row stayed on the old head. `touch_mistaken`
    then woke nobody and the stray gate opened. Returns {"restored": sha,
    "rows": [...]} or {"reason": one sentence, "grain": the ask that
    failed}. A reason changes nothing."""
    from . import harness, worktrees
    from ..roles.api import _base_texts, removed_statements

    row = conn.execute("SELECT head_commit FROM batches WHERE id = ?",
                       (batch_id,)).fetchone()
    tree = harness.worktree_of(conn, batch_id)
    first = asks[0][0] if asks else ""
    if row is None or not row["head_commit"] or not tree or not Path(tree).is_dir():
        return {"reason": f"{batch_id} has no worktree and head to restore in",
                "grain": first}
    head = row["head_commit"]
    try:
        root = worktrees.project_root(conn)
    except worktrees.WorktreeError:
        root = None
    try:
        fork = worktrees.base(tree, root)
    except worktrees.WorktreeError:
        return {"reason": "git cannot name the fork of the batch", "grain": first}
    # A restore commits its own paths only, and a tracked change in the
    # tree could be in those paths. So the restore waits for a tree that
    # holds only committed work (law 1: the structure writes no seat's change).
    furniture = set(worktrees.batch_furniture(conn, batch_id))
    dirty = [p for p in subprocess.run(
        [*worktrees.GIT, "-C", str(tree), "status", "--porcelain", "-z",
         "--untracked-files=no", "--", ".", ":(exclude).venv", ":(exclude).rota"],
        capture_output=True).stdout.decode("utf-8", "replace").split("\0")
        if p and p[3:] not in furniture]
    if dirty:
        return {"reason": "the worktree holds uncommitted changes", "grain": first}
    # Each file's text moves in memory through every ask. A file reaches
    # the disk only when every ask has its place.
    raws: dict[str, bytes] = {}
    nows: dict[str, list[str]] = {}
    rows: list[dict] = []
    for grain, only, act in asks:
        path, _sep, owner = grain.partition("::")
        base = _base_texts(tree, fork, [path]).get(path)
        if not base:
            return {"reason": f"the fork does not hold {path}", "grain": grain}
        target = Path(tree) / path
        if path not in raws:
            if not target.is_file():
                return {"reason": f"{path} is gone at the head", "grain": grain}
            raws[path] = target.read_bytes()
            nows[path] = raws[path].decode("utf-8", "replace").replace(
                "\r\n", "\n").splitlines(keepends=True)
        got = removed_statements(base, "".join(nows[path]))
        if got is False:
            return {"reason": f"{path} does not parse at the fork or at the head",
                    "grain": grain}
        lost = sorted({i for o, i in got[0] if (not owner or o == owner)
                       and (only is None or i in only)})
        if not lost:
            return {"reason": f"the head holds every statement of {grain}",
                    "grain": grain}
        ol = base.splitlines(keepends=True)
        nl = list(nows[path])
        spans = _statement_spans(base)
        said: list[str] = []
        # The last statement first, so an insert does not move the next place.
        for i in sorted(lost, reverse=True):
            end = spans.get(i, i)
            at = _place(ol, nl, i, end)
            if isinstance(at, str):
                return {"reason": at, "grain": grain}
            nl[at:at] = ol[i:end + 1]
            said.append(ol[i].strip())
        nows[path] = nl
        said.reverse()
        rows.append({"statements": said, "path": path, "grain": grain, "act": act})
    for path, raw in raws.items():
        text = "".join(nows[path])
        if b"\r\n" in raw:
            text = text.replace("\n", "\r\n")
        (Path(tree) / path).write_bytes(text.encode("utf-8"))
    acts = list(dict.fromkeys(r["act"] for r in rows))
    message = ("rota: restore " + "; ".join(
        f"{'; '.join(s[:60] for s in r['statements'])} in {r['grain']}" for r in rows)
        + f", ordered by {' and '.join(acts)}")
    try:
        sha = worktrees.commit(tree, message, only=tuple(raws))
    except worktrees.WorktreeError as exc:
        for path, raw in raws.items():
            (Path(tree) / path).write_bytes(raw)
        return {"reason": f"the commit failed: {exc}", "grain": first}
    if sha is None:
        return {"reason": "the restore changed no byte", "grain": first}
    claim = conn.execute("SELECT claimed_head FROM batches WHERE id = ?",
                         (batch_id,)).fetchone()
    conn.execute("UPDATE batches SET head_commit = ? WHERE id = ?", (sha, batch_id))
    if claim is not None and claim["claimed_head"]:
        conn.execute("UPDATE batches SET claimed_head = NULL WHERE id = ?",
                     (batch_id,))
    # Every row at the old head reads closed, and the new head holds no row,
    # so `touch_mistaken` and `mergeable` both drain.
    for r in rows:
        conn.execute(
            "UPDATE touch_strays SET status = 'restored', "
            "note = COALESCE(note, '') || ? WHERE batch_id = ? AND commit_sha = ? "
            "AND path = ? AND status IN ('open', 'mistake')",
            (f" restored at {sha[:8]} by the structure, ordered by {r['act']}",
             batch_id, head, r["grain"]))
        r["restored"] = sha
    return {"restored": sha, "rows": rows}


# The note prefix of a row that the structure could not put back. The tick
# does not try the row again until its note changes (frame 173 review p2,
# high 2).
FAILED = "restore: "


def _note_failed(conn: sqlite3.Connection, batch_id: str, head: str,
                 grain: str, reason: str) -> None:
    """Write "restore: <reason>" on the stray row once, and read the row as
    a `mistake`, so `touch_mistaken` wakes the Developer with the reason."""
    conn.execute(
        "UPDATE touch_strays SET status = 'mistake', note = "
        "CASE WHEN COALESCE(note, '') = '' THEN ? ELSE note || ' ' || ? END "
        "WHERE batch_id = ? AND commit_sha = ? AND path = ? "
        "AND status IN ('open', 'mistake') AND COALESCE(note, '') NOT LIKE ?",
        (FAILED + reason, FAILED + reason, batch_id, head, grain,
         f"%{FAILED}%"))


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
    the Developer only when a reason stands. All rows go back in one
    commit, or none goes back, and the row that failed holds the reason."""
    head = conn.execute("SELECT head_commit FROM batches WHERE id = ?",
                        (batch_id,)).fetchone()
    if head is None or not head["head_commit"]:
        return [], []
    rows = conn.execute(
        "SELECT path FROM touch_strays WHERE batch_id = ? AND commit_sha = ? "
        "AND status = 'mistake' ORDER BY path",
        (batch_id, head["head_commit"])).fetchall()
    if not rows:
        return [], []
    out = restore_head(conn, batch_id, [(r["path"], None, "the Architect's judgement")
                                        for r in rows])
    if "rows" in out:
        return out["rows"], []
    _note_failed(conn, batch_id, head["head_commit"], out["grain"], out["reason"])
    return [], [f"{out['grain']}: {out['reason']}"]


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
