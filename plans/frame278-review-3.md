Verdict: pass. Review 2's high is closed. 0 high, 1 low (CONFIRMED). Commit 9faedecf, worktree C:/Users/roman/rota_r223.

# Frame 278, review 3: the step asks the same-refs door (9faedecf)

## (a) Verdict on each point

1. The guard: CONFIRMED sound. Without the flag, the recursion is real. The flag resets on an exception. The deleted offers belong only to the discarded ask. One low: the ask leaks facts (finding 1).
2. Review 2's high: CONFIRMED closed. All four cases hold, and the test file passes 15 of 15.

## (b) Findings

1. rota/core/sandbox.py:2162-2174, `_decision_challenge_admitted`. Severity low. CONFIRMED.
   The ask trims `ctx.offers` back to its length before the ask. It does not trim `ctx.facts`.
   The door's `_end_form` (sandbox.py:2379) records a `row` fact during the ask.
   Probe 2, case A: an open decision challenge m150, and a challenge already sent this session.
   `decision_step` returned None and left `facts [('row', 'tst_ver_opt_show_py', '_end_form')]`.
   The outer refusal then carries a fact that its sentence does not quote.
   The fact resolves, so `check_facts` passes it. But `_ON_REFUSAL` (sandbox.py:549, 559) now fires on "offers or facts" for a refusal that had neither.
   Fix: in the `finally`, also take `facts = getattr(ctx, "facts", None)` before the ask and `del facts[kept_facts:]` after it.

Point 1 trace, for the record:
- Path: `decision_step` -> `_decision_challenge_admitted` -> `_same_refs_refusal` (developer, tester, challenge) -> `_challenge_repeat_refusal` -> answered prior at sandbox.py:2487 -> `_escalation_or_step` with `CODE_STEP` -> `decision_step` again.
- Probe 1 replaced the ask with one that sets no flag. `decision_step` on the answered shape raised RecursionError.
- Probe 1 raised KeyError inside the door. After the raise, `_ASKING_DOOR` read False, and an offer appended inside the door was gone. The outer offer stayed.
- The door's admit result does not depend on the flag. `_escalation_or_step` always returns a non-None string, so the nested None from `decision_step` changes only the discarded text.
- Probe 1, case 4: the real refusal on an answered decision challenge kept its own `msg.escalate_architect` offer. The trim uses the length before the ask, so no row of the real refusal is deleted.
- The checkout runs no threads in runner.py or sandbox.py (grep). So the global is safe today.
- A `contextvars.ContextVar` does the same with no module global and is safe under threads. A parameter on `_same_refs_refusal` needs threading through `_challenge_repeat_refusal` and `_escalation_or_step`, three signatures. Fix line, optional: replace `_ASKING_DOOR` with a `ContextVar` and set and reset it with its token.

Point 2 cases:
- Open and unanswered: `test_an_open_decision_challenge_gets_no_offer_of_itself` passes. Probe 2, case B: `_after_these` gave the code step and recorded no offer.
- After a tests receipt: `test_the_offer_returns_after_a_test_receipt` passes. `_moved_since_woken` admits the challenge.
- Night 153 shape: `test_after_these_offers_the_decision_challenge` and `test_the_code_step_becomes_the_challenge_with_the_decision` pass.
- Answered: `test_an_answered_decision_challenge_gets_no_offer_of_itself` and `test_after_these_keeps_the_code_step_once_the_tester_answered` pass.

Outside the points:
2. rota/core/sandbox.py:3110 and 3137, `_bind_send.stage`. Severity low. PLAUSIBLE.
   The step asks only the same-refs door. The stage also runs `_challenge_evidence` and `_red_line_refusal` on a challenge.
   `_challenge_admitted` (sandbox.py:4692) already asks the evidence door and the session door too. The step can offer a challenge that one of those doors refuses. No probe ran on that shape.
   Fix: ask `_challenge_admitted` with the step's own text, or record the residue as a frame.

## (c) Probes

- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b0dce033-321f-4299-b3e0-056d78ea27c8/scratchpad/r3_probe.py: the recursion with no flag, the reset on a raise, the facts on two shapes, and the real refusal's offers.
- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b0dce033-321f-4299-b3e0-056d78ea27c8/scratchpad/r3_probe2.py: an open decision challenge with a challenge sent this session. It ran `decision_step` and `_after_these`.
- `pytest tests/rota/test_frame278_decision_in_thread.py -q` from the worktree: 15 passed. The gate did not run, because no point needs it.

## (d) Usage

Estimate from this context: input about 45k tokens at the peak context, output about 7k tokens, total about 52k. The harness line holds the true count.
