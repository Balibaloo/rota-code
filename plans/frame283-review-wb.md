# Frame 283, W-B review: the positional keep on a grown count (24523db3)

Verdict: does not stand as is. The night's wall is fixed, but a true removal now passes a span write silently when the owner also grows.

## (a) The points

1. Holds. The night's five spans and the whole-file write give no note, and three sandbox span writes plus one whole-file write commit.
2. Fails in one shape. `log(x)` dropped before `log(x, 2)`, plus two added statements, now opens no note. See finding 1.
3. Holds. `log(x)` dropped before `log(x, 2)` with no add is noted. `validate(x)` to `print(x)` plus `stop(x)` is noted.
4. Holds. Of 93 night spans, 1 changes: 5bac8625 `clear`, the W-B rewrite. No true drop loses its note.
5. Holds. 198 passed. The commit adds 54 test lines and deletes none, so no assertion is weakened.

## (b) Findings

1. `rota/roles/api.py:22210`, `if count[o] > len(placed[o])`. High. CONFIRMED. Old `[log(x), log(x, 2)]`, new `[log(x, 2), z(), w()]`: bc16c86d names `log(x)`, 24523db3 gives None. A removal shifts `log(x, 2)` into index 0, and its tokens hold `log(x)`. Any added statement in the owner now hides the drop that pass 8c closed. The pins miss it because E8 adds nothing.
   Fix: on a grown count, do not pair index i when the next old statement of the owner also fits new[i].
2. Same line. Low. CONFIRMED. These shapes now pair as rewrites: `a(x)` to `log(a, x)` plus `c()`, and bare `return` to `return y` plus `stop()`. Each new line holds the old tokens. Both read as rewrites, so the change is acceptable.
   Fix: none. Record the shapes as accepted.
3. `rota/roles/api.py:21971`, `if gone and all(i in kept for i in gone)`. Low. PLAUSIBLE. The grown keep feeds this test, so the shift of finding 1 can also clear a tail note. No probe ran on a tail shape.
   Fix: probe a tail drop with an added statement after the fix of finding 1.
4. Outside the points. `tests/rota/test_frame283_rewrite_not_removal.py`, the removal-beside-an-add test. Low. CONFIRMED. The test passes on bc16c86d and on 24523db3, so it does not pin the new rule.
   Fix: add the shape of finding 1 as a pin that requires the note.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/79847ec6-3334-49c7-8221-098d6165a403/scratchpad/`.
- `r283wb_sandbox.py`: it runs `probe165wb.py` against `rota_r283wb`. Then it runs `code.write` and `code.commit` on `termui_base.py` in a git sandbox, for spans 600-613, 601-613, 601-615 and a whole file.
- `r283wb_shapes.py`: it runs `_drop_note` on 12 shapes. The new rule runs, and the parent rule runs through a copy with `!=` put back.
- `r283wd/p7.py` with `r283wb_p7/` (parent `api_old.py`, `shas.txt`): 93 clickI night spans, parent against 24523db3.
- Pytest: every `test_frame283_*.py` and `test_frame140_*.py` file, and `tests/rota/test_developer.py`. Result: 198 passed in 194 s.

## (d) Usage

About 45k input tokens and 9k output tokens, about 54k in total.

Does not stand.
