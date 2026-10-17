# Frame 223, review 1: the diff of 134a7d8f (parent 804bff55)

Verdict: accepted, with 0 high, 2 medium and 5 low findings. The push fires on the Tester's challenge wake alone, and the cap holds. Two medium findings ask for a pass 2 before the night (reasoned: the findings below, 2026-10-17). Meta workflow review of a rota workflow change.

## (a) Verdicts on the six points

1. The frame choice: PARTLY. Site-packages, stdlib and rota frames never match. A frame in the test module matches and is pushed (finding 1, CONFIRMED).
2. The false push: the s394 push misleads mildly. A rule keyed on the frame avoids it: push only when the line at the frame is a `raise` statement (finding 3, CONFIRMED).
3. The span: never empty and never the whole file. The span stays inside the innermost function. PUSH_CHARS applies to each pushed value (CONFIRMED). A raise inside a method shows no method signature (finding 2).
4. Only the Tester's challenge wake: CONFIRMED. The spy saw the function called on 3 Tester challenge prompts and on no other role or wake.
5. The case: `package_name="click"` runs on the project and the assertion checks only the Python suffix, so the body is right. The expectation admits wrong bodies, because it matches substrings only (finding 4).
6. The hunk alone: no change outside the design in `build_prompt`. The PUSH order of existing keys is unchanged. Two `except Exception: continue` paths hide errors, and the new block is last, so a wake cut removes it first (findings 5 and 6).

## (b) Findings

1. `rota/core/runner.py:2636-2641`, medium, CONFIRMED. The frame test is "the path is a path grain of `code_index`". The index holds test files: night 153 has 52 `tests/` path grains, and `tests/test_version_option.py` is one of them. The probe gave `('tests/test_version_option.py', 9)` for a trace whose last frame is a callback defined in the test module. The design says never the test file. Fix: skip a path that is the file of any row in `tests`, or a grain whose area is the tests area.
2. `rota/core/runner.py:2664-2675`, medium, PLAUSIBLE. `code.source` returns top-level `defs` only. A raise inside a method of a top-level class pushes `class X:` and its docstring line, not the method's `def` line. Most raise sites in click's `core.py` are methods of `Context`, `Command` and `Parameter`. The night-153 count is 14 of 15 on `version_option`, a function, so no case renders this path. Fix: take the signature from the innermost function that `_raising_span` finds, not from the top-level node.
3. `rota/core/runner.py:2636-2641`, low, CONFIRMED. Night 142's tr76 (test `inh_022b8a87`) fails with `TypeError: expected string or bytes-like object, got 'function'` at `src/click/_compat.py:492`, `return _ansi_re.sub("", value)`. The defect is in the caller, `termui.py:334` or `:100`, which passes a function. The push names `strip_ansi` as "the lines that raised" and points the seat at a file the batch did not touch. The signature `value: str` gives a small hint, so the push misleads only mildly. Fix: push only when `_raising_span` ends on an `ast.Raise` that holds the frame's line. All 14 `version_option` frames stay, because line 537 is `raise RuntimeError(`.
4. `tests/rota/cases/l1_tester.yaml:1471-1489`, low, CONFIRMED by reading. `text_includes_any` matches a substring anywhere in the body. The case does not run the body. So a body with the right decorator and a still-failing assertion passes, and so does a match inside a comment. `package_name="pytest"` or `"pip"` passes the test, but the version then comes from a test-runner dependency, which is a weak test. Fix: drop the pytest and pip strings, and add a `text_excludes` for the night's failing assertion form, or run the body.
5. `rota/core/runner.py:2643-2650` and `2657-2662`, low, CONFIRMED by reading. Both `sb.call` sites catch every `Exception` and continue with no record. A programming error in the push then shows as "no push" and no case turns red. Fix: catch only the expected errors (`SyntaxError`, `KeyError`, `ValueError`), or log the skip.
6. `rota/core/runner.py:679-680`, low, PLAUSIBLE. The new keys go after every existing push. The wake cut keeps the front, so a long challenge wake loses the new block first. No probe measured the night-153 wake length against the cap. Fix: count the cut on the night's challenge wakes, and move the block ahead of `code.source` file pushes if the cut ever removes it.
7. Outside: `rota/core/runner.py:2645` and `2658`, low, PLAUSIBLE. `code.source` adds the whole definition to `ctx.opened`, `read_idents` and `read_words`. The seat sees only the signature and the span. A door that checks read identifiers then credits lines the seat never saw. Other pushes at about lines 3081 and 3261 do the same. Fix: none now. Record it beside frame 223 if a door refusal reads `read_idents` on the challenge wake.

Outside, observed: `tests/rota/test_scene_two_batches.py::test_a_right_call_lands[the project test tests/test_templates.py as an encode]` failed in the spy run. The test does not read a prompt. This review did not check it on the parent, so its cause is open (PLAUSIBLE: not this diff).

Outside, observed: the frame regex reads the whole run output. A run of a project test file with two failing tests (tr76) holds two traces. The push takes the last trace, which can belong to another test function of the same file. Low, folded into finding 3.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b0dce033-321f-4299-b3e0-056d78ea27c8/scratchpad/r223/`.

- `clickI_night142.db` and `clickI_night153.db`: copies with their `-wal`. A read of `test_runs` found tr76 with `strip_ansi` and tr225 with the `version_option` trace.
- An inline probe ran the frame loop of `_raised_signature_pushes` on the night-153 index. Results: a site-packages or stdlib last frame falls back to `src/click/decorators.py:537`; a test-module last frame gives `tests/test_version_option.py`; an absolute path and a `rota/` path give None.
- `span.py`: `_raising_span` on eight shapes. Top-level raise gives the raise line. The nested `callback` gives the `if version is None ...` block down to the raise. A loop gives the inner `if` and the raise. A `match` gives the whole `match`. A class-level line gives None.
- An inline probe of `_render` on a 30,000-character span: 20,125 characters with the CUT note.
- `_spy223.py`: a pytest plugin that wraps `build_prompt` and `_raised_signature_pushes`. It ran with `test_scene_challenged.py`, `test_scene_challenged_again.py`, `test_scene_review.py` and `test_scene_two_batches.py`: 109 passed, 1 failed, 1 skipped, 6 xfailed in 41 s. The push function ran 3 times, all on `tester message challenge`. The one prompt with the raising lines is the new scene test's.
- The gate was not run, because of the review's 40k cap.

## (d) Usage

About 70k input tokens, 9k output tokens, 79k total, from the session's own count. The harness line is the record.
