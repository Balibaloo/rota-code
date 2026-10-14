# Momentum note of session 9b79f4a1, peer name rota-cd

Message rota-cd for a context question before you ask Roman. Facts are in
`plans/stack.md`. This session holds frames 233, 235, 225, 173, 229, 228,
204, 206, 203 and 198, every one at a commit. This page holds the
judgement, from the take of frame 213 at 02:26 on 2026-10-14 to the hand-off
after frame 233's last review.

## What this session did

- Took frame 213 from the vacancy b4070ef8 left, watched night 146 to its
  end at 07:00, named the frame at every mark while it ran, and pushed
  frame 234 from the three cancels of walk 1 before the night ended.
- Read the night on Opus, `plans/night146-read.md`. Closed sprint 3: frames
  232, 213 and 226 closed, frame 189 closed on the recommended reading by
  timeout. Proposed sprint 4 at the top of the stack, taken by timeout at
  07:41 with no reply from Roman.
- Frame 235, the IPv4 host: done by this session, one line in four files and
  one test, validating at a6d715dc. It is the largest single saving the
  nights have found: 83 of 218 minutes on night 146 were a refused IPv6
  connect to `localhost` on every request.
- Frame 233, the replayed onboarding: three steps on one implementer,
  5d5d7556 in code, with three accepted reviews, the last two lows fixed by this session at the
  hand-off. It validates on night 147.

## What I believe and why

- Night 147 is the test of frames 233 and 235 together, and its launch has
  two new steps that the gauntlet does not do by itself: seed the night
  cassette and point the principal replay at a record. From the checkout:
  `python probes/seed_night_cassettes.py .rota/clickI_night146.db .rota/night_cassettes.db`,
  and `ROTA_PRINCIPAL_REPLAY` set to the live `.rota/clickI.principal.jsonl`
  or a copy of it, because the gauntlet's default `$STATE/principal_replay.jsonl`
  does not exist. Check the argument order in the script's usage line
  first. Without the seed, onboarding runs live and reports no error, which
  is review 2's low 2. The ends-when: onboarding under 15 minutes with 70
  or more sessions on `cassette:`, against 39 minutes and 4 asks on night
  146.
- Frame 234, the Liaison's verdict that contests the request line, is the
  next night's wall and the real finding of night 146: 4 of 8 batches died
  on a page where the principal named other lines, and one on a page he
  approved with "Ok, go ahead". Its pass 1 shape is in the read, section 3:
  a door on `rulings.rule` that refuses a `contest` on a line the words do
  not name, and the brief line. I did not start it, because the 300k line
  came first.
- The sprint 4 order after frame 233 is 235 done, then 234, 202 with the
  surface move, 221 with the brief lines, 236, 225's pass 2. Rows 3 to 7 are
  about 15 cycles. Night 147 runs from row 7's commit. If a session needs
  the night sooner, launch it after frame 234 alone: 234 is the wall, and
  the other four are each one or two batches.
- Frame 202's surface move is the Tester wall behind frame 213's landed
  words: the principal's answer reached the Tester three times and the
  Tester kept `echo`, because the criterion's `surface_refs` named it. The
  read's candidate B is the door.

## What to doubt first

- Frame 233's principal key is the page text alone. The design wanted the
  system prompt's hash beside it and no recorded row holds one. A page that
  recurs across requests with different right answers would replay the
  newest. The third review's point 2 measures this on night 146's record.
- The seed's "native" skip reads an empty completion as the sign, because
  the night stores no protocol per session. Every night runs the text
  protocol today, so it is safe, and it is not a sign.
- Frame 235's night count is the median of `turns.ms` less the request's
  duration in Ollama's log. Ollama must run under `OLLAMA_DEBUG=1` again
  for that, with `.rota/ollama146.ps1` as the shape. Ollama was still
  running under debug at this hand-off; a restart loses nothing.
- The reserve: 0 free standbys at 09:3x, all five standby rows stale. Roman
  got one `[med]` notification at 09:3x that a window is needed.

## Roman's last rulings, in his words

- 2026-10-13 19:3x, "Ok", on the plan: frame 232 before night 146, the night
  with Ollama's log, frame 233 first next sprint (recorded by rota-ff).
- No reply since. The sprint 4 order and frame 189's close were taken by
  timeout at 07:41 on 2026-10-14, rated low.

## Live agents at the hand-off

- The reviewer of 5d5d7556 on `C:/Users/roman/rota_rv233c`, read-only, brief
  `rv233s3_brief.md` in this session's scratchpad, report to
  `plans/frame233-review-3.md`. If its ten lines are not in frame 233's
  status when you take the frame, read the report file: accept means the
  frame validates on night 147; revise means one more pass on a fresh
  implementer with the findings as its brief.
- The frame 233 implementer ended after step 3; its report is
  `scratchpad/f233/step1-report.md` with sections for steps 1 to 3.
- The scratchpad is
  `C:\Users\roman\AppData\Local\Temp\claude\d--repos-rota\9b79f4a1-9b90-4560-90e3-6e7dd48f1351\scratchpad`,
  with `status.py` to append a status line with the clock's time
  (`python status.py <frame> <body file> [--claim]`), `read146_brief.md`,
  and the review briefs. Review worktrees `rota_rv233`, `rota_rv233b` and
  `rota_rv233c` under `C:/Users/roman/` can be removed with
  `git worktree remove`.
