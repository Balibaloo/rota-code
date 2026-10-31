# Review p3 of frame 355: commit 710b1520

Verdict: the claim holds, with 0 high and 5 low findings. Points: 4 hold (2, 4, 5, 6), 2 hold with a finding (1, 3), 0 fail. Tests: 211 passed, 3 skipped, 0 failed.

## (a) Verdicts on the points

1. Holds, with findings 1, 2 and 4. `probe_model` (runner.py 6492-6525) unwraps `RecordingBackend` and `RoutedBackend`, returns True for `ReplayOnlyBackend`, copies the backend with `timeout = 30.0`, then calls `inner.complete("", "Say OK.", Pins(model=pins.model, temperature=0.0, num_ctx=pins.num_ctx, max_tokens=1, think=False))`. Any exception returns False. On a loaded model the cost is one prefill of a few tokens and one token out, well under a second. On an unloaded model the probe pays one load. `plans/operating-facts.md` line 146 gives a median load of 2.8 s for qwen3:8b, and the slowest loads take 56 s to 115 s. So 30 s covers the median reload and not the tail. A slow reload reads as down, and the next retry finds the model loaded, so the cost is one wait of 60 s. A wrong model name on a live server gives an `HTTPError` (a `URLError`), so the probe returns False. That counts as down, and the stop line tells the reader to start the server (finding 1).
2. Holds. Probe `probe_cases.py` with `probe_model` mocked True. Case 1: a session that answered turns 1 and 2 and stalled on turn 3 spent its attempt on each of three retries, `attempts` 1, 2, 3, then `quarantined`. Case 2: `loop.run` on a head wake that never answers quarantined m1 after three steps. `model_down` stayed unset, and the run went on to the Liaison's `tick:quarantined` wakes. Case 3, the probe mocked False: three steps, `attempts` 0, and the stop line in `model_down`.
3. Holds, with findings 3 and 4. After three failed probes, `model_stop` (loop.py 551-588) writes the line, `loop.run` breaks, and `onboard_run.drive` prints `render_state` and returns. `cmd_run` then runs `return 0` (cli.py 541). The next `rota run` does not read `model_down` and starts as usual. Only `model_stop` removes the row, at a session that commits or keeps a model turn. No command clears it. On a copy of `D:/repos/rota/.rota/dry1.db` with the row set and 5 asks, `cmd_agenda` printed the stop line first and once, then the asks.
4. Holds. `ReplayOnlyBackend.complete` raises `LLMUnavailable(..., replay_miss=True)` (cassettes.py 477-483). `run_session` skips `instrument_end` when `exc.replay_miss` is set (runner.py 6439), so a cassette miss spends its attempt and no probe runs. A `RecordingBackend` over a replay backend unwraps to `ReplayOnlyBackend`, and the probe returns True with no call. Under record mode the probe goes past the recorder to the live backend and writes no cassette.
5. Holds. No hunk is outside the claim. The `db.py` hunk fixes review p2 low 4, the `predicates.py` hunk low 5, and the `model_stop` hunk low 6. The stop line now carries the time. Low 7 is moot, because no inference from the sessions table is left.
6. Holds. The five files with `-n0`: 211 passed, 3 skipped in 86.25 s. Per file: test_frame355_stalled_call.py 19, test_predicates.py 102, test_request_page.py 70, test_step_failure.py 3, test_f16_answered_mark.py 20. The three skips are at test_frame355_stalled_call.py 377 and 463, because the worktree has no `.rota/dry1.db`. One skipped test is the agenda test, and probe `probe_agenda.py` covers it.

## (b) Findings

1. runner.py 6522-6525 and loop.py 581-585, low. PLAUSIBLE: the code read shows it. The probe drops its exception, so a wrong model name on a live server reads as down. After three ends the stop line says "Start the model server", and the server is up. Fix: keep the probe's exception text and put it in the stop line.
2. runner.py 6516-6520, low. PLAUSIBLE: `plans/operating-facts.md` line 141 says a timed-out `/api/chat` call keeps running and the next call queues behind it. `LiteLLMBackend` does not stream. So after a 300 s timeout the probe can queue behind the dead call and fail at 30 s. A wake whose own call runs long then reads as down on each retry and stops the run. Fix: on the LiteLLM path, read `/api/ps` or wait for the server to go idle before the probe, or record which backend streams.
3. loop.py 561-571, low. CONFIRMED: probe `probe_clear.py` set `model_down`, then ran one end whose probe answered. The outcome was not unavailable, and `model_down` still held "Stopped: old". A probe that answers proves the model is up. Fix: remove the row when the end's probe answered, as for a kept model turn.
4. cli.py 539-541, low. PLAUSIBLE: the code read shows it. `cmd_run` returns 0 after a model-down stop, the same as a quiescent run. A night launcher cannot tell the stop from the exit code. Fix: return a non-zero code from `cmd_run` when `drive` stops on `model_down`.
5. Outside the points. llm.py 475 (`LiveView.open` in `OllamaBackend.complete`), low. PLAUSIBLE: the code read shows it. The probe goes through `OllamaBackend.complete`, so it opens the live file again. The probe's "Say OK." then replaces the failed session's view in `.rota/live.md`. Fix: set `LIVE_PATH` to "0" for the probe, or open no live view when `max_tokens` is 1.

## (c) Probes

All files are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/05666872-07ce-4805-be2d-636d5ab7329f/scratchpad/f355r3/`. Each ran from `C:/Users/roman/rota_f354r` at 710b1520 with `ROTA_MODEL=qwen3:8b` and `PYTHONPATH` at the worktree. No probe called a model.

- `probe_cases.py`: the test file's `Stalled` and `AnswersThenStalls` backends, `probe_model` mocked, `time.sleep` stubbed. Case 1 three `loop.step` calls, case 2 and case 3 `loop.run` with `max_steps=8`. Output in point 2.
- `probe_agenda.py` on `dry1_agenda.db`, a copy of `D:/repos/rota/.rota/dry1.db`: set `model_down`, counted 5 asks, ran `cli.cmd_agenda` with `limit=3`. Output: the stop line first and once, then `[m3]`, `[m17]`, `[m16]` and the rest.
- `probe_clear.py`: set `model_down`, ran `loop.run` with `max_steps=1` on `Stalled` with the probe mocked True. Output: `unavailable False`, `model_down` unchanged.
- The suite: the five files of point 6 with `-q -n0 -rs`, then `--co` for the counts per file.

## (d) Usage

Estimate. The harness gives this agent no counter. The peak context was about 63k tokens. The input across the calls was about 900k, and the output about 10k. Total about 910k across the calls. The cap of 30k ran over. Most of the cost was the diff, the backend reads and the test run.
