# Frame 177, pass 2: the prints door names the test shape on a decorator factory

Meta workflow. The implementer of pass 2 writes this record on 2026-10-07.

## Why the pass exists

The review of 09e60cf6 found that pass 1 admitted all 6 of s274's turn 2 encodes. 5 of them assert `in` on the decorator that `version_option` returns, and fail with `TypeError: argument of type 'function' is not a container or iterable`. The stdout shape of night 128, a bare call with `sys.stdout` captured, met no door (observed: the review, as the coordinator's message quotes it, 2026-10-07).

## What the pass changed in `rota/roles/api.py`

- A new door in `tests.encode` runs before the prints door. For each surface name that the test calls, it reads the definition with `_definition_of`. When `_returns_factory` says the definition is a factory, `_factory_misuse` reads how the test uses it.
- `_factory_misuse` returns `"return"` when the test asserts on what a call returns: a comparison other than `is` or `is not`, a bare `assert`, `assert not`, `str()` or `len()`. A name counts as the return only when every binding of it is a call to the factory. It returns `"stdout"` when the test calls the factory as a bare statement and reads stdout through `getvalue`, `readouterr` or `redirect_stdout`.
- A test that decorates with the factory, passes its result to a call, or checks it with `is not None` meets no shape.
- The refusal is a ValueError with the coordinator's sentence: `` `<name>` is a decorator factory in `<file>`: it returns a decorator and prints nothing when it is called. The message prints when a command decorated with `<name>(...)` runs. Decorate a command with it and invoke the command with CliRunner, then assert on `result.output` ``. In a batch it records the `line_text` fact of the `def` line, through the same `_def_fact` as the kind clause.
- `_returns_factory` takes the module source. Its attribute form counts only on `click` or on a name that the module imports from click. So `return m.group(1)` is not a factory.

## Tests in `tests/rota/test_prints_door_kind.py`

- The `night128` fixture now copies the whole of `src/click` at 39fbe93 for the root and at 191e47a6 for the worktree.
- s274's 6 turn 2 encodes: 01, 03, 04, 05 and 06 meet the factory door with the exact sentence. 02 lands, because it asserts `True` and reads nothing that the call returns.
- The stored tests of night 128: 01, 03, 04, 05 and 06 read the stdout of a bare call and are refused. 02 swaps stdout and never reads it, so it meets no shape of this door.
- The lifts: s247 on night 119 at turns 4 and 8, and s267 on night 127 at turns 2 and 10, all land on night 128's worktree. Some of them first meet the invented-literal door on `hello`, `dummy` or `name`. The test logs the offered ledger line and sends the encode again, as a seat does.
- A test that decorates a command with `version_option`, invokes it with CliRunner and asserts on `result.output` lands.
- The factory refusal has no offer, nothing to follow, and one fact that passes `check_facts`.
- The shapes of `_factory_misuse`, 14 cases.
- The four lows: the full offer refusal with the kind clause; a refusal with no batch records no fact; a decorated `def` gets no kind clause; the attribute form of `_returns_factory`, with `m.group(1)` and `self.command()` as not a factory.

## What the pass did not do

- The factory door does not read the criterion's words. A factory prints nothing when it is called, so the two shapes fail whatever the criterion says (reasoned: the TypeError and the empty stdout of the review).
- The sentence names a recipe: "Decorate a command with it and invoke the command with CliRunner". The prints door's ruling says "the fact and no recipe" (Roman, 2026-09-15, 6b52a09d). The coordinator's message gives this sentence, so the pass uses it. The coordinator's message carries no ruling from Roman, so this is open for the review.
- s274's 02 and the stored 02 still land. They assert nothing that a factory can fail. That is a vacuous test, not this frame's shape.

## The gate

The gate ran once from the worktree on 2026-10-07: `suite: 23 failed, 3240 passed, 35 skipped, 17 xfailed, 18 warnings`, against the baseline `23 failed, 3210 passed`. New reds 0, reds gone 0, stale 0. The 23 reds are those of pass 1, which fail the same way at fb0cee10 (observed: pass 1's record).
