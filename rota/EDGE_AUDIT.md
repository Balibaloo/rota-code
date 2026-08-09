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

## Suggested order

1. **Findings 2 and 3** — verb fixes, mechanical, and they close the last of the
   one-name-two-jobs work the vocabulary pass started
2. **Finding 7** — one check, prevents a whole class of silent stranding
3. **Finding 5** — decide what reach means for a create
4. **Finding 1** — the eight channels. This is the interesting one and the only
   one that is really about the design rather than the notation
5. **Finding 4** — the reach declaration, once 1 is settled, because both are
   about how much a role should see
