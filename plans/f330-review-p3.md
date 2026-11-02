# Frame 330, review p3: commit d959c33f (b3c616be)

## Result

Verdict: hold. The loop_cap page works on the dry1w8 rows. The reset has one high defect. The four test files pass, 84 passed and 1 skipped.

Highs:

1. CONFIRMED. `rota/core/db.py` `_ruled_park` and the delete at about line 1131 read a stale ruling. The query takes the newest closed park ask of the batch, from any earlier park. On the dry1w8 copy no ask of the current park is open or answered. A criterion move with no actor still deleted all 37 runs of bg_1. `next_attempt` went from 11 to 1, and `gave_up` went false. After the next park, the old answered ask is still the newest closed one. So any criteria or tests move during a park restarts the counter without his answer. Law 6 then has no bound. Fix: restart only when the ask was answered after the newest run of the batch, and close the ruling once it is spent, for example a journal row or a stamp on the ask. Price: about 20 lines and one case of a second park.

Lows:

1. PLAUSIBLE. `rota/core/predicates.py` line 1896. The `park_ask` detail names `tst_waited` and "attempt 10 of 10". It does not name the last failure line. The page in `rota/roles/principal.py` near line 2418 reads `park_reds` and probably shows the line. No probe rendered that page. Fix: render the page on the copy and check the line. Price: one probe.
2. PLAUSIBLE. The reset does not check who moved the row. `_lift_quarantines` gets no actor, so another seat's criterion move or a Tester re-encode fires it the same as his move. High 1 covers the effect. Fix: the same guard as high 1. Price: none extra.

## Point 1: the page for bg_1

Yes for the cap and the test, partly for the failure line. On a copy, bg_1 is deferred at attempt 10. `gave_up`, `parked` and `park_owns` all return True. `park_ask` gives one page: "bg_1 is parked. The team gave up on: attempt 10 of 10 with tst_waited red. It is a page." The detail has no failure line (low 1). All readers call `gave_up`, so `close_stale_park_asks` and the status line follow the same predicate. I did not run those two on the copy.

## Point 2: what the delete of test_runs touches

`next_attempt` and `failing_attempt` restart at 1, which is the intent. `park_reds`, `_red_at_head` and `challenged_reds` see no red, so `gave_up` turns false and the park ends. The harness then runs the batch again at the head. The merge path needs green runs at the head, so a batch with no runs cannot merge until it runs again. I found no reader that fails on an empty set. The Developer's wake, review and `_moves_red` were not traced line by line, so that part is PLAUSIBLE. `test_run_journal` has all seven columns: id, batch_id, test_id, commit_sha, result, attempt, output. `lifecycle.record_run` writes the journal row with the run row, at insert time. So the history exists before any delete. The delete needs no journal write. The journal held 363 rows for bg_1 after the probe. Note: `db.py` line 1087 already deletes the runs of a test on a body move.

## Point 3: who can restart the counter

Any write that moves a criteria or tests row which reaches the red of a deferred batch. The move needs no actor and no link to the current park. The only gate is an answered park ask with a revise or contest, from any earlier park. Another seat's criterion move and a Tester re-encode both qualify. See high 1.

## Point 4: a loop_cap park with every test green

Unchanged. The new clause of `gave_up` needs `_red_at_head`. With no red run at the head it is false, and the old clauses decide. `park_ask` adds the cap words only when `park_reds` lists a red. Checked by reading, not by a probe.

## Point 5: the four test files

84 passed, 1 skipped, in 45 seconds, with -n0, ROTA_MODEL=qwen3:8b and the cassettes357 database. No case moved.

## Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/62bcfbfb-da09-4019-9041-3a50cdca6a58/scratchpad/rv/.

- p1.py on p3a.db, a copy of dry1w8/dry1.db: `gave_up`, `parked`, `park_owns`, `park_ask`, the park asks and `_ruled_park` for bg_1.
- p3.py on p3b.db, a second copy: a criterion move of tk_1_criteria_waited through `_moves_red` and `_lift_quarantines`. Runs went from 37 to 0, and `next_attempt` returned 1.
- pytest on the four files, from the worktree with PYTHONPATH set to the worktree.

## Usage

Input tokens: about 45k. Output tokens: about 6k. Total: about 51k.
