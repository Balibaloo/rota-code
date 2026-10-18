# Frame 143, review 1 of pass 1 at dcea6fd7

Reviewer on Opus, 2026-10-18, read-only, worktree `C:/Users/roman/rota_r143`
at dcea6fd7, parent 5902981b. Meta workflow. The door is sound on its
night bodies. One finding changes what the door admits, one changes the
right-call count, and three findings are low.

## (a) Verdict on each point

1. Provenance: the door is new, and it neither duplicates nor contradicts a sibling door. Pass.
2. Red case: s292's turn 1 encodes are admitted 3 of 3 at the parent, and 2 of 3 are refused at the commit. Pass.
3. Count: fires on 34 of 6669 calls, all 34 checked by hand are wrong calls, refuses 0 right calls. The "23 right calls" holds 4 wrong calls. Pass with finding 1.
4. Criterion reader: an example value is not the criterion's own value. Remove the exemption for an example. Finding 1.
5. Refusal text: it names the literal and how to build the expected string. It is 629 characters, the longest of five sibling texts. Pass with finding 3.
6. Population and extra tests: they change confidence only, and not the fire count. Finding 2 corrects the right-call denominator.

## (b) Findings

1. `rota/roles/api.py:7324`, `return [x for x in out if x not in criterion_text]`. Severity high. CONFIRMED. The exemption admits a literal that the criterion gives only as an example. Night 139's criterion says "(e.g., '3.10.4'), derived from `sys.version_info`". s250 turns 2, 4, 5 and 6 then asserted `assert "3.10.4" in result`, with the comment "actual version will vary". The harness venv runs Python 3.14.2 (observed: `.venv/Scripts/python.exe -V`, 2026-10-18), so these four tests fail against any correct code. With the parenthesised example removed from the criterion text, the door fires on exactly these 4 calls and on no other call (probe `eg_probe.py`). Fix: remove example spans, "(e.g. ...)", "(for example ...)" and "(such as ...)", from the criterion text before the exemption check, and add s250's body as a refused test.

2. Implementer's report, "Refuses 0 of 23". Severity low. CONFIRMED. The 23 right calls include calls outside a source criterion, where the door cannot fire. Over the source criteria, the rerun finds 20 calls whose criterion holds the literal. 4 of them are s250's wrong calls (finding 1). So the door refuses 0 of 16 right calls in its reach. Fix: write the closing count as "fires on 34 of 34 pinned-literal bodies, refuses 0 of 16 right calls", and 38 of 38 after finding 1's fix.

3. `rota/roles/api.py:8028-8036`, the refusal text. Severity low. CONFIRMED. The text quotes the first assert that holds a literal, not the assert that pins the expected output. On s292 it quotes the no-flag assert and leaves `endswith("Python 3.10.0")` for a second refusal. On s320 (7 fires) the body already builds `expected_suffix` from `sys.version_info`, and the text still tells the seat to build it. The text is 629 characters against 227 to 451 for the frames 273 and 277 texts. The quoted sentence and line have no length limit. Fix: name every literal assert in one refusal, say "remove the literal" when the body already reads `sys.version_info`, and give the host's real version.

4. `rota/roles/api.py:7317-7323`, the literal reader. Severity low. PLAUSIBLE. The reader takes any `3.x` or `3.x.y` string in an assert as a Python version. A test that sets its own program version, `@version_option("3.2.1", show_python=True)` and `assert "3.2.1" in out`, is refused under a source criterion (reader probe, a constructed body). No night body has this shape, so the count does not move. Fix: admit a literal that the test also passes as a call argument outside the asserts.

5. `rota/roles/api.py:7292`, `_PY_VERSION_SOURCE`. Severity low. CONFIRMED. The reader matches "the running interpreter's version", "platform.python_version()", "platform.python_version_tuple()" and "sys.version.split()[0]". It does not match "the Python interpreter version", "the current Python version", "the interpreter running the test" or "sys.hexversion". Night 154's `ver_opt_show_py` and night 156's `ver_opt_show_py_format` stay outside the door, as the implementer reports. The narrow reader follows frame 147's finding. Fix: none in this pass. Write the miss list in the frame's status so a later night can count it.

## Point 1: provenance

`tests_encode` (`rota/roles/api.py:7348-8855`) holds these body doors in order. The sentence-copy door is from 38dff85e (2026-08-15). The `input()` door and `_invented_literals` are from a15c92c7 (2026-09-02). The closed-stdin door is from a27aadf7 (2026-09-14). Frame 273's `or True` door is 000dfa78 (2026-10-17). Frame 277's cannot-fail operand door is 7b48a630 (2026-10-17). The invented-literal door stages a ledger row and admits. Frame 143's door sits after frame 277's door and before the mock and invented-literal doors. No earlier door reads a version literal, and no door reads the criterion's source words. Frame 277 refuses `... or sys.version_info[0] == 3`. Frame 143 tells the seat to compare against a value built from `sys.version_info`, which frame 277 admits. So frame 143 neither duplicates nor contradicts a sibling. Frame 143 refuses first, so the invented-literal door stages no ledger row for "Python 3.10.0", which is the correct order.

## Point 2: the red case

The probe replays the three `tests.encode` calls of s292 seq 1 from `clickI_night156.db`, with each criterion's stored text. At 5902981b all three are admitted. At dcea6fd7, `ver_opt_show_py` and `ver_opt_show_py_env` are refused with the frame 143 text, and `ver_opt_show_py_format` is admitted. The format criterion names no source, so its admission is by design. The criterion texts are the end-of-night rows, version 4 and version 2, and not the rows at turn 1.

## Point 3: the count

- `tests.encode` calls: 6669 (observed: rerun, 2026-10-18).
- Fires: 34, in 7 sessions: night 142 s481 (5), s488 (7), s562 (3), night 156 s292 (6), s294 (2), s299 (4), s320 (7). This matches the implementer's count.
- Calls with a version literal under a source criterion, by the commit's literal regex: 109. The implementer's 94 uses a different literal regex. The door fires on 34 of them.
- Hand check of all 34. Night 142 s481 and s488 assert `"3.12" in ... or "3.11" in ... or "3.10" in ...`. Night 142 s562 asserts `'3.10' ... or '3.9' ... or '3.8'`. Night 156 s292, s294 and s299 assert `"Python 3.10.0" not in result.output` or `endswith("Python 3.10.0")`. Night 156 s320 asserts `... or result_off.output.strip() == "3.10.0"`. Each one fails or checks nothing on the 3.14.2 host. There is no false fire in the 34. The s320 fires are right refusals with a text that does not fit the body (finding 3).
- Right calls: 20 under a source criterion, 0 refused. 4 of the 20 are wrong calls (finding 1), so 0 of 16.
- The name-binding path, `expected = "Python 3.10.0"`, fires on 0 of the 34 night bodies. Only the constructed test 2 reaches it.

## Point 4: the criterion reader

See findings 1 and 5. The answer to the open question is no. An example value shows the format. The criterion's source words still name the interpreter, so a literal taken from the example is pinned. s250 shows the cost: four stored tests that fail on any host other than 3.10.4.

## Point 5: the refusal text

The text names the literal and quotes the criterion sentence. It gives the f-string with `sys.version_info.major`, `.minor` and `.micro`, and `import sys`. So the seat can build the expected string from the text alone. Rendered lengths (observed: probe `lengths.py`, 2026-10-18): frame 143 on s292 629 characters, frame 277 451, frame 273 361, closed stdin 268, constant assert 227. The sentence-copy door is longer than all of these. See finding 3.

## Point 6: the population and the two extra tests

The door cannot fire without a source criterion. So n = 94 or n = 6669 gives the same 34 fires. The choice changes how the ratio looks, and not the count. Test 2, a literal through a name, and test 5, a criterion with no source, add confidence only. Test 2 pins a path that no night body used. Test 5 pins the frame 147 constraint. Neither test changes the frame's count. The right-call denominator does change (finding 2). The new test file and `tests/rota/test_triage_fork.py` give 58 passed at dcea6fd7. The gate did not run in this review.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/6977407c-6cda-4904-bd57-2ba520a13d06/scratchpad/r143/`.

- `parent/rota`: the parent package from `git archive 5902981b rota`, for the replay.
- `probes/replay_s292.py <package root>`: replays s292 seq 1's three encodes through `sandbox.build("tester")` with the night's criterion texts. It ran on the parent and on the worktree.
- `probes/count.py`: reruns the door's predicate over every `tests.encode` call in `clickI_night1*.db`, read-only. The output is `probes/count_out.txt`.
- `probes/eg_probe.py`: removes example spans from source criteria and lists the calls whose result changes.
- Reader probe, inline `python -`: source-word phrases, the package-version body, a literal in an assert message, and `_sentence_around` on night 139's criterion.
- `probes/lengths.py`: renders five encode refusals and prints their lengths.
- pytest: the new test file and `test_triage_fork.py`, 58 passed.

## (d) Usage

The caller reads the usage from the harness. The reviewer estimates about 50k input and 14k output, about 64k total. No sub-agent ran.
