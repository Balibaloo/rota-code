# Frame 282, review 2 of 42a4449e

Reviewer: read-only agent on C:/Users/roman/rota_r283old at 42a4449e, 2026-10-17. Verdict: the pass stands.

## (a) Verdicts

1. Partly holds. Two callers still read with no cap: `principal.land` (principal.py:1871) and `_line_refusal` (api.py:9108). Neither outcome changes for a line on the page. Only a reversed range differs (finding 3).
2. Holds. With no page size, "Lines 2 and 3 to 2026 are wrong." reads 2 to 2026, 2025 lines, the same as the reader at 43be926d (observed: probe r2probe.py).
3. Holds. m175 and m176 fault no line, and `built_line_faulted` returns False for lines 6 and 12 of a 14-line page (observed: probe r2probe.py). The cause is a new frame's wall.
4. Holds. `test_frame234_verdict_lines.py` and `test_frame255_files_correction.py`: 78 passed in 5.54s (observed: pytest, 2026-10-17).

## (b) Findings

1. rota/roles/principal.py:1871, low, CONFIRMED that the read has no cap (observed: grep of callers). `land` reads `_line_reading(answer.text)` before it knows the order. It then passes that set to `built_line_faulted`, which skips its own capped read. For a line on the page, the capped set and the uncapped set agree. The exception is a reversed range (finding 3). The cost of a large end such as "to 99999999" is PLAUSIBLE (reasoned: `range` builds one set entry for each number). Fix: call `built_line_faulted` with `faulted=None`, or read with `len(order)` after the order is known.
2. rota/roles/api.py:9108, low, CONFIRMED (observed: source read). `_line_refusal` tests `1 in _ref_lines(r)` with no size. Line 1 is on every page, so the cap cannot change the test. The cost risk of finding 1 applies here too. Fix: pass `size`, which `_line_refusal` holds as a parameter.
3. rota/roles/api.py:8950-8952, low, CONFIRMED (observed: probe). With a page size, "lines 5 to 3" reads [5] and drops line 3. With no size, the reader reads [3, 5]. The reader at 43be926d also read [3, 5]. A capped caller therefore loses the end of a reversed range. Fix: add the end digit when it is on the page and the range is empty.
4. Outside this frame, the wall of point 3, CONFIRMED (observed: probe). `_line_cues` looks for a cue only in the window after a reference. The m176 cue "remove" comes before "lines 6, 7 and 10 to 14", so the window is empty. `_LINE_FAULT` matches "remove" when it stands alone. The m175 window is " have nothing to do with this change". `_LINE_FAULT` matches neither "nothing to do with" nor "unrelated". Fix: in a new frame, read a cue verb that comes before the reference in the same clause, and add "nothing to do with" and "unrelated" as cues, with the count of each on the nights' records.

## (c) Probes

- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f282/r2probe.py runs `_line_reading`, `_ref_lines`, `_line_cues` and `built_line_faulted` with and without a page size, on the range sentence and on m175 and m176.
- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f282/api_old.py is api.py at 43be926d, read for the old `_ref_lines`.
- Two `python -c` checks: `_LINE_REF` matches on m175 and m176, and `_LINE_FAULT` on the m175 window and on "remove".
- pytest on the two touched test files.

## (d) Usage

Estimate: about 30k input tokens, 6k output tokens, 36k in all. Read the harness line for the true count.
