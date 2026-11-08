# Review: the design amendment of 2026-11-08, shape H (frame 360)

A read-only review on Opus of `plans/design-false-claim-2026-11-06.md`, section "Amendment of 2026-11-08", H0 to H11. The code is read at c8b73b54 on `rota/foundation`. No model ran. No tracked file changed. The probes are in `rev360/` in the scratchpad of session 0d047fa7.

**Verdict: revise. 2 high, 7 medium, 5 low.** The act and judgement split of H1 follows from the counts. The page states the limit of H1 too weakly, and the question to the principal omits his ruling of 2026-11-06 14:19.

## (a) The verdict on each point

1. H1 follows from the counts: 4 of 5 did the act, and 4 of 4 got the verdict wrong. The limit is stated untruly, because a printout that shows the fault also merges (F1).
2. The three refusals are checkable from the syntax tree. They catch A4. They admit A1 to A3 only if a name bound by an import is exempt. A run that raises or prints nothing has no defined record (F4, F5).
3. The page names 14 places, not 13, and it misses no reader of `claimed_head`. It misses the wiring that the probe had to patch (F6, F10).
4. Each sentence is true for a true claim, a false claim and no run. A run that raised gives an empty "it printed:" sentence. The stored stdout is not exact for a plain print, so store the exact text and show visible fold marks (F3, F4, F11).
5. The departure of H2 from ruling 2 is stated truly for the default form. The page misses that the 14:19 ruling already names the opt-in form. The rate of 1 of 19 comes mostly from merges before the claim door existed (F2, F7, F8).
6. Both new findings are CONFIRMED: `rota/roles/api.py` 19411 to 19435, and `rota/roles/principal.py` 2738 to 2740.
7. The question has a story, everyday roles, today's behaviour, an analogy and no identifiers. It omits the 14:19 ruling and the true limit of option 1, and it overstates the trial (F1, F2, F9).

## (b) Findings

**F1. High. CONFIRMED. The limit of H1 is stated as "a weak example". The true limit is wider.** Page lines 312, 490 and 476. H0 says "The fact gates nothing", so only the Tester can stop the merge, and nothing measures the Tester with the run. On the probe, 2 of 5 printouts show the split, and under H1 nothing stops the merge in those 2 samples. Option 1 in H10 says "a poor example prints nothing wrong, and a false 'already done' can still close". A reader takes the close as a result of the poor example only. The "Next on a count" trigger of H9 counts merged claims whose printout shows the fault. On the measured case, the page's own data predicts that the trigger fires on the first such claim. Fix: state the limit as "a false claim closes even when the printout shows the fault, unless a test goes red". Say that the trigger is predicted to fire on the case already measured.

**F2. High. CONFIRMED. The question and H9 omit the ruling of 2026-11-06 14:19.** The ruling says: "It can close as long as it is verified by another seat (and the review every merge setting is not on)" (`plans/stack.md` 1921). H2 line 380 says that the ruling "stays met in form, by the Critic's pass". The read section G and P1 show that this pass cannot verify: 0 of 5 said that the claim is false. H10 line 482 opens with 12 September only, and it says "Option 1 departs from no ruling". Under option 1 the condition of his ruling is met in form and is empty in fact. The provenance rule asks for that ruling, its date and the departure at the top of the question. Fix: open the question with the 14:19 ruling, and say that option 1 meets "verified by another seat" in form only.

**F3. Medium. CONFIRMED. The door stores a fold printed without `repr` as two line feeds.** `execute._local`, `rota/core/execute.py` 43 to 45, decodes with universal newlines. On Windows the child also writes each LF as CR LF. Probe `rev360/crlf.py` printed "splitting wo", CR LF, " rds". The stored stdout held "splitting wo", LF, LF, " rds", and no CR. A3's stdout shows the same two LFs after "words", and the A3 seat read them as "inserts two newlines". So the claim of H2 and H6 that the record is the exact stdout holds only for a `repr` print. The brief asks for `repr`, but the door must not depend on the brief. Fix: reconfigure the child's stdout with `newline=""` and capture bytes, then show each CR LF in his line as one visible fold mark.

**F4. Medium. PLAUSIBLE. A run that raises, or prints nothing, has no defined record or line.** Lines 352, 431 and 435 to 437. "The door records each run that completes" does not say whether a return code that is not 0 completes. If a raise is not recorded, A1's first run is lost, and the line says "No run of the code is on record", which is false. If a raise is recorded, the line says "it printed:" with nothing after it. A1's first run raised an `AssertionError` inside `_foldline`, which refuses a line that holds a line feed. That is a fact about the code. Fix: let "completes" mean "did not time out". Record the return code and the stderr. For a return code that is not 0, the line says "The run stopped with an error", then the last line of the stderr. For an empty stdout, the line says "it printed nothing".

**F5. Medium. CONFIRMED. Refusal 2 refuses A1 to A3 when it is read literally, and refusals 2 to 4 admit a renamed copy.** Lines 349 to 351. Probe `rev360/refusals.py` read the touch and its 13 names from the sample database and from `string.py`. A1, A2 and A3 each bind `_foldline` by `from icalendar.parser.string import _foldline`. A4 defines `_foldline` and imports nothing, so refusals 2 and 4 catch it. A program that has `import icalendar` and defines `def fold` passes all three refusals, because refusal 4 accepts a parent package. H2 line 366 accepts "not every dodge", but this dodge is the act of A4 with a new name. Fix: refusal 2 counts definitions and assignment targets only. Refusal 4 asks for a call of a name that the program imports from a touch module.

**F6. Medium. CONFIRMED. The reach and the price miss the wiring that the probe patched.** The probe sets `runner._wake_allow` and adds its wake kind to `runner.DETAIL_SHOWN` (`probe_architect_claim.py` 149 to 159, `rota/core/runner.py` 288 and 442). It also adds two edges to the graph of `rota/design/graph.py`. H2's file list (345 to 354) names none of these. Without the `DETAIL_SHOWN` entry, the seat does not see the request and the touch. `TICK_WORDS`, `rota/roles/principal.py` 2539, has no `claim` kind, so a stuck tick reads "the team could not finish a step". Fix: add the runner, the graph edge and the tick words to H2, and price them in H9.

**F7. Medium. PLAUSIBLE. The rate "1 of 19 merges" comes mostly from merges before the claim door.** Line 310 marks it as observed. The claim mark landed on 2026-11-02 at 657cf1a81 (git log). Most of the 19 merges are night merges, and I did not check their dates. Since the door, dry run 6b had 1 claim and dry run 7 had 0. The cost to his attention under H2 depends on the rate after the door. Fix: give the count of claims and merges since 2026-11-02, and mark the 1 of 19 as a rate from before the door.

**F8. Medium. CONFIRMED. The opt-in form of H2 departs from no ruling, and the question does not offer it.** The 14:19 ruling names "the review every merge setting". `merge_gate=review` holds a claimed batch today, and no page shows that hold (line 396). So a page for that hold, with the printout on it, is inside his rulings. Option 2 in H10 offers only the default wait, which departs from ruling 2. Fix: offer option 2 as "the job waits for you only when you switch on the review setting". Price the hold page that it needs.

**F9. Medium. CONFIRMED. The story in H10 overstates the trial, and option 2 has no next step after "no".** Line 486 says that the planner "ran it on the old code, five times". The table shows that A5 ran nothing and A4 ran its own copy. The line says that the planner wrote "words intact" and "the claim holds" "in all four of its reports". A3 wrote "The claim is violated", and A4 copied the real stdout. Only the yes/no mark was "holds" in all four. Option 2 does not say what happens after his "no". H3 says that his words go to the builder and the tester. Fix: write "ran a program four times, three of them on the project's own code", and "in all four reports it marked the claim as holding". Add the step after "no".

**F10. Low. CONFIRMED. The reach counts 14 places, not 13.** Row 13 of H7 holds two places, `_built_words` and `tests_missing.md` 27. A search for `claimed_head`, `_claimed(`, `critic_claim_note`, `claimed_lines`, `CLAIM_DETAIL` and `_claim_line` finds no other reader. `claimed_lines` has two callers, 399 and 468, and one change covers both. Fix: write 14.

**F11. Low. PLAUSIBLE. Two words of the line in H6 are false in some states.** "ran the code on one example" is false for A2's third run, which printed two inputs. "The only other evidence" reads wrong after "No run of the code is on record". Fix: write "ran one program", and drop "other" when there is no run.

**F12. Low. PLAUSIBLE. The predicate keys the wake by head, and the reader keys the run by batch.** Line 353 says "no ended `tick:claim` session at its head". `rota/core/boot.py` 167 to 179 moves the head and `claimed_head` together. After that move, a claim with no run (A5) wakes the Architect again. Fix: key the predicate by batch.

**F13. Low. PLAUSIBLE. The door names no act for a program that writes into the worktree.** The door takes no path, but the program can still open a file of the tree. A4's first try aimed at `src/icalendar/parser/string.py`. Measure 3 checks `git status` for A1 only. Fix: the door reads `git status` after each run, puts the tree back, and records the fact in the row.

**F14. Low. CONFIRMED. H0 says that the status of 09:29 "already withdrew" the reading of 08:20.** The status of 09:29 says "Roman rules its gate after the page". That defers the gate to him, and it does not withdraw it. Fix: write "deferred to his ruling".

**Outside the points.** F6, F12 and F13 lie outside the seven points.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/0d047fa7-9b87-4f76-a8a4-18bf24ea3678/scratchpad/rev360/refusals.py` applies refusals 2 to 4 with `ast` to A1 run 2, A2 run 3, A3 run 1, A4 run 1 and one renamed copy. It reads the touch from `arch/live/sample_1/dry6b.db` and the names from `string.py`.
- `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/0d047fa7-9b87-4f76-a8a4-18bf24ea3678/scratchpad/rev360/crlf.py` runs a child that prints a CR LF fold through `rota.core.execute.run`, and it shows the stored text.
- Read-only queries: `arch/live/results.json`, each run's stdout and record. `p1/run/results.json` and `p1/run/sample_1/dry6b.db`, the turns of s164: `claim_encodes('c2', encodes=False)` at turn 1, then a landed pass with `test: tst_fold_c2` at turn 4.

## (d) Usage

These are estimates, because the harness shows no count to this agent. Input is about 80k tokens of context at the end. Output is about 12k tokens. The total is about 92k.

**revise**
