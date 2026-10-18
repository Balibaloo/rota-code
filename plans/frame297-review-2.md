# Frame 297, review 2 of 8e7b7e73: the door after review 1, and the LF write

Read-only review on Opus, 2026-10-18, for session c32575f3. Worktree `C:/Users/roman/rota_r297` at 8e7b7e73. Brief `f297_review2_brief.md` in that session's scratchpad.

Verdict: not ready. Three high findings stand. The LF write makes finding 9 worse on a night worktree, because every night checkout holds CRLF. The ledger door closes a restored note too early, and a later silent drop then commits. The eight-line cap lists the wrong eight lines.

## (a) The verdict on each point

1. Fails. In a CRLF checkout, the LF write makes `_uncommitted` list a file that equals HEAD (finding 1). In a repository with CRLF blobs, a one-line change becomes a whole-file diff (finding 2). Only `harness.materialise` and `scaffold.py` still use `write_text` (finding 8). `_restored` reads with universal newlines, so the change does not touch it. No case or fixture asserts CRLF tree bytes.
2. Fails. The early close is a tree fact at the time of the ledger note, and the note can be stale at the commit. Probe Q2b committed `ctx.exit()` gone after a ledger note on another path. Probe Q2c, with no ledger note, was refused (finding 3).
3. Fails. The cap takes the first eight stored lines, and the note shows the eight lines of `_lost_named`, which puts `return` and `raise` first. A seat then closes the note on a line it never saw (finding 4). A seat with nine dropped lines reads eight lines with their line numbers and "and 1 more".
4. Findings 1, 2, 4 and 6 are closed by their tests. Finding 3 is closed, and the close it adds opens finding 3 of this review. Finding 5 is closed, and it opens finding 4. Finding 7 is closed, except for bg_2's row (finding 6). Finding 9 of review 1 is open on a night worktree (finding 1).
5. Holds. The text, `kind` and `about_table` of s214, s215, s274 and s300 match `ledger` exactly. N300 and N300_LINES match bg_3's `drop_notes` row exactly. N214 and N274 occur in `turns.user`. No test replays bg_2's eight-line row (finding 6).
6. Holds. Both touched files hold 0 CR bytes. The new prose follows STE. Two claims in it are wrong (finding 5).

## (b) Findings

1. `rota/roles/api.py:16101`. High. CONFIRMED by probe Q1d and the git repro `eolrepo`. The system gitconfig sets `core.autocrlf=true`, so a night checkout holds CRLF. In clickI, `git ls-files --eol` gives `w/crlf` for 160 files, and bg_1's `termui.py` holds 1025 CR bytes in 1025 lines. In Q1d, a one-line change and then the committed text again leave the file equal to HEAD. `_uncommitted` still lists `src/click/decorators.py`, because `git status --porcelain` reports an eol-only change as ` M`. The old CRLF write matched a night checkout, and the LF write breaks it. So the fix moves the defect of finding 9 from the LF fixtures to the nights. The CR bytes in bg_1 come from the checkout, so they do not show which file `code.write` wrote. Fix: write each line with the line ending that the old file bytes hold, and use LF for a new file.

2. `rota/roles/api.py:16101`. High. CONFIRMED by probe Q1b. A file committed with CRLF blobs (`i/crlf`) got a one-line write. The LF write gave numstat `3 3` for a three-line file, and the old CRLF write gave `1 1`. The sample repository `obsidian-contextual-note-templating` holds two `i/crlf` files. So a Windows repository gets a merged change in which every line of a written file changed. Fix: the fix of finding 1, which keeps the file's own line ending.

3. `rota/roles/api.py:17020`, the call of `_close_restored` in `_silent_note_refusal`. High. CONFIRMED by probes Q2b and Q2c. These are the steps of Q2b:
   1. A noted write drops lines of `decorators.py`, and a write puts them back.
   2. A ledger note about `other.py` lands. The door closes the restored note of `decorators.py` and stages a `restored` row.
   3. A whole-file write takes `ctx.exit()` out of the callback, and the result carries no `dropped` note (finding 7).
   4. The commit lands, and HEAD has no `ctx.exit()`.

   In Q2c, the same steps with no ledger note end in a refused commit, because the note is still open. Frame 283 ends a note when the tree holds the lines again, and the commit door judged that at the commit. The ledger door judges it earlier and stages the judgement. Fix: in the ledger door, test `_restored` in memory and stage no close, so that the commit door alone stages it.

4. `rota/roles/api.py:16954-16963`, `_listed_lines`. High. CONFIRMED by probe Q3. Ten stored lines, with `return value_9` and `raise ValueError(10)`, give a note that shows lines 1 to 6, 9 and 10. `_listed_lines` gives lines 1 to 8. The refusal then lists `value_7` and `value_8` with no line number, and it hides the `return` and `raise` lines under "and 2 more". The coordinator ruled on 2026-10-13 that `return` and `raise` come first (pass 1d). A ledger note that names `value_8 = compute(8)` closed the note with no refusal before it. The seat never saw that line, so the rule of frame 283's review 3, finding 2 fails. The frame 283 test passes only because its fixture holds no `return` line. Fix: build the list with `_lost_named` over the stored lines, and accept a listed line in `_note_says` only after a refusal shows it.

5. `rota/roles/api.py:16098-16100` and the body of 8e7b7e73. Low. CONFIRMED by a read of `test_p9_crlf.py`. The comment says that git saw a change in a write of the committed text. The probe of pass 2 added `# kept` to the file, so its ` M` proves nothing about CRLF. The CRLF cause is true for an LF checkout only (probe Q1a). The body also says "Eleven tests replay night 156's notes", and four tests replay them. Fix: name the LF checkout in the comment, and say "four replays" in the next commit body.

6. `tests/rota/test_frame140_commit_beside_note.py`, `test_the_refusal_lists_a_stored_line_the_newest_text_omits`. Low. CONFIRMED by the SQL on `drop_notes`. bg_2's row stores eight lines and shows six `kwargs` lines. The test uses a two-line entry that the night did not hold. Fix: add a replay with bg_2's exact row and the text of s214.

Outside the points:

7. `rota/roles/api.py:18128-18168`, `_whole_drop`. Low. CONFIRMED by probes Q2b and Q2c. A whole-file write that takes `ctx.exit()` out of a function body returns no `dropped` note. `_whole_drop` counts top-level lines only, so a lost statement inside a kept definition is silent. The defect predates 8e7b7e73, and it is the step that lets finding 3 commit a loss. Fix: run `_lost_statements` over each kept definition of a whole-file write.

8. `rota/core/harness.py:91` and `rota/core/scaffold.py:84-121`. Low. CONFIRMED by grep. Both still use `write_text`, so both write CRLF on Windows. `materialise` writes test files that `_uncommitted` excludes as furniture. `scaffold.py` writes a new project before its first commit. Neither changes a door's answer now. Fix: none now, and use the helper of finding 1 if it lands.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/c32575f3-13b3-4420-a2aa-defc2ca8caea/scratchpad/r297b/`. Each pytest probe ran from the worktree root with `-s -n0 -p no:cacheprovider --rootdir .` as its flags.

- `test_r2_probe.py::test_q1_eol`. Q1a writes the committed text with CRLF into an LF checkout. Q1b and Q1c write one changed line over a CRLF blob, with the new code and with CRLF bytes.
- `test_r2_probe.py::test_q3_cap`. It stores ten lines with a `return` and a `raise`, then nine plain lines. It prints the shown, listed and refused lines, and it closes on `value_8`.
- `test_r2_probe.py::test_q2_restored_other_path`. This first attempt failed in its setup, because the index did not hold `other.py`.
- `test_r2_probe2.py::test_q2b_with_ledger` and `test_q2c_without_ledger`. Each runs the restore, the ledger note on another path or none, the silent whole-file drop, and the commit.
- `test_r2_probe2.py::test_q1d_crlf_checkout`. It makes a CRLF checkout, sends a one-line write and then the committed text, and prints `_uncommitted` and `ls-files --eol`.
- `eolrepo/` is a repro with git alone. An LF write into a `w/crlf` checkout gives ` M` in `git status --porcelain` and an empty numstat.
- `git ls-files --eol` ran over each repository in `D:/repos/_AI/sample_repos`. In bg_1, `git diff HEAD~1 --stat` ran with a CR count of each changed file.
- Read-only SQL on `D:/repos/rota/.rota/clickI_night156.db` compared the test constants with `ledger`, `drop_notes` and `turns.user`.
- A grep of `tests/` for CRLF and a CR count of `tests/rota/cases/*.yaml` found no assertion on tree bytes.
- `tests/rota/test_frame140_commit_beside_note.py` gave 49 passed. A byte count found 0 CR bytes in both touched files.
- The gate did not run. The worktree holds no `tests/rota/cassettes.db`, so the gate replays no recorded case there (review 1, finding 10).

## (d) Usage

These numbers are estimates from the session counter.

- Input tokens: about 90k.
- Output tokens: about 12k.
- Total: about 102k. This is more than the cap of about 80k. The eol probes used the extra tokens.
