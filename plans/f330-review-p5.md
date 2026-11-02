# Frame 330, review p5: a drained start is not a stall

Commits `8566105b` (pass 5) and `0497f787` (pass 5b) on `21a2380a`, in `C:/Users/roman/rota_f354r`. `git log -1 --oneline` printed `0497f787 test(scheduler): the park key quarantines at the next ready park`.

## Result

Verdict: **stands**. No high and no medium finding.

- Low 1, PLAUSIBLE. The amended frame 86 test proves the quarantine "one park later" only with a hand-made `do:park` wake (`tests/rota/test_next_batch.py:754-755`). No test shows the real park predicate firing again at the cap. The pass 5 report says `spent_park` gives no wake after the commit `f1x`. So the suite proves the rule, but not that the real loop reaches it. Fix: add one test where a fourth park of the same batch becomes ready at the cap through the real predicate. Price: about 30 minutes.
- Low 2, CONFIRMED. A live batch whose key drained at the cap keeps a row at the cap with `quarantined = 0`. While that row exists, `quarantine_overrun` calls `all_wakes` and `quiet_park` on each `frontier` pass, in addition to the call in `quarantine_stalled`. On the dry1w9b copy, one `frontier` pass took 0.071 s, and 0.139 s with the start key of `bg_1` at 3. Fix: none needed now. If the time matters, build the wake list once in `frontier` and pass it to both functions. Price: about 20 minutes, with care for the order that the onboarding wall needs.

## Point 1: the drained start and the ready start

CONFIRMED by `rv5/p1_quarantine.py` on the dry1w9b copy. The cap is 3.

- The probe set `developer|tick:batch_start|bg_1` to 3 attempts, with `bg_1` `deferred`, so the wake is not ready. After `quarantine_overrun`, the row is `(3, 0)`. It is also `(3, 0)` after `quarantine_stalled` and after a whole `frontier` pass.
- Then the probe set `bg_1` to `running` with no head commit. The sessions table holds 3 committed starts, so the start wake is ready. Each of `quarantine_overrun`, `quarantine_stalled` and `frontier` makes the row `(3, 1)`. `quarantine_stalled` drops the wake, and `frontier` does not return it.
- A drained key at the cap is still dropped from the ready list at once. `quarantine_stalled` drops every key at `attempts >= cap`, with the flag or without it (`rota/core/scheduler.py:3013-3016`). So a wake that becomes ready again at the cap never dispatches again. Law 4 holds.

## Point 2: his restart forgets the start count

CONFIRMED by `rv5/p1_quarantine.py`. The probe re-landed `r_m139` through `apply_rulings`, so `m140` is `open`. Then it added a relay and the answer of the Terminologist, and committed a Tester update of `tst_waited`.

- The trigger is the answer, which leads to his ruling. The start key goes from `(2, 0)` to no row, and `next_attempt('bg_1')` is 1.
- No trigger. The start key stays `(2, 0)`, and `next_attempt` stays 11.
- The trigger is `m79`, his reply to an older park page. The start key stays `(2, 0)`, and `next_attempt` stays 11.

The forget runs only under `red_moved and _ruled_park(...)` (`rota/core/db.py:1131-1136`). `forget_keys` also lifts a quarantined start key, as the pass 5 report says.

## Point 3: the readers of `quarantined = 1`

No reader depends on the old rule in a way that breaks. The readers are these:

- `scheduler.quarantined_keys` (`scheduler.py:1901`). It serves `_lift_quarantines`, the pages and the `quarantined` predicate. A drained key at the cap is now not on the list. This is the intended change, and it is the reader that sent m144.
- `loop.step` (`loop.py:341-342`) marks the reported keys. It changes only which keys it can mark.
- `db.lift_keys`, `db.mark_ruled`, `db.forget_keys` and the `spared` read (`db.py:1119-1163`), and the delete at `db.py:1347`. Each one reads the flag of a row. None of them needs a drained key to have the flag.
- `principal._gave_up_tries` and `principal._stuck_ticks` read `quarantined_keys` and then the attempts. For a key that drained at the cap, they print "gave up" and "Stuck" later than before.
- In `quarantine_stalled`, the delete of a key that is no longer produced (`scheduler.py:3010-3011`) did depend on the old rule. Before, it never deleted a key at the cap, because `quarantine_overrun` set the flag on every such key first. Now, a drained key at the cap that names no live batch is deleted. This is how the start key of `bg_1` at 3 leaves after the merge. A key that names a live batch keeps its row, and that row quarantines when its wake is ready again. For a key that names no batch, the same delete already ran at attempts 1 and 2, so the bound always needed a wake that stays ready. The icalendar cycle does not come back, because the delete still never touches a quarantined key.
- `frontier_readonly` (`scheduler.py:1629`) filters on `attempts >= cap` and not on the flag, so it shows the same wakes as before.
- Night 73, the pending-start shape: the starts wrote nothing, so the batch stayed `running` with no head commit and the wake stayed ready. The key still quarantines. This is the ready case of point 1. `test_batch_start_attempt.py` passes.
- Frame 86, the night 93 shape: the park key drains when the batch becomes deferred. It now quarantines at the next ready park and not after the third park. See point 5.
- The scenes in `rota/testkit/scenes.py`, for example S1 and S3 with S4, quarantine keys after sessions that do nothing. The wake stays ready in those sessions, so the change does not affect them. `test_scene_two_batches.py` and `test_scene_park.py` give `74 passed, 1 skipped, 4 xfailed`.

## Point 4: the one-writer pin

CONFIRMED by a search. The only write of `quarantined = 1` in `rota/` is `scheduler.py:2965`, in `_quarantine_live`. The only insert into `tick_attempts` is at `scheduler.py:2801`, and it does not set the flag. The pin in `tests/rota/test_f20_quarantined_keys.py` now names `_quarantine_live` as the writer that serves both functions. The test passes.

## Point 5: the amended frame 86 test

The test still proves the W12 page and the bound, but through a hand-made wake (low 1). `quarantine_overrun(conn) == 0` shows that the park wake of the deferred batch drained. Then the test gives `quarantine_stalled` a `do:park` wake for `b_1`, and the result is `[]`. The page then holds "Stuck: the change was stopped after". That text needs the flag, so the quarantine did happen. The W12 check and the commit after the quarantine are the same as before.

## Point 6: the tests

- The briefed command: `107 passed in 16.18s`.
- The scene files `test_scene_two_batches.py` and `test_scene_park.py`: `74 passed, 1 skipped, 4 xfailed`.
- The files that name night 73, `quarantine_overrun` or `tick_attempt_cap`: `test_batch_start_attempt.py`, `test_frontier.py`, `test_onboarding.py`, `test_predicates.py`, `test_step_failure.py` and `test_frame278_challenge_rounds.py`. Result: `189 passed`.

## Point 7: recorded cases

No recorded case goes stale, by reading (PLAUSIBLE). The changed text is docstrings and comments in `scheduler.py` and `db.py`, and no prompt file changed. Three cases seed `tick_attempts` rows: `l1_liaison2.yaml`, `l1_survey.yaml` and `l1_answers.yaml`. Each seeded row already has `quarantined: 1`, and the change clears no flag. So the rendered prompts stay the same. The gate did not run, as the brief says.

## Probes

The probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/066a0dbd-4073-40a3-ae58-5d6d5157faf7/scratchpad/rv5/`. Each probe opens the dry1w9b copy with `mode=ro` and backs it up into `:memory:`.

- `p1_quarantine.py`: point 1, the drained start and the ready start through `quarantine_overrun`, `quarantine_stalled` and `frontier`. Point 2, the restart with his trigger, with no trigger, and with an older trigger.
- One inline probe listed the `tick_attempts` rows and the batches of the copy.
- One inline probe timed `all_wakes` and `frontier`, with and without a drained key at the cap.

## Usage

Input tokens: about 40k for this review. Output tokens: about 8k. Total: about 48k. These numbers are estimates, because the harness shows no exact count.
