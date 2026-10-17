# Frame 220, review 2 of pass 1b

Worktree `C:/Users/roman/rota_r283old` at d2ffdfe3, against 21f0e7b0. Reviewer: Opus agent, 2026-10-17. Read-only. The verdict: pass 1b stands, with two lows and one outside low.

## (a) Verdicts

1. The wider except lands no commit that the parent refused. CONFIRMED. It now swallows programming errors in `_batch_base` with no trace (finding 1, low).
2. Both callers now reach one path form inside `_base_text`. CONFIRMED. The fence passes a forward-slash `wpath` with root `_batch_worktree`. `_base_held` passes the raw `path` with root `_worktree_of`. The two roots are equal at that point.
3. The merge-base test fails when the route is HEAD~1. CONFIRMED by a mutation in an exported copy.

## (b) Findings

1. `rota/roles/api.py:16212`, low, PLAUSIBLE. `except Exception` swallows any `TypeError`, `AttributeError` or `NameError` raised inside `_batch_base`. A future bug there then fails silently on every write. The fence loses the base baseline and refuses base restores again (night 143's wall). `_base_held` returns True and holds every commit that drops a line. Nothing logs the cause. Fix: catch `(OSError, sqlite3.Error, _wt.WorktreeError)` only.
2. `rota/roles/api.py:15553`, low, CONFIRMED. The pass changes frame 283's commit door, and no test covers the change. With an absolute path, `_base_held` gave False at the parent and gives True at HEAD. The door now holds a commit it let through before. The direction is correct (it refuses more). Before, a database error in `_batch_base` raised out of `code.write`. Now the door holds the commit. Frame 283's three files stay 74 passed at both commits, so no case renders either path. Fix: add one `_base_held` case with an absolute path to `tests/rota/test_frame140_commit_beside_note.py`.
3. Outside. `rota/roles/api.py:16205` and `16211`, low, CONFIRMED, present at the parent too. A path with `..`, for example `pkg/../decorators.py`, passes `_within`. Then `git show fork:pkg/../decorators.py` reads `..` as a range and returns a commit log with exit 0. `_base_text` returns that log as the file text. The fence then skips a SyntaxError baseline, and `_base_held` holds every line. Both fail closed. Fix: normalise `rel` with `posixpath.normpath` and read the blob with `git cat-file blob`.
4. Outside, low, PLAUSIBLE. `_P(rel).resolve()` at line 16200 sits outside the `try`, and it catches `ValueError` only. An `OSError` from `resolve` on an odd absolute path now raises out of every fence write. Fix: move the normalisation inside the `try`.

## Point detail

- Point 1. At HEAD, a `_batch_base` that raises `sqlite3.OperationalError` gives `_base_held` True (the commit is held). At the parent, the same error raised out of the call. So the widened except converts a crash into a hold, and never into a landed commit.
- Point 2. `_base_text` now strips backslashes and makes an absolute path relative to the root. A backslash path from `_base_held` likely gave "" at the parent (reasoned, not probed). Now it reads the base. The roots agree, because `_batch_worktree` at line 14114 already succeeded for the write.
- Point 3. With `fork = "HEAD~1"` in `_base_text`, `test_the_base_of_a_batch_of_two_commits_is_its_fork_not_head_1` fails with the fence refusal "reaches the dynamic at line 1". The other two new tests pass under the mutation. At the parent, the merge-base test passes, and the other two new tests fail. Each test pins its own fix.

## (c) Probes

All probes ran in copies under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0162323a-8602-4856-80d2-0fa70223b3b2/scratchpad/f220r2/`, exported with `git archive`.

1. Frame 283's files (`test_frame140_commit_beside_note.py`, `test_revert_door.py`, `test_seam_start.py`): 74 passed in the worktree at HEAD, 74 passed in `par` (21f0e7b0). The imports resolve to each tree's own `rota`.
2. `mut` (HEAD with `fork = "HEAD~1"`): the three new tests gave 1 failed (the merge-base test) and 2 passed.
3. `par` with HEAD's `test_desk_guards.py`: the merge-base test passed. The cannot-be-named test and the absolute-path test failed.
4. `probe/test_p1.py`, copied to `head` and `par` as `tests/rota/zz_probe_p1.py`, run with `-n0 -s`. HEAD: rel True, abs True, dotdot "commit d63db98...", broken True. Parent: rel True, abs False, dotdot "commit d63db98...", broken raised `sqlite3.OperationalError`.
5. The probe file was copied into the worktree once by error, and was removed before any run. `git status` then showed only `tests/rota/test_r4_new.py` untracked, which predates this review.

## (d) Usage

Input about 70k tokens, output about 9k tokens, total about 79k. The estimate is the agent's own. Read the harness line for the true count.

Stands.
