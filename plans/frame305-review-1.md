# Frame 305, review 1: pass 1 at 666b92dc

Reviewer on Opus, 2026-10-23. Read-only. Worktree `C:/Users/roman/rota_r305`
at 666b92dc, parent 0dc04800. The old reader ran from `git archive 0dc04800`
in the reviewer's scratchpad (`r305/old`). The night databases were opened
with `?mode=ro`. No gate ran, and no test ran. The probe scripts are
`r305/p1.py` to `r305/p4.py` in the holding session's scratchpad.

## Verdict

Accept for the night. The m105 right map passes frame 250's door, and the
four recorded relating sentences now land on the repeating line. The
re-present names a wrong line on 0 of 14 recorded pages, against 5 of 14
before. The pass lost no right reading on the recorded words. All findings
are low. Each is a shape with no recorded case, or a case the pass did not
change.

## Findings

1. **Low, CONFIRMED. `returned_line` misses a bare number after a sentence
   break.** `_LINE_REF` reads a bare "3 is wrong" only at `^`, with `re.M`.
   `_line_cues` splits the words into sentences first, so `^` is a sentence
   start there. `returned_line` runs over the whole body, so `^` is a text
   line start. On "Line 2 is fine. 3 is wrong." the reader of `rulings.rule`
   names lines 2 and 3, and `returned_line` names line 2 alone. The page
   then says "your words about line 2", and his words were about two lines.
   No recorded re-present has this shape.
   Fix: read the references sentence by sentence with the split of
   `_line_cues`, `re.split(r"(?<=[.!?])\s+|[:;]", ...)`.

2. **Low, CONFIRMED. A negated cue moves to the subject.** "Line 7 repeats
   line 3, but do not drop it" gives `{7: 'drop'}`. His words keep both
   lines. Before the pass the reader gave `{3: 'drop'}`, so both readings
   are wrong. Now frame 250's door refuses an approve of line 7, the line
   he asked to keep. The cause is the old rule "strong cue wins over 'not'".
   No recorded case.
   Fix: a "not", "don't" or "do not" directly before a strong cue cancels that cue.

3. **Low, CONFIRMED. "both" loses the object.** "Line 7 repeats line 3, so
   drop both" gives `{7: 'drop'}`. His words fault lines 3 and 7. Before the
   pass the reader gave line 3 alone. The door refuses no contest of both
   lines, so the seat can still rule his map. No recorded case.
   Fix: "both" after a relating pair binds the cue to the subject and the object.

4. **Low, CONFIRMED. A shared reference with "say the same thing" forces a
   wrong contest.** "Lines 3 and 7 say the same thing, drop line 7" faults
   lines 3 and 7. His words drop line 7 only. A map that approves line 3 is
   refused: 'The words fault line 3, "drop"'. The pass did not change this.
   "say the same thing" without "as" is outside `_RELATING`, and "Lines 3
   and 7" is one reference. This is the frame's wall in another shape. No
   recorded case.
   Fix: a cue directly before a reference binds to that reference only, in any sentence.

5. **Low, CONFIRMED. "Drop it." in the next sentence faults nothing.** "Line 7
   repeats line 3. Drop it." gives no fault, as before the pass. The door
   refuses neither a contest of line 7 nor an approve, so no wrong ruling is
   forced. No recorded case.
   Fix: none in this frame. A later frame can carry "it" to the subject of the sentence before it.

6. **Low, CONFIRMED by probe, meaning by reading. Three recorded sentences
   of night 150 still fault the object.** m115, m124 and m140 say "Line 1 is
   the detail for line 2 and not a separate change". The "not" belongs to
   line 1. Both readers give `{2: 'not'}`, and the door refuses an approve
   of line 2. The closed verb list of `_RELATING` does not reach this
   relation. The pass did not change these readings.
   Fix: measure the subject rule on every two-line sentence before the list grows.

7. **Low, PLAUSIBLE. The no-line text gives no reason.** A principal who
   wrote "drop line 7" reads "The team could not turn your words into a
   ruling. Answer the page again, and say for each line you want changed
   what to do with it." He did say what to do with line 7. The text tells
   him to answer again, so he knows the next step. The text does not tell
   him what to change in his answer. The three sentences hold 11, 10 and 17
   words, within 20. The form with a line holds 13 in its second sentence.
   Fix: none in this frame. The reason belongs to a ruling on the text, which no ruling of Roman's names.

## Point 1: the bare-number grammar

The only bare-number form in `rulings.rule` is the second branch of
`_LINE_REF`, a number at a sentence start before "is", "are", "'s" or ":".
`_line_cues` gives each sentence to `_LINE_REF`, so the sentence start
counts. "Approve 2" and "1 ok" name no line under any reader of
`rulings.rule` (probe). The frame 267 test's reply is "1 ok, 11 is not about
this page". Under `_line_cues` it names no line, because "11" follows a
comma and not a sentence break. With a period, "1 ok. 11 is not about this
page" faults line 11. His meaning names two lines, 1 and 11. So the
reader's rule and his meaning both give no number. The pass did not change
a right test to fit its code. The old "about line 11" came from the seat's
refusal ("line 11: 'ask' is a question back"). That text was frame 267's
design, which the provenance shows to be the wrong source. `returned_line`
must read the references by sentence, as finding 1 says.

## Point 2: the night replay

Night 158's m105, read by the new `_line_cues` with a size of 8, gives
`{2: 'wrong', 7: 'drop'}`. The old reader gave `{2: 'wrong', 3: 'drop'}`.
The page has no batch line, and line 1 is the request. Results of frame 250's
door, `_faulted_approve`, and of `_line_refusal`:

| Map | Old | New |
|---|---|---|
| approve 1, 3 to 6, contest 2, 7, 8 (the right map) | refused, line 3 "drop" | passes |
| approve 1, 3 to 6 and 8, contest 2, 7 | refused, line 3 | passes |
| approve 7 | passes | refused, line 7 "drop" |

The three relating sentences of section 5, read from their databases, each
land on the repeating line. Night 140's m56 gives line 4, and the whole
message gives lines 3, 4 and 7. Night 142's m7 gives line 41. Night 147's
m87 gives line 7. The line repeated is in none of the four results.

## Point 3: the width of the rule

| Words | New reader | Old reader | His meaning | Binding |
|---|---|---|---|---|
| Drop line 3, because it repeats line 7 | 3 drop | none | drop 3 | right |
| Lines 3 and 7 say the same thing, drop line 7 | 3, 7 drop | 3, 7 drop | drop 7 | wrong, line 3 (finding 4) |
| Line 7 repeats line 3, but do not drop it | 7 drop | 3 drop | keep both | wrong, line 7 (finding 2) |
| Line 7 repeats line 3. Drop it. | none | none | drop 7 | missed, no harm (finding 5) |
| Line 7 repeats line 3, so drop both | 7 drop | 3 drop | drop 3 and 7 | line 3 missed (finding 3) |

Two more probes. "Line 7 repeats line 3, which is not a problem" gives
`{7: 'not'}`, as the pass report says. "Line 7 repeats line 3 and line 3 is
wrong" gives `{3: 'wrong'}`, which is right.

## Point 4: the count before and after

Twelve sentences name two single lines with every fault cue after the
second reference (`f305_count.py`'s filter).

| Night, message | Sentence, shortened | Old | New | His meaning |
|---|---|---|---|---|
| 140 m37 | Line 2 pairs ... doesn't match it, and line 8 is wrong | 8 | 8 | 8, and 2 by "doesn't match" |
| 140 m56 | Line 4 repeats line 2, so please remove it | 2 | 4 | 4 |
| 142 m7 | Line 41 repeats line 37 ... drop it | 37 | 41 | 41 |
| 142 m235 | Line 1 is right, but line 2 is still wrong | 2 | 2 | 2 |
| 144 m51 | Each one repeats line 1 ... line 5 wrongly says | 5 | 5 | 5 |
| 147 m87 | Line 7 just repeats line 2 ... drop it | 2 | 7 | 7 |
| 149 m39 | Line 2 is fine, but line 3 is wrong | 3 | 3 | 3 |
| 150 m115 | read line 1 as the details of line 2 and not as a separate change | 2 | 2 | 1 |
| 150 m124 | Line 1 is the detail for line 2 and not a separate change | 2 | 2 | 1 |
| 150 m140 | Line 1 gives the details for line 2 and is not a separate change | 2 | 2 | 1 |
| 155 m238 | Line 1 is fine, but line 2 still names the wrong test file | 2 | 2 | 2 |
| 158 m105 | Line 7 just repeats line 3 ... drop it | 3 | 7 | 7 |

Four readings moved, and each moved to his meaning. Three wrong readings
stay (finding 6). The pass lost no right reading.

The fourteen re-presents, the line each text names:

| Night, page | Old | New | His words name |
|---|---|---|---|
| 152 m96 | 5 | 5 | 5 |
| 152 m137 | 2 | 2 | 2 |
| 153 m123 | none | none | none |
| 154 m22 | 1 | 1 | 1 |
| 154 m130 | 4 | none | 1, 2, 5 |
| 154 m174 | none | none | 1 to 4, 6, 7, 10 to 14 |
| 155 shift page | 2 | 1 | 1 |
| 156 m22 | 1 | 1 | 1 |
| 156 m104 | 5 | none | 2 to 4 |
| 157 m22 | 1 | none | none |
| 157 m139 | none | none | more than one |
| 157 m210 | none | none | more than one |
| 158 m89 | none | none | more than one |
| 158 m122 | 1 | none | none |

Old: 5 lines his words did not name. New: none. The four right lines of the
old text stay, and the shift page gains one.

## Point 5: the texts and the prefix

The prefix comes from `session_commit` in `rota/core/db.py`, the second
miss: it writes `f"{result.trigger_msg}: {_why_no_ruling(result)}"` on the
page. `_page_under_reply` takes the page as the trigger's `cause_id`, and
the trigger is a principal `converse`. So the `cause_id = ask_id` and
`from_role = 'principal'` conditions of `returned_line` hold by
construction. The other notes on asks (`UNRECEIVED_NOTE`, the report note)
set the status to `unresolved`, and `returned_line` reads only `open` rows.
Over nights 140 to 158, every note on a message to the principal starts
with a reply id (14 of 14, and no note without the prefix). The doubt of
the pass report does not hold on the record.

The text can name a line his words did not name only through the bare
form. A text line that starts "10:30" reads as line 10 in both readers
(reasoned from the pattern). Finding 1 is the case where his words named
two lines and the text names one.

## Point 6: nothing else changed

`git diff 0dc04800 666b92dc --stat` shows four files: `rota/roles/api.py`,
`rota/roles/principal.py`, `tests/rota/test_frame305_line_reader.py` and
`tests/rota/test_runner.py`. The `api.py` diff has three hunks. The first
adds `_RELATING` and its comment above `_line_cues`. The other two are
inside `_line_cues`, lines 9387 to 9449 by the map tool. No line outside
`_line_cues` and its constant changed. The `test_runner.py` change is the
expected text and a two-line comment of one test.
