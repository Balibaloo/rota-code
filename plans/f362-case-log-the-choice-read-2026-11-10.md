# Read of L1-DV-log-the-choice-the-criteria-did-not-make

## 1. Result

The cause is the model. qwen3:8b has never passed this case on any brief, and the case's "3 of 5" was measured on llama3.1:8b (observed: `tests/rota/cassettes.db`, table `case_runs`, grouped by model). Nothing in the brief, the door or the harness changed between a green and a red run of the same model.

- Model: qwen3:8b has 0 passed rows on all four briefs it ran against: 0 of 5 runs on system `6f223a06`, 0 of 543 on `21146fc7`, 0 of 370 on `e40417db`, 0 of 290 on `345d8dcd`, the current one (observed: `case_runs`). llama3.1:8b passed 370 of 400 rows on `99db252f` and 10 of 10 on `e9c89e39` (observed: the same). gemma3:12b passed 5 of 5 on `6f223a06`, where qwen3:8b passed 0 of 5 (observed: the same).
- Brief: the composed Developer brief at `batch_start` has hash `3b8149b2` since 2026-10-30 05:33, unchanged through 2026-11-10 (observed: `case_runs.prompt_hash`, `at`). It names `ledger.log` three times, in the "Where you must choose, log it" paragraph, the "A choice the criteria did not make is a `ledger.log`" paragraph, and the tool list (observed: the cassette system text).
- Door: `ledger.log(about_ref, about_table, assumption, kind)` is in the tool list at this tick (observed: `rota/roles/prompts/developer/batch_start.tools`, and the system text). No run of the current brief mentions `ledger` in its transcript, so no refusal text exists to copy (observed: 0 of 535 rows of prompt `3b8149b2` contain the word).
- Harness: the judge counts `ledger` rows and the presence of `ledger.log` in the calls, nothing more (observed: `rota/testkit/fixtures.py` 712 to 718 and 828 to 831). The fixture is the one in the yaml, two criteria, one ticket with the refund sentence (observed: the cassette user text shows them).
- The 8B model does not reach the choice. In all five current runs qwen3:8b echoes the existing file back through `code.write` with no `money` function, commits it, and ends (observed: the transcripts, section 3). A model that writes no `money` cannot meet the refund question (reasoned).

## 2. Timeline

- 2026-08-10: the case and its comment "an 8B model finds it about three times in five" land in commit 8d908e56, under the L1 default model `llama3.1:8b` (observed: `git log -S`, `tests/rota/test_l1.py` line 42).
- 2026-09-17: the gate pins `FALLBACK_MODEL = "qwen3:8b"` in `rota/tools/gate.py` from its first commit 9beb1caf (observed: `git log -S`).
- Last green on llama3.1:8b: 10 of 10 rows on brief `24a54828`, system `e9c89e39`. The `at` column is empty for these rows, so no date (observed: `case_runs`). One system line was removed between `e9c89e39` and `6f223a06`, "Text with quotes of its own, such as source, goes unquoted...", and llama3.1:8b went 10 of 10 to 0 of 10 there (observed: a diff of the two system texts).
- First qwen3:8b recording: brief `97989b55`, 0 of 5, undated, before 2026-10-11 (observed: `case_runs` seq 112988, below the first dated row).
- First dated red: 2026-10-11 16:49, the last row of system `21146fc7`, which added `TOOL: batches.expect(batch_id=None)` to the list (observed: `case_runs.at`, the diff).
- 2026-10-11 to 10-12: brief `94d2adc8`, from b00aaa59 and 6307f965 (the `kind` word at the door). 0 of 370 (observed).
- 2026-10-30 01:11: brief `3b8149b2`, from 2aa9474d and 7e78d4ba (the records paragraph). 0 of 290 through 2026-11-10 03:46 (observed).
- Commits since 2026-10-28 that touch the wake: 2aa9474d, 7e78d4ba (the brief), 301d923d, 38b751d4 (other Developer modes, the brief hash did not move). None touches `ledger_log` in `rota/roles/api.py` (observed: `git log` on the paths, the hash).

## 3. The five recent runs, load qwen3:8b@249205, 2026-11-10 02:26 to 03:46

Each run is recorded twice, at 02:26 and at the re-record at 03:46, byte for byte the same.

1. Run 1: `code.probe`, `code.source`, `code.write` of the file with a broken f-string, refused as "not valid Python", `code.write` of the file unchanged, `code.commit` "Implement money formatting function", `code.commit` again. Ended on "sent again only calls that landed earlier in this session". No `money`, no ledger.
2. Run 2: the same calls and texts as run 1.
3. Run 3: the same, with `batches.expect(batch_id="b_b70dfe")` between the two commits.
4. Run 4: `model.load(ids=["m_0001"])` first, then the same sequence, commit message "Implement money formatting function for invoice email".
5. Run 5: the same as run 3.

The sibling case `L1-DV-build-a-clear-criterion` passed 5 of 5 on the same load with the same behaviour: the file written back without `money`, then a commit (observed: its transcripts). It is green because its judge counts the calls `code.write` and `code.commit` only.

## 4. Reach

- Every Developer `batch_start` wake on qwen3:8b shares the cause: the model copies the read file back instead of adding the named function. The clear-criterion case hides it behind a call-count judge (observed: section 3).
- This is the only register case that expects `ledger.log` (observed: `grep` on `tests/rota/cases/*.yaml`).
- Other Developer reds in `.rota-gate.json` are at other ticks, `tests_failing`, `answer`, `reopen`, and the yaml comment on `L1-DV-fix-the-code-not-the-test` records the same shape: the seat reads and then writes nothing. A per-case query for cases llama3.1:8b passed and qwen3:8b never passed ran past its time cap and is not in this report.

## 5. Fix shape

The case measures a model limit, not a frame: mark it red by construction under qwen3:8b, with the `red_by_construction` marker that frame 326 built, or record a floor on a larger model, as gemma3:12b passed it 5 of 5. A second fix sits in the harness: the clear-criterion judge should also check that the written text defines `money`, so a copied file is red, not green. No frame in the first 40 headings of `plans/stack.md` names this case or the Developer's copy-back; frame 326 names the marker.

## 6. Doubts

- The llama3.1:8b green passes logged generic assumptions, "assuming two decimal places", not the refund choice (observed: the cassette completions). The case never measured the refund reading, only that `ledger.log` was called.
- The dates of the model swap for this case are inferred from `seq` order, because the `at` column is empty before 2026-10-11.
- A removed system line about unquoted source turned llama3.1:8b red on the same brief. The brief read later may have other quoting costs for small models that this read did not measure.
- The current runs are deterministic replays of one load, so five runs are one sample.
