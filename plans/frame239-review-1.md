# Frame 239, passes 1 and 1b: the diff review of the batch join

Review of 865b5132 over 252feb0e, on the worktree `C:/Users/roman/rota_rv239`.
Rota workflow, the scheduler. Read-only. All probes ran on 2026-10-14.

Verdict: revise. The two fixed queries are correct, and the night's case now wakes the Tester and holds the merge. Two other readers of the same unfiltered join decide what the woken seats do. Both work against the fix. Findings 1 and 2 are the next pass's brief.

Counts: 2 high, 3 low.

## (a) The verdict on each point

1. Holds. At HEAD, bg_3 wakes the Tester for 3 criteria and `mergeable` refuses. At the parent, both pass bg_3.
2. Holds. `tests.batch_id` is NOT NULL, and each criterion of night 147 has 1 distinct batch. `harness.inherit` moves project rows between batches (finding 4).
3. Fails. `review` and `criteria_load` keep the unfiltered join and disagree with the fix (findings 1 and 2).
4. Holds. A batch with its own tests wakes nobody and merges past the check. A batch with no criteria wakes nobody.
5. Holds. Two of the three new tests are red on the parent. The `review` predicate and `criteria_load` have no test.
6. Holds. 0 CR bytes in the three files. One comment uses an idiom (finding 5).

## Point 1. The night's case

The final night database is not the walk-2 state. bg_3 holds 0 rows in `tests` there. Its 37 test runs name `inh_` ids that now sit in bg_4, because `harness.inherit` moved them (finding 4). The probe moves the 37 rows back to bg_3, sets bg_3 to `running`, and keeps bg_3's verdict `pass` at `16588ec9`.

- HEAD `tests_missing`: one wake, refs `('bg_3',)`, detail `without a test: cr_1_..., cr_2_..., cr_3_...`.
- HEAD `mergeable(bg_3)`: `criteria without a test: cr_1_..., cr_2_..., cr_3_...`.
- Parent `tests_missing` SQL: no row.
- Parent `mergeable` SQL: `untested` is empty, so the check passes to the verdict, and the verdict is `pass`.

On the final database as written, `mergeable(bg_3)` at HEAD returns None. `has_tests` is None there, so the criteria check never runs.

## Point 2. Who writes `tests.batch_id`

Two writers exist: `harness.inherit` (harness.py:265) and `tests_encode` (api.py:7976). The schema makes the column `NOT NULL REFERENCES batches(id)`. Night 147 holds 0 rows with a null or empty batch. Each criterion has 1 distinct batch: `cj_*` in bg_1, `cr_1..3` in bg_2, and `ver_opt_show_py` in bg_4. No test names a batch that is not a batch of its criterion's ticket.

`tests_encode` sets `batch_id = batch_id or ctx.batch_id or _batch_of_criterion(...)`. A tick wake carries the batch. The guard at api.py:7921 refuses an encode that would move another batch's row. So a Tester row keeps its batch across attempts. One gap remains: a byte-identical re-encode returns before that guard (finding 2).

`harness.inherit` writes `INSERT OR REPLACE` under an id that the path decides. So the next batch that inherits takes the row of each project test from the earlier batch (finding 4).

## Point 3. The other readers

The join of `tests` to a criterion with no batch filter is in four more places.

- `predicates.review`, predicates.py:1298-1302. This predicate decides a wake. It now disagrees with the fix (finding 1).
- `api.criteria_load`, api.py:5453, `tested_by`. This query decides what the woken Tester sees. It now disagrees with the wake detail (finding 2).
- `scheduler.park_criteria`, scheduler.py:1626. The query filters `t.batch_id = ?`, so it is correct.
- `sandbox._quoted_body_gone`, sandbox.py:1846. The query reads criterion text by test id, and decides no wake.

`_batch_of_criterion` (api.py:431) counts every batch of the ticket, the abandoned batch too. A ticket in bg_2 and bg_3 gives two rows, and the function returns None. A Tester woken by a message for bg_3 then meets the refusal "belongs to no batch", as s315 did. A tick wake does not meet it, because `ctx.batch_id` comes first. The fix is a join to `batches` with `b.status != 'abandoned'`. That fix is in the site of the implementer who edits `api.py` now.

## Point 4. The old rule and the greenfield batch

With one bg_3 test of each criterion, `tests_missing` gives no wake, and `mergeable` returns None. A running batch with a head commit and a ticket with no criteria gives no `tests_missing` wake. `mergeable` returns `no verdict` for it, which is the next check. The same batch with no head commit gives no wake either.

## Point 5. The tests

The three new tests ran on a copy of 252feb0e, with the test file of 865b5132. Two are red there: the test that the next batch owes nothing, and the test that the next batch never merges. The old-rule test is green on the parent, as it must be. All three are green at HEAD. No test covers the `review` predicate, `criteria_load`, the identical re-encode, or `mergeable` with `has_tests` None.

## Point 6. STE and CR bytes

`predicates.py`, `lifecycle.py` and `test_predicates.py` hold 0 CR bytes. The comments are short, in the active voice, and name the night and the frame.

## (b) Findings

1. **`review` wakes the Critic before the Tester on a re-dispatched batch.** predicates.py:1298-1302. Severity high. CONFIRMED. On the walk-2 state with no verdict, `review` gives `('bg_3',)` and `tests_missing` gives `('bg_3',)` in the same tick. `review` is band `gate` (20), and band `start` comes after it. So the Critic judges before the Tester's tests exist. A verdict is keyed to the commit, and a test does not move the commit. After the Tester encodes and the harness runs, `mergeable` finds the old `pass` and merges. The Critic never sees the batch's own tests. The comment at line 1295 says "review waits for it". The fix breaks that wait for this batch.
   Fix: add `AND t.batch_id = bt.batch_id` to the inner NOT EXISTS of `review`, with a test on `_two_batches_on_one_ticket`.

2. **The woken Tester sees bg_2's tests as its own, and a same-body re-encode lands nothing.** api.py:5453 and api.py:7822-7828. Severity high. CONFIRMED. `criteria_load` with `batch_id='bg_3'` returns `tested_by` `tst_confirm_eof_default`, `tst_confirm_eof_true_false` and `tst_confirm_eof_true_returns_default`. The wake says the same three criteria have no test. Walk eleven and night 46 show that the Tester acts on `tested_by`. A re-encode of `tst_confirm_eof_default` with the same path and body returns `unchanged: True`, and `ctx.writes` stays empty. This check comes before the other-batch guard at line 7921. A changed body meets the guard, "is a test of batch bg_2 ... Choose another id". So the wake can repeat with no row written.
   Fix: filter `tested_by` with `AND t.batch_id = bt.batch_id`, and limit the identical-body check to a prior row of the same batch. Both edits are in `api.py`, after the implementer's current edit.

3. **The comment and the commit message of 865b5132 name half the mechanism.** lifecycle.py:584-585. Severity low. CONFIRMED. The criteria check ran on bg_3 only because bg_3 held 37 project rows at walk 2. On the final database, bg_3 holds 0 rows, and `mergeable` passes it at HEAD too. A reader who checks the comment on the night database finds the opposite.
   Fix: add to the comment that the check ran because of the 37 project rows, and point to finding 4.

4. **Outside the points: `harness.inherit` moves a batch's project rows to the next batch.** harness.py:265-267. Severity low. CONFIRMED on the night: bg_3's 37 run ids are now 37 rows of bg_4, all with a null criterion. The id comes from the path, and `INSERT OR REPLACE` takes the row. If two batches run at once, the earlier batch loses its project tests. Then `harness.tests_for` does not run them for that batch. Also, `has_tests` becomes None, and `mergeable` skips the criteria check. Night 147 ran its batches one after the other, so the concurrent case is PLAUSIBLE only.
   Fix: make the id include the batch, and keep `inherited_id(rel)` as the path sign for the encode door.

5. **One comment uses an idiom.** predicates.py:785, "Those tests kept this predicate quiet". Severity low. CONFIRMED by reading.
   Fix: write "Those tests satisfied the NOT EXISTS, so this predicate gave no wake."

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f3b11814-a94a-4967-b659-274275321190/scratchpad/rv239/`. Each probe reads the night database read-only and works on a copy in memory.

- `p2_batch_ids.py`: batches, `batch_tickets`, null batches, tests for each batch, the distinct batch for each criterion, and the tickets that are in two batches.
- `p1_night_case.py`: the final state with bg_3 set to running. It runs `tests_missing` and `mergeable` at HEAD and the parent's SQL.
- `p1b_walk2.py`: the walk-2 state, with bg_3's 37 run ids moved back. It runs HEAD and the parent's SQL, then the old rule with bg_3's own tests.
- `p3_readers.py`: the walk-2 state with no verdict. It runs `review`, `tests_missing`, `criteria_load`, and two `tests_encode` calls under a bg_2 id.
- `p4_greenfield.py`: a running batch whose ticket has no criteria, with a head and without one.
- `parent/`: `git archive 252feb0e` with the test file of 865b5132. pytest ran the three new tests there, 2 failed and 1 passed. At HEAD in the worktree, 3 passed.
- A `tr -cd` count of CR bytes in the three files gave 0 for each.

## (d) Usage

About 75k input tokens and 9k output tokens, about 84k in all, from the context counter. The total is over the brief's 40k cap, because findings 1 and 2 needed two more probes. No sub-agent ran.
