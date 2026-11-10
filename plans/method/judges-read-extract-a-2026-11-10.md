# The read of the judges, extract part a, 2026-11-10

Part a holds reviews R1 to R20 of the draw `random.Random(363).sample` and the design reviews D1 to D7. One read-only agent wrote it.

## The limits of this page

- A status line is the session's own account of what it did with a finding. An earlier check found the status lines true and too sure: a doubt or a limit of an agent is often left out.
- A review page is the agent's account. Nobody checked a review against the code in this read.
- 40 of about 359 is one draw. This part holds 20 drawn reviews and 7 design reviews. Read the counts below as one draw, not as a rate.
- One reader and one pass.
- Open no database. This read opened none.

Two notes on the cells, from this reader:

- "Asked by: rule" means that the line matches rule C53 of `plans/method/reference.md` section 6. No asking line in this part names C53 or any rule by its name.
- "Given" comes from the review page and the status line only. This read opened no review brief in a scratchpad.

### R1. plans/f361-review-p1.md
- 1: date 2026-11-03 (commit 09a1fb50); frame 361, passes 1 and 1b, second look on pass 1c; kind: diff review; asked by: rule — "The diff review runs on Opus, cap 60k, eight points, on rota_r361 at 6447973d, to plans/f361-review-p1.md." (stack.md 2106, status 2026-11-03 01:51)
- 2: diff yes; brief yes (eight points); frame line not found; goal of the frame yes ("The code does what the ruling asks", page line 3); destination not found (page, stack.md 2106)
- 3: 9 findings (8 in the first look, 1 new in the second look)
  - F1 [scale: function-file] 38 tests red in four files the pass never ran -> next: repaired (status 2026-11-03 02:17, pass 1c "the four red files pin eager")
  - F2 [scale: function-file] 25 lazy rows can never bind a touch -> next: repaired (pass 1c in part, then pass 1d, status 02:26 "198 wait and 25 bind no code")
  - F3 [scale: function-file] a path with no deeper area binds the root area -> next: no record (the second look says "3. Not fixed"; status 02:26 says "The reviewer's second look had marked findings 3 and 4 fixed". The two records disagree.)
  - F4 [scale: function-file] the first-touch record row lists under `ledger.list(shipped=)` -> next: repaired (in part, second look "Accept"; status 02:26)
  - F5 [scale: function-file] `_why_idle` counts lazy rows -> next: repaired (second look "5. Fixed")
  - F6 [scale: words: an older run database changes to lazy at the upgrade] -> next: set aside, reason (the review: "Fix: no code change"; second look "No change, as recommended")
  - F7 [scale: function-file] an empty string reads two ways -> next: repaired (second look "7. Fixed")
  - F8 [scale: line-value] 240 refs for 223 ids -> next: repaired (status 02:17 "223 refs with no duplicates")
  - F9 [scale: function-file] the empty-value rule changes `onboarding_phases` and `runner` -> next: repaired (status 02:26 "the empty rule covers the election only")
- 4: verdict: "Verdict: fix. The code does what the ruling asks. The default moves 38 tests to red, and the implementer ran none of those files." Second look: "Verdict: fix. Five findings are fixed, two are partly fixed, and one is not fixed."
- 6: none
- 7: no — dry run 4 (status 2026-11-03 07:32, `plans/dry4-read-2026-11-03.md` line 73) names "m40's touch note carried no first-touch block". The read calls it "the one-tick window that frame 361 accepted", which the review named outside its points ("the race of the report's Q3").

### R2. plans/f20-review-p1.md
- 1: date 2026-10-27 (commit ec5010b8); frame 344's audit, fix F20 with F21, pass 1 (the status lines sit under frame 330's heading, `plans/archive/stack-2026-11-02.md` 109 to 110); kind: diff review; asked by: rule — "The review runs on Opus, cap 50k, to plans/f20-review-p1.md." (status 2026-10-27 15:22)
- 2: diff yes; brief yes (six points); frame line not found; goal of the frame yes (finding 1 reads the night 170 end that "the audit counts ... as F20 night evidence"); destination not found (page)
- 3: 6 findings
  - F1 [scale: frame] only a commit or a moved check of b_3 lifts the key, so the commit does not change night 170's end -> next: repaired (status 15:44, pass 1b "s217's touch write lifts tester|tick:tests_missing|b_3")
  - F2 [scale: line-value] a fallback phrase with no verb -> next: repaired (status 15:44 "the five low findings fixed")
  - F3 [scale: line-value] ledger ids on an agenda line -> next: repaired (same line)
  - F4 [scale: line-value] the subject comes twice -> next: repaired (same line)
  - F5 [scale: function-file] four deletes outside `lift_keys` with a LIKE wildcard -> next: repaired (same line)
  - F6 [scale: function-file] `invariants.i6` parses keys by its own rule -> next: repaired (same line)
- 4: verdict: "Verdict: the reader and the lift hold. One high finding is about scope, and five low findings are about words and stray deletes."
- 6: F1: "So this commit does not change the end of night 170. The audit counts that end as F20 night evidence." The session's next line (15:27): "Pass 1b on the same implementer, cap 60k: a key lifts when a row its seat reads for the subject moves, the touch list, a criterion of the batch, a landed ruling on its rows; the five low with it."
- 7: yes — status 2026-10-27 19:43 (archive stack-2026-10-30.md 204): "F20 with F21 PARTIAL, two own-rule reads unnamed, render_state principal.py:396 and parked scheduler.py:2349". Status 2026-10-30 14:42 (stack.md 2998): "loop.step at loop.py 336 marks quarantined keys by its own query". The review named neither `render_state` nor `parked`.

### R3. plans/frame303-review-1.md
- 1: date 2026-10-23 (commit fb2bceb4); frame 303, pass 1; kind: diff review; asked by: rule — "Review 1 runs on Opus in C:/Users/roman/rota_r303, the three admitted causes first." (stack.md 5537, status 2026-10-23 14:37)
- 2: diff yes; brief yes (six points, "the three admitted causes first"); frame line not found; goal of the frame yes (unasked request items on nights 150 to 158, page verdict); destination not found (page, stack.md 5537)
- 3: 6 findings
  - F1 (H1) [scale: function-file] a team-seat propose that refs a statement passes `_principal_cause` -> next: repaired (status 15:13, pass 1b "a cause counts only when the trigger comes from the Liaison or the principal")
  - F2 (M2) [scale: function-file] the case L1-VK-answer-a-refactor-proposal contradicts the brief -> next: repaired (status 15:13)
  - F3 (M3) [scale: approach] two admitted causes exist only for test fixtures, the pass's deviation -> next: repaired (status 15:13 "the verb-only deliver cause and the no-record guard are gone, 20 fixtures repaired")
  - F4 (L4) [scale: function-file] the entries branch has no record that needs it -> next: repaired (status 15:13 "an entries ref only on a Liaison relay")
  - F5 (L5) [scale: function-file] any report answers the proposal -> next: set aside, no reason (status 15:02 sends "H1, M2, M3 and L4" only; the review itself says "Fix: none now")
  - F6 (L6) [scale: function-file] the propose mode still offers `problem.assert` -> next: set aside, no reason (status 15:02)
- 4: verdict: "Accept for the night."
- 6: none
- 7: not sure — the case of 2026-10-24 15:42 (stack.md 5545) reads a textless propose again on night 162, with the cause in `_resolve_refs` of `rota/core/runner.py`, not in the door that the review read. Searched: `_principal_cause`, "textless propose", "team rows under".

### R4. plans/f356-review-p3.md
- 1: date 2026-11-01 (commit e77d703b); frame 356, pass 3; kind: diff review; asked by: rule — "Review p3 of 584f7f91 runs on the worktree, cap 25k, from f356_review_p3_brief.md in this session's scratchpad." (archive stack-2026-11-01.md 128, status 09:23)
- 2: diff yes; brief yes (six points); frame line not found; goal of the frame not found; destination not found (page)
- 3: 3 findings
  - F1 [scale: function-file] the class reader misses a tab-indented body -> next: set aside, reason (status 09:30 "residue unless a live case shows them"; Closed line 18:25 "Residue: review p3's three lows")
  - F2 [scale: function-file] a class header with a deeper continuation line gives no grain -> next: set aside, reason (same lines)
  - F3 [scale: line-value] the repair refusal says "nothing in the worktree defines it" where the check reads the index -> next: set aside, reason (same lines)
- 4: verdict: "Verdict: the claim holds on dry1's copy and the real click source. The review has 0 high and 3 low findings."
- 6: none
- 7: no — searched `_class_defines`, `_dotted_rows`, "nothing in the worktree defines", "tab-indented" in the stack and its archives after 2026-11-01. No later record.

### R5. plans/frame204-review-1b.md
- 1: date 2026-10-11 (commit 6663f6e6f); frame 204, pass 1b, the second look; kind: diff review; asked by: rule — "The second look runs now on Opus, cap 50k, `rota_rv204` at 6307f965, report to `plans/frame204-review-1b.md`." (stack.md 3118, status 2026-10-11 17:41)
- 2: diff yes; brief yes (the seven findings of review 1, four points); frame line not found; goal of the frame not found; destination not found (page)
- 3: 1 finding
  - F1 (N1) [scale: function-file] `fill_kinds` renders the slot in 24 modes that do not offer `ledger.log` -> next: repaired (status 17:53, pass 1c "`fill_kinds` drops the slot's sentence when the mode's tools exclude `ledger.log`")
- 4: verdict: "STANDS: 7 of 7 findings fixed, 0 high, 1 low new (N1), 34 cases newly stale."
- 6: none
- 7: yes — the gate of 2026-10-12 02:50 (stack.md 3123): "Pass 1 does not hold yet: five seats changed behaviour under the pass's brief text". The read of 02:57 (stack.md 3124): "three drops are pass 1b's own sentences". The review counted 34 stale cases and said the text-protocol line "costs nothing". It named no change of seat behaviour. The frame is parked.

### R6. plans/f344-review-p1.md
- 1: date 2026-10-30 (commit 6f190e5d); frame 344, the Critic's review loop (sprint 35 row 4), pass 1 with re-checks p1b and p1c; kind: diff review; asked by: rule — "Review p1 runs on Opus, cap 40k, to plans/f344-review-p1.md, with the tail's reach and the 19 stale Developer cases as its questions" (archive stack-2026-10-30.md 407, status 2026-10-29 11:17)
- 2: diff yes; brief yes (eight points); frame line not found; goal of the frame not found; destination not found (page, status 11:17)
- 3: 10 findings (7 in p1, 1 in p1b, 2 in p1c)
  - F1 [scale: function-file] the kept route admits a header, a brace, a fragment and prose -> next: repaired (status 14:03, pass 2)
  - F2 [scale: function-file] `_review_pending_line` fires while another test failed at an older commit -> next: repaired (status 14:03)
  - F3 [scale: function-file] the new case accepts one valid route only -> next: repaired (status 14:03)
  - F4 [scale: function-file] the test route ignores the run's commit -> next: repaired (status 14:03)
  - F5 [scale: function-file] `_fail_tail` sits on 8 refusals where 2 need it -> next: repaired (status 14:03)
  - F6 [scale: line-value] `answer.md` lines 20 to 21 say added lines only -> next: repaired (status 14:03)
  - F7 [scale: words: the cause of 19 stale Developer cases] -> next: repaired (status 14:03 "the 14 Developer cases were stale before either pass")
  - F8 [scale: line-value] p1b residual, `kept: d = {` passes -> next: set aside, no reason (named in the land line 14:05; the review says "does not block the land")
  - F9 [scale: line-value] p1c, one sentence of about 47 words -> next: repaired (status 15:52, pass 3c "one sentence each, 20 and 18 words")
  - F10 [scale: approach] p1c, the encoding rule holds in the prompt only, the door does not check it -> next: set aside, reason (status 15:26 "no door reads a criterion's meaning")
- 4: verdict: "Verdict: NOT READY. The review has 2 high findings and 5 low findings." p1b: "Verdict: READY for the land." p1c: "Verdict: NOT READY for the land, on point 1 only."
- 6: none
- 7: no — the Critic read of 2026-11-08 08:15 (stack.md 2173) says "the verdict door's test route needs only a test that is bound, live and passed at head". The review named this as F10 in p1c.

### R7. plans/f345-review-p15c.md
- 1: date 2026-10-30 (commit e93af473); frame 345, pass R6 (the 45 remaining deletions after R6b); kind: other: a read-only classification of deletions; asked by: own choice — "Judged: two sampled reviews found 4 wrong in 27 and the implementer's own audit 10 in 42, so its deletion judgement does not converge. A read-only reviewer now classifies all 45 remaining deletions" (archive stack-2026-10-30.md 134, status 10:16)
- 2: diff yes (`git diff f52c2716 r6root -- tests`); brief yes (three points); frame line not found; goal of the frame not found; destination not found (page)
- 3: 4 findings
  - F1 [scale: function-file] 9 deletions wrong and 1 must be a skip, in six test files -> next: repaired (status 10:46, "66 re-pinned, 35 deleted, 14 skipped")
  - F2 [scale: function-file] the quote-home check of `menu_ruling` at api.py:14214 -> next: owed (Closed line 10:46 "a quote in a clause that names another line" is a gap "for the next frame")
  - F3 [scale: function-file] the quote escape accepts a bare agreement -> next: no record
  - F4 [scale: function-file] a fixture comment on the reachable contest -> next: no record
- 4: verdict: "Counts: 35 delete, 9 re-pin, 1 skip, 45 in total."
- 6: none
- 7: no — searched "quote escape", "bare agreement", "quote-home", `menu_ruling` in the stack and archives after 2026-10-30. No later record names these sites.

### R8. plans/frame298-review-5.md
- 1: date 2026-10-18 (commit ad77deae); frame 298, pass 5, with a re-run at pass 5b; kind: diff review; asked by: rule — "review 5 runs on Opus, cap 50k, four points, to `plans/frame298-review-5.md`." (archive stack-2026-10-21.md 144, status 16:12)
- 2: diff yes; brief yes (four points); frame line not found; goal of the frame not found; destination not found (page)
- 3: 3 findings
  - F1 [scale: function-file] "nothing to do with" disputes the paths of a kept clause, `runner.py` 1813 to 1866 -> next: repaired (status 16:29, pass 5b)
  - F2 [scale: function-file] an "or" list names its first member by luck, `_TEST_FILE_LIST` -> next: repaired (status 16:29 "a test-file list takes 'or'")
  - F3 [scale: words: older than the frame, m160, m172 and m188 dispute two kept paths] -> next: set aside, reason (status 16:31 "outside and older than this frame")
- 4: verdict: "Verdict: points 2, 3 and 4 hold. Point 1 fails with one high finding." At d2e85f79: "Verdict: pass 5b closes finding 1 and finding 2."
- 6: none
- 7: no — searched `disputed_paths` and "nothing to do with" after the close of 2026-10-21. No later record.

### R9. plans/ladder-review-2026-10-15.md
- 1: date 2026-10-15 (commit e11dde47); frame 243, before pass 1; kind: rule review (the ladder block of CLAUDE.md, with frame 243's design); asked by: Roman — "Im not sure, this is important, ask a fable agent to review this" (2026-10-15 01:57, `plans/frame287-roman-words.md` 313 to 315)
- 2: diff no (the block at commit 6df77bcc); brief yes (`ladder_review_brief.md`); frame line yes (stack frames 243 and 250 in the ground read); goal of the frame yes (`plans/frame243-scope.md`); destination yes (`plans/composition.md` in the ground read) (page lines 3 to 12)
- 3: 9 findings
  - F1 [scale: words: the method rule above all frames] three kinds of change are not on the ladder -> next: repaired (commit e11dde47, the block's rungs 3 to 5)
  - F2 [scale: words: the method rule] rungs 1 and 2 are one kind, rung 6 is three, "cheapest first" fails on the actuals -> next: repaired (commit e11dde47, "by the loop each one shortens")
  - F3 [scale: words: the method rule] the overfit test checks a wording where a count decides -> next: repaired (commit e11dde47; status 02:05)
  - F4 [scale: words: the method rule] the placement rule fails on frame 234 and s188 -> next: repaired (status 02:05)
  - F5 [scale: frame] frame 243's new design is a word rule in another coat -> next: repaired (status 02:05 "the respecify rule is dropped")
  - F6 [scale: words: the method rule] "A prediction never gates" is left out -> next: repaired (status 02:05 "The review's block replaces the ladder")
  - F7 [scale: words: the method rule] "The tool never rules for the Principal" is left out -> next: repaired (same line)
  - F8 [scale: words: the method rule] "A capability is judged by the loop it shortens" is left out -> next: repaired (same line)
  - F9 [scale: words: the method rule] "Nothing stops quietly" is left out -> next: repaired (same line)
- 4: verdict: "The list of kinds is close to complete and the ruling behind it is right. The two rules under the list are wrong in the way that matters."
- 6: F5: "Frame 243's new design is a word rule in another coat, placed on rung 4 by the stack". The session's next line (stack.md 2880, 02:05): "Decided here: pass 1 is the supersede door, rung 1, and the record shape, rung 5: the wake prompt of a Developer and a Tester on a criterion carries the words of every contest ruling on that criterion beside its text; the respecify rule is dropped."
- 7: not sure — Roman, 2026-10-15 02:19 and 02:21 (W, 568 to 570): "But anyways, this wall ladder is not sound." and "Ok so the ladder needs design and review passes itself". His words name no place that the review did not name.

### R10. plans/frame257-review-1.md
- 1: date 2026-10-24 (commit 3d3f1f2c); frame 257, passes 1 and 1b; kind: diff review; asked by: rule — "Priced 2 cycles, about 60k on Opus and a review." (archive stack-2026-10-24.md 171, status 2026-10-23 20:44). No line names the review before its result.
- 2: diff yes; brief yes (five points); frame line not found; goal of the frame yes (point 2, the count over nights 140 to 159); destination not found (page)
- 3: 6 findings
  - F1 [scale: line-value] the pass report's line on 6 same-text repeats is wrong -> next: repaired (status 01:18 "the pass report's 'OK' labels were its parser's error")
  - F2 [scale: line-value] the count is 52 to 54, not 54 -> next: repaired (status 01:18 "52 to 54 of 54 by the review's replay")
  - F3 [scale: function-file] the `night` parameter of a test is unused -> next: no record
  - F4 [scale: line-value] the `NATURAL_KEYS` description -> next: no record
  - F5 [scale: line-value] provenance findings 2 and 3 not in the commit -> next: no record
  - F6 [scale: function-file] the near-duplicate block names the seat's own id -> next: no record (the review: "Fix: none in frame 257")
- 4: verdict: "51b29993 goes on the branch after the gate."
- 6: none
- 7: no — sprint row W2 (stack.md 791 to 793), "respecify meets the near-duplicate check", names the block of F6. Review 2 (status 02:48) names faults of pass 1c, a later pass.

### R11. plans/f345-review-p10.md
- 1: date 2026-10-30 (commit 6f190e5d); frame 345, pass R2, with re-check p10b; kind: diff review; asked by: rule — "Review p10 runs on Opus, cap 60k, to plans/f345-review-p10.md: the 120 reds replayed at the parent, each deleted door's callers, a sample of the deleted tests, the mapping that moves the skipped tests, the clarify and shift paths probed." (archive stack-2026-10-30.md 93, status 2026-10-29 15:23)
- 2: diff yes; brief yes (six points); frame line not found; goal of the frame not found; destination not found (page, status 15:23)
- 3: 4 findings
  - F1 [scale: approach] the sort rule of the pass deleted tests that pin landed rows, 6 of 15 sampled -> next: repaired (status 16:38, R2b "the 94 deleted tests read one by one, 15 ... restored")
  - F2 [scale: line-value] the guard lost `(order or refs)` -> next: repaired (status 16:38 "the guard term back")
  - F3 [scale: words: the gate record names a dirty parent] -> next: repaired (status 16:38 "the gate on the clean commit")
  - F4 [scale: function-file] p10b, no menu-form test pins law 6 on seat words -> next: no record
- 4: verdict: "Verdict: NOT READY." p10b: "Verdict: READY for the land."
- 6: none
- 7: not sure — reviews p15 to p15c (status 2026-10-30 09:46 to 10:26) found wrong deletions in pass R6, a later pass on the 116 tests that R2 skipped. These are not the 79 deletions of R2.

### R12. plans/frame266-review-1.md
- 1: date 2026-10-16 (commit 3e5b9c1a); frame 266, pass 1; kind: diff review; asked by: rule — "review 1 runs on Opus from `f266/review1_brief.md`, cap 60k, on `C:/Users/roman/rota_review_266`, to `plans/frame266-review-1.md`" (stack.md 2654, status 2026-10-16 19:05)
- 2: diff yes; brief yes (six points); frame line not found; goal of the frame not found; destination not found (page, stack.md 2654)
- 3: 3 findings
  - F1 [scale: function-file] a parameter name inside a write's source reads as a missing close -> next: repaired (status 19:17, pass 1b)
  - F2 [scale: function-file] a missing quote with no later quote gets the old text -> next: set aside, no reason (status 19:13 "the no-later-quote hole is written, not built")
  - F3 [scale: line-value] the head runs into the next argument -> next: repaired (status 19:17)
- 4: verdict: "Verdict: pass 1b. One high finding blocks the accept."
- 6: none
- 7: yes — night 153, status 2026-10-17 03:39 (stack.md 2667): "a dict value whose inner single-quoted string never closes ... the refusal was the generic text". Night 155 (2026-10-18 01:07) and night 158 (2026-10-21 14:33) show a further shape. Night 152 (2026-10-16 21:48) shows "review 2's known hole", the shape of F2. The frame was validating in these records.

### R13. plans/f354-review-p7.md
- 1: date 2026-11-01 (commit d25e107f); frame 354, pass 8; kind: diff review; asked by: rule — "Review p7 of 1f8e6e1a runs on the worktree, cap 30k, from f354_review_p7_brief.md." (archive stack-2026-11-01.md 81, status 01:56)
- 2: diff yes; brief yes (six points); frame line not found; goal of the frame not found; destination not found (page)
- 3: 5 findings
  - F1 [scale: function-file] the read-back on a stalled step's page says "line 2 runs again" -> next: repaired (status 02:13, pass 9)
  - F2 [scale: line-value] "1: drop" names every line, `_PAIR_WORD` -> next: repaired (status 02:13 "'1: drop' binds line 1 alone")
  - F3 [scale: line-value] "1 drop it 2 ok" gives line 2 no words, `_PAIR_END` -> next: repaired (status 02:13)
  - F4 [scale: function-file] the pair cut in `_clause_tokens` drops a negation -> next: repaired (status 02:13 "a negated pair is not his words")
  - F5 [scale: function-file] a line key on an empty page closes the ask with nothing read back -> next: repaired (status 02:13 "owes one read-back line")
- 4: verdict: "Verdict: the claim holds, with 0 high and 5 low findings."
- 6: none
- 7: no after the close of 2026-11-01 08:28 (searched `_LEAD_VERB`, `_PAIR_WORD`, `_clause_tokens`, `line_words`, "binder" in stack.md). Before the close, review p8 (status 2026-11-01 03:03) found 2 high at the same places: "a drop on a step reads back by the earlier page's line number", and "the negation guard scans the whole clause, so '1 is not right 2 ok' gives line 2 no words, a regression against 1f8e6e1a".

### R14. plans/frame197-review-1.md
- 1: date 2026-10-11 (commit efaa733f); frame 197, pass 1; kind: diff review; asked by: rule — "The review runs on Opus on the worktree `C:/Users/roman/rota_r195p1` at that commit, cap 40k, three points" (archive stack-2026-10-11.md 93, status 07:41)
- 2: diff yes; brief yes (three points); frame line not found; goal of the frame yes ("the night 138 loss the frame fixes", page point 1); destination not found (page)
- 3: 4 findings
  - F1 [scale: line-value] the shown call carries a placeholder for `words` -> next: repaired (status 08:18, pass 1b)
  - F2 [scale: function-file] the offered call is refused next, and the conftest line hides it -> next: repaired (status 08:18 "the conftest line is gone")
  - F3 [scale: line-value] a ref as a key gets no line number -> next: owed (status 08:18 "stay open on this frame for a later pass")
  - F4 [scale: function-file] a bad word before `words` gets the word refusal first -> next: owed (same line, and status 08:32)
- 4: verdict: "One more pass: the shown call becomes the full map with the unnamed lines as approve and the seat's own words, and the KNOWN_REFUSED_OFFERS line goes."
- 6: none
- 7: not sure — the Closed line of 2026-10-11 21:51 names m127, "the Liaison ruled line numbers the page did not have", "for another cause". It names no site. F3 and F4 have no record after the close.

### R15. plans/frame234-review-1.md
- 1: date 2026-10-14 (commit 60a24b7c); frame 234, pass 1; kind: diff review; asked by: rule — "The review of 39e2fba7 runs on Opus, cap 60k, read-only on `rota_rv234`, eight points, no gate, brief `rv234p1_brief.md`" (archive stack-2026-10-15.md 17, status 11:30)
- 2: diff yes; brief yes (eight points); frame line not found; goal of the frame yes (point 1, the four night-146 over-contests); destination not found (page)
- 3: 10 findings (8 numbered, 2 notes outside the points)
  - F1 [scale: function-file] the line-1 refusal misses cues that name line 1 -> next: repaired (status 11:45, pass 1b; review 2 at 11:52 "all eight findings of review 1 fixed")
  - F2 [scale: function-file] the line-1 refusal fires on a correction with no line number -> next: repaired (same lines)
  - F3 [scale: line-value] a match cue before a fault cue wins -> next: repaired (same lines)
  - F4 [scale: line-value] a negated match reads as a match -> next: repaired (same lines)
  - F5 [scale: line-value] the brief line "Line 1 is the request" -> next: repaired (same lines)
  - F6 [scale: line-value] the capture runs into a section header -> next: repaired (same lines)
  - F7 [scale: line-value] a refusal can name no line -> next: repaired (same lines)
  - F8 [scale: function-file] four branches have no test -> next: repaired (same lines)
  - F9 [scale: words: a measurement note on the probe] -> next: no record
  - F10 [scale: words: the order of the gate and the re-record] -> next: repaired (status 12:18, the gate with the re-records)
- 4: verdict: "Verdict: revise. The door refuses the four night-146 over-contests. It also refuses four right verdicts on nights 143 and 144."
- 6: none
- 7: yes — after the close of 2026-10-15 01:16, frame 345's design R "took the meaning doors out as one form" (Closed line 2026-10-30 10:46). `plans/f345-review-p15c.md` deletes tests of `test_frame234_verdict_lines.py` because each "pins the polarity door" or "the cue door". Within the frame, review 3 (status 2026-10-14 19:59) found "one added sentence with no line number ... silences the refusal on m131" at pass 2's door.

### R16. plans/f363-putdown-review-p1b.md
- 1: date 2026-11-10 (commit 66503daa); frame 363, pass 1b of the put-down tool; kind: diff review; asked by: rule — "The diff review of pass 1b runs on one reviewer on Opus, on a worktree at 80a96d7a, to plans/f363-putdown-review-p1b.md: each of the 7 repairs, the bytes on a copy of the real stack again, and any new fault." (stack.md 1799, status 12:12)
- 2: diff yes; brief yes (five points); frame line not found; goal of the frame not found; destination not found (page, stack.md 1799)
- 3: 2 findings
  - F1 [scale: function-file] `open(stack, "wb")` empties the stack before a failed write -> next: owed (status 12:25 "Owed before the first real use, as one small pass 1c, not started")
  - F2 [scale: function-file] a failed archive append leaves part of a block -> next: owed (same line)
- 4: verdict: "Verdict: accept. The seven repairs hold, and the stack bytes are right on every case."
- 6: none
- 7: not searched (a review of the last three days)

### R17. plans/f26-review-p1.md
- 1: date 2026-10-28 (untracked; file date 2026-10-28 02:33; status 02:34); frame 344's audit, fixes F26 and F28, pass 1; kind: diff review; asked by: rule — "Review p1 of F26 with F28 runs on Opus, cap 60k, to plans/f26-review-p1.md." (archive stack-2026-10-30.md 247, status 02:22)
- 2: diff yes; brief yes (eight points); frame line not found; goal of the frame yes (the F28 census on nights 170 and 171); destination not found (page)
- 3: 4 findings
  - F1 [scale: function-file] a gone row makes `rulings_rule` refuse every ruling -> next: repaired (status 02:50, pass 1b "a gone row's line leaves the every-line check")
  - F2 [scale: function-file] the F26 pin lets a bare `"committed": true` reader in -> next: repaired (status 02:50)
  - F3 [scale: function-file] no disagreement test for `land` and `rulings_line` -> next: repaired (status 02:50 "the two disagreement tests added")
  - F4 [scale: function-file] the night report scans `completion` for landed heads -> next: no record
- 4: verdict: "Result: both moves are clean, hold no foreign hunk and stale no recorded case."
- 6: none
- 7: not sure — the Closed line of frame 345 (2026-10-30 10:46) names "menu_ruling and a gone row" as a gap. `menu_ruling` replaced the door that the review read.

### R18. plans/f349-review-p3.md
- 1: date 2026-10-30 (commit 7d7e6687); frame 349, pass 3; kind: diff review; asked by: rule — "Review p3 runs on a reviewer on Opus, cap 30k, worktree at 8585d56f, report plans/f349-review-p3.md." (archive stack-2026-10-30.md 633, status 18:50)
- 2: diff yes; brief yes (four points); frame line not found; goal of the frame not found; destination not found (page)
- 3: 1 finding
  - F1 [scale: function-file] the `schedule.reask` exit refuses in a session that no answer woke -> next: owed (Closed line 18:55 "carried by frame 351 with the bare-name tier"; frame 351 is parked and unclaimed)
- 4: verdict: "Verdict: ready to close."
- 6: none
- 7: no — searched `schedule.reask`, "third-question" after 2026-10-30. No later record.

### R19. plans/f5-review-p1.md
- 1: date 2026-10-28 (commit 3acc2727); frame 344's audit, fix F5, pass 1; kind: diff review; asked by: rule — "The review runs on Opus, cap 70k, to plans/f5-review-p1.md." (archive stack-2026-10-30.md 214, status 00:14)
- 2: diff yes; brief yes (seven points); frame line not found; goal of the frame not found; destination not found (page)
- 3: 5 findings
  - F1 [scale: function-file] `_E_LINE` matches the `[100%]` progress line -> next: repaired (status 00:36, pass 1b)
  - F2 [scale: approach] the chain rule gives the cause, and 175 of 179 chained runs show click's own KeyError -> next: repaired (status 00:23 "the one reader returns the last raise ... and carries the cause beside it"; pass 1b 00:36)
  - F3 [scale: function-file] readers give two lines for one run -> next: repaired (status 00:36 "every reader gives one line for one run")
  - F4 [scale: function-file] the pin finds 1 of 6 shapes -> next: repaired (status 00:36 "the pin walks the code tree")
  - F5 [scale: line-value] INTERNALERROR gives an empty line -> next: repaired (status 00:36)
- 4: verdict: "Result: the move to one function is clean and holds no foreign hunk. The rule inside the function has two defects that real runs show."
- 6: none
- 7: no — frame 336's Closed line (2026-10-30 17:32) says the error comes "through the one reader harness.error_at". Searched `error_line`, `error_at`, `_raising_line_head`.

### R20. plans/frame297-review-2.md
- 1: date 2026-10-18 (commit 063dfeae); frame 297, pass 2; kind: diff review; asked by: rule — "Review 2 runs on Opus from `C:/Users/roman/rota_r297` at 8e7b7e73, six points, the LF write's blast radius first." (archive stack-2026-10-24.md 35, status 17:45)
- 2: diff yes; brief yes (`f297_review2_brief.md`, six points); frame line not found; goal of the frame not found; destination not found (page)
- 3: 8 findings
  - F1 [scale: approach] the LF write breaks a CRLF night checkout -> next: repaired (status 18:14, pass 4 "a write keeps the file's own line ending")
  - F2 [scale: function-file] a CRLF blob gets a whole-file diff -> next: repaired (same line)
  - F3 [scale: function-file] the ledger door closes a restored note too early -> next: repaired (status 18:14 "the ledger door only reads")
  - F4 [scale: function-file] the eight-line cap lists the wrong lines -> next: repaired (status 18:14 "the refusal lists exactly the shown lines")
  - F5 [scale: line-value] a comment and a commit body state wrong facts -> next: no record
  - F6 [scale: function-file] no replay of bg_2's eight-line row -> next: no record
  - F7 [scale: function-file] `_whole_drop` misses a lost statement inside a kept definition -> next: no record
  - F8 [scale: function-file] `harness.materialise` and `scaffold.py` still use `write_text` -> next: no record (the review: "Fix: none now")
- 4: verdict: "Verdict: not ready. Three high findings stand." The page then lists four high findings, and status 17:57 says "4 high, 4 low".
- 6: none
- 7: no — status 2026-10-24 08:12 (archive stack-2026-10-26.md 108) names the fault of F7 again: "a whole-file `code.write` that drops a statement inside a kept definition, no note opened, and the commit landed". The review named it. The frame left it with no record.

### D1. plans/design-contested-record-review-2026-11-06.md
- 1: date 2026-11-06 (commit 1b435c32); frame 362, the design before slice 1; kind: design review; asked by: rule — "The design review runs on Opus, cap 90k, seven points, to plans/design-contested-record-review-2026-11-06.md; the question goes to Roman after it." (stack.md 2015, status 10:21)
- 2: diff no; brief yes (seven points); frame line not found; goal of the frame not found; destination not found (page: the design and the read of the measured fault)
- 3: 9 findings
  - F1 [scale: approach] the batch half of the fact is discharged by any write -> next: repaired (status 10:40 "all 8 findings taken")
  - F2 [scale: function-file] `batches_annotate` clears the set only on a relay -> next: repaired (same line)
  - F3 [scale: function-file] the reader table lacks `touch_note` and `batches_judge_touch` -> next: repaired (same line)
  - F4 [scale: approach] the worst case is 9 sessions and two stuck lines -> next: repaired (same line)
  - F5 [scale: words: the open question to Roman reads a departure from R7 that is not there] -> next: repaired (status 10:36 "No question goes to Roman")
  - F6 [scale: approach] check 2 of the measure tests nothing new -> next: repaired (status 10:40)
  - F7 [scale: words: the replay plan names the wrong models and port] -> next: repaired (status 10:40)
  - F8 [scale: frame] design C mends 6 cases, not cause 8 -> next: repaired (status 10:36 "Decided: one rule in place of a row per kind")
  - F9 [scale: line-value] the constraint cell of section 1 -> next: no record
- 4: verdict: "Verdict: revise, then build."
- 6: F8: "Design C mends 6 cases of the contest path, not cause 8. The code already holds a general form". The session's next line (stack.md 2017, 10:36): "Decided: one rule in place of a row per kind, a contest of his on a ref with a verdict stays owed until a row of the ref's owner rests on that verdict."
- 7: not sure — frame 362 is open. Dry run 7 turn 6 (status 2026-11-06 16:40) shows "the owed contest on a test line, a kind that slice 1 does not cover". The design had placed that kind in slices 2 to 4.

### D2. plans/design-false-claim-amend-review-2026-11-08.md
- 1: date 2026-11-08 (commit 7f43e4f2); frame 360, the design amendment H0 to H11; kind: design review; asked by: rule — "The design review runs on Opus, cap 70k, seven points, to plans/design-false-claim-amend-review-2026-11-08.md. Then the question to Roman, H1 against H2." (stack.md 2176, status 09:41)
- 2: diff no; brief yes (seven points); frame line not found; goal of the frame not found; destination not found (page)
- 3: 14 findings
  - F1 [scale: approach] the limit of H1 is stated too weakly -> next: repaired (commit f9e2614f "all 14 findings taken")
  - F2 [scale: words: the question to Roman omits his ruling of 2026-11-06 14:19] -> next: repaired (same commit)
  - F3 [scale: function-file] `execute._local` stores a CR LF fold as two LFs -> next: repaired (same commit)
  - F4 [scale: approach] a run that raises has no defined record -> next: repaired (same commit)
  - F5 [scale: approach] refusal 2 refuses A1 to A3, and a renamed copy passes -> next: repaired (same commit)
  - F6 [scale: frame] the reach and the price miss the wiring -> next: repaired (same commit)
  - F7 [scale: line-value] the rate "1 of 19" is mostly from before the door -> next: repaired (same commit)
  - F8 [scale: words: the options offered to Roman] -> next: repaired (same commit)
  - F9 [scale: words: the story of the question overstates the trial] -> next: repaired (same commit)
  - F10 [scale: line-value] 14 places, not 13 -> next: repaired (same commit)
  - F11 [scale: line-value] two words of the H6 line -> next: repaired (same commit)
  - F12 [scale: function-file] the predicate keys by head, the reader by batch -> next: repaired (same commit)
  - F13 [scale: approach] the door names no act for a program that writes the tree -> next: repaired (same commit)
  - F14 [scale: line-value] "already withdrew" -> next: repaired (same commit)
- 4: verdict: "Verdict: revise. 2 high, 7 medium, 5 low."
- 6: F6: "The reach and the price miss the wiring that the probe patched." The session's next record: commit f9e2614f (09:51), "the revision of the design amendment, all 14 findings taken". No status line records the review's result. The next status line (stack.md 2177, 10:01) holds Roman's ruling and "Next: slice 2 of the false claim, H1 as revised, about 10 cycles".
- 7: not searched (a review of the last three days)

### D3. plans/design-false-claim-review-2026-11-06.md
- 1: date 2026-11-06 (commit d5a61119); frame 360, the design before slice 1; kind: design review; asked by: rule — "The design review runs on a fresh reviewer on Opus, cap 80k, seven points, to plans/design-false-claim-review-2026-11-06.md." (stack.md 2159, status 13:27)
- 2: diff no; brief yes (seven points); frame line not found; goal of the frame not found; destination not found (page)
- 3: 8 findings (6 numbered, 2 outside the points)
  - F1 [scale: approach] shape D repeats a door measured at 29 of 29 rote answers -> next: repaired (status 13:42 "all 8 findings taken. D is out.")
  - F2 [scale: line-value] the claimed line is false on run 1 -> next: repaired (same line)
  - F3 [scale: function-file] the touch page stays an open ask under "Waiting on you." -> next: repaired (same line)
  - F4 [scale: approach] no shape at the Tester -> next: repaired (same line, "New shape F")
  - F5 [scale: words: the controls and the replay target of the measure] -> next: repaired (same line)
  - F6 [scale: words: the question to Roman omits the premise of his ruling of 2026-11-02 17:14] -> next: repaired (status 13:36 "The recommendation of option 1 in the terminal is withdrawn, and Roman is told.")
  - F7 [scale: approach] a mechanical fact exists, a stub run -> next: repaired (status 13:42 "New shape G, a stub run, priced 8 to 10 and deferred")
  - F8 [scale: approach] the variant B-prime leans on a hold that nothing releases -> next: repaired (status 13:42, all 8 taken)
- 4: verdict: "Verdict: revise before the build. 8 findings: 5 high, 3 low, two of the low ones outside the points."
- 6: none at frame or above. F6 is about his ruling, and its next line is quoted above.
- 7: yes — status 2026-11-08 09:41 (stack.md 2176): "principal._built_words still says 'and the tests check the claim', the false sentence the review removed from CLAIMED_LINE". The same status names "the test: route of the verdict door does not check the Critic's own judgement". The review named neither. Frame 360 is open.

### D4. plans/design-onboarding-review-2026-11-03.md
- 1: date 2026-11-03 (commit f49964a5); frame 362, the onboarding design; kind: design review; asked by: rule — "The design review runs on a fresh reviewer on Opus, cap 60k, eight points with a materiality test, to plans/design-onboarding-review-2026-11-03.md; then one revision by the designer, then the reading to Roman." (stack.md 1828, status 00:52)
- 2: diff no; brief yes (eight points); frame line not found; goal of the frame not found; destination not found (finding 9 cites the purpose line) (page)
- 3: 12 findings
  - F1 [scale: frame] the page omits the `lazy` election that exists -> next: repaired (status 01:03 "B is the lazy election that exists today as the default")
  - F2 [scale: frame] the cost basis is wrong by about three times -> next: repaired (status 01:03, the Revision section for the 12 findings)
  - F3 [scale: approach] project-level commitments never reach a touched source file -> next: repaired (status 01:03 "bound to source files by a stated rule")
  - F4 [scale: approach] "neighbours" has no definition on the edges -> next: repaired (status 01:03 "the areas of its ranked callers")
  - F5 [scale: approach] the harvest kinds miss one witness and harvest the trap -> next: repaired (status 01:03, Revision section)
  - F6 [scale: words: the Critic exception conflicts with a Critic rule of 2026-10-01] -> next: repaired (status 01:03 "against 13d138b2 of 2026-09-30")
  - F7 [scale: frame] the slice is under-priced -> next: repaired (status 01:03 "the first the icalendar commitments at 16 to 19 cycles")
  - F8 [scale: approach] the slice measure cannot tell the push from the request -> next: repaired (status 01:03, Revision section)
  - F9 [scale: words: question 2 to Roman has no provenance] -> next: repaired (status 01:03 "Three rulings asked now, with the provenance first")
  - F10 [scale: line-value] "a later request on the same area: 0" -> next: repaired (Revision section)
  - F11 [scale: words: question 3 needs no ruling] -> next: repaired (Revision section)
  - F12 [scale: approach] the define cut keeps one sense per area -> next: repaired (Revision section)
- 4: verdict: "Revise. High 4, medium 5, low 3. The direction of design B stands."
- 6: F1: "The page omits the `lazy` election that exists." F2: "The cost basis is wrong by about three times." F7: "The slice is under-priced." The session's next line (stack.md 1830, 01:03): "B is the lazy election that exists today as the default ... two sessions of slices, the first the icalendar commitments at 16 to 19 cycles".
- 7: yes — the deep dive, status 2026-11-03 01:27 (stack.md 1835): "the lazy election has no exit, 240 rows deferred and the same 7 paged on every answer", and "B is priced at 77 to 86 cycles at the actual rate, four sessions". The review named the lazy election as present and priced B at two sessions.

### D5. plans/f362-review-shape-design.md
- 1: date 2026-11-04 (commit 98fe1447); frame 362, the shape layer design; kind: design review; asked by: rule — "The design review runs on Opus, cap 60k, eight points, from f362_review_shape_brief.md in this session's scratchpad, to plans/f362-review-shape-design.md." (stack.md 1870, status 00:20)
- 2: diff no; brief yes (eight points); frame line not found; goal of the frame not found; destination not found (page)
- 3: 10 findings
  - F1 [scale: approach] the consult instrument does not read the new door -> next: repaired (status 00:37 "all from the door over records that exist, 0 from new shape records")
  - F2 [scale: approach] the guess reader has no build step -> next: repaired (status 01:08, S1 "the guess rows gain copies and entry_point")
  - F3 [scale: function-file] the harvester does not run again after a merge -> next: repaired (status 00:37 "the harvester runs again after a merge")
  - F4 [scale: words: trap I1 is not a shape credit] -> next: repaired (status 00:37 "traps 4 of 12 disarmed and 2 partly")
  - F5 [scale: words: the operation number has no unit] -> next: repaired (status 00:32 "The review names the operation count"; 00:37)
  - F6 [scale: approach] no drop rule, and the measure follows the build -> next: repaired (status 00:37 "a keep rule per kind ... comes before any measure")
  - F7 [scale: frame] step 3 is priced too low -> next: repaired (status 00:37 "Shape layer 24 to 26 cycles priced")
  - F8 [scale: approach] `model.shape(name)` needs a name the seat may not have -> next: no record
  - F9 [scale: function-file] the call count of the copy row is empty on tips -> next: no record
  - F10 [scale: function-file] a third resolver of re-exports -> next: repaired (status 01:08 "code_calls written by the indexer with the resolver on harvest.Tree")
- 4: verdict: "Verdict: revise. The four facts are cheap and mechanical, and their counts hold on the pinned commits. Three high findings remain."
- 6: F7: "Step 3 is priced too low (low)." The session's next line (stack.md 1874, 00:37): "Shape layer 24 to 26 cycles priced, with the slice 36 to 41, about three sessions."
- 7: not sure — frame 362 is open. The S1 review (status 2026-11-04 01:26) names "harvest.Tree._imports reads the module body only, so code_calls misses definitions under a module-level if", and "the call pass adds about 0.8 s ... twice the design's price". These sit at the resolver that F10 placed on `harvest.Tree`.

### D6. plans/f363-moment-review-2026-11-10.md
- 1: date 2026-11-10 (commit d729d3d4); frame 363, the moment design; kind: design review; asked by: rule — "One review of the design runs on Opus, cap 60k, to plans/f363-moment-review-2026-11-10.md." (stack.md 1746, status 00:44). The frame's Ends-when asks for it: "designed from what exists with one review" (stack.md 1741).
- 2: diff no; brief yes ("the points of the session's brief"); frame line not found; goal of the frame not found; destination yes (the page tests the Destination line on dry runs 5, 7 and 8) (page)
- 3: 16 findings (F1 to F9, F12 to F18; the page notes that F10 and F11 became notes)
  - F1 [scale: direction] the sprint boundary is where Roman rules a placement -> next: repaired (no status line; `plans/method/reference.md` 425 to 427 "A placement stays (reasoned) until Roman rules it")
  - F2 [scale: words: rule C48 names "the next night's wall"] -> next: no record
  - F3 [scale: words: rule C77 moves frames itself] -> next: no record (reference.md 411 still says "before any frame moves")
  - F4 [scale: words: the amendment cites C55 without its second half] -> next: no record
  - F5 [scale: line-value] the Model bullet breaks C36 -> next: repaired (status 00:52 "the Model line names a wall only after an interview by C36")
  - F6 [scale: direction] the build-or-measure test is degenerate and has no exit -> next: repaired (status 00:52 "Next reads measure when every build row is closed")
  - F7 [scale: direction] "repeats" needs judgement on prose -> next: repaired (status 00:52 "the Destination line is three counts")
  - F8 [scale: words: cause 5 of the wall guide exists with that meaning] -> next: repaired (status 00:52 "frame 201's interview is a placed wall")
  - F9 [scale: line-value] the mark is (reasoned), not (ruled) -> next: repaired (status 00:52 "the amendment is marked reasoned")
  - F12 [scale: function-file] "the newest section" is not defined for the head reader -> next: owed (status 00:52 "Next: the state print's two lines, one fresh implementer")
  - F13 [scale: line-value] the Order bullet's numbers are not all frames -> next: repaired (stack.md 50 now reads "Order: build rows frame 182, frame 171, ...")
  - F14 [scale: line-value] the example count is wrong -> next: no record
  - F15 [scale: words: the order has two records in one section] -> next: no record
  - F16 [scale: line-value] "none: every ..." wording -> next: repaired (reference.md 423 "or \"none placed\"")
  - F17 [scale: function-file] the capability match counts a denial -> next: no record
  - F18 [scale: approach] the holder cannot see how far the build is against the Order -> next: no record
- 4: verdict: "Verdict: build with fixes."
- 6: F1: "C46 of section 4: the sprint boundary is where Roman rules a placement." Next record: reference.md 425 to 427, no status line. F6: "The test is degenerate and has no exit." F7: "'Repeats' needs judgement on prose." The session's next line (stack.md 1747, 00:52): "Taken: the Destination line is three counts, Next reads measure when every build row is closed, the Model line names a wall only after an interview by C36, the amendment is marked reasoned."
- 7: not searched (a review of the last three days)

### D7. plans/frame195-design-review.md
- 1: date 2026-10-11 (commit 33f96e4fb); frame 195, the design before pass 1; kind: design review; asked by: rule — "Then this session judges the design before any pass." (archive stack-2026-10-11.md 107, status 02:46)
- 2: diff no; brief yes (eight points); frame line not found; goal of the frame not found; destination not found (page)
- 3: 7 findings (points 1 to 5, 7 and 8; point 6 says "Fix: none")
  - F1 [scale: function-file] the load: the plugin can be shadowed or hidden -> next: repaired (status 03:03 "The fixes are folded into `plans/frame195-design.md`"; pass 1 at 04:19, `_rota_caught.py`)
  - F2 [scale: function-file] the import before the call turns a pass into a fail -> next: repaired (same lines)
  - F3 [scale: function-file] the wrap changes `exc_info` and the signature -> next: repaired (same lines)
  - F4 [scale: function-file] the section pushes the assertion out of the tail -> next: repaired (same lines)
  - F5 [scale: line-value] the `raised at` words -> next: repaired (same lines)
  - F6 [scale: line-value] the rules: record `result.output == ""` as a fact -> next: repaired (same lines)
  - F7 [scale: words: the baseline of the measure] -> next: repaired (status 03:03 "The baseline is 10 of 11 Developer sessions")
- 4: verdict: "Verdict: start the build after the fixes below."
- 6: none
- 7: no after the close of 2026-10-11 21:51 (searched `_rota_caught`, "caught by CliRunner"). Before the close, the diff review of 878c2352 (status 05:00) names a gap at the fix of F2: "the plugin wraps only when `click` is already in `sys.modules`, so a test that imports click inside its body gets no section, 66 of 104 Tester bodies". Review 1c (status 13:59) names a high on Python 3.12 and later at the finder.

## Gate lines

The gate lines hold "new red" or "0 new reds", on the frames of R1 to R20. Up to two per frame.

| Frame | Reviews | Line 1 | Line 2 |
|---|---|---|---|
| 361 | R1 | not found under frame 361's heading. The shared gate sits under frame 362's heading: 2026-11-03 03:52 (rota-5b) "4 new reds, 2 flaky in test_l3_rulings, 2 real", then "12 cases re-recorded" (stack.md 1842) | 2026-11-03 05:18 (rota-5b) "0 new reds, 0 stale ... The doors and the lazy default are accepted on the checkout." Then "Dry run 4, Run F, starts" (stack.md 1846) |
| 330 (F20's lines) | R2 | 2026-10-27 16:48 (rota-ba) "the gate on the merge c40811d0 gave 12 new reds against the baseline f9f5cd1, the 11 of the 9827e38a gate plus L1-LI-say-what-the-run-could-not-see". Next: "F20 with F21 is on the head." | not found |
| 344 | R6, R17, R19 | 2026-10-28 01:27 (rota-33) "the gate on 695e3beb ... gave 12 new reds against the baseline, the 9 known and three STALE cases". Next: "F23, F4 and F5 are on the head." | 2026-10-29 14:03 (rota-b8) "the gate 127 failed all in the baseline, 0 new reds, 57 stale". Next: "Re-check p1b runs on the p1 reviewer, cap 20k. Land on READY" |
| 303 | R3 | 2026-10-23 17:55 (rota-48) "new reds 0; reds gone 1, L1-AR-route-an-escalation; stale 0". Next: "Passes 1 and 1b accepted on the gate and review 1." | not found |
| 356 | R4 | 2026-11-01 07:02 (rota-40) "new reds 1, real, test_a_refusal_names_a_call_its_modes_hold". Next: "The fix goes to the same implementer by message, then the gate again." | 2026-11-01 09:23 (rota-11) "new reds 0; reds gone 0; stale 0. Pass 3 committed at 584f7f91." Next: "Review p3 of 584f7f91 runs" |
| 204 | R5 | 2026-10-12 02:50 (rota-cd) "new reds 19, 11 flaky". Next: "Pass 1 does not hold yet: five seats changed behaviour under the pass's brief text. ... A read runs now on Opus" | 2026-10-12 11:23 (rota-6d) "new reds 4, 0 flaky, the same four". Next: "The review of pass 1f runs on Opus" |
| 345 | R7, R11 | 2026-10-29 15:23 (rota-b8) "the gate with --no-rerecord 120 failed, 0 new against a baseline it stored itself, 92 stale". Next: "Not landed ... Review p10 runs on Opus" | 2026-10-30 10:46 (rota-86) "Gate on the worktree 48 failed, no new red." Next: "The frame's debt is cleared, so the frame closes" |
| 298 | R8 | 2026-10-18 16:24 (rota-89) "new reds 1, flaky, a handover seat test". Next: "Pass 5 stands on the gate." | 2026-10-18 16:41 (rota-89) "new reds 0; reds gone 0; stale 0. Night 157 launched at 16:40" |
| 243 | R9 | 2026-10-15 02:26 (rota-0c) "the agent's gate 571.9s, new reds 10, the 8 known and two flaky". Next: "The session's own gate runs now, and the tests commit after its five lines" | 2026-10-15 10:30 (rota-0c) "9 new reds, the known 8 and the flaky `scene_challenged_again`". Next: "Review 1 runs on Opus from a worktree at 26940b74" |
| 257 | R10 | not found | not found |
| 266 | R12 | 2026-10-16 19:32 (rota-e7) "9 new reds, the known 8 and the flaky `scene_challenged_again`". Next: "Accepted at ce658cdb. Validating on the next night." | 2026-10-17 12:57 (rota-29) "10 new reds, the known 9 by name and the flaky `scene_challenged_again`". Next: "Accepted at 7c0b2f32. Validating on the next night" |
| 354 | R13 | 2026-11-01 01:56 (rota-40) "new reds 6, the three flaky L3R n170 cases and three dry1 tests". Next: "Pass 8 committed at 1f8e6e1a. Review p7 of 1f8e6e1a runs" | 2026-11-01 02:53 (rota-40) "new reds 0; reds gone 0; stale 0. Pass 9 committed at 024ed0f0." Next: "Review p8 of 024ed0f0 runs" |
| 197 | R14 | 2026-10-11 07:41 (rota-c5) "new reds 0, reds gone 0, stale 0. Pass 1 committed at 76521304". Next: "The review runs on Opus on the worktree" | 2026-10-11 08:32 (rota-c5) "new reds 1, `test_handover.py::test_one_claim_wakes_exactly_one_standby`, flaky". Next: "Validating at b744b9cc." |
| 234 | R15 | 2026-10-14 12:03 (rota-f7) "10 new reds, the known 9 and `test_register_key` on the 9 stale Liaison cases". Next: "The gate runs again at 12:02 with the card free, for the 9 re-records." | 2026-10-14 13:05 (rota-f7) "9 new reds, the known set with its flaky one". Next: "Frame 234 validates at bf3ae643" |
| 363 | R16 | 2026-11-10 10:00 (rota-82) "1 new red, `test_the_parked_frame_never_prints`, and the gate marks it flaky". Next: "The implementer is resumed for two commits ... No second gate run" | 2026-11-10 12:12 (rota-82) "33 failed against a baseline of 33, 0 new reds". Next: "The diff review of pass 1b runs on one reviewer on Opus" |
| 349 | R18 | 2026-10-30 17:23 (rota-6d) "new reds 1, test_handover.py::test_a_newer_watcher_retires_the_older_one, flaky, passed on the rerun". Next: "Review p2 runs on a reviewer on Opus" | 2026-10-30 18:50 (rota-6d) "new reds 0, reds gone the same 2, stale 0". Next: "Review p3 runs on a reviewer on Opus" |
| 297 | R20 | 2026-10-18 17:56 (rota-9d) "new reds 0; reds gone 0; stale 0. The LF write moved no recorded case". Next: "Review 2 and pass 3 are out." | 2026-10-18 20:33 (rota-9d) "2 new reds". Next: "Pass 7 runs on the same implementer, cap 30k ... The mechanism is not closed until that gate is clean." |

## Counts

Part a: 27 reviews. 18 diff reviews, 1 rule review, 1 other (a classification), 7 design reviews.

Findings by scale:

| Kind | Reviews | Findings | line-value | function-file | approach | frame | direction | words |
|---|---|---|---|---|---|---|---|---|
| diff review | 18 | 90 | 25 | 53 | 5 | 1 | 0 | 6 |
| rule review | 1 | 9 | 0 | 0 | 0 | 1 | 0 | 8 |
| other (classification) | 1 | 4 | 0 | 4 | 0 | 0 | 0 | 0 |
| design review | 7 | 76 | 14 | 14 | 21 | 6 | 3 | 18 |
| all | 27 | 179 | 39 | 71 | 26 | 8 | 3 | 32 |

Next acts by class:

| Kind | repaired | owed | set aside, reason | set aside, no reason | no record |
|---|---|---|---|---|---|
| diff review | 63 | 5 | 6 | 4 | 12 |
| rule review | 9 | 0 | 0 | 0 | 0 |
| other (classification) | 1 | 1 | 0 | 0 | 2 |
| design review | 65 | 1 | 0 | 0 | 10 |
| all | 138 | 7 | 6 | 4 | 24 |

Reviews with a finding at the scale of the frame or above: 7 of 27. Diff review: 1 (R2). Rule review: 1 (R9). Design review: 5 (D1, D2, D4, D5, D6). Only D6 holds a finding at the direction scale.

Given-to counts (yes):

| Kind | diff | brief | frame line | goal of the frame | destination |
|---|---|---|---|---|---|
| diff review (18) | 18 | 18 | 0 | 7 | 0 |
| rule review (1) | 0 | 1 | 1 | 1 | 1 |
| other (1) | 1 | 1 | 0 | 0 | 0 |
| design review (7) | 0 | 7 | 0 | 0 | 1 |
| all (27) | 19 | 27 | 1 | 8 | 2 |

Asked-by counts: rule 25 (18 diff, 7 design; no line names the rule), Roman 1 (R9), own choice 1 (R7), not found 0.

Cell 7 counts:

| Kind | yes | no | not sure | not searched |
|---|---|---|---|---|
| diff review | 4 (R2, R5, R12, R15) | 9 | 4 (R3, R11, R14, R17) | 1 (R16) |
| rule review | 0 | 0 | 1 (R9) | 0 |
| other | 0 | 1 | 0 | 0 |
| design review | 2 (D3, D4) | 1 | 2 (D1, D5) | 2 (D2, D6) |
| all | 6 | 11 | 7 | 3 |

## What I could not find

- The briefs of the reviews in the scratchpads. This read opened none, so "given" comes from the page and the status line only.
- R1 F3: the second look says "Not fixed". The status line of 02:26 says the second look "had marked findings 3 and 4 fixed". This read did not settle which record is right.
- R2: the status lines of F20 sit under frame 330's heading in `plans/archive/stack-2026-11-02.md`, not under frame 344.
- R10: no status line names review 1 before its result. The ask is the price line of 2026-10-23 20:44.
- Gate lines for frame 257: none found. Gate lines for frame 361: none under its own heading.
- R17: no commit holds the page. The date is the file date and the status line of 02:34.
- D2: no status line records the review's result. The record is commits 7f43e4f2 and f9e2614f.
- D6: the next acts for F1, F13 and F16 come from a read of `plans/method/reference.md` and the stack's head, not from a status line.
- The next acts marked "repaired" for design reviews rest on the session's line "all N findings taken". This read did not open the revised design pages to check each finding.
- R20: the verdict says "Three high findings stand", and the findings list four high. The status line counts four.

## A reading, apart from the tables

This reading is one reader's, and it is not part of the cells.

- The diff reviews put 78 of 90 findings at a line or a function. The design reviews put 30 of 76 at the approach, the frame or the direction.
- The one frame-scale finding of a diff review, R2 F1, was repaired in the next pass, 17 minutes later.
- The design reviews end in one revision. The session's line says "all findings taken" in D1, D2, D3 and D4, within minutes. D5 and D6 leave findings with no record, and so does D1's ninth.
- The "no record" class is mostly low findings near the end of a list: R10 F3 to F6, R20 F5 to F8, D6 F14 to F18.
- In three records the later fault sits at the code or the text that repaired a finding of the same review chain: R5 (pass 1b's brief sentences), R13 (pass 9's negation guard), and D7 (the fix of point 2). This is an observation, not a cause.
- R20 F7 was named by the review, left with no record, and named again six days later by frame 283's record.
