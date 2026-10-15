# Frame 255, scope read: a files correction after the head commit

Read-only scope read, 2026-10-15 19:40. Meta workflow for the read, rota
workflow for every finding. Sources: `.rota/clickI_night149.db` and the
night DBs of 136 to 149, opened `?mode=ro`, and the code at the checkout's
HEAD 5bf32eb0. Scripts: `door25.py` and `pred.py` in session 4492a9c1's
scratchpad, `f255/`.

## 0. The verdict

Recommend candidate A with a predicate. Admit a `contest` or a `revise` on
a batch line after the head commit only when `_line_reading(words)` faults
that line. Change two sites: the door in `rulings_rule` and the batch filter
in `principal.land`. The rest of the route exists and has no head-commit
check. Count: the predicate fires on 14 of 16 files corrections, and on 0
of 9 refusals that were right (observed: `pred.py`, 2026-10-15 19:3x).

One correction to the frame's text. m105 does not fault line 8. 2 of the 3
night-149 replies were files corrections, m86 and m92. s212 contested line
8 against words that do not name the line, and the refusal of that contest
was right (observed: `messages` m105, `turns` s212).

## 1. What the principal asked for

The page m73, m85 and m91 shows 8 lines: line 1 the item
`confirm_default_on_eof`, lines 2 to 7 the criteria `cr_1` to `cr_6`, and
line 8 the batch `bg_2`. The touch rows of bg_2 are `src/click/termui.py`,
`src/click/utils.py`, `tests/test_utils/test_confirm.py` and
`tests/test_defaults.py`, all `expected` (observed: `batch_touch`, night
149, at the night's end).

- **m74** (before the head commit, the reference case): "Line 8 lists the
  defaults tests and the short help code in utils, which have nothing to do
  with this change, and it leaves out the termui tests where confirm is
  actually tested."
- **m86**: "Please keep working on this rather than drop it. ... line 8
  should touch only termui and the termui tests, not utils, the defaults
  tests or a new test file."
- **m92**: "Please keep going rather than drop this; ... Line 8 should touch
  only the termui code and the existing termui tests, not utils, the
  defaults tests or a new test file."
- **m105**: "Lines 3 and 5 can be checked simply: ... Lines 2, 3, 5, 6 and
  7 are also wrong to say \"instead of raising a UsageError\" ... Please fix
  those lines and keep going with the change, not drop it." The words name
  no line 8 and no file.

The right outcome for m86 and m92 (reasoned: from the words):

- Leave the batch: `src/click/utils.py`, `tests/test_defaults.py`, and
  `tests/test_utils/test_confirm.py`, which is "a new test file".
- Join the batch: the existing termui tests, `tests/test_termui.py` in the
  click tree (observed: frame 190's interview names that file, the comment
  at `rota/core/runner.py` about line 3258).
- Stay: `src/click/termui.py`.
- The item does not change. Both replies say keep going and do not drop.
  Line 1 is approved in every call of s188 and s199.

The right outcome for m105: the batch line is approved, because the words
do not fault it. The contest of line 8 that s212 sent was wrong.

## 2. The chain before the head commit, m74 on night 149

1. **The ruling row.** s170 called `rulings.rule` twice. The second call
   landed `r_3aa5b4358e` with `bg_2: contest` (observed: `rulings`). The
   door at `rota/roles/api.py` 8777 to 8812 skips the batch, because
   `head_commit` is empty: `if not batch["head_commit"]: continue` at line
   8808.
2. **The land.** `land`, `rota/roles/principal.py` 1705 to 2000. At lines
   1791 to 1801 the `batches` map marks a batch live when it has no head
   commit and is not merged or abandoned. A contest on a live batch stays
   in `per_item`. The verdict m75 carries `bg_2` (observed: `messages`).
3. **The relay.** `_owner_of_ref`, `rota/core/sandbox.py` 876 to 890, sends
   a batch id to `architect`. The relay split at sandbox.py about 3705 adds
   `BATCH_RELAY`. m76 went to the Architect with refs `["bg_2"]`
   (observed: `messages`).
4. **The mode.** `_mode_key`, `rota/core/runner.py` 296 to 305, keys an
   Architect relay to `annotate` when `scheduler.batch_relay`
   (`rota/core/scheduler.py` 1785 to 1802) holds: every ref a batch, the
   cause a verdict.
5. **The wake's inputs.** `resolve_inbound`, runner.py 1973 to 2002, pushes
   `touch` from `lifecycle.touch_set` and removes the paths that
   `disputed_paths` (runner.py 1695 to 1813) reads from the words.
   `push_working_set`, runner.py 3256 to 3268, pushes "the index's test
   files". On night 149 the s172 block had `"disputed": []` (observed: the
   `user` text of s172 turn 1). That is frame 244's wall, not this frame's.
6. **The write.** `batches_annotate`, api.py 5736 to 5794. In a relay of a
   contest it stages a `clear` of `batch_touch` for the batch, then the new
   paths. `_apply_write`, `rota/core/db.py` about 446, deletes the old rows.
   s172 wrote the same four files back (observed: `tool_calls` s172).
7. **The Developer's next wake.** s174, `tick:batch_start`. Every Developer
   wake gets `batches.expect` (api.py 15186 to 15228), and its "expected to
   touch" lists the `batch_touch` rows. s174 read `["src/click/termui.py",
   "src/click/utils.py", "tests/test_defaults.py",
   "tests/test_utils/test_confirm.py"]` (observed: s174 turn 1). The head
   commit came in s174, after the re-annotate.

## 3. The same chain after the head commit, if the door admitted the row

From the code. No step below was run.

- **Two doors, not one.** `rulings_rule` refuses at api.py 8809 to 8812.
  `land` also drops the contest: at principal.py 1792 to 1799 a batch with a
  head commit maps to `False`, so its contest leaves `per_item`, and with
  every other row approve, `land` returns `None` (observed: the code). A
  fix that opens only the first door lands a row that relays nothing. That
  is the shape frame 142's design 1.x described at principal.py 719 to 724.
- **The relay, the mode and the push.** `_owner_of_ref`, `batch_relay`,
  `_mode_key` and `resolve_inbound` read no `head_commit` (observed: the
  code). Once `land` keeps the ref, the Architect wakes in `annotate` as
  before the commit.
- **`batches.annotate` on a built batch.** No door reads `head_commit` or
  the batch status (observed: api.py 5736 to 5794). The clear and the new
  rows land as before the commit.
- **What moves after the re-annotate** (observed: the readers that
  `rota.tools.map table batch_touch` lists):
  - The Developer's `batches.expect` on its next wake shows the new list.
    No wake fires because of the change: the Developer reads the list at its
    next wake for another cause.
  - `code_commit`, api.py 14802 to 14823: a later commit that touches a
    non-test path outside the list writes an open `touch_strays` row. The
    Architect then judges it, and a `mistake` wakes the Developer in
    `touch_mistaken` to take the path out.
  - The Tester's `tick:tests_missing` push, runner.py 3248 to 3255, lists
    the `tests/` paths of the list.
  - `_surface_outside_batch`, api.py 4702 to 4775, the criterion repair's
    surface check, reads the list.
- **What does not move** (observed: the code):
  - An edit already committed to a dropped file stays in the diff. Nothing
    reverts it. `worktrees.touched` diffs against `HEAD~1` (worktrees.py
    280 to 285), so a file the next commit does not touch never becomes a
    stray. A path judged once is not raised again. A test path is never a
    stray (`_outside_prediction`, api.py 14840 to 14852).
  - Test rows the Tester wrote stay. On night 149 bg_2 held five new test
    files under `tests/test_utils/`, for example
    `test_confirm_stdin_closed_returns_default.py` (observed: `tests`).
    m86 and m92 decline "a new test file". A files correction does not
    move them.
  - On bg_2 the Developer's commits touched `src/click/termui.py` only
    (observed: the `touched` key in s174, s192 and s228). So for m86 and
    m92 the declined source files were a prediction only, and nothing in
    the diff needs a revert.

So the correction moves the prediction that three seats read, and the
stray detector from the next commit on. It does not move a committed file
or a written test (reasoned: from the readers above).

## 4. Why the door was built

- **Frame 142's design, 2.D, point 3** (`plans/frame142-design.md` 632 to
  662, commit aeb96e32, 2026-10-08): the refusal on every page, because
  "`land` already drops the batch, so the refusal changes no landed state.
  It turns a ruling that moves nothing into a choice the Liaison can make."
  Section 5 of the same design: "Whether a contest on a batch line goes to
  the Architect: no. The records give a batch-line contest no meaning, and
  the lever is the item's" (observed: the file).
- **Frame 190's design, 2.2, points 1 and 2** (`plans/frame190-design.md`
  577 to 600): it opened the route before the head commit, and "keeps the
  refusal for a batch with a head commit, with the item named, as frame 142
  designed it for the quarantine page." It gives no new reason for the
  refusal after the commit (observed: the file).
- `git log -S "a ruling on it moves nothing"` gives 10 commits from
  aeb96e32 to 7d4450cd. The code commit is b0a2086e, 2026-10-09 (observed:
  2026-10-15 19:3x).

What the design feared: a ruling that closes the page and relays the
words to nobody. The fear rested on one fact, `land` drops the batch ref,
and frame 190 removed that fact for the batch before the build. After the
commit the same `land` filter still drops it, so the premise is now made
by the code, not by the records (reasoned: section 3, first point).

For a files correction that drops a file, the fear does not hold
(reasoned: section 3). The ruling reaches the Architect, and the list moves
what the Developer, the Tester and the stray detector read. The part that
holds: a committed edit and a written test do not move. The principal
asked for "a new test file" to leave, and the route does not do that.

Prior ruling: "the principal's words always land on a row" (ruled: Roman,
2026-10-08 23:25, `rota/DECISIONS.md` about line 1445, copied from the
night read). The door's advice "Otherwise approve line 8" lands a row that
contradicts his words on that line. No record rules that a files
correction after the commit is refused (observed: the two designs and the
`git log -S` hits, read 2026-10-15).

## 5. The door's count, nights 136 to 149

25 sessions met the door, and 8 replies made no ruling row (observed:
`door25.py`, 2026-10-15 19:3x, the same totals as `xcount.py`). Nights 136
cases 1 to 6 ran before frame 190's build, under the door that refused a
batch line on every page (reasoned: frame 190's design cites night 136 as
its cause).

| # | Night | Session | Reply | Ruling on the batch | Kind | The words, one line |
|---|---|---|---|---|---|---|
| 1 | 136 | s185 | m85 | none | files | "Line 2 names the wrong tests: ... the terminal UI test file, not the defaults test file" |
| 2 | 136 | s201 | m97 | none | files | "That line still names the wrong tests. ... the terminal UI test file" |
| 3 | 136 | s343 | m228 | none | files | "Line two names the wrong tests ... belong with the other prompt tests" |
| 4 | 136 | s361 | m237 | none | other, wrong page | "Please send a page for that change instead" |
| 5 | 136 | s366 | m244 | approve | other, wrong page | "Please send a page that covers only the third change" |
| 6 | 136 | s368 | m247 | none | other, wrong page | "Please send a page for that change only" |
| 7 | 139 | s263 | m142 | none | other, checks of lines 2 and 3 | "The check for line 2 seems to call the custom version helper without its callback" |
| 8 | 142 | s387 | m260 | landed, no bg | other, checks of lines 2 and 3 | "Line 3's check is wrong: it passes the flag's own value as the default" |
| 9 | 143 | s326 | m210 | approve | files | "line 5 should still cover only confirm in termui and new tests in the termui test file" |
| 10 | 143 | s449 | m296 | approve | files | "Line 3 is also wrong: the work belongs in the version option decorator and its tests" |
| 11 | 143 | s457 | m301 | approve | files | "Line 3 is still wrong: the work belongs only in the version option decorator" |
| 12 | 143 | s527 | m359 | approve | files | "Line 5 is wrong because it still touches the Command class in core.py" |
| 13 | 144 | s274 | m167 | approve | files | "Line 5 still lists the pager test file, and I asked to leave that file alone" |
| 14 | 144 | s339 | m219 | approve | files | "Line 5 is wrong because it plans to touch the pager test file ... leaves out the echo tests" |
| 15 | 144 | s466 | m317 | none | files | "line 8 should drop the option default tests again" |
| 16 | 145 | s270 | m142 | approve | other, checks of lines 2 to 4 | "Line 3's check only shows the option exists" |
| 17 | 145 | s319 | m171 | approve | other, checks of lines 2 to 4 | "Line 3's check is wrong because the flag belongs to the decorator" |
| 18 | 145 | s338 | m186 | approve | other, checks of lines 3 and 4 | "Lines 3 and 4 probably fail because the test command gives no version" |
| 19 | 145 | s414 | m246 | approve | files | "Line 6 is also still wrong because the work should touch only the version option code and its tests in test_basic" |
| 20 | 145 | s428 | m256 | approve | files | "Line 6 is still wrong because the work should touch only the version option code" |
| 21 | 145 | s436 | m261 | approve | files | "Line 6 is still wrong because it touches the option flag and default map tests" |
| 22 | 146 | s299 | m163 | approve | files | "Line 5 is still wrong because shell completion has nothing to do with this" |
| 23 | 149 | s188 | m86 | approve | files | "line 8 should touch only termui and the termui tests, not utils, the defaults tests or a new test file" |
| 24 | 149 | s199 | m92 | none | files | "Line 8 should touch only the termui code and the existing termui tests" |
| 25 | 149 | s212 | m105 | approve | other, no fault of line 8 | "Lines 2, 3, 5, 6 and 7 are also wrong" |

Counts (reasoned: the words of each row, read by this agent):

- Files corrections: 16 of 25. Each says keep the change. 16 of 16 lost
  the files correction: 5 made no ruling row (1, 2, 3, 15, 24), and 11
  approved the batch line his words fault.
- Something else: 9 of 25. 3 are a wrong page on night 136 (4, 5, 6).
  6 contest the batch line beside words that fault criteria only (7, 8, 16,
  17, 18, 25). None is a stop.
- Right refusals: 9 of 25, the 9 "other" rows. In each, the words give the
  batch line no fault, so a contest of it was the seat's error. The text's
  advice for them, "Otherwise approve line N", was right.
- No reply in the 25 asked to stop the change. The door's first advice,
  "To stop the change, contest the item", fits 0 of 25 (reasoned: the words
  column).
- After frame 190's build, nights 139 to 149: 13 files corrections, 13 of
  13 lost; 6 right refusals.

## 6. The cheapest fix

**The predicate.** After the head commit, on a batch that is not merged or
abandoned, admit a `contest` or `revise` of the batch line when the line's
number is in `faulted` from `_line_reading(words)`, read before the batch
lift at api.py 8826 to 8838. Otherwise refuse as today.

**The count** (observed: `pred.py`, 2026-10-15 19:3x; the line numbers of
rows 1 to 7 come from `render_page` on the end-of-night DB, reasoned):

- Fires on 14 of 16 files corrections. The 2 misses are night 136: row 2,
  "That line" on a one-line page, and row 3, "Line two", a number in
  words. Neither shape has come back since night 136.
- Refuses 9 of 9 contests that the words do not support, so 0 right
  refusals are lost. m105 is one of them: `_line_reading` faults lines 2,
  3, 5, 6 and 7, and not line 8.
- Without the predicate, A admits all 25. `_line_refusal` does not stop the
  9: it takes `batch_lines` out of its unnamed-contest check, and a replay
  of s212's call through `_line_refusal` returns `None` (observed: run
  2026-10-15 19:3x). So bare A sends 9 wrong relays to the Architect.

**A against B.**

1. Recommend A with the predicate. It lands his words as a `contest` row and
   uses the route frame 190 built, with no new mode or tool.
2. B has no slot to name. After the commit, the item contest is the only
   lever the records give, and it cancels the change, which 16 of 16 files
   corrections refuse.
3. A changes two sites: the door at api.py 8808 to 8812 and the `land`
   filter at principal.py 1792 to 1799. Both must read the same predicate
   fact, a contest row that `land` keeps.
4. The refusal that stays, for words that do not fault the batch line,
   should say so and drop "To stop the change": "line 8: the words do not
   fault bg_2's files. Approve line 8." This meets the ends-when's "names
   where the correction goes" (reasoned).
5. Residue for the record, not this frame: a correction does not remove a
   committed file or a written test. On bg_2, "not ... a new test file"
   stays unmet after A. That is a candidate for its own frame after a
   night shows it.

**The test.** Replay m92 through `rulings_rule` on a page with bg_2 at
`head_commit = 6ea9f903...`, status `running`, with s199's map `{"1":
"approve", "2": "contest", "3": "contest", "4": "approve", "5": "contest",
"6": "approve", "7": "approve", "8": "contest"}` and m92's words. Red today:
the door's error. Green: a `rulings` row with `bg_2: contest`. A second
assertion: `land` keeps `bg_2` in the verdict, and the relay goes to the
Architect with refs `["bg_2"]`. A guard: m105 with s212's map is still
refused on line 8. Today `_line_refusal` passes on m92's map with and
without the lift (observed: run 2026-10-15 19:3x), so the door is the only
refusal.

Price: 2 to 3 cycles as the frame says, one implementer pass and one
review (reasoned: two sites, one predicate, three tests).

## Usage

The harness count is not visible to this agent. The caller reads it from
the harness line.
