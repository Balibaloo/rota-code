# Momentum note of session 3be6b81d, peer name rota-91

Message rota-91 for a context question before you ask Roman. Facts are in
`plans/stack.md`, frames 193 and 194, `plans/frame193-design.md` with its
2.F section and the pass 2c amendment, and the closed frame 190 in
`plans/archive/stack-2026-10-10.md`. The previous note,
`plans/handoff-45fc3fe2.md`, holds the reading that led to frame 193's
design. This page holds the judgement of this session, 2026-10-10 04:38 to
the hand-off.

## What this session did

- Took frame 193 at the standby wake and built it in four passes on two
  implementers: pass 1, the grouping gate and the words door; pass 2, the
  shift question, its page, its three answers, the park and the way back,
  one request per page, and the follow-up rule; pass 2b, the `supersedes`
  regression; pass 2c, seven review findings; pass 2d, three more; and two
  one-line fixes by hand. Five reviews, each on a worktree at the commit.
  The closing commit is 310fb80a. About 1.25M in agents.
- Roman ruled at the wake that a handed frame continues without a check.
  It is in `CLAUDE.md` and in memory.
- Launched night 138 at 09:18 from `C:/Users/roman/rota_night138` at
  310fb80a, cold, the agent principal on Opus, the first night with frame
  190's passes 3c to 3e. Read two cycle lines: neither was frame 193's.
  Pushed frame 194 from the second.

## What I believe and why

- The shift question is the right shape and it is untested on a night. Every
  review probed it on night 137's rows at s292, where it fires once for the
  confirm item and the three answers write what the design says. What no
  probe can show is whether the agent principal on Opus answers `later`,
  `now` or `drop` in words the door maps, and whether the Liaison in the
  new `request_shift` mode sends the page at all. Walk 2 or 3 of night 138
  is the first evidence. Read s-sessions in that mode first.
- The words door is proven on three nights' real answers: 52 more values
  admitted, every one `drop` to contest, none refused that was admitted
  before. The design's claim of eight night 133 answers with "separate
  request" and `drop` was wrong at the door: none reached `rulings.rule`
  as a word. The night 133 shape of frame 185 is therefore caught by the
  shift page or not at all.
- The reviews each found what the previous pass left, and the last high
  defect came from my own brief wording. Reviews earn their cost here.
  Keep one after every pass.

## What to doubt first

- `pending_asks`' hold by reach. It hides an earlier request's asks while
  the shift question is open and while the request is parked. A page that
  reaches both requests is never held. If walk 3 shows the principal a
  page about the old request with no shift page before it, the hold is
  the first suspect, then `held_asks` in `principal.py`.
- `resume_behind`. It fires when the new request's work items are all
  delivered or dropped, or when the request has items and none is work.
  A request with no item yet waits. If a parked item never returns on the
  night, read `item_parks` and the new request's items by kind.
- The converse paragraph on `supersedes`. It was rewritten three times. If
  the Liaison passes `supersedes` on a new request, the shift question
  never fires; if it omits it on a follow-up, the follow-up becomes a
  boundary and asks a question nobody needs. Count both on the read.

## Next, in order

1. Watch night 138 to its end: the watcher script is in this session's
   scratchpad, `watch_night.py`, copied from session 7d45e193's; arm your
   own with `python -I <your scratchpad>/watch_night.py .rota/night138.log
   6900`, background, timeout 7200000. At every CYCLE line, name the frame.
   Stop the night only when it loops on another frame's wall after frame
   193's ratios have their shape, which needs walk 2 at least.
2. At the end, copy `.rota/clickI.db`, its `-wal` and `-shm`, and
   `clickI.principal.jsonl` to the `_night138` names, as operating-facts
   line 684 says. Then one read on Opus: frame 193's three ratios first,
   frame 190's doors by count second, frame 194's two doors third.
3. Frames 185, 186 and 192 close or narrow on that read, as the design's
   table 2.6 and 2.F say. Frame 194 is claimed or narrowed on the same
   read.
4. The four known reds at HEAD and `test_map`'s 10 against 9 predate the
   frame and sit in no baseline since 2026-09-27. A gate's baseline move
   is a one-line frame when a session has room.

## Live agents

- The pass 2 implementer is spent at 347.9k. The pass 2b to 2d implementer
  is at 139.2k, resumable by message, and knows the shift question's code.
- Four reviewers are spent; their probes are in this session's scratchpad
  under `r193p1/`, `r193p2/`, `r193f/` and `r193d/`, with `r193p2/common.py`
  rebuilding night 137's rows at s292.
- The night watcher of this session dies with the session.

## Roman's last rulings, in his words

- 2026-10-10 04:47: "Yes, don't ask when you are handed over to".
- 2026-10-10 04:33: "Why not ask you blocking questions if you're there?
  There's enough context to explain the shift in focus".
