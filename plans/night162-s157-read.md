# Night 162, the read of s157: the criteria writer's invented text

Written 2026-10-24 14:27 by an Opus agent of session f3a8d4c2, read-only on
the night database `.rota/clickI_night162.db`.

## Verdict

**The words "raise UsageError" came from the glossary row `usageerror`,
the only exception name in s157's window, put in place of his "aborting".
Neither the code nor his words nor the brief gave them** (observed: s157
turn 1). s157 never read `confirm`'s source. The wake pushed symbol names
and no body. The glossary held `UsageError` and no `Abort` (observed).

**The cause is cause 1 at the criteria writer.** His words say "instead of
aborting". The first hop that differs is s157's turn-1 reply, which wrote
"must raise UsageError if stdin is closed, preserving existing behavior".
The shape is "a seat read the words and wrote something else", and its
input lacked the fact that confirm raises `Abort` (cause 2 underneath).

**The pairs came from the cumulative wake and the repeat refusals, not
from a criteria refusal loop.** s157 wrote c4, c5 and c7 in turns 5 and 7,
before the first criteria refusal in turn 8. The specify door admitted the
pairs by its own rule. Its threshold is 0.85 word overlap, and the pairs
measure 0.27, 0.67 and 0.57 (observed: `_prose_words` on the turn texts).

**No open frame holds this sign. A new frame:** "The criteria writer names
an exception that neither his words, the item nor the surface's source
holds, and the tests and the Developers follow it". Section 5 gives the
site, the ends-when, the red test and the price.

## 1. What s157 saw

s157 is the Terminologist on `tick:criteria`, model `qwen3.5:9b`, wake
refs `["confirm_default_on_eof"]`, 11 turns and 263 tool calls (observed:
`sessions`, `turns`, `tool_calls`). Of the calls, 247 are
`criteria.specify`. It made 0 `code.source` calls.

The system text is the Terminologist base brief and the criteria mode.
The mode's words on a criterion:

> "A ticket has the few criteria a person would check. Three is usual and
> six is many. ... A criterion for an edge the item's words never mentioned
> is a guess, and a guess is a ledger entry, not a criterion."

> "Criteria describe what must be *true when it is done*, not how to build
> it. "Deleting an account tombstones it and preserves billing history" is
> a criterion."

The brief's examples are `close_account`, `split_bill`,
`archive_invoices`, the tip function and the tombstone sentence. None
names an exception or a raise (observed: turn 1 system text).

The turn-1 user text held these blocks, pre-run:

- `[code.callables]`: 40 rows. `src/click/termui.py::confirm | function`
  is one. Names only, no body.
- `[glossary.consult]`: 20 rows. Two name a raise or an exception:
  > "usageerror | UsageError | exception for invalid user input | decided"
  > "usage | usage | the string returned by get_usage or printed as part of
  > a UsageError message ..."
  No row names `Abort`.
- `[glossary.lookup]`: `{"note": "the rows this wake named are gone."}`
- `[tickets.scan]`: one ticket, `tk_1_confirm_default_on_eof`, headline
  "let confirm() take a default_on_eof flag: when stdin is closed it
  returns the default instead of aborting".
- `[the item]`: "Let confirm() take a default_on_eof flag: when stdin is
  closed it returns the default instead of aborting. The flag defaults to
  False, so nothing changes for existing callers." His statement is the
  first sentence, verbatim.

Every line in the window that names `UsageError` or a raise, by source:

| Line | Source |
|---|---|
| "usageerror \| UsageError \| exception for invalid user input" | the glossary, onboarding row, `decided` |
| "printed as part of a UsageError message" | the glossary, the `usage` row |
| "instead of aborting" | his words and the item |
| "must raise UsageError if stdin is closed" | s157's own reply, turn 1, then re-shown in every later user turn |

The code says otherwise. `confirm` in `src/click/termui.py` catches
`(KeyboardInterrupt, EOFError)` and runs `raise Abort() from None`, and its
docstring says "raise a :exc:`Abort` exception" (observed: the clickI
checkout at `684178f~1`). The file imports `UsageError` and uses it in
`prompt` and `edit`, not in `confirm`. s157 never read the file.

## 2. Why "raise UsageError"

s157 invented the exception from the glossary, with no source that ties
it to `confirm`. The turn-1 reply:

> TOOL: criteria.specify(id='c2_confirm_default_on_eof_false', ...,
> text="When default_on_eof is False (the default), confirm() must raise
> UsageError if stdin is closed, preserving existing behavior.",
> term_refs=['option', 'usageerror'], surface_refs=['confirm'])

The `term_refs` name `usageerror`, the glossary row. The brief says
"Every criterion carries `term_refs` naming the glossary entries it relies
on". So the seat looked for a glossary term for "aborting", found one
exception row, and used it. The answers to the brief's three checks:

1. `confirm` or a neighbour raising `UsageError` in a file s157 read: no
   file was read. In the real file, `confirm` raises `Abort`.
2. The brief's example criterion naming an exception: no.
3. A glossary row: yes, `usageerror`, the only exception term pushed.

The item text says "aborting", and the glossary has no `abort` row. The
seat mapped the item's verb onto the nearest pushed term. The criterion
then says "preserving existing behavior", which is a claim about the code
that the seat never checked.

## 3. Why three near-duplicate pairs

The pairs came from the wake's repeat of the seat's own calls and from the
glossary repeat refusals. They did not come from a criteria refusal loop
or from the count instruction. The order of the `criteria.specify` calls:

| Turn | Calls | Result |
|---|---|---|
| 1 | c1, c2, c3 | all OK |
| 2 to 4 | `glossary.consult` and `glossary.lookup` on `default_on_eof`, twice each | `[]`, then "no entry", then repeat notes |
| 5 | `glossary.lookup`, c4 "The parameter 'default_on_eof' is a boolean flag that controls whether confirm() returns the default value on EOF." | c4 OK |
| 7 | `glossary.lookup`, c5, c6, c7 | c5 OK, c6 refused as near c3, c7 OK |
| 8 | `ledger.log`, then c8 to about c119, cut at the output budget | c8 refused as near c2, c9 onward refused at 6 criteria, the rest as near c5 |
| 9 to 11 | `ledger.log`, then c1 and c2 under new texts, and a second runaway | refused |

The first criteria refusal is in the user text of turn 8, after all six
landed. So no refusal shaped c4, c5 or c7.

What came before each pair:

- **c4, after the "define it first" sentence.** Turn 3's prose says: "The
  term `default_on_eof` is not in the glossary. Since it is a new
  parameter introduced by this item, I must define it before using it in
  criteria." The mode says "If you need a term that does not exist yet,
  define it first". The working set holds no glossary write call. So the
  seat wrote the definition as a criterion, c4, which restates c1.
- **c5, c6 and c7, after the repeat refusal.** Turn 7's user text ends:
  "ERROR glossary.consult: asked three times this session and the answer
  has not changed; not answered again. The answer is in this prompt." The
  seat then re-sent its turn-1 set under new ids and new words. c5
  restates c2, c6 and c7 restate c3. Each user turn re-shows the seat's
  earlier calls in full, so the seat reads its own criteria as a template
  to emit again.

The door's admission is by its rule. The near-duplicate predicate in
`criteria_specify`, `rota/roles/api.py` about line 5450, refuses at word
overlap 0.85 or more, "Near-verbatim only; the size of a ticket's criteria
is the brief's sentence, not this door's". The measured overlaps on the
turn texts:

| Pair | Overlap | Door |
|---|---|---|
| c1 and c4 | 0.27 | admitted |
| c2 and c5 | 0.67 | admitted |
| c3 and c7 | 0.57 | admitted |
| c3 and c6 | 0.92 | refused |

The count door then stopped c9 onward at "6 criteria already, and six is
many". A sibling: the base brief says "`criteria.consult` is what you have
already specified, check it before writing more". The criteria mode's
working set does not hold `criteria.consult` (observed: turn 1 tool list),
so the seat could not do that check (cause 10).

## 4. The cause by the guide

**Cause 1 at the criteria writer, shown by turn 1.** Step 3 of the guide's
section 4 applies first, because the sign names his words. His words:
"instead of aborting". The criterion after s157: "must raise UsageError if
stdin is closed, preserving existing behavior". No hop is between them, so
s157 is the first hop that differs.

The other two candidates do not hold as the one cause:

- **A door that admitted a text it should not.** The specify door has no
  predicate on an exception name, and its overlap predicate worked as
  ruled. A semantic duplicate door is a judgement by the rule of
  2026-09-09. The door is the fix site, not the cause.
- **A brief that pushed the seat to invent.** The brief says nothing
  about exceptions, and it says an edge the words never mention is a
  guess. Its "define it first" sentence with no define call made c4, which
  is the pair cause and not the invented text.

Under the cause-1 seam lies a cause-2 gap. The fact "confirm raises
`Abort`" was in no block of the wake. The wake pushed `confirm` as a name
and pushed `UsageError` as a glossary term. A stronger model would call
`code.source` first. A 9b seat wrote from the window alone.

## 5. The frame placed

No open frame holds this sign (observed: `python -m rota.tools.state --sid
f3a8d4c2` at 14:26, and the stack headings on "criteri", "invent" and
"glossary"). Frame 306 is about his page words that do not reach the
criterion. Frame 315 is about a re-slice. Frame 143 is about a Tester's
default. None is about a criterion that names a fact from no source.

The new frame, in the stack's form:

### A criterion names an exception that neither his words, the item nor the surface's source holds, and the tests and two Developers follow it (2026-10-24)

- Site: `criteria_specify` in `rota/roles/api.py`, lines 5307 to 5499,
  beside the near-duplicate door at about 5450, and the criteria wake's
  pre-run blocks in `rota/core/runner.py`. Ask the map tool first. Shares
  `api.py` with frames 201, 305, 313, 315 and 306. Rota workflow.
- Ends when: first, the mechanism. A `criteria.specify` whose text names
  an exception identifier that is in none of his statements, the item
  text, or the source of a callable in `surface_refs` is refused, and the
  refusal quotes the raise lines of that source. The criteria wake shows
  the raise lines of each surface it names. s157's turn-1 c2 is the red
  test. Second, on a night, criteria that name an exception from no source
  go from 2 of 6 on b_2 toward 0 over the next 3 nights. Third, the door
  makes 0 false refusals of a criterion whose exception is in the
  surface's source.
- Red test: s157 turn 1. On a fixture where `confirm` runs `raise Abort()
  from None`, the call `criteria.specify(id='c2_confirm_default_on_eof_false',
  ticket_id='tk_1_confirm_default_on_eof', text="When default_on_eof is
  False (the default), confirm() must raise UsageError if stdin is closed,
  preserving existing behavior.", term_refs=['option', 'usageerror'],
  surface_refs=['confirm'])` lands today (observed: turn 2, "OK
  criteria.specify -> {"id": "c2_confirm_default_on_eof_false"}"). The test
  asserts a refusal that names `Abort`. The same turn's c3, which names no
  exception, still lands.
- Rule check: the door reads a fact of the text, an identifier and where
  it occurs, and not a meaning. A stronger model that names `Abort` from
  the source passes it. So it passes the rule of 2026-09-09.
- Price: 2 cycles, about 60k on Opus and a review (reasoned: a door
  predicate and a wake block, by the rule of 2026-10-11 05:51).
- Cases to add, not this frame: the criteria mode lacks `criteria.consult`
  and a glossary write call, which made c4 (cause 10). The wake re-shows
  the seat's own calls in every user turn, which made c5 and c7 (cause 9
  at the repeat refusal's text "The answer is in this prompt").

## Usage

About 55k tokens of context on Opus, one agent, no sub-agent.
