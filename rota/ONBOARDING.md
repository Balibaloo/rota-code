# Onboarding, derived

Written the way `SYSTEM.md` was: not what onboarding does, but what a system
that has to *understand a repository it did not write* has to contain — taken
from the purpose and the evidence — and then the diff against what exists.

## Purpose

Turn a checkout nobody here has read into what the delivery loop needs to act on
it: the glossary, the constraints and the items, with honest provenance
(`observed`), honest coverage (constraint zero), and every judgement call
parked with the principal rather than made silently.

Stated as a test rather than an inventory, because an inventory can be full and
wrong: **onboarding is done when a cold role can act on the repository from the
artefacts alone.** A Developer who has read only the glossary writes the right
thing; a Critic can judge a change against the constraints; a Vision Keeper can
slice against the items. The answer key asks exactly that question in prose
("would a Developer who read only the glossary write the right thing?") and
has never measured it — so the score against the key is the floor, and a
downstream probe is the ceiling.

And the second output is the first one's shadow: **what the system could not
determine.** A word declined (`none_found` for `@term:x`), an area abandoned by
the attempt bound, a collision parked with the principal — each is a row, and
together they are the honest account of where understanding stopped. A run
that learned nothing must not report success; this is how it does not.

## What the evidence forces

Twenty-four worklist items on one repository (`probes/cnt/WORKLIST.md`) fixed
everything *beneath* the question and moved recall from 0 to 4 of 10 required
terms, where it stayed for six runs. The probes in items 21–24 then produced
all ten with zero trap hits — from hand-assembled context, in a handful of
single calls. The material produced the answers; the system failed to bring the
material and the question together. Five things follow.

1. **Orientation is the first artefact.** The account of what the program does
   for its user is the one context that displaces the everyday reading of a
   word — handed the call trace the model kept "an intent is a user's goal";
   handed the account it wrote "a recipe for making a note". The brief had
   never said what the project was: `Obsidian` 0, `plugin` 0 in 8,050
   characters. So something writes that account once, before any word is
   named, and every later phase reads it.

2. **The unit of work is the question, not the area.** The glossary answers
   *what is this, where is it written down, what is it for*; a constraint
   answers a counterfactual — *what breaks outside if this is renamed*; items
   answer *what does the product do*. Rota asked one question ("survey this
   area") of three roles and expected three artefacts to differ because the
   tables did. They cannot.

3. **Context is shaped like the answer, and the harness assembles it.** A
   meaning is not shaped like a place: `intent` lives in five areas and no
   area-shaped question reaches it. Every failure in items 11–21 was a cold
   session failing to reach material that already existed; asked to fetch, the
   model guesses filenames instead. *Compute the reach, do not ask the model to
   reach.* Areas stay for what they are good at — coverage accounting and the
   words only one place uses.

4. **Phases produce artefacts; concatenation destroys them.** No single probe
   structure dominated; each mechanism won specific terms, and stuffing them
   into one prompt scored below any alone. The mechanisms are additive only as
   phases whose output feeds the next, which is the shape the mechanical half
   already had — `index → partition → zero` — stopped one step short.

5. **Gates check shape; the principal absorbs judgement.** Prose was inert seven
   measured times; a checker used as a gate rejects correct entries. Structural
   guards on the *form* of an answer, and `observed` provenance carrying the
   residual wrongness to the principal's agenda.

## The spine

```
index       what exists, and what depends on what              mechanical
partition   areas, from directories, checked by the graph      mechanical
lexicon     the words the checkout declares, ranked            mechanical
zero        one constraint over everything unsurveyed          mechanical
orient      what the program does for its user, from code      vision_keeper, one session, @program
reconcile   the README read against the account                vision_keeper, one session, @prose; disagreements to the ledger
define      what each declared word means here                 terminologist, one session per word, @term:x
survey      what each area adds, and what it is bound to       terminologist then architect, per area
collision   one word, several readings: synthesise or report   terminologist, after the survey pass
agenda      observed entries and parked collisions             liaison → principal
```

Phases are strict and derived, never remembered: `scheduler.onboarding_phase`
reads the rows — an orientation record, the pending words, the unsurveyed areas
— and the predicates `orient`, `define` and `survey` fire only in their phase.
Each is discharged the way a survey always was: a record for the subject, or
the attempt bound. `onboarding_phases` is a setting; `survey` alone is the
pre-orientation design, kept so one phase can be measured against another.

**Subjects.** A wake's subject is `refs[0]`: a path for an area, `@program` for
the orientation, `@term:<word>` for a word. `ctx.area` carries it into the
session; `surveys.attest` files the record under it; a glossary row written for
a `@term:` subject has no area, because it was written about the whole program.

**The lexicon** (`onboarding/lexicon.py`, table `code_lexicon`) is the list of
words no session may choose: a directory name, a file name, a declared type's
head noun and compound, an authoring-surface key — weighted in that order, with
frequency as a tie-break that never decides. The orientation promotes it at
frontier time: a word the account needed scores higher, and two lexicon words
the account says together that the code also says together are one compound.

**What each session is shown** is pushed, by the existing rule — every read
callable with no arguments runs before the first turn:

| phase | pushed | question | closes with |
|---|---|---|---|
| orient | `code.front`: manifest, authoring surface, README's beginning, entry point | what does this product do for its user | items, then `attest` |
| define | `problem.baseline`, `code.concordance` for the word | *in this project, a X is …* | one `glossary.amend`, or `none_found` |
| survey (terminologist) | `problem.baseline`, `glossary.consult`, `code.area` | what does this area call things the glossary does not yet name | `attest` |
| survey (architect) | `problem.baseline`, `code.area`, `model.consult` | what could be renamed here without anything here failing, and who outside breaks | `model.amend`, then `attest` |

## Where the laws are touched, and where they are not

Nothing here shares context between sessions. The orientation is an artefact
(`items`, Vision Keeper's), read by the next phase through a declared edge
(`problem.baseline`) — which is exactly "shared state must be artefacts", and
the reason the define phase is allowed to know what the program is. Law 3 is
unchanged: `code` is a fact artefact and generates no contact; reading `problem`
derives a contact to Vision Keeper that Terminologist and Architect already hold.

`glossary.amend` in a define session is pinned to the wake's word — a session
that defines another word has left its own undone — and a spelling of the same
word is filed under the word the wake named. An area session that says a
program-level word differently writes a second row, never a replacement: the
collision the glossary exists to surface, and the failure mode (`INSERT OR
REPLACE` destroying the sense the run already had) that cost four correct
senses in two measured runs.

Vision Keeper's per-area pass is withdrawn from `SURVEY_ORDER`, not deleted. It
wrote sentences about code because a folded directory is not where a product's
behaviour lives; the orientation is the same role asking the right question at
the right grain. Putting it back is one edit and a re-measurement.

## What this does not claim

- One repository, one answer key, mostly one run per design. The first
  validation is below; the honest second one is another repository.
- Two failures are the model, not the design, and were isolated by
  elimination: the second-person collapse past one exchange, and the inability
  to *argue* that two senses are the same. The phase shape reduces exposure
  (fewer turns, nothing asked for an argument); it does not remove it.
- The counterfactual question for constraints is half-tested and the items
  question was untested before this. Both now run through the same probe-first
  loop; neither should be assumed to transfer because the definitions did.

## What the first run taught

`cnt_u`, 2026-08-23, `llama3.1:8b`, the phase design as first built. Quiescent
after 60 sessions and 20 minutes; every phase ran in order and handed its
artefact forward. Read end to end before scoring.

    terms_required present   5 of 10   intent · template · prompt · variable · provider
    must_not_mean (scorer)   0 hits    -- but `intent` is "a note's purpose or goal", which
                                          the literal-phrase matcher does not catch
    constraints              2, neither of the required two; `.` abandoned by Architect
    items                    5, product-level and generic
    sessions at the 12-turn cap   15 of 60  (~180 of ~300 turns)

**What held, structurally:** the phases, the subjects, the lexicon (the right
words were woken: `intent`, `template`, `variable`, `note`, `folder`, `prompt`,
`provider`, `frontmatter` was next), the pushed front and concordance, the
attest derivation of the orientation record, `observed` provenance throughout,
three collisions synthesised after the survey pass, quiescence with the
quarantines on the principal's agenda.

**What the loops were, and each is a harness fault closed the same day:**

| loop | sessions | fault | fix |
|---|---|---|---|
| `note`, define | 3 × 12 | model wrote `TOOL: glossary.amend [term=...]` and was refused every turn | the parser reads `name [args]` as the parentheses it stands for |
| `provider`, `intent suggest modal`, define | 2 × 12 | the word landed on turn 2; the session had no terminal act and re-sent its batch | a define session ends when its glossary row lands |
| `template`, `intent`, define | 3 each | `code.concordance(term='template')` restated the pushed subject and held the amend | a read of a pushed function is never fresh, whatever its arguments |
| `.github`, `providers`, `.`, survey | 3 × 12 each | `found` claimed with nothing written, refused, claimed again; attest held behind fresh reads | the outcome follows the writes; attest is never held |
| `.`, Architect | 3 × 12 | bindings were manifest keys; the refusal pointed at `code.probe`, which the mode lacks | the refusal names the paths the session opened |

**What was the model, not the harness:** the senses. Generic where the probe
was specific, because the orientation was five one-line behaviours and not the
account of how the thing works — the probe's account named `intents_to`,
frontmatter, templates, prompts; the run's items named none of them. Two
structural answers, both in `cnt_v`: the orientation brief asks for the causal
account first (what the user writes, what is read, what it turns into, what
comes out) and items from it; and a define sense must name where the word is
written down — a key, type or file the concordance showed — which every entry
in the answer key does and no generic sense did.

## The second run, and what it changed

`cnt_w`, same day, with the first run's five harness fixes and the revised
orientation brief. Quiescent after 58 sessions and **9 minutes** (20 before);
every area closed; one turn per area for the Terminologist's residue pass and
1–3 for most of the Architect's.

    terms_required present   5 of 10  (+ `variable_type` named)
    must_not_mean (by reading)  2: `intent` "a task or action", `folder` "container"
    senses naming a place    most -- the one-refusal nudge works that far
    constraints              5, every one an orientation item copied verbatim
    sessions at the cap      10 of 58, all the define phase's place-guard

Two findings, both structural, both closed before the third run:

- **The place-guard as a gate is a loop.** Refused, the session opened the
  declaring file — the nudge works — and then re-sent the identical sense for
  eleven turns; `note`, `setting`, `global intent` and `template select modal`
  were abandoned that way, three sessions each. A gate this model cannot
  satisfy loses the word; the guard is now one refusal, then the entry lands
  flagged ("naming no place") — the checker as flagger, which item 22 of the
  worklist had already measured as the right shape.
- **The pushed baseline is a list, and the Architect defined the list.** Five
  constraints, `commitment 1`…`commitment 5`, each an item's text. The
  worklist's founding finding — whatever is on the list gets defined — applied
  to a different role and a different list. Two guards, both on shape: a
  headline with no content word is a label, and a constraint whose text
  restates an item has answered the item's question, not the constraint's.

And three smaller ones from reading the transcripts: the orientation's
`problem.assert` lines were bullets under its account and the parser took only
the marked attest (bare and labelled calls at line start now merge with marked
ones); the define brief said "the word is on the `Refs:` line" and the model
defined `@term` (the prompt now says `The word: note`); and the define brief
ended on a `none_found` escape hatch, which became the exit the turn after a
refusal (the terminal act is the amend, and the hatch moved up and narrowed).

`global intent` was woken in this run: the orientation said "global intents",
the code says `globalIntents` fifteen times, and the bigram promotion composed
a word the lexicon alone could not carry. It was then lost to the place-guard,
which is the cost the bound now caps.

The third run (`cnt_x`) was stopped at the orientation: the account was the
best yet — "the authoring surface… defines intents, which are rules for
creating new notes based on existing ones… the program prompts for values and
templates… creates a new note" — and every behaviour under it was a prose
bullet, not a call; the derived outcome closed the orientation empty and every
define session ran without a baseline. The orientation is the one subject whose
empty record costs the whole run, so its first `found` with nothing written is
now refused once, naming the call shape, before the derivation applies.

The fourth (`cnt_y`) ran the orientation and the whole define phase clean —
five items from the account, twenty words in twenty sessions, one to three
turns each, none abandoned, `intent` off the "goal or action" reading for the
first time — and then looped on `.github`: the labelled-block merge now parsed
a `glossary.amend: term: artefact` block, the frame-word gate refused it
(rightly), and the rule that a refused write holds the attest refused
`none_found` too, every turn, with the right answer in hand. Two rules pointing
at each other. The hold is one refusal now — the turn to fix or drop — and
then the record follows what landed, which is the same bound every other
guard in this design ended up with.

## The fifth run, scored

`cnt_z`, the same day, with everything above. Quiescent after **52 sessions and
7 minutes**; every phase; two real collisions parked with the principal as
`clarify`; two Architect areas abandoned on a hint that printed `.github` paths
without their dot (fixed after, with a test).

    terms_required present   6 of 10   intent · template · prompt · variable · provider · global_intent
    named, not defined       +1        variable_type (as `template variable type`)
    must_not_mean            2         note "document", folder "container"
    copied from the index    0 of 28
    constraints              5; two on the key in substance -- "relies on the Filtered
                             Opener plugin" (the_filtered_opener_plugin_api) and
                             "compatibility with Obsidian's changing API" bound to
                             versions.json (the_minimum_obsidian_version) -- at
                             "relies on" precision, not the key's "reached by id
                             through a private field"
    orientation              5 items from the account; the account names the
                             authoring surface, intents as rules for new notes,
                             prompting for values and templates

Against the worklist's best single run on this repository (`d`: 4 defined, 2
named, 0 traps, 117 turns, never reaching the Architect) this is 6 defined, 1
named, 2 traps, ~140 turns, and all three roles ran to quiescence. `global
intent` -- "a set of predefined intents available everywhere… written in a note
specified by `globalIntentsNotePath`" -- is the key's sense, and it was a word no
run had ever woken: the orientation said it, the code spelled it, the bigram
promotion composed it.

What is still the model: the senses of the five prompt types, which the key
built the probe around. `note` reads as the document and `folder` as the
container whatever is pushed; the concordance for each is dominated by the
ordinary uses of the word, and the line that settles it -- `of_type:
"text|number|natural_date|note|folder"` -- is one among many. That is the
remaining lever and it is a context-shaping one, not a scheduling one: a
define session for a word with an enum member of its own name could be handed
the enum first. Not built; measured as the next wall.

The harness faults found by reading these five runs, all closed the same day
and each with a test: square-bracket and labelled-block call syntax, bare calls
beside marked ones, a pushed read re-called with its subject, the define
session with no terminal act, `found` claimed with nothing written, the attest
held behind reads, the place-guard and the refused-write hold as unbounded
gates, the orientation's items as prose, the `@term` sigil read as the word,
`sense=` in a define session, manifest keys as bindings, items restated as
constraints, dotted paths in hints, nested citation lists, and a root area
restating every word. Every one of them presented as a twelve-turn loop, and
none of them was visible from a score.

`cnt_final`, with the three fixes the fifth run exposed: **46 sessions, 268
seconds, nothing abandoned**, the same 6 + 1 of 10 and the same two traps, one
constraint (the Filtered Opener dependency, written well on one attempt and
overwritten on the next by the same id -- a loss a later amendment rule could
stop). Against the baseline of the same design that morning -- 60 sessions, 20
minutes, fifteen of them at the cap -- that is the spine doing what it was
built to do, and the senses where the model leaves them.

## Understanding, not metrics: the downstream probe and what it forced

The scorer can say 8 of 10 and the artefacts can still fail a developer. So the
goal stated above is now measured directly: `probes/downstream.py` hands a cold
model the run's glossary, items and constraints -- no code, no README -- and
asks seven questions a maintainer of cnt must be able to answer (where a user
writes a recipe and under which key; what a `note` prompt asks for and what
answers it; the five prompt kinds; who is affected if `with_templates` is
renamed; what a template is; global against local intents; what a provider
does). Read, not scored.

On the 8-of-10 run (`cnt_ab`, llama3.1:8b, 42 sessions, 2.5 minutes) the answer
to five of the seven was "the notes do not say", and on the same pipeline under
qwen2.5:7b (7 of 10, zero trap hits) the same five. The information was in
front of the define sessions every time -- the enum with its five members, the
`of_type` line, `providers/note.ts` calling the filtered-opener -- and was
summarised away: "an enumeration that specifies different types", "a piece of
information to be stored". That is the gap between evidence and artefact, and
it is the last one that was structural rather than the model's.

What changed for it, each measured on the next run:

- **The concordance is sections, by what kind of statement a line is**:
  declared as a kind (an enum member, with the enum's header) · in what a user
  writes · a file of its own · registered · declared · used (prose last) ·
  flows -- and it carries the declaring file whole where it fits. `note` now
  opens on `enum TemplateVariableType { note = "note" }`, `of_type:
  "text|number|natural_date|note|folder"` and `providers/note.ts` with its
  `api_getNote` call.
- **A kind is defined by its kind.** When the concordance shows the word as a
  member of an enum or an option in what a user writes, the sense must name
  the enum or a sibling; an enum's own sense must name its members (all of
  them when there are eight or fewer). One refusal, then flagged, like every
  guard here.
- **The orientation's account is kept** as the first item (`how_it_works`),
  so the baseline carries the mechanism and not only its headlines.
- **The Architect's answer has a shape** -- RENAME WHAT / WHO BREAKS / WHAT
  HAPPENS, the form that found the schema contract in the worklist's probe --
  and a guard for its failure mode: a WHO BREAKS naming a maintainer, the
  build or the tests is inside, and refused.
- Two harness faults found by reading the qwen run: a call written one
  argument per line fell to the lenient parser (newlines outside quotes are
  whitespace now), and `intents_to` split into the compound "intent to".

## Readers, measured on the same harness

Three readers on the identical pipeline, the same day, after the sections above:

| reader | define terms | traps | a maintainer's question answered from the artefacts |
|---|---|---|---|
| llama3.1:8b | 7 + 1 named | 1 | `note` "a type of template variable"; `template` and `provider` half-right; the rest "the notes do not say" |
| qwen2.5:7b | 7 | 0 | the same two half-right; the same five unsaid |
| qwen2.5:14b (partial offload, ~40–90 s a turn) | 6 + 2 named (20 defined; `global intent` never promoted: its account did not use the words) | 2, both generic headlines over right bodies | `template variable type` lists all five kinds; `provider` names both lookup tables and the five types; `date` names `natural_date` and the nldates plugin; `intent` names its fields and its file. Asked the seven questions from the finished run's artefacts, the same reader answered three and a half -- the frontmatter question, the rename-a-key question ("their existing recipes stop functioning"), `provider`, half of `template` -- and said "the notes do not say" to the five kinds it had itself written down. Re-probed on the define-phase glossary alone (20 rows, not 74): the same. The reader is brittle on that mapping at temperature zero; the residue rows were not the cause, which was worth knowing before guarding against them. |

The 7–8B readers plateau at the same place whatever they are shown; the 14B
reads what it is shown. Seven harness findings came out of reading it: a call
written one argument per line; the prompt's own `[artefact.verb]` push label
used as a call label; a survey session that re-sends its batch verbatim --
which is a fixed point at temperature zero, so the runner ends a session on
the third identical turn; and the reason it re-sent it. Every 14B survey ended

    outcome="found"
    citations=["src/intents/index.ts", "src/variables/index.ts"]

with no function named at all: the attestation minus the words
`surveys.attest`. The parser now takes a block of bare `key=value` lines as a
call when exactly one function in the working set has those parameters
(`outcome`/`citations` is only ever `surveys.attest`; `term`/`sense_body` only
`glossary.amend`); two candidates is ambiguity and is not parsed. Two areas
had been quarantined for want of those two words. And the first collision it
was woken for wrote its synthesis on turn three and re-sent the identical call
five more times, a minute each, until the third-identical rule ended it: a
collision session now ends on the write that is its verdict -- a synthesis or
a `glossary.same`, either of which leaves a row superseded -- as a define
session ends on its amend.

The last two were about the survey push, and they are the ones that matter for
understanding rather than throughput. `[code.area]` had a budget of 5,200
characters, sized when it fed the per-word define and a barrel plus a schema
was the point. For area `src/intents` it showed the Architect `index.ts` (891
bytes) and two *imported* files, and named the area's own `frontmatter.ts` and
`intents.ts` -- the parser, where every frontmatter key a user writes is read
by name -- as "did not fit". The Architect attested `none_found` for the one
area that holds the program's largest commitment, from a prompt of 6,644
characters in a 12,288-token window. The push is now 10,000 characters, the
area's own files whole while they fit, then a head of each own file that does
not, then the imports with what remains; an own file is never shown less than
an import. (It was 14,000 for one pass: at a 20,000-character prompt the same
reader that wrote well-formed calls from 7,000 wrote `glossary.amend:
\`intent_schema\`, The structure defining ...` and nothing parseable, twice,
and the area was abandoned. The reader's discipline is a function of the
prompt's length; the budget only has to be large enough to put the area's own
parser in front of it.) And for the root area the same Architect answered RENAME WHAT / WHO
BREAKS / WHAT HAPPENS five times over `manifest.json` -- the plugin's id and
name among them -- attested `found`, and wrote no `model.amend`; deriving
`none_found` from the writes was true to the writes and false to the session.
The orientation's rule now holds for every subject: a `found` with nothing
written is refused once with the shape of the owed call, and the turn after
the record follows what was written.

And one the repack exposed. The runner renders every tool result at a 6,000
character cap, pushed reads included, so `[code.area]` at 13,726 characters
reached the session as 5,900 of them and "TRUNCATED ... ask for the next
range" -- which a push has no range to ask for. No earlier push had been that
large, so nothing had said so. A pushed read is the wake; it renders at its
own cap (`PUSH_CHARS`, 20,000, a page above the pushes' own budgets) and the
wake keeps two thirds of the window when the transcript is trimmed, not half.

The Architect at 14B, with the area's parser in front of it and the brief
sharpened (anyone who must import an identifier from this repository is
inside, whatever you call them), moved its WHO BREAKS to the right party --
"users who define variables with specific types in their recipe frontmatters"
-- and kept pointing RENAME WHAT at the type names. Its pass over the finished
run wrote one real commitment (`TemplateVariableType enum values`, "users who
define variables in their notes using these exact strings 'text', 'number'")
among a dozen that named inside parties in words the guard did not know --
"the code inside PTPlugin.onload()", "the program's internal logic", "the
manifest.json file" -- and knows now. That is the reader's limit, not the
push's: the harness bounded every one of those sessions and none looped.

The rest of what the 14B taught the harness is small and was taken as it came:
a key written once per value (`citations="a"` / `citations="b"`) is that key's
list; `citations="a b c"` is three paths; a word glued to a label
(`glossary.amend:template_select_modal sense_body=...`) is the call's first
positional argument, which the sandbox binds; backticks around a name or a key
are stripped and a comma after the name is a label as a colon is; a row id
echoed as a term (`word#src`) is the word; a table under a label -- `term |
sense_body | sense_short` and a row per word, which is how llama3.1:8b wrote
one whole no-prose survey three sessions running -- is one call per row, the
header naming the keys. And one that was not a parse: a
survey turn wrote the same `glossary.amend(...)` line nineteen times to the
token cap -- 623 seconds at the partial-offload rate -- so the stream is
stopped at the third identical line, and the connection's close stops the
generation.

And one finding about the front that every reader agreed on: "users configure
intents in a YAML schema file". The schema was prominent and labelled as what a
user writes; the README sentence that says otherwise -- "a recipe is just text
kept at the start of a note in a special place called the Frontmatter" -- was
one paragraph above the example the front already carried. The front now
carries the first example *with* the paragraph before it and the sentence after.

`.rota/live.md` is the present tense of a run: every model call overwrites it
with the prompts and the completion as it streams. The `turns` table stays the
record.

## The state at the end of the day

`cnt_ad` — llama3.1:8b on the complete harness (corrected front, sectioned
concordance with the declaring file, kept account, bounded guards, all three
call syntaxes, the identical-turn stop): **47 sessions, 5 minutes, nothing
abandoned, 8 of 10 required terms** (7 defined + `variable_type` named;
`frontmatter` and `global intent` both woken by the account and both right),
one trap hit (`text` "string of characters" -- with the right kind named
beside it), and the Architect found the plugin-id registry contract and the
filtered-opener dependency, thinly.

The understanding probe, read two ways: with the 8B as the reader of the
artefacts, 4 of 7 questions answered (the recipe's place, global against
local, template, provider); with the 14B reading the *same* artefacts, 5–6 of 7
-- the note prompt "a specific note in the vault", the rename's affected users
-- which says the artefacts now carry it and the 8B under-reads them. What the
artefacts still lack outright: the bridge from "prompt kind" to
`TemplateVariableType` (the five are listed under the enum, not under
`prompt`), and the schema-as-contract constraint at its full generality.

The honest summary of eleven runs: the design is sound and fast -- every phase
runs in order, every subject is discharged or reported, and a run is five
minutes -- and the quality of understanding now tracks the reader. The same
pipeline under the 14B is the last measurement of the day (`cnt_14b`).

## Code, schema and manifest alone

cnt's README is excellent, and by the end of the day the front leaned on it --
the introduction, and the first example with the sentence above it that says
where a recipe lives. A good README is an easy way to look like understanding,
and the next repository's README may not exist. So `prose_sources` is a
setting (`rota onboard X --root ... --no-prose`): off, the README, `docs/`,
CHANGELOG and their kind are withheld from every context the harness assembles
-- the front, the concordance, the area source -- and from `code.source`
itself, which answers that prose is off for this run. The files stay indexed;
they are only unread. With prose withheld the front is the code's own front:
manifest, schema, the entry point's head, the most depended-upon source file
whole, and -- added after the first no-prose run -- the code that reads what
the user writes: the importer of the schema, found by the edge, as a head
(`src/intents/frontmatter.ts`, `getFileCache(file).frontmatter`). Every
reader told the schema was "a reference the code imports, not the place the
user writes them" had still written "users write their intents in
intentsSchema.yaml": the label said where they do not, and nothing in front
of it said where they do.

The first no-prose run (`cnt_np`, llama3.1:8b, 46 sessions, 205 s) read the
program's shape right from code alone -- a user writes intents, a global
intents note is merged in, a list to choose from, the chosen one runs,
notices on error -- and its glossary put `note`, `folder`, `text`, `date`
under the right kind, listed the enum's members for `template variable type`
and `reserved variable name`, and defined `global intent`, which the prose
run had not. What it lost without the README was the one sentence the README
supplies: where a recipe lives. Probed, the 14B reader answered `provider`
and the global-intent difference, named "an intent note file" as where the
user writes, and did not answer "which five kinds of prompt" -- because
without the README, `prompt` is this plugin's modal class and the five kinds
are *variable types*, which the glossary lists. The probe now also asks that
question in the code's words; the README-worded one stays.

Run again on the front with the schema's reader in it: the account says "a
user writes a frontmatter in a note with keys that match the schema in
intentsSchema.yaml; the program reads this frontmatter and turns it into an
array of Intent objects" -- from code alone. Scored, 7 of 10 required named
(`frontmatter` defined now, `global intent` not this time: the reader is
llama3.1:8b and the account varies), one trap. Probed: the 14B reader answers
the rename-a-key question from code alone ("the frontmatter keys in their
notes no longer match the schema"), lists four of the five variable kinds
asked in the code's words, and `provider`; it still says "the notes do not
say" to *which key* a recipe is written under (`intents_to` is in the schema
and nobody defined it) and to the note prompt's mechanics, which live in
`providers/note.ts` and the README. That is what a good README is worth here:
one key name and one mechanism, not the shape of the program.

The 14B on the same code-only front (`cnt_np14`: 40 sessions, 33 minutes,
nothing quarantined, no collisions) wrote the account "users write the
configuration in YAML frontmatter within their notes or globally through
settings; the program reads these configurations, validates them against a
schema, provides an interface to select templates and prompts, creates a new
note", and the best glossary of any run: 8 of 10 required named (7 defined --
`frontmatter`, `selection` and `provider` among them), one trap, bodies that
say what kind of thing each word is and where it is declared. Probed from
code-only artefacts: the rename-a-key question answered by both readers
("users who write frontmatter configurations using `with_templates` ... no
longer match the expected schema"), `provider` by both, the five variable
kinds and their enum by the 8B reader and the enum's name and file by the
14B, `template` as "written by users in YAML frontmatter" by the 8B. Unanswered
by both: which key a recipe goes under, the note prompt's mechanics, the
global-intent difference -- two of those three are README facts, and the
third is `globalIntentsNotePath` in `main.ts`, which the define phase never
got a word for. The Architect from code alone named the right party for
`src/intents` ("users who write frontmatter configurations") on the types
whose fields are the frontmatter keys, and CI trivia and class names
elsewhere.

So: with the README withheld, the tool recovers the program's shape, its
vocabulary and the kinds of its things from code, schema and manifest, and
a reader of its artefacts answers the maintainer's questions about as well
as it does with the README in -- four of eight against three and a half of
seven. What the README adds is two facts a maintainer would otherwise have
to read `frontmatter.ts` and `providers/note.ts` for.

## Onboarding v1.0.0 -- the process, to build and validate

What follows is the onboarding process as the original design
(`rota_tui/team-graph.html`, "Before you start") has it, reconciled with what
the runs above taught, written as the specification we build and validate
against. Steps 1-4, 6 and 9 exist and are measured; the rest exists as
charters, modes and a story, and has never run as a sequence. "Validated" for
a step means: run on a real repository with real readers, its artefacts read,
its outcome the one named in the last column.

| # | step | actor | shown | writes, terminal act | state |
|---|---|---|---|---|---|
| 0 | open -- no state folder means onboard; the first exchange is recorded | machine, Liaison | -- | state folder, transcript | explicit `rota onboard` today |
| 1 | index -- paths, symbols and their kinds, import edges, fan-in, areas from directories checked by the graph, the lexicon; `.gitignore` respected; the trust-ranked extras the principal points at (tests, issue tracker, usage) | machine | the checkout | `code_index`, `code_edges`, `code_lexicon`, areas | built; **symbol kinds kept** (and TS enums indexed); routes/commands, tests-as-intent still missing |
| 2 | constraint zero, bound to every unsurveyed area, shrinking as surveys land | machine | areas | `k0` | built |
| 3a | orient **from code** -- manifest, schema, entry point, the schema's reader; prose withheld | Vision Keeper | `code.front`, no prose | account + behaviours, `observed`; attest `@program` | **built, the default** (`orient_prose=on` restores the old front) |
| 3b | prose reconciliation -- the README read *against* the account; each disagreement a ledger entry ("README says X; the code shows Y") the agenda puts to the principal | Vision Keeper | `problem.baseline` + `code.prose` | `ledger` rows; attest `@prose` (owed artefact: the ledger) | **built** (`reconcile`, between orient and define) |
| 4 | define -- one word per session, from the concordance | Terminologist | baseline + `code.concordance` | one `glossary.amend`, `observed` | built, measured |
| 5 | surfaces -- the authoring schema's keys and the commands, read as what a user can do | Vision Keeper (Vision), Terminologist | schema + the code that reads it; command registrations | items per capability; glossary rows for keys (lexicon keeps keys whole) | not built |
| 6 | survey, per area -- residue words | Terminologist | `code.area` (own files first, 10k) + glossary + baseline | amends; attest | built, measured |
| 7 | survey, per area -- the model: what the area is for, its flows, what is buildable, its commitments | Architect | `code.area` + `model.consult` | area account + flows (model table), constraints; attest | **account built** (`model.describe`, one row per area, read by the probe); flows still missing |
| 8 | outside facts -- what the code reaches for (plugin APIs, registries, standards) | Architect / Terminologist ask; Researcher answers | the question; the clause | `references_`; answers | designed; never invoked in onboarding |
| 9 | collisions -- two senses of one word | Terminologist | both readings + concordance | synthesis or `same` | built |
| 10 | cannot-determine -- each role reports what the code underdetermines | Vision Keeper (Vision), Terminologist, Architect | own artefact + the area | `msg.report_liaison` with refs | designed as a beat; not built for onboarding |
| 11 | harvest -- dedupe, order, at most two questions in the principal's language; plus the two onboarding-only questions: *what changes next*, and *the election* (confirm upfront for the named core, lazily elsewhere) | Liaison | the reports | `msg.present_principal` | `observed_entries` presents k0 on session one and then blocks itself; the election has no representation |
| 12 | the principal answers and elects; answers land as utterances, statements, verdicts | principal, Liaison | one page | transcript, statements, per-item verdicts | modes exist; never run over onboarding output |
| 13 | drafts absorb the answers; a challenged `observed` becomes the first decision; survey deepens where "what changes next" points | Vision Keeper (Vision), Terminologist, Architect | the delta | amended rows; `decisions` | pieces exist as L1 cases; no flow |
| 14 | baseline signoff -- one page, corrections, lgtm; approvals set | Liaison, Vision Keeper (Vision), principal | items + open assumptions | `approval` per item | modes exist; not sequenced |
| 15 | lazy periphery to the ledger | machine / Vision Keeper (Vision) | the election | `ledger` rows | not built |
| 16 | seam plan (optional) -- boundaries from fan-in and k0's residue, as structural items for signoff | Architect, Vision Keeper (Vision) | fan-in, k0 | proposal, items | not built |
| 17 | ready -- the frontier quiet; gauges: observed:decided, k0's shrink | machine | -- | -- | k0 shrink exists; ratio not surfaced; "done" today is quiescence, not signoff |
| 18 | stay true -- our changes through the shape team before the Developer; foreign commits re-survey; new grains regrow k0 | machine, shape team | diffs | re-survey wakes | not built |

### Two questions the table had to settle

**Code before prose, and an overview first -- both.** The overview has to
come first: every later question is asked with the previous answer in front of
it, and without an account the glossary defined `intent` as "an intention or
goal" and wrote it again after reading all three files. But the account comes
from *code*: the no-prose front produces "a user writes a frontmatter in a note
with keys that match the schema; the program reads it and turns it into Intent
objects", and the runs above measure that as good as the README-fed one on the
shape of the program. So 3a is the orient, and the README is read second,
against the account, as a check -- where they disagree, "the README is stale"
and "the code has a bug" are the two readings and only the principal can say
which. Prose is hearsay from absent authors; it becomes a test of what the code
said, not a source of what the program is.

**What the principal brings.** Not the code -- what the code cannot contain.
Once: pointers to what they trust more than comments (tests, tracker, usage).
Two onboarding-only answers: what changes next, and the election. Rulings on
what the code underdetermines -- dead or dormant, bug or feature, which sense
is canonical, README or code -- at most two questions a round, in their
language. One page of signoff, corrected and lgtm'd: effort scaled with the
ambiguity the code held, not its size. First decisions when they challenge an
`observed` entry. Not expected: to explain the code, read the index, write a
definition, or confirm rows one by one. Absent -- as in every run above --
onboarding still reaches a valid terminal state: everything `observed`, the
election lazy everywhere, the questions held for the first conversation.

### Decisions still open

- The terminal state: quiescence (today) or the signed-off baseline (the
  design). v1.0.0 takes the design's answer and treats "presented, awaiting"
  as the valid state when the principal is absent.
- The cannot-determine artefact: a report message with refs (the charters'
  answer) versus rows on the survey record. v1.0.0: the report, because the
  harvest already reads reports.
- The model table for "what the area is for, its flows, what is buildable":
  new rows under the Architect's artefact, or the account kept on the survey
  record. v1.0.0: under the model, with grain refs, because the doc's model is
  "constraints, and what is buildable here".
- The election's representation and how it gates survey depth per area.
- Baseline-to-code refs on observed items, so they can be checked and
  invalidated; and the re-survey trigger (per-grain hash).
- The name of the scope role: the original is **Vision**, which says identity
  and purpose as well as the gate; "Vision Keeper" says only the gate. A rename
  touches the graph, predicates, prompts, cases and cassettes, so it is done
  first or not at all.

### Validation run 1, measured (llama3.1:8b, 2026-08-23)

`cnt_v1`: the full v1.0.0 spine -- code-only orient, reconcile, the keys in
the define queue, `model.describe` -- 46+33 sessions, nothing quarantined.
Scorer: 8 of 10 required named, **zero trap hits** (first run without one),
five constraints, and the glossary holds all 33 authoring keys with real
bodies (`with_templates` "an array of template objects used to create notes",
`of_type` "classifies the type of variable", `replaces_selection_with` "a
string used to replace the selected text"). Probed: **~6.5 of 8 with the 14B
reader** against 3.5 of 7 for every pre-v1.0.0 run -- "where does a user
write a recipe" answered from the code-only account, and the global-vs-local
intent difference answered for the first time in any run ("a global intent is
specified in a note path defined in the settings; one read from the active
note is local"). The 8B reader reaches 4 of 8 and now lists all five variable
kinds. Two findings: the keys initially lost to the `define_terms` cap on a
real repository (the closed vocabulary is now always pending; the cap bounds
only the open one), and reconcile's mechanics survived contact while llama's
*content* there was junk -- it "disagreed" its own items with each other. The
14B run read the README against its account and attested `none_found`, which
for cnt is the right answer.

### Validation run 1, measured (llama3.1:8b, 2026-08-23)

`cnt_v1`: the full v1.0.0 spine -- code-only orient, reconcile, the keys in
the define queue, `model.describe` -- 46+33 sessions, nothing quarantined.
Scorer: 8 of 10 required named, **zero trap hits** (first run without one),
five constraints, and the glossary holds all 33 authoring keys with real
bodies (`with_templates` "an array of template objects used to create notes",
`of_type` "classifies the type of variable", `replaces_selection_with` "a
string used to replace the selected text"). Probed: **~6.5 of 8 with the 14B
reader** against 3.5 of 7 for every pre-v1.0.0 run -- "where does a user
write a recipe" answered from the code-only account, and the global-vs-local
intent difference answered for the first time in any run ("a global intent is
specified in a note path defined in the settings; one read from the active
note is local"). The 8B reader reaches 4 of 8 and now lists all five variable
kinds. Two findings: the keys initially lost to the `define_terms` cap on a
real repository (the closed vocabulary is now always pending; the cap bounds
only the open one), and reconcile's mechanics survived contact while llama's
*content* there was junk -- it "disagreed" its own items with each other. The
14B run read the README against its account and attested `none_found`, which
for cnt is the right answer.

### Validation, in order

1. **Zero to onboarded** (1-9, 17): on cnt and on a second repository of a
   different shape, with prose withheld; every grain surveyed or under k0; the
   gauges read; the artefacts read by a person.
2. **Probe via the Liaison** (consult mode over 1-9): the maintainer's
   questions asked as read-only inquiries; owners answer from artefacts, drill
   to source when they cannot, and write back; "cannot determine" becomes a
   report. The hand-run probe above is the shape of this; the system runs it.
3. **Harvest, election, signoff** (10-15): with a principal present -- a
   scripted one first, a person second -- the questions arrive deduped and
   ordered, the election lands, the page is signed, `observed` becomes decided
   where they said so and ledger where they deferred.
4. **Stay true** (18): a commit to a surveyed file regrows what it invalidated.

Each of the four is a multi-role sequence; none is validated by its parts
passing. The first is the one the runs above are the start of.

### Validation 2's first hop, and why the route had never carried a message

The read-only route was complete on paper and had never run. It is drawn three
times in the graph (`liaison -> vision_keeper | terminologist | architect: ask`,
with `answer` back), each owner has an `ask` brief and an `ask.tools` file, the
mode exists in `sandbox.build`, and `probes/consult.py` measured the idea and
beat the monolithic dump 4-8 to 2-8. Driven through the real loop against the
click run on `qwen3:8b` -- one maintainer question, `python -m rota` intake,
nothing hand-fed -- Liaison replied to the principal asking them to clarify the
question, and the system went quiescent.

**Twelve faults, each of which hid the next**, in a route that was designed,
briefed at both ends, drawn three times in the graph and measured by a probe.
They are grouped below by where they sat -- the mode, the ask, the ladder, the
intake -- rather than by the order they were found, because the order they were
found is simply the order each one stopped concealing the one behind it.

Four of them are one shape: a hand-written `.tools` file or brief that had
fallen behind the graph, with nothing to notice. Three more are the other
shape, and it is the one worth remembering -- **the failure and the success
produce the same observable output.** An owner answering from an empty inbox
still sends a well-formed `answer`. A session whose writes were discarded still
reports `committed = 1`. Only the per-turn transcript distinguishes them, which
is why the route had to be *run* before any of them appeared. Once run, a check
written against one of them found two more by itself -- the rung-capability
lint caught Architect and Vision Keeper before either was reached. That is the
argument for writing the check at the moment the fault is understood rather
than after the fix: the second instance is free, and there is almost always a
second instance.

**The mode was never reachable.** `loop.run` calls `run_session` without a
mode, and the default was `"normal"`, so no session this system ever dispatched
was read-only. Law 10's guarantee -- the writers are not built, so there is
nothing to resist -- held only in the six tests that passed the mode by hand.
It looked fine because the three `ask.tools` files narrow to reads anyway,
which is the law being kept by three hand-maintained lists agreeing with it.
Derived from the wake now, beside the `provenance` derivation that already
works that way.

**Every ask was empty.** The channel takes refs and nothing else, so on this
route the refs *are* the question: the resolver expands the entry id into
`principal_said`, and that is the whole of how the principal's words reach the
owner. Measured on `llama3.1:8b`, four asks out of four carried `refs=[]`, in
both passes -- because the only worked example of the route in the system was
`msg.ask_terminologist(refs=[], question='...')`, which is refused for the
argument and, corrected the obvious way, sends the empty one. An owner woken
with an empty working set answers from nothing and looks, afterwards, exactly
like one that worked.

Refused at the channel rather than explained again. That is what
`l1_unresolved.yaml` predicted after prose failed to arbitrate refs six times:
"the fix will be structural -- a channel whose refs the sandbox will not let go
empty". It is satisfiable, which is the test a refusal has to pass here:
`entry_id` is in the session's own prompt and the message names it. Measured
across the guard: inquiry went **0 of 4 to 4 of 4** on the same brief, both
models, both passes.

**And the refs did not resolve, so the owner answered from memory.** The guard
above makes an ask carry the entry id; nothing followed it. `_resolve_refs`
turns a message's refs into the rows they name and its table list had no
`entries` row, because entries had only ever been reached through `entry_for`,
which looks up `e_{waking message id}` -- true on the intake hop, where Liaison
is woken by the message the entry belongs to, and false on every hop after it.

What that looked like on the live click run, with everything above already
fixed: Liaison routed the question, Architect woke with `refs: ["e_m5"]` and no
question in front of it, and answered with a description of a three-layer
architecture -- data, business logic, interface -- that click does not have.
Answering from memory is what a role does when handed nothing, and it is the
third fault in this route that is invisible from the outside: a well-formed
`answer` message comes back either way.

The L3 chain case passed straight through it, and the reason is worth keeping.
It asserted that Terminologist sent an answer, not that the answer named
anything. It now requires the answer's refs to include the glossary rows the
question is about, which is the difference between "it replied" and "it replied
from somewhere". Its first fixture also gave the ask message and the entry the
same id, which made `entry_for` match by accident; they are deliberately
unequal now.

**And the ladder that was supposed to catch a non-answer had never run.**
`schedule.reask` -- the register's one declared transition, "the answer came
back and left you where you were" -- is offered to Architect, Developer,
Terminologist, Tester and Vision Keeper. Not to Liaison, which is the one role
that talks to the principal, so the only asker whose block costs a person's
attention was the only asker that could not report one. The graph edge did not
exist.

Giving it the edge exposed three more, each pre-existing and each invisible
until a question actually travelled three hops:

- `schedule.reask` refused any wake whose cause was not a `question`. Liaison
  asks with `ask`. Written when Developer was the only asker, in the same shape
  as every other "names one instance" fault in this route.
- **a reply started a new thread instead of joining its cause's.**
  `thread_id = m.thread_id or m.cause_id or m.id` is right exactly one hop from
  the root -- the first reply's cause *is* the thread root -- and wrong at every
  hop after, where it names its parent and starts a thread of one. So
  `unresolved` looked for who had spoken in the ask's thread, found nobody, and
  woke the role that had just answered. Three times, then quarantine. Everything
  keyed on `thread_id` read the same way: `report_is_settled`, `round_close`'s
  harvest, `open_tips`' broadcast exclusion.
- the rungs' briefs and `.tools` files named one asker each --
  `msg.answer_developer`, because Developer was the only asker when they were
  written. A rung woken for a Liaison question could not reply to it, which is
  the silence `predicates.unresolved` explicitly says it avoids by reading
  reply-capability off the graph. It reads the graph and then hands the wake to
  a mode narrowed by hand. `test_an_unresolved_rung_can_answer_every_asker_that_
  reaches_it` derives it now.

Two more surfaced once the ladder actually moved, and they are the same fault
as the ask's refs, one layer along. A rung is woken by a *tick* carrying the
question in `refs`, and `resolve_inbound` returned `{}` for any wake without a
`message_id` -- so the rung saw a message id and nothing else: no question, no
resolved rows. Terminologist and Vision Keeper each answered with
`refs: ["m6"]`, the id of the question itself, because it was the only thing in
front of them. And nothing linked that answer back to the question, so
`schedule.reask` refused and the asker could not report that the second answer
missed either. `trigger_message` is now the one definition of what a session is
replying to, used by the prompt and by the outbound cause, so the two cannot
disagree.

With those in, the ladder completes: Architect, then Terminologist, then Vision
Keeper, each once, and quiescent -- against three identical answers and a
quarantine before.

What the rungs then answered was still hollow. Shown the question at last, they
read their artefacts properly -- three glossary lookups deep -- and replied
citing the *question*, which is the same nothing as citing the message. An
answer to Liaison has to name a row, because Liaison relays to the principal and
the principal has never seen one they cannot resolve; the channel already
refuses a message id for that reason, so a hollow answer hands Liaison something
it is forbidden to pass on.

The bound on that rule was found by measuring the wider version, and it is the
clearest example this session produced of a guard being too strict. Held to
citing a source on *every* channel, Vision Keeper spent all twelve turns of
`L1-VK-the-last-rung-rules-or-sends-it-up` re-reading its artefacts and
re-sending an empty answer, five runs out of five, committing nothing at all.
The rule was satisfiable -- the item id was in front of it -- and it did not
satisfy it, which is the whole of what law 4 means by a gate becoming a loop.
Narrowed to the channel that reaches a person, both directions hold.

And then the same guard produced the same failure again, one route along, for a
reason worth stating separately: **it was unsatisfiable in `ask` mode.**
`architect/ask.tools` offered `msg.answer_liaison` and no report, so an owner
asked about an unsurveyed area could neither cite a source nor say it had none.
It reached for `answer` four times, was refused four times, and the thread died
with the principal still waiting -- a worse outcome than the hollow answer the
guard exists to stop.

This route's description has said the missing half from the beginning: "owners
answer from artefacts, drill to source when they cannot, and write back;
**'cannot determine' becomes a report**." The report channel was in the graph
and in no `ask.tools` file. A guard is only fair when the escape it assumes is
actually built, and
`test_a_mode_that_answers_liaison_can_also_say_it_cannot` now derives that
rather than trusting four hand-written lists to agree with it -- the fourth
time in this route that a hand-maintained list fell behind the graph and the
failure was silent.

Opening the escape then needed somewhere for it to go. `liaison/report.md` was
written when the only reports in the system came from an exhausted escalation
ladder -- it opens "a role has run out of rungs ... everyone below has already
looked, and the only step left is a person" -- and on this route nobody below
has looked, because the other two owners have not been asked. So a report
answering an `ask` marks that ask unresolved and the ladder carries it, rather
than tipping Liaison into a mode that believes the ladder is spent. It is the
`schedule.reask` declaration derived, for the same reason the constraint-zero
case was derivable: in general only the asker knows an answer did not land, and
here the *answerer* said so, in a verb that means it.

That write has to be the last one in the commit, which is the point rather than
an ordering detail. Two earlier writes mark a question settled -- the sweep, for
somebody new speaking in the thread, and the trigger line, for the session
committing at all. A report saying "not mine" trips both and contradicts both.

And the ladder needed an end. `unresolved` skips the asker, which is right for
every role -- the asker is blocked and cannot answer itself. Liaison is the
exception the rule was never asked about: it is the asker *and* the only way
back to the person who asked, so a principal's question that no owner could
answer stopped in silence, which from their side is indistinguishable from the
system losing it. `liaison/unresolved.md` already said the right thing for that
wake and had no way to be reached for it: "every role that could have taken it
next has already spoken in this thread ... this is the strongest kind of
question you can put to the principal".

And the branch itself did not arbitrate. `liaison/answer.md` gained a paragraph
saying to reask rather than relay when an owner cites constraint zero; both
models relayed anyway, both passes, four times out of four. Eighth time. The
structural form -- refusing to relay an answer that names nothing but the
question and `k0` -- takes it to 2/2 on both models in both passes. `k0` is why
it can be structural at all: in general "the answer did not land" is invisible
to a query, and on this one route the owner says it by citing a row with a
fixed id that means "not surveyed".

**And with all of it working, the route answered worse than the probe it
replaces.** That is the measurement that matters and it had never been taken:
the same eight maintainer questions, the same answer key, through the wired
system instead of through `probes/consult.py`. The probe scores 4 of 8 strict.
The route scored none, two of the eight reaching the principal with nothing at
all and two with confident wrong answers -- on the rename question it replied
"the build passing indicates the change is compatible", which is the exact trap
the question exists to set.

One cause was in the push and is fixed. `push_working_set` offers every read
that is *callable with no arguments*, which is the right rule and left
`glossary.lookup` invoked with an empty term: the session arrived holding an
index of one-line senses and the full sense of nothing. The probe does the
opposite and says so in its own docstring -- "the index of short senses whole,
and full bodies only for the terms the question's words name --
`glossary.lookup`, mechanically" -- and that is the same rule as `area` for a
survey. The subject belongs to the wake, not to the role, so the system
supplies it rather than asking a cold session to think of it. Re-measured: one
near-hit and three partials against none, and silence down from two to one.

Three more followed, each measured on the same eight before the next was made.

    change                                       hits  partials  silent
    (as wired)                                     0       0        2
    glossary bodies the question names             0       3        1
    fan-out to every owner, and a drain            0       2        0
    ref resolution carries the body                1       2        0
    three answers compose into one reply           1       4        0

The composition row is the design's own sentence -- "three answers compose
into one reply" -- built at last on the broadcast round's pattern: answers to a
fan-out are harvested, not raced, and one session holds the whole round with
every body resolved. It recovered the rename trap's crux through the full route
for the first time ("the system silently fails for invalid frontmatter"), and
the hedging that two guards failed to forbid stopped by itself once the
session had enough to answer with.

The first hit arrived with the body row, and it is the whole key verbatim:
asked which kinds of template variable an intent can declare and where the set
is declared, the reply named the five kinds and the enum's file. What had been
stopping it was that `_resolve_refs` carried `sense_short` and not
`sense_body` -- the owner read the full sense, refed the term, and Liaison,
which writes the words the principal reads, was handed one line.

A fourth change was made by the same argument and reverted. `model.consult` /
`model.load` is the same index-and-body split as the glossary's, so pushing the
constraint bodies the question names should have helped identically. It moved
the score not at all and cost the rename question the one thing it had gained.
`DECISIONS.md` carries the table and the narrower rule it leaves: a session
starved of the thing it is asked about answers from nothing, and a session
given more of what it already had answers from the extra.

**The fan-out was the second, and it is fixed.** Every one of the eight
questions went to exactly one owner. The story this route comes from says
Liaison "opens readonly sessions" -- plural -- and "three answers compose into
one reply"; the shipped brief says "ask every owner that might hold part of the
answer"; and the case's own notes say "which owner holds the answer is not
Liaison's to know". A role cannot be asked to know that and not to act on it,
so the choice is gone: one `msg.ask_*` call stages the ask to every owner. All
three, on seven of the eight.

**What remains is the relay.** It summarises rather than passes through, and
it drifts into conversation with the owner in the principal's channel: "Thank
you for the detailed explanation. To clarify ... Is there anything else you'd
like to know?", and on one question a request back to the principal to confirm
something the *owner* had been unsure of. The cause is known and the fix is
not free -- the answer channel carries refs and no words, so Liaison is writing
prose from resolved rows rather than relaying anybody's sentences, and the
channel that carries its words to the principal is `converse`, whose field is
named `reply`. The parameter name has won three times in this project already.

**And one question in eight is never routed at all** -- "An intent declares a
prompt with `of_type: note`. When the intent runs, what is the user asked for?"
is answered by Liaison from its own head, which is the ordered test missing a
question that does not look like one.

**Intake had two branches and needed three.** `converse.md` asked "is this chat
or work?" and settled ties twice -- "Default to chat", "When in doubt, chat" --
so a question about the onboarded program, which is neither, fell to the
tiebreaker. So did everything else: `chat` was the answer to five of six
fixtures. Replaced by an ordered test, three questions asked in order, stopping
at the first yes. See the intake entry in `DECISIONS.md` for the arms; the
short version is that naming the third branch in prose moved almost nothing and
replacing the tiebreaker moved all of it.

**And the session could answer twice, with the right answer losing.** Chat and
ratification were already declared mutually exclusive, enforced at commit by
dropping the segmentation when a chat reply was also sent -- right about the
outcome, backwards about the casualty. Read whole, `llama3.1:8b` segmented
"morning. we need SSO, but only if it works with our LDAP" correctly on turn
one, confirmed it on turn four, emitted one stray `msg.converse_principal` on
turn five after the harness had told it its work was done, and committed a
session with an empty `statements` table. `L1-LI-segment` has been 0/5 against
exactly that, and its own diagnosis -- "a brief that can only be tuned in one
direction gets tuned until the other direction breaks" -- was right about the
cause and one layer above the mechanism.

Which call loses is not a judgement call: across 42 recorded sessions that gave
two answers, the first was the right one in **all 42** and the second arrived
on a wind-down turn. So the first answer stands and the second is refused,
where a refusal costs a turn instead of a session's work.

It is one rule rather than three, and that was not the first attempt. Guarding
the pairs one at a time -- chat against ratification, then segmenting against
routing -- left routing against chat uncovered, and the new inquiry case failed
0/5 on exactly it: Liaison routed the question to its owners *and* chatted
about it, five runs out of five. `api.refuse_second_answer` names the three
answers once and each channel declares which one it is.

## The boundaries phase (added after validation 2)

The severity read of validation 2 found the one class of fact both
measurements missed from opposite sides: consequences of change. The
constraints artefact held ten identifier-headlined rows ("choseIntent",
"PTPlugin") and zero of the answer key's two required commitments, and the
consult probe's rename question ("who breaks, and how do they find out?")
got "not mine" from every owner. The survey brief already forbade
symbol-grain constraints -- the failure was what stood in front of the
session: an area's source foregrounds identifiers, and the boundary (the
schema a user writes against, the manifest a registry reads) was never
anyone's subject.

So onboarding gained a fifth phase, after survey: `boundary_subjects`
enumerates the authoring surfaces (data files the code imports) and root
manifests mechanically from the index; one Architect session per file,
pushed `code.boundary` -- the file whole, plus every file that reads it --
under a brief that asks outside-in: who is on the other side, what do they
rely on, and when they make a mistake, find the branch that rejects it --
and if there is none, the failure is silence, and silence is the finding.
`none_found` stays free and honest for build furniture. The constraints are
written last, with the whole model in front of them, which is where a
commitment can actually be seen.

## Onboarding v2.0.0 -- the design, to build

v1.0.0 was a one-pass pipeline over a heuristic frame, whose artefacts stood
because they were written. Three validated repositories and one week of
severity reads broke that contract in three places at once: the frame is a
judgement (measured: a 14B judge scores 34/38 on six repositories including
two shapes every heuristic fails -- probes/partition_judge.py); the pipeline
must loop (an account written cold is a draft, and early errors seed every
later phase); and standing must be earned (sessions satisfy "found" with
stamps, because generating plausible text costs a model nothing). v2 wraps
the v1 spine -- unchanged phases, briefs and guards -- in revision machinery.

The governing rule, from the logical-failure review: **every cut circle gets
a revision path, and every artefact gets a falsification path.** A claim
climbs: exists -> drafted -> checked -> challenged -> ruled -> standing but
revisable. No claim skips a rung.

The stages, in order:

1.  **Index** (mechanical, exists). Trusted for existence claims only.
2.  **Frame** (new). Code claims the root manifests (the name-list is
    reliable exactly there); a judge session classifies the rest of the tree
    -- program / attached / ignore / boundary -- from the top-level stats,
    the README's first lines, and the entry point's imports (the fzf lesson:
    a README of badges misleads a judge that cannot see what main imports).
    The proposal is diffed against the heuristic prior; every disagreement
    and gray call becomes a ledger entry with a stated default. Defaults pin
    immediately; nothing waits. Rulings re-pin, and a re-pin re-earns what
    stood on the old frame.
3.  **Orient** (exists) -- explicitly a draft.
4.  **Reconcile** (reframed): a README claim the account cannot confirm is
    recorded as "the account did not see this" -- never "the code shows no
    such thing" -- and triggers a code look or a ruling. The prose's names
    are nominated for the glossary (v1.1 mechanism; a nominating session
    may replace the markdown-emphasis heuristics later, heuristics as prior).
5.  **Define** (exists). Collisions repair context-dependence after the fact.
6.  **Survey** (exists), over program areas only -- the frame guarantees it.
7.  **Re-orient** (new): one session, the draft account re-read with the full
    glossary and model in hand. The first draft stops being the final draft.
    Runs before boundaries so the most consequence-laden sessions get the
    revised account.
8.  **Boundaries** (exists, extended): each subject is typed -- authoring
    surface / manifest / export surface -- and the session's first recorded
    act declares who is on the other side. The declaration gates the
    inside-party guard (a library's importers are outside) and later feeds
    consult routing. Declarations are per-file: no repo-global shape.
9.  **Challenge** (new). `challenge = off | sample | full` in config, default
    sample: the load-bearing artefacts (constraints, the account, a sample
    of senses). A challenge session succeeds only by citation -- a line of
    source the claim cannot survive. **Models never adjudicate models**:
    authority attaches to evidence and rulings, never to which model spoke.
    A successful challenge supersedes the artefact AND re-wakes its writer
    -- a flag nobody drains is the quarantine-counter mistake again. Both
    readings surviving with evidence = contested, for the principal.
10. **Blind spots** (new): a session writes what this run structurally could
    not see -- unparsed formats, quarantined areas, dilution -- to the
    ledger. How tripwires are discovered rather than hand-written.
11. **Agenda** (exists): partition calls, prose disagreements, collisions,
    contested artefacts, blind spots. Rulings are decisions; decisions pin.
12. **Verification** (local only -- standing decision: no non-local models).
    Preregistered keys written before the run and checked against source;
    the consult probe; cross-family reading (different local models find
    different lines -- search diversity, never a trust hierarchy).
13. **Standing revision** (planned): own commits through the team; foreign
    commits re-survey; survey findings reopen frame rulings the moment they
    are found, not at a scheduled stage; rulings naming dead paths surface
    as tripwires.

### Stage 2, as built (2026-08-24)

The deterministic half first: `frame_rulings` (id, kind, provenance) with
the partition consulting it -- most specific prefix wins, decided outranks
observed, unruled paths keep the heuristics' answer -- and `repin()`
re-deriving partition, lexicon and constraint zero over the ruled table.
Then the session: `tick:frame` wakes the Architect first, pushed
`code.tree` and `frame.load`, writing through `frame.assign`, diffs to the
ledger mechanically.

Two measured lessons in the first live runs. The judge classified click's
tree correctly in its first turn at both model sizes -- and never attested,
re-sending the batch until the identical-turn rule ended the session,
llama 0/5 at recording. The cure was already the house philosophy: the
record follows what the session did, so a frame session that ends with
rulings staged and no record has its attest derived, citations taken from
the first indexed file each ruled prefix covers. And root dot-files left
`code.tree`: .editorconfig received a classification, which changes
nothing and costs the attention the ending needed.

### Stages 7, 9 and 10, as built (2026-08-24)

**Re-orient**: tick:reorient between survey and boundaries, Vision Keeper,
pushed its own baseline plus glossary.consult and model.consult; items are
revised by re-asserting their ids. Live on the finished cnt run: five of
six items revised with the vocabulary in hand, honest attest, one session.
Skipped when there is no glossary to revise with.

**Challenge**: tick:challenge, Critic, one session per load-bearing claim
(`challenge = off | sample | full`; sample is constraints and items, newest
first, capped at twelve). challenge.load shows the claim with its cited
sources opened; uphold is cheap on purpose; break demands a citation the
session opened and the quoted line, or it is refused -- models never
adjudicate models. A falsified claim goes to the ledger; standing changes
only by ruling, so Law 1 holds. The spec's "supersedes the artefact and
re-wakes its writer" is deferred to the ruling: as built, the drain is the
agenda.

**Blind spots**: tick:blindspot, Liaison, last; code.gaps recomputes the
run's limits from its record and the session writes the two or three that
could be hiding something to the ledger. The Researcher keeps its
woken-by-nothing property; the relay role relays.

**Challenge calibration, closed (2026-08-25):** the planted falsehood is
falsified -- after three measured design turns. The free-door uphold
rubber-stamped it; the symmetric gate left it unverdictable (a claim false
by absence has no defeating line, and the model re-sent an empty quote
into the gate for twelve turns); once-then-flagged converted the reading
into the verdict, evidence gap stated on the row. Final table on cnt:
eleven real claims stand, each with its supporting line; the plant
falsified; zero false breaks. The vacuous tautologies stand-with-a-line
rather than unfounded -- the third verdict is built and tested, and
whether a model reaches for it is now a bench fixture.

**The verdict ladder, reviewed against click (2026-08-25):** the
challenge pass made its first production catches and the review of
all twelve says the evidence gate held and the ladder did not. Every
citation was a real file and every quote a real line. But eleven of
the twelve sampled claims were one template -- "WHO BREAKS:
applications using click.X; WHAT HAPPENS: a NameError if X is not
found" -- a conditional true of every name in every program, and the
identical shape drew seven falsified and four stands, with
self-contradictory reasons on both sides. That is a coin flip wearing
citations. Three things follow, in order of how far upstream they
sit: the constraint over-production is the root cause (thirty-one
symbol-grain rows gave the Critic nothing worth judging); the
vacuity arm of the brief must name that exact shape; and the
operation was renamed, because `unfounded` was an operation and a
state at once where its siblings are not (uphold -> stands,
break -> falsified).

**Which name, measured (2026-08-26):** the rename was first made to
`challenge.dismiss` on the law alone, and the law alone was not
enough. Same four fixtures, same models, one word changed in the
brief and nothing else:

    operation             llama3.1:8b   qwen3:8b
    challenge.unfounded      1-3/4         3/4
    challenge.dismiss        0/4           2/4
    challenge.vacuous        3/4           3/4

`dismiss` was worst for both models in every run -- llama lost the
whole ladder to it, upholding the plant and breaking the honest
claim. The reason is not that `unfounded` matched its own verdict
state: `vacuous` does not match either, and scores like it. What
separates them is that `break`, `uphold` and `vacuous` all name what
is true of the *claim*, while `dismiss` names what the Critic does
to it. An operation renamed off a collision has to keep naming the
finding, not the gesture -- and `vacuous` was the only one of the
three that scored the same under every load, which is the second
reason it is the one shipped.

Validation plan: the challenge on/off twin (same repo, challenge off and
sample -- the score diff is the measured value of the pass), the v1 baseline
(v2 scores are not comparable to v1 scores by design; the twins bridge
them), and the fifth-repository rule: every new mechanism's validation set
must contain a shape chosen to break it, because the judgement layer's
input space is repo shapes and three similar repositories prove nothing.
