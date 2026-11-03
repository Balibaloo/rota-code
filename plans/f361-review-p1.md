# Frame 361, review of passes 1 and 1b

Verdict: fix. The code does what the ruling asks. The default moves 38 tests to red, and the implementer ran none of those files. The worktree is `C:/Users/roman/rota_r361` at `6447973d`, reviewed read-only. Findings: 2 high, 6 low.

## (a) The verdict on each point

1. Holds. No election reads `lazy`, `eager` wins, and a stored `eager` reads `eager`. No code path writes `lazy` into config (finding 6 is a note).
2. Holds. 223 ledger rows are open after the deferral, and the line says 223. The line shows once on every state print. It can never go away (finding 2).
3. Holds. No reader re-opens or re-pages a parked row. The merge parks no lazy row a second time. The record row leaks into `ledger.list(shipped=)` (finding 4).
4. Partly holds. `caselessdict.py` binds 5 rows, not the 9 that the report says. A path with no area changes the note (finding 3).
5. Holds. The agenda pages every non-lazy open row, `conflict` rows included. The signoff hook adds non-lazy rows and leaves lazy rows out.
6. Holds. One id lands every row of the wake. The door merges the wake refs first and refuses an empty list after the merge. The order matters only for an empty list.
7. Holds. No edit weakens an assertion. Five edits only add `eager`. One test moves its bound by the ruling. One edit is an allow-list entry.
8. Fails. The default turns 1 register case red and makes its recording STALE. It also turns 3 test files red outside the register (finding 1).

## (b) Findings

1. **High. CONFIRMED.** The default breaks four test files that the implementer did not run. Each one ran green on an export of `12c26a46`.
   - `rota/testkit/scenes.py:1125-1130`: the `critic` scene seats `liaison|tick:observed_entries|<k>`. Under `lazy` the loop takes `do:defer_baseline`, and the seat is never used. `test_scene_review.py` plus `test_scene_review_again.py` give `32 failed, 3 errors`. The message is "the loop never asked for {'liaison|tick:observed_entries|a_charge_is_a_whole_number_of_cents': 1, ...}".
   - `tests/rota/cases/l1_liaison2.yaml:214`: the fixture of `L1-LI-present-what-onboarding-only-observed` holds no election. `test_case_reachability.py` fails with "that predicate wakes ['-'] here".
   - `tests/rota/test_refs.py::test_observed_entries_presents_the_code_and_not_the_world` gets `do:defer_baseline` where it expects `tick:observed_entries`.
   - `tests/rota/test_chaos.py::test_the_scheduler_killed_between_steps_loses_nothing` gets a `do:defer_baseline` step, and the step has no outcome.
   - Fix: set `eager` in `scenes.critic` (a `config` row after `_base`), in the case fixture (a `config` row for `baseline_election`), and in the two tests. Then run the gate.

2. **High. CONFIRMED.** Some lazy rows can never bind a touch, so they wait for ever. On the dry3w7 copy, 25 of 223 rows have no rule: 20 glossary rows with an empty area and 5 item rows. `first_touch_rows` binds no item row, and no `model_areas` row has the empty id (`rota/core/lifecycle.py:681-688`). The agenda and the signoff hook leave these rows out. The state line "They wait in the ledger until a change touches them" then never goes away, and for these 25 rows that sentence is false. Fix: bind a glossary row with no area like a root-area row, and bind an item row when a batch of that item touches. Or give these rows one path out, and count them in their own words.

3. **Low. CONFIRMED.** A path with no deeper area binds the root area. A batch that touches `docs/nowhere/x.txt` binds the `.` area row and the one glossary row of area `.`. The note gains "notes the team recorded about this ground ...". `under()` returns True for `.` (`lifecycle.py:668-676`), so `.` becomes the area when no deeper area holds the path. The docstring says the root area "does not bind every note to every change". This is true only after the first such touch parks those rows. Fix: decide whether a root touch shows root notes, then make the code or the docstring match.

4. **Low. CONFIRMED.** The first-touch record row reaches its item. `ledger_items` of the record returns `{'canonical_order_duplicate_keys'}`. So `ledger.list(shipped=<item>)` lists the record under "open when X shipped" (`rota/roles/api.py:16331-16360`). It shows the raw words `Shown at the first touch of a change: {"batch": ..., "rows": [...]}`, because only `RESURVEY_WORDS` rows get their refs turned into words. The record was never open when the item shipped. Fix: leave `FIRST_TOUCH_WORDS` rows out of `ledger_list`, or give the record `about_table = 'batches'` so that it reaches no item.

5. **Low. CONFIRMED.** `_why_idle` counts lazy rows as open assumptions (`rota/core/loop.py:703-706`). On the deferred copy it returns "idle with 223 open assumption(s)". Each onboarded project under the default now idles with this note. Fix: leave the `LAZY_WORDS` rows out of the count, as `tick_agenda` does.

6. **Low. CONFIRMED.** An older run database that ran eager by default changes to `lazy` at the upgrade. dry3w7 holds no election row and showed the eager page. With the new code, `observed_entries` returns `do:defer_baseline` on 234 rows. With `eager` stored, it returns `tick:observed_entries` on 235 rows. This follows the ruling, because he did not choose. No code path writes `lazy`, so `config_history` stays empty and `rota elect eager` still wins. Fix: no code change. Name the change in the frame's status line for any resumed run.

7. **Low. CONFIRMED.** A stored JSON empty string reads two ways. `config.get` returns the empty string, and `observed_entries` reads `lazy` (`predicates.py:789-792`). Today only the predicate reads the value. Fix: read the election through `config.get` and treat the empty string as the default there, so that one reader holds the rule.

8. **Low. CONFIRMED.** The eager wake of dry3w7 carries 240 refs but only 223 distinct ids. So `defer_baseline` reports "deferred 240 observed rows" for 223 rows, and the prompt and the tests count 240. The duplicates are older than this change. Fix: de-duplicate `offered` in `observed_entries` before the wake.

Outside the points, and accepted: the race of the report's Q3. A batch can merge before the clerk's tick. Then `touch_note` no longer lists that batch, the rows stay open, and a later note on the same ground shows them a second time.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/07f209e6-af4a-434b-ac50-5b4ac1e3f670/scratchpad/r361/`. Each probe worked on a copy in a `tempfile.mkdtemp()` directory. The original dry3w7 was opened only with `mode=ro`.

- `p1_default.py`: a fresh database, then `config.set eager`, then a JSON empty string, then dry3w7 as it is and with `eager` stored. Points 1, 6 and 7.
- `p2_defer.py`: the drain on the copy. The result was resurvey 8, then `defer_baseline` 240, open 223, `lazy_count` 223, and the line once on each of two prints. `p2b_gap.py` showed 223 distinct `about_ref` and the table split.
- `p4_touch.py`: the binding of `caselessdict.py` (5 rows), the no-area path (2 rows), and the reach of `ledger_items` (0 lazy rows reach an item). `p4b_unbound.py`: 25 rows with no rule.
- `p3_park.py`: the note, then `do:first_touch` (6 refs), 1 record, the same words after the clerk, and no second wake. A second `record_first_touch` gives 0, `park_merged` gives 0, and the agenda gives an empty list.
- `p5_agenda.py`: three agenda wakes page `Lc1` (conflict) and `Ld1`, with 0 lazy rows. A `possible` symbol touch binds the constraint `alarms`.
- `p6_door.py one|empty`: an eager 240-ref wake through `run_session` with `ScriptedBackend`. Both calls land 223 ids plus `reading:m44`. The session ends at the present in one turn, so no reply goes back to the model. The wake text is 4963 characters, with no CUT.
- One `-c` call: `_why_idle` on the deferred copy.
- pytest in the worktree: `test_case_reachability.py -k observed` (1 failed), `test_scene_review.py test_scene_review_again.py` (32 failed, 3 errors), 12 scene and neighbour files (1 failed, 965 passed), 34 candidate files not in the report (2 failed, 1168 passed), and `test_l3*.py` (4 passed, 32 skipped).
- pytest on `git archive 12c26a46`, exported to `r361/base`: the review scenes and the reachability case gave 44 passed. The two reds of `test_refs` and `test_chaos` gave 2 passed.
- The gate did not run.

Point 8, the register count: 20 cases seed observed rows with no election. Only `L1-LI-present-what-onboarding-only-observed` reads `observed_entries`. Its tick goes red in reachability, and its prompt edit makes its recording STALE. The other 19 cases replay their own tick or message. No lazy row exists in their fixtures, so their scenes are unchanged (PLAUSIBLE from the read). `L3-a-maintainers-question-reaches-the-owner` runs the loop, and its 32 L3 tests skip here, so its replay is not measured.

## (d) Usage

These are estimates, because the harness shows no count. Input: about 95k tokens. Output: about 12k tokens. Total: about 107k tokens. That is above the cap of about 60k. The extra came from the test runs that found finding 1.
