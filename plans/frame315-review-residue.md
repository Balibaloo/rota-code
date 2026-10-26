Verdict: does not stand for the branch. Commit 035d86c7 refuses the one exit that night 167's recorded words had, and it accepts a drop of the item's main sentence on a change request.

# Frame 315 residue review: a removal is an amend at the words door

- Worktree: `C:/Users/roman/rota_r315b` at 035d86c7, above de4e2fb0.
- Reviewer: a read-only agent on Opus, 2026-10-26.
- Databases: `D:/repos/rota/.rota/clickI_night163.db` to `clickI_night166.db`, all by `?mode=ro`.
- Not read: `C:/Users/roman/rota_n167g`, as the brief asks. So night 167's full reply texts are not read here.

## (a) The verdict on each point

1. The removal forms: a finding stands. The forms match his recorded form, but that form points at no sentence. "remove" also matches a change request. Findings 1 and 2.
2. The sentence pick: CONFIRMED as described, with two defects. A request that names no sentence gives no removal, and a change request can point at the main sentence. Findings 1, 2 and 4.
3. The subset rule: the false-refusal count is 0 on each of the four nights. No landed assert dropped a sentence.
4. `_item_sentences` and "Line N": CONFIRMED for the m57 shape. The count of changed choices is 0. The cue also matches "check" as a verb. Finding 3.
5. `_item_sentence`: CONFIRMED. One caller at de4e2fb0, `_amend_step`. No test imports it.
6. The receipt: right. A `removed` key states a true fact on any wake. Finding 6 notes one gap.
7. Blast radius: `1 failed, 445 passed`. The one red is `test_invoke_door.py::test_a_session_with_no_batch_reads_the_root`, red on the base too.

## Point 1. The removal forms

The list at `rota/roles/api.py:1467`, each form bounded by word edges and read case-blind:

- "take it out", "take that out", "take this out", "take them out", and the same four with "off"
- "remove"
- "is not part of what i asked"
- "keep only what i asked for"
- "not what i asked"

Against his words:

- The loop record quotes none of his replies to m66, m75, m84, m95, m105 or m118. Section 1 quotes the line 1 text of the call rows of m66 and m118. Those rows are the present pages, not his replies.
- `plans/stack.md:1337` quotes his one reply form for the six pages: "take it out and keep only what I asked for". The forms "take it out" and "keep only what I asked for" match it.
- The test constant `M66` ("Someone added my note about the failing check ...") comes from the residue brief. No record that this review read holds it.
- "remove" matches a change request. "Remove the fallback to the bare home folder and use the Local folder" matches. "Do not remove the warning, just change it" matches too. Finding 2.

## Point 2. The sentence his words point at

`_removal_sentence` (`api.py:1473`) scores each item sentence by his words that share a stem with that sentence and with no other sentence. It reads the removal sentences first, then all of his words. A unique best score wins.

- His words name none: the result is None. The step falls back to the old amend. The door then refuses any drop. Finding 1.
- His words name two: the higher score wins, or a tie gives None. The door accepts a drop of one sentence only, so a drop of both is refused. Finding 4.
- His words are in no sentence: the result is None, the same as "name none".
- The second pass reads all of his words. A removal request with a change sentence can point at the sentence that the change names. Finding 2.

## Point 3. The subset rule over nights 163 to 166

Method: each `problem.assert` row of `tool_calls`, its full text from `turns.completion`, landed when `receipts` holds the session and the item. Only `problem_assert` writes `items.text` (the map, `table items`). So each item's text chain is complete from its first assert. `_dropped_sentences` ran on each landed change.

| Night | Landed asserts | Landed drops | False refusals |
|---|---|---|---|
| 163 | 10 | 0 | 0 |
| 164 | 7 | 0 | 0 |
| 165 | 10 | 0 | 0 |
| 166 | 9 | 0 | 0 |

The false-refusal count is 0. The four nights do not exercise the new refusal. So the count gives no evidence for or against the rule. Night 167, which these databases do not hold, is the case that exercises it. Finding 1.

## Point 4. `_item_sentences` and the "Line N" rule

- CONFIRMED: with m57 on a one-sentence item, the step names "line 10 of the page" and offers no amend (test 1, green).
- A sentence with "Line N" is out by `_PAGE_CUE` for any N, line 1 included. This rule existed before the commit. The new code reads "Line N" with N not 1 only to name the line in step 2.
- Contested wakes: night 163 has 6, all on `format_filename_example` (s159, s163, s167, s179, s184, s189). Nights 164 to 166 have 0.
- The old step offered a sentence on 5 wakes and none on s179. The new rule keeps each offered sentence as an item sentence. So the changed choices are 0, and no reply judges a changed choice.
- Outside the count: the s167 offer, "I don't know whether that example is there ...", is not about the item. The new rule still offers it.

## Point 5. The removed `_item_sentence`

`git grep` at de4e2fb0 finds one definition (`api.py:1428`) and one call (`api.py:1448`, in `_amend_step`). The other hits are in `plans/`. At 035d86c7 no code or test names it.

## Point 6. The receipt

The receipt (`api.py:2224`) adds `"removed"` when the new text is the old sentences in order with some out. The key states what left the item. It does not claim that he asked. So a ledger reader gets a true fact on any wake. One gap: a rewrite that changes a sentence and drops another gives no `removed` key. Finding 6.

## Point 7. Blast radius

```
ROTA_MODEL=qwen3:8b python -m pytest tests/rota/test_frame221_assert_words.py tests/rota/test_frame316_w3.py tests/rota/test_desk_guards.py tests/rota/test_frame240_land_lifts.py tests/rota/test_invoke_door.py -q -p no:cacheprovider
1 failed, 445 passed, 5 warnings in 76.24s
FAILED tests/rota/test_invoke_door.py::test_a_session_with_no_batch_reads_the_root
```

## (b) Findings

1. `rota/roles/api.py:1473-1502` and `1867-1872`. High. CONFIRMED. His recorded form "take it out and keep only what I asked for" points at no sentence. The new door refuses the drop of the appended test sentence. The base door accepted that drop. The step still offers an amend "with his sentence" that quotes his removal request, the shape that made s187 and s199 append. Probe p3: base LANDED, head REFUSED. This review did not read the whole night 167 reply, so the full text may point. The tests use a constructed quote, which hides the gap.
   Fix: with a removal form and no pointed sentence, point at the item sentence that `_names_other` marks against the rest. Never offer a removal request as the amend sentence. Add a test with the form at stack.md 1337.
2. `rota/roles/api.py:1467` and `1869-1870`. High. CONFIRMED. "remove" matches a change request, and the second pass reads all of his words. "Remove the fallback to the bare home folder and use the Local folder" points at the main sentence. The door accepts the drop of that sentence and returns `removed`. The early `return None` skips the lost-name check. On the base, that check refused the same assert because the text drops `get_app_dir`. "Do not remove ..." matches too.
   Fix: read the pointed sentence from the removal sentences only. Require an object of removal, such as "it", "that", "the note" or "the sentence", and no negation. Run the lost-name check before an accepted drop returns.
3. `rota/roles/api.py:1431-1443`. Med. CONFIRMED. `_OTHER_CUE` matches "check" as a verb and "file" or "test" in a correction about the item. "The function should check LOCALAPPDATA before APPDATA" is an "other" sentence. As his only sentence, step 2 tells the seat not to amend. The door then refuses an assert that appends that sentence. The name test is a substring test, so "file" in "profile" counts as named.
   Fix: match the nouns only, such as "its check", "the test", "the tests" or a file path, and test the item words by whole word.
4. `rota/roles/api.py:1869`. Low. CONFIRMED by reading. `_removal_sentence` returns one sentence. A request to remove two sentences gets a refusal for the drop of both.
   Fix: return the list of pointed sentences, and compare the drop with the list.
5. `tests/rota/test_frame221_assert_words.py:516-517`. Low. PLAUSIBLE. The `M66` constant is not a recorded quote. The record holds a different form, so the four tests prove a form that the night did not send.
   Fix: build the m66 test from the recorded reply text, read from the night 167 database by `?mode=ro`.
6. `rota/roles/api.py:2224`. Low. CONFIRMED by reading. The `removed` key appears only on a pure subset. A rewrite that drops a sentence and changes another reports no removal.
   Fix: accept, or name the key `dropped_in_order`, so that a reader does not take its absence as "nothing left".

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ad481e08-d0cc-4317-a992-02d5208ea7e8/scratchpad/r315/`.

- `p1.py`: `_REMOVAL_ASK`, `_removal_sentence` and `_amend_step` on 11 word sets. The sets are the recorded form, the m66 quote of the brief, change requests, "Do not remove", two sentences, none and absent.
- `test_p2_probe.py` and `test_p3_probe.py`: the door end to end through the fixtures of the test file. `test_p3_probe.py` ran at head and on a `git archive` of de4e2fb0 in `r315/base/`, with the new test file copied in for its constants.
- `p4.py` and `p5.py`: a first scan, rejected because `turns.user` repeats earlier tool lines.
- `p6.py`: point 3, the landed assert chains and `_dropped_sentences` over nights 163 to 166.
- `p7.py`: point 4, the contested wakes and the sentences that the old step offered, classified by `_names_other`.
- One `python -c` call: `_names_other` and `_amend_step` on "check" as a verb, "profile" and "the utils file".
- The pytest run of point 7, from the worktree root.

## (d) Counts

- Point 3, false refusals: night 163 0, night 164 0, night 165 0, night 166 0. The total is 0, out of 36 landed asserts and 0 landed drops.
- Point 4, changed choices: 0 out of 6 contested wakes, all on night 163.
- Point 7: 1 failed, 445 passed. The one red is the known red.

## (e) Usage

The harness gives no per-agent token split. The session counter moved from about 14,986k to about 14,909k tokens left. So this review used about 77k tokens, input and output together. That is past the cap of about 40k in the brief. The causes are the rejected first scan of point 3, the base comparison and a failed write of this record.

# Second look at 2383c991

Verdict: stands for the branch. Commit 2383c991 closes both high findings. Two low findings and one older med finding remain.

- Method: this review did not run `git checkout` in the worktree. The reviewer rules forbid a git command that changes a tree. A `git archive` of 2383c991 in the scratchpad (`r315/head2/`) gives the same code. The worktree stays at 035d86c7.
- Sources: `git show 2383c991`, and the "Pass 1b" section of `f315_residue_pass1.md`.

## Point 1. The two highs

- CONFIRMED, closed. His recorded words ("Line 1 still has the extra sentence about which tests to run, so please take it out and keep only what I asked for") are on an item whose second sentence came from s161 on `tick:contested`. The step names that sentence. The assert of the first sentence alone lands with `removed` (probe p9, case A).
- CONFIRMED, closed. On "Remove the fallback ...", the assert that drops the first sentence is refused. The assert that drops only the added sentence lands (probe p9, case B). `_added_sentences` never counts the first sentence.
- "Do not remove" now asks for no removal (`_removal_asks`).

## Point 2. The "added" rule

| Case | Result | Kind |
|---|---|---|
| A sentence of his request, held by no statement, also in a reply, on an item with a contested receipt | Counted as added. The drop lands. | Over-count, CONFIRMED (p9 case C) |
| A sentence that an amend added as a paraphrase, not a copy of his reply | Not counted. The drop is refused, and the step says "nothing was added". | Miss, CONFIRMED (p9 case D) |
| Two added sentences | Both counted. The drop of both lands. | Correct (p9 case E) |

- The contested receipt is a fact about the item, not about the sentence. One contested amend makes every later sentence that copies a reply a candidate.
- Over nights 163 to 166, the over-count is 0 items. Each text that an assert landed is in the scan (probe p8b). Only `format_filename_example` on night 163 has a contested receipt, and its text has one sentence. Each other item has one sentence, or it is `how_it_works` from orient with no copy of a reply. So the four nights do not exercise the rule.

## Point 3. The pronoun rule and the removed cue

- CONFIRMED. m57 gives no item sentence. "Its check ..." follows "Line 10 is still wrong." and counts as a page sentence. The step names line 10 and offers no amend (p9 case F, test 1 green).
- CONFIRMED. m24's correction stays an item sentence, and the step offers it (p9 case F, the m24 test green).
- The check, test and file cue is gone, so finding 3 of the first look is closed.
- A sentence of the item that starts with "Its" or "Their" and follows a page sentence is lost. "Line 3 is fine. Their folder must be Local when roaming is False." gives no item sentence (p9 case F). Low.

## The five files

`1 failed, 446 passed`. The one red is `test_invoke_door.py::test_a_session_with_no_batch_reads_the_root`, the known red.

## Findings of the second look

7. `rota/roles/api.py:1474-1505` at 2383c991, `_added_sentences`. Low. CONFIRMED by p9 case C. A sentence of his request that no statement holds word for word, and that he repeats in a reply, counts as added once any contested receipt exists. The count on nights 163 to 166 is 0.
   Fix: count a sentence as added only when it is absent from the item text before the first contested receipt. Or keep an item text per version.
8. `rota/roles/api.py:1474-1505` at 2383c991. Low. CONFIRMED by p9 case D. A paraphrase that an amend added copies no reply, so a removal cannot take it out. The step says "nothing was added", which is not true. The old wall comes back for a paraphrase.
   Fix: say "no amend added a copy of his reply" in place of "nothing was added". Or read the added sentence from the receipt's session call.
9. `rota/roles/api.py:1428-1449` at 2383c991. Low. CONFIRMED by p9 case F. A sentence that starts with "Its" or "Their" after a page sentence is always a page sentence, even when it is about the item.
   Fix: accept for now. Read it again if a night shows a lost correction.
10. Outside the points, older than the commit. Med. CONFIRMED by p10 on de4e2fb0 and by p9 case A at 2383c991. On a contested wake, the paraphrase "In get_app_dir, use AppData." of a two-sentence item lands. No check refuses an assert that is not a subset in order and adds no new word but loses most of his words.
    Fix: refuse an assert that loses a sentence of the item text with no removal request, when the sentence is not a subset match.

## Probes of the second look

All are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ad481e08-d0cc-4317-a992-02d5208ea7e8/scratchpad/r315/`.

- `head2/`: `git archive` of 2383c991. The five files ran there.
- `head2/tests/rota/test_p9_probe.py`: cases A to F through the fixtures of the test file.
- `base/tests/rota/test_p10_probe.py`: the paraphrase case on de4e2fb0.
- `p8.py` and `p8b.py`: the added rule over each text that an assert landed on nights 163 to 166, read-only.

## Counts of the second look

- Over-count, the items where the rule calls a ratified sentence added: night 163 0, night 164 0, night 165 0, night 166 0.
- The five files: 1 failed, 446 passed.

## Usage of the second look

The session counter moved from about 14,909k to about 14,885k tokens left. So the second look used about 24k tokens, inside its cap of about 25k.
