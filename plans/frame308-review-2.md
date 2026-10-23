# Frame 308, review 2: pass 2 at 541bb828

Reviewer on Opus, read-only, worktree `C:/Users/roman/rota_r308` at 541bb828, parent 27947b6f.

The verdict: do not accept as it stands. One fix is needed first (F1). The door creates no hang. But the door opens again at turn 2 for s382 and s387, and the old text then goes to the Tester.

## (a) The claim, point by point

1. Point 1, the fate of a refused session: CONFIRMED, no hang. A corrected respecify is available to all five seats, but it reopens the wall for two of them (F1).
2. Point 2, answers with no respecify tried: CONFIRMED, 0 of 15. Three ruled sessions tried no respecify and sent no answer.
3. Point 3, the text key: CONFIRMED, the key misses two routes (F1, F2). `msg.answer_developer` is not gated (F4, PLAUSIBLE).
4. Point 4, nothing else changed: CONFIRMED. Four files change, 2 recorded cases go STALE, and `test_roles_doc` is red at 27947b6f.

### Point 1 in detail

The prompt of each seat shows the right surface. `src/click/decorators.py::version_option` is in `[code.callables]` of turn 1 for s370, s382, s387, s398 and s412. It is also the surface on file, because no criteria write follows s349 (`receipts`).

The refusal of the door quotes the surface refusal. The seat keeps its turns, because `outbound` stays empty (`runner.py` 5459). So the seat can retry. The probe `retry_wake.py` replays turn 1, then sends the own text of the session with the right surface, against the rulings as they stood at each wake:

| Session | Retry with `version_option` | Answer after the retry |
|---|---|---|
| s370 | lands | admitted, criterion written |
| s382 | refused, "the principal contested these words ... Write what he asked for. Send his words about the check to the Tester with msg.answer_tester" | admitted, no criterion written (F1) |
| s387 | refused, the same branch | admitted, no criterion written (F1) |
| s398 | lands, his words | admitted, criterion written |
| s412 | lands, his words | admitted, criterion written |

When the session ends with no answer and no write, the relay closes. `relay` is not in `OWED_A_REPLY` (`rota/core/db.py` 671). So the barren session reaches `elif not (barren and was_unresolved):` and the update to status answered (`db.py` 1046 to 1049). No predicate wakes another Terminologist on that relay. No Tester wakes, because no answer goes out and no criterion version moves. The batch waits.

The batch does not hang more than before. The five rulings came from `tick:agenda` wakes s379, s384, s389, s394 and s400. Those wakes read ledger rows that s186, s264, s274 and s280 wrote (`receipts`), not the answers. So the next page on `ver_opt_show_py` comes as it came on night 159 (PLAUSIBLE: the agenda drains, 22, 21, 20, 14, 9 rows). Before the change, the Tester woke on the old text and every encode was refused (s383 t2 to t5). So the old answer bought no progress either.

### Point 2 in detail

The probe `p2count.py` reads every Terminologist relay session of both nights whose relay rules a criterion `contest` or `revise`. 22 sessions match, and 15 answered the Tester. Each of the 15 called `criteria.respecify` before or in the turn of the answer. So 0 answers went out with no respecify tried. s172, s397 and s404 tried no respecify and sent no answer (outside the door).

### Point 3 in detail

The answer to the Tester has one route, `msg.answer_tester`, behind `_ruling_answer_door`. The mode `criterion_repair` also offers `msg.answer_developer` and `msg.challenge_vision_keeper`. The door misses these failed repairs:

- A respecify refusal that names `msg.answer_tester` and also asks for new words. The branch at `api.py` 5818 says "Write what he asked for" and then names the answer (F1).
- A respecify refused by the argument check in `Sandbox.call` (F2).
- A respecify that returns `unchanged` and writes nothing (`api.py` 5825). That return raises nothing, so the door has no record (F3, PLAUSIBLE).

### Point 4 in detail

`git diff 27947b6f 541bb828 --stat` shows four files: `rota/core/sandbox.py`, the brief `criterion_repair.md`, and two test files. The sandbox hunks are the wrapper in `build` (745 to 747), the new check in `_ruling_answer_refusal` (1576 to 1615), `_failed_respecify` (1624 to 1643) and `_respecify_record` (1646 to 1664). The old missing-refs route keeps its effect, and `_parked` keeps the same query. No graph file changes.

The brief edit makes 2 recorded cases STALE. The probe `stale.py` composes all 162 single cases, and 2 hold the new sentence: `L1-TE-a-ruled-criterion-is-respecified-and-the-tester-told` and `L1-TE-repair-the-criterion-the-tester-cannot-encode`. The 4 chains that name the Terminologist start on other modes.

The test `test_roles_doc.py::test_a_verb_carries_words_or_does_not_regardless_of_recipient` is red at 27947b6f. The test reads only `graph.json`. The files `graph.json` and `graph.py` are the same at both commits. The probe `edges.py` runs the predicate of the test on `graph.json` of the parent. The verb `answer` splits: the edges tester to developer and tester to critic carry prose, and 15 other `answer` edges do not.

## (b) Findings

1. **F1. The words refusal turns the door off.** `rota/core/sandbox.py` 1638 and 1661. Night high, frame high. CONFIRMED: `retry_wake.py` on s382 and s387. The seat corrects the surface and meets the branch at `rota/roles/api.py` 5818. That refusal names `msg.answer_tester`, and it overwrites the surface refusal in `ctx.respecify_refused`. Then `_failed_respecify` skips the criterion, and the answer with the old text is admitted. This is the night 159 wall one turn later. Fix: exempt only the refusals at `api.py` 5702 and 5813 by a flag on the exception, and count every other refusal.
2. **F2. An argument refusal is not recorded.** `rota/core/sandbox.py` 550 to 560 against 1646. Night low, frame low. CONFIRMED: `argpath.py` on s382. A respecify with no `text`, or with an unknown argument, raises `ArgumentError` in `Sandbox.call` before the wrapper runs. The record `respecify_refused` stays `None`, and the answer is admitted with no write. Fix: key the door on a respecify call of the ruled criterion with no landed write.
3. **F3. The `unchanged` return is no refusal.** `rota/roles/api.py` 5825 to 5830. Night low, frame low. PLAUSIBLE: by the code, a same-words call under a ruling whose contested text differs from the row returns `unchanged` and raises nothing. The door then sees no failed repair. Fix: the F2 fix covers this case too.
4. **F4. The answer to the Developer is not gated.** `rota/core/sandbox.py` 758 to 759. Night low, frame low. PLAUSIBLE: `criterion_repair` offers `msg.answer_developer`, and the wrapper sits on the Tester answer only. No session of night 158 or 159 took that route under a ruling. Fix: none now. Record it as a known gap.
5. **F5. The new refusal names a call outside `_offer`.** `rota/core/sandbox.py` 1604 to 1608. Night low, frame low. CONFIRMED by reading: the text names `msg.answer_tester` with refs, but it records no offer. So the follow check of frame 144 (`sandbox.py` 563, `offers or facts`) never reads it. Fix: build the text with `api._offer` on `criteria.respecify`, with the answer in `then`.
6. **F6, outside. The replay reads the rulings of the end of night.** `replay308.py`. Night low, frame low. CONFIRMED: `retry.py` quoted the later ruling "Line 3 is still wrong ... Please remove line 4" for s382. The probe `retry_wake.py`, with the rulings cut at the wake, quoted r_03b3346468. The turn-1 counts hold, because the surface door fires before any ruling is read. Fix: cut `rulings` to the wake in the replay before any count past the first refusal.
7. **F7, outside. A new text that keeps the contested sentence lands.** `rota/roles/api.py` 5788. Night low, frame low. CONFIRMED: `retry_wake.py` on s370. The text of s370 keeps "exits cleanly and prints nothing", which the principal contested, and the retry lands. The same-words check reads whole texts only. Fix: route it to the frame that holds the 5788 gap of `plans/frame306-w1-hop.md` (e).

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b85289fd-418f-43a1-a641-15dad2620cfa/scratchpad/r308b/`. Each opens the night databases with `?mode=ro` and works on a copy in memory. No probe calls a model.

- `p1.py`: dumps the turns of s382, night 159.
- `p2.py`, `p3.py`: the messages m200 to m256 and the sessions s368 to s400, night 159.
- `p4.py`, `p5.py`, `p6.py`: the calls of Tester s383, the ledger rows, the batches, `ver_opt_show_py` and `receipts`.
- `retry.py`: turn 1 of five sessions on 541bb828, a retry with `version_option`, then the door. It uses the rulings of the end of night (F6).
- `retry_wake.py`: the same, with `rulings` cut to the wake at rowids 46, 47, 48, 50 and 52.
- `argpath.py`: two respecify calls that fail the argument check on s382, then the door.
- `p2count.py`: point 2 over every ruled Terminologist relay session of nights 158 and 159.
- `stale.py`: composes the 162 single cases and finds the 2 that hold the new sentence.
- `edges.py`: the predicate of `test_roles_doc` on `graph.json` of 27947b6f, through `git show`.
- `pytest -n 0` on `tests/rota/test_frame308_answer_after_respecify.py` and `tests/rota/test_frame308_ruling_answer.py`: 19 passed.

## (d) Usage

The harness gives no counter. The estimate is about 100k input tokens and about 12k output tokens, about 112k in total. No sub-agent ran.
