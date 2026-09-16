# Post-mortem of frame 21 (2026-09-16)

Meta workflow. Written 2026-09-17 by session 32a42b78 (rota-b9) for Roman.
Frame 21, provenance by reference, ran from the hand-off at 12:55 to the
close at 19:08: 373 minutes, 14 agents, 3.46M agent tokens reported and
about 0.6M more in four sweep sub-agents that reported none, and 244k of
the assistant's own context at the close (observed: the agents' usage
lines, the commit clock, `/context`).

## By activity

Wall minutes overlap, since agents ran beside each other. The call says
what the same result would have cost with what we know now.

| Activity | Wall min | Agent tokens | Call |
|---|---|---|---|
| Scope and diagnosis (2 agents) | 31 | 510k | Necessary. The scope made the design twelve answers. The diagnosis overturned the assistant's wrong cause. |
| Implementing, four stages | 155 | 1.32M | Half avoidable. Each stage was a cold agent that re-read the api file, the scope and the design: about 0.5M of re-reads that one resumed agent would not pay. |
| Test sweep of 48 files (4 sub-agents) | 30 | about 0.6M, not reported | Avoidable. A script does a mechanical sweep. The drop that forced it could have been a later, cheap frame. |
| Reviews, read-only (3 agents) | 44 | 731k | One third necessary. Two of 25 findings mattered (a writer that stamped nothing, an old database that regressed silently). One review of the whole diff finds both. |
| Fix cycles (3 agents) | 94 | 569k | Necessary given the findings. Fewer, larger passes shrink it. |
| Docs and the brief (1 agent) | 25 | 161k | Necessary. |
| Recorder and walks on the GPUs | 136 | 167k | The recorder (20 min) necessary. The Titan walk (17 min) avoidable with the fact "Titan is five times slower" on record. The cycled walk (65 min) necessary in hindsight: it found what no case or review saw. |
| Suite replays inside the agents (12 runs) | 90 | about 250k, inside the rows above | Avoidable in part. Tracebacks of 22 known reds were read twelve times: `--tb=no -rf` cuts the tokens; temp databases on the SSD cut the minutes. |
| Recovery from the assistant's mistakes | 30 | about 10k | Avoidable with three rules: the clock before a status line, the turns before a cause, the STALE set in every acceptance. |
| Coordination: stack, design record, briefs, reports | 373 | 244k (the assistant) | Necessary. Nine status lines, fifteen record commits, fourteen briefs, fourteen reports. |

Total avoidable with what we know now: about 1.8M of 4.1M agent tokens,
and about 100 minutes of wall (reasoned: the sums of the avoidable calls
above).

## By who decided

| Who | Decisions | Overturned later | By what |
|---|---|---|---|
| Roman | 3: the frame's ruling, the 3080 first, move the walk off the Titan | 0 | |
| The assistant | 21: Q1 to Q12, the stage split, a review per stage, three "accept as designed", two cuts (the audit rule, an empty answer lands nothing), Q11 parked, the GPU split | 3: the cause of the cycle (by the diagnosis), the status times (by the commit clock), the acceptance rule (by the missed STALE case) | The turns, the clock, the next agent's suite run |
| The agents | 34 reported deviations from a brief, each with a reason | 4 | The reviews |
| The reviews | 25 findings, 2 high | 5 accepted as designed by the assistant, with a reason | The assistant's judgement, on record |
| The walk | 1: silence was consent, and a door read a negation as a difference | 0 | |

The one defect that reached the composition (silence as consent) was
found by the walk alone. No case renders it, no review traced it, and
the old code had shipped it for seventy nights.

## What changes

1. One implementing agent per frame, resumed across passes until its
   context is spent. Scripts for mechanical sweeps.
2. Frames that fit one pass. An ends-when that demands a drop splits into
   "stop the writes" now and "drop the columns" later.
3. One review per frame, on the whole diff, for frames that touch the
   write pipeline, the schema or a predicate.
4. A walk in the ends-when of any frame that touches the seats.
5. A gate the assistant runs itself: FAILED against a stored baseline and
   the STALE set, five lines out.
6. A token budget in every frame's five lines, and the count every turn.
7. Suite runs with `--tb=no -rf`; temp databases on the SSD.
8. Three rules for the assistant: the clock before a status line, the
   turns before a cause, the STALE set in every acceptance.
