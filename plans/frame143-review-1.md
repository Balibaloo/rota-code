# Frame 143, review 1 of 5561fc13: the surface push and its sentence

Rota workflow. Worktree C:/Users/roman/rota_r283old at 5561fc13. Read-only. Date 2026-10-17.

Verdict: stands, with two findings. The push and the note work as built. The note's form is not the form the interview measured.

## (a) Verdicts on the points

1. Partly holds. The gate is `role == "tester" and (wake.kind == "tick:tests_missing" or inbound)` at rota/core/runner.py:681, then a resolved `surface_refs` row in `_criterion_surface_pushes` (runner.py:2731). It fires on any Tester message wake too, not only on encode wakes (observed: the test's challenge wake carries the block, test_scene_challenged.py:161-170). A fix wake with no inbound gets no block (reasoned: neither branch of line 681 is true).
2. The lines are the same. The block for click `confirm` holds the signature with `default: bool | None = False` and `-> bool`, `rv = True`, `rv = False`, `rv = default`, `return rv` (observed: probe p143b). The note renders before the source, on the header line beside `path` and `start` (observed: probe p143b). The interview had the sentence in the system brief, with other words.
3. A 200-line function with 60 returns gives a 142-line block of 20,346 characters (observed: probe p143). Only `PUSH_CHARS` = 20,000 in `_render` caps the block. The note survives the cut, because `_render` puts scalars first (observed: probe p143).
4. Holds. No Tester brief holds "asserts what" or "pushed source" (observed: grep of rota/roles/prompts/tester). A criterion with no `surface_refs` gives `{}`, so no block and no note (observed: test_scene_challenged.py:171-177 asserts the whole system and body text, green).
5. Every Tester case recorded at pass 1 holds the old brief sentence in its system text, so the re-record meets them all stale first (reasoned: base.md changed between 0884ddf4 and 5561fc13).

## (b) Findings

1. rota/core/runner.py:2822-2825. Severity high. PLAUSIBLE: the measured arm was the push plus the brief sentence "A body asserts what the surface returns, read from `code.source`, and never a value the criterion does not give." in the system text. Pass 1e ships other words, in the pushed block, before the source, under the key `surface` and not `code.source`. The 3 of 3 and 0 of 6 counts in plans/frame143-interview.md section 3 do not cover this form. Fix: replay s199 t3 and s203 t1 with the 5561fc13 prompt before the night gates on the form.
2. rota/core/runner.py:681. Severity low. CONFIRMED: the predicate admits every Tester message wake with a criterion or test ref, for example a challenge or an answer wake, and not only encode wakes. The test covers only the challenge wake, and no test covers the `tick:tests_missing` path. Fix: add one scene test for a `tests_missing` wake, and state in the frame that message wakes are in scope.

Outside the points: none found in the cap.

## (c) Probes

- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/p143.py: runs `_surface_lines` and `_render` on a synthetic 200-line function with a stub sandbox.
- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/p143b.py: runs `_surface_lines` and `_render` on the installed click `termui.confirm`.
- `pytest tests/rota/test_scene_challenged.py -q` with ROTA_MODEL=qwen3:8b: 18 passed, 1 skipped, 2 xfailed.

## (d) Usage

About 40k input tokens and 5k output tokens, 45k total (estimate; read the harness line). The cap of 15k was passed.
