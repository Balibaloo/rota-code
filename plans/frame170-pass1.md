# Frame 170, pass 1: a pass names an added line per criterion

**Record of 2026-10-07 09:51, meta workflow. The pass builds a door and a brief for the Critic seat, which is the rota workflow.**

The pass builds `plans/frame170-design.md` sections 1 to 6 on the branch `f170` in the worktree `C:/Users/roman/rota_f170`, from fb0cee10. The gate ran once. It shows no red that the pass caused (observed: the gate and the case history below, 2026-10-07 09:48).

## 1. What changed

- `rota/roles/api.py`. `verdicts_emit` gains `lines: dict[str, str] | None = None` as its last parameter. On `result='pass'` it calls `_pass_lines_check` and stores `json.dumps(lines)` in the write. A fail reads no lines and stores none. New helpers: `_batch_diff`, `_added_lines`, `_line_parts`, `_line_held`, `_pass_lines_check`, `_fail_on`, and the constant `_LINE_PART_MIN = 12`. `code_read` now takes its diff from `_batch_diff`.
- `rota/core/sandbox.py`. `ARG_HINTS_BY_OP[("verdicts", "emit")]` holds `line` and `quotes`, each pointing to `lines=`.
- `rota/core/db.py`. `init_db` adds `verdicts.lines TEXT` behind `_has_column`, as it adds `reason`. `SCHEMA_MARK` does not move.
- `rota/core/schema.sql`. `CREATE TABLE verdicts` holds `lines TEXT`.
- `rota/cockpit/inspect_api.py`. The `verdicts` lead columns end with `lines`, after `reason`.
- `rota/tools/nightreport.py`. `V_COLS` holds `lines`. Each verdict row prints `named=<n>`: the count of criteria a pass named, `-` on a fail, `?` when the column is absent.
- `rota/roles/prompts/critic/review.md`, 46 to 52 lines, and `rota/roles/prompts/critic/answer.md`: the old text to the new text of design section 3, verbatim.
- `rota/testkit/scenes.py`. `judge()` gains `lines`. A pass names c1's line of `UPGRADE` by default.
- Tests. `tests/rota/test_verdict_lines.py` is new, 30 tests. `test_arc_seam.py`, `test_delivery.py` and `test_desk_guards.py` carry `lines=` on their scripted passes. The last two get a real batch diff from the helper `a_batch_repo`.

## 2. Deviations from the design

1. **The offer's next step is the fail, not `AGAIN`.** Design section 2 says to record `claim_encodes` with `then=(AGAIN,)`. `AGAIN` sends the refused pass again, and the same door refuses it again. The follow check of frame 144 reports that as a refused offer (reasoned: `sandbox.follow`, "It fails when the door that refused it first refuses it again"). The step is `verdicts.emit(batch_id, result='fail', failed_criterion=<cid>)`, which the doors admit after a claim of True.
2. **A `lines` that is a list, and not a dict, gets the shape refusal.** The design names only text. The binder admits a list here, because the annotation names `dict` (observed: `validate_args`, `rota/core/sandbox.py`). One re-recorded run sent `lines=[id, line, line]`, met the shape refusal and sent the dict next (observed: `L1-CR-finish-the-review-with-the-answer-in-hand` run 3, 2026-10-07 09:40).
3. **Tests beyond section 5.** The file also holds the nearest-line hint, the four tolerated shapes, a part under 12 characters, a context line, a batch with no criteria, the column on an older database, the parsed call landing, the hints and the night report's count.
4. **Ratio two has no baseline.** The brief corrects the design, so this record writes none.

## 3. The recorded cases

The gate re-recorded 7 stale cases, five live runs each, on qwen3:8b. The counts before are the main checkout's `case_runs` at the last prompt hash (observed: `tests/rota/cassettes.db`, 2026-10-07 09:50).

| Case | Before | After |
|---|---|---|
| `L1-CR-pass-a-conforming-diff` | 390 of 390 | 5 of 5 |
| `L1-CR-fail-names-its-criterion` | 390 of 390 | 5 of 5 |
| `L1-CR-a-test-that-encodes-nothing-is-a-challenge` | 0 of 20 | 5 of 5 |
| `ACT-CR-quote-the-tests-code` | no row on qwen3:8b | 5 of 5 |
| `L1-CR-finish-the-review-with-the-answer-in-hand` | 415 of 415 | 5 of 5 |
| `L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist` | 0 of 735 | 0 of 5 |
| `L3-a-failed-verdict-turns-into-a-fix` | 237 of 392 | 2 of 5 |

- The doubtful-criterion case is the known `L1-CR` red. Its old runs pass the batch and send no question. The cause is not the new door (observed: the run of 2026-10-07 03:57, `verdicts.emit` with no question).
- The L3 case is not in the design's list. Its chain wakes the Critic in review mode, so its prompt changed. It is red in the stored baseline of 658abb6. It was 60 per cent green before. Its 3 red runs send a fail before `claim_encodes`, then claim False and challenge the Tester. That is the old fail-claim path, and the new door does not touch it (observed: runs 1 to 3, 2026-10-07 09:50).
- `L1-CR-a-test-that-encodes-nothing-is-a-challenge` was 0 of 20 at its last prompt hash in the main checkout, and is 5 of 5 now. The pass does not claim it as a fix: the read of why is not done.
- What the new door met in the green runs: values with line breaks, read by the second tolerance; a list in place of a dict; and a criterion's words in place of a line, refused by check 2. Each seat sent the call again and landed (observed: `L1-CR-finish-the-review-with-the-answer-in-hand` runs 1 to 3).

## 4. The gate

```
suite: 29 failed, 3207 passed, 35 skipped, 17 xfailed, 18 warnings
new reds (0): none
reds gone (0): none
stale (0): none
time: 686.7s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline fb0cee1 2026-10-07 09:48
```

- The worktree had no baseline, so the gate stored this run as its baseline, on the uncommitted tree. Its "new reds (0)" therefore compares the run with itself (observed: the gate's notes, 2026-10-07 09:48).
- Against the main checkout's baseline of 658abb6, 3 reds are new: `L1-CR-a-doubtful-criterion-...`, `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner` and `test_map.py::test_mode_lists_its_base_file_and_joins_every_line`. All three are in the known reds of frame 170's status of 05:04. The first is red at 0 of 735 before this pass.
- 5 of the 29 failed are the cases that the re-record cleared.
- The re-recordings are in the worktree's `tests/rota/cassettes.db`, which git ignores. The main checkout's cassette database does not hold them.
