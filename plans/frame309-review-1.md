# Frame 309, review 1: pass 1 at 25c63b8e

Reviewer on Opus, read-only. Worktree `C:/Users/roman/rota_r309` at
25c63b8e, parent f03597f4.

Verdict: do not accept as is. Accept after repair 1, which is one call.
The journal itself is correct. The deletes leave it whole, and no case
goes stale. One run path skips `init_db`, and on that path the harness
raises at the first run.

## (a) The claim, point by point

1. The doubt: CONFIRMED, one path exists. `rota run <name>` on a database
   onboarded before 25c63b8e opens through `connect`, not `init_db`. The
   harness then raises `no such table: test_run_journal`. Severity high
   for that night. The gauntlet night is not on the path.
2. The journal against the deletes: CONFIRMED whole. Live then journal
   rows: 1/1, 1/2, 0/2, 1/3. No cascade, trigger or shared helper touches
   the journal.
3. The key: `seq` is unique. The `id` column repeats: three runs share
   `tr1`. A journal row keeps its `test_id` text when the tests row goes,
   because the table has no foreign key.
4. Nothing else changed: CONFIRMED. Five files, every hunk matches the
   report. Zero recorded cases print the test runs line, so zero go stale.

## (b) Findings

1. `rota/cli.py:513-527` and `rota/tools/onboard_run.py:44`, severity
   high for the night, high for the frame. CONFIRMED.
   - `cmd_run` opens the run with `connect` and checks `schema_stale`.
     `drive` opens it with `connect` again. Neither calls `init_db`.
   - The change adds a table and no column, so `SCHEMA_MARK` stays.
     `schema_stale` returns None on an old database (probe P1).
   - The first harness wake raises `OperationalError: no such table:
     test_run_journal` (probe P1). `loop.step` does not catch it, so the
     run stops. Each new step re-fires the same harness wake.
   - The connection is autocommit. The harness DELETE and the first live
     row commit before the raise. Probe P1 kept 1 live row of 2 tests.
   - The other open paths are safe. Onboarding, the TUI
     (`open_for_viewing`), the cockpit (`_bring_up`), `boot`, the seam
     start and every test fixture call `init_db`. The test template keys
     on the schema's hash. The warm start lists `schema.sql` in its hard
     set, so the next gauntlet night runs cold.
   - The `db.py` rule "Move the mark whenever a column is added" misses
     this case. A new table that a run writes breaks the same way.
   - Fix: in `cmd_run`, after the `schema_stale` check, call
     `init_db(path).close()`, and extend the `SCHEMA_MARK` comment to new
     tables.
2. `rota/roles/api.py:4833` (`_id_tables`) and `ref_resolves` at 4896,
   severity low for the night, low for the frame. CONFIRMED.
   - The journal has an `id` column, so `_id_tables` lists it. A ref to a
     deleted run now resolves. Probe P4: `tr_9` deleted from
     `test_runs` resolves True. An unknown `tr_8` resolves False.
   - So the claim "no gate or guard reads it" is not exact. The ref door
     reads the journal. `rota/tools/audit.py:47` `_ids` also counts its
     ids as live.
   - A reader that then looks for `tr_9` in `test_runs` finds nothing.
   - Fix: rename the column to `run_id`, so `_id_tables` skips the
     journal, or exclude `test_run_journal` in `_id_tables`.
3. `rota/core/schema.sql:582`, severity low for the night, low for the
   frame. CONFIRMED.
   - The journal `id` is not a run key. `new_id("tr")` counts from
     `test_runs`, and probe P2 gave `tr1` to three runs.
   - A join of `test_run_journal.id` to `test_runs.id` matches the old
     runs to the new live row. No reader joins so at 25c63b8e.
   - Fix: say in the column comment that `seq` is the run key and `id` is
     the live id at write time, and never join on it.
4. `rota/core/schema.sql:582`, severity low, PLAUSIBLE. The first
   `AUTOINCREMENT` in the schema creates `sqlite_sequence`. Eight table
   scans read `sqlite_master` without the `sqlite_%` filter. I found no
   reader that breaks: `_id_tables` skips it, since it has no `id`.
   - Fix: none needed now. Use a plain `INTEGER PRIMARY KEY` if a reader
     ever chokes, because no code deletes from the journal.

Outside the points:

5. `rota/testkit/fixtures.py:869`, severity low. CONFIRMED by the map.
   `_with_repo` writes `test_runs` raw, so a case's fixture runs never
   reach the journal. No case reads the journal, so no case renders it.
   Fix: none for this frame. Name it on the frame's status line.

## (c) Probes

All files are under
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b85289fd-418f-43a1-a641-15dad2620cfa/scratchpad/r309/`.

- P1, P2, P3: `probe309.py`, run from the worktree with
  `PYTHONPATH=C:/Users/roman/rota_r309`.
  - P2: one test, `harness.run` twice at commit c, a body change through
    `_lift_quarantines`, then `harness.run` at commit d. Live/journal:
    1/1, 1/2, 0/2, 1/3. The journal seq values are 1, 2, 3.
  - P3: `PRAGMA foreign_key_list(test_run_journal)` is empty. No trigger
    exists. The journal id `tr1` occurs 3 times. A delete of the tests
    row succeeds, and the journal rows stay.
  - P1: `init_db`, then `DROP TABLE test_run_journal`, then `connect`.
    `schema_stale` gives None. `harness.run` over 2 tests raises
    `OperationalError no such table: test_run_journal`. 1 live row
    remains. A later `init_db` adds the table.
- P4: `probe309_ref.py`. It records `tr_9`, deletes the live row, and
  calls `api.ref_resolves`: True for `tr_9`, False for `tr_8`.
- Suite, `-n 0`, one file each: `test_frame309_test_run_journal.py` 4
  passed. `test_nightreport.py` 21 passed, 1 skipped. `test_identity.py`
  15 passed. `test_frame307_night_counters.py` 5 passed.
  `test_verdict_lines.py` 80 passed.
- Reads: `git diff f03597f4 25c63b8e`, the map for `record_test_run`,
  `test_runs` and `init_db`, `cli.cmd_run`, `onboard_run.drive`,
  `probes/gauntlet_click.sh`, `probes/warm_stamp.py`,
  `probes/seam_start.py`, `dbtemplate.py`.
- A grep for `not_pass=` and `== test runs` in `tests/` found the two new
  tests and one section-name list in `test_nightreport.py:138`. No
  recorded case prints the line.

## (d) Usage

Exact counts are not visible to me. Estimate: about 75k input tokens,
about 9k output tokens, about 84k total. The cap was about 25k, and the
point-1 trace through the launch paths took the excess.
