# Frame 324, the agency read: is the fix at the source of its cause

Read-only, 2026-10-26, on Opus, at HEAD 46e5c88b. Register: a copy of `.rota/clickI_night167.db` in this session's scratchpad, `a324/n167.db`, opened `?mode=ro`. No pytest. No file but this one changed.

## The result

**At one door of 13. The built fix covers 2 of 13 places, and the ruled general build covers 8 of 13.** The seat never received the partition. The pushed `[code.callables]` list showed `examples/termui/termui.py::clear` as row 1 and `src/click/termui.py::clear` as row 9, with no kind column. The register held `examples` as attached and `src` as program the whole time (observed: s280 seq 1 `turns.user`, `frame_rulings` of night 167). The frame calls the wall cause 5, "the seat has the fact and judges wrong". By wall-guide section 4, steps 5 and 6, the wall is cause 2, "the prompt lacks the fact", with cause 6 at the doors (reasoned: the prompt holds no partition word, and no door reads `frame_rulings` except `_program_rank`).

## 1. The purpose of the mechanism on the Site line

- The surface door is 395535da of 2026-08-27, "delivery hardened three ways". It closed the delivery wall: a criterion must carry a callable surface (observed: `rota/DECISIONS.md` 1056 to 1064, "Built, 2026-08-26"). The door asks "does the name exist", and it refuses a near miss.
- The same commit built the candidate lens, "pushed question-matched with the wake's subject" (observed: DECISIONS.md 1062 to 1064). That lens is `code.callables` today. The door and the list were one design. The list chooses, and the door only checks existence (reasoned).
- The refusal of `batches.guess` is 7ec9b940 of 2026-10-18, frame 298, under "the architect owns the guess" (ruled: Roman, 2026-10-18, cited in the code). It came for a bare `line_total` on L1 (observed: `plans/frame324-provenance.md` section 2).
- Nobody decided the order of `code_index`. The indexer walks `sorted(root.rglob("*"))` (observed: `rota/onboarding/indexer.py` 345, 448 to 461). Every symbol gets fan-in 0 (observed: the comment at `api.py` 14734 to 14736). So "fan_in DESC" is rowid order, and `examples/` sorts before `src/` (reasoned).

## 2. What exists

| What | Where | What it does |
|---|---|---|
| The ruled partition | `frame_rulings`, `rota/core/schema.sql` 992 to 999 | program, attached, ignore, surface, per prefix, written by the judge or Roman |
| The one reader of a ruling | `ruling_for`, `rota/onboarding/areas.py` 54 to 73 | the most specific ruling for a grain, `decided` first |
| The heuristic fallback | `is_attached`, areas.py 76 to 91; `EXAMPLE_DIRS` 51 | tests, examples, dot-directories |
| The kind of one grain, ruling then heuristic | inner `kind()` of `_program_rank`, `rota/roles/api.py` 5383 to 5387 | already the reader the frame asks for, local to one function |
| The same rule over all paths | `areas.propose`, areas.py 167 to 172 | program set: ruled program, or not ruled attached and not `is_attached` |
| A partition stamped on rows | `areas.pin`, areas.py 259 to 290 | writes `area` only. Attached files get the area they exercise, so `area` does not carry the kind |
| Bare-name rank, built | `_program_rank`, api.py 5364 to 5398; callers 5441 and 7586 to 7600 | frame 324, 5b319bc3 and 1e57044e |
| The ruling writer | api.py 16418 to 16458 | the judge's door, compares with `is_attached` |

The index has no kind column (observed: schema.sql 409 to 425). No reader outside `_program_rank` calls `ruling_for` at run time (observed: grep of `rota/`).

## 3. The reach: every place that shows or binds a symbol without the partition

| # | Place | File and line | The gap |
|---|---|---|---|
| 1 | `code.callables`, the pushed list | api.py 16578 to 16611 | fan-in order is rowid order. Attached rows listed, tests included. s280: example row 1, program row 9 (observed) |
| 2 | `_named_callables`, the source push and raise lines | api.py 5225 to 5245; runner.py 4489 to 4507, 4317 to 4323 | `ORDER BY grain`. Drops tests by pattern and keeps examples. Pushes the example's source first (reasoned) |
| 3 | `code.probe` | api.py 14741 to 14744 | definitions by grain. `examples/` before `src/` (reasoned) |
| 4 | The brief sentence and its pin | `rota/roles/prompts/terminologist/criterion_repair.md` 12; `tests/rota/test_prompts.py` 598 to 608 | "The list ranks by fan-in, not by fit". Every symbol has fan-in 0, so the sentence is false (observed) |
| 5 | `_vet_surface`, a bare name | api.py 5428 to 5446 | built |
| 6 | `_vet_surface`, a qualified ref | api.py 5440 and 5450 to 5462 | kept as written. The program test is a `tests` pattern, so an example passes (observed: W5 read, s280 seq 9) |
| 7 | `batches.guess`, a bare name | api.py 7586 to 7600 | built |
| 8 | `_surface_outside_batch` | api.py 5507 to 5574 | admits any path when the item says the name (observed: W5 read section 2) |
| 9 | The one-program check | api.py 9712 to 9741 | module by root existence. Reads neither index nor partition (observed: W5 read section 3) |
| 10 | The surface-module check | api.py 10129 to 10195 | known modules by glob of root, `src`, `lib` |
| 11 | The stdin scan | api.py 9650 to 9660 | `rglob` of the root, skips tests only. An example's `input()` counts as program (reasoned) |
| 12 | The second-definition door | api.py 19437 to 19466 | `elsewhere` drops tests only. A name that only an example defines sends the Developer to the example (reasoned) |
| 13 | `_callable_source`, a bare ref | api.py 5196 to 5202 | exact name, then rowid. Reads only, stores nothing (observed: review point 5) |

Count: 13 places in `rota/`, 4 of them seat-facing (1 to 4) and 9 at doors (reasoned). The fixture `test_a_qualified_example_from_the_seat_is_kept`, `tests/rota/test_frame324_program_rank.py` 101, pins the old behaviour of place 6 (observed).

The same source made earlier walls. Frame 215, night 142: s536 "set the surface ... to the first row of `[code.callables]`, a module in `examples/`" (observed: `tests/rota/test_criteria_surface.py` 455 to 459). Frame 215 fixed it at the respecify door and in a brief sentence, places 8 and 4. Frame 324 then fixed places 5 and 7. Two frames built four doors, and the list at place 1 never changed (observed: the cited code and pins; reasoned).

Not in the reach: `is_attached` without `ruling_for` at `rota/core/scheduler.py` 1314, `rota/onboarding/lexicon.py` 240 and `rota/onboarding/boot.py` 181. They run in onboarding and pick subjects, not surfaces (reasoned).

## 4. The fix against the reach

- **Built, 5b319bc3 and 1e57044e**: places 5 and 7. 2 of 13 (observed: the diff, `_program_rank`).
- **Ruled 2026-10-26 20:37, the Ends-when**: the probe and the listing (1, 3), the doors on its list that are in the gap (6 through 5454, 9, 10, 11 through 9654), and the bare-name list (5, 7). 8 of 13 (reasoned: the Ends-when line).
- **It leaves** 2 (`_named_callables` and the source push), 4 (the false sentence and its pin), 8 (`_surface_outside_batch`), 12 and 13.
- **7 of its 11 named sites are not this gap.** `api.py` 7407 and 7413 decide where a test file goes. 23137 is `_is_test_path`. `runner.py` 2079 matches his words to a test path. `attached` merges tests and examples, so the partition cannot answer "is this a test" (reasoned: schema.sql 996). `api.py` 9259 refuses a path outside the project. 13145 is `_is_prose`. `rota/core/boot.py` 173 is `discard_running` (observed). A build to that list changes seven doors that are right today.

## 5. My proposal

Not the same fix. The smallest place is the one reader and the three lists that read the index for a seat.

1. Lift `kind()` out of `_program_rank` into `areas.kind_of(conn, grain)`, ruling first, `is_attached` second (observed: api.py 5383 to 5387, areas.py 54 to 91).
2. Order `code.callables`, `_named_callables` and `code.probe` by `kind_of`, program first, and add a `kind` cell to each row (observed: places 1 to 3; reasoned: cause 2's cheap fix, wall-guide 201 to 205).
3. At `_vet_surface`, refuse any ref, bare or qualified, whose kind is not program when a program row of that name exists, and name that row (observed: W5 read, the repair, step 1; places 5 and 6).
4. Replace the false sentence in `criterion_repair.md` 12 with the order the list now uses. Change its pin and the qualified-example pin (observed: place 4, the fixture at test_frame324_program_rank.py 101).
5. Leave places 8 to 13 and the test-pattern doors, and count them on the next nights. With the list right, the encode checks meet no example surface (reasoned: W5 read section 4, all 63 `examples/` refusals came from the `clear` surface).

Price: one cold implementer pass, about 75k; one review, about 70k; one resumed fix, about 25k. That is 3 cycles, about 30k of the holding session (observed: `plans/operating-facts.md` 241 to 245, "A cycle costs the holding session about 10k"). The ruled build is priced at about 2 cycles for 11 sites. This proposal touches 4 functions, 1 brief and 2 pins. The gathering agent of the Waits-on line is not needed: place 1 answers its question from the turn of s280 (observed).

## 6. The doubt

- I read s280 only. A `tick:criteria` wake, such as s214 of night 165, also pushes the item and the source from `_named_callables`. That push can change what the seat saw (not checked).
- Places 11 to 13 are latent by the code. No night row shows them fire (not counted).
- The new order can push program rows of other names past the 20-row and 40-row caps of `code.callables`. One night measures the change (reasoned: api.py 16602 to 16611).

## Verdict

`at one door of 13`: the built fix covers 2 of 13, places 5 and 7. The ruled general build covers 8 of 13, and 7 of its 11 named sites are outside the gap. It leaves places 2, 4, 8, 12 and 13. The cause label of the frame, cause 5, is not the cause the code shows: the prompt of s280 held no partition word, and the list put the example first.
