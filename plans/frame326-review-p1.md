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

## Review 1b at a1db0e89

Date: 2026-10-26. Read-only review of 0cd32362, 01be0fb1, f2c5d668, f8168ce7 and a1db0e89 above af04bbe1. The tree is a `git archive` of a1db0e89, extracted into the scratchpad folder `r326p1/a1db`. The register is the same read-only copy `reg.db`.

Verdict: accept all five commits for the branch. Do not re-record the 18 STALE cases yet. First make `index_batch` leave the run in the state a delivery night has (answer 2). Then give `L1-DV-say-why-the-test-cannot-pass` and `L1-TS-act-on-the-reason-of-a-challenge` their `repo:` blocks (answer 4).

### 1. The high finding is closed

CONFIRMED. `probe_1b.py` builds the defaults case at a1db0e89. Its `repo:` keys are `batch`, `edit`, `index_batch` and `message`, and the case has no `onboard`. `code.probe("calculate_tip")` returns `main.py::calculate_tip`, lines 0 to 2, from 96 rows. Review 1 got `[]` from 93 rows. The diff removes both `onboard: true` lines of e41580e8 (`l1_developer.yaml` 240 to 245, `l1_findings.yaml` 88 to 93), and `index_batch: true` replaces them. `_with_repo` calls `indexer.refresh(conn, tree, main=False, batch_id=batch_id)` after the edit commit (`rota/testkit/fixtures.py` 880 to 888). That is the call that `runner._refresh_index` makes on a night.

### 2. The fixture index against the night index

The rows are the same, the areas are different, and the onboarding phase is wrong for delivery. `probe_1b.py` builds the defaults case two ways. The first way is `index_batch` alone. The second way adds `onboard`, which is the night order: onboard on main, then refresh the batch tree.

- Rows: 96 in each. Every grain, kind and line span is the same (the difference of the two sets is empty).
- Areas: with `index_batch` alone, every row has area `.`. With the night order, the rows carry `.`, `src/auth`, `src/billing`, `src/catalog`, `src/notify`, `src/store` and `web`. The reason is that `refresh(main=False)` keeps the areas that were there before, and with no onboarding there were none. `code.probe` returns the `area` column, so a probe of a file under `src/` shows `.` where a night shows the area. Most of the 18 STALE recordings probe a file under `src/`.
- Phase: an empty index used to give `onboarding_phase` the value `none`. Any index gives `frame` now. The night order also gives `frame`, because no session has attested the partition. On a night, a batch is delivered only after onboarding ends, at phase `done`.

The implementer's question: should `index_batch` also write the onboarding record? Yes, but the record must be the state of delivery, not the output of `boot.onboard`. The second option, a chain that sets `onboard` with `index_batch`, does not work. `probe_1b.py` shows `L3-a-failed-verdict-turns-into-a-fix` with `tick:frame` still offered under the night order, and only `tick:constraint_zero` goes away. The record a delivery night has:

1. The partition is pinned, so each row carries its area.
2. Each onboarding phase is closed, so `onboarding_phase` returns `done`.
3. Each area has a survey record, so constraint zero binds no grain and `tick:constraint_zero` does not fire.

The single-session L1 cases wake directly. So the phase does not reach their prompts, and seven of the 17 cases still replay. The areas do reach the prompts, through the probe rows. So build the record before the re-record. Otherwise the 16 recordings that probe the index go STALE a second time when the record lands.

### 3. The low findings are closed

CONFIRMED, all five:

- Finding 2: rule 2 reads `"code.probe" in tools` (`test_case_reachability.py` 250 to 258), and it accepts `index_batch`.
- Finding 3: the count is now 18, and the implementer quotes 18.
- Finding 4: `test_the_owed_set_only_shrinks_and_names_real_cases` fails when an id names no case, when the set grows past `OWED_CEILING = 10`, and when the set shrinks while the ceiling stays the same.
- Finding 5: `test_l1.py` fails a marked case that passes, then calls `pytest.xfail` after the STALE check. The run shows `XFAIL ... L1-TE-log-the-word-you-took-one-way - red by construction`.
- Finding 6: the note names `code.source` only when the mode's tools hold it. A pin covers `architect/deliver`.

A new low finding is in the fallback of findings 2 and 6. `prompts.available(role)` returns mode names, not functions (`rota/roles/prompts.py` 195 to 200). So the fallback `_wake_mode_tools(ctx) or _prompts.available(ctx.role)` (`api.py` 14400) never holds `code.source`. For the same reason, `prompts.mode_tools(role, mode) or prompts.available(role)` (`test_case_reachability.py` 247) never holds a code read. Today every mode has a `.tools` file (`modes` count: 0 without one), so neither fallback runs. A new mode without a `.tools` file would get "everything the role has", and it would pass the lint without a check.

### 4. The 18 STALE cases

CONFIRMED: 18. `test_l1.py` and `test_l3.py` at a1db0e89 give 39 failed, 124 passed, 1 skipped and 1 xfailed. When `L3-scope-becomes-a-ticket-with-criteria` runs alone, it passes. It failed only on `database is locked`. So there are 38 reds: 18 STALE and 20 that were in the 0265b414 set. This matches the implementer.

- The probe note, 9: `L1-DV-act-on-an-answered-challenge`, `L1-DV-ask-when-the-test-contradicts-its-criterion-at-the-fix-wake`, `L1-DV-build-a-clear-criterion`, `L1-DV-challenge-a-test-with-a-long-body`, `L1-DV-fix-what-the-verdict-names`, `L1-DV-log-the-choice-the-criteria-did-not-make`, `L1-DV-read-the-map-not-the-whole-file`, `L1-DV-restore-what-the-finding-names`, `L1-DV-say-why-the-test-cannot-pass`.
- The Tester challenge prompt and repositories, 6: `L1-TS-act-on-the-reason-of-a-challenge`, `L1-TS-fix-a-test-that-asserts-more-than-its-criterion`, `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner`, `L1-TS-hold-a-test-that-is-right`, `L1-TS-pass-a-literal-value-for-a-name-looked-up-at-run-time`, `L1-TS-send-a-test-written-into-the-reply-as-tests-encode`.
- The batch index, 3: `L1-DV-give-the-new-parameters-defaults`, `L1-DV-a-wordless-answer-on-a-right-red-test-is-carried-on`, `L1-DV-take-a-mistake-out`.

A re-record can absorb each change. Two changes need a decision first:

- Two STALE cases are still in `OWED` and have no repository: `L1-DV-say-why-the-test-cannot-pass` and `L1-TS-act-on-the-reason-of-a-challenge`. The run logs `WorktreeError: no project_root in config` for the second case. A re-record now would measure fault B, a refusal of `code.source`, and both cases would go STALE again when their `repo:` blocks land.
- The 16 cases that probe the index would record area `.` (answer 2).

`L1-DV-give-the-new-parameters-defaults` and `L1-DV-say-why-the-test-cannot-pass` are pinned to qwen3.5:9b, so their re-record needs that model on the card.

### Findings of review 1b

1. `rota/testkit/fixtures.py` 880 to 888. High for the order of the re-record, not for the branch. CONFIRMED: `probe_1b.py` shows that the rows are the same as the night's rows. It also shows area `.` on all 96 rows against six areas on a night, and phase `frame` in place of `done`. Fix: make `index_batch` pin the partition, close the onboarding phases and record a survey for each area before the refresh. Then re-record.
2. `rota/roles/api.py` 14400 and `tests/rota/test_case_reachability.py` 247. Low. CONFIRMED by a read: `prompts.available` returns mode names, so each fallback holds no function. Fix: treat a `None` from `mode_tools` as the role's whole namespace, for example `build(role, conn).functions()`.
3. `OWED`, the two STALE cases without a repository. Low. CONFIRMED: the run logs `no project_root` for `L1-TS-act-on-the-reason-of-a-challenge`. Fix: write their `repo:` blocks before the re-record, or leave both cases out of the re-record.

Probes of review 1b, in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/66edc387-a3b2-48b8-8dec-bb5b3aa63e50/scratchpad/r326p1/`: `a1db/` (the `git archive` of a1db0e89), `probe_1b.py` (the defaults case and the chain, built with `index_batch` alone and in the night order), `l1l3_a1db.log` (`test_l1.py` and `test_l3.py` at a1db0e89), and the two locked chains run again alone.

Usage of review 1b: input about 45k, output about 9k, total about 54k.

## Review 1c at 647c34d0

Date: 2026-10-26. Read-only review of 103f3dc5 and 647c34d0 above a1db0e89. The tree is a `git archive` of 647c34d0, extracted into the scratchpad folder `r326p1/b647`. The register is the same read-only copy `reg.db`.

Verdict: accept both commits for the branch. Re-record 16 of the 18 STALE cases now. Hold `L1-DV-say-why-the-test-cannot-pass` and `L1-TS-act-on-the-reason-of-a-challenge` until each case has a repository. A re-record now would record fault B, a refused `code.source`. The implementer's shared source file, `repo.edit_from`, is the right general repair, because three Click cases need the same 624 lines.

### 1. The finding on the re-record order is closed

CONFIRMED. `probe_1b.py` against 647c34d0 shows these results:

- With `index_batch` alone, the defaults case carries the areas `.`, `src/auth`, `src/billing`, `src/catalog`, `src/notify`, `src/store` and `web`. These are the same areas as in the night order, and the phase is `done`.
- The 96 rows are the same in both shapes.
- `code.probe("calculate_tip")` returns the batch's row. Its area is `.` because `main.py` is at the root. A night gives the same area.
- On `L3-a-failed-verdict-turns-into-a-fix`, `predicates.frame` and `predicates.constraint_zero` offer nothing in both shapes.

### 2. The written state against a night's state

`probe_1c.py` builds the defaults case in two shapes. The first shape is `index_batch` alone. The second shape adds `onboard`, so that `boot.onboard` runs first. The script then compares every table. Four tables differ:

- `code_lexicon`, 0 rows against 23. Only onboarding reads the table: `pending_terms`, `_define_wakes`, `stresses` and `code.front`. Only `vision_keeper/orient` holds `code.front`. No delivery seat sees the difference.
- `config`, 3 keys against 7. The night shape adds `created_at`, `lexicon_bigrams`, `project_branch` and `project_commit`. In a session, only the frame session reads `project_commit` (`runner.py` 6581). `compare.py` and `cli.py` read the keys for a person, not for a seat. No delivery seat sees the difference.
- `survey_records`, 20 rows against 40. The extra rows are the term records that close the define phase in the night shape. Only `surveys.consult` and `code_gaps` read the table. The modes that hold `surveys.consult` are the four survey and blindspot modes, and no delivery mode holds it.
- `constraints`, 1 row against 2. In the night shape, `k0` stays as a row with no bindings after every area has a survey. `constraints_for_grains` reads a constraint with no bindings as global. So on a night, `model.consult` returns `k0`, "this area has not been surveyed", for every grain set (observed: `probe_k0.py`, `['k0', 'k_d389ff']` against `['k_d389ff']`).

The `k0` difference is the only difference that a seat's prompt can show. It reaches a seat only through `model.consult`. Ten Architect modes and `vision_keeper/reorient` hold that call. No Developer or Tester mode holds it. None of the 18 STALE recordings calls `model.consult` (observed: `consult.py`, 0 of 18). So a re-record of the 18 does not record it. Two `architect/structural_review` cases have `index_batch` and still replay, so their recordings do not change.

Outside the points, the `k0` row on a night is probably a defect of the night, not of the fixture. `boot.refresh_constraint_zero` (`rota/onboarding/boot.py` 254 to 266) keeps the `k0` row when no coded area is left unsurveyed, and it deletes the row only when no coded area exists. So after onboarding, each night shows "this area has not been surveyed" as a global constraint to every seat that consults. The constraint's own text says that a survey removes an area from it. The fixture leaves the row out, which is the state that the text describes. PLAUSIBLE for real nights: the probe ran the night's own functions, and no night database was read. Fix: delete `k0` in `refresh_constraint_zero` when `remaining` is empty. Then the fixture matches the night.

A low inconsistency: `L1-AR-a-diff-no-constraint-binds-files-k0` seeds its own `k0`, "everything in this repository no survey has reached". With `index_batch`, the fixture records a survey for every area. The seat cannot see the surveys, because `structural_review` does not hold `surveys.consult`, and the case still replays. So nothing changes now.

### 3. No expected count shifts

CONFIRMED. Without `onboard`, `_delivery_index` writes rows to `code_index`, the area records, `survey_records`, `config` and `challenges`. It writes no row to `constraints`, `constraint_bindings` or `ledger`. The probe shows that the fixture's `constraints` hold only the seeded `k_d389ff`. No `index_batch` case also sets `onboard`, so `boot.refresh_constraint_zero` never runs for one of them (observed: `expects.py`).

The expectations of the 19 `index_batch` cases name `findings`, `batches`, `ledger` and `touch_strays`. Their forbidden writes name `constraints`, `criteria`, `items`, `tests`, `tickets`, `verdicts`, `glossary_terms` and `findings`. None of these cases counts `survey_records` or `challenges`. The grader counts the session's own writes after `snapshot_versions`, and the fixture runs before that call (`fixtures.py` 1287 to 1292). So a seeded record cannot enter a count.

### 4. The STALE set

CONFIRMED: 18, with the same names as at a1db0e89. `test_l1.py` and `test_l3.py` at 647c34d0 give 38 failed, 125 passed, 1 skipped and 1 xfailed. Of the reds, 18 fail `STALE`, and `diff` of the two STALE lists is empty. The other 20 are the reds that were in the 0265b414 set, and the xfail is the Terminologist case. This is the gate's expected stale line.

### Findings of review 1c

1. The `k0` row on a night, `rota/onboarding/boot.py` 254 to 266. Low, outside the frame. PLAUSIBLE: `probe_k0.py` shows the night shape returning `k0` from `model.consult` after every area has a survey. Fix: delete `k0` when no coded area is left unsurveyed. That is a frame of its own.
2. The two STALE cases in `OWED`. Low. CONFIRMED in review 1b, and still open. Fix: build `repo.edit_from` with one shared Click source, then re-record both cases.

Probes of review 1c, in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/66edc387-a3b2-48b8-8dec-bb5b3aa63e50/scratchpad/r326p1/`: `b647/` (the archive), `probe_1b.py`, `probe_1c.py` (the table counts in two shapes), `probe_k0.py` (`constraints_for_grains`, `model.consult` and `needs_structural_review` in two shapes), `expects.py`, `consult.py` (a read-only query of `case_runs`), and `l1l3_b647.log` with `stale_b647.txt`.

Usage of review 1c: input about 40k, output about 8k, total about 48k.
