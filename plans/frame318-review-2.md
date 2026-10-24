# Frame 318, review 2: commit f434fc23 in `C:/Users/roman/rota_p318w6`

Verdict: does not stand as committed. The `batch_start` hold is right. The
`verdict_failed` hold is a wrong hold on a shape night 160 shows twice.
Add `tick:verdict_failed` to the keys a criteria move reaches, and the
commit stands.

## (a) The points

1. Holds. The new test passes. Probe P1, a Tester `tests` body move,
   keeps `batch_start` at (3, 1) and lifts `tests_failing`.
2. Partly wrong. `batch_start`, `finding_violated`, `findings_exhausted`
   and `touch_mistaken` are right to hold. `verdict_failed` is wrong to
   hold. See finding 1.
3. Holds. `test_frame318_quarantine_lift.py`, `test_desk_guards.py`,
   `test_frontier_order.py` and `test_touch_note.py` pass, 13 and 372.
4. Holds. The script re-run gives 9 and 20. My own query of nights 162
   and 163 gives the same keys: 162 has two red keys, b_2 at s217 and b_3
   at s323. 163 has `verdict_failed` bg_1 at s135 and six `batch_start`
   reports, s223 to s262.
5. Holds for a write that does not amend. `test_steering.py` lines 172
   and 256 hold it, and both pass. A same-text criteria update amends.
   The version moves, so it lifts (probe P5). That behaviour is older
   than this commit.
6. Refuted. `_forget_batch_counts` deletes only rows with
   `quarantined = 0`. A key has one row, so a held key keeps (3, 1)
   (probe P6). The open gap is different. See finding 2.
7. Not stale. The L1 cases that seed a quarantined row are
   `l1_liaison2.yaml` lines 524 and 591, `developer|tick:tests_failing`,
   and `l1_survey.yaml` line 210, a Terminologist key. The rule lifts
   both kinds as before.

## (b) Findings

1. High. `rota/core/db.py` lines 671 to 689. CONFIRMED. The rule holds
   `developer|tick:verdict_failed` after a criteria move. The
   failed verdict stays at the head. `review` in
   `rota/core/predicates.py` line 1367 needs no verdict at the head, so
   the Critic never re-judges. Only a Developer commit frees the batch,
   and the Developer key is held. Probe P2 shows the key at (3, 1),
   `review` empty, and the `verdict_failed` wake still due. The frame 306
   route is his park page correction: the Terminologist relays it and
   respecifies the criterion. After it, the batch waits for the next
   park ask, and his correction frees nothing. Night 160 shows the
   opposite outcome on HEAD. bg_2 was held at s192. The s195 respecify
   lifted it, and at s197 the Developer committed `batches:bg_2`. The
   s255 respecify lifted it again, and at s258 the Developer committed.
   So two of the nine "stops" were lifts that bought a commit.
   Fix: add `tick:verdict_failed` to `_RED_TICKS`, and invert the second
   test.
2. Medium. `rota/core/db.py` line 690. CONFIRMED by reading, and the
   report's open question 1 names it. `_forget_batch_counts(conn, b)`
   still resets a live `batch_start` count before it reaches 3. On the
   night 163 shape, a respecify at 2 of 3 buys the same refusal two more
   ticks. Fix: pass the keys `_row_move_reaches` refuses as `keep`
   patterns, with one test.
3. Low, outside. `rota/roles/api.py` line 6330. PLAUSIBLE.
   `criteria.retire` writes with `amends` False. A retire moves no
   version, so it lifts nothing (probe P8: `tests_failing` and
   `critic|tick:review` stay at (3, 1)). The `_RED_TICKS` comment says a
   criteria move "retires" the tests, and a retire is no move. The red
   wake drops the retired test, but `given_up` still lists the held key,
   so the batch can stay parked. Fix: treat a `retired_by` write as a
   move in `_subject_moved`, or correct the comment.
4. Low. The count script counts any `criteria` receipt as a move. A
   retire receipt moves nothing, so it can overcount. Nights 160 to 163
   show no retire in the counted rows. Fix: none needed for this frame.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/a0790d20-6463-44cf-97ca-89e1ddd75c84/scratchpad/r2_probe.py`,
  run with `PYTHONPATH` at the worktree. It ran P1 (tests move), P5
  (same text), P6 (live count beside a hold), P2 (failed verdict at the
  head, then a respecify) and P8 (retire).
- `.../scratchpad/r2_after.py 160 bg_2 180 290` and `163 bg_1 180 230`:
  sessions and receipts after each `verdict_failed` lift.
- An inline query of nights 162 and 163: quarantine reports and the
  sessions with a `criteria` or `tests` receipt.
- The implementer's `f318w6_count.py`, re-run unchanged.
- pytest: the two frame 318 files (13 passed), the pass 1 callers' files
  (372 passed), and two `test_steering.py` no-move tests (2 passed).

## (d) Usage

About 45k input tokens, 9k output tokens, 54k total. The brief's cap was
about 20k.

## Re-check of 6f3181bd

Verdict: the commit stands. Findings 1 and 2 are closed.

- Finding 1: closed, CONFIRMED. `_RED_TICKS` at `db.py` line 683 holds
  `tick:verdict_failed`. Probe P2 again: after a respecify, the held
  `developer|tick:verdict_failed|bg_2` key is gone.
- Finding 2: closed, CONFIRMED. Lines 668 to 676 pass the live keys that
  `_row_move_reaches` refuses as `keep`. Probe P9: a live `batch_start`
  count of 2 stays (2, 0) after a respecify. The live Critic and
  `tests_failing` counts at 2 reset as before.
- Low, new, PLAUSIBLE. `keep` takes the exact keys as LIKE patterns. The
  `_` in `batch_start` and `bg_2` matches any one character. A distinct
  key that differs only at those places would also keep its count. No
  such key exists in the tick kinds. Fix: none needed now.
- Tests: `test_frame318_criteria_lift.py` and
  `test_frame318_quarantine_lift.py`, 14 passed.
- Probe: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/a0790d20-6463-44cf-97ca-89e1ddd75c84/scratchpad/r2_recheck.py`.
- Usage of the re-check: about 7k input tokens, 2k output tokens, 9k total.
