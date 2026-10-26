# Frame 340, review 1 of a24c5dc7

Verdict: a24c5dc7 does not stand. 2 high, 2 med, 4 low. The 54 tests of the two named files pass. The pass gate refuses 0 of 23 live pass lines of 2026-10-26. The close gate misses the "Met" close, which is the form of each close on 2026-10-26.

## (b) Findings, by severity

1. High. `rota/tools/status.py` 50 and 63. CONFIRMED. `NOT_PASS` searches the whole body for a whole word. Each of the 23 live pass lines of 2026-10-26 holds "read", "review" or "gate" somewhere, for example "The review reads it." or "Pushed from the C3 read". So the pass gate refuses 0 of 23 on frames with no Reach line. Frame 330's line of 18:20 is the red test that frame 340's Ends when names, and that line passes. The docstring says "Nothing passes the first gate", and that is false. Fix: test `NOT_PASS` only on the clause before the match, `body[:m.start()].rsplit(".", 1)[-1]`. On the same 23 lines that change refuses 21 and accepts all 8 pure read, review and gate lines.
2. High. `rota/tools/status.py` 51. CONFIRMED. `CLOSE_LINE` knows "closed", "closes", "popped" and "pops" only. The two closes of 2026-10-26, frames 321 and 283, start "**Met on night 3 of 3". They pass on a frame with no Reach line and on a frame at 1 of 10. From 2026-10-23 to 2026-10-26, the gate catches 7 of the last lines of 15 archived frames, and 5 "Met" closes escape. The move to the archive is a hand edit, so no tool gates the close itself. Fix: add `met` to the close words now, and put the gate on the archive move when a tool for the move exists.
3. Med. Frame 340 Ends when, first clause. CONFIRMED by read. The clause asks for a refusal when "the night clause has not moved". C76 step 7 asks for the same second count. The pass does not build it, and pass 1 says so in its open question 4. Fix: build the night count in pass 2, or amend the Ends when line with a reason.
4. Med. `rota/tools/state.py` 222 to 230. CONFIRMED. `reach_line` returns the first Reach line. With "10 of 10" then a recount "1 of 10", the close passes. With "1 of 10" then "10 of 10", the close is refused. Fix: read the last Reach line, the way `insert` treats the last status line, or refuse a block with two.
5. Low. `rota/tools/status.py` 262 and 263. CONFIRMED. `--force-close` stamps "(forced: r)" on any body. A plain note gets the stamp. A `--ruling` line gets the stamp after his words. Fix: append the stamp only when the close gate fires, and refuse the flag with `--ruling`.
6. Low. `rota/tools/status.py` 47 and 63. CONFIRMED by gate call, 0 of 98 archived closes hit. The pass gate runs before the close gate. A forced close whose body says "pass 2 built" or "implementer ... runs" is refused with the pass message. The `.*` in `implementer.*runs` spans sentences. Fix: skip the pass gate when `CLOSE_LINE` matches, and use `[^.]*` in place of `.*`.
7. Low. `rota/tools/status.py` 72 and 73. PLAUSIBLE. A Reach line with no count, or with k above N, passes the close. C76 refuses a close unless the reach reads one reader, and such a line shows nothing. Fix: refuse a close when `COUNT` does not match.
8. Low. `tests/rota/test_status_gates.py` 76, 83 and 124. CONFIRMED by read. Line 76 asserts the whole refusal text, and line 124 asserts the whole forced line, so a wording change turns them red. Line 83 pins "Pass 1 is at the gate." as accepted, which pins finding 1. Fix: assert the frame number and "Reach" only, and move line 83 into the refused set after finding 1.

## (a) The points

1. Pass pattern. CONFIRMED miss. 17 pass bodies and 6 review or gate bodies that start a pass all pass on frames with no Reach line, 0 refused. The 8 pure read, review and gate bodies pass. Misses: lines 1235, 1236, 1245 to 1248, 1258, 1259, 1270 to 1274, 1287 to 1294, 1365, 1367 of `plans/stack.md`. Lines 1365 and 1367 also fail `PASS_LINE` itself, "Pass 2 on the same implementer". Fix: finding 1.
2. Close pattern. CONFIRMED in part. The three "closed" lines, 302, 257 and 277, are refused at 1 of 10, with no Reach line and with a wrapped bullet, and pass at 3 of 3. The two "Met" lines, 321 and 283, pass on every frame. `--force-close` writes "(forced: probe reason)" and never passes the pass gate. Fix: finding 2.
3. Ruling. CONFIRMED. `main` skips both gates when `--ruling` is given. "closed, pass 1 runs now" lands on both test frames and on a frame with no Reach line. Fix: none, but see finding 5.
4. Reader. CONFIRMED. A wrapped bullet "- Reach: 1 / of 10, the wrapped / bullet." returns "1 of 10, the wrapped bullet.", which is right. Two Reach lines return the first, which is wrong for a recount. Fix: finding 4.
5. Old frames. The premise does not hold today. A close of frame 328 or 329 in the "Met on night 3 of 3" form passes with no Reach line, by finding 2. After finding 2 lands, `--force-close` with a reason is the right path. C76 names no start date and says a close on one count alone "is a residue line". A forced reason makes that residue visible, and a date skip would hide it on 137 live frames, 0 of which hold a Reach bullet. Change: none to the gate. Optional: the no-Reach refusal names `--force-close "pushed before C76"`.
6. Outside the brief. The test file is under `tests/rota`, a deviation the report states and the gate needs. `reach_line` also takes a string. The close match ignores case, which a "Closed." line needs. Frame 340 writes its own reach inside a status line, so the reader reads None for frame 340. Its own pass 2 will be refused once finding 1 is fixed. Message strings: finding 8.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/8db3a3f9-e4b2-4ce2-b920-9ce56f8071c8/scratchpad/r340/probe1.py`: 31 live bodies of 2026-10-26 through `status.main --no-commit` on a temp copy of the stack.
- `.../scratchpad/r340/probe2.py`: five archived last lines against six built frames. The frames are 1 of 10, none, 3 of 3, wrapped, and two pairs of Reach lines. The probe also runs `--force-close` on a pass body, a plain note, a ruling and a blank reason.
- `python -c` calls: `CLOSE_LINE` on the last lines of 115 archived frames of October, 98 hits. The same calls ran the candidate fix of finding 1 and `gate()` on three forced recap bodies.
- `pytest -p no:cacheprovider tests/rota/test_status_gates.py tests/rota/test_tools_state.py -q`: 54 passed.

## (d) Usage

The harness shows no count to this agent. Estimate: about 75k input tokens, 14k output tokens, 89k in total.
