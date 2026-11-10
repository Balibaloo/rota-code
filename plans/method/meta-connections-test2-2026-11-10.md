# An adversarial test of the five connections K1 to K5, 2026-11-10

Read-only, one agent of session 7fd2421e, with one sub-agent for the draw of K1. Evidence: `git log`,
`plans/stack.md` and `plans/archive/` by script, the run read pages, `rota/tools/handover.py`, and the
transcripts from 2026-10-10. "T <sid> <time>" is a transcript, and its time is UTC. Stack times are local.

## Result
1. K1: holds in part. A frame starts at one site. The site does not stay fixed: 8 of 17 built frames
   moved or grew, 7 with no word from Roman. Every move stayed at the scale of a site.
2. K2: holds in part. Repeats met in nine places. Alone, a session used a count to park, fold or bound.
   It enlarged a solution only through a question to Roman.
3. K3: holds in part. The first half fails on the price and the Site line. The second half holds for a
   record of a state that moves, and not for a ruling, a constant or a plan.
4. K4: holds in part. Agent reads of the whole follow his words in 7 of 7. "Stop pausing" and "never
   idle" are cited 0 times as a reason not to ask. Questions on size were asked, twice.
5. K5: does not hold as a finding on the way of working. All three requests named the function. The
   nights of the week before merged 13 of 18 on click. Roman's order ended the stretch.
6. K2 follows from K1. K5 is one case of K4. K3 stands apart, and the plan of 2026-10-31 contradicts
   the use that K4 makes of K3. Missing: a direction ends only when a new direction replaces it.

## K1. The unit of work is one sign at one site
**The draw.** `random.seed(20261110)`, then `random.sample(nums, 30)` over all 361 headings by number,
open and closed. The sub-agent read each push block in git and each code commit that the frame names.
I checked three of its quoted lines. The 30: 156, 333, 92, 292, 244, 341, 194, 166, 95, 289, 170, 120,
275, 282, 209, 276, 74, 183, 362, 306, 232, 208, 117, 354, 257, 280, 108, 81, 86, 138.
- No code commit: 12. Built at the pushed site: 9. Built at another site, or the cause rewritten: 4
  (92, 244, 306, 362). Grew past the site: 4 (282, 86, 354, 257). Closed on a ruling: 1 (280).
- Of 17 built frames, 8 moved or grew. The first move came from an agent's read in 3 (244, 257, 306),
  a review finding in 3 (282, 86, 354), the holder's own reading in 1 (92), Roman's words in 1 (362).
- Frames 306 and 362 moved eight times each. His words prompted 4 of all 25 moves.
- The Site line did not follow the build. 27 of 30 push blocks are unchanged but for session ids.
- What survives: each move goes from one site to another site, or to more sites. No move in the draw
  changed the scale. The larger fact of the draw: 12 of 30 units were never built.

**The first half.** The form of a run's read changed three times (headings of the read pages).
- To night 148: one section per held frame, then "New walls" or "Candidate frames, new"
  (`plans/night119-read.md:174`, `plans/night148-read.md:465`).
- Nights 149 to 175: "Every wall placed by the guide" (`plans/night149-read.md:496`), with 11 W labels
  on night 149 and 25 on night 174. The form starts with the wall guide, commit bb53fd95, 2026-10-15.
- Dry runs 1 to 3: one wall per page, 11 pages, in the steps of rule C76. Three merges followed.
- Dry runs 4 to 8: frame 362's measures, then "The walls, with their provenance"
  (`plans/dry4-read-2026-11-03.md:118`). From 11-03 to 11-09 a wall did not become a frame. One frame
  was pushed, frame 362, and it holds the walls of seven runs in 241 status lines.
- Reads in another form: the closed-reach read (10-26) gave C76, the facts read (10-27) gave sprint 26
  "by fact", the 24 cases (10-29) gave design R, the root read (11-08) gave C77. Each began with his words.

**The provenance of the form.** A session wrote it, for its own context and for three agents side by
side: "Group by site, not by subject." and a price table, "a door text or a number | 2" (T 84ce0759,
2026-10-11 04:46). Roman: "make sure that the meta workflow adopts these" (04:50). He did not write it.

**Verdict.** Holds in part. "A site fixed at the push" holds for the Site line and fails for the build.
The scale holds. The list of walls is the form of 10-15 to 10-29, not of the whole period.

## K2. Nothing adds up across units
Places where repeats met, and who started each:
1. **A design frame over wall frames.** Frame 190 over 7 frames, 193 over 4, 200 over 7
   (`plans/archive/stack-2026-10-10.md:7`, `stack-2026-10-11.md:7`, `stack-2026-10-13.md:48`). Frame 193:
   Roman "chose 'One design frame over the second request' from three options, the recommended one"
   (`stack-2026-10-10.md:46`). The session wrote the options. Frame 200: the session's proposal after
   "whats the next sprint of frames we should do?" (`plans/frame287-roman-words.md:417`). Frame 190:
   not recorded. Four frames under frame 200 are open today: 171, 182, 176, 194.
2. **A count over nights at the push.** 19 status lines in October. Frame 298 counted "19 pointer
   faults", and the session asked Roman six questions with "the cheap fix alone" as one option
   (T 6977407c, 2026-10-18 06:22 to 10:52). He ruled the design, priced "10 or more cycles".
3. **A guide cause at the push.** 68 push blocks name a cause, and 25 name cause 8. My grep finds no
   line that counts frames per cause. This place supports K2.
4. **The economy count.** Session 81fe1025 parked 11 frames on 2026-10-21 16:23, "the frame economy,
   31 live of 10" (`plans/stack.md:4030`). His messages of that day do not name the parks. On 11-01 a
   wall "joins frame 278, taken from the park" (`plans/archive/stack-2026-11-02.md:162`).
5. **A fold.** Frame 191 into 190 on a design review, by the session (`stack-2026-10-09.md:11`). Frame
   72 into 66, ruled by Roman (`stack-2026-09-23.md:580`).
6. **A bound on an overrun.** Session d5c14419, alone: "if review p6 opens one more edge with no case
   ... this frame closes on the measure" (`stack-2026-10-31.md:29`). Seven re-price lines, 09-20 to 09-22.
7. **One memory with a count.** The heredoc memory holds 27 strikes to 2026-09-30, then 4 in six weeks
   (10-07, 10-13, 10-26, 11-08). The count and two tools met, and the rate fell.
8. **A reopen.** "The frame reopens" (`plans/stack.md:4028`, frame 87, a validating frame), by the
   session. Of 28 "reopen" lines, none reopens a closed frame. That part of K2 holds.
9. **A match at the read.** Rule C76 step 2: "Match by symptom" (`plans/dry3-wall1-read-2026-11-02.md:52`).

**Verdict.** Holds in part. "Nothing adds up" is false as written. Alone, a session acts on a count to
make the work smaller (4, 5, 6). A count made a solution larger only through a question to Roman (1, 2).

## K3. A record at the moment of an act works, a record that must stay true does not
**Standing records that stayed true with no tool.** Each holds a ruling, a constant or a target.
- `plans/composition.md`: last commit 2026-09-16, 55 days. Each take reads it.
- `CLAUDE.md`, "writes a heartbeat every twenty seconds": in the file since 2026-09-19 (`git log -S`).
  `BEAT = 20.0` (`rota/tools/handover.py:172`). True for 52 days.
- `rota/COMPLETION.md`: no commit from 2026-09-17 to 2026-11-04. On 10-31 the plan "is read from
  `rota/COMPLETION.md`" (`plans/stack.md:72`). A page with no reader for 44 days set the order.
- The long term plan (`plans/stack.md:69`): the Sprint lines of frames 354, 355, 356, 358 and 359 cite
  its step. It steered for three days.

**Records made at the moment of an act that were wrong or ignored.**
- The price. Rule C46 places by it: "a wall of a held frame on its site, under three cycles"
  (`plans/stack.md:2474`). Last Cycles lines: frame 354 "22 of 5", 357 "10 of 2", 356 "6 of 2".
- The Site line: written at the push by C41, and the build moved in 8 of 17 (K1). The cause at the
  push: frame 260 was "re-scoped" 90 minutes after its push (`plans/stack.md:2477`).
- The seat measure: written at 23:08, and at 23:21 "The read landed and corrects two of my records"
  (T ce483c7b, 2026-11-02).
- The strike count: two strikes carry number 28 (the heredoc memory, lines 77 and 118). 30 is 31.

**The tool.** Strike 30 is "a status-line script through a quoted python heredoc" on 2026-11-08. The
status tool exists since f934ec21, 2026-10-18. The step has a second route. The hand-off has one.

**Verdict.** Holds in part, with the wrong variable. A record is true when the act that changes the
state cannot happen without the write. A record of a thing that does not move stays true alone.

## K4. The whole is looked at only when Roman asks
**A look that a session started alone.** I listed every agent launch whose brief names the backlog,
the open frames, a week or an audit, with his last message before it.
- Seven looks, seven after his message, at 0 to 8 minutes: 10-18 02:09, 10-26 22:09, 10-27 14:09,
  10-31 00:36, 10-31 02:55, 11-01 18:44, 11-09 23:47 (UTC).
- Started alone and changed the order: the 11 parks of 2026-10-21 (K2, place 4). It is the act of a
  rule on stale holders, not a look at the direction.
- The case of 10-31 00:38 in the transcripts read came 2 minutes after his "How have we been doing
  over the past few days?" (T d5c14419, 00:36). The session gave the content. He gave the moment.

**The standing words as a reason.** Session text, 2026-10-10 to 2026-11-09:
- "Nothing blocks on": 10 lines. One gives it as the reason not to ask: "so nothing blocks on you: I
  treat your ruling of 18:57 as the go ... you get a notification, not a question" (T 66edc387,
  2026-10-25 23:33). "Nothing waits on you" is in 65 lines, as a report.
- "Stop pausing": 0 lines. "Never idle": 0 as a reason not to ask or stop, 2 as the reason to hand off.
  "The handed frame continues without a check": 4 lines, each as the reason to start at once.
- The reasons that sessions give: "It is not a seat form or door change, so I did not ask you" (T
  a9a43280, 2026-10-30 20:15). "Why I did not ask you: ... The read found no words of yours on it. The
  stack marks this as assumed" (T 029756dd, 2026-11-06 08:30). The rule on departures decides.
- `AskUserQuestion` calls: 43 from 10-11 to 10-18, 19 from 10-21 to 11-09. Ten of the 43 came on
  10-18, after "Nothing blocks on me". Questions in terminal text are not counted.
- Questions on size exist: frame 298 (K2, place 2), and "From the fourteen proposals (Recommended) /
  Night 170 on the fixes as built / Stop and re-grill the stack" (T 8db3a3f9, 2026-10-26 21:13).

**Verdict.** Holds in part. The first sentence holds on the transcripts. The sentence on the standing
words names the wrong words. "A standing line goes stale" does not hold for the plan (K3).

## K5. One stretch worked in another way, and it ended with no decision
**The requests.** Each names the function: "Make click.pause() return True when it waited for a key
..." (`plans/archive/stack-2026-10-31.md:132`), "Make tip_calculator.calculate_tip() raise ValueError
when the tip percentage is below 0 or above 100 ..." (`plans/archive/stack-2026-11-02.md:195`), and
"canonsort_keys() raise ValueError when canonical_order names the same key twice ..." (`plans/stack.md:2021`).
Dry run 4 changed to the fold sentence, a request "that names no function" (`plans/dry4-read-2026-11-03.md:142`).

**What the seat supplied.** On click: "the seat set one row by hand and gave technical test diagnoses
that a careful person could not give" (`plans/dry1-turn16-read-2026-11-02.md`, Result 5). On icalendar:
"For my sentence it named the one file and the one function" (T ce483c7b, 2026-11-03 00:13).

**How the work was ordered.** By a rule of the plan: "the first wall is placed before any other fix"
(frame 354's Sprint line). One run ran again after each fix: dry1 has four measures and nine read pages
(`plans/operating-facts.md:380` to 388). The frame form stayed: 10 frames, each one wall at one site.

| The count | 10-23 to 10-30 | 10-31 to 11-02 | 11-03 to 11-09 |
|---|---|---|---|
| Code commits per day (`git log`) | 61 | 16 | 25 |
| Frames pushed | 43 | 10 | 1 |
| Roman's messages (transcripts) | 196 from 10-24 | 8 after 10-31 03:03 | 55 |
| Merges | 13 of 18 on nights 170 to 175, click | 3 on 3 repositories | 0 recorded, 7 runs |

- Nights 170 to 175 merged 2, 1, 2, 3, 3 and 2 of 3 (titles of the six read pages), "the agent
  principal on Opus" (`plans/night173-read.md:3`). I did not check whether those merges were correct.
- The stretch did not raise the merge count. It moved the seat to the session and added two
  repositories. On tips and icalendar the merge came "on the first build turn"
  (`plans/operating-facts.md:389`, 390). The months before built that ability. The stretch measured it.

**What ended it.** At 2026-11-02 23:18 the session wrote "That is step 3 of the long term plan done".
At 00:12 Roman asked "How is rotas understanding of repositories?". At 00:17 the session scored the
cold key: "rota knows the words of icalendar and none of its commitments". At 00:38 he ordered the
demand read, and the session wrote "I push the frame for it, because you ordered it over the economy"
(T ce483c7b). The fold sentence was the session's idea (00:36). So his order ended the stretch. For
the seat measure and step 4 of the plan, a decision is not recorded. No later status line cites step 4.

**Verdict.** Does not hold as stated. The breaker is on record, in a read page of the stretch itself.
What holds: for 69 hours the order came from a written plan with a measure outside the frame, and
Roman wrote 8 messages. That is a fact about the order source, not about the unit of work.

## 6. Overlap and dependence
- K2 is K1 seen over time. A wall is cut to a site, and rule C31 gives each new cause a new frame.
- K5 is not a claim. It is the one case where the order source was a plan. It belongs under K4.
- K3 stands apart. K4 uses K3 to dismiss a standing line, and the plan is a standing page that steered.
- Two claims and one case are left. The cut: work is cut to a site, and nothing joins it again. The
  order source: it changes only by his word.
- K1 to K5 drop the strongest connection of the first test, "the build measures itself by its own
  output". The stretch of K5 is the one time when the measure was outside the frame.

## 7. The connection that the session did not write
**A direction ends only when a new direction replaces it. Nothing above a frame is closed or finished.**
Each new direction began with Roman's word, and no record ends the one before.
- Frame 4, "Roman's order from here (2026-09-14 12:58)", is open. Its last status is 2026-09-21.
- The night as the order source: rule C46 of 10-12, replaced on 10-29 by "instead of faffing with
  nights try to develop the right behaviour in the liaison with test cases" (T 161c371b, 01:53).
- The case loop of 10-29: frame 352 has one status line, of 2026-10-31 01:55.
- The plan of 10-31: step 3 done, step 4 never cited again. The seat measure: six entries, then none.
- The onboarding slice of 11-03, the pause of 11-06 ("nothing of either is built before his word",
  `plans/stack.md:1879`), the root order of 11-08, the seat of 11-10.
- 76 of 136 open frames have their last status before 2026-10-18. 20 have one from 11-03 or later.

It joins K2 (a return does not meet its first sighting), K4 (he starts each turn) and the end of K5.
His own asks add a direction and close none. Doubt: I chose these cases. I did not draw them.

## 8. The three items under "Not explained by K1 to K5"
1. **A fix returns after a larger form.** The larger form was tried at least five times: frames 193,
   200, 298, 344 ("33 of 37 FIXED" at its close) and 345. For the dry runs the records point another
   way. `plans/walls-root-read-2026-11-08.md`, section 1, gives a provenance commit for 20 walls. By my
   count of its dates, 14 trace only to code from before 2026-10-10, 4 to a fix of late October or
   later, 1 is mixed, 1 is a setting. On a new repository most walls are first meetings with old code.
2. **Roman's own direction.** His words pull two ways: "should we just keep working the way we are?"
   (T e669185f, 10-13 17:49), "I don't like the direction. Let's just keep working" (T 21800a2b, 10-18
   02:17), "the initial fix was so narrow minded" (T ac089aa1, 10-26 20:33). He ended the stretch
   with a question, and the session's own score opened the turn.
3. **The mechanical repeats.** The heredoc strikes fell from 27 in five weeks to 4 in six. Strike 30
   used a route that the status tool does not close. The record shows a rate that fell and a route
   still open, not a lesson that failed.

## 9. What this test could not see
- The K1 classes come from one sub-agent. I checked 3 of its 25 moves. "Same site" is a judgement.
- The transcripts start on 2026-10-10. September and the sessions of frames 190 to 200 are not in
  the folder. Thinking blocks are mostly empty. His message count can include a peer's message.
- "Who started" is the gap to his last message. A reply to "How's it going?" mixes his moment and the
  content of the session. My word searches miss other wordings.
- I opened no run database and no diff of the product. Merge counts come from read pages and titles.
  The dates of the root read are an agent's `git log -S`. I counted them and did not check them.
- Section 7 is my own tidy story from chosen cases. It needs the same test as K1 to K5.
