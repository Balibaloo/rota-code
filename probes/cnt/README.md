# cnt — an onboarding reference

What a correct onboarding of **Contextual Note Templating** should have written,
derived by reading the repository rather than by running anything.

The repository: `D:/tmp/rota-live/repo`, branch `v3`, commit `766c9e30`.
An Obsidian plugin that creates notes from declarative recipes stored in the
frontmatter of other notes.

## Why this exists

`cnt_new.db` records a run that produced eight glossary terms, five of which are
the plugin's five *prompt types* defined as generic data types, and two
constraints with empty bodies. Nothing in the database said anything was wrong.
There was no reference to compare against, so "was that any good" could only be
answered by a person reading 105 turns.

This is that reference.

## The files

Each file mimics the columns of the rota table it is named for, so a run can be
diffed against it directly.

| file | table | columns |
| --- | --- | --- |
| `glossary_terms.yaml` | `glossary_terms` | id, term, sense_short, sense_body, provenance |
| `constraints.yaml` | `constraints` | id, headline, text, provenance, is_global |
| `constraint_bindings.yaml` | `constraint_bindings` | constraint_id, grain, grain_kind |
| `items.yaml` | `items` | id, text, kind, provenance |
| `survey_records.yaml` | `survey_records` | id, area, outcome |
| `code_index_missing.yaml` | `code_index` | grain, grain_kind, area — rows that **should** exist and do not |

And one file that is not a table:

| file | what it is |
| --- | --- |
| `answer_key.yaml` | the scoreable predictions, including `must_not_mean` |

`answer_key.yaml` is separate on purpose. The table files are faithful mimics and
stay loadable; the key is a different kind of claim and does not belong in a
column.

## How to score a run against it

Three questions, in increasing difficulty:

1. **Presence.** Which `terms_required` are in the glossary at all? On the
   recorded run: one of thirteen (`Folder`, and with the wrong sense).
2. **`must_not_mean`.** Does any recorded sense contain a word the key forbids?
   This is the only mechanical check on *understanding* here, and it is the
   reason the key is worth writing. On the recorded run: five hits.
3. **Senses.** Read them. Not automatable — see `SEAT.md` on why matching a
   sense needs either a brittle exact string or another model.

## The property that makes cnt a good probe

Five of its domain words have an everyday programming meaning that is not the
meaning this codebase uses:

    text · number · natural_date · note · folder

In `src/variables/providers/index.ts` these are the members of
`enum TemplateVariableType` — **the five kinds of value a user can be prompted
for** when an intent runs. Read as ordinary type names they are data types, and
that reading is fluent, confident and wrong.

The recorded run got all five wrong in the same way, which is what a probe is
for: the wrong answer was predictable in advance.
