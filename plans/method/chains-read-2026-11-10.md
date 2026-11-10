# The walls that came back, and what ended them: the read, 2026-11-10

Written by session 4a1d361a on frame 363, from the brief
`plans/method/chains-read-brief-2026-11-10.md`. The lead and two
sub-agents on Opus read the 41 chains of
`plans/method/turns-list-2026-11-10.md`, section 3, lines 311 to 366, one
time each. The lead checked five blocks of each sub-agent against the
sources. Nobody else read a block twice.

## Result

The counts are over the parts of the blocks. 19 chains split in cell 1, so
the 41 chains hold 64 parts. A chain that did not split is one part.

- **Cell 2, the state at the end.** Open: 18 parts. Ended: 46 parts.
  Cannot tell: 0 parts. By chain: 8 chains are open in every part, 25
  chains are ended in every part, and 8 chains hold an open part and an
  ended part. "Cannot tell" does not occur, because a run in the last
  three runs of a series makes the wall "open" by the brief's rule.
- **Cell 3, the conditions at the end.** "Conditions changed": 32 parts.
  Same: 26 parts. Not applicable, because no run follows dry run 9: 5
  parts. Not sure: 1 part (chain 41, part A).
- **Cell 5, the evidence of the 46 ended parts.** A read confirms with a
  count: 7. A frame closes on a count: 11. Absent only: 28.
- **Cell 4, the changes.** The blocks count 106 changes aimed at the
  chains, summed per chain. A change that aims at two chains counts in
  each, for example frame 258's passes in chains 12 and 35, and the
  rulings door of chain 7 in chain 28. 30 chains had two or more
  changes. 7 chains had none: 6, 8, 9, 13, 15, 19 and 22.
- **Cell 8, the origin, by part.** A frame that answered another wall: 24
  parts. A commit that answered another wall and names no frame: 13
  parts. Rota's first design: 17 parts. Not found: 10 parts. The second
  class is not one of the brief's three answers. The readers found it
  often enough to keep it apart.
- **Cell 1, the splits.** 19 chains split: 2, 6, 8, 11, 12, 14, 20, 25,
  27, 28, 29, 30, 31, 32, 36, 37, 38, 39 and 41. Chains 28 and 41 split
  in three parts. Chain 6 splits in four. The other 16 split in two.
- **Two chains are one sign.** Chain 13 (n156-W10) and chain 2 (n166-W9)
  are the `constraint_zero` quarantine at onboarding. The list does not
  link them, because the reads of nights 161 to 165 hold the key in
  their quarantine rows and not as a wall. Chain 6, part C, is the sign
  of chain 1, "made up". Chain 35 ends at night 151, and its sign comes
  back at night 155 as chain 12, part A.
- **One link of the list does not hold.** Chain 31 joins dry run 5's W10
  to dry run 6c's W5 from a cell that reads "not met". The block splits
  the chain there.

## The limits of this page

These limits hold for every block. They are the brief's, word for word.

- The chains come from one reader and one pass. A firm link is that
  reader's call. Cell 1 is the second look, so do it for every chain.
- A read page is the build session's own account. A wall that no read
  named after a change can still be there.
- The nights share state, and the records hold no pair of equal runs
  with fresh state. So one run without the sign does not show that the
  sign is gone. That is why cell 2 asks for three runs.
- The reads count walls in different ways. Some reads list only new
  walls, nights 127 to 137. A wall that such a read does not name is
  "not named", and not "gone".
- Do not open a database unless a cell needs it. If you must, open it
  with the URI `file:<path>?mode=ro&immutable=1`, so that SQLite writes
  no file beside it. The earlier read wrote `-shm` files with `mode=ro`
  alone.

This read opened no database.

Two more limits come from this pass.

- Cell 2 reads "named" as a wall that a read lists. Some readers also
  took a count row of a tool as a naming. Chain 1 is the case: its
  reader marks it "open", because night 173 still counts "made up" in
  its `nightcount` row. By the wall lists alone, the last naming is
  night 162 (chain 6, part C), and chain 1 is "ended". The tables keep
  the reader's "open" and mark it.
- After a split, most parts hold fewer than four turns. The turn counts
  in the headings are the counts of the joined chain.

## How the page was made

- Part a, chains 1, 3, 4, 5, 10, 16 to 21 and 32 to 35: a sub-agent on
  Opus, 303,866 tokens, 176 tool calls. Its page is
  `plans/method/chains-read-extract-a-2026-11-10.md`.
- Part b, chains 2, 7, 14, 24 to 26, 28, 29 and 36 to 41: a sub-agent on
  Opus, 296,709 tokens, 146 tool calls. Its page is
  `plans/method/chains-read-extract-b-2026-11-10.md`.
- The lead read chains 6, 8, 9, 11 to 13, 15, 22, 23, 27, 30 and 31.
- The blocks below are copied from the three sources in chain order. Each
  block names its reader under its heading. The Row line under each
  block is the reader's own summary.

## The lead's check of ten blocks

The lead read five blocks of each sub-agent against the sources it
names: the read pages, the stack lines, and `git show` or `git log -S`
on the commits.

| Chain | Reader | What the lead checked | Result |
|---|---|---|---|
| 1 | part a | frame 113 at `plans/stack.md`:3707 and "Park it" at :3723; night 173's "Made up 48 turns" at `plans/night173-read.md`:24; c7a228de by `git log -S`; night 146's counts at `plans/night146-read.md`:54-55 | Sources hold. Cell 2 reads a tool's count row as a naming. By the wall lists the chain ends after night 162 (see the limits above) |
| 5 | part a | frame 131 at `plans/archive/stack-2026-10-07.md`:131 and its close at :153; 8234b716, 6b52a09d and 02a25748 by `git show` | Sources hold |
| 17 | part a | frame 117 at `plans/stack.md`:3682; bdaca787's body, "Frame 100. On night 99 s132 ..."; the stub text in the reads of nights 120 and 122 to 124 (1, 0, 0, 0 hits) | Sources hold |
| 20 | part a | f0b2924c, d3154135 and a268266b by `git show`; night 155's row 5 at `plans/night155-read.md`:127 | Sources hold. Part a confirms f0b2924c as frame 250's pass 1, which part b left "not confirmed" |
| 35 | part a | frame 258's status lines of 2026-10-16 to 2026-10-21 in `plans/archive/stack-2026-10-24.md` | Sources hold. The lead's chain 12, part A, reads the same lines from night 155 on |
| 2 | part b | `plans/night166-read.md`:217; e7016e65's body names "frame 354, the first dry run's first wall"; 01e48a6f by `git show` | Sources hold. The lead's chain 13 now takes 01e48a6f as its origin, as chain 2 does |
| 7 | part b | 135c87d1 and 793aa684 by `git show`; "Same. The read-back text ..." at `plans/night172-read.md`:151 | Sources hold |
| 24 | part b | a3f2f96e's body, "Frame 306, pass 1b"; eeb0db69 at 2026-10-28 14:08 and 7f7a6d88 at 16:45 by `git show`; night 174's row at `plans/night174-read.md`:238 | Sources hold |
| 36 | part b | ced9de67 and cc013d96 on night 161's commit, 6862e93b and 970cbd81 on night 163's commit (`git merge-base`); b319696a, frame 312's close; 358fed11; `plans/night160-read.md`:275 | Sources hold |
| 41 | part b | the three parts' walls in extract c; 0b90f02b, a66b9a31 and 40980c59 in the cell; F7 as a fact of frame 344's audit (`plans/archive/stack-2026-10-30.md`:164-174) | Sources hold. Cell 3 of part A reads "not sure". Dry runs 6 and 6b changed the machine: dry run 6 measured the machine, and 6b ran behind a router (`plans/method/turns-list-2026-11-10.md`:386, 388). So part A's next runs changed the kind of run in part |

## The blocks

### Chain 1: n105-W4, 11 turns, firm

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "Vision Keeper writes fake `OK` tool results, 12 sessions [C7] (guide: frame 113, the same shape)" (`plans/method/turns-list-2026-11-10.md`:323). First turn n105, last turn n119, 11 turns: n105, n106, n107, n108, n109, n111, n112, n113, n115, n116, n119. The wall lines in the extract agree: each later wall is "own result lines" or "write own results" with "(guide: frame 113)" (`plans/method/turns-list-extract-a-2026-11-10.md`:296, 319, 342, 378, 408, 448, 469, 493, 532, 557, 634). The sign is one sign: the seat writes an `OK <tool> -> ...` line in its own reply (`plans/night105-read.md`:52). The main seat changes. Night 105 counts 12 Vision Keeper sessions and names the developer `s131` as one other role (`plans/night105-read.md`:52, 64). From night 106 the walls count Developer sessions, 22 on night 106 (`plans/night106-read.md`:46-48 by the extract line 319). The extract calls the link n105 to n106 "not sure (n106-W4, the Developer)" and the link n105 to n107 "same sign" (extract a:303). I keep one block, because the sign and the counter are the same. The night count counts every seat in one line (`plans/night120-read.md`:155). Night 110 had no session (extract a:355). Night 114 is thin. The extract did not read the count sections of nights 117, 118, 120 and 121 (extract a:540, 567, 651).
2. The state at the end: Open. The chain's last firm naming is n119. But the reads after night 119 still count the same sign under frame 113: night 120 "made up: 85 turns, 38 sessions" (`plans/night120-read.md`:155), night 121 163 turns (`plans/night121-read.md`:132), and nights 123, 124, 126 to 128, 130 to 133, 136 to 138 (grep "made up:" over `plans/night1*-read.md`). Later reads name the sign as a wall of another chain: n157-W11 "Made up: 71 turns in 36 sessions" (`plans/night157-read.md`:205), n162-W8 "made up 95 from 148" (`plans/night162-read.md`:335). Night 173, one of the last three runs, counts "Made up 48 turns in 27 sessions" (`plans/night173-read.md`:24). The reads of nights 174 and 175 hold no "made up" line (grep, absence only).
3. The conditions at the end: same, for the chain's own end at n119. Nights 120 to 122 ran the same kind of run on the same repository (extract a:656-708). The sign itself runs on past night 163, when the requests changed, to night 173 (`plans/night173-read.md`:24).
4. The changes:
   - Frame 113, "A Developer writes its own tool results" (`plans/stack.md`:3707). The cause read only: `plans/frame113-read.md`, commits e891bcf5, 0005d227, f7f5c838, d6154b2b (git log --grep "frame 113"). Kind: a rule or a record only. The read found "there was no rise at night 106" and "The form is taught by the prompt itself" (`plans/stack.md`:3722). Roman parked the frame, and no fix ran (`plans/stack.md`:3723, commit fa8ff072). The next read, night 117, counts "17 Developer sessions of 23" (`plans/stack.md`:3724).
   - Frame 232, "The stream stops at the protocol's boundary" (`plans/archive/stack-2026-10-14.md`:5). Commit 56bfe7c5, 2026-10-13 21:30, files `rota/llm/llm.py`, `rota/llm/toolproto.py`, `rota/core/runner.py` and two test files (git show --stat). Kind: other code of rota. The commit keeps the account line "wrote its own tool results" word for word, "so the count of the sign stays comparable" (56bfe7c5 body). Night 146 read: "fabricated tokens 1.1k in the walks and 1.2k over the night against 158k", and "0 end on an invented result, against 12" (`plans/night146-read.md`:54-55). The frame closes on night 146 on those counts (`plans/archive/stack-2026-10-14.md`, status 2026-10-14 07:21). The read does not say the sign fell. Later nights still count it, for example night 148 to 173 (cell 2).
   Count: 2.
5. The last change before the end: not applicable, the chain is open. Evidence: not applicable.
6. The place of the changes: the sign shows in the seat's reply. The frame 113 read places the cause in the prompt, `user = "\n\n".join(transcript)` at `rota/core/runner.py:2831` (`plans/frame113-read.md`:42). Frame 113 changed no file. Frame 232 touches another place: the stream reader `_consume_stream` in `rota/llm/llm.py` and the regex `INVENTED_RESULT` in `rota/llm/toolproto.py` (`plans/archive/stack-2026-10-14.md`, status 2026-10-13 21:32). It does not touch the prompt join.
7. Who started each change: frame 113 came from a read of a run, night 106's count, "Batch C, the night's stall, found by night 106's count" (`plans/stack.md`:3709). Roman parked it: "Park it" (`plans/stack.md`:3723). Frame 232 came from a read, `plans/night-reuse-investigation-2.md` of night 145, and Roman's words "cutting of the responses, this needs to be done intelligently" and "Ok" on the plan (`plans/archive/stack-2026-10-14.md`:7, 10).
8. The origin: the sign is the model's text. The frame 113 read names the prompt layout as the teacher: the transcript joined with blank lines and no frame, `rota/core/runner.py`, the transcript join (`plans/frame113-read.md`:42). `git log -S '"\n\n".join(transcript)'` gives c7a228de, 2026-08-09, "feat(runner): session runner, model seam, cassettes, and a synthetic arc". The detector `FABRICATED_RESULT` came in feb11d3f, 2026-08-11, "fix(sandbox): the session that argued with itself for twelve turns". The runner's cut, "NOT RUN, because you wrote a tool result", came in 5f27b85c, 2026-09-23, frame 77 (git log -S). Origin class: rota's first design.
9. After the end: the chain is open. In the three reads after n119, nights 120 and 121 count the same sign under its own frame, 113 (`plans/night120-read.md`:155, `plans/night121-read.md`:132). The extract says "Not named in n122" (extract a:651).

Row: Open | same | 2 | not applicable | rota's first design | origin frame: none

### Chain 2: n166-W9, 10 turns, firm

Reader: sub-agent, part b (`plans/method/chains-read-extract-b-2026-11-10.md`).

1. The wall: "the constraint tick quarantines at onboarding [C?] (W-I)" (`plans/method/turns-list-2026-11-10.md:324`; `plans/night166-read.md:217`). First turn night 166, last turn night 175, 10 turns. The chain holds two signs, so this block splits it.
   - Part A, the key `-|tick:constraint_zero|` at 3 at onboarding, and s1's refused report of it. n166-W9, n167-W12, n168-W11, n169-W8 name the key only (`plans/night167-read.md:105`, `plans/night168-read.md:114`, `plans/night169-read.md:69`). n170-W14 and n171-W14 name the key and s1's refusal on the ref 'tick: quarantined' (`plans/night170-read.md:70`, `plans/night171-read.md:71`). n172-W11, n173-W4 and n174-W11 name the refusal only: "refs are ids, and 'tick: quarantined' is not one" (`plans/night172-read.md:68`, `plans/night173-read.md:61`, `plans/night174-read.md:70`). Turns n166 to n174, 9 turns. From night 173 the key itself is a wall of its own, n173-W3, n174-W10, n175-W13, which is chain 26.
   - Part B, the onboarding claim tick `critic|tick:challenge|@claim:constraints:argument` that quarantines with no verdict. n172-W10, n173-W2, n174-W9, n175-W12 (`plans/night172-read.md:67`, `plans/night173-read.md:59`, `plans/night174-read.md:68`, `plans/night175-read.md:68`). Turns n172 to n175, 4 turns. The key is absent from night 171's quarantine line (`plans/night171-read.md:22`). The night 172 read itself links W10 to night 171's W14 as "Same key family" (`plans/night172-read.md:155`). The key, the seat and the sign differ, so the parts are two walls.
   - The same sign as Part A is older than the chain. n160-W8 names "`constraint_zero` quarantine at onboarding, a fifth night" (extract b, night 160, item 4), in the firm chain of n156-W10 (list line 335). The night 166 read says "The same key at 3 on nights 164 and 165" (`plans/night166-read.md:217`). The reads of nights 161 to 165 list no such wall, so no link joins the two chains.
2. The state at the end:
   - Part A: Open. Night 174, one of the last three runs of the night series, named it (n174-W11). The key itself is named at night 175 and at dry1 (chain 26).
   - Part B: Open. Night 175, the last run of the night series, named it (n175-W12).
3. The conditions at the end:
   - Part A: the nights stopped after night 175 (Roman, 2026-10-29 01:53, extract c, night 175, item 9). The next run is dry1, a dry run with the session in the Principal seat and a 40-step cap. Dry1 ran on click, the same repository as the nights (`plans/archive/stack-2026-11-02.md:195`, "dry1 on click"; `plans/dry1-first-wall-read-2026-10-31.md:5`). The kind of run changed. Conditions changed.
   - Part B: the last naming is night 175, the last night. The next three runs are dry1, dry2 and dry3, another kind of run, and dry2 and dry3 run on other repositories (extract c, dry2 item 2, dry3 item 2). Conditions changed.
4. The changes:
   - Part A, change 1. F20 with F21, sprint 28 row 1, "the root fix by frame 344's audit", a fact of frame 330. Commits ba128953, b2762648, a7127d41 on f20root, landed by merge 82d426c4 at 2026-10-27 16:48 (`plans/archive/stack-2026-11-02.md:108-112`; git log). Files and names: `scheduler.quarantined_keys`, `key_parts`, the lift in `db.write_state`, and the word tables through `TICK_WORDS` and `_gave_up_words` (`plans/f1-f15-f21-night172-read.md:124`). Kind: other code of rota. The night 170 read places W14 under F21 (`plans/night170-read.md:142`). The audit's proposal for F20 names "the constraint tick at onboarding (nights 160, 166 to 170)" as night evidence that should "go to 0 over 3 nights" (`plans/rootfix-audit-2026-10-27-b.md:42`). The build's status lines name b_3's stop on `tests_missing`, not the constraint tick. The next read: night 172's W11 has "Same text as night 171's W14: \"'tick: quarantined' is not one\"", 6 refusals in s1 and s84 (`plans/night172-read.md:68`, `:156`). Night 173 counts 12 refusals, night 174 counts 6.
   - Part A, change 2. Frame 354, commit e7016e65 at 2026-10-31 17:27, "fix(onboarding): constraint zero settles, and a quarantine report is never an empty page". Files: `rota/core/predicates.py`, `rota/onboarding/boot.py`, `rota/core/scheduler.py`, `rota/roles/api.py`, `rota/roles/principal.py`, `rota/core/sandbox.py` (git show). Kind: other code of rota, and a door that refuses a present with no refs. The commit message: "boot.coded_areas is now the one definition of an area with code", and "a quarantined key that reaches no row now travels as its own ref". Its own measure: "constraint zero fired twice with refs and was never quarantined" on a cold run of click at 2c8cd3a. This change answers dry1-W2 and dry1-W3, after the night series.
   - Not counted: frame 326's pass 1d of 2026-10-26 00:49 makes the test fixture's chain offer no `tick:constraint_zero` (`plans/stack.md:2332`). Its aim is the fixture state, not the night.
   - Part A count: 2.
   - Part B, change 1. F20 with F21, the same commits as Part A change 1, built before night 172. The night 172 read places W10 under F20 and F21: "The words \"could not check a claim for argument\" now reach the end print" (`plans/night172-read.md:155`). Sprint 33 row 6 keeps the wall as "A count until a fix of F20's lift covers it" (`plans/stack.md:305-307`). Status lines of 2026-10-28 12:34 and 17:08 count it on nights 174 and 175, "no held frame's site" (`plans/archive/stack-2026-10-30.md:349`, `:387`). No change after F20 aims at it (absent only: grep of `plans/stack.md` and the archives for "claim tick" and "constraints:argument").
   - Part B count: 1 (F20 with F21, by the read's placement).
5. The last change before the end: not applicable. Both parts are open.
6. The place of the changes:
   - Part A: the sign shows in the scheduler step `-|tick:constraint_zero|` (the predicate `constraint_zero` in `rota/core/predicates.py` and `refresh_constraint_zero` in `rota/onboarding/boot.py`, `plans/dry1-first-wall-read-2026-10-31.md:26`), and in the Liaison's call `present_principal` refused by the ref check. Change 1 touches the key readers in `rota/core/scheduler.py` and the word tables in `rota/roles/principal.py`. It does not touch the predicate or the refresh. Change 2 touches the predicate, the refresh, the send door and the page renderer, so it touches the place of the sign.
   - Part B: the sign shows in the Critic's `tick:challenge` sessions on the claim and in the key's quarantine. Change 1 touches the key readers and the words, another place.
7. Who started each change:
   - F20 with F21: frame 344's audit, which started on Roman's message of 2026-10-27 14:08: "a few sessions ago we analyzed the completed frames and found that many did not fix the root cause. Go back and review them" (extract c, night 170, item 9). It is sprint 28 row 1 (`plans/archive/stack-2026-11-02.md:108`).
   - Frame 354: a read of a run, `plans/dry1-first-wall-read-2026-10-31.md`, pushed in commit a79fd411.
8. The origin:
   - Part A. The predicate `constraint_zero` exists from 210649a7 (2026-08-09, "feat(scheduler): schema, atomic session commit, scheduler and boot"). The dry1 read gives the cause: the predicate wants every area of `code_index`, and the refresh binds only areas with `grain_kind = 'symbol'` (`plans/dry1-first-wall-read-2026-10-31.md:26-27`, reasoned, not replayed). `git log -S "grain_kind = 'symbol'"` on `rota/onboarding/boot.py` gives 01e48a6f (2026-09-08). Its message: "Constraint zero bound every indexed area, including areas of pure prose ... k0 now binds only to areas with symbol grains". It answers a wall of a cold walk on tipsC, 2026-09-04, and names no frame. The refusal text "refs are ids" comes from f73a7c01 (2026-08-14, "fix(sandbox): refs are ids, and the sandbox now knows what an id looks like"). Origin class: a fix that answered another wall, the prose-only walk of 2026-09-04, frame not found.
   - Part B. The predicate is `challenge` at `rota/core/predicates.py:2467-2472` (`python -m rota.tools.map fn challenge`). The `@claim:` refs come from 99774be3 (2026-08-24, "feat(sandbox): v2 stage 9 -- the understanding pipeline gets its adversarial reader"). No record says why the key first quarantines on night 172. Origin class: rota's first design for the predicate. The cause of the start at night 172 is not found.
9. After the end: not applicable for open parts. For Part A, the key is named after night 174 as n175-W13 and dry1-W2 (chain 26). For Part B, dry1 to dry3 name no claim tick (extract c, dry1 to dry3, item 4). The dry1 read says "Nights 173 and 175 repeat this at s84 for a Critic quarantine" (`plans/dry1-first-wall-read-2026-10-31.md:36`). Not sure.

Row (Part A): Open | conditions changed | 2 | not applicable | prose walk fix | origin frame: none
Row (Part B): Open | conditions changed | 1 | not applicable | first design predicate | origin frame: none

### Chain 3: n106-W5, 7 turns, firm

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "inherited failing test has no route, "has no criterion" [C10] (guide: frame 114)" (`plans/method/turns-list-2026-11-10.md`:325). First turn n106, last turn n113, 7 turns: n106, n107, n108, n109, n111, n112, n113. The wall lines agree on one frame, 114, for six walls (extract a:320, 343, 377, 447, 468, 494). One wall differs: n109-W2, "Developer makes a helper a Click command, import breaks the batch [C3] (guide: frame 131, the same sign)" (extract a:402). The read of night 109 files it under "New, held by no frame" (`plans/night109-read.md`:70-73). The extract joins n109-W2 to n111-W4 by "same sign at the same place (bg_2 dead since 3449fcca)" (extract a:413), and night 111 calls the shape "frame 114's shape" (`plans/night111-read.md`:87-95). The signs move along the chain. Night 106 names a challenge that "a challenge cannot reach, "has no criterion"" (`plans/night106-read.md`:43). Nights 107 to 113 name a batch that broke its own project file and doors that refuse the repair (extract a:343, 447, 468, 494). Frame 114 joins the two: "a broken project test is the Developer's own regression" (`plans/stack.md`:3737). I keep one block on that record. A reader who splits it puts n106-W5 alone.
2. The state at the end: Ended. The last naming is n113. Night 114 is thin and has no read, so it does not name the wall. Night 115: "No inherited or project test failed" (`plans/night115-read.md`:81 by extract a:477). Night 116 does not name it (`plans/night116-read.md`:59 by extract a:504). So three runs after n113, nights 114, 115 and 116, do not name it, and one of them, night 114, is thin.
3. The conditions at the end: same. Nights 114 to 116 ran on the same repository and requests (extract a:504-567). The nights stop at 175 and the requests change at 163, both far later.
4. The changes:
   - Frame 114, records only, 2026-10-02 to 2026-10-04: the push, the history read of 2026-10-02 19:05, the refused-repairs read `plans/frame114-read.md` of 2026-10-04 14:25, and the turn to "a build frame on two doors" (`plans/stack.md`:3734-3745; commits 89e4cb83, b32ae800, 53a4da40, 39e3dedf). Kind: a rule or a record only. The reads of nights 107 to 113 name the wall again after each status line (cell 1). The two doors, the cycle check on relative imports and the refusal that quotes the restore span, were never built. At HEAD `_own_package_import` still reads `node.level == 0` alone for the written file (`rota/roles/api.py`:29925, absence of a later change by `git log -S "_own_package_import"`, which finds code only in 13c39b3b).
   - Frame 220, after the end: 21f0e7b0 and d2ffdfe3, 2026-10-17, "the baseline holds the reaches of the working file and of the file at the batch's base commit" (git log --grep "frame 220"). Kind: a door. It aims at night 154's b4 restores, which frame 114 calls "its strongest case" (`plans/stack.md`:3746, 3748).
   - Frame 286, after the end: b0dbd926, 2026-10-18 00:13, "the unnamed-definition door records a stray for the Architect in place of its refusal", then 73c40121, 64fa6b6a (git log --grep "frame 286"). Kind: a door. Frame 114 names it: "the unnamed-definition door is frame 286, pushed" (`plans/stack.md`:3749).
   - Frame 114 build 2, after the end, 2026-11-10: 62c86178, bebae782, 3e673298, 91fc5e27, af678b27, b74c8d9f in the checkout `rota_p183` (`plans/stack.md`:3752-3755). Kind: a door and a prompt. It aims at dry run 8's W5, a base-red test that became a question (`plans/stack.md`:3750-3751), and no run has read it yet.
   Count: 4. One falls before the end, and it is a record only.
5. The last change before the end: frame 114's history read and its revised recommendation of 2026-10-02 19:05, a record only (`plans/stack.md`:3737). No code changed before the end. Evidence: absent only. Night 115 had no failing project test (`plans/night115-read.md`:81), and no record says why the shape did not come back.
6. The place of the changes: the sign shows in `code.write` and its doors in `rota/roles/api.py`: the unnamed-definition door, the drops door, and `_own_package_import` (`rota/roles/api.py`:29885), and in the challenge refusal "has no criterion" (`plans/stack.md`:3729 names `_challenge_evidence` in `rota/core/sandbox.py`). Frame 114's records touch no file. Frame 220 touches the fence (`rota/core/fence.py` by the frame's words, "fix(fence)"), another place. Frame 286 touches the unnamed-definition door, the same place as the sign of night 107 (b0dbd926 subject). Frame 114 build 2 touches the clarify door and the escalation door, another place (`plans/stack.md`:3752).
7. Who started each change: frame 114 came from a read of a run, night 106 (`plans/stack.md`:3730, "pushed by eca94a44"). Roman asked twice: "investigate this with a sub agent" (2026-10-04 14:18) and "whats the question here?" (2026-10-04 14:28) (`plans/stack.md`:3743, 3745). Frame 220 and frame 286 came from the read of night 154 and a row of sprint 12 (`plans/stack.md`:3746, 3748). Frame 114 build 2 came from the root read of the dry runs and a ruling: "Moved to the front by C77 (ruled: Roman, 2026-11-08)" (`plans/stack.md`:3750).
8. The origin: three doors of `code.write` and the challenge door produce the sign. The unnamed-definition door came in 04325814, 2026-09-14, "fix(desks): a definition no criterion names keeps its source", which answered click nights 47 and 48, "plans/wake-audit.md, finding 47" (git show). The own-package check came in 13c39b3b, 2026-09-14, after "Click night 51", finding 51 (git show). The challenge text "has no criterion" first shows in rota code at f4d7d4fc, 2026-09-14, which answered night 47, "finding 46" (git log -S, git show). No frame number is in those commits. Origin class: a frame that answered another wall: frame not found, wall: wake-audit findings 46, 47 and 51 of click nights 47 to 51.
9. After the end: yes, under other names, at the same place. Night 117's turn holds n117-W4, "relative-import cycles pass the own-package check, api.py:10751", and n117-W5, "no refusal names the batch's own lines or the restore span", both "(guide: frame 114)" from `plans/frame114-read.md`:103-111 (extract a:585-586). Later, night 154's n154-W3 names "the dynamic-import door on a restore, frame 220" (extract b:569).

Row: Ended | same | 4 | absent only | doors of night 47 | origin frame: none

### Chain 4: n108-W7, 6 turns, firm

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "all ten Architect answers have empty body_text [C11] (guide: frame 115)" (`plans/method/turns-list-2026-11-10.md`:326). First turn n108, last turn n119, 6 turns: n108, n109, n112, n113, n116, n119. Every wall line names an Architect answer to a Developer with no text and "(guide: frame 115)" (extract a:376, 409, 470, 495, 560, 635). The chain is one wall. The extract did not read the count sections of nights 120 and 121 (extract a:651).
2. The state at the end: Ended, with a later end than the chain shows. The reads after n119 name the same sign under frame 115: night 120 "1 of 1 Architect answers to a Developer has no text, m125" (`plans/night120-read.md`:156), night 121 "9 of 9" (`plans/night121-read.md`:133), night 123 "3 of 3" (`plans/stack.md`, frame 115 status 2026-10-05 12:19), night 124 "1 of 1 answers" (`plans/night124-read.md`:100), night 125 m74 and m75 "with no words" (`plans/night125-read.md`:79), night 126 "m83 and m93, `body_text` is null" (`plans/night126-read.md`:222), night 138 m241 and night 139 m140 and m156 (frame 115 status lines 2026-10-10 14:12 and 2026-10-11 00:30, `plans/stack.md`, the block from line 3757). Nights 127 to 137 list only new walls, so their silence is "not named". After night 139, night 140 says "No answer to a Developer was written" (`plans/night140-read.md`:61), night 141 says "0 escalations" (`plans/night141-read.md`:61), and night 142 names wordless answers of the Vision Keeper to the Tester only (`plans/night142-read.md`:134-140). So three runs after the last naming, nights 140 to 142, do not name an Architect answer to a Developer with no words.
3. The conditions at the end: same for the kind of run, the repository and the requests. Night 140 launched from 3f2e974e, after frame 200's pass 2 (extract b:259). Nights 140 and 141 held no escalation case for the Architect (`plans/night141-read.md`:61), so the condition that shows the sign did not occur.
4. The changes:
   - Frame 115, "The Architect's answer to an escalation carries no words" (`plans/stack.md`:3757). Records only, 2026-10-02 to 2026-10-07: the push, the history reads, "a build frame inside law 2" (commits 6e5ac96d, 50fe35ab, b1225823, 69278835, 9bf3ec48, ac5ea699). Kind: a rule or a record only. The reads of nights 109 to 139 name the sign again after it (cell 2).
   - Frame 200, passes 2 and 2b: 8d090e2e, 2026-10-11 14:41, "a wordless reply is stamped unresolved, a decision row routes an escalation, and the answer wake shows its cause", with 2cec6bb9, 8558e96c and 3f2e974e the same day (git log --grep "frame 200"). Files: `rota/core/predicates.py`, `rota/core/runner.py`, `rota/core/sandbox.py`, `rota/roles/api.py`, `rota/roles/prompts/architect/escalate.md`, `rota/roles/prompts/developer/answer.md`, `answer.tools` (git show --stat). Kind: a door and a prompt of a seat. The commit says the two new cases "read 1 of 5 and 2 of 5 on qwen3:8b" (8d090e2e body). Frame 115 waits on this pass (`plans/stack.md`, frame 115 Waits-on line, "added 2026-10-11 06:11 by 84ce0759"). The next read, night 140: "No answer to a Developer was written. Six answers to Tester questions carry refs and no words" (`plans/night140-read.md`:61).
   Count: 2.
5. The last change before the end: frame 200's pass 2, 8d090e2e and 3f2e974e, 2026-10-11. Evidence: absent only. Nights 140 and 141 had no Architect answer to a Developer, "The answer-mode door and the three-ref hint had no case" (`plans/night141-read.md`:61). No read gives a count of answers with words.
6. The place of the changes: the sign shows in the message row of `msg.answer_developer(refs, round_no=0)`, whose binder in `rota/core/sandbox.py` says "There is no prose field on" purpose (`rota/core/sandbox.py`:3760), and in the edge `architect -> developer: answer` of `rota/design/graph.json` (`plans/stack.md`:3759). Frame 115 changed no file. Frame 200's pass 2 touches the same file, `rota/core/sandbox.py`, and adds the receipt stamp and the refusal of an answer that adds no row. It leaves the channel without words and adds the row route in the Architect's brief and the Developer's answer wake (8d090e2e body).
7. Who started each change: frame 115 came from a design review of a frame, "found by frame 111's design review" (`plans/stack.md`:3759). Roman answered "investigate our decisions, previous thoughts etc" and "we have already discussed this, use a subagent to search our decisions logs, etc ie meta" (frame 115 status 2026-10-04 14:20 and 14:38). Frame 200 came from its scope read, "on the scope's count of 10 of 10 wordless answers over three batches" (`plans/frame200-design.md`, change 4, by frame 115's Waits-on line).
8. The origin: the channel `msg.answer_developer` with refs and no words. `git log -S "answer_developer"` gives 9a109336, 2026-08-09, "feat(prompt): prompt layer, client seam, validators, cockpit". The history read ties the form to law 2 of 2026-08-09, "conclusions travel, reasoning stays home" (`plans/stack.md`, frame 115 status 2026-10-02 19:05). Origin class: rota's first design.
9. After the end: yes, the same sign with other seats. Night 140: "Six answers to Tester questions carry refs and no words: m158, m161, m169, m171 by the Terminologist, and m166, m172 by the Vision Keeper" (`plans/night140-read.md`:61). Night 142: "The Vision Keeper's answers carry no words", m391 and m397 (`plans/night142-read.md`:134-140). Frame 131's read had named the same class on the Terminologist on nights 119 to 126 (frame 115 status 2026-10-07 01:10).

Row: Ended | same | 2 | absent only | rota's first design | origin frame: none

### Chain 5: n119-W2, 6 turns, firm

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "test calls a plain function as a Click command, product changes [C3] (guide: frame 131) (7.2)" (`plans/method/turns-list-2026-11-10.md`:327). First turn n119, last turn n126, 6 turns: n119, n120, n121, n123, n124, n126. Every wall line names a test that passes a plain function to `CliRunner.invoke` and "(guide: frame 131)" (extract a:624, 669, 695, 735, 761, 827). The chain is one wall. Night 122 holds the same cause by frame 131's status, "the cause is this frame's", and the extract says "n122: not named" (`plans/archive/stack-2026-10-07.md`:139; extract a:643). Night 127 names it as the baseline with no id, "3 tests stored on bg_1 pass the bare imported `echo_json` to `CliRunner.invoke`" (`plans/archive/stack-2026-10-07.md`:148; extract a:849).
2. The state at the end: Ended. The chain's last naming by id is n126, and night 127 names the sign as the baseline. Night 128 counts "Stored tests on bg_1 that pass a bare imported name to `.invoke`: 0 of 4, from 3 of 3 on night 127, and 0 night-wide" (`plans/archive/stack-2026-10-07.md`:153). Night 129 is thin and has no read. Night 130 shows the door's refusal and "The seat stored 2 tests at t3 that read stdout through `redirect_stdout`" (`plans/night130-read.md`:15). So three runs after night 127, nights 128, 129 and 130, do not name the sign, and one of them, night 129, is thin.
3. The conditions at the end: same. Nights 128 to 130 ran on the same repository, the same requests and the same kind of run. Night 128 ran the same Tester prompt hash, "byte-identical to night 127 through turn 3" (`plans/archive/stack-2026-10-07.md`:153).
4. The changes:
   - Frame 131, "A test calls a plain function as a Click command, and the Developer changes the product to fit" (`plans/archive/stack-2026-10-07.md`:131). The cause read `plans/frame131-read.md`, then pass 1 52db6bc4, pass 2 d8dd62cd and test lines af7316d4 on the branch `f131`, joined on `rota/foundation` as 68d1f6eb to 02a25748 on 2026-10-07 (`plans/archive/stack-2026-10-07.md`:144-149). File: `rota/roles/api.py`, `tests_encode`. Kind: a door. Night 128's read: "the door refused 8 encodes in 2 sessions", "0 of 4, from 3 of 3 on night 127" (`plans/archive/stack-2026-10-07.md`:153).
   Count: 1.
5. The last change before the end: frame 131's door, joined at 02a25748 before night 128 (`plans/archive/stack-2026-10-07.md`:149-151). Evidence: a frame closes on a count. The frame closes on "0 of 4, from 3 of 3 on night 127, and 0 night-wide" (`plans/archive/stack-2026-10-07.md`:153). The night shares state with night 127 and ran the same prompt hash, so the pair is close to equal at the Tester's turns 1 to 3, but one night only.
6. The place of the changes: the sign shows in the tests that the Tester stores through `tests.encode`, `tests_encode` in `rota/roles/api.py`:11881, and then in the Developer's product change. Frame 131 touches the same file and function, a new door in `tests_encode` (`plans/archive/stack-2026-10-07.md`:144).
7. Who started each change: a read of a run, "found by night 119's two reads" (`plans/archive/stack-2026-10-07.md`:133). The frame was "claimed by 86c3e06e on Roman's order of 00:55" (`plans/archive/stack-2026-10-07.md`:142). His words are not found in the block.
8. The origin: the cause read names the trigger as the prints door of `tests_encode`. It "refused the direct call twice, s131 and s137, with the fact and no route" (`plans/archive/stack-2026-10-07.md`:143). That door came in 8234b716, 2026-09-13, "a test that uses a printing surface's return value logs the assumption", beside the docs commit 878c06ad about "night 28 ... the return-value assumption" (git log -S "and the criterion" on `rota/roles/api.py`). The refusal lost its route in 6b52a09d, 2026-09-15, "the encode door keeps the print fact and drops the capsys recipe", on "Roman's call" after "Night 80's Tester wrote the shape it was handed" (git show). The read also names the mode: "the `tests_missing` mode has no `code.source`" (`plans/archive/stack-2026-10-07.md`:143). Origin class: a frame that answered another wall: frame not found, wall: night 28's return-value assumption, and night 80's Tester shape for the cut of the route.
9. After the end: yes, at the same place under another name. n128-W3: "frame 131's door does not read a local def under a decorator factory" (extract b:42). Frame 131's close calls it "a third shape the door's predicate does not read ... and it is frame 176" (`plans/archive/stack-2026-10-07.md`:153). Night 127 also named "A second shape beside it: the Tester's own wrapper command declares no argument" (`plans/archive/stack-2026-10-07.md`:148).

Row: Ended | same | 1 | frame closes count | night 28 door | origin frame: none

### Chain 6: n157-W9, 6 turns, firm

Reader: the lead.

1. The wall: "turns after "Your work for this session is complete" [C?] (W9)" (`plans/method/turns-list-2026-11-10.md`:328). First turn night 157, last turn night 162, 6 turns. The chain is not one wall. It joins four standing counts of the night tools: the turns after the end line, the window drops with the dangling pointers, the turns that the model made up, and the repeats. Night 157 names them as four walls, W9 to W12 (`plans/night157-read.md`:203-206). Night 158 names them as W8 to W11 (`plans/night158-read.md`:209-212). Nights 159 and 160 put all four in one row, W9 (`plans/night159-read.md`:224, `plans/night160-read.md`:279). Nights 161 and 162 name the window, the end line, made up and dangling in one row, and no repeats (`plans/night161-read.md`:290, `plans/night162-read.md`:335). So the block splits in four parts. Part A: the turns after the end line, nights 157 to 162, 6 turns. Part B: the window drops and the dangling pointers, nights 157 to 162, 6 turns. Part C: made up, nights 157 to 162, 6 turns. Part D: repeats, nights 157 to 160, 4 turns. Part C is the sign of chain 1 (n105-W4, cause 7, "made up").
2. The state at the end: Ended, for each part. Parts A, B and C: the last naming is night 162. Nights 163, 164a and 164 do not name them. Night 164a has no read page. Part D: the last naming is night 160. Nights 161, 162 and 163 do not name it as a wall. The signs are still counted after the end. The reads of nights 166 to 175 carry a `nightcount` row with made up, dangling pointers and repeats, and do not call it a wall (`plans/night166-read.md`:50, `plans/night175-read.md`:27). The reads of nights 163 to 165 hold no such count (grep "window drop", "made up", "dangling" on the three pages: 0).
3. The conditions at the end: conditions changed. The requests changed at night 163, the first run after the last naming of parts A, B and C (`plans/method/turns-list-2026-11-10.md`:96-100). Part D ends at night 160, and nights 161 to 163 hold the R1 requests until night 163.
4. The changes: no change aimed at these signs in the window from night 157 to night 163. Each read says "Not read" or "Not read further" (`plans/night157-read.md`:203-206, `plans/night161-read.md`:290, `plans/night162-read.md`:335). The reads point the window signs to frames 139 and 208. Frame 139 has one status line, 2026-10-05 09:21, "Unclaimed" (`plans/stack.md`:3592-3598). Frame 208 is "parked at night 158's read" on 2026-10-21 16:23 (`plans/stack.md`, frame 208's last status line). This cell rests on absence alone. Count: 0.
5. The last change before the end: none. Evidence: absent only. No read after night 162 says that a count fell. The `nightcount` rows of nights 166 to 175 show the counts go on.
6. The place of the changes: not applicable, no change. The places of the signs: part A, the end line in `rota/core/runner.py`, about line 6819; part B, the eviction notice `_EVICTED_PHRASE` in `rota/core/runner.py`, line 1462; parts C and D, the turns of the seats, counted by `rota/tools/nightcount.py`.
7. Who started each change: not applicable.
8. The origin: Part A: the text "You have sent your message. Your work for this session is complete" in `rota/core/runner.py` (about 6819) comes from c7a228de, 2026-08-09, "feat(runner): session runner, model seam, cassettes, and a synthetic arc" (`git log -S`). Origin class: rota's first design. Part B: the text "dropped to fit the window" comes from 5c76af2c, 2026-08-11, "fix(sandbox): the result cap fixed one turn and broke the next three" (`git log -S`). The commit names no frame. Origin class: rota's first design (a commit of 2026-08-11 with no frame). Part C: the sign is a tool result that the model writes. The counter is `rota/tools/nightcount.py`, 2b60571e, 2026-09-23. The code that admits the sign is the runner's parser, which chain 1 reads. Origin class: not found in this block. Part D: the repeats counter is `_repeats` in `rota/tools/nightcount.py`. The reads place no site that runs a repeat. Origin class: not found.
9. After the end: not sure. The read of night 165 names "The walk-3 end line names a stale guess key" (`plans/night165-read.md`:185). That is the end line of a page, another sign. The reads of nights 163 and 164 name no wall at the runner's end line or the window.

Row: Ended | conditions changed | 0 | absent only, counts continue | A, B first design; C, D not found | origin frame: none

### Chain 7: n170-W6, 6 turns, firm

Reader: sub-agent, part b (`plans/method/chains-read-extract-b-2026-11-10.md`).

1. The wall: "the Liaison's `rulings.rule` is refused before it lands [C?] (W6, F2)" (`plans/method/turns-list-2026-11-10.md:329`; `plans/night170-read.md:62`). First turn night 170, last turn night 175, 6 turns. The walls are n170-W6, n171-W6, n172-W6, n173-W1, n174-W1, n175-W6 (`plans/night171-read.md:63`, `plans/night172-read.md:63`, `plans/night173-read.md:58`, `plans/night174-read.md:60`, `plans/night175-read.md:62`). Each names refusals of `rulings.rule` and an answer of his that lands nothing. The reads' own "Same as" column joins them: night 172 "Same" (`plans/night172-read.md:151`), night 173 "Same door, `rulings.rule`" (`plans/night173-read.md:173`), night 174 "Same door ... as night 173's W1" (`plans/night174-read.md:205`), night 175 "Same shape as night 174's W1 on a new page, an account page" (`plans/night175-read.md:183`). The refusal texts change from night to night: the empty-words text is gone on night 173, and the act text fires on new forms on nights 173 and 174. The door and the sign are the same, so I do not split the chain.
2. The state at the end: Open. Night 175, the last run of the night series, named it (n175-W6). n175-W6 meets dry1-W5 by a "not sure" link only (extract c, night 175, item 8).
3. The conditions at the end: the last naming is night 175, the last night. The next runs are dry runs with the session in the Principal seat (extract c, night 175, item 9). Dry1 ran on click, and dry2 and dry3 on other repositories. Conditions changed.
4. The changes, in order. Before the chain, frame 330's rulings seam passes 4 to 4i and two brief changes landed before night 170 at 26a44700 (`plans/archive/stack-2026-11-02.md:95-102`). They come before the first naming, so I do not count them.
   1. F2 with F3, frame 344's audit, merge 135c87d1 at 2026-10-28 02:43, "land f2root, F2 with F3, one parser of his line references and what they ask of a named target". Files: `rota/roles/api.py`, `rota/roles/principal.py`, `rota/core/runner.py` (git show). Kind: a door. Built before night 172. The next read: "Same. The read-back text, the empty-words text and the act text all fired on night 171" (`plans/night172-read.md:151`). Count: 65 of 93 calls refused, against 75 of 92 on night 171 (`plans/stack.md:325-326`).
   2. Sprint 32 row 1, branch f2b: f53ff5b0 "read his words from the record at the rulings door" and 7762b169 "read his reply, not the seat's words, at the naming door", merged at ee3464fc (06:47) and bf858f82 (08:36) on 2026-10-28. File: `rota/roles/api.py`. Kind: a door. Built before night 173 (night 173 ran on 36d2a667). The next read: refusals that held his words in a nested field, "9" to "0", and "The empty-words text is gone" (`plans/night173-read.md:144`, `:173`). Count: 33 of 51 refused (`plans/stack.md:278`).
   3. Sprint 33 row 1, merge 793aa684 at 2026-10-28 11:47, "land w7root at 9923a021, one reader of his words and the rulings door on his reply, F2 passes 2f to 2g and P7 passes 1 to 1e". Commits include 1a57eb2c, af557f43, 4d13a8d8, 3b31077a, 9923a021, 69561d5b. File: `rota/roles/api.py`. Kind: a door. Built before night 174. The next read: "68 of 81 refused from 33 of 51, and 12 refusals were wrong on his words: 7 by the clause-edge rule on act spans, 4 by a false key on a ref shown on two lines, 1 a team's-note revise" (`plans/stack.md:236-239`).
   4. Sprint 34 row 1, merge dfcffd40 at 2026-10-28 14:45, "land seamroot at 90c5d390, the rulings seam of nights 173 and 174, W1, W9, W16 and the two door faults". Commits d28e6e05, cb7783db, 5cd73a2d, 9b2d34d6, 3944adee, 22f98cf2, eed16a28. File: `rota/roles/api.py`. Kind: a door. Built before night 175. The next read: "90 were refused: 79 by a door and 11 by the parser. 20 rulings landed", "Night 174 refused 68 of 81", and "8 of the 90 refusals are wrong on his words" against 12 on night 174 (`plans/night175-read.md:128`, `:148`).
   5. Frame 345, the deep Liaison cases, after night 175: the L3 rulings cases at 0b7fcc3b (2026-10-29 01:21), then the menu ruling b9337a8c "land R, a menu per page line from its row kind" (10-29 14:10) and f5487759 "retire the word form of a page ruling and its doors" (10-29 15:22). Files: `rota/roles/api.py`, `tests/rota/cases/l3_rulings.yaml` (`plans/archive/stack-2026-10-30.md:141`). Kind: a door, and the harness for the measure. Frame 345 "closed at 21 of 24 on gemma4:12b-it-qat" (same line). The next read is dry1, which names no wall of the rulings door by id (absent only). dry1-W5 meets n175-W6 by a "not sure" link.
   - Count: 5.
5. The last change before the end: not applicable. The chain is open.
6. The place of the changes: the sign shows in the refusals of `rulings_rule` at `rota/roles/api.py:17200-17728` (`python -m rota.tools.map fn rulings_rule`). Changes 1 to 4 each touch `rota/roles/api.py`, the file of the door. The commit subjects name the rulings door, the naming door, the line parser and the act readers. Change 1 also touches `rota/roles/principal.py` and `rota/core/runner.py`. Change 5 replaces the word form of a page ruling with a menu in `rota/roles/api.py`, at `line_menu` and `menu_ruling` (`plans/archive/stack-2026-10-30.md:141`). All five touch the place of the sign.
7. Who started each change:
   1. Frame 344's audit, on Roman's message of 2026-10-27 14:08: "a few sessions ago we analyzed the completed frames and found that many did not fix the root cause. Go back and review them". Then Roman at 19:40: "I want all the fixes implemented before the next night" (extract c, nights 170 and 171, item 9).
   2. A read of a run: sprint 32 row 1, "recommended on night 172's read" (`plans/stack.md:309`, `:331-337`).
   3. A read of a run: sprint 33 row 1, "recommended on night 173's read" (`plans/stack.md:271`, `:286-291`).
   4. A read of a run, sprint 33 row 1 and sprint 34 row 1. It landed "on Roman's word of 14:45" (`plans/stack.md:244`).
   5. Roman, 2026-10-28 14:30: "Sounds like we need less doors and more in depth test cases". Frame 345 was "pushed on Roman's go" (commit 6bd52ad4; extract c, night 174, item 9).
8. The origin: the door is `rulings_rule` in `rota/roles/api.py`. The route of his words through the Liaison comes from b57772f5 (2026-09-10, "feat(seat): the principal's words land through the Liaison, not a parser"). Each refusal text has its own origin. `_faulted_approve` comes from f0b2924c (2026-10-16, "fix(api): the verdict door refuses an approve of a line the words fault"). Its message names night 149's s212, which approved lines that his words faulted. The list names "frame 250's approve refusal" in another chain (list line 342), and this pass did not check that f0b2924c belongs to frame 250. The text "Your last answer to this page did not reach the team" comes from 0582873a (2026-10-16), frame 267 (`plans/archive/stack-2026-10-17.md:122`). Frame 267 answered a reply whose session lands no ruling. Origin class: a frame that answered another wall: frame 267, a reply that landed no ruling; and the door of f0b2924c, night 149's wrong approve, frame not sure.
9. After the end: not applicable. The chain is open.

Row: Open | conditions changed | 5 | not applicable | doors of frames | origin frame: 267

### Chain 8: dry4-W3, 6 turns, firm

Reader: the lead.

1. The wall: "4 pages carry the team's duplicate term senses [C?] (3)" (`plans/method/turns-list-2026-11-10.md`:330). First turn dry run 4, last turn dry run 9, 6 turns: dry4-W3 (`plans/dry4-read-2026-11-03.md`:124), dry5-W3 (`plans/dry5-read-2026-11-04.md`:52), dry6b-W4 (`plans/dry6b-read-2026-11-06.md`:62), dry7-W4 (`plans/dry7-read-2026-11-07.md`:160), dry8-W4 (`plans/dry8-read-2026-11-08.md`:48), dry9-W4 (`plans/dry9-read-2026-11-10.md`:56). All six walls sit at one place, the `term_collision` predicate and its pages. The signs are not one. Part A: the team's own duplicate senses become term pages to him (dry runs 4 and 5), or the same sessions reach no page (dry run 6b, "None reached the seat as a page in this run"). Part B: his answer on a term does not end the question, and the word comes back (dry runs 7, 8 and 9: "His answer on a term did not end the question", "m18 asked m14's term again", "The term question three times"). The root read joins 6b-4 and 7-4 as one wall, W10 (`plans/walls-root-read-2026-11-08.md`:24). Dry run 5's wall 4, "the m16 question came back after the seat answered it", has part B's sign and is not in the chain (`plans/dry5-read-2026-11-04.md`:53). Split: part A dry runs 4, 5 and 6b, 3 turns; part B dry runs 7, 8 and 9, 3 turns.
2. The state at the end: Part B: Open. Dry run 9, the last run of the dry series, names it. Part A: Ended by the split. Dry runs 6c, 7 and 8 do not name part A's sign. The predicate's other sign, part B, shows from dry run 7.
3. The conditions at the end: Part B: not applicable. No run follows dry run 9 in the records of 2026-11-10. Part A: the kind of run changed at dry run 6c, which continues 6b at turn 5 with `ROTA_ONESHOT=1` and the 3080 alone (`plans/method/turns-list-2026-11-10.md`:305). Dry run 7 starts from zero. Conditions changed.
4. The changes: no change aimed at this wall was found from dry run 4 to dry run 9. Dry runs 4 and 5 sent their walls to other passes (`plans/method/turns-list-extract-c-2026-11-10.md`:522, 551). The root read lists frame 183 and "The onboarding design's cut of the `term_collision` pages" as "183 pushed, never built. The cut "is not built"" (`plans/walls-root-read-2026-11-08.md`:24). Frame 183 moved to the front by C77 on 2026-11-08 10:49 (`plans/stack.md`:3252-3260). Build 2 of 2026-11-10 (02:20) is frame 114's clarify door. Frame 183's own line says "This frame's own door, the word check of glossary_same, and W10 of dry run 7, the term answer that does not end the question, stay open here" (`plans/stack.md`, frame 183, status 2026-11-10 01:00). The dry run 9 read says "Frame 183 was built in build 2" (`plans/dry9-read-2026-11-10.md`:59). The two records disagree. This page follows the frame's own line. Count: 0.
5. The last change before the end: Part B: not applicable, open. Part A: none. Evidence: absent only.
6. The place of the changes: no change. The place of the sign: the `term_collision` predicate, "`predicates.py` 371 to 597, its lines 127 to 218" (`plans/walls-root-read-2026-11-08.md`:24). The root read reads the cause as "His answer is keyed by sense id".
7. Who started each change: not applicable. The move of frame 183 to the front came from rule C77, "ruled: Roman, 2026-11-08", after his words "we need to reason on the list of walls and their provenances before planning?" (`plans/method/turns-list-2026-11-10.md`, dry7 cell 9).
8. The origin: `term_collision` comes from f6ac0c5b, 2026-08-14, "feat(scheduler): two senses of one word is an obligation, not bad luck" (`plans/walls-root-read-2026-11-08.md`:24, `git show`). Origin class: rota's first design.
9. After the end: Part B: not applicable, no read after dry run 9. Part A: yes, at the same place under another name: dry run 7's W4, part B.

Row: A Ended, B Open | A conditions changed; B not applicable | 0 | absent only | rota's first design | origin frame: none

### Chain 9: dry4-W4, 6 turns, firm

Reader: the lead.

1. The wall: "the guess misses `parser/string.py` by word match [C?] (4)" (`plans/method/turns-list-2026-11-10.md`:331). First turn dry run 4, last turn dry run 9, 6 turns: dry4-W4 (`plans/dry4-read-2026-11-03.md`:125), dry5-W7 (`plans/dry5-read-2026-11-04.md`:56), dry6c-W8 (`plans/dry6c-read-2026-11-06.md`:96), dry7-W9 (`plans/dry7-read-2026-11-07.md`:165), dry8-W11 (`plans/dry8-read-2026-11-08.md`:83), dry9-W2 (`plans/dry9-read-2026-11-10.md`:46). The first five are one sign at one place: the Architect's first guess names `parameter.py::q_split` or `property.py` by the word "split" and misses `string.py`. Dry run 9's W2 is the touch line that keeps `property.py` after two corrections. Its read says "Repeats W11" and "s149's prompt cut "1452 of 1472" candidate symbols, and `string.py` and `_foldline` never appear in it". So it holds the same miss and one more sign, the exclude rows that the rewrite does not read. No split.
2. The state at the end: Open. Dry run 9 names it.
3. The conditions at the end: not applicable. No run follows dry run 9 in the records of 2026-11-10.
4. The changes: no change aimed at the word match was found. The root read: "none by heading. Frame 362's demand read in part" (`plans/walls-root-read-2026-11-08.md`:26). The dry run 9 read: "W11 and root read W12, the guess ... no frame by heading" (`plans/dry9-read-2026-11-10.md`:102-114). Two changes touched the guess's place for other walls. First, frame 362's shape layer, 34cd529a "index calls in code_calls and mark copies on the guess" and baac0dae "tell the guess which copy to name", 2026-11-04 01:07 and 01:51 (`git log`). Its design aims at copies of one function, the test cases T2 and T3 (`plans/design-onboarding-shape-2026-11-04.md`:29, 161-162). It keeps the word match as the match rule (same page, line 270). Second, frame 182's pass 2, 0e4ebe03 and 8e373c39, 2026-11-10 02:18 and 03:39, which read the guess for the bound set and the commitment tie (`git log`). This cell rests on the absence of a change that names the wall. Count: 0.
5. The last change before the end: not applicable, open.
6. The place of the changes: no change aimed. The place of the sign: `code_callables` in `rota/roles/api.py`, "api.py 20081", which "matches whole name tokens" (`plans/dry4-read-2026-11-03.md`:125), and the guess mode of the Architect.
7. Who started each change: not applicable.
8. The origin: the guess mode comes from 7ec9b940, 2026-10-18, "feat(core): the Architect writes a scope guess per request before sign-off", frame 298 (`plans/walls-root-read-2026-11-08.md`:26, `git show`). Frame 298 answered night 156's wall: "A correction of the request's code pointer lands as an amendment of the request, and the live batch dies" (`plans/archive/stack-2026-10-21.md`:109). The word match of `code_callables` is older: `def code_callables` first appears in 395535da, 2026-08-27, "feat(sandbox): delivery hardened three ways" (`git log -S`). Origin class: a frame that answered another wall: frame 298, the code-pointer correction of night 156.
9. After the end: not applicable, no read after dry run 9.

Row: Open | not applicable | 0 | not applicable | frame 298 | origin frame: 298

### Chain 10: n147-W6, 5 turns, firm

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "merged change carries code he declined (E) [C?]" (`plans/method/turns-list-2026-11-10.md`:332). First turn n147, last turn n151, 5 turns: n147, n148, n149, n150, n151. The wall lines: n147-W6 as above, n148-W1 "bg_3 merges the version message he declined twice (H)", n149-W6 "frame 243's seam on walks 2 and 3 [C5]", n150-W11 "respecify keeps the contested text, frame 243 [C4]", n151-W13 "frame 243's cr_1 never respecified" (`plans/method/turns-list-extract-b-2026-11-10.md`:397, 412, 438, 467, 493). The sign changes inside the chain. On nights 147 and 148 a merge carries what he declined. On nights 149 to 151 no merge carries it, and the sign is a criterion text that keeps his declined words: night 149 "0 of 1 merges carry what the principal declined" (`plans/stack.md`, frame 243 status 2026-10-15 16:24), night 150 "0 of 0 merges" and "5 of 5 respecify relays ... kept that text" (status 2026-10-16 07:01). Frame 243's scope read joins the two signs: "the seam is the Terminologist's `criteria.respecify` on a contest relay", and night 147 "holds the same seam twice" (`plans/stack.md`, frame 243 status 2026-10-15 01:33). I keep one block on that record. A reader who splits it puts n147-W6 and n148-W1 in one part and n149-W6 to n151-W13 in the other.
2. The state at the end: Ended. The last naming is n151. Night 152: "0 of 2 landed respecifies kept the contested text" and "0 of 3 merges carry a thing his words declined" (frame 243 status 2026-10-16 22:30). Night 153: "0 of 3 respecifies keep a text he faulted; 1 of 2 merges carries a declined thing, bg_2's docstring ... frame 250's seam" (frame 243 status 2026-10-17 04:31). The extract marks n153 "not sure (section 5 reads frame 243)" (extract b:498). The reads of nights 154 and 155 hold no "declined", "frame 243" or "contested text" (grep, absence only). So nights 152, 153 and 154 do not name the wall by id, and night 153 holds a not-sure sign.
3. The conditions at the end: same. Nights 152 to 154 ran on the same repository, the same kind of run and the same agent principal on Opus (frame 243 status 2026-10-16 20:40). The requests change at night 163, later.
4. The changes:
   - Frame 243, pass 1 and 1b: 7618bfb5, 26940b74 and 7a2cb843, 2026-10-15, before night 149 (frame 243 status 2026-10-15 10:30 and 11:01). Files: `rota/core/runner.py` `push_working_set`, the block "[the principal contested these criteria]" in the Developer and Tester wakes, and the supersede refusal in `decisions_author` in `rota/roles/api.py` (status 2026-10-15 02:26, 10:50). Kind: other code of rota (the pushed rows of a wake) and a door. Night 149: "0 of 1 merges carry what the principal declined", the texts moved "only when a landed ruling quoted the declined phrase", "0 supersede refusals" (status 2026-10-15 16:24).
   - Frame 243, pass 2: cc6cbf57, 2026-10-15, `_relay_contest_block` in `rota/core/runner.py`, the block on the Terminologist's relay wake (status 2026-10-15 17:51, 18:02). Kind: other code of rota.
   - Frame 243, pass 2b: 966a978f, 2026-10-15, the block only for a contest verdict, one entry per ruling (status 2026-10-15 18:44, 18:55). Kind: other code of rota. Night 150: "5 of 5 respecify relays after the `separators=('', '')` contest kept that text, against 3 of 6 on night 149" (status 2026-10-16 07:01). Night 151: "2 of 5 landed respecifies kept the contested text", "0 of 2 merges carry a declined format" (status 2026-10-16 17:36).
   No change aimed at candidate E between night 147 and night 148 is found. Frame 243 names night 147's candidate E as its pointer (`plans/stack.md`, frame 243 "Pointer:" line).
   Count: 3.
5. The last change before the end: pass 2b, 966a978f. Evidence: a read confirms with a count. Night 152 gives "0 of 2 landed respecifies kept the contested text" and "0 of 3 merges" (status 2026-10-16 22:30), and night 153 gives "0 of 3 respecifies keep a text he faulted" (status 2026-10-17 04:31). The frame never closed. It was "parked at night 158's read: no live session holds the frame, and no night read has counted it since 2026-10-18 or before" (status 2026-10-21 16:23).
6. The place of the changes: the sign shows in the criterion text that the Terminologist writes with `criteria.respecify` in `rota/roles/api.py`, and then in the merged code (frame 243 status 2026-10-15 01:33). The three passes touch another place: the wake prompt builders `push_working_set` and `_relay_contest_block` in `rota/core/runner.py`. Pass 1 also touches `decisions_author` in `rota/roles/api.py`, another function in the same file.
7. Who started each change: a read of a run, "pushed from night 148's read" (frame 243 status 2026-10-15 01:16). A row of a sprint: "sprint 6, row 1", and commit 13d8f226 "Roman rules sprint 6's order, frame 243's scope read first". Roman ruled the shape on the ladder of change kinds: "there's only so many kind of changes we can make" (frame 243 status 2026-10-15 01:55). Pass 2 came from the second interview, "the seat that writes the text never saw his words" (status 2026-10-15 17:35).
8. The origin: the interview names the sentence "Keep the other words of the criterion" in the Terminologist's brief as what s188 followed (frame 243 status 2026-10-15 01:37). The sentence is in `rota/roles/prompts/terminologist/criterion_repair.md`. `git log -S` gives b0a2086e, 2026-10-09, "feat(rota): the park ask is a page with the item and its criteria", which carries "Roman ruled on 2026-10-08 that the park ask is a page with rows" and names no frame and no wall. The scope read also names "no code reads `decisions.supersedes`" (status 2026-10-15 01:33). Origin class: not found. The commit answered a ruling, and no frame or wall is named in it.
9. After the end: yes, not sure. Night 153's merge carries a declined docstring through "the clarify verdict approved" it, "frame 250's seam" (frame 243 status 2026-10-17 04:31). The clarify verdict is the third seam in frame 243's own heading (`plans/stack.md`:2858). Night 152 names another sign at the merge, "3 of 3 leave out a thing his words asked for", W8, frame 273 (status 2026-10-16 22:30).

Row: Ended | same | 3 | read confirms count | brief, no frame | origin frame: none

### Chain 11: n154-W2, 5 turns, firm

Reader: the lead.

1. The wall: "the commit after an `unchanged` rewrite [C8] (W2, N2)" (`plans/method/turns-list-2026-11-10.md`:333). First turn night 154, last turn night 162, 5 turns: n154-W2, n156-W3, n158-W1, n161-W8, n162-W7. The chain holds two signs. Part A: a commit lands the removal of a base statement past the note door of frames 140 and 283: n154-W2 (`plans/night154-read.md`:482-487), n156-W3, "Frame 283, right to fire, 1 residue" (`plans/night156-read.md`:147), and n158-W1 (a), "s279's false note let bb7c4492 remove `ctx.exit()`" (`plans/night158-read.md`:202). Nights 154, 156 and 158, 3 turns. Part B: a merge holds a change that no criterion names and no page shows: n158-W1 (b) to (e), n161-W8 and n162-W7, "merged changes outside the criteria, frame 306" (`plans/night161-read.md`:289, `plans/night162-read.md`:334). Nights 158, 161 and 162, 3 turns. n158-W1 joins the two parts. After the split, neither part reaches four turns alone.
2. The state at the end: Ended, both parts. Part A: the last naming is night 158. Night 159: "that merge holds his change and nothing else" (`plans/night159-read.md`:20-21). Nights 160, 161 and 162: frame 283 is "Met on night 3 of 3 ... 0 landed removals of a base statement and 0 merges that hold one" (`plans/archive/stack-2026-10-26.md`, frame 283, status 2026-10-24 10:33). Part B: the last naming is night 162. Extract c reads n162-W4 to W8 as "not met in n163, n164", and night 164a has no read page (`plans/method/turns-list-extract-c-2026-11-10.md`:54).
3. The conditions at the end: Part A: same. Nights 159 to 161 hold the R1 requests and the same kind of run. Part B: conditions changed. The requests changed at night 163, the first run after the last naming.
4. The changes, in order:
   - Part A. Frame 283, passes 1 to 7b, 2026-10-17 16:41 to 18:43, head b5b14311 "fix(api): the dropped sentence says when the commit is not held ..." (`git log`; `plans/archive/stack-2026-10-26.md`, frame 283, status lines of 2026-10-17). Files: `rota/roles/api.py` and `rota/core/schema.sql` (`drop_notes`). Kind: a door or a refusal. On night 155's commit (`git merge-base`). Night 155: "no held frame's door fired over ten Developer sessions, 0 of each sign" (status 2026-10-18 02:06). Night 156: "the door refused 33 commits over 10 Developer sessions and no commit landed a statement removal" (status 2026-10-18 07:22).
   - Part A. Frame 283, the residue fix ee166261, 2026-10-18 14:13, "fix(roles): a landed ledger note closes a dropped note when about_ref names the path" (`git log`; status 2026-10-18 13:50 and 14:13). File: `rota/roles/api.py`, `_close_logged_notes`. Kind: a door or a refusal. On night 157's commit. Night 158: "the measure reads 0 of 3, and a removal of a base statement merged" (status 2026-10-21 16:23).
   - Part A. Frame 283, W1 a, passes 1 to 4d, 2026-10-21 16:26 to 2026-10-23 16:19, on the branch from a00baecb (2026-10-23 13:24) to a4645b0d "fix(api): a removal request continues past "and" only onto a noun" (`git log`; frame 283, status lines of 2026-10-21 16:26 to 2026-10-23 16:19). File: `rota/roles/api.py`, `_removal_asked`, `_asks_removal`. Kind: a door or a refusal. a00baecb is on night 159's commit, and a4645b0d is on night 160's commit (`git merge-base`). Night 160: "Met: 9 fires seen, all right. 0 landed removals of a base statement with a note" (status 2026-10-24 01:11).
   - Part B. Frame 306, repair 1, 6e72b8b9, 913f54af and 8cff8209, 2026-10-23 16:08 (frame 306, status 16:08). Files: `rota/core/runner.py` (`answer_about`) and `rota/core/scheduler.py`. Kind: other code of rota. On night 160's commit. Night 160 merged nothing: "The merge count is 0 of 0, because nothing merged" (frame 306, status 2026-10-24 01:11).
   - Part B. Frame 306, pass 1 and 1b, 4093b0ca and a3f2f96e, 2026-10-24 02:53 (frame 306, status 02:53). Files: `rota/roles/api.py` (`_about_the_tests`, `criteria_respecify`) and the criteria mode. Kind: a door or a refusal, and a prompt of a seat. On night 161's commit. Night 161: "2 of 2 merges hold a change no criterion names and no page shows" (status 2026-10-24 05:58).
   - Part B. Frame 306, passes 2 to 3b, the route: feb198eb, 11e031c0, 237d4fb6 and c1879bf1 in `rota_p306b` on 214d22d0, and the case 3c0a2310 to 40276a10 (frame 306, status lines of 2026-10-24 08:02 to 11:03). Places: `code_commit` in `rota/roles/api.py` and `foreseen_notices` in `rota/roles/principal.py`. Kind: a door, and a page. Night 162 ran before these passes. Night 162: "2 of 2 merges hold changes no criterion names" (status 2026-10-24 10:35). Then 0e16a18e, "revert(api): batches.judge_touch takes a foreseen judgement as before", is on night 163's commit (`git merge-base`). The status of 2026-10-24 17:35 says "the route is designed and reverted since 11:31".
   Count: 6 (3 on part A, 3 on part B).
5. The last change before the end: Part A: a4645b0d, frame 283's pass 4d. Evidence: a read confirms with a count. Nights 160, 161 and 162 each read "met", and "The frame stays open at its residue row" (frame 283, status 2026-10-24 10:33). Part B: frame 306's passes of 2026-10-24, with the route reverted. Evidence: absent only. No read of nights 163 and 164 gives a count of merged changes outside the criteria. Frame 306 goes on with its first half, the words that do not reach the criterion (status 2026-10-24 17:35 and 18:24).
6. The place of the changes: Part A: each change touches the commit door's note check in `rota/roles/api.py`, frame 140's site. The sign shows there: the commit lands. Part B: repair 1 and pass 1 touch the hop from a page reply to the criteria (`runner.py`, `api.py`). The sign shows at the merge and at the page after it. Only the route of passes 2 to 3b touches that place (`code_commit`, `principal.py`), and the route was reverted.
7. Who started each change: Part A: the read of night 154, "candidate N2" (status 2026-10-17 16:40), as "sprint 12 row 1" (16:41). The residue fix: the read of night 156, W3, through a residue probe (status 2026-10-18 13:50). W1 a: the read of night 158, W1 (a) (status 2026-10-21 16:26). Part B: the read of night 158, W1 b and d (frame 306, "pushed from night 158's read"). Pass 1: the read of night 160, section 5, row 2 (status 2026-10-24 01:11). The route: "sprint 18 row 8" (status 2026-10-24 07:39). No message of Roman starts a change. Roman paused and resumed all work: "can you pause all work?" (2026-10-21 16:41) and "resume" (2026-10-23 12:16) (frame 283, status lines).
8. The origin: Part A: the result "already holds this text, so this write changed nothing" comes from 9c3592f0, 2026-09-30, "fix(desk): a write the file already holds says so and quotes the red assertion", from night 97's s215 and s216 (`git log -S`, `git show`). The stack pushed frame 93 for that wall: "The silent no-op write is a new wall, frame 93" (`plans/archive/stack-2026-09-29.md`:693). The note door is frame 140's 68e7ba44, 2026-10-17, which answered night 121's span write that drops its tail (`plans/stack.md`:3600-3606). Origin class: a frame that answered another wall: frame 93, night 97's silent no-op write. Part B: the merge of a batch does not compare its hunks with the criteria. The stray detector `_unnamed_def_strays` comes from b0dbd926, 2026-10-18, "the unnamed-definition door records a stray for the Architect in place of its refusal" (`git log -S`). No commit that adds the sign itself was found. Origin class: not found.
9. After the end: Part A: not sure. Frame 283's pass 5, for a whole-file write, was built on night 162's day and then reverted: "283 at its residue with pass 5 reverted" (frame 283, status 2026-10-24 11:03). Part B: yes, at the same seat and step under another name. Night 163's walk 1 is "the frame's night 3 sample of the first half, his page words "the code does not change" did not reach c_1" (frame 306, status 2026-10-24 17:35).

Row: Ended | A same; B conditions changed | 6 | A read counts; B absent only | A frame 93; B not found | origin frame: 93

### Chain 12: n155-W2, 5 turns, firm

Reader: the lead.

1. The wall: "request line contested, the live batch cancelled [C?] (2)" (`plans/method/turns-list-2026-11-10.md`:334). First turn night 155, last turn night 161, 5 turns: nights 155, 158, 159, 160 and 161. The chain holds two signs. Part A: a contest or a revise of line 1 that his words do not make lands, and the cancel abandons the live batch: n155-W2 (`plans/night155-read.md`:124), n158-W5 (`plans/night158-read.md`:206), n160-W3 (`plans/night160-read.md`:273), n161-W2 (`plans/night161-read.md`:283). Nights 155, 158, 160 and 161, 4 turns. Part B: the line reader places his words on the wrong line or misreads a cue: n158-W4 (`plans/night158-read.md`:205), n159-W4 (`plans/night159-read.md`:219), n160-W3, which the read also places on "cause 8 on frame 305's reader", and n161-W6, the team-note door reads "On line 11, use ..." as a drop (`plans/night161-read.md`:287). Nights 158, 159, 160 and 161, 4 turns. So the block splits.
2. The state at the end: Ended, both parts. The last naming is night 161. Night 162: "0 wrong line-1 contests from 2, 0 cancels from 2" (`plans/stack.md`:819). Night 163: "Night 2. 0 wrong contests of line 1" on frame 258, and "0 wrong placements on the clear pages, 1 wrong approve" on frame 305 (`plans/archive/stack-2026-10-24.md`, status lines of 2026-10-24 18:19). Night 164a has no read page. Night 164 closes both frames. Extract c places n163-W3, "a contest kept item 1 alive", as "not sure" (`plans/method/turns-list-extract-c-2026-11-10.md`:32).
3. The conditions at the end: conditions changed. The requests changed at night 163, the second run after the last naming.
4. The changes, in order (frames 258 and 305, `rota/roles/api.py`, kind: a door or a refusal):
   - Frame 258, pass 3, 3b and 3c: 2284cfab, 06b3988d and c641d108, 2026-10-18 03:52 to 05:15, "the line-1 spare holds when another sentence names another line" (`git log`; `plans/archive/stack-2026-10-24.md`, frame 258, status lines of 2026-10-18 03:56 to 05:22). On night 156's commit db0c781d. Night 156: "page replies with a batch line whose line 1 is contested, 0 of 7" (status 2026-10-18 07:22). Night 157: "The request line is no longer where batches die" (`plans/night157-read.md`:214). Night 158: "not met: 3 contests landed on a line no sentence names" (status 2026-10-21 16:23).
   - Frame 305, pass 1, 1b and 1c: a8d19792, 73dafcf9 and 5659a88f, 2026-10-23 13:42 to 13:54, "a fault cue binds to the subject of a relating clause" (`git log`; frame 305, status lines of 2026-10-23 13:43 to 14:03). On night 159's commit 73a4801f. Night 159 names W4, "the line reader's cue set leaks a word per night".
   - Frame 305, pass 2, 2b and 2c: c331eda8, 405fc29b and 04b49638, 2026-10-23 18:52 to 19:19, "the line reader faults any clause with a verb" (`git log`; frame 305, status lines of 2026-10-23 18:24 to 19:22). On night 160's commit 695e8be7. Night 160: "Met on its counts: 0 wrong refusals of 7", and the reader "missed two rulings by their verbs", W3 (frame 305, status 2026-10-24 01:11).
   - Frame 258, pass 1 and 1b of 2026-10-24: e5ae08a9 and fe4b3c78, 03:57 and 04:03, "a criteria correction no longer spares the request line" and "a negated keep no longer reads as a keep" (`git log`; frame 258, status lines of 2026-10-24 03:53 to 05:58). On night 162's commit 214d22d0. Night 162: "0 wrong line-1 contests from 2, 0 cancels from 2" (`plans/stack.md`:819).
   - Frame 305, the team-note case: 26471153 and 86d39d77, 2026-10-24 06:31 and 06:39, "a sentence that asks to change a team's note revises the note" (`git log`; frame 305, status lines of 2026-10-24 06:27 to 06:43). On night 162's commit. Night 163: "0 wrong placements on the clear pages, 1 wrong approve".
   Count: 5.
5. The last change before the end: frame 258's fe4b3c78 for part A, and frame 305's 86d39d77 for part B. Evidence: a frame closes on a count. Frame 258: "closed: met on its night 3 (observed: `plans/night164-read.md`, section 1; nights 162, 163 and 164)". Frame 305 closes with the same words (`plans/archive/stack-2026-10-24.md`, both frames, status 2026-10-24 22:55).
6. The place of the changes: every change touches `rota/roles/api.py`, the door of `rulings.rule` (`_agreed_contest`, `_unnamed_contest`, `_line_refusal`, `_KEEP_CHANGE`, the line reader). Part B's sign shows there, so the changes touch the place of the sign. Part A's cancel shows at another place: `principal.land` sets the item `contested`, and the `cancel` predicate abandons the batch (`plans/night161-read.md`:283 names `principal.py:2234` and `predicates.py:1531-1555`). No change of cell 4 touches those two places.
7. Who started each change: frame 258's pass 3, the read of night 155, section 5 (status 2026-10-18 02:54). Frame 305's pass 1, the read of night 158, W4 (frame 305, "pushed from night 158's read"). Frame 305's pass 2, a row of a sprint, "sprint 16 row 3" (status 2026-10-23 18:24), from the read of night 159, W4. Frame 258's passes of 2026-10-24, the walk of night 161 and a provenance read (status 03:47 and 03:53). The team-note case, a row of a sprint, "sprint 18 row 5" (status 2026-10-24 06:27), from the read of night 161, W6. No message of Roman found in the window (`plans/method/turns-list-extract-c-2026-11-10.md`:33).
8. The origin: Part A: the refusal text "have no ruling. Every line of the page takes one" and the map of `rulings.rule` come from b57772f5, 2026-09-10, "the Liaison landing feature", frame none (`plans/frame258-provenance.md`:48). The cancel text "is no longer schedulable" comes from 73c9cba3, 2026-08-27, "feat(scheduler): loop 6 earns G1 -- the brake pedal and the terminal exit" (`git log -S`). Origin class: rota's first design. Part B: "The reader is frame 234's pass 1, commit 39e2fba7, 2026-10-14 11:29" (`plans/frame305-provenance.md`:31). Frame 234 answered night 146's wall, "The Liaison's verdict contests the request line the principal never named, and the cancel abandons the batch" (`plans/archive/stack-2026-10-15.md`:5). Origin class: a frame that answered another wall: frame 234, night 146's contests of line 1.
9. After the end: not sure. Extract c places n163-W3, a contest that kept item 1 alive, as "not sure" against n161-W2 (`plans/method/turns-list-extract-c-2026-11-10.md`:32). Night 163 counts "1 wrong approve" on frame 305's reader (status 2026-10-24 18:19).

Row: Ended | conditions changed | 5 | frame closes count | A first design; B frame 234 | origin frame: 234

### Chain 13: n156-W10, 5 turns, firm

Reader: the lead.

1. The wall: "`constraint_zero` quarantine at s1 in onboarding [C?] (W10)" (`plans/method/turns-list-2026-11-10.md`:335). First turn night 156, last turn night 160, 5 turns: n156-W10, n157-W13, n158-W12, n159-W10, n160-W8 (`plans/night156-read.md`:154, `plans/night157-read.md`:207, `plans/night158-read.md`:213, `plans/night159-read.md`:225, `plans/night160-read.md`:278). The five walls are one sign at one place. The chain does not split. Chain 2 (n166-W9, "the constraint tick quarantines at onboarding") is the same sign. Night 166's read says "The same key at 3 on nights 164 and 165" (`plans/night166-read.md`:217). The list holds the two as two chains, because night 160's W8 is "not found in the 161 to 163 wall lists" (`plans/method/turns-list-extract-b-2026-11-10.md`:727).
2. The state at the end: Ended, by the rule. The last naming is night 160. Nights 161, 162 and 163 do not name it as a wall. But the sign shows in the quarantine rows of the reads of nights 163, 164 and 165: "`-|tick:constraint_zero|` ... at 3" (`plans/night163-read.md`:42, `plans/night164-read.md`:47, `plans/night165-read.md`:46). Night 166 names it again as W-I. So the sign did not stop. Only the wall lists stopped.
3. The conditions at the end: conditions changed. The requests changed at night 163, the third run after the last naming.
4. The changes: no change aimed at this wall in the window from night 156 to night 166. Each read says "Not placed" (`plans/night156-read.md`:154 to `plans/night160-read.md`:278). The night 158 read's plan lists "W12 the constraint_zero quarantine on its third night" under "Not read this night" (`plans/stack.md`:1085-1087). `git log -L` on the predicate `constraint_zero` (`rota/core/predicates.py`:2331-2362) shows no commit between 233436e5 (2026-08-12) and e7016e65 (2026-10-31). This cell rests on absence alone for the other files. Count: 0.
5. The last change before the end: none. Evidence: absent only. The quarantine rows of nights 163 to 165 show the sign.
6. The place of the changes: not applicable, no change. The place of the sign: the predicate `constraint_zero` in `rota/core/predicates.py`:2331-2362, which wakes `tick:constraint_zero`, and `refresh_constraint_zero` in `rota/onboarding/boot.py`:254.
7. Who started each change: not applicable.
8. The origin: the predicate `constraint_zero` in `rota/core/predicates.py` comes from 0aaedc04, 2026-08-10, "feat(onboarding): stage 7 exists, stage 8 shows how far the rest is" (`git log -L`). The stack records the same quarantine on night 85: "`tick:constraint_zero` reached three attempts ... Not diagnosed" (`plans/stack.md`:5726-5727). The cause came later, at frame 354: "The constraint zero predicate wanted every indexed area without a survey while the refresh bound only areas with a symbol grain" (e7016e65 body, 2026-10-31). Part b's chain 2 traces the binding to 01e48a6f, 2026-09-08, which answered a cold walk on tipsC and names no frame (`plans/method/chains-read-extract-b-2026-11-10.md`, chain 2, cell 8). Origin class: a commit that answered another wall, frame not found, the prose-only walk of 2026-09-04, as chain 2.
9. After the end: yes, the same sign at the same place under another name. The reads of nights 163 to 165 hold the key in their quarantine rows, and night 166 names W-I, the first wall of chain 2 (`plans/night166-read.md`:217).

Row: Ended | conditions changed | 0 | absent only, sign continues | commit for another wall, no frame | origin frame: none

### Chain 14: n170-W13, 5 turns, firm

Reader: sub-agent, part b (`plans/method/chains-read-extract-b-2026-11-10.md`).

1. The wall: "argument form and id refusals that a seat repeats [C?] (W13, F19, F22)" (`plans/method/turns-list-2026-11-10.md:336`; `plans/night170-read.md:69`). First turn night 170, last turn night 174, 5 turns. n170-W13 holds two signs, and the read places them under two facts: "F19 for s211; F22 for s209 and s200". Night 171 splits them into W11 and W13 (`plans/night171-read.md:68`, `:70`). So this block splits the chain.
   - Part A, ids from the wrong table, F22: n170-W13 (s209 `model.adopt` on b_3, s200 `tests.encode` on a b_1 id), n171-W11, n172-W16, n173-W15, n174-W18 (`plans/night172-read.md:73`, `plans/night173-read.md:72`, `plans/night174-read.md:77`). The reads say "Same as night 171's W11", "Same as night 172's W16", "Same as night 173's W15" (`plans/night172-read.md:161`, `plans/night173-read.md:187`, `plans/night174-read.md:222`). Turns n170 to n174, 5 turns. n175-W10 is "Same family as night 174's W18" (`plans/night175-read.md:187`), a "not sure" link in the extract.
   - Part B, argument form refusals that a seat repeats, F19: n170-W13 (s211 `msg.relay_vision_keeper`, round_no as words) and n171-W13 (`plans/night171-read.md:70`). Turns n170 and n171, 2 turns. n171-W13 meets n173-W14 by a "not sure" link (extract c, night 171, item 8). Part B alone does not reach four turns.
2. The state at the end:
   - Part A: Open. Night 174, one of the last three runs of the night series, named it (n174-W18).
   - Part B: Ended by the firm links. Nights 172, 173 and 174 name no wall of argument form refusals by a firm link. n173-W14, "the bg_3 Tester sends six broken bodies per turn", sits under the same fact F19 as "Same parse family as night 172's W18" (`plans/night173-read.md:186`). That is a "not sure" match, so the end rests on the firm links alone.
3. The conditions at the end:
   - Part A: open. The next runs after night 175 are dry runs, another kind of run. Conditions changed.
   - Part B: the last naming is night 171. Nights 172 to 174 ran on the same requests, the same models and the same repository (extract c, nights 172 to 174, item 2). Same.
4. The changes:
   - Part A, change 1. F22, frame 344's audit, merge 471ec356 at 2026-10-28 02:48, "land f22root, F22, one reader of the table an id lives in", with 538700af "four more sites read the one table reader". Files: `rota/core/db.py`, `rota/roles/api.py`, `rota/core/sandbox.py`, `rota/core/runner.py`, `rota/roles/principal.py` and five more (git show). Kind: other code of rota, one reader `db.table_of`. Built before night 172. The next read: "Same as night 171's W11", with 5 `model.adopt` refusals and one `ledger.log` refusal (`plans/night172-read.md:73`, `:161`). Night 173 counts 16 refusals, night 174 counts 8. The audit of 2026-10-30 marks F22 "FIXED" (`plans/rootfix-audit-2026-10-30-head.md:26`).
   - Part A count: 1.
   - Part B, change 1. F19, frame 344's audit, merge f8955d32 at 2026-10-27 18:10, "land f19root, F19, the quote forms from the parser". It deletes `_seat_forms`, `_one_backslash` and `_unescaped` in `rota/core/sandbox.py` (`plans/rootfix-audit-2026-10-30-head.md:23`). Kind: other code of rota. Built before night 172. The audit's aim: "night 170 W13 s211 repeated one call form 3 times ... go to 0 over 3 nights" (`plans/rootfix-audit-2026-10-27-b.md:34`). The next read, night 172, names no argument form wall. It counts "Seats repeat a refused call" as W18 (`plans/night172-read.md:75`). Night 173's W14 names 62 refusals of broken bodies in one session under F19.
   - Part B count: 1.
5. The last change before the end:
   - Part A: not applicable. Part A is open.
   - Part B: F19 at f8955d32. Evidence: absent only. Nights 172 to 174 name no such wall, and no read gives a count of argument form refusals that goes to 0. Night 173 names a sign under the same fact (n173-W14).
6. The place of the changes:
   - Part A: the sign shows in the id checks of the doors, `_must_exist` and the table helpers in `rota/roles/api.py`, `rota/core/runner.py` and `rota/roles/principal.py` (`plans/rootfix-audit-2026-10-27-b.md:55`). Change 1 adds `db.table_of` in `rota/core/db.py` and moves the helpers to it. It touches the place of the sign.
   - Part B: the sign shows in the call parser and the door texts on a call form, `rota/core/toolproto.py` and the relay tool. Change 1 touches the quote forms in `rota/core/sandbox.py`, `_quote_forms` and `_shown_views`. The relay refusal on round_no is another place. So change 1 touches another place for s211's sign, by the audit's own proposal.
7. Who started each change: both are rows of frame 344's audit, sprints 28 to 31, on Roman's message of 2026-10-27 14:08, "Go back and review them", and his message of 19:40, "I want all the fixes implemented before the next night" (extract c, nights 170 and 171, item 9). The audit names night 170's W13 as the evidence for both facts (`plans/rootfix-audit-2026-10-27-b.md:34`, `:58`).
8. The origin:
   - Part A: `_must_exist` comes from 6f2a2a7a (2026-08-10, "test(harness): the case runner, the obligation set, L1's first cases"). The text "is not a row of" comes from 84ea995f (2026-08-26, "feat(sandbox): observed gets its exit"). The audit says the helper set grew from 3 to 5 after frame 187 added an inline check (`plans/rootfix-audit-2026-10-27-b.md:57`). Origin class: rota's first design.
   - Part B: the call protocol comes from 231afe4c (2026-08-09, "feat(sandbox): namespaces built from edges, and the TOOL: protocol"). Origin class: rota's first design.
9. After the end:
   - Part A: not applicable. Part A is open. n175-W10 is "Same family", 113 `tests.retire` refusals (`plans/night175-read.md:66`, `:187`).
   - Part B: night 173 names n173-W14 under the same fact F19, with the Tester as the seat and a body as the call form. Not sure.

Row (Part A): Open | conditions changed | 1 | not applicable | rota's first design | origin frame: none
Row (Part B): Ended | same | 1 | absent only | rota's first design | origin frame: none

### Chain 15: dry4-W2, 5 turns, firm

Reader: the lead.

1. The wall: "the 40-session limit ends 5 of 8 turns [C?] (2)" (`plans/method/turns-list-2026-11-10.md`:337). First turn dry run 4, last turn dry run 9, 5 turns: dry4-W2 (`plans/dry4-read-2026-11-03.md`:123), dry5-W2 (`plans/dry5-read-2026-11-04.md`:51), dry6b-W5 (`plans/dry6b-read-2026-11-06.md`:63), dry8-W15 (`plans/dry8-read-2026-11-08.md`:102), dry9-W10 (`plans/dry9-read-2026-11-10.md`:83). The five walls are one sign at one place: the run loop stops a turn at its default of 40 sessions. No split. The sign is older than the chain. Frame 354 is titled "the first dry run stopped at the session cap before the plan page" (`plans/archive/stack-2026-11-01.md`:37), and dry run 3's turn 2 "stopped at the 40-session limit and not at rest" (`plans/stack.md`:2131).
2. The state at the end: Open. Dry run 9 names it.
3. The conditions at the end: not applicable. No run follows dry run 9 in the records of 2026-11-10.
4. The changes: no change aimed at the limit from dry run 4 to dry run 9. The root read: "none: a run setting" (`plans/walls-root-read-2026-11-08.md`:33). The dry run 9 read lists D9-10 under "none" in its frame table (`plans/dry9-read-2026-11-10.md`:114). Frame 354, which cut the Vision Keeper's prose sessions, closed on 2026-11-01, before dry run 4 (`git log`, f6a821fd). This cell rests on absence. Count: 0.
5. The last change before the end: not applicable, open.
6. The place of the changes: no change. The place of the sign: `drive` in `rota/tools/onboard_run.py`, `ap.add_argument("--limit", type=int, default=40)` at line 222, and the same default in `rota/cli.py`:987. "`drive` loops up to the limit, default 40" (`plans/pause-read-2026-11-06.md`:14).
7. Who started each change: not applicable.
8. The origin: the default of 40 comes from 90f09152, 2026-08-11, "fix(scheduler): a tick that cannot drain" (`git log -S 'default=40'`, `git show`). The commit answered another wall on the first foreign repository, "a survey session ... never called surveys.attest, so tick_survey never drained". It names no frame. Origin class: rota's first design (a commit of 2026-08-11 with no frame).
9. After the end: not applicable, no read after dry run 9.

Row: Open | not applicable | 0 | not applicable | rota's first design | origin frame: none

### Chain 16: n112-W1, 4 turns, firm

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "s252 refused the same challenge three times with the refusal in view [C8] (guide: frame 111)" (`plans/method/turns-list-2026-11-10.md`:338). First turn n112, last turn n119, 4 turns: n112, n113, n116, n119. The wall lines: n113-W4 "s143 sends two challenges and an escalation per reply [C8] (guide: frame 116)", n116-W4 "2 of 7 sessions refused the same challenge three times [C8] (guide: frame 116)", n119-W14 "5 of 20 Developer sessions send several challenges in one reply [C8] (guide: frame 116)" (extract a:467, 496, 556, 636). Two signs share the chain: a burst of challenges in one reply, and a session refused the same challenge three times. Frame 116 measures both in one ends-when: "Developer replies that land or attempt more than one challenge" and "sessions refused the same challenge three times" (`plans/stack.md`:3698). The first wall names frame 111, and frame 111 closed on night 112 with "the one-reply burst is frame 116" (`plans/archive/stack-2026-10-03.md`, frame 111 status 2026-10-03 13:44). I keep one block on frame 116's measure.
2. The state at the end: Ended. The chain's last naming is n119, but the next reads name the sign under frame 116. Night 120: "1 of 9 `tests_failing` sessions sent more than one challenge in a reply" (`plans/night120-read.md`:157). Night 121: "5 of 39 ... s303 sent 13 in one reply. 4 of 39 met `on exactly these refs already` three times or more" (`plans/night121-read.md`:134). Night 122: s145 "sent six challenges in one reply and two more in each of three turns, the sign of frame 116" (`plans/archive/stack-2026-10-07.md`:139, frame 131's status). After night 122: night 123 "frame 116, 0 Developer sessions hold more than one challenge in a reply" (`plans/night123-read.md`:86), night 124 "frame 116, 0 replies with more than one challenge" (`plans/night124-read.md`:122). Night 125 does not name frame 116, and its same-refs door refused 11 times, and some next calls are marked "not followed" (`plans/night125-read.md`:83-95). So nights 123, 124 and 125 do not name the wall, and night 125 is not sure.
3. The conditions at the end: same. Nights 123 to 125 ran on the same repository and requests. The door changed before night 125: 4968ea7d, frame 132, 2026-10-05 13:41 (git log -S "answered neither and did not change the test"), so night 125 met a new refusal text.
4. The changes:
   - Frame 116, "A Developer sends one challenge per red test in one reply" (`plans/stack.md`:3694). Records only: "pushed by 3d6e6173 on Roman's ruling that closed frame 111" (commit 8302ed1d), and the ends-when rewritten on 2026-10-03 14:42 (`plans/stack.md`:3701-3702). Kind: a rule or a record only. No commit builds the frame: `git log --grep "frame 116"` gives 8302ed1d only. The reads after it: night 113 "1 of 7 tests_failing sessions on both measures", night 116 "0 of 7 ... more than one challenge, and 2 of 7 sessions ... refused the same challenge three times" (`plans/stack.md`:3703-3704).
   Not counted, because it aims at another wall: frame 132's same-refs door, 4968ea7d, 2026-10-05, "the same-refs door admits a challenge the Tester did not answer", `rota/core/sandbox.py` (git show). It answers false refusals, "125 of them were not a repeat" (4968ea7d body).
   Frame 111's passes 538b84a, dad15d9, d366702, 92ca024 and eb7cd0d came before the chain's first turn (`plans/archive/stack-2026-10-03.md`, frame 111 status lines 2026-10-02 17:26 to 2026-10-03 02:32).
   Count: 1.
5. The last change before the end: frame 116's record, the ends-when rewrite of 2026-10-03 14:42 (`plans/stack.md`:3702). Evidence: a read confirms with a count, "0 Developer sessions hold more than one challenge in a reply" on night 123 and "0 replies" on night 124 (`plans/night123-read.md`:86, `plans/night124-read.md`:122). The change is a record only, so no code joins it to the end. No record says why the sign fell.
6. The place of the changes: the sign shows at the repeat-refs door in `rota/core/sandbox.py`, "which counts per call", and the runner's three-strike note in `rota/core/runner.py` (`plans/stack.md`:3696). Frame 116 touched no file. Frame 132's door, not counted, touches the same door in `rota/core/sandbox.py`.
7. Who started each change: frame 116 came from a read of a run, "found by night 112's read", and from Roman's ruling that closed frame 111 (`plans/stack.md`:3696, 3701). The rewrite of the ends-when came from Roman: "please update guidance" (ruled: Roman, 2026-10-03 14:42, `plans/stack.md`:3702).
8. The origin: the refusal "on exactly these refs already" came in ebc9bafd, 2026-09-02, "fix(sandbox): the disputed test carries its run, harness facts are refused at encode" (git log -S). Its body answers "S0 walk eight", where "the Developer ... challenged the Tester's tests with the right refs and quotes, nine rounds running", and "a challenge repeated on identical refs after a held answer is refused toward escalation" (git show). The door counts per call (`plans/stack.md`:3696). Origin class: a frame that answered another wall: frame not found, wall: S0 walk eight's nine-round challenge.
9. After the end: not sure. Night 125's same-refs door, frame 132's new text, met the same seat and step: s156 "t2: the same challenge", "not followed" (`plans/night125-read.md`:92). Night 126, the fourth run after night 122, names the wall again by its frame: n126-W16, "frame 116, three challenges in one reply [C8] (guide: frame 116)" (extract a:833). The list does not link n126-W16 to this chain. Night 144's candidate D names frame 116's heading again, a refusal that "ended Developer wakes s470 and s474 while a second red test ... had no challenge" (`plans/stack.md`:3705), outside the three reads.

Row: Ended | same | 1 | read confirms count | S0 walk eight | origin frame: none

### Chain 17: n113-W5, 4 turns, firm

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "stub of a long call reply stubs again to nothing [C7] (guide: frame 117)" (`plans/method/turns-list-2026-11-10.md`:339). First turn n113, last turn n119, 4 turns: n113, n115, n116, n119. The wall lines: n115-W6 "stubbed replies with a call rise to 87 prompts", n116-W7 "19 prompts hold a stubbed reply with a call", n119-W15 "51 turns hold a stubbed reply", all "[C7] (guide: frame 117)" (extract a:497, 533, 559, 637). The chain is one wall, a count of one sign: a results block whose reply stub is `[your reply of an earlier turn]` (`plans/stack.md`:3686, 3691).
2. The state at the end: Ended. The chain's last naming is n119, but the reads of nights 120 and 121 count the same sign under frame 117: "52 turns in 13 sessions hold `[your reply of an earlier turn]`, a count of the sign only" and "93 turns in 27 sessions" (`plans/night120-read.md`:158, `plans/night121-read.md`:135). No later night read holds the stub text or "frame 117" (grep over `plans/night1[2-7]*-read*.md`, absence only). The reads of nights 122, 123 and 124 do not hold the word "stub" (grep). So three runs after night 121 do not name it. The silence rests on absence alone. Those reads do not say they counted the sign.
3. The conditions at the end: same. Nights 122 to 124 ran on the same repository, requests and kind of run (extract a:706 on). No change to `_stub` landed between 2026-10-01 and 2026-10-25 (`git log -L` on `_stub` in `rota/core/runner.py`).
4. The changes:
   - Frame 117, "A stub of a long call line stubs again to no call" (`plans/stack.md`:3682). Records only: "pushed by 3d6e6173" in 289e0d59, 2026-10-03, and status lines with counts (`plans/stack.md`:3689-3692). Kind: a rule or a record only. `git log --grep "frame 117"` gives 289e0d59 only. The reads after it: night 113 "14 prompts in 6 sessions", night 116 "19 prompts in 7 sessions ... and 87 in 10 on night 115" (`plans/stack.md`:3691-3692).
   Not counted, because it came after the end and aims at another change: 25e35498, 2026-10-25, "fix(native): keep native calls in stubs, transcripts, keys and reports".
   Count: 1.
5. The last change before the end: frame 117's record, the night 116 status line of 2026-10-04 10:47 (`plans/stack.md`:3692). Evidence: absent only. No read after night 121 counts the sign, and no record says why the count stopped.
6. The place of the changes: the sign shows in the prompt that `_stub` in `rota/core/runner.py`:1796 builds, "which cuts each call line to `_STUB_CALL_CHARS`, 200 characters" (`plans/stack.md`:3684). Frame 117 touched no file.
7. Who started each change: a frame's pass, "found by frame 108's pass 2", and "pushed by 3d6e6173" (`plans/stack.md`:3684, 3689). The night counts came from the night reads.
8. The origin: `_STUB_CALL_CHARS` and the stub text `[your reply of an earlier turn]` came in bdaca787, 2026-10-01, "fix(runner): the window evicts old replies before results and keeps the newest read of each file" (git log -S). Its body: "Frame 100. On night 99 s132 spent 20 of 25 turns on code.source reads of the same spans", and "old replies become stubs of their TOOL lines" (git show). 94343981 the same day, "the stub reads calls inside a line", is frame 100's review fix. Origin class: a frame that answered another wall: frame 100, wall: night 99's repeated `code.source` reads of the same spans.
9. After the end: not sure. The reads of nights 122 to 124 hold no "stub" line (grep). Window drops are counted later as another sign, for example night 159's "window drops (198 turns, 33 sessions)" in n159-W9 (`plans/night159-read.md`:224), outside the three reads.

Row: Ended | same | 1 | absent only | frame 100 stub | origin frame: 100

### Chain 18: n118-W1, 4 turns, firm

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "`tests.load` shows a red inherited test as passing [C6] (guide: frame 130)" (`plans/method/turns-list-2026-11-10.md`:340). First turn n118, last turn n121, 4 turns: n118, n119, n120, n121. The wall lines: n119-W11 "bg_3 wakes show 34 passing project tests as red", n120-W6 "five of nine fix wakes show a red project test as passing", n121-W7 "16 of 16 fix wakes show two red project tests as passing", all "[C6] (guide: frame 130)" (extract a:604, 633, 668, 696). Night 119 shows the sign in the other direction, green shown as red. Frame 130 records it as the same query: "The query fails in the other direction" (`plans/stack.md`:3659). The chain is one wall at one place.
2. The state at the end: Ended. The last naming is n121. The extract says "n121-W7: not named in n122, n123, n124" (extract a:701). So three runs after the last naming do not name it. The record shape behind it is counted later as invariant I4, "Frame 130's shape", on nights 126 to 137, for example "71 I4 rows" (`plans/night130-read.md`:111, 181; `plans/night137-read.md`:237). That count is a row shape, not the wake sign.
3. The conditions at the end: same. Nights 122 to 124 ran on the same repository, requests and kind of run. The sign needs a red project test in one batch and a green run of it in another batch (`plans/stack.md`:3654). The reads of nights 122 to 124 do not say whether that condition occurred.
4. The changes:
   - Frame 130, "The Developer's fix wake shows a red project test as passing" (`plans/stack.md`:3651). Records only: pushed in 45b88a8b, 2026-10-04 18:00, and a status line of 2026-10-05 01:25 (`plans/stack.md`:3658-3659). Kind: a rule or a record only. The reads of nights 120 and 121 name the sign again after it (extract a:668, 696).
   - Frame 144's scenes and invariants, a304084b, 2026-10-05, and 0118233f, 2026-10-06, "the ten invariants and night 126's rows", which name frame 130 (git log --grep "frame 130"). Kind: the harness or the measure. Night 127: "I4 ... 68 ... Frame 130's shape" (`plans/night127-read.md`:87).
   - Frame 210, after the end: a2b70a84, 2026-10-12, "a test's latest run is the latest run in the batch that asks", files `rota/roles/api.py`, `rota/core/sandbox.py`, `rota/core/runner.py`, `rota/roles/principal.py` (git show --stat). Kind: other code of rota, a query at six readers. The frame "closed on night 143: the wake showed the right state of every inherited test in 23 of 23 wakes" (`plans/archive/stack-2026-10-12.md`:14).
   Count: 3. Two fall before the end, and neither changes the query.
5. The last change before the end: frame 130's record of 2026-10-05 01:25 (`plans/stack.md`:3659), with the measure commits of frame 144 after it. Evidence: absent only. The query had no batch filter until a2b70a84 on 2026-10-12 (the diff adds `AND batch_id = t.batch_id`), so no code change explains the silence of nights 122 to 124.
6. The place of the changes: the sign shows in the wake's `tests.load` block, built by the latest-run subquery in `tests_load` in `rota/roles/api.py`, about line 7313 at a2b70a84's parent (`plans/stack.md`:3653 names "about line 5651"). Frame 130 touched no file. Frame 144's invariants touch the test scenes, another place. Frame 210 touches the same function and subquery, and five other readers.
7. Who started each change: frame 130 came from a read of a run, "found by night 118's read", "pushed by 419281dc" (`plans/stack.md`:3653, 3658). Frame 144's invariants came from frame 144's plan, not found in detail here. Frame 210 came from a read of a run: "pushed by 91506043 from night 141's read" (`plans/archive/stack-2026-10-12.md`:9).
8. The origin: the subquery `SELECT id FROM test_runs WHERE test_id = t.id ORDER BY attempt DESC, rowid DESC LIMIT 1` came in 5fe70e13, 2026-08-10, "fix(testkit): ids the model cannot guess, and a prompt that fits" (git blame at a2b70a84's parent, lines 7311-7314). That commit names no wall of this kind. Origin class: rota's first design.
9. After the end: not in the next three reads, which do not name it (extract a:701). Later the same sign at the same place comes back under another frame: night 141, "s198 read 35 of 35 passing while 2 were red", frame 210 (`plans/archive/stack-2026-10-12.md`:5).

Row: Ended | same | 3 | absent only | rota's first design | origin frame: none

### Chain 19: n122-W1, 4 turns, firm

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "bg_1 holds the seat at attempt 5, key quarantined, nothing starts [C?] (F87)" (`plans/method/turns-list-2026-11-10.md`:341). First turn n122, last turn n125, 4 turns: n122, n123, n124, n125. The wall lines: n123-W5 "bg_1 running at attempt 8, key quarantined, nothing starts", n124-W6 "bg_1 running at attempt 4, key quarantined", n125-W4 "the bound's exit ends at frame 87's wall", all "(F87)" (extract a:713, 736, 760, 789). The reads name one shape: "bg_1 stands `running` at attempt 8 of 10 with its key quarantined, and `tick_batch_start` starts nothing" (`plans/night123-read.md`:12; `plans/night124-read.md`:13; `plans/night125-read.md`:41). The chain is one wall. Night 122 calls it "frame 87's open finding of night 100, and not a new wall" (`plans/night122-read.md`:7).
2. The state at the end: Ended. The last naming is n125. Night 126: "Known walls with 0 cases: frame 87, bg_1 was parked and bg_2 started" (`plans/night126-read.md`:229). Nights 127 and 128 do not name it (extract a:801), and their reads list only new walls, so they count as "not named" and not as "gone". So three runs after the last naming, nights 126, 127 and 128, do not name it, and two of them list only new walls.
3. The conditions at the end: same requests, repository and kind of run. One condition differs on night 126 by its own read: "The two nights differ in the cap, not in a repair: night 125 stopped at attempt 6 by the tick cap, and night 126 reached attempt 11 by the loop cap" (`plans/night126-read.md`:164).
4. The changes: no change after the chain's first turn aims at this shape. Frame 87, "A quarantined key outlives the batch's deferral, and its resume wakes nobody" (`plans/stack.md`:3940), built passes 1 to 7 on 2026-09-30, `0564c87` to `a8dbe10`, merged at `4cde741` (frame 87 status lines 2026-09-30 04:49 to 11:29). Those passes came before the chain and left this shape open: "Outside the ruling, left open: a running batch below its cap with a quarantined key still holds the seat" (frame 87 status 2026-09-30 04:49). A search of the commits of 2026-10-04 to 2026-10-20 for "quarantin", "holds the seat" and "frame 87" finds no change to that rule (git log --grep). Frame 87 was "parked at night 158's read" (frame 87 status 2026-10-21 16:23). Count: 0.
5. The last change before the end: none aimed at this shape. Evidence: absent only. Night 126's read gives a reason that is not a change: the batch reached the loop cap, the ladder ran through, "and the park freed the place" (`plans/night126-read.md`:164).
6. The place of the changes: the sign shows in the scheduler: `tick_batch_start` "starts no batch while a running batch has a head commit", and "No predicate wakes a seat on such a batch" (`plans/night123-read.md`:90; `plans/night122-read.md`:7). The parked path is `parked()` in `rota/core/scheduler.py`:1487 (`plans/night126-read.md`:164). No change of cell 4 exists to place.
7. Who started each change: not applicable, no change. Frame 87 itself came from a read of a run, "found by night 94's read" (`plans/stack.md`:3941).
8. The origin: `tick_batch_start` came in 210649a7, 2026-08-09, "feat(scheduler): schema, atomic session commit, scheduler and boot" (git log -S "def tick_batch_start"). `quarantine_overrun` came in 883d6c7b, 2026-08-11, "fix(scheduler): abandonment settled after the frontier had already answered", which answered "The oauthlib run went quiescent at 62 sessions" (git show). Frame 87's pass 1 left the running-batch shape open (cell 4). Origin class: a frame that answered another wall: frame not found, wall: the oauthlib run's quiescence of 2026-08-11, on top of rota's first design of the scheduler.
9. After the end: not sure. Night 126 counts 0 cases (`plans/night126-read.md`:229). Nights 127 and 128 list only new walls. Later, frame 142 "stops night 135 in walk 2 on a quarantine loop" (commit 2a9f0681), another quarantine wall outside the three reads.

Row: Ended | same | 0 | absent only | oauthlib run quarantine | origin frame: none

### Chain 20: n150-W6, 4 turns, firm

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "frame 250's approve refusal on "not as a separate change" [C8] (W6)" (`plans/method/turns-list-2026-11-10.md`:342). First turn n150, last turn n153, 4 turns: n150, n151, n152, n153. The wall lines: n151-W3 "frame 250's present fire on m46", n151-W4 "frame 250's clarify misses, m98 and m143 [C8]", n152-W11 "m75 approved on the confirm route [C8]", n153-W15 "m81's approve of cr_3, frame 250 [C1]" (`plans/method/turns-list-extract-b-2026-11-10.md`:462, 483, 484, 519, 549). The chain holds two walls, and I split it.
   - Part A, n150-W6 and n151-W3: frame 250's own door fires wrong on the present route. Night 150: "the approve refusal fired 6 times on 4 replies, 2 right ..., 4 wrong ... all on "and not as a separate change"" (`plans/stack.md`, frame 250 status 2026-10-16 07:01). Night 151: "1 wrong, m46" (status 2026-10-16 17:36).
   - Part B, n151-W4, n152-W11 and n153-W15: an approve of a row his words fault lands, on the clarify route or the confirm route, and no door refuses it. Night 151: "the clarify route approved 3 faulted rows on 2 of 6 replies, m98 and m143, with 0 fires". Night 152: "the confirm route approved m75 ... because that route has no fault door". Night 153: "m81 on cr_3" (frame 250 status 2026-10-16 17:36, 22:30, 2026-10-17 04:31).
   Part A is a false refusal by the fix. Part B is the sign that the fix aims at. The extract links them as "same cause" (extract b:470, 498).
2. The state at the end:
   - Part A: Ended. The last naming is n151. Night 152: "the present route fired 1 time, m87, right" (frame 250 status 2026-10-16 22:30). Nights 153 and 154 give no count of the present route (grep of `plans/night153-read.md` and `plans/night154-read.md`, absence only).
   - Part B: Ended. The last naming by id is n153. Night 155 names it as "row 5" with no id: "The clarify "Go ahead and build" answers m27, m58 and m84 approved the item while he held approval back" (`plans/night155-read.md`:127; extract b, n153-W15 "met in n155 as row 5"). The reads of nights 156, 157 and 158 hold no "frame 250" and no clarify approve line (grep, absence only). Frame 250 was parked: "no night read has counted it since 2026-10-18 or before" (frame 250 status 2026-10-21 16:23).
3. The conditions at the end: Part A, same. Part B, same. Nights 152 to 158 ran on the same repository and kind of run, and the requests change at night 163, later.
4. The changes:
   - Frame 250, pass 1: f0b2924c, 2026-10-16 00:49, "fix(api): the verdict door refuses an approve of a line the words fault", `rota/roles/api.py` `_line_refusal` (git show --stat; frame 250 status 2026-10-16 00:49). Kind: a door. The clarify route was "not built, because the fault reading refused 40 of 69 right approves" (same status).
   - Frame 250, pass 1b: d3154135, 2026-10-16 02:35, "the approve check skips a merged or abandoned change's line only" (git log --grep "frame 250"). Kind: a door. Night 150 is the next read: Part A's 4 wrong fires, and "the clarify route 1 of 13" (frame 250 status 2026-10-16 07:01).
   - Frame 250's pass 2, "the "not" reading", was set as sprint rows 8.5, 9.9, 10.11 and 11.12 and never built (frame 250 status lines 2026-10-16 07:01 to 2026-10-17 04:31; no code commit in `git log --grep "frame 250"` between d3154135 and 6e72b8b9).
   Not counted, because it aims at another wall: 6e72b8b9, 2026-10-23, "a clarify reply rules the rows the asker named", from night 158. Its body says "The check that refuses an approve against the words of a clarify is held ... it fires on 70 of 125 clarify rulings that approve every row".
   Count: 2, the same two for Part A and Part B. For Part A the two passes are the origin of the sign.
5. The last change before the end: Part A, d3154135. Evidence: a read confirms with a count, night 152's "1 time, m87, right" (frame 250 status 2026-10-16 22:30), on one night only. Part B, d3154135. Evidence: absent only. The clarify route got no door, and no read after night 155 counts the sign.
6. The place of the changes: Part A's sign shows in `_line_refusal` in `rota/roles/api.py`, the door that the two passes built, so the changes are at the same place. Part B's sign shows in `rulings_rule` in `rota/roles/api.py`, "which skips every clarify reply at the line reading, `not is_clarify`" (`plans/stack.md`:2837), and on the confirm route, "that route has no fault door" (frame 250 status 2026-10-16 22:30). The passes touch `_line_refusal` on the present route, another function in the same file.
7. Who started each change: a read of a frame, "pushed by 4754aaec from frame 243's scope read" (frame 250 status 2026-10-15 01:33). A row of a sprint: "Sprint 7, row 4", "claimed by 4492a9c1 for sprint 7's row 4" (status 2026-10-15 16:24, 23:56).
8. The origin: Part A: f0b2924c, frame 250's own door. Origin class: a frame that answered another wall: frame 250, wall: the clarify verdict that approves a yes-with-correction, night 148's m81 (`plans/stack.md`:2837). Part B: the skip `not is_clarify` came in a268266b, 2026-09-18, "fix(liaison): a ruling parks the word, and the class of a ledger row is a column", which answered "the term-collision loop" found by "A read-only diff review of 6895000" (git log -S, git show). Origin class: a frame that answered another wall: frame not found, wall: the term-collision loop of 2026-09-18.
9. After the end: Part A, not sure. No read of nights 152 to 154 names a wrong fire of the door. Part B, yes, without an id: night 155's row 5 is the same sign (`plans/night155-read.md`:127). After night 155, not sure. Night 158 led to 6e72b8b9, a clarify door that "keyed on tst_02 alone" (6e72b8b9 body), the same function under another wall.

Row: Part A: Ended | same | 2 | read confirms count | frame 250 door | origin frame: 250
Row: Part B: Ended | same | 2 | absent only | term-collision loop fix | origin frame: none

### Chain 21: n151-W5, 4 turns, firm

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "the parser blames the words [C9] (W5, N1)" (`plans/method/turns-list-2026-11-10.md`:343). First turn n151, last turn n154, 4 turns: n151, n152, n153, n154. The wall lines: n152-W7 "s290's write with no closing bracket [C9]", n153-W4 "CYCLE 1's dict value, frame 266 [C9]", n153-W5 "the escaped quote, frame 266 [C9]", n154-W7 "the dict value with escaped words, frame 266 [C9]" (`plans/method/turns-list-extract-b-2026-11-10.md`:485, 515, 538, 539, 573). Each wall is a shape of one sign: the call parser's unterminated-argument refusal points the seat wrong, and the seat repeats the call. Frame 266 holds every shape as "a case of this frame and not a new one, cause 9" (`plans/stack.md`, frame 266 status 2026-10-16 21:58). The seats differ: the Liaison on night 151, the Critics and the Developer on nights 152 to 154 (frame 266 status 2026-10-16 22:30, 2026-10-17 04:31). The chain is one wall.
2. The state at the end: Open, not sure. The extract links n154-W7 to night 155 "as rows 8 and 11", with no id (extract b, n154-W7 item 8). Night 155 also holds n155-W8 "cycle 1, the Critic's `lines` dict with a quote" and n155-W11 "onboarding parse loops" (grep of extract b). Night 158's frame 266 status: "The same shape as night 155", Critics s124 to s126 and s270 repeated a call that the parser refused (frame 266 status 2026-10-21 14:33, 15:49), and night 158 lists n158-W3 "the Critic's review, a value closes its quote early [C9]" (extract b, night 158). Night 160: "The one session that did is the Tester s220" (frame 266 status 2026-10-24 01:11). Night 165's W-E read "lands on this frame's site", 6 of 6 night sessions (frame 266 status 2026-10-25 03:32). Night 175, one of the last three runs, names W15 "Parse refusals and cut replies", "11 `rulings.rule` parse refusals in s163, s164, s177, s314, s316" (`plans/night175-read.md`:71). That read does not say the seats repeated the call, so the match is not sure.
3. The conditions at the end: conditions changed. The sign runs past night 163, when the requests changed, to night 175, when the nights stopped (cell 2). For the chain's own last firm naming, n154, the next runs, nights 155 to 157, had the same conditions.
4. The changes, all frame 266, "The call parser's refusal of an unterminated argument blames the words" (`plans/stack.md`:2635), all in `rota/llm/toolproto.py`, kind: a refusal:
   - Pass 1 and 1b: 74251f79 and ce658cdb, 2026-10-16, `_missing_close`, "the refusal names where the open string starts" (git log --grep "frame 266"). Night 152: "0 of 71 Liaison sessions ended on a repeated parse refusal, against 1 of 81 on night 151; over every role 4 did", "the `_missing_close` text fired 0 times" (frame 266 status 2026-10-16 22:30).
   - Pass 2: 3c38f2e5, 2026-10-16 22:50, `_short_close`, a short closing quote run (status 2026-10-16 22:51).
   - Pass 2b: 0617afda, 2026-10-17 01:58, `_no_close_bracket`. Night 153: "0 of 67 Liaison sessions", "over every role 5 did", "`_short_close` fired 3 times, all right, and the next call fixed 2 of 3" (status 2026-10-17 04:31).
   - Pass 3 and 3b: 58edbb6a and 7c0b2f32, 2026-10-17 12:24 and 12:34, `_open_inner` and `_escaped_open`. Night 154: "1 of 89 Liaison sessions ended on a repeated parse refusal", "6 sessions of any role; pass 3's dict text fired 0 times, the escaped-quote text fired once, s206, and the next call did not fix it" (status 2026-10-17 16:40).
   Not counted, because it names another frame: 566b945d, 2026-11-06, "frame 362, parse_args reads a list as it is written before the rewrites".
   Count: 4.
5. The last change before the end: not applicable, the state is open, not sure. Evidence: not applicable. The frame's count for the Liaison holds at night 166: "Frame 266, the parse refusal. Holds for the Liaison. 0 of 47 Liaison" (`plans/night166-read.md`:190).
6. The place of the changes: the sign shows in `extract` in `rota/llm/toolproto.py`, the unterminated-argument refusal, "lines 1008 to 1048", "and not `rota/roles/api.py` as the Site line says" (frame 266 status 2026-10-16 17:41). Each pass adds a branch to the same function.
7. Who started each change: a read of a run, "pushed from night 151's read" (frame 266 status 2026-10-16 17:36). Rows of a sprint: "sprint 9, row 2" and "sprint 11 row 4" (`plans/stack.md`, frame 266 Sprint line; status 2026-10-17 12:09). Passes 2 and 2b came from night 152's cycle read and its count (status 2026-10-16 21:58, 22:30). Pass 3 came from night 153's walls W4 and W5 (status 2026-10-17 12:09).
8. The origin: the parser and its `TOOL:` protocol came in 231afe4c, 2026-08-09, "feat(sandbox): namespaces built from edges, and the TOOL: protocol" (git log -S "unterminated argument list"). The words that blame a quote came in 9e9f123c, 2026-09-09, "fix(rota): four facts from the seat", "From tipsAH, 2026-09-09", and in 6333441b, 2026-09-12, "a quote that swallows the next argument is named", after "L1-DV-apply-the-answer on llama" (git log -S "a quote inside", git show). Origin class: a frame that answered another wall: frame not found, wall: the tipsAH run of 2026-09-09 and the L1 case on llama of 2026-09-12.
9. After the end: yes, under other names. Night 155 holds n155-W8 and n155-W11 (extract b), and night 158 holds n158-W3 (cell 2). The list puts n155-W8 at the head of a "not sure" chain of 5 turns, n155 to n161 (`plans/method/turns-list-2026-11-10.md`:355).

Row: Open, not sure | conditions changed | 4 | not applicable | tipsAH parser words | origin frame: none

### Chain 22: n151-W12, 4 turns, firm

Reader: the lead.

1. The wall: "frame 260's refusal text [C9] (W12)" (`plans/method/turns-list-2026-11-10.md`:344). First turn night 151, last turn night 156, 4 turns: n151-W12 (`plans/night151-read.md`:623), n152-W12 (`plans/night152-read.md`:734), n154-W9 (`plans/night154-read.md`:510), n156-W2 (`plans/night156-read.md`:146). The first three are one sign at one place: the surface door refuses a `src.` import, and its text names `click.testing`, the first import in sort order. n156-W2 is a wider wall: "bg_3's tests_failing loop: tests hard-coded 3.10.0; the surface-import door refused 14 encodes". Its read places "frame 260 for the import door's prefix" as one part. The chain holds as one wall at the surface door. No split.
2. The state at the end: Ended. The last naming is night 156. Night 157: "not sure (n157-W1)" (`plans/method/turns-list-extract-b-2026-11-10.md`:161). Nights 158 and 159 do not name frame 260, by absence in the extracts. Frame 260 has no status line between 2026-10-17 16:40 and 2026-11-08 10:49 (`plans/stack.md`, frame 260).
3. The conditions at the end: same. Nights 157 to 159 hold the R1 requests, the same repository and the same kind of run.
4. The changes: no change of code aimed at this wall in the window from night 151 to night 159. Frame 260 moved through sprint rows only: "Sprint 9, row 4" (status 2026-10-16 17:36), "Sprint 10, row 12" (22:30), "Sprint 12, row 6" (2026-10-17 16:40), and "Frame 260, the surface door's prefix: 2 cycles" in the plan after night 156 (`plans/stack.md`:1178). `git log --grep` on "keep_root", "surface door", "src. prefix" and "frame 260" from 2026-10-16 to 2026-10-24 finds only 14ed7303, "the surface door refuses an existing callable beside the new one", which is frame 257's pass 1c (`plans/archive/stack-2026-10-24.md`, frame 257, status 2026-10-24 02:53). This cell rests on absence. Count: 0.
5. The last change before the end: none. Evidence: absent only.
6. The place of the changes: not applicable. The place of the sign: the surface door in `rota/roles/api.py`, and `keep_root` of `module_of` and `_dotted_module` (`rota/roles/api.py`:22843 and 23002 today), "about lines 7618 and 7823" at the time (`plans/stack.md`, frame 260, Site line).
7. Who started each change: not applicable.
8. The origin: `keep_root` comes from 01ff078f, 2026-09-25, "fix(roles): the encode Wall names an import that works from an uninstalled root". Its body says: "The diff review of frame 82 found the Wall stripped src/ and named a module pytest cannot import from the case's fake repository" (`git show 01ff078f`). Frame 260 itself was "pushed from frame 222's pass 1" (status 2026-10-16 03:29). Origin class: a frame that answered another wall: frame 82, the encode Wall that named a module pytest cannot import.
9. After the end: not sure. Night 157's W1 (4) names another encode door at the Tester's step: "The encode door refused 6 encodes with "this test calls confirm() under pytest, where stdin is captured"" (`plans/night157-read.md`:195). On 2026-11-08 frame 260 is named again for dry runs 6c and 7: "W4, the Tester's encodes were refused until the key quarantined" (`plans/stack.md`, frame 260, status 2026-11-08 10:49).

Row: Ended | same | 0 | absent only | frame 82 | origin frame: 82

### Chain 23: n152-W1, 4 turns, firm

Reader: the lead.

1. The wall: "line numbers from `recent_chat` [C4] (W1, N1)" (`plans/method/turns-list-2026-11-10.md`:345). First turn night 152, last turn night 156 by the list, 4 turns: n152-W1, n153-W14, n155-W10 and n156-W8 (`plans/night155-read.md`:132, `plans/night156-read.md`:152). The four walls are one sign: the Liaison rules the lines of an earlier page that `recent_chat` carries. Frame 272 holds all four. The second look finds one more naming: n159-W3, "`recent_chat` carried m106 with its line numbers to page m116, and s239 and s240 contested lines 1 to 3 of m116 from it" (`plans/night159-read.md`:218). The list marks that link "not sure" (`plans/method/turns-list-extract-b-2026-11-10.md`:161). Frame 305's interview also places night 158's s209 at this cause (frame 272, status 2026-10-23 14:08). With n159, the chain holds 5 turns. No split.
2. The state at the end: Ended. With n159 as the last naming, nights 160, 161 and 162 read "Met: 0 first sessions that contest a line from an earlier page's reply, from 2", then "Met on night 2", and the frame closes on night 162 (`plans/archive/stack-2026-10-24.md`, frame 272, status 2026-10-24 01:11, 05:58 and 10:32). By the list's links alone, the last naming is night 156, and nights 157 to 159 do not name it.
3. The conditions at the end: same. Nights 160 to 162 hold the R1 requests, the same repository and the same kind of run.
4. The changes, in order:
   - Frame 272, passes 1 to 1c and the page-id fix: c22e8162 "fix(runner): a recent_chat reply names its page and its rows", dfe2a6cb and 599c30ee (2026-10-23 19:08), and a0a1c1ec "fix(runner): the landing block carries no page id" (19:52) (`git log`; frame 272, status lines of 2026-10-23 18:26 to 19:55). Files: `rota/core/runner.py` (`_recent_chat`) and `rota/roles/principal.py` (the saved page order). Kind: other code of rota, in the prompt that a seat reads. On night 160's commit 695e8be7. Night 160: "Met: 0 first sessions that contest a line from an earlier page's reply, from 2".
   Between night 152 and night 159 the frame moved through a sprint row only, "Sprint 11, row 6" (status 2026-10-17 04:31). Count: 1.
5. The last change before the end: a0a1c1ec, with c22e8162, dfe2a6cb and 599c30ee. Evidence: a frame closes on a count: "closed on night 162's read: met on nights 160, 161 and 162, its night 3" (frame 272, status 2026-10-24 10:32).
6. The place of the changes: the change touches `_recent_chat` in `rota/core/runner.py`, where the wake gets the old line numbers. The sign shows at another place: the refusals of `rulings.rule` in `rota/roles/api.py`, "'2' is not a line of the page" (frame 272, status 2026-10-18 01:18).
7. Who started each change: a row of a sprint: "held by this session, sprint 16 row 4" (frame 272, status 2026-10-23 18:26). The fix it names comes from frame 305's interview of night 158's s209 (status 2026-10-23 14:08). The frame was pushed from the read of night 152 (status 2026-10-16 22:30).
8. The origin: `_recent_chat` comes from 7a2c34b7, 2026-08-18, "feat(prompt): give Liaison converse mode a short chat memory" (`git log -S "def _recent_chat"`). The commit names no frame or wall. Origin class: rota's first design.
9. After the end: not sure. The closing count reads 0 on nights 160 to 162. Night 163's count for frame 305 names "1 wrong approve" at the Liaison's ruling step (frame 305, status 2026-10-24 18:19).

Row: Ended | same | 1 | frame closes count | rota's first design | origin frame: none

### Chain 24: n166-W3, 4 turns, firm

Reader: sub-agent, part b (`plans/method/chains-read-extract-b-2026-11-10.md`).

1. The wall: "an unasked answer wakes the Tester before the batch exists [C8] (W-C)" (`plans/method/turns-list-2026-11-10.md:346`; `plans/night166-read.md:211`). First turn night 166, last turn night 173, 4 turns. The walls are n166-W3, n169-W3, n170-W7, n173-W10 (`plans/night169-read.md:64`, `plans/night170-read.md:63`, `plans/night173-read.md:67`). Each names `msg.answer_tester` sent from the criteria tick before a batch exists, and a Tester woken on it whose writes the doors refuse. Night 170 says "as night 169's W3". The sign and the place are the same in all four, so the chain holds one wall.
2. The state at the end: Open by the rule, because night 173 is one of the last three runs of the night series. Only two night runs follow it. Night 174 counts "0 sessions; 0 fault rows", and "The answer door refused 4 `msg.answer_tester` calls of the Terminologist s228" (`plans/night174-read.md:238`). Night 175 counts "0; 0", and "The first Tester, s227, woke after s224 started bg_3" (`plans/night175-read.md:204`). Dry1 names no such wall (extract c, dry1, item 4).
3. The conditions at the end: the nights after night 173 ran on the same requests, models and repository. The nights stopped after night 175, and dry1 is another kind of run (extract c, night 175, item 9). Conditions changed after night 175.
4. The changes:
   1. Before the chain is a change that the cell 8 origin names. Between night 166 and night 169 no change aims at the wall. Sprint 23 keeps it as row 5, "W-C, next sprint rank 2: the answer door refuses an unasked answer in every mode. 1 read, 1 to 2 build" (`plans/stack.md:658-659`). The night 169 read says "No. 328's Site is `tests.encode`, which refused right. A candidate, C6" (`plans/night169-read.md:64`).
   2. F25, frame 344's audit, merge 552490b1 at 2026-10-28 00:28, "land f25root, F25, offers held to the seat's mode". Kind: a door and a prompt check. The night 170 read places W7 under F25 (`plans/night170-read.md:63`). Built before night 172. Night 172 names no such wall (absent only). Night 173 names it again as W10, with 16 refusals and 12 fault rows (`plans/night173-read.md:67`).
   3. Sprint 33 row 4, W10 of night 173: f0642982 "a message to a Tester or a Developer lands only on an item with a built batch" and 308b257f "the parked check reads the one batch predicate", merged at eeb0db69, 2026-10-28 14:08. File: `rota/core/sandbox.py`. Kind: a door. It landed after night 174 ended at 13:58, so night 174 ran without it (night 174 ran on 3ac83acc, `plans/stack.md:233`).
   4. W10 pass 1e: 7f7a6d88 "the encode door asks for a batch and the send door for its commit", merged at 21d145df, 2026-10-28 17:05:19, 27 seconds before night 175 launched (git log). File: `rota/roles/api.py`. Kind: a door. The next read: "**W10, `_unbuilt_refusal`.** 2 refusals, both in s222, `msg.answer_tester` ... The refusal is right by its rule" (`plans/night175-read.md:160`).
   - Count: 3 (changes 2, 3 and 4).
5. The last change before the end: not applicable by the rule, because the chain is open. The records show the sign absent on night 174 before changes 3 and 4 landed (`plans/night174-read.md:238`; git log, eeb0db69 at 14:08 after the run end at 13:58). So night 174's 0 is not joined to changes 3 and 4.
6. The place of the changes: the sign shows in `msg.answer_tester` from the Terminologist's criteria mode and the Tester's wake on it. The answer door in the criteria-tick mode does not fire, and the same door in the relay mode does (`plans/night169-read.md:64`). Change 2 touches the offers of each mode, another place by its subject. Change 3 touches the message landing in `rota/core/sandbox.py`, the place where the answer lands. Change 4 touches the encode door and the send door in `rota/roles/api.py`, the place of the refusal that s222 met.
7. Who started each change:
   - F25: frame 344's audit, on Roman's message of 2026-10-27 14:08, "Go back and review them" (extract c, night 170, item 9).
   - Changes 3 and 4: a read of a run, sprint 33 row 4, "recommended on night 173's read": "W10 and W20, a Tester woken before any batch exists writes 12 fault rows, under F25 and F6. Counts, then reads" (`plans/stack.md:299-302`).
8. The origin: the route comes from a3f2f96e (2026-10-24 01:41), "fix(terminologist): the criteria mode holds the route to the Tester". Its message: "Frame 306, pass 1b, from review 1, finding 1 ... so the criteria mode now holds msg.answer_tester" (git show). The status line of frame 306 says the same: "`criteria.tools` holds `msg.answer_tester`" (`plans/stack.md:2477`). Frame 306 answered his notes about a check that became criterion text, night 160's W2 (`plans/frame306-provenance-wa.md:100`, "Night 160 W2 is the same wall"). Night 166 is the first naming, two days later. Origin class: a frame that answered another wall: frame 306, wall n160-W2.
9. After the end: not applicable by the rule. Night 175 names "W10, `_unbuilt_refusal`", 2 right refusals of `msg.answer_tester` in s222, at the same seat and step (`plans/night175-read.md:160`). The read does not count it as a wall. Not sure.

Row: Open | conditions changed | 3 | not applicable | frame 306 route | origin frame: 306

### Chain 25: n171-W2, 4 turns, firm

Reader: sub-agent, part b (`plans/method/chains-read-extract-b-2026-11-10.md`).

1. The wall: "the account's description row reaches his pages after a rewording [C?] (W2)" (`plans/method/turns-list-2026-11-10.md:347`; `plans/night171-read.md:59`). First turn night 171, last turn night 174, 4 turns. The walls are n171-W2, n172-W9, n173-W8, n174-W7. The signs differ, so this block splits the chain.
   - Part A, n171-W2 alone: s152, a Vision Keeper woken by an unrelated deliver, re-asserted the `how_it_works` row with new words, the door took it, and the row reached m65 and m94 as a draft (`plans/night171-read.md:59`). 1 turn.
   - Part B, rows from other work on a request's page: n172-W9, "m71 lines 6 to 24 were glossary and constraint rows" (`plans/night172-read.md:66`), and n173-W8, "m56 carried 8 glossary and 14 constraint rows on the walk 2 request" (`plans/night173-read.md:65`). n174-W7 names the same kind of rows on account pages only, under the heading "A word that means more than one thing here" (`plans/night174-read.md:66`). The night 174 read says "Same rows as night 173's W8, now on account pages only. The heading is new in these reads" (`plans/night174-read.md:211`). Turns n172 to n174, 3 turns.
   - The night 172 read joins the parts: "Same sign as night 171's W2, with other rows: glossary, constraint and claim rows on a request's page" (`plans/night172-read.md:154`). The rows, the seat and the page differ, so I read two walls.
2. The state at the end:
   - Part A: Ended. Nights 172, 173 and 174 name no rewording of the description row (extract c, nights 172 to 174, item 4). The link of night 172 names other rows.
   - Part B: Open. Night 174, one of the last three runs of the night series, named it (n174-W7). The request-page sign itself fell: "rows of other work on a request page 36 to 0" on night 174 (`plans/stack.md:235-236`). n174-W7 holds the rows on account pages.
3. The conditions at the end:
   - Part A: nights 172 to 174 ran on the same requests, models and repository. Same.
   - Part B: open. The nights stopped after night 175, and the dry runs are another kind of run. Conditions changed.
4. The changes:
   - Part A, change 1. hiwroot, from the read `plans/night171-how-it-works-read.md`: f25b6303 "keep an observed description row's words outside onboarding", 2fb92e9c, 575e09b5 and 46c23831, landed at 5521b809 and bba2f842 on 2026-10-28 01:27 to 01:30 (git log; `plans/archive/stack-2026-10-30.md:221`, `:240`). Part A of the build is "a gate in problem_assert refuses a new text on an observed description row on every wake except onboarding". File: `rota/roles/api.py`. Kind: a door. Built before night 172. The next read names no rewording of the row (absent only).
   - Part A count: 1.
   - Part B, change 1. F15, frame 344's audit, merge 38a44c39 at 2026-10-28 02:48, "land f15root, F15, one reader of which request owns a row", with 7f1c7b6b and b68f9196. File: `rota/roles/principal.py`. Kind: other code of rota. Built before night 172. The night 172 read places W9 under F15: 2 pages, 26 lines (`plans/night172-read.md:66`). Night 173 counts 2 pages, 36 rows (`plans/night173-read.md:65`).
   - Part B, change 2. P8 and P9, merge 3ac83acc at 2026-10-28 11:48, "land w89root, a page is about one request, P8 and P9 under Roman's ruling of 2026-10-28 09:10". Commits 03876804 "the account's rows reach him on the account's page", 65cbda09 "a row of no request is off a request's page", 0d0bc33d. File: `rota/roles/principal.py` and the roles code. Kind: other code of rota, the page. Night 174 ran on 3ac83acc. The next read: "rows of other work on a request page 36 to 0" (`plans/stack.md:235-236`), and the same rows now stand on account pages under a new heading (n174-W7).
   - Part B count: 2.
5. The last change before the end:
   - Part A: hiwroot at bba2f842. Evidence: absent only. No read after it counts rewordings of the row.
   - Part B: not applicable. Part B is open.
6. The place of the changes:
   - Part A: the sign shows in `problem_assert`, the door that compares words only, at `rota/roles/api.py` about 2042 to 2056 (`plans/night171-how-it-works-read.md`, section 1). Change 1 puts a gate in `problem_assert`. It touches the place of the sign.
   - Part B: the sign shows in the page body of a request, `render_page` in `rota/roles/principal.py`. Change 1 adds one reader of the owner of a row in `rota/roles/principal.py`. Change 2 moves the account's rows to the account's page in the same file. Both touch the place of the sign.
7. Who started each change:
   - Part A: a read of a run, `plans/night171-how-it-works-read.md` (status of 2026-10-27 23:31, `plans/archive/stack-2026-10-30.md:207`), in the sprint that ran on Roman's message of 19:40: "I want all the fixes implemented before the next night".
   - Part B, change 1: frame 344's audit, on Roman's message of 2026-10-27 14:08, "Go back and review them".
   - Part B, change 2: sprint 32 row 4, a read of a run (`plans/stack.md:349-351`), and Roman's ruling of 2026-10-28 09:10, "Yeah that's right", to the answer "the account's own rows, the glossary, the constraints and the claims, go on their own page and never on a request's page" (`plans/stack.md:2977`).
8. The origin:
   - Part A: the read names the same-words door in `problem_assert`, overlap 0.8, and the signoff that submits every draft (`plans/night171-how-it-works-read.md`, sections 0 and 1). `_prose_words` comes from c6eb0274 (2026-09-01, "fix(sandbox): the intake fork"). The commit that set the 0.8 threshold is not found by this pass. Origin class: not found.
   - Part B: the rows come from `tick:observed_entries`, declared in 9c971e84 (2026-08-09, "feat(predicates): declare every predicate; no state is a dead end"). The night 174 read: "The rows are the survey's content, frame 179 by the facts page's unplaced list" (`plans/night174-read.md:211`). Origin class: rota's first design.
9. After the end:
   - Part A: n171-W1, in the same night, names the same row on another sign, "The contested description row cannot be amended" (`plans/night171-read.md:58`). After night 171, dry1-W5 names "how_it_works repeats; the landed approve is never read" (extract c, dry1, item 4), far after the end. Not sure.
   - Part B: not applicable. Part B is open. dry1-W15, "page m145 puts 15 re-survey constraints to the seat", meets n174-W7 by a "not sure" link (extract c, night 174, item 8).

Row (Part A): Ended | same | 1 | absent only | not found | origin frame: none
Row (Part B): Open | conditions changed | 2 | not applicable | rota's first design | origin frame: none

### Chain 26: n173-W3, 4 turns, firm

Reader: sub-agent, part b (`plans/method/chains-read-extract-b-2026-11-10.md`).

1. The wall: "the constraint tick is quarantined at the start [C?] (W3, F20)" (`plans/method/turns-list-2026-11-10.md:348`; `plans/night173-read.md:60`). First turn night 173, last turn dry1, 4 turns. The walls are n173-W3, n174-W10, n175-W13 (`plans/night174-read.md:69`, `plans/night175-read.md:69`), each "`-|tick:constraint_zero|` at 3", and dry1-W2, "constraint zero quarantined; the predicate wants every area" (`plans/dry1-first-wall-read-2026-10-31.md:6`). The key is the same in all four, so the chain holds one wall. The same key is Part A of chain 2 on nights 166 to 171, and n160-W8 names it on night 160. So the wall is older than this chain.
2. The state at the end: Ended. The chain crosses from the night series to the dry run series at dry1. dry2, dry3 and dry4, the three runs after dry1, name no such wall (extract c, dry1 item 8, "dry1-W2 to W4 ... not met in the next three reads"). The dry3 read lists "`constraint_zero n=1`" as outstanding, not quarantined (`plans/dry3-wall1-read-2026-11-02.md:42`).
3. The conditions at the end: the last night naming is night 175, and the nights stopped there. Dry1 ran on click, the same repository as the nights, with the session in the Principal seat (`plans/archive/stack-2026-11-02.md:195`). dry2 ran on tips, and dry3 and dry4 on other repositories (extract c, dry2 to dry4, item 2). The chain crosses from one series to the other, and the repository changed after dry1. Conditions changed.
4. The changes:
   1. F20 with F21, frame 344's audit, merge 82d426c4 at 2026-10-27 16:48 (the same change as chain 2, Part A). It landed before night 172, before this chain's first naming. The audit's proposal names "the constraint tick at onboarding (nights 160, 166 to 170)" and wants it at 0 over 3 nights (`plans/rootfix-audit-2026-10-27-b.md:42`). Kind: other code of rota. The night 173 read places W3 under F20, "Same as the F20 row's nights" (`plans/night173-read.md:175`). Nights 173, 174 and 175 each count the key at 3.
   2. Frame 354, commit e7016e65 at 2026-10-31 17:27, "fix(onboarding): constraint zero settles, and a quarantine report is never an empty page". Files: `rota/core/predicates.py`, `rota/onboarding/boot.py`, `rota/core/scheduler.py`, `rota/roles/api.py`, `rota/roles/principal.py`, `rota/core/sandbox.py`. Kind: other code of rota, and a door that refuses a present with no refs. The commit's own run: "constraint zero fired twice with refs and was never quarantined". Frame 354 closed on 2026-11-01 08:28: "condition 2 settled 1 of 1" (`plans/archive/stack-2026-11-01.md:100`). dry2 to dry4 name no such wall.
   - Count: 2.
5. The last change before the end: frame 354 at e7016e65. Evidence: a frame closes on a count. Frame 354's Ends-when holds "the predicate and the refresh use one rule for an area with code, so constraint zero settles and no quarantine row lands, after one onboarding replay confirms the cause" (`plans/archive/stack-2026-11-01.md:40`), and it closed on "condition 2 settled 1 of 1" (`:100`). The later dry runs do not name the key, but they ran on other repositories.
6. The place of the changes: the sign shows in the predicate `constraint_zero` at `rota/core/predicates.py` (about line 1880 at the read) and in `refresh_constraint_zero` at `rota/onboarding/boot.py` (about line 224) (`plans/dry1-first-wall-read-2026-10-31.md:26`). Change 1 touches the key readers in `rota/core/scheduler.py` and the word tables, another place. Change 2 touches the predicate and the refresh through `boot.coded_areas`, the place of the sign.
7. Who started each change:
   - F20 with F21: frame 344's audit, on Roman's message of 2026-10-27 14:08, "Go back and review them".
   - Frame 354: a read of a run, `plans/dry1-first-wall-read-2026-10-31.md`, pushed in a79fd411. The dry run itself came from Roman's ruling of 2026-10-31 00:58: "I will not sit in the seat untill it delivers multiple changes on multiple repos and is responsive. Use it yourelf" (extract c, night 175, item 9).
8. The origin: the same as chain 2, Part A. The predicate exists from 210649a7 (2026-08-09). The symbol filter in the refresh comes from 01e48a6f (2026-09-08): "Constraint zero bound every indexed area, including areas of pure prose ... k0 now binds only to areas with symbol grains". The predicate kept every area, and the dry1 read names that gap as the cause (reasoned, not replayed). 01e48a6f answers a wall of a cold walk on tipsC, 2026-09-04, and names no frame. Origin class: a fix that answered another wall, the prose-only walk of 2026-09-04, frame not found.
9. After the end: dry4-W1, "one `reconcile` key quarantines on the prose files", is another onboarding key at the start of a run (extract c, dry4, item 4). Frame 354's first condition aimed at the reconcile step. It is another tick at the same phase. Not sure.

Row: Ended | conditions changed | 2 | frame closes count | prose walk fix | origin frame: none

### Chain 27: dry6c-W2, 4 turns, firm

Reader: the lead.

1. The wall: "the Developer got his correction without its middle sentence [C?] (wall 2; root read W1)" (`plans/method/turns-list-2026-11-10.md`:349). First turn dry run 6c, last turn dry run 9, 4 turns: dry6c-W2 (`plans/dry6c-read-2026-11-06.md`:90), dry7-W1 (`plans/dry7-read-2026-11-07.md`:157), dry8-W9 (`plans/dry8-read-2026-11-08.md`:73), dry9-W3 (`plans/dry9-read-2026-11-10.md`:51). Two signs. Part A: his words on a running batch do not reach the Developer: the middle sentence of m27 (6c) and "Do not remove that branch in _foldline" (7). The root read joins these two as W1 (`plans/walls-root-read-2026-11-08.md`:15). Part B: a removal that no answer of his allowed lands, and a restore is needed: dry run 7's removal of the issue 1501 branch, dry run 8's W9 "the removal: closed in result, with residue", dry run 9's D9-3 "The imports came out twice, and a seat put them back each time". Dry run 7's W1 holds both signs. Split: part A dry runs 6c and 7, 2 turns; part B dry runs 7, 8 and 9, 3 turns.
2. The state at the end: Part B: Open, dry run 9 names it. Part A: Ended by the split. Dry run 8: "Its two walls of dry run 7, the criteria stamp and the removal push, are closed by the counts 1 and 2" (`plans/dry8-read-2026-11-08.md`:120). Blind run 1 runs on another repository and names no wall of dry run 7 (`plans/method/turns-list-2026-11-10.md`, dry7 cell 8). Dry run 9's D9-3 says his m44 "landed as `approve` with act `add` on `folds_long_lines`, not as a keep", and "s199 had those words in its first prompt". That is part B's sign. So dry runs 8, blind 1 and 9 do not name part A.
3. The conditions at the end: Part B: not applicable, no run follows dry run 9. Part A: conditions changed. Blind run 1, the second run after dry run 7, uses another repository and another request (`plans/method/turns-list-2026-11-10.md`, blind1 cell 8).
4. The changes, in order:
   - Part A. Frame 362, the record of his reply: dd396248, 901659b0, c5851e5b (2026-11-06 07:43), 6a354d42, f4111d0c, 659cac8b and 9a70e256 (09:09), "keep every clause add of his reply or refuse by name" (`git log`; `plans/stack.md`:1981-1986). Place: the Liaison's ruling door, `menu_ruling`. Kind: a door or a refusal. On dry run 7's commit dbd8d920.
   - Part A. Frame 362, the push: 35826d80, b9f269aa, dbcbdf2e and 8e2b8560, 2026-11-06 09:41, "push his whole reply once with the page lines it names" (`git log`; `plans/stack.md`:1984, 1987). Place: `rota/core/runner.py`, the Developer's wake. Kind: other code of rota, the prompt that a seat reads. On dry run 7's commit. Dry run 7: wall 1, "his two answers reached no push" (`plans/dry7-read-2026-11-07.md`:157).
   - Part A and B. 3e53c57a, 2026-11-08 09:37, "fix(runner): his words on the batch reach every Developer wake and the stray judgement", the push half of frame 173 (`git log`; `plans/walls-root-read-2026-11-08.md`:15, "The push half is built today, 3e53c57a"). Kind: other code of rota. On dry run 8's commit. Dry run 8: "the removal push ... closed by the counts 1 and 2", and W9 "closed in result, with residue".
   - Part B. Frame 173, the restore by the structure: 6eb4c225 "feat(core): the structure puts a removed statement back with no model", 4de501b7 "feat(roles): his keep on a removal line restores the statement by the structure", d974f836, 0a7264f1, ecbef55e and ba99c5f6, 2026-11-10 03:02, and e0ef6037, 3076a479 and 7af82636 at 05:11 (`git log`). Files: `rota/core/restore.py`, `rota/roles/api.py`, the prompts. Kind: other code of rota, a door, a prompt. On dry run 9's commit d856c51d. Dry run 9: "The imports came out twice ... A whole-file replace leaves none", meaning no anchor (`plans/dry9-read-2026-11-10.md`:51-54).
   Count: 4.
5. The last change before the end: Part A: 3e53c57a. Evidence: a read confirms with a count: "closed by the counts 1 and 2" (`plans/dry8-read-2026-11-08.md`:120). Part B: not applicable, open.
6. The place of the changes: Part A: the record changes touch `menu_ruling`, where the dry 6c read finds the loss, "`menu_ruling` keeps one shape per ref, so each add overwrote the one before it" (`plans/stack.md`:1970). The push changes touch the Developer's wake in `rota/core/runner.py`, where the sign shows. Part B: the sign shows at the commit that removes statements and at the restore. Frame 173's build touches `rota/core/restore.py`, the place of the restore. The removal commit door (`rota/roles/api.py`, F7's check) is not changed.
7. Who started each change: Part A: the read of dry run 6c, wall 2, and its wall 2 read (`plans/stack.md`:1969-1970). 3e53c57a: the root read and rule C77, "ruled: Roman, 2026-11-08". Part B: frame 173 from the plan of dry run 8 (`plans/method/turns-list-2026-11-10.md`, dry8 cell 6, "Built after blind run 1 and before dry run 9: ... 173 (03:02)"). Roman's message before that plan: "ok i need to do a meta review of how the project is going over the last two weeks" (2026-11-09 23:39) is listed with the turn, and no message of his names the restore.
8. The origin: Part A: "Provenance: frame 345's clause split and clause add of 2026-10-29, with no test of two adds; frame 322's change of 2026-10-27 made the push read row words where frame 312 read the whole reply" (`plans/stack.md`:1970). `menu_ruling`'s one shape per ref is e810eb77, 2026-10-29, "feat(liaison): rule a page by one menu option per clause", frame 345 (`plans/walls-root-read-2026-11-08.md`:15). Frame 345 answered "The Liaison's loss has no test at its scale, so a door or prompt change is measured by a night or not at all" (`plans/archive/stack-2026-10-30.md`:19). Origin class: a frame that answered another wall: frame 345, the Liaison's loss with no test at its scale. Part B: the removal check is 11d04b18f, 2026-10-27, "fix(api): F7, the commit compares the base with the tree for removals" (`plans/walls-root-read-2026-11-08.md`:15, `git show`). F7 is a fact of frame 344's audit, "Closed frames fixed one door of N" (`plans/archive/stack-2026-10-30.md`:164-174). Part b reads F7 as the answer to n171-W4, removals with no grant (`plans/method/chains-read-extract-b-2026-11-10.md`, chain 41, cell 8). Origin class: a frame that answered another wall: frame 344 (F7), wall n171-W4.
9. After the end: Part A: yes, at the same seat and step under another name: dry run 9's D9-3 holds his words "Put back every import you removed" that reached s199 and did not stop the removal. Part B: not applicable.

Row: A Ended, B Open | A conditions changed; B not applicable | 4 | A read counts; B not applicable | A frame 345; B frame 344 (F7) | origin frame: 345, 344

### Chain 28: n166-W2, 8 turns, not sure

Reader: sub-agent, part b (`plans/method/chains-read-extract-b-2026-11-10.md`).

1. The wall: "the naming door ignores the Liaison's own ask [C2] (W-B)" (`plans/method/turns-list-2026-11-10.md:353`; `plans/night166-read.md:210`). First turn night 166, last turn night 175, 8 turns: n166, n168, n170, n171, n172, n173, n174, n175. Rebuilt from column 8 of extract c: n166-W2 to n168-W7 (same cause); n168-W7 to n170-W4 (not sure); n170-W4 to n171-W7 (not sure); n171-W7 to n172-W5 (not sure, "the read says New"); n172-W5 to n173-W16 and n173-W9 (not sure, "New"); n173-W16 to n174-W5 and n175-W5 (same sign at the same place). The walls carry three signs, so this block splits the chain into three parts. The brief asks for two parts. Three parts are the honest split.
   - Part A, the naming door: n166-W2 and n168-W7, "the naming door reads his last answer only [C2]" (`plans/night168-read.md:110`). 2 turns.
   - Part B, a reading door misreads which line his words fault: n170-W4 "a door's text makes the Liaison contest an unfaulted criterion", n171-W7 "the rulings door reads a fault as no fault", n172-W5 "the rulings door lands a contest on a line his words do not name", n173-W9 "the rulings door reads a fault from another page's line number" (extract c, nights 170 to 173, item 4). 4 turns, joined by "not sure" links only. The reads call n172-W5 and n173-W9 "New" (`plans/night173-read.md:181`).
   - Part C, a landed act reverses his words: n173-W16, n174-W5 and n175-W5 (`plans/night173-read.md:73`, `plans/night174-read.md:64`, `plans/night175-read.md:61`). 3 turns, firm.
2. The state at the end:
   - Part A: Ended. Nights 169, 170 and 171 name no naming-door wall by a firm link (extract c, night 168, item 8).
   - Part B: Open by the rule. Night 173 is one of the last three runs of the night series. Night 174 counts the sign of W9 at "0" (extract c, night 173, item 8). Night 175 names no wall of Part B.
   - Part C: Open. Night 175 named it.
3. The conditions at the end:
   - Part A: nights 169 to 171 ran on the same requests, models and repository. Same.
   - Parts B and C: the nights stopped after night 175, and the dry runs are another kind of run. Conditions changed.
4. The changes:
   - Part A, change 1. Frame 337, "the naming door reads his earlier answers": 21f67802 and af60c5b9, landed as 7121f613 and 322da4b9 on 2026-10-26, before night 169 (`plans/f335-338-close-read-2026-10-30.md:14`, `:88`). File: `rota/roles/api.py`, `_unnamed_contest`. Kind: a door. Night 169 names no naming-door wall.
   - Part A, change 2. 7762b169 "read his reply, not the seat's words, at the naming door", 2026-10-28 06:46, branch f2b, in night 173's commit (git merge-base). Kind: a door. After the end.
   - Part A, change 3. f5487759, 2026-10-29 15:22, "retire the word form of a page ruling and its doors", which removes `_unnamed_contest`; then 939536c1 and fb27155b of frame 347 give the menu his earlier answers (`plans/f335-338-close-read-2026-10-30.md:88-89`). Kind: a door removed, and a prompt form. After the end.
   - Part A count: 3.
   - Part B: the changes of chain 7 to the rulings door: F2 with F3 at 135c87d1 (before night 172), f2b (before night 173), w7root at 793aa684 (before night 174), seamroot at dfcffd40 (before night 175), and frame 345's menu after night 175. The seam's commit 69561d5b, "an earlier page's numbers fault no line", aims at n173-W9 (`plans/seam-night173-read.md:11`). It is not in night 174's commit 3ac83acc (git merge-base), so night 174's "0" came before it. Part B count: 5.
   - Part C, change 1. seamroot, merge dfcffd40 at 2026-10-28 14:45, "the rulings seam of nights 173 and 174, W1, W9, W16". The read's proposal for W16: "a `remove` or `drop` on a code target lands only when its span asks for a removal" (`plans/seam-night173-read.md:11`). Commits d28e6e05 "a removal lands only on his named code target", 9b2d34d6 "a removal needs its target". File: `rota/roles/api.py`. Kind: a door. Built before night 175. The next read: n175-W5 "landed rulings reverse him" (`plans/night175-read.md:61`).
   - Part C, change 2. Frame 345's menu, b9337a8c and f5487759 on 2026-10-29, after the last naming. Kind: a door and the measure (24 L3R cases).
   - Part C count: 2.
5. The last change before the end:
   - Part A: frame 337. Evidence: a frame closes on a count. Frame 337 closed on 2026-10-30 17:33: "Naming-door refusals on a line his earlier answer names went from 2 of 2 to 0 on nights 169 to 175, reached once on night 175" (commit 613afc3b).
   - Parts B and C: not applicable. Both are open.
6. The place of the changes:
   - Part A: the sign shows in `_unnamed_contest` in `rota/roles/api.py`, which filled `words` with his last reply (`plans/archive/stack-2026-10-30.md:473`). Changes 1 to 3 touch that function or remove it. They touch the place of the sign.
   - Part B: the sign shows in the fault readers of `rulings_rule` in `rota/roles/api.py`. The changes touch the same file and function (chain 7, cell 6).
   - Part C: the sign shows where an act lands and where `granted` reads it as his permission: "The act check proves only that the span is his words (api.py 13774 to 13786). `granted` then reads the act as his permission" (`plans/seam-night173-read.md:9`). Change 1 touches the act check in `rulings_rule`. Change 2 replaces the word form. Both touch the place of the sign.
7. Who started each change:
   - Part A, change 1: a read of a run, sprint 25 row 5, "W7, W-B of night 166" (`plans/stack.md:548`), and Roman, 2026-10-26 19:30: "are we not fixing all the things in one go before the next night?" (extract c, night 168, item 9).
   - Part A, change 2: a read of a run, sprint 32 row 1 (`plans/stack.md:331-337`).
   - Part A, change 3, and Part C, change 2: Roman, 2026-10-28 14:30: "Sounds like we need less doors and more in depth test cases" (frame 345).
   - Part B: as chain 7, cell 7.
   - Part C, change 1: a read of a run, sprint 33 row 1, "recommended on night 173's read" (`plans/stack.md:286-291`), landed "on Roman's word of 14:45" (`plans/stack.md:244`).
8. The origin:
   - Part A: `_unnamed_contest` comes from 250f3806 (2026-10-14), "the verdict door refuses a contest on a line the principal's words do not name". It is frame 234's pass 2 (`plans/archive/stack-2026-10-15.md:29`; `plans/archive/stack-2026-10-30.md:473`). Its message names night 147's m131, where the Liaison contested lines that his words did not fault. Origin class: a frame that answered another wall: frame 234, the over-contest of night 147's m131.
   - Part B: the fault readers of `rulings_rule`. `_faulted_approve` comes from f0b2924c (2026-10-16), as in chain 7. Origin class: a frame that answered another wall: frame not sure, night 149's wrong approve.
   - Part C: the act check comes from 76f2f981 (2026-10-27 03:09), "an act is checked against his words before it is written". It is in night 170's commit 26a44700 (git merge-base). The seam read says "No build claimed this check" for the verb (`plans/seam-night173-read.md:95`). The frame of 76f2f981 is not found by this pass. Origin class: not found.
9. After the end:
   - Part A: night 170 names n170-W4, a door text that makes the Liaison contest an unfaulted criterion, at the same seat and the same door family. Not sure.
   - Parts B and C: not applicable. Both are open.

Row (Part A): Ended | same | 3 | frame closes count | frame 234 door | origin frame: 234
Row (Part B): Open | conditions changed | 5 | not applicable | fault reader door | origin frame: none
Row (Part C): Open | conditions changed | 2 | not applicable | not found | origin frame: none

### Chain 29: n166-W1, 6 turns, not sure

Reader: sub-agent, part b (`plans/method/chains-read-extract-b-2026-11-10.md`).

1. The wall: "the Tester's three bg_3 tests are red on any code [C5] (W-A)" (`plans/method/turns-list-2026-11-10.md:354`; `plans/night166-read.md:209`). First turn night 166, last turn night 174, 6 turns: n166, n167, n170, n172, n173, n174. Rebuilt from column 8 of extract c: n166-W1 to n167-W7 (not sure); n167-W7 to n170-W1 (not sure); n170-W1 to n172-W15 and n173-W13 (not sure, "the same door, sessions land tests later"); n172-W15 to n173-W13 and n174-W17 (same sign at the same place). The walls carry two signs, so this block splits the chain.
   - Part A, a Tester's test that the code cannot pass: n166-W1, three tests that assert what the right docstring cannot return, and n167-W7, "The Tester's test path replaces the module under test ... 35 of 35 tests error at fa4e8230" (`plans/night167-read.md:100`). Frame 328 holds both (extract c, night 166 item 6; `plans/stack.md:596-600`). 2 turns, joined by a "not sure" link.
   - Part B, the test-file door: n170-W1, "The test-file door refuses every path the Tester sends for the docstring criterion, and the key quarantines", 12 "is already inh_..'s file" refusals (`plans/night170-read.md:57`); n172-W15, n173-W13 and n174-W17, "the test-file door fires; sessions land tests later" (extract c, nights 172 to 174, item 4). 4 turns.
2. The state at the end:
   - Part A: Ended. Nights 168, 169 and 170 name no such wall by a firm link (extract c, night 167, item 8). n170-W1 meets it by a "not sure" link.
   - Part B: Open. Night 174, one of the last three runs of the night series, named it.
3. The conditions at the end:
   - Part A: the model changed. Night 168 ran on Gemma, "frame 323's second Gemma night, on Roman's word of 09:01" (`plans/stack.md:499-500`). Night 169 ran on "qwen3.5:9b in every seat" (`plans/stack.md:557-559`). Conditions changed.
   - Part B: open. The nights stopped after night 175, and the dry runs are another kind of run. Conditions changed.
4. The changes:
   - Part A, change 1. Frame 328, W-A, passes 1 to 3 on the branch, "Validating at a875a798" at 2026-10-26 03:52, before night 167 (extract c, night 166, item 6). a875a798 is dated 2026-10-26 03:05. Kind: a door at the encode and a route of the red to the Tester (frame 328's heading, "a red at encode goes back to the Tester", `plans/stack.md:648-649`). Night 167 names W7, another sign.
   - Part A, change 2. Frame 328, pass 4, sprint 24 row 2: "`tests.encode` refuses a test path that is a file of the code index outside the test folders, and a run that errors at collection goes back to the Tester as a red" (`plans/stack.md:596-600`). Pass 4b at a79474fd (commit d0902a1a, 2026-10-26 08:04). Night 168 "runs cold from the head of rows 2 and 3" (`plans/stack.md:621-624`). Kind: a door. Night 168 names no such wall (absent only).
   - Part A count: 2.
   - Part B, change 1. Frame 343, pass 1 at 685f44dc, "the test-file door offers a filled call to a new file beside a project test file, and tests_missing.md says the touch path with the project's tests is not the Tester's" (commit e904b295, status 2026-10-27 14:10). The branch commit is 6f7ab327, "offer a new file beside a project test file at the encode". Night 171 ran on 9827e38a with it (extract c, night 170, item 6). Kind: a door and a prompt. Night 171 names no such wall. Night 172 names W15: the door fires, and sessions land tests on the next call.
   - Part B, change 2. F35, merge 7021f964 at 2026-10-28 02:44, "one reader of the predicted files less the paths his words decline", and F31, merge e42d13d1 at 2026-10-27 18:56, "one asks_for_docs". The night 170 read places W1 under "F35 ... with F31" (`plans/night170-read.md:57`). Kind: other code of rota. Built before night 172. Night 172 and night 173 name the door again.
   - Part B count: 2.
5. The last change before the end:
   - Part A: frame 328's pass 4. Evidence: absent only. Frame 328 closed on 2026-10-31 01:58 with "328's count was ruled taken by a case or not at all" (commit 3c82ffa2), not on a night count.
   - Part B: not applicable. Part B is open. Frame 343 "closes at 0 of 3 on three nights with the door firing 12 times" (`plans/stack.md:279-280`).
6. The place of the changes:
   - Part A: the sign shows in `tests.encode` in `rota/roles/api.py`, which "checks only that the path ends in `.py`" (`plans/night167-read.md:100`), and in the route of a red run. Both changes of frame 328 touch `tests.encode` and the route. They touch the place of the sign.
   - Part B: the sign shows in the test-file clash refusal in `rota/roles/api.py` about lines 13447 to 13500 ("is {clash['id']}'s file", grep). Frame 343 touches that door and the brief `tests_missing.md`, the place of the sign. F35 and F31 touch the readers of the predicted files and of a docs criterion, another place.
7. Who started each change:
   - Part A, change 1: a read of a run, sprint 23 row 1 on night 166's read (`plans/stack.md:648-650`).
   - Part A, change 2: a read of a run, sprint 24 row 2 on night 167's read (`plans/stack.md:596`).
   - Part B, change 1: a read of a run, night 170's read, which pushed frame 343 in its own commit (extract c, night 170, item 5).
   - Part B, change 2: frame 344's audit, on Roman's message of 2026-10-27 14:08, "Go back and review them".
8. The origin:
   - Part A: frame 328's provenance read: "The encode door ran s198's tests on the head and let the red assertions through on purpose, frame 304's rule a3ce3f01 of 2026-10-23" (commit 3c82ffa2, frame 328 status of 2026-10-25 23:00). This pass did not read which wall frame 304 answered. Origin class: a frame that answered another wall: frame 304, wall not found.
   - Part B: the text "two tests in one file" of the clash refusal comes from e8c68bec (2026-09-02, "fix(sandbox): walk twelve -- the dispute reaches the seat, two more harness facts"). The night 170 read gives the cause: "The brief tells the Tester to use a path under `touch`, and every touch test path is a project test's file" (`plans/night170-read.md:57`). Origin class: a fix that answered another wall, a walk of 2026-09-02, frame not found.
9. After the end:
   - Part A: night 170 names n170-W1, the test-file door on the same seat and step, the Tester's encode. Not sure.
   - Part B: not applicable. Part B is open.

Row (Part A): Ended | conditions changed | 2 | absent only | frame 304 rule | origin frame: 304
Row (Part B): Open | conditions changed | 2 | not applicable | walk twelve fix | origin frame: none

### Chain 30: n155-W8, 5 turns, not sure

Reader: the lead.

1. The wall: "cycle 1, the Critic's `lines` dict with a quote [C?] (8)" (`plans/method/turns-list-2026-11-10.md`:355). The list gives no walls. From column 8 of extract b: n155-W8 meets n158-W3. n157-W3 meets n158-W3 and n160-W1 as "not sure". n158-W3 meets n160-W1 as "not sure". n160-W1 meets n161-W3 as "not sure" (`plans/method/turns-list-extract-b-2026-11-10.md`:138, 187, 212, 258). So the walls are n155-W8, n157-W3, n158-W3, n160-W1 and n161-W3, 5 turns: nights 155, 157, 158, 160 and 161. They hold two signs at the Critic's `verdicts.emit` step. Part A: a diff line inside a single-quoted value closes the string early, and the lines door names the phantom key "', ' is not a criterion of batch bg_1": n155-W8 (`plans/night155-read.md`:130), n158-W3 cycle 1 (`plans/night158-read.md`:204, "The same wall as night 155's s138 to s140"), and n160-W1 (a) (`plans/night160-read.md`:271). Nights 155, 158 and 160, 3 turns. Part B: frame 201's block refusal and hold on a Critic's pass: n157-W3, "three Critic passes cite a docstring" (`plans/night157-read.md`:197), n160-W1 (b), "The door refused 30 docstring lines in 15 sessions", and n161-W3, "The hold turned two right passes into wrong fails" (`plans/night161-read.md`:284). Nights 157, 160 and 161, 3 turns. Split.
2. The state at the end: Ended, both parts. Part A: the last naming is night 160. The reads of nights 161 to 163 hold no "is not a criterion of batch" and no `separators=(` (grep: 0 hits on the three pages). Part B: the last naming is night 161. Night 162: "0 right passes turned to fails from 2" (`plans/stack.md`:819-820). Night 163: "Night 2. Not seen" (`plans/stack.md`, frame 201, status 2026-10-24 18:19). Night 164a has no read page.
3. The conditions at the end: conditions changed, both parts. Part A: nights 161 and 162 hold the R1 requests, and night 163, the third run after, holds R2. Part B: the requests changed at night 163, the second run after the last naming.
4. The changes, in order:
   - Part A: none found. Frame 266 records the sign on nights 155 and 158 and builds no pass for it: "night 155, walk 1, `CYCLE` 1 ... whose own quotes closed the string early" and "night 158 ... the parser read `', '` as a dict" (`plans/stack.md`, frame 266, status 2026-10-18 01:07 and 2026-10-21 14:33). Night 158's read places it as "Not frame 266's parser: a case on frame 266 by cause, 1 cycle". Count for part A: 0, by absence.
   - Part B. Frame 201, pass 1, e374ecb8, 2026-10-21 12:05: "the block refusal names the kind of the matching parts when every one has no behaviour" (frame 201, status 12:05). Place: `rota/roles/api.py`, the lines check of `verdicts.emit`. Kind: a door or a refusal. On night 158's commit. Night 158: "untested: the block refusal fired 0 times" (status 2026-10-21 16:23).
   - Part B. Frame 201, pass 2 and 2b, 3a149081 and d7923e83, 2026-10-21 16:29, the diff with function context (frame 201, status 16:29). Places: `worktrees.diff` and `_batch_diff`. Kind: other code of rota. On night 159's commit.
   - Part B. Frame 201, passes 3 to 3d, the hold on a Critic's first pass, to 98ccbffd and 8b1566c8 "fix(api): the hold asks for the call in the same reply", 2026-10-23 14:43 (`git log`; frame 201, status lines of 13:46 to 15:17). Place: `verdicts.emit` in `rota/roles/api.py`, `PassHeld`. Kind: a door or a refusal. On night 159's commit (`git merge-base`). Night 159: "The hold fired 2 times, both in s128, both on a right pass of bg_1" (`plans/night159-read.md`:134-136). Night 160: "Not met ... In 19 of 20 review sessions the lines door refused the pass before the hold could run" (status 2026-10-24 01:11). Night 161: "5 fires on 5 passes with lines, 0 wrong passes caught, 2 right passes turned into wrong fails" (status 2026-10-24 05:58).
   - Part B. Frame 201, the pass of 2026-10-24: b8ad3f48 "fix(api): the first-pass hold keeps its question and offers no fail" and 6f95e1f0 "fix(api): the hold asks the seat to name the criterion in its fail" (`git log`; status 2026-10-24 06:26 to 06:34). Kind: a door or a refusal. On night 162's commit. Night 162: "0 right passes turned to fails from 2".
   Count: 4 (part A 0, part B 4).
5. The last change before the end: Part A: none. Evidence: absent only. Part B: b8ad3f48 and 6f95e1f0. Evidence: a read confirms with a count: night 162, "0 right passes turned to fails from 2", and night 163, "Not seen". No closing line of frame 201 was found in `plans/stack.md`.
6. The place of the changes: Part B: every change but pass 2 touches `verdicts.emit` and its lines check in `rota/roles/api.py`, where the sign shows. Pass 2 touches the diff builder, another place. Part A: the sign shows at the lines door in `rota/roles/api.py` ("`api.py` 11559", `plans/night158-read.md`:204) and in the call parser `rota/llm/toolproto.py`. No change touched either place.
7. Who started each change: Part B: pass 1 is "taken as sprint 14's row 1", from night 157's W3 (frame 201, status 2026-10-21 11:45). Passes 2 and 3 come from the frame's own review findings and its interview (status lines of 2026-10-21 15:57 and 2026-10-23 12:47). The pass of 2026-10-24 comes from the read of night 161, W3 (status 2026-10-24 05:58). No message of Roman found.
8. The origin: Part A: the refusal "is not a criterion of batch" comes from 1663c2bb, 2026-10-07, "feat(desks): a pass names an added line per criterion" (`git log -S`). Frame 201's provenance says "Roman ruled the lines check on 2026-10-07 08:57, a line per criterion" (frame 201, status 2026-10-21 11:50). The check is "frame 170's lines check" (frame 201's title). Frame 170 answered "A merge's review leaves no trace a person can read: every Critic pass since night 118 carries no reason" (`plans/archive/stack-2026-10-08.md`:5). Origin class: a frame that answered another wall: frame 170, Critic passes with no reason. Part B: n157-W3's block refusal "came from the review of 845e0b80 at c038ea3e, 2026-10-07 10:37", in frame 170 again (status 2026-10-21 11:50). n161-W3's hold is frame 201's own pass 3 of 2026-10-23, which answered n157-W3 and the judgement half of frame 201. Origin class: a frame that answered another wall: frame 170, and frame 201 for the hold.
9. After the end: not sure. Night 163's W1 names "The note door refuses the rewrite the item asks for" at the Developer, another seat (`plans/night163-read.md`:179). The reads of nights 161 to 163 name no Critic wall at the lines door, by the grep of cell 2.

Row: Ended | conditions changed | 4 | A absent only; B read counts | frame 170 | origin frame: 170

### Chain 31: dry5-W10, 5 turns, not sure

Reader: the lead.

1. The wall: "the write doubles every backslash of `string.py` [C?] (10)" (`plans/method/turns-list-2026-11-10.md`:356). The list gives no walls. The lead's chain script holds dry5-W10, dry6c-W5, dry7-W10, dry8-W13 and dry9-W12, with the links dry5-W10 to dry6c-W5 "not sure", dry6c-W5 to dry7-W10 firm, dry7-W10 to dry8-W13 "not sure", and dry8-W13 to dry9-W12 firm (`chains.json` in the lead's scratchpad). The first link does not hold. Extract c reads "dry5-W10: not met (dry6c-W5 says "Dry run 5: no")" (`plans/method/turns-list-extract-c-2026-11-10.md`:550), and the dry 6c read says of its wall 5 "Dry run 5: no" (`plans/dry6c-read-2026-11-06.md`:93). The script took the id from a "not met" cell. So the block splits. Part A: dry5-W10 alone, the Developer s207 wrote `string.py` with every backslash doubled (`plans/dry5-read-2026-11-04.md`:59), 1 turn. Part B: door refusals at the test step spend the turns until a key quarantines: dry6c-W5, "The Tester cannot write a test with backslashes" (`plans/dry6c-read-2026-11-06.md`:93), dry7-W10, "The Tester's encodes were refused more than three times on one door" (`plans/dry7-read-2026-11-07.md`:166), dry8-W13, "Door refusals spent the Developer's turns", provenance "root read W4, door text" (`plans/dry8-read-2026-11-08.md`:92-93), and dry9-W12, "Door refusals spent the turns. Repeats W13" (`plans/dry9-read-2026-11-10.md`:89). The root read joins 6c-5 and 7-10 as W4 (`plans/walls-root-read-2026-11-08.md`:18). Dry run 8 calls its W13 "dry run 7 wall 10 in kind". Part B holds 4 turns, dry runs 6c, 7, 8 and 9, and its seat moves from the Tester to every seat.
2. The state at the end: Part A: Ended. Dry runs 6, 6b and 6c do not name a doubled write by the Developer. Part B: Open, dry run 9 names it.
3. The conditions at the end: Part A: the machine changed. Dry run 6 measured the machine, dry run 6b ran behind a router, and dry run 6c ran on the 3080 alone with `ROTA_ONESHOT=1` (`plans/method/turns-list-2026-11-10.md`:305, 386). Dry run 6c continues 6b at turn 5 and does not start from zero. The records I read show no change of the request or the repository. Conditions changed, by the kind of run. Part B: not applicable, no run follows dry run 9.
4. The changes, in order:
   - Part A. Frame 362, pass 4i: defd4bbf "fix(doors): refuse a write one escape level deeper than the file", 9752cb62 and 7bdf1d01, 2026-11-04 15:02 (`git log`; `plans/stack.md`, status 2026-11-04 15:03). Place: the write door and `_escape_note` in `rota/roles/api.py`. Kind: a door or a refusal. On dry run 6's commit and after (`git merge-base`). Dry run 6c's read: "Dry run 5: no" for its backslash wall, which is the Tester's.
   - Part B. Frame 362, the parser fix of dry run 6c's wall 5: 566b945d, 2026-11-06 07:44, "fix(toolproto): frame 362, parse_args reads a list as it is written before the rewrites" (`git log`). Place: `rota/llm/toolproto.py`. Kind: other code of rota. On dry run 7's commit (`git merge-base`).
   - Part B. Frame 362, the test doors: b90dbf1e "the test doors read the code and say the true thing", 516d878a, 14a69c79, 9eb1855f and e742213f, 2026-11-06 10:20 (`git log`), from `plans/dry6c-tests-refused-read-2026-11-06.md` (`plans/stack.md`:1980, 1985). Place: the prints, collect and import doors of `tests.encode` in `rota/roles/`. Kind: a door or a refusal. On dry run 7's commit. Dry run 7: wall 10, "the surface door refused 9 encodes ... "this test imports src" refused 4 encodes".
   - After dry run 7, frames 155, 166 and 260 moved to the front by C77 and were not built: "All three pushed, never built" (`plans/walls-root-read-2026-11-08.md`:18). After dry run 8, frames 155 and 166 stay "not built" (`plans/dry8-read-2026-11-08.md`:131; `plans/dry9-read-2026-11-10.md`:111-112). The changes of frame 360 on the encode door of 2026-11-08, 4b138f84 and d3c8d008, refuse other shapes (`git log`). They are not counted here.
   Count: 3 (part A 1, part B 2).
5. The last change before the end: Part A: defd4bbf, 9752cb62 and 7bdf1d01. Evidence: absent only. No later read counts doubled writes. Part B: not applicable, open.
6. The place of the changes: Part A: pass 4i touches the write door, where the doubled write landed. Part B: the parser fix touches `toolproto.py`, and the dry 6c wall 5 read says "no single step loses the backslash" (`plans/stack.md`:1971). The test-door changes touch the encode doors where the refusals show. The doors of dry runs 8 and 9, the challenge door's quote rule, are not touched: "The challenge door's quote rule matches no frame by heading" (`plans/dry8-read-2026-11-08.md`:93).
7. Who started each change: Part A: the provenance read of dry run 5's walls 10 and 11, `plans/f362-dry5-walls-read.md` (`plans/stack.md`:1925). Part B: the read of dry run 6c's wall 5 and the read of the refused tests (`plans/stack.md`:1971, 1980). No message of Roman found for these changes.
8. The origin: Part A: the provenance read names "the rewrite refusal offered the whole file first and not the span the seat had read, no write check compares written text to read text, and _escape_note tells the seat to write the doubled form" (`plans/stack.md`:1925). The note's origin commit was not traced. Origin class: not found. Part B: the root read names "Parser 5f445aab, 2026-08-24. Quoter 27bd2edb, 2026-09-02. "No escaping" 6333441b, 2026-09-12, and 28b2a060, frame 122. Surface door d2091d8c, 2026-09-09" (`plans/walls-root-read-2026-11-08.md`:18). Origin class: rota's first design for the parser, the quoter and the surface door, and frame 122 for the "no escaping" text. Frame 122's wall was not read here.
9. After the end: Part A: yes, near the same place under another name: dry run 6c's wall 5, the Tester's backslashes at the encode step. Part B: not applicable.

Row: A Ended, B Open | A conditions changed; B not applicable | 3 | A absent only; B not applicable | A not found; B first design and frame 122 | origin frame: 122

### Chain 32: n105-W2, 4 turns, not sure

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "tests call CliRunner.invoke on plain function, KeyError prog_name [C?] (F109)" (`plans/method/turns-list-2026-11-10.md`:357). First turn n105, last turn n108, 4 turns. The walls, rebuilt from column 8: n105-W2 "met in n106 as n106-W1: same sign at the same place" (extract a:301). n106-W1 "challenged test rewritten into same fault, unchallenged never changes [C4] (guide: frame 110)" has "n107: not sure (n107-W1, frame 110's label). n108: not sure (n108-W3, a `_fixed` copy)" (extract a:316, 323). n107-W1: "crash label "failed before any assertion" fires on a chained exception [C9] (F110)" (extract a:339). n108-W3: "Tester answers with a new `_fixed` test, challenged test stays red [C?]" (extract a:372). The chain is not one wall, and I split it.
   - Part A, n105-W2 and n106-W1: the stored tests pass the plain function `echo_json` to `CliRunner.invoke`, and the Tester's answer keeps the fault. Night 106: "`inh_echo_json_02` "still invokes the plain function"" (extract a:301). Frame 110: "the three `echo_json` tests failed because they invoke a plain function through `CliRunner`" (`plans/archive/stack-2026-10-02.md`:146).
   - Part B, n107-W1 and n108-W3: two signs at the Tester's challenge answer after frame 110. n107-W1 is a wrong label of frame 110's pass 4: "s151's test was labelled `failed before any assertion` and the label is wrong" (frame 110 status 2026-10-02 18:04). n108-W3 is a new `_fixed` copy beside a red test. These two are also not the same sign.
2. The state at the end:
   - Part A: Ended, with the sign carried into chain 5. Nights 107 and 108 are "not sure" for n106-W1 (extract a:323). Night 109 names the same test shape under another cause: n109-W2, "Developers make a helper a Click command to satisfy a `CliRunner.invoke` test" (`plans/night109-read.md`:73; extract a:402). The sign comes back as chain 5's wall on nights 119 to 127 and ends at night 128 (chain 5, cell 2). Frame 131's read says the Tester's test "was written once and replayed" on nights 119 to 126 (`plans/archive/stack-2026-10-07.md`:143).
   - Part B: Ended. n107-W1: "n108: not sure ... Not named in n109, n110" (extract a:352). n108-W3: "not met in n109 ("The `_fixed` copy shape of night 108 did not recur", night109-read.md:68). Not met in n110, n111" (extract a:383). Night 110 ran 0 sessions (extract a:355), so its silence shows nothing.
3. The conditions at the end: Part A, same, see chain 5. Part B, conditions changed for night 110 only: a seam run from night 109's end that ran "0 new sessions" (`plans/archive/stack-2026-10-03.md`, frame 111 status 2026-10-03 03:04). Nights 109 and 111 ran the same repository and requests.
4. The changes:
   - Part A: frame 109, passes 1 and 2, 3b92f9e and bf74640, 2026-10-02, the parser's `_rescan_args` retry and the Developer's challenge briefs (`plans/archive/stack-2026-10-02.md`, frame 109 status 09:46, 10:28). Kind: a prompt of a seat and other code of rota. It aims at the challenge that never parsed, and the frame's heading also names "a test that calls a function as a command" (`plans/archive/stack-2026-10-02.md`:89). Night 106: "every Developer challenge parsed, nine landed" (frame 109 status 13:47). Frame 110, passes 1 to 4, ab70f47, dc62d48, db3078f, e7cd1b3, and pass 5 5729e07 "reverted by me at 8925d78", 2026-10-02: `code.source` in the Tester's challenge tools, the whole stored output on a Tester challenge wake, and a plain-text block of each failed test (frame 110 status 14:42 to 15:41). Kind: a prompt of a seat and other code of rota. Night 107: "no challenge named a test that crashed before its assertion", and "s137 re-encoded `tst_echo_json_compact_6` to v3 and it went green" (frame 110 status 18:04). Count: 2. Frame 131 later, see chain 5.
   - Part B: 4eb5a9a, 2026-10-02 18:05, "`_failed_before_assertion` cuts the output at the last chain marker and reads the test's own section" (frame 110 status 18:05). Kind: other code of rota, the runner's label. It aims at n107-W1. No change aimed at n108-W3 is found. Count: 1.
5. The last change before the end: Part A, see chain 5's frame 131. Evidence: a frame closes on a count (chain 5, cell 5). Part B, 4eb5a9a for n107-W1. Evidence: absent only. Night 108's read "counts the label, verdict not extracted" (extract a:352). For n108-W3 no change is found, and the evidence is the count "did not recur" of `plans/night109-read.md`:68.
6. The place of the changes: Part A's sign shows in the stored test bodies, through `tests.encode` in `rota/roles/api.py`, and in the Tester's answer. Frame 109 touches the parser `extract` and the Developer's briefs, another place. Frame 110 touches the Tester's challenge brief and tools and `_resolve_refs`, another place (frame 110 status 14:42). Part B's n107-W1 shows in the runner's label `_failed_before_assertion`, and 4eb5a9a touches the same function.
7. Who started each change: frame 109 came from a read of a run, "found by night 105's read", and Roman's order "this frame before frame 108" (ruled: Roman, 2026-10-02 09:26) (`plans/archive/stack-2026-10-02.md`:90, 94). Frame 110 came from night 106's read and Roman's order "110, 111, 112, then 108, 113, 114" (frame 110 status 14:30), and he ruled "interview the model in its context" (status 15:02). 4eb5a9a came from night 107's read (frame 110 status 18:04).
8. The origin: Part A: the stored tests are the Tester's. The trigger is the prints door of `tests_encode`, as chain 5's cell 8 records: 8234b716 of 2026-09-13 and 6b52a09d of 2026-09-15. Origin class: a frame that answered another wall: frame not found, wall: night 28's return-value assumption. Part B: n107-W1's label came in frame 110's pass 4, e7cd1b3, "under a generic failed-before-any-assertion rule" (frame 110 status 15:11). Origin class: a frame that answered another wall: frame 110, wall n106-W1. n108-W3: not found.
9. After the end: Part A, yes: n109-W2 names the same test shape with the Developer's side (cell 2). Part B, not sure. Night 109's read says the `_fixed` copy "did not recur" (`plans/night109-read.md`:68), and the extract names no other wall at the label.

Row: Part A: Ended | same | 2 | frame closes count | night 28 door | origin frame: none
Row: Part B: Ended | conditions changed | 1 | absent only | frame 110 label | origin frame: 110

### Chain 33: n119-W1, 4 turns, not sure

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "swallow refusal names the first argument, quote in a later one [C7] (guide: frame 122) (7.1)" (`plans/method/turns-list-2026-11-10.md`:358). First turn n119, last turn n126, 4 turns: n119, n120, n123, n126. The walls, rebuilt from column 8: n119-W1 "n120: not sure (n120-W4, frame 137)" (extract a:642); n120-W4 "never-ends refusal names a word that is no parameter [C7] (guide: frame 137)", "n123: not sure (n123-W3)" (extract a:666, 675); n123-W3 "parser refuses a challenge with no argument named and no step [C?]", "Met in n126 as n126-W18: same sign (`invalid syntax (<unknown>, line 1)`)" (extract a:734); n126-W18 "frame 137, parser refusals name a wrong thing [C7] (guide: frame 137)" (extract a:835). All four are refusals of the call parser in `rota/llm/toolproto.py` whose text names a wrong argument or none. Frame 137 calls itself "The residue of frame 122" and holds the night 120 and night 123 shapes (`plans/stack.md`:3631, 3638). I keep one block on that record. The links n119 to n120 and n120 to n123 are the reader's "not sure".
2. The state at the end: Ended. The last naming is n126. Nights 127 and 128 list only new walls, so they are "not named". Night 129 is thin and has no read. So three runs after the last naming do not name it, and none of the three could show its absence. The reads of nights 130 and 131 hold no "frame 137" (grep, absence only).
3. The conditions at the end: same. Nights 127 to 131 ran on the same repository, requests and kind of run.
4. The changes:
   - Frame 122, passes 4 to 6: 9fa6f2c, 50a156e and 94a6610, 2026-10-05, the swallow refusal names `why` and shows a form that parses, a name only if the function holds it, and the extra-quote sentence (`plans/archive/stack-2026-10-05.md`, frame 122 status 02:02, 02:26, 02:46). File: `rota/llm/toolproto.py`. Kind: a refusal. Passes 1 to 3, fb1bdba, 78ed236 and 1e87855, came before night 119 (frame 122 status 2026-10-04 17:39 to 18:35). Night 120: "closed on night 120", "0 of 249 sessions end after three refusals" (frame 122 status 2026-10-05 04:53). The same night shows n120-W4, "18 refusals in 5 sessions" that name a word the call lacks (`plans/stack.md`:3632).
   - Frame 137's instrument: fed7c580, 2026-10-05 16:26, "test(instruments): the fact check reads spans and lines exactly, and the parser fuzz runs in the gate" (git log --grep "frame 137"). Kind: the harness or the measure. Night 123 adds a shape: "`could not parse arguments: invalid syntax (<unknown>, line 1)`" (`plans/stack.md`:3638). Frame 137's own fix was never built. Its "Waits on" says "Roman's order. Low" (`plans/stack.md`:3634).
   Count: 2.
5. The last change before the end: fed7c580, a measure. Evidence: absent only. Nights 127 and 128 list only new walls and night 129 is thin, so no read counts the sign after night 126.
6. The place of the changes: the sign shows in the refusals of `extract` in `rota/llm/toolproto.py` (`plans/stack.md`:3631). Frame 122's passes touch the same function. fed7c580 touches the tests and the gate, another place.
7. Who started each change: frame 122 came from a read of a run, night 115, "pushed by 5e8ace65", and claimed "next on Roman's order of 12:50" (frame 122 status 2026-10-04 08:30, 16:58). Passes 4 to 6 came from the two blind reads of night 119 and "this session's ruling between two blind reads" (frame 122 status 2026-10-05 01:25). Frame 137 came from night 120's read, "pushed by e6218d79" (`plans/stack.md`:3636).
8. The origin: the parser and the `TOOL:` protocol came in 231afe4c, 2026-08-09 (git log -S "unterminated argument list"). The swallow refusal came in 6333441b, 2026-09-12, "fix(parser): a quote that swallows the next argument is named, and source goes unquoted", after "L1-DV-apply-the-answer on llama, 2026-09-12" (git show). Origin class: a frame that answered another wall: frame not found, wall: the L1 case on llama of 2026-09-12.
9. After the end: yes, outside the three reads and under the same family. Night 137: s320, "4 parse refusals, ended", "Frame 137's family" (`plans/night137-read.md`:83). Night 138: "s352 is night 137's s320 again: the refusal names a quote inside an argument" (`plans/night138-read.md`:65). Frame 266 later holds the same refusal on night 151, chain 21 of this page.

Row: Ended | same | 2 | absent only | llama L1 swallow | origin frame: none

### Chain 34: n119-W3, 4 turns, not sure

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "Tester answers a challenge in prose, sends no encode [C8] (guide: frame 132) (7.3)" (`plans/method/turns-list-2026-11-10.md`:359). First turn n119, last turn n124, 4 turns: n119, n122, n123, n124. The walls, rebuilt from column 8: n119-W3 "n122: not sure (n122-W2, "Near frame 132")" (extract a:644); n122-W2 "same-refs door ignores a new version of the test [C8] (guide: frame 145)", "n123: not sure (n123-W2). n124: not sure (n124-W1)" (extract a:714, and the n122-W2 item 8); n123-W2 "challenge closes as answered when every encode is refused [C8] (guide: frames 132 and 145)" (extract a:733); n124-W1 "accepting Tester's answer makes the door refuse the challenge as judged [C8] (guide: frames 132 and 145)" (extract a:755). The signs differ on the Tester's side: a prose answer with no encode, a new version, eight refused encodes, an accepting answer. They share one place, the same-refs door `you sent challenge to tester on exactly these refs already`, which reads the challenge as answered (`plans/archive/stack-2026-10-05.md`:158, frame 132's Site line). Frame 132's record joins night 123 to night 119: "night 123 holds this door with a new cause" (frame 132 status 2026-10-05 12:19). I keep one block on that record.
2. The state at the end: Ended. The last naming is n124. Night 125: "not met ... ("False refusals: 0 of 11", night125-read.md:9)" (extract a:766, n124-W1 item 8). Night 126 does not name it, and night 127 lists only new walls (extract a, n124-W1 item 8: "n126, n127: not named"). So three runs after the last naming do not name it, and night 127 lists only new walls.
3. The conditions at the end: same. Nights 125 to 127 ran on the same repository, requests and kind of run. Night 125 ran with the new door, "night 125 is the walk" (commit 4a2884f5).
4. The changes, all frame 132, "A Tester answers a challenge in prose and sends no test, and the door then calls the challenge answered" (`plans/archive/stack-2026-10-05.md`:157), with frame 145 in the same pass, in `rota/core/sandbox.py`, kind: a door:
   - Pass 1: 4968ea7d, 2026-10-05 13:41, `_challenge_repeat_refusal` with `UNANSWERED_CHALLENGES = 2` (frame 132 status 13:43; git show 4968ea7d). Night 124: "Refusals that the predicate should admit: 0 of 3, against 18 of 18 on night 123" (frame 132 status 14:57).
   - Pass 2: b2ed55b, 2026-10-05, the cap `LANDED_CHALLENGES = 3` (frame 132 status 15:17; commit b2ed55b8 "the same-refs door caps a chain of challenges across moves").
   - Pass 4: 96c5202 on the branch `f132p3`, the cap per criterion, landed at a2200a7 (frame 132 status 17:58; commit 4a2884f5). Pass 3, 4de1555, stayed on its branch (status 16:53). Night 125: "refusals of the answered form that the predicate admits, 0 of 11 same-refs refusals, against 125 of 141", and "after a barren Tester session, a second challenge that reaches the Tester, 1 of 2, against 0 of 8" (frame 132 status 19:49).
   Count: 3.
5. The last change before the end: pass 4, landed at a2200a7 before night 125. Evidence: a frame closes on a count. Frame 132 "closed on night 125, with frame 145", on "0 of 11" and "1 of 2" (frame 132 status 2026-10-05 19:49). The frame's Tester-side measure, "Tester challenge sessions that end with no encode after a reply that holds a test body", is not given in that close (absence only).
6. The place of the changes: the sign shows at the same-refs door, `rota/core/sandbox.py:1310-1417` in pass 0's record (frame 132 status 13:09), and at the close of a challenge with no call from the Tester (`plans/archive/stack-2026-10-05.md`:158). The three passes touch the same door, `_challenge_repeat_refusal` in `rota/core/sandbox.py`. No pass touches the Tester's answer mode.
7. Who started each change: a read of a run, "found by night 119's two reads", "pushed by e6218d79" (`plans/archive/stack-2026-10-05.md`:158, frame 132 status 01:25). The claim came from a low question "taken by timeout at 12:39" (frame 132 status 12:40). Passes 2 to 4 came from the reviews' confirmed defects (frame 132 status 13:55, 15:41, 16:53).
8. The origin: the refusal "on exactly these refs already" came in ebc9bafd, 2026-09-02, after "S0 walk eight" (git log -S; see chain 16, cell 8). Origin class: a frame that answered another wall: frame not found, wall: S0 walk eight's nine-round challenge.
9. After the end: yes, at the same door under other names. Night 125: n125-W9, "a door names `msg.challenge_tester`, the bound refuses it [C9] (guide: frame 148)" (extract a:794). Night 126: n126-W4, "same-refs step says end while another challenge lands [C9] (guide: frame 168)" (extract a:821).

Row: Ended | same | 3 | frame closes count | S0 walk eight | origin frame: none

### Chain 35: n147-W3, 4 turns, not sure

Reader: sub-agent, part a (`plans/method/chains-read-extract-a-2026-11-10.md`).

1. The wall: "verdict contests a line the words never name (B) [C?]" (`plans/method/turns-list-2026-11-10.md`:360). First turn n147, last turn n151, 4 turns: n147, n149, n150, n151. The walls, rebuilt from column 8: n147-W3 "149: not sure (n149-W9). 150: not sure (n150-W1)" (extract b:401); n149-W9 "the contest of an agreed line [C8]", "met in n150 as n150-W1 (frame 258 "6 signs, the night's root wall: m25"): same cause. met in n151 as n151-W1" (extract b:441, 446); n150-W1 "m25's "ok ... build it with json" makes a request item [C1]"; n151-W1 "frame 258's "ok" contest (m23) [C8]" (extract b:457, 481). Frame 258's record holds the four as one sign, a contest that lands on a line no sentence names: night 150's m25 "was ruled `how_it_works: contest`, and the Vision Keeper s112 made the item `json_only` from it" (`plans/archive/stack-2026-10-24.md`, frame 258 status 2026-10-16 07:01). Night 147's candidate B is the same cause by its read: "contest of a line the words do not name. That cause is candidate B" (`plans/night147-read.md`:209). I keep one block. The link n147 to n149 is the reader's "not sure".
2. The state at the end: Ended, and the end did not hold. The last naming is n151. Night 152: "0 contests landed on a line no sentence names, on 23 replies". Night 153: "0 contests on a line no sentence names, on 27 replies". Night 154: "0 contests on a line no sentence names, read in part" (frame 258 status 2026-10-16 22:30, 2026-10-17 04:31, 16:40). So three runs after the last naming do not name it, with counts. The sign comes back on night 155: "the spare did not hold on m62, m93 and m179 when the first sentence named another line, 3 of 5 batches" (frame 258 status 2026-10-18 02:54). Night 158: "3 contests landed on a line no sentence names" (status 2026-10-21 16:23), n158-W5 "contests on a line no sentence names, frame 258" (extract b, night 158). Night 160: "1 contest on a line no sentence names" (status 2026-10-24 01:11).
3. The conditions at the end: same. Nights 152 to 154 ran on the same repository and kind of run, with the agent principal on Opus. The requests change at night 163, later.
4. The changes, in `rota/roles/api.py`, kind: a door:
   - Frame 234's pass 2, candidate B: 250f3806, 2026-10-14 19:55, "the verdict door refuses a contest on a line the principal's words do not name, and "Note N" is line N", and 91d8fcc3, 20:42, "an unnumbered sentence spares an unnamed contest of an item line only" (git log --grep "frame 234"; both bodies name frame 234). Night 148 ran at 92c4f126, after both (extract b:409). Night 148 does not name the wall (extract b:401, "149: not sure").
   - Frame 258, pass 1 and 1b: e445aa64 and 8194e3a0, 2026-10-16, `rulings_rule`, "the agreed-contest refusal needs an instruction after the agreement" (frame 258 status 12:16, 13:32). Night 151: "3 contests landed on a line no sentence names, on 2 replies, against 6 on night 150" (status 17:36).
   - Frame 258, pass 2: 59030519, 2026-10-16 19:42, "an agreement alone admits no contest, and a sentence with no line number spares line 1 only when it names the request" (status 19:52, 20:00). Night 152: "0 contests ... on 23 replies" (status 22:30).
   - Frame 258, passes 3, 3b and 3c, after the end: 2284cfab, 06b3988d and c641d108, 2026-10-18, the line-1 spare, the files rule and the keep rule (status 03:56 to 05:22). Night 156: "page replies with a batch line whose line 1 is contested, 0 of 7", "one wrong landing, m125's `revise`" (status 07:22). Night 158: "not met: 3 contests landed" (status 2026-10-21 16:23).
   Later commits that name frame 234 are not read for their aim here: e5ae08a9 and fe4b3c78 of 2026-10-24, from nights 161 and 155, and 7762b169 and 9923a021 of 2026-10-28.
   Count: 4.
5. The last change before the end: frame 258's pass 2, 59030519. Evidence: a read confirms with a count, 0 on 23 replies on night 152 and 0 on 27 on night 153 (frame 258 status 2026-10-16 22:30, 2026-10-17 04:31). Night 154's 0 was "read in part". The sign came back on night 155 (cell 2).
6. The place of the changes: the sign shows in the Liaison's verdict on a page reply through `rulings.rule`, `rulings_rule` in `rota/roles/api.py`, at "`_unnamed_contest`'s spare of item lines" (`plans/archive/stack-2026-10-24.md`:185). Frame 234's pass 2 adds that door and its spare. Frame 258's passes touch `_agreed_contest`, `_unnamed_contest` and `_line_refusal` in the same file (frame 258 status 2026-10-16 19:32). All touch the same place.
7. Who started each change: frame 234's pass 2 came from night 147's read: "close frame 234 and open candidate B as its pass 2" (`plans/night147-read.md`:629). Frame 258 came from a read of a run, "pushed from night 149's read", candidate N6, and a row of a sprint, "sprint 8's row 2" (frame 258 status 2026-10-15 16:24, 2026-10-16 11:01). Pass 2 came from night 151's walls W1 and W2 (status 19:32). Pass 3 came from night 155's read, "the next night's precondition" (status 2026-10-18 02:54).
8. The origin: for the sign of nights 149 to 151, frame 258 names the spare of item lines in `_unnamed_contest` (`plans/archive/stack-2026-10-24.md`:185). `git log -S "_unnamed_contest"` gives 250f3806, frame 234's pass 2, and the spare came in 91d8fcc3, whose body names "night 143". Origin class: a frame that answered another wall: frame 234, wall: night 147's candidate B and night 143's contest. For night 147's sign, before any door, the origin is the Liaison's own line map in `rulings.rule`, and its commit is not found.
9. After the end: in the next three reads, no. The counts are 0 on nights 152 to 154 (cell 2). On the fourth run, night 155, the same sign returns at the same door under the same frame, and night 158 names it as n158-W5 (cell 2).

Row: Ended | same | 4 | read confirms count | frame 234 spare | origin frame: 234

### Chain 36: n160-W5, 4 turns, not sure

Reader: sub-agent, part b (`plans/method/chains-read-extract-b-2026-11-10.md`).

1. The wall: "page after a review with no verdict says the team stopped [C11] (W5)" (`plans/method/turns-list-2026-11-10.md:361`; `plans/night160-read.md:275`). First turn night 160, last turn night 163, 4 turns: n160, n161, n162, n163. Rebuilt from column 8: n160-W5 to n161-W7 (not sure) and to n163-W5 (same cause, "Frame 312") (extract b, night 160, item 8); n161-W7 to n162-W6 (not sure) (extract c, night 161, item 8). The walls carry two signs, so this block splits the chain.
   - Part A, a stop page that hides or misstates the state: n160-W5, "The page after a review with no verdict says the team stopped work, and he parked bg_1 on that belief" (`plans/night160-read.md:275`), and n163-W5, "The stuck after an all-approve, and stop pages that hide the cause ... Frame 312" (`plans/night163-read.md:183`). 2 turns.
   - Part B, a send with no text becomes an invented question: n161-W7, "The Vision Keeper's report with no words became a three-item question" (`plans/night161-read.md:288`), and n162-W6, "A textless propose became an invented question ... Frame 303's seam" (`plans/night162-read.md:333`). 2 turns.
2. The state at the end:
   - Part A: Ended. Nights 164a, 164 and 165 name no such wall (extract c, night 163, item 8, "n163-W5, W6, W8, W9: not met in n164, n165"). Night 164a has no read page of its own. `plans/night164-read.md` names one wall of it, W-F, so night 164a is "not named", not "gone".
   - Part B: Ended. Nights 163, 164a and 164 name no such wall (extract c, night 162, item 8, "n162-W4 to W8: not met in n163, n164; n164a: no read"). Night 164a is thin in the same way.
3. The conditions at the end:
   - Part A: the last naming is night 163, the first night on the trio R2 (`plans/method/turns-list-2026-11-10.md:243`). Nights 164a, 164 and 165 ran on the same requests, models and repository. Same between the last naming and the next three. The requests changed inside the chain, between night 162 (R1) and night 163 (R2).
   - Part B: the last naming is night 162, on R1. The next run, night 163, is the first on R2. Conditions changed.
4. The changes:
   - Part A, change 1. Frame 312, pass 1 and 1b: ced9de67 "the stopped page and the shift page name a quarantined review" and cc013d96 "a stuck tick reaches the principal in plain words", 2026-10-24 01:27 and 01:35 (+0100). File: `rota/roles/principal.py`. Kind: other code of rota, the page. Built before night 161 (extract b, night 160, item 6; both are ancestors of night 162's commit 214d22d0). Night 161 names no such wall. Night 163 names W5 with "Frame 312" as its place.
   - Part A, change 2. Frame 312, row 5's pass and passes 1b and 1c, commits 1694320b, c515e7f7 and 7f29d9e1 of 2026-10-24 21:19 to 21:46 (git log, author time). The close names "an answer lifts the `batch_start` key at `land` ... from 6785f35b" (commit b319696a). Kind: other code of rota. Nights 164 and 165 name no such wall (absent only).
   - Part A count: 2.
   - Part B, change 1. Frame 303's case, sprint 19 row 7, "a textless propose is refused, with s228 to s234 and m110" (`plans/stack.md:856-857`). It landed on night 163's commit 5758cc46 as 6862e93b "a Liaison wake resolves a batch ref to its item, state and verdict" and 970cbd81 "a batch verdict names its commit, and the report brief reads the batch row" (git merge-base). Files: `rota/core/` and the report brief. Kind: other code of rota and a brief of a seat. Night 163 names no such wall. Frame 303's status: "Past its night 3. Not exercised: 0 propose calls" (frame 303, status 2026-10-24 18:19 BST, `plans/stack.md` under heading 303).
   - Part B count: 1.
5. The last change before the end:
   - Part A: frame 312's row 5 pass. Evidence: a frame closes on a count. Frame 312 closed on 2026-10-30 17:44: "Pages after a review with no verdict that say \"stopped work\": 0 of 1 on night 171, m40, after 0 on night 161, from 2 on night 160" (commit b319696a). The count is of the first sign only.
   - Part B: frame 303's case. Evidence: absent only. Frame 303's last count is of propose calls, 0, which is another sign.
6. The place of the changes:
   - Part A: the sign shows in the stopped page text and the shift page in `rota/roles/principal.py` (frame 312's Site, `plans/archive/stack-2026-10-30.md:498`). Both changes touch that file: `_stuck_ticks` and `TICK_WORDS` for the page, and `land` for the lift. They touch the place of the sign.
   - Part B: the sign shows at the Architect's and the Vision Keeper's report edge to the Liaison, refs with no text, and in the Liaison's next page. The change touches the Liaison's wake and the report brief, the place where the empty send is read.
7. Who started each change:
   - Part A: a read of a run, sprint 17 row 4: "pushed from night 160's read, section 2, W5, by sprint 17's row 4" (`plans/archive/stack-2026-10-30.md:503`). Roman ruled the second half on 2026-10-24 01:30: "Yes there needs to be a passing review" (same frame, Waits-on line).
   - Part B: a read of a run, sprint 19 row 7 on night 162's read (`plans/stack.md:856`).
8. The origin:
   - Part A: the text "The team stopped work on this change" comes from 358fed11 (2026-10-09), "every page to the principal numbers the request's own lines first", frame 190's pass 1, the page (`plans/archive/stack-2026-10-10.md:17`). This pass did not read which wall frame 190 answered. Origin class: a frame that answered another wall: frame 190, wall not found.
   - Part B: `msg.report_liaison` exists from 7fcec388 (2026-08-09). Frame 303's case names the cause: "the seam is the Architect's report edge to the Liaison, refs only by the ruling of 2026-08-15" (frame 303, status 2026-10-24 15:42). Origin class: rota's first design.
9. After the end:
   - Part A: night 164 names n164-W1, "a batch with a retired criterion never reaches the Critic", and night 165 names n165-W9, "bg_1 ends with 2 red tests". Neither is a page sign. Not sure.
   - Part B: night 163 names n163-W6, "item 2 dies at its first Liaison session, four refused clarifies", at the Liaison seat. Not sure.

Row (Part A): Ended | same | 2 | frame closes count | frame 190 page | origin frame: 190
Row (Part B): Ended | conditions changed | 1 | absent only | rota's first design | origin frame: none

### Chain 37: n167-W2, 4 turns, not sure

Reader: sub-agent, part b (`plans/method/chains-read-extract-b-2026-11-10.md`).

1. The wall: "a body's backslash loses one escape level in the call [C4] (W2)" (`plans/method/turns-list-2026-11-10.md:362`; `plans/night167-read.md:95`). First turn night 167, last turn night 171, 4 turns: n167, n168, n169, n171. Rebuilt from column 8: n167-W2 to n168-W1 (same cause, "C4, the escape level") and to n169-W4 (not sure); n168-W1 to n169-W4 (same sign at the same place) and to n171-W3 (not sure); n169-W4 to n171-W3 (not sure) (extract c, nights 167 to 169, item 8). The walls carry two signs, so this block splits the chain.
   - Part A, an invalid escape passes rota's parse: n167-W2, n168-W1 "a body's backslash loses an escape level; encode admits the invalid escape" (`plans/night168-read.md:104`), and n169-W4 "A Developer write with an invalid escape passes rota's parse with a warning" (`plans/night169-read.md:65`). The night 169 read names the place as "a second site": `code.write`, not `tests_encode`. 3 turns.
   - Part B, n171-W3, "The escape door's advice produces a test that cannot pass on Windows", s153 told to "Write the path with forward slashes" (`plans/night171-read.md:60`). 1 turn. It is the advice of the door that frame 335 built for Part A (cell 8).
2. The state at the end:
   - Part A: Ended. Nights 170, 171 and 172 name no such wall by a firm link (extract c, night 169, item 8). n171-W3 meets it by a "not sure" link.
   - Part B: Ended. Nights 172, 173 and 174 name no such wall (extract c, night 171, item 8, "n171-W1, W3, W8, W9, W12: not met").
3. The conditions at the end:
   - Part A: the chain starts on models C (nights 167 and 168) and ends on models B (night 169) (`plans/method/turns-list-2026-11-10.md`, the run lines of nights 167 to 169). Nights 170 to 172 ran on trio R2, clickI and models B, the same as night 169. Same.
   - Part B: nights 172 to 174 ran on R2, clickI and models B, the same as night 171. Same.
4. The changes:
   - Part A, change 1. Frame 335, "The encode check lets an invalid escape through as a warning" (`plans/archive/stack-2026-10-30.md:442`): 71642373 "refuse an invalid escape at encode and name its raw form", 9a22a120 "give escape advice that the call keeps, on escapes only", and 0fcbce6d "name a real backslash form and no wrong form in escape advice", 2026-10-26, closed as a mechanism at 0fcbce6d at 19:32 (extract c, night 168, item 6). All are in night 169's commit 322da4b9 (git merge-base). File: `rota/roles/api.py`, `tests_encode`. Kind: a door. The next read names n169-W4 at another site: "**Partly, 335.** Its Site names the parse in `tests_encode`, not in `code.write`" (`plans/night169-read.md:65`).
   - Part A, change 2. F19, merge f8955d32 at 2026-10-27 18:10, "the quote forms from the parser". Kind: other code of rota. In night 172's commit de1203a9. It came after nights 170 and 171, which already did not name the wall.
   - Part A count: 2.
   - Part B, change 1. d6a9efe6 at 2026-10-27 19:38, "give escape advice that keeps the value of the string first", "the W3 advice fix at d6a9efe6 about 54k under frame 344" (`plans/archive/stack-2026-10-30.md:457`). File: `rota/roles/api.py`. Kind: a door text. In night 172's commit de1203a9. Night 172 names no such wall (absent only).
   - Part B count: 1.
5. The last change before the end:
   - Part A: frame 335 at 0fcbce6d, before night 169. Night 169 still names the sign at `code.write`, which no change touched: "The code.write site of night 169's W4 stays outside this frame" (`plans/archive/stack-2026-10-30.md:457`). The close read counts "0 `SyntaxWarning` lines on 170 to 173" (`plans/f335-338-close-read-2026-10-30.md:45`) and "Landed encodes that err at collection on an escape went from 6 of 7 to 0 on nights 170 to 175". Evidence: a frame closes on a count for the encode site. For the `code.write` site the sign is absent with no change at that site, and no record says why.
   - Part B: d6a9efe6. Evidence: absent only.
6. The place of the changes:
   - Part A: the sign shows at the seat's call form (two escape levels), at `tests_encode`, and at `code.write` (`plans/night169-read.md:65`). Change 1 touches `tests_encode` and its advice. It does not touch `code.write` ("No `simplefilter(\"error\"...)` exists outside `tests_encode` and `_form_value` at HEAD", `plans/f335-338-close-read-2026-10-30.md:45`). Change 2 touches the quote forms in `rota/core/sandbox.py`, another place.
   - Part B: the sign shows in the escape advice of the encode door in `rota/roles/api.py`. Change 1 touches that advice. It touches the place of the sign.
7. Who started each change:
   - Part A, change 1: a read of a run, candidate C2 of night 167's read (`plans/night167-read.md:95`), pushed as frame 335 at night 168's close (extract c, night 168, item 6), with Roman's message of 2026-10-26 19:30: "are we not fixing all the things in one go before the next night?".
   - Part A, change 2: frame 344's audit, on Roman's message of 2026-10-27 14:08, "Go back and review them".
   - Part B: frame 344's work on night 171's read, under Roman's message of 2026-10-27 19:40, "I want all the fixes implemented before the next night".
8. The origin:
   - Part A: the night 167 read names cause 4, "the call form needs two escape levels", and cause 8, "a collection error is not a red" (`plans/night167-read.md:95`). The call form comes from 231afe4c (2026-08-09, "the TOOL: protocol"). Origin class: rota's first design.
   - Part B: `git log -S "forward slashes"` gives 9a22a120 (2026-10-26 18:56), "give escape advice that the call keeps, on escapes only", a pass of frame 335. Frame 335 answered n167-W2 and n168-W1, which are Part A. Origin class: a frame that answered another wall: frame 335, walls n167-W2 and n168-W1.
9. After the end:
   - Part A: night 171 names n171-W3, the advice of the escape door, at the same seat and step, the encode of a test body with a backslash. Not sure.
   - Part B: nights 172 to 174 name no escape wall. n173-W14, "the bg_3 Tester sends six broken bodies per turn", sits under F19 (`plans/night173-read.md:186`). Not sure.

Row (Part A): Ended | same | 2 | frame closes count | rota's first design | origin frame: none
Row (Part B): Ended | same | 1 | absent only | frame 335 advice | origin frame: 335

### Chain 38: n169-W1, 4 turns, not sure

Reader: sub-agent, part b (`plans/method/chains-read-extract-b-2026-11-10.md`).

1. The wall: "the removal door reads his permission by one phrase [C11] (W1)" (`plans/method/turns-list-2026-11-10.md:363`; `plans/night169-read.md:62`). First turn night 169, last turn night 174, 4 turns: n169, n171, n172, n174. Rebuilt from column 8: n169-W1 to n171-W4 (not sure, "removals with no grant land, the opposite sign"); n171-W4 to n172-W2 (same sign at the same place) and to n174-W15 (not sure); n172-W2 to n174-W15 (not sure) (extract c, nights 169, 171 and 172, item 8). The walls carry two opposite signs, so this block splits the chain.
   - Part A, the removal door refuses or holds a commit: n169-W1, "each commit that removes line 518 is refused" after his grants, 28 removal refusals (`plans/night169-read.md:62`), and n174-W15, "The commit gate holds a write with an unread removal note", 2 refusals, "Same family as frame 339's door" (`plans/night174-read.md:74`, `:219`). 2 turns.
   - Part B, removals with no grant land: n171-W4, "A Developer deletes code he did not ask to change, and the commit lands" (`plans/night171-read.md:61`), and n172-W2, "the commits remove base code with no grant", "Same outcome as night 171's W4" (`plans/night172-read.md:59`, `:147`). 2 turns.
2. The state at the end:
   - Part A: Open. Night 174, one of the last three runs of the night series, named it.
   - Part B: Ended. Nights 173, 174 and 175 name no such wall by a firm link. Night 173: "Row 2 was not reached, because bg_3 removed no code" (`plans/stack.md:278-279`). n174-W15 meets it by a "not sure" link.
3. The conditions at the end:
   - Part A: open. The nights stopped after night 175, and the dry runs are another kind of run. Conditions changed.
   - Part B: nights 173 to 175 ran on R2, clickI and models B, the same as night 172. Same.
4. The changes:
   - Part A, change 1. Frame 339, "The removal door reads the principal's permission by one fixed phrase" (`plans/archive/stack-2026-10-28.md:22`). Commits include 076ea892 "the removal door records a stray for the Architect instead of refusing the commit" (2026-10-26 22:43), 4e58ad9c, d495db74, 99d88c8e and 5480f6b6 "the permission readers read act and target from the record per ref" (2026-10-27 02:49). The status: "The mechanism is on the branch" at 05:11, in night 170's commit 26a44700 (extract c, night 169, item 6). File: the roles code of the removal door. Kind: a door. Nights 170, 171, 172 and 173 name no such wall.
   - Part A count: 1.
   - Part B, change 1. F7 with W4, frame 344's audit, merge c8c819cd at 2026-10-28 01:01, "land f7root, F7 with W4, the commit compares the base with the tree". Pass 2 at aae59d4b: "night 171's commit names both of s164's removals ... a statement that moves under a new if or loop counts as removed" (`plans/archive/stack-2026-10-28.md:52`). Kind: a door. In night 172's commit de1203a9. The next read: n172-W2, "removals with no grant land, and no door refuses. New beside it: the stray route judged this one a mistake (s262)" (`plans/night172-read.md:147`).
   - Part B, change 2. Sprint 32 row 2, branch f7b: f6b0f41f "show the removed lines in the touch_mistaken wake", e855bd79 "show the judged row and grade the head in the restore wake", 00186009 "keep the mistake notes out of the touch_mistaken cycle key", merged at 27f8b53b and 36d2a667 on 2026-10-28 07:56 and 08:37. Kind: a prompt of a seat and a cycle key. In night 173's commit 36d2a667. The next read: "Row 2 was not reached, because bg_3 removed no code" (`plans/stack.md:278-279`).
   - Part B count: 2.
5. The last change before the end:
   - Part A: not applicable. Part A is open. Frame 339 closed on 2026-10-28 14:18: "Ends-when held on nights 172, 173 and 174: Developer sessions refused at the removal door after an answer that grants the removal, 0 of 1 on each night, one sample per night" (`plans/archive/stack-2026-10-28.md:57`). The same night 174 names W15 at the commit gate.
   - Part B: f7b at 36d2a667. Evidence: absent only. Night 173 says the row "was not reached, because bg_3 removed no code", so the case did not occur. Nights 174 and 175 name no removal with no grant by a firm link.
6. The place of the changes:
   - Part A: the sign shows in the removal door at the commit, its "line N" matcher and the sentence the page offers (`plans/archive/stack-2026-10-28.md:33`). Change 1 touches the removal door and the permission readers. It touches the place of the sign. n174-W15 shows at the same commit gate, on an unread removal note.
   - Part B: the sign shows at the commit, where no door refused removals of base code. Change 1 touches the commit's compare of the base with the tree, the place of the sign. Change 2 touches the `touch_mistaken` and restore wakes, the route after the sign, another place.
7. Who started each change:
   - Part A: a read of a run, `plans/night169-m36-read.md`, during night 169. Frame 339 was "pushed 20:47 from the m36 read" (extract c, night 169, item 6).
   - Part B, change 1: frame 344's audit, on Roman's message of 2026-10-27 14:08, "Go back and review them".
   - Part B, change 2: a read of a run, sprint 32 row 2 on night 172's read (`plans/stack.md:338-344`).
8. The origin:
   - Part A: frame 339's provenance read: "no ruling made the removal door, the session built it in frame 283 W1a pass 1 at 92e240fc on 2026-10-21 from night 158's read ... the 'line N' matcher came at 2acc7b5c on 2026-10-23 in pass 2 with no brief, status line or review that asked for it; the sentence to copy came at e1cfcdd2 on 2026-10-24 in frame 312" (`plans/archive/stack-2026-10-28.md:33`). This pass did not read which wall of night 158 frame 283 answered. Origin class: a frame that answered another wall: frame 283, a wall of night 158's read.
   - Part B: the same removal door of frame 283, which did not see a removal inside a rewrite. F7's subject says the commit did not compare the base with the tree before 2026-10-28. The commit that set the old compare is not found by this pass. Origin class: not found.
9. After the end:
   - Part A: not applicable. Part A is open.
   - Part B: night 174 names n174-W15 at the same commit and seat, the Developer, with the opposite sign. Night 175 names n175-W9, "a Developer writes the criteria into the code". Not sure.

Row (Part A): Open | conditions changed | 1 | not applicable | frame 283 door | origin frame: 283
Row (Part B): Ended | same | 2 | absent only | not found | origin frame: none

### Chain 39: n170-W15, 4 turns, not sure

Reader: sub-agent, part b (`plans/method/chains-read-extract-b-2026-11-10.md`).

1. The wall: "pages after the stop say \"check: none yet\" [C?] (W15, F21)" (`plans/method/turns-list-2026-11-10.md:364`; `plans/night170-read.md:71`). First turn night 170, last turn dry1, 4 turns: n170, n172, n175, dry1. Rebuilt from column 8: n170-W15 to n172-W12 (not sure); n172-W12 to n175-W1 (not sure); n175-W1 to dry1-W7 (same sign at the same place, "the causes differ") (extract c, nights 170, 172 and 175, item 8). The walls carry two signs, so this block splits the chain.
   - Part A, a stop page whose check lines misstate the tests: n170-W15, "The pages after the stop say \"check: none yet\"" on m96 and m102 (`plans/night170-read.md:71`), and n172-W12, "The page says the tests fail, and every check line on it says \"Passes\"" (`plans/night172-read.md:69`). 2 turns.
   - Part B, the `tests_missing` tick stops a batch at 3 attempts: n175-W1, "The `tests_missing` tick on c_2 and c_3 stops bg_3" (`plans/night175-read.md:57`), and dry1-W7, "a dotted surface ref passes the vet; encode refuses every test" (`plans/dry1-third-wall-read-2026-11-01.md:7`). 2 turns. The sign is the same and the causes differ: on night 175 his deletion of c_2 and c_3 never reached the criteria (n175-W2), and on dry1 the Terminologist stored `surface_refs=['click.pause']`.
2. The state at the end:
   - Part A: Ended. Nights 173, 174 and 175 name no such wall by a firm link. Night 173 counts the sign at "0. No tick gave up on tests and no page stopped" (`plans/night173-read.md:205`). So on night 173 the case did not occur.
   - Part B: Ended. dry2, dry3 and dry4 name no such wall (extract c, dry1, item 8).
3. The conditions at the end:
   - Part A: nights 173 to 175 ran on R2, clickI and models B, the same as night 172. Same.
   - Part B: the chain crosses from the night series to the dry run series at dry1. Dry1 ran on click, and dry2 to dry4 ran on other repositories. Conditions changed.
4. The changes:
   - Part A, change 1. F20 with F21, merge 82d426c4 at 2026-10-27 16:48 (chain 2). The audit says "W15, \"check: none yet\", comes from `_gave_up_tries` reading the page's keys, which is F20" (`plans/rootfix-audit-2026-10-27-b.md:50`). Kind: other code of rota. In night 172's commit. The next read names W12: "New. The page shows the tick's words and no red line, because the red test has no criterion and no line" (`plans/night172-read.md:157`).
   - Part A, change 2. w12root, merge 189dc7b2 at 2026-10-28 10:07, "the stopped page names the red test, night 172's wall W12", with 61608940 "the stopped page names the red test". File: `rota/roles/principal.py` and the roles code. Kind: other code of rota, the page. It landed after night 173 ended at 10:00 and is in night 174's commit 3ac83acc. Nights 174 and 175 name no such wall (absent only).
   - Part A count: 2.
   - Part B, change 1. For n175-W1, no change found. Sprint 35 does not name it (grep of `plans/stack.md:149-230`).
   - Part B, change 2. Frame 356, "A dotted surface ref passes the vet as written, and the encode door refuses every test for the criterion" (`plans/archive/stack-2026-11-01.md:102`): eeed30cc "one resolver reads a surface ref for the vet and the encode door" and 584f7f91 "a method grain only when the class defines the method", 2026-11-01. Kind: other code of rota. Frame 356 closed at 18:25 on dry1 turn 12: "the Tester wrote a test for each of the three criteria in 9 sessions with 0 never-calls refusals, against about 50 on the three sessions of the third wall".
   - Part B count: 1.
5. The last change before the end:
   - Part A: w12root at 189dc7b2. Evidence: absent only. Night 173's "0" came before w12root landed, and on that night no page stopped on tests.
   - Part B: frame 356. Evidence: a frame closes on a count, "0 never-calls refusals, against about 50", on dry1 turn 12 (`plans/archive/stack-2026-11-01.md`, frame 356, status 18:25).
6. The place of the changes:
   - Part A: the sign shows in the stop page's check lines in `rota/roles/principal.py`, `_gave_up_tries` by the audit. Change 1 touches the key readers and the word tables, the readers that `_gave_up_tries` uses. Change 2 touches the stopped page's text. Both touch the page, the place of the sign.
   - Part B: the sign shows at the `tests_missing` tick and at the encode door that refuses every test. Change 2 touches the vet and the encode door's read of a surface ref, the place of dry1's cause. The place of night 175's cause, the retire of his deleted criteria, is another place. No change touched it within the chain. w14root of 2026-10-29, "a criterion that his words delete is retired", aims at n175-W2 (merge 5bc46206).
7. Who started each change:
   - Part A, change 1: frame 344's audit, on Roman's message of 2026-10-27 14:08.
   - Part A, change 2: a read of a run, sprint 32 row 4, "W12 under F21" (`plans/stack.md:349-351`).
   - Part B, change 2: a read of a run, `plans/dry1-third-wall-read-2026-11-01.md`, in the dry run of Roman's ruling of 2026-10-31 00:58.
8. The origin:
   - Part A: `git log -S "none yet"` on `rota/roles/principal.py` gives b0a2086e (2026-10-09, "the park ask is a page with the item and its criteria"), in the same session's status lines as frame 190 (`plans/archive/stack-2026-10-10.md:21`). The frame of b0a2086e is not sure. Origin class: not found.
   - Part B: the stop text "could not write the tests" comes from cc013d96 (2026-10-24), frame 312's pass, which answered n160-W5 (chain 36). The attempt bound is older. The dotted ref of dry1 passed a vet whose origin this pass did not read. Origin class: not found for the sign's cause. The page text is from frame 312.
9. After the end:
   - Part A: night 175 names n175-W1, a stop page on `tests_missing` with "The team gave up: the team could not write the tests after 3 attempts", at the same page. Not sure.
   - Part B: dry3-W2, "stopped page m39 says \"after 0 attempts\"", and dry4-W14, "`touch_mistaken` quarantine; page says \"after 0 attempts\"", are stop pages of another key (extract c, dry3 and dry4, item 4). Not sure.

Row (Part A): Ended | same | 2 | absent only | not found | origin frame: none
Row (Part B): Ended | conditions changed | 1 | frame closes count | not found | origin frame: none

### Chain 40: n171-W5, 4 turns, not sure

Reader: sub-agent, part b (`plans/method/chains-read-extract-b-2026-11-10.md`).

1. The wall: "the Critic's pass door refuses a compound criterion [C?] (W5)" (`plans/method/turns-list-2026-11-10.md:365`; `plans/night171-read.md:62`). First turn night 171, last turn night 175, 4 turns: n171, n172, n174, n175. Rebuilt from column 8: n171-W5 to n172-W1 (not sure, "the read says New") and to n174-W12 (not sure); n172-W1 to n174-W12 (not sure, "New") and to n175-W14 (not sure); n174-W12 to n175-W14 (same sign at the same place) (extract c, nights 171, 172 and 174, item 8). The signs differ in form: 10 `verdicts.emit` refusals with no verdict (n171-W5), a fail on a two-line docstring example (n172-W1, `plans/night172-read.md:58`), three fails on an invariant criterion (n174-W12, `plans/night174-read.md:71`), and a review cycle on bg_1 (n175-W14, `plans/night175-read.md:70`). The build session's own read joins them by place: "The one door in all three cases is `_pass_lines_c[heck]`" (`plans/critic-loop-read-2026-10-29.md`, the result, nights 171, 174 and 175). Night 172's W1 sits under the same fact F37, "the added code lines that a pass names" (`plans/night172-read.md:146`). One place, one seat and one step, so I do not split the chain.
2. The state at the end: Open. Night 175, the last run of the night series, named it (n175-W14).
3. The conditions at the end: the nights stopped after night 175, and the dry runs are another kind of run. Conditions changed.
4. The changes:
   1. Sprint 32 row 3, branch f37b: ce3ecce5 "the Critic's pass names one line or several, as a list", 3b26e66e "a docstring run is one unit, and a kept line answers the hold", 91dd9119 and 9fc4d30c, merged at 0eaff3f1 on 2026-10-28 07:08. File: `rota/roles/api.py` and the Critic's prompts. Kind: a door and a prompt of a seat. In night 173's commit 36d2a667. The next read: "a Critic fail on a multi-line unit, 1 to 0" (`plans/stack.md:277`). Night 174 names W12, a fail on an invariant criterion, which no added line can meet.
   2. Sprint 34 row 2 and sprint 35 row 4, after the read `plans/critic-loop-read-2026-10-29.md`: b3d7c775 "admit a kept line or a passing test for a kept criterion" (2026-10-29 11:14), 23416479 "check the kept and test routes as whole facts", 319a4767, e226cca3 and a662f776 (2026-10-29). File: `rota/roles/api.py` and `rota/roles/prompts/critic/review.md`. Kind: a door and a prompt of a seat. After the last night. The next read is dry1, which names no Critic loop wall (absent only).
   - Count: 2.
5. The last change before the end: not applicable. The chain is open.
6. The place of the changes: the sign shows in `_pass_lines_check` in `rota/roles/api.py`, which serves `verdicts_emit` (`plans/rootfix-audit-2026-10-27-b.md:169`), and in the Critic's `review.md`. The critic-loop read: "`_pass_lines_check` and `review.md` admit an added line or a fail only, so a criterion met by a kept line or a passing test loops" (`plans/stack.md:173-177`). Both changes touch `_pass_lines_check` and the Critic's prompts. They touch the place of the sign.
7. Who started each change:
   1. A read of a run, sprint 32 row 3 on night 172's read: "The Critic's one-line pass, W1, under F37" (`plans/stack.md:345-348`).
   2. A count and a read: sprint 34 row 2, "A count on nights 170 to 174, then a read" (`plans/stack.md:248-251`), then the read of 2026-10-29 for sprint 35 row 4.
8. The origin: `_pass_lines_check` comes from 1663c2bb (2026-10-07), "feat(desks): a pass names an added line per criterion". Its message: "Roman ruled on 2026-10-07 that the Critic names, for each criterion, the line of the change that meets it, and that the door refuses a pass that leaves a criterion unnamed. This commit builds frame 170's design". The audit marks F37 "FIXED", each half with one reader (`plans/rootfix-audit-2026-10-27-b.md:170`). This pass did not read which wall frame 170 answered. Origin class: a frame that answered another wall: frame 170, on Roman's ruling of 2026-10-07, wall not found.
9. After the end: not applicable. The chain is open.

Row: Open | conditions changed | 2 | not applicable | frame 170 door | origin frame: 170

### Chain 41: dry1-W14, 4 turns, not sure

Reader: sub-agent, part b (`plans/method/chains-read-extract-b-2026-11-10.md`).

1. The wall: "page m144 says the team gave up after a merge [C?] (turn 16, 2)" (`plans/method/turns-list-2026-11-10.md:366`; `plans/dry1-turn16-read-2026-11-02.md:8`). First turn dry1, last turn dry5, 4 turns: dry1, dry3, dry4, dry5. Rebuilt from column 8: dry1-W14 to dry4-W14 (not sure, "a stopped page with a wrong count, another key"); dry1-W16 to dry3-W2 (not sure); dry3-W2 to dry4-W14 (not sure); dry4-W13 and dry4-W14 to dry5-W12 (same sign at the same place, "as dry run 4 walls 13 and 14") (extract c, dry1, dry3 and dry4, item 8). The chain holds three signs, so this block splits it into three parts. The brief asks for two parts. Three parts are the honest split.
   - Part A, a stopped page whose count or state is false: dry1-W14, "`quarantine_stalled` quarantined `developer|tick:batch_start|bg_1` at 3 because s192, s256 and s265 each counted one restart resume" while bg_1 had merged (`plans/dry1-turn16-read-2026-11-02.md:8`); dry3-W2, "m39 said \"after 0 attempts\"" (`plans/dry3-wall1-read-2026-11-02.md:8`); dry4-W14, "the page says \"could not put back code it was not asked to change after 0 attempts\"" (`plans/dry4-read-2026-11-03.md:135`). 3 turns.
   - Part B, the `touch_mistaken` route quarantines after a wrong mistake judgement: dry4-W13, "the Developer's edit of `_foldline` at `8e706696` was judged a mistake" (`plans/dry4-read-2026-11-03.md:134`), dry4-W14 (the same quarantine), and dry5-W12, "quarantine of `developer|tick:touch_mistaken|b_1`, 3 attempts, then m70 \"The team gave up\"" (`plans/dry5-read-2026-11-04.md:61`). 2 turns.
   - Part C, a drop lands as a contest: dry1-W16, "a drop on the description loops as `contested`" (`plans/dry1-turn17-read-2026-11-02.md:8`), and dry3-W2, "his \"Drop it\" landed as `contest` and not as a drop" (`plans/dry3-wall1-read-2026-11-02.md:8`). 2 turns.
2. The state at the end:
   - Part A: Ended. dry5, dry6 and dry6b name no stopped page with a false count. dry5-W12's page says "The team gave up" after 3 attempts, which `tick_attempts` holds (`plans/dry5-read-2026-11-04.md:61`).
   - Part B: Ended. dry6, dry6b and dry6c name no such wall (extract c, dry5, item 8, "dry5-W1, W4, W5, W9, W11 to W13: not met in dry6, dry6b, dry6c").
   - Part C: Ended. dry4, dry5 and dry6 name no drop that lands as a contest (extract c, dry3, item 8; dry4 and dry5, item 4).
3. The conditions at the end:
   - Part A: dry4 and dry5 both ran on icalendar with the fold sentence (extract c, dry4 and dry5, item 2). dry6 and dry6b are of group d. dry6c ran "with `ROTA_ONESHOT=1` and the 3080 alone" (`plans/method/turns-list-2026-11-10.md:305`). Not sure whether the requests changed at dry6. This pass did not read group d's run lines.
   - Part B: dry6c changed two settings on one database (`plans/method/turns-list-2026-11-10.md:305`). Conditions changed in part.
   - Part C: dry3 ran on another repository from dry4 and dry5 (extract c, dry3 to dry5, item 2). Conditions changed.
4. The changes:
   - Part A, change 1. 0b90f02b at 2026-11-02 02:52, "fix(core): a drained start is not a stall, and his restart forgets the start count". Its message: "The wall is the page m144 of dry1 turn 16". Kind: other code of rota, the stall rule. Before dry3 (in 44088319, git merge-base). dry2 names no such wall. dry3 names W2 with another cause: "the re-survey's writes to rows in the key lifted its quarantine".
   - Part A, change 2. Frame 360, a66b9a31 at 2026-11-04 00:35, "fix(roles): a stall page names the count at its send". Files: `rota/roles/principal.py`, `rota/core/sandbox.py`. Kind: other code of rota, the page. Before dry5 (in 79b1cdb0, extract c, dry4, item 6). dry5 names no page with "after 0 attempts" (absent only).
   - Part A count: 2.
   - Part B, change 1. Frame 362, 40980c59 at 2026-11-04 00:20, "fix(api): frame 362, a statement moved into a nested block is not lost". File: `rota/roles/api.py`. Kind: a door. Before dry5. The next read: dry5-W12 names the quarantine again, on "the removal of the assert and the 1501 branch" (`plans/dry5-read-2026-11-04.md:61`). After dry5 no change names wall 12 (extract c, dry5, item 6: walls 5, 10, 11 and 14 got passes).
   - Part B count: 1.
   - Part C, change 1. Not found for the description row. `plans/stack.md:2190`: "A drop on an observed row with no end state is frame 357's reach, 4 of 10 line kinds, and waits on Roman's ruling there". Frame 357's shape B is "on the branch" at a84a1cf4, 2026-11-02 13:44 (extract c, dry1, item 6). This pass did not check that shape B covers the description row. Part C count: 0 found, 1 not sure.
5. The last change before the end:
   - Part A: a66b9a31. Evidence: absent only.
   - Part B: 40980c59 came before the last naming, dry5. No change came after it. Evidence: absent only. The sign is absent in dry6 to dry6c, and no record says why.
   - Part C: not found. Evidence: absent only.
6. The place of the changes:
   - Part A: the sign shows in `quarantine_stalled` (dry1), the lift of a quarantine on a row write (dry3), and `_stuck_ticks`, which reads `tick_attempts` while the stall store holds the key (dry4) (`plans/dry4-read-2026-11-03.md:135`). Change 1 touches the stall rule, the place of dry1's cause. Change 2 touches the stall page's count, the place of dry4's cause.
   - Part B: the sign shows in `_removal_entry` and `_lost_in_block`, the block compare (`plans/dry4-read-2026-11-03.md:134`). Change 1 touches the same compare in `rota/roles/api.py`.
   - Part C: the sign shows in `land`, which "ends a drop only on a statement or a request item", in `_item_drops` at `rota/roles/principal.py` about 3858, and in `contested.md` (`plans/dry1-turn17-read-2026-11-02.md:8`).
7. Who started each change:
   - Part A, change 1: a read of a run, `plans/dry1-turn16-read-2026-11-02.md`, within frame 353's dry run on Roman's ruling of 2026-10-31 00:58.
   - Part A, change 2: a read of a run, dry4's read: "Walls 8 and 14 went to frame 360" (extract c, dry4, item 6).
   - Part B, change 1: a read of a run, dry4's read: "wall 13 to frame 362" (same cell).
8. The origin:
   - Part A: `quarantine_stalled` comes from 90f09152 (2026-08-11, "fix(scheduler): a tick that cannot drain"), rota's first design. `_stuck_ticks`, which gives the count on the page, comes from ced9de67 (2026-10-24), frame 312's pass, which answered n160-W5 (chain 36). Origin class: a frame that answered another wall: frame 312, wall n160-W5, for the count of dry4's page; rota's first design for the stall rule of dry1.
   - Part B: `_lost_in_block` comes from 11d04b18 (2026-10-27, "fix(api): F7, the commit compares the base with the tree for removals"). F7 is frame 344's fact that answered n171-W4, removals with no grant (chain 38, Part B). Origin class: a frame that answered another wall: frame 344 (F7), wall n171-W4.
   - Part C: `_item_drops` comes from 351f63c8 (2026-11-01, "a landed drop on a request line ends the item as dropped"), in the dry1 days of frame 357, which holds dry1-W10, "a dropped request returns as items" (extract c, dry1, item 6). This pass did not confirm 351f63c8's frame. Origin class: a frame that answered another wall: frame 357 (not sure), wall dry1-W10.
9. After the end:
   - Part A: dry6c-W1, "the Developer's start gave up after 3 sessions that wrote no code" (`plans/method/turns-list-2026-11-10.md`, group d, dry6c), is a true give-up of another key. dry8-W10, "the stopped page names the wrong cause", is the same page with another false part, five runs after dry5. Not sure.
   - Part B: dry8-W10, "the restore wake changed the fold" (group d, dry8), names the same route of the Developer, two runs past the three-run window. Not sure.
   - Part C: not found.

Row (Part A): Ended | not sure | 2 | absent only | frame 312 count | origin frame: 312
Row (Part B): Ended | conditions changed | 1 | absent only | frame 344 F7 | origin frame: 344
Row (Part C): Ended | conditions changed | 0 | absent only | frame 357 drop | origin frame: 357

## The two tables

### 1. The cells by chain and part

The count of cell 4 is the count of the part, or of the chain where the
reader gave one count for both parts. "Commit, no frame" means a commit
that answered another wall and names no frame.

| Chain | Part | Cell 2 | Cell 3 | Cell 4 | Cell 5 | Cell 8 |
|---|---|---|---|---|---|---|
| 1 | | Open (the lead reads Ended) | same | 2 | not applicable | rota's first design |
| 2 | A | Open | changed | 2 | not applicable | commit, no frame |
| 2 | B | Open | changed | 1 | not applicable | rota's first design |
| 3 | | Ended | same | 4 | absent only | commit, no frame |
| 4 | | Ended | same | 2 | absent only | rota's first design |
| 5 | | Ended | same | 1 | frame closes count | commit, no frame |
| 6 | A | Ended | changed | 0 | absent only | rota's first design |
| 6 | B | Ended | changed | 0 | absent only | rota's first design |
| 6 | C | Ended | changed | 0 | absent only | not found |
| 6 | D | Ended | changed | 0 | absent only | not found |
| 7 | | Open | changed | 5 | not applicable | frame 267 |
| 8 | A | Ended | changed | 0 | absent only | rota's first design |
| 8 | B | Open | not applicable | 0 | not applicable | rota's first design |
| 9 | | Open | not applicable | 0 | not applicable | frame 298 |
| 10 | | Ended | same | 3 | read confirms count | not found |
| 11 | A | Ended | same | 3 | read confirms count | frame 93 |
| 11 | B | Ended | changed | 3 | absent only | not found |
| 12 | A | Ended | changed | 2 | frame closes count | rota's first design |
| 12 | B | Ended | changed | 3 | frame closes count | frame 234 |
| 13 | | Ended | changed | 0 | absent only | commit, no frame |
| 14 | A | Open | changed | 1 | not applicable | rota's first design |
| 14 | B | Ended | same | 1 | absent only | rota's first design |
| 15 | | Open | not applicable | 0 | not applicable | rota's first design |
| 16 | | Ended | same | 1 | read confirms count | commit, no frame |
| 17 | | Ended | same | 1 | absent only | frame 100 |
| 18 | | Ended | same | 3 | absent only | rota's first design |
| 19 | | Ended | same | 0 | absent only | commit, no frame |
| 20 | A | Ended | same | 2 | read confirms count | frame 250 |
| 20 | B | Ended | same | 2 | absent only | commit, no frame |
| 21 | | Open | changed | 4 | not applicable | commit, no frame |
| 22 | | Ended | same | 0 | absent only | frame 82 |
| 23 | | Ended | same | 1 | frame closes count | rota's first design |
| 24 | | Open | changed | 3 | not applicable | frame 306 |
| 25 | A | Ended | same | 1 | absent only | not found |
| 25 | B | Open | changed | 2 | not applicable | rota's first design |
| 26 | | Ended | changed | 2 | frame closes count | commit, no frame |
| 27 | A | Ended | changed | 3 | read confirms count | frame 345 |
| 27 | B | Open | not applicable | 2 | not applicable | frame 344 (F7) |
| 28 | A | Ended | same | 3 | frame closes count | frame 234 |
| 28 | B | Open | changed | 5 | not applicable | frame 250 |
| 28 | C | Open | changed | 2 | not applicable | not found |
| 29 | A | Ended | changed | 2 | absent only | frame 304 |
| 29 | B | Open | changed | 2 | not applicable | commit, no frame |
| 30 | A | Ended | changed | 0 | absent only | frame 170 |
| 30 | B | Ended | changed | 4 | read confirms count | frame 170 |
| 31 | A | Ended | changed | 1 | absent only | not found |
| 31 | B | Open | not applicable | 2 | not applicable | rota's first design |
| 32 | A | Ended | same | 2 | frame closes count | commit, no frame |
| 32 | B | Ended | changed | 1 | absent only | frame 110 |
| 33 | | Ended | same | 2 | absent only | commit, no frame |
| 34 | | Ended | same | 3 | frame closes count | commit, no frame |
| 35 | | Ended | same | 4 | read confirms count | frame 234 |
| 36 | A | Ended | same | 2 | frame closes count | frame 190 |
| 36 | B | Ended | changed | 1 | absent only | rota's first design |
| 37 | A | Ended | same | 2 | frame closes count | rota's first design |
| 37 | B | Ended | same | 1 | absent only | frame 335 |
| 38 | A | Open | changed | 1 | not applicable | frame 283 |
| 38 | B | Ended | same | 2 | absent only | not found |
| 39 | A | Ended | same | 2 | absent only | not found |
| 39 | B | Ended | changed | 1 | frame closes count | not found |
| 40 | | Open | changed | 2 | not applicable | frame 170 |
| 41 | A | Ended | not sure | 2 | absent only | frame 312 |
| 41 | B | Ended | changed | 1 | absent only | frame 344 (F7) |
| 41 | C | Ended | changed | 0 | absent only | frame 357 (not sure) |

Notes on the table:

- Chain 28, part B: its reader writes "frame not sure" for f0b2924c. Part a's chain 20 places f0b2924c as frame 250's pass 1 (frame 250, status 2026-10-16 00:49). The table writes frame 250.
- Chain 31, part B: the root read names the parser, the quoter and the surface door as August and September commits, and the "no escaping" text as frame 122's 28b2a060. The table writes the class of the first three.
- Chain 30, part B: the hold of night 161 is frame 201's own pass 3. The table writes frame 170, the frame of the block refusal of night 157.
- Chains 2, 7, 14, 24 to 26, 28, 29 and 36 to 41 come from part b, and part b counts a night chain that is open at night 175 as "conditions changed", because the nights stopped there.

### 2. The frames in cell 8 of more than one chain

| Frame | Chains |
|---|---|
| 170 | 30 (both parts), 40 |
| 234 | 12 (part B), 28 (part A), 35 |
| 250 | 7 (the second door, f0b2924c), 20 (part A), 28 (part B) |
| 344 (F7) | 27 (part B), 41 (part B) |

Frames 100, 110, 122, 190, 201, 267, 283, 298, 304, 306, 312, 335, 345, 357, 82 and 93 each appear in one chain.

## What this read could not find

- The sub-agents' lists are on their pages, in the sections "What I could not find". The lead does not copy them here.
- Lead, chain 6, parts C and D: the code that runs a repeat and the code that admits a made-up result were not traced. Part C is the sign of chain 1, whose cell 8 traces it.
- Lead, chain 11, part B: no commit that adds a merge of changes outside the criteria was found.
- Lead, chain 31, part A: the origin commit of `_escape_note` was not traced.
- Lead, chain 8: `plans/dry9-read-2026-11-10.md`:59 says "Frame 183 was built in build 2". Frame 183's own status of 2026-11-10 01:00 says its door and "W10 of dry run 7 ... stay open here". The two records disagree. The block follows the frame's line and does not repair either record.
- Lead, chain 30: no closing status line of frame 201 was found in `plans/stack.md`.
- Lead, chain 31: the link from dry run 5's W10 to dry run 6c's W5 in the lead's `chains.json` rests on a cell that reads "not met". The list's line 356 holds that chain. The list is not repaired here.
- The brief says the dry runs use another repository. Dry run 1 ran on click, the same repository as the nights (part b, "What I could not find"). Dry runs 4 to 9 ran on icalendar, and blind run 1 on another repository.
- An empty file `a7_compute.py` is in the repository root, untracked, with the time 2026-11-10 15:46:40. The sub-agents' last writes to their pages were at 15:44:27 and 15:44:43. No record of this read names the file. The read left it in place.
- `runs.tsv` is not in the repository. It is in the lead's scratchpad. Part a used the extracts' copies of its times.

## Apart from the blocks

The brief asks for any answer formed during the read to go here, apart
from the blocks. The two sub-agents wrote theirs on their own pages, in
the sections "Apart from the blocks". The lead formed none that the
counts above do not already state.
