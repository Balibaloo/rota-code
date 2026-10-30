# Review of frame 349, commit 81b85d3d on rota/foundation, pass 1

Verdict: not ready to close. The 8 guards are correct and keep the old text for each mode that holds the call. The claim "a refusal names a call only where the mode holds it" is false on 2 live paths that the pass does not touch. Counts: 2 high, 4 low.

Worktree: C:/Users/roman/rota_f349 at 81b85d3d, parent 106647aa. Parent tree: the scratchpad copy `f349r/parent` (git archive, no worktree).

## (a) Verdicts on the points

1. No live seat reaches `_holds` with no wake and no mode. `_holds` reads `_wake_mode_set`, the same list as `held_calls`, but it does not intersect the role's graph. In a mode with no `.tools` file it holds every call (F3).
2. Yes at all 8 places. Each mode that holds the call gets the old text byte for byte. No no-call branch names a call. Places 7 and 8 give the fact with no route (F4).
3. Confirmed. With a live wake, developer/finding_violated and touch_mistaken refuse `msg.challenge_tester` with `NotInWorkingSet` before any door. The same function names `msg.escalate_architect` to developer/answer, which lacks it (F1).
4. The 2 that pass on the parent are the two "where held" tests. They hold the positive side: the guard keeps the call for a mode that holds it. The place 9 test fails on the parent only with `AttributeError: _holds` (F6).
5. Neither guard changes what a mode sees. Only vision_keeper/orient meets `@program`, and only terminologist/define meets `@term:x`. Both hold the call. The `@program` guard is dead, and its fallback names `problem.assert` anyway (F5).
6. Yes. The 7 rows match the 7 emptied keys. `test_f33_debts_name_open_frames.py` and `test_f25_offers_in_mode.py` give 69 passed.
7. Both are unrelated to the pass. The held card test passes on the parent. The L3R case runs liaison/landing, which holds only `rulings.rule` and `rulings.line`. No changed text is on that path (F7).

## (b) Findings

1. `rota/core/sandbox.py:3196-3199`, `_escalation_or_step`. Severity high. CONFIRMED.
   developer/answer holds `msg.challenge_tester` and lacks `msg.escalate_architect`.
   A fourth challenge on the same refs meets the cap and gets "Send msg.escalate_architect on the same refs."
   Probe `test_probe_cap.py` showed `holds escalate: False | text names escalate: True` in answer.
   The pass guarded the same helper, `_escalation_admitted`, at sandbox 2358 and api 23191 and missed this caller. The read listed only the challenge branch of this function.
   Fix: make `_escalation_admitted` return False when `api._holds(ctx, "msg.escalate_architect")` is False, so all 3 callers inherit it.

2. `rota/core/sandbox.py:3486-3488`, the same-refs door. Severity high. CONFIRMED. Outside the points.
   The branch keys on `recipient == "tester"`, so a critic gets the Developer's rung.
   critic/review repeated an answered challenge to the tester. The text said "Send msg.escalate_architect on the same refs, or make one real change to the code the test calls."
   The critic role holds no `msg.escalate_architect` and writes no code. Probe `test_probe_critic.py` showed it.
   Fix: key the branch on `ctx.role == "developer"` and give other senders "Act on the answer, or end the session with no call".

3. `rota/roles/api.py:6432`, `_holds`. Severity low. CONFIRMED.
   When the mode has no `.tools` file, `_holds` returns True for any call. `held_calls` intersects with `sb.functions()`.
   `tick:checkpoint_invalid` is a register entry and keys a mode with no `.tools` file.
   In that wake, developer `ledger.log` with equal halves named `surveys.attest`, which the developer graph lacks. Probe `f349r_p1b.py` showed it.
   For every mode with a `.tools` file, `_holds` equals `held_calls` on the 7 calls (probe `f349r_p1.py`). The first clause, no wake and no mode, is dead code: `ctx.mode` defaults to "normal".
   Fix: when the mode set is None, test the call against the role's graph, as `held_calls` does.

4. `rota/core/sandbox.py:2358-2367` and `4078-4094`. Severity low. CONFIRMED by reading.
   In the no-call branch, place 7 gives "the fix is not yours" and place 8 gives "A third question is the same question". Neither gives a route.
   Place 7 also drops "You escalated these refs already. End the session with no call" for a mode that escalated in an earlier session.
   Fix: give each no-call branch "End the session with no call", which names no call.

5. `rota/roles/api.py:4697-4705`, `surveys_attest`. Severity low. CONFIRMED by reading.
   The guard never fails at runtime. If it failed, the fallback text names `owed_fn`, which is `problem.assert` for the vision keeper.
   The comment says the guard keeps the call out of the text. That is false.
   Fix: drop the guard, or guard the fallback on `_holds(ctx, owed_fn)` and correct the comment.

6. `tests/rota/test_f25_offers_in_mode.py:456`. Severity low. CONFIRMED.
   The place 9 test builds the sandbox with no wake. On the parent it fails only on `api._holds`, so it holds no behaviour that changed.
   The runtime refusal it asserts held before the pass too. It does not cover the escalation branch of finding 1.
   Fix: add the developer/answer cap case of finding 1 as a follower test.

7. Pass report, the 2 "reds gone". Severity low. PLAUSIBLE.
   `test_gate.py` is unchanged since before 676ebde, and the held card test passes on the parent. A run environment at the baseline is the probable cause.
   Five frame 347 liaison commits lie between 676ebde and 106647aa. They are the probable cause for the L3R case. That case skips in this environment.
   Fix: record both as not the pass's doing.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/a9a43280-d634-4af9-9ae0-e50791297894/scratchpad.

- `f349r_p1.py`: built each role and mode with a `.tools` file with a tick wake. It compared `_holds` with `held_calls` on 7 calls. It found no difference. It then built 4 roles in `tick:checkpoint_invalid` and found differences.
- `f349r_p1b.py`: sent `ledger.log` with equal halves in developer checkpoint_invalid and tests_failing.
- `f349r/test_probe_cap.py`: the cap chain of `test_desk_guards` in developer/answer and tests_failing. It also built finding_violated and touch_mistaken with a live wake and sent the challenge.
- `f349r/test_probe_critic.py`: a repeated, answered critic challenge to the tester in critic/review.
- `f349r/parent`: git archive of 106647aa with the commit's test file as `test_f25_new_probe.py`. It ran the 5 follower tests, the held card test and the L3R case.
- At the commit: `test_f33_debts_name_open_frames.py` and `test_f25_offers_in_mode.py`, 69 passed. The held card test passed. The L3R case skipped.

## (d) Usage

About 105k input tokens, about 14k output tokens, about 119k total.
