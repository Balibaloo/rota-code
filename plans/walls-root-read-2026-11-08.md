# The walls of dry runs 6b, 6c and 7 with their provenances, reasoned together: the read, 2026-11-08

A read by C77 (`plans/method/reference.md` section 10), from the brief `walls_root_read_brief.md` of session 0ff6bcd7. The read lists, places and reasons. It fixes nothing. The session plans.

## Result

The 30 walls of the three runs and the claim arm of frame 360 make 20 distinct walls under four roots (observed: section 1). R1, a fact or a dependency that has no row: W1, W3, W5, W10, W11 and W20. R2, a fact that has a row that a reader does not read or that a push cuts: W2, W8, W9, W12, W13, W14 and W17. R3, a door or page text that names a wrong cause or an act nobody can do: W4 and W16. R4, the runtime outside the record: W6, W7, W15, W18 and W19. R1 is the biggest root: it ended dry run 7, cost dry run 6c a turn, and lets a false claim merge, and W20 is its control, because a row fixed it. 8 of 20 walls match a frame pushed and never built, 12 frames: 114, 127, 133, 134, 155, 166, 182, 183, 194, 260, 299 and 320. The proposal: each derived row names the row it rests on, and `scheduler.owed` counts a dependent of a changed row as owed, first as slice 2 of the contested record design with a guess stamp on `criteria`, about 3 cycles, reach 7 open places of 9, about 8 cycles for all.

## 1. The walls

Runs: 6b is turns 1 to 4 of `dry6b-read-2026-11-06.md`. 6c is turns 5 to 9 of `dry6c-read-2026-11-06.md`. 7 is `dry7-read-2026-11-07.md`. "Arm" is frame 360's replay on the dry6b database. A wall of a run is written as run-number, for example 7-1.

| W | Wall | Runs | Provenance (commit, date, frame) | The fact with no row | Seat | The row that should hold it | Frame matched | Built or pushed |
|---|---|---|---|---|---|---|---|---|
| W1 | His words on a running batch do not reach the seat that acts: "Do not remove that branch in _foldline" (7-1), and the middle sentence of m27 (6c-2) | 6c, 7 | `START_RULED_KEY` 6785f35b, 2026-10-24, frame 312. `removal_line` 11d04b18f, 2026-10-27, F7, "names no row and no key". One shape per ref in `menu_ruling` e810eb77, 2026-10-29, frame 345 (observed: `dry7-removal-read` section 2, `dry6c-wall2-correction-read` section 2) | The keep on the removed branch: 0 `ruled_refs` rows carry it. The m27 middle sentence: overwritten by the next add on the same ref (observed: the two reads) | Developer, and the Architect on `touch_strayed` | `ruled_refs` with act `keep` and `target_kind` `source_line`. The schema allows both, and 0 rows of dry run 7 use either (observed: `schema.sql` 818, the removal read section 3) | 173, 133, 299 | 173 built, passes 1 to 1d at 80440c1e to e611f9d6, then parked (observed: stack 3085). 133 and 299 pushed, never built. The push half is built today, 3e53c57a |
| W2 | The push cuts the base text: inherited rows fill 18,450 of 20,000 characters, so `[removed lines]` never shows (7-1, second half). `code.read` sits last in the Critic's wake (arm) | 7, arm | `PUSH_CHARS` b8c18fec. Frames 127 and 134, 2026-10-04 and 2026-10-05 (observed: `git log -S`, stack 3410 and 3370) | None. `code.diff` holds the removed lines, and the push budget evicts them (observed: the removal read section 4) | Developer, Critic | the row exists | 127, 134 | Both pushed, never built. The fix is built today under frame 362, 13b3a52e and 6b34d5e0, and neither frame moved |
| W3 | A correction moves one record and not the records derived from it: all 6 criteria keep `parameter.py::q_split` after the guess moved to `_foldline`, so the surface door refuses the Tester (7-2, and 7-10 first half) | 7 | `criteria.surface_refs` 395535da, 2026-08-27. `touch_guesses` 7ec9b940, 2026-10-18, frame 298. Slice 1 of the owed contest 0da8e39e to 5107f4dd, 2026-11-06, frame 362 (observed: `git log -S`, `git log`) | Which guess set a criterion's surface rests on. `criteria` has no `ruling_id` and no guess version, where `touch_guesses` and `batch_touch` each carry `ruling_id` (observed: `schema.sql` 390, 408 and 567) | Terminologist s150, then the Tester | a stamp on `criteria`, or a `refs` row of kind `ruling` from the criterion to the guess set | 194 in part. Slices 2 to 4 of the contested record design | 194 pushed, never built. Slices 2 to 4 designed, never built (observed: `design-contested-record-2026-11-06.md` section 6) |
| W4 | The Tester's encodes are refused until the key quarantines: false escape advice "no backslashes" and parser misreads (6c-5), and the `src.` import door that names the wrong import (7-10, second half) | 6c, 7 | Parser 5f445aab, 2026-08-24. Quoter 27bd2edb, 2026-09-02. "No escaping" 6333441b, 2026-09-12, and 28b2a060, frame 122. Surface door d2091d8c, 2026-09-09 (observed: `dry6c-wall5-backslash-read` section 3, `git log -S`) | None. The block form `body=[body]` exists since 858d7634, and no refusal names it (observed: the wall 5 read) | Tester | not a row: the refusal text | 155, 166, 260 | All three pushed, never built |
| W5 | A claim cites no source, so the Critic has no line to check and no row to quote, and the pass lands (arm). The one Tester test passes at the base (6c-7) | 6c, arm | The claim branch of `code_commit`. Frame 360's passes 5d4aa326 and 170e9250, 2026-11-06 (observed: `git log`) | The claim's evidence per criterion: none. Whether a Tester test is red at the base: the base run records inherited tests only (reasoned: `harness.base_red_ids`) | Critic | an evidence row per criterion on the claim, by shape E or H1 | 360, 182 | 360 in build now, slice 2 pass 1 of H1 (observed: stack 1884, status of 10:30). 182 pushed, never built |
| W6 | The Liaison's verdict sends one more model call after its relay, and gemma4 spends the 8192-token cap in silence past 300 s (6b-1) | 6b | The closing sentence c7a228dee, 2026-08-09. `ROTA_ONESHOT` c70156fcf, 2026-09-02, COMPLETION 3.32, "awaiting the seat's ruling" (observed: `dry6b-closing-call-read` section 2) | "The work is done" is text in a tool result, not a state that the runner reads (observed: the same read, section 1) | Liaison, and 6 of 7 seats | a session state, not a table row | none. COMPLETION 3.32 | Not built |
| W7 | `ROTA_ONESHOT` also turns off the hold of a write behind its read, so 3 Developer starts wrote nothing (6c-1) | 6c | c70156fcf, 2026-09-02 (observed: `dry6c-read` Result) | none | Developer | none | 360 by symptom only | Dry run 7 ran without the flag |
| W8 | The account page comes back after each "ok": a quarantined verdict on rows already approved never lifts (6b-2) | 6b | `_lift_quarantines` 258b9062, 2026-09-01. Frame 355, closed (observed: `git log -S`, the closing-call read section 6) | None. `rulings.status` is `landed`. The reader asks only whether a row moved (observed: the same) | Liaison, then the principal | the row exists | 355 | Closed. The read's fix 5 is not built (reasoned: no commit on `_lift_quarantines` since 2026-11-06) |
| W9 | A re-run after a stop counts one more attempt on the same commit, "attempt 12 of 10" (7-7) | 7 | `next_attempt` 10f41757, 2026-08-09 (observed: `git log -S`) | None. `test_runs.commit_sha` holds the commit. `next_attempt` reads `MAX(attempt)` by batch only (observed: `lifecycle.py` 518 to 524) | the harness, then the Developer | the row exists | 361 residue, "`rota run` never reaps a dead claim" | Residue, not built (observed: frame 361's residue line) |
| W10 | His answer on a term does not end the question (7-4). Five `term_collision` sessions reach no page (6b-4) | 6b, 7 | `term_collision` f6ac0c5b, 2026-08-14 (observed: `git log -L`) | His answer is keyed by sense id. A sense written after his answer has no ruled row, and the word he answered has none (observed: `predicates.py` 371 to 597, its lines 127 to 218; the dry 7 read question E) | Terminologist s114, Liaison s115 | a ruling ref on the word, not on each sense id | 183. The onboarding design's cut of the `term_collision` pages | 183 pushed, never built. The cut "is not built" (observed: frame 362 status of 2026-11-06 14:40) |
| W11 | The team invents criteria that the request does not say (6c-4, 7-8) | 6c, 7 | The twin refusal 395535da, 2026-08-27. Frame 322, passes built (observed: `git log -S`, stack 2113) | Which sentence of his request a criterion rests on. `refs` allows a criterion-to-statement row, and the request is one statement (reasoned: `schema.sql` 96) | Terminologist | a `refs` row from the criterion to a quoted span of his sentence | 322 | Built, residue open (observed: stack 2113, status of 2026-10-30) |
| W12 | The first guess picks a file by a word match, `q_split` and `split_on_unescaped_comma` (6c-8, 7-9, and dry runs 4 and 5) | 6c, 7 | The guess mode 7ec9b940, 2026-10-18, frame 298 (observed: the commit body) | Not read. The bound commitment `cw_99502ef494ad` on `string.py` line 122 is a row. Whether the guess wake reads it is not read | Architect | not known | none by heading. Frame 362's demand read in part | not known |
| W13 | An inherited red becomes a question to him, with the test's source on the page (7-3) | 7 | `unresolved_note` 09b87d48, 2026-08-14 (observed: `git log -S`) | None as a column. The red at the base is JSON in `config` `base_run:b1`. `predicates.unresolved` reads no base run (observed: `harness.py` 558 to 564, `predicates.py` 1402 to 1440) | Liaison s188 | a column on `tests`, or the same reader | 114 in part | Pushed, never built: 16 status lines, no pass (observed: stack 3465) |
| W14 | The rest line says "Nothing waits on you and nothing is building" with commitments 1 and survey 5 outstanding (7-5, and dry run 4) | 7 | `render_state` 9c5c71fe, 2026-09-08 (observed: `git log -S`) | None. The frontier is a query. `render_state` reads batches and quarantines only (observed: `principal.py` 640 to 694) | the principal | the query exists | 361 wall B | Residue, priced 2 cycles, not built (observed: frame 361's residue line) |
| W15 | The harness decodes pytest output as cp1252, 6 tracebacks (7-6) | 7 | `execute._local` 80a9f5e6, 2026-09-10 (observed: `git log -S`) | none | the harness | none | none | Fixed 6b4cf35d, 2026-11-08 (observed) |
| W16 | The run ends stuck with no page: "A new commit on the change starts it again" asks for an act that only code can do (6c-9, dry run 5 wall 14) | 6c | 4ae68ea7, 2026-09-30 (observed: `git log -S`) | none: a page form | the principal | not a row | none by heading | Not built |
| W17 | The Researcher has no search engine and answers in prose (6c-6) | 6c | e4f0dd1d, 2026-08-12, "discovery is a capability" (observed: `git log -S`) | None. The grant is known to the door that refuses (reasoned: the refusal text) | Vision Keeper, Researcher | the grant exists | none by heading | Not built |
| W18 | A blocked fault on 8 falsified claims (6b-3, dry run 5 wall 6) | 6b | `blindspot` e320238e, 2026-08-24 (observed: `git log -S`) | not read | Architect | not read | none read | not read |
| W19 | The 40-session limit ends turns 1 to 3 (6b-5, dry run 5 wall 2) | 6b | The default limit of 40 in `onboard_run.drive` (observed: `pause-read-2026-11-06.md`) | none: a run setting | none | none | none | a setting |
| W20 | The Architect's guess relay ends with no act, the relay is marked answered, and three Developers start on the old guess (6c-3) | 6c | `OWED_A_REPLY` in `db.py`. Frame 320 (observed: `f362-contested-guess-read` Result) | In 6c, no row said that the contest was owed. Slice 1 added `batch_touch.ruling_id` and `scheduler.owed` (observed: `schema.sql` 390, `scheduler.py` 1877) | Architect | now a row | 320, the contested record design | 320 parked, "no pass is built" (observed: stack 5212). Covered by slice 1. Dry run 7: the correction reached the batch 1 of 1 (observed: dry 7 read question A) |

## 2. The roots

**R1, a fact or a dependency that has no row.** W1, W3, W5, W10, W11 and W20.

- The fact has no row because no writer has a form for it. The removal line carries no ref (W1). `criteria` carries no stamp of the guess that it came from (W3). A claim carries no evidence (W5). A ruling keys a sense id and not the word (W10). A criterion quotes no span of his sentence (W11) (observed: section 1).
- The seat that needs the fact is the seat after the writer: the Developer, the Tester, the Critic, the Terminologist (observed: section 1).
- W20 is the control. Slice 1 gave the owed contest a row and a reader. Dry run 7's correction then reached the batch in one turn, where dry run 6c took two turns and three wrong starts (observed: dry 7 read question A, dry 6c read wall 3).

**R2, the fact has a row, and the reader does not read it or the push cuts it.** W2, W8, W9, W12, W13, W14 and W17. Each reader reads a subset: a budget (W2), row moves and not the ruling (W8), the batch and not the commit (W9), a config blob that one family of predicates reads (W13), batches and not the frontier (W14) (observed: section 1). W12 is placed here by a guess (reasoned: a bound commitment on `string.py` exists, and the guess wake is not read).

**R3, a door or page text that names a wrong cause or an act that nobody can do.** W4 and W16. W5 is in R3 in part: refusal 1 of the Critic's door names the `test:` route as the way to pass (observed: `f360-critic-claim-read` section C).

**R4, the runtime outside the record.** W6, W7, W15, W18 and W19. W6 also has an R1 face: the door's "done" is text and not a state (reasoned).

**The hypothesis against each wall.** The hypothesis: a thing with no row is invisible to every seat.

| W | Verdict | Why |
|---|---|---|
| W1 | holds in part | The keep had no row (observed). The second half of the failed restore is W2, where a row existed and the push cut it. 16 of 16 sessions that read the Architect's note still wrote "Restore" or "no changes needed" (observed: the removal read section 7). So the row is necessary and not sufficient |
| W3 | holds | The guess correction landed as rows. The criteria had no row that ties them to the guess, so no reader saw them as stale (observed: `schema.sql` 567) |
| W5 | holds | The claim has no row that a challenge can quote, refusal 4 (observed: the claim read section C) |
| W20 | holds | A row fixed it (observed) |
| W10 | holds in part | His answer is a row, keyed too narrowly (observed: `term_collision` lines 127 to 218) |
| W11 | holds in part | A row to the request exists. It is too coarse to refuse an invented case (reasoned) |
| W6 | holds in part | "Done" is not a state. The loss itself is the model's silent run (observed: the closing-call read) |
| W2, W8, W9, W13, W14, W17 | fails | The fact had a row, and a reader did not read it. R2 fits better |
| W4, W16 | fails | A text names the wrong cause or step. R3 fits better |
| W7, W15, W19 | fails | The runtime. R4 |
| W12, W18 | not known | not read |

Count: the hypothesis holds on 4 of 20 walls, holds in part on 3, fails on 11, and is not known on 2. On the three walls that the session named, the removal, the criteria and the claim, it holds on all three, with W1 in part (reasoned: the table). As a general law it fails: R2 has 7 walls and R1 has 6.

**The unbuilt frames.** 8 of 20 walls match a frame pushed and never built: W1, W2, W3, W4, W5, W10, W13 and W20. 2 more walls, W9 and W14, match an unbuilt residue line of a built frame (observed: section 3). Of the 10 walls of dry run 7, 6 sit on an unbuilt frame or residue: W1, W3, W9, W10, W13 and W14 (observed: section 1).

**The biggest root is R1, by cost.**

- W1 ended dry run 7: 19 `touch_mistaken` sessions, 8 commits, a quarantine and a park (observed: dry 7 read question C).
- W3 cost the Tester 13 refused encodes in turn 6 and 4 in turn 7, and left 1 of 3 live criteria on `q_split` (observed: dry 7 read question B).
- W5 lets a false claim merge: 1 of 1 claims false, 1 of 19 merges (observed: the claim read section H).
- W20 cost dry run 6c one turn and three Developer starts (observed: the contested guess read).
- R2's biggest cost is W2 inside W1. Each other R2 wall cost one page or one attempt (reasoned: section 1).

## 3. The unbuilt frames

Each line is the frame's push line in `plans/stack.md` (observed: `grep -n "^### N\. "`, then the heading, the Ends-when, Waits-on and Sprint lines, and the last three status lines only).

- 114: "Status 2026-10-02 13:47 (rota-65): pushed by eca94a44, unclaimed, blocked on Roman." 16 status lines, no pass. Waits on: "A build frame on two doors ... unclaimed, sprint 12 row 2."
- 127: "Status 2026-10-04 15:26 (rota-da): pushed by 419281dc. Unclaimed, unpriced until the read." The last line, 2026-10-05, names "a diff block of about 9,400 characters, frame 134". Waits on: "Roman's order."
- 133: "Status 2026-10-05 01:25 (rota-2e): pushed by e6218d79. Unclaimed, priced." The only status line.
- 134: "Status 2026-10-05 01:25 (rota-2e): pushed by e6218d79. Unclaimed, priced." The only status line. Waits on: "Recommended with frame 127".
- 155: "Status 2026-10-06 14:40 (rota-66): pushed by 488d31af from frame 152's hand-off". The only status line.
- 166: "Status 2026-10-06 16:36 (rota-66): pushed by 488d31af from night 126's read." The only status line.
- 182: "Status 2026-10-08 01:53 (rota-a1): pushed by 18588d6d from night 130's read." The last line, 2026-10-10, adds a night 138 instance. No pass.
- 183: "Status 2026-10-08 05:07 (rota-a1): pushed by 18588d6d from night 131's CYCLE line". The last line is night 133. No pass.
- 194: "Status 2026-10-10 10:38 (rota-91): pushed by 3be6b81d". The last line, 2026-10-10 14:12: "night 138's read says keep it open".
- 260: "Status 2026-10-16 03:29 (rota-05): pushed from frame 222's pass 1, unclaimed." The last line, 2026-10-17 16:40: "the surface door refused 26 times".
- 299: "Status 2026-10-18 12:40 (rota-04): pushed from frame 298's design review by the holding session, not started." The only status line.
- 320: "Status 2026-10-25 01:38 (rota-4a): Parked for the economy ... no pass is built".

Frames 127 and 134, named by C77 behind the biggest wall, are both pushed and never built (observed). Their cause was built today under frame 362, at 13b3a52e and 6b34d5e0, and neither frame took the count. By C77, a wall that matches an unbuilt frame moves that frame to the front with the new count (observed: C77).

Built frames with an unbuilt residue that matches a wall: 361, wall B and the reap (W14, W9). 173, built and parked after night 153 counted 0 of 3 (W1). 322, built with residue (W11). 306, its evidence half open (observed: stack 3085, 1857, 2113 and 2204).

Designs written and not built: slices 2 to 4 of `design-contested-record-2026-11-06.md` (W3, and W10 in part), and the cut of the `term_collision` pages in the onboarding design (W10) (observed).

## 4. The proposal

**The place.** `rota/core/scheduler.py` `owed`, line 1877, with one stamp on each derived row. A row that a seat writes from another row names the row and the version that it rests on. `owed` then counts a row as owed when the row under it has a newer ruling or a newer version. Slice 1 already does this for the guess line and the batch line through `ruling_id` (observed: `schema.sql` 390 and 408, `scheduler.py` 1877). The first step is slice 2 of the contested record design with one more edge: `criteria` records the guess set it was written from. A criterion whose guess set has a newer ruling is owed before `tests_missing` and the surface door read it (reasoned).

**The candidate "the reading that turns his words into rows", held against the code.** It is right for 2 of the 6 R1 walls and wrong for 4.

- Right for W1's middle sentence (6c-2): the one shape per ref of `menu_ruling` is in the reading (observed: the correction read section 1).
- Right in part for W1's keep. The reading cannot key a line that the page does not number. `removal_line` "names no row and no key", so the fix starts in the page and then reaches the reading (observed: `principal.py` `removal_line`).
- Wrong for W3. The guess correction did land as rows: `touch_guesses` with `ruling_id` m26, and `batch_touch` (observed: dry 7 read question A). The Terminologist wrote the criteria from the old guess, and no reading of his words is on that path.
- Wrong for W5. The claim is the Developer's words, not his.
- Wrong for W10 and W11. The rows exist with keys at the wrong grain, and the Terminologist's writes set those keys (reasoned).

So the general place is the "rests on" edge and its reader. The reading is one writer of that edge, not the place.

**The reach.** 9 places where one row rests on a row that he or a seat can change: the guess line, the batch line, the criterion, the test row, the glossary term, the constraint or model area, the statement, the source line of a removal, and the claim (observed: the contested record design section 1, table rows 1 to 7; the removal read section 3; the claim read section H). Slice 1 covers 2 of 9. So 7 of 9 places are open. The item's state, row 8 of the design, already holds as a state (observed).

**The price.**

- Slice 2 with the guess edge on `criteria` and the test row: about 3 cycles, the reach count first, then a pass and a review (reasoned: the design, "Each later kind about 20 lines and its readers").
- The keyed removal line: a design page first by C76 step 3b, then a pass and a review, about 4 cycles (reasoned: the removal read, F3).
- The term and the constraint, slice 4: about 1 to 2 cycles (reasoned).
- The claim stays on frame 360, which builds H1 now.
- In all, about 8 cycles for the whole reach, and 3 for the first step.

**The control on dry run 8.**

1. Before the run, with no model: copy `w5.db` of dry run 7 and run `owed` on `c1` to `c3` after s147's guess relay. Today they are not owed. After the fix, all three are owed (reasoned: the design's check style).
2. On the run: live criteria at the end whose surface names a file outside the batch's touch set, from 1 of 3 to 0.
3. On the run: Tester encodes refused by the surface door on a stale surface, from 9 in s185 to 0.
4. When he writes "do not remove": `ruled_refs` rows with act `keep` on a `source_line`, from 0 to 1 or more, after the keyed removal line.
5. Beside these, the R2 count of today's builds: Developer first pushes that are cut, from 25 of 35, and `touch_mistaken` pushes that hold `[removed lines]`, from 0 of 16.

## 5. Doubt

- I read no run database. Every count of a run comes from the reads named (observed: the brief's rule).
- W12 and W18 are not read. The root of W12 is a guess.
- W11's "the request is one statement" is reasoned and not counted in `refs`.
- W17's "the grant is known to the door" is reasoned from the refusal text, not from the code.
- I matched a wall to a frame by its heading, by the deeper reads, and by the frame's own lines. I read only the heading, the Ends-when, Waits-on and Sprint lines and the last three status lines. A pass in a middle status line can hide there. Frame 173 had passes in its middle lines, and I read its pass lines by grep (observed: stack 3096 to 3101).
- I found a built frame by a pass and a commit in a status line. Frame 361 says "the fix is on rota/foundation" with no commit in that form, and I count it built by its Waits-on line (observed).
- The cost ranking of R1 against R2 rests on one run per wall.
- The price of the proposal is reasoned from the design's own sizes. No pass brief exists.
- The claim arm is frame 360's replay and not one of the three runs. I list it because the brief names the claim.
