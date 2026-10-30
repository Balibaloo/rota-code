# Review p1 of frame 347 pass 1 at fa7ec9a3 (2026-10-30)

Verdict: LAND. No high. Three lows. The reach is exactly three references on the 41 replies.

## (a) Verdicts on the points

1. K0: PASS. All four probe shapes give the expected parts, and the caller blanks a quoted comma first.
2. F-in: PASS. "line 3 of utils.py" stays unbound, and that is right, because it names a code line.
3. The reach: PASS. Exactly three clauses change: n170-m6-m7 line 29, M63 line 6, M246 lines 2 to 4.
4. The re-pins: PASS. Each test keeps its old assertions, and `_rule_m245` adds one stronger assertion.
5. The tests: 2 red, 103 pass, 1 xfail. The same 2 reds are red at 676ebde1.
6. Outside: three lows, findings 1 to 3.

## (b) Findings

1. K0 has no code place guard. Severity low. CONFIRMED.
   - File: `rota/roles/api.py` 13420 (`_COMMA_REF` branch of `_subject_parts`).
   - Probe: "The traceback points at src/click/termui.py, line 4 raises" binds page line 4.
   - Probe: "The bug is in cli.py, line 5 of it" binds page line 5.
   - The "on" rule and F-in both refuse a reference after a path. K0 does not. No case of the 41 has this shape.
   - Fix: add `and not _CODE_PLACE.search(before.rstrip(" ,"))` and `not _CODE_AFTER.match(clause, end)` to the K0 branch.
2. A K0 part drops an F-in or an "on" binding in the same clause. Severity low. CONFIRMED.
   - File: `rota/roles/api.py` 13439-13440 (`if not named and not starts`).
   - Probe: "The tests in lines 2 to 4 are wrong, line 6 too" gives [{6}] only. Lines 2 to 4 bind nothing.
   - At 676ebde1 the same clause binds nothing at all, so this is no regression. It is a gap the new rules leave.
   - Fix: when `named` is empty, give the first part `placed or inside`, whether or not `starts` holds a part.
3. The K0 part can lose its verb, and "so" widens K0 past the read. Severity low. PLAUSIBLE.
   - File: `rota/roles/api.py` 13340 (`_COMMA_REF`).
   - Probe: "lines 1 and 2 are right, and line 4 too" gives the part "line 4 too". The part holds no verdict word.
   - Probe: "Remove lines 7 and 8, so line 2 stands alone" binds line 2. The read of 1.2 says that line 2 of m116-m118 names an older page and must stay unbound.
   - The 41 replies hold neither shape, so the measure cannot show either one.
   - Fix: allow "and" or "but" only, or measure "so" before the next pass. Track the verbless part in the menu text.

Notes on the points, not findings:

- Point 2: `_CODE_AFTER` reads a path or a code name only. "line 3 of the function" still binds line 3. This is acceptable, because "the function" is no code name the guard can see.
- Point 4: `test_s291s` keys `"8": "ask"` now. The refusal `ASK_NOT_OPTION` and the named-call landing are the same claims as before. F-in now makes a question clause, "what does the retry in line 8 mean", a line key. The 41 replies do not cover that shape. The implementer reported it as deviation 2.
- The `rfind` cut is safe for a bare list. `_bare_subject` returns lines only after a comma, so `rfind` always finds the comma of the part.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/00ca90d0-18a5-4929-b3d3-aedcb3b99ae5/scratchpad/`.

- `p347/reach_diff.py`, run against `D:/repos/rota` (rota and tests equal 676ebde1) and `C:/Users/roman/rota_f347r`. Output `p347/rv_head.txt` and `p347/rv_new.txt`, 159 lines each, 3 lines differ.
- `p347r/pt12.py`: 16 clauses through `_QUOTED` blanking and `_subject_parts`, size 10, at the commit.
- A `python -c` probe: 4 clauses of bare lists beside K0 and "of the function".
- `ROTA_MODEL=qwen3:8b pytest` with `ROTA_L1` unset on the four named files, in the worktree and in `D:/repos/rota`. Commit: 2 failed, 103 passed, 1 xfailed. Head: 2 failed, 92 passed, 1 skipped, 1 xfailed. The reds at both: `test_a_row_on_two_lines_of_the_page_lands_a_word_on_each` and `test_two_words_on_one_ref_of_another_act_keep_one_row`.
- Worktree: `C:/Users/roman/rota_f347r`, detached at fa7ec9a3, with `cassettes.db` copied in.

## (d) Usage

Input about 45k tokens. Output about 7k tokens. Total about 52k. The cap was 20k. Most of the excess is the diff, the read sections and the implementer's report.
