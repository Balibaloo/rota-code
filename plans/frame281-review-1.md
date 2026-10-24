# Frame 281, review 1 of 1a4ff6e9

Verdict: accept with one fix. The brief text states the ruling and names no product, parameter or error text. One other case still accepts an installed package name.

Worktree: C:/Users/roman/rota_r281 at 1a4ff6e9, base e330b7c1.

## (a) Verdict per point

1. Pass. The new sentences state the ruling and name no product, parameter or error text. One weak cross-reference (finding 3).
2. Pass. The frame 200 pin still holds the sentence on the test the row names, and the sentence is unchanged.
3. Partial. The comment states the ruling with the date and time. The case L1-TS-act-on-the-reason-of-a-challenge still accepts any `package_name=` value (finding 1).
4. Pass. test_prompts 34 passed. test_frame193_pass3 26 passed. test_principal_reply 12 passed. test_l1 158 skipped.

Point 1, the new sentences, quoted.

- base.md: "A test sets every input of its call that the criterion leaves open, with a value of its own, and logs the choice."
- base.md: "A value the test finds on the machine, such as an installed package, the clock or an environment variable, is not set by the test."
- base.md: "Where the criterion names a kind of value and not the value, the test asserts the kind, as a pattern, and not a literal the criterion does not give."
- challenge.md: "When the failure names an input the call did not set, set that input with a value you choose, and log the choice."
- challenge.md: "Do not take a name the error suggests, and do not take a name you find installed."
- challenge.md: "The paragraph on open inputs above gives the rule."
- challenge.md: "...because the row outranks the traceback for where an argument goes." The words "the criterion's wording and" are gone.
- challenge.md: "A claim in the row that an argument is required is the Developer's reading."
- challenge.md: "The criterion and the paragraph on open inputs decide which input the test sets, and with what value."
- tests_missing.md: "Set every input of that call that the criterion leaves open with a value you choose, and log the choice."
- tests_missing.md: "Do not take a name you find installed, as the paragraph on open inputs above says."

No sentence names click, `package_name`, `version_option` or the RuntimeError text. "installed package", "the clock" and "an environment variable" are generic kinds. No new sentence contradicts another sentence of the same composed brief. The tests_missing line "An unsourced literal is an assumption logged `invented`" agrees with "log the choice".

## (b) Findings

1. tests/rota/cases/l1_tester.yaml lines 703 to 714, case L1-TS-act-on-the-reason-of-a-challenge. Severity high. CONFIRMED: text_includes_any holds "version_option(package_name=" and "show_python=True, package_name=". The exclude refuses only the invoke form. A body with `package_name` set to an installed name passes this case. The comment defers the value to "its own frame". Frame 281 is that frame, and the ruling now refuses that value. Fix: drop the two `package_name=` forms, or add the installed names and the module name to text_excludes.
2. tests/rota/cases/l1_tester.yaml, case L1-TS-pass-a-literal-value-for-a-name-looked-up-at-run-time. Severity low. PLAUSIBLE: the ruling also says the test checks a generic version number in the output. The expectation checks only the decorator form, not the assertion form. A body that asserts a literal the criterion does not give still passes. Fix: add a check on the assert line, or record that the case measures the input clause only.
3. rota/roles/prompts/tester/challenge.md line 7 and tests_missing.md line 46. Severity low. PLAUSIBLE: both point to "the paragraph on open inputs above". The base paragraph never uses the words "open inputs". It says "every input of its call that the criterion leaves open". A small model may not find the referent. Fix: use the same words in the pointer as in the base, for example "the paragraph on inputs the criterion leaves open".
4. Outside the points. tests/rota/test_l1.py line 124. Severity low. CONFIRMED: both changed cases skip with "no cassettes recorded" under qwen3:8b. The suite does not measure the new expectations. Pass 1b moved 0 of 8, so only a live night shows the effect. Fix: none in this commit. The night of section 4 of plans/frame281-history.md is the measure.

## (c) Probes

1. git diff e330b7c1 1a4ff6e9 on the three briefs, the cases and test_prompts.py, in the worktree.
2. A python -c call that composed the tester brief for challenge, tests_missing and answer, and printed lines with install, literal, version, package or value.
3. grep for package_name in tests/rota/cases/. It found the case of finding 1.
4. pytest with ROTA_MODEL=qwen3:8b on test_prompts, test_frame193_pass3, test_principal_reply and test_l1. Then test_l1 with -rs on the literal-value case for the skip reason.

## (d) Usage

Input tokens about 30k. Output tokens about 4k. Total about 34k.
