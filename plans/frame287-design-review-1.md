# Frame 287, design review 1

Meta workflow. Read-only review on Opus, 2026-10-17, of `plans/frame287-design.md` at commit 92bc80ff. The reviewer read the composition page, the first section of `CLAUDE.md`, pages A to D, the design, and the headers of `rota/tools/map.py` and `rota/tools/handover.py`. The reviewer edited no tracked file and ran no gate.

## (a) The verdict on each point

1. Faithful to his words: FAILS on one quote and stretches six. The `Means:` field contradicts #369 "Don't make that persisted" (F1, F11).
2. Against the composition: FAILS on three lines. One writer (F2), the tool never rules for the Principal (F3), and nothing stops quietly (F9). Content identity is a low risk (F20).
3. Against the rulings in the brief: FAILS. The design replaces the agent reads of 2026-10-03 and 2026-10-04 14:52 with a print and does not say so (F7). It sends the brief change as a notice against C73 (F8).
4. The diagnosis: PARTLY HOLDS. Cause 2 is refuted for frames 114 and 115 by a grep (F4). Two counts and one mark overstate page B (F14). One cause is missing (F15).
5. Buildable as described: YES for a grep tool, NO for the stated bet. Today's records answer the frame 114 and 115 keys without a back-fill (F4). The 15 of 19 line is soft (F5). The `plans/index/` claim misreads the map precedent (F12).
6. The stack as a view: FIVE failure modes, two of them high (F9). A smaller first step buys most of page D's saving. That step is a take print that parses the existing `stack.md` in place, plus the status tool.
7. The brief split: the list of seven is too short. The split test "under one turn in ten" moves rules that fire every cycle and that no wake moment prints (F6).
8. The price: NOT HONEST. 16 cycles is the priced side of a history that ran about twice the price. About 26 to 32 cycles is honest, which is two sprints (F16).
9. The one question for Roman: there is a SECOND. His words become a committed record in the repository, and the brief change is his to check by C73 (F8). The ask gate also changes what he sees (F3).
10. What overfits: the end check is the frame 114 case itself. The mandatory `Law:` field and the `Derives:` back-fill fit door questions only (F17).
11. What is missing: section 6 answers "what is next" for one sprint. It does not answer the medium-term story, the inflow of frames against the outflow, or the rank of the parked frames (F10).

### Point 1, quote by quote

- #369, design lines 228-232: STRETCHED TO THE OPPOSITE. The quote ends "Don't make that persisted, just give yourself a habit to communicate meaning with me" (page A line 252). The design cites "give yourself a habit" for a persisted `Means:` field. Memory `rota-frames-mean-not-number.md` records "a habit, not a repo section".
- #619, design lines 46-47, 125: STRETCHED. The quote is "no, not with deterministic checks, with subagents" (page A lines 333-334). The design cites it for a deterministic tool that refuses frames and questions.
- #36 and #37, design lines 25-26, 166-167: STRETCHED. Both approve the code map, an AST index (page A lines 521-527). They do not rule fields in records or a written index of records.
- #403 and #404, design lines 149-150: STRETCHED. #403 asks for a habit "that means that you reach for subagents" (page A line 173). The design rules a tool print as that habit.
- #559, design lines 249 and 292: STRETCHED. #559 says debug planning "is relativeley intuative as long as it doesent open large questions" (page A line 436). It does not say the composition is his line or list who talks to whom. That list is the brief's C47 text.
- #558, design line 226: a question, "when is it actually important for me to make scheuding decisions?", is marked (ruled).
- #501, design line 53: "Why would i give it the frame? hand off" is about a hand-off, not about the future of frames.
- Faithful: #20, #42, #43, #70, #94, #245, #357, #473, #474, #610, #622, #623, #624, #626, A39, A114, A152, A153. #626 "progressive re-discovery" read as "pages for held frames only" is an interpretation (reasoned).

### Point 2, line by line

- "Every record has one writer": FAILS (F2).
- "Conclusions cross a boundary. Reasoning stays where it was made": HOLDS. The prints carry records and pointers, and each moved rule keeps its origin behind a pointer.
- "A record's identity derives from its content": LOW RISK (F20).
- "The tool never rules for the Principal": FAILS (F3).
- "Nothing stops quietly": FAILS for a hand edit of the view (F9).

### Point 3, the rulings the design touches

| Ruling in `CLAUDE.md` | What the design does | Named? |
|---|---|---|
| 2026-10-03, an agent reads the records before a block (C58) | the `ask` print replaces the agent; the memory rule retires | No (F7) |
| 2026-10-04 14:52, an agent answers two things and tests the recommended answer (C59) | "The two reads ... are this print"; the test of the answer is gone | Partly: the print is named, the revocation is not (F7) |
| C73, "check them with Roman" for own instruction files | section 8: "a notice, not a question" | No (F8) |
| 2026-10-09 01:09, a transcript pointer declined as too noisy | the take prints his words tagged with the frame | No (F20) |
| 2026-10-02, frame meaning is a habit (#369, memory) | a persisted `Means:` field | No, cited as support (F1) |
| 2026-10-15, the wall guide stands with a review frame after use | the guide gains step 0 | No (low) |
| 2026-10-09 01:09, the momentum note | kept | Yes |
| 2026-09-27, five lines a frame (C67) | kept, written by the tool | Yes |
| 2026-10-12 23:40 and 2026-10-16 22:33, placement and no pause | kept | Yes |
| C26, read the open frames at a take | replaced by the take print | Yes, as a change |

## (b) Findings

1. **`Means:` persists what he said not to persist.** Design lines 228-232 and frame 5 (line 320). High. CONFIRMED: page A line 252 reads "Don't make that persisted, just give yourself a habit to communicate meaning with me". Fix: drop the `Means:` field, or ask him with the quote in front of him.

2. **Frame files, `LAWS.md` and `DECISIONS.md` get several writers.** Design lines 172-178, 318, 339-340. High. CONFIRMED by the text. Section 10 says "the status tool is the only writer of a frame file". Section 4 also has the ask tool append `Ruling:` lines, a sweeper split the archive, and a back-fill agent fill `Site:` and `Law:`. The writer of `rota/LAWS.md` is "Roman through the Liaison", yet an agent and "every door frame" write `Derives:` under each law. An agent's reasoned key then sits in a decided record with no mark. Fix: keep the keys out of `LAWS.md` and `DECISIONS.md` in one derived file, written by one script, with a (reasoned) mark per row.

3. **The ask print rules for the Principal.** Design lines 146-151, 247-249, 263-265. High. CONFIRMED by the text and page C. "A question that names no record does not go" blocks a question on a field check. Page C shows 46 of 103 questions were open design choices that no record held. The print also "tells the session whether a question is one of those", which is the tool deciding what reaches him. Fix: the print adds the "records read" line and never refuses. The session decides whether the question goes.

4. **Cause 2 is refuted for frames 114 and 115. Today's records answer the keys.** Design lines 85-92, and page C section 3. High. CONFIRMED by grep on 2026-10-17. `grep -i permission rota/LAWS.md` returns 2 lines, 339 and 342, both in law 12. `grep -i stray` returns line 339 in law 12, and line 161. `grep -i reasoning` returns line 112, the title of law 2, and line 115. Page C's claim that law 12 "does not hold the words ... permission" is false. The failure is cause 1: nobody searched `LAWS.md`. Fix: put `rota/LAWS.md`, `rota/ROLES.md` and `rota/DECISIONS.md` in the ask scope first. Run the `Derives:` back-fill only for the misses the prototype names.

5. **The 15 of 19 line measures little.** Design line 316. High. CONFIRMED from the table of page C. Rows 12, 62, 87 and 100 have their answer in `CLAUDE.md` or memory, which load every turn, so a hit there proves nothing. Eight rows share three laws (2, 3, 12), and five rows are one frame 114 answer. Rows 59 to 61 and 102 have their answer in a transcript, which the prototype does not read before frame 3. The R class is itself a judgement: page C says R can be 17. The noise is the real risk. Over the archive, "answer" returns 1,059 lines, "door" 1,104 and "api.py" 310. Fix: count distinct answers, about 9, not rows. Take the keys verbatim from the question as sent. Count a hit only inside the capped print, about 3k tokens. Exclude rows whose answer loads every turn.

6. **The brief split moves rules that fire every cycle and that no moment prints.** Design lines 209, 272-275, section 3 table. High. CONFIRMED: the six moments are take, push, design, ask, night and close. No moment covers an agent launch, a commit, a scripted edit, or the 300k and 400k lines. Rules C37 and C38 (Opus on every agent), C39, C40, C43, C45, C50 with M1, C51, C52, C65, C72 and C74 act every cycle. C2 to C4 act on the count that arrives every turn. Fix: move a rule out only when a moment prints it. Keep the cycle rules in the brief, or add an `agent` and a `commit` moment.

7. **The print replaces two agent-read rulings, and the design does not say so.** Design lines 146-151, 263-265, 281-282. High. CONFIRMED against `CLAUDE.md` (page B lines 443-465). The 2026-10-03 ruling says "an agent reads the records". The 2026-10-04 14:52 ruling says "an agent answers two things", and the second is whether the recommended answer holds against the evidence. A grep print does neither. Frame 114's door change stood two days for want of that second test. Fix: the print feeds the agent read. Name both rulings as amended, and keep the test of the recommended answer.

8. **A second question for Roman: his words in the repository, and the brief change itself.** Design lines 177, 300-305, 346-349. High. CONFIRMED by the text. Section 10 says the words record is "his to decline", and section 8 says only the composition sentence is his. A153's words include "youre pissing me off", and #148 says the workflow transfers to another project. C73 says the session checks its own instruction files with Roman. Fix: put two items in section 8, the words record and the brief diff, each with a recommended answer.

9. **The view regime has two high failure modes.** Design lines 172, 207-208, 338-341. High. PLAUSIBLE. First, the next regeneration erases a hand edit of the view with no sign, which breaks "Nothing stops quietly". Sessions have edited `stack.md` by hand for a month. Second, `wake status` "commits" in one checkout where an implementer can hold staged files, so a plain `git commit` takes them in. Branches, which wait on a night, make the committed view conflict on every merge. A kill between the append and the regeneration is safe only if every read regenerates first. The archive parse is low risk (observed: 28 files, `### n.` headings throughout, 0 duplicate numbers across the archive and the 121 open headings). Fix: regenerate only when the bytes of the view match the last generated hash, and print a diff when they do not. Commit with an explicit pathspec. First step: a take print that parses `stack.md` in place, and the status tool.

10. **Section 6 answers "next" and not "future management".** Design lines 221-249. High. PLAUSIBLE, against page A section 5. He asks "What are we writing towards in the medium term?" (#356), "mid term story, succinct" (#358), "are we producing new frames and then never prioritising them" (#557), and "slower than they are being generated?" (#571). `wake next` prints one sprint. Nothing prints the destination, the 119 open frames against the rate of closes, or the parked rank. He would still ask what the work is for and whether the backlog shrinks. Fix: `wake next` also prints the destination line of the composition, opened and closed counts per day, and the parked ranks.

11. **Six quotes are stretched.** Design lines 25-26, 46-47, 53, 149-150, 226, 249, 292. Low. CONFIRMED: see point 1. Fix: mark those lines (reasoned) and cite the quote as context, not as a ruling.

12. **The map writes no index, so the precedent is wrong.** Design lines 163-167. Low. CONFIRMED: the `map.py` docstring says "There is no cache", because a cache key "misses the unstaged edit". A committed `plans/index/` drifts the same way and adds a commit per change. Fix: compute the hits at each call, as the map does. The records are about 2 MB of text.

13. **Two of three memory retirements do not follow from the status tool.** Design lines 279-281. Low. CONFIRMED from the memory index. The backslash rule covers every scripted edit, "status-line scripts included". Release-before-rearm concerns `handover.py release` and `holding`, not a status line. Fix: retire the clock rule only.

14. **Cause 1 and cause 4 overstate page B.** Design lines 83-84, 105-107, 112-113. Low. CONFIRMED. Page B says the history rule "recurred four times after the rule", strikes 2 to 5, and the design says five. Page B marks C5 and C14 to C22 "n/c", and the gate rules M2 and M3 recurred, so "stopped when a tool took the moment" is not observed. The "half the brief" figure is (reasoned) in page B and (observed) in the design. Fix: write four, and mark the tool pattern (reasoned).

15. **A cause is missing: the session held the fact and did not connect it.** Design section 2. Low. CONFIRMED from page C. Rows 59 to 61 had the frame 204 design open, row 99 had the composition line on the read list, and rows 89 and 90 had the interview committed. More prints do not fix a fact that was already in front of the session. Fix: add the cause, and route it to the interview rule, not to the index.

16. **The price is the priced side of the overrun history.** Design lines 314-325. Low. PLAUSIBLE by the anchors. Page B says closed frames ran a median of 5 cycles against 2 to 3 priced. Frame 3 alone is an agent pass over about 290 frame records, 57 decision headings and 14 laws, plus a review and a fix pass. Frame 4 needs a Roman check by C73 and a live take. Fix: price about 26 to 32 cycles, two sprints, or cut frames 3 and 5 until the prototype reports.

17. **The end check and the `Law:` field overfit the door questions.** Design lines 259-260, 316, 327-331. Low. PLAUSIBLE. The end check is the frame 114 case, which the designer already knows. Instrument frames, harness frames and meta frames such as 287 have no law, so a mandatory `Law:` invites filler. Fix: check on held-out questions, for example rows 64, 89 and 12. Make `Law:` optional with "none found".

18. **Sprint orders and the head rules of the stack have no record shape.** Design section 4 table. Low. CONFIRMED: `stack.md` lines 50 to 390 hold five sprint orders and the superseded "Stack" section, about 43k characters (page D section 7). Fix: add a sprint-order record with one writer, and a fixed head template for the view.

19. **The hook change removes the anti-idle prompt at task notifications.** Design line 213. Low. PLAUSIBLE. The echo is the "Standing instruction ... ask whether you are actually blocked", paired with the `really_blocked.py` Stop hook. A task notification is the turn where a session most often stops. Fix: keep the echo on notifications, or shorten its text.

20. **His words on every take reverse a declined pointer, and the `#n` tags are positional.** Design lines 129, 177. Low. PLAUSIBLE. The momentum ruling declined transcript pointers as "too noisy over time". The take print brings his words tagged by frame. The `#n` tags number messages in one extraction, so a changed filter renumbers every citation. Fix: key each quote by session and timestamp, and print his words at `ask` only.

Outside the points: `tests/rota/test_vocabulary.py` reads `rota/LAWS.md` for legacy words, so a `Derives:` line can turn the suite red (PLAUSIBLE, low). Finding 2's fix removes the risk.

## Closing verdict

The design does not stand as written. The direction stands: retrieval keyed by the moment, a status tool, and a smaller take. Findings 1, 3, 4, 6 and 7 decide the verdict. One field contradicts his words. The ask gate rules for him. The back-fill rests on a cause that a grep refutes. The brief split drops cycle rules. Two rulings are revoked and not named. A revision pass that answers findings 1 to 10 comes before any build frame.

## (c) Probes

All probes ran from `D:/repos/rota` at 92bc80ff in the Bash tool, read-only.

1. `grep -n` over `plans/frame287-roman-words.md` for every tag the design cites, and a read of lines 120-590.
2. Law text: `sed -n 105,150p` and `sed -n 320,345p` on `rota/LAWS.md`, and the law headings.
3. Frame 114 keys: `grep -ci` for permission, touch, stray, api.py, code.commit, write, door, fence, restore and unnamed over `rota/LAWS.md`, `rota/DECISIONS.md`, `plans/stack.md` and `plans/archive/*.md`, with the hit lines in LAWS.
4. Frame 115 keys: the same for answer, prose, reasoning, "decision record", architect, words and why.
5. Readers of `LAWS.md` and `DECISIONS.md` in `rota` and `tests`.
6. Archive parse: `### n.` heading counts per archive file, and duplicate frame numbers across the archive and `stack.md` (0).
7. The `map.py` docstring (no cache), the `handover.py` header, the hook in `.claude/settings.json`, and `git log -S "Standing instruction"`.

## (d) Usage

Input tokens: about 95k of context at the end (reasoned: this agent's estimate; read the harness line). Output tokens: about 14k (reasoned). Total: about 109k (reasoned).
