Verdict: 9680f12d stands for the branch, with two med findings for a next pass.

# Frame 322, review 2: the documentation door at `criteria.specify`

The reviewer read 9680f12d in `C:/Users/roman/rota_r322b`, above e02384ab. The review edited no tracked file. Every database opened with `?mode=ro`. No model call ran.

## (a) The points

1. CONFIRMED, with a correction. The headline list and the criterion list are already one list, `_NAMES_DOCS`, with all five words (`api.py:5703`). `_ASKS_FOR_DOCS` is frame 311's diff-line list (`api.py:13633`), and the commit does not change it. The pass report's open question 1 names the wrong list. The ruling of 2026-10-24 01:05 governs the criterion's own words, so the criterion list follows it with "help text" in. The ruling says nothing about a headline, so a headline list without "help text" does not depart from it. Recommendation: use two lists, the headline list ("docstring", "documentation") and the criterion list of five words. Reason: a word that starts a refusal must be narrow, and a word that admits a criterion can be wide. The four nights give the same counts with either headline list (point 2).
2. CONFIRMED. The door refuses 18 landed writes on the docstring item and 0 elsewhere. The count is the same with the pass's words, the brief's five words (the same five), the read's three words and the two words of `_ASKS_FOR_DOCS`. 13 of the 18 are the read's behaviour writes. The other 5 are s208's respecifies of cr_2 to cr_6 to an empty text on night 164 (finding 4). No refused criterion is off the docstring item. On each night exactly one headline names a documentation word, the docstring ticket's. 4 of 11 headlines name one.
3. CONFIRMED. `criteria_specify` (`api.py:5874`) and `criteria_respecify` (`api.py:6917`) call `_docs_ticket_refusal`, and the map lists no other caller. Test 3 asserts that the two texts are equal, and it passes. The text is: "tk_1_format_filename_example's headline is '...'. The ticket asks for a change to the documentation and not to the behaviour, and this criterion names no documentation. Write the criterion on the documentation: say what the docstring, the docs or the help text must say. If the item also needs a code change, that is the Vision Keeper's to slice: send msg.challenge_vision_keeper with the ticket". The headline clause, the "names no documentation" clause and the route clause are true. Both modes hold `msg.challenge_vision_keeper`. The clause "asks for a change to the documentation and not to the behaviour" is false for a mixed headline or a non-documentation use of a word (finding 3).
4. CONFIRMED. The new text keeps a word overlap of 0.889 with c_1's old words, the same as the old text, and 0.357 with c_1's staged words. With `_staged_ticket` patched to return None, the test fails with the near-twin refusal. So the test still proves the staged-twin rule, and the edit does not weaken it.
5. CONFIRMED. The docs check runs before the twin checks in `criteria_specify`, so a docs refusal on c_2 shows before the near-twin refusal. With "profile" added to `_NAMES_DOCS`, test 2 fails on the `_MARK` assert. The probe needs `-n0`, because the suite's xdist workers do not see a patch in the parent process.
6. PLAUSIBLE, one claim false. `casestatus --model qwen3:8b` lists the case as NEW. The `expect` passes on a docstring criterion. The `expect` does not fail on s185's first turn, because s185's c_3 names the docstring and `text_includes_any` checks one blob of all rows (`fixtures.py:605`). The rule at `test_case_reachability.py:254` needs a `repo:` block only, because `terminologist/criteria.tools` holds `code.source` and no `code.probe`. `onboard: true` meets it and also gives `code.callables` an index. Under the door every landed text names a documentation word, so the case passes when one criterion lands. The case measures the door, not the model (finding 2).
7. CONFIRMED. The map lists two callers of `_docs_ticket_refusal`, and one writer of `tickets.text`, `tickets_slice`. The 52 readers of `tickets` do not read the new function. The test runs: `test_criteria_one_id.py` 7 passed, `test_frame322_docs_ticket.py` 4 passed, `test_frame329_staged_twin.py` 9 passed, `test_fixtures.py` 1 failed and 11 passed, `test_case_reachability.py` 702 passed and 30 skipped. The one red is the known `test_no_case_leaves_a_reference_unwrapped`.

## (b) Findings

1. `rota/roles/api.py:5703`, med. CONFIRMED: `_asks_for` matches a substring, so the headlines "load_document raises ValueError on an empty file" and "add a --verbose option whose help text says show the steps" name documentation. The door then refuses every behaviour criterion on those behaviour tickets. The four nights hold no such headline, so the count in point 2 cannot show this. Fix: give the headline its own list, ("docstring", "documentation"), and keep the five words for the criterion.
2. `tests/rota/cases/l1_terminologist_docs.yaml:37`, med. CONFIRMED by reading `fixtures.py:605`: the check joins all rows and their ids into one blob. s185's turn passes it, and a criterion id with "docstring" in it passes it too. Fix: add a per-row text check, such as `each_text_includes_any`, that reads the `text` column only, and move the case to it.
3. `rota/roles/api.py:5724`, low. PLAUSIBLE: the door cannot read "only", so "The ticket asks for a change to the documentation and not to the behaviour" claims an intent the door does not know. Fix: write "The headline names the documentation" and keep the two routes.
4. Outside. `rota/roles/api.py:6712`, low. CONFIRMED on night 164: s208 respecified the retired cr_2 to cr_6 to an empty text, and each call returned `"respecified": true`. The final rows hold an empty text. PLAUSIBLE at HEAD: the first 90 lines of `criteria_respecify` hold no empty-text guard. The read's section 3 table says s208 respecified to docstring texts, which is not what landed. Fix: refuse an empty text and a retired row in `criteria_respecify`, and correct the read's row for night 164.
5. Outside. The pass report, open question 1, low. CONFIRMED: it says `_ASKS_FOR_DOCS` leaves out "help text", but the door uses `_NAMES_DOCS`, which holds it. Fix: correct the question in the frame record before Roman reads it.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ad481e08-d0cc-4317-a992-02d5208ea7e8/scratchpad/`.

- `r2_count3.py` and `r2_count4.py`: they pair each `TOOL:` line in a turn's `user` text with its `OK` or `ERROR` line, keep the landed `criteria.specify` and `criteria.respecify` texts, and apply the four word lists. 62 calls did not pair. `r2_probe5.py` showed that the four unpaired calls on the docstring ticket landed no write.
- `r2_probe3.py` and an inline probe: the s412 and s208 result lines, and the final criteria rows of night 164.
- `r2_p45.py`: the word overlaps of point 4.
- `r2_p4.py`: the frame 329 test with `_staged_ticket` patched to None. It fails.
- `r2_p5.py`: test 2 with "profile" added to `_NAMES_DOCS`, run with `-n0`. It fails.
- An inline `python -c`: `_asks_for` on three invented headlines.
- `casestatus --model qwen3:8b`, and the five pytest files of point 7.

## The counts

| Night | Headlines that name docs | Refused, docstring item | Refused, other |
|---|---|---|---|
| 163 | 1 of 3 | 2 | 0 |
| 164 | 1 of 2 | 11 (6 behaviour, 5 empty) | 0 |
| 165 | 1 of 3 | 3 | 0 |
| 166 | 1 of 3 | 2 | 0 |
| All | 4 of 11 | 18 | 0 |

The pass's words, the brief's five words, the read's three words and `_ASKS_FOR_DOCS` give the same table.

## (d) Usage

The harness reports a remaining budget only, and it does not split input from output. The budget fell from about 14,986,000 to about 14,890,000. So the review used about 96,000 tokens against a cap of about 40,000. The debug of the result pairing and of the xdist patch took the excess.
