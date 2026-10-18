# Frame 296, review 1 of 9c4b5368

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_r296` at 9c4b5368, parent 069990f9. Date: 2026-10-18.
Verdict: accept with low findings. The change removes the line-1 cue on 7 of 7 wrong moves and keeps the named line on 5 of 5 replies that name one. No cassette holds the old text, so no case goes stale.

## (a) Verdicts on the points

1. The red case: CONFIRMED. The night 156 row s239 seq 2 holds the parent's text with "line 1, version_option_show_python". The next call revised line 1. The commit's predicate names no line on the same words and page.
2. The right cases: CONFIRMED. The new text withholds line 1 on 7 of 7 wrong moves. It keeps the named request line on 5 of 5 replies that name it by number. The quote branch fires on 0 of 25 refused turns.
3. The deviation: CONFIRMED. `_names_request` fires on 5 of the 7 wrong moves, the same 5 the report names. Two predicates for "the words name the request" now live in `api.py`, with different scopes (finding 3).
4. The pinned assertion: a design pin, not a ruling and not a measurement. Commit 2dace61b (2026-10-09) wrote it from `plans/frame190-design.md` lines 860 to 867, review amendment 2, finding 2.
5. The stale line: no case is stale. 0 of 33,900 cassette rows hold the old text in `system`, `user` or `completion`. The gate's re-record has nothing to cover.
6. The open questions: keep "line one" out of `_LINE_REF`. Write "the principal's words" in place of "his words".

## (b) Findings

1. `tests/rota/test_request_page.py:636-648`, low, CONFIRMED. The M400 case is the founding case of the refusal (frame 190, amendment 2). The right call there is a revise of line 5, `version_option_show_python`. The old text named line 5. The new text names no line, and the updated assertion pins that loss. M400 says "line one" in words, and no 5-word run of line 5 appears in M400. No fire on nights 139 to 156 had this shape, so the cost is one fixture, not a measured night. Fix: state in the test comment that M400 now gets no target, and count the shape on the next night.

2. `rota/roles/api.py:9718-9730`, low, PLAUSIBLE. The change is text only. No door refuses a revise of line 1 on words that name no request line. `contested` at line 9808 holds contests only, so `_line_refusal` never sees a revise. The new text still says "a revise of the request needs his words on the request". A seat that reads m125 as words on the request can still revise line 1, and bg_2 dies the same way. Fix: count the moves to line 1 after this refusal on the next night, and push a door frame if one recurs.

3. `rota/roles/api.py:9258-9276` against `9718-9722`, low, CONFIRMED. Two predicates answer "do the words name the request", with opposite results on m125. `_line_refusal` admits a line-1 contest on a line-1 number, a quote, or a sentence with no number that shares a content word with the request (`_names_request`). The revise refusal admits a line only on a number reference (`_LINE_REF`, `_ref_lines`) or a 5-word quote (`_quotes_line`). `_names_request` admits m125 sentences 2 and 3 ("version", "python", "flag"), and the new predicate does not. The new predicate admits a numbered sentence, which `_names_request` skips by design. So on m125 a line-1 contest passes the contest door, and the revise refusal says the words name no line. Fix: name the split in the comment at line 9711, or join both in one helper in a later frame.

4. `tests/rota/test_frame296_revise_note_text.py`, low, CONFIRMED. No test reaches the `_quotes_line` branch of the new predicate. The branch fired on 0 of 25 recorded turns. Fix: add one test with words that quote 5 words of line 1 and hold no number.

5. Outside the points. The implementer report, section "Step 1", low, CONFIRMED. The report says the refusal fired 19 times. The rows hold 25 refused turns in 19 sessions. The report says n144 s587 repeated the call three times and its session ended. The rows show 2 revise calls, then a contest of line 7 at seq 3. Fix: correct the counts in the frame's status line.

## The counts of point 2

The probe read every `clickI_night1*.db`. It found 25 refused turns in 19 sessions, nights 139 to 156.

- Wrong moves to line 1, words name no request line: n139 s180 (seq 3), n140 s240, n142 s503, n149 s151, n152 s158, n153 s148, n156 s239. The new text names no line on 7 of 7.
- Words name a request line by number: n140 s184, n143 s204, n154 s108, n156 s108 (line 1), n155 s236 (line 2). The new text names that line on 5 of 5.
- The other 7 sessions name no request line. The new text names no line on each. None of them moved the revise to line 1 under the old text.
- `_quotes_line` added a line on 0 of 25 turns. No reply holds "line one" or another written number.

So the no-line form fires on 14 of 19 sessions. It withholds a right target on 0 of 5 recorded right calls. The fixture M400 adds 1 withheld right target (finding 1).

## Point 3 in detail

The probe ran `_names_request` over the sentences with no `_LINE_REF` match and no bare agreement. The request texts were the request ids and the page's line 1 text.

- It fires on n139 s180 (sentence 2), n140 s240 (2), n152 s158 (2), n153 s148 (2) and n156 s239 (2 and 3). That is 5 of 7.
- It does not fire on n142 s503 and n149 s151.

The claim holds. With `_names_request`, the refusal names line 1 on s239, and the red test cannot pass.

## Point 4 in detail

`git log -S` on the old assertion returns 2dace61b and 9c4b5368 only. The design text at `plans/frame190-design.md:860-867` says "The refusal of 2.2.1 names every request line". The design took the text from a review amendment, not from Roman. A later frame may change it with a recorded reason, and 9c4b5368 gives one in its comment.

## Point 5 in detail

`rota/tools/gate.py:207-224` reads the stale set from `casestatus.status`: the cases with no recording against the current prompt. A recorded prompt carries the refusal only when a replayed call is refused and the next turn quotes the ERROR line. The register `D:/repos/rota/tests/rota/cassettes.db` has 33,900 rows. A read-only query for three phrases of the old text found 0 rows in `system`, `user` and `completion`. The phrases: "the team's note", "revise rewrites a line", "To drop the note, contest it". No brief or prompt file outside `plans/` holds the text. So no prompt hash moves, and the stale line stays as before.

## Point 6 in detail

1. "line one": do not read written numbers. M400 says "line one" for a line of an older page. On the m399 page, line 1 is `confirm_with_default_on_eof`, the wrong request. A reader of "line one" steers the revise to the wrong item, which is the failure frame 190 fixed. No reply of the 19 sessions uses a written number, so the change gains nothing.
2. "his words": write "the principal's words". The same refusal says "the principal" one sentence before. One word for one thing is the rule.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/6977407c-6cda-4904-bd57-2ba520a13d06/scratchpad/r296/replay.py`, run from the worktree with `PYTHONPATH` set to it. It reads every refused turn in `D:/repos/rota/.rota/clickI_night1*.db`, read-only. It parses the refused call's words, the old text's request lines, the page from the prompt JSON and the next call. It runs the commit's `_LINE_REF`, `_ref_lines`, `_quotes_line` and `_names_request` on each turn.
- An inline query on `clickI_night156.db`, s239 seq 2: the user prompt and the completion.
- An inline query on `clickI_night144.db`, s587 seq 1 to 4: the last ERROR and the completion.
- An inline read-only query on `D:/repos/rota/tests/rota/cassettes.db` for the three phrases of the old text.
- `pytest tests/rota/test_frame296_revise_note_text.py tests/rota/test_request_page.py -q` in the worktree: 110 passed, 4 xfailed in 86.87s.
- `git log -S` on the old assertion and on the refusal sign, and `git show 2dace61b`.

## (d) Usage

An estimate. The harness line holds the exact figure. About 60k input tokens, about 10k output tokens, about 70k total. No sub-agent.
