# Frame 201: provenance of the lines check on `verdicts.emit`

Written 2026-10-21 by one read agent on Opus, about 73k, for session
5389be74, by the ruling of 2026-10-18 that every wall gets a provenance
read before its first fix.

**Answer.** Roman ruled the lines check on 2026-10-07 08:57. The ruling says that a pass names a line per criterion and that the door refuses a pass that leaves a criterion unnamed (observed: `plans/archive/stack-2026-10-08.md:20`). The design admitted multi-line values and docstring lines (observed: `plans/frame170-design.md:16,99`). The review of 845e0b80 then found that a whole block landed, so c038ea3e of 2026-10-07 added the refusal of more than 2 lines, with no candidate line and no fail route (observed: `plans/archive/stack-2026-10-08.md:23-24`, `git show c038ea3e`). Frame 180 of 2026-10-08 added the docstring refusal, the list of code lines and the quote refusal. It changed only the not-in-diff branch, so the block refusal still names nothing (observed: 20ac26ce, 5028568b, 54901ea7, b561fec8). No record forbids the block refusal from naming the added code lines, and two records argue for it (reasoned: section 6).

## 1. The ruling

- Frame 170: "**ruled: a pass names a line per requirement. The Critic writes, for each criterion, the line of the change that meets it, before it signs, and the door refuses a pass that leaves a criterion unnamed** (ruled: Roman, 2026-10-07 08:57 ...)" (observed: `plans/archive/stack-2026-10-08.md:20`). The docstring of `_pass_lines_check` repeats it (observed: `rota/roles/api.py:11450-11453`).
- The ruling names one line per criterion. It names no line count, no block rule and no docstring rule. The 2-line cap is a build decision (reasoned: the words at line 20).
- Frame 180 is not a ruling. Session 18588d6d claimed it "second on the order taken by timeout at 02:13" (observed: `plans/archive/stack-2026-10-08.md:87`). It changed the not-in-diff refusal twice:
  1. 5028568b, 2026-10-08 04:57: "When a named line is not in the diff and no added line is near, the refusal lists up to eight code lines of the diff" (observed: `git show 5028568b`; the review's low at `stack-2026-10-08.md:89`, "a line not in the diff gets no hint toward a code line").
  2. 54901ea7, 2026-10-08 05:35, and b561fec8, 06:05: a quote of a criterion gets its own words and the code-line list, with the fail route kept last (observed: `stack-2026-10-08.md:91-94`; `rota/roles/api.py:11539-11550`).
- Frame 180 also added 20ac26ce, 2026-10-08 04:11, which refuses a line with no behaviour ("a docstring line") (observed: `rota/roles/api.py:11283-11287,11558-11575`).

## 2. The three refusal texts

| Text | Commit, date | Decision | Workflow |
|---|---|---|---|
| "holds N lines, and a pass names one added line per criterion. Copy the one line of the [diff] block..." | c038ea3e, 2026-10-07 10:37 (frame 170 pass 2) | The diff review of 845e0b80, 10:12: "the line-break tolerance admits a whole added block... a value with more than 2 parts is refused with words that ask for the one line". The cap stays at 2: "Decided by the assistant, 2026-10-07" | Review: Rota. Decision: Meta (observed: `stack-2026-10-08.md:23-24`; `plans/frame170-pass2.md:10,48`) |
| "is not an added line of the diff... The added line nearest to it..." | 1663c2bb on `rota/foundation` (845e0b80 on `f170`), 2026-10-07 09:52, pass 1 | Design record of 09:08, from the ruling of 08:57 | Meta (observed: `stack-2026-10-08.md:21`; `plans/frame170-design.md:88-92`) |
| The same text plus "The added lines of code are..." | 5028568b, 2026-10-08 04:57, frame 180 pass 2 | The review of 7b25da26, 04:23 | Review: Rota. Decision: Meta (observed: `stack-2026-10-08.md:89-90`) |
| "that is the criterion's text, not a line of the diff..." | 54901ea7, 2026-10-08 05:35; b561fec8, 06:05 | Delta review medium CONFIRMED; second look high, "the quote refusal offers no fail route" | Review: Rota. Decision: Meta (observed: `stack-2026-10-08.md:91-94`) |

## 3. The design's condition and the build

- The design admitted a block. "A value with line breaks is split, and each non-empty part must hold" (observed: `plans/frame170-design.md:16`).
- The design admitted a docstring line. "A seat can name a comment line, a docstring line... and the door admits it". It made that line a miss for ratio two by hand, not a refusal (observed: `plans/frame170-design.md:99,221`).
- The condition for the residue: "a Critic session that ends with no verdict is read, and the frame closes when its cause is not the new door". Ratio one: sessions that land a verdict, at least 4 in 5 (observed: `stack-2026-10-08.md:20`).
- The build broke the condition on the fixture. At c038ea3e, `L1-CR-fail-names-its-criterion` sent a 3-line block, met the block refusal four times and ended with no verdict. The final record shows 0 of 5 runs right and 3 runs with no verdict (observed: `stack-2026-10-08.md:24,28`; `plans/frame199-read.md:13-16`). Frame 170 closed on night 130 only: "no Critic session ended without a verdict", 1 of 1 sessions (observed: `stack-2026-10-08.md:36`).
- The door now does this:
  - A block of more than 2 lines gets the block refusal, with no candidate line and no fail route (observed: `rota/roles/api.py:11497-11503`).
  - A docstring line of 1 or 2 lines gets the no-behaviour refusal, with the fail route and no code-line list (observed: `rota/roles/api.py:11561-11575`).
  - The 3-line `:param show_python:` block of night 157 and the 4-line value of night 144 met the block refusal. No verdict landed, and the quarantine followed (observed: `plans/night157-read.md:197` W3; `plans/night144-read.md:536-541`).
  - Night 152 is a different sign: a wrong pass landed on `show_python: bool = False,` (observed: `plans/stack.md:1550`; `plans/night152-read.md:42-49`).

## 4. The brief

- `rota/roles/prompts/critic/review.md:9-11`: "For each criterion, find the added line of the diff that meets it, a line that starts with `+`, and copy it without the `+`." Lines 33-36: "A pass carries `lines=`... The tool refuses a pass with a criterion that has no line, or a line the diff does not add." (observed: last change 1663c2bb, 2026-10-07).
- The brief does not say "one line". It does not say "not a docstring" and does not mention a block. Frame 180 changed the door but not the brief (reasoned: `git log -- rota/roles/prompts/critic/review.md` ends at 1663c2bb). `rota/roles/prompts/critic/answer.md:20-21` has the same shape.

## 5. Why only the no-near-line refusal names candidates

- Order in the code: the block check runs at `rota/roles/api.py:11497-11503`, before `_added_kinds` reads the diff at line 11504. So the code-line list does not exist yet when the block refusal is raised (observed).
- The block check's comment gives one reason: "A block is not a line. A whole added function given for every criterion lands on any batch, so the line names nothing (frame 170's review of 845e0b80...)" (observed: `rota/roles/api.py:11493-11496`). It gives no reason to name no candidate.
- 5028568b added the list for one reason: "So a seat on a correct batch finds a line to name and does not go to the fail route" (observed: `git show 5028568b`; comment at `rota/roles/api.py:11522-11525`). That commit changed only the not-held branch (observed: the diff of 5028568b).
- The pass 2 record says only "The block refusal records no offer. Its words name no call that the doors admit, so frame 144's law asks for none" (observed: `plans/frame170-pass2.md:17`). That rule is about offers, not about listed lines.
- So the gap is one of timing, not a decision. The block refusal predates the list by about 18 hours, and frame 180 did not go back to it (reasoned: c038ea3e at 2026-10-07 10:37 against 5028568b at 2026-10-08 04:57).
- Night 157's read names the same cause: "the refusal names no candidate `+` line" (observed: `plans/night157-read.md:197`).

## 6. What a cheap fix is allowed by the history

No record forbids the block refusal from listing the added code lines. The design's house rule "name the set, do not merely reject the guess" (`plans/frame170-design.md:92`) and frame 180's reason in 5028568b both argue for the list. Frame 201's ends-when asks that "a refused `verdicts.emit` names the one-line shape" (`plans/stack.md:1545`) (reasoned). The history sets three limits:
- The cap stays at 2 (`plans/frame170-pass2.md:48`).
- The fail route must stay last after any list (frame 180's second look, b561fec8, `stack-2026-10-08.md:93-94`).
- The no-behaviour refusal also lists no code lines, so a cut docstring block meets the same wall there (observed: `rota/roles/api.py:11570-11575`).
