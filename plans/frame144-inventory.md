# Frame 144: what each test tier sees, and where the walls of nights 113 to 122 fall

Meta workflow. A read-only inventory for Roman's question of 2026-10-05: which test categories would save night hours, and should the register or the suite have caught the walls. No model ran, and no gate ran. The read is by one agent on Opus, 2026-10-05 09:54.

## 1. The inventory

The suite holds 2,057 test functions in 105 modules of `tests/rota/` (observed: `grep -c "def test_"`, 2026-10-05). The model tiers hold 139 cases in 24 YAML files: 118 L1, 5 ACT, 5 L2, 6 L3, 5 G1 (observed: `tests/rota/cases/`, 2026-10-05).

| Tier, as the repo names it | Runs | Cost | Sees | Cannot see, by construction | Origin |
|---|---|---|---|---|---|
| T0 plumbing, sandbox, parser (`test_t0_*`, 177 tests) | no model | seconds | a door's answer to a call that a person wrote | a call nobody thought to write | designed, `rota/TESTS.md` section 6 |
| Runner contract (`test_runner.py`, 117) | scripted backend | seconds | the wake, the cut, the notes, on small inputs | a wake at night size, real cut events | designed, then grew per wall |
| Desk guards (`test_desk_guards.py`, 260) | no model | seconds | one recorded night call per wall, refused or admitted | the next call in the same class | grew, one test per wall since 2026-09-01 |
| Wake and push tests (`test_pushes`, `test_night46_context`, `test_render_cut`, `test_silent_cuts`) | no model | seconds | a named block in a built wake | a block lost at a size the fixture never reaches | grew from the wake audit, `plans/wake-audit.md` |
| Synthetic arc and seam arc (`test_arc_synthetic`, `test_arc_seam`, `test_delivery`) | canned completions | seconds | that the parts compose on one batch | two batches, a large file, a wrong call | designed, T0.5 of `rota/TESTS.md` |
| Chaos (`test_chaos*.py`, 14) | no model | seconds | a kill, a corrupt row, two writers | a seat's wrong act | designed, gate G3 of `rota/LOOPS.md` |
| Static prompt checks (`test_prompts.py`, 24) | no model | seconds | a brief that names a call its mode lacks | a refusal text that names one; only one guard's exits are listed by hand | grew |
| L1, ACT, L2 cases (`test_l1.py`) | recorded completion, live on a miss | 0 s replay; 15.7 s per live call | one seat on a 3 to 5 row fixture at window 12288 | a new wrong call; a state larger than the fixture; the cut paths, because a cassette holds no `done_reason` | designed, T1 of `rota/TESTS.md` |
| L3 handoffs, G1 segments | as L1 | as L1 | two seats in a chain; the seat flow | as L1 | designed, `rota/LOOPS.md` |
| The cassette register (`case_runs`, `casestatus`) | no model | seconds | which case is red or stale under which model and load | why; a count is a count of replays, not of calls | designed, frame 54 |
| The gate and its stale line (`rota.tools.gate`) | the suite, live re-record of stale cases since frame 89 | 465 to 1,106 s | a new red against the baseline | what no test asserts | designed, frame 30 |
| Night-data pins (`test_nightcount`, `test_nightreport`, `fixtures/extract_night.py`) | no model, reads `.rota/` copies, skip if absent | seconds | a counter on nights 91 to 93, 105, 106 | every night after 106 | grew, frames 83 and 105 |
| The world audit (`rota/tools/audit.py`) | no model, read-only | seconds per night | dangling refs, twin rows, an "answered" message with no reply | nothing it does not query; no script or gate runs it | designed: "Invariants over the world, not the write" |
| The night counters (`rota.tools.nightcount`) | no model | seconds, at GAUNTLET-DONE | made-up results, repeated wakes | the cause | grew, frame 105 |
| The night report (`rota.tools.nightreport`) and the cheap look | no model; the read is an agent | 73.5k tokens a read | the rows a read asks for | a fault no query names; the cheap look found 8 of 13 on night 119 | grew, frame 105 |
| The cycle alert (`test_cycles`, the CYCLE line) | no model | live during a night | a repeated round | its cause | designed, frame 83 |
| The walk, a cold night (`probes/gauntlet_click.sh`) | live model, GPU | 1 h 48 to 3 h 30 | any fault the model meets on click | a fault the model does not meet that night | designed, `rota/LOOPS.md` G4 |
| A warm night | live model | about 1 h | delivery only | onboarding | ruled, 2026-09-24 |
| A seam night (`probes/seam_start.py`) | live model from a recorded state | the walk starts 1 min after launch | the step under test | earlier steps | designed, frame 104 |
| The interview (`probes/frame37/interview_turn.py`) | one live call on a recorded prompt | minutes; 128.6k tokens for frame 121 | what the seat read and understood | a fault outside that turn | ruled, 2026-10-02 |
| Replays and fuzz in review scratchpads (frames 121, 122, 135, 136) | no model | minutes | a door over every recorded call of nights 113 to 120 | lost when the scratchpad is cleaned | grew; none is in `probes/` |

Observed sources for the table: the module docstrings, `plans/operating-facts.md` lines 153, 164, 210, 218, 235, 237, 239 and 673, and `.rota/night120.log` and `.rota/night121.log` for the night lengths, 2026-10-05.

Three facts from the read change the picture (observed: 2026-10-05):

- The world audit exists and runs on no night. Over nights 113 to 121 it prints 41 to 108 findings per night. On night 119, 68 of 72 are "answered and nothing answers it", 29 of them principal `converse` rows, so its signal is unread.
- Frame 122's two parser instruments still sit only in session 419281dc's scratchpad, `review122b/fuzz.py` and `review122c/prose.py`, as `plans/operating-facts.md` line 164 warned.
- `test_a_mode_that_encodes_holds_the_exits_the_guard_names` checks that a guard's named exit is in the mode's tools. It lists two exits by hand. Frame 126's `ledger.log` is the same class, outside its list.

## 2. The walls against the inventory

Classes: A, a door admits a wrong call. B, a wake or note hides or misstates a fact. C, a refusal names a call that fails. D, the model's judgement on a correct prompt. E, an instrument of the build session. F, other: F1 a door refuses a correct call, F2 a route is missing by design. "Before" means a test that a rule stated in advance could hold, with no data from the wall's own night (reasoned: the brief's strict sense).

| Frame | Fault | Class | Existing tier, and why it missed | Cheapest tier before a night |
|---|---|---|---|---|
| 135 | encode replaces a project test row | A | T0 sandbox: no fixture holds a project test row with no criterion | (e) copied id, on a (d) fixture |
| 138 | new id adds a second test | A | the guard reads `ctx.writes` only; no case stores a test first | (e) new id on a criterion with a stored test |
| 136 | span write drops used imports | A | the check ran on whole-file writes only; a case cannot force a span (frame 92) | (a) on night 113's s146, same sign; (e) span off at the head |
| 140 | span drops a def tail, commit lands | A | no test sends a write and a commit in one reply after a `dropped` note | (e) span ends inside a def, then commit |
| 116 | five challenges in one reply | A | the repeat door counts per call; no case sends a burst | (e) burst |
| 129 | decision restated as a new item | A | L1 VK cases end at the decision | none in the strict sense; a door test after |
| 113 | seat writes its own tool results | A | nightcount counts it, nothing gates on it | (e) made-up results block |
| 139 | two reads evict each other | B | runner tests use small files; register window 12288 | runner test on a 1,000-line fixture at 16384 |
| 134 | diff block cuts the source | B | wake tests assert blocks on small wakes; no cassette is cut | (b) rule "the source survives", on a large fresh fixture |
| 130 | wake shows another batch's green run | B | every fixture holds one batch | (d) two batches share an inherited id |
| 127 | red rows cut the source | B | as 134 | (b), as 134 |
| 120 | one traceback 34 times | B | as 134 | (b) on a fixture red at import |
| 121 | runner notes state wrong things | B | `test_render_cut` checks the words, not their truth; the cut path has no cassette | (g) a note's claim against the state |
| 117 | stub of a stub loses the call | B | no runner test held a 3,000-character write | (f) property: a stub of a stub still parses |
| 132 | prose answer closes the challenge | B | the audit's "answered" check fires on 13 of 16 nights from 106, but a Tester may answer by encode, so it cannot separate this class | (e) prose answer with no call |
| 137 | refusal names an absent argument | B | parser tests on hand forms; the fuzz is in a scratchpad | (f) and (g) on parser refusals |
| 126 | refusal names a missing tool | C | the exits check lists two exits by hand | (c) static: a named call is in the mode's tools |
| 128 | door sends the fix to a new file | C | no case fixes an inherited test | (c) follow the advice, on (d) |
| 123 | door advice leaves contradicting tests | C | as 128 | (c) and invariant "a criterion holds one test" |
| 143 | test asserts a default it lacks | D | only a model sees it | none; interview and L1 after |
| 131 | plain function invoked as command | D | no general rule, specific to Click | none in the strict sense |
| 133 | writes back the removed line | D | the seat had the fact | none; the interview |
| 142 | scripted principal names no option | E | `walk.py` has no test of its answers | unit test: an answer per ask kind |
| 144 | night corpus is no tier | E | this record | this record |
| 141 | surface door refuses package import | F1 | sandbox tests import from the module | (j) the project's own tests as calls the doors must admit |
| 125 | door reads "already" as a name | F1 | door tests on hand texts | (f) generated English sentences |
| 122 | parser cannot read nested quotes | F1 | parser tests on hand forms | (f) wide fuzz |
| 114 | inherited red test has no route | F2 | a refusal that names no call is legal | (c) every refusal names a reachable call |
| 115 | Architect answer has no words | F2 | edge coverage asserts an edge, not its content | none; a ruling |

Class counts (reasoned: this read's judgement per frame, 29 frames): A 7, B 9, C 3, D 3, E 2, F 5 (F1 3, F2 2). A, B and C are 19 of 29, faults of a structure's answer to a call. D is 3 of 29. In the strict sense, 23 of 29 have a tier that could see them before a night, and 6 do not: 129, 143, 131, 133, 144 and 115.

## 3. The candidate categories, judged

| Candidate | Close to it today | Before a night (strict) | Only after, as a regression | Build / run | Main risk |
|---|---|---|---|---|---|
| (a) state invariants after each recorded landed call | `rota/tools/audit.py`; frame 136's replay of 89 writes | 136 (night 113's s146) | 135, 138, 140, 123, 132 | about 80k / minutes; local, the nights are gitignored | 41 to 108 audit findings per night today; noise makes it unread |
| (b) wake rebuilt from recorded states | `test_night46_context`; frame 121's 93 cut events | 127 and 134 only if an older state held the shape (unread) | 120, 127, 134, 130, 139 | about 80k / minutes | a recorded state from an old schema; the 16384 window must be the pin |
| (c) every refusal that names a call is followed | the exits check (two exits); frame 136's dry run | 126, 114, 128, 123, and frame 135's three review cycles | 135, 136 | about 40k / seconds | a refusal's call is prose; a script must extract it |
| (d) two batches share the project's tests | none; every fixture holds one batch | 130, 135, 128 | none | about 30k / seconds | fixture upkeep |
| (e) scripted wrong seat on fresh fixtures | the desk guards, one call per wall | 135, 138, 136, 140, 116, 113, 132 | none | about 150k / under a minute | the catalogue holds only what a person names |
| (f) property and fuzz tests on doors | frame 122's fuzz, outside the repo | 122, 137, 117, 125 | none | about 20k to copy, 60k to fix seeds | a narrow generator reads 0 where a wide one read 64 |
| (g) truth check of notes and refusals | `test_render_cut` checks words | 121, 137 | 130, 132 | fold into (b) and (c) | each note needs a predicate; that is a design per note |
| (h) seam night in place of a cold night | `probes/seam_start.py`, frame 104 | the D class only, and still a night | all | built / about 1 h, GPU | a stale seam pair (`plans/operating-facts.md` line 154) |
| (i) designed and never built | T2 arcs on real models (`rota/TESTS.md` status); the audit never wired; no night-replay tier was planned before frame 144 | n/a | n/a | n/a | n/a |
| (j) the project's own tests and code as known-good calls (added) | none | 141, 125 if prose is fed | none | about 30k / seconds | a door may be right to refuse a real file |

Observed sources: `plans/stack.md` frames 121, 135 and 136, `plans/archive/stack-2026-10-05.md`, the audit over nights 106 to 121, 2026-10-05.

**Is the claim true that the register cannot catch a structure fault, because it replays recorded completions? No.** The claim holds for one seat's new wrong call. It is false for structure (reasoned: `ReplayOnlyBackend.complete` returns the recorded text, and the runner then executes its calls through today's doors). Three counter-examples:

1. Frame 106: `L1-AR-a-dead-end-is-reported-not-sat-on` went 0 of 5 because the first prompt's `[code.diff]` block changed with commit 4876aae (observed: `plans/operating-facts.md` line 237, 2026-10-01). A wake change reached the register as a red.
2. A turn's key holds the whole prompt, and turn 2's prompt holds turn 1's results. So a door that changes its answer to a recorded call makes the case stale or red (reasoned: `key_for(system, user, ...)`, `rota/llm/cassettes.py:395`).
3. The gate re-records stale cases live since frame 89 (observed: `plans/operating-facts.md` line 219). The register calls a model.

The true limit is narrower. The register sees structure only on the states its fixtures hold: 3 to 5 rows, one batch, window 12288, no cut event (ruled: `rota/TESTS.md` doctrine 0; observed: `plans/operating-facts.md` lines 217 and 673). The walls of nights 113 to 122 live in states it never holds: two batches, 34 inherited tests, a 1,011-line file.

## 4. One recommendation

Build in this order. Each item names its price on Opus, its review and its run time (reasoned: prices from frames 121, 135 and 136's actuals).

1. **The refusal reachability check (c).** Collect every refusal and note that names a call. Assert that the call is in every mode that can meet the door. Run the dry run of frame 136 on each named call. About 40k and one review of 70k. Seconds in the gate. It removes the cycle that cost frame 135 four reviews, 304k.
2. **Copy the parser fuzz and the old-against-new compare into `probes/` (f).** Put a fixed-seed slice in the gate. About 20k. Do it first if the scratchpad of 419281dc is due for cleaning.
3. **Two fresh fixtures (d) and the wrong-seat catalogue (e).** Fixture one: two batches that share inherited project tests, one stored Tester test per criterion. Fixture two: a 1,000-line module with a `from __future__` header. The catalogue: a copied id, a new id on a full criterion, a span off at the head, inside a def and at the tail, a write and a commit after `dropped`, a burst, a prose answer, a made-up results block, a backslash path, a repeated call. After each call, assert the invariants of item 4. About 150k and two reviews of 70k. Under a minute.
4. **The invariant library (a), run on the catalogue's states, on every night copy, and at GAUNTLET-DONE.** First remove the audit's by-design rows. About 80k. Minutes, local.
5. **The wake survival check (b)** over the `tests_failing` and `tests_missing` wakes of nights 113 to 121 at 16384: a source block, one row per red test of this batch at its head. About 80k. Minutes.

Total about 370k of build and about 350k of reviews. In the strict sense, items 1 to 3 would have held 16 of the 29 walls before a night (reasoned: section 2's last column). The night hours this saves are a prediction: about half the walls of nights 113 to 122 would not need a night to be found.

A night is still needed for these:

- The D class: 143, 131, 133 and 129. The seat had a correct prompt.
- Every ends-when ratio. A stochastic seat is measured only on a night (ruled: Roman, 2026-10-03).
- The 16384 window with real cut events, the scripted principal (142), and onboarding.
- A wrong call that nobody catalogued. Use a seam night (h) where the frame touches only delivery.

## 5. Where the first answer needs a correction

These points correct frame 144's stack text of 2026-10-05 09:46:

- "The register replays recorded completions, so it cannot make a new wrong call" is true. The inference that it cannot see a structure fault is false (section 3).
- "No replay entered the suite" is partly false. `test_nightcount` and `test_nightreport` read nights 105 and 106. `extract_night.py` feeds `test_cycles` and `test_next_batch`. `test_toolproto_quotes` pins calls of nights 105, 115 and 118. What is absent is a sweep over the whole corpus (observed: `tests/rota/`, 2026-10-05).
- The first tier of frame 144 partly rebuilds `rota/tools/audit.py`, which the answer did not name.
- The ends-when proves each tier by removing a fix of frame 130. Frame 130 is unclaimed, and `git log` holds no fix for it (observed: `plans/stack.md` and `git log --since=2026-10-03`, 2026-10-05).
- Replays of night data mostly catch a wall after its night. Prevention comes from (c), (d), (e) and (f), on fresh fixtures (reasoned: section 3's strict column).
