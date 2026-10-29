# W14 and the `_faulted_approve` door: the reach of night 175's stop

Read of 2026-10-29, at head 5aa17c7c. Registers: copies of
`.rota/clickI_night170.db` to `clickI_night175.db` (with their `-wal`
files), opened in a scratchpad. No code was edited.

## 0. The result

- **Question 1.** Four deciders say "this ruling takes the criterion
  away", and all four read one function, `_dropped_line`
  (`rota/roles/api.py` 6573), through `grant(conn, id, "drop")`. Only the
  act `drop` retires a criterion. On nights 170 to 175, 15 landed contest
  rows on a criterion carry his delete words. 3 retired the criterion, all
  three with act `drop` (r_m30, night 175). The other 12 carry `remove` or
  no act, and nothing reads them (observed: section 1.4).
- **Question 2.** The door fired 16 times on nights 170, 172, 173, 174 and
  175, and 4 more times in night 171's cassette replay of night 170. 3
  refusals were right, 12 were wrong, and 1 is disputed. Each of the 8
  pages with a wrong refusal landed a ruling that reverses his words on the
  refused line (observed: section 2.2).
- **A pointer to correct.** `plans/night175-read.md` names `api.py` line
  14464 as the retire reader. Line 14464 is in the team's-note revise door
  of `rulings_rule`. It reads the act to pass a revise of a team's note,
  and it retires nothing. The retire reader is `_dropped_line` (observed:
  `api.py` 6573 to 6581 and 14440 to 14466).

## 1. Question 1: the criterion that his words delete

### 1.1 What a landed contest on a criteria row does, by act

The chain for a retire (observed: the code at 5aa17c7c):

1. `rulings_rule` (api.py 14008) lands the row in `ruled_refs`.
2. The Terminologist wakes on the relay in mode `criterion_repair`.
   `runner._page_acts` (runner.py about 260) calls `criteria_page_acts`
   (api.py 6584).
3. `criteria_page_acts` lists the criterion under "retire" when the last
   ruling is a contest or a revise and `_dropped_line` is not None.
4. `runner._wake_allow` (runner.py 282) then adds `criteria.retire` to the
   tools. `runner._page_act_lines` (runner.py 297) writes "His ruling drops
   the line of X. Retire it with criteria.retire(id='X')."
5. `criteria_retire` (api.py 6704) admits the call only when
   `ruling_drops_line` is not None and the wake is the relay of that
   ruling. It writes `retired_by`.

`grant` (`rota/roles/principal.py` 810) matches the act exactly. With no
target, the newest row whose act is `drop`, or whose act is on the row
itself, decides. `_on_the_row` (principal.py 900) is true for a null
target or the kind `row` or `check` (observed).

| Act on the criterion row | Readers of the act | Result |
|---|---|---|
| `drop`, kind `row` | `_dropped_line` through `grant(id, "drop")`, then `criteria_page_acts`, `_wake_allow`, `_page_act_lines`, `criteria_retire` | **Retires.** Night 175's r_m30 retired c_4, c_5 and c_6 with 3 `criteria.retire` calls (observed: `criteria.retired_by`, `tool_calls`) |
| `remove`, kind `row` | No reader. `grant(id, "drop")` finds the row, because it is on the row, and returns None, because its act is not `drop`. So it also hides an older `drop` (reasoned: `grant` lines 852 to 864). The `remove` readers `_amend_step` (api.py 1564) and `_assert_words_fault` (api.py 1749) read request items. `_unruled_gone` (api.py 24181) and `_removal_words` (principal.py 2519) read code targets from `_gone_targets` | **Does nothing.** `criteria_retire` refuses "no ruling of the principal drops the line". Only `criteria.respecify` stays, and s256 sent "Superseded by c_1..." 35 times (observed: night 175's read, section 3) |
| `remove`, kind `source_line`, target the criterion id | No reader. `grant(id, "drop")` does not find it: it is not on the row, and its target holds no `drop` (reasoned: `grant`) | **Does nothing.** An older `drop` stays readable |
| No act | No reader. A later row with no act takes back an older `drop` on the row (observed: `grant` line 866) | **Does nothing**, and it cancels an older `drop` |
| A bare verdict word `drop`, `remove` or `strike` | `RULING_WORDS` (api.py 11543) maps each to `contest` and stores no act | The same as no act |

Two other sites read `drop` and retire nothing. The team's-note revise
door reads `act == "drop"` at api.py 14464 to pass a revise of a team's
note. `LineReading.note_act` (api.py 12556, the reader at 13818 to 13883)
reads "drop" in his words for the same door (observed).

Frame 329's site defers to the same reader. The near-copy refusal of
`criteria_respecify` names no retire, because "`criteria.retire` is for his
drop words only (frame 329, repair R2)" (observed: api.py 6883 to 6886).

`p10_form_read.md` at cb7783db is right in shape, with two changes at
head. `disputed_paths` (runner.py 1992) now reads the act `exclude`, not
`remove`. `RULED_ACTS` holds `exclude` (principal.py 1019). The line
numbers moved by about 30 to 40 (observed).

### 1.2 What `landing.md` tells the seat

`rota/roles/prompts/liaison/landing.md` says (observed):

- Line 24: "`remove` deletes the code that his words name, and never a
  file of the guess".
- Line 25: "`drop` takes a line off the page: "Drop line 5" is
  `rulings={"5": {"verdict": "contest", "act": "drop", "target_kind":
  "row", "words": "Drop line 5"}}`."
- Lines 60 and 61: "The reply strikes or drops a line from the change:
  `contest`. The door reads `drop`, `remove` and `strike` as `contest`."

So for a deleted criterion line the prompt asks for `contest` with act
`drop` and kind `row`. The seat's `remove` on a criteria row departs from
the prompt's act definitions (reasoned: lines 24 and 25). The seat follows
his verb. He wrote "Remove lines 7 and 8", and the prompt has an act named
`remove`. The one `drop` example uses the verb "Drop", so it matches only
his replies that say "drop". Lines 60 and 61 put `remove` beside `drop` as
one thing, at the level of the verdict (reasoned). r_m103_2 shows the
shape: his "Drop both of those examples" still landed as `remove`
(observed). Why the seat chose `remove` there is not in the records.

### 1.3 The reach

The places that decide "this ruling takes the row away" for a criterion or
its test (observed: callers of `ruling_drops_line` and
`criteria_page_acts`):

1. `criteria_page_acts` (api.py 6584), read by `runner._wake_allow` and
   `runner._page_act_lines`.
2. `criteria_retire` (api.py 6725).
3. `tests_retire` (api.py 6780).
4. The answer door in `sandbox.py` 2163, which drops the rewrite demand.

All four read `_dropped_line`, so one reader decides for all of them, and
it exists today (observed). Its gap is the vocabulary: it reads one act
name. Two maps already join `drop`, `remove` and `strike`. `RULING_WORDS`
joins them to `contest` and loses the delete. `SHIFT_WORDS` (api.py 11553)
joins `drop`, `remove` and `stop` to the stored word `drop`, on the shift
page only (observed). No map joins them at the level of the act.

Other rows take a delete by other readers, outside W14: request items by
`grant(item, "remove")` with kind `sentence`, requests by `item_parks`
kind `drop`, and team's notes by `note_act` (observed).

### 1.4 The count, nights 170 to 175

Landed contest and revise rows on a criterion, distinct by ruling and ref
(observed: `ruled_refs` joined to landed `rulings`):

| Night | Rows | By act | His delete words on the row | Retired |
|---|---|---|---|---|
| 170 | 1 | no act 1 | r_m97 c_1 "please drop all three formatting tests": not read against the page | 0 |
| 171 | 2 | `rewrite` row 1, `add` check 1 | 0 | 0 |
| 172 | 12 | no act 12 | 0 | 0 |
| 173 | 3 | no act 3 | 0. "please drop it" names line 8, a reading line | 0 |
| 174 | 2 | `remove` row 2 | 2: r_m79 c_3 and c_6 (W14 of night 174) | 0 |
| 175 | 17 | `drop` row 3, `remove` row 4, `remove` source_line 5, `remove` no kind 1, no act 4 | 13: r_m30 3 `drop`; r_m103_2 and r_m148 4 `remove` row; r_m118 and r_m122 4 `remove` source_line; r_m79 2 no act | 3, the `drop` rows |

Total: 15 rows with his delete words, 3 retired (observed). By act: `drop`
3 of 3 retired, `remove` row 0 of 6, `remove` source_line 0 of 4, no act
0 of 2. Two more `remove` rows on c_1 (r_m118 source_line, r_m138 no kind)
are wrong rulings, because he kept c_1 (observed: night 175's read).

### 1.5 The general solution from what exists (not built)

1. Put the meaning where the seat reads: `landing.md` lines 24, 25, 60 and
   61 say that a reply which removes, deletes, drops or strikes a page line
   is `drop` with kind `row`, and that `remove` is for code only.
2. Give the seat in-depth cases, not a door: an `l1_landing` case each for
   "Remove lines 7 and 8", "Drop both of those examples" and "Removing
   lines 7 and 8 is right" on a criteria page.
3. As a fact in the record, `_dropped_line` reads `remove` with kind `row`
   on a criterion as `drop`: no other reader reads `remove` on a criterion.
4. Reach: rows 1 and 2 cover all 12 missed rows, the 2 with no act
   included. Row 3 covers 6 of 12, with no prompt edit and no wrong retire
   on these nights (reasoned: 1.4).
5. Price: 2 cycles, one prompt and its cases, one reader and its test. The
   prompt edit unmeasures the 9 recorded cases of `l1_landing.yaml`
   (reasoned: `p10_form_read.md` and `prompt_hash`).

Caution: row 3 must not read `remove` with a target equal to the criterion
id. That form would retire c_1 on r_m118, which reversed him (reasoned:
1.4). The wrong c_1 rows came after `_faulted_approve` refusals (section
2).

## 2. Question 2: the `_faulted_approve` door

### 2.1 What the door checks

`_faulted_approve` (api.py 13437 to 13485) has one caller, `_line_refusal`
(api.py 13223), which `rulings_rule` calls at 14747 (observed: the map).
It refuses each approved line that has a fault cue, unless the line is
closed, line 1 of a request-first page, or a text line beside a batch
line when the clause names files. The refusal names the cue (observed).

The cues come from `LineReading.cues` (api.py 12467), which calls
`_line_cues` (api.py 13031). The lists live in `api.py` (observed):

- `_LINE_FAULT` (12259): wrong, isn't right, is not right, goes too far,
  still, drop, remove, strike, fails, should, instead, not, also.
- `_WEAK_CUES` (12585): also, still, not. `_NEGATED` (12611).
- `_AGREEMENT` (12629), `_FAULT_WORDS` and `_GONE` (12661 to 12671), and
  `_NO_VERB` (12681). Since frame 305's pass 2 the reader is inverted. Any
  clause with a verb faults its line unless it is an agreement. So a verb
  or a word missing from `_NO_VERB` can be the cue: "can simply be",
  "rule", "add", "Remove", "alone" (reasoned: the cues of 2.2).

### 2.2 Every refusal, nights 170 to 175

The source is `turns.user`, a refusal counted on the turn where it is new
and last (observed). Night 171's s92 and s93 are a cassette replay of night
170 (`sessions.backend` `cassette:ollama`), with the same 4 refusals. They
are left out of the table and the totals.

| Night, session, turn | Line, cue | His sentence | Door | Next call | Landed on that line |
|---|---|---|---|---|---|
| 170 s222 t4 | 3, "can simply be" | "Line 5 repeats line 4, and the check on line 3 can simply be that the docstring shows the example." | Right | contest 3 | r_m97 contest c_1. Not reversed |
| 170 s92 t4 | 1, "are fine" | "Your reading of my last answer in line 29 is right, and line 1 and the rest of the word notes are fine with me." | Wrong | the same call | see s93 |
| 170 s92 t5 | 1, "are fine" | the same | Wrong | session ends | see s93 |
| 170 s93 t3 | 1, "are fine" | the same | Wrong | contest lines 1 to 28 | see t5 |
| 170 s93 t5 | 1, "are fine" | the same | Wrong | contest 1 and 18 to 28 | r_m7 contest `how_it_works`. **Reversed** |
| 172 s196 t4 | 1, "drop" | "The first request is right." | Wrong | the same call | see t5 |
| 172 s196 t5 | 1, "drop" | the same | Wrong | contest 1 | r_m81 contest `s3`. **Reversed** |
| 173 s120 t3 | 4, "not" | "Line 7 is slightly off, because I approved two lines, lines 1 and 4, not one." | Wrong | revise 4 | r_m35 revise c_3. **Reversed** |
| 174 s100 t2 | 2, "rule" | "On line 2, rule against the critic and keep the claim, because when Click turns a missing value into None, it still runs the function with what the user gave." | Right | contest 2, `keep` check | r_m14 contest. Not reversed |
| 174 s159 t5 | 3, "add" | "For line 3, please add that what clear prints stays exactly the same and only the return value changes." | Disputed | revise 3, `rewrite` | r_m43 contest `remove` row. **Reversed** (W5 of night 174) |
| 174 s93 t7 | 13 to 20, "Remove" | "Remove lines 13 to 20, because they list groups of users and not words with more than one meaning, and lines 17 to 19 repeat lines 13 to 15." | Right | contest 13 to 20 | r_m8 contest `remove` row. Not reversed |
| 175 s283 t3 | 2, "alone" | "Please don't give up on this change: remove lines 7 and 8 and finish with line 2 alone, because I asked for only one example and only the docstring changes, not the code." | Wrong | contest 2 to 8 `remove` | r_m118 contest c_1. **Reversed** |
| 175 s293 t5 | 9, "not" | "Finish it with line 2 alone, and change only the docstring in the file on line 9, not the code." | Wrong | revise 9 | r_m122 revise bg_3. **Reversed** |
| 175 s316 t7 | 2, "instead" | "Please finish this change with line 2 instead of giving up." | Wrong | contest 2 `remove` | r_m138 contest c_1. **Reversed** |
| 175 s331 t6 | 2, "not" | "Please finish this change with line 2 and do not give up." | Wrong | contest 2 | r_m148 contest c_1. **Reversed** |
| 175 s338 t5 | 2, "not" | the same sentence, m152 | Wrong | contest 2, 8, 9; then approve 8, 9 after the W4 door | r_m152 contest c_1. **Reversed** |

Readings (reasoned, against his words):

- s222: "can simply be" asks for a new check on line 3, so the approve was
  wrong.
- s100: line 2 is the critic's challenge `challenge_items_parses_and_executes_inputs`.
  "rule against the critic" is a contest of the challenge. Night 174's
  read agrees: "the outcome is right".
- s93 of night 174: the refused call approved lines 14 to 20, which he
  removes.
- s159 is disputed. Night 174's read says "An add is a change, so the line
  takes no approve". `landing.md` line 28 gives the add on an approve,
  "an approved one too". The seat followed the prompt.
- Each wrong case takes the cue from a clause about another line or about
  the team: "fine" about line 1 itself, "drop" about line 2, "not one"
  about line 7, "alone" and "instead" and "do not give up" about the
  change.

### 2.3 Totals

- Right: 3 (170 s222, 174 s100, 174 s93).
- Wrong: 12, on 8 pages (170 m7 4, 172 m81 2, 173 m35 1, 175 5).
- Disputed: 1 (174 s159).
- A wrong refusal followed by a landed ruling that reverses his words on
  that line: 8 of 8 pages. With the disputed case, 9 of 9.
- Night 171's replay adds 4 wrong refusals and 1 reversed ruling, the copy
  of night 170.

### 2.4 With the door gone

The wrong cases land the call as the seat sent it (reasoned: no other
door refused those calls on those lines, by the turns):

- 170 m7: line 1 approve, and 18 to 28 contest with `drop`, his words.
- 172 m81: line 1 approve, and line 2 contest with `drop`, his words.
- 173 m35: line 4 approve, his "I approved ... lines 1 and 4".
- 175 m118, m122, m148: line 2 approve, and lines 7 and 8 (8 and 9 on
  m148) contest with `remove`. The verdicts are his. The act still retires
  nothing (section 1).
- 175 m138 and m152: line 2 approve, his words. Lines 7 and 8 (8 and 9)
  stay approve, the W4 door's push, so c_2 and c_3 stay live as they did.

The right cases land a misreading:

- 170 s222: line 3 approve. c_1's check stays, and his new check reaches
  nobody.
- 174 s100: line 2 approve. The critic's challenge stands against "rule
  against the critic and keep the claim".
- 174 s93: lines 14 to 20 approve. Seven of the eight glossary lines he
  removed stay on the page.
- 174 s159 (disputed): approve with `add` lands in the prompt's own form.
  The landed ruling was the reverse, `remove` (W5).

No fix to the door is proposed. Frame 345's cases decide its removal.
