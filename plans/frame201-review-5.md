# Frame 201, review 5 of 52fe49e1

The change stands. Two low findings remain, and neither one blocks the merge.

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_p201c` at 52fe49e1 on fe4b3c78. Date: 2026-10-24 06:31.

## (a) Verdicts by point

1. Yes. The change does only what the brief says. The gate of the hold, the lines check and `_fail_on` stay unchanged. The hold prefills no claim and no fail.
2. No door refuses a right fail for good. A fail with no claim gets one refusal that names `claim_encodes`, and a claimed fail lands.
3. No. The 5 old tests asserted the reply text only. No old test asserted the fail offers.
4. Both new tests are red at fe4b3c78 for the named reason. Both are red when the hold is removed, so they catch that change.
5. The doubtful case does not belong to this frame. The case was 0 of N on every load since 2026-10-17, before the hold fired in it.
6. The commit adds no CRLF and no debug print.

## (b) Findings

1. `rota/roles/api.py:12975`, `_HOLD_SAY`. Severity low. CONFIRMED. The new text says "your own fail" and does not tell the seat to name the criterion. The old text said "fail on c1". `verdicts_emit` checks the claim only `if failed_criterion:` (line 12477). The probe sent `verdicts.emit(result='fail')` with no criterion after a hold, and the write staged with `failed_criterion: None`. The door is older than this change. The new text makes a bare fail more likely, because it no longer names the criterion. Fix: write "your own fail on the criterion" in `_HOLD_SAY`, or refuse a fail with no `failed_criterion` in `verdicts_emit`.
2. `rota/roles/api.py:12483-12503`, the claim branch of `verdicts_emit`. Severity low. CONFIRMED. A seat that did not claim and sends its own fail after the hold gets one more refusal before the fail lands. The probe showed the refusal, then the claim, then the fail landed. On the recorded cases the seat claims on turn 0, so the cost did not show. The refusal key differs from the hold key, so the four-turn stop does not count the two together. Fix: none needed now. Measure the extra turn on the next night.
3. Point 5, the measurement. Severity low. CONFIRMED. `L1-CR-fail-names-its-criterion` at 5 of 5 is one load, `qwen3:8b@249002`. Ollama is deterministic per load, so the five runs are one sample. In the run, the lines check refused twice. The hold then fired on turn 2. On turn 3 the seat said "the opposite" and sent its own fail with `failed_criterion`. The fail landed on the claim from turn 0. Fix: record the case on a second load before the frame claims a rate.
4. Point 5, the doubtful case. Severity low. CONFIRMED. In all 5 new runs the seat claims True and passes on turn 0. The hold fires. On turn 1 the seat says the line "does what the criterion says" and sends the same pass, which lands. The seat then sends the pass twice more and gets "already landed". No turn names the Terminologist. Neither the old hold text nor the new hold text names the Terminologist. No cassette holds a run with the old hold text, because the case was STALE at fe4b3c78. So the data cannot show that the new text makes the question less likely. Every earlier run with hash `47f78c38b1cf2ee0` failed the same way with no hold. Fix: keep the case as a known red outside frame 201, and name it in the baseline.
5. Outside the points. `tests/rota/test_frame201_first_pass_hold.py:150`. Severity low. PLAUSIBLE. `test_the_hold_offers_no_fail_route` asserts `"claim" not in said`. A future criterion text that holds the word "claim" makes the test red for a reason unrelated to the hold. The fixture text holds no such word today. Fix: assert on the text after the last quoted line, or assert the absence of "claim and fail".

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/51917779-9e71-4bcd-b8e5-e5cbc8b1f811/scratchpad/r5/`.

- `oldhold.py`: a pytest plugin. With `R5_MODE=old`, the plugin execs the hold block of `git show fe4b3c78:rota/roles/api.py` into the module. With `R5_MODE=nohold`, the plugin replaces `_first_pass_hold` with a no-op. The plugin ran `tests/rota/test_frame201_first_pass_hold.py`. Old: 7 red, the two new tests among them, at lines 150 and 175. No hold: 10 red, the two new tests among them, at `_held` and line 173. New: 11 passed.
- `test_r5_probe.py`: after a hold, a bare fail stages with `failed_criterion: None`. An unclaimed fail on c1 is refused, and after `claim_encodes` the fail lands. 2 passed.
- `cas.py`, `cas2.py`, `cas3.py`, `cas4.py`: read `D:/repos/rota/tests/rota/cassettes.db` with `?mode=ro`. They print the runs by prompt hash and load, and the transcripts of seq 540988, 540943 and 540983.
- `git show 52fe49e1 | grep -c` with a CR character: 0. The blobs at both commits hold no CR. `git status` in the worktree is clean. The added lines hold no `print(` and no `breakpoint`.

## (d) Usage

Input tokens: about 60k. Output tokens: about 9k. Total: about 69k.
