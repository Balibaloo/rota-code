# Frame 305, review 4: pass 2c at 2b0c71e8

Reviewer on Opus, read-only. Worktree `C:/Users/roman/rota_r305` at
2b0c71e8, parent 01cc956a. Verdict: do not accept for the branch yet. Every
recorded reading of the 803 except one is right or doubtful. The new
"gone fault" shape is open, and "now" or "no longer" with any verb turns a
fault into a match. One recorded sentence shows it.

## (a) The claim, point by point

1. Re-judge: CONFIRMED. 165 changed against e630519c and 4 against 01cc956a. The counts are 158 right, 1 wrong and 6 doubtful. My three highs of review 3 and my high outside the points now read right.
2. The additions beyond the brief: both have one recorded sentence each, so the fit count is 2.
3. The diff: CONFIRMED. Two files changed, and every hunk is in the line reader. The tests pass.

## (b) Findings

### Point 1: the re-judge

`count4.py` reproduces 165 and 4. The 4 changed against 01cc956a:

- Night 140 m142: faulted {3}, matched {1}. Right. The match lost in pass 2b is back.
- Night 150 m66: faulted {3, 5, 10, 12}, matched {7, 9}. Right. This was review 3's high 1.
- Night 153 m60: faulted {}, matched {1}. Right. This was review 3's high 2.
- Night 158 m148: faulted {}, matched {3}. Right. This was review 3's high 3.

Review 3's high outside the points now reads right. CONFIRMED with
`gen4.py`: "Ok, I approve the page. Please fix line 3." faults {3}, and
"Line 3 lists the pager tests. Trim it, and then go ahead." faults {3}.

- Right: 158.
- Wrong: 1. Night 155 m_shift_echo_json_tests_m_p2, "This page also shows no line 2, so I cannot say what to do with it." New: faulted {2}. Right: faulted {}. Low, because the page has no line 2.
- Doubtful: 6. Night 142 m86, 143 m272, 144 m94, 146 m250, 150 m_shift_confirm_default_on_eof_m_p3 and 156 m_shift_echo_json_m_p2. All six are unchanged since review 3.

### Point 2: the additions beyond the brief

1. `rota/roles/api.py:10019` to 10020, `_instruction_cue`. The rule deletes "go ahead and X" before the reader looks for an instruction. The sentence behind it is night 153 m60, "Line 1 now says the flag defaults to False, so please go ahead and build it." `count4.py` finds no other recorded reply with "go ahead and" after a line reference. This addition is a fit. Low for the night and the frame, because "go ahead" asks for the build and not for a change to the line.
2. `rota/roles/api.py:10154` to 10155, the `approves` branch of `_line_cues`. In an approving reply, a head verb followed by "as" takes no direction. The sentence behind it is night 150 m114, "Please read line 1 as the details of line 2". `count4.py` finds no other approving reply with a verb, a line reference and then "as". This addition is a fit. Low for the night and the frame.

Fit count: 2.

### Point 3: the diff

`git diff 01cc956a 2b0c71e8 --stat` shows `rota/roles/api.py` (63 lines)
and `tests/rota/test_frame305_line_reader.py` (34 lines). Each hunk is in
the line reader:

- `_AGREEMENT` drops "now" from the "already ...s" alternative.
- New `_FAULT_WORDS`, `_GONE` and `_GONE_ASKED`.
- `_strong_word` is removed.
- `_agreement` reads `_GONE`.
- `_instruction_cue` deletes "go ahead and X".
- `_line_cues` sets the approval frame per sentence and keeps a head verb in that frame.

The tests changed in two places. The pass 2b expectation of night 140 m142 goes back to matched {1}. The new test `test_pass_2c_readings` holds ten cases. Tests at 2b0c71e8, with `pytest -n 0`: `test_frame305_line_reader.py`, `test_frame234_verdict_lines.py`, `test_frame250_verdict_faults.py`, `test_frame255_files_correction.py` and `test_runner.py` give 299 passed and 5 xfailed.

### Findings outside the points

1. Outside. `rota/roles/api.py:9714` to 9720, `_GONE`, the "no longer" and "now ...s" alternatives. High for the frame, low for the night. CONFIRMED with `gen4.py`. Night 146 m101's second sentence on its own, "Line 1 also no longer says to use only the standard library json module, ... so please put both back.", reads matched {1}. He asks to put the text back. The reply is right today only because its first sentence faults line 1, and the fault wins. More sentences that no night recorded read as matched: "Line 2 no longer mentions the default.", "Line 3 now lists the pager tests too.", "Line 5 now names more files than I asked for." and "Line 6 now drops the newline." A contest of such a line is then refused with "a contest reverses the principal". Fix: let "now" agree only before "says", "covers", "shows" or "reads", and let "no longer" agree only when a fault word or a fault verb follows it in the clause.

## (c) Probes

All probes are in
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b85289fd-418f-43a1-a641-15dad2620cfa/scratchpad/r305b/`.

- `c_api.py`: `git show` of `rota/roles/api.py` at 2b0c71e8. It is byte-equal to the worktree file.
- `count4.py`: runs the readers of e630519c, 01cc956a and 2b0c71e8 over `rows.json`. It prints 165 and 4 changed, and the recorded sentences of each addition and of `_GONE`.
- `gen4.py`: thirteen sentences that no night recorded, against the approval frame and `_GONE`.
- A `python -c` call that reads night 146 m101's second sentence alone.
- The test run of point 3, from the worktree root.

## (d) Usage

No exact meter. About 20k input tokens and 5k output tokens for this review, about 25k in total. The cap was 20k.
