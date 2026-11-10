# The design of rota, the product: six shapes, 2026-11-10

Written by one design agent for session 1efd37b1, frame 364, step 6 of the product review. The page proposes. It rules nothing and changes no code. Each proposal is (reasoned: this agent). Each count is the count of the page that the line names. I did not count again.
Short names: Map is `plans/method/product-map-2026-11-10.md`. FR is `plans/method/product-fold-read-2026-11-10.md`. Comp is `plans/composition.md`. PF is `plans/principal-flow.md`. DO is `plans/design-onboarding-2026-11-03.md`. UT is `plans/understanding-test-blind-2026-11-03.md`. D9 is `plans/dry9-read-2026-11-10.md`. CP is `rota/COMPLETION.md`.

## Result

1. Six shapes. Each is a whole way that rota works, and each moves a different axis.
2. A, the honest measure: no code changes. Runs start clean, the seat can say no, and a key judges the merge.
3. B, the example is the judge: the person approves input and output examples, and the change must pass them.
4. C, the strong hand: small models read and write rows, and one stronger model takes the edit.
5. D, the capability record: each stop writes the desk, the act and the model, and the intake reads those rows.
6. E, the read at the end: fewer pages before the work, and one reading page before the merge.
7. F, learn by the request: no model onboarding before the request. The model reads only the touched area.
8. Recommendation: A first, then B, with the stop row of D. Five questions go to Roman.
9. Largest doubt: B makes the fold's stop honest. B does not make the fold merge, because the Developer's code was wrong in 4 of 4 runs (FR).
10. The code contradicts no claim of the map as the break test corrected it. It widens two claims. See "What the code adds to the map".

## What holds for every shape

- The skeleton stays: one wake is one session, approval comes before work, and the merge conditions decide each merge (Map, "The reading", point 2).
- Each test runs under the measure of shape A. A count over runs that share state is not a count of observations (Map, mass 5: 395 of 1,855 sessions repeat word for word).
- The three loops are care, judgement and cost (Map, "The reading", point 4). "The Developer's stop" is the fold edit, wrong in 4 of 4 runs (FR). C1 to C5 are the claims of the break test (Map, step 5).
- The records hold three repositories with runs: icalendarI (dry runs 3 to 9), tipsI (dry run 2, blind run 1) and clickI (93 nights). The dry runs used the `local` profile: qwen3:8b, qwen3.5:9b and gemma4:12b-it-qat (observed: `rota/llm/profiles/local.toml`, and the stored profile of `.rota/dry3.db` and `.rota/dry4.db`, read by one agent).

## Shape A: the honest measure (no code of rota changes)

1. **The idea.** Rota stays as it is. Each run starts from a fresh clone with no history of rota, and a blind agent with the key closed sits in the seat. A key and a hidden probe exist before the run. One run card says what the run tested.
2. **The person.** Nothing changes. The seat is a blind agent, because "I will not sit in the seat untill it delivers multiple changes on multiple repos and is responsive. Use it yourelf" (ruled: 2026-10-31 00:58).
3. **The desks.** No change.
4. **Removed:** the reset of a lineage copy as the start of a measured run. **Amended:** nothing in `rota/`. **Added:** `probes/clean_start.sh` from `blind_start.sh` (observed: built, in a scratchpad only, `plans/dry-blind1/recipe.md`:11). `probes/runcard.py` reads the run database in read-only mode. The keys and probes of UT go under `probes/keys/`, as `plans/dry9/probe.py` does.
5. **The run card.** Who sat in the seat. Each page, and whether the seat agreed. The parts P1 to P6 of the destination that the run tested (Map, mass 9). The pages before the first batch. The score class of UT (`Correct`, `Honest stop`, `Wrong merge` and the others). The desk, the act and the attempt at the stop, read from the park, quarantine and ladder rows.
6. **Loops and claims.** It answers point 1 of the reading: the records cannot answer the question, "and the reason is the measures". It answers the step 6 view, point 3 (Map). It leaves every loop and C1 to C5 unchanged. It only counts them truly.
7. **Rulings crossed.** "Core is complete when every partial is built, click and two more lineage repositories merge cold" (CP, ruled 2026-09-12). A fresh clone is not a lineage copy. Question 1.
8. **The test.** It works if two runs on two repositories end with a card and a UT score, and share no session word for word. Baseline: 0 runs with a person, 1 blind run that stopped at its third page, every subject carries earlier deliveries (Map, reading point 1 and mass 9). UT ran 1 of its 72 designed runs (Map, mass 9).
9. **Cost and first.** 1 to 2 passes, all in `probes/`. Nothing must exist first. A blind agent writes each key before the run, as for `plans/dry-blind1/key.md`.
10. **Weakest point.** It fixes nothing. A blind agent is not "a careful person", so P1 and P5 stay untested by a person.
- **What it can show:** whether today's rota merges a right change on a clean repository with a seat that says no, and the desk and act at each stop. **What it cannot show:** a person's reading, the cause behind an act, or any change.
- **Overfit check.** It holds for any request that has a key, on any repository and any model. UT holds 12 requests on 3 repositories (designed). No key exists for a repository outside the three, and no record covers a language other than Python.
- **Honest stop.** It tells the person nothing new. It tells the session the desk and the act where the model stopped, on each run.

## Shape B: the example is the judge

1. **The idea.** Each criterion carries three to five examples: an input and its result, or "this stays the same". The person approves them at signoff. The harness runs them at the base and at the head. Only the person can change an approved example.
2. **The person.** The signoff page shows the examples in plain words: "this 80-character line becomes these two lines". After a stop, the page shows the example, the result he approved, and the result of the code.
3. **The desks.** The Terminologist writes the examples from the request, the account and the code. The Tester writes tests and can no longer turn a test green with no change of code. The Developer gets the failed examples with the actual output. The Critic reads the example results beside the diff.
4. **Removed:** the delete of earlier test rows at the same commit (`rota/core/harness.py`:186-191) when a test was written again. **Amended:** `criteria.specify` in `rota/roles/api.py` takes examples. The invented-literal door (`rota/core/divergence.py`) reads an approved example as material. `mergeable` (`rota/core/lifecycle.py`:1141-1244) gains "every example passes at the head". **Added:** an `examples` table in `rota/core/schema.sql`, its render on the signoff page (`rota/core/sandbox.py`, `rota/roles/principal.py`), and its run in the harness.
5. **What exists.** The "worked example" of page 1, "For a command, the command and its output" (PF:64-67, ruled 2026-09-13, not built). The base verdict door `_base_verdict_refusal` (`rota/roles/api.py`:23971). It said nothing on dry run 9, because the tests raised `ImportError` at the base (D9, point 3). The fold read found the faults by a call of `_foldline` on chosen strings (FR).
6. **Loops and claims.** It answers the judgement loop and C2: the gate gets an input that the loop did not write. It answers the care loop in part: a correction moves before the batch, where a contest costs no cancel. It answers C5 in part. It leaves the cost loop, C3 and the Developer's stop.
7. **Rulings crossed.** "Their attention is the scarcest budget" (Comp): the page grows. The Tester's `challenge` mode, which grants a read of the code (ruled 2026-09-24, `rota/roles/prompts/tester/challenge.tools`). "A prediction never blocks. Only a fact or a ruling gates" (Comp) holds: an approved example is a ruling. Questions 3 and 4.
8. **The test.** Under shape A, on the fold request and one request of UT on tipsI. It works if no merge passes a hidden probe that its examples fail, and if each stop names an example. Baseline: the batch's tests were green on wrong code in 2 of 3 fold heads (FR). Six batches went from fail to pass with no change of code (Map, mass 3).
9. **Cost and first.** 4 to 6 passes: the table and the door 1, the page 1, the harness and the gate 1 to 2, the Terminologist brief and its register cases 1 to 2. First: shape A, and Roman's answers to questions 3 and 4.
10. **Weakest point.** A small model writes the examples. The fold has a trap, "75 octets, not characters" (DO:147). Only a careful reader catches a wrong example, and no record shows a person who reads a signoff page.
- **Overfit check.** It holds for a function with an output. For click, an example is a command and its output (PF:65-66). For a change with no output, such as a docstring, only "this stays the same" examples apply. No record shows the Terminologist writing examples on any model.
- **Honest stop.** "For this input you approved this result. The code gives that result. The team tried 3 times." The person can check each sentence himself.

## Shape C: the strong hand

1. **The idea.** Small models read the repository and write rows, criteria and pages. One stronger model takes the edit and the verdict. A small desk that fails at its cap hands the same act to the stronger model once.
2. **The person.** Each page that reports a change names the model that wrote it. A stop page says "the small model failed 3 times, and the larger model failed too", or names the one that did the work.
3. **The desks.** The Developer and the Critic run the stronger model. The Architect, the Vision Keeper, the Terminologist and the Liaison stay small. The ladder `exhausted` (`rota/core/predicates.py`:1401-1459) gets one rung: the same act on the stronger model.
4. **Removed:** nothing. **Amended:** `routing()` in `rota/llm/profile.py` writes the `tick=model` pairs that `config.routed_model` reads already (built, not used). The `exhausted` predicate. **Added:** one profile, from `local-gemma-dev.toml`, and one rung in `LADDER` (`rota/core/predicates.py`:44-53).
5. **What exists.** Per-desk models and `RoutedBackend` (`rota/llm/llm.py`:680-703), used. `local-gemma-dev` routes the Developer to gemma-4-26B-A4B, built and not used. gemma-4 took "from a traceback to a change" 5/5 where qwen3.5:9b took 0/5 (CP:292-299). Night 62 with gemma-4 at the Developer desk "failed the same way the 9B did" (CP:213-214). Design C of DO proposes "a model profile per wake kind", not built.
6. **Loops and claims.** It answers the Developer's stop in part, if a stronger model writes the fold. It leaves the judgement loop: the loop's own tests passed wrong code (FR). It leaves care, cost, C1, C3 and C4.
7. **Rulings crossed.** "a careful person runs rota alone" (Comp, 2026-09-10), if the model is hosted (DO:143). "No model change is needed on this evidence" and "Roman owns this order" (CP, 2026-09-14). F1, "Parked until a remote provider" (CP, ruled 2026-09-17).
8. **The test.** Under shape A, the fold request on the stronger profile. It works if one head of two folds a long line at a space within the limit. Baseline: 0 of 4 heads did (FR), 0 of 7 fold runs merged (Map, reading point 5).
9. **Cost and first.** 2 to 3 passes. First: one register column for the fold edit on the stronger model, and a check that the 12 tokens a second (header of `local-gemma-dev.toml`) fits a run.
10. **Weakest point.** No record shows a stronger model writing the fold. A stronger edit still passes a gate whose tests the loop wrote. A model swap costs a reload in each direction (DO:153).
- **Overfit check.** The benchmark ran on small fixtures, "click's prompts are not" small (CP:314-315). The fold is one request on icalendarI. No record covers a repository or a request outside these two. The result is true only for the model named.
- **Honest stop.** It names the model at the stop. A stop with both models failed is the plainest record of "where small models stop".

## Shape D: the capability record

1. **The idea.** Each stop writes one row: the request kind, the desk, the act, the model, the attempts and the failed check. The rows stay on the person's machine across runs. At intake, the page says how often rota did this kind of work and where it stopped.
2. **The person.** The confirm page adds one line: "rota merged 3 of 3 changes that add a guard, and 0 of 7 that rewrite a function body". Outside the record, he chooses: a draft branch with no merge, or no work.
3. **The desks.** The Vision Keeper names the request kind at confirm. No other desk changes.
4. **Removed:** the step words as the only reason on a stop page (`rota/roles/principal.py`:2720-2742). **Amended:** the writers at quarantine, park and `exhausted` (`rota/core/loop.py`, `rota/core/predicates.py`). **Added:** a `stops` table, a store outside the run database, one line on the confirm page, and a draft mode that skips `worktrees.integrate`.
5. **What exists.** The `model_down` row names the true cause of one kind of stop (`rota/core/loop.py`:608-653). The path proposal of page 0, "assumed: this is a small change" (PF:48-50), is designed and not built. `nightcount.py` counts made-up turns per desk. The register attributes reds by hand.
6. **Loops and claims.** It answers C5: a stop shows by its limit and its model. It answers "honest about where small models stop" directly. It answers the cost loop in part: work outside the record costs no merge attempt. It leaves the judgement loop, care, C1 to C4.
7. **Rulings crossed.** "X2 the tool measuring its own seats" is post-core (CP, ruled 2026-09-12). "A prediction never blocks" (Comp): the line informs and never holds. "The tool never rules for the Principal" (Comp): the choice is his. Question 5.
8. **The test.** Under shape A, each stop of two runs has one row that names the desk, the act and the model. Baseline: a stop shows by the wake that failed, and 21 of 24 unresolved questions on the nights did not climb (Map, C5). 6 of 29 model reds carry an attribution (Map, mass 9).
9. **Cost and first.** 3 to 4 passes. First: shape A. The kinds come from the runs, not from a list made in advance.
10. **Weakest point.** The kinds overfit: 11 runs hold 5 sentences, and the fold counts six times (Map, mass 2 limits). The kind is a small model's judgement. A record of a few runs speaks with more weight than it has.
- **Overfit check.** The row is general. The kind list is not: clickI nights hold 3 sentences, icalendarI holds 5. No record exists for a model outside the profile, so the line must name the model.
- **Honest stop.** The plainest of the six shapes. It tells him before work and at the stop.

## Shape E: the read at the end

1. **The idea.** The person gives his attention at two points only. Before the work: one page with the cut, the items and the path. Before the merge: one page with the change in plain words. Everything else is a note.
2. **The person.** The pages before the first batch fall to one or two. The merge waits on his read of the diff, the tests and what each check covered. He merges or contests with words.
3. **The desks.** The Liaison writes the reading page. The Developer builds one ticket per session (PF, stage 1). The Vision Keeper proposes the path at confirm.
4. **Removed:** the agenda pages of ledger rows before the first batch (`rota/core/scheduler.py`:1268-1376) become notes. **Amended:** `merge_gate` defaults to `review` (`rota/core/config.py`:70-74), and the hold gets a page and a release (`rota/core/lifecycle.py`:1241). **Added:** the slice read (PF:140-181), the path line of page 0, and a reply route for a Liaison `converse`.
5. **What exists.** `merge_gate=review` returns "waiting on the principal's review" with no page and no release. No page explains a merged change (`rota/roles/principal.py`:555-592). No seat can answer a `converse`: the CLI refuses it, and the TUI marks it answered (`rota/cockpit/tui.py`:525-533).
6. **Loops and claims.** It answers the cost loop at the seat and the care loop, and point P5, "they can read". It answers C2 in part: the person judges. It leaves the Developer's stop, C3 and C4.
7. **Rulings crossed.** "Sign-offs after that, including on merges, are opt-in" (Comp). Frame 306 set aside a diff page before each merge as a cost to his attention (`plans/frame306-route-design.md`:179-185). "Use it yourelf" (2026-10-31): until he sits, a blind agent reads the page.
8. **The test.** Under shape A, two runs on two repositories. It works if the pages before the first batch are 2 or fewer, and the blind seat contests a wrong merge. Baseline: 6 to 16 pages (Map, mass 2). "One page at a time" holds on 3 of 23 pages (Map, mass 1).
9. **Cost and first.** 5 to 8 passes. First: the reply route for a `converse`, the wall of blind run 1 (Map).
10. **Weakest point.** The person's read becomes the judge, and no record measures a person's read. A blind agent's read with a key is not that read.
- **Overfit check.** It holds for any request with a small diff. The merges so far stand on one commit each (Map, mass 3), and the click merges were 48 lines (`rota/MAP.md`:123). A large diff costs the person more, and no record shows the cost.
- **Honest stop.** The reading page splits the change: what a test he approved checked, what only a model judged, and what nothing checked.

## Shape F: learn by the request

1. **The idea.** Before the first request, rota runs the steps with no model only: index, harvest, lexicon and shape. At each request, the model reads the touched area and its callers. Each record is kept by the commit and area hash, so a second run reads nothing twice.
2. **The person.** The first request starts in minutes. The page says which areas rota read for this request, and which it did not.
3. **The desks.** The Vision Keeper, the Architect and the Terminologist read one area per request, not every area. Delivery desks get the records of the touched area, pushed by the door, as `bound_constraints` does now.
4. **Removed:** the default list of model phases before the first request (`rota/core/config.py`:145-162). **Amended:** the survey offers the touched area and its ranked callers (`rota/core/scheduler.py`:1216-1264). `rota onboard --force` keeps the records whose hash matches (`rota/cli.py`:457-463). **Added:** the trigger from the guess (DO, design B, not built).
5. **What exists.** A survey record stays valid while its area hash matches, within one database (`rota/core/scheduler.py`:1236-1254). The warm snapshot and the night cassette exist on clickI nights only (`probes/walk.py`:152-175, `probes/night_cassette.py`). The `lazy` default and the harvester are built. Run T, the touched read, is designed and not run.
6. **Loops and claims.** It answers the cost loop and C3. It answers C4 in part, if the request's area is read when the request names it. It leaves judgement, care and the Developer's stop.
7. **Rulings crossed.** The model of the project is a capability with three measures (CP, item 11, ruled 2026-11-04). DO ruling 2 kept the whole read as the person's choice, to be decided by a measure. Comp: "The structure holds a model of its shape, terms, boundaries, and external commitments".
8. **The test.** Under shape A, two runs on icalendar and one on click. It works if the sessions before the first batch fall below half and the UT trap tasks score no lower. Baseline: about two in three sessions before the first batch are onboarding, and 123 onboarding sessions of dry run 8 repeat (Map, break test C3, mass 5).
9. **Cost and first.** DO estimates 32 to 38 cycles, about two sessions, for design B. First: Run T.
10. **Weakest point.** A trap of UT needs a record outside the touched area, such as the second copy of a function. A touched read can miss the copy that a whole read finds.
- **Overfit check.** DO: on 2,800 grains it saves about 30 minutes, and on 300 grains the cost "is close to today's". tipsI has 29 grains. So the gain is large on icalendar and small on a small repository, and the destination names a small one.
- **Honest stop.** It says what rota did not read. It does not say where the model stopped.

## The comparison

| | A measure | B example | C strong hand | D record | E read at end | F by request |
|---|---|---|---|---|---|---|
| Axis | what a run reports | what judges a change | which model does which act | what rota takes on | what the person sees, when | what rota learns first |
| Code of rota | none | table, door, gate, page | profile, one rung | table, store, one line | page, gate default, reply route | survey trigger, reuse |
| Loops answered | none, it counts them | judgement, care in part | Developer's stop in part | none whole | cost at the seat, care | cost |
| Claims answered | none | C2, C5 in part | none | C5 | C2 in part | C3, C4 in part |
| Honest stop | to the session | concrete, checkable | names the model | before work and at the stop | splits checked and unchecked | names what was not read |
| Rulings crossed | 1 | 2 | 3 | 1 | 2 | 2 |
| Passes | 1 to 2 | 4 to 6 | 2 to 3 | 3 to 4 | 5 to 8 | about 2 sessions |
| Weakest point | fixes nothing | a small model writes the examples | no record of a stronger fold | the kinds overfit | no record of a person's read | the touched read misses a copy |

## The recommendation

Build shape A first, then shape B, and take the stop row of shape D into B. The reasons:

- Every other test needs shape A. The map's first reading says the records cannot answer the question, "and the reason is the measures". Shape A crosses one ruling, and it changes no code.
- Shape B answers the loop that decides "a change they can read". The gate is sound on 77 of 77 merges, and its tests passed wrong code (Map, C2; FR).
- Shape B gives the person a page he can check with no knowledge of rota's rows. The fold trap and the made function name of dry run 9 both show on an example.
- Shape B builds a ruled design, the worked example of page 1 (PF, ruled 2026-09-13). It needs no new model and no new seat.
- The stop row of D costs one table and gives "honest about where small models stop" its record. B's failed example fills the row's last field.
- Shape C waits for A and B. If B shows the edit as the stop on clean runs, C is the next lever, and its test is ready. Shape E waits for a person, by the ruling of 2026-10-31. Shape F waits for Run T.

The order, one act at a time, with an expectation before each act and a compare after it:

1. Shape A: the clean start and the run card. One run of the fold request on today's rota. Expected: no merge, and the card names the Developer's edit at the stop.
2. The `examples` table, its door and its render. Read: the signoff page of one run shows the examples in plain words.
3. The harness and the gate. Read: on dry run 5's head, the examples fail where the batch's tests pass (FR).
4. The stop row. Read: each stop of two clean runs has a row with an example.
5. Stop, and compare over two clean runs on two repositories. Then choose C, E or F on the counts.

**The largest doubt.** Shape B makes the fold stop honest and does not make it merge. With the right function named, the Developer's code was wrong in 4 of 4 runs (FR). So B may turn "0 of 7 merged" into "0 of 7 merged, with a true reason". The destination needs a merge too, and that needs shape C or a request that a small model can build.

## The questions for Roman

Each question names the ruling it departs from. The words in quotes are the question as he gets it.

1. Shape A. "Core is complete when ... click and two more lineage repositories merge cold" (CP, 2026-09-12). "Today each test run starts from our own copy of a project, and that copy already holds earlier work by rota. The new measure starts from a clean download instead. Does a merge there count toward your completion line?" Recommended: yes, and the old copies stay for the nights. [high]
2. Shape A. "Use it yourelf" (2026-10-31 00:58). "Until you sit in the seat, a helper sits there with the answer key hidden, and it says no when a page is wrong. The report marks 'a careful person' as not tested. Is that enough for the count?" Recommended: yes. [med]
3. Shape B. "Their attention is the scarcest budget" (Comp). "Before the work starts, the page shows three to five examples for each part: this goes in, this comes out. You approve or correct them, and the change must pass them. Is that worth the extra lines?" Recommended: yes, five examples at most. [high]
4. Shape B. The Tester's challenge mode (2026-09-24). "Today, when the coder says a test is wrong, the tester writes it again, and the test can pass with no change to the code. With examples, only your word changes an example you approved. The tester's own tests can still change. Do you agree?" Recommended: yes. [med]
5. Shapes B and D. "X2 the tool measuring its own seats" is after core (2026-09-12). "When the team stops, rota writes one line: which step, which model, how many tries, and which example failed. You see that line on the stop page. Is this one line part of core?" Recommended: yes, because it is the "honest" half of the goal. [med]

## What the code adds to the map

- No seat can answer a Liaison `converse`. The map names the CLI refusal (blind run 1). The TUI also shows the converse and marks it answered (`rota/cockpit/tui.py`:525-533), and the web cockpit has no reply route (observed: one read agent, `rota/cockpit/server.py`:518-528).
- A dropped constraint keeps its row, and `bound_constraints` reads no objection, so the constraint likely still feeds the build (observed: one read agent, by grep, not by a run). This widens C1.
- Outside the map: `rota/MAP.md`:68 says the Tester writes "from the criterion alone", and the `challenge` mode grants `code.source`. CP:72-77 says `local-gemma-critic` shipped, and the dry runs' `local` profile runs the Critic on qwen3.5:9b. `plans/frame306-route-design.md` says `merge_gate=review` gives a diff page, and the code gives a hold with no page.

## What I could not see

- I ran nothing. Each cost in passes is my estimate. DO's cycle count is its own estimate.
- I read the map and not the mass read pages, except through the map. I read no transcript and no night.
- Whether a small Terminologist writes right examples. No record exists on any model.
- Whether a stronger model writes the fold. The one record, night 62, is on click and failed.
- The profile of dry runs 5 to 9. The read agent found no database for them under `.rota`, and I did not read `plans/method/product-seat-population-2026-11-10.md`.
- Dry run 9 (D9) is outside the map's 11 runs. I cite it for the base verdict door and the made function name only.
- The TUI and converse claims come from one read agent. I checked `rota/cockpit/tui.py`:525-533, `rota/roles/principal.py`:186-189, `rota/core/harness.py`:186-191 and `rota/core/lifecycle.py`:1241 myself.
- Whether a person reads an example page better than a criteria page. No record shows a person at any page.
