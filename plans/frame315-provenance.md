# Frame 315, the provenance read: a re-slice after a contest loses his corrections

Read 2026-10-24 06:02, at fe4b3c78 (the code under `rota/` is the same at
50609cd3). Sources: `.rota/clickI_night161.db` opened read-only, its
`turns`, `tool_calls`, `receipts`, `rulings`, `config`, `criteria`,
`tickets` and `messages`, `.rota/night161.log`, and the code. Read-only
except this file.

## The result

**The loss is a gap that no design covered, and one narrowing door makes
it worse.** His words landed on the right rows: the criteria c_1 to c_3
of tk_1 at version 4 (observed: `receipts`, s274). Frame 190's change 2.7
then retired tk_1 by `item_ver`, and no rule carries a retired ticket's
landed criteria or the landed rulings' words to the new ticket (observed:
`not_retired`, `scheduler.py:248-263`, and the criteria wake,
`runner.py:3984-3993`). The ruling of 2026-10-08, point 4, says "Every
word of the principal is a ruling on a row" (quoted:
`rota/DECISIONS.md`). The re-slice takes the row away, so his words land
on a row and then leave the build. Frame 190 meant the words to travel on
the item text, and frame 263's sentence filter lets only a sentence with
no line number reach the item. m131's correction shares a sentence with
"lines 3 and 4", so the filter dropped it (observed: s276's turns 1 and
2, `_item_sentence`, `api.py:1388-1402`).

**The repair is one carry in the criteria wake, 1 cycle, and a new-id
offer in the cross-ticket id refusal, 0.5 cycle.** Neither changes his
words. A third change, to let the amend carry the correction clause, edits
the text of his request. That is a composition question for Roman.

## 1. The chain, corrected against the records

1. m130 presented b_4 with the rows in the order item, c_1, c_2, c_3, b_4
   (observed: `config` `order:m131`). His m131: "Line 2 is wrong. I meant
   show_python as a true-or-false argument that the developer passes to
   version_option, not a new show-python flag that the user types on the
   command line, so lines 3 and 4 should also say ... The Python version
   should also be shown as major.minor.micro from sys.version_info."
2. s272 ruled the item and c_1 `contest`, c_2 and c_3 `revise`, b_4
   `approve` (observed: `rulings` r_5346319ecc). `principal.land` set the
   item `contested`. The log shows `do:cancel: abandoned b_4` right after
   the m130 line (observed: `night161.log` line 129).
3. s274, on the relay m133, respecified c_1 to c_3 of tk_1 with his
   words: "a boolean argument `show_python` that the developer passes"
   (observed: s274 turn 1, `criteria` at version 4). Those writes were
   right. tk_1 had `item_ver` 3, and its batch was already abandoned.
4. s275, on the relay m134, set the item `contested` again and set its
   priority. It wrote no text (observed: s275's turns).
5. s276, on `tick:contested`, saw the whole of m131 in `principal_said`
   (observed: s276 turn 1, the wake). Its first call amended the item with
   on and off words. The words door refused it and offered one sentence:
   "amend '...' with his sentence 'The Python version should also be shown
   as major.minor.micro from sys.version_info.'". s276 sent that sentence
   word for word (observed: s276 turns 1 to 3). The item went to version 4.
6. s277 reported. The Liaison asked m136, the right question. His m137:
   "Yes, show_python is a true-or-false argument that the developer passes
   to version_option ... When it is off, the message stays exactly as it
   is today." The Liaison ruled it `approve` on the item and on e_m132
   (observed: `rulings` r_206b20c23b).
7. s279, on the relay m138, saw m137's words and approved the item. A
   relay wake cannot rewrite a decided item (reasoned: `api.py:1561-1581`,
   "A relay wake does not rewrite them"). s279 did not try.
8. s281, on `tick:slicing`, saw the item's headline only. It sent tk_1,
   was refused because tk_1 went out in the abandoned b_4, and sliced tk_2
   from the headline (observed: s281's turns). tk_2 has `item_ver` 4, so
   tk_1 is retired.
9. s282, on `tick:criteria`, saw "the item" with "the principal said":
   the statement s3 only, "Give version_option a show_python flag that
   appends the running Python version to the message" (observed: s282
   turn 1). Its c_1 said "a boolean flag named show_python that ...
   appends ... to the help message". The id refusal fired on turn 1 and
   again on turn 10. The read's claim "never sent c_1 again" is not exact:
   s282 sent c_1 twice under the same id and never under a new id
   (observed: the runner's account on turn 12).
10. tk_2 holds c_2 to c_6. None says what `show_python` is. s288 later
    respecified c_6 after m139 (observed: `receipts`).

## 2. The answers

### Q1. The cancel path

1. `principal.land` (`principal.py:1921-2321`) writes the verdict. Its
   loop at `principal.py:2230-2247` maps `contest` and `revise` to
   `contested` and updates `items.approval`. It writes `verdict:<msg>`,
   `entry:<msg>` and the landed `rulings` row with `texts`, the contested
   criteria's texts as they stood (observed).
2. The `cancel` predicate (`predicates.py:1530-1555`) reads `batches`,
   `items` and `item_parks`. It fires on a live batch whose item is not
   `approved` at its version (observed).
3. `_perform` (`loop.py:440-446`) calls `lifecycle.abandon`
   (`lifecycle.py:165-186`). That sets the batch `abandoned`, invalidates
   its checkpoints, tears down the environment and keeps the worktree. It
   touches no ticket and no criterion (observed).
4. The `contested` predicate (`predicates.py:291-306`) wakes the Vision
   Keeper on `tick:contested`. Its wake is `_resolve_contest`
   (`runner.py:2451-2489`): the newest `verdict:` that contests the item,
   `principal_said` from the entry, and the item row (observed).
5. After a new approval, `tick_slicing` (`scheduler.py:313-391`) wakes on
   an item whose version is above the newest ticket's `item_ver` and
   whose tickets sit in no live batch (observed: the `amended` clause at
   `scheduler.py:344-352`).
6. `tickets.slice` (`api.py:4675-4738`) refuses an id from an abandoned
   batch and writes `item_ver` (observed).
7. `not_retired` (`scheduler.py:248-263`) then hides the old ticket from
   `tick_criteria`, `grouping`, `tests_missing` and the page
   (`principal.py:1028-1035`) (observed: its callers).

**Where the dead ticket's landed criteria go.** They stay in `criteria`
under tk_1 at their last version. Nothing reads them for the build again.
The contest block (`runner.py:3921-3931`, `contests_on`) keys by
criterion id, and tk_2's criteria have new ids, so no ruling on c_1 to c_3
reaches b_5 (observed). `rulings.texts` holds the version 3 texts, the
`--show-python` ones, not his corrected words (observed:
r_5346319ecc). The one reader of tk_1's c_1 after the re-slice is the id
refusal in `criteria.specify` (`api.py:5374-5384`), which reads it to
refuse s282 (observed).

### Q2. The Vision Keeper's amend on `tick:contested`

The wake showed all three of m131's sentences in `principal_said`
(observed: s276 turn 1). The seat's first amend was its own paraphrase,
with "includes" and "excludes", and the words door refused it for new
words (observed: the door's message on turn 2, the `new` branch at
`api.py:1677-1693`). The refusal ends with `_amend_step`
(`api.py:1405-1412`), which offers `_item_sentence(said)`
(`api.py:1388-1402`). That function drops any sentence that matches
`_PAGE_CUE` (`api.py:1343-1344`), a line number or "page". Sentence 1,
"Line 2 is wrong.", matches. Sentence 2, the correction, matches on
"lines 3 and 4". Only sentence 3 remained, so the door named it, and
s276 sent it word for word on turn 2 (observed). s276 kept the sentence
that was not the correction because the door told it to (reasoned: the
offer is the only sentence named, and a 9B seat follows a named offer).

### Q3. The slice

s281's wake held `problem.consult` with the item's headline, cut at 120
characters, and nothing else (observed: s281 turn 1, 703 characters).
The words "true-or-false", "developer passes", "c_1_" and "e_m13" do not
occur in any turn of s281 or s283 (observed: `instr` on `turns.user` and
`turns.system`). The ticket text copies the item's first sentence. A
ticket is a slice of work, so the slice is not where the words must land
(reasoned). s282's wake held "the item" from `push_working_set`
(`runner.py:3984-3993`). Its "the principal said" reads `statements`
through `refs` only, so it showed s3 and not m131 or m137 (observed). The
dead ticket's criteria and the clarify's words were in neither wake
(observed).

### Q4. The id refusal in s282

The cross-ticket branch at `api.py:5374-5384` raises a plain
`ValueError`: "'c_1_version_option_show_python' is already
tk_1_version_option_show_python's criterion. An id you invent is yours
once -- tk_2_version_option_show_python needs its own". It has no
`_offer` and no prefilled call with a new id (observed). The same-ticket
branch below it got `_offer(... "criteria.specify", {"id": INVENT, ...})`
at bab9911b, frame 310, on 2026-10-24, and the cross-ticket branch kept
its text from a9cb55de of 2026-09-03 (observed: `git log -S`). The seat's
turns after the refusal:

- Turn 2: c_3 under a new id.
- Turn 3: c_4 under a new id.
- Turns 4 and 5: `ledger.log`, an invention on the ticket, once with the
  wrong `about_table`.
- Turn 6: c_5. Turns 7 and 8: two more inventions.
- Turn 9: c_6, "The help message ... must include ...", and the invention
  "the help text reflects the flag state".
- Turn 10: all six criteria again, c_1 under the same id. Refused again,
  and c_2 to c_6 refused as twins.
- Turn 11: "All criteria ... have been successfully specified", which is
  not true for c_1 (observed: s282's turns).

The refusal cost the one criterion about what `show_python` is. Its text
was wrong too, a flag and the help message, so a new id alone would have
landed a wrong c_1 (reasoned: s282 turn 1's text, from a wake with s3
only).

## 3. The design history

| Piece | Commit | Frame or ruling | What it meant |
|---|---|---|---|
| `cancel` | 73c9cba3, 2026-08-27 | loop 6, law 9 | A revoked item's batch leaves the game. Silent on criteria |
| `_resolve_contest` | 8018c376, 2026-09-04 | "the principal's no reaches the desk" | The contested wake carries his words |
| `criteria.specify` cross-ticket refusal | a9cb55de, 2026-09-03 | "a criterion's id is one ticket's" | Stop a silent overwrite of another ticket's criterion. No route offered |
| the criteria wake's "the principal said" | 33ddea8a, 2026-09-13 | clickI night 35 | Statements only. It predates `rulings.words` landing on criteria |
| `item_ver`, `not_retired`, the amended re-slice | 2dace61b, 2026-10-09 | frame 190, 2.F amendment 4, change 2.7 | "every landed correction builds from criteria that predate it" |
| `_item_sentence`, `_amend_step` | bc226206, 2026-10-16 | frame 263 in frame 129's pass 2 | The item holds his words about the item, never his words about the page |
| same-ticket id offer | bab9911b, 2026-10-24 | frame 310 | A new id offered on the same ticket |

Frame 190's design, section 1.5, says the contested brief amends the item
with "`text=<what they meant>`", and change 2.7 re-slices so the new
criteria come from the amended item (quoted: `plans/frame190-design.md`,
lines 303-305 and 889-924). So frame 190 meant his words to reach the new
ticket, and its only carrier was the item text. Its test was night 133,
where his correction was on the item text (observed: the design's test
row 2.F.4). No line of frame 190 names criteria that a relay respecified
on the old ticket. The ruling of 2026-10-08, point 4, puts every word of
his on a row, and the criteria rows of tk_1 were that row (quoted:
`rota/DECISIONS.md`, "The park ask is a page with rows").

Frame 263 then narrowed the carrier. It was built against night 150's
s205 and s404, which copied page sentences into the item (observed:
`plans/archive/stack-2026-10-17.md`, frame 263). Its filter drops a whole
sentence for one line number, and no test held a correction that shares
a sentence with a line number (reasoned: the cue regex and its tests in
`tests/rota/test_frame221_assert_words.py`).

**Verdict: a gap.** No design covered words that land on criteria of a
ticket that the re-slice later retires (reasoned: frame 190 and the
ruling above). The amend's loss of m131's correction is a departure from
frame 190's intent "what they meant", caused by frame 263's filter
(reasoned).

## 4. The repair

1. **The criteria wake carries the ruled words and the retired ticket's
   criteria.** In `push_working_set`, `runner.py:3984-3993`, "the item"
   gains two keys when the item has a retired ticket. The first is the
   landed `rulings.words` whose `per_item` names the item or a criterion of
   its tickets, newest last. The second is each retired criterion's
   current text, marked as the old ticket's. On night 161 that shows m131,
   m137 and s274's c_1 to c_3 at version 4 to s282 (reasoned). The same
   two keys go to the `tick:slicing` wake, cheaply, from the same helper.
   Price: 1 cycle. It changes no words of his. It shows his words and the
   team's rows.
2. **The cross-ticket id refusal offers a new id.** At
   `api.py:5381-5384`, wrap the message in `_offer` with
   `criteria.specify` and `{"id": INVENT, "ticket_id": ticket_id, ...}`,
   as the same-ticket branch does. Price: 0.5 cycle, cause 9. It folds
   into the door family of frame 313 if that frame is open.
3. **Composition question, not a door: the amend's sentence.** The text
   of an item is his request. A change to `_item_sentence` that offers the
   clause "I meant show_python as a true-or-false argument that the
   developer passes to version_option, not a new show-python flag that the
   user types on the command line" puts different words of his into the
   request. That edits the text of his request, so Roman rules it. With
   repair 1 the criteria carry the correction without it (reasoned).
   Recommended answer: do not change the amend now. Read night 162 with
   repair 1 first.

Total: 1.5 cycles for repairs 1 and 2. The read's estimate of 2 cycles
holds with this provenance read counted (reasoned).

## 5. The red tests

1. **s282 turn 1, repair 1.** Fixture: night 161 at the start of s282.
   Assert that the `tick:criteria` wake on `version_option_show_python`
   holds the words of r_5346319ecc and r_206b20c23b, and the text of
   `c_1_version_option_show_python` at version 4. Red at fe4b3c78: "the
   principal said" holds s3 only (observed).
2. **s274's turn as the source rows of test 1.** s274's three
   `criteria.respecify` calls are the fixture's rows on tk_1. They were
   right, so they are not a red test of their own (reasoned).
3. **s282 turn 2, repair 2.** Fixture: tk_1 owns c_1. Send
   `criteria.specify(id="c_1_version_option_show_python",
   ticket_id="tk_2_version_option_show_python", ...)`. Assert that the
   refusal carries an offer of `criteria.specify` with a new id. Red at
   fe4b3c78: a bare `ValueError` (observed).
4. **s276 turn 2, only if Roman rules point 3.** The words door's offered
   sentence holds "developer passes". Red at fe4b3c78: the offer is the
   major.minor.micro sentence (observed).

## Usage

One agent on Opus, about 70k tokens. No test and no gate run. Every
database opened with `?mode=ro`.
