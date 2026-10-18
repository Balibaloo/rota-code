# Frame 298, the design: the Architect owns the scope guess at sign-off, and the Liaison relays its correction

Read-only design agent on Opus, 2026-10-18 12:17. Repository at HEAD
5902981b. Rota workflow, designed by the meta workflow. Sources:
`plans/frame298-investigation.md`, `plans/frame298-count.md`,
`plans/archive/p4-scope-disclosure.md`, `plans/frame190-design.md` 2.2,
`rota/LAWS.md`, `plans/composition.md`, and the code at HEAD. One probe:
`f298d/base.py` in session 6977407c's scratchpad, run on the night
databases 136 to 156 opened `?mode=ro`.

The ruling this design builds (ruled: Roman, 2026-10-18 about 12:05, in the
terminal): "Remove the mechanical guess, the architect owns the guess", and
"The Liaison relays, the Architect rewrites".

## 0. The design in one paragraph

The index line "code that names these words" leaves every page. A new
table, `touch_guesses`, holds the Architect's guess of the code that one
request item touches. A new predicate wakes the Architect once per request
item and item version, before the sign-off present. The send door stamps a
ref `guess:<item>` into each present that numbers the item, and the page
numbers that ref as the line right under the request. A contest or a revise
of that line relays the principal's words to the Architect, who writes a
new version of the guess. When a live batch of the item already holds a
prediction, the same line shows the batch's prediction, and a ruling on it
takes frame 190's batch route to `annotate`. A files correction that still
lands on line 1 meets a door that refuses it and names the guess line. The
item stays approved, so `cancel` does not fire.

## 1. The row

### 1.1 The choice: a new table, in the Architect's `batches` artefact

**Write a new table, `touch_guesses`. Do not reuse `batch_touch`**
(reasoned: the schema and the readers at HEAD).

| Cost | Reuse `batch_touch` with a pre-batch key | New table `touch_guesses` |
|---|---|---|
| Schema | `batch_id` is `REFERENCES batches(id)` and `confidence` has a `CHECK`. An item key breaks the foreign key. SQLite changes a foreign key only by a table rebuild, so every old night database needs a migration | one `CREATE TABLE IF NOT EXISTS`. Old databases gain the table at open |
| Readers | 10 readers read `batch_touch` (observed: `python -m rota.tools.map table batch_touch`). `annotate` fires on a batch with no rows, `touch_note` joins `batches`, `needs_structural_review`, `_predicted_touch`, `batches_expect`, `push_working_set` and `orphaned_grain_refs` read it. Each needs a guard against item keys | no reader until this frame adds them |
| Version | `batch_touch` keeps no version. A rewrite clears the rows (`batches_annotate`, the `clear` write) | the version is a column. Version 1 survives a correction, and the measurement of section 5 needs it |
| Identity | the key `batch_id:grain` would carry two kinds of subject | one kind of subject |

The new table costs less. The reuse saves one `CREATE TABLE` and costs a
migration and ten guards (reasoned: the table above).

**The table joins the `batches` artefact in `rota/core/db.py`, beside
`batch_touch`** (reasoned: law 1 and law 3). The Architect already writes
that artefact, so law 1 holds with no new writer. Law 3 derives contacts per
artefact from the graph's read and write edges, so a table inside an
existing artefact adds no edge, and the boot oracle in `rota/design/graph.json`
needs no change. P4's plan named "a graph writes-edge" for a table of its
own artefact (copied: `plans/archive/p4-scope-disclosure.md`, piece 2).
Inside `batches`, that edge exists already. The design review checks
`test_the_relay_split_matches_the_graph` and the boot oracle on this point.

### 1.2 The table

```sql
-- The Architect's guess of the code one request item touches, before any
-- batch exists. P4 piece 2 in its judged form (ruled: Roman, 2026-10-18,
-- "the architect owns the guess"). A prediction, never a permission (law 12).
-- Each correction writes a new version; the older versions stay, so the
-- Architect's own guess is countable against what the batch touched.
CREATE TABLE IF NOT EXISTS touch_guesses (
    item_id     TEXT NOT NULL REFERENCES items(id),
    ver         INTEGER NOT NULL,           -- the guess's version, 1, 2, ...
    item_ver    INTEGER NOT NULL,           -- the item's version at the write
    grain       TEXT NOT NULL,
    grain_kind  TEXT NOT NULL CHECK (grain_kind IN ('path','symbol')),
    confidence  TEXT NOT NULL DEFAULT 'expected'
                CHECK (confidence IN ('expected','possible')),
    ruling_id   TEXT,                       -- the ruling a rewrite rests on
    PRIMARY KEY (item_id, ver, grain)
);
```

- **Identity, law 14.** Class `content` in `rota/core/identity.py`: "the
  guessed touch set, per item and guess version". The key is the item, the
  version and the grain. The item id is content-derived already. A re-issue
  of the same grain in the same version is the same row (reasoned: law 14,
  "exact match at the door").
- **Junction.** The table has no `id` column, so it goes into
  `JUNCTION_TABLES` in `rota/core/db.py`, as `batch_touch` does.
- **Writer.** The Architect alone, through one op, `batches.guess`. The
  pipeline writes it (`ctx.writes`), never raw SQL.
- **Version.** `ver` is one more than the item's highest `ver`. A write
  happens in two cases: the predicate's wake (section 4), and a relay of a
  principal's ruling on the guess line (section 3). The current guess is
  the rows at the highest `ver`.
- **When.** After the Vision Keeper drafts the item, and before the
  sign-off present when the frontier allows it (section 4). The item's
  statement is confirmed by then.
- **What it holds.** Paths always, symbols only where the Architect is
  confident, the same split as `batches.annotate` (copied: the `annotate`
  brief and the op's docstring). `possible` rows are the symbols, so the page
  can show them as weaker. A guess with no path is refused: "a guess names at
  least one path. A new file goes beside the files that exist".
- **Provenance, law 11.** The table is no model, glossary, problem or frame
  row, so law 11's view does not cover it, the same as `batch_touch`
  (reasoned: law 11's first paragraph). `ruling_id` names the ruling a
  rewrite rests on. The op writes it, never the seat, so no seat writes a
  provenance word. The measurement reads "the Architect's own guess" as
  `ruling_id IS NULL`.

### 1.3 How the batch's prediction starts from the guess

1. The `annotate` wake's working set gains one pushed key, `the item's
   guess`, the current version's paths and symbols of the batch's item
   (site: `push_working_set` in `rota/core/runner.py`, beside the
   `tick:annotate` hint at about line 3485).
2. When the current version rests on a ruling, the key also carries the
   principal's words of that ruling, read from `entry:<verdict id>`.
3. `architect/annotate.md` gains one sentence: "`the item's guess` is what
   you guessed at sign-off, and what the principal corrected. Start from it.
   Read the source, and change a path only where the source says it is
   wrong."
4. Nothing copies rows. The batch's rows are a new prediction from source,
   and the guess stays as it was for the measurement (reasoned: law 12, the
   prediction is per batch, and a copy would hide whether the guess was any
   good).

## 2. The page

### 2.1 The guess line

**The guess is a numbered line right under its request item, on every
present that numbers the item as a request line, except the touch page, the
stopped page and the park page** (reasoned: P4's two halves, "coarse beside
the items at signoff, grounded before a batch builds", copied from
`plans/archive/p4-scope-disclosure.md`). The touch and stopped pages already
show the batch's line under "The team expects to touch", and two file lists
on one page would make the principal choose between them.

1. **The send door stamps the ref.** In the present path of
   `rota/core/sandbox.py`, beside the `stamped` block (about line 3480),
   after `request_rows`: for each request item the refs hold, add
   `guess:<item>` when the item has a `touch_guesses` row or a live batch
   with `batch_touch` rows. Do not add it when the refs hold a batch of
   that item, which is a touch or stopped page. Record the added refs in
   `stamped`, so `land` drops an approve of them as it drops any stamped
   approve.
2. **The ref is a page alias, not a table id.** `guess:<item>` names "the
   code line of this item". The ref derives from the item id, so law 14
   holds. `_resolve_refs` returns nothing for it, and the line renders in
   `request_block`. `_page_body` adds the ref to `in_block`, so the loop
   does not pass it to `touch_words`. `_items_reached` returns the item for
   it, so `off_page` keeps it on the page of its own request.
3. **`request_block` renders it.** After the item's line, before "It must:":

   ```
   You asked:
     1. Give version_option a show_python flag that appends the running Python version to the message.
     2. The team's guess at the code this touches: src/click/decorators.py, tests/test_basic.py. It might touch src/click/decorators.py::version_option.
   It must:
     3. ...
   ```

   When a live batch of the item has touch rows, the same line reads the
   batch's rows: "The team's plan of the code this touches: expected to touch
   ...; might touch ...". It leaves out the unsurveyed ground and the
   commitments, which are the touch note's. The line number does not move
   between the two words, because the ref is the same.
4. **Words, no seat names.** The page says "the team", as every page does
   today (observed: "The team expects to touch", "The team's notes" in
   `_page_body`). The line is labelled as a guess. The brief's "the
   Architect's guess" is the meta workflow's name for it (reasoned: the
   principal talks to the Liaison only, `plans/composition.md`, the parties).

### 2.2 The index line leaves

- `request_block` loses its `near` argument and the two lines that call
  `near_code`. `_page_body` loses the `near_code` lines under "It would:".
  "It would" rows get no replacement, because the guess is per request
  item (reasoned: an "It would" row is a seat's description of the item,
  and one code line per request is the line the principal corrects).
- `near_code` and `STOP_WORDS` leave `rota/roles/principal.py`. Their only
  callers are those two render paths (observed: the map tool). Two tests
  pin them: `tests/rota/test_signoff_assumptions.py:526` and
  `tests/rota/test_index_refresh.py:105`. The first changes to pin the guess
  line. The second tests the index refresh through `near_code`, so it reads
  `code_index` straight instead.

### 2.3 When the Architect has not written yet

The present can go out before the guess exists (section 4). Then the send
door stamps no guess ref, and `request_block` writes one unnumbered line
under the item:

```
     The team has not guessed the code this touches yet.
```

The line is unnumbered, so no ruling is owed on it, and "ok" means what it
means today. A files correction on such a page meets the door of 3.3, which
names the key `guess:<item>`.

### 2.4 The closing instruction

`_name_request` gains a partner, `_name_guess(lines)`, and the "Here is
what I understand" branch adds it after the request sentence:

```
Reply in your own words. 'ok' approves all of this and starts building. Name a line to correct only that line. Ask, if something here is unclear. To change what you asked for, name line 1. To correct the code it touches, name line 2.
```

With two request items: "To correct the code they touch, name line 2 or
5." With no guess line, the sentence is left out.

## 3. The route

### 3.1 A ruling on the guess line, in `rulings_rule`

**One door, after the team's-note revise door and before the batch-line
door** (site: `rulings_rule` in `rota/roles/api.py`, about line 9730).

1. **Approve** passes. `land` drops it, as a stamped approve.
2. **Contest or revise** passes when the words are not empty. The existing
   refusal "a contest carries the principal's words to the row's owner, and
   words is empty" holds it.
3. The guess lines join `batch_lines` in the `_line_refusal` call, because
   they show a prediction and hold only files (reasoned: `_line_refusal`
   spares `batch_lines` on touch words, at about line 9258).
4. **The off-page key.** A key `guess:<item>` where the item is a request
   item of the page's order is admitted, even when the refs do not hold the
   ref. This carries a files correction from a page sent before the guess
   existed (2.3). Every other key keeps the refusal "is not a line of the
   page".

### 3.2 What `land` writes

1. A `guess:` key with approve leaves `per_item`.
2. A `guess:` key with contest or revise stays in the verdict. `land`
   writes no `items` state for it, so the item keeps its approval and
   `cancel` does not fire (reasoned: `cancel` abandons a batch whose item
   is not approved at its version, `plans/frame190-design.md` 1.5).
3. **The alias.** When the item has a live batch with `batch_touch` rows,
   `land` writes the verdict with that batch id in place of the `guess:`
   key, and the same ruling. The rewrite runs after the built-batch filter
   at about line 1855, because that filter reads `built_line_faulted` on
   the page order, and the order holds no batch id. The cue of 3.3 already
   read the words, so the filter has nothing to add.
4. `verdict:<id>` and `entry:<id>` are written as for any ruling.

### 3.3 The door on line 1: the files cue

**A contest or revise of a request line whose words fault only the code is
refused, and the refusal names the guess line** (reasoned: the count;
observed: `plans/frame298-count.md`, section 3).

- **The predicate.** `pointer_fault(words, line, guess_lines)` from
  `plans/frame298-count.md` section 3, ported to `rota/roles/api.py`
  with its `FILES`, `REQUEST_TEXT`, `AGREE`, `FAULT`, `BARE_FAULT`, `KEEP`
  and `CLAUSE` patterns. The `batch_lines` argument becomes the page's
  guess lines and batch lines.
- **Its count, in-sample** (copied: `plans/frame298-count.md`, 2026-10-18
  11:4x): fires on 19 of 19 pointer faults and 8 of 8 batch-line faults.
  Refuses 43 of 43 right request contests, 18 of 18 (c) rows and 13 of 13
  (d) rows. The cue was written against these rows, so the count on the
  next night is the real count.
- **The text, guess line on the page:**
  "line 1 is the request, and the words fault only the code it touches.
  That code is line 2, the team's guess, and the team rewrites it from the
  principal's words. Rule line 2 contest with the words, and approve line
  1."
- **The text, no guess line:**
  "line 1 is the request, and the words fault only the code it touches.
  The team has not guessed that code yet. Rule the key guess:<item> contest
  with the words, and approve line 1."
- **Placement.** After the team's-note revise door, beside the guess-line
  door. A ruling that also faults the request's text (class (c)) does not
  fire the cue and lands on line 1 as today (section 7).

### 3.4 The relay and the Architect's mode

1. **The split.** In the relay split of `rota/core/sandbox.py` (about line
   3866), a `guess:` ref goes to `architect` + `GUESS_RELAY`, a new
   constant `":guesses"` beside `BATCH_RELAY`. A batch id from the alias
   takes today's `BATCH_RELAY` branch.
2. **`_owner_of_ref`** gains one rule before the ledger lookup: a ref that
   starts `guess:` goes to `architect`.
3. **`verdict_signoff.md`** gains one table line: "the team's guess —
   `msg.relay_architect`".
4. **The mode key.** `_mode_key` in `rota/core/runner.py` keys an
   Architect `relay` whose refs hold a `guess:` ref to the new mode
   `guess`, by the shape of the `batch_relay` key at about line 297. A tool
   added to `relay` is an invitation (copied: the comment there).
5. **The mode `architect/guess`.** One brief and one tools file.
   - `guess.tools`: `code.probe`, `code.source`, `code.callables`,
     `batches.guess`. The same read tools as `annotate`, and no ticket or
     criteria scan, because none exists before slicing.
   - `guess.md`, the tick case: "MODE: guess — guess what one request
     touches, before any plan. The item's words are in the working set.
     `code.probe` and `code.callables` to see where that work lives, then
     `batches.guess` once. Paths always. Symbols only where you are
     confident. This is a guess, not a permission."
   - `guess.md`, the ruling case, the shape of `annotate.md`'s ruling
     paragraph: "When the message is a relay with `principal_verdict` on
     the guess, the principal read your guess and corrected it. The words
     are `principal_said`. Call `batches.guess` once with the paths the
     words name. A path he says has nothing to do with the item is
     disputed. Drop it. Keep the others. Then stop."
   - The runner pushes `the index's test files` for a guess relay, as it
     does for a batch relay (copied: `plans/frame190-interview.md`, the
     seat made up a test path without it).
6. **The op `batches.guess(item_id, paths, symbols=None)`.** It refuses an
   item that is no request item, a directory the index lacks (the check of
   `batches_annotate`), an empty `paths`, and a second call in one session.
   In a session woken by a principal relay that rules the guess, it writes
   the next `ver` with `ruling_id` set to the verdict. Otherwise it writes
   the next `ver` with `ruling_id` empty.
7. **The re-present.** No new predicate. The next page of the item renders
   the new version, because the page reads the rows at render time. The
   item's next page after an approve is the touch note, and that page shows
   the batch's prediction, which starts from the corrected guess (1.3)
   (reasoned: an approved item slices, groups and annotates, and
   `touch_note` then owes the page). R7 holds: nothing waits on the
   principal to see the rewrite.

### 3.5 When a batch already runs

- The line under the request shows the batch's prediction (2.1, point 3).
  A ruling on it goes, through the alias, to `annotate`, and
  `batches.annotate` replaces the batch's `batch_touch` rows. That is
  today's route, which redrew the prediction on 19 of 20 files corrections
  of nights 151 to 156 (copied: `plans/frame298-investigation.md`,
  section 3).
- The guess rows stay as they are. The batch's rows lead once the batch
  holds a prediction, and the guess is the record of what the Architect
  guessed before any plan (reasoned: section 5 measures it).
- The batch is not cancelled, because the item stays approved (3.2).
- bg_3 on night 156 under this design: m191's line 2 shows bg_3's own
  prediction, which was already right (observed: `batch_touch` for bg_3,
  the investigation section 2.3). The m192 words fault line 1's files. The
  cue fires (row 98, copied: the count, section 3), the door names line 2,
  and the reading lands `{2: contest}` with the criteria contests. The
  criteria go to the Terminologist, bg_3 goes to `annotate`, and the item
  stays approved (reasoned).

### 3.6 A files sentence that still lands on line 1

The door of 3.3 refuses it and names the guess line or the key. The seat
then rules again, inside the same session, as it does after every refusal
today. The count shows the cue fires on 19 of 19 such sentences in-sample.
A sentence the cue misses lands on line 1 as today, `contested` is written,
and a live batch is cancelled. That residue is counted on the night
(section 5).

## 4. The predicate and the wake

### 4.1 `touch_guess`

```python
@predicate("touch_guess", wakes="architect", band="gate")
def touch_guess(conn) -> list[Wake]:
    """A request item with no guess of its code at its current version."""
```

- **Fires on** one item at a time (the reason of `annotate`, one session per
  subject): a request item (`_is_request_item`), approval `draft` or
  `approved`, not set aside (`not_parked`), with no `touch_guesses` row
  where `item_ver` equals `items.version`, and with no live batch whose
  `batch_touch` holds rows. It does not fire while `code_index` holds no
  path, because there is no code to guess against (copied: the `deliver`
  brief, "Unless there is no code yet").
- **Wakes** `Wake("architect", "tick:touch_guess", refs=(item,))`, keyed to
  the mode `guess`.
- **Drains** when the op writes a row at the item's version.
- **Band `gate`, declared in the file before `signoff`** (reasoned: `ORDER`
  in `rota/core/predicates.py`, gate 20 and start 30). The frontier then
  offers the guess before the Vision Keeper's submit inside one band. In
  band `start`, `signoff` would win every time, and the sign-off page would
  never carry a guess.
- **Register entry.** It joins `REGISTER_ENTRIES`: an item is owed its
  guess, and the predicate offers it until a row discharges it (reasoned:
  `rota/REGISTER.md`, "something is outstanding"). `outstanding()` then
  counts it.
- **An amended item** moves `items.version`, so the predicate fires again
  and the Architect writes a new version from the new words. The older
  rows stay.

### 4.2 The caps

- **Depth.** One item per wake, one `batches.guess` call per session.
- **Loop.** A session that writes no row leaves the predicate true. The
  tick-attempt bound quarantines the key after three attempts, as for any
  tick (reasoned: `quarantine_stalled` in `frontier`). A quarantined guess
  stops nothing else, and the page says "not guessed yet".
- **Relay loop.** Each guess relay rests on one landed ruling, and one
  ruling makes one relay (the door "every owner these rows belong to has
  its relay already"). The principal's replies bound the loop.

### 4.3 What the sign-off waits on

**Nothing new** (copied: P4, "Non-blocking by R7: nothing waits on the
principal's reaction"; reasoned: a prediction never blocks, the
composition's Flows). `tick_signoff` keeps its query. The first present can
go out before the guess exists, when the frontier runs the Vision Keeper
first or the item has several siblings. The page then shows 2.3's sentence,
and the next page of the item carries the line. The night counts how many
sign-off pages carried the guess (section 5, M0).

## 5. The measurement

The ruling of 2026-09-03 says the judged guess "must be measured before it
is trusted — a case with a preregistered expectation" (copied:
`plans/archive/p4-scope-disclosure.md`, piece 2).

### 5.1 The baseline, the index line

**The index line named a path of the merged batch's touch rows on 8 of 26
merged items over nights 136 to 156, and named a source file on 0 of 26**
(observed: `f298d/base.py`, 2026-10-18 12:1x; `near_code` on the item's
text at the night's end against the merged batch's final `batch_touch`
paths). Median precision 0.0, median recall 0.0. The text at the night's
end includes amendments, so this baseline is an approximation of what the
pages showed (reasoned: `items` keeps the current text only).

### 5.2 The expectation, preregistered

The subject is the Architect's own guess: version 1 at the item's first
version, `ruling_id IS NULL`. The truth is the merged batch's final
`batch_touch` paths with `confidence = 'expected'`. The model is the
night's Architect, `qwen3.5:9b`.

| Measure | Baseline (index line) | Expectation (guess) |
|---|---|---|
| M0: sign-off pages of a new item that carry the guess line | none | 3 of 4 or more |
| M1: merged items whose guess names a path of the truth | 8 of 26 (31%) | 60% or more |
| M2: merged items whose guess names a source path (not `tests/`) of the truth | 0 of 26 | 50% or more |
| M3: pointer faults that land on line 1 and write `contested` | 19 of 19 (copied: the count, (a) pointer) | 1 in 5 or fewer |
| M4: batches cancelled by a files correction | 13 over 21 nights: 5 pointer, 8 batch line (copied: the count, section 0 point 6) | 0 on the night, by the residue rule |

**The ratio that says the guess is worth the principal's eyes: M1 at 60%
or more and M2 at 50% or more, over at least five merged items** (reasoned:
a guess that names the source file the batch changes is one the principal
can check in one look, and the index line never did). A night holds about
three merged items (observed: 26 over 21 nights in 5.1), so the measure
needs two nights or more. If M1 is at or below the baseline's 31% after
five items, the guess is hollow. The frame then escalates to Roman with
P4's fallback, "mechanical only ... labelled as hits", as the recommended
answer (copied: P4, build order 2).

### 5.3 How the night counts it

A new section in `python -m rota.tools.nightreport`, "the guess", reads
`touch_guesses`, `batches`, `batch_touch`, `messages.body_refs` and the
`rulings` rows, and prints M0 to M4 with each item named. One line per
item: the guess version 1 paths, the truth paths, hit or miss, and the
rulings that rewrote it. The residue rule: an item that misses is read. A
miss whose cause is a scope change the principal made after the guess is
not a miss of the guess, and it is listed apart.

### 5.4 Frame 298's ends-when on a night

1. **Mechanism.** On the night, every pointer fault the cue fires on lands
   on the guess line or the alias batch, and the item keeps its approval in
   the same ruling. The guess line shows on the item's present pages, and
   no page shows "code that names these words".
2. **Ratio.** M3 at 1 in 5 or fewer, from a baseline of 19 of 19. M0 at 3
   of 4 or more.
3. **Residue.** A files correction that still writes `contested` is read.
   The frame closes when its cause is not the cause this frame named (no
   row to land on). A (c) reply that faults both the files and the text is
   such another cause, and it is a new frame.

M1 and M2 do not gate the close. They decide the escalation of 5.2 after
five merged items (reasoned: one night is too small a sample, and a zero
on a stochastic seat is a line no night proves, CLAUDE.md's three parts).

## 6. The passes

Price anchors (copied: `plans/operating-facts.md`, cost anchors): an
implementer pass on Opus cold 74k to 217k, a reviewer pass 61k to 147k, a
cycle about 10k of the holding session, about 3k with a report to a file.

| Pass | Files | Tests red first | Cycles | Review points |
|---|---|---|---|---|
| 1. The row, the op, the predicate, the mode | `rota/core/schema.sql`, `rota/core/identity.py`, `rota/core/db.py` (artefact group, `JUNCTION_TABLES`), `rota/roles/api.py` (`batches.guess`), `rota/core/predicates.py` (`touch_guess`, `REGISTER_ENTRIES`), `rota/core/runner.py` (the working set for `tick:touch_guess`: the item text, a `code.callables` hint, the index's test files), `rota/roles/prompts/architect/guess.md` and `guess.tools`, `rota/REGISTER.md` (the list) | new `tests/rota/test_touch_guess.py`: the predicate fires on a draft request item with an index, and not on a parked, contested or observed item, nor with a live batch that has touch rows, nor with an empty index; it drains on a row at the item's version and fires again after an amendment; the op refuses an unknown directory, empty paths and a second call, writes `ver` 1 then 2; identity and table checks pass. One L1 case, `L1-AR-guess-the-code-of-a-request`, on night 156's echo_json at version 1: the reply's `batches.guess` names `src/click/utils.py`, 5 runs recorded | 3 | the band and the file order against `signoff`; the identity class; no raw write; the gate's table and op checks |
| 2. The page and the send door | `rota/roles/principal.py` (`request_block`, `_page_body`, `_name_guess`, `_items_reached`, the words of the guess line, `near_code` and `STOP_WORDS` removed), `rota/core/sandbox.py` (the stamp), `tests/rota/test_signoff_assumptions.py`, `tests/rota/test_index_refresh.py` | night 156's m191 rebuilt: line 1 the item, line 2 the guess, criteria from 3, the closing sentence names line 2; the same page with a live bg_3 shows bg_3's rows on line 2; a page before the guess shows 2.3's sentence and no number; a touch page carries no guess ref; no page holds "code that names these words"; `off_page` keeps the guess ref | 3 | line numbers on every page kind; the stamp only on the "Here is what I understand" pages; `stamped` holds the guess; the re-records of the Liaison cases whose prompt carries a page |
| 3. The route | `rota/roles/api.py` (the guess-line door, the off-page key, `pointer_fault`, the guess lines in `batch_lines`), `rota/roles/principal.py` (`land`: approve dropped, contest kept, the alias after the built filter, no `items` write), `rota/core/sandbox.py` (`GUESS_RELAY`, `_owner_of_ref`), `rota/core/runner.py` (`_mode_key`, the pushes for a guess relay), the op's ruling branch, `guess.md`'s ruling paragraph, `annotate.md`'s one sentence, `verdict_signoff.md`'s table line | night 156's s322 on m192 rebuilt: `{1: contest, ...}` is refused with line 2 named; `{2: contest, ...}` lands, the item stays approved, the verdict holds bg_3, the relay keys `annotate`, `cancel` does not fire. Night 156's s108 on m24 rebuilt with no batch: refused with the guess line or the key named; the guess ruling relays to `guess` mode. The 43 (b) replies of the count still land on line 1 (a table test over the count's rows). One L1 case, `L1-AR-rewrite-the-guess-from-the-ruling`, on m23's words: the reply drops `tests/test_termui.py` and `tests/test_context.py`, 5 runs | 4 | the alias's place after the built filter; the off-page key only for the page's own request item; the cue's patterns copied exactly; a stale render between send and ruling; `cancel` silent |
| 4. The instrument | `rota/tools/nightreport.py` (the section of 5.3), its test | a fixture with two merged items, one hit and one miss, prints M0 to M4 | 2 | the truth is the final expected paths of merged batches; version 1 only |
| The walk | a full night from a worktree at the closing commit, because the frame touches the delivery path, the briefs and the write pipeline | the night | 0, then the read 1 | |

**Total: 13 cycles with the night's read** (reasoned: the anchors; a seam
design with its night is 8 to 10, and this one adds a table and two L1
cases). Tokens: four implementer passes at about 100k to 200k each, four
diff reviews at about 70k to 150k each, one design review at about 66k to
100k, and the night read at about 75k to 130k. The holding session spends
about 3k a cycle with reports to files.

**What each pass leaves for the next.**

- Pass 1 leaves rows that no page shows. The predicate runs on a night, so
  pass 1 alone already writes guesses that pass 4 can count.
- Pass 2 leaves a numbered guess line that a ruling cannot reach yet. A
  ruling on it would meet "not a line" for the off-page key and an unknown
  owner in the split. Do not run a night between pass 2 and pass 3.
- Pass 3 leaves the night count to pass 4.
- Pass 4 leaves the night.

**The walk the frame ends on: a full night** (reasoned: CLAUDE.md, "a full
night for the delivery path or when in doubt"). The frame touches the
sign-off page, the write pipeline, a predicate and two briefs.

## 7. What the design does not do

- **The (c) loop.** A reply that faults the files and the request's text
  in one breath does not fire the cue, and it lands on line 1 as today.
  The Vision Keeper's `contested` amendment can still carry the files words
  into the request text (copied: the investigation, s111 and s327). That is
  18 rows of the count. It is a new frame if the night shows it.
- **The Vision Keeper's amendment brief.** `contested.md` is unchanged.
- **The Tester's test paths.** The Tester still chooses where a test goes
  (copied: frame 190's open question 5.2).
- **"It would" rows** lose the index line and gain nothing.
- **No blocking.** The sign-off does not wait on the guess, and no diff is
  refused for straying outside it (law 12).
- **No copy.** The batch's `batch_touch` rows are never copied from the
  guess.
- **No history on the page.** The page shows the current version only.

## 8. Questions for Roman

**None.** The design applies the ruling of 2026-10-18 and the P4 ruling of
2026-09-03. Two choices close to his intent are recorded here as reasoned,
so the holding session can check them against the ruling.

1. **With a live batch, line 2 shows the batch's prediction, not the
   guess** (reasoned: "the architect owns the guess" covers both, because
   the Architect writes both; P4 puts the grounded prediction before the
   build; night 156's bg_3 died with a right prediction that no page
   showed, the investigation section 2.3). The other choice, the guess
   always, keeps two file lists that can disagree on one item's pages.
2. **The page names "the team", not the Architect** (reasoned: every page
   today says "the team", and the principal talks to the Liaison,
   `plans/composition.md`, the parties).

## 9. Register lines

None written. This frame writes only this record.
