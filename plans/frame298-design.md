# Frame 298, the design: the Architect owns the scope guess at sign-off, and the Liaison relays its correction

Read-only design agent on Opus, 2026-10-18 12:17. Repository at HEAD
5902981b. Amended after the design review at 2026-10-18 12:37, HEAD
620eb0d3 (section 10). Rota workflow, designed by the meta workflow.
Sources: `plans/frame298-investigation.md`, `plans/frame298-count.md`,
`plans/archive/p4-scope-disclosure.md`, `plans/frame190-design.md` 2.2,
`rota/LAWS.md`, `plans/composition.md`, `plans/frame298-design-review.md`,
and the code at HEAD. One probe: `f298d/base.py` in session 6977407c's
scratchpad, run on the night databases 136 to 156 opened `?mode=ro`.

The ruling this design builds (ruled: Roman, 2026-10-18 about 12:05, in the
terminal): "Remove the mechanical guess, the architect owns the guess", and
"The Liaison relays, the Architect rewrites".

## 0. The design in one paragraph

The index line "code that names these words" leaves every page. A new
table, `touch_guesses`, holds the Architect's guess of the code that one
request item touches. A new predicate, `guess`, wakes the Architect once per
request item and item version, before the sign-off present. The send door
stamps a ref `guess:<item>` into each present that numbers the item, and it
records in the same send which row that line shows: one guess version, or
one live batch's prediction. The render and `land` read that record and
never decide again. A contest or a revise of the line relays the
principal's words to the row he saw: to the Architect's `guess` mode for a
guess, or to `annotate` for a batch, with frame 255's check kept for a
built batch. A files correction that still lands on the request line meets
a door that refuses it and names the code line. The item stays approved, so
`cancel` does not fire.

## 1. The row

### 1.1 The choice: a new table, in the Architect's `batches` artefact

**Write a new table, `touch_guesses`. Do not reuse `batch_touch`**
(reasoned: the schema and the readers at HEAD).

| Cost | Reuse `batch_touch` with a pre-batch key | New table `touch_guesses` |
|---|---|---|
| Schema | `batch_id` is `REFERENCES batches(id)` and `confidence` has a `CHECK`. An item key breaks the foreign key. SQLite changes a foreign key only by a table rebuild, so every old night database needs a migration | one `CREATE TABLE IF NOT EXISTS`. Old databases gain the table at open |
| Readers | 10 readers read `batch_touch` (observed: `python -m rota.tools.map table batch_touch`). Each needs a guard against item keys | no reader until this frame adds them |
| Versions | `batch_touch` keeps no version. A rewrite clears the rows | each write is its own set of rows, and the Architect's first guess survives a correction |
| Identity | the key `batch_id:grain` would carry two kinds of subject | one kind of subject |

The new table costs less. The reuse saves one `CREATE TABLE` and costs a
migration and ten guards (reasoned: the table above).

**The table joins the `batches` artefact in `rota/core/db.py`, beside
`batch_touch`** (reasoned: law 1 and law 3). The Architect already writes
that artefact, so law 1 holds with no new writer. Law 3 derives contacts per
artefact, so a table inside an existing artefact adds no edge (checked:
the review, "Law 3 needs no edge", 2026-10-18 12:31).

### 1.2 The table

```sql
-- The Architect's guess of the code one request item touches, before any
-- batch exists. P4 piece 2 in its judged form (ruled: Roman, 2026-10-18,
-- "the architect owns the guess"). A prediction, never a permission (law 12).
-- A correction writes a new set beside the old one, so the Architect's own
-- guess stays countable.
CREATE TABLE IF NOT EXISTS touch_guesses (
    item_id     TEXT NOT NULL REFERENCES items(id),
    item_ver    INTEGER NOT NULL,           -- the item's version at the write
    ruling_id   TEXT NOT NULL DEFAULT '',   -- the ruling a rewrite rests on; '' for the Architect's own
    grain       TEXT NOT NULL,
    grain_kind  TEXT NOT NULL CHECK (grain_kind IN ('path','symbol')),
    confidence  TEXT NOT NULL DEFAULT 'expected'
                CHECK (confidence IN ('expected','possible')),
    PRIMARY KEY (item_id, item_ver, ruling_id, grain)
);
```

- **Identity, law 14.** Class `relation` in `rota/core/identity.py`: "the
  (item, item version, ruling, grain) tuple; a guess set is the rows of one
  (item, item version, ruling)". The key holds no counter. A second relay
  of one ruling writes the same rows again, which is the same rows (answers:
  review finding 9).
- **The guess set and its order.** A guess set is the rows of one
  `(item_id, item_ver, ruling_id)`. The sets of one item are ordered by
  their first `rowid`, at read. The current guess is the last set. A
  "version" in this record means a set, numbered at read by that order.
- **Junction.** The table has no `id` column, so it goes into
  `JUNCTION_TABLES` in `rota/core/db.py`, as `batch_touch` does.
- **Writer.** The Architect alone, through one op, `batches.guess`, by the
  pipeline (`ctx.writes`).
- **When.** After the Vision Keeper drafts the item, and before the
  sign-off present when the frontier allows it (section 4).
- **What it holds.** Paths always, symbols only where the Architect is
  confident, the split of `batches.annotate`. Symbols are `possible`.
- **Provenance, law 11.** The table is no model, glossary, problem or frame
  row, so law 11's view does not cover it, as for `batch_touch`. The op
  writes `ruling_id`, never the seat.

### 1.3 How the batch's prediction starts from the guess

1. The `annotate` wake's working set gains one pushed key, `the item's
   guess`, the current guess set's paths and symbols (site:
   `push_working_set` in `rota/core/runner.py`, beside the `tick:annotate`
   hint).
2. When the current set rests on a ruling, the key also carries the
   principal's words of that ruling, read from `entry:<verdict id>`.
3. `architect/annotate.md` gains one sentence: "`the item's guess` is what
   you guessed at sign-off, and what the principal corrected. Start from it.
   Read the source, and change a path only where the source says it is
   wrong."
4. Nothing copies rows. The measurement's truth is the merged diff, not
   `batch_touch`, so this seed does not touch the measure (section 5).

## 2. The page

### 2.1 The code line, stamped once at send

**The send door decides the row the line shows, records it, and every later
read uses the record** (answers: review finding 2).

1. **The stamp.** In the present path of `rota/core/sandbox.py`, beside
   the `stamped` block, after `request_rows`: for each request item the
   refs hold, decide the target in this order.
   - When the refs hold a batch of the item, the page is a touch or a
     stopped page. Stamp nothing.
   - When the item has a live batch (`pending`, `deferred` or `running`)
     with `batch_touch` rows, the target is `{"batch": <batch id>}`.
   - When the item has a guess set, the target is `{"guess": [<item_ver>,
     <ruling_id>]}`, the current set at the send.
   - Otherwise stamp nothing (2.3).

   Add `guess:<item>` to the refs, add it to `stamped`, and write one door
   row, `config` key `code:<message id>`, a JSON map of `guess:<item>` to its
   target. `door_rows` reads it as it reads `stamped` and `stalled`.
2. **The render reads the stamp.** `request_block` renders the line from
   the stamped target only. A guess target renders that set's rows, frozen.
   A batch target renders that batch's rows live, which is how a batch line
   renders today. A batch target whose batch is merged or abandoned at the
   read renders "The team's plan for this change is closed." and keeps its
   number. The line number never moves, because the ref is in the refs.
3. **`land` reads the stamp.** It never looks for a live batch (3.2).
4. **The ref is a page alias.** `guess:<item>` derives from the item id, so
   law 14 holds. `_page_body` adds it to `in_block`. `_items_reached` returns
   the item for it, so `off_page` keeps it on its own request's page.
5. **The page.** After the item's line, before "It must:":

   ```
   You asked:
     1. Give version_option a show_python flag that appends the running Python version to the message.
     2. The team's guess at the code this touches: src/click/decorators.py, tests/test_basic.py. It might touch src/click/decorators.py::version_option.
   It must:
     3. ...
   ```

   With a batch target, line 2 reads "The team's plan of the code this
   touches: expected to touch ...; might touch ...", with no unsurveyed
   ground and no commitments, which are the touch note's.
6. **When the guess and the batch's prediction differ.** The principal sees
   one list per item on one page, never both. Before a batch holds rows, he
   sees the guess. Once a live batch holds rows, every later page shows the
   batch's plan, labelled "plan", not "guess". The touch note already showed
   him the same plan before the build. The guess rows stay in the table for
   the measurement, and no page shows them again (reasoned: P4 puts the
   grounded prediction before the build; night 156's bg_3 died with a right
   prediction that no page showed).
7. **Words, no seat names.** The page says "the team", as every page does
   today. "The Architect's guess" is the meta workflow's name.

### 2.2 The index line leaves

- `request_block` loses its `near` argument and the two lines that call
  `near_code`. `_page_body` loses the `near_code` lines under "It would:".
  "It would" rows get no replacement.
- `near_code` and `STOP_WORDS` leave `rota/roles/principal.py`. Their only
  callers are those two render paths (observed: the map tool). The pins
  change: `tests/rota/test_signoff_assumptions.py:526` pins the guess line,
  and `tests/rota/test_index_refresh.py:105` reads `code_index` straight.

### 2.3 When the Architect has not written yet

The present can go out before the guess exists (section 4). The send door
then stamps nothing, and `request_block` writes one unnumbered line under the
item: "     The team has not guessed the code this touches yet." No ruling is
owed on it. A files correction on such a page meets the door of 3.3, which
names the key `guess:<item>`.

### 2.4 The closing instruction

`_name_guess(lines)` follows `_name_request` in the "Here is what I
understand" branch: " To correct the code it touches, name line 2." With
two request items: " To correct the code they touch, name line 2 or 5."
The numbers come from the order. With no code line, the sentence is left
out.

## 3. The route

### 3.1 A ruling on the code line, in `rulings_rule`

**One door, after the team's-note revise door and before the batch-line
door** (site: `rulings_rule` in `rota/roles/api.py`, at HEAD 620eb0d3 lines
9679 to 10009, the batch-line door at about 9858).

1. **Approve** passes. `land` drops it, as a stamped approve.
2. **A guess target.** Contest or revise passes when the words are not
   empty.
3. **A batch target.** The batch-line door's rules apply to the code line:
   a merged or abandoned batch takes that door's refusal. Before the head
   commit, contest or revise passes. After it, the line passes only when
   `code_line_faulted` holds: `built_line_faulted(words, order,
   "guess:<item>", read_faulted)`, or `pointer_fault(words, <request
   line>, code_lines)`. The first reads the ref's place in the order, so it
   takes the alias unchanged (observed: `built_line_faulted` at
   `api.py:9244`, HEAD 620eb0d3). The second admits the words that 3.3's
   cue sends to this line, so the cue's refusal never leads the seat into a
   second refusal (copied: `plans/frame298-count.md`, section 4, "or the
   first text sends the seat into a second refusal"). `land` reads the same
   `code_line_faulted`, so the two doors do not drift (answers: review
   finding 2, the skipped check).
4. The code lines join `batch_lines` in the `_line_refusal` call, because
   they hold only files.
5. **The off-page key.** A key `guess:<item>` where the item is a request
   item of the page's order is admitted with no stamp. Its target is the
   guess, because a page with no code line had no batch to show (2.1, point
   1).

### 3.2 What `land` writes

1. A `guess:` key with approve leaves `per_item`.
2. A `guess:` key with contest or revise stays. `land` writes no `items`
   state for it, so the item keeps its approval and `cancel` cannot fire
   (checked: the review, `cancel` reads only `items.approval` and
   `approval_ver`).
3. **The target from the stamp.** `land` reads `code:<message id>`. A batch
   target puts that batch id in the verdict in place of the key, after the
   built-batch filter. For a built batch, `land` keeps the row only when
   `code_line_faulted` holds, as in 3.1 point 3. A guess target, or no stamp, keeps
   the `guess:` key and writes `guess_target:<verdict id>` with the stamped
   set, so the Architect sees the set the principal read.
4. `verdict:<id>` and `entry:<id>` are written as for any ruling.

### 3.3 The door on the request line: the files cue

**A contest or revise of a request line whose words fault only the code is
refused, and the refusal names the code line** (reasoned: the count;
observed: `plans/frame298-count.md`, section 3).

- **The predicate.** `pointer_fault(words, line, code_lines)` from the count's
  section 3, ported to `rota/roles/api.py` with its patterns copied exactly.
  `code_lines` are the page's code lines and batch lines.
- **Its count, in-sample** (copied: `plans/frame298-count.md`, 2026-10-18
  11:4x): fires on 19 of 19 pointer faults and 8 of 8 batch-line faults.
  Refuses 43 of 43 right request contests, 18 of 18 (c) rows and 13 of 13
  (d) rows. The next night's count is the real count.
- **Three texts, every number from the order** (answers: review finding 5).
  `<n>` is the request line, `<m>` the code line or the batch line.
  1. A code line on the page: "line <n> is the request, and the words fault
     only the code it touches. That code is line <m>, and the team rewrites
     it from the principal's words. Rule line <m> contest with the words,
     and approve line <n>."
  2. A touch or stopped page: "line <n> is the request, and the words fault
     only the code it touches. That code is line <m>, the change's plan. Rule
     line <m> contest with the words, and approve line <n>." Line <m> then
     takes the batch-line door of today.
  3. No code line: "line <n> is the request, and the words fault only the
     code it touches. The team has not guessed that code yet. Rule the key
     guess:<item> contest with the words, and approve line <n>."
- **Placement.** After the team's-note revise door. A (c) reply does not
  fire the cue and lands on the request line as today (section 7).

### 3.4 The relay and the Architect's mode

1. **The send door's ref check.** `_bind_send.stage` in
   `rota/core/sandbox.py` (the `dangling` check, line 2876 at HEAD 620eb0d3)
   refuses every ref that `api.ref_resolves` (`rota/roles/api.py:4791`)
   does not resolve, and `guess:echo_json` resolves False (copied: the
   review's probe 2). `ref_resolves` gains one rule before its table loop:
   a ref that starts `guess:` resolves when the rest is an `items` id and
   `_is_request_item` holds for it. The test sends a Liaison relay with
   `guess:<item>` through the real `stage` and asserts no refusal, and asserts
   the refusal for `guess:<not an item>` (answers: review finding 1).
2. **The split.** In the relay split of `rota/core/sandbox.py`, a `guess:`
   ref goes to `architect` + `GUESS_RELAY`, a new constant `":guesses"`
   beside `BATCH_RELAY`. A batch id from a batch target takes today's
   `BATCH_RELAY` branch.
3. **`_owner_of_ref`** gains one rule before the ledger lookup: a ref that
   starts `guess:` goes to `architect`.
4. **The Liaison's briefs.** `verdict_signoff.md` gains one table line:
   "the code line — `msg.relay_architect`". `landing.md` gains one line:
   "The line under a request is the code it touches. Words about files,
   tests or paths go on that line, never on the request." (answers: review
   finding 12.)
5. **The mode key.** The predicate is named `guess`, so the tick wake
   `tick:guess` keys the mode `guess` through the `tick:` branch of
   `_mode_key` (answers: review finding 12). A relay to the Architect whose
   refs hold a `guess:` ref keys `guess` too, by the shape of the
   `batch_relay` key.
6. **The working set** (answers: review finding 11). For `tick:guess`: the
   item row (id and text), a `code.callables` hint from the item text, and
   the index's test files. For a guess relay, in `resolve_inbound` beside
   the batch-relay block: the item row, `guess` with the paths of the
   target set from `guess_target:<verdict id>`, and `disputed` from
   `disputed_paths(principal_said, paths, ...)` with the disputed paths
   taken out of `guess`, the shape of the batch relay. Also the index's test
   files.
7. **The op.** `batches.guess(item_id: str, paths: list[str], symbols:
   list[str] | None = None) -> dict`, listed in `guess.tools`. It refuses: an
   item that is no request item; an empty `paths`, "a guess names at least
   one path. A new file goes beside the files that exist"; a path under a
   directory the index lacks (the check of `batches_annotate`); a symbol
   with no `::`; and a second call for the same item in one session (answers:
   review finding 10). In a session woken by a principal relay whose
   verdict rules `guess:<item>` contest or revise, it writes the set with
   `ruling_id` set to the ruling. Otherwise `ruling_id` is ''. It returns
   `{"item_id", "grains"}`.
8. **The brief `architect/guess.md`, whole:**

   ```
   MODE: guess — guess what one request touches, before any plan.

   The request is `item` in your working set. `code.probe` and
   `code.callables` show where that work lives. Then call `batches.guess`
   once for the item.

   Paths always. Symbols only where you are confident. A test path is one
   of `the index's test files`, or a new file you name as new.

   **This is a guess, not a permission.** Nothing rejects a diff for straying
   outside it. Name the files you expect the change to edit, not every file
   that mentions its words.

   **A ruling of the principal.** When the message is a relay with
   `principal_verdict` on the guess, the principal read `guess` and
   corrected it. The words are `principal_said`. The paths under `disputed`
   are the ones the words call wrong. Call `batches.guess` once with the
   paths the words name and the paths of `guess`. Then stop.

   After the call, end the session with one line: "guessed <item>."
   ```

9. **The re-present.** No new predicate. The next page of the item renders
   the new set when its send stamps it. After an approve, the next page is
   the touch note, which shows the batch's plan that started from the
   corrected guess (1.3). R7 holds.

### 3.5 When a batch already runs

- Every page sent while a live batch holds rows stamps the batch (2.1). A
  ruling on it goes to `annotate`, today's route, which redrew the
  prediction on 19 of 20 files corrections of nights 151 to 156 (copied:
  the investigation, section 3). A built batch keeps frame 255's check.
- A page stamped with the guess before the batch formed still sends the
  ruling to the guess, because the principal read the guess. The Architect
  rewrites the guess set. The live batch's rows do not move, and its touch
  note or its next page shows its plan for him to correct there (reasoned:
  his words land on the row he read, ruling DECISIONS 1445).
- bg_3 on night 156 under this design: m191's line 2 is stamped with bg_3,
  whose prediction was already right. m192's words fault line 1's files, the
  cue fires (row 98), the door names line 2, and `{2: contest}` meets
  `code_line_faulted`, because bg_3 had a head commit. The cue half holds,
  so the contest lands, the item stays approved, and the relay takes the
  words to `annotate` for bg_3. bg_3 lives, which is the wall's fix
  (reasoned; the pass 3 red case pins the outcome).

### 3.6 A files sentence that still lands on the request line

The door of 3.3 refuses it and names the code line or the key. A sentence
the cue misses lands as today, writes `contested`, and a live batch is
cancelled. The night read classes those by hand (section 5).

## 4. The predicate and the wake

### 4.1 `guess`

```python
@predicate("guess", wakes="architect", band="gate")
def guess(conn) -> list[Wake]:
    """A request item with no guess of its code at its current version."""
```

- **Fires on** one item at a time: a request item (`_is_request_item`),
  approval `draft` or `approved`, not set aside (`not_parked`), with no
  `touch_guesses` row where `item_ver` equals `items.version`, with no live
  batch whose `batch_touch` holds rows, and only while `code_index` holds a
  path (copied: the `deliver` brief, "Unless there is no code yet").
- **Wakes** `Wake("architect", "tick:guess", refs=(item,))`.
- **Drains** when the op writes a row at the item's version.
- **Band `gate`, declared in the file before `signoff`** (reasoned: `ORDER`
  in `rota/core/predicates.py`, gate 20 and start 30).
- **The frontier test** (answers: review finding 7, the probe's 0 fires in
  347 tests). A new test in `tests/rota/test_frontier_order.py`: one draft
  request item, an index with a path, no guess. `frontier_readonly` returns
  `tick:guess` before `tick:signoff`. After a `touch_guesses` row at the
  item's version, it returns `tick:signoff` and no `tick:guess`.
- **Register entry.** It joins `REGISTER_ENTRIES`, the list in
  `rota/REGISTER.md` gains it, the count in
  `tests/rota/test_predicates.py:902` moves from 29 to 30, and the
  obligation lint in `rota/testkit/obligations.py` runs green with the new
  mode (answers: review finding 12).
- **An amended item** moves `items.version`, and the predicate fires again.

### 4.2 The caps

- **Depth.** One item per wake. One `batches.guess` call per item per
  session.
- **Loop.** A session that writes no row leaves the predicate true. The
  tick-attempt bound quarantines the key after three attempts. The page
  then says "not guessed yet".
- **Relay loop.** One ruling makes one relay. The principal's replies bound
  the loop.

### 4.3 What the sign-off waits on

**Nothing new** (copied: P4, "Non-blocking by R7"; reasoned: a prediction
never blocks). `tick_signoff` and the Vision Keeper's `submit` brief do not
name the guess (answers: review finding 12). The first present can go out
before the guess exists. M0 counts how often it does.

## 5. The measurement

The ruling of 2026-09-03 says the judged guess "must be measured before it
is trusted — a case with a preregistered expectation, runs on both models"
(copied: P4, piece 2).

### 5.1 The truth, from git

**The truth of a merged item is the set of paths of its merge commit's
diff** (answers: review finding 3). `worktrees.integrate` merges each batch
with `git merge --no-ff ... -m "rota: deliver <batch id>"` (observed:
`rota/core/worktrees.py:286`, HEAD 620eb0d3). The truth is `git diff
--name-only <merge>^1 <merge>` for the commit whose message is "rota:
deliver <batch id>", in that night's project repository. Neither the guess
nor `annotate` writes git, so the truth is independent of both. Pass 4
first checks that the night's repository keeps the merge commits after the
night ends, and reads them at the night's end if it does not.

### 5.2 The baseline, the index line

**The index line named a path of the merged batch's touch rows on 8 of 26
merged items over nights 136 to 156, and named a source file on 0 of 26**
(observed: `f298d/base.py`, 2026-10-18 12:1x). This baseline used
`batch_touch` as its truth. Pass 4 recomputes it against the git truth on
the nights whose repositories still hold the merge commits, and the
expectation below is compared with the recomputed number where it exists.

### 5.3 The measures

The subject of M1 and M2 is the Architect's own guess: the first set of the
item at the item's first version with `ruling_id = ''`. The models are the
night's Architect, `qwen3.5:9b`, and the recorded cases run on `qwen3:8b`
as well, so the case "runs on both models".

| Measure | How it is counted | Baseline | Expectation |
|---|---|---|---|
| M0 | sign-off pages (a present whose cause is a `submit`) of a new item that carry a code line, from `messages` and `code:<id>` rows | none | 3 of 4 or more |
| M1 | merged items whose own guess names a path of the git truth, from rows and the diff | 8 of 26 (31%), on `batch_touch` | 60% or more |
| M2 | merged items whose own guess names a path of the git truth outside `tests/` | 0 of 26 | 50% or more |
| M3 | files-only corrections that landed on a request line and wrote `contested`, of all files-only corrections | 19 of 19 (copied: the count) | 1 in 5 or fewer |
| M4 | batches cancelled after a files-only correction | 13 over 21 nights (copied: the count) | 0, by the residue rule |

**M0, M1 and M2 compute from rows and the diff alone. M3 and M4 need a
hand reading** (answers: review finding 4). A row tells a files-only
correction only after a reader classes the words, and the cue cannot count
its own misses.

1. The instrument lists every ruling that put contest or revise on a
   request line or a code line, with its words, its page, and whether
   `contested` and a `do:cancel` followed.
2. The night read classes each listed ruling by hand into the count's
   classes (a), (b), (c) and (d), by the rules of
   `plans/frame298-count.md` section 1.
3. **Cap: 30 rulings a night.** Over 30, the read classes the first 30 by
   time and writes the rest as unread. The count had 101 rows over 21
   nights, about 5 a night (copied: the count, section 0), so the cap is
   six times a usual night.

**The ratio that says the guess is worth the principal's eyes: M1 at 60%
or more and M2 at 50% or more, over at least five merged items.** A night
merges 1.24 items on average (copied: the review's finding 6, 26 over 21
nights), so five items take about four nights (answers: review finding 6).
The escalation waits on the item count, not on a night count. If M1 is at
or below the baseline after five items, the frame escalates to Roman with
P4's fallback, "mechanical only ... labelled as hits", as the recommended
answer.

### 5.4 Frame 298's ends-when on a night

1. **Mechanism.** On one night, every files-only correction the cue fires on
   lands on the code line or the batch line, and the item keeps its
   approval in the same ruling. No page shows "code that names these
   words".
2. **Ratio.** On that night's hand reading, M3 at 1 in 5 or fewer, from a
   baseline of 19 of 19, and M0 at 3 of 4 or more.
3. **Residue.** A files correction that still writes `contested` is read.
   The frame closes when its cause is not the cause this frame named. A (c)
   reply is such another cause, and it is the follow-up frame of 7.1.

The close needs one night. M1 and M2 do not gate it. They run on as a
count over about four nights and decide the escalation of 5.3.

## 6. The passes

Price anchors (copied: `plans/operating-facts.md`, cost anchors): an
implementer pass on Opus cold 74k to 217k, a reviewer pass 61k to 147k, a
cycle about 3k of the holding session with a report to a file.

**The order is 1, 3, 2, 4** (answers: review finding 7). Pass 3 changes the
door and the refusal texts before pass 2 numbers a new line on every page,
so the Liaison cases re-record once, under a working door.

| Pass | Files | Tests red first | Cycles | Review points |
|---|---|---|---|---|
| 1. The row, the op, the predicate, the mode | `rota/core/schema.sql`, `rota/core/identity.py`, `rota/core/db.py`, `rota/roles/api.py` (`batches.guess`), `rota/core/predicates.py` (`guess`, `REGISTER_ENTRIES`), `rota/core/runner.py` (the `tick:guess` working set), `rota/roles/prompts/architect/guess.md` and `guess.tools`, `rota/REGISTER.md`, `tests/rota/test_predicates.py` (29 to 30) | new `tests/rota/test_touch_guess.py`: the predicate and the op; the frontier test of 4.1 in `test_frontier_order.py`; one L1 case, `L1-AR-guess-the-code-of-a-request` | 3 | the band and the file order; the `relation` class; no raw write; the obligation lint |
| 3. The route | `rota/roles/api.py` (`ref_resolves`, the code-line door, the off-page key, `pointer_fault`, the three texts), `rota/roles/principal.py` (`land`), `rota/core/sandbox.py` (`GUESS_RELAY`, `_owner_of_ref`, the `code:` stamp, written here so the door and `land` have a stamp to read), `rota/core/runner.py` (the relay key and the guess relay's working set), `guess.md`'s ruling paragraph, `annotate.md`'s sentence, `verdict_signoff.md` and `landing.md` | **the wall's red case: night 156's s322 on m192 rebuilt**, `{1: contest, ...}` refused with line 2 named, and bg_3 not cancelled whatever the seat's second reading; night 156's s108 on m24 rebuilt with no batch, refused with the key named, and the guess relay passes the real send door; a page stamped with a guess sends its ruling to `guess` mode after a batch forms; a built batch target meets `code_line_faulted`; the 43 (b) rows still land on line 1. One L1 case, `L1-AR-rewrite-the-guess-from-the-ruling`, on m23's words | 4 | the stamp read by the door and by `land`, never a live lookup; the off-page key for the page's own item only; the patterns copied exactly; `cancel` silent |
| 2. The page | `rota/roles/principal.py` (`request_block`, `_page_body`, `_name_guess`, `_items_reached`, the line's words, `near_code` and `STOP_WORDS` removed), `tests/rota/test_signoff_assumptions.py`, `tests/rota/test_index_refresh.py`, the Liaison re-records | night 156's m191 rebuilt with a batch target and a guess target; a page before the guess; a touch page with no code line; no "code that names these words" anywhere; a closed batch target | 3 | line numbers on every page kind; one re-record of the Liaison cases |
| 4. The instrument | `rota/tools/nightreport.py` (M0 to M2 from rows and the git truth, the hand list for M3 and M4), its test | a fixture repository with two merged items, one hit and one miss, and a list of three rulings | 2 | the git truth from the merge commit; the first set only; the cap of 30 |
| The walk | a full night from a worktree at the closing commit | the night | 0, then the read 1 | |

**Total: 13 cycles with the night's read** (reasoned: the anchors). Tokens:
four implementer passes at about 100k to 200k each, four diff reviews at
about 70k to 150k each, and the night read at about 75k to 130k.

**What each pass leaves for the next.**

- Pass 1 leaves rows that no page shows. A night after pass 1 already
  writes guesses.
- Pass 3 leaves a door and a route with a stamp but no numbered line on the
  page. Its tests build the stamp by hand.
- Pass 2 leaves the night count to pass 4.
- Pass 4 leaves the night.

**The walk: a full night** (reasoned: CLAUDE.md, "a full night for the
delivery path or when in doubt").

## 7. What the design does not do

- **The (c) loop.** A reply that faults the files and the request's text in
  one breath does not fire the cue, and it lands on the request line as
  today. The follow-up frame is 7.1.
- **The Vision Keeper's amendment brief** is unchanged.
- **The Tester's test paths** are unchanged.
- **"It would" rows** lose the index line and gain nothing.
- **No blocking** and **no copy** of guess rows into `batch_touch`.
- **No history on the page.**

### 7.1 The follow-up frame, for the holding session to push

```
### Frame <n>, the files half of a (c) reply reaches the code line
- What: Site: rota/roles/api.py (`rulings_rule`, the code-line door beside `pointer_fault`). When the cue reads both files and request text, the door requires a code-line ruling beside the request-line ruling, so the files words reach the Architect and the text words reach the Vision Keeper.
- Ends when: on a night, of the (c) replies the hand reading finds, 4 in 5 or more carry a code-line contest beside the request-line one, from 0 of 18 (copied: plans/frame298-count.md); a reply that still loses its files words is read, and a new cause is a new frame.
- Waits on: frame 298's night, for the cue's real count. Price: 3 cycles, about 250k (a door with its count, one review, re-records).
- Sprint: next sprint, rank (reasoned) after frame 298's night read.
- Pointer: plans/frame298-design.md, sections 7 and 10; plans/frame298-design-review.md, finding 8. Status: pushed 2026-10-18, not started.
```

## 8. Questions for Roman

**None.** Two choices close to his intent are recorded as reasoned:

1. **With a live batch, the code line shows the batch's plan, not the
   guess** (2.1, point 6).
2. **The page names "the team", not the Architect** (2.1, point 7).

## 9. Register lines

None written. This frame writes only this record.

## 10. Amendments after the review, 2026-10-18

Each change answers one finding of `plans/frame298-design-review.md`.

1. **Finding 1, high.** `api.ref_resolves` admits `guess:<item>` for a
   request item. The test sends the relay through `_bind_send.stage`
   (3.4, point 1).
2. **Finding 2, high.** The send door stamps the target once, in the door
   row `code:<message id>`. The render and `land` read the stamp, and a
   built batch target keeps frame 255's check as `code_line_faulted`,
   `built_line_faulted` or the cue, so the cue's refusal does not lead into
   a second refusal (2.1, 3.1, 3.2, 3.5). The
   principal sees one list per item per page (2.1, point 6).
3. **Finding 3, high.** The truth is the merge commit's diff, read from git
   (5.1). The old baseline is recomputed on that truth where the
   repositories allow (5.2).
4. **Finding 4, high.** M3 and M4 are a hand reading of a listed set of
   rulings, capped at 30 a night (5.3).
5. **Finding 5, low.** Three refusal texts with their numbers from the
   order, one for the touch and stopped page (3.3).
6. **Finding 6, low.** Five merged items take about four nights. The
   escalation waits on the item count, and the close needs one night
   (5.3, 5.4).
7. **Finding 7, low.** The pass order is 1, 3, 2, 4. Pass 1 has a frontier
   test. Pass 3 holds the s322/m192 red case (4.1, 6).
8. **Finding 8, low.** The follow-up frame's text is in 7.1.
9. **Finding 9, low.** Class `relation`, key (item_id, item_ver, ruling_id,
   grain), no counter. The set's order is derived at read (1.2).
10. **Finding 10, low.** The op refuses a second call for the same item,
    not a second call (3.4, point 7).
11. **Finding 11, low.** The guess relay's working set carries the item row,
    the stamped set, and `disputed` (3.4, point 6).
12. **Finding 12, low.** The predicate is named `guess`, so `tick:guess`
    keys the mode `guess`. The brief is whole in 3.4 point 8. `landing.md`
    gains one line. The sign-off names nothing. The op's signature, the
    register count and the lint are named (3.4, 4.1, 4.3). The cases run on
    `qwen3.5:9b` and `qwen3:8b` (5.3).
