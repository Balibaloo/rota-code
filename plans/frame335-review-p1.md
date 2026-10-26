# Frame 335, review of pass 1

Date: 2026-10-26. Commits: `8a258a69` and `b0f06d41` on `ecf63fde`, read at the detached head `b0f06d41` in `C:/Users/roman/rota_r335`. The reviewer edited no tracked file and ran no model call, no replay case and no whole suite.

## (a) The verdict

**Held: the encode refusal and the quote half stand, but the collection note gives escape advice for a collection error that is not an escape, and the one-backslash raw form changes the body when a backslash comes before a letter that the call's literal decodes.**

## (b) Findings

1. `rota/roles/api.py` 17513, `_note_collection_error`. High. CONFIRMED. The gate is `escape is not None or "Did you mean" in error`. Python 3.12 and later write `Did you mean: 'x'?` on an `ImportError`, a `NameError` and an `AttributeError`. Probe `test_probe_p34.py::test_notes` gave this note for `ImportError: cannot import name 'format_filenme' ... Did you mean: 'format_filename'?`: "... Did you mean: 'format_filename'?`. Write the string as a raw string with one backslash: `r"..."`." The `AttributeError` typo gets the same advice. A Tester that misspells an import now meets advice about raw strings. The strip regex `Did you mean .*` needs a space, so Python's useful advice stays, and only the wrong sentence is added. Fix: gate the advice on `escape is not None` only, and drop the `"Did you mean" in error` arm.
2. `rota/roles/api.py` 17463 to 17484, `_raw_form` and `_raw_advice`. High. CONFIRMED. The advice tells the writer to type the raw form with one backslash in the call. The call's value is a literal that is not raw. Probe `probe_p2.py` sent `body='path = r"C:\Users\new"'`. Both paths stored `r"C:\Users` and a real line break and `ew"`, so the body is no longer Python. `\U` fails the strict path, and the fallback turns `\n` into a line break. With `r"C:\Roaming\new"` the strict path also makes a line break. With `\temp` the strict path makes a TAB and the fallback keeps `\t`, so the two paths store two bodies. `C:\Users\<name>` is the common Windows path, so the advice fails on a common case. The record's own forms, `\R`, `\M` and `C:\Users\x\AppData\Roaming`, store one backslash on both paths with single quote marks. Fix: let `_raw_advice` parse its own call form through `parse_args` and `_parse_args_lenient`, and give a form that comes back unchanged on both, or a forward-slash form for a path.
3. `rota/roles/api.py` 17443, `_ESCAPE_MESSAGES`. Low. CONFIRMED. Python 3.14 writes `"\777" is an invalid octal escape sequence`. No pattern matches it. Probe `test_probe_p1.py[octal]`: before, the body landed. Now it gets "the body is not Python (... Did you mean "\\777"? ...)", which is the level-wrong advice that the frame removes. Fix: add `invalid octal escape sequence` to the patterns and give the escape refusal.
4. `rota/roles/api.py` 9325 to 9337, `tests_encode`. Med. PLAUSIBLE. The refusal fires on every project. A project with no `filterwarnings = error` runs `"C:\Roaming"` with a warning and the correct value. The pass report raises this as its open question 2. The record shows only clickI, which has the filter. Fix: decide open question 2 on purpose, and record the reason in the comment of the refusal.
5. `tests/rota/test_frame328_path_door.py` 41. Low. CONFIRMED. `TST_C4_BODY` is now unused. No test now runs real pytest on a body that errors at collection with a `SyntaxError`. Test 4 of `test_frame335_escape.py` parses a recorded output only. Fix: delete `TST_C4_BODY`, or reuse it for a live-run case of the note.
6. Outside the points. `rota/llm/_lenient.py` 73 to 77. Med. CONFIRMED. The fallback reads only one quote mark. Probe `probe_p2.py` with `body='''path = r"C:\Users\x\AppData\Roaming"'''` stored `''path = r"..."''`. The strict path fails on `\U`, so the fallback takes the call. The call-form refusals in `toolproto.py` teach the triple-mark form. So the brief's own `\U` case fails in the form that rota teaches. This fault is older than frame 335, and the new advice now sends calls to it. Fix: make `closing_quote` and the value cut read a triple mark.
7. Outside the points. `rota/llm/_lenient.py` 26 to 47. Low. CONFIRMED. With `id='t1', body='...'` the fallback put the whole rest into `id`, because `closing_quote` scans from the right and stops at the last mark. A call with two single-quoted values that reaches the fallback loses the later values. Fix: stop at the first mark from the left that a `, name=` or the end follows.

## (c) The points

1. Stands. Lands: the raw form, `"\n"` with `"\t"`, `"\\\\"`, `"\\"`, `\N{BULLET}`, a `\R` in a comment, `assert (x, "m")` and `x is 1`. Refused with the escape refusal: `"C:\Users\x\AppData\Roaming"` ("holds `\U` ... `r"C:\Users\x\AppData\Roaming"`"), `\R`, `b"`, `f"`, `"""`, and a two-line literal with line 4 named right. Refused as "not Python": prose and `\N{NOPE NOPE}`, as before. No right body is refused. Finding 3 is the one changed refusal.
2. Held by finding 2. The record's forms store one backslash on both paths. A form with `\n`, `\t` or another decoded letter does not.
3. Held by finding 1. The record's note gives `r"C:/AppData\Roaming"`, keeps the `E` line and `tests/test_shorten.py`, and drops `Did you mean`. The circular import note has no change. An import or attribute typo gets the escape advice.
4. Stands. The s147 quote, two backslashes against a row with one, passes. The off-row quote is refused, and the refusal names both readings. A quote with two backslashes against a row with two passes as written. Four against two also passes.
5. The criterion half compares `[q] + _seat_forms(q)`. `_seat_forms` reads only `\'` and `\"`, and `_span_of` decodes only `\n`, `\t`, `\"` and `\'`. So the criterion half reads `\\` as two backslashes. The halves now disagree on one quote of a text with one backslash. Recommend: give the criterion half `_one_backslash` in this frame, as pass 2, with one test. Both rows reach the seat through the same JSON view, and line 215 of the record says that the halves read one rule.
6. Stands. The `module` case still proves the note after the commit of the Developer, the hedge word for word, and the re-encode to version 2. The `SyntaxError` kind of that proof now has no live pytest run. Finding 5 holds the residue.
7. No recorded prompt in `D:/repos/rota/tests/rota/cassettes.db` holds "invalid escape", "errors when pytest collects" or the new texts. "the body is not Python" reaches prompts of 8 cases: ACT-TS-five-criteria-one-per-reply, ACT-TS-give-the-prompt-a-stream, L1-TS-a-criterion-no-machine-could-check-is-vision_keepers, L1-TS-apply-a-term-and-write-the-test, L1-TS-assert-the-value-the-surface-returns, L1-TS-encode-a-criterion-the-principal-corrected, L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner, L1-TS-send-a-test-written-into-the-reply-as-tests-encode. A recorded `tests.encode` completion with a backslash before a letter that is not an escape is in L1-TS-send-a-test-written-into-the-reply-as-tests-encode and L1-TS-pass-a-literal-value-for-a-name-looked-up-at-run-time. These two are the likeliest stale cases. "Did you mean" is only in L1-LI-a-question-about-the-page-is-answered-not-ruled, and that text is not a collection note.
8. No CR byte in the four files before or after. No `print` and no bare `except` in the diff. `_one_backslash` repeats the `.replace` at `sandbox.py` 2384 and `api.py` 17472, but no helper with that job exists. The new tests use `pytest.raises(Exception)`, which is loose. The new texts follow STE. The note keeps the pair of a backtick, a full stop and a backtick before the next full stop, as the pass report says.

## (c2) The probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ac089aa1-c627-4128-af45-c49f490f4a93/scratchpad/r335/`.

- `test_probe_p1.py`: `tests.encode` through the `db` fixture of frame 328 with a fake run, on 21 bodies. It printed each reply or refusal.
- `probe_p2.py`: `parse_args` and `_parse_args_lenient` on six raw forms, with one and three outer quote marks. It printed each stored body.
- `test_probe_p34.py`: `_note_collection_error` on the record's output, a circular import, an import typo, an attribute typo and a truncated `\U`. `_challenge_evidence` on six pairs of a quote and a row.
- Read-only queries on `D:/repos/rota/tests/rota/cassettes.db` for point 7.
- `pytest tests/rota/test_frame328_path_door.py tests/rota/test_frame335_escape.py`: 20 passed.

## (d) Usage

The harness gives no split into input and output tokens. Its counter fell from 15,000,000 to about 14,900,000, so the review used about 100k tokens in total. That is over the 60k cap. No sub-agent ran.

## Review 2 of 0404c4f4

Date: 2026-10-26. Commit `0404c4f4` on `b0f06d41`, read in `C:/Users/roman/rota_r335`. Probe: `test_probe_r2.py` in the probe folder above. `test_frame335_escape.py` and `test_frame328_path_door.py` give 26 passed.

**Stands: both high findings of review 1 are closed, and two low faults stay in the advice text.**

1. Stands. The `ImportError` and the `AttributeError` with `Did you mean:` now keep the text of pytest and get no escape advice. Probe `test_notes`.
2. Stands. Probe `test_advice` gave this advice:
   - `"C:\Users\x\AppData\Roaming"`: "Write the path with forward slashes: `"C:/Users/x/AppData/Roaming"`. The raw string `r"C:\Users\x\AppData\Roaming"`, with one backslash, also comes through the call unchanged."
   - `"C:\Roaming\new"`: "Write the path with forward slashes: `"C:/Roaming/new"`."
   - `"C:\Roaming\temp"`: "Write the path with forward slashes: `"C:/Roaming/temp"`."
   - The record's line gives both forms. A regex `"\d+\.\w"` gets the raw form `r"\d+\.\w"` only.
   - `_call_keeps` refused `r"C:\Users\new"`, so the advice drops that raw form.
3. Only the forward-slash form for `C:\Users\new`. The doubled, the quadrupled, the `\x5c` and the raw forms all fail `_call_keeps`. Two forms come through both paths with a real backslash in the value: `"C:" + chr(92) + "Users" + chr(92) + "new"` and `str(PureWindowsPath("C:/Users/new"))`. Probe `test_keeps` gave `True` for both. Low. Fix: when no raw form comes through, name the `chr(92)` form after the forward-slash form, for a criterion about a backslash.
4. A fault, low, worth one line now. `"\777"` gets "Write it with forward slashes: `"/777"`", and that text gives a wrong value. The same branch serves any string that is not a path. Fix: when the string is not a path and no raw form comes through, say "write the value with no backslash" and name no form.
5. Stands. Against a criterion with one backslash, the quote with `\\` passes both halves, and a quote off the row with `\\` is refused. Probe `test_crit_half`. The criterion refusal does not name the `\\` reading, as open question 3 of the pass says.
6. One new fault, low, CONFIRMED. `_PATH_TEXT` reads `"\R"` alone as a path. Probe `test_advice[sep_R]` gave "Write the path with forward slashes: `"/R"`" first, which changes the value. Fix: ask `_PATH_TEXT` for two names or a drive before it reads a string as a path. Low, PLAUSIBLE: `api.py` 17487 is the first import of `rota.llm` by `rota/roles/api.py`, and it is local to avoid a cycle. No CR byte, no `print` and no bare `except` in the diff. The `except Exception` in `_call_keeps` carries its reason.

Open findings after review 2: med 1, the triple mark in the fallback (finding 6 of review 1, ruled out of this frame). Low 4: point 3, point 4, the `\R` path, and finding 7 of review 1.

Usage, review 2: the harness gives no split. Its counter fell from about 14,902,000 to about 14,880,000, so review 2 used about 22k tokens, and the two reviews used about 120k.
