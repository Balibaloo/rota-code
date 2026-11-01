# dry1's fourth wall: an exhausted batch has no restart from the seat (read, 2026-11-01)

Read only. Evidence: a copy of `.rota/dry1.db` in the probe directory, the checkout at 0245e1ff, `plans/stack.md`, the night reads 170 to 175. No model call, no gate, no rota run.

## Result

1. The cause. `bg_1` runs, its 34 tests pass, and the Tester's key `tester|tick:tests_missing|bg_1` is quarantined at 3 attempts. `given_up` lists the key, so `stopped_bouncing` and `parked` are true for the batch (observed: `tick_attempts` and `batches` in the copy; `rota/core/scheduler.py:1901-1919` and `2462-2497`). The ladder woke its three rungs, s149, s152, s155, so `_next_rung` is empty and `exhausted` wakes nobody more (observed: `sessions`; `rota/core/predicates.py:1129-1157`). `preempt` is the one predicate that parks a running batch with a spent ladder, and it returns before that branch when `next_batch` is empty: `next_batch` reads pending and deferred batches only, and dry1 has one batch (observed: `rota/core/predicates.py:1638-1654`, `rota/core/scheduler.py:1755-1760`). So the batch holds the seat as `running`, nothing wakes, and the status line says Stuck with "Nothing waits on you" (observed: `rota/roles/principal.py:471-484`).
2. The provenance. The park branch's order is from 9d2693db (2026-09-24, night 92's one order for the starter and the preempt). The spent-ladder park is from a6278c08 (2026-09-25) and ec33c1f7 (2026-10-26, frame 330, pass 5). The Stuck line's `ruled=False` read is from e51b540d and c7f3b8f3 (2026-10-31, frame 354, pass 5). The shift page is from 61a0f41d (2026-10-10, frame 193, pass 2), its waits text from cc013d96 (2026-10-24, frame 312). The rulings door's backing rule, which refused "1 now", is from 4d13a8d8 (2026-10-28, the seam's P7 pass 1) (observed: `git log -S`).
3. The reach. On nights 170 to 175, five of six nights ended with a quarantined running batch, and four named `tick:exhausted`: 170, 171, 172 and 175. The seat saw a stop page from `tick:quarantined` on 170, 172 and 175, a clarify and a shift page on 171, and no page on dry1. No page offered a restart of the stopped step (observed: the night reads, section 5 below).
4. The relation to frame 330. This wall is a part of frame 330, its last-item shape. Frame 330's site is `exhausted`, `preempt` and `parked`, its reach line names `tests_missing` among the nine keys, and night 170's read wrote "the shape cannot occur on the last item" because its red test needs a pending sibling (observed: `plans/stack.md:1693-1700`, `plans/night170-read.md:112`). With one batch the same park branch is never reached. The turn-8 refusal of "1 now" is a second, new cause at the rulings door, in the family of frames 265 and 292 (reasoned: section 2).
5. The fix at the source. Move the spent-ladder park in `preempt` above the `if not ranked: return []` exit, so a running batch that is parked with no rung left is deferred with or without a challenger (`rota/core/predicates.py:1638-1654`). The park then opens the park ask, the status line's parked line says "I ask you about it next", and the park page's contest is the restart (observed: `rota/roles/principal.py:430-452`, commit 0c6e54e2). Price 1 to 2 cycles, a predicate with a test. A second fix of 1 to 2 cycles at `_backed`, so a bare menu pair "1 now" names line 1, is needed before any shift answer in the menu form lands (section 2).

## 1. The cause

- `exhausted`, `rota/core/predicates.py:1023-1077`. It collects the batches with a failing run and every running batch, keeps the ones where `stopped_bouncing` is true, and wakes `_next_rung`. With no rung it wakes nobody (observed: lines 1065-1077).
- `stopped_bouncing`, `rota/core/scheduler.py:1901-1919`: true at `loop_cap`, or when `_running_given_up` lists a key. `_running_given_up`, lines 1922-1936, keeps a running batch's `given_up` keys that are not the Liaison's. For `bg_1` that is `tester|tick:tests_missing|bg_1` (observed: `tick_attempts`, `attempts 3, quarantined 1, reported 1`).
- `parked`, `rota/core/scheduler.py:2462-2497`: true for a running batch when a given-up key is not `tick:tests_failing`, line 2487. So `bg_1` is parked by the reader and still `running` in the table.
- `preempt`, `rota/core/predicates.py:1602-1658`. Line 1638: `ranked = next_batch(conn)`. Line 1639: `if not ranked: return []`. Line 1649: `if parked(conn, running["bid"]) and not _next_rung(...)`, the `do:park` wake with "its ladder is spent". The park waits behind the empty-list exit (observed).
- `next_batch`, `rota/core/scheduler.py:1741-1780`: `WHERE b.status IN ('pending','deferred')`. A run with one batch returns an empty list (observed: line 1759).
- The Stuck text, `rota/roles/principal.py:471-484`: `gave_up` reads `quarantined_keys(..., ruled=False)`, so a key with `reported = 1` is still a stall, and line 480 writes "Stuck: {words}. Nothing waits on you, and nothing moves until that is cleared. Tell me what to change." The words are `_gave_up_words`, line 2171. The parked line with "I ask you about it next", lines 430-452, needs a park ask, and no park exists (observed; reasoned: `keyed` holds parked batches with an ask).
- The quarantine wake: the `quarantined` predicate, `rota/core/predicates.py:1774`, reads unreported keys. s157 woke on it with detail "1 abandoned: tests_missing for bg_1 (tester), 3 attempts", called `msg.present_principal(refs=['bg_1'])` once, and committed. No message row holds that present: the messages about `bg_1` alone are m54, m57, m58, m64 and m67, all older and answered (observed: `tool_calls`, `turns`, `messages`). The door's exit for that call was not read within the cap. The commit set `reported = 1` on the key (`rota/core/loop.py:341-342`), so the wake never fires again.

## 2. The restart

- A new commit on the change. `_lift_quarantines`, `rota/core/db.py:961`, lifts the keys at a head commit. No seat wakes to commit, so the route is closed (reasoned).
- Words through `rota.tools.talk`. The tool writes a `converse` from the principal with no cause (`rota/tools/talk.py:83`), so m70 is a new request s2. `request_shift`, `rota/core/predicates.py:211-245`, asked the shift page about the earlier item. Its land, `_land_shift`, `rota/roles/principal.py:3878-3905`, writes one `item_parks` row for `park`, `now` or `drop` and lifts no key. A landed "1 now" would restart nothing (observed: the code; `item_parks` is empty).
- "1 now" on m72. The Liaison s170 and s171 each called `rulings.rule(rulings={'1': 'now'})` twice and were refused: "His words neither fault nor name line 1, so line 1 takes no now: the words start '1 now'" (observed: `tool_calls`, `turns` seq 4 of both). The writer is `_unbacked_approve.refusal`, `rota/roles/api.py:12495-12501`, reached from line 12544 when no row is backed. `_backed`, lines 12435-12462, backs an approve by agreement words, a contest or a revise by fault words, and any other verdict by a named line. `_line_reading("1 now", 1)` names no line, and so for "1 ok", "1 drop" and "1 later", on the checkout and at the parent of 3668fd4f alike (observed: the probe, section 7). The quantity rule of 3668fd4f is not the cause. Every shift answer in the menu form is refused by this door today (reasoned: the three menu words are neither agreement nor fault words).
- The step page's "try again". `rota/roles/principal.py:2947` offers it, and `land` lifts the key with `lift_keys`, line 3384, for a key in `steps`. `steps` are the rowless keys of the page, line 3327 and `rowless_key`, `rota/core/scheduler.py:1873`. The Tester's key names `bg_1`, a batch, so it is not a step. Its page from s157 never landed, and its flag is set, so no page shows it (observed).
- `lift_on_red_move`, `rota/core/db.py:1301`, resets a `tests_failing` key when the red moves. The key here is `tests_missing` (observed).
- The `do:park` route: never fires with one batch, section 1.

## 3. The reported flag

- Set to 1 by `rota/core/loop.py:341-342` for every quarantined unreported key when a `tick:quarantined` session commits. Set to 2 (`RULED`) by `mark_ruled`, `rota/core/db.py:1080-1087`, on his drop of a step.
- Read by `quarantined_keys`, `rota/core/scheduler.py:1851-1852`: `unreported=True` for the wake, `ruled=False` for the Stuck line.
- Cleared by `forget_keys`, `rota/core/db.py:1090-1095`, through `_lift_quarantines`, `lift_on_red_move` and `tick_slicing`, and by `lift_keys`, line 1071. Nothing clears it for this key today (observed: callers by the map tool).
- A cleared flag wakes the Liaison again with refs `['bg_1']`, as s157. The page would show the batch, and the key is not a step, so no "try again" line applies to it (reasoned: `rowless_key` and `steps`). A cleared flag alone is not the restart.

## 4. Provenance

See Result 2. Frames: 330 holds `exhausted`, `preempt` and `parked`, parked by 77c8dc39 with reach "1 of 10 after pass 4" (observed: `plans/stack.md:1693-1700`). Frame 265, "Now." lands as `later`, waits on a count (observed: `plans/stack.md:2163`). Frame 292, the shift door checks the word before the line (observed: line 2364). Frame 312 wrote the shift page's stuck words (archive, line 496). Frame 354 wrote the step page and `RULED` (archive 2026-11-01, line 37). The rulings seam's P7 pass 1 wrote `_backed` (commit 4d13a8d8).

## 5. Reach

From the night reads, `plans/night17*-read.md`:

| Night | Exhausted batch | What the seat saw |
|---|---|---|
| 170 | b_3, `tick:exhausted` three seats, then `tick:quarantined`; no pending batch (line 97, 112) | a stop page naming "tests_missing for b_3"; no retry |
| 171 | review key, s131, s134, s136; bg_1 held by `tests_failing` in walk 1 (lines 37, 129) | clarify m40 and a shift page; "later" deferred bg_1 |
| 172 | bg_3, s246 to s253 (line 109) | m120 "The team stopped work on this change"; no retry |
| 173 | bg_3 quarantined, no pending batch; the ladder not named (line 130) | the Stuck line for a claim, W2 |
| 174 | none named | none |
| 175 | s258 to s277 `tests_missing` then `tick:exhausted` (line 46) | stop pages from `tick:quarantined` s280 to s337, rulings to the Terminologist; no retry |

Four of six nights reached `tick:exhausted`, five ended with a quarantined running batch, and no page offered the batch's step again. The night databases were not opened: the reads named the count.

## 6. The fix lines

1. Source: `preempt`, `rota/core/predicates.py:1638-1654`, park a spent-ladder running batch before the challenger exit. 1 to 2 cycles. Covers the status line, the park ask and the shift page, because all three read the park.
2. `_backed`, `rota/roles/api.py:12435-12462`: a bare "N word" pair with a menu word names line N. 1 to 2 cycles with a test. Needed for any shift answer to land.
3. Door text: the gave_up Stuck line, `rota/roles/principal.py:480`, names the route. 2 cycles. Covers one door.
4. Steps: a batch key as a step with "try again", `rota/roles/principal.py:3327` and `lift_keys`. 1 to 2 cycles. Needs the flag cleared first, so not at the source.

## 7. Probes

In `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/3b83d22b-0033-48d3-816a-f69a7fe15544/scratchpad/dry1w4/`: `dry1.db` and `dry1.db-wal` copies, `probe1.py` to `probe6.py` (batches, keys, sessions, messages, the s170 and s171 turns, s157's calls), `old/rota/` with `api.py` at the parent of 3668fd4f for the `_line_reading` probe.

## 8. Usage

One agent on Opus, no sub-agents. Four map calls, 14 bash probes. About 58k tokens at the write.
