# Frame 363: the review of the moment design, 2026-11-10

A review of `plans/f363-moment-read-2026-11-10.md`, on the points of the
session's brief. It edits nothing but this page. Marks: CONFIRMED means
checked in a file at the line given. PLAUSIBLE means reasoned and not
checked. Severity: high, medium, low.

## Result

Verdict: build with fixes. Design A is at the right place, and design B
names functions and lines that exist. The Next test is not a test yet. By
its first clause, Next reads build after dry runs 5, 7 and 8, and it reads
build after every run until the first merge. No clause says when the build
is done and the next run is due, because the moment fires only at a read.
The first use at the stack's head shows the hidden judgement: it writes
"Next: build" and a measure, frame 364, in the same bullet.

Findings: 16. CONFIRMED 14, PLAUSIBLE 2. High 2, medium 9, low 5.

The three fixes that matter most:

1. Define "repeats" by counts, not prose, and add the exit to measure.
   Measure when every build row of the Order is closed, and name the fact
   that the run is for (F6, F7, F18).
2. Mark the amendment (reasoned), under his word of 00:32, and write a
   wall in the Model line only after C36's interview (F5, F9).
3. Make the head reader exact. Take the first `## ` section by position
   that holds `- Destination:`, and parse only `frame <n>` in the Order
   bullet. Delete the second copy of the order in the same section (F12,
   F13, F15).

## 1. The amendment against the other rules

- **F1. C46 of section 4: the sprint boundary is where Roman rules a
  placement.** CONFIRMED, medium. `plans/method/reference.md` 184 to 185:
  "The placement is (reasoned) until Roman rules it at the sprint
  boundary." The amendment puts a sprint end at every run's read. So
  either Roman rules at every run, which spends his attention, or the rule
  goes silent. The Sprint lines "this sprint" and "next sprint, rank <k>"
  (178 to 183) also change their meaning at each run.
  Fix: add one clause to the amendment: "The Order bullet stands
  (reasoned), and Roman re-orders it when he chooses, by C48."
- **F2. C48 names "the next night's wall".** CONFIRMED, low. Reference 419
  to 420: "send one notification that names it and the next night's wall,
  and start row 1 at once". The design says "C48 stays as it is". With
  Next build, no night follows.
  Fix: in C48, write "the Next line" for "the next night's wall".
- **F3. C77 moves frames itself.** CONFIRMED, low. Reference 532 to 533:
  "the old frame moves to the front with the new count". The dry run 8
  read moves four frames in its section 4: "By C77, 171, 172, 155 and 166
  move to the front". So "before any frame moves" in the amendment cannot
  hold.
  Fix: write "after C77's reasoning and its moves, and before the next
  build or run starts".
- **F4. The amendment cites C55 without its second half.** CONFIRMED,
  medium. Reference 385 to 386: a night stops when "its loop is a known
  open frame's wall and the held frame gets no new data from it". The
  amendment keeps the first half only: "Build when the walls the next run
  meets first are open frames not built, as C55 stops a night." Dry run 8
  met known walls and still gave new data: the criteria followed the
  correction, 3 of 3, and his words reached 3 of 3 wakes, from 0 of 22
  (`plans/dry8-read-2026-11-08.md`, Result 1).
  Fix: add "and the run can show no fact that a probe cannot show".
- **F5. The first use breaks C36.** CONFIRMED, medium. Reference 511 to
  514: "escalated only after the interview shows it on more than one
  sample". The Model bullet at `plans/stack.md` 57 to 60 writes "Model:
  one" for `L1-TS-the-run-shows-a-split-word`. Its source,
  `plans/method/handoff-13b7eef8.md` 29 to 30, says "a known red at 0 of
  5" and names no interview and no stronger model.
  Fix: move the case to "not interviewed" until the C33 replay and a
  stronger model run on that turn.
- C76 and C47: no clash found. C47 is keyed to a night (reference 411),
  the same small gap as F2.

## 2. The build-or-measure test by hand

| Run | Result | Destination repeats | Clause 2 decidable from the read | Next |
|---|---|---|---|---|
| 5 | No merge, stop on `touch_mistaken` after turn 9 (dry5 read, Result) | yes | partly: 5 of 14 walls say "the same as dry run 4", and no frame state is read | build |
| 7 | No batch merged, stop on `touch_mistaken` in turn 7 (dry7 read, Result) | yes | no: "The state of each older frame is not read" (dry7 read, section 4) | build |
| 8 | No merge, stop on a wrong test (dry8 read, Result 3) | yes | yes: section 4 names 4 front frames not built | build |

- **F6. The test is degenerate and has no exit.** CONFIRMED, high. Clause
  1 alone gives build at all three runs. The Destination line changes only
  after a run, and a run starts only on measure. So by the text, Next
  reads build until a merge, and nothing writes measure. The moment fires
  at a read only, so no rule fires after the build either. The first use
  shows the gap: `plans/stack.md` 55 to 58 write "Next: build" and "The
  one measure beside the build is frame 364".
  Fix: "Next reads build while a build row of the Order is open. It reads
  measure when every build row is closed. Name the count that the run is
  for."
- **F7. "Repeats" needs judgement on prose.** CONFIRMED, medium. Dry runs 7
  and 8 both merged nothing, and the dry run 8 read says they failed for
  different reasons: "Dry run 7 failed because the team worked on the
  wrong thing. Dry run 8 failed because the team worked on the right
  thing against a wrong check" (dry8 read, section 5). A prose comparison
  can call these one line or two lines.
  Fix: the Destination line carries three counts: merges on the
  destination request, the step of the long term plan, and the walls that
  match unbuilt frames. "Repeats" means all three are equal.

## 3. The Model line and cause 5

- **F8. Cause 5 exists with that meaning, and records of walls placed
  there exist.** CONFIRMED, medium. `plans/wall-guide.md` 324: "Cause 5.
  The seat has the fact, reads it, and judges wrong". Its ruling at 330 to
  335 is C36's. Placements: frame 201's interview, qwen3:8b on the Critic
  case 5 of 5 runs and 3 of 3 replays, "where qwen3:30b-a3b gets it
  right" (`plans/stack.md` 5304). Night 162's s305 places b_3's wall under
  cause 5 (stack 5267). The guide lists frames 200, 236 and 133 (377). No
  read of dry runs 4 to 8 places a wall under cause 5 (grep). Frame 201
  meets both conditions of C36. So the meta review's "No record says the
  8B stops here" (`plans/meta-review-2026-11-10.md` 60) is contradicted.
  Fix: the Model line writes the run's cause 5 walls, and "none placed, n
  interviews" when none, so that "none" and "not interviewed" differ.
  Seed it with frame 201's case.

## 4. The marks

- **F9. The mark is (reasoned), not (ruled).** CONFIRMED, medium.
  `plans/composition.md` 111 to 113: every conclusion carries a mark,
  "(ruled: a ruling and a judgement looked the same in prose)". His words
  give the session the redirect. They do not give the text of C46. The
  meta review says "The order is the session's under that word" (66 to
  67). Frame 364's Sprint line marks the same kind of act "(assumed: his
  word of 2026-11-10 00:32 covers ...)" (stack 1694).
  Fix: write "(reasoned: frame 363, under Roman's word of 2026-11-10
  00:32, "I want you to take charge of redirecting the project")".
  The amendment also departs from his ruled text of 2026-10-12 23:40.
  Reference 493 to 498 says such a departure "is still asked", with the
  ruling and its date first. PLAUSIBLE that his word of 00:32 covers it.
  Name the departure in C48's one notification, and block on nothing.
- The cite "(ruled: Roman, 2026-10-18 02:25)" holds: `plans/method/design.md`
  88 and `rota/tools/state.py` 360 carry 02:25. CLAUDE.md carries 02:20
  for the same session. No fix in this frame.

## 5. Design B against the code

- Names and lines hold (CONFIRMED by read, the suite not run):
  `Frame.sprint` at 135, `cut` at 51, `FIELD_LIMIT` at 46, `render` at
  334, the live count at 357 and 358, `render_since` at 509. The economy
  line is at 362, not 360. The test file holds 36 tests. The assertions at
  123, 134, 303 and 320 match a substring, and line 125 checks the last
  line only. So two lines added after "Live things" and before "## Open
  decisions" keep them green. Line 390 is on `--since`, which the change
  does not touch. The fixture `STACK` (line 19) has no section before
  `## Stack`.
- **F12. "The newest section" is not defined.** CONFIRMED, medium. 33 `##`
  sections stand between the title and `## Stack` (`plans/stack.md` 17 to
  1505). The file order is not the date order: Sprint 27 of 2026-10-27
  13:37 at line 359 stands above Sprints 28 to 31 at 386. The Sprint 26
  heading at 414 holds two dates. The long term plan at 69 is a `##`
  section that is not an order. A reader of the first section breaks when
  a non-order section goes on top, as the long term plan did on
  2026-10-31. The older Sprint sections have no bullets. So a reader that
  looks for the bullet falls through them to the sentence, which is safe.
  Fix: take the first `## ` section by position above `## Stack` that
  holds `- Destination:`, and print its heading.
- **F13. The Order bullet's numbers are not all frames.** CONFIRMED,
  medium. Stack 53 to 54: "364 (capability 9), 182 and 171 (6, D3), 183
  (1, A1) and 114 (2, A7), 173 (2, A7), then dry run 9". A digit parse
  reads 9, 6, 3, 1, 2, 7 and 9 as frames. `state.open_frames` holds frames
  1, 2 and 4, so a filter on open frames still reads frames 1 and 2.
  Fix: write "frame 364" in the bullet, and parse `frame (\d+)` only.
- **F14. The example count is wrong and counts unheld frames.** CONFIRMED,
  low. Design line 159 prints "4 of 6 name no capability". Frames 182, 171,
  183, 114 and 173 carry no Sprint line (a parse by `state.parse`), so the
  count is 5 of 6. The text says "one count over the held frames", and
  these five are not held.
  Fix: say that the Order count reads every frame the bullet names, held
  or not.
- **F17. The capability match counts a denial.** CONFIRMED, low. Frame
  363's Sprint line says "no single capability" and counts (the design's
  own doubt). Fix: match "capability <n>" or an exact name of
  `rota/COMPLETION.md`.

## 6. Over fitting, reminders and writers

- **F15. The order has two records in one section, and a third on the
  frames.** CONFIRMED, medium. The redirect section holds the numbered
  order at stack 30 to 41 and the Order bullet at 53 to 54. Each frame's
  Sprint line carries a rank (C46, reference 181 to 183). One writer holds
  all three, but they can disagree, which is cause 12 of the wall guide.
  Fix: the Order bullet is the order. Cut the numbered list to its
  reasons, or point it at the bullet.
- **F16. Two parts fit the last two weeks.** PLAUSIBLE, low. "none: every
  wall is wiring" uses the word of rota's current thesis, and a project
  with no wiring cannot write it. Clause 1 fits a streak of runs that
  merge nothing on one sentence.
  Fix: write "none: no wall placed under cause 5".
- No reminder is added. No line goes to CLAUDE.md, a memory or a hook,
  and the print reads a record that exists (design 104 to 107).

## 7. What the design misses

- **F18. The holder cannot see how far the build is against the Order.**
  PLAUSIBLE, high. After a run, the print shows Next and the Destination.
  It does not show which build rows of the Order closed since the four
  lines were written. So the holder cannot see when the next run is due,
  which is the exit of F6. The Destination line also carries no count of
  the gate's red floor and no count of his pages per run. The meta review
  names both as signs of the turn (85 to 89).
  Fix: the print adds "Order: k of n build rows closed" from
  `open_frames`, and the Destination line carries the gate's reds and his
  pages.

## Notes

- The finding numbers skip F10 and F11. F10 became the note on 02:25 in
  section 4, and F11 became the list of names that hold in section 5.
- The stack lines of the design moved after the first use. The long term
  plan is at 69, not 51, so the design's references to the stack are
  older by 18 lines.
- Not done: the test suite was not run. The reads of dry runs 4, 6b and
  6c were not opened.
