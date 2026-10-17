# Momentum note of session b0dce033, peer name rota-23

Message rota-23 for a context question before you ask Roman. The peer
name was rota-68 until the machine crashed at 06:26 on 2026-10-17 and
rota-23 after. Facts are in `plans/stack.md`. This session took frame 274
from the vacancy on disk at 02:15 on 2026-10-17, watched night 153,
stopped it at 04:02 at its second `CYCLE` line, ran its read, wrote sprint
11, built frame 223 to its accepted commit with two interviews, a review
and a gate, read frame 278's route and built its passes 1 to 1d with three
reviews. It hands off past 300k with every held frame at a commit. The
earlier notes `plans/handoff-1cf2843b.md` and the ones it names still
stand for sprints 6 to 10.

## Read first: one gate is owed, then sprint 11's rows 2 to 4, then night 154

Frame 278's pass 1d is at 25e85680 and its gate has not run. The worktree
`C:/Users/roman/rota_gate_223` holds the register copied by the backup API
and `.rota-gate.json`; move it to 25e85680 with `git -C <dir> checkout
--detach 25e85680` and run `python -m rota.tools.gate` from it, unpiped, in
the background. The known reds are nine names plus the flaky
`scene_challenged_again`; the last two gates listed the same nine, three of
them L1 cases with recordings of 2026-10-11 and 2026-10-13. The recorded
cases of the `tests_failing` and same-refs wakes go stale on 278's commit,
and the gate re-records them. Accept 278 when the stale line is 0 and the
new reds are the known names.

Then sprint 11's rows 2 to 4, in order, one implementer at a time: frame
140, the commit beside a `dropped` note; frame 277, the non-constant
tautology; frame 266's pass 3, the dict value and the escaped quote. Row
5, frame 278, is built. Row 1, frame 223, is accepted at afcf52d3. Then
night 154 from the checkout's head, cold, held on frame 223's ratio,
bodies after a reasoned challenge that pass the harness on the first run,
with frame 140, and counting frames 274, 273 and 278 at their first night.
The launcher shape is `.rota/launch_night153.sh`; copy it, change the sha
and the night number. Ollama runs as the tray app on port 11434, started
at 11:43 after the crash.

Roman ruled at 22:33 on 2026-10-16, "Stop pausing for sprint orders, I will
re prioritise if something changes". He answered frame 264's question at
about 04:40, "is there not an obvious answer? present the information
correctly the the llm when required??", recorded as the ruling that the
project's summary stays on the request page presented as the project
today. Frame 264 is buildable, placed after frame 274's pass 2 because
both edit `principal.py`.

## What I believe

- Frame 223's push is right and measured: 15 of 129 failed runs over
  nights 140 to 153, 0 false pushes after pass 2. It moves the Tester to an
  installed `package_name`, 3 of 5 on the gate's re-record, and never to
  `version=`. The `version=` belief is frame 281, cause 5, which needs a
  history read and then a question to Roman, rated medium: may a test pass
  a literal the criterion does not name when the call needs one to run.
  Recommended yes.
- Frame 278 is not a route question. Roman ruled the route on 2026-10-11
  06:30. The fix makes the thread view show the decision an answer adds
  and the same-refs step offer the challenge with the decision id, and
  after three reviews the step asks the door itself whether the call would
  land. Its residue: the evidence door and the red-line door can still
  refuse the challenge the step offers, review 3's second low, unprobed,
  and a decision a later decision supersedes, review 1's finding 5.
- The crash left no damage beyond the branch ref and the index, both
  repaired from the reflog; `git fsck --connectivity-only` was clean.
- Agents overran every cap this session: the night read 311.6k against
  300k, the reads 86k to 111k against 60k, the reviews 54k to 74k against
  20k to 40k, the implementers 90k to 133k against 60k to 80k. Price with
  that.

## What to doubt first

- The new case `L1-TS-pass-a-literal-value-for-a-name-looked-up-at-run-time`
  recorded fresh twice when it should have replayed; the gate then
  re-recorded it green 3 of 5 and `stale (0)`. If it reads stale again on
  278's gate, the cause is the register key, not the pass.
- Frame 274's skip fired 0 of 5 on night 153 because the contests fell on
  criteria, which `request_of` does not read. Pass 2, sprint 11 row 8, is
  cheap and rides along when `principal.py` is free.
- Frame 278's module flag `_ASKING_DOOR` in `rota/core/sandbox.py` is a
  global; review 3 offers a `ContextVar` as the optional fix. Not a wall.
- Frame 273's own sign is at 0, but the two tautologies of frame 277 hid a
  red test through a whole review. Build 277 before the night.

## Roman's last words

- 2026-10-17 about 11:43, in the terminal: "you can start ollama".
- 2026-10-17 about 11:38: "sorry pc crashed".
- 2026-10-17 about 04:40, to frame 264's question: "for the question that
  youre blocked on, is there not an obvious answer? present the
  information correctly the the llm when required??"
- 2026-10-16 22:33: "Stop pausing for sprint orders, I will re prioritise
  if something changes".

## Live agents at the hand-off

- None. Every implementer and reviewer has reported.
- Briefs and reports: `n153/`, `f223/`, `f278/`, `r223/`, `r278/`, `r278b/`
  under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b0dce033-321f-4299-b3e0-056d78ea27c8/scratchpad/`.
- Worktrees: `C:/Users/roman/rota_gate_223` at afcf52d3 with the register
  copied, kept for frame 278's gate. Remove it when that gate is accepted.
