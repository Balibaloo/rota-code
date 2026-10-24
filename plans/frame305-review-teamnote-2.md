Stands. The five findings of review 1 are repaired. Four new findings are low, and none lands a ruling against his words.

# Frame 305, review 2 of the team-note case

The review read d8abe2b6 on dcf7a6e3 and 52fe49e1 in `C:/Users/roman/rota_p305b`. The reviewer edited no tracked file. Three test files pass: 129 passed, 4 xfailed.

## (a) Verdicts by point

1. Holds. The keep door at api.py 11575 to 11577 counts an admitted note revise as a contest. "Line 11 is fine, so use click directly in the test." now refuses the revise and the contest with the same text. Review 1's probe "Leave line 11 as it is." refuses the revise, but the note door at 11392 refuses it first. See finding 1.
2. Holds for the three named cases. m11 and m45 return None, and s357's "On line 11, use the normal test runner" lands as revise. A fault with a change in one comma clause no longer lands. See finding 2.
3. Holds. The drop pattern has no "not needed" and no "don't need". A drop word after "say" or "reads" is new text. The own test compares whole words, and "Remove line 11." on a note that holds "removed" is a drop.
4. Holds. The refusal says "name line 11 by number and say the change" and keeps the request pointer. The "own" refusal at 11417 still lacks the by-number rule. See finding 4.
5. Fails in part. The "Line N is ..." skip hides "Line 11 is wrong, use click directly in the test." The older code admitted this sentence. See finding 2.
6. Untouched. The range 52fe49e1 to d8abe2b6 has four api.py hunks, at 11058, 11384, 11408 and 11569. `_KEEP_CHANGE` (10698), `_names_request` (10837) and frame 201's hold have no change. The diff has no CR byte.

## (b) Findings

1. tests/rota/test_frame305_note_revise.py 119 to 123. Severity low. CONFIRMED. The keep test passes on the note door at api.py 11392, not on the keep door. `_note_words` returns None for "Leave line 11 as it is.", so the new clause at 11577 never runs in the test. No test runs the keep door with a revise.
   Fix: add the case "Line 11 is fine, so use click directly in the test." with revise, and assert the keep refusal text.

2. api.py 11120 to 11124 and 11112. Severity low. CONFIRMED. Real change sentences return None and the door refuses the revise:
   - "Line 11 is wrong, use click directly in the test." The skip for "is" now needs a modal, and `_CUE_FAULT` no longer counts. dcf7a6e3 admitted the sentence.
   - "Line 11 is confusing, rewrite it to use click directly." `_NOTE_NO_CHANGE` matches "confus".
   - "On line 11, make sure the flag stays off." and "Line 11 should say the API is unchanged." `_NOTE_NO_CHANGE` matches "stays" and "unchanged".
   - "On line 11, fix the failing test by using click directly." and "On line 11, try again with click directly." `_CUE_KEEP` matches. Line 11 of s357 is a note about a failing test.
   Night 161 m218 holds the shape "should also check that the version message stays exactly as it is today" about line 7. The cost is a refused call, not a wrong landing.
   Fix: skip a clause on a no-change cue only when it holds no `_NOTE_CHANGE` verb, and keep `_CUE_FAULT` in the "is" skip when a change verb follows.

3. api.py 11079 and 11124. Severity low. CONFIRMED. "I agree with line 11, they should run it as planned." returns "change", and the door admits the revise. The note then closes as overruled. The contest door admits the same words, so the fault is not new.
   Fix: skip a clause with `_CUE_AGREE` and no fault cue before the change test, as dcf7a6e3 did.

4. api.py 11414 to 11419 and the keep refusal. Severity low. CONFIRMED by reading and by probe. The "own" refusal says "revise it on words that say the change" with no by-number rule. The keep door refuses a revise with "a contest reverses the principal". The Liaison reads a contest word for a revise call.
   Fix: give the "own" text the by-number rule, and name the ruled verb in the keep refusal.

5. Outside the points. api.py 11110. Severity low. CONFIRMED. "Line 11 says the wrong thing, delete it." returns None, because "says" stands before "delete". The refusal then offers both routes for a plain drop.
   Fix: suppress a drop word only when "say" follows a modal such as "should" in the same clause.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/51917779-9e71-4bcd-b8e5-e5cbc8b1f811/scratchpad/`. Each one ran from the worktree root.

- `r305/probe_door.py` (review 1): revise and contest on four sentences. Every revise is refused.
- `r305/probe_cases.py` (review 1): `_note_words` on nine sentences and two notes. Results match points 2 and 3.
- `r305/probe_words.py` (review 1): `_note_words` on nights 160 and 161. m11 and m45 return None. s357's m191 and m218 return "change" on line 11.
- `r305b/probe_words2.py`: `_note_words` on 17 edge sentences. Source of findings 2, 3 and 5.
- `r305b/probe_door2.py`: `rulings.rule` with revise and contest on seven sentences. Source of points 1 and 5.
- `git diff 52fe49e1 d8abe2b6`: hunk headers, the three names, CR count 0.
- `pytest tests/rota/test_frame305_note_revise.py tests/rota/test_frame296_revise_note_text.py tests/rota/test_request_page.py`: 129 passed, 4 xfailed.

## (d) Usage

Input tokens about 45k. Output tokens about 6k. Total about 51k. The harness gave no exact count.
