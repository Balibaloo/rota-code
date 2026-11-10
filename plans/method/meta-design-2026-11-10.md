# The design of the whole: five shapes and a control for the way of working, 2026-11-10

Written by one design agent for session 7fd2421e, on frame 363. Meta workflow. The page proposes. It rules nothing, and it changes no rule, tool or frame. Every proposal is (reasoned: this agent). Each count is the count of the page that the line names, and I checked none again.
Short names: R is `plans/method/reference.md`. S is `plans/stack.md`. D is `plans/method/design.md`. Comp is `plans/composition.md`. BSD is `plans/method/build-session-design-2026-10-29.md`. Map is `plans/method/meta-map-2026-11-10.md`. WE is `plans/method/meta-what-exists-read-2026-11-10.md`. AF is `plans/method/meta-above-frame-read-2026-11-10.md`. T2 is `plans/method/meta-connections-test2-2026-11-10.md`. TR is `plans/method/meta-transcripts-read-2026-11-10.md`. AG is `plans/f363-acting-gather-2026-11-10.md`. MR is `plans/method-reach-2026-10-26.md`.

## Result

1. The page holds five shapes and one control. Each shape is a whole way of working.
2. The control: a session puts a frame down with one reason on one line. Nothing else changes.
3. Shape A, the round: each run's read gives every open part one mark in one table.
4. Shape B, the plan sets the order: a frame serves a plan step with a measure outside the frame, and a step ends with a tally.
5. Shape C, the claim first: a session writes an expectation before a run or a build, and a compare closes the work.
6. Shape D, less form: the session removes the rules that ask for the next small step, and adds nothing.
7. Shape E, two seats: one seat judges and faces Roman, and cold workers hold one frame each.
8. Recommendation: build shape B in six small steps. Step 1 is the control. Step 2 is the part of shape D that crosses no ruling.
9. Shape B sends four questions to Roman: 1, 3, 4 and 5 of the section "The questions for Roman".
10. Largest doubt: shape B rests on one stretch of 69 hours with easy requests, and plans ended with a record in 2 cases against 9.

## What holds for every shape

- Every shape includes the control. The ruling of 2026-11-10 08:17 allows it, and no shape works while 88 frames are open and silent (AF).
- No tool refuses a session. Each tool does a step, or prints one line at the moment of an act.
- Each rule change goes to Roman through `plans/method/amendments.md` (R:6). The C46 change of 2026-11-10 did not go that way (WE, E6).
- Each test is a count over two runs, and then the count stops. The test still crosses "nothing measurable, we stay aware of all relevant points previously discussed without clutter" (Roman, 2026-10-17 18:19). Question 1 asks him.
- No shape repairs statement 5 alone. The product review holds the run's measure. A shape says what that measure must tell the session.
- The five moments are: a run's read, a push, a close, a hand-off, and the moment when a session sees that the size or the direction is wrong ("the wrong size").

## The control: put down, with a reason

1. **The idea.** A session can put a frame down by itself. It writes one reason on one line in one place. Roman reads that place, and he can pick any frame up again.
2. **The five moments.**
   - A run's read: no change. Each wall becomes a frame or joins one (C34, C77).
   - A push: no change.
   - A close: a frame has a third end beside the close and the park. The third end is the put-down.
   - A hand-off: the sender can put down a held frame that waits on nothing and that nobody builds. The taker gets fewer frames.
   - The wrong size: the session can put the frame down, and "the size is wrong" is a reason. The session can make work smaller only (T2, K2).
3. **What Roman sees.** One line per frame in the `## Parked` section of S, printed by `state --since`. Moments that need him: 0.
4. **Removed:** nothing. **Amended:** C34, one sentence: a wall not fixed now stays an open frame, or the session puts the frame down with a reason. C72: the session that holds the order can put down a frame of a spent holder. `## Parked` becomes one line per frame (D:104, written and not built). **Added:** about 6 lines in R.
5. **The tool step.** `status <n> --put-down "<reason>"` writes the line, moves the block to the archive, and commits. Sources: `rota/tools/status.py`, `handover.py drop --reason`, and the `Discharged:` record of AG. No tool moves a frame today (WE, statement 3, A4).
6. **Statements.** It answers statement 2 in part: one frame can leave. It leaves 1, 3, 4, 5 and the intake of statement 2.
7. **Rulings crossed:** none after the ruling of 2026-11-10. No question.
8. **The test.** It works if the 88 silent frames fall and each frame that leaves has a line. The 9 held frames of spent sessions leave the state print (Map, mass 5). It fails if the count of open frames grows again in two runs, as in "24 frames closed in five days against 32 pushed in two" (S:1683).
9. **Cost:** 1 pass for the tool. One agent drafts a reason for each silent frame, and the session judges the list. Nothing must be built first.
10. **Weakest point.** The intake rule stays, so the count grows again. A session alone can park, fold and bound today (T2, K2), and the count grew.

## Shape A: the round

1. **The idea.** The open work is one table, and the session writes the table again at each run's read. Each row is one part that a run showed, and each row gets one mark. A frame exists only for a row that the session builds before the next run.
2. **The five moments.**
   - A run's read: the tool opens the next table with each row that has no end mark. The session adds the run's walls. It marks each row: `build`, `joins row <k>`, `down: <reason>`, `model stops here` or `wrong question`.
   - A push: only a `build` row or Roman's word makes a frame. The frame names its row. It has no `Sprint:` line and no price.
   - A close: the close is a mark on the row, `done <commit>` or `left: <what>`. The part that is left stays on the same row. No new frame opens for it.
   - A hand-off: the taker reads the table first. The first item of the note names the row in work.
   - The wrong size: the session joins rows into one design row, or marks a row `wrong question`. The next read writes the table again, so the mark meets a choice.
3. **What Roman sees.** One line per round in `state --since`: the run's count, and the rows built, joined and put down. Moments that need him: 1 ruling at the start, then 0 per round.
4. **Removed:** C46 whole, the placement at the push and the four bullets (R:178, R:406). C47 and C49. The sprint cut of C40. The push sentence of M12. The last sentence of C34. The `Sprint:` field. The Sprint sections of S go to the archive. The economy line of `state` goes: it was over the cap in 180 of 193 prints (Map, mass 6). **Amended:** C31 (the remainder stays on the row), C76 step 7, the last sentence of C77, C48, C10. **Added:** one entry for the round. R: about 55 lines out, 12 amended, 22 in.
5. **The tool step.** `round open` carries the rows with no end mark, and it counts the rounds that each row has seen. `round mark` writes a mark with the clock. Sources: the batch A table (S:1628), the audit page of frame 344, the walls register of `plans/retro-2026-10-18.md`:56, the `Owed:` and `Discharged:` pair of AG, and `status.py`.
6. **Statements.** It answers 2 (the intake and the put-down), 3 (each part has a mark in one place) and 4 (a tool writes the table at the read). It answers 1 in part: a row can be a design. It leaves 5.
7. **Rulings crossed.** C46: "update guidance to make pushing frames a prioritization operation also" (2026-10-12 23:40). C34: "try to fix everything", then "Reasonably" (2026-10-15). The shape goes one step past the ruling of 2026-11-10: a wall can stay a row and never become a frame. Question 2.
8. **The test.** It works if each row of round 1 has a mark at round 2. The baseline is 148 of 362 rows carried by name and 16 with no word (AF). It works if a wall that returns goes to its old row. The baseline: no return reopens a frame (Map, K2), and 7 of 16 walls match frames that nobody built (S:48). It fails if rows have no mark after two rounds, or if every mark is `build`.
9. **Cost:** 4 passes: the tool 2, the state print 1, the rule sweep 1. First: the control, and the open frames written as rows.
10. **Weakest point.** The table is the Sprint section with a mark column. Sprints 2 to 12 carried 114 of 175 rows (AF). The newest run still sets the order, and statement 2 names that as part of the fault.

## Shape B: the plan sets the order

1. **The idea.** The order comes from one plan with steps, and a run gives the measure of each step. A frame exists because the measure of the open step cannot pass without the frame. A step ends with a tally of its parts, and the plan changes only by a written line.
2. **The five moments.**
   - A run's read: the read answers the measure of the open step first. The session writes one status line on the plan. A wall that stops the measure becomes a frame. The other walls stay in the read page, and the session puts them down as a group in one line.
   - A push: the block names the step. It says why the measure of the step cannot pass without the frame. A frame that serves no step says so, with the reason.
   - A close: the close writes the frame's mark on the table of the step. A step ends when its measure holds. The session then writes the tally: each part is done, moved by name, or put down.
   - A hand-off: the first item of the note is the open step, its measure and the last count. The take prints the same line.
   - The wrong size: a solution of any size inside the open step is the session's to build. A change of a step, of its measure, or of the order of the steps is one question to Roman.
3. **What Roman sees.** The plan once. Then one line per run and one tally per step, in `state --since`. Moments that need him: 1 at the start, 1 for each changed step, 0 per run. A new ask of his becomes one line on the plan: a new step, or the step that the ask replaces.
4. **Removed:** the amended sprint end of C46 with its four bullets (R:406 to R:432). The placement text of C46, "this sprint" and "next sprint, rank <k>". C47 and C49. The sprint cut of C40. The push sentence of M12. The Sprint sections of S. The economy line of `state`. **Amended:** C34 and C31 (the intake by the step). C46 (the step line at the push). C10 and C28 (the note and the take). C57 and [Autonomy] (the size inside a step). **Added:** one entry for the plan: its holder, its line per run, its end rule. R: about 45 lines out, 14 amended, 20 in.
5. **The tool step.** `status plan` writes the plan's line with the clock, as `status` does for a frame. `state` and `handover.py take` print the open step with its last line. Sources: `status.py`, the two lines of branch `f363state` (built and not merged), the plan of 2026-10-31 (S:69), the end test of the redirect (S:61), and the batch A table for the tally.
6. **Statements.** It answers 2 (the intake by the step) and 3 (a plan and a step get an end rule and a tally). It answers 1 in part: the size inside a step is free. It answers 5 in part: the measure is outside the frame. It leaves 4 for the old fields of a frame.
7. **Rulings crossed.** "Let's just keep working" (2026-10-18 03:17), which the session recorded as "the backlog keeps its shape". "They declare finished" (Comp, ratified 2026-09-16). "for now there is only cheap and escalate to me" (2026-10-15). The ruling of 2026-11-10 names a frame, and a step is larger. Questions 3, 4 and 5.
8. **The test.** It works if each pushed frame names its step and the reason. The baseline is 5 of 16 held frames (WE, statement 1, B). It works if the plan has a line after each run. The baseline: no status line cites step 4 after 2026-11-02 (T2). It works if each note starts with the step. The baseline is 0 of the notes after the first (Map, mass 7). It works if Roman's messages fall toward 8 in 69 hours, from 55 in 7 days (T2). It fails if a frame starts from the newest wall with no step line. It also fails if the plan's last line is older than the last run.
9. **Cost:** 3 passes: the tool with the two prints 1, the rule sweep with the note form 1, the first tally 1. First: the control. S:25 says that the plan stands and that the redirect is the order inside step 4.
10. **Weakest point.** The shape directs the work only as well as the measure of the step. The measure of step 4 is a merge with the session in the seat (S:95), and statement 5 names that fault. The evidence is one stretch of three days, and the three merges came "on the first build turn" (T2).

## Shape C: the claim first

1. **The idea.** A session writes what it expects before a run, a read or a build. It also writes the result that breaks the expectation. The compare closes the work, a failed expectation is a result, and a wall that the claim does not need is listed and left.
2. **The five moments.**
   - A run's read: the expectation is on the frame before the run starts. The first section of the read is the compare: held, failed or in part. The session then writes the next claim, on the least known fact about the destination.
   - A push: the block is the claim, the result that breaks it, and the act. The read agent writes the site after its read (MR:63). The block has no price.
   - A close: the compare closes the frame. "The claim failed" and "the question is wrong" are closes. A count of the fix's own output does not close a frame alone.
   - A hand-off: the note starts with the open claim and the result that breaks it. The taker's first act is the test or the compare, not the next pass.
   - The wrong size: the doubt is a claim. The session writes it with the result that breaks it, and gives it to one blind read. The result changes the order, or it ends the doubt.
3. **What Roman sees.** One line per compare in `state --since`, the failed ones first. Moments that need him: 1 ruling at the start, then 0.
4. **Removed:** C42, the price table and the actual at the close. 33 of 225 closes carry the actual (AF row 74). C35. The clause "under three cycles" of C46. "A fix is cheap or it goes to Roman" in C34. The price sentences of C30. **Amended:** C31 (the ratio becomes the claim), C41 (the site after the read), C54, C77, C10. **Added:** one entry. R: about 20 lines out, 12 amended, 18 in.
5. **The tool step.** `status <n> --expect` writes the expectation with the clock before the act. `status <n> --compare` prints the expectation and writes the result beside it. `state` lists each expectation that has no compare. Sources: the `--ruling` form of `status.py`, the `Owed:` and `Discharged:` pair of AG, the end test of the redirect (S:61), and the expectations on frame 363.
6. **Statements.** It answers 1: the unit is a claim at any scale. It answers 5 in part: a run is for one named count. It answers 3 in part: a unit that is a claim ends by its compare. It leaves 4, and it leaves 2 but for the control.
7. **Rulings crossed.** C47: "debug planing is relatively intuitive as long as it doesn't open large questions that lead you to do autonomous investigations first" (2026-10-12 23:52). C42, which he adopted on 2026-10-11 05:50. Question 6.
8. **The test.** It works if both runs have an expectation older than the run and a compare in the read. The baseline is 2 request keys and 1 set of lines (AF row 72). It works if one failed compare changes the next act, as the fold read changed point 5 of the product reading. It fails if both compares read "held" on a door count. The baseline is 116 of 157 frames closed on a door count (Map, mass 1).
9. **Cost:** 2 passes. First: the run's measure from the product review, because a claim about the destination needs that measure.
10. **Weakest point.** The shape makes the session's reading of Roman's word of 2026-11-10 the whole method. The reading is one day old. A session can write a claim that its own fix passes. A claim can stay at the scale of one door.

## Shape D: less form

1. **The idea.** The sessions saw the size alone in 5 of 8 moments and acted in 2. The form of the step gave the view no place (TR). So the session removes the forms that ask for the next small step. It adds only the control.
2. **The five moments.**
   - A run's read: the session reasons over the walls together, and C77 stays. It decides what to build. No rule says that every wall is a frame.
   - A push: four lines: what, ends when, the pointer, the status. The site comes after the read. No price and no `Sprint:` line.
   - A close: as today, with no price line. The remainder is a status line or a put-down, by the session's judgement.
   - A hand-off: as today. The hand-off tool stays as it is: 118 of 130 claims confirmed (Map, mass 6).
   - The wrong size: no form stands between the view and the act. No form asks for the view.
3. **What Roman sees.** The put-down lines, and a shorter rule page. Moments that need him: 1 large ruling at the start, on texts that he adopted.
4. **Removed:** three sentences of C34: "stop at the first answer", "cheap or it goes to Roman", "Every wall a read names is fixed". C42. The sprint cut of C40. C46 whole. C47, C49, C35. The push sentence of M12. "That cause is a new frame" in C31. The five rules that carry "leaves this page when the tool is proven": C24, C26, C68, C5, and C18 with C22 (R:13). The sentence at R:487 that says `state` prints the Reach line. The Stop hook that fires for no session (WE, F). The economy line of `state`. The hook line "If you are not blocked, continue working" (`.claude/settings.json`:18). The Sprint sections. **Amended:** C41, C72, and the idle rule of the brief with his limit of 2026-10-29. **Added:** the 6 lines of the control. R: about 100 lines out, 10 amended, 6 in.
5. **The tool step.** No new tool. `rota.tools.sweep` moves the texts.
6. **Statements.** It answers 2 at its rules and 1 at its forms. It leaves 3, 4 and 5. It gives no end rule to a plan.
7. **Rulings crossed.** "Ok, perfect now make sure that the meta workflow adopts these. This session and all future sessions" (2026-10-11 05:50), for the price and the sprint cut. "for now there is only cheap and escalate to me" (2026-10-15). The hook line is in the tracked settings since 2026-09-17, and I found no ruling for it. Question 7.
8. **The test.** It works if fewer product changes are a door, a refusal text or a wake line. The baseline is 14 of 19 (Map, mass 2). It works if a session acts on a size that it sees more often than 2 of 5 times (TR). It fails if the counts stay, or if the removed forms return by hand in the notes and the briefs. Two runs are too few for these counts.
9. **Cost:** 2 passes: one sweep and one review. First: the answer to question 7.
10. **Weakest point.** No case in the records shows that a removed text changes an act. The pressures that are not rules stay: the note in motion and a free agent slot, 5 of 8 moments each (TR).

## Shape E: two seats

1. **The idea.** One seat on the strong model faces Roman, judges, and holds the whole. It wakes at named moments, and it writes no status line, no brief and no merge. A cold worker takes one frame, lands it and ends (BSD, with his words "Interesting so the problem shifts").
2. **The five moments.**
   - A run's read: a worker runs the read and wakes the judge with the page. The judge writes the order and the put-downs.
   - A push: the worker pushes. For a frame that changes a seat's form, the judge first picks a shape from a design record (C76, step 3b).
   - A close: the worker writes a close record of five lines. The judge judges the record.
   - A hand-off: a worker ends with its frame and hands nothing on. The judge hands off about once in three days (BSD:126).
   - The wrong size: the worker writes one record and wakes the judge. The judge has no pass in motion at that moment.
3. **What Roman sees.** One seat that speaks with him. Moments that need him: 1 at the start, on the composition page. After that, his own asks.
4. **Removed:** nothing. **Amended:** the nine amendments of BSD:153 to BSD:170, of which 1 is built. Comp, "The build session". **Added:** the close record, the wake moments, two reserves. R: 0 lines out, about 25 amended, about 35 in.
5. **The tool step.** A claim of `handover.py` carries a record path. `hand` picks a standby by model. The judge arms the standby watcher between wakes. Sources: BSD, part 2, and the watcher that wakes a session in 6 seconds.
6. **Statements.** It answers the part of statement 1 that the step in motion makes: 6 of 8 moments (TR). It answers 4 in part: the worker that acts writes the record. It leaves 2, 3 and 5 to the judge, with no rule changed.
7. **Rulings crossed.** "one strong model, one context, no wiring" (Comp:95, ratified 2026-09-16). C11: "A hand-off means you stop and the stack goes to one session" (2026-09-20). C13, the reserve never widens a seat (2026-09-20). Question 8.
8. **The test.** It works if the judge's context per landed branch falls from 43k to under 15k (BSD:130). It works if one read of the whole starts with no word from Roman. The baseline is 0 of 7 (T2). It fails if the judge wakes, takes the first item of the note and continues, as 10 of 11 takers did (Map, mass 7).
9. **Cost:** 8 to 10 passes. First: his ruling on Comp, and the control.
10. **Weakest point.** It adds a seat and removes nothing. Session 5ee5ec0b wrote the root "no seat holds the whole" before any read, and the test found that it covers the size cases only. A project that adopts the workflow needs two models and the wake wiring.

## The comparison

| | Control | A, the round | B, the plan | C, the claim | D, less form | E, two seats |
|---|---|---|---|---|---|---|
| The order comes from | the newest run | the newest run, as a table | a plan step and its measure | the least known claim | the session's judgement | the judge seat |
| The unit of work | a frame at a site | a row | a step, then a frame | a claim | a frame | a frame |
| Statements answered | none whole | 2, 3, 4 | 2, 3 | 1 | none whole | none whole |
| Answered in part | 2 | 1 | 1, 5 | 3, 5 | 1, 2 | 1, 4 |
| Left | 1, 3, 4, 5 | 5 | 4 | 2, 4 | 3, 4, 5 | 2, 3, 5 |
| Pairs of WE section E settled | 3 | 2, 3 | 1, 2, 3, 10 | 1 | 1, 2, 5 | none |
| Moments that need Roman | 0 | 1, then 0 per round | 1, then 1 per changed step | 1, then 0 | 1, large | 1, on Comp |
| R: lines out, amended, in | 0, 3, 6 | 55, 12, 22 | 45, 14, 20 | 20, 12, 18 | 100, 10, 6 | 0, 25, 35 |
| New tool code | 1 flag | 1 tool | 1 target, 2 prints | 2 flags, 1 print | none | hand-off changes |
| Passes | 1 | 4 | 3 | 2 | 2 | 8 to 10 |
| Questions to Roman | 0 | 1, 2 | 1, 3, 4, 5 | 1, 6 | 1, 7 | 1, 8 |
| Weakest point | the intake stays | a Sprint section again | the measure of the step | his last word as the method | no case shows that a removal acts | it adds only |

## The recommendation

Build shape B. The reasons:

- Shape B is the one shape with a recorded stretch behind it. For 69 hours the order came from a plan with a measure outside the frame, and Roman wrote 8 messages (T2).
- Shape B gives an end rule to the kind of unit that ended worst. Plans ended with a record in 2 cases against 9 (AF).
- Shape B gives a session a route to a larger solution with no question. The sessions gave the rule on departures as their reason not to ask (T2, K4).
- Shape B removes more than it adds: about 45 lines out and 20 in. It needs one new target of an existing tool.
- Shape A keeps the newest run as the order source. Shape C is one day old, and it needs the product's measure first. Shape D alone has no evidence. Shape E adds only.
- Shape B takes one part from shape A: a mark for each part in one place, at the end of a step only. It takes nothing from shapes C and E now.

What the run's measure must tell the session, for shape B: whether the condition of the open step holds, for this request and this seat. The run page must also say which parts of the destination sentence the run tested. The product review designs the measure.

The order of the build. Each step is one act. The session writes its expectation before the step and compares after it (memory `rota-one-step-then-compare.md`).

1. **The control.** Build `status --put-down` and the one-line `## Parked` list. Amend C34 and C72. One agent drafts a reason for each silent frame, and the session judges the list. Read: the silent frames, 88 today, and the held frames of spent sessions, 9 of 17.
2. **The removals that cross no ruling.** The five rules whose tool is proven, C49, the sentence at R:487, the economy line, the Stop hook that fires for no session. Sprint sections 8 to 34 go to the archive. The idle rule of the brief gets his limit: "that idle rule was to prevent meaningless waits". Read: the lines of R, 725 today. This step shows no change in an act.
3. **The plan's line.** Build `status plan`. The run's read writes one line on the plan in place of the four bullets of C46. Read: the plan has a line dated after each of the next two reads.
4. **The step line at the push and in the note.** Amend C46, C10 and C28. Read: the pushed frames that name the step and the reason, 5 of 16 today, and the notes that start with the step, 0 today.
5. **The first tally.** The redirect ends by its own test (S:61), with one mark for each of its 7 items (S:28 to S:41). Items 6 and 7 have no status line today (AF row 50). Read: the unit ends with a record, and no item leaves with no word.
6. **The intake by the step, and the size inside a step.** Amend C34, C31, C57 and [Autonomy], after Roman answers questions 3 and 5. Read: the walls of a run that match a frame that nobody built, 7 of 16 at dry run 8.

Then stop and compare over two runs. If a session still sees a wrong size and writes it down only, add the expectation line of shape C. Do not build shape E.

## The questions for Roman

Each question names the ruling that the shape departs from. The words in quotes are the question as he gets it. A "card" is a frame.

1. Every shape. The ruling: "nothing measurable" (2026-10-17 18:19). "To see if the change works, the session wants to count a few things for two runs, and then stop the count. Is that inside what you said?" Recommended: yes. [low]
2. Shape A. C46 (2026-10-12 23:40) and C34 (2026-10-15). "After a run, the session lists what went wrong. Today each item becomes a card. Can an item stay as one line in the run's table, with a mark, and never become a card?" Recommended: yes. [med]
3. Shape B. "Let's just keep working" (2026-10-18 03:17), then "Ok then long term plan and execute" (2026-10-31). "On 18 October you stopped a sort of the open cards by the destination. On 31 October you ordered the long term plan. Does the plan now set the order? Then a problem that does not stop the plan's open step gets one line and no card." Recommended: yes. [high]
4. Shape B. "They declare finished" (Comp, 2026-09-16). "The session thinks that a step of the plan is done. It writes the tally and starts the next step. You read the tally later, and you can open the step again. Or do you want to say 'finished' before the next step starts?" Recommended: the tally is a candidate, and the session continues. [med]
5. Shape B. "for now there is only cheap and escalate to me" (2026-10-15), and the ruling of 2026-11-10 08:17. "Part a. A problem needs a large change, and the change serves the plan's open step. Can the session build it with no question to you? Part b. Can a session stop a whole step of the plan with a reason, as it can now put down one card?" Recommended: a yes. b no, the session asks you one time, with the tally. [high]
6. Shape C. C47 (2026-10-12 23:52). "A session thinks that the work aims at the wrong thing. Can it stop for one read that tests the thought, and give you the result in one line?" Recommended: yes, one read with a cap. [med]
7. Shape D. The texts adopted on 2026-10-11 05:50. "You adopted a price for each card and a size for each batch of cards. 20 of 22 cards passed their price, and nothing followed. Can the session remove both? Can it also remove the line that tells every session, on every turn, to continue when it is not blocked?" Recommended: yes to the first, and your word on the second. [med]
8. Shape E. Comp:95 (2026-09-16). "Today one session speaks with you, judges, and does the paperwork. Can a second kind of session do the paperwork and wake the first for a judgement only?" Recommended: not now. [high]

## What the scope excluded

- Each change to rota, the product, and the design of the run's measure.
- The hand-off, the standby and the context lines at 200k, 300k and 350k. The hand-off commands print the truth (Map, mass 6).
- The refusals older than the ruling of 2026-10-18: `standby` at 300k, the one watcher, and `status` on a time and a frame (WE, E4).
- The timeout of a low question against "treats silence as consent" (WE, E7).
- The briefs of the implementer and the reviewer, the review per pass (C53), and the model of each role.
- The memory index, and the mechanical repeats such as the heredoc fault.
- The content of the plan. Its steps and their order are Roman's.
- The reason for each of the 88 silent frames. The agent of step 1 drafts those.

## What I could not see

- I read no transcript. For the reads of masses 1 to 8, I read the lines of Map and not the read pages.
- Whether the 8 messages in 69 hours come from the plan or from Roman's own days.
- Whether the plan steers for longer than three days. The stretch held three easy requests.
- Whether a removed rule text changes an act. The records hold no such case.
- The code of branch `f363state`. I name its two lines from WE.
- The origin of the hook line. `git log -S` gives f3b4cfb4 of 2026-09-17, a commit that only starts to track the file.
- Whether Roman reads `state --since`. Each shape shows him its lines there, and I found no count of his reads.
- The next measure of the product review, and the second view of session 1efd37b1.
- The line counts for R and the pass counts are my estimates from the lengths of the entries.
- Whether "a frame" in the ruling of 2026-11-10 covers a wall that never becomes a frame. I read it as not covered, so questions 2 and 3 ask.
