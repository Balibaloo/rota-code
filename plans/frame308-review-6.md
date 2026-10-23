# Frame 308, review 6: pass 3d at 0798ac8d

Reviewer on Opus, read-only, in `C:/Users/roman/rota_r308` at 0798ac8d. No gate, no re-record, no full suite. Night databases opened with `?mode=ro`.

## Verdict

Put 0798ac8d on the branch. Review 5's findings 1 and 2 are closed, and cases A, A2 and H still refuse. The four commits apply in order on the branch head b57793c0, and the frame's three test files pass there. The pass report's count of 61 drops in 1102 readings is right, but that sweep does not reach the drop reader much. Night 160 holds 24 `order:` rows, and the record path is right where it differs from the fallback. Night 160 shows one new wall that predates this commit: `_WORDS_FAULT` misses "isn't right" and "should just say" (finding 1).

## (a) The points

1. Review 5's F1 and F2: closed. All nine drop cases and all five keep shapes read as intended.
2. The drop reader: 30 of 33 unique hits read as drops, and 3 do not. One of the 3 is a wrong refusal of a whole-line drop (finding 2). No partial edit or revert is admitted on real words. The count of 61 drops over 1102 readings, unchanged against 46471ca4, is right.
3. Review 5's F3: no change. The respecify of the dropped cr_3 lands, and the answer is admitted. Recommend the door fix (finding 3).
4. Night 160: 24 `order:` rows and 12 ruling relays, 10 with an answer call. On 9 of the 10, the record path gives the same verdict as the fallback. On s255 the two differ, and the record path is right.
5. Cherry-pick: all four patches apply in order on b57793c0, with no conflict.

## Point 1, review 5's findings 1 and 2

Probes `r6/test_r5_drop.py`, `r6/test_r5_keep.py` and `r6/test_r5_resp.py` ran against 0798ac8d: 15 passed.

- A, A2 and H: refused. A says "leaves out cr_2", A2 says "leaves out cr_3", H says "leaves out cr_2". A seat cannot omit a criterion that the ruling contests and does not drop.
- B: refused, with a respecify of cr_2 asked. C: admitted, as pass 3c intends. D: refused.
- E ("Remove line 5's last clause"), F ("should go further") and G: now refused with "leaves out cr_3". At 46471ca4, E and F were admitted. F2 is closed.
- k1 to k4, the four keep shapes: `_words_fault_on` True and `ruling_asks_no_new_words` False. g1 ("should go back"): no drop. F1 is closed.

## Point 2, the closed lists

Probe `r6/sweep_drop.py` splits every `rulings.words` of nights 140 to 159 at sentence ends. It runs `_drops_whole_line` on each `_DROP_LINE` hit. It found 43 hits, 33 unique. Output: `r6/sweep_drop.txt`.

Refused, 3:

- n140 r_4dfcbd586b "Line 3 should go back to how you had it": a revert. The refusal is right.
- n142 r_m144 "Don't remove lines 8 to 14 as a block": a negated request. The refusal is right.
- n142 r_m37 "I meant to drop lines 3 and 4 from your page, not from the README.": a whole-line drop. The refusal is wrong. The lead "I meant to" is not in `_REQUEST_LEADS`, so `_removal_spans` returns no clause. At 46471ca4, `_faults_on` read a drop here (finding 2).

Admitted, 30: each is a whole-line drop on my reading. Night 157's r_f117dc206e "remove line 4 and its check" is a whole-line drop too.

Synthetic shapes outside the nights, in the same probe style:

- "Drop line 5 but keep line 4." reads no drop, because `_NARROW_TAIL` holds "but". With a comma before "but", it reads a drop.
- "Can you drop line 5?" reads no drop. The lead is a question.
- "Remove line 5 up to the comma." reads a drop. The pass report names this gap.

Each wrong refusal makes the door ask a respecify of a line he dropped. That is a stall, not a leak. Only "up to the comma" leaks, and no night holds that shape.

The count: probe `r6/sweep_all_r6.py` is pass 3d's `sweep308_all.py` pointed at the worktree. It gives 1102 rows: 1024 asks, 78 stands, 61 drops. The output is identical to `sweep_3d.txt` and to `sweep_3c.txt`. The claim is right. The sweep reads only `contest` and `revise` items. r_m37 has an empty `per_item`, so the sweep never reads it.

## Point 3, review 5's finding 3

`test_r5_resp.py` at 0798ac8d prints "respecify LANDED" and "answer ADMITTED". The behaviour did not change.

Recommendation: refuse `criteria.respecify` on a criterion whose line the last ruling drops. Reasons:

- The answer refusal already says "Do not rewrite cr_3". A door makes the text true. A record for frame 192 leaves the frame 306 shape open until frame 192 lands.
- The predicate exists: `ruling_drops_line`. The door is one check in `criteria_respecify`.
- After 0798ac8d, the drop reader errs toward no drop on real words. So the door rarely blocks a rewrite he asked for.

## Point 4, night 160

`D:/repos/rota/.rota/clickI.db` holds 24 `order:` rows and 30 rulings. Probe `r6/replay_n160.py` is pass 3d's `replay308_wake.py` with night 160's twelve relay sessions. It ran once on the record path, and once with the `order` rows of `door_rows` forced empty.

- s94 and s170: no answer call.
- s136, s143, s175, s195, s211, s227: admitted on both paths.
- s219, s246, s265: refused on both paths.
- s255 (m117, ruling r_44b442e2a3 at m115): the record path admits the answer with cr_2 and cr_3. The fallback refuses it for no respecify of cr_3. `order:m115` puts cr_3 on line 4. His words on line 4 fault only its check. The record path is right.

Probe `r6/n160_paths.py` reads every contested criterion on both paths: 31 readings, 29 same. One difference is s255's cr_3, as above. The other is r_04b24ea9ce cr_2 (finding 1). On the read-only connection, the fallback render gives no line for most rows. So that probe understates the fallback, and the replay is the count of record.

## Point 5, the cherry-pick

`git format-patch -1` wrote each commit into `r6/patches/`. `git archive` of b57793c0 (`rota` and `tests`) went into `r6/head/`. `git apply --check`, then `git apply`, ran in order. 32c1f02f, 2b360151, 46471ca4 and 0798ac8d all apply. No patch conflicts. The patches touch `rota/roles/api.py`, `rota/core/sandbox.py` and three test files. In `r6/head`, `test_frame308_ruling_answer.py`, `test_frame308_answer_after_respecify.py` and `test_criterion_contest.py` give 67 passed. The import resolves to `r6/head/rota`.

## (b) Findings

1. `rota/roles/api.py:5406` `_WORDS_FAULT`. High. CONFIRMED on the reader, PLAUSIBLE at the door. Night 160's r_04b24ea9ce says "Line 4 still isn't right: its text is still my note, when it should just say ...". `order:m122` puts cr_2 on line 4. The reader reads a check fault and no words fault, so cr_2 "stands". Probe `r6/n160_m125.py` shows `_words_fault_on` False and `_CHECK_FAULT` True. The door asked a respecify only because `_same_words` was False on that row. With the ruled text unchanged, the door admits cr_2 with the words he faulted. This wall predates 0798ac8d. Fix: accept "should just say" and "line N still isn't right" in `_WORDS_FAULT`, with night 160's sentence as a red test.
2. `rota/roles/api.py:5462` `_drops_whole_line`. Low. CONFIRMED. Night 142's r_m37 "I meant to drop lines 3 and 4 from your page" reads no drop, because "I meant to" is not a request lead. At 46471ca4 it read a drop. "Drop line 5 but keep line 4." also reads no drop. Each case stalls on a respecify demand and does not leak. Fix: remove "but" from `_NARROW_TAIL`, and read a drop when no lead negates it.
3. `rota/core/sandbox.py` respecify door, review 5's F3. Low. CONFIRMED. The behaviour is unchanged at 0798ac8d. Fix: refuse `criteria.respecify` when `ruling_drops_line` names the line of the criterion.

Outside the points:

- `_DROP_LINE` misses "remove only line 8" in night 142's r_m144. The pattern needs the line right after the verb. Low. This predates the frame.
- The branch head moved to b57793c0 after the brief was written. The patches still apply there.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0cdcac52-3588-4266-b1fb-fc5d7d31b805/scratchpad/r6/`.

- `test_r5_drop.py`, `test_r5_keep.py`, `test_r5_resp.py`: review 5's probes, run from the worktree with `--rootdir .`. 15 passed.
- `sweep_drop.py` and `sweep_drop.txt`: every `_DROP_LINE` hit of nights 140 to 159, with the `_drops_whole_line` verdict.
- `sweep_all_r6.py` and `sweep_all_0798.txt`: pass 3d's per-criterion sweep at 0798ac8d, compared with `sweep_3c.txt` and `sweep_3d.txt`.
- `n160_paths.py` and `n160_paths.txt`: night 160's `order:` rows and each contested reading on both paths.
- `replay_n160.py`, `replay_n160_record.txt`, `replay_n160_fallback.txt`: the wake replay of night 160's twelve relay sessions on both paths.
- `n160_m125.py`: the predicates of cr_2 and cr_3 at the wake of m125.
- `patches/`, `head.tar`, `head/`: the four patches, the archive of b57793c0, and the patched copy with its three test files run.

## (d) Usage

About 75k tokens in total, measured from the session budget. This is over the cap of 25k. The split into input and output tokens is not available. No sub-agent ran.
