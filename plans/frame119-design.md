# Frame 119: the Developer wake takes two thirds of the window

Design read. Written by an Opus agent for 5e8ace65 on 2026-10-04 from `.rota/clickI_night113.db`, `tests/rota/cassettes.db` (read-only) and `rota/core/runner.py` at 247d0d7. Seat behaviour is the rota workflow. `_fit` and the push are the runner, the meta workflow. Scripts: `f119a.py` to `f119f.py` in the session scratchpad.

## 1. What the wake holds

The wake is built in two places. `push_working_set` (runner.py:2023) shapes `tests.load` for `tick:tests_failing` at runner.py:2202-2264. `build_prompt` (runner.py:334) renders each pushed key at `PUSH_CHARS` = 20,000 at runner.py:420. `tests_load` is api.py:5562-5645.

Every Developer `tests_failing` session on night 113 has a first prompt of 18,182 characters: 18,064 kept (`wake_room` = 27,096 * 2 // 3) plus the cut note (observed: f119a.py, 2026-10-04). Uncut, the wake is 47,547 at s153 and 46,961 at s154. It is 47,123 at s155 and s156 (observed: the cut notes).

Blocks of s153's uncut wake, in order (observed: f119b.py, f119d.py, 2026-10-04, unless marked):

| block | chars | after the cut |
|---|---|---|
| head: wake kind, refs, attempt line, "Already run" | 330 | kept |
| `batches.expect`: the item and the 37 test ids and paths | 3,913 | kept |
| `code.diff` | 2,167 | kept |
| `criteria.load` | 839 | kept |
| `references.load` | 22 | kept |
| `tests.load`: thread 887, own 3 red rows 4,306, project 34 red rows 28,734 | about 34,100, cut by `PUSH_CHARS` to about 20,130 | 10,780 kept: thread, own, about 6 project rows |
| `code.source` of what the own tests import | about 20,150 | all cut |

The `code.source` size is the remainder, 47,547 less the other blocks (reasoned: subtraction, consistent with a second `PUSH_CHARS` cut). The window cut removes 29,483: about 9,350 of project rows and all of `code.source`. No task text, history or door note is in the wake. The thread is the only message block.

## 2. Copies and growth

- All 37 runs at 3945a33c6a, 537e5f2281 and b16ded808b have one output each, byte-identical: 576 or 726 characters raw, 769 escaped in JSON (observed: f119c.py, `test_runs`, 2026-10-04). So the same traceback repeats 37 times, 3 in the own rows and 34 in the project rows.
- The project rows grow with the batch: 34 rows of 838 characters each, 28,734 in all. One copy of the traceback and 34 ids with paths is about 3,200.
- The kept wake holds 9 to 10 copies of that one traceback, about 6,900 characters, and 8 to 9 of them say nothing new (observed: f119b.py, 2026-10-04).
- `code.diff`, `batches.expect`, `criteria.load` and `code.source` return the same with one call. `tests.load` asked again is 34,100 characters, cut at `RESULT_CHARS` 6,000, so the thread and the red rows are the only usable copy (reasoned: runner.py:444, :1148-1175).
- The seat's re-reads target `src/click/utils.py` 1-20 and 1-50, the span with the bad import. The cut `code.source` push was the nearest copy of utils.py (observed: s154 t13-t15, s156 t5-t7).

## 3. Why two thirds

b8c18fe, 2026-08-24, `fix(sandbox): a pushed read is the wake, ...`, set `wake_room = (budget * 2) // 3` with the comment "a source push the size the area deserves is most of it" (observed: git log -S, 2026-10-04). The case was a survey's 13,726-character `code.area` push, `rota/ONBOARDING.md:410-417`. It was reasoned, not measured. The budget then was two thirds of the window at 4 characters per token. Later it fell to half at 3.97 (observed: `_fit_budget` docstring, runner.py:762-775, and `plans/archive/fit-overrun-read-2026-09-25.md:115-116`).

`DECISIONS.md`, `LAWS.md` and `plans/operating-facts.md` hold no ruling on the share (observed: grep, 2026-10-04). Frame 108's decision 1 depends on it: "One third pairs with the wake's two thirds, so a wake and a tail at their caps still fit" (observed: `plans/frame108-design.md:22-25`). Frame 108 ruled that a share comes from the budget and never from the middle, because a cap sized from the middle is circular. The two shares fit, but they leave the middle zero, and the separators make the sum 117 over.

## 4. Options

Replay inputs (observed: f119e.py, 2026-10-04). Budget 27,096, third 9,032, notice 140. The cap gives the reply `max(9,032 - 4 - results, 1,000)` = 1,000 on all three turns.

| turn | t-1 reply | t-1 results | newest middle unit | middle room now |
|---|---|---|---|---|
| s153 t16 | 10,928 | 8,566 | t11 utils 670-710, at most 1,937 | -795 |
| s154 t16 | 22,756 | 8,711 | t12 utils 674-696, about 1,301 | -940 |
| s156 t8 | 29,773 | 8,415 | t6 utils 1-50, at most 2,823 | -644 |

(a) Dedupe at the source. At runner.py:2238-2247, group the red rows by `said`: one traceback per distinct output, then the ids and paths. `tests.load` falls from about 34,100 to about 7,000. The seat loses nothing. But the uncut wake is still about 34,500, because `code.source` follows, so `wake_room` still cuts at 18,064. The seat sees about 3,700 of the source in place of the copies, and the middle room stays negative. Frame 108's cap still declines on all three turns (reasoned: arithmetic above). Stale: 0 cassettes carry the project key. Some of the 867 with own red rows go stale where two own tests share an output (observed: cassettes.db, 2026-10-04). Price about 30k.

(b) The share yields. At runner.py:898, `wake_room = budget // 2` when the transcript holds a middle `_RESULTS` block, else two thirds. Turn 1 keeps b8c18fe's case. The wake is 13,663 after its note. Middle room becomes 3,721, 3,576 and 3,872, and the newest unit fits on each turn. So the cap lands on all three (reasoned: `_cap_tail_reply` arithmetic, runner.py:696-724, with the trial pack keeping the newest read). On s153 the wake loses characters 13,548 to 18,064. They lie past offset 6,263 of `tests.load`, after the thread and the own rows, so they hold only repeated project rows. Fixed shares stay, so frame 108's rule holds. Stale: the turns past the first with a wake over half the budget. 54 cassettes carry a wake cut and 10 of them also the notice. Wakes between half and two thirds were not measured. Price about 30k for the pass and about 20k for the review.

(c) The share holds, and the cap cuts the wake further only when the trial pack keeps no middle read. The cut is by the deficit plus the smallest unit, floor `budget // 2`: 2,732, 2,241 and 2,467 on the three turns. The cap then lands on all three. It touches runner.py:696-724, and `_fit` must take the new wake back. Stale: at most the 10 cassettes with a wake cut and the notice. The cut is sized from the middle. Frame 108 refused that as circular, and the wake's size then moves on every turn. Price about 60k.

## 5. The dangling pointer

No option fixes it. "The answer is in this prompt." is written at runner.py:3292-3294 one turn before the next `_fit`, and any eviction can take the block (reasoned: the comment at runner.py:3284-3291). (b) only makes the eviction rarer on Developer turns. The smallest fix applies the rule of runner.py:3304-3315: make no claim about this prompt. Replace the sentence with one true in both cases: "If the window dropped it, ask once more and it is served again." That claim holds, because an evicted key goes to the serve branch up to `SERVE_CAP`. Stale: 620 cassettes carry the sentence (observed: cassettes.db, 2026-10-04).

The 54-turn count does not measure this sentence. `nightcount.py:165-167` counts a turn with the eviction notice and `unchanged since you asked` or `was run for you before you`. Those lines make no claim about place. The sentence itself appears in 72 turns in 25 sessions on night 113, and beside the eviction notice in 26 turns in 7 sessions (observed: LIKE over `turns`, 2026-10-04). Count it apart.

## 6. Recommendation

Take (b), and fold in the one-sentence fix of section 5. (b) is one line, keeps fixed shares as frame 108 ruled, keeps turn 1 as b8c18fe intended, and frees room on all three turns. On night 113 it costs only repeated rows. (a) is worth its own small frame, because it puts source in place of copies. Alone it frees no middle room.

Ends when:

- Mechanism: a turn past the first with a middle read gets the wake at half the budget, so `_cap_tail_reply` keeps one middle read beside a full tail.
- Ratio: Developer turns with the dropped notice, no middle results block and a tail reply over a third of the budget fall from 4 in 10 Developer sessions on night 113 (s153 t16, s154 t16, s155 t5, s156 t8). Turns with "The answer is in this prompt." beside the eviction notice fall from 26 in 7 sessions of 914 turns, toward 0 by construction.
- Residue: a session that still re-reads after a long reply is read, and the frame closes when its cause is not the wake's share.
