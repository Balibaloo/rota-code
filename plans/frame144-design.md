# Frame 144: the design, checked against the table

Meta workflow. Pass 0 of frame 144, the night databases are not a test tier. One agent on Opus wrote this record on 2026-10-05, after `plans/frame144-table.md`. No code changed, no gate ran, and `rota/TESTS.md` is not edited.

The table has 1,074 cells. 295 are T, 63 are P, 437 are N and 279 are n/a (observed: `f144/count.py` over the table, 2026-10-05). The frame's items as written hold 63 cells. The changes below hold about 150 more. The largest gaps are two columns that no item reaches: a refusal that states a false fact, 86 N cells, and a named call that no dry run checks, 71 N cells.

## 1. The items and the scenes against the table

### What each item holds as written

| Item | Cells it holds | The N cells it leaves in its own area |
|---|---|---|
| 1. Each refusal that names a call is followed through frame 136's dry run | 12 NC cells of `code.write` | 59 NC cells of staged ops (A3 18, A4 29, A7 12) and every FF cell. The dry run exists for `code.write` only (observed: `_admits`, `api.py:9022`, 2026-10-05). |
| 2. The fuzz and the compare move into `probes/` | 1 cell, the parser's RR (W122, W125) | The parser's FF and NC (W137) |
| 3. The scenes and the catalogue | 34 cells: S1 9, S2 5, S3 3, S4 2, S5 5, S6 2, the catalogue 8 | Every P3-S cell holds only when a test asserts on the scene. The ends-when names one proving wall per scene, not the assertions. |
| 4. The audit's invariants on the catalogue's states and at night's end | 8 cells | The audit holds 6 invariant groups (observed: `rota/tools/audit.py:71-175`, 2026-10-05). None of them is the one test per criterion, the project row's body, or a run of another batch. |
| 5. The fix wake at 16384 keeps its blocks | 8 cells of B2 | The same cut on `verdict_failed`, `batch_start`, `tests_missing` and `review` (B4, rank 9) |

The ends-when's own count for items 1 to 3, 16 of 29 walls before a night (copied: `plans/frame144-inventory.md`, section 4, reasoned), is about walls. The table counts cells. The two numbers measure different things and do not conflict.

### The changes, each with the cells it holds

Seven changes, in order of the cells they hold. Each one is short.

1. **Widen item 1 to every op, and check the facts.** (a) Each refusal that names a call records it as data. A helper `_offer(op, **kwargs)` renders the sentence and appends `(op, kwargs)` to a new `ctx.offers` list. (b) The dry run of a staged op is the real call on a copy of `ctx.writes`, `ctx.outbound`, `ctx.refusals` and the other mutable fields, which are restored afterwards. No api op writes the database directly (observed: no `INSERT`, `UPDATE` or `DELETE` statement in `api.py`, 2026-10-05). So the copy is the whole effect, except `code.write` (disk, `_admits` exists), `code.commit` (git) and `web.fetch`. (c) The check, on each scene state and each catalogue call: every offer is admitted, and item 4's invariants hold on the staged result. (d) The fact check, on the same refusals: each id that a refusal quotes names a row, each path exists in the worktree, each line number is inside the file, each argument name is in the op's signature. Cells: 61 NC cells (A3 18, A4 29, A7 12, A6 2) and about 60 of the 86 FF cells (reasoned: the FF cells that quote an id, a path, a line or a name, counted by eye). Not held: the revert door's claim about runs (A2, rank 11) and the runner's prose offers (A5, 9 cells).
2. **Name item 4's invariants.** I1 a criterion holds at most one test (W138, W123). I2 an `inh_` row has no criterion, and its body is the project file at the batch's base (W135). I3 a merged batch's latest run of each of its own tests at its head is a pass. I4 a run row's test is a test of the run's batch (W130). I5 a parked batch holds one open park ask, and an open park ask names a parked batch. I6 a quarantined key never names a merged or abandoned batch. I7 at most one batch runs (audit 3). I8 one open batch per item (audit 2). I9 an answered message has an answer, with the by-design rows listed and removed (audit 5, 68 of 72 findings on night 119 by `plans/frame144-inventory.md`). Cells: the 8 P4 cells, and the assertion that the 18 P3 cells of part C need.
3. **Merge item 5 into S6, and widen it to four delivery wakes.** S6 builds the large module. Item 5's rule, "each block the wake should hold survives the cut", runs on the `tests_failing`, `verdict_failed`, `batch_start` and `tests_missing` wakes at `num_ctx` 16384. Cells: the 8 P5 cells, the 2 P3-S6 cells, and 3 N cells (B4 cut and wrong at night size, B3 the Tester's cut). One build serves both.
4. **Merge S3 and S4 into one park scene, and add a dependent batch.** Batch b1 reaches attempt 5 of 10 with its `tests_failing` key quarantined. It is parked with its open park ask. Batches b2 and b3 are pending, and b3 declares b1 as its predecessor. Cells: the 5 cells of S3 and S4, and the stuck cell "pending behind a parked predecessor" (C1). `next_batch` admits a batch only when every predecessor is merged or abandoned (observed: `scheduler.py:1350-1383`, 2026-10-05). So b3 waits while b1 is parked, and the scene asks whether anything tells the principal (reasoned).
5. **Add S7, the review scene.** One batch with one constraint bound to the touched file, a diff that violates it, and a test that does not encode its criterion. The right calls run against the doors: `findings.find` with `violated`, `verdicts.emit` with `fail`, and a Developer's challenge that names both sides. Each must be admitted. The structural review wake must show the constraint. Cells: ranks 2, 3, 4 and 7 of the table, which are the wrong-merge cells that no item reaches, about 11 cells. `as::test_a_bound_constraint_demands_a_review_when_the_batch_meets_it` and `as::test_a_violated_finding_still_stops_the_merge` exist, so S7 extends `test_arc_seam.py` (observed: the test names, 2026-10-05).
6. **Add two wrong calls to the catalogue.** A write whose top level loads a name it does not bind (W146, red today). A span whose text binds an old name to a wrong value (s228's `t = TypeVar`, `plans/frame136-design.md`, section 6). Each catalogue call asserts: refused, or the invariants and the harness hold after it lands. Cells: 2 AW cells of A1.
7. **Add the known-good sweep, the inventory's (j).** On S1 and S6, each project test file goes in as a `tests.encode` body under a new id, and each project module gets a whole write and a span write with one added comment line. Each call must be admitted. Cells: about 15 RR cells of A1 and A3, and W141 (reasoned: the RR cells whose door reads imports, names or paths).

A further instrument, outside the gate: **a door-coverage report**. Run the suite once under line coverage, and list each `raise` line of `api.py` and `sandbox.py` that no test runs. It replaces the text match behind the AW column, 132 N cells, with a count that is exact. The gate then checks only that a new refusal site has a test that runs it. It is in the open questions because it costs a suite run under coverage.

### The N cells that no item holds, after the changes

- The RR cells of the doors outside S7 and the sweep, about 95 cells. A door that refuses a right call is found when a right call meets it, and only the sweep and S7 send right calls on purpose.
- The FF cells whose fact is not an id, a path, a line or a name, about 26 cells. The revert door's "the tests pass both ways" is the costly one.
- The A7 AW cells, 87, until the coverage report reads them.
- B1 and B3: the inbound shapes, the failed-run blocks of the Tester's challenge wake, and the shaped pushes of the shape modes, 18 cells.
- The runner's prose offers, 9 NC cells of A5.
- C3 `quarantine_looping` and C4 W142.

### What to remove

Nothing. Item 2 holds 1 cell of the table, and it stays, because the table covers the structure's side and the fuzz is the instrument for what a model can send (copied: `plans/stack.md`, frame 144's ends-when).

## 2. The scenes against the fixtures' code

The engine exists. `tests/rota/test_arc_seam.py` drives one sentence to a merged batch through the real scheduler, `run_session` with `ScriptedBackend`, real git on the sample repository, and `harness.run` (observed: lines 73 to 260, 2026-10-05). It takes 16.2 s for one batch and 19.0 s for a batch with two commits (observed: `pytest --durations=3`, 6 passed in 41.3 s, 2026-10-05). Its `drive` and `tick` helpers are local to the file. The sample repository holds three project tests, `tests/test_charges.py`, `tests/test_pricing.py` and `tests/test_templates.py`, which `harness.inherit` takes in at start (observed: `rota/testkit/samplerepo.py:676-698`, 2026-10-05). `gitfixture._template` builds the repository once per process and copies it, which is the pattern a scene cache can use.

What is missing for every scene: a module, `rota/testkit/scenes.py`, that holds `drive`, `tick` and one builder per scene, and returns the connection, the repository and the ids. Every scene below can be built with no model, because every seat's turn is a scripted completion through the real doors (reasoned: `ScriptedBackend` in `test_arc_seam.py`).

| Scene | The real ops that build it | Exists | Missing | No model? |
|---|---|---|---|---|
| S1, two batches share the project's tests | Two sentences through the Liaison, the Vision Keeper, the Terminologist, `tickets.slice`, `criteria.specify` and `batches.group`. `lifecycle.start(b1)` runs `harness.inherit`. b1's Developer edits `src/billing/charges.py` so that `tests/test_charges.py` goes red, and commits. `harness.run(b1)`. `lifecycle.defer(b1)` by a preempt. `lifecycle.start(b2)` inherits again under the same ids. `harness.run(b2)`. | Every op. The one-batch path. | The second item. A change that turns a project test red. The preempt step. | Yes. About 35 s by the anchor above (reasoned). |
| S2, a merged batch's Tester file is a project test of the next batch | S1, then b1's tests green, `verdicts.emit` pass, `lifecycle.merge(b1)`, then `lifecycle.start(b2)`. The Tester's `test_delete.py` at the root matches `inherit`'s pattern `test_*.py`. | `n46::test_the_developer_commit_leaves_the_testers_files_out_and_the_merge_delivers_them` holds the delivery. | The chain from S1. | Yes. About 10 s more (reasoned). |
| S3 and S4, merged into the park | b1 at five commits that leave a test red, `harness.run` after each. The `tests_failing` key dispatched past `tick_attempt_cap` 3 with no drain, through `note_dispatch` and `quarantine_overrun`. `predicates.park_ask` defers b1 and opens the ask. b2 and b3 pending, b3 behind b1 by a `batch_dep_facts` row. | `test_next_batch.py` holds the moves, on night 92's extract patched by SQL (observed: `fixtures/night92_cycle.json`, `_status`, `_attempt`, 2026-10-05). | The whole build through the ops. The op that writes the dependency fact, not read in this pass. | Yes. About 40 s, five harness runs (reasoned). |
| S5, a test at version 2 after an answered challenge | S1's b1, then the Developer's `msg.challenge_tester` with the criterion, the test and quotes, the Tester's challenge wake, and `tests.encode` with the stored id. | `ce` and `sb` build challenges and replaces on hand rows. | The chain from S1. | Yes. About 10 s more (reasoned). |
| S6, a module of 1,000 lines with a `__future__` header, and the wakes at 16384 | A generated module committed to the scene's copy of the repository before b1 starts, a criterion on a function deep in the file, a red test. Each of the four wakes built by `run_session` with `num_ctx=16384`, its first prompt captured. | `rn::test_the_assembled_prompt_of_a_replayed_turn_is_inside_the_budget` measures a size. | The generator, the capture, the block rule. The template must not change, or the cases that use the sample repository can go stale. | Yes. About 25 s (reasoned). |
| S7, review with a bound constraint | `model.amend` and a binding, then the batch through review. | Two `as` tests named above. | The right calls and the push assertion. | Yes. About 20 s (reasoned). |

The scenes together cost about 2.5 minutes of serial test time (reasoned from the 16.2 s anchor). The suite runs on several workers ("bringing up nodes", observed), and S2 and S5 extend S1, so the gate's added wall time is less. A build once per process, copied for each test, keeps the code as the source and stores no database between runs. Question 2 asks the judge to confirm that reading of the ruling.

## 3. Doctrine 0 of `rota/TESTS.md`

**Roman declined the proposed text below on 2026-10-05, and `rota/TESTS.md` holds another text since 0784616** (ruled: Roman, "the reason for small outputs is to make the results measurable"). The limit is on the output. The sentence on three to five rows of material is not in the doctrine. This note is the judging session's, c81b16d3.

The text today (observed: `rota/TESTS.md:48-52`, 2026-10-05):

> 0. **[A] Fixtures stay tiny - three to five rows, one judgement per case.** An 8B model will not fail a structural assertion, but it will drown in twenty statements with three plausible readings, and then the pass rate measures the fixture rather than the role. Harder variants get their own case ids so the simple one survives as the regression floor.

The ruling (copied: `plans/stack.md`, frame 144): "so small in output, can be complex in setup" (Roman, 2026-10-05 10:08). The proposed text, for Roman's check:

> 0. **[A] One judgement and a small output per case. The setup may be a scene.** A case asks the seat for one judgement, and its expected output is small: a few rows, one message or one call. The setup may be large. It may be a scene that code builds through the real ops, such as two batches that share the project's tests. A scene is built on every run and is never stored as a database. The material that the judgement weighs stays at three to five rows: an 8B model drowns in twenty statements with three plausible readings, and then the pass rate measures the fixture rather than the role. The rest of a scene is context. A case on a scene keeps a twin on a tiny fixture under its own id, so the simple case survives as the regression floor. Pin `num_ctx` to the night's window on a scene case (doctrine 2). (Ruled: Roman, 2026-10-05, "so small in output, can be complex in setup".)

Two points for the check. First, the sentence on three to five rows of material is this agent's reading. It keeps the doctrine's reason, which is about the input the judgement weighs, and the ruling speaks of the output. Second, the status lines at the top of `rota/TESTS.md` say that T1 cases "do not exist yet" and that the fixture is "(fixture database, one inbound message)". Both are out of date, and this design does not change them.

## 4. Prices

Anchors (copied: `plans/stack.md`, the statuses of frames 135, 136 and 144, harness lines):

- Frame 135, one door and its tests in `tests.encode`: a cold pass of 113.3k, then resumed passes of 36k, 15k and 24k. Four reviews: 99.2k, 71.6k, 66.4k, 67.1k.
- Frame 136, one door with a dry run, about 200 lines and 8 tests: a design of 214.6k, then resumed passes of 57k and 41k. Two reviews: 122.4k and 76.9k.
- Frame 144's inventory read: 171.6k.
- Sizes in the repository (observed: `wc -l`, 2026-10-05): `test_arc_seam.py` 415 lines, `test_arc_synthetic.py` 418, `rota/tools/audit.py` 239, `gitfixture.py` 232.

| Item or change | Build | Reviews | Gate time | Anchor |
|---|---|---|---|---|
| Item 1, widened: `_offer` at about 70 sites by script, the dry run of staged ops, the fact check | about 120k | two, about 140k | seconds, on the scenes' states | Frame 136's `_admits` (57k resumed, a 214.6k design before it) and frame 135's cold pass (113.3k). The script edit has no anchor. |
| Item 1 as written, `code.write` only | about 40k | one, about 70k | seconds | Frame 136's pass 2, 41k |
| Item 2 | about 20k | one, about 40k | seconds | No anchor in the repository. The files are outside it (copied: `plans/operating-facts.md` line 164). |
| Item 3: `scenes.py` with S1, S2, S5, the park, S7 | about 200k | two, about 150k | about 2 minutes serial | `test_arc_seam.py`, 415 lines, which each scene extends. No pass anchor for that file exists in the stack. |
| Item 3: the catalogue, 12 calls | about 50k | in the scene reviews | seconds | Frame 135's resumed passes, 15k to 36k each |
| Item 4: I1 to I9, the by-design list, the night hook | about 80k | one, about 70k | seconds | `audit.py`, 239 lines |
| Item 5 merged into S6, four wakes | about 60k | one, about 70k | about 25 s | No anchor. The block rule per wake has no built precedent. |
| The known-good sweep | about 30k | in the scene reviews | about 30 s | No anchor (copied: the inventory's estimate) |
| The door-coverage report | about 25k | one, about 40k | one suite run under coverage, outside the gate | No anchor |

The total is about 625k of build and about 630k of reviews. The inventory priced the five items at about 370k and 350k (copied: `plans/frame144-inventory.md`, section 4). The rise is item 1's widening, S7, and the named invariants. The table's 150 added held cells are the price's reason.

## 5. The proof per item: the landed fix that is removed

| Item | The fix removed | What goes red |
|---|---|---|
| 1 | The two `_admits` guards in `_span_lost_refusal`, `api.py:11243` and `11269`, landed by 08caa8d and narrowed by 467f4b8 (frame 136) | On S6, a span refusal offers a call that the dry run refuses. |
| 1, widened | Frame 135's pass 4, a71951a, which keeps a challenge of another test from opening a project test | The offered encode is admitted, and I2 fails on the staged result. |
| 2 | fb1bdba, "read a Critic's quote that holds quotes", in `toolproto.py` (reasoned: the headline matches frame 122's sign) | The fixed-seed slice holds a nested quote that no longer parses. |
| 3 | Frame 135's door, the project-id refusal in `tests_encode` near `api.py:5575`, from a9b094d and c68bd0e | On S1, the catalogue's copied id lands, and I2 fails. |
| 3, the park | 0c6e54e, "a quarantine park opens one ask to the principal, and a contest or a commit closes it" (frame 87) | On the park scene, I5 fails: a parked batch holds no open park ask. |
| 4 | The same as item 3, frame 135's door | I2 fails on S1 after the catalogue's copied id. |
| 5, in S6 | 2882eb5, "the fix wake shows a shared red output once", `runner._red_rows_by_output` (frame 127) | On S6 at 16384, the fix wake loses its source block. |

The ends-when named frame 130 as a proof (copied: `plans/frame144-inventory.md`, section 5). Frame 130 has no landed fix (observed: its block in `plans/stack.md`, unclaimed, 2026-10-05). S1 and I4 are red today on frame 130's cause, and they go green when frame 130 lands. That proves the scene by a wall it holds, which Roman accepted ("ok", copied: frame 144's status of 10:08). It is not a removal.

## 6. Open questions for the judging session

This agent did not read `LAWS.md`, `DECISIONS.md`, the archive or the transcripts for prior rulings on these questions. The judging session runs that read before it asks Roman.

1. **[med] Item 1's offers: a record as data, or a parse of the prose?** Recommended: data. `_offer(op, **kwargs)` at about 70 sites, by one script. The inventory names the prose parse as the main risk (copied: `plans/frame144-inventory.md`, section 3, item c). A refusal's text does not move, so no recording goes stale (reasoned).
2. **[low] Does a scene built once per process and copied meet "never stored as a database"?** Recommended: yes. The code builds it on every run, and the stored-database risk was a schema mark that falls behind (copied: frame 144's status of 10:03).
3. **[med] Merge item 5 into S6, and widen it to the four delivery wakes?** Recommended: yes. One build, and the wake cut on `verdict_failed`, `batch_start` and `tests_missing` is the same mechanism as walls W127 and W134.
4. **[med] Add S7, the review scene, to item 3?** Recommended: yes. It is the one scene that holds wrong-merge cells that no item reaches: a right fail verdict or a right violated finding refused.
5. **[low] The door-coverage report: a tool per frame, or in the gate?** Recommended: a tool per frame, with a gate check only that a new refusal site has a test that runs it. A full coverage run in every gate costs time that nothing measured.
