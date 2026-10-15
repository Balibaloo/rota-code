# Frame 129, review 1b: the diff 0bf6a5ea..254f04e4 on _assert_words_fault

Reviewer: read-only agent on worktree C:/Users/roman/rota_r129b at 254f04e4. Date: 2026-10-15.

Verdict: accept. The pass closes review 1's findings 1, 2 and 4, and it keeps s232 refused. Two findings are low, and one finding is a watch item for night 150.

## (a) Verdicts on the points

1. Accept. Only a message wake whose trigger verb is `deliver` takes the admit. The s232 replay from night 149 is still refused (observed: 2026-10-15).
2. Accept. Propose names `msg.report_liaison` and `decisions.author`, both in `propose.tools`. Answer names `msg.submit_liaison` alone, and `answer.tools` offers it.
3. Accept. Both new tests are red at 0bf6a5ea and green at 254f04e4. The file reads 19 passed. No CR byte.
4. Line given below.

## Answers

1. The admit is `if verb == "deliver": return None` at api.py line 1330. It sits after the challenge branch and the `tick:exhausted` branch, so those keep their refusals. `verb` comes from the trigger message on any wake kind. A tick wake has a trigger only when a ref resolves to a message (runner.py `trigger_message`). The `tick:contested` refs are item ids, so a contest wake does not take the admit. Night 149 holds three Vision Keeper deliver sessions: s103 (m20), s147 (m51) and s209 (m100). Replay: s232 on its own wake (message, propose, trigger m118), with the item text set back to CONFIRM on an in-memory copy, returns "confirm_default_on_eof is the principal's own words. A propose wake does not rewrite them. Send msg.report_liaison with what the item should say, so the principal rules. Or answer with decisions.author". The same call on s209's deliver context returns None. Note: on the database as it is, the s232 call returns None, because s232 committed and the item already holds the s232 words. A replay must restore the earlier text first.
2. `_wake_mode_tools` keys the mode by the wake. Propose: report and author are both in `propose.tools`, so the text is unchanged from pass 1. Answer: `answer.tools` has `msg.submit_liaison` and no `decisions.author`, so the text is "Send msg.submit_liaison with what the item should say, so the principal rules." `msg.submit_liaison` is the graph's Vision Keeper to Liaison `submit` send (sandbox.py line 745). The Liaison's submit mode presents items for the principal's signoff (prompts/liaison/submit.md). The answer brief, line 16 to 18, names the same call for a widened ask. So the call exists and does reach the principal. See finding 2 for one gap in the words.
3. With the old `_assert_words_fault` swapped in from 0bf6a5ea: `test_a_deliver_wake_amends_a_decided_item` fails with the deliver refusal, the right reason. `test_an_answer_wake_names_only_calls_the_mode_offers` fails on "A answer wake", the article line. The call-name subset check is never reached at the old commit. At 254f04e4 the file reads 19 passed, so pass 1's tests stay green. Both touched files hold 0 CR bytes.
4. Night 150's read: list each Vision Keeper deliver-wake `problem.assert` that changes a decided item's words, and check the item against the delivered statement's refs. Night 149 shows the pattern: s147 rewrote `how_it_works` and `confirm_default_on_eof`, and s103 rewrote `how_it_works`.

## (b) Findings

1. rota/roles/api.py line 1330. Severity low. PLAUSIBLE: the admit holds for any decided item on a deliver wake, not only an item the delivered statement reaches. Review 1's finding 3 offered the narrower gate, "when the trigger's statement refs reach the item". The deliver wakes of night 149 rewrite `how_it_works`, a description item that no single statement reaches, so a narrow gate would likely refuse a needed rewrite. A seat on a deliver wake can still put its own words on an older item, the s232 class of defect. Fix: keep the admit now, and let night 150's read (answer 4) decide whether to gate on the statement's refs plus the description item.
2. rota/roles/api.py lines 1343 to 1345. Severity low. PLAUSIBLE: `msg.submit_liaison` presents the items as stored, and the refused words never reach the store. The proposed words then travel only in the message prose. The text "with what the item should say" tells the seat to put them there, so the route works if the seat obeys. Fix: none needed now. Read one answer-wake refusal on night 150 for whether the submit carries the words.
3. tests/rota/test_frame221_assert_words.py lines 349 to 350. Severity low. CONFIRMED: `named <= offered` passes when the refusal names no call, and at 0bf6a5ea the test fails on the article before this check. The test does not prove that the answer text names `msg.submit_liaison`. Fix: add `assert "msg.submit_liaison" in msg`.

Outside the points: none.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/cd6300cd-93cb-43d0-81c1-5833e2698637/scratchpad/r129b.

- `oldswap.py` with `old_api.py`: a pytest plugin that execs the 0bf6a5ea `_assert_words_fault` into `rota.roles.api`. Ran the test file with `-p oldswap`: 2 failed, 17 passed.
- `replay.py`: opens night 149 with `?mode=ro`, backs it up to memory, restores CONFIRM on `confirm_default_on_eof`, and calls `_assert_words_fault` with s232's and s209's session contexts.
- Inline `python -c` reads of night 149: sessions, deliver messages, and `tool_calls` for s103, s147 and s209.
- The test file at 254f04e4: 19 passed. CR count with `tr`: 0 and 0.

## (d) Usage

About 45k input tokens and 8k output tokens, about 53k in all (estimate; read the harness line for the actual).
