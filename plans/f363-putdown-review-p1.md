# Review of 2ef34070, the put-down step of frame 363, pass 1

Verdict: accept after two fixes. The stack bytes are right on every case. Two faults reach the first real use: a race that loses a status line of another session, and a `--since` page that marks a put-down frame "(closed)".

The worktree `wt-f363` was at c19c8dd8. The worktree `wt-parent` was at 2ef34070^, for point 5. I removed both worktrees. The three test files of the change pass: 78 passed in 20 s.

## (a) Verdicts on the points

1. The bytes of the stack: NO FAULT FOUND. On frames 294, 341, 314 (the last frame), 279 and 130, the stack loses the block, gains the section, and changes no other byte. Each archive copy is the block plus one status line. Finding 7 is a fault in the title of the row, not in the bytes.
2. Half an act: CONFIRMED, findings 2, 5 and 6. A race loses a line. A failed stack write leaves the block in both files, and a rerun archives the block a second time.
3. The check of the debts: CONFIRMED, finding 3. An import failure gives no line. The import costs 1.2 s on every run, and the check costs 3.6 s on the real stack. The check opens no register and writes no file.
4. The state print: CONFIRMED, findings 1 and 4. The section holds the three lines in the correct order. A ruling on a put-down frame prints "(closed)". The cut of a row removes the reason.
5. What was there before: NO FAULT FOUND. `--body`, `--text` and `--ruling` give the same bytes, output and exit codes in 36 cases.
6. The tests: three gaps, listed at the end of section (b).

Point 1, more detail:

- Frame 279 has a split heading. Its block runs from `### 279. Th` to the next heading, so the tail of the heading moves with the block.
- The block of frame 130 holds three status lines of frame 129, from 2026-10-16. They move to the archive with frame 130, and no byte is lost.
- In the run of three frames (294, 341, 314), the rows stand newest first: 314, 341, 294. The archive has one head and a blank line between the blocks.
- When the archive file of the day exists, the tool keeps its old bytes as a prefix.

Point 3, more detail:

- The import loads 290 modules. These include pytest, `rota.roles.api`, `rota.core.runner`, `rota.core.sandbox`, `rota.core.db` and yaml.
- The import sets `api.RECORD = True` and binds the template `init_db` in the process of the tool.
- The tool calls no `sqlite3.connect`, opens no file to write, and changes nothing in `git status --ignored`.
- Outside the repository root, `python -m rota.tools.status` runs only with PYTHONPATH set. With PYTHONPATH set, `tests` imports too. A run on a copy took 1.47 s.
- A tool under `rota/tools` that imports a test module is a low fault here. The result goes silent when the import fails, and the import runs before the path check. When the import succeeds, the check is correct.
- The smaller form: compare `stack` to `Path(__file__).parents[2] / "plans" / "stack.md"` before the import, and print one line when the import fails.

Point 4, more detail:

- I put down 27 frames on one copy, each with a reason of 170 characters. With `--since 2026-11-10` the page is 11,016 characters, and all 27 rows show.
- With `--since 2026-11-01` the cap cuts 15 rows. With `--since 2026-10-20` the cap cuts 18 rows.
- After its frames 327, 316 and 306 are put down, `--sid 66edc387` prints "No frame.". The live count goes from 17 to 3. No put-down frame prints in the closed section.

## (b) Findings

1. `rota/tools/state.py:557-559` with `:517`. Severity high. CONFIRMED.
   - `render_since` flags every frame of an archive file as closed. So `since_row` prints "(closed)" on the rulings and the assumed lines of a put-down frame.
   - On the copy with 27 frames put down, the rulings of frames 363 and 364 printed "(closed)" eight times. On the copy with three frames, the ruling on frame 294 printed "(closed)" the same way.
   - Fix: build `every` with `closed = not is_put_down(f)` for the archive frames, and print "(put down)" for the others.
2. `rota/tools/status.py:372` to `:286`. Severity high. CONFIRMED.
   - `main` reads the stack before the debt check, and `put_down` writes the old text back 1.2 s to 4.8 s later.
   - In the probe, another session wrote a status line in that window, and the put-down lost it: "the other line survives: False".
   - The batch of 27 frames keeps this window open for about two minutes, on the stack that all sessions write.
   - Fix: run `suite_reds` before the read, and read the stack bytes again immediately before `insert` and `cut_block`.
3. `rota/tools/status.py:215-220`. Severity low. CONFIRMED.
   - When a reader module fails to import, the tool skips it with no line. With pytest blocked, frame 362 got no line. With the import working, frame 362 got one line that names 2 debts.
   - The import of 1.2 s also runs on every copy, before the path compare.
   - Fix: compare the stack path to the `plans/stack.md` of the repository first, and print one WARNING line on an import failure.
4. `rota/tools/state.py:465` with `rota/tools/status.py:280`. Severity low. CONFIRMED.
   - The row puts the full title before the reason, and the print cuts the row at 300 characters.
   - With a reason of 170 characters, 25 of 27 rows lost the end of the reason and the path of the block.
   - In the real stack, 15 of 136 headings leave less than 100 characters for the reason.
   - Fix: in the row, cut the title to `NAME_LIMIT` and keep the reason whole.
5. `rota/tools/status.py:285-287`. Severity low. CONFIRMED.
   - When the stack write fails after the archive write, the block is in both files.
   - A rerun then archives the block a second time. The probe made the stack read-only, and the result was "copies in archive: 2".
   - An archive path that the tool cannot write raises a traceback with exit 1. The docstring gives exit 1 the meaning "the line is written and the commit failed". The disk was clean after that failure.
   - Fix: catch OSError around the two writes, print what is on disk, and skip the append when the archive of the day already ends with this block.
6. `rota/tools/status.py:317-330`. Severity low. CONFIRMED.
   - The commit takes the whole archive file of the day. In the probe, an uncommitted block of another session in that file went into the put-down commit.
   - After a failed commit, both files stay staged, and the message says "the line is written".
   - A rerun then exits 2 with "holds no frame".
   - A file that another session staged stays out of the commit, as intended.
   - Fix: when the commit fails, print the exact `git commit -- <paths>` command, and use a message that names the put-down.
7. `rota/tools/status.py:242` with `plans/stack.md:2674`. Severity low. CONFIRMED.
   - The split heading of frame 279 gives the row "- 279. Th Put down ...". Roman cannot name the frame from that row.
   - Fix: join the heading of frame 279 in the stack before the batch runs. This is an edit of the data.
8. `rota/tools/status.py:201`. Severity low. PLAUSIBLE.
   - `append_block` writes the whole archive of the day again with "wb". A kill during that write can cut off the blocks of earlier put-downs in the same `--no-commit` batch.
   - I did not run a kill during the write. Git HEAD still holds the stack from before the batch, so the frames can be recovered.
   - Fix: open the archive with "ab" and write only the new tail.

The tests (point 6):

- No test runs `--since` on a put-down frame that holds a ruling or an assumed line. `test_since_prints_the_put_down_line_and_not_a_close` checks only the closed section, so finding 1 passes green.
- `test_a_reader_of_another_stack_and_a_broken_reader_refuse_nothing` breaks `debts()` only. No test makes the import fail, so finding 3 passes green.
- No test changes the stack between the read and the write, or fails one of the two writes. No test covers the claim "never in neither" in the comment, so findings 2 and 5 pass green.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/b49d24d2-57eb-433f-9940-45704503a6cd/scratchpad/review/`. Their copies are under `data/`, which is outside every git tree. This session has no Write tool, so I wrote the probes with a quoted heredoc. The probes hold no backslash, because they use `chr(10)`.

- `p1_bytes.py`: puts down frames 294, 341, 314, 279 and 130, each on a fresh copy of the stack and the archive. It compares each result to the old text minus the block. It diffs each archive block against the old block.
- `p1b_three.py`: writes a ruling on frame 294, then puts down frames 294, 341 and 314 on one copy. It checks the order of the rows and the archive. It also appends to the existing `stack-2026-11-08.md`.
- `p4_since.txt`: the output of `python -m rota.tools.state --stack <three> --since 2026-11-10`. The run with `--sid 66edc387` printed to the terminal.
- `p4_cap.py`: puts down 27 frames of the batches section. It renders `--since` for three dates, and counts the rows that keep the whole reason.
- `p5_same.py`: runs 9 cases on LF and CRLF copies, each with and without an enrolment, in both worktrees from one source stack. The files `p5_new.json` and `p5_old.json` are byte-identical.
- `p2_half.py`: tests a directory at the archive path, and a read-only stack followed by a rerun. It writes a racing status line inside `suite_reds`. In throwaway git repositories, it tests a staged file of another session, a pre-commit hook that fails, and an edit of another session in the archive file of the day.
- `p3_debts.py`: times the import of the reader and `suite_reds`. It watches `sqlite3.connect` and every open for writing. It compares `git status --ignored` before and after the run.
- `p3_skip.py`: runs `suite_reds` for frame 362 with pytest present and with pytest blocked. A run of the command line from `data/` with PYTHONPATH set took 1.47 s.
- pytest: `tests/rota/test_status_gates.py`, `tests/rota/test_tools_state.py` and `tests/rota/test_f33_debts_name_open_frames.py` gave 78 passed.

## (d) Usage

These counts are estimates, because the harness gives no count to the agent. Input tokens: about 160k. Output tokens: about 22k. Total: about 182k.
