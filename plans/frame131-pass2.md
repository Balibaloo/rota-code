# Frame 131, a test calls a plain function as a Click command: pass 2

Meta workflow. Pass 2 on Opus, 2026-10-07, in `C:/Users/roman/rota_f131` on the branch `f131` from af9db8a0. It repairs the seven findings of frame 131's review of af9db8a0. No model call was made. The gate did not run, because night 127 holds the GPU.

## What changed

- `rota/roles/api.py`, `_run_tree_reader`, which replaces `_base_reader`. The door now reads the files that the test runs against: the batch's worktree through `_worktree_of(ctx)`, as the surface door does. It reads the working file on disk, so the Developer's uncommitted write counts. The surface door and the module door also read the working file, never a commit. With no batch, `_worktree_of` gives the project root, and the door reads the root. The reader also says whether it reads the batch's worktree.
- `rota/roles/api.py`, `_plain_invoked`. The door reads a call only when the receiver is a runner: `CliRunner()` inline, a name bound to `CliRunner(...)` or `<module>.CliRunner(...)` in the body, or a name `runner`. A name `runner` covers a parameter and a variable. So `ctx.invoke(echo_json, [])` is admitted, because Click's `Context.invoke` takes a plain callback.
- `rota/roles/api.py`, the door in `tests_encode`. The fact is now `line_text` with the worktree-relative `path` and the line, and no `text`. So `check_facts` reads the line in the worktree, the file the seat sees, through `_worktree_lines`. The door records the fact only when it read the batch's worktree, because `_worktree_lines` reads the batch's worktree and nothing else. The refusal no longer names the line.
- `tests/rota/test_invoke_door.py`. The fixture's root has no `echo_json`. Batch b1 has a worktree, a copy of the root whose `utils.py` adds a plain `echo_json`. 37 tests.

The refusal, for s139's first body in the fixture:

```
the test inh_echo_json_01 passes `echo_json` to `.invoke`, and `echo_json` is a plain function in `src/click/utils.py`: `CliRunner.invoke` takes a command
```

## The new tests

- The root lacks the name, and the worktree holds a plain `def`: refused. The root alone would admit, so the door read the worktree.
- The root lacks the name, and the worktree holds it decorated: admitted.
- The worktree's last commit holds the plain `def`, and the working file lacks it: this door admits. So the door reads the working file.
- A session with no batch reads the root: admitted while the root lacks the name, refused when the root holds a plain `def`.
- `ctx.invoke`, `click_ctx.invoke` and `self.runner.invoke` are admitted. `runner`, a bound `CliRunner()`, a bound `testing.CliRunner(...)` and an inline `CliRunner()` are read.
- The fact check passes on the worktree, and fails after one line is added above the `def`.
- The stored rows and the Tester encodes of the eight nights, below.

## The counts on eight nights

Each night's base is the commit of its first test run, the Developer's first commit in the batch, which adds `echo_json` at line 689 of `src/click/utils.py`. The tests read that commit with `git show` from `D:/repos/_AI/sample_repos/clickI`. A test cannot read a night's worktree as it stood, because the worktree has moved since.

- Stored rows (observed: `test_the_stored_rows_of_eight_nights`, 2026-10-07). Nights 119 to 126 hold 186 stored tests with an `.invoke` call. The door refuses 10, all of them s139's `inh_echo_json_*`: night 119 `_01` and `_02`, night 121 `_01`, night 123 `_01` and `_03`, night 124 `_01`, `_02` and `_03`, night 126 `_01` and `_02`.
- Tester encode calls (observed: `test_the_tester_encodes_of_eight_nights`, 2026-10-07). The door refuses 78 calls. 70 are s139's, 10 a night on each night except 120. On night 120, s139 is the Liaison, so no Tester event happens there. 8 are on night 121: s229 `runner.invoke(confirm, ...)` 1, s302 3 and s312 4 with `runner.invoke(version_option, [])`. `confirm` and `version_option` are plain functions at the base, so these 8 refusals are right.
- The receiver rule changes none of these counts. The reviewer's replay with the pass 2 predicate gives the same 78 and 10 of 186.

## Mutants

Each mutant ran on `tests/rota/test_invoke_door.py`, and the file was then restored.

| Mutant | Red of 37 |
|---|---|
| The door off, `plain = None` | 7 |
| The decorator check removed | 4 |
| The local-name check removed | 1 |
| The receiver check removed | 3 |
| The reader reads the project root, as pass 1 did | 6 |

## The order of the doors

The door runs after the surface door and before the parrot door, a `Wall` at about `api.py:5738`. The order is right. The parrot door refuses a body whose words are the criterion's own. A body with a runner's `.invoke` call is Python, so the two doors do not meet on one body in practice. Both refusals state a fact. The surface door's import facts come first, because a test that dies at collection fails before any `.invoke` runs.

## Why a ValueError

The fault is the test's, and not the answer's or the criterion's. The prints door raises a `ValueError` for the same kind of fact. Pass 1's comment gave another reason, and that reason was wrong for s139: m63 cites no criterion, so a `Wall` would not have left m62 unresolved.

## The known miss

Night 119's `tst_v3`, version 2, calls `runner.invoke(dummy_cmd)` on a local `def` that carries only `@version_option`. The door admits it, because a local name is the test's own.

## Deviations from the brief

1. The receiver rule also reads `CliRunner()` inline and `<module>.CliRunner(...)`. Both are runners. The brief names a bound name and `runner` only.
2. The door records no fact when the session has no batch. `_worktree_lines` reads only the batch's worktree, so a fact on the root would fail the check against a true refusal.
3. A test cannot reach the night's worktree as it stood. So the eight-night tests read the base commit with `git show`, and the fixture tests prove the working-file read.

## Open

- The gate and the stale count wait for the GPU.
- A re-export through a package's `__init__.py` is still not followed.
