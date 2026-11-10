# Frame 363: the gather on acting on a spotted issue, 2026-11-10

A gather from what exists, read-only, for Roman's question of 2026-11-10:
"what about the ability to act well on issues spotted? Spotting problems
and doing the best thing about it". The base is
`plans/meta-review-2026-11-10.md`.

## Result

Of 10 traced doubts, 3 were acted on, 3 were acted on late and 4 were
lost (section C). Every doubt that was acted on in time was fixed by the
session that wrote it, inside the same frame, on the same day. Every lost
doubt crossed a session boundary or was relabelled "for Roman". The
method counts walls, reaches and placed frames. It never counts a doubt,
and no record discharges one. Rota itself holds the missing pattern: the
ledger row, `outstanding()` and the composition line "Nothing stops
quietly". The smallest design moves that pattern onto the frame as one
field line, `Owed:`, that `state` counts (section E).

## A. What the meta workflow holds for the path from issue to act

| Item | File and line | What it does | Counts open or discharged? |
|---|---|---|---|
| C76 | `plans/method/reference.md` 448-493 | Read before fix, seven steps. Step 7 closes on two counts or writes a residue line. The reach line is printed by `state` (`rota/tools/state.py` 222-247). No refusal, by Roman's "No don't make it a hard rule" | Walls only. A residue line has no discharge |
| C77 | reference.md 538-555 | A run's walls are reasoned over together. A wall that matches an unbuilt frame moves that frame to the front "with the new count" | Counts matches to unbuilt frames, at a run's read only |
| C36 | reference.md 533-536 | "Judged against" is escalated only after an interview on more than one sample | The only path to "the model stops here". C46's Model bullet (422) reads "none placed" |
| C30 | reference.md 124-135 | The grill quantises work into frames | Every response becomes a frame |
| C46 | reference.md 178-192, 406-438 | A push is a placement. At a run's read, Destination counts "the walls that match frames placed and not built" | Counts unbuilt frames, not doubts |
| C55, C56 | reference.md 385-399 | Stop a night that measures nothing | The one written "stop" response, scoped to nights |
| C34 | reference.md 499-507 | "Every wall a read names is fixed", and an unfixed wall "stays an open frame with its reason written" | Every response is a fix or a frame |
| [Assumed] | reference.md 362-365 | A decision for Roman carries "(assumed: why)" | `state --since` lists them (state.py 404, 530). 29 marks in the stack. Nothing discharges one |
| Section 11 | reference.md 557-635 | C57 escalates "a wall survives three cycles". [Autonomy] decides under a stated assumption | A question blocks a frame. A doubt is not a question |
| Intent | `plans/method/intent.md` 33-35, 96 | "Fixes must outpace new walls, and the biggest issue comes first". He refuses a fix that fits one case | States the goal. No mechanism |
| Design | `plans/method/design.md` 53-69, 85-92, 101, 111-117 | The state page prints "the leaving session's doubts". The taker asks about doubts "as an option and not a step". "No ledger". Tools enable and never gate | Prints doubts. Never counts them |
| Note form | `plans/method/handoff-13b7eef8.md` 123-159, `handoff-0ff6bcd7.md` 133-161 | Two sections: "Open and not built" and "What I believe, and what to doubt" | Four items of 0ff6bcd7's "Open and not built" repeat in 13b7eef8 a day later. Nothing marks one done |
| `state --from` | state.py 44, 318-331, 380-393 | Prints the note's doubts section verbatim | No. Text only |
| `state --since` | state.py 509-565 | Closed, decided under assumption, waits, rulings | Lists assumptions. No discharge state |

The reach line exists since 2026-10-26. The stack holds 7 `- Reach:`
lines in 15 days (observed: grep). A printed field that is optional is
written rarely.

## B. What rota holds for the same problem

| Pattern | File and line | What it makes visible | What discharges it |
|---|---|---|---|
| Ledger | `rota/core/schema.sql` 772-787 | An assumption (`default_taken`), with `kind` and `author`, status open, resolved or parked | A `decisions` row with `resolves_ledger`, written by the principal (`rota/roles/principal.py` 4005-4013, 4510-4516), or a merge with its reason in words (`rota/core/lifecycle.py` 248-253) |
| `outstanding()` | `rota/core/predicates.py` 2505-2582 | Every register entry as one fold, with a count, owners and refs | Only the state. "A wake-suppression is not a discharge" (2560) |
| "Nothing stops quietly" | `plans/composition.md` 50-51 | "Every open obligation stays visible and countable until something discharges it" | Something named. Silence never (composition 75-76) |
| Critic and challenge | predicates.py 2466-2472, `rota/core/scheduler.py` 1540-1555 | One Critic session owed per unchallenged load-bearing claim | A `challenges` row. "A break is a citation, or it is refused" |
| `Stuck` | `rota/core/loop.py` 66-85 | A predicate that fires again after a session changed nothing | Reported, not spun on. "Stuck and idle look identical in a log" |
| Quarantine | scheduler.py 3380-3390, predicates.py 2139-2165 | A wake past its cap. "Abandonment is visible, not silent" | The Liaison tells the principal what stalled |
| Escalation climbs | `rota/LAWS.md` 183-194 | A question nobody answers climbs (`unresolved`) | An answer. "It is never silence" |

Two points carry over. A discharge is a record with a writer, never an
absence. And a discharge can be a refutation: the Critic's "break" and
the ledger's "parked" close an obligation without a fix.

## C. Evidence: 10 doubts from 2026-10-29 to 2026-11-09

| # | The doubt | Where written | What happened | Verdict |
|---|---|---|---|---|
| 1 | Constraint zero quarantined, "reasoned, not replayed" | `plans/dry1-first-wall-read-2026-10-31.md` 6 | Fixed the same day, e7016e65, 2026-10-31 17:27 | Acted, 0 days |
| 2 | A false add: the nine cases need `act: null` before the measure | `plans/r-wrong-cases-read-2026-10-29.md` 190-197 | dba54e57, 2026-10-29 23:01. 189 `act: null` rows in `tests/rota/cases/l3_rulings.yaml` | Acted, 0 days |
| 3 | Run T "has not run", one run of each is needed first | `plans/dry4-read-2026-11-03.md` 9 | The probe ran at 04:08 the same day (stack 1737) and showed the approximation fails. Run T was not run, with the reason in `handoff-07f209e6.md` 13 | Acted, 0 days, a stop |
| 4 | m40 "Reply 'ok' to go ahead" reads as a gate. "The reader did not read it further" | `plans/dry3-wall1-read-2026-11-02.md` 137 | Recurred in arm run 1 (`plans/arm-run1-merge-read-2026-11-06.md` 74). Fixed 2026-11-06 (`principal.py` 349-353) | Late, 4 days, after a repeat |
| 5 | "The criteria themselves are doubtful: c3 ... breaks the 75-octet rule. I did not follow that cause" | arm-run1 read 170 | Dry run 8 walled on it: "no record judges the test" (`plans/dry8-read-2026-11-08.md` 33, 143). Frames 182 and 171 to the front 2026-11-09 23:41 (stack 1951) | Late, 3 days, as the biggest wall |
| 6 | The base verdict of tst_c1 v2 "is reasoned from its body, not run" | dry8 read 158 | Repeated in `handoff-13b7eef8.md` 149-152. Run 2026-11-10 00:49 after the meta review (stack 1956) | Late, 2 days |
| 7 | The role-to-model map of dry run 7 "was not read. Check it before any count is compared" | dry8 read 157 | `handoff-13b7eef8.md` 125-130: "Not a decision for the session; a fact for Roman's reading". No frame | Lost, relabelled to Roman |
| 8 | Four pause gaps. Biggest: "`rota run` does not run the recovery that `boot` holds", reach 4 of 7 | `plans/pause-read-2026-11-06.md` 81-84, on Roman's own ask | Listed as next in `handoff-1b9e813c.md` 26. No commit since touches it (git log) | Lost, 4 days |
| 9 | "`criteria.specify` stamps '' on any wake that is not `tick:criteria`" and three more | `handoff-0ff6bcd7.md` 133-148 | Copied into `handoff-13b7eef8.md` 141-145 under "Open and not built" | Lost, carried |
| 10 | "The measure of 0 of 5 rests on one case, one model and one wording" | `handoff-0ff6bcd7.md` 155 | `handoff-13b7eef8.md` 134-137: "A wording pass could try once more; a different model is Roman's call". No placement under cause 5 | Lost, carried |

Counts: 3 acted, 3 late, 4 lost. Two more doubts outside the ten are lost
too: the second probe input of dry8 read 159, and W12 and W18 of
`plans/walls-root-read-2026-11-08.md` 135, which no later page names.

The pattern: the acted three were cheap and inside the writer's frame.
The late three were acted on only after the doubt came back as a wall.
The lost four crossed a hand-off or were relabelled "for Roman" or
"Roman's call". Cases 7 and 10 show failure mode (4) of the meta review.
The doubt pointed at "the model stops here", and nobody wrote it.

## D. Roman's words

- "fuck like the initial fix was so narrow minded" (transcript ac089aa1,
  2026-10-26 20:33 UTC).
- "ok but that also sounds narrow, that cant be a law or rule for the
  future" (transcript 8db3a3f9, 2026-10-26 20:52 UTC).
- "we need critical thinking and context retreival to solve problems /
  because i was shocked at the poor quality of the solution that was
  proposed" (memory `rota-read-before-fix.md` 13).
- "No don't make it a hard rule, the model should be smart enough to do
  it" (transcript 8db3a3f9, 2026-10-26 23:11 UTC; stack 492).
- "Go back and review them to make sure that we have applied area root
  cause fix" (transcript c66eae69, 2026-10-27 14:08 UTC).
- "Do we keep having the same issues? Did we do a root cause analysis for
  the issues?" (transcript 161c371b, 2026-10-29 01:51 UTC).
- "we are finding more walls, are we doing proper root cause analysis?"
  and "The root cause is part of the workflow, is it not?" (stack 1929,
  2026-11-08 10:25).
- "I want to prevent over fitting. All I'm saying is that when we hit
  walls the solutions can range from simple to complex but theres only so
  many kind of changes we can make" (`plans/frame287-roman-words.md` 506,
  2026-10-15 01:54).
- "to suplement reasoning not overtake it", "as long as its enabling not
  inhibiting" (2026-10-18 02:20, T bf5baa63, via `CLAUDE.md`).
- "a million and one "reminders" and not one unified context
  environment" (2026-10-18 02:06, T bf5baa63, via `CLAUDE.md`).

His words ask for three things: a response at the right scale, a root
before a fix, and no new rule or reminder that does the thinking.

## E. The smallest design

**One field line on the frame, counted by `state`.** A doubt or an issue
that a read, a review or a note writes becomes one line at the frame it
bears on, in the form of the reach line:

```
- Owed: <the issue, one sentence>. Scale: case | class | design | direction.
  Act: fix | remove | stop | model stops here | question wrong | frame <n>.
  Rejected: <the other act considered, and why>.
```

A later status line with `Discharged: <first words of the Owed line>, by
<commit | run | ruling | drop, with the reason>` closes it. `state` prints
each frame's open Owed lines with their age in days. `state --from`
marks each doubt of a note as owed at a frame or as owned by no frame.
`state --since` lists the frames that closed with an open Owed line. The
Destination bullet of C46 gains a fourth count: the Owed lines open for
more than one run.

What each part builds on:

1. The line form: C67's frame fields and the `- Reach:` parser,
   state.py 222-247.
2. The discharge as a record with a writer: the ledger's
   `resolves_ledger` and the composition's "Nothing stops quietly".
3. The "drop, with the reason" discharge: the ledger's `parked` and the
   Critic's "a break is a citation".
4. The age and the count: `outstanding()` and `Stuck`. A doubt that
   survives a run is the build's `Stuck`.
5. The Act list: C55's stop, C36's model placement, and C76's step 4
   match against unbuilt frames. It names five acts that the method
   holds in scattered places, and it puts them beside the frame push.
6. The Scale field: Roman's "the solutions can range from simple to
   complex", and C77's reasoning over a run's walls, which picks it.
7. No refusal: Roman's "No don't make it a hard rule", and design.md
   85-92.

The owner is the holder of the frame. The line moves with the frame at a
hand-off, so a taker inherits it from the stack and not from a note.
A doubt about a frame that no session holds goes on the frame of the read
that wrote it.

**The cost.** The `state` change for Owed, Discharged, the age and the
three prints is an instrument fix, 3 cycles by C42. The rule text in
reference.md section 10 and the note form in section 12 are a door text,
2 cycles. A back-fill of the open doubts of the last two notes and of the
dry8 read is 1 cycle on one agent. The total is about 6 cycles.

**The generalisation test.** The line uses no rota concept. A project
that adopts the method has a stack of frames, a state print and a hand-off
note, so the same line fits. The Scale and Act fields are general:
"model stops here" reads as "the tool's limit" in another project. The
design is also the composition's own law, applied to the build. The
build session is a second instance of the same composition (ruled: C),
so the law should hold in both. The test holds, with one condition: a
project with no `state` tool reads the count by grep.

**Two alternatives rejected.**

1. A doubts page or a doubts table beside the stack. It is a new page and
   a second record that can disagree with the frames. Design.md 101
   rejected a ledger for the method ("No ledger"), and LAWS.md 192-194
   says "a stored rung is a second record that can disagree". Roman
   refused "a million and one reminders".
2. A refusal: `status` or `handover.py` refuses a close or a hand-off
   while an Owed line is open. Roman ruled against it ("No don't make it
   a hard rule"), and frame 340 built two refusals and took them out
   (reference.md 486-490).

**Doubts.**

- A count is not an act. The reach line is printed and was written 7
  times in 15 days. The meta review's reading 4 says "Rules exist and do
  not fire". The Owed count can be ignored the same way. The Destination
  bullet is the one place where a session must write a number at every
  run, and that is why the count goes there.
- The Scale field can be filled as "case" every time, which hides failure
  mode (2) in a field. Only C77's reasoning can check it.
- The ten cases come from a grep on marked words. A doubt written without
  those words is not in the sample, and the counts can be biased toward
  doubts that were noticed.
- The age in days may not be the right clock. A run may be the better
  unit, because the late cases came back at the next run.
