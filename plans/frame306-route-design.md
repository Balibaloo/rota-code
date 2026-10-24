# Frame 306, the route design: how a merged change outside the criteria reaches the principal

Design read on Opus, 2026-10-24. Repository `D:/repos/rota` at 850a8906.
No file under `rota/` changed between 214d22d0 and 850a8906 (observed:
`git diff --stat 214d22d0 HEAD -- rota/` is empty), so every line number
below holds at 214d22d0. Databases `.rota/clickI_night154.db` to
`.rota/clickI_night161.db`, opened `?mode=ro`. The sample tree
`D:/repos/_AI/sample_repos/clickI`, git read-only. Script:
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f33f3f44-c058-42c9-90d1-bfcf8f3dafaa/scratchpad/f306_route_count.py`.
Meta workflow. No file but this one is changed.

## The result

**Recommended: option (e), a shape detector at the grain of a statement,
fed into the stray route that exists, with option (a)'s notice for each
change the Architect keeps.** The detector raises two shapes that no
criterion names: an optional parameter added to a definition, and a line
of the base that the merge removes or rewrites. Each hit is a
`touch_strays` row, so `mergeable` holds the batch until the Architect
says foreseen or mistake. Each foreseen hit then shows on the end state
and the night report as a notice with no question (reasoned: sections 4
and 5).

Over nights 154 to 161, 8 batches merged with 24 source hunks. All 24 sit
in a definition a criterion names. 12 hunks in 6 batches hold a change no
criterion names or a line his words refused. The definition-grain check
named 0 of the 12. The Critic's line map, read line to criterion, names
5 of the 12 and raises 6 false notices. The shape detector names 7 of the
12, in 4 of the 6 batches, and raises 0 false notices (observed: section
3).

## 1. What reaches him today after a merge

**Nothing names a merged batch to him, and nothing shows him its diff**
(observed: the code below).

| Surface | Function and line | What it shows of a merged batch |
|---|---|---|
| The end state, printed when the run is quiet | `render_state`, `rota/roles/principal.py` 284, the line at 322 to 324; printed by `rota/cli.py` 733 and `rota/tools/onboard_run.py` 122 | A count only: "Done: 2 changes built, tested and merged." No batch name, no item, no file, no line (observed: `.rota/night161.log`, the tail) |
| The shift page | `_shift_page`, `principal.py` 1454 | Nothing after a merge. The page asks about a request shift before the build, and names a merge only as "until the new request is merged" (observed: 1476) |
| The Liaison's pages | `rota/roles/prompts/liaison/*.md`, `render_page` 1522 | Nothing. No Liaison brief names a merge (observed: grep of `merged` over the directory finds no file) |
| The night report | `rota/tools/nightreport.py`, `build` 493, `_git_truth` 205, `_guess_section` 293 | The batch status, the head and the commit shas per session, and the merged files as "truth" beside the guess. Files only. No definition, no line. The report is the meta workflow's, not his (observed: `.rota/night161_report.txt` lines 2 to 22 and 268 to 275) |
| The `done` wake | none | No wake of that name exists. `"done"` is only an onboarding phase (observed: `rota/core/scheduler.py` 881 and 902) |

The cockpit's `d` key compares two runs, not a batch's diff (observed:
`rota/cockpit/screens.py` 497 to 520). So the purpose sentence "no work
stays invisible" holds today for the count of merges and not for their
content (reasoned).

## 2. The stray route's grain

**A stray is a file the prediction did not name, or a top-level
definition that a write changed and that no criterion names. Neither
grain looks inside a definition a criterion names** (observed: the code
below).

- When: at each `code.commit`. `code_commit` calls `_outside_prediction`
  for paths and `_unnamed_def_strays` for definitions, and writes each hit
  as a `touch_strays` row with status `open` (observed:
  `rota/roles/api.py` 18741 to 18760).
- The path grain: `_outside_prediction` (`api.py` 19558) lists touched
  paths outside the predicted touch, less test paths and judged paths.
- The definition grain: `_unnamed_def_strays` (`api.py` 19574 to 19608)
  calls `_changed_unnamed_defs` (`api.py` 20127). That function reads
  top-level definitions only (`_def_sources`, 20113 to 20124). It skips a
  definition a criterion names by surface (20179), a new definition
  (`name not in before`, 20179), and a restored one (20183).
- The names come from `surface_refs` only, never from the criterion text
  (observed: `_criteria_surface_names`, `api.py` 20095 to 20110).
- No prediction, no stray (observed: `api.py` 19582).
- The hold: `mergeable` (`rota/core/lifecycle.py` 711) refuses the merge
  while a row is `open` or `mistake` at the head (758 to 768). The
  predicate `touch_strayed` wakes the Architect (`rota/core/predicates.py`
  2338). `batches.judge_touch` (`api.py` 19612) writes foreseen or
  mistake. A mistake wakes the Developer (`touch_mistaken`, 2363).
- `batches.strays` (`api.py` 19695 to 19703) lists the rows. It has 0
  callers (observed: `python -m rota.tools.map fn batches_strays`).

**Why night 161's changes are no stray.** b_1's `file=None`, its
`obj is None` branch and its `if file is None` branch sit in `echo_json`.
`echo_json` is new and is the surface of c_1 to c_3, so the definition
check skips it twice (observed: `git diff 2c8cd3ac e7e4a7a6`, criteria
surfaces). b_3's docstring edit, "``err``" to "`err`", and its two lines
in `except (KeyboardInterrupt, EOFError)` sit in `confirm`, the surface
of cr_1 (observed: `git diff 9d92a758 9622b3e5`). No `touch_strays` row
exists on nights 154 to 156, 158, 160 or 161 (observed: the table).

**The Critic's map.** Since 1663c2bb (Roman, 2026-10-07), a pass names
one added line per criterion in `verdicts.lines`, as JSON (observed: the
commit body, `verdicts_emit`, `api.py` 12526). Read the other way, a hunk
of the merged diff that holds no mapped line is a candidate. The count
costs no model call: one query over `verdicts.lines` and one
`git diff -U0` (reasoned). The map holds one line per criterion, so a
large hunk with one mapped line hides the rest of the hunk, and a
docstring hunk with no mapped line reads as outside (observed: section
3).

## 3. The count, nights 154 to 161

Nights 155, 157 and 160 merged nothing (observed: `batches`). The base of
each merged diff is the first merge commit, or 2c8cd3a, on the head's
first-parent chain. `git diff -U0 <base> <head> -- src/`. A hunk's
definition is the top-level definition its lines sit in. "Outside" is
this agent's reading of the hunk against the criteria texts of the batch
and night 158's m146 "Do not put parentheses around it" (reasoned). A
documentation hunk for the asked parameter is a companion, not outside.

Columns: hunks; in a named definition; in an unnamed definition; in no
definition; outside; outside and named by the definition grain; outside
and named by the Critic's line map; false notices of the line map;
outside and named by the shape detector.

| Night, batch | Hunks | Named def | Unnamed def | No def | Outside | Def grain | Line map | Line map false | Shape |
|---|---|---|---|---|---|---|---|---|---|
| 154 b1 | 1 | 1 | 0 | 0 | 1: `file` and `nl` parameters in the new `echo_json` | 0 | 0 | 0 | 1 |
| 154 b3 | 4 | 4 | 0 | 0 | 1: the return in `except (KeyboardInterrupt, EOFError)` | 0 | 0 | 2 (`:param` and `versionadded` docs) | 0 |
| 156 bg_1 | 4 | 4 | 0 | 0 | 1: the same interrupt branch | 0 | 0 | 1 (`versionadded` doc) | 0 |
| 158 bg_1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 158 bg_3 | 6 | 6 | 0 | 0 | 4: 13 docstring lines deleted with the `versionchanged` 8.0 and 8.4.2 entries; a duplicated 5-line block; the message line with " (...)" that his words refused; `ctx.exit()` deleted | 0 | 3 (all but the duplicate) | 1 (`:param` doc) | 2 (the deleted docstring lines and `ctx.exit()`; the message line is a widening, section 7) |
| 159 bg_1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 161 b_1 | 3 | 3 | 0 | 0 | 3: the `file=None` signature; the `obj is None` branch and `:param file`; the `if file is None` branch | 0 | 1 (the signature) | 0 | 3 (all hold the `file` parameter, one row) |
| 161 b_3 | 4 | 4 | 0 | 0 | 2: "``err``" to "`err`"; the interrupt branch | 0 | 1 (the docstring edit) | 2 (the named `default_on_eof` parameter and its docs) | 1 (the docstring edit) |
| **Total** | **24** | **24** | **0** | **0** | **12, in 6 of 8 batches** | **0** | **5** | **6** | **7, in 4 batches** |

(observed: the script's output and the diffs; the "Outside" column is
reasoned.)

Three facts follow.

- Every change outside the criteria sits inside a definition a criterion
  names. No hunk sits at module level or in an import (observed). So any
  check at the file or definition grain counts 0, and the provenance's
  "6 of 12" on nights 150 to 158 is a count of batches, not of strays the
  route saw (reasoned).
- Night 158's bg_3 deleted `ctx.exit()` from the version callback. That is
  a behaviour change outside the criteria, and cr_3 says "behave exactly
  as it does today" (observed: `git diff 75cf8ed0 ea03bf63`; reasoned).
  The provenance counted 9 deleted lines and missed this line.
- The interrupt branch is in 3 of 8 batches. The added lines are the
  criterion's own lines, and the stray is the `except` clause around
  them. No mechanical grain separates them (reasoned).

## 4. The options

One cycle is about 60k on Opus and one review. "False notices" counts on
the table of section 3.

**(a) A notice of each merged hunk outside the criteria, on the end state
and the night report, with no question and no gate.** He sees a list
under "Done": the batch, the definition, the hunk's lines. Where: after
`render_state`'s Done line, and a night-report section. When: after the
merge. The grain decides the content. At the definition grain it lists
0 of 12. At the Critic's line map it lists 5 of 12 with 6 false. It keeps
all three sentences: no sign-off, nothing invisible, nothing blocks. The
merged count of the frame's measure does not move, because nothing stops
a merge (reasoned). Price: 1 cycle.

**(b) The same notice before the merge, as a page he may answer, and the
merge does not wait.** He sees a page per batch at the review. His later
contest reaches the merged code by the existing contest route. Same grain
and false notices as (a). The merge race means most answers arrive after
the merge, so (b) costs a page and buys what (a) buys (reasoned). It
keeps "opt-in" for the merge, and **crosses "Attention is the scarcest
budget. Checkpoints are opt-in"** (`plans/composition.md` 103), because a
page per merge is a checkpoint he did not opt into (reasoned). Price: 1.5
cycles.

**(c) The Critic maps each hunk to a criterion, and an unmapped hunk goes
to the Architect by law 12's route before the merge.** The provenance's
repair 2. He sees nothing. Grain: the hunk, judged by a model. Gate: the
stray hold. It keeps all three sentences, because the gate is a seat's
judgement on a fact, not a page (reasoned). On the table the Critic
mapped the line `file.write(out + "\n")` to c_3 and passed b_1 with the
`file` branch in the same hunk (observed: night 161 `verdicts.lines`).
A door that needs every hunk mapped forces 6 documentation hunks into a
map, and the model can map the `file` hunk to c_3 as it did (reasoned).
The doubt stands. Price: 2 cycles, plus brief work on the Critic.

**(d) A mandatory diff page before every merge.** He sees each diff and
approves. Grain: lines. Gate: his approval. 0 misses and 24 hunks to
read on 8 batches. **Crosses "Sign-offs after that, including on merges,
are opt-in"** (ruled: Roman, 2026-09-16, `plans/composition.md` 23). The
setting `merge_gate = review` already gives him this when he opts in
(observed: `lifecycle.py` 806), so (d) is a change of default, not of
code. Price: 0 cycles in code, the cost is his attention.

**(e) A shape detector at the statement grain, into the stray route, with
(a)'s notice for each foreseen hit.** Added by this design from the code.
At each `code.commit`, beside `_unnamed_def_strays`, the detector reads
the base and head text of each touched source file and raises two shapes:

1. An optional parameter (one with a default) that a commit adds to any
   definition, when no criterion text or surface names the parameter.
   The grain is `path::def(param)`.
2. A base line that the diff removes, does not add back verbatim, and
   does not widen. The grain is `path::def:Lnnn`, one row per hunk. The
   exact predicate is in section 7.

Each hit is a `touch_strays` row, `open`. `mergeable` holds the batch,
`touch_strayed` wakes the Architect, and `judge_touch` closes it. A
mistake wakes the Developer to take it out. A foreseen hit shows in (a)'s
notice. He sees only what the Architect kept. The gate is a fact, a line
the diff holds, judged by a seat. It keeps all three sentences (reasoned).
The detector does not judge meaning, so the Critic's failure mode does not
enter. On the table it names 7 of 12, in 4 of 6 batches, with 0 false
notices. It misses the interrupt branch (3), the duplicate block (1) and
the widened message line (1), and the `obj is None` branch rides on b_1's `file` row (observed: section
3; reasoned). Price: 2 cycles, one for the detector and the hold, one for
the notice.

**(f) Refuse the write itself.** `code.write` refuses an optional
parameter or a removal no criterion names. **Crosses the ruling "A write
is permitted on any file"** (ruled: Roman, 2026-10-17, DECISIONS, cited at
`lifecycle.py` 758) and law 12, "the touch set is a prediction, never a
permission". Named only to set it aside.

| Option | He sees | Gate | Outside named | False | Crosses | Cycles |
|---|---|---|---|---|---|---|
| (a) at line map | a notice after the merge | none | 5 of 12 | 6 | none | 1 |
| (b) | a page per merge, not waited for | none | 5 of 12 | 6 | composition 103 | 1.5 |
| (c) | nothing | Architect, on the Critic's map | unknown, the model judges | 6 doc hunks to map | none | 2+ |
| (d) | every diff | his approval | 12 of 12 | 12 to read | composition 23 | 0 code |
| (e) | a notice of foreseen hits | Architect, on a fact | 7 of 12 | 0 | none | 2 |
| (f) | nothing | the write door | 7 of 12 | 0 | ruling 2026-10-17, law 12 | 1 |

## 5. The recommendation

**Build (e).** It is the only option that can remove a stray before the
merge with no new page, and it reads no meaning (reasoned: section 4).
The frame's measure counts merges that hold a change outside the
criteria. A notice alone leaves that count where it is. The stray hold
moves it when the Architect says mistake, and the notice covers the
foreseen rest, so nothing stays invisible (reasoned). The Architect
judged a definition stray `mistake` on night 159 (observed: night 159
`touch_strays`), so the route works on its own grain today.

**Pass plan.**

1. Pass 1, 1 cycle. The detector in `code_commit` beside
   `_unnamed_def_strays` (`api.py` 18741), its rows, and the red tests
   below. `mergeable`, `touch_strayed` and `judge_touch` take the rows as
   they are, because `_covers` already folds `path::name` grains under a
   bare path (observed: `api.py` 19643 to 19652). Check that `_covers`
   matches the new `path::def(param)` and `path::def:Lnnn` forms exactly.
2. Pass 2, 1 cycle. The notice: under `render_state`'s Done line, each
   merged batch with a foreseen row, the definition and the hunk's lines.
   A night-report section prints the same rows. `batches.strays` gets its
   first reader.
3. One review per pass. Total 2 cycles, 3 with a fix round.

**The red tests**, each on the clickI commits, git read-only, and a copy
of the night's database:

- Night 161 b_1, `2c8cd3ac..e7e4a7a6`: the detector raises
  `src/click/utils.py::echo_json(file)`. On a copy of
  `.rota/clickI_night161.db`, `mergeable(conn, 'b_1')` returns
  "touch strayed, unjudged" until `judge_touch` lands.
- Night 161 b_3, `9d92a758..9622b3e5`: the detector raises one row for the
  "``err``" docstring line in `confirm`, and no row for
  `default_on_eof: bool = False` or its `:param` lines.
- Night 158 bg_3, `75cf8ed0..ea03bf63`: rows for the deleted
  `versionchanged` lines and the deleted `ctx.exit()`, and no row for the
  widened `message %` line (section 7).
- Night 154 b1, `2c8cd3ac..0365603d`: rows for `echo_json(file)` and
  `echo_json(nl)`, and no row for `obj`, which has no default.
- Green controls: night 159 bg_1 `2c8cd3ac..d58b48d4` and night 156 bg_1
  `2c8cd3ac..bc1acb67` raise nothing.

**The measure for the next night.** Count merged batches with a hunk
outside the criteria by the reading of section 3. Count the shape hits
the Architect judged mistake and the Developer took out. Count every
foreseen hit listed on the end state. The design passes when no merged
batch holds a shape hit that is not on the end state, and the merged
count with a shape hit falls from 2 of 2 on night 161 (reasoned). The
interrupt branch is out of the measure's reach, so the frame's 0 of 3 may
need a second repair.

**What the design does not do.**

- It does not catch an over-wide clause around the criterion's own lines,
  such as `except (KeyboardInterrupt, EOFError)`. That needs a criterion
  that names interrupts, or a Critic who reads the clause. Night 161's
  read already marks it "reasoned, as on night 160".
- It does not catch added code that is dead or duplicated (night 158's
  block).
- It does not show him a diff, and it adds no page or question.
- It does not change the Critic's map or the write door.
- It raises a removed line in every repository, so a feature that edits
  an existing call costs one Architect wake. The two shapes are generic,
  not fitted to click, but that price is not measured outside clickI
  (reasoned).

## 6. Questions for Roman

None. Option (e) keeps the three sentences and rides the stray route
that Roman ruled on 2026-10-17 (observed: `lifecycle.py` 758). Options
(b), (d) and (f) cross the composition or a ruling, and the design does
not recommend them, so no question is open.

## 7. The removal shape beside the note door

Read on Opus, 2026-10-24, at 850a8906. Script for the price:
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f33f3f44-c058-42c9-90d1-bfcf8f3dafaa/scratchpad/f306_shape_price.py`.

**Result: both stand, with a split by what each one can see. The note
door holds a removed base statement before the commit. Shape 2 raises
what the door cannot see after the commit: docstring and comment lines,
and statements that the write result reads as changed.** No noted
removal reaches a merge at HEAD, so landed notes give the notice nothing
to list (reasoned: 7.1).

### 7.1 The note door today

- **What a note is.** A `code.write` whose text drops a statement that
  the batch's base holds returns a `dropped` note. The note names the
  path, each dropped line with its owner definition, and the line number
  (observed: `drop_notes` rows, night 161, "This write removes 4
  statements that your text does not hold: ..."). A note is a statement
  note. A docstring line is not a statement, so it opens no note
  (observed: night 158 bg_3 deleted 13 docstring lines and its only note
  names `ctx.exit()`).
- **Where it is stored.** The `drop_notes` table, one row per batch and
  path, with `status`, `note`, `lines`, `defs`, `whole` and `noted`
  (observed: `rota/core/schema.sql` 370). The status is `open` until a
  write puts the lines back or a `ledger.log` names a shown line, and then
  `restored` (observed: `plans/stack.md` frame 283, the passes of
  2026-10-17).
- **The door.** `code_commit` (`rota/roles/api.py` 18574) calls two
  checks before it commits (18592 to 18597).
  `_unread_drop_refusal` (18768) refuses while a note is open and the
  commit takes its path. `_unruled_removal` (18830) reads the `restored`
  rows and refuses when the tree still lacks a stored line that no
  criterion, request text or landed ruling asks to remove
  (`_unruled_gone` 19117, `_ruling_texts` 19124). So a note alone no
  longer discharges a removal. Only the restored lines or words that ask
  for the removal let the commit land (observed: the code; frame 283 W1 a,
  e60a3c25, after night 158's bb7c4492).
- **Who reads a note after the commit.** Nobody but the door. The readers
  of `drop_notes` are `_closed_notes` (18913), `_open_notes` (19163), and
  `discard_uncommitted` and `close_restored_notes` in
  `rota/core/lifecycle.py` 291 and 320 (observed: `python -m
  rota.tools.map table drop_notes`). No Architect wake, no Critic brief
  and no page reads the table. A removal that a ruling admitted is
  invisible after the commit, as every other change is (reasoned: section
  1).

**How shape 2 relates.** On a base statement that a write drops, shape 2
and the door see the same fact. The door acts first and stops the commit,
so a dropped statement reaches shape 2 only when the door admitted it on
words that ask for the removal. On a docstring line, and on a statement
that `_changed_kept` reads as a changed line, the door sees nothing and
shape 2 is the only check (observed: `_gone_statements` 18935 reads
stored statement lines; reasoned). On the table of section 3:

| Hunk outside the criteria | The note door at HEAD | Shape 2 |
|---|---|---|
| Night 158 bg_3, 13 docstring lines deleted | blind, a docstring line | row |
| Night 158 bg_3, `ctx.exit()` deleted | refuses the commit; bb7c4492 landed it on the note's claim before W1 a | row, if a ruling admits it |
| Night 158 bg_3, the widened `message %` line | blind | silent, a widening |
| Night 161 b_3, "``err``" to "`err`" | blind, a docstring line | row |

**The three choices, counted on the 12 hunks of section 3.**

- Shape 2 reads the notes and raises only a noted removal: 0 of 12 at
  HEAD. A noted removal lands only when restored or ruled, and the one
  that merged, night 158's `ctx.exit()`, is now refused at the commit.
- Shape 2 is dropped and landed notes feed pass 2's notice: 0 of 12 in the
  notice. The door still stops `ctx.exit()`, so 1 of 12 is held, by the
  door.
- **Both stand: 7 of 12 hunks in 4 of 6 batches. The door holds 1 hunk,
  `ctx.exit()`, before the commit. The detector raises 6 hunks in 6 rows:
  shape 1 on night 154 b1 (`file`, `nl`) and night 161 b_1 (`file`, which
  covers its 3 hunks), shape 2 on night 158 bg_3's docstring deletion and
  night 161 b_3's docstring edit.** Recommended. The door and shape 2 do
  not raise the same line twice, because the door's refusal keeps a
  dropped statement out of every commit unless words admit it (reasoned).

### 7.2 Shape 2's exact rule

A hunk H of `git diff -U0 <base> <commit> -- <source paths>` raises one
row when H holds a removed line r for which all three hold:

1. `r.strip()` is not empty.
2. `r.strip()` is not the stripped text of any added line in the diff of
   the same file. A moved line is not a removal.
3. No added line a of H holds `r.strip()` as a character subsequence of
   `a.strip()`. A line that only gains characters is a widening, not a
   removal.

**Night 161 b_3's signature line is silent because H has no removed line
at all.** The hunk is `@@ -295,0 +296,1 @@`, one added line,
`default_on_eof: bool = False,`, in a signature of one parameter per line
(observed: the script, "new 296,1 old 295,0"). Section 4's red test holds
with no exemption. The exemption of rule 3 is for the general case, a
one-line signature `def f(a, b=1):` that becomes `def f(a, b=1, c=2):`.
The old line is a subsequence of the new, so shape 2 is silent, and the
new optional parameter is shape 1's row.

**Rule 3 reads no criterion words. It is a character test on the diff.**
Its price on the table: night 158 bg_3's message line is a widening, so
shape 2 is silent on the line that holds the " (...)" his words refused.
That case is the other half of frame 306, the hop from his words to the
criterion (reasoned).

**Shape 1 does read criterion words.** A new optional parameter is silent
when its name is a token of a criterion text or a surface ref of the
batch. That is a token match, not a seat's judgement, and it can miss: a
criterion that says "file" for another reason silences a `file`
parameter. Plainly, it is a word-reading guard of the kind cause 5 warns
of: "every judgement-shaped guard regressed a register case or gained
nothing" (observed: `plans/wall-guide.md` 329). The guard is kept because
without it shape 1 raises every asked parameter, `default_on_eof` and
`show_python` on 4 of 8 batches. Its errors fall on the safe side for the
gate, because a miss lets a parameter through to the notice and never
blocks a right merge (reasoned).

Shape 2 does not reuse the door's `_asks_removal` to skip a removal that
a ruling admitted. That skip would read his words, and the cost of not
skipping is one Architect wake that answers foreseen (reasoned).

### 7.3 The price on a whole night

Each `code.commit` is diffed from the batch's base to the commit, as
`_unnamed_def_strays` reads it. A grain judged once is not raised again
(observed: `api.py` 19582 to 19584). The commits are the night report's
per-session commit lines. Neither night had a `touch_strayed` wake
(observed: `sessions.wake_kind`).

- **Night 160:** 8 commits, shape 1 on 0, shape 2 on 0, so 0 Architect
  wakes beside 0 actual `touch_strayed` wakes.
- **Night 161:** 12 commits, shape 1 on 3 (b_1 from 8ff5eca), shape 2 on 5
  (b_3 from d9db63f, the "``err``" line; b_5 from d51d168, its rewritten
  `message %` line), so 3 Architect wakes, one per first raise, beside 0
  actual `touch_strayed` wakes. If the Architect is slow and the Developer
  commits again, the count stays 3, because the hold reads the head.

The b_5 hit is a rewrite the feature needs, so 1 of the 3 wakes answers
foreseen. That wake is the cost of a rule that reads no words (reasoned).

## Usage

The harness count is not visible to this agent.
