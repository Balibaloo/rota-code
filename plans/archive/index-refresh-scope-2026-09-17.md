# Scope report: the code index after a commit (frame 33, 2026-09-17)

Rota workflow. Observed by a reviewer-type agent, read-only, 76k on the
harness line, 52 tool calls, 2026-09-17. Every line below is the agent's
finding with its file and line. The design record that reads this page
is `plans/archive/index-refresh-design-2026-09-17.md`.

## Verdicts, one line per question

1. Built once in `boot.onboard` by `indexer.build`, on the main checkout at `config.project_root`; two tables, `code_index` and `code_edges`.
2. 75 reader sites on `code_index`; the seats' probes are `code.probe`, `code.survey`, `code.callables`, `code.source`; the signoff prediction is `principal.near_code`; the diff check reads `batch_touch`, not the index.
3. `code.commit` writes `batches.head_commit` and `touch_strays` through the pipeline and never touches the index; `lifecycle.merge` merges into main and never re-reads or rebuilds it.
4. Per run. One index per database, of one commit of the main checkout. A worktree differs by the branch base, the Developer's commits, the harness's test files and the scaffold floor.
5. Existing tests cover build, replace-on-rebuild, chaos mid-swap and a refresh under a running batch. No test asserts a probe sees a committed symbol.
6. Finding 42 is at `plans/wake-audit.md:71`. Quoted below.
7. Three hook points: inside `code_commit`, after `session_commit` in the runner, after `worktrees.integrate` in `lifecycle.merge`. Measured cost 0.5 to 1.3 s on click.

## Facts

### 1. Where the index is built

1. `rota/onboarding/boot.py:81-83`: `onboard(conn, root)` calls `indexer.build(conn, root)` first, then `areas_mod.propose`, `areas_mod.pin` (84-85), `lexicon_mod.build` (86), writes `config.project_root` (87-88), then `checkout_of(root)` stamps `config.project_branch` and `config.project_commit` (103-106).
2. `rota/onboarding/indexer.py:343-430`: `build` walks the tree (356), hashes each file (366), parses symbols (382), resolves import edges (389-396), then in one `BEGIN IMMEDIATE` transaction deletes both tables (409-410) and inserts path grains with `content_hash` (412-415) and symbol grains as `path::symbol` (417-419), and `code_edges` (421).
3. `rota/core/schema.sql:370-381`: `code_index(grain PK, grain_kind, area, fan_in, sym_kind, content_hash)`. Comment at 368-369: "Not an artefact any role writes: it is rebuilt, never decided." `code_edges(src, dst)` at 383-387.
4. Map of `code_index`: writers are `indexer.build` (410, 413, 418) and `areas.pin` (`rota/onboarding/areas.py:254, 263, 271`), which fills `area`. `build` leaves `area` NULL; `boot.repin` at `rota/onboarding/boot.py:193-211` re-pins, rebuilds the lexicon and rebinds constraint zero.
5. Which checkout: `root` is the project root. `rota/core/worktrees.py:43-63` `project_root` reads `config.project_root`, no default. Worktrees live under `<project>/.rota/worktrees/<batch>` (66-74) and `.rota` is in `SKIP_DIRS`, so `walk` never indexes a worktree (`indexer.py:323-326, 333`).
6. Other callers of `indexer.build`: `rota/cli.py:665` in `cmd_refresh` (operator command), `rota/testkit/fixtures.py:724`. No caller in `rota/core` or `rota/roles`.

### 2. Who reads the index

7. `rota/roles/api.py:5442-5451`: `code.probe` is `SELECT grain, grain_kind, area, fan_in FROM code_index WHERE grain LIKE ?`. Database only. No tree read. This is the probe finding 42 names.
8. `code.source` at `api.py:7153-7179` reads the batch's worktree when there is one, else the project root (`_worktree_of`, 7381-7399). A miss falls back to `_indexed_like` (7171, 7414-7452), which reads the index.
9. Other seat probes on the index (map): `code_area` 5657, `code_prose` 5821, `code_front` 5863-5872, `code_vocabulary` 6117, `code_concordance` 6246-6255, `code_gaps` 6572, `code_tree` 6870, `code_survey` 7099, `code_callables` 7117, `code_boundary` 7030 (edges).
10. Signoff prediction, partial A7 piece 2: `rota/roles/principal.py:425-454` `near_code` scans `SELECT grain FROM code_index WHERE grain_kind = 'symbol'` (446-447) for the item's words. Caller: `render_page` at `principal.py:383`.
11. The batch's prediction: `batches.annotate` at `api.py:3717-3764` reads path grains (3737-3738) to refuse a directory the index lacks (3746-3755), then writes `batch_touch` rows through the pipeline (3756-3763). This is the only prediction found for a batch; the phrase "sentence three's first prediction" occurs only at `plans/stack.md:36-37`, with no function named. Reasoned: it names this call, the Architect's first `batches.annotate` on the batch.
12. The check against the diff: `_predicted_touch` at `api.py:8452-8462` reads `batch_touch`; `_outside_prediction` at 8465-8477 reads `touch_strays` and `stray_paths`. Neither reads `code_index`. The stale index enters through what `annotate` refused or allowed, not through the check.
13. Freshness readers: `area_content_hash` at `api.py:2457-2474` aggregates `content_hash` of path grains per area. `scheduler._survey_wakes` at `rota/core/scheduler.py:849-859` compares it with `survey_records.area_hash`; a mismatch makes the area unsurveyed and re-fires three roles. `sandbox.build` at `rota/core/sandbox.py:545-548` stamps `ctx.area_hash_at_wake` when a session is built. `surveys_attest` at `api.py:2873` stamps it into the record.
14. Duplicate-name door in `code.write` at `api.py:7799-7810` reads symbol grains and then adds `_defined_in_tree` (7810) because "The index is the tree at onboarding; the batch's own commits are not in it." This is finding 27's fix (`plans/wake-audit.md:56`). An empty write at 7550-7552 reads path grains to decide whether a file existed before the batch.
15. Other readers that a stale index misleads: `criteria_specify` via `_surface_names_what_the_item_names` (3268-3317, 3446), `_vet_surface` (3124-3162), `check_bindings_resolve` (`rota/roles/validators.py:126-128`), `orphaned_grain_refs` (`rota/tools/audit.py:189`).

### 3. What a commit changes

16. `code_commit` at `api.py:8299-8449`: refuses an undefined surface by reading the worktree (8349-8353, 8363-8369), then `worktrees.commit(tree, message, exclude=test_paths)` (8410). On success it appends `("batches", batch_id, {"head_commit": sha})` (8428), computes `touched` from git (8429), and appends one `touch_strays` row per stray (8437-8441). No read or write of `code_index`.
17. The rows land at `rota/core/runner.py:2264` (`writes=[_as_write(w) ...]`) and `session_commit(conn, result)` at 2282. The one post-landing hook that exists is `apply_rulings` at 2287-2290, keyed on a `rulings` write.
18. `lifecycle.merge` at `rota/core/lifecycle.py:137-190`: materialises and commits the tests in the worktree (156-162), `worktrees.integrate` (167) runs `git merge --no-ff` in `project_root` (`worktrees.py:274-286`), sets `status = 'merged'` (176), records `delivered:<item>` (184-185), tears down the environment (186) and destroys the worktree (188). No index read, no rebuild, no `repin`. Caller: `loop._perform` at `rota/core/loop.py:281-284` for `do:merge` (`predicates.py:1206`).
19. `cmd_refresh` at `rota/cli.py:645-684` is the only existing refresh: `indexer.build` (665), `boot.repin` (666), `project_commit` update (667-669), `tick_survey` to reopen changed areas (671), `orphaned_grain_refs` (672-674). It is an operator command, never called by the loop.

### 4. Per run, per batch or per worktree

20. Per run. One `code_index` per database, one `project_root` (`worktrees.py:57-63`), one `project_commit` (`boot.py:103-106`). Nothing keys a grain by batch or worktree.
21. A worktree starts as branch `batch/<id>` off the main branch at `lifecycle.start` (`lifecycle.py:59`, `worktrees.py:130-132`). While the batch runs its files differ from the indexed tree by: the scaffold floor (`lifecycle.py:72`), the Developer's commits (`api.py:8410`), the harness's test files (`lifecycle.py:161`; `api.py:8401-8409`), and the Developer's uncommitted writes (`code.write`, 7504-8215).
22. After a merge, main moves (`worktrees.py:278-286`) and the index still describes `project_commit` at onboarding. The next batch's worktree branches from the moved main, so the gap grows by every merged batch.

### 5. Existing tests and the pinned test

23. `tests/rota/test_onboarding.py:44` covers both languages, `:59` no-parser files, `:90` symbols under the defining file, `:136` reindex replaces rather than accumulates, `:1277` symbol kinds, `:1364-1433` a refresh under a running batch keeps the batch, reopens the edited area and reports dropped grains.
24. `tests/rota/test_chaos_staytrue.py:49` pins the transaction at `indexer.py:407-426`.
25. `tests/rota/test_touch_divergence.py:44` a stray row on commit, `:134` a second definition refused, `:175-187` a name the batch defined is seen without the index (worktree read, finding 27).
26. `tests/rota/test_night46_context.py:56, 232, 565` insert `code_index` rows by hand; line 74 asserts an empty probe is a note. No test commits a new function and then probes for it.
27. A pinned test for the refresh would: onboard a git fixture, start a batch with a worktree, `code.write` a new `def`, `code.commit`, land the session, then assert `code.probe(pattern=<name>)` returns `path::name` with `sym_kind='function'`, and assert `principal.near_code(conn, "<name word>")` lists the file. A second assertion after `lifecycle.merge`: the same probe from a session with no batch.

### 6. Finding 42's text

28. `plans/wake-audit.md:71`, quoted: "| 42 | click n46 s155 | developer tests_failing | `code.probe(pattern='echo_json')` returned nothing for a symbol the batch had committed: the index is built at onboarding (`indexer.build`) and never refreshed after a commit | an index that knows the batch's own symbols | open. A refresh after `code.commit` and `do:merge`; the area content hashes depend on it, so the freshness rule needs reading first |".
29. Related: finding 27 at `plans/wake-audit.md:56` (the duplicate-name door, fixed by reading the worktree).

### 7. Hook points

30. Measured cost (this probe): clickI checkout, 163 files, 915 symbols: 1.30 s cold, 0.50 s warm. The rota repo, 572 files, 2783 symbols: 5.26 s cold, 3.70 s warm. No measurement exists in `plans/operating-facts.md`.

- **A. Inside `code_commit`, after `worktrees.commit` returns a sha**, `rota/roles/api.py:8428`. Rebuild from `tree`, the worktree. Cost: one build per commit; twelve commits in one session are on record (`api.py:8378-8383`), so up to 15 s per session on click. Risk: a raw write inside a session, outside the pipeline, on the session's connection; a session that dies after the commit leaves the index at the worktree while `batches.head_commit` never lands (`runner.py:2282`). Every area hash changes, so `_survey_wakes` (`scheduler.py:851-859`) reopens the touched areas and a concurrent survey's `area_hash_at_wake` (`sandbox.py:548`) goes stale.
- **B. After `session_commit` in the runner**, `rota/core/runner.py:2282-2290`, keyed on a `batches` write carrying `head_commit`, the pattern `apply_rulings` uses at 2287. Rebuild from the batch's worktree. Cost: one build per Developer session that committed, not per commit. Risk: the same hash flip as A. `area` is NULL until `boot.repin` runs (`boot.py:207-208`), and repin re-runs `refresh_constraint_zero` (210), which can rebind constraint zero to a moved partition mid-batch.
- **C. After `worktrees.integrate` in `lifecycle.merge`**, `rota/core/lifecycle.py:167-176`, or after `lifecycle.merge` in `loop._perform` (`loop.py:283`). Rebuild from `project_root` and `repin`, then update `project_commit` as `cmd_refresh` does (`cli.py:665-669`). Cost: one build per merge. Risk: lowest for correctness of the index, since it describes main again, but it does not answer finding 42 inside the batch: the Developer's `tests_failing` probe at n46 s155 ran before the merge. The hash flip is real here and legitimate under `cmd_refresh`'s contract (`cli.py:647-652`), so three survey wakes per changed area fire in the middle of a night.

## Open questions the design must settle

- Which tree the index describes between a commit and the merge: main, the worktree, or main plus the running batch's symbols. Only one batch runs at a time (`loop.py:268-269`), so a worktree index is well defined, but the Architect's `code.source` reads main when no batch is in context (`api.py:7399`).
- Whether a batch's own commit counts as a tree change under the freshness rule (`scheduler.py:841-859`). Options: freeze `content_hash` on existing paths during an in-batch refresh, stamp hashes at merge only, or accept the reopen. Finding 42's note says this rule "needs reading first".
- Whether a refresh is one function shared by `cmd_refresh`, hook B and hook C (`build` + `repin` + `project_commit` + `orphaned_grain_refs`), and whether `frame_repinned` (`scheduler.py:481-484`) still holds after it.
- Whether the raw writer stays raw. `code_index` has no pipeline writer by design (`schema.sql:368-369`); the diff review will ask if law 1 applies.
- Whether the refresh also cures `near_code` at signoff, which reads only symbol grains (`principal.py:446-447`): a merge-time refresh does, a commit-time one does as well; the design says which and the pinned test asserts it.
