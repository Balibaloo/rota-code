# Frame 317, review 1

Verdict: the change at 9a2caccc stands. Pass 1c makes two low fixes, F2 and F3. The label of point 2 needs no change.

## (a) The verdict on each point

1. Confirmed. Only Tester answer wakes move. On 247 wakes of night 161 the other 226 prompts are byte for byte the same, and 156 wake tests pass.
2. Not confirmed. The label "failed before any assertion" on s410 is right by frame 110's own rule. No fix. See F1.
3. Night 161 gives no wrong pick. All 41 picks are `E ` lines, and 28 runs give no head. Night 160 gives one wrong pick. See F3.
4. A criterion with no test adds nothing, which is correct. A test of a retired ticket in the batch still travels. See F2.
5. Plausible fit. s364's first turn grows by about 5.0k characters on the real night. A five-test wake grows by about 9.2k characters. See F4.
6. Clean. No CR byte in the three files at either commit. The diff adds no print, breakpoint or pdb.

## (b) Findings

1. Point 2, the label. `rota/core/runner.py:2780` and `_failed_before_assertion` at line 3130. Severity low. CONFIRMED that the label is correct. The probe gives True on the whole s410 output and True on its 700 tail, so pass 1b did not change the label. Frame 110 built the label for night 106's `_02`, which raised `KeyError: 'prog_name'` inside `runner.invoke` (`plans/frame110-design.md` lines 78 and 103). `rota/roles/prompts/tester/challenge.md` line 7 reads the label for exactly this shape: "A test that calls a function the way a runner calls a command is the test's fault." The interview's words "in the call under test" exclude frame 304's arrange label, `FAILED_BEFORE_ASSERTION`. They do not exclude frame 110's block heading. The Tester `answer.md` brief does not read the label. Fix: none. Keep the label, and close the open question of pass 1b with this reading.
2. Point 4, a retired ticket. `rota/core/runner.py:2818` to 2824. Severity low. CONFIRMED. The probe made `tk_2_version_option_show_python` retired by a newer slice `tk_3` of item `i1` in `b_5`, and both test blocks still showed on m200. `tests_missing` drops such a ticket with `not_retired(conn, "bt.ticket_id")` at `rota/core/predicates.py:830`, so the wake shows a test that the predicates say owes nothing. Fix: append `scheduler.not_retired(conn, "bt.ticket_id")` to the query of the new loop.
3. Point 3, the word search. `rota/core/runner.py:2834` to 2846, `_raising_line_head`. Severity low. CONFIRMED on night 160, not on night 161. Night 160, seq 243, `tst_confirm_default_on_eof`: the search picks the source line `assert False, "Expected UsageError on EOF ..."`, because the line holds "Error". Also, "Try passing" never decides a pick on night 161, because every line with it also holds "Error". The word fits click's one message and not the workflow. Fix: take the first line that starts with `E `, then fall back to `Traceback`, and drop "Try passing".
4. Point 5, the size. Severity low. PLAUSIBLE, not measured in tokens. Night 161 recorded s364 at `num_ctx` 16384, with a 4,203-character system and a first user of 13,828 characters, growing to 27,989 by turn 9. The change adds about 4,969 characters to m200 on the real night and 9,203 to m154, which holds five failed tests. The largest turn of any 16k session on night 161 already holds 64,375 characters. So s364 at about 37k characters and a five-test wake at about 41k characters stay inside what the night ran. No tokenizer ran, so the token count is open. Fix: none for pass 1c. Read the token count on the next night.
5. Outside the points, test strength. `tests/rota/test_frame317_answer_wake.py:315`. Severity low. CONFIRMED by reading. The Developer test asserts only that no block shows. A Developer wake never had a block, so the test cannot fail for this change. Probe 1 covers the claim of point 1. Fix: assert the Developer prompt equals a stored copy, or leave probe 1 as the proof.
6. Outside the points, the arrange path. `rota/core/runner.py:2788` to 2792. Severity low. PLAUSIBLE. When `_arrange_raise_tail` returns a tail, the code replaces `last_run` whole and drops `state` and `raising_line`. The block then reads the label from the arranged tail. That tail starts at the test's line, so the label stays correct. Fix: none needed. Note it in a comment, or keep `state` in the replacement.

## (c) Probes

All probe files sit in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/51917779-9e71-4bcd-b8e5-e5cbc8b1f811/scratchpad/r317/`.

1. `probe_wakes.py` ran on `old/` (`git archive 025378be`) and `new/` (`git archive 9a2caccc`), each on its own copy of `clickI_night161.db`. It built 247 wakes: each message for its own role and verb, plus each Tester message as an answer and as a challenge. 21 prompts differ, all Tester answer wakes. Results are in `old.json` and `new.json`.
2. `probe_head.py` ran `_raising_line_head` on every failed run of `test_run_journal`, read-only. Night 161: 69 failed runs, 41 `E ` picks, 28 empty, 0 others. Night 160: 13 failed runs, 1 `E ` pick, 11 empty, 1 other.
3. `test_probe317.py` ran with pytest on the frame's fixture: the retired ticket, a criterion with no test, one and two running batches, and the s410 label on the whole output and the tail.
4. Read-only SQL on night 161: `sessions` and `turns` for s364, s370, s397 and s410, the 16k turn maximum, and the test rows against `batch_tickets`.
5. `pytest tests/rota/test_runner.py tests/rota/test_frame317_answer_wake.py tests/rota/test_frame304_arrange_raises.py`: 156 passed.

## (d) Usage

About 70k input tokens, about 10k output tokens, about 80k in total, by the reviewer's own count. The cap was about 30k. Probe 1 and the night reads took the excess.
