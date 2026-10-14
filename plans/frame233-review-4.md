# Frame 233, pass 4: the diff review of the replayed cut

Review of be5b067c over ea6f869e, on the worktree `C:/Users/roman/rota_rv233d`. Meta workflow, the night's instrument. Read-only. Reviewer: Opus, 2026-10-14.

**Verdict: accept.** The key matches, the cut line replays byte-equal, and the seed marks the five cut turns of night 146 and no other turn. Four low findings follow. None of them blocks the frame. Findings 1 and 2 are candidates for a later pass.

## (a) The verdict on each point

1. The key: holds. The wrap and `RecordingBackend.complete` compute the same key from the same arguments.
2. The runner's branch: holds. The cut line is byte-equal to night 146's s71 seq 2. All other differences come from `cut_note`.
3. The seed's inference: holds on night 146, with 5 of 5 marked. `invented_result` does leave a sign, in the session note (finding 1).
4. The present-row rule: right. A key with night 145's whole reply keeps the whole reply and gets no reason.
5. The live record path: holds. The connection is autocommit, and the delete removes only a reason that the miss made false.
6. The tests: 4 of 9 are red on the parent. The delete branch, an `invented_result` record and a `tools` call have no test.
7. STE and CR bytes: holds. The three files hold 0 CR bytes.

## Points

**1. The key.** `NightBackend.complete` calls `key_for(system, user, pins, "native" if tools else "text")` (`probes/night_cassette.py:94`). `RecordingBackend.complete` uses the same expression (`rota/llm/cassettes.py:342-343`). `RecordingBackend` passes `pins` unchanged and never replaces it. `tools=None` and `tools=[]` both give `"text"` in the two places. The seed keys every turn with `"text"`, and it skips native sessions. So a seeded row and a hit agree. The cut replay test and the seed test prove a hit on a seeded key (observed: 9 passed, 2026-10-14).

**2. The runner's branch.** Probe p2 builds a `Completion` with night 146's s71 seq 1 text. It parses the text with `toolproto.extract_lenient` against the architect sandbox, once with `raw={"done_reason": "length"}` and once with `raw={}`. With `length`, the parse gives 2 calls (`model.describe` and a `ToolError`), and `_cut_inside_last` returns True. The runner's line, `ERROR reply cut: ` plus `_reply_cut_line(...)`, occurs once in night 146's s71 seq 2 `user`, byte-equal at its index (observed: p2, 2026-10-14). With `raw={}`, `inside` is False, and the runner runs the broken call, which is night 147's shape.

Probe p3 diffs night 146 against night 147 at the first differing prompt of the five sessions. Every difference is one of three kinds: the cut line, the error line of the last call that the cut skips, and the counts of the `CUT this exchange` window. The window counts depend on `cut_note` through `_CUT_NOTE_CHARS` (`rota/core/runner.py:3796`). So the raw value drives all three differences. The next key then matches (reasoned: no probe ran a whole session). The s9 case uses the second shape, "The cut fell after the last call", and p3 shows the same pattern for it.

**3. The seed's inference.** Probe p4 ran `seed` on a backup of `.rota/clickI_night146.db` into `scratchpad/rv233d/seeded.db`. The counts are sessions 104, turns 311, notes 61, walk 390 and cut 5. The marked turns are s71 seq 1, s81 seq 5, s24 seq 1, s41 seq 1 and s9 seq 2. They are the five longest completions of the onboarding, 19,382 to 33,904 characters. The next longest is s70 seq 1 at 15,390 characters, and its next prompt holds no cut line. An independent sign agrees: the onboarding note turns that hold "reply was cut at the output budget" are in s9, s24, s41, s71 and s81 only (observed: p5, 2026-10-14). Nine later turns hold an inherited cut line, and the count rule correctly skips them. The seed drops the note turns before it pairs a turn with its next turn, so a note never acts as the next prompt. The count rule can still miss a cut when the same prompt evicts an older cut block (finding 2). `invented_result` leaves a sign that the implementer missed (finding 1).

**4. The present-row rule.** Take a key that night 145 seeded with a whole reply and that night 146 recorded cut. The seed finds the key present with no reason row, and it compares the completions. They differ, so the seed writes no reason. The key keeps night 145's whole reply with no reason. A replay then gives the whole reply on the whole branch, and the next prompt is the one night 145 saw. Night 145's chain stays consistent with its own next rows, so the rule is right. A cut reason on night 145's whole text would make the replay add a false cut note.

**5. The live record path.** `wrap` opens the file with `open_dev_db` (`probes/night_cassette.py:133`), and `open_dev_db` connects with `isolation_level=None` (`rota/llm/cassettes.py:156`). So each `INSERT OR REPLACE` and each `DELETE` lands at once. The LiteLLM backend returns `raw={}` (`rota/llm/llm.py:602`), and a `Completion` with the default `raw` is the same. In both cases the wrap deletes the reason row of the key. A miss always writes the completion with `INSERT OR REPLACE`, so the old reason belongs to a text that is gone. The delete removes nothing that is still true. An inner backend that raises writes nothing.

**6. The tests.** The parent's probes with HEAD's test file give 4 failed and 5 passed (observed: p6, 2026-10-14). The red tests are the seed count test on `cut`, the cut replay, the table creation and the seed mark. At HEAD the file gives 9 passed. The hit with no row has a test (`not plain.raw`, and the old-file test). Three branches have no test: the `DELETE` on a live record, a live record of `invented_result`, and a call with `tools` set.

**7. STE and CR bytes.** The comments and the commit body use short active sentences and name their subject. A byte count gives 0 CR bytes in each of the three files.

## (b) Findings

1. `probes/seed_night_cassettes.py:42-48`, low, CONFIRMED. The comment says that the runner writes no sign of `invented_result`. The session note holds "the stream stopped at the invented result" in 9 onboarding sessions of night 146: s9, s22, s24, s28, s35, s77, s81, s82 and s104 (observed: p5, 2026-10-14). The prompts do not change, so the keys still match. A replayed session loses that error line in its note, and nightcount compares the sign (reasoned: frame 232's comment at `rota/core/runner.py:3831`). Fix: infer `invented_result` for the turn whose completion ends at the `FABRICATED_RESULT` match in a session whose note holds the line, or correct the comment.
2. `probes/seed_night_cassettes.py:51-52`, low, PLAUSIBLE. The count rule misses a cut when the next prompt evicts an older cut block in the same turn. Night 146 holds no such turn, and the note cross-check gives 5 of 5. Fix: count the cut lines only in the part of the next prompt after the own prompt's exchanges, or check the note's cut sentence per session.
3. `tests/rota/test_frame233_night_cassette.py:207-300`, low, CONFIRMED. No test covers the `DELETE` branch, an `invented_result` record, or a call with `tools` set. Fix: add a live record with `raw={}` over a key with a reason, one `invented_result` record, and one `tools=[...]` call that misses the `text` key.
4. `probes/night_cassette.py:100-106` with `rota/core/runner.py:3581`, low, PLAUSIBLE. Probe p2 proves the cut line, and p3 traces the rest of the diff to `cut_note`. No probe replays a whole s71 session. Fix: let night 148's onboarding count close the point, with s71, s24, s41, s9 and s81 all replayed.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f3b11814-a94a-4967-b659-274275321190/scratchpad/rv233d/`.

- `p1_s71.py`: backs up `D:/repos/rota/.rota/clickI_night146.db` (read-only URI) into `n146.db`, and prints s71 seq 1 and seq 2.
- `p2_cut.py`: builds an architect sandbox on the copy `n146_sb.db`. It runs `extract_lenient`, `_cut_inside_last` and `_reply_cut_line` on s71 seq 1 with and without `length`, and compares with s71 seq 2.
- `p3_diff.py`: backs up `D:/repos/rota/.rota/clickI.db` (night 147, read-only URI) into memory, and diffs the first differing prompt of the five sessions.
- `p4_seed.py`: runs `seed` on `n146.db` into `seeded.db`, and lists the marked turns and the longest completions.
- p5, a `python -c` call: counts the onboarding note turns with the stream-stop line and with the cut sentence.
- p6: `git archive ea6f869e` into `par/` with HEAD's test file beside it, then pytest on that file. Then pytest on the worktree's file at HEAD with `ROTA_RUNS` under the scratchpad.

## (d) Usage

From the context counter: about 64k input, 9k output, 73k in total. The cap was 50k. The parent test run, the note cross-check and the report write spent the excess.
