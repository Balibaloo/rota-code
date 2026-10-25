# Frame 324, pass 1: the review of 3ca7afaa

Verdict: Stands. The six points hold. One medium finding and two low findings remain for a later pass.

## (a) The points

1. Holds. s214 stores `src/click/termui.py::clear` through `criteria.specify` with the frame rulings in place (probe C).
2. Holds. With its own path, s199 writes the guess `src/click/termui.py::clear`. With neither path in `paths`, the frame rank picks the `src` row and writes a guess. That follows R. With only the example path in `paths`, the example wins, as R says "a row inside the seat's own paths wins first".
3. Holds. With no `frame_rulings` row, `is_attached` marks `examples/` attached and the `src` row wins. The refusal for two `program` rows, verbatim: "echo_via names 3 symbols in the index, and 2 of them are program code. Write one as path::name, the program's first: src/click/_compat.py::echo_via, src/click/termui.py::echo_via, examples/termui/termui.py::echo_via". `batches.guess` adds ". Or leave symbols out".
4. Holds. A qualified `examples/...::clear` is stored as written at both doors. The single-row tests pass at 23588406 and at 3ca7afaa. The single-row refusal of deviation 1 is not part of the wall. Provenance section 4 shows that all six repeats on a unique name wrote a guess on a later call.
5. Holds. No other caller can store an `examples/` surface from a bare name. In `api.py`: 2006, 5555, 5580, 5622, 5637 and 5645 only check that the name exists. 4561 returns None when more than one row matches. 5132 and 18743 read only, and 18743 filters to the exact name. 5056 `_callable_source` takes the first row for a bare ref. It reads source and stores nothing. `batches.annotate` (7383) stores symbols as written, and that includes bare names. It does not resolve a name to a path, so it cannot pick the example.
6. Holds. The seven named files pass with 168 passed. The new file gives 5 failed and 2 passed at 23588406. The L1 TE and AR run gives 7 failed and 37 passed at both commits, with the same seven ids. The commit changes no existing test, so no assertion is weaker.

## (b) Findings

1. `rota/roles/api.py` 5284 to 5285 and 7289 to 7291. Medium. CONFIRMED. SQLite `LIKE` ignores case for ASCII, and `_` matches any one character. The probe (E) indexed `examples/termui/termui.py::clear` and `src/click/core.py::Clear`. For bare `clear`, both doors silently stored the class `Clear`. Before the fix the example row was stored. That row had the wrong path but the right name. The resolver now promotes a different symbol with no refusal. Fix: before the resolver runs, keep only the rows whose grain ends with `::` plus the exact name, as line 18743 does.
2. `tests/rota/test_frame324_program_rank.py` 48 to 51. Low. CONFIRMED. In every test, the fixture rulings agree with `is_attached`. Thus no test fails if `ruling_for` is removed from the resolver. Probe B ruled `examples/termui` as program and `src/click/termui.py` as attached. The door then stored the example, so the code reads the ruling correctly. Fix: add a test where the ruling and the heuristic disagree.
3. `rota/roles/api.py` 7309 to 7341. Low. CONFIRMED. The call `symbols=["clear", "src/click/termui.py::clear"]` writes the same grain twice and returns `grains: 3` (probe G). Fix: remove duplicate entries from `resolved` before the writes.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b18846fb-98a1-4a67-92e0-2b450b5603d8/scratchpad/r324/probe1.py`. The probe reuses the fixture of the new test file. It runs `ruling_for`, both doors with the frame rulings, a ruling that disagrees with the heuristic, two `program` rows, a case-only match and a duplicate symbol.
- `scratchpad/r324/base` is a `git archive` export of 23588406. The new test file and the L1 `-k "L1-TE or L1-AR or ACT-TE or ACT-AR"` cases ran in it. A cassette copy was used and then deleted. The results are in `scratchpad/r324/l1_base.txt` and `scratchpad/r324/l1_head.txt`.
- The pin command from the report ran in `C:/Users/roman/rota_r324`. The worktree cassette copy is deleted, and `git status` is clean.

## (d) Usage

About 55k input tokens and 7k output tokens, about 62k in total, against a cap of about 15k.

## Re-check of 11618573

1. Holds. In the new test, a bare `clear` beside a class `Clear` stores `src/click/termui.py::clear` at both doors. Probe E now stores the example's `clear` and refuses at `batches.guess` with the text of 23588406.
2. Holds. The source shows the test fails without the ruling read. `test_the_frame_ruling_outranks_is_attached` expects `EXAMPLE`. Without `ruling_for`, `is_attached` makes `src` the program, and the door stores `LIBRARY`. The trigger stamps `frame_provenance`, so the rulings are read (probe A).
3. Holds. Probe G writes `src/click/termui.py::clear` once, through `dict.fromkeys`.
4. Holds in part. `batches.guess` is byte-equal to 23588406 for a name with no exact row (probe H). `criteria.specify` is not byte-equal when two or more rows match only by case. The probe used `examples/termui/termui.py::Clear` and `src/click/core.py::Clear`. For bare `clear`, 23588406 stores the `examples/` row and 11618573 stores the `src/` row. Low. CONFIRMED (probe H at both commits). Both doors store a symbol of the wrong case. Fix: refuse a bare name that has no exact row, or correct the deviation text to say the program row wins.
5. Holds. The seven files give 171 passed. The commit adds three tests and changes no existing assertion.

Probes: `scratchpad/r324/probe1.py` and `scratchpad/r324/probe2.py`. Probe 2 ran in the worktree and in the 23588406 export. Usage: about 9k tokens on this re-check.

Stands.
