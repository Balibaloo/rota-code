# Frame 144, pass 7: the scenes are states that the loop reaches

Meta workflow. Pass 7 of frame 144, the night databases are not a test tier. A fresh implementing agent on Opus wrote this record on 2026-10-05, on branch `f144p5` in the worktree `C:/Users/roman/rota_f144p5`. The pass repairs the findings of the delta review of 2d7cc73. No file under `rota/` outside `rota/testkit` changed. No refusal's text moved.

Commit: 0c38e09 (code and tests). This record is the next commit.

## The design

A scene's build is now a run of `loop.step` and nothing else (`scenes.step`, `scenes.play`). The loop pumps the principal, computes the frontier, performs an action or picks a wake, counts the dispatch, starts a batch, runs the session and cascades. `turn` and `drive` are gone. A scene holds two scripts (observed: each build, 2026-10-05):

- The seats' script answers a session by the key of the wake that the loop dispatched: `scheduler.tick_key` for a tick or an action, `role|verb|refs` for a message. A wake with no answer fails the build, with its key, its attempt and the frontier in the error. Two survey keys take a function, `role|tick:survey`, that answers every area.
- The principal's script answers an ask by its verb and its exact refs, through the `principal` argument of `loop.step`. An ask with no answer is deferred.

The principal speaks between two steps through `talk.open_with`, the intake of the TUI. A build ends when a condition on the database holds. `scenes.build` fails when a seat or an answer of the script is never asked for, so a scene cannot claim a step it did not take.

The seams, each named in the module's docstring:

1. `loop.run_session` is wrapped for the build. The wrapper reads the wake that the loop dispatched and passes the seat's lines as the backend. Every other argument goes on unchanged.
2. `provision.ensure_env` is a stub, as in pass 6.
3. The backend that `loop.step` receives names no server, so `note_spill` reads no card. No code replaces it.

`cascade_wakes`, `cycle` and the attempt counting now run in every build, because the loop runs them.

## The eight findings

1. **The wake that the loop does not pick.** Removed by the design. The twin check below finds 0 steps that differ from a plain `loop.step` in every scene.
2. **S1.** In the loop's order b1's fix wake goes before item 2's sign-off. b1's Developer commits once more and stays red, then ends three sessions with nothing done, and the key is quarantined. The Liaison reports it, the principal reads it, item 2's sign-off ranks it first, and `do:preempt|b1,b2` defers b1. b1 is then parked, so the loop wakes the Liaison's park ask, which the principal leaves open. b2 starts and its harness runs. The claim stays: two batches that share the project's tests, the first deferred by a preempt. The test asserts the preempt and the absence of `do:park`.
3. **S7's observed constraint.** In `critic` and `review` the loop picks `liaison|tick:observed_entries|<k>`. The Liaison presents it, the principal approves it, the Liaison relays the verdict to the Architect, and the Architect runs `model.adopt`. A test asserts one present and a provenance that is no longer `observed`. No other scene has a code-basis row, so the loop picks the wake nowhere else.
4. **The review's binding.** The test now asserts that `constraints_for_grains` on the touch set holds the bound constraint, and that the empty grain set does not. Proof on the data (`touch7.py`, on copies of the database): green as built, red with the binding deleted, red with `charges.py` out of the touch set, green on a fresh copy.
5. **The landed calls.** `land(sc, key, name)` now runs the loop until it picks `key`, and the seat's session is the sweep's call. `scenes.LANDINGS` holds five lands, each on the loop's pick: S1's encode on `tester|tick:tests_missing|b2`, and on the review's second build the Architect's violated finding, the Developer's `code.write` on `developer|tick:finding_violated|b1`, the Critic's challenge on `critic|tick:review|b1`, and the Critic's fail on the next `critic|tick:review|b1`, after the Tester answered the challenge. Between the lands the Critic upholds the finding and the Tester replaces t1, as seats.
6. **The end frontier.** Every scene asserts its end frontier by key, and its `tick_attempts` rows at the end. The table below lists them.
7. **S2's order of annotation.** Removed by the design: b1 and b2 are annotated in the loop's order.
8. **The fail while the same Critic's challenge is open.** A catalogue row with `question` set, on the review's second build after the Critic's challenge lands (`at`). It gates nothing and warns with today's outcome: the call lands (observed: the gate run of this pass). The question, open: may a Critic fail a batch on a criterion while its own challenge of that criterion's test is open? No door changed. In one session, a door already refuses the same fail: "you have already challenged the tester this session". That shape is now an ordinary row of `critic`.

## The twelve removals that stayed green

| Scene | Removal | Now | How |
|---|---|---|---|
| S1 | `A_proj_sign2` | not met | No project test in S1 has a criterion. Only a landed fix of a project test gives one. |
| S1 | `N_lift` | red | The build fails: "the loop never asked for {'developer\|tick:tests_failing\|b1': 1}". |
| S2 | `A_replaces` | not met in S2 | S2 re-encodes no test. S5's new row "the stored id at a new path" goes red. |
| S2 | `N_harness_count` | red | The end's `tick_attempts` rows. |
| S5 | `A_stored_path` | red | The new row "the stored id at a new path", words "t1 is stored at test_upgrade.py". |
| S5 | `N_batch_of_msg` | not met | One batch runs, so the running fallback names the same batch. |
| park | `S_key_batch` | not met | No quarantined key names a second batch or an id that holds another. |
| park | `P_ask_once` | red | The build fails on a second `liaison\|tick:park_ask\|i1,b1`. S1 goes red the same way. |
| critic | `N_harness_count` | red | The end's `tick_attempts` rows, in `critic` and `review`. |
| critic | `N_lift` | red | The end's `tick_attempts` rows, in `critic` and `review`. |
| review | `A_diff_touch` | red | The new row "a violated finding on a file the diff does not touch". |
| review | `L_touch_unknown` | not met | The review's touch set is known. |

## The scenes

Proofs ran in memory through `mut7.py`, with the test file minus its second build. Each run printed that the changed source reached the compiler and that the target file's sha256 was the same after (observed: `mutout7/`, 2026-10-05).

| Scene | Steps that differ from plain `loop.step` | End frontier | `tick_attempts` at the end | Proofs, red |
|---|---|---|---|---|
| S1 `two_batches` | 0 of 61 | `tester\|tick:tests_missing\|b2` | the fix key (3, quarantined, reported), `quarantined\|b1` 1, `park_ask\|i1,b1` 1 | frame 135's door (2 rows); `N_lift` (build); `P_ask_once` (build) |
| S2 `merged_then_next` | 0 of 58 | `tester\|tick:tests_missing\|b2`, `terminologist\|tick:survey\|src/billing`, `terminologist\|tick:survey\|.` | none | the merge's delivery (3 tests); the other-batch door; frame 135's door; `N_harness_count` |
| S5 `challenged` | 0 of 42 | `critic\|tick:review\|b1` | none | `version + 1` (2 tests); the clash door; `A_stored_path`; `A_replaces` |
| park | 0 of 79 | `developer\|tick:batch_start\|b2` | 8 rows, in the test | the park ask's id (b23d17b, build); `P_ask_once` (build); the overrun's `>=` (build: the loop is quiescent) |
| `critic` | 0 of 42 | `critic\|tick:review\|b1` | none | the claim door; `N_harness_count`; `N_lift` |
| `review` | 0 of 43 | `architect\|tick:structural_review\|b1` | `critic\|tick:review\|b1` 1 | f933f25's matcher (2 tests); the existence check; `A_diff_touch`; the binding deleted (data) |

"Steps that differ" is `twin7.py`: build A by the scene's builder, then build B on a fresh repository with a plain `loop.step` per step, a `ScriptedBackend` of A's lines chosen by the step's index alone, and no seam on `run_session`. Every table of A equals B's in all six scenes (observed: `twin7.txt`, 2026-10-05). No `batch_start` case remains.

S2's end frontier holds two survey wakes: the merge changed `src/billing` and the root, so the survey of those areas is owed again. It is the loop's own state, after the Tester's wake.

Equal rows: each scene built in its own process under `PYTHONHASHSEED=1` and `=2` gives equal rows in all 46 tables (observed: `dump7.py`, 2026-10-05). The tokens: the scene's root in three forms, pytest's run time in `test_runs.output`, `turns.user` and `turns.system`, `sessions.prompt_hash` and the `prompt_hash` inside `sessions.pins_json`, `config_history.at`, and the value of `config created_at`.

## The cost

The park's tests and its second build share `test_scene_park.py`, so the park is built twice. `test_scene_park_again.py` is gone. `review` goes on from `critic` in `test_scene_review.py`: the `critic` rows, its calls, then the Critic's pass, then the review's tests. `test_scene_critic.py` is gone. Ten builds in all, against thirteen.

Times, each file alone on one process (observed: 2026-10-05 21:43): S1 37.0 s, S2 28.4 s, S5 22.4 s, park 46.8 s, review 26.6 s, 161 s in all. The five files on four workers took 330 s, with the park's two builds at 107 s and 196 s. The machine was not steady: the park file alone took 47 s at 21:45 and 161 s at 21:52 on the same code, with no other gate running. So the four-worker figure is not a measure of this pass, and the aim of about 60 s is not shown. The park is the slowest file: 79 steps and 9 harness runs per build.

## Deviations

- **S1 now holds a quarantine and a park ask.** The loop's order gives them. The brief allowed "whatever the loop's order gives".
- **The park ends with b3's touch note unread.** The principal answers in the pump of the step that also picks b2's start. To end before b2 starts, the scene ends with the note sent.
- **Four lands share the review's second build**, in the loop's order, and not a build each. Each lands on the loop's pick, and the state it meets has nothing landed out of order: the fail lands after the challenge is answered. A build each costs four more builds of `critic`.
- **The Developer's `code.write` lands on the review's fix wake**, not on b2. No scene's loop picks a Developer wake of b2 after b2's start.
- **The park's file keeps the name `test_scene_park.py`**, and `test_scene_park_again.py` is removed. The brief said the park's tests run on `park_again`'s build. The file holds the same thing under the clearer name.
- **The park's overrun count is gone from the ids.** The loop's frontier calls `quarantine_overrun` itself. The test asserts the row (3, 1, 1) and that the report is the loop's next pick after the last dispatch. Under `S_cap` the build fails, because the loop is quiescent.
- **Test names in the chained module carry the scene's name**, such as `test_a_right_call_lands_critic`, so two scenes share a module.
- **The time aim is not shown**, for the reason above.

## Seen and not fixed

- The fail while the Critic's own challenge is open lands across sessions and is refused in one session. The rule is not ruled.
- After a merge, the Terminologist's survey of the merged areas is owed again (S2's end frontier). Each merge on a night costs one survey session per changed area.

## Report

**Commits on `f144p5`.** 0c38e09, the code and tests. The record is the commit after it. Nothing is pushed, and `rota/foundation` is untouched.

**The seams in the loop.** Three. `loop.run_session` is wrapped only to give the seat's lines as the backend. `provision.ensure_env` is a stub. The backend names no server, so `note_spill` reads nothing. The module's docstring names all three.

**The findings.**

1. HIGH, the wake that the loop does not pick: removed. A plain `loop.step` replay differs in 0 steps in all six scenes.
2. HIGH, S1: built in the loop's order. One red commit, three empty sessions, quarantine, report, preempt, park ask, then b2.
3. S7's observed constraint: presented, approved, relayed and adopted, wherever the loop picks it (`critic`, `review`).
4. LOW, the binding: `constraints_for_grains` asserted on the touch set and on the empty set. Red with the binding deleted, red with `charges.py` out of the touch set.
5. LOW, the lands: all five land on the loop's picks. Four share the review's second build, in the loop's order.
6. LOW, the end frontier: asserted by key in every scene, with the `tick_attempts` rows. `P_ask_once` is now red.
7. LOW, S2's order: removed by the design.
8. The fail while the Critic's own challenge is open: a question row, `at` the review's challenge land. Today it lands. No door changed.

**The twelve removals.** Red: S1 `N_lift`, S2 `N_harness_count`, S5 `A_stored_path`, park `P_ask_once`, critic `N_harness_count`, critic `N_lift`, review `A_diff_touch`. Not met: S1 `A_proj_sign2`, S2 `A_replaces` (red on S5's new row instead), S5 `N_batch_of_msg`, park `S_key_batch`, review `L_touch_unknown`. The table above gives each reason.

**Per scene.** Steps that differ from the loop: 0 in each of the six. The end frontiers, the proofs and the times are in the tables above. Times alone: S1 37.0 s, S2 28.4 s, S5 22.4 s, park 46.8 s, review 26.6 s. All five on four workers: 330.0 s on a machine that was not steady.

**The catalogue: 14 rows.** S1 3, S2 2, S5 5 (one new), `critic` 2 (one new), `review` 2 (one new), and the question row on the review's second build. **Right calls: 46** in the sweep, and 5 landed. **Strict xfails: 4.** S1's run test and the W146 row, held by frames 130 and 146. The W138 and X7 rows, held by frame 138.

**The suite.** The five scene files on four workers: 81 passed, 4 skipped, 4 xfailed, 1 warning. The gate on 0c38e09 (observed: `python -m rota.tools.gate`, 2026-10-05):

```
suite: 23 failed, 2867 passed, 34 skipped, 12 xfailed, 17 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 1455.1s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds are the three that the brief expects. The seventeenth warning is the question row's warning.

**Deviations.** See the section above: S1's park, the park's unread note, four lands on one build, the write on the review's fix wake, the park file's name, the overrun count, the test names, and the time aim.

**Seen and not fixed.** The open question of finding 8. The survey that each merge owes again.

**The probes** are in the session's scratchpad, `p7/`: `build.py`, `lands.py`, `twin7.py` with `twin7.txt`, `mut7.py` with `runmuts.sh` and `mutout7/`, `touch7.py`, `dump7.py` with `seed/`.
