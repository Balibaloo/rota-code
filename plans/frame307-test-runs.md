# Frame 307's residue: what `test_runs` holds, night 159

A read on Opus, 2026-10-23. Row W7 of `plans/night159-read.md` section 2.
No code and no record changed. The database was opened `?mode=ro`.

## (a) The answer in five lines

1. `test_runs` holds the last harness run per batch and commit only, less the
   runs of each test whose body changed later. It holds 287 rows of the 987
   test executions that the log prints in 27 `do:harness` lines.
2. Two deletes make the gap. `harness.py:154` replaces each earlier run at the
   same commit (693 rows, 19 whole runs). `db.py:617` deletes every run of a
   test on a re-encode of its body (7 rows of the 8 surviving runs).
3. The 4 rows missing at c29d89dd77 are `tst_cr1_default_off`,
   `tst_cr4_plain_function_default`, `tst_cr6_simple_default_return` and
   `tst_confirm_eof_default`. The walk 3 Tester re-encoded all four, and
   `db.py:617` deleted their walk 2 runs.
4. The three walk 2 reds now live only in the `tests.load` prompts of s185
   and s189, which read `test_runs` while the rows still existed.
5. One ratio of section 1 rests on `test_runs`: frame 140's "no project test
   went red in 287 runs". The recount is 0 red in 279 project-test rows, of
   942 project-test runs. The fix is a writer: an append-only journal beside
   `record_test_run`, 1 cycle.

## (b) The writers

One function inserts into `test_runs`, and one caller calls it (observed:
`grep "INTO test_runs\|record_test_run" rota`, the tests excluded).

- `rota/core/lifecycle.py:401`, `record_test_run`, the only `INSERT OR
  REPLACE INTO test_runs` (observed: line 412).
- `rota/core/harness.py:128`, in `harness.run`, the no-worktree case: one
  `error` row per test (observed).
- `rota/core/harness.py:157`, in `harness.run`, the normal case: one row per
  test of the batch (observed):

  ```
  conn.execute("DELETE FROM test_runs WHERE batch_id = ? AND commit_sha = ?",
               (batch_id, head))
  for test_id, result in results:
      lifecycle.record_test_run(conn, new_id("tr", conn), batch_id, test_id,
  ```

- `harness.run` has one caller, the `harness` action of the loop,
  `rota/core/loop.py:512`. That action prints the log line
  "`<bid>: N test(s), K not passing`" (observed: `loop.py` 512 to 514).

So the table records one run kind only: the mechanical harness run before the
Critic (observed: the schema comment "the mechanical gate before Critic").
These runs write no row:

- The sandbox run at encode. `_encode_run` at `rota/roles/api.py:14991` calls
  `harness._run_one` and returns the verdict to the encode door. It writes
  nothing (observed: `api.py` 15051).
- The base run. `harness.record_base_run` at `harness.py:300` writes a JSON
  record to `config`, not to `test_runs` (observed: `harness.py` 349).
- The Developer and the Critic. Neither role has a tool that runs a test. No
  `execute.run` of pytest exists outside `harness.py` (observed: grep of
  `rota/roles/api.py` and `rota/core`).
- The merge gate. `lifecycle.mergeable` reads `test_runs` at the head commit
  and runs nothing (observed: `lifecycle.py` 765 to 770).

Two deletes remove rows that the writer wrote:

- `harness.py:154`: a new run at the same batch and commit deletes the run
  before it. The comment gives the reason: the `review` gate reads "no
  non-pass run at this commit" (observed: `harness.py` 150 to 155).
- `db.py:617`: a write to `tests` that carries `body` deletes every run of
  that test, at every commit (observed). The comment gives the reason: the
  hold guard and the gates read the run of the old body (observed: `db.py`
  613 to 617).

`rota/core/identity.py:107` declares `test_runs` a "journal, one execution,
one row". Both deletes contradict that declaration (reasoned: a journal keeps
its rows).

## (c) 35 against 39

The table holds these run sets for night 159 (observed: `test_runs` grouped by
batch and commit):

| batch | commit | attempt | rows | not pass | log line of that attempt | log says |
|---|---|---|---|---|---|---|
| bg_1 | d58b48d4f2 | 3 | 35 | 0 | 38 | 35, 0 |
| bg_2 | 1a674dd204 | 1 | 35 | 0 | 62 | 35, 0 |
| bg_2 | 0f6e3e013b | 3 | 35 | 0 | 66 | 36, 1 |
| bg_2 | 2f3c2dd7ca | 4 | 35 | 0 | 67 | 36, 0 |
| bg_2 | c29d89dd77 | 11 | 35 | 0 | 85 | 39, 3 |
| bg_2 | 89da5b89fc | 14 | 41 | 1 | 236 | 41, 1 |
| bg_4 | 6465d71fc0 | 6 | 35 | 0 | 185 | 36, 1 |
| bg_4 | b5f0be71c3 | 10 | 36 | 1 | 206 | 36, 1 |

The attempt number is the Nth `do:harness` line of the batch in the log
(reasoned: `next_attempt` is MAX(attempt)+1 per batch, and no delete removed
a whole maximal run, so the numbers did not repeat). Walk 2 has 11 bg_2 lines,
log lines 62 to 85, so attempt 11 is line 85 (observed: the log).

The walk 2 commit is c29d89dd77, the park commit (observed: night read
section 2, "attempt 11 against `loop_cap` 10 at c29d89dd"). Lines 79, 84 and
85 say "39 test(s), 3 not passing". Lines 79 and 84 were attempts 9 and 10 at
the same commit, and `harness.py:154` replaced them (reasoned: only attempt
11 survives at c29d89dd).

Attempt 11 wrote 39 rows: the 35 non-criterion tests and 4 criterion tests.
The s185 and s189 `tests.load` lists show the same 39 ids (observed: 4
criterion ids and 35 `inh_` or inherited ids). The table holds the 35 and none
of the 4. The 4 missing rows:

- `tst_confirm_eof_default`, pass.
- `tst_cr1_default_off`, fail.
- `tst_cr4_plain_function_default`, fail.
- `tst_cr6_simple_default_return`, fail.

`db.py:617` removed them. The walk 3 Tester re-encoded all four ids, in s253
and s278 (observed: `tool_calls`, `fn = 'tests.encode'`). Their only rows are
now at 89da5b89fc, attempt 14 (observed: `test_runs` by `test_id`). A row at
another commit can go only by `db.py:617`, because `harness.py:154` deletes
at its own commit only (reasoned: these are the only two deletes in `rota/`).

The same writer explains the other gaps of the table. At 0f6e3e013b and
2f3c2dd7ca, `tst_confirm_eof_default` is missing (36 against 35). At
6465d71fc0, the red `tst_ver_opt_no_flag` is missing, re-encoded from s303 to
s413 (observed: `tool_calls`). So extract A's "no criterion-test run of
walk 2" is exact: every bg_2 criterion test was re-encoded in walk 3
(reasoned).

The count of all deletes: the log prints 987 executions in 27 runs (observed:
the sum of the `do:harness` lines). The 8 surviving runs wrote 294 rows, and
the table holds 287. So `db.py:617` removed 7 rows of surviving runs, and
`harness.py:154` removed 693 rows of 19 runs (reasoned: the arithmetic).

## (d) The three reds

| test | `tests` | `test_runs` | `tests.load` in `turns` |
|---|---|---|---|
| `tst_cr1_default_off` | the current body, version 4 | 1 row, `tr325`, 89da5b89fc, `fail`, attempt 14 (walk 3) | s185 and s189 turn 1, `last_result` `fail` |
| `tst_cr4_plain_function_default` | the current body, version 4 | 1 row, `tr328`, 89da5b89fc, `pass`, attempt 14 | s185 and s189 turn 1, `fail` |
| `tst_cr6_simple_default_return` | the current body, version 3 | 1 row, `tr329`, 89da5b89fc, `pass`, attempt 14 | s185 and s189 turn 1, `fail` |

The walk 2 reds live only in the `tests.load` blocks of the `turns.user`
text. `tests.load` reads `test_runs` live, at `rota/roles/api.py:9377`, so
the red rows existed when s185 and s189 started (reasoned). The `tests` table
holds no result. The rows in `test_runs` are walk 3 runs of the new bodies.

One quoted row of each, from s185 turn 1, `[tests.load]` (observed):

- `tst_cr1_default_off` fail: `E           AttributeError: 'FakeStdin' object has no attribute 'readline'`
  then `E           assert 'UsageError' in "<class 'AttributeError'>"`.
- `tst_cr4_plain_function_default` fail: `E       TypeError: confirm() missing 1 required positional argument: 'text'`.
- `tst_cr6_simple_default_return` fail: `E       TypeError: confirm() missing 1 required positional argument: 'text'`.

In s189 turn 1, `tst_cr4_plain_function_default` fails on the `readline`
`AttributeError` instead (observed). So the body changed between s185 and
s189, which agrees with the night read's "no `text` in s185's copy, FakeStdin
in s189's".

## (e) The ratios

Section 1 of the night read has these counts on tests and runs:

- **Frame 304, "1 batch of 4 deferred with the code right".** The count rests
  on the diffs and on `tests.load` in s185 and s189, not on `test_runs`
  (observed: night read lines 76 to 89). The gap does not change it. The
  commit list "1a674dd204, 0f6e3e013b, c29d89dd77 and 89da5b89fc" came from
  the commits that `test_runs` holds. The table also holds 2f3c2dd7ca, and
  the list omits it. That is not a ratio.
- **Frame 143, "2 of 8 stored tests".** The count rests on `tests`, which
  holds 8 criterion tests (observed). The gap does not change it.
- **Frame 140, "no project test went red in 287 runs".** The count rests on
  `test_runs`: 287 is the row count of the table, criterion rows included
  (observed). The gap changes it. The recount:
  - Project-test rows in the table: 279, all `pass` (observed: 287 less 8
    criterion rows).
  - Project-test runs in the log: 942. bg_1 ran 34 for 3 runs, bg_2 35 for
    14 runs, and bg_4 35 for 10 runs (reasoned: the log counts less the
    criterion tests of each batch).
  - So the table shows 279 of 942, and 663 project-test results are gone.
    At every log line, "K not passing" is at most the count of criterion
    tests in that run (observed: the log and `tests`). So the log allows 0
    project reds, and does not prove 0 (reasoned).

The corrected sentence: "no project test went red in 279 recorded runs, of
942. The log counts allow 0 in the rest."

## (f) The fix

The gap is the writer's, so the fix is a writer: `record_test_run` also
inserts each run into an append-only journal that no gate reads and no
delete touches, and the night report counts from that journal. Price: 1
cycle, the schema, the one insert, the report section and one test.

The reason against a report line alone: a line can only say which runs the
table holds. Frame 140's ratio needs the per-test result of the 663 runs that
left no row, and no record holds them (reasoned). The reason against removing
the two deletes: the `review` gate, the hold guard and the Developer's wake
read the table as "the live run per test", and the deletes keep that true
(observed: the comments at `harness.py:150` and `db.py:613`). A second table
keeps the journal that `identity.py:107` declares without a change to those
readers (reasoned).

## (g) Usage

About 45k tokens on Opus. Scratch: `w7/load.py` in the session scratchpad.
