# The rulings seam, review of pass 1 at 624621eb

## Verdict

Pass 1 stands with two high findings. The record is write-once against UPDATE. Every writer of a `rulings` row stages its rows. The two call forms write the same rows. The back-fill gives the same answers as the parent. The 6 reds are red at 2c8e7e13 too. Two defects block a clean pass 1:

- The acknowledge path of `rulings.rule` now refuses a page with no numbered line when one of its refs is gone. The Liaison then has no call that it can make (finding 1).
- A keypress verdict on a ref that no table holds disappears from `ruled_refs`, `last_ruling_on` and `rulings_load`. No fault row records it (finding 2).

Counts: 2 high, 9 low (4 of the low are outside the points).

## (a) The points

1. The record: CONFIRMED, with one gap. No UPDATE or DELETE on `ruled_refs` exists in `rota/`. The view derives `status`, `confirmed_by` and `provenance`. `RULED_VERDICTS` holds `park` and `resume`. `ruled_ref_home` accepts `reading:<id>` when the message exists. The trigger refuses UPDATE only, so DELETE stays open (finding 5).
2. The one writer: CONFIRMED. These paths write `rulings`: `_stage_ruling` on both paths of `rulings_rule`, and `_insert_keypress_ruling` for `land` and `_land_shift`. The two testkit writers are `fixtures.py` 116, which back-fills, and `fixtures.py` 245, whose `per_item` is `{}`. `land`, `_land_shift` and `apply_rulings` only UPDATE the status. Every writer stages its rows.
3. The deviation on refusal: his verdict vanishes quietly from the new record. It stays only in `rulings.per_item` and in the `body_refs` of the verdict message (finding 2).
4. The two call forms: CONFIRMED. The object form and the `acts` form give equal staged writes, equal view rows and equal results. All 21 refusal texts of the parent `rulings_rule` are still in head. Head adds 5 refusals for `acts`. One refusal that the builder adds has no way out (finding 1).
5. The back-fill: CONFIRMED. A parent-schema database with one old row migrates at the `init_db` of head. `last_ruling_on` gives the same three answers as the parent. A value that is not a stored word loses its answer (finding 11).
6. The stale cases: the new sentences reach every landing prompt. They can change the call. The `.tools` sentences reach no prompt (finding 7).
7. The 6 suite reds: CONFIRMED. All 6 are red by name at 2c8e7e13 and at 624621eb.

## Point 1, the record

CONFIRMED by grep and by reading `rota/core/schema.sql` 688 to 778. The only UPDATE on `ruled_refs` is in `tests/rota/test_ruled_refs.py` 121, which expects the trigger to refuse it. `_apply_write` in `db.py` 535 to 547 turns a write on an id that is on file into an UPDATE. So a staged row that repeats an id aborts the whole commit. Ids hash a fresh `new_id("r")`, so no path repeats an id today. `confirmed_by` does not exclude a reading row inside the same ruling (finding 6).

## Point 2, the one writer

CONFIRMED by grep of `INSERT INTO rulings`, `INSERT OR IGNORE INTO rulings` and the staged `rulings` writes. `rota.tools.map table ruled_refs` names three writers: `backfill_ruled_refs`, `_stage_ruling` and `insert_ruling_rows`. No writer of a `rulings` row skips its rows.

## Point 3, the skipped ref

CONFIRMED by the probe `rv_probe.py p3` at the head and the parent. The probe lands a keypress `{s1, calculate_tip, l_1: approve, x_gone: contest}` on a page that names `x_gone`.

- Head: `rulings.per_item` holds `x_gone`. `ruled_refs` holds 3 rows and no `x_gone` row. `last_ruling_on("x_gone")` returns None. `rulings_load` rewrites `per_item` from the rows, so `x_gone` is gone there too. `faults` holds 0 rows.
- Parent: `last_ruling_on("x_gone")` returns the contest. `rulings_load` returns all 4 refs.

Fix: write a `faults` row for each skipped ref in `_insert_keypress_ruling`. Keep the `per_item` of the `rulings` row in `rulings_load`.

## Point 4, the two call forms

CONFIRMED by `rv_probe.py p4`. The reply rules 3 refs, and line 3 is a contest with act `remove`, target `how_it_works` and target kind `row`. The object form and the flat form give equal staged writes, equal `ruled_refs_live` rows and equal results. The `rulings` row equals the row of a plain verdict-word call. `rv_probe.py refusals` collects the string parts of each `raise` in `rulings_rule`. The parent has 21 refusals and the head has 26. No refusal of the parent is missing.

## Point 5, the back-fill

CONFIRMED by `rv_probe.py oldmake` at the parent schema, then `oldread` at the parent and at the head. The probe uses one row with `per_item {s_1: approve, c_1: contest}` and `texts {c_1: ...}`. Both trees return the same dicts for `s_1`, `c_1` and an unknown ref. The head back-fills 2 rows with the source `backfill` and `old_text` on `c_1`.

## Point 6, the stale cases

CONFIRMED by `rv_prompt.py`, which renders `prompts.compose("liaison", "landing")` at both trees. Every landing case shares this system text. The diff adds four sentences: two in `landing.base.md` and two in `landing.md`. So the prompt names the two forms twice, in different words. The sentences can change what the Liaison sends. They offer a new value shape and a new argument, with the literal example `app.py:518`. `mode_tools` and `mode_order` skip a line that starts with `#`. `mode_kinds` reads only its `# ledger.log kinds:` line. So the `.tools` sentences reach no prompt. I did not render the tool signature. The claim of the report that `acts=None` reaches the prompt stays PLAUSIBLE.

## Point 7, the suite reds

CONFIRMED. I ran the 6 named tests in `git archive 2c8e7e13` and in the worktree. Each tree failed the same 6 tests:

- `test_fixtures::test_no_case_leaves_a_reference_unwrapped`
- `test_invoke_door::test_a_session_with_no_batch_reads_the_root`
- `test_onboarding::test_the_same_constraint_written_twice_is_one_gate`
- `test_pins::test_with_prompt_keeps_every_pin`
- `test_roles_doc::test_a_verb_carries_words_or_does_not_regardless_of_recipient`
- `test_scene_two_batches::test_a_right_call_lands[the project test tests/test_templates.py as an encode]`

## (b) Findings

1. `rota/roles/api.py` 12613 to 12622, the acknowledge path. High. CONFIRMED by `rv_ack.py`. The page has no numbered line and a ref that no table holds. Head refuses `rulings={}` with "Rule the rows of the page", but the page numbers no row. The parent acknowledged the same page. The reach in a real night is PLAUSIBLE, because m191 of frame 316 shows a gone ref on a page. Fix: build the acknowledge rows with `unheld="skip"`, and write a fault for each skipped ref.
2. `rota/roles/principal.py` 2566 to 2584 and `rota/roles/api.py` 13070 to 13093. High. CONFIRMED by `rv_probe.py p3` (point 3). A keypress verdict on an unheld ref leaves no row and no fault. `rulings_load` also drops the ref from `per_item`. Fix: write one `faults` row for each skipped ref, and keep `rulings.per_item` in `rulings_load`.
3. `rota/roles/principal.py` 2576 to 2578. Low. CONFIRMED by reading `land` 2518 to 2523. `words_from` names the verdict message, and that message has no `body_text`. The words are in `config` `entry:<id>` and in `entries`. A span check in pass 3 then finds no span on any keypress. Fix: set `words_from` to null for a keypress, or name the entry that holds the words.
4. `rota/roles/principal.py` 862 to 866 (`ruling_rows`). Low. PLAUSIBLE. A verdict that is not a stored word raises even under `unheld="skip"`. So `land` raises after it inserted the verdict message. `cli.py` 862 to 863 sends only `approve` and `contest` today. Fix: skip the word under `unheld="skip"` and log it, as for a ref.
5. `rota/core/schema.sql`, the trigger `ruled_refs_never_change`. Low. CONFIRMED by reading. The trigger refuses UPDATE and permits DELETE. Fix: add a BEFORE DELETE trigger with the same message.
6. `rota/core/schema.sql`, the `confirmed_by` subquery of `ruled_refs_live`. Low. PLAUSIBLE. A row `reading:<its own reply>` inside the same ruling confirms that ruling. No pass-1 writer can stage that key, because `api.py` 12653 to 12692 refuses a key off the page. Fix: require `cr.id != r.id` and `cr.rowid > r.rowid` before pass 2 writes reading rows.
7. `rota/roles/prompts/liaison/landing.md` 14 to 15 and `landing.base.md` 12 to 13. Low. PLAUSIBLE. The landing prompt now has four sentences on two forms, with a literal target `app.py:518` that is on no page. A small model can copy that target into a contest, and pass 1 checks no target. Fix: say each form once, and measure the copy rate in the re-record of the 10 stale cases.
8. Outside. 18 test files insert a `rulings` row raw and call no back-fill, for example `test_agent_principal.py`, `test_frame193_pass2.py` and `test_frame329_staged_twin.py`. Low. CONFIRMED by grep. They stay green because their readers read `rulings`. A pass-2 reader of `ruled_refs` sees no rows there. Fix: add the test helper of question 3 of the report before pass 2.
9. Outside. `rota/testkit/fixtures.py` 115 to 123. Low. CONFIRMED by reading. A seeded verdict gets source `backfill` and provenance `reasoned`. A real keypress reads `keypress` and `decided`. Fix: seed the verdict rows through `ruling_rows` with source `keypress` and `unheld="skip"`.
10. Outside. `rota/tools/map.py`, the column parser. Low. CONFIRMED by `map table ruled_refs`. The parser lists `The`, `not`, `and`, `so` and `or` as columns. They are words of the `--` comments inside `CREATE TABLE`. Fix: strip `--` comments before the parser splits the columns.
11. Outside. `backfill_ruled_refs` in `rota/core/db.py`. Low. CONFIRMED by `test_ruled_refs.py` 290 to 306. An old value such as `later` gets no row. So `last_ruling_on` returns None where the parent returned the value. Fix: map the old words through `RULING_WORDS` and `SHIFT_WORDS` before the filter.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e03f97fc-cdd4-4daa-864c-2ca4d7ef42a5/scratchpad/`. Each one runs with the tree as the working directory, and puts that tree first on `sys.path`.

- `rv_parent/`: `git archive 2c8e7e13`, the parent tree.
- `rv_probe.py p4`: the object form, the flat form and plain verdict words on one reply with three refs. The probe compares the writes, the view rows and the results.
- `rv_probe.py refusals`: the refusal texts of `rulings_rule` in each tree, in `rv_ref_head.json` and `rv_ref_parent.json`.
- `rv_probe.py p3`: a keypress verdict with one unheld ref, at the head and the parent.
- `rv_probe.py oldmake` and `oldread`: one old-shaped `rulings` row, made at the parent schema. The probe reads it at the parent, then migrates it at the head.
- `rv_ack.py`: the acknowledge path on a page with no numbered line and a gone ref, at both trees.
- `rv_prompt.py`: the landing prompt and its tool list at both trees, in `rv_prompt_head.txt` and `rv_prompt_parent.txt`.
- pytest: the 6 named reds, in `rv_parent/` and in `C:/Users/roman/rota_rseam`.

## (d) Usage

- Input tokens: about 100k, an estimate from the budget counter. The cap was about 60k, and the review went over it.
- Output tokens: about 15k, an estimate.
- Total: about 115k.
