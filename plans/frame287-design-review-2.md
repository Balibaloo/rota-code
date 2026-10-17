# Frame 287, design review 2

Meta workflow. Read-only review on Opus, 2026-10-17, of revision 2 of `plans/frame287-design.md`. The worktree was `D:/repos/rota` at HEAD 71cb13e0. The reviewer read review 1, revision 2, the composition page, the first section of `CLAUDE.md`, and the parts of pages A to D that a point needed. The reviewer edited no tracked file and ran no gate.

## (a) The verdict on each point

1. Review 1's ten high findings: eight hold. F6 does not hold (finding 1). F7 is named, but the amendment narrows the 2026-10-03 read (finding 4).
2. New contradictions: no new contradiction of the composition. Four ruled marks in the body still stretch page A (finding 10). The grep claims of cause 1 hold for frame 114 and not for frame 115 (finding 2).
3. The prototype's check: the count is 7, not 9. The seven answers are listed below (finding 3).
4. The order of frames: frame 3 points the brief at tools that frame 4 builds. Frame 5 rebuilds four parts of frames 2 and 4 (finding 5).
5. Section 8: the three recommended answers do not contradict page A. A fourth item is owed, the harness setting of section 5 (finding 7).
6. Readability: the record mostly stands alone. Six places lean on revision 1 or on page B's codes with no gloss (finding 13).

### Point 1, finding by finding

| Review 1 | Section 11 says | In the body? | Holds? |
|---|---|---|---|
| F1 `Means:` | dropped, section 6 | Yes, lines 276-278 | Yes |
| F2 one writer | one derived file, section 4 | Yes, lines 202-208, 213 | Yes. A low new defect: the derived file is a cache (finding 6) |
| F3 the print rules | never refuses, sections 3 and 6 | Yes, lines 148-151, 181, 293-295 | Yes |
| F4 cause 2 refuted | cause 1 rewritten, section 2 | Yes, lines 89-107 | For frame 114 only (finding 2) |
| F5 15 of 19 | distinct answers under the cap, section 9 | Yes, line 372 | The shape holds. The count is wrong (finding 3) |
| F6 cycle rules | stay, sections 3 and 5 | Partly, lines 195-198, 249, 322-325 | No. Rules that no moment prints still move (finding 1) |
| F7 two rulings | named as amended, sections 3 and 7 | Yes, lines 176-180, 311-314 | Named. The amendment opens a gap on a miss (finding 4) |
| F8 second question | three items, section 8 | Yes, lines 336-361 | Yes. A fourth is owed (finding 7) |
| F9 the view | deferred to frame 5, sections 5 and 9 | Yes, lines 256-262, 376 | Yes. The deferral has a rebuild cost (finding 5) |
| F10 future | `wake next` prints four things | Yes, lines 279-285 | Yes |

### Point 3, the R rows and their distinct answers

Page C classes 19 rows as R: 6, 12, 15, 26, 27, 28, 30, 59, 60, 61, 62, 64, 87, 89, 90, 99, 100, 102, 103. Four rows have an answer that loads every turn, so frame 1 excludes them: 12 and 62 (`CLAUDE.md`), 87 (the interview rule in `CLAUDE.md`), 100 ("Bulk reading goes to agents" in `CLAUDE.md`). The remaining 15 rows hold seven distinct answers.

1. Law 3, the Terminologist writes the criteria (`LAWS.md:121-147`): row 6.
2. Law 2, conclusions travel and reasoning stays home (`LAWS.md:112-119`): rows 15, 28, 30.
3. Law 12, the touch route cf067ce4, and the composition line "A prediction never blocks": rows 26, 27, 99, 103.
4. Roman's notes answers of rows 53 and 55, 10-11 15:43 and 15:59, and `plans/frame204-design.md`: rows 59, 60, 61.
5. `rota/ROLES.md:150-170`, the Developer never builds what nobody asked for: row 64.
6. `plans/frame244-interview.md`, committed 6d989149: rows 89, 90.
7. Roman's 10-04 14:34 answer of row 30, with the two-things rule of 2026-10-04 14:52: row 102.

Answer 7 is borderline. Half of it is in `CLAUDE.md` and loads every turn. With row 102 excluded the count is 6. Answers 4 and 7 live in a transcript, so the prototype finds them only if it reads the extraction of his words.

## (b) Findings

1. **Rules that no moment prints still leave the brief.** Design line 249 and line 323. High. CONFIRMED by the text and page B. Line 249 moves "the standby wake, the hand-off at 300k and 400k, the night stop, the sprint boundary, the escalation route" to `plans/method/`. The six moments are take, push, design, ask, night and close. No moment fires at 300k or 400k, at a standby wake, or at a sprint boundary. The table of section 3 has no row that prints a method file at all. Page B lines 41-43 mark C2 and C4 as rules whose failure recurred. Cause 5 of the design says a prose rule held away from its moment fails, and the move puts these rules further away. Fix: move a rule only when a row of section 3 prints its method file, and keep C2 to C4, the escalation route and the standby wake in the brief.

2. **Cause 1 is shown for frame 114 and not for frame 115.** Design lines 96-99. High. CONFIRMED by grep at 71cb13e0. `grep -ni permission rota/LAWS.md` gives lines 339 and 342, law 12. `grep -ni reasoning` gives lines 112, 115 and 303, so law 2's title matches. But the questions of rows 15, 28 and 30 do not hold the word "reasoning". Their words are "answer", "prose", "words" and "decision record". `grep -ci prose rota/LAWS.md` gives 0. `grep -ni answer` gives 12 lines, and none is in law 2, lines 112-119. Frame 1 takes the keys verbatim from each question, so law 2 is a likely miss. Cause 2 is then still live for frame 115. Fix: write that cause 1 holds for frame 114, and that frame 115 is a probable cause 2 case that frame 1 decides.

3. **The prototype's count is 7, not 9.** Design line 372 and line 386. Low. CONFIRMED from page C's table: see point 3. Review 1's "about 9" is the source, and revision 2 copied it. Fix: write "7 distinct answers, listed in review 2", and name row 102 as borderline.

4. **The amended agent read has nothing to read on a miss.** Design lines 176-181 and 311-314. High. PLAUSIBLE by the text. The 2026-10-03 agent now "reads the print's hits instead of the whole record set". A cause 2 question returns no hit, so the agent reads nothing and the question goes with "records read: none". That is the frame 114 path of 10-04, which the 2026-10-03 ruling exists to close. The 3k cap can also cut the hit that answers. Fix: the agent reads the hits first, and runs the full 10-03 read when the print has no hit or reaches its cap.

5. **Frame 3 points at frame 4's tools, and frame 5 rebuilds frames 2 and 4.** Design lines 315-317, 374-380. Low. CONFIRMED by the text. Frame 3 writes brief items 5 and 6, which point at `wake night` and `wake close`, and frame 4 builds them. Line 379 says frame 3 waits on frames 1 and 2 only. Frame 5 moves the stack to `plans/frames/`. Then the take parser, the status writer, `wake close` and the index's `### n.` parse must change. Frame 5 also edits `CLAUDE.md` again ("stack rule 5 reads the view"), which needs a second C73 check. Section 8 item 3 says "after frame 4", while the frame 3 row sends the diff in frame 3. Fix: run frame 4 before frame 3, and put stack access in one reader and writer module in frame 2.

6. **The derived file is a cache, against the map precedent it cites.** Design lines 160, 192 and 202-204. Low. CONFIRMED by the text. Line 202 names `plans/index.tsv`, "rebuilt on demand ... with no cache". Lines 160 and 192 have the close "rebuild" the index, so it persists between calls. A file in `plans/` drifts from an unstaged edit, which is review 1 finding 12. Fix: compute the hits at each call and write no file, or state that the file is a cache and rebuild it at every call.

7. **A fourth item for Roman is owed.** Design line 253 and section 8. Low. CONFIRMED by the text. Line 253 removes five tool schemas from the build session and calls it "a harness setting Roman holds, item for him". Section 8 lists three items and omits it. Fix: add item 4, the tool schemas, with a recommended answer.

8. **The scratchpad is no home for his words.** Design lines 223-226 and 349-351. Low. PLAUSIBLE. The scratchpad path holds the session id, so a taker's tool cannot find another session's extraction. Answers 4 and 7 of point 3 sit only in his words. Item 2's "no" itself holds: #148 and #149 rule a transfer, and A153's "logs" are the decision logs of A114. Fix: name one fixed local path outside the repository and the script that regenerates it from the transcript directory.

9. **The price sums wrong.** Design lines 372-376 and 380. Low. CONFIRMED by arithmetic. Frames 1 to 4 are 3 + 3 + 3 + 3 = 12 cycles, not 16. Sixteen includes frame 5. Fix: write 12 for frames 1 to 4 and 16 with frame 5. Then rescale the honest expectation of about 25.

10. **Four ruled marks in the body still stretch page A.** Design lines 30, 184-186, 254 and 294. Low. CONFIRMED against page A. Line 30 cites #36 and #37, which approve the map, as a ruling for a derived index of records. Lines 184-186 cite #403 and #404, a habit of reaching for subagents, as a ruling for the "records read" line. Line 254 cites #42 and #43 for the hook echo, and page A line 231 shows #43 is about the count. Line 294 cites #559 as (ruled) for a split it does not state. Section 11 says the quotes were marked in section 1 only. Fix: mark these four (reasoned) and cite the quote as context.

11. **Section 3 misreads page D's percentage.** Design line 155. Low. CONFIRMED: page D line 22 says 58% to 78% of the take's tool output is `stack.md`. Page D line 37 says the stack is 55% status lines. Line 155 writes "58% to 78% of it status lines". Fix: write "58% to 78% of the take's tool output is the stack, 55% of the stack is status lines".

12. **The end check is still the frame 114 case, and `Law:` is still mandatory.** Design lines 306-308 and 385-389. Low. CONFIRMED by the text. Review 1 finding 17 asked for held-out questions and an optional `Law:` field. Section 10 notes the fit, but section 7 item 2 still says "Write `Site:`, `Law:`, `Sign:`". Frame 2's check is the frame 114 question that the designer knows. Fix: check frame 2 on rows 64 and 89, and allow "Law: none found".

13. **Six places lean on revision 1 or page B with no gloss.** Design lines 249, 256, 274, 365-367, 427, and the codes C, W and M throughout. Low. CONFIRMED by the text. "The back-fill of revision 1", "the regenerated view of revision 1", "less than revision 1's 4k", "Revision 1 answered next alone" and "the `Derives:` line" name content the record no longer holds. C25, C73, W5 and M14 are page B row numbers with no text beside them. A reader of the record alone cannot tell what C73 asks. Fix: give each code its rule in a few words at first use, and state the dropped revision 1 parts in one paragraph of section 11.

Outside the points: none found beyond findings 8 to 13.

## Closing verdict

The design does not stand as written, but it is close. The direction and the answers to F1, F2, F3, F8, F9 and F10 stand. Findings 1, 2 and 4 decide the verdict. Finding 1 moves rules out of the brief that no moment prints, and two of them are recurring failures. Finding 2 shows that cause 1 is not proven for frame 115 under the prototype's own verbatim keys. Finding 4 leaves the agent read with nothing to read on the miss that the ruling exists for. A short revision on these three, and the count of 7 in frame 1, comes before frame 1 is pushed. No new composition contradiction was found.

## (c) Probes

All probes ran from `D:/repos/rota` at 71cb13e0 in the Bash tool, read-only.

1. `awk` over the table of `plans/frame287-questions.md` for the rows with class R, and `sed` on its class key and section 3.
2. `grep -ni` over `rota/LAWS.md` for permission, stray, reasoning, answer and prose, and the law headings. `sed -n 112,120p rota/LAWS.md` for the body of law 2.
3. `grep -n` over `plans/frame287-roman-words.md` for #43, #474, #148, #149, A153, #403 and #559, and `sed` on the quote blocks.
4. `grep -n` over `plans/frame287-context-cost.md` for 55%, 58%, 78% and 12.5k, and over `plans/frame287-rules-origin.md` for C2 to C4, C26, C58, C59, C73 and M14.

## (d) Usage

Input tokens: about 70k of context at the end (reasoned: this agent's estimate; read the harness line). Output tokens: about 10k (reasoned). Total: about 80k (reasoned).
