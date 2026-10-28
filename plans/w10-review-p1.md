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

## p2

This section reviews commit f0642982 on top of fe1d300c. Verdict: READY. Findings: 0 high, 4 low. The commit closes the p1 high and the p1 two-batch finding.

### (a) Verdicts on the points

1. The p1 high: FIXED. A Tester on a message wake with no batch can no longer ask. The answer to a question that is already open still lands, and only a question that passed the door can be open.
2. One check: PARTLY. `api.built_batch` carries the two-batch rule, and on the s315 shape both doors give bg_3. `_ruling_answer_refusal._parked` keeps its own commit query (finding p2-1).
3. The steering fixture: NO HIGH. The tipsAT run database was not found. The record says the Vision Keeper woke on a challenge and wrote "the item was already built". A Developer challenge follows a test run on a commit, so a commit fits the night (PLAUSIBLE).
4. test_invoke_door: the test went green for a new reason (finding p2-2). The door now refuses a call that it let through before. It does not let through a call that the test expects to be refused. No high.
5. A ticket that never exists: NO. `criteria.specify` refuses an unknown ticket, and a staged ticket that does not exist has no batch, so the door refuses. A staged criterion under a real ticket with a built batch lands before its write commits (finding p2-4).
6. The tests: 51 files, the new file, `test_steering`, `test_request_page` and `test_invoke_door` included: 1652 passed, 2 skipped, 10 xfailed. My file list has 51 files, not the builder's 55.

### (b) Findings

p2-1. LOW. PLAUSIBLE. `rota/core/sandbox.py` lines 2124 to 2132, `_ruling_answer_refusal._parked`. This function keeps its own query: a batch that is not merged or abandoned and has a commit. `built_batch` counts a merged batch as built. On a park relay where the only batch is merged, `_parked` says the send door refuses. The send door now lets the answer through. The ruling door then stays silent, so its check is lost. The pin test `test_one_reader_holds_the_criterion_to_batch_query` scans only `_unbuilt_refusal` and `_batch_of_criterion`, so it does not see this query. The probe did not run a park relay.
   Fix: make `_parked` call `api.built_batch`, and make the pin scan every function in `sandbox.py` and `api.py` for `head_commit` next to `batch_tickets`.

p2-2. LOW. CONFIRMED. `tests/rota/test_invoke_door.py` lines 378 to 386 and `rota/roles/api.py` line 460. Probe `rv2_p4.py` ran the test body at both commits. At fe1d300c the first encode landed, because `_batch_of_criterion` gave b1 (running, no commit). At f0642982 the first encode is refused with "c1 exists and belongs to no batch". The test's first `pytest.raises(ValueError)` accepts that refusal, so the test is green for a reason it does not name. `tests.encode` changed for every Tester with no `ctx.batch_id`: a batch with no commit is no longer a home for its test. In nights 172 and 173, every Tester encode on a message wake came after a Developer commit (s123, s227, s229).
   Fix: give the first `pytest.raises` of the test a `match`, and say in the commit body that `tests.encode` now needs a commit.

p2-3. LOW. CONFIRMED. `rota/core/sandbox.py` lines 1945 to 1950. The refusal to the asker has 25 words when it carries three refs, and each extra ref adds a word. Both refusals copy the refs, so they carry rota identifiers such as `c_1`.
   Fix: drop `{ids}`: "No change from these criteria has a commit yet, and you hold no batch. Stop here."

p2-4. LOW. PLAUSIBLE. `rota/core/sandbox.py` lines 1906 to 1916, the `staged` branch. Probe `rv2_p5.py` staged `c_ghost` under tk_1, which has a built batch, and the answer landed before any row for `c_ghost` existed. If the commit later refuses the staged criterion, the Tester wakes on a criterion with no row. The ticket exists in this case, so the door sends no message for a ticket that never exists.
   Fix: let the staged branch count only a criterion whose write passed its door in this session, and drop the outbound message when the commit drops that write.

### (c) Probes

The probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/2ebac251-aff2-4075-a2e8-ad7f47182931/scratchpad`. `p1/` holds `git archive fe1d300c rota`. Night 169 and night 147 are behind the current schema, so `init_db` refuses them. The shapes were rebuilt on the night-173 replay copy `n173_new.db`.

- `rv2_p1b.py`: the m30 shape. The Tester woke on an answer m29 and has no batch. The ask is refused at f0642982, and it lands at fe1d300c. The open-question answer lands at both. The s315 shape: tk_1 in bg_2 (abandoned) and bg_3 (merged), both with commits. At f0642982, `built_batch` and `_batch_of_criterion` both give bg_3, and the door lands. At fe1d300c, both give None, and the door refuses.
- `rv2_p4.py`: the body of `test_a_session_with_no_batch_reads_the_root` at both commits, with each exception printed.
- `rv2_p5.py`: `criteria.specify` on `tk_nope` is refused. An answer on a criterion staged under tk_1 lands. An answer on a criterion staged under `tk_never` is refused.
- `rv2_p1.py`: the first attempt on the night 169 and night 147 copies. `init_db` refused it because the schema is stale.
- Inline reads of nights 172 and 173: the `code.commit` sessions and the Tester encodes on message wakes.

The texts at f0642982:
- "No change built from c_1, c_2, c_3 has a commit yet, and you hold no batch, so there is nothing to ask about. Stop here." (25 words)
- "No change built from c_ghost2 has a commit yet, so the Tester has nothing to work on. Stop here." (18 words)

### (d) Usage

The harness reports no token counts to this agent. The figures are estimates for p2: input about 60k tokens, output about 7k tokens, total about 67k. The run went past the 30k cap.

## p3

This section reviews commit 308b257f on top of f0642982. Verdict: READY. Findings: 0 high, 2 low. Both lows are left over from p2.

### (a) Verdicts on the points

1. p2-1: PARTLY. `_parked` calls `api.built_batch` and has no commit query of its own. The pin now scans `_ruling_answer_refusal`. `_parked` still drops a merged batch, and the send door counts a merged batch as built (finding p3-1).
2. p2-3: NOT MET. With four refs, the Tester text has 28 words, and the answer text has 24. Both texts still carry rota identifiers (finding p3-2).
3. The tests: `test_answer_tester_no_batch.py` and `test_invoke_door.py` gave 56 passed.

### (b) Findings

p3-1. LOW. PLAUSIBLE. `rota/core/sandbox.py` line 2130, `_parked._live_built`. The filter `b["status"] != "merged"` keeps the old rule. On a park relay where the only built batch is merged, `_parked` says the send door refuses. `_unbuilt_refusal` lets the answer land, so the ruling door stays silent and its check is lost. The probe did not run a park relay.
   Fix: drop the merged filter, so that `_parked` returns true exactly when `_unbuilt_refusal` refuses.

p3-2. LOW. CONFIRMED. `rota/core/sandbox.py` lines 1946 to 1953. Probe `rv3_p2.py` sent four refs. The Tester text: "No change built from c_1, c_2, c_3 and 1 more has a commit yet, and you hold no batch, so there is nothing to ask about. Stop here." The text has 28 words, because the cap of three ids adds "and 1 more".
   Fix: name no ids: "No change from these criteria has a commit yet, and you hold no batch. Stop here."

### (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/2ebac251-aff2-4075-a2e8-ad7f47182931/scratchpad/rv3_p2.py`: the night-173 copy with no batch. A Tester woken by m29 asks `msg.question_vision_keeper`, and a Terminologist sends `msg.answer_tester`. Each call sends refs c_1 to c_4, and each is refused.
- pytest on the two files: 56 passed in 12 s.

### (d) Usage

The figures are estimates for p3: input about 25k tokens, output about 2k tokens, total about 27k. The run went past the 10k cap.
