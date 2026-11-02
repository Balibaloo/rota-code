# Review p1 of frame 360, pass 1, commit 06004e13

## Result

Hold for one short pass. The ruled shape lands, and the measure on the dry2w3 copy passes. Two medium findings put "built" in front of the seat for a claim, or stop a true claim. Counts: high 0, medium 2, low 6. The fixes cost about 5 cycles in total.

- F1, medium: the shift page says "The change b1 is built" for a live claimed batch.
- F2, medium: a refused test write with words other than the test-file words blocks the claim.
- F3 to F8, low: the notes tail, a weak fourth control, the per-session exclusion, boot reconcile, the stale mark, and a scope question (outside).

The probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ce483c7b-be58-4d58-bfc4-db1081518842/scratchpad/r360/`.

## Point 1. The ruled shape lands

Verdict: holds. The test measures all four controls and the harness as a fifth.

- The test file passes: `9 passed in 87.00s` (observed: pytest of `tests/rota/test_f360_claimed_batch.py` in the worktree).
- The fixture copies `dry2.db` with its wal and shm to `tmp_path`, and it never opens the source (observed: test file lines 80 to 83).
- It clears the key `developer|tick:batch_start|b_2` on the copy (observed: lines 96 to 97).
- It asserts the control and the result for each of the four controls: `head_commit` None then the fork, `tick_batch_start` one wake then `[]`, `tests_missing` no wake then a wake, `mergeable` "nothing committed" then another reason (observed: lines 115 to 136).
- The fourth control asserts only the absence of one string. The real reason after the claim is `criteria without a test: c_10, c_5` (observed: probe `test_probe_p1.py`). See F4.

## Point 2. The false claim

Verdict: holds. The red path goes back to the Developer, and the real commit takes the head.

Probe `test_probe_p2.py` on the `world` fixture of the pass (observed):

1. After the claim, `head_commit` and `claimed_head` are both `e50e1a5`, and the status is `running`.
2. With a failing test row and a `fail` run at the fork, `tests_failing` gives `('developer', 'tick:tests_failing', ('b1',), 'attempt 1')`.
3. A Developer `code.write` to `src/auth/__init__.py` and `code.commit` give `committed: True` and head `fb4ee3f`.
4. After the land, `head_commit` is `fb4ee3f` and `claimed_head` stays `e50e1a5`. The mark stops matching. It is not cleared (see F7).
5. `harness` owes a run for `b1` at the new head.
6. After a pass run at the new head and the merge, the page says "Done: 1 change built, tested and merged." and no claim line.

## Point 3. The refusal test

Verdict: holds on the program side. It fails on part of the test side (F2).

- Every `code.write` refusal goes into `ctx.refusals` through the wrapper (observed: `rota/core/sandbox.py` 5207 to 5212). `code.write` is the only write op (observed: grep of `@op("code"`).
- A path outside the tree raises in `_within` inside the op, and a manifest raises in `_fence.check_manifest` (observed: api.py 22040, 22743). Both block the claim. That is the right side, because the session meant a change (reasoned).
- A test-file write that fails an earlier door blocks the claim. A write of invalid Python to `tests/test_formatting.py` gives "is not valid Python", and the commit gives no claim. A valid write to the same path gives the test-file words and a claim (observed: probe `test_probe_p3.py`, 2 cases). The test-file check is at api.py 23066, after the span, parse and duplicate checks at 22087 to 23036 (observed). See F2.
- On dry2w3, the four refusals of s63 all carry the test-file words, so s63 claims (observed: `q3.py` on the copy, the turns of s63).
- A discard is not excluded. A discard happens when a session ends with no commit, so that session never reaches the branch. The next attempt starts on a clean tree, and its empty commit claims (reasoned: `boot.discard_running`, `lifecycle.discard_uncommitted`). The same holds for the `bg_2` of night 163: the exclusion is per session, and the next attempt with no refusal claims (reasoned). Each false claim costs one Tester session, one harness run and one `tests_failing` wake. Before, the cost was up to three empty starts and the ladder (reasoned: design page 3 A). See F5.

## Point 4. The pages

Verdict: the state line holds. The shift page does not (F1).

Grep of `merged` and `built` in `rota/roles/principal.py` (observed). The lines that show a batch to the principal:

- 353 to 374, the state line. A merged claim reads `CLAIMED_LINE`, "No code changed." (observed: the test of the pass and probe p4).
- 386 to 398, the parked-notes tail. It appends to `out[-1]`, which is now `CLAIMED_LINE` when a claim merged. The page reads "No code changed. These tests show the code already does this. They carry 1 choice the team made where you said nothing." (observed: probe `test_probe_p4.py::test_notes_tail`). See F3.
- 401 to 404, the re-survey line. It names no batch, so it does not say "built" (observed).
- 2793 to 2804, `merged_removal_line`. It reads `touch_strays`, and a claim writes none, so it says nothing for a claim (reasoned: the claim branch stages one `batches` write only).
- 2512 to 2548, `_shift_where` and `_built_words`. For a live claimed batch, the page reads "approved. The change b1 is built, and no test has run yet." (observed: probe `test_probe_p4.py::test_live_claim_words`). See F1.
- 3536 to 3547, `built` in the ruling path. It is a list of batch ids, not a page line (observed).
- No Done page exists after a merge. The agenda prints `render_state` when no ask waits, so the agenda merge line is the state line (observed: `rota/cli.py` 745 to 750).

## Point 5. Older databases

Verdict: holds.

- Probe `q5.py` copied dry1w14 and dry2w5 with wal and shm, and ran `init_db` twice on each copy (observed).
- Before: no `claimed_head`. After the first run: the column exists. After the second run: the column exists once, with no error.
- No table lost a row on either copy, and no table was added. `batches` kept 1 row on dry1 and 2 rows on dry2w5.
- `render_state` on each copy says "Done: 1 change built, tested and merged." as before.
- `init_db` runs the `ALTER` only when `_has_column` is false, so a second run does nothing (observed: db.py 461 to 464).

## Point 6. Recorded cases

Verdict: at most 3 cases can go STALE. The gate gives the final count.

- A case reaches the claim only if its Developer has `code.commit`, its batch has no head, and a recorded run commits an unchanged tree (reasoned: api.py 24055 to 24070).
- Three Developer cases seed a batch with no `repo.edit` and no `head_commit`, and give `code.commit` (observed: a yaml scan of `tests/rota/cases/`): `L1-DV-apply-the-answer-and-carry-on`, `L1-DV-build-a-clear-criterion`, `L1-DV-log-the-choice-the-criteria-did-not-make`. `L1-DV-elect-on-a-revoked-item` has no `code.commit` (observed: `reopen.tools`).
- All three have live qwen3:8b runs that call `code.commit` before any `code.write`. The qwen3:8b cassettes hold the old note in the user turn after that call (observed: `q13.py` on `tests/rota/cassettes.db`, opened read-only and immutable). The key of the next turn holds the tool result, so the new note misses the cassette (reasoned).
- Every other Developer case seeds a head through `repo.edit` or the batch row, so its note does not change (observed: `rota/testkit/fixtures.py` 1007 to 1017).

## Point 7. Forbidden areas

Verdict: holds.

- The diff stat from 0160747f to 06004e13 over `rota/roles/prompts` and `rota/LAWS.md` is empty (observed).
- The challenge and escalation branch keeps its words and returns before the claim branch (observed: the diff, api.py 24034 to 24040). The guard tests of the pass pass (observed: the run of point 1).
- `lifecycle.mergeable` and `predicates.review` are not in the diff (observed: the stat lists five files). The merge gate of law 8 runs unchanged.
- The schema change is one column in `CREATE TABLE batches` and one `ALTER TABLE ... ADD COLUMN` (observed: the diff). No CHECK changes, so no rebuild fires (reasoned).

## Point 8. The Done line and its claim

Verdict: the line shows only after the merge, and only after green tests.

- The line counts batches with `status = 'merged'` only (observed: principal.py 363 to 366).
- The only loop writer of `merged` is `lifecycle.merge`, reached through the `merge` predicate (observed: the map of `batches` writers, predicates.py 1803 to 1820).
- The `merge` predicate needs a Critic `pass` and `mergeable` None. `review` wakes the Critic only when every run at the head passes and every live criterion has its own test in the batch (observed: predicates.py 1499 to 1530).
- So a claimed batch whose tests never ran cannot show the line through the loop (reasoned). A direct call of `lifecycle.merge` skips the gate, as the merge test of the pass does. No loop path calls it so.
- Before the merge, the shift page says "built" (F1).

## Findings

1. **F1, medium, CONFIRMED.** `rota/roles/principal.py` 2535 to 2548. `_built_words` says "The change b1 is built, and no test has run yet." for a live claimed batch (probe p4). The ruling puts "No code changed" in front of the seat. Fix: when `claimed_head = head_commit`, say that no code changed and that the tests check the claim. 2 cycles.
2. **F2, medium, CONFIRMED.** `rota/roles/api.py` 23066 against 22087 to 23036. A Developer write to a test file that fails the span, parse or duplicate door carries other words, and it blocks the claim (probe p3). A weak model with a bad escape then falls back to three empty starts, the wall of this frame. Fix: put the Developer test-file check before the span and parse doors, or keep the path in `ctx.refusals`. 2 cycles.
3. **F3, low, CONFIRMED.** `rota/roles/principal.py` 386 to 398. The notes tail appends to `CLAIMED_LINE`, so "They carry" reads as "these tests carry" (probe p4). Fix: append the tail to the Done line, or give the tail its own line. 1 cycle.
4. **F4, low, CONFIRMED.** `tests/rota/test_f360_claimed_batch.py` 136. The fourth control asserts only `!= "nothing committed"`. The real reason is `criteria without a test: c_10, c_5` (probe p1). The test also skips on any machine without the scratchpad copy. Fix: assert the reason in full. 1 cycle, with F1.
5. **F5, low, PLAUSIBLE.** `rota/roles/api.py` 24057. The exclusion reads the refusals of this session only. A session after a discard, or after a session with refused program writes, claims. A probe needs a two-session sandbox on one batch. Each false claim costs one Tester session and one harness run, and the red tests send it back. Fix: none now. Count false claims on dry run 3. 0 cycles.
6. **F6, low, PLAUSIBLE.** `rota/core/boot.py` 157 to 168. A merge conflict defers a claimed batch after the "rota: tests of" commit. A restart then writes that commit as `head_commit`, the mark stops matching, and a later merge reads "built". A probe needs a conflicting merge and a boot. Fix: leave it until a night shows it. 0 cycles.
7. **F7, low, CONFIRMED.** `rota/roles/api.py` 24077. A real commit leaves `claimed_head` at the fork (probe p2: `e50e1a5` against head `fb4ee3f`). Only the equality reader is safe. A reader of `claimed_head IS NOT NULL` alone misreads. Fix: a comment on the column that names equality as the only test, or a NULL write on a real commit. 1 cycle.
8. **F8, low, PLAUSIBLE, outside.** `rota/roles/api.py` 24034 to 24037. A message on the `triage` route does not count as sent, so a session that asked a scope question and commits an unchanged tree claims. A probe needs a triage message in `ctx.outbound`. Fix: decide whether a scope question excludes a claim. 0 to 1 cycle.

## Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ce483c7b-be58-4d58-bfc4-db1081518842/scratchpad/r360/`. The pytest probes ran from the worktree root with `ROTA_MODEL=qwen3:8b`, `-p no:xdist` and `--rootdir .`.

- The test file of the pass, in the worktree: 9 passed.
- `test_probe_p1.py`: the `dry2w3` fixture of the pass, a claim, then `mergeable`. It printed `criteria without a test: c_10, c_5`.
- `test_probe_p2.py`: the `world` fixture, a claim, a red run, a real write and commit, a green run and the merge.
- `test_probe_p3.py`: a valid and an invalid write to `tests/test_formatting.py`, then `code.commit`.
- `test_probe_p4.py`: `_built_words` on a live claim, and the state page with one claim, one build and one parked note.
- `q3.py`: the calls and refusals of s63 to s65 on a copy of dry2w3 in `r360/`.
- `q5.py`: `init_db` twice on copies of dry1w14 in `r360/d1/` and dry2w5 in `r360/d5/`.
- `q7.py` to `q13.py`: read-only, immutable reads of `D:/repos/rota/tests/rota/cassettes.db` for the empty-commit note, and a yaml scan of `tests/rota/cases/` for Developer cases with no head.

## Usage

The reviewer has no exact meter. The estimate is about 130k input tokens and about 16k output tokens, about 146k in total. The work went past the cap of 30k in the brief, mostly on the cassette search of point 6.

## Pass 1b

Stands. Commit 11eea04d fixes F1, F2, F3, F4, F6 and F7, and the probes confirm each fix. No new high or medium finding appears. The refusal record changes no recorded case.

- The test file of the pass now passes 14 of 14 at 11eea04d (observed: pytest in the worktree, 114 s).
- F1, fixed, CONFIRMED. The shift page reads "approved. The change b1 changes no code. The team claims that the code already does this, and the tests check the claim. No test has run yet." (observed: `test_probe_1b.py::test_shift_and_boot`).
- F2, fixed, CONFIRMED. The sandbox keeps the path as the fourth field, and the claim decides the side by the path (observed: the diff, sandbox.py 5212 to 5215, api.py `_program_write_refused`). A write to `tests/test_formatting.py` that the parse door refuses still claims. A write to the same path that the span door refuses still claims. A refused write to `src/auth/__init__.py` from the parse door blocks the claim (observed: `test_probe_1b.py::test_refusal_sides`, 3 cases).
- F3, fixed, CONFIRMED by the new test of the pass. The tail joins the Done line only, and the claimed line is its own line (observed: principal.py diff, `test_the_notes_tail_does_not_join_the_claimed_line`).
- F4, fixed. The measure test now asserts the full reason of the gate (observed: the test file diff, the run above).
- F6, fixed, CONFIRMED. After a claim, the tests commit and a deferred status, `reconcile_worktrees` moves the head to `b356002`, and `claimed_head` moves with the head (observed: `test_probe_1b.py::test_shift_and_boot`).
- F7, fixed, CONFIRMED. A real commit after a claim gives `claimed_head` None and the head `21f3d1f`. After the merge, the page says "Done: 1 change built, tested and merged." (observed: `test_probe_p2.py` rerun at 11eea04d).
- The refusal record: every reader of `ctx.refusals` indexes the tuple or unpacks it with `*_` (observed: grep of `refusals` in `rota/` at api.py 2955, 3003, 3416, 4685, 4719, 14470 and db.py 1729, 2142). The tuple never enters a prompt, so no cassette key changes (reasoned). The commit write adds `claimed_head` only on a batch with a claim, and no recorded case seeds a claim (reasoned: point 6).
- F5 and F8 stay open as low, as pass 1 left them (reasoned: the diff does not touch them).
- Usage for pass 1b: about 25k input tokens and about 4k output tokens, about 29k in total. The work went past the cap of 10k because of the probe runs.
