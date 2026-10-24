# Frame 312, review of row 5: commit 16c36c2f

Verdict: the commit does not stand. The page renders m115's shape. But
it states a false cause, and the route it offers needs a false
correction. Reviewer on Opus, read only, in `C:/Users/roman/rota_p312w5`.

## (a) The verdict on each point

1. Pass in form, fail in fact. The night's rows render the page (quoted below). It names
   the file, the line, the function and the written file, with no rota
   names. Its cause line is false for night 163 (finding 1).
2. The row is the note of the last write that landed, not of the last attempt.
   A failed session lands no staged note row. The page shows every
   note row for a written path, with the ask for the first path only (findings 4, 5).
3. Fail. The page's own sentence lands at the door only when the Liaison keys the
   ruling to the batch's rows and passes the words whole. His plain words
   are refused. Words alone do not restart the team (finding 2).
4. Fail. The file is gone. Each Developer session's end puts the tree
   back to HEAD (finding 3).
5. Pass. Review, tests_failing and tests_missing keys show no refusal lines.
   The page tests pass: 137 passed, 4 xfailed.
6. Pass. No page test holds a length bound. The check lines drop only when
   `_refused_commit` returns lines. The night's page went from 22 to 19 lines.
7. Information, not proof. Every Developer session's discard sets the row to `restored`, so
   the page must read it. The status alone does not show a refusal (finding 4).

The page from night 163's own rows, key forced to quarantined at 3 (probe 2):

```
The team gave up: the change could not start after 3 attempts.
A check refused each commit, because the change removes `return` at line 609 of src/click/termui.py, in clear(), and no words of yours ask for that.
The check lets the commit through when the code keeps that line, or when your words ask to remove it.
The team wrote src/click/termui.py and did not commit it.
If the change must remove it, say so, as 'remove the `return` at line 609 in clear()'. The team starts again only when you correct a line here.
```

## (b) Findings

1. `rota/roles/principal.py` 1427-1430. High. CONFIRMED. The page says
   the change "removes `return` at line 609" and "no words of yours ask
   for that". Line 609 of the base is the bare `return` under
   `if not isatty(sys.stdout):`. s254's write puts `return False` there.
   Page lines 4 and 7 ask for exactly that: "clear() returns False when
   stdout is not a terminal". The note says "removes or rewrites". The
   page drops "rewrites" and so turns the door's misreading into his fault.
   Fix: say "rewrites" when the note does, and quote the new line. Open a
   frame for the door: `_asks_removal` does not read a rewrite that a
   criterion asks for.
2. `rota/roles/principal.py` 1433-1436. High. CONFIRMED for the words,
   PLAUSIBLE for the restart. The probe landed rulings on the night copy.
   The page's phrase lands when the ruling is keyed to a criterion or to
   the batch rows. It is refused when keyed to the page alone. His own
   words "clear() must return False there instead of the bare return" are refused.
   An approve with empty words is refused. So the route depends on how the
   Liaison writes the ruling. That is a seat's route. A landed ruling does not lift the quarantine. Only a moved
   criteria row does (`rota/core/db.py` 641-655). On m115 he agrees with
   every line, so the restart asks for a correction he does not mean.
   That is the wall in a new form. Fix: let a landed ruling that names the batch lift the
   Developer start key, or take the route to Roman for a ruling.
3. `rota/roles/principal.py` 1431. Medium. CONFIRMED by read. `_discard_at_end`
   runs at every Developer session end, on success (`runner.py` 6004) and
   failure (6096). It calls `discard_uncommitted` (`lifecycle.py` 264).
   At render the written file is not in the tree. "wrote ... and did not
   commit it" reads as code that waits for him. Fix: "The team wrote
   src/click/termui.py three times, and each time the runner put the file back."
4. `rota/roles/principal.py` 1388-1411. Medium. PLAUSIBLE. The page
   says "A check refused each commit" when any note row of any status
   exists for a written path. It never reads a refusal. The row has one
   key per batch and path, so a later landed write overwrites it. A failed
   session lands none (`api.py` `_put_note`). The session query has no
   bound to the current quarantine cycle. A commit refused for a test or a
   syntax error, with an old note on the path, gets this page. Fix: take
   the refusal from the last `code.commit` result of the key's sessions,
   or run `_unruled_gone` on HEAD and the note at render.
5. `rota/roles/principal.py` 1432-1436. Low. PLAUSIBLE. With two notes
   the page lists both, but the ask names `asks[0]` only. The text says
   "that line" and "it". Fix: one ask for each note, plural text.

## (c) Probes

All are in the scratchpad
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/a0790d20-6463-44cf-97ca-89e1ddd75c84/scratchpad/`.
Each one opens the night db read only and copies it into memory.

1. `r5_p1.py`, `r5_p2.py`: drop_notes rows, sessions s221-s254, their
   `code.write` and `code.commit` calls. bg_2's row is `restored`.
2. `r5_p4.py`, `r5_p5.py`: render m115 from the night's refs. The night
   ends with the key unquarantined, so `r5_p5.py` sets it to 3.
3. `r5_p6.py`, `r5_p7.py`, `r5_p8.py`: s254's write text. It holds
   `return False` under the isatty check. The base file is read in the
   clickI checkout.
4. `r5_p9b.py`: three other keys render no refusal lines. Five rulings
   run through `_ruling_texts` and `_unruled_gone` on the rewritten text.
5. Pytest: `test_frame312_stuck_review.py`, `test_request_page.py`,
   `test_park_page.py`. 137 passed, 4 xfailed.

## (d) Usage

Input tokens about 60k, output tokens about 9k, total about 69k. The
harness shows no exact count to the reviewer.

## Re-check of 26186652

Verdict: the commit does not stand. Findings 3, 4 and 5 are closed. Finding 1 is closed
in its text, and a medium remains on the offered sentence. Finding 2 is
closed for the restart. A new high replaces it: the page says "the team
reads your words", and the Developer's window does not hold them.

The page at m115's own moment (probe `r6_p3.py`, sessions after s222 cut,
key at 3):

```
The team gave up: the change could not start after 3 attempts.
A check refused the commits, because the change rewrites `return` at line 609 of src/click/termui.py, in clear(), as `return False`.
To allow that, say so, as 'remove the `return` at line 609 in clear()'.
The team wrote src/click/termui.py 2 times, and the runner put the file back each time.
Your answer to this page starts the team once more, and the team reads your words. Do not correct a line that you agree with.
```

1. Finding 1: closed in text. The page now says "rewrites ... as
   `return False`". A medium remains on the offered sentence at
   `principal.py` about 1462. The door admits only removal words:
   `_REMOVAL_WORDS` in `api.py` 19665 holds remove, drop, delete, take
   out, no longer, stop and without. Probe `r6_p4.py`: "change ... to `return False`",
   "replace ... with `return False`" and "rewrite ... as `return False`"
   are all refused. So the page cannot offer the rewrite's own words
   today, and "remove" is the only sentence the door admits. That
   sentence also admits a pure removal of the guard, which he did not ask
   for. CONFIRMED. Fix: teach `_removal_spans` a rewrite verb with its
   new text, and admit only that new line. Then offer "change the
   `return` at line 609 in clear() to `return False`". Do it in a new frame.
2. Finding 2: closed for the restart. `land` at `principal.py` 2137-2144
   deletes the quarantined `developer|tick:batch_start` key that the
   page's `stalled:` config row names. The night's config holds
   `stalled:m115` with that key. The lift runs only when the ask closes,
   so a words reply lifts the key when `apply_rulings` lands the Liaison's ruling.
3. New, high, CONFIRMED (`principal.py` about 1471-1473). "the team
   reads your words" is false. Probe `r6_p4.py` landed an approve-all
   ruling with the page's sentence on the night copy. Then it built the
   Developer's `tick:batch_start` window with `push_working_set`. The
   pushes are `batches.expect`, `criteria.load`, `glossary.lookup`,
   `the principal contested these criteria` and `tickets.load`. His words
   are in none of them. The only ruling push is `contests_on`
   (`runner.py` 568), which shows contested criteria only. The page
   tells him not to contest a line. So the route the page advises keeps
   his words out of the window. Only the commit door reads them, through
   `_ruling_texts`. Fix: push the landed rulings that `_ruling_texts`
   returns with the principal's flag into the Developer start window. Or
   change the text to "the check reads your words".
4. Finding 3: closed. The page says the runner put the file back each
   time. "2 times" beside "3 attempts" is true. s220 wrote no file.
5. Finding 4: closed. The page runs `_unruled_gone` on the row's
   `noted` text at render. It counts only the last N sessions of the
   key, where N is the key's attempts. At the end of night 163 the last
   three bg_2 start sessions, s259 to s261, wrote nothing, so no
   refusal shows. That is correct.
6. Finding 5: closed. The page gives one ask for each gone statement.

Counts: 11 page files with the frame's file: 259 passed, 5 xfailed.

Probes, in the scratchpad named in (c): `r6_p1.py` reads the row's
`noted` text and `stalled:m115`. `r6_p2.py` lists the last start
sessions. `r6_p3.py` renders m115 at its own moment. `r6_p4.py` builds
the Developer window and tries three rewrite sentences.

Usage of the re-check: input about 45k, output about 5k, total about 50k.

## Re-check of a3f2d8e8

Verdict: the commit stands. The open high from the re-check of 26186652
is closed.

1. The window holds his words. CONFIRMED. Probe `r6_p4.py` ran again on
   the night copy. It lands an approve-all ruling on m115 with the page's
   sentence. Then it builds the Developer's `tick:batch_start` window for
   bg_2. The window now has the push "the principal's words on this
   change, newest last". Probe `r7_p1.py` prints that block: the night's
   two newest landed words, then "remove the `return` at line 609 in
   clear()" last. So the page's line "the team reads your words" is true.
2. The medium on the offered "remove" sentence stays open, as the
   re-check of 26186652 says. It needs a door change in a new frame.

Counts: `test_prompts.py` with `test_frame312_stuck_review.py`: 49 passed.

Usage of this re-check: input about 8k, output about 2k, total about 10k.
