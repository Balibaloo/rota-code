# Frame 308, review 3: pass 2b at e7cf6426

Reviewer on Opus, read-only, worktree `C:/Users/roman/rota_r308` at e7cf6426, parent 541bb828.

The verdict: do not accept as it stands. The landed-write key closes F1, F2 and F3 of review 2. But `ruling_asks_no_new_words` reads three rulings that ask for new words as "no new words". With the rulings as they stood at each wake, the door now admits s370 and s250 with the old text. The count is 8 refused and 7 admitted, not 11 and 4.

## (a) The claim, point by point

1. Point 1, F1 to F3: CONFIRMED closed. Each shape is refused, and the text names the respecify step.
2. Point 2, `ruling_asks_no_new_words`: CONFIRMED wrong on 3 of 8 rulings that it marks. s370, s220 and s250 ask for new words (F1).
3. Point 3, the setup of `test_request_page`: CONFIRMED half right. s272 of night 145 called respecify three times before its answer, but no call landed (F2).
4. Point 4, the diff: CONFIRMED. Five files change, the three test files pass, and the stale count stays 2.

### Point 1 in detail

The probe `f3.py` replays s382 at its wake on e7cf6426. The surface refusal comes first, then the same-words refusal at `api.py` 5818, then the answer. Neither refusal carries `criterion_stands`. The door prints:

"No respecify of ver_opt_show_py has landed in this session. The principal's ruling in the relay is on ver_opt_show_py. Your answer carries ver_opt_show_py as it stands now. Your last respecify of ver_opt_show_py was refused with: ... Write what he asked for. Send his words about the check to the Tester with msg.answer_tester, with this criterion in refs. Respecify ver_opt_show_py first with a corrected criteria.respecify call. Then answer once with msg.answer_tester, with these refs: [ver_opt_show_py]"

The quoted refusal names `msg.answer_tester`, and the door then forbids that answer. The door has the last word, so the seat still meets one order. This is low (F4). The probe `retry_wake.py` gives the same refusal for s387. The F2 shape, `argpath.py`, records the `ArgumentError` and refuses the answer. The F3 shape, `f3.py`, gets `unchanged: True`, and the door refuses the answer.

### Point 2 in detail

The probe `p2b.py` cuts `rulings` to the ruling of each wake and calls `ruling_asks_no_new_words` on each ruled criterion of the 15 answering sessions. It says "no new words" on 8 rulings:

| Session | Ruling words, in part | Asks new words |
|---|---|---|
| s220, cr_2 and cr_3 (158) | "Keep line 4, but fix its check ... Drop line 5, because I never asked for the prompt to be hidden" | yes, "Drop line 5" |
| s274 (158) | "Line 3's check is wrong ... Please fix that check" | no |
| s250, cr_1, cr_4, cr_5, cr_6 (159) | "line 7 should go ... Drop line 14" | yes, two removals |
| s302 (159) | "For the check on line 2, wrap a small command ..." | no |
| s349 (159) | "line 2 is what needs correcting. The check runs the command ..." | no |
| s370 (159) | "please rewrite line 3 ... change it to say the command prints the same version message as today" | yes |

`_WORDS_FAULT` (`api.py` 5395) matches "is wrong", "should say" and "needs to say" only. It misses "rewrite line", "change it to say", "Drop line" and "should go". The implementer named the cr_3 case. The miss is wider: s370 and s250 too.

The probe `replay_wake.py` is `replay308.py` on e7cf6426 with the rulings cut at the wake. Refused: s220, s204, s333, s382, s387, s398, s405 and s412, 8 in total. Admitted: s131, s274, s250, s302, s349, s370 and s392, 7 in total. s250 and s370 answered after a refused respecify and no write, so each answer carried the old text. Both are wrong admits. The pass count of 11 uses the rulings of the end of night (review 2, F6).

### Point 3 in detail

Night 145 is in `D:/repos/rota/.rota/clickI_night145.db`. s272 woke on m144. In turn 1 it called `criteria.respecify` on cr_1, cr_2 and cr_3 and then `msg.answer_tester`. All three respecify calls got "the principal contested these words". The answer m145 went out. `receipts` holds no row for s272. So the night respecified and landed nothing. The new setup lands a respecify, which is a shape that the night never took. The test checks the inbound of the Tester, so the setup is acceptable. The comment is false.

### Point 4 in detail

`git diff 541bb828 e7cf6426 --stat` shows five files: `rota/core/sandbox.py`, `rota/roles/api.py` and three test files. The hunks:

- `Sandbox.call` records an `ArgumentError` on `criteria.respecify` (553 to 560).
- `_ruling_answer_refusal` keys on the landed write, `respecify_stands` and `ruling_asks_no_new_words`. The missing-refs door speaks first. While a ruled criterion has no write, its text offers no call (frame 135).
- `_note_respecify_refusal` replaces `_failed_respecify`. `_respecify_record` adds the flag to `respecify_stands`.
- `api._stands` puts `criterion_stands` on the four refusals at 5724, 5729, 5835 and 5840. Their texts do not change.
- `api.ruling_asks_no_new_words` is new, and it is no op.

No brief and no graph file changes. The 162 single cases compose as before, so the stale count stays 2 (`stale.py`). `pytest -n 0` on `test_frame308_answer_after_respecify.py`, `test_frame308_ruling_answer.py` and `test_request_page.py`: 130 passed, 4 xfailed.

## (b) Findings

1. **F1. The no-new-words predicate admits rulings that ask for new words.** `rota/roles/api.py` 5671 and 5395, read at `rota/core/sandbox.py` 1604 to 1610. Night high, frame high. CONFIRMED: `p2b.py` and `replay_wake.py`. On s370 ("please rewrite line 3 ... change it to say") and s250 ("line 7 should go ... Drop line 14") the door admits the answer with the old text and no write. On s220 the missing-refs route offers `[cr_3, cr_2]` with no rewrite, although "Drop line 5" asks for one. The same regex gap lets the respecify door say "The criterion stands" on these rulings. Fix: widen `_WORDS_FAULT` to removals and rewrites ("drop line N", "line N should go", "remove line N", "rewrite line N", "change it to say"), with s370, s250 and s220 as red tests.
2. **F2. The setup comment of `test_request_page` misstates night 145.** `tests/rota/test_request_page.py` 1676 to 1677. Night low, frame low. CONFIRMED: `clickI_night145.db`, s272 turn 2 shows three refused respecify calls, and `receipts` holds no row for s272. Fix: say that s272 tried and was refused, and that the test lands one respecify so it checks the inbound of the Tester only.
3. **F3. The pass count still reads the rulings of the end of night.** `replay308.py`. Night low, frame high. CONFIRMED: `replay_wake.py` gives 8 refused and 7 admitted, against the 11 and 4 of the report. The predicate of 2b reads the last ruling, so the cut now changes the result. Fix: cut `rulings` to the wake in the replay, and report the count from that.
4. **F4. The quoted refusal names the answer that the door refuses.** `rota/core/sandbox.py` 1617 to 1624. Night low, frame low. CONFIRMED: `f3.py` on s382 prints "Send his words about the check to the Tester with msg.answer_tester" inside a refusal of that answer. The order that follows is clear, but frame 135 asks for no such pair. Fix: quote the refusal only up to "Write what he asked for", or let the 5818 branch of `criteria_respecify` drop its route while no write has landed.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b85289fd-418f-43a1-a641-15dad2620cfa/scratchpad/r308b/`. Each opens the night databases with `?mode=ro` and works on a copy in memory. No probe calls a model.

- `retry_wake.py`: from review 2, run again on e7cf6426. It shows that s382 and s387 are refused after a corrected surface, and that s370 turn 1 is admitted.
- `argpath.py`: the F2 shape of review 2. The door refuses.
- `f3.py`: the F3 shape of review 2 (`unchanged`), and the s382 turn 2 shape with the full door text.
- `p2b.py`: `ruling_asks_no_new_words` on each ruled criterion of the 15 sessions, with the rulings cut at the wake by `verdict_id`.
- `replay_wake.py`: `replay308.py` on e7cf6426 with the same cut.
- A `python -c` read of night 145: s272 calls, results, `receipts`, m144 and m145.
- `stale.py`: the 162 single cases. 2 hold the brief sentence of pass 2.
- `pytest -n 0` on the three test files: 130 passed, 4 xfailed.

## (d) Usage

The harness gives no counter. The estimate for review 3 is about 30k input tokens and about 8k output tokens, about 38k in total, over the 25k cap. No sub-agent ran.
