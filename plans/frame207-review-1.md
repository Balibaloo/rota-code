# Frame 207, pass 1: diff review

Verdict: **STANDS**. 0 high findings and 6 low findings, one of them outside the points. The worktree is `C:/Users/roman/rota_rv207`, detached at f8ae0140. The diff is `git diff fa508ab7 f8ae0140`. Rota workflow unless marked. Read and probed 2026-10-11.

## (a) Verdicts on the points

1. The filter: holds. On night 140's database, `inh_f3b0c3db` gets `own=True`, and a project test gets `own=False` (observed).
2. The base run: holds. A fresh start records 37 rows in 2 pytest children. A resumed batch records none. All four sentences read the record (observed).
3. The red base: the escalation door admits the call, and the call lands. The Architect has no tool that clears a red test (observed, finding 3).
4. The cost: 2 children and 7.7 s on click's base. A hang can block the batch start for up to 4080 s on click (finding 2).
5. The deviation: for a batch that starts at this commit, no path shows a red inherited test before the record exists. A batch from before this commit gets the "no base run" text, which still blames the diff (finding 5).
6. Outside: the four touched files and the Developer door files pass. One red, `test_invoke_door.py::test_a_session_with_no_batch_reads_the_root`, is red at fa508ab7 too (finding 6).

## Point 1. The filter

Probe `p1.py`. It opens a copy of `clickI_night140.db`, imports rota from the worktree, and calls `tester_paths` and `_own` for bg_2. It then calls `_run_one` on a `git archive 3901a51` export of bg_2's base, with bg_2's venv and `PYTHONPATH` on the export's `src`.

```
rota from C:/Users/roman/rota_rv207/rota/__init__.py
tester_paths(bg_2) = ['tests/test_utils/test_confirm_closed_stdin.py', 'tests/test_utils/test_confirm_false_stdin_aborts.py', 'tests/test_utils/test_confirm_open_stdin.py']
bg_2 tests 39 own True: ['inh_36675d53', 'inh_495fc34e', 'inh_f3b0c3db', 'tst_v1_show_python', 'tst_v3_show_python']
inh_f3b0c3db own = True
a project test inh_01fdb170 tests/test_utils/test_echo_via_pager.py own = False
own True -> pass | 1 passed in 0.04s
own False -> fail | 1 failed in 0.15s
project test own False -> pass | 61 skipped, 1000 deselected in 0.13s
```

The three bg_1 Tester files take the batch filter. The 34 project files keep the project filter. Under the new `_own`, night 140's red test passes at bg_2's base. Under the old `own=bool(criterion_id)`, it fails.

## Point 2. The base run, and the sentences that read it

Probe `p2.py`. It inserts a fresh batch `bg_9` (no head) and a resumed batch `bg_8` (head `abc`) into the database copy, on the base export, and counts `execute.run` calls.

```
fresh: found 37 seconds 7.7
pytest children: 2 [(3, True, 360), (34, False, 4080)]
recorded 37 red {}
resumed: base_run None children 0
second start of bg_9: children 0
```

A fresh start records once, under `config` key `base_run:bg_9`. A resumed batch records none. A second start of the same batch does not run again.

The sentences, before (fa508ab7) and after (f8ae0140). A grep of `rota/` for "passed before", "change broke" and "diff broke" finds no fifth site. `developer/tests_failing.md` makes no claim of the kind.

1. The push, `runner.py:2908`. Before: `{n} test(s) with no criterion are the project's, and they passed before this batch. Your diff broke them. Read code.diff below and restore what it changed; a challenge has no side here`. After, with a red base: `1 test(s) with no criterion are the project's, and the base run at this batch's start found inh_00000000 red too. The base run said: DeprecationWarning: 'isolated_filesystem' is deprecated and will be removed in Click 9.0. Your diff did not break it, and the fix is not yours. Send msg.escalate_architect(refs=['inh_00000000'])`. With a green base, the old sentence stays to the byte (test `test_the_fix_wake_keeps_its_sentence_when_the_base_run_passed`).
2. The single-test hint, `sandbox.py:1155`. Before: `. {id} has no criterion: it is the project's own test and it passed before this batch. A challenge has no side there. Read code.diff and restore what your change broke`. After: `. inh_00000000 has no criterion: it is the project's own test and the base run at this batch's start found inh_00000000 red too. The base run said: ... Send msg.escalate_architect(refs=['inh_00000000'])`.
3. The hint for all failing tests, `sandbox.py:1195`. Before: `. The {n} failing test(s) have no criterion: they are the project's own and passed before this batch. A challenge has no side there. Read code.diff and restore what your change broke`. After (probe `test_p5.py::test_fourth_sentence`, a challenge with `refs=['cx']`, a criterion with no test): `... yours names no test. The 1 failing test(s) have no criterion: they are the project's own and the base run at this batch's start found inh_00000000 red too. The base run said: ... Send msg.escalate_architect(refs=['inh_00000000'])`. No test in the diff covers this site (finding 4).
4. The owner refusal, `sandbox.py:1225`. Before: `{id} has no criterion: it is the project's own test and it passed before this batch. A challenge has no side there. Read code.diff and restore what your change broke`. After: `inh_00000000 has no criterion: it is the project's own test and the base run at this batch's start found inh_00000000 red too. The base run said: ... Send msg.escalate_architect(refs=['inh_00000000'])`.

Probe `test_p5.py::test_mixed`, one project test red at the base and one green:

```
MIXED PUSH: 2 test(s) with no criterion are the project's, and the base run at this batch's start found inh_00000000 red too. ... Send msg.escalate_architect(refs=['inh_00000000']). Inh_00000001 passed before this batch. Read code.diff and restore what your change broke
```

The id `inh_00000001` becomes `Inh_00000001` (finding 1).

## Point 3. A test red at the base

Probe `test_p3.py`, on `_f207_db(tmp_path, [], "fail")` from `test_runner.py`. The challenge is refused with the new text. Then `sb.call("msg.escalate_architect", refs=["inh_00000000"])` runs for real.

```
ESCALATE -> {'id': 'm1', 'to': 'architect', 'verb': 'escalate'}
```

The door admits the exact call. The diff's own test also dry-runs the call and reads `admitted`.

Probe `test_p3b.py` writes the outbound message into `messages` and reads `predicates.all_wakes`.

```
ALL WAKES [('architect', 'message', (), None), ('developer', 'tick:tests_failing', ('b1',), None), ('terminologist', 'tick:criteria', ('echo_json',), None)]
```

The Architect wakes on the message. Its `escalate.tools` holds `model.amend`, `decisions.author`, `msg.answer_developer`, `msg.challenge_vision_keeper`, `msg.propose_vision_keeper`, `findings.find`, `msg.report_liaison` and reads. None of these tools changes a test, a filter or a test run. `lifecycle.mergeable` refuses while any run at the head is not `pass` (`lifecycle.py:484-488`). So a test red at the base still blocks the merge for ever.

The Developer's `tick:tests_failing` also fires while the escalation is open. `predicates.tests_failing` (`predicates.py:902-931`) has no escalation guard. Each such wake reads "You escalated these refs already. End the session with no call" until the tick quarantines. This is frame 114's wall. The pass moves the seat to an honest call, and it does not open a route (finding 3).

## Point 4. The cost

- A fresh start with inherited tests runs one pytest child per filter group. That is one child when no merged Tester file is in the tree, and two when one is. Click's base: 2 children, 7.7 s (observed, probe `p2.py`).
- A red group runs again file by file through `_run_one`. That adds one child for every file in the group, green files included. On click's project group that is 34 more children.
- A resumed batch runs none.
- The timeout: `harness.py:335` passes `timeout=timeout * len(group)`, with `timeout=120`. The probe recorded 360 s for the own group and 4080 s for the project group. A hang in one test holds the group child for 4080 s. The per-file reruns then wait 120 s more on the hanging file.
- `lifecycle.start` runs inside `loop.step` (`loop.py:318`) before the session, so the whole loop waits. The batch's own `harness.run` waits at most 120 s per file (finding 2). `execute._local` kills the child on `TimeoutExpired`, so the wait ends.

## Point 5. The deviation: the record at the next start

The record is written in `lifecycle.start`, before any session of the batch. `harness.run` and every door that reads the record come after a commit. So for a batch that starts at this commit, no path shows a red inherited test before the record exists (reasoned, from `lifecycle.py:116-127` and `loop.py:318`).

Two paths show the text with no record:

- A batch that started before this commit and resumes with a head. Probe `test_p5.py::test_night140_db` on the night 140 copy: `NIGHT140 bg_2: no base run of inh_f3b0c3db is on record. A challenge has no side there. Read code.diff and find what your change broke`. Under point 1's change, this test now passes in bg_2, so this door does not fire for it.
- A deferred batch with no commit that finds a new test file when it resumes. The record exists, so the new row has none. This path is rare (reasoned).

The "no base run" text still tells the seat to find what its change broke. That text is the old blame with no evidence (finding 5). I agree with the deviation itself. At the merge, the record would describe the old batch's filter and not the next batch's tree.

## Point 6. The test files

```
ROTA_MODEL=qwen3:8b python -m pytest tests/rota/test_caught.py tests/rota/test_runner.py tests/rota/test_night46_context.py tests/rota/test_developer.py tests/rota/test_developer_expect.py tests/rota/test_revert_door.py tests/rota/test_invoke_door.py tests/rota/test_prints_door_kind.py tests/rota/test_offers_followed.py tests/rota/test_row_route.py -q -n 0 -p no:cacheprovider
FAILED tests/rota/test_invoke_door.py::test_a_session_with_no_batch_reads_the_root
1 failed, 428 passed, 4 xfailed in 211.81s
```

The red is `Failed: DID NOT RAISE <class 'ValueError'>` at `test_invoke_door.py:375`. On a `git archive fa508ab7` export the test is red the same way, `1 failed in 1.39s`. The diff touches neither `tests.encode` nor `api.py`. So the red is not this pass's red (finding 6).

## (b) Findings

1. `rota/core/sandbox.py:1476`. Low. CONFIRMED: probe `test_mixed` shows `Inh_00000001 passed before this batch`. The join capitalises the first letter of every part after the first. The "passed" part starts with an id, so the id changes and no ref matches it. Fix: start that part with a word, for example `the base run found {ids} green`.
2. `rota/core/harness.py:335`. Low. CONFIRMED for the number: the probe recorded a 4080 s timeout for the 34-file group of click. PLAUSIBLE for the hang: no hanging test was run. The batch start, and the loop with it, waits up to about 70 minutes on one hanging test. Fix: bound the group timeout, for example to `timeout + 10 * len(group)`.
3. `rota/core/predicates.py:902-931`, `rota/roles/prompts/architect/escalate.tools`, `rota/core/lifecycle.py:484-488`. Low, the wall of frame 114. CONFIRMED: probe `test_p3b.py` shows the Architect wake and a Developer `tick:tests_failing` wake while the escalation is open. The Architect holds no tool that clears a red test, and the merge gate counts the red row. Fix: a new frame that lets a test red at the base not block the merge, or gives the Architect a lever, and guards `tests_failing` on an open escalation.
4. `rota/core/sandbox.py:1195`. Low. CONFIRMED by a read of the diff: no new test reaches the hint for all failing tests. Probe `test_fourth_sentence` shows the text is right today. Fix: add a door test for a challenge with a criterion that has no test, on a red base.
5. `rota/core/sandbox.py:1473-1475`. Low. CONFIRMED: probe `test_night140_db` shows `no base run of inh_f3b0c3db is on record. ... find what your change broke`. The sentence presumes that the diff broke a test that rota never ran at the base. Fix: say that rota cannot tell whether the diff broke the test, and name `code.diff` and the escalation as the two calls.
6. Outside the points. `tests/rota/test_invoke_door.py:375`. Low. CONFIRMED: red at f8ae0140 and at fa508ab7 alike. Fix: check the red set of the gate for this test, and push a frame when the gate does not know it.

PLAUSIBLE, not counted: `record_base_run` trusts a green group run. A file that passes in a group and fails alone gets `pass` at the base. The door then says "passed before this batch" falsely, because the batch runs each file alone. Fix, when a night shows it: record from per-file runs.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/59bdd13a-98f3-4dda-ba43-071cb487b114/scratchpad/rv207/`. Each probe imports rota from the worktree. No probe wrote to a tracked file or to the database of the night.

- `base/`: `git archive 3901a51` of `D:/repos/_AI/sample_repos/clickI`, the base of bg_2.
- `clickI_night140.db*`: a copy of `D:/repos/rota/.rota/clickI_night140.db` with its WAL.
- `p1.py`: `tester_paths`, `_own` and `_run_one` on bg_2 and the base export (point 1).
- `p2.py`: `inherit` on a fresh batch, a resumed batch and a second start, with a count of `execute.run` calls and their timeouts (points 2 and 4).
- `test_p3.py`: the challenge refusal and a real `msg.escalate_architect` call on `_f207_db` (point 3).
- `test_p3b.py`: the escalation written to `messages`, then `predicates.all_wakes` (point 3).
- `test_p5.py`: the fourth sentence, the mixed base, the missing record, and the night 140 copy (points 2 and 5).
- `old/`: `git archive fa508ab7` of `rota` and `tests`, for the red in point 6.
- The test run of point 6, from the worktree root, as quoted there.

## (d) Usage

About 100k input tokens, about 14k output tokens, about 114k total, against an 80k cap. The harness line is the authority. No sub-agent. No model call.
