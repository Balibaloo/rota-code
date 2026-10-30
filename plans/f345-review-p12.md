# Review p12, passes R3 to R3c at f8a591d1

Verdict: READY. No finding is high. Three findings are low.
The read used the worktree C:/Users/roman/rota_p12 at f8a591d1, against 559b2540.
No live model and no gate ran. tests/rota/test_r1_menu_form.py and test_ruled_refs.py pass: 39 passed, 3 skipped.

## (a) Verdicts on the points

1. Holds. The digit rule reads only a line reference or an ordinal line. A bare number, a verb or a negation does not change the options. `held` lands no row. A clause-key add lands the same row as the line-key add.
2. Holds. Each conflict fires once per line, keyed by the line text. Two conflicts in one call cost two turns, then the call lands. No loop exists. Finding 1 is a false conflict on a read-back line.
3. Holds. The refusal is "line N: the quote lies in clause cK, and cK names no page line. Key that clause instead: ...". It fires once per line and clause across turns, and the next call lands.
4. Holds with a note. Eight cases changed, each on line 1 only. n174-m53-m58 expects ask and has no lines. Six of the eight have line 1 as the one add line. In n172-m80-m81 and n172-m83-m84, line 1 is the statement s3, which offers no add (finding 3).
5. Holds. The prompt has 41 lines, from 39. Every sentence matches the code. The example reply gives c4 options none, held and add, and gives "The rest is fine." lines 1, 3 and 5. The prompt does not tell the conflict rule, and it does not need to.
6. Holds. One test is deleted: `test_a_line_key_wins_over_its_clause_key`. It pinned landed rows s1 approve and l_1 drop. The same call now lands the same rows after one refusal. `test_a_clause_with_no_lines_and_no_key_is_refused_once` and the conflict tests cover the new rule.
7. Outside: findings 1 and 2. runner.py now calls `page_menus` once and passes the menu to `page_clauses`. This change is correct.

## (b) Findings

1. rota/roles/api.py:14073-14080, low, CONFIRMED. The conflict check maps both options through `_OPTION_SAME["line"]` only. On a read-back line, a clause `drop` lands `misread, drop`, so the two keys agree. The check refuses them as two options. Live log r3c_after.txt shows this for n172-m83-m84 on runs 1 and 2: "Clause c4 gives drop, and the line key "2" gives misread, drop". Each refusal costs one turn. Fix: map `mine` and `theirs` through `_OPTION_SAME["read-back"]` when `menu[n][0]` is read-back.
2. rota/roles/api.py:14101-14106 and 14174, low, CONFIRMED. The no-line clause add appends line `adds[0]` and does not check `by_line`. A line key on the same line overwrites the add with no conflict refusal. Probe: `{"3": "drop", "c2": "add The page leaves out the tax.", "2": "other the tax"}` refused once on the quote, then landed calculate_tip as contest with words "the tax". The add is lost. Fix: run the R3c conflict check on `adds[0]` for a clause-key add.
3. tests/rota/cases/l3_rulings.yaml, cases L3R-n172-m80-m81 and L3R-n172-m83-m84, low, CONFIRMED. Line 1 is s3, kind other, with no add option. The page has no add line at all. So `act: null` on line 1 guards nothing in these two cases. Fix: drop the two lines, or say in the case why they stay.

Outside the points, PLAUSIBLE, no finding number: the unkeyed refusal text lists the unkeyed clauses. A changed set gives a new text, so it fires again. n174-m47-m48 run 1 got "c3, c4" and then "c4". The count is bounded by the subsets. Keying the once by clause, as the conflict check does, removes the repeat.

## (c) Probes

1. A pytest probe of the `db`, `_page` and `_seat` fixtures. The probe was copied into the worktree for one run and then deleted. Source: C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/00ca90d0-18a5-4929-b3d3-aedcb3b99ae5/scratchpad/p12/test_p12_probe.py. Output: out.txt beside it. It ran the digit rule on seven clauses, clause add against line add, held and none, two conflicts, unkeyed and approve refusals, the old deleted call, and add with other.
2. A yaml diff by case of 559b2540 and f8a591d1: 8 cases changed, line 1 only.
3. `page_menus` on each changed case, seeded with `fixtures.seed` into temporary databases under scratchpad/p12. It gave add lines [1] for six cases and [] for n172-m80-m81 and n172-m83-m84.
4. `page_clauses` on the prompt example and on "Thanks, looks good otherwise.".
5. Live log reads: r3c_after.txt for conflict and unkeyed refusals.

## (d) Usage

The session counter shows about 70k tokens used, above the 45k cap. About 62k were input and about 8k were output.

# Re-check p12b, passes R3d and R3e at 4fa8f775

Verdict: NOT READY. One finding is high. Three findings are low.
The read used the worktree C:/Users/roman/rota_p12b at 4fa8f775, against f8a591d1.
No live model, no `ROTA_L1=1` and no gate ran.
tests/rota/test_r1_menu_form.py passes in replay: 36 passed in 5.74s.

## (a) Verdicts on the points

1. Holds with finding 1. On a page of many lines, the binder splits "Does it round? Drop line 3." into two clauses, and the statement keeps its options. On a one-line page, the whole reply is one clause, so it offers `ask` only. The landing case a-question-then-a-statement-at-the-confirm-is-the-question expects that `ask`. The prompt rule matches the code. But a question clause that names a line lands its option after the one refusal (finding 1).
2. Holds. No conflict refusal remains, so no false conflict can fire. The read-back mapping now only decides whether a clause add gets a note (finding 4).
3. Holds. Clause add against line `other` on line 2: the line key landed, no refusal, one note. Clause drop against line approve: approve landed, no refusal, no note. No-line clause add against line `other` on `adds[0]`: the existing test shows the same. Line 2 is a request line and offers no `drop`, so the brief's "line drop" shape is `other` there. The R3c once-per-line refusal and the p12 low 2 refusal are both gone from the code.
4. The note costs Roman a visible line. `faults` is read by `render_state` (rota/roles/principal.py:328), the cockpit snapshot and `rota.tools.faults list`. The state print shows "Rota itself failed N times this run. The people who build it have the list." No night code reads `faults`, so a note blocks no night. Each open row stays until a build frame closes it with `rota.tools.faults close`. The landing already writes `faults` rows for an unheld ref (api.py:13857), so the table is not new to the landing. A softer record exists: `tool_calls` keeps each call with its keys, so the displaced add is already on record there. Judgement: yes, this note is a cost Roman sees, because each displaced add reads to him as a failure of rota.
5. Holds. 36 passed. Two tests were deleted. `test_a_clause_key_and_a_line_key_that_differ_are_refused_once` is replaced by `test_a_line_key_wins_over_a_clause_key_with_no_refusal`, which tests the opposite rule. `test_a_line_key_on_the_add_line_keeps_or_conflicts_with_the_add` (added in R3d) is replaced by `test_a_line_key_on_the_add_line_wins_and_the_add_is_noted`.
6. Outside: findings 2, 3 and 4.

## (b) Findings

1. rota/roles/api.py:14130-14162 against 14167-14168, high, CONFIRMED. The skip "a key on his question lands nothing" applies only to a clause with no lines. A question clause that names a line goes through the first branch and lands its option. Probe: "Is line 3 needed? The rest is fine." with `{"c1": "drop", "rest": "approve"}` was refused once, then landed l_1 as contest, drop, with the words "Is line 3 needed?". Also, `ASK_NOT_OPTION` fires once per session, so a second question in the same session lands with no refusal. Fix: skip `k in asks` before the `c["lines"]` branch, and skip a line key on a line in `ask_lines`.
2. rota/roles/api.py:13798 and 14173-14176, low, CONFIRMED. `_RIDES_WITH_ADD` does not hold `add`. So a line key `add` on `adds[0]` displaces a clause add of the same quote, and writes a fault row. Probe: c2 add and "2" add, both "The page leaves out the tax.", landed calculate_tip as approve, add, and wrote "line 2: the line key "2" gives add, and it displaced the add of clause c2". Fix: write no note when the two keys land the same `_OPTION_ROWS` row, as the lined branch does.
3. rota/roles/api.py:13850, low, PLAUSIBLE. A displaced add is a choice of the seat, not a fault of rota. A `faults` row puts it in the principal's "Rota itself failed" count, and a build frame must close it by hand. Fix: drop the fault row and let `tool_calls` keep the record, or give the note a kind that `render_state` does not count.
4. rota/roles/api.py:14133-14137 and 14146-14155, low, CONFIRMED by reading. The comment still says that two keys are "refused, once per line (pass R3c)". The read-back mapping now gates only the add note, and a read-back line offers no add. `test_two_keys_that_land_one_read_back_row_agree` asserts only the landed row, which the line key gives anyway, so it guards nothing of the mapping. Fix: correct the comment, and drop the mapping or make the test assert the note.

## (c) Probes

1. A plain-script probe of the `_page` and `_seat` helpers on a fresh `init_db` per probe. The pytest run from the scratchpad failed in collection on a temporary template path, so a runner script called each probe. Source: C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/00ca90d0-18a5-4929-b3d3-aedcb3b99ae5/scratchpad/p12b/test_p12b_probe.py, test_p12b_probe2.py and run_probe.py. Output: out.txt and out2.txt beside them. It ran the three shapes, add against add, add against approve, a question clause with a line, and `page_clauses` on two mixed replies at sizes 3 and 1.
2. `rota.tools.map table faults` and reads of the readers: principal.py:328, cockpit/server.py:165 and tools/faults.py.
3. `pytest tests/rota/test_r1_menu_form.py` in replay with `ROTA_MODEL=qwen3:8b` and `ROTA_L1` unset.
4. `git diff` of the tests between f8a591d1, bc5b5333 and 4fa8f775 for deleted tests.

## (d) Usage

About 33k tokens in total, above the 20k cap. About 26k were input and about 7k were output.

# Re-check p12c, pass R3f at f144bab1

Verdict: READY. No finding is high. Three findings are low.
The read used the worktree C:/Users/roman/rota_p12c at f144bab1, against 4fa8f775.
No live model, no `ROTA_L1=1` and no gate ran.
tests/rota/test_r1_menu_form.py passes in replay: 36 passed in 4.60s.

## (a) Verdicts on the points

1. Holds. A clause key on his question lands nothing, with or without a line. A line key on a line that only questions name lands nothing. Each refusal text names its clause and line, so each fires once per clause and line. The probe "Is line 3 needed? The rest is fine." with `{"c1": "drop", "rest": "approve"}` was refused once, then landed s1 and calculate_tip only. l_1 has no row. Two questions on lines 3 and 2 gave two refusals, then landed s1 only. A statement in its own clause still lands its line (finding 1 shows the merge limit).
2. Holds. `_displaced_text` and the `displaced` list are gone. The one `_stage_fault` call left in `_menu_page` (api.py:13843) is the old unheld-ref fault. Probe F, a clause add against a line key add on line 2, wrote no `faults` row. The test `test_a_line_key_on_the_add_line_wins_with_no_note` asserts `_faults(sb) == []` for a line key `other`.
3. Holds. The comment at api.py:14126-14131 now says that the line key wins with no refusal, and that `tool_calls` keeps both keys. `test_two_keys_that_land_one_read_back_row_agree` is gone. `_OPTION_SAME` stays live for `rest` and read-back rows (api.py:14067, 14229).
4. Holds. 36 passed in replay with `ROTA_L1` unset.
5. Outside: findings 1 to 3.

## (b) Findings

1. rota/roles/api.py:13990 with 14093-14112, low, CONFIRMED. The binder puts "Is line 3 needed? Drop line 3." in one clause, and the "?" makes the clause ask-only. So his explicit drop lands nothing. The seat repeated `{"3": "drop", "rest": "approve"}` after the one refusal, and the call landed with line 3 unruled. Then `rulings.rule(ask=...)` was refused: "this reply is already read: one ruling per reply". So the question is never asked and the line is never ruled in that reply. Before R3f the same call landed a drop. Fix: refuse the call while a line in `ask_lines` has a key, or let the landing send the ask for `ask_lines` itself.
2. rota/roles/api.py:14108-14110, low, CONFIRMED. The check `once in t` is a substring test. The text "clause c1 is his question" lies inside "line 3: clause c1 is his question". Probe G: a prior line-3 refusal muted the clause c1 refusal, and the call landed at once. Nothing landed on l_1, so the cost is one lost refusal. Fix: compare the text before ", so" for equality.
3. rota/roles/api.py:13834, low, PLAUSIBLE. `refused` holds all `rulings.rule` refusals of the Ctx, not of the ask. Probe E: a refusal "clause c1 is his question" already in the Ctx muted the refusal of a new page's clause c1. This matters only if one Ctx serves more than one reply. Clause numbers repeat per page. Fix: key the refusal text by the ask id, or clear the refusals per reply.

## (c) Probes

1. C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/00ca90d0-18a5-4929-b3d3-aedcb3b99ae5/scratchpad/p12c/probe_c.py, run by run_probe.py beside it on a fresh `init_db` per probe. Output: out.txt beside it. Shapes A to G: a question clause key, a line key on a question line, a merged question and statement, two questions, a prior refusal in the Ctx, a displaced clause add, a line refusal that mutes a clause refusal.
2. probe_r.py beside it: the merged reply keyed twice, then `rulings.rule(ask=...)`.
3. `api.page_clauses` on the two replies at size 3.
4. A grep of api.py for `displaced`, `_OPTION_SAME` and `_stage_fault`.
5. `pytest tests/rota/test_r1_menu_form.py -q` with `ROTA_MODEL=qwen3:8b` and `ROTA_L1` unset.

## (d) Usage

About 40k tokens in total, above the 15k cap. About 33k were input and about 7k were output.
