# Frame 203, the gate's wall, pass 1: the implementer's report

The implementer on Opus, session be3ef742's agent, 2026-10-11 14:30 to 16:02. Meta workflow. The edits are in the main checkout, not committed and not staged. The pass measured in two worktrees of its own: `C:/Users/roman/rota_i203` (HEAD 696faa4d plus the pass) and `C:/Users/roman/rota_i203b` (HEAD 696faa4d). The raw lines are in the session scratchpad, `f203/pairs.log`.

## Verdict

Levers 1 and 2 are built and pass their tests. Lever 3 changes nothing, because 8 workers did not win both pairs. The gate in the pass's worktree printed no new red, and its `time:` line is 330.0s against today's 650s to 760s. Read caveat 1 under (c) before you use that number.

## (a) What changed

- `rota/testkit/gitfixture.py` (+86 -35 lines with the next items): one mechanism for every per-process template. `template(key, build)` builds a tree once per process for each key. `copy_template(key, build, dest)` copies the tree and returns the builder's value. `_relink` moves a copied linked worktree's two absolute links to the copy. `_template()` for the sample project now uses `template("sample", ...)`, and the old `_TEMPLATE` global is gone.
- `rota/testkit/dbtemplate.py` (new, 79 lines): a wrapper of `init_db`. On a new file it copies a template database and then calls the real `init_db` on the copy. An existing file and `:memory:` go to the real `init_db` untouched. The key is the sha256 of `schema.sql` plus the source of `init_db`. `install()` binds the wrapper in every loaded `rota.*` module that holds the real `init_db`.
- `tests/rota/conftest.py` (+6 lines): calls `dbtemplate.install()` at import, before any test module imports `init_db`.
- `tests/rota/test_verdict_lines.py` (+31 -10): `s279` copies a template of `_s279_repo`. `_repo_of`, which `s134`, `kinds` and `_one_criterion` use, copies a template keyed by `(rel, before, after)`, built by `_build_repo_of`.
- `tests/rota/test_findings_doors.py` (+20 -9): `a_night` copies a template of `_night_repos`, keyed by `(batch_id, changed)`. The template holds the project `root` and its linked worktree `batch`. `night128`, `night114`, `night118` and the three direct callers use it.
- `tests/rota/test_templates.py` (new, 6 tests): the copied database equals a fresh one in schema text, `PRAGMA user_version` and every table's row count, and its `-wal` file is not empty. An existing file keeps its rows. A schema change gives a new template that holds the new table, and the old key comes back after the undo. A copied s279 repository has the built log, `HEAD` and a clean status. A copied `a_night` pair has the built logs and `HEAD`s, and `git worktree list` and `rev-parse --show-toplevel` name the copy.
- `rota/tools/gate.py`: no change (lever 3).

## (b) The suite

Touched files, `ROTA_MODEL=qwen3:8b ... -m pytest <file> -q -n0 -p no:cacheprovider`:

- In the worktree: `test_templates.py` 6 passed. `test_verdict_lines.py` 69 passed. `test_findings_doors.py` 28 passed. `test_seam_start.py` 17 passed, which monkeypatches `init_db`. `test_onboarding.py` 1 failed and 52 passed. The red, `test_the_same_constraint_written_twice_is_one_gate`, fails at HEAD in `rota_i203b` too.
- In the main checkout, with the other implementer's edits: `test_templates.py`, `test_verdict_lines.py` and `test_findings_doors.py` together, 103 passed.

The gate, one run, from `C:/Users/roman/rota_i203` after the other gates ended (15:56:24 to 16:01:57), with the baseline file copied in:

```
suite: 3 failed, 3347 passed, 195 skipped, 20 xfailed, 17 warnings (baseline: 24 failed, 3580 passed, 32 skipped, 20 xfailed, 17 warnings)
new reds (0): none
reds gone (20): 18 L1 cases and 2 L3 chains (list in the scratchpad task output)
stale: the register is absent (C:\Users\roman\rota_i203\tests\rota\cassettes.db)
time: 330.0s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 5d68808 2026-10-11 02:11
```

The 20 reds gone are not fixed. The worktree has no `cassettes.db`, so the recorded cases skipped. No traceback, because there is no new red. No casestatus count, because the register was absent.

## Each lever, before and after

Load: "gate" is a `python -m rota.tools.gate` of another session on the machine. Another implementer also ran single `test_l1.py` cases in the main checkout during the first measurements.

Lever 1, the template database, `-n0`, `test_desk_guards.py` + `test_runner.py` + `test_t0_sandbox.py`, 507 tests:

| round | before | after | load |
|---|---|---|---|
| 1 | 113.2s | 36.7s | a gate ran at the start of both; it ended during "after" |
| 2 | 377.1s | 54.8s | a full gate with about 40 worker processes started during "before" and ran through "after" |

Round 1 is the clean pair: 3.1 times faster. The whole suite at `-n 16`, the gate's count today: before 627.6s (no gate at the start, a gate started part way), after 462.7s (a gate ran the whole time). Both: 3 failed, the same count. Both runs had no cassette register (caveat 1).

Lever 2, the git templates, `-n0`, three rounds each. Both worktrees held lever 1 for these pairs, so the pair isolates lever 2. A gate ran during all of them.

| file | before | after | median before / after |
|---|---|---|---|
| `test_verdict_lines.py` (69) | 27.1, 30.0, 32.1s | 14.6, 16.0, 31.4s | 30.0s / 16.0s |
| `test_findings_doors.py` (28) | 26.8, 25.7, 24.2s | 12.4, 11.1, 10.8s | 25.7s / 11.1s |

The 31.4s "after" of round 3 is under the gate's peak load. All runs passed.

Lever 3, the worker count, the whole suite in the pass's worktree, `--tb=no -q -p no:cacheprovider`, back to back from 15:11 to 15:32. Another session's gate ran through all four runs.

| pair | `-n 16` | `-n 8` | winner |
|---|---|---|---|
| 1 (16 then 8) | 462.7s | 435.6s | 8 |
| 2 (8 then 16) | 405.9s | 430.9s | 16 |

8 did not win both pairs, so `rota/tools/gate.py` keeps `-n auto`. The second run of each pair was the faster one in both pairs, so the order or the other gate's phase moves the result more than the count does.

## (c) Deviations from the brief

1. The gate ran from the pass's worktree, not the main checkout, so that the other implementer's edits stay out of the pass's reds. The worktree has no `tests/rota/cassettes.db`, so 163 more tests skipped than the baseline, and the 330.0s `time:` line is not the ratio for today's 650s to 760s. The suite runs of levers 1 and 3 skipped the same tests. The next session must gate the main checkout, which holds the register, for the ratio. The brief allowed one gate run, so the pass did not run a second one.
2. `rota/core/db.py` is the other implementer's file, so `init_db` stays as it is. The wrapper in `rota/testkit/dbtemplate.py` replaces `init_db` in the test process at conftest import. It keeps `init_db`'s behaviour on an existing file, and a monkeypatch of `rota.core.db.init_db` still works (`test_seam_start.py` passes).
3. The copied database gets one extra write, `PRAGMA user_version = <same value>`. Without it the copy's `-wal` file is empty, the indexer reads it as a text file, and `test_onboarding.py::test_empty_project_does_not_seed_constraint_zero` found one area. A fresh `init_db` leaves pages in the `-wal`, and the write restores that.
4. `_repo_of` serves `_one_criterion` and `test_a_re_export_lands` as well as `s134` and `kinds`, so those tests copy a template too. `a_batch_repo`, which `test_delivery.py` and `test_desk_guards.py` import, is unchanged, because the brief did not name it.
5. Lever 2 has no git call count. The pass measured wall time only and did not load the count's plugin.
6. The coordinator moved this report from the scratchpad to this tracked path. The file is not staged.

## (d) Open questions for the assistant

1. Gate the main checkout for the frame's ratio. Recommended: run it after the other implementer's pass is committed, so that the reds belong to one pass.
2. Lever 3 measured nothing that decides the count under a parallel gate. Recommended: close lever 3 with no change, or run one pair on a quiet machine with the register present.
3. `install()` rebinds `init_db` in production modules inside the test process, for example `rota.core.boot`. Recommended: keep it. The alternative is an edit of `init_db` in `rota/core/db.py`, after the other implementer's pass lands.
4. The two worktrees `C:/Users/roman/rota_i203` and `C:/Users/roman/rota_i203b` remain for the reviewer. Remove them with `git worktree remove --force` after the review.

## (e) Usage

The agent cannot read its own harness line. Read the tokens from the harness line of this agent's run. No sub-agent ran.
