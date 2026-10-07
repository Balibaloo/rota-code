# Frame 170, the merges read: what a pass and a finding prove

**Read of 2026-10-07 05:13, meta workflow. The seats it reads are the rota workflow.**

**A Critic pass proves only that the Critic emitted it.** On 10 of 10 merges of nights 114 to 128, the Critic sent its verdict in its first turn with 0 read calls, claimed `encodes=True` on every criterion it named, and wrote `reason=''` (observed: the turns of the 10 Critic sessions, `crit.py`, 2026-10-07). On a replay of two recorded Critic turns with one criterion's code taken out of the diff, the seat sent `pass` in 2 of 2 runs, and named no criterion (observed: `interview_turn.py` on database copies, 2026-10-07 05:10). The Architect's findings name `k0` in 18 of 18 rows, because no constraint binds the files these batches change, except on night 118, where 11 bound constraints were pushed and none was checked. Two findings were lost to an id reuse, on 2 of the 2 nights that merged twice.

Sources: the night databases `D:/repos/rota/.rota/clickI_night<n>.db`, opened `mode=ro`. Scripts: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/6cc11c8b-d798-4ba5-a74f-23bdd33674c1/scratchpad/n170/` (`m1.py`, `crit.py`, `tst.py`, `tst2.py`, `arch.py`, `mkcopy.py`, and the outputs `c<n>.out`, `r1*.out`).

## 1. The merges

10 batches have status `merged` on the 8 nights (observed: `batches`, `verdicts`, `findings`, `receipts`, `m1.py`, 2026-10-07).

| Night | Batch, item | Head | Critic | `verdicts.emit`, verbatim | Architect | Findings: id, constraint, grain, the diff touches the grain |
|---|---|---|---|---|---|---|
| 114 | bg_2, confirm_with_default_on_eof | 24feb33d | s202 | `verdicts.emit(batch_id='bg_2', result='pass', failed_criterion=None, reason='', diff_ref='')` | s203 | f1 k0 `src/click/termui.py` yes. f2 k0 `tests/test_defaults.py::test_lookup_default_returns_hides_sentinel` no. f3 k0 `tests/test_defaults.py::test_default_map_source` no. f4 k0 `src/click/utils.py` no |
| 116 | bg_1, echo_json | 88a11ce7 | s149 (answer wake) | `verdicts.emit(batch_id='bg_1', result='pass', failed_criterion=None, reason='', diff_ref='src/click/utils.py')` | s150 | f1 k0 `src/click/utils.py` yes |
| 118 | echo_json_group, echo_json | 0133968b | s144 | `verdicts.emit(batch_id='echo_json_group', result='pass', reason='', diff_ref='')` | s145 | f1 k0 `src/click/utils.py` yes. f2 k0 `src/click/__init__.py` yes |
| 119 | bg_2, confirm_default_on_eof | cc96a22b | s218 | `verdicts.emit(batch_id='bg_2', result='pass', reason='', diff_ref='')` | s219 | f1 k0 `src/click/termui.py` yes. f2 k0 `tests/test_defaults.py` no |
| 120 | bg_1, echo_json | a60ed772 | s148 (answer wake) | `verdicts.emit(batch_id='bg_1', result='pass', failed_criterion=None, reason='', diff_ref='src/click/utils.py')` | s149 | f1 k0 `src/click/utils.py` yes, **lost**: s181 wrote `f1` version 2 for bg_2 |
| 120 | bg_2, confirm_with_default_on_eof | 0a171187 | s180 | `verdicts.emit(batch_id='bg_2', result='pass', reason='', diff_ref='')` | s181 | f1 k0 `src/click/termui.py` yes. f2 k0 `tests/test_defaults.py` no |
| 126 | bg_2, confirm_default_on_eof | a0d92ad4 | s225 | `verdicts.emit(batch_id='bg_2', result='pass', reason='', diff_ref='')` | s226 | f1 k0 `src/click/termui.py` yes. f2 k0 `tests/test_defaults.py` no |
| 127 | bg_3, version_option_show_python | 24726e9f | s279 | `verdicts.emit(batch_id='bg_3', result='pass', reason='', diff_ref='')` | s280 | f123 k0 `src/click/decorators.py` yes |
| 128 | bg_1, echo_json | cb31ea31 | s142 | `verdicts.emit(batch_id='bg_1', result='pass', reason='', diff_ref='')` | s143 | f1 k0 `src/click/utils.py` yes, **lost**: s196 wrote `f1` version 2 for bg_2 |
| 128 | bg_2, confirm_with_default_on_eof | 5f293c2a | s195 | `verdicts.emit(batch_id='bg_2', result='pass', failed_criterion=None, reason='', diff_ref='')` | s196 | f1 k0 `src/click/termui.py` yes. f2 k0 `tests/test_defaults.py` no |

- `reason=''` on 10 of 10 verdicts. `diff_ref` is not empty on 2 of 10, both answer wakes (observed: the table).
- `k0` is the constraint of 18 of 18 finding rows filed. Its text: `Nobody has read this area yet, so what it is committed to is unknown. Treat a change here as touching commitments that have not been written down: it is not a prohibition, it is the absence of the information that would let anyone say. Surveying the area removes it from this constraint, including a survey that finds nothing — that is a result.` (observed: `constraints`, night 114).
- 11 of 18 rows name a file the diff changes. The other 7 name `tests/test_defaults.py` or `src/click/utils.py`, which the diff does not change. Each of the 7 is in the batch's `batches.expect` list, `expected to touch`, which the push shows the Architect (observed: `arch.py`). `findings_find` checks the grain against the diff only on `violated` (reasoned: `rota/roles/api.py:2849-2856`).
- 2 of 18 rows were lost. On night 120 and night 128 the second Architect wrote `f1` again, and the receipt shows `f1` version 2 by that session. So 2 of 10 merged batches end with no finding row. Night 120 and night 128 are the 2 nights of 8 with two merges, so the loss is 2 of 2 where it can happen (observed: `receipts`). `findings_find` appends the id the seat names and does not read an existing row of that id (reasoned: `rota/roles/api.py:2875-2894`). The pushed `findings.load` is per batch and shows `[]`, so the second seat cannot see the first row (observed: s196's prompt).

## 2. What each Critic read

All 10 Critics got the same push: `criteria.load`, `tests.load`, `code.read` and its `diff` (observed: the first prompt of each, `crit.py`). `code.read` is "Critic's entire view of the implementation", the diff hunks only, and the review mode's tools have no `code.source` (observed: `rota/roles/api.py:9358`, `rota/roles/prompts/critic/review.tools`, 2026-10-07).

| Night, Critic | Calls before the verdict, in order, and what came back | Diff, criteria | Order of verdict and prose | What the prose says of the tests | Do the stored tests run the path each criterion names |
|---|---|---|---|---|---|
| 114 s202 | 3 `claim_encodes` True, `OK` each. `emit` pass, `OK` | both pushed | verdict in turn 1, prose from turn 2 | none, it reads the diff | 3 of 3 call `confirm` on EOF. `tst_confirm_eof_raises_exception` puts `assert False` inside `try ... except Exception`, so it passes whether or not `confirm` raises (reasoned: the body) |
| 116 s149 | 1 `claim_encodes` True on `echo_json_compact_3`, `OK`. `emit` pass, `OK` | both pushed | prose first, in turn 1 | `The test passed` | 3 of 3 call `echo_json` and assert its output or its `TypeError` |
| 118 s144 | 6 `claim_encodes` True, `OK` each. `emit` pass, `OK` | both pushed, 2 files | verdict in turn 1 | none | 6 of 6 call `echo_json`. `_2` (no decorators or context) and `_6` (uses the `json` module) name a property that an assertion on output cannot see (reasoned: the bodies) |
| 119 s218 | 4 `claim_encodes` True, `OK` each. `emit` pass, `OK` | both pushed. `tests.load` cut, 512,706 of 532,706 characters not shown | verdict in turn 1 | none, a check mark per criterion on the diff | 4 of 4 call `confirm` on EOF with the flag |
| 120 s148 | 1 `claim_encodes` True on `echo_json_compact_3`, `OK`. `emit` pass, `OK` | both pushed | prose first, in turn 1 | the Tester `confirmed` the test | 3 of 3 call `echo_json` |
| 120 s180 | 3 `claim_encodes` True, `OK` each. `emit` pass, `OK` | both pushed | verdict in turn 1 | `The tests ... all pass, confirming the implementation works as expected` | 1 of 3. `cr_2_confirm_eof_state`, `must detect the EOF state on stdin before attempting to prompt`: the test asserts `isinstance(result, bool) or result is None`. `cr_3_confirm_eof_default_map`, `returns the value from the default map`: the test body is the body of `cr_1`'s test, with no default map |
| 126 s225 | 2 `claim_encodes` True, `OK` each. `emit` pass, `OK` | both pushed | verdict in turn 1 | a red `test_imports.py` is `unrelated to the diff and was already failing` | 2 of 2 criteria, 3 test functions, call `confirm` on EOF or read its signature |
| 127 s279 | 3 `claim_encodes` True, `OK` each. `emit` pass, `OK` | both pushed. `tests.load` cut, 67,511 of 87,511 characters not shown | verdict in turn 1 | `Version info is appended and derived from runtime inspection when show_python=True (tst_vo_true)` | 0 of 3. No test passes `--version` (observed: `plans/night127-read.md`, section 6) |
| 128 s142 | 3 `claim_encodes` True, `OK` each. `emit` pass, `OK`. Then 5 turns that repeat the 4 calls into refusals | both pushed | verdict in turn 1, prose from turn 2 | none, it reads the diff | 3 of 3 (observed: `plans/night128-read.md`, section 2) |
| 128 s195 | 3 `claim_encodes` True, `OK` each. `emit` pass, `OK` | both pushed | verdict in turn 1 | none, a check mark per criterion | 3 of 3 (same source) |

- 0 of 10 Critics sent a read call in any turn. 10 of 10 had the diff and the criteria in the first prompt, so no read was needed to see them (observed: the table).
- 8 of 10 sent the verdict in a first turn that holds only calls. The reasoning came in a later turn, after the verdict had landed, and no row stores that prose. The 2 others were answer wakes on one challenged criterion (observed: `crit.py`, `clen` per turn).
- `claim_encodes` came back `True` for 29 of 29 claims. No claim was `False` (observed: the table).
- Night 127's s279 passed a diff whose new path raises `NameError`. The diff hunks begin at line 424 of `src/click/decorators.py`, so the import block was not in front of the seat, and the seat has no call that reads it (reasoned: the pushed diff and `review.tools`). Its prose says that `tst_vo_true` confirms the append. That test asserts only `exit_code == 0` on a bare invoke (observed: the body in s279's prompt).
- Night 120's s180 named the gap in its own prose, `While the detection happens during the read attempt`, and passed `cr_2_confirm_eof_state` (observed: s180, turn 2). The diff catches `EOFError` after the read, so the merge does not meet `cr_2` as written. The diff returns `default` and reads no default map, so it does not meet `cr_3` as written (reasoned: s180's pushed diff).
- Night 128's s196, the lost `f1`, is an Architect case. It is in sections 1 and 3.

## 3. What each Architect read

The structural-review push keeps the rows of `model.consult` whose constraint reaches a file of the diff, and always `k0` (observed: `rota/core/runner.py:2514-2545`, 2026-10-07). A constraint reaches a file when a binding's grain is that file or a parent directory of it. A constraint with no binding reaches every diff (observed: `_reaching_constraints`, `rota/roles/api.py:2747-2772`). `k0` has 0 bindings on all 8 nights, so it is in every push (observed: `arch.py`). The `model.consult` op itself filters on `constraints_for_grains`, with the same rule on equal grains (observed: `rota/roles/api.py:2931-2953`, `rota/core/scheduler.py:1937-1973`).

| Night, Architect | Diff files | Pushed `model.consult` | Own `model.consult` call, grains, result | Constraints bound to a diff file | Findings |
|---|---|---|---|---|---|
| 114 s203 | `termui.py` | `k0` only | 5 grains from `expected to touch`, `k0` only | 0 | 4, all `k0` |
| 116 s150 | `utils.py` | `k0` only | none | 0 | 1, `k0` |
| 118 s145 | `__init__.py`, `utils.py` | **12 rows: `k0` and 11 bound to `src/click/__init__.py`** | none | 11 | 2, both `k0`. 0 of 11 checked |
| 119 s219 | `termui.py` | `k0` only | 3 grains, `k0` only | 0 | 2, `k0` |
| 120 s149 | `utils.py` | `k0` only | none | 0 | 1, `k0`, lost |
| 120 s181 | `termui.py` | `k0` only | 2 grains, `k0` only | 0 | 2, `k0`. Then wrote its own tool results, and its `decisions.author` did not run |
| 126 s226 | `termui.py` | `k0` only | 2 grains, `k0` only | 0 | 2, `k0` |
| 127 s280 | `decorators.py` | `k0` only | 2 grains, `k0` only | 0 | 1, `k0` |
| 128 s143 | `utils.py` | `k0` only | none | 0 | 1, `k0`, lost |
| 128 s196 | `termui.py` | `k0` only | none | 0 | 2, `k0` |

- `k0` was the only constraint returned in 9 of 10 Architect sessions. The cause is the register, not the seat: the surveyed constraints bind `src/click/globals.py`, `src/click/_utils.py` and `src/click/__init__.py` on every night, plus 1 example path on night 118 and 6 test paths on night 128. No binding names `termui.py`, `utils.py` or `decorators.py` (observed: `constraint_bindings`, `m1.py`). So the survey never read the three files that every item of these nights changes.
- On night 118 the push showed 11 bound constraints. The Architect filed `k0` on `src/click/__init__.py` and checked none of the 11 (observed: s145). The brief tells it to file one `k0` row only `When no constraint other than k0 is in range` (observed: `rota/roles/prompts/architect/structural_review.md`). `findings_find` does not refuse a `k0` row on a file that bound constraints reach (reasoned: `rota/roles/api.py:2803-2894`).
- 5 of 10 Architects called `model.consult` again, with the grains of `expected to touch` and not of the diff (observed: the table).

## 4. The replay

**The seat sent `pass` on a diff that misses one criterion in 2 of 2 runs, and named no criterion in either.** The 2 controls on the recorded prompts also sent `pass`, so the interview path gives the recorded verdict (observed: `r127_*.out`, `r128_*.out`, 2026-10-07 05:10).

`interview_turn.py` cannot hold an edited diff. It reads the turn's `user` text from the database by session and turn, and it has no option to change it. It also adds a preamble that says the session has ended and `Call no tool`, and a line that lists the session's recorded calls (observed: `probes/frame37/interview_turn.py`, 2026-10-07). This read did not change the script. It ran the script on copies of the night databases in the scripts folder (`mkcopy.py`). Each copy holds the edited `user` text of turn 1, and has no `tool_calls` rows for the session, so the calls line says `none` and does not show the recorded pass. The one question asked for the exact `TOOL:` lines the seat would send. A replay as the seat's own turn, with no preamble, would take a mode of the script that sends the edited prompt with the system text and adds nothing, or a flag that reads the `user` text from a file. The read did not build that. So these runs are what the seat says it sends, under an interview frame, and not a recorded seat turn (reasoned: the frame differs from the night's turn).

`ollama ps` showed no model before the first run, and `qwen3.5:9b` only before the later runs. Model `qwen3.5:9b`, temperature 0, `num_ctx` 16384, think false, as the session's pins.

| Run | Prompt | First `verdicts.emit` | `reason` | Names the missing criterion |
|---|---|---|---|---|
| r127_control | s279 turn 1, as recorded | `pass` | `The diff introduces the `show_python` parameter and appends the Python version when True, satisfying all criteria.` | not applicable |
| r127_no_cr3 | s279 turn 1. The `python_version` line is out, and the `echo` line is the original, so nothing is appended. The parameter and the docstring that promises the append stay | `pass` | `''` | no. It claimed `cr_3_version_option_show_python_true` `encodes=True` |
| r128_control | s142 turn 1, as recorded | `pass` | `''` | not applicable |
| r128_no_sep | s142 turn 1. `json.dumps(obj, separators=(",", ":"))` is `json.dumps(obj)`, while the criterion `echo_json_compact` quotes the separators | `pass` | `''` | no |

- Count: the first `verdicts.emit` is `fail` in 0 of 2 edited runs, and `reason` names the criterion in 0 of 2. 4 model calls in all.
- The s142 edit changes one argument and removes no line, because removing the one `json.dumps` line breaks the function for every criterion (reasoned: the diff has one line for `echo_json_compact`).

## 5. The mechanism

A pass proves today that the batch's tests are green and that the Critic sent `verdicts.emit(result='pass')` (observed: the 10 verdicts, section 1, 2026-10-07). It does not prove that the diff meets each criterion. The seat passed a diff with one criterion's code taken out in 2 of 2 replays, and on night 120 it passed `cr_2` while its own prose named the gap (observed: section 4, 2026-10-07 05:10, and s180). It does not prove that the tests run the criteria's paths: `claim_encodes` came back `True` in 29 of 29 claims, also on night 127's 3 tests that never pass `--version` (observed: section 2). It does not prove that the new code runs at all outside the hunks, because the Critic sees the hunks and has no call that reads the rest of the file (reasoned: `code.read` and `review.tools`, section 2). It leaves no words, because the verdict comes first in 8 of 10 sessions and `reason` is empty in 10 of 10 (observed: section 2).

A finding proves today that the review ran on the batch. It does not prove that a constraint was checked, because in 9 of 10 reviews the register has no constraint that binds the diff's files, and in the tenth the seat checked none of 11 (observed: section 3). It does not always survive the night, 2 of 2 nights with two merges (observed: section 1).

The sites, one per gap:

| Gap | Site |
|---|---|
| A pass carries no reason, 10 of 10 | the door: `verdicts_emit`, `rota/roles/api.py:6734-6821`, which by its docstring never refuses an empty `reason` |
| The verdict comes before the reasoning, 8 of 10 | the brief: `rota/roles/prompts/critic/review.md`, the order of work and the line `A remark goes in reason= on either result` |
| A pass lands on a diff that misses a criterion, 2 of 2 replays | the brief: `rota/roles/prompts/critic/review.md`, step 1, which asks a question per criterion and requires no answer per criterion before `pass` |
| `claim_encodes` is `True` on tests that never run the criterion's path, 29 of 29 | the door: `verdicts_claim_encodes`, `rota/roles/api.py:6693-6730`, which records the claim with no check, and which the brief asks for only on the way to a fail |
| The Critic sees the hunks and not the file around them | the prompt builder: the `code.read` push in `rota/core/runner.py`, the Critic's whole view of the code |
| `k0` is the only constraint for the files that every item changes, 9 of 10 | the prompt builder: the structural-review push in `rota/core/runner.py:2514-2545` shows `k0` alone. The cause behind it is the onboarding survey, which bound no constraint to `termui.py`, `utils.py` or `decorators.py` |
| A `k0` finding stands beside 11 bound constraints, night 118 | the door: `findings_find`, `rota/roles/api.py:2803-2894` |
| A finding on a file the diff does not touch, 7 of 18 | the door: `findings_find`, which checks the grain against the diff only on `violated` |
| A second batch's `f1` replaces the first batch's `f1`, 2 of 2 | the door: `findings_find`, which writes the id the seat names with no check of the row's batch |
