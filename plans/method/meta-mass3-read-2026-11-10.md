# How the way of working sizes a solution: a read of 15 cases, 2026-11-10

Roman's question: "how can issues be really solved at the appropriate scales. As in how does the workflow avoid limiting the correct solution". This page is a blind read of the records from 2026-10-01 to 2026-11-09. It edits nothing. It did not read `plans/meta-review-2026-11-10.md` or `plans/method/meta-map-2026-11-10.md`, so that their findings do not steer it.

## Result

In 15 cases where the records hold a first solution and a later, different one for the same problem, the first solution was the right size in 0 cases. The selection makes that count close to 0 by its design. The base rate is in other records: 7 of 56 closed frames fixed at the source (observed: `plans/closed-reach-2026-10-26.md` line 9), and 0 of 14 open frames (observed: `plans/agency-prevalence-2026-10-26.md` line 26).

- A session or its agents enlarged the solution with no word from Roman in 3 of 15 cases.
- Roman's words started the enlargement in 12 of 15. In 9 his words were about that problem. In 3 his general ask started an agent read that changed the frame.
- The right solution was a removal, a stop, or "the question is wrong" in 6 of 15. Roman said so in 3, and an agent read said so in 3.

The workflow does not forbid a solution of the right size. It never asks for one. Three things set the size of a first solution, and each is written in the method:

1. **The price table and the guide make a door the norm.** A door text costs 2 cycles, and the guide had only "cheap" or "escalate to me" (observed: `plans/method/reference.md` lines 162 and 504; `plans/wall-guide.md` line 132).
2. **A frame is born from one night's turn and is measured on it.** The site is fixed at the push, the red test is that turn, the ends-when counts the fix's own output, and a recurrence opens a new frame (observed: `plans/method/reference.md` lines 154 and 171; cases 1, 3, 9).
3. **A larger solution has one route, a question to Roman.** Nothing in the loop asks "is this the right size" after a push. Each rule that later asked it, C76, frame 344, C77 and frame 363, was written on his words.

## 1. The cases

Size words: text, door (one check at one place), function, mechanism, design, direction (a change of what is built or tested), removal, stop.

| # | The issue | First solution, size, who, moment | Later solution, size, who | Gap | What the first cost |
|---|---|---|---|---|---|
| 1 | A batch with a quarantined key keeps the one batch seat (frame 330) | One check on the `tests_failing` key, door. The session, from night 168's read and a provenance read, in the pass brief | `stopped_bouncing` reads `given_up`, all 10 keys, function. An agency read that Roman's general ask started | 3 hours | 4 passes, 148k, a review 78k, 2 gates, "Cycles: 9 of 3". Night 169 stalled on `batch_start`, a key the first fix left out |
| 2 | The removal door reads his permission by a fixed phrase (frame 339) | A door built by the session (frame 283, 10-21), a "line N" matcher an implementer added (10-23), a sentence to copy (frame 312, 10-24). Three doors | Removal: the matcher and the sentence go, and the door records a stray for the Architect by law 12. An agency read with no cause | 5 days | Night 169 stopped at walk 1, 28 refusals in 10 of 14 Developer sessions, 0 merges |
| 3 | A span write removes a branch with no note (frame 173) | The offer names the statement, and a `dropped` note is written. Text. The session, from night 127's read | A restore act from the stray rows, with no model. Roman's question of 11-08 10:23 | 26 days | Nights 146 to 154 counted notes, and "the note stopped 0 of 3". Dry run 7 ended on the same removal, 8 commits over 19 sessions |
| 4 | A failing inherited test has no route (frame 114) | A question to Roman with three options, then a door change. The session, at the push | "whats the question here?", then "File writes were always permitted everywhere". Law 12 holds the answer, and two doors contradict it. Roman | 2 and 15 days | The question went 5 times in 3 sessions (observed: frame 287, `plans/archive/stack-2026-10-18.md` line 32) |
| 5 | The merge carries a format he declined twice (frame 243) | A lexical respecify door. A scope read agent | Roman: "there's only so many kind of changes we can make". Then a Fable review: the contest ruling's words go into the Developer and Tester wake, mechanism | 40 minutes | Low. The same fact came back on frames 306 and 337, and on dry run 7 at 0 of 22 Developer pushes |
| 6 | His words on a page land wrong (facts F2 and F3, the seam, frame 345) | Door rules over his words, seam passes 3a to 3f. Each review added a cue list or a negation reader. The session and its reviewers | Roman: "the night is the wrong scale of test", "less doors and more in depth test cases". 24 L3R cases, one word per line, three cue doors out. Direction and removal | About 1 day for the seam, 16 days from frame 213 | Seam "cycles: 13". The baseline of the 24 cases: 71 of 72 runs wrong |
| 7 | A Developer writes rota's `criteria.json` into the project (frame 346) | A refusal `_rota_record`, or a record. Door. The session, as a question | "That's a prompt change to explain that task tracking is part of the harness". Text. Roman | 19 hours | Low. The case went 5 of 5 after the prompt |
| 8 | An item the code already holds has no end (frame 360) | Shape A, a claim proven by tests, the fork as the head. A design page, ruled | The false claim merged on the arm run, tests pass on the old code. Design shapes F and A, then frame 182's base verdict. A later run, then the session | 4 and 7 days | A merge of a request the code did not hold |
| 9 | A batch goes green with the behaviour removed (frame 182) | A read to name "the one site a change would touch". Waits on Roman's order. Never run | The base verdict: each new test runs on the base code, and the encode door reads it. Mechanism. Moved to the front by C77 | 32 days | Nights 131, 132, 136, 138 merged without a test of the change. Dry run 8's W1 and W2 |
| 10 | A backslash is lost between the seat and the door (frame 335, W3, dry5 wall 10, dry6c wall 5) | A warning read as an error, and advice forms, slash form first. Door and text. The session from night 168 | "The brief's premise was wrong". `parse_args` reads the call as written first, and the rewrites run only on failure, 15 lines. A read agent by itself | 11 days | W3's advice wrote a wrong test on night 171. On dry run 5 the note told the seat to double the backslash, and a 289-line file was rewritten |
| 11 | The surface door takes the first index symbol (frame 324) | Candidate R, a resolver for 2 doors, then "option A", then a general build "proposed from the reads and the composition page and not from the code". The session | The ruled partition through one reader at about 13 places, "where the seat gets its information". Roman: "the initial fix was so narrow minded" | 1 day | 2 of 13 places covered. A general proposal wrong on its premise |
| 12 | The first account page is too large for one Liaison reply (frames 361, 362) | A size bound that sends a large baseline to the ledger. Door. The session, from dry3's read | The lazy election that exists already, then a demand-first design "designed both ways". Roman's questions, and a design review | 1 day | 235 notes he was asked to approve. 153 of 206 sessions on dry3 were onboarding |
| 13 | The Critic gives no verdict on a two-case criterion (F37) | A cap of 2 added lines per criterion. A review of 845e0b80, 2026-10-07 | A word list (a review found it misses 10 of 12), then a rule on statement shape. A later night, a review, the session | 20 days | Night 171 walk 1: no verdict in 3 sessions |
| 14 | Closed frames fix one door of N (the method) | The guide's cheap fix per door as the norm (frame 251, 10-15) | C76's reach line (10-26), the audit of frame 344 (10-27), "less doors" (10-28), C77 (11-08), frame 363 (11-10). Each step on Roman's words | 26 days | About 520 to 540 cycles against about 240 to 270 at the source, before later frames |
| 15 | A session does not find what the records hold (frame 287) | A `Law:` line on every frame, a door on a push with no law line. Texts and a door. The session | "you are not rota", "you can design your context". The state print and the method pages by moment. Roman | 9 hours | Two design reviews: "does not stand", 10 high. On 11-10 frame 363 names the same gap again |

Sources, by row:

1. `plans/archive/stack-2026-11-02.md` lines 3 to 29 and 36 to 38.
2. `plans/archive/stack-2026-10-28.md` lines 22 to 36.
3. `plans/stack.md` lines 3222 to 3251 and 1929.
4. `plans/stack.md` lines 3589 to 3614.
5. `plans/stack.md` lines 2737 to 2749.
6. `plans/archive/stack-2026-10-30.md` lines 19 to 30 and 370 to 383. `plans/closed-reach-2026-10-26.md` line 13.
7. `plans/archive/stack-2026-10-30.md` lines 3 to 17.
8. `plans/stack.md` lines 1991 to 2065.
9. `plans/stack.md` lines 3144 to 3165.
10. `plans/archive/stack-2026-10-30.md` lines 442 to 458. `plans/dry6c-wall5-backslash-read-2026-11-06.md` lines 3 to 12. `plans/stack.md` lines 1855 and 1858.
11. `plans/archive/stack-2026-10-29.md`, the block of frame 324, statuses of 2026-10-26 20:21 and 20:37.
12. `plans/stack.md` lines 1962 to 1990 and 1712 to 1724.
13. `plans/archive/stack-2026-10-30.md` lines 194 to 199. `plans/stack.md` line 5304.
14. `plans/closed-reach-2026-10-26.md`. `plans/wall-guide.md` lines 128 to 133. `plans/archive/stack-2026-10-30.md` lines 164 to 175.
15. `plans/archive/stack-2026-10-18.md` lines 18 to 45.

## 2. What shaped the first solution

### 2.1 The price and the guide (observed)

- C42: "A door text or a number is 2 cycles, an instrument fix 3, a seam design with its night 8 to 10" (observed: `plans/method/reference.md` line 162). Roman ruled the anchors on 2026-10-11.
- C34 and the guide: "For now there is only cheap and escalate to me" (observed: `plans/method/reference.md` line 504; `plans/wall-guide.md` line 33). That ruling is also his, of 2026-10-15. The guide's "Cheap fix" line priced one place, and "Until 2026-10-26 this guide made that price the norm" (observed: `plans/wall-guide.md` line 132).
- The frames' price lines quote that table. Frame 339: "a door text or a number is 2 cycles". Frame 335: "two doors and one note text". Frame 330: "1 read ... then 2 build". The actuals ran over and did not change the size: frame 330 "Cycles: 9 of 3", frame 335 "7 of 3" (observed: case rows 1 and 10).

### 2.2 The frame's shape: one night, one site, its own measure (observed)

- C41: "Every frame's first line names its site as a fixed field" (observed: `plans/method/reference.md` line 154). The site is written at the push, before any reach is counted. Frame 330's site named three functions at 18:10, and its reach line of "1 of 10" came only after the agency read at 21:13.
- C31: the ratio has "a baseline from the night that found the wall", and the residue rule says "the frame closes when its cause is not the cause the frame named. That cause is a new frame" (observed: `plans/method/reference.md` lines 166 to 172). A recurrence then becomes a new frame. 45 of 48 one-door frames have a later frame at the same fact (observed: `plans/closed-reach-2026-10-26.md` line 15).
- The ends-when often counts the fix's own output. Frame 173 closed on notes "in at least 9 in 10", and the night showed "the note stopped 0 of 3" (observed: `plans/stack.md` lines 3226 and 3246). Frame 182 asks for "the one site a change would touch" (observed: `plans/stack.md` line 3148).
- The pass brief carries the night's case. Frame 330's pass 1 brief: "one check, ... true at loop_cap or on a quarantined tests_failing key". Its gate then showed 20 more reds, and "the pass 2 brief named only the two [scenes] the implementer saw" (observed: `plans/archive/stack-2026-11-02.md` lines 16 and 21).

### 2.3 A larger solution goes through Roman (observed and reasoned)

- Every rule that asks about the size came from his words: C76 on 2026-10-26, frame 344 on 10-27, "less doors" on 10-28, C77 on 11-08, frame 363 on 11-10 (observed: `plans/method/reference.md` lines 446 to 556; `plans/stack.md` line 1704).
- Before C76, a question was the route for anything that was not cheap. Frame 182 sat on "Waits on: Roman's order" for a month. The long term plan counts 41 such lines (observed: `plans/stack.md` lines 3149 and 114).
- After C76, the session still enlarged from the records and not from the code. Frame 324: "proposed from the reads and the composition page and not from the code, and it was wrong on its premise" (observed: case row 11).
- (reasoned) The workflow sends a solution up to Roman by a question, and it has no moment that sends a solution back to be enlarged. In 12 of 15 cases, a word of his was that moment.

### 2.4 Weaker shapers (observed)

- Reviews check a diff against numbered points, and they add rules at the door. F37's cap "came from the review of 845e0b80". Seam review p5 found "_REPORT_DENIALS is a third negation reader" (observed: `plans/archive/stack-2026-10-30.md` lines 194 and 377). A review asked about scale only once in these cases: the design review of frame 362 found that the lazy election exists.
- Implementers add mechanism that no one asked for. Frame 339's "'line N' matcher came at 2acc7b5c on 2026-10-23 in pass 2 with no brief, status line or review that asked for it" (observed: `plans/archive/stack-2026-10-28.md` line 33).
- Older frames with the right shape are not found. The read of frame 360 says "No open or parked frame covers it", while frame 182 held the base-run shape from 10-08 (observed: `plans/stack.md` lines 1993 and 3144). Frame 155 of 10-06 names the quote fault that dry6c's wall 5 found in `_quote_bare_keywords` (observed: `plans/stack.md` line 3391). Eleven frames were parked on 2026-10-21 "for the economy", frame 173 among them (observed: `plans/stack.md` line 3248).
- The handover did not change a solution's size in any case read here (observed: the 15 rows). A frame's head lines carry the size across sessions unchanged.

## 3. The counts of step 4

| Count | Cases | Number |
|---|---|---|
| The first solution was the right size | none | 0 of 15, by selection |
| A session or its agent enlarged it with no word from Roman | 8 (the session's false-claim design), 10 (the read agent), 13 (a night, a review, the session) | 3 |
| Roman's word on that problem enlarged or changed it | 3, 4, 5, 6, 7, 11, 12, 14, 15 | 9 |
| Roman's general ask started the agent read that changed it | 1, 2, 9 | 3 |
| The right solution was a removal, a stop or "the question is wrong" | 2 (agent), 4 (Roman), 6 (Roman), 7 (Roman), 10 (agent), 12 (agent review) | 6 |

In case 6 the session ran the removal itself after his direction. The door-off experiment changed 0 of 24 right cases (observed: `plans/archive/stack-2026-10-30.md` line 36). In case 7 the session offered two options, and he chose a third, smaller kind.

## 4. The opposite: a solution at the right scale

- **Dry run 6c, wall 5, the strongest counter-case.** A read agent with a brief whose premise was wrong said so: "The brief's picture of wall 5 is wrong in three parts". It found two parser rewrites at fault and a verbatim form that no prompt names (observed: `plans/dry6c-wall5-backslash-read-2026-11-06.md` lines 5 to 12). The fix ran the parser on the call as written first. It counted its reach over 358,805 recorded calls in 81 databases, and 78 calls changed (observed: `plans/stack.md` line 1858). No word of Roman's came before it.
- **The fourteen agency reads of 2026-10-26.** The briefs "name no cause and no site". The agents found 12 of 14 frames at one door and 2 on a wrong premise. They proposed the removal for frame 339 and `given_up` for frame 330 (observed: `plans/agency-prevalence-2026-10-26.md` lines 3 and 26).
- **The F6 probe of 2026-10-27.** An agent read 12 rules over 82 functions and four nights and found the same criterion for all 85 tests. The right move was no fix (observed: `plans/archive/stack-2026-10-30.md` line 206).
- **Frame 243's brief loop.** The session replayed eight brief lines at temperature 0, found that no line moved both seats, and put no brief line into the pass (observed: `plans/stack.md` line 2751).
- **The session's statement of 2026-10-28 14:30.** The session stated the problem "from the start" and corrected his reading: "57 of 68 refusals on night 174 were fact doors and right" (observed: `plans/archive/stack-2026-10-30.md` lines 378 and 379).

What was different (reasoned, from these five):

1. The brief asked for the whole: the purpose, every reader, or every recorded call. It did not name a site or a cause.
2. The evidence spanned many nights, runs or all readers in the code, not the one turn that found the wall.
3. The measure was at the seat's own scale: a replay, recorded calls, or the L3R cases. It was not a night's ratio.
4. The agent could say that the premise was wrong, and the session acted on that.

These features are now in C76 step 3 and C77. Cases 8 to 13 after 2026-10-26 show the rule in place and a first solution still at the door. So the rule is written and does not yet fire at the push (reasoned: rows 8, 11, 12, 13).

## 5. What this read could not see

- The pass briefs and read briefs live in session scratchpads, for example `f330_pass1_brief.md`. This read saw only their summaries in status lines.
- Roman's words are seen only where a status line quotes them. His reasons between quotes, and the terminal threads, were not read. No transcript was read.
- The selection takes cases with two solutions. It cannot give the rate of first solutions that were right. The base rates in section 1 come from other reads.
- Several "later" solutions are not proven. Frames 173, 182 and 114 are open on 2026-11-10. The later solution can be the next door.
- The count of "his word" is a reading of each block. A session can propose a change that he then rules, and the block can credit either one.

## 6. What a reader inside the workflow cannot see about itself

- A session sees a problem through its frame: one site, one red test, one night's ratio. The other readers of the same fact are not on the frame until a read counts them.
- The stack is 1.3 MB and is never read whole. A match by symptom does not find an older frame with the same cause and a different heading (cases 8, 9 and 10).
- The price table makes a door the cheap move, and the overrun does not reach the next price. "9 of 3" is written and does not change the size of the next fix.
- Reviews and implementers refine the solution they are given. Nothing in a review brief asks whether the solution is the wrong kind.
- The session cannot see its own anchor on the last night or run. Each read gives the next sprint, and the sprint is a list of walls.
- The rules that ask about size are written on Roman's words. The session cannot tell, from inside, whether it would have asked without him. The records show it rarely did (3 of 15).
