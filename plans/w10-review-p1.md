# W10 review, pass 1, of fe1d300c

Verdict: NOT READY. Findings: 2 high, 4 low. The reviewer read only. The worktree is `C:/Users/roman/rota_rw10` at fe1d300c, and the parent is 8c71b473.

## (a) Verdicts on the points

1. One reader: PARTLY. Both doors call `api.criterion_batches`, but each door applies its own predicate. A ticket in two batches passes the door and fails `tests.encode` (finding 2).
2. The s112 shape: FIXED. At fe1d300c the replay is refused. At the parent the same call lands as m29. The text has 35 words, and it tells the Terminologist to stop (finding 3).
3. The kept deviation: REOPENS THE WALL. A Tester with no batch can ask, and the answer to that question lands with no batch (finding 1). In nights 170 to 173 every Tester question had a batch, count 0.
4. Glossary-only answer: LANDS with no batch, at both commits. The woken Tester has no criterion to test (finding 4). Count 0 in nights 170 to 173.
5. The reach: eight other pairs, not six. No door of the eight reads the batch fact. Count 0 in nights 170 to 173. Night 169 shows one call through `vision_keeper` to `tester` (finding 5).
6. The tests: 479 passed, 2 xfailed. No test pins the one reader (finding 6).

## (b) Findings

1. HIGH. CONFIRMED. `rota/core/sandbox.py` lines 4609 to 4613, `_bind_send`. A criterion that an open Tester question names skips the check. The question door lets a Tester with no batch ask. Probe P3 replayed night 173 before any batch. The Tester `msg.question_terminologist(refs=['c_1'])` landed. With that question open, `msg.answer_tester(refs=['c_1'])` landed with no batch. The woken Tester then meets "belongs to no batch" again. Night 169 shows the asking half on record: s113 had no batch and asked the Vision Keeper (m30). Nights 170 to 173 hold four Tester questions (night 172 s124, s127, s230, s246), and each had a batch wake.
   Fix: refuse `msg.question_terminologist` about a criterion when the Tester has no `ctx.batch_id` and `criterion_batches` is empty, and keep the exemption.

2. LOW. CONFIRMED. `rota/roles/api.py` line 460 and `rota/core/sandbox.py` lines 4617 to 4619. The two doors read the same rows by two predicates. The door asks for any live batch with a commit. `_batch_of_criterion` asks for exactly one batch. Probe P1 put tk_1 in bg_1 (merged) and bg_9 (running), both with commits. The answer landed, and `_batch_of_criterion` returned None for a Tester with `ctx.batch_id` None. The new test docstring says the doors "cannot disagree", and that is false. Eight nights from 144 to 167 hold a ticket in two batches. Night 147 s315 has the fault "criteria belong to no batch", and its ticket sat in bg_2 (abandoned) and bg_3 (merged). The divergence existed before this commit.
   Fix: make one function that returns the batch `tests.encode` attaches to, and make the door refuse when that function returns None or the batch has no commit.

3. LOW. CONFIRMED. `rota/core/sandbox.py` lines 4637 to 4640. The refusal has 35 words in three sentences. The brief asks for under 25. The text names no rota identifier. "Your work here is done" tells the Terminologist to stop, and stopping is the right action.
   Fix: "No change from this criterion has a commit yet. The Tester reads your new words later. Stop here."

4. LOW. PLAUSIBLE. `rota/core/sandbox.py` line 4609, the `crit` filter. Probe P4 sent `msg.answer_tester(refs=['callback'])` with no batch. The answer landed at fe1d300c and at the parent. The woken Tester holds no criterion and no batch, so it has nothing to encode. The probe did not run the woken Tester. In nights 170 to 173 every answer to a Tester carried a criterion ref, count 0.
   Fix: when no ref is a criterion, let the answer land only as a reply to an open Tester question.

5. LOW. CONFIRMED by the read and the records. Eight pairs send `answer` or `reopen` to a Tester or a Developer, and none reads the batch fact:
   - `architect` to `developer` answer: `_bind_send` line 4510, `_rowless_answer_refusal`. It checks that rows exist.
   - `terminologist` to `developer` answer: `_bind_send` line 4464. It checks glossary terms.
   - `tester` to `developer` answer: `_bind_send` lines 3839 and 3921, `_answer_evidence`. It reads test runs.
   - `vision_keeper` to `developer` reopen: `_bind_send` line 3651. It checks items.
   - `vision_keeper` to `developer` answer, `vision_keeper` to `tester` answer, `researcher` to `developer` answer, `researcher` to `tester` answer: no role check in `_bind_send`.
   In nights 170 to 173 every call through these pairs replied to a message, or named a batch that existed (night 172 m115, bg_3). The count is 0. Night 169 m31, from `vision_keeper` to `tester`, woke s115 with no batch, and `tests.encode` refused s115. The builder report says six pairs and lists eight.
   Fix: do not wake a Tester on an answer when no criterion of the answer has a batch. One check at the wake covers all pairs.

6. LOW. CONFIRMED by the read. `tests/rota/test_answer_tester_no_batch.py`, `test_both_doors_read_one_reader`. The test calls the two readers and compares their outputs. A second inline query in either door still passes it.
   Fix: monkeypatch `api.criterion_batches` and assert that both `tests.encode` and the answer door change their result.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/2ebac251-aff2-4075-a2e8-ad7f47182931/scratchpad`. Each copies `clickI_night173.db` (opened `mode=ro`), deletes `tests`, `batch_tickets`, `batches` and messages from seq 30, and runs `init_db` on the copy.

- `rv_p2c.py`: replays s112's `msg.answer_tester(refs=c_1..c_4)` in mode `normal` with no trigger. It runs once at fe1d300c and once at the parent from `parent/` (`git archive 8c71b473 rota`). At fe1d300c it is refused, and at the parent it lands as m29.
- `rv_p34.py`: a Tester asks with no batch and lands. With the question open, the answer lands with no batch. A glossary-only answer lands.
- `rv_p4b.py`: `tk_1`, `callback` and `c_1 + callback` at both commits. `callback` lands at both.
- `rv_p1.py`: a ticket in two batches with commits. The door lands, and `_batch_of_criterion` returns None.
- Inline `python -c` reads of nights 147, 169 to 173: messages, `tool_calls` joined to `sessions`, faults, and tickets held by two batches.
- Tests: the 16 files in `tests/rota` that name `answer_tester` or `park_criterion_relay`, the new file included. Result: 479 passed, 2 xfailed, 73 s.

## (d) Usage

The harness reports no token counts to this agent. The figures are estimates: input about 85k tokens, output about 9k tokens, total about 94k. The run went past the 40k cap.
