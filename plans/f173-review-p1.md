# Review of pass 1, frame 173: the restore of a removed statement by the structure

Commit 207a553d on d7f88ca1, read in the worktree `C:/Users/roman/rota_f173r`. Read-only. Written 2026-11-10.

## (a) The verdict

**Fix before the pick.** The restore puts the fork bytes back and commits with no model. Two high findings stand: an untracked Developer file lands in the structure's commit, and a partial restore drops an unrestored mistake from the gate.

1. CONFIRMED. The head file equals `git show fork:path` byte for byte after the restore, line 130 included, LF endings kept. Probe P1.
2. CONFIRMED with one departure. A changed line between the anchors returns "the fork's context around the statement changed at the head" and writes no commit. A repeated anchor line returns no reason: the rule walks to the next unique line, checks the lines between, and restores at the fork place, once, in both the repeated line and the repeated block probes. A statement that stands twice in the fork and is gone twice returns no reason: both go back for the path grain, one for an owner grain, each at its fork place. The brief expected a reason in the second and third case. The probe shows a correct restore instead, so no defect. Probes P2a, P2b, P2b2, P2c.
3. CONFIRMED, with finding 1. `worktrees.commit` makes the commit, `sessions` holds 0 rows, and the message is "rota: restore <statement> in <grain>, ordered by the Architect's judgement". `git status --porcelain` is empty before and after. A dirty tracked file returns "the worktree holds uncommitted changes" and no commit. An untracked new file is not seen and lands in the commit. Probes P1 and P3.
4. CONFIRMED. The row reads `restored` and the note holds the new sha. `init_db` on a copy of dry run 8's `final.db` keeps its 2 rows and the CHECK gains `restored`; an `UPDATE` to `restored` is accepted. `touch_mistaken` returns `[]` after the restore. `mergeable` on the fixture returns "no verdict" before and after, because the verdict gate comes before the stray gate; the stray query itself holds the `mistake` row before and nothing after. Probes P1, P1b, P4.
5. CONFIRMED by reading `loop.py` 266 to 292. The restore loop runs before the scheduler actions and before the role dispatch, so no wake for the same row reaches a seat in the tick before the restore. In a tick where every row returns a reason, the wake falls through to the dispatch as today, with no commit and the row still `mistake` (probe P2a). Two gaps: a partial restore falls through with the head moved and the second row lost (finding 2), and a quarantined Developer key hides the wake and the restore with it (finding 6).
6. CONFIRMED. `_removal_entry` returns the same JSON at 207a553d and at d7f88ca1 on the one removal, on the a585c4ea shape and on no removal. `test_f7_restore_wake.py` passes, 10 tests. `removed_statements`, `restore_stray`, `restore_wake` and `_place` are new at d7f88ca1. `_statement_spans` existed in `api.py` with another meaning (finding 7).
7. A smaller fixture tests the same rule: the fold function with the module head, about 60 lines per file, because the anchors sit one line from the statement and the a585c4ea change is inside the fold function. Probe P2c tests the rule on a 13 line file. The fixtures hold 0 CR bytes, 0 tabs and no non-ASCII byte. They copy icalendar's `string.py`, a third party source under its licence, with no licence line in the fixture.
8. CONFIRMED. After the restore on a585c4ea's shape the diff against the fork holds the escape branch and its two comments, and 0 rows stand at the new head, so the stray gate opens. The fix belongs in the restore: the structure's commit never passes `code_commit`, so only the restore can write the row (finding 4).
9. CONFIRMED green. `test_f173_structure_restore.py`: 4 passed in 3.96s. The related set `-k "stray or removal or touch or restore or park or commit"` with `-n 0` and no time limit: 713 passed, 12 skipped, 6501 deselected in 579s. Pass 1's cut at 89 percent hid 11 percent, all green here.
10. No reader misses `restored`, by reading each of the 12 readers the map lists. `_mistake_rows`, `touch_mistaken`, `touch_strayed` and the stray query of `mergeable` read `mistake` or `open` at the head, and the restored row sits on the old head. `batches_strays`, `batches_judge_touch` and the Principal's `_removal_words` read the head's rows, so a restored row is not shown. `_removal_strays` reads the last row of a grain with `status != 'open'`, and a `restored` status is neither `mistake` nor `foreseen`, so a later removal of the same statement opens a new row for the Architect. `_outside_prediction` and `_unnamed_def_strays` count the grain judged for the batch, as a `mistake` row did before. No `code.read` reads the table.

## (b) Findings

1. HIGH. `rota/core/restore.py` 56 to 62 and `rota/core/worktrees.py` 221. The dirty check runs `git status` with `--untracked-files=no`. `worktrees.commit` then runs `add -A`. A new file that a Developer wrote and did not commit lands in the structure's commit. CONFIRMED: probe P3 wrote `src/new_dev.py` untracked, the restore returned a sha, and `git show --stat HEAD` lists two files. Law 1 says the structure writes no seat's change. Fix: drop `--untracked-files=no` from the status call, so an untracked file is a reason too.

2. HIGH. `rota/core/restore.py` 97 to 110 and `rota/core/loop.py` 270. A partial restore moves `head_commit`. The row with a reason stays `mistake` at the old head. `touch_mistaken` then wakes nobody, and the stray query of `mergeable` finds no row at the new head. The mistake leaves the gate with no Developer and no judgement. CONFIRMED: probe P5 and P5c, two `mistake` rows, one restorable. After `restore_wake`: done 1, reasons 1, head moved, `touch_mistaken` `[]`, stray hold `[]`. Fix: place every lost statement first, and commit once only when no row has a reason, or write the unrestored row again as `mistake` at the new head.

3. LOW. `rota/core/restore.py` 97 to 110. Two restorable rows at one head: the first call moves the head, and the second call's `UPDATE` keys on the new head, so it marks nothing. The statement is back and the row says `mistake` on an old head. CONFIRMED: probe P5d, rows `restored` and `mistake` at one sha, file equals the fork. The report names this as open question 2. Fix: the same one commit for all rows as finding 2, with the old head passed in.

4. LOW. `rota/core/restore.py` 103 to 110, point 8. The restore commit writes no row at the new head. A grain that still differs from the fork, the escape branch of a585c4ea, carries no row and the stray hold ends. CONFIRMED: probe P8, the diff against the fork holds the escape branch and two comments, and the row count at the new head is 0. `_removal_strays` says the Architect's note covers the removals it names and no later change. The structure's commit never passes `code_commit`, so the fix belongs in the restore. Fix: after the commit, when the grain's text still differs from the fork, write an `open` row at the new head with the note "changed outside the restore".

5. LOW. `rota/core/loop.py` 266 to 276. A partial restore falls through to dispatch with no `conn.commit()`. The git commit stands at once. The head move waits for the commit at line 384 after the dispatch. A crash between the two leaves git HEAD one commit ahead of `batches.head_commit`. PLAUSIBLE: read, not run. Fix: `conn.commit()` right after `restore_wake` when `done` is not empty.

6. LOW. `rota/core/loop.py` 266 to 267. The restore runs only when the Developer's `tick:touch_mistaken` wake is in `ready`. `frontier` filters `ready` through `quarantine_stalled`. A quarantined key `developer|tick:touch_mistaken|<batch>` hides the wake, and the restore never runs on that batch. PLAUSIBLE: `scheduler.py` 1681 to 1684, read. Fix: read the `mistake` rows at each running head in `step`, not through the Developer's wake.

7. LOW. `rota/core/restore.py` 114 and `rota/roles/api.py` 18837. `_statement_spans` names two functions with two meanings and two signatures. CONFIRMED: `git grep` at d7f88ca1 finds the api.py one. Fix: rename the restore's function `_statement_ends`.

8. LOW. `tests/rota/fixtures/dry8_string_99619246.txt` and `dry8_string_a585c4ea.txt`, 584 lines. The context rule reads the fold function and one unique line each side. The a585c4ea replay needs the fold function only. About 60 lines per file test the same rule. CONFIRMED: probe P2c tests the rule on a 13 line file. Fix: cut each fixture to the fold function with the module head.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/33f037c1-f639-4fa5-8bd4-0cc91eeff019/scratchpad/f173r/`. They ran from the worktree root `C:/Users/roman/rota_f173r` at 207a553d.

- `probe_restore.py`, output `probe_restore.out` and `probe_restore2.out`. It builds the test module's fixture in a scratch repo and runs `restore_wake` on each head: P1 the one removal with a byte compare against `git show fork:path`, `git status --porcelain` before and after, the `sessions` count and the message. P2a a comment line between the anchors. P2b the before anchor repeated in `validate_token`. P2b2 the whole fold block repeated. P2c a 13 line fork with one statement in two functions, gone twice, for the grains `p.py`, `p.py::a` and `p.py::b`. P3 a tracked file dirty, then an untracked new file. P4 `init_db` on a copy of dry run 8's `final.db` with its WAL. P5 and P5c two `mistake` rows, one with changed context, with the stray query of `mergeable`. P5d two restorable rows. P8 the a585c4ea bytes as the head, with `git diff -U0 HEAD~2 HEAD`. P1b the stray query on the one row fixture.
- `probe_entry.py`, outputs `entry_new.json` and `entry_old.json`. It runs `_removal_entry` on the fixture at 207a553d and at d7f88ca1 (`D:/repos/rota`, where `api.py` equals d7f88ca1) and `cmp` compares the JSON.
- `pytest tests/rota/test_f173_structure_restore.py -q -n 0` and `pytest tests/rota/test_f7_restore_wake.py -q -n 0`, both with `ROTA_MODEL=qwen3:8b`.
- `pytest tests/rota -q -n 0 -k "stray or removal or touch or restore or park or commit"` with no time limit.
- `git grep` for each new definition name at d7f88ca1. `git show 207a553d` for the four edited source files. A byte count of the fixtures for CR, tab and non-ASCII bytes.


## (d) The counts and the time

- Points: 10 answered, 9 CONFIRMED by a probe or a run, 1 (point 7) by a byte count and a read.
- Findings: 8. High 2 (findings 1 and 2). Low 6. CONFIRMED 6, PLAUSIBLE 2 (findings 5 and 6).
- Tests: 4 new passed, `test_f7_restore_wake.py` 10 passed, the related set 713 passed and 12 skipped in 579s. The gate was not run.
- Probes: 2 scripts, 14 cases, 2 pytest files and 1 pytest set.
- Time: started about 2026-11-10 01:05, the set ran 01:30 to 01:40, the page written 01:45, by the clock.

## (e) What I did not read

- `C:/Users/roman/rota_p173`, as the brief says.
- The cassette case `L1-DV-put-back-a-removed-block` was not replayed by name. `test_f7_restore_wake.py` ran green, 10 tests.
- `batches_judge_touch` past its row writes, the cockpit pages, `quarantine_stalled`'s body, and `code.read`.
- Parts 1, 3 and 4 of the fix brief, which the commit does not build.
## (f) Usage

Input and output token counts are not shown to this session. The context at the end of the review is about 80k tokens, over the 50k cap of the brief by about 30k, most of it the test set's wait and the heredoc retries. No sub-agent.
