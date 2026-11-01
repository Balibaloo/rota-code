# Review p2 of frame 278: 43192f27, on the branch as 40548281

Verdict: accepted. H1 and H2 are closed on the dry1 copy. No new high. 4 low. Tests: `tests/rota/test_frame278_challenge_rounds.py` 10 passed. The gate did not run.

Worktree `C:/Users/roman/rota_f354r` at 40548281. `rota.__file__` is in the worktree. Copy of dry1 after turn 12: `scratchpad/dry1w6/dry1.db`, never written. The probe ran on the copy `scratchpad/rv/rv4.db` and rolled back each change.

## Result

Highs: none.

Lows:

1. L1 stays, and its price falls. The count has no reset, so `tests_failing` stays silent for bg_1 at every later head. A red run at a new head parks the batch at once, and the Developer never gets a turn. CONFIRMED by probe p8, point 3. Fix: count only the challenges with `messages.seq` above the last closed park ask of the batch. The park ask and the challenges are both messages, so they share one order. Price: 0.5 cycle, no schema.
2. L5, `rota/core/predicates.py:1880-1888`. The `park_ask` wake detail reads "bg_1 is parked. The team gave up on: . It is a page." The Liaison reads this detail. CONFIRMED by probe p8. Fix: when `given_up` is empty, put `challenge_words` in place of the key list. Price: 0.2 cycle and cassette drift on park cases.
3. L6, three copies of the count. `stopped_bouncing` (`scheduler.py:1975`) and `tests_failing` (`predicates.py:992`) read `challenged_reds` with no head filter. `gave_up` (`scheduler.py:2031`) reads it with the head filter. At a new head with the old red run, `stopped_bouncing` is True, and `gave_up` and `parked` are False. CONFIRMED by probe p8. No wrong action follows today, because `do:harness` fires next. Fix: one helper for the count at head that the three sites read. Price: 0.3 cycle.
4. L7, the revise of a criterion does not end a park on the count. `gave_up` reads the head commit only, and a key park lifts on a criterion move. The batch then waits for a new commit, and the page says so. PLAUSIBLE: read from the code, no probe moved a criterion. Fix: the reset of L1 at the park answer covers this case. Price: inside L1.

## 1. H1

Closed. On the copy with bg_1 `running`, `tests_failing` returns `[]`. `challenged_reds` gives `tst_waited` at the head commit `4fcd6d73`, 6 challenges, versions 3, 5, 6, 7 and 8. `stopped_bouncing`, `parked` and `gave_up` are True. `_next_rung` is empty. `spent_park` and `quiet_park` return `do:park bg_1` with the detail "bg_1: the Developer challenged tst_waited 6 times, and the Tester wrote versions 3, 5, 6, 7 and 8, and its ladder is spent". `preempt` returns `[]`, because no challenger exists.

The chain still stops at the frontier on the copy. `frontier_readonly` holds two Architect `tick:unresolved` wakes (m98, m99) and two Critic `tick:challenge` wakes. `_quiet_last` keeps the quiet park back while they are ready. None of the four keys has a row in `tick_attempts`, so each can run up to `tick_attempt_cap` 3 times. The park then fires when they drain or stall. PLAUSIBLE bounded, because the cap holds for each key. This stop is not H1. The Developer wake is gone.

After `do:park` (`loop.py:486`, `lifecycle.defer`), `park_ask` wakes the Liaison with refs `click_pause_returns_true_on_key, bg_1` and the id `m_park_421158fa15_bg_1`. `_park_page` renders "The team challenged the check tests/test_termui_tk_1_criteria_waited.py 6 times, and wrote versions 3, 5, 6, 7 and 8 of it." and the last red line. The page has the test, the count and the versions of the Tester.

## 2. H2

Closed. With bg_1 `deferred`: `gave_up` True, `given_up` `[]`, `parked` True, `park_owns` True, `close_stale_park_asks` closes 0, `next_batch` `[]`. `_render_state` puts bg_1 in `held` through `parked`, so the page does not count it as pending work. On the copy the page shows "Waiting on you: 2 things" first and returns before the Stuck lines. That return is older than this commit, and the key parks share it.

`gave_up` is not the one check. `stopped_bouncing` keeps its own read of `challenged_reds`, gated on `running` and with no head filter. `tests_failing` adds a third read with no gate. See L6. On a deferred batch they cannot disagree, because `stopped_bouncing` is False there and `parked` reads `gave_up` first.

## 3. A new head and a revise

New commit, probe p8: `gave_up` False, `parked` False, `next_batch` gives bg_1. The batch resumes. At the new head, before a run, `tests_failing` is `[]`, `stopped_bouncing` True, `parked` False, `spent_park` None, `exhausted` `[]`. `frontier_readonly` holds `do:harness bg_1`. So the test runs at the new head.

If the run is red, `challenged_reds` still counts 6, because the count has no reset. `parked` turns True through its last exit, and `spent_park` returns `do:park` at once, because the ladder is spent. `park_ask_id` hashes the head, so the ask opens under a new id. The batch does not loop. Each commit costs one harness run and one page. The cost is that the Developer is never woken on the red test again, at any head. If the run is green, `challenged_reds` is empty and the batch goes on.

Revise of a criterion with no new commit: the park holds, because `gave_up` reads only the head. `park_ask_id` moves with the criteria versions, so a new ask opens once the old ask closed. See L7.

Price of the reset: the report of pass 2b says messages and runs share no order. That is true for a reset at a green run. The reset at the park answer needs no run order, because the park ask is a message. Count the challenges after the seq of the last closed park ask of the batch. This gives the Developer three new challenges after each answer, and it covers the revise. Price: 0.5 cycle.

## 4. L2

Closed. Probe p8, quoted:

- Below the cap: "the Developer challenged tst_waited 6 times, and the Tester wrote versions 3, 5, 6, 7 and 8"
- At the cap, with `failing_attempt` patched to 10: "attempt 10 of 10; the Developer challenged tst_waited 6 times, and the Tester wrote versions 3, 5, 6, 7 and 8"

## 5. Readers of `given_up` alone

The map lists 8 callers of `given_up`.

- `park_ask` (`predicates.py:1880`) builds the detail from the keys. It matters on dry1. See L5.
- `park_ask_id` (`scheduler.py:2493`) gets an empty key string. The head and the versions still move the id. It does not matter.
- `quarantined` (`predicates.py:1805`) skips a key that a park owns. A park on the count has no key. It does not matter.
- `park_untested` (`scheduler.py:2173`) and `_park_page` (`principal.py:2422`) read the `tests_missing` key of the Tester only. It does not matter.
- `_render_state` (`principal.py:413`) reads `keyed`, then `looped` for the rest. The commit handles it.
- `_running_given_up` and `gave_up` are the helpers themselves.
- `rota/tools/invariants.py:172` reads `park_owns`, so it follows `gave_up`.

## Probes

All in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/62bcfbfb-da09-4019-9041-3a50cdca6a58/scratchpad/rv/`. Each ran from the worktree root with `PYTHONPATH` on it.

- p8 `p8.py` on `rv4.db`, a fresh copy of `dry1w6/dry1.db`. Running bg_1: `tests_failing`, `challenged_reds`, `stopped_bouncing`, `parked`, `gave_up`, `_next_rung`, `stop_detail` below and at the cap, `spent_park`, `quiet_park`, `preempt`, `frontier_readonly`. Then bg_1 deferred: `park_owns`, `next_batch`, `park_ask`, `park_ask_id`, `close_stale_park_asks`, `_render_state`, `_park_page`. Then a new head, deferred and running. Every change rolled back.
- p9 inline on `rv4.db`: the `tick_attempts` rows of the frontier keys, and the full `_render_state` with bg_1 deferred.
- p10 pytest `tests/rota/test_frame278_challenge_rounds.py`, `ROTA_MODEL=qwen3:8b`, `ROTA_DEV_DB` on `cassettes357.db`: 10 passed.

No probe called the model, ran the gate or ran rota. No probe opened `D:/repos/rota/.rota/dry1.db`.

## Usage

About 80k input tokens, 12k output tokens, 92k total. The review passed the cap of 20k.
