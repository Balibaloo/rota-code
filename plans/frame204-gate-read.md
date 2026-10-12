# Frame 204, the gate at 882aa65e: five seat cases dropped

Read on 2026-10-12 02:54, read-only, by an Opus agent of the meta workflow.
Sources: `C:\Users\roman\rota_g204\gate204.out`, the register
`C:\Users\roman\rota_g204\tests\rota\cassettes.db` opened `mode=ro`
(`case_runs` and `cassettes`), and `git diff 40cd2715 882aa65e` on the
worktree. No model was called. The statements are about the rota workflow,
the seats, unless they say otherwise.

## Summary

| Case | Before | At 882aa65e | Cause | In the pass? |
|---|---|---|---|---|
| `L1-AR-route-an-escalation` | 5/5 (prompt `dff145b8`), 4/5 at 13:01 (`224945df`) | 3/5, two loads | an older lure: `findings.find` then `msg.answer_developer`, which the answer door then steers | no, a perturbation of the prompt by the kind sentence |
| `L1-TS-a-criterion-no-machine-could-check-is-vision_keepers` | 4/5 (`18597259`) | 2/5 | the new sentence in `tester/tests_missing.md` | yes, pass 1b |
| `L1-TS-an-outside-fact-is-the-researchers` | 5/5 (`18597259`) | 3/5 | the same sentence, and the literal door accepts the guessed string | yes, pass 1b and pass 1 |
| `L1-TS-a-criterion-that-contradicts-the-request-goes-back` | 5/5 | 5/5, red on the follow check | the encode door offers a triage the triage door refuses | no, the door is from 2026-10-05 |
| `L1-VK-reconcile-the-readme` | 1/1 (`8b7e4031`) | 0/1 | the word "finding" became "conflict" in `vision_keeper/reconcile.md` | yes, pass 1b |

One fix covers both TS seat drops. The other three causes need one fix each.

## 1. The runs, turn by turn

The current runs are load `qwen3:8b@248856`, 2026-10-12 02:48 (observed:
`case_runs` by `load_id`). The TS cases write three identical rows per run,
so five runs show as fifteen rows (observed: duplicate transcripts).

### `L1-AR-route-an-escalation`, 3 of 5

The case expects `msg.challenge_vision_keeper` or `msg.propose_vision_keeper`.
The escalation carries `[<b1>, <k1>]` and no finding.

- Run 2, failed. Turn 1: `findings.find(id="fnd_0001", constraint_id=k, status="violated", grain="export")`, accepted. Turn 2: `msg.answer_developer(refs=[b, k])`. The door refused: "refs=['b_0d3177', 'k_ad1752'] add no row to the refs of m_in ... This session wrote fnd_0001. Send msg.answer_developer(refs=['fnd_0001'])." Turn 3: the seat sent exactly that, and it landed. End: prose, "This session is complete." It wrote `findings` 1 and sent `developer/answer` (observed: transcript, run 2).
- Run 5, failed. The same shape: `findings.find` twice, `msg.answer_developer(refs=[b, k])` refused with the same offer, then `msg.answer_developer(refs=[fnd])`. End: prose, "No further action" (observed: transcript, run 5).
- Passing runs: run 1, `findings.find` then `msg.challenge_vision_keeper`. Run 3, `findings.find`, `msg.challenge_vision_keeper`, then the same answer pair. Run 4, `decisions.search`, `model.amend` refused as a second constraint, then `msg.challenge_vision_keeper` (observed: transcripts).

The same prompt `330ba472` on load 248855 at 2026-10-11 23:03 gave the same five runs, 3 of 5 (observed: `case_runs`). The failed shape is older than the pass: run 1 at 13:01 on prompt `224945df` called `findings.find` and then `msg.answer_developer`, 4 of 5 (observed: `case_runs`, load 248850).

### `L1-TS-a-criterion-no-machine-could-check-is-vision_keepers`, 2 of 5

The case expects a question to the Terminologist or the Vision Keeper and forbids a write to `tests`.

- Run 1, failed. `tests.triage(verdict='encodable')`, then `tests.encode` with a body that imports `export_file` from `export` and asserts `is not None`, `isinstance(..., str)` and `"finance" in export_file()`. Both landed. End: prose, "No further action is needed." Wrote `tests` 1, sent nothing.
- Run 3, failed. The same, with two assertions on `export_file()` and no string literal. Both calls landed. End: prose.
- Run 5, failed. The same, with `export_file().is_readable()` and `.is_well_formed()`. Both landed. End: prose.
- Passing runs 2 and 4: `encodable`, then a body of `assert True`. The constant door refused: "every assertion here is on a constant ... that is tests.triage verdict='cannot'". The seat then sent `cannot` and `msg.question_terminologist` (observed: transcripts).

Before the pass, all five runs on prompt `18597259` at 15:43 first encoded `assert True`, were refused, and four routed. The fifth failed on a body that did not parse (observed: `case_runs`, load 248851).

### `L1-TS-an-outside-fact-is-the-researchers`, 3 of 5

The case expects a question to the Terminologist or the Researcher and forbids a write to `tests`.

- Run 2, failed. `tests.triage(verdict='encodable')`, then `tests.encode` with `from webhook import sign` and `assert "signature" in sign({"data": "example"})`. Both landed. Wrote `ledger` 1 and `tests` 1. The seat called no `ledger.log`, so the literal door wrote the row (observed: `called` lists no `ledger.log`; reasoned: pass 1 makes the literal door stage its own `invented` row). End: prose, "now ready to be run."
- Run 4, failed. The same, with `sign_webhook()` and `startswith("sha256=")`. Wrote `ledger` 1 and `tests` 1. End: prose.
- Passing runs 1, 3, 5: `encodable`, `assert True` refused by the constant door, then `cannot` and `msg.question_terminologist`. Run 3 also wrote its own tool result, which the case reads as a pass (observed: transcripts).

Before the pass, all five runs on prompt `18597259` encoded `assert True` first and routed (observed: `case_runs`, load 248851).

### `L1-TS-a-criterion-that-contradicts-the-request-goes-back`, 5 of 5, red

The seat passes 5 of 5. The test is red on the frame 144 follow check in `tests/rota/conftest.py` (observed: `gate204.out`).

- Run 1 sent `tests.triage(verdict='encodable')` and `tests.encode` in one reply. The triage door refused: "c_a73c75 says 'returns' and s_a72bbf says 'prints'. Send tests.triage(... verdict='contradicts_request' ...)". The encode door then refused: "c_a73c75 has no triage verdict from you yet. Call tests.triage(criterion_id='c_a73c75', verdict='encodable') and then tests.encode in the same reply." The follow check replayed that offer, and the triage door refused it. Turn 2: `contradicts_request` and a second `encode`, which the door refused as routed. End: prose. The question to the Terminologist was sent (observed: transcript, run 1; `gate204.out`).
- Runs 2 to 5: `encodable` refused, then `contradicts_request`, then prose (observed: transcripts).

No run of this case before 882aa65e sent the encode in the same reply as a refused triage (observed: a scan of every load since 248835 for "no triage verdict", 0 hits).

### `L1-VK-reconcile-the-readme`, 0 of 1

The case expects 1 to 6 `ledger` rows and one survey record.

- Run 1, failed. Turn 1: reads (`code.probe`, `code.prose`, `problem.baseline`, `problem.consult`). Turn 2, after the README's text and `problem.baseline` `[]`: `code.probe(pattern='billing')`, `code.prose`, `problem.consult()`, `surveys.attest(outcome="none_found", citations=["README.md"])`. End: the attest. Wrote `survey_records` 1 and `ledger` 0 (observed: the cassette completion, row 52718; transcript).
- Before the pass, run 1 on prompt `8b7e4031` called `ledger.log` twice on the README's claims and attested (observed: `case_runs`, load 248851).

## 2. The causes

The system text of each mode differs from the text before the pass only in
the lines below (observed: `difflib` over the last two distinct `system`
values in `cassettes` per mode).

- Architect `escalate`: the base sentence "Its `kind=` is one word: `invented`, `default`, `scope`, `conflict`, `blocked`, `fault` or `other`." and the tool line `ledger.log(about_ref, about_table, assumption, kind)`.
- Tester `tests_missing`: the same kind sentence, the same tool line, and the edit at `tests_missing.md:46`.
- Vision Keeper `reconcile`: "finding" to "conflict", `kind="conflict"` in the dictated call, and the tool line.

### `L1-AR-route-an-escalation`: outside the pass

The cause is an older lure in the escalate mode (reasoned: the failed shape
ran at 13:01 before the pass, and the pass changed no line about routing).
No sentence of the pass is followed: the failed runs call no `ledger.log`.
The kind sentence moves the 8B seat's sampling, and the case sits at its
threshold of 4 (reasoned: 4/5, 5/5, 3/5 on three prompts, and each prompt
replays the same runs on two loads).

Two older texts carry the failed runs. First, `escalate.md` pairs
`findings.find` with `msg.answer_developer`: "`findings.find` with the
finding's own id and `status='satisfied'`, and say so with
`msg.answer_developer`". The seats call `findings.find` with
`status='violated'` on an escalation with no finding, which the same bullet
excludes: "Without a finding in the refs, this is not the case". Second, the
answer door's refusal offers only `msg.answer_developer(refs=['fnd_...'])`,
and both failed runs take that offer (observed: runs 2 and 5).

### `L1-TS-a-criterion-no-machine-could-check-is-vision_keepers`: the pass

The cause is pass 1b's sentence in `tester/tests_missing.md:46` (reasoned:
the only change in the system text besides the kind sentence, and every
failed run does what the sentence says). The seat followed:

> A string the test chooses that nothing in the material says -- a sample
> name, a prompt's wording -- is an assumption. Encode the test:
> `tests.encode` writes the assumption to the ledger for you.

"Encode the test" is an imperative in the paragraph just before the
`cannot` paragraph. "Writes the assumption to the ledger for you" tells the
seat that a value it chose is covered. The old text, "`ledger.log` it
against the criterion, then encode", put a step before the encode. Before
the pass, the seat wrote `assert True`, and the constant door turned it to
`cannot`. After the pass, three of five runs write a call to an invented
function, which no door refuses (observed: transcripts). Runs 3 and 5 hold
no string literal, so the imperative and not the literal door explains
them (reasoned).

### `L1-TS-an-outside-fact-is-the-researchers`: the pass

The cause is the same sentence (reasoned: as above). The literal door of
pass 1 adds to it: the guessed header string `"signature"` lands as an
`invented` row, and the encode is accepted (observed: `wrote` `ledger` 1 with
no `ledger.log` call; reasoned: pass 1's literal door). The case's own note
names this failure: "Encoding a remembered header name is the failure".

### `L1-TS-a-criterion-that-contradicts-the-request-goes-back`: outside the pass

The cause is the encode door at `api.py:6120`, from c888968b of 2026-10-05
(observed: `git blame`). When the triage in the same reply was refused as
`contradicts_request`, the encode door still offers
`tests.triage(verdict='encodable')`, and that offer can never land. Run 1's
shape, triage and encode in one reply, is new at 882aa65e (observed: 0 hits
before). The pass's "Encode the test" may have pulled the encode into the
same reply (reasoned, not tested). The defect itself is the door's.

### `L1-VK-reconcile-the-readme`: the pass

The cause is pass 1b's word change in `vision_keeper/reconcile.md:13`
(reasoned: the only change in the system text, and the seat attested
`none_found`). The bullet now reads:

> the README says something the code did not show, or contradicts the
> account — that is a conflict, and you cannot rule on it

The fixture's account is empty, so nothing in the account contradicts the
README. "Conflict" names a contradiction, and the seat found none.
"Finding" covered a claim the code did not show. The case runs once, so one
replay decides it (observed: `runs: 1` in `l1_survey.yaml`). An interview of
the seat at this turn would confirm the reading.

## 3. The fixes

1. TS, both seat drops, one fix: rewrite `tests_missing.md:46` with no
   imperative, and bound it. Example: "A string the test chooses ... is an
   assumption, and `tests.encode` logs it for you. A function or a format
   the material does not name is no assumption: that is `cannot`." Re-record
   the three TS cases and `ACT-TS-*` (reasoned: one sentence causes both).
2. TS, the literal door: a guessed literal on a criterion that names
   somebody else's spec should not land as `invented`. Hold this until fix 1
   is re-recorded, because fix 1 may close it alone (reasoned).
3. VK reconcile: keep `kind="conflict"` in the dictated call, and give the
   bullet back a word that covers a missing claim. Example: "that is a
   disagreement ... log it with `kind="conflict"`". Re-record the case
   (reasoned).
4. TS contradicts, outside the pass: the encode door at `api.py:6120` reads
   the triage refusal of the same reply, and offers that refusal's call
   instead of `encodable`. A new frame, because the door is older than frame
   204 (reasoned).
5. AR route, outside the pass: a new frame, not frame 204's. The shortest
   fix is the answer door's refusal: when the escalation's refs hold a
   constraint, name `msg.challenge_vision_keeper` beside the
   `answer_developer` offer. An interview of run 2's turn 2 should come
   before a second brief shape (reasoned: the CLAUDE.md rule of 2026-10-02).

Fixes 1 and 3 belong to frame 204's next pass. Fixes 4 and 5 are new frames,
and frame 204's acceptance can read those two cases as outside its cause.
