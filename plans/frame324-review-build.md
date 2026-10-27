# Frame 324, review of f57eb508: the ruled partition through one reader

Read-only review. Worktree `C:/Users/roman/rota_r324b` at f57eb508, parent d495db74. Reviewer on Opus, 2026-10-27 01:44.

## Verdict

**The build holds on its six points. It adds one high defect and leaves one high gap. Do not merge as is. Two small fixes bring it to merge.**

- High, added by this change: the one-program door now admits `from src.click... import`, because `_module_kind` reads the folder `src` as program (finding 1).
- High, a gap in the ruling's scope: `_named_callables` still decides the partition by name, so the criteria wake pushes the example's `clear` source before the library's (finding 2).
- The listing, the probe, the surface door and the 14 STALE cases are as the build report says. Probes on night 167's real index confirm them.

## (a) The verdict on each point

1. One reader: PARTLY. `kind_of` is right. Seven sites still decide the partition by path pattern, and `_named_callables` is the one that feeds the seat (finding 2).
2. s280's red test: CONFIRMED. The test is red on d495db74 and green on f57eb508. On night 167's real index the listing puts `src/click/termui.py::clear` first with kind `program`.
3. The ranking deviation: CONFIRMED. The library's `clear` comes first for every night 165 and 167 hint. A common word moves a wrong symbol first inside the program rows (finding 4, low).
4. The surface door: CONFIRMED. On night 167 the door refuses the full example path and names `src/click/termui.py::clear`. `read_config` keeps its outcome. No test holds the `read_config` negative (finding 5, low).
5. The 14 STALE cases: CONFIRMED. The listing and probe change is the whole cause. No case can fail before re-recording in any way other than STALE.
6. Weakened assertions: none in the changed test. One new place test passes while the encode is refused (finding 6, low).

## Point 1. The one reader

CONFIRMED for the reader. `kind_of` (`areas.py` 82 to 96) reads `ruling_for`, then `is_attached`. It strips `::name`. It returns one of the four stored values. An old run database with no `frame_rulings` table falls back to the heuristic, because `ruling_for` catches `sqlite3.Error`.

The remaining path patterns in `rota/`, sorted:

| Site | Decision | Verdict |
|---|---|---|
| `api.py` 5225 to 5246, `_named_callables` | the surface candidates and their order, for the criteria wake's `code.source` push, `_criteria_raise_lines` and the exception door | partition. Must read `kind_of` (finding 2) |
| `api.py` 19572, the copy door of a Developer write | "a name the index holds in one other module". `_is_test_path` drops tests and keeps `examples/` | partition. A demo's `clear` makes the library's `clear` a "convention", so a copy passes (PLAUSIBLE, finding 3) |
| `runner.py` 4710, the Tester's touch push | `startswith("tests/")` picks the test paths of the touch set | partition. Low. A project with `test/` gets no push |
| `scheduler.py` 1331, `lexicon.py` 248 | boundary subjects and vocabulary paths, by `is_attached` | partition. Low. A ruling does not reach them. The build report names both (question 3) |
| `areas.py` 237, the edges of `propose` | `is_attached` on each edge end | partition, inside the reader's own module. Low. A ruled `program` file under `examples/` loses its edges |
| `api.py` 13238 `_is_prose_ref`, the docs count of `boot.py` | prose or not | prose check. Keeps its own, as the build report says |
| `api.py` 8720 `_defined_in`, 17226 `_dotted_module`, 18247, 19305 to 19331, 19838 | import resolution and the `src` or `lib` layout | project edge. Keeps its own |
| `api.py` 19621, the Developer's test-file refusal, and 21482, 21500, the stray detectors | is this a test file, the Tester's ownership | test-file shape, not program or demo. Keeps its own |
| `api.py` 16468, 16574 | the judge's proposal before a ruling exists | the heuristic is the input. Keeps its own |
| `nightreport.py` 430, `samplerepo.py`, `scenes.py`, `scaffold.py` | tools and fixtures | not doors. Keep |

## Point 2. s280's red test

CONFIRMED.

- `test_frame324_one_reader.py` on a scratch copy of the d495db74 tree: 13 failed, among them `test_s280_listing_shows_the_programs_clear_first_with_its_kind`. At f57eb508 the two frame 324 files give 23 passed.
- The test uses 12 copied rows. On a copy of `.rota/clickI_night167.db`, with the words of m150 as the hint, d495db74 shows `examples/termui/termui.py::clear` at row 0 and the library's `clear` at row 8. f57eb508 shows `src/click/termui.py::clear`, kind `program`, at row 0, and the example at row 11, kind `attached`.

## Point 3. The ranking deviation

CONFIRMED, with one low cost. Night 165's index, and the hints of the `clear_screen_return_status` item:

- The item text, the guess hint of s199: f57eb508 puts the library's `clear` at row 0. d495db74 put the example's `clear` there.
- The ticket text, the c_1 hint of s214: the library's `clear` is at row 0, and the example is at row 1.
- "Add a format option to the command so the file output keeps its style": rows 0 to 5 are `core.py::Option`, `core.py::Command`, `decorators.py::option`, `decorators.py::command`, `termui.py::style` and `types.py::File`. click holds no symbol named `format`, so "format" moves nothing.
- "The progress bar should format the label and echo it to the file": row 0 is `src/click/types.py::File`, and `_termui_impl.py::ProgressBar` is row 5. The word "file" moves the wrong symbol first (finding 4).

## Point 4. The surface door

CONFIRMED. `criteria.respecify` on a copy of night 167, criterion `tk_3_clear_screen_return_success`:

- `examples/termui/termui.py::clear`: d495db74 stores it. f57eb508 refuses with "the frame marks that file attached, not program code. The program defines clear too: src/click/termui.py::clear."
- `examples/aliases/aliases.py::read_config`: frame 215's wall refuses it on both commits, with the same text. The outcome holds.
- `src/click/termui.py::clear`: both commits store it.
- The W5 read asked for a refusal when "the bare name has exactly one program row". The build refuses at one or more rows and lists up to five. This choice is defensible and needs no fix.

## Point 5. The 14 STALE cases

CONFIRMED. The cause is the listing and probe change, the column and the order together.

- By mode: Architect `annotate` and `guess`, 5 cases: `L1-AR-annotate-a-batch`, `L1-AR-annotate-from-the-guess`, `L1-AR-guess-the-code-of-a-request`, `L1-AR-re-annotate-from-the-principals-correction`, `L1-AR-rewrite-the-guess-from-the-ruling`. Terminologist `criteria`, 2 cases: `L1-TE-a-docstring-ticket-gets-a-docstring-criterion`, `L1-TE-a-new-behaviour-is-a-new-callable`. Critic `challenge`, 1 case: `L1-CR-challenge-a-claim`. Developer, 2 cases: `L1-DV-act-on-an-answered-challenge`, `L1-DV-read-the-map-not-the-whole-file`. Vision Keeper, 4 cases: `L1-VK-orient-the-program`, `L1-VK-reconcile-the-readme`, `L1-VK-reorient-the-account`, `L1-VK-survey-an-area-for-what-it-does`.
- The probe used one register copy, the 14 node ids and three trees. f57eb508: 14 failed, each `STALE`. d495db74: 14 passed. Variant A is f57eb508 with `_frame_ranked` a no-op, the hint sort removed and the probe note restored: 14 passed. So no other part of the change touches these prompts.
- The column is not the only cause. The order also changes the text, as point 2 shows. A re-record must cover both.
- Before a re-record, a case can only fail as STALE. `test_l1.py` 194 fails on "no cassette" before any assertion runs. The width risk comes after the re-record. `_prompt_overrun` (`runner.py` 1800) adds an error when the prompt passes the budget. The column adds about 10 characters to a row, so about 400 for 40 listing rows and 600 for 60 probe rows. This risk is PLAUSIBLE and low on a 16384 window.

## Point 6. Weakened assertions

CONFIRMED, none weakened. `test_frame324_program_rank.py` changes one test from "kept" to "refused, and the text names the library's path". The ruling of 20:37 replaces the clause that the old test held. The guess half keeps its assertion.

`place_known_modules` is weak (finding 6). Another door refuses its encode. The test checks only that the text lacks "no module of".

## (b) Findings

1. `rota/roles/api.py` 9820, the one-program door with `_module_kind`. **High.** CONFIRMED. The batch's test imports `click`, and the new body is `from src.click.termui import clear`, on a criterion with no surface. d495db74 refuses: "this test imports src ... a second module is a second program". f57eb508 stores the test. `_module_kind("src")` matches the folder `src` at depth 0, and its files are program. The W5 read recorded the three `src` refusals of night 166 as right. With the surface `src/click/termui.py::clear`, a later door still refuses the import. Fix: test `m in _program_modules(ctx.conn)` in place of `_module_kind(ctx.conn, m) == "program"`.
2. `rota/roles/api.py` 5225 to 5246, `_named_callables`. **High.** CONFIRMED. On night 167 the hint "clear returns True if it cleared the screen" gives `['examples/termui/termui.py::clear', 'src/click/termui.py::clear']`, the example first. The criteria wake pushes `code.source` from this list (`runner.py` 4492 to 4512). `_criteria_raise_lines` and the exception door read the same list. So the seat still reads the demo's source first. The same filter, `startswith("test")` on the file name, drops `src/click/testing.py`: the probe lost `make_input_stream`. Fix: drop an `attached` or `ignore` row that has a program twin, sort the rest by `_KIND_RANK`, and test tests with `kind_of` plus `is_test`.
3. `rota/roles/api.py` 19572, the copy door. **Low.** PLAUSIBLE. The set of other definitions excludes test paths only. With `clear` in `examples/` and in `src/`, a second `def clear` reads as a convention and passes. Fix: keep only rows where `kind_of(...) == "program"`.
4. `rota/roles/api.py` 16729 to 16732, the hint-word key of `code_callables`. **Low.** CONFIRMED. "...echo it to the file" puts `types.py::File` before `ProgressBar`. `criterion_repair.md` still says "The list ranks by fan-in, not by fit", and that text is now false. Fix: state the real order in the mode text at the next re-record.
5. `tests/rota/test_frame324_one_reader.py`. **Low.** CONFIRMED by grep. No test holds the `read_config` negative that the W5 read asked for. The probe shows that the outcome holds today. Fix: add the negative beside `test_s280_full_example_path_is_refused_and_names_the_programs_clear`.
6. `tests/rota/test_frame324_one_reader.py` 250 to 262, `place_known_modules`. **Low.** CONFIRMED. The encode returns "Import the surface from its own module: `from python.bank.core import charge`". That advice is wrong for a `python/` source root, and the test passes. Fix: assert that the encode lands, or assert the exact refusal.

Outside the points:

7. `rota/roles/api.py` 7468 to 7484, `_program_modules`. **Low.** PLAUSIBLE. A program file in a folder with no `__init__.py` adds its stem, so `scripts/run.py` makes `run` a known module. Before, only the root and `src` or `lib` counted. Fix: add a stem only for a file at the root or under a source root.
8. `rota/roles/api.py` 10219 to 10228, the known modules. **Low.** PLAUSIBLE, question 4 of the build report. A package that the batch adds under `src/` is not in the index yet. It is no longer known once the index holds one program `.py` file. Fix: join the `src` and `lib` glob to the set, and do not use it only as a fallback.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e03f97fc-cdd4-4daa-864c-2ca4d7ef42a5/scratchpad/r324/`.

- `old/`: `git archive d495db74` of `rota`, `tests`, `pytest.ini` and `rota_serial_plugin.py`, with the new test file copied in. `varA/`: the same of f57eb508, with `patchA.py` applied to undo the listing and probe change.
- `db/n167.db` and `db/n165.db` are copies of the night databases. `db/reg.db` is a copy of the register. No probe opened an original.
- `p2.py`: `code.callables` on night 167 with the words of m150, both trees (point 2).
- `p4.py`: `code.callables` on night 165 with the item text, the ticket text and two common-word hints, both trees (point 3).
- `p5.py` and `p5b.py`: `criteria.respecify` with four refs on night 167 and night 165, both trees (point 4). Night 165 refuses all four by an earlier door, so it shows nothing.
- `ids.txt`: the 14 node ids. pytest ran them with `ROTA_DEV_DB=db/reg.db` at f57eb508, `varA/` and `old/` (point 5).
- `p6.py`: the encode text of three place tests (point 6, finding 6).
- `p7.py` and `p7b.py`: the one-program door on `src.click.termui` and `termui` imports, with and without a surface (finding 1).
- `p8.py`: `_named_callables` on night 167 (finding 2).
- `p9.py` and `p9b.py`: the import hint scan with a bare surface. The hint was right, so this probe gives no finding.
- pytest of `test_criteria_surface.py`, `test_frame324_program_rank.py` and `test_frame324_one_reader.py` at f57eb508: 64 passed.

## (d) Usage

- Input tokens: about 120k cumulative (estimate, no counter shown).
- Output tokens: about 15k (estimate).
- Total: about 135k.

## Pass 1b

**Pass 1b at ec6edb90 stands. Both high findings are fixed, and the probes confirm both. Of the four lows left, three reasons hold. Low 8's reason does not hold, but low 8 does not block a merge.**

Probes: `git archive ec6edb90` into `r324/p1b/`, then the same scripts as above. The four test files `test_frame324_one_reader.py`, `test_frame324_program_rank.py`, `test_criteria_surface.py` and `test_prompts.py` give 102 passed.

1. The high findings: FIXED, CONFIRMED.
   - Finding 1: `p7.py` and `p7b.py` give "this test imports src, ... a second module is a second program" with a surface and without one, as on d495db74. `termui` is still refused. `place_one_program` still lands, so `billing` beside `store` passes.
   - Finding 2: `p8.py` on night 167 gives `['src/click/termui.py::clear']` for the `clear` hint. The example has a program twin, so it is dropped. `src/click/testing.py::make_input_stream` is back. `examples/aliases/aliases.py::read_config` has no twin, so it stays, after the program row.
   - The listing of point 2 is unchanged: `src/click/termui.py::clear`, kind `program`, at row 0.
2. The remaining path patterns: no new partition site. Beside the sites that point 1 accepted, the wider grep finds test-function names (`api.py` 8499, 9409, 9512, 9836, 18127, 19548) and the new-file layout (19303, 20059). These are not program or demo decisions. The partition sites that remain are those of point 1: `runner.py` 4710, `api.py` 19559 (low 3), `scheduler.py` 1331, `lexicon.py` 248 and `areas.py` 237. Two more sites are low and PLAUSIBLE. These are the worktree scans at `api.py` 10238 and 10372. They skip `tests` only, so the first file that defines a name can be in `examples/`. `p9b.py` showed a right hint for 10238, and no probe reached 10372.
3. The lows left:
   - Low 3, the copy door: the reason HOLDS. The change alters which second definition counts as a convention, and that needs its own tests. Keep it on the frame's open list.
   - Low 6, `place_known_modules`: the reason HOLDS. An exact assertion would pin the wrong `from python.bank.core` advice. The test checks the door it names. The advice is the hint scan's defect, and it is a separate item.
   - Low 7, the stem of a file with no `__init__.py`: the reason HOLDS. A source-root rule is a design choice, and the cost today is a door that admits too much.
   - Low 8, the `src` and `lib` glob used only as a fallback: the reason DOES NOT HOLD. "Still open" does not justify it, because pass 1 made the regression and a union with the glob restores the parent's behaviour with no design choice. Fix: `_known |= _program_mods` and the glob always, in `api.py` 10210 to 10216 of ec6edb90.

Usage, pass 1b: about 14k input and 3k output (estimate).
