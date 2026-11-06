# Review of `dc33edfb`, frame 362: the test doors

## The result

Verdict: accept, with two follow-ups before the next dry run. The three doors fix the 30 measured refusals. The replay agrees with the report: 27 of 35 calls pass every door, and the 8 calls that remain refused meet a correct path clash. The 10 neighbouring door test files are green: 544 passed. Two high findings remain. The commitment guard path keeps the old false collect text (finding 3). The fixture door refuses every parametrized test with a false harness claim (finding 8, outside, older than the commit). The other findings are low.

## (a) Verdict on each point

1. Holds with gaps. The door reads the syntax of the `def`, not the value. Five print-only surfaces pass, and four value surfaces are refused (findings 1, 2).
2. Holds. The clickI tests of nights 28, 42 and 45 pass. The prints door refuses 0 of the 18 calls. The 2 that stay refused meet the clash at `src/icalendar/tests/test_folding.py`, the file of `c_1_fold`. That clash is correct.
3. Holds with gaps. Four good shapes are refused, and four bodies that check nothing or are not collected are admitted (findings 4, 5, 6). The 1 of 12 is dry3 s183 t1. It meets the correct clash at `tests/test_caselessdict.py`, the file of `tst_c2_no_dup_keys`.
4. Partly holds. Both new texts are true for the bodies they refuse. A second copy, `_encode_guard`, keeps the old false text and the old rule (finding 3). The prompt `tester/tests_missing.md` line 51 is true as it stands.
5. Holds. The folder comes from the `code_index` path rows that `_test_dirs` keeps as attached test files. The hint is correct on all nine layouts in the probe. The result of `_refuse_program_path` does not change, because it builds `dirs` from the same `indexed` set and conn.
6. Holds. pytest collects all 11 bodies, and each body holds a check call. B1 and B2 check only that `confirm` does not raise, and they use `pytest` with no import. B6 and B9 assert `IsNotNone` on a bool. Those checks are weak, but the judgement belongs to the desks.
7. The fault is real, and the reason in the report for not fixing it is false (finding 7). The criterion "The serialized output of to_ical folds lines" and an item "to_ical returns the calendar" give an offer of `contradicts_request`.

## (b) Findings

1. `rota/roles/api.py` 10634-10661, `_gives_a_value`. Low. CONFIRMED (probe_prints P2, P4, P4b, P4c, P5). These surfaces are admitted, but each one prints and gives no usable value: `return print(...)`, `out = print(...); return out`, `return sys.stdout.write(...)`, a value in one branch with a print on the default path, and a generator that prints and has a bare `yield`. The night 28 loop opens again for these shapes. Fix: count a value only when no path falls through, and no return value is a print or write call or a name bound from one.
2. `rota/roles/api.py` 10676-10709 and 12427. Low. CONFIRMED (P6c, P9, P11b, P12). These surfaces return a value and stay refused: a base method with a `pass` body that a subclass overrides, a function under `functools.lru_cache`, a call `script.echo_json(...)` through `import script`, and a re-export with a bare ref. Each refusal is the old word rule, so the head behaves the same. `as_method` is True for every `Attribute` call, so a module call goes to the route that reads every definer. Fix: send a call on an imported module through `_defined_in`, and read a `pass` base def as a stub when another def overrides it.
3. `rota/roles/api.py` 11300-11304, `_encode_guard`. High. CONFIRMED (test_probe_guard.py). A `pytest.raises` guard test, a `unittest.TestCase` guard test and a test with no check all get "pytest will collect nothing from this body: it needs a def test_...(): with an assert". `tests_encode` line 11338 sends every `criterion_id` that names a stated commitment to `_encode_guard`. This is the same false text that the commit removed at line 11447. Fix: give `_encode_guard` the two refusals and `_holds_a_check` of lines 11450-11460.
4. `rota/roles/api.py` 11161-11181, `_holds_a_check`. Low. CONFIRMED (probe_collect C4b, C11, C11b, C13). These good tests get "checks nothing": `from pytest import raises`, `import pytest as pt` with `pt.raises`, `from numpy.testing import assert_allclose`, and `raise AssertionError(...)`. The text then says "no pytest.raises", which is false for C11. Fix: resolve each call name through the imports of the body, and count an `assert_*` name and a raise of `AssertionError`.
5. `rota/roles/api.py` 11174 and 11914. Low. CONFIRMED (C12, C12b). `self.assertTrue(True)` in a `TestCase` is admitted. `assert True` is refused by the F14 door, because that door reads `ast.Assert` nodes only. The old collect door refused C12. So the commit opens a check that cannot fail. Fix: give the first argument of each `self.assert...` call to `assert_cannot_fail`, as the door does for an `assert`.
6. `rota/roles/api.py` 11445-11446, `has_test`. Low. CONFIRMED (C7, C9, C10b, and a real pytest run in rd362/collect_truth). Three bodies are admitted, and pytest runs none of them as a test. These bodies are a class `AddChecks` with no `Test` prefix, a `@pytest.fixture` named `test_total`, and an `async def` test, which fails under plain pytest. The text "pytest collects this body" is false for these bodies. The gap is older than the commit. Fix: count module-level `test` functions, and methods of `Test` classes with no `__init__` or of `TestCase` subclasses, and refuse an `async def` test.
7. `rota/roles/api.py` 9167-9203, `_contradiction_offer`. Low. CONFIRMED (probe_triage T1, T5). The triage door refuses `encodable` for "The serialized output of to_ical folds lines at 75 octets" when the item says "returns". The door also refuses "The serialized output keeps every escape sequence" against "the folded result". Report section 2 says that the triage door has no surface to read. That is false: `criteria.surface_refs` holds the surface, and `_surface_gives_a_value` takes a name. The offer fired 0 times on dry runs 3 to 6c. Fix: skip the offer when a surface ref of the criterion gives a value through `_surface_gives_a_value` with `as_method=True`.
8. Outside. `rota/roles/api.py` 11885-11913, the fixture door. High. CONFIRMED (C8). A test under `pytest.mark.parametrize` with the argnames a, b and s is refused. The refusal says that `test_add` takes `a`, that the harness has no such fixture, and that every run errors at setup. That harness claim is false, and parametrize is a common shape of a good test. The code is older than the commit. Fix: add the argnames of each `parametrize` mark on the function to `own`.
9. Outside. `rota/roles/api.py` 10693-10694. Low. PLAUSIBLE. The method route calls `definers_of` with no `staged` value. A new file that the Developer writes is not in the index until a commit, so the route does not see a printing def in that file. Also, the door reads the tree before the diff, and the criterion can ask to change the surface. The base-red gate probably catches the second case. Fix: also scan the unindexed `.py` files of the worktree in the method route.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/029756dd-9273-4a54-95d8-2da05a2bfe52/scratchpad/rd362/`. Each probe ran from the worktree root `C:/Users/roman/rota_p362t` and called no model.

- `common.py`: loads `_db`, `_tester` and `_encode` from `tests/rota/test_f362_test_doors.py`.
- `probe_prints.py`: sends 23 surfaces in a sample tree through `tests.encode` (point 1).
- `probe_collect.py`: sends 20 test bodies through `tests.encode` (point 3). `collect_truth/` holds three bodies, and real pytest ran them.
- `test_probe_guard.py`: sends three guard bodies through the `proj` fixture of `test_f362_consumers.py` (point 4).
- `probe_hint.py`: sends a clash on nine layouts (point 5).
- `probe_register.py` and `probe_register_show.py`: read `D:/repos/rota/tests/rota/cassettes.db` with `immutable=1`, and list the 11 admitted bodies (point 6).
- `probe_triage.py`: sends five criterion and request pairs through `tests.triage` (point 7).
- Suite: 10 door test files with `-p no:cacheprovider`. Result: 544 passed in 80 s.
- Read without a run: `tests_read/replay_head.json` and `replay_commit.json` of the implementer (point 2).

## (d) Usage

The harness shows no counter. The estimate is about 100k input tokens of context, about 16k output tokens, and about 116k in total.

## Second look, bd10fb23

### The result

Verdict: accept, with two high follow-ups. The diff mends findings 1 to 8 for every shape that the first probes sent. The criterion path refuses all four bodies that must stay refused. Two high findings remain. On the guard path, `assert True` passes (S1). The fixture door still refuses a fixture from the project conftest (S2). The 11 door test files pass: 573 passed in 79 s. `tests/rota/test_triage_fork.py` passes: 53 passed.

### (a) Verdict on each point

1. Findings 1 to 8, with the same probes at `bd10fb23`:
   - Finding 1: fixed. P1 to P5 are refused, and P5b is admitted.
   - Finding 2: fixed. P6c, P9, P11b and P12 are admitted. P7, a property that the test calls, is now admitted too, and that is a doubt.
   - Finding 3: fixed for the two texts. A `pytest.raises` guard test and a `TestCase` guard test land, and an empty guard test is refused. The guard path admits `assert True` (S1).
   - Finding 4: fixed. C11, C11b and C13 land. C4b now meets the import door, not the collect door.
   - Finding 5: fixed for `assertTrue(True)`. `self.assertEqual(1, 1)` lands (S4).
   - Finding 6: fixed for C7 and C10b. C9, the `async def` test, lands by deviation.
   - Finding 7: fixed for T1 and T5. T3 stays refused by deviation 1.
   - Finding 8: fixed for C8. A class-level `parametrize` (R7) and a conftest fixture (R6) are still refused (S2).
2. The rule. On the criterion path, these four bodies are refused: `def test_x(): pass` (R1), an English sentence (R2), a body with no test function (R3), and `assert True` (R4). On the guard path, `assert True` lands (S1). The diff refuses three tests that it is not certain of: a nested `Test` class (S3, new), a conftest fixture and a class-level `parametrize` (S2, older code in a door the diff edits).
3. The three deviations:
   - Triage in one direction: the deviation does not follow the rule. The criterion "q_split returns the folded line" against the ticket "When icalendar writes a long line" keeps the offer (T3). That ticket is the wording of the dry runs. The refusal is not certain, but it fired 0 times. It opens no certain wrong admit.
   - The fixture door admits any test with a decorator that is not a mark: this follows the rule. A wrong admit is possible only when the decorator gives no argument, and the door cannot know that.
   - A class with any base counts as collected: this follows the rule. The wrong admit is certain only for a stdlib base such as `dict`. R10 shows that such a body is still refused when it checks nothing.
4. The old cases hold. The clickI tests of nights 28, 42 and 45 in `test_desk_guards.py` pass, and so does `test_f362_test_doors.py`. The prints probes P1, P6, P11c, P11d, P12b and P13 are refused as before. `test_triage_fork.py` and the offer test of the p2 file pass.
5. New defects: S3 and S5. The test files pass.

The import door, api.py 12290-12379, reads these names: the stdlib names, `pytest`, the `.py` files and folders at the worktree root, the program modules of the index, and the project name in `pyproject.toml`. It reads no installed package and no declared dependency, so it cannot know whether `numpy` or `hypothesis` is installed, and its refusal of them is not certain.

### (b) Findings

- S1. `rota/roles/api.py` 11514-11521, `_encode_guard`. High. CONFIRMED (test_probe_guard2.py: assert_true lands). The guard path runs the collect door and no constant door. So a guard test that cannot fail lands, and its commitment shows as guarded. The guard path had this gap before pass 2. Fix: move the F14 constant check of `tests_encode` into a function, and call it on both paths.
- S2. `rota/roles/api.py` 12090-12131, the fixture door. High. CONFIRMED (probe_p2 R6, R7). A test that takes a fixture from the project `tests/conftest.py` is refused, and the refusal says that the harness has no such fixture. A method under a class-level `parametrize` is refused in the same way. `_conftest_fixtures` (line 23463) exists, and the unbound-name door at line 11745 uses it already. Fix: add `_conftest_fixtures(_worktree_of(ctx))` and the argnames of class-level marks to the given names.
- S3. `rota/roles/api.py` 11333-11367, `_collected_tests`. Low. CONFIRMED (R9, and a real pytest run in rd362/collect_truth2 that passed 1 test). The door says "pytest collects nothing" for a test in a nested `Test` class, and pytest collects that test. Pass 1 admitted this body. Fix: read nested classes with the same class rule.
- S4. `rota/roles/api.py` 12140-12150. Low. CONFIRMED (R5). `self.assertEqual(1, 1)` lands, because only the four one-argument truth asserts go to `assert_cannot_fail`. Fix: refuse a two-argument `self.assert...` call when both arguments are constants.
- S5. `rota/roles/api.py` 11294 and 11325, `_CHECK_WORDS`. Low. CONFIRMED (R8). The door reads a word inside the name as a check, so a bare call of the surface `fail_safe` counts as a check. Fix: count a name only when it starts with `assert` or equals `fail`, `raises` or `warns`.

### (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/029756dd-9273-4a54-95d8-2da05a2bfe52/scratchpad/rd362/`. Each probe ran at `bd10fb23` and called no model.

- `probe_prints.py`, `probe_collect.py` and `probe_triage.py` ran again with no change.
- `test_probe_guard2.py`: seven guard bodies through the `proj` fixture. The first `test_probe_guard.py` stops at the first body that lands, because it slices a dict.
- `probe_p2.py`: R1 to R10, the four bodies that must stay refused and the new edge cases.
- `collect_truth2/`: a real pytest run of the nested class.
- Suite: the 10 files of the first look and `tests/rota/test_f362_test_doors_p2.py`. Result: 573 passed. The implementer counted 665 tests in a different set of 10 files.

### (d) Usage

The harness shows no counter. This look used about 30k input tokens of context and about 8k output tokens. The total for both looks is about 155k.

## Third look, a2c4552b

### The result

Verdict: accept, with one high follow-up at `ensure_env` (U4). S1 to S5 and the triage skip are fixed, and my probes give the expected result at `a2c4552b`. The fixture door and the import door now read the right sources. Each door still has a small gap in both directions (U1 to U3). The 16 door test files pass: 716 passed in 80 s. My count differs from the 837 of the implementer, because the sets of 11 files from the second look differ. The cost is small (point 4).

### (a) Verdict on each point

1. All fixed:
   - S1: fixed. A guard test with `assert True` is refused, and a `pytest.raises` guard test and a `TestCase` guard test land.
   - S2: fixed. A conftest fixture (R6) and a class-level `parametrize` (R7) land.
   - S3: fixed. The nested `Test` class (R9) lands.
   - S4: fixed. `self.assertEqual(1, 1)` (R5) is refused.
   - S5: fixed. A bare call of `fail_safe` (R8) is refused as a test that checks nothing.
   - The triage skip: fixed in both directions. T1 to T5 are accepted. `test_triage_fork.py` holds night 91, and it passes, because that criterion has no surface ref.
2. The fixture door, in both directions:
   - Good tests that are still refused: a fixture that the test module imports (F2), and a fixture that the body renames with `name=` (F3). See U1.
   - Names admitted that no source gives as a fixture: `pytest` and `Calendar` (F6, F7). The door admits them because a conftest imports them. See U2.
   - `mocker` and `criterion_id` are still refused, and both refusals are right. No conftest gives either name, and rota's interpreter has no `pytest-mock`. That interpreter runs the tests when the worktree has no `.venv`. A worktree whose `.venv` holds `pytest-mock` admits `mocker`, and that is also right.
3. The import door, in both directions:
   - `billing`, `utils`, `app` and `numpy` are refused (I1, I2, I3, I10).
   - `dateutil`, `hypothesis`, `pytz` and `yaml` land (I6 to I9). `yaml` lands because rota's interpreter holds it.
   - The invented modules `date` and `cal` land, because each is a part of a declared name: `python-dateutil` and `sphinx-icalendar` (I4, I5). See U3.
   - `ensure_env` (`rota/core/provision.py` 85-132) installs `pytest`, `[project].dependencies` and the project itself, editable, with `--no-deps`. A project can declare its test packages in these places: `[project.optional-dependencies]` extras such as `test` or `dev`, the PEP 735 `[dependency-groups]` (icalendar uses the group `test`), poetry groups, `tests_require` and the extras in `setup.cfg` or `setup.py`, requirements files, and the `deps` of `tox.ini`. The fix belongs at `ensure_env` (U4).
4. The cost, measured in one process on the icalendar layout with the `pyproject.toml` of icalendar at `99619246`:
   - The fixture door: the first call that reads the plugin sources takes 0.36 s. Later calls take 0.011 s, against 0.005 s at `bd10fb23`. The plugin read is cached by the mtime of the folder.
   - The import door: 0.02 s to admit and 0.06 s to refuse, against 0.05 s at `bd10fb23`.
   - So the cost is about 0.4 s for each process, and it needs no fix.
5. New defects: U1 to U3 and U5. The test files pass.

### (b) Findings

- U1. `rota/roles/api.py` 12187-12193 (`own`) and 12199-12271, the fixture door. Low. CONFIRMED (probe_p3 F2, F3). Two good tests get "the file give[s] no fixture of that name". The first takes a fixture that the test module imports from `icalendar.tests.helpers`. The second takes a fixture that the body defines with `@pytest.fixture(name=...)`. pytest registers both. Fix: build `own` from `_fixture_defs(tree)` and the names that the body imports, as the conftest read does.
- U2. `rota/roles/api.py` 23648-23660, `_path_conftest_fixtures`. Low. CONFIRMED (F6, F7). The conftest of icalendar holds `import pytest`, so a test that takes the fixture `pytest` lands. A plain `import x` binds a module, and a module is never a fixture, so that admit is certainly wrong. Fix: give no fixture name for a plain `import` statement, and keep the names of `from ... import`.
- U3. `rota/roles/api.py` 12430-12432, the declared-name match. Low. CONFIRMED (I4, I5). `m.lower() in d` is a substring match, so `import date` and `import cal` land on icalendar. No source gives either module. Fix: read the import names from `top_level.txt` or `RECORD` of installed distributions. For a declared name that is not installed, match a whole `_` segment, or the name with a `py` prefix removed.
- U4. `rota/core/provision.py` 43-54 and 85-132, `declared_dependencies` and `ensure_env`. High. CONFIRMED by a code read and probe I6. The door now admits `import hypothesis` on icalendar. `ensure_env` installs only `[project].dependencies`, so the test errors at collection. The implementer saw that error in a run. Fix at `ensure_env`: install the `test` dependency group (`pip install --group test`, pip 25.1 or later) and the `test`, `tests` and `testing` extras. Until that fix, the door admits a declared name that is not installed only when no environment exists yet.
- U5. `rota/roles/api.py` 23663-23720, `_harness_site_dirs`. Low. PLAUSIBLE, from fault 6 of the implementer. A case tree has no `.venv`, so the door reads the site folder of rota. A package added to rota's venv then changes recorded door results with no change of code. Fix: in a case run, read the site folders from a fixed list that the case records.

### (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/029756dd-9273-4a54-95d8-2da05a2bfe52/scratchpad/rd362/`. Each probe called no model.

- `probe_p2.py`, `probe_triage.py` and `test_probe_guard2.py` ran again at `a2c4552b`.
- `probe_p3.py`: F1 to F8 and I1 to I10, each call timed, on the icalendar layout with its real `pyproject.toml`. `CODE_ROOT` selects the code.
- `old_bd10/`: `git archive bd10fb23` of `rota/` and the test helper. `probe_p3.py` ran on it for the timing before the change. No git command changed the worktree.
- Suite: 16 door files with `-p no:cacheprovider`. Result: 716 passed in 80 s.

### (d) Usage

The harness shows no counter. This look used about 30k input tokens of context and about 9k output tokens. The total for the three looks is about 195k.
