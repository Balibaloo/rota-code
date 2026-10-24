# Frame 316, review 2 of 0c8024c9: one item per agenda page, and the park

Reviewer: read-only, Opus. Worktree `C:/Users/roman/rota_r316` at 0c8024c9. No gate run. No tracked file edited.

## (a) The verdicts on the points

1. Starvation: CONFIRMED by design. The second item's rows never come while the running item has an open row. On night 162, no agenda tick fired between s95 and s378. So the confirm rows would never reach the principal before b_2 merged. They park at the merge.
2. The park: the three cases behave as the report says. A shared row stays open, a late row stays open, and a no-item row of the merged batch parks. On night 162, 0 of the 28 parked rows were shown to him as rows. 26 of 28 are about a criterion that he saw on a page. 14 of those criteria have his verdict.
3. The readers: every `status = 'open'` reader is right to leave out a parked row, except `land`. `land` drops a ruling on a row that parked while its page was open (finding 1). `nightcount.py` does not read `ledger`.
4. The mark: `clickI_warm.db` carries `ledger-grid-faults`. The warm stamp lists `db.py`, `schema.sql` and `scheduler.py` as hard files. So the next night goes cold by itself and deletes the snapshot. A seam start from night 161 or 162 is refused. No tracked fixture carries the old mark.
5. The deviations: the inherited-test guard holds for a row with no writer. A row with a writer now goes to the writer's batch item (finding 4). The reply-row rule is correct. No route shows a parked row's words to the principal (finding 2).
6. The hunks: two more defects (findings 3 and 5).

## (b) Findings

1. `rota/roles/principal.py:2158`, with `rota/core/lifecycle.py:245`. Severity high. CONFIRMED. A ruling on a row that parked while its page was open writes no decision. The merge does not wait for an open agenda page. The probe opened a page with `l_c0`, merged b_2, and landed a contest on `l_c0`. `land` returned `m10`. The row stayed `parked`, with 0 decisions. The shipped line then counts his contested row as a choice "where you said nothing". Fix: in `park_merged`, skip a row named in an open principal message, or let `land` accept a `parked` row.
2. `rota/roles/principal.py:325-331`. Severity medium. CONFIRMED by a read of the code. No route shows a parked row's words. `ledger_list` (`api.py:12307`), the cockpit snapshot (`server.py:153`) and every page reader filter `status = 'open'`. The total also names `scope` and `conflict` rows as "choices". On night 162, 6 of the 28 rows are `scope` rows. Fix: add a reader of parked rows by item, and a line to the Liaison that names it, before the "Ask me to show them." sentence returns.
3. `rota/core/scheduler.py:1112-1114`. Severity medium. CONFIRMED. A row of a queued item waits for as long as the running item has an open row. The probe added one version row on each of 5 ticks. The confirm row `l_c0` was on none of the 5 pages. Then its batch runs and merges, and the row parks without a page. On night 162 this pattern parks all 28 rows. Fix: give the oldest waiting item one page after N pages of the running item, or show the row before its batch merges.
4. `rota/core/lifecycle.py:653-665`. Severity low. PLAUSIBLE. A note about an `inh_*` test now falls back to the writer's batch. The frame 209 pin passes only because its fixture has no receipt. On a night, a Developer note on an inherited test becomes a row of the running item, and it parks at the merge. The result is probably right, but no test pins it. Fix: add a test with a receipt for an inherited-test note, and state the intended item.
5. `rota/core/scheduler.py:1102-1104` against `rota/core/lifecycle.py:684-685`. Severity low. PLAUSIBLE. The agenda drops description items from a row's set, and the park does not. A row that reaches the merged item and the account stays open at the merge. The agenda then sees only the merged item for that row. When no live row is left, the page item becomes the merged item. The page `ORDER BY id` also sorts `b_10` before `b_2`. Fix: drop description items in `ledger_items` for both callers.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f1f0bcfa-7b93-4f01-99dc-afb4bf54e8a6/scratchpad/r2_p3.py` read night 162 read-only. It listed the agenda sessions s95 and s378 to s419, and each ledger row with its items and writer. Nothing ran between s95 and s378.
- `.../scratchpad/r2_p4.py` listed the sessions near both merges, and every principal message with its seq and refs.
- `.../scratchpad/r2_p5.py` counted the 28 parked rows against the principal messages before each merge. The result: 0 shown as rows, 14 with a verdict on the about_ref, and 12 with the about_ref shown only.
- `.../scratchpad/test_r2probe.py` used the fixture of `tests/rota/test_frame316_pass2.py`. `test_race_page_open_then_merge` gave finding 1. `test_starve` gave finding 3. Both passed and printed the states.
- Reads: `probes/gauntlet_click.sh:76-88` and `probes/warm_stamp.py:35,131-147` for point 4, and `clickI_warm.db` read-only for the mark.

## (d) Usage

About 100k input tokens of context, about 12k output tokens, about 112k in total. The cap was about 40k. Night 162's message and ledger lists took most of the excess.

Does not stand: the park drops a ruling that the principal gives on an open page (finding 1), and no route shows the parked words (finding 2).

## Re-check of c34c77e3

Read-only, at `c34c77e3` (passes 2b and 2c). The probe `test_r2probe.py` ran again, 2 passed. `r2_p3.py` ran again on night 162 read-only. The four files `test_frame316_pass2.py`, `test_request_page.py`, `test_prompts.py` and `test_refs.py` gave 197 passed and 4 xfailed. No gate ran.

- Finding 1: closed. The probe now prints `status after land: resolved` and `decisions on l_c0: 1`. `land` reads `status IN ('open', 'parked')`.
- Finding 2: closed. `ledger_list(shipped=...)` returns the parked rows of one shipped item with their kind. `converse.md:59` names the route, and `converse.tools` offers `ledger.list`. The Done line gives counts by kind and "Ask me to show them."
- Finding 3: closed for the page order, and open for the shape of night 162. The probe now shows `l_c0` on the first page, before the version rows. The new rule acts only when the agenda fires. The agenda predicate is in band `start`, at order 30 (`predicates.py:75`), so it fires only when no traffic, fix or gate wake is due. On night 162, no agenda session ran between s95 and s378, and b_2 merged before s378. So under the new rule, the first confirm row of the agenda (`l_adb1f2d4ca`, s157) still reaches no page before the merge. The row parks, and the route is now the shipped line and `ledger.list(shipped=...)`. The intent row `l_79905828a5` reached him on the sign-off page m47, as before. The band is a ruling of 2026-09-13 ("After that, nothing waits on a page"). So the remaining gap is by design, and the park with its route is the answer. Severity low.
- Finding 4: closed. `ledger_items` returns an empty set for a test with no criterion, and the writer's batch no longer applies. The frame 209 pin now has a receipt and a checkpoint on bg_2.
- Finding 5: closed. `ledger_items` drops description items for the park and the agenda alike. Running batches order by `rowid`.

The stale set before the gate. The tool text reaches the prompt through `sb.signatures()` (`sandbox.py:492-507`, `runner.py:398`). The prompt shows each tool as `TOOL: name(args)`, with each default written out. The docstring does not reach the prompt. The new argument changes the line to `TOOL: ledger.list(shipped=None)`. Four Liaison modes offer `ledger.list`: `agenda`, `converse`, `round_close` and `submit` (their `.tools` files). So every recorded case of these four modes goes stale. That set is larger than pass 2c's 9 `converse` cases. The `agenda`, `round_close` and `submit` cases were not counted here.

Stands: the five findings are closed in the code and the probes. Before the gate, expect every case of the four Liaison modes to go stale.
