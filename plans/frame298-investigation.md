# Frame 298, the investigation: what kills a batch when the principal corrects the files under his request

Read-only agent on Opus, 2026-10-18 11:40. Repository at HEAD 9c4b5368,
which holds frame 296's edit of `rota/roles/api.py`.
Rota workflow, read by the meta workflow. Sources: `.rota/clickI_night156.db`
and the night databases of 150 to 155, opened `?mode=ro`;
`.rota/clickI.principal.jsonl`; `.rota/night156.log`. Scripts:
`f298_turns.py`, `f298_count.py`, `f298_route.py` and `f298_near.py` in
session 6977407c's scratchpad.

## 0. The problem in plain words

Think of a shop. You ask for one job. The clerk writes your job on a card.
Under the job, a small grey line says "places in the shop with these words
on the shelf label". Nobody chose that line. A machine prints it from the
words on the card, every time the card is shown.

Later, the foreman writes a real plan of which shelves he will open. That
plan has its own numbered line, and you can correct it. When you do, the
foreman redraws his plan and keeps working. That route works: in the last
six nights it redrew the plan 19 times out of 20.

On three cards you saw only the grey line, not the foreman's plan. You said
"this points at the wrong shelves". The clerk had no place to put that,
because the grey line belongs to nobody. So the clerk wrote "he rejects the
job". Rejecting the job stops any work already started on it. Then the
person who keeps the card copied your words about shelves into the job
itself. The machine read the new words, found more labels with "test" and
"flag" and "option" on them, and printed a worse grey line. You corrected
it again, and the loop went on.

On the third card the foreman's real plan was already right. Only the grey
line was wrong. Your correction of the grey line stopped work that matched
what you wanted.

So the problem is: a line you can read and correct has no owner. Your
correction can land only as a rejection of your own request, and that
rejection stops the work.

## 1. The pages

**The page kinds for one request** (observed: `_page_body`,
`_park_page`, `_shift_page` in `rota/roles/principal.py`, and the pages of
night 156 in the jsonl).

| Page | Opens with | Numbered rows | Rulings a row takes | Where files appear |
|---|---|---|---|---|
| confirm | "Did I hear you right?" | the statements (quoted), then other rows | approve, contest, revise | nowhere |
| present, sign-off or agenda | "Here is what I understand you want" | request items, their criteria, the account, "It would", "It would not", then the team's notes (ledger rows, terms, other) | approve, contest, revise. A revise of a team's note is refused. An approve of a stamped request row off the sign-off page is dropped by `land` | the unnumbered "code that names these words" line under each request item (`request_block`, `near=True`) and under each "It would" row. It is no row |
| touch | "Before I build this, here is what I expect to touch" | the request item and criteria, the account rows, then the batch line under "The team expects to touch" | batch line: approve is dropped; contest or revise is kept before the head commit, and after it when the words fault the line (frame 255). An approve of an item is dropped on this page | the numbered batch line, from `batch_touch` through `touch_words`. No pointer under line 1 (`near` is False) |
| stopped | "The team stopped work on this change" | the same rows as touch, plus "The team gave up on" | the same as touch | the numbered batch line |
| park | "This change stopped. The team tried N times" | the item and its criteria | an approve of every row is the ceiling. A contest or revise goes to the owners | the failing test paths in "The last attempt", unnumbered |
| shift | "You asked for something new" | one line, the earlier item | later, now, drop | nowhere |
| clarify | "I need one thing from you" | none. Keys are row ids | a partial map. A row left out is parked | a batch's touch words as an unnumbered bullet under "This is about", when a batch is a ref |

(observed: the code at HEAD; the page texts m22, m100, m104, m145, m191,
m200 in the jsonl.)

**The pointer line and the batch line never share a page** (reasoned: the
touch and stopped branches call `request_block` without `near`, and the
present branch shows no batch row unless the wake put a batch in the refs).
On night 156 no present of the "Here is what I understand" kind carried a
batch ref (observed: `messages.body_refs` of m22 to m215).

## 2. The three deaths of night 156

### 2.1 echo_json, m22 to m45. No batch existed.

No row of `batches` names `echo_json` on night 156 (observed: `batches`).
Every page was a present with the pointer under line 1.

1. **m22.** Line 1 is the item, the pointer reads `tests/test_termui.py,
   tests/test_utils/test_echo.py, tests/test_context.py`. Line 2 is the
   account. Line 3 is a team's note. His reply m23: "Line 1 points at the
   wrong code: echo itself lives in click's utils module, and the termui and
   context tests have nothing to do with this change ... The rest of the
   page is fine." s106 and s107 sent `{1: contest, 2: contest, 3: approve}`
   three times each. `_line_refusal` refused each: "The words name line 1
   and do not name line 2." The runner ended both. No ruling. The page came
   back with "Your last answer to this page did not reach the team"
   (observed: `turns` s106, s107; the jsonl at 05:33:11).
2. **m22 again, reply m24.** "On line 1, keep my request as written but
   change the code it points at: drop the terminal UI tests and the context
   tests, and point at the echo function in click's utils module and the
   echo tests. On line 3, add that the helper uses only the standard library
   json module ..." s108 sent `{1: revise, 2: approve, 3: revise}`. The
   team's-note door refused line 3. s108 sent `{1: revise, 2: approve, 3:
   contest}`, and it landed as `r_beb6f61b09`: `echo_json: revise`
   (observed: `turns` s108; the jsonl `next` row). He asked to keep line 1.
   The page offered no row for "the code it points at", so line 1 was the
   only row the words could reach (reasoned: `_page_body`).
3. **land.** `"revise": "contested"`. The item went `contested` (observed:
   `land` at principal.py about 2030; `items` ends `contested`).
4. **s110**, the Vision Keeper relay, tried `set_approval(approved)` four
   times. The frame-190 door refused each: "the principal ruled echo_json
   revise. land wrote `contested` ... Leave it" (observed: `turns` s110).
5. **s111**, `tick:contested`, called `problem.assert` with his words
   appended: "... Drop the terminal UI tests and the context tests, and
   point at the echo function in click's utils module and the echo tests.
   The helper uses only the standard library json module ..." The item went
   to version 2 (observed: `turns` s111; `items.version` = 2). The brief
   `vision_keeper/contested.md` tells the seat to amend with the
   principal's words, so the seat did what it was told (reasoned: the brief).
6. **m32 and m40.** Line 1 now shows his correction as request text, and
   the pointer reads `tests/test_options.py, tests/test_termui.py,
   tests/test_basic.py`. Replies m33 and m41: "Line 1 still points at the
   wrong code ... take my correction notes out of the request text". s117,
   s118 and s129 met "'2' is not a line of the page" and then landed `{1:
   contest}`. s120 and s131 wrote `contested` again. s121, s123 and s126
   re-asserted the same version-2 text, so the version did not move
   (observed: `turns` s117 to s131).
7. **m44, reply m45.** He faulted line 1 again and contested the Critic's
   note. s134 landed `{echo_json: approve, challenge_items_echo_json:
   contest}`. `config` holds `stamped:m44 = ["echo_json"]`, and `land` drops
   an approve of a stamped row. The item stayed `contested` (observed:
   `config`, `items`; reasoned: `land` about 1895). The night read records
   the contested tick quarantined at s128 (copied: `plans/night156-read.md`,
   section 3).
8. The shift page then set echo_json aside on his "Later" (observed: the
   jsonl at 05:36:24).

No batch died here because none existed. The request died in a loop.

### 2.2 bg_2, m122 to m125. A batch existed. Its line was not on the page.

bg_2 was live with no head commit. Its `batch_start` tick was quarantined
(observed: the m104 page, "The team gave up on: batch_start for bg_2, 3
attempts"). bg_2's batch line was line 5 on m100 and m104, and he approved
it on m104 (observed: `r_2ae69e4282`, `bg_2: approve`).

1. **m122** is an agenda present. Refs: three team's notes, one ledger row,
   the item and its three criteria. No bg_2 (observed: `messages.body_refs`).
   Line 1's pointer reads `tests/test_options.py, tests/test_basic.py,
   tests/test_defaults.py`. His reply m123 says "Lines 1 to 4 are fine as
   written" and asks where line 8's code is from.
2. s238 asked m124 instead of a ruling. His reply m125: "As far as I know,
   that code doesn't do this ... please build the flag as new work. The
   Python version should come from sys.version_info as major.minor.micro."
3. **s239** sent `{1..4: approve, 5: contest, 6: contest, 7: revise, 8:
   approve}`. The team's-note door refused line 7: "revise rewrites a line
   of what the principal asked for: line 1, version_option_show_python.
   Revise the line the words are about." s239 moved the revise to line 1,
   and it landed as `r_07fab4102f`: `version_option_show_python: revise`
   (observed: `turns` s239; the jsonl `next` row).
4. `land` wrote `contested`. `cancel` fired: "do:cancel: abandoned bg_2: its
   item is no longer schedulable" (observed: `night156.log` line 103).

This death is not a files correction. No word of m125 faults line 1 or a
file. The cause is the refusal text that offered line 1, frame 296's wall
(copied: `plans/night156-read.md`, section 3, death 2). Frame 296's edit at
9c4b5368 offers line 1 only when the words name it or quote it
(observed: `rota/roles/api.py` at 9c4b5368).

### 2.3 bg_3, m191 to m192 and m200 to m216. A batch existed. Its line was not on the page.

bg_3 had head commit `2a50023` (observed: `batches`). Its touch rows were
already narrowed to `src/click/decorators.py::custom_version_option`,
`::version_option` and three `tests/test_basic.py` version tests (observed:
`batch_touch` for bg_3). That narrowing came from his own m145 correction
through the batch-line route (section 3).

1. **m191** is an agenda present. Refs: seven ledger rows, the item and its
   criteria. No bg_3 (observed: `messages.body_refs`). Line 1's pointer
   reads `tests/test_options.py, tests/test_basic.py,
   tests/test_defaults.py`. bg_3's real prediction does not name
   `test_options.py` or `test_defaults.py` (observed: `batch_touch`).
2. His reply m192 faults lines 2 to 4, 9 and 11, and ends: "Line 1 also
   names the options and defaults test files, which have nothing to do with
   this change, so keep the work to version option and its tests in the
   basic tests file."
3. **s322** sent a map with no ruling on lines 5 to 8 and 10, was refused,
   and then landed `{1: contest, 2: contest, 3: contest, 4: contest, 9:
   contest, 11: contest, the rest: approve}` as `r_e244215675` (observed:
   `turns` s322). The words name line 1, so no door refused the contest
   (reasoned: `_line_refusal` admits a contest on a named line).
4. `land` wrote `contested`. `cancel` fired: "do:cancel: abandoned bg_3: its
   item is no longer schedulable" (observed: `night156.log` line 150).
5. **s327**, `tick:contested`, amended the item to version 3 with his test
   notes inside it: "... turning the flag on to check that the message ends
   with "Python" ... The show_python option should be a normal keyword
   argument with no callback from the caller." (observed: `turns` s327; the
   m200 page).
6. **m200 and m215.** Line 1 shows the polluted text. The pointer reads
   `tests/test_options.py, tests/test_basic.py,
   tests/test_shell_completion.py`. m201: "Line 1 still names the options
   and shell completion test files ... and it mixes in my notes about the
   tests." m216: "Line 1 is still wrong." s333 and the m215 session landed
   `version_option_show_python: contest` again (observed: the jsonl `next`
   rows `r_4d37b78c88`, `r_80727d2fad`). No batch existed after m192.

**Summary of the three.**

| Death | Batch at the reply | Batch line on the page he answered | What his words faulted | What killed it |
|---|---|---|---|---|
| echo_json | none | no | the pointer | no batch. The request looped `contested` |
| bg_2 | bg_2, no head commit | no | a team's note, line 7 | the refusal offered line 1, the revise landed there, `cancel` |
| bg_3 | bg_3, head `2a50023` | no | the pointer, and criteria | the contest of line 1 for the pointer, `cancel` |

## 3. The route that exists

**On a touch or stopped page, a files correction of the batch line keeps the
batch and redraws the prediction** (reasoned: the code at HEAD; observed:
the counts below).

1. `rulings_rule`, the batch-line door after "A batch line is a prediction
   of what the change touches". Before the head commit, a contest or revise
   of the batch line passes. After it, the line passes when
   `built_line_faulted` reads a fault of that line in the words. Otherwise
   the refusal is "line N: the words do not fault bg_x's files. Approve line
   N." A merged or abandoned batch is refused: "the change is merged ... To
   change what you asked for, contest the item".
2. `land` keeps the batch ref with contest or revise in the verdict, and
   drops item approves on the touch page, so the item stays `approved`.
3. The Liaison's `verdict_signoff` relays the batch to the Architect.
   `_owner_of_ref` sends a batch id to `architect`, keyed to `annotate`.
4. The Architect calls `batches.annotate` and replaces the touch rows. The
   next page shows the new prediction. `cancel` does not fire, because the
   item is still approved at its version.

**Night 156's m145 is the route working.** "Line 5 lists far too much ...
please keep the work to version option and its own tests." `r_1258ac05f9`
landed `bg_3: contest` with the item approved. s261 relayed bg_3 to the
Architect. s262 called `batches.annotate`. m165 shows the batch line cut
from 40 grains to 5. bg_3 lived (observed: the jsonl, `tool_calls` s260
to s262).

**The count, nights 136 to 156.**

- Nights 136 to 149: 16 files corrections at a batch line, 0 landed on the
  batch line. 5 made no ruling and 11 approved the line. The route did not
  exist after the head commit until frame 255 (copied:
  `plans/frame255-scope.md`, section 1, 2026-10-15).
- Night 150: no files correction on a page with a batch line. Its three
  batch-line contests fault other things (observed: `f298_count.py`).
- Nights 151 to 156: 20 files corrections on a page with a batch line. 20 of
  20 landed a contest or revise of the batch line. 19 of 20 relayed to the
  Architect and an `annotate` followed (observed: `f298_route.py`).
  - 15 of 20 kept the item approved in the same ruling. Of those, 9 batches
    merged, 1 was running at the night's end, and 5 ended abandoned later.
    The abandonments came after the correction, not from it (reasoned: the
    item stayed approved and `cancel` needs an unapproved item. The cause of
    each later abandonment is not read here).
  - 3 of 20 (night 155, m61, m92 and m178) also contested the item in the same
    ruling, and the batch ended abandoned (observed: `per_item`).
  - 2 of 20 (night 155, m224 and m230) had no item key, on a page
    without the item. bg_5 ended abandoned.
  - Night 155's m61 is the one with no relay.

**Why the route did not apply to the three deaths.** The route reads a ruling
on a batch ref, and the three pages he answered held no batch ref. The only
file list on those pages was the pointer under line 1, and the pointer is
no row (observed: `body_refs` of m22, m32, m40, m44, m122, m191, m200,
m215). His files words then had one row to reach, line 1, the request
itself. A contest or revise of line 1 writes `contested`, and `cancel`
abandons any live batch of the item. For echo_json no batch existed, so the
route had nothing to redraw even in principle. For bg_3 the batch existed
and its prediction was already right, but the agenda present did not show
it.

## 4. The pointer

**`near_code` computes the line from the item's current text at every
render, and no row stores it** (observed: `principal.py` 1592 to 1621; the
map tool lists only `code_index` as read, and two callers, both render
paths).

1. It lowercases the text, splits on spaces, and keeps alphanumerics and
   `_`.
2. It keeps words of 4 or more letters not in `STOP_WORDS`, and adds the
   singular of a word that ends in "s".
3. It counts, per file, the `code_index` symbols whose name **contains** a
   kept word as a substring.
4. It returns the 3 files with the most hits.

**Why the appended text named more wrong files** (observed: `f298_near.py`,
the night-156 index, 2026-10-18 11:3x).

| Text | Top hits | Pointer |
|---|---|---|
| echo_json v1 | "echo" 24, "line" 11, "object" 6 | test_termui 8, test_echo 6, test_context 5 |
| echo_json v2, his words appended | "test" 550, "echo" 24, "context" 21, "use" 14 | test_options 100, test_termui 66, test_basic 41 |
| version option v2 | "flag" 47, "version" 8 | test_options 36, test_basic 9, test_defaults 4 |
| version option v3, his test notes appended | "option" 81, "flag" 47, "argument" 28 | test_options 57, test_basic 27, test_shell_completion 13 |

The words he used to drop files, "tests", "context", "option", match
hundreds of test-function names, because "test" is no stop word and the
match is a substring. The ranking counts symbols, so a test file with many
functions beats the one source file that defines `echo` (1 hit in
`src/click/utils.py`). His correction text is the strongest input the
pointer ever reads (reasoned: the counts above).

**No row stores the pointer.** The `stamped:` config rows hold item ids
only. The page text exists only in the principal jsonl, which no seat reads
(observed: `config` for m22 to m215; reasoned: `near_code` writes nothing).
So no ruling, relay or seat can move it. The pointer moves only when the
item's text moves.

## 5. The smallest change

Three shapes. Each cycle count is an estimate (reasoned: the anchors of
`plans/operating-facts.md`, a door 2 cycles, a seam design with its night 8
to 10).

**Shape A. The door sends a pointer fault to the change, and the page stays
as it is.** About 4 cycles: door and land, one review, one night.

- `rulings_rule` in `rota/roles/api.py`: when a contest or revise of a
  request line rests on words that fault only files, refuse it. With a live
  batch of that item, the refusal names the batch as a key the seat may
  rule: "line 1's files are the index, not your request. The change bg_3
  holds the prediction. Rule bg_3 with the words." The door admits that
  off-page batch key for the page's own item. With no batch, the refusal
  says "approve line 1. No change exists yet to correct".
- `land` in `rota/roles/principal.py`: the batch filter runs only when a
  batch is in the page's refs, so an off-page batch contest already stays in
  the verdict. One test pins it. The rest of the route is unchanged.
- What he sees: the same page. What the Liaison records: a batch ruling
  from an agenda page. Who talks to whom: unchanged, the Architect already
  takes batch corrections.
- Law 9 and the amendment ruling: not touched. Fewer `contested` writes
  means fewer cancels, and a files fault is no amendment of the request.
- Roman's ruling: not needed by the composition rule (reasoned).
- Limit: the pointer stays wrong on the page, so he may correct it again.
  The files cue needs a count on nights 136 to 156 before its pass:
  fires on how many pointer faults, refuses how many right request
  contests.

**Shape B. The page shows the change's own prediction under the request
when a change exists.** About 8 cycles: a seam design with its night.

- `request_block` and `_page_body` in `rota/roles/principal.py`, and the
  door's stamp in the present path of `rota/core/sandbox.py`: on a present
  about an item with a live batch that has touch rows, stamp the batch into
  the refs and number its line. Drop the pointer for that item. Before any
  batch, keep the pointer, and compute it from the request's first text,
  with "test" and "tests" as stop words.
- His files words then reach the batch line, and the route of section 3
  carries them. 19 of 20 such corrections redrew the prediction on nights
  151 to 156.
- What he sees: a new numbered line on agenda pages. Who talks to whom:
  unchanged.
- Law 9: not touched. The P4 ruling of 2026-09-03, coarse beside the items
  and grounded before the build, is touched: the coarse line goes away once
  a grounded one exists.
- Roman's ruling: needed, because it changes what the principal sees.

**Shape C. The pointer becomes a row with an owner.** About 10 or more
cycles: a new row, its identity, a graph edge, a door and a brief.

- A pointer row per item (or `batch_touch` rows with a confidence of
  `index` on a pre-batch), numbered on the page, owned by the Architect. A
  ruling on it relays to the Architect, who rewrites it. The grounded touch
  note later starts from it.
- Files: `rota/roles/principal.py`, `rota/roles/api.py`,
  `rota/core/sandbox.py`, the schema, `architect/annotate.md`.
- What he sees: a new numbered line on every present. Who talks to whom:
  the Architect takes a correction before any batch exists, the judged
  guess that P4 piece 2 deferred.
- Law 9: not touched. The P4 ruling is touched, and the composition is
  touched.
- Roman's ruling: needed.

**Beside every shape: the Vision Keeper's amendment carried the pointer
words into the request text twice** (observed: s111, s327). Shape A stops
the contest that wakes it. Shapes B and C stop it only when the words land
on the new line. A pointer fault that still lands on line 1 keeps this
second harm (reasoned).

**Recommended: shape A first.** It closes bg_3's death with no change of
the page, and it needs no ruling. Shape B is the shape that stops the
repeat corrections, and it goes to Roman as a page question (reasoned: the
three deaths and the route's count).
