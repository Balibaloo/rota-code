# Frame 213, passes 1 and 1b: the review of 1055a2c5 and f252df24

Reviewer: a read-only agent on the worktree `C:/Users/roman/rota_rv213` at
f252df24, 2026-10-13. All statements are about the rota workflow, the seats,
unless they say meta workflow.

Verdict: accept with one high. Route B now reaches the repair mode, but it
tells the Terminologist to rewrite a criterion that the principal approved.

## (a) Verdicts on the points

1. Route A holds end to end, and law 2 holds. CONFIRMED (observed: probe A).
2. Route B reaches `criterion_repair`, and no door refuses `criteria.respecify`. The wake marks an approved criterion `revise`, which is finding 1, high. CONFIRMED.
3. No change for a criterion ruled directly. The s122 relay stages the same refs with and without the edit. CONFIRMED.
4. Holds. The case with no test and no commit keeps the old sentence. The abandoned and deferred cases admit. CONFIRMED.
5. Holds. The criterion shows `check: none yet.`, and a live batch's test still shows. CONFIRMED.
6. Holds. The order of the doors caused the red. A challenge with no red test in its refs meets no new door. CONFIRMED.
7. Holds with a count of 10, not 11. 9 are red at 4036b497 and 1 is red at c0954f92. All 10 are green at f252df24. CONFIRMED.
8. Gate: 8 new reds, all in the known set. Stale 0. CONFIRMED.

### Point 1, route A

Probe A replays night 145's shape: the page m141, the verdict m143 that
contests c1 with the m142 words, and the relay m144. A scripted
Terminologist session on m144 ran in `criterion_repair`. It called
`criteria.respecify` and then `msg.answer_tester`, and it committed. The
answer m145 woke the Tester. `resolve_inbound` gave
`principal_verdict = {c1: contest}` and `principal_said` = the m142 words
(observed: probe A, 2026-10-13).

Law 2 says that judgement crosses a role boundary only as structured
findings, and that a role keeps its reasoning in the decision record. The
principal's words are not the reasoning of a role. They reach the Tester
through the ruling's own cause chain, which the relay wake already uses. No
new edge exists. The sentence in `rota/roles/prompts/tester/answer.md:13`
labels the words. It does not put the reasoning of a seat on the answer. The
ruling of 2026-10-08, point 2, says that the Tester rewrites the test from
the ruled words, and this sentence serves that ruling (reasoned: the law
text and the diff).

### Point 2, route B

Probe B replays night 144's m400. The Liaison ruled `{c1: approve,
tst: revise}` with the m400 words and relayed the test row. The relay went
to the Terminologist with `[c1]`. The mode of the wake is `criterion_repair`.
A scripted session there called `criteria.respecify` with new text and then
`msg.answer_tester`. The session committed, the criterion text changed, and
the inbound of the Tester carried `{c1: revise}` and the m400 words
(observed: probe B). The words need the entry `e_m400`, which the wiring
records in a night. Without that entry, `principal_said` is None in the
fixture.

`api._ruled_ids` returns `{c1}` as approved. Only `_adopt_rows` reads it,
and `glossary.adopt` is not in the `criterion_repair` tools. So no door
refuses the repair. The defect is the other way: see finding 1.

### Point 3, `stage_park_relay`

s122 woke on the relay m36 `[cj_serializable]`, caused by the verdict m34
on `[cj_serializable, bg_1]`. `verdict_rows(m34)` holds no test row, so
`tested` is empty. The new `body_refs` is
`list(dict.fromkeys(list(contested)))`, which equals the old
`list(contested)`. 0 of the 24 verdicts of night 145 name a test row
(observed: probe P3 on `clickI_night145.db`, read-only). `verdict_rows`
keeps contested and revised rows only, so an approved test row never adds
its criterion (reasoned: scheduler.py:1765-1782).

### Point 4, the answer door

`test_a_repaired_criterion_reaches_the_tester_only_after_a_commit` passes
at f252df24, with the old sentence. The parametrised `abandoned` and
`deferred` cases admit. The merged case names the test, the criterion, the
batch and its status (observed: pytest at f252df24).

### Point 5, the check line

Probe P5 rendered the version option request. The c1 test sits in the
abandoned bg_3, and a c2 test sits in the running bg_5. With no batch, c1
shows `check: none yet.` and c2 shows its check. On the page about bg_3, c1
shows its test (observed: probe P5).

### Point 6, the quote door

At the first placement the red-line door ran inside `_challenge_evidence`,
before `_same_refs_refusal`. A repeat challenge then met a plain
`ValueError`, and not the `EndRefusal` of frame 165. The end form case and
`test_end_form` expect the ending refusal, so both went red. After the
move, the same-refs door answers first (reasoned: sandbox.py:2981-3011 and
the pass report). Both are green in this gate (observed). With no run, or
with a green newest run, `_red_line_refusal` returns None (observed: probe
P6).

### Point 7, the new tests

The new tests are 10 items, not 11: test_desk_guards.py 3 (one function,
and one function with two parameters), test_request_page.py 7 (six
functions, one with two parameters). Each file at f252df24 ran as an
untracked copy in a worktree at each parent.

- 4036b497: 10 failed. The failures are assertion failures and the old
  refusal sentence, not import errors (observed).
- c0954f92: 9 passed, 1 failed. The failure is
  `test_a_revised_test_row_wakes_the_terminologist_in_the_repair_mode`.
- f252df24: 10 passed.

### Point 8, the gate

The gate ran from the worktree with the `.rota-gate.json` of the checkout
and a `sqlite3` backup of `tests/rota/cassettes.db`.

```
suite: 30 failed, 3848 passed, 35 skipped, 17 xfailed, 29 warnings (baseline: 24 failed, 3580 passed, 32 skipped, 20 xfailed, 17 warnings)
new reds (8): test_invoke_door::test_a_session_with_no_batch_reads_the_root, test_l1[L1-AR-a-test-that-misses-its-criterion-gets-a-decision-row], test_l1[L1-AR-route-an-escalation], test_l1[L1-DV-apply-the-answer-and-carry-on], test_l1[L2-DV-name-the-block-rather-than-retry], test_l1[L2-DV-name-the-deferred-batch-not-the-running-one], test_scene_challenged_again::test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op, test_scene_two_batches::test_a_right_call_lands[the project test tests/test_templates.py as an encode]
reds gone (1): test_l1[L1-VK-a-statement-on-an-existing-account-is-a-behaviour]
stale (0): none
time: 776.8s, model qwen3:8b, baseline 5d68808 2026-10-11 02:11
```

Every new red is in the known set: the 2 HEAD reds, the 2 Architect cases,
`apply-the-answer` of frame 224, the 2 L2 cases of frame 204, and
`test_scene_challenged_again`, which the gate marks flaky. `test_map` is
green in this run. The skipped count is 35 and not 32, as in the pass
report. This review did not trace the 3 extra skips.

## (b) Findings

1. **high, CONFIRMED. `rota/core/runner.py:1749-1756`.** The route B
   mapping writes the `revise` of the test row over the own `approve` of
   the criterion. Probe B ruled `{c1: approve, tst: revise}`. The wake of
   the Terminologist then read `principal_verdict = {c1: revise}`.
   `criterion_repair.md:24-26` says to rewrite each criterion with contest
   or revise. `criteria.respecify` admitted the rewrite and committed it.
   The reason is that `last_ruling_on(c1)` returns `approve`, so the door
   of frame 226 (the principal faulted the check and not these words)
   never fires. On m400 the principal approved the criterion and said
   to change the test. The seat is told to change his approved words.
   `api._ruled_ids` reads the same chain and calls c1 approved, so two
   readers of one ruling disagree.
   Fix: keep the own ruling of a criterion, and carry the ruling of a test row under its own key. The repair brief then sends those words to the Tester with `msg.answer_tester`.

2. **low, CONFIRMED. `rota/core/sandbox.py:1135-1140`
   (`_red_line_refusal`).** When the `>` line of the run does not assert,
   the door takes the first `assert` line of the body. The refusal then
   names that line as the line the test fails at, which is false. Probe P6
   gave a run with `>       result.output.strip()` and the body line
   `assert result is not None`. The refusal named
   `assert result is not None`.
   Fix: use the `>` line whatever it holds, and use the first `assert` only when the run has no `>` line.

3. **low, PLAUSIBLE. `rota/roles/prompts/tester/answer.md:13`.** The
   sentence says that the words are about the test of this criterion. On
   route A the principal can contest the words of the criterion alone. The
   Terminologist has then applied the words already, and the Tester reads
   them as a fault in its test. The sentence also does not say what to do
   with the words. The reason is the text alone. No night shows a Tester
   that read the label so.
   Fix: say that the words are the ruling of the principal on this criterion, and that the test checks what the words ask.

Outside the points: the commit message of f252df24 says that the mode key,
the answer reader and the answer door agree. They do. The fourth reader,
`api._ruled_ids`, does not agree with the runner (finding 1).

## (c) Probes

- `C:/Users/roman/rota_rv213/tests/rota/probe_rv213.py`, untracked, now
  removed with the worktree. It ran four functions with `pytest -n0 -s` on
  the `m399` fixture: route A end to end, route B end to end with
  `_ruled_ids`, `last_ruling_on` and a same-words respecify, the check
  lines of `request_block`, and `_red_line_refusal` with no run, a green
  run and a red run whose `>` line does not assert.
- The scratchpad file `rv213_p3.py`. It read
  `D:/repos/rota/.rota/clickI_night145.db` read-only and immutable. It
  traced s122 to m36 and m34, and computed `tested` for m34 and for all 24
  verdicts.
- Worktrees at 4036b497 and c0954f92, now removed. Each held untracked
  copies of the two test files at f252df24 as `probe_new_*.py`. pytest ran
  the 10 new items with `-k` and `--tb=line`.
- The gate from the worktree, unpiped into a scratchpad file, after a copy
  of `.rota-gate.json` and a `sqlite3` backup of the register.

## (d) Usage

About 95k input tokens and 15k output tokens, about 110k in all, by the
token counter of the session. The cap was 80k. The gate wait, the three
worktrees and a heredoc that the shell refused took the excess. No
sub-agent ran.
