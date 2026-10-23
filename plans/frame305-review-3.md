# Frame 305, review 3: pass 2b at 01cc956a

Reviewer on Opus, read-only. Worktree `C:/Users/roman/rota_r305` at
01cc956a, parent e76212ee. Verdict: do not accept for the branch yet. Pass
2b fixes the five wrong readings and the m46 door of review 2. It makes
three new wrong readings that are high for their night, and the approval
frame lets an imperative inside an approving reply fault nothing.

## (a) The claim, point by point

1. Re-judge: CONFIRMED 165 changed against e630519c and 12 against e76212ee. My counts are 155 right, 4 wrong and 6 doubtful. All four highs of review 2 now read right.
2. The four wrong ones: CONFIRMED wrong. Three are high for their night: night 150 m66, night 153 m60 and night 158 m148.
3. The door: CONFIRMED. `_line_refusal` refuses the m46 and m64 contests, and three right line-1 contests still land.
4. The diff: CONFIRMED. All hunks are in the line reader and in the request door. The frame's tests pass.

## (b) Findings

### Point 1: the 165 re-judged

`count3.py` reproduces 165 changed against e630519c and 12 against
e76212ee. I read the 12 and kept my review 2 reading of the other 153.

- Right: 155.
- Wrong: 4.
- Doubtful: 6.

Review 2's highs, each now right:

- Night 140 m6: faulted {}, matched {}. Right.
- Night 144 m112: faulted {10}, matched {1}. Right.
- Night 150 m114, m123 and m139: faulted {}, matched {}. Right.

The other changes of the 12:

- Night 154 m22: line 3 leaves the matched set and stays faulted. Right.
- Night 157 m162: line 3 leaves the matched set and stays faulted. Right.
- Night 140 m142: line 1 leaves the matched set. The fault on line 3 is right, so the entry stays right. The match is lost, and no door needs it.
- Night 157 m22: line 1 leaves the matched set, so the entry equals e630519c and leaves the 165.

The wrong ones, with the right set:

1. Night 150 m66, "line 7 is not a real problem, since the helper is missing only because it has not been built yet". New: faulted {3, 5, 7, 10, 12}, line 7 on "is". Right: faulted {3, 5, 10, 12}, matched {7, 9}.
2. Night 153 m60, "ok, that looks right. Line 1 now says the flag defaults to False, so please go ahead and build it." New: faulted {1}, cue "says". Right: matched {1}.
3. Night 158 m148, "Ok, every line now says what I asked for, and line 3 is fixed. Please keep going and finish the change, and don't drop it." New: faulted {3}, cue "is fixed". Right: matched {3}, or both sets empty.
4. Night 155 m_shift_echo_json_tests_m_p2, "This page also shows no line 2, so I cannot say what to do with it." New: faulted {2}. Right: faulted {}. This one is unchanged since pass 2.

The doubtful ones are review 2's list less night 154 m22: night 142 m86, 143 m272, 144 m94, 146 m250, 150 m_shift_confirm_default_on_eof_m_p3 and 156 m_shift_echo_json_m_p2.

### Point 2: the four wrong ones judged

Three of the four come from the removals and the narrowing that review 2
asked for. Review 2 named four phrases as fits. Its fix was to make the
shapes more general, not to remove them. The removals traded a fit for a
wrong reading of the same recorded sentence.

1. `rota/roles/api.py:9682`, `_AGREEMENT`, night 150 m66. High for the night, high for the frame. CONFIRMED: `count3.py` and `doors3.py` fault line 7, and "Line 7 is not a problem." faults {7}. He calls the line no problem, so a fault there sends his words against a line he accepts. The brief's rule 1 already names "a negated fault" as an agreement. Fix: add "(is|are) not an? (real )?(problem|issue)" back as the negated fault of rule 1, together with "is not wrong".
2. `rota/roles/api.py:9699` to 9701, `_AGREEMENT`, night 153 m60. High for the night, high for the frame. CONFIRMED by `count3.py`. "now says the flag defaults to False" reports what the line says, and the reply opens with "that looks right". The narrowing that fixed "now has a typo" also caught "now says". Fix: let "now says", "now covers" and "already says" take any object, keep the no-object rule for "has" and "have", and let `_instruction_cue` fault "now says the wrong thing" on its strong word.
3. `rota/roles/api.py:9682`, `_AGREEMENT`, night 158 m148. High for the night, low for the frame. CONFIRMED: "Line 3 is now fixed." faults {3}. Fix: read "(is|are) (now )?fixed" as a negated fault of rule 1, because the line had a fault and he says it is gone.
4. `rota/roles/api.py:10086` to 10125, `_line_cues`, night 155's shift page. Low for the night and the frame. PLAUSIBLE: the page has no line 2, so no door can act on the fault. Fix: let a reference with "cannot say" or "can't tell" and no instruction take no direction.

### Point 3: the request door

`doors3.py` runs `_line_refusal` with a line-1 contest on a page of three lines, with line 1 the request.

- m46: faulted {}, matched {2, 3}. Refusal: "The words do not fault line 1, and they ask to keep the change. Approve line 1."
- m64: the same reading and the same refusal.
- "Line 1 is wrong: the helper should print compact JSON with no spaces, not pretty JSON." faults {1}, and the refusal is None. The contest lands.
- "Please don't drop this change. Line 1 should say the helper prints compact JSON on one line." faults {1}, and the refusal is None. The keep-change words do not block a contest that the words support.
- Night 157 m22's shape, "Line 1 names the wrong change: ... so replace it", faults {1}, and the contest lands.

The new check reads `_KEEP_CHANGE` only when no line is faulted. That agrees with the check below it, which already treats keep-change words as no correction of the request. No finding.

### Point 4: the diff

`git diff e76212ee 01cc956a --stat` shows three files: `rota/roles/api.py`
(+148 lines in total), `tests/rota/test_frame234_verdict_lines.py` and
`tests/rota/test_frame305_line_reader.py`. Each api.py hunk is in the line
reader, lines 9687 to 10143, or in the request door at line 10227.

- The xfail is removed. The m46 test and the new m64 test expect the new refusal text. That is his meaning.
- One pass 2 expectation changed. "Please remove it, since line 1 now says the flag is off by default." now gives (set(), set()). The test now holds the lost match of night 140 m142. Finding 2 above restores it.
- The ten cases of `test_pass_2b_readings` hold review 2's right sets.

Tests at 01cc956a, with `pytest -n 0`: `test_frame305_line_reader.py`,
`test_frame234_verdict_lines.py`, `test_frame250_verdict_faults.py`,
`test_frame255_files_correction.py` and `test_runner.py` give 289 passed and
5 xfailed.

### Findings outside the points

5. Outside. `rota/roles/api.py:10114` to 10121, the `approves` branch of `_line_cues`. High for the frame, low for the night. CONFIRMED with `doors3.py`. In a reply that approves the page, a head verb faults only when it is a strong word of the old list. "Ok, I approve the page. Please fix line 3." faults nothing. "Line 3 lists the pager tests. Trim it, and then go ahead." faults nothing. So the old leak comes back in each approving reply, and 53 of the 803 replies match `_APPROVES`. No recorded reply of the 53 loses a right fault today. The implementer names this in doubt 2. Fix: keep a head verb that leads its clause after "please" or a break, and remove the direction only from the describing verb after the reference.
6. Outside. `rota/roles/api.py:9772`, `_APPROVES`. Low for the night and the frame. PLAUSIBLE: the frame is set for the whole reply by one sentence anywhere in it. A reply that ends "so go ahead." after a correction of a line loses the describing verbs of every sentence. Fix: apply the frame to the sentence that approves and to the sentences after it only.

## (c) Probes

All probes are in
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b85289fd-418f-43a1-a641-15dad2620cfa/scratchpad/r305b/`.

- `b_api.py`: `git show` of `rota/roles/api.py` at 01cc956a. It is byte-equal to the worktree file.
- `count3.py`: runs the readers of e630519c, e76212ee and 01cc956a over the 803 messages of `rows.json`. It prints 165 and 12 changed, the 12 entries, and the 53 approving replies.
- `doors3.py`: imports the worktree api. It runs `_line_refusal` on m46, m64 and three right line-1 contests. It reads eight sentences that no night recorded against the approval frame and the agreement shapes.
- The test run of point 4, from the worktree root.

## (d) Usage

No exact meter. About 30k input tokens and 7k output tokens for this review, about 37k in total. The cap was 30k.
