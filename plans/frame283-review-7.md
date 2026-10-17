# Frame 283, review 7 of b5b14311

Worktree C:/Users/roman/rota_r283 at b5b14311. Read-only. Base 268e565f.
Verdict: the pass stands. Two lows remain, and both touch only a database that 268e565f wrote.

## (a) Verdicts on the points

1. F1 to F3 are fixed on their shapes (observed: r6 probe at b5b14311, 4 passed). BASE now ends "No note is open, and the commit is not held." TT shows a fence of three and _shown_lines returns the line. TICK and T1 use _quote (observed: the two new tests pass).
2. The rename holds. The map names one writer, _put_note at api.py:16030, which stages "restored", and one reader, _open_notes at api.py:15995 (observed: map table drop_notes). _open_notes keeps a landed row only when its status is "open", and it drops a staged row of any other status (observed: api.py:15997 and 16005). A grep finds no "closed" literal in api.py. The schema CHECK names "open" and "restored".
3. The new fence and the old single-backtick form both close by the ledger route (observed: probe r7, rows single_old_plain, single_old_tick, new_plain, new_tick, new_two, new_edge, all said True). The pass 6 form with spaces does not close. Finding F1 covers it.
4. s340 and s388 are still refused (observed: -k "s340 or s388", 3 passed). The three files are green: test_frame140_commit_beside_note.py, test_revert_door.py and test_identity.py, 72 passed.

## (b) Findings

F1. rota/roles/api.py:16206. Low. CONFIRMED (observed: probe r7, row old_double_tick, shown [] and said False).
_shown_lines no longer reads the pass 6 fence with spaces, "`` log(`b`) ``". A note that 268e565f stored with a backtick in its line now shows no line. The ledger route then cannot close that note. The guard at api.py:15511 appends a new fenced line only on a later code.write. Only a database written between abd3caf4 and b5b14311 holds that form. No night ran on it (reasoned: the frame's night has not run yet).
Fix: start the night on a fresh database or a snapshot older than abd3caf4. Else add the "`` x ``" form to the test at api.py:16206.

F2. rota/core/schema.sql:358. Low. PLAUSIBLE (reasoned: CREATE TABLE IF NOT EXISTS keeps an old CHECK).
A database built at 268e565f keeps CHECK (status IN ('open','closed')). _put_note's "restored" row then fails the CHECK on the write. Snapshots from nights before abd3caf4 have no drop_notes table, so they get the new CHECK.
Fix: the same as F1. Use no database that a pass of frame 283 built before b5b14311.

Outside the points: none. tail_note is always set where pass 7 appends the sentence, because the branch runs only under "if tail_note" (observed: api.py:15496).

## (c) Probes

- r6 probe: C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f283/r6/test_r6_probe.py, run with pytest -s at b5b14311. 4 passed.
- r7 probe: C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f283/r7/test_r7_probe.py. It builds a note in seven fence forms and runs _shown_lines and _says on a ledger text. It ran from a temporary untracked copy in the worktree's tests/rota. The copy was deleted, and git status was clean after.
- Tests: the three files, 72 passed. The s340 and s388 tests, 3 passed.

## (d) Usage

About 30k input tokens, 6k output tokens, 36k total (estimate; read the harness line).
