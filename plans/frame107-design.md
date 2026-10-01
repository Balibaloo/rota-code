# Frame 107, the Critic's doubt reaches the Terminologist: design record, revision 3

Rota workflow. Opus scope read, 2026-10-01 15:27. Ruled: Roman, 2026-10-01 15:25:
the doubt goes to the Terminologist, and the verdict lands first, as written.
Revision 3 folds the short review's fixes into pass 1, which builds them.

## 1. The edge: (a), a `question`

Choose (a), `critic -> terminologist question`, `expects: answer`. It reuses
the Terminologist's `question` mode and the Critic's `answer` mode, and each
brief needs one paragraph (reasoned). Option (b) needs a new Terminologist
`challenge` mode, because the verb names the mode a message wakes (observed:
`rota/roles/prompts.py` `compose`). The binder requires words in `question=`,
and the doubt is a sentence.

`rota/design/graph.json` gains two edges in the field shape of
`developer -> terminologist question` and `terminologist -> developer answer`:

- `critic -> terminologist`, `messages`, `v: question`, `expects: answer`,
  `rows: single`, `prose: question`, after `critic -> tester challenge`.
- `terminologist -> critic`, `messages`, `v: answer`, `rows: single`, after
  `terminologist -> architect answer`. Its `n` reads "the criterion stands, or
  the report it took", because a wrong criterion goes to the Liaison by report.

Each label names frame 107 and the ruling. The `silent_channels` entries
`critic -> terminologist` and `terminologist -> critic` go. No code reads them
(observed: grep of the tree outside `.venv` and `.git`, 2026-10-01).

No op goes in `rota/roles/api.py`. The sandbox generates
`msg.question_terminologist` and `msg.answer_critic` from the edges (observed:
`rota/core/sandbox.py` 497-508).

## 2. The tools and the guards

Tool lines: `critic/review.tools` gains `msg.question_terminologist`.
`terminologist/question.tools` and `terminologist/unresolved.tools` gain
`msg.answer_critic`. The `unresolved` line is a pass 1 addition:
`test_an_unresolved_rung_can_answer_every_asker_that_reaches_it` requires it,
because the new answer edge makes the Terminologist a rung for the Critic.

Guards in `rota/core/sandbox.py`:

1. An empty `question=` is refused by the binder, as before.
2. The overlap refusal, a third question on refs that two answers already
   covered, gains a Critic branch. Its way out reads "the verdict stands as
   written: end the session". The Critic holds no `schedule.unresolved`.
3. The Terminologist's answer guard names `msg.report_{recipient}`. For the
   Critic it now names `msg.report_liaison`, the only report edge the
   Terminologist holds. The other recipients keep their text.

A second verdict is refused in `verdicts.emit` (`rota/roles/api.py`). The
verdict id is the role, the batch and the head commit. A staged or stored row
with that id refuses the call: "your verdict on batch b1 at this commit
already landed, and one commit gets one verdict: end the session". A new head
commit gets its own verdict. The unit test is
`test_a_second_verdict_on_one_commit_is_refused` in `tests/rota/test_desk_guards.py`.

## 3. The brief lines

`critic/review.md`: frame 88's line that put the doubt in `reason=` becomes:
> A doubt about what a criterion should say is not a fail. Judge the criterion
> as written and emit the verdict. Then send the doubt to the Terminologist,
> the writer of the criteria, with `msg.question_terminologist`. The refs name
> the criterion. `question=` says the words you doubt and why. A doubt about
> whether the test encodes the criterion is `msg.challenge_tester` instead.

`critic/answer.md`: the header becomes "MODE: answer — a role answered a
message you sent." The prefix stays, because
`test_every_piece_names_its_own_mode` needs it. The first branch:
> If the Terminologist answered your question about a criterion, read the
> answer and end the session. Your verdict on this batch already landed. Do
> not claim, and do not emit a second verdict: the tool refuses it.

The Tester branch follows, with its claim and emit steps unchanged.

`terminologist/question.md`: "Three roles" becomes "Four roles", and
`msg.answer_critic` joins the list. One paragraph:
> The Critic asks about a criterion, not a term. You wrote the criteria. Read
> the criterion against its ticket with `criteria.consult`. The refs of your
> answer name the criterion. The answer says whether the criterion means what
> the test encodes, as the question quotes it. If the criterion means what its
> ticket asks, answer with `msg.answer_critic`. If it does not, send
> `msg.report_liaison` and name the criterion. Answering is not amending here too.

## 4. The case

`L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist` goes in
`tests/rota/cases/l1_judgement.yaml`, after
`L1-CR-a-test-that-encodes-nothing-is-a-challenge`. The Critic cannot read the
item row, so the doubt comes from the criterion and the code alone. The
criterion says the invoices go. The test encodes that. The diff meets it. The
code's own comment says the invoices must survive.

The repo edit is the sample `src/billing/accounts.py` in full, as the
challenge case writes it, with two lines changed: `delete` joins the store
import, and `delete("invoices", account_id)` runs before the tombstone. The
store has `delete(table, id)` (observed: `rota/testkit/samplerepo.py` 153).
The kept comment "Closing does not delete: the invoices have to survive for
seven years" carries the doubt.

The keys:

- `expect.writes.verdicts`: `count: 1` and `text_includes: ['"result": "pass"']`.
  The case runner has no field-value key, so the result is asserted as a
  substring of the row's JSON (observed: `rota/testkit/fixtures.py` 504-532).
- `expect.messages`: one `question` to `terminologist`, `refs_include: [<c1>]`.
- `forbidden.recipients`: `[tester, developer]`.

## 5. Structure tests

- `tests/rota/test_graph_reply.py`: the answer edge and `msg.answer_critic`
  satisfy `test_an_asking_edge_has_its_reply`.
- `rota/ROLES.md`: the Critic reaches "developer (challenge), terminologist
  (question), tester (challenge)". Its namespace line reads "a verdict, two
  challenges and a question". The Terminologist's line adds "critic (answer)".
- `rota/SYSTEM.md`: the table row, the "Critic's hole" paragraph and gap 2 say
  that gap 2 closes for the Terminologist only.
- `tests/rota/test_docs.py`: `test_critic_still_cannot_ask_anything` becomes
  `test_critic_asks_only_the_terminologist`.
- `tests/rota/test_t0_sandbox.py`: `test_s9_critic_namespace_is_review_plus_challenge`
  adds `msg.question_terminologist` to the Critic's outbound set.
- `tests/rota/test_edge_coverage.py`: the new case covers
  `(critic, terminologist, question)`. `BACKLOG` gains
  `(terminologist, critic, answer)`, which has no case.
- Law 3: `derived_contacts('critic')` is `['developer', 'terminologist',
  'tester']`, and `derived_contacts('terminologist')` includes `critic`.
  `assert_consistent` passes (observed: run by pass 1, 2026-10-01). Both edges
  derive by law, with no `contact_exceptions` entry.

## 6. Re-records owed

Nine (observed: grep of `tests/rota/cases/*.yaml`, 2026-10-01).

The Critic's `review` brief and tools change:
1. `ACT-CR-quote-the-tests-code` (`l1_acts.yaml`)
2. `L1-CR-pass-a-conforming-diff` (`l1_judgement.yaml`)
3. `L1-CR-fail-names-its-criterion` (`l1_judgement.yaml`)
4. `L1-CR-a-test-that-encodes-nothing-is-a-challenge` (`l1_judgement.yaml`)
5. `L3-a-failed-verdict-turns-into-a-fix` (`l3_handoffs.yaml`)

The Terminologist's `question` brief and tools change:
6. `L1-TE-answer-a-term-question` (`l1_terminologist.yaml`)
7. `L1-TE-answer-the-architects-question` (`l1_answers.yaml`)

The Critic's `answer` brief changes:
8. `L1-CR-finish-the-review-with-the-answer-in-hand` (`l1_answers.yaml`)

The new case:
9. `L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist`

Watch: `L1-TE-a-rung-for-a-question-the-principal-asked` reads
`terminologist/unresolved.tools`. The situational narrowing drops
`msg.answer_critic` on that wake, so it may stay green (reasoned).

## 7. Risks

1. The answer reaches the Critic after its verdict. The `answer` brief ends the
   session, and `verdicts.emit` refuses a second verdict. A session with no
   writes on an answer wake is not refused by any guard pass 1 found
   (reasoned: grep of `rota/core`, 2026-10-01). The walk confirms it.
2. Case 2 may send a needless question. Its `forbidden.recipients` may then
   gain `terminologist`.
3. Case 4 may drift to the Terminologist door. The brief gives each door one
   sentence.
4. A wrong criterion reaches the Liaison by report, not a repair:
   `criterion_repair` wakes on a Tester's question only (observed:
   `predicates.py` 1122). Widening it is a later frame.
5. The second-verdict refusal is new for every role that emits. A recorded
   case where a seat emits twice on one commit now reads a refusal. The gate
   shows such a case as stale or red.

## 8. Open questions

None on the design. The edge is Roman's ruling, and the verdict order is settled.
