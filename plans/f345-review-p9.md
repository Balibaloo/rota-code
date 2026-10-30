# Frame 345, review p9: R1 (e810eb77) and R1b (3a09a36f) on r1root

Verdict: NOT READY. One high finding and five low findings. The rest key approves a line that his clause contests.

## (a) The verdict on each point

1. Partly. The ruled line lands the same verdict, act, target_kind and target by both keys. The approved lines differ in `words` (finding 2).
2. Yes. A call `{"rest": "approve"}` lands approve on the line that his clause drops (finding 1).
3. The builder's list is wrong. Only three cases went right to wrong, and the R1b input caused each one (finding 5).
4. The prompt is the cause. The menu offers drop on both lines, and one clause names both lines (finding 4).
5. Confirmed. Both tests fail at 49dcb976 and at 3a09a36f.
6. Two expected rulings have no option: `approve, add` on the `how_it_works` line in n174-m47-m48 and n175-m75-m76 (finding 3).
7. No old door runs on the menu path for a dict `rulings`. MENU_PAGES defaults to True in production and in the gate. The switch is off for 700 tests in 22 modules, not 198 (finding 6).
8. 40 lines, and it names rest, the lines correction and ask. It teaches two forms, and its example is a measured case (finding 4).

## (b) Findings

1. rota/roles/api.py:14685 and 14697. High. CONFIRMED. With DROP = "Drop line 3, because nobody types the percentage. The rest is fine.", the call `{"rest": "approve"}` landed l_1 as approve with no act. `{"1": "approve", "rest": "approve"}` did the same. R1b skips the `missing` check when the seat gives rest. R1b also lets rest approve a read-back line that his words name. Fix: compute `missing` always, and exempt only the lines of a clause whose words match `_REST_LINES`. The plain form `{"3": "drop", "rest": "approve"}` then still lands.
2. rota/roles/api.py:14699. Low. CONFIRMED. `{"c1": "drop", "c2": "approve"}` gives s1 the words "The rest is fine.". `{"3": "drop", "rest": "approve"}` gives s1 his whole reply. Fix: in the rest loop, set `shape_of[ref] = {"words": span_of.get(n, his)}`.
3. rota/roles/api.py:14353 with 14414. Low. CONFIRMED. A seeded probe of the 24 cases ran `menu_kind` on each expected line. Two misses: line 1 `how_it_works` is kind other, and the cases expect `approve, add`. Both cases fail at R1b. Fix: offer `add <quote>` on the `how_it_works` line, or give the line the request menu.
4. rota/roles/prompts/liaison/landing.md:22 and 28. Low. PLAUSIBLE. The prompt teaches the line key and then the clause key, so it teaches two forms. Its example is L3R-n173-m34-m35, a measured case, and that case went right to wrong. In L1-LI-drop-both-examples, `page_clauses` gives one clause with lines [1, 2], and the menu offers drop. The seat keyed each line and chose rewrite for line 2 in runs 1 and 3. R1 asked for one option per clause. Fix: teach the clause key as the one form, with an example from outside the measured cases.
5. r1b_report.md line 5. Low. CONFIRMED. The R1 log fails n170-m58-m59 and n174-m53-m58 at 1/3 each, so they were wrong at R1 too. n175-m116-m118 was right at R1. The true flips are three each way. Right to wrong: n172-m92-m93, n173-m34-m35, n175-m121-m122. In each case turn 1 differs between the logs at temperature 0. So the R1b input caused each case, not the timing of a refusal. n172-m92-m93: the seat chose add, then other, where R1 chose exclude. n173-m34-m35: the seat put `misread, drop` on clause c4, then swapped lines 7 and 8. n175-m121-m122: run 3 landed at once with lines 2 and 9 contested. R1 refused the line key "7", and R1b accepts it. Fix: correct the report, and record R1b a second time before R2 reads the counts.
6. tests/rota/conftest.py:319 and 22 test modules. Low. CONFIRMED. `pytestmark` sets `old_page_form` for each whole module, 700 tests by `--collect-only`. Only test_r1_menu_form and the unmarked modules run the menu form and the `landing.clauses` payload. Fix: mark only the tests that call the word form, and let the rest run with MENU_PAGES True.

Outside the points: an empty or non-dict `rulings` on a page skips the menu branch (api.py near 14851). The call then reaches the word-form doors and their refusal text. PLAUSIBLE, low. A `lines` correction on a line key is silently dropped. PLAUSIBLE, low.

## (c) Probes

- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/68459b4f-6e2b-4299-b66e-6ca5ca44f7fd/scratchpad/p9/test_p9_probe.py: pytest on the `_page` and `_seat` fixtures. It runs the clause key, the line key with rest, all line keys, rest only, line 1 with rest, and line 1 with no rest.
- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/68459b4f-6e2b-4299-b66e-6ca5ca44f7fd/scratchpad/p9/menus_probe.py: it seeds each L3 case and checks each expected row against the menu of `menu_kind`. The result: 2 misses.
- `api.page_clauses` on the drop-both reply, size 2. The result: one clause, lines [1, 2].
- `git archive 49dcb976` into scratchpad/p9/parent, then the two test_read_back tests there and at 3a09a36f. Both fail at both commits.
- A grep of r1_after.txt and r1b_after.txt for the FAILED lists, the turn-1 refusals and the assertion details.
- `pytest --collect-only` on the 22 marked modules. The result: 700 tests.

## (d) Usage

Input tokens: about 85k cumulative. Output tokens: about 9k. Total: about 94k. These are estimates. The harness gives no exact count.

## p9b: R1c (db0b25ee on r1root, built on 3a09a36f)

Verdict: NOT READY. There are two high findings. Counts at R1c: L3 16 of 24, runs 47 of 72, 49 refusals, landing 9 of 12.

### (a) The verdict on each point

1. F1, F2, F3 and F4 are closed. A probe closes each one.
   - F1 and F2: `{"rest": "approve"}` and `{"1": "approve", "rest": "approve"}` are now refused, with "line 3: his words name the line". The rest lines now carry "The rest is fine." as their words.
   - F3: `line_menu` on `how_it_works` in n174-m47-m48 and n175-m75-m76 gives `approve; add <quote>; drop; rewrite; other <quote>`.
   - F4: landing.md has 39 lines. It teaches the line key alone, and a grep finds its example in no case file.
2. The cause is the form, not the F1 fix and not the prompt. In runs 2, 4 and 5 the seat sent `{"1": "approve", "2": "approve", "3": "rewrite", "rest": "none"}` and repeated it. The code refused it with "lines 1, 2 have no ruling" and wrote no ruling. Runs 1 and 3 sent `rest: approve` and passed. CONFIRMED (finding p9b-1).
3. All 27 refusals carry `"rest": "none"`, and the seat keys the reported lines `approve` itself. The seat left out no line. The form is the cause. CONFIRMED (finding p9b-1).
4. The first deviation is safe because it refuses and lands nothing. The second deviation is unsafe. A quote of the clause that names line 3, keyed on line 1 as `other`, lands a contest on line 1. CONFIRMED (finding p9b-2).

### (b) Findings

- p9b-1. rota/roles/api.py:14608. High. CONFIRMED. The reply was "Drop line 3." and the call was `{"1": "approve", "2": "approve", "3": "drop", "rest": "none"}`. The call was refused with "lines 1, 2 have no ruling ... give those lines a key". A line key `approve` on a line that no clause names takes `continue`, so the line gets no ruling. The refusal then asks for the key that the seat gave, so the seat repeats its call. Fix: a line key with approve or ok on a line that no clause names lands approve with his whole reply as the words.
- p9b-2. rota/roles/api.py:14611. High. CONFIRMED. The reply was "Drop line 3." and the call was `{"1": "other \"Drop line 3.\"", "3": "drop"}`. s1, which is line 1, landed `contest` with the words "Drop line 3.". `_holds_span` checks only that the quote is in his reply. The check does not ask whether the quote names a different line. This breaks law 6: the row carries his words, but the line is the seat's choice. Fix: take the quote on an unnamed line only when the quote lies inside a clause with no lines.

### (c) Probes

- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/68459b4f-6e2b-4299-b66e-6ca5ca44f7fd/scratchpad/p9/test_p9_probe.py: run again at db0b25ee.
- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/68459b4f-6e2b-4299-b66e-6ca5ca44f7fd/scratchpad/p9/test_p9b_probe.py: the approve keys with `rest: none`, and the `other` quote on line 1.
- `line_menu` on the seeded n174-m47-m48 and n175-m75-m76.
- A read-only query of tests/rota/cassettes.db `case_runs` (Gemma, at or after 2026-10-29T12:00): the named-line transcripts, and the calls of the 27 refusals from 72 L3 runs.

### (d) Usage

Input tokens: about 60k cumulative for p9b. Output tokens: about 5k. Total: about 65k. These are estimates.

## p9c: R1d (57e0cfb5 on r1root, built on db0b25ee)

Verdict: NOT READY. One high finding stays open. Counts at R1d: L3 17 of 24, runs 51 of 72, 27 refusals, landing 10 of 12.

### (a) The verdict on each point

1. p9b-1 is closed. CONFIRMED. For the reply "Drop line 3.", the call `{"1": "approve", "2": "approve", "3": "drop", "rest": "none"}` now lands lines 1 and 2 approve and line 3 drop.
2. p9b-2 is not closed. CONFIRMED. The first `{"1": "other \"Drop line 3.\"", "3": "drop"}` is refused. The same call a second time lands s1, which is line 1, as `contest` with the words "Drop line 3.".
3. The question: the deviation is safe. A line key approve on a read-back line that no clause names lands no row. The `left` check skips read-back lines, so the call is not refused. The rest also skips a read-back line outside the rest clause. So the line stays out, as the seam design's review, finding 1, ruled. PLAUSIBLE, from reading api.py near 14608 and the `left` check.

### (b) Findings

- p9c-1. rota/roles/api.py:14635. High. CONFIRMED. The refusal for a change on an unnamed line fires once per session. On a repeat, the code sets the span to his whole reply and lands the option. The new quote check (14611) therefore only delays the landing by one call. Line 1 gets a contest that his words do not hold, and that breaks law 6. Fix: refuse a change on a line that no clause names on every call, unless the quote lies inside a clause with no lines.

### (c) Probes

- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/68459b4f-6e2b-4299-b66e-6ca5ca44f7fd/scratchpad/p9/test_p9b_probe.py: run again at 57e0cfb5. The approve keys land. The first quote call is refused.
- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/68459b4f-6e2b-4299-b66e-6ca5ca44f7fd/scratchpad/p9/test_p9c_probe.py: the same quote call twice in one session. The first call is refused, and the second call lands contest on line 1.

### (d) Usage

Input tokens: about 25k for p9c. Output tokens: about 2k. Total: about 27k. These are estimates.

## p9d: 1141b441 on r1root, built on 57e0cfb5

Verdict: READY for the land. No finding stays open.

1. p9b-2 and p9c-1 are closed. CONFIRMED. test_p9c_probe.py sends the same quote call twice. Both calls are refused, and nothing lands on line 1.
2. The fix is at rota/roles/api.py:14634. The refusal for a change on an unnamed line now fires on every call, and the fallback to his whole reply is gone.
3. p9b-1 stays closed. CONFIRMED. test_p9b_probe.py landed the approve keys with `rest: none` and refused the first quote call.

Probes: C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/68459b4f-6e2b-4299-b66e-6ca5ca44f7fd/scratchpad/p9/test_p9c_probe.py and C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/68459b4f-6e2b-4299-b66e-6ca5ca44f7fd/scratchpad/p9/test_p9b_probe.py, run at 1141b441. 3 passed.

Usage: about 8k input tokens and 1k output tokens for p9d, about 9k in total. These are estimates.
