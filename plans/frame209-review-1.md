# Frame 209, review 1: commit b170ba43, the agenda guard for a note about an inherited test

Reviewer: Opus, read-only, worktree `C:\Users\roman\rota_rv209` at b170ba43. Date 2026-10-12.
Verdict: the pass stands. No finding blocks the commit. One design question is open for the holder.

## (a) Verdict on each point

1. CONFIRMED. On a copy of the night's database, `frontier` at b170ba43 returns 5 wakes. At c18f868c it raises the night's `AttributeError`.
2. CONFIRMED covered. Twelve call sites reach `_items_reached`. The new guard sits inside the function, so it covers every site. No other site makes a criterion swap.
3. The test proves the order. With the sort removed, the same test fails on the order. The order is the brief's ruling, but law 8 reads the lineage wider. See finding 1.
4. CONFIRMED. The test fails at c18f868c with the night's traceback, `principal.py:554`. It passes at b170ba43.

## (b) Findings

1. `rota/core/scheduler.py:1085-1094`, low, PLAUSIBLE. The two notes are in the request's own lineage. Both `inh_*` tests belong to bg_2, and bg_2's item is `confirm_default_on_eof`, the one open request. Law 8 says "A lineage's open assumptions are presented at its gates". The fix sorts the two notes after the rows that reach the request, behind up to 30 rows with a page cap of 7. `_items_reached` also gives them no item, so every reach-based gate (`waits`, `off_page`, `request_rows`) sees them as about no request. The cause is that `_items_reached` has no `tests` branch. The pass report names the same question as open. The rows are notes that a project test passed before, so the order cost is small.
   Fix: if the holder wants the lineage rule, reach a test with no criterion through `tests.batch_id` to the batch's item, and change the test's expected order to rowid order.
2. Outside the points. `rota/roles/principal.py:548-579`, low, PLAUSIBLE. `_items_reached` reaches no item for any test id, with or without a criterion. Only `reaches_request` swaps a test to its criterion. So a note on a test with a criterion reaches the request in the sort, but `waits` and `off_page` see no item for it. The behaviour is older than b170ba43 and no case renders it.
   Fix: move the test-to-criterion (or test-to-batch) step into `_items_reached`, and drop the swap in `reaches_request`.

No high finding. The guard in `_items_reached` also makes the scheduler guard redundant for the crash. Each guard alone makes the test pass by reading. The two guards together cost nothing.

## (c) Probes

All under `C:\Users\roman\AppData\Local\Temp\claude\d--repos-rota\91506043-2ba0-4cdf-b0eb-d1a00b7bca68\scratchpad\rv209\`.

- `night141_copy.db`: a backup of `clickI_night141.db`, read through `file:...?mode=ro`. The original stayed unopened for writing.
- `c18\`: `git archive c18f868c` of `rota`, `tests`, `pytest.ini`, `pyproject.toml` and `rota_serial_plugin.py`.
- `probe_frontier.py`: copies the database again, lists the open rows about a test, then runs `tick_agenda` and `frontier`. Output in `out_b170.txt` (5 wakes, agenda refs 7 rows) and `out_c18.txt` (both raise `'NoneType' object has no attribute 'partition'`). The night has 32 open rows, 2 about tests, both with no criterion, and 0 with a NULL `about_ref`.
- `test_c18.txt`: the b170ba43 test file on the c18f868c code. Result: 1 failed at `rota\roles\principal.py:554`, `AttributeError`.
- `test_b170.txt`: `test_request_page.py` and `test_frame193_pass2.py` on the worktree. Result: 108 passed, 4 xfailed.
- `test_nosort.txt`: the c18 scratch copy with the swap guard on and the sort removed. Result: 1 failed, `('l_a94d65762...182', 'l_req') == ('l_req', ...)`. The assertion holds the order.
- `lineage.txt`: the open request is `confirm_default_on_eof`. Both `inh_*` tests are in bg_2, and bg_2's item is that request. `PAGE_ASSUMPTIONS` is 7.

No gate ran. The points need no full suite.

## (d) Usage

Estimate from the reviewer: about 40k input tokens, 6k output tokens, about 46k total. Read the harness line for the true count.
