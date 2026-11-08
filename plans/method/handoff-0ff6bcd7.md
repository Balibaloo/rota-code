# Handover from session 0ff6bcd7 (rota-f6), 2026-11-08

Result first: the C77 root-cause read across dry runs 6b, 6c and 7 is done,
and its first step is built. Twenty distinct walls sit under four roots. The
biggest root by cost is R1, a fact or a dependency with no row. Its first step,
slice 2 of the contested record, is on the checkout: a criterion records the
guess ruling it rests on, and a stale criterion holds its batch and wakes the
Terminologist. H1 of frame 360 is on the checkout too: the Architect runs one
program at a claim, the door records the exact printout, and the Tester and
the Critic read it. The design's first count is measured and red: the Tester
on qwen3:8b, shown the split-word printout, wrote no check against the split,
0 of 5. The interview found the cause in the record, the wake showed no input
and no width, and pass 2a fixes the sentence. The gate on that checkout runs
at the hand-off. Dry run 8 from zero is the next step, and its scripts are
ready. No correct merged change exists yet. The taker holds frame 362 with
357, 358, 360 and 361.

## What happened, at altitude

1. **The C77 root-cause read.** `plans/walls-root-read-2026-11-08.md`. The
   sender's hypothesis, a thing with no row is invisible to every seat, holds
   on the three biggest walls and fails as a general law: 4 of 20 whole, 3 in
   part, 11 fail. R2, a row exists and a reader skips it or a push cuts it,
   has 7 walls to R1's 6. Twelve frames were pushed and never built, 114, 127,
   133, 134, 155, 166, 182, 183, 194, 260, 299, 320. By C77 every matched
   frame took its count at `33a3a807`, and 127 and 134 closed into
   `plans/archive/stack-2026-11-08.md` on the removal fix of this morning.
   "The reading that turns his words into rows" is the wrong place: right for
   2 of 6 R1 walls. The general place is the "rests on" edge and its reader,
   `scheduler.owed`.
2. **Slice 2 of the contested record, built.** `2afce977` to `b3973125`, plus
   `b27fb330`. `criteria.guess_ruling`, the Terminologist's criteria doors as
   the one writer, stamped with the verdict the `tick:criteria` push showed.
   `scheduler.criterion_owed` reads a criterion as owed when his newest ruled
   set is newer than its stamp. `tests_missing` holds the batch, the
   Terminologist wakes on `tick:criterion_owed` in `criterion_repair` with the
   new set and his words, and `api._refuse_owed` refuses the Tester's encode
   of an owed criterion with one line that names the rewrite. On dry run 7's
   `w5` copy, `owed` on c1 to c3 goes from None to m26 with `_foldline`.
   Review `plans/f362-review-slice2-p1.md`, two looks, pick. Reach: 10
   places, 2 covered and the test row in part; `_criterion_surface_pushes` is
   the one dry run 7 would hit next.
3. **H1 of frame 360, built.** `bcb11a0b` to `1c66f010` and `9ec70996` to
   `e3637731`. The `tick:claim` wake, the `code.run` door with its refusals
   and the `claim_runs` table, the Tester's and the Critic's readers, the P1
   door fix, and the guard fixes. Review `plans/f360-review-h1-p1.md`, two
   looks, pick. Roman's ruling of 10:01 stands: a claim closes with a check
   that runs, and the Architect's run is the evidence.
4. **The measure, 0 of 5.** The register case
   `L1-TS-the-run-shows-a-split-word` on qwen3:8b: 4 of 5 Testers wrote
   `assert _foldline(line) == line`, 1 of 5 `assert "_foldline" in line`. The
   interview, `plans/f360-tester-interview-2026-11-08.md`: the wake held no
   input and no fold width, and nothing said what ⏎ means. Pass 2a shows the
   call with its input and width, and the phrase "A ⏎ marks a fold". The gate
   at the hand-off re-records the case: that count is pass 2a's measure.
5. **The gate baseline** moved to `a95298b3`: 32 known reds, 7,232 passed,
   stale 0. The old baseline of 2026-10-31 had 34.
6. **Housekeeping.** This session's watcher died with its previous process
   and left a nulls row; `handover.py peers` printed UNREADABLE for it. The
   re-arm rewrote the row. The sender's implementer on H1 was not cut: it
   committed after the hand-off, and the resume agent found it done.

## What comes next, in order

1. **The gate's result, read at the hand-off:** 34 failed and 7,288 passed
   against the baseline's 32, the six guard reds gone, stale 0, 2 new reds
   and both are the register cases, each 0 of 5 on qwen3:8b. Two findings
   from their recordings, both in the record and neither built:
   - `L1-AR-run-the-code-at-a-claim`: the Architect sent `code.run(text)`
     three times per run, the word `text` and no program, copied from the
     tools line, so the door wrote no row and no refusal names the cause.
     The fix is in the claim mode's prompt or the door: the prompt shows one
     real program inside the call, and the door refuses a bare `text` with
     one sentence. About 1 cycle, then re-record. The probe of 2026-11-08
     had 4 of 5 run a program, with a different wake.
   - `L1-TS-the-run-shows-a-split-word`: pass 2a did not move it. The door
     `tests.encode` told every run "the criterion, its ticket or the
     principal's words say it prints; nothing says it returns anything", so
     the Tester asserted on stdout through `sys.stdin`. The word it read is
     the run sentence's own "it printed:". The interview's second finding is
     confirmed by the door's text. The fix: the run sentence says "showed"
     or "gave", or the prints door leaves the run sentence out of the
     material it reads. About 1 cycle, then re-record with the interview on.
   Store the baseline after those two passes, or now with the two as known
   reds: `python -m rota.tools.gate --baseline`.
2. **Dry run 8 from zero**, the same request, from
   `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/0ff6bcd7-73e0-40b9-af75-01c8fdc9ed9a/scratchpad/dry8/dry8_start.sh <commit>`
   and `dry8_turn.sh <copy> <msg>=<words> ...`, copied from dry run 7's. The
   session is the Principal (ruled: Roman, 2026-10-31 00:58). Count: his
   answer on a running batch reaches the Developer's next wake (from 0 of
   22), the criteria after a correction of the guess (from 1 of 3 live on
   `q_split`), surface-door refusals on a stale surface (from 9), the restore
   of removed code, a claim with its run and the Tester's check on the
   printout, and the first merge. Read the run by C77's order: the walls,
   their provenance, the match to a frame, then one reasoning, then the plan.
3. **H1 pass 2**, the principal's line in every state (RC of the design's
   revision): `runner._claim_line`, `claimed_lines`,
   `principal._built_words`. About 2 cycles.
4. **Slice 3 of the contested record**, the pages he reads: the hold and the
   spent key with the way out, `code_target` and `code_line` show an owed
   line. The Stuck line's words are a stopgap. About 2 cycles.
5. **The restore as an act of the structure** (the sender's item 5): the
   stray rows hold the statements and their base lines; when his word or the
   Architect's judgement says keep, the structure puts them back from the
   fork. Read the reach first. About 3 cycles after a read.
6. The rest of the sender's list: the term answer that does not end the
   question (W10, frame 183), the legend beside his words, the backfill of
   the owed stamp, the rest line of frame 361 (W14), the re-run's attempt
   count (W9), Roman's milestone of 2026-11-06.

## Open and not built

- `criteria.specify` stamps '' on any wake that is not `tick:criteria`, one
  needless rewrite wake per criterion written there when a ruled set exists.
- The contest-on-criterion condition of design row 3 is not built: a
  check-only ruling writes nothing, so the hold would never lift.
- `code.run`: a store through a name that holds a namespace, `d = vars(m)`,
  passes the text check; a renamed copy beside a real call passes too. A
  change to an existing ignored file is not put back.
- The Critic's claim note still rests on the tests and the run; no seat
  judges the printout. The design holds that by H1.
- 57 red inherited rows carry whole bodies on a restore wake (frame 127's
  case, now closed into the archive on the fold fix; the whole-body read by
  id is still open under frame 362's residue).
- `L1-DV-apply-the-answer-and-carry-on` is a known red at 0 of 5 since the
  baseline of 2026-11-08 11:15.

## What I believe, and what to doubt

- The order slice 2 before dry run 8 is this session's reading of C77, not
  a ruling: the biggest root first, and dry run 8 would have walled on the
  stale criteria next. Roman re-orders if he disagrees.
- The measure of 0 of 5 rests on one case, one model and one wording. Pass
  2a is one change to the wording, and the re-record is its only count.
- Every implementer and reviewer today ran over its cap, by 1.2 to 2.
- The gate's two picks merged by hand in `predicates.tests_missing`: the
  claim loop first, the owed hold after it, then the spent-key filter. The
  four files of both frames gave 145 passed on the merged checkout, and the
  gate at the hand-off is the proof.

## Records

Briefs and reports in this session's scratchpad,
`C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/0ff6bcd7-73e0-40b9-af75-01c8fdc9ed9a/scratchpad/`:
`walls_root_read_brief.md`, `c77_frames_brief.md` and `c77_frames.py`,
`f362_slice2_p1_brief.md`, its report and review brief, `f360_h1_p1_resume_brief.md`,
`f360_h1_p1_report.md` (passes 1 to 1c), `f360_h1_p1_review_brief.md`,
`f36x_guards_report.md`, `dry8/`, and the reviewers' probes under `r360h/` and
`r362s2/`. Worktrees: `rota_p360h` at `c43d48ca`, `rota_p362c` at `affbaea5`,
`rota_p36x` at `18c7df55`, `rota_r360h`, `rota_r362c`, all picked and
removable. The pages: `plans/walls-root-read-2026-11-08.md`,
`plans/f362-review-slice2-p1.md`, `plans/f360-review-h1-p1.md`,
`plans/f360-tester-interview-2026-11-08.md`.

This session keeps the end of its context to answer the taker.
