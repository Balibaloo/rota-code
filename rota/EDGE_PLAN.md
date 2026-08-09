# Remediation plan

Every finding in `EDGE_AUDIT.md` has a solution. Six packages, ordered so each
lands on ground the previous one made solid. Each says what changes, what proves
it, and what could go wrong.

Two findings arrived after the audit was written and are folded in as **16** and
**17**.

---

## 16 · `findings` is bound to the wrong artefact — **fix, mine, this session**

I put `findings` in `TABLES_OF_ARTEFACT["model"]`. A finding is Architect's
structural verdict on a *batch*; it is not part of the system model, which is
constraints, bindings and surveys.

The consequence is not cosmetic. Receipts map table → artefact, and the cascade
walks refs from there — so writing one **`satisfied`** finding, a clean review
saying nothing is wrong, produces:

```
architect<-cascade  developer<-cascade  architect<-cascade  critic<-cascade
```

A clean structural review wakes the entire delivery chain as though the system
model had changed, and wakes Architect twice — including the role that just
wrote it, which is a livelock shape.

**Fix:** make `findings` its own artefact node, owned by Architect, with refs
`findings → model` (which constraint) and `findings → batches` (which batch). It
sits beside `verdicts` in the graph, because that is what it is.

## 17 · Nineteen capabilities no prompt mentions — **fix**

Not redundant — **unbriefed**. The role has the function and is never told when
to use it:

| role | never mentioned |
|---|---|
| architect | `ledger.log`, `model.load`, `model.survey`, `msg.report_liaison`, `transcript.quote` |
| gatekeeper | `brief.list`, `code.survey`, `ledger.log`, `problem.prioritize` |
| liaison | `msg.ask_architect`, `msg.ask_gatekeeper`, `msg.ask_terminologist`, `schedule.consult` |
| terminologist | `brief.list`, `code.survey`, `criteria.consult`, `msg.answer_tester`, `msg.challenge_gatekeeper`, `transcript.quote` |

Three of these are load-bearing and their absence is a functional hole:

- **Liaison's three `msg.ask_*`** are the entire readonly-inquiry route — law 10,
  "every principal message is handled read-only first". No prompt tells Liaison
  that routing a question is a thing it does.
- **`problem.prioritize`** is the priority lever of law 9. Gatekeeper is never
  told it exists.
- **`ledger.log`** appears only in Developer's brief. Architect and Gatekeeper
  can log assumptions and are never told to.

This is the static half of the L1 gap: before spending GPU on whether a role
*chooses* the right action, make sure it has been told the action exists.

---

# The packages

## P1 · The loop closes

**Finding 9.** Nothing else matters while a failed batch can never pass.

- add `commit_sha TEXT` to `test_runs`, `verdicts`, `findings`
- `harness`, `review`, `structural_review` fire when the batch's current
  `head_commit` has no row of that kind — not when no row exists at all
- `lifecycle.record_test_run`, `verdicts.emit`, `model.find` stamp it
- `mergeable` reads the judgements *for the current commit*

**Proves it:** one loop-shaped test — green harness → Critic fails → Developer
commits → assert `review` fires again → Critic passes → assert it merges. That
test would have caught this on the day the predicate was written.

**Risk:** low. New column, three `WHERE` clauses. The only judgement call is
whether a verdict against an *older* commit still counts for `mergeable` — it
must not, or a stale pass merges a diff nobody judged.

## P2 · The cascade is honest

**Findings 10, 11, 16, plus the missing refs.**

1. **Move `findings` out of `model`** (16) — do this first; it changes what
   refs exist
2. **Add the missing refs edges.** Every schema foreign key that crosses an
   artefact boundary should have one:

   | edge | from |
   |---|---|
   | `criteria → tickets` | `criteria.ticket_id` |
   | `batches → tickets` | `batch_tickets.ticket_id` |
   | `batches → problem` | `batches.item_id` |
   | `tests → batches` | `tests.batch_id` |
   | `verdicts → batches` | `verdicts.batch_id` |
   | `findings → batches` | `findings.batch_id` |
   | `findings → model` | `findings.constraint_id` |

   `model → decisions` (`constraints.rationale_decision`) is the one to leave:
   decisions supersede rather than change, so it is not a cascade path.

3. **Resolve the cycle.** `model → code → batches → model` is semantically real.
   Either declare a back-edge and break it deliberately, or accept the cycle and
   define the order some other way — but `cascade_order` must stop returning
   alphabetical order while claiming dependency order.
4. **Make the fallback loud.** A silent `except CycleError: return sorted(...)`
   is how this survived. If it cannot compute the order it should raise.
5. **Assert acyclicity at boot**, alongside the other graph checks.

**Proves it:** `amend tickets` wakes its criteria, its batch and its tests. A
clean finding wakes nobody. `cascade_order()` is not `sorted()`.

**Risk:** medium — this is the package that changes behaviour most. Adding seven
refs edges widens every blast radius, and `batches → problem` in particular means
an item amendment now cascades where previously only the approval check caught
it. That is the intent, but it will wake more than it used to.

## P3 · Owners can read what they own

**Finding 12.** Four read edges, all using operations that already exist:

| edge | verb | reach |
|---|---|---|
| `liaison → transcript` | `quote` | `window` / `body` |
| `liaison → brief` | `list` | `all` / `index` |
| `architect → decisions` | `search` | `query` / `index` |
| *ledger reads* | — | **ruling owed** |

Record Critic-not-reading-verdicts as deliberate in the graph node note, so the
next audit does not re-raise it.

**Proves it:** the "owners who cannot read what they own" query returns only the
deliberate cases.

**Risk:** low, but `liaison → transcript` deserves a thought — Liaison is the
role that must not interpret, and giving it the transcript gives it more to
interpret *with*. The counter is that quoting is how you avoid interpreting.

## P4 · Vocabulary residue

**Findings 2, 3, 5, 15.** Mechanical, and they finish what the vocabulary pass
started:

- `tests.author` → `tests.encode`
- `model.survey` → `model.attest` (`code.survey` keeps the word)
- explicit `rows` on the five creates — or a value that means *creates*
- `verdicts → code` becomes `n:1` once P1 lets a batch be judged twice

**Proves it:** `python -m rota.tools.vocabulary --analyse` stays at zero, and a
new check — *no verb names two different acts across artefacts* — which is the
one the sweep could not make because it compares kinds, not acts.

**Risk:** none.

## P5 · The checks that would have caught all of this

The audit's real conclusion: **every check is about a thing, none about a
sequence.** Four new ones, cheap:

1. **refs graph is acyclic** — would have caught 10
2. **every schema FK crossing artefacts has a refs edge** — would have caught 11
   and half of P2 automatically, and keeps catching it
3. **every operation is offered by at least one mode** (finding 7) — stops a
   `.tools` file silently stranding a capability
4. **every operation is mentioned in at least one prompt** — would have caught 17

And the one that is not a lint but a test: **the loop-shaped case** from P1.
Fail, fix, pass. Any gate that can only fire once fails it.

**Risk:** none. Check 4 will fail on day one — that is P6.

## P6 · Briefing gaps

**Finding 17, plus finding 1's `architect → terminologist: question`.**

Nineteen capabilities need a sentence in a prompt saying when to use them. Three
need more than a sentence because they are whole jobs nobody described:

- Liaison routing a principal question to the role that owns the answer
- Gatekeeper moving priority
- Architect and Gatekeeper logging assumptions

Also record the six deliberate no-verb channels in the graph so they read as
decisions rather than omissions.

**Proves it:** check 4 from P5 goes green.

**Risk:** none, and this is the package that most changes what the system
actually does when a model is driving it.

---

## Order, and why

```
P1  loop closes          nothing works downstream of this
P2  cascade honest       changes what wakes; do it before testing wakes
P4  vocabulary           mechanical, no dependencies, cheap to land
P5  checks               green once P1-P4 are done, except check 4
P6  briefing             makes check 4 green; last because it is the most words
P3  owner reads          independent; slot anywhere
```

P1 and P2 are the two that change behaviour. Everything else is additive.

## Still owed as rulings

- **13** — may Terminologist and Tester log assumptions?
- **14** — may Terminologist author decisions, or does law 11 not reach glossary
  terms?
- **12** — ledger read access, or dedupe at the agenda?
- **P2.3** — break the refs cycle, or define the order another way?
