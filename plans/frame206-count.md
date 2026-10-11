# Frame 206 count: where the gate's workers wait

The count agent's report, Opus, 2026-10-11, session 59bdd13a. Meta
workflow. One full run of `tests` at `-n 16 -p no:cacheprovider` with the
plugin `c206_count.py`, from the worktree `C:/Users/roman/rota_c206` at
3f2e974e, with the gate's environment: `ROTA_MODEL=qwen3:8b`, `CI=1`,
`TMPDIR`, `TEMP` and `TMP` on `C:/Users/roman/rota_gate/tmp`, and the four
recording names and `PYTEST_ADDOPTS` unset. The ini adds `-n auto --dist
loadfile`, and `-n 16` wins. Result: 4 failed, 3391 passed, 198 skipped,
19 xfailed, in 468.9s (observed: `run_all.log`, 2026-10-11 16:55). The
recorded cases skip, because the worktree has no `cassettes.db`. Other
work shared the machine, so seconds are loaded. The raw JSON (one file per
worker), the plugin, the reader `c206_read.py` and the log are under
`C:\Users\roman\AppData\Local\Temp\claude\d--repos-rota\59bdd13a-98f3-4dda-ba43-071cb487b114\scratchpad\c206\`.

## Headline

1. The run is one worker long (observed). Worker gw0 holds
   `tests/rota/test_developer.py` from 38s to 466s, because `--dist
   loadfile` keeps a file on one worker. The other 15 workers end between
   138s and 229s. The 16 workers use 3138s of the 7456 worker-seconds the
   run holds, 0.42. So most of the idle CPU that the machine shows is
   workers with no work, not workers that wait.
2. Inside a worker's own wall, spawn wait is the largest part: 0.47.
   Process CPU is 0.19. Sleeps are 0.005. The rest, 0.33, is wait that no
   wrapper saw (reasoned: file IO in SQLite and fixture copies, the asyncio
   loop of the Textual tests, and HTTP reads, see below).
3. In `test_developer.py`, 28 tests each lay a fresh venv and run pip
   through `rota/core/provision.py` `ensure_env`: 28 `python -m venv`
   (166s) and 28 `python -m pip` (160s) on gw0 alone. That is 326s of
   gw0's 466s.
4. Git is 6392 spawns and 646s, 0.21 of worker wall, 60ms to 300ms each.
5. Sleeps do not matter. The main threads sleep 16.8s in all, most of it
   in `tests/rota/test_handover.py:71`.

## Method and its limits

- Wait is wall minus `time.process_time` of the worker process. The
  process time counts every thread of the worker.
- Spawn wait runs from the start of `Popen.__init__` to the first return
  of `wait` or `communicate`. Only spawns on the main thread go into a
  test's numbers. A sleep inside a spawn wrapper is not counted again.
- The sleep wrappers do not see `recv_into`, which `http.client` uses
  through `socket.makefile`. They also do not see the Windows asyncio
  proactor, lock waits or `Thread.join`. These waits fall in "rest".
- The fixture table counts each fixture's own setup body. The setup of
  nested fixtures is removed from the parent.
- The phase timeline uses `time.time`. A test in `test_handover.py`
  patches the clock, so gw14's last phase reads 86444s. That value is an
  artefact. gw14's process ended at 176s, and the tail table counts its
  60s in the window from the same artefact.
- `tests/rota/test_principal_reply.py` calls the live server at
  `http://127.0.0.1:11434/api/chat` in `_tokens` (line 205, observed in
  the source). The two tests of that file wait 69.5s with 0.4s CPU. The
  brief said to call no model. The suite made this call itself, and the
  count could not stop it without an edit to the test.

## Tables

### totals

| measure | seconds | fraction of worker wall |
|---|---|---|
| worker wall | 3138.0 | 1.000 |
| process CPU | 599.8 | 0.191 |
| spawn wait | 1484.0 | 0.473 |
| sleep wait | 16.8 | 0.005 |
| rest | 1037.4 | 0.331 |
| inside test phases, wall | 2766.5 | 0.882 |
| inside test phases, CPU | 411.2 | 0.131 |
| outside test phases (collect, idle) | 371.5 | 0.118 |
| spawn wait outside phases | 29.0 | 0.009 |
| sleep wait outside phases | 2.7 | 0.001 |

per worker: gw0 466/50/466, gw1 138/32/138, gw2 165/25/165, gw3 149/26/150, gw4 145/60/145, gw5 191/38/192, gw6 192/39/193, gw7 228/69/229, gw8 201/36/202, gw9 214/37/216, gw10 192/25/194, gw11 186/33/189, gw12 181/40/184, gw13 183/30/187, gw14 172/29/176, gw15 134/32/138

### top 20 tests by wait (wall minus CPU)

| test | wall | CPU | wait | spawn | sleep | rest | spawns |
|---|---|---|---|---|---|---|---|
| `tests/rota/test_scene_park.py::test_b1_is_parked_with_one_open_ask_and_b2_waits` | 71.9 | 4.3 | 67.6 | 46.1 | 0.0 | 21.5 | 165 |
| `tests/rota/test_screens.py::test_no_key_breaks_on_a_seat_with_no_run` | 65.1 | 4.7 | 60.4 | 0.2 | 0.0 | 60.2 | 1 |
| `tests/rota/test_arc_seam.py::test_one_sentence_becomes_a_merged_batch` | 64.3 | 7.4 | 56.9 | 53.9 | 0.0 | 3.0 | 50 |
| `tests/rota/test_developer.py::test_a_second_run_on_the_same_root_gets_a_fresh_worktree` | 51.7 | 1.6 | 50.2 | 48.2 | 0.0 | 2.0 | 18 |
| `tests/rota/test_provision.py::test_ensure_env_lays_an_interpreter_that_has_pytest` | 48.3 | 0.0 | 48.3 | 48.3 | 0.0 | -0.0 | 4 |
| `tests/rota/test_scene_two_batches_again.py::test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op` | 52.8 | 4.8 | 48.0 | 29.6 | 0.0 | 18.4 | 144 |
| `tests/rota/test_scene_large_module.py::test_every_session_of_the_scene_ran_at_the_nights_window` | 52.1 | 4.4 | 47.8 | 36.6 | 0.0 | 11.1 | 126 |
| `tests/rota/test_scene_large_module_again.py::test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op` | 52.0 | 4.8 | 47.2 | 29.4 | 0.0 | 17.8 | 109 |
| `tests/rota/test_greenfield.py::test_a_merged_batch_lands_on_the_base_branch` | 47.2 | 0.3 | 46.9 | 46.8 | 0.0 | 0.1 | 21 |
| `tests/rota/test_scene_two_batches.py::test_b1_failed_the_project_test_and_b2_took_the_project_tests_in` | 50.1 | 4.7 | 45.4 | 35.8 | 0.0 | 9.6 | 161 |
| `tests/rota/test_invariants.py::test_the_scenes_end_breaks_only_the_known_invariant` | 42.7 | 3.7 | 39.0 | 33.0 | 0.0 | 5.9 | 114 |
| `tests/rota/test_scene_merged_then_next.py::test_the_delivered_test_is_a_project_test_of_b2` | 40.8 | 4.1 | 36.7 | 31.3 | 0.0 | 5.3 | 102 |
| `tests/rota/test_scene_challenged_again.py::test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op` | 38.7 | 2.6 | 36.1 | 16.8 | 0.0 | 19.4 | 41 |
| `tests/rota/test_principal_reply.py::test_the_landing_wake_for_a_77_line_present_fits_the_window` | 34.8 | 0.2 | 34.6 | 0.0 | 0.0 | 34.6 | 0 |
| `tests/rota/test_scene_challenged.py::test_t1_is_at_version_2_and_green_on_the_same_commit` | 33.3 | 3.0 | 30.4 | 25.2 | 0.0 | 5.2 | 58 |
| `tests/rota/test_index_refresh.py::test_a_path_grain_carries_no_span` | 30.5 | 0.3 | 30.3 | 2.1 | 0.0 | 28.2 | 6 |
| `tests/rota/test_developer.py::test_dispatch_creates_the_worktree` | 31.3 | 1.5 | 29.9 | 28.3 | 0.0 | 1.6 | 22 |
| `tests/rota/test_developer.py::test_a_deferred_batch_keeps_its_worktree_and_commits` | 31.0 | 2.0 | 29.1 | 25.8 | 0.0 | 3.3 | 13 |
| `tests/rota/test_register_key.py::test_end_to_end_the_door_stops_a_real_run` | 28.0 | 0.0 | 28.0 | 27.9 | 0.0 | 0.1 | 3 |
| `tests/rota/test_developer.py::test_the_repositorys_own_tests_join_the_batch` | 29.0 | 1.0 | 28.0 | 24.9 | 0.0 | 3.1 | 11 |

### top 15 files by wait

| file | wall | CPU | wait | spawn | sleep | rest | spawns |
|---|---|---|---|---|---|---|---|
| `tests/rota/test_developer.py` | 427.5 | 35.5 | 392.0 | 379.1 | 0.0 | 12.9 | 508 |
| `tests/rota/test_onboarding_phases.py` | 168.8 | 27.0 | 141.8 | 27.1 | 0.0 | 114.7 | 314 |
| `tests/rota/test_screens.py` | 158.9 | 29.0 | 129.9 | 8.5 | 1.3 | 120.1 | 52 |
| `tests/rota/test_index_refresh.py` | 108.1 | 11.1 | 96.9 | 34.0 | 0.0 | 63.0 | 229 |
| `tests/rota/test_onboarding.py` | 112.1 | 20.9 | 91.2 | 17.7 | 0.0 | 73.5 | 198 |
| `tests/rota/test_arc_seam.py` | 89.3 | 13.5 | 75.8 | 73.1 | 0.0 | 2.8 | 128 |
| `tests/rota/test_scene_park.py` | 75.5 | 4.8 | 70.6 | 48.5 | 0.0 | 22.1 | 255 |
| `tests/rota/test_desk_guards.py` | 82.7 | 12.3 | 70.5 | 28.0 | 0.0 | 42.5 | 324 |
| `tests/rota/test_principal_reply.py` | 69.9 | 0.4 | 69.5 | 0.0 | 0.0 | 69.5 | 0 |
| `tests/rota/test_invariants.py` | 74.1 | 6.7 | 67.3 | 62.6 | 0.0 | 4.7 | 558 |
| `tests/rota/test_greenfield.py` | 67.1 | 0.7 | 66.4 | 66.2 | 0.0 | 0.2 | 55 |
| `tests/rota/test_scene_two_batches.py` | 66.0 | 7.3 | 58.7 | 48.6 | 0.0 | 10.1 | 374 |
| `tests/rota/test_scene_large_module.py` | 59.6 | 5.3 | 54.3 | 43.8 | 0.0 | 10.6 | 246 |
| `tests/rota/test_provision.py` | 48.4 | 0.0 | 48.3 | 48.3 | 0.0 | 0.0 | 4 |
| `tests/rota/test_scene_two_batches_again.py` | 52.8 | 4.8 | 48.0 | 29.6 | 0.0 | 18.4 | 144 |

### by phase

| phase | wall | CPU | spawn | sleep |
|---|---|---|---|---|
| setup | 711.5 | 91.4 | 311.1 | 0.0 |
| call | 1975.1 | 286.0 | 1142.1 | 13.5 |
| teardown | 79.9 | 33.8 | 1.8 | 0.6 |

### top 10 fixtures by setup wait (own body, nested fixtures removed)

| fixture | scope | setups | wall | CPU | wait | spawn | sleep | rest | top file by wait |
|---|---|---|---|---|---|---|---|---|---|
| `scene` | module | 5 | 248.2 | 20.4 | 227.7 | 175.1 | 0.0 | 52.7 | `tests/rota/test_scene_park.py` |
| `db` | function | 1190 | 120.0 | 13.3 | 106.7 | 12.4 | 0.0 | 94.3 | `tests/rota/test_desk_guards.py` |
| `project` | function | 176 | 104.1 | 22.4 | 81.7 | 21.3 | 0.0 | 60.3 | `tests/rota/test_onboarding_phases.py` |
| `world` | function | 26 | 63.7 | 6.5 | 57.2 | 15.8 | 0.0 | 41.4 | `tests/rota/test_index_refresh.py` |
| `built` | module | 1 | 41.3 | 3.7 | 37.6 | 31.7 | 0.0 | 5.9 | `tests/rota/test_invariants.py` |
| `night128` | function | 19 | 39.0 | 3.3 | 35.6 | 32.0 | 0.0 | 3.7 | `tests/rota/test_prints_door_kind.py` |
| `critic` | module | 1 | 25.0 | 2.6 | 22.4 | 16.0 | 0.0 | 6.4 | `tests/rota/test_scene_review.py` |
| `tmp_path` | function | 2187 | 18.0 | 6.5 | 11.5 | 0.0 | 0.0 | 11.5 | `tests/rota/test_desk_guards.py` |
| `s279` | function | 24 | 10.6 | 1.6 | 9.1 | 0.8 | 0.0 | 8.3 | `tests/rota/test_verdict_lines.py` |
| `repo` | function | 13 | 6.6 | 2.2 | 4.4 | 1.2 | 0.0 | 3.1 | `tests/rota/test_gitfixture.py` |

### spawns by command (all threads; main thread)

| command | count | wall | main count | main wall | ms each |
|---|---|---|---|---|---|
| `python -m pytest` | 239 | 334.0 | 239 | 334.0 | 1397 |
| `python -m pip` | 34 | 264.8 | 34 | 264.8 | 7787 |
| `python -m venv` | 33 | 213.2 | 33 | 213.2 | 6460 |
| `git rev-parse` | 2001 | 133.1 | 1858 | 123.8 | 67 |
| `git commit` | 404 | 121.8 | 404 | 121.8 | 301 |
| `git worktree` | 343 | 66.5 | 343 | 66.5 | 194 |
| `git add` | 384 | 64.3 | 384 | 64.3 | 168 |
| `git diff` | 752 | 53.9 | 752 | 53.9 | 72 |
| `git show` | 740 | 50.8 | 740 | 50.8 | 69 |
| `git merge-base` | 578 | 33.7 | 578 | 33.7 | 58 |
| `git status` | 407 | 31.3 | 407 | 31.3 | 77 |
| `git init` | 179 | 29.6 | 179 | 29.6 | 165 |
| `git cat-file` | 144 | 22.4 | 144 | 22.4 | 155 |
| `git ls-files` | 269 | 20.6 | 267 | 20.4 | 76 |
| `python -c` | 13 | 16.7 | 13 | 16.7 | 1286 |
| `powershell -NoProfile` | 22 | 13.8 | 22 | 13.8 | 629 |
| `git branch` | 85 | 6.8 | 85 | 6.8 | 80 |
| `git merge` | 13 | 4.9 | 13 | 4.9 | 375 |
| `git config` | 65 | 4.4 | 65 | 4.4 | 68 |
| `ver` | 15 | 3.3 | 15 | 3.3 | 220 |

all spawns: 6755, wall 1493.5

### spawn sites, top 15 by wall (main thread)

| command | site | count | wall |
|---|---|---|---|
| `python -m pip` | `rota/core/execute.py:38` | 34 | 264.8 |
| `python -m pytest` | `rota/core/execute.py:38` | 215 | 260.9 |
| `python -m venv` | `rota/core/execute.py:38` | 33 | 213.2 |
| `git commit` | `rota/testkit/samplerepo.py:778` | 98 | 33.2 |
| `git status` | `rota/core/worktrees.py:216` | 400 | 30.8 |
| `git worktree` | `rota/testkit/gitfixture.py:48` | 230 | 30.4 |
| `python -m pytest` | `tests/rota/test_caught.py:112` | 18 | 28.5 |
| `python -m pytest` | `tests/rota/test_register_key.py:435` | 3 | 27.9 |
| `git rev-parse` | `rota/core/worktrees.py:163` | 409 | 27.8 |
| `git rev-parse` | `rota/onboarding/boot.py:73` | 374 | 27.6 |
| `git show` | `tests/rota/test_prints_door_kind.py:42` | 320 | 26.2 |
| `git worktree` | `rota/core/worktrees.py:36` | 66 | 24.0 |
| `git commit` | `rota/core/worktrees.py:191` | 76 | 22.5 |
| `git merge-base` | `rota/tools/invariants.py:76` | 382 | 22.2 |
| `git show` | `rota/tools/invariants.py:76` | 382 | 21.0 |

### sleeps by call site, main thread, top 15

| kind | site | count | wall |
|---|---|---|---|
| time.sleep | `tests/rota/test_handover.py:71` | 295 | 8.2 |
| Event.wait | `<string>:8` | 265 | 4.3 |
| time.sleep | `rota/tools/handover.py:900` | 73 | 2.0 |
| time.sleep | `rota/tools/handover.py:246` | 12 | 0.7 |
| Event.wait | `tests/rota/test_handover.py:107` | 39 | 0.6 |
| Event.wait | `tests/rota/test_refs.py:811` | 1 | 0.5 |
| time.sleep | `tests/rota/test_handover.py:118` | 3 | 0.2 |
| time.sleep | `tests/rota/test_handover.py:141` | 2 | 0.1 |
| time.sleep | `tests/rota/test_handover.py:743` | 1 | 0.1 |
| time.sleep | `tests/rota/test_llm_stream.py:21` | 3 | 0.1 |
| time.sleep | `tests/rota/test_handover.py:804` | 1 | 0.1 |
| time.sleep | `tests/rota/test_handover.py:802` | 1 | 0.1 |
| Event.wait | `tests/rota/test_chaos_onboarding.py:135` | 2 | 0.0 |
| Event.wait | `tests/rota/test_handover.py:258` | 1 | 0.0 |
| time.sleep | `rota/tools/handover.py:1021` | 1 | 0.0 |

total main thread: 953 calls, 16.8s

### sleeps by call site, background threads, top 15

| kind | site | count | wall |
|---|---|---|---|
| time.sleep | `rota/tools/handover.py:720` | 4275 | 116.0 |
| Condition.wait | `rota/cockpit/screens.py:203` | 33 | 7.1 |
| Condition.wait | `rota/cli.py:244` | 10 | 0.9 |
| Event.wait | `threading.py:1383` | 1 | 0.8 |
| select.select | `selectors.py:305` | 2 | 0.6 |
| time.sleep | `rota/tools/handover.py:900` | 10 | 0.2 |
| time.sleep | `tests/rota/test_handover.py:71` | 7 | 0.2 |
| Event.wait | `rota/cli.py:244` | 5 | 0.1 |
| Condition.wait | `rota/cockpit/tui.py:479` | 4 | 0.0 |
| Event.wait | `threading.py:1011` | 1 | 0.0 |
| socket.accept | `socketserver.py:511` | 1 | 0.0 |
| Event.wait | `rota/cockpit/tui.py:716` | 2 | 0.0 |

total background threads: 4351 calls, 125.9s

### serial tail: last 60 s of the run

run end 465.9s after the first worker start; window from 405.9s

| worker | ends at | busy in window | tests in window (seconds in window) |
|---|---|---|---|
| gw0 | 466 | 60 | `test_developer.py::test_a_red_run_names_the_files_changed_since_it` 15, `test_developer.py::test_a_passing_test_says_nothing` 13, `test_developer.py::test_a_finding_names_a_file_the_diff_changed` 12 |
| gw1 | 138 | 0 |  |
| gw2 | 165 | 0 |  |
| gw3 | 150 | 0 |  |
| gw4 | 145 | 0 |  |
| gw5 | 192 | 0 |  |
| gw6 | 193 | 0 |  |
| gw7 | 229 | 0 |  |
| gw8 | 202 | 0 |  |
| gw9 | 216 | 0 |  |
| gw10 | 194 | 0 |  |
| gw11 | 189 | 0 |  |
| gw12 | 184 | 0 |  |
| gw13 | 187 | 0 |  |
| gw14 | 176 | 60 | `test_handover.py::test_a_wall_clock_step_does_not_end_a_wait` 60 |
| gw15 | 138 | 0 |  |

### per worker: last test start, last test end

- gw0: last phase ends 466s, `tests/rota/test_developer.py::test_the_drops_refusal_names_the_insert_at_top_span`
- gw1: last phase ends 138s, `tests/rota/test_survey_door.py::test_a_constraint_outside_a_survey_may_be_global`
- gw2: last phase ends 165s, `tests/rota/test_scene_park.py::test_the_calls_leave_the_scene_as_it_was_built`
- gw3: last phase ends 150s, `tests/rota/test_invariants.py::test_a_night_is_checked_by_path_and_left_as_it_was`
- gw4: last phase ends 145s, `tests/rota/test_chaos_inquiry.py::test_a_corrupted_report_does_not_kill_the_frontier`
- gw5: last phase ends 192s, `tests/rota/test_schema_has_no_clock.py::test_no_table_carries_a_clock_column`
- gw6: last phase ends 193s, `tests/rota/test_onboarding_phases.py::test_reconcile_reads_each_docs_file_as_its_own_area`
- gw7: last phase ends 229s, `tests/rota/test_scene_park_again.py::test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op`
- gw8: last phase ends 202s, `tests/rota/test_scene_review_again.py::test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op`
- gw9: last phase ends 216s, `tests/rota/test_arc_seam.py::test_a_failing_test_comes_back_and_the_second_commit_is_what_merges`
- gw10: last phase ends 194s, `tests/rota/test_progress.py::test_the_block_reads_the_stage_the_count_and_the_reference`
- gw11: last phase ends 189s, `tests/rota/test_index_refresh.py::test_a_refresh_that_works_ends_the_note_the_failed_one_left`
- gw12: last phase ends 184s, `tests/rota/test_screens.py::test_the_seats_own_run_is_recognised_however_it_was_spelled`
- gw13: last phase ends 187s, `tests/rota/test_toolproto_fuzz.py::test_the_slice_holds_frame_122s_prose_with_apostrophes`
- gw14: last phase ends 86444s, `tests/rota/test_handover.py::test_a_wall_clock_step_does_not_end_a_wait`
- gw15: last phase ends 138s, `tests/rota/test_vertical_slice.py::test_understanding_loop_live`

## Three levers

Each number is reasoned from the tables above. The run's wall is the
latest worker's end, so a lever recovers run wall only when it moves
that worker.

1. **Lay the Developer test venv once** (tests: `tests/rota/test_developer.py`,
   35 tests, and `tests/rota/test_provision.py`; site: the `ensure_env`
   path through `rota/core/execute.py:38`). One session venv, copied or
   shared, removes about 26 of the 28 venv and pip pairs on gw0, about
   300s of 326s. The file then takes about 125s, and gw0 ends near 165s.
   The run then ends at the next worker, gw7 at 229s. Recovered run wall:
   about 237s of 466s, 0.51. Splitting the file across workers (for
   example `--dist loadgroup` with groups inside the file) recovers the
   same tail without the venv change, but spends the same 326s of worker
   time on other workers.
2. **Cut git spawns in the scene and worktree fixtures** (tests: the
   `scene` fixture, 5 module setups, 175s spawn; `built`, `critic`,
   `night128`; the files `test_scene_*`, `test_invariants.py`,
   `test_arc_seam.py`, 704s wall and 503s spawn; sites
   `rota/testkit/samplerepo.py:778`, `rota/testkit/gitfixture.py:48`,
   `rota/core/worktrees.py:163,191,216`, `rota/tools/invariants.py:76`).
   Frame 203's template cut a file's git calls from 311 to 131. The same
   ratio on 646s of git recovers about 370s of worker time, about 23s of
   run wall at 16 workers after lever 1. Before lever 1, it moves the run
   wall by 0s, because gw0 holds the tail.
3. **Copy a template database in the `db` fixture** (1190 setups, 120s
   wall, 107s wait, 94s of it rest; heaviest in
   `tests/rota/test_desk_guards.py`; also the `project` fixture, 176
   setups, 82s wait). Frame 203 measured 140ms to 4.8ms for `init_db` on
   a copied template. That recovers about 110s of worker time, about 7s
   of run wall at 16 workers after lever 1, and 0s before it.

Two smaller items are outside the three levers. `test_principal_reply.py`
waits 69.5s on the live model server, and that wait grows when a night
holds the card. `test_screens.py` waits 120s in the Textual loop, with
`test_no_key_breaks_on_a_seat_with_no_run` at 60s alone.
