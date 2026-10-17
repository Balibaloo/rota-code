# Frame 278, review 2 of 0da2f3d1 (parent 8372fa1c, pass 1 at 5cbef762)

Verdict: the three points hold, and one new high stands outside them. The step offers the decision challenge while that challenge waits open, and the door refuses it as "it waits".

Worktree: C:/Users/roman/rota_r223 at 0da2f3d1. Read-only review on Opus, 2026-10-17.

## (a) Verdict on each point

1. Point 1 holds. The answered decision challenge gets no offer in the refusal or in "after these", in every order and with the reason row.
2. Point 2 holds. The night 153 refs, the test alone, and the two keys that must not match all give the expected step.
3. Point 3 holds. Both texts keep their old bytes, `_after_these` guards on the Developer, and only the three files move.

## (b) Findings

1. `rota/core/sandbox.py:2157` (`_decision_challenge_answered`), used by `rota/core/runner.py:3048`. Severity high. CONFIRMED.
   The Developer sent the decision challenge m150 on `[crit, test, dec]`, and m150 is open with no answer.
   The door refuses a second copy: "it waits for an answer. A second copy is the same question twice".
   On the same rows, `_after_these` says "Send msg.challenge_tester(refs=['ver_opt_show_py', 'tst_ver_opt_show_py', 'dec_1_tst_ver_opt_show_py'], ...)".
   The thread shows m143 answered, so the "after these" key is shown on a `tests_failing` wake in this state.
   This is the class of review 1's high: a step names a call that the door refuses (frame 135's law).
   The predicate reads only `_judged_by(..., "tester")`, so an open prior on the same set does not count.
   The same predicate feeds `_escalation_or_step`, so a refusal on other refs can offer the waiting call too. That path is PLAUSIBLE, not probed.
   Fix: offer the decision challenge only when the door admits it, that is `_same_refs_refusal(ctx, "tester", "challenge", args["refs"])` gives None, without the side effects of an offer.
2. `rota/core/sandbox.py:2157`. Severity low. PLAUSIBLE.
   The predicate is not the door's predicate. The door admits after a receipt on the test (`_moved_since_woken`) and after a Tester answer whose encodes were refused (`_tester_judged`). The predicate withholds the offer in both states.
   This direction breaks no law, because the seat gets `CODE_STEP`. But the seat then misses the decision's route on a new test body.
   Fix: the same fix as finding 1. One predicate for the door and the step removes both gaps.
3. `tests/rota/test_frame278_decision_in_thread.py:142`. Severity low. CONFIRMED by reading.
   The test for review 1's finding 3 replaces m144's refs with `[crit, test, d_dev]` and drops `dec`. So the test passes also when the filter drops every row.
   Fix: keep `dec` beside `d_dev` in m144, and assert that the answer is the `dec` row alone.

## Point 1, the high is closed

Probe q1 builds night 153's rows, the decision challenge m150 with the Tester's answer m151, and the closed escalation m152 on the same refs. Each case runs the real `_same_refs_refusal` and `runner._after_these`.
- A1, sent `[crit, test, dec]`: the door says "they answered (m151) ... Make one real change to the code the test calls." "After these" gives the old code text.
- A2, sent `[dec, test, crit]`: the same two texts.
- A3, m150 stored as `[test, dec, crit]`: the same two texts.
- A4, m150 stored with the Developer reason row `d_r` added: the same two texts. `_without_own_reasons` removes the row before the set compare.
- A5, no closed escalation: the door offers `msg.escalate_architect`, which is a new refs list and admitted. "After these" gives the code text.
No case offers the refused call. B1, the open prior, is finding 1.

## Point 2, the three right cases

Probe q2 runs the real `_escalation_admitted` and `_escalation_or_step`, and `_after_these`.
- C1, night 153, refs `[crit, test]`, decision by the Architect on the test: the escalation is refused, and the step offers the decision challenge on `[crit, test, dec]`. "After these" offers the same call.
- C2, refs `[test, crit]`: the same result.
- C3, refs `[test]` with the escalation admitted: the step offers the decision challenge before the escalation. The new guard `set(mine) <= set(tests)` places it.
- C4, a Developer decision on the red test: "fact. Make one real change to the code the test calls." "After these" gives the old code text.
- C5, an Architect decision on `other_test`: the same two code texts.
- C6, refs `[test]` with a Developer decision: the escalation offer comes back, as before the pass.

## Point 3, the hunk alone

- The code text: `head + " Make one real change ..."` joins to the old three literals byte for byte. The new test asserts the full string, and C4 and C7 print it.
- The offer text: `head + " " + offer[0]` and `f"{fact} {offer[0]}"` give the old f-strings, with one space in each join.
- `_after_these` calls `decision_step` only when `sb.ctx.role == "developer"`. C7, a Tester ctx, gives the code text.
- `git diff --stat 8372fa1c 0da2f3d1` lists `rota/core/runner.py`, `rota/core/sandbox.py` and the test file only. The design record does not move in this commit.
- The thread query adds `a.from_role AS answer_from`, and the filter keeps a row only when its author is the answer's role. No other thread entry changes.
- The test file with `test_desk_guards.py` and `test_end_step_nudge.py` gives 378 passed in 42.85s at 0da2f3d1. I did not run the gate.

## (c) Probes

All probes are under C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b0dce033-321f-4299-b3e0-056d78ea27c8/scratchpad/r278b/.
- `q1.py`: cases A1 to A5 and B1. It runs the real same-refs door and `runner._after_these` on the test file's `_night153` rows.
- `q2.py`: cases C1 to C7. It runs `_escalation_admitted`, `_escalation_or_step` and `_after_these`.
- Pytest at the worktree: the three files above, 378 passed.

## (d) Usage

Input tokens about 45k. Output tokens about 7k. Total about 52k. These are my estimates, and the harness line is the record.
