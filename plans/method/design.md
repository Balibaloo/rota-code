# The build session's context across sessions: the design

Frame 287's record, revision 7, written by session bf5baa63 on Fable on
2026-10-18 between 02:20 and 02:40, from Roman's words in the terminal
from 01:27 to about 02:35. It replaces the six revisions in
`plans/frame287-design.md`, which stay as history. Meta workflow. One
page. Where a line is his, it carries (ruled); where it is the session's
reading, (reasoned); where it is a measurement, (observed).

## 0. The premise

The build session is one strong model above a harness. It is not a seat
of rota, it has no wake, and it takes the whole stack on its turn (ruled:
Roman, 2026-10-18 01:27). It designs its own context (ruled: the same).
Roman's words are persisted for their intent and found whenever a model
looks for an answer, and never forced onto a model each turn (ruled: the
same). Nothing blocks on him for sessions at a time; the sessions work
through the backlog (ruled: Roman, 02:33). A handover is a real handover:
seeded by a note, completed by a dialogue the taker opens when it needs to
(ruled: Roman, 02:25). Agents are the membrane of the session's context
(ruled: Roman, 02:25, "yes thats why I want you to use subagents").
Context occupancy is the measure, not tokens (ruled: Roman, 02:25).

## 1. Four facts about the session that the design respects

1. Every session is a cold read, and the first page it reads sets its
   frame. Tonight's first page was a procedure, and the session followed
   steps (observed: this session, 2026-10-18).
2. It reasons well with few things held with their why, and badly with
   many imperatives held apart.
3. Whatever a tool result pulls in stays for the session. The take cost
   35k from a 3,700-line stack (observed: the count hook).
4. It retrieves well with a key in hand and badly from a story. The frame,
   the file, the door and the law are the keys; a question's words are not
   (observed: frame 293, 0 of 11 by words, 2 of 11 by the frame key).

## 2. The layers

**The intent page, `plans/method/intent.md`, about 1k tokens.** What rota
is for, in the composition's words, and how Roman works with the session:
grill one question at a time with a recommended answer, check his claims
against the records and the code before acting, say what a frame changes
in rota's terms, Simplified Technical English, no narration. Intent is
versioned by amendment and not by time: a later word of his wins only
where it amends, and the page records the amendment with its date
(reasoned: the composition, "only a ratified amendment revokes"; ruled:
Roman, 02:30, recency is not the point). The page changes only on his
ruling. A session that wants a change writes a proposed amendment to
`plans/method/amendments.md`, which he reads when he returns (reasoned:
the drift guard; the brief grew to 75 rules over sessions without him).
This page is the first thing a session reads, before the state.

**The state page, printed by a tool, about 3k.** `python -m
rota.tools.state` prints from `plans/stack.md` in place: the held frames
with what each changes in rota's terms, the live agents and nights, the
open decisions with their rating, and the leaving session's doubts. At most
ten live things. No rulings: a resolved ruling lives at the thing it rules
(section 2, rulings at the thing). The stack stays the history behind the
print, and nobody reads it whole (reasoned: layer 3 of section 1).

**The handover, a dialogue.** The leaving session writes the momentum
note, `plans/method/handoff-<sid>.md`: its reading at altitude, what it
believes and doubts, what is live. It hands at about 350k and keeps the
last 50k to answer the taker (ruled: Roman, 02:30, "maybe last 50k not
100"; this amends the ruling of 2026-09-27 that the last 100k belongs to
the frame). The taker reads the intent page, the state print and the
note, forms its own reading, and messages the leaving session for what the
note withholds or what it doubts, as an option and not a step. The taker
owns the stack from its first status line; the leaving session stops when
released. The note leaves the repository when its frames close.

**Agents as the membrane.** Nothing bulky enters the session's context:
no file, no stack, no night database. The session asks a question with a
cap, and an agent reads and answers with pointers and marks, to a file
under `plans/` or the scratchpad, with ten lines back. "What rules this
door and what did we decide about it", "what did this night give frame
283", "where are we". Implementers and reviewers stay as they are, one
implementer per frame resumed by message, one read-only review per code
pass. A synthesis, a page drafted from many sources, runs in two levels:
extractors, each blind to the others and capped, to files; one
synthesiser that reads the files and writes the page; the session judges
the page and never the sources (ruled: Roman, 02:35, "super important";
reasoned: the low-frequency method, synthesis not summary). An agent
spawns sub-agents only when its brief allows it, with a cap each.

**Tools that enable and never gate.** A step a model must remember at a
moment is a defect; a tool does the step or prints the next one, and never
refuses the session (ruled: Roman, 02:25, "enabling not inhibiting"). The
set: `handover.py` as it is, with the dialogue; `state`, above; `status`,
one line with the clock, appended and committed by pathspec, with
`--ruling` writing his words at the frame; the night's launch and stop;
the gate from a worktree with the register copied in; the cycle read's
brief. Each tool's rule leaves the brief when the tool lands.

**Rulings at the thing.** A ruling about a door lives in the door's
comment with its law line, and in the law. Frame 114 recurred five times
because the door's comment named nights 47 and 48 and never law 12, so
every reader saw the failure and not the rule (observed:
`plans/frame114-history-read.md`; frame 293). `rota/tools/rulings.py`
stays as the search by frame, file, door and law for an agent's use. No
ledger (observed: frame 293's counts).

**The frame economy.** At most ten live things on the state page. Parked
work is one ranked line each in the archive's parked section. A night
pushes nothing by itself: its read ranks the walls, and the holding
session pushes what it will hold next (reasoned: sixty open frames is a
backlog wearing a state's name; three frames were pushed from one night's
cycles tonight).

**Autonomy.** Nothing blocks on him for sessions at a time (ruled: Roman,
02:33). A question keeps its rating, high, medium or low, and the low
timeout, as today (ruled: Roman, 02:35, "keep the same high, med, low
system"). A session decides the rest under a stated assumption, written
where the decision is. When he returns, `python -m rota.tools.state
--since <date>` prints what closed, what was decided under assumption,
what waits on him, ranked (reasoned: his attention is the scarcest budget,
and a return should cost one screen).

**The measure.** Context occupancy, which the count hook gives each turn
(ruled: Roman, 02:25, "context right? tokens dont really matter"). Agent
tokens are spent freely against it. The take should cost about 5k, the
brief about 1k a turn, a cycle about 3k.

## 3. What the existing records become

The composition page stays the centre, and the intent page is its
build-session paragraph at the next resolution. `CLAUDE.md`'s first
section becomes the intent page plus a pointer, in one sweep (ruled:
Roman, 02:35, "double check reasoning, then yes"; the check is in section
5). Its 75 rules go to `plans/method/reference.md`, keyed by the moment
they fire at, each with its origin and its tool when one exists.
`plans/operating-facts.md` and `plans/wall-guide.md` stay as the agents'
reference. The stack stays as history and the archive grows. The memory
directory keeps the user's cross-project preferences; the rota rules in it
move to the reference. `plans/stack.md`'s head rules move to the reference
too. `rota/LAWS.md` and `rota/DECISIONS.md` are rota's and do not move.

## 4. How we would know it works

A taker's state reply cites nothing it did not need and asks the sender
or Roman only what the records do not hold; the take costs about 5k
(observed: 35k tonight); the brief loads about 1k (observed: 8.4k); a
session runs about twenty cycles with the count under 300k at the
twentieth; a question that a record answers reaches him 0 times over
three sessions, read on the residue rule; and the live count on the state
page stays at or under ten.

## 5. The one-sweep check

The risk of one sweep: a known failure recurs in the gap before its tool
lands. Page B found 18 of 118 rules whose failure returned after the rule
was written, the worst at 27, 15 and 5 strikes (observed:
`plans/frame287-rules-origin.md`). Of those three, the backslash patch
and the status time are tool work, `status` and the Write tool, and the
history read is an agent's question, so the three worst are covered by
the first frames below. The remaining rules fire at moments the state
print names, so the print lists the reference lines for the moments a
held frame will meet. The gap is then one or two sessions for the rules
no tool covers, and the reference holds them by moment. The sweep stands
(reasoned; the alternative keeps the fragmented context for weeks).

## 6. The build order

1. The intent page, drafted in two levels from the composition, the 219
   quotes of `plans/frame287-roman-words.md`, the brief's ruled lines and
   the memory files; Roman and the session edit it. 2 cycles.
2. `state`, `status` and the handover dialogue in `handover.py`, with the
   350k line. 3 cycles and a review.
3. The sweep: `CLAUDE.md` to the intent page and a pointer, the rules to
   `reference.md` by moment, the stack's head rules and the rota memory
   files with them. A sweeper and a review. 3 cycles.
4. Law lines on the doors the archive names, by a script over the comments
   that cite a night, and `rulings.py` kept. 2 cycles.
5. `state --since` for his return. 1 cycle.

About 11 cycles. Frames 2 and 4 share no file and run beside each other.
