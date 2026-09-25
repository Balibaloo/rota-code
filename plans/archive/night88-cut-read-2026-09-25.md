# Night 88 cut read: what a seat lost (batch B, 2026-09-25)

Rota workflow. This record is batch B's one read on `plans/stack.md`, for
frames 47, 53, 59 and 61. It reads `.rota/clickI_night88.db`, read-only, at
tree `fa391b6`. The read ran at 2026-09-25 02:10 by the clock.

Scope: 191 sessions, 738 `turns` rows. 93 rows are session notes
(`SESSION ENDED`, `system` and `user` empty), so 645 rows are model turns.
Every session ran `qwen3:8b` on Ollama with `num_ctx` 16384 and
`max_tokens` null (observed: `sessions.pins_json`, 2026-09-25).

The code read is HEAD. Night 88 ran on 2026-09-21 before 04:05, and
`rota/core/runner.py` changed after it (commits `59cb2ad`, `42b8950`,
`a47b69e`). So the cut forms below come from the text in the database, and
not from the code (reasoned: the file date and `git log`).

Probe scripts, all in
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/5748c2d9-70b2-4e3e-ae68-0b1745ed8f86/scratchpad/`:

- `b1_survey.py`: counts each cut wording per column.
- `b2_detail.py`: the cut text in `completion`.
- `b3_inventory.py`: the inventory of item 1. It writes `events.json`.
- `b4_reply.py`, `b5_longreplies.py`, `b12_replycost.py`: the reply cut.
- `b6_window.py`: window use and denied demand.
- `b7_ledger.py`, `b8_ledgerloss.py`: the `cut ...` errors and the ledger row.
- `b9_refusals.py`: refusals and unmet refusals. It writes `refusals.json`.
- `b10_classify.py`, `b11_resultsblocks.py`: the class of each cut.
- `b13_reread.py`: re-reads in sessions with an eviction.

## 0. The batch's own counts do not reproduce

The stack says 95 turns carry a cut in `user`, 39 in `system` and 20 in
`completion`. This read finds other numbers (observed: `b1_survey.py`,
`b2_detail.py`, 2026-09-25):

- `system`: 0 turns carry a `CUT` notice, an eviction notice or a reply cut
  error. 122 turns hold the word "cut" in any case, from the briefs. The
  figure 39 is not a count of cuts.
- `user`: 78 turns carry a `CUT ... are not shown` notice. 89 carry the
  eviction notice. 26 carry `ERROR reply cut`. 126 carry at least one of
  the three.
- `completion`: 3 turns carry `CUT`, and each is the seat that copies a
  notice from its prompt. 13 session notes carry a `cut ...` error. 9 session
  notes carry the reply cut error (10 lines).

So the system prompt is never cut on night 88. The `system` side of frame 53
is a question of size only.

## 1. The inventory

### 1.1 The cut forms and their wording

The code and the data show seven forms (observed: `rota/core/runner.py:520-547`,
`:572-592`, `:817-844`, `:1795-1804`, `:2290-2313`, `:2612-2615`;
`rota/roles/api.py:155-189`, `:6478`, `:7515-7525`, 2026-09-25):

| Form | Site | Wording | Call named for the rest |
|---|---|---|---|
| wake | `_render_cut` in `_fit` | `CUT your wake: n of m characters are not shown.` | "Nothing returns a wake." |
| exchange | `_exchange_cut` in `_cap_exchange` | `CUT this exchange: ...` | "Nothing returns an earlier turn. Call again what you still need." |
| eviction | `_fit`, middle | `[k earlier exchange(s) dropped to fit the window. ...]` | "re-read anything you still need" |
| result | `_render` | `CUT the result: ...` | `code.source(path, start=<line>, end)` for a span, else "Ask for a narrower part." |
| pushed set | `_decision_dropped`, `code.tree` push | `CUT the rulings for "w": n of m rows ...`, `CUT this area's files: ...` | `decisions.search(query=...)`, or `code.source` of a named file |
| reply | `done_reason == "length"` | error `your reply was cut at the output budget ...`, then `ERROR reply cut:` in the next prompt | none |
| record | `_cut` in `api.py` | error `cut <what>: n of m <unit> not stored` or `not shown` | none, by design for the ledger row |

A seventh notice is not a `CUT` form but withholds a result: `ran, and this
turn has no room left for its result (20,000 characters of results already).
Ask for it again in your next turn, on its own` (observed: `runner.py:2612`).
It appears in 25 turns of 8 sessions (observed: `b11_resultsblocks.py`,
2026-09-25).

No `CUT your wake` notice appears on night 88 (observed: `b3_inventory.py`,
2026-09-25).

### 1.2 The `CUT` notices, counted

A notice stays in the transcript, so later turns repeat it. The read counts
102 notice occurrences and 52 distinct cut events. An event is one
(session, what, removed, total) tuple (observed: `b3_inventory.py`,
2026-09-25).

| Form | Events | Removed | Median removed | Largest | Total of the cut blocks |
|---|---|---|---|---|---|
| result | 23 | 120,745 chars | 2,257 | 13,580 | 371,573 chars |
| exchange | 23 | 288,034 chars | 8,205 | 44,433 | 588,205 chars |
| area files | 4 | 232 files | 58 | 103 | 328 files |
| rulings | 2 | 31 rows | 15 | 28 | 43 rows |

By role and mode (the wake line):

| Role | Mode | Events | Forms |
|---|---|---|---|
| critic | tick:challenge | 18 | 16 result, 2 exchange |
| vision_keeper | tick:reconcile | 16 | 7 result, 9 exchange |
| architect | tick:survey | 7 | 5 exchange, 2 area files |
| architect | tick:annotate | 4 | 4 exchange |
| terminologist | tick:criteria | 3 | 3 exchange |
| terminologist | tick:survey | 2 | 2 area files |
| vision_keeper | message | 2 | 2 rulings |

By the call named: 23 name no call ("Nothing returns an earlier turn"). 21
name `code.source` at the line the cut fell. 2 say "Ask for a narrower
part". 4 name `code.source` of the omitted files. 2 name `decisions.search`.

Size of the 46 character cuts: 4 under 500, 4 from 500 to 2,000, 12 from
2,000 to 5,000, 13 from 5,000 to 10,000, 13 from 10,000 to 50,000. The
quartiles of the removed size are 2,107, 6,865 and 13,580 characters. The
quartiles of the removed fraction are 0.13, 0.40 and 0.56. 22 of 191
sessions carry at least one event.

### 1.3 Evictions, reply cuts and record cuts

- Eviction: 89 turns in 19 sessions carry the notice. By role and mode:
  critic tick:challenge 42, architect tick:annotate 16, vision_keeper
  tick:reconcile 12, developer tick:batch_start 12, architect tick:survey 4,
  terminologist tick:criteria 3 (observed: `b3_inventory.py`, 2026-09-25).
- Reply cut: 10 turns in 9 sessions. Section 3 has the detail.
- Record cut: 26 `cut ...` lines in 13 sessions. Section 5 has the detail.

## 2. What was removed, classed

The read classes all 52 `CUT` events, the 10 reply cuts and the 26 record
cuts. That is more than the 20 the brief asks for (observed:
`b10_classify.py`, `b11_resultsblocks.py`, `b5_longreplies.py`, 2026-09-25).
The method for each form:

- **result (23): a tool call's result.** Each is the tail of a source span
  that the seat asked for. 21 name the `code.source` call that returns the
  rest. Nine events repeat one span, `src/click/core.py` 0 to 400, or
  `core.py` 958 to 1631, across the critic sessions s87, s89, s162, s163 and
  s164. The class is a result, and the seat has a call to get it back.
- **exchange, reply block (10): the seat's own reply.** The read compares
  the cut total with the length of the previous `completion`, and an equal
  length marks a reply block. Then it reads the removed tail. In s30 and
  s40 the tail is 115 and 144 more `code.source` calls in a counting loop.
  In s32, s134 and s183 the tail holds 18, 5 and 48 tool results the seat
  wrote itself. In s89, s159 and s157 turn 8 the tail is model code or
  reasoning with a compression ratio of 18 to 42, so it repeats. In s69 the
  tail is 21 `model.amend` lines, and s157 turn 7 is 73 `criteria.specify`
  lines. Those calls already ran before the cut, so the cut removes the
  record of the calls and not the calls. The class is prose the seat did not
  need, or its own reasoning in a loop.
- **exchange, results block (13): results and refusals.** The original is
  not stored. The read counts the calls in the reply against the result
  lines still visible. In s30 and s40, 294 and 304 calls show 67 and 19
  results. In s69 turn 2 and s157 turn 7, every visible line is an `ERROR`,
  32 and 34 of them. So the cut tail there is more refusals
  (reasoned: the visible prefix is all refusals and the calls repeat one
  op). The class is a tool call's result, and in two events a refusal.
- **area files (4) and rulings (2): a pushed set.** 4 events remove file
  names from a pushed area list. 2 remove 28 and 3 `decisions` rows for one
  word, which are rulings. Each names the call that returns the rest.
- **reply cut (10): a runaway reply.** Section 3.
- **record cut (26): a verdict, and a read.** Section 5.

**Result of the class.** No `CUT` event removes a verdict the seat wrote.
Two remove rulings, 31 rows, and each names the call to get them. Two
results-block cuts hide refusals from the seat. The largest mass, 288,034
characters of exchange cuts, is a runaway reply and the results it called
for (reasoned: the counts above).

## 3. Frame 47, the `completion` side: the reply cap

**The reply cap is 8,192 tokens, which is half the 16,384 window.** The site
is `OllamaBackend.max_tokens = 8192`, sent as `num_predict` when the pin is
null (observed: `rota/llm/llm.py:372`, `:387`; `pins_json` `max_tokens: null`
on all 738 rows, 2026-09-25). `_fit_budget` gives the prompt the other half.
So prompt plus reply fit the window.

**The cut bit on 10 of 645 model turns, 1.6 per cent, in 9 of 191
sessions** (observed: `b4_reply.py`, `b5_longreplies.py`, 2026-09-25).
Roles: architect 4, vision_keeper 3, terminologist 2, critic 1. Modes:
tick:annotate 3, tick:reconcile 3, tick:criteria 2, tick:grouping 1,
tick:challenge 1. The replies are 20,049 to 37,836 characters long. The
frame's figure of 3.9 per cent is night 87's, and a different count.

**What the cut removed is a runaway, not content** (reasoned: the text of
all 10). Each capped reply is a loop. Four are counting loops of `code.source`
or `criteria.specify`. Three are tool results the seat wrote itself. One
echoes its own wake. Two are prose or code that repeats, with a compression
ratio of 12 to 26. No capped reply lost a verdict or a ruling. The one call
it loses is the last, half-written call of a loop.

**What the cut cost is time.** The 10 capped turns took 906,149 ms. That is
24.2 per cent of the night's 3,744,036 ms of model time (observed:
`b12_replycost.py`, 2026-09-25). Each capped reply then fills the next
prompt, and `_cap_exchange` cuts it again (section 2). All 9 sessions
committed.

## 4. Frame 53, the `system` and `user` side: the window

**No prompt went over the half-window budget.** Per turn the read computes
`_fit_budget(16384, len(system))`, which is `32,522 - len(system)`
characters (observed: `b6_window.py`, 2026-09-25).

- The system prompt: quartiles 4,133, 4,443 and 5,419 characters, largest
  10,141. It is never cut.
- `len(user)` against the budget: the deciles are 0.04, 0.08, 0.11, 0.16,
  0.22, 0.30, 0.38, 0.56 and 0.82. The largest is 1.00. 46 turns are over
  0.9 of the budget. 0 are over it.
- `system` plus `user` against the full window at 3.97 characters to the
  token: the median is 0.17. The largest is 0.50.

**The denied demand is 873,048 characters on 54 turns.** The read rebuilds
the prompt that each turn would have had without `_fit`. It adds the
previous `user`, the new reply and results block, and each exchange cut's
removed size. On 334 turns with no cut, the rebuilt length equals the real
length every time. So the method is exact where the read can test it
(observed: `b6_window.py`, 2026-09-25). The split: 282,665 characters by
exchange cuts and 590,383 by eviction.

**795,314 of the 873,048 would fit in the full window.** The full window is
`int(16384 * 3.97) - len(system)`. If each turn also keeps room for its own
reply, 759,910 would fit. So the half-window rule, and not the window,
denies 87 to 91 per cent of the denied demand (reasoned: the two bounds).

By role and mode, turns and characters denied:

| Role, mode | Turns | Denied | Fits in the full window |
|---|---|---|---|
| critic, tick:challenge | 22 | 314,139 | 313,090 |
| vision_keeper, tick:reconcile | 10 | 224,494 | 178,353 |
| architect, tick:annotate | 8 | 125,216 | 125,216 |
| terminologist, tick:criteria | 3 | 109,398 | 78,854 |
| architect, tick:survey | 5 | 58,158 | 58,158 |
| developer, tick:batch_start | 6 | 41,643 | 41,643 |

**Whether the denied characters carry load is only partly known.** The
exchange-cut part is a runaway and its results (section 2), so most of it
carries no load (reasoned: section 2's class). The eviction part is older
reads. Sessions with an eviction repeat an identical read call 241 times of
852 reads, 28 per cent. Sessions without one repeat 93 of 858, 11 per cent
(observed: `b13_reread.py`, 2026-09-25). Long sessions repeat more anyway, so
the gap is a sign and not a proof (reasoned: the two groups differ in
length).

## 5. Frame 59: the ledger row cuts

**The 13 sessions with a `cut ...` error are three different cuts, and only
6 sessions cut the principal's ledger row** (observed: `b7_ledger.py`,
2026-09-25).

| Cut | Sessions | Lines | Role, mode |
|---|---|---|---|
| `the principal's ledger row, from this verdict's why` | s86, s87, s88, s89, s90, s91 | 6 | critic, tick:challenge |
| `the principal's ledger row, from this verdict's quote` | s88, s89 | 2 | critic, tick:challenge |
| `the challenge row's quote` or `why` | s89, s186 | 2 | critic, tick:challenge |
| `the candidate symbols` or `the symbols matching the hint`, `not shown` | s128, s134, s157, s159, s180, s183 | 16 | architect tick:annotate, terminologist tick:criteria |

The last row is a read cut of 865 of 885 symbol rows. It is not a ledger
row. It has no call, and s183 hit it 9 times.

**6 of the night's 8 falsified ledger rows lost part of the why.** The
`ledger` table holds 8 rows by the critic, all "falsified" (observed:
`b8_ledgerloss.py`, 2026-09-25). The row keeps 160 characters of the quote
and of the why (observed: `rota/roles/api.py:7508-7513`). The losses:

| Session | Why lost | What the principal's row lost |
|---|---|---|
| s86 | 6 of 166 | `rning.`, the end of a word |
| s87 | 83 of 243 | "the code shows no such warning is triggered by using the group command structure", the finding |
| s88 | 225 of 385, and 130 of 290 of the quote | "logic or emission of a DeprecationWarning related to the command invocation mechanism", the object of the finding |
| s89 | 106 of 266, and 225 of 385 of the quote | "It does not warn users simply for calling Context.get_parameter_source, nor does it cause code to fail.", the finding |
| s90 | 141 of 301 | "deprecation warning logic ... The claim describes an event that is not present in the cited source.", the finding |
| s91 | 36 of 196 | "derstanding its structure and usage.", the end of a clause |

**4 of the 6 lose the clause that says why the claim is false** (reasoned:
the kept 160 characters end before the finding in s87, s88, s89 and s90).
In each, the kept part states the claim or the context, and the cut falls
where the finding starts. The Critic writes its why in claim-then-finding
order. So a fixed prefix keeps the claim and drops the verdict's reason.

## 6. Frame 61: refusals and the ones never met

**The night has 836 op refusal lines and 22 parse errors, in 72 of 191
sessions** (observed: `b9_refusals.py`, 2026-09-25). The read takes each
turn's new results block, the tail of the next `user` after the reply. It
takes the last turn's refusals from the session note, less the ones earlier
turns already showed.

The unit is a (session, op) pair with at least one refusal. A pair is met
when a later turn of the same session shows `OK` for that op, or for an op
the refusal names.

- 110 pairs are refused. 44 are met later. 66 are never met, in 43 sessions.
- 40 of the 66 refusals close the matter and owe no call. Examples:
  "you have already sent report to liaison", "asked three times this
  session", "the two halves of this assumption say the same words", "not in
  this role's working set".
- 26 read as correctable. The read then checks each of the 26 by hand
  (observed: the listing in `b9_refusals.py`, 2026-09-25):
  - 9 also close: "six is many" (s128, s180), "an item already says it"
    (s82, s144, s165, s188), "already batched" (s158, s182), and "not the
    judge's to assign" (s2).
  - 3 are reads with wrong arguments in s158, which owe nothing.
  - **14 owe a write or an act, in 11 sessions, and the seat never made
    it.** These are `msg.present_principal` (s1, s97, s167), `ledger.log`
    (s115, s157, s180), `glossary.adopt` (s133), `criteria.specify` (s157),
    `decisions.author` and `msg.reopen_developer` (s181),
    `msg.reopen_developer` and `problem.assert` (s189), `surveys.attest`
    (s68) and `model.amend` (s69).

**5 of the 14 fall on the session's last turn**: s69, s133, s157 twice, and
s180. The seat had no later turn to meet them. **9 had later turns, and the
seat did not return to the refused call.**

**The seat reports the refused write as done in none of the 11 final
replies read.** s115 says "The ledger log was skipped". s1 says "I have named
the call, but it cannot be made". s189 and s181 write prose about the
statement and do not mention the refused call (observed: the final
`completion` of s1, s68, s115, s181 and s189, 2026-09-25). The frame's fault
from `ACT-TS-five-criteria-one-per-reply` is not seen on night 88. The read
covers 5 of the 11 finals only.

**Two results-block cuts hide refusals from the seat** (section 2): s69
turn 2 and s157 turn 7. There the seat cannot meet a refusal it never saw
(reasoned: the visible prefix is all `ERROR` lines).

## 7. What the read settles, per frame

**Frame 47, the reply cut fires thirty times more often.** The read settles
the category. The reply cut is cosmetic for content: 10 of 645 turns, 1.6 per
cent. Each of the 10 is a runaway loop, and none loses a verdict, a ruling
or a working call. The cut is not cosmetic for cost. The 10 turns took 24.2
per cent of the night's model time, and each one then fills the next prompt.
The two named fixes both miss. A larger cap makes a loop run longer. Telling
the seat before the trim cannot help a seat that is in a loop. The open
question is the price of an earlier stop, for example a lower cap or a
detector for a repeated line. The read gives that repair a clear value:
about a quarter of the night's model time.

**Frame 53, does a prompt get more than half the window.** The read settles
the size. No prompt exceeds the half-window budget. The median prompt uses
0.17 of the full window, and the largest uses 0.50. The half-window rule
denied 873,048 characters on 54 turns, and 795,314 of them would fit in the
full window. That is one tenth of night 87's 8,784,628. The read partly
settles the load. The 282,665 exchange-cut characters are runaways and carry
no load. The 590,383 evicted characters are older reads. The seats in those
sessions repeat reads at 28 per cent against 11, which is a sign of load and
not a proof. The fraction is still a ruling for Roman, now on a smaller
number. The frame should also record that `max_tokens` equals half the
window. A prompt over half has to take room from the reply's cap.

**Frame 59, the ledger row is shorter than the reasoning.** The read
corrects the count and settles the question. Only 6 of the 13 sessions cut
the principal's ledger row. The other 7 are a read cut of the candidate
symbols. But 6 of the night's 8 falsified ledger rows are cut. In 4 of the
6, the cut removes the clause that says why the claim is false. So the
principal rules on a row that keeps the claim and drops the reason. The
frame's repair can be priced now. Exempt the ledger row from the 160
cap, or keep the why whole in the row. The read finds no case for the
second repair option, a fetch call, because a principal does not reread.
The repair is 60k. The symbol read cut, 865 of 885 rows with no call, is a
new finding with no frame.

**Frame 61, an unmet obligation.** The read gives the size. The night has
110 refused (session, op) pairs, and 66 are never met. 49 of the 66 close the
matter by design, and 3 are reads. 14 owe a write or an act in 11 sessions,
and 9 of those 14 had later turns in which the seat did not return. That is
the fault's size on night 88: 9 obligations, or 14 with the last-turn cases.
The read leaves the second half of the ends-when open. No read final reply
reports a refused write as done, so night 88 does not reproduce the
`ACT-TS` case. The read also finds that a results-block cut hid refusals
from the seat in 2 turns. The repair's restatement at the tail would cover
those too, if it sits after the cut.
