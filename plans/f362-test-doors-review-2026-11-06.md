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
