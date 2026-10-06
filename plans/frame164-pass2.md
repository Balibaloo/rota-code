# Frame 164, the scalar door, pass 2

This record is about the rota workflow: the binder that every seat's call goes through. The pass ran in the worktree `C:/Users/roman/rota_f164`, branch `f164`, from `01367219`. It answers the four findings of the review of pass 1, which is at `scratchpad/review164/REPORT.md`.

## 1. Finding 1, the offer kept a wrong id

**One refusal now names both facts, and the offer carries an id that the doors admit when the id has an item.** The pass chose the second repair of the brief. If the id check ran ahead of the scalar door, the seat would meet two refusals in turn. The scalar door now reads the id when it refuses (reasoned: the brief asks for the repair that gives one refusal naming both facts).

The new helper `_scalar_id_fault` in `rota/core/sandbox.py` runs only when the scalar door refuses and `ctx` has a connection. It finds two faults:

- The id is a row of another `_ID_TABLES` table, which the id door of `_bind` refuses.
- The id is absent from the table that the op's own `_must_exist(ctx, "<table>", id)` names. `_must_exist_table` reads that call from the op's source.

When the clashing row is a ticket, a batch or a criterion, and its item is a row of `items`, the offer carries that item with the number. Any other wrong id is the seat's to choose, so the offer carries `api.INVENT`, as the id door's offer does. The sentence then lists up to six rows, as `_must_exist` does. Each id that the sentence names is recorded as a `row` fact.

The double-wrong sentence of s249 turn 3 and of night 115 s200 turn 3, verbatim:

```
problem.prioritize: priority='high' is a word where problem.prioritize takes a whole number; send priority=1, priority=2 or another whole number. The id is wrong too: 'tk_1_version_option_show_python' is a row of tickets, not of items, and its item is 'version_option_show_python'. Send id='version_option_show_python' with the number
```

The absent-id form, s200 turn 4 on night 115:

```
problem.prioritize: priority='high' is a word where problem.prioritize takes a whole number; send priority=1, priority=2 or another whole number. The id is wrong too: 'tk_2_version_option_show_python' is no row of items; items rows are [...]. Send the id of a row of items with the number
```

On a copy of each night's database (observed: `test_scalar_door.py`, 2026-10-06):

- s249 turn 3 and s200 turn 3: the offer is `problem.prioritize(id='version_option_show_python', priority=1)`. `follow` gives `second: None`, and the one `row` fact holds.
- s200 turn 4: the offer is `problem.prioritize(id=api.INVENT, priority=1)`, the id door's shape. The listed rows hold as facts. The dry run fills the id with `x_follow0_id`, and `_must_exist` refuses it. The id door's own offer on `problem.prioritize` meets the same refusal, so this is the id door's class and not a new door.

So 4 of the 5 doubly wrong refusals on nights 113 to 126 now offer a call that lands. The fifth carries the id door's own offer. s249 turn 5 had a right id and is unchanged.

## 2. Finding 2, five mutants survived

Seven tests were added, so the file holds 24. The review's plugin ran against the file with M8 matched to pass 2's line, plus three mutants of the new code (observed: `scratchpad/f164/mut2/mut_plugin.py`, 2026-10-06). **14 of 14 mutants are caught.**

| mutant | failed tests |
|---|---|
| M1 no string annotation branch | 3 |
| M2 no Union branch | 1 |
| M3 no `strip()` | 1 |
| M4 no `'1'` and `'0'` | 1 |
| M5 no finite check | 1 |
| M6 the sentence always says `text` | 19 |
| M7 no replacement of the value | 5 |
| M8 no `api._offer` | 4 |
| M9 `int` read as `float` | 1 |
| M10 no hook in `Sandbox.call` | 4 |
| M11 no `whole` in the sentence | 5 |
| M12 the offer keeps the seat's id | 3 |
| M13 no id half | 3 |
| M14 an empty name with `op=None` | 1 |

The new tests:

- `test_the_offer_of_s249s_turn_5_is_recorded_and_admitted`: `api.RECORD` set, a collecting `_ON_REFUSAL`, the offer `problem.prioritize(id=..., priority=1)`, and `second is None`.
- `test_a_ticket_id_with_a_word_gets_one_refusal_that_names_both`, for s249 turn 3 on night 126 and s200 turn 3 on night 115.
- `test_an_absent_id_with_a_word_gets_the_id_doors_offer`, for s200 turn 4 on night 115.
- `test_a_padded_true_and_the_digits_are_truth_values`: `' true '`, `'1'`, `'0'` and `'False\n'`. Python's `int()` and `float()` accept spaces by themselves, so only a `bool` shows `strip()`.
- `test_an_optional_scalar_annotation_object_is_read`: `int | None` and `Optional[int]` as objects, on a stub signature.
- `test_a_call_with_no_op_names_the_function`.

The night tests skip when the night's file is absent.

## 3. Finding 3, the empty name

With `op=None`, `dotted` is now `fn.__name__`. The sentence reads `a='x' is a word where stub takes a number; ...`. Pass 1 also dropped a space in `checks = {**ENUMS, ...}`, and pass 2 puts it back.

## 4. Finding 4, run 2 of the re-recorded case

The re-record of `L1-VK-relay-the-ruling` in pass 1 changed the shape of run 2 (observed: the review's `cassette_cmp2.py`, 2026-10-06). Run 2 has 3 turns and 2 calls, `problem.set_approval` and `problem.prioritize`, once each. Its reply is two closing think tags and the JSON object `{"id": "i_0dbd2f", "approval": "approved", "priority": 1}`. The run is green. Runs 1, 3, 4 and 5 keep the calls of the old live run. Only their last prose moved, from `"1"` to `1`. A later stale read should not count run 2 as a new wall.

## 5. The replay

The binder replay of pass 1 ran again on the pass 2 tree. It gives the same result: 20398 calls, 67 differ, and all 67 carry text for a typed scalar. The id half needs a connection, and the replay sends none.

## 6. The gate's five lines

The command was `D:/repos/rota/.venv/Scripts/python.exe -m rota.tools.gate`, run in the worktree and backgrounded (observed: 2026-10-06, about 17:50 to 18:07):

```
suite: 23 failed, 3022 passed, 34 skipped, 12 xfailed, 18 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 864.6s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds are the three that fail at `ebed3ae1` with the door stashed (observed: pass 1, section 6 of `plans/frame164-pass1.md`, 2026-10-06). The baseline is from 658abb6. No case is stale, so no re-record ran.

## 7. Deviations

- The repair names a ticket's, a batch's or a criterion's item, which the brief did not name. The brief's `api.INVENT` alone would leave every offer of the four ticket-id refusals refused by `_must_exist`. The item is a fact of the row, so the offer lands.
- The mutant run used the review's plugin with `-n0`. M8's old line no longer exists, so the copy matches pass 2's line.

## 8. Seen and not fixed

- The id door of `_bind` offers `id=api.INVENT` on `problem.prioritize`, which needs an existing row. That offer meets `_must_exist` in a dry run. The scalar door's absent-id offer inherits the same shape.
- The review saw that `1e3` and `0x10` for an `int` read `is a word`, and that `1_000` converts to 1000. Both are Python's `int()`, and pass 2 left them.
- Of the 61 converted calls, 16 meet another door after the conversion: 10 the id door and 6 `_must_exist` (the review, point 1). Those refusals are as before.

## 9. Report

- `rota/core/sandbox.py`: `_must_exist_table`, `_scalar_id_fault` and `_item_of` come before `validate_args`. The scalar door's offer takes the id half, and `dotted` falls back to `fn.__name__`.
- `tests/rota/test_scalar_door.py`: 24 tests, with the helpers `_night_copy` and `_refused`.
- The harness reports the pass's token usage to the assistant.
