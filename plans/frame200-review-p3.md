# Frame 200, pass 3: diff review of fa508ab7

Reviewer: an Opus agent, read-only, on the worktree `C:/Users/roman/rota_rv200p3` at fa508ab7. Written 2026-10-11 21:58. The diff is `git diff 1ea71e58 fa508ab7`, two files.

**Verdict: STANDS.** Points: 5. Points met in full: 3 (1, 2, 5). Points met in part: 2 (3, 4). Findings: 4, all low. CONFIRMED: 3. PLAUSIBLE: 1. New reds from the diff: 0.

The two night 140 bodies are refused, and every correct test of point 2 is admitted. The attribute kinds also refuse a test that runs the option through a command and reads an attribute beside it. No night 140 body has that shape, so the finding is low.

## (a) Verdict on each point

1. Yes. Both night 140 bodies are refused with kind `decorator-attribute`. The refusal names the factory's `def` line through the fact, and no test line.
2. Yes. Three correct tests are admitted. A fourth edge shape, an attribute read on the bare return beside a real run, is refused (finding 1).
3. In part. The `inline-attribute` kind fires on `version_option(...).callback(...)`. A correct test with `version_option(...).__name__` beside a real run is refused (finding 1). The suite holds no row for the kind (finding 2).
4. In part. The text states the fact and offers no runner call, inside ruling 6b52a09d. The text does not tell an 8b Tester what to write instead (finding 3).
5. Yes. The four door files give 463 passed and 1 failed. The 1 red is also red at 1ea71e58, so the diff does not cause it (finding 4, outside).

## (b) Findings

1. `rota/roles/api.py:6002-6008`. Severity low. CONFIRMED. The attribute walk refuses any attribute read on a factory return, even when the same test runs the option through a command. Probe P2d and probe P3c are both refused. P2d reads `opt.__name__` after it invokes `cli = command()(opt(hello))`. P3c reads `version_option(show_python=True).__name__` beside a decorated command that it invokes. The call kinds `decorator` and `decorator-argument` have the same gap from earlier passes, so the pass follows the precedent. Fix: skip the two attribute kinds when the test also applies the factory to a command that the test runs.
2. `tests/rota/test_prints_door_kind.py:781-786`. Severity low. CONFIRMED. No row reaches `inline-attribute`. Probe P3a shows that the kind fires, with the text in point 3. Fix: add P3a's body as a row of `test_a_factory_that_adds_an_option_on_a_plain_function_is_refused`.
3. `rota/roles/api.py:6961-6962`, the door text. Severity low. PLAUSIBLE. The text says what the test does wrong, and not what runs the option. Night 140's read, section 2, records the sibling text "passing it to a call" on `tst_v2_show_python`. After it, s325 sent 33 encodes and stored no test for c2 (copied from the read, not re-run here). Fix: count this kind's refusals and re-encodes on the next night, and bring residue to Roman with frame 177's exclusion cited.
4. Outside. `tests/rota/test_invoke_door.py:372`, `test_a_session_with_no_batch_reads_the_root`. Severity low. CONFIRMED. The test fails with "DID NOT RAISE" at fa508ab7, and also at 1ea71e58 from a `git archive` copy. The diff does not cause it. Fix: check that the gate's red or stale set holds the test, and push a frame if it does not.

A note on the line item, no finding: `decorator-attribute` returns the binding line, 8 for N140_V1. `inline-attribute` returns the line of the attribute. The caller drops `_line` at `api.py:6949`, so no refusal shows either number.

## Point 1: night 140's two bodies

Probe P1 ran `_plain_decorated` and the door through `tests.encode` on `N140_V1` and `N140_V3`. The pass copied these bodies from `clickI_night140.db`.

```
P1-n140-v1 | _plain_decorated= ('option', 8, 'decorator-attribute', 'callback') | REFUSED: `option` is the decorator that `version_option` returns, and reading `.callback` on it never runs the option that `version_option` adds
P1-n140-v3 | _plain_decorated= ('option', 8, 'decorator-attribute', 'callback') | REFUSED: `option` is the decorator that `version_option` returns, and reading `.callback` on it never runs the option that `version_option` adds
```

The probe ran outside pytest, so the refusal hook of the conftest gave no facts. The pytest rows assert the fact `("line_text", "def version_option")`:

```
ROTA_MODEL=qwen3:8b python -m pytest tests/rota/test_prints_door_kind.py -q -n 0 -p no:cacheprovider -k n140 -v
2 passed, 79 deselected in 0.80s
```

So the refusal names the line `def version_option` of the worktree's `src/click/decorators.py`. That is the right line for a fact of the worktree. The refusal names no line of the test.

## Point 2: false refusals on correct tests

```
P2a-runner-output | _plain_decorated= None | ADMITTED
P2b-call-command | _plain_decorated= None | ADMITTED
P2c-bare-applied-then-attr | _plain_decorated= None | ADMITTED
P2d-bare-applied-attr-on-bare | _plain_decorated= ('opt', 9, 'decorator-attribute', '__name__') | REFUSED: `opt` is the decorator that `version_option` returns, and reading `.__name__` on it never runs the option that `version_option` adds
```

- P2a puts `@command()` and `@version_option(show_python=True)` on `cli`. It invokes `CliRunner().invoke(cli, ["--version"])` and reads `result.exit_code` and `result.output`.
- P2b calls the same decorated `cli` as `cli(["--version"])` inside `pytest.raises(SystemExit)`, then reads `capsys`.
- P2c binds `opt = version_option(...)` and `cli = command()(opt(hello))`. It invokes `cli`, then reads `cli.params[0].name` after the invoke.
- P2d is P2c with `opt.__name__` added. P2d is the edge of finding 1.

## Point 3: the `inline-attribute` kind

```
P3a-inline-callback | _plain_decorated= ('version_option', 6, 'inline-attribute', 'callback') | REFUSED: `version_option(...)` returns a decorator, and reading `.callback` on it never runs the option that `version_option` adds
P3b-inline-applied-then-params | _plain_decorated= None | ADMITTED
P3c-inline-dunder-beside-runner | _plain_decorated= ('version_option', 11, 'inline-attribute', '__name__') | REFUSED: `version_option(...)` returns a decorator, and reading `.__name__` on it never runs the option that `version_option` adds
```

- P3a reaches the kind with `version_option(show_python=True).callback(None, None, True)`.
- P3b is admitted. It reads `cli.params` on `cli = version_option(...)(command()(hello))`. `is_factory` does not match a call of a call.
- P3c is the correct test that the kind refuses. It invokes a decorated command, and it also reads `.__name__` on a second inline factory call.

## Point 4: the door text

The text, verbatim, for N140_V1 and N140_V3:

```
`option` is the decorator that `version_option` returns, and reading `.callback` on it never runs the option that `version_option` adds
```

The fact is `line_text` = `def version_option`. The text holds none of the words that `test_the_call_shape_refusal_names_no_shape` forbids: `CliRunner`, `invoke`, `command`, `Decorate`, `assert`, `--`. So the text stays inside ruling 6b52a09d.

The text says that the read never runs the option. The text does not say what runs the option. The comment at the caller says that the sentence omits when a decorated command prints, by frame 177's review. An 8b Tester must infer from the word "decorator" that the option runs only on a command. Night 140's sibling text left s325 with 33 encodes and no stored test for c2 (finding 3).

## Point 5: the other doors

```
ROTA_MODEL=qwen3:8b python -m pytest tests/rota/test_prints_door_kind.py tests/rota/test_invoke_door.py tests/rota/test_desk_guards.py tests/rota/test_fence_nudge.py -q -n 0 -p no:cacheprovider
FAILED tests/rota/test_invoke_door.py::test_a_session_with_no_batch_reads_the_root
1 failed, 463 passed, 1 warning in 64.06s
```

The same test at 1ea71e58, from a `git archive` copy under the scratchpad, with `rota` imported from that copy:

```
FAILED tests/rota/test_invoke_door.py::test_a_session_with_no_batch_reads_the_root
1 failed, 36 deselected in 2.81s
```

`test_desk_guards.py` holds tests of the invented-literal door. `test_invoke_door.py` and `test_fence_nudge.py` hold tests of the surface door. The diff changes the return of `_plain_decorated` only. `rota.tools.map fn _plain_decorated` names one caller, `tests_encode` at `api.py:6946`, and that caller unpacks the tuple with `*attr`.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/59bdd13a-98f3-4dda-ba43-071cb487b114/scratchpad/rv200p3/probe_p3.py` runs `_plain_decorated` and the door through `tests.encode` on nine bodies. It uses the helpers of `test_prints_door_kind.py` and ran from the worktree root.
- `.../scratchpad/rv200p3/base/` is a `git archive` copy of 1ea71e58. The test `test_a_session_with_no_batch_reads_the_root` ran there.
- The pytest runs above ran from the worktree root with `-n 0`.

## (d) Usage

About 45k input tokens, 10k output tokens, about 55k total (estimate). The harness line is the authority. Sub-agent: none. Model calls: none.
