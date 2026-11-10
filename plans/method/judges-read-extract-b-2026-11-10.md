# The judges read, extract part b, 2026-11-10

Part b of the read of what each kind of judge finds. Reviews R21 to R40 of the draw `random.Random(363).sample`, then design reviews D8 to D15. One extractor wrote this page, read only.

## Limits

- A status line is the session's own account of what it did with a finding. An earlier check found the status lines true and too sure: a doubt or a limit of an agent is often left out.
- A review page is the agent's account. Nobody checked a review against the code in this read.
- 40 of about 359 is one draw. This part holds 20 of the 40, plus 8 design reviews outside the draw.
- One reader and one pass.
- Open no database. This read opened none.

Notes on method. "asked by: rule" means rule C53 of `plans/method/reference.md` section 6, ruled by Roman 2026-09-27: "One read-only diff review runs after every pass, whatever the pass touches, on a worktree at the pass's commit" and "A design review reads the scope report and the design record before any code". The quoted line is the status line that started the review, where I found one. "frame line" is "not found" in every block, because no status line or review page that I read says that the reviewer got the frame's heading line. The brief files sit in session scratchpads, and I did not read them. Cell 5 is merged into the "-> next" part of each finding line. Cell 7 searches were by function name over `plans/stack.md` and `plans/archive/stack-*.md`, with `grep -l` and then the dated lines.

### R21. plans/frame282-review-1.md
- 1: date 2026-10-17 (commit 76ff4a0e); frame 282, pass 1 (43be926d); kind: diff review; asked by: rule — "Owed: review 1 from a worktree, after frame 283's review 5, three agents being the ceiling, and the gate." (archive stack-2026-10-21.md, status 2026-10-17 18:27)
- 2: diff yes; brief yes; frame line not found; goal of the frame yes (the count re-run, the red case); destination no (status 18:36, review section (a))
- 3: 3 findings
  - F1 [scale: function-file] `built_line_faulted` reads the wider range, no test -> next: repaired (pass 2 adds the tests; the implementer found the finding "does not hold on his real words", frame 289's wall) (status 2026-10-17 18:45)
  - F2 [scale: line-value] a range end has no cap, "lines 2 and 3 to 2026" -> next: repaired (pass 2, the range ends at the page's last line) (status 18:45)
  - F3 [scale: words: the brief's diff range is empty] -> next: no record
- 4: verdict: "stands. Two lows, no high."
- 6: none
- 7: yes — `_line_reading` later "faults lines 1 and 4 on 'I approved two lines, lines 1 and 4, not one', an earlier page's numbers" (W9, archive stack-2026-10-30.md:247, 2026-10-28 02:22); and "_line_reading faults 'Line 2 was wrong before, now it is fine'" (archive stack-2026-10-31.md:16, 2026-10-30 20:03)

### R22. plans/f355-review-p1.md
- 1: date 2026-10-31 (695e75e1); frame 355, pass 1 (31e5fe47); kind: diff review; asked by: rule — "Pass 1 committed at 31e5fe47. Review p1 runs on the worktree at it, cap 35k." (archive stack-2026-11-01.md:15, 2026-10-31 18:57)
- 2: diff yes; brief yes (7 points); frame line not found; goal not found; destination no (review page)
- 3: 5 findings
  - F1 [scale: approach] every `LLMUnavailable` is given back as transient, so a wake that never answers holds the frontier -> next: repaired (pass 2 rule, then pass 3 replaced it with a probe call after review p2 found pass 2's inference wrong) (status 19:04, 19:57, 20:39, 23:13)
  - F2 [scale: function-file] a message on two rows closes when one row moves -> next: repaired (pass 2, `messages.moved_refs`) (19:57)
  - F3 [scale: function-file] `told` is added by `init_db` only -> next: repaired (pass 2, "added on connect") (19:57)
  - F4 [scale: function-file] `undo_dispatch` can give back another dispatch's count -> next: repaired (pass 2, `Wake.counted`) (19:57)
  - F5 [scale: function-file] one report marks every quarantined message told -> next: repaired (pass 2, `Wake.message_ids`) (19:57)
- 4: verdict: "the claim holds for a transient outage, with 1 high and 4 low findings."
- 6: none
- 7: no — `LLMUnavailable`, `instrument_end`, `probe_model`, `model_down` appear only in lines dated 2026-10-24 and 2026-10-31 to 2026-11-01; the close (2026-11-01 02:13) names review p3's lows as residue

### R23. plans/meta-review-2026-11-10.md
- 1: date 2026-11-10 (97198fe8); frame 363, before any pass (the page is "the pointer of frames 363 and 364"); kind: other: a meta review, the synthesis of eight blind extractors over 2026-10-26 to 2026-11-09; asked by: Roman — "i need to do a meta review of how the project is going over the last two weeks" (page lines 3-4)
- 2: diff no; brief not found (the extractor reports are in the transcript of 5ee5ec0b); frame line no; goal of the frame no; destination yes (the Result reads the run against the destination) (page)
- 3: 5 findings (the five points of "The reading")
  - F1 [scale: direction] "The stall compounds, the errors do not." The fault is the conversion of a placed wall into a built fix -> next: owed (frame 363 pushed, the order at the stack's head) (stack.md, 2026-11-10 00:34, 00:35)
  - F2 [scale: direction] the build stored 32 reds as the gate's baseline -> next: owed (frame 363 ends-when part 4; the baseline gate of 07:20 attributes 5 of 33 reds) (stack.md:1741, :1919)
  - F3 [scale: direction] a session steers at the scale its instruments show; `rota/COMPLETION.md` uncited for 44 days -> next: repaired in part (state print pass 1, d3adac83, a capability line) (00:57)
  - F4 [scale: direction] rules exist and do not fire, C39 and C76 -> next: owed (order item 3, "One fresh implementer per pass, by rule C39's stop clause") (page; 00:35)
  - F5 [scale: direction] no read of dry runs 4 to 8 places a wall as a model's limit -> next: repaired (the sentence corrected: "frame 201's interview is a placed wall") (00:52)
- 4: verdict: "Rota went from never run alone to measured eight times, and the destination is not reached."
- 6: F1 "The fault is in the conversion of a placed wall into a built fix." Next line: "The order stands at the stack's head, 97198fe8, with the review page plans/meta-review-2026-11-10.md." (00:35). F3 "A session steers at the scale its instruments show." Next: "Two lines print on the real stack: 4 of 16 held frames name a capability" (00:57). F5 "No read of dry runs 4 to 8 places a wall as a model's limit". Next: "the meta review's sentence on the model's limit is corrected: frame 201's interview is a placed wall." (00:52). F2 and F4: the next line is the order of 00:35.
- 7: not searched (a review of the last three days)

### R24. plans/p12-review-p1.md
- 1: date 2026-10-28 (e904b295); frame: fix P12 for wall W12, sprint 32 row 4, frame number not found; pass 1 (61608940 on w12root); kind: diff review; asked by: rule — the line that started it: not found (the result line is archive stack-2026-10-30.md:318, 2026-10-28 09:57)
- 2: diff yes; brief yes (6 points); frame line not found; goal not found; destination no (review page)
- 3: 6 findings
  - F1 [scale: function-file] `_key_words` sentences run past 25 words -> next: repaired (pass 1b, "m127 is two sentences of 15 and 21 words"; debt kept: "render_state still joins several keys into one sentence that can pass 25 words") (10:08)
  - F2 [scale: function-file] `_capital` prints "Test_types.py" -> next: repaired ("a root file keeps its case") (10:08)
  - F3 [scale: function-file] two stuck batches print one clause twice -> next: repaired ("print one clause with a count") (10:08)
  - F4 [scale: line-value] "1 more test files" -> next: no record
  - F5 [scale: function-file] the test counts the wrong span -> next: repaired ("the long-error test counts the rendered sentence") (10:08)
  - F6 [scale: function-file] an own red test's error shows twice -> next: owed ("Debts on W12: an own red test's error shows twice") (10:08)
- 4: verdict: "READY. ... None of them blocks the land."
- 6: none
- 7: yes — "_gave_up_words already holds the key's words but no page calls it" (frame 354, archive stack-2026-11-01.md:53, 2026-10-31 14:27)

### R25. plans/f354-review-p5.md
- 1: date 2026-10-31 (f06a6052); frame 354, pass 6 (e51b540d, the page's own name is "review p5"); kind: diff review; asked by: rule — "Pass 6 committed at e51b540d. Review p5 runs on the worktree at it, cap 30k." (archive stack-2026-11-01.md:70, 2026-10-31 23:04)
- 2: diff yes; brief yes (6 points); frame line not found; goal not found; destination no (review page)
- 3: 4 findings
  - F1 [scale: function-file] the second page of a retried step reads "try again" back as a wrong line -> next: repaired (pass 7) (23:55)
  - F2 [scale: function-file] a scripted `drop` on a step lands and the status says Stuck -> next: repaired (pass 7) (23:55)
  - F3 [scale: function-file] his repeat names the read-back line too -> next: set aside, reason ("finding 3 needs no code, because the binder's fallback gives a whole reply to every line of a two-line page and the read-back line is gone from this page") (23:55)
  - F4 [scale: function-file] the test helper reads the first present -> next: no record (pass 7 "briefed for the four"; its report line does not name it) (23:09, 23:55)
- 4: verdict: "the claim holds on the Liaison path, with 1 high and 3 low findings."
- 6: none
- 7: no after the close — `_READ_BACK` and `_retries_said` appear in no line past 2026-11-01. Before the close: "The read-back line of m33 names lines 1 and 2 only, so the two retries are not read back, review p6 low 1 live" (archive stack-2026-11-01.md:29, 2026-11-01 00:48)

### R26. plans/frame296-review-1.md
- 1: date 2026-10-18 (861cd414); frame 296, pass 1 (9c4b5368); kind: diff review; asked by: rule — "The review's points: the deviation and the 5 of 7, the 'line one' questio[n]" (archive stack-2026-10-21.md, 2026-10-18 11:36, the line is cut there)
- 2: diff yes; brief yes (6 points); frame line not found; goal of the frame yes (the red case, the counts over nights 139 to 156); destination no (review page)
- 3: 5 findings
  - F1 [scale: function-file] the M400 fixture now gets no target -> next: owed ("the M400 fixture with no target ... are the residue to read") (2026-10-18 12:12)
  - F2 [scale: approach] the change is text only, no door refuses a revise of line 1 -> next: owed (the validation count, closed at 0 on night 158) (12:12; 2026-10-21 16:23)
  - F3 [scale: function-file] two predicates give opposite answers on m125 -> next: set aside, reason ("The two predicates ... stay as frame 258's residue") (2026-10-21 16:23)
  - F4 [scale: function-file] no test reaches `_quotes_line` -> next: no record
  - F5 [scale: words: the report's counts] -> next: repaired (status 11:51 gives "25 refused turns in 19 sessions") (11:51)
- 4: verdict: "accept with low findings."
- 6: none
- 7: no — `_names_request` and `_quotes_line` appear only in archive stack-2026-10-21.md

### R27. plans/frame302-review-2.md
- 1: date 2026-10-23 (0fd11882); frame 302, passes 2 and 2b (5323f8ea); kind: diff review; asked by: rule — "Review 2 runs on the reviewer on Opus from C:/Users/roman/rota_r302 at 5323f8ea, six points, cap 40k" (archive stack-2026-10-24.md, 2026-10-23 15:54)
- 2: diff yes; brief yes (6 points); frame line not found; goal not found; destination no (review page)
- 3: 5 findings
  - F1 [scale: function-file] `new_test_file` admits `tests/test_utils.py` and typos -> next: repaired in part (pass 2c, the stem rule); "A typo of an indexed test file still lands, open and low" (2026-10-23 16:04)
  - F2 [scale: function-file] a disputed file lands through `new_files` -> next: set aside, reason ("The disputed-file gap is `disputed_paths`'s and not this door's") (16:00)
  - F3 [scale: line-value] the prompts keep "new" beside "test file" -> next: no record
  - F4 [scale: line-value] a refused source path ends with a route sentence -> next: no record
  - F5 [scale: words: the cause of six reds] the reds came from frame 302's own pass 1b -> next: repaired (said in the status line, "so they are no model limit") (16:00)
- 4: verdict: "accept for the branch."
- 6: none
- 7: not sure — `new_test_file` is in no later line, and `new_files` lines end 2026-10-23 16:00

### R28. plans/frame220-review-2.md
- 1: date 2026-10-17 (a02ae2e7); frame 220, pass 1b (d2ffdfe3); kind: diff review; asked by: rule — "Review 2 runs on Opus from `C:/Users/roman/rota_r283old` at d2ffdfe3, cap 15k, read-only: the widened except, the path normalisation against `_base_held`'s callers, the merge-base test's base." (archive stack-2026-10-21.md, 2026-10-17 23:16)
- 2: diff yes; brief yes (3 points); frame line not found; goal no; destination no
- 3: 4 findings
  - F1 [scale: line-value] `except Exception` hides bugs in `_batch_base` -> next: repaired (frame 286 pass 1, "frame 220's four lows in `_base_text`") (2026-10-18 00:15)
  - F2 [scale: function-file] no `_base_held` test with an absolute path -> next: repaired (same pass) (00:15)
  - F3 [scale: function-file] a path with `..` makes `git show` return a log -> next: repaired (same pass) (00:15)
  - F4 [scale: line-value] `resolve()` sits outside the `try` -> next: repaired (same pass) (00:15)
- 4: verdict: "pass 1b stands, with two lows and one outside low."
- 6: none. The session's line: "every low fails closed, so none changes a night's count, and the four ride the next pass on this site, frame 286's" (23:22)
- 7: yes — "no committed test pins the base read ... and `_base_text` runs twice per `.py` write" (stack.md:2347, 2026-10-26 05:28)

### R29. plans/frame267-review-1.md
- 1: date 2026-10-16 (a3ab24c9); frame 267, pass 1 (0582873a); kind: diff review; asked by: rule — "The review runs on Opus, cap 80k, on `C:/Users/roman/rota_review_267`, to `plans/frame267-review-1.md`" (archive stack-2026-10-17.md, 2026-10-16 19:50)
- 2: diff yes; brief yes (7 points, with the design's sections 5.1 and 5.4); frame line not found; goal of the frame yes (point 1, the condition on night 151); destination no (review page)
- 3: 6 findings
  - F1 [scale: function-file] `_why_no_ruling` names a fixed fault and hides the live one -> next: repaired (pass 1b) (2026-10-16 20:19)
  - F2 [scale: function-file] `_missed_reply_line` adds no new fact; the review's own fix is "none in this pass" -> next: no record
  - F3 [scale: line-value] "Its last refusal:" for an error -> next: repaired ("the head says refusal or error") (20:19)
  - F4 [scale: function-file] the s336 test uses a made-up call -> next: repaired ("the s336 replay runs its real completion") (20:19)
  - F5 [scale: function-file] four tests fail at HEAD~1 on the new argument -> next: no record
  - F6 [scale: function-file] nothing caps how often a page returns -> next: repaired ("a page returns once per ask") (20:19)
- 4: verdict: "pass 1b for one high."
- 6: none
- 7: not sure — `_why_no_ruling` is in no later line. Before the close, review 2 named "the same defect stays on a second path, the runner's other end line" (2026-10-16 20:25). After the close, frame 320 changed `_missed_reply_line` and named no fault there (stack.md:5500, 2026-10-24 22:15)

### R30. plans/f356-review-p1.md
- 1: date 2026-11-01 (d25e107f); frame 356, pass 1 (cb758ccd); kind: diff review; asked by: rule — "Review p1 of cb758ccd runs on the worktree, cap 25k, from f356_review_p1_brief.md." (archive stack-2026-11-01.md, 2026-11-01 03:47)
- 2: diff yes; brief yes (6 points); frame line not found; goal not found; destination no (review page)
- 3: 5 findings
  - F1 [scale: approach] the method half of the claim rests on a row shape the indexer never writes -> next: repaired (pass 2, the class grain) (06:27)
  - F2 [scale: function-file] a kept dotted ref meets the never-calls check as one string -> next: repaired (pass 2, one resolver at read time) (06:27)
  - F3 [scale: function-file] the vet ignores the module part -> next: repaired (pass 2) (06:27)
  - F4 [scale: function-file] the import door reads the first part of a dotted import -> next: set aside, reason ("low 4 is residue, the Tester gets a hint it can follow") (03:52)
  - F5 [scale: line-value] the call form `click.pause()` stays as written -> next: repaired ("a trailing () is stripped") (06:27)
- 4: verdict: "the claim holds for a top-level dotted name such as `click.pause`, and it does not hold for a method ref."
- 6: none
- 7: no after the close — `_dotted_rows` and `_resolve_surface` appear only in archive stack-2026-11-01.md. Before the close, review p2 named two highs in pass 2's method half (07:58)

### R31. plans/w11-review-p1.md
- 1: date 2026-10-28 (660ec167); frame: fix W11, sprint 33 row 3, frame number not found; pass 1 (5d73ffa1), with looks p2 and p3 on the same page; kind: diff review; asked by: rule — the line that started it: not found (result line archive stack-2026-10-30.md:354, 2026-10-28 12:50)
- 2: diff yes; brief yes (6 points); frame line not found; goal not found; destination no (review page)
- 3: 9 findings (p1 6, p2 2, p3 1)
  - F1 [scale: function-file] the night print does not show the ending -> next: repaired (pass 1b; p2-1 then found it still hides; pass 1c) (13:31, 13:54)
  - F2 [scale: function-file] the hold step holds a parse error -> next: repaired (pass 1b, one reader `_parse_refusal`) (13:31)
  - F3 [scale: function-file] a later call clears the held list and loses the error -> next: repaired (pass 1b; p2 point 3 confirms) (13:31)
  - F4 [scale: line-value] the heading "The calls you stood by ran" is false -> next: repaired (13:31)
  - F5 [scale: function-file] no test checks the hold note or the night print -> next: no record
  - F6 [scale: words: the gate's baseline sat in the worktree] -> next: no record (pass 1b's gate ran in the worktree again; the land used a touched-file run in rota_g328) (13:31, 14:00)
  - p2-1 [scale: function-file] the failures line counts 155 sessions -> next: repaired (pass 1c) (13:54)
  - p2-2 [scale: function-file] the dropped list copies parse errors -> next: repaired (pass 1c) (13:54)
  - p3-1 [scale: function-file] a ToolError's raw text quotes the next call -> next: no record
- 4: verdict: "NOT READY. The commit stops the s130 crash, and its tests prove it. One high stays"
- 6: none
- 7: no — `_parse_refusal` appears only in archive stack-2026-10-30.md

### R32. plans/frame226-review-1c.md
- 1: date 2026-10-13 (8bf5478d); frame 226, pass 1c (84a06216), with a second look on pass 1d; kind: diff review; asked by: rule — the line that started it: not found (the 16:32 line is cut; result line 2026-10-13 16:48, archive stack-2026-10-14.md)
- 2: diff yes; brief yes (7 points); frame line not found; goal not found; destination no (review page)
- 3: 4 findings (3, then 1 in the second look)
  - F1 [scale: function-file] `_CHECK_FAULT` matches the verb "check" -> next: repaired (pass 1d) (16:51)
  - F2 [scale: function-file] an empty surface with the same text answers `unchanged` -> next: set aside, reason ("0 such rows in six nights, kept") (16:48)
  - F3 [scale: function-file] `surface_changed` set on an empty vetted surface -> next: repaired ("an empty vetted surface is no surface change") (16:51)
  - F4 [scale: line-value] the check-alone branch misses a contradicted text -> next: repaired (one-line door by the session, fbde40e6) (17:07)
- 4: verdict: "accept with one high finding." Second look: "accept."
- 6: none
- 7: yes — at the second look's site: "`_WORDS_FAULT` misses 'isn't right' and 'should just say' in night 160's r_04b24ea9ce" (frame 308, archive stack-2026-10-24.md:129, 2026-10-24 00:57)

### R33. plans/frame315-review-residue.md
- 1: date 2026-10-26 (31b64685); frame 315, residue pass 1 (035d86c7), with a second look at 2383c991; kind: diff review; asked by: rule — "Review runs on Opus from `rota_r315b` at 035d86c7, cap 40k, se[ven points]" (stack.md, 2026-10-26 06:24, the line is cut)
- 2: diff yes; brief yes (7 points); frame line not found; goal not found; destination no (review page)
- 3: 10 findings (6, then 4 in the second look)
  - F1 [scale: approach] his recorded removal words point at no sentence, so the door refuses the drop -> next: repaired (pass 1b, the provenance route; "the word route is wrong") (06:35, 06:46)
  - F2 [scale: function-file] "remove" matches a change request and drops the main sentence -> next: repaired (1b) (06:46)
  - F3 [scale: function-file] `_OTHER_CUE` catches "check" as a verb -> next: repaired ("the check, test and file rule is gone") (06:46)
  - F4 [scale: function-file] one removed sentence only -> next: repaired ("one or several") (06:35)
  - F5 [scale: function-file] the tests use a constructed quote -> next: repaired (second look: "with his recorded words the step names the added sentence") (06:51)
  - F6 [scale: function-file] `removed` shows only on a pure subset -> next: no record
  - F7 [scale: function-file] the added rule over-counts -> next: owed (06:51)
  - F8 [scale: function-file] an added paraphrase is missed -> next: owed (06:51)
  - F9 [scale: function-file] "Its" or "Their" is always a page sentence -> next: no record (the line names "two lows", and the page has three)
  - F10 [scale: function-file] an older med: a short paraphrase lands and loses his words -> next: owed ("The two lows and the med are this frame's next residue") (06:51)
- 4: verdict: "does not stand for the branch." Second look: "stands for the branch."
- 6: none
- 7: not sure — the frame is open; its last line (2026-10-30 17:44) says "What stays: the two lows and the med"

### R34. plans/f183-114-review-p1.md
- 1: date 2026-11-10 (66dcbdc4); frames 114 and 183, build 2 (62c86178, bebae782, 3e673298), with a second look at b74c8d9f; kind: diff review (the page says "on Fable", the status line says "on Opus"); asked by: rule — "The review runs on Opus, cap 60k, from f183_114_review_brief.md to plans/f183-114-review-p1.md, that question first." (stack.md, 2026-11-10 01:32)
- 2: diff yes; brief yes (10 points); frame line not found; goal of the frame yes (dry run 8's rows, W3, W5, W7); destination no (review page)
- 3: 9 findings (7, then 2 in the second look)
  - F1 [scale: function-file] `_with_parked_batch` holds only while an open present names the batch -> next: repaired (pass 2b) (02:06)
  - F2 [scale: function-file] any open present counts as the park page -> next: repaired (2b) (02:06)
  - F3 [scale: function-file] `_landed_ruling_refusal` lists duplicates and a ruling of another question -> next: repaired (2b) (02:06)
  - F4 [scale: function-file] the landing Liaison does not see the held line -> next: no record
  - F5 [scale: function-file] the push runs on six modes -> next: repaired ("base and landing.base get no earlier answers") (02:06)
  - F6 [scale: function-file] a mixed set offers the end step -> next: repaired (02:06)
  - F7 [scale: function-file] `_base_red_refs` compares ids, not nodes -> next: no record
  - S1 [scale: function-file] `parked_line` names no held page -> next: owed ("Lows open") (02:20)
  - S2 [scale: line-value] the offer's words name the dropped test only -> next: owed (02:20)
- 4: verdict: "Fix before the pick." Second look: "pick."
- 6: none
- 7: not searched (a review of the last three days)

### R35. plans/frame222-review-2.md
- 1: date 2026-10-16 (e523106b); frame 222, pass 1d (c5f67351); kind: diff review; asked by: rule — "Review 2 runs on Opus fr[om ...]" (archive stack-2026-10-17.md, 2026-10-16 06:38, the line is cut)
- 2: diff yes; brief yes (6 points); frame line not found; goal of the frame yes (point 6, the counts 24 of 25 and 19 of 24); destination no (review page)
- 3: 4 findings
  - F1 [scale: function-file] the hint permits two bodies that fail at run time -> next: owed ("the lows wait on night 151's count ... with the first low read first"); night 151: "review 2's first low shows 0 signs" (06:43; 17:36)
  - F2 [scale: line-value] the hint asks for `@click.command()` and 21 of 24 bodies lack `import click` -> next: owed (06:43)
  - F3 [scale: function-file] the invoke predicate reads no keyword and no receiver -> next: owed (06:43)
  - F4 [scale: function-file] the already-imported clause reads no module and no alias -> next: owed (06:43)
- 4: verdict: "accept with four low findings."
- 6: none
- 7: no after the close (2026-10-17 04:31) — `_unbound_name_hint` appears only in archive stack-2026-10-17.md. Before the close: "s306's hint offered `import cmd`, the standard library module, for a click command" (2026-10-16 17:36)

### R36. plans/frame309-review-1.md
- 1: date 2026-10-23 (4286b988); frame 309, pass 1 (25c63b8e); kind: diff review; asked by: rule — "Review 1 runs on the reviewer on Opus from C:/Users/roman/rota_r309 at 25c63b8e, four points, cap 25k" (archive stack-2026-10-24.md, 2026-10-23 18:43)
- 2: diff yes; brief yes (4 points, the report's doubt among them); frame line not found; goal not found; destination no (review page)
- 3: 5 findings
  - F1 [scale: function-file] `cmd_run` skips `init_db`, the first run raises -> next: repaired (pass 1b) (19:00)
  - F2 [scale: function-file] `_id_tables` lists the journal, so a deleted run's id resolves -> next: repaired (1b); "audit.py's _ids still counts journal ids", residue at the close (19:00, 19:02)
  - F3 [scale: line-value] the journal `id` is no run key; a column comment -> next: no record
  - F4 [scale: words: `sqlite_sequence`, the review says "none needed now"] -> next: no record
  - F5 [scale: function-file] `_with_repo` writes `test_runs` raw; "Name it on the frame's status line" -> next: no record
- 4: verdict: "do not accept as is. Accept after repair 1, which is one call."
- 6: none
- 7: no — `test_run_journal` later appears once, as the history a restart keeps (archive stack-2026-11-02.md:165, 2026-11-02 00:13), with no fault

### R37. plans/f362-review-slice-p1.md
- 1: date 2026-11-03 (d04808b8); frame 362, slice pass 1, the harvester (0756c7eb); kind: diff review; asked by: rule — "The review runs on Opus, cap 60k, eight points, on rota_r362s, to plans/f362-review-slice-p1.md, with the project-wide over-push as the point to weigh." (stack.md:1858, 2026-11-03 07:35)
- 2: diff yes; brief yes (8 points); frame line not found; goal not found; destination no (review page)
- 3: 9 findings
  - F1 [scale: function-file] `record` writes 7,790 rows with no transaction, a fault leaves a partial stamp -> next: repaired (pass 1b) (07:41)
  - F2 [scale: function-file] bindings are never replaced at a new commit -> next: repaired (1b) (07:41)
  - F3 [scale: function-file] the docs-claim fallback over-pushes 73 candidates -> next: repaired (1b) (07:41)
  - F4 [scale: function-file] the `:rfc:` form adds 27 candidates -> next: owed ("Lows 4 to 8 are residue for the next slice") (07:41)
  - F5 [scale: function-file] unit synonyms pair falsely -> next: owed (07:41)
  - F6 [scale: function-file] a preservation candidate quotes one line -> next: owed (07:41)
  - F7 [scale: function-file] the docs set takes a CI log -> next: owed (07:41)
  - F8 [scale: function-file] the id hashes the line number -> next: owed; later pass 2c: "a stated commitment's id is cw_ plus a hash of kind, path and text with no line" (07:41; stack.md:1878, 2026-11-04 01:08)
  - F9 [scale: function-file] a harvester fault stops the onboarding -> next: repaired (1b) (07:41)
- 4: verdict: "fix."
- 6: none
- 7: not sure — frame 362 is still open in `plans/stack.md`

### R38. plans/frame200-review-1.md
- 1: date 2026-10-11 (dcd2e44d); frame 200, pass 1 (2e6afd1c), with a second look on pass 1b (dd583398); kind: diff review; asked by: rule — the line that started it: not found (the 10:36 line is cut; result line archive stack-2026-10-13.md, 2026-10-11 10:50)
- 2: diff yes; brief yes (8 points); frame line not found; goal of the frame yes (point 2, the 12 night bodies); destination no (review page)
- 3: 7 findings (6, then 1 in the second look)
  - F1 [scale: function-file] the door refuses a factory applied to an inline command -> next: repaired (pass 1b) (11:54)
  - F2 [scale: function-file] `_adds_option` misses `return option(...)(f)` -> next: repaired (1b) (11:54)
  - F3 [scale: function-file] the escalate branch still tells a seat to write -> next: repaired (1b) (11:54)
  - F4 [scale: line-value] "the option that criterion X names" -> next: repaired ("the refusal names the factory") (11:54)
  - F5 [scale: function-file] an aliased `command` import -> next: repaired (11:54)
  - F6 [scale: function-file] the empty-commit note tells a scope sender to end -> next: repaired (11:54)
  - S1 [scale: function-file] the argument kinds refuse a helper `def` or `functools.wraps` -> next: owed ("folds into pass 2's brief") (11:57)
- 4: verdict: "one more pass, three high and three low, all confirmed" (status 10:50). Second look: "stands, 0 high, 1 low" (status 11:57)
- 6: none
- 7: no after the close (2026-10-13) — `_plain_decorated` later appears in a reader merge with no fault (archive stack-2026-10-30.md:253). Before the close: night 140's read found "two Tester tests that read `.callback` ... which the door `_plain_decorated` ... admits, high" (2026-10-11 21:51)

### R39. plans/frame339-review-p1.md
- 1: date 2026-10-26 (1530c06d); frame 339, pass 1 (c7264f5a), with looks on 1b (a0b0b6ae) and 1c (7f263584); kind: diff review; asked by: rule — "Review 1 of c7264f5a runs on Opus from rota_r339, cap 40k, ... the red test both ways, the criterion-asked case on night 169's own criteria" (archive stack-2026-10-28.md, 2026-10-26 22:49)
- 2: diff yes; brief yes (9 points); frame line not found; goal not found; destination no (review page)
- 3: 11 findings (8, then 2 in look 1b, 1 in look 1c)
  - F1 [scale: function-file] a mistake verdict on a removal is lost on the next commit -> next: repaired (1b) (23:36)
  - F2 [scale: function-file] the stray prompts do not explain a removal row -> next: repaired (1b) (23:36)
  - F3 [scale: function-file] a held refusal names a route the next reply refuses -> next: repaired ("write_only on a note with no line") (23:36)
  - F4 [scale: function-file] a third door, the ledger door -> next: repaired in part ("the route's first sentence"); the Reach line: no record (23:36)
  - F5 [scale: words: his words of night 169 miss the matcher; fix "none owed"] -> next: set aside, reason ("his explicit ask costs one Architect wake, a cost law 12 allows") (23:00)
  - F6 [scale: function-file] assertions dropped -> next: repaired ("the pins") (23:36)
  - F7 [scale: line-value] a test docstring names a call it does not make -> next: no record
  - F8 [scale: function-file] a removal in an unpredicted file gives two rows -> next: repaired (1b), and the fix opened 1b-1 (23:36)
  - 1b-1 [scale: function-file] a change outside the grain escapes the sign-off -> next: repaired (1c) (23:36 brief; review 1c "Stands")
  - 1b-2 [scale: line-value] the prompt sentences hold for some rows only -> next: repaired ("the two prompt sentences hold for every row") (23:36)
  - 1c-1 [scale: line-value] one prompt gap remains -> next: no record
- 4: verdict: "Stands with fixes." Look 1b: "Does not stand." Look 1c: "Stands."
- 6: none
- 7: not sure — the close (2026-10-28 14:18) names "a replace that removes a line may pass the removal door with no row, night 173 s123". Before the close, F7 review p1 named "a mistake judgement carries onto a later removal" (2026-10-27 19:33)

### R40. plans/f362-owed-contest-review-2026-11-06.md
- 1: date 2026-11-06 (0540e97c); frame 362, slice 1 of the owed contest (36a2edd2), with looks 2 (822311e0), 3 (3ebc5ac5) and 4 (153dd09a); kind: diff review; asked by: rule — the line that started it: not found (the 11:06 line is cut; result line stack.md:2023, 2026-11-06 11:19)
- 2: diff yes; brief yes ("Outside the brief" in finding 8); frame line not found; goal not found; destination no (review page)
- 3: 13 findings (8, then 3, then 2, then 0)
  - F1 [scale: function-file] a newer approve of the batch line ends an owed contest -> next: repaired (pass 2, "all eight findings taken") (11:34)
  - F2 [scale: function-file] the migration stamps old rows empty -> next: repaired (pass 2) (11:34)
  - F3 [scale: function-file] 7 of 20 tests pass at the parent -> next: repaired (pass 2) (11:34)
  - F4 [scale: function-file] six branches have no test -> next: repaired ("All 11 of the reviewer's mutations turn a test red") (11:34)
  - F5 [scale: function-file] two park pages for one owed key -> next: repaired ("one page for each owed key") (11:34)
  - F6 [scale: function-file] `_guess_seed` drops the guess under a batch-line contest -> next: repaired (pass 2) (11:34)
  - F7 [scale: function-file] a batch annotated before a contest keeps old rows -> next: repaired (pass 2) (11:34)
  - F8 [scale: function-file] `connect` adds no `ruling_id` column -> next: repaired (pass 2) (11:34)
  - E1 [scale: function-file] the backfill stamps nothing with no relay receipt -> next: set aside, reason ("(assumed: a wrong stamp hides a contest that nobody rewrote, and a missing stamp costs one more wake): the backfill with no relay receipt is not built") (11:55)
  - E2 [scale: function-file] no code turns "give the request up" into a drop -> next: repaired (pass 3) (12:31)
  - E3 [scale: function-file] a newer contest on a merged batch ends an owed contest -> next: repaired (pass 3) (12:31)
  - T1 [scale: function-file] the approval check opens the equal-set door -> next: repaired (pass 3b) (12:42)
  - T2 [scale: function-file] `owed_tries` matches the verdict, not the item -> next: repaired (3b) (12:42)
- 4: verdict: "sound for the measured case, with gaps. Merge after findings 1 and 2 are decided." Look 4: "pick."
- 6: none
- 7: not sure — frame 362 is still open

### D8. plans/frame200-design-review.md
- 1: date 2026-10-11 (fb8112ba); frame 200, before pass 1; kind: design review; asked by: rule — "The design review runs now on Opus." (archive stack-2026-10-13.md, 2026-10-11 06:11)
- 2: diff no; brief not found; frame line not found; goal of the frame yes (point 6, the measure); destination no (review page; the design record and the scope)
- 3: 7 findings (one per point)
  - F1 [scale: approach] change 1 misses the call form and drops the limit to option factories -> next: repaired (folded into the design) (06:30)
  - F2 [scale: approach] change 2 leaves two refusals that tell the seat to write -> next: repaired (folded) (06:30)
  - F3 [scale: approach] change 3 can end a wake that owes a write -> next: repaired (folded) (06:30)
  - F4 [scale: approach] change 4's row reaches no seat that can change the test -> next: repaired (Roman ruled the route at 06:30) (06:30)
  - F5 [scale: approach] change 5 marks right replies unresolved -> next: repaired (folded) (06:30)
  - F6 [scale: frame] two of four counts need a read -> next: repaired (folded) (06:30)
  - F7 [scale: frame] a night on pass 1 alone does not measure the frame -> next: repaired ("one night at the end") (06:30)
- 4: verdict: "Do not start as written. Change 5 matters most."
- 6: F6 "Two of the four counts are queries on the night's database. The other two need a read." F7 "A night on pass 1 alone does not measure the frame." Next line for both: "The fixes are folded into `plans/frame200-design.md`. Pass 1 is ready: changes 1 and 2 with the two `sandbox.py` refusals." (06:30)
- 7: not sure — I searched the frame's block only

### D9. plans/frame200-pass5-design-review.md
- 1: date 2026-10-12 (bdef119d); frame 200, pass 5 design; kind: design review; asked by: rule — "The design review runs on Opus, cap 60k, read-only, brief `review2[...]`" (archive stack-2026-10-13.md, 2026-10-12 15:48)
- 2: diff no; brief yes; frame line not found; goal of the frame yes (point 6, the ends-when ratio); destination no (review page)
- 3: 8 findings
  - F1 [scale: function-file] the same-refs door stops matching a reasoned prior -> next: repaired (folded, `_without_own_reasons`) (16:01)
  - F2 [scale: function-file] four hints write the call with no `reason=` -> next: repaired (16:01)
  - F3 [scale: function-file] the `writes` edge turns a law test red -> next: repaired (16:01)
  - F4 [scale: function-file] the answer-mode door accepts the Developer's own row -> next: repaired (`exclude_author`) (16:01)
  - F5 [scale: frame] the night read is priced at 150k against 270k to 330k -> next: repaired ("6 to 7 cycles, 600k to 700k") (16:01)
  - F6 [scale: words: the source of the measure's numerator] -> next: repaired ("the numerator has its SQL and a text rule") (16:01)
  - F7 [scale: function-file] `identity.py` declares `decisions` a journal -> next: repaired (16:01)
  - F8 [scale: function-file] a copied id overwrites the row -> next: repaired (16:01)
- 4: verdict: "not as written, 2 high, 6 low" (status 15:57)
- 6: F5 "The night read is priced at 150k against 270k to 330k." Next: "6 to 7 cycles, 600k to 700k, one night" (16:01)
- 7: not sure — I searched the frame's block only

### D10. plans/frame204-design-review.md
- 1: date 2026-10-11 (b46a6513); frame 204, design pass 1; kind: design review; asked by: rule — "The design review on Opus follows, then Roman's ruling on the design as one piece." (stack.md, frame 204, 2026-10-11 15:15)
- 2: diff no; brief yes (`scratchpad/review204d_brief.md`); frame line not found; goal not found; destination no (review page)
- 3: 9 findings
  - F1 [scale: approach] the fallback conflict row holds a merge on a page, against the ruling of 2026-09-12 -> next: repaired (design pass 2, "under `auto` nothing holds a merge on a page") (15:40)
  - F2 [scale: approach] a batch held by a quarantined message never moves -> next: repaired ("the quarantine is the release of a hold") (15:40)
  - F3 [scale: words: one corpus note in two categories] -> next: repaired ("question 0 at log time places the two-cell note") (15:40)
  - F4 [scale: function-file] the predicate cannot see an `about_ref` that is a path -> next: no record
  - F5 [scale: frame] the predicate holds almost nothing on four nights -> next: repaired (counted again; a recorded case and a seam night added) (15:40)
  - F6 [scale: approach] the faults table has no reader and no discharge -> next: repaired ("three readers and a close command") (15:40)
  - F7 [scale: approach] the fallback line is not shown quietly; pass 5 needs four owner modes -> next: repaired ("pass 5 is removed") (15:40)
  - F8 [scale: frame] pass 1 does not price its re-records -> next: repaired ("57 stale cases at about 6 card hours") (15:40)
  - F9 [scale: words: two questions for Roman that the records answer] -> next: repaired ("Q1 and Q3 are dropped with the records' answers") (15:40)
- 4: verdict: "do not start as written, 3 high, 6 low" (status 15:34)
- 6: F5 "The predicate holds almost nothing on the four nights." Next: "the predicate holds 0 to 2 of 6 merges on nights 136 to 139 and pass 2 adds a recorded case and a seam night" (15:40). F8 "Pass 1 does not price its re-records, and its stale list is a guess." Next: "pass 1 names 57 stale cases at about 6 card hours" (15:40)
- 7: not sure — the frame is parked

### D11. plans/frame287-design-review-1.md
- 1: date 2026-10-17 (72557395); frame 287, design revision 1; kind: design review; asked by: Roman and rule — "this session reasons over the four `plans/frame287-*.md` pages on Fable, writes `plans/frame287-design.md`, runs one design review on Opus, and brings Roman the design; no question to him before that (ruled: Roman, 2026-10-17 18:22, in the note)" (archive stack-2026-10-18.md, 2026-10-17 18:54)
- 2: diff no; brief yes (11 points); frame line not found; goal of the frame yes (point 1, his words); destination yes (point 2, the composition) (review page)
- 3: 20 findings
  - F1 [scale: approach] the `Means:` field persists what he said not to persist -> next: repaired (revision 2) (19:13)
  - F2 [scale: approach] frame files and law files get several writers -> next: repaired (19:13)
  - F3 [scale: approach] the ask print rules for the Principal -> next: repaired ("a print that never refuses or decides") (19:13)
  - F4 [scale: frame] cause 2 is refuted for frames 114 and 115 by a grep -> next: repaired ("cause 1 rewritten ... the back-fill dropped") (19:13)
  - F5 [scale: frame] the 15 of 19 check measures little -> next: repaired ("about nine distinct answers"; review 2 counts 7) (19:13)
  - F6 [scale: approach] the brief split moves cycle rules no moment prints -> next: repaired ("the cycle rules kept"; review 2 says this does not hold) (19:13)
  - F7 [scale: approach] the print replaces two agent-read rulings unnamed -> next: repaired ("both rulings named as amended") (19:13)
  - F8 [scale: words: a second question owed to Roman] -> next: repaired ("three items for Roman") (19:13)
  - F9 [scale: approach] the view regime has two high failure modes -> next: repaired ("deferred to a fifth frame behind a hash guard") (19:13)
  - F10 [scale: direction] section 6 answers "next" and not the medium-term story -> next: repaired (`wake next` prints "the destination, the sprint, the open and closed counts and the parked ranks") (19:13)
  - F11 [scale: line-value] six quotes stretched -> next: no record
  - F12 [scale: approach] the map writes no index -> next: no record
  - F13 [scale: approach] two memory retirements do not follow -> next: no record
  - F14 [scale: line-value] two counts overstate page B -> next: no record
  - F15 [scale: frame] a cause is missing -> next: no record
  - F16 [scale: frame] the price is the priced side of the overruns -> next: no record
  - F17 [scale: frame] the end check overfits the door questions -> next: no record
  - F18 [scale: approach] sprint orders have no record shape -> next: no record
  - F19 [scale: function-file] the hook change removes the anti-idle prompt -> next: no record
  - F20 [scale: approach] his words on every take reverse a declined pointer -> next: no record
- 4: verdict: "The design does not stand as written. The direction stands"
- 6: F4 "Cause 2 is refuted for frames 114 and 115. Today's records answer the keys." Next: "cause 1 rewritten as the unsearched law file with the back-fill dropped" (19:13). F5 "The 15 of 19 line measures little." Next: "the prototype counting about nine distinct answers under a 3k cap" (19:13). F10 "Section 6 answers "next" and not "future management"." Next: "`wake next` printing the destination, the sprint, the open and closed counts and the parked ranks" (19:13). F15, F16, F17: the next line names none of them.
- 7: not sure — I searched the frame's block only

### D12. plans/frame287-design-review-2.md
- 1: date 2026-10-17 (910495d7); frame 287, design revision 2; kind: design review; asked by: rule — "Review 2 runs on Opus, cap[...]" (archive stack-2026-10-18.md, 2026-10-17 19:13, the line is cut)
- 2: diff no; brief yes (6 points); frame line not found; goal not found; destination yes (point 2, the composition) (review page)
- 3: 13 findings
  - F1 [scale: approach] rules that no moment prints still leave the brief -> next: repaired ("a rule moves only when a tool prints it") (19:25)
  - F2 [scale: frame] cause 1 holds for frame 114 and not for frame 115 -> next: repaired ("frame 115 placed under cause 2") (19:25)
  - F3 [scale: line-value] the count is 7, not 9 -> next: repaired ("the seven answers listed") (19:25)
  - F4 [scale: approach] the amended agent read has nothing to read on a miss -> next: repaired (19:25)
  - F5 [scale: approach] frame 3 points at frame 4's tools -> next: repaired ("frames 3 and 4 swapped ... frame 5 parked") (19:25)
  - F6 [scale: approach] the derived file is a cache -> next: repaired ("no index file") (19:25)
  - F7 [scale: words: a fourth item owed to Roman] -> next: repaired (19:25)
  - F8 [scale: approach] the scratchpad is no home for his words -> next: no record
  - F9 [scale: line-value] the price sums wrong, 12 not 16 -> next: no record (the status line repeats the finding)
  - F10 [scale: line-value] four ruled marks stretch page A -> next: no record
  - F11 [scale: line-value] section 3 misreads a percentage -> next: no record
  - F12 [scale: frame] the end check is still the frame 114 case -> next: no record
  - F13 [scale: words: six places lean on revision 1] -> next: no record
- 4: verdict: "The design does not stand as written, but it is close."
- 6: F2 "Cause 1 is shown for frame 114 and not for frame 115." Next: "frame 115 placed under cause 2" (19:25). F12 "The end check is still the frame 114 case, and `Law:` is still mandatory." Next: no record.
- 7: not sure — I searched the frame's block only

### D13. plans/frame287-design-review-3.md
- 1: date 2026-10-18 (c787dcbc); frame 287, design revision 4; kind: design review; asked by: rule — the line that started it: not found (result line archive stack-2026-10-18.md, 2026-10-18 01:39)
- 2: diff no; brief yes (11 points); frame line not found; goal of the frame yes (point 1, his words of 01:27); destination not found (review page)
- 3: 13 findings
  - F1 [scale: frame] frame 1's check is circular -> next: repaired ("a pilot with a baseline count ... written blind to page C") (01:39)
  - F2 [scale: frame] R4 fixes cause 1 with prose -> next: repaired ("a `Searched:` field") (01:39)
  - F3 [scale: approach] the ledger grows by habit only -> next: repaired ("the status tool gains `--ruling`") (01:39)
  - F4 [scale: approach] the search has no match rule -> next: repaired ("the search joins whitespace, folds case") (01:39)
  - F5 [scale: approach] nothing writes the asker's words on `Keys:` -> next: no record
  - F6 [scale: approach] two back-fill agents write one record -> next: no record
  - F7 [scale: approach] no step follows a zero-hit print -> next: repaired ("a zero hit sends the agent to `LAWS.md` and the composition whole") (01:39)
  - F8 [scale: approach] no `Said:` for an old ruling -> next: no record
  - F9 [scale: frame] the back-fill size is 219 blocks -> next: no record
  - F10 [scale: frame] two ends-when lines are not observable -> next: no record
  - F11 [scale: line-value] R4.2 and R4.5 disagree -> next: no record
  - F12 [scale: approach] `ROLES.md` is outside the search -> next: repaired ("holds `ROLES.md` and the briefs") (01:39)
  - F13 [scale: line-value] the header says "Revision 2" -> next: no record
- 4: verdict: "Revision 4 does not stand as written. The direction stands"
- 6: F1 "Frame 1's check is circular." Next: "frame 1 becomes a pilot with a baseline count before any ledger" (01:39). F2 "R4 fixes cause 1 with prose, and it calls the failure findability." Next: "every frame gains a `Searched:` field after `Site:` at the push" (01:39). F9 and F10: no record; revision 6 then removed the ledger and its back-fill (01:58).
- 7: not sure — I searched the frame's block only

### D14. plans/frame298-design-review.md
- 1: date 2026-10-18 (861cd414); frame 298, the design; kind: design review; asked by: rule — the line that started it: not found (the 12:20 line is cut; result line archive stack-2026-10-21.md, 2026-10-18 12:36)
- 2: diff no; brief not found; frame line not found; goal of the frame yes (M1 to M4); destination no (review page)
- 3: 12 findings
  - F1 [scale: function-file] the send door refuses every relay with `guess:<item>` -> next: repaired (12:40)
  - F2 [scale: approach] line 2 resolves on three clocks -> next: repaired ("picks the line's row once") (12:40)
  - F3 [scale: frame] M1's truth is seeded by the guess -> next: repaired ("the deliver merge's `git diff --name-only`") (12:40)
  - F4 [scale: frame] M3 has no instrument -> next: repaired ("a hand reading capped at 30 a night") (12:40)
  - F5 [scale: function-file] no refusal text for a touch or stopped page -> next: repaired ("a third refusal text") (12:40)
  - F6 [scale: frame] five merged items take about four nights -> next: repaired ("the close needs one night") (12:40)
  - F7 [scale: approach] pass 2 records under a door that refuses -> next: no record by name (the line counts "twelve amendments") (12:40)
  - F8 [scale: frame] the (c) residue is a known wall -> next: repaired ("Frame 299 is pushed") (12:40)
  - F9 [scale: function-file] `touch_guesses` class and key -> next: repaired ("class relation keyed ...") (12:40)
  - F10 [scale: function-file] one `batches.guess` call per session -> next: no record by name (12:40)
  - F11 [scale: approach] the guess relay lacks the working set -> next: no record by name (12:40)
  - F12 [scale: words: what a build needs] -> next: no record by name (12:40)
- 4: verdict: "approve the shape, amend before pass 1."
- 6: F3 "M1's truth is seeded by the guess it measures." Next: "the truth for M1 and M2 is the deliver merge's `git diff --name-only`". F4 "M3 counts the cue's misses with no instrument that can see them." Next: "M3 and M4 are a hand reading capped at 30 a night". F6 "Five merged items take about four nights." Next: "the close needs one night and M1 and M2 run on over about four nights". F8 "The (c) residue is a known wall, not a prediction." Next: "Frame 299 is pushed from section 7.1 for the (c) replies, next sprint." (all 12:40)
- 7: not sure — I searched the frame's block only

### D15. plans/rulings-seam-design-review.md
- 1: date 2026-10-27 (e679a348); frame: the rulings seam, sprint 33 row 1, worktree rota_p337; frame number not found (the status line sits in frame 330's archived block); kind: design review; asked by: rule — the line that started it: not found (result line archive stack-2026-11-02.md:61, 2026-10-27 00:18)
- 2: diff no; brief not found; frame line not found; goal not found; destination no (review page)
- 3: 14 findings
  - F1 [scale: function-file] the every-line rule reads silence on the read-back line as approve -> next: repaired ("reading: refs are exempt") (00:18)
  - F2 [scale: approach] park and shift pages return before the line -> next: repaired ("present and confirm pages only") (00:18)
  - F3 [scale: approach] the order is built again at ruling time -> next: repaired ("into the ask's body_refs") (00:18)
  - F4 [scale: function-file] `_faulted_approve` no longer refuses -> next: repaired ("C1 to C5 stay on the whole reply") (00:18)
  - F5 [scale: function-file] `_earlier_reading` lets an earlier span pass -> next: repaired (same) (00:18)
  - F6 [scale: function-file] `_land_shift` bypasses the writer -> next: repaired (00:18)
  - F7 [scale: function-file] keypress rows collide -> next: no record
  - F8 [scale: approach] the view has no order for `superseded` -> next: no record
  - F9 [scale: function-file] three readers are not named -> next: repaired ("three more readers join passes 2 and 4") (00:18)
  - F10 [scale: approach] doubt 1 cites the wrong misuse -> next: no record
  - F11 [scale: approach] the wait on frame 330 is not needed -> next: no record
  - F12 [scale: approach] a smaller design covers F1 to F3 in about 11 cycles -> next: repaired ("the third design is taken") (00:18)
  - F13 [scale: function-file] `_table_of_ref` refuses nothing today -> next: no record
  - F14 [scale: line-value] the head moved during the review -> next: no record
- 4: verdict: "The design stands with changes."
- 6: none
- 7: not sure — I searched for the result line only

## Gate lines

| Frame | Line 1 | Line 2 |
|---|---|---|
| 282 (R21) | not found | not found |
| 355 (R22) | 2026-10-31 18:20 (rota-fc): "new reds 1, real, test_the_mark_has_one_writer ... The fix goes to the same implementer by message, then the gate runs again before the commit." | 2026-10-31 18:57 (rota-fc): "new reds 0; reds gone 0; stale 0. Pass 1 committed at 31e5fe47. Review p1 runs on the worktree at it" |
| 363 (R23) | 2026-11-10 10:00 (rota-82): "1 new red, `test_the_parked_frame_never_prints`, and the gate marks it flaky ... The implementer is resumed for two commits" | 2026-11-10 12:12 (rota-82): "33 failed against a baseline of 33, 0 new reds ... The diff review of pass 1b runs" |
| P12, W12 (R24) | 2026-10-28 12:16 (rota-a5): "7 new reds against the stored baseline, 0 flaky, and all 7 are the known set ... 0 from the lands" -> night 174 launched | not found (the 09:31 line says "6 the known reds and 1 flaky", with no "new red" words) |
| 354 (R25) | 2026-10-31 21:12 (rota-fc): "new reds 1, real, test_the_landing_brief_names_every_menu_option ... One sentence goes into the landing brief by message" | 2026-10-31 23:04 (rota-fc): "new reds 0; reds gone 0; stale 0. Pass 6 committed at e51b540d. Review p5 runs" |
| 296 (R26) | 2026-10-18 11:51 (rota-04): "new reds 0; reds gone 1, the flaky handover drought test; stale 0 ... Pass 1 accepted at 9c4b5368." | not found |
| 302 (R27) | 2026-10-23 15:17 (rota-45): "new reds 2 ... Judged here: the three commits are reverted on the branch before night 159" | 2026-10-23 17:55 (rota-48): "new reds 0; reds gone 1 ... Passes 1 to 2c accepted on the gate and reviews 1 and 2." |
| 220 (R28) | not found in the frame's lines (frame 286's line of 2026-10-18 00:44: "the long gate on b0dbd926 accepted with no red of this frame's own") | not found |
| 267 (R29) | 2026-10-16 20:11 (rota-e7): "9 new reds, the known 8 and the flaky `scene_challenged_again` ... Waits on the review alone." | 2026-10-16 20:40 (rota-e7): "11 new reds, the known 8 and three flaky ... Accepted at 98b7b562." |
| 356 (R30) | 2026-11-01 03:47 (rota-40): "new reds 1, test_one_claim_wakes_exactly_one_standby, ... green alone ... Pass 1 committed at cb758ccd. Review p1 ... runs" | 2026-11-01 07:40 (rota-40): "new reds 0; reds gone 0; stale 0. Pass 2 committed at eeed30cc." |
| W11 (R31) | 2026-10-28 13:31 (rota-27): "gate 6 known reds, 0 new, no cassettes in the worktree ... Review p2 on the same reviewer" | not found |
| 226 (R32) | 2026-10-13 16:48 (rota-ff): "the gate from a worktree reads 8 new reds, the 7 known and 1 flaky, 1 gone, no re-record, piped through tail so its stale line is unread" | 2026-10-13 17:07 (rota-ff): "new reds 8, the 7 known and the flaky `test_scene_challenged_again`, reds gone 1, stale 0" -> "Validating at fbde40e6." |
| 315 (R33) | 2026-10-26 07:21 (rota-f9): "8 new reds, 1 flaky and green on its rerun ... The residue's two commits, 44ea0f9b and 01c0f5fa, are accepted on the branch." | not found |
| 114 and 183 (R34) | not found in frame 114's lines; frame 182's line of 2026-11-10 03:34 names "one gate on the full checkout, build 2 and frame 173 included" | not found |
| 222 (R35) | 2026-10-16 04:52 (rota-05): "10 new reds, the known 8 and the two flaky ... Passes 1, 1b and 1c committed at 531582af." | 2026-10-16 06:38 (rota-05): "10 new reds, the known 8 and two flaky ... Pass 1d committed at c5f67351." |
| 309 (R36) | 2026-10-23 19:25 (rota-7e): "new reds 7, 6 flaky ... and 1 real, test_schema_has_no_clock ... Not accepted on this gate. Pass 1c is sent" | not found |
| 362 (R37, R40) | 2026-11-03 09:12 (rota-5b): "6 new reds, all 6 flaky timing cases ... the slice's harvester are accepted on rota/foundation." | 2026-11-06 13:59 (rota-28): "new reds 0, reds gone 2, stale 0 ... Slice 1 of the owed contest is accepted on the checkout." |
| 200 (R38) | 2026-10-11 10:59 (rota-88): "new reds 0; reds gone 0; stale 0 ... Pass 1b runs on." | 2026-10-11 12:17 (rota-88): "new reds 0; reds gone 0; stale 0 ... Pass 1 holds at dd583398." |
| 339 (R39) | 2026-10-27 00:20 (rota-70): "8 new reds, 0 stale ... The two red cases are read before any fix, by C76" | 2026-10-27 01:16 (rota-70): "6 new reds, the known five and test_handover's watcher test, flaky ... Frames 339, 340 and 330 and row 4 stand on it." |

## Counts

By kind of judge. Diff reviews: 19 (R21, R22, R24 to R40). Other: 1 (R23, the meta review). Design reviews: 8 (D8 to D15).

Findings by scale:

| Kind | Findings | line-value | function-file | approach | frame | direction | words |
|---|---|---|---|---|---|---|---|
| Diff review | 124 | 17 | 97 | 4 | 0 | 0 | 6 |
| Other (meta) | 5 | 0 | 0 | 0 | 0 | 5 | 0 |
| Design review | 96 | 9 | 19 | 40 | 20 | 1 | 7 |

Next acts by class:

| Kind | repaired | owed | set aside, reason | set aside, no reason | no record |
|---|---|---|---|---|---|
| Diff review | 79 | 18 | 7 | 0 | 20 |
| Other (meta) | 2 | 3 | 0 | 0 | 0 |
| Design review | 62 | 0 | 0 | 0 | 34 |

"repaired" includes "repaired in part" in R21 F1, R23 F3, R24 F1, R27 F1 and R39 F4. A repair counted here can be one that a later look found incomplete (R22 F1, R31 F1, R39 F8, D11 F6).

Reviews with a finding at scale frame or above: diff 0 of 19; other 1 of 1; design 7 of 8 (all but D15).

Given to the judge (yes counts):

| Kind | diff | brief | frame line | goal | destination |
|---|---|---|---|---|---|
| Diff review (19) | 19 | 19 | 0 | 6 | 0 |
| Other (1) | 0 | 0 | 0 | 0 | 1 |
| Design review (8) | 0 | 5 | 0 | 5 | 2 |

Asked by: diff reviews, rule 19 of 19, with the starting status line quoted for 14 and not found for 5 (R24, R31, R32, R38, R40). Other: Roman 1. Design reviews: rule 8 of 8, with Roman's ruled note also for D11; the starting line not found for 3 (D13, D14, D15).

Cell 7: diff reviews, yes 4 (R21, R24, R28, R32), no 8, not sure 6, not searched 1 (R34). Other: not searched 1. Design reviews: not sure 8.

## What I could not find

- The brief files of the reviews. They sit in session scratchpads, so "brief yes" means only that the page or the status line shows numbered points.
- Whether any reviewer got the frame's heading line: no record found for any of the 28.
- The status line that started R24, R31, R32, R38, R40, D13, D14 and D15. Several lines are cut in the stack at a fixed length in my reads, and I did not read their full text.
- The frame numbers of P12 (R24), W11 (R31) and the rulings seam (D15).
- A gate line for frames 282, 220 and 114, and a second gate line for several frames (see the table).
- The next act by name for D14 F7, F10, F11 and F12. The status line counts "twelve amendments", and the review has twelve findings.
- For the design reviews, cell 7 rests on each frame's own block only.
- R31 F6 and R36 F4: the review's own fix line says "none" or names a step outside the code, so "no record" may be the expected act.

## A reading, apart from the tables

I formed one while I read. In this part, the diff reviews name faults at the line and the function, and the session repairs most of them in the next pass. The design reviews are the only judges here that name the frame's measure, its price or its cause. The one review that reads at the direction scale is the meta review that Roman asked for. The lows of the design reviews more often get no recorded act than the lows of the diff reviews. The later faults that I found under cell 7 sit at the same function as the review, and in a shape that no point of the review's brief asked about. This reading is one reader's, on 28 pages.
