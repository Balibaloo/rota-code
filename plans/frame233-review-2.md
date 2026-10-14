# Frame 233, step 2: the diff review of 3a1da933

Read-only review on the worktree `C:/Users/roman/rota_rv233b` at 3a1da933. Meta workflow, the night's instrument. Reviewer: Opus, 2026-10-14.

**Verdict: accept, 0 high, 2 low.** The seed hits the key the wrap computes. The gate adds no red outside the known set of nine.

## (a) The points

1. The boundary is correct. The script takes `MIN(seq)` of the sessions with `trigger_msg = 'm_p1'`, and seeds every session below it. Nights 145 and 146 both give start s105, 104 sessions seeded, 0 skipped as native, 335 and 390 walk sessions left out. In both nights s105 is the Liaison that `m_p1` woke, and night 146's log says "ONBOARDED after 113 steps" before "== walk 1". (observed: probes 1 and 2, night146.log lines 20-24)
2. The keys are equal. The runner passes one `pins` object to `backend.complete` and writes `pins.as_dict()` to `sessions.pins_json`, so `Pins(**pins_json)` rebuilds the runtime key. The onboarding pins hold `think: null` and no other extra, so `extras()` is empty both ways. A night-146 seed replayed through `night_cassette.wrap` with each night-146 turn gave 104 of 104 sessions as `cassette:ollama` and 0 live calls. A night-145 seed against night 146 gave 78 of 104 sessions whole and 86 of 104 first turns. (observed: probe 2; runner.py:3329-3376, 3546, 4532)
3. The skip is safe in both directions, but the sign is wrong. A text session can have an empty completion when the model writes nothing after its thinking (reasoned: the text strips the thinking). Nights 145 and 146 hold 0 such sessions in onboarding (observed: probe 1). A skip then costs replay coverage only, never a wrong replay. A native reply can carry text beside its calls (reasoned: the protocol allows both). The profile check catches a native profile first. No production caller passes `native_tools=True` to `run_session`, so a native profile still runs the text protocol today (observed: grep, only tests/rota/test_pins.py:138 passes it). The profile skip is therefore an over-skip, which is harmless.
4. The gauntlet is correct for three of four parts. `WALK_REPLAY` and `ROTA_NIGHT_CASSETTES` prefix the onboarding command alone, so the walks get neither. `wrap` also returns the backend unchanged for any phase other than `onboarding`. `$STATE` is set at line 18, before line 98 reads it. `bash -n` passes. No night 147 exists under `.rota/`, and no `night_cassettes.db` exists, so the replay from this commit is not observed (observed: `ls .rota`). Probe 2 stands in for it at the wrap level.
5. The reset clears the carry. A recorded call, then a failed live session, then a session that replays whole: the new wrap with `begin()` gives `cassette:ollama`, and the parent wrap gives `ollama`. `step` runs one `run_session` per call, so `begin()` before each `step` covers each session. (observed: probe 3, loop.py:320-370)
6. The three lows of review 1 are fixed. Low 1 by `begin()` and its call at walk.py:278. Low 2 by the docstring sentence at night_cassette.py:45-47. Low 3 by the autouse fixture that restores `TALLY` in place. The test file alone printed no `cassettes:` line. (observed: the diff, the test run)
7. The tests are red on the parent. `begin` is absent at c6d507d9 (observed: probe 3), and `probes/seed_night_cassettes.py` is absent there, so both new tests raise. The tests do not cover: the walk's `begin()` call, the gauntlet line, the runner's real pins against a seeded key, the synthetic note turns (finding 1), and the default path from a worktree (finding 2). (reasoned: the test source)
8. The gate passes against the known set. Its five lines: `suite: 31 failed, 3869 passed, 35 skipped, 17 xfailed, 26 warnings`; `new reds (9)`, the same nine as review 1, with `test_scene_challenged_again` as the flaky one; `reds gone (1): L1-VK-a-statement-on-an-existing-account-is-a-behaviour`; `stale (0): none`; `time: 565.4s`. The worktree already held `.rota-gate.json` and `tests/rota/cassettes.db`, so the reviewer copied nothing. (observed: the gate, 2026-10-14)

## (b) Findings

1. **Low. CONFIRMED. Outside the points.** `probes/seed_night_cassettes.py:67-70`. The seed reads every `turns` row, and `db.session_note` writes a synthetic turn with an empty system and an empty user text (db.py:1196-1200). Night 146 holds 61 such rows in onboarding. The seed writes one cassette row under the key of two empty texts and counts the other 60 as "already present". No real prompt hits that row, so the replay is not wrong. The printed counts are wrong: of 313 turns and 59 present, 1 and 59 are note rows. Fix: skip a turn whose `system` and `user` are both empty, as `turns` keeps a note there.
2. **Low. PLAUSIBLE. Outside the points.** `probes/seed_night_cassettes.py:105`. The default destination is `night_cassette.cassette_path()`, which is `paths.RUNS`, the `.rota/` of the checkout that holds the script. The gauntlet reads `$STATE/night_cassettes.db` under `ROTA_RUNS` or `D:/repos/rota/.rota` (gauntlet_click.sh:18 and 98). A seed run from a night worktree without `ROTA_RUNS` writes a file the gauntlet never reads, and onboarding then runs live with no error. Fix: print the destination path and the gauntlet's path, or make the seed take the destination as a required argument.

## (c) Probes

All probes are under the scratchpad `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/9b79f4a1-9b90-4560-90e3-6e7dd48f1351/scratchpad`. Each opens the night databases with `file:...?mode=ro`.

- `rv2_p1.py`: the boundary, the `m_p1` row, the sessions near s105, the empty and failed turns, the profile and the pins of nights 145 and 146.
- `rv2_p2.py`: the seed of each night into `rv2_c145.db` and `rv2_c146.db`, then each night's onboarding turns through `night_cassette.wrap` with a counting fake, with `begin()` and `name` per session.
- `rv2_p3.py`: the failed-session carry on the new wrap and the parent wrap (`parent_night_cassette.py`, from `git show c6d507d9`), each on its own file. The probe also lists the duplicate keys inside night 146.
- `pytest tests/rota/test_frame233_night_cassette.py -q`: 4 passed.
- `python -m rota.tools.gate` from the worktree, foreground, 565.4s.

## (d) Usage

Input about 60k tokens, output about 10k tokens, total about 70k (reasoned: the reviewer's estimate; read the harness line for the true count).
