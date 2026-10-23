# Frame 308, review 4: the per-criterion reading at 32c1f02f

Reviewer on Opus, read-only, in `C:/Users/roman/rota_r308` at 32c1f02f. No gate, no re-record. Night databases opened with `?mode=ro`.

## Verdict

Accept 32c1f02f for the mechanism, with one high finding to fix before the branch. The record path maps each criterion to the line he saw. The sentence split on ":" moves a line's body away from its line reference, so one line's words reach every other criterion. The eight changed tests keep the one-answer rule but decide the `drop` shape, which the Ends-when gives to frame 192. The door was right to stay silent on s136.

## (a) The points

1. The map: CONFIRMED right on the record. The fallback gives the right lines for m116 at night 159's end state, and wrong lines where rows moved (m98).
2. The eight tests: they keep the one-answer rule and bend the drop rule. A rewrite of a dropped line is frame 192's question, and the tests now assert it as the right path.
3. "has to change": 35 of 933 rulings rows of nights 140 to 159 move from no-words-fault to words-fault. No row moves the other way. One match is a negated removal.
4. s136: the door is silent by design. `ruling_asks_no_new_words` is True for `echo_json_helper`, `rota/core/sandbox.py:1608`. No fix.
5. The second `_CHECK_FAULT` branch: no finding. The branch adds the answer route only, and the answer door needs every ruled criterion in that answer anyway.

## Point 1, the map

- `principal.land` writes `order:<reply>` from `Ask.order`, and `open_asks` sets `Ask.order` from the second value of `render_page` (`rota/roles/principal.py:199`, `1900-1902`). `numbered` appends every numbered row, so the `guess:` row and the ledger note hold their own lines.
- Probe p1 built the 14 lines of m116 (request, `guess:`, cr_1 to cr_6, how_it_works, bg_2_summary, three description rows, `l_e6df5e65b3`) as `order:m117`. With the words of m117, "Line 7 should go" reaches cr_5 (line 7) only, "Lines 3, 4 and 6 are off" reaches cr_1, cr_2 and cr_4, and "line 14" reaches the ledger note. Each criterion gets the line he saw.
- The fallback `_page_order` on `clickI_night159.db` returns the same 14 rows in the same order for m116 at the end of the night. For m116 the fallback is right. For m89 at m98 it is wrong (cr_2 on line 3), as the pass's own test shows.
- Nights 158 and 159 hold 0 `order:` rows. The wake count of 10, 0 and 5 therefore ran on the fallback only. Night 160's `clickI.db` holds `order:m35`, so the record path is live from night 160.

## Point 2, the eight tests

- m98 says "Drop line 5" for cr_3. The Ends-when of the frame says: "the cr_3 `drop` shape goes to frame 192 as a case". Frame 192 maps a drop to `contest`, and the owner amends.
- The Terminologist has no op that retires a criterion. `criteria.respecify` is its only write. So the door can only ask for new words, and `_land_cr3` lands a rewrite that keeps cr_3 alive with other text.
- Seven tests now call `_land_cr3` first, and the pass-2 test asserts "No respecify of cr_3 has landed". These keep the rule of the frame: one answer carries every ruled criterion. They also assert that a rewrite is the right answer to a drop. That is the decision of frame 192, made here by the only write the code has.
- A rewrite of a line he dropped is the shape frame 306 counts: a merged change that holds a line his words refused. Before pass 3, cr_3 counted as standing, which was also wrong.

## Point 3, `_WORDS_FAULT` over nights 140 to 159

Probe p3 took the regex at 695e8be7 from `git show` and compared it with the regex at 32c1f02f on every `rulings.words`. 933 rows, 35 change side, all from False to True. Pairs with the same words count twice.

- n140: r_4dfcbd586b "Line 3 should go back to how you had it", r_m148 and r_0335c737a2 "remove line 3".
- n142: r_m37 and r_c41ec12f53 "drop lines 3 and 4", r_m126 "change line 2", r_m139 and r_4aa9ef5962 "drop line 13", r_m144 and r_9676ff6676 "Do not remove lines 8 to 14 as a block" (negated, his words use the contraction).
- n143: r_0d799dbe7b "drop line 6", r_315669e21d and r_614273c9e6 "remove lines 2 to 8", r_4c53628c13 "drop lines 1 and 2".
- n144: r_77986256f3, r_6106f75a03 and r_5d7f7fadba "drop lines 2 to 8", r_e4117a0553, r_m56 and r_0437afee08 "drop lines 2 to 5", r_m124 and r_c692d1f1f5 "remove line 10".
- n152: r_6196cdc9cc "Change line 5", r_97255ac8d5 "replace line 2".
- n154: r_bfed1d4d86 "delete line 5".
- n155: r_m59, r_2a7d2e4710, r_m86 and r_1e779a59e2 "rewrite lines 3 and 5".
- n157: r_fb0e73c536 "Replace line 4", r_034e661dbc "Delete line 7", r_f117dc206e "remove line 4".
- n158: r_ce163d8060 "Drop line 5".
- n159: r_84b69b4f0d "line 7 should go", r_9f4774a407 "rewrite line 3", r_e4f88a83f2 "remove lines 7 and 8".

The "has to change" branch alone moves no row of these nights. Its only case is m224 of night 159.

## Point 4, s136 of night 160

Probe p4 replayed s136 on an in-memory copy of `clickI.db`.

- s136 is a Terminologist in mode `normal`, woken by m37, a `relay` from the Liaison with refs `["echo_json_helper"]`. `_principal_relay` returns `(['echo_json_helper'], {'echo_json_helper': 'contest'})`, so the relay kind is read.
- The words of r_401e577391: "Line 2's check is wrong ... Please fix the test so it accepts that one trailing newline, and keep the code as it is." `order:m35` puts `echo_json_helper` on line 2.
- The respecify refusal ("is not a symbol the index knows") carries no `criterion_stands` flag, and `ctx.writes` stays empty. The door does not key on that text.
- `ruling_asks_no_new_words(ctx, 'echo_json_helper')` is True: a check fault, no words fault, and the text unchanged. So `unwritten` is empty at `rota/core/sandbox.py:1605-1610`, `missing` is empty, and the door returns None at line 1615.
- The silence is right. He faulted the test and not the criterion. The answer carries the criterion as it stands. No fix.

## Point 5, the second `_CHECK_FAULT` branch

`rota/roles/api.py:5904` tests the whole words. The branch runs only when the per-criterion words fail the stands test. On cr_3 of m98 the per-criterion words hold "Drop line 5" only, and the whole words hold "fix its check" of cr_2. The refusal then says "Write what he asked for" and adds the route to the Tester with cr_3 in refs. The answer door asks for cr_3 in that one answer anyway, so the route is not wrong. With the answer closed, the route is the closed note, which is right too. Not a finding.

## (b) Findings

1. `rota/roles/api.py:9752` (`_SENTENCE`, used by `_ruling_words_on` at about line 5739). High. CONFIRMED. The split on ":" and ";" cuts "Line 3: fix its check. Line 4: it should say aborts." into a label and a body. The body names no line, so it reaches every criterion. Probe p1: cr_1 on line 3 reads words-fault True from the "should say" of line 4. The door then asks new words of a criterion whose check alone he faulted. Night 157's r_4a62d8a771 has the shape: the "change its check" of line 3 reaches crit_show_python_version on line 5. Its side stays right there by chance. 4 rulings of nights 140 to 160 use "line N:". Fix: in `_ruling_words_on`, split on sentence ends only, or join a fragment that is only a line reference to the next fragment.
2. `tests/rota/test_frame308_ruling_answer.py` (`_land_cr3`, its seven callers, and the pass-2 assertion at about line 261). High. PLAUSIBLE: the Ends-when gives the drop shape to frame 192, and the tests assert a rewrite of a dropped line as the right path. Fix: mark the cr_3 expectation as the case of frame 192, with an xfail or a comment that names frame 192, and do not assert the rewrite as the outcome.
3. `rota/roles/api.py:5408-5413` (`_WORDS_FAULT`). Low. CONFIRMED. The pattern has no negation guard. Night 142's r_m144 "Don't remove lines 8 to 14 as a block" matches. Per criterion, lines 9 to 14 then read as asking new words. In probe p1 the negated shape reads cr_1 "Line 3 is fine, fix its check" as words-fault True. Fix: drop a match that `_NEGATED` precedes, as the line reader does.
4. The count of pass 3. Low. CONFIRMED. Nights 158 and 159 hold no `order:` rows, so the count of 10, 0 and 5 measures the fallback only. Fix: count the record path on night 160's `clickI.db` after the night ends.

Outside the points: the m117 sentence "The line 8 check needs prompt text" gives `_CHECK_FAULT` False for cr_6. The same is true at 695e8be7, so it is not a change of this pass.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/8e879083-89bd-4f17-a62c-8f59f02dd210/scratchpad/r4/`.

- `p1_map.py`: an in-memory database with `rulings`, `messages` and `config`, the 14 lines of m116 as `order:m117`, the words of m117, the colon shape, the negated shape, and m98 on the page of the frame test. It also ran `_page_order` on m116 of `clickI_night159.db`.
- `p3_words.py`: the regex at 695e8be7 from `git show` against the regex at 32c1f02f, over every `rulings.words` of `clickI_night140.db` to `clickI_night159.db`.
- `p4_s136.py` with `helpers.py` (the head of `replay308_wake.py`, pointed at `rota_r308`): replays the calls of s136 on a copy of `clickI.db`. It prints the relay, the ruling, the record, `ruling_asks_no_new_words` and the return of the door.
- Inline: a count of "line N:" rulings over nights 140 to 160, and `_ruling_words_on` on night 157's r_4a62d8a771.

## (d) Usage

About 80k tokens in total, measured from the session budget. This is over the cap of 30k. The split into input and output tokens is not available. No sub-agent ran.
