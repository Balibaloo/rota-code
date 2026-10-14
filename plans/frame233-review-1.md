# Frame 233, step 1: the diff review of c6d507d9

Read-only review on the worktree `C:/Users/roman/rota_rv233` at c6d507d9. Meta workflow, the night's instrument. Reviewer: Opus, 2026-10-14.

**Verdict: accept, 0 high, 3 low.** The wrap does what the frame's step 1 asks. The gate adds no red outside the known set.

## (a) The verdict on each point

1. `name`: one reader exists, `rota/core/runner.py:4533`, and no print or log line reads it. No two sessions interleave, because `step` runs one `run_session` per wake with no thread. A failed session never reads `name`, so its counts carry into the next session (finding 1). (observed: grep of `rota/` and `probes/`, runner.py:4568-4593, probe 1)
2. `backend.replay` exists. `RecordingBackend.__init__` sets `self.replay` at `rota/llm/cassettes.py:335`, so the walk's print does not raise. (observed: the source)
3. The key is `key_for`: the model, the temperature, `num_ctx`, the protocol, the whole system text, the user text and `pins.extras()` when set. A changed brief or door changes the system or user text, so it changes the key. `pins.prompt_hash` is not in the key. The tool schemas are not in the key, only the protocol (finding 2). (observed: cassettes.py:203-219, probe 1)
4. The miss path runs live on the inner backend and records. It does not raise. With `WALK_REPLAY=1`, a new prompt reached the fake once, wrote 1 row, and the second call hit with `cassette:fake`. (observed: probe 1, the test file 2 passed)
5. The register is untouched. `git diff c6d507d9~1 c6d507d9 -- rota tests/rota/cassettes.db` is empty. The night file defaults to `paths.RUNS / "night_cassettes.db"`. The gauntlet exports `ROTA_RUNS=$REPO/.rota` with `REPO=D:/repos/rota`, so every night worktree shares one file under `.rota/`. (observed: the diff, night_cassette.py:31, gauntlet_click.sh:9 and 18)
6. The import resolves. Python puts the script's own directory first on `sys.path` for `python <dir>/probes/walk.py`, from any working directory. `probes/walk.py:34` already imports `progress` the same way on every night. `walk.py:15` puts the repository on the path before the import, so `from rota import paths` resolves too. (reasoned: Python's script-path rule, observed: walk.py:15 and 34)
7. The test is red on the parent: `probes/night_cassette.py` is absent at c6d507d9~1, and the test loads that path. The test does not cover the walk's 7 lines, the print, or the import from another directory (points 2 and 6). It does not cover the carry of counts after a failed session (point 1), a changed system text that runs live (point 3), or the default path under `.rota/` (point 5). (observed: `git ls-tree c6d507d9~1 probes/night_cassette.py` is empty, the test source)
8. The gate from the worktree: 31 failed, 9 new reds with 1 flaky, reds gone 1, stale 0, 561.4s. The 9 match the known set by composition: the 2 HEAD reds, the 2 Architect cases, `L1-DV-apply-the-answer-and-carry-on`, `L1-TS-encode-a-criterion-the-principal-corrected`, the 2 L2 Developer cases and `test_scene_challenged_again` as the flaky one. (observed: the gate's five lines, 2026-10-14; reasoned: the match is by the stack's list at line 291, not by name)

The five lines:

```
suite: 31 failed, 3867 passed, 35 skipped, 17 xfailed, 26 warnings (baseline: 24 failed, 3580 passed, 32 skipped, 20 xfailed, 17 warnings)
new reds (9): test_invoke_door::test_a_session_with_no_batch_reads_the_root, L1-AR-a-test-that-misses-its-criterion-gets-a-decision-row, L1-AR-route-an-escalation, L1-DV-apply-the-answer-and-carry-on, L1-TS-encode-a-criterion-the-principal-corrected, L2-DV-name-the-block-rather-than-retry, L2-DV-name-the-deferred-batch-not-the-running-one, test_scene_challenged_again::test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op, test_scene_two_batches::test_a_right_call_lands[the project test tests/test_templates.py as an encode]
reds gone (1): L1-VK-a-statement-on-an-existing-account-is-a-behaviour
stale (0): none
time: 561.4s, model qwen3:8b, temp root C:/Users/roman/rota_gate/tmp, baseline 5d68808 2026-10-11 02:11
exit 1: 9 new reds, 1 of them flaky
```

The worktree already held `.rota-gate.json` and `tests/rota/cassettes.db`, copied by the holding session at 08:33. The reviewer did not copy them again.

## (b) Findings

1. **Low. CONFIRMED.** `probes/night_cassette.py:50-55` with `rota/core/runner.py:4568-4593`. A session that fails never reaches `getattr(backend, "name", "")`, so `name` does not reset. The failed session's calls then count in the next session's `sessions.backend`. Probe 1: a failed all-hit session, then a session with no call, gave `cassette:fake`. A failed live session, then an all-hit session, gave `fake`. The error is at most one session per failure. Fix: reset the counters in `probes/walk.py` before each `step`, through a `NightBackend.begin()` method.
2. **Low. CONFIRMED for the key, PLAUSIBLE for the effect.** `rota/llm/cassettes.py:342-343`. The key holds the protocol and not the tool schemas. A door that changes only a native schema keeps the key, and the wake replays the old reply. The night runs the text protocol today, because `native_tools` is opt-in and `walk.py` does not pass it, so the doors are in the system text. Fix: add one sentence to `night_cassette.py` that the replay is valid for the text protocol only, or hash `tools` into the night key.
3. **Low. CONFIRMED. Outside the points.** `tests/rota/test_frame233_night_cassette.py`. The fake's recordings go into the suite's global `TALLY`. The test file alone printed `cassettes: 3 recorded in 0.0s`. `conftest.py:116` then saves the run to `.rota-timings.json`, and `Tally.previous()` reads the newest run with `records` as the cost of a record. A fast fake record then makes the next estimate near zero. Fix: in the test, save `TALLY.as_dict()` before and restore it after, or give the fake wrap a private tally.

Read and found sound: `host` and `default` pass the card endpoint for an Ollama inner and a `RoutedBackend` inner (observed: loop.py:118-124, llm.py:638-641). A `None` backend wraps `llm.default_backend()`, which is what `run_session` builds at runner.py:3328 (observed). Nothing in `rota/` tests `isinstance(backend, RecordingBackend)` (observed: grep).

## (c) Probes

- Probe 1, `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/9b79f4a1-9b90-4560-90e3-6e7dd48f1351/scratchpad/rv233/probe1.py`: a counting fake behind `wrap(..., "onboarding")` over a temporary file with `WALK_REPLAY=1`. It ran the miss path, the hit path, the two carries after a failed session, and three `key_for` comparisons.
- The test file at c6d507d9: `ROTA_MODEL=qwen3:8b python -m pytest tests/rota/test_frame233_night_cassette.py -q`, 2 passed in 3.06s.
- `git ls-tree c6d507d9~1 probes/night_cassette.py`: empty.
- `git diff c6d507d9~1 c6d507d9 --stat -- rota tests/rota/cassettes.db`: empty.
- The gate from the worktree, unpiped: `python -m rota.tools.gate`, 561.4s.
- Greps for readers of `name`, `host`, `default`, `RecordingBackend` and `TALLY` in `rota/`, `probes/` and `tests/rota/conftest.py`.

## (d) Usage

About 62k input tokens, 9k output tokens, about 71k total, against a cap of 60k. The harness line holds the exact count. The gate's 561s is wall time and no tokens. No sub-agent.
