# Review p5 of frame 354: commit e51b540d

Verdict: the claim holds on the Liaison path, with 1 high and 3 low findings. Points: 4 hold, 1 holds with a finding (point 1), and point 5 finds no hunk outside the claim. Tests: 18, 19, 41 and 70 passed, 0 failed.

## (a) Verdicts on the points

1. Holds on the Liaison path, with finding 2 on the scripted path. `rulings.rule({"1": "drop"})` gives `per_item` `{KEY: "approve"}`, and `apply_rulings` marks the key `(3, 1, 2)` once. `{"1": "try again"}` gives a contest, and the lift deletes the row once. Neither stages a fault. A typed reply never reaches a verdict. `parse_reply` (principal.py 130-148) returns verb `reply` for "1 drop", "1 try again", "drop" and "ok", and `land` closes nothing on a `reply`. Only a script builds a verdict. A scripted `per_item` `{KEY: "drop"}` lands as the stored verdict `drop`, and `land` does not act on it. A scripted `{KEY: "try again"}` is refused: "'try again' is not a stored verdict".
2. Holds. The five callers are these. `resolve_inbound` (runner.py 2549) and `_menu_page` (api.py 14143) and `rulings_rule` (api.py 14984) test `is None` only, so a step line leaves `gone_lines` and `gone`. `ruling_rows` (principal.py 1117) writes the `ruled_refs` and `reading` rows with the home `tick_attempts`. Its version query reads only a table with a `version` column, and `tick_attempts` has none. `_identifier_grants` acts on `criteria` only. `_code_target` (api.py 24808) now calls a step key no code target. No caller reads `tick_attempts` as a row by `id`. `rowless_key` holds only for a quarantined, unruled key, so no caller writes a row for a key that is not quarantined.
3. Holds. `_retries_said` (principal.py 2058-2071) counts the `landed` `ruled_refs` rows with `contest` or `revise` on the key. It adds words only when the newest row is one of them. Over three retries the pages say nothing, "once before", "2 times before", then "3 times before". The line says "2 times", not "twice". Each retry writes one `reading` row and one `landed` row.
4. Holds. After `drop`, `render_state` says "Nothing waits on you and nothing is building", and `code_gaps` lists no step. After `try again` the row is gone, and the status line says the same words. The fixture runs no scheduler, so the status line has no word for a step that waits to run again.
5. None outside the claim. The `landing.md` sentence is in the commit message and in the pass report at the coordinator's word. The `scheduler.py` hunk is the claimed `regrouped_key` read.
6. `test_frame354_quarantine_page.py -n0`: 18 passed. `test_frame337_earlier_answers.py -n0`: 19 passed. `test_r1_menu_form.py -n0`: 41 passed. `test_request_page.py -n0`: 70 passed.

## (b) Findings

1. rota/roles/principal.py 1202 and 1308, high, CONFIRMED. The second page of a retried step carries a read-back line: '2. Your answer "1 try again", as the team read it: line 1 is wrong. Say ok, or say what we misread.' He asked to run the step again, and the page says he called the line wrong. Every retry adds this line, and he must answer it. Fix: give a step key its own read-back words in `_READ_BACK_VERDICT`, "you asked me to try it again", or leave the read-back line off a step line that `_retries_said` already says.
2. rota/roles/principal.py 3263-3266, low, CONFIRMED. A scripted `per_item` `{KEY: "drop"}` closes the ask as answered and writes a `keypress` and a `landed` row with `drop`. The key stays at `(3, 1, 0)`, and `render_state` says "Stuck" again. The page now says the word `drop`, so a script that copies the page hits this path. Fix: in `land`, read `drop` on a step as `approve`, or refuse a step verdict outside approve, contest and revise.
3. rota/roles/api.py 14726-14735, low, CONFIRMED. On the second page, his repeat "1 try again" names line 2 too, because the read-back line quotes "1 try again". `rulings.rule({"1": "try again"})` is refused: "line 2: his words name the line, and the call gives it no option". The Liaison must rule the read-back line it did not mean to rule. Fix: do not count a match inside the quoted words of a read-back line as a name of that line.
4. tests/rota/test_frame354_quarantine_page.py 190-196, low, CONFIRMED. `_present_critic` reads the first present with no `ORDER BY`. A second call returns the old answered page, and `rulings.rule` refuses "no open page". So `test_the_next_page_of_a_retried_step_says_he_asked_before` calls `render_page` with `stalled=[KEY]` and no `ask_id`, and the page it checks has no read-back line. That is why finding 1 is not measured. Fix: read the newest present with `ORDER BY seq DESC`, and test the second page through a second present.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/05666872-07ce-4805-be2d-636d5ab7329f/scratchpad/f354p5r/`. They ran from `C:/Users/roman/rota_f354r` with `ROTA_MODEL=qwen3:8b`. No model call ran.

- `probe_scripted.py`: `parse_reply` and `land` on "1 drop", "1 try again", "drop" and "ok". Each gives verb `reply`, and the ask stays open.
- `probe_verdicts.py`: `land` with `per_item` `drop`, `try again`, `approve` and `contest` on the critic key. It prints `tick_attempts`, `ruled_refs`, the ask status and `render_state`.
- `probe_liaison2.py`: `rulings.rule` with the line form and the key form of `drop`, `try again` and `ok`. The key form is refused as "no clause and no page line", and `ok` is refused as no option of a step line.
- `probe_retries.py`: three cycles of present, `try again` and `apply_rulings`, then a `drop`. Each cycle prints the page line, the faults, `tick_attempts` and `render_state`. The end prints `code_gaps`.
- `probe_page2.py`: the second page after one retry, with `body_refs`, the order and the page text.
- Reads of the five callers of `ruled_ref_home`, of `land` 3255-3300 and of the `tick_attempts` schema through `rota.tools.map`.
- The four pytest runs of point 6, each with `-q -n0`.

## (d) Usage

The harness shows no exact counts, so these figures are estimates. Input: about 50k tokens of context at the end. Output: about 10k tokens. Total: about 60k. The brief's cap was 30k. The retry probe needed three runs, and the cap did not hold.
