# Frame 110, the Tester re-wraps a test it should fix: scope read

Frame 110. Date 2026-10-02. Revision 1. Meta workflow, about the rota workflow's Tester seat on night 106.
Database: `.rota/clickI_night106.db`, read-only. All queries ran 2026-10-02 14:00 to 14:33.

## 0. Two corrections to the premise

- No challenge named `inh_echo_json_02`. The nine Developer challenges to the Tester name `_03` five times (m64, m65, m67, m70, m71), `_01` twice (m66, m72), and `tst_cr1_default_arg` and `tst_cr2_eof_default_true` once each (observed: `SELECT id, body_refs FROM messages WHERE verb='challenge' AND to_role='tester'`). The Tester never left a named test for `_02`. It did what each challenge named.
- All three tests failed from the start, not `_02` alone. The m66 wake carried `_01`'s `last_run` as `fail`, `AttributeError: 'function' object has no attribute 'name'` at `src\click\testing.py:387` (observed: `s146` turn 1 user, `resolved_refs.inh_echo_json_01.last_run`). A re-encode deletes the test's runs (observed: `rota/core/db.py:576-580`). So `test_runs` now shows no `_01` or `_03` row before af4cbede, and `plans/night106-read.md` section 2 reads that gap as a pass (reasoned: the deleted rows were the red runs the wakes quoted).
- The present harness text is `KeyError 'prog_name'` for every `test_runs` row of the three tests (observed: `test_runs` filtered on `output LIKE '%prog_name%'`, 13 of 13). The Tester saw the older `AttributeError` text in `s146` and `s153`.

## 1. The Tester's challenge mode

- The wake on `developer->tester challenge` composes `rota/roles/prompts/tester/base.md` and `rota/roles/prompts/tester/challenge.md` (observed: `s146` turn 1 system holds "MODE: challenge").
- `challenge.md:3-4` frames every claim as "asserts more than the criterion asked for, less, or something else". `challenge.md:6` says "Read the criterion again, cold, and decide". The brief says nothing about the harness output, the test's call shape or the challenge's code quote (observed: `challenge.md:1-16`).
- `base.md:5-6` says "You have no access to the codebase and this is not an oversight" (observed).
- `challenge.tools:1-8` lists `criteria.load`, `tests.consult`, `tests.encode`, `msg.answer_developer`, `msg.question_terminologist`, `msg.question_vision_keeper`, `batches.expect`, `msg.answer_critic` (observed). No `tests.load`, no `code.source`, no run tool. `answer.tools:6` has `code.source`, and challenge mode does not (observed).
- The Tester cannot run a test. It sees the failure text once: the runner puts the test's last run, 700 characters of tail, into `resolved_refs` (observed: `rota/core/runner.py:1580-1595`).
- The answer door in `rota/core/sandbox.py:674-697` checks that a held answer quotes the criterion. No door checks an encode against the failure text (observed).

## 2. What the Tester saw and said

- `s146` (m66, `_01`): the challenge `asks` quotes the criterion and the line `result = runner.invoke(echo_json, ['{"key": "value"}'], ...)`. It does not say "echo_json is not a command" (observed: `s146` turn 1 user). The tail shows `cli = <function echo_json ...>` and the AttributeError.
- `s146` said the fault is the argument shape: "invokes the CLI with a JSON string ... the test must be rewritten to pass a Python dict" (observed: `s146` completion 1). It encoded `runner.invoke(echo_json, [{"key": "value"}])`, still a plain function, and `tests.encode` returned OK (observed: `s146` turn 2 user).
- `s146` said "I will not touch the other two tests (`inh_echo_json_02`, `inh_echo_json_03`) because they are not part of this challenge" (observed: `s146` completion 1). The choice of test came from the refs.
- `s153` (m70, `_03`) named the real fault: "the test invokes it as if it were a Click command ... `runner.invoke` expects a Click command object, not a bare function" (observed: `s153` completion 1). It wrapped with `@runner.command()`, which `CliRunner` does not have, and passed `[BadObj()]` (observed: `s153` turn 3 tool line). The encode returned OK.
- `s155` read the next red as "`@runner.command()` ... is not a valid Click API" and moved to `@click.command()` (observed: `s155` completion 1). `s157` said "Click expects a `Command` object" (observed: `s157` completion 1).
- So the seat named the fault in three of five sessions. Each fix left two faults no seat named: `def cli(obj)` has no `@argument`, and a dict or an object is not a command-line string (observed: final bodies of `_01` and `_03` in `tests`; reasoned: click parses `args` as strings, and a parameter with no declaration receives nothing).
- No encode was refused for the call shape. The refusals were `the test chooses 'Should have raised TypeError'` and `pytest will collect nothing` in `s142`, and `the test uses what echo_json returns` in `s157` (observed: `ERROR tests.encode` lines in `turns.user`).

## 3. The `tests.encode` guard

- The op is `rota/roles/api.py:4563-5420` (observed: `python -m rota.tools.map`, then read).
- "pytest will collect nothing" is the shape check at `api.py:4625-4633`: the body needs a `def test_...` and an `assert` (observed).
- "the test chooses" is the invented-literal check at `api.py:5370-5394`: a literal not in the criterion, ticket, glossary or principal's words needs a `ledger.log` first (observed).
- Precedent for a harness-fact guard that reads the worktree: the `input()` checks at `api.py:4635-4750`. They parse the body with `ast`, walk `_worktree_of(ctx)` source files, find the called function's `def`, and refuse with the fix in the text (observed).
- Precedent for name resolution: `api.py:5170-5222` maps `from M import Y` to the worktree file, parses its module body, and lists the names it defines (observed).
- A non-command predicate is decidable from what the op holds (reasoned: both precedents read the same inputs). Steps:
  1. Find every `X.invoke(target, args, ...)` where `X` is bound to `CliRunner()` in the body.
  2. If `target` is a `def` in the body, accept it only when a decorator is `click.command`, `click.group`, or `command`/`group` imported from `click`, called or bare. `@runner.command()` fails this test.
  3. If `target` is imported from a worktree module, parse the module through the `api.py:5170-5190` resolver and apply the same decorator test to its `def`. A `Command(...)` assignment also counts.
  4. A target the op cannot resolve passes. A false refusal costs more than a miss (reasoned: the `api.py:4800-4806` note on a bare name).
- A second predicate covers what the night's later bodies kept: an `args` list literal holding a `dict`, a `set`, a list, or a call to anything but `str` is not a command line (reasoned: s146, s157 and the final `_01` pass a dict; `_03` passes `BadObj()`).
- `code.probe` cannot answer "is this a click command". `code_index` holds `grain`, `sym_kind`, `line_start` and `line_end`, and no decorator (observed: `rota/core/schema.sql:374-391`; `api.py:6353-6417`). The probe could give a span for `code.source`, and the decorator line may sit outside it (reasoned: `rota/onboarding/indexer.py:455-460` stores the parser's span and does not name decorators). The `ast` read in the op is the better source.

## 4. Recorded cases that wake the Tester on a challenge

- `L1-TS-hold-a-test-that-is-right` (`tests/rota/cases/l1_tester.yaml:7-49`): inbound developer challenge on a correct test. Expects one `answer` to the Developer. Forbids writes to `tests`, `criteria`, `items`. The comment at lines 41-48 records a flip to rewriting after the challenge toolkit grew two lines (observed).
- `L1-TS-fix-a-test-that-asserts-more-than-its-criterion` (`l1_tester.yaml:51-93`): inbound challenge on a test that asserts an ellipsis the criterion never named. Expects `criteria.load` and exactly one `tests` write. Forbids `criteria`, `items`, `tickets` (observed).
- No other case has `inbound: {... to: tester, verb: challenge ...}` (observed: grep over `tests/rota/cases/*.yaml`). No Tester case holds a `CliRunner` test. `L1-DV-challenge-a-test-with-a-long-body` at `l1_developer.yaml:309-375` holds one, from the Developer side, and expects a challenge (observed).
- Guard unit tests live in `tests/rota/test_desk_guards.py` and `tests/rota/test_t0_sandbox.py` (observed: grep for `tests_encode`).

## 5. Options with prices

Prices come from `plans/operating-facts.md:214-223` (the implementer cold pass 74k to 77k, resumed 24k to 40k, a cold diff review 61k to 76k). Re-record cost is about five minutes of GPU per case at five runs (`operating-facts.md:100`).

- (a) A brief line in `challenge.md`: "Read the last run's failure. Change the test the challenge names, at the line the challenge quotes." Add `code.source` to `challenge.tools`. Implementer pass about 25k, diff review about 60k. Re-records: the two Tester challenge cases, both composed from `challenge.md` (reasoned). Risk: a toolkit growth flipped `L1-TS-hold-a-test-that-is-right` once (observed: `l1_tester.yaml:41-48`), and a brief line on a 9B seat moved two cases at `operating-facts.md:333`. Gain is small: the seat already named the fault in three of five sessions, and the brief cannot tell it click's argument rules.
- (b) Two guards in `tests.encode`, after the `input()` checks: a non-command `invoke` target, and a non-string `args` element. Refusal text, for example: "`echo_json` is a plain function, and `CliRunner().invoke` runs a click command: the call fails before any assertion runs, against any code. Call `echo_json(obj)` directly and read the output with `capsys`, or decorate a wrapper with `@click.command()` and `@click.argument`." And: "`args` is a command line: each element is a string. A dict here reaches the command as text or not at all." Implementer cold pass about 75k (two predicates, six to eight unit tests, one gate). Diff review about 65k. Re-records: none (reasoned: the op body is not in a composed prompt). The refusal reaches every mode that encodes, `tests_missing` included, so a new test of this shape never lands.
- (c) Both. About 100k of implementer and 70k of review, two re-records, and the (a) risk.

## 6. Recommendation

Choose (b). The refusal reaches the seat at the moment of the encode, in every mode, and costs no re-record. The night shows a seat that knows the fault and still writes an unrunnable body, which is a harness fact and a door's job (reasoned: `s153`, `s155`, `s157` completions).

Two notes for the stack, outside frame 110:

- `_02` stays broken under (b), because no seat re-encodes it. The Developer challenged `_03` and `_01` only. A frame on the Developer's choice of test needs its own read (reasoned: section 0).
- `plans/night106-read.md` section 2 says only `_02` failed before af4cbede. The deleted runs at `db.py:580` explain that reading. A correction line is owed there (reasoned: section 0).

## Revision 2, 2026-10-02 14:38, the holder

Decided from the design review (observed: the reviewer's probes on `graph.json`, `runner.py:1580-1595`, `harness.py:171` and night 106's `runs`, 2026-10-02):

1. No new edge. The Tester has `reads code (source)`, ruled 2026-09-24, so `code.source` joins `tester/challenge.tools` as a mode narrowing with a ruling comment, as `answer.tools` has. `tests.load` and `code.probe` are dropped: both need edges the graph does not grant, and `tests.load`'s rows are written for the Developer.
2. The failure text goes by the runner route: the resolver at `runner.py:1580-1595` keeps the whole stored output, at most 2000 characters by `harness.py:171`, for a Tester wake only, and the 700-character tail for every other role, so no other role's prompt moves. The 700 tail of `_03`'s run holds parser frames and not the test's own call line; the full 1999 characters hold the call and `TypeError: object of type 'BadObj' has no len()`.
3. The brief: `challenge.md:3-4` widens past "more, less or something else" to a test that cannot run against any code; after line 6 one conditional line: if the test's last run failed before any assertion ran, read that failure and the code the test calls with `code.source`, and change the line the failure names; a test that calls a function the way a runner calls a command is the test's fault. `base.md:5-6` stays, as answer mode lives with it.
4. No guard in `tests.encode`. Option (b) and the positional-args variant are declined: both need a list of runner callees, which is framework knowledge, and the destination is any small Python repository.
5. Section 0 line 10 is corrected: `_02` raised `KeyError: 'prog_name'`, `_01` `KeyError: slice(None, 1, None)`, `_03` `TypeError: object of type 'BadObj' has no len()`.
6. One new case, `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner`, framework-free: the repository seeds `src/report/export.py` with a plain `echo_json`, the test calls `asyncio.run(echo_json({"a": 1}))`, the seeded red run says `ValueError: a coroutine was expected, got None`; expects one `tests` write whose body calls `echo_json` directly, forbids `criteria`, `items`, `tickets`. Re-records: that case and the two challenge cases. Price: one pass about 90k, one review about 65k, three re-records about 15 GPU minutes.

## Revision 3, 2026-10-02 14:42, the pass 1 implementer

What landed in pass 1 (observed: the four touched test files, 569 passed and 20 skipped, 2026-10-02):

1. `tester/challenge.tools` names `code.source` under a ruling comment. The graph-grant test passes.
2. `tester/challenge.md` widens the claim to a test that cannot run against any code. One conditional line follows "Read the criterion again, cold, and decide." The line names `code.source`.
3. `runner._resolve_refs` takes `role`. `resolve_inbound` passes `wake.role` at both of its calls. A Tester gets the whole stored output, and every other role gets the 700 tail. The other four call sites pass no role, so they keep the tail.
4. `test_runner.py` holds `test_a_tester_reads_the_whole_failure_and_a_developer_reads_the_tail`, with a 1999-character output.
5. `l1_tester.yaml` holds `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner`. The case schema has a body check, so the case expects one `tests` write with `text_includes: ["echo_json({"]` and `text_excludes: ["asyncio.run"]`. The case has no recording yet.

Deviations: the criterion defines "compact" as "with no indentation", because `json.dumps` keeps its default separators and the test must not ask for `{"a":1}`. The key stays `output_tail` for the Tester, though it holds the whole output.
