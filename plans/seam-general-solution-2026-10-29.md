# The rulings seam: the general solution from what exists

Read of 2026-10-29, frame 345. No code changed. Counts come from
`l3r_baseline.txt` (head, 0 of 24) and `l3r_main_record.txt` (after W14,
1 of 24) in the session scratchpad, and from five scripts in the same
scratchpad: `l3r_count.py`, `l3r_case.py`, `l3r_door.py`, `l3r_code_reader.py`,
`l3r_bind.py`. The Gemma file `l3r_gemma.txt` was empty when this was
written.

## The result first

Propose candidate (d), a mix of (a) and (b) that the code already holds.
Code binds each page line to the clause of his reply that names it, and
the context shows that binding to the seat. The seat then gives each line
one word that is both the verdict and the act. Code fills the span from
the bound clause and the target kind from the word.

- The seat's largest error is not the verdict. It is the act that it
  leaves out: 241 line rulings landed with the right verdict and no act
  (observed: `l3r_case.py` on the main record).
- The doors teach that error. Every act refusal ends with "or leave the
  act out" (observed: `rota/roles/api.py` 14411, 14431, 14460).
- The code reader of his words is worse at polarity than the seat, and
  better at binding. It binds 119 of 132 lines that need a non-approve
  ruling (observed: `l3r_bind.py`). It reads 13 of 22 cases with at least
  one wrong verdict (observed: `l3r_code_reader.py`).
- So meaning stays with the seat, and code gives the seat facts before it
  chooses. This is the place that the ruling of 2026-10-26 names.

## 1. What the seat must produce, and what it gets wrong

Today one call carries, for each line: a verdict, an optional act, a
target kind, a target, and a span of his words. It can use the object
form or the flat `acts` form (observed: `landing.md` lines 11 to 20).

Field counts, main record, 72 runs (observed: `l3r_count.py`,
`l3r_case.py`):

| Field | Wrong in landed rulings | Refusals that caught it |
|---|---|---|
| No landing at all | 16 runs, 7 cases | the loops below |
| Act left out | 241 line rulings, 15 cases | none: the door permits it |
| Act named wrong | 18 (remove for drop, exclude, rewrite) | "ask no removal" 13 |
| Target kind | follows the act, 0 errors of its own | none |
| Span of his words | lands only when right | "the act X rests on ''" 59 |
| Verdict | 23 line rulings, 7 cases | see section 2 |
| Line left out | 28, all read-back lines | read-back door 27 |
| Form | n/a | not a line 10, acts key 5, other form 9 |

The baseline shows the same order: span 22 + 6 + others, read-back 28,
`_faulted_approve` 22, "have no ruling" 21, form about 35 (observed:
`l3r_count.py` on the baseline).

The 28 "line N: no ruling" are read-back lines. The seat approved them,
the read-back door refused, and the seat then left the line out (observed:
the case lines 5, 6, 4, 10, 47 and 68 of the refusing cases). In 5 of the 7
cases that the door fired on, the judge says approve is right (observed:
`l3_rulings.yaml` judge lines of n170-m58, n170-m74, n171-m27, n172-m76,
n172-m97). The door reads "reads my last answer correctly" as a fault
(observed: `_line_cues` gives the cue `reads`).

The seven no-landing cases loop on the span door: n175-m116 11 span
refusals, n172-m92 8 span and 5 removal, n173-m90-m91 6 span (observed:
`l3r_door.py`).

## 2. Where the seat read wrong with no door firing

| Case | Line | Seat | Judge | What the seat misread |
|---|---|---|---|---|
| n172-m80-m81 | 1 | contest | approve | "drop it" bound to line 1 |
| n173-m34-m35 | 7 | contest | revise | "slightly off ... not one" |
| n173-m90-m92 | 9, 10 | contest | approve | the range "11 and 13 to 22" |
| n175-m121-m122 | 9 | revise | approve | "change only the docstring ... not the code" |
| n175-m136-m138 | 2 | contest | approve | "instead of giving up" |
| n175-m136-m138 | 7, 8 | approve | contest, drop | "Removing lines 7 and 8 is right" |
| n175-m75-m77 | 6 | revise | contest, rewrite | "Replace line 6 with" |

(observed: the assertion lines of the main record.) Three of these seven
match a cue of `_faulted_approve` that refused the seat earlier in the
same run: "drop" (m80), "not" (m121), "instead" (m136) (observed:
`l3r_door.py`, the faulted_approve row). The door moved the seat to the
code's reading, and the code's reading is wrong there (observed:
`l3r_code_reader.py` gives the same wrong verdicts on m80 line 1, m121
line 9, m136 line 2). One case is no reading of words: n174-m53-m58 needs
the fact that the page's change is merged (observed: its judge line).

## 3. The candidates

### (a) The seat quotes, code derives verdict and act

The seat gives per line the sentence of his reply. Code derives the
verdict and the act through `said` and a verb table.

- Reach by construction: the verdict is right where `_line_cues` is
  right, 9 of 22 cases (observed: `l3r_code_reader.py`). The act needs a
  verb table. "Lines 11 to 22 are wrong because ..." must be a drop, and
  "Line 5 is wrong" must be a rewrite (observed: judge lines of
  n173-m90-m91 and n173-m61-m62). No verb table derives those. About 5
  cases right (reasoned).
- Cannot: the 13 cases where the code's polarity is wrong. The errors
  become silent rows, not refusals (reasoned).
- Reuses `said`, `_line_cues`, `_cue_clauses`. Removes the meaning doors.
- Against the ruling: it makes code the reader of meaning. That is the
  symptom of 2026-10-28 (reasoned).
- Price: a new verb table and its growth per night. Three or more cycles,
  and it grows (reasoned: `_line_cues` grew one shape per night, frames
  234, 250, 305).

### (b) The prompt only: rows with kinds, one example per act, one call per line

- `landing.md` already has one example per act (observed: lines 21 to 37).
  W14 edited the prompt and moved 0 to 1 (observed: the brief).
- Cannot: the read-back door and `_faulted_approve` refuse right readings
  for any prompt, 44 refusals in the main record (observed). The span
  door still loops. One call per line multiplies turns across the same
  doors (reasoned).
- Reuses everything. Removes nothing. Price: one cycle. Reach: 1 to 3
  cases (reasoned).

### (c) A stronger model in the Liaison seat only

- Can: better spans, fewer form errors, fewer left-out acts (reasoned).
- Cannot: the 44 false refusals, and the exit "leave the act out" (reasoned).
  The seven misreads of section 2 are partly door-made (observed).
- Price: no code. One cycle per model run.

### (d) Proposed: code binds, the seat picks one word per line

1. The runner adds to the `landing` payload, for each page line, the
   clause of his words that names it, or "not named". The source is
   `api._cue_clauses` or `LineReading.refs`, the reader that 38 callers
   share (observed: `rota.tools.map fn _line_reading`). The text is his,
   through `said`.
2. The seat gives each line one word: approve, drop, rewrite, keep,
   exclude with a path, add, contest, revise. A table of about eight rows
   in `rulings_rule` turns the word into the object shape that the door
   checks today. The table is the act list of `landing.md`, not a reader of
   his words (reasoned).
3. Code fills `words` with the bound clause and `target_kind` from the
   word. The span door then checks his own text and cannot refuse it.
4. For a line that is not named, the seat quotes his words. That is 13 of
   132 lines: the adds on line 1, "the second line", the read-back with
   "the other lines are fine" (observed: `l3r_bind.py`). The existing span
   check `_words_from` proves the quote.
5. The read-back approve rests on that fact: a bound clause or a proved
   quote. Its polarity check through `_line_reading(his).matched` goes.

- Reach by construction: the act cannot be left out on a line the seat
  rules as drop, rewrite, exclude, keep or add. The span loops end. The
  read-back and `_faulted_approve` refusals of right readings end. About
  17 cases lose every recorded block (reasoned: 15 act-missing cases and
  the 7 no-landing cases, less the overlap and the cases in the next line).
- Cannot by construction: the seat's own misreads of section 2, about 3
  cases left after the door-made ones (m34 line 7, m136 lines 7 and 8,
  m75-m77 line 6), and n174-m53-m58, which needs the merged fact in the
  payload. Those stay with the seat and the measure (reasoned).
- Reuses `said`, `_cue_clauses`, `LineReading.refs`, the object form,
  `_words_from`, `_names_path`, `_shown_prediction`, the L3 runner.
- Removes: the flat `acts` form, the stray-field and acts-key form
  errors, the empty-span refusals, and, behind the L3 measure,
  `_faulted_approve`, `_unnamed_contest`, `_agreed_contest` and the
  read-back polarity check. These are the reading doors of appendix D of
  `plans/paths-nights170-173.md`. The fact doors stay. No new door.
- Price: one frame. One implementer pass for the payload field (about 30
  lines in `rota/core/runner.py` near 2388), the word table (about 25
  lines in `rulings_rule`), and `landing.md` cut to about 45 lines. One
  review. Re-record the 24 L3 cases and the 12 L1 landing cases, about
  12 minutes per L3 run. A second pass retires the reading doors once
  the measure holds (reasoned).

Why (d): it is the only candidate that keeps meaning with the seat, as the
ruling of 2026-10-28 asks, and gives the seat facts before it chooses, as
the ruling of 2026-10-26 asks. It removes the exit that makes the seat drop
the act, which is the largest field error (reasoned).

## 4. The Gemma trial: what a model change can and cannot fix

`l3r_gemma.txt` was empty at writing. By field (reasoned):

| Field | A model change can fix | A model change cannot fix |
|---|---|---|
| Verdict polarity | some of the 3 seat-made misreads | 4 door-made misreads while `_faulted_approve` refuses |
| Read-back lines | nothing | the 27 refusals of right approves |
| Act left out | some, if it keeps the act under refusal | the exit text that invites it |
| Act named wrong | likely most (remove against drop) | none in principle |
| Span | likely most paraphrases | none in principle |
| Form | likely most | none in principle |

A Gemma score above qwen3:8b measures the model. It does not show the
doors are right, because 44 refusals of the main record fall on right
readings for any model (observed: section 1 and appendix D, 5.2).
