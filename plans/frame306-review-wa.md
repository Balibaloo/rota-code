# Frame 306, W-A review: a check line has a number, and his drop retires the test

Worktree `C:/Users/roman/rota_r306wa` at 54814fa6 (a0afb995, 896abeef, 54814fa6 on 643db050). Read-only.
Verdict: stands. 0 high, 2 medium, 3 low. 3 cases go STALE. The touched files run 199 passed, 4 xfailed.

## (a) The points

1. Stands. `order` holds the test id in 17 reads. One misbehaved and is fixed (`is_test_row`, api.py 12110). Table in (e).
2. Stands. Lines 1 and 2 alone land (probe D). "Remove line 4" lands `contest` on the test (probe B). New words for line 4 land `contest` on the test, `tests.retire` refuses with the ruling id, and the prompt sends the Tester to `tests.encode` (probe C). His night-164 words, "the second check under line 2", are refused at line 4 and land on cr_1 at line 2 (probes A, A2). See finding 1.
3. Stands. No ruling, a ruling that keeps the line, and a wake off the chain each refuse (5 tests green, probe B). The wrong-wake sentence names no route. See finding 4.
4. Stands with one gap. With the red retired: `tests_failing` [], `exhausted` [], harness predicate [], `live_tests_for` holds the green only, `park_reds` empty, `failing_attempt` 0, `mergeable` "no verdict" (probe B). `tests_triage` still reads the retired test as the encoder. See finding 2.
5. Stands. The relay wake carries `principal_test_verdict {RED: contest}` and `principal_said`. The Tester's answer wake carries both, offers `tests.retire`, and the retire lands `retired_by r_...`, version 2 (probe B). His actual night-164 words stop at the first hop (finding 1). `answer.md` 15 says a drop is a retire, not a new encode.
6. Stands. The next render shows `3. check: tst_format_filename_doc` alone (probe B). The closing sentence names item lines and code lines, both before any check line. A later clarify names rows, not numbers (runner.py 2574). `_ruling_line` reads the recorded order, and `ruling_drops_line` reads a kept test's verdict first (probe S).
7. Stands. A database marked `criteria-retired` refuses with `SCHEMA_STALE`. `init_db` on a fresh one holds `tests.retired_by` (probe 7).
8. 3 STALE: `L1-TS-apply-a-term-and-write-the-test`, `L1-TS-assert-the-value-the-surface-returns`, `L1-TS-encode-a-criterion-the-principal-corrected`. Main at 1995c10a reads 0 stale with the same code as 643db050. The cause is `tester/answer.md`, not a check line. The report's "none found" counts page cases only.

## (b) Findings

1. api.py 12121-12185, `_line_refusal`. Medium. CONFIRMED: m121's own words with `4: contest` refuse, "The words name line 2 and do not name line 4". With `2: contest` they land on cr_1 as night 164 did. The number on the page is the only repair, and nothing reads "the second check under line N". Fix: let `_ruling_words_on` and the contest door read "the Nth check under line M" as the Mth criterion's Nth test line.
2. api.py 7425, `tests_triage` `done`; predicates.py `tests_missing`. Medium. CONFIRMED: with the criterion's only test retired, `tests_missing` wakes nobody and `tests.triage` says "tst_... already encodes it". The criterion stays live and untested, and nothing says so. Fix: add `live_tests(conn, "id")` to both reads, so a retired test encodes nothing.
3. db.py 745-777, `red_before` and `lift_on_red_move`. Low. PLAUSIBLE: both read every `test_runs` row of the batch. After a retire the next harness run writes no run for the retired test, `now != before`, and the `tests_failing` key resets once. One lift on a red that he removed is right, and a second cannot happen. Fix: none needed, or filter `before` with `live_tests`.
4. api.py 6373-6376. Low. CONFIRMED: the wrong-wake refusal says only "Only the wake that carries the ruling ... retires a test". The brief asks each refusal to name a route. Fix: add "Answer from the wake the Terminologist's `msg.answer_tester` opens".
5. report (d) and pass 1b "Cases to re-record: none found". Low. CONFIRMED: 3 Tester answer cases go STALE through the prompt hash. Fix: name them in the report and re-record them in the gate.

## (c) Probes

All under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/48122667-6b95-4100-a43b-30ec9c6540dd/scratchpad/r306wa/`.
- `p7_schema.py`: init_db, mark set to `criteria-retired`, reopen refuses. Fresh database holds the column.
- `p25_route.py` and `p25_lib.py`: the fixture of `test_frame306_test_retire.py`, then `rulings.rule` through `run_session` for five word sets (A, A2, C, D, B).
- `p345_route2.py`: probe B's route through `resolve_inbound` for the relay and the Tester wakes, `_wake_allow`, `tests.retire`, the next render, the seven `live_tests` readers, `tests.triage`. Probe S: two reds, drop line 3, retire, then `ruling_drops_line` on the kept test is None. The reply was inserted by hand, so pump wrote no `order:m121`; `_ruling_line` fell back to the render.
- `p4_all_retired.py`: one test only, retired, then `tests_missing`, `tests_failing`, `tests.triage`.
- `casestatus_wt.txt`: `ROTA_MODEL=qwen3:8b ROTA_DEV_DB=D:/repos/rota/tests/rota/cassettes.db python -m rota.tools.casestatus` in the worktree. The first run without `ROTA_DEV_DB` created an empty `tests/rota/cassettes.db` in the worktree, gitignored.
- pytest on the five touched test files: 199 passed, 4 xfailed.

## (d) Usage

About 100k input tokens, 14k output tokens, about 114k in total. No sub-agent.

## (e) Outside the points: the `order` readers

| Reader | A test id there |
|---|---|
| `_ruling_line` api 6397 | resolves to its line, the goal |
| `rulings_rule` 11897 key, 11945 `asked`, 12149 `request_first`, 12152-12166 batch, closed and item lines | a test is none of these, no effect |
| 12110 `unnamed` | skipped by `is_test_row`, probe D |
| 12143 `contested`, 12172 approved | a contested check line needs words that name it, probes A and B |
| 12131-12139 faulted batch, 12182 faulted text | a test is no batch and has no text, an empty string |
| `land` 2141 record, 2214 and 2262 line faults | stored and replayed, index by the real ref |
| runner 2430 clarify `lines`, 2583 `_page_named_lines` | "row tst_..." |
| `door_rows(..., "order")` | `_ruling_line` only, the others read `stalled` and `stamped` |
