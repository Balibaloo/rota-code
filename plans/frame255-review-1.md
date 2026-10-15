# Frame 255, review 1: pass 1 at 4fe07692

Read-only diff review on the worktree `C:/Users/roman/rota_r255` at 4fe07692 (meta workflow, this build session's agent). Verdict: accept with one high finding. The predicate and the two doors work as the scope read says. The batch lift in `rulings_rule` is now wider than the new door needs, and a moved test locks it in.

## (a) Verdicts on the points

1. CONFIRMED. `built_line_faulted` admits 14 of 16 files corrections and refuses 9 of 9 right refusals. The 2 misses are rows 2 and 3 of night 136, as the scope read says.
2. CONFIRMED with a low finding. The two orders can differ only when a page row changes between the read and the land. Then `land` drops the contest with no error. The admitted row relays to the Architect with refs `["bg_2"]` and wakes `annotate`, and `batches.annotate` lands.
3. CONFIRMED. s212 now reads "line 8: the words do not fault bg_2's files. Approve line 8." The second call that the text steers is admitted and approves bg_2, which is the right call for m105.
4. The new s313 expectation is the right reading. M198 says "line 2 names the wrong tests", and line 2 is bg_2. The frame 142 reading cancelled the change for a files correction. The s263 and M85 texts are correct. See finding 1 for the second half of the s313 test.
5. CONFIRMED stale. The lift comment at `rota/roles/api.py` 8860 to 8862 still says the batch door sends the contest to the item. Two comments in `land` still say a batch ref leaves the ruling.
6. CONFIRMED. At 4e9d53aa, 3 of the 4 new tests fail for the reason each names, and the page-order test passes. With the new `api.py` and the old `principal.py`, only the land test fails, on `assert None == 'contest'`. At 4fe07692 the four touched test files give 142 passed and 4 xfailed.
7. Count on night 150: (1) files corrections after a head commit that land a batch `contest`, relay, and wake `annotate`, against 0 of 13 on nights 139 to 149. (2) Each "do not fault" refusal read as right or as a miss, and each item contest admitted beside words that fault only a built batch line.

## (b) Findings

1. `rota/roles/api.py` 8860 to 8872, the batch lift in `rulings_rule`. Severity high. CONFIRMED. The lift adds the item's line to `faulted` when the words fault a built batch line. Frame 142 needed that, because the door sent the contest to the item. Now the door admits the batch contest itself. So the lift only admits a second call, a contest of the item, which cancels the change. 16 of 16 files corrections asked to keep the change. A probe removed the lift in a scratch copy. The s313 item-contest call was then refused with "The words fault line 2. Line 1 is the request, and they do not fault it. Rule line 2, and approve the rest." That refusal is the right steer. The moved test `test_a_files_correction_of_a_built_batch_line_is_admitted` asserts that the item contest is admitted, so it locks the wide lift in. Fix: keep the lift for a merged or abandoned batch only, and make the test's second call expect that refusal.

2. `rota/roles/principal.py` 1803 to 1824 with `_page_order` at 1705. Severity low. CONFIRMED by a synthetic probe. `apply_rulings` builds the `Ask` with no order, so `land` renders the page again. The render reads `off_page`, `aside_items`, the criteria and the `stalled` config. The ask status does not change the order. The landing mode holds only `rulings.rule` and `rulings.line`, so the window is an earlier open ruling that lands first in the same `apply_rulings` loop. A probe deleted one criterion between the read and the land. bg_2 moved from line 8 to line 7, the contest left the verdict with no error, and the verdict landed with the criteria only. With no other contest, `land` returns None after it closes the ask, and the words are lost as before frame 255. Fix: stage the admitted batch refs on the `rulings` row, and let `land` keep a batch contest that the row names.

3. `rota/roles/principal.py` 1782 to 1786 and 1869. Severity low. CONFIRMED by a read. The comments say "The batch's ref is never a row the principal rules, so it leaves the ruling" and "`per_item` is the ruling less any batch ref". Frame 190 made both false before the build, and frame 255 makes them false after it. The lift comment at api.py 8860 is point 5. Fix: rewrite the three comments to name the two cases that keep a batch contest.

4. `tests/rota/test_park_page.py` 644 to 651. Severity low. CONFIRMED by a read. The docstring says `land` keeps the contest for the Architect. The test calls no `land`. The claim is true by `test_land_keeps_bg_2_and_the_relay_reaches_the_architect`. Fix: point the docstring at that test.

Outside the points:

5. `rota/roles/api.py`, `_line_refusal`. Severity low. CONFIRMED by a probe, and older than this pass. On m105, the map that "Approve line 8" steers to approves lines 6 and 7, and the words fault both. The door admits it. The same probe admitted a contest of line 1 with m105, whose words say "keep going with the change, not drop it". The line-1 result can come from the scene: the test's item has `decided` provenance and may not read as a request item. Fix: none in this frame. Count both shapes on night 150 before a frame.

6. `rota/roles/api.py`, `built_line_faulted`. Severity low. PLAUSIBLE. The predicate reads line numbers only. Night 136's "That line" and "Line two" miss, and a correction that names files with no line number also misses. The scope read says no such shape came back after night 136. Fix: none now. Night 150 counts it under point 7.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4492a9c1-4457-41ce-a46b-42b300ec21c1/scratchpad/f255/r1/`.

- `p1_pred.py`: replays the 25 sessions of nights 136 to 149 through the worktree's `built_line_faulted`. The order comes from `render_page` on each end-of-night database, read with `mode=ro`. Result: 10 files admitted, 6 refused, 9 other refused. Rows 13, 14, 15 and 22 have no line at the night's end, because their items went aside later. Their refusal text names lines 5, 5, 8 and 5, and each is in `faulted`, so the count at the time is 14 of 16 and 9 of 9.
- `p1b.py`: shows that the four pages of rows 8, 13, 15 and 22 render an empty order at the night's end, because `off_page` drops every ref.
- `test_p2_annotate.py`: m92 through `run_session` and `apply_rulings`, the relay with refs `["bg_2"]`, the Architect wake keyed `annotate`, and a scripted `batches.annotate` that commits.
- `test_p2_drift.py`: stages s199's ruling, deletes `cr_6` before `land`, and shows bg_2 leaves the verdict.
- `test_p3.py`: s212's first call and three second calls on m105.
- `old/`: `git archive 4e9d53aa` of `rota` and `tests`, with the new test file. Run 1 at the old code: 3 failed and 1 passed. Run 2 with the new `api.py`: 1 failed, the land test. Run 3 with both new files and the lift patched out by `nolift.py`: the s313 test fails on the item-contest call.
- At 4fe07692: `pytest` of the four touched test files gives 142 passed and 4 xfailed. The gate did not run, because no point needs it.

## (d) Usage

About 95k input tokens and 12k output tokens, about 107k in total. This is the agent's estimate, and the harness line is the count.
