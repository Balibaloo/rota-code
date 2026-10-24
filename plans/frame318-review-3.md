# Frame 318, review 3: passes 3 and 3b at d4a60ad9

Verdict: the code stands. The night 164 claim does not stand. The rules in the report's table hold on the fixture shapes, and the 11 new tests pass. On the night database, two of the five events keep the key, not four. Both head resets, s229 and s233, still lift.

## (a) The points

1. Rule table: every row maps to a line and a passing test. Rows 1 to 5 decide at `db.py:626` (`_moves_red` before the body deletion at 632) and `db.py:727`. Rows 6 to 8 decide at `db.py:803` and `806`. Row 9 is `db.py:637`, unchanged. Stands.
2. Night 164 after the change: s228 keeps at the move, then lifts at attempt 5 (`same_head`, new red). s229 lifts. s233 lifts. s244 keeps. s252 keeps. Findings 1 and 2.
3. The right lifts stand: a cure (`db.py:813`), a re-encode of the red test (`_moves_red` reads the red before line 632 deletes the runs), a retire or respecify of the red criterion (the LEFT JOIN at 690), a new red test at the same head (806), and `verdict_failed` on a criteria move (729). Each has a passing test in `test_frame318_red_move_lift.py`.
4. `same_head` comes from `harness.py:169` only, and `harness.py:182` passes it. First run of a batch: no run at the head, so False, and `before` is empty, so no lift. Head moved twice between runs: False, and `before` is the newest run per test at the older head, so the normal compare holds. Parked batch: the commit lifts at `db.py:637` while parked, and the resume run has `same_head` False. Stands.
5. Confirmed. At 7b8a5f27, exported to the scratchpad, `test_a_right_call_lands[the project test tests/test_templates.py as an encode]` fails: 1 failed, 42 passed. At d4a60ad9 the seven files give 105 passed, 1 failed, 2 skipped, 5 xfailed. The red is the same test.
6. `casestatus`: 0 stale, 0 failing, 166 never measured.

## (b) Findings

1. HIGH, CONFIRMED. `rota/core/db.py:803`. s229's reset persists. The night shape is {shorten, docstring_example} at e9bb to {shorten, 4 inherited} at 63c65435, not {R} to {R, 4}. s228's test `tst_format_filename_docstring_example` failed at attempt 5 and passed at attempt 6, so one red of `before` is gone and the key lifts. The probe shows `lift True`. The report's "4 of 5 right" and the fixture of `test_a_head_that_grows_the_red_keeps_the_quarantine` do not match the night. Fix: store the red set in the quarantine row, and lift a head run only when one of those tests passes.
2. MEDIUM, CONFIRMED. `tests/rota/test_frame318_red_move_lift.py:5-9` and the report. s228 added a red test, not a passing one: the journal shows `fail` at attempt 5 at the same head e9bb. Under pass 3b the harness lifts the key at attempt 5. That lift is the rule's intent, so the code is right, and the report's count is wrong. Fix: correct the docstring and the report, and give the s228 test a red new test at the same head.
3. HIGH, CONFIRMED, outside the points, present at 7b8a5f27 too. `rota/core/db.py:776-779`. `red_before` reads the runs of every test, and `harness.run` runs live tests only. After a retire of the red criterion, the red test keeps an older run, so `before` holds it and `now` never does. Every later harness run at any head lifts `tests_failing`: the probe shows three runs, three lifts. The quarantine is void for the rest of the batch. Fix: read `red_before` and `now` through the live-test condition, or delete the retired criterion's runs at the retire.
4. LOW, PLAUSIBLE. `rota/core/harness.py:137-141`. The no-worktree branch records `error` rows at the head, so a later real run at that head reads `same_head` True and `before` as those rows. A real failure has another first error line, so the pair is gone and the key lifts. Fix: skip the lift when every run of `before` is the no-worktree error.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/48122667-6b95-4100-a43b-30ec9c6540dd/scratchpad/f318_probe_night164.py`: replays the five events through `session_commit`, `red_before` and `lift_on_red_move` with the harness order, then a retire with three runs.
- `D:/repos/rota/.rota/clickI_night164.db` read `?mode=ro`: `test_run_journal` per attempt, the red rows, `receipts` of s228, s229, s233, s244, s252.
- pytest on the seven files at d4a60ad9, and on `test_scene_two_batches.py -k test_a_right_call_lands` at 7b8a5f27 in `scratchpad/base7b8a` (git archive, no checkout).
- `python -m rota.tools.casestatus` from the worktree root.

## (d) Usage

About 330k input tokens across the turns, about 9k output tokens, about 340k total, estimated.
