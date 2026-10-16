# Frame 222, review 1 of 531582af: the NameError door's four hint shapes

Reviewer: a read-only agent on Opus, worktree `C:/Users/roman/rota_r222` at 531582af, 2026-10-16. Meta workflow, about the rota workflow's Tester seat.

Verdict: accept with two findings for a pass 1d or frame 260. The four shapes, the order and the count hold as claimed. Two highs sit next to the frame: shape 3a sends 24 of its 25 night bodies to the plain-function door, and frame 260's cause is wrong. The register case fails because the NameError door and the surface door disagree on the `src.` prefix. The surface door does not read only the first import.

## (a) Verdict on each point

1. Holds. The order is 1, 2, 4, 3a, 3b. Each predicate behaves as claimed in a probe. Finding 3 is a low edge.
2. Holds. The replay from the worktree gives 32 of 69: shape 1 11, shape 2 4, shape 4 17, 3a 25, 3b 12. Shapes 1, 2 and 4 bind in the spot reads. Shapes 3a and 3b name no line that binds the name, as designed.
3. Partly right, as pass 1b said. A Tester that follows 3a passes the surface door's checks and meets the plain-function door. Finding 1.
4. Holds, with one correction. All seven shape tests are red at b42aee07 and green at 531582af. The 3b test is red at b42aee07 too. It is green only on pass 1's uncommitted text.
5. Holds. Both moved tests keep their meaning. The first test still asserts shape 3a on a `ledger` body with no `from` line.
6. Yes, the two names can be confused. Finding 4, low.
7. The surface door is untouched, and the case fails there and not at the NameError door. The cause that frame 260 names is wrong. Finding 2.

## (b) Findings

1. **Shape 3a tells 24 of 25 night bodies to pass the surface to `.invoke`, and the plain-function door refuses that.** `rota/roles/api.py:13319-13325`, `_unbound_name_hint` shape 3a. Severity high by the brief's rule: the hint names the surface line, which does not bind the name, on a shape the nights hold 25 times. The text is not worse than the old text, which named the same line. CONFIRMED.
   - Count over the 25 3a refusals in `refusals.json`: 24 pass the stand-in to `runner.invoke(...)`. 19 already import the surface, so "add `from click.decorators import version_option`" asks for a line that the body already holds. Night 46 saw this same pattern.
   - Probe `test_p3_follow_3a_on_cli_app`: s485's body with `cli_app_with_version_option` replaced by `version_option`, as the hint says. The NameError door and the surface door's never-calls check at `api.py:7847` admit it. Then `_plain_invoked` at `api.py:7863` refuses it: "passes `version_option` to `.invoke`, and `version_option` is a plain function ... `CliRunner.invoke` takes a command".
   - A right body defines a small command that the surface decorates or calls, as s549's seq 4 did. That is a definition the test owes, which is 3b's instruction plus the surface import.
   - Fix: in 3a, when a runner's `.invoke` takes the stand-in, say that the test owes a click command that uses the surface, and omit an import line that the body already holds.

2. **Frame 260's cause is wrong. The register case fails on the `src.` prefix, not on the first import.** `rota/roles/api.py:7618-7619` and `7823-7829`, the surface door, against `api.py:7385-7386` and `7402-7403`, the NameError door. Severity high: the NameError door's own line is refused by the next door, so the follow check fails. CONFIRMED.
   - `imported_from` collects every `from X import` and `import X` line, indented ones included. `imports_ok` is true when any of them matches. The text "this test imports from random" comes from `sorted(imported_from)[0]`, and `random` sorts before `src.billing.accounts`.
   - The NameError door builds its line with `keep_root=not _installed`, so an uninstalled tree gets `from src.billing.accounts import close_account`. The surface door's `_dotted` uses the default `keep_root=False` and wants `billing.accounts`.
   - Probe `test_p7` on `_click_tree` with the `close_account` surface, an uninstalled tree. An unbound `close_account` gets "add `from src.billing.accounts import close_account`". That line, with no `random`, inside the function or at the top, is refused by the surface door, which asks for `from billing.accounts import close_account`. The body with `import random` first and `from billing.accounts import close_account` inside the function is admitted.
   - The pass 1 traceback holds the same two lines: the offer body imports `src.billing.accounts`, and the second refusal asks for `billing.accounts`.
   - The contradiction is older than this commit for shape 1. This commit extends it to the lines of 3a and 4.
   - Fix: re-scope frame 260 to one `keep_root` rule for both doors, for example accept the module with and without `src.` on an uninstalled tree. Drop the first-import ends-when.

3. **A surface symbol that is also a fixture name gets shape 2, never shape 1.** `rota/roles/api.py:7342-7349`. Severity low. PLAUSIBLE, from a read. The fixture branch runs before the surface is read and passes an empty surface, so shape 1 cannot fire. `_unbound_name_hint` itself keeps shape 1 for the case (probe `test_p1a`). No night body holds such a surface. clickI's conftest defines `runner`, so a surface named `runner` would meet it.
   - Fix: run the fixture branch after `named` is read, and pass the surface to `_unbound_name_hint`.

4. **`_package_definer` and `_package_definers` differ by one letter.** `rota/roles/api.py:13191` and `15784`. Severity low. CONFIRMED by a read.
   - `_package_definer(root, name, keep_root)` walks every package directory of the worktree. It returns the `(dotted module, path)` with the shortest dotted path that defines the name, for the NameError door's shape 4.
   - `_package_definers(root, init_rel, path, name)` reads the sibling modules of one package directory. It returns the sorted stems that define the name, for a write door (frame 229).
   - Fix: rename the new one to `_project_module_of`, as pass 1c proposed.

Notes on the points, not findings:

- Point 1. The probes show the following:
  - shape 1 wins over 4 and 3 for the symbol and for the module leaf;
  - `@pytest.fixture(name='cli_runner')` gives `cli_runner`, and a bare `@fixture` gives the function's name;
  - conftests under `.venv` and `build` are skipped;
  - `_package_definer` finds `src/pkg/mod.py` and the root's `rootmod.py`;
  - it skips `examples/` with an `__init__.py`, `pkg2/tests/`, a directory with no `__init__.py`, `.hidden/` and `build/`;
  - a `testing.py` that imports a missing module gives 3b, and a `testing.py` that loads gives shape 4.
- Point 2. Spot reads, with each new hint:
  - shape 1, night 144 s549 seq 4, `version_option`: `from click.decorators import version_option` binds the name.
  - shape 2, night 143 s320 seq 4, `monkeypatch`: a test argument binds the name. The body also uses `pytest` unbound, which the stdlib branch takes next.
  - shape 4, night 145 s289 seq 1, `version_option` under the surface `custom_version_option`: `from click.decorators import version_option` binds the name.
  - shape 3a, night 143 s464 seq 1, `cli`: the line binds `version_option`, not `cli`. `runner` is also unbound and gets shape 2 next.
  - shape 3a, night 144 s549 seq 1, `cli`: the same line and the same miss. The same session's seq 4 then defined `cli` under `@version_option`, which is the right body.
  - shape 3b, night 145 s378 seq 5, `patch`: no line, and the hint does not name `unittest.mock`.
  - The replay scores shapes 1, 2 and 4 as binding by their shape, and does not run the load check. The spot reads confirm the lines for clickI.
- Point 4. Results at b42aee07, then at 531582af:
  - `test_the_name_error_hint_names_the_surface_import_for_the_surface_and_its_module`: red, then green.
  - `test_the_name_error_hint_takes_a_pytest_fixture_as_a_test_argument`: red, then green.
  - `test_the_name_error_hint_calls_the_surface_in_place_of_a_stand_in`, the `version_option` and `cli` case: red, then green.
  - `test_the_name_error_hint_calls_the_surface_in_place_of_a_stand_in`, the `close_account` and `ledger` case: red, then green.
  - `test_the_name_error_hint_says_the_test_owes_a_helper_beside_the_surface`, shape 3b: red, then green. It is green only against pass 1's text, which was never committed.
  - `test_the_name_error_hint_imports_a_name_the_project_defines`: red, then green.
  - `test_an_unbound_name_is_told_the_import_the_surface_names`, moved: red, then green.
  - `test_an_installed_project_is_told_the_import_without_src`, moved: green, then green. Its asserted line is shape 1, which the old text already gave.
- Point 5. The first moved test asserts shape 1 on a `close_account` body, with "The criterion's surface is" and the `src.` line. It then asserts shape 3a on the body `assert ledger.close('a1') == 'kept'`, which has no `from` line, and asserts no "owes a definition". The second test still asserts the line without `src.` on an installed tree, now through shape 1. It no longer covers 3a on an installed tree, and the parametrised 3a test covers only an uninstalled tree.
- Point 7. The api.py hunks of the diff start at old lines 7332, 7370 and 13103. The surface door at `api.py:7817-7853` and `imported_from` at 7618-7619 are outside them. The pass 1 traceback names the second refusal at `api.py:7822`, the surface door, after the stdlib offer at 7361. The NameError door does not refuse there.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/738ddbaf-1cc4-48f9-9414-01f5058ba1fb/scratchpad/f222/r1/`.

- `replay_wt.py` is `replay.py` with `sys.path` pointed at the worktree. It ran on `refusals.json`, and `replay_out.txt` holds the output. Result: 11, 4, 17, 25 and 12, plus 40 stdlib refusals and 3 with no surface.
- `spot.py` takes one refusal per shape and two under 3a. It prints the new hint and checks with `ast` whether the line binds the name.
- Two inline Python runs counted the 25 3a bodies: 19 import the surface already, and 24 invoke the stand-in.
- `old/` is `git archive b42aee07` with the 531582af `tests/rota/test_desk_guards.py`. The eight shape and moved tests ran with `-k` there and in the worktree, for point 4.
- `new/` is `git archive 531582af` with two scratch test files.
  - `new/tests/rota/test_r1_probe.py` holds `test_p1a` to `test_p1e` for point 1 and `test_p3_follow_3a_on_cli_app` for point 3. 6 passed.
  - `new/tests/rota/test_r1_probe7.py` holds `test_p7` for point 7 and finding 2.
- No tracked file was edited. The full gate was not run.

## (d) Usage

The agent cannot see the harness count. The estimate is about 80k input tokens and 15k output tokens, about 95k in total, over the 50k cap. Read the real number from the harness line.
