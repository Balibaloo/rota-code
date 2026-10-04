# Frame 113, a Developer writes its own tool results: the cause read

Rota workflow throughout. Scripts: `f113a.py` to `f113f.py` in the session scratchpad. Databases opened read-only. Counts are whole-database, as the night log counts them.

## 0. The headline

There was no rise at night 106. Night 105 is the outlier. Night 105 ran 4 Developer sessions and 43 Developer turns, and night 106 ran 33 sessions and 476 turns (observed: `sessions` and `turns` of `clickI_night105.db` and `clickI_night106.db`, 2026-10-04). The Developer `made up` count on nights 93 to 104 is 7, 21, 2, 19, 12, 3, 12, 28, 17, 17 (observed: the `made up` line of `.rota/night93.log` to `.rota/night104.log`, 2026-10-04). The sign is chronic, and the transcript layout teaches it.

## 1. What the seat sees before it invents

Turns read, prompt tail and reply (observed: `f113a.py`, 2026-10-04):

| night | turn | role | what the reply does | class |
|---|---|---|---|---|
| 116 | s180 t6 | Developer | `TOOL: code.source(...107, 135)`, then a full `OK code.source -> ...` head with the real `defs` map and source text | continuation |
| 116 | s179 t4 | Developer | 14 `TOOL: code.source` lines, each followed by its own `OK` block, 22,443 characters | continuation |
| 116 | s186 t5 | Developer | repeats the prompt's last exchange: the `code.write` call and its `ERROR code.write: start=291 ...` line, byte for byte | echo |
| 113 | s143 t11 | Developer | repeats the last exchange: prose, `TOOL: code.commit(...)`, `OK code.commit -> {"committed": true, "head_commit": "3945a33c..."}` | echo |
| 113 | s146 t9 | Developer | `TOOL: code.write(...)`, then `OK code.write -> path: src/click/utils.py, start: 688 ...`, not in the prompt | claim, but the write call ran |
| 113 | s131 t5 | Developer | `TOOL: code.source(...251, 346)`, then the `OK code.source` head | continuation |
| 114 | s250 t21 | Developer | `TOOL: code.write`, `TOOL: code.commit`, then both `OK` results | continuation, both calls ran |
| 114 | s250 t7 | Developer | quotes an earlier `ERROR code.write` and an `OK code.write` inside a code fence while it reasons | quotation |
| 116 | s163 t3 | Vision Keeper | repeats the prompt's last two exchanges, `problem.assert` and `ledger.log`, with their results | echo |
| 116 | s203 t4 | Vision Keeper | repeats the last two exchanges, one result is `unchanged since you asked earlier this session` | echo |
| 114 | s219 t10 | Vision Keeper | the prompt shows the runner's warning `You wrote tool results into your own reply` directly above a real `OK decisions.author`; the reply writes 9 more calls with results | continuation |
| 113 | s115 t6 to t8 | Vision Keeper | three identical replies, each echoing its own earlier invented reply | echo |

Each inventing reply starts with a `TOOL:` line and puts the first result directly after it. The first invented line follows exactly one call in nearly all turns (column `before1st` = 1). Echo copies the prompt's newest exchange. Continuation writes the result the seat expects for a new call. A claim with no call behind it is rare (observed: the table, 2026-10-04).

Counts by class, Developer, turn classed by its first invented line (observed: `f113c.py`, 2026-10-04):

| night | sessions | inventing turns / turns | echo | continuation | claim | lines echo / cont / claim |
|---|---|---|---|---|---|---|
| 113 | 9/10 | 20/164 | 9 | 10 | 1 | 15 / 11 / 2 |
| 114 | 18/28 | 41/409 | 23 | 16 | 2 | 33 / 29 / 4 |
| 116 | 6/11 | 16/104 | 8 | 8 | 0 | 12 / 25 / 0 |

Vision Keeper: 113 33 turns, 31 echo, 2 continuation; 114 37 turns, 31 and 6; 116 31 turns, 29 and 2; no claim (observed: `f113c.py`, 2026-10-04). A claim here means an `OK code.write` or `OK code.commit` line not in the prompt. Only one of those has no call of that function before it: s250 t7, the quotation.

## 2. What teaches the form

The prompt is one text: `user = "\n\n".join(transcript)` at `rota/core/runner.py:2831`. A reply block and its results block stand side by side, with a blank line between them and no frame (observed: the code and s163 t3, 2026-10-04). The seat reads, at the end of its prompt:

```
TOOL: problem.assert(id="confirm_default_on_eof", text="Let confirm() take ...", kind="in_scope")

OK problem.assert -> {"id": "confirm_default_on_eof"}
```

A reply that continues this pattern is the likeliest text. The runner wrote this down itself at `rota/core/runner.py:513`: "This is the transcript format teaching the model to continue it ... the reply and the results are the same kind of text in the same stream" (observed: the comment, 2026-10-04).

A second fact points the same way. The wake's pushed results use another frame, `[batches.expect]` on its own line and the JSON below. That frame stands in 683, 1,084 and 677 prompts on nights 113, 114 and 116. No reply on those nights writes a `[fn]` frame line (observed: a regex count, 2026-10-04). The pushed block follows no `TOOL:` line, so this is not yet proof that a new frame stops the copy (reasoned: the pairing of call and result is absent there).

The system text says, at `rota/core/runner.py:323`: "Results come back on your next turn, never inside this one." The text lists call forms `TOOL: artefact.verb(key='value')` and shows no result line (observed: the system of s180 t1, 2026-10-04). The Developer briefs under `rota/roles/prompts/developer/` say nothing about results.

## 3. What the runner does today

1. It detects the first invented line with `FABRICATED_RESULT` (`rota/core/runner.py:531`) and records the error `wrote its own tool results`.
2. It adds a feedback line: "You wrote tool results into your own reply ... Send the calls alone and stop; I will answer." (`runner.py:3061`).
3. It runs the calls before the first invented line. It drops every call after it and says `NOT RUN, because you wrote a tool result of your own ahead of them` (Rule 1, frame 77, `runner.py:3066` and `3462`).
4. It stores the whole reply: `_append(transcript, kinds, _REPLY, completion.text)` at `runner.py:3469`. The invented lines stay in every later prompt until tier 1 of `_fit` stubs the reply, which happens only when the prompt is over budget.

The next prompt holds the invented reply in 68 of 76, 110 of 121 and 68 of 76 inventing turns on nights 113, 114 and 116 (observed: `f113b.py`, 2026-10-04). So the invented line and the real line stand side by side in the next prompt, as in s219 t10.

## 4. Night 105 to night 106

`git log 4f56050..bf74640` holds 15 commits. Two touch code or briefs: `3b92f9e` (the challenge rescan in `rota/llm/toolproto.py`, and the quotes line in `tests_failing.md` and `exhausted.md`) and `bf74640` (one sentence on single quotes in the same two briefs) (observed: `git log` and `git diff`, 2026-10-04). Neither commit touches the transcript layout, the stub, the results text or `_fit`. Frames 100, 106 and 107 were already in at night 105's commit. No commit taught the form between the two nights (reasoned: the diff, and the counts in section 0 show exposure, 4 against 33 sessions). Per Developer turn the rate is 2/43 on night 105 and 63/476 on night 106.

## 5. The harm

- Write or commit result where no call ran: 0 on nights 113, 114 and 116. Rule 1 runs the calls before the invention, and every invented `code.write` or `code.commit` line follows its own real call. The one exception, s250 t7, is a quotation (observed: `f113c.py` and `f113e.py`, 2026-10-04).
- Invented `OK code.commit` with no new landed commit in the next prompt: 0, 1, 0 turns. The `ran anyway` shas are real commits whose call stood before the invention, for example s143's `3945a33c`, an echo (observed: `f113c.py` and the night logs, 2026-10-04). So `ran anyway` counts echoes beside real commits and not commits from memory.
- Window: Developer replies with 5 or more invented lines are 0, 2 and 2. s153 t8 on night 114 (11,872 characters, 11 lines) and s179 t4 on night 116 (22,443 characters, 14 lines) were cut in the next prompt, and the next prompt evicted the middle. s250 t23 evicted with the reply whole. s192 t7 evicted nothing (observed: `f113e.py`, 2026-10-04).
- Lost calls: s179 t4 ran 1 of 14 calls. The other 13 were dropped by Rule 1 and asked again in later turns.

## 6. Options

| | mechanism | lines | the seat loses | cassettes stale | price |
|---|---|---|---|---|---|
| a | store the reply cut at its first invented line; the results block says in one sentence how many lines it cut | `runner.py:3469`, one sentence near `runner.py:3061`, offsets from `scanned` | text after the invention, which Rule 1 already does not act on | prompts after an inventing completion: 2,618 completions hold an invented line today; frame 100 counted 3,587 | one pass, about 150k, and a re-record |
| b | runner results in a frame a reply does not continue, for example the wake's `[fn]` header | `_as_block` and every `OK {call.name} ->` site, `_SOURCE_RESULT`, `_OK_LINE`, `FABRICATED_RESULT`, `nightcount.py`, `nightreport.py` | nothing | 22,316 of 26,472 prompts hold a runner result line | two passes, about 600k, and a full re-record |
| c | a brief line against writing results | `runner.py:323` | nothing | all 26,472, because the system text changes | about 20k |

Frame 100's design read concluded that a reply should be stored cut at its first invented result. It parked the cut as its own frame because it changes every turn after an invented result, 3,587 cassettes against option C's 545, and one walk could not tell which change moved a case (observed: `plans/archive/stack-2026-10-02.md`, status 2026-10-01 14:43, 2026-10-04).

Option (c) is a fourth shape of words. `4951ca0` wrote "Results come back on your next turn, never inside this one", `feb11d3` wrote the feedback sentence, and frame 77 wrote the `NOT RUN` line (observed: `git log -S`, 2026-10-04). s219 t10 shows the warning directly above the line it copies. So the project rule asks for an interview before (c) (reasoned: the seat has the fact in front of it and does not act).

## 7. Recommendation

Option (a). It removes the seat's own invented lines from every later prompt, and so the self-echo loop and the long stored reply. It touches one append site and one sentence. Option (a) does not act on a session's first invention. Option (b) does, but it needs a replay first: `interview_turn.py` on s180 t6 and s163 t3 with the results re-rendered, as a frame below this one (reasoned: the wake's frame is never copied, but it follows no call).

Ends-when:

1. Mechanism: a reply with a line that `FABRICATED_RESULT` matches is stored up to that line, and the next results block names the count of lines cut. The diff review checks the offset between `scanned` and `completion.text`.
2. Ratio: later inventing turns, a session's second and after, over all inventing turns. Baseline Developer 44 of 77 on nights 113, 114 and 116 (11, 23, 10), and Vision Keeper 59 of 101 (observed: `f113f.py`, 2026-10-04). The frame closes when one full night is at or under half the baseline, Developer 29% or less. The session ratio, 40 of 59 on nights 113 to 116, is not this frame's line.
3. Residue: a session that still invents a second time is read. The frame closes when its cause is a new call with a new result (continuation), and not a copy of its own stored invented line. A first invention is option (b)'s frame.
