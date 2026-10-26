# Frame 324, W5 of night 167: the read of the two encode doors that refuse each other's remedy

- Date: 2026-10-26 07:41. Read-only, on Opus. Meta workflow.
- Repository: `D:/repos/rota` at HEAD f92dd3849517e2f9bae3cd6339a8d22461e84bfb, branch `rota/foundation`.
- Count scripts: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4cdad7e1-c78d-472d-86ab-f4c72d52763e/scratchpad/f324w5_count.py`, `f324w5_rows.py` and `f324w5_turns.py` in the same folder.

Sources:

- `plans/night167-walk2-read.md` section 2, `plans/night167-read.md` section 2 row W5 and section 5, and frame 324's block in `plans/stack.md` (status lines of 2026-10-25 10:11 to 10:33 and 2026-10-26 06:46). These are the symptom records. This page cites them and does not repeat them.
- `plans/frame324-provenance.md` sections 2 and 5, `plans/frame324-review-p1.md` section (a), `plans/frame304-provenance.md` section 2.
- The pass-1 brief `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b18846fb-98a1-4a67-92e0-2b450b5603d8/scratchpad/f324_p1_brief.md` lines 37 to 38 and 54 to 55.
- `rota/roles/api.py` at HEAD: `_program_rank` 5364 to 5398, `_vet_surface` 5401 to 5504, `_surface_outside_batch` 5507 to 5574, the one-program check 9640 to 9670, the surface check 10243 to 10274.
- `git log -S` and `git log -L` on both checks. Commits 7b886078, d2091d8c, 4abf0d96, aa23868a, f3de0534, 5b319bc3, 1e57044e.
- `tests/rota/test_desk_guards.py` lines 61 to 95, 3012 and 3890. `rota/testkit/samplerepo.py` lines 60 to 81.
- `D:/repos/rota/.rota/clickI_night163.db` to `clickI_night167.db`, opened with `?mode=ro`: `tool_calls`, `turns`, `receipts`, `criteria`, `tests`, `items`.
- `rota/DECISIONS.md`, `rota/LAWS.md`, `plans/composition.md`, searched for a ruling on surfaces, example files and the one-program rule.

## The result

**A gap, at the respecify door and not at the encode doors: frame 324 kept a qualified path as written on the premise that frame 215's door refuses an `examples/` surface, but frame 215's door admits any surface whose name the item says, so `examples/termui/termui.py::clear` passed and put the Tester between two right checks with no exit.**

The two encode checks each hold a right rule (observed: sections 1 and 4). They contradict only when the surface sits outside the program (reasoned: section 3). The frame-324 build met its ruling. The ruling's clause "a qualified path is kept as written" rests on a premise that the rows of night 165 already refuted (observed: s426 seq 14, section 2).

## 1. Who made each check

| Check | First commit | Date | Case and workflow | Red test |
|---|---|---|---|---|
| One-program check, "one program, one name" (`api.py` 9640 to 9670) | 7b886078 | 2026-09-02 | S0 walk thirty-two: three tests imported `script`, one imported `main`, and `main.py` never existed. Rota workflow case, built in the meta workflow | `test_one_program_one_module_name_across_a_batch`, `tests/rota/test_desk_guards.py` 3012 |
| Surface check, "Import the surface from its own module" (`api.py` 10243 to 10274) | d2091d8c | 2026-09-09 | tipsU: surface `main.py::calculate_tip`, the test imported `billing`. Rota workflow case, built in the meta workflow | the `billing` case inside `test_a_bare_call_of_the_surface_name_is_a_call_of_the_surface`, `test_desk_guards.py` 61 to 95 |

- Neither commit names a frame. Both predate the numbered frames of these doors, and `plans/frame304-provenance.md` section 2 lists them by walk, items 10 and 19 to 20 (observed).
- The surface check grew twice. 4abf0d96, 2026-09-12, clickI night 23, derives the dotted module of a src layout, with `test_a_src_layout_surface_is_imported_by_its_dotted_module` at `test_desk_guards.py` 3890. f3de0534, 2026-10-12, frame 215, night 142, loads the surface's module first and routes an unloadable one to the Terminologist (observed: `git log -L 10243,10274`, the commit bodies).
- The one-program check changed once since, c8f2fa5c of 2026-10-21, in the stdin lines next to it and not in its rule (observed: `git log -L 9640,9670`).

## 2. Why the respecify admits a full `examples/` path

**A choice in pass 1, with a reason, and the reason is wrong** (observed and reasoned below).

- The choice: "A qualified path from the seat is kept as written and never ranked" (observed: pass-1 brief lines 37 to 38, and 54 to 55 for the red test). The review confirmed it: "A qualified `examples/...::clear` is stored as written at both doors" (observed: `plans/frame324-review-p1.md` point 4). The code says the same (observed: `api.py` 5434 to 5437, "A qualified ref stays as written").
- The reason: "A qualified `examples/` path from a seat, as s426 sent, stays outside R. Frame 215's repair-only door covers it at `respecify`" (observed: `plans/frame324-provenance.md` lines 146 to 148).
- Frame 215's door does not cover it when the item names the callable. `_surface_outside_batch` lets a ref pass when its name is in the words of the item, its statements or the ticket (observed: `api.py` 5564 to 5565). The item of night 167 is "Make clear() return True ..." (observed: `items` row `clear_screen_return`), so `clear` passes.
- The rows that disprove the premise existed when the provenance was written. On night 165, s426 seq 14 respecified `c_3_clear_terminal_success` to `examples/termui/termui.py::clear` and got a receipt (observed: `tool_calls`, `receipts` of `clickI_night165.db`).
- s280's receipt shows the move: `"surface_changed": true, "from": ["src/click/termui.py::clear"], "to": ["examples/termui/termui.py::clear"]` (observed: s280 turn 2). The callable list in s280's prompt showed the example row first, with the same fan-in 0 as the program row (observed: s280 turn 1).

The full-path case recurs. Over nights 163 to 167, 29 `criteria.respecify` calls named a qualified `examples/` surface, and 11 stored (observed: `tool_calls` and `receipts` of the five databases). Night 163: 13 calls, 5 stored. Night 164: 6, 2 stored. Night 165: 9, 3 stored. Night 166: 0. Night 167: 2, 1 stored (s280). The names include `clear`, `format_filename`, `get_app_dir` and `read_config`.

## 3. The rows of s280, s281 and s283

- s280, Terminologist on qwen3.5:9b, seq 9: `criteria.respecify(id='tk_3_clear_screen_return_success', surface_refs=['examples/termui/termui.py::clear'], ...)`. Receipt: `criteria`, tk_3, version 2 on the row (observed: `tool_calls`, `receipts`, `criteria`).
- The 8 refusals, each `tests.encode`, in call order (observed: `tool_calls` seq and the results in `turns.user`):

| Session, call | Test id | Import line of the body | Refusal |
|---|---|---|---|
| s281 seq 10 | tst_tk3_v2 | `from click.termui import clear` | surface: "the surface 'examples/termui/termui.py::clear' lives in termui.py and this test imports from click.termui. Import the surface from its own module: `from examples.termui.termui import clear`" |
| s281 seq 11 | tst_tk3_v2 | `from examples.termui.termui import clear` | one program: "this test imports examples, and the batch's other tests import click -- one program, one name. Import from click like the others; a second module is a second program" |
| s281 seq 12 | tst_tk3_v2 | `from click.termui import clear` | surface, the same text |
| s281 seq 13 | tst_tk3_v2 | `from examples.termui.termui import clear` | one program, the same text |
| s283 seq 9 | tst_tk3 | `from click.termui import clear`, inside the test function | surface, the same text |
| s283 seq 10 | tst_tk3 | `from examples.termui.termui import clear` | one program, the same text |
| s283 seq 11 | tst_tk3 | `from click.termui import clear` | surface, the same text |
| s283 seq 12 | tst_tk3 | `from click.termui import clear` | surface, the same text |

Five surface refusals and three one-program refusals. Every body imported one of the two modules and never both (observed: the completions of s281 turns 1 to 5 and s283 turns 3 to 6).

By the code, one body passes both checks: one that imports `examples.termui.termui` and `click` together. The one-program check refuses only when the agreed module `click` is absent from the body (observed: `api.py` 9663 to 9664). The surface check passes when any import matches `examples.termui.termui` (observed: `api.py` 10253 to 10255). Neither refusal names that exit (observed: the texts above). The exit is no remedy. The example's `clear` at `examples/termui/termui.py` line 132 is a click command of the demo program, not the library's `clear` that the item asks for (observed: s281 turn 2, the `code.source` defs). A test through that exit tests the wrong code (reasoned).

The one-program check also misreads the src layout. It asks whether `click.py` or `click/` exists at the worktree root, and click lives at `src/click` (observed: `api.py` 9661). It also reads every test of the database, not the batch's only (observed: `api.py` 9652 to 9653). Neither fact changes W5, because the example import is wrong in either case (reasoned).

## 4. What the two checks refuse that is right

Counts of `tests.encode` refusals, nights 163 to 167 (observed: `turns.user` results, counted per call by `f324w5_count.py`; night 167's 8 match section 3):

| Night | Surface check | of which `examples/` | One-program check | of which `examples` |
|---|---|---|---|---|
| 163 | 13 | 0 | 0 | 0 |
| 164 | 3 | 0 | 2 | 0 |
| 165 | 32 | 30 | 32 | 25 |
| 166 | 0 | 0 | 3 | 0 |
| 167 | 5 | 5 | 3 | 3 |

- The 25 refusals off `examples/` each had an exit that the refusal names (observed: the texts). The one-program refusals named `src` (`from src.click ...`) or `termui` as the module, and both are wrong imports in an installed src layout. The surface refusals named `os`, `click.termui` for a `utils` surface, or `click.testing`. Those are right.
- Some surface refusals off `examples/` refuse a working re-export, `from click import ...` for `src/click/utils.py::format_filename` and `src/click/termui.py::clear` (observed: night 163 s124, night 165 s261). The named remedy imports, so those cost a turn and left an exit (reasoned).
- The 63 refusals on `examples/` all came from the `clear` item: 55 on night 165 in 12 sessions and 8 on night 167 in 2 (observed). Night 165's surfaces came from a bare name, which 5b319bc3 fixed, and from one qualified respecify, s426 seq 14 (observed: `plans/frame324-provenance.md` section 4, `receipts`). Night 167's came from a qualified respecify, which 5b319bc3 kept.
- The sample repository has no `examples/` folder. It is a src layout with the packages `store`, `auth`, `billing`, `catalog` and `notify` (observed: `samplerepo.py` 60 to 81). No encode on it is recorded, so it shows no count. By the code, the one-program check would refuse a test that imports `billing` in a batch whose other tests import `store`, because neither exists at the root (reasoned: `api.py` 9661). That is a latent defect of the one-program check, not W5.

## 5. The smallest remedy

The remedy belongs at the surface door of `criteria.specify` and `criteria.respecify`, in `_vet_surface`. A qualified ref whose path is of frame kind `attached`, when the bare name has exactly one `program` row, is refused, and the refusal names the program row to copy. The encode checks are each right, and an exit through them would make a test of the demo command pass in place of the library's `clear`. So a fix there admits wrong tests, and a fix at the respecify removes the cause of both refusals (reasoned: sections 3 and 4).

Red tests from the rows (observed):

- night 167 s280 seq 9, `examples/termui/termui.py::clear` must be refused and name `src/click/termui.py::clear`;
- night 165 s426 seq 14, the same ref, stored today;
- night 165 s132 seq 7, `examples/aliases/aliases.py::get_app_dir`, stored today;
- a negative test: `examples/aliases/aliases.py::read_config`, whose name has no `program` row, keeps today's outcome.

The rows the fix would have let through the two encode checks: night 167 s281 seq 10 and 12 and s283 seq 9, 11 and 12, the five bodies that import `from click.termui import clear` (reasoned: the surface would stay `src/click/termui.py::clear`). s281's id `tst_tk3_v2` would then meet the one-test door, and s283's re-encode of `tst_tk3` meets frame 328's guard, W3 (reasoned: `plans/night167-read.md` row W3). Night 166 has no row that the fix changes. Its 3 refusals are one-program refusals of `src` imports, and they stay refused (observed).

## 6. A ruling on the surface

**The build did not depart from a ruling. The remedy amends one clause of Roman's ruling of 2026-10-25 10:11.**

- Roman ruled candidate R: "Yeah ok nice, go for it, the decision will be reviewed by the design and review agents right?" (ruled: Roman, 2026-10-25 10:11, `plans/stack.md` frame 324). R as written holds "A qualified path is kept as written" (observed: `plans/frame324-provenance.md` line 131). Passes 5b319bc3 and 1e57044e build that clause (observed: `api.py` 5434 to 5437).
- No ruling of Roman's covers what a surface may name, the example files, or the one-program rule (observed: `plans/frame324-provenance.md` line 81, and no hit in `DECISIONS.md`, `LAWS.md` or `plans/composition.md`).

## The repair

1. At `_vet_surface`, give a qualified ref the same frame kind that `_program_rank` reads. Refuse a ref of kind `attached` when its bare name has exactly one `program` row, and name that row in the refusal.
2. Red tests: s280 seq 9 of night 167, s426 seq 14 and s132 seq 7 of night 165. The negative test: `read_config`, with no `program` row, keeps today's outcome.
3. Price: 1 build cycle and a review, about 40k (reasoned: one predicate in a function that serves both ops, by frame 324's pass 1).
4. Out of scope: the one-program check's root-only existence test and its query over all tests, a latent defect on any multi-package src layout. That needs its own read before a fix, by the rule of 2026-10-18.

## The question for Roman

On 2026-10-25 at 10:11 you approved candidate R for frame 324: "Yeah ok nice, go for it". R keeps a path that a Terminologist writes out in full, on the reason that an older door, frame 215's, refuses a demo program's path. That door lets the path through when the request names the function. On night 167 the Terminologist wrote the full path of the demo program's `clear`. The Tester was then refused 8 times, because one check asks for the demo's import and the other check asks for the library's import.

- **Option A, recommended.** When a full path points into a demo folder and the library has exactly one function of that name, the door refuses and names the library's path to copy. This changes one clause of R. A Terminologist who sends the demo path gets the right path back in one turn.
- **Option B.** Keep R as ruled. The full path stays as written. The Tester keeps meeting the two checks on that item, as on nights 165 and 167.

Usage: about 110k on the harness counter, against a cap of 60k.
