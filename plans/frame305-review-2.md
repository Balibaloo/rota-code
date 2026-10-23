# Frame 305, review 2: pass 2 at e76212ee

Reviewer on Opus, read-only. Worktree `C:/Users/roman/rota_r305` at
e76212ee, parent e630519c. Verdict: do not accept for the branch yet. The
reader is right on 153 of 166 changed messages. Two high defects stay: the
m46 door gap and the agreement phrases that turn a fault into a match.

## (a) The claim, point by point

1. The count: CONFIRMED 166 of 803. My reading gives 153 right, 6 wrong and 7 doubtful. Four wrong ones are high for their night.
2. The m46 gap: CONFIRMED. At e76212ee the request door returns None on m46, so a line-1 contest lands and cancels the change. High.
3. The rules beyond the brief: 4 agreement phrases have one recorded sentence each, and the review names them fits. The three rules have 8 to 21 sentences each.
4. Nothing else changed: CONFIRMED. All hunks are in the line reader, api.py 9579 to 10043. Both changed expectations are his meaning. The tests pass.

## (b) Findings

### Point 1: the count

I re-ran the count with my own probe on the commits themselves, not on the
implementer's worktree. It gives 803 messages and 166 changed, the same
as the report. I read every entry, old set against new set.

- Right: 153.
- Wrong: 6.
- Doubtful: 7.

The wrong ones:

1. Night 140 m6. "Ok, the glossary matches how Click uses those words, so go ahead. Lines 13 to 23 list kinds of users rather than words with more than one meaning, but they don't conflict with anything I asked for." Old: faulted {}, matched {}. New: faulted {13 to 23}, cue "list". Right: faulted {}. High for the night. CONFIRMED: `_faulted_approve` refuses an approve of lines 13 to 23 on this reply.
2. Night 144 m112. "My note on line 1 only asked you to drop the part ..., so the line as it reads now is right ... My note on line 10 only meant the "does today" part shouldn't say the helper already exists". Old: faulted {1}. New: faulted {1, 10}, line 1 on "asked". Right: faulted {10}, matched {1}. High for the night, because the reader faults a line he called right. The old reader had the same fault on line 1. CONFIRMED: the approve door refuses an approve of line 1.
3. Night 150 m114. "Ok, I approve the page. Please read line 1 as the details of line 2 and not as a separate change". Old: faulted {2}. New: faulted {1, 2}, line 1 on "read". Right: faulted {}. High for the night, PLAUSIBLE: a fault on line 1 opens the request door to a line-1 contest, because `_line_refusal` returns early when line 1 is faulted.
4. Night 150 m123. "Ok, I approve. Line 1 is the detail for line 2 and not a separate change." Old: faulted {2}. New: faulted {1, 2}, line 1 on "is". Right: faulted {}. High, as entry 3. CONFIRMED that the approve door refuses lines 1 and 2 when line 1 is not a request.
5. Night 150 m139. "Ok, I approve the page. Line 1 gives the details for line 2 and is not a separate change." Old: faulted {2}. New: faulted {1, 2}, line 1 on "gives". Right: faulted {}. High, as entry 3.
6. Night 155 m_shift_echo_json_tests_m_p2. "This page also shows no line 2, so I cannot say what to do with it." Old: faulted {}. New: faulted {2}, cue "cannot say". Right: faulted {}. Low: the page has no line 2.

The doubtful ones:

1. Night 142 m86. "Line 1 says what I asked for. The test files it names have nothing to do with echo". New matches line 1, but the next sentence faults its test files.
2. Night 143 m272. "For line 8, keep it off by default, and take the confirm flag out of this change". New matches line 8 on "keep". The answer can revise line 8.
3. Night 144 m94. "On line 3, keep it simple and let the standard json module raise its own error". New matches line 3 on "keep". The sentence is an answer, not an agreement.
4. Night 146 m250. "Ok, that's what I asked for. Line 2 just repeats line 1". New faults line 2 on an approval. Other nights read "only repeats" as "drop it".
5. Night 150 m_shift_confirm_default_on_eof_m_p3. "Put line 1 aside for later." New faults line 1 on "Put" on a shift page.
6. Night 156 m_shift_echo_json_m_p2. "Later for line 1, so set the echo helper aside". New faults line 1 on "set" on a shift page.
7. Night 154 m22. "On line 3, please add ... Lines 2 and 3 are otherwise fine". New puts line 3 in both sets. `_line_refusal` reads matched minus faulted, so the fault wins, and that is his meaning.

The implementer's reading of "about 150 right and about 12 wrong or doubtful" holds. Fix: read an approval opener ("Ok, I approve", "go ahead") as a frame for the reply, and let a describing verb with no fault word take no direction after it.

### Point 2: the m46 gap

Night 151's m46 reply was "Please don't drop this change. I'd rather you
try again and fix the failing tests. Lines 2 and 3 now say what I want,
and the fix should still use only the standard json module." The seat
contested line 1, the request. On night 151 that contest cancelled bg_1
(frame 258, pass 2, as the `_line_refusal` comment records).

- At e630519c the reader faults lines 2 and 3 on "should" and "still". The door refuses with "The words fault lines 2 and 3. Line 1 is the request, and they do not fault it. Rule lines 2 and 3, and approve the rest." The refusal stops the contest, but its text names a leaked fault.
- At e76212ee the reader matches lines 2 and 3 and faults none. `named` is empty, so `_line_refusal` returns `approve`, which is None. CONFIRMED by `doors.py`: refusal None with and without the request texts, and `_KEEP_CHANGE` matches the words.
- What lands wrongly: the line-1 contest lands, and it cancels the change he asked to keep.

Night 151's m64 has the same shape ("Please don't drop this change ...
Lines 2 and 3 say what I want"). The gap is a shape, not one sentence.
Severity: high for the night, high for the frame.

Fix line on `_line_refusal`: before `if not named or 1 in faulted: return approve`, refuse a line-1 contest when 1 is not in `faulted` and `_KEEP_CHANGE` matches, with "The words do not fault line 1, and they ask to keep the change. Approve line 1."

### Point 3: the rules beyond the brief

The probe `shapes.py` counts the distinct recorded messages of the 803 in
which each shape decides a reference.

Added agreement phrases:

| Phrase | Sentence behind it | Messages | Reading |
|---|---|---|---|
| "is fixed" | night 158 m148, "line 3 is fixed" | 1 | fit |
| "needs no change" | night 157 m22, "line 1 needs no change" | 1 | fit |
| "is not a real problem" | night 150 m66, "line 7 is not a real problem" | 1 | fit |
| "is the version I approved" | night 147 m19 (145 m19 is the same text) | 1 distinct | fit |
| "correctly" | night 143 m88 | 2 (m88, m93) | second sentence exists |
| "as they are" | night 159 m212 | 2 (152 m137, 154 m130) | second sentence exists |
| "says what I asked for" | night 142 m86 | 5 | second sentence exists |
| "now says" and kin | night 140 m142 | 8 | second sentence exists |
| "already ...s" | night 143 m76, 140 m147 | 6 | second sentence exists |

Added rules:

| Rule | Sentence behind it | Messages |
|---|---|---|
| A reason clause keeps the old reading | night 140 m142, "since line 1 now says" | 9 |
| A line in an object phrase keeps the old reading | night 145 m11, "repeats the summary from line 1" | 21 |
| A question keeps the old reading | night 149 m57, "what does line 3 mean" | 8 |

Fit count: 4. The three rules each have a second sentence of the same shape.

### Point 4: nothing else changed

`git diff e630519c e76212ee --stat` shows four files: `rota/roles/api.py`
(+379, -44 in total), `tests/rota/test_frame234_verdict_lines.py`,
`tests/rota/test_frame250_verdict_faults.py` and
`tests/rota/test_frame305_line_reader.py`. Every api.py hunk is in the
line reader, lines 9579 to 10043. No door code changed.

- Frame 234, "Please drop note 8. Note 9 is fine.": the new value ({8}, {9}) is his meaning. He asked to drop note 8.
- Frame 250, night 149 m105, "Lines 3 and 5 can be checked simply: call confirm without the flag ...": the faulted set is the same, and the cue is now "can be checked". The clause instructs how to check, so a fault there is his meaning. The refusal shows his instruction in place of the later "wrong".
- The xfail on `test_m46s_contest_of_the_request_line_is_refused` hides the point 2 gap. It is strict, so the fix in point 2 turns it into an XPASS failure, and the fixer must restore the test with the new expected text.

Tests at e76212ee, with `pytest -n 0`: `test_frame305_line_reader.py`,
`test_frame234_verdict_lines.py`, `test_frame250_verdict_faults.py`,
`test_frame255_files_correction.py` and `test_runner.py` give 275 passed,
7 xfailed in 107 s.

### Findings outside the points

1. Outside. `rota/roles/api.py:9682` to 9708, `_AGREEMENT`. High for the frame, low for the night. CONFIRMED with `gen.py`. The open "already" and "now" shapes turn a fault into a match. "Line 7 already has the broken check, so fix it." reads matched {7}. "Line 4 now says the wrong thing." reads matched {4}. "Line 2 now has a typo." reads matched {2}. The first check of `_line_refusal` then refuses a contest of those lines with "a contest reverses the principal". No recorded sentence of the 803 has this shape, so the count does not show it. Night 142's m109 has the near shape "Line 7 still has the broken check". Fix: limit "already" and "now" to "says", "covers" and "does" before "what I" or "that", and fault the clause when a fault word follows in it.
2. Outside. `rota/roles/api.py:9993` to 10043, `_line_cues`. Low for the night and the frame. CONFIRMED by `count.py`. Night 154 m22 and night 157 m162 put line 3 in both sets. Every reader of the pair must know that the fault wins. Fix: remove the faulted lines from `matched` before `_line_cues` returns.

## (c) Probes

All probes are in
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b85289fd-418f-43a1-a641-15dad2620cfa/scratchpad/r305b/`.

- `old_api.py` and `new_api.py`: `git show` of `rota/roles/api.py` at e630519c and e76212ee. `new_api.py` is byte-equal to the worktree file.
- `count.py`: runs both readers over the 803 recorded messages of nights 140 to 159. It prints 166 changed, and the messages with a line in both sets.
- `rows.json`: the 803 message keys that `count.py` read.
- `doors.py`: imports the worktree api. It runs `_line_refusal` on M46 with a line-1 contest, and `_faulted_approve` on night 140 m6, night 150 m123 and night 144 m112.
- `shapes.py`: wraps `_agreement` and `_head_verb` in the new reader and counts the messages that each added shape decides.
- `gen.py`: seven sentences that no night recorded, against the "already", "now", "matches" and "is fixed" shapes.
- The test run of point 4, from the worktree root.

## (d) Usage

No exact meter. About 95k input tokens and 12k output tokens, about 107k in total. The brief's cap was about 60k.
