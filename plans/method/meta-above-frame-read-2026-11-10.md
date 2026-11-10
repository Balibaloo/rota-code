# The units above the frame, and how each one ended: a read of the records, 2026-11-10

Result: the records hold 114 units larger than one frame. 21 finished with a line, 8 stopped on a decision with a reason, 44 gave way to a new unit, 21 only stopped being cited, 15 are alive, and 5 fit a new class. Of 361 frames, 218 closed with a line and 88 are open and silent.

Short names: S is `plans/stack.md` at commit 51eda0be. A-date is `plans/archive/stack-<date>.md`. CP is `rota/COMPLETION.md`. R is `plans/method/reference.md`. OF is `plans/operating-facts.md`. N-sid is `plans/method/handoff-<sid>.md`. LTP is the long term plan of 2026-10-31. All dates are in 2026.

## 1. How the read found the units

- I read the head of S, lines 1 to 1690, whole. This part holds the redirect, the long term plan, sprints 8 to 35, "## Stack" and "## The batches".
- I took sprints 2 to 7 from the history, each from the last commit before the next sprint replaced it (`git show 17e67ca31~1:plans/stack.md` and five more). Sprint 1 lives in a status line of 10-11 00:40.
- A script read every frame block of S and of the 40 archive files: the heading, the section, and each status line with its date.
- Four agents on Opus read the parts I did not: 09-10 to 10-18, the standing measures, 10-26 to 10-31, and 11-01 to 11-10. Each got the six classes and no expected result. I checked 15 of their quotes against the files. All 15 hold.
- A unit is in the list when it names two or more frames, steps or entries, and stands outside one frame's own Ends-when line. A design frame is in the list when its head line says that it holds other frames.
- The count per kind: order of frames 16, plan with steps 16, list 5, direction 7, standing measure 20, design frame that holds frames 14, target 2. That is 80. The Sprint sections are 34 more.
- The classes: 1 finished, and a line says so. 2 stopped by a decision, with a reason. 3 replaced, and a line names the open parts. 4 replaced, no word on the open parts. 5 no end. 6 alive today. I add 7: the unit stops because the thing that fed it stops, and no line names the unit. I add 8: the unit waits on an answer that does not come.
- "Who" codes: R is Roman's words in the record. R-ok is his "ok" to a session's proposal. Sn is a session alone. Rule is a rule of R.

## 2. The units that are not Sprint sections

| # | Kind | Unit | Start, who | Parts | Last sign of life | End | The open parts |
|---|---|---|---|---|---|---|---|
| 1 | target | "Core, by capability" and the completion line, CP:14 | 09-12, R: "Roman confirmed the statuses" (CP:20) | 11 partials, 28 built | 11-04, capability 11 added (04b794f0) | 6 | 9 partial, 1 built, 1 parked. No frame cites the page from 09-17 14:24 to 10-31 02:50 (checked by `git log -S` and an archive grep). |
| 2 | plan | The plan of 09-10, ten goals, CP:153, frames 1 and 2 | 09-10, "agreed". His words: not recorded | 10 goals | 09-17 18:22, frame 2 | 5 | 4 done by frame 1's text of 09-14, which never changed. 6 have no end line. Frames 1 and 2 are open. |
| 3 | plan | "The order from here", CP:192, which is frame 4 | 09-14, R: "Roman owns this order" (CP:328) | 7 steps | 10-31, the LTP names steps 4 to 7. Own last status 09-21 | 6 | 1 done, 1 "not needed", 1 built and never walked (frame 33), 4 unbuilt. |
| 4 | plan | "Four small frames and two campaigns", frame 1's status | 09-17, R ruled the bands | 6 | 09-17. The LTP names them again on 10-31 | 5 | Pushed 0 of 6. The trigger, frame 2's close, never fired. |
| 5 | plan | Model setup, ten steps, CP:332 | 09-11, R's extension. "Not built. Not ruled." | 10 | 09-16, `plans/model-setup.md` | 5 | Two pages disagree: all ten ran, or 5 built and 5 open. |
| 6 | plan | Post-core list, the long-runs test, "After the split", CP:406 to 512 | 09-12 to 09-14, R | 6 items, 1 test, 1 task | 09-14. The LTP names the long-runs test | 5 | No work is recorded on any of them. |
| 7 | plan | The completion diary, tracks A to D, `plans/archive/completion-diary.md` | 08-28 | not counted | 09-13 | 3: "the live account is `rota/MAP.md` and `rota/COMPLETION.md`" | The open track items: not traced. |
| 8 | plan | The responsibility audit, five phases, in `plans/archive/` | before 09-03 | 5 phases | 09-03 | 1: "Status: CLOSED (2026-09-03)" | None. |
| 9 | plan | "Roman's plan for the session", frame 17, A-09-16:9 | 09-16, R | 5 steps, frames 16 to 22 | 09-16 | 1 | All 7 frames closed on that day. |
| 10 | order | The tooling chain, `plans/archive/tooling-flow-2026-09-17.md` | 09-17, R ruled the order | 9 frames and frame 4 | 09-17 | 1: "the chain is done except frame 4" (line 3) | 4 frames "closed by ruling". Their measure moved to a later frame's close. |
| 11 | order | The first stack and its "Parked" bullet list (6b47d0b5) | 09-14, Sn on R's ask for one file | 9 frames. 8 bullets then, 26 today | 09-23, the last bullet added | 5 for the list | 6 frames closed, 3 open. No bullet has a closing line. |
| 12 | order | The order of 09-18: 43, 38, 37, 33, 41, 42 | R | 6 | 09-20 | 3: "This replaces the order of 2026-09-18" | Done 1, carried by name 5. |
| 13 | order | The order of 09-20: "46, next just work your way down the table" | R | 10 | 09-21 | 3, after one day | Done 0, carried 10. |
| 14 | order | The order of 09-21 00:29 and the two rulings of 13:40, S:1512 | R | 13 | 09-21 | 3, after 14 hours (S:1552) | Done 1, carried 12. |
| 15 | holder | Frame 62, "batch the open frames" | 09-21, R: "make the next session start with a batching frame" | 21 frames, 4 batches | 09-21 14:05 | 1 | Of the 21 frames, 10 are closed today and 11 are open. |
| 16 | order | The eight-step batch order, S:1551 | 09-21, R ruled it from four options | 8 steps | 09-27, "before batch B's repairs" | 5 | Done 3, half done 2, no word 3. S:1509 still says "Read the batch order for what to work next". |
| 17 | order | Batch A, the cassette key | 09-21, frame 62 | 4 frames, then 5 more | 09-23 | 1: "**The batch is closed.**" (S:1628) | Frames 68 and 69 "popped unstarted and parked as one item". |
| 18 | order | Batch B, what a seat lost on night 88 | 09-21, frame 62 | 1 read, 4 frames | 09-28 | 5 | The read ran. 0 of 4 frames closed. 2 are parked. Frame 57, his own ask, has one status line. |
| 19 | order | Batch C, the night's stall | 09-21. The label reached 78 frames by 10-10 | 78 | 10-10 | 2: R "Ok", 10-07 00:55, "24 frames closed in five days against 32 pushed in two" (S:1683) | 44 closed, 34 open. 20 of the 34 have no status line after 10-08. |
| 20 | order | Batch D, the principal seam | 09-21, frame 62 | 2 frames, then 4 more | 10-09 | 4: the order of 10-09 does not name frame 42 | 3 closed, 3 open. Frame 42, his ask, has one status line, of 09-18. |
| 21 | order | The rulings of 09-24: frame 82 first, then 83 and 82 at once | R | 5 frames | 09-25 | 1 | All 5 closed. |
| 22 | order | "The order from here", 09-25 14:34, S:1590 | R: "Do it" | 5 items, 1 frame | 09-27 | 4: the order of 10-04 names none of them | Done 2, half done 2, no word 2. |
| 23 | order | The order of 10-02 14:30, in a status line of frame 110 | R | 6 | 10-04 | 3 | Done 4, carried 2. |
| 24 | order | The order of 10-04 12:50, S:1613 | R | 11 frames | 10-07 | 3 | Done 6. 5 are open today. |
| 25 | order | The order of 10-07 00:55, S:1683 | R: "Ok" | 4 items | 10-08 | 1 for items 1 to 3 | Item 4 is the stop of batch C. It has no end line. |
| 26 | holder | Frame 144, the night databases as a test tier | 10-05, R's question | 5 items, 11 passes | 10-07 | 1: "the 5 went to frames 172 to 175" | 3 of those 4 frames are open today. |
| 27 | holder | Frame 190, what the principal sees (the order of 10-09, S:1685) | R chose it from three options | 7 frames as walls, 4 night walls | 10-10 | 4 for the walls: "closed into frame 193" names a residue and no wall | 0 closed with it. 3 closed later. 4 are open, 3 of them with no later status line. |
| 28 | holder | Frame 193, the second request | 10-10, R | 3 walls | 10-11 00:30 | 1 | Frames 185 and 192 still read "Waits on: frame 193". |
| 29 | holder | Frame 200, the build loop design | 10-11, R's sprint order | 7 frames, 138 status lines | 10-13 15:10 | 1, by its residue rule. The close names 5 other frames | The 7 held frames: 0 closed, all open today. Cost: 46 cycles against 8 to 10. |
| 30 | holder | Frame 204, what a seat's note is for | 10-11, R | 4 passes | 10-17 | 2: parked 10-21, "no live session holds the frame" | 2 passes built, 1 moved to frame 198, pass 4 no word. The reason is the frame count, not the parts. |
| 31 | holder | Frame 252, the wall guide reviewed | 10-15, R: "add a review frame" | 3 steps | 10-16 22:30, "The Fable review is still owed" | 5 | Step 1 done. Steps 2 and 3 have no later line. |
| 32 | holder | Frame 287, the meta workflow | 10-17, R: "this is a serious flaw with the meta workflow" | a grill, 4 reads, 5 build steps | 10-18 05:23 | 1: "closed. The five build steps ... are in the tree" with 5 commits (A-10-18:70) | It pushed frames 294 and 295. Both are open and silent. Cost: 29 cycles against 4. |
| 33 | direction | The night gives the order: one sprint at each night's read (C46) | 10-11, R-ok. The rule: R, 10-12 23:40 | 35 sprints, nights 144 to 175 | 10-29 00:50 | 2: R, 10-29 01:53, "instead of faffing with nights ...". "Nights stop." (S:153) | Section 3. The ruling's section has no word on the open rows of sprints 32 to 34. |
| 34 | direction | Three nights validate a frame ("night k of 3") | 10-15, R | 22 frames waited on a night on 10-29 | 10-28 | 7 | 15 closed, each with its own line. 1 parked. 6 open. 85 of 133 Ends-when lines in S still name a night. |
| 35 | direction | The fact as the unit: F1 to F37, sprint 26, frame 344 | 10-26, R's question. "the reading is the session's" (S:417) | 37 facts | 10-30 14:42 | 1: "33 of 37 FIXED ... 4 PARTIAL" (A-10-30:418) | The 4 PARTIAL: 2 sit in open frames with no later line, 1 went to frame 353 which does not name it, 1 went to frame 351 whose heading is lost. |
| 36 | direction | Test cases in place of nights: the 24 L3R cases, frames 345, 347, 348 | 10-28, R: "less doors and more in depth test cases" | 24, 12 and 41 cases | 11-01, "L3R 22 of 25" | 3: the loop goes to frame 352 | Frame 352 is unclaimed and has one status line. The cases still run in the gate. |
| 37 | direction | The Gemma trial of frame 323 | 10-25, R's ask | 2 nights | 10-26 18:26 | 2: R, "I only want to replace with gemma if it can do everything" | None. |
| 38 | direction | The Gemma trial on the 24 cases | 10-29, R: "and maybe a Gemma trial" | 1 count, 2 models | 10-29 07:31 | 1: "the Liaison seat runs on gemma4:12b-it-qat" (A-10-30:63) | No line sets the one-seat switch beside the ruling of row 37. |
| 39 | direction | Dry runs with the session in the Principal seat | 10-31 00:58, R: "Use it yourelf" (S:124) | 13 runs | 11-10 04:27 | 6 | Dry runs 1 to 3 merged. Of the next 10 runs, 1 merged, and its claim was false (arm run 1). |
| 40 | target | His three conditions for his seat, S:127 | 10-31, R | 3 | 11-10 | 6 | "Multiple repos" has a reached line (11-02). "Multiple changes" has none. "Responsive" has no measure. |
| 41 | plan | The long term plan, S:69 | 10-31 03:04, R: "Ok then long term plan and execute" | 7 steps | 11-10, "The long term plan below stands" (S:25) | 6 | Step 1 half. Steps 2 and 3 reached, with a line. Step 4 in work. Steps 5 to 7 no later word. |
| 42 | list | The records' debts in the plan, S:113 | 10-31, Sn, from the audit | 6 items | 10-31 | 5 | No frame was pushed for them. 39 of 41 "Waits on: Roman's order" lines remain. 4 of 7 recommendations have no later word. |
| 43 | plan | The onboarding design, frame 362 | 11-03, R: "it has to be designed both ways" | 26 parts | 11-08 | 5 | 17 done, 3 in part, 1 carried by name, 5 with no later word. Its cycle count stops at 11-06 with no line. |
| 44 | plan | The contested record design, `plans/design-contested-record-2026-11-06.md` | 11-06, Sn: "No question goes to Roman" | 4 slices | 11-10, a hand-off note | 5 | 2 built, 1 carried in N-33f037c1:86, 1 gone. |
| 45 | plan | The false claim design, frame 360 | 11-06, Sn. R ruled on it four times | 5 parts | 11-08 17:35 | 5 | 2 built, 1 carried in a note, 1 gone, 1 not recorded. |
| 46 | list | The "known issues" of 11-06 02:01, S:1859 | R's words. The session wrote the entries | 4, then 1 more | 11-10, frame 364's Sprint line | 5 | 3 done, 1 open in four frames, 1 gone in the main. No line counts them or says they are resolved. |
| 47 | plan | The milestone: capability 11's measures on three tiers, S:1859 | 11-06, R: "this is the next source of issues and the next milestone" | 3 measures on 3 repositories | 11-10, N-33f037c1:89 | 6, as a name in 7 hand-off notes | Not started. Its owed parts have no later line. |
| 48 | plan | The pause plan, `plans/pause-read-2026-11-06.md` | 11-06 04:30, R's question | 8 lines | 11-07, N-8b2312ef:29 | 8: "not answered. Do not ask again." | 0 built. The 4 later notes do not name it. |
| 49 | order | The frames moved "to the front by C77" | 11-08 10:49, Sn, after R's question on root cause | 13 frames, then frame 171 | 11-09 23:41 | 4: the redirect names 5 of them | 8 of 13 have no status line after the move. No block changed its place in the file. |
| 50 | plan | The redirect, S:17, frame 363 | 11-10 00:32, R: "I want you to take charge of redirecting the project" | 7 items, 4 lines, 1 test on two cycles | 11-10 04:14 | 6 | Items 1 to 5 in work. Items 6 and 7 have no status line. |
| 51 | plan | The worker shape, `plans/method/build-session-design-2026-10-29.md` | 10-29, R's ask | 9 amendments | 10-29 | 5, until the redirect's item 7 names it | 1 built (3a05db0d). |
| 52 | list | `plans/method/amendments.md` | 10-18, the design of frame 287 | 4 entries | 10-18 | 5 | None ruled. The C46 change of 11-10 did not go through the page. |
| 53 | list | Frames 331 to 334, "the four frames Roman agreed to" (S:555) | 10-25 23:21, R-ok to three | 4 | 10-26 18:10 | 5 | 4 of 4 have one status line, the push. |
| 54 | list | The close-read sweep of 10-30 | Who started it: not recorded | 17 frames | 10-30 17:48 | 1 | 9 closed. 8 got a "Residue" line. 5 of the 8 have no later line. |
| 55 | holder | Frames 345, 347 and 348, each on the last one's residue | 10-28, R's go | 3 conditions each | 10-31 01:55 | 1, three times | The last residue, seven edges, went to frame 352. |
| 56 | holder | Frames 340 and 342, the status tool's refusals and the close gate | 10-26, Sn | 3 parts each | 10-29 05:16 | 2: R, "No don't make it a hard rule, the model should be smart enough to do it" (S:492) | The two built refusals came out the same night. |
| 57 | holder | Frame 341, the wall guide prices by reach | 10-26 | 3 parts | 11-02 23:22 | 2: parked, "parts 2 and 3 wait on the count to 2026-11-10" | Part 1 built. No line of 11-10 yet. |
| 58 | holder | Frame 353, the instrument and the cold walk | 10-30, then LTP steps 1 and 2 | 3 parts | 10-31 12:36 | 1: all "met", part 2 "on its second branch: the cold walk reached no merge" | The close does not name the residues of frames 311 and 328. |
| 59 | holder | Frame 362 | 11-03, R | about 60 runs, reads, designs and builds. 13 sessions, 249 status lines | 11-10 04:27 | 6 | Its Ends-when names the onboarding slice. Its last 50 status lines name other work. |
| 60 | holder | Frames 357, 358, 360, 361, handed on as a set | 11-01 to 11-02 | 4 | 11-06 and 11-08 | 6 | Each waits on a count "of the next 3" runs. 9 hand-offs moved them. The last 2 wrote no line in them. |
| 61 | measure | The walk register, `tests/rota/walks.jsonl` | 09-11 (09cb4e24), a plan step marked "Not built. Not ruled" | 156 rows | 10-26, two rows of night 166 | 5 | 153 rows are older than 09-23. Nights 90 to 165 and 167 to 175 have no row. No dry run has a row. |
| 62 | measure | One read per night, `plans/night<N>-read.md` | 10-01, night 103. A ruling for it: not found | 66 files | 10-29, night 175 | 2, with row 33 | Its section 0 changed form twice with no line. |
| 63 | measure | The wall list in each run's read (W1, W-A) | 10-15, night 149 | one list per read | 11-08, dry run 8 | 6 | The label form changed three times. No rule for it was found. |
| 64 | measure | The cause of each wall by `plans/wall-guide.md` | 10-15, R ruled the guide | nights 149 to 169 | 10-26 | 4: night 170 has a fact column in its place | Night 175 and dry runs 4 to 8 place no wall by cause or fact. |
| 65 | measure | Made-up turns per night, `rota.tools.nightcount` | 09-23, R: "count first, then fix the runner" | 68 logs | 10-29, night 175 | 7 | No dry run has a count. |
| 66 | measure | The door count per night (C35) | 10-15, R | not counted | 10-29 | 7: "W14's count moves to the cases" (S:170) | No line for the other doors. |
| 67 | measure | One read per CYCLE line of a night (M12) | 09-29, R | 18 files | night 174 | 7 | None. |
| 68 | measure | The seat measure, OF:380 to 390 | 10-31, LTP step 2: "The baseline for his seat is written" | 6 entries | 11-02 | 4 | Dry runs 4 to 8 have no entry. Their numbers are in the run reads. S:63 still cites "his pages per run". |
| 69 | measure | One read per dry run, `plans/dry<N>-read-<date>.md` | 10-31 | 13 runs, 12 with a read | 11-08 | 6 | Blind run 1 "is not read". 5 reads and `plans/dry9/` are not committed. |
| 70 | measure | The nine counts of frame 362 in the dry reads | 11-04, the run brief | 5 reads | 11-07, dry run 7 | 4: dry run 8 has seven other counts | No word. |
| 71 | measure | The key score of the survey, `plans/dry3-key-score-2026-11-03.md` | 11-03, R's question | 2 entries | 11-03, dry run 4 | 5 | Dry runs 5 to 8 have no score. |
| 72 | measure | A request key before the run, and the four lines after a run (S:43) | 11-10, frames 364 and 363 | 2 keys, 1 set of lines | 11-10 | 6 | New. One entry each. |
| 73 | measure | The frame economy, "N live of 10" | 10-18, `plans/method/design.md`:103, reasoned | one count per sprint and per state print | 11-10, "17 of 10" | 6 | No recorded count is at or below 10. |
| 74 | measure | "Cycles: actual N of M" on a closing status (C42) | 10-11, R | 33 of 225 closed frames | 10-18, then 3 single lines to 10-26 | 5 | About 60 frames closed later with no such line. The rule stands at R:360. |
| 75 | measure | The gate line and the gate baseline | 09-17, frame 30 | about 380 lines, 10 baselines | 11-10 03:34 | 6 | OF:242 still names the baseline of 10-11. |
| 76 | measure | The model bench table, `probes/bench/RESULTS.md` | 08-25 | 11 rows | 09-23 | 5 | Later model trials are in status lines only. |
| 77 | measure | CP as the log of night results | 09-10 | not counted | 09-17 | 2: "The page takes no status update after 2026-09-17" (CP:11) | "the stack says where the plan stands" (a2f658d3). |
| 78 | measure | One hand-off note per leaving session (C10) | 10-09, R: "1 yes" | 101 notes | 11-10 | 6 | The clause that a note leaves at its frame's close stopped after 10-15. |
| 79 | measure | One provenance read per new wall (C64) | 10-18, R | 32 files | 10-28 | 3: "C64's provenance read is step 3's second question" (R:491) | 13 dry reads carry a provenance section. |
| 80 | measure | The cost anchors, OF:244, "re-derive from the last three frames" | 09-17 | 4 lines | 10-11 | 5 | No later line. |

## 3. The Sprint sections

A row is one numbered row of the section. "Done" means one of three things, read before the next sprint's time. The row's frame closed. Or a status line of that frame inside the interval says built, landed or committed. Or the row was a night, a read or a count, and it ran. "Carried" means that the next section names the row's frame number or its label. "No word" means neither. Sprints 2 to 25 come from the script, with 10 results set by hand and 36 rows without a frame number judged by hand. Sprints 1 and 26 to 35 are by hand.

| Sprint | Written, and by whom | Rows | Done | Carried by name | No word | Note |
|---|---|---|---|---|---|---|
| 1 | 10-11 00:40, R-ok | 9 | 5 | 1 | 3 | Frames 198, 185, 192. Frame 185 has no status line since. |
| 2 | 10-13 05:47, Sn, taken by timeout | 12 | 2 | 10 | 0 | It lasted 9 hours. |
| 3 | 10-13 15:10, Sn, timeout | 14 | 7 | 7 | 0 | |
| 4 | 10-14 07:21, Sn, timeout | 16 | 7 | 9 | 0 | |
| 5 | 10-14 17:51, R: "Yeah sounds good" | 15 | 8 | 6 | 1 | Candidate F. Candidate E became frame 243. |
| 6 | 10-15 01:16, R: "Ok yes" | 15 | 5 | 10 | 0 | |
| 7 | 10-15 16:24, Sn, timeout | 15 | 8 | 7 | 0 | |
| 8 | 10-16 07:01, Sn, timeout | 16 | 4 | 11 | 1 | Frames 253 and 173 leave. Sprint 10 names both again. |
| 9 | 10-16 17:36, R: "Yes do it" | 16 | 4 | 12 | 0 | |
| 10 | 10-16 22:30, R: "Stop pausing for sprint orders" | 21 | 3 | 18 | 0 | |
| 11 | 10-17 04:31, Sn under that ruling | 20 | 5 | 15 | 0 | 2 rows are carried by "row 20's list, as sprint 11 had them". |
| 12 | 10-17 16:40, Sn | 15 | 6 | 9 | 0 | Row 14 is carried by "row 14's list". Row 0, frame 287, came at 17:38 on R's words. |
| 13 | 10-18 07:22, Sn | 9 | 5 | 0 | 4 | The 4 rows hold 44 frames, by number or by the two lists. Sprint 14 names none of them. |
| 14 | 10-18 19:30, Sn | 7 | 3 | 3 | 1 | "28 live of 10". Two rows became frames 302 and 303. |
| 15 | 10-21 16:23, Sn | 9 | 7 | 0 | 2 | It parks 12 frames "of sessions no longer live". |
| 16 | 10-23 17:51, Sn | 6 | 5 | 1 | 0 | |
| 17 | 10-24 01:10, Sn | 8 | 7 | 1 | 0 | |
| 18 | 10-24 05:58, Sn | 9 | 9 | 0 | 0 | |
| 19 | 10-24 10:32, Sn | 9 | 9 | 0 | 0 | |
| 20 | 10-24 18:20, Sn | 8 | 7 | 0 | 1 | The 63 re-records. Sprint 22 names them again. |
| 21 | 10-24 22:55, Sn | 7 | 6 | 1 | 0 | |
| 22 | 10-25 02:30, Sn | 7 | 6 | 1 | 0 | |
| 23 | 10-25 22:50, Sn | 7 | 4 | 3 | 0 | W-B, W-C, W-F "stay in night 166's read". |
| 24 | 10-26 07:32, Sn | 7 | 4 | 2 | 1 | Frame 312's second half. Sprint 26 names it again. |
| 25 | 10-26 18:08, Sn | 7 | 2 | 5 | 0 | C2, C3, C5 and W7 became frames 335 to 338. |
| 26 | 10-26 22:02, re-cut 23:06, R's question | 6 | 6 | 0 | 0 | Its list of 19 facts goes to sprints 27 to 31 by number. |
| 27 | 10-27 13:37, Sn | 5 | 5 | 0 | 0 | |
| 28 to 31 | 10-27 14:26, Sn under frame 344, on R's ask | 34 facts | 34 | 0 | 0 | One block. The borders of the four sprints were not kept. End line in A-10-30:285. |
| 32 | 10-28 05:56, Sn | 6 | 5 | 0 | 1 | W13. For row 2 the read ran. Its fix: not checked. |
| 33 | 10-28 10:38, Sn | 6 | 4 | 1 | 1 | W2, the claim tick, "the third night". |
| 34 | 10-28 14:18, Sn | 7 | 2 | 5 | 0 | Row 6 became frame 345. |
| 35 | 10-29 00:50, Sn | 7 | 0 | 6 | 0 | It lasted 68 minutes. Row 7, night 176, is "out" by the ruling. |
| 35, amended | 10-29 01:58, R | 4 | 3 | 1 | 0 | Inside row 4: the account page has no later word. The `_rota_record` question was never asked, and the LTP lists it as a debt. |
| 35, amended | 10-31 00:58, R. Its parts are "Recommended, not ruled" | 3 | 0 | 3 | 0 | The LTP of 03:04 carries all 3. The flaky set has no word after it. |

- The sum: 362 rows. Done 197, carried by name 148, no word 16, out by a ruling 1.
- Sprints 2 to 12 have 175 rows: 59 done, 114 carried, 2 with no word. Sprints 13 to 25 have 100 rows: 74 done, 17 carried, 9 with no word.
- The low rows of sprints 2 to 12 repeat. 33 frames stand in five or more sprints. Today 16 of them are silent, 7 closed, 6 live and 4 parked.
- The 44 frames that leave at sprint 14: today 28 are silent, 6 live, 6 closed and 4 parked. Sprint 15 names 4 of them again.
- Sprints 2 to 25 name 110 frames in their rows. Today 59 are closed, 31 silent, 11 live and 9 parked.
- Every section from sprint 3 on starts with one end line: "Night N ended sprint k ..., because it was that sprint's night". The line ends the sprint on the night. It does not speak of the rows.

## 4. The counts per class

| Class | Units of section 2 (80) | Sprint sections (34) | All units (114) | Frames (361) |
|---|---|---|---|---|
| 1. Finished, with a line | 16 | 5 (every row done: 18, 19, 26, 27, 28 to 31) | 21 | 218 closed or popped with a line |
| 2. Stopped by a decision, with a reason | 8 | 0 | 8 | 20 parked with a line |
| 3. Replaced, the open parts named | 8 | 19 (every open row carried by name) | 27 | 3 folded into a named frame (72, 191, 310) |
| 4. Replaced, no word on the open parts | 7 | 10 (1, 5, 8, 13, 14, 15, 20, 24, 32, 33) | 17 | 4 in the archive with no closing line (68, 69, 77, 251) |
| 5. No end | 21 | 0 | 21 | 88 open, no park line, no status line for more than 14 days |
| 6. Alive today | 15 | 0 | 15 | 28 open with a status line of 10-27 or later |
| 7. Stopped with its source, no line of its own | 4 | 0 | 4 | 0 |
| 8. Waits on an answer that does not come | 1 | 0 | 1 | 0 |

- The frames: the numbers 39, 44 and 351 have no heading. Of the 88 silent frames, 38 have one status line, the push. 36 of the 88 read "Waits on: Roman's order".
- By kind, classes 1 and 2 against 4, 5, 7 and 8: orders 5 against 6. Plans 2 against 9. Lists 1 against 4. Directions 4 against 1. Measures 2 against 11. Holders 10 against 2. Targets 0 against 0.

## 5. The units that ended with a record

- The 14 holders are frames, and a frame has a close rule (R, S1: "Pop it when its ends-when holds"). 10 of 14 end in class 1 or 2. No rule gives a section, a plan page or a measure an Ends-when line.
- The Sprint section is the one unit above the frame with an end rule, C46. All 34 got their end line. The rule ends the sprint at the night, so the rows end by a carry or by silence.
- Of the 8 class 2 ends, 5 quote Roman's words with a reason: rows 19, 33, 37, 56 and 62. 2 are parks of one frame by a session, rows 30 and 57. Row 77 is the page's own line. No session stopped an order, a plan or a direction with a reason.
- The class 1 units are short. 15 of the 16 end within four days of their start. The start of row 8 is not recorded.
- The two cleanest ends give each part a mark in one place. Row 17: the batch table strikes each frame with its date and names the two left over (S:1628). Row 35: one audit page holds a verdict for each of 37 facts, and the close line counts them (A-10-30:418).
- A clean end of the unit does not settle the parts it held. Row 29 closes with 0 of its 7 frames closed. Row 26 hands 5 items to 4 frames, and 3 are open. Row 35 hands 4 facts on, and 2 of them have no line today. Rows 55 and 36 hand a residue down three frames to frame 352, which nobody holds.
- Two class 1 closes record their cost against the price: 46 cycles against 8 to 10 (row 29), and 29 against 4 (row 32). Sprints 28 to 31 carry a price of about 120 cycles and no actual.
- 3 of the 20 measures end with a line. 11 stop with no line: 5 just stop, 3 are replaced by another form, and 3 stop with the nights.

## 6. What this read could not see, and where the method can have bent the result

- I did not read the transcripts. An order that Roman gave in the terminal and no session wrote down is not in the list.
- The run briefs live in session scratchpads. "No later word" means no later line in S, the archives, the hand-off notes and the pages under `plans/`.
- I did not read `plans/method/meta-*.md`, `plans/meta-review-2026-11-10.md`, `plans/method/handoff-5ee5ec0b.md` or `plans/method/product-*.md`. The redirect section quotes the meta review. I took none of its sentences as a result.
- "Done" in section 3 is generous. It counts a build that landed, and many of those frames stayed open for more nights. Rows that are a night or a read count as done when they ran. A stricter rule, the frame closed, gives a lower count.
- "Carried by name" is a number in the next section's text. It says nothing about work. For sprints 8 to 35 I read today's text of each section, and 2 sections changed after they were written (12 and 34).
- The frame classes come from a pattern on the last status line and from a limit of 14 days. I read 25 odd cases by hand. A silent frame can be a frame that waits by intent.
- Class 1 says that a line states the end. I did not test the statement. Frame 353's part 2 is "met" with no merge.
- The agents got my list of candidate units as a start. It can have held them to my kinds. They added rows 10, 12, 23, 53 and 54, and the loss of frame 351's heading.
- I checked 15 of the agents' quotes and not their counts. The counts of rows 19, 34, 35, 43 and 59 are theirs alone. Row 59's "about 60" comes from cut lines.
- No agent read 10-18 to 10-26 outside the Sprint sections. Units of those days that are not sprints can be missing: `plans/retro-2026-10-18.md`, `plans/wall-research.md`, `plans/model-scan-2026-10-25.md`, frame 314's flow chart.
- The unit borders are mine. Rows 37 and 38 can be one unit, and row 55 can be three. Row 33 and the 34 sections count the same sprints twice, once as a direction and once as sections. Each choice moves a class count by one to three.
- S grew by 5 lines during the read. The line numbers of S:1 to S:1690 did not move. Lines below them can be off by 5.
