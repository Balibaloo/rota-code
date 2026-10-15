# Review of the ladder of change kinds, 2026-10-15

Read-only review of the block in `CLAUDE.md` that starts "**A wall's fix is
chosen from a ladder of change kinds**", commit 6df77bcc. Brief:
`ladder_review_brief.md` in the holding session's scratchpad. Reviewer: one
agent, at 02:00. Ground read: `plans/composition.md`; `plans/stack.md` frames
243 and 250 and the sprint 6 heading; `plans/frame243-scope.md` sections 0,
3, 4, 5; `plans/frame243-interview.md` section 0; `plans/night148-read.md`
sections 0 and 12; `plans/night147-read.md` section 13; five doors and three
predicates in the code; `plans/archive/stack-2026-10-15.md`; `git log
--oneline -60`. Meta workflow throughout, except where a line says rota
workflow.

## 0. Verdict

The list of kinds is close to complete and the ruling behind it is right.
The two rules under the list are wrong in the way that matters. The overfit
test checks a wording where the sprint's own evidence shows a count decides,
and the placement rule puts the door that closed the sprint's largest wall
on the wrong rung. Frame 243's new design is a word rule in another coat,
placed on rung 4 by the stack, and on night 148's case it reproduces the
two-format text that failed. A rewrite is in section 7.

## 1. Completeness against the code

Three kinds of change that the structure admits are not on the ladder
(observed: the code and the log, 2026-10-15).

1. **A mode's tool set.** Each mode has a `.tools` file, and the doors read
   it: `_wake_mode_tools(ctx)` at `rota/roles/api.py:5388` decides whether a
   refusal may name `msg.challenge_vision_keeper`, and `decisions_author`
   names `msg.report_liaison` only where the mode offers it. The
   Terminologist's `relay.tools` holds two calls, `criterion_repair.tools`
   holds ten. A wall that a seat meets because its mode lacks a call, or
   holds one it should not, is fixed by one line in a `.tools` file. The
   composition names this kind: "Capability comes from wiring. No brief
   grants what is not wired." Night 148's candidate M, four relay wakes that
   end in a refused `glossary.adopt`, is this kind by sight (reasoned: the
   relay mode offers adopt and lookup alone).
2. **A state rule: what a batch does by itself.** `mergeable` at
   `rota/core/lifecycle.py:592`, the scheduler's cancel that abandons a
   batch at a contest, the quarantine lift at a landed ruling, and
   `tick_attempts` caps. Rung 3 names wakes and relays only. Three of the
   sprint's fix commits are this kind: 865b5132 `mergeable` counts the
   batch's own tests, 24be87ec the review predicate and `criteria_load`,
   be5e63d9 the lift (observed: the log). Frame 240 closed on the lift
   alone.
3. **The reply reader.** The runner's account of a reply with no parsed
   call, a1ffe54d: "the list-under-a-name account reads the parser's calls,
   names the mode's tools only, and reaches the seat's next turn". Frame 237
   closed on that and one brief line together, 8 agent runs. A reader of
   the reply is not a door, because there is no call, and not a brief line.

One widening: rung 4 says "what a row carries to the seats". The principal's
page is a record a reader gets too, and frame 246, the raw tick key on a
page, is a wall of that kind with no rung (reasoned: candidate G names the
page, not a row).

Not missing: the offer, `_offer` with 49 callers, a refusal that carries the
corrected call, is a shape of rung 1. The instrument, the recorder and the
gate, is the meta workflow and is priced in `plans/operating-facts.md`, so
the ladder need not hold it.

## 2. Distinct kinds, and the order

Rungs 1 and 2 are one kind in the code. A declared field exists only through
the door that checks it, both edit the op in `rota/roles/api.py`, and rung 2
also edits the brief's call line so the seat knows the field (reasoned: the
`dropped` note of frame 173, `plans/night148-read.md` section 0, is a door
with a note). Rung 2 is not cheaper than rung 3.

Rung 6 is three kinds: a line to the principal is a route and spends his
attention; a stronger model is a config line; an executable check is the
sandbox or the harness. They share one sentence and nothing else (reasoned:
the composition prices the first by attention and the others by cycles).

The order "cheapest first" does not hold on the sprint's actuals
(observed: `plans/archive/stack-2026-10-15.md`, the "Cycles: actual" lines).
Doors: frame 219, 2 of 2 to 3; frame 229, 3 of 3; frame 238, 3 of 2 to 3;
frame 234, 10 agent runs of 2, with four reviews. A state rule, frame 240,
about 2. A predicate, frame 239, three passes. A brief line with a reader
fix, frame 237, 8 of 2. The median door is the cheapest kind, and the
dearest fix but one was a door. The cost of a door follows what its
predicate reads: an owner or a landed ruling costs 2 or 3, a reading of the
principal's words cost 10. So the order is by the predicate's reach, not by
the rung.

## 3. The overfit test

**Unsound as a test, because every predicate can be stated without the
night's words** (reasoned: two cases below). The lexical door of frame 243's
scope reads, without a night's word, "a rewrite keeps a quoted literal of the
contested text when one sentence of his words holds a removal word and every
placeholder word of the literal". It passes the test as written. It was
dropped for a different fact: it fires on 1 of 60 contested respecifies and
covers 1 of 3 seam cases (observed: `plans/frame243-scope.md`, sections 0
and 5.1, `scan.py`). The count found the overfit. The wording test did not.

**A door that passes the test as written and worked**: frame 219's
`decisions_author`, `rota/roles/api.py:9617-9624`: a write under an id whose
author is not the caller is refused. A record's owner is a fact for every
call. It refused s175 twice on night 148 and 0 right writes (observed:
`plans/night148-read.md`, section 8).

**A door that fails the test's rung 1 note and worked**: frame 234's
`_line_refusal` and `_unnamed_contest`, `rota/roles/api.py:8424-8505`. Its
statement is clean, "a contest lands on a line only when the words name
it". Its code is a cue list grown from nights' sentences: `_BARE_AGREEMENT`
with "Looks good to me", `_LINE_REF`, "isn't a request", "don't belong
there", and the `_CHECK_FAULT` and `_WORDS_FAULT` lists at 5058 and 5063
that the same seam's doors of frames 226 and 227 use. By the rung 1 note, "a
door whose predicate needs a word list taken from the case is a brief line
in disguise", every one of those doors goes up a rung. Frame 234's door
closed at 0 of 6 cancels over two nights, with 13 to 20 over-contests
refused and 0 right rulings refused on five nights (observed: the archive,
frame 234, the statuses of 2026-10-14 19:55 and 2026-10-15 01:16). The brief
line that the note prefers was tried once, pass 1c, for one case, and cost
two re-record cycles and a 2 of 5 regression on a second case.

So the sound test is the one the scope already ran: **run the predicate on
the records of every night that holds the wall; it must fire on each known
instance and on no right call**. A predicate that fires on one instance is
overfit whatever its words say, and a cue list that fires on fifteen with
no false refusal is not.

## 4. The placement rule

"A seat that lacked a fact is rung 1 or 2; a seat that had the fact and
judged wrong is rung 4 or above."

- **s188, night 148.** The words of m71 were in its prompt. It says "The
  format was not rejected" (observed: `plans/frame243-interview.md`, section
  0). By the rule it had the fact and goes to rung 4. The interview's own
  reading sends it to rung 1: "the scope's door at seam 1, which matches
  the literal against his words, is the fix that reaches s188", because the
  door states the fact it missed, "His words reject that format". The rule
  gives two rungs for one case, because "had the fact" and "had the words"
  are not the same thing. A seat has a fact when a row or a result states
  it. Words it must read are not a fact it has.
- **s173, night 147.** It read a "because" clause as a requirement and
  corrected itself in the same conversation. By the rule, rung 4 or above.
  That holds: a reading no door can count is rung 6, a stronger reader, or
  the principal on one line (reasoned: the interview names a misread, and
  one sample).
- **Frame 238, closed.** Vision Keeper s285's relay carried the two
  constraints and not the item's landed approve. It lacked the fact. The fix
  was a door that reads the landed ruling. Rung 1, as the rule says
  (observed: the archive, frame 238).
- **Frame 234, closed.** Liaison s427 had "Lines 1 to 4 match what I asked
  for" in front of it and contested lines 1 to 4. By the rule, rung 4 or
  above. The fix that closed it was a door, rung 1, with one brief line. The
  rule would have sent the sprint's largest wall away from the fix that
  worked (observed: the archive, frame 234).

The rule holds where the seat lacked a row, 238 and 229, and fails where
the seat had words to read, 234 and s188. The line that holds: a wall that
is a reading of words goes to rung 1 when a count on the records shows a
door can read them, and to rung 6 when no count does.

## 5. Frame 243's new design

The design: after a contest ruling with words, the criterion's new text
holds the ruling's sentence verbatim, found as the sentence that shares the
most words with the old text, or the call names the sentence it leaves out
with a why that lands as a note.

**It is a word rule in another coat, on rungs 1 and 2, not rung 4**
(reasoned). The sentence pick is a bag-of-words overlap, the check is a
substring presence, and the escape is a declared field with a why. Rung 4
is "what a row carries to the seats that read it". No column changes, and
the reader that lacked the source, the Developer, still reads the criterion
alone: s190's prompt held the criterion, the ticket and the request, and no
ruling (observed: `plans/frame243-scope.md`, section 0).

**Night 148, s188.** The door admits two outcomes. First, s188 puts "not
replace that message with just the command name and the Python version"
into the text beside "{command} {python_version}". That is a text that holds
both formats, which is the shape that failed: s188 "respecified the text to
hold both formats; s190 committed to the first half of the text" (observed:
`plans/stack.md`, frame 243, line 1). Second, s188 names the sentence it
leaves out and says "the format was not rejected", which is what it said in
the interview. The note lands in the ledger, which no reader on the build
path reads, the same quiet end as `decisions.supersedes` at seam 2. Either
way the build is not changed by the door.

**Night 147.** s130 dropped his clause. A presence check on the sentence
that shares the most words with the old text would catch that drop, when
the pick lands on the clause's sentence. s173 misread a "because" clause as
a requirement. The rule would put that clause into the criterion verbatim,
which hands the misread to the Tester as text. The stack's line "s173's
shape falls under the same rule, because the ruling's sentence lands whole"
is the opposite of what the interview found (reasoned: the clause was the
cause, and the rule preserves it).

**A correct rewrite.** `criterion_repair.md` asks for "words that name an
observable outcome", and his sentences are prose with "it", "that message"
and "the test". A rewrite that paraphrases into checkable form holds no
sentence verbatim. A three-word match already flags 15 of 60 right rewrites
(observed: the scope, 5.1), so a verbatim presence will hold on about 0 of
60, and every right call must carry the omission note to land. A field that
every call must carry says nothing. The door also crosses frame 227's
branch at 5440: a fault on the check means "The criterion stands", and the
new rule asks for a sentence about a test in the criterion's words. The
sentence pick is unstable on m71 itself: the first sentence holds "python"
and "version", the second holds "command", and the scope needed both.

**The rung-4 fix that the ladder's own words name**: the Developer and the
Tester read the source and not a paraphrase. s190 built from the criterion
with no ruling in its prompt. A batch start that carries the latest contest
ruling's words beside each criterion it contested is a record shape, states
no night's word, and reaches s188, s173 and s130 by effect, because the
builder sees "not replace that message with just the command name and the
Python version" whatever the Terminologist wrote (reasoned: seam 1 matters
only because the build reads the criterion alone, scope section 3, fact 1).
Its count before the pass: how many of the 3 declined merges had a ruling
with words that the builder's prompt lacked. The scope says 3 of 3.

## 6. What the composition requires that the ladder leaves out

- **A prediction never gates.** The ladder places a case from the
  interview. An interview is one replay, and the register says a replay
  does not always reproduce (observed: f9d0ac0e). A rung chosen from one
  sample is a prediction that then gates the pass shape. The count on the
  records is the fact; the interview is the reading of it.
- **The tool never rules for the Principal.** A door that reads his words
  and tells a seat "His words reject that format" is the tool reading him.
  The composition allows a gate on a fact or a ruling. His words are a
  ruling; a reading of them is neither, unless the count shows the reading
  holds on the records. The ladder has no line on when a door may read his
  words and when the reader is the principal himself, rung 6, "the
  principal on one line". Frame 250's clarify verdict, a yes-with-correction,
  is such a case: whether m81 rejects the format is one line to him.
- **A capability is judged by the loop it shortens.** The ladder prices by
  rung in cycles. The loop a door shortens is one turn; a brief line's loop
  is a night; the principal's line's loop is his reply time and his
  attention. The order of the rungs should be the loop each shortens, with
  the reach from the count beside it.
- **Nothing stops quietly, and a seat can check the claim against the
  source.** The design's omission note lands in the ledger with no reader
  on the build path, as `supersedes` did. The criterion carries the
  paraphrase and the note carries the source, which inverts rung 4's own
  sentence.

## 7. The block, rewritten

**A wall's fix is chosen from a ladder of change kinds, and the kind is
named in the frame before the pass** (ruled: Roman, 2026-10-15 01:54, "when
we hit walls the solutions can range from simple to complex but there's only
so many kind of changes we can make", after frame 243's first design was a
four-condition word rule written from one night's sentence). The kinds, by
the loop each one shortens, shortest first:

1. A door: a tool result at one call that states a fact and a step, and
   may offer the corrected call. The fact is a row, an owner, a landed
   ruling, a path, or a reading of the principal's words that the count in
   the test below supports.
2. A declared field: the call states what the seat did, and the door checks
   the statement against the record. The brief's call line names the field.
3. A predicate or a state rule: who wakes, when, who receives a relay, and
   what a batch does by itself: cancel, merge, lift.
4. A mode's tools: what the seat can call. No brief grants what is not
   wired.
5. A record shape: what a reader gets, a seat or the principal: the source,
   never a paraphrase of it. The reply reader is here: what the runner says
   back to a reply with no call.
6. A brief line: the wording of a judgement. Only after the interview says
   the seat lacked the sentence. A seat that had the sentence and judged
   wrong is not moved by a second sentence.
7. The reader: the judgement moves to the principal on one line, to a
   stronger model for that one step, or to an executable check that the
   wrong result fails.
8. The composition: who sees what and who rules. A grill to Roman.

The overfit test, before any pass, is a count and not a wording. Run the
predicate on the records of every night that holds the wall. It fires on
each known instance and on no right call, or the rung is wrong. A predicate
that fires on one instance is overfit whatever its words say. The interview
reads the case and the count places it: a seat that lacked a row or a
result is rung 1 to 5; a seat that read the words and judged wrong is rung
1 only with the count, else rung 7. A placement from one replay is a
prediction and does not gate a pass. A night's read names the rung and the
count beside each candidate, and the price follows the count.
