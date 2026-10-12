# Frame 215, review 1c of 5ac87a07

Reviewer: read-only agent on Opus, worktree `C:/Users/roman/rota_rv215c` at
5ac87a07, 2026-10-12. Verdict: the pass stands. Highs: 0. Lows: 2.

## (a) Verdicts on the points

1. Holds. `clear_load_cache` drops the keys of one worktree only. `lifecycle.start` calls it after `ensure_env` on the resume path. A fresh `import rota.core.lifecycle` loads with no cycle, and it does not load `rota.roles.api`.
2. Holds. Entry `e_p4`, statement `s4` and the item's `refs` row match `n142.db` field for field. The item text, the ticket text and `_N142_TEXT` do not name `process_commands`.
3. Holds in part. The cache test is red at 0a554207 and green at 5ac87a07. The statement test is green at 0a554207, because the door read statements before this pass. A mutation of the door's statement read makes it red, so the test guards the source.
4. Holds. The four new reds are the four known reds of other frames. The diff touches no door that those four cases call, as section (b) note 3 says.
5. Holds. The diff adds a comment, a private function with a docstring and two tests. No op, door text, brief or case file changes. The pass's gate printed "stale (0): none".
6. Holds. The new cache test holds three intact escapes for a new line in its bytes literals. No file of the commit holds a CR byte.

## (b) Findings

1. `tests/rota/test_criteria_surface.py:472-495`. Severity low. CONFIRMED by reading.
   The cache test calls `clear_load_cache` directly. No test runs `lifecycle.start`, so a removed call at `rota/core/lifecycle.py:123-124` stays green.
   The pass report says the same thing in its open question 2.
   Fix: add one test that runs `lifecycle.start` on a deferred batch with a cached failure and asserts the key is gone.
2. `rota/roles/api.py:11524`, `clear_load_cache`. Severity low. CONFIRMED for the mechanism, PLAUSIBLE for a night.
   The function compares `str(worktree)` with the key's root. The key's root is `str(Path(row["worktree"]))`, so Windows separators are normalized there.
   Probe c1: a key under `C:/a` survived `clear_load_cache(Path("C:/a"))`, because `str(Path("C:/a"))` is the form with backslashes.
   The one caller passes `_Path(row["worktree"])`, the same form `_worktree_of` builds. So no current path misses.
   Fix: compare `str(Path(worktree))` in `clear_load_cache`, so a string argument and a Path argument clear the same keys.

Notes, not findings:

3. Point 4 from the diff. `test_a_session_with_no_batch_reads_the_root` runs no batch, so it never reaches `lifecycle.start`. The two-batch scene fails on "ledger.log: missing required argument(s) ['kind']", an argument check this diff does not touch. The two `L1-AR` cases are Architect seat replays, and the diff changes no Architect door or brief. A clear of the cache costs one more probe and gives the same result in the same environment. Timeouts are not cached either way.
4. The resume path reaches the call. `worktrees.create` returns the old worktree for a deferred batch, so `start` enters its `else` branch, and `ensure_env` runs before the clear. The scheduler's resume wake at `rota/core/scheduler.py:462` has the kind `tick:batch_start`. `loop.step` calls `lifecycle.start` for that kind in the same process as `run_session`.
5. The 12:06 status of frame 215 in `plans/stack.md` says "the same four known to other frames" and does not list the four. The four names match the known reds in frame 204's statuses of 02:50 and 03:11 and in frame 200's status of 15:19.

Outside the points: nothing above low in the three files.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d609cf11-e3b0-446b-b02a-29ab3633c919/scratchpad/rv215c/`, or ran as `python -c` from the worktree.

- Point 1, import: `python -c "import rota.core.lifecycle"` in a fresh interpreter printed "lifecycle ok False". The second value is `'rota.roles.api' in sys.modules`.
- Point 1, probe c1: four keys seeded, `('C:/a',h,m,1)`, `('C:/a',h2,n,2)`, `('C:/ab',h,m,1)` and a key under `str(Path('C:/a/b'))`. `clear_load_cache(Path('C:/a'))` dropped none of them. `clear_load_cache('C:/a')` then dropped the two `C:/a` keys and kept `C:/ab` and `C:/a/b`. So the scope is exact by string, and the prefix `C:/ab` does not match.
- Point 2: `n142.db`, copied from review 1's scratchpad, opened read-only.
  - `s4`: span_entry `e_p4`, span 0 to 94, status `ratified`, version 1, text "Give version_option a show_python flag that appends the running Python version to the message." The seed is the same.
  - `e_p4`: author `principal`, ts_order 83, version 1, the same text. The seed is the same.
  - `refs`: `('items','show_python_version_flag','statement','s4',1)` is in the night. The night also holds three more links to `s4`, from items `how_it_works` and `executes_commands` and from glossary term `show_python`. The door reads only the item's link, so the seed omits them correctly.
- Point 3, `old/`: `git archive 0a554207` of `rota` and `pyproject.toml`, with `tests` from 5ac87a07, run with `PYTHONPATH` on `old/`. Result: 1 failed, 35 passed. The failure is the cache test, "AttributeError: module 'rota.roles.api' has no attribute 'clear_load_cache'". The statement test passed.
- Point 3, `mut/`: `git archive 5ac87a07` of `rota`, `tests` and `pyproject.toml`. The statement query at `rota/roles/api.py:4446` was changed to `AND 0`. Result: 1 failed, 35 passed. The failure is the statement test, a Wall at `api.py:4467`.
- Point 3, the commit: the test file in the worktree gave 36 passed in 10.77 s.
- Point 5: `map fn clear_load_cache` names one caller, `lifecycle.start`. `rota/core/sandbox.py` does not name the function. The diff has no hunk under `rota/roles/briefs`, `tests/rota/cases` or a door function.
- Point 6: a byte read of `git show 5ac87a07` and of the three files at 5ac87a07 found 0 CR bytes. The cache test holds the backslash only in the two expected `write_bytes` lines.

## (d) Usage

The reviewer cannot read the harness line. Estimate: about 33k input tokens, about 7k output tokens, about 40k total, at the 40k cap.
Take the real figures from the harness line.
