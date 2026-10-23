# Probe: the five scene "again" tests, red in the suite and green on the retry

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_g301` at 695e8be7, 2026-10-23.

## Verdict

The five reds are real. `test_run_journal.output` holds pytest's run time, and `scenes.TIMED` does not mask that column, so two builds differ. The gate's retry runs each "again" file alone, and a file alone compares nothing, so the retry is green by construction. Frame 309's commit df6880cf is the cause. Frame 272's `order:` record is not the cause.

## (a) The verdict on each point

1. Each test asserts that its build's rows equal the first build's rows, table by table. The red is `<scene>: the tables that differ between the two builds: ['test_run_journal']`. The five alone at `-n 0` pass 3 of 3. All twelve scene files at `-n 4` go red 2 of 2. CONFIRMED.
2. The cause is a clock. One column, `test_run_journal.output`, differs in the "N passed in 0.0Xs" tail. Config rows and all other tables are equal. CONFIRMED.
3. No. The `config` table is equal between the builds in every scene. A plugin that adds `test_run_journal.output` to `scenes.TIMED` turns all reds of the scene pairs green. CONFIRMED.
4. Since df6880cf, 2026-10-23 18:42, frame 309. The gates that list the five are f7b39946, d6a36081 and 695e8be7. The gate at 8a5b3390 does not list them, and 8a5b3390 does not hold df6880cf. CONFIRMED.

## (b) Findings

1. `rota/testkit/scenes.py:1642`, high, CONFIRMED. `TIMED = {"test_runs.output", "turns.user", "turns.system"}` does not hold `test_run_journal.output`. Commit df6880cf copies each `test_runs` row into `test_run_journal` at `rota/core/lifecycle.py:421` (`record_test_run`), with the same `output`. The probe diff shows, for example, park `tr7`: first `2 passed in 0.02s`, again `2 passed in 0.03s`. Six chains differ: challenged, critic (the review chain), large_module, merged_then_next, park, two_batches. Fix: add `"test_run_journal.output"` to `TIMED` in `rota/testkit/scenes.py`.
2. `tests/rota/scene_tests.py:95` with `rota/tools/gate.py:639`, high, CONFIRMED. `meet` returns "the other build is not done yet" when the first build's file is absent. The gate's `_rerun` runs only the red node ids, so an "again" test never compares on the retry. The `-s` output of the solo runs shows `'the other build is not done yet, and it compares'`. So the gate marks any row difference of a scene as flaky, and every such red hides. Fix: make `_rerun` add the first-build file of each red `_again` file, or make `meet` fail when it compares nothing under the gate.
3. The brief names 8a5b3390 as a gate with the five flaky, low, CONFIRMED. The stack status of 19:09 lists only the handover test as new red at 8a5b3390. The third gate is d6a36081 (stack status 19:46). Fix: none in code. Correct the record.
4. Outside: `test_scene_challenged_again` goes red the same way, low, PLAUSIBLE. The gate does not list it as new, probably because the baseline f9f5cd19 holds it red already (stack 2026-10-16 names it flaky). Fix 1 also turns it green in the probe run.
5. Outside: `test_scene_two_batches.py::test_a_right_call_lands[the project test tests/test_templates.py as an encode]` is red in every probe run, low, PLAUSIBLE as a baseline red. The error is `ledger.log: missing required argument(s) ['kind']`. The gate does not list it as new. Fix: none in this frame.

## The reproduction

The cheapest reproduction is all twelve `tests/rota/test_scene_*.py` at `-n 4`, about 112 s. It went red twice in two runs. The review pair alone at `-n 0` passed once, because the run time matched by chance. The race is a coin flip per journal row between `0.02s` and `0.03s`.

## The rows that differ

Only table `test_run_journal`, column `output`, the pytest run time tail. Keys from probe 4: challenged `tr4`, critic `tr2`, large_module `tr9`, merged_then_next `tr8`, park `tr7`, two_batches `tr7` (first differing row each). Row counts are equal (11, 7, 14, 11, 19, 13).

## The cause with its commit

df6880cf `feat(core): journal every harness run in test_run_journal`, frame 309. The mask in `scenes.TIMED` predates it and was not extended.

## The fix

Add `"test_run_journal.output"` to `TIMED` in `rota/testkit/scenes.py`, which `_clocked` reads.

## (c) Probes

1. Gate output `.../tasks/bv3160f6h.output` read. It holds no failure text for the five, only the L1 red.
2. `pytest tests/rota/test_scene_review.py tests/rota/test_scene_review_again.py -n 0`: 35 passed.
3. `pytest tests/rota/test_scene_*.py -n 4`, twice: 6 and 7 failed, all `test_run_journal`.
4. Same with `--basetemp=<scratchpad>/bt1`, then `<scratchpad>/diffrows.py` on `bt1/scene-rows`: the diff above.
5. The five `_again` files alone at `-n 0 -s`, three times: 5 passed each, `met` shows no compare.
6. Plugin `<scratchpad>/probe_timed.py` (adds the column to `scenes.TIMED`), loaded by `-p probe_timed` at `-n 4`, `--basetemp=<scratchpad>/bt2`: 1 failed (finding 5 only), 165 passed, 14 row files, no diff.
7. `git log -S test_run_journal`, `git merge-base --is-ancestor df6880cf` on the three gated commits, and `grep flaky plans/stack.md`.

`<scratchpad>` is `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/8e879083-89bd-4f17-a62c-8f59f02dd210/scratchpad`.

## (d) Usage

About 30k input tokens and 6k output tokens, about 36k in total. The figures are estimates.
