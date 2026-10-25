# Frame 306, W-A, the provenance: his page line numbers reach a seat that does not see the page

Provenance read, 2026-10-25, at 9581584f. Databases night 150 to 165,
`?mode=ro`. Meta workflow. No model ran. No other file changed.

## The verdict

**Two wakes quote his whole reply to a seat, with no map from his line
numbers to the rows. The record of that map exists: `principal.land`
stores the page order at his reply, and `_ruling_line` reads it. The quote
never uses it. No ruling of Roman's chose a verbatim quote to a seat. On 3
of 17 nights a seat landed his page line numbers as criterion text.**

## 1. The mechanism today

1. The Liaison passes his reply whole as `words`. `landing.md` says "with
   the reply as `words`", and `answering.md` line 20 says "Put the
   principal's words whole in `words`" (observed). `rulings_rule`,
   `rota/roles/api.py` 11940, stores `words` as given, at 12382 to 12385
   (observed). r_ee6e30a55d's `words` equal m37's `body_text`, and
   r_39fbc7b24e's equal m201's (observed: night 165, `rulings`, `messages`).
2. The repair wake. `build_prompt`, `rota/core/runner.py` 768, calls
   `_last_word_lines` (518) on `tick:criterion_repair`. For each criterion
   ref, lines 551 to 556 append "The principal's last word on this
   criterion" with `ruled['words']` whole, then "Write the criterion in the
   principal's words." (observed). `_contest_block` (600 to 629) adds the
   contested text and "He said:" with the same words.
3. The challenge wake. `runner.py` 4226 to 4235 puts `_contest_block` after
   `criteria.load` for a Developer or a Tester (observed). The relay wake of
   the Terminologist gets it from `_relay_contest_block` (632).
4. What the seat sees beside the quote: the criteria rows by id, the
   contested texts by id, and the code. It never sees the page, so "line 3"
   has no referent. The block says "He contested crit_2_..., crit_3_..." and
   does not say which line each was (observed: s359 seq 1, the user field).
5. The map exists. `config` holds `order:m37` = `["get_app_dir_windows",
   "c1", "c2", "c3", "c4", "c6", "c8", "bg_1"]` and `order:m201` with
   crit_2 on line 3 and crit_3 on line 4 (observed). `_ruling_line`,
   `api.py` 6406, reads that order, frame 272. `_ruling_words_on`, 6479,
   keeps the sentences of the words that bear on one criterion, frame 308.
   Only the respecify doors use the two. The wakes do not (observed: grep).

Cases. s132 woke for c1, saw his sentences on lines 2 to 7, and landed the
whole reply as c1's text (observed: s132 turns 2 and 3). s147 sent the same
for c2. s149 failed bg_1 on that text. s359 cut 17 docstring lines in
f465478 (observed: `plans/night165-read.md`, W-A).

## 2. The origin

- 33cd99b2, 2026-10-13 06:42, frames 226 and 227, night 144: "The
  criterion repair wake carries the principal's last ruling verbatim", and
  "Write the criterion in the principal's words" (observed: the commit,
  `git log -S`). The wall was s546, which put back a flag he contested.
- 7a2cb843, 2026-10-15, frame 243 pass 1b, night 149: the same words as a
  block after the criteria for the Developer and the Tester (observed).
- Rulings. DECISIONS, 2026-10-08, point 2: "the Tester rewrites the test
  from the ruled words", and point 4: every word of his "is a ruling on a
  row" (observed). These say where his words land, not how a line number
  reaches a seat. I found no ruling of Roman's on the quote's form
  (observed: grep of DECISIONS and `plans/frame243-scope.md`).

## 3. The design's own condition

`plans/composition.md` line 27: "The wiring records the words verbatim
before the Liaison wakes. The Liaison's confirmed reading is a second
record." Line 106: "The verbatim words and the confirmed reading are two
records. An unchecked inference is never a record" (observed). Liaison
`base.md`: "The words stay verbatim ... Never tidy, summarise or correct a
principal's words" (observed).

So the words are one record and the `per_item` reading is a second. The
page order at his reply ties his numbers to that reading. The wakes send
the first record and a bare list of ids, and drop the order that joins
them (reasoned: section 1, step 5). A repair keeps his words verbatim and
writes no reading into his quote (reasoned: composition line 106).

## 4. The count

Over 17 databases, night 150 to 165 with 164a, 266 of 647 live rulings
hold "line N" in `words` (observed: script over `rulings`).

His page line numbers in a criterion text, by a Terminologist's
`criteria.specify` or `criteria.respecify` (observed: `turns`, a script
on the `text=` argument and the next turn's `OK`):

| Night | Sessions that landed the text | Tried, not seen to land | Criterion at night end |
|---|---|---|---|
| 155 | none | s380 "Line 1 adds ..." | clean |
| 157 | s257 | s265, s355 | cr_2 v5 "Lines 3 and 4 ..." |
| 159 | none | s250, s302 | clean |
| 160 | s195, s211, s219, s227, s246, s255, s265 | none | cr_2 v15 "Line 3's check ...", cr_3 v8 "Line 4's check ..." |
| 161 | none | s288 | clean |
| 165 | s132 | s147, s328 | c1 later fixed to v4 |

That is 9 sessions that landed and 9 that tried, on 6 nights. A script
cannot count the test and code edits that read a number as a code line.
The night reads name two: night 160 W2, where s256 encoded cr_3's note
into a test that stayed red, and night 165, s359's docstring cut (observed:
`plans/night160-read.md` line 272).

Night 160 W2 is the same wall. Its fix, 4093b0ca, refuses a sentence whose
subject is a page line or a check (`_CHECK_SUBJECT`, api.py 5410). s132's
"Change line 2 so ..." opens with a verb, so it passed (reasoned: the
regex, and s132's `OK`). The wake that sends the bare number stays.

## 5. The repair's shape

**A. A line legend beside his words, and the sentences of his row.** Where
`_last_word_lines` and `_contest_block` quote a ruling, read `order:<reply
id>` and add one line per number his words name: "On his page, line 3 was
crit_2_format_invalid_bytes: <its text>". His words stay verbatim, as
composition line 106 requires. On the repair wake, quote only
`_ruling_words_on` for the woken criterion, and change "Write the
criterion in the principal's words" to "Write the behaviour his words ask
for. His line numbers name lines of his page, listed above." s132 then
sees the line 2 sentence for c1 with c1's text beside it, and has no lines
5 and 6 to copy. s149 then reviews a behaviour, not an instruction. s359
sees that lines 3 and 4 were crit_2 and crit_3, so "remove both lines"
names two criteria, not docstring lines. Red tests: s132's wake on
r_ee6e30a55d, s359's wake on r_39fbc7b24e. About 2 cycles.

**B. A respecify door that refuses any page line number in a criterion
text.** Widen 4093b0ca to any "line N" not followed by "of". s132 and s147
are refused. The door does not reach s359, whose wake carries the same
bare number into a code edit that no door reads. About 1 cycle.

**I favour A.** It acts at the hop where the number loses its referent,
for every seat that gets the quote. It reuses `_ruling_line` and
`_ruling_words_on`, and it keeps the two records apart. B covers one seat,
and s359 shows the wall in a code edit that B cannot see.
