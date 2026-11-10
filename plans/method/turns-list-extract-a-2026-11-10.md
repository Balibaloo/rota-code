One reader and one pass, group a, nights 82 to 126.

Rota workflow for the seats, meta workflow for the build session. The source of the run line of each block is `runs.tsv` of the lead. All clock times are local (+01:00). `runs.tsv` gives UTC, and this page adds one hour. "Gap" is the read's landing time minus the end of the night. A read's landing time is the first commit that adds the page (`git log --diff-filter=A --follow`). Wall causes come from `plans/wall-guide.md` section 2. A cause marked "(guide: frame N)" comes from the "October frames" list of that cause. Frames before 107 have no placement in the guide, so their walls take a cause only where the read's own words fit the cause heading. "F<n>" is frame n.

Read pages that are not reads of one night: `plans/archive/ten-reds-read-2026-09-24.md` (the gate's ten reds, frame 82) is listed under night 92, because it landed after night 92 ended. `plans/archive/fit-overrun-read-2026-09-25.md` (the register, frame 56) and `plans/archive/night88-cut-read-2026-09-25.md` (batch B) are listed under night 88. `plans/frame113-read.md` (a cause read over nights 93 to 106) is listed under night 116. `plans/frame114-read.md` (a cause read over nights 107 to 113) and `plans/frame123-read.md` (nights 115 to 117) are listed under night 117. `plans/archive/night70-vs-night86-2026-09-23.md` is listed under night 86. Night 70 is out of scope.

Thin blocks whose night has a read in a stack status line and no read page: nights 87, 89, 90, 91, 99, 100, 101 and 102 (commits `b89f5473`, `4979834a`, `557b29c4`, `c9adc635`, `2792e073`, `2d39309b`, `0d159868`, `dfa0a104`). This page does not fill their cells from those lines.

### night 82
- run: start 2026-09-16 00:42, commit d4bf6796 by date (runs.tsv line 2)
- read pages: none
- 2 to 6, 9, 11: no read
- 8: no walls named (no read)
- 12: stop classes gaveup_nothing 1. Not named: gaveup_nothing (no read)

### night 83
- run: start 2026-09-17 16:19, commit 3ab5c73c by date (runs.tsv line 3)
- read pages: none
- 2 to 6, 9, 11: no read
- 8: no walls named (no read)
- 12: stop classes none

### night 84
- run: start 2026-09-17 18:19, commit 7e53796e by date (runs.tsv line 4)
- read pages: none
- 2 to 6, 9, 11: no read
- 8: no walls named (no read)
- 12: stop classes none

### night 85
- run: start 2026-09-18 02:16, commit 68950003 by date (runs.tsv line 5)
- read pages: `plans/archive/night85-2026-09-18.md`
- read landed: 2026-09-18 02:59 (a364c020). Run end: 02:55 (night85-2026-09-18.md:4, "between 02:16 and 02:55"). Gap: 0:04
- 2: "frame 34, the cards in work mode and night 85 launched beside the diff review" (commit 779984ad, 2026-09-18 02:17)
- 3: frames 33, 34 and 35 in the stack (`plans/archive/stack-2026-09-18.md` lines 6 and 314, `plans/archive/stack-2026-09-16.md`), claimed by 75d12c2b (commit 406832e3, 02:14)
- 4: 1 wall.
  - n85-W1: Liaison present m27, 64k characters against a 12288 window, no seat answers [C2] (source: night85-2026-09-18.md:30-55)
- 5: commit ab5704bf "the ollama overflow rule corrected, and frame 36's cause measured", 14 min after the read. First fix a268266b at 03:23, 24 min (git log)
- 6: F36 (pushed in a364c020): built before night 86, closed on night 86 (commits e390c6c3 06:08, 0653baf4 07:30, f9b09119 07:48)
- 8: n85-W1: not met in n86 ("No present stayed open", night86-2026-09-18.md:16). n87: no read. Not met in n88 ("No prompt exceeds the half-window budget", night88-cut-read-2026-09-25.md:333)
- 9: the session: "The order of the walls changes. Frames 33, 34 and 35 are all below this one on the delivery path" (night85-2026-09-18.md:188-190). Decided: turned
- 11: 75d12c2b holds frames 33, 34, 35 (406832e3). No hand-off inside the turn (git log)
- 12: stop classes none

### night 86
- run: start 2026-09-18 06:08, commit 8b15af89 by date (runs.tsv line 6)
- read pages: `plans/archive/night86-2026-09-18.md`; `plans/archive/night70-vs-night86-2026-09-23.md` (frame 38, landed after nights 87 to 90)
- read landed: 2026-09-18 07:30 (0653baf4). Second read 2026-09-23 12:58 (9193d004). Run end: not found (runs.tsv gives None, the page gives only the start). Gap: not found
- 2: "frame 36's second fix closes the bypass, night 86 runs" (commit e390c6c3, 2026-09-18 06:08)
- 3: frame 36's line (`plans/archive/stack-2026-09-18.md:60`)
- 4: 4 walls.
  - n86-W1: Developer exhausts 10 of 10 attempts on bg_1, no verdict [C?] (source: night86-2026-09-18.md:29-58)
  - n86-W2: a criterion asks what the ticket and base code forbid [C?] (source: night70-vs-night86-2026-09-23.md:14-18)
  - n86-W3: four broken test versions judge one diff [C?] (source: night70-vs-night86-2026-09-23.md:93-96)
  - n86-W4: write door closes after three whole-file writes [C?] (source: night70-vs-night86-2026-09-23.md:95)
- 5: commit 4ee99b51 "sentence three cut a batch too on night 86", 3 min after the read. After the second read: 0fe1b8ce "frame 38 closes on the category model context", 0 min (git log)
- 6: F37 (pushed in 0653baf4, "unclaimed and unpriced"): still open at night 87. It was claimed on 2026-09-23 (0fe1b8ce). The second read produced no new frame. F37 carries its three walls (0fe1b8ce)
- 8: n86-W1 to W4: n87: no read. Not met in n88 (the cut read names cuts only). n89: no read
- 9: the session: "Frame 37 is pushed for it, unclaimed and unpriced, because the question is where a 9B model stops and that is a question for Roman" (commit 0653baf4 body). Decided: turned. Second read, the session: "Step 2 of frame 4's order, a larger Developer, stays closed" (night70-vs-night86-2026-09-23.md:19). Decided: continued
- 11: 75d12c2b, hands off 2026-09-18 16:50 (d391ed22). 9108c499 claims frames 33 and 4 at 18:37 (285a4a54). Second read by 07e01dfc (night70-vs-night86-2026-09-23.md:4)
- 12: stop classes gaveup_nothing 1, pend_behind 1. Named: gaveup_nothing ("tick:exhausted attempt 10 of 10"). Not named: pend_behind

### night 87
- run: start 2026-09-19 14:44, commit f3205688 (runs.tsv line 7)
- read pages: none
- 2 to 6, 9, 11: no read
- 8: no walls named (no read)
- 12: stop classes gaveup_red 1. Not named: gaveup_red (no read)

### night 88
- run: start 2026-09-21 02:51, commit d192b62a (runs.tsv line 8)
- read pages: `plans/archive/night88-cut-read-2026-09-25.md`; `plans/archive/fit-overrun-read-2026-09-25.md` (frame 56, the register, not the night)
- read landed: 2026-09-25 02:13 (4318e36e). Fit read 02:03 (a94bf17b). Run end: 2026-09-21 04:03 (runs.tsv). Gap: 94:10. Both landed after night 93 started at 01:56
- 2: not found
- 3: frames 47, 53, 59 and 61 in the stack (night88-cut-read-2026-09-25.md:3-4)
- 4: 5 walls. The fit read names 0 live walls: "the 603 are historical" (fit-overrun-read-2026-09-25.md:6).
  - n88-W1: reply cap cuts 10 runaway-loop turns, 24.2% of model time [C?] (F47) (source: night88-cut-read-2026-09-25.md:322-330)
  - n88-W2: half-window rule evicts older reads, seats repeat reads 28% [C2] (F53) (source: night88-cut-read-2026-09-25.md:332-344)
  - n88-W3: ledger row cut at 160 drops why a claim is false [C?] (F59) (source: night88-cut-read-2026-09-25.md:346-355)
  - n88-W4: 14 refused writes owed and never met [C?] (F61) (source: night88-cut-read-2026-09-25.md:357-366)
  - n88-W5: symbol read cut, 865 of 885 rows with no call [C?] (F85) (source: night88-cut-read-2026-09-25.md:356)
- 5: commit 01ff078f fix(roles), 5 min after the read. It is frame 82's fix. The first act on the read is de9f8f63 "frame 85 takes the symbols cut with no call", 17 min (git log)
- 6: F85 (pushed de9f8f63, 2026-09-25 02:30): pushed after night 89 had run. State: not found
- 8: n88-W1 to W5: n89, n90, n91: no read
- 9: the session: "Frame 53 ... The fraction is still a ruling for Roman, now on a smaller number" (night88-cut-read-2026-09-25.md:340). Decided: continued (commit 4318e36e "frames 47, 53, 59 and 61 carry what it settles")
- 11: batch B ran for 5748c2d9 (night88-cut-read-2026-09-25.md:17). 5748c2d9 took frames 82, 83, 79 at 2026-09-25 00:11 (f1d12ff3)
- 12: stop classes gaveup_nothing 1, pend_behind 2. Not named: gaveup_nothing, pend_behind (the read names cuts only)

### night 89
- run: start 2026-09-22 19:30, commit 369a34f9 (runs.tsv line 9)
- read pages: none
- 2 to 6, 9, 11: no read
- 8: no walls named (no read)
- 12: stop classes gaveup_nothing 1, pend_behind 2. Not named: both (no read)

### night 90
- run: start 2026-09-23 10:50, commit f251a51b (runs.tsv line 10)
- read pages: none
- 2 to 6, 9, 11: no read
- 8: no walls named (no read)
- 12: stop classes gaveup_nothing 1, pend_behind 2. Not named: both (no read)

### night 91
- run: start 2026-09-24 01:07, commit b79882e2 (runs.tsv line 11)
- read pages: none
- 2 to 6, 9, 11: no read
- 8: no walls named (no read)
- 12: stop classes gaveup_red 1. Not named: gaveup_red (no read)

### night 92
- run: start 2026-09-24 15:45, commit 40b4777d (runs.tsv line 12)
- read pages: `plans/archive/ten-reds-read-2026-09-24.md` (frame 82, the gate's ten known reds, not a read of night 92)
- read landed: 2026-09-24 20:13 (71aa7cea). Run end: 19:02 (runs.tsv). Gap: 1:11
- 2: "frame 80 is taken by 8736e9fc and night 92 runs cold from the worktree at 40b4777" (commit d19085dc, 15:47)
- 3: frame 80's line (`plans/archive/stack-2026-09-24.md:254`)
- 4: 2 walls (of the gate, not of the night).
  - n92-W1: six of ten known reds are brief faults [C?] (F82) (source: ten-reds-read-2026-09-24.md:23)
  - n92-W2: four check faults, two put fixture text the product never shows [C13] (F82) (source: ten-reds-read-2026-09-24.md:23-26)
- 5: commit 9cda6702 "frame 82's read lands and its design review runs on Opus", 1 min, an agent started (git log)
- 6: F84 (pushed 8b851d00, 2026-09-25 02:18, "frame 84 carries the leftovers"): still open at night 93 (open in `plans/stack.md:4469`)
- 8: n92-W1, W2: not met in n93 ("Frame 82, line 4: validated", night93-walk-2026-09-25.md:227). Not met in n94, n95
- 9: Roman: "can you do it in a subagent?" (2026-09-24 20:00, `plans/archive/stack-2026-09-25.md:129`). Decided: continued, by agents
- 11: 8736e9fc claims frame 82 at 20:02 (06341e0f). Hand-off at 23:47 (52190e25). 5748c2d9 and 00aea66b both take at 00:11 (f1d12ff3, eb7a66e1)
- 12: stop classes gaveup_red 1, pend_behind 1. Not named: both (the read is of the gate)

### night 93
- run: start 2026-09-25 01:56, commit 794a28f2 (runs.tsv line 13)
- read pages: `plans/archive/night93-walk-2026-09-25.md`
- read landed: 2026-09-25 11:03 (6003aa2c). The agent ran at 06:28 (page line 3). Run end: 05:21 (runs.tsv). Gap: 5:42
- 2: "the baseline is at 794a28f, night 93 runs for frames 82, 83 and 79" (commit 6417f0c8, 01:58)
- 3: frames 82, 83, 79 (`plans/archive/stack-2026-09-25.md` lines 66, 619, 411)
- 4: 2 walls.
  - n93-W1: resumed b_1 past cap, no predicate wakes it, three batches wait [C?] (F83, then F86) (source: night93-walk-2026-09-25.md:234-240)
  - n93-W2: stuck three times on t_ej_02, newline not in criterion c_2 [C?] (F88) (source: night93-walk-2026-09-25.md:248-251)
- 5: commit bedcabd4 "frames 82 and 79 close on night 93 ... frame 86 takes the resume past the cap", 0 min. Agent for frame 86 pass 1 started at 11:04 (914445e2), 1 min
- 6: F86: built before night 94, pass 2 in a6278c0 (night94-walk-2026-09-25.md:6-7)
- 8: n93-W1: met in n94 as n94-W1: not sure (same sign, nobody wakes after a resume, the read names a quarantined key). Not met in n95 ("Night 95 had none", night95-walk-2026-09-28.md:287). Not met in n96 ("the resume is still unobserved", night96-walk-2026-09-29.md:52).
  n93-W2: met in n94 as n94-W4: same sign at the same place (bg_1 echo_json criterion, the read renames the cause to the indent). Not met in n95 ("the format fault is gone", night95-walk-2026-09-28.md:257). n96: not named
- 9: the session: "Frame 83: not validated ... Frame 79: validated" (night93-walk-2026-09-25.md:233,242). Decided: continued
- 11: read by an agent on Opus (page line 3). 5748c2d9 holds frames 82, 83, 79 (f1d12ff3)
- 12: stop classes gaveup_nothing 1, pend_behind 3. Named: gaveup_nothing ("Stuck ... run out of things to try"), pend_behind ("Three schedulable batches then waited behind it")

### night 94
- run: start 2026-09-25 12:00, commit a6278c08 (runs.tsv line 14)
- read pages: `plans/archive/night94-walk-2026-09-25.md`
- read landed: 2026-09-25 16:29 (22ddde8e). Run end: 16:21 (runs.tsv). Gap: 0:08
- 2: "frame 86's pass 2 is committed, night 94 runs for frames 59, 83 and 86" (commit b793a11e, 12:02)
- 3: frames 59, 83, 86 in the stack (`plans/stack.md:4131`, `:4519`; `plans/archive/stack-2026-09-25.md:619`)
- 4: 5 walls.
  - n94-W1: resume to bg_1 with quarantined key, nobody wakes after s278 [C?] (F86, then F87) (source: night94-walk-2026-09-25.md:385-391)
  - n94-W2: Architect groups prefix id tk_1, refused three times [C?] (source: night94-walk-2026-09-25.md:279-288)
  - n94-W3: unfounded verdict's ledger row loses 205 of 505 characters [C?] (F59) (source: night94-walk-2026-09-25.md:393-394)
  - n94-W4: Critic finding on one-line constraint leads to rewrites breaking imports [C?] (F88) (source: night94-walk-2026-09-25.md:396-399)
  - n94-W5: page omits bg_3 and shows a stale grouping entry [C11] (F86) (source: night94-walk-2026-09-25.md:389)
- 5: commit 48329b12 fix(critic) "the unfounded verdict's ledger row keeps the whole reason", 19 min (git log)
- 6: F87 (pushed 22ddde8e): still open at night 95 (pass 3 on 2026-09-30, ca013d2e). F88 (pushed 22ddde8e): built before night 95 ("4840fda holds ... frame 88 in full", night95-walk-2026-09-28.md:7-8)
- 8: n94-W1: not met in n95, n96, n97 (night95-walk-2026-09-28.md:287; night96-walk-2026-09-29.md:52; night97-walk-2026-09-29.md:112).
  n94-W2: met in n95 as n95-W2: same sign at the same place ("the grouping refusal is night 94's prefix error again", night95-walk-2026-09-28.md:276).
  n94-W3: not met in n95 ("3 of 3 falsified rows are whole", night95-walk-2026-09-28.md:288). Not named in n96, n97.
  n94-W4: n95: not sure (n95-W1 is frame 88's route, another sign). Not named in n96, n97.
  n94-W5: not met in n95, n96, n97
- 9: the session: "Frame 83: the restart loop falls" and "Frame 86, pass 2: works as built, and the night still stalls" (night94-walk-2026-09-25.md:383,386). Decided: continued
- 11: read by an agent on Opus (page line 3). 5748c2d9 hands at 12:29 at the 300k mark (ad7c7979). 213e58fd takes frame 86 at 12:32 (1de75c77)
- 12: stop classes gaveup_nothing 1, gaveup_red 1, pend_behind 1. Named: a give-up (the quarantined tests_failing key, the grouping stall; the class of each is not sure), pend_behind ("bg_2 never started")

### night 95
- run: start 2026-09-28 00:37, commit 4840fda3 (runs.tsv line 15)
- read pages: `plans/archive/night95-walk-2026-09-28.md`
- read landed: 2026-09-28 02:03 (d22b62fa). Run end: 01:59 (runs.tsv). Gap: 0:04
- 2: "the GPU pause is lifted and night 95 runs again at 4840fda" (commit 154bc1f2, 00:37)
- 3: frames 86, 59, 88 (night95-walk-2026-09-28.md:7-8)
- 4: 2 walls.
  - n95-W1: Architect cannot file a finding, empty answer cycles the Developer [C10] (F88, then F90) (source: night95-walk-2026-09-28.md:283-285)
  - n95-W2: Architect groups prefix tk_1 again, version_option gets no batch [C?] (source: night95-walk-2026-09-28.md:263-279)
- 5: commit d852f9a4 "frame 90 is pushed", 0 min. Hand-off 3ee470e0 at 02:10, 7 min
- 6: F90 (pushed d852f9a4): built before night 96 (night 96 ran at "f933f25, frame 90's closing commit", night96-walk-2026-09-29.md:3-4)
- 8: n95-W1: not met in n96 ("Frame 90's ends-when holds on this walk", night96-walk-2026-09-29.md:18). Not named in n97, n98.
  n95-W2: n96, n97: not named. Met in n98 as n98-W2: same sign at the same place (grouping of tk_1_version_option_show_python, night98-walk-2026-09-29.md:74,104)
- 9: Roman: the hand-off "at Roman's word" (commit 3ee470e0, his words not found). The session: "Frame 88 ... The route never started, because the Architect could not file a finding" (night95-walk-2026-09-28.md:283). Decided: turned to frame 90
- 11: read by an agent on Opus. 213e58fd hands at 02:10 (3ee470e0). b4768744 claims frame 90 at 02:13 (e5e067db)
- 12: stop classes gaveup_nothing 1, pend_behind 1. Named: gaveup_nothing ("gave up on: structural_review for bg_1"). Not named: pend_behind

### night 96
- run: start 2026-09-29 02:49, commit f933f253 (runs.tsv line 16)
- read pages: `plans/archive/night96-walk-2026-09-29.md`
- read landed: 2026-09-29 05:45 (310f727d). Run end: 05:37 (runs.tsv). Killed at 05:44 (page line 4). Gap: 0:08
- 2: "night 96 runs again at Roman's word, detached at f933f25" (commit f5149085, 02:49)
- 3: frame 90's line (`plans/archive/stack-2026-09-29.md:3`)
- 4: 1 wall.
  - n96-W1: broken indent folds confirm's tail into next function, exit unusable [C9] (F92) (source: night96-walk-2026-09-29.md:28-35)
- 5: commit f778373b, the stack is handed, 1 min. F92 was pushed before the read at 05:30 (b7eb628e)
- 6: F92: built before night 97 (night97-walk-2026-09-29.md:20, "frame 92's door fires")
- 8: n96-W1: met in n97 as n97-W1: same cause (the read names frame 92's exit). n98: not sure (n98-W3 is a low label reading of the same door). n99: no read
- 9: Roman: "Roman ruled at about 05:40 that walk 3 costs GPU on a commit with frame 92's wall unfixed" (night96-walk-2026-09-29.md:46-47, the session's account). Decided: stopped the night, turned to frame 92
- 11: written by b4768744, rota-48 (page line 3). Handed to 00aea66b at 05:45 (f778373b, d491e98b)
- 12: stop classes ab_amended 1, end_working 1, gaveup_nothing 1. Named: end_working ("bg_4 was at its harness ... when the night was killed"), gaveup_nothing ("bg_2 abandoned, bg_3 deferred"). Not named: ab_amended

### night 97
- run: start 2026-09-29 07:48, commit 7d31f206 (runs.tsv line 17)
- read pages: `plans/archive/night97-walk-2026-09-29.md`
- read landed: 2026-09-29 12:02 (b7ca7dd9). Run end: 10:08 (runs.tsv). Gap: 1:54
- 2: "frame 92 validates at 7d31f20 and night 97 runs detached" (commit 74636696, 07:48)
- 3: frame 92's line (`plans/archive/stack-2026-09-29.md:518`)
- 4: 2 walls.
  - n97-W1: span door exit "end=352" drops `return rv`, confirm's tail lost [C9] (F92) (source: night97-walk-2026-09-29.md:93-105)
  - n97-W2: write of unchanged text accepted silently, seat repeats it [C?] (F93) (source: night97-walk-2026-09-29.md:97-105)
- 5: commit a04c3785 "frame 92's pass 4 builds on Opus", 2 min, an agent started. Fix 3766e2b2 at 12:26, 24 min
- 6: F93 (pushed b7ca7dd9): still open at night 98, "Frame 93: no" (night98-walk-2026-09-29.md:106). Pass 4 of F92 built before night 98 (3766e2b2)
- 8: n97-W1: met in n98 as n98-W1: same sign at the same place (confirm loses `return rv`, the read: "lost it by a whole-def span", night98-walk-2026-09-29.md:100-102). n99, n100: no read.
  n97-W2: not met in n98 (night98-walk-2026-09-29.md:106). n99, n100: no read
- 9: the session: "Leave it validating. The door fired and guided two sessions to a commit, but one exit led to the broken tail" (night97-walk-2026-09-29.md:109-110). Decided: continued
- 11: the night ran under 00aea66b. Hand-off "at Roman's word" to 36d4fbef, rota-16, at 11:54 (1baeb690, 54d50324). Read by an agent for 36d4fbef (page line 3)
- 12: stop classes ab_amended 1, gaveup_nothing 1, pend_behind 1. Named: not sure for ab_amended ("bg_2 was abandoned at attempt 1, its item is no longer schedulable"). Not named: gaveup_nothing, pend_behind

### night 98
- run: start 2026-09-29 14:48, commit 60cc23f6 (runs.tsv line 18)
- read pages: `plans/archive/night98-walk-2026-09-29.md`
- read landed: 2026-09-29 16:46 (2f77b0ac). Run end: 16:40 (runs.tsv). Gap: 0:06
- 2: "frames 89 and 91 close, frame 92 validates at d03b35c, and night 98 runs detached" (commit 18f924d4, 14:49)
- 3: frame 92's line (`plans/archive/stack-2026-09-29.md:518`)
- 4: 3 walls.
  - n98-W1: whole-def span write stops short, deletes 13 lines, every door accepts [C8] (F95) (source: night98-walk-2026-09-29.md:93-102)
  - n98-W2: grouping wake shows the Architect the wrong ticket [C?] (F96) (source: night98-walk-2026-09-29.md:103-104)
  - n98-W3: span refusal calls the top-level def "the body of except block" [C9] (source: night98-walk-2026-09-29.md:44-46)
- 5: commit e5546681 "frame 94 is held by 532b3429", 2026-09-30 03:20, 635 min (git log)
- 6: F95: built before night 99 (merged at b6a7707, f9bfb543 09:53). F96: built before night 99 (merged at 4df551b, 50c1e1a9 04:45)
- 8: n98-W1 to W3: n99, n100, n101: no read
- 9: the session: "Verdict, frame 92: the door fired, raised nothing, and guided two sessions to a landed commit" (night98-walk-2026-09-29.md:47-48). Decided: continued, frame 92 closes
- 11: read by an agent for 36d4fbef (page line 3). 532b3429 holds frame 94 from 2026-09-30 03:20 (e5546681)
- 12: stop classes gaveup_nothing 1. Named: not sure ("no batch formed for tk_1_version_option_show_python")

### night 99
- run: start 2026-09-30 11:50, commit 0bd5f3bb (runs.tsv line 19)
- read pages: none
- 2 to 6, 9, 11: no read
- 8: no walls named (no read)
- 12: stop classes gaveup_nothing 1, pend_behind 2. Not named: both (no read)

### night 100
- run: start 2026-09-30 14:11, commit bdefec9d (runs.tsv line 20)
- read pages: none
- 2 to 6, 9, 11: no read
- 8: no walls named (no read)
- 12: stop classes gaveup_nothing 1, pend_behind 1. Not named: both (no read)

### night 101
- run: start 2026-09-30 20:05, commit ff0f6928 (runs.tsv line 21)
- read pages: none
- 2 to 6, 9, 11: no read
- 8: no walls named (no read)
- 12: stop classes gaveup_red 1. Not named (no read)

### night 102
- run: start 2026-10-01 03:27, commit 9f725811 (runs.tsv line 22)
- read pages: none
- 2 to 6, 9, 11: no read
- 8: no walls named (no read)
- 12: stop classes gaveup_red 1. Not named (no read)

### night 103
- run: start 2026-10-01 09:52, commit ae9abd05, from night 101's database (runs.tsv line 23)
- read pages: `plans/night103-read.md`
- read landed: 2026-10-01 09:57 (57987a3d). Run end: 09:54 (runs.tsv). Gap: 0:03
- 2: "frame 104 pass 3 is committed and night 103 run 2 starts at the seam in one minute" (commit aa79f8ea, 09:54)
- 3: frame 104's line (`plans/archive/stack-2026-10-01.md:47`)
- 4: 3 walls.
  - n103-W1: result cap hides the batch's tests, Critic passes blind [C2] (F101) (source: night103-read.md:21-27,40-41)
  - n103-W2: Architect writes its own tool results, frame 98's door misses it [C7] (guide: frame 113, the same shape) (source: night103-read.md:31-34,44-45)
  - n103-W3: seam run 1 stops on a missing column [C?] (source: night103-read.md:6)
- 5: commit ff3fbb8b "frame 104's third review finds one rare high", 1 min. Fix 0d78ee20 fix(probes) at 09:59, 2 min
- 6: no new frame by number (not found). The read confirms F101 and F104 (night103-read.md:39-41)
- 8: n103-W1: n104: no read. Not met in n105, n106.
  n103-W2: n104: no read. n105: not sure (n105-W4, the Vision Keeper). n106: not sure (n106-W4, the Developer).
  n103-W3: n104: no read. Not met in n105, n106
- 9: the session: "Frame 104 holds: the seam walk started one minute after launch" (night103-read.md:39). Decided: continued
- 11: read on Opus (page line 8). d2cc277a holds frames 104 and 101 (91feb6ce, 207f00cd). Hand-off to 10885dab at 14:14 (de65f97c, 3846f702)
- 12: stop classes none

### night 104
- run: start 2026-10-01 12:36, commit a8ab7ff1, from night 101's database (runs.tsv line 24)
- read pages: none
- 2 to 6, 9, 11: no read
- 8: no walls named (no read)
- 12: stop classes none

### night 105
- run: start 2026-10-02 02:53, commit 4f560506 (runs.tsv line 25)
- read pages: `plans/night105-read.md`
- read landed: 2026-10-02 04:08 (d62dd95f). Run end: 04:03 (runs.tsv). Gap: 0:05
- 2: "the gate at 4f56050 holds at 23 against 23 and night 105 runs for frames 100, 106 and 107" (commit df724c6e, 02:55)
- 3: frames 100, 106, 107 (`plans/archive/stack-2026-10-02.md` lines 58, 36, 5)
- 4: 5 walls.
  - n105-W1: Developer challenge to Tester never parses, 13 identical calls [C7] (guide: frame 109) (source: night105-read.md:44-46)
  - n105-W2: tests call CliRunner.invoke on plain function, KeyError prog_name [C?] (F109) (source: night105-read.md:48)
  - n105-W3: night print counts wrong, 20 turns for 43, "repeats: 0" [C13] (F105) (source: night105-read.md:7,46)
  - n105-W4: Vision Keeper writes fake `OK` tool results, 12 sessions [C7] (guide: frame 113, the same shape) (source: night105-read.md:50-64)
  - n105-W5: 20 sessions take turns past "work ... is complete" [C?] (source: night105-read.md:66-68)
- 5: commit 0f3816d6 "Roman rules frame 109 before 108 and moves frame 105's line to 60k", 318 min (git log)
- 6: F109 (pushed d62dd95f): built before night 106, closed on night 106 (1de91e5d)
- 8: n105-W1: not met in n106 (frame 109 closes, "every Developer challenge parsed", 1de91e5d). Not named in n107, n108.
  n105-W2: met in n106 as n106-W1: same sign at the same place (`inh_echo_json_02` "still invokes the plain function", night106-read.md:18). Not named in n107, n108.
  n105-W3: n106: not sure (night106-read.md:52, the print does not define a term). n107: not sure (n107-W8, another count). n108: not named.
  n105-W4: n106: not sure (n106-W4, the Developer). Met in n107 as n107-W4: same sign (own `OK` lines, the count lists vision_keeper 20 turns, night107-read.md:47). Met in n108 as n108-W9: same sign (vision_keeper 27 turns).
  n105-W5: not met in n106, n107, n108
- 9: Roman: the order "frame 109 before 108" and frame 105's line at 60k (commit 0f3816d6 subject, his words not found). Decided: turned (order)
- 11: read on Opus (page line 3). eca94a44 holds frames 107, 106, 105, 100 from 10885dab's hand-off at 02:56 (a49f2d4b)
- 12: stop classes gaveup_nothing 1, pend_behind 2. Named: gaveup_nothing ("gave up on: tests_failing for bg_1"), pend_behind ("bg_2 and bg_3 never started")

### night 106
- run: start 2026-10-02 10:40, commit bf74640f (runs.tsv line 26)
- read pages: `plans/night106-read.md`
- read landed: 2026-10-02 13:47 (1de91e5d). Run end: 13:40 (runs.tsv). Gap: 0:07
- 2: "the gate at 8288a39 holds 23 against 23 and night 106 runs for frames 109 and 105" (commit 7cdefca6, 10:40)
- 3: frames 109 and 105 (`plans/archive/stack-2026-10-02.md` lines 89, 106)
- 4: 5 walls.
  - n106-W1: challenged test rewritten into same fault, unchallenged never changes [C4] (guide: frame 110) (source: night106-read.md:24-38)
  - n106-W2: Developers loop on refused repeat challenge, do not escalate [C8] (guide: frame 111) (source: night106-read.md:56)
  - n106-W3: wakes repeat on unchanged tree, ladder spent [C6] (guide: frame 112) (source: commit 1de91e5d body)
  - n106-W4: Developer writes own result lines, 22 sessions [C7] (guide: frame 113) (source: night106-read.md:46-48)
  - n106-W5: inherited failing test has no route, "has no criterion" [C10] (guide: frame 114) (source: night106-read.md:43)
- 5: commit a0974f3e "Roman rules the order 110, 111, 112, 108, 113, 114", 43 min. Code commit bda757fc feat(nightcount) at 14:32, 45 min
- 6: F110: built before night 107 ("It is the walk of frame 110", night107-read.md:3). F111: still open at night 107, built before night 108 (d366702, night108-read.md:3). F112: still open at night 107. F113: still open, put aside by Roman on 2026-10-04 (fa8ff072). F114: still open at night 107
- 8: n106-W1: n107: not sure (n107-W1, frame 110's label). n108: not sure (n108-W3, a `_fixed` copy). n109: not sure (night109-read.md:62-68, the Tester answered one of four).
  n106-W2: n107: not sure (n107-W2). n108: not sure (n108-W1, the read moves frame 111's wall). n109: not sure (n109-W1).
  n106-W3: met in n107 as n107-W3: same cause (the read names frame 112). n108, n109: not sure (one CYCLE line each).
  n106-W4: met in n107 as n107-W4, in n108 as n108-W9, in n109 as n109-W8: same cause (the reads name frame 113).
  n106-W5: met in n107 as n107-W5, in n108 as n108-W8: same cause (the reads name frame 114). n109: not sure (n109-W3 is "held by no frame")
- 9: Roman: the order "110, 111, 112, 108, 113, 114" and frame 105's cost line dropped (commit a0974f3e subject, his words not found). Decided: continued in his order
- 11: eca94a44 holds the stack. Hand-off at 15:53 to 46f23339 (e810fe02, 97ca57dd)
- 12: stop classes gaveup_nothing 2, pend_behind 1. Named: gaveup_nothing ("bg_1 parked past the attempt cap and bg_2 given up"), pend_behind ("Walk 3 ran bg_3's grouping, annotation and approval only, 0 commits")

### night 107
- run: start 2026-10-02 15:52, commit 8925d789 (runs.tsv line 27)
- read pages: `plans/night107-read.md`
- read landed: 2026-10-02 18:04 (08ca7ac4). Run end: 17:49 (runs.tsv). Gap: 0:15
- 2: "the gate at 6db7ffc holds 23 against 23 and night 107 runs for frame 110" (commit fbf74128, 15:52)
- 3: frame 110's line (`plans/archive/stack-2026-10-02.md:144`)
- 4: 11 walls.
  - n107-W1: crash label "failed before any assertion" fires on a chained exception [C9] (F110) (source: night107-read.md:16,72)
  - n107-W2: escalation with no reply reads `answered` [C?] (F111) (source: night107-read.md:28-30,75)
  - n107-W3: one pure repeat group of three Developer wakes [C6] (guide: frame 112) (source: night107-read.md:33-43)
  - n107-W4: own `OK` result lines, developer 24 turns in 9 sessions [C7] (guide: frame 113) (source: night107-read.md:45-49)
  - n107-W5: 25 inherited tests red at 6037f989, no route [C10] (guide: frame 114) (source: night107-read.md:51-58)
  - n107-W6: whole-file rewrite drops package exports, drops guard misses it [C8] (source: night107-read.md:71)
  - n107-W7: `__getattr__` door blocks repair of a file a commit broke [C8] (source: night107-read.md:74)
  - n107-W8: report's commit column misses a form, 3 against 6 [C13] (source: night107-read.md:70)
  - n107-W9: made-up counter counts a copied real result line [C13] (source: night107-read.md:74)
  - n107-W10: Developer challenges three tests whose last run passed [C?] (source: night107-read.md:73)
  - n107-W11: Architect names later batches after the first [C?] (source: night107-read.md:76)
- 5: commit f3dc8916 status, 0 min. Fix 4eb5a9ab "the crash label reads the last traceback section", 2 min
- 6: no new frame. The label fix of F110 is built before night 108 (4eb5a9a, night108-read.md:3)
- 8: n107-W1: n108: not sure (night108-read.md:18-24 counts the label, verdict not extracted). Not named in n109, n110.
  n107-W2: n108: not sure (n108-W4). Met in n109 as n109-W1: same sign at the same place (an escalation `answered` with no answer row). n110: no session.
  n107-W3: n108, n109: not sure (a CYCLE line each). n110: not met.
  n107-W4: met in n108 as n108-W9 and in n109 as n109-W8: same cause. n110: no session.
  n107-W5: met in n108 as n108-W8: same cause. n109: not sure (n109-W3). n110: not met.
  n107-W6, W7: n108: not sure (the unnamed-definition door refused four writes, "unread", night108-read.md:43). n109, n110: not met.
  n107-W8 to W11: not met in n108, n109, n110
- 9: the session: "night 107's read reaches frames 110 to 114, frame 110's crash label misfires on a chained ex..." (commit f3dc8916 subject). Decided: continued
- 11: 46f23339 holds frames 110, 111, 112 (c0a5f30a, 8f10a316, 754d1b79)
- 12: stop classes gaveup_nothing 1, pend_behind 2. Named: gaveup_nothing ("`echo_json_group` was given up, not parked"), pend_behind (the two other batches "`pending`, 0 commits")

### night 108
- run: start 2026-10-02 18:34, commit 4eb5a9ab (runs.tsv line 28)
- read pages: `plans/night108-read.md`
- read landed: 2026-10-02 22:31 (1f07a682). Run end: 22:24 (runs.tsv). Gap: 0:07
- 2: "frame 110 closes on the gate alone at 4eb5a9a, frame 111 validates on night 108" (commit 103bc7cf, 18:35)
- 3: frame 111's line (`plans/archive/stack-2026-10-03.md:5`)
- 4: 9 walls.
  - n108-W1: repeat-refs door skips an unanswered challenge, nine land [C8] (guide: frame 111) (source: night108-read.md:65)
  - n108-W2: push key lists the Architect's own challenges on the Developer's test [C?] (source: night108-read.md:66)
  - n108-W3: Tester answers with a new `_fixed` test, challenged test stays red [C?] (source: night108-read.md:67)
  - n108-W4: Architect's `tick:unresolved` answers Tester challenges with no words [C?] (source: night108-read.md:68)
  - n108-W5: Tester re-encodes one test five times, sends no answer [C?] (source: night108-read.md:69)
  - n108-W6: spent-ladder batch keeps taking commits, not parked [C?] (source: night108-read.md:70)
  - n108-W7: all ten Architect answers have empty body_text [C11] (guide: frame 115) (source: night108-read.md:45-57)
  - n108-W8: inherited tests fail in two batches [C10] (guide: frame 114) (source: night108-read.md:42)
  - n108-W9: own result lines, 95 turns in 55 sessions [C7] (guide: frame 113) (source: night108-read.md:59-61)
- 5: commit e4b29877 "night 108 moves frame 111's wall to the unanswered challenge, pass 4 starts", 0 min. Fix 92ca0240 at 22:37, 6 min
- 6: no new frame. F111 pass 4 built before night 109 (92ca024, night109-read.md:3)
- 8: n108-W1: n109: not sure (n109-W1). n110: no session. n111: not sure (n111-W1 to W3).
  n108-W2: not met in n109 ("No Architect challenge is in it, unlike m177 and m182 on night 108", night109-read.md:18). Not met in n110, n111.
  n108-W3: not met in n109 ("The `_fixed` copy shape of night 108 did not recur", night109-read.md:68). Not met in n110, n111.
  n108-W4: met in n109 as n109-W4: same sign (a passing commit from a wake on an empty Architect answer, outside the ladder). n110, n111: not met.
  n108-W5: not met in n109, n110, n111.
  n108-W6: n109: not sure (n109-W4). n110, n111: not met.
  n108-W7: met in n109 as n109-W9: same cause. n110, n111: not met.
  n108-W8: n109: not sure (n109-W3). n110: not met. Met in n111 as n111-W4: same cause ("This is frame 114's shape").
  n108-W9: met in n109 as n109-W8, in n111 as n111-W5: same cause. n110: no session
- 9: the session: "night 108 moves frame 111's wall to the unanswered challenge, pass 4 starts" (commit e4b29877 subject). Decided: turned inside frame 111
- 11: 46f23339 holds the stack (5cda62c7)
- 12: stop classes gaveup_nothing 3. Named: gaveup_nothing (bg_1 and bg_2 deferred, bg_3 at "attempt 10 of 10", night108-read.md:36-41)

### night 109
- run: start 2026-10-02 23:04, commit 92ca0240 (runs.tsv line 29)
- read pages: `plans/night109-read.md`
- read landed: 2026-10-03 02:26 (09d42eb8). Run end: 02:18 (runs.tsv). Gap: 0:08
- 2: "frame 111 validates on night 109 at 92ca024" (commit 5cda62c7, 23:05)
- 3: frame 111's line (`plans/archive/stack-2026-10-03.md:5`)
- 4: 9 walls.
  - n109-W1: escalation turned into a challenge has no answer row, door refuses all night [C12] (F111) (source: night109-read.md:72)
  - n109-W2: Developer makes a helper a Click command, import breaks the batch [C3] (guide: frame 131, the same sign) (source: night109-read.md:73)
  - n109-W3: a commit passes the criteria, leaves two inherited tests red [C?] (source: night109-read.md:74)
  - n109-W4: only passing bg_2 commit came from a wake outside the ladder [C?] (source: night109-read.md:75)
  - n109-W5: six challenges in one turn, "already sent" refuses 14 times [C8] (guide: frame 116) (source: night109-read.md:76)
  - n109-W6: bg_3 gets no Developer session, no batch reviewed [C?] (source: night109-read.md:77)
  - n109-W7: harness records no test run on some landed commits [C?] (source: night109-read.md:78)
  - n109-W8: own result lines, developer 84 turns in 29 sessions [C7] (guide: frame 113) (source: night109-read.md:58-60)
  - n109-W9: Architect answers m64, m96, m99 with no words [C11] (guide: frame 115) (source: night109-read.md:66)
- 5: commit 103a7582 "night 109 holds the landing half of frame 111 and shows a pending-door defect, pass 5 starts", 0 min. Fix eb7cd0de at 02:32, 6 min
- 6: no new frame. F111 pass 5 built before night 110 (eb7cd0de is night 110's commit)
- 8: n109-W1: n110: no session. Met in n111 as n111-W1: same sign at the same place (m97, the closed escalation with no answer row, night111-read.md:61-66). n112: not sure (n112-W1).
  n109-W2: n110: no session. Met in n111 as n111-W4: same sign at the same place (bg_2 dead since 3449fcca). n112: not sure (n112-W2, the same sign in bg_3).
  n109-W3: n110, n111: not met. Met in n112 as n112-W7: same sign at the same place (bg_2, `inh_022b8a87` and `inh_51d478df` red at the head).
  n109-W4 to W7: not met in n110, n111, n112.
  n109-W8: met in n111 as n111-W5 and in n112 as n112-W3: same cause.
  n109-W9: met in n112 as n112-W4: same cause. n110, n111: not met
- 9: the session: "pass 5 starts" (commit 103a7582 subject). Decided: continued
- 11: 46f23339 keeps frame 111 through night 109 (ed0aae86). Hand-off at 03:00 to 3d6e6173 (dc9f7d0d, 9c28a20f)
- 12: stop classes gaveup_nothing 1, gaveup_red 1, pend_behind 1. Named: a give-up (bg_1 "37 red", bg_2 "the CYCLE at attempt 5"; the class of each is not sure), pend_behind ("bg_3 never got a Developer session")

### night 110
- run: start 2026-10-03 02:59, commit eb7cd0de, from night 109's database (runs.tsv line 30)
- read pages: `plans/night111-read.md` section 1
- read landed: 2026-10-03 03:29 (958e206a), after night 111 ran. Run end: 03:00 (runs.tsv). Gap: 0:29
- 2: "frame 111 validates on seam night 110 at eb7cd0d" (commit dc9f7d0d, 03:00)
- 3: frame 111's line (`plans/archive/stack-2026-10-03.md:5`)
- 4: 1 wall.
  - n110-W1: seam copies the quarantined tick row, the night wakes nobody [C13] (source: night111-read.md:11-17)
- 5: commit 37cc7a1c "night 111 reruns the seam from a pair cut by hand", 03:04. It is 4 min after the night and before the read
- 6: no frame
- 8: n110-W1: not met in n111 (it ran from the cut pair, night111-read.md:15-16). Not met in n112, n113
- 9: the session: "frame 111's seam night 110 woke nobody, and night 111 reruns the seam from a pair cut by hand" (commit 37cc7a1c subject). Decided: continued
- 11: 3d6e6173 (night111-read.md:3; 9c28a20f)
- 12: stop classes gaveup_nothing 1, gaveup_red 1, pend_behind 1 (shared with night 109's database). Not named: all three

### night 111
- run: start 2026-10-03 03:05, commit eb7cd0de, from night 109's database cut by hand (runs.tsv line 31; night111-read.md:15)
- read pages: `plans/night111-read.md`
- read landed: 2026-10-03 03:29 (958e206a). Run end: 03:18 (runs.tsv). Gap: 0:11
- 2: "night 111 reruns the seam from a pair cut by hand" (commit 37cc7a1c, 03:04)
- 3: frame 111's line (`plans/archive/stack-2026-10-03.md:5`)
- 4: 5 walls.
  - n111-W1: thread key says "not answered yet", door says answered, for m97 [C12] (F111) (source: night111-read.md:61-66)
  - n111-W2: earlier refusals evicted by turn 17, third send sees none [C2] (F111) (source: night111-read.md:56-60)
  - n111-W3: refusal gives the rung as a bare name after a dash [C9] (F111) (source: night111-read.md:53-55)
  - n111-W4: circular import kills bg_2's suite, door refuses whole-file repair [C10] (guide: frame 114) (source: night111-read.md:87-95)
  - n111-W5: four of four Developer sessions write own tool results [C7] (guide: frame 113) (source: night111-read.md:97-98)
- 5: fix ee1ed121 "the thread agrees with the door, and the way out stays in the wake", 04:13, 44 min
- 6: no new frame. F111 pass 6 built before night 112 (ee1ed12, night112-read.md:1)
- 8: n111-W1: n112: not sure (n112-W1). n113: not met. n114: no read.
  n111-W2: not met in n112 ("eviction does not explain this night", night112-read.md:107). n113: not sure (n113-W7). n114: no read.
  n111-W3: not met in n112 (five sessions met the new sentence, night112-read.md:48). n113: not met. n114: no read.
  n111-W4: met in n112 as n112-W2 and in n113 as n113-W2: same cause ("frame 114, not frame 111"; "night 112's shape a third time"). n114: no read.
  n111-W5: met in n112 as n112-W3 and in n113 as n113-W1: same cause. n114: no read
- 9: the session: "The frame does not close on this seam. The door text works where the seat reads it" (night111-read.md:102-103). Decided: continued (pass 6)
- 11: read by 3d6e6173 (night111-read.md:3)
- 12: stop classes gaveup_nothing 1, gaveup_red 1, pend_behind 1 (shared state). Named: a give-up ("the tick quarantined again"). Not named: the other two

### night 112
- run: start 2026-10-03 04:14, commit ee1ed121, from night 109's end (runs.tsv line 32; night112-read.md:1)
- read pages: `plans/night112-read.md`
- read landed: 2026-10-03 13:44 (8302ed1d). Run end: 06:04 (runs.tsv). Gap: 7:40
- 2: "frame 111's pass 6 lands at ee1ed12, the review and seam night 112 run" (commit 92e97a90, 04:15)
- 3: frame 111's line (`plans/archive/stack-2026-10-03.md:5`)
- 4: 7 walls.
  - n112-W1: s252 refused the same challenge three times with the refusal in view [C8] (guide: frame 111) (source: night112-read.md:105-107)
  - n112-W2: bg_3 self-made circular import, drops door refuses repair 37 times [C10] (guide: frame 114) (source: night112-read.md:62-67,109)
  - n112-W3: 20 of 29 Developer sessions write own results [C7] (guide: frame 113) (source: night112-read.md:69-72)
  - n112-W4: four Architect answers empty, the call has no words argument [C11] (guide: frame 115) (source: night112-read.md:84-87)
  - n112-W5: "different refs" refusal fires on identical refs, 12 sessions [C9] (source: night112-read.md:98)
  - n112-W6: "ran anyway" detector narrower than the account [C13] (source: night112-read.md:74)
  - n112-W7: bg_2 inherited `inh_022b8a87`, `inh_51d478df` red at head, no repair tried [C10] (guide: frame 114) (source: night112-read.md:79)
- 5: commit 032c71ca "frame 108's design caps the tail at a third of the budget", 1 min
- 6: F116 (pushed 8302ed1d): still open at night 113 (open in `plans/stack.md:3691`)
- 8: n112-W1: met in n113 as n113-W4: same sign (s143 met one refusal three times, under frame 116). n114: no read. n115: not met.
  n112-W2: met in n113 as n113-W2: same cause. n114: no read. Not met in n115 ("No inherited or project test failed", night115-read.md:81).
  n112-W3: met in n113 as n113-W1 and in n115 as n115-W5: same cause. n114: no read.
  n112-W4: met in n113 as n113-W3: same cause. n114: no read. Not met in n115 (night115-read.md:89).
  n112-W5: n113: not sure (s149 meets the same text, night113-read.md:73). n114: no read. n115: not met.
  n112-W6, W7: not met in n113, n115. n114: no read
- 9: Roman: frame 111 "closes on Roman's ruling after night 112" (commit 8302ed1d subject, his words not found). The session: "Frame 111's line fails on its first half and holds on its second" (night112-read.md:105). Decided: stopped frame 111, turned to frame 108
- 11: read by an Opus agent for 3d6e6173 (night112-read.md:3). Hand-off to 5e8ace65 at 2026-10-04 03:02 (928d18fb)
- 12: stop classes gaveup_nothing 1, gaveup_red 2. Named: a give-up (bg_3 "exhausted at attempt 10", bg_2's s254 "woke on tick:exhausted"; the class of each is not sure)

### night 113
- run: start 2026-10-04 03:00, commit 6ff6fd02 (runs.tsv line 33)
- read pages: `plans/night113-read.md`
- read landed: 2026-10-04 04:19 (0a4c9567). Run end: 04:06 (runs.tsv). Gap: 0:13
- 2: "frame 108 validates on cold night 113 at 6ff6fd0" (commit e5c6a61c, 03:01)
- 3: frame 108's line (`plans/archive/stack-2026-10-04.md:3`)
- 4: 8 walls.
  - n113-W1: 9 of 10 Developer sessions write own results [C7] (guide: frame 113) (source: night113-read.md:53-55)
  - n113-W2: batch breaks its own utils.py import a third time [C10] (guide: frame 114) (source: night113-read.md:60-68)
  - n113-W3: Architect answer m71 has NULL body_text, m66 unanswered [C11] (guide: frame 115) (source: night113-read.md:72-74)
  - n113-W4: s143 sends two challenges and an escalation per reply [C8] (guide: frame 116) (source: night113-read.md:79-81)
  - n113-W5: stub of a long call reply stubs again to nothing [C7] (guide: frame 117) (source: night113-read.md:85-87)
  - n113-W6: Developer wake takes two thirds, tail cap cannot act [C2] (guide: frame 119) (source: night113-read.md:91)
  - n113-W7: "The answer is in this prompt" written one turn before eviction [C9] (guide: frame 169, the same sign) (source: night113-read.md:92)
  - n113-W8: bg_1 attempts repeat on red trees [C6] (guide: frame 112) (source: night113-read.md:93)
- 5: commit 3ba47d55 "frame 119 holds the Developer wake", 0 min. Code a27be33f feat(gate) at 04:42, 23 min (frame 118, not from the read)
- 6: F119 (pushed 3ba47d55): still open at night 114 (pass 1 lands at 06:04, 42cfb9a7). Built before night 115 (56f8d302)
- 8: n113-W1: n114: no read. Met in n115 as n115-W5 and in n116 as n116-W5: same cause.
  n113-W2: n114: no read. Not met in n115, n116 (night115-read.md:81; night116-read.md:59).
  n113-W3: n114: no read. Not met in n115 (night115-read.md:89). Met in n116 as n116-W8: same cause.
  n113-W4: n114: no read. Not met in n115 (0 of 8). Met in n116 as n116-W4: same cause.
  n113-W5: n114: no read. Met in n115 as n115-W6 and in n116 as n116-W7: same cause.
  n113-W6: n114: no read. n115: not sure (n115-W1 is a defect of the fix). Not met in n116 ("never met the half share", night116-read.md:95).
  n113-W7, W8: n114: no read. Not met in n115, n116
- 9: the session: "Frame 108's mechanism holds. Its residue has a different cause, the Developer wake at two thirds, and that cause is a new frame" (night113-read.md:98). Decided: continued, frame 108 closes
- 11: read by an Opus agent for 5e8ace65 (night113-read.md:3)
- 12: stop classes gaveup_red 1, pend_behind 2. Named: gaveup_red ("three walks each ended `Stuck. The team gave up on: tests_failing for bg_1`"). Not named: pend_behind

### night 114
- run: start 2026-10-04 04:46, commit 52e9ee81 (runs.tsv line 34)
- read pages: none. `plans/night115-read.md` section 9 holds five lines on night 114's merge and names no wall
- 2 to 6, 9, 11: no read
- 8: no walls named (no read)
- 12: stop classes gaveup_nothing 1, gaveup_red 1. Not named: both (no read)

### night 115
- run: start 2026-10-04 06:45, commit 56f8d302 (runs.tsv line 35)
- read pages: `plans/night115-read.md`
- read landed: 2026-10-04 08:29 (93333bc3). Run end: 08:16 (runs.tsv). Gap: 0:13
- 2: not found in commit subjects. The read's title: "the walk of frame 119 at 56f8d30" (night115-read.md:1)
- 3: frame 119's line (`plans/archive/stack-2026-10-04.md:41`)
- 4: 6 walls.
  - n115-W1: half share counts a runner note as a read, s73 [C2] (guide: frame 119) (source: night115-read.md:112)
  - n115-W2: new sentence turns a closed reconcile into a quarantined one [C9] (guide: frame 121) (source: night115-read.md:100,112)
  - n115-W3: Critic quote that holds quotes never parses [C7] (guide: frame 122) (source: night115-read.md:101)
  - n115-W4: two Tester tests contradict, the fix goes to a new file [C8] (guide: frame 123) (source: night115-read.md:79-85)
  - n115-W5: 7 of 10 Developer sessions write own results [C7] (guide: frame 113) (source: night115-read.md:75-77)
  - n115-W6: stubbed replies with a call rise to 87 prompts [C7] (guide: frame 117) (source: night115-read.md:95-97)
- 5: commit d6dafd41, 0 min. Fix 4d5757db "the refusal keeps its old wording, and a runner note is no read", 08:34, 5 min
- 6: F121, F122, F123 (pushed 7205465a): still open at night 116. F119 pass 3 and 4 built before night 116 (4d5757db, 76438522)
- 8: n115-W1: not met in n116 (frame 119 closes, 466861d0). Not named in n117, n118.
  n115-W2: n116: not sure (n116-W6, other sign of frame 121). Not named in n117, n118.
  n115-W3: not met in n116 ("The night held no Critic quote with inner quotes", night116-read.md:79). n117: not named. n118: not sure (section 3 is a baseline, not extracted).
  n115-W4: met in n116 as n116-W1 and in n117 as n117-W1: same cause. Not met in n118 ("0 of 1 given-up batches hold a left-over test", night118-read.md:7).
  n115-W5: met in n116 as n116-W5: same cause. n117: not named. n118: not found (section 5 not read).
  n115-W6: met in n116 as n116-W7: same cause. n117: not named. n118: not found (listed under "Not read")
- 9: the session: "Frame 119's Developer mechanism is not yet measured, because no Developer wake reached half the budget" (night115-read.md:111). Decided: continued (pass 3)
- 11: read by an Opus agent for 5e8ace65 (night115-read.md:3)
- 12: stop classes gaveup_nothing 1, pend_behind 2. Named: gaveup_nothing ("gave up on: reconcile ..., challenge ..., tests_failing"), pend_behind ("the same item stayed `pending` with no commit")

### night 116
- run: start 2026-10-04 09:24, commit 76438522 (runs.tsv line 36)
- read pages: `plans/night116-read.md`; `plans/frame113-read.md` (a cause read of frame 113)
- read landed: 2026-10-04 10:47 (5ab7cc15). Cause read 10:54 (0005d227). Run end: 10:35 (runs.tsv). Gap: 0:12
- 2: "frame 119's pass 4 lands at 7643852 ... night 116 is the second walk" (commit 0b09644a, 09:24)
- 3: frame 119's line (`plans/archive/stack-2026-10-04.md:41`)
- 4: 8 walls. The cause read adds no wall: "There was no rise at night 106. Night 105 is the outlier" (frame113-read.md:7).
  - n116-W1: two Tester tests contradict, the fix refused by the assumption door [C8] (guide: frame 123) (source: night116-read.md:56-63)
  - n116-W2: Vision Keeper answers a challenge with a decision, asserts it as an item [C?] (F129) (source: night116-read.md:83-84)
  - n116-W3: criteria door reads the word "already" as a callable [C8] (guide: frame 125) (source: night116-read.md:85)
  - n116-W4: 2 of 7 sessions refused the same challenge three times [C8] (guide: frame 116) (source: night116-read.md:69-71)
  - n116-W5: 6 of 11 Developer sessions write own results [C7] (guide: frame 113) (source: night116-read.md:52-54)
  - n116-W6: `CUT your wake` notices from the reply-cut retry [C9] (guide: frame 121) (source: night116-read.md:96)
  - n116-W7: 19 prompts hold a stubbed reply with a call [C7] (guide: frame 117) (source: night116-read.md:73-75)
  - n116-W8: one escalation and one Architect answer, both with no text [C11] (guide: frame 115) (source: night116-read.md:65-67)
- 5: commit 466861d0 "frame 125 holds the ...", 0 min. Fix 2882eb51 at 13:15, 148 min (frame 120)
- 6: F125 (pushed 466861d0): still open at night 117 (pass 1 at 16:35, 64ca411). F129 (pushed 64ca411, 16:35, after night 117 ran): still open. F113: put aside, "Roman parks frame 113" (fa8ff072, 12:51)
- 8: n116-W1: met in n117 as n117-W1: same cause. Not met in n118 (night118-read.md:7), n119 (frame 123 closes).
  n116-W2: not named in n117, n118. Met in n119 as n119-W17: same cause (the read names frame 129).
  n116-W3: n117: not named. n118: not sure (section 4 is a baseline). Not met in n119 ("0 turns hold `the item names`").
  n116-W4: not named in n117, n118. Met in n119 as n119-W14: same cause.
  n116-W5: n117: not named. n118: not found. Met in n119 as n119-W12: same cause.
  n116-W6: not met in n117, n118, n119.
  n116-W7: n117: not named. n118: not found. Met in n119 as n119-W15: same cause.
  n116-W8: not named in n117, n118. Met in n119 as n119-W13: same cause
- 9: Roman: "Are we sure it's just the card? Is there no configuration mismatches?" (2026-10-04 12:50, `plans/archive/stack-2026-10-04.md:66`), and "Roman parks frame 113 and rules the order, the batch stoppers 120, 123 and 125 first" (commit fa8ff072 subject). Decided: turned (order)
- 11: read by an Opus agent for 5e8ace65 (night116-read.md:3). Hand-off to 419281dc at 13:56 (353515bd, 148af0ab)
- 12: stop classes gaveup_nothing 1, pend_behind 1. Named: gaveup_nothing ("gave up on: tests_failing for bg_2"). Not named: pend_behind

### night 117
- run: start 2026-10-04 13:28, commit 5543881a (runs.tsv line 37)
- read pages: `plans/frame123-read.md` (nights 115 to 117); `plans/frame114-read.md` (nights 107 to 113, landed 14:26 while night 117 ran)
- read landed: 2026-10-04 15:26 (e8caa3e2). Run end: 15:16 (runs.tsv). Gap: 0:10
- 2: "frame 120, the Developer's wake holds one traceback 34 times, validates on night 117" (commit 353515bd, 13:56)
- 3: frame 120's line (`plans/archive/stack-2026-10-05.md:3`)
- 4: 5 walls.
  - n117-W1: Tester's fix under a new id goes to a new file, 4 of 4 [C8] (guide: frame 123) (source: frame123-read.md:71-74)
  - n117-W2: a door names `ledger.log`, which the challenge set lacks [C9] (guide: frame 126) (source: frame123-read.md:74)
  - n117-W3: `tests.load` block cuts the wake before any code.source [C2] (guide: frame 127) (source: frame123-read.md:108-112)
  - n117-W4: relative-import cycles pass the own-package check, api.py:10751 [C10] (guide: frame 114) (source: frame114-read.md:103-109)
  - n117-W5: no refusal names the batch's own lines or the restore span [C10] (guide: frame 114) (source: frame114-read.md:110-111)
- 5: commit 0d31d56f "the fix goes under a new id and the door offers", 0 min. Fix da7bade1 at 15:45, 18 min
- 6: F123: built before night 118 (c76006db, night118-read.md:3). F126, F127 (pushed 0d31d56f): still open at night 118. F128 (pushed b502f0aa, 16:21): still open at night 118
- 8: n117-W1: not met in n118 (night118-read.md:7), n119 (frame 123 closes). n120: not named.
  n117-W2: n118: not named. Not met in n119 ("Frame 126: 0 of 5", night119-read.md:170). n120: not named.
  n117-W3: n118: not named. Met in n119 as n119-W16: same cause (frame 127 counted). n120: not named.
  n117-W4, W5: n118: not named. n119: not sure (n119-W4, a relative import written back). n120: not sure (n120-W2, frame 136)
- 9: Roman: "investigate this with a sub agent" (2026-10-04 14:18, `plans/stack.md:3740`) and "we have already discussed this, use a subagent to search our decisions logs, etc ie meta" (14:34, `plans/stack.md:3769`). Decided: turned (frame 114 becomes a build frame, 39e3dedf; the brief gains a rule, 5f5385eb)
- 11: frame123-read for 419281dc (frame123-read.md:3). frame114-read by a read-only agent on Opus (frame114-read.md:3)
- 12: stop classes gaveup_nothing 2, pend_behind 1. Not named: both (the reads name the Tester mechanism and the door)

### night 118
- run: start 2026-10-04 16:20, commit c76006db (runs.tsv line 38)
- read pages: `plans/night118-read.md`
- read landed: 2026-10-04 18:00 (5ed6eae3). Run end: 17:50 (runs.tsv). Gap: 0:10
- 2: "frame 123, a Tester's fix replaces the old test, validates on night 118 at c76006d" (commit b502f0aa, 16:21)
- 3: frame 123's line (`plans/archive/stack-2026-10-05.md:19`)
- 4: 3 walls.
  - n118-W1: `tests.load` shows a red inherited test as passing [C6] (guide: frame 130) (source: night118-read.md:136)
  - n118-W2: criterion cr_3 states a false "as before" [C?] (source: night118-read.md:137)
  - n118-W3: Tester encodes product source as a test, 15 calls [C?] (source: night118-read.md:138)
- 5: commit 45b88a8b "frame 130 ... is pushed", 0 min. Fix 78ed2366 at 18:09, 9 min (frame 122)
- 6: F130 (pushed 45b88a8b): still open at night 119 (open in `plans/stack.md:3648`)
- 8: n118-W1: met in n119 as n119-W11, n120 as n120-W6, n121 as n121-W7: same cause (the reads name frame 130).
  n118-W2: n119: not named. n120: not sure (n120-W3, another criterion). n121: not named.
  n118-W3: not met in n119, n120, n121
- 9: the session: "This matches no open frame. It is a new wall" (night118-read.md:8). Decided: continued
- 11: 419281dc holds the stack. Hand-off to e6218d79 at 18:40 (ae2e2a93, 6cebc2d8)
- 12: stop classes gaveup_red 1, pend_behind 1. Named: gaveup_red ("`confirm_default_on_eof_group` was given up"), pend_behind ("the stuck batch holds the queue")

### night 119
- run: start 2026-10-04 18:40, commit 1e878553 (runs.tsv line 39)
- read pages: `plans/night119-read.md`; `plans/night119-read-fable.md`; `plans/night119-compare.md`
- read landed: 2026-10-05 01:25 (343f6d79, all three). Run end: 01:01 (runs.tsv). Gap: 0:24
- 2: "frame 122 ... validates on night 119 with frame 125" (commit ae2e2a93, 18:40)
- 3: frames 120, 122, 123, 125 (commit e9dd1ef8)
- 4: 17 walls. W1 to W5 are in both reads. W6 to W10 are in the Fable read only and "No one has checked these against the database" (night119-compare.md:84-85).
  - n119-W1: swallow refusal names the first argument, quote in a later one [C7] (guide: frame 122) (7.1) (source: night119-compare.md:77-79)
  - n119-W2: test calls a plain function as a Click command, product changes [C3] (guide: frame 131) (7.2) (source: night119-compare.md:80-81)
  - n119-W3: Tester answers a challenge in prose, sends no encode [C8] (guide: frame 132) (7.3) (source: night119-compare.md:82-83)
  - n119-W4: Developer writes back the line it says it removes [C5] (guide: frame 133) (7.4) (source: night119-compare.md:84)
  - n119-W5: large diff block removes the source from the fix wake [C2] (guide: frame 134) (7.5) (source: night119-compare.md:85)
  - n119-W6: cycle door names a fix that is a cycle, s152 [C?] (source: night119-compare.md:89)
  - n119-W7: fix wake's source is CliRunner, not the traceback's file [C?] (source: night119-compare.md:90-91)
  - n119-W8: code.write never ends for three causes [C?] (source: night119-compare.md:92-94)
  - n119-W9: Vision Keeper in propose mode asserts a criterion's words as item [C?] (source: night119-compare.md:95-96)
  - n119-W10: returns-against-prints door refuses a test of an argument [C?] (source: night119-compare.md:97-98)
  - n119-W11: bg_3 wakes show 34 passing project tests as red [C6] (guide: frame 130) (source: night119-compare.md:100-101)
  - n119-W12: made up, 119 turns in 53 sessions [C7] (guide: frame 113) (source: night119-read.md:163)
  - n119-W13: 6 of 6 Architect answers have empty text [C11] (guide: frame 115) (source: night119-read.md:164)
  - n119-W14: 5 of 20 Developer sessions send several challenges in one reply [C8] (guide: frame 116) (source: night119-read.md:165)
  - n119-W15: 51 turns hold a stubbed reply [C7] (guide: frame 117) (source: night119-read.md:166)
  - n119-W16: 6 of 20 fix wakes hold no code.source [C2] (guide: frame 127) (source: night119-read.md:169)
  - n119-W17: 1 of 6 Vision Keeper sessions leaves a new item from a decision [C?] (F129) (source: night119-read.md:171)
- 5: commit 447d0466 "frames 131 to 134 are pushed", 0 min. Fix 9fa6f2cc at 02:01, 36 min
- 6: F131, F132, F133, F134 (pushed 447d0466): still open at night 120. The residue pass of F122 is built before night 120 (be1eb5c, night120-read.md:5)
- 8: n119-W1: not met in n120 ("0 sessions end on a parser refusal with the frame's cause", night120-read.md:13). n120: not sure (n120-W4, frame 137). n121, n122: not named.
  n119-W2: met in n120 as n120-W7 and in n121 as n121-W6: same cause. n122: not named.
  n119-W3: n120, n121: not named. n122: not sure (n122-W2, "Near frame 132").
  n119-W4, W5: not met in n120, n121, n122.
  n119-W6: not met.
  n119-W7: met in n120: same sign at the same place ("the fix wake's source is `CliRunner` in 6 of 6 wakes ... stand again", night120-read.md:171). n121, n122: not named.
  n119-W8: met in n120: same sign ("a Developer's `code.write` never ends for a cause that is not a quote in a quote, s231", night120-read.md:171). n121, n122: not named.
  n119-W9, W10: not met in n120, n121, n122.
  n119-W11: met in n120 as n120-W6 and in n121 as n121-W7: same cause.
  n119-W12 to W17: not found in n120 and n121 (their count sections were not read). Not named in n122
- 9: the session, on the two reads: "The frame's ends-when names the cause, so the frame stays open" (night119-compare.md:41-43). Decided: continued (frame 122 stays open)
- 11: e6218d79 (night119-compare.md:30, its scratchpad)
- 12: stop classes gaveup_red 2. Named: gaveup_red ("bg_1 and bg_3 stalled on one shape", bg_1 parked, bg_3 given up)

### night 120
- run: start 2026-10-05 03:04, commit be1eb5c2 (runs.tsv line 40)
- read pages: `plans/night120-read.md`
- read landed: 2026-10-05 05:05 (ebf763b0). Run end: 04:52 (runs.tsv). Gap: 0:13
- 2: "frame 122 ... validates on night 120 at be1eb5c" (commit 1a572569, 03:04)
- 3: frame 122's line (`plans/archive/stack-2026-10-05.md:56`)
- 4: 7 walls.
  - n120-W1: Tester stores its test under a project test's id [C8] (guide: frame 135) (6.1) (source: night120-read.md:173)
  - n120-W2: span write of one line removes the import lines, door admits [C8] (guide: frame 136) (6.2) (source: night120-read.md:174)
  - n120-W3: criterion holds a behaviour that the request does not hold [C?] (6.3) (source: night120-read.md:175)
  - n120-W4: never-ends refusal names a word that is no parameter [C7] (guide: frame 137) (6.4) (source: night120-read.md:176)
  - n120-W5: revert door says tests pass both ways while all error [C8] (guide: frame 149) (6.5) (source: night120-read.md:177)
  - n120-W6: five of nine fix wakes show a red project test as passing [C6] (guide: frame 130) (source: night120-read.md:16,179)
  - n120-W7: two bg_3 tests call a plain function as a Click command [C3] (guide: frame 131) (source: night120-read.md:15)
- 5: commit f3bd38e9 "frames 135 to 137 are pushed", 0 min. Fix 8151d87b at 05:30, 25 min (frame 121)
- 6: F135, F136, F137 (pushed f3bd38e9): still open at night 121 ("does not hold frame 135's door", night121-read.md:5). F135 is built before night 122 (a71951a)
- 8: n120-W1: not met in n122 ("0 encodes under a project test's id") or n123 ("the door had no case"). n121: not named.
  n120-W2: not met in n123 (night123-read.md:11). n121, n122: not named.
  n120-W3: not met in n121, n122, n123.
  n120-W4: n121, n122: not named. n123: not sure (n123-W3).
  n120-W5: not met in n121, n122, n123.
  n120-W6: met in n121 as n121-W7: same cause. n122, n123: not named.
  n120-W7: met in n121 as n121-W6 and in n123 as n123-W4: same cause. n122: not named
- 9: the session: "frame 121 gets its baseline from night 120" (commit f3bd38e9 subject). Decided: continued
- 11: e6218d79 (night120-read.md:3, its scratchpad). Hand-off to 5101d8d0 at 05:35 (ae481feb, 07fabf01)
- 12: stop classes gaveup_red 1. Named: gaveup_red ("bg_3 was given up for a new cause")

### night 121
- run: start 2026-10-05 05:35, commit 8151d87b (runs.tsv line 41)
- read pages: `plans/night121-read.md`
- read landed: 2026-10-05 09:20 (1e63fd86), after night 122 started at 09:06. Run end: 09:05 (runs.tsv). Gap: 0:15
- 2: "frame 121, two runner notes say what happened, validates on night 121" (commit ae481feb, 05:35)
- 3: frame 121's line (`plans/archive/stack-2026-10-05.md:84`)
- 4: 7 walls.
  - n121-W1: span write ends early, drops the tail, note beside the commit [C8] (guide: frame 140) (6.1) (source: night121-read.md:157)
  - n121-W2: surface door refuses a test importing through the package [C8] (guide: frame 141) (6.2) (source: night121-read.md:158)
  - n121-W3: park ask answer names no option, Liaison asks three times [C10] (guide: frame 142) (6.3) (source: night121-read.md:159)
  - n121-W4: Tester's test asserts a default the function lacks [C2] (guide: frame 143) (6.4) (source: night121-read.md:160)
  - n121-W5: serve cap refusal, then the same call, read loop of two spans [C2] (guide: frame 139) (source: night121-read.md:9)
  - n121-W6: bg_1 test passes a plain function to CliRunner.invoke [C3] (guide: frame 131) (source: night121-read.md:11)
  - n121-W7: 16 of 16 fix wakes show two red project tests as passing [C6] (guide: frame 130) (source: night121-read.md:12)
- 5: commit 6f09e478 "frames 139 to 143 are pushed", 1 min. Fix 08caa8d2 at 09:43, 23 min
- 6: F139, F140, F141, F142, F143 (pushed 6f09e478): still open at night 122, which started before the read
- 8: n121-W1 to W5: not met in n122, n123, n124.
  n121-W6: n122: not named. Met in n123 as n123-W4 and in n124 as n124-W7: same cause.
  n121-W7: not named in n122, n123, n124
- 9: the session: "night 121's read shows no false claim in a note, frame 121 waits on night 122" (commit 6f09e478 subject). Decided: continued
- 11: 5101d8d0 (night121-read.md:3, its scratchpad)
- 12: stop classes gaveup_nothing 1, gaveup_red 2. Named: a give-up ("bg_1 was parked past the attempt cap, bg_2 was given up"; the class of each is not sure)

### night 122
- run: start 2026-10-05 09:06, commit a71951a2 (runs.tsv line 42)
- read pages: `plans/night122-read.md`
- read landed: 2026-10-05 10:00 (7aa9e2e8). Run end: 09:54 (runs.tsv). Gap: 0:06
- 2: "night 122 walks frame 135" (commit d7fba968, 09:07)
- 3: frame 135's line (`plans/archive/stack-2026-10-05.md:110`)
- 4: 3 walls.
  - n122-W1: bg_1 holds the seat at attempt 5, key quarantined, nothing starts [C?] (F87) (source: night122-read.md:7)
  - n122-W2: same-refs door ignores a new version of the test [C8] (guide: frame 145) (source: night122-read.md:61)
  - n122-W3: Tester's v2 test expects a space against the criterion [C?] (source: night122-read.md:8)
- 5: commit 425a41a6 "frame 145 is pushed", 1 min
- 6: F145 (pushed 425a41a6): still open at night 123. Built before night 124 (46b0888f)
- 8: n122-W1: met in n123 as n123-W5, n124 as n124-W6, n125 as n125-W4: same cause (the reads name frame 87).
  n122-W2: n123: not sure (n123-W2). n124: not sure (n124-W1). Not met in n125 ("False refusals: 0 of 11", night125-read.md:9).
  n122-W3: n123: not named. n124: not named. n125: not sure (n125-W1, the same test id, another fault)
- 9: the session: "That is frame 87's open finding of night 100, and not a new wall" (night122-read.md:7). Roman: "The order is fine" (2026-10-05 10:11, `plans/archive/stack-2026-10-07.md:92`). Decided: continued
- 11: 5101d8d0 (night122-read.md:3). Hand-off to c81b16d3 at 10:47 (55e5c18f, e94ba234)
- 12: stop classes gaveup_nothing 1, pend_behind 2. Named: gaveup_nothing (bg_1 "its `tests_failing` key quarantined"), pend_behind ("`tick_batch_start` starts nothing while a batch runs")

### night 123
- run: start 2026-10-05 10:36, commit 467f4b8f (runs.tsv line 43)
- read pages: `plans/night123-read.md`
- read landed: 2026-10-05 12:17 (87d949d0). Run end: 12:03 (runs.tsv). Gap: 0:14
- 2: "night 123 walks frames 135 and 136" (commit 6df57cbf, 10:36)
- 3: frames 135 and 136 (`plans/archive/stack-2026-10-05.md` lines 110, 136)
- 4: 5 walls.
  - n123-W1: constant-assertion door refuses a test that fails with no exception [C8] (guide: frame 147) (6.1) (source: night123-read.md:114)
  - n123-W2: challenge closes as answered when every encode is refused [C8] (guide: frames 132 and 145) (6.2) (source: night123-read.md:115)
  - n123-W3: parser refuses a challenge with no argument named and no step [C?] (6.3) (source: night123-read.md:116)
  - n123-W4: both red tests call a plain function through CliRunner.invoke [C3] (guide: frame 131) (source: night123-read.md:11)
  - n123-W5: bg_1 running at attempt 8, key quarantined, nothing starts [C?] (F87) (source: night123-read.md:13)
- 5: commit 57e64b4d "frame 147 is pushed", 3 min
- 6: F147 (pushed 57e64b4d): still open at night 124 (open in `plans/stack.md:3566`)
- 8: n123-W1: met in n124 as n124-W8 and in n125: same cause ("3 are frame 147's sign", night125-read.md:15). n126: not sure ("Frame 147, 5 constant-assertion refusals", night126-read.md:230).
  n123-W2: n124: not sure (n124-W1). Not met in n125. n126: not named.
  n123-W3: n124, n125: not named. Met in n126 as n126-W18: same sign (`invalid syntax (<unknown>, line 1)`).
  n123-W4: met in n124 as n124-W7 and in n126 as n126-W10: same cause. n125: not named.
  n123-W5: met in n124 as n124-W6 and in n125 as n125-W4: same cause. Not met in n126 ("frame 87, bg_1 was parked and bg_2 started")
- 9: Roman: "Please switch to fable for the non-..." (2026-10-05, `plans/archive/stack-2026-10-05.md:152`, a rule on agents) and "Yeah ok" (12:00, `plans/archive/stack-2026-10-07.md:96`). The session: "night 123's read goes to seven frames" (commit 57e64b4d). Decided: continued
- 11: c81b16d3 (night123-read.md:3)
- 12: stop classes gaveup_red 1, pend_behind 3. Named: gaveup_red ("bg_1 was given up"), pend_behind ("Why bg_2, bg_3 and bg_4 never started")

### night 124
- run: start 2026-10-05 13:42, commit 6afda476 (runs.tsv line 44)
- read pages: `plans/night124-read.md`
- read landed: 2026-10-05 14:57 (d3f4e8e4). Run end: 14:45 (runs.tsv). Gap: 0:12
- 2: "frames 132 and 145 land at 4968ea7 and validate on night 124" (commit 46b0888f, 13:43)
- 3: frames 132 and 145 (`plans/archive/stack-2026-10-05.md` lines 157, 184)
- 4: 9 walls.
  - n124-W1: accepting Tester's answer makes the door refuse the challenge as judged [C8] (guide: frames 132 and 145) (6.1) (source: night124-read.md:147)
  - n124-W2: revert door refuses the repair of a head failing at import [C8] (guide: frame 149) (6.2) (source: night124-read.md:148)
  - n124-W3: refused commit leaves its write, wakes show it beside red output [C14] (guide: frame 150) (6.3) (source: night124-read.md:149)
  - n124-W4: commit lands a decorator whose name the module never binds [C8] (guide: frame 146) (6.4) (source: night124-read.md:150)
  - n124-W5: drops door names `start=0, end=0`, `__future__` door refuses it [C9] (6.5) (source: night124-read.md:151)
  - n124-W6: bg_1 running at attempt 4, key quarantined [C?] (F87) (source: night124-read.md:13)
  - n124-W7: frame 131 stands [C3] (guide: frame 131) (source: night124-read.md:12)
  - n124-W8: frame 147 stands, 4 of 4 encodes refused [C8] (guide: frame 147) (source: night124-read.md:9,12)
  - n124-W9: frame 115 stands [C11] (guide: frame 115) (source: night124-read.md:12)
- 5: commit 9b960262 "frames 149 and 150 are pushed", 0 min. Commit a25f192e, 2 min
- 6: F149 (pushed 9b960262): still open at night 125 (pass 1 at 22:36, 1742c362). Built before night 126. F150 (pushed 9b960262): still open at night 125 (open in `plans/stack.md:3544`)
- 8: n124-W1: not met in n125 (night125-read.md:9). n126, n127: not named.
  n124-W2: not met in n125 ("Frame 149, 0 turns hold `undoing yourself`"), n126 ("0 `code.commit` calls met the revert door"). n127: not named.
  n124-W3: not met in n125, n126 ("Frame 150, 0"). n127: not named.
  n124-W4: not met in n125 ("frame 146, 0 runs in `error`"). Met in n126 as n126-W11: same cause. n127: not named.
  n124-W5: not met in n125, n126, n127.
  n124-W6: met in n125 as n125-W4: same cause. Not met in n126. n127: not named.
  n124-W7: met in n126 as n126-W10 and in n127 (baseline, 3 tests): same cause. n125: not named.
  n124-W8: met in n125: same cause (night125-read.md:15). n126: not sure. n127: not sure ("Not read for a right test refused").
  n124-W9: met in n125 as n125-W10 and in n126 as n126-W15: same cause. n127: not named
- 9: the session: "night 124's read goes to four frames, and frames 149 and 150 are pushed" (commit 9b960262). Decided: continued
- 11: c81b16d3 (night124-read.md:3). Hand-off to 3f72d9cb at 15:17 (9ff0c8ca, d0fcd0fa)
- 12: stop classes gaveup_red 1, pend_behind 3. Named: gaveup_red ("bg_1 was given up at a head that fails at import"), pend_behind ("Why bg_2, bg_3 and bg_4 never started")

### night 125
- run: start 2026-10-05 18:47, commit 18313503 (runs.tsv line 45)
- read pages: `plans/night125-cycle-read.md` (read while the night ran); `plans/night125-read.md`
- read landed: 2026-10-05 19:49 (9f34a048). Cycle read 19:39 (f23baaf0), 6 min before the end. Run end: 19:45 (runs.tsv). Gap: 0:04
- 2: "frame 132's review at 96c5202 holds, the door lands at a2200a7, and night 125 is the walk" (commit 4a2884f5, 18:48)
- 3: frames 132 and 145 (`plans/archive/stack-2026-10-05.md` lines 157, 184)
- 4: 10 walls.
  - n125-W1: Tester's test fails for a fault inside the test, no door sees [C?] (7.1) (source: night125-read.md:237)
  - n125-W2: Tester writes the repair in a code block, no encode, no nudge [C4] (guide: frame 152) (7.2) (source: night125-read.md:238)
  - n125-W3: door says end the session, runner asks for a call [C9] (guide: frame 153) (7.3) (source: night125-read.md:239)
  - n125-W4: the bound's exit ends at frame 87's wall [C?] (F87) (7.4) (source: night125-read.md:240)
  - n125-W5: one-message door held two right challenges back, s146 [C?] (7.5) (source: night125-read.md:241)
  - n125-W6: escalation refusal prints `they answered (answered)` with no answer row [C9] (F154) (7.6) (source: night125-read.md:242)
  - n125-W7: `NOTE ... will not be accepted again` is false for tests.encode [C9] (7.7) (source: night125-read.md:243)
  - n125-W8: quarantine report reached him as a touch page, stock answer approved [C11] (7.8) (source: night125-read.md:244)
  - n125-W9: a door names `msg.challenge_tester`, the bound refuses it [C9] (guide: frame 148) (7.9) (source: night125-read.md:245)
  - n125-W10: Architect answers m74, m75 hold no words [C11] (guide: frame 115) (source: night125-cycle-read.md:166)
- 5: commit 5cad12e1, 0 min. F152 pass 1 runs at 19:51 (d3ae5ede), 2 min, an agent started
- 6: F152: built before night 126 (5eba59c6 22:35, "its commits join the main branch"). F153: built before night 126 (20fa715e 14:08). F154 (pushed 73d10e6a): still open at night 126 (open in `plans/stack.md:3440`)
- 8: n125-W1: n126: not named. n127: not sure (night127-read.md:162, a Tester wrapper declares no argument). n128: not named.
  n125-W2: met in n126 as n126-W8: same cause. n127: not sure (the residue "is frame 152's residue and a new cause", night127-read.md:165). n128: not named.
  n125-W3: met in n126 as n126-W9: same cause. n127: not sure (frame 165, the end step). n128: not named.
  n125-W4: not met in n126 ("Known walls with 0 cases: frame 87"). n127, n128: not named.
  n125-W5: not met in n126, n127, n128.
  n125-W6: met in n126 as n126-W17: same cause ("154 item 6"). n127, n128: not named.
  n125-W7, W8: not met in n126, n127, n128.
  n125-W9: met in n126 as n126-W14, in n127 and n128 (known walls, frame 148): same cause.
  n125-W10: met in n126 as n126-W15: same cause. n127, n128: not named
- 9: Roman: frame 152 "is claimed by 3f72d9cb on Roman's word" (commit d3ae5ede, 19:51), and the claim "on Roman's "Yes" of 21:56" (`plans/archive/stack-2026-10-06.md:13`). Decided: continued
- 11: 3f72d9cb holds frames 132, 145, 144 (6d084cfe). Hand-off "at Roman's word" to 2ba331e1 at 21:56 (55b328dd, 75918de6)
- 12: stop classes gaveup_nothing 1, pend_behind 2. Named: gaveup_nothing ("the tick cap gave bg_1 up at attempt 6"), pend_behind ("bg_2 and bg_3, that stays `pending` behind bg_1")

### night 126
- run: start 2026-10-06 14:32, commit fbe4cc25 (runs.tsv line 46)
- read pages: `plans/night126-read.md`
- read landed: 2026-10-06 16:36 (cc506d32). Run end: 16:09 (runs.tsv). Gap: 0:27
- 2: "night 126 runs on the joined tree at fbe4cc25" (commit a3c7196f, 14:34)
- 3: frames 152, 144, 149, 153, 151 ("The tree joins frames 152, 144, 149, 153 and 151", night126-read.md:3)
- 4: 20 walls. W1 to W7 are new. W8 to W20 are known frames with a case.
  - n126-W1: `problem.prioritize` admits a string, `next_batch` crashes [C8] (guide: frame 164) (9.1) (source: night126-read.md:205)
  - n126-W2: not-Python door of tests.encode names a wrong cause [C9] (guide: frame 166) (9.2) (source: night126-read.md:206)
  - n126-W3: ladder's end relays a batch id to the approve step [C6] (guide: frame 167) (9.3) (source: night126-read.md:207)
  - n126-W4: same-refs step says end while another challenge lands [C9] (guide: frame 168) (9.4) (source: night126-read.md:208)
  - n126-W5: "The answer is in this prompt" after the window dropped it [C9] (guide: frame 169) (9.5) (source: night126-read.md:209)
  - n126-W6: a seat sends one call about a hundred times in one reply [C?] (9.6) (source: night126-read.md:210)
  - n126-W7: 22 reply cuts in 15 sessions [C?] (9.7) (source: night126-read.md:211)
  - n126-W8: frame 152 line not met, 2 of 5 [C4] (guide: frame 152) (source: night126-read.md:7)
  - n126-W9: frame 153 line not met, 1 of 11 [C9] (guide: frame 153) (source: night126-read.md:8)
  - n126-W10: frame 131, 19 commits on bg_1 [C3] (guide: frame 131) (source: night126-read.md:217)
  - n126-W11: frame 146, a module that fails at import [C8] (guide: frame 146) (source: night126-read.md:218)
  - n126-W12: frame 140, a span drops 13 lines [C8] (guide: frame 140) (source: night126-read.md:219)
  - n126-W13: frame 129, an item asserted from a criterion's words [C?] (F129) (source: night126-read.md:220)
  - n126-W14: frame 148, two refusals name a refused call [C9] (guide: frame 148) (source: night126-read.md:221)
  - n126-W15: frame 115, m83 and m93 with no words [C11] (guide: frame 115) (source: night126-read.md:222)
  - n126-W16: frame 116, three challenges in one reply [C8] (guide: frame 116) (source: night126-read.md:223)
  - n126-W17: frame 154 item 6, `they answered (answered)` [C9] (F154) (source: night126-read.md:224)
  - n126-W18: frame 137, parser refusals name a wrong thing [C7] (guide: frame 137) (source: night126-read.md:225)
  - n126-W19: frame 113, 84 turns in 33 sessions [C7] (guide: frame 113) (source: night126-read.md:226)
  - n126-W20: frame 130, `test_light_imports` red from attempt 6 [C6] (guide: frame 130) (source: night126-read.md:227)
- 5: commit 2c89a2ba "frames 164 and 165 record the low question on their start", 2 min
- 6: F164: built before night 127 (978db43a 23:16). F165: built before night 127 (29ae4b17 23:20). F166, F167, F168: still open at night 127 (open in `plans/stack.md` lines 3430, 3421, 3412). F169: still open at night 127 (closed 2026-10-11, `plans/archive/stack-2026-10-11.md:123`)
- 8: n126-W1: not met in n127 ("0 loop crashes on a typed scalar"). n128: not counted. n129: no read.
  n126-W2: met in n127 and n128 (known wall, frame 166): same cause. n129: no read.
  n126-W3: met in n127 and n128 (known wall, frame 167): same cause. n129: no read.
  n126-W4: not met in n127 ("no challenge on another test landed after it"). n128: not named. n129: no read.
  n126-W5: n127, n128: not sure (frame 169's sentence counted, "how many stood after an eviction was not read"). n129: no read.
  n126-W6: not met in n127, n128. n129: no read.
  n126-W7: met in n127 (3 lines) and n128 (7 lines): same sign. n129: no read.
  n126-W8: not met in n127 (the line is met). n127: the residue is "a new cause". n128: not named. n129: no read.
  n126-W9: n127: not sure (frame 165, the end step). n128: not named. n129: no read.
  n126-W10: met in n127 (baseline, 3 tests) and n128 (new wall 3, "The nearest frame is 131"): same cause. n129: no read.
  n126-W11: not named in n127, n128. n129: no read.
  n126-W12: met in n127 (known wall, frame 140): same cause. Not met in n128 ("frame 140's `dropped` note, 0"). n129: no read.
  n126-W13: not named in n127, n128. n129: no read.
  n126-W14: met in n127 and n128 (known wall, frame 148): same cause. n129: no read.
  n126-W15: not named in n127, n128. n129: no read.
  n126-W16, W17, W18: not named in n127, n128. n129: no read.
  n126-W19: met in n127 and n128 (known wall, frame 113): same cause. n129: no read.
  n126-W20: met in n127 and n128 (known wall, frame 130): same cause. n129: no read
- 9: the session: "night 126's read closes frames 149, 151 and 153, and pushes frames 164 to 169" (commit cc506d32). Frames 164 and 165 "start by timeout on the recommended answer" (commit ebed3ae1). Decided: continued
- 11: 2ba331e1 hands off past 300k at 14:34 to 488d31af (a3c7196f, 39f5dbf1). 488d31af hands at 23:55 to 86c3e06e (1915705c, e080a46a)
- 12: stop classes gaveup_nothing 1, pend_behind 1. Named: gaveup_nothing ("bg_1 `deferred` past the cap"), pend_behind ("bg_3 `pending` and next")

## Not found, and why

- Run end of night 86, and the gaps of nights 82 to 86 other than night 85: runs.tsv gives None.
- Column 2 of nights 88 and 115: no commit subject names the run before it started.
- The state of frame 85 and the push of frame 117: no heading or status found by the grep of this pass.
- The count sections of `plans/night118-read.md` (section 5), `plans/night120-read.md` (section 5) and `plans/night121-read.md` (section 5) were not read, for lack of budget. Matches against those sections read "not found".
- Roman's words behind the rulings of commits 0f3816d6, a0974f3e, 8302ed1d, fa8ff072 and 3ee470e0: the subjects say "Roman rules", and this pass did not find the quote.

## Expected answers formed while reading (apart from the turns)

- Many reads land after the next night has started (nights 86, 88, 110, 121). Such a turn cannot change the next run.
- The frame number in a later read seems the most reliable key for column 8. A wall that a read files as "held by no frame" is hard to match.
