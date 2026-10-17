# Frame 283, review 3 of 7471569c

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_r283` at 7471569c, 2026-10-17. Meta workflow review of a rota workflow door. Verdict: does not stand. Points 1, 4 and 5 hold. Point 3 shows a regression that the suite does not render.

## (a) Verdicts on the points

1. Both highs of review 2 are fixed. `test_identity.py` passes (observed: 55 passed over three files). The key is (batch_id, path) by the schema's PRIMARY KEY and the description, but the kind is "content", and the docstring's "relation" fits a pair key better (low, label only). A whole-file note stores its module-level lines, and a comment write does not close it (observed: the new test, and probe R3d).
2. Low 3, the whole-token match, is fixed (observed: the new test). Low 4, a session that dies, is left with no reason. Low 5, rows of a merged or abandoned batch, is left with no reason. The pass report says only "stay as they are, for the record".
3. The door takes the base from `_batch_base`, the merge base of the worktree with the project root, or HEAD~1. It reads `git show <base>:<path>` and keeps a line only when the base's definition of the same qualified name holds the stripped line. A base line opens a note (probe A). A batch line opens none (the new test). A base git cannot resolve keeps every line (probe B). Indentation does not cause a miss, because the compare uses stripped lines. A line whose owner the batch renamed or nested opens no note and no reply note (probes C and F, finding 1). A base that does not parse keeps nothing (probe E, finding 3).
4. Both shapes are still refused at 7471569c. s340: `test_s340s_commit_in_the_reply_after_the_unchanged_write_is_refused`. s388: `test_s388s_commit_in_the_next_reply_with_no_write_is_refused`. Both pass only through the fallback, because the fixture repository has one commit (finding 4).
5. `test_revert_door.py::test_the_repair_of_a_head_that_fails_at_import_is_admitted` is green (observed). It asserts that the S144 write restores the fixture bytes, and that `code.commit` in the next reply returns `committed` True. It does not assert that no note opened.
6. The next night meets the ledger route that needs lines the note does not show. A whole-file note shows one line, and a span note shows eight. The seat logs what it read, the note stays open, and every commit is refused (finding 2).

## (b) Findings

1. `rota/roles/api.py:16107-16114` `_base_held`, high, CONFIRMED (observed: probes C and F). The owner match is exact. Probe C: the batch renames `f` to `g`, and a later write drops `echo(x)` from `g`. The result says `dropped`, and `_open_notes` is empty. Probe F: the batch nests `echo(x)` in `f.inner`, and the same happens. `entry` is None, so `reply_notes` also gets no path (api.py:15499). The commit in the same reply then lands too (reasoned: the diff's guard). This is a regression against frame 140, which refused that commit for every note. Fix: keep a line when the base file holds it in any owner, `_def_lines(base, spans, "")`, and keep the owner match for the count only.
2. `rota/roles/api.py:16159` `_close_logged_notes` with `_whole_drop` (api.py:17228) and `_lost_sentence` (api.py:17549), high, CONFIRMED (observed: probe R3d). A whole-file drop of `X = 5`, the main guard and `a()` stores three lines. The note shows "from `X = 5`" only. A ledger that names `X = 5` and "the main block" leaves the note open. A span note names eight lines and "N more", and the ledger needs every one. The seat cannot quote a line it never saw. Fix: name every stored line in the refusal text, or close on the path plus the first line the note shows.
3. `rota/roles/api.py:16108-16115` `_base_held`, low, CONFIRMED (observed: probe E). A base that `ast.parse` refuses gives `spans` None, so `keep` and `names` are empty and no note opens. The docstring says a base the door cannot read keeps every line. Fix: return True when `_def_spans(base)` is None and the base text is not empty.
4. `tests/rota/test_frame140_commit_beside_note.py:234` `_developer`, low, CONFIRMED (observed: probe B prints `BASE HEAD~1` on a one-commit repository, and the note keeps every line). The s282, s340 and s388 tests run through the fallback. No test renders the base-held path on the s282 text. Fix: commit a second, unrelated change in `_developer`, so HEAD~1 is a real base.
5. Review 2's lows 4 and 5, low, CONFIRMED (observed: the diff touches no `runner.py` and no merge path, and the pass report gives no reason). Fix: write one record line for each with its reason, or land the staged `drop_notes` writes in `session_fail`.

## (c) Probes

All under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f283/r3/`, run from the worktree with `pytest -s -p no:xdist --rootdir .`.

- `test_probe_r3b.py`: probes A to E. A two-commit repository, a span write that drops `echo(x)` and `return x`. A: base line, note opens. B: one commit, `BASE HEAD~1`, every line kept. C: owner renamed, no note. D: line re-indented under `if x:`, `return x` kept. E: base does not parse, no note.
- `test_probe_r3c.py`: probe F, the line nested in `f.inner`, no note.
- `test_probe_r3d.py`: a whole-file module-line note and a ledger that names `X = 5`. The note stays open. `_LOST_NAMED` is 8.
- A `python -c` probe of `_says`: a 77-character line cut at 60 inside a word. The full quote does not match, and the cut quote does. The note shows the cut, so this is no finding.
- `pytest tests/rota/test_identity.py tests/rota/test_frame140_commit_beside_note.py tests/rota/test_revert_door.py -q`: 55 passed.

## (d) Usage

The harness does not show this agent its own numbers. Estimate: about 40k input, 9k output, 49k total. No sub-agents.
