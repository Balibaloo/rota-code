# What rota assumes about a codebase

Onboarding was built and validated against one repository — an Obsidian plugin
in TypeScript, forty-odd files, one README, a yaml authoring surface. Every
mechanism that works carries assumptions calibrated there, and the honest
posture is to know which are *design* (they'd be kept on any repository, and are
written down here so nobody re-litigates them), which are *tripwires* (they hold
until a differently-shaped repository trips them, and each has a tell), and
which are *debts* (known to need a system, not yet built).

A second repository is the instrument for this list: each entry names what a
run against it would confirm or break. When one trips, the fix goes in the code
and the entry moves sections — this file records the current shape of the bet,
not a permanent truth.

## Laws — assumed by design, kept on purpose

**Authored means tracked.** The index holds what `git ls-files` answers for,
minus generated names and minified shapes; without git, everything that is not
obviously machine-made ([indexer.py](../rota/onboarding/indexer.py) `walk`).
Asking git rather than re-implementing ignore rules is the design; a tracked
file that matches an ignore rule stays, because somebody committed it on
purpose.

**Text that does not parse is still part of the project.** A file with no
parser arrives as a path-kind grain — findable, openable, citable — and only a
UTF-8 decode failure excludes it as "not authored text". This was learned the
hard way: the schema, the README and both registry manifests of the first
repository were invisible until the walk stopped equating "has a tree-sitter
grammar" with "is part of the project".

**Directories are the partition.** An area is a directory somebody already
chose, checked against the import graph and folded into its parent below three
files; tests and examples never form areas of their own — they are attached to
the area they exercise ([areas.py](../rota/onboarding/areas.py)). Inventing a
partition from import clustering would file every later decision somewhere
nobody would look. Both exclusions were measured, not guessed: six of
icalendar's fourteen proposed areas were `tests/*`, and ten of click's sixteen
were `examples/*` demo apps — with every one of the run's eleven "leaky" areas
among them.

**Structure names the vocabulary; frequency never does.** A word enters the
lexicon from a directory, file, declared type, authoring key or surface — never
from being said often ([lexicon.py](../rota/onboarding/lexicon.py)
`STRUCTURAL`). Frequency-ranked word lists were three quarters
`getter`/`parser` noise every time it was tried.

**The prose is a check, not a source — and its vocabulary is data.** The
account of the program is written from code alone; the README is then read
*against* it, disagreements go to the ledger for the principal
(reconcile), and the README's own names for things — frequent, emphasised,
absent from the code's vocabulary — are nominated into the define queue so the
glossary can hold "the README's word for X" (`prose_names` in lexicon.py).
Claims are hearsay; names are facts about the prose itself.

**Kinds are declared.** What a thing can be one of is read from enums, union
types and option strings in the authoring surface — the concordance leads with
"declared as a kind" because that is the line that settles a word, measured
three runs out of three.

## Tripwires — hold for now, each with a tell

`rota onboard` prints the mechanical ones against each checkout, so a new
repository announces which of these it stresses before any session runs.

**Seven languages parse; the rest are path-only.** Python, JS, TS, Go, Rust,
Java, Ruby ([languages.py](../rota/onboarding/languages.py)). A Swift or Kotlin
repository would index as paths with no symbols, no edges, no declared
vocabulary — onboarding would run and understand almost nothing, quietly.
*Tell:* the onboard report's language mix; three or more unparsed files sharing
a code-like suffix is called out.

**The import statement is the dependency graph.** Edges come from resolvable
import/use/require statements. Frameworks that wire by convention — decorators
into a registry, file-based routing, dependency injection — under-report
coupling, so fan-in under-ranks the actual load-bearing files. *Tell:* a
surveyed area whose account keeps naming files the graph says nobody imports.

**Identifiers decompose into English.** `parts`/`singular` assume camel/snake
case and English plurals. Abbreviation-heavy or non-English naming starves the
lexicon and misfamilies words. *Tell:* a lexicon whose top words are two-letter
fragments.

**The authoring keys are few enough to owe them all.** Every key-source word is
always pending (34 on the first repository). A config-schema-heavy project with
hundreds of keys would owe hundreds of define sessions. *Tell:* the onboard
report counts keys and warns past sixty.

**The README is one file, at the root, in Markdown, in English.** Reconcile
reads exactly that file; the prose-name harvest reads its headings, bold and
quotes; the function-word list is English. A `docs/` site, an rst README, or a
non-English one contributes nothing (claims *or* names). *Tell:* onboard warns
when no root README is indexed, and warns when `docs/` holds ten or more prose
files — measured on click, whose README is a page of marketing (the harvest
correctly nominated nothing: its vocabulary is the code's) while 37 files of
real prose sit in `docs/` where reconcile never looks.

**There is an authoring surface.** The strongest vocabulary signal (weight 4.0)
is keys a user writes in yaml/toml — and the loudest concordance section is
"in what a user writes". A library has neither: click's users author *code*
(decorators), its key count is zero, and every product meaning rests on
declarations alone. Holds as graceful degradation, but the consult questions a
maintainer asks about a library are phrased in API vocabulary, and nothing has
measured whether the glossary built without a surface answers them. *Tell:*
zero key-source lexicon words at onboard time.

**One repository is one program.** The orientation writes one account
(`@program`); a monorepo would get one account for three products. *Tell:*
onboard warns when the partition proposes a single area for a large tree, and a
monorepo shows the opposite — top-level areas that share no edges.

**Budgets are calibrated at forty files.** Push caps (10k area, 20k push),
`define_terms`, session counts per phase — all tuned where a whole area fits in
one window. A three-hundred-file repository multiplies sessions linearly
(fine) but also grows each area (not fine past the cap: heads-only views).
*Tell:* `code.area` falling back to heads for most files of an area.

**The executor is a local 8B/14B at temperature 0.** Briefs are tuned to that
attention span — prompts past ~12k characters collapse discipline, knife-edge
cases see-saw on a byte. This is an assumption about the runner, not the
repository, but every brief carries it. *Tell:* the L1/L3 suite, which is the
recorded form of exactly this bet.

## Debts — known to need a system

**Comments and docstrings are invisible.** The concordance skips comment lines
on purpose (imports and comments "name the word and move it"), and nothing
harvests docstrings. For a Python repository in the docstring culture, most of
the stated meaning lives there — inert. Needs a decision first: docstrings are
prose *inside* the code, so the reconcile posture (check, not source; names,
not claims) probably extends to them, but nothing implements it.

**Tests are indexed, never read as intent.** A test names the behaviour the
project promises, in the project's own vocabulary, and for spec-conformance
repositories the tests are most of the evidence there is. Planned; not built.

**Generated-but-committed code is surveyed as if authored.** Vendored
dependencies, protobuf output, migration snapshots — tracked, parsed, and
currently indistinguishable from what the team wrote. A repository with a
`vendor/` or `generated/` tree would spend survey sessions describing a
machine's output.

**`docs/` beyond the README.** Reconcile and the name harvest stop at the root
README. Projects whose real prose lives in `docs/` get a reconcile that checks
the wrong document. Extending it is mechanical once the README form holds; the
open question is ordering (which document is *the* claim source when they
disagree with each other).
