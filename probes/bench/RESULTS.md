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

## The mixture-of-experts question, answered

A sparse model breaks the rule the table above is built on -- "fits fully
or decodes at a twentieth the speed" -- because only a few billion of its
parameters are active per token, so the experts can sit in system RAM and
be paid for only when used. If that held, a 10GB card could run 30B-class
judgement. Measured, it does not.

| model | fit | turn | frame | define | challenge | read | recover |
|---|---|---|---|---|---|---|---|
| qwen3:30b-a3b | 40% GPU | 79.6s | 17/38 | 13/14 | 2/4 | 4/5 | 3/4 |
| qwen3:8b (think off) | full | 12.5s | 34/38 | 12/12 | 2/3 | 4/5 | 4/4 |

Six times the turn and half the frame score. A small onboarding goes from
nineteen minutes to two hours.

The interesting half is *which* number died. Decode held up at 8.3 tok/s --
the sparse trick works, and a model twice the size still writes at a usable
rate. **Prefill collapsed to 92 tok/s**, against 4,165 for the dense 8B on
the same card. Prefill is compute-bound rather than memory-bound, so the
60% of the model sitting in RAM has to be walked for every one of the
prompt's four thousand tokens before a single one comes back: forty-three
seconds of reading before the thinking starts. This system's prompts are
long by design -- the whole push architecture exists to put the right
material in front of a session -- so it is precisely the wrong workload
for a partially offloaded MoE.

Sparsity buys generation, not comprehension, and onboarding is nearly all
comprehension. The rule survives with a sharper edge: what matters is not
whether a model fits, but whether its *prefill* fits.

**A third caveat, and it is the one that bites: temperature zero is
deterministic within a model load and not across two.** Measured on the
challenge battery -- the identical prompt, byte for byte, the same model,
the same pins -- llama3.1:8b answered 3 of 4 in one process and 1 of 4 in
another an hour later, and three repeats inside each process were
identical every time. So a score is a fact about a load, not only about a
model.

What survives that: differences measured back-to-back on one loaded model,
and differences far larger than the drift. The frame column is safe --
34/38 against 5/38 is not a load artefact. The narrow columns are not:
challenge at four items moved two of them across loads, so a 2/3 against a
3/3 there says nothing. Read the small batteries as ordering evidence only
when the arms were interleaved in one process, and grow them before
reading them any other way.

Two caveats this table now carries, both found by using it:

**The challenge column pre-dates a rename.** These scores were taken with
the third verdict named `challenge.unfounded`; it is `challenge.dismiss`
now, because the vocabulary law caught an adjective in a verb slot. Whether
the verb changes what models reach for is measured separately -- and the
fixtures are re-snapshotted, so the next run of this table measures the
brief production actually sends.

**Half the battery snapshots a brief and half does not.** `challenge`,
`define` and `orient` fixtures carry the composed production brief;
`frame`, `read`, `recover` and `decline` carry compact hand-written
probes. Both are deliberate -- the production frame brief asks for
`frame.assign` tool calls, and parsing thirty-eight of those well enough
to score would make the grader the thing under test -- but the mix was
invisible until a brief edit aged four fixtures silently. Every fixture
now declares its origin and a test holds the snapshots to their briefs.

The re-bench worth running is not this one again. Nine candidates was the
right shape for the question "what fits and what judges"; that question is
answered. The next one is narrower and later: the three or four models
that fit fully, against a battery that has grown more real cases, with
every live failure since turned into a fixture.

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
