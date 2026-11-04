# Frame 362, design review of the shape layer page

Verdict: revise. The four facts are cheap and mechanical, and their counts hold on the pinned commits. Three high findings remain. The named consult instrument cannot see the new read. The guess reader has no build step. The harvester does not run again after a merge.

The review read `plans/design-onboarding-shape-2026-11-04.md` at `8e0d621c` in `D:/repos/rota`, read-only. HEAD is `6ae1e90a`, one docs commit later, and no file under `rota/` changed between the two commits.

## (a) The verdict on each point

1. Stands. CONFIRMED. On the pinned trees, every fact count is the same as on the dive's trees. Only line numbers, grain totals and one similarity change. No conclusion of the page changes.
2. Stands, with one low finding. CONFIRMED. No call edge exists today. The re-export follow is new logic for a new table, not a change to `code_edges`. Law 1 holds: `indexer.build` is the only writer. See finding 10.
3. Partly. The push meets the push rule, because the batch comes from the wake (CONFIRMED). `model.shape(name)` carries a weaker form of the `model.load` fault (PLAUSIBLE). See finding 8.
4. Three traps hold (T3, C3, I2), two hold partly (T2, C4), and one does not hold (I1). See findings 2 and 4.
5. Revise. CONFIRMED. The gain of 2 comes from Q5 and Q8. Both read records that exist today, and no new fact is needed. `probes/consult.py` does not read `model.shape`, so the named instrument shows no gain. See finding 1.
6. Revise. The number is reasoned and has no unit. A dry run can score it after a definition. See finding 5.
7. Revise. The page states no drop rule and no threshold. Build the boundaries and `code_calls` first. Do not build the variant kind yet. See finding 6.
8. Partly. The 1.3 seconds is measured on the probe. The cycles use line 250 and the 1.6 rate. Step 3 and step 5 are priced too low, and two wires have no price. The measures come after every build. See findings 3, 6 and 7.

### Point 1 in detail

The pinned commits are descendants of the dive's trees. Each pin adds 3 commits of rota's own deliveries (observed: `git merge-base --is-ancestor` and `git log` in `D:/repos/_AI/sample_repos`). The diffs are small: tips 5 files, click 4, icalendar 4.

| Repository | Changed on the pin | Same on the pin |
|---|---|---|
| tips | grains 20 to 29; py files 3 to 6; `calculate_tip` similarity 0.77 to 0.88; `display_results` at `main.py:6` and `tip_calculator.py:13`, not 4 and 11 | 2 copy pairs, 0 helpers, 0 groups, 1 guard, 1 README run line |
| click | grains 1,182 to 1,188; py files 79 to 82 | 1 pair, 54 targets, 13 helpers, 10 variant groups, 65 exports |
| icalendar | grains 2,794 to 2,800; py files 258 to 261 | 3 pairs, 65 targets, 34 helpers, 15 by area, 1 unit group, 31 variant groups, 84 exports, 1 script, 4 guards |

The trap facts are present on the pins: `CompletionItem` with 2 caller files, `format_completion` over 4 shells, `to_info_dict` of `Option` and `Argument`, and `get_duration_property` with 2 caller files (observed: `traps.py`). The pinned line numbers now match the blind test page. The page's `main.py:4` does not match.

## (b) Findings

1. **The consult instrument does not read the new door (high).**
   - Where: `probes/consult.py` 44 to 57 and 128 to 140. The page, section 4.1, line 142, and section 6, step 6.
   - CONFIRMED by a read. The Architect's artefact in `consult.py` is `model_areas` and `constraints` only. The probe calls no `.tools` read, so a new line in `architect/ask.tools` cannot change its score.
   - The two whole answers do not need the new facts. Q5 reads the `export` grains, which the indexer writes today. Q8 reads the `metadata` script candidate, which the harvester writes today (observed: harvest.py 12 to 13, 503 to 506). Copies, `code_calls` and variant groups add no point on the consult set.
   - The gain is a record gain, not a code read. The Architect's `ask` holds no code read (observed: `ask.tools`).
   - Fix: extend `consult.py` with a shape section by the question's names, or score through the live ask route. Credit the gain to a door over existing records.

2. **The guess reader has no build step (high).**
   - Where: the page, section 3.1, line 53, against section 3.5 and section 6, lines 184 to 191.
   - CONFIRMED by a read. Section 3.1 names the Architect at the guess as a reader. Section 3.5 and the build order hold no door and no step for the guess. `code.callables` stays unchanged.
   - T2 and T3 are place traps. The guess decides the place. The shape push reaches the Developer at `batch_start`, after the guess wrote the touch. The Developer can only stray, through `touch_strayed`.
   - The Critic at `review` does see the diff and the copy push, so T3 keeps a reader there.
   - Fix: add a step that marks copies and their entry-point reach in `code.callables`, priced 2. Else remove the guess from Readers and score T2 as partly.

3. **The harvester does not run again after a merge (high).**
   - Where: `rota/onboarding/boot.py` 119, the one caller of `harvest.record`. `rota/onboarding/indexer.py` `refresh`, 615 onwards. The page, section 5, line 178.
   - CONFIRMED by a grep. Only `boot.py` calls `harvest.record`. `indexer.refresh(main=True)` rebuilds the index and repins, and calls no harvest.
   - So after the first merge, `code_calls` describes the new commit. The `variant`, `entry_point` and `intake` rows describe the onboarding commit. The push quotes member lines that are now wrong.
   - Fix: call `harvest.record` in `refresh(main=True)` after `build`, in step 3, and price it.

4. **I1 is not a shape credit (low).**
   - Where: the page, section 4.2, line 157.
   - PLAUSIBLE. The unit group is the pass 1 harvester row (observed: harvest.py 393 to 427). The commitment push of pass 2 reads it, not the shape door.
   - I1 is a "tests pass before code" task. The right outcome is "already done", and that decision falls before a batch exists. A push at `batch_start` arrives late.
   - The group can push toward the trap. The docs line says "75 characters", and the request is about letters.
   - Fix: move I1 to the commitment layer's count. Push the code side, `string.py` 122, as the binding fact.

5. **The operation number has no unit (low).**
   - Where: the page, section 1, line 13.
   - CONFIRMED by a read. The number is reasoned from the length of the push. The baseline of `plans/onboarding-demand-read-2026-11-03.md` section 2 counts sessions, "Did a row change the act?", not acts.
   - The count a dry run read takes. The denominator is the `tool_calls` rows with a writing `fn` of the Developer, Tester and Critic sessions on the batch. The numerator is the rows whose `args_summary`, or the `turns.completion` of that turn, names an id or a grain of the pushed constraint key or shape key in the `turns.user` of that session.
   - Fix: state the definition on the page. Predict the number for a touch that hits a shape fact, such as I2 or T3, and not the fold.

6. **No drop rule, and the measure follows the build (low).**
   - Where: the page, section 7, line 197, and section 6, steps 1 to 6.
   - CONFIRMED by a read. Copies "stays" at 0 of 3 true on icalendar. Variant groups stay at 3 of 10. No threshold is stated before a measure. Every fact is built in steps 1 to 5, and the only measures are in step 6.
   - On the evidence, build first: `entry_point` and `intake`, which serve the landing and change-log checks of every task; `code_calls`, true 6 to 8 of 10, which also gives the caller rule its rank 1; and copies as a free query.
   - Not yet: the variant kind. It is 3 of 10 true on icalendar, it needs a cap, and it widens the meaning of `contradicts`. A touch of `cal/event.py` pushes 9 lines, and `new` and `example` are noise (observed: `pushsize.py`).
   - Fix: write a keep rule per fact before step 1, for example "kept when 6 of 10 true and one trap task changes". Run the consult and I2 and T3 after steps 1 and 5, before the variant kind.

7. **Step 3 is priced too low (low).**
   - Where: the page, section 6, step 3; `rota/core/db.py` 427 to 429; schema.sql 274 to 278.
   - CONFIRMED by a probe and a read. `init_db` on a copy of the dive's `ical.db` refuses `variant`, `entry_point` and `intake` by the CHECK. `init_db` widens three tables only, and `commitment_candidates` is not one of them.
   - The id is `cc_` plus a hash of the kind, the path, the line and the text. A script row that moves from `metadata` to `entry_point` gets a new id, and the old row goes stale. The `bind` branch at harvest.py 503 keys on `metadata` and must move too.
   - Step 5 is a new op with a body and a `.tools` line, not a door text.
   - Fix: price step 3 at 5 to 6 with a `_widen_candidate_kinds`, and step 5 at 3.

8. **`model.shape(name)` needs a name the seat may not have (low).**
   - Where: the page, section 3.5, item 2; `rota/roles/prompts/architect/ask.tools`.
   - PLAUSIBLE. `model.load` failed because the seat never saw an id. A code name is better, because a question often holds one. But the `ask` of the Architect has no code read to find a name it lacks.
   - Q7 uses everyday words. Its variant groups are keyed as `TZProvider.create_timezone` and siblings (observed: `out/pin_ical.json`). Q5 names `from_ical`, a method, and methods are not in `code_index`.
   - The page does not state the match rule. The page also calls the `PYTZ` and `ZONEINFO` groups noise in 3.3 and uses them for Q7 in 4.1.
   - Fix: state the match as the word match of `code.callables` over grain names, export names and the class-dot-method form. Return every hit.

9. **The call count of the copy row is empty on tips (low).**
   - Where: the page, section 3.1, line 39; the `helpers` function of the probe, which skips a call when the target file is the caller file.
   - CONFIRMED by a probe. On the pinned tips, `code_calls` as probed holds 0 rows. `main.py` calls its own copy inside `main.py`, and the tests are kept apart as attached files.
   - So "the call count of each side" is 0 and 0, and it cannot tell the live copy from the dead one. The entry-point join does tell them apart.
   - Fix: write same-file calls and test calls with a flag column, or drop the call count from the copy row.

10. **A third resolver of re-exports (low).**
    - Where: `rota/onboarding/indexer.py` 214, `resolve`; `rota/onboarding/harvest.py` 467, `_reexported`; `Resolver.define` in the probe.
    - PLAUSIBLE. The indexer resolves imports one way, and the harvester resolves re-exports another way. The design adds a third resolver, written on the Python `ast`, inside an indexer that parses with tree-sitter. Three resolvers can disagree on one package.
    - Fix: put the call resolver beside `_reexported` on `harvest.Tree`, and share one module map with the binding rule.

Outside the points: findings 3, 9 and 10.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/535a30c6-b4f1-4ae7-85bc-11d741145722/scratchpad/rshape/`. Each ran with `D:/repos/rota/.venv/Scripts/python.exe -I`, with the repository root first on `sys.path`.

- `src/tips`, `src/click`, `src/ical`: `git archive` of tipsI `ff1f65f`, clickI `09c82f3` and icalendarI `4f12af1e`.
- `db/<repo>.db`: the `reindex.py` of the dive on each pinned tree. Grains 29, 1,188 and 2,800.
- `out/pin_<repo>.json` and `out/dive_<repo>.json`: the `shape.py` of the page on the pinned trees, and again on the trees of the dive. The icalendar total was 1.50 and 1.56 seconds.
- `cmp.py`: the fact sets compared, dive against pin.
- `traps.py`: the rows behind C3, C4, I1 and I2 on the pins.
- `variant.py`: the variant groups checked per class. Getter and setter pairs in one class do not inflate the count. 10 of 10 click groups and 31 of 31 icalendar groups hold.
- `pushsize.py`: the shape push per touched file on icalendar. `cal/component.py` gives 14 lines and 1,787 characters. `cal/event.py` gives 9 lines, and `attr.py` gives 11 lines.
- `widen.py`: `init_db` on a copy of the `ical.db` of the dive, then an insert of each new kind. The CHECK refuses all three.

## (d) Usage

About 100k input tokens, about 14k output tokens, about 114k in total, estimated by the agent. The harness line was not visible. The cap of the brief was about 60k. About 45 tool calls ran. No model session, gate or sub-agent ran. The review wrote one file in the repository, this page, untracked.
