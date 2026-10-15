# Frame 244, review 2: passes 2 and 2b at 4e9d53aa

Read-only diff review on the worktree `C:/Users/roman/rota_r244` at 4e9d53aa. Reviewer: Opus agent, 2026-10-15. Verdict: accept. The five points hold. Two low findings, no high finding.

## (a) Verdicts on the points

1. Holds. The block lists no path of `expected` or `possible` in either form, the disputed form lists each path once in order, `principal_said` leaves the shown message and stays in the inbound, and a `revise` shows no block (CONFIRMED, probe p12).
2. Holds. The scheduler builds every message wake with `detail=r["verb"]` (`rota/core/scheduler.py:117`), and night 149 stamps `wake_detail = 'relay'` on 5 Architect sessions. A routed model and a window survive beside `think=True`. A Liaison relay and an Architect tick keep the profile's think (CONFIRMED, probe p12).
3. Holds. The rule touches no recorded case beyond `L1-AR-a-ruled-constraint-gets-no-new-row`, `L1-AR-adopt-what-the-principal-approved` and `L1-AR-re-annotate-from-the-principals-correction` (CONFIRMED, probe p3 and the register).
4. Holds. The four new or changed tests are red at d633ce4f for the reason each names, and 19 of 19 are green at 4e9d53aa (CONFIRMED, probe p4).
5. Night 150's count, two lines, in section (b) item 5 below.

## (b) Findings

1. Point 1, `rota/core/runner.py:590-603`. No defect. The block cannot list a path of `expected` or `possible` by construction. `resolve_inbound` at `rota/core/runner.py:1995-2001` strips every disputed path from `expected` and `possible` before the block reads `disputed`. Probe p12 printed the s152 and s172 blocks with no path line, and a two-batch inbound (bg_2 and bg_3 contested, bg_4 revise) gave `tests/test_defaults.py`, `src/click/utils.py`, `docs/a.md`. The shared path `src/click/utils.py` showed once. The revise batch's `rev_only.py` stayed out. A relay with only `revise` gave an empty block and kept `principal_said` in the shown message. CONFIRMED.
2. Point 2, `rota/core/runner.py:138-146`. No defect. Night 149's `sessions` table holds `('architect', 'message', 'relay', 5)`, so the predicate matches the night. With a bound profile that routes the Architect to `qwen3.5:9b`, sets think False for it and a window of 8192, the relay wake got `qwen3.5:9b 8192 True`. The Architect's `tick:annotate` and `ask` wakes got `qwen3.5:9b 8192 False`. The Liaison relay got the base pins unchanged. CONFIRMED.
3. Point 3. The L1 cases with an inbound `verb: relay` are six. Three are Architect cases, and they are the three above. The others are Terminologist and Vision Keeper cases, which the rule does not reach. The scene and arc tests drive Architect relays through `ScriptedBackend` and `Pins(model="scripted")`, so no cassette key moves for them. The register's `key_misses` after 18:00 hold only the three Architect cases under the new rule, at 19:49 to 19:54. The register then holds live runs for all three at 20:01 to 20:04: 5 of 5, 5 of 5, and 9 of 10 for the re-annotate case. The pass 2b report says the gate re-recorded none. A later gate did, so that line in the report is out of date. CONFIRMED.
4. Point 4. From `git archive d633ce4f` with the two test files of 4e9d53aa copied in, 4 failed and 15 passed. `test_s152s_wake_shows_his_words_under_the_touch_list` and `test_s172s_wake_names_no_path_when_the_parser_found_none` fail on the old heading "he contested these files". `test_the_block_lists_the_disputed_paths_alone` fails because the old block lists the kept `src/click/termui.py`. `test_the_architects_relay_wake_thinks` fails on `assert None is True`. At 4e9d53aa, 19 passed. Gap, low: no test covers the dedupe across two contested batches, the revise batch's disputed paths, or a routed Architect profile with the relay rule. Probe p12 covers all three. Fix: add the two-batch inbound and the routed-profile wake from p12 as tests. CONFIRMED.
5. Point 5. Count a of n Architect relay wakes after a batch `contest` that keep a file his words decline, against night 148's 2 of 2 and night 149's 2 of 2. Read `sessions.pins_json` for `"think": true` on each, because night 149 shows `"think": null`. Count b of N right calls on the other relay wakes (approve, glossary contest, no verdict), and the wall-clock cost of a thinking wake against night 149.
6. Low, `rota/llm/cassettes.py:567-569` with the tier's pins. The case run's stamp says think false, and the session ran think true. The three Architect relay cases hold `case_runs.extras = '{"think": false}'` for the live runs of 20:01 to 20:04, but their cassette keys carry `think: true` from `routed_pins`. Frame 65 ruled that the key must carry the value the wire carries. The cassette key does. The case run's record does not. `casestatus.wanted_pins` reads the same false value, so the cases show green, and the register cannot say that these runs thought. CONFIRMED by a query of the register. Fix: stamp the case run with the pins that `routed_pins` returns for the case's wake, or record the per-session think beside the run.
7. Low, `rota/core/runner.py:595-597`. The disputed form says "The principal said these files have nothing to do with this change", but the paths are the output of `disputed_paths`, a parser guess. The night-149 interview found the seats read a heading as his own list. A parser false positive would now reach the seat as his own words. On s152 and s172 the parser found no path, so no recorded night renders this form. PLAUSIBLE: the form renders on synthetic data only. Fix: say "His words name these files" only after the parser's count on nights 148 and 149 shows no false positive, or word it as "These files match his words".

Outside the points:

8. Low, `rota/core/runner.py:140-141`, older than this commit. With a profile bound and no routed model or window for a role, `routed_pins` returns the base pins, and the profile's think for that model never applies. Probe p12 showed a Liaison relay at think False under a profile that sets qwen3:8b think True. The night's base pins come from the profile, so the effect on a night is likely nil. PLAUSIBLE. Fix: apply the profile's think before the early return.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4492a9c1-4457-41ce-a46b-42b300ec21c1/scratchpad/f244/r2/`.

- `p12.py`: runs `_files_contest_block` on the s152, s172, two-batch and revise inbounds from the test module, and `routed_pins` under a bound routed profile and with no profile. Run from the worktree root.
- `p3_cases.py`: lists every case YAML entry with an inbound `verb: relay`, by role.
- Register queries, inline `python -c`, read-only (`mode=ro`) on `D:/repos/rota/tests/rota/cassettes.db`: `key_misses` and `case_runs` after 2026-10-15T18.
- Night 149 queries, read-only on `D:/repos/rota/.rota/clickI_night149.db`: message wakes by role and detail, and `pins_json` of the five Architect relay sessions.
- p4: `git archive d633ce4f` into `r2/old`, with the two test files of 4e9d53aa copied in, then pytest on the two files there and in the worktree.

## (d) Usage

Input tokens: about 72k. Output tokens: about 8k. Total: about 80k, estimated from the context count. The harness line gives the true count. Sub-agents: none.
