# The wall method: from a wall to a fix that a night proves

Frame 251, the design pass. Written 2026-10-15 by an Opus agent from the
brief `f251/design_brief.md` in the holding session's scratchpad. Read-only
on the repository. Every statement is about the meta workflow, the build
session, unless a line says rota workflow, the seats.

Ground read, at HEAD 887d1470: `plans/composition.md`; `CLAUDE.md`, the
paragraph "In a loop, you diagnose" and the provisional block;
`plans/ladder-review-2026-10-15.md`; `plans/frame243-scope.md` sections 0
and 3 to 5; `plans/frame243-interview.md`; the closed frames of
`plans/archive/stack-2026-10-15.md` and `stack-2026-10-14.md`, with frames
110, 121, 152, 165, 193, 207, 215 and 227 from older archives;
`plans/frame110-interview.md`, `plans/frame165-interview.md`,
`plans/frame193-interviews.md`, `plans/frame237-interview.md`;
`plans/operating-facts.md`, the anchors and the register lines on the
probe, the gate and re-records; `probes/frame37/interview_turn.py`, its
head and its arguments; `git log --oneline -80` and the fix commits since
2026-10-04.

## 0. The method in one page

A wall is a fact from a night: a batch stopped, a seat looped, or a merge
carries what the principal declined. The method is a loop of seven steps.
Steps 3 to 5 repeat inside one frame. Each step writes one record, and the
next step reads only that record.

| Step | Input | Output | Cost | Record |
|---|---|---|---|---|
| 1. Chain | the night's records | the turns that carry the wall: each seat's call, the result, the commit | part of the night read | the night read's section |
| 2. Seam and corpus | the chain, every night that holds the seat's mode | the seam where the wrong thing first enters the build or the page; the corpus: each known instance, and the right calls at the same seam | a scope read, 1 to 2 cycles, 150k to 220k | `plans/frame<n>-scope.md` |
| 3. Reproduce | the corpus | for each instance: a control replay, byte-equal or not; an interview in the conversation; the class of the case (section 6) | 1 cycle, 70k to 105k | `plans/frame<n>-interview.md` |
| 4. Place | the class | the first move, and the test that move takes | in the holding session, under 5k | the frame's status line |
| 5. Try on the case | the move, the corpus | a replay count or a records count: instances moved, right calls broken | 1 cycle a round, 60k to 100k, 2 to 50 minutes of the card for about 120 calls | the try record, `plans/frame<n>-try.md` |
| 6. Pass | the move that passed its try | the diff, red tests first, the re-record of the touched cases, the gate, a review | 2 to 3 cycles, 75k to 120k a pass, 50k to 95k a review | the pass report and the review file |
| 7. Night | the commit | the ratio line, read with its residue rule | 0 cycles, hours of the card, the night read | the night read, the frame's close |

A move that fails its try goes up one move and returns to step 5. A move
that fails three tries, or reaches the reader or the composition, blocks on
Roman as a question (reasoned: the escalation rule of `CLAUDE.md`, "a wall
survives three cycles").

The loop holds four lines of the composition.

- **A prediction never gates.** The class from one replay places the first
  move only. The try's count gates the pass. The night's ratio gates the
  close (observed: `plans/composition.md`, Flows; reasoned: a replay is one
  sample at temperature 0).
- **The tool never rules for the principal.** A move that reads his words
  is admitted only when the count shows the reading holds on the records.
  Otherwise his words go to a reader: a seat that gets the words verbatim,
  or the principal on one line (observed: Flows; reasoned: the review,
  section 6).
- **A capability is judged by the loop it shortens.** The moves are tried
  in the order of the loop that tests them: a replay in seconds, a records
  count in minutes, a re-record in tens of minutes, a night in hours, a
  ruling in the principal's reply time (observed: The ceiling).
- **The feedback rate is the ceiling.** Step 5 exists so that a candidate
  meets its shortest loop before it meets a re-record or a night (ruled:
  Roman, 2026-10-15, "maybe we can iterate briefs on the specific case
  before doing a full re-record").

## 1. Reproduce

### 1.1 What the replay is

A replay sends one recorded turn, `turns.system` and `turns.user`, to the
seat's own model with the session's pins, as one `/api/chat` call (observed:
`plans/operating-facts.md`, the anchors, "A replay of one turn is one
`/api/chat` call with those two strings"). Three tools exist.

1. `probes/frame37/interview_turn.py`: replays one turn with no tools, adds
   a preamble and every question in one call. Arguments: `--db`, `--sid`,
   `--seq`, `--questions`, `--model`, `--think`, `--timeout`, `--host`
   (observed: the file's arguments at HEAD).
2. The conversation form, `scratchpad/f243/interview_conv.py` of session
   4754aaec: call 1 replays the turn, the night's own completion goes in as
   the assistant turn, and each question is its own user turn (observed:
   `plans/frame243-interview.md`, section 1). The same session's
   `subst_replay.py` replays a turn with one brief sentence replaced.
3. The seam probe, `seamlib.py` in the scratchpad folder `seam135` of
   session c81b16d3: it sends a recorded turn with the real door's refusal
   in place of the night's result, reads the next call, and sends that
   call through the doors (observed: `plans/operating-facts.md`, the line
   "A door that no night meets closes on a live seam").

Tools 2 and 3 live in scratchpads. The method needs them in `probes/`, so
the first frame this design pushes is their port (reasoned: a step of the
loop must not depend on a dead session's folder).

### 1.2 The control comes first

Replay the unchanged turn before any question or candidate. The replay must
give the recorded completion byte for byte. Three cases are on record.

- Frames 110, 243 and 165: the control reproduced (observed:
  `plans/frame110-interview.md`, "The replay matched byte for byte";
  `plans/frame243-interview.md`, section 1, s188 and s173; the frame 165
  review's replay, 9 of 10 sessions equal to the byte).
- Frame 237: the control did not reproduce. s187's turn 1 matched 80
  characters and then wrote `code.source` calls where the night wrote a
  prose list, 3 of 3 runs (observed: `plans/frame237-interview.md`, section
  5; `plans/operating-facts.md`, the probe line of 2026-10-14).
- Frame 135's seam probe: the control held at 3 of 4 turns (observed: the
  seam line in `plans/operating-facts.md`).

### 1.3 What the replay proves, and what it cannot

A replay that reproduces proves that the turn's prompt alone gives the
wrong call. It then proves, per candidate, whether a changed prompt gives
another call on that turn. It is one sample: the pins hold temperature 0,
so five runs are one call (observed: `plans/operating-facts.md`, "A sample
of five is one live call").

The replay cannot prove five things (observed or reasoned as marked).

1. **Spread.** One prompt hash gave 4 glossary words and later 6 at
   temperature 0 (observed: the register line of frame 237, pass 1c). Two
   replays of s173 that changed whitespace only, and no word, moved the
   seat to a right call (observed: `plans/frame243-brief-loop.md`, section
   1). One replay that moves is not a rate. Section 3.3 takes several
   samples for that reason.
2. **A cut.** The probe sends no `num_predict`, so a turn the night cut at
   the output budget does not cut on the replay (observed: the probe line
   of 2026-10-14; the gate line on the cut paths).
3. **The next turns.** A replay of turn 1 changes the result that turn 2
   would read. Only the seam probe replays a turn after a changed result
   (reasoned: each turn's prompt holds the earlier results).
4. **The chain's effect.** Whether the batch merges, cancels or loops
   depends on other seats and on rules (reasoned: the wall of frame 243 is
   s188's text read by s190, two sessions apart).
5. **Another card.** A recording made on the Titan differs from one made on
   the 3080 at temperature 0 (observed: `plans/operating-facts.md`, frame
   124). A replay runs on the card the night used.

### 1.4 The interview

Ask in the conversation form, one question a turn, with the night's own
completion in view. The stock probe asks every question in one call with no
completion, and on frame 243 it gave answers the record contradicts: s173
said "I did not write the words 'default spaced'" (observed:
`plans/frame243-interview.md`, section 1). Ask about inputs, never about
reasons alone (observed: the probe's docstring, the rule of
`rota/testkit/interview.py`). Four questions place a case:

1. What did the prompt say about the thing the call got wrong? Quote it.
2. Did you read that as a fact for this call, and which line?
3. Which line of your instructions told you to do what you did?
4. What one sentence would have moved you? Then write the call with it.

Answer 4 is a candidate for step 5, never a fix. On frame 243, s188 named a
sentence its brief already held, and under that sentence it sent the same
text byte for byte (observed: answers 4 and 5).

### 1.5 When a case has no replay

- The wrong thing was written by a rule, not by a seat: a fold, a cancel, a
  merge, a lift, a tick. Frames 225, 239 and 240 (observed: the archive).
  The case is reproduced by a unit test on the night's rows, red at the
  parent.
- The control does not reproduce: frame 237. The interview is still read
  against the record, but no replay count gates the pass. The move takes a
  records count or goes to the night.
- The wall needs the next turn after a result: use the seam probe.
- The wall sits at the principal's reading or at a ruling. No replay
  exists, because the reader is a person (reasoned).

## 2. The moves

A move is a kind of change. The list is closed by the code: every fix
commit from 2026-10-04 to 2026-10-15 is one of these moves or an instrument
fix (observed: `git log` from 2026-10-04, the `fix(...)` and `feat(...)`
headlines). The instrument, the recorder, the gate and the night cassette,
is the meta workflow and is priced in `plans/operating-facts.md`. It is not
a move.

| Move | Where | Can fix | Cannot fix | Cycles, actual | Stale cases | Its test |
|---|---|---|---|---|---|---|
| A. A result's text | a door's refusal, a note, a runner note | a seat that read a wrong or empty fact in a result: 229, 227, 165, 121 | a seat whose prompt never held the fact | 2 to 3 (229: 3; 227: 2 inside 226; 165: about 5 with two reviews) | the cases whose replay reaches the text | replay, the seam probe |
| B. A door's check | the op in `rota/roles/api.py` or `sandbox.py`: refuse, admit, offer | a call that a fact at call time shows wrong: an owner, a landed ruling, a path, an import | a judgement no record decides | 2 to 10 (219: 2; 238: 4 of 3; 230: 2; 221: 7; 234: 10) | few, unit tests | records count |
| C. A rule | a predicate, the fold, the scheduler, `mergeable`, a lift, the harness | a wrong thing done by the structure, or a door that refuses a right call | a seat's call | 2 to 10 (240: 5 runs; 239: 3 passes; 225: 10; 207: 2) | none to few | unit test on the night's rows, records count |
| D. A record's shape | the wake's user text, a page, a pre-run | a seat or a reader that lacked the source, or got it in a form it cannot read | a seat that read the source and judged wrong | 3 to 10 (110: a late pass of five, after two brief shapes; 193: a design frame) | every case of the mode | replay, records count of the field |
| E. A reply reader | `rota/core/runner.py`, the parser, a nudge, `llm.py` | a reply with no parsed call: a list, a code block, an invented result | a wrong call that parses | 2 to 8 (152: 2; 232; 237: 8 with a brief line) | the whole register when the prose changes | replay of the next turn, records count of the reply form |
| F. A mode's tools | the mode's `.tools` file | a call the mode lacks or holds and should not | a call it holds and misuses | about 2, no closed case yet (night 148's candidate M, frame 249) | the cases of the mode | replay, the tool list is in the system text |
| G. A brief line | `rota/roles/prompts/<role>/<mode>.md` | a seat that lacked a sentence, or a sentence that pulls it wrong | a seat that had the sentence and judged wrong | 2 to 8 (234 pass 1c: 2 re-records and a regression; 237: 8) | every case whose composed text holds the line | replay, section 3 |
| H. The reader | config, a route, the sandbox | a judgement a 9B seat cannot make: the principal on one line, a stronger model for one step, an executable check | nothing by itself: each sub-move has its own loop | unknown, no closed case | config only | the principal: a night and his attention; a model: replay with `--model`; a check: a unit test |
| I. The composition | `plans/composition.md` | who sees what and who rules | anything below it | a grill | none | Roman rules |

Sources for the cycle column: the "Cycles: actual" lines of the archive
(observed: `plans/archive/stack-2026-10-15.md`, `stack-2026-10-14.md`,
`stack-2026-10-13.md`, `stack-2026-10-07.md`). The stale column follows the
register lines: a `landing.md` change makes the 9 Liaison cases stale, about
45 minutes of the card; a change to the format prose of `runner.py` owes a
re-record of the whole register, about 128 live calls (observed:
`plans/operating-facts.md`, the lines on frame 234 pass 1c and on
`runner.py` prose).

**The cost does not follow the move.** Door checks cost 2 to 10. The cost
follows what the check reads: an owner or a landed ruling costs 2 or 3, a
reading of the principal's words costs 7 to 10, with false refusals found
in review each time (observed: frames 219, 238 at 2 to 4; frames 221 and 234
at 7 and 10; the review, section 2). So the order of the moves is the loop
that tests them, and the price is set from the count.

**What a replay can try, and what only a night measures.**

- Tried on the replayed case: A, D, E, F, G, and H's stronger model. Each
  changes the text one seat reads, so a replay with the change in place is
  the shortest loop.
- Tried by a records count, with no model: B and C. The check or the rule
  runs over the rows of every night that holds the seam.
- Only a night measures: the chain's effect of any move, a rule's effect on
  other batches, H's principal line, and every case with no replay
  (section 1.5).

## 3. Iterate on the case

This is the loop Roman asked for (ruled: Roman, 2026-10-15, "our briefs are
not perfect, maybe we can iterate briefs on the specific case before doing
a full re-record"). It serves moves A, D, E, F and G. One precedent ran it
and it worked: frame 234's pass 1c replayed two candidate lines on six
recorded turns at no GPU cost for the register, ranked them 3 of 6 against
6 of 6, and the chosen line then re-recorded at 5 of 5, after a first line
re-recorded untried had dropped a shift case from 15 of 15 to 9 of 15
(observed: `plans/operating-facts.md`, the line on frame 234 pass 1c).

### 3.1 The set of turns

1. **Instances**: every known instance of the wall at this seam, over every
   night that holds it, each a turn whose control reproduces. Frame 243 has
   three: s188 on night 148, s130 and s173 on night 147 (observed: the
   scope, section 3).
2. **Right calls**: recorded turns of the same mode where the seat did
   right, at least as many as the instances, at most ten. For frame 243:
   contested respecifies with right text, from the 60 on nights 145 to 148
   (observed: the scope, 4.1).
3. **Register cases**: every case whose composed text holds the changed
   text. List them before the try, not after (observed: the register line
   on `ask.md`, "list every case whose composed text holds the line").

### 3.2 The measured fact the round is built on

The loop ran once on frame 243, before this design, and its result sets the
round's shape (observed: `plans/frame243-brief-loop.md`, 2026-10-15 02:27,
eight lines, sixteen replays, one sample per seat per line, temperature 0).

- No line moved both seats. Line 1 moved s188 and half of s173. Line 5, the
  keep sentence removed, moved s173 and not s188 (section 0 of the report).
- Two controls that changed whitespace only, no word, moved s173 to a right
  `cj_compact` (section 1 of the report).
- Line 1 moved s188 in the loop. The same words with one line break inside
  them did not move s188 in the interview (section 0 of the report;
  `plans/frame243-interview.md`, section 4).

So one replay at temperature 0 is one sample, and a whitespace change is
enough to move a seat that sits at a tipping point. A move on one replay
says little about a line's meaning (reasoned: the three facts above). The
night also runs at temperature 0, and its prompts differ in their working
set from wake to wake, so the spread over small perturbations is the
spread the night meets (reasoned: `plans/operating-facts.md`, "Sizes go up
and down between the turns of one session").

### 3.3 One round

1. Write one to three candidates. Take each from the interview's answers and
   from the brief's own wording, never from a phrase of the night's
   sentence (reasoned: a line that names a wrong word pulls the seat to it,
   `plans/operating-facts.md`, frame 234 pass 1c). A removal of a sentence is
   a candidate too: line 5 of frame 243's loop was the only line that gave
   s173 a fully right call (observed: the report, section 4).
2. Make five samples of each candidate, and of the unchanged brief, the
   null. A sample is the prompt with one fixed perturbation that changes
   no word: as written; the paragraph's line breaks made spaces; two
   newlines after the paragraph; one newline before it; the candidate on
   its own line. The same five perturbations serve every candidate and the
   null, so the samples are paired (reasoned: the report's two controls are
   two of these five, and the pins hold temperature 0, so a repeat of one
   prompt is no sample, `plans/operating-facts.md`, "A sample of five is
   one live call").
3. Replay every sample on every turn of 3.1, items 1 and 2, at the
   session's pins.
4. Score each reply with a script, never by eye. "Moved" means the reply's
   call passes the predicate the night's ratio uses: for frame 243, the
   respecify text holds no format the principal declined and drops no
   clause his words add. "Broken" means a right call's reply changes its
   call, its count or its form. The whole reply is scored, not the target
   call alone: frame 237's candidate moved the form 3 of 3 and wrote 54
   calls where the brief asks for a few (observed:
   `plans/frame237-interview.md`, section 5); frame 243's line 1 moved
   s173's `cj_compact` and lost "TypeError" from `cj_serializable`
   (observed: the report, section 3).

### 3.4 The thresholds

1. **A tipping turn is not counted.** A turn whose null moves in 2 or more
   of 5 samples sits at a tipping point. It leaves the count for this
   round, and the try record names it. On frame 243, s173 is such a turn
   (observed: the report, section 1, 2 of 2 perturbations moved it).
2. **A turn is moved** when the candidate moves it in 4 or more of 5
   samples (reasoned: 4 of 5 against a null of at most 1 of 5 is a gap
   that a whitespace change did not make on the measured case).
3. **A right call is broken** when the candidate breaks it in 2 or more of
   5 samples.
4. **A candidate passes** when it moves at least half of the counted
   instances, breaks no right call, and at least one instance is counted.
   The bar is a ratio and never a zero, by the ruling of 2026-10-03 on a
   stochastic seat (observed: `CLAUDE.md`, the three parts of an
   ends-when).

The thresholds are (reasoned) until a second wall measures them. The first
frame that runs the loop writes its counts beside them in the try record.

### 3.5 When the loop stops and the move goes up

- **Two rounds**, six candidates, with no pass. The move goes up (reasoned:
  frame 110 tried two brief shapes and a door over five passes before the
  record shape moved it, `git log` 7da1d435 to e7cd1b39; frame 243's loop
  ran eight lines and found none that moved both seats, the report,
  section 4).
- **At once**, before any round, when every instance is a tipping turn or
  the control does not reproduce. The replay cannot measure the case
  (section 1.5).
- **After one round**, when the interview named a sentence that the brief
  already holds and no candidate moves that seat in 4 of 5. The seat had
  the sentence and judged wrong (observed: s188, answers 4 and 5,
  `plans/frame243-interview.md`; s188 moved on 1 of 8 lines in one sample,
  the report, section 4).

"Goes up" means the next move the placement test names for the case
(section 6), not the next row of the table. On frame 243 the loop's own
reading is that a brief line does not answer s188 (observed: the report,
"Reading for the frame").

### 3.6 The re-record, and when it runs

The re-record runs once, in the pass, after a candidate passes. It is never
the try. The pass runs the touched test files, then the gate, and the gate
re-records its stale set one case at a time (observed:
`plans/operating-facts.md`, the gate lines from frame 89). Its cost: about
15.7 seconds a case live; the 9 Liaison cases about 45 minutes of the card;
runner prose about 128 live calls, tens of minutes (observed: the same file,
the re-record lines). A register case that goes red under the passed line
is a broken right call that the try missed. Add its turn to the set of 3.1
and run one more round before the pass continues (reasoned: the set grows
with each miss, and the next wall's try starts from it).

### 3.7 The price of a round

One cycle: an agent on Opus, 60k to 100k, writes the candidates and the
perturbations, runs the replays and the score script, and writes the try
record (reasoned: frame 243's interview cost 82.3k on the harness line for
fewer calls, `plans/stack.md`, frame 243's status of 01:37). The card time
is turns times candidates plus the null, times five samples. Frame 243's
shape, 3 instances and 3 right calls, 3 candidates and the null, is 6 x 4 x
5 = 120 calls. At 1 s to 25 s a call that is 2 to 50 minutes of the card
(observed: the call times in `plans/frame243-interview.md`, 1 s to 25 s).
The null's 30 calls serve both rounds, so round 2 costs 90. The replay
does not run beside a gate or a night that uses the card (observed: the
seam line, `qwen3:8b` left the card at the probe's first call).

## 4. The count

### 4.1 For a check or a rule, moves B and C

The test is the review's (observed: `plans/ladder-review-2026-10-15.md`,
section 3). **Run the predicate on the records of every night that holds the
seam. It fires on each known instance and on no right call.** Write the
count as two numbers: fires on a of n instances, and on b of N right calls.

- A predicate that fires on one instance in N is overfit, whatever its
  words. Frame 243's lexical door fired on 1 of 60 contested respecifies and
  reached 1 of 3 cases (observed: the scope, 4.1 and 5.1).
- A cue list that fires on many with no false refusal is not overfit.
  Frame 234's doors refused 13 to 20 over-contests and 0 right rulings on
  five nights (observed: the review, section 3).
- The count reads the nights that hold the seat's mode, not only the nights
  that hold the wall. Frame 243's count read nights 145 to 148 (observed:
  the scope, the sources).

A door also has a step. Follow each sentence of the refusal exactly on the
replay, because a refusal that names a next call is a route (observed:
`plans/operating-facts.md`, the frame 135 line: four reviews each found a
hole behind a sentence). So a door's try is the count plus a seam probe on
the instances: the seat's next call after the refusal.

### 4.2 For a move a replay cannot test

The equivalent of the count has three parts.

1. **Red first on the case.** A unit test built from the night's rows is
   red at the parent and green after. Frames 238 and 239 did this (observed:
   the archive, "2 red on 9624565c").
2. **Reach.** Count over every night's records how often the rule's input
   condition occurs, and how many of those the change alters. Frame 243's
   record-shape candidate counts the declined merges where the builder's
   prompt lacked a ruling with words: 3 of 3 (observed: the review, section
   5). A reach of one is the same sign of overfit as a predicate's.
3. **No right path changed.** Of the occurrences the change alters, name
   each one that was right on the night. That number must be 0.

A move that neither a replay nor a count can test, H's principal line or I,
has no equivalent before the night. Its price is the principal's attention,
and it is a ruling, so it is a question to Roman with a rating (observed:
`CLAUDE.md`, the rating rule).

## 5. The night

The ends-when line keeps its three parts (observed: `CLAUDE.md`, the ruling
of 2026-10-03).

1. **The mechanism**: what the move meets, which the pass builds and the
   review checks. For a replay move, the try's count is part of it.
2. **A ratio with the baseline of the night that found the wall**, never a
   zero. Frame 243: merges that carry what the principal declined, from 1
   of 3 on nights 147 and 148 toward 0 of the next 3 (observed: the scope,
   4.5).
3. **The residue rule**: a session that still shows the sign is read, and
   the frame closes when its cause is not the cause the frame named. That
   cause is a new frame. Frame 234 closed this way, its residue m81 went to
   frame 243 (observed: the archive, frame 234's close).

Two night rules apply to the loop.

- A door that no night meets closes on a live seam probe, not on more
  nights (observed: `plans/operating-facts.md`, frames 135 and 136).
  Frames 228 and 229 closed "on the door test, because the door never fired
  in three nights" (observed: the archive). The seam probe is the stronger
  close.
- A night that loops on another frame's wall is stopped (observed:
  `CLAUDE.md`, the ruling of 2026-10-09 20:19).

When the night's ratio fails and the residue's cause is the frame's own
cause, the loop returns to step 3 with the night's new instances added to
the corpus. The move that failed on a night goes up, by the same rule as a
failed try.

## 6. The placement test

### 6.1 The test

Ask the questions in order, from the chain and the interview. The first yes
gives the first move.

1. **Did a rule do the wrong thing, not a seat?** A fold, a cancel, a merge,
   a lift, a tick, a wake, or a door that refused a right call. Then move C
   at that rule.
2. **Did the reply hold no call that the parser reads?** A list, a code
   block, a call in prose, an invented result. Then move E, with move G for
   the call's written form.
3. **Did the result the seat read state a wrong fact, or none?** Then move
   A, tried on the replay.
4. **Did the seat's prompt lack the fact the right call needs?** Then the
   fact is a record. If the seat must read it before it acts, move D. If the
   fact is checkable at the call, move B, and its refusal states the fact.
5. **Did the prompt hold the fact in a form the seat did not read?** The
   interview shows it: the seat quotes something else, or cannot find it.
   Then move D, tried on the replay.
6. **Did the seat lack a call, or hold one it should not?** Then move F.
7. **The seat read the fact and judged wrong.** Then two tests run, and the
   cheaper that passes wins:
   - a predicate that decides the right call, counted by section 4.1: move
     B;
   - a brief line, iterated by section 3, unless the interview names a
     sentence the brief already holds.
   If neither passes, look downstream: does a later reader lack the source
   that would undo the wrong call? Then move D at that reader. Else move H.

A case with several seats is placed per seat, at the seam where the wrong
thing first enters the build or the page (observed: frame 243's scope, seam
1, "the build reads the criterion and nothing else").

### 6.2 The test on the closed frames

| Frame | The wall | What the seat lacked, by the read or the interview | Fix that closed it | Night count at the close | Test gives | Match |
|---|---|---|---|---|---|---|
| 110 | a challenged test rewritten into the same fault | the failure sat inside an escaped JSON string; the seat read a criterion question | after two brief shapes and a reverted door: the failed run as plain text above the JSON, e7cd1b39 (D) | closed on the gate, night 107 fired no challenge | Q5: D | yes |
| 121 | three runner notes tell the seat a wrong thing | a true fact in the note | the runner's note texts (A) | false in 0 of 44 events on two nights against 18 of 38 | Q3: A | yes |
| 152 | the Tester writes its repair in a code block, no call | the reply held no call | the runner's nudge (E) | 1 of 15 against 2 of 5 | Q2: E | yes |
| 165 | the Developer sends a call after "End the session with no call." | had the step, placed it with the system | the step's text, tried on 10 replayed sessions (A) | 1 of 1 against 1 of 11 | Q3: A | yes |
| 193 | a second request's words land on the first request's item | `current_request` naming s1 tied the words to s1 | a design frame: the predicates that present an earlier item, and the wake's request (C and D) | 0 of 20 pages against 12 of 30 | Q1: C at the predicates; Q5 gives D for the Liaison | partial |
| 198 | the agenda tick puts a merged request's rows on the next page | nothing, a rule | the agenda tick (C) | 0 of 9 pages | Q1: C | yes |
| 207 | an inherited test runs without its warning filter | nothing, the harness | the harness flag and the door's account (C, A) | 0 of 4 on two nights against 1 of 1 | Q1: C | yes |
| 213 | a cancelled batch's test stays on every page, and the relay is refused | nothing, a door refused a right call | the relay refusal and the page's check line (C, D) | 3 of 5 answers reached a Tester; closed by the residue rule | Q1: C | yes, D beside it unnamed |
| 219 | a Vision Keeper overwrites the principal's decision | the row's owner was not in its prompt | `decisions_author` refuses a write under another author (B) | 0 of 10 principal rows changed | Q4: B | yes |
| 221 | a Vision Keeper's assert rewrites the principal's request | the item was live and his | the assert door, three passes, two reviews on false refusals (B) | 0 of 4 batches abandoned | Q4: B, and the count first on its reading of his words | yes; the count was not run, and the cost was 7 of 4 |
| 225 | a contested note's fold overwrites his approve | nothing, a rule | the fold (C) | 0 of 9 pages, 0 of 3 nights | Q1: C | yes |
| 226 | a repair rewrites a corrected criterion back | nothing, the predicate woke the repair | the `criterion_repair` predicate and the respecify door (C, B) | 0 of 1, 0 of 3 over two nights | Q1: C | yes |
| 227 | a relay lands `unchanged` with a silent note | the note did not say he contested | the `unchanged` note's text and the contested-sentence refusal (A, B) | 0 of 14 against 2 of 4 | Q3: A | yes |
| 228 | the touch judge matches a stray by exact path | nothing, the door dropped a right judgement | the judge at symbol grain (C) | 0 of 0, three nights | Q1: C | yes |
| 229 | the cycle door names `from .core import` for any name | the refusal stated a false fact | the refusal's text names the defining module (A) | 0 of 0, three nights | Q3: A | yes |
| 234 | the Liaison contests a line his words match | had "Lines 1 to 4 match what I asked for" and contested them | the verdict door's cue reading (B), with one brief line tried on six turns (G) | 0 of 3 cancels, 0 of 6 over two nights | Q7: B by the count, 13 to 20 fires and 0 false | yes |
| 237 | the survey writes `glossary.amend` as a list | no written-out call to copy | the brief's call written out and the runner's list account (G, E) | 0 of 5 quarantined | Q2: E with G | yes |
| 238 | a Vision Keeper contests an item his reply approved | the landed ruling was not in the relay | the door reads the landed ruling (B) | 0 of 3, the door never fired | Q4: B | yes |
| 239 | a re-dispatched batch merges with no test | nothing, a rule | `mergeable` and two readers count the batch's own tests (C) | validating, 0 of 0 | Q1: C | yes |
| 240 | a quarantine outlives the approve | nothing, a rule | the lift on a landed ruling (C) | 0 of 3 walk ends | Q1: C | yes |
| 243, open | the merge carries the declined format | s188 read his words and judged the format kept; s190, the builder, had no ruling in its prompt | not closed | 1 of 3 merges | s188, Q7: the door counts 1 of 60, and no line of eight moves both seats, so downstream; s190, Q4: D, the ruling's words beside the criterion | the review's fix, unproved |

Sources: the Site and close lines of each frame in the archives named in
the header, and the fix commits; the interview files for 110, 165, 193, 237
and 243.

### 6.3 The frames where the test fails

- **Frame 193, partial.** The test gives one move per seat, and frame 193
  was a design frame over four walls with predicates and the wake's content
  together. The test names C first, because a predicate presented the old
  item, and it names D for the Liaison only when the Liaison is placed as a
  second seat. A seam design over several walls is placed per wall, and
  the test does not say so of itself (reasoned: the frame's Site line names
  four frames).
- **Frame 213, partial.** The test names C for the relay refusal. The page's
  check line, a record shape, was a second wall in the same frame. The test
  gives the first move, not the second.
- **Frame 221, the cost.** The test gives B, which is the fix. It also says
  that a check which reads the principal's words takes the count first.
  The frame ran no count, and its reviews found false refusals from the
  removal-word rule twice (observed: the scope, 5.2). The test would have
  changed the order of the work, not the move.
- **Frame 110, the order.** The test gives D at once from the interview's
  answer, "the same line sits inside an escaped JSON string". The frame
  tried two brief shapes and a door first, because the interview ran after
  them. The test matches the final fix, and the frame shows the cost of the
  steps before step 3.

No closed frame was fixed by move F or H. The test has no evidence for
those two moves (observed: the table).

## 7. What the first ladder got wrong

1. It was a list of places ordered by a price the actuals refute, not a
   loop: a door cost 2 on frame 219 and 10 on frame 234, so the order must
   be the loop that tests each move, with the price set by the count.
2. Its test checked a predicate's words and placed a case from one replay,
   so it passed the lexical door that the count shows overfit, and it gave
   no test at all for a brief line or a record shape.
3. It had no step that tries a candidate on the replayed turns before the
   pass, so brief lines met the register untried, as on frame 234's pass 1c
   and frame 243's candidate line.

## 8. The block for `CLAUDE.md`

The block below replaces the provisional block, from "**Provisional until
frame 251 closes**" to "and the price follows the count." It keeps the
paragraph "In a loop, you diagnose" above it.

```
**A wall's fix comes from a loop, and each move is tried in its shortest
loop before a pass** (ruled: Roman, 2026-10-15 02:22, "the ladder needs
design and review passes itself"; design: `plans/wall-method-design.md`).

1. Chain: the night read names the turns that carry the wall.
2. Seam and corpus: a scope read names where the wrong thing first enters
   the build or the page. It lists every known instance and the right
   calls of the same mode, over every night that holds the seam.
3. Reproduce: replay each instance unchanged first. The replay must give
   the recorded reply byte for byte. Then interview in the conversation,
   one question a turn, with the night's reply in view.
4. Place: ask in order, and take the first yes. A rule did it: change the
   rule. The reply had no call: the reply reader. A result stated a wrong
   fact: its text. The prompt lacked the fact: the record a seat reads, or
   a door that states it. The fact was there in a form the seat missed:
   the record's shape. The seat lacked a call: the mode's tools. The seat
   read the fact and judged wrong: a counted door or an iterated brief
   line, else the source for the next reader, else the reader itself.
5. Try: a text move is replayed on every instance and on as many right
   calls, in five samples that change whitespace only, beside the same
   five of the unchanged brief. One replay at temperature 0 is one
   sample, and whitespace alone moved a seat (observed:
   `plans/frame243-brief-loop.md`). A turn the null moves in 2 of 5 is
   not counted. A turn is moved at 4 of 5. A line passes when it moves
   half the counted instances and breaks no right call in 2 of 5.
   A door or a rule is counted on every night's records: it fires on each
   instance and on no right call. A predicate that fires on one instance
   is overfit, whatever its words. Score with a script, never by eye.
6. Pass: red tests first, then the re-record of the touched cases at the
   gate. The re-record is never the try.
7. Night: the ratio line with its three parts and the residue rule.

Stop a brief line at once when the interview names a sentence the brief
already holds. Stop any try after two rounds with no pass. A stopped move
goes to the next answer of step 4. Three moves that fail, or a move that
reaches the reader or the composition, block on Roman with a rating. A
placement from one replay is a prediction. The try's count gates the
pass, and the night gates the close.
```

The block is 38 lines inside the fence.
