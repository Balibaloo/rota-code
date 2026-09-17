# The tooling flow (2026-09-17)

Meta workflow. Roman ruled the order on 2026-09-17 after the post-mortem
of frame 21 (`plans/archive/postmortem-frame21-2026-09-16.md`). This
page is the plan a session reads before it claims a tooling frame.

## The order

```
Session A (done)         Session B                Session C
32 brief batch           29 map                   4 plan, step 2
26 agent types           24 sweep tool              priced by 28
30 gate                                              walked under 31
```

Frames 23, 25, 28 and 31 are measuring frames. Their lines landed in
frame 32. Each closes when frame 4 has run under its rule and the
measurement is on the stack.

## The rules of the chain

- Opus builds, Fable judges. An implementer or a sweeper runs on Opus.
  The session that holds the frame is Fable. It judges by working back
  from the output: the gate on the commit, the findings against the
  known ones, spot reads of hunks. It reads the output in full, never the
  agent's reasoning (ruled: Roman, 2026-09-17; observed: frame 27, Opus
  implemented a briefed stage as well as Fable at nine tenths of the
  tokens, and reviewed only what the points named).
- One session holds one tooling frame at a time and continues down the
  stack until 300k. At 400k it lists the agents and hands off to the
  youngest peer listed, by name, with the frame number and the stack
  commit (ruled: Roman, 2026-09-17).
- A standby peer waits with no frame. Its prime: "You are a standby
  peer. Do not claim a frame and do not read the stack yet. Reply with
  your session id in one line, then wait. A hand-off arrives by message
  from a peer: a frame number and a stack commit. When it does, follow
  the wake steps in CLAUDE.md and claim that frame."
- A session started before frame 26 landed does not see the agent types
  implementer, reviewer and sweeper. It restarts before it claims a
  frame that needs them (observed: frame 29 was unclaimed for this on
  2026-09-17).
- Frame 4 and every frame after the tooling need Roman at the grill.
  The chain stops there while Roman is away.

## Where the reasons are

- Why each tool: the post-mortem, section "What changes", and the
  conversation of 2026-09-17 summarised in each frame's first line.
- Cost anchors: `plans/operating-facts.md`, the register section.
- The known-good run every tool is measured against: frame 21,
  `plans/archive/refs-design-2026-09-16.md`.
