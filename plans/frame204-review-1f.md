# Frame 204, pass 1f review, commits 24b75e68 and c9e915c5

Reviewer: read-only agent on Opus, worktree C:/Users/roman/rota_g204e at c9e915c5.
Date: 2026-10-12. Verdict: the pass stands. No high finding. Four low findings, one of them outside the points.

## (a) Verdicts on the numbered points

1. Holds. The sentence has 24 words and no imperative. The mode offers `msg.question_researcher`. The sentence overlaps the pass 1d `cannot` sentence on a format (L1).
2. The miss is the model, with a door gap behind it (L3). No run of 15 at the new hash took the sentence's route (L2).
3. Holds. The sentence and the template name `@prose` and the item id. The template alone names the table. The pass 1d words stay intact.
4. Holds. The area_hashes-only account gets the area advice, and the empty account gets `@prose`.
5. Holds. The test fails at 6a80be2c and at ab641368, and passes at c9e915c5. Two checks are weak (L4).
6. Holds. 8 of 157 cases moved their brief hash. All 8 carry a re-record at the new hash between 11:18 and 11:21.

## (b) Findings

L1. rota/roles/prompts/tester/tests_missing.md:11-13 against :49-50. Severity low. PLAUSIBLE.
The new sentence: "An unsourced literal is an assumption logged `invented`, but a header or format defined in another spec, not this criterion, is `outside_fact`, for `msg.question_researcher`."
The pass 1d sentence: "A function or a format that the material does not name is not a test, and the criterion is `cannot`."
A format that another spec defines is also a format the material does not name. So the brief gives two verdicts for one format.
Lines 52-57 make `outside_fact` the sharper form of `cannot`, and the case accepts both desks. So the conflict costs no route.
The literal half agrees with the literal door: api.py:7058-7081 and 7255-7256 stage the row as kind `invented` and admit the encode.
Fix: in line 50, write "is `cannot`, or `outside_fact` when another spec defines it".

L2. tests/rota/cassettes.db, case_runs for L1-TS-an-outside-fact-is-the-researchers, prompt_hash 0f282ba959d5fa2c. Severity low. CONFIRMED.
Three record batches at the new hash (11:02:48, 11:02:51, 11:19:58) give 15 runs. All 15 triage `encodable` first. No run triages `outside_fact` or calls `msg.question_researcher`.
The 12 passing runs encode `assert True`. The constant-assertion door refuses it: "every assertion here is on a constant ... that is tests.triage verdict='cannot'". The seat then triages `cannot` and asks the Terminologist.
So the 4/5 is the constant door's result, not the sentence's route. Pass 1e's text gave 1/5, and pass 1d's text gave 3/5, with the same door path.
The case's `any_of` accepts the Terminologist and the Researcher. Commit c9e915c5 says the case "expects that route". The case accepts that route and does not require it.
Fix: write in the frame status that the sentence's route is unmeasured, 0 of 15, and that the pass comes from the constant door.

L3. rota/roles/api.py:7058-7081 (the literal door) against tests_missing.md:49-50. Severity low. PLAUSIBLE.
The failing run 2 (seq 425835) triaged `encodable` and encoded `from webhooks import sign` with `sign({"data": "example"})["headers"]["signature"]`. The run wrote `ledger: 1, tests: 1` and sent nothing.
The case forbids a write to `tests`, so the run failed. This is the frame's TS1 wall, an invented header test, again in 1 of 5.
The brief says a function that the material does not name is `cannot`. No door refuses the import of `sign`. The literal door logged a literal as `invented` and admitted the test.
I did not read the ledger row of run 2, so the literal that the door logged is an inference.
Fix: by the residue rule, push a frame for a door that refuses an imported name that the surface and the material do not name.

L4. tests/rota/test_prompts.py:292-295 and :309. Severity low. CONFIRMED by reading.
`"item" in part and "id" in part` passes on "never an item id", and "id" matches inside "did" or "said". So the check does not prove the item route is offered.
`"is an assumption, and\nthe encode records it"` pins a line break. A re-wrap of the paragraph breaks the test for a correct edit.
Fix: assert on "the item id" and `"items"` in the template, and normalise whitespace before the assumption check.

L5 (outside the points). rota/roles/api.py:8101-8107. Severity low. CONFIRMED by probe p4.
Pass 1f took the second half of the 1e L1 fix only. The empty-account refusal still says "a row about a README or docs claim takes about_ref='@prose'" to every seat.
A Terminologist or a Tester on an empty account gets README advice for a ref that is not about prose.
Fix: offer the `@prose` sentence only when `ctx.area` starts with `@prose`, else say the ref names no row.

## (c) Probes

All probes sit in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/5083f684-6864-4cc2-ae65-244a1c2c8966/scratchpad/r1f/.
- Map: `map mode tester/tests_missing` lists `msg.question_researcher`, `msg.question_terminologist` and `ledger.log`. `map mode vision_keeper/reconcile` lists `ledger.log`.
- Register reads: read-only queries on tests/rota/cassettes.db, case_runs and cassettes, for the outside-fact case and the 8 moved cases.
- p3.py: `@prose` with about_table `README.md`, `docs/usage.md` and `items` on an empty account. All three landed.
- p4.py: `billing` on an empty account, an area_hashes-only account, and a database with no area_hashes table. Results: `@prose` advice, area advice, `@prose` advice. `@src/billing` landed as l_6de9d4cb51.
- p5.py: the body of the brief test run on `git archive` trees. 6a80be2c: FAIL at the `@prose` check. ab641368: FAIL at the item check. c9e915c5: PASS.
- p6.py (copied from review 1e): the brief hash of every case at 6aa1abd8 and c9e915c5. 8 of 157 differ, the same 8 as review 1e.
- pytest: tests/rota/test_identity.py and tests/rota/test_prompts.py gave 40 passed in 4.09s.
No model was called. The gate was not run. The gate figures are the holding session's.

## (d) Usage

Input tokens: about 75k. Output tokens: about 9k. Total: about 84k, over the 50k cap. Read the harness line for the exact count.
