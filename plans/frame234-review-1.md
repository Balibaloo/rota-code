# Frame 234, review 1: the diff review of 39e2fba7

Reviewer: an Opus agent, read-only, on the worktree `C:/Users/roman/rota_rv234` at 39e2fba7 over 7daf9fed. Meta workflow. Date: 2026-10-14.

Verdict: revise. The door refuses the four night-146 over-contests. It also refuses four right verdicts on nights 143 and 144. Findings 1 to 4 are the next pass's brief.

## (a) The verdict on each point

1. Reproduced: 4 over-contests refused (m35, m45, m119, m271), and no right verdict refused on night 146. The reader's direction is wrong on no refused reply.
2. Failed: the door refuses 4 right verdicts that landed on nights 143 and 144 (m263, m339, m193, m236). This is high.
3. Agree: the batch lift matches 2.D. No IndexError and no wrong index are reachable.
4. Holds: the regex reads the text of `render_page`. Case folding and punctuation work. The capture also takes section headers (low).
5. The two-word window passes both phrases. Recorded reply 143 m339 shows that the window keeps a match that a later fault in the clause reverses. A negated cue reads as a match.
6. The refusal texts are STE and name no pronoun. The brief line "Line 1 is the request" is false on shift pages and on pages that open with a note.
7. Nine red on the parent and four green, by the diff. Not covered: the shift skip, a clarify, an empty `order`, the quote branch inside the door, the "the lines they name" fallback.
8. The longer brief fits. No hard prompt budget exists. `_fit_budget` charges the system prompt against the transcript budget.

## (b) Findings

1. `rota/roles/api.py:8108-8115`. High. CONFIRMED. The line-1 refusal fires when the words name line 1 in words that the cue list misses. Night 144 m193 says "Line 1 isn't a request, so please take it off the page". The reader gives faulted {2}, line 1 (statement `s3`) is contested, and the door refuses. Night 144 m236 says "On line 1, the echo tests are right, but the termui and context test files don't belong there". The reader gives faulted {12}, line 1 (`echo_json`) is contested, and the door refuses. On m193 the refusal text "Line 1 is the request" is also false, because line 1 is a quoted note. Fix: skip the line-1 refusal when any reference names line 1, whatever its cue, and when `order[0]` is not the request item of the page.
2. `rota/roles/api.py:8108-8115`. High. CONFIRMED. The line-1 refusal fires on a request correction that names no line. Night 143 m263 says "Line 3 is wrong ... Also, take the version from the running interpreter's version info, written as major.minor.micro." The seat contested line 1, and line 1 on night 146 carries "major.minor.micro". The new door refuses that contest. Fix: skip the line-1 refusal when a sentence of the words, split at `.`, `!` and `?` only, holds no line reference. This keeps s122, s133 and s245 refused.
3. `rota/roles/api.py:7788`. High. CONFIRMED. A match cue before a fault cue in one window wins. Night 143 m339 says "Line 2's text is right now, but its check still passes a show python switch ... no such switch exists." The reader gives matched {2}, and the door refuses the right contest on line 2. Fix: put the lines in `matched` only when the window holds no fault cue.
4. `rota/roles/api.py:7752-7754`. High. CONFIRMED by a synthetic probe. A negated match cue reads as a match. `_line_reading("Line 4 doesn't match what I asked for")` returns `(set(), {4})`, so the door refuses a contest on line 4. No recorded reply holds the phrase. Fix: drop a match cue that `not`, `n't` or `never` precedes within two words, and count it as a fault.
5. `rota/roles/prompts/liaison/landing.md:43-44`. Low. PLAUSIBLE. "Line 1 is the request" is false on a shift page, which line 39 describes, and on a page that opens with a statement. The seat reads the line on every landing. Fix: write "On a page that starts with the request, line 1 is the request."
6. `rota/roles/api.py:7798`. Low. CONFIRMED. The capture of line 1 runs on into an unnumbered section header. On night 146 m45 the capture ends with "It must:". A five-word quote across the header can count as a quote of line 1. Fix: stop the continuation at a line with no leading indent.
7. `rota/roles/api.py:8110-8112`. Low. PLAUSIBLE. When every faulted number is past the end of the page, the door still refuses line 1. The text then says "The words fault the lines they name", which names no line. Fix: refuse only when `named` is not empty.
8. `tests/rota/test_frame234_verdict_lines.py`. Low. CONFIRMED by a read. No test covers the shift skip, a clarify, an empty `order`, or the quote branch inside `rulings_rule`. `test_an_approval_and_a_named_fault_land_as_before` tests only "fine". Fix: add one door test per branch, and the four recorded replies of findings 1 to 3 as door guards.

Outside the points:

9. A measurement note, not a defect. In the end-state night DB, `bg_1` and `bg_2` are `abandoned`. The closed-status lift then adds line 1 to `faulted`, and m35 and m119 are no longer refused. At ruling time both batches were unbuilt, so the live door refuses them. A probe that reads the end state must apply the lift on `head_commit` only, or it reports 2, not 4.
10. The register-key red (`test_register_key::test_the_parameter_set_holds_the_shapes_that_would_break_it`) clears only after the 9 L1-LI re-records. Run the acceptance gate after the re-record.

## Points in detail

Point 1. The script `p3_146.py` uses the key order of `per_item` and the batch lift on `head_commit` only. It flags m35 (B), m45 (B), m119 (B) and m271 (A) of 23 contest rows. Line 1 of each page, read in `clickI_night146.principal.jsonl`, is the request. The reader misses some faults: on m6, "and so are lines 18 to 23" gets no direction. No miss on night 146 causes a refusal.

Point 2. `p1_nights.py` ran on nights 140 to 146 with the key order of `per_item`. That order is not the page order, because the seat writes contests first. `p2_render.py` re-rendered the pages, and only about half match the ruling-time id set. I checked each flag against the page text in the principal logs. Four flags are right verdicts: 143 m263, 143 m339, 144 m193 and 144 m236. The other flags are order artifacts: 145 m135, 144 m431, 144 m6, 143 m6, 143 m272, 142 m296 and 140 m15. The count is a floor, because the order is unsure on rows that the probe did not flag.

Point 3. The batch door at `api.py:8042-8071` refuses a non-approve on a built or closed batch line and names the item. The lift after line 8079 makes a fault on that line count against the item. The two agree. `order[n - 1]` has the guard `1 <= n <= len(order)`. `order.index` has the guard `item_id in order`. With no item line on the page, the lift skips, and the line-1 refusal can still fire on a contest of line 1. That result is the s122 intent.

Point 4. On the page text of m45, "ADD an Echo_JSON(obj) helper, next to echo!" counts as a quote. "add an echo json helper next" does not, because the word class keeps the underscore. "Line 2 is wrong." does not count. The sub-line "code that names these words" of line 1 is in the capture, and that is right for a files correction.

Point 5. "Lines 1 to 4 match what I asked for" gives matched {1 to 4}. "Lines 2 to 5 are wrong, so please match each one to code" gives faulted {2 to 5}. The recorded counter-case is 143 m339, finding 3.

Point 6. Both refusal texts name the lines and the action. The texts say "the principal", not "he". The brief line repeats the rule of line 30 for line 1, with an exception for the request. The brief line contradicts line 39 on shift pages, finding 5.

Point 7. On the parent, `_quotes_line` and `_line_reading` do not exist. Six tests import them and fail. Three door tests expect a `ValueError` that the parent does not raise. The four guards pass on the parent. That gives 9 red and 4 green.

Point 8. `rota/core/runner.py:986-999`, `_fit_budget`, returns `int(num_ctx / 2 * 3.97) - system_chars`. The brief grows by about 190 characters. The transcript budget shrinks by the same amount. A landing session has one wake with the page and the reply, so the cut does not fire.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/58da19ca-3cc0-49b5-a8a7-5edb2f08ef46/scratchpad/rv234/`.

- `p1_nights.py`: the door logic with the key order of `per_item`, on nights 140 to 146 (`mode=ro`).
- `p2_render.py`: `render_page` on each night DB, and the door logic with the quote check where the id sets match.
- `p3_146.py`: night 146 with the batch lift on `head_commit` only. It reproduces the 4.
- `p4_quote.py`: `_quotes_line` on the page text of m45, and `_line_reading` on 8 phrases.
- Inline `python -c` reads of `rulings`, `statements` and the principal logs for the flagged asks.

## (d) Usage

From the context counter: about 90k tokens in all, over the 60k cap. The input and output split is not in reach. Sub-agents: none.
