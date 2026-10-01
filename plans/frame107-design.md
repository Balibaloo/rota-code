# Frame 107, the Critic's doubt reaches the Architect: design record

Rota workflow. Opus scope read, 2026-10-01 15:15. Ruled: Roman, 2026-10-01 15:12.

The change is one edge, one generated op with a guard, one new Architect mode
and four text edits. The Architect has no `challenge` mode today
(observed: `rota/roles/prompts/architect/`, 2026-10-01). A message wakes its
recipient in the mode named by the verb (observed: `prompts.compose`, and the
`test_graph_reply.py` docstring), so the mode must be added. The Critic emits
its verdict on the criterion as written, and the doubt goes beside it
(reasoned: a held verdict is a new stall). Open question 1 confirms this.

## Scope

**1. `rota/design/graph.json`.** Add after the `critic -> tester challenge`
edge, in its shape. `expects: decision` copies `architect -> vision_keeper
challenge`. Frame 106's pass 3 holds this file, so add the edge after its commit.

```json
{"s": "critic", "t": "architect", "type": "messages", "v": "challenge",
 "expects": "decision", "n": "doubt about what a criterion says, not about its test",
 "rows": "single", "prose": "quotes",
 "label": "beside the verdict, never instead of it (ruled: Roman, 2026-10-01)"}
```

**2. `msg.challenge_architect`.** The sandbox generates every
`msg.<verb>_<recipient>` op from the graph (observed: `rota/core/sandbox.py`
1890-1960). The edge alone gives `send(refs: list[str], quotes: str | list |
dict, round_no: int = 0)`. No code goes in `rota/roles/api.py`. The generic
challenge rule for a recipient other than the Tester requires one ref row
quoted verbatim (observed: `_challenge_evidence`, sandbox.py 846-856). Add one
branch in `_challenge_evidence` for `ctx.role == "critic"` and
`recipient == "architect"`, modelled on the Tester branch:

1. The refs name one criterion. A test id refuses: "a doubt about a test is msg.challenge_tester".
2. The criterion belongs to this batch (copy the `batch_tickets` check, sandbox.py 784-793).
3. `quotes=` spans the criterion's text (the generic rule, kept).
4. An open Critic challenge on the same criterion refuses a second. The repeat
   guard (sandbox.py 1291-1318) reads answered challenges only.

The generated doc says "Dispute a row architect owns", but the Terminologist
writes the criteria (observed: `criteria.specify` occurs only in
`terminologist/*.tools`). Add a doc branch: "Doubt what a criterion says."

**3. `rota/roles/prompts/critic/review.tools`.** Append `msg.challenge_architect`.

**4. `rota/roles/prompts/critic/review.md`.** Replace lines 28-30 ("A doubt
about what a criterion should say ... in `reason=`.") with:

> A doubt about what a criterion should say is not a fail. Judge the criterion
> as written and emit the verdict. Then send `msg.challenge_architect`: refs
> naming the criterion, `quotes=` copying the words you doubt, and why in one
> sentence. A doubt about whether the test encodes the criterion is
> `msg.challenge_tester` instead.

**5. New `rota/roles/prompts/architect/challenge.md`:**

> MODE: challenge. The Critic doubts what a criterion says.
>
> The Critic judged the batch against the criterion as written, and the
> verdict stands. Your job is the criterion. Read it, its ticket and the
> constraints it touches. Then decide which case it is:
>
> - **The criterion is right.** `decisions.author` naming the criterion and why.
> - **A constraint is wrong or missing.** That is yours. `model.amend`, then
>   `decisions.author` naming the criterion and the change.
> - **The criterion is wrong or out of scope.** Scope is the Vision Keeper's.
>   `msg.challenge_vision_keeper`, refs naming the criterion, `quotes=` its words.
>
> Do not write to the batch and do not message the Developer. A doubt does not
> reopen the Critic's verdict.

**New `architect/challenge.tools`:** `criteria.scan`, `model.consult`,
`model.load`, `model.amend`, `decisions.search`, `decisions.author`,
`msg.challenge_vision_keeper`, `msg.report_liaison`. `decisions.author` satisfies `test_an_asking_edge_has_its_reply` for the
`decision` kind (observed: `REPLY_TOOL` in `tests/rota/test_graph_reply.py`).
Each name exists in `architect/escalate.tools` (observed).

**6. `rota/ROLES.md`.** The Critic's line 210 becomes "**Reaches** architect
(challenge), developer (challenge), tester (challenge)."
`test_each_role_lists_exactly_the_recipients_it_can_reach` fails without it.
Line 206, "a verdict and two challenges", becomes "three challenges". The
implementer runs `tests/rota/test_roles_doc.py` to learn whether the
Architect's **Woken by** line needs `challenge`.

## The case

Add to `tests/rota/cases/l1_judgement.yaml` after
`L1-CR-a-test-that-encodes-nothing-is-a-challenge`. The criterion says the
invoices go, the test encodes that faithfully, and the diff meets it. The item
and the code's comment say the invoices must stay. The right act is a verdict
on the criterion as written and a challenge to the Architect, not the Tester.

```yaml
- id: L1-CR-a-doubtful-criterion-is-a-challenge-to-the-architect
  tier: T1
  model: gemma3:12b
  role: critic
  runs: 5
  pass: 3
  tick: review
  refs: [<b1>]
  repo:
    batch: <b1>
    message: "close an account"
    edit:  # the sample file whole, as in the model case; the change shown
      src/billing/accounts.py: |
        def close_account(account_id):
            # Invoices are records of sale: the law keeps them for seven years.
            rec = load("billing_accounts", account_id)
            if rec is None:
                return False
            delete_all("invoices", account_id)
            rec.values["state"] = "tombstoned"
            save(rec)
            return True
  fixture:
    items:
      - {id: <i1>, text: "closing tombstones the account and keeps its invoices",
         kind: in_scope, provenance: decided, approval: approved, approval_ver: 1, version: 1}
    tickets: [{id: <tk1>, item_id: <i1>, text: "close an account"}]
    criteria:
      - {id: <c1>, ticket_id: <tk1>, term_refs: '[]',
         text: "closing an account tombstones it and deletes its invoices"}
    batches: [{id: <b1>, item_id: <i1>, status: running, head_commit: abc123}]
    batch_tickets: [{batch_id: <b1>, ticket_id: <tk1>}]
    tests:
      - {id: <tst1>, batch_id: <b1>, criterion_id: <c1>, path: test_close.py,
         body: "close_account('a1')\nassert load('invoices', 'a1') is None\nassert load('billing_accounts', 'a1').values['state'] == 'tombstoned'"}
    test_runs: [{id: <r1>, batch_id: <b1>, test_id: <tst1>, commit_sha: abc123, result: pass}]
  expect:
    messages:
      - {to: architect, verb: challenge, count: 1, refs_include: [<c1>]}
  forbidden: {writes: [criteria, tests]}
```

Before the first run, the implementer confirms three facts. The sample `store`
module has `delete_all`, or the edit adds it. The case runner reads a verdict
count and forbidden messages; if so, add `verdicts: {count: 1}` to `expect`
and `messages: [{to: tester}]` to `forbidden`. The Critic sees `<i1>`; if not,
the code comment carries the doubt alone. `test_edge_coverage.py` (77-85)
counts this case for `(critic, architect, challenge)`, so the backlog stays.

## Re-records owed

The brief line and the tool list change for the Critic's `review` mode. Every
case with `role: critic` and `tick: review` re-records (observed: grep of
`tests/rota/cases/*.yaml`, 2026-10-01). The count is five, plus the new case.

1. `ACT-CR-quote-the-tests-code` (`l1_acts.yaml` 315)
2. `L1-CR-pass-a-conforming-diff`, 3. `L1-CR-fail-names-its-criterion`, and
4. `L1-CR-a-test-that-encodes-nothing-is-a-challenge` (`l1_judgement.yaml` 6, 70, 296)
5. `L3-a-failed-verdict-turns-into-a-fix` (`l3_handoffs.yaml` 128, Critic at `review` first)

Not owed: the Critic's `answer`, `finding_review` and `challenge` cases, and
every Architect case, because none reads a changed file.

## Risks

1. Case 2 may now send a needless challenge to the Architect; forbid `{to: architect}` there.
2. Case 4 may drift from the Tester door to the Architect door; the brief gives each door one sentence.
3. The Architect's new mode has no case; a barren wake goes unresolved and climbs (`rota/core/db.py` 765).
4. Frame 106 edits `graph.json` now, so the pass starts after frame 106's commit.

## Open questions

1. Does the batch wait for the Architect's reply before the verdict lands?
   Recommended: no. A held verdict is a new stall on an Architect wake, which
   is the cost the edge exists to remove.
