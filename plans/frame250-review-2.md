# Frame 250, review 2: pass 1b at d3154135

Verdict: accept. Review 1's high is fixed. The guard spares only a merged or abandoned change's line, and m245 line 6 is refused. The count reproduces 7 of 177. No high finding. Three low findings, all outside the pass's diff or carried. Reviewed on the worktree `C:/Users/roman/rota_r250b` at d3154135, 2026-10-16.

## (a) Verdicts on the points

1. PASS. (a) An open change's line is refused: the m245 tests and my probe show it. (b) A merged or abandoned change's line lands: no test covers it, and my probe lands it end to end. (c) The m85 text line stays spared: the three m85 tests are green, and my probe on `_faulted_approve` returns None.
2. PASS with one low. The request refusal wins only when its four guards pass. On night 133's s313 shape it names both lines, and one call lands. On the m245 family it does not fire, and line 1 alone escapes (finding 1).
3. PASS. m255 and m260 each approve bg_4's line 6, running, against "Line 6 is still wrong". Both are wrong approves. The re-run from the worktree prints 177 verdicts, fires on 7.
4. PASS. At a `git archive 0865fe13` copy with the new test file: 2 failed, 11 passed, 1 xfailed. The two reds are the two m245 refusal tests. At d3154135 all four m245 tests pass.
5. PASS. The mark is `strict=True, raises=pytest.fail.Exception`. With `--runxfail` the test fails by "Failed: DID NOT RAISE <class 'ValueError'>". Without it, the test reports XFAIL.
6. PASS. The `_unnamed_contest` docstring at api.py 8757 says "the item of a merged or abandoned batch's line counts as named". Pass 1 fixed it at f0b2924c, not pass 1b.
7. PASS. `_ref_lines` at api.py 8542 takes `re.I`. `_WORDS_FAULT` at api.py 5089 takes "through" and "-". Pass 1 fixed both at f0b2924c. Pass 1b did not touch them, and need not.

## (b) Findings

1. `rota/roles/api.py:8688` (the request refusal's guard on a sentence with no line number). Severity low. CONFIRMED. All three night 145 replies open with an unnumbered sentence, "Please don't give up on this change". So a map that contests line 1 and approves line 6 gets the approve refusal, which names line 6 alone. The probe then contested lines 1 to 4 and 6, and the ruling landed with the item contested. That contest cancels the work the words ask to keep. No night 145 map contested line 1, so no recorded shape holds it. The guard predates pass 1b (m263, frame 234). Fix: let `_BARE_AGREEMENT` or a keep-going pattern ("don't give up", "keep going", "don't drop") pass the unnumbered-sentence guard.
2. `rota/roles/api.py:8678` (the request refusal names `faulted`, not the lines `_faulted_approve` keeps). Severity low. CONFIRMED by a direct probe on `_line_refusal`. With night 136's m85 words and line 1 contested, the refusal says "Rule line 2, and approve the rest". The seat that follows contests text line 2 and approves bg_2 on line 5, and the ruling lands. m85's right map contests line 5, the batch line (`test_request_page.py`). The files correction is then lost. The text predates pass 1b, and no night map contested line 1 on m85. Fix: in the request refusal, name a batch line in place of a text line that the `_TOUCH_WORDS` guard spares.
3. `count_present_1b.py` and `_faulted_approve`'s docstring (the batch status at the night's end). Severity low. PLAUSIBLE. The count spares night 146's m162 line 5 because bg_4 is abandoned at the night's end. bg_4 can have been open at the ruling. Then the door fires on 8, and m162 holds two faulted lines. The pass report names this as its open question 1. Fix: night 150's read labels each batch-line fire with the batch status at the ruling's sequence.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/738ddbaf-1cc4-48f9-9414-01f5058ba1fb/scratchpad/f250/r2/`.

- Worktree run: `test_frame250_verdict_faults.py`, `test_park_page.py`, `test_request_page.py` and `test_frame255_files_correction.py`. Result: 145 passed, 5 xfailed.
- `probe_fa.py`: `_faulted_approve` direct. m85 text line with a batch line on the page: None. The same with no batch line: refused. An open batch line with touch words: refused. The same line in `closed_lines`: None. A text line with touch words beside an open batch line: only the batch line is named.
- `test_r2_closed.py`: the m245 fixture, run from the worktree. With bg_4 merged or abandoned, the night map is refused for line 4 alone. With line 4 contested, the map lands with bg_4 approve. Line 1 contest plus line 6 approve: refused for line 6 alone. Lines 1 to 4 and 6 contested: the ruling lands with the item contested.
- `probe_l1.py`: `_line_refusal` with m85's words and line 1 contested gives "Rule line 2". With line 2 contested and line 5 approved, it returns None.
- `db145.py`: `.rota/clickI_night145.db` read with `mode=ro`. Rulings r_f38b69e7c3, r_c8757431e3 and r_58c63355f6 on m245, m255 and m260 each rule bg_4 approve. Each reply's words equal the ruling's words. bg_4 is running at head 04d4368f at the night's end.
- `count_present_wt.py`: `count_present_1b.py` with the import path set to the worktree. Output: 177 verdicts, fires on 7, the seven the pass names.
- `old/`: `git archive 0865fe13` with the test file from d3154135. `api.py` is byte-equal to 0865fe13. Result: 2 failed, 11 passed, 1 xfailed.
- The m81 test with `--runxfail`: "Failed: DID NOT RAISE". Without it: 1 xfailed.
- The gate was not run. No point needs it, and the pass report shows no new red at the rulings door.

## (d) Usage

The harness line is not visible to me. Estimate: about 75k input, 9k output, about 84k in total, against the 40k cap. Read the harness line for the true number. Sub-agents: none.
