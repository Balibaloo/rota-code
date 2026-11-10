# The work loop, read from 24 closed frames, 2026-11-10

A blind read. The reader got no hypothesis. The reader did not open `plans/method/meta-*.md`, `plans/meta-review-2026-11-10.md`, the redirect section of `plans/stack.md`, or the blocks of frames 363 and 364.

## 1. The draw

- Seed: `random.seed(20261110)`, then `random.sample(closed, 24)`. The list `closed` is sorted by frame number, lowest first.
- A frame heading has the form `### <n>. <title> (<date>) (<session id>)`. The stack and the archive hold 361 such headings, numbers 1 to 364.
- Closed means: the block stands in a `plans/archive/stack-<date>.md` file. Rule C71 says "Closed frames leave the file". 40 archive files hold 225 frames. The draw came from those 225.
- `plans/stack.md` holds 136 frames. I found no closed frame among them. Frame 252 carries a "closed" line that belongs to frame 251.
- 11 of the 24 were pushed before 2026-10-10. No second draw was necessary.
- The 24 in draw order, with the push date and the close date: 95 (09-29, 09-30), 255 (10-15, 10-16), 55 (09-20, 09-22), 225 (10-13, 10-14), 345 (10-28, 10-30), 296 (10-18, 10-21), 298 (10-18, 10-21), 178 (10-07, 10-08), 301 (10-21, 10-24), 261 (10-16, 10-17), 120 (10-04, 10-05), 101 (09-30, 10-01), 58 (09-21, 09-23), 223 (10-12, 10-17), 103 (10-01, 10-01), 72 (09-23, 09-23), 336 (10-26, 10-30), 340 (10-26, 10-29), 210 (10-12, 10-12), 219 (10-12, 10-15), 131 (10-05, 10-07), 338 (10-26, 10-30), 41 (09-18, 10-08), 110 (10-02, 10-02).

## 2. The table

The source of every field is the frame's block and its status lines. I checked the 32 commits that the closes name with `git log`. All 32 exist. The After field comes from keyword searches of the later frames, the later night reads and the dry run reads. "n" is a night. Tokens are the harness line of the agents.

| Frame | Spotted | Placed | Built | Measured | Closed | After |
|---|---|---|---|---|---|---|
| 41 | Roman's idea, no run. Later n92 (1 merge) and n132 (1 walk). | Roman's "ok" to a three-frame order, 20 days after the push. Unpriced. | Probe code `probes/agent_principal.py` and a brief. 3 passes, 3 reviews. | n133 read by an Opus agent, 10-08: 83 calls, 82 landed, 43 contests. | "closed on night 133's read" | Not a wall. The ruling of 10-31 puts the build session in the seat. |
| 55 | The session's 4 re-records of 1 case: 20 of 20 red. | "Roman orders it". Probe 40k. The claim's reason: not recorded. | No code. Probes about 25k, 3 sessions. The cause stood in `plans/operating-facts.md` from 09-09. | The session's query of the register, 09-22, and Roman's answer. | "Roman ruled the write-off, and the frame closes" | Seen again: the case reads green on 09-23 (frame 65) and 0 of 1 on 10-14 (frames 202, 237). |
| 58 | The diagnosis of n88: 12 of 191 sessions are 4 sessions run 3 times. | Roman's order of the batches. 40k. | Core code, `d68c38a`. 1 pass 76.7k, 1 review 91.4k. | The holding session read n90 while it ran, 61 minutes after launch: 2 keys differ at turn 1. | "closed at `f251a51`, on night 90's evidence, read while the night still ran" | Seen again: n131, 7 sessions on one prompt hash, every turn the same. Frame 183, open. |
| 72 | Roman's words and one code line. No run. | Blocked on Roman. 10k. | Nothing. | Nothing. | "popped, folded into frame 66", 7 minutes after the push | Frame 66 salts the ids. Frame 73: nine cases fail a salted run. |
| 95 | n98's walk read: 1 session drops 13 lines. n97 lost 1 line by another route. | Roman's word to run frames side by side. 120k. | Door code, a note in `code.write`. 4 passes 175.8k, 3 reviews 112.5k. | n100 read by an Opus agent: the sentence fired once, the offer 8 times, "no seat took an offered span". n99 reached no path. | "closed, proved on night 100" | Seen again: n121, a span write drops 13 lines of `confirm()` beside the note. Frames 140, 173, 313, open. |
| 101 | A reviewer's probe in frame 97, then 1 session on n103. | Roman, by phone. 70k. | Wake code, `bb7156b`. 2 passes 67k, review 53.4k, cause read 69.7k. | The session's read of 1 session, s170, on n104, 1 minute after the merge. | "closed at a8ab7ff ... Ends-when met on both cuts." | Not seen in 2 searches. |
| 103 | Frame 102's gate, 1 run: 89 of 99 rows misread. | Roman's "Ok" to the recommendation. 55k. | One test. 2 passes 36.8k, review 32.4k. | The gate's new-red line at `a8ab7ff`. A tool. | "closed at a8ab7ff: the gate's new-red line no longer names the register-key test" | The test shows red or flaky in 7 later gates. The same cause: not recorded. |
| 110 | n106's read: 7 challenges, 1 batch. The scope read found two parts of the push line wrong. | "Roman rules the order: 110, 111, 112". Unpriced, then "about 30k". | Brief, wake and door code. 5 passes 157.3k, 1 reverted. Scope 106.6k, 2 reviews 148.5k, interview 66.9k. | The gate at `4eb5a9a`. n107 "fired no challenge on a crashed test". The frame's own case stays red "by design". | "**Closed.** ... the frame closes on the gate alone" | Seen again: n119 to n127, tests pass a plain function to `CliRunner.invoke`. Frame 131. |
| 120 | Frame 119's design read: 1 wake on n113, 0 of 3. | Roman's order of 12:50. 50k. | Wake code. 2 passes 82.9k, 2 reviews 85.9k. | n119, two blind reads that agree: 7 of 7 wakes hold source, from 0 of 3. n117 and n118 reached no path. | "closed on night 119." | The same sign by another cause: 3 of 9 wakes on n120, 17 of 39 on n121. Frame 127. |
| 131 | n119's two blind reads: 2 of 3 batches. The fault of frame 110. | Roman's order, 2 days later, after 4 more nights showed it. 65k. | Door code in `tests.encode`. Read 170.5k, 2 passes 187.3k, 2 reviews 139.9k. | n128 read by an Opus agent: 8 refusals in 2 sessions, 0 of 4 stored tests, from 3 of 3 on n127. | "closed. Night 128: the door refused 8 encodes in 2 sessions" | Seen again in new shapes: frame 176 (open), frame 230 on n145, frame 254. |
| 178 | Frame 170's merges read: 2 of 2 nights, 7 of 18 rows. | A low question, taken by timeout. 100k. | Door code, 3 checks. 3 passes 142.5k, 2 reviews 150.7k. | n131 read: 1 refusal of this frame, 0 of 2 rows. "The sample is small". | "closed. ... The frame closes on the three-part rule" | Seen again once: n137, 1 row names a file the diff does not touch. No frame. |
| 210 | n141's read and the session's query: 1 session. | The session, at once. 2 cycles, 80k. | Query code, six readers, `a2b70a84`. 1 pass 68.5k, review 60.9k. | n143 read: 23 of 23 wakes show the right state. | "closed on night 143" | Not seen. Frame 130 holds the same query from 10-04 and stays open. |
| 219 | n143's cycle read: 1 overwrite. The night read counts 4. | Roman's sprint order, row 7. 3 cycles, 150k. | Door code. Part 1 landed under frame 200. 1 pass shared with frame 187. 3 of 3 cycles. | n148 read: 0 of 10 principal rows changed, 1 refusal. | "closed on night 148 ... the supersede is frame 243's wall, this frame's wall by effect" | Seen again by another route, at the close: frame 243, open and parked. |
| 223 | Frame 200's value-wall read: 3 of 5 runs of 1 case. | Waited on frame 200. Claimed at n153's cycle line, 4 days later. 3 to 4 cycles, 250k. | Wake code and 1 sentence. 2 passes, 2 interviews, 1 review. "9 of 3 priced". | n154 read: 5 of 7 bodies pass, from 0 of 5. "the push fired on 0 of 19 challenge wakes". | "the frame closes; the push is unexercised" | Seen again: n161 and n162, Testers write a package that is not installed. Frames 304 (open), 317, 284 (open). |
| 225 | The session's read of n144 while it ran: 1 page. The night read counts 4 of 4. | The session, by C46: "costs under three cycles". 2 cycles, 100k. | Fold code. 5 passes, 3 reviews, 1 history read. | n147 read: 0 of 9 pages, 0 of 4 batches. Pass 2 landed after n146. | "**Closed.** Cycles: actual 10 of 2 over passes 1 to 2." | Not seen in 1 search. |
| 255 | n149's read: 3 of 3 replies. The scope read corrects it to 2 of 3. A count: 8 of 25 over 14 nights. | The session: "sprint 7, row 2". 2 to 3 cycles, 120k. | Door code. Scope 144.4k, 2 passes 184.1k, 2 reviews 165k. | n150, n151, n152 reads: "0 of 0" each. | "closed: night 152 shows 0 of 0 ... by cause 8's close rule" | Seen again on another route: n155 to n157, files corrections lost. Frame 298. |
| 261 | n150's read and a recount: 32 of 35 wakes, 1 walk. | The session: "sprint 8, row 1, the next night's wall". By timeout. 2 to 3 cycles, 120k. | Door code. 2 passes 125.5k, 1 review 45k. | n151, n152, n153 reads: 0 of 3, 0 of 6, 0 of 5 omit the draft. The door fired 0 times. | "closes. Night 153: 0 of 5 submits omitted the woken draft" | Not seen in 2 searches. |
| 296 | n156's read: 1 case. Pass 1's count: 19 fires, 7 moved the revise. | The session: "this sprint, row 1". 2 cycles, 60k. | A refusal text and tests. 2 passes, 1 review. "actual 4 of 2". | n158 read: 0 landings on n157 and n158, from 1. Fires of the text: not recorded. | "closed at night 158's read, night 3 of 3 at 0" | Seen again: n160, s290's `revise` on line 1 "cost bg_3". Frames 258, 305. |
| 298 | n156's read: 7 corrections, 2 of 3 batches dead. A count: 19 over 21 nights. | The session: "row 0". Roman rules the design. "10 or more cycles", 400k. | A table, a page line, briefs, doors. 7 passes, 5 reviews. "36 cycles over four sessions". | n158 read: 0 batches dead on n157 and n158, 3 of 3 corrections land on the guess line. | "closed at night 158's read: the ratio is met on the third batch" | Seen again in another shape: n160 and n161, batches die on a line-1 ruling. Frames 258, 305, 315 (open). |
| 301 | n157's read: 6 refusals in 2 sessions. The refusing door dates from 09-02, built "with no ruling". | The session: "sprint 14, row 2". 3 cycles, 60k. | Door code. 3 passes, 1 review, 2 gates. "6 cycles". | n158 to n160 reads: 0 cases. | "Met, and not exercised ... No night held a body that the predicate is about. Closed." | Not seen in 1 search. |
| 336 | A provenance read of n167 and n168: 6 pages, 8 of 318 red runs. | The session: "sprint 25, row 6". 1 cycle, 30k. | Page code. Read 90k, 3 passes, 1 shared review. "3 cycles of 1". | A close read by another session, 10-30: 0 of 2 pages on n171. | "**Closed.** Taken up by a9a43280 after session ac089aa1 spent with no hand-off" | Not seen. The nights stop on 10-29. |
| 338 | A provenance read: 7 of 19 relays over n160 to n168. | The session: "sprint 25, row 4". 1 cycle, 40k. | Relay code. Read 116k, 1 pass 72k, 1 shared review. "2 cycles of 1". | The same close read: 0 of 1, 0 of 1, 0 of 5 on n171, n172, n175. | "**Closed.**", the same words | Not seen. |
| 340 | Roman's ruling of 10-26 and a page: "0 of 14 at the source". 6 of 6 pass lines. | The session: "this sprint, row 1, before any pass". 2 cycles, 80k. | Tool code. 2 refusals built, then removed on his ruling "No don't make it a hard rule". About 5 cycles, 350k. | The closing session's script over the stack, 10-29: 17 pass lines with no Reach line, then 0. | "Closed on the records." | Holds: 13 of 13 frames pushed from 10-27 carry a Reach line (my count). |
| 345 | Roman's words of 10-28: "the night is the wrong scale of test". 24 wrong refusals on n170 to n173. | Roman's direction: "sprint 34, before row 2". 3 cycles and a review, 160k. | 24 cases, a runner, then design R, the Liaison's menu form. 40 passes, 15 reviews, 111 status lines. | The register at `24a4a4cb`, 10-30: 21 of 24 cases right on Gemma. A tool. No night. | "**Closed.** ... design R took the meaning doors out as one form" | Seen again: dry runs 5 and 6c, the menu's `add` keeps one sentence of three. |

## 3. The counts

Spotted.
- The observation comes from a night's read page in 10 frames. It comes from a read made for another frame in 6 (101, 120, 178, 223, 336, 338).
- The session's own run or query gives it in 4 (55, 58, 103, 225). Roman's words give it in 4 (41, 72, 340, 345).
- 16 of 24 start from one night or one run. 5 start from a count over more nights (178, 255, 336, 338, 345). 3 start from no run.
- A later read corrects a number or a fact of the push line in 4 frames (110, 219, 225, 255).

Placed.
- Roman's word places 11 frames. The session places 12. One is not recorded (55).
- Before 2026-10-12, Roman's word places 9 of 11. From 2026-10-12, the session places 11 of 13.
- The session's reason is the night that just ended in 9 of its 12 placements.
- 18 frames get their first work within a day of the push. 6 wait longer: 2 days (55, 58, 131, 219), 4 days (223), 20 days (41).
- 23 of 24 carry a price (41 does not). 22 of those have a recorded cost. 20 of the 22 cost more than the price. The middle frame costs about 3 times its price.
- The largest gaps: 110 (about 480k against 30k, the night read not counted), 131 (about 500k against 65k). Then 345 (40 passes against 3 cycles) and 298 (36 cycles against 10).
- No frame of the 24 records a new place or a new price after it passed its price.

Built.
- 19 frames change product code. 3 change a test, a probe or a tool (103, 41, 340). 2 change nothing (55, 72).
- Of the 19: 8 add or change a door or a refusal text (95, 131, 178, 219, 255, 261, 296, 301). 6 change what a wake shows (58, 101, 110, 120, 210, 223).
- 3 change a route or a fold (225, 336, 338). 2 build a new form (298, 345).
- A review finds a high or a medium defect in at least 13 of the 22 built frames. Each such finding gets a new pass.
- 18 of the 22 built frames need 2 passes or more. 4 need one (58, 210, 219, 338).

Measured.
- 13 closes rest on a night where the built thing met a case (41, 58, 95, 101, 120, 131, 178, 210, 219, 225, 298, 336, 338).
- 7 of those 13 rest on 3 cases or fewer (58, 95, 101, 178, 219, 298, 336). 6 rest on 7 cases or more.
- 5 closes rest on nights where the built thing met no case (110, 223, 255, 261, 301). In 223 and 261 the count moved without it.
- 3 closes rest on a tool or a script (103, 340, 345). 2 rest on a ruling (55, 72). 1 does not record the fires (296).
- A session that did not build the frame writes the close in 17 of 24.
- 3 ends-when lines count batches (131, 225, 298). The others count calls, wakes, rows or pages at one site.

Closed and after.
- 15 closes state a count of register lines. 13 say 0 or none. 2 say 1 (131, 255).
- No close of the 24 names a capability of `rota/COMPLETION.md`. The rule that asks for it dates from 2026-10-31, after every push in the draw.
- The issue is seen again in 13 of 24. The same sign: 7 (55, 58, 95, 110, 178, 223, 296). Another shape or route: 6 (120, 131, 219, 255, 298, 345).
- It is not seen in 8 (101, 210, 225, 261, 301, 336, 338, 340). 3 do not fit the question (41, 72, 103).
- By the closing evidence, the issue is seen again after 5 of the 7 closes on 3 cases or fewer. It is seen again after 3 of the 5 closes on no case, and after 2 of the 6 closes on 7 cases or more.
- No return reopens the closed frame. Each return is a new frame number or a count line.
- 10 of the later frames that hold these returns are open on 2026-11-10: 130, 140, 173, 176, 183, 243, 284, 304, 313, 315.

## 4. Per step: meant to do, does in fact, the evidence

The rules have dates. I hold a frame only to a rule that was in force on its day.

### Spotted

Meant to do. Find the failing turn first, then name a cause.
- [C32] "a cause goes on the stack only after the turns of the failing sessions are read: what each seat called, what came back, what it committed."
- [C76, steps 1 and 2, from 2026-10-26] "Find: the turn, what the seat was shown and what it sent, verbatim." Then "Match by symptom against the open and the parked frames, cheap, so no duplicate frame opens."
- [M12] "Push the frame while the night runs". [C34] "Every wall a read names is fixed, cheaply or by escalation".

Does in fact. The step turns one failure on one night into a frame with a site and a mechanism in its first line.
- 16 of 24 push lines rest on one night or one run. The push line names the site and the fix shape before any cause read.
- The turns are read, as C32 asks. Every wall frame quotes sessions, messages and counts.
- The push is not matched against open frames. Frame 210 names the query that frame 130 held for 8 days. Frame 130 stays open today.
- Frame 131 is the fault that frame 110 closed 3 days before. Frame 55 found a fact that `plans/operating-facts.md` held for 11 days.
- From 2026-10-15 a frame gets a count over many nights at the push or in its first pass (255, 296, 298, 301, 336, 338). The count sizes the sign. It does not change the site.

### Placed

Meant to do. Rank the frame by the wall it closes and by its cost, with the biggest issue first.
- [C46, from 2026-10-12] "A push is a placement". The rank is "by the wall it closes and the cycles it costs".
- [C42] "Every price line carries cycles beside tokens." [C30] The price comes with "the behaviour the price buys".
- [C47] "The session picks the next night's wall itself". [C77, from 2026-11-08] "The biggest root goes first."
- The intent page: "Fixes must outpace new walls, and the biggest issue comes first" (reasoned).

Does in fact. The step puts the newest night's wall in the next sprint row. The price is written and then not used.
- Before C46, Roman's word places 9 of 11. After C46, the session places 11 of 13. The blocks record no re-order by Roman for those 11.
- The session's reason is the night that just ended in 9 of 12. Examples: "sprint 8, row 1, the next night's wall", "pushed from its read".
- No placement in the draw compares the new frame with an older open frame.
- 20 of 22 frames with a price and a cost go over the price, about 3 times in the middle. No record shows a second look at the place.
- Frame 225 is placed "this sprint" because it "costs under three cycles". Its close says "actual 10 of 2".
- A drawn frame is a frame that was picked. The draw does not show the frames that were placed and left. Section 6 gives a rough count.

### Built

Meant to do. One agent builds, another context reviews, and the fix covers every place with the same gap.
- [C39] "One implementing agent per frame." "The writer never reviews its own diff."
- [C53] "One read-only diff review runs after every pass, whatever the pass touches".
- [C64, from 2026-10-18] "Every new wall gets a provenance read before its first fix".
- [C76, step 6] "Build at the reach. The pass brief carries the reach count."

Does in fact. The step builds a small change at the named site and then repairs it under review. The builder and the reviewer follow the rules.
- Every built frame has an implementer and at least one separate review. The review finds a high or medium defect in at least 13 of 22.
- The change is a door, a refusal text or a wake line in 14 of 19 product changes.
- The passes multiply. 18 of the 22 built frames need 2 passes or more. Frame 225 needs 5 for one precedence check.
- The 4 walls built after the C64 ruling carry a provenance or a history read (298, 301, 336, 338).
- A built door becomes a later wall. Frame 301 repairs a door that a session built on 2026-09-02 "with no ruling".
- Two frames build a form and not a door (298, 345). Both need a ruling by Roman first. Both cost the most.

### Measured

Meant to do. A night at the closing commit shows the mechanism at work and a ratio that moved.
- [C54] "A frame that touches the seats, the briefs, the write pipeline or a predicate ends on a walk."
- [C31, from 2026-10-03] The ends-when holds "the mechanism the seat meets". Then it holds "a ratio with a baseline from the night that found the wall, never a zero". Then it holds the residue rule.
- [C36] "A placement from one replay never gates, and the night gates the close."

Does in fact. The step asks one question: does the sign show at this site on the next night? The answer is often from few cases or none.
- The ends-when has the three parts in 11 of the 14 wall frames pushed from 2026-10-03. Frames 210, 336 and 338 have two parts.
- The night is the only instrument for a wall frame, and the night chooses the cases. 5 of the 19 closes that rest on a night met no case.
- 7 of the 13 closes with a case rest on 3 cases or fewer. Frame 58 closes 61 minutes into a night.
- A ratio can move with no help from the build. Frame 261: the door fired 0 times. Frame 223: "the push fired on 0 of 19 challenge wakes".
- The measure reads the site, not the walk. Frame 95 closes when the sentence fires once, and "no seat took an offered span".
- The session that reads the night measures frames that it did not build, from an agent's read page. That is so in 17 of 24.
- Two frames have a measure that is not a night: the gate's line (103) and a register of 24 cases (345).

### Closed

Meant to do. Close when the ends-when holds, with the cost beside the price, and count progress as capability.
- [S1] "Pop it when its ends-when holds". [C31] "the frame closes when its cause is not the cause the frame named. That cause is a new frame."
- [C76, step 7] "Close on two counts: the reach reads one reader, and the night's count moved. One without the other is a residue line."
- [C42] "The closing status writes the actual cycles and tokens beside the estimate". [C69] "The closing status names the count of register lines the frame wrote".
- The intent page: "Progress is rota's capability, not frames closed".

Does in fact. The step ends the frame's number. It does not end the issue. The rest of the issue gets a new number.
- The issue returns in 13 of 24. No return reopens a frame. Frame 255's close says it: "a later case reopens it as a new frame".
- The close moves what is left to other frames in its own words. Examples: "frame 243's wall, this frame's wall by effect", "its frame form is frame 284", "it is frame 176".
- 10 frames that hold those returns are open today. Frames 140 and 173 hold frame 95's wall, 6 weeks after "closed, proved".
- A close covers different things. Examples: 0 of 0 (255), "Met, and not exercised" (301), the gate alone (110), two nights for three (296).
- The close writes the actual cost beside the price, as C42 asks. No close acts on the gap.
- 13 of 15 closes write 0 register lines. The measure stays in a status line and in a night's read page.

## 5. The frames that do not fit

My reading is: one night starts a frame, a small fix lands at one site, a thin night closes the number, and the issue returns. These frames do not fit.

- 210 fits least. One pass covers six readers, the night shows 23 of 23, and the issue does not return. But the same issue sat open as frame 130.
- 345 fits least on the build. Roman's words start it, it grows to 40 passes, and a case register measures it. The loss still returns in dry runs 5 and 6c.
- 225, 338 and 336 close on real cases over one to three nights and are not seen again. 225 costs 5 times its price for that.
- 101 closes on one session one minute after a merge. By my reading it must return. Two searches find no return.
- 261 and 301 close with no case for the door. By my reading they must return. They do not, in the searched text.
- 120 and 131 close on 7 cases or more, and still return in another shape. A solid close does not stop the return.
- 298 is a design that Roman ruled, with a count over 21 nights. It still returns in another shape after 36 cycles.
- 41 is not a wall. It builds a tool for the nights, and its close rests on 83 calls.
- 55 and 72 have no build. 55 closes by a write-off, and its case reads green one day later. 72 lives 7 minutes.
- 340 is a rule about the loop. Its count is a script over the stack, and the habit holds on 13 of 13 later frames.
- 103 is measured by a tool on the same day. Its after state is not clear from the record.

## 6. What this read could not see, and where the method can have bent the result

- I read status lines. I did not open a night database, a test result or a diff. A status line can state a reason that was written after the choice.
- I cut most middle status lines at about 300 characters. A field that reads "not recorded" can stand in the cut text.
- The closing numbers come from status lines that cite a read page. I opened those read pages only through search excerpts.
- The After field is a keyword search. A miss reads as "not seen". The 8 frames in that group are the weakest part of the page.
- "Seen again" is my judgement of likeness from short excerpts. A strict reader counts the 7 with the same sign and not the 6 with another shape.
- I searched for returns. I did not search for proof that a fix held. The method finds a return more easily than it finds a fix that held.
- The nights walk one repository with the same few requests. A wall on those requests has more chances to return than a wall elsewhere.
- The nights stop on 2026-10-29. Frames 336, 338, 340 and 345 had only dry runs after their close.
- The draw holds closed frames only. It cannot show placement for the frames that were never picked.
- A rough word search of `plans/stack.md`: 134 open frames, 94 with no word of a pass or a commit, 45 of those pushed before 2026-10-10.
- "Closed" means archived. At least 4 archived frames carry no close (68, 69, 191, 310). Frame 72 in the draw is such a fold.
- The cost ratios mix tokens and cycles, and some prices leave out the night read. Read "about 3 times" as an order of size.
- The counts are from 24 frames. The split by closing evidence (5 of 7, 3 of 5, 2 of 6) is too small to carry weight.
- Rule C46 and rule C77 in `plans/method/reference.md` state findings of frame 363 and of the read of 2026-11-08. I read those two entries as rules.
- Some status lines of 2026-11-08 cite `plans/walls-root-read-2026-11-08.md`. I did not open that page.
- `plans/stack.md` changed while I read it. Line numbers moved by one or two between my commands.
