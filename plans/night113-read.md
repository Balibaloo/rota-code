# Night 113: the walk of frame 108 at 6ff6fd0

Read by an Opus agent for 5e8ace65 on 2026-10-04 from `.rota/clickI_night113.db`, the report, the log and `.rota/clickI_night109.db`.
Seat behaviour is the rota workflow. `_fit` and its cap are the runner, the meta workflow.
The night ran 03:00 to 04:06, 228 sessions, 914 turns, and three walks each ended `Stuck. The team gave up on: tests_failing for bg_1` (observed: night113.log, 2026-10-04).
Every session ran at num_ctx 16384 on both nights (observed: `sessions.num_ctx`, 2026-10-04).

## 1. Frame 108's measure

Definitions. The budget is `_fit_budget(16384, len(system))` per turn, 26,185 to 32,522 characters. The tail reply is the previous turn's `completion`.
"No middle results block" means no line that starts `OK <fn>` or `ERROR <fn>` between the end of the `dropped to fit the window` notice and the start of the tail reply in `turns.user`.
The scripts are `m108.py`, `cuts.py`, `room.py` and `replay.py` in the session scratchpad. The same scripts ran on both databases.

(a) Turns with the notice, no middle results block, and a tail reply over a third of the budget (observed: m108.py, 2026-10-04):

| night | turns | Developer turns | other turns |
|---|---|---|---|
| 109 | 21 | 18 in 15 sessions: s146 t19, s147 t4 t11 t22, s152 t11, s192 t5, s196 t8, s198 t4, s199 t13, s203 t11, s208 t4, s209 t20, s210 t18, s211 t11, s216 t5, s218 t24, s219 t9 t14 | 3: s24 t4, s32 t5, s69 t4 |
| 113 | 8 | 4: s153 t16, s154 t16, s155 t5, s156 t8 | 4: s24 t4, s32 t5, s69 t4, s194 t6 |

The night held tail replies over a third of the budget: 19 turns, the largest 38,592 characters at s32 t4 against 29,033 (observed: m108.py, 2026-10-04). So the night exercised the path.
Night 113 had 10 Developer sessions and night 109 had 35, so the fall from 18 to 4 Developer turns is mostly fewer sessions (observed: `sessions`, 2026-10-04).

Why the cap did not save a read in the eight turns:

- Developer turns. The wake is 18,179 characters in every one, two thirds of 27,096, cut at `wake_room` (observed: room.py, 2026-10-04). The tail then gets 9,032 at least, and wake plus tail is 27,213, over the budget. No trial pack can keep a middle read, so the cap never lands on a Developer turn with a full wake (reasoned: `_cap_tail_reply` arithmetic, runner.py:698-724).
- s24 t4. The results block was 43,524 characters, cut to 11,196 by `_cap_exchange`. A replay of the turn rebuilt from s24 t3 gives the recorded prompt byte for byte with the cap off. With the true results size the trial pack keeps no read, so the cap declines by design (observed: replay.py, 2026-10-04).
- s32 t5, s69 t4, s194 t6. Each results block was also cut: 14,640, 23,412 and 21,938 characters (observed: cuts.py, 2026-10-04). The prompts of s32 t5 and s69 t4 equal night 109's byte for byte, so the cap did not change them (observed: cmp.py, 2026-10-04).

(b) The cap fired in 4 turns in 2 sessions. A firing is a `CUT this exchange` note whose total equals the tail reply's length, with a middle results block kept and the prompt under the budget (observed: cuts.py, 2026-10-04).

| turn | reply | kept | prompt / budget | middle read survived |
|---|---|---|---|---|
| s32 t9 (vision_keeper) | 27,679 | 8,563 | 21,701 / 29,033 | yes, `code.source` core.py 168-205 |
| s32 t10 | 23,579 | 7,963 | 24,648 / 29,033 | yes, the same span |
| s196 t4 (architect) | 32,914 | 10,936 | 19,654 / 27,679 | yes, no block dropped |
| s196 t5 | 32,814 | 11,296 | 23,245 / 27,679 | yes, no block dropped |

On night 109, s32 t9 had a 29,031-character prompt and `_cap_exchange` cut the reply to 19,074 (observed: cuts.py, 2026-10-04). Night 109 has no cap, so its baseline for (b) is 0.

(c) Re-reads after a long reply emptied the window. I read the turns of the eight (a) turns and the four (b) turns (observed: turns.py, heads.py, `_source_spans`, 2026-10-04).

- s156: t7 held utils.py 1-20, 1-50 and 674-696. The t7 reply was 29,773 characters with three whole-file writes. At t8 the middle was empty. t8 called `code.source(path='src/click/utils.py', start=1, end=20)` again, the same call as t5, and t9 called 1-50 again, as at t6. At t9 the runner answered `asked three times this session ... The answer is in this prompt.`, and the prompt held no real copy. Yes, a re-read caused by the long reply.
- s153: t15 held utils.py 670-710. The t15 reply was 10,928 characters, a list of the tool catalogue. At t16 the middle was empty. t17 read 674-696, a span inside 670-710. Yes, but s153 had read 674-710 three times before t15.
- s154: t15 held 1-30 and 674-696. The t15 reply was 22,756 characters. At t16 the middle was empty, and the seat read 1-50 and 674-690 again. Yes.
- s155 t5: the middle held no head at t3 to t5 before the long reply, so nothing was lost.
- s32 and s196, where the cap fired: each re-read with the read in view. s32 repeated `code.probe` and `code.source` 168-205 from t4, before any eviction, with 18 to 24 invented results per reply. s196 t4 re-asked the t3 calls whose results stood in its tail. The cause is a repetition loop, not eviction (observed: turns, 2026-10-04).

Verdict: the night exercised the path. The cap fired 4 times and each kept a read. The Developer re-reads in s153, s154 and s156 remain, and the cap cannot reach them while the Developer wake takes two thirds of the budget. That is a new wall, section 7.

## 2. Frame 113: invented results

- 9 of 10 Developer sessions wrote their own tool results: s131, s141, s143, s146, s148, s153, s154, s155, s156. Only s151 did not (observed: `nightcount.FABRICATED_RESULT` over completions, 2026-10-04). Night 109: 29 of 35. The line asks under 5.
- 15 of 28 lines in Developer sessions copy a real result line from the same prompt (observed: echo.py, 2026-10-04). s143's one line is an `OK code.commit`, and its commit 3945a33c6a landed and broke the suite.
- vision_keeper 15 is not new. Night 109 reads 13, night 112 reads 14 (observed: night109.log, night112.log, 2026-10-04).
- s115: `OK problem.assert -> {"id": "echo_json"}` and `OK ledger.log -> {"id": "l_1f93775f9a"}` at t6 to t8, 6 of 8 copied from the prompt. s169: `OK problem.set_approval -> unchanged since you asked earlier...`, a copy of the runner's line. s202: `ERROR decisions.author: asked three times...` and `OK decisions.search -> id | author | headline | supersedes`, 9 of 9 copies (observed: f117.py, 2026-10-04). The seat echoes the runner's lines after its calls.

## 3. Frame 114: inherited tests and bg_1

- c11de9f538 (s131): 2 of 37 red, `inh_echo_json_01` and `inh_echo_json_02`, Tester tests with an `inh_` id (observed: test_runs, 2026-10-04).
- 3945a33c6a (s143): 37 of 37 `error`. s143 wrote `echo_json_command` with `@click.command()` into utils.py, and the conftest import failed with `NameError: name 'click' is not defined` at utils.py:704.
- 537e5f2281 (s146): s146 added `from . import click` at line 1 to fix the NameError. The suite then failed with `cannot import name 'click' from partially initialized module`, 37 of 37.
- 61fd02488c and b16ded808b (s153) removed `echo_json_command`. Line 1 stayed, so 37 of 37 stayed red. 61fd02488c has no test run.
- s155 named the cause in its commit message, `Fix circular import by removing from . import click`. Its whole-file rewrites met `this rewrite of src/click/utils.py drops` in 14 turn tails. Its span write at 674-690 came back `already holds this text`, and its commits came back `committed: False, why: nothing changed` (observed: s155 t9 to t15, 2026-10-04).
- s156 read lines 1-20 and 1-50 ten times, the span that holds the import, and wrote nothing that landed (observed: tool_calls, 2026-10-04).
- The drops door appears in 23 prompts in Developer sessions s131, s153, s154, s155 and in s87. `this write changes` appears once, at s154. `has no criterion` and `reaches the dynamic` appear 0 times (observed: LIKE over turns, 2026-10-04).
- bg_1 ended on `developer|tick:tests_failing|bg_1 attempts=3 quarantined=1 reported=1`. The cycle detector fired at attempt 6 (observed: report, night113.log, 2026-10-04). This is night 112's shape a third time: the batch breaks its own utils.py import, and the drops door refuses whole-file repairs.
- Correction, 2026-10-05: s146 did not add `from . import click` at line 1. It sent `start=0, end=15`, and the write replaced the 15 header lines of utils.py with that one line (observed: `plans/frame136-design.md`, 2026-10-05).

## 4. Frame 115: Architect answers

- One Architect answer to the Developer, m71 from s149, answered m69. `body_text` is NULL (observed: messages, 2026-10-04). m66, s143's escalation, got no answer.
- s149 then sent `msg.answer_developer` three more times. The door refused the first repeat with `saying it again with different refs`.
- `that is what the product does` appears in s74, s174, s201 and s226, from turn 2 of each, 9 prompts (observed: LIKE, 2026-10-04). Night 109 had 4 refusals and night 112 had 0.

## 5. Frame 116: one challenge per reply

- 7 Developer sessions woke on `tick:tests_failing`: s141, s143, s148, s153, s154, s155, s156 (observed: report, 2026-10-04).
- s143 is the one session with replies that attempt more than one: t6, t7 and t8 each sent two `msg.challenge_tester` and one `msg.escalate_architect`. m65 (t4) and m66 (t5) had already landed, so all nine were refused (observed: s143 turns, 2026-10-04). s153 t15 names three msg tools in a catalogue list with no arguments, and that is not an attempt.
- s143 met the cr_3 refusal `you sent challenge to tester on exactly these refs already (m64)` at t7, t8 and t9: three times. The ratio is 1 of 7 on both measures, against 1 of 21 on night 112.
- After the refusals s143 wrote `echo_json_command` and committed 3945a33c6a, the commit that broke the suite.

## 6. Frame 117: empty stubs

14 prompts in 6 sessions hold `[your reply of an earlier turn]`: s70, s131, s142, s143, s153, s155. In all 6 the original reply held a `TOOL:` call (observed: stubcount.py, f117.py, 2026-10-04).
In s131, s142, s143, s153 and s155 the first stub is readable and its stub stubs to nothing. The calls are `code.write`, `tests.encode` and `msg.challenge_tester` with long arguments. s70 t1's `surveys.attest` reply did not parse at all.
Baselines by the same script: night 109, 79 prompts in 22 sessions, 20 with a call. Night 112 from s252, 18 prompts in 8 sessions, 7 with a call.

## 7. New walls

- The Developer wake takes two thirds of the window. On `tick:tests_failing` it is 18,179 of 27,096 characters, so a tail over about 9,000 empties the middle, and frame 108's cap cannot act (observed: room.py, section 1; reasoned: runner.py:898-900). No frame names this.
- Dangling pointers: 54 turns in 12 sessions. s153 (12), s155 (9) and s156 (8) are Developer sessions under that wake. The runner's `unchanged since you asked` and `asked three times ... The answer is in this prompt.` are written one turn before an eviction. s156 t9 is the clear case. The code says so at runner.py:3284-3291.
- Repeats: 5 wakes, 11 sessions. [s141, s143], [s148, s153] and [s154, s155, s156] are bg_1 attempts on red trees. [s132, s138] is one Tester `tests_missing` tick: s132 asked the Terminologist in 4 turns, and s138 encoded the tests. [s159, s165] is a vision_keeper signoff that submitted `echo_json_compact_01` to the Liaison twice, one turn each (observed: `nightcount._repeats`, tool_calls, 2026-10-04).

## Verdict

The path ran, and the cap did what it was built to do in 4 of 4 firings (observed: section 1). The measure falls from 21 to 8 turns. The fall is mostly the smaller Developer count, and the 4 Developer turns left are out of the cap's reach by construction.
Frame 108's mechanism holds. Its residue has a different cause, the Developer wake at two thirds, and that cause is a new frame (reasoned: the three-part rule).
