# Frame 257, review 2: pass 1c, commit c0813629

Verdict: accept with one fix (finding 1). The door change is correct for the measured case. No recorded case outside the target case changes.

## (a) Verdicts on the points

1. CONFIRMED. The new branch sits inside `if tails & set(new)` (api.py 5193). `if not new` returns at 5190 first, so the branch cannot fire with no new callable. The no-new refusal (5180-5189), the invented refusal (5214-5222) and the all-existing refusal (5223-5233) keep their order and their conditions.
2. CONFIRMED. `%::bill` does not match `main.py::split_bill`, because the pattern needs the literal `::` before the tail. A bare new name is skipped by `not in new` and also fails both query terms. The probe refused `[bill, main.py::split_bill]` for a new `bill` and `[split_bill, main.py::bill]` for a new `split_bill`, and admitted `[split_bill]` alone.
3. CONFIRMED with a caveat. The text has 44 words with one old name, in plain words, and carries the route. Quote: "the item names split_bill, a new callable, and this surface also names calculate_tip, which exists today. The surface is what the test calls. A test of calculate_tip tests the old behaviour. Name split_bill alone as the surface, in its own file: surface_refs=["split_bill"]". The route drops the path half of the seat's ref (finding 2).
4. CONFIRMED right by the record. Night 147's `echo` was a location, and a surface of `echo` led the Developer to change click's `echo`. The probe refuses `[echo_json, src/click/utils.py::echo]`. No case in `tests/rota/cases/*.yaml` carries a mixed surface. The `tests.encode` surface door (api.py 8877-8890) needs the test to call a surface name, not to call only surface names, so a comparison test can still call `echo`.
5. None in the case files. Every `surface_refs` list in `tests/rota/cases/*.yaml` holds one name. In the cassette database, only `L1-TE-a-new-behaviour-is-a-new-callable` holds admitted mixed surfaces beside a new callable. `L3-a-challenge-reaches-the-role-that-can-answer-it` and `L1-TE-specify-criteria` hold mixed surfaces, but their items name no callable, so `new` is empty there.
6. CONFIRMED. On 8e22d0fc, `tails & new` is `{split_bill}` and the door returns, so `pytest.raises` fails. The test is red on the old code by reading. Run on c0813629: `39 passed in 1.58s`.
7. The seat's own behaviour on the base. Run 5 met no new refusal. The `ledger.log` refusal and the invented `OK criteria.specify ->` lines came after the criteria landed, on other ops. The case file `l3_handoffs.yaml` line 104 records the same "wrote its own tool results" fault on qwen3:8b from 2026-09-13. The change alters no prompt and no other door, so it cannot cause them.

## (b) Findings

1. api.py 5199-5202, low, CONFIRMED. The `old` query matches path grains, because the indexer writes a `grain_kind='path'` row per file (indexer.py 452). The probe refused `[split_bill, main.py]` with "A test of main.py tests the old behaviour". The words call a file a callable. Fix: add `AND grain_kind = 'symbol'` to the query of the new branch.
2. api.py 5208-5209, low, CONFIRMED. The route is always the bare name `surface_refs=["split_bill"]`, also when the seat sent `main.py::split_bill`. The encode door reads the path half to find the module (api.py 8897), so the route drops a fact the seat had. "in its own file" can also read as "a new file". Fix: echo the seat's own ref for the new callable in the route, and drop "in its own file".
3. api.py 5934 and 5993, low, PLAUSIBLE. `criteria.respecify` does not call `_surface_names_what_the_item_names`. A repair can write `[split_bill, calculate_tip]` again. My probe could not seed a row through the sandbox, so this is unproven. Fix: call the door from respecify, or record why the move route covers it. (Outside the points.)
4. api.py 5193-5210, low, CONFIRMED. A name that is neither new nor indexed beside the new callable passes: `[split_bill, made_up_name]` was admitted. The invented refusal sits after the early return. The gap predates this change. Fix: run the invented check before the return of the new branch. (Outside the points.)

## (c) Probes

- `scratchpad/p257r2_mixed.py`: reads `D:/repos/rota/tests/rota/cassettes.db` read-only. It counts qwen3:8b completions with a `surface_refs` list of two or more names.
- `scratchpad/p257r2_cases.py` and `p257r2_cases2.py`: read `case_runs` transcripts. They list the cases whose `criteria.specify` calls carry a mixed surface.
- `scratchpad/p257r2_door.py`: calls `criteria.specify` through the sandbox on c0813629. Cases A to G cover the suffix, the bare name, the path grain, the echo location and an invented name.
- `scratchpad/p257r2_resp.py`: tries a respecify of a mixed surface. The sandbox did not keep the specified row, so the probe is inconclusive.
- `pytest tests/rota/test_criteria_surface.py -q -n 0` on c0813629: 39 passed.

All probe paths are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b00cc646-4611-4fd9-8f73-b6b404eeda3a/scratchpad/`.

## (d) Usage

Estimate: about 40k input tokens, about 8k output tokens, about 48k total. The harness gives no exact count.
