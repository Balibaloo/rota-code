# Frame 204, pass 1e review, commits 397001a8 and ab641368

Reviewer: Opus, read-only, worktree C:/Users/roman/rota_rv204e at ab641368.
Date: 2026-10-12. Verdict: the pass stands after one brief fix (H1).

## (a) Verdicts on the numbered points

1. Holds. An `@prose` row lands on an empty account and on a one-area account, and the agenda takes it.
2. Holds for the reconcile seat. The `@prose` offer goes to every seat with no `model_areas` row, so it can mislead (L1).
3. Fails. The new sentence has 25 words and contradicts the pass 1d sentence and the literal door (H1, L2).
4. Holds. The sentence and the template name `about_ref="@prose"` and the README path, and the pass 1d words stay intact. The template drops the item-id route (L3).
5. Holds. Both new tests fail at 6a80be2c and pass at ab641368. The brief test pins wording and misses the contradiction of H1 (L4).
6. Eight cases change their prompt hash. The list is in finding N1.

## (b) Findings

H1. rota/roles/prompts/tester/tests_missing.md:11-13 against :47-50. Severity high. PLAUSIBLE.
The new sentence says "Every literal the test asserts comes from the criterion, surface or material".
Lines 47-49 say "A string the material does not fix -- a sample name, a prompt's wording -- is an assumption, and the encode records it by itself."
The literal door agrees with lines 47-49: `_invented_literals` (api.py:5397, used at 7058) stages a guessed literal as kind `invented` and admits the encode.
So the brief now tells the seat two things about a sample name. A seat that reads line 11 as absolute triages a criterion with a sample name as `cannot`.
Only the scoped half, "a header or format only another spec defines", agrees with line 49-50.
No model was called, so the effect on the seat is not measured.
Fix: scope the sentence: "A header or format that only another spec defines is `outside_fact`; a sample string stays an assumption the encode records."

L1. rota/roles/api.py:8019-8023 and 8094-8097. Severity low. CONFIRMED.
`_declares_an_area` reads `model_areas` only. `_area_resolves` also accepts `area_hashes`, which onboarding writes before the survey.
Probe p1, account with an `area_hashes` row for src/billing and no `model_areas` row:
`'billing' names no row ... the account declares no area, so a row about a README or docs claim takes about_ref='@prose'`, while `@src/billing` landed as l_6de9d4cb51.
The reconcile phase runs before the survey, so the README advice reaches every onboarding seat with a wrong ref, for example a Terminologist in define.
For a seat that is not about prose the advice names a wrong subject. A Developer on a warm account still gets the area advice.
Fix: offer `'@prose'` only when `ctx.area` starts with `@prose`, and let `_declares_an_area` read `area_hashes` too.

L2. rota/roles/prompts/tester/tests_missing.md:11-15 and api.py:5263-5275. Severity low. CONFIRMED by reading.
The sentence routes `cannot` to `msg.question_researcher`. Line 14-15 and the triage door's `cannot_next` route `cannot` to `msg.question_terminologist`.
The verdict that routes to the Researcher is `outside_fact` (line 58, api.py:5282).
The sentence also counts 25 words, so it is not under 25.
Fix: write `outside_fact` in place of `cannot` in the new sentence, which also resolves part of H1.

L3. rota/roles/prompts/vision_keeper/reconcile.md:17-18. Severity low. CONFIRMED on old run databases.
The template no longer offers "the item id it touches". On clickI_night142, 14 of 29 Vision Keeper conflict rows named an item, for example `how_it_works`; night 141 shows 14 of 34.
An `@prose` row reaches no item: `_items_reached(conn, row)` returns [] in probe p2. The park, the request sort and the contest of an item at land (principal.py:1810-1827) then never see the row.
The interview's wall was a directory name on an empty account. The item route worked on warm accounts.
Fix: keep "or the item id it touches, under about_table='items'" as the second choice in the template, or rule that reconcile rows reach no item.

L4. tests/rota/test_prompts.py:282-305. Severity low. CONFIRMED.
The test pins exact phrases, for example "only another spec defines is `cannot`", so the H1 fix breaks the test for a correct edit.
The test does not check that the new Tester sentence agrees with the pass 1d sentence.
Fix: assert on the routed verdict word and the ref only, and add one assertion that the brief keeps the "is an assumption, and the encode records it" sentence.

N1. The stale set (point 6). CONFIRMED by probe p6.
`fixtures.instructions_for` gives a new hash at ab641368, against 6a80be2c, for these 8 cases of 157:
ACT-TS-five-criteria-one-per-reply, ACT-TS-give-the-prompt-a-stream, ACT-TS-three-criteria-one-per-reply,
L1-TS-a-criterion-no-machine-could-check-is-vision_keepers, L1-TS-a-criterion-that-contradicts-the-request-goes-back,
L1-TS-an-outside-fact-is-the-researchers, L1-TS-encode-a-criterion, L1-VK-reconcile-the-readme.
The hash covers the first seat's composed brief only. A chain or gauntlet case that reaches these seats later can turn red on replay and not show as stale. That part is PLAUSIBLE.
L1-TS-an-outside-fact-is-the-researchers is at risk from L2: the sentence names `cannot` for the Researcher route, and the case expects `outside_fact`. That is PLAUSIBLE.

Outside the points: none beyond L1's onboarding scope.

## (c) Probes

All probes sit in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/5d91f76d-246c-40b7-8ebe-acd318e106d2/scratchpad/rv204e/.
- p1.py: ledger.log through `build("vision_keeper", mode="reconcile")` with `@prose`, `@prose:docs/a.md`, `billing`, `@billing` on an empty account, a one-area account and an area_hashes-only account. `@prose` landed as l_f3bb5e2394 on both accounts.
- p2.py, p3.py: one open `@prose` conflict row. `_items_reached` gave []. `render_page` gave the row. `tick_agenda(principal_present=True)` gave `liaison<-tick:agenda(ledger=1)`.
- old/: `git archive 6a80be2c` with the two test files of ab641368. Both new tests failed there. At ab641368, test_prompts.py and test_identity.py gave 40 passed.
- p6.py: the prompt hash of every case at both trees. 8 of 157 differ.
- Read-only queries on D:/repos/rota/.rota/clickI_night141.db and clickI_night142.db for ledger rows.
No model was called. The gate was not run.

## (d) Usage

Input tokens: about 70k. Output tokens: about 9k. Total: about 79k, over the 50k cap. Read the harness line for the exact count.
