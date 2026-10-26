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
