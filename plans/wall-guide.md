# The wall guide: how to decide the fix of a wall

Frame 251, the wall guide. Designed 2026-10-15 on Fable by an agent of
session dae006d1, from first principles, with `plans/wall-research.md` and
its six tables as the evidence. Every statement is about the rota workflow,
the seats, unless it says meta workflow, the build session. A number copied
from a record keeps that record's mark and date. Every frame is named with
its number and its name.

## 0. What this guide is for

Roman's purpose, in his words (ruled: Roman, 2026-10-15, in the terminal,
`plans/wall-research/rulings.md` entries 7 to 13 and 43):

- "I just want to spend time to reason about all the kinds of problems that
  we can have with walls in rota and make a reasoning guide for future
  sessions to offload that work off them."
- "It's a guide to making decisions about how to fix walls. So night reader
  maybe, solution designer definitely."
- It makes three decisions easier: where the fix goes, by kind of problem;
  whether to fix at all; whether a fix overfits the night. Not how much to
  spend.
- Two walls are one kind by "the same cause in the structure".
- "If a wall is only a small inefficiency and we can't fix it easily then
  leave it ... we either can fix it cheaply (which is what the guide
  documents) ... or if we dont expect anything in the wall ladder to fix
  it, escalate all the way to the top so that we can discuss the problem
  and design at the highest level." Then: "for now there is only cheap and
  escalate to me."
- On overfit: "this is the kind of knowledge that we just have about the
  project."

The build session wakes cold, like a seat. Before this guide, the project's
judgement about walls sat in 150 frames, the archive, the decisions and the
operating facts, and every hand-off relearned it. This guide is the record
the designer restarts from, so a wall costs one or two cycles and not five
to seven, and Roman sees only what is new (ruled: Roman, 2026-10-15, "Yes
that's exactly it").

What this guide is not: a method, a ladder, or a price list. The loop of
steps is `CLAUDE.md`'s proposed block and the design records. This guide
reasons about causes and the decisions each cause points to.

## 1. The structure, and the failures it permits

The composition is one page, and every cause below comes from one of its
lines (observed: `plans/composition.md`, ratified 2026-09-16). A reader
rebuilds section 2 from this page.

**The parties.** The Principal is in the team. He holds intent, speaks,
writes no records, and his attention is the scarcest budget. The Liaison
faces him, infers his intent, and checks the reading. A seat is a small
model that wakes cold, acts once and ends. It reads only what the wiring
pushes into its prompt. The structure, not a seat, decides what happens
next. Capability comes from wiring. No brief grants what is not wired.

**The records.** Every record has one writer. Work is re-derived from the
records each pass. Nothing stops quietly. A record says whether it was
observed, reasoned or decided.

**The flows.** Intent flows down: Principal, Liaison, records, seats.
Evidence flows up the same path. A prediction never gates. The tool never
rules for the Principal. Every claim cites a source.

**The ceiling.** The feedback rate is the ceiling. A weak model is trusted
only as far as the loop that checks it is short.

**The build session.** The same composition, a second instance: one strong
model in one context, about twenty cycles a sprint, that reads a night,
names walls and designs fixes.

From these lines, what the structure permits at each place:

1. **At every hop of intent down**, a cold seat rewrites what came in. His
   words can be lost (no slot for them), reversed (a yes-with-correction
   read as a yes), merged with what he declined, or paraphrased. Each hop
   is a model, and the next hop reads the rewrite, not the words
   (reasoned: "Intent flows down: Principal, Liaison, records, seats").
2. **At every seat**, the prompt is the whole world. The wiring can leave a
   fact out, the window can drop it, the world can hold it in no record,
   the wiring can push it in a shape the small model does not read, or the
   seat can read it and judge wrong. Five different causes, one sign each
   (reasoned: "Each seat wakes cold, acts once, and ends"; "Capability
   comes from wiring").
3. **At every record**, a rule re-derives work from rows. A row can be
   stale, belong to another batch or request, carry a key a seat can vary,
   or outlive its cause. The rule then wakes the wrong seat or shows the
   wrong page (reasoned: "Outstanding work is re-derived from the records
   each pass"). Two records about one fact have two writers and no
   reconciler but the cascade (reasoned: "Every record has one writer").
4. **At every instrument**, the wiring reads a reply, admits or refuses a
   call, and tells the seat why. A parser can read a reply wrong. A door's
   predicate can be wider or narrower than its fact. A refusal's text is an
   instruction a small model follows literally, so a wrong step is a wrong
   act. A mode can lack the call the act needs (reasoned: "No brief grants
   what is not wired"; the small-model limits C1 to C5 in
   `plans/wall-research/small-model.md`).
5. **At the top of evidence up**, the page is the one surface he sees. A
   page can show rows that are not his, and his answer then lands on a
   wrong row, which corrupts intent down (reasoned: "Evidence flows up the
   same path"; "attention is the scarcest budget").
6. **At the measuring instrument**, the night read counts through code the
   build session wrote. A wrong instrument puts the wall in the wrong place,
   and a count from it is a prediction wearing the word observed (reasoned:
   "A prediction never blocks").
7. **At the build session**, the session names the wall from a status line
   and not from the turns, and prices the fix by its own cycles. A door is
   one cycle and a design is ten, so a session reaches for the door. Its
   own fix is then the next wall (reasoned: the build session is a second
   instance of the composition with twenty cycles a sprint).

The ceiling line sets the shape of every fix: a fix holds when it shortens
the loop that checks the seat, or gives the next seat a fact, and it fails
when it asks the same seat to judge better (reasoned: "A weak model is
trusted only as far as the loop that checks it is short").

## 2. The causes

Fourteen causes. Thirteen are rota's, and one is the build session's. Each
entry names its line, how it shows on a night, how to confirm it, the cheap
fix with its evidence, what overfits, when to leave it, and when to
escalate. The October frames placed under each cause are this pass's
placement from the research's rows (reasoned: `plans/wall-research/frames.md`,
columns 3 and 4, re-read against the structure; no turn was read). The
research's own placements differ in 16 rows, listed in section 6.

### Cause 1. His words change on a hop

- **Line.** "Intent flows down: Principal, Liaison, records, seats" and
  "The tool never rules for the Principal". Each hop is a cold model that
  rewrites what it read, and the wiring has a fixed vocabulary for what his
  words can become, the ruling words (reasoned: the composition, Flows;
  `rota/roles/api.py:8292`, `RULING_WORDS`).
- **On a night.** A merge carries what he declined. A criterion's text
  holds a format he contested. A relay lands `unchanged`. A `drop` or "a
  separate request, for later" lands as a contest. A re-annotate keeps the
  files he declined. A yes-with-correction reaches nobody.
- **Confirm.** Open the chain in the night database: his verbatim words,
  the Liaison's verdict, the ruling row, the criterion's text after each
  seat, the page he saw. The hop whose output first differs from his words
  is the seam. Two shapes: a hop had no slot for the word (mechanical), or
  a seat read the words and wrote something else (judgement). Frame 243's
  scope read is the worked case: s188 kept the format, s190 built from the
  criterion alone, and no code read `decisions.supersedes` (observed:
  `plans/frame243-scope.md`, 2026-10-15).
- **Cheap fix.** For the mechanical shape, the slot: a ruling word, a
  route, a field. For the judgement shape, do not fix the hop. Give the
  next seat his words beside the record it builds from, because the
  downstream seat reads the record and not the words. Frame 243's pass puts
  the contest ruling's words whole beside the criterion in the Developer and
  Tester wakes, reaching 559 of 2402 such wakes over nights 137 to 148
  (observed: `plans/frame243-try.md`, 2026-10-15). It validates on night
  149. Frame 227, a relay of his correction lands unchanged, closed at 0 of
  14 against 2 of 4 by a door that names his contest (observed:
  `frames.md`, 2026-10-13). Frame 226, a repair rewrites a corrected
  criterion back, closed at 0 of 3 over nights 145 and 146 after its token
  set was cut to what his words do not name (observed: `failed-fixes.md`
  row 11).
- **Overfits.** A door that reads his words for a meaning. Frame 243's
  lexical door fired on 1 of 60 contested respecifies; its presence rule
  would refuse about 59 of 60 right paraphrases; frame 234's door was
  silenced by one added sentence in 74 of 131 replies; frame 226's first
  token set refused `version_option`, "the name the principal's own words
  ask for" (observed: `failed-fixes.md` rows 11, 13, 15, 16). A brief line
  at the hop: frame 243 replayed eight lines, and "no line moved both"
  seats, while two whitespace-only controls moved one (observed:
  `plans/frame243-brief-loop.md`). This cause's closes cost the most, 7 to
  10 cycles a wall (observed: `plans/wall-method-fit-review.md` section 3).
- **Leave it.** Never, when the effect reaches a merge or a page. The
  composition names it: a seat's row then stands over his.
- **Escalate.** When the fix would read his words for a meaning, or would
  add a vocabulary for what he may say. Already ruled: "the door approach
  cannot be used for every issue identified" and "it's not as simple as
  adding a reminder" (ruled: Roman, 2026-10-15 00:50 and 00:51 UTC); the
  principal's words always land on a row (ruled: Roman, 2026-10-08,
  `rota/DECISIONS.md` line 1445); the Liaison's verbatim words and confirmed
  reading are two records (ruled: Roman, 2026-09-16, the composition).
- **October frames, 9:** 227, 226, 234, 250, 243, 244, 196, 192, 185.

### Cause 2. The prompt lacks the fact

- **Line.** "Each seat wakes cold" and "Capability comes from wiring". The
  wiring chooses what to push, and the window bounds it, so a fact the
  wiring left out or the window dropped does not exist for the seat
  (reasoned: the composition, A model).
- **On a night.** The seat re-reads a span it already read. A tail reply
  empties the window's middle. A wake holds one traceback 34 times and no
  source. A repair pre-run shows no expected files. A test asserts a default
  the function lacks.
- **Confirm.** Open the seat's turn in the night database and search the
  prompt for the fact. Absent: this cause. Present: cause 4 or 5. Check the
  eviction notices and the prompt's size against `num_ctx`, because a
  prompt one token over loses its front (observed: finding 79,
  `plans/operating-facts.md`, 2026-09-15).
- **Cheap fix.** A runner change in the wake builder or the window rule,
  2 cycles. Frame 120 closed at 7 of 7 wakes holding a `code.source` block
  against 0 of 3; frame 108 closed at "a middle read survived in all 4",
  8 against 21 on night 109; frame 119 closed by the residue rule on night
  116 (observed: `frames.md`, 2026-10-04 and 2026-10-05). Frame 243's
  record shape, above, is this fix applied one seat below a cause-1 wall.
- **Overfits.** A sentence that tells the seat what to do about the gap.
  Frame 119's eviction sentence, "ask once more and it is served again",
  made three seats repeat their calls at temperature 0 and was reverted;
  frame 169 rebuilt it only where the answer's span is gone, and frame 208
  is open on that rebuild's own match (observed: `failed-fixes.md` row 2).
  A larger push is not the fix either: "pushing more of the artefact is not
  the same as pushing the right part" (observed: `rota/DECISIONS.md` line
  417).
- **Leave it.** When the seat recovers the fact by a call the mode has, and
  the cost is steps only.
- **Escalate.** When the fact does not fit the window beside the brief,
  because the window is a budget and every cap is his ruling (law 7).
- **October frames, 8:** 108, 119, 120, 134, 139, 127, 143, 217.

### Cause 3. The fact is in the world and in no record

- **Line.** "The structure holds a model of its shape, terms, boundaries
  and external commitments, as records observed from the code." A fact of
  the project's runtime or the test harness that no record holds cannot be
  pushed into a prompt, and a small model does not infer it (reasoned: the
  composition, The project).
- **On a night.** A test is red on a runtime error the seat repeats. A
  `CliRunner` call swallows a `NameError` and the output is empty. A
  decorator turns a function into a Click command and the plain call fails.
  A merged change raises on a path its tests never take.
- **Confirm.** Ask whether the error holds under every model: run the test
  body by hand. If the error is a fact about files, the index, the database
  or the harness, it is this cause. If "display means return or print" is
  the question, it is a judgement, cause 5 (observed: `rota/DECISIONS.md`
  line 943, the line kept at walk twelve).
- **Cheap fix.** A door that states the fact, with its count on every
  night's encode bodies, 2 cycles. Frame 131, a test calls a plain function
  as a Click command, closed at 0 of 4 from 3 of 3 on night 127, ruled over
  the per-wall order as a design frame on a shared cause (observed:
  `frames.md`; the fit review section 2). Frame 230, its residue, flagged
  67 of 1,153 bodies with 0 false refusals in review (observed: frame 230's
  review 1, 2026-10-15, quoted through the Opus draft, section 4). Frame 195 closed as an instrument fix at 0 of 7
  against 10 of 11 (observed: `frames.md`, 2026-10-11).
- **Overfits.** One door per runtime shape. Frame 131's plain function came
  back as frame 230's lambda, and `hello.main` and `self.runner.invoke` are
  still admitted (observed: the Opus draft, section 4, frame 230). A door
  that enumerates shapes is a list that the next shape escapes.
- **Leave it.** When the harness catches it at the merge gate and the cost
  is one attempt.
- **Escalate.** When the fact is about the target project and a seat should
  learn it, because the Researcher is the one seat that brings the world in,
  as cited records (the composition, Flows; `rota/LAWS.md`, L0).
- **October frames, 5:** 131, 195, 223, 230, 172.

### Cause 4. The prompt holds the fact in a shape the seat does not read

- **Line.** "Each seat wakes cold" and the ceiling. A small model acts on
  the shape of its prompt as much as its content: it follows the literal
  last line, needs a form to copy, and reads runner text with no speaker
  mark as its own reply (observed: `small-model.md` groups A1, B, C, D, 25
  limits, 2026-10-15).
- **On a night.** The seat acts against a fact its prompt holds. A failure
  line sits inside an escaped JSON string. A step "End the session with no
  call" is followed by a call. A reply holds the act in a code block and no
  call. The seat copies the brief's example word for word. The seat takes
  the first row of an unhinted list.
- **Confirm.** The interview in the seat's exact context, one question a
  turn, with every answer read against the record, because the model's own
  account disagrees with the record in 3 of 4 turns (observed:
  `small-model.md` G1). Frame 110's interview found the JSON string in one
  call after three passes had not (ruled: Roman, 2026-10-02 15:02,
  "interview the model").
- **Cheap fix.** The record's shape or a form to copy, 2 to 3 cycles. Frame
  165: the step as a one-line reply form, the old step 0 of 5 and the form
  5 of 5 on replay, 1 of 1 on night 127, "one case is thin" (observed:
  `failed-fixes.md` row 7). Frame 237: a written-out call example moved the
  form in 3 of 3 replays, and the night closed at 0 of 5 survey wakes
  quarantined (observed: `small-model.md` D3; `frames.md`). Frame 215: a
  door, 0 of 3 and 0 of 4 against 1 of 2 (observed: `frames.md`). A brief
  line closed 1 October wall, frame 237 (observed: `frames.md` section 3).
- **Overfits.** A brief line measured on one case. Frame 234's line took a
  shift page from 15 of 15 to 9 of 15; frame 82's headline took two cases
  from 2 of 5 and 5 of 5 to 0 of 5 and 3 of 5; one sentence in the runner's
  format prose took a survey case from 770 of 780 to 0 of 20 (observed:
  `plans/operating-facts.md`, the brief rulings). One replay is one sample
  that whitespace moves (observed: `plans/frame243-brief-loop.md`). A line
  that helps one model and hurts the other is emphasis, not a fix
  (observed: `rota/DECISIONS.md` line 347).
- **Leave it.** When the seat reaches the act by its second turn and no
  door loops it.
- **Escalate.** Never for the shape. The brief is the session's to write
  and measure (ruled: Roman, 2026-09-02, "the system prompt is where the
  real work is").
- **October frames, 7:** 215, 214, 184, 110, 165, 152, 237.

### Cause 5. The seat has the fact, reads it, and judges wrong

- **Line.** The ceiling: "A weak model is trusted only as far as the loop
  that checks it is short." A judgement is not a predicate, and what no
  invariant can see is "perfect form with wrong meaning; plausible-but-wrong
  judgement" (observed: `rota/DECISIONS.md` line 1186, 2026-08-29).
- **On a night.** A Tester writes a test that never runs the behaviour. A
  Developer fits the wrong test, or writes back the line it says it
  removes. A touch judge calls the item's own file a mistake. A seat
  respecifies and keeps the declined format because "the format was not
  rejected" (observed: `plans/frame243-interview.md`, s188).
- **Confirm.** Rule out causes 2 to 4 first from the prompt and the
  interview. The model is the last suspect: on 2026-09-14 and 15 the
  instrument, the wake, the brief and a mode's tools were each wrong before
  the model (ruled: Roman, `plans/operating-facts.md`). Then ask whether a
  stronger model does the act on the same turn, because "if not then it's
  the structure's fault" (ruled: Roman, 2026-09-23 14:08 UTC).
- **Cheap fix.** None on the seat. What closed walls here moved the check:
  give the next seat the fact (cause 2's fix, frame 243's record shape), or
  a door where the wrong act leaves a mechanical trace, or a challenge that
  must quote both rows, because "when two outcomes cost that differently,
  which one you get is decided by noise" (observed: `rota/DECISIONS.md`
  line 1248, ruled 2026-08-26). Frame 200, the build loop, took 46 cycles
  against 8 to 10, closed at 5 of 8 against 3 of 12, and its residue became
  five frames (observed: `frames.md`, 2026-10-13).
- **Overfits.** A reminder. "I'm saying it's not as simple as adding a
  reminder" (ruled: Roman, 2026-10-15 00:51 UTC). A door on the judgement:
  "every judgement-shaped guard regressed a register case or gained
  nothing" (observed: `plans/operating-facts.md`, 2026-09-02).
- **Leave it.** When a downstream check catches the act every time and the
  cost is steps: a challenge, the Critic on `gemma3:12b`, the merge gate.
  The Critic case no 8B passes is run on the larger model and not fixed
  (observed: `small-model.md` H1, 2026-09-12).
- **Escalate.** Every wall here that reaches a merge or a page, as a
  problem at the composition's level: the loop that checks this seat is too
  long for this model. The choices Roman has not ruled are in section 5,
  question 1. Already ruled: interview first (2026-10-02), the model is the
  last suspect (2026-09-14), a stronger model is the test of the structure
  (2026-09-23).
- **October frames, 3:** 200, 236, 133. Frame 243's s188 is this cause at
  one seat, placed under cause 1 by its effect.

### Cause 6. A rule reads a row that does not mean what the rule assumes

- **Line.** "Outstanding work is re-derived from the records each pass" and
  "A record's identity derives from its content". A predicate is a rule
  over rows, and a row can be stale, belong to another batch or request,
  carry a key a seat can vary, or outlive its cause (reasoned: the
  composition, Records; law 14).
- **On a night.** `tests.load` shows a red test as passing from an older
  batch. The agenda tick puts a merged request's rows on the next page. A
  re-dispatched batch merges with no test because `tests_missing` counts
  the abandoned batch's tests. A quarantined tick outlives the approve. A
  wake repeats on an unchanged tree. An empty answer is stamped answered.
- **Confirm.** Open the predicate and the query. List every value the rule
  reads and every op that can change each. The row that the rule reads and
  the row the rule means differ (observed: frame 132's four passes,
  `plans/operating-facts.md`, 2026-10-05).
- **Cheap fix.** A predicate change with the query's filter, 2 cycles.
  Frame 210 closed at the right state in 23 of 23 wakes; frame 209 at no
  `frontier` call raised; frame 198 at 0 of 9 pages over three merges;
  frame 240 at 0 of 3 walk ends; frame 112 by the timer rule (observed:
  `frames.md`). Eight October closes were predicate changes (observed:
  `frames.md` section 3).
- **Overfits.** A count keyed on a value a seat can vary: three reviews
  each found an endless chain through the real ops until the key was the
  criterion, which only `criteria.specify` writes (observed: frame 132,
  `plans/operating-facts.md`). A fold condition fitted to the night's rows:
  frame 225 took four reviews and 10 cycles of 2 before `is_default` left
  the fold (observed: `failed-fixes.md` row 10). A premise read from the
  status line: frame 112's design was "wrong in two parts" at the scope
  read (observed: `failed-fixes.md` row 6).
- **Leave it.** When a cap bounds the repeat and the cost is wakes only.
  Frame 112 closed on the cap at three.
- **Escalate.** When the rows are what he sees (cause 11), or the rule
  enforces a law: the cascade (law 9), the single writer (law 1), the
  ladder (law 6).
- **October frames, 17:** 112, 186, 210, 209, 213, 225, 198, 240, 241,
  239, 187, 182, 179, 174, 167, 130, 150.

### Cause 7. The runner or the parser reads a reply wrong

- **Line.** "A model is a component." Everything a seat does crosses one
  text boundary, and the runner's parser is the only reader. A reply that
  holds the act in a form the parser does not read is a reply with no
  call (reasoned: the composition, A model).
- **On a night.** Zero landed and twelve refused. A quote that holds quotes
  never parses. A line break reads as a space. A completion runs past the
  protocol's boundary and the seat invents its tool result. A stub of a
  long call line stubs again.
- **Confirm.** Read the reply bytes in the night database against what the
  runner recorded as the call. A reply that holds the act and no recorded
  call is this cause. A recorded call that was refused is cause 8.
- **Cheap fix.** A runner change, 2 to 4 cycles, the largest closed group:
  13 of 56 October closes (observed: `frames.md` section 3). Frame 109:
  nine landed and zero refused; frame 122: 0 of 249 sessions; frame 151:
  0 of 148 lost a line break; frame 232: 1.2k over the night against 158k
  (observed: `frames.md`).
- **Overfits.** A sentence in the runner's format prose. The shared prose
  is every desk's prompt, and one sentence changed the hash of every mode
  and took a case from 770 of 780 to 0 of 20; "the parser's refusal is the
  place for a transport hint" (observed: `plans/operating-facts.md`,
  2026-09-12). A one-time nudge: frame 152's fence nudge was spent on a
  reply with no test, frame 175 (observed: `frames.md`).
- **Leave it.** Frame 113, a Developer writes its own tool results, is
  parked at 29 of 35 sessions, and frame 232's cut at the protocol boundary
  bounds its cost (observed: `small-model.md` E1; `frames.md`).
- **Escalate.** Never. The runner is wiring.
- **October frames, 8:** 109, 122, 151, 232, 117, 137, 175, 113.

### Cause 8. A door's predicate is not its fact

- **Line.** "No brief grants what is not wired" and "Only a fact or a ruling
  gates." A door is a predicate on a state of files, the index or the
  database. A predicate wider than its fact admits a wrong call. A
  predicate narrower than its fact refuses a right one (reasoned: the
  composition, Flows; `plans/operating-facts.md`, "If the check names a
  state ... wrong under every model, the check is a door").
- **On a night.** A batch stopper: the same refusal many times in one
  session. An encode under a project test's id replaces it. A span write
  removes the file's imports. A prose answer is called answered. A seat's
  `supersedes` replaces his decision row. A revert of a head red at import
  is refused.
- **Confirm.** Read the refusal in the next turn's `user` text (observed:
  `plans/operating-facts.md`). Then count the predicate on every night's
  records: fires on a of n instances, refuses b of N right calls. The
  count, not the wording, is what found frame 243's lexical door at 1 of
  60 (observed: `plans/ladder-review-2026-10-15.md`, 2026-10-15).
- **Cheap fix.** A door or a predicate change with that count, 2 to 3
  cycles: 21 doors and 8 predicate changes among the 56 October closes
  (observed: `frames.md` section 3). Frame 132: 0 of 11 same-refs refusals
  against 125 of 141; frame 177: 0 of 3 from 3 of 3; frame 135: 10 of 10;
  frame 221: 0 of 4 after three reviews; frame 219: 0 principal `decisions`
  rows changed (observed: `frames.md`). A door holds a fact an 8B model
  cannot see and Python enforces silently (observed:
  `plans/operating-facts.md`, 2026-09-09).
- **Overfits.** A predicate stated in words: a phrase list on his words or
  a seat's words, cause 1's evidence. A door whose argument is optional: an
  optional argument is filled on every call and a refusal of it loops the
  seat, `L1-TS-encode-a-criterion` green to 0 of 5 (observed: frame 81,
  2026-09-24). Two doors on one signal that disagree: "the first guard
  becomes a lesson on how to evade the second" (observed: 2026-09-01). A
  door closed on its unit test alone: frames 228, 229 and 238 closed at 0 of
  0 over three nights, unproved on a night (observed: `failed-fixes.md`
  B.2). Across the 26 named doors, 2 held on a later night, 7 did not, and
  17 have no later count (observed: `doors.md`, 2026-10-15).
- **Leave it.** When the door had 0 cases over three nights and its unit
  test is green: close by the door test and let the residue rule reopen.
- **Escalate.** When the predicate would read his words for a meaning
  (cause 1), or would bound a judgement: slicing, triage, review (ruled:
  Roman, 2026-09-02, "prompts over guards"; `plans/operating-facts.md`).
  Already ruled for his rows: "The tool never rules for the Principal".
- **October frames, 29:** 111, 123, 125, 135, 136, 132, 145, 149, 164,
  170, 177, 178, 180, 189, 221, 238, 228, 219, 245, 247, 220, 183, 176,
  173, 147, 146, 140, 141, 116.

### Cause 9. The refusal's text, or a runner note, points the seat wrong

- **Line.** The ceiling, and "Each seat wakes cold". A refusal's repair text
  is an instruction the small model follows literally, so the door's
  predicate can be right and its step still wrong. The seat follows the
  door's last words, drops a condition, and takes advice that is refused
  again (observed: `small-model.md` C1 to C5; `plans/operating-facts.md`,
  "A refusal's repair text is an instruction that the model follows
  literally").
- **On a night.** A door says end and the nudge asks for a call. A refusal
  names a call the mode lacks. Six sentences state a fact the rows do not
  hold. The import hint names an import that binds nothing. The seat logs
  the door's questions as notes. A note says `written nothing` after a
  landed write.
- **Confirm.** Read the refusal's text beside the seat's next call. The
  next call is the text's advice, and the advice is wrong, refused, or
  impossible in the mode. This cause and cause 8 differ by one question:
  was the door right to fire?
- **Cheap fix.** Rewrite the refusal as one fact and one step, and name
  another call only where the door then admits it, 2 to 3 cycles (observed:
  `plans/operating-facts.md`, frame 135's line, 2026-10-05). Frame 197: 0
  of 38 against 1 of 43; frame 121: the claim false in 0 of 8, the old line
  false in 39 of 77; frame 169: 1 of 4 against 2 of 6; frame 153: the nudge
  fired 0 times (observed: `frames.md`). Name both arguments in one
  message, because one at a time flips the seat between two fixes
  (observed: `plans/operating-facts.md`).
- **Overfits.** A conditional invitation: the seat drops the condition
  (frame 119, reverted; frame 169; frame 208 open). A refusal that names a
  next call is a route the review must follow: frame 135's door took four
  passes and four reviews, 188k and 304k, because each sentence's advice
  opened a hole (observed: `plans/operating-facts.md`). The door's hint
  "prefix it with what it is" produced `c_` plus the item id (observed:
  2026-09-01).
- **Leave it.** When the wrong step costs one refused turn and the seat
  then takes the right one.
- **Escalate.** Never. The text is wiring. 44 of 118 October walls sit in
  code an earlier fix wrote, and 16 open frames name an earlier door, nudge
  or brief line in their heading (observed: `plans/wall-research.md`
  finding 1; `failed-fixes.md` B.3). Review every refusal's sentence as
  advice the seat will take.
- **October frames, 16:** 197, 229, 222, 168, 166, 154, 148, 126, 128,
  121, 153, 169, 208, 159, 248, 181.

### Cause 10. The mode lacks the call or the route the act needs

- **Line.** "Capability comes from wiring. No brief grants what is not
  wired." The mode's `.tools` file is the seat's whole namespace, and "a
  refusal is bounded only if the session can satisfy it or say why it
  cannot, and both have to be reachable in the mode" (observed:
  `rota/DECISIONS.md` line 384).
- **On a night.** A Critic doubts a criterion and cannot reach its writer.
  A Developer that knows the test is wrong writes the product to fit it. A
  park ask's answer names no option. A relay from the Liaison to itself
  wakes with no mode and every tool.
- **Confirm.** Open the mode's `.tools` file and `runner._mode_key`. The
  right act has no call there, or the message edge has no route in the
  graph. `python -m rota.tools.map mode <name>` lists the ops.
- **Cheap fix.** A new mode, not a tool added to a branch: brief, `.tools`,
  `_mode_key` branch, an `obligations.py` line, a register case, and the
  old mode's cases re-earned, 2 to 3 cycles (observed:
  `plans/operating-facts.md`, 2026-09-09). Frame 107 closed with eight green
  cases; frame 142 at 0 of 569 sessions against 27 (observed: `frames.md`).
- **Overfits.** A tool added to a mode: "an 8B model reads the tool list as
  the list of what this session is for". `decisions.author` on the Vision
  Keeper relay wrote 14 decisions; relay tools on the Liaison took G1 from
  10 of 10 to 0 of 5 (observed: `plans/operating-facts.md`, 2026-09-09).
- **Leave it.** When the act climbs the ladder and lands one rung up at a
  bounded cost (law 6).
- **Escalate.** When the route is new: who talks to whom is the
  composition's, and law 3 derives every edge from the artefacts. Frame
  114's route was already answered: a broken project test is the
  Developer's own regression (ruled: Roman, 2026-09-14;
  `repeated-questions.md` row 1).
- **October frames, 5:** 107, 142, 171, 114, 188.

### Cause 11. What reaches him is not his, or what is his does not reach him

- **Line.** "Evidence flows up the same path" and "Their attention is the
  scarcest budget." The page is the one surface he sees, and a page built
  from the wrong rows costs his attention and lands his answer on a wrong
  row (reasoned: the composition, The parties).
- **On a night.** Pages m391 to m431 each hold one Architect ledger row. The
  old request's page stays open after he moved on. A raw tick key sits on
  his page. An Architect's answer carries refs and no words.
- **Confirm.** Read the page against the rows: is the row wrong in the
  tables (cause 6) or only on the page? Frame 115, the answer with no
  words, is law 2 by design, "conclusions travel, reasoning stays home",
  and is not a wall (ruled: law 2; `repeated-questions.md` row 2).
- **Cheap fix.** None closed cheaply. Frames 190 and 193 closed as design
  frames on a shared cause, ruled over the per-wall order, at 0 of 20 pages
  by line 1 against 12 of 30, and they were one of the two closes that cut
  the open count (observed: `plans/wall-method-fit-review.md` section 2;
  `frames.md`).
- **Overfits.** A route change per row kind. Frame 190's residue became
  193, then 198 and 185's path (observed: `frames.md`, column 9).
- **Leave it.** Never on a page. A page costs the scarcest budget.
- **Escalate.** Always, as a design question: what the principal sees is
  the composition's (ruled: Roman, 2026-10-09 10:31, frame 190; 2026-10-12
  23:52, Roman rules when "the principal sees" changes).
- **October frames, 4:** 190, 193, 246, 115.

### Cause 12. Two records of one fact disagree, and no rule reconciles them

- **Line.** "Every record has one writer." A fact that two records hold has
  two writers, and the only reconciler is the cascade along the refs (law
  9). A criterion's text and its surface ref, two write doors, a ticket and
  its amended item (reasoned: the composition, Records; law 1).
- **On a night.** s250 and s274 move between two callables. The surface
  door wants a name in one file and the copy door forbids it. An amended
  item keeps its old ticket and the batch is cancelled twice.
- **Confirm.** Name the two records and their writers. Check whether the
  cascade reached the second after the first changed.
- **Cheap fix.** Thin. Frame 191 was folded into frame 190's design. Frame
  202 took passes 1, 1b, 1c and 2 and a cue door that held 1 of 1 on night
  148 (observed: `doors.md` row 3; `frames.md`). Frame 194 is open.
- **Overfits.** A door on one of the two records that reads the other's
  words: frame 202's surface-move door is a phrase list, held on one case.
- **Leave it.** When the cascade reaches the second record on the next
  wake.
- **Escalate.** Which record wins is a law question (law 1, law 9, law 11's
  ranks: decided over observed over reasoned).
- **October frames, 3:** 202, 194, 191.

### Cause 13. The instrument or the transport is wrong

- **Line.** "A prediction never blocks. Only a fact or a ruling gates." The
  night read counts through code the build session wrote, and a count from
  a wrong instrument is a prediction that wears the word observed
  (reasoned: the composition, Flows).
- **On a night.** An inherited test runs without its warning filter and
  cannot merge. Every live turn runs 2.06 seconds longer. A score lies
  while the transcript is clear. Four nights of a looping Developer were
  prompts the server had cut.
- **Confirm.** The control replay: replay the turn unchanged and compare
  bytes. Read the register's per-load history before attributing a flip to
  the model (observed: `plans/operating-facts.md`, 2026-09-01 and
  2026-09-15).
- **Cheap fix.** The instrument first, 1 to 3 cycles. Frame 207: 0 of 4 on
  two nights against 1 of 1; frame 235: 0.017 s against 2.06 s on 1,318
  matched pairs (observed: `frames.md`).
- **Overfits.** A fix to the seat for an instrument's fault. Finding 79:
  "the instrument was the wall. The model was never the wall" (observed:
  `plans/operating-facts.md`, 2026-09-15).
- **Leave it.** Never. A wrong instrument misplaces every other cause.
- **Escalate.** Never. Say the count that lied in the register.
- **October frames, 2:** 207, 235.

### Cause 14. The build session misnames the wall, or sizes the fix by its budget

Meta workflow. The composition applies to the build session as a second
instance, so its walls are the same walls one level up.

- **Line.** "One strong model, one context" and twenty cycles a sprint. The
  session names a wall from a status line, prices by cycles, and a door
  costs one cycle where a design costs ten (reasoned: the composition, The
  build session; the rule of 2026-10-11 05:51).
- **On a sprint.** 8 of 118 October rows name the sign and not the cause,
  and the 62 open rows rest on the heading alone (observed: `frames.md`
  section 4). Two premises were wrong at the scope read, frames 111 and 112
  (observed: `failed-fixes.md` rows 5 and 6). Four closes rest on a door
  that never fired (B.2). Residue was renamed four times: 219 to 243, 234
  to 250 and 243, 240 to 247 and 230, 200 to five frames (observed: the
  fit review section 1). Closed frames cost a median 5 cycles against 2 to
  3 priced (observed: the fit review section 2).
- **Confirm.** Before the frame: the scope read names the seam and every
  instance over every night. Before a second brief shape: the interview.
  Before a door: the count. What the session changed that day is the last
  suspect (ruled: `CLAUDE.md`, the loop rules).
- **Cheap fix.** Name the residue by its cause, not its sign: "the frame
  closes when its cause is not the cause the frame named" (ruled: Roman,
  2026-10-03, the three-part ends-when). A design frame on a shared cause
  closes more than a door: the two closes that cut the open count, frames
  131 and 190, were both (observed: the fit review section 2).
- **Overfits.** The sign table. One sign can come from five causes, and a
  session that enters by sign reaches for the cheapest cause's fix.
- **Leave it.** A wall the session cannot name after a scope read and an
  interview is a wall for the next night's read, with its count.
- **Escalate.** Three failed moves, a wall that survives three cycles, or a
  change at the composition (ruled: `CLAUDE.md`).

## 3. Overfit, reasoned once

Roman: "this is the kind of knowledge that we just have about the project"
(ruled: Roman, 2026-10-15). This section writes it down.

**From the structure.** A seat is a stochastic text generator at the word
level, and his words are free text with no vocabulary. One word in the
system text moved a seat's act at temperature 0, and whitespace alone moved
s173 (observed: `small-model.md` G2; `plans/frame243-brief-loop.md`). So a
fix whose predicate is stated in words, his words, a seat's words or a
phrase list, is a sample of one night's words. A fix whose predicate is a
state of files, the index or the database is a fact under every model and
every night (reasoned: `plans/operating-facts.md`, the door rule of
2026-09-09; `rota/DECISIONS.md` line 943). The first test of a fix is
whether its predicate can be stated without the night's words.

**The count, not the wording.** The ladder review corrected that test: every
predicate can be worded, and what tells a fit from a fix is the count over
every night's records, fires on a of n instances and refuses b of N right
calls, with a reach denominator (observed: `plans/ladder-review-2026-10-15.md`,
2026-10-15). The count found frame 243's lexical door at 1 of 60 before any
night ran. A door with no count is a prediction.

**Two models.** Every edit that corrected a defect helped both models, and
the only edit they disagreed on added emphasis. Helps both: a fix. Helps
one: emphasis, and the structural form is not found yet. Helps neither:
the diagnosis was wrong (observed: `rota/DECISIONS.md` line 347). Roman's
own test is the same: "Are any of the fixes specific to the language or
model?" (ruled: Roman, 2026-10-05).

**Cost, not prohibition.** When two outcomes cost differently, noise decides
which one the seat takes. A fix that makes the right act cheaper than the
wrong one holds. A fix that forbids the wrong act leaves it cheap, and the
refusal's text teaches the seat the next evasion (observed:
`rota/DECISIONS.md` line 1248; `plans/operating-facts.md`, 2026-09-01).

**Where the fix sits.** A fix at the hop that failed asks the same seat to
judge better. A fix one seat downstream gives the next seat a fact from a
record. The second generalises, because the record carries the fact to
every seat that reads it, and the first does not, because the seat's
judgement is the ceiling (reasoned: the ceiling line; frame 243's record
shape against its two dropped rules).

**A brief line.** Measure it on the case that owns the behaviour plus every
case whose composed text holds the line, and on several replay samples per
seat before a re-record, because one replay is one sample (observed:
`plans/operating-facts.md`, frame 82 and frame 234's lines;
`plans/frame243-brief-loop.md`). A change to the runner's shared prose owes
the whole register.

**The honest gap.** The doors table cannot decide overfit by door type: 1 of
8 phrase doors and 6 of 18 fact doors did not hold, and 17 of 26 have no
later count, 5 of them with no case since the fix (observed: `doors.md`).
The three phrase doors that failed did so at the count, before a night
(observed: `failed-fixes.md` rows 13, 15, 16). What the records show is that
the count catches an overfit before the night does, and that most doors are
never counted again. Count every door at every read, or its hold is a
claim.

## 4. From a wall to a decision

Answer in order. Each question names its record. Stop at the first answer
that places the wall, and take that cause's entry.

1. **Is the sign an open frame's sign?** `plans/stack.md`, the headings, and
   the night read's candidate line. Yes: a case added to that frame, placed
   by cause and not by sign. A wall whose sign matches but whose cause
   differs is a new frame (ruled: Roman, 2026-10-03, the residue rule).
2. **Is the instrument right?** The control replay and the register's
   per-load history. No: cause 13, before anything else.
3. **What did the seat have in its prompt?** The seat's turn in the night
   database. The fact is absent: cause 2, or cause 3 when no record holds
   it. Present: ask the interview whether the seat read it. Not read: cause
   4. Read and judged against: cause 5.
4. **Did a door fire, and was it right to?** The refusal in the next turn's
   `user` text, and the predicate's count on every night. Wrong to fire or
   wrong not to: cause 8. Right to fire and the step wrong: cause 9. The
   act has no call in the mode: cause 10. The reply held the act and no
   call was recorded: cause 7.
5. **Did the rule read the rows it means?** The predicate, its query, and
   the rows. No: cause 6. Two records about one fact: cause 12.
6. **Did his words survive every hop?** His verbatim words, the verdict, the
   ruling, the criterion's text after each seat, the page. The first hop
   that differs: cause 1. The page itself: cause 11.
7. **Decide.** The cause's cheap fix, with its count, when the entry has one
   and the count is in hand. Leave it, when the entry's "leave it" holds
   and the cost is steps only; write the frame's close as left, with the
   number. Escalate to Roman, when the entry's "escalate" holds, as the
   problem at the composition's level, with the rulings the entry cites so
   the question is only what is open. Before any question, two reads: what
   the records say, and whether the recommended answer holds against the
   frame's evidence (ruled: Roman, 2026-10-04 14:52).

## 5. For Roman

Four questions the structure and the evidence do not settle. Each is a
story. Each has a recommended answer and a rating.

### Question 1 [high]. When the clerk reads the ruling and still files the old form

A clerk in a records office receives a letter with the manager's correction
clipped to the front. The clerk reads the correction, says so when asked,
and files the old form anyway. Today the office hands the next clerk a copy
of the correction beside the form, so the error stops one desk down. Where
that is not enough, the office redesigns the whole desk, which takes a
month. Cause 5 has no cheap fix on the seat, and Roman ruled "for now there
is only cheap and escalate to me". The question is what the escalation
looks like when it arrives.

- **Option A.** Put a senior clerk at that one desk for that one letter: a
  stronger model on the judgement turn, replayed once. One cycle, untested
  (observed: `plans/wall-method-fit-review.md`, via frame 251's status of
  2026-10-15 10:51). It answers Roman's own test, "if
  not then it's the structure's fault" (ruled: Roman, 2026-09-23).
- **Option B.** A checker at the outgoing post: a judge at the merge gate
  that reads his words against the change. Eight to ten cycles and a night,
  priced and declined as the next design frame on 2026-10-15 10:58, not
  declined as never.
- **Option C.** Ask the client to initial each letter: a principal checkpoint
  after every rewrite of his words. Costs his attention.

Analogy: a spell-checker that flags a word is not the same as a proofreader
who reads the sentence. Recommended: A first, as the test that every cause-5
escalation runs before it reaches Roman, so the question he gets says
whether a stronger model did the act. Then B as a design frame when A says
the structure is at fault.

### Question 2 [med]. May a door read his words at all

A receptionist keeps a list of phrases that mean "cancel the appointment".
A caller says "I'd rather not come in", and the list misses it, or the list
holds "not" and cancels an appointment the caller confirmed. Today the
office builds such lists, and three of them failed before the first night
at the count, 1 of 60, 59 of 60, 74 of 131. One list held at 0 of 6 with no
false refusal over two nights (frame 234), and another at 1 of 1 (frame
202). Roman asked on 2026-10-15 whether "the fix may be a list of his
phrases in the code" is the right question, and did not rule.

- **Option A.** No door reads his words. His words reach the seats as a
  record beside the row, and a judge or a person reads them.
- **Option B.** A door may read his words when its count on every night's
  records shows 0 false refusals with a reach denominator, and one false
  refusal at any later read reopens the frame.

Analogy: a smoke detector may key on smoke, never on the word "fire".
Recommended: B, because frame 234's door is the one measured case that
held, and the count is the test the ladder review named. Rated medium: an
edit depends on it, in every cause-1 frame.

### Question 3 [low]. When the alarm never rings

A shop installs an alarm after a break-in. For three nights nothing
happens. Today the shop calls the alarm proven on its bench test alone,
and three frames closed that way, 228, 229 and 238 (observed:
`failed-fixes.md` B.2). The alternative keeps the frame open until the
alarm rings once.

Recommended: close on the door's unit test after three nights at 0 of 0,
with the count line kept in the night read so a later fire reopens the
frame by the residue rule. Rated low: it sets an order and no edit depends
on it.

### Question 4 [low]. What "a small inefficiency" is

A workshop has a drawer that sticks. Every job takes a minute longer and
no job is wrong. Roman ruled that such a wall is left when it cannot be
fixed easily. The records measure a night in steps, asks, dollars and
minutes (observed: `plans/night148-read.md`, section 13.3, via the stack).

Recommended: a wall is small when it reaches no page and no merge, a cap
bounds it, and it costs steps or card time only. The night's steps and asks
are the measure. Rated low.

## 6. What this pass could not settle

- **The placements are reasoned from status lines.** No turn of any failing
  session was read. The research says the same of its rows. A cold test of
  this guide on night 149's new walls is the first real test.
- **Where this pass differs from the research's placements, 16 rows.**
  Frames 110, 165, 152 and 237 go to cause 4, the shape, from "parser" and
  "judged wrong", because their interviews name a form the seat could not
  read or copy. Frames 230 and 172 go to cause 3 from "door" and
  "unplaced", because the fact is Click's runtime. Frames 192 and 185 go to
  cause 1 from "a mode lacked a tool", because the wiring had no slot for
  his word. Frames 191, 202 and 194 go to cause 12 from three buckets.
  Frame 150 goes to cause 6 from unplaced. Frames 181 and 248 go to cause 9
  from unplaced. Frame 115 goes to cause 11 as not a wall. Frame 235 goes
  to cause 13 from "the transport". Frame 188 goes to cause 10 from
  "other".
- **Not placed, 2:** frame 129, a Vision Keeper authors a decision then
  asserts it as an item, and frame 249, a ruling relayed to the
  Terminologist ends in `glossary.adopt`. The records name the sign only.
- **The weakest part.** Causes 4 and 5 are the causes the ceiling line
  predicts and the ones that cost the most, and their evidence is the
  thinnest: frame 165 closed at 1 of 1, frame 237's defect did not
  reproduce on replay, 0 of 3, and frame 200's close is a 46-cycle design
  frame whose residue became five frames. The cheap fix the guide names for
  cause 5, give the next seat the fact, rests on frame 243, which validates
  on night 149 and has no count yet.
- **The doors.** 17 of 26 named doors have no later count. Section 3's
  claim that the count catches an overfit before the night rests on three
  doors.
- **Which model the interviews ran on.** The research says frames 152, 165
  and 243 ran on `qwen3.5:9b`; the holding session did not take that as
  fact, because night 148's log names both models (observed: frame 251's
  status of 12:05).
- **Cycle counts.** Frames 234, 237 and 238 carry different cycle counts in
  the archive and the fit review. This guide quotes `frames.md`.
- **Cause 14 has no frame rows.** Its evidence is the research's findings
  and the fit review, not a table of its own.
