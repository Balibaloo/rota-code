# The principal's flow, taken from wsff

*2026-09-12. A design. Start from the moments wsff puts a person in the
loop, name the page rota shows at each one, and name what rota lacks.*

## Summary

wsff (humanlayer, "Why Software Factories Fail", 2026) puts the person at
five moments: product review, system architecture, program design, each
vertical slice, and the merge read. Rota holds the principal at two: the cut
and the signoff page. The three moments that decide the shape of code have
no page. Two of them have a setting or a sentence that points at a page
that does not exist: `merge_gate=review` waits on a review nothing
presents, and the grouping brief asks for a dependency fact no tool writes.

The design below is six pages and three paths. Every page is a draft with a
default. The principal approves, contests with words, or says nothing. Two
pages hold the run: the product page and the design page. The rest wait on
nobody. Nothing here is a new artefact or a new verb at the seat. Each page
is a kind of present, which is the ruling of 2026-09-12.

## The moments wsff names

| moment | what the person sees | what the person decides | leverage |
|---|---|---|---|
| product review | the problem in the user's words, what success looks like, a mockup | is this the thing | highest |
| system architecture | contracts, data shapes, who talks to whom | do these promises hold | high |
| program design | file-tree diff, signatures, call-stack tree | is this the shape | high, and the cheapest moment to change a mind |
| vertical slices | one slice at a time, contract first, 100 to 200 lines | is this slice right, resteer | medium, repeated |
| merge read | the diff | read the code | the floor |

wsff says the model drafts every one of these and the person argues with it.
wsff also says about 40 percent of tasks skip all of it.

## The pages

Each page says what it is for, what approve does, and what contest does.
The seat shows one page at a time. The register names the page that is owed.

### Page 0. The cut, and the path

**When.** The principal has spoken. Liaison has cut the words into
statements. This is the fidelity gate of law 8, built today.

**New.** The page carries one more line: the path the system proposes.
Three paths exist. *oneshot*: pages 1 and 4 only, no hold after page 1.
*plan*: pages 1 and 2 as one page, then page 3, then one read per batch.
*full*: every page, one read per slice. The proposal is a ledger row on the
account, "assumed: this is a small change, built without a design page",
so the principal rules on it with the verdict they already give.

**Who drafts.** Vision Keeper, in deliver, with the account. The size is a
judgement about the statement, which is scope.

**Hold.** Yes. This is intent time.

### Page 1. The product page

**When.** Vision Keeper has written the account and the items. This is the
signoff page, built today, with open assumptions beside each row (A1).

**New.** Two silent points the deliver brief does not log today:

1. **The worked example.** What the user does, and what they see. For a
   program with a screen, the screen in words. For a command, the command
   and its output. This is wsff's mockup at the cost an 8B model can pay.
   The tips walk shipped a program with no way to run it. An example on
   the page would have shown that before a line was written.
2. **The success line.** What the principal would read afterwards to say
   the work was worth it. wsff: "the support tickets about X stop". Law 13
   forbids time. A measure is not time. The row is what page 5 asks about.

Both are ledger rows on `how_it_works`. Approve takes the default. Contest
sends the words to Vision Keeper through the contested loop.

**Hold.** Yes, as today.

### Page 2. The commitments page

**When.** Architect has read the ratified statements against the model and
written the constraints the statements create (deliver, built today).

**Blindspot.** The Architect derives promises from the principal's words,
and the principal never sees them. Signoff presents items only. A decided
constraint reaches the principal only if a diff later violates it.

**New.** The constraints the statement created, each as one sentence in
words: what will persist, what will be exposed, what outside code will
depend on. Contracts and data shapes are what law 12 already calls a
commitment. Sequence diagrams are out. wsff says they can be overkill, and
an 8B model cannot draw one that holds.

**Rulings.** Approve does not stamp. A `reasoned` row becomes `decided` when a
ruling ref lands through adopt. Contest sends the words to
Architect. On the plan path this page is the bottom half of page 1.

**Hold.** No. A wrong commitment is caught at page 3 or by structural review.

### Page 3. The design page

**When.** Tickets exist, criteria exist, the batch is grouped, and annotate
has run. Today annotate writes paths and symbols and touch_note shows them
as a sense check nothing waits on (P4, R7).

**Blindspot.** Rota shows where the change lands. wsff shows what it is.
Every signature is a decision otherwise made during code review, at the
most expensive moment to change a mind.

**New.** A design mode for the Architect, keyed by its cause: a batch with a
touch set and no design. It reads the criteria and the source and writes
four things.

1. The file-tree diff: which files are new, which change.
2. The signatures: one per callable the criteria name in `surface_refs`,
   with types. The criteria brief already makes the Terminologist name the
   callable. The design names its shape.
3. The call tree: from the entry point to the named callables, in diff
   form.
4. The slice order: the tickets of the batch in build order, contract
   outward. This is the fact the grouping brief promises and no tool
   writes. It lands in `batch_dep_facts` through a new `batches.depend`
   op, and within a batch as the ticket order.

Liaison presents the four as one page, rendered in words at the edge.

**Rulings.** Approve lets the batch start. Contest with words goes to the
Architect, who amends. A contest about scope is the Architect's
`msg.propose_vision_keeper`, as today. Law 12's rule stands: nothing
mechanical rejects a diff for straying from the design. The principal
approved a shape, not a fence.

**Hold.** Yes. This amends ruling 2 of 2026-09-12, "hold at intent time
only", to "hold at intent time and at design time". The touch note stays
non-blocking on the oneshot path, where no design page exists.

**Feasibility.** Signatures from `surface_refs` are close to what the
criteria mode already does. The call tree is an untested judgement at the
8B tier. Preregister a case, run both models, and keep the 14B fork open.

### Page 4. The slice read

**When.** The Developer has committed one ticket's diff, tests are green,
Critic has passed it.

**Blindspot.** A batch is built in one session and judged once.
`merge_gate=review` returns "waiting on the principal's review" and no
predicate presents anything. The lights-on setting leads nowhere.

**New.** The ticket is the slice. The Developer builds one ticket per
session, in the order the design page set. After Critic passes a ticket,
Liaison presents its diff as a page: the ticket, its criteria, the diff,
and the design it was built against. The principal reads 100 to 200 lines.

**Rulings.** Approve lets the next ticket start. Contest with words goes to
the Developer, who amends against `principal_said`, as the contested loop
does for items.

**A page is a hold or a note. There is no third kind.** (Ruled on the
2026-09-13 questions.) A hold waits on a keypress, and the batch defers
while it waits. A note waits on nobody: the build goes on, the page stays
owed on the register until answered, and a contest that arrives after the
work is an amendment under law 9 and E1 level 2. "Silence approves" was
a third kind, and it needed a clock. Law 13 forbids a clock on a page,
and a step count is a clock in the frontier's units. So the predicate
reads no clock. It reads whether the page is a hold or a note, and
whether a ruling row exists.

**Hold.** Full path: the slice read is a hold, per slice. Plan path: the
slice read is a note, and the batch merges after its last ticket passes
as today. Oneshot: the merge read is a note.

**R7.** A hold on a slice must not block all building. The Developer is
single-instance and `batch_start` waits on the running batch. So a batch
held on a slice defers, as law 9's preemption defers, and the next
schedulable batch starts. The held batch resumes on the ruling. A contest
on a slice has its own cap, in the `contest_defences` mould. A contested
design cascades to the tickets not yet built. Both are open in the build
order.

`merge_gate` becomes the path's read rule. The default is *plan*, which is
lights-on. wsff's evidence and rota's tips walks both argue for it.

### Page 5. The got-it page

**When.** Every batch of an item has merged. The system is quiescent on the
item and its ledger rows are closed.

**Blindspot.** Quiescence with an empty ledger is the system saying it has
nothing left. L0 says only the principal can say they got what they
wanted, and nothing asks them. R1 rules there is no finish line, so this
page is a ruling on one item, never an ending.

**New.** One page: the success line from page 1, the batches merged under
it, and the question. Approve records a decision under the principal's
name that resolves the success row. Contest with words is a new statement,
and the understanding loop runs again. There is no third loop, as LAWS
says.

**Hold.** No. Nothing waits on it. The register shows it as owed.

### The design is an artefact, not a page (added after the long-term question)

A design page per batch is approved, built against, and forgotten. The
next batch's Architect drafts from source with no memory of what the
principal ruled. Over a long project that is a chat's memory, which L0 was
written against. So the shape is a standing artefact, the way the glossary
is.

- One writer, the Architect (law 1).
- Rows keyed by callable, not by batch (law 14). A signature row is the
  same row across batches.
- Provenance derives from refs (law 11). A row is `observed` when a design
  page first names a callable and the row rests on its grain in the index.
  The index already holds every callable. A row is `decided` when a ruling
  ref lands through adopt after the principal approves the page. Approve
  does not stamp. The artefact
  holds only what was ruled on or drafted for a ruling. Click has 885
  callables. The index is the 885. The shape is the ones a criterion or a
  design ever named, filled in as batches touch them. That is the size of
  R9's memory, not the size of the repository. (2026-09-13.)
- The design page is an amendment to this artefact, presented as pages
  already are.
- Structural review intersects a diff's grains with design rows, as it
  intersects bindings today. A diff that changes an approved signature is
  a finding. No model judges quality. The finding is a fact: this shape
  was ruled on and this diff changed it.

This gives E6 a third kind of drift, keeps X1 post-core, and gives the
principal's design rulings the settled memory R9 requires. It is one
table, one writes-edge, one identity declaration, and one more join in
the review trigger.

## The paths

| path | pages | holds | notes |
|---|---|---|---|
| oneshot | 0, 1, then merge | page 1 | the merge read |
| plan | 0, 1+2, 3, 4 per batch, 5 | pages 1 and 3 | pages 2, 4, 5 |
| full | 0, 1, 2, 3, 4 per slice, 5 | pages 1, 3, and each slice | pages 2, 5 |

The path is a row the principal approved at page 0. A contest at any later
page can raise the path. Nothing lowers it without a ruling.

## How the seat guides

1. **One page at a time.** The seat shows the page that is owed and nothing
   else. A run with no page owed shows the ticker and the register.
2. **The header says what the page is for.** "Design for b1, page 3 of 5.
   Approve starts the build. Contest sends your words to the Architect."
   The principal never has to know which desk owns what.
3. **Most important first.** Within a page, the row that changes the build
   most is first. This is the 2026-09-12 ruling, applied to every page.
4. **Never twice.** A page after a contest shows only what is still open.
   `_bind_send` already refuses a clarify whose words were put once.
5. **The header says whether the page holds.** "The build goes on. Contest
   later and it becomes an amendment" for a note. "Waiting on you. Other
   batches run" for a hold.
6. **Contest is words, not a form.** The words go to the owner. Liaison
   relays and never interprets, as today.
7. **The register names the page owed.** "owed: design page for b1". The
   cockpit answers why the page says what it says.

## What this changes in the rulings

- Ruling 2 of 2026-09-12: hold at intent time only. Becomes: hold at intent
  time and at design time, on the plan and full paths.
- R7: the touch note never blocks. Stands on the oneshot path. On the other
  paths the design page replaces the touch note.
- `merge_gate`: auto or review. Becomes the read rule of the path, default
  plan. The review page is built, so review no longer waits on nothing.
- Grouping: the brief's dependency sentence gets its tool. A tool in the
  list changes the plain case, so the grouping case is re-recorded.

## Build order, each piece measured

1. **Deterministic first.** `batches.depend` writes `batch_dep_facts`. A
   `slice_read` predicate presents a passed ticket's diff. `principal.land`
   takes approve and contest on a diff page. The ticket order inside a
   batch is a column the design writes and `batch_start` reads. Pinned in
   tests, no model.
2. **Page 1's two rows.** The deliver brief logs the example and the
   success line as ledger rows. The account case on the register measures
   it. The A1 plan records that a paragraph moved the account case from
   5/5 to 0/5 once, so this is one sentence at a time, re-recorded each.
3. **The design mode.** New mode, its own tool list, its own case with a
   preregistered expectation, on both models. Signatures first, the call
   tree second, because the first is close to work the criteria mode does
   and the second is new.
4. **The commitments page.** The signoff present adds the statement's
   decided constraints. Mechanical: the rows exist, the present is missing.
5. **Page 5.** A predicate presents the success row once an item's batches
   have merged. Mechanical.
6. **Cold walks.** "tip calculator pls" on oneshot. "a CRM for a small
   plumbing business" on full. Both write a result row first, as the
   model-setup plan requires.

## Recommendation, 2026-09-12

Do it in two stages. Defer the rest.

**Stage 1, before the gauntlet (goal 10).** The strict gains and the dead
ends:

1. One ticket per Developer session, one Critic verdict per ticket. The
   smallest scope per 8B call, and the change most likely to raise the
   register on its own.
2. The slice read page, so the review setting stops waiting on nothing.
3. `batches.depend`, so the grouping brief's sentence has a tool.
4. The worked example row on page 1. One sentence, re-recorded.

**Stage 2, as goal 5.** The shape artefact, observed from the index at
onboarding, amended by the design page, joined into structural review.
Held on the plan path. Signatures and slice order first. The call tree
only if signatures hold on both models.

**Deferred.** Page 2, page 5, the full path's per-slice holds. None pays
before the lineage merges cold.

**Where it sits in the plan.** After click's first cold merge on the
batch unit (2026-09-13, question 1) and before goal 10. The gauntlet measures the delivery loop, and stage 1
changes that loop. Goals 4, 6, 7, 8 and 9 are untouched. Goal 3's walks
re-run once on the new unit.

**Rulings owed by the principal before stage 2.**

- Hold at design time on the plan path. Amends ruling 2 of 2026-09-12.
- Default to the plan path. Today's default is auto merge. Oneshot stays
  one keypress away.

## What it costs, said plainly

This is not a strict upgrade. It trades autonomy and compute for the
principal's eyes at the shape of the code.

- The default changes from auto merge to the plan path. A principal away
  for a day stops every batch at its design page.
- Two more holds per batch on the plan path. A6 calls the principal's
  attention the one budget that cannot be refilled.
- One Developer session and one Critic session per ticket, not per batch.
  The Critic's hardest case runs on gemma3:12b at 8 GB, which swaps with
  the 9B on a 10 GB card. Per-ticket verdicts are one swap per ticket
  unless the band order queues the Critic behind the Developer.
- C4 and C5 reopen. Walks and the Developer and Critic cases recorded
  before stage 1 measure a loop that no longer exists.
- Three paths are state the seat shows and the predicates read.

The strict gains: `batches.depend` makes a dead sentence true; the review
setting gets its page; the worked example answers a measured stall; the
ticket unit fits the 8B context.

## Size

| kind | count |
|---|---|
| new presents or predicates | 5 |
| new ops | 1 |
| new model modes | 1 |
| new tables | 1, the shape |
| brief edits | 4 |
| new register cases | about 8 |
| re-records | 5 |
| ruling amendments | 3 |

For calibration: A1 pieces 1 to 4 and P4 piece 1 took 2026-09-03 to
2026-09-12. This plan is that much again, plus the ticket unit, which
nothing this month touched. Roughly a third of the second half of the
budget.

## The audit's universe, entry by entry

Checked against `plans/responsibility-audit.md` and
`plans/archive/responsibility-allocation.md`.

**Conflicts and corrections.**

- R7. A hold on a slice of a running batch blocks all building. Fixed in
  page 4: a held batch defers, the next schedulable batch starts.
- C2 is graded VERIFIED on `batch_dep_facts`. No tool writes that table.
  The honest grade today is PARTIAL. `batches.depend` earns VERIFIED. The
  allocation doc is the audit's, closed, and the grade change is the
  principal's to record.
- R1. Page 5 is a ruling on one item, never an ending.

**Amended.** R17 keeps both moments: page 2 is the coarse guess, page 3
the grounded one, and page 3 holds on the plan and full paths. R16 stands.

**Strengthened.** A1 (three more silent points at intent), A7 (pages 2 and
3 before any code), C3 (program design under the Architect), C6 (a signed
shape makes incidental change answerable), D1 (the principal reads as a
second non-builder), E3 (every page carries its rows), E6 (a third kind of
drift), F1 (the path is the attention knob), G1 (the worked example is the
S0 stall).

**Changed in mechanism, same grade.** C4 and C5 (the unit is the ticket),
D4 (a contest on a slice needs its own cap), E1 (a contested design
cascades to the tickets not yet built).

**Consistent.** R2 keeps maintainability post-core: the slice read is the
principal doing it, not a role. R3, R8, R10, R11 hold as written.

## The Architect and the principal

The split on the design page:

- **Signatures.** The principal rules. L0 says the principal is technical,
  and wsff says these are the decisions otherwise made at code review.
  The Architect drafts, not the Developer: a Developer drafting its own
  design and building it is the builder judging its own plan (D1).
- **Slice order.** The Architect's order is the default. The principal
  contests it. C2 gives ordering to the principal by priority and to the
  Architect by dependency.
- **File diff.** A fact about the plan. A sense check.
- **Off the page.** The touch set of paths and symbols, and constraint
  bindings. Both mechanical.

**The route the Developer needs.** The Architect never writes code, and on
8B a signature may not be buildable. The Developer already escalates to
the Architect for a constraint it cannot satisfy. A signature it cannot
build to goes on that route: one sentence in `batch_start.md`, one ref on
the escalate. Without it the Developer builds something else and logs
nothing.

**The unchecked window.** On the plan path, after the principal approves a
design, nobody compares the diff to it until the batch read. Law 12
forbids a machine doing it as a gate. The shape artefact makes the
difference a finding at structural review, which is a fact, not a gate.

## Questions from the seat, 2026-09-13, and the rules

**1. Click first.** Click stays on the batch unit until its first cold
merge. Stage 1 changes the loop under measurement, and every Developer
and Critic recording and all 27 click nights measure the batch unit. A
rerun that destroys its own control is the mistake SEAT.md names. One
honest merge on a real repository is the control every later comparison
needs. If click's last red turns out to be the batch unit itself, a
Developer session too large for one call, that is the evidence for stage
1, and the switch happens then with the red as its case.

**2. Silence.** There is no silence. A page is a hold or a note. A hold
waits on a keypress and the batch defers. A note waits on nobody and
stays owed on the register. A contest after the work is an amendment. The
predicate reads no clock, wall or step. R7's stall is a hold nobody
answers, and that is not a stall: the register says "waiting on you" and
every other batch runs. E4 must show it as waiting, not stuck.

**3. The shape's size.** The shape holds what was ruled on or drafted for
a ruling: the callables a criterion or a design page ever named, filled
in as batches touch them. Observed rows are read from the index at the
moment a page first names the callable, not at onboarding. The index
holds the 885. The shape holds the memory.

**4. The Critic's cost.** Accepted, and now in the cost list. One verdict
per ticket multiplies Critic calls, and gemma3:12b at 8 GB swaps with the
9B on a 10 GB card every turn. Three swaps on a tipsI-sized batch where
there was one. The relief is scheduler order, not a smaller unit: within
the band, the file order offers the Developer's next ticket before the
Critic's review of the last one, so the Critic's reviews queue and the
swap is per batch. The price of that order is a fail on ticket 1 found
after ticket 3 is built. Measure both orders on tipsI before choosing.

**5. The default is measured by a person first.** The two rulings, hold
at design time and default to the plan path, are the knob the seat
exchanges were about. Twice on 2026-09-12 a person at the seat said "stop
asking me". The design hold is the right hold, because it is the cheapest
moment to change a mind, and the reconcile pages were the wrong ones. The
default does not ship until the principal has driven one batch on each
path at the TUI. A driver cannot measure "stop asking me".

## What stays rota's, and wsff does not have

- A ledger row for every silent point, on every page, resolved only by a
  ruling that names it.
- Provenance on every row the principal rules on.
- No time, no estimate, no deadline on any page (law 13).
- No reviewer election. There is one principal.
- Every page change is measured on the register before it is kept.

## Answers, 2026-09-13

Roman's rulings on the four questions the plan raised, recorded in
`rota/DECISIONS.md` ("The principal's flow: five rulings").

1. **Click first.** Stage 1 changes the loop under measurement, and a
   rerun that destroys its own control is the mistake SEAT.md names.
   Click's first cold merge on the batch unit is the control. If click's
   last red is the Developer session being too large for one call, that
   red is stage 1's case and the switch happens then.
2. **There is no silence.** A page is a hold or a note, nothing else. A
   hold waits on a keypress and the batch defers. A note waits on nobody,
   stays owed on the register, and a contest after the work is an
   amendment under law 9. The predicate reads no clock, wall or step: it
   reads the page's kind and whether a ruling row exists. "Silence
   approves" needed a clock, so it is gone. On the plan path the slice
   read is a note and the batch merges after its last ticket as today. A
   hold nobody answers is not R7's stall: the register says waiting on
   you, other batches run, and E4 shows it as waiting.
3. **The shape holds the memory, not the repository.** Rows are the
   callables a criterion or a design page ever named, filled in as batches
   touch them. Observed rows are read from the index when a page first
   names the callable, not at onboarding. The index keeps the 885.
4. **The Critic's cost is accepted** and in the cost list. The relief is
   band order, not a smaller unit: offer the Developer's next ticket before
   the Critic's review of the last, so reviews queue and the swap is per
   batch. The price is a fail on ticket 1 found after ticket 3. Measure
   both orders on tipsI before choosing.
5. **The default is measured by a person first.** The two rulings, hold
   at design time and default to the plan path, do not ship as defaults
   until Roman has driven one batch on each path at the TUI. A driver
   cannot measure "stop asking me".
