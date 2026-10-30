# Classification p15c, the 45 remaining deletions of R6

Counts: 35 delete, 9 re-pin, 1 skip, 45 in total. The 45 are the 55 `-def test_` lines of `git diff f52c2716 r6root -- tests`, less the 10 that R6b re-added. The most re-pins are in test_frame234_verdict_lines.py (4). Each re-pin and the skip has a probe. One new code gap is named (finding 2).

The line between delete and re-pin: a test is a re-pin when its menu call goes through a door that the menu form keeps. Those doors are the naming refusal with its quote escape, the key refusals, and the read-back rows. A test is a delete when the only menu call is a plain option on a line that his words name. Then the old claim was a code read of a polarity, a cue or a span. A re-pin of it pins nothing about his words.

## (a) The points

1. The list: 45 deletions in 14 files. The list is complete.
2. The rows: each of the 45 has a verdict. 25 verdicts come from p15 and p15b, and 20 are new. Probes confirm each new re-pin and the skip.
3. The table: written here, with the counts first.

## (b) The table

The column "Earlier" gives the verdict of p15 or p15b. A dash marks a test that no review sampled.

| # | File | Test | Earlier | Verdict | Line |
|---|---|---|---|---|---|
| 1 | f25_offers_in_mode | the_offer_of_stray_fields_carries_every_line_of_the_page | p15b delete | delete | It pins the word-form offer that moves stray `acts` fields. |
| 2 | f2_rulings_words | s271s_call_lands_on_his_reply | p15 delete | delete | It pins `words` as a nested field of an act. |
| 3 | f2_rulings_words | s275s_call_lands_on_his_reply | p15b WRONG | re-pin | Night 172 m132: R8, lines 9 to 15 `drop`, line 18 `rewrite`, c1 to c3 `none`. Keep the reading:m121 rewrite and challenge_constraints_sentinel drop assertions (p15b test_probe_s275.py). |
| 4 | f2_rulings_words | s271s_call_with_its_nested_words_as_words_lands | - | delete | It pins a nested `words` span sent again as the `words` argument. The menu has neither. |
| 5 | f2_rulings_words | a_line_objects_words_from_his_reply_land_on_the_row | p15 delete | delete | It pins `words` as a field of a line object. |
| 6 | f345_p5_landing | remove_on_a_line_that_is_no_code_lands_as_a_drop | p15b delete | delete | It reads the verb "remove" as a drop. |
| 7 | frame193_pass1 | a_phrase_maps_by_its_first_word | p15 delete | delete | It reads the verb of a seat phrase. |
| 8 | frame193_pass1 | s94s_words_inside_the_map_is_refused_as_its_own_argument | - | re-pin | The menu still refuses the keys `words` and `ask` inside `rulings`. Keep two `pytest.raises` with menu options on the `_m11` page. The texts start "rulings has a key words, and words is its own argument of rulings.rule" and "rulings has a key ask, and ask is its own argument of rulings.rule". Drop the old offered call and the third part, which lands `words=M12`. No other test pins these two refusals. |
| 9 | frame193_pass1 | s263s_contest_of_the_change_line_names_line_5 | p15 delete | delete | It pins the texts of the frame 255 door and the word-form naming door. |
| 10 | frame193_pass1 | a_sentence_that_names_and_faults_a_criterion_spares_its_contest | - | delete | It pins the polarity door, which spares a sentence that names and faults. The menu call is a plain `rewrite` on the named line. |
| 11 | frame193_pass1 | a_sentence_that_names_and_agrees_spares_no_contest | p15b delete | delete | It pins a polarity refusal text. |
| 12 | frame234_verdict_lines | the_same_words_land_when_line_1_is_approved | p15 delete | delete | It pins the non-refusal of the line-1 door. |
| 13 | frame234_verdict_lines | a_page_that_opens_with_a_quote_takes_a_contest_on_line_1 | - | delete | S122 names lines 3 and 4 only, and no words ask for a change of s1. The menu refuses line 1, also with a quote (probe_f A1). The old claim is the line-1 door. |
| 14 | frame234_verdict_lines | a_reference_to_line_1_with_no_cue_lets_it_be_contested | - | delete | It pins the cue door. Its menu landing on the same words is pinned by `test_a_right_verdict_of_nights_143_and_144_lands[144 m193]`. |
| 15 | frame234_verdict_lines | a_sentence_with_no_line_number_lets_line_1_be_contested | - | re-pin | `_request_page`, `{"1": "other Also, take the tip in cents.", "2": "rewrite", "rest": "approve"}`. Keep `calculate_tip == "contest"` (probe_f A3). On this page the clause takes `none` only, so the line key holds the quote (api.py:14221). The option `add` lands approve (probe_b A3). |
| 16 | frame234_verdict_lines | the_quote_branch_lands | - | skip | The new gap of finding 2. |
| 17 | frame234_verdict_lines | a_fault_past_the_end_of_the_page_refuses_nothing | p15 delete | delete | It pins the non-refusal of a word-form refusal. |
| 18 | frame234_verdict_lines | a_fault_after_a_match_in_one_clause_lands_the_contest | - | delete | It pins the polarity read in one clause, as row 19 does. The menu call is `{"2": "rewrite"}`, which 143 m339 pins already. |
| 19 | frame234_verdict_lines | a_negated_match_lands_the_contest | p15b delete | delete | It pins the polarity of "does not match". |
| 20 | frame234_verdict_lines | words_that_fault_line_1_land_a_contest_on_it | p15b WRONG | re-pin | `_present`, `{"1": "other json, not yaml", "rest": "approve"}`. Keep `s1 == "contest"` (p15b probe_del.py). |
| 21 | frame234_verdict_lines | a_named_fault_on_line_4_lands | p15 delete | delete | It pins the non-refusal of the fault door. |
| 22 | frame234_verdict_lines | a_sentence_with_no_line_number_lets_an_unnamed_line_be_contested | - | re-pin | `_present`, `{"2": "other Also, take the tip in cents.", "3": "rewrite", "rest": "approve"}`. Keep `how_it_works == "contest"`. Add `calculate_tip == "contest"`, the unnamed line (probe_f A6). |
| 23 | frame234_verdict_lines | a_bare_agreement_names_no_line | - | delete | It pins a refusal that read "The rest looks fine" as an agreement, which is a polarity. The menu has no such refusal (probe_b A7, finding 3). |
| 24 | frame234_verdict_lines | an_unnumbered_sentence_spares_a_line_of_the_request | - | re-pin | `_page11`, `{"3": "other Line 3 is wrong because the tip is rounded.", "4": "other Also, take the tip in cents.", "rest": "approve"}`. Lines 3 and 4 are kind request and take no `rewrite`. Keep `c3 == "contest"` (test_probe_c test_a8). |
| 25 | frame250_verdict_faults | a_right_approve_of_a_matched_line_lands | p15b delete | delete | It pins the non-refusal of the match door. |
| 26 | frame258_request_line | a_sentence_that_names_line_1_lets_it_be_contested | - | re-pin | `_rule(page, words, ...)` with `"c3": "rewrite"`, c1, c2, c4, c5, c6 `none`, `"1": "other Line 1 is wrong too, because the flag should be called eof_default."`, `"rest": "approve"`. Keep `ruled[ITEM] == "contest"`. The errors are empty (test_probe_c test_258). |
| 27 | frame258_request_line | a_request_word_no_criterion_holds_lets_line_1_be_contested | p15b delete | delete | It reads a request word in code. A quote of its clause on line 1 meets the quote-home refusal, which sends the quote to clause c5 (api.py:14223, test_probe_e). The old row has no menu path. |
| 28 | frame305_note_revise | a_drop_of_the_note_is_still_told_to_contest | p15 delete | delete | It pins the text of a word-form refusal. |
| 29 | frame305_note_revise | a_sentence_that_only_describes_the_note_is_no_revise | - | delete | It pins the refusal "line 11 is the team's note", a read of descriptive words. The menu lands `l_9` contest on `rewrite` and on `drop` (probe_b B). |
| 30 | frame305_note_revise | words_with_no_change_are_no_revise | p15b delete | delete | It pins a word-form refusal of revise. |
| 31 | frame305_note_revise | a_change_that_holds_a_need_word_is_a_revise | p15 delete | delete | It reads a need word. |
| 32 | frame305_note_revise | s357s_plain_revise_with_no_act_lands_as_on_the_parent | p15 delete | delete | It pins the revise verb. |
| 33 | frame305_note_revise | an_act_span_that_names_no_line_is_read_in_its_clause | - | delete | It pins the span read of an act in its clause. |
| 34 | frame305_note_revise | a_span_across_a_clause_edge_reads_every_clause_it_meets | - | delete | It pins a span read across clause edges, in both parametrize cases. |
| 35 | frame305_note_revise | act_fields_beside_the_line_keys_get_the_object_form | - | delete | It pins the word-form shape refusal and its offered object form. |
| 36 | frame337_earlier_answers | a_later_fault_after_an_earlier_match_lands_the_contest | p15b delete | delete | It pins the order of polarity across the exchange. |
| 37 | read_back | a_row_of_the_earlier_answer_needs_his_contest_of_the_line | - | re-pin | `{"1": "approve", "2": {"option": "misread", "rows": ["l_1"]}, "rest": "approve"}` on the same page and words. Keep `pytest.raises`. Change the match to "no clause of his names line 2" (test_probe_d). The old match "read-back line 2" is gone. |
| 38 | read_back | his_reply_alone_confirms_a_reading | p15b delete | delete | It pins the guard on `words="ok"`. |
| 39 | ruled_refs | the_object_form_writes_the_rows_and_the_flat_form_is_refused | - | delete | It pins the object form with `act: remove` and the refusal "takes no acts". The argument `acts=` now meets the generic menu-form text (probe_b D). |
| 40 | seam2_word_per_line | the_drops_of_a_conjoined_subject_land | p15b delete | delete | Line 2 is kind request, and its menu offers no drop. |
| 41 | seam_night173 | s120s_call_on_m35_lands_with_c_3_approved | p15 delete | delete | It pins how the word form reads the line numbers of an earlier page. |
| 42 | seam_night173 | a_change_request_backs_the_revise | p15 delete | delete | It pins the revise door. |
| 43 | seam_night173 | a_ref_on_two_lines_takes_its_act_on_either_line | p15 delete | delete | It pins the flat `acts` map. |
| 44 | seam_night173 | a_say_clause_follows_a_line_reference | - | delete | It pins where the code cuts a span after "say". That is a span read. |
| 45 | seam_night173 | a_revise_on_lines_his_words_name_passes | - | re-pin | Night 174 m55: lines 7 and 9 `rewrite`, lines 2 to 6 and 8 `approve`, `"rest": "approve"`. The clause [2, 3, 4, 5, 6, 8] names those lines, so each needs a key. Change the assertion: the lines with `act == "rewrite"` are [7, 9], with verdict contest, not revise (test_probe_d test_m55). |

## (c) Findings

1. Six test files: 9 deletions are wrong, and 1 deletion must be a skip. Severity high. CONFIRMED by the probes of rows 3, 8, 15, 20, 22, 24, 26, 37 and 45. Each menu call lands the old row or meets a refusal that the menu form keeps. The files are frame234 (4 re-pins, 1 skip), f2, frame193, frame258, read_back and seam_night173 (1 re-pin each). Fix: apply the table.
2. rota/roles/api.py:14214, the quote-home check of the menu ruling, for row 16. Severity low. CONFIRMED by probe_a A4. In "Line 2 is wrong, and the software calculates the tip wrong too.", one clause names line 2 only. The words fault calculate_tip, line 1, and no number names line 1. `other <quote>` on line 1 meets the naming refusal at 14238. The quote escape takes a quote only from a clause that names no line. Fix: skip the test with the reason "menu_ruling: a quote inside a clause that names another line cannot carry a change of an unnamed line". This gap differs from the `line_words` gap, because no number names line 1.
3. Outside the points. rota/roles/api.py:14214. Severity low. CONFIRMED by probe_b A7. On `_present`, `{"2": "other The rest looks fine.", "3": "rewrite"}` lands calculate_tip contest. The quote escape accepts any clause that names no line, a bare agreement included. The seat brief puts that clause under `rest`, and only the seat's reading guards it. Fix: no change in R6. Design R puts the reading on the seat, so record the risk only.
4. Outside the points. tests/rota/test_frame234_verdict_lines.py:101, `MENU_143_144["143 m263"]`. Severity low. PLAUSIBLE from probe_f A3 and A6. The fixture lands line 1 approve. On this page, `"1": "other Also, take the version ..."` lands the night's contest through the quote escape. The ruled seat can choose either call. Fix: say in the test comment that the night's contest is reachable.

## (d) Probes

Folder: C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/00ca90d0-18a5-4929-b3d3-aedcb3b99ae5/scratchpad/p15c/

- old_bodies.py prints an old test body at f52c2716. It is the p15b script, pointed at D:/repos/rota.
- probe_a.py runs `page_clauses` and the menu calls on `_present`, `_request_page` and `_page11` for the frame234 rows.
- probe_b.py runs the `add` calls, the bare agreement, the `ask` and `words` keys, `acts=`, and the frame305 note line.
- probe_f.py runs the `other <quote>` calls for rows 13, 15 and 22.
- test_probe_c.py runs night 174 m55 (the first shape is refused), frame258 row 26, and `_page11` row 24.
- test_probe_d.py runs the read-back rows key, the `misread` rows call, and the full m55 call.
- test_probe_e.py runs the frame258 request-word quote on line 1.
- The worktree is C:/Users/roman/rota_p15c, detached at r6root (4f824369), with cassettes.db copied in. No tracked file changed. No live model and no gate ran.

## (e) Usage

The harness shows no exact split. The estimate is about 45k context tokens and 13k output tokens, about 58k in total. The total is above the cap of 45k. Sub-agents: none.
