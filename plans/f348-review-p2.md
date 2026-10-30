# Review of frame 348, commits 54aa7922 and a8ff05d4 on rota/foundation, pass 2

Verdict: not ready to close. Pass 3 lands the n175 case, and the suite holds. Two high findings break law 6. A second approve now lands on a line his earlier answer calls wrong. An earlier fault in a clause with "is unclear" or "tell me where" binds nothing. Counts: 2 high, 3 low.

Worktree: C:/Users/roman/rota_f348b at 3b15c467, removed after the review. A second worktree at a4a2f1aa ran one test, and was removed.

## (a) Verdicts on the points

1. Partly fixed. High 2 and low 3 and low 4 of p1 hold fixed. High 1 holds only in part (finding 1 below).
   "I looked at line 2 again." and "Line 2, line 3 and line 4 are about the tip." now keep the earlier fault, and approve is refused.
   "Line 2 is fine now." as the reply lands approve, which is correct.
   "Line 2 was wrong before, now it is fine." is refused once. The menu then offers add and other only, and `other now it is fine.` lands c1 contest.
   An earlier "Line 2 is fine." with `{"c1": "approve"}` lands approve on all six refs. The rows carry the reply's words, from m78.
   The refusal menu now reads "takes add <quote>; other <quote>", with no approve.
2. All matches are requests for facts. The scan read 305 principal texts: 69 in l3_rulings.yaml and l1_landing.yaml, 236 on nights 170 to 175. It found 6 matches:
   - L3R-n175-m11-m14 m14, "Please tell me what the claim says".
   - night172 m14, "Please tell me what the claim about arguments said and why".
   - night174 m14, "line 3 is unclear, so which claim about an argument could".
   - night174 m25, "Line 3 is unclear to me, so what does".
   - night175 m25, "Line 3 is unclear to me, so please say what it means" (two matches).
   No match in the corpus is a statement. Constructed statements match (finding 3).
3. Lines 2 and 6 stay bound. The strip loop removes them from the ask clause before `ask_lines` is built, so `ask_lines` is {1, 3, 4, 5}. On M14 the approve of line 1 gets the question refusal, and lines 2 and 6 get the approve refusal. `ask=` lands. On the next reply, "Line 3 is fine.", with m12 and m14 as earlier answers, lines 2 and 6 refuse approve again. The ask clause clears nothing, because the earlier loop skips a question clause.
4. Three hunks reach past the claims. The `span_of` order now puts the reply's words first on every line that no earlier answer faults. The second `_is_question` caller, the earlier-answer loop at api.py 14258, takes the wider question test (finding 2). The case L3R-n175-m11-m14 drops its checks of lines 2, 3 and 6, and now expects only an ask.
5. `test_frame337_earlier_answers.py` and `test_r1_menu_form.py`: 49 passed. L3R replay with ROTA_DEV_DB on a scratchpad copy of cassettes.db: 2 failed, 23 passed. The two reds are L3R-n171-m27-m28 and L3R-n172-m76-m77, the same as p1. L3R-n175-m11-m14 now passes, so the 24 old cases hold at 22. The 12 landing L1 cases were not run.

## (b) Findings

1. `rota/roles/api.py:14482-14490`, the refusal that fires once. Severity high. CONFIRMED.
   The once rule lets a repeat approve land on a line that his earlier answer correctly calls wrong.
   Probe: earlier "Line 2 is wrong.", reply "I had another look at the page.", the same all-approve call twice. The first call was refused. The second landed c1 approve.
   A small model repeats a refused call often, so the guard of m75 now costs one turn and protects nothing.
   For a misread fault, the refusal menu still steers the seat to `other`, and that lands a contest against his words.
   Fix: keep the refusal on every call, and fix the misread in `_line_reading` for "was wrong before, now it is fine", or route that line to ask.
2. `rota/roles/api.py:14258`, the earlier-answer loop skips a clause that `_is_question` matches. Severity high. CONFIRMED.
   Pass 3 widens the test, so an earlier fault now binds nothing when its clause also asks for facts.
   Probe: earlier "Line 2 is wrong and line 6 is unclear.", silent reply, all approve. The call landed c1 approve at once.
   The same held for "Line 2 is wrong, tell me where it came from.". The control "Line 2 is wrong and line 6 is odd." was refused.
   The skip existed before for a question mark. Pass 3 adds "is unclear" and the request verbs to it. No recorded case renders the path.
   Fix: in the earlier loop, skip only the lines that the question names, and bind a line that `_line_reading` faults in the same clause.
3. `rota/roles/api.py:14099-14102`, `_ASKS_FOR_FACTS`. Severity low. CONFIRMED on constructed text, no corpus hit.
   The pattern matches statements with show, explain or say before a wh-word.
   Probe: "Lines 3 and 4 show how the parser works, so they are fine.", "The notes explain why the tool fails, and that is right." and "Nobody can say where it came from, so drop line 6." all read True.
   The cost is one extra ask to him, not a wrong ruling.
   Fix: require an imperative or a request frame before the verb: sentence start, "please", "can you", "could you".
4. `rota/roles/api.py:14166-14169`, the comment "The mark is read as a character only". Severity low. CONFIRMED by reading.
   The comment is false since pass 3, because `_is_question` also reads words.
   Fix: change the comment to name `_ASKS_FOR_FACTS`.
5. `tests/rota/cases/l3_rulings.yaml:6049-6055`, the case L3R-n175-m11-m14. Severity low. CONFIRMED by reading. Outside the points.
   The case expected contest on lines 2 and 6. It now expects only an ask and no ruling.
   No case now checks that a reply which rules nothing keeps m12's faults on lines 2 and 6.
   Fix: add `expect_lines` for lines 2 and 6 to a second case whose reply is silent, from the same night.

Outside the points: `test_f345_p5_landing.py` has one red, L1-LI-remove-lines-on-a-criteria-page-is-a-drop-9-lines0. The same red shows at a4a2f1aa, so frame 348 did not cause it.

## (c) Probes

All probes ran from the worktree root with `ROTA_MODEL=qwen3:8b`, and were deleted after the run.

- `scratchpad/p348_scan.py`: `_ASKS_FOR_FACTS.finditer` over every principal `body_text` in l3_rulings.yaml and l1_landing.yaml, and over `messages` rows from the principal in the six night databases. The databases opened with `immutable=1`, so nothing wrote to them.
- A `python -c` call: `_is_question` on 8 constructed phrases.
- `tests/rota/test_probe348p2.py`, 11 tests on the `_page6` and `_landing` fixtures: the p1 phrases, the fault approved twice, M12 then M14 with four calls, the next reply after M14, and earlier faults next to "is unclear", "odd" and "tell me where".
- `test_frame337_earlier_answers.py` and `test_r1_menu_form.py` as is.
- `test_l3_rulings.py` with `ROTA_DEV_DB` on `scratchpad/f348r2_cass.db`, a copy of `tests/rota/cassettes.db`.
- `test_f345_p5_landing.py` at 3b15c467, and at a4a2f1aa in a temporary worktree.

The scratchpad is C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/a9a43280-d634-4af9-9ae0-e50791297894/scratchpad.

## (d) Usage

Input tokens: about 40k. Output tokens: about 9k. Total: about 49k. The cap of 40k was exceeded by the replay runs and the base check.
