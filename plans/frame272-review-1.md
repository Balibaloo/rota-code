# Frame 272, review 1: pass 1 at b230820f

Verdict: do not accept b230820f for the branch. The rewrite names wrong rows on s239, the case the frame names as its red test. The page name also gives the seat no contrast, because the seat never sees the id of the present page.

Reviewer on Opus, read-only. Worktree `C:/Users/roman/rota_r272` at b230820f. No gate, no re-record and no model call ran.

## (a) The claim, point by point

1. Point 1, NOT MET. Over 83 converse wakes of nights 158 and 159, 81 carry a reply to an earlier page. The new builder rewrites 201 replies and names 693 rows. 73 rows are not the row he saw (33 on night 158, 40 on night 159), measured on the end-of-night rows. s209 of night 158 names every row right. s239 of night 159 names 2 of 3 rows wrong, and the wake-time record confirms the drift.
2. Point 2, the doubt is real and high. Page m105 of night 159 lost its line 1 before s239 woke. Page m24 of night 158 lost its guess line after echo_json merged. The rewrite then names a neighbour row as the faulted row.
3. Point 3, NOT MET. The seat now reads "Row guess:confirm_default_on_eof of page m50 is wrong". Its own `landing.lines` maps line 2 of the present page to the same row id. The prompt never names the present page (m89), so "of page m50" has nothing to differ from. The text can still be read as a fault of the present line 2.
4. Point 4: 2 recorded L1 cases change their prompt. Both are in `tests/rota/cases/l1_liaison2.yaml`: `L1-LI-words-about-another-function-get-their-own-statement` and `L1-LI-a-new-request-on-another-function-takes-no-supersedes`. Each gains a `"page"` key on an "ok" reply. The text does not change, but the prompt hash does, so the gate shows both STALE.
5. Point 5, MET with one note. The commit changes `rota/core/runner.py` and adds the test file only. The brief's diff from 573b0528 also shows `plans/stack.md`, because the parent of b230820f is f0ed15aa, not 573b0528. The new test file and `test_chat_intake.py` give 12 passed with `-n 0`.

## (b) Findings

1. `rota/core/runner.py` 2557-2563, high for the night and for the frame. CONFIRMED. `_recent_chat` takes the old page's order from `render_page` on today's rows. On night 159, s239's own landing shows bg_2_summary under "How it is described" (version 2, `is_description` 1). Page m105 showed it as line 1 under "You asked". A present page with touches does not number a described row, so m105 now renders as [cr_echo_json_prints_compact, bg_3]. s239's m106 then reads "Row cr_echo_json_prints_compact of page m105 is wrong", "Row bg_3 of page m105 should say ..." and "Line 3 of page m105 should name ...". He faulted bg_2_summary and cr_echo_json_prints_compact. The same drift hits m25 of night 158 after echo_json is delivered. The guess row leaves the page, and "Line 2" becomes "row echo_json". The unit test passes because its rows are ledger notes, and nothing moves them. Fix: record the order of each page when the principal is shown the page, for example as config `order:<page id>`, and read that record in `_recent_chat`.
2. `rota/core/runner.py` 2253 and the landing in `resolve_inbound`, high for the frame. PLAUSIBLE. The probe of s209's prompt finds no "m89" anywhere. `landing` holds `page_kind`, `page`, `lines`, `reply` and `line_rows`, but no page id. So "of page m50" and "of page m105" have no present page id to differ from. Each rewritten row id also maps straight to a present line through `landing.lines`, when the present page shows that row. For m51 against m89, the row id is a closer pointer to present line 2 than "Line 2" was. Only the replay of s208 and s209 turn 1 can measure the effect. Fix: add the present page id to `landing`, so each rewritten reply names a page that the seat can compare.
3. `rota/core/runner.py` 2489-2495, low. CONFIRMED. A probe ran `_page_named_lines("Ok: 2 is wrong. 3 is fine. Lines 1 to 9 too; note 2 stays.", "m5", ["a","b","c"])`. It gave "Ok:row b of page m5 is wrong. row c of page m5 is fine. Row a, row b and row c of page m5 too; ...". A bare number loses its leading space, and its sentence starts in lower case. A range past the page is cut at the page end with no trace, but the docstring says that a number past the page stays a line. Fix: keep the matched leading space, give a sentence start a capital, and keep a range end past the page as "line N".
4. Commit parentage, low. CONFIRMED. `git log` shows b230820f on f0ed15aa. 573b0528 is a sibling commit that adds the claim tag and the status line of frame 272 to `plans/stack.md`. A plain diff from 573b0528 reads as a revert of both lines. Fix: rebase or cherry-pick b230820f onto the branch head before a merge.
5. The probe of point 1, low, outside the points. CONFIRMED. On night 159, 5 old turns do not line up with the rebuilt list, because the probe deletes later messages by `seq` and cannot restore the rows of that time. The 73 wrong rows count drift up to the end of the night. They are an upper bound for the wakes. Wake-time drift is confirmed for s239 and s240 (2 rows each). It is strongly probable for s137, s138 and s152 of night 158, which ran after bg_1 merged. Fix: none in the code. A re-count needs the order record of finding 1.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b85289fd-418f-43a1-a641-15dad2620cfa/scratchpad/r272/`.

- `p1.py`: printed messages m105, m106 and m116 of night 159, read-only.
- `p2.py 158` and `p2.py 159`: copied each night database into the scratch directory. For each Liaison converse wake, from the latest to the earliest, it deleted later messages, rebuilt `recent_chat` with the new `_recent_chat` and compared it with the turn-1 prompt. It checked each named row against the `landing.lines` of the reply's own wake. The output is in `p2_n158.txt` and `p2_n159.txt`.
- `p3.py`: listed every recorded `lines` map of each page, to date the drift. Each page has one recorded map only.
- Inline `python -c` probes: s239's landing (bg_2_summary under "How it is described"), the items row of bg_2_summary, `off_page` and `_is_request_item` at night end, s209's prompt keys and the absence of "m89", the batches and their seq, and `_page_named_lines` on a bare number and on a range.
- `p5.py` and `p5b.py`: seeded each Liaison case of `tests/rota/cases/*.yaml` whose inbound is a principal converse (19 cases). It ran `resolve_inbound` with the new code and listed the turns that gain a `page` key. 2 cases gain one.
- `p4.py`: read the cassette table for `recent_chat` in recorded L1 prompts. It found no match by `prompt_hash`, so `p5.py` replaced it.
- A read-only count of `recent_chat` across all cassettes ran for over 9 minutes with no result. I stopped it. It wrote nothing.
- `pytest -n 0 tests/rota/test_frame272_recent_chat_pages.py tests/rota/test_chat_intake.py`: 12 passed.

## (d) Usage

The session does not show its exact token counts. The estimate is about 85k input tokens, 15k output tokens, and 100k in total.
