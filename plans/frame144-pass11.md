# Frame 144, pass 11: the five test gaps of the review of 96fe3425

Meta workflow. Pass 11 of frame 144, the night databases are not a test tier, and the frame's last pass. An implementing agent on Opus wrote this record on 2026-10-07, on the branch `f144p10` in the worktree `C:/Users/roman/rota_f144p10`, from 96fe3425. The review found 0 high and 5 low, all gaps in the tests, and 4 of its 6 mutants survived. The pass repairs the five and adds no item.

Only `rota/tools/invariants.py` changes under `rota/`, so a night meets no line of this pass.

## What changed

| File | Lines | The change |
|---|---|---|
| `rota/tools/invariants.py` | +12, -4 | `_replaced` reads the order of the receipts. I5 joins `items` as `park_ask` does |
| `tests/rota/test_invariants.py` | +36, -5 | Two I9 tests, two helpers, and the replace test made whole |
| `tests/rota/test_scene_large_module.py` | +10 | One `blocks` test on a bracket line inside a block |
| `tests/rota/test_scene_two_batches.py` | +20 | One test that compares `_S156_SENT` with night 126 |

1. **`_S156_SENT` is tied to the night.** `test_the_s156_row_holds_the_nights_bytes` opens `D:/repos/rota/.rota/clickI_night126.db` with `mode=ro&immutable=1` and compares s156's turn 2 with `_S156_SENT`. It skips when the database is absent.
2. **A woken session with no receipt is no replace.** `test_i9_a_woken_session_that_writes_no_receipt_on_the_test` puts t1 at version 2 and adds a committed session that the challenge woke, with no receipt. The challenge is a finding.
3. **The blank line before a header is tested.** `test_a_function_name_in_brackets_inside_a_block_is_no_header` puts `[tests.load]` inside `code.diff`, after a line of text. `blocks` gives `code.diff` and `criteria.load` only. The lookbehind stays.
4. **`_replaced` reads the order of the receipts, not the current version.** `receipts.new_version` is the table's version at the write, from `db.bump_version`, and not the row's version. So `new_version > 1` says nothing about the test (observed: `db.session_commit`, and night 126's s150 receipt holds 4 while the test is at version 2, 2026-10-07). The woken session's receipt now counts as a replace only when an earlier receipt on the same row has a lower `new_version`. `test_i9_a_woken_session_that_creates_the_test_does_not_replace_it` has the woken session create t9 and a later session replace it. The challenge is a finding. `test_i9_a_challenge_answered_by_the_replace_it_woke` now writes the earlier receipt itself, so it does not rest on the scene's receipts.
5. **I5 uses an inner join on `items`,** as `predicates.park_ask` does. A batch with no item row is then not read, and an open ask on it reads as an ask on no batch.

On nights 119 to 127, each of the 21 excluded challenges has an earlier receipt on its test before the woken receipt (observed: a script over the nine read-only databases, 2026-10-07). So the new rule excludes the same 21 rows.

## The checker's counts

Unchanged from pass 10 (observed: `python -m rota.tools.invariants`, read-only, 2026-10-07): night 126 44 findings, I2 6, I4 34, I9 3, I10 1. Night 127 82 findings, I2 6, I4 68, I9 8. I5 is 0 on both.

## The tests

The three touched test files gave 97 passed, 2 skipped and 6 xfailed, against 93 passed in pass 10 (observed: `pytest -n 3`, 2026-10-07).

## The mutants

The review's mutants ran again on this tree, each in place with its file's bytes restored after it. `git diff` had the same hash before and after the run. The script is `scratchpad/p11_mutants.py` of session 86c3e06e. m6 is new and is the rule that item 4 removes.

| Mutant | The change | Red |
|---|---|---|
| m1_no_given_up | `_owes_ask` drops `given_up` | 1 |
| m2a_old_rule | `_replaced` reads only a version above 1 | 3 |
| m2b_session_only | `_replaced` reads a woken session and a version above 1, no receipt | 2 |
| m3_s156_byte | one byte of `_S156_SENT`, `exit_code == 0` to `== 1` | 1 |
| m4_no_blank_line | the lookbehind of `_BLOCK` to `^` | 1 |
| m5_no_frame174 | the I9 sentence drops "frame 174" | 0 |
| m6_current_version | `_replaced` reads the receipt and the current `t.version > 1` | 1 |

6 of 7 are red. m5 survives. No test reads the I9 sentence, and the review's five lows name no test for it.

## The gate

Observed: `python -m rota.tools.gate` in the worktree, 2026-10-07, 02:59 to 03:11.

```
suite: 23 failed, 3152 passed, 35 skipped, 17 xfailed, 18 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 659.7s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The gate printed one line before the five: `main card: held by qwen3:8b until 2026-10-07T03:04:37.068191+01:00, re-records wait`. The three new reds are three of the known four, as in pass 10. No case was stale, so no re-record ran. Passed is 3152, pass 10's 3148 and the 4 new tests.

## Deviations

- **Item 4 reads the order of the receipts, not `new_version > 1`.** The brief asked for the receipt's `new_version > 1`. That number is the table's version counter, so it is above 1 for nearly every receipt and would leave the test red. The earlier receipt on the same row is the order that the brief's test asks for.
- **The s156 test opens the night with `immutable=1` as well as `mode=ro`,** as `invariants.open_readonly` does, so no read writes a journal beside the night.

## Usage

The harness line carries the tokens. The agent's own estimate for this pass is about 35k, under the cap of 50k. No sub-agent ran. No model call ran outside the gate.
