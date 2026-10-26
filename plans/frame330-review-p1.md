# Frame 330, review 1 of 43d5985c

Date: 2026-10-26. Commit: 43d5985c on 58b8c8bd, worktree `C:/Users/roman/rota_r330`, read-only.

## (a) The verdict

**The change stands: the check stops the right batches, the ladder climbs and the park frees the seat, with one med gap in the tests.**

## (b) Findings

1. **med, CONFIRMED.** The law 9 preempt of a quarantined running batch has no test now. `rota/core/predicates.py:1637-1644`. Probe 3 gives `do:preempt (batch_1, batch_2)` on night 168's rows with `i_2` at priority 9 and a rung owed. The scenes `park` and `two_batches` proved this path at 58b8c8bd. No file in `tests/rota/` asserts it now. The unit tests at `test_predicates.py:1695` and `test_next_batch.py:65` cover the preempt of a batch that still bounces only.
   Fix: add a test to `test_frame330_stopped_bouncing.py`: priority 9 on `i_2`, one rung asked, expect `do:preempt`.
2. **low, CONFIRMED.** `exhausted` gates on the count per batch and writes the detail from the count across batches. `rota/core/predicates.py:1047-1070`. Probe 2: `b1` fails a shared test id at attempt 10, and `b2` ran that id later. The wake fires with the detail "attempt 4 of 10". The old gate did not fire, and the new detail is false.
   Fix: take the `attempt N` of the detail from `failing_attempt`, so the gate and the text read one count.
3. **low, CONFIRMED.** A comment in `parked` is now false. `rota/core/scheduler.py:2288-2289` says "A running batch keeps the old test, so this changes no preempt of a running batch." The key half of `stopped_bouncing` now changes the park of a running batch.
   Fix: rewrite the two lines to name frame 330 and the key half.
4. **low, CONFIRMED, outside the points.** A quarantine below the cap spends the ladder for good. Probe 1, last block: the three rungs are asked on the quarantine, a commit lifts the key, and the batch reaches attempt 10. Then `exhausted` gives `[]`. With no other batch, the seat then stays quiet at the cap with no new note. This follows the existing rule "The ladder is not asked again" in `parked`, so the risk is small.
   Fix: none now. Record the shape in frame 330's block, and act if a night shows it.

## (c) The points

1. Holds. `stopped_bouncing` gives True for attempt 6 with the key, True for attempt 10 with no key, False for attempt 6 with no key, False for a deferred batch with the key, False for the key of `batch_2` and of `batch_10`, False for a key not quarantined. No batch that was right to run stops (probe 1).
2. Holds. With `batch_2` pending the wakes are Developer, Architect, Vision Keeper on `tick:exhausted`, then `do:park`, then `park_ask` and `tick:batch_start|batch_2` (probe 1). With no other batch the three rungs wake, `preempt` gives `[]`, `batch_1` stays `running`, and the frontier holds nothing for it. Law 6 lines 186-188 allow "a page, a hold or a note". The Liaison's `quarantined` note reached the principal once, so the quiet is a hold with a note and not silence. Recommend: accept the implementer's "no park with no challenger". Revisit it with finding 4 if a night shows a held seat at the cap.
3. Holds. A deferred batch with the given-up key is `parked`, `exhausted` gives `[]`, and `next_batch` gives `batch_2`. A deferred batch at attempt 6 with no key is not parked. The deferred branch of `parked` has no change in the diff.
4. Holds with finding 1. At 58b8c8bd `park` proved that item 2's preempt defers a quarantined running batch and that the park ask follows (S3, S4). `two_batches` proved that the preempt defers b1, and not `do:park` (S1). Now both prove the three rungs and then `do:park` at item 2's grouping. S3, S4 and the S1 project-id door still hold. The general law 9 preempt keeps tests at `test_predicates.py:1695`, `test_next_batch.py:65` and `test_frame193_pass2.py:212`. The preempt of a quarantined batch lost its only proof.
5. Holds. `stop_detail` in `rota/core/scheduler.py:1751` gives the text from `_quarantined_tries`, the key's `attempts` column. `exhausted` and `preempt`'s park read it. At `loop_cap` it gives "", so both keep the old text (test 6 of the new file). "the tests still fail after 3 tries" is STE. Cases with `tick:exhausted` or `do:park`: `l1_developer.yaml` (detail "attempt 10 of 10"), `l1_exhausted.yaml` (attempts 10 and 11), `l1_judgement.yaml`. All are at or past the cap, and none holds a quarantined key of a running batch. The key in `l1_liaison2.yaml` is on a deferred `b1`. So this change predicts no stale case.
6. Holds with finding 2. The two counts differ only when another batch ran the same test id later. `failing_attempt` is then equal or higher, so the gate fires more, never less. The scene `two_batches` shares the project test ids between b1 and b2, but b1 is deferred and below the cap there, so neither half fires. Night 168's shape has no shared id.
7. Holds. Night 93's rows hold `s153`, `s156`, `s160` on `tick:exhausted|b_1`, so `_next_rung` gives "" (probe 2). With the key quarantined the ladder is spent, and `do:park` is the right answer. The downstream proof, a deferred given-up batch waits for the principal, still holds (29 passed). The fixture lost only the preempt route, which finding 1 covers.
8. One fault: the stale comment of finding 3. No CR byte in any of the 7 files (probe 4). No `print`, no bare `except`, and `git diff --check` is clean. `_quarantined_tries` narrows `given_up` to one key and one status, so it is not a copy. The frame and law names in the docstrings agree with the records.

## (d) Usage

The harness gave no split into input and output. The budget fell from 15,000,000 to about 14,925,000 tokens, so this review used about 75k in total. No sub-agent. Probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ac089aa1-c627-4128-af45-c49f490f4a93/scratchpad/r330/`: `probe1.py` (points 1 to 3 and finding 4), `probe2.py` (points 6 and 7), `probe3.py` (finding 1), and probe 4, a `python -c` call that counts CR bytes per changed file. Test run: `test_frame330_stopped_bouncing.py` and `test_next_batch.py`, 29 passed.
