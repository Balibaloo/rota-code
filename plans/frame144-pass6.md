# Frame 144, pass 6: the scenes, repaired to states that a night produces

Meta workflow. Pass 6 of frame 144, the night databases are not a test tier. A fresh implementing agent on Opus wrote this record on 2026-10-05, on branch `f144p5` in the worktree `C:/Users/roman/rota_f144p5`. The pass repairs the twelve findings of the delta review of 906b765. No file under `rota/` outside `rota/testkit` changed. No refusal's text moved. The gate's stale line is 0.

Commit: 2d7cc73 (code and tests). This record is the next commit.

## The rule, and the engine that applies it

The rule of the review: a scene is a state that the real scheduler, the real ops and the real gates produce. `scenes.turn` applies it at every step (observed: each build, 2026-10-05):

- It calls `scheduler.frontier`, the loop's own call, so the quarantine marks land as in a night.
- It takes the frontier's own wake of the role and kind it is asked for, with its detail. A wake that the frontier does not hold fails the build.
- A scheduler action goes first, as in `loop.step`. A session is refused while an action waits, and an action runs through `loop._perform`.
- A session's dispatch is counted by `note_dispatch`, and a second dispatch carries its attempt. A batch start runs `lifecycle.start` before the session. A committed `tick:quarantined` session sets `reported`, as `loop.step` does.

The principal speaks through `talk.open_with`, the TUI's intake, and answers through `principal.pump` with `ScriptedPrincipal`. `answer` defers each ask before the one it answers, as a `None` in the script does. No raw row of a message remains. The raw rows left are `config.project_root`, as in pass 5, and none other.

Every scene now runs the onboarding's survey phase first, through the frontier: each area's Terminologist, then each area's Architect, and constraint zero after each survey. The reason: without an onboarding, the Developer's first commit indexes the code, the phase turns to `frame`, and `open_tips` holds every deliver (observed: S1's second item never reached the Vision Keeper, 2026-10-05). Nights 119 to 124 are onboarded, and their `k0` binds nothing (observed: read-only reads, 2026-10-05). The scenes set `onboarding_phases` to `survey`, a setting the principal owns. The default runs eight more phases, and none of them binds a file.

## The twelve findings

1. **S7's review.** The Architect's `tick:annotate` wake writes `batch_touch` for `charges.py` and `upgrade.py`. The Critic passes on its review wake, so `structural_review` fires (observed: the frontier holds `architect|tick:structural_review|b1`). The test checks the touch set against the binding. The proof removes f933f25's matcher (see the proofs).
2. **S1 and S2's starts and runs.** In S1, item 2 arrives after b1's red harness, its sign-off relay ranks it 2 above item 1, and the frontier's `do:preempt` defers b1. Each harness runs on the `do:harness` wake after a Developer commit. b2's Developer commits `src/billing/export.py`. No run has a NULL `commit_sha` in any scene (observed: `night_shape.py`, 2026-10-05).
3. **The principal's verdict.** `principal.pump` lands each verdict, its `rulings` row and `config verdict:<id>`, and closes the confirm. The sign-off runs as a night runs it: the Vision Keeper's `tick:signoff` and `msg.submit_liaison`, the Liaison's `msg.present_principal`, the pump, the Liaison's `verdict_signoff` with `msg.relay_vision_keeper`, and the Vision Keeper's `problem.prioritize`. No confirm or present stays open.
4. **The kinds.** The shared `item` step runs the Architect's deliver with `model.consult`. `annotate` runs the Architect's annotate and the Liaison's touch note, which the principal acknowledges. `rulings` now holds a row per verdict. The park's quarantined row has `reported = 1`. The park's `batch_dep_facts` row is gone: no op writes it, and no night holds one. The park's docstring says so, and says that the scene proves the park keeps b1 out of `next_batch`, with b2 and b3 in priority order.
5. **S5's catalogue.** X2 is a row, refused by `tests_encode` with "test_upgrade.py is t1's file, and t1 is the test of this same criterion". X7 is a row, held by frame 138.
6. **W138.** The row is held by "frame 138".
7. **The words.** The constraint row's words are "no constraints row has id=". The shared test now fails a row that has a door and no words. Each such row goes red when its own door is removed (see the catalogue).
8. **The park's fix wakes.** Each comes from the frontier with its `attempt N` detail. The loop's own `replace(wake, attempt=n)` sets the attempt on the second and third dispatch with no commit. The `tick:quarantined` wake runs before the park ask, with `msg.present_principal(refs=['b1'])`, and the principal acknowledges it.
9. **The free columns.** No column is dropped whole. `sessions.prompt_hash` becomes a token. Inside `sessions.pins_json`, only the `prompt_hash` value becomes a token, so a moved `model`, `num_ctx` or `temperature` is seen. In `test_runs.output`, `turns.user` and `turns.system`, only pytest's summary time becomes a token. `config_history.at` becomes a token, because the survey's `config.set` writes it.
10. **The quarantine mark.** The park's docstring names both writers. The builder reads `quarantine_overrun`'s count at the first call of the next frontier, and `test_quarantine_overrun_marked_the_key_and_the_liaison_reported_it` asserts 1. Under the `S_cap` mutant, the overrun marks nothing, `quarantine_stalled` marks the key after the wake list is computed, and the frontier comes back empty (observed: `mut6.py S_cap`, 2026-10-05).
11. **The commit path.** The second build's test lands the first sweep call of each op through `scenes.land`, a whole session that commits. A `code.write` adds `code.commit`. Five ops land: `tests.encode` and `code.write` on S1, `msg.challenge_tester` and `verdicts.emit` on the Critic's scene, and `findings.find` on S7.
12. **The cost.** The park's second build is in `test_scene_park_again.py`. The runs are the real wake's, so none is dropped. The park reaches attempt 5 with four commits, because the harness now also runs after the first commit. That removes one commit and four runs.

## The scenes

The build times are the module fixtures' setups. The second build's time includes the landed calls. Seven files ran on four workers with `--dist loadfile` in 91.4 s of wall time, while night 125 ran on the same machine (observed: `pytest --durations`, 2026-10-05). The aim of about 60 s is not met. Section 5 of the brief allows no fewer real runs.

| Scene | Build, second build | Steps not held | Tables that still differ in kind | Proofs: the fix removed, and what went red |
|---|---|---|---|---|
| S1 `two_batches` | 11.7 s, 24.7 s | 2 of 49 | `findings`, `verdicts`, `constraint_bindings` empty; `runs_other_batch_test` 3 (frame 130) | Frame 135's project-id door: both project-id rows. A zero span: 10 sweep span writes. The keypress approval in `principal.land`: the build, slicing never fires. |
| S2 `merged_then_next` | 15.8 s, 28.0 s | 2 of 53 | `constraint_bindings` empty; `runs_other_batch_test` 3 (frame 130) | The merge's delivery, `if tree and tests:`: the delivered-test test and its row. The other-batch door: the merged id row. Frame 135's door: the delivered id row. |
| S5 `challenged` | 13.0 s, 16.0 s | 1 of 36 | `findings`, `verdicts`, `constraint_bindings` empty | `version = version + 1` in `db.py`: the version test. The clash door: the X2 row. The harness per test: the build, the replaced test gets no run. |
| S3 and S4 `park` | 27.0 s; 23.6 s and 22.3 s in `_again` | 1 of 73 | `findings`, `verdicts`, `constraint_bindings` empty; one open clarify, which is the park | The park ask's id that names the batch (b23d17b): the park test. `parked`: the park test. The overrun's `>=`: the build and the overrun test. |
| S7 `critic` | 17.3 s, 9.5 s | 1 of 33 | `findings`, `verdicts` empty | The claim door of `verdicts_emit`: the fail-before-claim row. The harness per test: the build. The keypress approval: the build. |
| S7 `review` | 10.6 s, 11.3 s | 1 of 34 | `findings` empty | f933f25's matcher, `or grain.split("::", 1)[0] in grains`: the push test and the violated finding. The constraint's existence check: the `k_none` row. The harness per test: the build. |

"Steps not held" is `would_fire.py`'s count of NEVER and PRED lines (observed: 2026-10-05). Each is the Developer's `tick:batch_start` session, once per batch. `loop.step` runs `lifecycle.start` between the choice of the wake and the session (`loop.py:313-318`), so the predicate no longer fires when the session starts. The scenes do the same. The park's two lines where the attempt differs are the loop's own `replace(wake, attempt=n)`.

The tables that every scene leaves empty and a night fills: `challenges`, `decisions`, `frame_rulings`, `ledger` and `model_areas`. The onboarding phases that write them do not run, and the scenes' surveys attest none found without `model.describe`. `tick_attempts` is empty in S1, S2, S5 and the Critic's scene, because a batch's move resets its keys (`db._lift_quarantines`). Nights 123 and 124 keep rows for batches that never moved. No scene fills a table that no night fills (observed: `night_shape.py`, nights 119, 121, 123 and 124, 2026-10-05).

Every proof ran in memory through `mut6.py`, which hands the changed source to the loader and writes no file. Each target file's sha256 was the same after the run as before.

## The catalogue, 10 rows

| Scene | The call | The door and the words, or the frame that holds it |
|---|---|---|
| S1 | b2's Tester encodes under `inh_db70e774` at `tests/test_charges.py` | `tests_encode`, "inh_db70e774 is the id of the project's test" |
| S1 | the same id at `tests/test_export.py` | `tests_encode`, the same words |
| S1 | b2's Developer writes a top level with an unbound name (W146) | held by frame 146 |
| S2 | b2's Tester encodes under b1's merged id `t1` | `tests_encode`, "t1 is" |
| S2 | b2's Tester encodes under the delivered file's project id | `tests_encode`, "inh_ae5f34e8 is the id of the project's test" |
| S5 | the challenge wake encodes `t2` for c1 (W138) | held by frame 138 |
| S5 | the challenge wake encodes `t1_fixed` at a new path (X7) | held by frame 138 |
| S5 | the challenge wake encodes `t1_fixed` at `test_upgrade.py` (X2) | `tests_encode`, "test_upgrade.py is t1's file, and t1 is the test of this same criterion" |
| Critic | the Critic's fail with no claim | `verdicts_emit`, "a fail on c1 stands on its test actually encoding it" |
| S7 | the Architect's finding on `k_none` | `findings_find`, "no constraints row has id=" |

Each of the seven rows with a door went red with its own door removed: frame 135's door (three rows), the other-batch door, the clash door, the claim door and the existence check (observed: `mut6.py`, 2026-10-05).

## The sweep, 46 right calls

- S1, 43, as in pass 5.
- The Critic's scene, 2: the claim of False and the challenge, and the fail after a claim of True.
- S7, 1: the Architect's violated finding.

The Developer's challenge on `tests_failing` left the sweep. Its wake needs a red harness, and S7's harness is green. S5's build lands the same call through a whole session.

## The strict xfails, 4

- `test_scene_two_batches.py::test_every_run_names_a_test_of_its_own_batch`, held by frame 130.
- The W146 row, held by frame 146.
- The W138 row and the X7 row, held by frame 138.

## The suite

The seven scene files: 73 passed, 4 skipped, 4 xfailed, in 91.4 s on four workers (observed: 2026-10-05).

The gate on 2d7cc73 (observed: `python -m rota.tools.gate`, 2026-10-05):

```
suite: 23 failed, 2859 passed, 34 skipped, 12 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 755.7s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds are the three that the brief expects.

## Deviations

- **A new scene, `critic`.** S7 must end at the structural review, which needs a pass verdict. One commit gets one verdict: "your verdict on batch b1 at this commit already landed" (observed: 2026-10-05). So the Critic's rows run on S7's build stopped at the Critic's wake, and `review` is that build plus the Critic's pass.
- **The survey phase in every scene**, with `onboarding_phases` set to `survey`, for the reason above.
- **S2 has a structural review.** `k0` binds nothing after the survey and so is global. The Architect files a satisfied finding on `k0`, as nights 119 and 121 hold.
- **The park reaches attempt 5 with four commits**, not five.
- **The park's dependency row is gone.** S4's "b3 behind b1" is not in the scene.
- **The Developer's challenge left S7's sweep**, for the reason above.
- **`turn` does not call `cascade_wakes`, `cycle` or `note_spill`.** The first two read rows only, and `note_spill` reads an Ollama card that a scripted run has not.
- **The time aim is not met**: 91.4 s against about 60 s.

## Seen and not fixed

- **The same challenge twice is refused with the wrong words.** `rota/core/sandbox.py:2131` refuses a challenge sent twice in one session with "saying it again with different refs" when the refs are equal (copied: the brief; X4 of `cat_probe.py`).
- **An unonboarded project holds every deliver after its first commit.** A commit indexes the code, `onboarding_phase` returns `frame`, and `open_tips` holds each deliver until the frame is judged (observed: S1 without the survey, 2026-10-05). A delivery engagement that never onboarded meets it on its second sentence.
- **Under the `S_cap` mutant the frontier is empty**, with a quarantined key and a running batch. `quarantine_stalled` marks the key after `all_wakes` computed the list, so `tick:quarantined` is absent in that pass. The overrun's order exists for this case, and the scene now holds it.
