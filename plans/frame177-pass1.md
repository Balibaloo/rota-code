# Frame 177, pass 1: the prints door reads the function's kind

Meta workflow. The implementer of pass 1 writes this record on 2026-10-07.

## What the pass changed

- The prints door of `tests.encode` now reads the definition of the name it guards before it refuses a return check. It reads the tree the test runs against: the batch's worktree, or the project root when the session has no batch. This is the reader of frame 131's door, `_run_tree_reader` (reasoned: the door reuses the variable `read` that the invoke door already holds).
- The door does not refuse when the definition is a `def` that returns a decorator or a command. That is a `def` whose own body returns an inner `def`, or a call to `option`, `argument`, `command`, `group`, `Command` or `Group`. `_returns_factory` decides this. A nested `def` is not read for its own returns.
- When the door still refuses and the definition is a `def` with no decorator, the sentence ends with `: \`<name>\` is a plain function in \`<file>\``. Both refusals of the door carry the clause. In a batch, the clause records a `line_text` fact on the `def` line, as frame 131's door does.
- When the tree holds no definition, or only a re-export, the door says what it said before.
- Frame 131's import resolver moved out of `_plain_invoked` into `_defined_in` and `_last_binding`, and `_imported_names` reads the test's `from` imports. `_plain_invoked` calls them, so the two doors resolve an import the same way. The behaviour of `_plain_invoked` does not change (observed: `tests/rota/test_invoke_door.py`, 2026-10-07, all green with the night tests).
- `_definition_of` finds the definition. The test's import decides first. The criterion's surface ref `path::name` is the second route, for a call such as `click.version_option`. A name that the test binds itself gives None.

## Tests

`tests/rota/test_prints_door_kind.py`, new:

- `test_s274s_turn_2_encode_on_a_decorator_factory_lands`: s274's turn 2 encode on c4, read from `D:/repos/rota/.rota/clickI_night128.db` with `mode=ro`. The worktree holds `src/click/decorators.py` at 191e47a6, and the root at 39fbe93. The encode lands.
- `test_no_encode_of_s274s_turn_2_meets_the_prints_door`: none of the six encodes meets this door. Another door may refuse one of them, and the test allows that.
- `test_a_refusal_on_a_plain_function_names_the_kind`: the exact sentence on a plain `echo_json` that prints.
- `test_the_kind_is_a_fact_that_the_check_reads_in_the_worktree`: the fact passes `sandbox.check_facts`.
- Unit tests of `_returns_factory` and `_definition_of`.

The existing test of a plain function that prints is `test_a_test_that_uses_a_printing_surfaces_return_value_logs_the_assumption` in `tests/rota/test_desk_guards.py`. It stays unchanged and green. Its refusal now carries the kind clause, and its `match` still holds.

## The gate

The gate ran once from the worktree on 2026-10-07: `suite: 23 failed, 3210 passed, 35 skipped, 17 xfailed, 18 warnings`, stale 0. The worktree had no baseline, so the gate stored this run as the baseline. Its new-reds line is therefore empty by construction. The 23 red ids then ran against `rota/roles/api.py` at fb0cee10, and all 23 failed there too (observed: 2026-10-07, `23 failed in 220.06s`). So the pass causes none of them. They are 18 L1 cases, 1 L3 chain, `test_map`, `test_onboarding`, `test_pins` and `test_roles_doc`.

## What the pass did not do

- A night is not run. The frame's ratio, stdout tests on a factory from 3 of 3 to at most 1 in 3, needs the walk.
- The door that refuses a name the worktree lacks runs before the prints door. So no encode reaches the prints door with an imported name that the worktree lacks. The "no definition" case is tested on the helper, not on an encode.
- A decorated `def` that is not a factory, a class and an assignment get no kind clause. The brief names only the plain function.
- s274's bodies read `"Python" in result`, where `result` is a decorator. Such a test fails with a `TypeError` against any code. The door now admits it, as the brief asks. No door checks that a factory's return is used as a decorator. That is a possible next frame (reasoned: from the bodies at turn 2 of s274).
