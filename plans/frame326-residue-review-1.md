Verdict: 9492a40b stands for the branch. Findings: 1 med, 3 low.

# Frame 326 residue, review 1 of 9492a40b

**Verdict: stands for the branch.** The two halves of the fix are correct, and no other door changed. One finding is med: no committed test pins the base read. Three findings are low, and two of them are outside the points and older than the commit.

The worktree is `C:/Users/roman/rota_r326r` at 9492a40b. No model ran. No case under `tests/rota/cases/` ran. No tracked file changed.

## The points

1. **The base read. CONFIRMED.** The guard calls `_base_text(ctx, _root, wpath.replace(...))` at `rota/roles/api.py:18911`. The fence calls the same helper with the same arguments at line 18967. A path new in the batch gives "", and the `if _base_defs:` test skips it. A base that git cannot read gives None, and the test skips it too. `_base_text` catches `OSError`, `sqlite3.Error` and `WorktreeError`, and it decodes with "replace". A base that does not parse raises `SyntaxError`, and the guard catches it. On Python 3.14.2 a null byte also raises `SyntaxError` (probe c6). Test 4 covers the base that does not parse. Test 3 covers a path new in the batch.
2. **The language filter. CONFIRMED.** Line 18931 compares the suffix of the file of the index row with `_splitext(path)[1]`. The filter does not name `.py`. The guard sits inside `if path.endswith(".py"):` at line 18714, so the suffix is `.py` in every case today. Test 3 refuses a new `src/notify/text.py::truncate` beside `src/notify/formatting.py::truncate`, and it is green at 9492a40b.
3. **Deviation 1. CONFIRMED.** At 3aac03c4 with the new test file, the file gives `3 failed, 13 passed` (probe c1). Test 3 fails with `DID NOT RAISE`. Tests 1 and 2 fail with the gate's text, "the tree already defines truncate in web/format.js". The "once" condition now counts the distinct files, other than `path` and not test paths, that hold the name. The files come from index rows with the same suffix as `path`, and from the `.py` files of the worktree through `_defined_in_tree`. The guard refuses when that count is 1 and no criterion names `path`. A name in `had_before`, now the working file and the base file, is not counted.
4. **The tests. CONFIRMED.** `_SAMPLE_SYMBOLS` puts `web/format.js::truncate` and `web/format.js::money` in `code_index`. Test 1 drops `truncate` with a partial `code.write` and writes `samplerepo.FILES[path]` back whole. At 3aac03c4 the second write fails with the gate's text, and at 9492a40b it passes. Test 2 drops `money` on disk, as deviation 2 says. The tests use `rota.core.sandbox.build` and call no model. The file has no `llm`, `ollama` or `model` reference.
5. **The blast radius. CONFIRMED.** `had_before` has readers only in the guard, at lines 18899 to 18922. `_base_text` has five callers, and the guard is the only new one. The other four are the fence, `_base_held`, `_unnamed_def_strays` and `_changed_unnamed_defs`, and the commit does not touch them. The diff changes only `rota/roles/api.py` (15 lines added) and the test file. The five files give `2 failed, 192 passed`. The two reds are also red at 3aac03c4 (probe c3).
6. **The red outside the pass. CONFIRMED.** `test_a_session_with_no_batch_reads_the_root` is red at 3aac03c4 in a `git archive` tree. A bisect on `git archive` trees finds the first red at b00aaa59 (2026-10-11, "a seat names the kind of its note at the door, and faults go to an operator table"). The commit before it in the path list, 3f2e974e, is green. The first `_encode` at test line 381 no longer raises. The commit body says "The literal door stages its own `invented` row and refuses no encode". That sentence is the probable cause. The review did not trace it.
7. **The refusal text. CONFIRMED, with one false clause that is older than the commit.** The text is the same as before. "The tree already defines {name} in {file}" is true for a worktree hit. For an index hit it can be false (finding 3). "A name the project has once" is now true within one language. "The tests and the callers reach the first one" is true for a Python caller and a Python file. The new filter makes that clause more accurate than before.

## Findings

1. **Med. `tests/rota/test_touch_divergence.py:265` to 311. No committed test pins the base read. CONFIRMED.** A plugin made `_base_text` return None everywhere, and the file gave `16 passed`. A control plugin that raised from `_base_text` gave `11 failed`, so the plugin reached the workers. The suffix filter alone makes tests 1 and 2 green. A probe test needs the base read. In it, the base of `src/notify/legacy.py` defines `render`, and `src/notify/templates.py` also defines `render`. The batch empties `legacy.py`, and a whole-file write puts the base text back. The write passes at 9492a40b. Without the base read it fails with "already defines render in src/notify/templates.py". Fix: add that probe as a fifth test.
2. **Low, outside. `tests/rota/test_fixtures.py:63`. `test_no_case_leaves_a_reference_unwrapped` is red at 3aac03c4 and at 9492a40b. CONFIRMED.** It lists bare items in `l1_liaison2.yaml`, lines 336 to 451 and more. The pass report does not name it, because the implementer did not run that file. Fix: check the red against the gate baseline, and give it a frame if the baseline does not hold it.
3. **Low, outside, older than the commit. `rota/roles/api.py:18924` to 18949. The guard refuses a move to a new module, and its text names a file that no longer holds the name. CONFIRMED.** A probe dropped `truncate` from `src/notify/formatting.py` on disk and wrote `truncate` to a new `src/notify/text.py`. The refusal said "the tree already defines truncate in src/notify/formatting.py". The index row comes from onboarding, and the worktree file no longer defines the name. Fix: drop an index hit whose worktree file no longer defines the name.
4. **Low. `rota/roles/api.py:18911` and 18967. Every `.py` write now calls `_base_text` twice. CONFIRMED.** The map lists both calls in `_code_write`. Each call runs `_batch_base` and two git commands. Fix: read the base once above the guard, and give the text to the guard and to the fence.

## The probes

All probe files are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ad481e08-d0cc-4317-a992-02d5208ea7e8/scratchpad/`.

- c1, `r326_head/`: a `git archive` of 3aac03c4 with the test file of 9492a40b. It ran `test_touch_divergence.py`: `3 failed, 13 passed`. `import rota` resolved inside the extract.
- c2, `r326_plug/r326_nobase.py` and `r326_plug/r326_boom.py`: plugins loaded with `-p`. `r326_nobase` gave `16 passed` in the worktree. `r326_boom` gave `11 failed, 5 passed`.
- c3, `r326_head/`: the two reds of point 5 at 3aac03c4: `2 failed`.
- c4, `r326_new/tests/rota/test_r326_probe.py`: a `git archive` of 9492a40b with two probe tests. `test_probe_write_back_beside_a_python_twin` passes, and it fails under `r326_nobase`. `test_probe_move_to_a_new_module` fails with the text in finding 3.
- c5, `r326_bis/run.sh`: a bisect on `git archive` trees with `-n0`. 6c83f6c0 is green and 0d0f4771 is red. The first red is b00aaa59, and 3f2e974e is green.
- c6: `ast.parse(chr(0))` on Python 3.14.2 raises `SyntaxError`.

## The test counts

| Run | Tree | Result |
|---|---|---|
| `test_touch_divergence.py` | 3aac03c4 code, new tests | 3 failed, 13 passed |
| `test_touch_divergence.py`, base read off | 9492a40b | 16 passed |
| the five files of point 5 | 9492a40b | 2 failed, 192 passed |
| the two reds | 3aac03c4 | 2 failed |
| the invoke red | 6c83f6c0, 3f2e974e, b00aaa59 | green, green, red |

## Usage

The harness reports no split of input and output tokens to this agent. Its remaining-token count fell by about 66k during the review, input and output together. The brief's cap was about 40k. The bisect of point 6 used most of the excess.
