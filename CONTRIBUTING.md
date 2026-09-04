# Commit message standard

This repo uses [Conventional Commits](https://www.conventionalcommits.org/)
for the summary line, with a plain-prose body. No author or co-author
footer of any kind — no `Co-Authored-By:`, no `Signed-off-by:`, no tool
signature. Authorship lives in `git log --format='%an'`, not in the
message body.

## Format

```
type(scope): summary

Body, in short paragraphs. Explain what changed and why — the
mechanism, the bug, the measurement — not a restatement of the summary.
```

- **type** — one of:
  - `feat` — a new capability
  - `fix` — a bug fix, including a design/behaviour correction
  - `docs` — documentation, design notes, decision records, plans
  - `test` — new or changed tests, fixtures, recordings, benchmarks
  - `refactor` — restructuring with no behaviour change
  - `chore` — everything else mechanical (renames, bookkeeping, marks)
- **scope** — optional, lowercase, names the module or subsystem most
  responsible for the change (`sandbox`, `scheduler`, `cockpit`,
  `prompt`, `core`, `cli`, `testkit`, `audit`, `bench`, `client`,
  `register`, `plan`, `roles`...). Omit it when the change doesn't
  belong to one area.
- **summary** — states the change or the finding directly. Doesn't need
  to be imperative-mood ("add X"); "the collision the design exists
  for" or "a criterion's id is one ticket's" are both fine, as long as
  the reader knows what happened without opening the diff.
- **body** — optional. Use it when there's a *why* worth keeping: the
  bug's mechanism, what was measured, what was tried and reverted and
  why. Skip it for anything the summary already says in full. No
  bullet walls — short paragraphs read better in `git log`.
- **footer** — none. No `Co-Authored-By`, no ticket references, no
  sign-off block.

## Examples

A one-liner needs nothing else:

```
chore: stage 0 done -- 92 renames, 183 green
```

A body that carries the reasoning, not just the outcome:

```
docs: the fan-out is settled, and the two stubborn fixtures share a shape

"Liaison chooses which owner holds the answer" moves from open to
settled, with what it cost. And the two fixtures no arm has ever made
stable turn out to share a structure: both open with something that is
not the message itself -- a greeting before a request, a fact before a
question -- which is a hypothesis with a cheap test rather than a
coincidence between two hard sentences.
```

A fix that names the bug's actual mechanism, including a reverted
attempt and why it was wrong:

```
fix(prompt): the hedge was carrying the answer

Relays reaching the principal kept ending in a question that belonged
to whoever builds the thing, not whoever asked about it -- and trailing
questions correlated with the misses, so refusing them should have
forced a session to commit to what the owner said or say it couldn't
with schedule.reask.

It forced the wrong half. Two relays with real content and a hedge
attached got refused, and the session committed to neither -- the ask
went unresolved, the ladder ran to its end, and Liaison handed the
principal their own question back. Two informative partial answers
became two content-free clarifications; the one full hit was untouched.

The trailing question wasn't the disease -- it was the model shipping a
partial answer with an honest caveat, and the caveat was the only part
a guard could see. Reverted: the relay is still the largest quality gap
here, and the next attempt should give it something better to say
rather than forbid a way of saying things. Forbidding is the wrong
family when what's forbidden is a symptom of the session knowing less
than it needs.
```

A longer one, multiple paragraphs each carrying one finding:

```
fix(sandbox): the collision the design exists for, and the three reasons it never happened

term_collision is the glossary's contradiction -- one word, two senses,
only the principal rules -- and on this repository it never fired on a
real ambiguity once, though two words genuinely mean two things here.
Three compounding reasons.

A second differing sense was thrown away as a duplicate: accidental
repetition and genuine collision arrive in the identical shape, and
INSERT OR REPLACE on a term-derived id kept whichever was written last
-- destroying the correct sense four times across two runs. A differing
sense from a *different area* is now a second row, since area is
evidence and not authority: which sense survives isn't computable and
nothing wins silently anymore.

The mode named two outcomes and offered one verb: its brief already
said "if they say the same thing, that's a duplicate, and saying so is
the answer", but the working set was only two reads and a report.
glossary.same is the missing half -- it recognises sameness (an
observation) without collapsing senses (a decision that stays the
principal's); the losing row is superseded rather than deleted, since
only one kind of mistake here is recoverable.

It also fired at the wrong time: band fix outranks start, so one
collision found in area two drained a whole run to zero survey records
in 71 turns. It now holds while the survey pass runs and fires
immediately after, since the downstream cost of an unresolved collision
doesn't exist yet during onboarding -- rests_on_a_collision already
suppresses any consumer.
```

## Why no footer

Every commit on `rota/foundation` from 2026-08-09 onward was rewritten
to this standard on 2026-09-04 (518 commits; the 300 commits before
that date, predating the `rota` project, were left untouched). The
history this repo already has doesn't carry per-commit attribution
trailers, and this file makes that the rule going forward rather than
an accident of how the rewrite happened to land.
