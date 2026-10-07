# Frame 131, a test calls a plain function as a Click command: pass 1

Meta workflow. Pass 1 on Opus, 2026-10-07, in `C:/Users/roman/rota_f131` on the branch `f131` from 5fa2ed27. No model call was made. The gate did not run, because night 127 holds the GPU.

## What changed

- `rota/roles/api.py`, `_plain_invoked`, before `tests_encode`. The predicate finds each call `<expr>.invoke(NAME, ...)` whose first argument is a bare name. It resolves NAME through the body's `from ... import` lines to a module file and reads that file in the base. It returns the name, the file and the `def` line when the last top-level binding of the name is a `def` with no decorator.
- `rota/roles/api.py`, `_base_reader`, before `tests_encode`. The reader gives a project file's text at the project root's `HEAD`, by `git show`, the same way `_signature_drift` reads "the project's definition". With no `project_root` in the config, it reads nothing, and the door admits.
- `rota/roles/api.py`, the door in `tests_encode`. It runs after the surface door and before the parrot door, the prints door and the literal door. So the placeholder id, the path and the criterion checks run first.
- `tests/rota/test_invoke_door.py`, new, 25 tests.

The refusal, for s139's first body against the test fixture's base:

```
the test inh_echo_json_01 passes `echo_json` to `.invoke`, and `echo_json` is a plain function in `src/click/utils.py` at line 8: `CliRunner.invoke` takes a command
```

The refusal names no call, no fixture and no test body. It records one fact, the `def` line of the base's text, through `_fact` with the kind `line_text`. So frame 144's fact check reads the refusal.

## What the door admits

- A name that the test file binds itself: a local `def`, a class, or an assignment. A name imported and bound again in the test is the test's own.
- A first argument that is an attribute, a call or a string.
- A name whose last top-level binding in the module is a decorated `def`, a class, an assignment such as `echo_json = command()(echo_json)`, or an import. A re-export in a package's `__init__.py` is an import, so the door admits it. The door does not follow it.
- A name that the module does not bind, and a module that the base does not hold, such as an installed library.
- A module under a `tests` folder, a `test_*.py` file or a `conftest.py`.

The import forms that resolve: `from src.click.utils import`, `from click.utils import` against `click/` or `src/click/`, a package's `__init__.py`, and a relative import, which starts at the test file's own folder.

## The counts

- Stored rows (observed: `test_the_stored_rows_of_four_nights`, 2026-10-07). On nights 119, 123, 125 and 126, 90 stored tests hold an `.invoke` call. Against the base at each night's s130 head, the door refuses 6, each one of s139's: night 119 `inh_echo_json_01` and `_02`, night 123 `_01` and `_03`, night 126 `_01` and `_02`. It refuses 0 others. Each refusal names `src/click/utils.py` at line 689. This equals the read's count, 6 of 90, by night 2, 2, 0, 2.
- Tester encode calls (observed: a scratch script over the turns, 2026-10-07). The door refuses 10 calls a night, 40 on the four nights, all from s139, and no call of any other session. This equals the read's count.
- The s139 bodies come from night 126, s139 turn 5 for `_01` and `_02` and turn 4 for `_03`. A script compared the test file's literals with the turns, byte for byte, and all three are equal.
- The base commits per night come from the read's `door.py`, because no table records the commit that a batch started from.

## Mutants

Each mutant was run on the test file, and the file was then restored.

- The door off, `plain = None`: 5 tests go red. These are the three s139 bodies, the no-recipe test and the fact-check test.
- The decorator check removed: 3 tests go red, the decorated command through the op and two predicate cases.
- The local-name check removed: 1 test goes red, the imported name that the test binds again.

## The known miss

Night 119's `tst_v3`, version 2, calls `runner.invoke(dummy_cmd)` on a local `def` that carries only `@version_option`. The door admits it, because a local name is the test's own. That test fails for the same reason as s139's: `version_option` gives no command. The read records this miss in section 5.

## Deviations from the brief

1. The door reads the base at the project root's `HEAD`, and not at a stored base commit of the batch. No table stores the commit that a batch started from. The worktree can hold the Developer's wrap, so the worktree is not the base. After another batch merges, `HEAD` moves past the batch's base.
2. The refusal is a `ValueError`, and not a `Wall`. In `rota/core/db.py`, a `Wall` on an answer wake with no test written marks the question unresolved as "the answer did not change the criterion; encoding it still parrots". s139 met this door on an answer wake, the answer to m63, and its criterion is not at fault. The prints door raises a `ValueError` for the same kind of fact.
3. The refusal names the line as `at line 689`, and not as the line inside the code span of the brief's form.
4. The test file's literals hold empty lines where the bodies hold four spaces. The Write tool removes trailing spaces, so a list comprehension puts the spaces back. A script proved the three bodies equal to the turns.
5. The refusal test runs the hook of frame 144 as `test_scalar_door._refused` does: the follow check and the fact check. Frame 136's dry run, `_admits`, serves `code.write` only, and no other door test sends a refusal through it.
6. The four neighbouring files ran too: `test_desk_guards.py`, `test_offers_followed.py`, `test_triage_fork.py` and `test_fence_nudge.py`, 400 passed and 7 xfailed. `test_fence_nudge.py` replays recorded completions, and it made no model call.

## Open

- The gate and the stale count wait for the GPU, step 7 of the brief.
- A re-export through a package's `__init__.py` is not followed. No stored row on the four nights imports `echo_json` from `click` or `src.click` directly.
- The Developer's answer mode writes code against a test that it knows is wrong. The read names this as a separate wall.
