# Frame 164, the scalar door, pass 1

This record is about the rota workflow: the binder that every seat's call goes through. The pass ran in the worktree `C:/Users/roman/rota_f164`, branch `f164`, from `ebed3ae1`.

## 1. The count

The count ran before any edit (observed: `probes/frame164/count.py`, 2026-10-06). The script reads every op of `api.REGISTRY` with `inspect.signature(eval_str=True)`. It keeps each parameter that declares `int`, `bool` or `float`, alone or with `None`. It then parses every `turns.completion` of nights 113 to 126 with `toolproto.extract_lenient`, with every registered op as the allowed set. Each night database opens with `mode=ro&immutable=1`. Every WAL file of these nights is 0 bytes, so the immutable read misses no row. The script writes `probes/frame164/calls.json`, which the replay reads. That file is 15 MB and stays untracked.

The ops with a typed scalar, 8 ops and 11 parameters. No op declares `float`.

| op | defined at | typed scalar parameters |
|---|---|---|
| `brief.list` | api.py:687 | `since_version: int` |
| `brief.segment` | api.py:595 | `span_start: int`, `span_end: int` |
| `code.concordance` | api.py:7661 | `limit: int` |
| `code.prose` | api.py:7260 | `limit: int` |
| `code.source` | api.py:8680 | `start: int`, `end: int` |
| `code.write` | api.py:9250 | `start: int`, `end: int` |
| `problem.prioritize` | api.py:1148 | `priority: int` |
| `verdicts.claim_encodes` | api.py:6533 | `encodes: bool` |

The calls on nights 113 to 126. A row counts values, so a call with `start` and `end` counts twice.

| op | parameter | arrived as | `int()` or the word converts | values |
|---|---|---|---|---|
| `brief.list` | `since_version` | int | | 75 |
| `brief.segment` | `span_end` | int | | 45 |
| `brief.segment` | `span_start` | int | | 45 |
| `code.prose` | `limit` | int | | 8 |
| `code.source` | `end` | int | | 20127 |
| `code.source` | `start` | int | | 20127 |
| `code.write` | `end` | int | | 930 |
| `code.write` | `start` | int | | 930 |
| `problem.prioritize` | `priority` | int | | 211 |
| `problem.prioritize` | `priority` | str | False | 6 |
| `problem.prioritize` | `priority` | str | True | 62 |
| `verdicts.claim_encodes` | `encodes` | bool | | 34 |

Totals: 42600 typed scalar values in 20398 distinct calls. 68 values came as text, and every one is `problem.prioritize`'s `priority`. 62 convert with `int()`: `'1'` to `'6'`. 6 do not, and all 6 are `'high'`: night 115 s200 turns 3 to 6, and night 126 s249 turns 3 and 5. No other op ever received text for a typed scalar.

Only night 126 holds a text priority in `items` (observed: a read of `items` on nights 113 to 126 for `typeof(priority) <> 'integer'`, 2026-10-06). It is `version_option_show_python`, `'high'`. Night 115's four `'high'` calls left no text row.

## 2. The door

The door is in the binder, `validate_args` in `rota/core/sandbox.py`, after the container check and before the enum check. For each parameter whose annotation is `int`, `bool` or `float`, alone or with `None`, and whose value is a `str`:

- `int`: `int(text.strip())`. A success replaces the value.
- `float`: `float(text.strip())`, and the result must be finite. A success replaces the value.
- `bool`: `true`, `false`, `True`, `False`, `1` and `0`, after a strip, map to `True` or `False`.
- Any other text: the binder returns the refusal sentence, and `Sandbox.call` raises it as `ArgumentError`.

A value of another Python type passes unchanged, so `None` at a default passes too. The annotation helper `_scalar_kind` also reads a string annotation, because the binder keeps the string when `eval_str` fails.

`validate_args` takes a new keyword `ctx`. `Sandbox.call` passes `self.ctx`, and the door records its offer with `api._offer`. The offer is the same call with the value replaced by `1`, `1.0` or `True`. `Sandbox.call` now also calls the follow hook, `_ON_REFUSAL`, for an `ArgumentError` that carries offers or facts. Before the pass the hook ran for a `ValueError` of the op only. Only the scalar door records an offer at the binder, so no other binder refusal reaches the hook.

## 3. The sentence

The refusal of s249's call, verbatim:

```
problem.prioritize: priority='high' is a word where problem.prioritize takes a whole number; send priority=1, priority=2 or another whole number
```

The other two forms:

```
verdicts.claim_encodes: encodes='yes' is a word where verdicts.claim_encodes takes true or false; send encodes=true or encodes=false
<op>: <name>='<text>' is a word where <op> takes a number; send <name>=1.0, <name>=2.5 or another number
```

Text with no letter, such as `'1.5'` for an `int`, reads `is text where` in place of `is a word where`. The form follows the enum door, `{key}={value!r} is not one of [...]`: the argument and its value first, then what the op takes.

Frame 144's check admits the sentence (observed: `ROTA_OFFER_LOG` on the three refusing tests, 2026-10-06). Each offer records `second: None`, `said_in_refusal: True` and `bad_args: []`. The offers are `problem.prioritize(id='version_option_show_python', priority=1)` twice and `verdicts.claim_encodes(criterion_id='c1', encodes=True)`.

## 4. The tests

`tests/rota/test_scalar_door.py`, 17 tests. With the door's loop disabled, 16 fail and 1 passes (observed: a temporary edit of the loop's guard to `if True:`, 2026-10-06). The test that passes is the count's own check that the list holds `problem.prioritize` and `verdicts.claim_encodes`.

- `test_s249s_word_for_a_priority_is_refused_and_writes_nothing`: the refusal verbatim, and `ctx.writes` is empty.
- `test_s180s_digit_for_a_priority_lands_as_the_integer_1`: `priority='1'` stages `{"priority": 1}`, and the type is `int`.
- `test_a_word_for_a_truth_value_is_refused_and_true_converts`: `encodes='yes'` is refused and stages no claim, and `encodes='false'` lands as `False`.
- `test_a_value_of_the_declared_type_and_a_default_none_pass_unchanged`: typed values and `None` pass unchanged, text converts, and `'nan'` is refused for a `float`.
- `test_next_batch_on_night_126_returns_bg_3_after_s249s_call`: a backup of night 126's database, read with `mode=ro&immutable=1`, goes to `tmp_path`. The copy sets the item to 1, as s243 left it. s249's turn-5 call goes through the sandbox, the staged writes apply, and `next_batch` returns `["bg_3"]`. Without the door, `'high'` lands and `next_batch` raises the night's `TypeError`. The test skips when the night's file is absent.
- `test_the_count_finds_the_typed_scalars_of_night_126`.
- `test_every_typed_scalar_refuses_the_word_high`, 11 cases, one per parameter of the count's list. The list comes from `api.REGISTRY` at collection, so a new op with a typed scalar joins by itself.

## 5. The replay

`probes/frame164/replay.py` sends each distinct call of the count through one tree's `validate_args`, with the op's signature as the binder exposes it. The parent tree is `git archive ebed3ae1 rota`, unpacked in the scratchpad. The new tree is the worktree.

20398 calls, 67 differ, and all 67 carry text for a typed scalar. The calls with such text number 67 in all. The 68 text values of the count are 67 distinct calls, because night 124 s185 turn 8 sent one call twice. 61 calls convert to an integer, and 6 are refused with the sentence of section 3. No call without text changes.

## 6. The gate's five lines

The command was `D:/repos/rota/.venv/Scripts/python.exe -m rota.tools.gate`, run in the worktree, which took 958.8 s (observed: 2026-10-06, 17:10 to 17:26):

```
suite: 25 failed, 3013 passed, 34 skipped, 12 xfailed, 26 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (4): tests/rota/test_handover.py::test_one_claim_wakes_exactly_one_standby, tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (1): L1-VK-relay-the-ruling (+1 -0 against baseline)
time: 958.8s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The gate also printed `note: the tree moved past the baseline (658abb6 -> ebed3ae)` and `flaky: tests/rota/test_handover.py::test_one_claim_wakes_exactly_one_standby`.

The three hard new reds are not this pass's. Each fails at `ebed3ae1` with `rota/core/sandbox.py` stashed (observed: the three node ids run at the parent, 2026-10-06, `3 failed`). The baseline is from 658abb6, so the gate counts reds that the tree gained between 658abb6 and `ebed3ae1`.

The stale case is this pass's. Its Vision Keeper sends `problem.prioritize(id="i_55ed6f", priority="1")`. The op's result was `"priority": "1"` and is now `"priority": 1`, so the next turn's prompt moved. The case replays green at the parent and reads STALE on the new tree. The card held `qwen3.5:9b` for another implementer until 17:28:40. Then the case was re-recorded by exact id with `ROTA_L1=1 ROTA_MODEL=qwen3:8b ROTA_NUM_CTX=12288`: `17 recorded`, `1 passed`. A replay after it gives `1 passed` with no recording (observed: 2026-10-06, 17:29). The pass did not run the gate a second time.

## 7. Deviations

- The replay runs the binder's argument check, `validate_args`, and not the whole `Sandbox.call` with the op's body. The door lives in `validate_args`, and the op bodies need each night's database state. The parent tree came from `git archive`, not a git worktree, so the pass did not write to `D:/repos/rota/.git`.
- The `next_batch` test does not set the value to 1 and stop. It sets 1 and then sends s249's call through the door, because a test that only sets 1 is green on the parent. The brief asks for every test to be red without the repair.
- `float` refuses `nan` and `inf`, which `float()` accepts. No column means a value that is no number.
- `Sandbox.call` now runs the follow hook for an `ArgumentError` with offers. Without the change, frame 144's check would never read the new offer.
- The gate ran once, before the re-record of the stale case. The record gives that run's lines and the re-record's result apart.
- The `next_batch` test and the count read the night databases under `D:/repos/rota/.rota/`, read-only. The pass wrote nothing under `D:/repos/rota`.

## 8. Seen and not fixed

- The prompt's signature line is `TOOL: problem.prioritize(id, priority)` with no type (night126-read.md section 6). A seat still meets the refusal once before it sends a number. A type in the signature line changes every recorded prompt, so it is a separate frame.
- Night 126's database still holds `'high'`. The door stops a new text value. It does not repair a row that a night already wrote.
- `next_batch` sorts on `-(r["priority"] or 0)` and trusts the column. The door is the only guard. A write that skips the sandbox can still put text there.
- Night 115 s200 sent `'high'` four times on the ticket id `tk_1_version_option_show_python`, and the id door refused each call (observed: `turns.user` of s200, turns 4 to 7, 2026-10-06). The binder's argument check runs before the id door in `_bind`. So on such a call the scalar door now speaks first, and the id refusal comes on the next send. s249's turn 3 has the same shape.

## 9. Report

- `rota/core/sandbox.py`: the helpers `_scalar_kind`, `_scalar_from_text` and `_scalar_refusal` come before `validate_args`. The door loop is in `validate_args`, and `Sandbox.call` passes `ctx` and runs the follow hook for a binder refusal.
- `tests/rota/test_scalar_door.py`: 17 tests, as section 4 lists.
- `probes/frame164/count.py` and `probes/frame164/replay.py`: the count and the replay, kept. `calls.json` is their 15 MB output and stays untracked.
- The cassette of `L1-VK-relay-the-ruling` is re-recorded in the worktree's `tests/rota/cassettes.db`, which git does not track.
- The harness reports the pass's token usage to the assistant. The record does not estimate it.
