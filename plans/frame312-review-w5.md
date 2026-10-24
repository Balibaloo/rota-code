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
