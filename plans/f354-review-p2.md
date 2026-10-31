# Review p2 of frame 354: commit 751eab24

Verdict: the claim holds, with 1 high and 3 low findings. Points: 5 hold, 1 holds with a finding (point 1). Tests: 10 passed and 35 passed.

## (a) Verdicts on the points

1. The regroup path holds, but the stale group key misinforms the Liaison. A group key of 3 files at 3 attempts goes to `alone` (scheduler.py 803 to 806). Each file then wakes as `(a,)` under a new key with its own count. A one-file key at the bound goes to `abandoned`. `quarantine_stalled` never deletes a quarantined row (scheduler.py 2690), so the group key stays in `tick_attempts` with `quarantined = 1`. The `quarantined` predicate reads it with `unreported=True` and wakes the Liaison with "1 abandoned: reconcile for ... 3 attempts" (predicates.py 1765 to 1797). The probe closed all 3 files, and the predicate still sent that line. The report is wrong, because no file is abandoned. The page readers `render_state` and `_stalled_keys` (principal.py 415, 460, 2006) read the same key. A file that closed inside the failed group is excluded: `done` filters `open_areas` before `alone` builds the single wakes.
2. The door accepts the run's shape by design. The comment at api.py 15647 says "reconcile logs 'README says X' about README.md under items". The brief's template is a different shape: `about_ref` is an item id or `"@prose"`, and `about_table` is "items" or the file's path (reconcile.md 17 to 18). The readers of `ledger.about_table` are: predicates.py 559 (only `glossary_terms`), the ledger listings at api.py 15941 and 15948, the id key at identity.py 95, and `_ledger_names` at api.py 5019. No reader joins `about_table = 'items'` to the `items` table, and the pages read `about_ref`. So no code reader is misled. A seat that reads the listing sees "items" beside a path.
3. A code grain is never written for a group of several. The loop skips each citation whose `_grain_path` is not the row's own file (api.py 4984). The probe cited `src/x.py` over 3 files, and no row got it. A group of one keeps every citation, as before. The only reader of `survey_citations` is `check_survey_citations` (validators.py 150, 158). That reader counts rows and `resolves`, and it needs no code grain.
4. The paragraph is outside the budget and inside the cut. `_prose_group_text` cuts the files at `cap` (18,000) and then puts the lead in front (api.py 18177). The lead plus 18,000 plus the `files` line stays under `PUSH_CHARS` 20,000. On s18 (2 files) the text reads: "This wake holds these 2 files: docs/unicode-support.md, docs/upgrade-guides.md. Check each file against the account, one file at a time. Close each file with its own `surveys.attest`, with that file's path in citations. The session ends when every file has its row." The largest pushed `[code.prose]` is s16, 3 files, 17,504 characters, with no cut. The one-file wakes s6, s7, s8 and s13 have no lead, and they keep the 6,000 cut.
5. No hunk is outside the claim. `reconcile.md` is the same bytes as at 24b75e68: `git diff 24b75e68 751eab24` on the file is empty.
6. `test_onboarding_phases.py -k reconcile -n0`: 10 passed, 86 deselected. `test_prompts.py -n0`: 35 passed.

## (b) Findings

1. rota/core/predicates.py 1765 with rota/core/scheduler.py 803, high, CONFIRMED. A quarantined reconcile key of several files stays in `tick_attempts`. The Liaison then reports the group as abandoned after its files close alone. The probe gave `'1 abandoned: reconcile for @prose, @prose:docs/a.md, @prose:docs/b.md (vision_keeper), 3 attempts'`, and all 3 files had a row. Fix: the `quarantined` predicate and the page readers skip a `tick:reconcile` key of more than one ref, because the scheduler wakes those files alone.
2. rota/roles/api.py 5020, low, CONFIRMED. `_ledger_names` matches `ref == area`, and the README's area id is `@prose`. The brief tells a docs conflict to use `about_ref="@prose"` with the file's path in `about_table`. The probe logged a conflict on docs/a.md and attested README.md, docs/a.md and docs/b.md. The README row got `found`. Fix: match `about_ref == area` only when `about_table` is empty or names that same file.
3. rota/roles/api.py 4960, low, CONFIRMED. `several` tests `len(targets) > 1`, not the group size. An attest in a group that closes one file keeps the old stamp. The probe logged a conflict on docs/b.md and attested `found` with docs/a.md only. docs/a.md got `found` and docs/b.md got `none_found`. Fix: apply the named test whenever `len(group) > 1`.
4. rota/roles/api.py 5017, low, PLAUSIBLE. A row with `about_ref=<item id>, about_table="items"` names no file. The brief offers that shape first. In a group of several, a `found` attest after such a row stamps `none_found` on every file. The fixture holds no item, so no probe ran. Fix: in a group, refuse the `found` attest when no target is named, and ask for the file's path in `about_table`.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/05666872-07ce-4805-be2d-636d5ab7329f/scratchpad/f354r2_q1.py` and `f354r2_q2.py` in the same folder: read-only queries on `f354p2.db`. The queries read the `tick_attempts` rows, the `tick:quarantined` details, the 4 conflict rows, the `found` rows and their citations.
- Two inline queries on `turns` of `f354p2.db` measured the `[code.prose]` section of turn 1 of the 17 reconcile sessions and quoted s18.
- `tests/rota/test_zz_f354r2_probe.py` in the worktree, now deleted. The test used `ScriptedBackend` on `_prose_group_of_three`. Case A found the README marked `found`. Case B found docs/a.md marked `found` for a docs/b.md conflict. Case C found no item in the fixture.
- `tests/rota/test_zz_f354r2_probe2.py` in the worktree, now deleted. The test added a quarantined group key and 3 closed rows, then called `tick_reconcile` and `quarantined`. It found no wakes, and it found the false Liaison line.
- `pytest -n0` on the two test files of point 6. `git status --short` in the worktree is clean after the probes.

## (d) Usage

Input tokens about 75,000, output tokens about 9,000, total about 84,000. The figures are estimates, because the harness shows no counter.
