# Frame 143, review 2 of pass 1b at 89bcef6b

Reviewer on Opus, 2026-10-18, read-only, worktree `C:/Users/roman/rota_r143`
at 89bcef6b, parent dcea6fd7. Meta workflow. Pass 1b closes review 1's
finding 1, and the count is 38 of 38 and 0 of 16. Three findings are low.
No finding is high.

## (a) Verdict on each point

1. Example stripping: s250's four rows are refused, and the source words stay. An open "e.g.," or "for example," clause with a comma is not stripped. Pass with finding 1.
2. Count: fires on 38 of 38 pinned bodies, refuses 0 of 16 right calls, over 6669 calls. No change from review 1 except s250's 4 new fires. Pass.
3. Refusal text: s292 is 430 characters and quotes both asserts. A four-assert body is 449 characters and drops two of five literals with no count. Pass with finding 2.
4. Own program version: yes, a pinned assert can hide. A literal passed to any call outside the asserts admits the body. Finding 3.
5. Tests: the two test files give 61 passed. Frames 273 and 277's tests sit in `test_triage_fork.py` and pass. No new red.

## (b) Findings

1. `rota/roles/api.py:7299-7302`, `_EXAMPLE_SPAN`. Severity low. CONFIRMED. The open-clause branch needs whitespace right after the keyword. "sys.version_info, e.g., 3.12.1." and "sys.version_info, for example, '3.12.1'." keep the literal, so a pinned `assert out.endswith("3.12.1")` is admitted. "e.g. 3.12.1" and "(e.g. 3.12.1)" are stripped and refused. No night criterion has the comma form outside parentheses, so the count does not move. Fix: allow an optional comma after the keyword, `(?:e\.g\.|for example|for instance|such as),?\s`, and add a test for "e.g., 3.12.1".

2. `rota/roles/api.py:8072-8085`, the refusal text. Severity low. CONFIRMED. The text names at most three literals and gives no count of the rest. A body with four pinned asserts and five literals names '3.10.0', '3.11.4', '3.12.1' and drops '3.13.0' and '3.9.7'. The asserts get "and 2 more", but the literals do not. The text also says "the literal" before a list of three. The `builds` flag reads only `sys.version_info`, `sys.version` and `platform.python_version` as attributes. A body with `from sys import version_info` gets `builds=False` and the build step. Fix: write "the literals" for more than one, and add "and N more" after the third literal.

3. `rota/roles/api.py:7320-7326`, the `given` set. Severity low. CONFIRMED. Any string constant in any call outside an assert exempts its version literal. Three constructed bodies under the s292 criterion are admitted with `assert ... "Python 3.10.0"` in an assert: `check(result, "3.10.0")` with a helper that asserts, `print("expected 3.10.0")`, and `result.output.split("Python 3.10.0")`. A literal in an assert message stays refused, because the message is inside the `Assert` node. No night body under a source criterion passes a version literal to a call outside its asserts (0 calls), so the count does not move. Fix: admit a literal only when it is an argument of a decorator call or of a call named `version_option`, and add the helper body as a refused test.

## Point 1: the s250 replay

The probe reads s250's `tests.encode` calls for `c1_version_option_show_python` from `clickI_night139.db` and runs them through `sandbox.build("tester")` with the row's criterion text. Seq 2, 4, 5 and 6 are refused, each with a 335-character text that quotes `assert "3.10.4" in result`. The source match runs on the full criterion text, not on the stripped text. So "the version from sys.version_info, e.g. 3.12.1" keeps its source words, and the door fires. "Read sys.version_info, e.g. the major part. The output must be exactly 3.12.1." strips only the first clause and admits the literal from the second sentence. That is correct.

## Point 2: the count

- `tests.encode` calls: 6669 (observed: rerun at 89bcef6b, 2026-10-18).
- Fires: 38 in 8 sessions. Night 142 s481 (5), s488 (7), s562 (3). Night 139 s250 (4). Night 156 s292 (6), s294 (2), s299 (4), s320 (7). The 34 of review 1 are unchanged, and s250's 4 are new.
- Right calls whose criterion holds the literal: 20. The door refuses 4, which are s250's wrong calls. The other 16 are night 138 s377, s379, s381, s386 and night 139 s271. In each, the literal sits only in a comment that copies the criterion. So the door refuses 0 of 16.
- Fires whose body reads the interpreter: 7, all s320. Fires with more than one pinned assert: 12. The most asserts in one fire: 3.
- Calls under a source criterion that the `given` set exempts: 0.

## Point 3: the text

- s292: 430 characters. It quotes both pinned asserts, the first cut at 64 characters. It names '3.10.0' once. It gives the build step, because the body does not read `sys`.
- s320: the 7 fires carry "Remove the literal", because the body reads `sys.version_info`. The constructed s320 test pins this.
- A constructed body with four pinned asserts and five literals: 449 characters. It quotes two asserts and adds "and 2 more". See finding 2 for the literals.
- "Remove the literal" appears only when `builds` is true. `builds` is true for `platform.python_version()` and false for `from sys import version_info`.

## Point 4: the admitted program version

See finding 3. A helper that asserts inside, with no literal in its own assert, was outside the door before this pass too. The new hole is the second step: the same literal in a direct assert is also admitted once a call takes it.

## Point 5: the tests

`ROTA_MODEL=qwen3:8b python -m pytest tests/rota/test_frame143_literal_version.py tests/rota/test_triage_fork.py -q` gives 61 passed at 89bcef6b. Frames 273 (000dfa78) and 277 (7b48a630) added their tests to `test_triage_fork.py`. The gate did not run in this review.

## Outside the points

None found.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/6977407c-6cda-4904-bd57-2ba520a13d06/scratchpad/r143b/`.

- `count2.py`: reruns `_literal_python_version` over every `tests.encode` call in `clickI_night1*.db`, read-only. It counts fires, right calls, `builds`, multi-assert fires and `given` exemptions.
- `peek.py`: prints the literal lines of the night 138 and night 139 right calls.
- `p134.py`: eight criteria through `_EXAMPLE_SPAN` and the door, and s250's rows through `sandbox.build("tester")`.
- `p34.py`: the four-assert text, the `builds` flag, and four bodies that hide a literal through a call.
- pytest: the two test files, 61 passed.

## (d) Usage

The caller reads the usage from the harness. The reviewer estimates about 40k input and 9k output, about 49k total. No sub-agent ran.
