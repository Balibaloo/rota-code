# Frame 234, pass 1b: the diff review of 474a6b43

Meta workflow. Read-only review of the Liaison's ruling door on the worktree `C:/Users/roman/rota_rv234` at 474a6b43, over 39e2fba7.

Verdict: accept. Findings 1 and 2 below are low and fail open. They can go to a later pass or wait for the next night's ratio.

## (a) Verdicts on the points

1. Review 1's findings: all eight are fixed. Findings 1 to 4 are CONFIRMED fixed by probe. Findings 5 to 8 are fixed by a read.
2. Counts: night 146 refuses 4 of 4 over-contests. Nights 143 to 146 refuse 0 right rulings.
3. The no-number skip keeps s122, s133 and s245 refused. A polite closing sentence lets a line-1 over-contest through. Night 146 held none.
4. `_BARE_AGREEMENT` matches "Ok, go ahead." and "Yes.". It misses "Looks good to me." and "Approved, thanks.". It does not match "Fine, but line 3 is wrong.".
5. `request_first` is `not shift and _is_request_item(conn, order[0])`. On a batch page, `request_block` numbers the request items before the touches. So line 1 is the item, and the value is true. This is read only. The fixture probe did not run.
6. STE: the texts, comments and brief line pass. The brief grows by about 30 characters. The budget effect is nil.

## Points in detail

Point 1. `p1_findings.py` ran `_line_reading` and `_line_refusal` from the worktree with `request_first` forced true. 144 m193 and 144 m236 return None through the "names line 1" skip. 143 m263 returns None through the no-number skip. 143 m339 now reads faulted {2}, matched {}. "Line 4 doesn't match what I asked for" reads faulted {4}, and the refusal is None. Finding 5: the landing line now says "On a page that starts with the request, line 1 is the request." Finding 6: the continuation of `_quotes_line` now needs a leading space or tab. Finding 7: `_line_refusal` returns None when `named` is empty. Finding 8: the file adds door tests for a clarify, an empty page, the quote branch, a fault past the end, and the four recorded guards. No test names the shift skip.

Point 2. `p2_counts.py` uses the key order of `per_item`, the batch lift on `head_commit` only, `quoted` false, and `_is_request_item` on the end-state database.

| Night | Rows with words | Over-contests refused | Right rulings refused |
|---|---|---|---|
| 143 | 76 | - | 0 (m272 refuses only with `request_first` forced true; review 1 calls it an order artifact) |
| 144 | 90 | - | 0 |
| 145 | 44 | - | 0 |
| 146 | 66 | 4 of 4: m35, m45, m119 (line 1), m271 (reversal) | 0 |

Point 3. The three replies of s122, s133 and s245 are the rulings on m35, m45 and m119. Each sentence of each reply names a line, so the skip does not fire. The refusal holds. The shape that passes is a reply that faults line 3, contests line 1, and adds one sentence with no line number. "Line 3 is wrong. Thanks.", "Line 3 is wrong. Everything else is fine." and "Line 3 is wrong. Good work." all return None. The recorded principal writes this shape: 143 m6 and 144 m6 end with "The rest of the page looks fine to me.". On night 146, every row that contests line 1 with line 1 unfaulted is refused. So night 146 held no reply of the shape.

Point 4. `p3b_shape.py` results: "Ok, go ahead." true, "Yes." true, "Okay." true, "Yes, go ahead!" true, "Looks good to me." false, "Approved, thanks." false, "Thanks." false, "Fine, but line 3 is wrong." false. The last result is right. The two misses widen the skip of point 3.

Point 5. `rulings_rule` takes `order` from `render_page`. For a present page with touches, `render_page` calls `request_block` first. `request_block` appends each request item, then its criteria, then the touches follow. So the refs `[bg_1, echo_json, ...]` give `order[0] = echo_json`. `_is_request_item` reads the same state at render and at rule time, so the two agree. A page with quoted words ("You asked:") puts a statement at line 1, and `request_first` is false there by design (m193). `p5_batch.py` rendered m35, m63 and m84 from the end-state copy of night 146. Each rendered an empty `order`, because the batches are closed. So the probe proves nothing for point 5. A fixture with an unbuilt batch was not built inside the cap.

Point 6. The refusal texts are unchanged from pass 1, which review 1 passed. The new comments use the active voice and cite the review findings. The brief line is one sentence of 11 words.

## (b) Findings

1. `rota/roles/api.py:8139-8141`. Low. CONFIRMED by a synthetic probe. A sentence with no line number releases the line-1 refusal, even when the sentence only agrees. "Line 3 is wrong. Everything else is fine." with line 1 contested lands the contest. Nights 143 and 144 hold the closing sentence "The rest of the page looks fine to me.". Night 146 held no such reply. Fix: release only on a no-number sentence that holds a `_LINE_FAULT` cue or holds no `_LINE_MATCH` cue.
2. `rota/roles/api.py:7756-7757`. Low. CONFIRMED. `_BARE_AGREEMENT` misses "Looks good to me." and "Approved, thanks.". The miss feeds finding 1. Fix: allow a tail of "to me", "thanks" or "thank you", and add "thanks" to `_AGREE`.
3. `tests/rota/test_frame234_verdict_lines.py`. Low. PLAUSIBLE. No test covers a confirm page (the shift skip) or a batch page with line 1 contested. Point 5 rests on a read only. Fix: add one door test on refs `[bg_1, calculate_tip, how_it_works, l_1]` with an unbuilt batch, and one on a confirm page.

Outside the points: the implementer's probe `f234/p1b_nights.py` puts `D:/repos/rota` on `sys.path`, not a worktree. Its result is valid only while the checkout holds the same `api.py`. This is a note, not a finding.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/58da19ca-3cc0-49b5-a8a7-5edb2f08ef46/scratchpad/rv234b/`. Each imports from the worktree.

- `p1_findings.py`: findings 1 to 4 through `_line_reading` and `_line_refusal` on the recorded words of 143 m263, 143 m339, 144 m193 and 144 m236, plus four negation strings.
- `p2_counts.py`: the refusal counts on nights 143 to 146, read only, with the `head_commit` lift.
- `p3_skip.py`: the sentence split of m35, m45, m119 and m271 on night 146, with `_LINE_REF` and `_BARE_AGREEMENT` per sentence.
- `p3b_shape.py`: each line-1 contest that is not faulted on nights 143 to 146 and its release reason, four synthetic replies, and eight agreement strings.
- `p5_batch.py`: `render_page` on batch-first pages of a copy of night 146, `n146.db`. The result was an empty `order`.

No pytest run. No gate run.

## (d) Usage

Input tokens: about 36k. Output tokens: about 6k. Total: about 42k, from the context counter.
