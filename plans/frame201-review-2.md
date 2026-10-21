# Frame 201, review 2 of 09dbbb60

Verdict: accept. The pass closes finding 1 of review 1 on the shape of night 157, and it closes finding 2. Two medium findings leave the same class of defect open on other shapes of real click code. Neither finding is a regression against the parent f6050421. The worktree is `C:/Users/roman/rota_r201` at 09dbbb60. I edited no tracked file.

## (a) The claim and the verdict on each point

The claim: `verdicts.emit` gives `_added_kinds` a `git diff -W` of the batch, with git's Python driver from an attributes file outside every repository. The block refusal names the held code lines of the seat first. The `[diff]` block and `code.read` keep the plain diff. I read the claim as true. `_batch_diff` has two callers, and only `_pass_lines_check` passes `function_context=True`.

1. Closed. On the fixture and on the real head 87156816 of night 157, the plain hunk is `@@ -461,6 +462,9 @@`. The s324 call gets the docstring text, and one docstring line gets the no-behaviour refusal (probes p1, p1b).
2. Same lines. On 20 batches, the raw `+` lines of the two diffs are equal, in the same order, and 1021 in all. `-W` merges 127 hunks into 74, and it changes no added line (probe p2).
3. Right. 64 lines go from None to a docstring line, 10 from a blank line to a docstring line, 2 from None to a plain import, and 2 from None to a blank line. Ten lines read by hand are all `:param` prose, `.. versionadded::` lines or blank lines inside a docstring. No line reads as a docstring line or a plain import that is neither. The two `import sys` lines of night 152 sit in the body of `confirm`, after the closing fence, so the plain import is right. The door now refuses a pass that names one of them alone, with the no-behaviour text, where the parent admitted it.
4. Mostly sound, findings 1, 3 and 4. The file is `<tempdir>/rota-diff-python.gitattributes`, one file for every process. A path with a space and a non-ASCII character survives. A repository `.gitattributes` with `*.py diff=custom` overrides the driver, and git then uses its default funcname. `*.py -diff` makes both diffs binary, so the two stay equal. The test does not prove the driver (finding 3).
5. Sound, finding 5. On probe e1 the text names the three held lines first. A part of a line names the whole added line, and a copy of that whole line lands, so the whole line is the right text. The sentence holds the 20-word cap when the quoted code is not counted. The sentence cannot name a line the diff does not hold, because `_held_code` reads only the code lines of the `-W` walk, and point 2 makes those the plain added lines.
6. Two cases go stale, finding 6. The pin changes add the new sentence and nothing else.
7. `test_no_case_leaves_a_reference_unwrapped` checks that no case file holds a bare id beside its `<id>` form. It fails on `tests/rota/cases/l1_liaison2.yaml`, which this frame does not touch, so the red is not this frame's.

## (b) Findings

### High

None.

### Medium

**1. The Python driver starts a `-W` hunk at a `def` inside a docstring.** `rota/core/worktrees.py:353-367`. CONFIRMED by probe p4. The fixture adds two `:param strict:` lines to the docstring of `make_pass_decorator` in the real `decorators.py` at 2c8cd3ac. That docstring holds the example line `def decorator(f):`, indented. With the driver, the hunk is `@@ -64,13 +64,15 @@`, it starts inside the docstring, and the two lines read as code. Without the driver, git starts the hunk at line 51, the real `def make_pass_decorator(`. Click has seven such lines in docstrings at 2c8cd3ac: five in `core.py` and two in `decorators.py`. The parent misses the same lines, so this is a hole in the fix, not a regression. Fix: give a rota driver whose funcname pattern matches `def`, `async def` and `class` at column 0 only.

**2. Outside. The walk misses a docstring after a signature that wraps without a trailing comma.** `rota/roles/api.py:11486-11493`. CONFIRMED by a direct probe and by p4. The header goes on only while a line ends in `,` or `(`. So `def f(`, then `a, b`, then `) -> int:` never sets `expect_doc`, and an added `:param a:` line reads as code. With `a, b,` the same line reads as a docstring line. In click at 2c8cd3ac, 38 of 264 definitions with a docstring have this header shape, `make_pass_decorator` among them. The fault is older than this frame, but it keeps finding 1 of review 1 open on those functions under `-W` too. Fix: let the header go on while its brackets are not balanced.

### Low

**3. The real-diff test does not prove the driver.** `tests/rota/test_verdict_lines.py:1103-1118`. CONFIRMED by probe p1. `version_option` is a top-level `def`, and git's default funcname matches it. With no attributes file, the `-W` diff still holds ` def version_option(`, and the kinds are the same. The pass report says that this test proves the driver. Fix: add a fixture with the change in a method docstring, and assert that the hunk opens at the method.

**4. A failed write of the attributes file escapes as `OSError`.** `rota/core/worktrees.py:358-367`. CONFIRMED by probe p5: with the temp directory missing, `diff` raises `FileNotFoundError` out of `verdicts.emit`, not a `LinesRefusal`. A race is PLAUSIBLE: `write_bytes` truncates and then writes, so a concurrent git can read an empty file. That race gives the default funcname, which finding 1 shows is no worse. Fix: write to a unique name and `os.replace` it, and on `OSError` run `-W` without the `-c` pair.

**5. The held-line sentence names more than one line and says "Copy that one".** `rota/roles/api.py:11649-11653`. CONFIRMED by the pinned text of e1 and by the recorded call of `L1-CR-fail-names-its-criterion`, where the sentence will name two `delete(...)` lines. The words "is the line" and "that one" point at one line, and the seat gets two or three. For a part that two added lines hold, `_held_code` names the first line only. Fix: keep the text for one held line, and for more write "The lines you sent hold these added lines: ... Copy the one that meets <cid>."

**6. Two recorded cases go stale.** CONFIRMED on `D:/repos/rota/tests/rota/cassettes.db` (probe p6). 70 `qwen3:8b` rows hold the old block text, and no row holds the new sentence. In both cases the seat sent held code lines, so the new sentence goes into the next prompt and the key misses. The cases are `L1-CR-fail-names-its-criterion`, `qwen3:8b`, runs 1 to 5, and `L1-CR-finish-the-review-with-the-answer-in-hand`, `qwen3:8b`, runs 4 and 5. Fix: re-record the two cases, as review 1 priced for the diff route.

## (c) Probes

All probe files are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/81fe1025-ee88-45f4-8210-744972761835/scratchpad/r2/`. Each ran from the worktree root with `D:/repos/rota/.venv/Scripts/python.exe`.

- The test file `tests/rota/test_verdict_lines.py`: 76 passed.
- p1.py builds the real bg_2 fixture in `fx1`. It compares the plain diff, the `-W` diff with the driver and the `-W` diff without it. The plain hunk is `-461,6 +462,9`. The two `-W` diffs give the same kinds.
- p1b.py runs on `real157`, a local clone of clickI. HEAD~1 is 2c8cd3ac and HEAD holds the tree of 87156816. The probe sends the s324 call and one docstring line through `verdicts.emit`. The door refuses both with the right texts.
- p2.py runs the count script of the pass against `rota_r201`, with a check of the raw `+` lines. The output is in p2.out: 20 batches, 127 hunks to 74, 1021 lines and 78 changes.
- p4.py builds the `make_pass_decorator` fixture in `fx4` and prints three diffs.
- p5.py tries a temp path with a space and a non-ASCII character, three repository `.gitattributes` bodies, and a missing temp directory.
- p6, inline, queries `cassettes` and `case_runs` for the block text, the list text and the new sentence. It also reads the seat calls before the refusals.
- Inline probes run `_held_code` on parts of lines and `_added_kinds` on a wrapped signature. One counts the click definitions by header shape.
- Inline, `pytest -k unwrapped` runs on `tests/rota/test_fixtures.py`.

## (d) Usage

Input: about 1.1M tokens summed over the turns, with about 95k of context at the end. Output: about 15k tokens. Total: about 1.1M. These numbers are estimates, because I have no meter.
