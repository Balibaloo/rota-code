# Bakeoff results — 2026-08-25

Nine candidates, twenty-one fixtures, graders tested in both directions.
Speed via warmed micro-bench (systematically ~2x pessimistic vs live run
telemetry; relative order holds). Full logs: the bakeoff logs of this date.

| model | fit | turn | frame | define | read | challenge | recover | verdict |
|---|---|---|---|---|---|---|---|---|
| **qwen3:8b** (think off) | **full** | 12.5s | **34/38** | **12/12** | 4/5 | 2/3 | 4/4 | **the new understanding engine, pending live-discipline gate** |
| llama3.1:8b | full | 8.1s | 23/38 | 11/12 | 2/5 | **3/3** | 4/4 | stays: suites + delivery |
| gemma3:12b | 76% | 62s | **36/38** | 11/12 | 4/5 | 1/3 | 3/4 | frame-specialist reserve |
| qwen2.5:14b q3 | 75% | 153s | 35/38 | 12/12 | 3/5 | 2/3 | 4/4 | incumbent's judgement, kept for cross-family reads |
| qwen3:4b (think off) | full | **6.2s** | 5/38 | 9/12 | 4/5 | 1/3 | 3/4 | fast tier; not a judge |
| granite3.2:8b | 96% | 31s | 32/38 | 8/12 | 4/5 | 1/3 | 3/4 | honourable mention |
| ministral-3:8b | 83% | 34s | 11/38 | 11/12 | 5/5 | 1/3 | 4/4 | reader, not judge |
| mistral-nemo:12b | 82% | 106s | 13/38 | 8/12 | 1/5 | 1/3 | 4/4 | out |
| qwen3.5:9b | 73% | — | 0/38 | 9/12 | 3/5 | 2/3 | 3/4 | thinking-contaminated; retest someday |

Post-run addendum (2026-08-25): the live click trap ("context" -> "the
environment in which") was rebuilt as fixture `define:context-click` from the
real concordance -- and both qwen3:8b and llama3.1:8b pass it single-shot,
2/2. The live failure happened only on the collision path (the area-scoped
`context#src_click` sense, left unreconciled because its term_collision tick
was quarantined). So the bench-live gap is a *mode* gap: these batteries
measure the model's judgement, not the session shapes; a model can score
12/12 on define and still lose a trap to a quarantined tick. Session-loop
discipline stays the live gate's job.

Findings that outlast the table: the practical VRAM budget on a 10GB card
with a desktop is ~8GB at 12k context, so only <=5.2GB models fit fully;
no model declines gracefully (0-1/2 across the board -- every one defines
"the"); and llama3.1:8b broke the plant 3/3 in single-shot, a reminder
that single-shot verdicts and multi-turn session discipline are different
capabilities -- which is why the winner still faces the live gate.
