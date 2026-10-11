# Frame 200, review 2e: two challenge doors contradict on the Developer's answer path

Verdict: PASS 2E NEEDED. Door 1 tells the Developer to drop the decision row. Door 2 then refuses that exact shape and ends the session. The challenge that design 200 change 4 wants never lands, and the case passes on the silent end.

Worktree `C:/Users/roman/rota_rv200e` at 8558e96c, read-only. No model was called.

## (a) Verdicts

1. Door 1 is `_challenge_evidence`, `rota/core/sandbox.py:1094-1105`. Door 2 is `_answer_mode_challenge_refusal`, `rota/core/sandbox.py:958-961`. The verb guard calls door 2 at line 2364, before door 1 at line 2368.
2. Yes. `refs=[c1, tst1, d1]` passes both doors on the case's fixture, in either order. CONFIRMED.
3. Door 2 reads the challenge's refs, not the answer's refs. `<d1>` is in `decisions`, and the check looks there. CONFIRMED.
4. Yes. Door 1's hint is `[c, tst]`, and door 2 refuses `[c, tst]` with an EndRefusal. This is frame 194's shape on a new pair. CONFIRMED.
5. No Tester wake follows. The only ready wake is the Developer's `tick:tests_failing` on the same batch, with the same red test. CONFIRMED on the frontier.
6. Fix: door 2 offers the trigger's decision row instead of an end, and door 1's hint adds that row. One door test proves it. About 150k tokens, one pass with one re-record.

## (b) Findings

1. `rota/core/sandbox.py:1094-1096`. High. CONFIRMED by probe 2, rows 1 and 2. In an answer wake, door 1's hint `send refs=['c', 'tst']` drops the decision row that the trigger carries. Door 2 then refuses the hinted shape.
   Fix: when the trigger is an answer whose `body_refs` hold a `decisions` row, append that row to each hinted refs list.
2. `rota/core/sandbox.py:951-961`. High. CONFIRMED by probe 2, row 2. Door 2 ends the session when the challenge lacks a decision row, even when the trigger holds one. The session can never retry with the right refs.
   Fix: when the trigger's `body_refs` hold a decision row, return a plain refusal through `api._offer` with `refs=[...refs, d]`, not an `_Ending`.
3. `rota/core/sandbox.py:956-959`. Low. CONFIRMED by probe 2, row 2. The text says "no ref of this answer" and "The answer carries the rows you sent back and no words". The refs that door 2 reads are the challenge's refs. The answer in this fixture added `<d1>`, a row the Developer did not send. Both sentences are false here.
   Fix: say "no ref of this challenge is a decision row", and say "the rows you sent back" only when the trigger holds no decision row.
4. Outside the points. `tests/rota/cases/l1_answers.yaml:161-166`. Low. CONFIRMED by the brief's transcript read and by probe 2. `expect.messages: []` admits the silent end, so the case passes 5/5 while the challenge never lands. The suite cannot see findings 1 and 2.
   Fix: after the door fix, expect one `challenge` to the tester whose refs hold `<d1>`, or pin the three-ref route in a door test.
5. Outside the points. `rota/core/predicates.py:900-931` with `rota/core/loop.py:303-323`. Low. PLAUSIBLE on a night, because no night was replayed. `note_dispatch` counts the re-fired `tick:tests_failing` key (`rota/core/scheduler.py:2089-2106`). With no new test run, `attempt` stays 1, so only the tick quarantine bounds the loop. Each wake shows the Developer the same red test and a decision it cannot route.
   Fix: none separate. The fixes of findings 1 and 2 remove the cause.

## Point 1: which door writes each refusal

- Refusal 1, "a challenge to the tester names both sides of the conflict ... yours names no criterion. The failing tests of this batch: send refs=[...]": `_challenge_evidence`, `rota/core/sandbox.py:1013`. Lines 1093-1096 build the hint from the failing `test_runs` of the batch. Lines 1102-1105 raise it.
- Refusal 2, "no ref of this answer is a decision row ...": `_answer_mode_challenge_refusal`, `rota/core/sandbox.py:935`. The predicate is `_holds_decision(ctx.conn, refs)` at line 951, defined at lines 1509-1513. The text is at lines 956-961. `_end_form` writes "Nothing more is owed ... in this session." (line 1380).
- The order in the verb guard is door 2 at lines 2363-2366, then door 1 at lines 2367-2368. So `refs=[d1]` passes door 2 and dies on door 1. `refs=[c, tst]` dies on door 2 first.

## Point 2: three refs on the case's fixture

Probe 2 built the scene with `fixtures.load_case`, `fixtures.seed`, `fixtures.seed_inbound` and `fixtures.wake_for`. It built the sandbox with `runner.session_sandbox`, the path `run_case` takes, so `ctx.trigger` is the inbound answer `m_in`. The quotes were spans of `<c1>` and `<tst1>`. Output, verbatim:

```
ids c_230e19 tst_12b03e d_fdd7fe inbound m_in ('answer', '["c_230e19", "tst_12b03e", "d_fdd7fe"]', None)
mode normal trigger m_in
['d_fdd7fe'] REFUSED ValueError a challenge to the tester names both sides of the conflict in refs -- the criterion and the test -- and yours names no criterion. The failing tests of this batch: send refs=['c_230e19', 'tst_12b03e']
mode normal trigger m_in
['c_230e19', 'tst_12b03e'] REFUSED EndRefusal no ref of this answer is a decision row. The answer carries the rows you sent back and no words. If you still read the test as wrong, say so in one sentence and end. End the session with no call. Your whole next reply is this one line, and no TOOL: line: Nothing more is owed on tst_12b03e in this session.
mode normal trigger m_in
['c_230e19', 'tst_12b03e', 'd_fdd7fe'] LANDED {'id': 'm1', 'to': 'tester', 'verb': 'challenge'}
mode normal trigger m_in
['d_fdd7fe', 'c_230e19', 'tst_12b03e'] LANDED {'id': 'm1', 'to': 'tester', 'verb': 'challenge'}
```

Rows 1 and 2 reproduce the five recorded runs. Rows 3 and 4 show that the right challenge lands. `_same_refs_refusal` at line 2385 did not fire, because no prior challenge exists.

Probe 1 built the sandbox with `sandbox.build` alone. That left `ctx.trigger` None, so door 2 did not apply and `[c, tst]` landed. Probe 1 is not the production path. `runner.session_sandbox` sets the trigger at `rota/core/runner.py:3226`.

## Point 3: which refs door 2 reads

Door 2 reads the challenge's `refs` at line 951. It reads the trigger row only for `verb` and `body_text` (lines 947-950). The fixture writes `<d1>` to `decisions` (yaml lines 154-160). Probe 2 read it back from `decisions` as `d_fdd7fe`. So door 2 sees `<d1>` when the challenge carries it, as rows 3 and 4 show. The refusal fires only because the Developer obeyed door 1 and dropped `<d1>`. The word "answer" in the text names the wrong message (finding 3).

## Point 4: do the two doors contradict

Yes. Door 1's hint at lines 1094-1096 lists only `criterion_id` and `test_id` of the failing tests. It never reads the trigger. Door 2 requires a `decisions` row in the same refs. The hinted call `refs=['c_230e19', 'tst_12b03e']` is the exact call that door 2 refuses, as probe 2 rows 1 and 2 show. Door 2 then ends the session, so no third call can repair the refs. This is frame 194's shape: the repair text of one door is the refusal of the other door.

## Point 5: what follows the end with no call on a night

1. The session ends on the `EndRefusal` with no write and no message. `loop.step` sets `productive` False, because `res.writes` and `res.messages` are empty (`rota/core/loop.py:328-330`). `cascade_wakes` at line 337 has no message to cascade.
2. No predicate wakes the Tester. The Tester's tick predicate is `tests_missing` (`rota/core/predicates.py:755`), and it does not fire on a batch that has tests. A Tester reaches a challenge only through a message, and none exists.
3. `tests_failing` (`rota/core/predicates.py:900-931`) fires again for the Developer. The batch is `running`, and the latest run of `<tst1>` is `fail`. `attempt` comes from `MAX(test_runs.attempt)`. No harness run raises it, so it stays below `loop_cap` 10.
4. `loop.step` counts the tick in `note_dispatch` (`rota/core/loop.py:303`) and runs the Developer again on the same red test (lines 320-323).

Probe 3 seeded the case's fixture without the inbound answer, which stands for the answer once consumed. It then ran `scheduler.frontier`. Output, verbatim:

```
loop_cap 10
frontier with the answer consumed (not seeded):
   developer tick:tests_failing ('b_0319fd',) attempt 1
```

So the batch goes to the Developer's next attempt with the same red test. The next wake is a tick, not an answer wake, so door 2 does not apply there. Door 1 still gives the two-ref hint, and a two-ref challenge then lands without the decision row. Whether the seat sends that challenge on a tick wake is a night question (PLAUSIBLE).

## Point 6: the fix line

Fix: in `_answer_mode_challenge_refusal`, when the trigger answer's `body_refs` hold a `decisions` row, return an `api._offer` refusal, not an `_Ending`, that names `msg.challenge_tester` with `refs=[c, tst, d]`. In the batch hint of `_challenge_evidence`, append the same decision id when the trigger is such an answer.

Proof: one door test in `tests/rota/test_desk_guards.py` on this case's scene, built through `runner.session_sandbox`. The test asserts three things:

- `refs=[d]` gives a hint that names all three ids.
- `refs=[c, tst]` raises a plain refusal that names `d`.
- `refs=[c, tst, d]` lands.

Then re-record `L1-DV-a-wordless-answer-leaves-a-wrong-test-alone`, with `expect.messages` holding one challenge to the tester.

Price for an implementer: about 150k tokens in one pass. The pass holds two door edits, one door test, one case re-record of five runs and one gate run. Cycles: 2, the pass and its review.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/59bdd13a-98f3-4dda-ba43-071cb487b114/scratchpad/rv200e/`.

- `probe_doors.py`: probe 1. It runs the four refs shapes through `sandbox.build`, with no trigger set. It is the control, not the production path.
- `probe_doors2.py`: probe 2. It runs the same four shapes through `runner.session_sandbox`. The output is under point 2.
- `probe_frontier.py`: probe 3. It runs `scheduler.frontier` on the case's fixture without the inbound answer. The output is under point 5.
- Each probe ran from the worktree root as `PYTHONPATH=C:/Users/roman/rota_rv200e ROTA_MODEL=qwen3:8b D:/repos/rota/.venv/Scripts/python.exe <probe>`. Each used a temporary database and called no model.
- No pytest run and no gate run. No point needed the suite.

## (d) Usage

The reviewer cannot read the harness count. Estimate: about 80k input tokens and 12k output tokens, about 92k in all. Read the true count from the harness line.
