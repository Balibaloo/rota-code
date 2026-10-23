# Frame 283, W1 a, pass 1: review of e60a3c25

Verdict: **does not stand.** The door refuses s279's commit on the night database with the pass's text. The predicate admits removals that no ruling covers, and the route still leads a seat into the new refusal. Counts: 2 high, 2 medium, 2 low. All six are CONFIRMED by probe or by the record.

Reviewed at e60a3c25 in `C:/Users/roman/rota_r283`, parent f6a80169. Read-only. No gate, no re-record.

## (a) The claim, point by point

1. Point 1 holds. The replay on a copy of `.rota/clickI_night158.db` gives the pass's refusal byte for byte. The sentences have 19, 8 and 15 words. The seat can act on both routes, but its writes back failed on the night (F5).
2. Point 2 fails. The door admits a removal on any mention of the line or its call name in any landed ruling of the database. A criterion that demands the line admits its removal too. The texts must be the batch's own, and a mention must not count as a ruling (F1).
3. Point 3 fails. The first text offers the ledger route. The ledger door admits the note. Then the commit door refuses. The two doors disagree on the unruled path (F2). The first text must change.
4. Point 4: the commit after a ledger note was frame 283's behaviour, not frame 140's. Session judgement built it, and no ruling of Roman's covers it. One recorded case holds the ledger route text: `L1-DV-a-wordless-answer-on-a-right-red-test-is-carried-on` (qwen3:8b). The case is stale where a commit follows its ledger notes (PLAUSIBLE).
5. Point 5: the door is silent on a path that the commit does not take, so a merge can carry the removal. When the seat edits that path again, the door refuses every commit and says "this commit removes", which is false (F3).
6. Point 6: the pass stopped reading the row. It did not fix the row. `_close_logged_notes` still writes `restored` while the line is gone (F4).

## (b) Findings

1. **The predicate reads a mention as a ruling, and it reads every batch's rulings.** `rota/roles/api.py:16819-16831` (`_ruling_texts`) and `16763` (`_says` over the keys of `_gone_statements`, `16799-16801`). High. CONFIRMED.
   - Probe P2a: criterion "The tool must echo the value it reads". The removal of `echo(i)` after a ledger note commits.
   - Probe P2b: a landed ruling of another item, "echo is fine in the pager test". The same removal commits.
   - Probe P2c: on s279's replay, a criterion "the callback must still call ctx.exit()" admits the removal of `ctx.exit()`. The criterion forbids the removal, and the door admits it.
   - Probe P2d: a criterion with the word "continue" admits the removal of `continue`. A criterion with "return" admits the removal of a bare `return`. The controls with no word are refused.
   - On the night database, `_ruling_texts` for bg_3 reads 27 texts, with the 23 landed rulings of all items. The `echo` hit is a ruling about the pager test file of another batch. The `return` hit is a ruling about `confirm()`. A definition key also adds its last name, for example `callback`.
   - Fix: read only the criteria and rulings of the batch's own item, and admit only a text that names the full line or `name(` beside a removal word. Drop the bare keyword and bare call name keys.
2. **The route ends in a refusal, and the two doors disagree.** `rota/roles/api.py:17186-17195` (`_note_routes`), used at `16714` and `17271`. High. CONFIRMED.
   - On the night, s279 turns 7 to 12 read "Put the lines back with code.write, or log the removal with ledger.log naming the path and the lines". The seat took the ledger route three times, at seq 17, 20 and 23.
   - In the replay, the ledger note lands, the note closes, and the commit gets the new refusal. The ledger door `_silent_note_refusal` admits the note and still offers the ledger route.
   - After the close, no note is open, so a second ledger note meets no door. A seat can loop on ledger and commit.
   - The two doors agree on the restore path and on the ruled path. They disagree on the unruled path. For a ruled removal the ledger close is still needed, because the open note refuses first.
   - Fix: let `_note_routes` take the entry, and offer the ledger route only when `_ruling_texts` names a stored line. Otherwise offer the restore and `msg.escalate_architect`, in both doors.
3. **An earlier removal is carried by a merge, or it blocks the path with a false text.** `rota/roles/api.py:16757-16758` and `16767-16772`. Medium. CONFIRMED.
   - Probe P5a: HEAD already lacks `echo(i)`, and a `restored` row names it. A commit of another path lands. Nothing reads `drop_notes` at the merge.
   - Probe P5b: the same batch with an unrelated edit of the same path is refused with "this commit removes `echo(i)`". The commit removes nothing.
   - `discard_uncommitted` (`rota/core/lifecycle.py:291-295`) and `_discard_at_end` (`rota/core/runner.py:5432-5436`) stage `restored` with no tree check, so a closed row does not prove a restore.
   - Fix: compare the tree with HEAD to tell "this commit removes" from "the batch's head lacks". Put the same check at the merge for the closed rows of the batch.
4. **The `restored` row still names two facts.** `rota/roles/api.py:16873-16876` (`_put_note`), called from `17156` (`_close_logged_notes`). Medium. CONFIRMED.
   - The replay ends with the row at `restored` and `ctx.exit()` gone from the tree. The pass's own test asserts that state.
   - Readers of the status: `_open_notes`, `discard_uncommitted` and `close_restored_notes` read `status = 'open'`. `_closed_notes` reads `status != 'open'`. No code reader now trusts `restored` as a restore. A person who reads the table does, as the night 158 read did.
   - Fix: stage a second status, for example `logged`, in `_close_logged_notes`, and run the vocabulary test.
5. **The first route of the refusal failed on the night.** `rota/roles/api.py:16767-16772`. Low. CONFIRMED.
   - s279's writes back at seq 18, 24 and 25 were refused with "is not valid Python" and by the span door. The new text names the same code.write route first.
   - `msg.escalate_architect` is in the Developer's `tests_failing` tools, so the second route is real.
   - Fix: none in this door. The cut door owns the failed write back. Measure the escalate route on the next night.
6. **The refusal grows past 20 words, and two words are not simple.** `rota/roles/api.py:16767-16772`. Low. CONFIRMED.
   - One line gives 19 words in the first sentence. Each further line adds about four words.
   - "discharge" and "The team's note" are not plain words. The seat wrote the note.
   - Fix: write "Your note does not allow a removal." Put the list of lines in its own sentence.

Outside the points:

- The pass's s279 test uses a fixture database with one criterion, not the night database. Probe P1 closes that gap: the real criteria, items and rulings of the night give the same refusal.
- `_gone_statements` (`16799`) takes a call name after `return`, `await` or `yield`, but not after `raise`. A raised call is named only by its whole line. Low, no fix needed now.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/81fe1025-ee88-45f4-8210-744972761835/scratchpad`. Each ran with `PYTHONPATH=C:/Users/roman/rota_r283` from the worktree root.

- P1 `r283_replay.py`: copies `.rota/clickI_night158.db` to `r283_n158.db`, clears the row of bg_3, and replays the pass's `_replay`. Result: the row is `restored`, and the refusal equals the test's `REFUSAL`.
- P1b, inline: `_ruling_texts` on the copy for bg_3, with `_says` for `ctx.exit()`, `ctx.exit`, `echo`, `echo(`, `continue` and `return`. Result: 27 texts. Only `echo` (1) and `return` (1) hit, both from rulings of other batches.
- P2a and P2b, `r283_width.py`: a two-commit repository, a write that drops `echo(i)`, a scope ledger note and a commit. Results: A and B committed, and the control E was refused.
- P2c, `r283_p2b.py`: s279's replay with a criterion that demands `ctx.exit()`. Result: committed.
- P2d, `r283_width2.py`: a `restored` row for `continue` and for a bare `return`, with the line gone from the tree. Results: committed with the word in a criterion, refused in the controls.
- P5, `r283_p5.py`: HEAD lacks `echo(i)`, and a `restored` row names it. Results: another path commits, and an unrelated edit of the same path is refused.
- P4, `r283_cass2.py` and one inline query: `case_runs.transcript` of `tests/rota/cassettes.db`, read-only, for the ledger route text, the note text and the new text. Result: the ledger route is in `L1-DV-a-wordless-answer-on-a-right-red-test-is-carried-on` only, qwen3:8b, 39 runs. The new text is in no case. The transcripts are summaries, so they do not show whether a commit after a ledger note landed.
- P4b, `git log -S` on the three changed frame 140 tests: abd3caf4, 02ea9522 and ee166261 added them, all frame 283 commits. `plans/frame297-discard-history.md:23` calls the note route a session's judgement, not a ruling.
- s279's tool calls and turns on the copy, seq 14 to 39, from `tool_calls` and `turns`. No `drop_notes.noted` value was printed.

## (d) Usage

- Input tokens: about 100k.
- Output tokens: about 15k.
- Total: about 115k, against a cap of about 60k. The cassette query over 1.7 GB took about seven minutes.
