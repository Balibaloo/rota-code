# Frame 107, the Critic's doubt reaches the Terminologist: design record, revision 2

Rota workflow. Opus scope read, 2026-10-01 15:27. Ruled: Roman, 2026-10-01 15:25:
the doubt goes to the Terminologist, and the verdict lands first, as written.

## 1. The edge: (a), a `question`

Choose (a), `critic -> terminologist question`, `expects: answer`. It reuses
the Terminologist's `question` mode and the Critic's `answer` mode, and each
brief needs one paragraph (reasoned). Option (b) needs a new Terminologist
`challenge` mode, because the verb names the mode a message wakes (observed:
`rota/roles/prompts.py` `compose`). The binder requires words in `question=`,
and the doubt is a sentence.

Add two edges to `rota/design/graph.json`, after `critic -> tester challenge`:

```json
{"s": "critic", "t": "terminologist", "type": "messages", "v": "question",
 "expects": "answer", "n": "doubt about what a criterion says, in words; the refs name the criterion",
 "rows": "single", "prose": "question",
 "label": "beside the verdict, never instead of it (ruled: Roman, 2026-10-01 15:25)"},
{"s": "terminologist", "t": "critic", "type": "messages", "v": "answer",
 "n": "the criterion stands, or the repair it took", "rows": "single"}
```

Remove the `silent_channels` entries `critic -> terminologist` and
`terminologist -> critic`, which the edges make false. No code reads them
(observed: grep of `*.py` and `*.js`, 2026-10-01).

## 2. The op `msg.question_terminologist` and its guard

The sandbox generates the op from the edge (observed: `rota/core/sandbox.py`
499-508). Its signature is `send(refs: list[str], question: str, round_no: int = 0)`.
The existing guards refuse three things for a Critic question:

1. An empty `question=`: "msg.question_terminologist needs question=" (the binder).
2. A third question on refs that overlap two answered ones (sandbox.py
   1322-1349). The door named is `schedule.unresolved`, which the Critic does
   not hold. The implementer adds a Critic door: "emit the verdict as written".
3. A ref to an id that does not exist (the generic ref check, reasoned).

The open-question guard (sandbox.py 1248-1260) is the Tester's only.

## 3. The brief lines

`critic/review.md` lines 28-30 ("A doubt about what a criterion should say
... in `reason=`.") become:
> A doubt about what a criterion should say is not a fail. Judge the criterion
> as written and emit the verdict. Then send `msg.question_terminologist`, the
> writer of the criteria: refs naming the criterion, and in `question=` the
> words you doubt and why. A doubt about whether the test encodes the
> criterion is `msg.challenge_tester` instead.

Tools: `critic/review.tools` appends `msg.question_terminologist`, and
`terminologist/question.tools` appends `msg.answer_critic`.

`terminologist/question.md`: "Three roles can ask you this" becomes "Four
roles", and `msg.answer_critic` joins the list. Add:
> The Critic asks about a criterion, not a term. Read the criterion against
> its ticket with `criteria.consult`. If the words say what the ticket asks,
> answer with refs to the criterion. If not, `msg.report_liaison` naming the
> criterion. Answering is not amending here too.

`rota/roles/prompts/critic/answer.md`, after the first paragraph:
> If the Terminologist answered a question about a criterion, your verdict on
> this batch already landed. Read the answer and end. Do not claim and do not
> emit again.

## 4. The case

Add to `tests/rota/cases/l1_judgement.yaml` after
`L1-CR-a-test-that-encodes-nothing-is-a-challenge`. The Critic cannot read the
item row, so the doubt comes from the criterion and the code alone. The
criterion says the invoices go. The test encodes that. The diff meets it. The
code's own comment says the invoices must survive.

```yaml
- id: L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist
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
    edit:
      src/billing/accounts.py: |
        # L1-CR-a-test-that-encodes-nothing-is-a-challenge's repo.edit, whole, two lines changed:
        #   from ..store import Record, delete, load, save
        #   delete("invoices", account_id)   # in close_account, before the tombstone
  fixture:
    items: [{id: <i1>, text: "closing an account", kind: in_scope, provenance: decided, approval: approved, approval_ver: 1, version: 1}]
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
    writes: {verdicts: {count: 1}}
    messages: [{to: terminologist, verb: question, count: 1, refs_include: [<c1>]}]
  forbidden: {recipients: [tester, developer]}
```

The pass writes the edit out in full. The store has `delete(table, id)`
(observed: `rota/testkit/samplerepo.py` 153). The kept comment "Closing does
not delete: the invoices have to survive for seven years" carries the doubt.

## 5. Structure tests

- `tests/rota/test_graph_reply.py`: the new answer edge and `msg.answer_critic`
  in `terminologist/question.tools` satisfy `test_an_asking_edge_has_its_reply`.
- `tests/rota/test_roles_doc.py`: in `rota/ROLES.md`, the Critic's line 210
  becomes "**Reaches** developer (challenge), terminologist (question), tester
  (challenge)". The Terminologist's line 134 adds "critic (answer)". Line 206,
  "a verdict and two challenges", becomes "a verdict, two challenges and a question".
- `tests/rota/test_edge_coverage.py`: the new case covers
  `(critic, terminologist, question)` through `expect.messages`. The answer
  edge `(terminologist, critic, answer)` has no case. Either the backlog set
  gains it in the same commit, or a second case with `inbound: {from: critic,
  to: terminologist, verb: question}` covers it. Recommended: the backlog, as
  the frame's ends-when names one case.
- The generated doc string ("Ask terminologist a question. The refs say what
  it is about") fits. No doc branch.
- Law 3: `derived_contacts('critic')` is `['developer', 'terminologist',
  'tester']`, and `derived_contacts('terminologist')` includes `critic`
  (observed: `rota/design/graph.py` 142, run 2026-10-01 15:27). Both edges
  derive by law, with no `contact_exceptions` entry.

## 6. Re-records owed

Eight, plus the new case (observed: grep of `tests/rota/cases/*.yaml`, 2026-10-01).

The Critic's `review` brief and tools change:
1. `ACT-CR-quote-the-tests-code` (`l1_acts.yaml` 315)
2. `L1-CR-pass-a-conforming-diff` (`l1_judgement.yaml` 6)
3. `L1-CR-fail-names-its-criterion` (`l1_judgement.yaml` 70)
4. `L1-CR-a-test-that-encodes-nothing-is-a-challenge` (`l1_judgement.yaml` 296)
5. `L3-a-failed-verdict-turns-into-a-fix` (`l3_handoffs.yaml` 128)

The Terminologist's `question` brief and tools change:
6. `L1-TE-answer-a-term-question` (`l1_terminologist.yaml` 51)
7. `L1-TE-answer-the-architects-question` (`l1_answers.yaml` 228)

The Critic's `answer` brief changes:
8. `L1-CR-finish-the-review-with-the-answer-in-hand` (`l1_answers.yaml` 265)

## 7. Risks

1. The answer reaches the Critic after its verdict. Re-review is not wanted,
   and a second `verdicts.emit` has no refusal today (observed: `verdicts_emit`,
   2026-10-01), so the `answer` brief ends the session. The implementer checks
   that a session with no writes commits on an answer wake.
2. Case 2 may send a needless question; its `forbidden.recipients` gains `terminologist`.
3. Case 4 may drift to the Terminologist door; the brief gives each door one sentence.
4. A wrong criterion reaches the Liaison by report, not a repair: `criterion_repair`
   wakes on a Tester's question only (observed: `predicates.py` 1122). Widening it is a later frame.

## 8. Open questions

None. The edge is Roman's ruling, and the verdict order is settled.
