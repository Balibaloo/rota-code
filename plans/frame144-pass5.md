# Frame 144, pass 5: the review of ee17f70, and the scenes

Meta workflow. Pass 5 of frame 144, the night databases are not a test tier. A fresh implementing agent on Opus wrote this record on 2026-10-05, on branch `f144p5` in the worktree `C:/Users/roman/rota_f144p5`. Part A repairs the five lows of the delta review of ee17f70. Part B builds the design's step 4: `rota/testkit/scenes.py`, the catalogue of known wrong calls and the sweep of right calls. No model runs in either part. No refusal's text moved, and the gate's stale line is 0.

Commits: 69c10f0 (part A), 906b765 (part B).

## Part A, the five lows

Each repair has a test that goes red without it (observed: each test run with the repair stashed or removed, 2026-10-05).

1. **The digest holds `raw`.** `probes/frame122/fuzz.py`, `outcome`: each call and each refusal now adds `c.raw` to the digest. The fixture is recorded again. Every digest moved except 119 cases of the model slice that read nothing. No right set moved in any of the eight slices (observed: the right lists before and after, compared slice by slice). `test_a_moved_raw_text_moves_the_slice` holds it with a parser that moves `raw` only.
2. **The binder's own door.** `api.door_of`: when the walk reaches `call`, `dry_run` or `follow` with an empty chain, it takes that frame. A missing or unknown argument now names `... in call` through a seat's call, and `... in dry_run` for the dry run's `code.write` check. `test_an_argument_error_of_the_binder_names_its_door`.
3. **The head up to the bracket.** `sandbox._line_holds`: outside a docstring, the line's text before its first `(` must equal the quote's, cut at 60 characters as the decorator door cuts it. The word-boundary rule is gone, because the head rule holds it. `test_a_decorator_line_off_by_one_reads_false_on_a_twin_decorator` builds `@dec` above `@dec.b`, and a line fact moved by one reads false. The decorator door's add-after offer meets known finding 2 on that file, so the test has a line in `KNOWN_REFUSED_OFFERS`.
4. **A span with a node and no head.** `sandbox._span_holds` reads it false, except for a `match_case`, which `api._head_of` gives no head by design. `test_the_fact_check_reads_a_span_and_a_line_against_the_tree` now gives its facts a head. `test_a_span_that_names_a_statement_and_no_head_reads_false` holds the rule. The reviewer's "no head" mutant at the cut door's first span site turned `test_offers_followed.py` and `test_desk_guards.py` red by the fact check: "the fact names a FunctionDef and no first line" (observed: a byte mutant, then restored, 2026-10-05).
5. **The call log.** See the next section.

### The `id(ctx)` key of `_CALL_LOG`

- **Age.** The key dates from 231afe4, 2026-08-09, "feat(sandbox): namespaces built from edges, and the TOOL: protocol" (observed: `git log -S_CALL_LOG -- rota`, 2026-10-05). It is older than c888968. Frame 144's dry run did not introduce the reuse. The dry run cuts its own entry back and pops an entry it created.
- **A session can meet it.** The smallest reproduction, one process and two `ctx` objects: build a Developer sandbox, call `glossary.lookup`, never drain, free it, build a second sandbox, and drain. At build 9 the fresh `ctx` drained `('glossary.lookup', "term='account'")`, a call it never made (observed: `C:/Users/roman/repro_calllog.py` on this tree, 2026-10-05). `run_session` drains on both of its exits, so a stale entry needs a reader that logs calls and never drains. `rota/cockpit/progress.py` builds a sandbox and runs `push_working_set`, which calls `sb.call`, and never drains. The TUI runs `loop.run` in its own process. This pass did not prove that a preview and a session share one process (reasoned, not run).
- **Repair, by the brief's rule.** `tests/rota/conftest.py` holds an autouse fixture that empties `sandbox._CALL_LOG` after each test. No session behaviour changed. `test_a_test_that_never_drains_its_calls_leaves_them` and `test_the_next_test_starts_with_an_empty_call_log` are a pair in one file, which `--dist loadfile` keeps in order. Without the fixture, the second goes red. The reviewer's order, `test_offers_followed.py`, `test_desk_guards.py` and then `test_s9_tool_calls_are_recorded_as_evidence`, was green on this tree before the fixture too: 297 passed (observed: 2026-10-05). The collision depends on addresses, so the pair is the test that holds it.

## Part B, the scenes

`rota/testkit/scenes.py` holds `drive` and `tick`, one builder per scene, the catalogue, the sweep, `send` and `rows`. Each scene has its own test file, `tests/rota/test_scene_<name>.py`, so the gate's workers build the scenes side by side. The shared tests are in `tests/rota/scene_tests.py`: the catalogue's refusals, the sweep's landings, a check that the calls leave the scene's rows as built, and a second build whose rows must equal the first.

### How a scene is built

Through the ops, in this order: the principal's words by `record_entry`, the Liaison's `brief.segment` and `brief.ratify` and its delivers, the Vision Keeper's `problem.assert` and `problem.set_approval`, the Terminologist's `glossary.amend`, `tickets.slice`, `criteria.specify` and `batches.group` on the scheduler's own ticks, `lifecycle.start` with `harness.inherit`, the Developer's `code.write` and `code.commit`, the Tester's `tests.triage` and `tests.encode` on `tick:tests_missing`, `harness.run`, the Critic's `verdicts.emit` on `tick:review`, and `lifecycle.merge` or `lifecycle.defer`. Every session runs through `run_session` with `ScriptedBackend`. `drive` fails on any note of a session except the prompt's size note at 4096 and a cut note, so a door that starts to refuse a scene's script turns the scene red.

The raw rows and the stubs, each with its reason:

- The principal's messages and the Liaison's relay of the sign-off are rows, as in `test_arc_seam.py`. The principal is not a seat, and the gate that produces the relay is the principal's.
- `config.project_root` is a row, as in `test_arc_seam.py`. It is a fact about the repository and not a declared setting.
- The park's `batch_dep_facts` row (b1 before b3) is raw. No op in `rota/` writes that table (observed: no insert outside the schema, 2026-10-05).
- `provision.ensure_env` is a stub during `lifecycle.start` and `harness.run`. It lays a venv and runs pip, 8.5 s per start (observed: `time_seam.py`, 2026-10-05). The harness then uses rota's own interpreter, its fallback. No scene asserts on the environment.
- The scenes construct a few wakes directly, as `test_arc_seam.py` does: the Developer's `tick:batch_start`, the Architect's `tick:survey` on `src/billing` in S7, and a `tick:tests_failing` that the park dispatches with `note_dispatch`.

### The free columns

Under pytest the conftest pins git's clock, so the commit shas repeat between builds. Three readings of the clock remain, and `rows` names each:

- `test_runs.output` ends with pytest's run time. The duration becomes `in <t>s`.
- The fix wake pushes the red run's output, so the run time reaches `turns.user` and `turns.system` too. They get the same rule. `sessions.prompt_hash` and `sessions.pins_json` hash that prompt, so they are dropped.
- Onboarding writes `config.created_at`. Its value becomes `<t>`.

### The scenes

Build time is the module fixture's setup, and the second build is the equality test's call (observed: `pytest --durations` on the five files, five workers, 2026-10-05). The five files took 50.2 s of wall time together.

| Scene | Build, second build | The state | Proof: the fix removed, and what went red |
|---|---|---|---|
| S1 `two_batches` | 8.8 s, 6.3 s | Items 1 and 2. b1 starts, its Developer's commit turns `tests/test_charges.py` red, the harness runs, b1 is deferred, b2 starts and takes in the project's tests under the same ids. | Frame 135's project-id door, `api.py` `if project and (...)` made false. Both catalogue rows with the project's id landed: `the project id of test_charges at its own path` and `at a new path`. |
| S2 `merged_then_next` | 11.1 s, 9.0 s | b1 through the Developer, the Tester's root `test_upgrade.py`, a green harness, a pass verdict and the merge. b2 starts and takes in the delivered file. | Section 5 names none. The wall the state comes from: `lifecycle.merge`'s delivery of the Tester's bodies (`if tree and tests:` made false, click night 50). `test_the_delivered_test_is_a_project_test_of_b2` and the delivered-id catalogue row went red. |
| S5 `challenged` | 9.6 s, 7.6 s | t1 asserts the full price, the harness is red, the Developer's `msg.challenge_tester` quotes the criterion and the test, and the Tester's challenge wake replaces t1 under its stored id. | Section 5 names none. The wall the state comes from: `session_commit`'s `version = version + 1` on an amendment (`db.py`). `test_t1_is_at_version_2_and_green_on_the_same_commit` went red. |
| S3 and S4, `park` | 25.4 s, 23.2 s | Items 1 to 3. b1 makes five commits with a red harness after each (attempt 5 of 10). Three dispatches of its `tests_failing` wake with no commit, then `frontier` quarantines the key. The Vision Keeper raises item 2, the preempt defers b1, and the Liaison's `park_ask` session opens the ask. b2 and b3 are pending, b3 behind b1. | 0c6e54e's own `ask_parked` is gone from the tree. Its present form is the park ask's id that names the batch, `msg_id = park_ask_id(...)` in `sandbox.py`, from b23d17b. With that line made `pass`, `test_b1_is_parked_with_one_open_ask_and_b3_waits_behind_it` went red. |
| S7 `review` | 7.3 s, 5.1 s | Onboarding, then the Architect's survey of `src/billing` reads `charges.py` and binds the constraint "a charge is a whole number of cents". b1's Developer makes `prorate` divide without rounding and adds the upgrade module. The Tester's test asserts only a positive charge. The harness is green. | Section 5 names none. The wall the state comes from: "an unknown touch set is reviewed" (`lifecycle.needs_structural_review`, `return True` made `return False`). `test_the_structural_review_wake_shows_the_bound_constraint` went red. |

After each removal the file was restored from a copy, and its bytes equalled the bytes before. `git diff` shows nothing in `db.py` or `lifecycle.py` (observed: `C:/Users/roman/proofs.py`, 2026-10-05).

### The catalogue, 8 rows

| Scene | The call | The door, and the first words |
|---|---|---|
| S1 | b2's Tester encodes under `inh_db70e774` at `tests/test_charges.py` | `tests_encode`, "inh_db70e774 is the id of the project's test". The offer meets known finding 1, and `KNOWN_REFUSED_OFFERS` names it. |
| S1 | the same id at `tests/test_export.py` | `tests_encode`, the same words |
| S1 | b2's Developer writes `upgrade.py` with `RATE = upgrade_rate` at the top level (W146) | strict xfail, held by frame 146: the write lands |
| S2 | b2's Tester encodes under b1's merged id `t1` | `tests_encode`, "t1 is" |
| S2 | b2's Tester encodes under the delivered file's project id | `tests_encode`, "inh_ae5f34e8 is the id of the project's test". The offer meets known finding 1. |
| S5 | the Tester's challenge wake encodes `t2` for c1, which holds t1 (W138) | strict xfail, held by frame 144: no door refuses it, and no other frame names W138 (observed: `git log -S"W138"` finds frame 144's table only) |
| S7 | the Critic's fail on c1 with no claim | `verdicts_emit`, "a fail on c1 stands on its test actually encoding it" |
| S7 | the Architect's finding on a constraint that does not exist | `findings_find` |

The park has no catalogue row. Its file shows the parametrised test as skipped, "no row".

### The sweep, 47 right calls, all land

- S1, 43: each of the three project test files as a `tests.encode` body under a new id and path, after the triage, and for `test_templates.py` after the `ledger.log` that the literal door names. Each of the 20 sample modules that parse gets a whole write with a comment line on top and a span write of one comment line at 0. `src/auth/accounts.py` does not parse in the sample, so it has no right write.
- S7, 4: the Critic's `verdicts.claim_encodes(c1, False)` and `msg.challenge_tester` with both quotes. The Critic's fail after a claim of True. The Architect's `findings.find` with `violated`. The Developer's `msg.challenge_tester` with both quotes on `tick:tests_failing`.

The design named a Critic's `verdicts.emit` with `fail` as S7's right call. On this scene the test does not encode its criterion, so the door asks for the claim first, and a claim of False makes the right call a challenge. Both shapes are in the sweep.

### The strict xfails of part B, 3

- `test_scene_two_batches.py::test_every_run_names_a_test_of_its_own_batch`, held by frame 130: after b2 starts, all six runs of b1 name tests whose row is b2's.
- The W146 catalogue row, held by frame 146.
- The W138 catalogue row, held by frame 144.

## The suite

The touched files of part A pass: `test_offers_followed.py`, `test_toolproto_fuzz.py`, `test_desk_guards.py`, `test_t0_sandbox.py`, `test_night46_context.py`, `test_touch_divergence.py` and `test_viewer.py`, 450 passed and 7 xfailed. The five scene files: 68 passed, 4 skipped and 3 xfailed in 50.2 s (observed: 2026-10-05).

The gate on the tree of both commits (observed: `python -m rota.tools.gate`, 2026-10-05):

```
suite: 24 failed, 2853 passed, 34 skipped, 11 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (4): tests/rota/test_handover.py::test_a_confirmed_hand_off_waits_for_the_receiver, tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 636.6s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The gate marked `test_handover.py::test_a_confirmed_hand_off_waits_for_the_receiver` flaky: it passed on the gate's own rerun. Its file passed alone afterwards, 53 passed. The other three new reds are the three that the brief expects.

## Deviations

- `provision.ensure_env` is a stub in every scene, for the time reason above.
- S7 binds its constraint in an Architect survey after onboarding, and not in the deliver wake. The deliver mode has no `code.source`, and `model.amend` binds only a file the session read.
- S5's run history is one row: the harness keeps one run of a test at a commit, so the pass of version 2 replaced the fail of version 1.
- The park's proof removes b23d17b's line and not a line of 0c6e54e, because 0c6e54e's code is no longer in the tree.
- The W138 row is held by frame 144, because no other frame names W138.
- The proofs ran with `-n0` on the scene file alone.

## Seen and not fixed

- **A stale call log can reach a session.** The reproduction above: one process, a reader that never drains, and a later `ctx` at the freed address drains the reader's calls into its `tool_calls`. `rota/cockpit/progress.py` is such a reader. Not proved to share a process with a session.
- **The fix wake's prompt holds pytest's run time.** The red run's output ends with "in 0.12s", and the push carries it, so two runs of one state give two prompts and two cassette keys (observed: the park's two builds, `turns.user` of the Developer's `tests_failing` sessions, 2026-10-05).
- **`test_arc_seam.py` ignores its own sessions' refusals.** Its Terminologist sends `glossary.amend(id='g1', ...)`, which the binder refuses for the unknown argument `id`. `drive` there checks `committed` only.
- **A fail verdict with no `failed_criterion` lands** on the review scene. The catalogue does not hold it, because this pass found no ruling that names it wrong.
- **The gate's flaky red**, `test_a_confirmed_hand_off_waits_for_the_receiver`. The scene files add git and subprocess load to the workers. This pass did not read that test.

## Where things are

Part B is whole for the scenes that this pass owns. Scene 6, the module of 1,000 lines with the four wakes, and the nine invariants are the next passes, by the brief. The scene files' tests are the place for an invariant check: each module fixture holds `ids["rows"]`, and `scenes.rows` gives every table.
