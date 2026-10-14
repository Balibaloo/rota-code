# Frame 221, review 2: the assert door at 5e2f0e57 over 3de76eaf

Rota workflow, the Vision Keeper's `problem.assert` door. Read-only review on the worktree C:/Users/roman/rota_rv221b.

Verdict: revise. The two code highs of review 1 are fixed on the shapes they named. The drop check now refuses a contest that removes a named thing in plain words, which is the contest the door exists to admit. Findings 1 to 3 below are the next pass's brief.

## (a) Verdicts on the points

1. Review 1's seven findings: 1 fixed, 2 partly fixed, 3 fixed, 4 fixed, 5 not addressed, 6 fixed, 7 fixed. Probes P1a, P1b and P2a, P2b confirm the two code highs on their shapes.
   - Finding 1: fixed. P1a and P1b refuse a text that drops `show_python`. P1c admits the text that keeps it.
   - Finding 2: partly fixed. An approving ruling on the item blocks the assert (P2a, P2b). A contest ruling admits the principal's words (P1c). The rule "the words name only other lines" is not built. The implementer's deviation 1 states this. A pre-frame-225 ruling that folds a criterion contest onto the item still admits the s128 retry.
   - Finding 3: fixed. exhausted.md sends a decided item to `msg.report_liaison`.
   - Finding 4: fixed. The exhausted refusal names `msg.report_liaison` first, and a test checks the order.
   - Finding 5: not addressed. challenge.md is unchanged. The finding was an escalation to Roman, so the pass had no edit to make.
   - Finding 6: fixed. contested.md line 18 now names the principal and uses the active voice.
   - Finding 7: fixed. A test covers the exhausted refusal. The relay branch is removed. No test covers the onboarding skip, and this commit does not touch it.
2. The ruling read: the door takes the newest `rulings` row by rowid that names the id in `per_item` and has a status other than `stale`. The door reads rulings from every page, and the door ignores which page woke it. An `open` ruling counts (P4c). The door no longer checks that the id is in the wake's refs (P5). See findings 2 and 3.
3. The contested.md example still lands (P7, and the test `test_the_contested_briefs_own_example_lands`). No new refusal text and no new brief line has a pronoun for the principal. The lines of contested.md that the diff did not touch still say "they" and "their" for the principal (lines 3, 6, 9, 11, 19 to 24). That is outside this diff.
4. exhausted.md's new sentence matches the mode's tools. `exhausted.tools` offers `msg.report_liaison`, `problem.assert` and `decisions.author`.
5. The 12 tests: all 12 pass at HEAD. On the parent, 5 are red: the s399 test (new expected text), the approving ruling, the negated name, the s128 approving ruling and the exhausted refusal. The other 7 pass on both commits. No test covers these branches: the legacy `approval = 'contested'` fallback with no ruling and no verdict, a contest ruling with empty words, an id outside the wake's refs, an `open` ruling, and a contest that removes a named thing in plain words.

## (b) Findings

1. `rota/roles/api.py:1312-1325` (the drop check). High. CONFIRMED by probe P3. The principal's ruling contests the item with "I don't want a flag. Always append the running Python version, shown as major.minor.micro." The seat writes "The `version_option` always appends the running Python version, shown as major.minor.micro." The door refuses it, because the text drops `show_python`. The principal's words name the removal in plain words, and the plain words never contain the identifier. The refusal then tells the seat to keep the item. So the door blocks the contest it exists to admit, and the batch repeats the frame 197 loop. Fix: admit a dropped token when the principal's words carry a negation cue ("no", "not", "don't", "without") within three words of one of the token's word parts or its kind word ("flag"), and add P3 as a test.
2. `rota/roles/api.py:1276-1277` and 1289. Low. CONFIRMED by probe P5. The wake is `tick:contested` with refs `("tip_split",)`. The seat asserts `version_option_show_python`, which has a landed contest ruling. The door admits the assert. The old code checked `id in wake_refs`, and the pass removed the check. A contest that a previous rewrite already applied still reads as live until a new ruling lands. Fix: return the "does not contest the item" refusal when the id is not in `ctx.wake_refs`.
3. `rota/roles/principal.py:736`, read at `rota/roles/api.py:1289`. Low. CONFIRMED by probe P4c. A newer `open` ruling that approves the item hides a landed contest. The door then refuses the contest. An open row exists between the Liaison's `rulings.rule` and `principal.land`. Fix: read only `status = 'landed'` rulings in this door, for example with a `landed_only` argument to `last_ruling_on`.
4. `rota/roles/api.py:1305-1308`. Low. PLAUSIBLE: the refusal says "The contest names other lines" when no ruling names the item at all and the approval is not `contested`. That sentence is then false, and the seat can look for lines that do not exist. Fix: say "No ruling of the principal contests the item" when `ruled` is None and `found` is empty.
5. `rota/roles/api.py:1310-1311`. Low. CONFIRMED by probe P6, and the behaviour is older than this pass. A contest ruling with empty words admits any text, including "Anything the seat likes, `foo_bar`." The legacy fallback has no words either, so the legacy branch admits any text. Fix: refuse a rewrite with no words of the principal, and point the seat at `msg.report_liaison`.

Outside the points: finding 5 is outside the points. Review 1's finding 5, the challenge route, still waits on Roman.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/58da19ca-3cc0-49b5-a8a7-5edb2f08ef46/scratchpad/rv221b/.

- `probe1.py`: the test file's database fixture, a `tick:contested` wake and `problem.assert` through `build("vision_keeper", ...)`. The probe ran from the worktree with `PYTHONPATH` set to the worktree. Results:
  - P1a, contest ruling, text drops `show_python`: refused, drops `show_python`.
  - P1b, the same text with no backticks: refused, drops `show_python` and `version_option`.
  - P1c, contest ruling, text keeps the flag in the principal's words: admitted.
  - P2a and P2b, the ruling approves the item and contests `l_x`: refused, "does not contest the item".
  - P3, the contest says "I don't want a flag", text drops the flag: refused, drops `show_python`.
  - P4a, an older contest on m249 and a newer approve on m300: refused.
  - P4b, an older approve and a newer contest: admitted.
  - P4c, a landed contest and a newer `open` approve: refused.
  - P5, the wake refs `tip_split` and the assert is on `version_option_show_python`: admitted.
  - P6, a contest ruling with empty words, a text in the seat's own words: admitted.
  - P7, the contested.md example on `tip_split` with a config verdict: admitted.
- `parent/`: `git archive 3de76eaf rota tests pyproject.toml` with the HEAD test file copied in. Pytest on the test file: 5 failed, 7 passed. At HEAD the same file gives 12 passed.

## (d) Usage

From the context counter: about 49k tokens in all, about 43k input and about 6k output. That is over the 35k cap. The parent's test run and the second probe launch cost the excess.
