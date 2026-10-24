# Frame 306, review 1 of pass 1 (6f4fd0c2)

Verdict: accept with one fix. 6f4fd0c2 goes on the branch after the gate, with finding 1 fixed in a pass 1b or with the fix recorded as owed. Reviewer read-only in C:/Users/roman/rota_r308 at 6f4fd0c2.

## (a) The verdict on each point

1. CONFIRMED. count2.py on 6f4fd0c2 gives 857 texts, 46 named, 28 refused, 18 passed, 0 refused outside. No night text is refused wrongly. Three note texts pass (finding 3). Synthetic behaviour texts are refused (finding 2).
2. CONFIRMED. The s195 calls under m76 and the s255 cr_3 call under m115 get "The criterion stands" with his words. The s255 cr_2 call gets the repair 1 refusal. Frame 308's tests stay green: 68 passed over the three files. The Tester route is callable from criterion_repair. The route is not callable from the criteria mode (finding 1).
3. Deviation 1, the order: right. Repair 1 asks for a rewrite that repair 2 refuses under a check-only ruling, so repair 2 must speak first. Deviation 2, the own-words skip: right. The skip runs after db3b0944's rule, and the same-words branch answers the row's own text. Deviation 3, "Also add a second check" admitted: acceptable for now, but it keeps a note door open to fit one test (finding 3).
4. Neither stale case goes red from its stored transcript. Both recorded respecify texts pass `_about_the_tests`. Neither ruling makes `ruling_asks_no_new_words` true, so repair 2 does not fire. Both cases are stale only by the prompt hash.
5. CONFIRMED. The diff touches only api.py, criterion_repair.md and the new test file. The test file asserts that night 158's cr_2 "contain" text passes the text door. No evidence page code changes.

## (b) Findings

1. rota/roles/api.py 5136-5141 with 5379. High. CONFIRMED. `criteria_specify` uses `_about_the_tests_refusal`, and the note form names `msg.answer_tester`. `rota/roles/prompts/terminologist/criteria.tools` holds no `msg.answer_tester`. Only criterion_repair.tools and unresolved.tools hold it. The refusal names a call that the criteria mode cannot make, against frame 135's law. Night 155's "Line 1 adds the `echo_json` helper..." is a specify-time text that meets this refusal. Fix: give `_about_the_tests_refusal` a flag, and let the specify door drop the Tester sentence and say "Write the behaviour that the check must show".
2. rota/roles/api.py 5108-5130. Low. CONFIRMED on synthetic texts (probe_fp.py). The widened rule refuses these behaviour texts: "The check command exits with status 1 ...", "Each check reports its name ...", "Line 2 shows the Python version ...", "A test run with --verbose prints each test name.", "Assertions in the user's code raise AssertionError ...". Click nights hold no such text, so the count shows 0. A linter, a test runner or a page of output lines in an adopting repository meets a false refusal. Fix: anchor the subject rule to the modal of a note ("must", "should" plus a check verb) or to "Line N's check", and add these five texts as controls.
3. rota/roles/api.py 5108-5121. Low. CONFIRMED by the count. Three note shapes pass the door. Night 157 cr_2 ends "so that the output check can see True". Night 159 ver_opt_show_py ends "Also add a second check that turns the flag on and checks ...". Night 155's nine "The new tests must be placed ..." texts pass because a word sits between "the" and "tests". The pass keeps the imperative open to keep frame 308's S398_TEXT test green. Fix: decide in a ruling whether a placement rule for new tests is a criterion, and match "add a ... check" after frame 308's test is re-read against the 2026-10-08 ruling.
4. rota/roles/api.py 5138-5141. Low. PLAUSIBLE. Under a ruling that asks new words (s255 cr_2 under m115), repair 1 says "Send a note about the check to the Tester with msg.answer_tester". The answer door in sandbox.py 1604-1650 refuses that answer until a respecify of cr_2 lands. The refusal text gives the order only by sentence order. Fix: say "When the behaviour lands, send the note ..." in the note form.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0cdcac52-3588-4266-b1fb-fc5d7d31b805/scratchpad/r306/.

- count2.py, count.py: the pass's count, pointed at rota_r308. It read nights 140 to 160 with ?mode=ro and printed 857, 46, 28, 18, 0.
- probe_fp.py: eleven synthetic texts through `_about_the_tests`. Five behaviour texts gave True, and three note texts gave False.
- An inline probe read the full ends of the 143, 157 cr_2 and 159 texts from the night databases.
- An inline probe read tests/rota/cassettes.db (?mode=ro) for the two stale cases' latest qwen3:8b transcripts. A second probe ran `_CHECK_FAULT` on the case entry "line 3 is wrong: ..." (False) and `_about_the_tests` on both recorded texts (False, False).
- pytest -n 0 on test_frame306_check_note.py, test_frame308_answer_after_respecify.py and test_frame308_ruling_answer.py: 68 passed.

## (d) Usage

The harness count is not visible to this agent. My estimate is 75k input tokens, 9k output tokens, 84k total. This is above the 25k cap. Take the harness line as the measure.
