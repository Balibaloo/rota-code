# Review of 80a96d7a, the put-down step of frame 363, pass 1b

Verdict: accept. The seven repairs hold, and the stack bytes are right on every case. Two new faults are low, and each needs a write that fails in the middle to show.

The worktree `wt` was at 80a96d7a. The worktree `wt-old` was at 2ef34070^ (df04b7bf), for point 4. I removed both worktrees. The three test files of the change pass: 91 passed in 25 s.

## (a) Verdicts on the points

1. The seven repairs: all seven faults are gone. The detail for each finding is below.
2. The bytes of the stack: NO FAULT FOUND. Frames 294, 341 and 314, and two runs of 27 frames, give exact bytes and one whole copy in the archive.
3. The repair of the gap: NO FAULT FOUND. A line written inside the real debt check survives. The gap from the last read to the write is 11 to 59 ms.
4. The old paths: NO FAULT FOUND. `--body`, `--text` and `--ruling` give the same bytes in 36 cases, and the commit path of `--text` prints the same lines.
5. New faults: two, both CONFIRMED by a simulated write failure. They are findings 1 and 2 of section (b).

Point 1, by finding of the earlier review:

- Finding 1, gone. After a ruling on frame 294 and three put-downs, the `--since 2026-11-10` page prints "(closed)" 0 times and "(put down)" 1 time. On 27 frames, no row of a put-down frame prints "(closed)". The 2 "(closed)" rows with `--since 2026-11-01` are frames of the real archive files of 2026-11-01 to 2026-11-08.
- Finding 2, gone. Point 3 holds the probe.
- Finding 3, gone. On a copy, `suite_reds` returns in 1 ms and does not import the reader. A command line run on a copy takes 0.22 s. With pytest blocked and the stack path patched to match, the tool prints one WARNING line. The line names the reader and the ModuleNotFoundError. With pytest present, frame 362 gets one line that names 2 debts.
- Finding 4, gone. With a reason of 153 characters, each row that the page shows holds the whole reason and the path of the block. The rows in the stack are 294 to 342 characters long. The page cap now cuts whole rows: `--since 2026-11-10` shows 20 of 27 rows and prints "7 older rows cut". `--since 2026-11-01` shows 10 rows, and `--since 2026-10-20` shows 8. The `## Put down` section of the stack holds all 27 rows.
- Finding 5, gone. A read-only stack gives exit 1 and a correct message. After the rerun, the archive holds frame 294 one time, and the stack no longer holds the frame. A directory at the archive path gives exit 1, and the stack bytes do not change.
- Finding 6, gone. A pre-commit hook that fails gives exit 1 and prints a `git -C <plans> commit -m ... -- <stack> <archive>` command. The reason held a single quote, a dollar variable and backticks. I ran the printed command in Git Bash: exit 0, and HEAD holds the two files with the put-down summary and prose.
- Finding 8, gone. The archive opens in mode "ab". A write cut half way keeps the bytes of the earlier put-down as a prefix.

Point 2, more detail:

- For each case, the stack after the run equals the old text minus the blocks, one blank line, the section head and the rows. No other byte changes. The stack keeps its LF line end.
- The run of 27 frames from `## The batches` and the run of the last 27 frames of the file each give 27 rows, newest first.
- The archive file of the day holds each block one time. Each block is the old block plus one put-down status line. The archive has one head and ends with one LF.

Point 3, more detail:

- The probe patched `status.REPO_STACK` and the reader's `STACK` to the copy, so the real `suite_reds` ran on it. The patched `reader.debts` wrote a status line into frame 341 of the copy after its real work.
- Result: "the other line survives: True". The run took 3.78 s, and the debt check took most of that time.
- The gap is the time from the last `read_bytes` of the stack to the `open(stack, "wb")`. On the first put-down the gap was 17 ms.
- Over a batch of 27 put-downs, the gap was 10.9 ms to 59.3 ms. The gap grows with the archive of the day, because `archived` parses that file. The old gap was 1.2 s to 4.8 s.
- A run on the real stack takes 3.5 s to 4.0 s for the debt check, so the batch of 27 takes about 100 s. The stack is open to a lost line for about 1.6 s of that time in total.

## (b) Findings

1. `rota/tools/status.py:349-356`. Severity low. CONFIRMED by simulation.
   - `open(stack, "wb")` empties the stack before the write. A write that fails after the open leaves a cut stack.
   - The message then says "the frame is still in the stack. Run the put-down again". Both claims are false in this case.
   - The probe made the write raise ENOSPC after half the bytes. The stack went from 5753 lines to 2570 lines, and from 136 frames to 22. The rerun exited 2 with "the stack holds no frame 294".
   - The test `test_a_failed_stack_write_leaves_the_block_once_after_a_rerun` uses a read-only file. There the open fails before it empties the file, so the test passes.
   - In the batch with `--no-commit`, the rows of the earlier put-downs exist only on disk. A cut stack loses them, and git HEAD holds only the stack from before the batch.
   - Fix: write the new stack to a temporary file beside it, and `os.replace` it onto the stack.
2. `rota/tools/status.py:338-348` with `:240-241`. Severity low. CONFIRMED by simulation.
   - A failed archive write can leave part of the block in the archive. The message says "Check ... for a part of the block", and the tool leaves the part there.
   - `archived` matches only a whole block. So the rerun appends a second, whole copy.
   - The probe cut the append at half its bytes. After the rerun, the archive held two headings of frame 294.
   - The part has no put-down line. So `--since` prints frame 294 in the Closed section: "294. Four caps live as literals ... (archived 2026-11-10)". This is the fault of finding 1 of the earlier review, by another path.
   - Fix: on an OSError of the append, truncate the archive back to its old length before the tool exits 1.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/b49d24d2-57eb-433f-9940-45704503a6cd/scratchpad/review1b/probes/`. Their copies are in `review1b/data/`, which is outside every git tree. Each probe ran from the worktree root and printed the path of the status module that it imported.

- `p2_bytes.py`: puts down frames 294, 341 and 314, each on a fresh copy. It then puts down 27 frames of `## The batches`, and the last 27 frames of the file, on one copy each. It compares the stack with the exact expected bytes, and each archive block with the old block.
- `p1_repairs.py`: writes a ruling on frame 294, puts down three frames and counts the marks of `--since`. It puts down 27 frames with a long reason and renders three dates. It runs a read-only stack and the rerun, a directory at the archive path, and an append cut half way.
- `p3_race.py`: runs the real debt check on a copy with a writer inside `reader.debts`. It times the gap from the last read to the write for one put-down and for a batch of 27.
- `p3_skip.py`: runs `suite_reds` on a copy, with pytest blocked, and with the reader present. A command line run on a copy took 0.22 s.
- `p6_commit.py`: in a throwaway git repository, a pre-commit hook fails. The probe then runs the printed command in Git Bash.
- `p4_same.py`: the probe `p5_same.py` of the earlier review, run in both worktrees from one source stack. The files `data/p4_new.json` and `data/p4_old.json` are byte-identical.
- `p4_commit.py`: the commit path of `--text` with a hook that fails and then passes. The outputs `data/p4c_new.txt` and `data/p4c_old.txt` are byte-identical.
- `p5_new.py`: a stack write that fails after the open, and an archive append cut half way. A rerun follows each.
- pytest: `tests/rota/test_status_gates.py`, `tests/rota/test_tools_state.py` and `tests/rota/test_f33_debts_name_open_frames.py` gave 91 passed.

## (d) Usage

These counts are estimates, because the harness gives no count to the agent. Input tokens: about 130k. Output tokens: about 22k. Total: about 152k.
