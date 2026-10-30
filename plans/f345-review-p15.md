# Review p15: pass R6 on r6root (8a8f059a)

Verdict: NOT READY. The sample of 15 deletions holds 2 wrong deletions. One re-pin hides a loss. The fixes are small, and the rest of the pass is sound.

- Wrong deletions: `test_a_right_verdict_of_nights_143_and_144_lands` and `test_m236_the_moved_reading_lands_with_the_item_approved`, both in test_frame234_verdict_lines.py.
- The re-pin that hides a loss: `test_s159s_drop` in test_frame193_pass1.py.
- The 10 skips: each reason names a real code gap.
- The three replay reds: CONFIRMED. They fail at r6root and at the head of rota/foundation too.

## (a) The points

1. The deletions: 2 of the 15 sampled deletions are wrong. The other 13 follow the rule.
2. The re-pins: 9 of the 10 sampled re-pins follow the ruled menu. `s159s_drop` hides a binder loss. Two park re-pins still pass a `words` argument.
3. The skips: all 3 reasons are real in the code at r6root.
4. The reds: CONFIRMED. The same three tests fail at r6root and at the rota/foundation head.
5. The open questions: answered below in section (c).

### Point 1, the 15 sampled deletions

| File | Test | Verdict |
|---|---|---|
| frame234 | the_same_words_land_when_line_1_is_approved | Follows the rule. It pins the non-refusal of the line-1 door, which is gone. |
| frame234 | a_right_verdict_of_nights_143_and_144_lands | WRONG. It pins the landed rows of recorded night verdicts, and the menu form lands them (finding 1). |
| frame234 | m236_the_moved_reading_lands_with_the_item_approved | WRONG. It pins landed rows on the guess key. Keep it skipped with the line_menu reason, as guess_route does (finding 2). |
| frame234 | a_named_fault_on_line_4_lands | Follows the rule. It pins the non-refusal of the fault door. |
| frame234 | a_fault_past_the_end_of_the_page_refuses_nothing | Follows the rule. It pins the non-refusal of a word-form refusal. |
| frame305 | a_drop_of_the_note_is_still_told_to_contest | Follows the rule. It pins the text of a word-form refusal. |
| frame305 | a_change_that_holds_a_need_word_is_a_revise | Follows the rule. It reads a need word, and the menu offers no revise there. |
| frame305 | s357s_plain_revise_with_no_act_lands_as_on_the_parent | Follows the rule. It pins the revise verb. |
| night173 | s120s_call_on_m35_lands_with_c_3_approved | Follows the rule. It pins how the word form reads line numbers of an earlier page. |
| night173 | a_change_request_backs_the_revise | Follows the rule. It pins the revise door. |
| night173 | a_ref_on_two_lines_takes_its_act_on_either_line | Follows the rule. It pins the flat `acts` map. |
| frame193 | a_phrase_maps_by_its_first_word | Follows the rule. It reads the verb of a seat phrase. |
| frame193 | s263s_contest_of_the_change_line_names_line_5 | Follows the rule. It pins the texts of the frame 255 door and the naming door. |
| f2 | s271s_call_lands_on_his_reply | Follows the rule. It pins `words` as a nested field of an act. |
| f2 | a_line_objects_words_from_his_reply_land_on_the_row | Follows the rule. It pins `words` as a nested field of a line object. |

The count of wrong deletions is 2 of 15. At that rate, about 8 of the 57 deletions are wrong. Both wrong deletions are in the file that had the most deletions.

### Point 2, the 10 sampled re-pins

| Test | The call | The assertion |
|---|---|---|
| frame234 m25s_instruction_lands_on_the_request_line | Uses the menu (`add <quote>` on the request line). | Ruled: add lands approve with the act add. |
| read_back contest_of_the_line_rules_a_row | Uses the menu (`misread` with rows). | Ruled: in `_OPTION_ROWS`, misread lands contest. |
| read_back three_clauses | Uses the menu. | Ruled: the read-back text shows drop. |
| frame193 s159s_drop | Uses the menu. | HIDES A LOSS. The test now asserts six drops, not seven (finding 3). |
| frame305 s357s_words_revise_the_note_and_land | Uses the menu (rewrite). | Ruled: in `_OPTION_ROWS`, rewrite lands contest. |
| request_page revise_of_the_item_line | Uses the menu (`other <quote>`). | Ruled: other lands contest. |
| request_page touch_note | Uses the menu. | Ruled: `line_menu` gives a merged or abandoned batch approve only. |
| principal_reply ruling_door_holds_the_page | Uses the menu. | Ruled: the menu refusals replace the word-form refusals. |
| park_page, line 292 | The TOOL text passes `words=` with WALK. The seat today makes no such call. | The assertion holds (finding 4). |
| park_page, line 780 | The TOOL text passes `words=` with WALK. The seat today makes no such call. | The assertion holds (finding 4). |

The 23 touched files ran in replay at r6root with this result: 565 passed, 11 skipped, 8 xfailed and 3 failed. The 3 failures are the 3 reds of point 4.

### Point 3, the 10 skips

1. `line_menu`, 8 tests: the reason is real. `menu_kind` gives line 1 the kind request, with the options approve, `add <quote>` and `other <quote>`. Only the kind touch takes `exclude`, so no option lands on the guess key or on bg_3 (api.py:13891-13908, 13793-13801).
2. `page_clauses`, 1 test: the reason is real. `menu_ruling` calls `page_clauses(his, ...)` with his reply only (api.py:14077), so the earlier exchange names no line.
3. `menu_ruling`, 1 test: the reason is real. `span_of` takes every line that a clause names. The `missing` check at api.py:14329 does not filter a line whose row is gone.

### Point 4, the three reds

The same three tests fail at both commits, with `ROTA_L1` unset:

- `test_seam2_word_per_line.py::test_a_row_on_two_lines_of_the_page_lands_a_word_on_each`
- `test_seam2_word_per_line.py::test_two_words_on_one_ref_of_another_act_keep_one_row`
- `test_f345_p5_landing.py::test_a_landing_counts_its_ruled_refs_rows_as_writes[L1-LI-remove-lines-on-a-criteria-page-is-a-drop-9-lines0]`

The head of D:/repos/rota is now c49d88be, not f52c2716. Its only commit after f52c2716 changes docs. The `rota/` tree is the same, so the result holds for f52c2716.

## (b) Findings

1. tests/rota/test_frame234_verdict_lines.py, `test_a_right_verdict_of_nights_143_and_144_lands`, deleted. Severity high. CONFIRMED by the probe probe1.py. On `_request_page`, the menu call lands the contested lines of 144 m193, 143 m339 and S122, and line 1 is keyed `other <quote>` where his words name line 1. 143 m263 contested line 1, which his words do not name. The menu refuses that call: "no clause of his names line 1". That row change is a ruled menu result to pin, not to delete. Fix: restore the test as a re-pin with menu options, one expected row set for each recorded verdict.
2. tests/rota/test_frame234_verdict_lines.py, `test_m236_the_moved_reading_lands_with_the_item_approved`, deleted. Severity low. CONFIRMED by reading. The test pins landed rows on the key `guess:calculate_tip` with recorded words from night 144. The same `line_menu` gap blocks it as it blocks the 7 skipped guess_route tests. Fix: restore the test, skipped with the guess_route reason, and count it in the `line_menu` debt.
3. tests/rota/test_frame193_pass1.py, `test_s159s_drop`, re-pinned. Severity high. CONFIRMED by a probe of `page_clauses(M63, 8)`. The probe gives the clause lines [5], [2, 3, 4], [7, 8] and [1]. M63 says "line 6 calls the README stale" and then "drop those three". No clause names line 6, so the menu refuses the drop that he asked for. The re-pin lowers the assertion to six drops and passes green on a binder loss. Fix: keep the test at seven drops and mark it `xfail(strict=True)` with the binder reason, or fix the clause split of `line_words`.
4. tests/rota/test_park_page.py:292 and :780, re-pinned. Severity low. CONFIRMED by grep. The re-pinned calls still pass `words=WALK`, and `rulings_rule` still accepts `words` (api.py:14364). The seat today sends no `words`, so these tests do not pin the call that the seat makes. Fix: remove the `words` argument from the re-pinned calls.

## (c) The open questions of the report

1. Change `line_menu`. Do not retire the guess route. Recorded night 144 (m236) shows that he contests the guess files under line 1. Today no option can carry that contest. The fix gives the request line of a stamped page `exclude <path>` for each path that the line shows.
2. Yes, this is a binder fault. `page_clauses(M63, 8)` gives no clause that names line 6. The words about line 6 stay inside the clause of line 5. Fix the split in `line_words` before the s159 test pins fewer rows.
3. The code outside the tests is the same. From f52c2716 to r6root, only `plans/stack.md` changed outside the tests. So 45 of the 48 reds run the same code and tests as on foundation. The 3 reds in the touched files are the reds of point 4. A gate run against the foundation baseline is still the record, so run it once before the merge.
4. Add the law 6 test now. `rulings_rule` still takes `words`, and finding 4 shows that tests still pass it. One menu call with extra `words` must assert that each row carries only the words of his clause.

## (d) Probes

- The probe probe1.py loads the old frame234 file from f52c2716 (old234.py in the same folder). It makes the menu call for each RIGHT_143_144 verdict, S122_ON_REQUEST, "Line 9 is wrong." and the negated match. Then it prints the rows or the refusal. Folder: C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/00ca90d0-18a5-4929-b3d3-aedcb3b99ae5/scratchpad/p15/
- An inline Python probe printed M63 and the result of `page_clauses(M63, 8)` from test_frame193_pass1.
- pytest ran the 23 touched files at r6root in replay, with ROTA_MODEL=qwen3:8b and `ROTA_L1` unset.
- pytest ran test_seam2_word_per_line.py and test_f345_p5_landing.py at r6root and at the D:/repos/rota head (c49d88be).
- git diffs and greps gave the old bodies, the skip reasons and the calls that pass `words`.
- The worktree is C:/Users/roman/rota_p15. It is detached at r6root, and nothing in it changed.

## (e) Usage

The harness shows no exact split. The estimate is about 45k input tokens and 10k output tokens, about 55k in total. That is above the cap of 30k. Sub-agents: none.

# Re-check p15b, pass R6b

Verdict: NOT READY. The fresh sample of 12 deletions holds 2 wrong deletions. The 12 reversals are sound.

- Wrong deletions: `test_words_that_fault_line_1_land_a_contest_on_it` (frame234) and `test_s275s_call_lands_on_his_reply` (f2_rulings_words).
- Reversed re-pins that fail the rule: none.
- The replay result is 3 failed, 576 passed, 14 skipped, 8 xfailed. The 3 reds are the 3 reds that p15 found at foundation.

## (a) The points

1. The deletions: 2 of the 12 fresh samples are wrong. By the brief, 2 is NOT READY.
2. The 12 reversals: each call is a menu call that the seat makes today. Each assertion holds the old claim.
3. `_rule_m245`: its one test passes for the right reason. The `words=M246` argument changes no row.
4. The replay: the 23 touched files give the same 3 reds as p15. R6b's report says each touched file passed, and that is not correct.

### Point 1, the 12 fresh deletions

| File | Test | Verdict |
|---|---|---|
| f25 | the_offer_of_stray_fields_carries_every_line_of_the_page | Follows. It pins the word-form offer that moves stray act fields. |
| f2 | s275s_call_lands_on_his_reply | WRONG. It pins the rows of night 172 m132, and the menu lands them (finding 2). |
| f345_p5 | remove_on_a_line_that_is_no_code_lands_as_a_drop | Follows. It reads the verb "remove" as a drop. |
| frame193 | a_sentence_that_names_and_agrees_spares_no_contest | Follows. It pins a polarity refusal text. |
| frame234 | a_negated_match_lands_the_contest | Follows. It pins the polarity of "doesn't match". |
| frame234 | words_that_fault_line_1_land_a_contest_on_it | WRONG. The menu lands the contest on s1 (finding 1). |
| frame250 | a_right_approve_of_a_matched_line_lands | Follows. It pins the non-refusal of the match door. |
| frame258 | a_request_word_no_criterion_holds_lets_line_1_be_contested | Follows. It reads a request word in code. The menu refuses that call. |
| frame305 | words_with_no_change_are_no_revise | Follows. It pins a word-form refusal of revise. |
| frame337 | a_later_fault_after_an_earlier_match_lands_the_contest | Follows. It pins the order of polarity across the exchange. |
| read_back | his_reply_alone_confirms_a_reading | Follows. It pins the guard on `words="ok"`. |
| seam2 | the_drops_of_a_conjoined_subject_land | Follows. Line 2 is kind request, and its menu offers no drop. |

### Point 2, the 12 reversals

- frame234 a_right_verdict_of_nights_143_and_144: menu keys, row sets per verdict. Holds.
- frame234 m236: skipped with the `line_menu` reason. Holds.
- frame234 an_unnumbered_sentence_never_spares_a_note_line: menu refusal on line 6. Holds.
- read_back only_his_words_confirm_the_line: `"3": "ok"` meets the read-back branch at api.py:14204-14208, which leaves the line out. Holds.
- guess_route a_request_correction_still_lands_on_line_1: `other <quote>`, contest on the item. Holds.
- frame258 the_criteria_words_alone_do_not_spare_line_1: menu refusal on line 1. Holds.
- frame337 s193s: skipped on the `page_clauses` gap. Holds.
- frame250 s212s: `other <quote>` and rewrite, contests on c1 and l_2. Holds.
- frame250 the_map_with_line_6_contested: rewrite on line 6, clause keys none. Holds (point 3).
- night173 s179s: rewrite on line 5, the act is rewrite. Holds.
- night173 a_revise_on_a_line_with_no_words_is_refused_once: refused on each call. Holds.
- f25 the_offer_gives_no_approve_to_a_line_his_words_fault: menu refusal, no offer. Holds.
- frame193 s159s_drop: seven drops, skipped with the binder reason. Holds.

## (b) Findings

1. tests/rota/test_frame234_verdict_lines.py, `test_words_that_fault_line_1_land_a_contest_on_it`, deleted (old line 197). Severity high. CONFIRMED by probe_del.py. `page_clauses` gives the clause "1 is wrong: ..." the line [1]. On `_present`, line 1 is kind other. The call `{"1": "other json, not yaml", "rest": "approve"}` lands s1 contest. The old assertion holds. Fix: restore the test as a re-pin with `other <quote>` on line 1.
2. tests/rota/test_f2_rulings_words.py, `test_s275s_call_lands_on_his_reply`, deleted (old line 102). Severity high. CONFIRMED by test_probe_s275.py. On night 172 m132, the menu call keys 9 to 15 drop, 18 rewrite and the clauses c1 to c3 none. The call lands reading:m121 rewrite and challenge_constraints_sentinel drop. Both old assertions hold. Its sibling s271s asserts `words`, but s275s asserts only the acts. Fix: restore the test as a re-pin with that menu call.
3. tests/rota/test_frame250_verdict_faults.py:195, `_rule_m245`, and tests/rota/test_read_back.py:74, `_answer`. Severity low. CONFIRMED by probe_rev.py. The call with `words=M246` and the call without it land the same rows: bg_4 contest, cr_3_show_python_append approve. So the test passes for the right reason. The seat today sends no `words`. Fix: remove the `words` argument from both shared helpers.
4. Outside the points. The R6b report section (b) says each touched file passed. The replay gives 3 reds in 2 touched files. p15 found that the same 3 fail at foundation. Severity low. CONFIRMED by the replay. Fix: correct the report line.

## (c) Probes

Folder: C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/00ca90d0-18a5-4929-b3d3-aedcb3b99ae5/scratchpad/p15b/

- old_bodies.py and new_bodies.py print a test body at f52c2716 or at r6root.
- probe_del.py runs `page_clauses` and the menu calls for findings 1 and the seam2 conjoined drop.
- test_probe_s275.py runs the menu call of finding 2 on the night 172 database.
- probe_rev.py runs `_rule_m245`'s call with and without `words`.
- pytest ran the 23 touched files in replay at r6root, with ROTA_MODEL=qwen3:8b and `ROTA_L1` unset.
- The worktree is C:/Users/roman/rota_p15b, detached at r6root (4f824369). Nothing in it changed.

## (d) Usage

The harness shows no exact split. The estimate is about 40k context tokens and 9k output tokens, about 49k in total. That is above the cap of 20k. Sub-agents: none.
