# The build session: review and redesign, 2026-10-29

A fresh Fable session wrote this on Roman's ask of 2026-10-29, read-only,
from `CLAUDE.md`, the composition, reference sections 2 to 13, `handover.py`,
today's design record, the momentum note of 0ce92518, the git log, the stack.

## The result first

The judge spent its context on clerking because the build session is one
seat with four jobs: it faces Roman, it judges, it designs, and it clerks.
Rota has a Liaison and seats, but the build session got "one strong model,
one context, no wiring" (observed: composition.md 95), and every rule since
put work into that context. The redesign splits the seat along the line
the composition draws: a Fable Liaison that faces Roman, designs and
judges, and an Opus Steward that holds the frames and does the day. The
Steward wakes the Liaison through the claim file `handover.py` already
uses, so the Liaison waits at no cost. The design moment is a record and
a step between the cause read and the first pass.

## Part 1. Why the judge never reached the design altitude

1. One seat, four jobs (observed: composition.md 92 to 98). Rota's Liaison
   carries words and judges the route. The build session also clerks. A
   rule, and the root.
2. A status line at every change (observed: S2, ruled 2026-09-14). The
   judge wrote 32 lines in five hours, and 62 of 78 commits were
   `docs(plans)` (observed: `git log` 04:50 to 10:30). A rule.
3. The session writes the fix brief by hand (observed: C32, C33, C39).
   Eight briefs, 519 lines, sit in the judge's scratchpad. The report is
   capped at ten lines (C43), the brief is not. A rule with a missing half.
4. Merge, re-record and worktree are session steps (observed: M4, C54, the
   note's eleven worktrees). Seven merges each landed a re-record in the
   context. An absent clerk step.
5. No design moment between cause and fix. Section 10 goes find, match,
   read, match, re-read, build (observed: C76). Step 3 asks for "a
   proposal at the smallest place" from "what the code already holds", and
   the memory of 2026-10-26 bound the read to the code. Today's design
   record says it: "a read bounded by the code could not produce it"
   (observed: its last section). An absent step, plus a rule that scopes
   the read.
6. A handed frame continues without a check (C28, 2026-10-10), never idle
   (C2, C4, 2026-09-30), fixes outpace walls (CLAUDE.md). Together they
   start the inherited pass at once, and no step asks the shape before
   pass 1 (reasoned: passes 2 to 7 kept pass 1's shape until Roman asked).
7. C40 caps a sprint at twenty cycles "because every report lands in the
   session's context" (observed). A rule that treats the symptom.
8. A Fable session lasts one night, so the costliest model rebuilds the
   picture from a note and a 5,707-line stack six times a week (observed:
   the note, `wc -l`; reasoned: the cadence). A cadence, not a rule.

## Part 2. The redesign

### The parties

- The Principal. Unchanged. He speaks, he rules, he writes nothing.
- The Liaison, Fable, one resident context. It faces Roman alone, records
  his words and its confirmed reading, chooses a shape from a design
  record, judges a close record, and drafts every question to him. No
  status line, no brief, no merge (reasoned: Roman, 2026-09-17).
- The Steward, Opus, one resident context. It holds the frames, writes the
  pass briefs from the design record, launches agents, reads the ten-line
  reports, merges, re-records, writes the status and reach lines, and
  keeps the worktrees. It never faces Roman and never chooses a shape
  (reasoned: causes 2 to 4 are clerical).
- Agents, Opus, cold, as today, plus one design agent.
- The reserve: two pools, one per model (observed: C13, a standby
  continues a seat and never widens it).

### The records and their writers

- His words and the confirmed reading: the Liaison. Unchanged.
- The design record, `plans/design-<seam>-<date>.md`: the design agent
  writes the implemented facts, the axes, the shapes with cost, failure and
  measure, and "What the scope excluded". The Liaison writes one line under
  it, the chosen shape and why (reasoned: today's record is the template).
- The pass brief: the Steward, thirty lines at most, pointing to the design
  record and the reach line (reasoned: today's briefs restate the design).
- Status lines, reach lines, merge and re-record counts: the Steward.
- The close record, five lines per frame: counts before and after, the
  reach reader, the review verdicts, the doubt. The Steward writes it, the
  Liaison judges it (reasoned: C43 gives a worker ten lines).
- The Liaison's momentum note: judgement and open choices. The Steward
  hands with the state print only (reasoned: it holds no judgement).

### The flows

Intent flows down: Roman, the Liaison's reading, the chosen line on the
design record, the Steward's brief, the agent. Evidence flows up: ten
lines from the agent, a close record from the Steward, one line at
altitude from the Liaison to Roman. The Steward asks the Liaison through a
record. The Liaison asks Roman one question with a recommended answer.

### The design moment

It sits between steps 3 and 6 of section 10, before pass 1 of any frame
that changes a seat's call, a page form, a door set or a law. The Steward
launches the design agent with the cause read, the provenance read, the
composition page and the laws the seam touches. The brief carries no scope
to the code's shape and demands the excluded section. The Steward wakes
the Liaison, which reads the record, about 5k, and writes the choice or
one question back (reasoned: M20; today's record chose in minutes a shape
five passes had not).

### The wake moments of the Liaison, and what it reads

1. Roman speaks: his words and the state print.
2. A design record waits: the record only.
3. A close record waits, or a count fell: the five lines, and the review
   file for a judgement case only.
4. A question to Roman is needed: the Steward's facts at the frame.
5. Once a day: the state print and the close records since the last wake.

A claim file addressed by session id wakes an idle session in six seconds
at no token cost (observed: handover.py docstring). The claim gains a
record path beside the frame number, and the Liaison arms the standby's
watcher. Between wakes it spends nothing.

### The hand-offs and the price

Each seat hands at 300k to a standby of its own model, and `hand` picks by
model. The Steward takes in about 30k from the state print. Tonight: about
300k of Fable for 25 cycles and seven branches, 43k per branch (observed:
the brief, the git log). Under the design a Fable day costs his turns,
assumed 40k, four design records at 8k, seven closes at 4k, one daily read
at 10k: about 110k (reasoned, the sizes assumed). The Fable hand-off falls
from one a night to one in three days, the Steward hands once a night at a
tenth of the take cost: one more hand-off a day, the costly kind down by
two thirds.

First measure: Fable context per landed branch, 43k tonight, under 15k in
the first week. Second: frames whose pass 1 follows a design record with an
excluded section, 0 of 7 tonight.

### Roman's two proposals against this design

An Opus Liaison with Fable beside it. Right: the clerking leaves the Fable
context, and Fable is woken at moments. Weaker: the Liaison's first job is
to infer his intent and judge the route, the reasoning he ruled only Fable
does (ruled: 2026-09-17). An Opus Liaison asks him more, which spends the
scarcest budget, and two seats beside him break "one seat faces the
Principal" (observed: composition.md 25). Move the clerking down, not his
face.

Opus on the day as the standby, a new Fable above. Right: this is the
design's shape. Weaker: "as the standby" joins the reserve with a role, and
the reserve continues a seat and never widens it (ruled: 2026-09-20, C13),
so the Steward is a seat with its own reserve. And the wake is unnamed: a
Fable that sits in the conversation spends context on every exchange, and
one never asked never designs. The design adds the claim-file wake, the
design record as the unit that wakes Fable, and the close record. Neither
proposal names the design moment, and his first ask was that moment.

## The amendments to the method page

- composition.md, the build session: two seats, the Liaison on Fable and
  the Steward on Opus, and the Steward never faces Roman.
- Section 3, C28: a frame with no design record gets the moment before
  pass 1.
- Section 10, C76: step 3b, the design moment, with no scope to the code
  and a required excluded section.
- Memory 2026-10-26, a general solution from what exists: binds the read,
  not the design.
- Section 5, C43: the Steward writes the brief, thirty lines, pointing to
  the design record.
- Sections 6 and 8, S2: the Steward writes status lines, and the Liaison
  judges a design record and a close record only.
- Section 12: two reserves by model, and `hand` picks the sender's model.
- Section 13: a claim carries a record path, and the Liaison arms the
  watcher between wakes.
- CLAUDE.md: "never idle" binds the seat that holds frames, the Steward.

## The question Roman must settle first

He ruled on 2026-09-30 that a session is never idle, after one sat at
356k with no frame. This design departs from it: the Fable Liaison waits
on a watcher between wakes and holds no frame. Does "never idle" bind the
seat that holds frames only, so the Liaison may wait? Recommended: yes.
The ruling protected frames that waited unclaimed. Here the Steward holds
every frame, and an idle Liaison costs nothing and keeps its context.

## Ruled, 2026-10-29 about 11:0x, Roman in the terminal to rota-21

On the first question, the idle rule: "Oh no that idle rule was to prevent meaningless waits". So the rule of 2026-09-30 binds a session that holds context and nothing to do; a Liaison that waits on a watcher at no cost is not idle in his sense. He then said "Interesting so the problem shifts", on the Steward: a resident Opus context fills as the Fable context did. The session's reading, not his: the Steward is not resident; a worker wakes cold on one frame from the reserve with the frame block, the design record and the choice line, lands, and ends, so nothing accumulates but records. Measure: Fable context per landed branch, worker context per frame.
