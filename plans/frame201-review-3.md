# Frame 201, review 3 of a3a84d06

Verdict: accept. Pass 2b closes review 2's findings 1, 2, 4 and 5 on their own cases. On the 20 stored batches, 4 of 1021 added lines change kind, and all 4 are right. One medium finding: the class-wide hunk lets an earlier method spoil a later method's docstring, on two shapes that the parent read right. Click at `main` holds neither shape. The worktree is `C:/Users/roman/rota_r201` at a3a84d06. I edited no tracked file.

## (a) The claim and the verdict on each point

The claim: rota's own diff driver opens a `-W` hunk at a column-0 `def`, `async def` or `class` only. The attributes file is written with `mkstemp` and `os.replace`, and a failed write gives `-W` with no driver. A header goes on while its brackets are open. Two held lines or more get a sentence for several lines.

1. All four closed. `tests/rota/test_verdict_lines.py` gives 80 passed. Each of the four new tests asserts on its own case: the hunk of `make_pass_decorator`, the `a, b` header, the missing temp directory, and the e1 pin with three lines.
2. The plain case is right, two shapes are not. A string `x = """ ... """` in the first method leaves the second method's docstring line right (A1). A `'"""'` in the first method (A2) or a one-line header `def a(self, x='#'):` (A3) gives the docstring line None. The parent gives a docstring line on both (finding 1). A column-0 example `def` in a module docstring opens the hunk inside the docstring, as in the parent (finding 3).
3. The new rule gives no wrong kind on an open `def f(`. Kinds come from the line shape, and the `@@` line resets the header. The new rule continues every header that the old rule continued, so it loses a right kind only where the bracket count is wrong. A `#` in a string makes `_code_part` cut the header, and the header then takes in each later `def` of the hunk (A3, finding 1).
4. 4 of 1021 lines change kind, all in night 155 `bg_5`, and all 4 are right. They are the docstring of `echo_json`, whose header wraps with no trailing comma: None to a docstring line. Three batches merge one hunk each (9 to 8, 8 to 7, 2 to 1).

## (b) Findings

### High

None.

### Medium

**1. An earlier method in the class-wide hunk spoils a later method's docstring.** `rota/core/worktrees.py:358` and `rota/roles/api.py:11505-11509`. CONFIRMED by probe p23. A method change now gives a hunk from the class line, so the walk reads every earlier method. Two shapes then give a later docstring line None, where 09dbbb60 gave a docstring line:
- A2: `SEP = '"""'` in the first method. The fence count is odd, so the walk opens a string that is not a docstring.
- A3: `def a(self, x='#'):` on one line. `_code_part` cuts at the `#`, the header has one open bracket, and `def b` joins that header.

The miss is the safe way round: the door admits the line, as in review 2's finding 1. Click at `main` has no line of either shape (probe p2walk: 0 code lines read as docstring lines). Fix: reset `in_header`, `expect_doc` and `in_str` at each line that starts with `def `, `async def ` or `class ` at the hunk's class indent or deeper while no docstring is open, or strip strings before the fence and bracket counts.

### Low

**2. Outside. A `#` in a default value hides a docstring.** `rota/roles/api.py:11428-11432`. CONFIRMED by probe p2walk. `progressbar` in click's `termui.py` has `fill_char: str = "#",`. The joined header does not parse, so all 101 missed docstring lines of click are that docstring. The parent misses them too, so this is not a regression. Fix: find the comment with `tokenize`, not with `split("#")`.

**3. A column-0 example `def` in a module docstring opens a hunk.** `rota/core/worktrees.py:358`. CONFIRMED by probe p23, B1 and B2. The walk reads the example as a header. Prose `pass` and `import os` inside the module docstring get "`pass`" and "a plain import" (B2). A real `import os` after the docstring gets None (B1). The parent gives the same kinds. Fix: none needed now. Note it in the docstring of `_added_kinds`.

**4. Outside. Old and new code share one attributes path with two contents.** `rota/core/worktrees.py:372`. PLAUSIBLE: 09dbbb60 writes `*.py diff=python` and a3a84d06 writes `*.py diff=rota` to `rota-diff-python.gitattributes`. A process on each version rewrites the file in turn, and a race gives git's indented Python driver. Fix: name the file after its driver, for example `rota-diff-rota.gitattributes`.

## (c) Probes

All probe files are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/81fe1025-ee88-45f4-8210-744972761835/scratchpad/r3/`. Each ran from the worktree root with `D:/repos/rota/.venv/Scripts/python.exe`. `old/` holds `git archive 09dbbb60 rota`.

- `pytest tests/rota/test_verdict_lines.py -q`: 80 passed.
- `p4kinds.py` writes `old.json` and `new.json`. Each holds the `-W` diff and the kinds of the 20 batches under one tree's driver and walk. `p4cmp.py` compares the two files, and checks the added lines against the plain diff. The output is in `p4.out`.
- `p2walk.py` walks each column-0 block of `src/click` at `main` as one hunk, and compares the docstring kinds with `ast`. Under a3a84d06: 9781 lines, 101 missed, 0 extra. Under 09dbbb60: 451 missed, 0 extra.
- `p23.py` builds five small repositories under `repos/` and prints the hunk and the kinds under each tree: A1, A2, A3, B1 and B2.
- `p3.py` runs `_added_kinds` under each tree on three hand diffs: an open `def f(` before a second hunk, an open `def f(` before body lines, and a `)` in a string.

## (d) Usage

Input: about 350k tokens summed over the turns, with about 50k of context at the end. Output: about 12k tokens. Total: about 360k. These numbers are estimates, because I have no meter.
