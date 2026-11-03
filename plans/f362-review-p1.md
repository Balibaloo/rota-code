# Frame 362, review of passes 1 and 1b: the three doors

Verdict: fix. One high finding and five low findings are on the points. One low finding is outside the points.

The review read the worktree `C:/Users/roman/rota_r362` at `ca18e553`, read-only. The probes ran on scratch copies of dry3w7 and on the register fixtures.

## (a) The verdict on each point

1. Partial. The lookup matches the glossary id exactly. A casing variant gets a false "holds no row" note. No old database holds such a ref. See finding 5.
2. Fix. The `criteria`, `criterion_repair` and `unresolved` wakes now get the pushed sentence "Call glossary.lookup(term) with the term you need." The `grouping` wake gets no lookup, because its modes do not list the read. See finding 4.
3. Fix. The files come from `batch_touch` through `predicted_rows`, and from the diff only when a worktree exists. The empty-touch note is false when a global constraint exists. See finding 3.
4. Accept with a note. `PUSH_CHARS` caps each key, not the working set. The new key is the last key. On `bg_1` 2,533 characters come before it. A long wake loses the key first. See finding 6.
5. Fix. The 628 `variable` and `export` grains with no area fall back to the area of their file correctly. A file that is not in `code_index` maps to no area, so `k0` stays with its false headline. See finding 1.
6. Fix. No other reader compares the headline. `findings.find` on `k0` lands on dry3 `bg_1`. Beside a bound constraint, the pushed headline is false. See finding 2.
7. 17 of 198 single-session cases change their first prompt. The 7 chain cases were not measured. The table is in section (b), point 7.
8. Accept. A `term_collision` wake with gone glossary ids still gets "the rows this wake named are gone." The commit message is true.

## (b) Findings

### Finding 1. A file outside `code_index` brings back the false `k0` (high)

- Where: `rota/core/scheduler.py:3237` (`grain_area`), read by `unsurveyed_areas` at 3256, by `constraints_for_grains` at 3226 to 3232, and by `bound_constraints` at `rota/roles/api.py:4231`.
- CONFIRMED. On dry3, every area has a survey record. The probe put `src/icalendar/tests/test_new_thing.py` in the touch set of `bg_1`. `bound_constraints` returned `k0` with the headline "this area has not been surveyed". The area `src/icalendar/tests` has a survey record.
- `constraints_for_grains` gives `["k0"]` for the new file alone and for the new file beside `caselessdict.py`. `unsurveyed_areas` returns an empty list and True there, so the old fallback stays.
- The structural review row keeps the old headline too, because `_zero_row_for` changes the headline only when no grain is unknown.
- A batch that adds a file is the usual case for a Developer and a Tester. The predicted touch set names files that do not exist yet, so the index has no row for them.
- The point-5 check passed: 628 of the 629 no-area grains resolve. The one miss is `.well-known/funding-manifest-urls`, a path with no area.
- Fix: for a path that is not in `code_index`, return `areas.area_of(dirname, coded areas)`, the walk that `indexer.refresh` uses.

### Finding 2. The pushed `k0` headline is false beside a bound constraint (low)

- Where: `rota/core/runner.py:4315` (`ZERO_SURVEYED_HEADLINE`), `4319` (`_zero_row_for`), and the keep set at `4709`.
- CONFIRMED. The probe bound the constraint `wire` to `caselessdict.py` on dry3. The structural push held `k0` with "no constraint binds this diff; every touched area has a survey record", and `wire` beside it.
- In the same session, `_bound_exit` says "The constraints that bind this diff are [wire]". The door refuses `findings.find` on `k0`: "k0 is for a file that no constraint reaches, and 1 constraints reach ...". The refusal costs the seat one turn.
- No other reader compares the headline. The constraint write at `api.py:3906` compares the stored headline, and the stored headline does not change. The merge gate (`lifecycle.py:954`) and the predicates (`predicates.py:1236`, `1669`) exclude `k0` by id.
- `findings.find` with `k0` and `satisfied` lands on dry3 `bg_1` when no other constraint is bound.
- The true wording in both cases: "every touched area has a survey record".
- Fix: drop `k0` from the keep set when `_reaching_constraints` gives another id. Else use the headline "every touched area has a survey record".

### Finding 3. The empty-touch note hides the global constraints (low)

- Where: `rota/roles/api.py:4226` to `4228`.
- CONFIRMED. The probe emptied `batch_touch` for `bg_1` and added the global constraint `gl`. `bound_constraints` returned "Batch bg_1 names no file yet, so no constraint is bound to it." `_reaching_constraints` with an empty file list holds `gl`.
- The files come from `predicted_rows`, which reads `batch_touch`, then from `_diff_files` when a worktree exists. The `guess` table is not read. At `batch_start` the diff is empty, so the touch set alone decides.
- 6 register cases render this note: `L1-DV-build-a-clear-criterion`, `L1-DV-log-the-choice-the-criteria-did-not-make`, `L1-TS-encode-a-criterion`, `L1-TS-a-criterion-no-machine-could-check-is-vision_keepers`, `L1-TS-an-outside-fact-is-the-researchers` and `L1-TS-a-criterion-that-contradicts-the-request-goes-back`.
- Fix: with no files, push the rows that `_reaching_constraints` gives for an empty file list, with the note "Batch names no file yet. The rows below reach every file."

### Finding 4. Non-delivery wakes get a pushed instruction (low)

- Where: `rota/roles/api.py:3716` to `3721`.
- CONFIRMED in the case dump. 5 recorded cases changed from "gone" to "This wake names no glossary row. Call glossary.lookup(term) with the term you need.": 3 Terminologist `tick:criteria`, 1 Terminologist `tick:criterion_repair` and 1 Architect `tick:unresolved`.
- PLAUSIBLE harm. The sentence is an order in a push, and the old note was not an order. The sandbox refuses a Terminologist `report` after a lookup miss and no define. So an extra lookup can block the exit of the seat.
- The `criterion_repair` wake names `c1`, and `c1` has `term_refs`. The door could give those rows. The `criteria` wake names a ticket, and the criteria of the ticket can have refs.
- Fix: skip the key in the push when the wake names no glossary row and no batch. Or resolve a criterion ref or a ticket ref to its `term_refs`.

### Finding 5. A casing variant gets "holds no row" (low)

- Where: `rota/roles/api.py:3658` (`_criteria_term_rows`) and `3636` (`_glossary_rows_of`).
- CONFIRMED on a synthetic ref. The probe gave `c1` the refs `Canonical_Order`, `Calendar` and `calendar`. The push returned the root row `calendar`, which has an empty area. It also returned the note that the glossary holds no row for `Canonical_Order` and `Calendar`. The rows `canonical_order` and `calendar#src_icalendar_cal` (term "Calendar") exist.
- `criteria.specify` stages `term_refs` with no check against `glossary_terms` (`api.py:6578` to `6580`). Only `validators.check_criteria_terms` checks them, after the write.
- The old databases show no such ref. All scratchpad run databases hold 1,728 criteria refs. 288 of them name no id, and none of the 288 is a casing or slug variant of a row. So the note is true on every recorded ref.
- An exact id can name the sense of another area, for example `calendar` in place of `calendar#src_icalendar_cal`. The push shows the `area` column, so the seat can see it.
- Fix: refuse an unknown id at `criteria.specify` with the near ids. Or match the missing refs on the lower-case term before the note.

### Finding 6. The new key is the first key that a cut takes (low)

- Where: `rota/core/runner.py:4421` to `4432`.
- PLAUSIBLE. `PUSH_CHARS` (20,000, `runner.py:1099`) caps each key at render time (`runner.py:1056`). It does not cut the working set. The cut of the whole wake is `_fit`, at two thirds of the budget. `_render_cut` keeps the head.
- The key is the last pushed key at both wakes. On dry3 `bg_1`, with the composed brief, 2,533 characters precede it in the Developer prompt and 2,828 in the Tester prompt. The wake rooms are 11,758 and 11,289 at the `num_ctx` of the run, 16,384. So `bg_1` keeps the key.
- A wake that passes the room loses this key first, before the long reads `batches.expect` and `criteria.load`.
- Fix: put the key before `criteria.load` in the dict, because the key is short.

### Finding 7, outside the points. A batch wake with no refs skips door 1 (low)

- Where: `rota/roles/api.py:3707`.
- CONFIRMED in the case dump. Door 1 runs only when `ctx.wake_refs` is not empty. A `message:answer` wake has no refs, so it takes the typed path with an empty term. It gets "no entry for" the empty term and the glossary size. This happens even when `ctx.batch_id` names the batch.
- 6 recorded Developer and Tester `message:answer` cases render that note. The behaviour is older than this pass.
- Fix: test `ctx.wake_refs or ctx.batch_id` at line 3707.

### Point 7, the changed cases

The dump built the first prompt of every case under the base tree (`D:/repos/rota`, equal to `888dbdf0` in `rota/` and `tests/`) and under the worktree. Then it compared the hashes.

| Wake | Cases | What changed |
|---|---|---|
| Tester `tick:tests_missing` | 7 | the lookup and the new key |
| Developer `tick:batch_start` | 4 | the lookup and the new key |
| Terminologist `tick:criteria` | 3 | the "gone" note became the new note |
| Terminologist `tick:criterion_repair` | 1 | the same |
| Architect `tick:unresolved` | 1 | the same |
| Architect `tick:structural_review` | 1 | the `k0` headline (`L1-AR-a-diff-no-constraint-binds-files-k0`) |

The total is 17. The 7 chain cases, the `L3` and `G1` files, have no top-level role, and the dump did not build them. A chain with a `batch_start` or `tests_missing` leg also goes STALE.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/07f209e6-af4a-434b-ac50-5b4ac1e3f670/scratchpad/`. Each probe copies dry3w7 into a numbered folder under `r362/` before a write.

- `r362_p1.py`: a read-only (`mode=ro`) read of dry3w7: glossary, term refs, touch, constraints, survey areas, `code_index` areas.
- `r362_p2.py` and `r362_p3.py`: over every scratchpad run database, read-only. They count the criteria term refs that name no glossary id and look for casing or slug variants. The result: 1,728 refs, 288 absent, 0 near.
- `r362/probe_a.py`: points 1 and 4. The casing refs, and the push order and offsets with an empty brief.
- `r362/probe_b.py`: point 4 with the composed brief. The offsets and the `_fit` wake rooms.
- `r362/probe_c.py`: points 3, 5 and 6. `constraints_for_grains` in eight states, `bound_constraints` with a new file and with an empty touch set, and the structural push beside a bound constraint.
- `r362/probe_d.py`: point 6. `_bound_exit` and `findings.find` on `k0` and on `wire`.
- `r362/probe_e.py`: points 2, 6 and 8. `findings.find` on `k0` on dry3, the `term_collision` lookup with live and gone ids, and the lookup on the `criteria`, `criterion_repair`, `survey` and `unresolved` wakes.
- `r362/cases_dump.py` and `r362/cmp.py`: point 7. The first prompt of each register case under both trees (`r362/old.json`, `r362/new.json`). No model ran, and the gate did not run.

## (d) Usage

The harness does not show the counts. The estimate: about 100k input tokens in context, about 16k output tokens, about 116k in total. The cap was about 60k, so the review went over the cap. The case dump of point 7 took most of the overrun.

## Second look, pass 1c at eb295ae4

Verdict: fix. Pass 1c fixes findings 1, 2, 4 and 6 and the outside finding 7. It fixes finding 3 only in part. Finding 5 does not change. A new file at the repository root still brings back the false `k0`.

The second look ran the same probes again on fresh copies of dry3w7: `r362/probe_a.py` to `r362/probe_e.py`. The root-file probe is `r362/probe_f.py`. The case dump did not run again.

| Finding | Result | What the probe showed |
|---|---|---|
| 1, a new file outside the index | Fixed | `src/icalendar/tests/test_new_thing.py` maps to `src/icalendar/tests`. `constraints_for_grains` gives no `k0`. `bound_constraints` gives the note that no constraint binds the two files. |
| 2, the `k0` headline beside a bound constraint | Fixed | The pushed headline is now "every touched area has a survey record", which is true beside `wire`. `k0` stays in the push, and the door still refuses a `k0` finding while `wire` binds. The refusal names `wire`, so the cost is one turn at most. |
| 3, the empty-touch note | Partly fixed | The note is now "The touch set of batch bg_1 is empty, so no binding was checked." The note is true. The global constraint `gl` is still not pushed, so the seat does not see it. |
| 4, the pushed order on other wakes | Fixed | The `criteria`, `criterion_repair` and `unresolved` wakes raise `TypeError`, and the push skips a read that raises `TypeError`. The `term_collision` "gone" note stays. |
| 5, a casing variant | Not fixed | The probe still gives the note that the glossary holds no row for `Canonical_Order` and `Calendar`. No recorded ref has this form, so the finding stays low. |
| 6, the place of the new key | Fixed | The key now comes right after `criteria.load`. On `bg_1`, 1,892 characters come before it in the Developer prompt and 1,894 in the Tester prompt. Before pass 1c the counts were 2,533 and 2,828. |

### The new top-level file (high)

- Where: `rota/core/scheduler.py`, the prefix walk at the end of `grain_area`.
- CONFIRMED. On dry3, the root area `.` holds 186 index rows and has a survey record. `new_tool.py` maps to no area, so `unsurveyed_areas` reports an unknown grain. `constraints_for_grains` gives `k0`. `bound_constraints` gives `k0` with "this area has not been surveyed".
- The same happens to a new file in a directory that is not an area, for example `docs/new_page.md` or `newdir/x.py`. The prefix test `path.startswith(area + "/")` never matches `.`.
- Fix: let the area `.` hold every path in the prefix walk, so that `max` by length still picks a deeper area first. This is what `areas.area_of` does when it lands at the root.
