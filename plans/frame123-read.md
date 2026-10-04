# Frame 123 read: a Tester's fix leaves the old test

Rota workflow: the seats of rota on nights 115, 116 and 117. Read by an agent on Opus for session 419281dc, 2026-10-04 15:24. Sources: `.rota/clickI_night11{5,6,7}.db` (tables `turns`, `tool_calls`, `tests`, `test_runs`, `messages`, `receipts`, `ledger`), `.rota/night117.log`, `rota/roles/api.py`, `rota/core/runner.py`, `rota/core/sandbox.py`, `rota/roles/prompts/tester/`.

## 1. Night 115, s137 and the challenge m44

- m44: developer to tester, `challenge`, refs `["echo_json_compact_3", "tst_echo_json_compact_3"]` (observed: `messages`, 2026-10-04).
- The wake prompt shows the old test whole: id `tst_echo_json_compact_3`, path `tests/test_utils/test_echo_json_3.py`, two functions. `test_echo_json_raises_on_unrecoverable_error` needs `CircularRef` to raise (observed: s137 t1 `user`, 2026-10-04).
- The tool calls at seq 1 to 3 (`batches.expect`, `criteria.load`, `tests.consult`) carry no arguments. They are the runner's pushed reads, not seat calls (observed: `tool_calls`, 2026-10-04).
- t1 call: `tests.encode(id='tst_echo_json_compact_3_fixed', criterion_id='echo_json_compact_3', path='tests/test_utils/test_echo_json_3.py', body=...)`. The body keeps the passing function and replaces the raise test with `test_echo_json_handles_circular_references`, `assert isinstance(parsed, str)` (observed: s137 t1 `completion`, 2026-10-04).
- t1 result: `ERROR tests.encode: tests/test_utils/test_echo_json_3.py is already tst_echo_json_compact_3's file; two tests in one file overwrite each other on disk. Name this one for its own criterion -- tests/test_<what it checks>.py` (observed: s137 t2 `user`, 2026-10-04).
- t2 prose: "I cannot create a second test function in that same file". It then reasons "This implies I should create a *new* file for the *new* test" (observed: s137 t2 `completion`, 2026-10-04).
- t2 call: `tests.encode(id='tst_echo_json_circular', criterion_id='echo_json_compact_3', path='tests/test_utils/test_echo_json_circular.py', ...)`. Result: `OK tests.encode -> {"id": "tst_echo_json_circular"}` (observed: s137 t3 `user`, 2026-10-04).
- t3 call: `batches.expect(batch_id='echo_json_compact_batch')`, OK. t4 is prose: "The original test in `test_echo_json_3.py` remains unchanged". No answer message is sent (observed: s137 turns, 2026-10-04).
- Stored at the end: `tst_echo_json_compact_3` version 1, unchanged, and `tst_echo_json_circular` version 1. Both are on `echo_json_compact_3` (observed: `tests`, 2026-10-04).
- The door names the old test's id. Its only remedy is a new file. Nothing in the door or the prompt says that the same id replaces the old test (observed: door text above, and s137 t1 `system`, 2026-10-04).
- The Tester has no call that removes or retires a test. The `tests` ops are `triage` (`rota/roles/api.py:4288`), `encode` (`:4657`), `load` (`:5561`) and `consult` (`:5648`) (observed: `@op("tests"` grep, 2026-10-04).
- Replacement exists only as `tests.encode` under the old id. The clash query excludes the same id (`api.py:5544`, `id != ?`), so the row is written again at a new version (observed: code, 2026-10-04). Night 116's s183 did this for `tst_cr1_confirm_default_on_eof`, which reached version 2 (observed: `tests` and `receipts`, night 116, 2026-10-04).
- The prompt shows no replace rule. `challenge.md:9-10` says only "fix the test with `tests.encode`". The runner's id paragraph pulls the other way: "An id for something you are creating is yours to invent — make it short and unique, and do not build it out of an id you were shown" (`rota/core/runner.py:299-303`) (observed: s137 t1 `system`, 2026-10-04).

## 2. Night 116, s185

- m90: developer to tester, `challenge`, refs `["cr_2_confirm_default_on_eof", "tst_cr2_confirm_default_on_eof"]` (observed: `messages`, 2026-10-04).
- t1 call: `tests.encode(id='tst_cr2_confirm_default_on_eof_fixed', criterion_id='cr_2_confirm_default_on_eof', path='tests/test_confirm_default_on_eof_no_abort.py', ...)`, with `result = confirm("Proceed?", default_on_eof=True)` and `assert result == False` (observed: s185 t1 `completion`, 2026-10-04).
- t1 result: `ERROR tests.encode: the test chooses 'Proceed?', and nothing in the criterion, its ticket, the glossary or the principal's words says it. That is an assumption, and it is logged where it is made: ledger.log(about_ref='cr_2_confirm_default_on_eof', about_table='criteria', assumption="the test assumes Proceed? where the material is silent") -- then send this encode again unchanged` (observed: s185 t2 `user`, 2026-10-04).
- Site: the invented-literal door, `rota/roles/api.py:5470-5494` (observed: code, 2026-10-04).
- Why it fired on a fix: the literal `'Proceed?'` came from the old test, written by s181. s181 logged one ledger row, `l_2fa2a2d1ca`, about `cr_1_confirm_default_on_eof` only (observed: `ledger` and `receipts`, 2026-10-04).
- In s181 that one row covered all three criteria, because the door reads the session's own ledger writes with no criterion filter (`api.py:5472-5473`) (reasoned: code). In s185 the door reads stored rows `WHERE about_ref = ?` for `cr_2` only (`api.py:5474-5476`), and finds none (reasoned: code, with the ledger rows above).
- "Log the assumption first" requires the call `ledger.log(about_ref='cr_2_confirm_default_on_eof', about_table='criteria', assumption=...)` and then the same encode again.
- `ledger.log` is not in the challenge mode's working set. `rota/roles/prompts/tester/challenge.tools` lacks it, and s185's system prompt lists eight functions and says "Nothing else exists" (observed: file, and s185 t1 `system`, 2026-10-04). `tests_missing.tools` and `answer.tools` carry it (observed: files, 2026-10-04).
- `base.md:22` still tells every Tester that `ledger.log` is reachable "whatever woke you" (observed: s185 t1 `system`, 2026-10-04). A call outside the working set raises `NotInWorkingSet` (`rota/core/sandbox.py:245-249`, `:276-279`) (reasoned: code, not run).
- t2, t3, t4: the seat writes "I must remove this specific string literal" and "I will re-encode the test without the `"Proceed?"` prompt text". Each turn it sends the identical encode, `"Proceed?"` included (observed: s185 t2 to t4 `completion`, 2026-10-04).
- t4 also writes its own `ERROR` lines into the completion. The runner's account ends with "wrote its own tool results" and `NOTE tests.encode has been refused the same way in three turns and will not be accepted again` (observed: s185 t4 `user` and t5, 2026-10-04).
- Why four times: the one call the door names is outside the working set, and the seat never tried it. The seat then followed the door's last words, "send this encode again unchanged", and not its own sentence about removing the literal (reasoned: the turns above).
- Had the log landed, the clash door would fire next. The fix's path is `tst_cr2`'s file under a new id, and the clash check runs after the literal check (`api.py:5543` after `:5470`) (reasoned: code order).
- Stored at the end: `tst_cr1_confirm_default_on_eof` v2 asserts `False`, `tst_cr2_confirm_default_on_eof` v1 asserts `True`. They sit on two criteria, `cr_1` and `cr_2`, not one (observed: `tests`, 2026-10-04). The earlier record called it "one criterion group" (`plans/night116-read.md` section 4, observed 2026-10-04).

## 3. Night 117, bg_2 and bg_1

### bg_2

- Shape: the same left-over sign, and a contradiction across criteria. It is not two contradicting tests on one criterion (reasoned: the rows below).
- At the end `cr_1` has two tests. `tst_confirm_eof` (s211, `tests/test_confirm_eof.py`) and `tst_confirm_eof_cr1` (s213, `tests/test_confirm_eof_cr1.py`) both call `confirm("Are you sure?", default_on_eof=True)` and assert `result == "yes"` (observed: `tests` and `receipts`, 2026-10-04).
- The two `cr_1` tests agree. `tst_confirm_eof_cr1` also calls `closed_stdin.close()` and fails against any reader: `ValueError: I/O operation on closed file` at `src\click\termui.py:105` (observed: `test_runs`, commit `9868bf795c`, 2026-10-04).
- `tst_confirm_eof_cr2` to `tst_confirm_eof_cr6` (s221, `tests_missing`) assert `result == True` for the same call. No code returns both `"yes"` and `True` there (observed: `tests`; reasoned: `"yes" != True`).
- Red at the one head `9868bf795c`: 7 of 41, all seven batch tests (observed: `test_runs`, 2026-10-04).
- s212 (Developer) read `assert result == "yes"` against `default: bool | None = False` and sent m118, `challenge`, refs `["cr_1", "tst_confirm_eof"]` (observed: s212 turns and `messages`, 2026-10-04).
- s213 (Tester, 24 turns) t1: `tests.encode(id='tst_confirm_eof_fixed', criterion_id='cr_1', path='tests/test_confirm_eof.py', ...)`. Result: the clash door, `tests/test_confirm_eof.py is already tst_confirm_eof's file; ...` (observed: s213 turns, 2026-10-04).
- s213 t2: `tests.encode(id='tst_confirm_eof_cr1', ..., path='tests/test_confirm_eof_cr1.py', ...)`, OK. The body asserts `"yes"` with no `default=` argument, so the stored "fix" changes no assertion (observed: s213 t2 call, 2026-10-04).
- s213 t9 and t15: `tests.encode(id='tst_confirm_eof', criterion_id='cr_1', path='tests/test_confirm_eof.py', ...)` with `confirm("Are you sure?", default="yes", default_on_eof=True)`. That is the right move: the old id, a real fix (observed: s213 calls, 2026-10-04).
- Both were stopped by the in-session guard: `OK tests.encode -> {"id": "tst_confirm_eof_cr1", "unchanged": true, "note": "cr_1 already has a test this session (tst_confirm_eof_cr1), and one criterion takes one. Nothing was written. If that test is wrong, this is not the session that discovers it."}` (observed: s213 t10, t16 `user`, 2026-10-04).
- Site: `rota/roles/api.py:5531-5538`. It counts the session's writes on the criterion and ignores whether the new id is an existing row (observed: code, 2026-10-04).
- s213 t13, t18 to t23: more encodes under `tst_confirm_eof_fixed` and `tst_confirm_eof_v2`. Each got the same note, then `asked three times this session`, then `NOTE tests.encode has been refused the same way in three turns` (observed: s213 turns, 2026-10-04). The t9 body still closed the stream, so it would have stayed red (reasoned: the `ValueError` run above).
- The Developer's escalations: s214 sent m119, `escalate`, refs `["cr_1", "tst_confirm_eof"]`. s215 (Architect) sent m120, `challenge` to the Vision Keeper (observed: `tool_calls` and `messages`, 2026-10-04).
- s216 (Vision Keeper) authored `d_b144845f04`, which says only that "the test `test_confirm_eof.py` is failing" and "a need to revisit the implementation", and sent `msg.reopen_developer` (observed: `decisions` and `tool_calls`, 2026-10-04).
- s217, s218, s222, s223, s224 each sent `msg.challenge_tester` and `msg.escalate_architect` on `["cr_1", "tst_confirm_eof"]`. Both were refused as repeats: `you sent challenge to tester on exactly these refs already (m118)` and `you sent escalate to architect on exactly these refs already (m119) and they answered (answered) with no row beyond your own refs` (observed: `tool_calls`, s217 t2 and t3 `user`, 2026-10-04).
- Why the same refs six times: the red test the Developer can read first is still the old `tst_confirm_eof`. The Tester's reply landed under another id, so the Developer's one ref never changed (reasoned: the rows and calls above).
- The Architect did one thing with the escalations: one challenge to the Vision Keeper, m120. That produced an empty decision. No later escalation reached it, because each was refused at the door (observed: `messages` m119 to m120 and `tool_calls`, 2026-10-04).
- The log: `CYCLE: period 1, rounds 3, wakes: developer|tick:tests_failing|attempt 4|["bg_2"]` (observed: `night117.log:100`, 2026-10-04).

### bg_1

- bg_1 parked: `do:park: deferred bg_1; its ladder is spent` (observed: `night117.log:88`, 2026-10-04). Red at head `154ddecf8a`: 5 of 38 (observed: `test_runs`, 2026-10-04).
- The causes are not a contradiction. `inh_55974267` (`tests/test_imports.py`, a project test) fails on `assert 'json' in {...}`, the Developer's own import (observed: `test_runs`, 2026-10-04).
- `inh_echo_json_01`, `_02`, `_03` call `echo_json` through a runner and fail on `SystemExit(2)`, `Got unexpected extra argument` (observed: `test_runs`, 2026-10-04).
- The left-over sign is present. s142 (Tester, challenge m64) sent `inh_echo_json_03_fixed` six times and met the literal door on assertion messages. At t6 and t7 it met the clash door, and at t8 it wrote `inh_echo_json_compact_3` at a new path (observed: s142 calls, 2026-10-04).
- `inh_echo_json_compact_3` holds `assert True` and fails with `NameError: name 'click' is not defined`. `inh_echo_json_03` stayed. The two do not contradict. The new one fails against any code (observed: `tests` and `test_runs`, 2026-10-04).

## 4. The common mechanism

- When a Tester accepts a challenge, it writes the fix under a new id, `<old id>_fixed`. The system then sends it to a new file, and the old test stays and keeps running. It happened in 4 of 4 challenge sessions read: s137, s185, s213, s142 (observed: section 1 to 3 calls, 2026-10-04).
- (iii) The brief's wording: yes. `challenge.md:9-10` never says to keep the test's id. `runner.py:299-303` tells the seat to invent ids and not to build them from a shown id (observed: files, 2026-10-04).
- (i) The door's text: yes. The clash door at `api.py:5550-5554` names the old test's id and offers only a new file. The seat followed that remedy at the next turn in 3 of 3 cases: s137 t2, s213 t2, s142 t8 (observed: turns, 2026-10-04).
- (ii) A missing call: partly. No call retires a test. The replace exists, `tests.encode` under the old id, but no prompt says so (observed: section 1). Night 116 adds a door that names `ledger.log`, which the challenge working set lacks (observed: section 2). Night 117 adds a guard at `api.py:5531-5538` that blocks the replace after a first write (observed: section 3).
- (iv) The seat ignores a fact: not the main cause. The old id is in the prompt, but nothing says that reusing it replaces the test (reasoned: sections 1 and 3).
- One (iv) residue: s185 t2 to t4 says it will remove `'Proceed?'` and sends the same body four times (observed: section 2). That belongs to the missing `ledger.log` and is not frame 123's left-over mechanism (reasoned).
- Interview: not needed before a door change, because the seat acts on the door's remedy each time (reasoned: 3 of 3 above). Before a brief change, interview night 115 `--sid s137 --seq 1`: why `tst_echo_json_compact_3_fixed` when the prompt shows `tst_echo_json_compact_3`.
- For the s185 residue, interview night 116 `--sid s185 --seq 2` only if the `ledger.log` frame is taken (reasoned).

## 5. Options for the smallest fix

1. Door. Site: `rota/roles/api.py:5550-5554`. When the clashing row encodes the same `criterion_id`, the refusal says: `<path> is <old id>'s test of the same criterion. To fix that test, send this encode again with id='<old id>'. The same id replaces it.`
   - What changes for the seat: the next encode goes to the old id, and the row is replaced in place.
   - Nights it would have changed: night 115 s137 t2, night 117 s213 t2 and s142 t7. It would not change night 116, where the door was never reached (reasoned: sections 1 to 3).
   - Pin: a sandbox test in `tests/rota/test_t0_sandbox.py`, beside `test_one_criterion_gets_one_test_in_a_session` (`:378`). Use challenge mode with row `t1` on `c1` at `p.py`. An encode of `t1_fixed` at `p.py` must name `id='t1'`, and an encode of `t1` must land one row at version 2. Re-record night 115 s137 as a case.
2. Brief. Site: `rota/roles/prompts/tester/challenge.md:9-10`, plus one exception in `rota/core/runner.py:299-303`. Line: "Fix the test with `tests.encode` under its own id and path from the message. The same id replaces it. A new id leaves the old test running beside the fix."
   - What changes for the seat: the first encode goes to the old id, so the clash door never fires.
   - Nights it would have changed: all four first encodes, s137 t1, s185 t1, s213 t1, s142 t1. Night 116 still meets the literal door (reasoned).
   - Pin: recorded cases from s137 t1 and s213 t1. An interview comes first (section 4).
3. Code. Site: `rota/roles/api.py:5531-5554`. In challenge mode, an encode on the challenged test's criterion writes over the challenged id, whatever id it carries. The guard at `:5531` also passes an encode whose id is an existing row of that criterion.
   - What changes for the seat: nothing to read. The new-id fix becomes a replacement.
   - Nights it would have changed: night 115 s137 t1, night 117 s213 t1 and s142 t6. It would not change night 116 (reasoned).
   - Pin: two sandbox tests in `tests/rota/test_t0_sandbox.py`. First, a challenge-mode encode of `t1_fixed` on `c1` leaves one row, `t1`, version 2. Second, after a first write, an encode of an existing id of the criterion still lands.

- Recommendation: option 1. The deciding fact: the seat obeyed the clash door's remedy at the next turn in 3 of 3 cases. The guard at `:5531` then never fires, because no new id lands first (reasoned).
- Not in any option: night 116's door that names `ledger.log` in a mode without it (`challenge.tools`, `api.py:5488-5494`), and the ledger lookup by `about_ref` that misses a literal inherited from a sibling criterion. These are a separate frame (reasoned: different site, different sign).

## 6. Baselines

| Night | `tests_failing` batches | Given up | Two tests of one criterion that contradict | Left-over test on one criterion at give-up | Contradiction across criteria |
|---|---|---|---|---|---|
| 115 | 1, `echo_json_compact_batch` | 1 | 1 of 1 | 1 of 1 | 0 |
| 116 | 2, `bg_1` merged, `bg_2` | 1 | 0 of 2 | 0 of 2, the fix never landed | 1 of 2, `cr_1` against `cr_2` |
| 117 | 2, `bg_1` parked, `bg_2` | 2 | 0 of 2 | 2 of 2 | 1 of 2, `cr_1` against `cr_2` to `cr_6` |

(observed: `sessions` wake kinds, `batches`, `test_runs` at each head, `tests` grouped by criterion, 2026-10-04.) The frame's own line, one criterion that contradicts, falls to 0 on nights 116 and 117 without a fix. A ratio on left-over tests tracks the mechanism better: 1 of 1, 0 of 2, 2 of 2 (reasoned).

## 7. Night 117 Developer wakes, the `[tests.load]` block

- s152 (bg_1): block 12,194 characters. It holds 4 rows of "the batch's tests, not passing", each 1,799 to 3,186 characters, and the start of "the project's own tests, not passing". The largest row is `inh_echo_json_compact_3`, 3,186 (observed: s152 t1 `user`, 2026-10-04).
- s222 (bg_2): block 10,933 characters. It holds the challenge history (m118, m119) and 5 rows, the fifth cut. Each row is a body of 565 to 961 characters plus the harness output, `said` and `raised at`. The largest are `tst_confirm_eof_cr1` at 3,247 and `tst_confirm_eof` at 2,871 (observed: s222 t1 `user`, 2026-10-04).
- s223 and s224: block 10,771, 4 rows. Every wake ends `CUT your wake: 10,312 of 28,376` (s222), `10,474 of 28,538` (s223, s224) or `20,388 of 38,452` (s152). `[tests.load]` is the last block, so the wake is cut before any `[code.source]` block (observed: block heads, 2026-10-04; reasoned: order).

## Not read

- Night 115 s139 to s141 turns, beyond the record in `plans/night115-read.md`.
- Night 116 s186, s187, s190, and the Architect s188.
- Night 117 s211 and s221 turns, s222 to s224 beyond their calls, s215 and s216 beyond their calls, and the bg_1 Tester sessions s132, s138, s140, s145, s148, s163.
- The project checkout `C:/Users/roman/rota_night117`. No test was run against code.
- The `NotInWorkingSet` refusal for `ledger.log` in challenge mode was not run.
