# Frame 104: a night starts from a snapshot at the seam under test

Design record. Written by d2cc277a on 2026-10-01 after the design read of
`probes/gauntlet_click.sh`, `probes/warm_stamp.py`, `probes/walk.py`,
`rota/core/worktrees.py`, `rota/core/lifecycle.py` and `rota/core/db.py`.
Meta workflow.

## What a seam is

A seam is a run database at the state under test, paired with the commit
the batch's worktree stood at. Night 101's database at its end is the
first pair: one batch `bg_1`, status `running`, head `e1f99723`, the
Critic's fail recorded in `verdicts` (observed: `.rota/clickI_night101.db`,
2026-10-01).

## What stops a warm start from doing this today

- `warm_stamp.relocate` refuses a snapshot that holds a batch, because a
  batch row carries a worktree path (observed: `relocate`, 2026-10-01).
- `restore_click` removes every worktree under `.rota/`, deletes every
  `batch/*` branch and wipes the checkout's `.rota`. The commits survive
  as objects. `e1f99723` is still in the click checkout (observed: `git
  cat-file -t`, 2026-10-01).
- The batch's interpreter is `.venv` inside the worktree, made by
  `provision.ensure_env` at batch start only (observed: `lifecycle.py:120`).
  A recreated worktree has none, and nothing in the loop makes one later.
- `walk.py` posts its second argument as a new principal sentence unless it
  equals the last principal entry. A seam start posts nothing.
- `init_db` refuses a database behind `SCHEMA_MARK` (observed: `db.py:169`,
  the mark is `ledger-kind`). The seam door reuses `schema_stale`.

## The design

One new probe, `probes/seam_start.py`, beside `warm_stamp.py`:

- `pair <db>`: prints the running or deferred batches with their head
  commits, so the launcher command is written from a fact.
- `restore <run> <db> <commit> <click_root>`: the door, then the restore.
  The door refuses, exit 1, when the snapshot is behind the schema mark,
  when no running or deferred batch heads at `<commit>`, or when `<commit>`
  is not an object in `<click_root>`. The restore copies the snapshot to
  `$ROTA_RUNS/<run>.db` by sqlite backup, rewrites `project_root` and each
  batch's `worktree` to `<click_root>/.rota/worktrees/<id>`, clears
  `runtime_processes`, adds the worktree with `git worktree add -b
  batch/<id> <path> <head>` under rota's hooks-off git, runs
  `provision.ensure_env` on it and writes `env:<id>`. One line of output on
  success, `SEAM: ...`.

The launcher reads `GAUNTLET_SEAM_DB` and `GAUNTLET_SEAM_COMMIT`. Both set:
after `restore_click` and the prev backup, it runs the restore, exports
`WALK_FROM_WARM=1` and `WALK_FROM_SEAM=1`, skips onboarding, the fresh
check and the three sentences, and runs one walk with `WALK_PHASE=seam`.
One set and not the other: exit 3 with a sentence.

`walk.py` under `WALK_FROM_SEAM=1` posts no sentence. `WALK_FROM_WARM=1`
already stops the warm snapshot write.

## What the night measures

The time from the launcher's `== seam` line to the first committed session
of the seam walk. The frame's line is fifteen minutes. The night also runs
the loop frame 102 fixed, from the fail that night 101 stopped on.

## Out of scope

A seam snapshot taken mid-night by the walk. The pair is cut by hand from a
night's database for now. A bundle of the commits for a checkout that lacks
them: the door refuses and names the commit.
