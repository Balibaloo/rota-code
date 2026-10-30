# Review p4: frame 347 pass 4 at a00c99c8

Worktree `C:/Users/roman/rota_f347r`, detached at a00c99c8. Read-only. No live model, no gate.

## (a) Verdict

Pass with lows. No high finding.

1. Point 1: pass with one low. The three sentences are brief text. No code reads his words with them. `landing.md` has 45 lines. The sentence bodies in `landing.md` and in `_TOUCH_WHEN` agree word for word. Only the joint before the example differs: ":" in the brief, "as" in the menu. Each sentence is a rule on what his words say about a shown file. The `approve` sentence is the nearest to a verb rule, because it uses "keep" (finding 4). The `approve` and `exclude` sentences overlap on a line with two or more files (finding 2).
2. Point 2: pass. `page_menus` writes `when` at api.py 14000-14003, only on a touch entry with more than one option. The wake shows it through `landing["menus"]` at runner.py 2508 and 2515. `rulings.rule` reads `page_menus(...)[1]` at api.py 14157. That is `per_line`, and the diff does not change it. The probe confirms that `per_line` has no `when`.
3. Point 3: pass with two lows. The comment marks the words as "test words, not his". The call lands the old claim: `KEY` contest, `ITEM` approve. The skip reason cites api.py 14308, but the refusal is at api.py 14332-14333 (finding 1). The re-pin excludes one file of the two that the words refuse (finding 3).
4. Point 4: pass. The run had `ROTA_L1` unset. The three named files and `test_frame234_verdict_lines.py` gave 118 passed and 1 skipped.
5. Outside the points: the key `exclude <path>` matches no option string on the menu, because the options carry real paths. Nothing breaks, because no code reads `when`. The brief explains the template.

## (b) Findings

1. `tests/rota/test_frame234_verdict_lines.py` 469-473. Low. CONFIRMED. The skip reason names "api.py 14308". At a00c99c8 line 14308 holds the `home` assignment of the quote branch. The raise of "no clause of his names line" is at 14332-14333. At 2c0c7c75 it was at 14313-14314. A line number in a reason goes stale on the next edit above it. Fix: cite `rulings.rule` and the refusal text, not a line number.
2. `rota/roles/api.py` 13842-13847 and `landing.md` 18-19. Low. PLAUSIBLE. A touch line can show files A and B. If he says "change only the docstring in A", `approve` fits ("put the change in one of them"). `exclude B` also fits ("also when he names where the change goes"), because B is then not part of the change. The m121 case had one shown file on line 9, so the measured cases do not show the overlap. Fix: let `approve` hold when every shown file stays in the change, and let `exclude` take the files that his place leaves out.
3. `tests/rota/test_guess_page.py` 273-274. Low. CONFIRMED. The words say "the options and defaults test files ... have nothing to do with this change". The call keys only `exclude tests/test_options.py`. Under the new `exclude` sentence the seat keys both paths. The assert on `KEY` contest holds with one path, so the test does not pin the full reading. Fix: key `exclude tests/test_options.py, tests/test_defaults.py` and assert both exclude rows.
4. `rota/roles/api.py` 13840 and `landing.md` 17. Low. PLAUSIBLE. The `approve` sentence says "his words keep the shown files". In m76-m77 he writes "keep line 5 to the terminal module", and the case expects `exclude`. M192 writes "keep the work to version option". A seat that matches the word "keep" picks `approve` in an exclude case. Fix: write "his words accept the shown files" and do not use "keep".

## (c) Probes

1. `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/00ca90d0-18a5-4929-b3d3-aedcb3b99ae5/scratchpad/p4probe/test_p4probe.py`. It calls `api.page_menus` on order `guess:calculate_tip, l_1` with the page "1. The change touches: src/a.py". Result: the touch entry carries `when` with three keys. The other entry carries no `when`. `per_line` carries no `when`. Each sentence body of `_TOUCH_WHEN` occurs in `landing.md`. The key `exclude <path>` is not an option string.
2. A pytest run with `ROTA_L1` unset and `ROTA_MODEL=qwen3:8b` on `test_r1_menu_form.py`, `test_guess_page.py`, `test_seam_permission_readers.py` and `test_frame234_verdict_lines.py`. Result: 118 passed, 1 skipped.
3. grep for the refusal text at a00c99c8 (line 14333) and at 2c0c7c75 (line 14314).
4. A print of the M192 tail from `tests.rota.test_guess_route`.

## (d) Usage

Input tokens: about 31,000, including the system context. Output tokens: about 4,000. Total: about 35,000. This is above the 15k cap. Most of the excess is the fixed system context.
