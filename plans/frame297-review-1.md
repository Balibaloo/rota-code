# Frame 297, review 1 of 095db1c4: the ledger door on an open dropped note

Read-only review on Opus, 2026-10-18, for session c32575f3. Worktree
`C:/Users/roman/rota_r297` at 095db1c4. Brief `f297_review1_brief.md` in that
session's scratchpad.

Verdict: the door refuses the three shapes of night 156, and the text names the
lines. Three high findings stand before the door is safe. The token rule refuses
s215's honest removal note. The door fires for roles that hold no `code.write`.
The refusal states a tree fact that it never reads.

## (a) The verdict on each point

1. Holds. The door refuses s214, s274 and s300 with their real notes, and the text names each shown line. All three seats sent `src/click/decorators.py`, and `_ref_names` matches it.
2. Fails in one place. The door refuses s215's honest removal note `l_8c98565350` at its first two sends (finding 1). No class (a) note is refused on the record, and one is PLAUSIBLE (finding 8).
3. Fails. The commit door refuses only on a dirty path with the lines gone. The ledger door also fires when the lines are back or the tree matches HEAD (finding 3).
4. The skip is right. An empty entry closes only on a changed file. The commit door's route sentence still offers the ledger route for that entry, and that route is dead (finding 6).
5. Holds. The cut form and the full form of a shown line both land and close the note. A criterion note that names the path lands, and the note stays open.
6. Fails. The Architect, the Tester and the Liaison carry the running batch's `batch_id`, and the door fires for each (finding 2).
7. The loop is bounded. The runner ends the session at the fourth equal refusal. The text gives the lines, except in findings 1, 4 and 5.
8. Partly. The renamed test keeps the old coverage. Two replays use s282's note and not the night's note, and s300 has no test (finding 7). No CR byte is in either file. The new prose follows STE.

## (b) Findings

1. `rota/roles/api.py:16908`, with `_says` at 16853. High. CONFIRMED by probe P1. Against s215's real note, "`echo(` at line 543", the text "removed echo(msg, color=ctx.color) and ctx.exit() ..." is refused. The refusal says "This note names none of them". The seat named the line in its call form. The lookahead in `_says` rejects `echo(` when a word character follows it. On the night, s215 sent this text five times. Fix: count a shown line that ends in an open bracket as said when the text holds it followed by any character.

2. `rota/roles/api.py:16933` and `16888-16891`. High. CONFIRMED by probe P6. `loop._batch_of` gives a message wake the running batch, so every role with `ledger.log` carries a `batch_id`. The roles are the Architect, the Developer, the Liaison, the Terminologist, the Tester and the Vision Keeper. The Architect, the Tester and the Liaison were each refused with "Put the lines back with code.write", and only the Developer holds `code.write`. Each then logged a note that names a shown line. That note landed and closed the Developer's open note, so a commit without the lines can land. Fix: fire the door and the close only when `ctx.role == "developer"`.

3. `rota/roles/api.py:16935-16943`. High. CONFIRMED by probes P3 and P3b. In P3b, a write puts the lines back. The note stays open until a commit, so an honest note after the write is refused with "Put the lines back". In P3, the write sends the committed text again. The ledger door says "holds a write that no commit holds", and the commit door then says "the tree is exactly as you found it". The commit door reads the tree with `_restored` and `_uncommitted`, and the ledger door reads neither. Fix: run the commit door's `_restored` check on the worktree first, close a restored note, and require the path in `_uncommitted`.

4. `rota/roles/api.py:16941`, with the cause at `16107-16124`. Low. CONFIRMED by probe P7 and the bg_3 row of `drop_notes` on night 156. bg_3's note shows four statements, but the entry stores three. The fourth is `output = message % {...` at line 547. A note that names that shown line is refused again with the same sentence. The note text is built before `_base_held` and `_changed_kept` filter the lines. Fix: rebuild the note text from the stored lines after the filters.

5. `rota/roles/api.py:16134-16142`. Low. CONFIRMED by the bg_2 row of `drop_notes` on night 156. A later write keeps the earlier lines but replaces the note text. bg_2's row stores eight lines, `echo(` and `ctx.exit()` among them, and its text shows the six `kwargs` lines only. The door quotes that text, so the seat never sees `echo(`. A note that names one `kwargs` line closes `echo(` as well. Fix: list the stored lines in the ledger refusal, not the newest note text.

6. `rota/roles/api.py:16609-16611` and `16834-16835`. Low. CONFIRMED by probe P4. `_put_note` stores an entry with no line and no definition only when `_note_entry` finds no stored line. This occurs when `before` cannot be read or every dropped line is blank. The door lets s214's text land on that entry, and the note stays open. The commit door then refuses with the route "or log the removal with ledger.log", and no ledger note can close that entry. Fix: for such an entry, the commit door names the `code.write` route only.

7. `tests/rota/test_frame140_commit_beside_note.py:524-552`. Low. CONFIRMED by reading the tests against the night database. The s214 test uses s282's three-statement note, but s214 met "`echo(` at line 543" only. The s274 test sends `kind="default"`, but s274 sent `kind='scope'`. It also uses s282's note and not s274's seven statements. No test replays s300 or s215's real note. Probe P1b shows that `scope` reaches the door in `tests_failing` mode, so the outcome holds. Fix: add replays with the exact notes and kinds of s214, s215, s274 and s300.

8. Class (a) row `l_5ccbe7600e`, night 151. Low. PLAUSIBLE, by the scan `scan_a.py`. Earlier, s297 and s314 got `dropped` results on `src/click/decorators.py` in bg_4, before s322 logged "prog_name is a nonlocal variable ...". `_ref_names` matches its `path::version_option` grain. If those notes were still open, the door refuses an honest note. The other 21 (a) rows met no earlier `dropped` result on their path in their batch. Nights 140 to 155 hold no `drop_notes` row, so nobody can check this on the record. Fix: none until a night shows the shape.

Outside the points:

9. Low. PLAUSIBLE. In P3, `_uncommitted` listed `src/click/decorators.py` after `code.write` sent the committed text again. `git diff --cached` then found nothing to commit. The likely cause is `Path.write_text` at `rota/roles/api.py:16098`, which writes CRLF on Windows. Fix: write with `newline=""`, then check that both doors give one answer on a write that matches HEAD.

10. Low. CONFIRMED. The gate found no baseline in the worktree and stored `.rota-gate.json` there. That file is ignored and untracked. The register `tests/rota/cassettes.db` is absent, so the gate replayed no recorded case. All 7 reds are also in the main checkout's baseline. Fix: run the gate in the main checkout to replay the cases.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/c32575f3-13b3-4420-a2aa-defc2ca8caea/scratchpad/r297/`. Each ran from the worktree root with pytest `-s`.

- `test_probe_door.py::test_p1_night156_shapes` sends the texts of s214, s215 and s300 against their real notes, from `drop_notes` and `turns.user` of `.rota/clickI_night156.db`. All three were refused.
- `test_p1b_s274_scope` sends s274's text with `scope`, `assumption` and `default`.
- `test_p3_clean_tree` sends the committed text again, then a ledger note and a commit.
- `test_p3b_restored_dirty` sends the restoring span, then an honest note and a commit.
- `test_p4_empty_entry` stores an entry with no line and no definition, then sends a ledger note and a commit.
- `test_p5_cut_and_full` sends the cut form, the full line, and a criterion note that names the path.
- `test_p6_other_roles` lands the `drop_notes` row, then sends notes as the Architect, the Tester and the Liaison.
- `test_p7_shown_not_stored` names bg_3's shown `output = ...` line and `echo(message)`.
- `test_p8_ref_forms` sends five forms of `about_ref`.
- `scan_a.py` finds earlier `dropped` results for the 22 class (a) rows of nights 140 to 156.
- Read-only SQL found the rows of `drop_notes`, `ledger`, `tool_calls` and `turns` for s214, s215, s274 and s300 on night 156.
- `tests/rota/test_frame140_commit_beside_note.py` gave 40 passed. `test_desk_guards.py`, `test_t0_sandbox.py` and `test_runner.py` gave 578 passed.
- `rota.tools.gate` gave 7 failed, 4119 passed and 207 skipped, with no new reds against its own fresh baseline.
- A byte count found 0 CR bytes in both touched files and in their parents.

## (d) Usage

These numbers are estimates from the session counter. They are not exact.

- Input tokens: about 125k.
- Output tokens: about 15k.
- Total: about 140k. This is more than the brief's cap of about 80k. The gate run and the night replays used the extra tokens.
