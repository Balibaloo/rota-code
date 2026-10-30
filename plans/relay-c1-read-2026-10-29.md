# The relay drops `<c1>`: a read, 2026-10-29

## Result

The code drops `<c1>` on purpose. The seat ruled the criterion `approve`, and an approved criterion reaches no relay.
The filter that drops it came in commit 63d9042c (2026-10-27 01:35, frame 338).
None of f920fd39, 9e4d7c6c and ed7d00a8 changed this behaviour.
The model swap did not cause the red. The recorded qwen3:8b reply fails the same way on today's code.
The wrong side is the seat's verdict. The principal's words change the criterion, so the brief's own rule reads `revise`.
The brief primes the error. Its only example rules a criterion `approve`, at `rota/roles/prompts/liaison/answering.md:47`.

## (a) The verdict on each point

1. Relay path traced. The drop is at `rota/core/sandbox.py:4749-4753`, fed by `ruled_rows` at `rota/core/scheduler.py:2054-2060`.
2. Reproduced without a model. The gemma refs and the qwen refs both store `["e_m_in"]`. A `revise` ruling stores both refs.
3. The three named commits: none is the cause. The cause is 63d9042c, which landed between the green qwen run and the gemma run.
4. Reach: 1 filter site. `ruled_rows` has 4 call sites in 3 functions. 2 L1 cases expect a criterion in a relay, and 1 is hit.
5. Fix: correct the brief's example to a `revise` reading, then re-record the case on gemma4. The code is right by frame 190, 2.F, amendment 1.

## (b) Findings

1. `rota/core/sandbox.py:4749-4753`, high, CONFIRMED. On a relay, the send stage reads `ruled_rows(conn, trigger, writes)`.
   The session staged one `rulings` row and one `ruled_refs` row with verdict `approve`.
   So `ruled_rows` returns `[]` and not None, at `rota/core/scheduler.py:2054-2060`.
   The filter then keeps only refs that are in `[]` or are no criterion. `e_m_in` stays, `c_ec730c` goes.
   Before 63d9042c, the branch read `verdict_rows`, which is None for a `converse` trigger. So no filter ran, and qwen passed.
   The probe shows the stored refs `["e_m_in"]` for both the gemma call and the qwen call.
   Fix: none in the code. The filter applies a ruled design: an approved criterion reaches no relay.
2. `rota/roles/prompts/liaison/answering.md:47`, high, PLAUSIBLE. The only `rulings.rule` example rules a criterion `approve`.
   Both models copy the example on a reply that adds "the total, both printed" to "the tip is right".
   Lines 16-17 of the same brief define that change as `revise`. Five runs of five on each model chose `approve`.
   Fix: give the example a `revise` verdict on a criterion, with the words that change it. Price: 1 edit, then 1 live gemma record of 5 runs.
3. `rota/core/sandbox.py:4440-4441` with `4754-4757`, low, CONFIRMED. Outside the points.
   The relay merges the trigger's `body_refs` (`e_m_in`) into the refs before the approval filter runs.
   So the guard "the principal approved these criteria as they stand" never fires on a converse reply.
   The qwen call `refs=["c_ec730c"]` stored `["e_m_in"]` and raised nothing. The terminologist gets a relay with nothing to act on.
   Fix: test the guard against the refs minus the trigger's `body_refs`. Price: 1 cycle with a unit test.
4. `tests/rota/cases/l1_answering.yaml:38`, low, PLAUSIBLE. The expectation `refs_include: [<c1>]` is right only under a `contest` or `revise` reading.
   The case asserts no verdict. A future seat that rules `approve` and relays nothing passes no check that names the cause.
   Fix: add an expected `ruled_refs` write with verdict `revise` on `<c1>`, if the register supports a write check. Price: 1 cycle.

## The mechanism in one sentence

The seat stages an `approve` ruling on `<c1>`, so `ruled_rows` returns an empty list, and the relay filter removes every criterion not ruled `contest` or `revise`.

## The reproduction output

The probe ran `fixtures.run_case` with scripted replies and a backend that raises if asked. Run 1 ids.

```
gemma approve | relay rows: [('terminologist', 'relay', '["e_m_in"]')] | ruled_refs: [('c_ec730c', 'approve')] | problems: ["message m1 missing refs {'c_ec730c'}", ...]
qwen approve  | relay rows: [('terminologist', 'relay', '["e_m_in"]')] | ruled_refs: [('c_ec730c', 'approve')] | problems: ["message m1 missing refs {'c_ec730c'}", ...]
gemma revise  | relay rows: [('terminologist', 'relay', '["e_m_in", "c_ec730c"]')] | ruled_refs: [('c_ec730c', 'revise')] | problems: [...]
```

The second problem on each line is the scripted run's note that no model completion followed. It is an artefact of the probe.

## The commits

- f920fd39 (2026-10-27 02:44): read-back contest and landing brief. No hunk on the relay filter or `ruled_rows`.
- 9e4d7c6c (2026-10-27 02:51): landing wake refs. No hunk on the relay filter or `ruled_rows`.
- ed7d00a8 (2026-10-28 00:14): the verdict read from `ruled_refs` rows. It touches `scheduler.py` by 6 lines, not the staged branch.
- 63d9042c (2026-10-27 01:35, frame 338): adds `ruled_rows` with the staged branch, and moves the relay filter from `verdict_rows` to `ruled_rows`. This is the change.

## The reach (C76)

- The filter: 1 site, `rota/core/sandbox.py:4749-4757`.
- The callers of `ruled_rows`: `predicates.py:494` (`term_collision`), `sandbox.py:4749` and `4750` (`_bind_send.stage`), `scheduler.py:2074` (`ruled_criteria`).
- The L1 cases that expect a criterion in a relay: 2. `l1_answering.yaml:38` is hit. `l1_liaison2.yaml:653` rules `<c1>` `contest`, so it passes the filter.
- The other relay expectations (`l1_liaison2.yaml:87`, `341`, `342`, `374`) carry no criterion, and the filter keeps them.

## The fix line and its price

Change the example at `answering.md:47` to a criterion ruled `revise` by words that change it. Then re-record the case live on gemma4:12b-it-qat.
Price: 1 cycle for the edit and the replay of the answering cases, plus 1 live record of 5 runs.
Finding 3 is a separate 1-cycle code fix.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/00ca90d0-18a5-4929-b3d3-aedcb3b99ae5/scratchpad/relay_c1_probe.py`: builds the case fixture by `fixtures.for_run(case, 1)` and runs `fixtures.run_case` with three scripted replies. It prints the stored relay refs and the `ruled_refs` rows.
- A query of `tests/rota/cassettes.db` for the recorded replies of the case, gemma4 and qwen3:8b.
- `git show --stat` on the three commits, `git blame` on `ruled_rows` and the filter, and `git show 63d9042c` on `scheduler.py` and `sandbox.py`.

## (d) Usage

Estimated: input about 60k tokens across the calls, output about 8k tokens, total about 68k. The harness gives no exact count.
