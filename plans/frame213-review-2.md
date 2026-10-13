# Frame 213, pass 1c: the review of 126b8c4e

Reviewer: a read-only agent on the worktree `C:/Users/roman/rota_rv213c` at
126b8c4e, 2026-10-13. All statements are about the rota workflow, the seats,
unless they say meta workflow.

Verdict: revise. The code of the three asks holds, but the gate shows one new
red outside the known set. The Tester case
`L1-TS-encode-a-criterion-the-principal-corrected` reads 3/5 under the new
`answer.md` line. The pass also has five low findings.

Counts: 1 high, 5 low.

## (a) Verdicts on the points

1. Route B holds through the inbound. The criterion keeps `approve`, and the test ruling travels as `principal_test_verdict`. Every door admits `criteria.respecify` on the approved criterion (finding 2). CONFIRMED.
2. Route A is unchanged. The Tester's inbound is the same at f252df24 and at 126b8c4e. CONFIRMED.
3. The sentence names `msg.answer_tester`, and the mode holds it. The condition is readable only when the criterion has its own ruling (findings 3 and 4). CONFIRMED.
4. The door names the `>` line in all three runs, as asked. On real nights the first `>` line is often a library line (finding 5). CONFIRMED.
5. Law 2 holds. The words stay on the cause chain, and the answer carries refs alone. CONFIRMED.
6. One test, not several. It covers ask 1, is red at f252df24 and green at 126b8c4e. Asks 2 and 3 have no red-first test (finding 6). CONFIRMED.
7. No other reader takes the test verdict as the criterion verdict. `ruled_test_criteria` only keys the mode. CONFIRMED.
8. Gate: 11 new reds, 3 flaky, stale 0. One red is outside the known set (finding 1). CONFIRMED.

### Point 1, route B end to end

The probe replays m400. The Liaison rules `{c1: approve, tst: revise}` with
the m400 words and relays the test row. The relay m401 goes to the
Terminologist with `[c1]`, and the mode key gives `criterion_repair`
(observed: probe RB).

- The Terminologist's inbound: `principal_verdict = {c1: approve}`,
  `principal_test_verdict = {tst: revise}`, and `principal_said` holds the
  m400 words. At f252df24 the same inbound read `{c1: revise}` and had no
  test key (observed: probe RB at both commits).
- `api._ruled_ids` returns `{c1}`. `last_ruling_on(c1)` gives `approve`, and
  `last_ruling_on(tst)` gives `revise`. The two readers now agree with the
  inbound (observed).
- The real wake prompt through `run_session` holds `principal_test_verdict`
  in the user prompt and "A ruling on a test" in the system prompt (observed).
- A scripted `criteria.respecify` on c1 in that wake is admitted. The session
  commits, and the text of c1 changes. No door refuses it. The frame 226 door
  fires only on a contest or a revise of c1 (observed: probe RB; reasoned:
  `rota/roles/api.py:4863-4866`).
- The Tester's wake on the Terminologist's answer, with the relay as cause:
  `principal_verdict = {c1: approve}`, `principal_test_verdict = {tst: revise}`,
  and `principal_said` holds the m400 words (observed: probe RBT).

### Point 2, route A

Probe RA replays m141, m143 (a contest of c1 with the m142 words), m144 and
the answer m145. The Tester's inbound keys are `from, principal_said,
principal_verdict, refs, resolved_refs, verb` at both commits.
`principal_verdict = {c1: contest}` at both commits. Neither commit gives
`principal_test_verdict` (observed: probe RA at f252df24 and at 126b8c4e).
The reason: `tested` stays empty when no test row is ruled, so the hunk adds
nothing.

### Point 3, the repair sentence

The new paragraph, `rota/roles/prompts/terminologist/criterion_repair.md:32-36`:

> **A ruling on a test.** When the message holds `principal_test_verdict`, the
> principal ruled on the test of the criterion, not on its words. If the
> criterion is approved, do not call `criteria.respecify`. Send
> `msg.answer_tester` with the criterion in `refs`, so the Tester rewrites the
> test from the principal's words.

`python -m rota.tools.map mode terminologist/criterion_repair` lists
`msg.answer_tester -> message answer to tester`. The sandbox call
`msg.answer_tester(refs=[c1])` in that wake returns `to: tester` (observed).
The seat reads "approved" as `principal_verdict = {c1: approve}` on m400's
shape. When the Liaison rules the test row alone, the inbound has no
`principal_verdict`, and the condition has no field to read (finding 4).

### Point 4, the quote door

Probe RL calls `_red_line_refusal` on a red run of `tst_ver_opt_show_py_01`
with a quote that misses every line. The body's first assert is
`assert result is not None`.

- The `>` line does not assert, `>       result = runner.invoke(cmd, ['--version'])`.
  The refusal names `result = runner.invoke(cmd, ['--version'])`. At
  f252df24 it named `assert result is not None` (observed).
- The `>` line asserts, `>       assert 'Python' in result.output`. The
  refusal names `assert 'Python' in result.output` at both commits (observed).
- No `>` line. The refusal names `assert result is not None` at both commits
  (observed).

### Point 5, the Tester's answer sentence

Old line 13: "**When the message holds `principal_said`, those words are the
principal's words about the test of this criterion.**"

New line 13: "**When the message holds `principal_said`, those words are the
principal's ruling on this criterion or its test, and the test checks what
the words ask.**"

Law 2 (`rota/LAWS.md:112-116`) lets judgement cross a role boundary only as
structured findings. The principal's words are not a role's reasoning. They
reach the Tester through the ruling's own cause chain, which the relay
already uses. `principal_test_verdict` is a per-item ruling, ids and states.
The Terminologist's answer carries refs alone. So the words stay off the
answer and beside the test, as the ruling of 2026-10-08, point 2, allows
(reasoned: the law text and probe RBT).

### Point 6, the new tests

The 40 lines are one test,
`test_an_approved_criterion_keeps_its_verdict_beside_its_revised_test`. It
covers ask 1: the inbound keys, the key name in the brief, and an admitted
`msg.answer_tester`. It does not call `criteria.respecify`, so it does not
prove the "do not respecify" half of ask 1. A copy of the file at 126b8c4e
ran in a worktree at f252df24. The test failed at its first assert,
`assert 'revise' == 'approve'` (observed). The test passes at 126b8c4e
(observed: the probe run, 100 passed, 4 xfailed). Asks with no red-first
test: 2, ask 2 (the quote door) and ask 3 (the answer sentence).

Note: the parent of 126b8c4e is 2f78e6d3, not f252df24. Between the two,
`rota/roles/api.py` and other test files changed. `runner.py`, `sandbox.py`
and the two prompts are the same (observed: `git diff --stat`).

### Point 7, the other readers

`python -m rota.tools.map table rulings --column per_item` lists 7 readers.
Each reads the per-item key of its own row. Only `ruled_test_criteria`
(`rota/core/scheduler.py:1834-1865`) maps a test row to its criterion. Its
one caller, `park_criterion_relay`, uses the result to key the mode
(`runner.py:281`), the answer reader (`sandbox.py:672`) and the relay stage
(`sandbox.py:3594`). None of them reads the verdict value as the
criterion's. `last_ruling_on` and `_ruled_ids` read the criterion's own
key. The page writer reads no relay inbound. Before 126b8c4e the runner hunk
was the only place that wrote a test verdict over a criterion key (reasoned:
the map output and the code at each site).

### Point 8, the gate

The gate ran from the worktree, after a copy of the checkout's
`.rota-gate.json` and a `sqlite3` backup of `tests/rota/cassettes.db`. The
output is in the scratchpad file `rv213c_gate.txt`. The five lines follow.

```
suite: 34 failed, 3853 passed, 35 skipped, 17 xfailed, 28 warnings (baseline: 24 failed, 3580 passed, 32 skipped, 20 xfailed, 17 warnings)
new reds (11): tests/rota/test_handover.py::test_one_claim_wakes_exactly_one_standby, tests/rota/test_invoke_door.py::test_a_session_with_no_batch_reads_the_root, tests/rota/test_l1.py::test_l1_case[L1-AR-a-test-that-misses-its-criterion-gets-a-decision-row], tests/rota/test_l1.py::test_l1_case[L1-AR-route-an-escalation], tests/rota/test_l1.py::test_l1_case[L1-DV-apply-the-answer-and-carry-on], tests/rota/test_l1.py::test_l1_case[L1-TS-encode-a-criterion-the-principal-corrected], tests/rota/test_l1.py::test_l1_case[L2-DV-name-the-block-rather-than-retry], tests/rota/test_l1.py::test_l1_case[L2-DV-name-the-deferred-batch-not-the-running-one], tests/rota/test_map.py::test_the_fixture_project_contributes_no_table, tests/rota/test_scene_challenged_again.py::test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op, tests/rota/test_scene_two_batches.py::test_a_right_call_lands[the project test tests/test_templates.py as an encode]
reds gone (1): tests/rota/test_l1.py::test_l1_case[L1-VK-a-statement-on-an-existing-account-is-a-behaviour]
stale (0): none
time: 534.8s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 5d68808 2026-10-11 02:11
```

Before the five lines, the gate re-recorded 2 stale cases in the register
copy of the worktree. `L1-AR-judge-a-stray-foreseen-or-a-mistake` went from
STALE to green 5/5. `L3-a-failed-verdict-turns-into-a-fix` stayed FAIL 0/5,
stale by its failure. The flaky set is `test_handover`, `test_map` and
`test_scene_challenged_again`.

Against the known set:

- The 2 HEAD reds, `test_invoke_door::...reads_the_root` and
  `test_scene_two_batches::...as an encode`. Known.
- The 2 Architect cases. Known.
- `L1-DV-apply-the-answer-and-carry-on`, frame 224. Known.
- The 2 L2 cases, frame 204. Known.
- `test_scene_challenged_again`, flaky. Known.
- `test_map::test_the_fixture_project_contributes_no_table`, flaky. The brief
  names `test_every_op_joins_a_definition`. `plans/operating-facts.md:679`
  names this node and its cause, a leaked handover watcher.
- `test_handover::test_one_claim_wakes_exactly_one_standby`, flaky. It is
  the source of the same leak, so it is not a finding.
- `L1-TS-encode-a-criterion-the-principal-corrected`, 3/5. Not known.
  Finding 1.

## (b) Findings

1. **high, CONFIRMED. `rota/roles/prompts/tester/answer.md:13`.** The new
   red `L1-TS-encode-a-criterion-the-principal-corrected` reads 3/5 at
   126b8c4e. Its first red line: `AssertionError:
   L1-TS-encode-a-criterion-the-principal-corrected: 3/5 passed, needs 4`,
   then `run 1: expected writes to tests (1..1), got 0`. The register holds
   a live recording at 18:30:47 under prompt hash `44640eddfd788c44`, 3/5.
   The hashes before read 4/5 (`8637f910ae676693`, live at 16:15:54) and 5/5
   (`eab9484e13d0d243`, replays from 05:36 to 15:47) (observed: `case_runs`
   in the register copy of the worktree and in the register of the
   checkout). The case wakes the Tester in `answer` mode, so the changed line
   of `answer.md` is in its prompt (reasoned: the case YAML,
   `tests/rota/cases/l1_answers.yaml:542-553`). Run 1 encoded four tests that
   use an undefined helper, met the NameError door each time, and ended with
   no write. The holding session ran only the page files before the commit,
   so it did not see this case.
   Fix: read the turns of runs 1 and 5, re-word line 13 or keep the old line, re-record to 4/5 or better, and gate again.

2. **low, CONFIRMED. `rota/roles/api.py:4863-4866`
   (`criteria_respecify`).** On m400's shape the Terminologist's
   `criteria.respecify` of the approved c1 is admitted and committed. Only
   the brief paragraph stops the rewrite of approved words. The frame 226
   door reads `last_ruling_on(c1)`, which is `approve`, so it never fires
   (observed: probe RB, the text of c1 changed).
   Fix: refuse `criteria.respecify` when the ruling of the wake approves the criterion and carries a test verdict, and name `msg.answer_tester`.

3. **low, PLAUSIBLE. `rota/roles/prompts/terminologist/criterion_repair.md:30`.**
   The ruling paragraph ends "An approved criterion needs nothing." On m400
   the wake shows `principal_verdict = {c1: approve}`. That sentence comes
   before the new paragraph and tells the seat to do nothing. The new
   paragraph then tells the seat to send `msg.answer_tester`. A small model
   can stop at the first sentence (reasoned: the order of the brief; no
   night ran it yet).
   Fix: end line 30 with "unless the message holds `principal_test_verdict`", or move the new paragraph above it.

4. **low, CONFIRMED. `rota/core/runner.py:1752-1767`.** The Liaison can rule
   the test row alone, `{tst: revise}`. The relay then still keys
   `criterion_repair`. The inbound holds `principal_test_verdict` and the
   words, and no `principal_verdict` (observed: probe RB1). The new
   paragraph says "If the criterion is approved". The seat has no field
   that says so, and the paragraph gives no step for that case.
   Fix: say "If `principal_verdict` holds no contest or revise for the criterion" in the paragraph.

5. **low, CONFIRMED. `rota/core/sandbox.py:1139-1140`
   (`_red_line_refusal`).** The first `>` line of a run is often a frame in
   library code, not a line of the test. In nights 143 to 145, 8 of 41
   marked red runs have a first `>` line that is not in the test body. An
   example is `prog_name = ctx.find_root().info_name` for `inh_dcc9ea38`. In
   4 of the 8, a later `>` line is in the body (observed: a read-only query
   on `clickI_night143.db` to `clickI_night145.db`). The refusal then tells
   the seat that the test fails at a click line. It also says that "a quote
   of another line of the test names the wrong conflict". The fix line of
   the first review asked for this behaviour, so the defect starts there.
   Fix: take the first `>` line that is in the code of the test body, else the first `assert`.

6. **low, CONFIRMED. `tests/rota/test_request_page.py:1587-1624`.** The pass
   adds one test, for ask 1. Asks 2 and 3 have no red-first test. The resume
   message asked for one per ask (observed: the diff). The one test also
   does not show that the repair wake avoids `criteria.respecify`.
   Fix: add a door test with a non-asserting `>` line, and a check on the new line of `answer.md`.

Outside the points: findings 4 and 5 sit beside points 3 and 4. No other
finding.

## (c) Probes

- `tests/rota/probe_rv213c.py`, untracked, in both worktrees, now removed
  with them. A copy stays in the scratchpad as `probe_rv213c.py`. It imports
  the fixtures of `test_request_page.py`. It ran five functions with
  `pytest -n0 -s`:
  - RB: route B, the inbound of the Terminologist, `_ruled_ids`,
    `last_ruling_on`, the wake prompt through `run_session`, and a scripted
    `criteria.respecify`.
  - RB1: route B with the test row ruled alone.
  - RBT: the inbound of the Tester after `msg.answer_tester`.
  - RA: route A for both seats.
  - RL: `_red_line_refusal` on four red runs.
- A second worktree, `C:/Users/roman/rota_rv213c0` at f252df24, now removed.
  It held the 126b8c4e `test_request_page.py` as `probe_new_request_page.py`
  and the probe above. The new test failed there at its first assert, and
  the probe printed the values before the change.
- A read-only query on `D:/repos/rota/.rota/clickI_night142.db` to
  `clickI_night145.db`, opened immutable. It counted red runs whose first
  `>` line is not an assert, or is not in the test body.
- Read-only queries on `case_runs` in the register copy of the worktree and
  in the register of the checkout, for the case of finding 1.
- The gate from the worktree, unpiped into the scratchpad file
  `rv213c_gate.txt`, after a copy of `.rota-gate.json` and a `sqlite3`
  backup of the register.

## (d) Usage

About 105k input tokens and 15k output tokens, about 120k in all, by the
estimate of this session. The cap was 80k. The gate wait and the register
queries took the excess. No sub-agent ran.
