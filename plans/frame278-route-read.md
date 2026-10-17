# Frame 278, the route read: where an Architect's finding about a test goes

Rota workflow throughout. Read-only on the checkout at d2b7fe12, 2026-10-17. Databases opened `mode=ro`.

## 1. Verdict

A route exists today, and Roman ruled it on 2026-10-11 06:30. The route is not new, so frame 278 does not escalate. The Architect writes a decision row and answers the Developer. The Developer's answer mode relays the row to the Tester by `msg.challenge_tester` with the decision id in refs. The Tester then wakes in challenge mode (observed: briefs, tools files and night databases below, 2026-10-17). On night 153 the route existed and the Developer seat did not take it. So the wall is not cause 10. It is a seat that had the fact and did not act on it, plus a thread view that hides the decision from the later Developer wakes (reasoned: sections 4 and 5).

## 2. The route today

| Step | Seat | Row or wake | Evidence |
|---|---|---|---|
| 1 | Developer | `msg.escalate_architect` from `tests_failing` | m143 on night 153 (observed: `clickI_night153.db` messages) |
| 2 | Architect, mode `escalate` | `decisions.author`, then `msg.answer_developer`. The tools hold no `msg.*_tester` call | `rota/roles/prompts/architect/escalate.tools` (observed) |
| 3 | Developer, mode `answer` | wake on the answer. The wake resolves the decision ref to its text with `"table": "decisions"` | s278 prompt, `resolved_refs.dec_1_tst_ver_opt_show_py` (observed) |
| 4 | Developer, mode `answer` | `answer.tools` holds `msg.challenge_tester`. `answer.md` says: "If the answer is a decision row that says the test does not encode the criterion, send `msg.challenge_tester` with that row's id in refs" | `rota/roles/prompts/developer/answer.md:19-21` (observed). s278's system text held the sentence (observed) |
| 5 | Tester, mode `challenge` | `message_tips` wakes the Tester on the open challenge | `rota/core/predicates.py:179`, `open_tips` (observed) |

No Tester wake fires on a `decisions` row or on an `msg.answer_developer` that names a test. The Tester's wakes are `tests_missing` (`predicates.py:755`) and the messages addressed to it. Those are challenges from the Developer and the Critic, and answers from the Terminologist, the Vision Keeper and the Researcher (observed: the `.tools` files that hold `msg.challenge_tester` and `msg.answer_tester`, 2026-10-17). The Architect has no edge to the Tester in any mode (observed: grep of `rota/roles/prompts/*/*.tools`, 2026-10-17).

## 3. The records

- Roman's ruling, verbatim from `plans/archive/stack-2026-10-13.md`, frame 200, status 2026-10-11 06:30: "**Roman ruled at 2026-10-11 06:30 on change 4's route, the recommended option of three by `AskUserQuestion`: the Developer's answer mode gains `msg.challenge_tester`, and a challenge whose refs add a decision row does not count against the per-criterion cap; no new edge** (ruled: Roman, 2026-10-11)."
- The gap the ruling closed, `plans/frame200-design-review.md` section 4, 2026-10-11: "The row about a test reaches no seat that can change the test. `graph.json` has no `architect -> tester` edge." And: "The cheapest route is a challenge that carries the row's ref."
- The build: commit 8d090e2e, 2026-10-11, "the Developer's answer wake shows the cause it answers, shows a decision row's text, and may challenge the Tester only with a decision ref".
- Law 2, `rota/LAWS.md:112-116`: "The reasoning is written into the decision record by whoever decided, and reached by following a ref." Law 3 derives every message edge from read and write edges. So a direct Architect to Tester edge is a composition change (reasoned: `LAWS.md:121-147`).
- Frame 115, status 2026-10-04 14:38: the row route is "a build frame inside law 2" (observed: `plans/stack.md:1722`).
- `git log -S "answer_tester"` and `git log -S "escalate_architect"` show only the commits that made the tools: 6afbbad1, fdad09df, 7da68101, ebc9bafd, ead29c49. None holds a ruling on an Architect to Tester edge (observed, 2026-10-17).
- Frames 114 and 212 name other routes: a failing inherited test, and the Architect's route of an escalation (observed: `plans/stack.md:1627`, `1084`).

## 4. Night 153, what happened

1. s278 woke on m144 in answer mode. Its prompt held the branch sentence and the decision row's text. It made 3 reads, wrote one sentence of prose that blamed the code, and ended with no call (observed: `turns` and `tool_calls` of s278).
2. s283, s285 and s286 woke on `tick:tests_failing`. The thread view listed m143 as `"answered with no words"` (observed: s283 turn 3 prompt). `runner.py:2982` writes that text when the answer message has no `body_text`, and does not read the answer's decision refs (observed: `rota/core/runner.py:2972-2990`). So these wakes never saw `dec_1`.
3. s283 sent `msg.challenge_tester` with refs `['ver_opt_show_py', 'tst_ver_opt_show_py']`, without the decision id. The same-refs door refused it. The "after these" text said "Make one real change to the code the test calls" (observed: s283 turns 3 and 11, `runner.py:3218-3221`). A challenge with `dec_1` in refs adds a decision row, which Roman ruled does not count against the cap (reasoned: the ruling above, not run).

## 5. The count, nights 140 to 153

Architect decisions with "not encode" in the text: 11, on nights 142 (2), 144 (2), 145, 146, 147 (2), 148, 151 and 153. No Architect decision or message said "is wrong" or "cannot pass" (observed: `scratchpad/f278/count.py` to `count4.py` of session b0dce033, 2026-10-17).

| Night | Decision | Developer wake | Challenge with the decision ref landed | Tester on it called `tests.encode` | Code calls before the relay |
|---|---|---|---|---|---|
| 142 | dec_1_test_does_not_encode_criterion | s398, 1 turn | no | - | 0 |
| 142 | did_escalation | s551 | m389 | s552 yes | 0 |
| 144 | d_001 | s256 | m158 | s257 yes | 3 |
| 144 | dec_1 | s557 | m390 | s558 yes | 0 |
| 145 | dec_1_tst_version_flag_true | s386 | m223 | s387 yes | 5 |
| 146 | dec_001 | s282 | m152 | s283 yes | 2 |
| 147 | dec_001 | s158, 15 turns | no, 4 attempts refused, the first for a missing criterion ref | - | 9 |
| 147 | dec_1_tst_confirm_eof_default | s241, 1 turn | no | - | 0 |
| 148 | dec_1_confirm_default_on_eof | s160 | m58 | s161 yes | 0 |
| 151 | dec_1_tst_confirm_eof | s238 | m116 | s239 yes | 4 |
| 153 | dec_1_tst_ver_opt_show_py | s278, 1 turn | no | - | 0 |

- The relay landed 7 of 11. The Tester woke and called `tests.encode` 7 of 7. This read did not check whether each encode landed or turned the test green (observed: tool names only).
- The relay did not land 4 of 11. Three are one-turn answer wakes that ended in prose: s398, s241 and s278. One is s158, whose challenges were refused.
- The Developer edited the code after the finding in 7 of 11 cases. In the woken session before the relay: 5 of 11. In the same batch after a failed relay: 2 of 4, night 147 bg_2 (s263, s268) and night 153 bg_3 (s283, s285, s286) (observed: sessions with `code.write` or `code.commit` whose `wake_refs` name the test's batch).
- The baseline for frame 278's ratio: failed relays 4 of 11 over the fourteen nights, 1 of 1 on night 153 (observed).

## 6. The recommended answer

No question goes to Roman. The route exists, and Roman ruled it at 2026-10-11 06:30 (ruled: frame 200, archive). Place the wall again, from cause 10 to a seat that had the fact and did not act, plus a view that hides the fact (reasoned: sections 4 and 5). Two cheap fixes, in order:

1. The thread view. When an answer has no words and its refs hold a `decisions` row, show the row's id and text in place of "answered with no words". When that row is the Architect's and names the red test, the "after these" step offers `msg.challenge_tester` with the criterion, the test and the decision id. The offer replaces "Make one real change to the code the test calls". Site: `rota/core/runner.py:2972-2990` and `3212-3221`. Count: on night 153 it fires on 3 of 3 later Developer wakes on bg_3. Over nights 140 to 153 it can reach only the 4 failed relays. It refuses 0 right calls, because the one call it offers is the ruled route (reasoned: not run). What overfits: an offer keyed on the words "does not encode". Key it on the table, the author and the test ref, not on the text.
2. The answer wake that ends in one turn of prose, 3 of 11. By the rule of 2026-10-02 the seat is interviewed in its context before a second brief shape. Replay s278 with `probes/frame37/interview_turn.py --seq <s278's turn>`, and ask what it read in the branch sentence. Decide the fix from what it says.

The ends-when for the night, in three parts. The mechanism: fix 1 in the `tests_failing` wake. The ratio: failed relays after an Architect finding on a test, from 4 of 11 toward 1 of the next 3. The residue: a session that still shows the sign is read, and a cause other than the hidden decision or the unrelayed answer is a new frame.
