"""
A batch's runtime state, and the only place that writes it.

`batches.status` is not artefact content. Architect owns what a batch *is* — the
tickets in it, the constraints it touches — and that composition is immutable
once formed. Whether it is running, deferred or merged is something the
scheduler observes about the world, the same kind of fact as a claim or a
checkpoint, and it carries no judgement at all.

Keeping it on the `batches` row is a convenience: it belongs in its own table
alongside `claims` and `checkpoints`, and the reason it is not there yet is that
moving it touches every query in the scheduler for no behavioural gain. What
matters is that it has exactly one writer, which is this module. That is what
law 1 is protecting; the table layout is how the protection is implemented, not
what it is.

None of these transitions produce receipts. A receipt says a role decided
something, and nothing here is decided — starting the next batch is what the
schedule already said, and merging is what a passing verdict already meant.
"""
from __future__ import annotations

import sqlite3

from . import config


def _reindex_main(conn: sqlite3.Connection, batch_id: str) -> None:
    """
    The index describes main again, now that this batch has stopped running.

    Every door out of `running` comes here: merged, abandoned and deferred.
    Between a Developer's commit and that moment the index describes the
    batch's worktree, and after it the worktree is either gone or owned by
    nobody. The refresh also re-pins the partition and stamps the area hashes,
    so a merged change reopens the areas it touched exactly once.

    Best effort. A run with no project root, no git, or no tree on disk still
    changes the batch's status: the transition is a fact about the schedule,
    and the index is a derived view of a checkout this run may not have. The
    reason is recorded, never swallowed silently -- a swallowed one let a
    Developer write on the project's master for 160 steps (tipsP, 2026-09-09).
    """
    from ..onboarding import indexer
    from . import worktrees

    try:
        indexer.refresh(conn, worktrees.project_root(conn), main=True,
                        batch_id=batch_id)
    except Exception as exc:                    # noqa: BLE001 -- best effort
        # Every exception, not a list of two. A parse error, a locked database
        # or a bug in the walk would otherwise escape after `status` already
        # says merged, and the caller would read a delivered batch as a failed
        # transition.
        indexer.note_refresh_failure(conn, batch_id, exc)


def _reindex_batch(conn: sqlite3.Connection, batch_id: str, tree) -> None:
    """The index describes this batch's worktree. Best effort, as above."""
    from ..onboarding import indexer

    try:
        indexer.refresh(conn, tree, main=False, batch_id=batch_id)
    except Exception as exc:                    # noqa: BLE001 -- best effort
        indexer.note_refresh_failure(conn, batch_id, exc)


def start(conn: sqlite3.Connection, batch_id: str) -> None:
    """
    Dispatch. Only reachable through `batch_start`, which already refused if
    anything else was running.

    The worktree is made here, not by the Developer. Law 9 puts every decision
    about a worktree's life outside the role — a role that could create its own
    would be deciding where its work lives, which is a scheduling question
    wearing a tool. A deferred batch keeps the one it had, which is what makes
    resuming it a cold session in surviving work rather than a fresh start.
    """
    from . import worktrees

    conn.execute("UPDATE batches SET status = 'running' WHERE id = ?", (batch_id,))

    # A port range, from the scheduler and not from the batch: two batches must
    # never reach each other's ports and a batch cannot promise that, because it
    # cannot see the other one. Same reasoning that puts the worktree here.
    # Idempotent, so a resumed batch gets back the ports its tests name.
    from . import environments
    environments.reserve(conn, batch_id)

    # A folder with no repository gets one first: the principal's own trial
    # was a plain folder, and a batch there had nowhere to build.
    from . import scaffold
    root_row = conn.execute("SELECT value FROM config WHERE key = 'project_root'").fetchone()
    if root_row and (root_row["value"] or "").strip():
        from pathlib import Path as _Path
        scaffold.ensure_repo(_Path(root_row["value"].strip('"')))

    try:
        worktrees.create(conn, batch_id)
    except worktrees.WorktreeError as exc:
        # No git, or no project root: the batch still runs. Boot reconciles a
        # missing worktree the same way it reconciles a diverged one. The
        # reason is on record, because a swallowed one let a Developer write
        # on the project's master for 160 steps (tipsP, 2026-09-09).
        conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                     (f"worktree:{batch_id}", str(exc)[:300]))
    else:
        # Greenfield gets its floor before anyone works: the pyproject that
        # makes the harness's pytest invocation deterministic and the tests/
        # directory the Tester's paths need. A repository with its own test
        # configuration is left entirely alone.
        scaffold.ensure_floor(conn, batch_id)
        # The batch's own interpreter, with what the project declares. Best
        # effort: a failure is noted and the harness falls back to rota's own
        # interpreter, which is what it always ran.
        from . import provision
        row = conn.execute("SELECT worktree FROM batches WHERE id = ?",
                           (batch_id,)).fetchone()
        if row and row["worktree"]:
            _, note = provision.ensure_env(_Path(row["worktree"]))
            # The install can make a module load that failed before, at the
            # same head (frame 215's review 1b, finding 1).
            from ..roles.api import clear_load_cache
            clear_load_cache(_Path(row["worktree"]))
            conn.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                (f"env:{batch_id}", note))
            # The repository's own tests join the batch. A merge must not
            # break what the tree already proved (tipsY, 2026-09-09).
            from . import harness
            harness.inherit(conn, batch_id, _Path(row["worktree"]))
            # A resumed batch brings its own commits back with it, and the
            # index has described main since it stopped. Without this, the
            # first session of the resumed batch probes for symbols the batch
            # itself already wrote and finds nothing.
            if head_of(conn, batch_id):
                _reindex_batch(conn, batch_id, _Path(row["worktree"]))


def defer(conn: sqlite3.Connection, batch_id: str) -> None:
    """
    Preemption: a higher-priority batch arrived.

    The worktree and its commits survive — commit-first is what bounds the loss,
    because an uncommitted change never existed. The checkpoint does not: a
    deferred batch resumes cold, in the worktree it left behind.

    **The environment goes with the checkpoint, and the ports stay with the
    worktree.** That split is not a new decision; it is this one applied to a
    third thing. What survives a deferral is what cannot be recomputed, and
    everything a running process holds — a seeded database, a warm cache, a
    bound port — is reproducible by starting it again from the worktree. So the
    processes are checkpoint-like and die. The reservation is a number in a row,
    it holds nothing, and keeping it is what makes resuming *continuing*: the
    tests were written against those ports and they are still those ports.
    """
    from . import environments

    conn.execute("UPDATE batches SET status = 'deferred' WHERE id = ?", (batch_id,))
    conn.execute("UPDATE checkpoints SET valid = 0 WHERE batch_id = ?", (batch_id,))
    environments.teardown(conn, batch_id, release_ports=False)
    _reindex_main(conn, batch_id)


def abandon(conn: sqlite3.Connection, batch_id: str) -> None:
    """
    Cancelled by ruling. The other terminal state, and the work did not happen.

    Deferral is a pause and this is not: an abandoned batch is never offered
    again, which is the whole difference -- `batch_start` re-offers deferred
    work the moment it is schedulable, so a batch whose item was revoked
    needed a state that is out of the game rather than waiting in it.

    The worktree stays. A ruling can be appealed, an abandoned diff is
    evidence about what was attempted, and deleting it would make cancelled
    work less inspectable than delivered work. The ports go: abandoned work
    has no further claim on a number in a row.
    """
    from . import environments

    conn.execute("UPDATE batches SET status = 'abandoned' WHERE id = ?",
                 (batch_id,))
    conn.execute("UPDATE checkpoints SET valid = 0 WHERE batch_id = ?",
                 (batch_id,))
    environments.teardown(conn, batch_id, release_ports=True)
    _reindex_main(conn, batch_id)


def merge(conn: sqlite3.Connection, batch_id: str) -> None:
    """
    Delivered. The end of the line for a batch, and the only terminal state that
    means the work happened.

    The worktree goes; the branch stays. Deleting the branch would make a merged
    batch harder to inspect than an abandoned one.

    The environment goes too, and this time so does the reservation: a delivered
    batch has no further claim on a port, and holding one would walk the range
    forward for the lifetime of the project.
    """
    from . import environments, harness, worktrees

    # law 1: one writing role per row; a journal entry has one author
    # The Tester's bodies as they stand, delivered in a commit of their
    # own. The Developer's commits exclude the test paths, so the diff
    # under review is the code; the merge carries the tests the harness
    # last ran, not the version a Developer commit happened to catch
    # (click night 50, 2026-09-14).
    tree = harness.worktree_of(conn, batch_id)
    tests = harness.tests_for(conn, batch_id)
    if tree and tests:
        from pathlib import Path as _Path
        if _Path(tree).is_dir():
            harness.materialise(_Path(tree), tests)
            worktrees.commit(tree, f"rota: tests of {batch_id}")

    # The merge merges. A conflict leaves the batch deferred -- paused, its
    # worktree and commits intact -- rather than marked delivered.
    try:
        worktrees.integrate(conn, batch_id)
    except worktrees.WorktreeError as exc:
        if "not clean" in str(exc):
            conn.execute("UPDATE batches SET status = 'deferred' WHERE id = ?",
                         (batch_id,))
            # The batch has left `running`, so the index must leave its
            # worktree, even though nothing merged. Without this the conflict
            # left every reader on the worktree while main sat at its old head.
            _reindex_main(conn, batch_id)
            raise
        # No git, no branch: the degraded mode the rest of the loop already
        # tolerates -- the batch is still delivered as far as the database
        # can know.
    conn.execute("UPDATE batches SET status = 'merged' WHERE id = ?", (batch_id,))
    # The item's version as delivered. An approval of a later version is
    # new work and slices again; without the record the corrected split sat
    # approved with one spent ticket (tipsAH, 2026-09-09).
    row = conn.execute(
        "SELECT i.id, i.version FROM items i JOIN batches b ON b.item_id = i.id "
        "WHERE b.id = ?", (batch_id,)).fetchone()
    if row is not None:
        conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                     (f"delivered:{row['id']}", str(row["version"])))
    # Night 162's version pages carried 28 open rows of the two merged items,
    # and a drop of them changed a version test (frame 316, pass 2).
    park_merged(conn, batch_id)
    environments.teardown(conn, batch_id, release_ports=True)
    try:
        worktrees.destroy(conn, batch_id)
    except worktrees.WorktreeError:
        pass
    # Last: the worktree the index described is gone, and main now carries the
    # merge. The areas the batch touched reopen once, here, rather than on
    # every commit the batch made.
    _reindex_main(conn, batch_id)


# The account's words for a discard. The next batch-start wake says the
# same words (frame 297).
DISCARDED = "The runner discarded the writes that no commit held: "
# The account's words for a path the discard could not put back.
NOT_PUT_BACK = "The runner could not put back these paths: "


def discard_uncommitted(conn: sqlite3.Connection, batch_id: str,
                        close_notes: bool = True,
                        failed_out: list[str] | None = None) -> list[str]:
    """
    Put the batch's worktree back to its HEAD, and return the paths that
    no commit held. The batch's test files stay, as `_uncommitted` counts
    them. With `close_notes`, the open `drop_notes` rows of those paths
    close, because their lines are back. So does each open note whose
    lines the tree holds (frame 297's review 3, finding 3). `failed_out`
    gets each path git could not put back.

    law 4: an uncommitted change never existed. Ratified 2026-09-16: "A
    session commits or discards before it ends." Night 156's s214 ended
    with its write in bg_2's tree, and s215 inherited the write and its
    note (frame 297).
    """
    import os
    from pathlib import Path

    from . import worktrees

    row = conn.execute("SELECT worktree FROM batches WHERE id = ?",
                       (batch_id,)).fetchone()
    if not (row and row["worktree"]) or not Path(row["worktree"]).is_dir():
        return []
    keep = {r[0].replace(chr(92), "/") for r in conn.execute(
        "SELECT path FROM tests WHERE batch_id = ?", (batch_id,))}
    gone = worktrees.discard(row["worktree"], keep, failed_out)
    if close_notes and gone:
        norm = {p.replace(chr(92), "/") for p in gone}
        for r in conn.execute("SELECT path FROM drop_notes WHERE batch_id = ? "
                              "AND status = 'open'", (batch_id,)).fetchall():
            if os.path.normpath(r["path"]).replace(chr(92), "/") in norm:
                conn.execute("UPDATE drop_notes SET status = 'restored' "
                             "WHERE batch_id = ? AND path = ?", (batch_id, r["path"]))
    if close_notes:
        close_restored_notes(conn, batch_id)
    return gone


def close_restored_notes(conn: sqlite3.Connection, batch_id: str) -> list[str]:
    """
    Close each open `drop_notes` row of the batch whose lines the worktree
    holds, and return its path. The check is the commit door's `_restored`.

    Frame 297's review 3, finding 3: a session wrote the HEAD text back and
    ended. The path was clean, so the discard did not close its note. A
    stale note then refuses the next seat's first note.
    """
    import json
    from pathlib import Path

    from ..roles.api import _restored

    row = conn.execute("SELECT worktree FROM batches WHERE id = ?",
                       (batch_id,)).fetchone()
    if not (row and row["worktree"]) or not Path(row["worktree"]).is_dir():
        return []
    closed = []
    for r in conn.execute("SELECT path, lines, defs, whole, noted FROM drop_notes "
                          "WHERE batch_id = ? AND status = 'open'",
                          (batch_id,)).fetchall():
        try:
            now = (Path(row["worktree"]) / r["path"]).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            now = ""
        entry = {"lines": json.loads(r["lines"]), "defs": json.loads(r["defs"]),
                 "whole": json.loads(r["whole"]), "noted": r["noted"]}
        if _restored(now, entry):
            conn.execute("UPDATE drop_notes SET status = 'restored' "
                         "WHERE batch_id = ? AND path = ?", (batch_id, r["path"]))
            closed.append(r["path"])
    return closed


def discard_lines(gone: list[str], failed: list[str]) -> list[str]:
    """The account's lines for a discard. The paths are a JSON list, so a
    name that holds ", " stays one path (frame 297's review 4, finding 4)."""
    import json

    lines = [DISCARDED + json.dumps(gone, ensure_ascii=False)] if gone else []
    if failed:
        lines.append(NOT_PUT_BACK + json.dumps(failed, ensure_ascii=False))
    return lines


def _last_developer(conn: sqlite3.Connection, batch_id: str) -> str | None:
    last = conn.execute(
        "SELECT id FROM sessions WHERE role = 'developer' AND wake_refs LIKE ? "
        "ORDER BY seq DESC LIMIT 1", (f'%"{batch_id}"%',)).fetchone()
    return last["id"] if last else None


def last_discard(conn: sqlite3.Connection,
                 batch_id: str) -> tuple[list[str], list[str]]:
    """The paths that the last discard of the batch put back, and the paths
    it could not put back. The newest turn of the batch's last Developer
    session that holds a discard line is the record. ([], []) when there
    is none (frame 297)."""
    import json

    sid = _last_developer(conn, batch_id)
    if not sid:
        return [], []
    for (text,) in conn.execute(
            "SELECT completion FROM turns WHERE session_id = ? ORDER BY seq DESC",
            (sid,)):
        found: dict = {}
        for line in (text or "").splitlines():
            line = line.removeprefix("- ")
            for head in (DISCARDED, NOT_PUT_BACK):
                if line.startswith(head):
                    try:
                        paths = json.loads(line[len(head):])
                    except ValueError:
                        paths = []
                    found[head] = [p for p in paths if isinstance(p, str)]
        if found:
            return found.get(DISCARDED, []), found.get(NOT_PUT_BACK, [])
    return [], []


def note_discard(conn: sqlite3.Connection, batch_id: str,
                 lines: list[str]) -> None:
    """Write the discard lines as one more turn of the batch's last Developer
    session. The boot's discard has no session of its own, so the next seat
    reads the record there (frame 297's review 4, finding 3)."""
    from .db import session_note

    sid = _last_developer(conn, batch_id)
    if sid and lines:
        session_note(conn, sid, lines)


def head_of(conn: sqlite3.Connection, batch_id: str) -> str | None:
    row = conn.execute(
        "SELECT head_commit FROM batches WHERE id = ?", (batch_id,)).fetchone()
    return row["head_commit"] if row else None


def record_test_run(conn: sqlite3.Connection, run_id: str, batch_id: str,
                    test_id: str, result: str, attempt: int = 1,
                    commit_sha: str | None = None, output: str = "") -> None:
    """
    One test, one outcome.

    Mechanical, like recording an entry: the harness ran the test and the test
    said what it said. Routing that through a model would introduce a paraphrase
    risk over a boolean.

    The run also goes to `test_run_journal`. The deletes that keep
    `test_runs` live never touch the journal (frame 309).
    """
    row = (run_id, batch_id, test_id,
           commit_sha if commit_sha is not None else head_of(conn, batch_id),
           result, attempt, output)
    conn.execute(
        "INSERT OR REPLACE INTO test_runs "
        "(id, batch_id, test_id, commit_sha, result, attempt, output) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)", row)
    conn.execute(
        "INSERT INTO test_run_journal "
        "(id, batch_id, test_id, commit_sha, result, attempt, output) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)", row)


def next_attempt(conn: sqlite3.Connection, batch_id: str) -> int:
    # Fact F4 leaves this read on `test_runs`: the counter counts every run
    # of the batch, not the newest run of each test.
    row = conn.execute(
        "SELECT COALESCE(MAX(attempt), 0) + 1 AS n FROM test_runs WHERE batch_id = ?",
        (batch_id,)).fetchone()
    return row["n"]


# ---------------------------------------------------------------------------
# The merge gate
# ---------------------------------------------------------------------------

def predicted_rows(conn: sqlite3.Connection, batch_id: str,
                   staged=()) -> list[dict]:
    """
    The batch's predicted touch rows, less the grains his words decline.

    F35: the doors and the seat's working view read the prediction here.
    No other function reads `batch_touch` for them. A grain is declined when
    his newest landed ruling on the batch grants `remove` on the grain. A
    file-qualified symbol is declined also when its file is declined. On
    night 170 the Tester was shown the test paths his words declined, and
    the test-file door refused 12 sends (plans/night170-read.md, W1).

    `staged` is the session's own writes. A door reads them so that it sees
    the rows the session is about to land. The rows come in grain order,
    the landed rows first.

    P4 (ruled R16/R17, 2026-09-03): the page puts the Architect's own rows
    to the principal as a sense check. So `touch_set` does not read this.
    """
    from .runner import disputed_paths

    rows = [dict(r) for r in conn.execute(
        "SELECT grain, grain_kind, confidence FROM batch_touch "
        "WHERE batch_id = ? ORDER BY grain", (batch_id,))]
    rows += [{"grain": w[2].get("grain"), "grain_kind": w[2].get("grain_kind"),
              "confidence": w[2].get("confidence")}
             for w in staged or ()
             if w[0] == "batch_touch" and isinstance(w[2], dict)
             and w[2].get("batch_id") == batch_id and w[2].get("grain")]

    def file_of(row: dict) -> str | None:
        grain = row["grain"]
        if row["grain_kind"] == "path":
            return grain
        if row["grain_kind"] == "symbol" and "::" in grain:
            return grain.split("::", 1)[0]
        return None

    asked = list(dict.fromkeys(
        [r["grain"] for r in rows] + [f for f in map(file_of, rows) if f]))
    gone = set(disputed_paths(conn, batch_id, asked)) if asked else set()
    return [r for r in rows
            if r["grain"] not in gone and file_of(r) not in gone]


def predicted_files(conn: sqlite3.Connection, batch_id: str,
                    staged=()) -> list[str]:
    """
    The files the batch is predicted to touch, less the files his words
    decline: the path grains and the file of each file-qualified symbol.

    A bare symbol names no file, so it gives none. The doors compare a
    diff with this list (F35).
    """
    files = []
    for r in predicted_rows(conn, batch_id, staged):
        if r["grain_kind"] == "path":
            files.append(r["grain"])
        elif r["grain_kind"] == "symbol" and "::" in r["grain"]:
            files.append(r["grain"].split("::", 1)[0])
    return list(dict.fromkeys(files))


def needs_structural_review(conn: sqlite3.Connection, batch_id: str) -> bool:
    """
    Whether there is anything for Architect to check this batch against.

    Stated once, because the gate and the predicate were each deciding it
    separately and disagreed. `structural_review`'s docstring says "a diff whose
    grains intersect constraint bindings" and its query said no such thing: it
    fired for any batch with a passing verdict and no findings. `mergeable`
    then demanded a finding before merging. On a project with no constraints --
    which is every project until Architect has written a model -- those two
    combine into a deadlock, and it is a quiet one, because every part of it
    looks like it is working.

    The batch is finished. Tests pass, the verdict passes. `structural_review`
    fires, Architect is woken, and there is nothing it can legally do:
    `findings.find` requires a `constraint_id` and the column is `NOT NULL
    REFERENCES constraints(id)`, so with no constraints there is no finding to
    record. No finding lands, so the gate still says "no structural review yet",
    so the predicate fires again. The work never merges, and what eventually
    stops it is the livelock guard -- an escalation reporting a role that did
    its job perfectly.

    The rule is the schema's own, quoted from `constraint_bindings`: "a
    constraint with zero bindings is global -- missing bindings must always
    mean *always visible*, never *invisible*." So:

      * no constraints at all -> nothing to review, and nothing to wait for
      * any global constraint -> review, whatever the batch touches
      * otherwise -> review if the batch's touch set meets a binding

    Unknown touch set counts as needing review. Erring toward a review costs one
    session; erring away from it merges a change nobody checked.
    """
    n = conn.execute("SELECT COUNT(*) AS n FROM constraints").fetchone()["n"]
    if not n:
        return False

    globals_ = conn.execute(
        "SELECT COUNT(*) AS n FROM constraints c WHERE c.is_global = 1 "
        "   OR NOT EXISTS (SELECT 1 FROM constraint_bindings b "
        "                  WHERE b.constraint_id = c.id)").fetchone()["n"]
    if globals_:
        return True

    # A path his words decline is not predicted ground, so a binding on it
    # asks for no review (F35).
    touched = {(t["grain"], t["grain_kind"]) for t in predicted_rows(conn, batch_id)}
    if not touched:
        return True                 # nothing predicted; do not assume nothing hit

    return any((b["grain"], b["grain_kind"]) in touched for b in conn.execute(
        "SELECT grain, grain_kind FROM constraint_bindings WHERE resolves = 1"))


def touch_set(conn: sqlite3.Connection, batch_id: str) -> dict:
    """
    One batch's predicted touch, read out for the seat.

    P4 (ruled R16/R17, 2026-09-03): the modification scope is put to the
    principal as a sense check -- never time, never effort -- and it has four
    parts, all of them mechanical. `expected` and `possible` are the
    Architect's own rows (`batches.annotate`: paths always, symbols only where
    confident). `unsurveyed` is the intersection with constraint zero -- the
    register's account of what nobody has read -- taken by path prefix,
    because an area covers the files under it. `commitments` are the other
    constraints bound to a touched grain: exact on the grain, or by the same
    prefix rule for a path. A global constraint is bound to nothing and so is
    everybody's business, not this batch's.
    """
    from ..onboarding.boot import ZERO

    row = conn.execute(
        "SELECT b.id AS id, b.item_id AS item_id, b.status AS status, "
        "       i.text AS item_text FROM batches b "
        "LEFT JOIN items i ON i.id = b.item_id WHERE b.id = ?",
        (batch_id,)).fetchone()
    if row is None:
        return {}
    touch = [dict(t) for t in conn.execute(
        "SELECT grain, grain_kind, confidence FROM batch_touch "
        "WHERE batch_id = ? ORDER BY grain", (batch_id,))]
    paths = [t["grain"] for t in touch if t["grain_kind"] == "path"]

    def under(path: str, area: str) -> bool:
        area = area.rstrip("/")
        return path == area or path.startswith(area + "/")

    unsurveyed = sorted({
        b["grain"] for b in conn.execute(
            "SELECT grain FROM constraint_bindings "
            "WHERE constraint_id = ? AND resolves = 1", (ZERO,))
        if any(under(p, b["grain"]) for p in paths)})

    commitments: list[dict] = []
    for b in conn.execute(
            "SELECT b.constraint_id AS cid, b.grain AS grain, "
            "       b.grain_kind AS kind, c.headline AS headline "
            "FROM constraint_bindings b "
            "JOIN constraints c ON c.id = b.constraint_id "
            "WHERE b.constraint_id != ? AND b.resolves = 1 "
            "ORDER BY b.constraint_id, b.grain", (ZERO,)):
        hit = any(t["grain"] == b["grain"] and t["grain_kind"] == b["kind"]
                  for t in touch)
        if not hit and b["kind"] == "path":
            hit = any(under(p, b["grain"]) for p in paths)
        if hit:
            commitments.append({"id": b["cid"], "headline": b["headline"],
                                "bound_to": b["grain"]})

    return {
        "batch": row["id"], "status": row["status"],
        "item": {"id": row["item_id"], "text": row["item_text"]},
        "expected": [t["grain"] for t in touch if t["confidence"] == "expected"],
        "possible": [t["grain"] for t in touch if t["confidence"] != "expected"],
        "unsurveyed": unsurveyed,
        "commitments": commitments,
    }


def touch_notes(conn: sqlite3.Connection, status: str | None = "open") -> set[str]:
    """
    The presents that are touch notes: a `present` carrying a batch's ref.

    Derived, not declared. A message carries no flag saying which kind of
    present it is, and the one table a touch note's refs name and a signoff's
    never do is `batches`. The gates that ask "is anything open to the
    principal" -- `tick_signoff`, `tick_agenda`, `observed_entries` -- set
    these aside, because a note nobody has to answer (R7: non-blocking) must
    not freeze a gate that waits on a ruling.
    """
    from .db import refs_of

    batches = {r["id"] for r in conn.execute("SELECT id FROM batches")}
    if not batches:
        return set()
    where = "verb = 'present'" + (" AND status = ?" if status else "")
    args = (status,) if status else ()
    return {r["id"] for r in conn.execute(
                f"SELECT id, body_refs FROM messages WHERE {where}", args)
            if batches & set(refs_of(r["body_refs"]))}


# The ledger words that say the change contradicts an owned row (section 2).
HOLDING_KINDS = ("conflict", "scope")
# The tables whose rows belong to one batch through its tickets.
_BATCH_TABLES = ("items", "tickets", "criteria", "tests")


def _batch_rows(conn: sqlite3.Connection, batch_id: str) -> set[str]:
    """The batch, its item, its tickets, their criteria and their tests."""
    rows = {batch_id}
    b = conn.execute("SELECT item_id FROM batches WHERE id = ?",
                     (batch_id,)).fetchone()
    if b and b["item_id"]:
        rows.add(b["item_id"])
    tickets = [r["ticket_id"] for r in conn.execute(
        "SELECT ticket_id FROM batch_tickets WHERE batch_id = ?", (batch_id,))]
    rows.update(tickets)
    crits: list[str] = []
    if tickets:
        marks = ",".join("?" * len(tickets))
        crits = [r["id"] for r in conn.execute(
            f"SELECT id FROM criteria WHERE ticket_id IN ({marks})", tickets)]
    rows.update(crits)
    marks = ",".join("?" * len(crits)) or "NULL"
    rows.update(r["id"] for r in conn.execute(
        f"SELECT id FROM tests WHERE batch_id = ? OR criterion_id IN ({marks})",
        (batch_id, *crits)))
    return rows


def _writer_batches(conn: sqlite3.Connection, ledger_id: str) -> set[str]:
    """The batches of the sessions that wrote a ledger row.

    The route is `receipts` to `sessions.wake_refs` or `checkpoints.batch_id`
    (frame 198's scope, section 4). The park reads the same route."""
    from .db import refs_of

    found: set[str] = set()
    for s in conn.execute(
            "SELECT s.id, s.wake_refs, c.batch_id FROM receipts r "
            "JOIN sessions s ON s.id = r.session_id "
            "LEFT JOIN checkpoints c ON c.session_id = s.id "
            "WHERE r.table_name = 'ledger' AND r.row_id = ?", (ledger_id,)):
        found.update(refs_of(s["wake_refs"]))
        if s["batch_id"]:
            found.add(s["batch_id"])
    return found


def ledger_items(conn: sqlite3.Connection, ledger_id: str) -> set[str]:
    """The items one ledger row is about, for its agenda page and its park.

    The row's `about_ref` names them through `_items_reached`. A test names
    them through its criterion. A row of no item belongs to its writer's
    batch (frame 198's scope, section 4). An empty set means no item and no
    batch, or the account alone."""
    from ..roles.principal import _items_reached
    from .runner import _is_description

    row = conn.execute("SELECT about_ref FROM ledger WHERE id = ?",
                       (ledger_id,)).fetchone()
    if row is None:
        return set()
    ref = row["about_ref"]
    # `_items_reached` has no `tests` lookup. Night 162's l_71e52c9d0a on
    # `tst_c2_version_on` reached no item (frame 316, pass 2).
    test = conn.execute("SELECT criterion_id FROM tests WHERE id = ?",
                        (ref,)).fetchone()
    if test is not None and not test["criterion_id"]:
        # An inherited test has no criterion, so its row reaches no request,
        # not even through its writer's batch (frame 209; frame 316's
        # review 2, finding 4).
        return set()
    if test is not None:
        ref = test["criterion_id"]
    reached = set(_items_reached(conn, ref))
    # The account belongs to no request, so its rows ride on every page, as
    # in `off_page`. The park and the agenda drop it alike (the review of
    # 61a0f41d, finding 2; frame 316's review 2, finding 5).
    items = {i for i in reached if not _is_description(conn, i)}
    if reached:
        return items
    batches = _writer_batches(conn, ledger_id)
    if not batches:
        return set()
    marks = ",".join("?" * len(batches))
    return {r["item_id"] for r in conn.execute(
        f"SELECT item_id FROM batches WHERE id IN ({marks})", tuple(batches))}


def park_merged(conn: sqlite3.Connection, batch_id: str) -> list[str]:
    """Park the open ledger rows of the merged batch's item, and return them.

    A park is not a close: a close writes a decision with no keypress,
    against DECISIONS of 2026-09-03. The parked row leaves every page, and
    the shipped line of `render_state` counts it (frame 204's design,
    section 4, frame 198's option (a))."""
    row = conn.execute("SELECT item_id FROM batches WHERE id = ?",
                       (batch_id,)).fetchone()
    if row is None:
        return []
    item = row["item_id"]
    parked = []
    for r in conn.execute("SELECT id FROM ledger WHERE status = 'open' ORDER BY rowid"
                          ).fetchall():
        # A row that also reaches a live item stays for that item's page.
        items = ledger_items(conn, r["id"])
        if items and items <= {item}:
            parked.append(r["id"])
    # A parked entry leaves every page, so the keys about it lift (frame 242).
    from .db import write_state

    for ledger_id in parked:
        write_state(conn, "ledger", ledger_id,
                    "UPDATE ledger SET status = 'parked' WHERE id = ?", (ledger_id,))
    return parked


def _batch_notes(conn: sqlite3.Connection, batch_id: str,
                 rows: set[str]) -> list[sqlite3.Row]:
    """The open `conflict` and `scope` rows of the batch.

    A row about one of the batch's rows is the batch's. A row about a path,
    an area or any row that reaches no item is the batch of the session that
    wrote it. Night 138's two rows under `tests/test_utils/` reach their
    batch only this way (frame 204's design review, finding 4)."""
    out = []
    marks = ",".join("?" * len(HOLDING_KINDS))
    for r in conn.execute(
            f"SELECT id, about_ref FROM ledger WHERE status = 'open' "
            f"AND kind IN ({marks}) ORDER BY id", HOLDING_KINDS):
        if r["about_ref"] in rows:
            out.append(r)
            continue
        if any(conn.execute(f"SELECT 1 FROM {t} WHERE id = ?",
                            (r["about_ref"],)).fetchone()
               for t in _BATCH_TABLES):
            continue                     # a row of another batch's item
        if batch_id in _writer_batches(conn, r["id"]):
            out.append(r)
    return out


def _next_rungs(conn: sqlite3.Connection) -> dict[str, str]:
    """Each `unresolved` message that a rung still owes, with that rung.

    A question that the triage made `unresolved`, or one whose ladder ran
    out, gets no rung, so nobody owes it a reply (`schema.sql`, messages)."""
    from .predicates import unresolved

    return {w.refs[0]: w.role for w in unresolved(conn) if w.refs}


def waiting_on_a_seat(conn: sqlite3.Connection, batch_id: str) -> str | None:
    """`waiting on <owner>: <ids>` while a seat owes a reply about the batch.

    A message with a verb of `db.OWED_A_REPLY` holds while it is `open`, or
    `unresolved` with a next rung. A `quarantined` message holds nothing:
    nothing moves a message out of it, so the quarantine is the release
    (frame 204's design review, finding 2). A `conflict` or `scope` row holds
    only through such a message about it. A row that no seat was asked about
    waits on a page, and nothing waits on a page after intent (finding 1).
    """
    from .db import OWED_A_REPLY, refs_of

    msgs = conn.execute(
        "SELECT id, to_role, body_refs, status FROM messages "
        f"WHERE verb IN ({','.join('?' * len(OWED_A_REPLY))}) "
        "AND status IN ('open', 'unresolved') ORDER BY seq, id",
        OWED_A_REPLY).fetchall()
    if not msgs:
        return None
    rows = _batch_rows(conn, batch_id)
    notes = _batch_notes(conn, batch_id, rows)
    reach = rows | {n["about_ref"] for n in notes}
    rungs = _next_rungs(conn) if any(
        m["status"] == "unresolved" for m in msgs) else {}

    held: dict[str, list[str]] = {}
    for m in msgs:
        refs = set(refs_of(m["body_refs"]))
        if not refs & reach:
            continue
        owner = m["to_role"] if m["status"] == "open" else rungs.get(m["id"])
        if owner is None:
            continue
        ids = held.setdefault(owner, [])
        ids.append(m["id"])
        ids.extend(n["id"] for n in notes
                   if n["about_ref"] in refs and n["id"] not in ids)
    if not held:
        return None
    return "; ".join(f"waiting on {owner}: {', '.join(ids)}"
                     for owner, ids in held.items())


def _live(conn, col: str) -> str:
    from .scheduler import live_criteria

    return live_criteria(conn, col)


def mergeable(conn: sqlite3.Connection, batch_id: str) -> str | None:
    """
    Why this batch cannot merge, or None if it can.

    Three conditions, and the order is the review order: the harness passed, the
    Critic passed, the Architect found nothing violated. Returning the *reason*
    rather than a boolean is what lets the loop say why a batch is sitting there
    instead of leaving it to be inferred from its absence.
    """
    # Every question is about *this* commit. A verdict against an older diff is
    # not evidence about the one on disk, and treating it as such would merge a
    # change nobody judged — the precise failure the commit stamps exist for.
    head = head_of(conn, batch_id)
    if head is None:
        return "nothing committed"
    # law 8: the merge gate runs harness, then Critic, then Architect
    # Every criterion has its test. The repository's own tests join the
    # batch, so a green harness alone no longer says the Tester has been
    # here: tipsZ (2026-09-09) merged on the inherited test with no test of
    # either criterion.
    # Once the batch has any test. A batch with none never reaches a
    # verdict, since review waits for a test run; the check is for the
    # batch whose only tests are inherited.
    # A test counts for its own batch only. Night 147, walk 2: bg_3 merged
    # on the tests of bg_2, an abandoned batch on the same ticket (frame 239).
    # The check ran on bg_3 only because bg_3 held 37 inherited tests then.
    # `harness.inherit` later moved those rows to bg_4, so the night's
    # database shows bg_3 with no test (frame 239's review, finding 4).
    has_tests = conn.execute(
        "SELECT 1 FROM tests WHERE batch_id = ? LIMIT 1", (batch_id,)).fetchone()
    untested = [r["id"] for r in conn.execute(
        "SELECT c.id FROM batch_tickets bt JOIN criteria c ON c.ticket_id = bt.ticket_id "
        "WHERE bt.batch_id = ? AND NOT EXISTS (SELECT 1 FROM tests t "
        "                                       WHERE t.criterion_id = c.id "
        "                                       AND t.batch_id = bt.batch_id) "
        # A retired criterion owes no test, so it holds no merge (frame 306,
        # pass 1c).
        + _live(conn, "c.retired_by") +
        " ORDER BY c.id", (batch_id,))] if has_tests else []
    if untested:
        return f"criteria without a test: {', '.join(untested)}"

    verdict = conn.execute(
        "SELECT result FROM verdicts WHERE batch_id = ? AND commit_sha = ? "
        "ORDER BY rowid DESC LIMIT 1", (batch_id, head)).fetchone()
    if not verdict:
        return "no verdict"
    if verdict["result"] != "pass":
        return f"verdict {verdict['result']}"

    # law 12: the touch set is a prediction, never a permission; this hold is the stray route, an unexpected change goes to the Architect (ruled: Roman, 2026-10-17, DECISIONS "A write is permitted on any file")
    # The head commit touched ground the prediction never named, and the
    # Architect has not said foreseen or mistake, or said mistake and the
    # Developer has not taken it out. clickI night 32 (2026-09-13):
    # `echo_json` merged in two unpredicted files, unasked.
    strays = conn.execute(
        "SELECT status, GROUP_CONCAT(path, ', ') AS paths FROM touch_strays "
        "WHERE batch_id = ? AND commit_sha = ? AND status IN ('open', 'mistake') "
        "GROUP BY status ORDER BY status", (batch_id, head)).fetchall()
    for s in strays:
        if s["status"] == "open":
            return f"touch strayed, unjudged: {s['paths']}"
        return f"touch strayed, a mistake still in the head commit: {s['paths']}"

    # A red test of a retired criterion holds no merge. He dropped its line
    # (frame 306, pass 2, finding 2).
    from .scheduler import live_tests

    failing = conn.execute(
        "SELECT COUNT(*) AS n FROM latest_runs "
        "WHERE batch_id = ? AND commit_sha = ? AND result != 'pass'"
        + live_tests(conn, "test_id"),
        (batch_id, head)).fetchone()["n"]
    if failing:
        return f"{failing} test(s) not passing"

    reviewed = conn.execute(
        "SELECT COUNT(*) AS n FROM findings WHERE batch_id = ? AND commit_sha = ?",
        (batch_id, head)).fetchone()["n"]
    if not reviewed and needs_structural_review(conn, batch_id):
        return "no structural review yet"

    from ..onboarding.boot import ZERO
    # A finding the Critic dismissed at this commit does not hold the merge.
    # Ruled by Roman on 2026-09-27: only the Critic can reopen a green,
    # signed-off batch, so its dismissal closes the finding at this commit.
    violated = conn.execute(
        "SELECT COUNT(*) AS n FROM findings f WHERE f.batch_id = ? "
        "  AND f.commit_sha = ? AND f.status = 'violated' AND f.constraint_id != ? "
        "  AND NOT EXISTS (SELECT 1 FROM finding_rulings fr "
        "                  WHERE fr.finding_id = f.id AND fr.commit_sha = f.commit_sha "
        "                    AND fr.ruling = 'dismissed')",
        (batch_id, head, ZERO)).fetchone()["n"]
    if violated:
        return f"{violated} constraint(s) violated"

    # A seat still owes an answer about this batch's rows. The merge waits
    # on the seat, never on a page (frame 204's design, section 4; DECISIONS
    # of 2026-09-12, point 2).
    owed = waiting_on_a_seat(conn, batch_id)
    if owed:
        return owed

    if config.get(conn, "merge_gate") == "review":
        return "waiting on the principal's review"

    return None
