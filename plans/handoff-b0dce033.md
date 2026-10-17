# Momentum note of session b0dce033, peer name rota-68

Message rota-68 for a context question before you ask Roman. Facts are in
`plans/stack.md`. This session took frame 274 from the vacancy on disk at
02:15 on 2026-10-17, watched night 153, stopped it at 04:02 at its second
`CYCLE` line, ran its read, wrote sprint 11, built frame 223's passes 1,
1b and 2 with two interviews and a review, read frame 278's route and
started its pass 1. It hands off past 300k with every held frame at a
commit. The earlier notes `plans/handoff-1cf2843b.md` and the ones it
names still stand for sprints 6 to 10.

## Read first: sprint 11 is at the top of the stack, and the next night waits on rows 2 to 4

Roman ruled at 22:33 on 2026-10-16, "Stop pausing for sprint orders, I will
re prioritise if something changes". Sprint 11's order is at the top of
`plans/stack.md`, written from `plans/night153-read.md`. He asked nothing
of this session but one thing: at about 04:40 he answered frame 264's
question in the terminal, "is there not an obvious answer? present the
information correctly the the llm when required??", which the stack
records as the ruling that the project's summary stays on the request
page presented as the project today. Frame 264 is buildable, placed after
frame 274's pass 2 because both edit `principal.py`.

Night 154 runs from the checkout's head after sprint 11's rows 2 to 4 are
built: frame 140, the commit beside a `dropped` note; frame 277, the
non-constant tautology; frame 266's pass 3, the dict value and the escaped
quote. Row 1, frame 223, is built and validating. It is held on frame 223's
ratio, bodies after a reasoned challenge that pass the harness on the first
run, with frame 140, and counts frames 274 and 273 at their second night.
The launcher shape is `.rota/launch_night153.sh`; copy it, change the sha
and the night number.

## What I believe

- Frame 223's push is right and measured: 15 of 129 failed runs over
  nights 140 to 153, 0 false pushes after pass 2. It moves the Tester to an
  installed `package_name`, 3 of 5, and never to `version=`. The `version=`
  belief is frame 281, cause 5, which needs a history read and then a
  question to Roman, rated medium: may a test pass a literal the criterion
  does not name when the call needs one to run. Recommended yes.
- The gate's known reds are eight names plus the flaky
  `scene_challenged_again`; `test_fixtures::test_no_case_leaves_a_reference_unwrapped`
  is among them and predates frame 223. Three of the L1 reds carry
  recordings of 2026-10-11 and 2026-10-13, so they are not of this sprint.
  A fresh baseline would make the new-reds line useful again.
- Frame 278 is not a route question. Roman ruled the route on 2026-10-11
  06:30. The wall is the thread view in the runner that drops an answer's
  decision refs, and the same-refs step that then points to the code.
- Agents overran every cap this session: the night read 311.6k against
  300k, the reads 86k to 111k against 60k, the review 74k against 40k, the
  implementer 133k for pass 1 against 80k. Price with that.

## What to doubt first

- The new case `L1-TS-pass-a-literal-value-for-a-name-looked-up-at-run-time`
  recorded fresh twice when it should have replayed. The implementer's
  guess is a missing `ROTA_NUM_CTX` on the command line. Read the stale
  line of the gate on afcf52d3 before you trust its tally.
- Frame 274's skip fired 0 of 5 on night 153 because the contests fell on
  criteria, which `request_of` does not read. Pass 2, sprint 11 row 8, is
  cheap and rides along when `principal.py` is free.
- Frame 273's own sign is at 0, but the two tautologies of frame 277 hid a
  red test through a whole review. Build 277 before the night.

## Roman's last words

- 2026-10-17 about 04:40, in the terminal, to frame 264's question: "for
  the question that youre blocked on, is there not an obvious answer?
  present the information correctly the the llm when required??"
- 2026-10-16 22:33: "Stop pausing for sprint orders, I will re prioritise
  if something changes".

## Live agents at the hand-off

- Frame 278's pass 1 implementer may still be running in the checkout
  when you take over; its report lands at `f278/pass1-report.md` under
  this session's scratchpad,
  `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b0dce033-321f-4299-b3e0-056d78ea27c8/scratchpad/`.
  Frame 278's status line says whether it reported. If the diff is in the
  checkout uncommitted, read the report, run the touched tests, and judge
  it as pass 1.
- Briefs and reports: `n153/`, `f223/`, `f278/`, `r223/` under that
  scratchpad.
- Worktrees: `C:/Users/roman/rota_gate_223` at afcf52d3 with the register
  copied, and `C:/Users/roman/rota_r223` at 134a7d8f. Remove both when
  frame 223's gate is accepted.
