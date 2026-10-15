# Questions put to Roman that an earlier ruling already answered

This record is task F of frame 251's research. Each row is a question that
went to Roman, or nearly went to him, while a ruling or a design already held
the answer. It recommends nothing.

Sources: `plans/stack.md`, `plans/archive/*.md`,
`plans/operating-facts.md`, `CLAUDE.md`, and the build transcripts (session
ids of eight characters). Transcript times are UTC. Record times are local,
one hour later.

Counts: 9 rows asked to Roman, 3 rows dissolved before the ask.

## Asked to Roman

| # | The question | When asked | The earlier ruling, its date and words | Source |
|---|---|---|---|---|
| 1 | Frame 114, a failing inherited test has no route: change the door? Asked in the grill with three options. | 2026-10-04 14:18, again 14:28, session 419281dc | 2026-09-14: "a broken project test is the Developer's own regression, restore the code" (record paraphrase, f4d7d4f after night 47). Roman first answered "investigate this with a sub agent", then "whats the question here?". The read showed the doors already permit the restore. | `plans/stack.md:1234`, `:1240`, `:1242` |
| 2 | Frame 115, the Architect's answer to an escalation carries no words: the row route? | 2026-10-04 14:20, session 419281dc | Law 2 of 2026-08-09, "conclusions travel, reasoning stays home". Discussed again on 2026-10-03. Roman answered "investigate our decisions, previous thoughts etc" and then "we have already discussed this, use a subagent to search our decisions logs, etc ie meta" (14:34). | `plans/stack.md:1252`, `:1257`, `:1259`; `plans/frame115-history.md` section 7 |
| 3 | The note at the merge: "Two pieces: the Architect reads the batch's defaults ... Which do you want?" | 2026-10-12 22:31 UTC, session 31e55586 | 2026-10-11 15:44 "Start as written" and 15:49 "Every default" (frame 204's design, law 8). Roman replied "yeah but not just defaults, the architect reviews all notes and escalates and thats what blocks the work, is that right? is the architect right for everything?". A peer then wrote that the design already answers it, section 2 and section 6, one strike on the history rule. | 31e55586 AUQ; `plans/stack.md:572`, `:573`; peer message of 2026-10-12 22:32 UTC |
| 4 | "[med] A default the seats took and never showed you ... What happens to that note at the merge?" and "these are non blocking notes?" | 2026-10-12 22:27 to 22:29 UTC, session 31e55586 | 2026-10-11 15:00: "thats where the categories of note come in because some categories do and some don't". Roman answered "ok, so these are non blocking notes? how important are they?" and "so it should be part of architect review right?". | 31e55586 AUQ; `plans/stack.md:566` |
| 5 | Frame 198's "waits on Roman's ruling" line: what a page carries after a merge. | Carried on the stack to 2026-10-12 | 2026-10-11 15:44, "Start as written", frame 204's design section 11, Q2. The peer wrote: "Frame 198's 'waits on Roman's ruling' line is stale". | Peer message 2026-10-12 22:32 UTC to 80cae596 |
| 6 | Frame 63's walk: may the night run? Held for his word each time. | Twice on one day, before 2026-09-22 19:28 | No earlier ruling. The repeat itself drew the ruling: "You have signoff to run the nights" (2026-09-22 19:28). | `plans/operating-facts.md:171` |
| 7 | A re-record lost 10 of 10 greens on `L1-TE-survey-an-area-for-its-terms`. Does the cheap re-record rule hold? | 2026-09-20 23:16 UTC, session cb5428a2 | 2026-09-20, "A re-record runs without asking" (record paraphrase). Roman answered "Re-record freely, keep the rule". | cb5428a2 AUQ; `plans/archive/stack-2026-09-22.md:1065` |
| 8 | "[high] What tells a cheap fix apart from one that only fits tonight?" | 2026-10-15 10:54 UTC, session dae006d1 | Roman answered "I thought that this is the kind of knowledge that we just have about the project. Use opus to do deep research". The earlier words: 2026-10-15 00:54 UTC, "I want to prevent over fitting ... theres only so many kind of changes we can make". | dae006d1 AUQ; 4754aaec typed |
| 9 | Frame 90 or frame 89: "Which do I claim now?" | 2026-09-28 01:12 UTC, session b4768744 | The order of 2026-09-27 (frame 89, the gate repair, ruled before batch B, 18:44 UTC "The gate re-records its stale set") and the hand-off. Roman answered "We're you not handed off to properly?". The earlier order's exact words are not found. | b4768744 AUQ; 213e58fd AUQ |

## Dissolved before the ask

| # | The question | When | The earlier ruling, its date and words | Source |
|---|---|---|---|---|
| 10 | Frame 144's budget: does the price above the frame's line block on Roman? | 2026-10-05 11:41 | 2026-09-17, "budget is a useless escalation signal", and 2026-09-18, "i dont care about opus costs". The history read dissolved the question. | `plans/archive/stack-2026-10-07.md:94`, `:95` |
| 11 | Frame 204's [med] question of 06:41 on a rename nobody asked for. | 2026-10-13 06:41, withdrawn 06:53 | Frame 204's design, category 4. The history read: "the question dissolves". | `plans/stack.md:618`, `:619`; `plans/frame204-history-read.md` |
| 12 | The gate's stored baseline: does it move? The implementer asked twice. | 2026-09-24 | No ruling found. The record calls it "Roman's call, not a frame yet". | `plans/archive/stack-2026-09-24.md:331` |

## The rules that came from these repeats

- 2026-10-03: an agent reads the records for a prior ruling before a frame
  blocks on Roman. The cause was frames 114 and 115 (ruled: Roman,
  2026-10-03, `CLAUDE.md`).
- 2026-10-04 14:52: before any question, an agent answers what the records
  say and whether the recommendation holds. The cause was session 419281dc,
  which asked two inherited questions, "yeah add it" (ruled: Roman,
  2026-10-04, `CLAUDE.md`).
- 2026-09-22 19:28: the nights need no ask, after frame 63's walk was asked
  twice (ruled: Roman, `plans/operating-facts.md:171`).
- The memory file "rota history before escalation" counts 3 strikes by
  2026-10-12. Row 3 is the strike that the peer of 2026-10-12 wrote.

## What the scan did not find

- The transcripts hold no typed message with "I already", "as I said",
  "already told" or "we discussed". His pointers back are in `AskUserQuestion`
  answers (rows 2, 3, 8, 9) and in the records.
- No record uses the words "taken by timeout" for a question that a ruling
  already answered.
- Row 9's earlier ruling is inferred from the order of 2026-09-27. No record
  line was found that names it.
