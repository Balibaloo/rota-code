# Frame 312, review 1: pass 1 at 7e1b8cdc

Verdict: accept with one fix. Commit 7e1b8cdc can go on the branch after the gate. Finding 1 is a follow-up for the next pass, and it does not block the gate.

The reviewer did not move `C:/Users/roman/rota_r311`. The review rules forbid a git command that changes a tree. The reviewer exported 7e1b8cdc with `git archive` to the scratchpad and probed that copy.

## (a) Verdict per point

1. Holds. `_stuck_ticks` reads `tick_attempts` by the exact key that `scheduler.tick_key` writes, `role|kind|refs`. `_stalled_keys` splits the refs on "," and matches the batch id exactly, so it also finds a key with more than one ref, such as `-|do:preempt|bg_1,echo_json`. No key form is missed.
2. Holds for m45 and m53. Fails for every other tick kind (finding 1). The sentence "Its tests passed at the review's last attempt" is true by the predicate and by the reset rules.
3. Right. A review key beside a Tester key gives "The team stopped work on this change." A missing test is work the team did not finish. The shift row of the same batch shows rota's names (finding 1).
4. No recorded L1 case goes stale. The `park` scene's request_shift wake text changes, but its seat is scripted, not recorded.

## (b) Findings

1. `rota/roles/principal.py:1370-1372` and `:1431-1433`. Severity high. CONFIRMED. For a tick kind that is not a review, the shift row writes the raw kind. The `park` scene probe gave this text: "The team gave up on tests_failing after 3 attempts." and "What it waits on: a new start of tests_failing." With a quarantined preempt, the night 160 copy gave "a new start of do:preempt". The request_shift wake carries this text to the Liaison (`predicates.py:238`), and the shift page shows it to the principal. The page contract shows his words, not rota's names. Fix: map each kind to words, for example tests_failing to "the fix of its failing tests". Leave out the `do:` scheduler keys, and leave out `liaison|tick:quarantined`.
2. `rota/roles/principal.py:1431-1433`. Severity low. PLAUSIBLE. On a tests_failing quarantine, the park ask is the way forward. The waits line says "a new start of tests_failing" and does not name the park page that waits for his answer. The `park` scene shows this line before `park_ask` opens. Fix: when a park ask of the batch is open or can open, name that page and do not name a restart.
3. `rota/roles/principal.py:1669-1671`. Severity low. CONFIRMED that the claim holds. `review` (`predicates.py:1338`) fires only when every run at the head passes. A new head commit, a test move or a criterion move clears the review's count or lifts its quarantine (`db.py:600-660`). So all three attempts ran on one green head. The claim fails only if a test run turns red at the same head with no move. The harness does not do that. Fix: none.
4. `rota/roles/principal.py:1667`. Severity low. PLAUSIBLE. When the wake names keys, `_stuck_ticks` ignores its `batch` argument. A key of a second batch on the page then counts toward the first batch's opening sentence. No recorded page has two batches with a stalled key. Fix: filter the given keys by the batch, as `_stalled_keys` does.
5. Outside the points. `rota/roles/principal.py` request block, an old line. Severity low. CONFIRMED. The m45 page still shows "The team gave up on: review for bg_1, 3 attempts." The line shows the id `bg_1` and repeats the new first line. Fix: drop the gave-up line when the opening sentence already names the review.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0cdcac52-3588-4266-b1fb-fc5d7d31b805/scratchpad/r312/`. The tree at 7e1b8cdc is in `src/` there.

- `p1_night160.py` reads `clickI_night160.db` with `?mode=ro`. It printed `_stalled_keys` = `['critic|tick:review|bg_1']` and `_stuck_ticks` = `[('review', 3)]`. Shift echo_json: "...all 35 of its tests pass. Its review stopped after 3 attempts with no verdict." and "a new start of its review." Shift confirm_default_on_eof: "nothing from you."
- `p1b_m45.py` and `p1c_m45.py` run on the copy `n160_copy.db`. They set bg_1 to running, and they stub `off_page` to undo m53's park. The m45 page opens with the review sentence. With an added Tester key, the page opens with "The team stopped work on this change." A preempt key at the cap gave "a new start of do:preempt".
- `src/tests/rota/test_zz_probe312.py` builds the `park` scene and spies on `_shift_where`. It printed "The team gave up on tests_failing after 3 attempts." and "a new start of tests_failing."
- A search of the cases: `tests/rota/cases/*.yaml` holds no `tick:review` key. The quarantined keys are in `l1_liaison2.yaml:522`, `l1_liaison2.yaml:589` and `l1_survey.yaml:208`. These cases render park pages or no page. The only request_shift case, `l1_liaison2.yaml:417`, has no batch. `l1_landing.yaml:312` has no batch.

## (d) Usage

About 75k input tokens and 9k output tokens, about 84k total. The review went over the cap of 20k because of the scene probe.
