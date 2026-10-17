# Frame 140, review 1: pass 1 at 68e7ba44, the commit beside a `dropped` note

Reviewer: a read-only agent on the worktree `C:/Users/roman/rota_r140` at
68e7ba44, 2026-10-17. Rota workflow throughout.

Verdict: accepted with one medium finding. The mechanism holds on the
runner path. The refusal's second step leads to a second refusal in the
same reply. One recorded qwen3:8b case changes its replay.

## (a) Verdicts on the points

1. Reply boundary: holds on `run_session`, scenes and replay. Two narrow
   paths lose a commit (findings 2 and 3, low). PLAUSIBLE.
2. Reach: file B alone is right by design. A same-reply rewrite keeps a
   stale note, and the commit is refused (finding 1). CONFIRMED.
3. Frame 135's law: the text names the note's lines. Its second branch
   names a commit that the door refuses in the same reply (finding 1).
   CONFIRMED.
4. Byte for byte: the diff removes 0 lines. No other refusal and no result
   key changes. CONFIRMED.
5. Recorded cases: `L1-DV-read-the-map-not-the-whole-file` (qwen3:8b) goes
   stale or red. `L3-a-failed-verdict-turns-into-a-fix` (gemma3:12b) has
   the same shape off the suite model. CONFIRMED on the newest run of each.
6. Tests at dd9079af: 3 fail, 1 passes, as the pass report says. The
   revert-door line keeps the test on the revert door. CONFIRMED.

## (b) Findings

1. `rota/roles/api.py:15323` and `:15744`, medium, CONFIRMED. A note stays
   on `ctx.reply_notes` after a later write on the same path puts every
   statement back. Probe B: s282's span write, then a whole write that
   keeps every statement and returns no note, then `code.commit`. The
   commit is refused, and the refusal quotes "This write removes 3
   statements", which is no longer true. The refusal's own step says
   "write those lines back first, then commit". A seat that does both in
   one reply meets the refusal again. Frame 135's law says a refusal names
   only a call the doors admit. Cost: one more reply and one false fact.
   Fix: end the step with "then commit in your next reply", or drop the
   path's note when a later write on it returns no `dropped` key.

2. `rota/core/runner.py:4224` (stood-by path), low, PLAUSIBLE. Held calls
   run after `begin_reply()` of a reply with no calls. A held noted write
   and a held commit run together, so the commit is refused. The seat gets
   one answer through `stoodby_retried`. If that retry is spent, the loop
   breaks, and the write stays uncommitted. At dd9079af that commit landed.
   The seat never read the note there, so the refusal is right. The loss
   is the commit with no later reply. Fix: when `stoodby_retried` is
   spent and the only refusal is the note door, give one more reply.

3. `rota/core/runner.py:3992`, the loop over `max_iterations`, low,
   PLAUSIBLE. A noted write and its commit in the last allowed reply leave
   the write uncommitted, and no later reply exists. This is the wall that
   point 1 names. The pass count of "0 on a last turn" counts sessions that
   ended by choice, not by the cap. Fix: count the cap-ended sessions over
   nights 140 to 153 before the night, and accept the loss if the count is 0.

4. Outside the points. `rota/roles/api.py:15318`, low, CONFIRMED on this
   Windows host. `code.write` writes CRLF. A whole write of the HEAD text
   leaves the path dirty by line ends alone. Probe D: `git diff
   --ignore-cr-at-eol --stat` is empty, and `_uncommitted` lists the path.
   So the branch for a path the commit does not take never clears a noted
   path that the seat reverted by a whole write. The cause is older than
   frame 140. Fix: none in this frame. Note it beside frame 140's site.

5. Outside the points. `rota/testkit/scenes.py:536` and `:1506`, low,
   PLAUSIBLE. The scene scripts `commit()` and `land()` write and commit in
   one scripted reply. A future scene whose write drops a statement is
   refused, and its script has no second reply. The six scene files pass
   today, apart from one red that is not frame 140's (below). Fix: none
   now. A scene that writes a shorter file needs a second reply.

The scene probe found one red:
`test_scene_two_batches.py::test_a_right_call_lands[the project test
tests/test_templates.py as an encode]`, with `ledger.log: missing required
argument(s) ['kind']`. It does not touch `code.write` or `code.commit`.
Check it against the gate's known reds.

Counts: medium 1, low 4, high 0.

## Point details

Point 1, paths:

- `run_session`: one `begin_reply()` per completion, before the parse.
  Notes of reply N never refuse reply N+1. A held tail that a new reply
  supersedes is dropped at line 4310, so no held note leaks.
- A second `Sandbox`: `session_sandbox` builds a new `Ctx` per session,
  so notes never cross sessions. The cockpit's `build_sandbox` runs reads.
- Replay of a recorded case: it goes through `run_session` with the
  replay backend, so the boundary is the same.
- The dry run: `_code_write` returns `{}` before the record, and
  `_ctx_snapshot` restores a dict. A dry run never sends `code.commit`.
- `scenes.send`: one fresh sandbox per call. The `before` calls and the
  call share it with no boundary. No sweep call in the six scene files has
  a noted write before a commit, because the scene files pass.

Point 2, probe results:

- A: noted write on A, whole write of A back, write B, commit. Refused,
  because A stays dirty by CRLF (finding 4). On an LF host the design
  skips A, which is right.
- B: noted write, whole rewrite that keeps every statement, commit.
  Refused with the stale note (finding 1). Wrong.
- C: rota has no `code.revert` op. The revert door is a door of
  `code.commit`. A revert by a whole write is probe C: refused, as in A.

Point 3: the text quotes `path: note`, and the note names each statement
and its line. It gives one choice with two branches. It names no second
call, except the commit after the write-back (finding 1).

Point 4: the diff of 68e7ba44 holds 0 removed lines. The new record is on
`ctx`, and `out["dropped"]` keeps its text.

Point 5: the scan reads the newest `case_runs` row of each case and model
that holds `code.write` and `code.commit`, 62 pairs. For each reply with a
write before a commit, it finds the cassette whose completion is the next
reply. It then checks that prompt for a `"dropped":` write result before
the landed `OK code.commit` line. Two cases match:

- `L1-DV-read-the-map-not-the-whole-file`, qwen3:8b, reply 2 of 5.
- `L3-a-failed-verdict-turns-into-a-fix`, gemma3:12b, reply 2.

`L1-DV-take-a-mistake-out` matched on an older run (seq 284795) only. Its
newest run (seq 529466) shows no note before its commit. Limit: a commit
in the last reply of a case has no next prompt, so the scan cannot see it.

Point 6: at dd9079af with the new file copied in, the result was
`3 failed, 22 passed` over the new file and `test_revert_door.py`. Test 1
fails with `DID NOT RAISE <class 'ValueError'>`. Test 3 and test 4 fail on
the missing mechanism (`begin_reply`, `reply_notes`). Test 2 passes, as a
control does. The revert-door test still sends the commit through every
door after the note door, with the same runs. So it still measures the
admission of the repair. It no longer shows the one-reply shape of s144.
Test 1 covers that shape.

## (c) Probes

All under
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/eefbf293-6e8b-4a35-91c4-b3f1fed91a11/scratchpad/f140/r1/`.

- `probe_reach.py`: pytest on the fixture of the pass. Tests A, B, C and D
  of point 2 and finding 4.
- `probe_cases.py` to `probe_cases4.py`: read-only scans of
  `D:/repos/rota/tests/rota/cassettes.db`. The final scan of point 5 ran
  inline and applies the logic of `probe_cases4.py` to all 62 pairs.
- `parent/`: `git archive dd9079af` of `rota/` and the test support, with
  the new test file copied in. It ran the new file and `test_revert_door.py`.
- The six scene test files at 68e7ba44: `122 passed` and 1 red before `-x`
  stopped. Then three of the files: `1 failed, 107 passed`.

## (d) Usage

- Input tokens: about 95k, cache reads included. This is an estimate,
  because no harness counter shows in this context.
- Output tokens: about 12k.
- Total: about 107k, over the 40k cap. The case scan of point 5 took five
  probe shapes.
