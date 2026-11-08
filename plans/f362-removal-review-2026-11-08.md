# Frame 362, review of pass 1 of the removal wall: d833194b and 805f5fb4, 2026-11-08

The verdict is fix before the pick. Fix 1 is sound and reaches 10 of 10 Developer modes and the stray judgement. Fix 2 folds the passing rows. But its line names a read that returns 0 of 105 passing rows on the `w6.db` copy. Counts: 0 high, 2 medium, 3 low. The reviewer worktree is `C:/Users/roman/rota_r362r` at 805f5fb4. The review edited no tracked file.

## (a) The verdict on each point

1. Point 1 holds. The gate at `runner.py` 4784 to 4790 fires on every Developer wake and on the Architect `tick:touch_strayed` wake: 10 of 10 modes. The `w6.db` push holds "Do not remove that branch in _foldline" at character 1,207 (CONFIRMED).
2. Point 2 holds. `if said:` drops the block when no ruling names the batch. `batch_ruled_refs(bid)` keys the block to one batch. `RULED_CHARS` 3,000 at 4448 bounds it, with the same soft rule as before. The text is the same in every mode (CONFIRMED: one block over 10 Developer wakes, 1,144 characters on both seats).
3. Point 3 holds for the rows. The fold reaches `batches.expect`, `tests.load` and `tests.consult`, 3 of 7 blocks. No brief line in `rota/roles/prompts/*/` reads inherited rows one by one. No seat loses a row that its brief uses (CONFIRMED by grep).
4. Point 4 fails. The line is a promise that the doors do not keep. A call of `tests.load` on the copy shows 0 of 105 passing inherited rows (CONFIRMED). See finding 1.
5. Point 5 is by sample, not by construction. The key order is fixed. The size of the folded `batches.expect` is not bounded. See finding 2.
6. Point 6: 0 stale cases. The two commits change no brief and no `.tools` file, so no `prompt_hash` or `system_hash` changes. The gate under `qwen3:8b` shows 0 new reds and stale (0). So no recorded case renders a changed push. No `qwen3.5:9b` case is stale by the same reason (PLAUSIBLE: the push does not depend on the model).
7. Point 7: 3 of 3 planted faults turn a test red. The related set: 549 passed, 7 skipped. The file: 9 passed.

## (b) Findings

1. `rota/core/runner.py` 2121 and 1166 to 1169, `INHERITED_LINE`. Severity medium. CONFIRMED. The line says "A call of tests.load returns their rows." On the `w6.db` copy, a call is cut at `RESULT_CHARS` 6,000. The call of `tests.load` shows 0 of 105 passing rows, because 57 red bodies of about 3,900 characters come first. A call of `batches.expect` shows 37 of 105. A call of `tests.consult` shows 52 of 105. No read takes a test id. So a seat that follows the line spends a turn and does not get the row. Fix: drop the second sentence of the line, so it reads "<n> inherited tests pass, not shown.", or add an `ids` argument to `tests.load` in a pass of its own.
2. `rota/core/runner.py` 2133 to 2146 and `rota/roles/api.py` 28773, the residue. Severity medium. CONFIRMED by measurement. On the copy, `[batches.expect]` starts at 1,999 and `[code.diff]` at 9,314, and `[removed lines]` is at 9,556. Each red or unrun inherited row costs about 107 characters in `batches.expect`. About 97 more such rows put `[removed lines]` past 20,000. The fold takes only rows whose latest run in the batch passed. So a batch with many red inherited rows, or a wake before the base run, puts the base text behind the cut again. Fix: on `tick:touch_mistaken`, push `code.diff` before `batches.expect`, which is the first option of F2 in the read.
3. `rota/core/runner.py` 1144 to 1146, the head sentence. Severity low. PLAUSIBLE: read, not run on a model. "Calling any of these again returns the same thing" is false for a folded block. The fold line says the opposite. Fix: change one of the two sentences in the same pass as finding 1, or drop the call claim of the fold line.
4. The cover of the suite. Severity low. CONFIRMED by the gate: 0 stale and 0 new reds. No recorded case renders the fold line or the ruled block on a fix wake. The fold also reaches the Critic `review` and `answer`, the Architect `exhausted`, the Developer `exhausted` and `findings_exhausted`, and three Tester modes. So no model response to the new push is measured. Fix: add inherited rows and a ruling of his to the fixture of `L1-DV-put-back-a-removed-block`, and record it.
5. `tests/rota/test_f362_removal_push.py` 213 to 227, outside the points. Severity low. PLAUSIBLE: read. The 10-mode test passes `batch_id="b1"` to the sandbox by hand. It does not prove that `_batch_of` gives `answer` and `challenge` wakes a batch. `_batch_of` falls back to the one running batch, so the live path holds today. Fix: build the two message wakes through `_batch_of`, as `_prompt` does.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/0d047fa7-9b87-4f76-a8a4-18bf24ea3678/scratchpad/r362/`.

- `p1_copy.py`: copied `w6.db` to `w6copy.db` with the SQLite backup API. It opened the original with `mode=ro`.
- `p1_push.py`: built the pushes of Developer `touch_mistaken`, Architect `touch_strayed` and Critic `review` on `b1`. Results: 33,512, 12,833 and 32,046 characters. His words are at 1,207 and 572 in the first two, and not in the Critic wake.
- `p5_offsets.py`: the block offsets of the restore wake and the cost of each inherited row. The copy holds 105 pass, 56 fail and 1 error among the inherited rows, and 0 with no run.
- `p4_call.py`: called `tests.load`, `batches.expect` and `tests.consult` and rendered each at `RESULT_CHARS`. It counted the passing inherited ids that show.
- `plug/fault_gate.py`, `plug/fault_one_whole.py`, `plug/fault_red_folded.py`: pytest plugins that patch `rota.core.runner` in memory, loaded with `-p`. No tracked file changed. Results: 3 failed, 3 failed and 1 failed of 9.
- `pytest tests/rota/test_f362_removal_push.py`: 9 passed. The related set with `-k "push or runner or inherit or touch or ruled or critic"`: 549 passed, 7 skipped.
- `casestatus --model qwen3:8b` and `--model qwen3.5:9b` in the worktree: 203 never measured, because the worktree has no register. The run created an empty ignored `tests/rota/cassettes.db`. That file turned 7 skipped `test_l1` cases into 7 failures in one related run. The review deleted the file, and the rerun gave 549 passed, 7 skipped.
- The gate with `ROTA_DEV_DB=D:/repos/rota/tests/rota/cassettes.db`: 33 failed, 7223 passed, 55 skipped, 16 xfailed, new reds 0, stale 0, 2,189.5 seconds. The gate had no baseline in the worktree and stored one in the ignored `.rota-gate.json`. So its "new reds (0)" compares with nothing. Against the main baseline at 5bf28154, 1 red is new: `test_f16_answered_mark.py::test_the_mark_has_one_writer`. It names `lifecycle.py:discharge_touch_notes`, which c2fa3f40 added before 70e8e9b2. The two commits do not touch `lifecycle.py`. So that red is older than this pass.
- Caution for the session: the gate also ran `prepare_register` on the shared register. A second gate, PID 2996 from 07:42, ran at the same time.

## (d) Usage

- Input tokens: about 110k, an estimate, because the harness count is not visible to the reviewer.
- Output tokens: about 14k.
- Total: about 124k.

fix before the pick

## Second look: pass 1b, abc32d2f

The verdict is pick. Both medium findings are fixed, and low 4 is the only finding left. The review read abc32d2f in the implementer's worktree `C:/Users/roman/rota_p362r` and ran its tests there. The review did not run `git checkout` in `C:/Users/roman/rota_r362r`, because the reviewer's rules forbid a git command that changes a tree. No tracked file changed, and the gate did not run.

1. Medium 1 is fixed (CONFIRMED). `INHERITED_LINE` at `runner.py` 2122 is now "{n} inherited tests pass, not shown." It names no read. The guard test asserts that no "A call of" text is left. Low 3 goes with medium 1, because the fold line now makes no claim about a call.
2. Medium 2 is fixed by construction (CONFIRMED). `push_working_set`, at about `runner.py` 4761 to 4771, puts `code.diff` right before `batches.expect` on `tick:touch_mistaken`. The `START_RULED_KEY` block is added after that step, so his words stay first. On the `w6.db` copy, the offsets are now: his words at 801, `[code.diff]` at 1,999, `[removed lines]` at 2,241 and `[batches.expect]` at 5,295. Inherited rows no longer move the base text. The wake head, his newest reply and the diff are still not bounded, but they are not this wall.
3. The planted fault: a pytest plugin put `batches.expect` before `code.diff` on the restore wake, in memory. `test_the_removed_lines_stand_before_200_red_inherited_rows` went red: 1 failed, 9 passed. The probe is `scratchpad/r362/plug/fault_expect_first.py`.
4. Low 5 is fixed (CONFIRMED). The ten-mode test writes real `answer` and `challenge` messages with refs `["c1"]`. It asserts that `_batch_of` gives `b1`, and it builds the sandbox from that batch.
5. Low 4 is left, as the implementer says. No recorded case renders the fold line or the ruled block on a fix wake, and a recording needs a model run.
6. The tests at abc32d2f: the pass's file gave 10 passed. The related set gave 550 passed, 7 skipped. The offset probe is `scratchpad/r362/p5_offsets_1b.py`.

Second look usage: about 15k input tokens and 3k output tokens, an estimate.

pick
