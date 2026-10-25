# Frame 326, review 1 of pass 1 at af04bbe1

Date: 2026-10-25. Read-only review of the six commits 527659cf, 789b4565, e41580e8, 15cb9847, a895e899 and af04bbe1 above 0265b414. Worktrees: `C:/Users/roman/rota_r326` at af04bbe1 and `C:/Users/roman/rota_r326b` at 0265b414. The register is a read-only backup copy of `C:/Users/roman/rota_g301/tests/rota/cassettes.db`, taken at 22:40, the same source the implementer used.

## The verdict

Accept 527659cf, 789b4565, 15cb9847, a895e899 and af04bbe1 for the branch. Hold back e41580e8.

- e41580e8 indexes the main checkout, not the batch tree. On the two cases that fault A names, a probe of a name the batch wrote returns a bare `[]`, and the repair 2 note can no longer fire. So e41580e8 brings back the fault A symptom on the cases it was meant to repair.
- Without e41580e8, the lint of a895e899 fails `L1-DV-challenge-a-test-that-contradicts-its-criterion`. Put that case in the `OWED` index group, with the nine others of that group.
- The STALE set at af04bbe1 is 15 cases, not 14. The fifteenth case is `L1-DV-log-the-choice-the-criteria-did-not-make`, and repair 2 makes it STALE.

Verdicts by point:

1. CONFIRMED with a gap. `casestatus` lists the marked case apart, and the pin covers both halves. `test_l1.py` still runs the case as a plain red. The case should be an xfail after the STALE check.
2. CONFIRMED. The note fires only on an index with no row. One mode, `architect/deliver`, holds `code.probe` without `code.source`, and for that mode the note names a call it does not hold.
3. FAILS on the count. Repair 2 makes 9 Developer recordings stale, not 8. `casestatus` is not at fault and needs no line of its own: it reads `key_misses` and calls the cases STALE after one replay.
4. FAILS. Onboarding indexes the main checkout before the batch worktree exists. The repair is a batch-tree refresh in `_with_repo`.
5. CONFIRMED. The three `repo:` blocks have the shape of the runner case. The `truncate` source is the criterion's function. `OWED` names `L1-TS-act-on-the-reason-of-a-challenge`.
6. CONFIRMED with two gaps. The test passes, 706 passed and 39 skipped. Rule 2 reads the brief, not the tools. `OWED` has no guard against growth.
7. CONFIRMED. The prompt test refuses the partial token `msg.answer_`. The new line has the form of `terminologist/question.md`.
8. FAILS on the count. There are 15 STALE cases, not 14: 9 from the probe text and 6 from the prompt change.
9. CONFIRMED. The suite has 42 reds, and none of them comes from model behaviour that this pass changed. The pass makes 10 reds that are new, and each one is STALE.

## Point 1. The `red:` marker

CONFIRMED for `casestatus`. `red_by_construction` (`rota/tools/casestatus.py` 619 to 628) reads the field. `render` takes a marked row out of every state count, adds `, 1 red by construction` to the summary line, and lists the row apart, `--red` included. The pin `test_casestatus_lists_a_case_red_by_construction_apart` covers the real case's reason and the split of the render. `casestatus` has no pass rate, so "no count" is "no state count". The per-model table is a scratchpad script, and it can import the one definition.

`tests/rota/test_l1.py` has no branch for `red:`. `test_l1_case` runs the case and asserts the threshold (`test_l1.py` 207). The run at af04bbe1 shows `L1-TE-log-the-word-you-took-one-way: 0/5 passed, needs 3` as a plain red.

The case's own comment says "Red until that mode exists". The red is expected, it has an owner, and it has an end. An xfail with the marker's reason states exactly that. A strict mark is wrong here, because a STALE `pytest.fail` would then read as an expected failure, and the gate reads STALE from the FAILED lines. So put the branch after the STALE check and after the recording, and call `pytest.xfail(case["red"])` there. When the case passes while it is marked, fail it with "remove `red:`".

## Point 2. The empty-index text

CONFIRMED. The new branch (`rota/roles/api.py` 14394 to 14398) runs `SELECT 1 FROM code_index LIMIT 1` and returns the note only when the index has no row. A miss in a populated index still returns a bare `[]`. The probe `probe_defaults.py` shows both: `calculate_tip` returns `[]` from an index of 93 rows, and the same probe returns the note after the rows are deleted.

The modes that resolve `code.probe` and not `code.source` through `prompts.mode_tools` or `prompts.available`: 1, `architect/deliver`. For that mode the note says "Read the file with `code.source`". The working set refuses that call, so this is fault D's class, a text that offers a call the seat does not hold. In practice only the register meets an empty index, because a night always onboards. The one `architect/deliver` case that has no repository, `L1-AR-constrain-an-external-commitment`, has no recorded probe. So the text misleads in principle and no recording meets it now. Low.

## Point 3. The stale Developer recordings

The count is 9, not 8. With the note removed by a swap of the function body (`plug/r326_noprobe.py`), `L1-DV-say-why-the-test-cannot-pass` and `L1-DV-restore-what-the-finding-names` replay green, and `L1-DV-log-the-choice-the-criteria-did-not-make` goes back to its recorded `0/5`. At af04bbe1 the same case fails `STALE`. It was red before the pass and it is red after the pass, so a compare of the red sets does not show it.

The register read-only (`probers.py`, `mode=ro`): the cases whose last five `qwen3:8b` runs call `code.probe` with no `onboard` and no seeded `code_index` are build-a-clear, log-the-choice, challenge-long-body, ask-when, act-on-answered, fix-what-the-verdict, read-the-map and restore. That makes 8. `say-why` is the ninth case. It is pinned to qwen3.5:9b and has no repository, so its index is always empty.

`casestatus` is not at fault, and it needs no line of its own. Before any replay at af04bbe1 it calls these cases green, because a tool result is not in the system text. After one replay writes a `key_misses` row, `casestatus` calls build-a-clear and log-the-choice STALE (observed: the fresh copy `reg2.db`, after three replays). The gate also adds every `Failed: STALE` red to its stale set (`stale_by_failure`, `rota/tools/gate.py` 480 to 486). PLAUSIBLE, low: `say-why` still read green in `casestatus` after its miss. The cause is probably the key of the pinned model, and this review did not read it.

## Point 4. What `onboard: true` indexes

The main checkout. `_with_repo` (`rota/testkit/fixtures.py` 832 to 835) calls `boot.onboard(conn, repo.root)`, and `onboard` (`rota/onboarding/boot.py` 83) calls `indexer.build(conn, root)`. The batch worktree is made after that step (`fixtures.py` 862), and the edit is committed after it (868). `.rota` is in the indexer's skip set. So the index never holds the batch's code.

Probes:

- `probe_index.py`, the challenge case: the index has `src/billing/accounts.py::close_account` at 26 to 34, from the sample file of 34 lines. The batch file has 19 lines, and `def close_account` is at line 14. A `code.source` of that span reads past the end and returns no text.
- `probe_defaults.py`, the defaults case: `main.py` is not in the main checkout. `code.probe("calculate_tip")` returns `[]` from 93 rows. With no index, the same probe would return the repair 2 note.

So repair 3 does not reach fault A. Worse, it turns off the repair 2 note on the two cases that fault A names. On a night, `runner._refresh_index` (`rota/core/runner.py` 6615) calls `indexer.refresh(conn, tree, main=False, batch_id=batch_id)` after the Developer's commit. The repair is the same call in `_with_repo`, after the edit commit, when `onboard` is set. The same option clears the nine index entries of `OWED`. The two onboarded cases replay green today only because their recordings probe `invoices_for`, a name that is in neither tree.

## Point 5. The Tester `repo:` blocks

CONFIRMED. Each block has a `batch` key with the case's batch, a `message` and one small file under `edit`. This is the shape of `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner` (`l1_tester.yaml` 137). The fix case's source is `truncate(subject, width=72)` in `src/mail/subject.py`, the function that the criterion and the test body call. The hold case's source keeps the invoices, so the test stays right. The send case's `commit_sha: HEAD` is rewritten to the edit commit by `_with_repo` (`fixtures.py` 878). `OWED` names `L1-TS-act-on-the-reason-of-a-challenge` in its `repo:` group (`test_case_reachability.py` 224).

## Point 6. The reachability rules

The test passes at af04bbe1: `test_case_reachability.py` and `test_index_refresh.py` together give 706 passed and 39 skipped. Of the skips, 19 are `OWED` and 20 are ticks.

Rule 1 is exact. `CODE_READS & set(tools)` with no `repo:` gives a problem, and the tools come from `prompts.mode_tools(role, mode) or prompts.available(role)`.

Rule 2 is narrower than the brief. It reads `"code.probe" in prompts.piece(role, mode)`, so it fires only when the brief names the probe. It also accepts a seeded `fixture.code_index`. The narrow form misses the modes that list the probe and do not name it. `verdict_failed` and `finding_violated` are such modes. `L1-DV-fix-what-the-verdict-names` probed an empty index 5 of 5 times and `L1-DV-restore-what-the-finding-names` 1 of 5 times. Both went STALE under repair 2, and the lint passes both. Fault A's second case, the defaults case, is in the same class. Rule 2 also passes the two onboarded cases, although their index holds the wrong tree.

The `OWED` set can shrink and it can also grow. A case that leaves its problem behind fails with "Remove it from OWED" (`test_case_reachability.py` 280 to 281). Nothing fails when a new id joins the set, and nothing fails when an id names no case. `OWED` is used nowhere else (observed: grep).

The 19 owed cases, by group (observed: `owed.py`):

- A `repo:` block, 10: `L1-AR-rewrite-the-guess-from-the-ruling` (architect/guess), `L1-AR-re-annotate-from-the-principals-correction` (architect/annotate), `L1-AR-constrain-an-external-commitment` (architect/deliver), `L1-DV-say-why-the-test-cannot-pass` (developer/tests_failing, repo and index), `L1-TE-a-new-behaviour-is-a-new-callable` and `L1-TE-specify-criteria` (terminologist/criteria), `L1-TE-put-a-word-with-two-senses-to-the-principal` (terminologist/term_collision, repo and index), `L1-TS-act-on-the-reason-of-a-challenge` (tester/challenge), `L3-scope-becomes-a-ticket-with-criteria` and `L3-a-challenge-reaches-the-role-that-can-answer-it` (a terminologist/criteria leg).
- An index of the batch's code, 9: `L1-AR-find-against-a-constraint` and `L1-AR-a-diff-no-constraint-binds-files-k0` (architect/structural_review), `L1-AR-judge-a-stray-foreseen-or-a-mistake` (architect/touch_strayed), `L1-DV-build-a-clear-criterion`, `L1-DV-log-the-choice-the-criteria-did-not-make` and `L1-DV-read-the-map-not-the-whole-file` (developer/batch_start), `L1-DV-challenge-a-test-with-a-long-body`, `L1-DV-ask-when-the-test-contradicts-its-criterion-at-the-fix-wake` and `L1-DV-act-on-an-answered-challenge` (developer/tests_failing).

## Point 7. The Tester answer line

CONFIRMED. `test_prompts_never_name_a_function_the_role_lacks` (`tests/rota/test_prompts.py` 124 to 152) matches each dotted token that starts with `msg` or an artefact name. It refuses each token that is not in the role's namespace. The partial token `msg.answer_` is not in the namespace, so the provenance read's literal wording cannot ship. The line writes "the one `msg.` answer call you hold". The test checks the role's whole namespace, not the working set of each wake, so it allows both full names.

The form matches `terminologist/question.md` 5 to 9: "the one `msg.` call you hold", then the list of answer calls, then "exactly one of them is in front of you: the channel you have is the role that asked". The Tester line drops the Terminologist's last sentence, "You are never holding a choice of who to reply to". That difference does not matter here.

## Point 8. The STALE set

At af04bbe1 the suite fails 15 cases `STALE`. `casestatus` on the fresh copy, before any replay, reads 6. The gate's stale set is the union of the two, so its expected stale line is 15.

- The probe text, repair 2, 9 cases: `L1-DV-act-on-an-answered-challenge`, `L1-DV-ask-when-the-test-contradicts-its-criterion-at-the-fix-wake`, `L1-DV-build-a-clear-criterion`, `L1-DV-challenge-a-test-with-a-long-body`, `L1-DV-fix-what-the-verdict-names`, `L1-DV-log-the-choice-the-criteria-did-not-make`, `L1-DV-read-the-map-not-the-whole-file`, `L1-DV-restore-what-the-finding-names`, `L1-DV-say-why-the-test-cannot-pass`.
- The prompt change, repair 6, 6 cases. `casestatus` reads all six by the system text: `L1-TS-act-on-the-reason-of-a-challenge`, `L1-TS-fix-a-test-that-asserts-more-than-its-criterion`, `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner`, `L1-TS-hold-a-test-that-is-right`, `L1-TS-pass-a-literal-value-for-a-name-looked-up-at-run-time`, `L1-TS-send-a-test-written-into-the-reply-as-tests-encode`. Repair 4 also moves the first code read of the fix, hold and send cases.

A caution about the gate: run it at af04bbe1 with `--no-rerecord`. Without that flag, the gate tries 15 live re-records, five runs each (`rota/tools/gate.py` 491 to 505).

## Point 9. The 42 reds at af04bbe1

CONFIRMED: 42. `test_l1.py` gives 34. The rest of the tree gives 8, plus one `database is locked` red in `test_gauntlet.py` that passed when it ran alone. None of the 42 is a change in model behaviour caused by this pass.

- STALE, 15: the set of point 8. Four of them are frame 281's four known Tester reds (act-on-the-reason, fix-asserts-more, fix-calls-plain, pass-literal). At 0265b414 they failed on a recorded result, and now they fail STALE. Of the other 11, 10 are new reds of this pass and all 10 are STALE. The eleventh is log-the-choice, which was a red at 0265b414 too.
- Model results that were red at 0265b414 and have the same score now, 15: `ACT-TS-five-criteria-one-per-reply`, `L1-AR-a-test-that-misses-its-criterion-gets-a-decision-row`, `L1-AR-cite-the-clause-into-a-constraint`, `L1-AR-constrain-an-external-commitment`, `L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist`, `L1-DV-a-wordless-answer-leaves-a-wrong-test-alone`, `L1-DV-apply-the-answer-and-carry-on`, `L1-DV-fix-the-code-not-the-test`, `L1-LI-a-question-then-a-statement-at-the-confirm-is-the-question`, `L1-RS-say-what-you-tried-when-you-find-nothing`, `L1-TE-amend-glossary`, `L1-TE-log-the-word-you-took-one-way` (red by construction), `L1-TS-apply-a-term-and-write-the-test`, `L1-VK-amend-a-contested-item`, `L1-VK-an-outside-fact-is-the-researchers`.
- Follow-check reds, frame 144, red at 0265b414, 4: `L2-DV-name-the-block-rather-than-retry`, `L2-DV-name-the-deferred-batch-not-the-running-one`, `L1-VK-answer-a-refactor-proposal`, `ACT-TS-three-criteria-one-per-reply`.
- Other files, all in the gate baseline of f9f5cd19, 8: `test_invoke_door.py::test_a_session_with_no_batch_reads_the_root`, `test_onboarding.py::test_the_same_constraint_written_twice_is_one_gate`, the `test_templates.py` encode case of `test_scene_two_batches.py::test_a_right_call_lands`, `test_fixtures.py::test_no_case_leaves_a_reference_unwrapped`, `test_pins.py::test_with_prompt_keeps_every_pin`, `test_roles_doc.py::test_a_verb_carries_words_or_does_not_regardless_of_recipient`, and the two `test_l3.py` chains `L3-a-challenge-reaches-the-role-that-can-answer-it` and `L3-a-failed-verdict-turns-into-a-fix`.

At 0265b414 the 34 reds of `test_l1.py` give 24 reds and 10 passes. The 10 passes are the 8 Developer cases of repair 2, plus send and hold.

## Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/66edc387-a3b2-48b8-8dec-bb5b3aa63e50/scratchpad/r326p1/`.

- `reg_backup.py`: a SQLite backup of the `rota_g301` register, opened with `mode=ro`, into `reg.db` (22:40) and `reg2.db` (23:11).
- `probe_index.py`: builds the challenge case's database through `_with_repo`, then compares the index span of `close_account` with both files.
- `probe_defaults.py`: builds the defaults case, then calls `code_probe` before and after the index rows are deleted.
- `plug/r326_noprobe.py`: a pytest plugin that swaps the body of `code_probe` for the 0265b414 body. It ran log-the-choice, say-why and restore.
- `probers.py`, `sw.py`, `sw3.py`, `miss.py`: read-only queries of `case_runs` and `key_misses`.
- `modes.py`: counts the modes that have `code.probe` and do not have `code.source`.
- `owed.py`: maps each `OWED` id to its problem, and checks each id against the case ids.
- Test runs, all with `ROTA_DEV_DB` on the copy and `ROTA_MODEL=qwen3:8b`: `test_l1.py` at af04bbe1 (34 failed, 123 passed); the 34 ids again for the reasons; the 34 ids at 0265b414 (24 failed, 10 passed); `tests/rota` without `test_l1.py` at af04bbe1 (9 failed, 5131 passed, log `rest_af04.log`); the gauntlet case alone (passed); `test_case_reachability.py` with `test_index_refresh.py` (706 passed, 39 skipped).
- `casestatus --model qwen3:8b` on `reg.db` before the replays: 17 failing, 20 provisional, 6 stale, 122 green, 1 red by construction.

## Usage

- Input tokens: about 135k. Output tokens: about 20k. Total: about 155k.

## Findings

1. `rota/testkit/fixtures.py` 832 to 868 with e41580e8 (`l1_developer.yaml` 243, `l1_findings.yaml` 92). High. CONFIRMED: `probe_defaults.py` returned `[]` for the batch's `calculate_tip` from an index of 93 rows, and the note fires on an empty index. `probe_index.py` showed a span of 26 to 34 for a batch file of 19 lines. Onboarding indexes the main checkout before the batch worktree exists, and it switches off the repair 2 note on both cases of fault A. Fix: hold back e41580e8, make `_with_repo` call `indexer.refresh(conn, tree, main=False, batch_id=batch_id)` after the edit commit when `onboard` is set, then add the two lines again.
2. `tests/rota/test_case_reachability.py` 258 to 261. Low. CONFIRMED: `probers.py` showed `L1-DV-fix-what-the-verdict-names` (5 of 5) and `L1-DV-restore-what-the-finding-names` (1 of 5) probing an empty index. Both went STALE under repair 2, and the lint passes both. Rule 2 reads the brief, so it misses each mode that lists `code.probe` and does not name it. Fix: key rule 2 on `code.probe` in the mode's tools, and fix the cases that this exposes.
3. Repair 2's count, `rota/roles/api.py` 14394. Low. CONFIRMED: `r326_noprobe.py` sent `L1-DV-log-the-choice-the-criteria-did-not-make` back to its recorded `0/5`. At af04bbe1 the same case fails STALE. The stale set is 15, not 14, and the re-record list needs this case. Fix: re-record 15 cases, and quote 15 as the gate's expected stale line.
4. `tests/rota/test_case_reachability.py` 212 to 282. Low. CONFIRMED: grep finds no other use of `OWED`. No test fails when an id joins the set or names no case. Fix: assert that `OWED` is a subset of the case ids and that `len(OWED) <= 19`.
5. `tests/rota/test_l1.py` 207. Low. CONFIRMED: the run at af04bbe1 fails `L1-TE-log-the-word-you-took-one-way` as a plain `0/5`. Fix: after the STALE check, call `pytest.xfail(case["red"])` for a marked case, and fail a marked case that passes.
6. `rota/roles/api.py` 14395 to 14398. Low. CONFIRMED: `modes.py` finds `architect/deliver`, which has `code.probe` and does not have `code.source`. The note offers that mode a call it does not hold. Fix: name `code.source` only when `prompts.mode_tools(ctx.role, ctx.mode)` holds it.
7. Outside the points: the register at `C:/Users/roman/rota_g301`. Low. CONFIRMED: during this review another process wrote `key_misses` rows (23:07 to 23:09) for four other cases. `casestatus` on a copy taken at 23:11 read 12 stale, not 6. Fix: read `casestatus` for this frame from a copy taken at a known time, or from the gate's own register.
