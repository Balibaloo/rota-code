# Frame 287, the design: the build session gets wiring

Meta workflow. Reasoned on Fable by session 0162323a on 2026-10-17 from
the four pages `plans/frame287-roman-words.md` (A), `-rules-origin.md`
(B), `-questions.md` (C) and `-context-cost.md` (D). Revision 2, after
design review 1, `plans/frame287-design-review-1.md`, which found ten
high findings against revision 1; each is answered where it applies and
listed in section 11. Every line carries a mark. `#n` and `An` are quote
tags in page A. Nothing here is built yet.

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
   touches, keyed by file, door, law, frame, seat, sign and his words.
   The print informs. It never refuses, and it never decides what reaches
   him (reasoned: section 3; review 1, finding 3).
4. The keys live in one derived file that one script writes from the
   records as they are, with a (reasoned) mark per row, as the map tool
   derives its answers from the code on demand. `LAWS.md` and
   `DECISIONS.md` are not written (ruled: #36, #37 "i really like the
   scripted approach", "completely separate tooling, nice"; review 1,
   findings 2 and 12).
5. A tool writes every status line and the take reads a print instead of
   the stack. The frame files and the view come after the print has
   proved itself (observed: D, sections 1, 3 and 7; review 1, finding 9).
6. A lookup is a tool. Understanding is an agent on Opus that reads the
   lookup's hits and tests the recommended answer. Judgement stays in
   this seat (ruled: A153 "answers should be retreived by subagents to
   build understanding"; #94 "fable is the only one capable of the
   reasoning required for good high level decisions"; the agent reads of
   2026-10-03 and 2026-10-04 14:52 stay, fed by the print).

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
  (A114, 10-04); "not with deterministic checks, with subagents" (#619,
  said of finding walls; reasoned: it fits retrieval too).
- The scope: "the whole method, with an important focus on the context,
  looking at previous decisions/implementation etc entire project
  context, progressive re-discovery, project future management" (#626).
- The future: "I don't know what frame numbers mean, tell me a story"
  (#357); "the meaning of the frame is important whereas the number is
  not ... Don't make that persisted, just give yourself a habit" (#369);
  "What are we writing towards in the medium term?" (#356); "are we
  producing new frames and then never prioritising them into the current
  sprint?" (#557); "Why would i give it the frame? hand off" (#501);
  "Stop pausing for sprint orders, I will re prioritise if something
  changes" (#610).
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
aware of all this yourself?" (#622). Five causes.

1. **The read list is state, not precedent, and nobody searched the law
   file.** The take reads the composition, the momentum note, the open
   frames and the frame's memory files. It does not name `rota/LAWS.md`,
   `rota/ROLES.md`, `rota/DECISIONS.md`, the briefs, the archive or the
   transcripts. Those arrive only through two rules that fire after a
   question forms, and that failure recurred four times after the rule
   (observed: B, section 1, C58 and C59). Review 1 probed the keys a
   session had in hand for frames 114 and 115: `grep -i permission
   rota/LAWS.md` lands in law 12, and `grep -i reasoning` lands on law
   2's title. The records answered the keys. No session ran the grep
   (observed: review 1, finding 4, 2026-10-17). This is the first cause,
   and the largest. It holds for frame 114 alone: frame 115's questions
   used "answer" and "prose", and neither word reaches law 2 in
   `LAWS.md` (observed: review 2, finding 2, by grep). Frame 115 is
   cause 2.
2. **Some records are filed by principle, not by the thing in hand.** Law
   12's title is "Constraints protect external commitments only"; its
   body holds "permission" and "stray", so a body search finds it and a
   title search does not. The 10-04 read that dissolved frame 114's
   question sits in a frame file no door name points to (observed: C,
   section 3; review 1, finding 4). This cause is second, and it decides
   what the index adds after cause 1 is fixed: a key for each record the
   prototype misses with the question's own words, law 2 first (observed:
   review 2, finding 2).
3. **A conclusion that dissolves a question is filed where nothing keyed
   by the question points, and his answers stay in one transcript.** The
   10-04 read of frame 114 wrote "the fix was always allowed" to a frame
   file and a status line; the frame closed; on 10-17 the question went
   to him twice more. Frame 204's group was asked nine times across
   three sessions while his answers sat in one session's `AskUserQuestion`
   results (observed: C, section 1, groups 1 and 3).
4. **A session held the fact and did not connect it.** Rows 59 to 61 of
   page C had frame 204's design file on the read list, and row 99 had
   the composition's "A prediction never blocks". The session read them
   and asked anyway (observed: C, the "Read list" column; review 1,
   finding 15). A print of hits does not fix this one. An agent that
   reads the hits against the question and says what they answer does
   (reasoned: the ruling of 2026-10-04 14:52 already asks for that).
5. **A rule that fires at a moment is held by prose that the session must
   recall at that moment.** 18 of 118 rules saw their failure return. The
   history rule at 5 strikes, the status time at 15 and the backslash
   patch at 27 are all prose rules about a moment. The failures that
   stopped recurring stopped when a tool took the moment: the hand-off
   target by `handover.py`, the standby arm, the gate (observed: B,
   summary and table; reasoned: the pattern across the three).

The common cause (reasoned): the composition says "Capability comes from
wiring. No brief grants what is not wired", and the build session was
given a brief and no wiring. The brief grew by one story per failure,
to 8.4k tokens a turn with about half of it serving events of fewer than
one turn in ten (observed: B, section 2). The brief is now part of the
clutter it was written to prevent.

## 3. The mechanism: six moments, one tool

One tool, `python -m rota.tools.wake <moment> <keys>`, prints the
points the records hold on the keys, in a fixed order, with a pointer
per point, under a cap of about 3k tokens (observed: D, section 3, the
visible content of a median cycle). The session reads the print and
decides. An Opus agent reads the pointed files when the print exceeds
what a decision needs or when the question is why, and returns ten lines
and a file (ruled: A153; C43 for the ten-line form). The tool is
deterministic, the agent builds understanding, and this seat judges
(reasoned: the split he approved for the map, #36 and #37, and for
subagents, A114 and #619). The print never refuses an action and never
decides whether a question reaches him. Those stay with the session
(ruled: composition, "The tool never rules for the Principal"; review 1,
finding 3).

| Moment | Keys in hand | What the tool prints | Replaces |
|---|---|---|---|
| **take** | the held frame numbers | one page per frame: the fields, the last status line, the law lines its site matches, the decisions on its site, the open and closed frames on the same site, the pointers | the stack read of 27k to 38k ctx, 58% to 78% of it status lines (observed: D, section 2) |
| **push** | site, sign, seat, night | the law or brief rule whose body matches the site or the sign, the frames open and closed on the site, the frames with the same sign, the decisions on the site, his words tagged with the sign or the frame | the guide's step 1, which asks only whether the sign is an open frame's (observed: B, W5) |
| **design** | the door, predicate, file or brief rule the frame edits | the law lines it matches, the decisions and design records on it, the prior frames that touched it with their verdicts | the design review's first read, today the scope report alone (observed: B, C53) |
| **ask** | the frame, the question text | every record whose body matches the question's words and the frame's site: `LAWS.md`, `ROLES.md`, `DECISIONS.md` first, then the briefs, the frame files, the archive, his words; then a "records read" line for the question to carry | the first of the two agent reads of 2026-10-04 14:52 becomes cheap; the second, the test of the recommended answer, stays with the agent (observed: B, C58, C59) |
| **night** | each wall's sign, seat, door, file | the law behind the door, the frames on the sign and the site, the door's count lines over past nights | the guide's steps 1 and 8, and the count that C35 asks for by hand |
| **close** | the frame number | the frame's closing status written, its momentum note deleted, the `handed` column corrected, the index rebuilt | three hand steps that drift: 29 notes in `plans/`, a `handed` column that contradicts the stack (observed: D, section 7; B, C21) |

Rules the table carries (reasoned unless marked):

- The take prints pages for the held frames only. Precedent for a frame
  that is not held arrives when that frame is taken or pushed. That is
  the progressive part of re-discovery (ruled: #626 "progressive
  re-discovery").
- His words print at a push and an ask, by sign, frame and topic words,
  not at every take. The momentum ruling declined a transcript pointer
  on every hand-off as noisy over time (ruled: #474 "2 too noisy over
  time?"; review 1, finding 20).
- A push prints before the frame is written, so the `Law:` field and the
  placement are written from the print. A push whose site has an open
  frame prints that frame first, which is the case frame 220 held for
  frame 114 five rows down (observed: C, group 1).
- The ask print feeds the agent read. The two rulings stand as amended:
  the agent of 2026-10-03 reads the print's hits first, and reads the
  whole record set as the ruling says when the print has no hit or
  reaches its cap, because a question with no hit is the frame 114 path
  that ruling exists to close (observed: review 2, finding 4); and the
  agent of 2026-10-04 14:52 still answers both
  things, what the records say and whether the recommended answer holds
  against the frame's evidence. The question carries the "records read"
  line. A question with no hit still goes; 46 of 103 past questions were
  open choices no record held (observed: C, counts; review 1, findings 3
  and 7). He reads the line on his phone before the question, and "did
  you look into this" has an answer in the text (ruled: #403 "do you have
  a habbit, up front guidance, that means that you reach for subagents",
  #404 "yeah add it").
- The night print's first line is the law behind the door. The guide's
  section 4 gains a step 0: "which law or brief rule decides this case?"
  The placement cites the law line, and a door that contradicts the law
  it should derive from is cause 8 whatever its count (observed: frame
  287's origin, two doors against law 12 and no review read the law).
- The close is one command. The note leaves. The index is rebuilt
  (ruled: C10's "leaves the repository when the frame it carries
  closes", not applied 29 times; observed: D, section 7).
- The cycle rules stay in the brief. No moment prints an agent launch, a
  commit or a scripted edit, so Opus on every agent, reports to a file,
  one implementer a frame, the gate before a commit, the script rule and
  the commit form are not moved (observed: review 1, finding 6).

## 4. The keys and the one derived file

The index is derived on every run. The tool parses the records as they
are and keeps no file, as the map tool parses the code with no cache
(observed: `map.py`, "There is no cache"; review 1, finding 12; review 2,
finding 8). No existing record gains a field written by an agent. One
writer per record stays true, and every derived row the print shows
carries (reasoned: the script, the pattern it matched) (ruled:
composition, "Every record has one writer"; review 1, finding 2).

| Record | Writer today | Key the script derives | From |
|---|---|---|---|
| A frame in `plans/stack.md` or the archive | the holding session | number, `Site:` files and doors, `Law:` (new field, section 7), `Sign:` (new field), the nights its status lines name | the fields, `### n.` headings, backticked names |
| A law | Roman through the Liaison | number, title, and the words of its body | the law's text; no `Derives:` line is written into `LAWS.md` |
| A decision | the same | title, the files and doors its body names | the entry's text |
| A role | the same | role name, the words of its body | `ROLES.md` |
| A night read | the reading session | night number, the frames, doors and signs it names | backticks and `frame n` |
| A frame file, a design, a review, an interview | the session or agent | frame number, the files and doors it names | the file name and body |
| His words, `plans/roman-words.md` | the extraction script, from the transcripts | date, session, the frame numbers the message names, the question it answers | regenerated by the script page A used; 151k characters today (observed: `compact.txt`) |
| A ruling from an `AskUserQuestion` | the status tool | frame, date, question, answer | the session runs `wake ruling --frame n` when the answer lands; the tool appends a status line in the frame's record, as the session does by hand today |
| A sprint order | the reading session | sprint number, date, the rows | the `## Sprint` sections of the stack; today they have no key (observed: review 1, finding 18) |
| A memory file | the session | the moments it fires at | a `Moment:` line in the frontmatter, so the take prints the memory files for the moments the frame will meet |

Whether his words become a record in the repository is his to rule
(section 8). Until he rules, the tool greps the extraction in the
scratchpad that page A built, and the index holds no row from it
(reasoned: review 1, finding 8).

The questions of the past that had no key, and the key that answers each
(observed: B, section 3; reasoned: the mapping):

- "Was this decided?" the `ask` print: laws, roles and decisions first,
  by the question's words and the frame's site.
- "Why does this door exist?" the frame whose `Site:` names the door, its
  `Law:` and the nights its status lines name.
- "What touches this file?" every frame's `Site:`, open or closed.
- "Which frames share a cause?" the guide's cause number, parsed from
  "Cause n by the guide" in the frame's text.
- "What did Roman say about this?" his words by frame and topic.
- "What is next and why?" section 6.

## 5. What stops loading

Measured today, and the smaller form (observed: D; reasoned: the form).

| Item | Today | Smaller form | Saving |
|---|---|---|---|
| The stack at a take | 27k to 38k ctx, 55% status lines | the take print, about 2k to 3k a held frame, parsed from `stack.md` in place | 7k to 14k a hand-off, 20k to 55k a session |
| Status lines written by hand | a 2k-char script a cycle, 15k tok a session; 15 strikes on the clock | `wake status --frame n --text ...` stamps the clock, keeps the line endings, appends, commits `plans/stack.md` by pathspec | about 10k a session; the clock rule retires |
| The brief | 8.4k every turn, about half for events under one turn in ten | a rule moves to `plans/method/<moment>.md` only when a tool prints it at its moment: the take procedure by `wake take`, the standby wake and the hand-off steps by `handover.py`, which prints its own procedure at `standby`, `take` and `hand` today, the night stop by `wake night`, the escalation route by `wake ask`, the close by `wake close`; each stays one line in the brief with its origin behind a pointer; the 300k and 400k thresholds, the sprint boundary and the cycle rules stay, because no tool prints them (observed: review 2, finding 1) | about 2k to 3k a turn, several hundred turns a session (reasoned) |
| The memory index | 2.2k every turn | unchanged; `Moment:` lets the take print the files the frame will meet | fewer wrong reads |
| The composition page | 1.7k a take, cited in no state reply | unchanged; it is the frame of reference every placement is read against (ruled: "the page wins") | none |
| Momentum notes | 29 in `plans/`, 143k chars | the close deletes the note | less drift on disk |
| Tool schemas no session calls | about 12.5k tok a turn, five tools | out of the build session's tool set | 12.5k a turn; a harness setting Roman holds, item for him |
| The hook echo and the count hook | every prompt | unchanged; the echo is his standing instruction against idling at a task notification, and the count serves three thresholds (ruled: #42, #43; review 1, finding 19) | none |

The frame files and the regenerated view of revision 1 are not in this
table. They come as a later frame, after the take print has parsed
`stack.md` in place for a sprint, because a regenerated view erases a
hand edit with no sign and conflicts on every merge once branches land
(observed: review 1, finding 9). When they come: regenerate only when the
view's bytes match the last generated hash, print a diff when they do
not, and commit by pathspec.

A cycle's unseen cost, about 6k ctx of thinking and tokenizer gap, stays
(observed: D, section 3). The design cuts what the session reads and
writes, not what it thinks.

## 6. The future: what he asks, and what prints

What he asks (observed: A, section 5): what the work is for in the medium
term, whether the backlog shrinks or grows, which frames matter, what is
next and why, and no question to him about order unless the order
crosses his intent or the composition (ruled: #356, #557, #571, #558,
#610). Revision 1 answered "next" alone (observed: review 1, finding 10).

- No `Means:` field. He ruled it: "Don't make that persisted, just give
  yourself a habit to communicate meaning with me" (#369). The habit
  stays a habit, held by memory M14 (observed: review 1, finding 1).
- `wake next` prints four things: the destination line of the composition
  page, "a careful person runs rota alone on a small Python repository
  and gets a merged change they can read"; the sprint rows with each
  frame's name and the wall it closes with the night's cost; the counts
  of frames opened and closed over the last seven nights; and the parked
  frames with their rank (reasoned: the four questions above, one print
  each).
- The sprint section stays the reading session's writing, and the script
  parses it for the key (section 4). The session that reads a night
  writes the order and one line, which wall the next night debugs and
  why (ruled: C46, C47, C48).
- A push places itself as C46 says, and the push print gives the
  placement its reason: the wall's cost on the night and the frames it
  shares a site or a cause with (reasoned).
- His rulings on the future are the ones C47 names. The session decides
  whether a question is one of those; the print does not (ruled: #559,
  2026-10-12 23:52; review 1, finding 3).

## 7. The brief changes this implies

Each one a line in `CLAUDE.md`, with the procedure behind a pointer.
Each ruling the change touches is named (reasoned: section 5; review 1,
finding 7).

1. The take: run `wake take`, read the composition page, read the
   momentum note, read the print. The stack is not read at a take.
   Amends C25 to C27.
2. The push: run `wake push` first. Write `Site:`, `Law:`, `Sign:` and
   `Sprint:` from the print. Amends C41 and C46; `Law:` and `Sign:` are
   new fields beside `Site:`.
3. The design: the design brief and the design review carry the `wake
   design` print. The review's first point is the law line. Amends C53.
4. The question: run `wake ask` first. The agent read of 2026-10-03 reads
   the print's hits. The agent of 2026-10-04 14:52 still tests the
   recommended answer. The question carries "records read: ..." or
   "records read: none". Amends C58 and C59, and names both as amended.
5. The night read: the guide gains step 0, the law behind the door. The
   count line comes from the print. Amends C34 and W5.
6. The close: one command, `wake close`. Amends C10's last clause and C71.
7. The status line: the tool writes it. No script by hand. Amends C67,
   C68 and memory `rota-status-time-from-clock.md`, which retires.
8. The hand-off: unchanged in its thresholds and in the momentum note
   (ruled: #474 "1 yes"); the taker reads the print and not the stack.
9. The brief itself: a procedure moves to `plans/method/` only when a
   tool prints it at its moment, as section 5 lists; each moved rule is
   one line with its origin behind a pointer; the thresholds, the sprint
   boundary, the cycle rules and the every-turn rules stay (observed:
   review 1, finding 6; review 2, finding 1).
10. The wall guide: step 0; the guide cites laws by number and decisions
    by title, not by line (observed: B, W2).

One memory rule retires with the status tool, the clock. The backslash
rule and the release-before-rearm rule stay, because the tool does not
hold their moments (observed: review 1, finding 13). The history rule
does not retire; it is amended to run from the print.

## 8. What Roman rules

Three items, each with a recommended answer (reasoned: review 1, finding
8; C73, the session checks its own instruction files with him).

1. **[high] The composition's build-session sentence.** Today: "one
   strong model, one context, no wiring". Recommended: "The assistant
   sits above rota: one strong model, one context, and thin wiring. Its
   tools build its wake at each moment from the records, keyed by what
   the moment touches. Its brief is the first section of `CLAUDE.md`.
   Its records are this page, the stack, and the memory directory." If
   he keeps "no wiring", the tools stand as the map tool does, separate
   tooling the brief points at, and only the sentence changes (reasoned).
2. **[med] His words as a record in the repository.** Page A is in
   `plans/` now, and the workflow is meant to transfer to another project
   (ruled: #148, #149). Recommended: no. The tool greps the extraction
   in a scratchpad or a local path outside the repository, regenerated by
   the script, and `plans/frame287-roman-words.md` leaves the repository
   when this frame closes (reasoned).
3. **[med] The brief diff itself**, section 7, when it is written.
   Recommended: he reads the diff of `CLAUDE.md` once, after frame 4
   below, as C73 says, and rules the lines he wants changed (ruled: C73).
4. **[low] The tool schemas no build session calls**, about 12.5k tokens
   on every turn for five tools (observed: D, section 1). The setting is
   the harness's and his. Recommended: leave them out of the build
   sessions' tool set if the harness allows it per project; otherwise
   nothing (reasoned).

Everything else sits under lines he has already ruled: the scripted
approach (#36, #37), subagents for retrieval (A114, A153), the momentum
note (#474), no persisted meaning line (#369), no pause on orders (#610),
reports to a file with ten lines back (C43), and the status line's five
fields (C67). Those parts go to him as a notice with the three items.

## 9. The frames to build, with the prototype first

The prototype's bet, after review 1: a search over the records as they
are, with the keys a session has in hand, finds the record that held the
answer. The back-fill of revision 1 is gone; the index adds keys only for
what the prototype misses (reasoned: review 1, findings 4 and 5).

| Frame | Site | Ends when | Price |
|---|---|---|---|
| 1. The prototype, `wake ask` and `wake push` | `rota/tools/wake.py`, read-only over the records | the print, under its 3k cap, names the record that held the answer for the seven distinct answers of page C's R rows after rows 12, 62, 87 and 100 are excluded, whose answer loads every turn: law 3 (row 6); law 2 (rows 15, 28, 30); law 12 with the touch route and "A prediction never blocks" (rows 26, 27, 99, 103); his notes answers with `frame204-design.md` (rows 59 to 61); `ROLES.md:150-170` (row 64); `frame244-interview.md` (rows 89, 90); his 10-04 14:34 answer (row 102), with the keys taken verbatim from each question as sent; the misses are named with the key they lacked, law 2 the expected first; one review (observed: review 2, point 3) | 3 cycles |
| 2. The take print and the status tool | `rota/tools/wake.py`, `plans/stack.md` read in place | `wake take` prints one page per held frame from `stack.md` as it is; `wake status` writes one line with the clock and commits by pathspec; one taker takes a frame with the print and its state reply cites the law line the print gave; one review | 3 cycles |
| 3. The night, design and close prints, and `wake next` | `rota/tools/wake.py`, `rota/tools/handover.py` for the `handed` column | `wake night` prints the law behind each wall's door on one night's read; `wake close` deletes the note and corrects the column; `wake next` prints the four things of section 6; the 29 notes are gone | 3 cycles |
| 4. The method files and the brief split | `CLAUDE.md`, `plans/method/`, `plans/wall-guide.md`, the memory files | the brief under 5k tokens by `wc`; each moved rule one line with a pointer, and every moved rule has the tool of frames 1 to 3 that prints it; step 0 in the guide; the clock memory marked retired; the diff goes to Roman as item 3 of section 8 | 3 cycles, a sweeper and a review |
| 5. The frame files and the view | `plans/stack.md`, `plans/frames/`, `plans/archive/` | parked until a sprint under frames 1 to 4 shows the take print or the status tool wanting for the stack's size; then the sweeper splits the stack and the archive, the view regenerates byte-stable twice, refuses on a hash mismatch with a diff, commits by pathspec, and the take parser, the status writer and the close are re-pointed at the frame files | 4 cycles, plus a second edit of `CLAUDE.md` (observed: review 2, point 4) |

Frames 1 and 2 share one file and run in order. Frame 3 follows 2 on
the same file. Frame 4 waits on 3, because the brief points at tools that
must exist (observed: review 2, point 4). Frame 5 is parked. About 12
cycles for frames 1 to 4 against the anchors, and the overrun history
says closed frames ran a median of 5 cycles against 2 to 3 priced, so
the honest expectation is about 20 (observed: B, C42; review 1, finding
16; review 2, finding 8 on the sum).

The check at the end of frame 2 (reasoned: the groups page C found, and
their nature as door questions is why it is one check among the nine
answers of frame 1, not the only one): a taker under the new take is
given the frame 114 question cold, and its state reply places it under
law 12 from the print.

## 10. What to doubt

- The prototype may find that a grep over the records answers most of
  the nine and that the index adds little. That is a good outcome: the
  wiring is then the moments and the print, not the keys (reasoned:
  review 1, finding 4).
- The ask print could become a longer read list in a tool's clothing. The
  guard is the cap, about 3k tokens, and the agent reads the rest
  (observed: D, section 3).
- A print of hits does not fix cause 4, a fact held and not connected.
  The agent's second read, the test of the recommended answer against the
  evidence, is the fix for that, and it is already ruled. The design
  keeps it (reasoned: section 2, cause 4).
- The `Law:` field fits door questions best. Questions about a run, a
  card or a design choice have no law, and the print returns the frames
  on the site and his words instead (observed: review 1, finding 17).
- The composition change is the one thing that could be wrong at the
  altitude that matters. If he keeps "no wiring", the design loses only
  the sentence (reasoned).

## 11. The reviews' findings and where each is answered

Review 2, `plans/frame287-design-review-2.md`, three high: 1 only a rule
a tool prints moves out of the brief, sections 5 and 7; 2 cause 1 holds
for frame 114 alone and frame 115 is cause 2, section 2; 4 the agent
reads the whole record set when the print has no hit or reaches its cap,
section 3. Its lows: the seven answers, section 9; frames 3 and 4
swapped and frame 5 parked, section 9; the sum 12 and the expectation
20, section 9; no index file, section 4; the fourth item for Roman,
section 8.

Review 1's findings:

High: 1 `Means:` dropped, section 6. 2 one derived file, no writes to
`LAWS.md` or `DECISIONS.md`, section 4. 3 the print never refuses or
decides, sections 3 and 6. 4 cause 1 rewritten, back-fill dropped,
section 2 and 9. 5 the prototype counts distinct answers under the cap,
section 9. 6 cycle rules stay, sections 3 and 5. 7 both rulings named as
amended, sections 3 and 7. 8 three items for Roman, section 8. 9 the view
deferred to frame 5 with the hash guard, sections 5 and 9. 10 `wake next`
prints four things, section 6.

Low: 11 stretched quotes marked, section 1. 12 no cache, section 4. 13
one memory retires, section 7. 14 four recurrences, section 2. 15 cause
4 added, section 2. 16 the honest price, section 9. 17 the `Law:` fit,
section 10. 18 sprint orders keyed, section 4. 19 the hook stays, section
5. 20 his words at push and ask only, section 3. The `test_vocabulary.py`
note falls with the `Derives:` line.

Usage: the four pages cost this session about 60k of context to read
(reasoned: 144k bytes at 4 bytes a token, less the truncated tail).
