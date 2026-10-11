# Frame 200, pass 2c: the nine findings of the review of 8d090e2e

Main checkout `D:/repos/rota`, branch `rota/foundation`, HEAD 7d5553a9 at the gate. Rota workflow. No commit, no `git add`, no sub-agent, no model call outside the gate. All observations 2026-10-11.

## (a) What changed

```
 rota/core/db.py                    |  44 ++++++++++++++--
 rota/core/sandbox.py               |  74 ++++++++++++++++++++++-----
 rota/roles/api.py                  |  43 ++++++++++++++++
 tests/rota/cases/l1_answers.yaml   |  20 ++++++--
 tests/rota/cases/l1_architect.yaml |   8 ++-
 tests/rota/test_predicates.py      |  47 +++++++++++++++++
 tests/rota/test_row_route.py       | 101 ++++++++++++++++++++++++++++++++++++-
 7 files changed, 316 insertions(+), 21 deletions(-)
```

The other modified files in `git status` (`rota/testkit/gitfixture.py`, `tests/rota/conftest.py`, `tests/rota/test_findings_doors.py`, `tests/rota/test_verdict_lines.py`, and the untracked `rota/testkit/dbtemplate.py`, `tests/rota/test_templates.py`) belong to frame 203's implementer. This pass did not touch them. No file holds a CR byte.

- `rota/core/db.py`, `_owes_a_reply`: finding 1. The pair `critic -> developer` owes no reply, because `developer/challenge.md` says "You have no message back to Critic". The first fix of the brief. A barren session on that challenge still reads unresolved by the older barren-challenge rule.
- `rota/core/db.py`, new `_answers_by_message`, and `_received(conn, result, trig)`: finding 2. A decision is no receipt when the graph gives the addressee an `answer` edge to the asker. The graph gives that edge to the Architect toward the Developer, so the Architect must answer. The Vision Keeper has no answer edge to the Architect or to the Terminologist, so its decision stays a receipt.
- `rota/core/db.py`, `_received`: finding 8. A decision that cites the trigger's id is a receipt. A decision that cites any other id of the `messages` table is a receipt for that message only, so the overlap rule does not apply to it.
- `rota/core/sandbox.py`, `_answer_mode_challenge_refusal`: finding 9. The sentence "The answer carries the rows you sent back and no words." appears only when the trigger's `body_text` is empty.
- `rota/core/sandbox.py`, `_rowless_answer_refusal`: finding 3. When `ctx.writes` holds a row, the refusal names those row ids and offers `msg.answer_developer(refs=[<written ids>])` through `api._offer`. With no write, the text is unchanged.
- `rota/core/sandbox.py`, new `_carries_decision`, used by `_challenges_on` and `_challenge_cap_refusal`: finding 7. The cap exemption holds only for a decision that is a ref of the trigger answer, or a decision whose own `refs` cite a test of the challenge. `_challenges_on` reads each prior challenge's `cause_id` for the same rule. The answer-mode door keeps `_holds_decision`.
- `rota/roles/api.py`, new `_escalated_test_route`, used in `findings_find`: finding 5, the reviewer's route. When the constraint id is a criteria or tests row, the trigger is an escalation, and its refs hold a test and no finding, the refusal names `decisions.author` with the test id, then `msg.answer_developer`. It records an offer of `decisions.author` with `id` and `text` as `INVENT`. It refuses no call that was admitted before.
- `tests/rota/cases/l1_answers.yaml`, `L1-DV-a-wordless-answer-leaves-a-wrong-test-alone`: finding 4. The inbound answer now carries `<d1>`, an Architect decision that says the test is wrong and names lines 10 and 13. The cause line stays. The expectation stays the one sentence and no landed `code.write` or `code.commit`. The case id is unchanged. No Developer door was added.
- `tests/rota/cases/l1_architect.yaml`, `L1-AR-a-test-that-misses-its-criterion-gets-a-decision-row`: finding 5. The decision must carry one of `decorated()`, `(cmd)`, `line 10`, `line 13`, and must not carry `is valid` or `correctly identifies`.
- `tests/rota/test_predicates.py`: three tests, one per finding 1, 2 and 8, after probe `p1.py` cases B, C and D.
- `tests/rota/test_row_route.py`: the cap test's decision now cites `tst1`. Five new tests: an unrelated decision meets the cap (finding 7), a decision the trigger answer carries passes the cap (finding 7, guard), the amend then answer offer and its dry run (finding 3), the answer with words (finding 9), and the `findings.find` route (finding 5).

Finding 6 is older than the frame and is not this pass. Candidate frame: the cassette store has no `done_reason` column, so a replayed `Completion` has no `raw`, a reply cut at the output budget replays as `unterminated argument list`, and the next prompt changes (`rota/llm/cassettes.py:346-358`, `:392-410`, `rota/core/runner.py:3506`).

### The refusal texts as the tests see them

- Finding 3, an amend of `k_new` then `msg.answer_developer(refs=['c1', 'tst1'])`:
  `refs=['c1', 'tst1'] add no row to the refs of m155, so the Developer gets back the rows it sent. This session wrote k_new. Send msg.answer_developer(refs=['k_new']).`
  The offer is `msg.answer_developer {"refs": ["k_new"]}`, and `dry_run` admits it.
- Finding 3, no write (unchanged):
  `refs=['c1', 'tst1'] add no row to the refs of m155, so the Developer gets back the rows it sent. Write what you found with decisions.author, then send msg.answer_developer with the decision's id in refs.`
- Finding 9, an answer with text, the test asserts the start:
  `no ref of this answer is a decision row. If you still read the test as wrong, say so in one sentence and end. End the session with no call.` followed by `END_FORM`.
- Finding 9, an answer with no text (unchanged):
  `no ref of this answer is a decision row. The answer carries the rows you sent back and no words. If you still read the test as wrong, say so in one sentence and end. End the session with no call.` followed by `END_FORM`.
- Finding 5, `findings.find(constraint_id='c1')` on escalation m155:
  `'c1' is a row of criteria, not a constraint. A finding names a constraint from model.consult. The escalation m155 is about the test tst1 and carries no finding. If tst1 does not encode its criterion, write a decision with decisions.author, refs=['tst1'], that names the line of tst1 that does not encode it. Then send msg.answer_developer with the decision's id in refs.`

### Red on 8d090e2e

Each new test asserts a behaviour that the review's probes measured on 8d090e2e: `p1.py` case B read `unresolved` for finding 1, case C read `answered` for finding 2, case D read `answered` for finding 8, and `p5.py` line 1 named `decisions.author` for finding 3. The tests for findings 5, 7 and 9 assert texts or results that 8d090e2e's code does not produce, by reading. I did not run the new tests against a checkout of 8d090e2e, because the brief forbids `git checkout`. The guard test `test_a_decision_the_trigger_answer_carries_passes_the_cap` is green on 8d090e2e too, by design.

## (b) The suite

Touched files, each with `ROTA_MODEL=qwen3:8b .venv/Scripts/python.exe -m pytest <file> -q`:

- `tests/rota/test_predicates.py`: `92 passed in 126.68s`.
- `tests/rota/test_row_route.py`: `15 passed in 17.91s`.
- `tests/rota/test_case_reachability.py tests/rota/test_desk_guards.py tests/rota/test_offers_followed.py tests/rota/test_prints_door_kind.py`: `936 passed, 20 skipped, 6 xfailed in 170.85s`.

The gate, started at 15:18:26 after the other gate on the machine ended, command `ROTA_MODEL=qwen3:8b .venv/Scripts/python.exe -m rota.tools.gate`, verbatim:

```
main card: held by qwen3:8b until 2026-10-11T15:22:13.0975152+01:00, re-records wait
suite: 27 failed, 3601 passed, 32 skipped, 19 xfailed, 17 warnings, 1 error (baseline: 24 failed, 3580 passed, 32 skipped, 20 xfailed, 17 warnings)
new reds (3): tests/rota/test_delivery.py::test_the_judgement_records_what_it_judged, tests/rota/test_desk_guards.py::test_a_second_verdict_on_one_commit_is_refused, tests/rota/test_verdict_lines.py
reds gone (0): none
stale (2): L1-AR-a-test-that-misses-its-criterion-gets-a-decision-row, L1-DV-a-wordless-answer-leaves-a-wrong-test-alone (+2 -0 against baseline)
time: 1747.1s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 5d68808 2026-10-11 02:11
note: the tree moved past the baseline (5d68808 -> 7d5553a)

flaky: tests/rota/test_delivery.py::test_the_judgement_records_what_it_judged
flaky: tests/rota/test_desk_guards.py::test_a_second_verdict_on_one_commit_is_refused
flaky: tests/rota/test_verdict_lines.py
.......................................................................  [100%]
71 passed in 14.96s

note: 2 stale cases wait for the main card
exit 1: 3 new reds, 3 of them flaky
```

- No `rerecorded` line. The gate printed no re-record, because the main card was held by another run. The two re-scoped cases are STALE and wait for the main card.
- The three new reds pass on the gate's re-run, `71 passed`, so the gate marks all three flaky. `tests/rota/test_verdict_lines.py` and the `1 error` belong to frame 203's files, which change in this checkout during the run. This pass touched neither.
- No traceback: the gate printed none, because each new red is flaky.

Case tallies: none measured in this pass. `L1-DV-a-wordless-answer-leaves-a-wrong-test-alone` and `L1-AR-a-test-that-misses-its-criterion-gets-a-decision-row` are STALE. Their previous tallies, 1 of 5 (false, by finding 4) and 2 of 5 (wrong diagnosis, by finding 5), no longer apply. The Architect prompt can also move for cases where `findings.find` meets the new route. No such case showed as stale beyond these two.

Casestatus counts: the gate's stale line, 2 stale. I did not run `casestatus`.

## (c) Deviations from the brief

1. No re-record ran. The gate held the two cases for the main card, and the brief allows one gate run. Re-record the two cases when the card is free, then read their tallies before any acceptance.
2. The Developer case keeps `expect: messages: []`, which checks nothing by itself. The re-scoped answer carries a decision row, and `developer/answer.md` then designs `msg.challenge_tester` with the decision's id. So the case forbids only a landed `code.write` or `code.commit` and does not forbid the challenge. The review's point stands: a run whose every `code.write` fails as invalid Python still passes. The brief rules out a Developer door, so the case cannot tell the designed end from a failed write.
3. The red-first proof for findings 5, 7 and 9 is by reading, not by a run on 8d090e2e, because the brief forbids `git checkout`. A worktree would allow it.
4. Finding 1 took the brief's first fix. The probe shows no case that it misses: the Developer's reply to a Critic challenge is a commit or a `ledger.log`, and neither carries the challenge.

## (d) Open questions for the assistant

1. Should the Developer case gain a positive branch, for example `any_of` with a tester challenge that refs `<d1>`, or a check that no `code.write` was even attempted? The current case reads a failed write as a pass.
2. `_carries_decision` reads a decision's own `refs` for a test id. A decision whose refs cite only the criterion, and which the trigger answer does not carry, still meets the cap. Is that the intended reading of the ruling of 06:30?
3. The pass 2d patch in `plans/frame200-pass2d-report.md` was built on a worktree with pass 2c staged. Pass 2c's final text differs from any earlier draft only if that worktree took another copy. Check that patch against this diff before it lands.

## (e) Usage

About 95k input tokens, about 20k output tokens, about 115k in total, against a cap of 150k. These are estimates from the context counter, not the harness line. Sub-agent usage: none.
