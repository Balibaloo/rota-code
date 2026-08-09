# Agreed changes — the verification checklist

Everything settled in the design session, written so it can be **checked** rather
than remembered. Each item says what changes and how to prove it landed.

Status key: `[ ]` not started · `[~]` partly done · `[x]` done and verified

---

## 1. Names

The register: **every role is named for what it is answerable for, as a job a
senior person could hold.** Not the subject they know about, not what they do
when woken.

| now (legacy) | becomes | answerable for |
|---|---|---|
| `client` | **`principal`** | wanting it and ruling on it — principal–agent, not seniority. Every role is a fragment of their attention; they are the whole that stayed whole, and the root of the message DAG |
| `interface` | **`liaison`** | the conversation with the principal, and the clarity of everything crossing **to and from them**. Organises and re-presents; never interprets or summarises |
| `vision` | **`gatekeeper`** | what the project is — and isn't. Also solves the `vision`/`Vision` collision, the only one at L0 |
| `domain` | **`terminologist`** | one meaning per word. Prescriptive by discipline, which is why not *lexicographer* |
| `architect` | `architect` | the system holding together, and its outward promises |
| `tester` | `tester` | what "done" means, written so a machine can check it. It does the testing *by writing the tests* |
| `developer` | `developer` | making it exist |
| `critic` | `critic` | whether it was done, and done well |

- [x] **1.1** role ids renamed in `design/graph.json` (and `layout.json` keys)
- [x] **1.2** prompt directories renamed under `rota/prompts/`
- [x] **1.3** `from_role` / `to_role` string literals renamed across `rota/` and `tests/`
- [x] **1.4** predicate `wakes=` targets renamed in `predicates.py`
- [x] **1.5** `client` → `principal` everywhere, including `client.py` (module name),
      `ClientBackend`, `client_present`, `to_role='client'`
- [x] **1.6** databases are throwaway — every one is built by `init_db` from
      `schema.sql` at test or boot time, so there is nothing to migrate

Done by `rota/tools/rename_roles.py` (`77dbe12`), which is kept because it
records what was renamed and what was deliberately *not*: `clientX`,
`getBoundingClientRect`, and three sentences where "interface" was English (now
"protocol"). Its first run missed `.tools` files, and nothing failed — mode
allowlists are data, so a stale name silently narrows the working set.

**Verify:** `grep -rniE "\b(interface|vision|domain|client)\b" rota/ tests/rota/`
returns nothing outside this file and the rename script. **Clean; 108 tests green.**

---

## 2. Collisions — one name, one job

Seven found mechanically by `python -m rota.tools.vocabulary --analyse`.

- [x] **2.1** `consult` ×3 → operation keeps `consult`; **message verb → `ask`**;
      **session mode → `readonly`**
- [x] **2.2** `batch` ×2 → Architect's operation → **`group`**; the reach value keeps `batch`
- [x] **2.3** `index` ×2 → `brief.index` operation → **`list`** (matching `ledger.list`);
      the reach value keeps `index`
- [x] **2.4** `brief` ×2 → artefact keeps `brief`; **message verb → `deliver`**
      (*broadcast* is the informal name for delivering to all three, not a wire verb)
- [x] **2.5** `scope` ×2 → item kinds become **`in_scope` / `out_of_scope`**;
      `non_goal` went with it, since the opposite of in-scope is out-of-scope
- [x] **2.6** `utterance` ×2 → journals hold **entries**; `cause_kind` value → **`conversation`**
- [x] **2.7** `amend` ×2 → operation keeps `amend` (the owner's act); the
      principal's ruling becomes **`revise`** (a request for that act)

Done by `rota/tools/split_senses.py`. `graph.json` had to be handled
structurally — `consult` and `brief` are told apart by *edge type*, which no
textual pass can see.

Two consequences worth recording, because neither was in the plan:

- **the mode key is the message verb**, so renaming `brief → deliver` renamed
  the prompt files with it (`gatekeeper/brief.md` → `deliver.md`). That coupling
  is deliberate — it is what makes a role's modes enumerable from the graph
- **`gatekeeper/consult.md` was the `consult` *verb*'s prompt, not the session
  mode's.** It became `ask.md`, not `readonly.md`. The two senses were close
  enough that the first pass renamed the wrong one and nothing complained

**Verify:** `python -m rota.tools.vocabulary --analyse` reports zero collisions.
**Zero**, and `tests/rota/test_vocabulary.py` now makes it a constraint rather
than a report — including a case proving the check can fail, and one proving
composition (artefact↔table, operation↔result) is not reported as collision. The
first sweep's 17 findings were 10 parts noise, and an ignored check looks like
coverage.

---

## 3. Reach — the grammar was two axes wearing one name

`scope` as read-breadth was jargon we invented; the project meaning is the
ordinary one. Rename ours, keep theirs. And it is **not one axis**: six values
answer *which rows*, two answer *how much of each row*.

```
rows:  none | single | batch | window | delta | query | all
depth: index | body
```

- [x] **3.1** edge field `a:` → `rows:` + `depth:` in `design/graph.json` (93 edges)
- [x] **3.2** `graph.py`: `SCOPES` → `ROWS` + `DEPTH`; `Edge.a` → `Edge.rows`/`Edge.depth`
- [x] **3.3** `check_structure`'s `full`-is-owner-only rule becomes a rule about
      *authority*, stated once — **but not in the agreed words.** "`rows: all`
      reads are owner-only" would have banned seven ordinary reads: the three
      shape roles reading the brief index, Architect scanning criteria,
      Terminologist scanning tickets, Liaison consulting the schedule. Reading a
      whole index is the normal case and always was. The rule that survives is
      the pair: **a non-owner may take every row, or take bodies, but never
      both.** Same intent, correct extension
- [x] **3.4** `inspect_api.py` and `panels.js` display both fields
- [x] **3.5** `full` disappears as a value — it and `index` returned the same
      thing once `full` meant the full index; the only difference was permission
- [x] **3.6** *not agreed, but necessary:* **`depth` is a read concept only.** A
      message carries refs, never bodies — a law, not a setting — and a write's
      depth is whatever was written. Putting the field on those edges to hold a
      constant would be inventing data, so `check_structure` rejects it

**Verify:** no `"a":` key remains in `graph.json`; `full` appears nowhere.
**Both hold.** `tests/rota/test_graph_reach.py` proves the authority rule can
fail (a non-owner taking the model whole) and that ownership makes the identical
read legal — the rule catches nothing today, which is what a satisfied lint
looks like, not a weak one.

---

## 4. Laws amended

- [x] **4.1** **Liaison narrowed** — owns clarity of traffic *to and from the
      principal only*. Role-to-role traffic is not its business
- [x] **4.2** **Priority moves from `batches` to `items`** — it is a property of
      what the principal wants, which is an item. Makes `batches` single-writer
      and gives law 9's "priority moves batches whole" for free
- [x] **4.3** **Review order flips: harness → Critic → Architect.** Already true
      in `predicates.review`, which screens intent before paying for a
      constraint review; the structural half lands with the delivery loop (§5.6)
- [x] **4.4** **`architect → critic: finding` is removed** — with Critic first,
      Architect's judgement is a gate. This was the *only* declared contact
      exception, so law 3 now derives every message edge with none
- [x] **4.5** **Findings carry the grain**: `{constraint_id, status, grain}`, as
      rows on a `findings` table rather than a message. Nothing about *why* —
      asserted, not trusted: the test rejects a `why`, `reason` or `text` column
- [x] **4.6** **Critic's brief gains one standing question** — *"is there
      anything here nobody asked for?"* Judgement, not enumeration. (The
      hunk→criterion mapping was designed and then dropped: it improved the
      explanation, not the outcome, and cost a scaling cliff)
- [x] **4.7** **Touch set** — `batch_touch`, paths always and symbols where
      confident, with the confidence written down rather than implied. It gates
      nothing, and a test commits a write outside the set to prove it
- [x] **4.8** **Stop / halt** — two verbs, in `rota/config.py`. `stop` drains;
      `halt` preempts; neither resumes on its own; the idle reason names the
      halt so a stopped system never reads as a finished one. Intake still lands
      in both
- [x] **4.9** **Ledger resolution is decision-linked** — `decisions.author`
      stages the close in the same commit, and there is no `ledger.resolve` at
      all. This also made `ledger.status = 'resolved'` reachable, so it left
      §5.6's list

---

## 5. Predicates and the delivery loop

- [x] **5.1** 21 predicates declared, each naming the state it drains
- [x] **5.2** `check_terminal_states()` — every lifecycle state drained or
      declared terminal *with a reason*
- [x] **5.3** `check_predicates_can_fire()` — declarations are not implementations
- [x] **5.4** `check_states_are_reachable()` — a state nothing writes is a state
      nothing can be in
- [x] **5.5** **Wire the predicates into `loop.py`** — all 21, and `frontier()`
      is now one call instead of `open_tips(...) + predicate_wakes(...)`. That
      union was the frontier stated twice, with the tips half invisible to every
      check written against the other
- [x] **5.6** **Build the unreachable states' writers** — `rota/lifecycle.py` is
      the single writer of batch runtime state, and `rota/harness.py` records
      what the tests said. `ledger.status = resolved` was closed by §4.9
- [x] **5.7** `batch_touch` table, so `annotate` can fire — and the dynamic-table
      exemption in the lint went with it
- [x] **5.8** `merge` implemented. `lifecycle.mergeable` returns the *reason* a
      batch cannot merge rather than a boolean, so a finished-looking batch that
      is stuck says why
- [x] **5.9** **Predicate priority: fix-before-start**, as four bands —
      `traffic` (already in flight) · `fix` · `gate` · `start`
- [x] **5.10** **Retry exhaustion escalates, never abandons** — the `exhausted`
      predicate. `tests_failing` going quiet above the cap was abandonment
      wearing the clothes of a budget: work undone, nothing firing, the system
      reporting itself quiescent. The rung is *derived* from what has already
      been sent about the batch rather than stored, so it cannot drift out of
      step with the messages that are the escalation. It stops at Gatekeeper —
      above that is the principal, and nothing wakes a person
- [x] **5.11** Split `Predicate` — `DERIVED` and `SCHEDULER` sentinels. `wakes=""`
      meant both "computed per row" and "no role at all", so the lint could not
      tell a typo from a deliberate blank
- [x] **5.12** **Per-batch `annotate` mode** for Architect, separate from
      `group`: grouping is cheap and index-only, annotating reads source, and one
      session across all batches would exhaust the context that makes it useful

**Verify:** `python -m rota.predicates` — 21 predicates, four lints, **no
problems**. The delivery loop runs end to end in `tests/rota/test_delivery.py`
with no model in it at all; if any step there had needed one, the design would
be wrong.

---

## 6. Config — the principal owns all of it, exceptions ruled case by case

All in `rota/config.py`, declared with the reason each exists. Reading an
undeclared key is an error rather than a default — a typo that silently returns
a default is invisible at both the call site and the setting site.

- [x] **6.1** `loop_cap` (default 10) — dev↔test bounces. Spends compute
- [x] **6.2** `interrupt_cap` (default 3) — before it becomes the principal's
      problem. **Spends the principal.** Different resource, different number,
      and a test asserts the two defaults stay apart
- [x] **6.3** `merge_gate` — does a passing verdict merge, or wait for review?
      A setting the principal toggles, *not* phase-derived: trust should not
      increase on a schedule
- [x] **6.4** `contest_defences` (default 1) — how many times Gatekeeper may
      defend an item before it must amend. *Declared; enforcement lands with the
      contest path*
- [x] **6.5** `ledger_signoff` — whether a decision resolving a ledger entry
      needs the principal's sign-off. *Declared; enforcement with signoff*
- [x] **6.6** the principal-touch cap and the message attempt cap moved into the
      same surface. `tests_failing` had a literal `10` in it and `boot` took a
      cap nobody passed; a test now asserts neither module enforces a limit it
      did not read from here

---

## 7. Closed since, and still open

**Closed while doing the rest** — each was on this list as owed:

- ~~L0 has never been written~~ → **`rota/LAWS.md`**. The engagement, the eight
  answerabilities, and the thirteen laws with every amendment marked and
  reasoned. Three tests keep it honest: every declared L0 term must appear there,
  every role must be named, and no legacy vocabulary may survive
- ~~the dynamic-table exemption is a bypass~~ → gone with `batch_touch`. There is
  no longer a way to declare a predicate against a table that does not exist
- ~~prompts, not started~~ → all 43 modes have a piece, and three new constraints
  hold them: every mode has one, every piece names its mode, and a `.tools`
  narrowing may not name anything outside the role's namespace

**Found while doing the rest** — neither was on any list, and no check we had
could have seen either:

- **Nothing turned tickets into batches.** `criteria` produced them, `batch_start`
  waited for them, and no predicate connected the two — so the understanding loop
  ran to completion and the delivery loop never began. Every check was about
  *states*, and a missing step *between* two reachable states is invisible to all
  of them. Closed by `grouping`; the gap it represents is not
- **Neither owner could read its own bodies.** Terminologist had the glossary
  index and no way to fetch a sense body it had itself written; Architect the
  same for constraint text. Writing something you cannot read back is not
  ownership. Closed by two read edges using operations that already existed

**Still open, deliberately:**

- **Phases** — law 7 said "phase-dependent" and `phase` appears **zero times** in
  `rota/`. On inspection it is two booleans (*does the problem statement exist*,
  *did the state folder exist at boot*) wearing a state machine's clothes. The
  law now says caps are the principal's rather than phase-derived; if we ever
  want real phases they should be predicated like everything else
- **Ticket readiness** — Architect is accountable for it via the touch set, but
  Gatekeeper owns the text and Terminologist the criteria. Written down as an
  accountability rather than left an accident
- **Reachability stops at link 1 of 5** — schema state → api function → role
  namespace → mode tools → a predicate that wakes that mode. Only the first is
  checked, and links 2–5 are where `grouping` was hiding
- **`survey_records.outcome`** is listed as a lifecycle but both values are
  terminal, so by my own definition it is a classification
- **`contest_defences` and `ledger_signoff` are declared, not enforced.** Both
  are read by nothing yet; the paths they gate are not built
- **Edge coverage is 34/99.** Developer has none at all — the delivery loop is
  exercised through the scheduler and the harness rather than through sessions,
  which is honest for what exists and is not the same as tested

---

## 8. Verification

Every command below, run at the point this checklist was closed:

| check | result |
|---|---|
| `python -m rota.graph` | **graph consistent**, contacts derive with zero exceptions |
| `python -m rota.predicates` | 21 predicates, four lints, **no problems** |
| `python -m rota.tools.vocabulary --analyse` | **zero collisions** |
| `python -m rota.coverage` | 34/99 edges |
| `python -m pytest tests/rota -q` | **174 passed**, 6 skipped |

**The legacy-terminology check**, which is the one that says the rename is done:

```bash
grep -rniE "\b(interface|vision|domain|client|utterance|non_goal)\b" \
  rota/ tests/rota/ \
  | grep -vE "AGREED.md|rename_roles.py|split_senses.py|test_vocabulary.py"
```

**Returns nothing.** The three excluded files are the two migration scripts and
the test that asserts the terms are gone — all three are *about* the old names,
which is the only legitimate reason to contain one.

Every check above is also a test, so none of this depends on remembering to run
it: `test_graph_reach`, `test_predicates`, `test_vocabulary`, `test_laws`,
`test_config`, `test_frontier`, `test_delivery` and `test_prompts` each hold one
part of this document.
