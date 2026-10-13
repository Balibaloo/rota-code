# Frame 225, review 1d: commit 725d43ab, the fold names the items from the answer as given

Verdict: stands. The commit closes review 1c's high. No high finding. Two low findings remain from review 1c, and one new low note.

Rota workflow throughout. Worktree C:/Users/roman/rota_rv225c at 725d43ab. Reviewer: read-only agent, 2026-10-13.

## (a) Verdicts on the numbered points

1. Closes the high. CONFIRMED: review 1c's probe at 725d43ab gives case C verdict {"L9": "contest"}, approval approved, relay refs []. Case D, the default note, still contests the item, as A1 says.
2. Holds. The earlier set adds batch ids, stamped refs and resumed refs to `ruled`. Each one only stops a non-default note from adding a contest on a row the answer already rules. A resume on the item now wins over the note: CONFIRMED by probe, see finding 2.
3. Holds. The new test is red on df474208 and green on 725d43ab: CONFIRMED by probe. The batches row sets id, item_id and status 'running'. The schema requires item_id NOT NULL and a status in its CHECK list (schema.sql:457-463). The row meets both.
4. Holds. `git show 725d43ab | grep -c $'\r'` printed 0. The comment sentence at principal.py:1736 is true: `ruled` reads `answer.per_item` before the batch filter, the stamped filter and the resume pop.

## (b) Findings

1. tests/rota/test_signoff_assumptions.py:272-276. Severity low. CONFIRMED by reading.
   The new docstring is a history note: "The review of df474208 found". Review 1c finding 2 named this pattern. The duplicate conflict-with-approve test also stays.
   Fix: state the behaviour in the docstring: "A scope note's contest leaves an item the answer approves, on a batch page too."

2. rota/roles/principal.py:1737 with the resume pop at 1790-1797. Severity low. CONFIRMED by probe.
   Answer {"echo_json": "resume", "L9": "contest"} with a scope note: at df474208 the item was contested. At 725d43ab the item stays draft and the verdict is {"L9": "contest"}. The new result follows the rule "his explicit ruling wins over an inferred one". The behaviour change has no test.
   Fix: none needed for the defect. Add one test if the frame wants the resume case pinned.

3. rota/roles/principal.py:1772-1792. Severity low. CONFIRMED by reading. Outside the points.
   Review 1c finding 3 stays open. The block comment still says a contest "contests the row the assumption was about" with no exception. The line "(`per_item` is the ruling less any batch ref ...)" no longer explains the fold, because the fold reads `ruled`.
   Fix: name the two cases in the block comment, and point to the comment at the fold.

Review 1c finding 4, the Critic about_ref "items:X", is not touched by this commit and stays PLAUSIBLE.

## (c) Probes

- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/80cae596-3d3e-44f8-a0fe-b9ff034a378c/scratchpad/rv225c/probe.py, run at 725d43ab. A: item contested. B: item approved. C: verdict {"L9": "contest"}, item approved, refs []. D: item contested.
- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/80cae596-3d3e-44f8-a0fe-b9ff034a378c/scratchpad/rv225d/probe.py with principal_df4.py, the file at df474208. The probe calls the new test function on a fresh init_db with each land(). Result: 725d43ab PASS, df474208 FAIL with approval contested. A resume case gives the results in finding 2.
- No pytest run. The gate runs in the worktree, and the brief forbids its register.
- git show 725d43ab piped to grep -c for CR: 0.

## (d) Usage

Input tokens: about 22k. Output tokens: about 4k. Total: about 26k. The harness line holds the exact count.
