# Review p1 of frame 356: commit cb758ccd

Verdict: the claim holds for a top-level dotted name such as `click.pause`, and it does not hold for a method ref. The review has 2 high and 3 low findings. Points: 1 holds in part, 2 holds, 3 holds in part, 4 fails, 5 finds no hunk outside the claim, 6 holds. Tests: 4 passed in the new file, and 121 passed in the nine vet and criteria files, 0 failed.

## (a) Verdicts on the points

1. Holds in part. On dry1's index copy, the vet gives these results:
   - `click.pause` gives `src/click/termui.py::pause`.
   - `pause` gives `src/click/termui.py::pause`.
   - `click.termui.pause` gives `src/click/termui.py::pause`.
   - `src/click/termui.py::pause` gives `src/click/termui.py::pause`.
   - `click.nothing_here` stays as written at specify. The repair door refuses it.
   - `click.Context.invoke` stays as written at specify, and the repair door refuses it. The claim gives a grain for this ref (finding 1).
2. Holds. On dry1 the index holds `getchar` twice in program code. `click.getchar`, `click.termui.getchar` and `getchar` all raise the same refusal: "getchar names 2 symbols in the index, and 2 of them are program code. Write one as path::name, the program's first: src/click/_termui_impl.py::getchar, src/click/termui.py::getchar". The refusal names the suffix and not the ref as written. The ref's module part, `termui`, does not narrow the choice (finding 3). For `pause` there is one program row and one attached row, so `_program_rank` picks the program row without a refusal. That pick follows the ruling of frame 324.
3. Holds in part. With the stored grain, `surface_names` at `api.py:10744` is `{'pause', 'src/click/termui.py::pause'}`. The never-calls check at `:10969` passes both a `pause()` call and a `click.pause()` call. The import door at `:10951` runs first and refuses a body that imports only from `click`. That door refuses `from click import pause` and also `import click` with `click.pause()`. Its hint is "`from click.termui import pause`", and the Tester can follow it (finding 4).
4. Fails. A ref that the vet keeps, such as `click.Context.invoke`, `click.nothing_here` or `click.pause()`, reaches `:10969` as one whole string. The probe gave "never calls" for every body form. The Tester gets "this test never calls 'click.Context.invoke' ... call it and assert on what it returns or does". The Tester already calls the callable, so that step cannot help. The text does not name `tests.triage(verdict='cannot')`, which is the route to repair (finding 2).
5. Finds no hunk outside the claim. The diff changes `_vet_surface` and adds the new test file only. A bare ref or a `::` ref skips the loop, `name` stays equal to `ref`, and the old path runs.
6. Holds. `tests/rota/test_frame356_dotted_surface.py`: 4 passed. Nine files together with `-n0`: 121 passed in 49.42s. The files are the new test, `test_frame324_one_reader`, `test_frame324_program_rank`, `test_criteria_surface`, `test_criteria_one_id`, `test_criterion_contest`, `test_frame318_criteria_lift`, `test_frame328_criterion_quote` and `test_f10_item_callables`.

## (b) Findings

1. **The method half of the claim depends on a row shape that the indexer never writes.** `rota/roles/api.py:5617` to `:5625` and `tests/rota/test_frame356_dotted_surface.py:77` to `:84`. High. CONFIRMED. The indexer does not go into a class body (`rota/onboarding/indexer.py:147`, "Do not descend: a method inside a class is the class's business"). The probe found 0 symbol grains of the form `path::Class.name` on dry1 and on nights 170 to 175. The test inserts `src/click/core.py::Context.invoke` by hand, so the test passes on a fixture that no real run makes. On the real index, `click.Context.invoke` stays as written, and the dry1 wall comes back for every method surface. The reason for the deviation in the pass report, "the index writes a method as `path::Class.name`", is false. Fix: write the test on the real index shape. Then resolve a dotted method ref through its class row, for example `click.Context` gives `src/click/core.py::Context`, and let the encode door match the method name.
2. **A dotted ref that the vet keeps meets the never-calls door as a whole string, and no body can pass.** `rota/roles/api.py:5719` keeps the ref. `:10744` and `:10969` refuse it. High. CONFIRMED. The probe ran five body forms against the stored refs `click.pause` and `click.Context.invoke`. The never-calls check refused all ten. The ref types that stay as written are: dotted methods (finding 1), dotted new names such as `click.nothing_here`, and the call form `click.pause()` (finding 5). The vet passes all of them at specify, because `required` is False there. The refusal text asks for a call that the body already makes. Fix: at `:10744`, add the last dotted segment of a ref with no `::` to `surface_names`. This makes the door weaker only for refs that the index does not hold.
3. **The vet ignores the module part of a dotted ref.** `rota/roles/api.py:5621` to `:5639`. Low. CONFIRMED. `click.core.pause` stores `src/click/termui.py::pause`, and `os.path.echo` stores `src/click/utils.py::echo`. The vet does not give a note for either. `click.termui.getchar` is refused as ambiguous, but its module part matches one of the two rows exactly. Fix: before `_program_rank`, keep only the rows whose dotted module (`module_of`) ends with the ref's prefix. If no row is left, keep the ref as written.
4. **The import door refuses the public re-export, and its regex reads only the first part of a dotted `import`.** `rota/roles/api.py:10757` and `:10951`. Low. CONFIRMED by the probe, which runs the same expressions. `import click.termui` with `click.termui.pause()` gives `imported_from = {'click'}`, so the door refuses a correct import. The Tester gets a hint that it can follow, so this does not block the change. The code is older than this commit, and the wall read already notes the re-export part. Fix: capture the dotted name in the regex at `:10757`, and accept a package that re-exports the surface name.
5. **Outside the points: the call form of a ref stays as written.** `rota/roles/api.py:5617`. Low. CONFIRMED. `click.pause()`, the form that s139's prompt used, finds no row and no near match, so the vet keeps it. A bare `pause()` gets a near-match refusal. Fix: remove a trailing `()` from the ref before the lookup.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/393648aa-e5f9-4235-ad76-56489455e14e/scratchpad/f356r1/`. Each ran from the worktree root `C:/Users/roman/rota_f354r` on `dry1.db`. That file is a copy of `dry1w3/dry1.db` and is in the same directory.

- `q1_dups.py`: lists the names that have two or more program rows (5, `getchar` among them) and the rows for `pause`, `invoke` and `echo`.
- `q2_vet.py`: runs `_vet_surface` on 13 refs, once with `required` False and once with it True. It also counts the dotted symbol grains, which are 0.
- `q3_encode.py`: copies the import-door and never-calls expressions of `tests_encode` (`:10732` to `:10757`, `:10945` to `:10950`, `:10969`), with `module_of` taken from the code. It runs 5 bodies against 3 surfaces.
- `q4_more.py`: runs the vet on `click.pause()`, `pause()`, `click.Context` and `Context.invoke`. It also counts the dotted symbol grains on the copies of nights 170 to 175, read-only, and finds 0 on each.
- pytest with `-n0` on the new file (4 passed) and on the nine files (121 passed in 49.42s).

## (d) Usage

- Input tokens: about 50k in context at the end. This is an estimate, because the harness shows no exact count.
- Output tokens: about 10k, also an estimate.
- Total: about 60k.
