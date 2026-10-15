# Frame 255, review 2: pass 1b at d3340828

Read-only diff review on the worktree `C:/Users/roman/rota_r255b` at d3340828 (meta workflow, this build session's agent). Verdict: accept with one low finding. The lift now fires for a merged or abandoned batch only. The three `land` comments, the lift comment and the `_page_order` comment say what the code does. The moved test is red at 15cbf388 for the right reason and green at d3340828.

## (a) Verdicts on the points

1. CONFIRMED. s313's item contest is refused with the exact steer of review 1. m92's batch contest is admitted with bg_2 `contest`. On the m91 page with bg_2 `merged` or `abandoned`, an item contest beside words that fault only line 8 is admitted, so the lift fires. With bg_2 `running`, the same call is refused: "The words fault line 8. Line 1 is the request, and they do not fault it. Rule line 8, and approve the rest."
2. CONFIRMED with one low finding outside the three named comments. The lift comment, the touch-note comment, the frame 190 comment and the `per_item` comment name the two cases that keep a batch contest. No sentence in `api.py` or `principal.py` says that a batch contest after the commit is dropped or goes to the item, except in the past tense of frame 142. The `_unnamed_contest` docstring is stale (finding 1).
3. CONFIRMED. The `_page_order` comment names the window: an earlier open ruling lands first in the same `apply_rulings` loop and moves a row. The diff adds five comment lines to `_page_order` and changes no code there.
4. CONFIRMED. With the d3340828 test file over a `git archive` of 15cbf388, the test fails on the second call with "DID NOT RAISE <class 'ValueError'>". The first call passes. At d3340828 the four touched test files give 142 passed and 4 xfailed.

## (b) Findings

1. `rota/roles/api.py` 8524 to 8528, the `_unnamed_contest` docstring. Severity low. CONFIRMED by a read. The docstring says "`read` holds the faulted and matched lines after the batch lift, so a batch line's item counts as named." The lift now adds the item's line for a merged or abandoned batch only. For an open built batch, the item line is no longer named by the fault of the batch line. On a page where the item is not line 1, `_unnamed_contest` now refuses an item contest that it admitted at 15cbf388. That behaviour agrees with finding 1 of review 1, but the docstring states the old rule. Fix: write "so the item of a merged or abandoned batch's line counts as named."

No high finding. The code change is the one review 1 asked for. The query drops `head_commit` because only `status` decides the lift now, and the door above refuses every ruling of a merged or abandoned batch line before the lift runs.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4492a9c1-4457-41ce-a46b-42b300ec21c1/scratchpad/f255/r2/`.

- `test_r2_p1.py`: imports the fixtures of the worktree's `test_frame255_files_correction.py` and `test_park_page.py`. It replays s313's item contest on `n133` with M198, m92's map on `m91`, and an item contest on `m91` with bg_2 set to `merged`, `abandoned` and `running` and words that fault only line 8. Run from the worktree root with `R2_TESTS` set: 9 passed, with the printed results in point 1.
- `old/`: `git archive 15cbf388 rota tests`, with `tests/rota/test_park_page.py` from d3340828 written over it by `git show`. `pytest -k built_batch_line_is_admitted` with `PYTHONPATH` on `old/`: 1 failed, "DID NOT RAISE". A print of `rota.__file__` shows that the run imports the archived code.
- At d3340828 in the worktree: `pytest` of `test_park_page.py`, `test_frame255_files_correction.py`, `test_frame193_pass1.py` and `test_request_page.py` gives 142 passed and 4 xfailed. The worktree has no changes after the probes. The gate did not run, because no point needs it.

## (d) Usage

About 45k input tokens and 6k output tokens, about 51k in total. This is the agent's estimate, and the harness line is the count.
