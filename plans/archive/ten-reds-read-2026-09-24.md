# The ten known reds, read from their transcripts

Date: 2026-09-24. Written by the frame 82 read agent on Opus 5.5.

Frame 82, the ten known reds blind the gate, line 1. Meta workflow for every
statement about cases, the gate and the register. Rota workflow for every
statement about what a seat did.

## Summary

No case is a salt fault. No fixture and no check names an id literally that the
salt changes. Every hole in the ten cases goes through `fill`, and the checks
go through the same `fill`, so a fixture id and a check id move together
(observed: `rota/testkit/fixtures.py` `for_run` and `load_case`, 2026-09-24).
In three of the ten cases, run 1 fails with the unsalted ids as well:
`L1-CR-a-test-that-encodes-nothing-is-a-challenge`,
`L1-VK-reopen-after-an-election` and `L1-AR-survey-a-shared-helper`. The salt
did not make these faults. The salt made five runs of five different problems,
and five problems showed a fault that one reply had hidden (reasoned: frame 66
turned one replayed reply into five samples).

The classes: six brief faults, four check faults, zero salt faults. Two of the
check faults are in the fixture, which puts something in front of the seat that
the product would not put there. One of the brief faults also needs a door
text change.

Source of every tally: the register `tests/rota/cassettes.db`, table
`case_runs`, the rows of the gate replays at 2026-09-24 15:30 to 15:40, one row
per run number at the highest `seq` (observed: 2026-09-24 20:00). The tallies
match on all three replays of that hour. The tool-result lines come from the
`cassettes` table, `user` column.

## The ten cases

### 1. ACT-DV-edit-inside-the-function

- Ask: the Developer fixes `confirm()` so that it returns the default at EOF,
  and does not challenge the Tester.
- Record: 3 of 5 pass, 4 needed. Runs 1, 4 and 5 pass. Runs 2 and 3 fail with
  `forbidden call to msg.challenge_tester`. In run 2 the seat wrote the fix,
  called `code.commit`, got `"committed": true`, then called `tests.load`. The
  tool returned `"last_result": "fail"` with the old `SystemExit: 1` output and
  no `changed since this run, not run` key. The seat read the old red as its
  fix failing. It then sent `msg.escalate_architect` and
  `msg.challenge_tester`, quoting "Code src/ui.py after fix: catches EOFError".
- Class: check fault, in the fixture. The fixture seeds `test_runs.commit_sha`
  as `abc123`, which is no commit in the case's repository. `changed_since`
  reads an unknown sha as "the working tree alone". After a commit the working
  tree is clean, so `tests.load` says nothing changed. In production the run
  names a real commit, and `tests.load` says "changed since this run, not
  run". So the case withholds the one fact that the product gives the seat.
- Fix: in `tests/rota/cases/l1_acts.yaml`, seed the run with
  `commit_sha: HEAD`. In `rota/testkit/fixtures.py`, near line 787, resolve
  `HEAD` in `test_runs.commit_sha` to the base commit, the same way the code
  resolves `touch_strays.commit_sha`. The base commit is the commit before the
  batch's `edit` commit, because the red run is a statement about that commit.
- Mark: (observed: run 2's cassettes, the `tests.load` result after
  `code.commit`, 2026-09-24) and (reasoned: `rota/core/worktrees.py`
  `changed_since` docstring, "An unknown `sha` ... counts the working tree
  alone").

### 2. L1-AR-a-dead-end-is-reported-not-sat-on

- Ask: the Architect in `exhausted` finds none of the three shapes, and reports
  the stall to the Liaison with the batch in refs.
- Record: 2 of 5 pass, 3 needed. All five runs take the same path. The seat
  calls `model.amend` with a headline that restates the constraint, and the
  door refuses: "cn_... already governs this subject". The seat then calls
  `msg.challenge_vision_keeper` two to four times with the constraint's own id
  twice in refs, and the door refuses the quotes. Runs 1 and 2 then fall
  through to `msg.report_liaison` with the batch id. Runs 3, 4 and 5 stop after
  the refused challenges, and run 5 sends `msg.answer_developer` instead.
- Class: brief fault. `rota/roles/prompts/architect/exhausted.md` puts the three
  shapes first, and the seat reads the criterion ("peaks under 64MB") against
  the constraint ("never buffer the whole set") as a contradiction. The brief
  does not say that "contradict each other" means two constraint rows. It does
  not say what to do after a door refuses. The report is the last paragraph, so
  the seat reaches it only by chance.
- Fix: in `rota/roles/prompts/architect/exhausted.md`, state that a
  contradiction is two constraint rows that cannot both hold. State that a
  criterion that a constraint allows is not a contradiction. Add: "If a door
  refuses you, send `msg.report_liaison` with the batch id in refs, and stop."
- Mark: (observed: runs 1 to 5 of the replay at 2026-09-24 15:39, the errors
  list of each run).

### 3. L1-AR-survey-a-shared-helper

- Ask: the Architect surveys `src/billing` and writes 1 to 9 constraints that
  name a surface of the area.
- Record: 0 of 1 pass, 1 needed. The case has no hole, so it runs once. The seat
  called `model.amend` eleven times, one call per public name: "Charge class",
  "total_of function", "prorate function", "BillingAccount class",
  "open_account function", "balance function", "Invoice class",
  "issue_invoice function", "void function", "renew function",
  "upgrade function". The door refused "void function" as a label. Ten
  constraints landed, and the check allows nine. The older runs 2 to 5 in the
  register made the same eleven calls with one more refusal, so nine landed and
  they passed.
- Class: brief fault. The survey brief lets the seat write an inventory of
  names as constraints. No constraint says what callers rely on. The case's own
  comment names the rounding of `total_of` as the thing to protect, and no
  headline says it. The range "1..9" caught the inventory by one row, and the
  pass or fail depends only on how many public names the area has.
- Fix: in `rota/roles/prompts/architect/survey.md`, say that a constraint is
  what a caller relies on, not one row for each name. Say that a headline made
  of a name and "function" or "class" is a label. In `rota/roles/api.py`
  `model_amend`, near line 2203, refuse a headline whose words are one
  identifier plus "function", "class", "method" or "module", as the door
  already refuses "void function".
- Mark: (observed: the transcript of run 1, the replay at 2026-09-24 15:39,
  `wrote: {"constraints": 10}`).

### 4. L1-CR-a-test-that-encodes-nothing-is-a-challenge

- Ask: the Critic sees a test that asserts only `is not None`, and challenges
  the Tester with the criterion and the test in refs. It writes no verdict.
- Record: 1 of 5 pass, 3 needed. Run 1, unsalted, fails. Runs 1, 2, 3 and 5
  call `verdicts.claim_encodes(encodes=True)` and `verdicts.emit`, and runs 1,
  3 and 5 try `msg.challenge_developer`. Every failing run names the same
  distraction first. Run 1: "the diff removes the `BillingAccount` dataclass and
  related functions (`open_account`, `balance`)". Run 3 tries to challenge the
  removed lines with refs `b_...:src/billing/accounts.py:1:3`. Only run 4 sends
  `msg.challenge_tester`.
- Class: check fault, in the fixture. The case's `repo.edit` replaces all of
  `src/billing/accounts.py` with only `close_account`. The sample repository's
  file also holds `BillingAccount`, `open_account` and `balance`
  (`rota/testkit/samplerepo.py`, line 345). So the diff deletes three
  definitions that nobody asked to delete. The Critic sees a real unrequested
  change and reviews that change, not the test.
- Fix: in `tests/rota/cases/l1_judgement.yaml`, write the `edit` as the whole
  sample file with only the body of `close_account` changed to set
  `state = "tombstoned"`. Keep every other definition.
- Mark: (observed: runs 1, 3 and 5 of the replay at 2026-09-24 15:39, their
  first reply) and (observed: `rota/testkit/samplerepo.py` line 345,
  2026-09-24).

### 5. L1-DV-apply-the-answer-and-carry-on

- Ask: the Developer receives the Terminologist's answer on "display currency",
  and writes and commits the code.
- Record: 2 of 5 pass, 4 needed. Runs 1 and 3 write
  `def format_amount(amount): return f"${amount:.2f}"` over the whole file and
  commit. Runs 2, 4 and 5 call `code.write` with the criterion's sentence as the
  file text: `"amounts are shown in the display currency, in
  src/notify/formatting.py"`. The door refuses three times, "is not valid
  Python", and the seat ends. No run calls `code.source` before it writes.
- Class: brief fault. `rota/roles/prompts/developer/answer.md` says "Carrying
  on means `code.write` and `code.commit`", and says nothing about reading the
  file first. The seat has a criterion and an answer and no code, so it writes
  the criterion. The passing runs also delete `truncate` and `pluralise` from
  the file, and the check passes them (reasoned: a whole-file write with
  `start=0, end=-1` replaces the sample file).
- Fix: in `rota/roles/prompts/developer/answer.md`, add before the
  `code.write` paragraph: "Read the file with `code.source` first. `code.write`
  takes Python source, not the criterion's words." Optionally, in
  `tests/rota/cases/l1_answers.yaml`, add a check that `truncate` is still in
  the file.
- Mark: (observed: runs 1 to 5 of the replay at 2026-09-24 15:39).

### 6. L1-LI-a-question-about-the-page-is-answered-not-ruled

- Ask: the principal asks "what does line 3 mean, where did that come from?".
  The Liaison answers with `ask`, and writes no ruling.
- Record: 3 of 5 pass, 4 needed. Every run calls `rulings.rule` with a
  `rulings` map. The passing runs 1, 2 and 3 also pass `ask="Line 3 assumes the
  bill is one number..."`, and the door then sends a converse and writes no
  ruling. The failing runs 4 and 5 pass only `rulings={"1": "approve", "2":
  "approve", "3": "contest"}`, and a ruling lands. So every run rules lines 1
  and 2 as approved on a reply that approves nothing.
- Class: brief fault. `rota/roles/prompts/liaison/landing.md` describes the
  question case in prose in the middle. It ends with "Call `rulings.rule` once,
  with `rulings` for every line", which pulls every run to a map. The passes
  depend on the seat adding `ask` beside the map.
- Fix: in `rota/roles/prompts/liaison/landing.md`, put the question case first.
  Give the exact call: `rulings.rule(ask="...")`, with no `rulings`. Limit the
  closing line to a reply that is a ruling.
- Mark: (observed: runs 1 to 5 of the replay at 2026-09-24 15:39).

### 7. L1-TE-answer-a-term-question

- Ask: the Developer asks which "account" a transaction row hangs off. The
  Terminologist answers with `msg.answer_developer`, and gives the two senses.
- Record: 3 of 5 pass, 4 needed. Runs 1, 2 and 3 call
  `msg.answer_developer(refs=[g1, g2])`. Runs 4 and 5 write the answer as prose
  and call no send. Run 4 prose: "The `account` in the transaction row refers
  to the **login identity**", which also resolves the collision. The runs carry
  no error, so the runner did not nudge them.
- Class: brief fault. `rota/roles/prompts/terminologist/question.md` says
  "answer with refs pointing at the term ids" and then explains that the
  channel is fixed. It never names the call as the act. The prose reply reaches
  nobody.
- Fix: in `rota/roles/prompts/terminologist/question.md`, write the act first:
  "Send the answer with `msg.answer_<asker>`, refs to every sense of the term.
  A reply in prose reaches nobody." Add: "Two senses is the answer. Do not pick
  one."
- Mark: (observed: runs 4 and 5 of the replay at 2026-09-24 15:39).

### 8. L1-TE-challenge-an-unusable-item

- Ask: the Liaison asks about the item "make the thing work properly". The
  Terminologist replies with `msg.answer_liaison`.
- Record: 3 of 5 pass, 4 needed. Runs 1, 3 and 5 call `msg.answer_liaison`.
  Runs 2 and 4 call `msg.report_liaison`: "there is no term to define ... I
  report this to the liaison". The glossary in the fixture is empty.
- Class: check fault. `rota/roles/prompts/terminologist/ask.md` says: "If your
  artefact does not carry it, say so — `msg.report_liaison`." The glossary
  carries nothing, so the failing runs follow the brief. The check accepts only
  `answer`. No run challenges the item as unusable, although the case name asks
  for that.
- Fix: in `tests/rota/cases/l1_terminologist.yaml`, accept either verb with
  `any_of`: `{to: liaison, verb: answer}` or `{to: liaison, verb: report}`,
  each with `refs_include: [<i1>]`. If Roman wants the challenge that the name
  promises, that is a ruling and a new case, not this repair.
- Mark: (observed: runs 2 and 4 of the replay at 2026-09-24 15:39) and
  (reasoned: the brief's own `report_liaison` line covers an empty glossary).

### 9. L1-TS-apply-a-term-and-write-the-test

- Ask: the Tester receives the answer on "account", and encodes one test for
  the criterion.
- Record: 2 of 5 pass, 4 needed. Every run passes the glossary id as
  `criterion_id`, because the inbound's only ref is `<g1>`. Every run tries to
  test the glossary, not the program:
  `assert lookup('account')['sense_short'] == '...'`. The door names the right
  criterion id in its refusal, "criteria rows are ['c_592a68']". Runs 1 and 4
  retry with the criterion id and a glossary test lands. Runs 2, 3 and 5 write
  `assert True`, the door refuses a constant, and they end with "named an act
  and did not perform it".
- Class: brief fault. `rota/roles/prompts/tester/answer.md` says "Applying it is
  `tests.encode`" and does not say which row the test belongs to. The fixture
  also gives the seat nothing to call: the criterion has no `surface_refs` and
  the case has no `repo`. So the passing runs pass with a test of the glossary,
  and the check counts it.
- Fix: in `rota/roles/prompts/tester/answer.md`, add: "The answer names a term.
  Find the criterion that carries the term with `criteria.load`. Encode the
  test against that criterion's id, and call the function its surface names."
  In `tests/rota/cases/l1_answers.yaml`, give the case a `repo` with a batch
  and give `<c1>` `surface_refs: '["src/billing/accounts.py::close_account"]'`.
- Mark: (observed: runs 1 to 5 of the replay at 2026-09-24 15:39).

### 10. L1-VK-reopen-after-an-election

- Ask: the Developer elects after a revocation. The Vision Keeper sends
  `msg.reopen_developer` with the item.
- Record: 3 of 5 pass, 4 needed. Run 1, unsalted, fails. Every run first calls
  `msg.reopen_developer(refs=[b1])` with the batch id from the inbound. The door
  refuses: "b_... is not an item. A reopen names the approved item that changed
  under the batch". The fixture's item is `approval: draft`, which is the
  correct state after a revocation. Runs 2, 4 and 5 retry with the item id and
  the door accepts it. Runs 1 and 3 read the refusal and stop. Run 3: "Since no
  item is approved, the developer must first finalize the draft item".
- Class: brief fault, with a door text fault. `rota/roles/prompts/vision_keeper/elect.md`
  says "with the item as it now stands" and does not say that refs carry the
  item id. The door's refusal says "approved item", and the item after a
  revocation is a draft, so the refusal points the seat away from the only
  item it has.
- Fix: in `rota/roles/prompts/vision_keeper/elect.md`, write: "Send
  `msg.reopen_developer` with `refs=[the item id]`. The batch id alone is
  refused." In `rota/core/sandbox.py`, line 1056, drop "approved" from the
  refusal: "A reopen names the item that changed under the batch".
- Mark: (observed: runs 1 and 3 of the replay at 2026-09-24 15:39).

## The eleventh: test_map.py::test_a_shared_file_name_lists_the_candidates

Flaky, not wrong. The test calls `map_tool.main(["file", "__init__.py"])`,
which parses the live `rota/` tree with no cache. It passed alone
(observed: 2026-09-24, before 20:09, 1 passed in 8.71 s), and no test writes under
`rota/` (observed: a grep of `tests/rota`, 2026-09-24). The gate log keeps no
traceback, so the cause is not observed. The likely cause is a second session
that edits a `rota/*.py` file while the gate parses it (reasoned: frames 83
and 82 share one checkout). Fix: give the test the `index` fixture and call
`query_file`. Or mark the test flaky with that reason in
`tests/rota/test_map.py`.

## The fixes by file

- `rota/roles/prompts/architect/exhausted.md`: case 2.
- `rota/roles/prompts/architect/survey.md`: case 3.
- `rota/roles/api.py`, `model_amend` near line 2203: case 3, the label guard.
- `rota/roles/prompts/developer/answer.md`: case 5.
- `rota/roles/prompts/liaison/landing.md`: case 6.
- `rota/roles/prompts/terminologist/question.md`: case 7.
- `rota/roles/prompts/tester/answer.md`: case 9.
- `rota/roles/prompts/vision_keeper/elect.md`: case 10.
- `rota/core/sandbox.py`, line 1056: case 10, the refusal text.
- `rota/testkit/fixtures.py`, near line 787: case 1, resolve `HEAD` in
  `test_runs.commit_sha`.
- `tests/rota/cases/l1_acts.yaml`: case 1, `commit_sha: HEAD`.
- `tests/rota/cases/l1_judgement.yaml`: case 4, keep the whole file in the
  `edit`.
- `tests/rota/cases/l1_answers.yaml`: case 9, a `repo` and `surface_refs`.
  Optionally case 5, a check that `truncate` survives.
- `tests/rota/cases/l1_terminologist.yaml`: case 8, `any_of` answer or report.
- `tests/rota/test_map.py`: the eleventh.

## Re-records after the fix

Re-record nine of the ten by exact id: cases 1, 2, 3, 4, 5, 6, 7, 9 and 10.
Each fix changes the prompt, a tool result or the diff that the seat reads, so
the old cassettes stop being evidence.

Case 8 needs no re-record. Its fix changes only the check, so the gate replays
the recorded runs against the new check.

A brief change moves every case of the same mode (reasoned: frame 81 measured
one brief change that turned a second case red). Re-record the other cases of
these modes as well, and compare each with its tally before the change:
`architect/exhausted`, `architect/survey`, `developer/answer`,
`liaison/landing`, `terminologist/question`, `tester/answer` and
`vision_keeper/elect`. The door text change in `rota/core/sandbox.py` reaches
every case that sends a refused `msg.reopen_developer`. The `HEAD` resolution
in `rota/testkit/fixtures.py` reaches only a case that seeds `commit_sha: HEAD`
in `test_runs`, so today it reaches case 1 alone.

## Revision 2, after the design review (observed: the reviewer on Opus 5.5, 87.4k on the harness line, 43 tool calls, 8.6 minutes, 2026-09-24 20:22)

The classes hold. These corrections win over the text above.

- Case 1, `ACT-DV`: the red run belongs to the edit commit, not the base. Fix: beside the `touch_strays` line in `rota/testkit/fixtures.py`, `UPDATE test_runs SET commit_sha = ? WHERE batch_id = ? AND commit_sha = 'HEAD'` with the edit sha. The two `tick: tests_failing` cases in `l1_developer.yaml` (lines 102, 237) carry the same fault and move after, one at a time, each with its own re-record.
- Case 4, `CR`: the replacement edit also calls `rec.data` and deletes names `src/billing/__init__.py` imports. Fix: copy the sample file whole and change one line in `close_account`, `rec.values["state"] = "tombstoned"`.
- Case 3, `AR-survey`: "void function" was refused by `_NOT_VOCABULARY`, not by a name-plus-kind rule. No new guard in `model_amend`. Land the survey brief line first and re-record the six survey cases; decide on a guard after.
- Case 8, `TE-challenge`: `report` is the act `ask.md` asks for on an empty glossary. Fix: expect `{to: liaison, verb: report}` only; do not accept `answer` beside it.
- Case 9, `TS-apply-a-term`: give the fixture a repo and `surface_refs`, add `<c1>` to the inbound `body_refs`, drop the `criteria.load` sentence; run 2 wrote a constant comparison, not `assert True`.
- Every brief change is one bolded headline act, never a paragraph (observed: frame 81, a paragraph 2 of 5, two sentences 0 of 5, a headline green). `liaison/landing.md` gets one line, not a rewrite.
- The map test: build the index from a small tree in `tmp_path` with two `__init__.py` files through `build_index(root)`; the `index` fixture still reads the live folder.
- Re-record list, beyond the ten: `L2-AR-place-a-block-developer-could-not`; the five survey cases `an-area-for-its-commitments`, `a-signature-callers-rely-on`, `an-exception-contract`, `a-patch-seam`, `an-exported-name`; the six landing cases `plain-agreement-approves-every-line`, `a-named-line-is-contested-and-the-rest-approved`, `a-correction-in-a-sentence-contests-the-line-it-is-about`, `a-question-then-a-statement-at-the-confirm-is-the-question`, `approve-one-line-only-approves-that-line-alone`, `a-long-page-is-ruled-without-the-rows`; and `L1-TE-answer-the-architects-question`. Record each one's tally before the change.
- Order: all changes land in one pass. The landing line re-records with its six siblings and is judged against their tallies before the change.
