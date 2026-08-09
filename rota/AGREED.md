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

- [ ] **3.1** edge field `a:` → `rows:` + `depth:` in `design/graph.json` (91 edges)
- [ ] **3.2** `graph.py`: `SCOPES` → `ROWS` + `DEPTH`; `Edge.a` → `Edge.rows`/`Edge.depth`
- [ ] **3.3** `check_structure`'s `full`-is-owner-only rule becomes
      **`rows: all` reads are owner-only** — a rule about *authority*, stated once
- [ ] **3.4** `inspect_api.py` and `panels.js` display both fields
- [ ] **3.5** `full` disappears as a value — it and `index` returned the same
      thing once `full` meant the full index; the only difference was permission

**Verify:** no `"a":` key remains in `graph.json`; `full` appears nowhere as a reach value.

---

## 4. Laws amended

- [ ] **4.1** **Liaison narrowed** — owns clarity of traffic *to and from the
      principal only*. Role-to-role traffic is not its business
- [ ] **4.2** **Priority moves from `batches` to `items`** — it is a property of
      what the principal wants, which is an item. Makes `batches` single-writer
      and gives law 9's "priority moves batches whole" for free
- [ ] **4.3** **Review order flips: harness → Critic → Architect.** Cheap checks
      loop; expensive checks run once and feed the verdict. Most failures are
      failures of intent, so screen there first
- [ ] **4.4** **`architect → critic: finding` is removed** — with Critic first,
      Architect's judgement is a gate. This was the *only* declared contact
      exception, so law 3 now derives every message edge with none
- [ ] **4.5** **Findings carry the grain**: `{constraint_id, status, grain}`.
      Nothing about *why*
- [ ] **4.6** **Critic's brief gains one standing question** — *"is there
      anything here nobody asked for?"* Judgement, not enumeration. (The
      hunk→criterion mapping was designed and then dropped: it improved the
      explanation, not the outcome, and cost a scaling cliff)
- [ ] **4.7** **Touch set** — Architect records expected paths always, symbols
      where confident, with its confidence noted. Stale symbols drop
      automatically, like unresolvable bindings. It stays a *prediction*, not a
      permission
- [ ] **4.8** **Stop / halt** — two verbs. `stop` drains (finish what is
      running, dispatch nothing more); `halt` preempts. Explicit resume only,
      with the halt visible as the idle reason and at the agenda tick. Intake
      still lands while halted; recording and inquiry are always free
- [ ] **4.9** **Ledger resolution is decision-linked** — never self-resolve.
      `decisions.resolves_ledger` already exists. Self-resolve would void
      "no milestone with open assumptions"

---

## 5. Predicates and the delivery loop

- [x] **5.1** 21 predicates declared, each naming the state it drains
- [x] **5.2** `check_terminal_states()` — every lifecycle state drained or
      declared terminal *with a reason*
- [x] **5.3** `check_predicates_can_fire()` — declarations are not implementations
- [x] **5.4** `check_states_are_reachable()` — a state nothing writes is a state
      nothing can be in
- [ ] **5.5** **Wire the predicates into `loop.py`** — declared and tested, not
      yet dispatched
- [ ] **5.6** **Build the six unreachable states' writers**:
      `batches.status` running/deferred/merged · `test_runs` results ·
      `ledger.status = resolved`
- [ ] **5.7** `batch_touch` table, so `annotate` can fire
- [ ] **5.8** `merge` implemented (currently `return []`)
- [ ] **5.9** **Predicate priority: fix-before-start.** Failed verdicts and
      failing tests outrank new batches. One thing at a time
- [ ] **5.10** **Retry exhaustion escalates, never abandons** — climbing law 6's
      ladder one rung at a time (Architect → Gatekeeper → principal), because the
      usual *reason* for exhaustion is not knowing who to ask
- [ ] **5.11** Split `Predicate` — waking a role and "the scheduler should act"
      are different types; flattening them is why `wakes` drifted twice
- [ ] **5.12** **Per-batch `annotate` mode** for Architect, separate from
      `group`: grouping is cheap and index-only, annotating reads source, and one
      session across all batches would exhaust the context that makes it useful

---

## 6. Config — the principal owns all of it, exceptions ruled case by case

- [ ] **6.1** `loop_cap` (default 10) — dev↔test bounces. Spends compute
- [ ] **6.2** `interrupt_cap` (default 3) — before it becomes the principal's
      problem. **Spends the principal.** Different resource, different number
- [ ] **6.3** `merge_gate` — does a passing verdict merge, or wait for review?
      A setting the principal toggles, *not* phase-derived: trust should not
      increase on a schedule
- [ ] **6.4** `contest_defences` (default 1) — how many times Gatekeeper may
      defend an item before it must amend
- [ ] **6.5** `ledger_signoff` — whether a decision resolving a ledger entry
      needs the principal's sign-off
- [ ] **6.6** client-touch cap and message attempt cap moved into the same surface

---

## 7. Still open, deliberately

- **L0 has never been written.** Every source presupposes the engagement and none
  states it. Concepts declared in `tools/vocabulary.py`; prose owed
- **Phases** — law 7 says "phase-dependent" and `phase` appears **zero times** in
  `rota/`. On inspection it is two booleans (*does the problem statement exist*,
  *did the state folder exist at boot*) wearing a state machine's clothes. If we
  ever want real phases they should be predicated like everything else
- **Ticket readiness** — Architect is accountable for it via the touch set, but
  Gatekeeper owns the text and Terminologist the criteria. Written down as an
  accountability rather than left an accident
- **Reachability stops at link 1 of 5** — schema state → api function → role
  namespace → mode tools → a predicate that wakes that mode. Only the first is
  checked
- **The dynamic-table exemption is a bypass** — one predicate uses it; it must
  stay one
- **`survey_records.outcome`** is listed as a lifecycle but both values are
  terminal, so by my own definition it is a classification
- **Prompts** — the whole point of the vocabulary pass. Not started

---

## 8. Verification

```bash
python -m rota.graph                       # graph consistent, contacts derive
python -m rota.predicates                  # every state has a way out
python -m rota.tools.vocabulary --analyse  # collisions, duplication, hierarchy
python -m rota.coverage                    # edge coverage
python -m pytest tests/rota -q             # 108 green at the time of writing
```

**The legacy-terminology check**, which is the one that says the rename is done:

```bash
grep -rniE "\b(interface|vision|domain|client|utterance|non_goal)\b" \
  rota/ tests/rota/ | grep -v "AGREED.md"
```

Every remaining hit must be ordinary English, never an identifier.
