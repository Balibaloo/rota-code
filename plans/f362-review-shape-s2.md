# Review: frame 362, shape pass S2, `49b7b7a9` (2026-11-04)

Verdict: stand. No finding is high. Fix the one medium finding before a dry run merges a batch. I probed a `git archive` copy of `49b7b7a9` under the scratchpad, and changed nothing in `C:/Users/roman/rota_p362h`. The S2, harvest and S1 tests pass on the copy, 51 of 51.

## (a) Verdicts by point

1. CONFIRMED. All four forms have code, and three fire on the pins. On tips, `README.md` line 3 (`python main.py`) and the `main.py` guard each bind `main.py`. On icalendar, the script `icalendar = "icalendar.cli:main"` binds `cli.py` and `pyproject.toml`. The guards in `cli.py` and `timezone/equivalent_timezone_ids.py` bind their own files. Click gives no row, and its one guard (`decorators.py`) is dropped. The guard rule drops `cal/lazy.py` and `fuzzing/ical_fuzzer.py`. By my own read, all 5 rows are true. The timezone guard is a maintainer run that rebuilds the data. That run starts in the file, so the fact is true, but no user starts that run. No `metadata` script row is left.
2. CONFIRMED. The three forms fire on the pins. `testpaths` binds the test files under its paths: 4 on tips, 50 on click and 171 on icalendar, including `conftest.py` and `__init__.py`. `change_log` on click binds `CHANGES.md` at `## Version 8.5.0`, the heading above "Unreleased". `news_fragment` on icalendar binds 71 fragments under `news/` and `CHANGES.rst` (finding 3). I read all 5 rows as true.
3. CONFIRMED. In a git fixture, a second commit moved every row to the new commit and added the new `testpaths` row and its binding. A forced fault in `harvest.record` gave one warning, and the refresh returned with the index built. The connection held no open transaction afterwards. On icalendar a harvest at a new commit takes 0.97 to 1.01 s, and 0.00 s at a commit it has read. The full `refresh(main=True)` on the archive tree took 7.7 to 27 s with no stable difference, because `repin` dominates.
4. CONFIRMED. The map names one writer of `commitment_candidates` and two writes of `candidate_bindings`, all in `harvest._write`. A database made by the S1 `init_db` refuses `entry_point`. The S2 `init_db` widens both CHECKs, keeps the rows, and keeps the two autoindexes. `foreign_key_check` is empty, `integrity_check` is ok, and `foreign_keys` is back on. A second `init_db` changes nothing.
5. CONFIRMED. The `db.py` change moves the rebuild of `_widen_to_dropped` into `_widen_check` with a mark argument, and the `'dropped'` path is the same as before. The `cli.py` change prints each warning. The lifecycle needs the warnings, because `_reindex_main` is the only `main=True` caller in a live run, and it drops them (finding 1). The runner calls `refresh(main=False)`, which runs no harvest, so it has no warning to see.

## (b) Findings

1. `rota/core/lifecycle.py` lines 48 to 56, with `rota/onboarding/indexer.py` lines 693 to 700. Severity medium. CONFIRMED. `_reindex_main` ignores `RefreshReport.warnings`. Then `_refresh_worked` deletes the `index:<batch>` note, an older note too. After a harvest fault on a merge, the config held no note, and no record says that the candidates describe an older commit. Fix: in `_reindex_main`, write each warning under a `harvest:<batch>` config key or to the stress list, and clear the key when a harvest works.
2. `rota/onboarding/harvest.py`, `entry_guard`. Severity low. CONFIRMED by probe 4. The rule keeps `sys.exit(main())`. It drops a guard that calls a top-level class (`App().run()`), a guard that calls an imported `main`, and the reversed test `"__main__" == __name__`. A thin launcher module, `from pkg.cli import main` and then `main()`, is a common program start. Fix: count top-level classes and names imported from project modules as the own functions of the file.
3. `rota/onboarding/harvest.py`, `_contribution_files`. Severity low. CONFIRMED on icalendar. The `news_fragment` row binds the 71 old fragments and `CHANGES.rst`. A change adds a new fragment, so the old fragments are files no change touches. The `CHANGES.rst` file says that nobody adds entries to it. The row text names `news/`, so a touch of `CHANGES.rst` shows the rule, and that part is useful. Fix: bind `CHANGES.rst` and the `news/` path grain only, and leave out the old fragments.
4. `rota/onboarding/indexer.py`, the `refresh(main=True)` branch, with `harvest.record`. Severity low. CONFIRMED. A tree with no git gives the commit "", so the skip of `record` never fires, and each refresh harvests again, about 1 s on icalendar. Fix: accept and record this, because a live main checkout has git, or skip when a "" harvest of the same tree exists.
5. Outside the points. `plans/design-onboarding-shape-2026-11-04.md` line 276. No finding. The last Revision line records the rename to `contribution`, the tips count and the guard rule. Sections 3.4, 6.1 and 6.2 still say `intake` in 14 places, and the Revision line explains the old word.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/535a30c6-b4f1-4ae7-85bc-11d741145722/scratchpad/r362s1/s2/`. Each puts the `tree/` copy first on `sys.path`.

1. `tree/`: a `git archive` of `49b7b7a9` with `rota/`, the S2, S1 and harvest tests, and the test support files. pytest on the three tests gives 51 passed.
2. `pa_forms.py`: points 1 and 2, the rows, forms, bindings and guard decisions on the three pins under `r362s1/pins/`.
3. `pb_old.py` with `old.db`: point 4, a database made by the S1 copy `r362s1/after/` and then opened by the S2 `init_db`.
4. `pc_refresh.py` with `wc/`: point 3, a git fixture of two commits, a forced harvest fault through `indexer.refresh` and `lifecycle._reindex_main`, and the times on icalendar.
5. An inline `python -c` probe: finding 2, `entry_guard` on four guard forms.

## (d) Usage

Input tokens: about 45k for this review, estimated, because the harness shows no counter. Output tokens: about 9k, estimated. Total: about 54k, above the cap of about 40k. No sub-agent started.
