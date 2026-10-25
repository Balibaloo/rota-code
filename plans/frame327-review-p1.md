# Frame 327, review 1 of pass 1 at 19ae12b5

Date: 2026-10-25. Reviewer: a read-only agent on Opus, worktree `C:/Users/roman/rota_r327` at 19ae12b5, base 85f685e6.

Verdict: accept d85a8db4 (repair 1) for the branch. Do not accept 19ae12b5 (repair 2) as it is. Its bare-id form shows a wrong call for comma-joined ids, which is a quarter of the old refusals in the register (finding H1). Fix H1 in a pass 1b before the cherry-pick, because 19ae12b5 stales 8 cases and a second text change would stale them again.

## (a) Verdicts

1. CONFIRMED. Every offered parameter has its true type. 210 of 1089 `api.py` parameters changed. The list and dict parameters that stay `string` are unions or sets, and no role is offered one.
2. CONFIRMED. The handler is `except Exception`. A non-evaluation error recurs on the second call and is not masked. The fallback degrades the whole function in silence (finding L1).
3. CONFIRMED. The exec-built `send` evaluates in its own namespace. The namespace keeps the same keys before and after.
4. CONFIRMED. Review 3's probe gives byte-identical prompts over 98 cases and 325 prompts. `keyprobe.py` gives byte-identical keys. The door text change reaches text replays only through point 7.
5. CONFIRMED. The register holds 0 native runs and 0 native cassettes. No test pins a real native key or a real tools hash.
6. CONFIRMED for the two probes. Both forms refuse, both show `refs=[...]`, and both keep under the length rules. The bare-id form is wrong for comma-joined, space-joined and empty strings (finding H1).
7. CONFIRMED. 11,183 text runs over 40 cases hold the old text. On the suite model qwen3:8b, 8 cases hold the text on their latest prompt, so the gate's stale count rises by up to 8.
8. CONFIRMED. The file has 0 CR, 0 doubled backslash, 4 intact backslash-quote escapes, and parses. 6 passed.
9. CONFIRMED. The six reds are in the gate baseline of f9f5cd19. Frame 281's four Tester reds cover none of them. `test_handover` is flaky, not red.

## Point 1: the true JSON type of every parameter, CONFIRMED

The probe `p1.py` builds each schema twice, once with the new `schema_for` and once with `inspect.signature` forced to the old reading. It compares the shapes with the descriptions removed.

- `api.py`: 448 functions, 1089 parameters, 0 evaluation failures. 210 parameters changed: 95 to an array of strings, 54 to integer, 26 to boolean, 25 to object, 9 to an array of integers, 1 to number. No `required` list and no description changed.
- The working sets of all eight graph roles, built with `sandbox.build`: 0 evaluation failures. 108 role-parameter changes, 54 to an array of strings and 54 to integer, over 64 distinct function-parameter pairs. No role offers a `bool` or a `dict` parameter today.
- `X | None` describes X. `glossary.consult`'s `terms`, `list[str] | None`, is an array.
- Still `string` in a working set, with a container in the annotation:
  - `ledger.log`'s `kind`, `str | list[str]`. `schemas_for_sandbox` replaces it with the mode's enum, so the seat never sees `string`.
  - `msg.challenge_*` and `msg.answer_*`'s `quotes`, `str | list | dict`. A union of three gives `string`, as before. The door accepts all three forms.
- Still `string` in `api.py`, not offered to any role: 21 parameters annotated `set[int]`, `frozenset[int]` or `list[str] | tuple`. `_json_type` has no mapping for a set or a tuple (finding L3, outside).
- The implementer reports "85 parameters are now arrays" over seven roles. The probe counts 54 array changes over eight roles, the Researcher included. The report's count is not reproduced (finding L4, outside).

## Point 2: the fallback catches only the evaluation failure, CONFIRMED

The handler at `rota/llm/toolschema.py:128-131` is `try: inspect.signature(fn, eval_str=True)` and `except Exception: inspect.signature(fn)`. The class is broad, but only the evaluation differs between the two calls. A signature error recurs on the second call and propagates.

Probe `p23.py`, in a module with the future import, as every rota module has:

- `a: nosuchmod.Thing` (an unimportable name): NameError caught. The schema returns, and every parameter is `string`, including `b: list[str]` and `c: int`.
- `a: "Undefined"`: caught, the same result.
- `list[str] | "Bad"`: the TypeError at evaluation is caught.
- The non-callable `42`: TypeError propagates from the second call. Not masked.

The fallback is silent and per function. One unresolvable annotation turns every list of that function back into a string, and no test or log shows it (finding L1). The venv runs Python 3.14. In a module without the future import, an undefined name raises NameError from both calls under PEP 649. That is the old behaviour too, and no rota module is in that state.

## Point 3: the exec-built `send`, CONFIRMED

Probe `p23.py` on the Developer's `msg.challenge_tester`:

- `__globals__` is the exec namespace, not the sandbox module. The keys are `_label`, `_prose`, `_stage`, `_why`, `send` and `__builtins__`.
- The raw annotations are strings, because `exec` inherits the future flag from `sandbox.py`. `co_flags` has the future-annotations bit.
- `inspect.signature(fn, eval_str=True)` gives `(refs: list[str], quotes: str | list | dict, reason: str | None = None, round_no: int = 0)`.
- The key set of the namespace is the same after the evaluation. No name was added.
- The schema: `refs` array of strings, `quotes` string, `reason` string, `round_no` integer. The `msg.question_*` sends have the same shape with `question` string. The `msg.elect_*` and `msg.escalate_*` sends use the module globals and give the same `refs` array.

## Point 4: text mode is untouched, CONFIRMED

1. I ran review 3's probe, the copy at `.../scratchpad/p327/hist_identity.py`, at 19ae12b5 with `PYTHONPATH` on the worktree. The output is 98 cases, 325 prompts, 0 errors. `cmp` against the implementer's `p327/h_base.json` from 85f685e6: identical.
2. I ran `p327/keyprobe.py` at 19ae12b5. `cmp` against `p327/k_base.json`: identical.
3. `key_for` at `rota/llm/cassettes.py:198-224` adds the tools hash only when `protocol == "native"` and is unchanged by the pass.

The scripted probe never sends a string `refs`. So it cannot show the bare-id text change. Point 7 counts the text runs that do.

## Point 5: native keys, CONFIRMED

- `D:/repos/rota/tests/rota/cassettes.db`, opened `mode=ro`: `case_runs` holds 489,707 rows, all `protocol = 'text'`. 0 cassettes have a non-empty `tool_calls`. Repair 1 makes 0 register rows stale through the tools hash.
- The worktree has no `tests/rota/cassettes.db`.
- Tests that call `key_for` with `"native"` (`test_native_calls.py:271-279`, `test_register_key.py:124-203`) pass synthetic tools such as `[{"name": "a"}]`. No test pins a hash of a real schema. `test_native_calls.py`, `test_register_key.py` and the frame's file: 95 passed, 2 skipped.

## Point 6: the `refs` door at `sandbox.py:3064`, CONFIRMED for the two probes

Probe `p6.py`, the Vision Keeper's `msg.report_liaison`:

| sent | branch | the form shown | words | longest sentence |
|---|---|---|---|---|
| `'["c_734322", "tst_dcae01"]'` | list in a string | `refs=["s_1b9009", "c_734322"]` | 20 | 11 |
| `'m_283ec8'` | bare id | `refs=["m_283ec8"]` | 37 | 17 |
| `'  [c_1'` | list in a string | the fixed example | 20 | 11 |
| `''` | bare id | `refs=[""]` | 37 | 17 |
| `'c_1, c_2'` | bare id | `refs=["c_1, c_2"]` | 38 | 17 |
| `'c_1 c_2'` | bare id | `refs=["c_1 c_2"]` | 38 | 17 |

- Every string raises ValueError. 0 messages are stored. The list and tuple paths are unchanged: `[]` lands as before, and an unknown id refuses as "names no row".
- The pass accepts nothing new. Both new branches sit inside `if isinstance(refs, str)` and raise.
- No global cap on door texts exists. Two per-door tests set the rules: `test_frame308_answer_after_respecify.py:248` (each sentence at most 20 words outside the quote) and `test_frame258_request_line.py:105` (under 50 words). Both new texts meet both rules.
- The bare-id form copies the whole string into one element. For the empty string, a comma-joined string and a string with a label such as `refs: b_348da1`, the form is a wrong call (finding H1).
- The `[` branch shows fixed ids, not the seat's own ids (finding L2).

## Point 7: text runs that hold the old text, CONFIRMED

Probes `p7.py`, `p7b.py` and `p7c.py`, all `mode=ro`, search for "one id as a bare string".

- 11,183 runs over 40 cases, all text. By model: qwen3:8b 10,585, llama3.1:8b 371, qwen3.5:9b 137, qwen3:4b 70, gemma3:12b 15, qwen3.5:4b 5.
- 627 cassettes hold the text in the system, user or completion field.
- On the latest prompt hash of each case and model: 5,150 runs over 29 cases.
- On the suite model qwen3:8b and the latest prompt: 4,916 runs over 8 cases. The live runs give the same 8 cases, 49 live runs in all.

| case | qwen3:8b runs on the latest prompt | live runs holding / live runs |
|---|---|---|
| L1-AR-a-dead-end-is-reported-not-sat-on | 14 | 4 / 65 |
| L1-AR-a-dead-end-leaves-the-desk-to-a-named-seat | 486 | 3 / 10 |
| L1-CR-fail-names-its-criterion | 21 | 3 / 100 |
| L1-DV-a-wordless-answer-leaves-a-wrong-test-alone | 53 | 3 / 66 |
| L1-DV-escalate-a-finding-the-loop-could-not-answer | 792 | 16 / 25 |
| L1-DV-fix-what-the-verdict-names | 184 | 1 / 45 |
| L1-LI-present-the-touch | 2877 | 16 / 16 |
| L2-AR-place-a-block-developer-could-not | 489 | 3 / 46 |

The gate's stale count can rise by up to 8 cases on qwen3:8b. Two of the 8 are already baseline reds: `L1-CR-fail-names-its-criterion` and `L1-DV-a-wordless-answer-leaves-a-wrong-test-alone`. The step from a run to a stale case is PLAUSIBLE: the replay of a recorded refusal gives a new next prompt, and the key misses.

The value after "bare string, " in the old refusals: 8,370 single ids, 2,852 comma-joined, 193 space-joined. The qwen3:8b live runs of `L1-LI-present-the-touch` send values such as `b_9f9824, i_62de3d`. At least one live run sent a list in a string, `['c_c2e7a4', 'tst_a8b667']`, which now takes the `[` branch.

## Point 8: the test file's bytes, CONFIRMED

- `tests/rota/test_frame327_schema.py` at 19ae12b5 equals the worktree copy. 3,249 bytes, 0 CR, 0 doubled backslash, 4 backslashes, all in the backslash-quote escapes of line 79. The file ends with LF and parses.
- The exact-text test at line 76 matches the door's text, so no escape was lost.
- `pytest tests/rota/test_frame327_schema.py`: 6 passed in 3.44s.

## Point 9: the six reds at 19ae12b5, CONFIRMED

I ran the six reds at 19ae12b5: 6 failed, 58 passed, 4 xfailed. Each is in the gate baseline `.rota-gate.json` of f9f5cd19, 2026-10-18, both in `D:/repos/rota` and in `C:/Users/roman/rota_g301`.

| test | in the baseline | covered by frame 281's four |
|---|---|---|
| test_invoke_door.py::test_a_session_with_no_batch_reads_the_root | yes | no |
| test_onboarding.py::test_the_same_constraint_written_twice_is_one_gate | yes | no |
| test_scene_two_batches.py::test_a_right_call_lands[the project test tests/test_templates.py as an encode] | yes | no |
| test_fixtures.py::test_no_case_leaves_a_reference_unwrapped | yes | no |
| test_pins.py::test_with_prompt_keeps_every_pin | yes | no |
| test_roles_doc.py::test_a_verb_carries_words_or_does_not_regardless_of_recipient | yes | no |

Frame 281's four Tester reds are register cases: five-criteria, three-criteria one-per-reply, act-on-the-reason and apply-a-term (stack status of 2026-10-25 12:16 and 18:28). They need the register, and the worktree has none, so they skip there. None of the six is one of them. The gate covers the six through its baseline.

`test_handover.py::test_the_sid_decides_the_address_and_not_the_name` is flaky. The base-run failure in `p327/suite_base.txt` is `PermissionError: [WinError 5]` on `os.replace` of a peer file, a Windows file race. At 19ae12b5 it passed 3 of 3 alone, and `test_handover.py` passed 60 of 60.

## Findings

Ranked by severity.

1. H1, high, CONFIRMED. `rota/core/sandbox.py:3074-3078`. The bare-id form puts the whole string into one element. A comma-joined string such as `b_9f9824, i_62de3d` gets one element that holds both ids. The empty string gets a list that holds an empty string. A labelled string such as `refs: b_348da1` gets one element with the label in it. The register shows 3,045 of 11,415 old refusals were comma-joined or space-joined. `L1-LI-present-the-touch` does this on its qwen3:8b live runs. The commit's own comment says a small model follows a refusal literally. Fix: split the string on commas and whitespace, keep the id tokens, and show them, such as `refs=["b_9f9824", "i_62de3d"]`, and show `refs=[]` for an empty string.
2. L1, low, CONFIRMED. `rota/llm/toolschema.py:128-131`. The fallback is per function and silent. One bad annotation turns every list and int of that function back into `string`. The probe showed `b: list[str]` and `c: int` as `string`. No test fails if an offered function falls back. Fix: add a test that every function of the eight roles' working sets evaluates with `eval_str=True`.
3. L2, low, PLAUSIBLE. `rota/core/sandbox.py:3070-3073`. The `[` branch shows the fixed ids `s_1b9009` and `c_734322`. A seat that copies the form literally sends ids that name no row and gets a second refusal. Fix: when the string parses as a list of strings, show those ids in the form.
4. L3, low, CONFIRMED, outside. `rota/llm/toolschema.py:38-65`. `_json_type` has no mapping for `set`, `frozenset` or `tuple`. 21 `api.py` parameters stay `string`. No role is offered one today. Fix: map those origins to an array, or record that no offered function uses them.
5. L4, low, CONFIRMED, outside. The implementer's report, section (a), says 85 parameters are now arrays over seven roles. The probe counts 54 over eight roles, the Researcher included. Fix: correct the count in the frame's record.

## Probes

All probe files are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/66edc387-a3b2-48b8-8dec-bb5b3aa63e50/scratchpad/r327/`. Each ran from `C:/Users/roman/rota_r327` with `D:/repos/rota/.venv/Scripts/python.exe`.

- `p1.py`: compares the old and the new schema of 448 `api.py` functions and of the eight roles' working sets.
- `p23.py`: the fallback with an unimportable name, an undefined name, a TypeError at evaluation and a non-callable. Then the exec-built `send` of the Developer.
- `hist_identity.py` and `keyprobe.py` (review 3's, in `../p327/`): the outputs `h_r327.json` and `k_r327.json`, compared with `cmp` to `../p327/h_base.json` and `../p327/k_base.json`.
- `p6.py`: the `refs` door with nine values, and the word counts of each text.
- `p7.py`, `p7b.py`, `p7c.py`: the register in `mode=ro`, the runs and cassettes that hold the old text, the latest-prompt and live narrowing, and the sent values.
- pytest: the frame's file, `test_native_calls.py` with `test_register_key.py`, the six reds, and `test_handover.py` four times.
- A byte check of `tests/rota/test_frame327_schema.py` through `python -c` with `chr(92)`.

## Usage

The harness shows no exact count. Estimate: about 95k input tokens in context at the end, about 18k output tokens, about 113k total. No sub-agent.
