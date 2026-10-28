# F2 review, pass 2f: 1a57eb2c on f2c, against 480afc2d

**Verdict: NOT READY.** The top-level check does what the commit claims, and the replay of 240 calls changes one result, rightly. One finding is high. A `words` value inside a line object or an `acts` entry with no act still lands words he never said on the row. Six findings are low.

## (a) Verdicts on the points

1. The rule: the check refuses his words when the seat reformats them. It lands any character substring of his reply, "No." and "call line 4 wrong." included (findings 2, 3).
2. The replay: 1 of 240 results changes. Night 172 s214 call 55 moves from the naming refusal to the new refusal. The new refusal is right, because the seat cut his sentence to "Only the doc, the code stays the same."
3. The fixtures: the commit changes nine tests and adds two. Seven changed tests and both new tests still test what their names say. Two are judgement cases that the change weakened: `test_his_reply_alone_confirms_a_reading` and `test_an_act_rests_on_his_record_and_not_on_the_words_argument` (findings 6, 7).
4. The fallback: six readers in `api.py` read `body_text` alone. On a reply that `land` writes with no body, the door and those readers disagree (finding 5).
5. Law 6: yes. A landed row can carry words that are not his, through the nested line form or an `acts` entry with no act (finding 1). An act with its own words is checked by `_words_from` and is refused.
6. The gate: confirmed. The same 6 tests are red at the commit and at the parent. The touched files give 287 passed. The diff holds 0 CR bytes and no hunk outside the claim.

### Point 1, the probes of the rule

His reply is night 172 m129: "Fix the change ... the code stays the same. Line 11 is wrong: my answer asked for that fix and did not call line 4 wrong, so keep line 4 as it is. Lines 9 and 10 are read right, and all the other lines are fine."

| `words` | Result | Right? |
|---|---|---|
| "the code stays the same. Line 11 is wrong" (across two of his sentences) | lands | yes |
| "the code stays the same Line 11 is wrong" (his stop dropped) | refused | no, his words |
| "the code stays the same, Line 11 is wrong." | refused | no, his words |
| "Line 11 is wrong:" | lands | yes |
| "Line 11 is wrong," (his colon made a comma) | refused | no, his words |
| "did not call line 4 wrong," | lands | yes |
| "Lines 9 and 10 are read right;" | refused | no, his words |
| `"keep line 4 as it is"` (the seat adds quotes) | refused | no, his words |
| "Put back the two removed lines." (paraphrase) | refused | yes |
| "call line 4 wrong." (his "not" cut off) | lands | no, he said the opposite |
| "No." / "I." / "ne 4 wr." (letters inside his words) | lands | no |
| his `Line 3 says "use Roaming."`, seat `Line 3 says "use Roaming".` | refused | no, his words |
| his straight apostrophe, seat curly apostrophe | refused | no, his words |

The check also refuses a sentence of an earlier answer of the thread, which `_words_from` accepts for an act. That case is PLAUSIBLE. No probe ran.

### Point 2, the replay

The method is the method of review p2. The three registers were copied to scratch before any open, with their WAL files. Each call runs on an in-memory copy at the state of its trigger.

- 240 calls, 150 with a top-level `words`. The parent and the commit give 63 lands and 177 refusals each.
- 1 result changes: 172 s214 call 55, refusal to refusal. His m93 says "Only the docstring changes and the code stays the same." The seat wrote "Only the doc, the code stays the same." The new text is right on his words.
- 9 more calls pass `words` that are not in `body_text`, because the body is empty. The fallback to `entry_for` finds the words, and all 9 land as at the parent. Without the fallback, the check refuses 8 approve calls and 1 clarify contest.

### Point 3, the fixtures

- `test_words_the_seat_adds_to_his_reply_are_refused`: still tests its name. The refusal now comes from the new door.
- `test_the_probe_sentence_alone_is_refused`: new, tests its name. Red at the parent.
- `test_s271s_call_with_its_nested_words_as_words_lands`: new, tests its name. The row words come from `acts`, so the assertion on `row["words"]` does not read the top-level `words`.
- `test_an_act_rests_on_his_record_and_not_on_the_words_argument`: judgement case (finding 7).
- `test_frame306_clarify_about.py`, three tests: an entry holds the words that the test passes. This is the shape that `land` writes. Each still tests its name.
- `test_his_reply_alone_confirms_a_reading`: judgement case (finding 6).
- `test_request_page.py`, two tests: `record_entry` gives m400 its words. Each still tests its name.
- `test_runner.py` s336: m178 now holds the reply of night 151. A probe on a copy of the night 151 register shows that the fixture equals the recorded body, 499 characters.

## (b) Findings

1. **rota/roles/api.py 13801 to 13814 and 11916 to 11922, high. CONFIRMED.** The check reads the top-level `words` only. On m129, `rulings={"11": {"verdict": "contest", "words": "Line 4 is wrong too."}}` lands. The `ruled_refs` row carries "Line 4 is wrong too." with `words_from` None. The same `words` in an `acts` entry with no act also lands. `_insert_landed_rows` in `principal.py` copies the words to the landed row, so they reach the owner of the row. The comment of the commit gives this as the reason for the check. The parent does the same, so the hole is not new. Fix: refuse the `words` of each shape that `_words_outside` against his reply and `_words_from` both fail to find.
2. **rota/roles/api.py 11867 to 11882, low. CONFIRMED.** `_holds_span` is a character substring test. "No.", "I." and "ne 4 wr." land as his words on m129. "call line 4 wrong." lands, and `rulings.words` stores it, although he wrote "did not call line 4 wrong". The verdicts still rest on his reply, because the doors read `his`. Only the words to the owner change. Fix: match whole words, and require the span to start and end at his clause marks.
3. **rota/roles/api.py 11873 to 11876, low. CONFIRMED.** The rule refuses his own words after a small change of marks. A dropped stop between two of his sentences, a comma for his colon, added quotes and a curly apostrophe are each refused. The seat can try again, but each refusal costs a turn. Fix: drop quote marks and fold the apostrophe forms before the compare, and compare the sentence without its final comma, colon or semicolon.
4. **rota/roles/api.py 11877 to 11881, low. CONFIRMED by the replay.** The refusal quotes his first sentence, not the sentence of `words` that failed. On s214 the seat copied his first sentence exactly and cut his second. The refusal then showed the sentence that the seat had right. Fix: quote the first sentence of `words` that his reply does not hold, then his first sentence.
5. **rota/roles/api.py 11753, 11763, 11891, 13594, 13845, low. CONFIRMED.** Only the new check reads `entry_for`. The read-back guard, the naming and fault doors, `_shift_acts_conflict`, `_words_from` and the note clause reader read `body_text` alone. With m129 in the shape that `land` writes, the s271 call is refused: "His reply does not say that line 9 is right". He wrote "Lines 9 and 10 are read right". The claim of the commit names clarify answers only. The three registers hold 34 present and 10 confirm answers with an empty body too. No call of nights 170 to 172 reaches the disagreement. Fix: give `_his_reply` the entry fallback, and make every door read his reply through it.
6. **tests/rota/test_read_back.py 298 to 300, low. CONFIRMED.** The call now passes `words` equal to his reply, as the spy showed. A guard that reads `words` in place of his reply then still refuses, so the test no longer pins the rule of its docstring. "ok" still passes the new check when his reply holds "ok" inside a word, such as "look" or "token". Fix: give his reply a word that holds "ok", for example "I took a look.", and pass `words="ok"`.
7. **tests/rota/test_frame305_note_revise.py 205 to 216, low. PLAUSIBLE.** The first call now meets the new door, and the second call repeats `test_an_act_on_words_he_did_not_say_is_refused`. No test now passes an act span that `words` holds and his record does not. That case still exists, because `words` can put his sentences in a new order. An act span across the new sentence border is then in `words` and not in his reply. Fix: pass his sentences in a new order as `words`, with the act on a span across the border, and assert "his words do not hold it".

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/77c8dc39-1322-4ba4-bcb6-9a1031822837/scratchpad/p2f/`.

- `parent/` and `head/`: `git archive` of `rota` at 480afc2d and at 1a57eb2c. `pfull/`: the whole parent tree.
- `db/`: copies of the night 151, 170, 171 and 172 registers, with the WAL files of nights 170 to 172.
- `replay.py`: replays the 240 calls at each tree. The output is `par.json` and `new.json`. `diff.py` compares them.
- `count.py`: counts the top-level and the nested `words` that his body does not hold.
- `probe_rule.py`: the span table of point 1, and the nested forms of point 5, on m129, at the head and at the parent.
- `probe_fallback.py`: m129 with an empty body and the entry, at the head (finding 5).
- `spy_his.py`: a pytest plugin that prints what the check compares. It ran with `-n0` on `test_read_back.py` and the frame 306 and frame 305 tests.
- Point 6: the touched files and frame 337 at the head gave 287 passed. The 6 reds of the builder report gave 6 failed at the head and in `pfull/`. The 6 test files of the head on the parent code gave 3 failed: the two refusal tests and the frame 305 test.
- The diff and three of its files hold 0 CR bytes, counted on the bytes of `git diff` and `git show`.

## (d) Usage

Input about 120k tokens, output about 20k tokens, about 140k in total. These are estimates, because the harness shows no per-call counts. The cap was 60k, and the replay and the probes used the rest.
