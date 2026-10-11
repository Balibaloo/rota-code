# Frame 200 review of 8d090e2e, passes 2 and 2b, Opus, 2026-10-11

The reviewer's report, from `rv200p2/report.md` under session be3ef742's scratchpad. 152.8k on the harness line against 100k. Probes beside it. Rota workflow.

# Review of 8d090e2e, frame 200, the build loop, passes 2 and 2b

Read-only review. Worktree `C:/Users/roman/rota_rv200` at 8d090e2e. Rota workflow unless marked. All observations 2026-10-11.

## (a) Verdicts

1. The stamp and the once-guard: the guard holds. An unanswered escalation gets 3 wakes (Architect, Vision Keeper, Liaison), then no wakes. `tick_attempt_cap` is never reached. The stamp marks the Developer's designed reply to a Critic challenge unresolved (finding 1).
2. The receipt rule: it counts a decision that answers another message (finding 8, low). It also counts the Architect's own decision as the reply when its answer never lands (finding 2, high).
3. The challenge door: a Tester or a Critic cannot reach it, because the door checks `ctx.role == "developer"`. `END_FORM` names the refused challenge's test ids, which is correct. The refusal text says "no words" also when the Tester's answer has text (finding 9, low).
4. The cause line: no other recorded prompt moves. Only `L1-DV-a-wordless-answer-leaves-a-wrong-test-alone` gets the line. Its 43 cassettes are the only ones in the copy that hold `This answers your`.
5. `_rowless_answer_refusal`: the `findings.find` branch and the `model.amend` branch land only when the answer cites the row written in this session. On nights 138 and 139, 0 of 6 such answers cited it (finding 3). A row written before the escalation counts as added when it is not in the escalation's refs. It does not count when it is in those refs.
6. The two red cases: the seats followed brief lines, not doors. Neither proposed door is safe as worded. The Developer case's one pass is false, and the Architect case's two passes hold the wrong diagnosis (findings 4, 5).
7. The STALE replay: the cassette stores no `done_reason`. A reply cut at the output budget replays as `unterminated argument list`, so the next prompt changes (finding 6).

## (b) Findings

1. **`rota/core/db.py:690-725` and `:848-862`. High. CONFIRMED.** The stamp marks a Critic challenge to the Developer unresolved after the designed reply. `developer/challenge.md` says "You have no message back to Critic". The reply is the next commit or a `ledger.log`. Neither write cites the challenge's criterion. Probe `p1.py` case B shows the result `('unresolved', <note>)`, and `unresolved()` then wakes `('liaison', ('m5',))`. So the challenge goes to the principal's page. Nights 138 and 139 hold 0 such challenges, so the rate is not measured. Fix: leave `critic -> developer` out of `_owes_a_reply`, or count a `code.commit` or a `ledger` write by the addressee as a receipt for that edge.
2. **`rota/core/db.py:702-716`. High. CONFIRMED.** A decision that cites a ref of the escalation is a receipt for every addressee, including the Architect. The Architect has an answer edge to the Developer. Probe `p1.py` case C: the Architect writes `d_1` on `c_1` and sends nothing. The escalation then reads `answered`, and `unresolved()` returns no wake. This is night 127's m72 shape again. The new escalate brief makes it likely: author the decision first, then answer, and the answer can be refused or cut. Fix: count a decision as a receipt only when the graph gives the addressee no `answer` edge to the asker.
3. **`rota/core/sandbox.py:960-990` and `:2817-2824`. Medium. CONFIRMED.** The rowless door refuses the `model.amend` and `findings.find` answers that the escalate brief designs. The brief says "`model.amend`, and say so with `msg.answer_developer`". It never says to cite the amended row. On nights 138 and 139, 6 Architect answers came after `model.amend` or `findings.find` (m85, m92, m94, m101, m241, m156). 0 of 6 cited a new row (probe `q2.py`). Probe `p5.py`, line 1: an amend, then an answer that carries the escalation's refs, is refused. The refusal names `decisions.author`, not the row the session wrote. Fix: when `ctx.writes` holds a row, the refusal offers `msg.answer_developer(refs=[<written ids>])` through `api._offer`.
4. **`tests/rota/cases/l1_answers.yaml:44-145`. Medium. CONFIRMED.** The Developer case reads 1 of 5, and that one pass is false. In run 5 (seq 416171), all three `code.write` calls failed as invalid Python, so the forbidden check found no landed write. Run 2 measured nothing (finding 6). So 0 of 4 measured runs took the branch. In runs 1, 3 and 4 the seat opened with `code.source` and committed. Those runs followed "Read the file with `code.source` first" and "Carrying on means `code.write` and `code.commit`". The fixture's answer carries only the escalation's refs, and the rowless door of this commit now refuses that answer. So the Architect can no longer send the wake this case measures. Fix: re-scope the case to an answer that the door still admits, or retire it. Do not add a Developer door.
5. **`tests/rota/cases/l1_architect.yaml`, new case. Medium. CONFIRMED.** The two passing Architect runs wrote the wrong diagnosis. Run 3 wrote "The test `tst_1bf646` is valid and correctly identifies that the `version_option` decorator does not append the Python version". Run 2 says the same of `tst_a90196`. The case's fault is the test, which calls a plain function. The case checks only that a decision is written and an answer is sent. A Developer that gets this row fits the code, which is s282's failure. Fix: add an expectation on the decision's text, for example that it names the test's call line, or count these runs as red.
6. **`rota/llm/cassettes.py:346-358` and `:392-410`, with `rota/core/runner.py:3506`. Low. CONFIRMED. This defect is older than the frame.** A replayed `Completion` has no `raw`, so `done_reason == "length"` is never true on replay. Live run 2 of the Developer case (14:16:00) had cut replies. Its turn-3 cassette `8329e386e018` holds `cut at the output budget`. On replay, the same completion parses as `unterminated argument list`. A sibling cassette `16db4b6c78b3`, also 13596 characters, holds that text. The 14:39:00 replay hit the error twice, then missed: `no cassette for qwen3:8b key=6e3a826ce9a2`. The first replay already fed turn 1's recorded cassette back without the cut flag. So the live recording at 14:16 already mixed both texts. Fix: store `done_reason` in a cassette column, and return it in `Completion.raw` on replay.
7. **`rota/core/sandbox.py:1478-1482` and `:1510-1514`. Low. PLAUSIBLE.** The cap exemption accepts any `decisions` row in refs, not the decision that the answer carried. A Developer challenge from any mode that cites an unrelated decision skips `LANDED_CHALLENGES`. The ruling of 06:30 says "a challenge whose refs add a decision row". This is PLAUSIBLE because a decision id can reach the Developer's prompt through `rulings_line`. Fix: exempt the challenge only when its decision is a ref of the trigger answer, or when the decision cites the challenged test.
8. **`rota/core/db.py:702-716`. Low. CONFIRMED.** The rule matches by ref overlap, so a decision that answers another message is a receipt. Probe `p1.py` case D: a decision with refs `[c_1, m54]` marks m61 (`[c_1, c_3]`) answered. The decision cites m54, and m54 stays `open`. Fix: when a decision cites a message id, count it as a receipt for that message only.
9. **`rota/core/sandbox.py:950-956`. Low. CONFIRMED by reading.** The refusal says "The answer carries the rows you sent back and no words" in every Developer answer wake. On the two nights, both Tester answers to a Developer challenge carried text (m64 has 143 characters, m137 has 213). Fix: state "no words" only when the trigger's `body_text` is empty.

Point 6, the two proposed doors:

- The Developer door refuses `code.write` when the cause line names the Developer's own challenge or escalation and the answer has no words and no decision ref. It would refuse the write that a `model.amend` answer asks for, because that answer carries a constraint and no decision. 5 of the 8 Architect escalation answers on nights 138 and 139 came after `model.amend`. The rowless door already refuses a wordless Architect answer, so the new door would fire on almost no live wake. Not recommended.
- The Architect door refuses `msg.challenge_vision_keeper` when the escalation's refs hold a test and no constraint. It would refuse 3 of 3 such challenges on nights 138 and 139 (m61, m83, m139). m139 is night 139's c2, where frame 202 names a criterion defect. For that case the Vision Keeper challenge is the designed route, "the criteria do not mean what everyone assumed". Not recommended.
- A better site exists for the Architect. Failing runs 1 and 5 met the `findings.find` refusal ("is a row of criteria, not a constraint") in the turn before the challenge. That refusal already refuses the call. Let it offer `decisions.author` with the test id, then `msg.answer_developer`. That change refuses no new call. Run 4 skipped `findings.find`, so it covers 2 of 3 failing runs.

Outside the points:

- Outside. The commit body says the Developer case reads "1 of 5". The measured value is 1 of 4, and that one pass is false (finding 4).

## (c) Probes

All probes are in the scratchpad directory `rv200p2/` of session be3ef742. They ran from the worktree with `PYTHONPATH` set to the worktree.

- `p1.py`: fresh `init_db`, then `session_commit` and `unresolved()`. Case A: the ladder, 3 wakes. Case B: the Critic challenge. Case C: the Architect decision and no answer. Case D: the receipt by overlap.
- `p5.py`: `_rowless_answer_refusal` on a stub ctx, six shapes.
- `q1.py`, `q2.py`: read-only queries on copies of `n138p5.db` and `n139p5.db`. `q1.py` lists the owed messages and their sessions. `q2.py` lists the new refs in the Architect's answers.
- `q3.py`, `q4.py` and inline queries on `cass.db`: a copy of `D:/repos/rota/tests/rota/cassettes.db`, taken 14:39. They read the case runs, the transcripts (`run2_first.txt`, `run2_rec.txt`) and the cassette prompts of the Developer case.
- No pytest run, no gate run, no model call.

## (d) Usage

About 125k input tokens, about 14k output tokens, about 139k in total, against a cap of 100k. These are estimates from the context counter, not the harness line.

One more pass: 2 high, 3 medium, 4 low.
