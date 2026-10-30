# Review of frame 349, commit 8585d56f on rota/foundation, pass 3

Verdict: ready to close. Pass 3 fixes the high finding and the two lows of review p2 that it names, and each fix holds under a probe. One low finding remains outside the points. The new exit `schedule.reask` refuses in a session that no answer woke. Counts: 0 high, 1 low.

Worktree: C:/Users/roman/rota_f349c at 8585d56f. Parent tree: C:/Users/roman/rota_f349p at b4801fa1, and the scratchpad copy `f349r3/ptree` (git archive of b4801fa1).

## (a) Verdicts on the points

1. Yes for all 4 roles. In mode `normal` the developer, the architect, the vision keeper and the terminologist get "The exit is schedule.reask(what_is_missing=...) with the reason: what the two answers left open". `("schedule", "reask")` is in `api.REGISTRY`, the mode holds the op, and `_holds` is True. The modes that hold a question and lack the op (architect, terminologist and vision_keeper `deliver`, and 6 developer modes) get "end the session with no call".
2. Confirmed. The lint at this commit, with the parent's sandbox.py, reports one finding: `_bind_send:schedule.unresolved`, "sandbox.py:4097 names `schedule.unresolved`, which no door admits". On this commit it reports nothing. The lone-dotted-string rule gives no false positive. Only 7 strings name `schedule.*`, and all name `schedule.reask`. `test_f25_offers_in_mode.py`: 68 passed.
3. Confirmed. At b4801fa1 both new tests fail on the text "The exit is schedule.unresolved". At 8585d56f both pass.
4. None. The sandbox.py diff has three hunks. Hunk 1 drops the dead developer branch of the same-refs rung. Hunk 2 changes a comment only. Hunk 3 is the third-question `else` branch. The api.py hunk changes a comment only. The developer holds one send to the tester in every mode, `msg.challenge_tester`, and it returns at sandbox.py 3398 before the rung. So hunk 1 changes no behaviour.

## (b) Findings

1. `rota/core/sandbox.py:4090-4093`, the third-question `else` branch. Severity low. CONFIRMED. Outside the points.
   The text names `schedule.reask` when the mode holds it. `schedule_reask` (api.py 17329) refuses when `ctx.trigger` is empty: "nothing woke you with an answer".
   Probe `f349r3/test_probe_reask_exit.py`: architect/normal with no trigger got the refusal, then the reask refusal. With trigger `a2` the reask returned `{'id': 'q2', 'status': 'unresolved'}`.
   A session that a batch or a tick wakes meets the third-question door and gets an exit that the op refuses.
   PLAUSIBLE also: a trigger that answers a question on other rows makes the reask mark that other question.
   Fix: name the reask only when `ctx.trigger` is an answer to a question of these rows, else give the end.

Outside, no finding: tester/answer holds `schedule.reask`, and the tester branch still gives it the end. Frame 135's law rules that branch.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/a9a43280-d634-4af9-9ae0-e50791297894/scratchpad. Each ran from the worktree root with `PYTHONPATH` set to the tree under test.

- `f349r3/test_probe_third_q3.py` at 8585d56f: the p2 probe with the hold of `schedule.reask` added. A third question from 4 roles on rows answered twice. 4 passed, and all texts name `schedule.reask`.
- `f349r3/probe_lint.py` at 8585d56f: `lint.findings()` on this tree, then with `_trees` patched to parse the parent's sandbox.py. It lists every `schedule.*` name that the lint reads.
- An inline probe on `lint.modes()`: the modes that hold a question and lack `schedule.reask`, the developer's sends to the tester, and the critic and tester modes that hold `schedule.reask`.
- `f349r3/test_probe_reask_exit.py` at 8585d56f: architect/normal meets the third-question door, then calls `schedule.reask` with no trigger and with trigger `a2`.
- `f349r3/ptree`: git archive of b4801fa1 with the commit's test file as `test_f25_new_probe.py`. The two new tests failed on the old text.
- At 8585d56f: `test_f25_offers_in_mode.py`, 68 passed. The 4 third-question tests passed. The gate did not run, because no point needed it.

## (d) Usage

About 45k input tokens, about 8k output tokens, about 53k total.
