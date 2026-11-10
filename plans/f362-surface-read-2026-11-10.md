# The read before a fix: D9-1 with D9-2 and D9-6, 2026-11-10

The read was done on rota at `db3cf81a`, against the dry run 9 database opened read-only (`scratchpad/dry9/runs/dry9.db` of session c1a39439). No code changed. The brief is `scratchpad/f362/surface_read_brief.md`.

## Result

1. The reach is 21 doors and pages: 8 for the surface, 6 for the touch, 7 for the stop (section 8).
2. The index holds the real function. `code_index` has the row `src/icalendar/parser/string.py::_foldline`, `grain_kind` `symbol`, `sym_kind` `function`, lines 118 to 156 (observed: `dry9.db`). `commitment_candidates` holds 4 rows with `symbol` `_foldline`, one on line 122 that names the 75-octet limit (observed: `dry9.db`).
3. Surface: two readers miss the row. `_word_hits` matches whole words only, so `_foldline` is one word, `foldline`, and the push to s154 held 0 program rows (observed: `api.py:22307-22325`, s154 turn 1). `_vet_surface` then saw no neighbour, because the fuzzy ratio of `fold_long_lines` to `_foldline` is 0.667 and the cutoff is 0.75, so it kept the name as greenfield (observed: `api.py:6824-6857`, my run of `difflib`).
4. Touch: his 30 exclude rows sit on the ref `guess:folds_long_lines`. `batches.guess` reads no exclude row, and `predicted_rows` reads the exclude rows of the batch ref only (observed: `api.py:9172-9285`, `lifecycle.py:531-567`).
5. Stop: a stop row exists, `item_parks`, and 7 predicates read it through `not_parked`. Only the shift page writes it. The park page's "ok" writes no row, and `criterion_owed` does not read it (observed: section 7).
6. The smallest general fix is three row reads, about 13 cycles (section 9). It closes none of frames 172, 155 and 166. It closes the D9-2 repeat of W11, part of the root read's W12, and none of W16 (section 10).

## 1. The index of symbols (question 1)

- Onboarding writes `code_index`: `grain`, `grain_kind` (path, symbol, table, route, variable, export), `area`, `fan_in`, `sym_kind`, `content_hash`, `line_start`, `line_end` (observed: `rota/core/schema.sql:504-526`).
- The run's index holds 1472 symbol rows, 694 path rows, 367 variable rows and 261 export rows (observed: `dry9.db`). `_foldline` has a symbol row in `string.py`, and two export rows, `parser/__init__.py::_foldline` and `parser/string.py::foldline` (observed: `dry9.db`).
- The index holds no `fold_long_lines` row at the end of the run (observed: `dry9.db`). The row I read is the end state. That the row was there after onboarding is reasoned: the main checkout did not change.
- `code_lexicon` holds 403 rows and no word that starts with `fold` (observed: `dry9.db`).

## 2. `criteria.specify` (question 2)

The door is `criteria_specify`, `api.py:7356-7557`. It checks the ticket, the woken item, the id, the twin, the cap of six, and then the surface at lines 7538-7539 (observed):

```
    _surface_names_what_the_item_names(ctx, ticket_id, surface_refs)
    surface = _vet_surface(ctx, surface_refs, required=False, ticket_id=ticket_id)
```

What it validates about `surface_refs` (observed: `api.py:6751-6858`, `7122-7192`):

- A ref the index holds is resolved to its grain. A test or an attached twin is refused.
- An unknown ref with a fuzzy neighbour at cutoff 0.75 is refused with the neighbours named (`api.py:6824-6834`).
- When the item names a new callable, the surface must name it, and a bare invented name is refused (`api.py:7166-7183`).

What it does not validate (observed, with the reason in brackets reasoned):

- An unknown ref with no neighbour is kept. Lines 6846-6850 hold the refusal for the repair door only: `if required and ticket_id and bare not in given and not in_tree:`. At specify `required` is False.
- When the item names no new callable, `_surface_names_what_the_item_names` returns at line 7128, before the invented-name check. The item `folds_long_lines` gives no name in a callable form, so it returned (reasoned: `callables_in`, `api.py:7068-7119`).
- No reader splits `_foldline` into `fold` and `line`. `difflib` compares whole strings, and `_word_hits` compares whole words.

## 3. The respecify door (question 3)

- The text "The surface is a callable in a file the batch expects to touch" is the `Wall` of `_surface_outside_batch`, `api.py:6919-6924` (observed). `criteria_respecify` calls it at lines 8401 and 8545, after `_vet_surface(required=True)` (observed).
- It reads `predicted_rows` for every live batch of the ticket, and takes the path rows as the touch set (observed: `api.py:6880-6893`).
- It binds the surface to the touch set by design. Frame 215 refused a surface in an unexpected file that the sandbox could not import (observed: the docstring, `api.py:6862-6878`).
- The touch set held `property.py` because `predicted_rows` drops only the paths that his ruling on the batch ref excludes (observed: `lifecycle.py:563-567`). His 30 excludes are on `guess:folds_long_lines`, so none applied (observed: `ruled_refs` r_m24). s195 sent `fuzzing/ical_fuzzer.py::TestOne` and was refused there (observed: `tool_calls`).

## 4. The commit door (question 4)

- The text is in `code_commit`, `api.py:27448-27506` (observed). It reads `criteria.surface_refs` of the batch. A bare name must have a definer by `definers_of` with the worktree. A `path::name` ref must be a top-level def or class in that file (observed).
- The door reads the tree, not the index. If the surface were `src/icalendar/parser/string.py::_foldline`, the file exists and its top level defines `_foldline`, so the door says nothing and the commit passes (reasoned: the AST read of lines 27486-27497).

## 5. The encode door (question 5)

- "does not define": `tests_encode`, `api.py:12842` and `12855` (observed). Line 12855 ends "Nothing in the tree defines it yet; the Developer writes it first" when no file defines the name (observed: lines 12853-12858). This text sends the team to build the made name.
- "this test never calls": `api.py:12907-12913` (observed). It compares the body's calls with `_surface_call_names` of the stored ref, so a test of `_foldline` fails it (reasoned).

## 6. The touch guess rewrite (question 6)

- The door is `batches_guess`, `api.py:9172-9285` (observed). The Architect s149 called it five times on relay m27 (observed: `tool_calls`).
- It reads `owed_ruling` to stamp `ruling_id` (the stored value is `m26`), and `_refuse_the_contested_set` (observed: `api.py:9255-9256`, `9337-9352`, `touch_guesses`).
- `_refuse_the_contested_set` refuses only a set equal to the contested set. It reads no `ruled_refs` row with act `exclude` (observed: `api.py:9349`).
- So the set `property.py`, `test_common_functionality.py`, `test_split_on_unescaped_semicolon.py` passed. It is not equal to the 30-path set, and two of its paths are excluded (observed: `touch_guesses`, `ruled_refs` r_m24).
- s149's prompt listed `property.py` under `disputed` (observed: s149 turn 1). The seat saw the exclude, and the door did not hold it.
- `batches_annotate`, `api.py:9287-9334`, has the same reads (observed).

## 7. The park (question 7)

- The park page ends "Reply 'ok' if every line says what you want. The team then stops here and tells you." (observed: `principal.py:2842-2843`).
- An "ok" that approves the page whole sets the verdict `answered`, so no Liaison wakes on it (observed: `principal.py:4318-4334`). No other row is written. r_m63 holds 9 `approve` rows with no act (observed: `ruled_refs`).
- `item_parks` is the stop row: `kind` park, now, drop or resume (observed: `schema.sql:949-959`). Only `_land_shift` writes it, and `by` admits only `shift` and `request` (observed: `principal.py:4674-4730`, `schema.sql:955`). The table is empty in this run (observed: `dry9.db`).
- `not_parked` is read by 7 of 50 predicates: contested, guess, grouping, touch_note, preempt, quarantined and park_ask. `tick_slicing`, `tick_criteria` and `next_batch` read it too (observed: my scan of `predicates.py`, `scheduler.py:407`, `451`, `2178`).
- `criterion_owed` does not read it (observed: `predicates.py:1759-1776`). `scheduler.criterion_owed` stops only for an item with `approval` `dropped` (observed: `scheduler.py:2105-2135`).
- Turn 7 started from m64's contest. s209 rewrote the batch touch under m66. Then 12 Terminologist sessions woke on `tick:criterion_owed`, and their answers woke 11 Testers and 3 Developers by message (observed: `sessions`, `messages` m68 to m81). `open_tips` reads no park row (observed: `scheduler.py:63-127`).

## 8. The reach

Surface: a door or page that accepts or prints a surface name and does not check it against the index's program symbols.

1. `api.py:22307` `_word_hits`, the push of `code.callables` and `model.shape`: whole words only, 0 program rows for s154 (observed).
2. `api.py:6828-6834` `_vet_surface`: neighbours by `difflib` at 0.75 only (observed).
3. `api.py:6846-6857` `_vet_surface`: keeps a name with no neighbour when `required` is False (observed).
4. `api.py:7128` `_surface_names_what_the_item_names`: returns before the invented check (observed).
5. `api.py:6850` the respecify check: `in_tree` counts a definition the batch wrote. Why `property.py::fold_long_lines` passed it is not read (reasoned).
6. `api.py:12853-12858` the encode import door: "the Developer writes it first" (observed).
7. `api.py:12907-12913` the encode never-calls door: holds the test to the stored name (observed).
8. `api.py:27500-27505` the commit door: "Define it in the file named" (observed).

Touch: a door or page that accepts or prints a touch path and does not read the exclude rows of both refs of the code line.

1. `api.py:9172` `batches.guess`: equal set only (observed).
2. `api.py:9287` `batches.annotate`: equal set only (observed).
3. `lifecycle.py:531-567` `predicted_rows`: the batch ref only (observed).
4. `api.py:6861-6924` `_surface_outside_batch`: reads item 3 (observed).
5. `runner.py:816-826` `_line_legend`: one exclude row per ref, 1 of 30 printed (observed: code, `turns` of s159).
6. `principal.py:2292-2326` `code_line` and `lifecycle.py:666` `touch_set`: print the Architect's rows by ruling P4 (observed: the docstring at `lifecycle.py:550-551`).

Stop: a door or predicate that acts on a parked batch and does not read a stop row.

1. `principal.py:4327-4334` the whole-page "ok": writes no `item_parks` row (observed).
2. `schema.sql:955` the `by` check: no value for a park page (observed).
3. `principal.py:1362` `RULED_ACTS`: no stop act, so "stop here" landed as a contest (observed: r_m64).
4. `predicates.py:1759-1776` `criterion_owed`: no `not_parked` (observed).
5. `scheduler.py:2105-2135` `scheduler.criterion_owed`: `dropped` only (observed).
6. `scheduler.py:63-127` `open_tips`: no park read (observed).
7. `api.py:25407` `code.write`: no batch status read. s223, s226 and s233 wrote on the deferred bg_1 (observed: the door, the dry run 9 read D9-6).

The reach is 21 (reasoned: the three lists).

## 9. The fix shape

Each part is a row read. No part changes a prompt.

1. **Surface.** `_word_hits` also matches a hint word inside a name with its underscores removed, ranks by the count of words hit, and keeps the program first. On this index the words of `fold_long_lines` then give `Contentlines` and `_foldline` at 2 hits each (observed: my run, with "program" read as "not under `/tests/`"). `_vet_surface` reads the same function for an unknown ref. A program row that it returns counts as a neighbour, and the refusal of line 6834 names it, unless `item_callables(...).new` gives the name. The doors at 12855 and 27502 read the same neighbours and route to `msg.question_terminologist` in place of "the Developer writes it first". Price: about 3 cycles for the reader and the door, and 2 for the two texts.
2. **Touch.** `predicted_rows` reads `disputed_paths` on the batch ref and on `guess:<item>`. `owed` already reads those two refs as one fact (observed: `scheduler.py:1883-1886`). `batches.guess` and `batches.annotate` refuse a path that `granted(..., "exclude", path)` holds on either ref, and quote his words, beside `_refuse_the_contested_set`. `_line_legend` prints the count and the paths of the exclude rows. Price: about 3 cycles for the readers and the doors, and 2 for the legend.
3. **Stop.** The whole-page "ok" of a park page writes one `item_parks` row of kind `park` through `_write_park`. `by` gets a third value for it. `scheduler.criterion_owed` adds `not_parked`, so the chain of turn 7 has no source. A resume stays the shift page or a new request, as today. Price: about 3 cycles. A `stop` act for "stop here" on another page is a seam design of 8 to 10 cycles, and it is outside this fix.

The total is about 13 cycles, by the anchors of `plans/operating-facts.md:252`: a door text 2, an instrument fix 3, a seam design 8 to 10, a count on a night 0.

The counts for dry run 10:

- Surface: live criteria whose surface the index does not hold and the request does not give. Dry run 9: 3 of 4 at the stop, cr_1, cr_2 and cr_6 (observed: `criteria`). Target 0. A second count: commits that define a made surface name, 2 (214065e4, 830d178e), target 0.
- Touch: rows of `touch_guesses` or `batch_touch` on a path his exclude rows name. Dry run 9: 2 of 3 in the m26 set (observed). Target 0.
- Stop: seat sessions after a park page approved whole. Dry run 9: 31. Target: the Liaison landings and one relay Architect, 5 on this run's chain (reasoned: s206 to s209 and s236 against section 7). Dry run 10 may reach no park, and then the count is not taken.

## 10. The match to frames and unbuilt solutions

- 172, "its tests never take that path", matches D9-8 and not this fix. It stays open (observed: `stack.md:3341`).
- 155, the keyword quoter, and 166, the not-Python door, match D9-12 in part. This fix closes neither (observed: `stack.md:3384`, `3479`).
- W11 of dry run 8, the first guess without `string.py`: part 2 closes its D9-2 repeat, where the exclude rows were skipped. Part 1 also puts `_foldline` in the guess push, because the guess wake reads `code.callables` (observed: `runner.py:5096-5106`).
- W12: in the dry run 8 read, W12 is the rest line, which is D9-11, and this fix does not touch it (observed: `dry8-read-2026-11-08.md:88`). The root read's W12 is the guess by word match. Part 1 closes the word-match half (observed: `walls-root-read-2026-11-08.md:26`).
- W16, the silent approve: not closed. Part 3 reads the whole-page approve as a stop and does not change the meaning of a silent line (reasoned).
- D9-6 has no frame. Part 3 is new.

## 11. What contradicts the dry run 9 read

1. D9-1 says s154's prompt holds `_foldline` in a list of test grains. The prompt holds no `_foldline` row. The only match is inside `test_foldline_does_not_split_...`, and the list has 0 program rows and 15 attached rows (observed: s154 turn 1).
2. D9-6 and section 3 put the stop under R1, a fact with no row. The row and 7 predicate readers exist. The writer at the park page is missing, and `criterion_owed` skips the row, so the stop is R1 at the writer and R2 at the reader (observed: section 7).
3. D9-2 names "root read W12" as seen before. That W12 is not the W12 of the dry run 8 read, which is the rest line (observed: section 10).

## 12. Doubts

- The substring neighbour can refuse a true new name that holds the words of an old one. The exemption covers only a name the request gives in a callable form (reasoned: `callables_in`).
- DECISIONS records "a name with no neighbour is greenfield intent and kept" (observed: `DECISIONS.md:1056-1062`). Part 1 widens "neighbour" and keeps that rule. If the session reads the change as a departure, Roman gets the question first, by the memory `rota-provenance-before-a-fix`.
- I read "program" as "not under `/tests/`" in my count, not by `kind_of` (reasoned).
- Why respecify admitted `property.py::fold_long_lines` is not read. An index refresh after 830d178e is a guess (reasoned).
- After a park row, a later correction of his on the item wakes no owner, because `contested` reads `not_parked`. That is the stop he asked for, but the resume path needs a sentence on the page (reasoned).

## 13. The decision of the holding session (c1a39439, rota-f8)

1. Part 1 does not go in by word match. A match of a hint word inside a name fits `fold_long_lines` against `_foldline` and not the next made name (reasoned: the overfit refusal, Roman, 2026-10-15). The row that decides is already read in two places: the index holds no such symbol, and `item_callables(...).new` gives no new name for the item (observed: section 2, lines 6846 to 6850 and 7166 to 7183). The fix joins the two reads at specify: a surface the index does not hold, on an item that names no new callable, is refused. The refusal names the exit, name a symbol the index holds or name the new callable in the item, and lists the word-hit candidates of the index as help, program rows first. The encode door and the commit door route the same case to the Terminologist, never to "Define it in the file named".
2. The greenfield rule of `rota/DECISIONS.md` line 1056 is a build record of 2026-08-26, the session's design, and no ruling of Roman. Its exit, a new feature names its entry point, was built later as the item's new callable (observed: lines 7166 to 7183). The test `test_a_name_with_no_neighbour_is_a_design_not_a_typo` moves to that exit: the item names the new callable, and the surface lands. The record gets an amendment line.
3. Parts 2 and 3 go in as the page gives them. The `stop` act on other pages is a seam design and stays out.
