# Frame 246, pass 1b: the diff review

Commit 9d24ce8b, read in the worktree `C:/Users/roman/rota_r246b`. Reviewer: an Opus agent of session cd6300cd, 2026-10-15.

Verdict: ACCEPT. The pass closes findings 1 and 3 of review 1. It touches nothing else. Two lows stay, and neither blocks.

## (a) The verdict on each point

1. Yes. `@prose` renders as "the README". Every other bare ref loses its `@`. A ref with a colon renders as before (probes 1 and 2).
2. With the eight rows of review 1's probe 1, the last two rows drop: the Terminologist's `src/store` and the Developer's `bg_2`. That is the first-come order (probe 3).
3. Both tests are red at 401bbf3f on the old behaviour, and green at 9d24ce8b. The two files and the diff hold 0 CR bytes (probes 4 and 5).
4. The diff touches `code_gaps` and the two new tests only. Between 401bbf3f and 9d24ce8b no other code file changed.
5. Night 150: a quarantined `@prose` reconcile key reads "comparing the account with the README", and no gap fact holds an `@` or a `|`.

## Answers in detail

### 1. The bare refs

The night database `clickI_night149.db` holds one quarantined row only, `-|tick:constraint_zero|`. `code_gaps` filters that row, so the night renders no quarantine fact. The probe copied the database into memory with the backup API from a `?mode=ro` connection. Then it put ten synthetic rows into the copy and called `code_gaps`. The first six facts were these:

- `@prose` gave "comparing the account with the README".
- `@prose:docs/usage.md` gave "docs/usage.md", as before.
- `@surface:.readthedocs.yaml` gave ".readthedocs.yaml", as before.
- `@claim:constraints:c7` gave "checking the claim c7", as before.
- `@src` gave "src".
- A bare `@` gives an empty ref. The `or` then gives "the whole project". That result is correct, but it comes from the fallback and not from a rule.

A second probe rendered the other pseudo areas of `scheduler.py:543-549`. `@program`, `@frame`, `@reorient` and `@blindspots` render with no `@`. The words are internal names, for example "work on frame" (finding 1).

### 2. The order

`tick_attempts` has `tick_key TEXT PRIMARY KEY`, so the table has an implicit rowid. `note_dispatch` writes the row with `INSERT ... ON CONFLICT DO UPDATE`, which keeps the rowid. The quarantine writers use `UPDATE`, which keeps the rowid too. No code in `rota/` runs `VACUUM`, so no rowid changes after the insert. So the rowid order is the order of the first dispatch of each key. A key that `clear_dispatch` or `_lift_quarantines` deleted gets a new rowid when it comes back, so it sorts as a new key. That is the correct reading of "first come".

Review 1's probe 1 at 9d24ce8b printed the first six rows in insert order: both reconcile rows, three Critic rows, and the Architect row. The Terminologist row and the Developer row dropped.

### 3. The tests

- `test_the_gaps_name_the_readme_reconcile_in_words` at 401bbf3f failed on `assert not [...]`. The fact read "comparing the account with @prose". That is finding 1 of review 1.
- `test_the_gaps_keep_the_first_quarantines_whatever_the_seat` at 401bbf3f failed on `any("docs/usage.md" ...)`. The six facts were the Architect rows and the Critic rows, sorted by key. That is finding 3 of review 1.
- At 9d24ce8b, `tests/rota/test_onboarding_phases.py` gave 91 passed.
- The second test fails under `ORDER BY tick_key DESC` too, because the Critic rows `c1` and `c2` then win. So the test holds the order and not only one wrong order. That is reasoned from the keys, and not run.

### 4. Scope

`git diff --stat 401bbf3f 9d24ce8b -- rota tests` shows the two files of this commit only. The commits between them are `docs(plans)` commits. `_ref_words` is defined inside the loop. That costs nothing at six rows and changes no behaviour.

### 5. The line for night 150

Read each gap fact of the Liaison's notes and the principal's page. Expect "the README" for the `@prose` reconcile key and no `@`, `|` or `tick:` in any fact.

## (b) Findings

1. `rota/roles/api.py:11563`, severity low, CONFIRMED. The bare pseudo areas render as internal names: "The Vision Keeper could not finish work on frame after 3 tries". Probe 2 printed this for `@program`, `@frame`, `@reorient` and `@blindspots`. The kinds `orient`, `frame`, `reorient`, `blindspot`, `define` and `survey` have no entry in `kind_words`, so they read "work on". No night database holds such a key (review 1, probe 3). Fix: give each pseudo area and each onboarding kind its words in one helper, the helper that frame 253 builds for its two routes.
2. `rota/roles/api.py:11545`, severity low, PLAUSIBLE. `ORDER BY rowid` keeps the first dispatch, not the first quarantine. A key that ran early and was quarantined late wins over a key quarantined first. This is reasoned from `note_dispatch` and `quarantine_overrun`, and no probe staged it. The difference matters only above six quarantined keys, and no night has more than six. Fix: none needed now. Record the meaning beside the comment if a later frame adds a quarantine time.

## (c) Probes

All probe files are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/cd6300cd-93cb-43d0-81c1-5833e2698637/scratchpad/r1b/`.

1. `probe_night.py`: opened `D:/repos/rota/.rota/clickI_night149.db` with `?mode=ro`, copied it to memory, and called `code_gaps` on the night as is. Then it replaced the rows with ten synthetic keys and called `code_gaps` again.
2. `probe_bare.py`: five keys with `@program`, `@blindspots`, `@frame`, `@reorient` and `@term:widget` in a fresh database.
3. `probe_eight.py`: review 1's probe 1, copied unchanged, run at 9d24ce8b.
4. `parent/`: `git archive 401bbf3f` of `rota`, `pytest.ini`, `pyproject.toml` and `rota_serial_plugin.py`, with `tests` from 9d24ce8b. `pytest -n0 -k "readme_reconcile or first_quarantines"` gave 2 failed, for the reasons in answer 3.
5. At 9d24ce8b: the whole `tests/rota/test_onboarding_phases.py` gave 91 passed in 54 s. A count of CR bytes gave 0 in `api.py`, 0 in the test file and 0 in `git show 9d24ce8b`.

The gate did not run. No point needed the full suite, because the diff touches one function and adds two tests.

## (d) Usage

The harness line holds the exact numbers. The estimate is about 40k input and 6k output, about 46k in total, against the 40k cap. No sub-agent ran.
