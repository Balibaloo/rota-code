# Frame 297, review 3 of ae1747bd (passes 3 and 4, diff 8e7b7e73..ae1747bd)

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_r297` at ae1747bd.
Verdict: sound with one high gap. The discard, the line-ending rule and the
read-only ledger door work as built. The next seat never reads the discard,
so one step of the ruled repair is missing. The gate shows no new red.

## (a) The verdict on each point

1. The discard: correct for each case in the brief. A non-ASCII path breaks it (finding 5).
2. The three paths: no Developer end is missed. Other roles correctly skip the discard. A failed end shows the wrong status line (finding 2).
3. The record: the seat of attempt 2 does not see the detail. `DETAIL_SHOWN` hides it (finding 1). Frame 150's ends-when is met by the clean tree only.
4. The notes: a note of another path stays open, and so does a note after a failed landing (finding 3). A refusal from such a note is plausible, not observed.
5. The line ending: correct on the CRLF checkout, the LF tree and the CRLF blob. A file with mixed endings becomes a whole-file diff (finding 4).
6. Review 2's findings 3 and 4: closed. The ledger door stages no close, and the refusal lists exactly `_shown_lines`.
7. The tests: faithful in shape. The touched files hold 0 CR bytes. The new wake sentence breaks STE (finding 7).

## (b) Findings

1. `rota/core/runner.py:339`, `DETAIL_SHOWN`, with `rota/core/scheduler.py:455-463`. High. CONFIRMED by probe B, `test_p3_detail_reaches_the_seat`. The detail of attempt 2 names the discarded path. The prompt of the next session holds neither "discarded" nor "attempt". Roman's option A says "the next builder reads that note first" (`plans/frame297-discard-history.md` section 5). So the seat reads nothing about the discard, and the detail lives only in `sessions.wake_detail`. A batch with a commit gets no discard sentence on any wake. Fix: add `tick:batch_start` to `DETAIL_SHOWN` with a register case that carries the live detail.

2. `rota/core/runner.py:5393-5398` against `rota/core/loop.py:59`. Low. CONFIRMED by probe B, `test_p2_failed_status_line`. The failed path appends the discard line after `session failed: ...`. The loop prints `errors[-1:]`, so the status line names the discard and hides the exception. The comment at `loop.py:55-58` says that the failure line comes last. The account's last turn is also the discard line now, not the error that `session_fail` writes. Fix: insert the discard line before the `session failed` line in `outcome.errors`.

3. `rota/core/lifecycle.py:284-291` and `rota/core/runner.py:5305`. Low. CONFIRMED by probe B for the open rows. The harm is PLAUSIBLE. These are the two cases:
   1. A session writes a noted drop, then writes the HEAD text back, and ends. The path is clean, so it is not in `gone`. The row stays `open` after the end (`test_p4_write_back_leaves_open_note`).
   2. `after_landing` raises after the normal-path discard. The staged closes never land, and the failed path finds a clean tree and closes nothing. A landed open row stays open, and the account loses the discard line (`test_p2_after_landing_raises`).

   The next seat's commit landed in case 1, because HEAD holds the lines. A refusal needs a note whose lines HEAD lacks, or a next write that does not parse. Then the next seat meets s215's shape again. Every open note at a Developer end is moot, because the end leaves no uncommitted write. Fix: at a Developer end, close every open note of the batch in the database after the landing, whatever `gone` holds.

4. `rota/roles/api.py:16757-16758`, `_line_ending`. Low. CONFIRMED by probe C, `test_pc_mixed`. A committed file with one CRLF line and 569 LF lines got a one-line write. The numstat was `569 569`. One CRLF byte makes the rule write CRLF on every line. Fix: use the ending that most lines of the old bytes hold.

5. `rota/core/worktrees.py:236-276`, `discard`. Low. CONFIRMED by probe A. Git quotes a non-ASCII path in `status --porcelain` with octal escapes. `discard` passes the escaped name to `git checkout`, and git refuses the whole pathspec list. So `a.py` stayed modified beside the non-ASCII file. `discard` still returned both paths, and the account says that both were discarded. The `check=False` hides the error. No indexed path in the old run databases is non-ASCII. Fix: read `status --porcelain -z`, and check the return code of the checkout.

Outside the points:

6. Commit body of a9096db8. Low. CONFIRMED by a read of `plans/frame297-provenance.md:99-102`. The body says that s215 "committed that write as its first act". s215 met the note at its first commit, and that commit was refused. The body also says that the next wake names the paths, and the seat never reads them (finding 1). Fix: correct both sentences in the next commit body.

7. `rota/core/lifecycle.py:256` and `rota/core/scheduler.py:460`. Low. CONFIRMED by a read. The detail reads "ended with no commit. Its writes were discarded at the session's end, no commit held them". The sentence uses the passive, joins two clauses with a comma, and says "no commit" twice. Fix: "the last session committed nothing. The runner discarded its writes to <paths>", with the constant and the matcher changed together.

## (c) Probes

All probes are under
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/c32575f3-13b3-4420-a2aa-defc2ca8caea/scratchpad/r3/`.
Each ran from the worktree root with `ROTA_MODEL=qwen3:8b` and `-p no:cacheprovider --rootdir=C:/Users/roman/rota_r297`.

- `pa.py`: `worktrees.discard` on temporary repositories. Cases: a modified file, an unstaged deletion, a staged new file, a staged rename, an untracked file in a new directory, a name with a space, a kept test file, an ignored file and a session commit. All came back as point 1 asks, and the commit and the test file stayed. A second repository held a non-ASCII tracked file beside a modified `a.py` (finding 5).
- `test_pb.py`: `run_session` end paths. The wake detail against the next prompt (finding 1). A backend that dies (finding 2). A write-back to HEAD, and `session_commit` patched to raise (finding 3). A Tester session on the batch left the tree dirty, as designed.
- `test_pc.py`: a CRLF checkout, an LF tree and CRLF blobs under `core.autocrlf=true`. In each, a one-line change gave numstat `1 1`, the HEAD text gave `_uncommitted == []`, and `_restored` was true after the restoring write. A mixed-ending file and a `.gitattributes` `eol=crlf` tree followed (finding 4).
- `test_pd.py`: ten stored lines with `return` and `raise`. The refusal listed exactly `_shown_lines`, with no "more". `value_7` and `value_8` were refused. A ledger note after a restoring write staged 0 `drop_notes` rows, and the note stayed open.
- The two touched test files: `63 passed in 45.68s`.
- The gate: `7 failed, 4142 passed, 207 skipped, 22 xfailed`. New reds 0, reds gone 0. The register is absent in the worktree, so the gate gave no stale count.
- A CR count over the 11 touched files: 0 in each.
- SQL over `D:/repos/rota/.rota/*.db`: 3353 `tests.path` rows, none with a leading `./` or a backslash. No non-ASCII path grain in `code_index`.

## (d) Usage

The harness gives no exact count. The estimate is about 110k input tokens and about 18k output tokens, about 128k in total. That is above the cap of about 80k, because of the gate and the four probes.
