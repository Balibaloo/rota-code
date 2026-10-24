# Frame 306, the provenance: his words about a check become the criterion's text, and a deletion outside the criteria merges with no page that shows it

Provenance read on Opus, 2026-10-24, second edition. The first edition of
2026-10-23 (commit 6dc7706c) read night 158 only. This edition adds night
160's W2, the count over nights 140 to 160, and the repair. Repository at
HEAD 53e49cfb. Night 160 ran at 695e8be7 (observed: `plans/night160-read.md`
line 4). Databases `.rota/clickI_night140.db` to `.rota/clickI_night160.db`,
opened `?mode=ro`. The sample tree `D:/repos/_AI/sample_repos/clickI`, git
read-only. Meta workflow. No file but this one is changed.

## The verdict

**The words stop at one design choice: a page line is a criterion, so his
note about a line's check is ruled as a contest of the criterion, and the
Terminologist's brief tells it to write the criterion "in the principal's
words", while `criteria.respecify` refuses only a test-subject text and the
same words sent back, never a new text that names a page line or a check**
(observed: `rota/roles/prompts/terminologist/criterion_repair.md` 22 to 31,
`rota/core/runner.py` 493, `rota/roles/api.py` 5076 and 5894 to 6093).

No ruling of Roman's decided that the criterion takes his words about a
check. His ruling of 2026-10-08, point 2, says the opposite order: "A
contest or a revision moves the criterion's version, the Tester rewrites
the test from the ruled words" (ruled: `rota/DECISIONS.md` 1459 to 1465).
The text rule came from frames 226 and 227, commit 33cd99b2 of 2026-10-13
(observed: the commit body).

## 1. The hop today, from a page reply to a criterion's text

The seats wake in this order (observed: night 160, `messages` m75 to m78,
`turns` s195; the code at HEAD):

1. The Liaison shows the page. Each criterion row carries its check line,
   by point 2 of the 2026-10-08 ruling (observed: `render_page`,
   `rota/roles/principal.py` 1456, and `request_block` 1145).
2. He replies. The Liaison calls `rulings.rule`, which is `rulings_rule`
   (`rota/roles/api.py` 10986). The row stores `per_item`, his `words`,
   and `texts`, the contested criterion texts from `contested_texts`
   (`principal.py` 712; written at `api.py` 11387 to 11394).
3. `land` (`principal.py` 1847) and `apply_rulings` (`principal.py` 2331)
   close the ask. The relay of a contest on a criterion goes to the
   Terminologist. `park_criterion_relay` (`rota/core/scheduler.py` 1843)
   and `ruled_clarify_criteria` (1873) key the wake as `criterion_repair`.
4. The runner builds the wake: `resolve_inbound` (`runner.py` 1936) and
   the repair block at `runner.py` 480 to 500, which prints his last words
   per criterion and "Write the criterion in the principal's words. Do not
   send the sentence he contested." `_contest_block` (`runner.py` 539) adds
   every contested text.
5. The Terminologist calls `criteria.respecify`, which is
   `criteria_respecify` (`api.py` 5894). That door writes the criterion.
   Then it calls `msg.answer_tester` with the criteria in `refs`. The
   Tester reads his words through the chain as `principal_said` (observed:
   `rota/core/sandbox.py` 1647 to 1673 and 3281 to 3298).
6. The Tester rewrites the test from the new criterion text and his words.

**A route to the Tester exists, and it runs only behind a respecify**
(observed: the brief, lines 26 to 31: "Send that answer only after each
respecify lands"). The only path that skips the respecify is
`principal_test_verdict`, which needs a ruling keyed on a test row, and
"The principal never rules on a test" (ruled: 2026-10-08, point 2). On a
park page the row he faults is always the criterion row (reasoned).

The commits that built each hop:

| Hop | Commit | Date | Decided by |
|---|---|---|---|
| A park page with criterion rows and their check lines | b0a2086e, 2dace61b | 2026-10-09 | Roman's ruling of 2026-10-08 23:25, `DECISIONS.md` 1445 |
| A contest of a criterion on a park page wakes `criterion_repair` | 172b373b | 2026-10-09 | the diff review of b0a2086e |
| `texts` on a ruling, and "Write the criterion in the principal's words" | 33cd99b2, 81ce21b7 | 2026-10-13 | frames 226 and 227, after night 144 |
| The answer to the Tester after the respecify, and `principal_test_verdict` | 126b8c4e, 57c1a869 | 2026-10-13 | frame 213 fix 1 and a review |
| The door: a criterion whose subject is the tests | db3b0944 | 2026-09-02 | S0 walks 11 to 28 |
| The door: a check fault refuses the same words, "The criterion stands" | 84a06216 (`_CHECK_FAULT`, `api.py` 5418) | 2026-10-13 | frame 226 candidate E |
| The answer carries every ruled criterion | 983194bd | 2026-10-23 | frame 308 |
| A clarify reply rules the asker's rows | 6e72b8b9 (`answer_about`, `runner.py` 183) | 2026-10-23 | frame 306 repair 1 |
| A ruling read per criterion on the page order | c93d8d8c, 63cf4993, e62e1081, 6413e4ee | 2026-10-23 | frame 308, after night 160 ran |

**The sentence that decided the rewrite from his words is a frame's, not
Roman's.** "The criterion repair wake carries the principal's last ruling
verbatim" (observed: 33cd99b2). No ruling, frame or review separates his
words about a check from his words about a behaviour at the Terminologist.
The `_CHECK_FAULT` door separates them only when the seat sends the
criterion's own words back (observed: `api.py` 6041 to 6045, the branch
needs `_same_words(text, cur["text"])`). A new text that copies the note
passes every door (reasoned: the branches of `criteria_respecify`).

## 2. Where the words stopped

**Night 158, bg_3, "Do not put parentheses around it."** The brief names
m145. m145 is the Liaison's clarify, and the words are his reply m146
(observed: first edition, section 1, `.rota/night158.log` line 151). The
clarify carried only `tst_version_option_shows_python_02`. Liaison s286
ruled `{cr_2: approve, tst_02: approve}`, and the door refused cr_2 as no
row of the question. s286 then ruled `{tst_02: approve}`, so no contest
reached cr_2. The relay woke s287 in `relay` mode, which cannot respecify
(observed: `turns` s286 t1 and t2, s287 t1 to t6). cr_2 kept "contain",
which admits "(Python 3.14.2)" (observed: `criteria`, night 158). Repair 1
landed as 6e72b8b9 and closes the refused key (observed: commit). It
moves nothing when the seat rules an approve, because only a contest or a
revise wakes `criterion_repair` (observed: `plans/frame306-review-1.md`,
finding 1).

**Night 160, bg_2, the note in the criterion.** The first note came from
his m76 on page m75, which faulted only checks: "Line 4's check only looks
at the signature, but it should check that confirm's docstring explains
the flag. Line 3's check should also close stdin first" (observed:
`rulings` r_42118c7554). The Liaison ruled cr_2 and cr_3 `contest`,
because the page lines 3 and 4 are criteria (observed: `per_item`).

s195 woke on relay m78 in `criterion_repair`. Its wake showed "He contested
this text" with the old behaviour texts, his words, and the brief line
"Write the criterion in the principal's words" (observed: `turns` s195 t1).
It wrote the note as the text, and the door admitted both (observed:
`receipts` s195, cr_2 v6, cr_3 v7):

```
criteria.respecify(id='cr_2_confirm_default_on_eof', text="Line 3's check must close stdin first to show that confirm() returns the default at end of input without waiting.", term_refs=['line'], surface_refs=['src/click/termui.py::confirm'])
criteria.respecify(id='cr_3_confirm_default_on_eof', text="Line 4's check must verify that confirm()'s docstring explains the 'default_on_eof' flag and its effect on EOF behavior.", term_refs=['line'], surface_refs=['src/click/termui.py::confirm'])
```

Its turn 2 says why: "the checks must be observable and testable against
the `confirm` implementation" (observed: `turns` s195 t2). The repair brief
asks for "words that name an observable outcome", and a check is the most
observable thing in his words (reasoned).

**m84 to m121.** He then said six times that the text is "my note pasted
in" (observed: `rulings` r_9b2fa6b320, r_ac7f186294, r_b9397f2bc9,
r_13005d5d2c, r_44b442e2a3, r_04b24ea9ce). Each reply mixed a behaviour
sentence and a check sentence for the same line. Each was ruled `contest`
of the criterion, so each woke a Terminologist with every earlier ruling
(observed: `turns` s255 t1 lists r_42118c7554 first). The `texts` column
then quoted the note-shaped text as "He contested this text", so the wake
showed the note as the thing to replace and his words as the thing to
write (observed: r_ac7f186294 `texts`). s211 copied his meta sentence into
cr_2: "The text of line 3 should also say what confirm must do again"
(observed: r_ac7f186294 `texts`).

s255 woke on m117 for m114's reply. It tried six times. The door refused
cr_3 with "Write what he asked for. Send his words about the check to the
Tester", from the same-words branch (observed: `turns` s255 t7). Turn 4's
calls landed as cr_2 v13 and cr_3 v14 (observed: `receipts`; the texts
match the head rows):

```
criteria.respecify(id='cr_2_confirm_default_on_eof', text="Line 3's check must close stdin first to give confirm an empty, closed input before calling it. Its text should say that with the flag on and stdin closed, confirm returns the default right away without waiting for input.", term_refs=['default_on_eof'], surface_refs=['src/click/termui.py::confirm'])
criteria.respecify(id='cr_3_confirm_default_on_eof', text="Line 4's check must verify that confirm()'s docstring explains what happens at end of input, specifically that with the flag on and stdin closed, confirm returns the default right away without waiting.", term_refs=['default_on_eof'], surface_refs=['src/click/termui.py::confirm'])
```

**Why a note and not a behaviour.** Three causes act together (reasoned:
the calls above and the doors).

- His words name the line and the check. The page made the check part of
  the criterion row, so the Liaison had no other row to rule.
- The brief says to write the criterion in his words, and his words were
  about the check.
- No door reads the new text for a page line or a check. `_about_the_tests`
  matches only a text that starts with "the tests" (`api.py` 5076 to 5086).

The Tester then encoded the note's wording as an assertion, "without
waiting" or "immediately", and the head docstring failed it (observed:
`plans/night160-read.md` section 2, W2).

## 3. The evidence page before a merge

**No page shows him the diff, and no page lists a deletion** (observed:
`principal.py`, `render_page` 1456, `request_block` 1145, `code_line` 1108,
`_park_page` 1294; no renderer reads a diff). The pages show the request
lines, each criterion with its check line, the team's guess or plan of the
touch set as files, and on a park page the tests' state.

**The merge needs no page.** `mergeable` (`rota/core/lifecycle.py` 711)
holds on tests, verdicts, strays, reviews and constraints. The setting
`merge_gate = review` blocks with no page behind it, and the nights run
`auto` (observed: first edition, section 2). "Sign-offs after that,
including on merges, are opt-in" (ruled: Roman, 2026-09-16,
`plans/composition.md` 22 to 23).

**Neither frame 298's guess nor the stray route covers a deletion inside a
named definition.**

- Frame 298's guess is the Architect's scope guess at sign-off, before the
  build (observed: `plans/frame298-design.md` title). It predicts files,
  not lines.
- The stray route judges files (cf067ce4, 2026-09-13) and changed
  definitions no criterion names (`_unnamed_def_strays`, `api.py` 19162,
  b0dbd926, 2026-10-18; `batches_strays` 19283).
- bg_3's three deleted `versionchanged` entries sit in the docstring of
  `version_option`, which cr_2 names. So the definition is named, and no
  stray is recorded (reasoned: the door's grain is the definition).

## 4. The count over nights 140 to 160

Script: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0cdcac52-3588-4266-b1fb-fc5d7d31b805/scratchpad/f306_count.py`,
read-only. All 21 databases exist. Criterion versions come from three
places, because no table holds each version's text: the `criteria` rows,
every `criteria.specify` or `criteria.respecify` call parsed from
`turns.completion`, and the `rulings.texts` values.

**(a) Quoted phrases of four words or more in his ruling words: 13. Held
by no criterion text of the same item: 8.** Nights 144 (1), 146 (1), 147
(3), 156 (2), 157 (1). The test reads any version, not only later ones,
so 8 is a lower bound. The measure is blind to night 158 and night 160,
because "Do not put parentheses around it" and "my note pasted in" are not
quoted phrases. The first edition's wider count stands beside it: on
nights 156 to 158, 11 of 24 replies that fault a row left the row with no
later write.

```sql
SELECT id, per_item, words FROM rulings WHERE words != '';
-- per row: the items of the criteria in per_item; each "quoted" span of
-- 4+ words, normalised to [a-z0-9_] tokens, tested as a substring of the
-- normalised texts of every criterion version of those items
```

**(b) Criterion texts on file: 857. Texts that name a page line, a check
or a test: 46. Texts that name a page line ("Line N"): 15, on 5 criteria
over 4 nights:** night 155 `c_1_echo_json_tests` (1), night 157
`crit_show_python_help` (3), night 159 `cr_1_confirm_default_on_eof` (1),
night 160 cr_2 (7) and cr_3 (3). The shape is new from night 155 and
grows (observed).

```sql
SELECT id, text FROM criteria;
SELECT completion FROM turns WHERE completion LIKE '%criteria.%specify(%';
SELECT texts FROM rulings WHERE texts IS NOT NULL;
-- regex on each text: \bline \d+\b | \bcheck(s|ed|ing)?\b | \btests?\b
```

**(c) Merged batches: 23. Batches whose diff deletes a source line that
no criterion text names: 1, night 158 bg_3, 9 lines,** among them the
three `.. versionchanged:: 8.0` entries (observed: `git diff -U0` of
`merge-base(head, 2c8cd3a)` to the head, `src/` only). A deleted line
counts when its stripped text is not among the added lines and no token of
four letters or more is a word of the item's criteria. The first edition's
hunk count, which also reads added code, found 6 of 12 on nights 150 to
158.

```sql
SELECT id, item_id, head_commit FROM batches WHERE status = 'merged';
-- per row: git merge-base <head> 2c8cd3a; git diff -U0 <base> <head> -- src/
```

## 5. The repair

The candidates, one sentence each:

1. **The route.** In `criteria_respecify` (`api.py` 5894), when his words
   on this criterion's line match `_CHECK_FAULT` and not
   `_words_fault_on`, refuse any new text and point to
   `msg.answer_tester`, as the same-words branch does today.
2. **The text door.** `criteria_respecify` and `criteria_specify` refuse a
   text that names a page line ("Line 3's") or whose subject is a check,
   by a wider `_about_the_tests` (`api.py` 5076).
3. **The brief.** `criterion_repair.md` 22 to 31 and `runner.py` 493 say
   to write the behaviour his words ask for and to send his words about a
   check to the Tester, in place of "Write the criterion in the
   principal's words".
4. **The evidence page.** The end page and the night report list each
   merged line deletion that no criterion names, as a notice with no
   question, from `batches_strays` (`api.py` 19283).

**Recommended: the pair 2 and 1, in that order.** Candidate 2 keeps
db3b0944's design that "a criterion names what the program does", and it
catches all 15 "Line N" texts of section 4 (b) with no reading of his
words. Candidate 1 keeps the 2026-10-08 ruling, point 2, that the Tester
rewrites the test from the ruled words, and frame 213 fix 1's
`principal_said` route. It extends frame 308's "The criterion stands"
from the same words to any words. Candidate 3 is a brief change, and the
brief has said the opposite since 33cd99b2, so it follows the doors and
does not replace them (reasoned). Candidate 4 is a separate frame: it
fires on 1 batch of 23, and the merge page is his opt-in by the 2026-09-16
ruling.

**The red tests**, on copies of `.rota/clickI_night160.db`:

- s195 turn 1, before its landed writes: the two calls quoted in section
  2. Both must be refused, and the refusal must name
  `msg.answer_tester`.
- s255 turn 4, with relay m117 and ruling r_44b442e2a3 live: the two calls
  quoted in section 2. Both must be refused. A third case keeps a true
  behaviour text admitted: "With default_on_eof=True and stdin closed,
  confirm() returns the default without waiting for input."

**The doubt.** A check that is the behaviour, such as "the docstring
explains the flag", reads as a check to a regex. Candidate 2 must refuse
the page-line form and the "check must" subject, and not the word "check"
anywhere (reasoned: 46 texts hold the words, and 31 of them do not name a
line).

## Usage

The harness count is not visible to this agent. The meta workflow takes
the harness line as the measure.
