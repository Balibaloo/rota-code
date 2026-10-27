# Frame 330, review of pass 5 at 39ce5842

## Verdict

**Sound with one high finding.** The widened check frees the seat on night 169's shape and on all nine other keys. The probes confirm this. The high finding: the Developer rung wakes on a green batch, and its brief says the tests are still red. The cause words never reach any rung prompt, because `tick:exhausted` is not in `DETAIL_SHOWN`. Counts: 6 points answered, 5 findings (1 high, 4 low), 3 probes. The suite: `test_frame330_stopped_bouncing.py` 18 passed. Three neighbour files 61 passed. The `test_scene_*.py` files 1 failed (the known red), 165 passed. I did not run the gate.

## (a) The points

1. CONFIRMED. The Developer rung wakes on `tick:exhausted`, `parked` is true at once, and the seat goes to `batch_2` after the third rung. The Developer's brief is `developer/exhausted.md`, and the brief says "still red".
2. CONFIRMED. On `critic|tick:review` the first rung wakes the Developer on a green batch. The Developer cannot act on a Critic's stuck review. The brief tells it that the tests are red.
3. CONFIRMED for all three deviations. Each deviation is right. Dropping any one of them brings back a known wall.
4. CONFIRMED. The brief lines are false on 9 of the 10 keys. The fix is below, in finding 1.
5. CONFIRMED. No reader of the old words or of `_quarantined_tries` remains. The two remaining "tries" sites are not readers of `stop_detail`.
6. CONFIRMED. Only `test_scene_park.py` and `test_scene_two_batches.py` move a stuck batch, and both use the `tests_failing` key. No scene asserts the old quiet. No scene proves the nine new keys.

### Point 1, night 169

Probe 1 used night 168's fixture with no tests, no head commit, and only `developer|tick:batch_start|batch_1` quarantined. The results:

- `exhausted` returns `("developer", "tick:exhausted", ("batch_1",), "the change could not start after 3 attempts")`.
- `parked("batch_1")` is True at once. `preempt` returns `[]` while a rung is owed, so the batch keeps the seat until the ladder is spent. That is correct, because `next_batch` reads only pending and deferred batches.
- After the Developer is asked, the Architect wakes with the same detail. After all three rungs, `preempt` returns `do:park` with "batch_1: the change could not start after 3 attempts, and its ladder is spent". Then `next_batch` returns `batch_2`.
- The Developer seat wakes in mode `exhausted`. Its user prompt is only "You were woken by: tick:exhausted" and "Refs: batch_1". Its system prompt holds `developer/exhausted.md`, with "still red". The detail is not in either prompt.

### Point 2, the review key

Probe 1 used `critic|tick:review|batch_1` on a green batch. The ladder is Developer, then Architect, then Vision Keeper, then `do:park`. The detail is "the review gave no verdict after 3 attempts", and no prompt shows it. The Developer's tools are `msg.*`, `ledger.log` and loads, and it has no code tool. So the rung can only route a block that does not exist in its lane. The brief offers it four routes: a term, a criterion, a constraint, and a test that does not encode its criterion. None of the four is the cause, which is a Critic that gave no verdict. On a green batch the Developer most likely escalates to the Architect. That costs one session, and Law 6 accepts this cost against silence. `structural_review` is the same, and its detail reads "a step of the team after 3 attempts".

### Point 3, the deviations

- A quarantined `tick:findings_exhausted` key counts as asked. This is right, because `_next_rung` already counts committed sessions of both kinds as one ladder (frame 88). If you drop the rule, a quarantined `developer|tick:findings_exhausted|b` puts the batch in `given_up`, and `exhausted` then wakes the Developer again on `tick:exhausted`. That costs three more sessions under a second key. The keys of the other roles with `findings_exhausted` never occur, so they cost nothing.
- `exhausted` still reads batches with a failing test of any status. This is right. `test_next_batch.py::test_a_preempted_batch_past_its_cap_resumes_exhausted` pins night 93's ladder on a deferred `b_2` at "attempt 11 of 10". If you drop the rule, that test goes red and night 93's silent seat comes back. Frame 87 still holds, because `_running_given_up` returns `[]` for a deferred batch below the cap.
- `parked` keeps the untested-head exit for `tests_failing` only. This is right. `db._lift_quarantines` lifts every key of a running batch on a head commit except `tests_failing` (frame 318). So any other key ends its park by itself. If you drop the early return, a green batch has no failing run at head, and it never parks. That brings back night 169. If you extend the early return to `tests_failing`, an untested fix stays parked for ever (frame 86's pass 2 review).

### Point 4, the rung brief

`rota/roles/prompts/developer/exhausted.md` lines 1, 3 and the last paragraph:

> MODE: exhausted — you have spent the loop on this batch.
> The tests have bounced against the code up to the cap and are still red.
> **Do not spend another attempt on the code.** You have had the budget.

For 9 of 10 keys the tests can be green, and "up to the cap" is false below `loop_cap`. Fix: see finding 1.

### Point 5, deleted or changed words

- `_quarantined_tries`: the grep finds no hit in `rota/` or `tests/`.
- "still fail after" or "N tries": the grep finds hits only in `test_frame330_stopped_bouncing.py` (the new words), `tests/rota/fixtures/status_gates_2026-10-26.json` lines 50 and 54 (status text, not a reader), and the independent "tries" words at `principal.py` 1305, `api.py` 15984, `test_onboarding_phases.py` 2017/2035/2055 and `test_request_page.py` 367. None of these reads `stop_detail`.
- Recorded cases: `tests/rota/cases` has no hit for "still fail after", "could not start after" or "gave no verdict after". The detail never enters a prompt (finding 4), so no cassette key moves.
- The "second table" was only the inline f-string at `scheduler.py` 1767 of the parent commit. The diff removes it, and `TICK_WORDS` is now the one table.

### Point 6, the scenes

The suite ran 12 `test_scene_*.py` files: 1 failed, 165 passed, 5 skipped, 8 xfailed. The one red is `test_scene_two_batches.py::test_a_right_call_lands[the project test tests/test_templates.py as an encode]`, which was red before pass 1. In `test_scene_park.py` 47 to 64, the stuck batch moves through the three rungs, then `do:park`, then `developer|tick:batch_start|b2`. In `test_scene_two_batches.py` 52 and 97, the batch moves through `do:park` before item 2. Both are on the `tests_failing` key. No scene assertion pins the old quiet. The xfails are frames 130 and 134, which are not related. No scene seeds a non-`tests_failing` key on a running batch. So a scene that encodes the old quiet for those keys would have gone red, and none did.

## (b) Findings

1. `rota/roles/prompts/developer/exhausted.md` 1 to 5 and `rota/core/runner.py` 433 to 445. **High.** CONFIRMED. Probe 2 ran a `critic|tick:review` quarantine on a green batch. "still red" is in the system prompt. The detail "the review gave no verdict after 3 attempts" is in neither prompt, because `tick:exhausted` is not in `DETAIL_SHOWN`. The rung acts on a false premise with no cause. Fix: add `tick:exhausted` to `DETAIL_SHOWN`, and replace the brief's second sentence with "The batch stopped. The line under Refs says which budget ran out." Re-record the 3 cases that name `tick:exhausted`: `l1_developer.yaml`, `l1_exhausted.yaml` and `l1_judgement.yaml`.
2. `rota/roles/prompts/vision_keeper/exhausted.md` 9 to 15. **Low.** PLAUSIBLE. On a green batch with a stuck review, the last rung reads "the batch was building the wrong thing". The brief then offers `problem.assert`, which drops the approval of a correct item. No probe ran a model. Fix: the same detail line as finding 1, and one brief sentence: "If the line names a step and not the tests, report it with `msg.report_liaison`".
3. `rota/core/scheduler.py` 1745 to 1751, `_running_given_up`. **Low.** CONFIRMED. Probe 3: a pair key `critic|tick:finding_review|batch_1,f_1` is out of `given_up`. Its Liaison note wake has refs `("batch_1",)`. When that note's own key `liaison|tick:quarantined|batch_1` is quarantined, `given_up` lists it. Then `exhausted` wakes the Developer with "the team could not report a stopped step after 3 attempts", and `parked` is True. A failed report now stops a batch. Fix: filter `_running_given_up` to the keys of seat kinds, or leave out the Liaison's report kinds `tick:quarantined` and `tick:park_ask`.
4. `rota/core/scheduler.py` 1754 to 1760, the `stop_detail` docstring. **Low.** CONFIRMED by probes 1 and 2. The docstring says "the detail reaches a prompt", but it reaches only `sessions.wake_detail`, the cockpit and the night report. The pass 1 status line (fixture line 50) builds its stale-case plan on that claim. Fix: make the claim true through finding 1, or correct the docstring.
5. `rota/roles/principal.py` 1371 to 1385, `TICK_WORDS`. **Low.** CONFIRMED by probe 1. `structural_review` reads "a step of the team after 3 attempts". So do `finding_violated`, `touch_mistaken` and `exhausted`. This is implementer question 2. After finding 1 these words reach a model. Fix: add the four kinds to `TICK_WORDS` in the same commit as finding 1.

Outside the points: findings 3 and 4 are outside the points.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e03f97fc-cdd4-4daa-864c-2ca4d7ef42a5/scratchpad/r5/`. Each probe uses the `night_168` fixture of the test file on a temporary database. No probe touches a `.rota/*.db`.

- `probe1.py`: night 169's shape, `critic|tick:review` and `architect|tick:structural_review`. For each it runs `exhausted`, `parked`, `preempt`, `next_batch`, `tick_batch_start`, and the climb through three rungs to `do:park`. It also checks `DETAIL_SHOWN` and the user prompt from `build_prompt`.
- `probe2.py`: the Developer rung's whole prompt on the review key. It checks "still red" and the detail in the system prompt and in the user prompt.
- `probe3.py`: a pair key alone, then with the Liaison note's quarantined key. It runs `given_up`, `exhausted` and `parked`.
- pytest with `-p no:cacheprovider` and `ROTA_MODEL=qwen3:8b`: `test_frame330_stopped_bouncing.py` 18 passed. `test_next_batch.py`, `test_park_page.py` and `test_frame312_stuck_review.py` 61 passed. The 12 `test_scene_*.py` files: 1 failed (the known red), 165 passed, 5 skipped, 8 xfailed.
- Not run: the gate, and the widened check against the night databases of nights 145, 160 and 165. Those are under the `.rota/` that the brief forbids.

## (d) Usage

This is an estimate, because the harness gave no exact count. About 85k input tokens and about 10k output tokens, so about 95k in total.
