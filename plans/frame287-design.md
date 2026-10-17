# Frame 287, the design: the build session gets wiring

Meta workflow. Reasoned on Fable by session 0162323a on 2026-10-17 from
the four pages `plans/frame287-roman-words.md` (A), `-rules-origin.md`
(B), `-questions.md` (C) and `-context-cost.md` (D). Every line carries a
mark. `#n` and `An` are quote tags in page A. Nothing here is built yet.

## 0. The design in six sentences

1. The build session is the one seat in the composition that has no
   wiring, and that absence is the flaw Roman named (observed:
   `plans/composition.md`, "one strong model, one context, no wiring";
   #623 "a serious flaw with the meta workflow").
2. Rota's seats restart from records, and the structure builds each wake
   from records keyed by the wake's subject. The build session restarts
   from a fixed list of state files, and reaches precedent only through
   a rule it must remember at the moment of a question (observed: B,
   sections 1 and 4).
3. The design gives the build session thin wiring: one tool that, at six
   moments, prints the points the records hold on what the moment
   touches, keyed by file, door, law, frame, seat, sign and his words
   (reasoned: section 3).
4. The records gain the keys the tool needs as fields the writer fills at
   write time, and a script derives the index from the fields, as the
   map tool derives its index from the code (ruled: #36, #37 "i really
   like the scripted approach", "completely separate tooling, nice").
5. The stack becomes a view over one record per frame, status history
   leaves the view, a tool writes every status line, and the brief keeps
   only what every turn needs (observed: D, sections 1, 3 and 7).
6. A lookup is a tool. Understanding is an agent on Opus that reads the
   lookup's hits and returns ten lines. Judgement stays in this seat
   (ruled: A153 "answers should be retreived by subagents to build
   understanding"; #94 "fable is the only one capable of the reasoning
   required for good high level decisions").

## 1. The purpose, in his words

- The need, from the first day to the last: "do they have this stuff
  encoded somewehere?" (#70, 09-17); "the hard task is to make this all
  uniffied so that accros multiple sessions, it appears that a single
  session leverages all of this context" (#624, 10-17).
- The sign of success: "nothing measurable, we stay aware of all
  relevant points previously discussed without clutter" (A152).
- The method: "the whole design and rationale should be in the logs",
  "answers should be retreived by subagents to build understanding"
  (A153); "use a subagent to search our decisions logs, etc ie meta"
  (A114, 10-04); "not with deterministic checks, with subagents" (#619).
- The scope: "the whole method, with an important focus on the context,
  looking at previous decisions/implementation etc entire project
  context, progressive re-discovery, project future management" (#626).
- The future: "I don't know what frame numbers mean, tell me a story"
  (#357); "the meaning of the frame is important whereas the number is
  not" (#369); "Why would i give it the frame? hand off" (#501); "Stop
  pausing for sprint orders, I will re prioritise if something changes"
  (#610); "when is it actually important for me to make scheuding
  decisions?" (#558).
- The clutter: "are there any items that affect every session by a bit?
  im noticing no session is below 100k" (#20); "whats the strategy to
  keep track of facts like these without cluttering memory?" (#245);
  "The count every turn, i dont want this to influence planning untill
  its actually relevant" (#42).
- The momentum: "I feel like handover looses a lot of context momentum
  that we can carry over" (#473); "the frame is only a memory tool, what
  does the project as a whole need here?" (A39).

What "a single session" would do (reasoned: from #624): a session that
had lived every day would know the laws because it wrote them, would
remember what Roman said when the topic returns, would know why each
door exists, and would know what is next and why. It does this by
association. A topic comes up and the relevant points surface. That is
retrieval keyed by the topic in hand, at the moment the topic arrives.
It is not a longer read list.

## 2. Why the session was not equipped

Roman's question: "think critically, why were you not equipped to be
aware of all this yourself?" (#622). Four causes, each observed.

1. **The read list is state, not precedent.** The take reads the
   composition, the momentum note, the open frames and the frame's memory
   files. It does not name `rota/LAWS.md`, `DECISIONS.md`, `ROLES.md`,
   the briefs, the archive or the transcripts. Those arrive only through
   two rules that fire after a question forms, and that failure recurred
   five times after the rule (observed: B, section 1 and C58, C59).
2. **The records are filed by principle, not by the thing in hand.** Law
   12's title is "Constraints protect external commitments only". A
   session that meets a write door's refusal searches for the door, the
   file or the word "permission", and the law does not answer to those
   words. The same holds for law 2 and frame 115 (observed: C, section
   3). Rota's own map tool solved this for code: it answers to a function
   or a table name. Nothing answers to a door, a law or a frame for the
   records (observed: B, section 3).
3. **A conclusion that dissolves a question is filed where nothing keyed
   by the question points.** The 10-04 read of frame 114 found "the fix
   was always allowed" and wrote it to a frame file and a status line.
   The frame closed. On 10-17 the question went to him twice more
   (observed: C, section 1, group 1). Roman's own answers in an
   `AskUserQuestion` result stay in one transcript until a session copies
   them. Frame 204's group was asked nine times across three sessions
   (observed: C, group 3).
4. **A rule that fires at a moment is held by prose that the session must
   recall at that moment.** 18 of 118 rules saw their failure return. The
   worst three, at 27, 15 and 5 strikes, are all prose rules about a
   moment: a scripted edit, a status write, a question. The failures that
   stopped recurring stopped when a tool took the moment: the hand-off
   target by `handover.py`, the standby arm, the gate (observed: B,
   summary and the table; reasoned: the pattern across the three).

The common cause (reasoned): the composition says "Capability comes from
wiring. No brief grants what is not wired", and the build session was
given a brief and no wiring. The brief grew by one story per failure,
to 8.4k tokens a turn with half of it serving events of fewer than one
turn in ten (observed: B, section 2). The brief is now part of the
clutter it was written to prevent.

## 3. The mechanism: six moments, one tool

One tool, `python -m rota.tools.wake <moment> <keys>`, prints the
points the records hold on the keys, in a fixed order, with a pointer
per point. The session reads the print and decides. An Opus agent reads
the pointed files when the print exceeds what a decision needs, and
returns ten lines and a file (ruled: A153; C43 for the ten-line form).
The tool is deterministic, the agent builds understanding, and this
seat judges (reasoned: the split he approved for the map, #36 and #37,
and for subagents, #619 and A114).

| Moment | Keys in hand | What the tool prints | Replaces |
|---|---|---|---|
| **take** | the held frame numbers | one page per frame: the fields, the last status line, its law lines, the decisions and rulings on its site, his words tagged with the frame, the open and closed frames on the same site, the pointers | the stack read of 27k to 38k ctx, 58% to 78% of it status lines (observed: D, section 2) |
| **push** | site, sign, seat, night | the law or brief rule the door derives from, the frames open and closed on the site, the frames with the same sign, the decisions on the site, his words on the topic | the guide's step 1, which asks only whether the sign is an open frame's (observed: B, W5) |
| **design** | the door, predicate, file or brief rule the frame edits | the law lines it derives from, the decisions and the design records on it, the prior frames that touched it with their verdicts | the design review's first read, today the scope report alone (observed: B, C53) |
| **ask** | the frame, the topic words of the question | every record on the topic: laws, roles, decisions, frame files, his words; then a line "records read: ..." the question must carry | C58 and C59, five strikes (observed: B) |
| **night** | each wall's sign, seat, door, file | the law behind the door, the frames on the sign and the site, the door's count lines over past nights | the guide's steps 1 and 8, and the count that C35 asks for by hand |
| **close** | the frame number | the frame's history file closed, its momentum note deleted, the `handed` column corrected, the index rebuilt | three hand steps that drift: 29 notes in `plans/`, a `handed` column that contradicts the stack (observed: D, section 7; B, C21) |

Rules the table carries (reasoned unless marked):

- The take prints pages for the held frames only. Precedent for a frame
  that is not held arrives when that frame is taken or pushed. That is
  the progressive part of re-discovery (ruled: #626 "progressive
  re-discovery").
- A push prints before the frame is written, so the `Law:` field and the
  placement are written from the print. A push whose site has an open
  frame prints that frame first, which is the case frame 220 held for
  frame 114 five rows down (observed: C, group 1).
- The ask print is the two reads of 2026-10-04 14:52 made mechanical.
  The question carries the "records read" line, or it does not go. He
  reads that line on his phone before the question, and "did you look
  into this" has an answer in the text (ruled: #403 "do you have a
  habbit, up front guidance, that means that you reach for subagents",
  #404 "yeah add it"; reasoned: the form).
- The night print's first line is the law behind the door. The guide's
  section 4 gains a step 0: "which law or brief rule decides this case?"
  The placement cites the law line, and a door that contradicts the law
  it should derive from is cause 8 whatever its count (observed: frame
  287's origin, two doors against law 12 and no review read the law).
- The close is one command. The frame's record stays. The note leaves.
  The index is rebuilt (ruled: C10's "leaves the repository when the
  frame it carries closes", not applied 29 times; observed: D, section 7).

## 4. The record shapes and their keys

The index is derived, never hand-written. A script reads the fields and
the markers below and writes `plans/index/` as the map tool writes its
tables. One writer per fact stays true: the record's writer fills the
field, the script derives the key (ruled: composition, "Every record has
one writer"; #36 the scripted approach).

| Record | Writer | Keys today | Keys added | How |
|---|---|---|---|---|
| A frame, `plans/frames/<n>-<slug>.md` | the holding session, through the status tool | frame number | `Site:` files, doors and seats; `Law:` the law or brief rule; `Sign:` the error or refusal text; `Night:` the nights it counts on | fields the push writes, the tool checks they exist |
| The stack, `plans/stack.md` | the script | frame number | none; it is a view | regenerated from the frame files: sprint rows, then each open frame's fields and last status line |
| A law, `rota/LAWS.md` | Roman through the Liaison | law number | the doors and files that derive from it | a `Derives:` line under each law, filled once by an agent and then by every door frame |
| A decision, `rota/DECISIONS.md` | the same | line number | `Site:` and `Law:` on each entry | one agent pass, then each new entry |
| A night read | the reading session | night number | the frames, doors and signs it names, in backticks and `frame n` | parsed, no new field |
| A frame file, a design, a review, an interview | the session or agent | frame number in the name | `Site:` and `Law:` in the header | the brief's report form gains the two lines |
| His words, `plans/roman-words.md` | the extraction script, from the transcripts | none | date, session, the frame numbers the message names, the question it answers | regenerated by the script page A used; grep by topic words, 150k characters, one agent call reads it whole (observed: `compact.txt`, 151,405 bytes) |
| A ruling from an `AskUserQuestion` | the ask tool | none | frame, date, the question text | the tool appends question and answer to the frame file as a `Ruling:` line when the answer lands |
| A memory file | the session | the index line | the moment it fires at | a `Moment:` line, so the take prints the memory files for the moments the frame will meet, and C27's "the memory files the frame names" is derived |

The archive becomes unnecessary (reasoned): a closed frame's file stays
in `plans/frames/` with its closing status, keyed by number and site. The
close-date key, which nobody has in hand, goes (observed: B, section 3,
S6). The existing archive is parsed once into frame files by a sweeper,
since every frame is `### n.` delimited.

The questions of the past that had no key, and the key that answers each
(observed: B, section 3; reasoned: the mapping):

- "Was this decided?" the `ask` print over laws, decisions, rulings and
  his words, by topic words and site.
- "Why does this door exist?" `Law:` and `Night:` on the door's frame,
  reached from the door name by `Site:`.
- "What touches this file?" every frame's `Site:`, open or closed.
- "Which frames share a cause?" the guide's cause number as a field,
  `Cause:`, on each wall frame.
- "What did Roman say about this?" `plans/roman-words.md` by frame and
  topic.
- "What is next and why?" section 6.

## 5. What stops loading

Measured today, and the smaller form (observed: D; reasoned: the form).

| Item | Today | Smaller form | Saving |
|---|---|---|---|
| The stack at a take | 27k to 38k ctx, 55% status lines | the take print, about 2k to 3k a held frame | 7k to 14k a hand-off, 20k to 55k a session |
| Status lines written by hand | a 2k-char script a cycle, 15k tok a session; 15 strikes on the clock, 27 on the backslash | `python -m rota.tools.wake status --frame n --text ...` stamps the clock, keeps CRLF, appends to the frame file, regenerates the view, commits | about 10k a session, and three memory rules retire |
| The brief | 8.4k every turn, about half for events under one turn in ten | the every-turn rules stay, about 4k; the hand-off, standby, night, sprint and escalation procedures become `plans/method/<moment>.md`, printed by the tool at the moment; each rule one line, its origin behind a pointer | about 4k a turn, several hundred turns a session |
| The memory index | 2.2k every turn | unchanged; the per-file `Moment:` line lets the take print the files the frame will meet, so C27 needs no judgement | none a turn, fewer wrong reads |
| The composition page | 1.7k a take, cited in no state reply | unchanged; it is the frame of reference every placement is read against (ruled: "the page wins") | none |
| Momentum notes | 29 in `plans/`, 143k chars | the close deletes the note | none in context, less drift on disk |
| The hook echo | 390 chars on every prompt, 58 times a session, about 5.5k tok | fires on Roman's prompts only, not on task notifications | about 5k a session; a `.claude/settings.json` edit |
| Tool schemas no session calls | about 12.5k tok a turn, five tools | out of the build session's tool set | 12.5k a turn; a harness setting Roman holds, item for him |
| The count hook | every turn | unchanged; three thresholds need it (ruled: #42, #43 explain and ignore until relevant) | none |

A cycle's unseen cost, about 6k ctx of thinking and tokenizer gap, stays
(observed: D, section 3). The design cuts what the session reads and
writes, not what it thinks.

## 6. The future: frames and sprints

What he asks for (observed: A, section 5): the meaning of a frame, not
its number; what is next and why; whether the important work is being
done; and no question to him about order unless the order crosses his
intent or the composition (ruled: #558, #559, #610).

- Every frame carries a `Means:` line, one sentence in rota's terms, what
  the frame changes for the seats or the principal (ruled: #369 "give
  yourself a habit to communicate meaning with me"; reasoned: a field the
  view and every mention can print, so the habit is not recalled, it is
  read).
- The sprint section of the view is derived: for each row the frame
  number, its name, its `Means:` line, the wall it closes with the
  night's cost, and the cycles. The reading session writes the order; the
  script writes the rows. The order carries one reasoned line, which wall
  the next night debugs and why (ruled: #557 "sprint evolution",
  crossing off and taking on; C46, C47).
- "What is next and why" is `python -m rota.tools.wake next`: the sprint
  rows and the one line. Roman reads it, or asks and the session prints
  it. No session waits on an order (ruled: #610).
- A push places itself as C46 says, and the push print gives the
  placement its reason: the wall's cost on the night and the frames it
  shares a site or a cause with (reasoned).
- Roman's rulings on the future are the ones C47 names: an order that
  crosses intent or the composition, who talks to whom, what the
  principal sees, what ships without him, or a night design that opens an
  investigation first. The `ask` print tells the session whether a
  question is one of those before it goes (ruled: #559, 2026-10-12 23:52).

## 7. The brief changes this implies

Each one a line in `CLAUDE.md`, with the procedure behind a pointer
(reasoned: section 5, the brief split).

1. The take: run `wake take`, read the composition page, read the
   momentum note, read the print. The stack is not read at a take.
2. The push: run `wake push` first. Write `Site:`, `Law:`, `Sign:`,
   `Means:`, `Sprint:` from the print. A frame without `Law:` is refused
   by the status tool.
3. The design: the design brief and the design review carry the `wake
   design` print. The review's first point is the law line.
4. The question: run `wake ask` first. The question carries "records
   read". A question that names no record does not go. The two reads of
   2026-10-04 14:52 are this print.
5. The night read: the guide gains step 0, the law behind the door. The
   count line comes from the print.
6. The close: one command, `wake close`.
7. The status line: the tool writes it. No script by hand.
8. The hand-off: unchanged in its thresholds; the momentum note stays as
   ruled (#474 "1 yes"); the taker reads the print and not the stack.
9. The brief itself: the procedures of the hand-off, standby duty, the
   night, the sprint and the escalation move to `plans/method/`, each
   rule one line with its origin behind a pointer; the brief keeps the
   rules that act every turn.
10. The wall guide: step 0; `Cause:` as a field; the guide cites laws by
    number and decisions by title, not by line (observed: B, W2).

Three memory rules retire when the status tool lands, the clock, the
backslash and the release-before-rearm (reasoned: the tool holds each
moment). The history-before-escalation rule retires when the ask print
lands, because the question form carries it.

## 8. The one thing Roman rules

The composition's build-session paragraph says "one strong model, one
context, no wiring". The design gives the build session thin wiring:
tools that build the wake at each moment from keyed records, as the
structure does for a seat, with the records as its only memory. That
sentence is a composition change, so it is his (ruled: the composition's
own rule that the page wins and he ratifies it; #559 the composition is
his line).

Recommended wording for the paragraph (reasoned): "The assistant sits
above rota: one strong model, one context, and thin wiring. Its tools
build its wake at each moment from the records, keyed by what the
moment touches. Its brief is the first section of `CLAUDE.md`. Its
records are this page, the frame files, and the memory directory."

Everything else in this design sits under lines he has already ruled:
the scripted approach (#36, #37), subagents for retrieval (A114, A153,
#619), the momentum note (#474), meaning over number (#369), no pause on
orders (#610), reports to a file with ten lines back (C43), and the
status line's five fields (C67). Those parts go to him as a notice, not
a question.

## 9. The frames to build, with the prototype first

The doubt the momentum note named first: whether the index can be built
from prose records. The answer is to build it forward from fields and
back-fill the past once by agents, and to test the back-fill on the
questions that already went wrong (reasoned).

| Frame | Site | Ends when | Price |
|---|---|---|---|
| 1. The prototype | `rota/tools/wake.py`, read-only | `wake ask` and `wake push` run over the records as they are, with no new field, on the 19 questions page C marks R: the print names the record that held the answer for at least 15 of 19, by site and topic words alone; the misses are named with the key they lacked | 3 cycles, one implementer and one review on Opus |
| 2. The frame files and the status tool | `plans/stack.md`, `plans/frames/`, `plans/archive/`, `rota/tools/wake.py` | the sweeper has split the stack and the archive into frame files; the view regenerates byte-stable from them twice; `wake status` writes one line and the commit; the stack rule 5 reads "the view" | 4 cycles, a sweeper, an implementer and a review |
| 3. The fields and the back-fill | `rota/LAWS.md`, `rota/DECISIONS.md`, the frame files, `plans/roman-words.md` | `Derives:` under each law and `Site:`, `Law:` on each decision and frame file, filled by one Opus agent from the records and checked on frames 114, 115, 204 and 220; `roman-words.md` regenerated by the script with frame tags; the index builds from the fields | 4 cycles, two agents and a review |
| 4. The brief split and the method files | `CLAUDE.md`, `plans/method/`, `plans/wall-guide.md`, `.claude/settings.json`, the memory files | the brief under 4k tokens by `wc`; each moved rule one line with a pointer; step 0 in the guide; the hook echo on prompts only; three memory rules marked retired with the tool that holds them; one session takes a frame with the new take and its state reply cites a law line | 3 cycles, a sweeper and a review, then one take |
| 5. The close and the next view | `rota/tools/wake.py` | `wake close` deletes the note, corrects `handed`, rebuilds; `wake next` prints the sprint rows with `Means:`; the 29 notes are gone | 2 cycles |

Frames 1 and 2 share no file and run side by side. Frame 3 waits on 2
for the frame files. Frame 4 waits on 1, because the brief points at a
tool that must exist. In all about 16 cycles, one sprint (reasoned: by
the anchors of 2026-10-11 05:51).

The check at the end (reasoned: the three groups page C found): a taker
on the first take under the new method is given the frame 114 question
cold, and its state reply places it under law 12 without a read of the
law file by hand. That is the awareness he described, on the case that
started this frame.

## 10. What to doubt

- The back-fill is partial. An agent filling `Site:` on 160 closed frames
  will miss some. The agent route stays for what the index misses, so a
  miss costs a read and not a question (reasoned).
- The view and the frame files double the places a frame appears. The
  view is never edited by hand, and the status tool is the only writer of
  a frame file. If a session edits the view, the next regeneration erases
  the edit, which is the right failure (reasoned).
- The ask print could become a longer read list in a tool's clothing. The
  guard is the key: it prints what matches the site and the topic words,
  with a cap, and the agent reads the rest. The cap is read D's cycle
  size, about 3k tokens of visible content (observed: D, section 3).
- His words as a record in the repository. They are already in the
  transcripts on the same machine, and page A is in `plans/` now. The
  record is regenerated, never edited, and quotes him as typed (reasoned;
  his to decline).
- The composition change is the one thing that could be wrong at the
  altitude that matters. If he keeps "no wiring", the tools still stand as
  the map tool does, as separate tooling the brief points at, and the
  design loses only the sentence (reasoned).

Usage: the four pages cost this session about 60k of context to read
(reasoned: 144k bytes at 4 bytes a token, less the truncated tail).
