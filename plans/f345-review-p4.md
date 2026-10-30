# Frame 345, review p4: commits 27291602, 1eb5c557 and 8960b6d3 on seam2root (parent 7df90d09)

Verdict: READY. The p3 high findings are closed. The four findings below are low, and none blocks the land.

## (a) Verdict on each point

1. CLOSED. The match binds a number only as its clause's subject. The carry holds inside one sentence. Probe p1 shows the three p3 replies bound right, and the two path lines have their words. Finding 4 stays as the one allowed verdict read.
2. CONFIRMED. The check at api.py 14823 to 14840 reads `match` and `ctx.refusals` only. `_line_reading` keeps four callers below it, all outside the brief (finding 2).
3. CONFIRMED. An approve on a no-words read-back line is refused once. The log shows 9 such refusals, one turn each (finding 1).
4. CONFIRMED with one open sentence. 41 lines. Examples: revise line 16, rewrite line 18, now line 23. The `remove` sentence still differs from the code (finding 3).
5. CONFIRMED. 180 passed, 7 xfailed in 47.90s. Ten deleted tests, each pins a removed behaviour (section b, tests).
6. NO CONTRADICTION. All 12 cases are stale, because the prompt changed. Two expectations depend on the `words` column (finding 4).
7. OUTSIDE. The diff touches no file the briefs did not order. One match miss on n175-m121-m122 (finding 5).

## (b) Findings

1. rota/roles/api.py 14830 to 14840 and `_no_words_refusal` 13546. Low. CONFIRMED. On a read-back line, the check refuses every ruling except `absent`, `approve` included. The sentence then offers "approve or leave out line N". The log holds 9 refusals on line 4 of n175-m44-m45 and n175-m44-m46, the read-back line, at turn 1 of 9 runs. Each costs one turn. Fix: on a read-back line, let the sentence say "leave out line N" only, or let `approve` pass.
2. rota/roles/api.py 14813 to 14815, 14871, 14906, 14938, 14994. Low. CONFIRMED by code read. `words_reading` still feeds the merged-change door, the naming door of frame 337, the item-contest cancel and `_faulted_approve`. The brief keeps all four out of this pass. Fix: none now. Name them in the next pass's brief.
3. rota/roles/prompts/liaison/landing.md 19 against `_WORD_KINDS` 11608. Low. PLAUSIBLE. The prompt says `remove` on a page line "is a drop of that line". The code writes act `remove`, kind `row`, and `RULED_ACTS` (principal.py 1019) lists `remove` and `drop` apart. The three l1 drop cases exclude `"act": "remove"`, so the seat must say `drop`. Fix: fold `remove` to `drop` in `WORD_ACTS` when the line is not a guess or a batch row, or change the sentence to "say `drop`".
4. tests/rota/cases/l1_landing.yaml 59 and 348. Low. PLAUSIBLE. `text_includes` 'list of dishes' and 'separate request' read the `rulings` write. Its `words` column is the seat's `words` argument (api.py 14410), which the one-word form no longer asks for. The per_item verdicts hold, because 14475 folds `drop` to `contest` before 14521 stores it. Fix: re-record the 12 cases live after the land and drop the two words expectations if they fail.
5. Outside. rota/roles/api.py `_subject_lines` through `line_words` 13495. Low. CONFIRMED by probe p1. In n175-m121-m122, "change only the docstring in the file on line 9" gives line 9 no words. The log shows 3 refusals on line 9. The case expects `approve`, so the refusal points the seat right. Fix: none now. Record the miss as a cost of the subject rule.

Tests deleted, 10: `test_a_later_with_his_words_in_acts_gets_the_call_with_his_reply`, `test_a_keep_in_acts_on_the_shift_page_is_named_and_left_out`, `test_a_seat_verdict_against_his_shift_word_gets_no_call`, `test_s271s_acts_call_lands_on_his_reply`, `test_s275s_acts_call_lands_on_his_reply`, `test_the_object_form_and_the_flat_form_write_the_same_rows` and `test_a_ref_on_two_lines_takes_either_key_in_acts` pin the `acts` map, the flat form or the shift door, which pass 1 removes on purpose. Three are renamed to the object form. `test_an_acts_entrys_words_outside_his_reply_are_refused` pins a guard on seat words, which code now copies. `test_s120s_call_3_revise_of_c_3_is_refused` and `test_a_negated_change_verb_backs_no_revise` pin the revise cue door, which pass 2c deletes on purpose.

## (c) Probes

- p1: C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0ce92518-cd4c-46c5-8db2-374566fad335/scratchpad/p4_lw2.py ran `line_words` on eight l3_rulings replies and printed each line's words.
- p2: grep on seam2c_after.txt for "no words of his name": 12 hits, lines 50 to 189, and the log around n175-m44-m45.
- p3: the five test files in replay, ROTA_MODEL=qwen3:8b, ROTA_L1 unset: 180 passed, 7 xfailed.
- p4: `git diff 7df90d09..8960b6d3` for the stat, the deleted test names and the three prompt files.
- p5: awk reads of api.py 13458 to 13547, 14790 to 14860, 14865 to 15000, 11600 to 11640, and of principal.py 3622 to 3650.

## (d) Usage

Input tokens: about 36k. Output tokens: about 5k. Total: about 41k.
