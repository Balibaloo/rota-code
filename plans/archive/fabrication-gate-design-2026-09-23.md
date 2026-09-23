# Design record: the runner runs nothing from a made-up turn, and never points at a deleted answer (frame 77)

Written by the assistant, session dba7e375, on 2026-09-23 16:40, for a
design review before any code. Meta workflow for the build. Rota workflow
for the fault. The tree is `d84825c`.

## The fault (observed: frame 75, `plans/archive/stack-2026-09-23.md`)

1. `_fit` evicts an earlier result from the prompt and leaves a notice,
   `re-read anything you still need` (`rota/core/runner.py:557-561`).
2. The seat asks for the result again. On night 86 the runner answered
   `the answer is above`. Today it answers `What X returned then still
   stands` on the second asking and `Use what X returned earlier, or finish
   without it` on the third (`:2660-2704`). Both point at a result the seat
   cannot see when it is evicted.
3. The seat invents the result in its reply and writes from memory.
4. The runner flags the reply, `wrote its own tool results` (`:2419-2425`),
   tells the seat nothing behind those lines ran, and then dispatches every
   parsed call (`:2426`, `:2519`). The hold at `:2510-2514` fires on a fresh
   read only, and a repeat is not fresh.

Every local model on the box invents under the same pointer (observed:
`probes/frame37/replay_runner.py`, 2026-09-23). The counters of frame 76
say the runner ran a write in the turn after a fabrication on nights 70,
86, 87 and 90, and night 70's merge `3c17d35` is one of them.

## Rule 1: a turn's calls run up to the first invented result, and every call after it is held

- The parser already yields the calls in order. Find the offset of the
  first `FABRICATED_RESULT` match in the completion. A call whose text
  starts after that offset is held, through the existing `held` and
  `held_calls` path at `:2510-2514`, and is not dispatched. A call before
  the offset runs as today.
- The feedback keeps the fabricated line and adds one line that names the
  held calls, in the form the held tail already uses. The real results of
  the calls that ran follow. The seat acts on them next turn.
- Why hold and not refuse: the calls after the invention were built on the
  invented result. The seat must re-decide them with the real result in
  view. The held-tail rule already says a new turn's calls supersede last
  turn's held tail (`:2412-2417`), so nothing is re-sent for the seat.
- Edge: the invented result comes before any call. Then every call is held.
- Edge: a `code.write` runs and its `code.commit` is held, because the
  invention sits between them. The write's result says `written, not
  committed`, and the seat commits next turn.

## Rule 2: an evicted result is served again, and a refusal never points at a deleted answer

- Today a result is served at most twice per key: on the first asking and
  once more after an eviction (`:2620-2624`). The third asking is refused
  with `asked three times this session and the answer has not changed`,
  and the line `Use what X returned earlier, or finish without it` is
  reached in exactly the evicted case (`:2655-2662`).
- The rule: when the key's result is not in the prompt the seat has just
  read, the runner serves it again, at the result cap. The refusal counter
  applies only when the result is in the prompt, and its sentence says so:
  `the answer is in this prompt`.
- The concern the code records (`:2610-2620`): the eviction notice is
  sticky, so a test on the notice alone reads evicted for ever, and night
  88's `s137` was served in full at turns 7, 8 and 9 and died on the
  identical-turn stop. So `evicted` must be per key, true only when that
  key's block is gone from the prompt. The review's point 1 says whether
  it is per key today.
- If a result is larger than the room `_fit` leaves, serving it again every
  turn evicts it every turn. Then the runner serves it at the result floor
  and says the room is the limit. That case belongs to frames 53 and 56 and
  is named here so the walk can tell it from this frame's fault.

## Pinned tests

1. The recorded shape of `s145` turn 6: a source call, an invented result,
   a write and a commit in one completion. The source runs, the write and
   the commit are held, the feedback names both, and a write in the next
   turn dispatches.
2. An invented result before any call: nothing runs, the feedback names
   every call as held.
3. A key served at turn N and evicted by `_fit` before turn N+1: the
   asking at N+1 is served in full with no refusal line. The asking at N+2
   with the block present gets the unchanged line.
4. The third asking of a key whose result is in the prompt is refused, and
   the refusal says the answer is in this prompt.

## What the frame retires

The runner's own count of the hole, 8 of 8183 prompts, lived in a comment
at `8b15af8:2093-2106` and gated the decision to leave it open. Frame 76's
counters replace it. A comment that carries a measurement names the
counter that keeps it current.

## Not in this frame

The criterion wall, the test wall and the write door of frame 38. The reply
cut of frame 47. The obligation restatement of frame 61. Frame 76's counter
c counts a notice beside any repeat refusal, not the refusal of the evicted
key, so it is an upper bound. The review says whether the walk can accept
on it as is.

## Acceptance

The gate green with the stale line read. A diff review on a worktree at the
commit. A full night from a worktree at the closing commit. Its counters
read zero writes run after a fabrication and zero commits. Its outcome is
read against night 86's.

## Points for the design review

1. How is `evicted` computed, per key or per prompt? Quote the lines. If it
   is per prompt, name the cheapest per-key test.
2. Can `FABRICATED_RESULT` match inside a call's argument, such as a
   `code.write` whose text holds a line `OK x.y: ...`? Count the recorded
   completions in `tests/rota/cassettes.db` where the first match sits
   inside a `text='...'` span. Say whether the offset test needs to skip
   argument spans.
3. The held-tail semantics: quote how `held` is rendered and whether a held
   call is re-sent by the runner or only by the seat. Say whether holding a
   `code.commit` after a dispatched `code.write` leaves a state the next
   turn cannot recover.
4. Attempt accounting: does a held write count as a Developer that wrote
   nothing for the write door and the attempt cap? Quote the door's counter.
5. The `oneshot` path: rule 1 must hold there too. Which seats run oneshot,
   and does the hold path exist for them?
6. Night 90 ran with today's second serve in place and still had 37
   sessions that invented and 8 writes run after. Read two of those
   sessions' turns and say what the seat was shown before it invented. This
   bounds what rule 1 buys against rule 2.
7. The fixture: name the existing test that drives `run_session` with a
   scripted completion, so the four pinned tests copy it.
8. Anything here that contradicts the composition's Records or Flows lines,
   `plans/composition.md`.

## The design review, 2026-09-23 16:45 (observed: a reviewer agent, read-only, 120k on the harness line against 100k, 62 calls)

Both rules sound with named changes. What the review settled, and what
the build takes from it:

- `evicted` is per key today (`runner.py:2583-2585`: the notice stands,
  the key was answered on an earlier turn, and its rendered result is not
  in the prompt). Rule 2 needs no new test for it.
- **Night 90's eight writes run after a fabrication had the real result
  in the prompt every time.** No seat invented after a pointer to an
  evicted answer. So rule 2 buys nothing on night 90's eight, and rule 1
  carries the walk. In five of the eight the invention precedes the write.
  In three the write precedes the invention, built on real reads, and the
  seat invented only the write's own result.
- **Finding 1, high.** The stood-by path at `runner.py:2334-2349` runs
  every held call when the seat replies with prose. Rule 1 must hold the
  invented tail in a list that path never runs, or "Done." after an
  invention lands the from-memory write. Pinned: invention, then "Done.",
  nothing written.
- **Finding 2, high.** `tests/rota/test_runner.py:709-738` and `:741-760`
  pin the refusal of the third asking while the eviction stands. Rule 2
  serves it. The frame rewrites both tests to the new bound.
- **Finding 3, high.** A result over the exchange room reads evicted every
  turn, and an unbounded re-serve repeats night 88's `s137`. The build
  bounds the evicted re-serve: a key is served at most three times in a
  session, and the refusal after that says the result does not fit the
  room and asks for a narrower span. It never says to use what the call
  returned earlier.
- **Finding 4, high.** Counter b of `rota.tools.nightcount` counts by
  turn, so it cannot read zero when a write precedes the invention by
  design. The build refines it: writes whose call sits after the first
  invented result, with the by-turn total kept on the same line.
- **Finding 5, low.** `extract_lenient` at `rota/llm/toolproto.py:931-937`
  computes call spans and drops them. `find(raw)` misses 16 of 1263
  `code.write` calls and resolves 744 duplicate raws to the first copy.
  The build takes positions from the parser.
- **Finding 6, low.** Under `ROTA_ONESHOT` the hold path does not exist
  and a write ends the session at `runner.py:2791`. The flag is off on
  every night and in the suite, on for a bare `walk.py`. The build gates
  rule 1's hold apart from `oneshot` and skips that break while an
  invention hold stands.
- Attempt accounting: a held write that is never re-sent leaves the
  session barren, one attempt on the tick key (`loop.py:325`, `:515-519`).
  That is the right count for a from-memory write.
- Fixtures: `test_runner.py:340-371` for the scripted backend and the
  fabrication line, `:1292-1316` for the Developer write and commit with
  the `worktree` fixture, `_evicting_repeats` at `:695-706` for the
  eviction shape.
