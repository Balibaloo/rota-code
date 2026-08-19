# contextual-note-templating v3 — written before the first session ran

The third repository, and the first one written *for* the question it answers:
"can I point this at a codebase and learn something from the result." The two
existing keys were written the same way and for the same reason — a prediction
made after reading the output is not a prediction.

**This one matters more than the other two.** The `master` branch of this repo
was already onboarded while I was working out whether the tool runs at all, so
every claim I could make about it is contaminated by having seen the answer. v3
has never been surveyed. Everything below was verified by reading the source at
`766c9e3`, not recalled, and nothing here has been run.

**Repo** contextual-note-templating @ `766c9e3` · TypeScript · 18 source files
under `src/`, an Obsidian plugin. Declared purpose, from `manifest.json`:
*"Prompts for values and templates to create notes."*

---

## What the partition should say before anybody looks

    src                     main.ts
    src/intents             frontmatter.ts, index.ts, intents.ts
    src/templates           index.ts, templates.ts
    src/variables           index.ts, suggest.ts, templateVariables.ts
    src/variables/providers folder.ts, natural_date.ts, note.ts, number.ts,
                            text.ts, index.ts
    src/settings            index.ts, settings.ts
    src/notice              index.ts

Seven areas. If the partition produces fewer than five, the areas are too coarse
to survey separately and the survey results will be about `src`, not about
anything in it.

---

## Predictions

### 1. `intent` is the load-bearing word and it has exactly one sense here

An **Intent** is a named thing a user invokes to create a note. `src/intents/index.ts`:
it carries `name`, `hidden`, `disabled`, `templates`, `sourceNotePath`, and
`newNoteProperties`.

The sense that must *not* appear is the English one — "intention", "purpose",
"what the user meant". On `master` the glossary produced *"intents: Intention or
action of a note"*, which is the dictionary and not this codebase. That entry is
the specific thing to watch for: it is fluent, it is wrong, and nothing in the
audit catches it because "intention" and "action" are novel words.

**Pass:** a sense mentioning notes being *created*, or templates, or frontmatter.
**Fail:** a sense that would be true of the English word without this repo.

### 2. `template` and `variable` are distinct and are routinely confused

A **Template** is a file whose text becomes the new note. A **TemplateVariable**
is a value prompted for and substituted into it. They appear together in every
signature and a definition of either that does not mention the other is
incomplete rather than wrong.

`TemplateVariableType` is a closed set of five: `text`, `number`, `natural_date`,
`note`, `folder`. Each has a provider module. Five is the kind of number a survey
either finds exactly or does not find at all.

### 3. Frontmatter is the interface, and `intents_to` is its key

Intents are declared in a note's YAML frontmatter under `intents_to`, and each
carries `make_a` as its name (`src/intents/frontmatter.ts`). A glossary that
defines `frontmatter` without reaching `intents_to` has defined the Obsidian
concept and not this plugin's use of it.

**This is the best available test of whether a survey read the source or the
file names.** `intents_to` and `make_a` cannot be guessed from a path.

### 4. There is a real constraint about imports and merge order, and it is subtle

`getFrontmatter` resolves imported frontmatter and merges with
`namedObjectDeepMerge(fmImports, fm)` — the *local* frontmatter is the second
argument and therefore wins. A constraint saying imports are overridden by the
importing note is correct and load-bearing; one saying imports are merged is
true and says nothing.

### 5. `hidden` and `disabled` are tri-state, on purpose

Both parse `undefined`, a boolean, or a string whose first character is `T`.
That is a commitment to a frontmatter format written by hand, and it is the kind
of thing a constraint should catch. `disabled` also *filters* — a disabled intent
is dropped, not marked — which means "disabled" and "hidden" are not synonyms and
a glossary that treats them as one has lost a behaviour.

### 6. The esbuild-yaml commitment is real and was already found on master

`intentsSchema.yaml` is imported directly into TypeScript behind a `@ts-ignore`,
bundled by esbuild. On `master` this surfaced as the constraint *"commitment to
esbuild"*, which the audit flagged as echoing the brief. The finding is right and
the wording is empty: a constraint here should say what breaks without it, which
is that the schema cannot be imported and validation stops.

---

## What counts as an invention

- a sense for `intent`, `template` or `variable` derived from the word rather
  than the source
- any constraint about Obsidian's API that this repo does not itself state
- a scope item naming a function that does not exist — the `master` run produced
  22 items and every one was a real symbol, so this is a bar already cleared once
- a number (five variable types, seven areas) that does not match the source

## What counts as a legitimate refusal

- `none_found` on `src/notice` — it is one small module and may genuinely hold
  no term, constraint or scope worth recording
- declining to define `Template` separately from Obsidian's own notion of a
  template file, *if it says that is why*

## The comparison this run exists to make

`master` produced: 4 glossary terms, 2 constraints, 22 scope items, 15 surveys,
and one audit finding. Three of the four terms were near-circular
(`folder: Folder in a provider`, `frontmatter: Front matter of a note`) and one
was the dictionary (`intents`).

So the question is not whether v3 produces artefacts — it will. It is whether
**any single term or constraint here could only have come from reading this
source.** One entry mentioning `intents_to`, `make_a`, the merge order, or the
five variable types would be worth more than twenty of what `master` produced.

---

# The result, appended after the run

24 sessions, quiescent in 117 seconds. 3 glossary terms, 2 constraints, 2 scope
items, 14 surveys, 1 audit finding.

| # | prediction | outcome |
| --- | --- | --- |
| 1 | `intent` gets the dictionary sense, not this repo's | **predicted exactly** — `intent: "a specific action or task"` |
| 2 | `template` / `variable` distinct; five variable types | **missed** — neither word is in the glossary at all |
| 3 | `intents_to` / `make_a` if it read the source | **absent** |
| 4 | the import merge order | **absent** |
| 5 | `hidden` / `disabled` tri-state and the filter | **absent** |
| 6 | the bundling commitment, worded as what it is rather than what breaks | **predicted exactly** — `"Commitment to Obsidian API"`, same audit finding as `master`'s `"commitment to esbuild"` |
| — | seven areas, and under five is too coarse | 5 surveyed: `src/settings`, `src/templates`, `src/notice` never partitioned |

**The question this run existed to ask** was whether any single term or
constraint could only have come from reading this source. **None could.** Every
entry is derivable from a file name and a general knowledge of Obsidian:
`folder: directory in file system`, `esbuild_config_mjs: configuration file for
build tool`, `intent: a specific action or task`.

Two things this settles, and they point in opposite directions.

**The machinery is not the problem.** It partitioned a codebase it had never
seen, sequenced three roles across five areas, kept constraint zero honest,
reached quiescence in under two minutes, and audited its own output correctly.
Nothing livelocked, nothing was fabricated, and the two scope items it did write
name real symbols. Predictions 1 and 6 landing exactly is itself evidence that
the failure is *systematic* rather than random — the same shapes came out of a
different branch.

**The artefacts are.** `master` produced 22 scope items and v3 produced 2, from a
codebase of the same size and shape, which means the number is not being driven
by the source. The glossary is the sharper signal: three terms, all of them
definable without opening a file.

So the next thing worth doing is not another run. It is the survey brief and what
a survey session is *shown* — the same question that turned out to be the whole
of the intake bug, one artefact along. A role asked to find terms in an area, and
handed a file list, will name the files.
