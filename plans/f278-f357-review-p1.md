# Review p1, frames 278 and 357: f24b5e48 and a8ea948e

Reviewer: Opus, read only, worktree `C:/Users/roman/rota_f354r` at a8ea948e. Date: 2026-11-01.

## Result

- f24b5e48 (frame 357): accepted. The drop lands as `dropped` on the dry1 rows, `awaiting_confirm` goes quiet, and `brief_ratify` refuses s2. The rebuild keeps every row and is safe with open WAL readers. The lows below can wait.
- a8ea948e (frame 278): not accepted. The count is right on dry1 (6 on `tst_waited`), and the detail and the park page carry it. But the new bound does not stop the loop. The Developer's `tests_failing` wake still fires below `loop_cap`, so `quiet_park` never fires. A park on the challenge bound alone also does not hold.

Highs:

1. H1, a8ea948e. `tests_failing` (`rota/core/predicates.py:955-986`) ignores `stopped_bouncing`. On the dry1 copy the frontier still holds `developer tick:tests_failing bg_1`. CONFIRMED (probe p4). Fix: skip a running batch with a row in `challenged_reds` in `tests_failing`. Price: 0.5 cycle.
2. H2, a8ea948e. A deferred batch parked on the challenge bound alone is not parked. `parked` (`rota/core/scheduler.py:2655`), `park_message_rests` (2189), `close_stale_park_asks` (2635) and `_render_state` (`rota/roles/principal.py:402`) read `given_up` only, and `challenged_reds` is gated on `running`. On a copy with bg_1 set `deferred`, `parked` is False and `next_batch` returns bg_1. CONFIRMED (probe p5). Fix: one helper that reads `given_up` or the ungated count, at those four sites. Price: 1 cycle, with the reset of point 7.
3. H3, outside both commits. A drop on the two draft items of m90 lands as `items.approval = 'contested'` (`rota/roles/principal.py:3659`). The `contested` predicate wakes the Vision Keeper, whose brief offers "defend it once" when the principal gives no replacement. No item end status exists. PLAUSIBLE: the model's choice is not probed. Fix: a landed `drop` on an item writes an `item_parks` row of kind `drop`, as `_land_shift` does. Price: 1 cycle.

Lows:

4. L1, a8ea948e. The count has no reset at a green run or a new head. CONFIRMED by the query text. Fix: count the challenges after the last green run of the test. Price: 1 cycle, after a shared order exists.
5. L2, a8ea948e. Below `loop_cap` the detail starts with "attempt 8 of 10", and the docstring at `rota/core/scheduler.py:2072-2074` calls that text false below the cap. CONFIRMED (probe p4). The fix line is in point 9. Price: 0.2 cycle.
6. L3, f24b5e48. The refusal says "contested" for a drop. No reader turns the word into a second ask. PLAUSIBLE harmless. Price of a change: 0.5 cycle and cassette drift.
7. L4, f24b5e48. A confirm whose only statements are dropped loses them in the send door and goes out with no statement row. PLAUSIBLE, no wake reaches the path now. Fix: refuse a confirm with no statement ref left after `off_page`. Price: 0.3 cycle.

## 1. The drop on the dry1 rows

The probe widened a copy of the dry1 database and set s2 and s3 back to `proposed`, their state before m77. It then ran `_drop_statements(conn, ["r_m75"])`.

- s2 and s3 read `dropped`. s1 stays `ratified` (probe p1).
- `awaiting_confirm` returned one wake on s2 and s3 before the drop, and an empty list after it (probe p1).
- `brief_ratify` on s2 raised "the principal contested s2 in r_m75, so s2 is not ratified and not delivered" (probe p1). The approve rows of m78 (`r_m78`, rowid 24) come after r_m75 (rowid 23), and `statement_drop` still returns r_m75.
- The landed rows of r_m75 carry `source = 'landed'`, `verdict = 'contest'`, `act = 'drop'` (rows `rr_d304d1a4539d`, `rr_e0d5ed116c77`). The query of `_drop_statements` matches them. The keypress path also writes landed rows (`rota/roles/principal.py:3751-3761`), so a key drop reaches the same write.

Verdict: CONFIRMED on the rows.

## 2. init_db on an older database

- Every row and every column of `statements` stays. The rows compare equal before and after, and `PRAGMA table_info` gives the same 8 columns (probe p1).
- `integrity_check` is ok. `foreign_key_check` is empty before and after. The only foreign key to `statements` is its own `supersedes`.
- No trigger is on `statements`. The views `ruled_refs_live` and `provenance` name it, and both read after the rename (probe p2).
- With a second connection inside an open read transaction and a third with a live read, `init_db` committed. The reader kept its snapshot and saw the new CHECK after its commit (probe p2). The database is in WAL mode.
- Residue: the check for the word `dropped` sits outside the write lock. Two processes can rebuild twice. The second rebuild copies the widened table, so no row is lost. A busy writer makes `BEGIN IMMEDIATE` raise before the `try`, and the pragmas stay changed on that connection only.

Verdict: CONFIRMED safe.

## 3. The seat words

The verdict brief of the Liaison (`rota/roles/prompts/liaison/verdict.md:8-10`) says "A contested statement is not ratified and not delivered" and "end the session with no call". So the word maps to a stop, not to a second ask. The `contested` predicate (`rota/core/predicates.py:298`) reads `items.approval`, not statements. The callers of `contested_statement` are the ratify door, the deliver door (`rota/core/sandbox.py:4735`) and `ratified_request` (`rota/roles/principal.py:1443`). None of them asks again.

A change to "dropped" touches `api.contested_refusal` (`rota/roles/api.py:1215-1220`) and needs the act of the ruling. The text reaches the model, so cassettes that hold the refusal drift. Price: 0.5 cycle plus a cassette check. Recommendation: keep the words (L3).

## 4. A drop on a ratified request

`_drop_statements` writes nothing on a `ratified` statement, as the pass 1 report says. Today one route stops a ratified request: the shift page. `_land_shift` writes an `item_parks` row of kind `drop` (`rota/roles/principal.py:3943-3952`), and `cancel` abandons the live batch of the item (`rota/core/predicates.py:1588-1591`).

m90 is a `present` page with the draft items `surface_is_click_pause` and `write_tests_again`. `drop` is in `RULED_ACTS` (`rota/roles/principal.py:1061`). A drop on an item lands as `contest`, and `land` writes `approval = 'contested'` (`rota/roles/principal.py:3659`). Nothing writes an end status for an item, and the `items` CHECK has no such value (`rota/core/schema.sql:57`). The Vision Keeper wakes on `contested` with two branches: amend, or defend once and report back. So the drop does not end the two items. The items end only if the Vision Keeper does not defend. See H3.

## 5. off_page and the page m77

On the dropped copy, `off_page(["s2","s3","reading:m75"], confirm=True)` returns `{s2, s3}` (probe p3). The send door then keeps `reading:m75` alone (`rota/core/sandbox.py:4496-4500`). The statement guard (4708-4721) loops over the refs that are left. No check refuses a confirm with no statement. So such a page stays open with the read-back line only, or with no row. PLAUSIBLE: no probe ran the door. `awaiting_confirm` no longer wakes the Liaison for s2 and s3 (point 1), so no wake reaches the path today. See L4.

## 6. The count and the chain on dry1

- `challenged_reds(bg_1)` finds `tst_waited` with 6 challenges (m95 to m100) and the versions 3, 5, 6, 7 and 8 of the Tester. `stopped_bouncing(bg_1)` is True. `failing_attempt` is 8, and `given_up` is empty (probe p4).
- `exhausted` returns an empty list. `_next_rung(bg_1)` is empty, because s149, s152 and s155 already climbed the ladder for `tests_missing` on this batch. The rung count has no reset per cause.
- `spent_park(bg_1)` returns `do:park` with the detail "bg_1: attempt 8 of 10; the Developer challenged tst_waited 6 times, and the Tester wrote versions 3, 5, 6, 7 and 8, and its ladder is spent". `preempt` returns an empty list, because `next_batch` is empty while bg_1 runs.
- `quiet_park` reads `spent_park` only when no predicate wakes a seat. `frontier_readonly` holds `developer tick:tests_failing bg_1`, two Architect `tick:unresolved` wakes, a Liaison `round_close` and two Critic wakes (probe p4). The `tests_failing` wake stays until `loop_cap`, so the park cannot fire. The chain stops here. See H1.
- `_park_page` on the copy renders "The team challenged the check tests/test_termui_tk_1_criteria_waited.py 6 times, and wrote versions 3, 5, 6, 7 and 8 of it." So the page carries the test, the count and the versions when it is sent.
- After a forced deferral, `parked` is False and `next_batch` returns bg_1 (probe p5). `close_stale_park_asks` then marks the new park ask answered. See H2.

## 7. No reset at a green run

The count query in `challenged_reds` (`rota/core/scheduler.py:2015-2019`) reads every closed challenge that names the test. It has no time, run or head filter. In the case of the brief, the two old challenges and the one new one give 3, which is `tick_attempt_cap`. The ladder climbs on the first new challenge. CONFIRMED by the query text. No fixture ran.

The records give no shared order. `messages.seq` stops at 103 on dry1. `test_run_journal.seq` runs from 141 to 289 for `tst_waited` (probe p6). They are two counters. `sessions.seq` (max 210) can share the counter of messages, but a message carries no session id. A reset needs a session id on the message, a message seq on the run, or a count after the last change of the head commit. Price: 1 cycle with a schema column, and a migration as in point 2. The same reset ends the park of H2 at a new head, so H2 and the reset belong to one pass.

## 8. Which count is right

Design 200 change 4 (ruled: Roman, 2026-10-11 06:30) says a challenge that carries the decision row of the Architect "does not count against the cap". The cap is the refusal of a further challenge at the door (`rota/core/sandbox.py:2588-2593`). The ruling keeps the route to the Tester open. It says nothing about the ladder.

The ladder count answers a different question: whether the loop ends. Law 6 says "It is never silence". On dry1, m95 to m99 carry `d_1`, and the door counts 1 for `tst_waited` (probe p4). If the ladder used the count of the door, it would read 1, and the loop would stay unbounded. So the frame 278 count is right for the ladder, and the door count is right for the refusal. PLAUSIBLE, because no ruling names the ladder.

On dry1 the door lets the Developer send more `d_1` challenges, and the ladder already reads the bound. The two counts do not conflict, because the ladder refuses nothing. Today the disagreement has no effect, because the chain stops at H1.

## 9. The detail below loop_cap

The docstring at `rota/core/scheduler.py:2072-2074` says that below the cap "attempt 6 of 10" and "past its cap" are both false. The new code writes "attempt 8 of 10" first when no key is quarantined (line 2094). The count is true as a number. The clause is misleading, because it reads as the cause, and the docstring of the same function calls it false. Fix line for `stop_detail`:

    return f"{why}; {looped}" if why else looped

`exhausted` keeps its own fallback text for the case with no detail.

## 10. Other readers of the new branch

- `next_batch` (`rota/core/scheduler.py:1827`) reads `parked`. A running batch is not in its rows, so nothing changes while bg_1 runs. A deferred batch loses the branch through the `running` gate, so `next_batch` lists it again. See H2.
- `spent_park` and `quiet_park` now fire on the count. `preempt` reaches `spent_park` only beside a challenger.
- `_render_state` (`rota/roles/principal.py:399-407`) reads `parked` on deferred batches only. A deferred batch on the count alone counts as pending work, not as held.
- `given_up` does not read the branch. The Stuck line of the status page reads `given_up` keys, so it shows nothing for the count.
- Tests: 15 files ran from the worktree. They hold the park, two_batches and challenged scenes, frame 330, frame 312, frame 278, frame 357, the park page, next_batch and predicates. Result: 333 passed, 2 skipped, 6 xfailed (probe p7). No test moved.

## Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/62bcfbfb-da09-4019-9041-3a50cdca6a58/scratchpad/rv/`. Each ran from the worktree root with `PYTHONPATH` set to it. Each copy came from `dry1w6/dry1.db` before the probe.

- p1 `p1.py` on `rv1.db`: `init_db`, the row and column compare, `integrity_check`, `foreign_key_check`, the reset of s2 and s3 to `proposed`, `_drop_statements`, `awaiting_confirm`, `contested_statement`, `api.brief_ratify`, `off_page`.
- p2 `p2.py` on `rv2.db`: `init_db` with two open readers, one inside a read transaction; the triggers, the views and the indexes.
- p3 inline on `rv1.db`: `off_page` on the refs of m77.
- p4 `p3.py` and inline on `rv1.db`: `challenged_reds`, `stopped_bouncing`, `stop_detail`, the challenge rows, `exhausted`, `_challenges_on`, `_next_rung`, `spent_park`, `quiet_park`, `frontier_readonly`, `_park_page`.
- p5 inline on `rv3.db`: bg_1 set `deferred`, then `parked`, `stopped_bouncing`, `park_message_rests`, `next_batch`.
- p6 inline on `rv3.db`, read only: the columns of the run and message tables and the seq ranges.
- p7 pytest from the worktree, `ROTA_MODEL=qwen3:8b`, `ROTA_DEV_DB` on `cassettes357.db`, the 15 files of point 10.

No probe called the model, ran the gate or ran rota. No probe opened `D:/repos/rota/.rota/dry1.db`.

## Usage

The harness gives no exact split. Estimate: about 100k input tokens, about 15k output tokens, about 115k in total. That is over the cap of 40k, mostly from the chain of point 6.
