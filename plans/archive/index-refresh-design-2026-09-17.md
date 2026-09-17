# Design record: the code index refreshed after a commit (frame 33, 2026-09-17)

Rota workflow. Written by the assistant (rota-02, session 3b4093c6) from
the scope report `plans/archive/index-refresh-scope-2026-09-17.md`. The
design review reads both pages before any code. Every conclusion carries
a mark.

## The defect

`code.probe` returned nothing for a symbol the batch had committed
(observed: finding 42, `plans/wake-audit.md:71`, click night 46). The
index is built once at onboarding from the main checkout (observed:
scope facts 1 and 5). Nothing after `code.commit` or `lifecycle.merge`
touches it (observed: scope facts 16 to 18). The gap grows by every
merged batch (observed: scope fact 22).

## What the refresh must do

1. Inside a batch, after a Developer session lands a commit, the index
   describes the batch's worktree. `code.probe`, `batches.annotate`,
   `_indexed_like` and the surface vetting then see the batch's own
   symbols and paths (reasoned: these are the readers the scope names
   in facts 7, 8, 11 and 15).
2. After a merge, and after a batch ends without a merge, the index
   describes main at its new head, and `config.project_commit` names
   that head (reasoned: the next batch's Architect and the signoff
   page read main).
3. The freshness rule does not reopen a survey for a batch's own
   commits. It reopens each touched area once, after the merge, as
   `cmd_refresh`'s contract already does (reasoned: one reopen per
   Developer session is churn; the scope's hook B risk).
4. No seat writes the index. The refresh runs in the runner and in the
   lifecycle, never inside a session (ruled: `schema.sql:368-369`, the
   index is rebuilt, never decided).

## The design

### One function

`indexer.refresh(conn, tree, *, main)` in `rota/onboarding/indexer.py`.

- `main=True`: `build(conn, tree)`, `boot.repin`, `config.project_commit`
  from `checkout_of(tree)`, `tick_survey` to reopen the changed areas,
  `orphaned_grain_refs`. This is `cmd_refresh`'s body today (observed:
  `rota/cli.py:665-674`). `cmd_refresh` calls the function.
- `main=False`: `build(conn, tree)`, then restore `area` on every grain
  from the grains the build replaced, by path. A new path takes the area
  of its longest indexed directory prefix. No `repin` and no
  constraint-zero rebind (reasoned: `repin` can move a partition
  mid-batch, scope hook B). No `project_commit` change: the config
  names main's head, and the index names the worktree until the batch
  ends.

### Three hooks

1. **In the batch.** `rota/core/runner.py` after `session_commit`
   (2282), keyed on a `batches` write that carries `head_commit`, the
   pattern `apply_rulings` uses at 2287. Call
   `refresh(conn, worktree_of(batch), main=False)`. One build per
   Developer session that committed, 0.5 to 1.3 s on click (observed:
   scope fact 30). Not inside `code_commit` (reasoned: scope hook A, a
   raw write inside a session on the session's connection, and a dying
   session leaves the index ahead of the rows).
2. **At the merge.** `rota/core/lifecycle.py` in `merge`, after
   `worktrees.integrate` (167) and the status write (176). Call
   `refresh(conn, project_root, main=True)`.
3. **When a batch ends without a merge.** Wherever the lifecycle
   destroys a batch worktree on a cancel or a quarantine, call
   `refresh(conn, project_root, main=True)`, so the index never
   describes a dead worktree. The scope did not locate this path. The
   implementer finds it with `python -m rota.tools.map fn destroy` and
   names it in the report.

### The freshness rule

`scheduler._survey_wakes` (`rota/core/scheduler.py:849-859`) skips the
hash comparison while a batch is running (a `batches` row with status
`running`; only one runs at a time, observed: `loop.py:268-269`). After
the merge the comparison resumes and reopens each touched area once,
through hook 2's `tick_survey`.

Alternative considered: an `area_hashes` table written only by
`main=True` refreshes, read by `area_content_hash`. The observable
behaviour is the same and it costs a schema change (reasoned). Rejected
for this frame. The design review may overturn.

A survey attested mid-batch stamps the worktree's hash (observed: scope
fact 13). After a merge, main carries the same content, so the stamp
holds. After a cancel, main differs, so the area reopens once. That is
honest: the survey described content that never landed (reasoned).

### What does not change

The 75 reader sites keep reading `code_index` and `code_edges`. The
refresh changes what the rows say, not how they are read. `code.source`
keeps its worktree-first read. The duplicate-name door in `code.write`
keeps its tree read (finding 27).

## Pinned tests

1. Onboard a git fixture, start a batch with a worktree, `code.write` a
   new function, `code.commit`, land the session. `code.probe` returns
   `path::name` with `sym_kind='function'`. `principal.near_code` on a
   word of the name lists the file. `batches.annotate` accepts the new
   directory.
2. After `lifecycle.merge`, the same probe from a session with no batch
   returns the symbol, and `config.project_commit` equals main's head.
3. An in-batch commit does not reopen the touched area's survey. The
   merge reopens it once.
4. A batch cancelled after a commit leaves the index at main: the probe
   returns nothing for the symbol.
5. The existing refresh-under-a-running-batch test
   (`tests/rota/test_onboarding.py:1364-1433`) still holds, through the
   shared function.

## The walk

A full night on click from a worktree at the closing commit. The
summary must show, for each Developer session that committed, a probe
after the commit that finds the batch's symbol, and the count of survey
reopens per merge (ruled: the brief, a frame that touches the write
pipeline or a predicate ends on a walk).

## Open for the design review

1. The skip in `_survey_wakes` against the `area_hashes` table.
2. The Architect's `code.source` reads main when no batch is in context
   (`api.py:7399`) while the index describes the worktree mid-batch.
3. Hook 1 in the runner against inside `code_commit`.
4. Where the cancel path is, and whether a quarantine destroys the
   worktree.
5. Whether `frame_repinned` (`scheduler.py:481-484`) holds after a
   `main=True` refresh mid-night.

## Design review, 2026-09-17

A reviewer-type agent, read-only, 78k on the harness line, 34 tool
calls. Eight points and three findings outside them. The assistant's
ruling on each follows the finding (ruled: the assistant, in the smart
zone, 2026-09-17).

1. **The freshness skip is wrong** (observed: the reviewer read
   `tests/rota/test_onboarding.py:1391-1433`, which holds a batch at
   `running` and asserts the edited area reopens; the skip turns that
   test red, and the skip lifts on abandon and defer while the index
   still describes a dead worktree). Ruling: drop the skip. Build the
   `area_hashes(area, hash)` table, stamped by onboarding after
   `areas.pin`, at the end of `boot.repin`, and so by every
   `main=True` refresh. `area_content_hash` reads the table. No
   predicate changes.
2. **Hook 1 holds, with one defect** (observed: `runner.py:2379-2382`
   carries the batch id and `head_commit` in the write; the landing is
   committed before 2282, the connection is autocommit, `build` opens
   its own transaction; a gone worktree makes `walk` return `[]` and
   `build` then empties both tables). Ruling: `refresh` raises when the
   tree is missing or when `walk` is empty for a root with tracked
   files. The runner catches, notes, and keeps the old index.
3. **The area rule needs one correction** (observed: `areas.py:253-272`,
   an area is a directory name or `.`, and tests walk up to an existing
   area at 236-242). Ruling: a new path's area is the longest existing
   area that prefixes its directory after `_untest`, through the same
   walk `_attach_tests` uses. Its symbols take the path's area.
4. **Hook 2 runs last** (observed: `lifecycle.py:172` re-raises a
   conflict before the status write; `tick_survey` at
   `scheduler.py:778-781` writes nothing, the reopen is the hash
   mismatch that `onboarding_phase` evaluates at 729). Ruling: the
   refresh runs after `worktrees.destroy`, and hook 2 does not call
   `tick_survey`. The design states the pause: after every merge the
   run re-enters `survey` until three sessions per touched area close.
   The walk's summary counts those sessions per merge.
5. **Hook 3's path does not exist** (observed: `worktrees.destroy` has
   two callers, `cli.py:333` and `lifecycle.py:188`; `abandon` keeps
   the worktree at `lifecycle.py:123-126`, `defer` at 94-96; a
   quarantine is a `tick_attempts` state). Ruling: hook 3 keys on the
   batch leaving `running`: `refresh(main=True)` in `abandon` and in
   `defer`. On `start` of a batch that resumes with a `head_commit`,
   `refresh(worktree, main=False)`.
6. **Nothing lands a session in the tests** (observed: the touch tests
   read `sb.ctx.writes`, `fixtures.py:736` sets `head_commit` by a raw
   `UPDATE`, and `gitfixture.worktree` places the tree outside `.rota`
   at `gitfixture.py:88`). Ruling: extract `runner.after_landing(conn,
   result)` for `session_commit`, `apply_rulings` and the refresh, and
   move the fixture worktree under `<root>/.rota/worktrees/<id>` so the
   tests walk the production layout.
7. **The readers hold** (observed: `loop._batch_of` hands the one
   running batch to every session that names no other, so the
   Architect's `code.source` reads the worktree too). The three low
   cases, `near_code` after a cancel, the typo door near a new
   callable, a binding to a deleted path, are known and accepted.
8. **`frame_repinned` holds** (observed: `scheduler.py:483-484` returns
   once the flag is 1, `repin` is idempotent).

Outside the points:

- **High. `walk` skips every worktree** (observed: `indexer.py:333`
  tests the absolute path's parts against `SKIP_DIRS`, and `.rota` is
  in the set; the reviewer's probe: `[]` under `.rota/worktrees/b1`,
  one file for the same tree elsewhere). Hook 1 as first designed
  would have emptied the index on the first commit of every night.
  Ruling: `walk` tests `path.relative_to(root).parts`, and `build`
  refuses an empty walk of a root that has tracked files.
- **Low. The survey pause after a merge** (`scheduler.py:729`): stated
  under point 4.
- **Low. The in-batch index never holds the batch's `tests/` paths**,
  which stay untracked until the merge commit (`lifecycle.py:162`), so
  `batches.annotate` refuses a new test directory mid-batch. A known
  gap of `main=False`, not this frame.

The pinned tests grow by three: `walk` under `.rota/worktrees` lists
the files; a missing or empty tree keeps the old index; the stamped
area hash at onboarding equals the live aggregation it replaces.
