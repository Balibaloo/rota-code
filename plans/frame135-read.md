# Frame 135, a Tester's encode replaces a project test: the read

This record is about the rota workflow. It is the read for pass 1, written 2026-10-05.
Source: `.rota/clickI_night120.db`, opened read only, and `rota/roles/api.py` at b5e1f01.

## The cause

The cause in `plans/night120-read.md`, wall 1, is confirmed. A Tester sent its own test under the id of a project test with a new path. `tests.encode` admitted the encode, and the commit rewrote the project test's row (observed: s140 turns, `test_runs`, 2026-10-05).

- s140 is a Tester, mode `answer`, `qwen3.5:9b`, woken by m64 for `echo_json_compact_3` in bg_1 (observed: `sessions`, 2026-10-05).
- The seat saw 34 ids in two lists, `batches.expect` "tests" and `tests.consult`. Each was `inh_...` with `criterion_id` null. The list started `{"id": "inh_01fdb170", "criterion_id": null, "path": "tests/test_utils/test_echo_via_pager.py"}, {"id": "inh_022b8a87", "criterion_id": null, "path": "tests/test_utils/test_confirm.py"}` (observed: s140 turn 1 user, 2026-10-05).
- The system text said: "An id for something you are creating is yours to invent -- make it short and unique, and do not build it out of an id you were shown." The seat took the first listed id in turn 1, and the second listed id in turn 5 (observed: s140 completions, 2026-10-05).
- No completion says why it chose the id. The seat wrote only "I will create a test in `tests/test_utils/test_echo.py`" (observed: s140 turn 1). It copied the first row of the list that it was shown (reasoned: the order of its two ids is the order of the list).

The four earlier calls under `id='inh_01fdb170'`, `path='tests/test_utils/test_echo.py'`, each got a refusal that names no id (observed: s140 turns 2 to 5, 2026-10-05):

1. `pytest will collect nothing from this body: it needs a def test_...() containing at least one assert.`
2. `the test uses pytest and never imports it: a NameError against any code.`
3. `the test chooses '<NonSerializable>', and nothing in the criterion ... says it.`
4. `tests/test_utils/test_echo.py is already inh_5f7b1750's file; two tests in one file overwrite each other on disk. Name this one for its own criterion -- tests/test_<what it checks>.py`

Turn 5 then sent `tests.encode(id='inh_022b8a87', criterion_id='echo_json_compact_3', path='tests/test_utils/test_echo_json.py', ...)` and got `OK tests.encode -> {"id": "inh_022b8a87"}`. The refusal at call 4 told the seat to change the path. It said nothing about the id, so the seat changed both.

## The counts

- bg_1's run at a60ed772f8, the merged head: 36 rows, 36 `pass`, 36 distinct ids (observed: `test_runs`, 2026-10-05). The run of `inh_022b8a87` says `1 passed`. s140's body holds one test. `test_confirm.py` holds two (`test_prompts`, `test_confirm_repeat`).
- No bg_1 row carries `test_confirm.py`, and the harness runs one file per row (observed: `harness.run`, `_run_one(root, t["path"], ...)`). So `test_confirm.py` did not run in bg_1's merge run (reasoned: from those two facts).
- bg_2's run of `inh_022b8a87` says `2 passed`. `harness.inherit` ran at bg_2's start, found `test_confirm.py` not owned by bg_2, and wrote `INSERT OR REPLACE` under the same id (observed: `rota/core/harness.py:206-210`, `rota/core/lifecycle.py:127`). That replace erased the row's link to `echo_json_compact_3`, not the test. s140's file `tests/test_utils/test_echo_json.py` merged with bg_1, and the next inherit took it as the project test `inh_9092879e`. `inh_9092879e` ran `1 passed` in bg_2 at 0a171187 and in bg_3 at 6ae763f0, then `error` at bg_3's three later heads with the rest of bg_3 (observed: `test_runs`, corrected in pass 2, 2026-10-05). Today the row `inh_022b8a87` is bg_3, criterion null, path `test_confirm.py`, version 1 (observed: `tests`, 2026-10-05).
- Count: 1 session, 1 row stolen, 1 merged batch that skipped one project file. Calls with a project id: 5 of 5 `tests.encode` calls in s140.

## The admitting code (`rota/roles/api.py`, b5e1f01)

- 5532-5534: `prior` reads the row by id. It returns early only on an equal path and body.
- 5554-5557: `stored` asks for `id = ? AND criterion_id = ? AND batch_id = ?`. The project row has a null criterion, so `replaces` is false and the path check at 5558 never runs.
- 5576-5582: `other` refuses a row of another batch only. In bg_1 the project row was bg_1's own.
- 5587-5607: `clash` looks for another id on the sent path. `test_echo_json.py` had no row.
- 5621: the encode is staged. The commit UPDATEs every staged column, so the row takes the new path, criterion and body.

## The sign of origin

The sign is `criterion_id IS NULL` on the stored row, not the `inh_` prefix.

- `tests` has two writers: `harness.inherit`, which writes `criterion_id` NULL, and `tests_encode` (observed: `rota.tools.map table tests`, 2026-10-05).
- `tests_encode` calls `_must_exist(ctx, "criteria", criterion_id)` at 5135, so a Tester's row always holds a criterion (reasoned: an encode with no criterion is refused before it is staged).
- In night 120's database, 0 rows have a null criterion and a name without `inh_`, and 0 `inh_` rows have a criterion (observed: `tests`, 2026-10-05). The night 119 Tester's `inh_echo_json_01` holds its criterion, so the sign keeps it replaceable (reasoned).

## The predicate

`tests.encode` refuses when the stored row of `id` has `criterion_id IS NULL` and a path other than the sent path.

- s140's case has a new path: `test_echo_json.py` against `test_confirm.py`. All five calls of s140 meet the predicate.
- A challenge fix of the project test itself keeps the stored path. The predicate does not meet it, so frame 128's path behaves as it does today (reasoned: frame 128 is open and unruled).
- The door stands after the equal-body check and before the one-test guard, so the seat reads the id fault before the path fault.
