# Frame 234, pass 2: diff review 3 of the unnamed-line refusal

Rota workflow, the Liaison's `rulings.rule` door. Worktree `C:/Users/roman/rota_rv234c` at 250f3806 over 0acf4c68. Reviewer: an Opus agent, read-only, 2026-10-14.

## (a) Verdict

Revise. One high finding and two low findings. The door refuses m131 as the frame asks. A single sentence with no line number silences the refusal on m131's words.

1. Point 1, m131 through the door: CONFIRMED. HEAD refuses with the named text. The parent lands the contest.
2. Point 2, batch-line skip: correct. m181 stays where it was, and the read files it under frame 189.
3. Point 3, the unnumbered-sentence guard: CONFIRMED gap. One added sentence silences the refusal on m131. 74 of 131 referenced replies carry such a sentence.
4. Point 4, "notes?": no false reference on nights 143 to 147. All "note N" tokens are references.
5. Point 5, key order: the door reads `order`. The three artifacts are the probe's alone (reasoned from the code).
6. Point 6, tests: five new tests are red on the parent. Three branches have no test.
7. Point 7, STE and CR: 0 CR bytes in the two files. No pronoun for the principal. The refusal text is STE.

## Points

Point 1. The probe builds the `_present` page with a request item first, three more items and seven notes, 11 lines. `ask.order` is `calculate_tip, c1, c2, c3, l_1 .. l_7`. s281's ruling contests 3, 4, 5, 6 and 8 to 11. At HEAD the door raises "The words name lines 3, 4 and 7 and do not name lines 5, 6 and 8 to 11. A contest rests on the principal's words. Approve the lines the words do not name, or rule them as the words say." At 0acf4c68 the same call lands, with `l_1`, `l_2`, `l_4` .. `l_7` as contest. The named and unnamed sets are as the brief says.

Point 2. A batch line is a page row whose id is a `batches` row. The page shows one on a prediction page, before the build, and on a review page, after it. On a built batch the batch door already refuses every non-approve ruling of the batch line (`api.py` 8616 to 8645). So a contest on a built batch line cannot cancel a batch, with or without the skip. Before the build, the batch door lets the contest pass to the Architect as a correction of the prediction. The skip lets an unnamed contest of an unbuilt batch line land, which is the report's open point 6. m181's words "Ok, go ahead." name no line, so `named` is empty and the refusal is silent before the skip applies. m181 stays exactly where it was. The read (`plans/night147-read.md` line 545) files m181 under frame 189, the prediction page, and not under this door. The skip agrees with that reading.

Point 3. The guard returns None when any sentence has no line reference and is not a bare agreement. m131's words with " Please also keep the tests small." added land the full over-contest at HEAD, the same as the parent. On nights 143 to 147, 317 ruling rows carry words. 131 of them carry a line reference. 74 of the 131 also carry a sentence with no reference that is not a bare agreement, so the refusal is silent on them. 57 rows have every sentence referenced. The guard was set for night 143's m263, which corrected the request item in an unnumbered sentence. The costly lines of m131, 5 and 6, are the Critic's notes. An unnumbered sentence about the item does not correct a team note.

Point 4. `notes?` needs a digit after the word, so "note that line 3 is wrong" reads nothing new. "a note 5 words long" now names line 5, which empties the unnamed set of line 5 and can silence a refusal. It adds no fault, because the window after the reference must carry a fault cue. The five nights hold 32 "note" or "notes" tokens. Only three are followed by a number: 144 m294 "note 8", "Note 9", and 147 "Note 7". Each one is a real reference. The prose case does not occur in the records (observed: probe p34, 2026-10-14).

Point 5. `rulings_rule` computes `contested` as `i + 1 for i, r in enumerate(order) if per_item.get(r) == "contest"` after the key map. The door therefore never uses the seat's key order. The three artifact rows, 143 m6, 144 m6 and 143 m272, contest lines the words name under the page order, per the implementer's page reads. The ruling-time page is not in the run database, so this review did not re-run those three rows. The claim is (reasoned: the door's `contested` reads `order`).

Point 6. On the parent code, five of the seven new test functions are red: the s281 refusal, the note reference, the s171 refusal, the batch-line test and the bare-agreement test. The batch-line test is red only by `TypeError` on the new keyword. It calls the helper and passes `frozenset({5})` by hand, so the call site that computes `batch_lines` from `batches` has no test. The m131 and m65 tests call the helpers, not the door. No test pins the silence on m28 or m181. No test reads "notes 8 to 11" or "lines 8 to 11" into the named set of the new refusal. `test_m131s_words_land...` and the m263-shape test are green on the parent, as guards are. The file gives 39 passed at HEAD.

Point 7. The refusal text has three sentences, each under 20 words, in the active voice. It says "the principal's words" and uses no pronoun for the principal. The comments follow STE. `api.py` and the test file hold 0 CR bytes.

## (b) Findings

1. `rota/roles/api.py` 8355 to 8357, `_unnamed_contest`. Severity high. CONFIRMED: m131's words plus one sentence with no number land the full over-contest through the door (probe p1). 74 of 131 referenced replies hit the guard (probe p34). Fix: let an unnumbered sentence exempt only item lines (request and criteria), and keep refusing an unnamed contest of a team note.
2. `tests/rota/test_frame234_verdict_lines.py` 370 to 383. Severity low. CONFIRMED: the batch-line test calls `_line_refusal` with a hand-made set, and the parent fails it only by `TypeError`. Fix: add a door test on a page with a `batches` row whose unnamed contest lands.
3. `tests/rota/test_frame234_verdict_lines.py`, new section. Severity low. CONFIRMED by reading: no test pins m28 and m181 silence, or a range "notes 8 to 11" in the named set. Fix: add three parametrised cases through `_refusal`.

Outside the points: none found above low within the cap.

## (c) Probes

All under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4a757f92-bd97-4750-9830-bd149134e576/scratchpad/rv234/`.

- `parent/`: `git archive 0acf4c68 rota`, the parent package.
- `p1_door.py head|parent`: builds the 11-line page with `_present`, calls `rulings.rule` with s281's ruling, on m131 and on m131 plus one unnumbered sentence.
- `p34_nights.py`: reads `rulings` on `clickI_night143` to `147.db` read-only. It counts referenced replies with an unnumbered sentence and lists every "note" token.
- `p6_parent.py`: runs the seven new test functions against the parent package.
- pytest on `tests/rota/test_frame234_verdict_lines.py` at HEAD: 39 passed.

## (d) Usage

Input tokens: about 55k. Output tokens: about 7k. Total: about 62k. The count comes from the context counter, and the harness line is the authority.
