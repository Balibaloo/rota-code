# Frame 215, pass 1: diff review of f3de0534

Reviewer: read-only, Opus. Worktree `C:/Users/roman/rota_rv215` at f3de0534.
Date: 2026-10-12. The review is meta workflow. The seats are rota workflow.
Verdict: the pass stands with one high finding. The high finding has a one-line fix.
Counts: 1 high, 6 low.

## (a) Verdicts on the numbered points

1. The respecify door refuses the shape of s536 and names the expected files. The door reads the new criterion text as request words, so the seat can pass it by writing the callable name in its text (finding 1, high).
2. `_module_load_error` runs the worktree interpreter in the worktree, as the harness does, but without pytest, conftest or the plugin environment. It costs 0.04 s to 0.13 s for each refusal, and it fails open on a slow module or a non-cp1252 error (findings 3 and 4, low).
3. All three Tester modes that hold `tests.encode` list `msg.question_terminologist`. The offered call lands in the fixture. The quoted question is a fixed text, so no quote can break it.
4. The Tester sessions s537 to s562 of night 142 reached neither uncovered door. The second part of the ends-when is met on the shape of night 142. Both doors still force the import on a plausible shape (finding 2, low).
5. The sentence has exactly 25 words and no imperative. The sentence agrees with the door, but the door is wider, and the seat cannot read the files of the batch (finding 5, low).
6. All three new tests are red at f906f218 and green at f3de0534. The door-1 test uses the rows of night 142. The door-2 test uses the s542 body from the turn record on a generic fixture. The brief test pins the words and not the line breaks.
7. The stale set from the brief: `L1-TE-a-ruled-criterion-is-respecified-and-the-tester-told` and `L1-TE-repair-the-criterion-the-tester-cannot-encode`. Five recorded cases reach the two encode doors (listed below).

Point 7, the cases whose recorded transcripts hold the text of the surface door or the NameError door (qwen3:8b, `case_runs.transcript`):

- `ACT-TS-three-criteria-one-per-reply` (5 runs)
- `L1-TS-an-outside-fact-is-the-researchers` (15 runs)
- `L1-TS-apply-a-term-and-write-the-test` (1937 runs)
- `L1-TS-encode-a-criterion-the-principal-corrected` (415 runs)
- `L1-TS-hold-a-test-that-is-right` (5 runs)

These five change only when the surface module of the fixture exists and does not load. Neither repair-mode case has `batch_touch` rows, so the new door passes both. Their change is the prompt key alone.

## (b) Findings

1. `rota/roles/api.py:4808-4809` (the call) and `api.py:4428` (`words_from = list(texts)`). Severity high. CONFIRMED. The door takes its words from the new text that the seat sends. Probe p1, case e2: `process_commands` in the new text makes `examples/imagepipe/imagepipe.py::process_commands` PASS on the rows of night 142. The refusal says "No word of the request or the criterion names process_commands", so the refusal itself shows the seat the way past it. The old text of the criterion is also seat-written. Fix: take words from the item, its statements and the ticket text only, and drop `text` and `cur["text"]` from `texts`.
2. `rota/roles/api.py:6751` (the "no module of that name" hint) and `api.py:6866` ("It is defined in"). Severity low. CONFIRMED for the mechanism, PLAUSIBLE for a night. Probe p3: `from imagepipe import process_commands` gets "Import the surface from its own module: `from examples.imagepipe.imagepipe import process_commands`". `from src.click.decorators import process_commands` gets "It is defined in examples.imagepipe.imagepipe". Both refusals offer an import that does not load. Night 142 met neither refusal: zero hits in the turns of s537 to s562. Fix: call `_module_load_error` before each of the two hints, and use `_unloadable_surface` when it reports an error.
3. `rota/roles/api.py:11487-11504` (`_module_load_error`). Severity low. CONFIRMED. A non-cp1252 character in the error text makes the `print` of the child fail after it writes three fields. The parent then returns an empty string, which is falsy, so the doors offer the import again. Probe p2: `pkg.uni`, which raises `RuntimeError` with a non-cp1252 character, returned the empty string. A non-cp1252 module name leaves fewer than four fields, and the unpack then raises `ValueError` out of the door (PLAUSIBLE, from the code). Fix: print the message and the name through `ascii()`, or pass `PYTHONIOENCODING=utf-8`, and return `first or kind`.
4. `rota/roles/api.py:11494`. Severity low. CONFIRMED for the time cost, PLAUSIBLE for the rest. The probe runs again on every refusal, with no cache. Probe p2: a module that sleeps 5 s costs 5.04 s on each call. A top level past 60 s times out, and the doors then offer the import. The child inherits the stdin of the harness, so a top-level `input()` blocks until the timeout. The probe reads no `conftest.py`, no pytest `pythonpath` and no `plugin_env()`. Probe p2: a root `conftest.py` stubs `PIL`, and `pkg.pil` still reads as broken, but pytest would load it. Fix: pass `stdin=DEVNULL`, cache the result per worktree head and module, and state the pytest difference in the docstring.
5. `rota/roles/prompts/terminologist/criterion_repair.md:11-13`. Severity low. CONFIRMED from the tools file. The sentence asks for "a file the batch expects to touch", but `criterion_repair.tools` has no `batches.expect`, and the pre-run shows no touch rows. The seat learns the files only from the refusal. The door also accepts a `possible` path row, a symbol-row name and a file stem of the request, which the sentence does not say. Fix: add the expected files of the batch to the pre-run in a later frame, and keep the sentence.
6. `rota/roles/api.py:4421-4425`. Severity low. CONFIRMED for the mechanism, PLAUSIBLE for a night. The door joins the touch rows of every batch that holds the ticket, abandoned batches included. Probe p1, case g: tk_2 also placed in the abandoned `batch_2` admits `imagepipe.py` through a row of batch_2. Case g2 names `tests/test_options.py` of batch_2 in the refusal. The union never refuses a surface that the live batch expects. On night 142 each ticket sits in one batch only. Fix: skip abandoned batches in the query, with the same status filter that `batches_expect` uses.
7. Outside the points. `rota/roles/api.py:4380-4402` (`_vet_surface`, not in this diff). Severity low. CONFIRMED from the code. At repair, `_vet_surface` already refuses a callable that does not exist and that the item or ticket does not name. So the brief line "If the right callable does not exist yet, name it the way you intend it" is false in criterion repair, whatever the new door does. The new door itself admits a new name in an expected file (probe p1, case c, PASS). Fix: a separate frame aligns the brief sentence with `_vet_surface`.

Also outside, no finding: the pre-repair criterion text in the door-1 test, "The --version output names the Python version.", is not the text of night 142. The database holds only the text after s536.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/5083f684-6864-4cc2-ae65-244a1c2c8966/scratchpad/rv215/`.

- `n142.db`, `p1.db`: copies of `.rota/clickI_night142.db`. `q1.py` and `q2.py` read the batches and touch rows of tk_2. tk_2 is in `batch_3` only.
- `q3.py`: counts the refusal texts in the turns of the Tester sessions s537 to s562. "no module of that name" 0, "It is defined in" 0, the surface door in 13 turns, the NameError door in 9 turns.
- `p1.py`: calls `_surface_outside_batch` on the rows of night 142 for cases a to g2. a REFUSED. b, c, c2, d, e and e2 PASS. e3 REFUSED. g PASS. g2 REFUSED with the files of batch_2.
- `p1b.py`: all 830 indexed callables outside the two expected files, on the words of night 142. 829 refused, 1 passed (`src/click/termui.py::confirm`, through the word "confirm").
- `p2.py`: `_module_load_error` on the live batch_3 worktree. imagepipe gives "ModuleNotFoundError: No module named PIL" in 0.12 s. `click.decorators` and `src.click.decorators` give None. Synthetic worktree `wt/`: slow None at 5.04 s, `os._exit(0)` None, non-cp1252 the empty string, missing helper and stubbed PIL both report an error.
- `test_p3_route.py`: pytest with `-p tests.rota.conftest` on the desk fixture. The two uncovered doors still offer the imagepipe import. The refusal of the NameError door routes to `msg.question_terminologist`, and the offered call lands as `m1`. Result: 3 passed.
- `old/`: `git archive f906f218` of `rota` and `tests`, with the three new test files copied in. Result: 3 failed: DID NOT RAISE, "Import the surface from its own module" present, and the sentence absent.
- Touched files at f3de0534: `test_desk_guards.py`, `test_criteria_surface.py`, `test_prompts.py`. Result: 376 passed in 33.30 s.
- Cassette read: `tests/rota/cassettes.db` opened with `mode=ro&immutable=1`. A LIKE scan of `case_runs.transcript` for the two door texts gave the five cases in point 7.
- The gate did not run. Point 7 names the set, and the gate of the holding session gives the stale line.

## (d) Usage

The estimate of the reviewer: about 95k input tokens, 12k output tokens, about 107k in total. Take the figure from the harness line. Sub-agents: none.
