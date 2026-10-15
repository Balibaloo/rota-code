# Frame 256, review 1: pass 1 at 15cbf388, "through" as a range word

Verdict: accept. The diff does what the frame names, and the count holds. Three low findings sit outside the four points. No finding is high.

Worktree: `C:/Users/roman/rota_r256` at 15cbf388. Reviewer: an Opus agent, read-only. Date: 2026-10-15.

## (a) Verdicts on the points

1. PASS. `_LINE_REF` and `_ref_lines` agree on every lower-case shape. Mixed case "Through" disagrees (finding 1).
2. PASS. The recount gives 72 databases, 2036 principal messages, 12 with "through", 3 change, 9 do not.
3. PASS. The test is red at 4fe07692 because the old reader gives ({2}, set()). The test is green at 15cbf388, 48 passed. The full m96 reply faults {1, ..., 7}, not {2, ..., 7}.
4. Night 150 counts each principal reply with "lines N through M": the in-range lines read faulted or matched, and the unnamed contest door fires on 0 of their in-range contests.

## Point 1: the shapes

Each line shows the reading before (4fe07692) and after (15cbf388), as (faulted, matched). Probe: `r1/shapes.py`.

| words | before | after | reads as a range |
|---|---|---|---|
| lines 2 through 7 are wrong | ({2}, {}) | ({2..7}, {}) | yes |
| Lines 2 through 7 and 9 are wrong | ({2}, {}) | ({2..7, 9}, {}) | yes |
| lines 2 through 7, 9 and 11 are wrong | ({2}, {}) | ({2..7, 9, 11}, {}) | yes |
| notes 8 through 11 are fine | ({}, {8}) | ({}, {8..11}) | yes |
| lines 2 through 7 match | ({}, {2}) | ({}, {2..7}) | yes |
| line 3 through line 5 is wrong | ({5}, {}) | ({5}, {}) | no. The pattern does not admit the shape. Line 3 takes no direction, and line 4 is lost (finding 2) |
| 2 through 7 is wrong (sentence start) | ({}, {}) | ({}, {}) | no. The bare form takes one number before "is". "2 to 7 is wrong" also reads nothing, so the change keeps parity with "to" |
| lines 2 Through 7 are wrong | ({2}, {}) | ({2, 7}, {}) | no. The two patterns disagree (finding 1) |
| lines 7 through 2 are wrong | ({7}, {}) | ({2, 7}, {}) | no. A reversed range gives its two ends. "to" does the same |
| lines 2 thru 7 / 2 through to 7 | ({2}, {}) | ({2}, {}) | no. Out of scope |

The token "through" holds no "to", so the `_ref_lines` alternation reads it whole.

## Point 2: the count

My recount (`r1/count2.py`) runs the old and the new `_line_reading` on every principal message of every night database, read-only. It does not filter on "through" before it compares. Result: 72 databases, 2036 messages, 3 readings change. The 3 are night138 m214, night149 m92 and night149 m96. All 3 hold "lines N through M". The 9 other messages with "through" are night139 m93, night141 m17, night144 m317 and m339, night146 m46, m113, m120 and m170, and night149 m86. They are every principal message with "through" and no range, and none changes. The pass's `count.py` imports from `D:/repos/rota`, which held the edit at its run. The recount imports the committed tree and agrees.

## Point 3: the test

The old reader on the test's m96 sentence gives ({2}, set()). The test asserts ({2, ..., 7}, set()), so it fails for the reason it names: line 2 alone. The old reader gives ({}, {8}) on "notes 8 through 11 are fine". At 15cbf388 both asserts hold, and the file gives 48 passed.

The full m96 text from `clickI_night149.db` gives faulted {1, 2, 3, 4, 5, 6, 7} and matched {}. The third sentence, "Line 1 should point only at termui", adds line 1. So the first sentence alone is the right input for a {2, ..., 7} assert. The fourth sentence, "notes 8 to 11 have nothing to do with this change", takes no direction. `_unnamed_contest` still names lines 8 to 11 from the reference, so a contest of them passes that door.

## (b) Findings

1. `rota/roles/api.py:8401`, low, CONFIRMED (outside). `_LINE_REF` has `re.I`, and the `_ref_lines` token pattern has no flag. "lines 2 Through 7" reads {2, 7}, and "Lines 2 To 7" reads the same. The probe showed ({2, 7}, set()). No recorded principal reply holds the shape. Fix: pass `re.I` to the `re.findall` in `_ref_lines`.
2. `rota/roles/api.py:8381`, low, CONFIRMED (outside, older than the pass). "line 3 through line 5 is wrong" reads faulted {5}. Line 3 gets no cue, and line 4 is lost. The "to" form fails the same way. Fix: admit an optional `lines? ` after the range word in `_LINE_REF`.
3. `rota/roles/api.py:5087`, low, PLAUSIBLE (outside). `_WORDS_FAULT` reads "to" as a range word and not "through" or "-". The probe showed "Lines 2 through 7 are wrong" gives False and "Lines 2 to 7 are wrong" gives True. At api.py:5458 an answer that also names a check then tells the Architect "The criterion stands". The route is wrong only when the words fault a check too. Fix: write `(?:,| and| to| through|-)` in the `_WORDS_FAULT` range group.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4492a9c1-4457-41ce-a46b-42b300ec21c1/scratchpad/f256/r1/`.

- `shapes.py`: loads the old `_LINE_REF`, `_ref_lines` and `_line_reading` from `git show 4fe07692:rota/roles/api.py` into a copy of the module namespace. It runs the shapes old and new, and the test's two inputs on the old reader.
- `count2.py`: runs the old and the new reader on every principal message of the 72 night databases with `?mode=ro`, and lists every change.
- A `python -c` read of m92, m96 and m214 from the night databases, read-only, and of the `messages` columns.
- A `python -c` check of `_WORDS_FAULT` on three range shapes.
- `pytest tests/rota/test_frame234_verdict_lines.py -q` in the worktree: 48 passed in 5.71s.

No git command changed a tree or the index. The gate did not run, because no point needs it.

## (d) Usage

Harness count: about 47k tokens in total (15,000,000 at the start, about 14,953,000 at the end). The harness does not split input and output for this agent. The cap was 40k. Sub-agents: none.
