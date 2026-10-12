# Frame 215, review 1b of 3a3cd94f

Reviewer: read-only agent on Opus, worktree `C:/Users/roman/rota_rv215b` at
3a3cd94f, 2026-10-12. Verdict: the pass stands. Highs: 0. Lows: 2.

## (a) Verdicts on the points

1. Finding 1 is fixed. Case e2 is refused, and a new callable in an expected file still passes.
2. Finding 2 is fixed. Both p3 shapes route to the Terminologist, and a loading module keeps the old hint word for word.
3. Findings 3 and 4 are fixed. The cache key misses one case: a dependency that `ensure_env` installs at a deferred batch's resume (finding 1 below, low).
4. Finding 6 is fixed. An abandoned batch neither admits nor names a surface, and its only ticket passes as a ticket in no batch.
5. All five new tests are red at 0353d1b9 and green at 3a3cd94f. The surface tests seed night 142's rows, except the item's statement.
6. The diff moves no brief and no op docstring. No case file holds a changed refusal text. Stale cases: none found.

## (b) Findings

1. `rota/roles/api.py:11542-11550`, `_module_load_error`. Severity low. CONFIRMED for the mechanism, PLAUSIBLE for a night.
   The key is worktree, batch head, module and the module file's stamp. It holds no fact about the interpreter's packages.
   Probe q2: `pkg.late` imports `rota_late_dep`. The first call refused. The probe then made `rota_late_dep` importable with no commit and no edit of `pkg/late.py`.
   The second call still returned "ModuleNotFoundError: No module named 'rota_late_dep'" in 0.00 s. After `_LOAD_CACHE.clear()` it returned None.
   The sandbox installs packages only in `provision.ensure_env`, called from `lifecycle.start` (`rota/core/lifecycle.py:120`).
   `lifecycle.start` runs at a batch's start and at the resume of a deferred batch (`rota/core/scheduler.py:462`). A resume keeps `head_commit`.
   The runner builds sandboxes in the same process (`rota/core/runner.py:30`), so the cache lives for the whole night.
   So a night meets the case when a commit adds a dependency to the manifest, the Tester is refused, the batch defers, and the resume installs the dependency.
   The fence lets a manifest write through only when a criterion names a dependency (`rota/core/fence.py:125-142`). So the path is narrow.
   Fix: clear `_LOAD_CACHE` for the worktree in `lifecycle.start` after `ensure_env`, or add the venv's site-packages stamp to the key.

2. `tests/rota/test_criteria_surface.py`, `_night142`. Severity low. CONFIRMED.
   Night 142 links item `show_python_version_flag` to statement `s4`. The seed writes no statement and no `refs` row.
   So no test covers the statement source of the door's words, which is one of the three sources finding 1 named.
   Probe q1 case e5 shows that the source works: a statement that names `process_commands` admits the surface.
   Fix: seed `s4` and its `refs` row in `_night142`, and add one case where only the statement names the callable.

Outside the points: none above low.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/5083f684-6864-4cc2-ae65-244a1c2c8966/scratchpad/rv215b/`.
They import the worktree's code through `sys.path`, and each copies `rv215/n142.db` before it writes.

- `q1.py`, points 1 and 4. Output, observed 2026-10-12:
  - a s536 imagepipe: REFUSED, "No word of the request or the ticket names process_commands".
  - b no batch: PASS. c new callable in `src/click/decorators.py`: PASS. c2 `tests/test_basic.py`: PASS.
  - e word of the request (`version`): PASS. e2 the name in the seat's text only: REFUSED.
  - e4 the ticket text names it: PASS. e5 statement `s4` names it: PASS.
  - g abandoned `echo_json_batch` holds imagepipe as expected: REFUSED. The refusal names only `src/click/decorators.py, tests/test_basic.py`.
  - g2 a file only the abandoned batch names: REFUSED with the same two files.
  - h a ticket whose only batch is abandoned: PASS, as a ticket in no batch.
- `test_p3b.py`, point 2, run by pytest from the worktree root, 4 passed:
  - Both shapes with a broken module: "examples.imagepipe.imagepipe does not load in the sandbox ... Send msg.question_terminologist(...)".
  - Both shapes with a module that loads: the old texts, "Import the surface from its own module: `from examples.imagepipe.imagepipe import process_commands`" and "It is defined in examples.imagepipe.imagepipe: `from ...`".
  - The diff adds lines only before the two old `raise` statements, so the old texts are the same word for word.
- `q2.py`, point 3:
  - `pkg.uni` returns "RuntimeError: caf" plus the ascii escapes of the two characters, in 0.05 s. The load reads as failed.
  - `pkg.slowfail` (sleep 5 s, then a missing import): 5.05 s, then 0.00 s with the same text.
  - `pkg.asks` (top-level `input()`): "EOFError: EOF when reading a line" in 0.05 s.
  - `pkg.late`: the stale result in finding 1.
- `old/`, point 5: `git archive 0353d1b9` of `rota`, `tests` and `pyproject.toml`, with the two test files from 3a3cd94f.
  The import resolved to `old/rota/roles/api.py`, which has no `_LOAD_CACHE`.
  Run: 5 failed, 46 passed. The five failures are exactly the five new tests.
  At 3a3cd94f the two test files gave 353 passed in 33.90 s.
- Point 6: a search of `tests/rota/cases` for the changed and the new refusal texts found no file.
  The gate's stale line, "stale (0): none", comes from the implementer's report. This review did not run the gate.

## (d) Usage

The reviewer cannot read the harness line. Estimate: about 36k input tokens, about 8k output tokens, about 44k total, inside the 50k cap.
Take the real figures from the harness line.
