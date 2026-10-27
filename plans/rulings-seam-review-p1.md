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

## Pass 2

Pass 2 at c4a51c7d stands. Both high findings of pass 1 are fixed. The red tests of frames 338, 337 and 322 are red at 624621eb and green at c4a51c7d. s281 stays refused. The frame 315 test change is right. The briefs and the call forms do not change. Two reasons of the implementer do not hold as written, and one pass-2 reader is left with no reason. None of the three blocks the pass. Counts: 0 high, 4 low.

I did not create the worktree `C:/Users/roman/rota_rseam2`. The review rules allow no git write, and `git archive` gives the same trees read-only. So no worktree needs removal. The trees are `p2_head` (c4a51c7d), `p2_base` (624621eb) and `p2_mix` (the tests of c4a51c7d over the `rota/` of 624621eb), all in the scratchpad.

### Pass 2, the points

1. The two high findings: FIXED, CONFIRMED by `rv_ack.py`, `rv_ack2.py` and `rv_probe.py p3` on `p2_head`. The acknowledge path lands `{b_1, x_gone: approve}` and `{x_gone: approve}`, and it stages one `faults` row for each gone ref. The keypress on `x_gone` writes one open `faults` row with the author `system` and the call `principal.land`. `rulings_load` returns all 4 refs again. `render_state` and the cockpit `snapshot` read `faults`, so the fault is visible to him. `last_ruling_on("x_gone")` still returns None, and the fault text is now the only record of that verdict. `rv_probe.py p4` stays equal for the object form and the flat form.
2. The F1 readers: 14 functions of design 3.1 now read the view, and 2 are deleted. These read the view: `last_ruling_on`, `term_collision`, `_line_legend`, `contests_on`, `park_ruling`, `_confirm_landed`, `_reply_sentence_fault`, `_landed_approval`, `rulings_load`, `_ruling_texts`, `contested_statement` and `chain_verdict`. `_retired_carry` gives its words to the new `_item_ruled`, which reads the view. `_assert_words_fault` reads the view through `_reply_sentence_fault`, and no reader reads `act` yet. `ruled_clarify_criteria` and `ruled_test_criteria` are deleted. Six functions still read `rulings` or a map by their own rule:
   - `_words_on_rows`: the reason holds. A flat-form row and a back-filled row carry the whole reply as `words`, as pass 1 probe p4 showed.
   - `_ruling_order`: the reason holds. A back-filled row has `line` null, so the rows cannot give the order of an old page.
   - `land`: the reason holds. Design 3.5 puts the re-checks of `land` in pass 3.
   - `_land_shift`: the reason holds. It reads the keypress map that it gets, and no stored ruling.
   - `apply_rulings`: the reason holds. `rv_ack.py` shows a ruling with a ref that has no row, so a map built from the rows loses that verdict.
   - `verdict_rows`: the stated reason does not hold (finding P2-1). The function itself must stay.
   - `_resolve_contest` is the seventh. Design 3.5 row 2 names it for pass 2. It still scans the `verdict:` maps in `config`, and the report gives no reason (finding P2-2).
3. Frames 338, 337 and 322: CONFIRMED. `p2_mix` gives 7 failed and 115 passed on `test_frame338_test_row_relay`, `test_frame337_earlier_answers`, `test_frame315_carry`, `test_ruled_refs` and `test_frame234_verdict_lines`. The 7 reds are the 2 tests of frame 338, the 1 of frame 337, the 2 of frame 315 and 322, and the 2 high tests. `p2_head` gives 122 passed. `rv_s281.py` runs s281 through the door at both trees with four earlier answers: none, "Lines 5 to 11 are fine.", "Lines 5 to 11 are wrong." and both sentences. All 8 calls are refused, and each tree gives the same refusal text.
4. The frame 315 test: right, and not weakened. The old assertion pinned the defect of frame 322: s185 got no ruled words because the item had no old ticket. Proposal line 2 of frame 322 asks for `RULED_KEY` on every generation. The new test asserts the exact list `[M118, M137]` and an item key set with no `RETIRED_KEY`. So it pins the new rule and the rule of frame 315 that no old criteria appear.
5. Casestatus: the briefs and the call forms are unchanged, CONFIRMED. The diff touches no file under `rota/roles/prompts/`. No `@op` signature changes. `rv_tools.py` renders the tool signatures of four modes at both trees, and the outputs are byte-equal. I did not run casestatus again, because the brief forbids a touch of `cassettes.db`. The pushed working set does change on paths that no recorded case renders (finding P2-3).

### Pass 2, the findings

- P2-1. `rota/core/scheduler.py` 1961 (`verdict_rows`). Low. CONFIRMED by reading `land` 2530 to 2562 of 624621eb. The report says that a relay can run before the keypress `rulings` row exists. `land` writes the `verdict:` map and the keypress row in one transaction, so the claim is false in production. The function must stay for another reason. The map in `config` is the map after `land` filters it, and `land` turns `guess:<item>` keys into batch ids. The Liaison rows hold the map before that filter. Fix: write that reason in the docstring of `verdict_rows`.
- P2-2. `rota/core/runner.py` 2685 (`_resolve_contest`). Low. CONFIRMED by reading. Design 3.5 row 2 names this function for pass 2. It still scans every `verdict:` map with `LIKE`, by its own rule, and the report does not name it. Fix: read the newest landed contest or revise row on `item` from `ruled_refs_live`, or record why it stays.
- P2-3. `rota/core/runner.py` `_item_ruled`, and `rota/core/sandbox.py` the relay split. Low. PLAUSIBLE. The criteria and slicing pushes now carry `RULED_KEY` on a first generation. A converse reply now keys `criterion_repair`, and the relay refuses an approve-only relay. These changes alter the prompt or the next turn on paths that no recorded case renders, so casestatus cannot show them. Fix: record one criteria case with a first generation and one converse relay case before the night that tests the pass.
- P2-4. `rota/roles/api.py` `rulings_rule`, `from_earlier`. Low. PLAUSIBLE. At 624621eb, an earlier answer that named a line excused every contest on that line. Now only a contest row whose words came from the earlier fill is excused. An object-form contest that carries its own `words` is now refused on a line named only in an earlier answer. No recorded call uses the object form. Fix: excuse a line that an earlier answer names whatever the shape holds, or test the object form on the m76 and m78 shape.

### Pass 2, the probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e03f97fc-cdd4-4daa-864c-2ca4d7ef42a5/scratchpad/`.

- `rv_ack.py`, `rv_ack2.py` and `rv_probe.py p3` and `p4` on `p2_head`: the two high paths, the fault rows and the two call forms.
- pytest on `p2_mix` and `p2_head`: the red tests of frames 338, 337, 315 and 322, the high tests and the s281 tests.
- `rv_s281.py` on `p2_base` and `p2_head`: s281 through the door with four earlier answers.
- `rv_tools.py` on `p2_base` and `p2_head`: the tool signatures of four modes, in `rv_tools_base.txt` and `rv_tools_head.txt`.
- A static pass over the functions of design 3.1 in `p2_head`: what each one reads.

### Pass 2, usage

- Input tokens: about 38k, an estimate from the budget counter.
- Output tokens: about 6k, an estimate.
- Total: about 44k, against a cap of about 50k.

## Pass 4

Pass 4 at fbce68db does not stand. One high finding is a regression of frame 305 in both directions: the door now takes the act that the Liaison writes for a team note and never checks it against his words (P4-1). A second high finding is that no brief names the acts `keep`, `rewrite`, `add` and `drop`, or the target kind `check`. So P6 to P8, P11 and the Tester route of `criteria_respecify` grant nothing for a live Liaison (P4-2). The commit holds no hunk of pass 5. P1 works on m37 with an act and writes the stray with none. `_resolve_contest` reads the record. Counts: 2 high, 6 low.

The tree is `p4_head` (fbce68db) in the scratchpad. `p4_mix` holds the tests of fbce68db over the `rota/` of c4a51c7d.

### Pass 4, the points

1. Contamination: CONFIRMED clean. The diff c4a51c7d..fbce68db does not touch `rota/core/sandbox.py`, `rota/core/schema.sql`, `rota/tools/nightreport.py` or `tests/rota/test_read_back.py`. The 282 long lines that 899879de adds share 2 lines with pass 4: a `from __future__` import and one SQL head in a test. The names that pass 5 defines are absent from `p4_head/rota`, for example `reading_line`, `readings_owed`, `_READ_BACK_VERDICT`, `_unconfirmed_line` and `_is_reading`.
2. One helper: the deleted names are gone. `_words_remove_a_kind`, `_REMOVE_CUES`, `_removal_asks`, `_DROP_LINE`, `_faults_on`, `_keep_cancels`, `_ADD_LINE`, `_page_added_lines`, the 6 P10 patterns, `_note_words` and `_ruling_words_on` have no hit in `rota/`. `_asks_removal` and `_removal_spans` stay, and they read only the texts that are not his. `earlier_exchange` stays in the C5 reader and the landing push only. Three readers of his words for a permission remain (P4-6).
3. m37: CONFIRMED by `rv_m37.py` and the new tests. Act `remove` with target `get_app_dir:518` on `batch_1` commits with no stray. The same act on the item ref also commits with no stray. A plain approve writes the stray `src/click/utils.py::get_app_dir`. The new tests fail on the old tree and pass on fbce68db. A later plain approve on the same ref takes the grant back (P4-3). The bare target `518` and an act with no target grant nothing (P4-4).
4. The deviations: both are gaps. P11 reads the act of the call, and nothing compares that act with his words (P4-1). The night turns are m11 and m45 of night 160, and s357 of night 161. One target per ref cannot hold two paths on one key. m192 and m201 of night 156 name two test files on one key, and the tests that pinned them are deleted (P4-7).
5. The landing sentence: qwen3.5:9b can fill `remove` from m37, but it cannot learn the other acts. PLAUSIBLE, because this review ran no model. The example in the brief shows `remove` with `app.py:518`, and the target form `utils.py:518` grants. But the sentence says "only when the reply asks for that change", and m37 permits a removal ("You can remove"). The sentence does not say which line carries the act, and m37 is an approve. It names no other act (P4-2, P4-5).
6. `_resolve_contest`: CONFIRMED. It walks `ruled(conn, [item])` from the newest row, and it takes the first contest or revise. It reads no `verdict:` map. The words still come from `entry_for` of the verdict message, so it gives the whole reply and not the span of the row.
7. Weakened assertions: the night turns below lost their pins with no granted test in their place. The new tests in `test_seam_permission_readers.py` test the mechanism of each P reader with an act and with none, and no night turn.
   - `test_guess_route`: m192, m201, m110 and m68 (two files on one key), and m147 and m193 (a keep clause spares a file).
   - `test_frame308_answer_after_respecify`: s370, s250 and s220 (a drop or a rewrite asks new words), and s274 (a fault of the check alone asks none).
   - `test_frame308_ruling_answer`: a revert or a partial edit is no drop, a negated removal asks no new words, and a keep yields to a request for new words.
   - `test_request_page`: 32 cases of the no-clause scope.

   The negative pins kept a false drop or a false keep out. These pins now have no owner until the pass 3 checker exists (P4-8).

### Pass 4, the findings

- P4-1. `rota/roles/api.py`, the team-note block of `rulings_rule` (the diff hunk at 12492). High. CONFIRMED by `rv_p11.py` on `p4_mix` and `p4_head`. At fbce68db, a revise with act `rewrite` lands on the words of m11 and m45 of night 160 and on "Line 11 is wrong." At c4a51c7d, the same calls were refused. The s357 words "On line 11, use the normal test runner" as a plain revise landed at c4a51c7d and are refused at fbce68db. So the five refusals of night 161 return for each Liaison that writes no act. Fix: keep `_note_words` as the check until pass 3 reads the span, or refuse an act whose `words` span his reply does not hold.
- P4-2. `rota/roles/prompts/liaison/landing.md` 14 to 16, `landing.base.md` and `answering.md`. High. CONFIRMED by grep. The briefs show the act `remove` in one example. No brief names `keep`, `rewrite`, `add` or `drop` as an act, or `check` as a target kind. Only the refusal text of `_ruling_shape` lists them. So P6, P7, P8, P11 and the Tester route grant nothing in a live night. Fix: name each act and the line it sits on in one sentence each, then measure the 3 contest cases and the m37 case on both forms.
- P4-3. `rota/roles/principal.py` `grant`. Low. CONFIRMED by `rv_m37.py`. The newest landed row decides, so a later ruling that approves `batch_1` with no act takes back the removal of m37. Night 169 landed m41 on the same refs after m37. The failure writes a stray, so the Architect sees it. Fix: decide whether a null act revokes, and write the rule into the brief and the docstring.
- P4-4. `rota/roles/api.py` `_gone_targets` against the brief. Low. CONFIRMED by `rv_m37.py`. `get_app_dir:518` and `utils.py:518` grant. `518`, a prose target and an act with no target grant nothing. The brief shows one example form only. Fix: name the form "function or file, a colon, the line number" in the brief.
- P4-5. `rota/roles/prompts/liaison/landing.md` 16. Low. PLAUSIBLE. "Only when the reply asks for that change" excludes a permission such as m37 "You can remove". Fix: write "asks for or permits that change".
- P4-6. `rota/roles/api.py` about 1906, 1427 to 1446 and 6794. Low. CONFIRMED by reading. Three readers of his words remain for a permission. The lost-name filter of P2 passes a drop when his words hold the name, even in a keep. `_item_sentences` reads `_PAGE_CUE` on his words to refuse an amend. P9 matches a contested name in his span by a word-bound pattern. Fix: move each one to `grant`, or record each one as a check of type C that pass 3 owns.
- P4-7. `rota/core/runner.py` `disputed_paths`. Low. CONFIRMED by reading. It needs an exact target per path, and a row holds one target. So the second wrong file of m192 and m201 stays on the guess. Fix: let `target` hold a list for target kind `path`, or split the guess key per path.
- P4-8. The order of the passes. Low. CONFIRMED by `git log c4a51c7d..fbce68db`. Pass 4 landed with no pass 3, so no checker compares an act with his span. Fix: keep the deleted negative pins as xfail tests of the pass 3 checker, so their night turns stay owed.

### Pass 4, the probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e03f97fc-cdd4-4daa-864c-2ca4d7ef42a5/scratchpad/`.

- `p4.diff` and `p5.diff` with an inline compare of the added lines, and a grep of the names that pass 5 defines in `p4_head`.
- A grep of the old helper names and `earlier_exchange` in `p4_head/rota`.
- `rv_m37.py` on `p4_head`: 8 placements and targets of the m37 act, and a later plain approve.
- `rv_p11.py` on `p4_mix` and `p4_head`: 4 sets of his words, each as a plain revise and as a revise with act `rewrite`.
- pytest on `p4_mix` and `p4_head`: `test_frame339_removal_stray`, `test_frame305_note_revise`, `test_frame283_removal_on_ruling` and `test_seam_permission_readers`. The result is 2 failed and 1 import error on the old tree, and 116 passed on fbce68db.

### Pass 4, usage

- Input tokens: about 46k, an estimate from the budget counter.
- Output tokens: about 8k, an estimate.
- Total: about 54k, against a cap of about 50k.
