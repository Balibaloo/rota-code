# F37 pass 2 review: ce3ecce5 and 91dd9119 on f37b, against 442e32b0

Verdict: NOT READY. One high finding and one high plausible finding stand. The prompt says "several" lines, and the door refuses three docstring lines with "Copy the one". Every list route that follows the advice of the hold costs a second hold.

## (a) Verdict on each point

1. Only the four named places change. The diff has four files, not five. The hold text grows by one sentence for each one-line criterion. See finding 4.
2. Partly kept. A list of two lines lands. A list of three or more lines lands only as one branching statement. "Several" is not kept. See findings 1 and 3.
3. Three calls land the s238 shape with a two-line list. The second hold asks "or the opposite?" again on the list that the hold asked for. See finding 2.
4. Both plants go red. The door plant reds 6 tests. The prompt plant reds 2 tests.
5. The two prompt sentences pass. `_HOLD_MORE` holds 23 words in one instruction, over the 20-word limit for an instruction.
6. No foreign hunk. No CR byte in the four files at the parent, at the head or in the work tree.
7. Seven cases stamp the new sentence. The list of the builder holds one wrong case and misses one. See finding 5.

## (b) Findings

1. `rota/roles/prompts/critic/review.md:11`, `answer.md:22`, `rota/roles/api.py:15995`. Severity high. CONFIRMED.
   The prompt says "When several added lines meet it together, copy them as a list". The door admits at most `_LINE_PARTS_MAX` = 2 lines, unless the lines are one `if`, `try`, `match` or conditional expression.
   Probe D sent c_2 as the three lines of the example block: `Example:`, the `>>>` line and `"c.txt"`.
   The door refused it with "they are not one statement that a pass can name ... Copy the one that does what the criterion says."
   So a docstring example of three lines gets the "one line" reading back from the door. That reading is the s238 wall.
   Fix: name the cap in both prompt sentences and in `_HOLD_MORE` ("two added lines"), or let a criterion that asks for docs name more docstring lines.

2. `rota/roles/api.py:16039-16051`. Severity high. PLAUSIBLE.
   The one-line hold now tells the seat to send a list. The door then reads that list as a moved line and holds it again.
   Probe A: call 1 is held, call 2 with the list is held, call 3 lands. Probe C, with the list from the start, lands on call 2.
   The second hold repeats "Do those lines do what the criterion says, or the opposite?" and names "your own fail" again.
   Night 161 measured the hold turning 2 right passes of 5 into wrong fails. Each extra hold on a right pass is one more such chance.
   Fix: when the moved value holds the held line and adds lines, read it as the answer to the hold and let the pass land.

3. `rota/roles/api.py:15884-15886`. Severity low. CONFIRMED by reading.
   The refusal for three or more lines with no behaviour still says "A pass names one added line per criterion."
   That sentence is the rule that s238 wrote down before it failed c_2. The new prompt sentence says the opposite.
   Fix: say "A pass names, for each criterion, one added line or two lines that meet it together."

4. `rota/roles/api.py:16057`. Severity low. CONFIRMED.
   `_HOLD_MORE` follows every one-line criterion. Probe A call 1 shows it three times in one hold, once for c_1, c_2 and c_3.
   c_1 and c_3 had a right line. The repeated sentence can move them to lists, and a moved criterion is held again.
   Fix: say `_HOLD_MORE` once, after the last criterion, before `_HOLD_SAY`.

5. The stale list in section (b) of the builder report. Severity low. CONFIRMED.
   `L1-CR-dismiss-a-finding-on-a-falsified-constraint` is mode `finding_review`. Its composed prompt does not hold the new sentence.
   `L3-a-failed-verdict-turns-into-a-fix` is a chain with a Critic `review` leg. Its composed prompt holds the new sentence, and the list misses it.
   The seven stale cases: `ACT-CR-quote-the-tests-code`, `L1-CR-finish-the-review-with-the-answer-in-hand`, `L1-CR-pass-a-conforming-diff`, `L1-CR-fail-names-its-criterion`, `L1-CR-a-test-that-encodes-nothing-is-a-challenge`, `L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist`, `L3-a-failed-verdict-turns-into-a-fix`.
   Fix: re-record these seven cases by id, and drop the `finding_review` case from the list.

6. Outside the points. `rota/roles/api.py:15310`. Severity low. CONFIRMED by reading.
   The `_line_parts` docstring says "The door refuses more than `_LINE_PARTS_MAX` parts." Since F37 pass 1, the door admits a branching statement of more parts.
   Fix: say that the door refuses more parts unless they are one branching statement.

7. Outside the points. No gate ran at 91dd9119. Severity low. CONFIRMED from the builder report.
   I ran the five test files that read the hold text: 200 passed at 91dd9119. The two extra readers are `test_arc_seam.py` and `test_frame306_pass_skips_retired.py`.
   Fix: run the gate once at 91dd9119 before the merge.

### Point 3: the full hold text on each call (probe A)

The seat sees each text after the prefix `HELD verdicts.emit: `.

Call 1, the turn-1 shape, the same `>>>` line for c_1, c_2 and c_3:

> before the pass lands, answer for c_1, c_2 and c_3. Criterion c_1 says: "The docstring of format_filename must include an example demonstrating that when shorten=True, a path like "a/b/c.txt" is displayed as "c.txt".". Your line holds '>>> format_filename("a/b/c.txt", shorten=True)'. Does that line do what the criterion says, or the opposite? If the criterion needs more than that line, send the pass again with the added lines that meet it together, as a list. Criterion c_2 says: "The example in the docstring must explicitly show the input path and the resulting shortened output to verify the behavior.". Your line holds '>>> format_filename("a/b/c.txt", shorten=True)'. Does that line do what the criterion says, or the opposite? If the criterion needs more than that line, send the pass again with the added lines that meet it together, as a list. Criterion c_3 says: "The docstring must include an example showing that when shorten=True, a path like "a/b/c.txt" is displayed as "c.txt".". Your line holds '>>> format_filename("a/b/c.txt", shorten=True)'. Does that line do what the criterion says, or the opposite? If the criterion needs more than that line, send the pass again with the added lines that meet it together, as a list. Say which in your own words, and in the same reply send the pass again or your own fail on the criterion.

Call 2, the turn-3 shape with c_2 as a list of the `>>>` line and the `"c.txt"` line:

> before the pass lands, answer for c_2. The criterion says: "The example in the docstring must explicitly show the input path and the resulting shortened output to verify the behavior.". Your lines hold '>>> format_filename("a/b/c.txt", shorten=True)', then '"c.txt"'. Do those lines do what the criterion says, or the opposite? Say which in your own words, and in the same reply send the pass again or your own fail on the criterion.

Call 3, the same pass: LANDED {'id': 'critic:b1:abc123', 'result': 'pass'}

Probe B replays s238 as recorded, with the `"c.txt"` line alone on call 2. Call 2 then shows the one-line form for c_2 with `_HOLD_MORE`. Call 3 lands with any lines.

### Point 4: the plants

- The door plant removes `_HOLD_MORE` from the one-line form of `holds()`. Six tests go red, and `test_the_one_line_hold_names_the_list_form` is one of them.
- The prompt plant removes the new sentence from both prompt files when `Path.read_text` reads them. Both ids of `test_each_critic_prompt_names_the_list_form` go red.
- `test_prompts.py` and `test_verdict_lines.py` stay green under both plants. Only the new tests pin the prompt sentence.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/2568e043-732b-4ab6-9d66-bc0069e83123/scratchpad/f37r2/`. Each probe ran from the worktree root.

- `probe_hold.py` builds the s238 diff and its three criteria in a temporary git repository. It calls `verdicts.emit` through the sandbox for the sequences A, B and C. It prints `asks_for_docs`, which is True for all three criteria. The output is in `probe_hold.out`.
- `probe_three.py` runs sequence D, the three-line example block for c_2.
- `plant_door.py` is a pytest plugin. It runs `_first_pass_hold` again without `_HOLD_MORE`. It ran on `test_frame201_first_pass_hold.py`, `test_prompts.py` and `test_verdict_lines.py`.
- `plant_prompt.py` is a pytest plugin. It removes the sentence from the two prompt files when they are read. It ran on the same three files.
- `probe_stale.py` composes `fixtures.instructions_for` for every `l*.yaml` and `g*.yaml` case and finds the new sentence.
- The clean run of the three files and `test_arc_seam.py` gave 188 passed. `test_frame306_pass_skips_retired.py` and `test_arc_seam.py` gave 12 passed.
- The s238 turns come from `D:/repos/rota/.rota/clickI_night172.db`, opened read-only, the tables `turns` and `tool_calls`.

## (d) Usage

Input is about 85k tokens and output is about 16k tokens, about 101k in total. These numbers are estimates from the session counter. The use is over the 50k cap.

# Pass 3 review: 3b26e66e on f37b, against 91dd9119

Verdict: READY. The two high findings of pass 2 are closed. Four low findings stay, and none of them blocks the merge.

## (a) Verdict on each check

1. The three-line example for c_2, sent as a list after the hold, lands on call 2. The kept held line means the hold does not fire again (probe E).
2. The s238 shape lands on call 2 when the list keeps the held line (probe F). When the seat drops the held line first, as s238 did, the pass lands on call 3 (probe F2).
3. A docstring run names one criterion only. The same three-line run for c_1 and c_2 is refused (probe H).
4. Added code lines keep the old cap. Three code lines that are not a branch are refused for a criterion that asks for docs and for a behaviour criterion (probes I1 and I2).
5. A list that drops the held line is still held. The second hold uses the many-line form, and call 3 lands (probe G).
6. The no-behaviour refusal and the `_line_parts` docstring name the unit rule. Two other refusals do not name it. See finding P3-1.
7. `_HOLD_MORE` has 18 words. It occurs once in a hold for four criteria, after the last criterion and before `_HOLD_SAY`.
8. The diff adds one new behaviour beyond these checks: the lines that a kept-line list adds are never asked about. See finding P3-2. No CR byte is in the three files at 3b26e66e.

## (b) Findings

P3-1. `rota/roles/api.py` at the overlap refusal and the last refusal of the block loop in `_pass_lines_check`. Severity low. CONFIRMED.
   Probe J sent three docstring lines that are not adjacent for c_2, a criterion that asks for docs. The refusal says only that "A value of several lines lands as one `if`, `try`, `match` or conditional expression". It does not name the docstring run, and it says "Copy the one".
   Probe H got the overlap refusal for a docstring run. That refusal says "One statement of several lines" and lists the code lines for a docs criterion.
   Fix: name "or a run of adjacent docstring lines, for a criterion that asks for documentation" in the last refusal, and say "unit" in place of "statement" in the overlap refusal.

P3-2. `rota/roles/api.py`, `moved_from` in `_first_pass_hold`. Severity low. PLAUSIBLE.
   A list that keeps every held line and adds lines lands without a hold. Probe E landed two new lines, `Example:` and `"c.txt"`, with no question about them.
   Frame 201 pass 3b held a moved line once more so that the door asks about every new line. A seat that keeps a wrong line and adds another one now gets no second question.
   Fix: none needed for s238. If wrong passes rise on the next night, hold the added lines only, with no `_HOLD_MORE`.

P3-3. `rota/roles/prompts/critic/review.md:11` and `answer.md:22`. Severity low. CONFIRMED by probes I1 and I2.
   The prompts still say "When several added lines meet it together, copy them as a list". Three added code lines that are not one branch are refused with "Copy the one that does what the criterion says".
   The s238 class, a docstring example, is now kept. A code criterion is not kept.
   Fix: say "several adjacent docstring lines, or one `if`, `try` or `match` statement" in both prompts.

P3-4. `_doc_run_of`. Severity low. PLAUSIBLE.
   A docstring run has no length cap. A branch has `_BRANCH_BODY_MAX`. A criterion that asks for docs can name a whole added docstring, and that docstring can hold lines that do not meet the criterion.
   Fix: none now. Count the length of doc-run values on the next night before a cap is added.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/2568e043-732b-4ab6-9d66-bc0069e83123/scratchpad/f37r2/probe_p3.py` reuses the setup of `probe_hold.py`. It adds three code lines to the diff and a behaviour criterion c_4. It runs the sequences E to J through the sandbox. The output is in `probe_p3.out` in the same directory.
- I ran `test_frame201_first_pass_hold.py`, `test_verdict_lines.py`, `test_prompts.py`, `test_arc_seam.py` and `test_frame306_pass_skips_retired.py` at 3b26e66e: 199 passed. No gate ran.

### The hold text a seat sees on call 1 of probes E, F, F2 and G

The seat sees the text after the prefix `HELD verdicts.emit: `.

> before the pass lands, answer for c_1, c_2, c_3 and c_4. Criterion c_1 says: "The docstring of format_filename must include an example demonstrating that when shorten=True, a path like "a/b/c.txt" is displayed as "c.txt".". Your line holds '>>> format_filename("a/b/c.txt", shorten=True)'. Does that line do what the criterion says, or the opposite? Criterion c_2 says: "The example in the docstring must explicitly show the input path and the resulting shortened output to verify the behavior.". Your line holds '>>> format_filename("a/b/c.txt", shorten=True)'. Does that line do what the criterion says, or the opposite? Criterion c_3 says: "The docstring must include an example showing that when shorten=True, a path like "a/b/c.txt" is displayed as "c.txt".". Your line holds '>>> format_filename("a/b/c.txt", shorten=True)'. Does that line do what the criterion says, or the opposite? Criterion c_4 says: "format_filename strips the name and lowers its case when shorten=True.". Your line holds 'name = filename.strip()'. Does that line do what the criterion says, or the opposite? If a criterion needs more than one line, send the pass again with its lines as a list. Say which in your own words, and in the same reply send the pass again or your own fail on the criterion.

Call 2 of probe F2, after the output line alone:

> before the pass lands, answer for c_2. The criterion says: "The example in the docstring must explicitly show the input path and the resulting shortened output to verify the behavior.". Your line holds '"c.txt"'. Does that line do what the criterion says, or the opposite? If a criterion needs more than one line, send the pass again with its lines as a list. Say which in your own words, and in the same reply send the pass again or your own fail on the criterion.

Call 2 of probe G, after a list that drops the held line:

> before the pass lands, answer for c_2. The criterion says: "The example in the docstring must explicitly show the input path and the resulting shortened output to verify the behavior.". Your lines hold 'Example:', then '"c.txt"'. Do those lines do what the criterion says, or the opposite? Say which in your own words, and in the same reply send the pass again or your own fail on the criterion.

## (d) Usage

Pass 3 used about 20k tokens of input and about 7k tokens of output, about 27k in total. These numbers are estimates from the session counter.
