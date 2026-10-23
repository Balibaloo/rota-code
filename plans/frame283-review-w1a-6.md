# Frame 283, review 6 of pass 4c at d7ddfb00

Verdict: accept for the branch. Do not close the frame. Pass 4c closes F4 fully. Pass 4c closes most of F1 and F2. Five probe sentences stay on the wrong side, and each one admits the removal of a kept line. The night exposure stays zero.

## (a) The claim, point by point

1. Partly met. F4 is closed. F1 and F2 are closed for every sentence the pass tested. The verb list and the position-word list are short, so five sentences of review 5's own scripts still admit `ctx.exit()` (F1, F2 below).
   - Wrong side in `r5_and.py`: "Remove echo(message) and ensure ctx.exit() still runs.", "Remove echo(message) and move ctx.exit() to the end.", "Delete echo(message) and test ctx.exit().".
   - Wrong side in `r5_more.py`: "Remove echo(message), move ctx.exit() to the end.", "Remove the echo that ctx.exit() follows.".
   - Safe side, known as review 5's F3: "Please remove ctx.exit(), and echo(message) too." refuses `echo(message)`.
   - All other rows of the two scripts are right. 25 rows that admitted `ctx.exit()` at cbdc68f8 now refuse it.
2. Met. The diff is two files, `rota/roles/api.py` (+18, -11) and `tests/rota/test_frame283_removal_on_ruling.py` (+39). The code hunks are `_NEXT_VERBS`, `_CLAUSE_END`, `_NOT_TARGET`, the clause end in `_removal_spans`, and the deletion of `_removal_asked`. The test hunks are the three tests of the pass report. `_removal_asked` had no test of its own. `git grep` at 599b72e4 finds it only at its definition and in review 3's text. No test is gone and no test is re-pointed.

## (b) Findings

1. **The verb list misses common next verbs, and an adverb before a listed verb defeats it.** `rota/roles/api.py:17559-17560` (`_NEXT_VERBS`). Low for the night, high for the frame. CONFIRMED.
   - Probe A: "and ensure", "and move" and "and test" admit `ctx.exit()`. Probe M: ", move ctx.exit() to the end" admits it.
   - Review 5's F1 named "ensure", "move" and "test". The pass did not add them.
   - Probe N: night 152 "drop ... and just say confirm prompts as usual" runs on past "and just say". No line is named there, so no side changes.
   - A closed list of fifteen verbs does not generalise. Each missed verb is the keep shape the guard exists for.
   - Fix: end the clause at "and", "and then" or a comma before any word that is not an article, a determiner or a code name, or widen the list and allow one adverb before the verb.
2. **"that" does not end the target part.** `rota/roles/api.py:17570-17572` (`_NOT_TARGET`). Low for the night, high for the frame. CONFIRMED.
   - Probe M: "Remove the echo that ctx.exit() follows." admits `ctx.exit()`.
   - Review 5's F2 fix line named "that", "which" and "near". The pass left out "that" and "near". "which" already ends the clause.
   - Fix: add `that` and `near` to `_NOT_TARGET`, or end the target part at a relative clause after the first noun.
3. **Review 5's F3 stays open on the safe side.** `rota/roles/api.py:17562`. Low, low. CONFIRMED by probe A. The pass report records the choice. Fix: none needed for the branch.

Outside the points:

4. **The pass 4 and pass 4b count scripts now fail on the current tree.** `scratchpad/f283_p4b_count.py:52` calls `api._removal_asked`. Low, low. CONFIRMED by grep. The pass report names this as deviation 4. Fix: none in the tree. Do not re-run those scripts against d7ddfb00.

Not a finding: "Keep ctx.exit(), but drop it from the test." admits `ctx.exit()` at cbdc68f8, 599b72e4 and d7ddfb00. The sentence is ambiguous, and the pronoun can name `ctx.exit()`.

## (c) Probes

All probes ran with `D:/repos/rota/.venv/Scripts/python.exe` against `C:/Users/roman/rota_r283` at d7ddfb00. The scripts are review 5's, in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/1b2c3f89-168f-4708-a241-5ecb0a745d11/scratchpad/r5/`. No new probe file was written.

- A, `r5_and.py r5/api_p4.py`: 38 shapes, new rule against cbdc68f8, with the request clauses printed.
- M, `r5_more.py`: 13 shapes of comma lists, pronoun reach and locators.
- N, `r5_nights.py`: nights 140 to 158, read-only. It printed the request clauses that still hold "and" after the removal verb.
- T: `pytest -n 0` on `tests/rota/test_frame283_removal_on_ruling.py` and `tests/rota/test_frame140_commit_beside_note.py`, 100 passed.
- D: `git diff 599b72e4 d7ddfb00`, read hunk by hunk. `git grep _removal_asked` at both commits. A grep of the scratchpad for callers.

## (d) Usage

About 45k input tokens, about 6k output tokens, about 51k total. The figures are estimates. The harness shows no exact count to the reviewer.
