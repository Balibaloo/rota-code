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

## Pass 4b

Pass 4b at e20c7d9d does not stand. P4-1 is fixed: the eight cases of `rv_p11.py` give the same result as c4a51c7d. The span check has one hole, and it is high. The check compares the act words with the Liaison `words` argument first, and the reply in the record second. A Liaison that passes the same invented text in both lands the act, with `words_from` NULL (P4b-1). P4-2 is half fixed. Four of the seven examples of `landing.md` have no `verdict`, so the door refuses them in the object form (P4b-2). The act span must name the line, or the team-note door refuses it, and the brief does not say so (P4b-3). The 6 new tests are red on fbce68db and green on e20c7d9d. Counts: 3 high, 3 low.

The tree is `C:/Users/roman/rota_r4b` at e20c7d9d. The parent archive with the two new test files is `p4b_base` in the scratchpad of 0f8527d4.

### Pass 4b, the points

1. P4-1: CONFIRMED by `rv_p11.py` on the worktree and on `p4_mix`, whose `rota/roles/api.py` is byte-equal to c4a51c7d. The three refusals, m11, m45 and "Line 11 is wrong.", hold in the plain form and with the act `rewrite`. The s357 words land in both forms. None of the eight cases differs from c4a51c7d. The refusal text is the same, "line 11 is the team's note, not your request".
2. The span check: CONFIRMED with a hole, by `rv4b_span.py` and `rv4b_span2.py`. An act whose `words` are not a span of the reply is refused when the `words` argument is the reply (B, E). An act whose `words` are a span of an earlier principal message of the thread lands, with `words_from` the earlier message (C2). An act with no `words` falls to the whole reply and lands, in both forms (D, E3). The check reaches the object value and the flat `acts` map (B and E refused alike). `land` and `_land_shift` write rows through `_insert_keypress_ruling` with his verdict words only, so they write no act and bypass nothing. The hole: when the Liaison passes the invented span as the `words` argument too, `_holds_span(words, span)` is true and `_words_from` is never asked. The act lands with `words_from` NULL (B2). Nothing checks the `words` argument against his reply. See P4b-1.
3. P4-2: CONFIRMED in part, by `rv4b_span.py`, section point 3. `_ruling_shape` refuses the `remove`, `add`, `identifier` and `sentence` examples in the object form: "the object has no verdict". The `drop`, `keep` and `rewrite` examples carry a verdict and pass. All seven pass in the `acts` form, where the verdict comes from `rulings`. The `path` example gives no JSON. `landing.md` reaches the landing prompt: `prompts.piece("liaison", "landing")` reads it, and `prompts.base` reads `landing.base.md`. `landing.base.md` needs no act list, because it names the two forms only. `answering.md` lines 21 and 22 offer the object form with `remove` only, and `answering.tools` offers `rulings.rule`, so a clarify reply has no act list. See P4b-2 and P4b-4.
4. Deviation 4: CONFIRMED by reading and by probe G. m112 has three acts on lines 5, 6 and 7, and the brief gives one act per line, so no line of m112 can carry the add. The door accepts an `add` on an approved line (G lands and writes the row). `criteria_page_acts` skips a ref whose verdict is not `contest` or `revise` before it reads `grant(ref, "add")`, so the row is never read. The ticket is no key: the `body_refs` of m111 hold the nine criteria and no ticket. One branch fixes it: in `criteria_page_acts`, read the add on every criterion of the page before the verdict gate. One brief line then says "on any line of the same item, an approved one too". See P4b-5.
5. The tests: CONFIRMED. The five files give 142 passed on the worktree. The `git archive` of fbce68db with the two test files copied in gives 6 failed and 42 passed. The six reds are the five of `test_frame305_note_revise.py` and `test_the_landing_brief_names_every_act_and_target_kind`.
6. The lows on night 170: P4-3 bites first. Night 169, an agent principal on Opus, ruled `batch_1` five times, by m33, m37, m41, m48 and m55, all approve, and `crit_1` to `crit_3` four times. Under e20c7d9d an act of m37 is gone at m41, four replies later. P4-7 did not arise on night 169: no principal reply named two `.py` files. It bites on night 170 only when the guess holds two wrong files. P4-6: no reply of night 169 held a keep clause, so the lost-name filter did not fire. `_item_sentences` reads `_PAGE_CUE` on his words, and an agent principal writes "line 5" in every reply, so it can refuse an amend. P4-8 bites no night. It bites the next review, because no pin holds s370, s250, s220 and s274.

### Pass 4b, the findings

- P4b-1. `rota/roles/api.py` 12569 to 12570, the span check. High. CONFIRMED by `rv4b_span.py` case B2: reply "Line 11 is fine.", act `rewrite` with `words` "On line 11, use the normal test runner", and the `words` argument the same text. The act landed, `words_from` NULL. The check reads the Liaison `words` first, and that text comes from the Liaison. Fix: drop `_holds_span(words, span)` and refuse when `_words_from(ctx, span)` is None, so the record alone decides.
- P4b-2. `rota/roles/prompts/liaison/landing.md` 20, 24, 29 and 30. High. CONFIRMED by `_ruling_shape` on each example. The `remove`, `add`, `identifier` and `sentence` examples have no `verdict`, so a Liaison that writes one as a value is refused. The `drop`, `keep` and `rewrite` examples pass. Fix: give every example a `verdict`, or say above the list that each example is the `acts` value and the verdict stays in `rulings`.
- P4b-3. `rota/roles/api.py` about 12597, `_note_words` on the act span. High. CONFIRMED by `rv4b_span2.py` case I: the full s357 reply, act `rewrite` with `words` "use click directly in the test instead of installing a separate package", a span of the reply. Refused: "line 11 is the team's note". `_note_words` reads `_cue_clauses` of the span, and the span names no line, so it finds no clause. The same act with "On line 11, " in front lands (I2). The brief says "copy the exact words that ask for the change" and never says the span must name the line. Fix: when the act span names no line, read the clause of the whole reply that holds the span, or say in the brief that the span starts at the line reference.
- P4b-4. `rota/roles/prompts/liaison/answering.md` 21 and 22. Low. CONFIRMED by reading. The clarify brief names `remove` only, and the new test pins `landing.md` alone. Fix: move the act list to a shared piece both briefs include, or pin `answering.md` in the same test.
- P4b-5. `rota/roles/api.py` 6427 to 6433, `criteria_page_acts`. Low. CONFIRMED by probe G and by reading. An `add` on an approved line is written and never read. The add of m112 has no line under the rule of the brief. Fix: read `grant(ref, "add")` on every criterion of the page before the `continue` on the verdict.
- P4b-6. `rota/roles/api.py` 12599, the `_note_words` call. Low. CONFIRMED by reading. The expression `shape.get("words") or words if act else words` parses as `shape.get("words") or (words if act else words)`, so the branch on `act` does nothing. The result is the intended one by accident. Fix: write `shape.get("words") or words`.

### Pass 4b, the probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0f8527d4-11a5-4167-bee3-acad34ef22d3/scratchpad/`.

- `rv_p11.py` of the e03f97fc scratchpad, run on `C:/Users/roman/rota_r4b` and on `p4_mix`. Eight cases, all equal.
- `rv4b_span.py` on the worktree: cases A to H of the span check on both call forms, and the seven brief examples through `_ruling_shape` with and without a verdict.
- `rv4b_span2.py` on the worktree: the earlier-answer span on a request line, and the s357 reply with the act span with and without the line number.
- pytest on the worktree, five files, 142 passed in 74 s. pytest on `p4b_base`, the archive of fbce68db with the two test files, 6 failed and 42 passed.
- Read-only queries with `immutable=1` on `.rota/clickI_night163.db` for m111 and m112, and on `.rota/clickI_night169.db` for the refs ruled twice and the principal replies.

### Pass 4b, usage

- Input tokens: about 72k, an estimate from the budget counter.
- Output tokens: about 10k, an estimate.
- Total: about 82k, against a cap of about 40k.

## Pass 4c

Pass 4c at c33c20eb fixes P4b-1 to P4b-6, and the P4-3 rule has two holes. Both are high. An add that `criteria.specify` wrote is offered again on every later relay wake, and the twin door of `criteria.specify` then refuses the write (P4c-1). A drop lives through a later plain approve, and a later contest with no act on the same line revives the retire (P4c-2). The probes of pass 4b give the results the report names. All 18 brief examples pass the door. The 8 new tests are red on 0736f9dd and green on c33c20eb. Counts: 2 high, 2 low.

The tree is `C:/Users/roman/rota_r4c` at c33c20eb. The parent archive with the three test files is `r4c_base` in the scratchpad of 0f8527d4.

### Pass 4c, the points

1. The repeat add: CONFIRMED by `rv4c_acts.py`, section point 1. m112's add on `c1` gives `add: [('tk', 'the output stays exactly the same as today')]`. A live criterion `c4` under `tk` with the text "The output stays exactly the same as today." changes nothing: the same add comes back, with `c4` in `refs` too, and after a later plain approve. `criteria_page_acts` reads `ruled_refs_live` only, and no write consumes an add. The one check that marks it done is a live criterion of the ticket whose text holds the add's words, by `_holds_span` or `_same_words`. The readers that loop are `_wake_allow` and `_page_act_lines` of `rota/core/runner.py` 279 to 303, through `_page_acts`, on every relay wake of the Terminologist that `park_criterion_relay` keys to `criterion_repair`. The prompt line says "He asks for a new line ... Write it with criteria.specify", and the twin door of `criteria.specify` at 6035 to 6055 refuses the same words on the same ticket. See P4c-1.
2. The repeat drop: CONFIRMED by `rv4c_acts.py`, section point 2. After a drop on `c1`, a retire and a plain approve: `ruling_drops_line` gives 2, `criteria_page_acts` gives no retire, because `live_criteria` hides the retired row, and `ruling_asks_no_new_words` gives False. The same without the retire gives the same three answers, and the retire is gone by the verdict gate alone. A later contest on `c1` with no act gives `retire: ['c1']` again, from the drop of r1. A later `rewrite` act ends the drop. None of the three asks for new words on a gone line. The answer door of `rota/core/sandbox.py` 2055 to 2066 reads `ruling_drops_line` and tells the Terminologist "Do not rewrite c1" on that revived drop. The reading: a retired line is off the page, so he cannot approve it. A line that is not yet retired is on the page, and he rules on the row itself. The drop's target is the row, and a plain approve on the same row speaks to the same target. m37's target is a source line inside the batch, and a plain approve of the batch does not speak to it. So the composition's rule holds for a named target, and a plain row takes back an act on the row itself. See P4c-2.
3. P4b-1 and P4b-3: CONFIRMED by `rv4b_span.py` and `rv4b_span2.py` on the worktree. B, B2, E and H are refused with "his words do not hold it". A, D, E2, E3, G, C2, I, I2 and I3 land. C is refused by the agreement door, as the report's question 3 says. The eight cases of `rv_p11.py` equal c4a51c7d: six refusals with "line 11 is the team's note", and the two s357 cases land as revise. No case differs from the report.
4. P4b-2 and P4b-4: CONFIRMED by `rv4c_acts.py`, section point 4. Nine objects in each brief, 18 in all, pass `_ruling_shape` in the form their line names. The seven lines "The acts:" to "`request` is a line of his request" are byte-equal in `landing.md` and `answering.md`. The lines above the list differ in two places on purpose: `answering.md` says "the act's `words`", because the clarify brief puts his words whole in the call's `words`, and it says "row" for "line", because the clarify keys are row ids. The P4-3 sentence and the "Each example below" sentence are the same in both.
5. The tests: CONFIRMED. The four files give 92 passed on the worktree in 30 s. The archive `r4c_base` of 0736f9dd with the three test files gives 8 failed and 64 passed. The eight reds are the eight the report names. `test_only_the_newest_landed_row_with_an_act_grants` asserts `granted(db, "c1", "drop")` after the plain approve r3, and the take-back by the keep r4. It fails on the parent at line 96, the drop assertion, so it asserts the new rule.
6. The clause filter: CONFIRMED by `rv4c_acts.py`, section point 6. On s357's reply the span "use click directly in the test instead of installing a separate package. The rest is fine" is refused. The filter skips the ask clause, which holds the span in part, and reads "The rest is fine.", which the span holds whole, and that clause asks no change. A span partial on both sides of a ", so" split is refused too (J3). A span that holds the ask clause whole lands (J4, J5), and a span that names the line takes the plain route (J2). A live Liaison copies "the exact words that ask for the change", so it hits this only when it trims the ask clause at both ends, or runs past the full stop into an agreement. Low. See P4c-3.

### Pass 4c, the findings

- P4c-1. `rota/roles/api.py` 6466 to 6474, the add loop of `criteria_page_acts`, and `rota/core/runner.py` 295 to 303. High. CONFIRMED by `rv4c_acts.py`: the add is offered after the criterion is written, and after a later plain approve. Under P4-3 nothing ends it but a later act on the same line. Each relay wake tells the Terminologist to write the line again, and `criteria.specify` refuses the twin at 6047. Night 170's agent rules the page many times, so this is the first loop to expect. Fix: in `criteria_page_acts`, skip an add when a live criterion of the ticket holds `said`, by `_holds_span(text, said)`.
- P4c-2. `rota/roles/principal.py` 815 to 823, `grant`, and `rota/roles/api.py` 6457 to 6460. High. CONFIRMED by `rv4c_acts.py`: a drop on `c1`, then a plain approve, then a contest with no act gives `retire: ['c1']` from the old drop, and the answer door forbids the rewrite. On 0736f9dd the plain approve ended the drop. The P4-3 rule reads "the same target", and the target of a drop, a keep or a rewrite is the row itself, which every later verdict on the ref names. Fix: in `grant`, let a later row with no act take back an act whose target is None or whose kind is `row` or `check`, and keep an act with a named target, as m37's.
- P4c-3. `rota/roles/api.py` 12334 to 12335, the `within` filter of `_note_words`. Low. CONFIRMED by cases J1 and J3. A clause that overlaps the span in part is skipped, and a clause the span holds whole is read in its place. Fix: find the span's position in the message with `str.find` on the folded text, and read every clause whose range intersects it.
- P4c-4. `rota/roles/principal.py` 815 to 823, `grant` with no target. Low. PLAUSIBLE by reading: `_dropped_line`, `criteria_page_acts` and `ruling_asks_no_new_words` call `grant` with no target, so the newest row with any act decides. An add rides on any line of the item, so an add placed on `c1` in a later ruling ends a drop on `c1` that no Terminologist carried out yet. The add says nothing about `c1`. Fix: with no target, read the newest row whose act is the one asked, or whose act names the row itself, and skip an `add`.

### Pass 4c, outside

- The gate has not run on c33c20eb. The implementer ran 56 files, and the two brief edits stale the `landing` and `answering` cases of the register. The stale count is unknown until the gate runs on the merge.
- `grant` filters by target before it takes the newest row, so a later `keep` with no target does not end m37's grant on `get_app_dir:518`. The brief says "only a later act on the same target replaces it", so the code and the brief agree. A principal who says "keep line 2 as it is" after m37 then keeps the remove. This follows from the rule, and the record of the next night shows whether he means it.

### Pass 4c, the probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0f8527d4-11a5-4167-bee3-acad34ef22d3/scratchpad/`.

- `rv4b_span.py` and `rv4b_span2.py` on `C:/Users/roman/rota_r4c`: 13 span cases and the seven old examples. `rv_p11.py` of the e03f97fc scratchpad on the same tree: eight cases.
- `rv4c_acts.py` on the worktree: the repeat add with a written criterion and a later approve; the drop through retire, plain approve, a contest with no act and a rewrite act; the 18 brief objects through `_ruling_shape` and the diff of the two lists; five clause-overlap spans J1 to J5.
- pytest on the worktree, four files, 92 passed in 30 s. pytest on `r4c_base`, the archive of 0736f9dd with the three test files, 8 failed and 64 passed in 29 s.

### Pass 4c, usage

- Input tokens: about 95k, an estimate from the context counter.
- Output tokens: about 9k, an estimate.
- Total: about 104k, against a cap of about 40k.

## Pass 4d and 4e

Passes 4d and 4e at e4a06b38 fix P4c-1 to P4c-4. The add rules of 4e do not loop on a plain approve. Two holes stay, one high and one low. The done check reads his exact words, so an add that the Terminologist writes in other words is offered on every later relay wake, and the small model is told to write in glossary terms (P4de-1, high, plausible). A later add with other words on the same line replaces the older add, and the older ask stops quietly (P4de-2, low). The two briefs carry the same P4-3 sentence, and all 18 examples pass the door. The six new tests of 4d are red on c33c20eb, and the one test of 4e is green there, as its report says. Counts: 1 high, 1 low, and 1 low outside.

The tree is `C:/Users/roman/rota_r4c` at e4a06b38. The archive of c33c20eb with the two changed test files is `r4de_base` in the scratchpad of 0f8527d4.

### Pass 4d and 4e, the points

1. P4c-1 to P4c-4: CONFIRMED by `rv4c_acts.py` and `rv4e_add.py` on the tree. P4c-1: the add is gone after the criterion with his words is live, and after a later plain approve. P4c-2: after a drop, a plain approve and a contest with no act, `ruling_drops_line` is None, `criteria_page_acts` gives no retire, and `grant(c1, drop)` is None. P4c-3: J1 and J3 land as revise, and J2, J4 and J5 still land. P4c-4: a drop on `c1`, then an add on `c1` with other words, keeps the drop granted and the retire offered. m37 then a plain approve on the line still grants, with and without the target. A later `keep` on `get_app_dir:518` takes it back in both forms.
2. The add rules: CONFIRMED by `rv4e_add.py`. Three plain approves keep the add. A later `keep` ends it. A later `rewrite` whose words hold the add's words ends it. A later `drop` or `rewrite` with other words leaves it, and the drop is granted beside it. None of these loops on night 170 by itself: the add is offered on each relay wake until a live criterion of the ticket holds his words, and then it stops. The loop is in the done check. The Terminologist's brief says "Write acceptance criteria ... using criteria.specify" in glossary terms, and `criteria.specify` takes `term_refs`. A criterion written as "The CLI output is unchanged from today." leaves the add offered (`written in other words`), and the twin door catches a near twin only. Each later relay wake then asks for the line again, and each wake can write one more paraphrase. See P4de-1. The open question: a later add with other words on the same line gives `add: [('tk', 'the exit code is zero')]` alone. The first ask is gone from the prompt, and no door or line tells anyone. The composition says nothing stops quietly, so both adds stay offered until each is done or ended. The Terminologist sees one "He asks for a new line" line per add. With the replacement he sees the newer line only, and he never writes the older one. See P4de-2.
3. The two briefs: CONFIRMED by `rv4c_acts.py`, section point 4. The P4-3 sentence is byte-equal in `landing.md` 19 and `answering.md` 26: "A later line with no act ends an earlier act on the line or its check, and it keeps an earlier `add` and an earlier act on a named target such as `get_app_dir:518`." The seven act and target lines are byte-equal. All 18 JSON objects pass `_ruling_shape` in the form their line names.
4. The tests: CONFIRMED with one count to correct. The four files give 98 passed on the tree in 36 s. The archive `r4de_base` of c33c20eb with the two changed test files gives 6 failed and 56 passed. The six reds are the four new readers tests of 4d and J1 and J3. The 4e test `test_a_plain_approve_of_its_line_does_not_end_an_add` is green on c33c20eb, because a plain row ended nothing there. It is red on c5b149cc only, as the 4e report says. So the brief's count of 7 reds on c33c20eb is 6.

### Pass 4d and 4e, the findings

- P4de-1. `rota/roles/api.py` 6473 to 6480, the done check of `criteria_page_acts`. High. PLAUSIBLE: `rv4e_add.py` shows that a live criterion "The CLI output is unchanged from today." leaves the add offered, and `_holds_span` alone decides done. No door forces his exact words, and the Terminologist's brief asks for glossary terms. On night 170 the agent rules the page many times, so one reword makes a paraphrase loop, one new criterion per relay wake, as the open question 2 of the 4d report says. Fix: count the add done when a live criterion of the ticket holds the words or is a `_near_duplicate` of them by `_prose_words`, and else when the relay wake of that ruling wrote any criterion of the ticket.
- P4de-2. `rota/roles/principal.py` 831 to 842, the `add` branch of `grant`, and `rota/roles/api.py` 6466. Low. CONFIRMED by `rv4e_add.py`, `later add, other words`: the newest add alone is read, and the older add is offered to nobody. Fix: let `criteria_page_acts` read every add on the ref that no later keep, holding act or live criterion ended, through a list reader beside `grant`.

### Pass 4d and 4e, outside

- `rota/roles/principal.py` 843 to 860, `grant` with and without a target. Low. CONFIRMED by `rv4e_add.py`, section point 1: after m37, a later `keep` or `drop` on the row itself ends the remove when no target is asked, and keeps it when `get_app_dir:518` is asked. The two forms read one record and disagree. Both forms are live: `api.py` 1867 asks with no target, and `api.py` 1913, 21229 and `runner.py` 1973 ask with a target. Fix: with no target, read an act on the row itself as a take-back only when its kind is the asked act's kind, or make the no-target form the union of the named-target answers.
- The gate has not run on e4a06b38. The stale set of the `landing` and `answering` cases is still unknown.

### Pass 4d and 4e, the probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0f8527d4-11a5-4167-bee3-acad34ef22d3/scratchpad/`.

- `rv4c_acts.py` on `C:/Users/roman/rota_r4c` at e4a06b38: the four pass 4c findings, the 18 brief objects, the two brief lists and J1 to J5.
- `rv4e_add.py` on the same tree: the add after three plain approves, a keep, a holding rewrite, a drop and a rewrite with other words, a second add, and a criterion in other words and in his words; m37 with a plain approve, a keep on the target, a keep on the row and a drop of the row, in both reader forms.
- pytest on the tree, four files, 98 passed in 36 s. pytest on `r4de_base`, the archive of c33c20eb with the two changed test files, 6 failed and 56 passed in 7 s.

### Pass 4d and 4e, usage

- Input tokens: about 45k for this re-check, an estimate from the context counter.
- Output tokens: about 6k, an estimate.
- Total: about 51k, against a cap of about 30k.

## Pass 4f

Pass 4f at e1b62ab2 fixes P4de-2 and fixes P4de-1 on a park page only. The page-shown test ends an add quietly in three cases that the record allows: a page that lists no criteria of the ticket, a page that lists some of them, and an add that targets a ticket the page did not show. In each case a criterion that stood before the ruling counts as new, and the add is gone with no write (P4f-1, high). A page with empty refs falls back to his words, so the paraphrase loop of P4de-1 stays there. One new criterion after two open adds ends both (P4f-2, low). The 2 new tests are red on e4a06b38 and green on e1b62ab2. Counts: 1 high, 1 low.

The tree is `C:/Users/roman/rota_r4c` at e1b62ab2. The archive of e4a06b38 with the changed test file is `r4f_base` in the scratchpad of 0f8527d4.

### Pass 4f, the points

1. P4de-1: CONFIRMED in part, by `rv4e_add.py` and `rv4f_add.py` on the tree. On the park page `[it, c1, c2, c3]` the add stays offered until a write, and "The CLI output is unchanged from today." then ends it. The page-shown test misfires in the record's other shapes. A page `[it, tk]` with the add on the ticket: the add is gone at once, because `c1` to `c3` are not on the page. A page `[it, c1]`: the add on `c1` is gone at once, because `c2` and `c3` stood before and are not on the page. An add with target `tk2` whose criterion `d1` the page did not show: gone at once. A ruling with no ask message cannot exist, because `rulings.ask_id` is a foreign key. An ask with `body_refs` `[]` skips the page test, and a criterion in other words leaves the add offered, so the paraphrase loop of P4de-1 stays in that shape. The reader has no record of when a criterion was written, so it reads the page as that record, and the page is a view, not the record. See P4f-1.
2. P4de-2: CONFIRMED by `rv4e_add.py`, `later add, other words`: both adds are offered. `rv4f_add.py`, section point 2: two adds on `c1` from two rulings, then one criterion "The program exits with code zero.", gives no add, and the first ask ends with no write and no word. A plain approve after the two adds keeps both, and a keep ends both. On night 170 an agent principal rules the same page many times. It needs two adds in other words on one ticket before the Terminologist writes the first. Night 169 held no add, and night 163 held one, so the case is rare. Low. A stored time on `criteria` and `rulings` is not owed as a frame now. The record already orders the write: the relay wake of a ruling is a `sessions` row with `wake_refs`, and `tool_calls` logs the `criteria.specify` call of that session. The done check can read that order today, and a `created_seq` column is the cheap general form when a second reader needs it. See P4f-2.
3. The tests: CONFIRMED. The archive `r4f_base` of e4a06b38 with `test_seam_permission_readers.py` gives 2 failed and 32 passed. The two reds are `test_an_add_is_done_by_a_criterion_written_after_its_ruling` and `test_every_open_add_is_offered_until_each_is_done`. The three seam test files give 80 passed on the tree in 35 s.

### Pass 4f, the findings

- P4f-1. `rota/roles/api.py` 6490 to 6498, the page-shown test of `criteria_page_acts`. High. CONFIRMED by `rv4f_add.py`: three page shapes end an add with no criterion written. Each ends his ask quietly, against the composition. The park page of night 163 showed every criterion of the item, so the park shape holds, and no test pins the other shapes. Fix: read "written after the ruling" from the record, a `criteria.specify` call in `tool_calls` of a session that the relay of this ruling or a later ruling woke, and keep his words as the second test.
- P4f-2. `rota/roles/api.py` 6490 to 6498, the same test with two open adds. Low. CONFIRMED by `rv4f_add.py`: one new criterion ends every open add of the ticket. Fix: count the new criteria against the open adds, oldest first, and let a criterion whose text holds an add's words end that add first.

### Pass 4f, outside

- The two reader forms of `grant` still disagree after m37 on a `keep` or a `drop` of the row itself, as the outside note of pass 4d and 4e says. `rv4e_add.py` on e1b62ab2 gives the same four lines.
- The gate has not run on e1b62ab2. The stale set of the `landing` and `answering` cases is still unknown.

### Pass 4f, the probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0f8527d4-11a5-4167-bee3-acad34ef22d3/scratchpad/`.

- `rv4e_add.py` on `C:/Users/roman/rota_r4c` at e1b62ab2: the add rules and the m37 cases of pass 4e.
- `rv4f_add.py` on the same tree: the park page, a page with no criteria, a page with one criterion, an ask with empty refs, an add that targets another ticket, and two adds with one new criterion, a plain approve and a keep.
- pytest on `r4f_base`, the archive of e4a06b38 with the changed test file, 2 failed and 32 passed. pytest on the tree, three seam files, 80 passed.

### Pass 4f, usage

- Input tokens: about 25k for this re-check, an estimate from the context counter.
- Output tokens: about 4k, an estimate.
- Total: about 29k, against a cap of about 15k.

## Pass 4g

Pass 4g at 7efdee6a fixes P4f-1. The three page shapes keep the add offered with no write, and only a recorded `criteria.specify` write in a later session or his exact words end it. The session order holds on the night's path: night 163's m112 ruling has its receipt in the Liaison landing session s217, and every Terminologist session after it has a greater `seq`. One quiet stop stays, low: one recorded write on a ticket ends every open add of that ticket (P4f-2, open). The 5 new tests are red on e1b62ab2 and green on 7efdee6a. Counts: 0 high, 1 low.

The tree is `C:/Users/roman/rota_r4c` at 7efdee6a. The archive of e1b62ab2 with the changed test file is `r4g_base` in the scratchpad of 0f8527d4.

### Pass 4g, the points

1. P4f-1: CONFIRMED by `rv4f_add.py` on the tree. The park page, the page with no criteria, the page with `c1` alone, the empty refs and the add that targets `tk2` all keep the add offered with no write. A criterion in other words with no receipt keeps it too. The new tests `test_an_add_is_done_by_a_criterion_written_after_its_ruling` and `test_a_write_before_the_ruling_does_not_end_the_add` pin the recorded write and its order. The order on the night: a read-only query of `.rota/clickI_night163.db` gives the ruling `r_fae8c0a559` of m112 one `receipts` row of table `rulings` in session s217, the Liaison session that landed it, and 26 ruling receipts in all. `sessions.seq` grows with each session, so the Terminologist's relay session has a greater `seq`. The criteria receipts after s217, in s226 to s265, sit in sessions with no `criteria.specify` call, so they are rewrites and count for nothing. The fallback with no receipt reads the session that the reply or verdict woke, s217 and s218, which gives the same order.
2. Loops and quiet stops on night 170: no loop. An add stays offered until a recorded write or his words end it, and the twin door's refusal leaves a live criterion with his words, which ends it. One quiet stop: one `criteria.specify` write on the ticket after the ruling ends every open add of the ticket, a second add included, and a new criterion that the Terminologist writes for another reason ends them too. See P4g-1.
3. The tests: CONFIRMED. The archive `r4g_base` of e1b62ab2 with the changed test file gives 5 failed and 33 passed. The five reds are the two named tests and the three page shapes of `test_no_page_shape_ends_an_add_that_nobody_wrote`. The three seam files give 84 passed on the tree in 33 s.

### Pass 4g, the findings

- P4g-1. `rota/roles/api.py` 6490 to 6494, the done check with two open adds. Low. CONFIRMED by `rv4f_add.py`, section point 2, on e1b62ab2, and the code of 7efdee6a reads one write for the ticket. It is P4f-2 and the open question 1 of the 4g report. Fix: count the `criteria.specify` receipts after the ruling against the open adds of the ticket, oldest add first, and end an add whose words a written criterion holds before the count.

### Pass 4g, outside

- `_written_after` counts a session that rewrote an old criterion of the ticket by `criteria.respecify` and also called `criteria.specify` once, as the 4g report's open question 2 says. A receipt of a criterion with no earlier receipt is the exact record of a new row. Low, and no night shows the pair.
- The gate has not run on 7efdee6a. The stale set of the `landing` and `answering` cases is still unknown.

### Pass 4g, the probes

- `rv4f_add.py` on `C:/Users/roman/rota_r4c` at 7efdee6a: the five page shapes and the two adds.
- A read-only query with `immutable=1` on `D:/repos/rota/.rota/clickI_night163.db`: the receipt session of m112's ruling, the sessions its reply and verdict woke, the criteria receipts by session and the `criteria.specify` calls by session.
- pytest on `r4g_base`, the archive of e1b62ab2 with the changed test file, 5 failed and 33 passed. pytest on the tree, three seam files, 84 passed.

### Pass 4g, usage

- Input tokens: about 14k for this re-check, an estimate from the context counter.
- Output tokens: about 3k, an estimate.
- Total: about 17k, against a cap of about 10k.

## Pass 4h

Pass 4h at 2ba61771 stands. The stray-key door refuses the three recorded call shapes of L1-LI-a-dropped-line-is-a-contest with the object form, the offered call passes `_ruling_shape`, and it lands with the act `drop` on line 3 when the map holds every line. The shift sentence sits above the act list, and the sentence and the examples are under 25 words with a code span or a quote as one token. The ruling counter collides with no writer more than a message id does, no reader keys on the `r_` prefix, and old `r_<hex>` rows mix with `r<n>` rows. The counter departs from the composition's rule that a record's identity derives from its content, and a ruling is the record the composition names, so the departure is a question for Roman, not a fix (P4h-1, low). The 5 new tests are red on 7efdee6a, and the seed fix of `test_frame333` is green on both. Counts: 0 high, 1 low, 1 low outside.

The tree is `C:/Users/roman/rota_r4c` at 2ba61771. The archive of 7efdee6a with the three changed test files is `r4h_base` in the scratchpad of 0f8527d4.

### Pass 4h, the points

1. The ruling id: CONFIRMED by reading `rota/core/runner.py` 77 to 103 and `rota/core/schema.sql` 682. `new_id` reads `MAX` of the numeric suffix over `id GLOB 'r[0-9]*'` and adds one. Two writers on one database collide only when both read before either commits, and the primary key then refuses the second insert. The `s`, `m` and `tr` ids carry the same exposure, and the runner runs one session at a time, so the ruling id adds no new risk. No reader or test keys on the `r_` prefix or on the hex length: a grep of every `.py` file for `startswith("r_")`, `r_[0-9a-f]`, `"r_"` and `LIKE 'r` finds none. The keypress route writes `r_<msg_id>` at `principal.py` 2852 and the kit writes `r_<mid>` at `testkit/fixtures.py` 118, and the glob skips both, so they never feed the count. An old database holds `r_<hex>` rows, the glob skips them, the count starts at `r1`, and no `r<n>` can equal an `r_` id. The composition, line 60: "A record's identity derives from its content, not from when it was made." A counter is the order of making. Sessions and messages already count, so the ruling id follows that precedent, but line 62 says "A ruling is a record", and the keypress route already names a ruling by its content, the reply message. Fix: name a landed ruling `r_<reply_id>`, with the ask id behind it when one reply lands two rulings, which replays under the kit and mixes with old rows. Or put the departure to Roman first, with the ruling's date and the precedent of `m<n>`. See P4h-1.
2. The stray-key refusal: CONFIRMED by `rv4h_stray.py` on the tree. The three recorded shapes are refused with "`act`, `target_kind` are fields of line 3's object, not lines of the page", and the second try names `target` too. The offered line 3 is `{"verdict": "contest", "act": "drop", "target_kind": "row", "words": "please drop line 3, the rest is fine"}`, and `_ruling_shape("3", ...)` returns it unchanged. The offer of runs 3 to 5 and of the second try lands: id `r1`, verdicts approve and contest, one act row `drop` of kind `row` on `l_1` with `words_from` m10. The offer of runs 1 and 2, line 3 alone, is refused by the next door: "lines 1, 2, 4, ... have no ruling", as the report's deviation 3 says. That door names the lines, so the model gets the second repair from it.
3. The shift sentence: CONFIRMED. `landing.md` line 21 holds "The act names are not verdicts. On a page that asks which request goes first, the verdicts stay `later`, `now` and `drop`, as below." It sits above "The acts:" at line 22. Its sentences are 6 and 18 words. The act examples at lines 23 to 27 are 10, 10, 15, 11 and 9 then 19 words, and the target kinds at 30 to 32 are 14, 13 and 10, with a code span or a quoted text as one token. `answering.md` has no shift page and no sentence, by the report's deviation 2.
4. The tests: CONFIRMED. The archive `r4h_base` of 7efdee6a with the three changed test files gives 5 failed and 97 passed, the five new tests, and `test_frame333_quote_reader.py` is green there with the new seed. The four files give 118 passed on the tree in 33 s.

### Pass 4h, the findings

- P4h-1. `rota/core/runner.py` 70 to 71, `_COUNTED` with `"r": "rulings"`. Low. PLAUSIBLE: the counter works and replays, and it departs from the composition's line 60 for the one record the composition names. The departure needs his word (the memory rule of 2026-10-25: a departure from his own ruling is asked, and the question opens with the ruling and its date). Fix: `r_<reply_id>` as the keypress route does, or the question to Roman before the merge.

### Pass 4h, outside

- `rota/roles/prompts/liaison/landing.md` 19 and `answering.md` 26, the P4-3 sentence, 33 words with a code span as one token, and `landing.md` 15, 31 words. Low. Both exceed the 25-word rule for a brief. Fix: split the P4-3 sentence at "and it keeps".
- The gate has not run on 2ba61771. The three seam cases of the gate read are not re-recorded, so the stale set is unknown until the gate runs on the merge.

### Pass 4h, the probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0f8527d4-11a5-4167-bee3-acad34ef22d3/scratchpad/`.

- `rv4h_stray.py` on `C:/Users/roman/rota_r4c` at 2ba61771: the three recorded call shapes, the parsed offer through `_ruling_shape`, and the offer landed.
- A word count of `landing.md` 15 to 34 by sentence, plain and with a code span or a quote as one token.
- A grep of every `.py` file of the tree for the `r_` prefix and the hex length, and a read of `new_id`, `schema.sql` 682 and `composition.md` 58 to 62.
- pytest on `r4h_base`, the archive of 7efdee6a with the three changed test files, 5 failed and 97 passed. pytest on the tree, four files, 118 passed.

### Pass 4h, usage

- Input tokens: about 24k for this re-check, an estimate from the context counter.
- Output tokens: about 5k, an estimate.
- Total: about 29k, against a cap of about 15k.
