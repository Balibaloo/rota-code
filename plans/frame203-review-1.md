# Frame 203, the gate's levers, pass 1: the diff review of d3bc6fd4

Reviewer on Opus, read-only, 2026-10-11 16:16. Meta workflow. Worktree `C:/Users/roman/rota_rv203`, detached at d3bc6fd4. No gate ran. Every pytest run used `ROTA_MODEL=qwen3:8b` and `-n 0`.

Verdict: the pass stands. One low defect is confirmed in `_relink`. One coverage gap is open for the acceptance gate.

## (a) Verdict on each point

1. Holds. At conftest import, `install()` rebinds `rota.core.db` alone. Later modules read the wrapper. A monkeypatch of `rota.core.db.init_db` acts as before. The copy equals a fresh database in every compared item.
2. Holds. The header write adds one frame of page 1 to the `-wal` file. A reader before the write sees the same state. The key moves with `schema.sql` and with the `init_db` source. xdist workers cannot race, because each worker builds its own template under `mkdtemp`.
3. Holds on a path with a space and on a prefix path. The relink fails when the temp path differs in case from the path git writes. The copy then shares the template's repository, and a commit leaks into the template (finding 1).
4. Holds. All six fixtures give the same HEAD, commits and clean status. No key omits a builder argument.
5. 163 tests skip for the missing register: 161 "no cassettes recorded" and 2 "the register is not on this machine". The commit does not change which tests run. The 163 tests now open their databases through the wrapper, and no gate has run them that way (finding 2).

## (b) Findings

1. `rota/testkit/gitfixture.py:198-212` (`_relink`), severity low. CONFIRMED. With `TEMP=c:/users/roman/appdata/...`, `mkdtemp` gives a base in lowercase, and git writes `C:/Users/roman/AppData/...` in `.git` and `gitdir`. `bytes.replace` matches neither form. The copy's `batch/.git` still names the template. A commit in the copy moved the template's `batch` HEAD, and the next copy returned a head that differs from the built one. The default TEMP and the gate's TEMP have the true case, so no run today meets the defect. Fix: build the base from `Path(tempfile.mkdtemp(...)).resolve()`, and raise in `_relink` when a link does not name `new` after the replace.
2. `rota/testkit/fixtures.py:1229` and `:1320` (`run_case`, `run_chain`), severity low. PLAUSIBLE. The 161 cassette cases call `init_db` through the wrapper, and the report's gate skipped every one of them. The probe shows the same schema, rows and pragmas. The `-wal` file is 4152 bytes against 1030032 bytes fresh. The case repository sits beside the database, not around it, so the onboarding does not index the `-wal`. Fix: gate a checkout that holds `tests/rota/cassettes.db` before the frame closes, as the report's open question 1 says.
3. Outside the points. `rota/testkit/gitfixture.py:149-172` (`template`), severity low. PLAUSIBLE. The `atexit` clean-up does not run in every xdist worker. `C:/Users/roman/rota_gate/tmp` holds 982 `rota_sample_template_*` directories, 12 of them from 2026-10-11 16h, from before this commit. Each leaked worker now leaves the sample, the database and the git templates, not the sample alone. A gate ran during the review, so the count after a gate with this commit is not measured. Fix: let the gate remove `rota_template_*` under its temp root after the run.

## Detail for point 1

- Rebound at conftest import: `rota.core.db`. No loaded `rota.*` module kept the real `init_db`.
- Imported after conftest, each module binds the wrapper: `rota.core.boot`, `rota.testkit.fixtures`, `rota.testkit.scenes`, `rota.cockpit.tui`, `rota.cockpit.server`, `rota.tools.onboard_run`, `rota.tools.talk`. `rota.cli` and `rota.cockpit.progress` import inside the function, so they read the wrapper at the call.
- A monkeypatch of `rota.core.db.init_db` reaches the callers that read the module global: `open_for_viewing`, the local imports, and the seam restore. Callers that bound the name at import do not see the patch, as before the commit. The probe called `open_for_viewing` and hit the patch. `test_seam_start.py` passes, 17 tests.
- Fresh against copy: the same `sqlite_master` text, `journal_mode` wal, `user_version`, `foreign_keys` 1, `page_size`, `auto_vacuum`, `application_id`, `encoding`, `freelist_count`, `busy_timeout`, `synchronous`, `integrity_check`, and every row of every table. One table has rows: `config`, with `('schema', 'ledger-kind')` in both.
- The key leaves out `connect`, `schema_stale`, `_has_column` and `SCHEMA_MARK`. No test patches them, and the template lives for one process, so the omission has no effect.

## Detail for point 4

`test_templates.py` 6, `test_verdict_lines.py` 69, `test_findings_doors.py` 28 and `test_seam_start.py` 17: 120 passed in 74.07s. Keys: `s279` has no argument. `("repo_of", rel, before, after)` holds every argument of `_build_repo_of`. `("a_night", batch_id, tuple(changed))` holds every argument of `_night_repos`. `constraints` and `others` act after the copy. The builders read no environment that a test changes.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/c81dd240-3837-494d-a148-76820abc8093/scratchpad/rv203/`.

- `p1.py`: imports the worktree's conftest. It lists the rebound modules, imports the late modules, compares a fresh database with a wrapper copy and a raw copy, and patches `rota.core.db.init_db`.
- `p3.py`: builds the `a_night` template and copies it to a path with a space and to `<base>_copy`. It reads `.git` and `gitdir`, `rev-parse --show-toplevel`, `worktree list` and `status`. It commits in the copy and reads the template's HEAD. Run three times: TEMP with a space, TEMP in lowercase, and TEMP with `..`.
- pytest on the four files above.
- `pytest tests/rota --setup-only -rs`, grouped by skip reason.
- `ls` counts of the template directories under `C:/Users/roman/rota_gate/tmp`.

## (d) Usage

Estimate: about 60k input tokens, 10k output tokens, 70k total. The harness line is the true count.
