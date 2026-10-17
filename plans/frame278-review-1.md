# Frame 278, review 1 of 5cbef762 (parent 96e275dc)

Verdict: one high defect. The new step can offer the same challenge that the door refuses. The other four points hold, with three low findings.

Worktree: C:/Users/roman/rota_r223 at 5cbef762. Read-only review on Opus, 2026-10-17.

## (a) Verdict on each point

1. Point 1 holds for the night 153 shape. The asker's own reason row stays out, but a Developer row from another message shows (finding 3, low).
2. Point 2 holds. The key is the table, `author = 'architect'` and the test in the decision's refs. Neither probe case gets the new step.
3. Point 3 holds for the night 153 refs. A challenge on other refs than the escalation still gets the escalation offer again (finding 2, low).
4. Point 4 holds. No other refusal text and no other thread entry changes. The 436 existing tests pass.
5. Point 5 holds in part. Test 1 is red at the parent for the pass's reason. Four tests are red by a missing name only, and no test covers "after these".

## (b) Findings

1. `rota/core/sandbox.py:2303` and `rota/core/runner.py:3417`. Severity high. CONFIRMED.
   The Developer sends the decision challenge `[crit, test, dec]` (m150), and the Tester answers it (m151). The Developer then sends the same challenge again.
   The same-refs door refuses it with "they answered (m151)". With the escalation closed on those refs, the step then offers `msg.challenge_tester(refs=['ver_opt_show_py', 'tst_ver_opt_show_py', 'dec_1_tst_ver_opt_show_py'], ...)`. That is the exact call that the door refused.
   This breaks frame 135's law: a refusal names only a call that the doors admit. The seat can loop on this refusal. The runner's "after these" text offers the same call after m151, because `architect_decision_on` does not read whether the decision challenge was already sent and answered.
   Fix: give the new step only when no challenge from the role on the offered refs, compared as a set, has an answer from the Tester. Otherwise keep `CODE_STEP`. Apply the same check in the runner.
2. `rota/core/sandbox.py:2294`. Severity low. CONFIRMED.
   Prior escalation m143 is on `[crit, test]`, and the Architect answered it with the decision. A challenge on `[test]` alone is refused, and the step offers `msg.escalate_architect on the same refs`. The Architect has already decided on that test.
   A challenge on `[crit, test]` or `[test, crit]` gets the new step, as night 153's s283 would. So the night 153 refs are covered, and a variant of its refs is not.
   Fix: in `_escalation_or_step`, test `architect_decision_on` before the escalation offer when the role is the Developer. A decision on a test of the refs then comes before a second escalation.
3. `rota/core/runner.py:3020` (`_decisions_in`). Severity low. CONFIRMED.
   An answer whose refs add `d_dev`, a Developer decision from another message, shows `{'id': 'd_dev', 'author': 'developer', ...}` as the answer. The set difference removes only the reason rows in the asker's own refs. It does not remove the asker's rows by author.
   Fix: exclude rows where `author` is the asker's role (`m.from_role`), as `_without_own_reasons` does.
4. `tests/rota/test_frame278_decision_in_thread.py`. Severity low. CONFIRMED.
   At the parent, 6 of 7 tests fail. Only test 1 fails on its assert ("answered with no words" against the decision row). Tests 3 to 6 fail on `AttributeError` for the new names, so they do not show the old behaviour. The runner's "after these" branch has no test, and finding 1 is in that branch. The implementer states this gap.
   Fix: add a `push_working_set` or helper-level test for "after these", and a test for the answered decision challenge of finding 1.

Outside the points:

5. `rota/core/runner.py:3417`. Severity low. PLAUSIBLE.
   The runner branch has no `role == "developer"` guard, but the sandbox branch has one. `architect_decision_on` finds rows only for the role's own messages, so a Tester wake finds a decision only on its own escalations. Also, neither branch excludes a decision that a later decision supersedes.
   Fix: add the Developer guard in the runner, and skip decisions that another row's `supersedes` names.

## Point 1, the view shows only the rows that an answer adds

`_decisions_in` takes the answer's refs minus the question's refs, and keeps the `decisions` rows. The binder adds the sender's reason row to the stored refs (`_without_own_reasons`, frame 200 pass 5). So the echo of the asker's own reason row is removed, and test 2 covers that echo. Probe P1: an answer that adds a Developer row not in m143's refs shows that row as the answer's (finding 3).

## Point 2, the key

Probes P2: an Architect decision with refs `["other_test"]` gives "fact. Make one real change to the code the test calls.". A Developer decision on the red test gives the same text. A decision with empty refs gives None, so the words are never a key. The query reads the table, the author and the test id only.

## Point 3, the order

The order in `_escalation_or_step` is the escalation offer, then `END_STEP`, then the new step. `_escalation_admitted` refuses any prior Developer escalation on the same refs, compared as a sorted list. Probe P3 with the real doors and m143 on `[crit, test]`:
- refs `[crit, test]`: the new step.
- refs `[test, crit]`: the new step.
- refs `[test]`: "Send msg.escalate_architect on the same refs." (finding 2).
So s283's challenge gets the new step. The 19 of 30 count holds the cases where the escalation offer comes first. Finding 2 owes those cases a fix line.

## Point 4, nothing else moves

In the diff, the only changed outputs are on two paths. The first is the empty-text answer with a decision row that the answer adds. The second is the step when `architect_decision_on` finds a row. `CODE_STEP` keeps the old text exactly. Everywhere else, the "after these" text and `_thread_on_tests` give the same strings as before. At 5cbef762, `test_desk_guards.py`, `test_night46_context.py`, `test_revert_door.py` and `test_end_step_nudge.py` gave 436 passed. I did not run the full gate.

## Point 5, the red test

At the parent copy, the new file gave "6 failed, 1 passed". Test 1 failed on the pass's reason. Test 2 passed, and it guards the echo. Tests 3 to 6 failed on `AttributeError: module 'rota.core.sandbox' has no attribute 'CODE_STEP'` and on the missing helpers. At 5cbef762 the file gave 7 passed. No test covers the runner's "after these" branch (finding 4).

## (c) Probes

All probes are under C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b0dce033-321f-4299-b3e0-056d78ea27c8/scratchpad/r278/.
- `p1.py`: P1, the Developer row that an answer adds. P2, the key cases. P3, the real escalation door on three ref lists. All use the test file's `_night153` rows.
- `p2.py`: the decision challenge m150 with the Tester's answer m151, then the same challenge again. The escalation was admitted, so the step offered the escalation.
- `p3.py`: p2 plus a closed escalation m152 on the same refs. The refusal offered the call that it refused (finding 1).
- `parent/`: `git archive 96e275dc rota tests pyproject.toml` with the new test file copied in. Pytest ran the new file on the parent code. The import path was checked.
- At the worktree: the new file (7 passed), and the four existing files (436 passed in 101.78s).

## (d) Usage

Input tokens about 60k. Output tokens about 9k. Total about 69k. These are my estimates, and the harness line is the record.
