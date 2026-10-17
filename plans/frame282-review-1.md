# Frame 282, review 1 of 43be926d: the line reader reads a range on every number

Reviewer: read-only agent, Opus, on C:/Users/roman/rota_r283old at 43be926d, 2026-10-17. Rota workflow.

Verdict: stands. Two lows, no high.

Note on the brief: f99988f5~1 is 43be926d itself (observed: `git log -1 f99988f5~1`). So the diff the brief names is empty. This review read `git diff 43be926d~1 43be926d`: 2 files, 42 insertions, 2 deletions, api.py touches only `_LINE_NUM`, `_LINE_REF` and the `_ref_lines` tokenizer.

## (a) Verdicts on the points

1. Stands. Every shape reads as the words say. The false shapes do not read as a range (observed: r1probe.py):
   - "Notes 6, 7 and 10 to 14" reads 6, 7, 10 to 14.
   - "lines 2, 3 and 5 to 7" reads 2, 3, 5, 6, 7.
   - "lines 1 to 3, 5 and 8" reads 1, 2, 3, 5, 8.
   - "Lines 1 to 3 and 5 to 7" reads 1, 2, 3, 5, 6, 7.
   - "lines 5-7 and 9" reads 5, 6, 7, 9.
   - "note 6 and 7 to the Architect" reads 6 and 7. The match stops at "7", because "to the" has no number.
   - "line 2 to 3.1" reads 2 and 3. The ".1" falls outside the match. The old reader read the same.
   - "lines 5 to 7, 9 – 10" (en dash) reads 5, 6, 7, 9, 10.
2. Stands. Five reads of `_LINE_REF` and `_ref_lines`. Two change outcomes, and one of them is outside the verdict doors (finding 1):
   - `_line_cues` (api.py:9008, 9011) feeds `_line_reading` and the approve door at api.py:9590. A wider reading faults or matches more lines. That is the intended change.
   - `_line_reading` also feeds `built_line_faulted` at principal.py:1871, the principal-side filter that keeps a contest or a revise on a built batch. A wider reading keeps more of those rows (finding 1).
   - `_line_refusal` api.py:9096 asks only "is line 1 in a reference". A list item's range now can contain 1 only in a shape like "lines 3 and 0 to 2". No real change (reasoned).
   - api.py:9104 and api.py:9233 call `_LINE_REF.search` as a yes or no. The first number is still required, so the answer does not change (reasoned: the widened part is optional and follows the first number).
   - `_unnamed_contest` api.py:9265 clips to the page size. More named lines give fewer unnamed contests, so the door refuses less. That is the intended change.
   - No caller reads a seat's own text. Every input is the principal's words (observed: callers listed by the map tool, then read). `_WORDS_FAULT` api.py:5265 is a separate pattern and already admits a range at any number.
3. Stands. count.py re-run gives "replies with a digit: 401; replies whose lines changed: 5", the same as count.out (observed: diff of the two outputs, empty). The script reads every principal reply with a digit (`body_text glob '*[0-9]*'`), not only replies with "line" or "note". All five changes match the words: night 133 m304, night 142 m291, night 148 m12, night 154 m175 and m176. One caveat: count.py puts D:/repos/rota first on sys.path, so it imports the main checkout's api.py and not the worktree's. A re-run with the worktree's api.py loaded first gives the same 401 and 5 (observed: `python -c` that imports rota.roles.api from the worktree, then executes count.py).
4. Stands. `L1-VK-amend-a-contested-item` is red at f99988f5~1, which is 43be926d: 0/5, needs 4 (observed: replay with ROTA_DEV_DB on a sqlite backup of the register, 23 cassettes replayed, no STALE). The first refusal, run 1: "expected writes to items (>=1), got 0; forbidden call to decisions.author". The case's failure is a forbidden decisions.author call and no items write, not a line reading. This review did not run the case at 43be926d~1. The report's stash run is the only evidence that the case is red without the change.
5. The next night first meets night 154's shape on the principal-side filter (principal.py:1871). A contest on a built batch at lines 11 to 14 now reaches the Architect, where before the filter dropped it.

## (b) Findings

1. principal.py:1871 (with api.py:9008-9011), low, PLAUSIBLE. The wider reading changes an outcome outside the verdict doors. `built_line_faulted` reads `_line_reading(answer.text)[0]`, so a contest or a revise on a built batch at a list item's range (night 154's lines 11 to 14) now survives the drop and reaches the Architect. This matches the principal's words, so it is the right behaviour. No test covers it: the four new tests call `_ref_lines` alone (observed: test_frame234_verdict_lines.py, the appended tests). Fix: add one test that calls `built_line_faulted` on m175's words with a batch at order index 11, and note the counted predicate ratio (14 of 16, 9 of 9) as unchanged or re-counted.
2. api.py:8917, low, PLAUSIBLE. A range on a list item is unbounded. "lines 2 and 3 to 2026" reads 2024 lines (observed: r1probe.py). The old reader had the same exposure on the first number only. `_unnamed_contest` clips to the page size, but `_line_cues` and `_line_reading` do not, so a number in the principal's prose after "and N to" can fault a line that his words do not name. No reply in nights 130 to 154 has this shape (observed: count.out, 5 changes, all true). Fix: drop a range whose end is above the page size, or cap the end at the page size in `_line_reading`.

Outside the points:
- The brief's diff range f99988f5~1..43be926d is empty. The frame's commit is 43be926d alone (observed: `git log -1 f99988f5~1`). Fix: name the range as 43be926d~1..43be926d in the next brief.

## (c) Probes

- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f282/r1probe.py: runs `_LINE_REF` and `_ref_lines` from the worktree on ten shapes.
- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f282/r1count.out: count.py re-run, identical to count.out after the header. A second run loaded the worktree's api.py first and gave the same totals.
- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f282/r1cass.db: a sqlite backup of tests/rota/cassettes.db. The pytest replay of the L1 case at 43be926d used it through ROTA_DEV_DB. Delete it after the review, because it is large.
- No tree was edited. The worktree shows one untracked file, tests/rota/test_r4_new.py, which this review did not create.

## (d) Usage

About 45k context tokens in all, input and output together, by the remaining-token count (estimate). The harness line is the true count.
