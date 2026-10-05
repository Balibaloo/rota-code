# Frame 144: the table of the structure, from the code

Meta workflow. Pass 0 of frame 144, the night databases are not a test tier. One agent on Opus read the code and the suite on 2026-10-05. No model ran, no gate ran, and no file outside this record and `plans/frame144-design.md` changed.

The table maps the structure's side of rota: every op a seat can call and each door on it (part A), every wake block and the cut (part B), and every state and move of a batch, a test, a key and an ask (part C). The columns are the ways a row can fail. Each cell says what holds that failure today or after frame 144.

## How the table was built

- Modes and ops: the 83 `.tools` files under `rota/roles/prompts/` name 89 api ops and 32 `msg.*` ops (observed: a scratchpad script, `f144/doors.py`, 2026-10-05).
- Doors: every `raise` site with its text, in the op function and in the helpers it calls inside `api.py`, plus `_bind_send` and its evidence helpers in `rota/core/sandbox.py`, plus the per-call doors in `run_session` of `rota/core/runner.py` (observed: `f144/doors.py` and a read of `runner.py` lines 2900 to 3550, 2026-10-05). `api.py` holds 202 `raise ValueError` and 20 `raise Wall` (observed: grep, 2026-10-05).
- Coverage: a script searched `tests/rota/*.py` for every four-word run of each refusal's literal text (observed: `f144/cover.py`, 2026-10-05). A hit is a test that quotes the refusal. For `code.write`, `tests.encode`, `code.commit` and the runner, the agent then read the test names and judged each door by hand. Some script hits are false matches, and those were dropped where read.
- Wakes: `build_prompt` (`runner.py:334`), `push_working_set` (`runner.py:2134`), `_fit` and `_pack` (`runner.py:907` and `998`) were read in full (observed, 2026-10-05).
- States: the CHECK columns of `rota/core/schema.sql`, `rota/core/lifecycle.py`, the park and quarantine functions of `rota/core/scheduler.py`, `harness.inherit`, and the predicate registry, printed live (observed, 2026-10-05).

## Marks

- **T**: a test in the suite holds the cell. The cell names the test.
- **P1** to **P5**: an item of frame 144's ends-when holds it. **P3-S1** to **P3-S6** name a scene of item 3, and **P3-cat** names item 3's catalogue of wrong calls.
- **N**: nothing holds it.
- **n/a**: the failure cannot occur on this row.
- **Wnnn**: a known wall of frame nnn, from `plans/frame144-inventory.md`, section 2.

Test file abbreviations: `dg` test_desk_guards, `sb` test_t0_sandbox, `n46` test_night46_context, `rn` test_runner, `nb` test_next_batch, `td` test_touch_divergence, `tf` test_triage_fork, `dl` test_delivery, `fr` test_frontier, `pr` test_predicates, `ps` test_pushes, `rc` test_render_cut, `dv` test_developer, `as` test_arc_seam, `pm` test_prompts, `ce` test_challenge_evidence, `ic` test_intake_fork, `tp` test_t0_parser.

Scenes of item 3 (copied: `plans/stack.md`, frame 144's ends-when): S1 two batches that share the project's tests. S2 a merged batch whose Tester file is a project test of the next batch. S3 a batch at attempt 5 of 10 with a quarantined key beside two pending batches. S4 a parked batch with its park ask. S5 a test at version 2 after an answered challenge. S6 a module of 1,000 lines with a `__future__` header and a wake at the window of 16384.

A P3-S cell has a condition. The scene builds the state, and the cell is held only when a test asserts on that state: the scene's own proving test, or item 4's invariants run on the scene. Items 3 and 4 as written do not name those assertions. The design file lists the ones each scene needs.

A cell marks P only where the item's text, as written today, reaches the cell. Item 1 is "followed through frame 136's dry run". Only `code.write` has a dry run (observed: `_admits`, `api.py:9022`, its one caller family, 2026-10-05). So P1 is marked on `code.write` doors only. The design file proposes the change that widens it.

## Part A. Ops and doors

Columns: **AW** the door admits a wrong call. **RR** the door refuses a right call. **FF** the refusal states a false fact. **NC** the refusal names a next call that the doors refuse or that harms.

For AW, T means a test sends the wrong call of the door's own shape and sees the refusal. A wrong call of another shape that the door misses is a new row, as for W138. FF is n/a when the refusal states only the condition that raised it. FF is N when the refusal computes a fact from the state, such as lines, names, runs or paths, and no test checks that fact against the state. NC is n/a when the refusal names no call.

### A1. `code.write` (`code_write` at `api.py:8997`, body `_code_write` at `api.py:9044`)

14 modes carry `code.write`. 30 distinct refusal sites, and 2 sites that write a note and never refuse. Each door is checked by hand.

| Door | Line | AW | RR | FF | NC |
|---|---|---|---|---|---|
| "batch {} has no worktree" (`_batch_worktree`) | 8766 | N | n/a | n/a | n/a |
| "no batch: code is written in a batch's worktree" | 9054 | T `dg::test_code_is_written_in_a_batch_or_not_at_all` | n/a | n/a | n/a |
| "{} escapes the worktree" (`_within`) | 8940 | T `dv::test_a_write_cannot_escape_the_worktree` | P3-cat (a backslash path) | n/a | n/a |
| "{} is the name of the argument, not a file" | 9063 | T `td::test_a_placeholder_path_and_an_empty_write` | N | n/a | P1 |
| "start={} came with no end" | 9074 | T `dg::test_a_start_with_no_end_is_refused` | n/a | n/a | P1 |
| "an empty write to {} changes nothing" | 9094 | T `td::test_a_placeholder_path_and_an_empty_write` | T `dg::test_an_empty_span_removes_its_lines_and_an_empty_whole_write_removes_the_file` | n/a | P1 |
| "{} does not exist, so start={}, end={}" | 9113 | N | N | n/a | P1 |
| "start={}, end={} is not a span of {}" | 9120 | N | N | N | n/a |
| A boundary inside a statement (`_cut`, parts) | 9445 | T `dg::test_a_span_that_cuts_a_statement_is_told_where_the_boundaries_are` | T `dg::test_a_boundary_on_a_blank_line_between_statements_is_accepted` | T `dg::test_the_refusal_names_statements_with_the_words_of_the_source` | P1 |
| "Python refuses any statement above the `from __future__`" | 9472 | T `dg::test_an_insert_above_a_future_import_is_refused_with_the_line_after_it` | N | n/a | P1 |
| "line {} is the docstring of {}" | 9501 | T `dg::test_a_module_docstring_takes_no_insert_and_a_bare_string_is_no_docstring` | T same test, the bare-string half | n/a | P1 |
| Boundaries in two blocks (parts) | 9548 | T `dg::test_a_span_from_one_def_into_the_next_is_refused_with_both_edges` | T `n46::test_a_span_that_covers_whole_inner_statements_is_a_legal_edit` | N | P1 |
| The merge and the `dropped` note (`_tail_drop`, `_whole_drop`), never a refusal | 9558, 10286 | P3-cat (W140, a span that ends inside a def) | n/a | T `dg::test_a_span_write_that_stops_short_lands_and_says_what_it_drops` | n/a |
| "{} is a new module at the project root, and the project's package lives" | 9603 | N | N | n/a | n/a |
| "{} at the project root has the name of the standard-library module" | 9610 | T `dg::test_a_root_file_cannot_shadow_the_standard_library` | N | n/a | n/a |
| D: "Python takes {} only above every other statement" | 9690 | T `dg::test_a_future_import_below_another_line_is_told_to_go_first` | N | N | T `dg::test_a_span_refusal_names_no_call_the_doors_refuse` |
| Compile refusal "{} is not valid Python" | 9692, 9735 | T `dg::test_a_file_that_parses_and_does_not_compile_is_refused` | T `dg::test_a_broken_escape_in_an_indented_span_is_written_back` | T `dg::test_an_indented_span_that_does_not_parse_is_told_its_own_line` | n/a |
| "{} defines {} twice" | 9764 | T `dg::test_a_file_defines_each_name_once` | T `dg::test_an_overload_stub_is_not_a_second_definition` | N | n/a |
| "the tree already defines {} in {}" | 9820 | T `td::test_a_second_definition_of_a_name_the_tree_has_once_is_refused` | T `td::test_a_file_may_keep_a_name_it_already_defined` | N | n/a |
| The fence (`rota/core/fence.py`, `check` and `check_manifest`) | fence 136, 159 | T `dg::test_the_fence_holds_a_reach_no_criterion_names` | T `dg::test_the_fence_judges_the_change_not_the_file_it_was_made_in` | N | n/a |
| "{} is a test file, and the tests are the Tester's" | 9849 | T `dg::test_the_developer_writes_no_test_file_and_keeps_the_main_guard` | N | n/a | n/a |
| "{} is the program's entry point" (main guard) | 9869 | T `dg::test_the_developer_writes_no_test_file_and_keeps_the_main_guard` | N | N | P1 |
| "the `__main__` block of {} calls {}" | 9894 | N | N | N | n/a |
| "{} reads input() at module level" | 9917 | T `dg::test_module_level_input_through_a_local_function_is_refused` | T `n46::test_the_word_stdin_in_a_comment_does_not_stand_the_input_door_down` | n/a | n/a |
| "{} reads input() internally, and a test in this batch calls" | 9966 | T `dg::test_an_unshielded_test_refuses_a_reader_of_input` | T `dg::test_a_shielded_test_lets_a_reader_of_input_be_written` | N | n/a |
| "{} is the surface for a criterion that gets its value from the user" | 10026 | N | N | N | n/a |
| Drops `gone`, span: "To change {} alone, write only" | 10174 | T `dg::test_a_rewrite_may_not_delete_what_the_tests_import` | N | N | P1 |
| Drops `used`, whole file: "Either write the whole file" | 10185 | T `dg::test_a_whole_write_of_one_def_that_uses_the_dropped_helpers_is_refused` | T `dg::test_a_star_import_silences_the_used_check` | N | P1 |
| "this write changes {}, and no criterion of this batch names" | 10207 | T `n46::test_a_write_may_not_change_a_definition_no_criterion_names` | T `n46::test_a_private_helper_no_criterion_names_keeps_its_source` | N | P1 |
| "{} imports {} from {} at module level ... a cycle" | 10222 | T `n46::test_a_module_may_not_import_its_own_package_at_module_level` | N | n/a | n/a |
| A1 and A2, a span removes used lines (`_span_lost_refusal`, frame 136) | 10237 | T `dg::test_a_span_that_removes_used_imports_is_refused_with_the_insert` | T `dg::test_a_star_import_or_a_builtin_keeps_the_span_door_silent` | T `dg::test_a_span_that_removes_used_imports_is_refused_with_the_insert` | T `dg::test_a_span_refusal_names_no_call_the_doors_refuse` |
| "the batch's tests import {} and no such module exists yet" | 10240 | T `dg::test_the_written_module_is_told_what_the_tests_import` | N | N | n/a |
| "{} is not where `import {}` looks" | 10250 | N | N | N | n/a |
| A missing door: the top level of a written module loads a name that it does not bind (W146) | none | N (W146) | n/a | n/a | n/a |
| A missing door: a wrong binding of an old name passes the span predicate (`plans/frame136-design.md`, section 6) | none | N | n/a | n/a | n/a |

### A2. `code.commit` (`code_commit` at `api.py:10396`)

14 modes. 5 sites, each checked by hand.

| Door | Line | AW | RR | FF | NC |
|---|---|---|---|---|---|
| "no batch: a commit belongs to one" | 10411 | N | n/a | n/a | n/a |
| "the tree does not define {}, the surface the criteria name" | 10469 | T `dg::test_a_commit_defines_the_surface_the_criteria_name` | N | N | n/a |
| "this commit puts the tree back where it stood" (the revert door) | 10492 | T `dg::test_a_commit_that_undoes_the_last_one_is_churn` | N | N ("the tests pass both ways" is false, wall 5 of `plans/frame136-design.md`) | n/a |
| "nothing changed, and the finding stands" | 10509 | T `dg::test_an_empty_commit_under_a_finding_names_the_signature_drift` | T `dv::test_committing_nothing_says_so_rather_than_inventing_a_commit` | N | N |
| "batch {} has no worktree" (shared) | 8766 | N | n/a | n/a | n/a |
| A missing door: a commit in the reply after a `dropped` note lands (W140) | none | P3-cat (W140) | n/a | n/a | n/a |

### A3. `tests.encode` (`tests_encode` at `api.py:4679`)

6 modes. 33 distinct sites, each checked by hand against the test names.

| Door | Line | AW | RR | FF | NC |
|---|---|---|---|---|---|
| "{} was triaged {} in this session. A routed criterion gets no test" | 4709 | T `tf::test_a_routing_verdict_does_not_license_an_encode` | T `tf::test_a_claimed_criterion_encodes` | n/a | N |
| "{} has no triage verdict from you yet. Call tests.triage" | 4718 | T `tf::test_an_encode_with_no_branch_claim_is_refused` | T `tf::test_a_claimed_criterion_encodes` | n/a | N |
| "path {} is not a Python file" | 4732 | N | N | n/a | n/a |
| "the body is not Python" (Wall) | 4738 | N | N | N | n/a |
| "pytest will collect nothing from this body" (Wall) | 4748 | N | N | n/a | n/a |
| "this test calls input(), and pytest captures stdin" (Wall) | 4765 | T `dg::test_a_test_that_reads_stdin_cannot_pass_under_pytest` | T `dg::test_a_shielded_test_of_a_reader_of_input_is_encoded` | n/a | N |
| "this test closes sys.stdin" (Wall) | 4781 | T `n46::test_a_test_that_closes_stdin_is_refused` | T `n46::test_replacing_sys_stdin_by_assignment_satisfies_the_input_door` | n/a | N |
| "{}() reads input() through {}, a name {} bound to input" (Wall) | 4857 | T `n46::test_a_function_reading_input_by_another_name_is_seen` | N | N | N |
| "{}() reads input() internally ({}), and this test calls" (Wall) | 4867 | T `dg::test_an_unshielded_test_of_a_reader_of_input_is_refused` | T `dg::test_a_shielded_test_of_a_reader_of_input_is_encoded` | N | N |
| "the test uses {} and never imports it" (Wall) | 4954 | T `n46::test_a_library_module_never_imported_gets_the_line_to_add` | T `dg::test_a_name_the_body_defines_is_not_an_unimported_one` | N | N |
| "the test uses {} and never imports or defines it", surface named (Wall) | 4978 | T `dg::test_an_unbound_name_is_told_the_import_the_surface_names` | T `dg::test_a_name_the_body_defines_is_not_an_unimported_one` | N | N |
| "the test uses {} and never imports or defines it" (Wall) | 4983 | T `dg::test_a_name_the_test_never_imports_is_a_nameerror` | T `dg::test_a_name_the_body_defines_is_not_an_unimported_one` | N | n/a |
| "this test imports {}, and the batch's other tests import {}" | 5013 | N | N | N | n/a |
| "{} takes {}, and the harness has no such fixture" (Wall) | 5044 | T `dg::test_a_fixture_the_harness_lacks_errors_at_setup` | N | n/a | N |
| "every assertion here is on a constant" (Wall) | 5072 | N | N | n/a | N |
| "`assert print(...)` is always False" (Wall) | 5110 | T `dg::test_asserting_on_print_is_always_false` | N | n/a | n/a |
| "{}.{}(...) is not a real Mock method" (Wall) | 5126 | N | N | n/a | n/a |
| "this test imports {}, and no module of that name exists in the tree" (Wall) | 5237 | T `dg::test_a_test_imports_only_modules_the_tree_has` | T `dg::test_the_tests_imports_exclude_the_stdlib_and_the_projects_packages` | N | n/a |
| "this test imports {} from {}, and {}.py defines no such name" (Wall) | 5281 | T `n46::test_an_import_of_a_name_the_module_lacks_is_refused_for_any_name` | N | N | n/a |
| "{} does not define {}, and no criterion names it" (Wall) | 5328 | T `n46::test_an_import_of_a_name_the_module_lacks_is_refused_for_any_name` | N | N | n/a |
| "{} does not define {}, and this test imports it from there" (Wall) | 5346 | T `dg::test_a_surface_imported_from_a_module_that_lacks_it_is_pointed_at_its_file` | N | N | N |
| "the surface {} lives in {}.py and this test imports from {}" (Wall) | 5367 | T `dg::test_a_src_layout_surface_is_imported_by_its_dotted_module` | N (W141, an import through the package is refused) | N | N |
| "this test never calls {}, the surface the criterion names" (Wall) | 5374 | N | T `dg::test_a_bare_call_of_the_surface_name_is_a_call_of_the_surface` | N | N |
| "that is {}'s own sentence written back" (Wall) | 5399 | N | N | n/a | T `pm::test_a_mode_that_encodes_holds_the_exits_the_guard_names` (the named exit is in the mode, W126) |
| "the test uses what {} returns, and the criterion {} says it prints" | 5482 | T `dg::test_the_criterion_under_test_speaks_first_on_print_versus_return` | N | N | n/a |
| "the test uses what {} returns, and the criterion, its ticket or the pr" | 5486 | T `dg::test_a_test_that_uses_a_printing_surfaces_return_value_logs_the_assumption` | N | N | N |
| "the test chooses {}, and nothing in the criterion ... names it" (`_invented_literals`) | 5513 | N | N | N | N |
| "{} exists and belongs to no batch" | 5523 | N | N | N | n/a |
| "{} is the id of the project's test {}" (frame 135) | 5583 | T `sb::test_a_new_test_under_a_project_tests_id_is_refused` | T `sb::test_a_challenge_wake_still_fixes_a_project_test_at_its_own_path` | N | T `sb::test_a_challenge_of_another_test_does_not_open_a_project_test` |
| "{} is stored at {}. To replace it, send this encode again with path" | 5607 | T `sb::test_a_replace_keeps_the_stored_path` | T `sb::test_the_stored_id_replaces_after_a_first_write_this_session` | N | N |
| "{} is a test of batch {}, and this session writes batch {}" | 5626 | T `sb::test_a_stored_test_of_another_batch_is_refused_as_a_first_write` | P3-S1 (an inherited row that `inherit` moved to another batch) | N | N |
| "{} is {}'s file, and {} is the test of this same criterion" | 5641 | T `sb::test_a_project_row_that_holds_a_criterion_is_still_the_projects` | N | N | N |
| "{} is already {}'s file; two tests in one file overwrite each other" | 5650 | T `dg::test_two_tests_may_not_share_a_file` | T `sb::test_a_second_criterion_is_a_second_test` | N | n/a |
| One test per criterion, in the session | 5590s | T `sb::test_one_criterion_gets_one_test_in_a_session` | T `sb::test_two_replaces_of_one_test_stage_one_write` | n/a | n/a |
| A missing door: a new id on a criterion that holds a stored test (W138) | none | P3-cat (W138) | n/a | n/a | n/a |

### A4. `msg.*` (`_bind_send` at `sandbox.py:928`, with `_answer_evidence`, `_challenge_evidence` and `_escalation_over_removed_grain`)

32 send ops in 83 modes share 41 sites. Each verb guards its own doors. AW is marked per door from the script's hits, read once by the agent. RR, FF and NC were not checked per door: those columns hold one mark per door, from the door's text only.

| Door | Line | AW | RR | FF | NC |
|---|---|---|---|---|---|
| "refs is a list of ids and you sent one id as a bare string" | 989 | N | N | n/a | N |
| "refs are ids and nothing else; you sent {}" | 1009 | N | N | n/a | N |
| "refs are ids, and {} is not one" | 1023 | N | N | n/a | n/a |
| "{} names no row -- not in any table" | 1039 | N | N | n/a | n/a |
| "{} is not an item. A reopen names the item" | 1077 | N | N | n/a | n/a |
| "{} is approved at its current version; nothing changed under the batch" | 1085 | N | N | N | n/a |
| "a page carries at most {} open assumptions" | 1101 | N | N | N | N |
| "you have already put these words to the principal, in {}" | 1122 | T `sb::test_an_owner_that_could_not_answer_is_not_relayed` | N | N | n/a |
| "'{} ...' is the principal's own sentence, pasted back" | 1145 | N | N | n/a | n/a |
| "{} names no row, so this question is about your own bookkeeping" | 1179 | N | N | n/a | n/a |
| "{} is a message, and the principal has never seen one" | 1190 | N | N | n/a | n/a |
| "an ask carries the question in its refs and you sent none" | 1213 | N | N | n/a | n/a |
| "{}'s last run reached input() through the code it calls" | 1233 | T `dg::test_a_tester_cannot_hold_a_test_whose_run_reached_stdin` | N | N | N |
| "{} already has your open question, {}" | 1266 | T `tf::test_a_criterion_already_questioned_is_not_asked_again` | N | N | n/a |
| "you were woken for batch {} and a report from here is about it" | 1281 | N | N | n/a | N |
| "you sent {} to {} on exactly these refs already ... the answer po" | 1356 | T `dg::test_the_same_escalation_twice_is_refused_toward_the_answer` | N | N | N |
| "you sent {} ... and they answered ({}) with no row be" | 1364 | T `dg::test_the_same_escalation_twice_is_refused_toward_the_answer` | P3-S5 (W145, a challenge of version 2 refused as the answered one) | N | N |
| "you sent {} ... and they answered. Sending it again" | 1384 | T `dg::test_the_same_escalation_twice_is_refused_toward_the_answer` | P3-S5 (W145) | N | N |
| "you sent {} ... and it waits for an answer" | 1400 | T `dg::test_a_challenge_that_waits_for_its_answer_is_not_sent_twice` | N | N | N |
| "{} has answered {} questions of yours on these rows" | 1440 | N | N | N | N |
| "claim the branch first: brief.intake" | 1452 | T `ic::test_an_unclaimed_reply_is_refused` | N | n/a | N |
| "you claimed work, so the reply carries refs" | 1457 | N | N | n/a | N |
| "you claimed work and segmented nothing" | 1473 | T `ic::test_work_claimed_with_the_entry_as_its_ref_is_still_nothing` | N | n/a | N |
| "you looked up {} and the glossary had nothing" | 1524 | N | N | N | N |
| "already asked -- {} carries {} to the Terminologist" | 1571 | T `tf::test_a_later_question_on_the_routed_criterion_is_refused` | N | N | N |
| "read the reply before you relay it" | 1715 | T `test_term_collision::test_a_relay_before_the_ruling_is_refused` | N | n/a | N |
| "the answer you are relaying cites nothing it came from" | 1753 | T `sb::test_an_answer_names_what_it_came_from` | N | n/a | N |
| "an answer names the rows it came from, and these name none" | 1794 | T `sb::test_an_answer_names_what_it_came_from` | N | n/a | N |
| "{}, and refs={} names none ... send msg.report_liaison" | 1822 | T `sb::test_a_terminologist_answer_with_no_term_is_sent_to_the_report` | N | N | N |
| "{} is not a statement, and a confirmation asks the principal" | 1850 | N | N | n/a | N |
| "you have already sent {} to {}; saying it again with different refs" | 1873 | N | N | n/a | n/a |
| "every owner these rows belong to has its relay already" | 1923 | N | N | n/a | n/a |
| "an answer to a challenge names the criterion the test stands on" | 689 | N | N | n/a | N |
| "an answer that keeps the test carries the criterion's words" | 693 | T `tf::test_an_answer_to_a_challenge_quotes_the_criterion_or_is_the_fix` | N | n/a | N |
| "a challenge to the tester names both sides of the conflict" | 789 | N | N | n/a | N |
| "{} is not a criterion of this batch" | 800 | T `ce::test_a_foreign_criterion_is_not_this_batchs_fight` | N | N | N |
| "{} has no criterion: it is the project's own test" | 812 | T `n46::test_a_challenge_may_not_name_the_projects_own_test` | P3-S2 (the Tester file of a merged batch is now a project test) | N | N |
| "quotes= must copy {}'s exact words" | 842 | N | N | N | N |
| "quotes= must contain the disputed row's own words" | 863 | T `ce::test_the_other_channels_hold_the_looser_form_of_the_rule` | N | N | N |
| "the finding stands on a fact about your tree" | 885 | N | N | N | N |
| "the finding {} is about {}, which constraint {} binds" | 907 | T `dg::test_an_escalation_over_a_removed_name_is_the_finding_restated` | N | N | N |
| A missing door: a burst of one challenge per red test in one reply (W116) | none | P3-cat (W116) | n/a | n/a | n/a |

### A5. The runner's per-call doors (`run_session`, `runner.py:2649`)

These doors act on every seat and every op. Each was checked by hand.

| Door | Line | AW | RR | FF | NC |
|---|---|---|---|---|---|
| "prompt did not fit" (logged, not shown to the seat) | 2913 | T `rn::test_an_over_budget_prompt_is_named_before_it_is_sent` | n/a | N | n/a |
| "your reply was cut at the output budget" | 2929, 2957 | T `rn::test_a_cut_reply_with_no_call_is_shown_the_cut_once_and_the_session_commits` | n/a | T `rn::test_the_cut_line_is_true_beside_held_and_broken_calls` (W121) | N |
| "You wrote code into your reply" | 2973 | T `dg` (fragment, one test) | N | n/a | N |
| "You said what you would do and did not do it" | 2995 | T `dg` (fragment, one test) | N | n/a | N |
| "You were woken because something is owed here" | 3013 | T `rn` and `dg` (fragment) | N | n/a | n/a |
| Held calls: "The calls you stood by ran, and these were refused" | 3034, 3049 | T `rn::test_a_new_read_holds_the_action_which_executes_if_stood_by` | N | N | n/a |
| "repeated its previous turn verbatim twice; ended" | 3069 | N | N | n/a | n/a |
| "You wrote tool results into your own reply" (W113, parked) | 3123 | T `rn` (fragment, one test) | N | n/a | N |
| The turn's result cap: "Ask for it again in your next turn" | 3272 | T `rn::test_two_source_reads_in_one_turn_are_capped_as_a_turn` | N | T `rn::test_a_withheld_result_is_not_remembered_as_an_answer` | N |
| Repeat refused, the window took it: "not served again" | 3363, 3389 | T `rn::test_an_evicted_answer_is_served_again_and_a_present_one_is_a_line` | P3-S6 (W139, two reads evict each other) | N | N |
| Repeat refused, unchanged: "has not changed; not answered again" | 3410, 3439 | T `rn::test_a_read_already_answered_does_not_hold_the_action_again` | N | N | N |
| Pushed and asked repeat lines (`_PUSHED_REPEAT`, `_ASKED_REPEAT`) | 3473 | T `rn::test_a_pushed_read_does_not_hold_the_action_behind_it` | N | T `rn::test_the_pushed_repeat_line_also_claims_nothing_about_this_prompt` | n/a |
| "refused the same way in three turns", then the stop at four | 3528, 3532 | T `rn` (fragment) | N | N | N |
| "NOT RUN, because you wrote them before the answers" | 3538, 3544 | T `rn` (fragment) | N | n/a | N |
| A missing door: one reply that holds many calls of one kind (W116) | none | P3-cat (W116) | n/a | n/a | n/a |

### A6. The parser and the sandbox's generic doors

| Door | Site | AW | RR | FF | NC |
|---|---|---|---|---|---|
| Parser refusals, 9 `ToolError` sites, 86 tests in `tp` and `test_toolproto_quotes` (by family) | `rota/llm/toolproto.py` | T `tp` | P2 (W122, W125) | N (W137) | N (W137) |
| "{} is not in this role's working set" (`NotInWorkingSet`) | `sandbox.py:246, 285` | T `sb::test_s9_developer_cannot_write_the_model` | n/a | n/a | n/a |
| Argument validation, `ArgumentError` (`validate_args`) | `sandbox.py:341` | T `sb` (family) | N | N (W137) | N |
| Positional binding | `sandbox.py:158, 165` | T `sb::test_s9_positional_and_keyword_for_the_same_argument_is_an_error` | N | n/a | n/a |
| "{} is already a row of {}; an artefact id is unique" (`_bind`) | `sandbox.py:2121` | N | N | n/a | n/a |
| "{} is the {} row you wrote this session" (`_bind`) | `sandbox.py:2107` | T `dg::test_a_prefixed_item_id_is_still_a_minute` | N | n/a | n/a |

### A7. Every other op, by door family

Not checked per door. 36 ops hold 154 doors. AW counts the doors whose refusal text the script found in a test, as T, and the rest as N. RR, FF and NC hold one mark per op, and the agent read no test for them except where named. RR is T when an arc test lands a right call of the op, `as`, `test_arc_synthetic` or `dl`. That holds the common case only.

| Op | Doors | AW (T of all) | RR | FF | NC |
|---|---|---|---|---|---|
| `batches.group` | 6 | 5 T, 1 N | T `as::test_one_sentence_becomes_a_merged_batch` | N | n/a |
| `batches.annotate` | 1 | 1 T | T `test_arc_synthetic` | N | n/a |
| `batches.expect`, `batches.strays` | 2 | 2 N | N | n/a | n/a |
| `batches.judge_touch` | 3 | 3 N | N | N | n/a |
| `brief.segment` | 4 | 2 T, 2 N | T `as` | N | n/a |
| `challenge.break`, `.uphold`, `.vacuous` | 8 | 2 T, 6 N | N | N | N |
| `criteria.cite` and the four other `cite` ops (`_cite_op`, shared) | 4 | 1 T, 3 N | N | n/a | n/a |
| `criteria.specify` | 10 | 4 T, 6 N | T `as` | N | N |
| `criteria.respecify` | 5 | 2 T, 3 N | N | N | n/a |
| `decisions.author` | 2 | 2 N | N | n/a | n/a |
| `findings.find` | 5 | 5 N | N | N | N |
| `frame.assign` | 4 | 4 N | N | n/a | n/a |
| `glossary.adopt` | 3 | 1 T, 2 N | T `test_arc_synthetic` | n/a | n/a |
| `glossary.amend` | 10 | 8 T, 2 N | T `as` | N | N |
| `glossary.same` | 6 | 4 T, 2 N | N | N | N |
| `glossary.synthesise` | 7 | 4 T, 3 N | N | N | N |
| `ledger.log` | 4 | 4 N | N | N | N |
| `ledger.unaddressed` | 2 | 1 T, 1 N | N | n/a | n/a |
| `model.amend` | 15 | 6 T, 9 N | N | N | N |
| `model.describe` | 3 | 1 T, 2 N | N | n/a | n/a |
| `problem.assert` | 6 | 5 T, 1 N | T `as` | N | N |
| `problem.describe` | 2 | 2 N | N | n/a | n/a |
| `references.record` | 1 | 1 N | N | n/a | n/a |
| `rulings.line` | 2 | 2 N | N | n/a | n/a |
| `rulings.rule` | 11 | 6 T, 5 N | T `nb::test_a_words_answer_leaves_the_park_ask_open_and_wakes_landing_once` | N | n/a |
| `schedule.reask` | 4 | 3 T, 1 N | N | N | n/a |
| `surveys.attest` | 7 | 3 T, 4 N | N | N | N |
| `tests.triage` | 4 | 3 T, 1 N | T `as` | N | N |
| `tickets.slice` | 4 | 3 T, 1 N | T `as` | N | n/a |
| `verdicts.claim_encodes` | 1 | 1 N | T `test_arc_synthetic` | n/a | n/a |
| `verdicts.emit` | 3 | 1 T, 2 N | T `as` | N | N |
| `verdicts.rule` | 4 | 4 N | N | n/a | n/a |
| `code.source` | 1 | 1 T | N (W139, the serve cap) | n/a | n/a |
| 47 read ops with no refusal site (`*.load`, `*.consult`, `code.probe` and others) | 0 | n/a | n/a | n/a | n/a |

The 47 reads fail as blocks, not as doors. Part B holds them.

## Part B. Wakes, blocks and the cut

A wake is the user prompt that `build_prompt` writes (`runner.py:334`). It holds fixed head lines, the inbound message as JSON, and the pushed blocks. `push_working_set` (`runner.py:2134`) pushes every read in the mode's tools that the graph declares a read of the role and that runs with no arguments. Then it reshapes the push for 7 triggers. Over the 83 modes this is 281 pushed block slots of 47 distinct reads (observed: the graph and the `.tools` files, 2026-10-05). The rows below are by block, not by mode. The 281 slots are not checked one by one.

Columns: **Absent** the block is missing when it should be there. **Cut** the cut removes it. **Wrong** the block states a wrong thing.

### B1. The head lines and the inbound

| Block | Absent | Cut | Wrong |
|---|---|---|---|
| "You were woken by: {kind}" and the inbound id | T `rn::test_trigger_message_is_answered_on_commit` | n/a (the cut keeps the front of the wake) | n/a |
| "Refs:" and the subject word or area | T `test_onboarding` (family) | n/a | N |
| "This is attempt {n} of {cap} on this wake" | T `test_batch_start_attempt::test_a_refired_batch_start_says_which_attempt_it_is` | n/a | N |
| The wake's detail (`DETAIL_SHOWN`) | T `n46::test_a_tick_wake_says_its_detail_to_the_role` | n/a | N |
| The failed-run blocks of a Tester's challenge wake (`_failed_run_blocks`, frame 110) | N | N | N |
| The inbound JSON (`resolve_inbound`, 379 lines, about 20 verb shapes, by family) | T `rn` (family) | N | N |
| "Already run for you ... Calling any of these again returns the same thing" | T `rn::test_working_set_is_pushed_not_only_offered` | n/a | N (the code says the sentence is false for the fix wake's `tests.load`, `runner.py:405`) |
| The system prompt: the brief and the signatures (`compose_system`) | T `pm` (family) | n/a (charged against the budget, never cut) | T `pm::test_a_mode_that_encodes_holds_the_exits_the_guard_names` (partial, W126) |

### B2. The fix wake, `developer/tests_failing`

The wall-dense wake. 9 of the 29 walls are in it or its cut (W120, W127, W130, W133, W134, W139, W116, W114, W131).

| Block | Absent | Cut | Wrong |
|---|---|---|---|
| "challenges and escalations on these tests" (the thread) | T `n46::test_the_fix_wake_shows_the_thread_on_a_red_test` | P5 | T `n46::test_a_closed_prior_with_no_answer_row_reads_closed_in_the_thread` |
| "after these", the way out | T `n46::test_the_thread_carries_the_way_out_after_it` | P5 | N |
| "the batch's tests, not passing" | T `n46::test_the_fix_wake_pushes_the_red_tests_and_the_code_they_call` | P5 | P3-S1 (W130, the latest run has no batch filter) |
| "the project's own tests, not passing at your commit" (`_red_rows_by_output`) | T `n46::test_the_fix_wake_separates_the_projects_own_tests_and_pushes_the_diff` | T `rn::test_red_rows_with_one_output_show_it_once_and_the_source_survives` (W127, W120) | P3-S1 (W130) |
| "what that means" | T `n46::test_the_fix_wake_separates_the_projects_own_tests_and_pushes_the_diff` | P5 | N ("they passed before this batch" is false for a Tester file of a merged batch, P3-S2 does not assert it) |
| "passing, not shown" | T `n46::test_the_fix_wake_pushes_the_red_tests_and_the_code_they_call` | P5 | P3-S1 (W130) |
| `code.source`, the spans the tests call (`_source_the_tests_call`) | T `n46::test_the_fix_wake_pushes_the_red_tests_and_the_code_they_call` | P5 (W134) | N |
| `code.diff`, pushed only when a project test is red | T `n46::test_the_fix_wake_separates_the_projects_own_tests_and_pushes_the_diff` | P5 (W134: the diff sits before the source in the push order, so the cut takes the source) | N |
| `criteria.load`, `code.probe`, `references.load`, `batches.expect` | T `rn::test_working_set_is_pushed_not_only_offered` (family) | P5 | N |

The order claim in the `code.diff` row is (reasoned: the generic loop inserts `code.diff` first, and `pushed["code.source"] = spans` adds a key after it, `runner.py:2162-2173` and `2361-2369`).

### B3. The other shaped pushes

| Block | Absent | Cut | Wrong |
|---|---|---|---|
| Critic review: `criteria.load`, `tests.load`, then `code.read` last | T `rn::test_the_critic_wake_keeps_the_criteria_and_tests_in_front_of_the_diff` | T same test | N |
| Criteria wake: "the item", `code.callables`, `code.source` of up to 2 files | T `ps::test_the_criteria_wake_carries_the_item_and_the_module_the_ticket_names` | N | N |
| Slicing wake: this wake's items and the rest as ids | T `ps::test_the_slicing_wake_sets_its_item_apart_from_the_account` | N | N |
| Agenda wake: the page's rows and a count | T `ps::test_the_agenda_wake_pushes_the_pages_seven_and_counts_the_rest` | N | N |
| Annotate wake: the hint from the batch's tickets | N | N | N |
| Structural review: `batches.expect` without tests, `model.consult` filtered to the reaching constraints | T `test_t0_sandbox` and `dl` (family) | N | N (on an exception the block is dropped with a log line only, `runner.py:2401`) |
| `decisions.search` per subject word (`_budget_decision_hits`) | T `ps::test_the_decision_push_is_inside_its_own_budget` | T `ps::test_the_cut_decision_push_names_the_call_for_the_rest` | N |
| `glossary.lookup` for the terms the asker named | T `ps` (family) | N | N |
| Tester `tests_missing`: `tickets.load`, `criteria.load`, `tests.consult`, `glossary.lookup`, `batches.expect` | T `n46::test_the_missing_tests_wake_names_the_criteria_without_a_test` | N | P3-S2 (the inherited Tester file of a merged batch) |
| Every other generic push, 40 distinct reads over the other modes (by family) | T `rn::test_working_set_is_pushed_not_only_offered` | T `rn::test_the_pushed_working_set_obeys_the_same_cap_as_a_fetched_one` | N |
| A push that raises other than `TypeError` or `ArgumentError` kills the session before the first turn (`runner.py:2166`) | N | n/a | n/a |

### B4. The cut

| Mechanism | Absent | Cut | Wrong |
|---|---|---|---|
| `_render` per pushed block at `PUSH_CHARS` 20000 | n/a | T `rn::test_a_pushed_read_is_not_cut_at_the_result_cap` | T `rc::test_a_cut_span_names_the_line_and_the_next_call` |
| `_fit_budget`: half the window at 3.97 characters a token, less the system prompt | n/a | T `rn::test_the_fit_budget_is_half_the_window` | n/a |
| The wake cut, `_render_cut` at two thirds or one half of the budget | n/a | T `rn::test_a_wake_yields_half_the_budget_to_keep_a_middle_read` | T `rc::test_a_cut_wake_keeps_its_note_byte_for_byte` |
| The wake cut at night size, the window of 16384, on wakes other than the fix wake | n/a | N | N |
| `_pack`, tiers 1 to 4: stubs, covered reads, the newest read of each span, the rest | n/a | T `rn::test_old_replies_become_stubs_before_a_read_goes` | T `rn::test_a_dropped_result_takes_the_stub_of_its_turn` |
| `_pack` at night size with a 1,000-line file (W139) | n/a | P3-S6 (W139) | N |
| `_cap_tail_reply`, `_cap_exchange` | n/a | T `rn::test_a_tail_larger_than_the_budget_leaves_a_middle_read` | T `rn::test_a_latest_exchange_over_the_budget_is_cut_to_fit` |
| `_stub` of an old reply, and a stub of a stub (W117) | n/a | T `rn::test_a_stub_keeps_calls_the_parser_finds_inside_a_line` | N (W117) |
| The notes: `_dropped_note`, `cut_note`, the reply cut line | T `rn::test_fit_pays_for_the_notice_it_inserts` | n/a | T `rc::test_one_wording_for_every_cut` (W121) |

## Part C. States and moves

Columns: **Stuck** a state that nothing leaves. **Silent** a move that wakes nobody. **Contra** two rows that contradict. For a state row, Silent is n/a. For a move row, Stuck is n/a.

`check_terminal_states`, `check_predicates_can_fire` and `check_states_are_reachable` in `rota/core/predicates.py` prove that every CHECK state of 8 lifecycle columns has a declared drain or a declared end, and `pr::test_every_lifecycle_state_has_a_way_out` runs them. The checks return no problem today (observed: the live call, 2026-10-05). They read declarations. They cannot see a derived state, a drain that a filter hides, or a drain that fires on a state no fixture builds.

### C1. A batch

| Row | Function | Stuck | Silent | Contra |
|---|---|---|---|---|
| State `pending` | `batches_group` stages it | T `pr::test_every_lifecycle_state_has_a_way_out` | n/a | P4 (audit 2, two open batches of one item, runs in no test today) |
| State `pending` behind a parked predecessor | `next_batch` needs each predecessor merged or abandoned (`scheduler.py:1350`) | P3-S3 | n/a | n/a |
| State `running` | `lifecycle.start` | T `pr::test_every_lifecycle_state_has_a_way_out` | n/a | P4 (audit 3, two running at once) |
| State `deferred` | `lifecycle.defer` | T `pr::test_every_lifecycle_state_has_a_way_out` | n/a | P3-S1 (its project test rows move to the batch that starts next) |
| State `merged` | `lifecycle.merge` | n/a | n/a | P4 (W135: merged while a project row holds a Tester body) |
| State `abandoned` | `lifecycle.abandon` | n/a | n/a | T `nb::test_a_contest_on_the_park_ask_abandons_the_batch` |
| Derived state: parked (`scheduler.parked`) | deferred with a given-up key, or at `loop_cap` on its failing head | T `nb::test_a_parked_batch_resumes_on_a_new_head_commit` | n/a | P4 (a parked batch with no open park ask) |
| Move: group, none to `pending` | `batches_group` | n/a | T `as::test_one_sentence_becomes_a_merged_batch` | n/a |
| Move: start, `pending` or `deferred` to `running`, with `harness.inherit` | `lifecycle.start`, `loop.step` | n/a | T `dl::test_dispatching_a_batch_marks_it_running` | P3-S1 (W130, `inherit` writes `INSERT OR REPLACE` under an id that names no batch) |
| Move: preempt, `running` to `deferred` | `predicates.preempt`, `loop._perform` | n/a | T `nb::test_the_preempt_reads_the_start_s_order_and_is_bounded` | T `fr::test_a_batch_key_keeps_its_count_until_the_batch_moves` |
| Move: park, `running` to `deferred` with a park ask | `predicates.park_ask` | n/a | T `nb::test_the_park_wake_defers_the_running_batch` | P3-S4 |
| Move: cancel or contest, to `abandoned` | `predicates.cancel`, `principal.land` | n/a | T `test_arc_synthetic::test_arc_revocation_stops_the_batch` | T `nb::test_a_contest_on_the_park_ask_abandons_the_batch` |
| Move: merge, `running` to `merged` | `predicates.merge`, `lifecycle.mergeable`, `lifecycle.merge` | n/a | T `dl::test_a_clean_batch_merges_without_waking_anyone` | P3-S1 (`mergeable` reads latest runs, W130 class, reasoned) |
| Move: resume after a lift | `tick_batch_start` | n/a | T `nb::test_a_preempted_batch_past_its_cap_resumes_exhausted` (W86) | T `nb::test_a_quarantined_batch_resumed_after_a_preempt_waits_for_the_principal` (W87) |
| Move: past the cap with a spent ladder, to `deferred` | the exhausted ladder | n/a | T `nb::test_a_running_batch_past_its_cap_with_a_spent_ladder_is_deferred` | n/a |
| Move: reopen when the item loses approval | `predicates.reopen` | n/a | T `dl::test_a_running_batch_whose_item_lost_approval_reopens` | n/a |
| Move: the merge delivers the next batch's start | `next_batch` after `merge` | n/a | P3-S2 | P3-S2 |

### C2. A test and its runs

| Row | Function | Stuck | Silent | Contra |
|---|---|---|---|---|
| State: an inherited row, `inh_` id, no criterion | `harness.inherit` | n/a | n/a | T `sb::test_a_new_test_under_a_project_tests_id_is_refused` (the door), P4 for the world (W135) |
| State: an inherited row of a deferred batch after another batch starts | `harness.inherit` | n/a | n/a | P3-S1 |
| State: a Tester test at version 1 | `tests_encode` | n/a | n/a | P4 (W138, W123: a criterion holds one test) |
| State: a Tester test at version 2 | `tests_encode`, replace | n/a | n/a | P3-S5 (W145) |
| State: the Tester file of a merged batch, inherited by the next batch | `lifecycle.merge`, then `harness.inherit` | n/a | n/a | P3-S2 |
| State: a run `fail` or `error` | `lifecycle.record_test_run` | T `pr::test_every_lifecycle_state_has_a_way_out` | n/a | P3-S1 (W130: `tests_load` takes the latest run by `test_id` with no batch filter, `api.py` near 5722) |
| State: a run at an old head | `test_runs.commit_sha` | n/a | n/a | T `test_grouping_rule::test_the_state_reads_failures_at_the_head_commit_not_by_id_order` |
| Move: encode, new | `tests_encode` | n/a | T `as::test_one_sentence_becomes_a_merged_batch` (the harness fires) | P3-cat (W138) |
| Move: encode, replace | `tests_encode` | n/a | T `dg::test_a_re_encoded_test_is_owed_a_fresh_run` | P3-S5 |
| Move: the harness run | `harness.run` | n/a | T `dl::test_the_harness_records_what_the_tests_said` | T `dl::test_a_stale_pass_does_not_merge` |
| Move: a commit lifts the batch's keys and resets attempts | `db._lift_quarantines` | n/a | T `dg::test_a_commit_resets_the_failing_ticks_attempts` | T `dg::test_a_head_commit_still_revives_the_batchs_keys` |

### C3. A key, `tick_attempts`

| Row | Function | Stuck | Silent | Contra |
|---|---|---|---|---|
| State: attempts below the cap | `note_dispatch` | T `fr::test_a_tick_that_cannot_drain_is_eventually_quarantined` | n/a | T `fr::test_a_batch_key_keeps_its_count_until_the_batch_moves` |
| State: quarantined, not reported | `quarantine_overrun`, `quarantine_stalled` | T `fr::test_telling_the_principal_discharges_the_telling` | n/a | n/a |
| State: quarantined and reported | the `quarantined` predicate | T `nb::test_a_hand_commit_found_at_boot_ends_a_quarantine_park` | n/a | P4 (a quarantined key of a merged or abandoned batch) |
| State: quarantined beside pending batches, at attempt 5 of 10 | `given_up`, `next_batch` | P3-S3 | n/a | P3-S3 |
| Move: the cap is reached, quarantine | `quarantine_overrun` | n/a | T `fr::test_the_quarantined_wake_carries_the_affected_rows` | n/a |
| Move: a stall, quarantine | `quarantine_stalled` | n/a | T `nb::test_the_park_count_survives_a_commit_and_quarantines` | n/a |
| Move: a loop of messages, quarantine | `quarantine_looping` | n/a | T `pr` (family) | N |
| Move: the batch moves, the counts reset | `db._forget_batch_counts` | n/a | T `nb::test_a_batch_count_survives_absence_and_a_move_resets_it` | n/a |

### C4. An ask, `messages`, with the park ask and the challenge

| Row | Function | Stuck | Silent | Contra |
|---|---|---|---|---|
| State `open` | `_bind_send` stages it | T `pr::test_every_lifecycle_state_has_a_way_out` | n/a | n/a |
| State `answered` | `db.session_commit` answers the trigger | n/a | n/a | P4 (audit 5, with the by-design rows removed) |
| State `unresolved` | `schedule_reask` | T `pr::test_every_lifecycle_state_has_a_way_out` | n/a | n/a |
| State `quarantined` | the step's failure cap, `quarantine_looping` | T `test_step_failure::test_a_message_whose_session_fails_every_time_is_quarantined_at_the_cap` | n/a | n/a |
| State: a park ask open | `predicates.park_ask`, `park_ask_id` | T `nb::test_a_words_answer_leaves_the_park_ask_open_and_wakes_landing_once` | n/a | P3-S4 |
| State: a park ask whose batch left the park | `close_stale_park_asks` | T `nb` (family) | n/a | P4 |
| State: a challenge to the Tester, answered | the Tester's session commits | n/a | n/a | P3-S5 (W145) |
| Move: send, a recipient wakes | `message_tips` | n/a | T `fr::test_the_frontier_is_every_predicate` | n/a |
| Move: any committed reply answers the trigger, prose too (W132) | `db.session_commit` | n/a | n/a | P3-cat (W132) |
| Move: reask, `unresolved`, the ladder | `schedule_reask`, `predicates.unresolved` | n/a | T `dl::test_the_ladder_climbs_one_rung_at_a_time` | n/a |
| Move: the principal answers a park ask in words (W142) | `rulings_rule`, `principal.land` | n/a | T `nb::test_a_words_answer_leaves_the_park_ask_open_and_wakes_landing_once` | N (W142, the scripted principal names no option, `walk.py`) |
| Move: a verdict, then merge or `verdict_failed` | `verdicts_emit`, `predicates.verdict_failed` | n/a | T `dl::test_a_failed_batch_can_still_pass` | n/a |
| Move: a violated finding stops the merge | `findings_find`, `predicates.finding_violated` | n/a | T `as::test_a_violated_finding_still_stops_the_merge` | n/a |
| Move: a touch stray, judged | `predicates.touch_strayed`, `touch_mistaken` | n/a | T `td::test_a_commit_outside_the_prediction_writes_a_stray_row_and_still_commits` | n/a |

## Counts

The counts are of cells, from the tables above, by a script over this file (observed: `f144/count.py`, 2026-10-05). The A7 AW cells count per door: a cell of "5 T, 1 N" is 5 T and 1 N.

| Part | Cells | T | P1 | P2 | P3 | P4 | P5 | N | n/a |
|---|---|---|---|---|---|---|---|---|---|
| A1 to A6, read door by door | 556 | 128 | 12 | 1 | 11 | 0 | 0 | 259 | 145 |
| A7, by door family | 257 | 79 | 0 | 0 | 0 | 0 | 0 | 140 | 38 |
| A, all | 813 | 207 | 12 | 1 | 11 | 0 | 0 | 399 | 183 |
| B | 111 | 43 | 0 | 0 | 5 | 0 | 8 | 36 | 19 |
| C | 150 | 45 | 0 | 0 | 18 | 8 | 0 | 2 | 77 |
| All | 1,074 | 295 | 12 | 1 | 34 | 8 | 8 | 437 | 279 |

The N cells of part A by column, all sections: AW 132, RR 110, FF 86, NC 71. The AW count holds 87 doors of A7 that the text search did not find in a test, and that count is a ceiling (see the limits).

Rows not checked one by one: the 154 doors of A7 on every column, the 41 doors of A4 on RR, FF and NC, the 281 push slots of part B, and the 20 or so verb shapes of `resolve_inbound`.

The few N cells in part C do not mean that part C is safe. 26 of its 150 cells are P3 or P4, and each P3 cell holds only under the condition in the marks section. Part C also lists 4 entities only.

## The N cells, ranked by harm

The rank is this agent's judgement. A wrong merge comes first, then a stuck batch, then a wasted session.

A wrong merge:

1. **A3, NC of the stored-test refusals** at 5607, 5626 and 5641. Each names an encode call, and no dry run checks it. A named replace that lands on the wrong row is frame 135's class, which cost four reviews (copied: `plans/stack.md`, frame 135's statuses).
2. **A7, RR of `verdicts.emit`**. Door 6396 refuses a fail verdict unless the test encodes the criterion. A right fail that this door refuses lets a batch merge.
3. **A7, RR and AW of `findings.find`**, 5 doors and no test found. A right violated finding that a door refuses lets a batch merge past a constraint.
4. **B3, the structural review push dropped on an exception**. The Architect then reviews with no constraint in view, and the code logs it only (`runner.py:2401`).
5. **A6, AW of the artefact id door** at `sandbox.py:2121`. Twin ids across tables made a correct challenge resolve to a criterion once (copied: the comment at `audit.py:125`).

A stuck batch:

6. **A1, the missing door W146**: a written module's top level loads a name that it does not bind. The harness then sees every test red at import.
7. **A4, RR of the challenge doors** 789 and 842. A right challenge of a wrong test that a door refuses leaves the batch with no route, the W114 class.
8. **B3, a push that raises other than `TypeError` or `ArgumentError`**. The session dies before its first turn, and the key goes to quarantine.
9. **B4, the wake cut at 16384 on wakes other than the fix wake**: `verdict_failed`, `batch_start`, `tests_missing`, `review`. Item 5 holds the fix wake only.
10. **B1, the failed-run blocks of the Tester's challenge wake** (`_failed_run_blocks`, frame 110). No test names them, and they are the only plain words the Tester reads about the challenge.

A wasted session, the rest, in order:

11. A2, FF of the revert door: "the tests pass both ways" is false (copied: `plans/frame136-design.md`, wall 5).
12. A3, all four columns of `_invented_literals` at 5513.
13. C3, a quarantine by a message loop that contradicts another row (`quarantine_looping`).
14. A5, the verbatim-repeat door at 3069, AW and RR.
15. A1 and A3, the FF cells that quote a computed name, line or path, 37 cells.
16. A4 and A7, the NC cells of staged ops, 41 cells.
17. B1, B3 and B4, the Wrong cells of the shaped pushes and the inbound, 18 cells.
18. C4, W142: the scripted principal's answer names no option. It is an instrument of the build session and not a seat's structure.

## The limits of the table

- The table covers the structure's side only. It does not list every wrong thing a model can send. Item 2's fuzz stays the instrument for that (copied: `plans/stack.md`, frame 144's ends-when).
- AW marks the door's own shape. A wrong call of a shape no door names is invisible here, unless a wall named it. W138 and W140 were such shapes. The catalogue holds only what a person names.
- The A4 and A7 AW cells come from a text match of four-word runs. A test that asserts with a short `match=` or with no text is missed, so the T count is low. A shared phrase can match an unrelated test, so a few T cells may be false. The agent read the hits for A1 to A6 and dropped the false ones there.
- RR, FF and NC in A4 and A7 are one mark per door or per op from the refusal's text. The agent did not read a test for each. 154 doors in A7 and 41 in A4 are not checked one by one on those columns.
- Part B rows are by block, not by mode. 281 pushed slots over 83 modes are not checked one by one. `resolve_inbound` has about 20 verb shapes in one row.
- Part C covers 4 entities. Items, statements, criteria, ledger rows, glossary terms, constraints and the onboarding phases have states too, and the table does not list them. Onboarding walls are fewer in nights 113 to 122, and the frame's sites are delivery (reasoned: the 29 frames of the inventory).
- "Wakes nobody" is marked T when a test asserts the next wake. A move whose next wake fires only on a state that no fixture builds, such as S3, can still be silent on a night.
- The window. Every T cell in part B runs at a test's own budget. None runs at 16384 with a wake of night size, except `rn::test_the_assembled_prompt_of_a_replayed_turn_is_inside_the_budget`, which checks the size and not the blocks.
- The model's judgement on a correct prompt, the D class, has no cell (copied: `plans/frame144-inventory.md`, section 2: W129, W131, W133, W143).
