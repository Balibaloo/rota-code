# The method's reach, 2026-10-26: where the build session decides the size and the site of a fix

Meta workflow. Roman asked on 2026-10-26: "we found significant issues in the workflow. What follows?" Read only, at 85ae074a, by one agent on Opus. Sources: `plans/method/intent.md`, `plans/method/reference.md` whole, `plans/method/design.md`, `plans/wall-guide.md` sections 0, 1, 3, 4, causes 12 and 16, `plans/composition.md`, the frame 251 block (`plans/archive/stack-2026-10-15.md` line 172), the frame 287 block (`plans/archive/stack-2026-10-18.md` line 18), frame 252 (`plans/stack.md` line 2150), `plans/night168-read.md` sections 2 and 5, `plans/night169-read.md` sections 2 and 5, `.claude/agents/*.md`, the stack head and frames 339 to 342, and the briefs `agency_template.md`, `f330_pass5_brief.md`, `f340_review1_brief.md`, `n169_read_brief.md` and `f339_reach_brief.md` in session 8db3a3f9's scratchpad. `f330_pass1_brief.md` and `f330_review1_brief.md` do not exist there, so pass 5 and frame 340's review 1 stand in for them (observed: `find` in the scratchpad).

## The result

The method sets the site of a fix before it reads the reach, and 23 places downstream read that site (reasoned: section 3). The night read places a wall at the door that fired, the push writes `Site:` first, the price class follows the door, and the brief, the review, the gate and the close all check the fix against that site (observed: the rules cited in section 1). Tonight's changes reach 6 of the 23 places, and 2 of the 6 are parked (reasoned: section 4). The three method frames of tonight carry a `Reach: 1 of 1` that the session wrote with no read, and frame 341's line is wrong: at least five other places price a fix (observed: section 4). So the method fix repeats the shape it fixes. The smallest place that covers the reach is one record, the frame's `Reach:` line written by the read agent, with every other place reading it (reasoned: section 5).

## 1. The path of a wall, from the CYCLE line to the close

| Step | Rule, ruling or build, with its date | What the step decides about the size or the site |
|---|---|---|
| 1. A CYCLE line fires | M12, read it at once (ruled: 2026-09-29); C55, stop a night that loops on a known frame's wall (ruled: 2026-10-09); C56 (taken by timeout: 2026-10-16) | The site of attention is the first wall that loops. Nothing about size (reasoned) |
| 2. The night read, section 2 | The read brief's shape (`n169_read_brief.md`: "each placed by section 4 of `plans/wall-guide.md`, and say ... whether an open frame's Site covers it"); C34 (ruled: Roman, 2026-10-15, frame 251) | The site is the hop or the door where the sign shows: guide step 3 "the first hop that differs", step 4 "Did a door fire". Night 169's W1 is "cause 8" at the removal door (observed: `night169-read.md` section 2) |
| 3. The night read, section 5 | The largest wall first (reasoned: intent, his questions of 2026-10-13); C42 anchors (ruled: 2026-10-11) | Each row names a site, one red test from the night's turn, and a price of 1 to 2 cycles (observed: `night168-read.md` section 5, ranks 2 to 6) |
| 4. The match | Guide section 4 step 1, by sign (2026-10-15); C76 step 2, by symptom (ruled: 2026-10-26) | A wall joins an open frame by its sign. Facts under different causes never meet (reasoned: section 2) |
| 5. The push | C41 `Site:` first (ruled: 2026-10-11); C67 five lines (ruled: 2026-09-27); C30 and C31 the Ends-when (ruled: 2026-10-03); C46 the `Sprint:` line (ruled: 2026-10-12) | The site is fixed as the first field before any read. C31's ratio takes its baseline "from the night that found the wall", so the measure is the door's instance. C46 rides a frame in this sprint when it "costs under three cycles" |
| 6. The sprint order | C46 sprint end (ruled: 2026-10-12); C47 the session picks (ruled: 2026-10-12); C48 start row 1 at once (ruled: 2026-10-16); C40 a sprint is "one seam design and three or four small frames" (ruled: 2026-10-11) | The budget holds one seam a sprint. Every other row is a door (reasoned: C40's text) |
| 7. The reads before a fix | C32 the turns (no origin); C33 the interview (ruled: 2026-10-02); C64 the provenance (ruled: 2026-10-18); C76 step 3 the reach (ruled: 2026-10-26) | C32, C33 and C64 read the one mechanism and the one seat. Only C76 asks for other places (observed: section 10 text) |
| 8. The decision | C34 "A fix is cheap or it goes to Roman" (ruled: 2026-10-15); the guide's "Cheap fix" lines, "A door is one or two cycles" (cause 8) | Cheap means a door. A seam is not cheap, so it is escalated or cut down (reasoned) |
| 9. The pass brief | C32 the session writes the fix brief; C39 one implementer; `implementer.md` "You change nothing outside the brief" | The site of the edit is the brief's file and lines. `f330_pass5_brief.md` gives five points and line ranges, and no reach line (observed) |
| 10. The review | C53 one review per pass (ruled: 2026-09-27); `reviewer.md` "Answer every numbered point in the brief first" | The review checks the session's points. `f340_review1_brief.md` has six points on the diff and none on what the fix leaves (observed) |
| 11. The judgement and the gate | C53 judging part "the gate on the commit, the findings against the known ones"; C51 the gate (no origin) | Correct at the site. The gate counts new reds and knows no reach (observed: the rule texts) |
| 12. The walk and the night count | C54 (no origin); C35 a door's count (ruled: 2026-10-15) | The count is over the door's instances on nights, "fires on a of n" (observed: C35) |
| 13. The close | C31 residue rule: "That cause is a new frame" (ruled: 2026-10-03); cause 8's close at 0 of 0 over three nights (ruled: 2026-10-15); C42 actual beside estimate | The frame closes on its door. The next reader's failure opens a new frame. 45 of 48 one-door frames had a later frame at the same fact (observed: `closed-reach-2026-10-26.md`) |
| 14. The memory strike | C69, C70 a habit goes to memory with a strike count (proposed: 2026-09-23) | A repeat becomes one more record at its sign (reasoned) |

## 2. What exists that already asks for the reach, the purpose or what exists

| Rule or record | What it asks | Why it did not produce the reach |
|---|---|---|
| Guide step 1 and cause 16: "Two or more open frames under one cause become one design frame" (2026-10-15) | A merge of frames | The guide's 16 causes come from composition sentences about hops, seats and records (observed: guide section 1). No sentence says a fact has one reader. "Every record has one writer" covers writes only (observed: composition, Records). So one fact sits under several causes: his ruling is cause 2 on night 168 W7 and cause 8 on night 169 W1 (observed). The merge never fires (reasoned) |
| Cause 16, "sizes the fix by its budget", confirm: "the scope read names the seam and every instance over every night" | The failure itself, by name | Section 4's eight steps never reach cause 16, and its instances are over nights, not over the code (observed: section 4 text) |
| Guide section 3: the count "with the reach as the denominator"; C35 | A reach | The reach is a door's instances on the nights' records, not the code's readers (observed: section 3; frame 251, status 02:43) |
| C52 and `map`: "a table's writers and readers" | A reader list, as a tool | It fires at the brief as a grep shortcut, after the site is set (observed: C52 sits in section 5, `implementer.md`) |
| C64 provenance read (2026-10-18) | The purpose | It reads the one mechanism the frame names (observed: C64 text) |
| Frame 287's design: retrieval by "the frame, the file, the door and the law" | What exists | A door key returns that door's history. Step 4 wrote law lines at 143 doors, one per door (observed: frame 287 status 04:56). Roman declined a triage of 124 open frames into wall-groups at 03:17 (ruled: "I don't like the direction") |
| Intent: "a fix must generalise", "I want to prevent over fitting" (ruled: 2026-10-15 01:54) | Generality | The guide made overfit a field about the night's words, a phrase against a state, not about the code's other readers (observed: section 3, the "Overfits" fields) |
| Frame 252, the guide reviewed after three reads (ruled: 2026-10-15) | Whether placements pointed at the fix that held | Open since 2026-10-15, two reads logged, no review (observed: `plans/stack.md` line 2150) |
| `f339_reach_brief.md`: "The list decides the size of the fix" | The reach, before C76 | One frame's practice, not a rule (observed) |
| Memories `rota-general-solution-from-what-exists` (20:21) and `rota-read-before-fix` (21:18) | The same rule | Written twice in one hour, 1 strike each, two records of one fact (observed: memory files) |

## 3. The reach: every place in the method that decides a fix's size or site

23 places (reasoned: the path of section 1 and the texts it cites):

1. The night read brief's placement column, "Open frame's Site". 2. The night read's section 5 rows: site, one red test, price. 3. Guide section 4, first answer stops, steps 3 and 4 place at the hop or door. 4. The guide's "Cheap fix" price lines and section 0's "a wall costs one or two cycles and not five to seven" (ruled: Roman, 2026-10-15, "Yes that's exactly it"). 5. C34, cheap or escalate. 6. C42 and the cost anchors in `plans/operating-facts.md` line 239. 7. C40, the sprint cut. 8. C46, the placement under three cycles. 9. C41 and C67, `Site:` first at the push. 10. C30 and C31, the Ends-when ratio from the night's sign. 11. C32 and C64, the reads of one mechanism. 12. C33 and C36, the interview of one seat. 13. C35 and guide section 3, the door count. 14. The match by sign or symptom, guide step 1 and C76 step 2. 15. The pass brief, C32 and C39. 16. `implementer.md`, "nothing outside the brief". 17. The review points, C53 and `reviewer.md`. 18. The session's judgement, C53. 19. The gate, C51. 20. The close, C31's residue rule, cause 8's 0 of 0 rule, C42's actual. 21. The sprint order, C46 sprint end, C47, C48. 22. The memory strike, C69 and C70. 23. C57, escalate after three cycles or a spent budget.

## 4. Tonight's changes against the reach

| Change | Places covered | Note |
|---|---|---|
| C76 (ruled: 2026-10-26) | 11 (adds the reach question), 15 (the brief carries the count), 20 (close at one reader) | Text. C34 stays beside it unamended: "stop at the first answer" and "cheap or ... Roman" against "Build at the reach". Two rules of one moment, no reconciler (observed: section 10) |
| Frame 340, built at d1c934ae | 15 and 20, by a status line | It checks that a `Reach:` line exists, and the session writes that line (observed: frame 340 Ends-when). A hand edit meets no gate (observed: pass 2 deviations). It refuses, and design.md section 2 says a tool "never refuses the session" (ruled: Roman, 2026-10-18 02:25, "enabling not inhibiting"). C64's amendment of 2026-10-25 asks that a departure from his ruling is asked (reasoned) |
| Frame 341, parked | 3 and 4 | Its line "Reach: 1 of 1, the guide is the one page that prices a wall's fix" is wrong: places 2, 5, 6, 7 and 8 price too (observed: their texts). No read ran (observed: no status line) |
| Frame 342, parked | 20, the zero baseline | `Reach: 1 of 1` with no read (observed) |
| Sprint 26 by fact | 21, and part of 7 | Night 170's rows still come from the night read by wall (observed: stack head rows 1 and 2) |

Covered: 6 of 23, 2 of them parked. Left: 1, 2, 5 to 10, 12 to 14, 16 to 19, 22, 23 (reasoned: the table). The largest gaps are 1 and 9: the night read and the push still set the site before any read, so a C76 read starts from a frame whose `Site:` already names the door (reasoned: frames 341 and 342 show it, observed).

## 5. The proposal, at the smallest place that covers the reach

1. One record: the frame's `Reach:` line, written by the C76 step 3 agent from `agency_template.md` question 3, never by the session, names the fact, its one reader and each place by file and line, and `Site:` derives from it (C41, C67).
2. The placements read it: the night read brief's column becomes "the fact, and the frame whose Reach line holds it" (`n169_read_brief.md`), guide step 1 matches by fact, and C46 places by it (frame 341 folds in here).
3. The prices read it: C34, C42 and the guide's cheap-fix lines price one reader for N places, and a reach above one reader is a seam with its night by C42 (sprint 26 head).
4. The checks read it: the pass brief quotes it, the reviewer's first fixed point is "which places of the Reach line the diff leaves", C31's mechanism names the one reader, and the close reads it (C76 steps 6 and 7).
5. The tool prints and does not refuse: `state` prints the Reach line beside each held frame, and frame 340's two refusals go to Roman as a departure from "enabling not inhibiting" (design.md section 2; C64, 2026-10-25).

Price: one text sweep of C31, C34, C41, C42, C46, C53, guide section 4 and its price lines, and the night read and review brief templates, by a sweeper and one review, about 3 cycles; the `state` print, 1 cycle; about 4 cycles, about 40k of session context, about 250k agent tokens (reasoned: C42 anchors). A text change and one small tool, with no rota night. The measure is frame 341's count, frames closed at one door while a Reach line reads above one, from 48 of 56 toward 0 over two weeks. Section 0's ruled price line and C34's ruled words change only on his word, so they go to `plans/method/amendments.md` (ruled: reference.md head).

## 6. The doubt

1. The text already asked for most of this: cause 16, step 1's merge, `map`'s readers, the generalise intent, and two memories tonight. The session then pushed 341 and 342 with self-written reach lines in the same hour. So the fault may be in how the session applies the text under a budget of twenty cycles and largest-wall-first, and one more text place may join the unapplied ones (reasoned).
2. The reach counts come from agents briefed with a wide reach definition, and an agent asked to count N finds N. That one reader at the source costs less than the doors it replaces rests on 45 of 48 later frames, not on a priced pilot (reasoned).
3. Not read: `plans/closed-reach-a.md` to `-d.md`, the frame 287 investigation pages, and the transcripts on whether "yes update" ruled the two gates (observed: this read's scope).
