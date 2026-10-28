# F4 review, pass 1: commit b2003ad9 on f4root

Worktree C:/Users/roman/rota_f4, parent ae9b99c6. Read-only review. No tracked file changed.

Result: the view is correct, and the order rule is sound. One high finding: `init_db` drops the view and makes it again, and a live reader fails in the gap. Four findings are low.

## (a) Verdicts

1. PASS. `rowid` is stable. No `WITHOUT ROWID`, no `VACUUM` in rota, and `tr` ids never trigger the `REPLACE`. Among live rows, `rowid` follows insert order.
2. PARTIAL. 4 of the 7 reads want no newest run. `red_before`, `_stored_runs` and `_runs_at` want a newest run with a scope (finding 4).
3. PASS. Red then green gives "passed on its newest run". Green then red gives None, and the caller says "restore what your change broke".
4. PASS with a gap. `connect`, `connect_readonly` and `invariants.open_readonly` make a temp view, and the file gets nothing. A plain `sqlite3.connect` opener gets "no such table" (finding 5).
5. PARTIAL. A new reader in a new function goes red. A second read in one of the 7 allowed functions stays green (finding 3).
6. PASS by code. Every door path that names a red reads the view. The night count of 1 to 0 is PLAUSIBLE only, because s201's fault row is seat text.
7. PASS. No recorded case is stale by structure. Every seeded test has one run, and its batch is the test's batch.
8. The 4-line hunk in rota/core/harness.py belongs to F4. It is the comment on the `same_head` read of `test_runs`. F5's `error_at` is not in the commit: grep count 0. No finding, and the hunk stays.

## (b) Findings

1. rota/core/schema.sql:603, with rota/core/db.py:296. Severity high. CONFIRMED. `DROP VIEW IF EXISTS latest_runs` runs in `executescript` with no transaction. A second connection on the same file then reads "no such table: latest_runs" until the `CREATE` commits. Probe p4_race_initdb.py: 11 `init_db` calls during a reader loop gave 18,589 failed reads of 601,060. The control without the `DROP` line gave 0 errors in 154 schema applies. `init_db` runs on a live night file from the cockpit (`open_for_viewing`, tui.py:343 and 902, server.py `_bring_up`), from `faults.py` and from `talk.py`. Every tick predicate (`tests_failing`, `harness`, `review`, `exhausted`) reads the view. The `provenance` view at schema.sql:122 has the same pattern, but no tick reads it. Fix: put the `DROP` and the `CREATE` of the view in one `BEGIN` and `COMMIT` inside schema.sql, or drop the view only when its body differs.

2. rota/core/sandbox.py:2230. Severity low. CONFIRMED by probe, PLAUSIBLE in a night. The green check of `project_tests_fact` has no commit filter. Probe shape D: the newest pass is at commit c1, the head is abc, and no run at abc exists. The door says "your change broke nothing there" about a commit that no harness ran. A Developer that commits and then challenges in one session meets this text. Fix: add `AND commit_sha = <the batch head>` to the green query, and fall through to the old text when no run at the head exists.

3. tests/rota/test_f4_latest_runs.py:131-161. Severity low. CONFIRMED. The pin compares a set of (file, function) pairs. A second read inside an allowed function passes. Probe pinroot: a second `test_runs` read with `ORDER BY attempt DESC` inside `red_before` gave the same single pair. Concatenated names, `f"FROM {T}"` and a quoted `"test_runs"` also escape the scan. Fix: pin the count of read sites per allowed function, and match an optional quote before the table name.

4. rota/core/db.py:960, rota/core/sandbox.py:5609, rota/roles/api.py:20834. Severity low. CONFIRMED by reading. These 3 of the 7 want a newest run, not history or all runs. `red_before` wants the newest run that ran code. `_stored_runs` and `_runs_at` want the newest run per test at one commit. `_stored_runs` and `_runs_at` keep the `attempt, rowid` order, so a second order rule survives. No disagreement shows today, because harness.py:181 deletes a commit's runs before it records that commit again. `_stored_runs` must stay independent of the door's reader (frame 149), so its own query is right. Fix: order `_stored_runs` and `_runs_at` by `rowid` only, and name `red_before` in the pin comment as a scoped newest-run reader.

5. rota/core/db.py:164, the night tools. Severity low. CONFIRMED. A pre-F4 file opened with a plain `sqlite3.connect` has no view. Probe p3_fact.py: `predicates.tests_failing` on that connection raised "no such table: latest_runs". `nightreport` opens with a plain `sqlite3.connect` but reads no view, so it is safe. `nightcount` and `audit` use `connect_readonly`, so they are safe. An ad-hoc read script that calls rota functions through a plain opener fails on an old night. Fix: tell read scripts to open through `connect_readonly`, in operating-facts.md.

Outside the points: none beyond finding 1, which point 4 found.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b3bc8a66-bd69-4749-a050-07bdd1893c24/scratchpad/f4rev. Each one ran with PYTHONPATH set to the worktree.

- p1_rowid.py: a scratch table with a TEXT key. It ran two attempts, a re-run at one commit with the harness delete, a delete and `VACUUM`, and a delete of the top row followed by an insert. The view gave the insert-newest row each time. SQLite 3.50.4.
- p3_fact.py: four shapes on `project_tests_fact` with a base run of pass. A red then green gave the green text. B green then red gave None. C attempt 3 then attempt 1 gave the green text. D gave the green text at an old commit. The probe also opened a pre-F4 file through the three openers, a plain opener, `connect` and `init_db`.
- p4_race.py, p4_race_nodrop.py, p4_race_initdb.py: one reader thread reads the view while a writer applies the schema. With the DROP: 275,808 errors in 38 applies. Without the DROP: 0 errors in 154. With real `init_db`: 18,589 errors in 11 calls.
- pin_probe.py with pinroot/: ran the pin's `_sites` on a scratch tree with 7 read forms.
- p7_cases.py and p7b.py: walked every `test_runs` seed in tests/rota/cases. 33 rows in 30 fixtures. No test has 2 runs, and no run batch differs from its test's batch. A grep for the changed door texts found 0 cases.
- pytest tests/rota/test_f4_latest_runs.py: 8 passed.
- git show of the harness hunk, and a grep for `error_at` in harness.py at b2003ad9: count 0.

## (d) Usage

Input about 100k tokens, output about 14k tokens, total about 114k. The context reached about 98k, past the 80k cap.
