# Frame 309, review 2: pass 1b at 431fa122

Verdict: accept for the branch, with two low findings. The reviewer edited no tracked file except this page.

## (a) The claim

The pass claims two changes on parent 25c63b8e.

- `cmd_run` calls `init_db(path).close()` after the `schema_stale` check. So a database onboarded before the journal gets `test_run_journal`.
- `_id_tables` in `rota/roles/api.py` skips `test_run_journal`. So `ref_resolves` and `ledger_log` never read the journal.

Point 1, the `init_db` call: holds. The call runs before `drive` on every path through `cmd_run`. Before the call, only `require`, an environment write and the `schema_stale` read run. No harness runs there.

Point 1, a database that already has the table: holds. `CREATE TABLE IF NOT EXISTS` adds nothing. Each `ALTER` is behind `_has_column`. The mark write is `INSERT OR IGNORE`. A current database leaves `init_db` with no change. A database that lacks another table or column of the current schema also gets that table or column now. That is correct.

Point 1, the readers of the journal in `rota/`: holds with one exception. The readers by name are `record_test_run` (writer, `rota/core/lifecycle.py:422`) and the night report (`rota/tools/nightreport.py:703-731`). `rota/core/identity.py:108` is a registry entry, not a read. Three generic readers walk every table and so read the journal. These are `rota/tools/audit.py:47` `_ids`, `rota/tools/invariants.py:289` `i10`, and `rota/cockpit/server.py:274`. Only `audit._ids` reads the journal ids. See finding 1.

Point 2: holds. `test_frame309_test_run_journal.py` and `test_identity.py` pass with `-n 0`, 21 passed.

## (b) Findings

1. `rota/tools/audit.py:47-54`, low, CONFIRMED by a code read. `_ids` puts every `id` of every table with an `id` column in the known set. The set includes the journal ids. A ref to a test run that `test_runs` deleted then reads as resolved in `audit`. The audit misses that dangling ref. The `api.py` change does not cover this reader. Fix: skip `test_run_journal` in `_ids`, or share one `_NOT_REFFABLE` set from `rota/core/identity.py` between `api.py` and `audit.py`.
2. Outside the points. `rota/tools/onboard_run.py:226`, low, CONFIRMED by a code read, not by a run. `main` calls `drive` on an existing database with no `--root`. `drive` opens the database with `connect` alone (`onboard_run.py:44`). So an old database through this door still raises on the first journal write. The new comment at `rota/core/db.py:170-172` names this rule, and this door breaks it. Fix: call `init_db(db_path).close()` at the top of `drive`, and drop the call in `cmd_run`.

`i10` in `invariants.py` reads the journal integer columns for type only. That read is correct and needs no change. The cockpit check at `server.py:274` reads table names only.

## (c) Probes

1. `git diff 25c63b8e 431fa122` in `C:/Users/roman/rota_r309`. Four files, each hunk read.
2. `python -m rota.tools.map` for `fn init_db`, `table test_run_journal`, `fn cmd_run`, `fn drive`, `fn record_test_run`. The map gives one writer and no reader of the journal by name. `drive` has two callers: `cli.py:539` and `onboard_run.py:227`.
3. A grep for `sqlite_master` and `journal` in `rota/`. This found the three generic readers and the night report.
4. `ROTA_MODEL=qwen3:8b python -m pytest tests/rota/test_frame309_test_run_journal.py tests/rota/test_identity.py -q -n 0`. Result: 21 passed in 2.17s.

## (d) Usage

Input tokens: about 32k. Output tokens: about 3k. Total: about 35k. The total is an estimate and is over the 15k cap.
