# Frame 302, review 2: passes 2 and 2b at 5323f8ea

Reviewer on Opus, read-only, in `C:/Users/roman/rota_r302` at 5323f8ea.
Verdict: accept for the branch. The union turns the six red register calls green on the full case fixtures. Two findings are low for the night, and one is a wrong admit that the pass report counts as right.

## (a) The claim, point by point

1. CONFIRMED. All six red calls, replayed through `run_case` on the full case fixtures, now pass every check of their cases. With the union removed, the same six calls fail with the recorded problem text. Nothing else that the cases expect is missing on those runs.
2. The test-file rule admits a test file for an untouched module, a typo of an indexed test file, and a file whose stem is an indexed test directory. It refuses a basename that the index holds in another directory. Of the 8 refusals, all 8 are right. Of the 7 admitted calls, 1 is right, 4 are plausible predictions, and 2 are wrong (finding 1).
3. A file that the principal's words call wrong now lands through `new_files` and writes its row. Before pass 2b it wrote no row through `new_files`. Through `paths` it landed before and lands now, because no door reads `disputed`. No register run put a disputed file in `new_files` (finding 2).
4. CONFIRMED. The directory door refuses a `new_files` entry under an unindexed directory, in `paths` or only in `new_files`, in guess and in annotate.
5. A seat can still put an existing test file in `new_files`. The cost of that shape is now zero, because the union writes the row. The three sentences are clearer than "name as new", but "a new test file" and "new tests in a file" read alike to a small model (finding 3).
6. CONFIRMED. The diff touches 4 files: `rota/roles/api.py`, the two prompts and `tests/rota/test_frame302_unindexed_path.py`. No hunk is outside the door, the two ops, the prompts and the tests. The older test now expects 3 grains, and that is right, because `src/click/options.py` in `new_files` is now a touched path. The test still shows that the symbol's file half meets the door.

## (b) Findings

1. `rota/roles/api.py:6064-6070`, `new_test_file`. Severity: low for the night, low for the frame. CONFIRMED. The rule admits `tests/test_utils.py` when the index holds the directory `tests/test_utils/`. Night 155's s281 and s285 wrote that path. The item says "the utils test file, where the existing echo tests already live", which is `tests/test_utils/test_echo.py`. So the pass report's "7 right new test files" is 5 at most. The same rule admits a typo, `tests/test_termiu.py` beside `tests/test_termui.py`, and `tests/test_bsic.py` beside `tests/test_basic.py` (probe 3). The cost is a wrong row, not a blocked call. Fix: refuse a test-shaped file whose stem is an indexed directory beside it, and list the files of that directory.
2. `rota/roles/api.py:6014-6020` with `rota/core/runner.py:2085-2126`. Severity: low for the night, low for the frame. CONFIRMED by probe 4, PLAUSIBLE as a night risk. A disputed test file in `new_files` now writes a row, and the case fails on `text_excludes`. With the union removed, the same call passes. The new route equals the old `paths` route, because no door reads `disputed`. 81 `new_files` arguments in the register name no disputed file. Fix: none now. If a run shows the shape, refuse in a relay wake a `new_files` entry that the index holds.
3. `rota/roles/prompts/architect/guess.md:7-11`, `annotate.md:21-25`. Severity: low for the night, low for the frame. PLAUSIBLE. The red seats put the existing test file that receives new tests in `new_files`. The old line said "a new file you name as new", and the seat read "new tests" as "new file". The new text keeps the word "new" next to "test file" three times. No recording at the new prompt hash exists, so the effect is unmeasured. The union makes the shape harmless, so the prompt now only affects honesty. Fix: after the re-record, count the runs that name an indexed file in `new_files`.
4. Outside the points. `rota/roles/api.py:6101-6102`. Severity: low. PLAUSIBLE. A refused source path, for example s274's `src/click/options.py`, now ends with "A new test file beside the indexed tests needs no `new_files`". A seat can read that as a route and write a new test file in place of the source file it meant. No recording shows it. Fix: none until a night shows the shape.
5. Outside the points. The green register runs at 15:21 on 2026-10-23, prompt hashes 4925e6c7 and 2a2cafa1, ran on `rota_g301` with frame 302 reverted. Those prompts have no `new_files` sentence, and both cases pass 5 of 5 there. So frame 302's own pass 1b sentence and parameter caused the six reds, and pass 2b repairs a wall that frame 302 built. Severity: low. CONFIRMED by the transcripts. Fix: say this in the frame's status line, so the reader does not count the reds as a model wall.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/1b2c3f89-168f-4708-a241-5ecb0a745d11/scratchpad/r2/`. Each ran from the worktree root with `PYTHONPATH` on the worktree.

1. `p1_replay.py`: reads the 15:16 runs of the two cases from the register copy, read-only. It feeds each run's recorded `TOOL:` lines as scripted replies to `fixtures.run_case` on the case's full fixture, `for_run` filled. Result: 10 of 10 pass, the six reds included. With the argument `control`, the union is replaced by `paths` alone, and the same six fail with the recorded problems.
2. `p2_sweep.py`: the pass sweep, re-pointed at `rota_r302`, with the union applied. It prints each refusal and each admitted unindexed test file with the item text. Result: 104 calls, 8 refusals, 7 calls with admitted test files.
3. `p3_doors.py`: the two doors on a small index. Results: an untouched-module test file lands, a typo lands, `tests/test_utils.py` lands, a basename held elsewhere is refused, a test-shaped file in `src/click/` is refused, `*_test.py` beside the tests lands, and three `new_files` entries under unindexed directories are refused.
4. `p4_disputed.py`: three scripted calls on the two case fixtures, with and without the union. With the union, the disputed files in `new_files` write rows and fail `text_excludes`. Without the union, the same calls pass.
5. A register query: 81 `new_files` arguments in `case_runs`, 0 that name `test_defaults` or `test_options`.
6. `pytest tests/rota/test_frame302_unindexed_path.py -q -n 0`: 31 passed.

No gate and no re-record ran. No tracked file was edited.

## (d) Usage

The harness shows no token count to this agent. The estimate is about 90k input tokens and 12k output tokens, about 102k in total.
