# Review: frame 362, shape pass S1, `34cd529a` (2026-11-04 01:23)

Verdict: stand. No finding is high. Fix the two medium findings before the measure of step 9. The worktree `C:/Users/roman/rota_r362s` at `34cd529a` stayed read-only. The targeted tests pass, 51 of 51 (`test_f362_shape_s1.py`, `test_identity.py`, `test_index_refresh.py`).

## (a) Verdicts by point

1. CONFIRMED. The map names two writers of `code_calls`, both in `indexer.build` (indexer.py 510, 533), and no other writer. The build deletes and rewrites every row, not only the rows of the changed files. An edit of `a.py` changed only the rows of `a.py`. A rename in `b.py` removed the row of the unchanged `c.py` too, and that is correct.
2. CONFIRMED. On the icalendar pin the row is `src/icalendar/parser/content_line.py -> src/icalendar/parser/string.py::_foldline`. At the pin `content_line.py` imports from `parser.string` directly, so the re-export does not fire there. A fixture that imports through `parser/__init__.py` gives the same row. Calls on `self`, on an instance, through `getattr`, `globals()` and `eval` give no row and no error.
3. CONFIRMED. My own run of `_reexported`, `modules()` and `bind` on the three pins at `bf1c8c8a` and at `34cd529a` gives two files of 137,221 bytes, and `cmp` is clean. The binding rule shares `Tree.modules()` and `Tree.absolute` only. It does not read `definer`. One change is outside the pins: see finding 7.
4. CONFIRMED. The query reads `code_index` symbols only, so methods stay out. The click pin gives 4 pairs, and all 4 are true for a designer: 4 of 4. See the list below.
5. CONFIRMED for the fields. The prompt has a gap. On tips with hint "tip", `main.py::calculate_tip` has `copies: ["tip_calculator.py"]` and `entry_point: "__main__ guard"`. `tip_calculator.py::calculate_tip` has `copies: ["main.py"]` and no `entry_point`. The composed guess prompt differs by the two added lines only. The sentence says what the fields mean. It does not tell the Architect what to do with them (finding 1).
6. CONFIRMED. Two cases go STALE: `L1-AR-guess-the-code-of-a-request` and `L1-AR-rewrite-the-guess-from-the-ruling`. The guess prompt hash moves from `517b378b` to `9a7b6caf`. The checkout gate at 01:12 tried the new hash and wrote 5 `no cassette` misses for each. The other 9 cases that carry a `code.callables` push replayed green after the commit, and no transcript holds `copies` or `entry_point`. The gate re-records stale cases by itself, five live runs each, unless a model holds the main card (exit 3) or `--no-rerecord` is given.
7. CONFIRMED. On the icalendar pin, `build` takes 1.74 to 1.86 s with `code_calls` and 0.92 to 1.01 s without, in steady runs. The first runs took 2.6 to 3.4 s and 1.4 to 1.6 s. The call pass costs about 0.8 s: walk 0.15, parse 0.25, resolve 0.30. The design prices this fact at 0.36 s plus a shared parse (finding 5).
8. CONFIRMED. The test rows are readable. On icalendar 41 of the 65 program targets have a test caller row, as the design counts, and a reader filters with `areas.is_attached`. The table has no reader yet. The same-file omission hides a copy that its own file calls. On tips `main.py` calls its own `calculate_tip`, and no row shows that. Only the entry-point mark tells the live side, and a library copy pair has no entry point (finding 3).

Point 4, the click pairs:

- `get_pager_file`, `termui.py` and `_termui_impl.py`: the public wrapper and the work. True.
- `getchar`, the same two files: the wrapper imports the platform implementation lazily. True.
- `raw_terminal`, the same two files: the same wrapper form. True.
- `_get_windows_console_stream`, `_compat.py` and `_winconsole.py`: the non-Windows stub and the Windows work. True, because a change of one must read the other.

So the copies kind reads 2 of 2 on tips, 4 of 4 on click and 0 of 3 on icalendar. Part one of the keep rule of section 6.1 holds on two repositories.

## (b) Findings

1. `rota/roles/prompts/architect/guess.md` lines 6 to 7. Severity medium. CONFIRMED by the diff of the composed prompt. The sentence defines `copies` and `entry_point`, and gives no step. Section 3.1 wants the guess to name both copies or the live one. Section 7 says a small model may name one copy. Fix: add one instruction, for example "When a row has `copies`, name the copy whose file has an `entry_point`, or name both."
2. `rota/onboarding/harvest.py` line 250, `_imports`. Severity medium. CONFIRMED. The resolver collects definitions from `module.body` only, while the index holds definitions under a module-level `if`. So `copies` counts the click pairs `getchar` and `raw_terminal`, and `code_calls` cannot reach them. `termui.py` has no row to any of the four click copy names. `raw_terminal` fails on this rule, `get_pager_file` on finding 4, and `getchar` on an indirect call through `_getchar`. Fix: collect definitions from module-level `if` and `try` bodies too, and test the click `raw_terminal` row.
3. `rota/onboarding/harvest.py` lines 304 and 327. Severity low. CONFIRMED on tips. A same-file call writes no row, so a copy that its own file calls looks uncalled. The design accepts this for tips, because the guard tells the live side. A library copy pair has no guard. Fix: write same-file rows with a marker column, or record the limit in section 3.1 before the copy push of step 5.
4. `rota/onboarding/harvest.py` line 304, `calls`. Severity low. CONFIRMED. A module definition wins over a function-local import of the same name. The click wrapper `termui.get_pager_file` imports `get_pager_file` inside its body, so its call to the work gives no row. A parameter that shadows an imported name gives a false row (`pkg/shadow.py` in probe 4). A star re-export, `from .star import` with a star, gives no row. Fix: resolve a bare name in the scope of its function first, and expand a star import through the top-level names of the target.
5. `rota/onboarding/indexer.py` lines 546 to 572, `_calls`. Severity low. CONFIRMED. `Tree(root)` walks the tree again with `indexer.walk` and parses every file again with `ast`. The call pass costs about 0.8 s on icalendar, twice the price in the design. After a merge `harvest.record` builds a third `Tree`. Fix: build one `Tree` in `refresh` and pass it to `build` and to `harvest.record`, or set the price in the design to 0.8 s.
6. `rota/onboarding/shape.py` lines 58 to 72, `entry_points`. Severity low. CONFIRMED. Every `__main__` guard is an entry point, with no filter. On icalendar `cal/lazy.py`, `fuzzing/ical_fuzzer.py` and `timezone/equivalent_timezone_ids.py` carry `__main__ guard`. Section 6.1 keeps guards only if a filter of fuzzers and module demos takes icalendar to 6 of 10. All three `main` copies on icalendar carry an `entry_point`, so the mark tells no live side there. Fix: give a guard with no script and no README line the reason "module demo", or record that the step 9 measure decides the filter.
7. `rota/onboarding/harvest.py` line 651, `_reexported`. Severity low. CONFIRMED. A two-dot relative re-export, `from ..core import helper` in `pkg/sub/__init__.py`, bound nothing before and binds `pkg/core.py` now. The change is right, and no pin and no test covers it. Fix: add a test that pins the two-dot form.
8. Outside the points. The pass report, section "Open questions". Severity low. CONFIRMED. The pass report does not name the two STALE guess cases, and the re-record is a live measurement of the new sentence. Fix: read the re-recorded verdicts of the two guess cases before step 5 starts.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/535a30c6-b4f1-4ae7-85bc-11d741145722/scratchpad/r362s1/`. Each puts its tree root first on `sys.path`.

1. `pins/`: the three pins, read out again with `git archive`. `diff -rq` against `s1pins` of the pass is clean.
2. `before/` and `after/`: `git archive` of `rota/` at `bf1c8c8a` and at `34cd529a`.
3. `p1_calls.py`: point 1, the two-file and three-file rebuild, and point 2, the re-export, attribute, string, star, cycle and two-dot fixture.
4. `p2b.py`: point 2, the attribute, string, star and shadow calls through `Tree.calls`.
5. `bind.py` with `b.json`, `a.json` and `w.json`: point 3, the binding comparison at both commits and at the worktree.
6. `p3b.py`: point 3, the two-dot re-export at both commits.
7. `p5_door.py`: point 5, `code.callables` on the tips pin, with and without `project_root`.
8. `p5_prompt.py` with `pb_guess.txt` and `pa_guess.txt`: point 5, the composed prompts and their hashes at both commits.
9. `p6_cases.py`, `p6b.py` and `p6c.py`: point 6, read-only queries on `D:/repos/rota/tests/rota/cassettes.db` for `case_runs` and `key_misses`.
10. `p7_cost.py` and `p7b.py`: point 7, the build time with and without `_calls`, and the walk, parse and resolve split.
11. `p8_ical.py`: points 4 and 8, the entry points, the test callers and the copies on icalendar and click.
12. pytest: `tests/rota/test_f362_shape_s1.py`, `test_identity.py` and `test_index_refresh.py`, 51 passed.

## (d) Usage

Input tokens: about 100k, estimated, because the harness shows no counter. Output tokens: about 16k, estimated. Total: about 116k. No sub-agent started.
