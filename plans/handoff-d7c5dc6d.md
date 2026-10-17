# Momentum note of session d7c5dc6d, peer name rota-c1

Message rota-c1 for a context question before you ask Roman. Facts are in
`plans/stack.md`. This session took frame 283 from session 0e37e9d7 at
17:53 on 2026-10-17, closed its review loop at b5b14311 after seven
passes, fixed frame 143's recorded case, built frame 282's line reader,
ran four retrieval reads for frame 287, and hands off past 300k with the
reasoning of frame 287 as the next step.

## Read first: Roman's rulings of this evening, in order, in his words

1. 18:15, on frame 287's scope: "yeah the whole method, with an important
   focus on the context, looking at previous decisions/implementation etc
   entire project context, progressive re-discovery, project future
   management, etc".
2. 18:17, when asked how the investigation reads its evidence: "this is
   just a basic approach, youre not reasoning about the purpouse, not
   thinking critically, grilling".
3. 18:19, when asked which sign shows the method works: "nothing
   measurable, we stay aware of all relevant points previously discussed
   without clutter".
4. 18:22, when asked what decides which records reach a session with a
   task: "youre pissing me off, im not re-discussing this shit with you,
   the whole design and rationale should be in the logs" and "answers
   should be retreived by subagents to build understanding". Then at
   18:24: "maybe not the whole design but a lot of it".

**Do not ask him a question on frame 287 before you have read the four
pages and reasoned.** The grill on this frame is over; it was a strike.
What the pages leave open, you reason, you write, and you bring him the
design to rule on, in his words where his words exist.

## What I believe about frame 287, and what to doubt

The four pages are `plans/frame287-roman-words.md`,
`plans/frame287-rules-origin.md`, `plans/frame287-questions.md` and
`plans/frame287-context-cost.md`. Read them in that order; the first is
the longest and the one that matters most, because the design is to be
built from his words. My reading before the pages, which the pages have
since made sharper:

- The build session is the one seat with no wiring. Rota's own answer to
  the same problem is already in its composition: a seat restarts from
  records and the structure builds its wake, keyed by the wake's subject.
  Nothing builds the build session's wake. The take's read list names
  current state only; the laws, the decisions, the briefs, the archive
  and his transcript words arrive only after a question forms, and then
  only if a session remembers the rule to read them. Nineteen of 103
  questions since 2026-10-01 had their answer in a record already.
- "Aware of all relevant points without clutter" is a wake built per
  moment, not a bigger read list. The moments where a session acts on
  the past: the take, a push and its placement, a design that touches a
  door or a brief, a question that is about to go to him, a night read
  that names a cause. At each, a tool brings the points keyed by what
  the act touches: the file or function, the law or brief rule, the
  sign, and the frame. The old corpus is keyed once by agents; every new
  conclusion is keyed by the session that writes it.
- Clutter has a measured shape: the stack is 175k tokens and 55% status
  lines; a take spends 27k to 38k and most of it on the stack; the brief
  loads 8.4k every turn and half of it serves rare events; a cycle costs
  9k for 2.8k of content. The frame's state should be fields with history
  behind a pointer, a status line a reference plus a three-line
  judgement, and the brief split into what every turn needs and what a
  moment needs.
- The future, the frames and the sprints, is managed today by hand in
  prose. He does not want to order work or be asked for orders; he wants
  the meaning of a frame and the reason for its place. A frame's
  placement should carry its reason and its law line, and "what is next
  and why" should be a query, not a read of 3,400 lines.

Doubt first: whether the keyed index can be built from the records as
they are, because the stack and the archive are prose and the transcripts
are 730 MB. Prototype the keying on frames 114, 220 and 286 before any
rule is rewritten. Doubt second: whether his words already name a shape I
have not seen; read the design theme of the words page before you write
one line of design. Doubt third: my own split of what loads every turn
against what loads at a moment; the cost page's numbers decide it, not
my sense of it.

The output of the reasoning is a design record, `plans/frame287-design.md`:
the mechanism, the record shapes it needs, the moments it fires at, what
it stops loading, and the brief changes it implies, each line marked. Then
a design review on Opus, then the design goes to Roman as one
notification with the changes in his own words where they are his.

## The held frames

- **Frame 283**, the commit after an `unchanged` rewrite, sprint 12 row
  1 and the next night's wall. At b5b14311 after passes 1 to 7b and
  reviews 1 to 6; review 7 and the gate on b5b14311 were running at the
  hand-off, see the stack's last line for their result. The door refuses
  21 of 32 commits over nights 140 to 154, 20 of them right. Known reds on
  the gate: the ten names on the 17:48 line of its status, less the
  revert test. The frame cost 25 cycles against 2 priced, because a door
  that reaches into the session's store and the schema was priced as a
  text; the next price for a door of that shape is 8.
- **Frame 143**, the Tester's wrong value, row 5. The case is 5 of 5 at
  4806e99d. Four other Tester cases went red on the gate's re-record after
  the push; pass 1d's read of them was running at the hand-off, to
  `plans/frame143-pass1b-read.md`'s sibling `frame143-pass1d-read.md`.
  The likely cause: the surface block reaches every Tester encode wake,
  and cases that expect a question or a refusal now get a test. The cheap
  fix, if the read agrees: narrow the push to wakes whose criterion names
  a return value.
- **Frame 282**, the line reader, row 4. At 43be926d, review 1 stands,
  pass 2 for its two lows was running at the hand-off; commit it and the
  night validates.
- **Frame 287**, above.
- **Frame 220** row 2 and **286** row 3, the fence's baseline and the
  unnamed-definition door, both `api.py`, free now that frame 283 is at a
  commit.

The next night runs from the head after rows 1 to 4, held on frame 283
with frame 140. Frame 287's reasoning comes before it if you judge the
design changes how the night's read places walls; I believe it does, and
I would reason first and launch the night from the head while the design
review runs.

## Live agents at the hand-off

- Frame 283's review 7, to `plans/frame283-review-7.md`.
- Frame 143's pass 1d read, to `plans/frame143-pass1d-read.md`.
- Frame 282's pass 2 implementer, report under `f282/` in this session's
  scratchpad,
  `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/`.
- The gate on b5b14311 from `C:/Users/roman/rota_gate_223`, its output
  under this session's tasks directory, the newest `.output` file.
- Briefs and reports: `f283/`, `f143/`, `f282/`, `f287/` under the same
  scratchpad. Frame 287's extracted transcript text is in `f287/`:
  `roman_words.txt`, `compact.txt`, `roman_answers.txt`,
  `questions_full.txt`, and the scripts beside them.
- Worktrees: `C:/Users/roman/rota_gate_223` for the gate,
  `C:/Users/roman/rota_r283` and `C:/Users/roman/rota_r283old` for
  reviews, removable when the frame closes.
