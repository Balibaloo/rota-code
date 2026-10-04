# Night 115: the walk of frame 119 at 56f8d30

Read by an Opus agent for 5e8ace65 on 2026-10-04 from `.rota/clickI_night115.db`, the report, the log, and the baselines `.rota/clickI_night113.db` (cold, 6ff6fd0) and `.rota/clickI_night114.db` (warm, 52e9ee8).
Seat behaviour is the rota workflow. `_fit`, the cut notes and the repeat line are the runner, the meta workflow.
The night ran 06:45 to 08:16, 203 sessions, 833 turns, and ended `Stuck. The team gave up on: reconcile for @prose:docs/parameters.md, challenge for @claim:constraints:click_paramtype, tests_failing for echo_json_compact_batch` (observed: night115.log, 2026-10-04).
Scripts: `m108.py`, `cuts.py`, `turns.py` from the night 113 read, and the new `n115b.py`, `n115d.py`, `n115e.py`, `n115f.py`, `n115g.py`, `n115w.py`, all in the session scratchpad.

## 1. Frame 119's measure

The first fact: night 115 did not exercise the Developer path frame 119 built. No Developer wake was over half the budget. The largest turn 1 was 10,635 characters against a half of 13,548. On night 113 every `tests_failing` wake was 18,182 (observed: turn 1 sizes by role, 2026-10-04). The batch did not break its own import this night, so `tests.load` held one red row and not 34.

(a) Turns with the dropped notice, no middle results block, and a tail reply over a third of the budget (observed: m108.py, 2026-10-04):

| night | all turns | Developer turns | Developer sessions |
|---|---|---|---|
| 113 | 8 | 4: s153 t16, s154 t16, s155 t5, s156 t8 | 10 |
| 114 | 16 | 4: s153 t9, s246 t6, s248 t9, s249 t6 | 28 |
| 115 | 14 | 3: s130 t15, s130 t16, s139 t5 | 10 |

The other 11 turns on night 115 are s24 t4, s32 t5 and s73 t4 to t12, an Architect survey.

(b) The wake took half in 8 turns, all in one session: s73, Architect, `tick:survey`, t6 to t13. Each notice reads `CUT your wake: 4,799 of 18,920`, so 14,121 kept against two thirds at 18,828 (observed: n115b.py, 2026-10-04). No Developer turn took half.
The block that half kept is not a read. At t6 the middle holds `[your reply of an earlier turn]` and `ERROR reply cut: your reply was cut at the output budget`, 332 characters. At t5, at two thirds, the middle held nothing (observed: the prompts of s73 t5 and t6, 2026-10-04). `keeps_a_read` asks only for a `_RESULTS` kind, and the runner's reply-cut note is a `_RESULTS` block (reasoned: runner.py, `_fit`, from the prompt and not from a replay). So the share cost 4,707 characters of source for no read.
s73 was already in a loop at t4: one `surveys.attest` with the same citations repeated, 34,500 characters per reply, cut each turn (observed: s73 turns, 2026-10-04). The half share did not cause the loop.

Frame 108's cap on a Developer tail reply. A firing is a `CUT this exchange` note on the tail with a middle results block kept (observed: cuts.py, 2026-10-04):

| night | firings | cut tails with an empty middle |
|---|---|---|
| 113 | 0 | 4 |
| 114 | 6 in 3 sessions: s244 t5 t6 t7, s246 t3, s249 t3 t15 | 4 |
| 115 | 3 in 1 session: s134 t11 t13 t17 | 0 |

On nights 114 and 115 the cap landed on wakes under half, which were not cut. So frame 119 did not cause these firings (reasoned: the wake sizes above).

(c) Re-reads after a long reply. I read the turns of the three (a) turns and the cap turns (observed: turns.py, 2026-10-04).

- s130: t13 read utils.py 0-726 and the drops door refused a rewrite. t14 sent a whole-file `code.write` of 14,512 characters. At t15 the middle was empty, and t15 sent the whole file again, 14,151, which did not parse. t16 read 0-400 again. Yes. The wake was 4,985, 19% of the budget, so the cause is the whole-file reply and not the wake's size.
- s139: t1 and t2 were prose of 37,928 characters with no call. t3 read three spans. t4 to t6 were prose, `Wait, maybe the issue is...` repeated, with no call. No re-read. The cause is a prose loop.
- s134 t11 to t17: the cap kept a middle read in each firing. The seat still asked 348-379 two and three times per reply at t15 and t16, and met `unchanged since you asked` and the repeat line. I did not check that each copy was in view, so the cause stays open.
- Night 114: s153 re-read 687-702 at t11, which its window held at t8, after replies of 11,872 and 26,181. s246 held decorators.py 418-575 at t5, sent a 36,295 write, and read 470-575 at t6 to t8 (observed: night 114 prompts, 2026-10-04).

(d) The sentence (observed: n115d.py, 2026-10-04):

| night | old sentence beside the notice | new sentence beside the notice |
|---|---|---|
| 113 | 26 turns, 7 sessions | 0 |
| 114 | 31 turns, 9 sessions | 0 |
| 115 | 0 | 35 turns, 7 sessions (90 turns in all) |

The new line follows `not answered again.`, so the seat reads a refusal and an invitation in one line. Five readings:

- s33, Vision Keeper, reconcile. The t6 prompt equals night 113's byte for byte, except the sentence. The system prompt is equal and the temperature is 0. On night 113, t6 sent `surveys.attest` and the session closed. On night 115, t6 repeated its ten calls, and the runner ended the session on a verbatim repeat. s34 and s35 did the same, and the wake was quarantined (observed: n115w.py, 2026-10-04). The new sentence caused this wall.
- s133 t16 to t18: it asked once more, as told, three times. Each `code.write` was refused with the same line. It was never served. A loop.
- s28: it asked `code.source docs/index.md` again at t4 and t5, was refused, and stopped with no call. Night 113 attested at t6.
- s132 t15: refused on `tests.load`. It read once, wrote at t18, then sent the same write at t19 and t20, `already holds this text`. It acted, then looped.
- s138 t10: refused on `tests.load`. It read 348-379 and wrote at t13. It acted.

In none of the five did the window drop the block, so no serve came. The invitation pays only on an eviction, and it costs a loop when the block is in view.

(e) The reply cap at its floor. Night 115 has no Developer reply cut to about 1,000 characters. The smallest kept tail is 7,882 (observed: cuts.py, 2026-10-04). Night 114 has one: s249 t15 kept 930. Its next turn wrote another span, which did not parse, and t16 read 420-552 again. It did not repeat the lost write.

(f) The cut notice. No wake on night 115 was cut at turn 1. In s73 the turn 1 wake is 18,920 characters uncut. t2 prints `CUT your wake: 92 of 18,920 characters`. t6 prints `CUT your wake: 4,799 of 18,920 characters`. The total holds through a second cut. On night 113, s153 printed `29,483 of 47,547` at t1 and `118 of 18,182` at t2 (observed: the prompts, 2026-10-04).
The reply-cut retry uses `_render_cut(completion.text, 4000)`. So a cut reply prints `CUT your wake: ... Nothing returns a wake`, in 7 Developer turns on night 115 and 14 on night 114 (observed: n115b.py, 2026-10-04). That wording is false for a reply. It predates frame 119.

Verdict, three parts.
Mechanism: the Developer seat never met the half share. Its wakes were all under half. The one session that met it kept a runner note in place of a read (observed: (b)).
Ratio: 3 Developer turns in 10 sessions against 4 in 10 on night 113 and 4 in 28 on night 114. Dangling pointers are 65 of 833 turns in 11 sessions against 54 of 914 in 12 and 115 of 1,351 in 19 (observed: the three logs, 2026-10-04). The night does not prove the line, because its wakes did not reach the path.
Residue: s130 re-read after a whole-file write, with a wake at 19%. s139 looped in prose. Neither cause is the wake's size. The new sentence is a regression with its own cause: s33, s34 and s35 repeated at temperature 0 where night 113 moved on.

## 2. Frame 120: one traceback, many copies

`tests_failing` wakes that hold a `[code.source]` block: 2 of 7 on night 113, 15 of 21 on night 114, 8 of 8 on night 115. Most copies of one `said` text kept in one wake: 10 (s148), 14 (s145), 1 (observed: n115f.py, 2026-10-04). Night 115 has no batch red at import, so it does not test frame 120.

## 3. Frame 113: invented results

Developer sessions that wrote their own results: 9 of 10, 18 of 28, 7 of 10. Lines that copy a real line of the same prompt: 15 of 28, 33 of 66, 30 of 33. On night 115, s134 copied 16 of 16 and s133 9 of 9 (observed: n115e.py, 2026-10-04). The line under 5 is not met. Most lines on night 115 echo the runner.

## 4. Frame 114: inherited tests, and why the batch stuck

- No inherited or project test failed on night 115. The one red test is the Tester's `tst_echo_json_compact_3`. The drops door appears in 14 prompts in s130, s133, s138. `this write changes` and `has no criterion` appear 0 times (observed: LIKE over turns, 2026-10-04).
- 12 commits. Red per head: 0 of 34 at 6782ecd2bb, 3db2cfaae4, daa8ba09f8, then 1 of 37 or 38 at 892aa5072c, 53dc92fe67 and e3f3a83c5a (observed: report, test_runs, 2026-10-04).
- The cause is two tests that contradict. Under criterion `echo_json_compact_3`, `test_echo_json_raises_on_unrecoverable_error` needs a `CircularRef` with `self.ref = self` to raise `TypeError` or `ValueError`. `tst_echo_json_circular` needs the same class to print a JSON string (observed: the tests table, 2026-10-04). Code that passes one fails the other (reasoned: `json.dumps` raises `TypeError` there, and the `str(obj)` fallback then succeeds).
- s136 challenged at t15, m44, with the criterion's `or raise` clause. The Tester s137 tried to put a fixed test in `test_echo_json_3.py`, met `two tests in one file overwrite each other`, and put it in a new file. The old test stayed (observed: s137 turns, 2026-10-04).
- s138 caught `RecursionError` and `MemoryError`, with no effect. s139, s140 and s141 sent no call at all: prose about recursion, and the runner's `You wrote code into your reply`. No seat challenged a second time. The cycle fired at attempt 9 (observed: night115.log, 2026-10-04).

## 5. Frame 115: Architect answers

Night 115 has no Developer escalation and no Architect answer. Night 113: m71, no text. Night 114: m128, no text. `that is what the product does`: 9 turns in 4 sessions, 11 in 4, 9 in 4 (s77, s146, s160, s187) (observed: n115g.py, 2026-10-04).

## 6. Frame 116: one challenge per reply

Developer replies with more than one challenge or escalation: 1 of 7 on night 113 (s143), 1 of 21 on night 114 (s245 t9, by count, not read), 0 of 8 on night 115 (observed: n115g.py, 2026-10-04). The night held one Developer challenge in all, so the 0 says little.

## 7. Frame 117: empty stubs

Prompts with `[your reply of an earlier turn]` where the reply held a call: 14 prompts in 6 sessions, 98 in 20, 87 in 10 with 8 of them holding a call: s73, s130, s131, s132, s134, s135, s136, s138 (observed: n115g.py, 2026-10-04). Up from night 113.

## 8. New walls

- `reconcile for @prose:docs/parameters.md`. Vision Keeper s33, s34, s35, temperature 0. Each probed four patterns, read docs/parameters.md 0-400, and wrote `OK code.probe -> []` lines of its own from t3. At t5 the repeat line refused `code.probe`. At t6 each repeated its ten calls, and the runner ended it on `repeated its previous turn verbatim twice` (observed: n115w.py, 2026-10-04). Night 113 and night 114 ran one s33 on the same wake, the same to t5, and it closed at t7 with `ledger.log` and `surveys.attest`. The cause is the new sentence, section 1(d).
- `challenge for @claim:constraints:click_paramtype`. Critic s86, s87, s88. Each called `challenge.uphold` with a quote of `validate_count` that holds `"Should be a positive, even integer."`. From t2 it opened the quote with `"'''` and escaped the inner quotes, and the parser answered `unterminated argument list` at every turn until the session ended (observed: n115w.py, 2026-10-04). Nights 113 and 114 never had this claim. Their survey made other constraints, and the night diverged early, at s1 t3. Each had 2 Critic sessions with the same parse error and none was given up.

## 9. Night 114's merge

bg_2, `confirm_with_default_on_eof`, merged with one commit, 24feb33dfd by s189 at `tick:batch_start`, 37 of 37 passing on its first run, and a Critic verdict of pass (observed: night114_report.txt, 2026-10-04).
It never woke a `tests_failing` Developer. The batches that stuck went red after their first commit and did not leave that loop.
On night 115 the same item stayed `pending` with no commit, because the stuck wakes stopped the night first.

## Verdict

Frame 119's Developer mechanism is not yet measured, because no Developer wake reached half the budget (observed: section 1).
Two defects show on the night. The half share counts a runner note as a read in s73. The new sentence turned one closed reconcile into a quarantined one at temperature 0 (observed: sections 1(b) and 1(d)).
The batch stuck on two Tester tests that contradict, and the Developer seats stopped calling (observed: section 4). A night with a batch red at import is still needed for frames 119 and 120 (reasoned: section 2).
