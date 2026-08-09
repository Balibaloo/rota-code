# Edge audit

All 118 edges in `design/graph.json`, checked mechanically and by reading. The
graph is the part-list — `sandbox.build` constructs every namespace from it, so
an error here is not a documentation error, it is a capability that exists or
fails to exist.

Findings are numbered. Each says whether it needs a **ruling** (a decision only
the principal can make) or is a **fix** (unambiguous, just work).

---

## What is clean

Worth stating, because it is most of the graph:

- **No duplicate edges.** No `(source, target, type, verb)` appears twice.
- **No unimplemented edges.** Every read and write has a function in `api.py`.
- **Law 3 holds with zero exceptions** — the declared message edges and the set
  derived from read/write structure agree exactly.
- **Every parallel edge pair is legitimate.** 22 pairs carry more than one edge;
  every one is a distinct verb, not a duplicate. `architect → model` carries
  five: amend, consult, survey, find, load — a write, an index read, a record, a
  verdict and a body read. That is what a multigraph of a real system looks like.
- **`consult`, `load`, `scan` are used consistently** across every artefact they
  appear on. `consult` is always "my own artefact, index depth"; `load` is
  always "the rows for this batch, in full".
- **Every role can be woken**, by an inbound verb or a predicate or both.

### On the parallel edges looking new

They are not new. The count went 113 → 118 across the entire session, and only
**four** are genuinely new capabilities (`model.find`, `batches.annotate`, and
the two owner body-reads in finding 4). The 22 multi-edge pairs are almost
entirely original.

What changed is that they are *drawn* separately now. Before `computeSpread`,
parallel edges rendered on top of one another and only the last was visible —
the picture was claiming one relationship where there were five. The graph did
not get more complicated; it stopped under-reporting.

---

## Findings

### 1 · Eight channels the structure grants and no verb uses — **ruling**

Law 3 derives a contact wherever a role reads a judgement artefact someone else
writes, or writes one someone else reads. Eight such channels have no verb, so
they are permitted and unusable:

| channel | derived via | reading |
|---|---|---|
| `architect → terminologist` | criteria, glossary | **probably a real gap.** Architect reads the glossary and cannot ask about a term. Developer and Tester both have `question → terminologist` |
| `critic → terminologist` | criteria | a criterion Critic cannot judge has nowhere to go. It can challenge the *test* but not the *criterion* |
| `gatekeeper → terminologist` | tickets | inform: Terminologist reads tickets Gatekeeper writes |
| `gatekeeper → architect` | tickets, batches, decisions | inform |
| `terminologist → architect` | criteria, glossary | inform |
| `terminologist → critic` | criteria | inform |
| `tester → critic` | tests | inform |
| `developer → critic` | verdicts | **deliberate, and should be recorded as such.** A fail names its criterion and you do not argue with the judge |

The *inform* ones are mostly fine — the receipt cascade already wakes those
owners, so a message would duplicate it. The two marked in bold are different:
one looks like a missing capability, the other like a deliberate refusal that
has never been written down.

**Needs:** a ruling per row — declare a verb, or record the refusal. Right now
all eight are silent, and silence reads the same either way.

### 2 · `author` means two different acts — **fix**

`decisions.author` writes a decision with its reason. `tests.author` writes an
executable test. Same verb, unrelated acts.

The vocabulary sweep missed it because `collisions()` compares *kinds* — is this
word an operation and also a state — and both of these are operations. A word
used for two different operations is invisible to it.

**Suggested:** `tests.encode`. A test encodes its criterion, which is exactly
what Tester is answerable for, and it is not a word anything else uses.

### 3 · `survey` means both looking and recording — **fix**

`code.survey` is a read: go and look at an area. `model.survey` is a write: file
what you found, with citations. The act of surveying and the act of attesting to
a survey are not the same act, and the second is the one that starves constraint
zero.

**Suggested:** `code.survey` keeps it; `model.attest` for the write. You attest
that an area was surveyed, and the citations are what make it evidence rather
than a claim.

### 4 · `brief.list` declares `depth: index` and returns full text — **ruling**

Flagged mechanically: the query selects `text` with no `substr`.

I marked it `index` during the reach split on the argument that a statement *is*
its own index — there is no body being withheld, because `statements` has no
second column. That is true and it is also convenient, and the convenience is
the problem: marking it `body` honestly would trip the authority rule, because
the three shape roles reading every ratified statement are **non-owners taking
every row at body depth** — the single most important read in the system.

So one of these is wrong:

- **the declaration** — statements do have a body, and it should say so
- **the rule** — "every row at body depth is owner-only" is too blunt. The real
  distinction is whether an artefact *has* an index/body split worth enforcing:
  `glossary_terms` and `constraints` do (`sense_body`, `text`); statements,
  tickets and criteria do not
- **the edge** — `brief.list(since_version)` is delta-shaped by construction, so
  `rows: delta` may be the honest answer and the whole tension dissolves

I lean to the third: the operation was *built* for deltas and the edge does not
say so. But it changes what the three shape roles see on a cold read, which is a
behavioural change, not a relabelling.

### 5 · Five writes declare no reach — **fix**

`problem.assert`, `tickets.slice`, `criteria.specify`, `batches.group`, and the
`principal → liaison: converse` message have no `rows`.

Four of the five create rows rather than touching existing ones, so "how many
rows does it reach" is arguably the wrong question — but leaving the field empty
says "nobody decided" rather than "not applicable", and `Edge.reach` renders it
as `none`, which is a different and false claim. Either give them a value or add
one that means *creates*.

### 6 · `tickets.scan` flagged `rows: all` while filtering — **false positive**

The filter is an optional argument; the default path returns every row. The
check was not smart enough to see the branch. Noted so the next person running
it does not chase it.

### 7 · Mode narrowing leaves operations unreachable in narrowed modes — **ruling**

Six roles have operations that appear in *no* narrowed mode's `.tools`. They
stay reachable through un-narrowed modes (a mode with no `.tools` gets
everything), so nothing is lost today:

| role | ops in no narrowed mode | still reachable via |
|---|---|---|
| architect | 6 | `ask`, `escalate` |
| gatekeeper | 6 | `ask`, `challenge`, `elect` |
| terminologist | 9 | `ask`, `question` |
| liaison | 4 | `answer` |
| developer | 1 | `answer`, `challenge`, `reopen` |
| tester | 1 | `answer`, `challenge` |

The risk is directional: the moment someone adds a `.tools` file to the last
un-narrowed mode of a role, those operations silently become unreachable —
present in the namespace, offered by nothing. **A check should assert that every
operation is offered by at least one mode**, so narrowing a mode cannot strand a
capability by accident.

### 8 · Coverage is 34/99, and the gaps have a shape — **fix, at length**

| kind | uncovered |
|---|---|
| reads | 30 |
| messages | 25 |
| writes | 11 |

Reads and messages are what a role does *during a session*; writes are what the
machinery does. We have tested the machinery. **Developer is 0/14** — every one
of its edges is untouched.

---

---

# Second pass — intent, not notation

The first pass checked whether the edges are *well formed*. This one asks whether
they say what anyone meant. Four of these are worse than anything above.

### 9 · The delivery loop is a straight line, not a loop — **fix, urgent**

Three gates guard themselves with "does a row exist for this batch":

```
harness             b.id NOT IN (SELECT batch_id FROM test_runs)
review              b.id NOT IN (SELECT batch_id FROM verdicts)
structural_review   v.batch_id NOT IN (SELECT batch_id FROM findings)
```

Each therefore fires **once per batch, ever**. Walked:

| step | frontier |
|---|---|
| green harness, no verdict | `tick:review` |
| Critic fails it | `tick:verdict_failed` |
| **Developer commits a fix** | `tick:verdict_failed` — again |

`review` will not re-fire, because a verdict row exists. Neither will `harness`,
because test_runs exist. So a batch that fails review **can never pass**: the
Developer bounces on `verdict_failed` until the livelock guard trips.

The guards ask "has this ever been judged" when the question is "has anything
happened *since* it was judged". Nothing records which commit was judged —
`test_runs`, `verdicts` and `findings` all carry `batch_id` and no `commit_sha`.

**Fix:** stamp each judgement with the `head_commit` it judged, and fire when the
batch's current head has no row. Three columns, three predicates. That is what
makes the loop a loop.

This is the sharpest illustration of the reachability gap: every state involved
is reachable, every predicate can fire, every lint is green. The hole is in the
*sequence*, and nothing we have looks at sequences.

### 10 · The cascade runs in alphabetical order — **fix**

Law 9: *"Resolution descends the refs DAG through each artefact's owner in
dependency order (model → backlog → schedule)."*

It does not. The refs graph **is not a DAG** — `model → code → batches → model`
is a genuine cycle, and semantically a real one: a constraint change affects the
batches it bounds, which affects their code, and the model binds that code.

`cascade_order` catches `CycleError` and falls back to `sorted(deps)`. So the
documented dependency order has **never once run**; every cascade since the
system was built has fired in alphabetical order, silently.

Two things wrong, and the second is worse than the first:

- the refs graph has a cycle nothing declares or checks
- a fallback that changes documented behaviour **and says nothing**. A cascade in
  the wrong order looks exactly like a cascade in the right one

**Fix:** assert acyclicity at boot, or declare which ref is the back-edge and
break it deliberately. Either way the fallback must be loud.

### 11 · Nothing refs `tickets`, so amending one cascades to nothing — **fix**

```
amend tickets  ->  wakes NOTHING
```

Criteria are written per ticket (`criteria.ticket_id`), batches are groups of
tickets (`batch_tickets`), tests trace to criteria. Re-slice a ticket and its
criteria, its batch and its tests all keep working from wording that no longer
exists — because no `refs` edge points at `tickets`.

**Missing:** `criteria → tickets`, `batches → tickets`. Both relations already
exist as foreign keys; they were never drawn as refs.

### 12 · Four roles cannot read what they own — **fix**, one **ruling**

| role | writes | can it read it |
|---|---|---|
| **liaison** | `transcript` | **no** — and Gatekeeper, Terminologist and Architect all can |
| **liaison** | `brief` | **no** — cannot see its own prior segmentation |
| **architect** | `decisions` | **no** — Gatekeeper can `decisions.search`; Architect cannot |
| architect / developer / gatekeeper | `ledger` | no — only Liaison reads it |
| critic | `verdicts` | no — **deliberate, keep** |

The first three are gaps of the same kind I already fixed for `glossary` and
`model` and did not think to look for elsewhere:

- **Liaison cannot quote the transcript it owns.** The role answerable for the
  clarity of everything crossing to and from the principal cannot check what
  they actually said. Three roles that never speak to them can.
- **Liaison cannot read the brief.** It segments a second entry with no view of
  what it already segmented, so nothing stops it re-stating the same material.
- **Architect cannot search prior decisions.** Its own prompt tells it to propose
  seams; Gatekeeper's tells it to check prior refusals first. Architect writes to
  the decision record and cannot look in it.

**Critic not reading its own verdicts is right** and should be recorded as
deliberate: a judge that remembers its prior objection is anchored, and cold
re-judgement is the property worth having.

**Ledger is the ruling.** Nobody can check whether an assumption is already
logged, so a retried session logs it twice. Either give the three writers a read,
or accept duplicates and dedupe at the agenda. Mild either way.

### 13 · Terminologist and Tester cannot log an assumption — **ruling**

`ledger.log` is *"a choice made where the criteria were silent"*. Architect,
Developer and Gatekeeper have it. Terminologist and Tester do not.

Both make exactly that kind of choice: Terminologist picking one sense of a
colliding term, Tester deciding what an untestable criterion must have meant.
Those are assumptions in precisely the law's sense, and they are currently
invisible.

The counter-argument is real: Terminologist is *supposed* to challenge rather
than assume, and giving it a ledger might make assuming feel legitimate.

### 14 · Terminologist cannot author a decision, but writes `decided` rows — **ruling**

Law 11: entries are `decided` — *"authored reason on file, written by the decider
in the same session as the decision"* — or `observed`.

`glossary.amend` defaults `provenance='decided'`. Terminologist is not a writer
of `decisions`. So it marks terms as decided and **cannot write the reason that
makes them so**. Either the law does not apply to glossary terms, or an edge is
missing.

### 15 · `verdicts → code` is `1:1` — **fix**

One verdict judges one diff. Once finding 9 is fixed and a batch can be judged
more than once, it is `n:1`.

---

## What this audit says about the checks

Findings 9, 10 and 11 were invisible to every lint in the repo, and they are the
three that stop the system working. The pattern is the same each time:

**Every check we have is about a thing. None is about a sequence.**

- reachability asks *can this state be written* — not *can it be written twice*
- the terminal-state lint asks *does this state have a way out* — not *does the
  way out still work the second time*
- `check_contacts` asks *is this channel derivable* — not *does anything traverse
  it*
- the refs graph is called a DAG in three docstrings and in law 9, and **nothing
  asserts it**

Cheapest new check with real reach: **assert the refs graph is acyclic**, and
make `cascade_order`'s fallback loud instead of silent. After that, one
loop-shaped test — fail a verdict, fix it, assert the batch can still pass —
which would have caught finding 9 on the day it was written.

---

## Suggested order

**Unambiguous, do now:**

1. **Finding 9** — the delivery loop cannot converge. Nothing else matters while
   that is true
2. **Finding 10** — assert acyclicity; make the fallback loud
3. **Finding 11** — two missing refs edges
4. **Finding 12**, first three — Liaison reads transcript and brief, Architect
   searches decisions
5. **Findings 2, 3** — `tests.encode`, `model.attest`
6. **Finding 7** — the "every operation is offered by some mode" check
7. **Finding 5** — explicit reach on the five creates
8. **Finding 15** — `verdicts → code` cardinality
9. **Finding 1** — record the six deliberate channels; add
   `architect → terminologist: question`

**Rulings owed:**

- **13** — may Terminologist and Tester log assumptions?
- **14** — may Terminologist author decisions, or does law 11 not reach glossary
  terms?
- **12, ledger** — read access for the three writers, or dedupe at the agenda?
