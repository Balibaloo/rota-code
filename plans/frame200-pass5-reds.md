# Frame 200, pass 5: the three cases the re-record left red

Read by an Opus agent, 2026-10-12 18:29, on a backup copy of
`tests/rota/cassettes.db` at
`C:\Users\roman\AppData\Local\Temp\claude\d--repos-rota\d609cf11-e3b0-446b-b02a-29ab3633c919\scratchpad\reds5\cassettes.db`.
This is about the rota workflow, the Developer seat. No pass 5 door refused a
call in any failing run. The reason door admitted every reasoned challenge.

## 1. `L2-DV-name-the-deferred-batch-not-the-running-one`: FAIL 0/1

The cause is the seat, moved by pass 5's tool signature line. No door is
involved (observed: case_runs seq 433635, 433636 and 433657, 2026-10-12
18:07 to 18:25).

- The prompt hash did not move, `eb20a04e985c6de7`. The system hash moved
  from `064f1d996830a645` to `bb9a5f798916d974`, and the load moved from
  `qwen3:8b@248863` to `qwen3:8b@248864`.
- The system diff between the two first-turn cassettes (rowid 52882 old,
  53946 new) is one line, and the user text is identical:
  `-  TOOL: msg.challenge_tester(refs, quotes, round_no=0)` /
  `+  TOOL: msg.challenge_tester(refs, quotes, reason=None, round_no=0)`.
- Problem: `none of the permitted answers was given; wrote ['ledger'], sent [('vision_keeper', 'question')]`.
- The seat called the right role. The old run sent
  `msg.question_vision_keeper(refs=["b_db76fa"], ...)`, the deferred batch.
  The new run sent `refs=["c_c7f366"]`, the criterion. The case needs
  `refs_include: [<b1>]`, so the criterion ref fails.
- The last two turns: the say repeats `msg.question_vision_keeper(refs=["c_c7f366"], ...)`.
  The errors are older doors only: `ledger.log: 'c_c7f366' is a row of criteria, not of criterion. ...`,
  four times `msg.question_vision_keeper: you have already sent question to vision_keeper; saying it again with different refs is a second answer to one question, and the recipient has to reconcile them. Your work here is done`,
  and `msg.question_vision_keeper was refused the same way in four turns; the session ended on it`.
- `exhausted.md` names no ref for the three question rungs. It names refs for
  the challenge rung only. The case's 1/1 was one sample on one system text.

Is it pass 5's: pass 5's code moved the system text by one tool line. Pass 5's
doors and brief sentence did not cause it. The seat's ref choice is the cause.

Fix line: re-record once at a new load. If it stays red, add one sentence to
`rota/roles/prompts/developer/exhausted.md`: "Put this batch's id in `refs` of
the message you send." That sentence is a brief change and its own frame.

## 2. `ACT-DV-edit-inside-the-function`: FAIL 3/5, needs 4

The cause is the seat. No pass 5 door refused or changed the path in either
failing run (observed: case_runs seq 433637 and 433638, 2026-10-12 18:25).
The baseline at prompt hash `3697edde4a361441` was 4/5 on three recordings,
run 1 red each time with `forbidden call to msg.challenge_tester`. The prompt
hash moved to `55f5747b6eaee85f` with the `tests_failing.md` reason slot.

- Run 1: `expected a call to code.commit; called ['batches.expect', 'code.diff', 'code.probe', 'code.source', 'code.write', 'criteria.load', 'references.load', 'tests.load']`.
  The seat wrote once and then looped on `batches.expect`. The errors are
  `repeat refused: batches.expect asked three times ...`, `wrote its own tool results`,
  and `batches.expect was refused the same way in four turns; the session ended on it`.
  No challenge, no pass 5 door.
- Run 2: `forbidden call to msg.challenge_tester`. The seat wrote and
  committed. `tests.load` still showed the old fail. The seat then called
  `msg.escalate_architect` and then
  `msg.challenge_tester(refs=['c_c2d836', 'tst_22d54a'], quotes=[...], reason="The test asserts that confirm() returns the default when stdin is at EOF and default_on_eof=True. My code now implements exactly that behavior ... the two-line check answer is Yes.")`.
  The reason door admitted it, and the run wrote `decisions: 1`. The last two
  turns: `Nothing more is owed on tst_22d54a in this session.`, then errors
  `wrote its own tool results`, the older challenged-test door on `code.write`
  and `code.commit` (`you sent challenge to tester in this session (m2): ...`),
  and a `tests.load` repeat refusal.
- Baseline run 2 passed and new run 2 fails. Baseline run 1 failed on a
  challenge and new run 1 fails on a loop. The failures moved between runs,
  and the count moved by one, on a stochastic seat.

Is it pass 5's: no. The rule of the brief applies: 3/5 with no pass 5 door in
the two failing runs is the seat.

Fix line: one re-record of the case.

Note for pass 5b, low: the reason door admitted a reason that argues the
test passes ("the two-line check answer is Yes"). The door checks form and
copies, not the direction of the argument (reasoned: the door reads only the
call's own reason and its quotes, design section 11, fix 2). The TOOL line
shows `reason=None`, which reads as optional while the door refuses a
missing reason (observed: the system diff above).

## 3. `L1-DV-fix-the-code-not-the-test`: FAIL 0/5

The failure text did not change. Before and after, all five runs carry
`forbidden call to msg.challenge_tester` (observed: prompt hash
`3697edde4a361441` at 16:23 and `55f5747b6eaee85f` at 17:52, 2026-10-12).
Run 1 follows the same path in both: probe, source, write, commit,
`tests.load`, two challenges. The only difference is that the new challenges
carry `reason=`, the reason door admits them, and the run writes
`decisions: 1`. The error is the same quote door in both:
`msg.challenge_tester: quotes= must copy c_d1f8db's exact words and what you sent is not in the criteria row. ...`.
Pass 5 did not change this case's failure.
