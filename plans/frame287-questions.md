# Frame 287, read C: every question to Roman since 2026-10-01, and where its answer was

Date: 2026-10-17. Read-only, Opus, from `questions_brief.md` in session
d7c5dc6d's scratchpad. The meta workflow (the build sessions) is the
subject. The rota workflow (the seats) appears only as the content of a
question.

**Verdict.** 103 questions went to Roman from 2026-10-01 to 2026-10-17.
The records already held the answer for 19 of them. A read dissolved 6
more. 78 were open: 32 of those a rule required (a sprint order or an
empty reserve), and 46 were design or run choices. 38 rows outside the
order and reserve groups belong to 8 groups asked twice or more by
substance. The worst group is frame 114, the Developer's write on a file:
5 asks in 3 sessions over 13 days, and law 12 held the answer since
2026-08-09 (observed: `rota/LAWS.md:337-342`;
`plans/frame114-history-read.md`, section 1).

## Method

1. `extract_questions.py` and `extract_questions_full.py` in the
   scratchpad stream all 105 transcripts line by line. They keep each
   main-thread assistant record from 2026-09-30T23:00Z with an
   `AskUserQuestion` or `PushNotification` tool call, or a text that
   starts with `[high]`, `[med]` or `[low]`. They pair each record with
   its tool result and with the next typed user message in the same file.
   Output: `questions_full.txt`, 102 records (observed: the script run,
   2026-10-17).
2. Row 103 is a plain-text question with no rating. The script missed it.
   It is added from `roman_words.txt`, entry 2026-10-17T15:50:54Z
   (observed).
3. Times are local, UTC+1, the clock Roman and the stack use (observed:
   `frame114-history-read.md` writes 15:50:54Z as 16:50 local).
4. One `AskUserQuestion` call is one row, also when it holds two
   questions (rows 4, 11, 12).
5. "Answer at" is the next typed message. For a notification, that
   message is sometimes about something else (rows 15, 16, 22, 23). The
   table says so.

Class key: **R** answered by the records before the ask. **D** dissolved
on a read: the premise falls when the named file is read. **O** open,
and the ask was right. **O\*** open, and a rule required the ask (sprint
order, empty reserve, frame choice before 2026-10-12 23:52). "Read list"
is Yes when the place is on the hand-off read list: the composition page,
the momentum note, the open frames, or a memory file the frame names.
Every row is (observed: `questions_full.txt`, the row's time) unless a
cell carries its own mark.

## The table

| # | Local time | Sid | Frame | Question, rating | Roman's answer | Where the answer was before | Read list | Class | Same as |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 10-01 07:13 | d2cc277a | order | Which frame starts now: 104, 100+101+88, or 103 | 09:12 "Frame 104 ... (Recommended)" | nowhere: "Roman assigns" rule in CLAUDE.md requires the ask | n/a | O\* | order group |
| 2 | 10-01 10:21 | d2cc277a | order, 101 | Next frame after 104: 101 with the result cut | 10:30 "Frame 101 first ... (Recommended)" | nowhere, rule requires ask | n/a | O\* | order group |
| 3 | 10-01 14:15 | 10885dab | order | Which frame: 106 read, 100, or rule 107 | 14:26 "Frame 106 read (Recommended)" | nowhere, rule requires ask | n/a | O\* | order group |
| 4 | 10-01 15:10 | 10885dab | 106, 107 | Does the Architect get a reads-tests edge; and frame 107's route | 15:12 "Yes, add the edge (Recommended)" twice | nowhere: a new read edge changes the graph (reasoned: law 3 derives edges from reads, so a read edge is a design choice) | n/a | O | 5, 6, 50 |
| 5 | 10-01 15:23 | 10885dab | 107 | Critic's doubt about a criterion: to the Architect as an exception? | 15:24 "Wait the terminologist writes the criteria? Not the architect?" | law 3 (`LAWS.md:121-147`) and the graph: the Terminologist writes the criteria | No | D | 6, 50 |
| 6 | 10-01 15:24 | 10885dab | 107 | Same, after the read: to the Terminologist | 15:25 "The Terminologist (Recommended)" | law 3, same as row 5 | No | R | 5 |
| 7 | 10-01 16:12 | 10885dab | 106 | Dead-end Architect proposes a seam; what does the case accept | 16:33 "Say again?" | nowhere | n/a | O | 8, 9 |
| 8 | 10-01 16:34 | 10885dab | 106 | Which outcome counts as success | 17:17 "So looking at the system as a whole, what should happen here and why?" | nowhere | n/a | O | 7, 9 |
| 9 | 10-01 17:18 | 10885dab | 106 | Rewrite the case: the stall leaves to a named next seat | 17:18 "Yes (Recommended)" | nowhere | n/a | O | 7, 8 |
| 10 | 10-01 22:38 | 88ab150f | standby | Watcher killed at 10-min limit; raise limit or re-arm | no answer in file | nowhere before; CLAUDE.md now carries the 7200000 timeout (observed: CLAUDE.md, Standby duty, at HEAD) | n/a | O | reserve group |
| 11 | 10-02 04:09 | eca94a44 | order, night report | Which frame next; the night report line | 09:26 "The coder's broken message first (Recommended)", "Fix the two wrong counts, move the line to 60k (Recommended)" | nowhere, rule requires ask | n/a | O\* | order group |
| 12 | 10-02 13:47 | eca94a44 | inherited test, order | [med] Where does a failing inherited test go; [low] order | 14:29 "Theoretically, in a team, what's the correct way to deal with this?"; order "(Recommended)" | a broken project test is the Developer's own regression since 2026-09-14 (observed: CLAUDE.md, the history-read paragraph, cites it) | No | R | 103 (same seat question: what a Developer may repair) |
| 13 | 10-02 15:00 | eca94a44 | Tester fixes test | [med] Tester names the bad test but never fixes it; add a door? | 15:01 "Interview the model" | nowhere: this answer is the origin of the interview rule of 2026-10-02 15:02 | n/a | O | 14, 87, 89, 90, 93 |
| 14 | 10-02 15:11 | eca94a44 | Tester fixes test | [low] Tester reads code 5/5, fixes 1/5; door or close | 15:15 "What did you find in it's interview?" | the interview rule, 13 minutes old (observed: CLAUDE.md "ruled: Roman, 2026-10-02 15:02") | No (memory file written later) | D | 13, 89, 90 |
| 15 | 10-02 16:09 | 46f23339 | 115 | Architect's answer to a Developer carries no words; edge gains prose? | 18:53, unrelated: "I don't know what the frame numbers mean" | law 2 (`LAWS.md:112-119`): conclusions travel, reasoning stays home, reached by a ref | No | R | 28, 30 |
| 16 | 10-02 18:10 | 46f23339 | 112 | [low] Repeat wakes: close as measured | 18:53, unrelated message | nowhere | n/a | O | none |
| 17 | 10-03 02:27 | 46f23339 | 111 | Night 109 read, notice with no question | 02:28 "can we restart the run from just before where the issue started" | n/a, a notice | n/a | O | none |
| 18 | 10-03 06:07 | 3d6e6173 | 111 | [med] Developer repeat ask: close and push the burst | 13:42 "Close and push the burst (Recommended)" | nowhere | n/a | O | none |
| 19 | 10-04 02:32 | 3d6e6173 | second card | [med] What a second bench is for | 02:33 "Keep the checker moving (Recommended)" | nowhere | n/a | O | 20, 21 |
| 20 | 10-04 02:33 | 3d6e6173 | second card | [med] Gate beside a night on the slow bench | 02:35 "Check during the night, re-read the stumbles (Recommended)" | nowhere | n/a | O | 19, 21 |
| 21 | 10-04 02:35 | 3d6e6173 | second card | [med] If the ten-minute trial fails | 02:36 answered | nowhere | n/a | O | 19, 20 |
| 22 | 10-04 04:59 | 5e8ace65 | order, 119 | [low] 119 before 113 | 10:01, unrelated: "So the titan is useless?" | nowhere, rule requires ask | n/a | O\* | order group |
| 23 | 10-04 09:31 | 5e8ace65 | second card | [med] Second card re-records only on the main card | 10:01 "So the titan is useless?" | nowhere | n/a | O | 25 |
| 24 | 10-04 10:55 | 5e8ace65 | cut reply | [med] When the reply cut runs | 12:51 "Park it" | nowhere | n/a | O | none |
| 25 | 10-04 12:53 | 5e8ace65 | second card | [med] Stale case while a night holds the main card | 12:54 "Wait for the main card (Recommended)" | Roman's own question of row 23, 3 hours earlier, which the session answered with a read | n/a | O | 23 |
| 26 | 10-04 14:16 | 5e8ace65 | 114 | [med] Developer breaks a project file; system refuses a partial repair | 14:16 "[Request interrupted by user for tool use]" | law 12 (`LAWS.md:337-342`, since 2026-08-09); touch route cf067ce4 (2026-09-13); composition Flows line 73 "A prediction never blocks" (observed: `frame114-history-read.md`, section 1) | composition: Yes; law 12: No | R | 27, 29, 99, 103 |
| 27 | 10-04 14:16 | 419281dc | 114 | [med] What may a later Developer do to a file the work broke | 14:18 "investigate this with a sub agent" | same as row 26 | same as 26 | R | 26, 29, 99, 103 |
| 28 | 10-04 14:18 | 419281dc | 115 | [med] The Architect's answer has no place; where does it go | 14:19 "investigate our decisions, previous thoughts etc" | law 2, same as row 15 | No | R | 15, 30 |
| 29 | 10-04 14:26 | 419281dc | 114 | [med] The fix was always allowed and the Developer never found it; what changes | 14:28 "whats the question here?" | same as row 26; the session's own read dissolved the premise | same as 26 | D | 26, 27, 99, 103 |
| 30 | 10-04 14:29 | 419281dc | 115 | [med] May the Developer read the decision record the Architect points at | 14:34 "sorry i may have missexplained ... we have already discussed this, use a subag[ent]" | law 2, same as row 15 | No | R | 15, 28 |
| 31 | 10-05 05:36 | 5101d8d0 | order, 135 | [low] F-135 before 116 and 117 | 08:35 "Yes, any questions?" | nowhere, rule requires ask | n/a | O\* | order group |
| 32 | 10-05 07:51 | 5101d8d0 | 135 | [low] Run pass 4 after 400k spent | 08:35 "Yes, any questions?" | nowhere | n/a | O | none |
| 33 | 10-05 19:50 | 3f72d9cb | order, 152 | [low] Next frame F-152 | 19:50 "Continue" | nowhere, rule requires ask | n/a | O\* | 34, order group |
| 34 | 10-05 19:50 | 3f72d9cb | order, 152 | [low] Same, in the terminal | 19:50 "Continue" | row 33, the same minute | n/a | O\* | 33 |
| 35 | 10-06 12:23 | 2ba331e1 | passes | [med] Relaunch four stopped implementers | 12:23 "Yes, relaunch all four (Recommended)" | nowhere | n/a | O | none |
| 36 | 10-06 16:37 | 488d31af | order, 164, 165 | [low] Start 164 and 165 | 16:43 "What?" | nowhere, rule requires ask | n/a | O\* | order group |
| 37 | 10-06 23:56 | 488d31af | reserve | [med] 0 armed standbys; run /standby | 10-07 00:03 "fixed" | CLAUDE.md requires the notice | Yes | O\* | reserve group |
| 38 | 10-07 05:08 | 6cc11c8b | order, 177 | [low] Claim 177 beside 170 | no answer; taken by timeout (reasoned: archive `stack-2026-10-07.md` holds 2 "taken by timeout" lines) | nowhere, rule requires ask | n/a | O\* | order group |
| 39 | 10-07 05:15 | 6cc11c8b | Critic pass | [high] Inspector signs "passed" with an empty card | 08:55 "Is this a model limitation also?" | nowhere | n/a | O | 40 |
| 40 | 10-07 08:55 | 6cc11c8b | Critic pass | [high] What must a pass carry | 08:56 "Pass names a line per requirement (Recommended)" | nowhere | n/a | O | 39 |
| 41 | 10-08 01:53 | 18588d6d | order, 178 | [low] Next frame 178 | no answer, timeout | nowhere, rule requires ask | n/a | O\* | order group |
| 42 | 10-08 09:42 | 225aec9c | order, 142 | [low] Order 142, 182, 183, 179, 181 | 09:45 "a standby is running" | nowhere, rule requires ask | n/a | O\* | 43 |
| 43 | 10-08 09:46 | 225aec9c | order, 142 | [low] Same, in the terminal | 09:46 "what have found in the last run? and how does it relate to the rest of the backlog?" | row 42 | n/a | O\* | 42 |
| 44 | 10-08 19:52 | acb1f403 | 142 | [low] How many "fix it" on one parked change | 19:53 "What's the question?" | nowhere before; DECISIONS 2026-10-08 park ask entry came from this grill (reasoned: same date, written after) | n/a | O | 45 |
| 45 | 10-08 19:53 | acb1f403 | 142 | [low] Same, as a story | 19:54 "Well that depends on why it failed" | as row 44 | n/a | O | 44 |
| 46 | 10-09 10:29 | d7cf65d1 | 190 | [high] Reviewer says eleven times the page is off-request | 10:31 "Re-batch around what the principal sees (Recommended)" | nowhere | n/a | O | none |
| 47 | 10-09 16:44 | d7cf65d1 | reserve | [med] Hand-off claim never taken | no answer in file | CLAUDE.md requires the notice | Yes | O\* | reserve group |
| 48 | 10-10 03:28 | 45fc3fe2 | 193 | [med] Second request: one design frame | 03:29 "One design frame over the second request (Recommended)" | nowhere | n/a | O | 49 |
| 49 | 10-10 04:24 | 45fc3fe2 | 193 | [high] Your box versus the composition on approved work | 04:25 "Sorry I'm feeling a bit disconnected, can you motivate the entire system?" | composition and law 9 (`LAWS.md:241`): only a ratified amendment revokes approved work; the question cites both | Yes | O | 48 |
| 50 | 10-11 06:23 | 84ce0759 | 200 | [med] How the Architect's decision row reaches the Tester | 06:30 "Developer challenge carries the row (Recommended)" | law 3 rules out a hand-drawn edge; the choice between derived routes was open (reasoned) | No | O | 4, 5 |
| 51 | 10-11 14:01 | be3ef742 | 204 | [med] Shipped request's notes land on the next page; park them | 14:02 "so we have to be carefull to ensure that the workflow generalises" | nowhere | n/a | O | notes group |
| 52 | 10-11 14:02 | be3ef742 | 204 | [med] My reading of "generalises" | 14:02 "walk me throught this with plaintext diagrams" | row 51 | n/a | O | notes group |
| 53 | 10-11 15:40 | c81dd240 | 204 | [high] What a seat's note is for; start as written | 15:43 "Start as written (Recommended)", "Architect reviews some categories of notes if I don't and escalates or resolves no?" | nowhere | n/a | O | notes group |
| 54 | 10-11 15:44 | c81dd240 | 204 | [med] Narrower: the Architect looks only at notes on constrained walls | 15:58 "Say again?" | row 53 | n/a | O | notes group |
| 55 | 10-11 15:58 | c81dd240 | 204 | [med] Which notes the Architect reviews | 15:59 "Every default" | row 53 | n/a | O | notes group |
| 56 | 10-12 10:31 | 5d91f76d | 226 | [med] Fix the criterion repair before the night | 10:37 "Fix the repair first (Recommended)" | nowhere | n/a | O | none |
| 57 | 10-12 12:06 | 5083f684 | reserve | [med] 0 armed standby; open a session | 12:19 "standby ready" | CLAUDE.md requires the notice | Yes | O\* | reserve group |
| 58 | 10-12 23:18 | 31e55586 | reserve | [med] Night runs unwatched; reserve empty | 23:19 "Right, sorry, catch me up" | CLAUDE.md requires the notice | Yes | O\* | reserve group |
| 59 | 10-12 23:27 | 31e55586 | 204 | [med] Notes still open at the merge; what happens | 23:27 "ok, so these are non blocking notes? how important are they?" | Roman's answers of rows 53 and 55, 10-11 15:43 and 15:59; `plans/frame204-design.md` | frame 204 open: Yes | R | notes group |
| 60 | 10-12 23:28 | 31e55586 | 204 | [med] A default shipped unshown; park at the merge? | 23:29 "so it should be part of architect review right?" | rows 53, 55: "Architect reviews ... and escalates or resolves", "Every default" | Yes | R | notes group |
| 61 | 10-12 23:29 | 31e55586 | 204 | [med] Architect review, park at merge, or both | 23:31 "yeah but not just defaults, the architect reviews all notes and escalates and thats what blocks the work" | rows 53, 55 | Yes | R | notes group |
| 62 | 10-12 23:40 | 31e55586 | sessions | [med] Which session takes 204 and the sprint re-cut | 23:44 "[User dismissed ...]" | CLAUDE.md: "Roman assigns work to a session ... The reserve exists to continue this seat, and not to widen it" | No | R | none |
| 63 | 10-13 05:47 | fb742825 | order, sprint 2 | [low] Sprint 2 order | no reply; an idle notice only | ruling of 10-12 23:40 and 23:52 requires the grill at the boundary | n/a | O\* | order group |
| 64 | 10-13 06:41 | 31e55586 | 204 | [med] Developer finds a thing nobody asked for: take it out or ask | no answer in file | `rota/ROLES.md:150-170`: the Developer "Never builds what nobody asked for ... a scope question or a `ledger.log`" (observed: `frame114-history-read.md`, section 1) | No | R | notes group |
| 65 | 10-13 08:50 | fb742825 | reserve | [med] Past 300k, reserve empty | no answer in file | CLAUDE.md requires the notice | Yes | O\* | reserve group |
| 66 | 10-13 15:11 | e669185f | order, sprint 3 | [low] Sprint 3 order | 15:13 "What's the problem?" | boundary grill required | n/a | O\* | order group |
| 67 | 10-13 19:01 | e669185f | night reuse | [med] Which reuse option first | 19:02 "[No preference]" | nowhere | n/a | O | 68 |
| 68 | 10-13 19:21 | e669185f | night reuse | [med] Reuse buys under 9 minutes; what next | 19:25 "Ok so nevermind the first step, what do these results mean?" | `plans/night-reuse-investigation.md` and the Fable read, which the question cites | n/a | D | 67 |
| 69 | 10-14 07:21 | 9b79f4a1 | order, sprint 4 | [low] Sprint 4; close 189 | no answer, timeout | boundary grill required | n/a | O\* | order group |
| 70 | 10-14 09:28 | 9b79f4a1 | reserve | [med] Window needed at 302k | no answer in file | CLAUDE.md requires the notice | Yes | O\* | reserve group |
| 71 | 10-14 14:29 | 58da19ca | reserve | [med] Window needed at 295k | 15:00 "didnt see your notifficaiton but now we have standbys" | CLAUDE.md requires the notice | Yes | O\* | reserve group |
| 72 | 10-14 17:51 | f3b11814 | order, sprint 5 | [low] Sprint 5 order | 17:58 "Yeah sounds good" | boundary grill required | n/a | O\* | order group |
| 73 | 10-15 01:16 | 4754aaec | order, sprint 6 | [low] Sprint 6 order, row 1 frame 243 | 01:21 "Ok yes" | boundary grill required | n/a | O\* | order group |
| 74 | 10-15 01:50 | 4754aaec | 243 | [high] Which rung carries your words to the seats | 01:51 "I'm saying it's not as simple as adding a reminder" | nowhere | n/a | O | 78, 79 |
| 75 | 10-15 02:44 | 4754aaec | wall method | [high] Rule the wall method block | 10:29 "Not yet, one more review pass" | nowhere | n/a | O | 76, 77 |
| 76 | 10-15 10:41 | 4754aaec | wall method | [high] Rule it after the second review | 10:43 "make the fable reviewer review if the wall ladder is the right thing" | row 75 | n/a | O | 75, 77 |
| 77 | 10-15 10:51 | 4754aaec | wall method | [high] Fit review: one wall versus a sprint | 10:57 "No, sorry I kicked this off poorly ... make a reasoning guide for future sessions" | nowhere | n/a | O | 75, 76 |
| 78 | 10-15 11:13 | dae006d1 | 251 | [high] A checker that grows by your sentence shapes: standing fix? | 11:14 "I have no idea what this means" | nowhere | n/a | O | 74, 79 |
| 79 | 10-15 11:15 | dae006d1 | 251 | [high] Same, re-worded: a list of your phrases in the code | 11:43 "What is this question, redesign the wall guide from first principles on fable" | row 78 | n/a | O | 74, 78 |
| 80 | 10-15 11:45 | dae006d1 | 251 | [high] Who opens the wall guide | 11:46 "night reader maybe, solution designer definitely" | nowhere | n/a | O | none |
| 81 | 10-15 11:46 | dae006d1 | 251 | [high] Which decision the guide eases | 11:47 three options incl. "(Recommended)" | nowhere | n/a | O | none |
| 82 | 10-15 11:47 | dae006d1 | 251 | [high] What makes two walls one kind | 11:48 "The same cause in the structure (Recommended)" | nowhere | n/a | O | none |
| 83 | 10-15 11:49 | dae006d1 | 251 | [high] When to leave a wall unfixed | 11:51 "if a wall is only a small inefficiency and we can't fix it easily then leave it ..." | nowhere | n/a | O | none |
| 84 | 10-15 11:51 | dae006d1 | 251 | [high] Rungs above the cheap fix | 11:53 "I guess for now there is only cheap and escalate to me" | nowhere | n/a | O | none |
| 85 | 10-15 11:53 | dae006d1 | 251 | [high] Cheap fix versus a fix that fits only tonight | 11:54 "I thought that this is the kind of knowledge that we just have about the project. Use opus to do deep research" | the records: `plans/operating-facts.md`, the archive (reasoned: Roman's words point at them) | No | D | none |
| 86 | 10-15 11:55 | dae006d1 | 251 | [high] Is that the value | 11:55 "Yes that's exactly it ..." | nowhere | n/a | O | none |
| 87 | 10-15 12:16 | dae006d1 | 251 | [high] Escalation when a seat judges against your words | 12:28 "That sounds rare, we have to interview the model" | interview rule, 2026-10-02 15:02, in CLAUDE.md | No (memory `rota-interview-the-seat.md` is in MEMORY.md, not named by frame 251) | R | 13, 89, 90 |
| 88 | 10-15 12:35 | dae006d1 | 251 | [med] Rule the CLAUDE.md paragraph | 12:47 "Yes rule it, add a review frame" | nowhere | n/a | O | none |
| 89 | 10-15 13:28 | dae006d1 | 244 | [high] Re-annotate wake: route to the 14B | 13:29 "Have we interviewed it?" | `plans/frame244-interview.md`, committed 6d989149 before the ask (observed: `roman_words.txt` line 3256); the question did not cite it | No | R | 13, 87, 90 |
| 90 | 10-15 13:29 | dae006d1 | 244 | [high] Same, "given the interview" | 13:30 "Did we interview it?" | same as row 89 | No | R | 89 |
| 91 | 10-15 16:24 | cd6300cd | order, sprint 7 | [low] Sprint 7 order | 16:27 "Ok, wow were already on sprint 7?" | boundary grill required | n/a | O\* | order group |
| 92 | 10-16 07:01 | cc1d654e | order, sprint 8 | [low] Sprint 8 order | no answer, timeout | boundary grill required | n/a | O\* | order group |
| 93 | 10-16 07:29 | cc1d654e | 261 | [med] The three survey lines read as the plan | 10:30 "I'm confused by this, did you already investigate with a subagent?" | the history-read rule of 2026-10-03 and the two-things rule of 2026-10-04 14:52 in CLAUDE.md require the read first | No | D | 13, 89 |
| 94 | 10-16 15:22 | 738ddbaf | reserve | [med] Reserve empty at night 151 | 15:37 "Ok, added standbys" | CLAUDE.md requires the notice | Yes | O\* | reserve group |
| 95 | 10-16 17:36 | 70d05878 | order, sprint 9 | [low] Sprint 9 order | 17:39 "Yes do it" | boundary grill required | n/a | O\* | order group |
| 96 | 10-16 22:30 | 04be1489 | order, sprint 10 | [low] Sprint 10 order | 22:32 "Stop pausing for sprint orders, I will re prioritise if something changes" | nowhere: this answer is the ruling | n/a | O\* | order group |
| 97 | 10-17 02:14 | 1cf2843b | reserve | [med] Reserve empty at night 153 | 02:15 "ok added" | CLAUDE.md requires the notice | Yes | O\* | reserve group |
| 98 | 10-17 04:31 | b0dce033 | order, sprint 11 | [low] Sprint 11 written, starting now | 11:38 "sorry pc crashed" | the 10-16 22:33 ruling: a notice, not a wait | Yes | O\* | order group |
| 99 | 10-17 16:40 | 0e37e9d7 | 114 | [med] May a Developer restore a definition its own batch broke | 16:46 "What does your questions mean?" | law 12, touch route cf067ce4, composition line 73, Roman's 10-04 14:18 "investigate this with a sub agent" | composition: Yes; law 12: No | R | 26, 27, 29, 103 |
| 100 | 10-17 18:15 | d7c5dc6d | 287 | [med] How the investigation reads its evidence | 18:17 "this is just a basic approach, youre not reasoning about the purpouse" | CLAUDE.md: "Bulk reading goes to agents"; memory `rota-grill-purpose-before-content.md`: purpose before content | No | R | 102 |
| 101 | 10-17 18:18 | d7c5dc6d | 287 | [med] Which sign tells you the new desk works | 18:19 "nothing measurable, we stay aware of all relevant points previously discussed without clutter" | nowhere | n/a | O | none |
| 102 | 10-17 18:20 | d7c5dc6d | 287 | [med] Awareness without clutter: which memo lands | 18:23 "im not re-discussing this ... the whole design and rationale should be in the logs answers should be retreived by subagents" | Roman's 10-04 14:34 answer of row 30 and the two-things rule of 2026-10-04 14:52 in CLAUDE.md | No | R | 30, 100 |
| 103 | 10-17 ~16:48 | 0e37e9d7 | 114 | (no rating) Same as row 99, as a story: may a builder restore what it broke | 16:50 "File writes were always permitted everywhere, just that if there were unexpected changes then the architect is required to sign off. I thought we already discussed this, did you look into this?" | same as row 99 (observed: `roman_words.txt`, 2026-10-17T15:50:54Z) | composition: Yes; law 12: No | R | 26, 27, 29, 99 |

**Counts** (observed: this table).

- R, answered by the records: 19. Rows 6, 12, 15, 26, 27, 28, 30, 59,
  60, 61, 62, 64, 87, 89, 90, 99, 100, 102, 103.
- D, dissolved on a read: 6. Rows 5, 14, 29, 68, 85, 93.
- O, open: 78. Of these, 32 are O\*, asked because a rule required it:
  23 in the order group and 9 in the reserve group. 46 are design or
  run choices that no record held.
- Asked twice or more by substance: 71 rows in 10 groups. Without the
  order group and the reserve group, which a rule repeats: 38 rows in 8
  groups.

(reasoned: the R and D line is a judgement. Rows 62 and 100 are rules
on the method, not on the substance, and a reader can move them to O.
Then R is 17.)

## 1. The questions asked more than once

1. **Frame 114, may a Developer write on a file no criterion names:**
   rows 26, 27, 29, 99, 103. 5 asks, sessions 5e8ace65, 419281dc,
   0e37e9d7, 2026-10-04 and 2026-10-17. Rows 26 and 27 went in the same
   minute from two sessions (observed: 14:16 for both). On 10-04, 419281dc
   read the records after Roman said "investigate this with a sub agent",
   and found "The fix was always allowed" (row 29). That finding stayed in
   `plans/frame114-read.md` and in the stack's 10-04 status. It never
   reached a law or a DECISIONS entry. On 10-17, 0e37e9d7 read the
   composition page, the momentum note and the open frames. None of them
   named law 12 or the 10-04 read. It asked twice more (observed:
   `frame114-history-read.md`, header and section 4; DECISIONS 2026-10-17
   entry).
2. **Frame 115, words on the Architect's answer:** rows 15, 28, 30. 3
   asks, sessions 46f23339 and 419281dc. Law 2 holds the answer. Roman
   answered row 30 with "we have already discussed this". Neither session
   had law 2 on its read list (reasoned: the read list has no law file).
3. **What a seat's note is for, and who reviews it:** rows 51 to 55, 59
   to 61, 64. 9 asks, sessions be3ef742, c81dd240, 31e55586, 10-11 and
   10-12. Roman answered on 10-11 at 15:43 and 15:59. 31e55586 held frame
   204 open with `plans/frame204-design.md` and asked again 32 hours
   later. Roman's answers of 10-11 were in the AskUserQuestion results of
   another session's transcript only (reasoned: no record row quotes them
   before 10-12 23:31).
4. **Did you interview the seat:** rows 13, 14, 87, 89, 90, and 93 by
   kind. Roman asked "did you interview" or "did you investigate" four
   times after the rule of 2026-10-02. On rows 89 and 90 the interview
   existed and the question did not cite it.
5. **The reserve is empty:** rows 10, 37, 47, 57, 58, 65, 70, 71, 94,
   97. 10 notices, 10 sessions. A rule requires each one. The repeat is
   a fact of the reserve, not of the records.
6. **The order of frames:** 27 rows. Rules required each ask until
   2026-10-16 22:33, when Roman said "Stop pausing for sprint orders".
7. **The second card:** rows 19 to 21, 23, 25. One session asked 3, a
   second session asked 2 more on the same card.
8. **Frame 106, the dead-end case:** rows 7, 8, 9. One session, three
   shapes of one question.
9. **The Critic's route and graph edges:** rows 4, 5, 6, 50. Law 3
   answers the route class each time.
10. **Roman's words to the seats:** rows 74, 78, 79. Two sessions. Roman:
    "I have no idea what this means".

## 2. The cost

- 93 of 103 questions have a typed reply in the file. The sum from ask to
  next typed message is 57.8 hours (observed: `cost.py` on
  `questions_full.txt`). The next message is not always an answer: rows
  15, 16, 22, 23 got an unrelated message.
- Nine waits pass 2 hours: rows 11 (5.3 h), 15 (2.7 h), 18 (7.6 h), 22
  (5.0 h), 31 (3.0 h), 39 (3.7 h), 75 (7.8 h), 93 (3.0 h), 98 (7.1 h).
  Together 45.2 hours. Most cross a night of Roman's sleep (reasoned: the
  ask times are 04:00 to 07:30).
- The R and D rows cost Roman 25 replies. Their waits sum to about 7.3
  hours, mostly row 15's 2.7 hours and row 93's 3.0 hours (observed: the
  table times).
- 26 answers took the recommended option: rows 1, 2, 3, 4, 6, 9, 11, 12
  (order half), 18, 19, 20, 24, 25, 35, 40, 46, 48, 50, 53, 56, 81, 82,
  and the push replies 31, 72, 73, 95 (observed: `cost.py`, and the push
  texts). 4 more went by timeout: rows 38, 41, 69, 92.
- 22 answers were a question back or a complaint: rows 5, 7, 8, 12, 14,
  29, 30, 36, 44, 49, 52, 54, 59, 60, 68, 78, 79, 89, 90, 99, 102, 103.
  Each one is a sign that the ask did not stand alone (reasoned).

## 3. What the questions have in common that the records did not key

Each repeated question has a natural key: the door, the law or the file
the question is about. No record is findable by that key from the
hand-off read list.

| Question group | Natural key | Record that held it | Findable by the key? |
|---|---|---|---|
| Frame 114 | the write door: `code.commit`, the unnamed-definition door, the fence; law 12 | `LAWS.md:325-342`; `touch_strayed.md`; `frame114-read.md` (10-04) | No. Law 12's title "Constraints protect external commitments only" does not hold the words write, door or permission. The 10-04 read sat in a frame file that no door names (observed: `LAWS.md:325`) |
| Frame 115 | the edge `architect -> developer: answer`; law 2 | `LAWS.md:112-119` | No. Law 2's title is "Conclusions travel; reasoning stays home". A search for "answer" or "prose" in the law file does not reach it (reasoned) |
| Notes, frame 204 | the note kinds, the merge, the Architect's review | Roman's AskUserQuestion results of 10-11; `frame204-design.md` | No. Roman's answers lived in one transcript. The design file did not quote them before row 61 (reasoned: rows 59 to 61 restate them) |
| Inherited test | `inh_*` tests, the Developer's regression | DECISIONS and the ruling of 2026-09-14, cited in CLAUDE.md | Partly. CLAUDE.md cites it in a paragraph about escalation, not under the test or the door |
| Interview | the seat's turn, `interview_turn.py` | CLAUDE.md, memory `rota-interview-the-seat.md`, `frame244-interview.md` | Yes for the rule. No for the instance: the question text did not cite the interview file |
| Developer scope, row 64 | "nobody asked for", the Developer's role | `rota/ROLES.md:150-170` | No. ROLES.md is not on the read list |
| Graph edges | the edge name, law 3 | `LAWS.md:121-147` and the graph | Partly. Law 3 names "message route" and "derived" (observed: row 5 cites the law in the question) |
| Method of a read | "read by agents" | CLAUDE.md, memory `rota-grill-purpose-before-content.md` | Yes. Both are loaded every turn (observed: the system context of this read) |

The common shape (reasoned: from the table above and section 1):

- The answer stands in a law, a role page or a ruling under a title that
  names the principle, not the door or the file. A session that meets a
  door's refusal text greps for the door, and the law does not answer to
  that word.
- A session's own read that dissolves a question writes the result to a
  frame file. The frame closes and leaves the stack, and nothing keyed by
  the door points at the file (rows 29 and 99).
- Roman's answers in an AskUserQuestion result stay in one transcript
  until a session copies them into a record. Two sessions later asked the
  same design question (rows 59 to 61).
- The hand-off read list names the composition page, the momentum note,
  the open frames and the frame's memory files. It does not name
  `LAWS.md`, `DECISIONS.md` or `ROLES.md`. All 19 R rows had their answer
  in a file outside the list, except rows 59 to 61 and 99, where the open
  frame or the composition line was on the list and the session did not
  connect it to the question.

Usage: about 70k tokens of the 80k cap (reasoned: this agent's own count; read the harness line for the true figure).
