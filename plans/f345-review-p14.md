# Review p14: pass R5 at bcab3fce

Verdict: pass. No high finding. Two low findings and one note. The worktree is C:/Users/roman/rota_p14.

## (a) Verdict on each point

1. Holds. Each probe in the brief binds as the brief says. `_NOT_SUBJECT` and `_ON_LINE` can both match one `before`, and `_ON_LINE` wins.
2. Holds. Four rows match the code: m121 "with line 2", m136 "on line 9", m53-m55 "to line 3", m116 "lines 7 and 8".
3. Holds. The two new tests pass, 4 of 4. The skipped test now states a binding that the code no longer gives.
4. Holds with a note. The two files give 75 passed, 2 failed, 2 skipped. The report names the 2 failures as red before the change.

Point 1 detail. Both regexes match when a path ends in a word "on", as in "rota/on line 4". `lead` is then false, and the `elif` sets `placed`. So `_ON_LINE` wins and line 4 binds.

Point 3 re-pin. The test must assert `line_words(his, 3)[3] == "Nobody needs the note on line 3, so drop it."`. It must also assert that the drop lands on the first call with no refusal.

## (b) Findings

1. rota/roles/api.py:13393. Severity low. CONFIRMED. A code place after "on" now binds a page line. "fix the call in cli.py on line 5" binds 5. "the bug is in rota/roles/api.py on line 40" binds 40, size 50. Before R5 these clauses bound nothing. `_NOT_SUBJECT` cannot catch the path, because "on" stands between the path and the reference. The m121 target "the file on line 9" has the same form, so the rule cannot tell the two apart. Fix: refuse `placed` when `_PATH_SHAPE` matches the last word before "on".
2. rota/roles/api.py:13393. Severity low. CONFIRMED. A joined reference after a placed one is lost. "we put the fix on line 3 and on line 5 and also line 6" binds {3, 5}, not 6. The `placed` branch does not set `last_end`, so `_REF_JOIN` never reads line 6. Fix: set `last_end = end` in the `placed` branch, and add joined references to the set of the reference before them.
3. Note, outside the points. A bare list after "on" is not placed. "the old note sits there on 1, 2 and 3" binds nothing. This agrees with the rule that a bare list in a clause names no line. No fix is needed.

## (c) Probes

- Scratchpad file p14_probe.py, run from the worktree root with the worktree first on `sys.path`. The probe ran `_subject_lines` on 13 clauses and `line_words` on 5 replies, with size 10.
- An inline `python -c` ran `_subject_lines` at size 50 on the two code-place clauses of finding 1.
- An inline `python -c` ran `line_words` on the reply of the skipped test, at size 3. The result was {1: "Line 1 is right.", 2: None, 3: "Nobody needs the note on line 3, so drop it."}.
- pytest, replay, `ROTA_MODEL=qwen3:8b`, `ROTA_L1` unset, on test_seam2_word_per_line.py and test_r1_menu_form.py. The result was 2 failed, 75 passed, 2 skipped.
- pytest with `-k "after_on or after_with"`. The result was 4 passed.
- A read of the 2 failing tests. Each seats the reply "Drop the note, both times. The rest is fine.". That reply holds no "on" before a reference, so R5 cannot change it. The error is the clause-key refusal for "c1". The report section (b) names both as red before the change.

## (d) Usage

Input tokens: about 190k over all turns. Output tokens: about 6k. Total: about 196k.
