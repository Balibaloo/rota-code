# Review of frame 349, commit b4801fa1 on rota/foundation, pass 2

Verdict: not ready to close, and one line short. Pass 2 fixes all six findings of review p1, and each fix holds under a probe. One high finding remains outside the points. The place 8 block that pass 2 rewrote still names `schedule.unresolved` in its last branch. No op of that name exists, and four roles meet the text. Counts: 1 high, 3 low.

Worktree: C:/Users/roman/rota_f349b at b4801fa1, parent 81b85d3d. Pass 1 tree: the scratchpad copy `f349r2/p1tree` (git archive of 81b85d3d, no worktree).

## (a) Verdicts on the points

1. Yes. With no `.tools` file, `_holds` reads `ctx.working_set`. `sandbox.build` sets it at sandbox.py 833 from `grouped`, and `sb.functions()` reads `_available`, which `build` fills from the same `grouped`. The p1b probe now gives "names attest: False" in checkpoint_invalid and tests_failing. The p1 probe shows no divergence.
2. developer/answer at the cap now gets "Make one real change to the code the test calls." The mode holds `code.write`. `_code_step` gives the end after a challenge in the session. No caller sends a seat to a step it cannot take. Place 7 gives "End the session with no call".
3. Yes for the critic: "Act on the answer, or end the session with no call." developer/tests_failing keeps its text byte for byte, but the text is not the rung. The developer's only verb to the tester is `challenge`, and it returns at sandbox.py 3399 before the rung. So the rung's developer branch is dead (F3). tests_failing gets "Send msg.escalate_architect on the same refs." from `_escalation_or_step`, as at 81b85d3d.
4. Not weakened. The test still pins the critic's whole refusal to the byte. Only the step changed, and that change is finding 2 of p1. The fact sentence and "Do not send this challenge again." are unchanged.
5. The lint passes: `test_f25_offers_in_mode.py` and `test_desk_guards.py` give 429 passed. Outside the 11 known places, 5 sites name `msg.challenge_tester` to a mode that lacks it. No site names `msg.escalate_architect` to such a mode. All 5 are bare names with no parenthesis, so the lint cannot see them (F4). Count: 5.
6. Confirmed. At 81b85d3d both new tests fail on the old text. At b4801fa1 both pass.

## (b) Findings

1. `rota/core/sandbox.py:4096-4097`, place 8, the `else` branch. Severity high. CONFIRMED. Outside the points.
   A third question on answered rows from the architect, the developer, the terminologist or the vision keeper gets "The exit is schedule.unresolved".
   `api.REGISTRY` holds no `schedule.unresolved`. The op was renamed to `schedule.reask` (api.py 17290).
   Probe `f349r2/test_probe_third_q.py` showed the text for all 4 roles, and `("schedule", "unresolved") in api.REGISTRY` is False.
   The lint misses the text twice: the name has no parenthesis, and `lint.exists` drops an op that does not exist.
   Fix: name `schedule.reask(what_is_missing=...)` under `api._holds(ctx, "schedule.reask")`, else "end the session with no call".

2. `rota/roles/api.py:23202-23203`, the comment in `_revert_refusal`. Severity low. CONFIRMED by reading.
   The comment says that `_escalation_admitted` reads the repeat doors and not the mode. Since pass 2 it reads the mode first.
   The pass report says the `_holds` test stays only for the lint.
   Fix: say that the lint reads the literal guard, and that `_escalation_admitted` also asks the mode.

3. `rota/core/sandbox.py:3493-3496`, the same-refs rung. Severity low. CONFIRMED.
   The graph gives the developer one verb to the tester, `challenge`. That verb returns at sandbox.py 3399 through `_challenge_repeat_refusal`.
   So `ctx.role == "developer" and recipient == "tester"` is never true here, and the escalation rung text is dead.
   The senders that reach the rung are the critic (challenge) and the answerers of the tester. All get "Act on the answer".
   Fix: drop the developer branch and keep the one sentence, or record the branch as dead in its comment.

4. `rota/roles/api.py:15924`, `15930`, `16025` with `16034`, `22387` and `22516`. Severity low. CONFIRMED for 3, by reading for 2. Outside the 11 known places.
   critic/answer holds `verdicts.emit` and `verdicts.claim_encodes` and lacks `msg.challenge_tester`.
   Probe `f349r2/test_probe_critic_answer.py` showed the `verdicts.emit` refusal and the `claim_encodes(False)` note name `msg.challenge_tester`. The reversal text at 15924 is the same function.
   `_code_write` names `msg.challenge_tester` for a test file (22387) and for a stdin call (22516). developer batch_start, challenge, finding_violated, touch_mistaken and verdict_failed hold `code.write` and lack the challenge.
   The read of frame 349 put the bare-name tier in a separate frame. These 5 sites are part of that reach.
   Fix: guard each text on `_holds(ctx, "msg.challenge_tester")` in the bare-name frame, and give the fact alone where it is false.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/a9a43280-d634-4af9-9ae0-e50791297894/scratchpad. Each ran from the worktree root with `PYTHONPATH` set to the tree under test.

- `f349r_p1.py` at b4801fa1: no divergence between `_holds` and `held_calls` in any mode with a `.tools` file, and none in `tick:checkpoint_invalid` for 4 roles.
- `f349r_p1b.py` at b4801fa1: developer `ledger.log` with equal halves in checkpoint_invalid and tests_failing. The text names no `surveys.attest`.
- `f349r/test_probe_critic.py` and `f349r/test_probe_cap.py` at b4801fa1: the critic text, the answer and tests_failing cap texts, and the NotInWorkingSet refusals of finding_violated and touch_mistaken.
- `f349r2/p1tree`: git archive of 81b85d3d with the commit's test file as `test_f25_new_probe.py`. The two new tests failed on the old texts.
- `f349r2/test_probe_third_q.py`: a third question from 4 roles on rows answered twice.
- `f349r2/test_probe_critic_answer.py`: critic/answer with a tick wake sends a fail verdict with no claim, then claims False.
- At b4801fa1: `test_f25_offers_in_mode.py` and `test_desk_guards.py`, 429 passed. The gate did not run, because no point needed it.

## (d) Usage

About 80k input tokens, about 10k output tokens, about 90k total.
