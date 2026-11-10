One reader and one pass, group b, nights 127 to 160.

## How this extract reads its sources

- Times. `runs.tsv` gives UTC. The read pages, the status lines and the commits give local time, UTC+1 in this window. A gap is in UTC.
- "Read landed" is the commit that adds the read page (`git log --diff-filter=A`). Many reads land in one commit with a frame push. Column 5 takes the first commit after that commit.
- Walls. A read of nights 127 to 137 has two lists: new walls, and a table of known walls with a case. The new walls get ids here. The table goes into one line "also named". A read of nights 138 to 142 has no wall list. Its walls here come from its verdict lines, its findings and its register lines. A read of nights 143 to 148 lists "Candidate frames, new". Its walls here are the title wall and the candidates. A read of nights 149 to 154 places each wall by the guide, and a read of nights 155 to 163 has a wall table.
- Causes. The wall guide started on 2026-10-15 (frame 251). A read before night 149 names no cause, so its walls read `[C?]`. From night 149 on, the bracket is the first cause that the read names in the wall's placement. A wall with no cause in the read reads `[C?]`.
- Column 6. A frame "from" a read is a frame whose first lines or push line cite that read, or a read of the same turn (a cycle read or a sub-read). The state is from the frame's status lines before the next run's start (`plans/stack.md` and `plans/archive/stack-2026-10-*.md`). "Built" means a status line before that start says a pass "committed at", "landed on the implementer" or "is built". A frame with only its push line is "still open". Several lines and no build line is "not sure".
- Column 8. "Same cause" means the next read, or the frame's status line for that night, places the case on the same frame. "Same sign at the same place" means the next read names the same sign on the same seat or record. Everything else that looks near is "not sure". "Not found" means not in the wall lists and frame status lines this extract read. It is not proof of absence.
- Column 12. The class check is a keyword search of the read page (script `c12.py` in the lead's scratchpad: "abandon", "park", "stuck", "exhaust", "amend", "contest ... cancel", "running", "crash"). A hit is quoted. A hit whose words do not clearly name the stop reads "not sure".
- Roman's words come from `plans/method/meta-direction-read-2026-11-10.md` (times in UTC there). That read found no typed message from 2026-10-08 to 2026-10-10. No transcript was opened.

### night 127
- read pages: `plans/night127-read.md`; sub-read `plans/frame131-read.md` (landed 2026-10-07 01:10 local, during the run).
- read landed: 2026-10-07 01:21 UTC (ca0d836f). Run end: 2026-10-07 01:06 UTC (runs.tsv). Gap: 0:15
- 2: "The frame now waits on night 127, its measure: Tester challenge sessions that end with no call after a reply with a test body, from 2 of 5 on night 126 to at most 1 in 5" (frame 152, status 2026-10-06 23:28). Frames 164 and 165 have measures for night 127 in their status lines of 23:16 and 23:20.
- 3: frame status lines of frames 152, 164 and 165 in `plans/archive/stack-2026-10-07.md`.
- 4: 6 new walls.
  - n127-W1: merged bg_3 raises `NameError` on its new path, tests never take it [C?] (source: `plans/night127-read.md`:159)
  - n127-W2: span door's end offer admits a write that removes a branch, no `dropped` note [C?] (source: :160)
  - n127-W3: Tester's own wrapper command declares no argument, the test passes one [C?] (source: :161)
  - n127-W4: parser prints a `SyntaxWarning` for a value that holds `\}` [C?] (source: :162)
  - n127-W5: a seat answers a challenge with nothing, row stamped answered (I9) [C?] (source: :163)
  - n127-W6: one-time Tester nudge spent on a reply with no test [C?] (source: :164)
  - also named: known walls with a case, frames 167, 140, 170, 159, 166, 147, 148, 130, 113, 169 (source: :168-179).
- 5: frame 131's commits join `rota/foundation` (68d1f6eb at 02:21:52, joined at 26467821 02:22:14), 0 min after the read. The commits were written during the run (author times 01:21 to 02:07).
- 6: 172: still open at night 128 (one push line, 02:20). 173: still open. 174: still open. 175: still open (fs2 on frames.json).
- 8: n127-W1: 128: not met (frame 172 status 05:03, "6 of 6 stored tests ... take the added path"). 129: no read. 130: not found. n127-W2: met in n128 as known row "173 ... s246 t22": same cause. 129: no read. 130: not found. n127-W3: met in n128 as n128-W3: not sure. n127-W4: not found in 128 or 130. n127-W5: met in n128 as known row "174, 4 I9 rows": same cause. met in n130 as known row "174, 5 I9 rows": same cause. n127-W6: not found in 128 or 130.
- 9: the session: "Then night 128 as the walk, its measure: Tester tests stored on bg_1 that pass a plain function to a runner's invoke" (frame 131, status 2026-10-07 02:22, rota-b4). Decided: continued.
- 11: rota-b4, session 86c3e06e (frame 172 to 175 push lines; commit 93d591c3).
- 12: named: gaveup_nothing not sure (":62 `tick:exhausted`, 10 of 10" is a table of refusals), gaveup_red not sure (same line). Not named: none clearly.

### night 128
- read pages: `plans/night128-read.md`; sub-reads `plans/frame170-history-read.md` (05:12 local) and `plans/frame170-merges-read.md` (05:15 local).
- read landed: 2026-10-07 04:03 UTC (fd6da6f2). Run end: 2026-10-07 03:48 UTC. Gap: 0:15
- 2: "Then night 128 as the walk, its measure: Tester tests stored on bg_1 that pass a plain function to a runner's invoke, from 3 of 3 on ni[ght 127]" (frame 131, status 2026-10-07 02:22).
- 3: frame 131's status line in `plans/archive/stack-2026-10-07.md`.
- 4: 3 new walls.
  - n128-W1: prints door refuses a decorator factory test, the stdout test cannot pass [C?] (source: `plans/night128-read.md`:157)
  - n128-W2: a finding id named again in the next batch replaces the last finding [C?] (source: :158)
  - n128-W3: frame 131's door does not read a local def under a decorator factory [C?] (source: :159)
  - also named: known rows 173, 98 and 113, 171, 170, 174, 130, 167, 166, 148, 147, 159, 169, reply cuts (source: :163-177).
- 5: commit 93d591c3 "session 86c3e06e hands the stack off with frame 170 next", 0 min after the read (05:04:23 local).
- 6: 176: still open at night 129. 177: built before night 129 (status 09:25), closed 2026-10-08 01:53 on night 130's read. 178 (from the merges read): still open at night 129, closed on night 131's read. 179 (from the merges read): still open.
- 8: n128-W1: 129: no read. 130: not sure (night 130 section 2 reads frame 177's factory door). 131: not met (known row "177 ... The factory door refused 0"). n128-W2: 130: not sure (known row "178, `findings.find` admits a grain the diff does not touch", another half of the frame). 131: not sure (frame 178 closes in section 1). n128-W3: met in n130 as known row "176 ... s250 t2": same cause. met in n131 as known row "176, 3 stored tests": same cause.
- 9: the session: "session 86c3e06e hands the stack off with frame 170 next" (commit 93d591c3). Decided: continued.
- 11: rota-b4 (86c3e06e) writes the read. Session 6cc11c8b takes the stack (commit b0701bbb, 05:04) and writes the frame 170 reads (rota-52). Hand-off 86c3e06e to 6cc11c8b.
- 12: named: gaveup_red yes (":14 bg_3 stuck: 4 red at 191e47a6").

### night 129
- read pages: no read
- read landed: no read. Run end: 2026-10-07 12:42 UTC. Gap: no read
- 2: no read
- 3: no read
- 4: no read
- 5: no read
- 6: no read
- 8: no read. Nights 129 and 130 ran at 9d6ad60c. Night 130's read counts night 129's onboarding in its own counts (source: `plans/night130-read.md`:3).
- 9: no read
- 11: no read
- 12: stop classes of runs.tsv: none.

### night 130
- read pages: `plans/night130-read.md`
- read landed: 2026-10-08 00:53 UTC (7fc29a1c). Run end: 2026-10-08 00:41 UTC. Gap: 0:12
- 2: "Relaunch warm from `.rota/launch_night129.sh` ... as night 130, about 25 minutes less than cold. The frame stays validating." (frame 170, status 2026-10-07 13:42, rota-a1).
- 3: frame 170's status line, `plans/archive/stack-2026-10-08.md`.
- 4: 5 new walls.
  - n130-W1: lines door admits an added line that does not touch the criterion [C?] (source: :164)
  - n130-W2: a Critic sends `verdicts.emit` again after its verdict landed [C?] (source: :165)
  - n130-W3: two Tester tests of one batch assert different results of one call [C?] (source: :166)
  - n130-W4: a `version_option` test passes no version, click cannot find it [C?] (source: :167)
  - n130-W5: batch ran 7 attempts with no test of its criterion, went green [C?] (source: :168)
  - also named: known rows 176, 178, 179, 171, 98 and 113, 147, 174, 130, 167, 169, 115, 114, span crosses blocks, reply cuts (source: :172-186).
- 5: commit 91e76e2e "session 18588d6d takes frame 178 by timeout on the recommended answer", 20 min after the read.
- 6: 180: still open at night 131 (closed 2026-10-08 09:42 on night 132's read). 181: still open. 182: still open.
- 8: n130-W1: 131: not met (known "Frame 170's lines door, 0"). 132: not sure (n132-W1 names frame 180 as nearest). 133: not found. n130-W2: met in n131 as known row "181, 2 refusals": same cause. met in n132 as known row 181: same cause. met in n133 as known row 181: same cause. n130-W3: 132: not sure (known row 143). n130-W4: met in n132 as known row 143 "2 on bg_3 with no version": same sign at the same place. n130-W5: met in n131 as n131-W1: same cause (frame 182 status "night 131: bg_3 merged with no test of its own"). met in n132 as known row "182, 1 merge, bg_4": same cause. 133: not met (frame 182 status "bg_1 merged with its own 3 tests").
- 9: the session: "frames 170 and 177 close on night 130's read, and frames 180 to 182 are [pushed]" (commit 7fc29a1c). Decided: continued.
- 11: rota-a1 (frame 180 to 182 lines); session 18588d6d (commit 91e76e2e).
- 12: named: gaveup_nothing yes (":127 `Stuck: ... 3 tests are still failing`"), gaveup_red yes (":144 ... `tick:exhausted` sent m138").

### night 131
- read pages: `plans/night131-read.md`
- read landed: 2026-10-08 05:49 UTC (c76bb34e). Run end: 2026-10-08 05:37 UTC. Gap: 0:12
- 2: "The six commits of `f178` are on `rota/foundation` ... This session's gate runs on the joined tree at 51678e1f. Then the next night as the walk." (frame 178, status 2026-10-08 03:41). No measure is written for the night.
- 3: frame 178's status line, `plans/archive/stack-2026-10-08.md`.
- 4: 6 new walls.
  - n131-W1: batch merges with no own test, a criterion counts another batch's tests [C?] (source: :207)
  - n131-W2: a ruling by ledger id never rules the glossary senses [C?] (source: :208)
  - n131-W3: Liaison's clarify refused for a backticked identifier that names no row [C?] (source: :209)
  - n131-W4: `k0` violated refusal says check constraints that bind a file [C?] (source: :210)
  - n131-W5: principal's script answers a glossary question with another item's answer [C?] (source: :211)
  - n131-W6: batch's first commit holds the behaviour, later commits remove it [C?] (source: :212)
  - also named: known rows 176, 177, 179, 181, 171, 129, 174, 130, 167, 169, 148, 166, 147, span, reply cuts, made-up results (source: :216-233).
- 5: commit 238a0eae "the gate holds on frame 180's join, night 132 runs as its walk", 5 min after the read.
- 6: 183: not sure (2 status lines before night 132, no build line).
- 8: n131-W1: met in n132 as known row "182, 1 merge, bg_4": same cause. 133: not met (frame 182 status). 135: no read. n131-W2: 132: not met ("Frame 183, 0 collision sessions"). met in n133: same cause (frame 183 status "night 133 ... 3 `tick:term_collision` sessions"). 135: no read. n131-W3: not found in 132 or 133. n131-W4: 132: not sure (known row 179, `k0`). n131-W5: not found. n131-W6: 132: not sure (known row 176).
- 9: the session: "frame 178 closes on night 131's read, and three frames gain the night's [cases]" (commit c76bb34e). Decided: continued.
- 11: rota-a1, session 18588d6d; hand-off 18588d6d to 225aec9c (commit 2d3010ca, 06:54).
- 12: named: gaveup_nothing yes (":21 bg_4, stuck on 4 red"). Not named: ab_amended.

### night 132
- read pages: `plans/night132-read.md`
- read landed: 2026-10-08 08:42 UTC (b3575cea). Run end: 2026-10-08 08:27 UTC. Gap: 0:15
- 2: "This session's gate runs on the joined tree now, after night 131's end. Then night 132 as this frame's walk." (frame 180, status 2026-10-08 06:39). No measure in the line.
- 3: frame 180's status line, `plans/archive/stack-2026-10-08.md`.
- 4: 7 new walls.
  - n132-W1: a criterion that holds by an absence has no added line [C?] (source: :266)
  - n132-W2: a Critic sends the same refused pass again with no prose [C?] (source: :267)
  - n132-W3: `msg.challenge_tester` with `refs` as a dict refused for a wrong reason [C?] (source: :268)
  - n132-W4: rulings on a chat entry reach the ledger and the decisions [C?] (source: :269)
  - n132-W5: each quarantined chat entry makes a new quarantine key [C?] (source: :270)
  - n132-W6: a Tester stores its own test with an `inh_` id [C?] (source: :271)
  - n132-W7: merged change prints fewer version parts than his sentence [C?] (source: :272)
  - also named: known rows 142, 182, 129, 143, 176, 177, 179, 181, 174, 130, 169, 148, 147, span, reply cuts, made-up results (source: :276-294).
- 5: commit f2150586 "frame 180 closes on night 132's read, and eight frames gain the night's cases", 0 min after the read.
- 6: none found. No frame cites night 132's read (frames.json search).
- 8: n132-W1: 133: not found. 135: no read. 136: not sure (n136-W9 names frame 180). n132-W2: 133: not sure (known row 181). n132-W3: not found. n132-W4: 133: not sure (n133-W10, frame 142). n132-W5: not found. n132-W6: not found. n132-W7: 133: not found. 136: not sure (n136-W7, frame 182).
- 9: Roman, by the session's record: "Roman orders frame 41, then 142, with 182 as a read beside the next night" (commit 5783cb24, 09:52 local). His own words are not in the meta direction read. Decided: turned (frame 41, the agent principal, runs next).
- 11: rota-a1; session 225aec9c holds the stack (commit 2d3010ca).
- 12: named: gaveup_nothing yes (":154 ... the walk ended `Stuck`"). Not named: ab_amended.

### night 133
- read pages: `plans/night133-read.md`
- read landed: 2026-10-08 18:37 UTC (a1c07a99). Run end: 2026-10-08 18:18 UTC. Gap: 0:19
- 2: "Then night 133 with `GAUNTLET_AGENT=opus` from a worktree at the closing commit, as this frame's walk." (frame 41, status 2026-10-08 15:22, rota-39). No measure in the line.
- 3: frame 41's status line (frames.json, frame 41).
- 4: 10 new walls.
  - n133-W1: Liaison copies its earlier ask-back from `recent_chat` [C?] (source: :364)
  - n133-W2: present pages list bookkeeping rows, not the request [C?] (source: :365)
  - n133-W3: "a separate request, for later" lands as `contest`, batch abandoned [C?] (source: :366)
  - n133-W4: correction raises item version, cancel abandons the live batch [C?] (source: :367)
  - n133-W5: Vision Keeper approves an item on the relay of its own report [C?] (source: :368)
  - n133-W6: grouping opens a batch on a contested item, cancel takes it [C?] (source: :369)
  - n133-W7: a ruling with `'ask'` as a verdict is refused and resent [C?] (source: :370)
  - n133-W8: an ask open at the end of onboarding is answered again [C?] (source: :371)
  - n133-W9: two walks end at the step cap of 250, nothing merged [C?] (source: :372)
  - n133-W10: a ruling approves an entry of his own words as a line [C?] (source: :373)
  - also named: known rows 140, 114, 130, 174, 177, 178, 179, 181, 147, 148, 169, reply cuts, made-up results (source: :379-394).
- 5: commit adaf2504 "frame 142's scope report and design run on Opus", 1 min after the read.
- 6: 184: still open at night 135. 185: still open. 186: still open (closed 2026-10-11 00:30 on night 139's read).
- 8: n133-W1: 135: no read. 136: not found. met in n137 as known row "184, the ask-back copy, 1": same cause. n133-W2: 136: not sure (n136-W3, frame 45). n133-W3: 136: not found. met in n137 as known row "185 ... 1, s299": same cause. n133-W4: not found. n133-W5: not found. n133-W6: 136: not found. met in n137 as known row "186, 13 batches": same cause. n133-W7: met in n136 as n136-W10 ("Night 133 had `ask`, s130"): same sign at the same place. n133-W8: met in n136 as n136-W12 ("Night 133: 1"): same sign at the same place. met in n137 as known row "41 ... 2": same sign at the same place. n133-W9: not found. n133-W10: 136: not sure (n136-W2).
- 9: the session: "frame 142's scope report and design run on Opus" (commit adaf2504). Decided: continued.
- 11: rota-39 (frame 41), rota-a0 (frames 184 to 186).
- 12: named: ab_after_giveup yes (":18 The abandon loop: 6 batches abandoned"). pend_behind not sure (":8" is about park-ask choices). Not named: ab_phantom.

### night 134
- read pages: no read. Night 134 is not a row of `runs.tsv`. The brief names it a log with no database.
- 2 to 6, 9, 11: no read
- 8: no read
- 12: not in runs.tsv.

### night 135
- read pages: no read
- read landed: no read. Run end: 2026-10-09 04:27 UTC. Gap: no read
- 2: no read
- 3: no read
- 4: no read
- 5: no read
- 6: no read. Frames 187 and 188 cite night 135 in their first lines (frames.json). No read page exists.
- 8: no read
- 9: no read
- 11: no read
- 12: stop classes of runs.tsv: none.

### night 136
- read pages: `plans/night136-read.md`
- read landed: 2026-10-09 09:25 UTC (e57656a3). Run end: 2026-10-09 09:08 UTC. Gap: 0:17
- 2: "The two other lows go to night 136's read. Then a narrow review and the launch." (frame 142, status 2026-10-09 06:05, rota-68). No measure in the line. The read tests "Frame 142's three ratios" (source: :23).
- 3: frame 142's status line, `plans/archive/stack-2026-10-09.md`.
- 4: 12 new walls.
  - n136-W1: correction of predicted files has no row, batch-line door refuses it [C?] (source: :245)
  - n136-W2: a ruling approves every line while his words refuse the page [C?] (source: :246)
  - n136-W3: contest about an item on constraint rows makes the Architect log a row [C?] (source: :247)
  - n136-W4: approval of an Architect row lands on the constraint, not the item [C?] (source: :248)
  - n136-W5: `agenda` tick outranks `annotate`, batch never gets its touch set [C?] (source: :249)
  - n136-W6: quarantined wake presents a batch as a touch note [C?] (source: :250)
  - n136-W7: `mergeable` accepts a criterion's test from another batch [C?] (source: :251)
  - n136-W8: a stored test passes whatever the code does [C?] (source: :252)
  - n136-W9: kind check admits a `:param` docstring line [C?] (source: :253)
  - n136-W10: a ruling word not approve, contest or revise ends the session [C?] (source: :254)
  - n136-W11: answered-question refusal in report mode sends the seat to a relay [C?] (source: :255)
  - n136-W12: a page open at a walk's end is answered again [C?] (source: :256)
  - also named: known rows 147, 177, 170, 181, 178, 167, 148, 130, 174, 179, 169, reply cuts, made-up results (source: :260-274).
- 5: commit c18d85d7 "frame 142 closes on night 136's read, and frame 189, the prediction page", 0 min after the read.
- 6: 189: not sure (3 status lines, no build line). 190: built before night 137 (status 10:54), closed 2026-10-10 03:30 into frame 193.
- 8: n136-W1: 137: not sure (n137-W4). 138, 139: not found. n136-W2: not found. n136-W3: not found. n136-W4: not found. n136-W5: not found. n136-W6: 137: not sure (n137-W6, another key). n136-W7: 137: not sure (n137-W10). met in n138 as the verdict "Walk 1 merged b_2 with 0 tests of its own ... Frames 182 and 172" (:19): same cause. n136-W8: 137: not sure (known row 147). n136-W9: not found in 137 to 139. n136-W10: met in n137 as known row "192, `drop`, 4 refusals": same cause. 138: not met (frame 192 verdict, 5 of 5 drew a ruling). met in n139 as the frame 192 verdict "s265 sent `drop` as a value": same cause. n136-W11: 137: not sure (known row 187). n136-W12: met in n137 as known row "41 ... m62 and m161": same sign at the same place.
- 9: the session: "frame 142 closes on night 136's read, and frame 189, the prediction page" (commit c18d85d7). Decided: continued.
- 11: rota-68, rota-9e (frames 189, 190).
- 12: named: pend_behind not sure (":3" names the park page of the tree). Not named: ab_amended.

### night 137
- read pages: `plans/night137-read.md`
- read landed: 2026-10-10 02:28 UTC (4664e08b). Run end: 2026-10-09 19:19 UTC. Gap: 7:09
- 2: "The last delta review runs on Opus on a worktree at af535499 ... The night launches on its verdict." (frame 190, status 2026-10-09 16:32). No measure in the line.
- 3: frame 190's status line, `plans/archive/stack-2026-10-10.md`. The read: "Roman stopped it at 20:20 in walk 3" (source: :3).
- 4: 10 new walls.
  - n137-W1: his words about another request land on this page's item [C?] (source: :276)
  - n137-W2: correction of a `check:` line has no route to the test [C?] (source: :277)
  - n137-W3: a note's contest contests its `about_ref`, overrides his approve [C?] (source: :278)
  - n137-W4: clarify answer asking to remove files is ruled approve on the batch [C?] (source: :279)
  - n137-W5: Tester's file door sends tests away from the predicted file [C?] (source: :280)
  - n137-W6: quarantined page of a contested-item key does not say what failed [C?] (source: :281)
  - n137-W7: stamp adds only items the refs reach, not the walk's request [C?] (source: :282)
  - n137-W8: a ruling call with an unclosed quote ends the session [C?] (source: :283)
  - n137-W9: `batches.annotate` grows by one path a call in a loop [C?] (source: :284)
  - n137-W10: a merged helper is not exported though he asked for it [C?] (source: :285)
  - also named: known rows 186, 192, 187, 185, 184, 41, 147, 169, 170, 181, 178, 174, 130, 114, 148, 166, span, reply cuts (source: :289-308).
- 5: commit 43461f47 "frame 190 closes into frame 193, the second request, on Roman's order", 2 min after the read.
- 6: 192: still open at night 138. 193: built before night 138 (status 05:45), closed 2026-10-11 00:30 on night 139's read.
- 8: n137-W1: 138: not sure (frame 193 ratio 1 fails, `plans/night138-read.md`:9). 139: not sure. n137-W2: not found in 138 to 140. n137-W3: not found. n137-W4: 138: not sure (the `disputed_paths` miss on m132, :107). n137-W5: not found. n137-W6: not found. n137-W7: not found. n137-W8: 138: not sure (register line 3, words inside rulings). n137-W9: not found. n137-W10: 138: not sure (b_2 merged, NameError).
- 9: Roman, by the session's record: "frame 190 closes into frame 193, the second request, on Roman's order" (commit 43461f47). Night 138 later stopped "on Roman's ruling of 2026-10-09 20:19" (`plans/night138-read.md`:3). Decided: turned.
- 11: rota-8a, rota-91 (frames 192, 193).
- 12: named: ab_after_giveup yes (":15 the cancel abandoned each at its first wake. 13 of 14"). ab_phantom not sure (the same line names first-wake abandons, the class is not checked).

### night 138
- read pages: `plans/night138-read.md`
- read landed: 2026-10-10 13:12 UTC (00adb5eb). Run end: 2026-10-10 12:55 UTC. Gap: 0:17
- 2: "Then a three-point review, then night 138 from a worktree at the closing commit" (frame 193, status 2026-10-10 08:26, rota-91). The read checks frame 193's three ratios against targets, for example "Target at most 1 in 10" (source: :9).
- 3: frame 193's status lines, `plans/archive/stack-2026-10-11.md`.
- 4: 7 walls, from the verdict and register lines.
  - n138-W1: frame 193 ratio 1 fails, request B never got a statement [C?] (source: :9, :12)
  - n138-W2: ratio 3 fails, 2 of 43 answers draw no ruling [C?] (source: :11)
  - n138-W3: frame 185 open, his put-off reached no door [C?] (source: :13)
  - n138-W4: walk 1 merged b_2 with 0 own tests, `NameError` on every call [C?] (source: :18)
  - n138-W5: `CliRunner` hides `NameError`, the red row shows empty output [C?] (source: :19, :191)
  - n138-W6: Liaison puts `words` inside the `rulings` map, answer lost [C?] (source: :192)
  - n138-W7: `disputed_paths` misses "should not edit" on m132 [C?] (source: :107)
- 5: commit 3dca7429 "night 138's verdicts land on frames 193, 194, 185, 186 and 192", 0 min after the read.
- 6: 194: not sure (2 status lines). 195: still open at night 139. 196: still open. 197: still open (closed on night 140's read). 200: not sure (no status line parsed).
- 8: n138-W1: 139: not met (ratio 1 holds, `plans/night139-read.md`:7). 140, 141: not found. n138-W2: 139: not sure (ratio 3 fails by one, cause not the frame's). 140: not met (frame 197 status "0 of 38"). n138-W3: 139: not met ("Frame 185: no case"). n138-W4: met in n139 as n139-W3: same cause (frame 172 status 2026-10-11 00:30 "night 139 adds an instance"). n138-W5: 139: not met ("frame 195 had no case"). 140: not met (frame 195 status "0 of 7"). n138-W6: 140: not met (frame 197 status "0 of 38"). n138-W7: not found in 139 to 141.
- 9: the session: "night 138's verdicts land on frames 193, 194, 185, 186 and 192" (commit 3dca7429). Decided: continued.
- 11: rota-06, rota-91 (frames 194 to 197).
- 12: named: ab_after_giveup not sure (":10 batches abandoned at their first wake: 0 of 3"). gaveup_nothing not sure (":98 `check:` lines that say "gave up"").

### night 139
- read pages: `plans/night139-read.md`; sub-read `plans/frame199-read.md` (2026-10-11 01:40 local).
- read landed: 2026-10-10 23:30 UTC (9b5aeafd). Run end: 2026-10-10 23:12 UTC. Gap: 0:18
- 2: "Then the commit, night 139 from a worktree at it, and a two-point review of the 3d hunks beside the night." (frame 193, status 2026-10-10 21:18, rota-06). The ratio targets are restated in the read (source: :7-9).
- 3: frame 193's status lines, `plans/archive/stack-2026-10-11.md`.
- 4: 6 walls, from the verdicts, the register lines and the sub-read.
  - n139-W1: ratio 3 fails by one answer, m142, cause not the frame's [C?] (source: :9)
  - n139-W2: a merged request's open ledger rows reach the next page [C?] (source: :12)
  - n139-W3: bg_3 loop, Tester tests call decorators wrong, Developer fits them [C?] (source: :15)
  - n139-W4: on a quarantine page the Liaison contests the batch line [C?] (source: :143)
  - n139-W5: same-refs step sends the Developer to code a wrong test calls [C?] (source: :144)
  - n139-W6: the gate's baseline is of 2026-09-27, four reds named by hand [C?] (source: `plans/frame199-read.md`:1)
- 5: commit 9bc17925 "frames 193 and 186 close on night 139's read", 0 min after the read.
- 6: 198: not sure (4 status lines). 199: closed before night 140 (status 2026-10-11 02:46 "closed"). 201: still open at night 140. 202: still open.
- 8: n139-W1: not found. n139-W2: not found in 140 to 142 (frame 198 status has no line for them). n139-W3: 140: not sure (`plans/night140-read.md` section 2 reads frame 200's doors). n139-W4: not found. n139-W5: 140: not sure. n139-W6: not found.
- 9: Roman: "Ok, perfect now make sure that the meta workflow adopts these. This session and all future sessions. Update the meta workflow, integrate robustly" (10-11 04:50 UTC, 84ce0759, meta direction read row 1). Also "Yes, paralelise maximally" (10-11 04:36 UTC). Decided: turned (the way of working, parallel frames).
- 11: rota-06, rota-88, rota-c5 (frames 198, 199, 201, 202); sessions 84ce0759 and be3ef742 (meta direction read rows 1 to 3).
- 12: Not named: gaveup_red (no keyword hit, :15 reads the bg_3 loop, the class is not checked).

### night 140
- read pages: `plans/night140-read.md`
- read landed: 2026-10-11 20:51 UTC (98e7aa1a). Run end: 2026-10-11 18:34 UTC. Gap: 2:17
- 2: "The night launches from 3f2e974e when the gate's lines are read" (frame 200, status 2026-10-11 16:46, rota-be). Frame 195: "The walk is the next night, with the design's fix 7 measure ... from 10 of 11 on night 138's b_3 to at most 1 in 5" (status 2026-10-11 14:53).
- 3: status lines of frames 200 and 195, `plans/archive/stack-2026-10-13.md` and `-10-11.md`.
- 4: 6 walls, from the shape and the findings.
  - n140-W1: Liaison s228 lost answer m127, walk 1 ended quiet [C?] (source: :32)
  - n140-W2: the Stuck line names a quarantined tick on an approved item [C?] (source: :30, :199)
  - n140-W3: bg_2 cannot merge, the inherited red of the cycle read [C?] (source: :3, :27)
  - n140-W4: `_plain_decorated` admits a factory return that never decorates [C?] (source: :196)
  - n140-W5: `_repoint` substring match keeps a false `in this prompt` sentence [C?] (source: :197)
  - n140-W6: challenge door refuses a second answer with different refs [C?] (source: :198)
- 5: commit 1ea71e58 "frame 200's pass 3 closes the door on a decorated result's attribute read", 0 min after the read.
- 6: 207: built before night 141 (status 22:02). 208: still open.
- 8: n140-W1: not found. n140-W2: met in n141 as n141-W1 (`plans/night141-read.md`:33): same sign at the same place. n140-W3: 141: not sure (section 3 "Frame 207 on bg_2"). 143: not met (frame 207 status "bg_3's 3 inherited tests passed 6 of 6"). n140-W4: not found. n140-W5: met in n141 (frame 208 status "night 141 counts the shape again: 2 of 3"): same cause. n140-W6: 142: not sure (`plans/night142-batch2-read.md`:189, the challenge cap).
- 9: Roman: "pause all gpu work" (10-11 18:43 UTC, meta direction read line 187). Decided: stopped (GPU work paused).
- 11: rota-be (frames 207, 208); session 59bdd13a took frames at 16:21 (frame 200 status 2026-10-11 16:25).
- 12: named: end_working yes (":3 The holding session stopped it in walk 3").

### night 141
- read pages: `plans/night141-read.md`; sub-read `plans/frame204-gate-read.md` (2026-10-12 02:57 local).
- read landed: 2026-10-12 01:15 UTC (2caa8d33). Run end: 2026-10-12 01:01 UTC. Gap: 0:14
- 2: "night 141 from that commit, cold, three sentences, the measure unchanged" (frame 200, status 2026-10-11 22:02, rota-be).
- 3: frame 200's status line, `plans/archive/stack-2026-10-13.md`.
- 4: 7 walls, from the shape, the sections and the sub-read.
  - n141-W1: Stuck line of walk 1 names an approved item [C?] (source: :33)
  - n141-W2: walk 2 crashes in `tick_agenda` on a `None` criterion [C?] (source: :34)
  - n141-W3: no run at bg_2's head, `tests.load` shows a stale run [C?] (source: :31)
  - n141-W4: s197's write over `confirm` dropped the body after `except` [C?] (source: :75)
  - n141-W5: m14 answered twice, sign-off page open after `ONBOARDED` [C?] (source: :191)
  - n141-W6: encode door offers a triage verdict it refused in the same reply [C?] (source: `plans/frame204-gate-read.md`, frame 211)
  - n141-W7: answer door's refusal steers the Architect to resend with the finding [C?] (source: `plans/frame204-gate-read.md`, frame 212)
- 5: commit 2e6580b8 "frame 209's first gate reads stale on frame 204's cases", 2 min after the read.
- 6: 209: built before night 142 (status 02:09). 210: built before night 142 (status 02:24). 211: still open. 212: still open.
- 8: n141-W1: not found. n141-W2: 142: not found. 143: not met (frame 209 status "no `frontier` call raised"). n141-W3: 143: not met (frame 210 status "23 of 23 wakes"). n141-W4: 142, 143: not found. met in n144 (frame 173 status "night 144: 1 admitted span write with no note"): same cause. n141-W5: not found. n141-W6: not found. n141-W7: met in n144 (frame 212 status "4 of 4 Architect unresolved wakes ended with nothing"): same cause.
- 9: the session: "night 141's read lands, frame 210 is pushed for the stale test run" (commit 2caa8d33). Decided: continued.
- 11: rota-cd (frames 209 to 212).
- 12: named: end_working yes (":3 Walk 2 crashed in the agenda tick").

### night 142
- read pages: `plans/night142-read.md`, `plans/night142-walk1-read.md` (landed 05:51 local, during the run), `plans/night142-batch2-read.md` (08:58 local).
- read landed: 2026-10-12 07:50 UTC (f50dafab). Run end: 2026-10-12 07:41 UTC. Gap: 0:09
- 2: "**Frames 209 and 210 validate at a2b70a84** on that tally; night 142 is their walk." (frames 209 and 210, status 2026-10-12 03:00, rota-cd).
- 3: status lines of frames 209 and 210, `plans/archive/stack-2026-10-12.md`.
- 4: 6 walls.
  - n142-W1: `batch_2` loops to exhaustion, challenge cap refuses the fix of `tst_2` [C?] (source: `plans/night142-batch2-read.md`:191)
  - n142-W2: a cancelled batch's broken test stays on every page [C?] (source: frame 213, from the walk 1 read)
  - n142-W3: Liaison copies the converse brief's example ask word for word [C?] (source: frame 214, from the walk 1 read)
  - n142-W4: criterion repair takes the first row of an unhinted callable list [C?] (source: frame 215, `plans/night142-read.md` section 2)
  - n142-W5: criterion repair pre-run shows no expected files [C?] (source: frame 217)
  - n142-W6: the cancel abandons a batch on a contest of its item [C?] (source: `plans/night142-read.md`:210)
- 5: commit 6cc81151 "batch_2's read finds the challenge cap closed the path on a changed test", 8 min after the read.
- 6: 213: still open at night 143. 214: still open. 215: built before night 143 (status 11:30). 217: not sure (no status line parsed).
- 8: n142-W1: not found in 143 to 145. n142-W2: 143: not found. met in n144 as n144-W3 (frame 213 status "3 of 3 principal answers about a challenged test's content reached no Tester"): same cause. met in n145 (frame 213 status "8 of 8"): same cause. n142-W3: 144: not sure (frame 214 status, walk 2's `brief.segment`). n142-W4: 144: not sure (frame 215 status "the respecify door never fired"). n142-W5: not found. n142-W6: 143: not sure (n143-W3).
- 9: the session: "batch_2's read finds the challenge cap closed the path on a changed test" (commit 6cc81151). Decided: continued.
- 11: rota-cd, rota-21, rota-6d (frames 213 to 217).
- 12: named: ab_after_giveup yes (":210 cancel then abandoned it on a contest of its item"). gaveup_nothing yes (":11 `batch_2` reached exhaustion, attempt 10 of 10").

### night 143
- read pages: `plans/night143-read.md`
- read landed: 2026-10-12 15:25 UTC (59a91766). Run end: 2026-10-12 15:06 UTC. Gap: 0:19
- 2: "**Pass 1 validates at c9e915c5**, and night 143 is its walk with frame 200 and frame 215." (frame 204, status 2026-10-12 11:30, rota-6d).
- 3: frame 204's status line, `plans/stack.md` (frame 204).
- 4: 4 walls (title and candidates).
  - n143-W1: bg_6 stops at attempt 1 on an inherited test its Developer broke [C?] (source: :1)
  - n143-W2: fence's baseline is the working file, a restore is refused [C?] (source: :562)
  - n143-W3: Vision Keeper's `problem.assert` under a live item's id rewrites the request [C?] (source: :574)
  - n143-W4: NameError door's import hint names a surface import that does not bind [C?] (source: :585)
- 5: commit b50116f5 "frame 204's passes 1g and 1h validate at 78b9b705 on the re-record gate", 13 min after the read.
- 6: 219: not sure (2 status lines). 220: still open at night 144. 221: still open. 222: still open.
- 8: n143-W1: not found in 144 to 146. n143-W2: not found in 144 to 146 (frame 220 status). n143-W3: met in n144 (frame 221 status "1 more, Vision Keeper s478"): same cause. 145: not sure (frame 221 status "0 asserts ... candidate G folds in"). 146: not sure. n143-W4: met in n144 (frame 222 status "1 of 2 calls"): same cause. 145, 146: not found.
- 9: the session: "night 143's read lands, frames 210 and 209 close, frames 220 to 222 are [pushed]" (commit 59a91766). Decided: continued.
- 11: rota-b1 (frames 219 to 222).
- 12: named: ab_after_giveup yes (":27 bg_1 `echo_json`, abandoned before a build"). ab_contest_plan yes (":56 the cancel then abandons").

### night 144
- read pages: `plans/night144-read.md`; sub-read `plans/frame204-history-read.md` (2026-10-13 06:53 local).
- read landed: 2026-10-13 04:47 UTC (75b5c2e2). Run end: 2026-10-13 04:25 UTC. Gap: 0:22
- 2: "Judged here: night 144 does not launch, because the measure pair is red on the Tester side" (frame 200, status 2026-10-12 22:44, rota-b1), then "the commit, the launcher's SHA and night 144's launch follow its five lines" (frame 200, status 22:55, rota-2f).
- 3: frame 200's status lines, `plans/archive/stack-2026-10-13.md`.
- 4: 5 walls (title and candidates A to D).
  - n144-W1: criterion repair rewrites a criterion he just corrected, back (A) [C?] (source: :620)
  - n144-W2: relay of his correction lands `unchanged`, the note does not say so (B) [C?] (source: :635)
  - n144-W3: his answer about a challenged test's content reaches no Tester (C) [C?] (source: :645)
  - n144-W4: one-challenge-per-session door ends the wake, a second red test waits (D) [C?] (source: :655)
  - n144-W5: the measure batch builds the wrong flag [C?] (source: :1)
- 5: commit f6748446 "sprint 2's order is taken by timeout at 06:07", 21 min after the read.
- 6: 225 (a cycle read of night 144): built before night 145 (status 00:51). 226: built before night 145 (status 06:43). 227: still open at night 145 (closed on night 145's read).
- 8: n144-W1: 145: not met (frame 226 status "0 of 2 repairs restored contested words"). 146: not met. 147: not found. n144-W2: 145: not met (frame 227 "0 of 14"). n144-W3: met in n145 (frame 213 status "8 of 8"): same cause. 146, 147: not found. n144-W4: not found. n144-W5: 145: not sure (title "the measure batch is green twice and never reaches the Critic").
- 9: Roman: "regarding the next night, its expencive but debuging and so debug planing is relativeley intuative as long as it doesent open large questions" (10-12 22:50 UTC, row 4). The session took sprint 2 "by timeout" (commit f6748446). Decided: continued.
- 11: rota-0a, rota-ea (frames 225 to 227); session 31e55586 (row 4).
- 12: named: ab_after_giveup yes (":27 bg_1 `echo_json`, abandoned before a build"). ab_contest_plan not sure (":698" is a frame table row). gaveup_red yes (":605 Walk 2's summary says "The team gave up""). Not named: ab_amended.

### night 145
- read pages: `plans/night145-read.md`; sub-read `plans/day-read-2026-10-13.md` (landed 2026-10-13 11:33 local, during the run).
- read landed: 2026-10-13 14:11 UTC (17e67ca3). Run end: 2026-10-13 13:48 UTC. Gap: 0:23
- 2: "Night 145 is the walk: repairs that restore contested words after a principal correction, from 1 of 1 on night 1[44]" (frame 226, status 2026-10-13 08:07, rota-0a).
- 3: frame 226's status line, `plans/archive/stack-2026-10-14.md`.
- 4: 5 walls (title and candidates E to H).
  - n145-W1: measure batch green twice, never reaches the Critic, one criterion untested [C?] (source: :1)
  - n145-W2: respecify door judges the text alone, a surface repair is refused (E) [C?] (source: :498)
  - n145-W3: import-cycle door names `from .core import ...` for any name (F) [C?] (source: :515)
  - n145-W4: Vision Keeper's assert on a challenge creates a new request (G) [C?] (source: :526)
  - n145-W5: encode door admits `runner.invoke(lambda: ...)` (H) [C?] (source: :534)
- 5: commit 23c2aa7c "sprint 3 is taken by timeout, and frame 226's pass 1c starts", 20 min after the read.
- 6: 228: built before night 146 (status 17:53). 229: built (17:53). 230: still open. 232: built (21:32). 233: still open.
- 8: n145-W1: 147: not sure (n147-W2, `tests_missing`). n145-W2: 146: not sure (n146-W3). n145-W3: 146, 147, 148: not met (frame 229 status "0 cycle-door refusals"). n145-W4: 146: not sure (frame 221 status). n145-W5: 146, 147: not found. met in n148 (frame 230 status "s154's bodies with `runner.invoke(lambda: confirm(...))`"): same cause.
- 9: Roman: "ok im not confident about the approach, the goal is reduce iteration cost by reusing previous nights, / Please do a complete investigation of possibilities" (10-13 17:50 UTC, row 5), then "Just investigate how to reuse, all the time is spent on the card generating tokens. Investigate with fable" (18:03, row 6). Also "stop all gpu work" (22:38 UTC). Decided: turned (frame 231, the reuse investigation).
- 11: rota-ff, rota-84 (frames 228 to 233); session e669185f (rows 5, 6).
- 12: named: gaveup_nothing yes (":204 `exhausted attempt 10 of 10`"). gaveup_red not sure (the same line).

### night 146
- read pages: `plans/night146-read.md`; sub-read `plans/frame225-history-read.md` (2026-10-14 10:59 local).
- read landed: 2026-10-14 06:21 UTC (5ff33401). Run end: 2026-10-14 06:00 UTC. Gap: 0:21
- 2: "Judged here: the frame validates at 56bfe7c5 with the four lows carried to night 146's read" (frame 232, status 2026-10-13 21:59, rota-84). Frame 213: "Then the frame validates and night 146 counts it" (20:32).
- 3: status lines of frames 232 and 213, `plans/archive/stack-2026-10-14.md`.
- 4: 6 walls (title and candidates A to E).
  - n146-W1: frame 234's verdict over-contest cancels 4 of 8 batches [C?] (source: :1)
  - n146-W2: client connects to `localhost`, waits 2.04 s for IPv6 (A) [C?] (source: :612)
  - n146-W3: respecify door lands a surface move to a comparison callable (B) [C?] (source: :620)
  - n146-W4: touch judge judges the item's own file a mistake (C) [C?] (source: :628)
  - n146-W5: fold contests an approved item through a `default` note (D) [C?] (source: :634)
  - n146-W6: exhaustion `propose` becomes an item about streaming (E) [C?] (source: :638)
- 5: commit 0d73891d "sprint 4's order is taken by timeout, frame 189 closes", 22 min after the read.
- 6: 234: built before night 147 (status 11:30). 235: built (08:07). 236: still open.
- 8: n146-W1: met in n147 as n147-W1 (title "a chain that starts at the verdict's over-contest"): not sure. 148: not met (frame 234 status "0 of 3 batches cancelled"). n146-W2: 147: not met (frame 235 closed on its median). n146-W3: not found. n146-W4: 147, 148, 149: not met (frame 236 "0 of 0 `touch_mistaken` wakes"). n146-W5: 147: not sure (frame 225 status names night 146's 2 of 2 as the base). n146-W6: not found.
- 9: the session: "sprint 4's order is taken by timeout" (commit 0d73891d). Decided: continued.
- 11: rota-cd, rota-f7 (frames 234 to 236); session 58da19ca (frame 225 history read head).
- 12: named: ab_after_giveup not sure (":64" is a frame table row). ab_contest_plan yes (":1 frame 234's verdict over-contest cancels 4 of 8 batches"). ab_contest_work yes (same line). gaveup_red not sure (":124" is a quote of a seat).

### night 147
- read pages: `plans/night147-read.md`
- read landed: 2026-10-14 16:51 UTC (c3fe66f4). Run end: 2026-10-14 16:33 UTC. Gap: 0:18
- 2: "**Validating at 5e2f0e57** on night 147, pending that review: batches abandoned after a seat's assert on their item, from 2 of 3 on night 143 and 2 on night 146" (frame 221, status 2026-10-14 14:47, rota-f7).
- 3: frame 221's status line, `plans/archive/stack-2026-10-14.md`.
- 4: 7 walls (title and candidates A to F).
  - n147-W1: bg_2 dies on a chain from the verdict's over-contest of Critic notes [C?] (source: :1)
  - n147-W2: re-dispatched batch merges with no test, `tests_missing` counts the old batch (A) [C?] (source: :579)
  - n147-W3: verdict contests a line the words never name (B) [C?] (source: :593)
  - n147-W4: notes of no request reach a request's page (C) [C?] (source: :599)
  - n147-W5: a quarantined tick outlives the approve of its item (D) [C?] (source: :604)
  - n147-W6: merged change carries code he declined (E) [C?] (source: :610)
  - n147-W7: Tester cannot test `confirm` on EOF through `CliRunner` (F) [C?] (source: :617)
- 5: commit 9624565c "sprint 5 is ruled, frame 198 closes, and frame 238's pass 1 starts", 7 min after the read.
- 6: 237: built before night 148 (status 20:27). 238: built (18:34). 239: built (18:48). 240: built (23:39). 241: still open.
- 8: n147-W1: 148: not met (frame 234 "0 of 3"). n147-W2: 149, 150: not met (frame 239 "0 of 0 re-dispatched batches"). n147-W3: 149: not sure (n149-W9). 150: not sure (n150-W1). n147-W4: 148: not found. met in n149 (frame 241 status "2 pages"): same cause. met in n150 (frame 241 "2 agenda pages"): same cause. n147-W5: 148: not met (frame 240 "0 of 3"). n147-W6: met in n148 as n148-W1 ("Candidate E, again"): same cause. met in n149 as n149-W6: same cause. met in n150 as n150-W11: same cause. n147-W7: met in n148 as candidate "F, again" (`plans/night148-read.md`:497): same sign at the same place. 149: not sure (n149-W5, frame 254).
- 9: the session, with Roman by record: "sprint 5 is ruled, frame 198 closes" (commit 9624565c). Decided: continued.
- 11: rota-7e, rota-92 (frames 237 to 241).
- 12: named: ab_amended not sure (":53" is about `glossary.amend`).

### night 148
- read pages: `plans/night148-read.md`
- read landed: 2026-10-15 00:16 UTC (909f37ed). Run end: 2026-10-14 23:55 UTC. Gap: 0:21
- 2: "**Frames 187 and 219 validate at 92c4f126** on night 148: Vision Keeper sessions per contested observed item with every call refused, from 3 of 3 on night 147 to at most 1 in 3" (frames 187 and 219, status 2026-10-15 00:03, rota-92).
- 3: status lines of frames 187 and 219, `plans/archive/stack-2026-10-15.md`.
- 4: 8 walls (title and candidates G to N).
  - n148-W1: bg_3 merges the version message he declined twice (H) [C?] (source: :1, :471)
  - n148-W2: blindspot note puts a raw tick key on his page (G) [C?] (source: :467)
  - n148-W3: re-annotate after a files contest keeps the declined files (I) [C?] (source: :476)
  - n148-W4: `glossary.lookup` matches the term's case (J) [C?] (source: :483)
  - n148-W5: Developer logs the kind door's three questions as three notes (L) [C?] (source: :487)
  - n148-W6: a criterion ruling relayed ends in `glossary.adopt` on a criterion id (M) [C?] (source: :490)
  - n148-W7: `tick:unresolved` escalates a challenge after its test went green (N) [C?] (source: :494)
  - n148-W8: 2 of 3 bg_2 tests assert the exit code, not the value (F again) [C?] (source: :497)
- 5: commit 13d8f226 "Roman rules sprint 6's order, frame 243's scope read first", 5 min after the read.
- 6: 243: built before night 149 (status 02:26). 244: built (14:27). 245: built (13:18). 246: not sure (5 status lines). 247: still open. 248: still open. 249: still open. 250: still open.
- 8: n148-W1: met in n149 as n149-W6: same cause. met in n150 as n150-W11: same cause. met in n151 as n151-W13: same cause. n148-W2: 150, 151: not met (frame 246 "0 of 1 fact pages"). n148-W3: met in n150 (frame 244 status "night 150 shows the wall again"): same cause. 151: not met (frame 244 "0 of 2"). n148-W4: met in n149 (frame 247 status "walk 1's 4 fault rows are this frame's case"): same cause. n148-W5: not found. n148-W6: not found in 149 to 151. n148-W7: 150, 151: not met (frame 245 "0 of 1", "0 of 3"). n148-W8: not sure.
- 9: Roman: "right but capability wise" (10-14 23:07 UTC, row 7), "I want to prevent over fitting" (00:54, row 8), "But anyways, this wall ladder is not sound." (01:19, row 9), "Ok so the ladder needs design and review passes itself" (01:21). Decided: turned (frame 251, the wall guide).
- 11: rota-0c, rota-4f (frames 243 to 250); sessions 4a757f92, 4754aaec, dae006d1 (rows 7 to 11).
- 12: runs.tsv classes: none.

### night 149
- read pages: `plans/night149-read.md`
- read landed: 2026-10-15 15:24 UTC (7d4450cd). Run end: 2026-10-15 15:00 UTC. Gap: 0:24
- 2: "Frame 245 validates at f6e03017 on night 149**: unresolved wakes on a green test, from 1 chain toward 0 of the next 3" (frame 245, status 2026-10-15 14:27, rota-4f). Frame 244: "re-annotates that keep a declined file, from 2 of 2 toward 0 of the next 3" (14:32).
- 3: status lines of frames 244 and 245, `plans/archive/stack-2026-10-16.md`.
- 4: 11 walls, placed by the read.
  - n149-W1: bg_2 cancelled by s232's assert, frame 129's case [C8] (W1) (source: :501)
  - n149-W2: files correction after the head commit lands nowhere [C1] (W2) (source: :519)
  - n149-W3: "through" not read as a range [C8] (W3) (source: :536)
  - n149-W4: the approve of faulted lines [C1] (W4) (source: :546)
  - n149-W5: frame 254, the stdin door [C8] (W5) (source: :559)
  - n149-W6: frame 243's seam on walks 2 and 3 [C5] (W6) (source: :563)
  - n149-W7: one criterion id written four times [C8] (W7) (source: :577)
  - n149-W8: the gap note in words [C11] (W8) (source: :585)
  - n149-W9: the contest of an agreed line [C8] (W9) (source: :596)
  - n149-W10: four Developer wakes cut behind the block [C2] (W10) (source: :604)
  - n149-W11: frame 222's hints, 1 of 6 right [C9] (W11) (source: :613)
- 5: commit 5518ef67 "frame 246's review 1b accepts with two lows", 0 min after the read.
- 6: 254 (night 149 cycle read): built before night 150 (status 01:43). 255: built (21:26). 256: built (22:39). 257: still open. 258: still open. 259: still open.
- 8: n149-W1: 150: not sure (n150-W2). n149-W2: 150: not sure (frame 255 status). 151, 152: not met ("0 of 0"). n149-W3: 150, 151, 152: not met (frame 256 "read whole"). n149-W4: 150: not sure (n150-W6). n149-W5: 150: not met (no Tester session). 151: not met ("0 of 1 right bodies refused"). 152: not met. n149-W6: met in n150 as n150-W11: same cause. met in n151 as n151-W13: same cause. 152: not found. n149-W7: 150: not sure (frame 257, "the reverse shape"). 151: not found. met in n152 (frame 257 "s271 specified `ver_opt_show_py` 18 times"): same cause. n149-W8: 150: not sure (n150-W10, frame 259). n149-W9: met in n150 as n150-W1 (frame 258 "6 signs, the night's root wall: m25"): same cause. met in n151 as n151-W1: same cause. met in n152 (frame 258 status): same cause. n149-W10: not found. n149-W11: met in n151 as n151-W11: same cause. 152: not sure.
- 9: the session: "night 149's read closes frames 202, 187 and 236, pushes frames 255 to 259, and proposes spri[nt 7]" (commit 7d4450cd), then "sprint 7 is taken by timeout" (43b78a8a, 16:46). Decided: continued.
- 11: rota-3e, rota-c8 (frames 254 to 259); hand-off to session 4492a9c1 (commit 451aef87, 18:56).
- 12: Not named: ab_amended (no keyword hit).

### night 150
- read pages: `plans/night150-read.md`; sub-read `plans/frame264-reads.md` (2026-10-16 07:29 local).
- read landed: 2026-10-16 10:00 UTC (68db0dee). Run end: 2026-10-16 05:00 UTC. Gap: 5:00
- 2: "**Pass 1b committed at d3154135. Frame 250's present route validates at d3154135 on night 150.**" (frame 250, status 2026-10-16 02:35, rota-c8).
- 3: frame 250's status line, `plans/stack.md` (frame 250).
- 4: 11 walls, placed by the read.
  - n150-W1: m25's "ok ... build it with json" makes a request item [C1] (W1) (source: :484)
  - n150-W2: s112 asserts a new item `json_only` in a contested wake [C8] (W2) (source: :494)
  - n150-W3: the signoff loop [C8] (W3, N1) (source: :501)
  - n150-W4: the made-up surface `import_json` [C8] (W4, N2) (source: :511)
  - n150-W5: the words door's repair text [C9] (W5, N3) (source: :518)
  - n150-W6: frame 250's approve refusal on "not as a separate change" [C8] (W6) (source: :526)
  - n150-W7: the account rows contested [C11] (W7, N4) (source: :531)
  - n150-W8: "Now." lands as a park [C1] (W8, N5) (source: :538)
  - n150-W9: the park does not reach the sibling item [C6] (W9, N6) (source: :544)
  - n150-W10: the Terminologist's fault rows, frame 259 [C8] (W10) (source: :550)
  - n150-W11: respecify keeps the contested text, frame 243 [C4] (W11) (source: :556)
- 5: commit db7c950d "fix(api): a signoff submit that leaves out the draft that woke it is refused", 0 min after the read.
- 6: 261: built before night 151 (status 11:01). 262: still open. 263: still open. 264: not sure (4 status lines, waits on Roman's word). 265: still open.
- 8: n150-W1: met in n151 as n151-W1: same cause. n150-W2: not sure. n150-W3: 152: not met (frame 261 "0 of 6 signoff submits"). n150-W4: 151, 152, 153: not met (frame 262 "0 of 0"). n150-W5: 152: not sure (frame 263 "wrong for another cause"). 153: not sure (n153-W13). n150-W6: met in n151 as n151-W3 and n151-W4: same cause. met in n152 as n152-W11: same cause. met in n153 as n153-W15: same cause. n150-W7: 151, 152, 153: not met (frame 264 "0 contests"). n150-W8: 151 to 153: not met (no shift page). n150-W9: not found. n150-W10: met in n152 (frame 259 "4 fault rows"): same cause. met in n153 as n153-W16: same cause. n150-W11: met in n151 as n151-W13: same cause.
- 9: the session: "frame 261's pass 1 commits at db7c950d and its review starts" (commit c618c215). "Frame 264 waits on Roman's word, not re-asked" (frame 243, status 2026-10-16 13:33). Decided: continued.
- 11: rota-d0 (frames 261 to 265); rota-05 (frame 243).
- 12: named: ab_after_giveup yes (":29 `json_only` ... abandoned after m37"). ab_contest_plan yes (":166 6 contests | batch_2 abandoned").

### night 151
- read pages: `plans/night151-read.md`
- read landed: 2026-10-16 16:36 UTC (134e8806). Run end: 2026-10-16 16:14 UTC. Gap: 0:22
- 2: "**Pass 1b committed at 8194e3a0. Frame 258 validates at 8194e3a0 on night 151.**" (frame 258, status 2026-10-16 13:32, rota-d0).
- 3: frame 258's status line, `plans/archive/stack-2026-10-24.md`; sprint 8, `plans/stack.md`:1440.
- 4: 15 walls, placed by the read.
  - n151-W1: frame 258's "ok" contest (m23) [C8] (W1) (source: :555)
  - n151-W2: frame 258's line-1 contest on "Please don't drop" [C8] (W2) (source: :562)
  - n151-W3: frame 250's present fire on m46 [C?] (W3) (source: :568)
  - n151-W4: frame 250's clarify misses, m98 and m143 [C8] (W4) (source: :572)
  - n151-W5: the parser blames the words [C9] (W5, N1) (source: :577)
  - n151-W6: a consumed reply with no ruling [C14] (W6, N3) (source: :585)
  - n151-W7: the relay's approval write outside its refs [C8] (W7, N4) (source: :594)
  - n151-W8: the plain-string decorator body [C8] (W8, N5) (source: :600)
  - n151-W9: the whole-file write of `__init__.py` [C8] (W9, N6) (source: :605)
  - n151-W10: the asked-for file left out [C1] (W10, N7) (source: :611)
  - n151-W11: frame 222's `import cmd` [C9] (W11) (source: :617)
  - n151-W12: frame 260's refusal text [C9] (W12) (source: :623)
  - n151-W13: frame 243's cr_1 never respecified [C?] (W13) (source: :627)
  - n151-W14: bg_4 quarantined after "don't drop" [C?] (W14) (source: :634)
  - n151-W15: frame 241's notes on another request's page [C?] (W15) (source: :641)
- 5: commit ff109084 "night 151's boundary closes frames 245, 246 and 230, pushes frames 266 to 271", 0 min after the read.
- 6: 266: built before night 152 (status 19:05). 267: built (19:50). 268: still open. 269: still open. 270: still open. 271: still open.
- 8: n151-W1: met in n152 (frame 258 status): same cause. n151-W2: met in n152 (frame 258 status): same cause. n151-W3: met in n152 as n152-W11: same cause. n151-W4: met in n152 as n152-W11: same cause. met in n153 as n153-W15: same cause. n151-W5: met in n152 as n152-W7: same cause. met in n153 as n153-W4: same cause. met in n154 as n154-W7: same cause. n151-W6: 153: not met ("0 of 27"). met in n154 as n154-W11 ("1 of 30, m176"): same cause. n151-W7: 152: not sure (n152-W3, frame 268's sign with another cause). n151-W8: 152: not met ("0 bodies"). n151-W9: 152: not met ("0 whole-file writes"). n151-W10: met in n152 as n152-W13 ("frame 271, 2 of 2"): same cause. n151-W11: 152: not sure. n151-W12: met in n152 as n152-W12: same cause. met in n154 as n154-W9: same cause. n151-W13: 153: not sure (section 5 reads frame 243). n151-W14: not found. n151-W15: met in n153 as n153-W2: same cause.
- 9: Roman, by the session's record: "Roman rules sprint 9's order and the next night on frame 258's pass 2" (commit 0213c1db, 17:40). Decided: continued.
- 11: rota-e7 (frames 266 to 271).
- 12: named: ab_after_giveup yes (":29 bg_1 ... abandoned after m45"). Not named: gaveup_nothing.

### night 152
- read pages: `plans/night152-read.md`
- read landed: 2026-10-16 21:30 UTC (2eed4e0a). Run end: 2026-10-16 21:04 UTC. Gap: 0:26
- 2: "Waits on the gate from `C:/Users/roman/rota_gate_267c` alone, then night 152 launches from 98b7b562." (frame 267, status 2026-10-16 20:29, rota-e7). No measure in the line. Sprint 9 holds the night's frames (`plans/stack.md`:1393).
- 3: frame 267's status line; sprint 9, `plans/stack.md`:1393.
- 4: 13 walls, placed by the read.
  - n152-W1: line numbers from `recent_chat` [C4] (W1, N1) (source: :653)
  - n152-W2: the vacuous test [C8] (W2, N2) (source: :668)
  - n152-W3: the inferred carrier [C6] (W3, N3) (source: :675)
  - n152-W4: the words door on "using" [C?] (W4, N4) (source: :685)
  - n152-W5: the quarantine page [C11] (W5, N6) (source: :691)
  - n152-W6: the Critic's two-quote close, cycle 1 [C9] (W6) (source: :698)
  - n152-W7: s290's write with no closing bracket [C9] (W7) (source: :701)
  - n152-W8: bg_3 merged with no behaviour [C8] (W8) (source: :708)
  - n152-W9: frame 253, the quarantine wake with no refs [C?] (W9) (source: :719)
  - n152-W10: m73 taken in as a new request [C?] (W10) (source: :725)
  - n152-W11: m75 approved on the confirm route [C8] (W11) (source: :729)
  - n152-W12: frame 260's refusal text [C9] (W12) (source: :734)
  - n152-W13: frame 271, 2 of 2 [C1] (W13) (source: :738)
- 5: commit 277fd100 "a sprint order never pauses the session, ruled by Roman on 2026-10-16 22:33", 4 min after the read.
- 6: 272: still open at night 153. 273: built before night 153 (status 01:09). 274: built (23:38). 275: still open. 276: still open.
- 8: n152-W1: met in n153 as n153-W14: same cause. 154: not found. met in n155 as row 10 ("Frame 272"): same cause. n152-W2: met in n153 as n153-W3: same cause. 154: not met (frame 273 "0 fires"). n152-W3: met in n153 as n153-W1: same cause. 155: not met ("not frame 274's carrier", `plans/night155-read.md`:12). n152-W4: met in n153 as n153-W13: same cause. n152-W5: not found. n152-W6: 153: not sure (n153-W5). n152-W7: met in n153 as n153-W4: same cause. n152-W8: not found. n152-W9: not found. n152-W10: met in n155 as row 1 ("Frame 214"): same cause. n152-W11: met in n153 as n153-W15: same cause. met in n155 as row 5: same cause. n152-W12: met in n154 as n154-W9: same cause. n152-W13: 155: not sure (row 3, "Frame 196's sign ... or frame 271's").
- 9: Roman: "Stop pausing for sprint orders, I will re prioritise if something changes" (10-16 21:32 UTC, row 12). Decided: continued (the rule went into CLAUDE.md, commit 277fd100).
- 11: rota-ea, rota-3a (frames 272 to 276); session 04be1489 (row 12).
- 12: runs.tsv classes: none.

### night 153
- read pages: `plans/night153-read.md`; sub-read `plans/frame278-route-read.md` (2026-10-17 04:46 local).
- read landed: 2026-10-17 03:31 UTC (459f37ef). Run end: 2026-10-17 03:01 UTC. Gap: 0:30
- 2: "Waits on the gate from `C:/Users/roman/rota_gate_266d` alone, then night 153 launches." (frame 266, status 2026-10-17 02:03, rota-3a). No measure in the line.
- 3: frame 266's status line; sprint 10, `plans/stack.md`:1333.
- 4: 19 walls, placed by the read.
  - n153-W1: the carrier's skip lets criteria of another request through [C6] (W1) (source: :682)
  - n153-W2: another request's notes on the page, frame 241 [C11] (W2) (source: :689)
  - n153-W3: the non-constant tautology [C8] (W3, N2) (source: :692)
  - n153-W4: CYCLE 1's dict value, frame 266 [C9] (W4) (source: :699)
  - n153-W5: the escaped quote, frame 266 [C9] (W5) (source: :704)
  - n153-W6: the Tester's body with no working value, frame 223 [C3] (W6) (source: :706)
  - n153-W7: the commit beside a noted write, frame 140 [C8] (W7) (source: :713)
  - n153-W8: span door's offer leads to a removal, frame 173 [C9] (W8) (source: :717)
  - n153-W9: the output budget cuts, frame 47 [C4] (W9) (source: :721)
  - n153-W10: the Architect's decision goes to the Developer only [C10] (W10, N3) (source: :725)
  - n153-W11: "compact" lost at the criteria hop [C1] (W11, N4) (source: :730)
  - n153-W12: the decision id overwrite [C6] (W12, N1) (source: :736)
  - n153-W13: the words door on "using", frame 275 [C8] (W13) (source: :739)
  - n153-W14: line numbers from `recent_chat`, frame 272 [C4] (W14) (source: :741)
  - n153-W15: m81's approve of cr_3, frame 250 [C1] (W15) (source: :744)
  - n153-W16: work notes as faults, frame 259 [C6] (W16) (source: :746)
  - n153-W17: criteria under one id, frame 257 [C8] (W17) (source: :749)
  - n153-W18: `glossary.adopt` on a criterion id, frame 249 [C?] (W18) (source: :751)
  - n153-W19: `assert False` under `except Abort` refused, frame 147 [C8] (W19) (source: :755)
- 5: commit 804bff55 "Roman rules frame 264, the account rows stay on the request page", 2 min after the read.
- 6: 277: built before night 154 (status 12:36). 278: built (11:45). 279: not sure (2 status lines). 280: still open.
- 8: n153-W1: 154: not met (frame 274 "0 items of another request contested"). 155: not met. n153-W2: met in n156 as n156-W6: same cause. n153-W3: 154: not met (frame 277 "0 of 336"). 156: not met. n153-W4: met in n154 as n154-W7: same cause. met in n155 as rows 8 and 11 ("Frame 266"): same cause. n153-W5: met in n154 as n154-W7 ("dict value with escaped words"): same cause. n153-W6: 154: not met (title "frame 223's wall does not recur"). n153-W7: 154: not sure (n154-W2, frame 283). n153-W8: met in n154 as n154-W4: same cause. n153-W9: not found. n153-W10: met in n154 (frame 278 status "1 of 3 relays to the Tester failed"): same cause. n153-W11: not found. n153-W12: met in n154 as n154-W13: same cause. n153-W13: not found. n153-W14: met in n155 as row 10: same cause. met in n156 as n156-W8: same cause. n153-W15: met in n155 as row 5: same cause. n153-W16: not found. n153-W17: not found. n153-W18: met in n155 as row 9 ("Frame 249's sign"): same cause. n153-W19: met in n154 as n154-W6: same cause.
- 9: Roman: "right now the strategy for finding walls is reactive, / is there a proactive approach?" (10-17 11:49 UTC, eefbf293), then "no, not with deterministic checks, / with subagents" (11:50). He also ruled frame 264 (commit 804bff55). Decided: turned.
- 11: rota-29, rota-68, rota-23 (frames 277 to 280); session eefbf293; hand-off note `plans/handoff-b0dce033.md` (frame 274, status 2026-10-17 12:04).
- 12: named: gaveup_nothing not sure (":64 0 `Stuck` lines").

### night 154
- read pages: `plans/night154-read.md`; sub-reads `plans/frame114-history-read.md` (17:04 local), `plans/frame143-pass1b-read.md` (18:04), `plans/frame143-pass1d-read.md` (18:47), all 2026-10-17.
- read landed: 2026-10-17 15:40 UTC (fa2adc59). Run end: 2026-10-17 15:19 UTC. Gap: 0:21
- 2: "The taker's first step is frame 278's gate, then sprint 11's rows 2 to 4, then night 154." (frame 274, status 2026-10-17 12:04, rota-23). No measure in the line.
- 3: frame 274's status line; sprint 11, `plans/stack.md`:1267.
- 4: 13 walls, placed by the read.
  - n154-W1: the push's frame form [C8] (W1, N1) (source: :475)
  - n154-W2: the commit after an `unchanged` rewrite [C8] (W2, N2) (source: :482)
  - n154-W3: the dynamic-import door on a restore, frame 220 [C8] (W3) (source: :489)
  - n154-W4: landed removals with no note, frame 173 [C8] (W4) (source: :492)
  - n154-W5: no restore route [C10] (W5, N3) (source: :495)
  - n154-W6: the constant door on `assert False` under `except` [C8] (W6) (source: :500)
  - n154-W7: the dict value with escaped words, frame 266 [C9] (W7, N5) (source: :503)
  - n154-W8: the step's call lacks `quotes`, frame 278 [C9] (W8, N4) (source: :507)
  - n154-W9: the surface door's text on `src.`, frame 260 [C9] (W9) (source: :510)
  - n154-W10: the line reader, frame 282 [C1] (W10) (source: :514)
  - n154-W11: the reply with no ruling, frame 267 [C?] (W11) (source: :518)
  - n154-W12: the Tester's `"y"`, frame 143 [C?] (W12) (source: :520)
  - n154-W13: the decision id overwrite, frame 280 [C6] (W13) (source: :524)
- 5: commit fbc508e6 "frame 283 is claimed by session 0e37e9d7 and its pass 1 runs on Opus", 1 min after the read.
- 6: 281: not sure (2 status lines). 282: built before night 155 (status 18:47 "review 2 of 42a4449e"). 283: built (17:33). 284: still open. 285: still open. 286 (sub-read): built (status 00:15 on 10-18). 287 (sub-read, the method frame): not sure (handed with the stack at 23:57). 288 (sub-read): still open. 289: not sure (2 lines). 290 (sub-read): not sure (4 lines).
- 8: n154-W1: not found. n154-W2: 155: not met (`plans/night155-read.md`:50, "0 of"). met in n156 as n156-W3 ("Frame 283, right to fire"): same cause. n154-W3: 155 to 157: not met (frame 220 closed "0 of 0 on nights 156, 157"). n154-W4: 156: not sure (n156-W3). n154-W5: 155 to 157: not met (frame 286 "0 of 0"). n154-W6: not found. n154-W7: met in n155 as rows 8 and 11: same cause. n154-W8: not found. n154-W9: met in n156 as n156-W2 ("frame 260 for the import door's prefix"): same cause. n154-W10: 156: not met (frame 282 "0 of 0"). n154-W11: 157: not sure (n157-W7). n154-W12: 156: not sure (n156-W2, "Frame 143 for 3.10.0"). n154-W13: not found.
- 9: Roman: "File writes were always permitted everywhere, just that if there were unexpected changes then the architect is required to sign off. I thought we already discussed this" (10-17 15:50 UTC, row 13), and "ok but wait this is a serious flaw with the meta workflow" (16:34). Decided: turned (frame 287, the method).
- 11: rota-7d, rota-91, rota-c1, rota-08 (frames 281 to 290); sessions 0e37e9d7 and d7c5dc6d.
- 12: named: ab_after_giveup yes (":44 b2 ... abandoned at log line 100"). gaveup_nothing yes (":85 The tick exhausted at attempt 10").

### night 155
- read pages: `plans/night155-read.md`
- read landed: 2026-10-18 01:14 UTC (af844499). Run end: 2026-10-18 01:03 UTC. Gap: 0:11
- 2: "**Validating on night 155**: the mechanism's count, writes refused for the want of a criterion on a named definition" (frame 286, status 2026-10-18 00:35, rota-08).
- 3: frame 286's status line, `plans/archive/stack-2026-10-21.md`.
- 4: 12 walls (the read's table).
  - n155-W1: his answer to a Liaison question lands as a new request [C?] (1) (source: :123)
  - n155-W2: request line contested, the live batch cancelled [C?] (2) (source: :124)
  - n155-W3: his files correction never reaches the touch list [C?] (3) (source: :125)
  - n155-W4: Tester stores a test at a product path [C8] (4) (source: :126)
  - n155-W5: Vision Keeper's contested loop on `echo_json` [C?] (5) (source: :127)
  - n155-W6: criteria name test files as surfaces [C8] (6) (source: :128)
  - n155-W7: cycles 3 and 4, the shift page's line 2 [C?] (7) (source: :129)
  - n155-W8: cycle 1, the Critic's `lines` dict with a quote [C?] (8) (source: :130)
  - n155-W9: cycle 5, Terminologist relay loop on `glossary.adopt` [C?] (9) (source: :131)
  - n155-W10: cycle 2, '2' is not a line, from `recent_chat` [C?] (10) (source: :132)
  - n155-W11: onboarding parse loops, Critic and Architect [C?] (11) (source: :133)
  - n155-W12: `problem.prioritize(priority='high')` refused as a word [C9] (12) (source: :134)
- 5: commit 0d94570f "frame 287's revision 7 is one page in plans/method/design.md", 24 min after the read.
- 6: 291 (night 155 cycle read): still open at night 156. 292: not sure (2 status lines).
- 8: n155-W1: 156: not found. 157: not sure (n157-W2). n155-W2: 156: not sure (n156-W1, a new design frame). 157: not met (`plans/night157-read.md`:15 "The request line killed no batch"). met in n158 as n158-W5 ("Frame 258"): same cause. n155-W3: 157: not sure (n157-W4). n155-W4: not found. n155-W5: 156: not sure (n156-W9). n155-W6: not found. n155-W7: not found. n155-W8: met in n158 as n158-W3 ("value closed its quote", cycle 1, Critic): same sign at the same place. n155-W9: not found. n155-W10: met in n156 as n156-W8: same cause. n155-W11: not found. n155-W12: not found.
- 9: Roman: "i feel like im loosing controll of the workflow" (10-18 00:56 UTC, row 15), "nothing blocks on me for multiple sessions, / so you just work through the backlog" (01:35, row 16), "I just asked for your thoughts on the backlog, I don't like the direction. Let's just keep working" (02:17, row 17). Decided: turned (frame 287's design page), and the triage agent stopped.
- 11: rota-08 (frames 291, 292); sessions bf5baa63 and 21800a2b (rows 15 to 17).
- 12: named: ab_after_giveup yes (":11 All five batches were abandoned"). ab_contest_plan yes (":124 The request line is contested and the live batch is cancelled").

### night 156
- read pages: `plans/night156-read.md`
- read landed: 2026-10-18 06:22 UTC (069990f9). Run end: 2026-10-18 06:04 UTC. Gap: 0:18
- 2: "validating from night 156, night 1 of 3, at db0c781d." (frame 258, status 2026-10-18 05:22, rota-39).
- 3: frame 258's status line; sprint 12, `plans/stack.md`:1202.
- 4: 10 walls (the read's table).
  - n156-W1: a correction of the request line ends the item [C10] (W1) (source: :145)
  - n156-W2: bg_3's `tests_failing` loop, tests hard-code 3.10.0 [C?] (W2) (source: :146)
  - n156-W3: bg_2's batch-start quarantine after a span write dropped `echo(` [C?] (W3) (source: :147)
  - n156-W4: revise-on-note door text names line 1 as the only target [C9] (W4) (source: :148)
  - n156-W5: relay Developer reads an uncommitted write as existing code [C14] (W5) (source: :149)
  - n156-W6: the request page carries the merged request's notes [C?] (W6) (source: :150)
  - n156-W7: a seat repeats a right refusal verbatim, the reply is lost [C?] (W7) (source: :151)
  - n156-W8: on a 1-line page seats rule lines 2 and 3 [C?] (W8) (source: :152)
  - n156-W9: the contested quarantines, part of W1 [C?] (W9) (source: :153)
  - n156-W10: `constraint_zero` quarantine at s1 in onboarding [C?] (W10) (source: :154)
- 5: commit 9c4b5368 "fix(roles): the revise-on-note refusal names the drop first", 254 min after the read.
- 6: 296: not sure (4 status lines). 297: still open at night 157. 298: built before night 157 (status 11:44).
- 8: n156-W1: 157: not met (":15 The request line killed no batch"). 158, 159: not found. n156-W2: 157: not sure (n157-W1). n156-W3: 157: not found. met in n158 as n158-W1 (a), "frame 283's case": same cause. n156-W4: 158: not met (frame 296 "night 3 of 3 at 0"). n156-W5: not found in 157 to 159. n156-W6: not found. n156-W7: 157: not sure (n157-W12). n156-W8: 159: not sure (n159-W3). n156-W9: part of W1. n156-W10: met in n157 as n157-W13: same sign at the same place. met in n158 as n158-W12: same sign at the same place. met in n159 as n159-W10: same sign at the same place.
- 9: Roman: "there is now a rulings table that wasnt there before and its not linked to anything via foreign keys" (10-18 11:48 UTC, 6977407c). Decided: turned (the rulings ledger).
- 11: rota-04, rota-89 (frames 296 to 298); session 6977407c.
- 12: named: ab_after_giveup yes (":19 bg_2 ... abandoned at m125 with no head").

### night 157
- read pages: `plans/night157-read.md`
- read landed: 2026-10-18 18:17 UTC (3d5fe03d). Run end: 2026-10-18 17:55 UTC. Gap: 0:22
- 2: none found. No status line names night 157 between night 156's end and 16:40 local (pre2 search).
- 3: sprint 13, `plans/stack.md`:1141; frame 297's status "night 157 walks frame 298" (frames.json).
- 4: 13 walls (the read's table).
  - n157-W1: bg_1's test loop, `confirm()` rewritten whole [C8] (W1) (source: :195)
  - n157-W2: a textless propose becomes a request row [C15] (W2) (source: :196)
  - n157-W3: bg_2's review, three Critic passes cite a docstring [C5] (W3) (source: :197)
  - n157-W4: guess rewrites reach no page [C12] (W4) (source: :198)
  - n157-W5: guess and annotate name `src/click/options.py`, which does not exist [C8] (W5) (source: :199)
  - n157-W6: a vacuous pass on `--show-python` [C8] (W6) (source: :200)
  - n157-W7: replies that did not reach the team [C?] (W7) (source: :201)
  - n157-W8: agent principal says "I'm on the second one now" [C?] (W8) (source: :202)
  - n157-W9: turns after "Your work for this session is complete" [C?] (W9) (source: :203)
  - n157-W10: window drops and dangling pointers [C?] (W10) (source: :204)
  - n157-W11: made up, 71 turns in 36 sessions [C7] (W11) (source: :205)
  - n157-W12: repeats, 15 wakes [C?] (W12) (source: :206)
  - n157-W13: `constraint_zero` quarantine at s1 [C?] (W13) (source: :207)
- 5: commit 993bdd5b "frame 298, Night 157's read on Opus", 0 min after the read.
- 6: 301: built before night 158 (status 2026-10-21 13:56). 302: not sure (2 status lines). 303: not sure (2 status lines).
- 8: n157-W1: 158: not sure (n158-W2). 159: not sure (n159-W2). n157-W2: met in n159 as n159-W3 ("frame 303's sign"): same cause. n157-W3: 158: not sure (n158-W3). 160: not sure (n160-W1). n157-W4: 158: not met (frame 298 "measure is met"). n157-W5: met in n158 as n158-W6 ("Night 157's W5"): same cause. met in n159 as n159-W5: same cause. n157-W6: not found. n157-W7: 158: not sure (n158-W4). n157-W8: not found. n157-W9: met in n158 as n158-W8, n159 as n159-W9, n160 as n160-W9: same sign at the same place. n157-W10: met in n158 as n158-W9, n159-W9, n160-W9: same sign at the same place. n157-W11: met in n158 as n158-W10, n159-W9, n160-W9: same sign at the same place. n157-W12: met in n158-W11, n159-W9, n160-W9: same sign at the same place. n157-W13: met in n158-W12, n159-W10, n160-W8: same sign at the same place.
- 9: Roman: "The second builder works in a different copy of f the worksite" (10-18 16:23 UTC, c32575f3, during the run). The read: "No item merged. The request line killed no batch, against 2 of 3 on night 156, so frame 298's route held." (:15). Decided: continued.
- 11: rota-00, rota-76 (frames 301 to 303); session c32575f3.
- 12: named: gaveup_nothing yes (":38 "Stuck: bg_1 is parked.""). gaveup_red not sure (no keyword hit; W1 reads bg_1's test loop).

### night 158
- read pages: `plans/night158-read.md`
- read landed: 2026-10-21 15:23 UTC (166e5716). Run end: 2026-10-21 15:02 UTC. Gap: 0:21
- 2: "Validating from night 158 on Critic sessions that end with no verdict after a block refusal, from 3 on night 157 tow[ard]" (frame 201, status 2026-10-21 12:32, rota-00).
- 3: frame 201's status line; sprint 14, `plans/stack.md`:1094.
- 4: 12 walls (the read's table).
  - n158-W1: unasked and contrary code merged, `ctx.exit()` removed [C8] (W1) (source: :202)
  - n158-W2: bg_2's test loop, the arrange step raises [C8] (W2) (source: :203)
  - n158-W3: the Critic's review, a value closes its quote early [C9] (W3) (source: :204)
  - n158-W4: Liaison rules line 2 against his words, "drop" misplaced [C8] (W4) (source: :205)
  - n158-W5: contests on a line no sentence names, frame 258 [C8] (W5) (source: :206)
  - n158-W6: the guess names a path not in `code_index` [C8] (W6) (source: :207)
  - n158-W7: the instruments: M0, M1, M2 and the landed-commit count [C13] (W7) (source: :208)
  - n158-W8: turns after "Your work for this session is complete" [C?] (W8) (source: :209)
  - n158-W9: window drops and dangling pointers [C?] (W9) (source: :210)
  - n158-W10: made up, 67 turns in 33 sessions [C7] (W10) (source: :211)
  - n158-W11: repeats, 12 wakes [C?] (W11) (source: :212)
  - n158-W12: `constraint_zero` quarantine at s1 [C?] (W12) (source: :213)
- 5: commit 7e4564af "frame 283, pass 1 of W1 a runs on a[n implementer]", 2 min after the read.
- 6: 304: not sure (8 status lines). 305: built before night 159 (status 2026-10-23 14:08). 306: not sure (3 lines). 307: not sure (4 lines). 308 (sub-read `plans/frame304-s220-read.md`, 2026-10-23 13:34): not sure (5 lines).
- 8: n158-W1: 159: not met (":20 that merge holds his change and nothing else"). 160: not sure (n160-W2). met in n161 as n161-W8 ("frame 306 holds it"): same cause. n158-W2: met in n159 as n159-W2 ("cause 8 on frame 304's door"): same cause. 161: not sure (n161-W4). n158-W3: 160: not sure (n160-W1). n158-W4: met in n159 as n159-W4 ("frame 305's site"): same cause. met in n160 as n160-W3: same cause. met in n161 as n161-W2: same cause. n158-W5: met in n160 as n160-W3 ("Frame 258's sign"): same cause. met in n161 as n161-W2: same cause. n158-W6: met in n159 as n159-W5: same cause. n158-W7: met in n159 as n159-W7: same cause. n158-W8: met in n159-W9, n160-W9, n161-W9: same sign at the same place. n158-W9: met in n159-W9, n160-W9, n161-W9: same sign at the same place. n158-W10: met in n159-W9, n160-W9: same sign at the same place. n158-W11: met in n159-W9, n160-W9: same sign at the same place. n158-W12: met in n159-W10, n160-W8: same sign at the same place. 161: not found.
- 9: the session: "sprint 15 at night 158's read, two merges with unasked code" (commit 166e5716). Decided: continued.
- 11: rota-45, rota-f9 (frames 304 to 308).
- 12: Not named: gaveup_red (no keyword hit; W2 reads bg_2's test loop, not checked against the class).

### night 159
- read pages: `plans/night159-read.md`
- read landed: 2026-10-23 16:51 UTC (2d4fb5bb). Run end: 2026-10-23 16:36 UTC. Gap: 0:15
- 2: "Judged here: the hold stays for night 159, because no right-pass case regresses and the night measures the wrong passes" (frame 201, status 2026-10-23 15:17, rota-45). Frame 302: "the three commits are reverted on the branch before night 159, so the night measures nothing of this frame" (15:17).
- 3: status lines of frames 201 and 302; sprint 15, `plans/stack.md`:1038.
- 4: 10 walls (the read's table).
  - n159-W1: bg_4's criterion holds his words as pasted text [C1] (W1) (source: :216)
  - n159-W2: bg_2's tests could not pass, the seat that saw why was refused [C8] (W2) (source: :217)
  - n159-W3: a team row became a request, its page fed line numbers [C11] (W3) (source: :218)
  - n159-W4: the line reader's cue set leaks a word per night [C8] (W4) (source: :219)
  - n159-W5: guess and touch rows name grains not in `code_index` [C?] (W5) (source: :220)
  - n159-W6: frames 304 and 283 did not fire, "Not a wall" [C?] (W6) (source: :221)
  - n159-W7: the instruments: M0 and `test_runs` per commit [C13] (W7) (source: :222)
  - n159-W8: the 17 faults, mostly W1 and W2 [C?] (W8) (source: :223)
  - n159-W9: turns after "complete", window drops, made up, repeats [C?] (W9) (source: :224)
  - n159-W10: `constraint_zero` quarantine at s1 [C?] (W10) (source: :225)
- 5: commit cc22ca34 "frame 304, night 159 not met on its own door, pass 2 on the rule", 1 min after the read.
- 6: 309: not sure (8 status lines before night 160).
- 8: n159-W1: met in n160 as n160-W2 ("Cause 1 at the Terminologist hop"): same cause. 161: not sure (n161-W1). 162: not sure (n162-W2). n159-W2: 161: not sure (n161-W4). 162: not sure (n162-W1). n159-W3: 161: not found. met in n162 as row 7 ("a case on frame 303's seam", `plans/night162-read.md`:455): same cause. n159-W4: met in n160 as n160-W3: same cause. met in n161 as n161-W2 and n161-W6: same cause. n159-W5: 160 to 162: not met (frame 302 closed "met on nights 160, 161 and 162"). n159-W6: not a wall. n159-W7: not found. n159-W8: part of W1 and W2. n159-W9: met in n160 as n160-W9: same sign at the same place. met in n161 as n161-W9: same sign at the same place. n159-W10: met in n160 as n160-W8: same sign at the same place.
- 9: the session: "frame 304, night 159 not met on its own door, pass 2 on the rule" (commit cc22ca34). Decided: continued.
- 11: rota-7e (frame 309).
- 12: named: gaveup_nothing yes (":51 walk 3 "Stuck: bg_4 is parked""). ab_contest_plan not sure (":270 touch page"). Not named: gaveup_red (no keyword hit).

### night 160
- read pages: `plans/night160-read.md`
- read landed: 2026-10-24 00:10 UTC (22046fa7). Run end: 2026-10-23 20:44 UTC. Gap: 3:26
- 2: "then the gate, then night 160 from the clean head." (frame 283, status 2026-10-23 19:47, rota-19). No measure in the line. The hand-off note is `plans/method/handoff-b85289fd.md` (frame 283, status 19:46).
- 3: frame 283's status lines; sprint 16, `plans/stack.md`:987.
- 4: 9 walls (the read's table).
  - n160-W1: the Critic's lines check refuses a right pass on both batches [C8] (W1) (source: :271)
  - n160-W2: bg_2's criteria hold his notes about the checks [C1] (W2) (source: :272)
  - n160-W3: a "revise" on line 1 cancelled a request he wanted [C8] (W3) (source: :273)
  - n160-W4: the criterion that held his newline was overwritten [C8] (W4) (source: :274)
  - n160-W5: page after a review with no verdict says the team stopped [C11] (W5) (source: :275)
  - n160-W6: the Developer cannot edit a docstring [C9] (W6) (source: :276)
  - n160-W7: his onboarding m6, "Drop those lines", not carried out [C10] (W7) (source: :277)
  - n160-W8: `constraint_zero` quarantine at onboarding, a fifth night [C?] (W8) (source: :278)
  - n160-W9: turns after "complete", window drops, made up, repeats [C?] (W9) (source: :279)
  - also named: the end of walk 3 is the Ollama runner, "not a wall of rota's" (source: :58).
- 5: commit 96aafbf4 "night 160's verdicts on sixteen frames, frames 309, 297 and 301 closed", 3 min after the read.
- 6: 310 (night 160 cycle read): still open at night 161. 311: not sure (8 status lines). 312: built before night 161 (status 02:35).
- 8: n160-W1: 161: not sure (n161-W3, frame 201's hold). 162: not found. met in n163 (frame 311 status "night 163, walk 1, the frame's first exercised sample: the docstring line"): same cause. n160-W2: 161: not sure (n161-W8). 162: not sure (n162-W4, "a case on frame 306"). met in n163 as n163-W4 ("Cause 1 at the criteria writer. Frame 306"): same cause. n160-W3: met in n161 as n161-W2: same cause. n160-W4: not found in 161 to 163. n160-W5: 161: not sure (n161-W7). met in n163 as n163-W5 ("Frame 312"): same cause. n160-W6: 161: not sure (n161-W6, the span refusal). n160-W7: not found. n160-W8: not found in the 161 to 163 wall lists. n160-W9: met in n161 as n161-W9: same sign at the same place.
- 9: Roman: "Mmm, I don't know, we already have the cockpit to view DBs, I'm just really lost when you talk about certain states like review fails" (10-24 00:40 UTC, row 18), then "Get a subagent ... to investigate this by implement this as an independent companent" (00:48). Decided: turned (frame 314, the chart tool).
- 11: rota-19, rota-17, rota-71 (frames 310 to 312); session 0cdcac52 (row 18); hand-off from b85289fd (frame 283, status 2026-10-23 19:46).
- 12: named: ab_contest_plan not sure (":66 the touch page m147"). gaveup_nothing yes (":35 "Stuck. The team gave up on: review for bg_1""). gaveup_red not sure (the same line).

## What this extract could not find

- Night 134 has no row in `runs.tsv`.
- Nights 129 and 135 have no read page. Frames 187 and 188 cite night 135, and no read page holds that night.
- Frames 200, 217 and 300 have no status line in the form `- Status <date> <time>` that the script reads. Their column 6 cells read "not sure", and frame 300 is left out of turn 144.
- The causes of walls before night 149 are `[C?]`, because those reads predate the wall guide.
- Column 8 rests on the wall lists and the frame status lines this extract read. A wall that returned under a new name with no frame link reads "not found".
- Column 12 rests on a keyword search. It does not check a class against each batch.

## Expected answers formed while reading (not part of the turns)

- From night 155 on, five wall rows repeat each night in the same words: turns after "complete", window drops, made up, repeats, and `constraint_zero`. They match by "same sign at the same place" across every next read, and no frame is built for them in this window.
- From night 149 on, most walls name an open frame, so most matches are "same cause" through that frame. Before night 149, most new walls have no frame link in the next read and read "not found" or "not sure".
- Roman's typed words turn the work in 9 of the turns from night 139 on. The session's own judgements in the other turns all read "continued".
