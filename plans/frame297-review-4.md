# Frame 297, review 4 of 5eec792b (pass 5, diff ae1747bd..5eec792b)

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_r297` at 5eec792b.
Verdict: sound for the walk, with five low findings and no high finding.
The next seat reads the discard on the normal end, on the failed end and after a restart.
The seat reads nothing after a landing failure, a boot discard or a refused checkout.
The discard holds every path case of point 3. Frame 283's ends-when holds.

## (a) The verdict on each point

1. The key: present in attempt 2's first prompt, absent when nothing was discarded, and kept across a reopened database. Two end paths lose it (findings 1 and 3).
2. close_restored_notes: it cannot close a note on the seat's own unjudged write. The discard runs first in both paths. Frame 283's ends-when holds (probe B6).
3. The discard: every case is put back except the locked files. The account names the locked paths exactly. The seat's key then says that the tree is at HEAD, and that is false (finding 2).
4. The failed path: `errors[-1]` is `session failed: ...`, and the account turn follows the failure turn. Confirmed.
5. Review 3: findings 1, 2, 5 and 7 are closed. Finding 3 case 1 is closed. Finding 3 case 2 is half closed (finding 1). The correction of finding 6 is wrong again (finding 5). The frame 140 file shows no regression.
6. The six touched files hold 0 CR bytes. The new prose is Simplified Technical English, except one runner comment ("moot").

## (b) Findings

1. `rota/core/runner.py:5397-5405`. Low. CONFIRMED by probe B3. `session_commit` raised once after the normal-path discard. The tree was clean, and `out.errors` held the discard line before `session failed`. The account held only `SESSION FAILED: RuntimeError('landing died')`. The second discard found a clean tree, so `session_note` wrote nothing. The next `batches.expect` had no "discarded before you" key. Fix: in the failed path, write the discard lines that `outcome.errors` already holds when the second discard returns none.

2. `rota/roles/api.py:17505` with `rota/core/lifecycle.py:336-352`. Low. CONFIRMED by probe B5. A refused checkout left `M src/click/decorators.py` and its note open. The account said "could not put back these paths: src/click/decorators.py". The next seat read "NOTES.txt. No commit held them, so the tree is at HEAD." `last_discard` reads the DISCARDED line only. So the seat inherits s214's shape and reads a false statement about the tree. Fix: `last_discard` also returns the NOT_PUT_BACK paths, and the key names them and drops "the tree is at HEAD".

3. `rota/core/boot.py:191`. Low. CONFIRMED by a read. The boot's discard writes no session turn and passes no `failed_out`. A process that dies inside s214's shape leaves the tree dirty, and the boot discards it. The next seat's key is then absent, because no account holds the line. The paths git refused at boot go nowhere. Fix: the boot passes `failed_out` and writes both lines as a turn of the batch's last Developer session.

4. `rota/core/lifecycle.py:351`. Low. CONFIRMED by a read, harm PLAUSIBLE. The account joins the paths with ", ", and `last_discard` splits on ", ". A path name that holds ", " comes back as two wrong paths. Point 3's own goal is any path name. No old run database holds such a path. Fix: write one path per line under the DISCARDED line, or store the list as JSON.

Outside the points:

5. Commit body of 5eec792b, paragraph 3. Low. CONFIRMED by SQL on `D:/repos/rota/.rota/clickI_night156.db`. The body says that "s215's first act was a commit of s214's write, not a read". The `tool_calls` of s215 are pushed reads at 1-5, `code.probe` at 6, `code.source` at 7 and 8, then `code.commit` at 9. So s215 read first and then committed, and that commit was refused. The provenance (`plans/frame297-provenance.md:99-102`) agrees. Fix: the next commit body says that s215 read the span at calls 6 to 8, and its first commit at call 9 was refused.

## (c) Probes

All probes are under
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/c32575f3-13b3-4420-a2aa-defc2ca8caea/scratchpad/r4/`.
Each ran from the worktree root with `ROTA_MODEL=qwen3:8b`.

- `b/test_pb4.py`, `-n0 --rootdir=C:/Users/roman/rota_r297`: 6 passed.
  - B1: s214's shape, then `db.close()` and `db.connect` on the file. `in_transaction` was False after the end. Attempt 2's first prompt opened `[batches.expect]` with the key and the path.
  - B2: a session that wrote nothing. The next detail said "nothing written and nothing committed", and the key was absent.
  - B3: `runner.session_commit` patched to raise once (finding 1).
  - B4: a backend that dies. `errors[-1]` began `session failed:`. Turn 3 was the account and turn 2 was `SESSION FAILED`. The next prompt held the key.
  - B5: `_git_paths` refused the checkout of PATH (finding 2).
  - B6: after s214's end, no note was open. A fresh sandbox repeated the removal, and the commit in the same reply was refused. The ledger route then landed the commit.
- `pa4.py`: `worktrees.discard` on a temporary repository. These came back to HEAD: `a.py`, `src/café.py`, `my file.py`, `[ab].py`, the unstaged deletion `gone.py`, the staged new `staged.py`, the staged rename, and the untracked `new dir/nö.py`. `a.py.bak` was untouched by the `[ab].py` pathspec. `locked.py` and `untracked_locked.py` held an open handle. Both stayed, both were in `failed_out`, and neither was in the returned list.
- `test_old140.py`, the 8e7b7e73 copy of the frame 140 file: 4 failed, 45 passed on 5eec792b. The same 4 failed on an archive of ae1747bd under `r4/ae`. So pass 5 adds no regression. The 4 are review 3's accepted changes: the shown lines, the ledger door and the line ending.
- The two touched test files in the worktree: `66 passed in 100.79s`.
- A CR count over the six touched files: 0 in each, and 0 in the added lines.
- SQL over `D:/repos/rota/.rota/*.db`: no turn holds "no commit held", so the new DISCARDED prefix breaks no old record. The open `drop_notes` rows in `clickI`, `clickI_night156` and `clickI_prev` store lines, so `close_restored_notes` cannot close them on any text.
- The gate did not run. No point needed the full suite.

## (d) Usage

Input tokens about 95k, output tokens about 12k, total about 107k.
