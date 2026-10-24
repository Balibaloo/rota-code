# Frame 318, review 1 of 9dadee0c

Verdict: accept with one fix. The s315 shape holds, and Law 6 still bounds the loop. One defect is confirmed. A second harness run at the same head compares its red with the commit before, not with the run before. So a same-head re-run on an unchanged red lifts the key again.

## (a) Verdict per point

1. Holds. A docstring commit on the same red keeps the key at (3, 1). A red test that passes lifts the key. Both ran green.
2. Holds, with one gap. Every path that records runs calls `_judge_key`. The parked branch is reachable and right per frame 87. The gap is the same-head re-run, finding 1.
3. Holds for the recorded rows. The b5edb9ac docstring commit did not move the first line. The blanking is right in width, but the first line is read from a 2000-character tail, finding 2.
4. Holds. Both changed tests state the rule, not the code. No other test or door depends on the commit reset.
5. Holds. The count climbs to `tick_attempt_cap`, and `quarantine_stalled` sets the quarantine. The predicate's `loop_cap` on the batch attempt is a second bound that no commit resets.
6. Holds. The re-run gives the same counts. "Right" uses the same identity as the code for the first run at a new head. The script does not judge same-head re-runs, which the code does judge.

## (b) Findings

1. `rota/core/db.py:691-708` (`_red`, `lift_on_red_move`) and `rota/core/harness.py:155`. Severity low. CONFIRMED. The probe ran: run at f64fd52, commit, run with a new red (lift), quarantine, run again at the same head with the same red. The key was lifted again (`_key` returned None). The cause: the harness deletes the runs at the head first, and `_red(at_head=False)` reads the newest run at any other commit. Re-runs at one head are common: night 162 b_3 has attempts 7 to 19 at b5edb9ac, and night 161 b_5 has attempts 3 to 13 at a6ed327. Most re-runs follow a moved test, which lifts the key already. A same-body test write deletes the runs with no move (`db.py:625`), and that path now lifts where it did not before (PLAUSIBLE path). Fix: in `harness.run`, read the red at the head before the DELETE, and use it as the baseline when it is not empty.
2. `rota/core/harness.py:227` with `rota/core/db.py:686-692`. Severity low. PLAUSIBLE. The output keeps the last 2000 characters, so `_first_error` reads the first `E ` line of the tail, not of the run. Night 160 shows this: its first lines start with `+    where <built-in method lower ...>`, a continuation line. A length change at the end of the output (the pytest duration) can move the cut across a line boundary. A different first error with the same tail then reads as unmoved, which holds a key that should lift. No recorded row in nights 160 to 162 shows a path, a time, a line number or an id in a first line. Only `0x` addresses appeared, three lines on night 160. Fix: strip the summary line before the cut, or store the first `E ` line at run time before the truncation.
3. Outside. `tests/rota/test_desk_guards.py`: the brief's filter `-k quarantin` selects no test. The changed test matches `-k failing_ticks`, and it passed. Severity low. CONFIRMED by the run ("no tests ran"). Fix: none in code. Use `-k "quarantine or failing_ticks"` in later briefs.
4. Outside. `rota/core/harness.py:111-131`, the no-worktree path. All error rows carry the same text with no `E ` line, so the identity is the empty string. The first such run after a real red lifts the key once. Later runs hold. Severity low. PLAUSIBLE from the code. Fix: none needed now. The path fails toward the old behaviour.

## (c) Probes

- `tests/rota/test_r318_probe.py`, untracked, deleted after. It ran the same-head re-run (finding 1, the assertion that shows the defect passed). It also ran a toy tail cut, which did not change the first line, so finding 2 stays PLAUSIBLE. `git status` was clean after.
- `scratchpad/r318_q.py`: night 162 b_3 runs per attempt with the first `E ` line, from `test_run_journal`, `?mode=ro`.
- `scratchpad/r318_q2.py`: distinct first lines in nights 160 to 162, matched for addresses, paths, times, line numbers and ids.
- `f318_count.py`, re-run on all nights. Hand checks on night 161: b_3 ff776a1 to 9622b3e is right (two reds to all pass at attempt 8). b_5 d51d168 to a6ed327 is wrong (the same five tests and lines at attempts 2 and 3). Night 162 b_3 f64fd52 to b5edb9a is wrong (`assert 1 == 0` at attempts 6 and 7).
- Tests: `test_frame318_quarantine_lift.py` and `test_frontier.py`, 25 passed. `test_desk_guards.py -k quarantin`, 0 selected. `-k "quarantine or failing_ticks"`, 1 passed. `test_desk_guards.py`, `test_frame309_test_run_journal.py`, `test_next_batch.py` and `test_park_page.py` (the map callers), 410 passed.

## (d) Usage

The counter is not visible to this agent. The estimate is about 75k context at the end, about 1.2M cumulative input with the cache, and about 10k output. That is above the 30k cap, mostly because of one long dump of night 162's runs.
