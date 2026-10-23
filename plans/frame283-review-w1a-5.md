# Frame 283, review 5 of pass 4b at 599b72e4

Agent: Opus, read-only, 2026-10-23. Worktree `C:/Users/roman/rota_r283` at 599b72e4, parent cbdc68f8.

Verdict: accept for the branch. Do not close the frame. Pass 4b closes review 4's F1 to F3, and the night exposure stays zero. The request clause still runs past "and" before a verb, past a comma before a verb, and past a locator word. So a keep shape of that form still admits the removal of the kept line (F1, F2).

## (a) The claim, point by point

1. Met. Review 4's probe S at 599b72e4: all 13 shapes of group P1 and all 8 of group P4 stay right. All 8 of group X are right now, and 6 of them were wrong at cbdc68f8. F1, F2 and F3 of review 4 are closed.
2. Partly met. Three of the four named shapes admit `ctx.exit()`, and only one is right. "drop X and keep Y" refuses Y, which is right. A rule that ends the clause at "and" before a non-removal verb is right on the 141 night sentences. 13 request clauses hold "and" after the verb. 5 have "and" before a verb, and each next clause asks for no removal. 8 join nouns, and a verb rule leaves them whole.
   - "Remove the echo and make sure ctx.exit() runs." admits `ctx.exit()`. Wrong.
   - "Remove echo(message) and ctx.exit()." admits both. Right.
   - "Remove echo(message) and then call ctx.exit()." admits `ctx.exit()`. Wrong.
   - "Drop echo(message) and keep ctx.exit()." admits the echo and refuses `ctx.exit()`. Right.
   - The 5 verbs after "and" on the nights are "add" (2), "put", "just say" and "say".
3. Met, with one note. The diff is two files. The code hunks are `_CLAUSE_END`, `_outside_code`, `_breaks`, `_removal_spans`, `_removal_asked` and `_asks_removal`. The test hunks are the two new tests of the pass report. `_asks_removal` has one caller, `_unruled_gone`. `_removal_asked` now has no caller in `rota/` or `tests/` (F4).

## (b) Findings

1. **The request clause runs past "and" and past a comma before a verb.** `rota/roles/api.py:17556-17560` (`_CLAUSE_END`). Low for the night, high for the frame. CONFIRMED.
   - Probe A: "Remove the echo and make sure ctx.exit() runs." admits `ctx.exit()`.
   - The same holds for "and then call", "and call ... instead", "and ensure", "and move", "and check that", "and test" and "and make".
   - Probe M: "Drop echo(message), call ctx.exit() last." admits `ctx.exit()`. A comma ends the clause only before a closed word list.
   - Probe M: "Please drop line 1, rewrite line 3 in plain words." admits line 3.
   - These are keep shapes of the class that review 4's F1 named. Probe N finds no night sentence that the cut would move to the wrong side.
   - Fix: end the clause at "and", "and then" or a comma before a non-removal imperative verb of a closed list.
2. **A locator word or an exception word inside the request clause admits the named line.** `rota/roles/api.py:17626-17648` (`_asks_removal`). Low for the night, high for the frame. CONFIRMED.
   - Probe A and probe M admit `ctx.exit()` on each of these:
     - "Remove the line above ctx.exit()."
     - "Remove echo(message) before ctx.exit()."
     - "Remove the echo next to ctx.exit()."
     - "Remove echo(message) instead of ctx.exit()."
     - "Remove echo(message) rather than ctx.exit()."
     - "Remove echo(message) except ctx.exit()."
     - "Remove echo(message), not ctx.exit()."
   - cbdc68f8 admitted the same, so the class is not new.
   - A model that misreads "the line above X" and deletes X is the failure this guard exists for.
   - Fix: match the name only before the first locator or exception word of the clause: above, below, before, after, next to, near, instead of, rather than, except, not, that, which.
3. **"Remove X, and Y too" now refuses Y.** `rota/roles/api.py:17557`. Low for the night, low for the frame. CONFIRMED.
   - Probe S, group P3: "Please remove ctx.exit(), and echo(message) too." admits `echo(message)` at cbdc68f8 and refuses it at 599b72e4.
   - The comma before "and" ends the clause for every next word.
   - The error is on the safe side. The seat gets a refusal for a removal that the principal asked for.
   - Fix: end at ", and" only before a verb or a keep word, the same list as F1.
4. **`_removal_asked` has no caller.** `rota/roles/api.py:17620-17623`. Low for the night, low for the frame. CONFIRMED.
   - The map prints "callers (0)". Only the pass's count script in the scratchpad calls it.
   - Fix: delete it, or name it in the docstring as the per-sentence count hook.

Outside the points: none found. The pronoun reach is right on 6 keep shapes of probe M, for example "Do not touch ctx.exit(), the echo is dead, remove it." refuses.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/1b2c3f89-168f-4708-a241-5ecb0a745d11/scratchpad/r5/`. Each ran with `D:/repos/rota/.venv/Scripts/python.exe` against `C:/Users/roman/rota_r283`. `api_p4.py` is `git show cbdc68f8:rota/roles/api.py`.

- S: review 4's `r4/r4_shapes.py`, re-run with `r5/api_p4.py` as the old rule. Every row of groups P1, P4 and X is right. Group P3 shows F3.
- A, `r5_and.py`: 38 shapes with `ctx.exit()` and `echo(message)` as the gone line, at cbdc68f8 and at 599b72e4, with the request clauses printed.
- M, `r5_more.py`: 13 shapes of comma lists, pronoun reach and locators at 599b72e4.
- N, `r5_nights.py`: nights 140 to 158, read-only with `?mode=ro`. It rebuilds the 141 sentences of the pass's count. 60 admit. 81 hold "and". 13 request clauses hold "and" after the removal verb, and the probe prints each one.
- T: `tests/rota/test_frame283_removal_on_ruling.py` and `tests/rota/test_frame140_commit_beside_note.py` with `-n 0`, 88 passed.
- D: `git diff cbdc68f8 599b72e4`, read hunk by hunk. The map and `git grep` find the callers.

## (d) Usage

- Input: about 40k tokens of context at the end. The harness gives no exact split.
- Output: about 7k tokens.
- Total: about 47k tokens, against a cap of about 25k.
