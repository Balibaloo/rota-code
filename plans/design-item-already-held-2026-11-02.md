# Design: what ends an item the code already satisfies (2026-11-02)

A design page by C76 step 3b for frame 360, after `plans/dry2-wall1-read-2026-11-02.md`. Read-only at 3adb4726 on `rota/foundation`. The dry2w2 and dry2w3 databases of session 208997ee were copied into this session's scratchpad, and the queries ran on the copies. No file of the repository changed except this page.

## Result

Recommend shape A, the read's proposal: an unchanged tree at the start of a batch becomes a claim that the code already holds the item, the batch takes its fork commit as its head, and the Tester, the harness, the Critic and the merge prove the claim with tests and no code change. Shape A puts a fact, a test run, behind the claim, so a weak Developer that claims "met" to escape work costs one Tester session and one run and then meets red tests, and it covers all three ways in: a guard clause, a re-ask of merged work, and a restart.

Question for Roman: when the team finds that a job you asked for is already true of the code, should the team prove it with checks that join the project and tell you "no code changed", or end the job on a team member's word (recommended: prove it with checks)?

## 1. Four facts the code holds now

### 1.1 The empty-commit branch of `code.commit`, and its note

- `code_commit` starts at `rota/roles/api.py` 23892. It calls `worktrees.commit(tree, message, exclude=test_paths)` at 24010, and `None` means that nothing was staged (observed).
- On `None` with no drift, the door returns `{"committed": False, "why": "nothing changed", ...}` and writes no row (observed: api.py 24015 to 24047).
- A session that sent `msg.challenge_tester` or `msg.escalate_architect` gets "the tree is exactly as you found it. You have sent your message: end the session" (observed: api.py 24034 to 24040, frame 200).
- Every other session gets the note "the tree is exactly as you found it. If the criteria are already met, say so in your reply and end the session, with no message to anybody; if you were going to change the code, the change comes first: code.write, then commit" (observed: api.py 24042 to 24047).
- The writer's own docstring expects this case: "None is not a failure. A Developer session that reasoned, read and concluded the code was already right has nothing to commit" (observed: `rota/core/worktrees.py` 209 to 211). No reader of the database records the conclusion (reasoned: the door writes nothing on this branch).
- The comment over the note names the other use of the same branch: "the Developer probed, loaded criteria, called commit on an untouched tree, logged a real assumption, and ended -- five runs of five, twice, with `code.write` never called" (observed: api.py 24016 to 24021). So an empty commit is either a true claim or an escape, and the door cannot tell them apart (reasoned).
- The Developer's `batch_start` brief names no "already met" case. Only the door note offers it (observed: grep of `rota/roles/prompts/developer/`).

### 1.2 The stall rule and the rungs after it

- `tick_batch_start` (`rota/core/scheduler.py` 498) counts a running batch with no `head_commit` and a committed Developer session on `tick:batch_start` as a start that did not land: "The start is owed until a commit exists" (observed: scheduler.py 510 to 525).
- It re-wakes the Developer with "attempt {n} of {cap}" and the words "the last session ended with nothing written and nothing committed" (observed: scheduler.py 535 to 553).
- The tick quarantine takes the key `developer|tick:batch_start|<batch>` at the cap of 3 (observed: dry2w3 `tick_attempts`, attempts 3, quarantined 1).
- `exhausted` (`rota/core/predicates.py` 1145 to 1199) then wakes the next rung on `tick:exhausted`, with the detail from `stop_detail` (observed). The ladder is `("developer", "architect", "vision_keeper")` (observed: predicates.py 46). `_next_rung` returns an empty string after the Vision Keeper, and the Liaison is reached only by a `report` (observed: predicates.py 1253 to 1281).
- No rung's tools hold an act for "already met". The Developer's `exhausted.tools` holds loads, `ledger.log` and four messages. The Architect's holds `decisions.author` and messages. The Vision Keeper's holds `problem.assert`, `decisions.author`, `ledger.log` and `msg.report_liaison` (observed: the three `exhausted.tools` files).
- The stopped page opens "The team stopped work on this change." and then "The team gave up: {part}." (observed: `rota/roles/principal.py` 3062 and 3069). The part for this key is "the change could not start" (observed: principal.py 2393).
- On the dry2w3 copy, `tick_batch_start` still returns `Wake('developer', 'tick:batch_start', refs=('b_2',), detail='attempt 4 of 3: the last session ended with nothing written and nothing committed')`. The quarantine alone holds it back (observed: `f360d/control.py`).

### 1.3 How the Vision Keeper slices one sentence

- On an existing account, the deliver brief says: "The statement is a new behaviour. Assert it as its own item, with an id that names the behaviour, one `problem.assert` per distinct thing" (observed: `rota/roles/prompts/vision_keeper/deliver.md` 35 to 38, f4b29e57, 2026-09-09).
- It then says: "One item per distinct thing the software must do" (observed: deliver.md 43 to 44, 9a109336, 2026-08-09).
- It also says: "an item already on file for the same behaviour is not asserted again under a new id, however differently worded" (observed: deliver.md 44 to 46). The account already held `calculates_tip`, "The program calculates the tip amount by multiplying the total amount by the tip percentage divided by 100.", approved (observed: dry2w2 `items`). The dedupe sentence did not stop `returns_tip_as_before` (observed: dry2w3 `items`).
- The brief says nothing about a guard clause, a condition, or a clause that keeps a behaviour. Its one limit is on out-of-scope items: "only where the statement's own words name a boundary" (observed: deliver.md 48 to 50).
- The Terminologist already wrote the clause as a criterion of the first ticket: `c_2` of `tk_1`, "When the tip percentage is valid (between 0 and 100 inclusive), the program returns the calculated tip amount without raising an exception.", with the test `tst_tip_valid` in `b_1` (observed: dry2w3 `criteria`, `tests`).

### 1.4 The readers that assume an approved item means a code change

The read's 11 places hold at 3adb4726 (observed: the lines below). One more reader is added at the end.

1. `deliver.md` 35 to 38 and 43 to 44, as in 1.3.
2. `challenge_subjects`, scheduler.py 1428 to 1458: the Critic challenges every item, request items too. The only readers of `challenges` are the done-set at scheduler.py 1465, a count of `falsified` at api.py 19353, and the finding review at api.py 19471. None acts on `stands` for a request item (observed: grep of `FROM challenges`).
3. `problem_describe`, api.py 2445 to 2449: "is the principal's own words, so it asks for something".
4. `terminologist/criteria.md` 18 to 22: "An existing callable is the surface only when the item asks for what that callable already does." No check follows.
5. `tests_missing`, predicates.py 910 to 951: the Tester waits for `head_commit`. Its reason is greenfield: "The thing the criterion names now exists to be imported and called" (observed: predicates.py 919 to 921).
6. `harness`, predicates.py 971 to 994: `b.head_commit IS NOT NULL`.
7. `tick_batch_start`, scheduler.py 510 to 553, as in 1.2.
8. `code.commit`, api.py 24042 to 24047, as in 1.1.
9. `mergeable`, `rota/core/lifecycle.py` 875 to 876: "nothing committed" when `head_of` is `None`.
10. The ladder's three tool files, as in 1.2.
11. The stopped page, principal.py 3062 to 3070.
12. Added here: the state line "Done: {merged} change{s} built, tested and merged." counts every merged batch (observed: principal.py 354 to 356). Under any shape that merges with no code change, this line calls the batch "built" (reasoned).

Two readers already accept an empty diff. The Critic's review brief says a criterion that keeps a behaviour "is met by `kept: <the one line>`" or "by `test: <the test id>`, its own passing test that step 2 finds encodes it" (observed: `rota/roles/prompts/critic/review.md` 14 to 18). `code.diff` reads the diff from the batch's fork, not from `HEAD~1` (observed: api.py 20213 to 20218).

### 1.5 Probed: `lifecycle.merge` takes a branch whose only new commit is the tests commit

The probe is `f360d/test_merge_tests_only.py` in this session's scratchpad. It builds the `gitfixture` sample project, one item, one running batch `b1` with a worktree, and sets `head_commit` to the worktree's fork commit with no Developer commit. Results (observed: pytest, 2 passed in 6.77 s):

- With one test row: `lifecycle.merge` commits "rota: tests of b1" in the worktree, `integrate` makes a merge commit "rota: deliver b1" with two parents, the status is `merged`, and the diff from the base to the new main head is `tests/test_probe_f360.py` only.
- With no test row: the status is `merged` and main's head does not move, because `git merge --no-ff` of a branch with no new commit reports "Already up to date" and exits 0 (observed). So a merge with no tests leaves no trace in git (reasoned). `mergeable` stops that case today, because the review waits for a test run and every live criterion needs its test (observed: lifecycle.py 877 to 900).

## 2. The axes

- **Where the end is written.** The slicer: the Vision Keeper's deliver brief, before any item exists. The Critic's verdict: `challenge.uphold` on a request item, before any batch. The commit door: the empty-commit branch, at the start of the batch. The stall rule: `tick_batch_start`, after the start.
- **What the end means.** Merged with tests and no code change. Delivered as already held, with no merge. Folded into the first item as a criterion, so no second item exists. Dropped, as frame 357's drop did on turn 4.
- **Who proves the claim.** The Tester and the harness, with tests that join the project. The Critic, by a reading of a quote. Nobody, so the Developer's word is the end.
- **What the seat reads.** A merge line that says no code changed. A line that says the code holds the item already. Nothing, because the item never exists.

## 3. Candidate shapes

The prices use the anchors of `plans/operating-facts.md` line 250: "a door text or a number, 2; an instrument fix, 3, frame 199; a seam design with its night, 8 to 10" cycles (observed).

### A. The read's proposal: the empty commit is a claim, and the tests prove it

At the empty-commit branch, when the batch has no head and the session sent no challenge or escalation, the door writes the worktree's HEAD, the fork commit, as `head_commit`, with a mark that the head is a claim and not a change. The note says: "You claimed the criteria are met. The Tester's tests check the claim." `tests_missing`, `harness`, the Critic, the Architect and `merge` then run as they are (reasoned: readers 5, 6 and 9 read only `head_commit`; the Critic accepts `test: <id>`, 1.4). The Done line says "No code changed. These tests show the code already does this." for a marked batch.

- Cost: 6 to 7 cycles. The door write and the mark are an instrument fix, 3. The note and the Done line are two door texts, 2 to 3. One review (reasoned: the anchors; the read priced 5 to 6 before reader 12 was found).
- Changes: a door's result (`code.commit` on an unchanged tree), the Developer's note, which is a prompt's shape, and the seat's state line, which is a page form. It changes the meaning of `merged` from "the code changed" to "the code holds it, with tests". No law changes: law 8's merge gate, harness, then Critic, then Architect, runs unchanged (reasoned: `rota/LAWS.md` 222 to 240). Needs Roman's ruling for the meaning of `merged` and the page line.
- Weak model: a Developer that claims "met" to escape work gets a head at the fork. The Tester encodes the criteria black-box, the harness runs them, and they go red on a new behaviour. Then `tests_failing` wakes the Developer with real red tests, the normal fix loop (reasoned: the comment at api.py 24016 to 24021 names five of five such escapes; under A each costs one Tester session and one run, not three empty starts and a ladder). The check is a test run, a fact.
- Failure: a weak Tester writes a test that asserts what the code does and not what the criterion says. The test is green at the fork, and a new behaviour merges with no code. Concrete: for "round the tip to two decimals", a test `assert calculate_tip(100, 15) == 15.0` passes on the old code. The Critic's step 2, "Does each test encode its criterion?", is the only check, and the Done line puts "No code changed" in front of the seat (reasoned: review.md step 2). A second failure: night 163's `bg_2` and night 169's `batch_1` ended starts with writes that a door refused or discarded (observed: the read, section 5). Under A those sessions become claims too. They go to the Tester and to red tests, which is a better wake than a fourth empty start, but the claim is false (reasoned). The door can exclude a session whose non-test writes were refused or discarded, and the build decides that.
- Measure: on a writable copy of dry2w3 with the key `developer|tick:batch_start|b_2` cleared, a Developer sandbox on `b_2` calls `code.commit` on the unchanged tree. Then `head_commit` is the fork commit, ff1f65f (control NULL), `tick_batch_start` returns `[]` (control: "attempt 4 of 3"), `tests_missing` wakes the Tester for `b_2` (control: no wake), and `mergeable` no longer says "nothing committed" (control: "nothing committed"). The merge half is the probe of 1.5. On the next dry runs: items that end as three empty starts, from 1 of 2 on dry2 toward 0, and each merge with no code change shown on the Done line, counted.

### B. The source fix: a guard clause stays a criterion of the first item

The deliver brief says that a clause which keeps the current behaviour under a condition, such as "and return the tip as before otherwise", is a criterion of the item it guards and not an item. The dedupe sentence at deliver.md 44 to 46 also names the account's own items, so `calculates_tip` stops a second item.

- Cost: 2 to 3 cycles. A prompt text is 2, and the recorded cases of the deliver mode move with it (reasoned: the anchors; frame 358's footer change staled recordings).
- Changes: a prompt's shape. No door, no page form and no law. L1 holds: "Downstream roles re-decompose into their own artefacts" (observed: LAWS.md 226 to 227). Needs Roman's ruling only because it edits a prompt's shape by C76 step 3b.
- Weak model: the Vision Keeper is the seat that must judge "keeps a behaviour" against "new behaviour". A weak model splits anyway, or folds a real new behaviour into a criterion. Nothing checks the split except the seat on the signoff page (reasoned: m16 put the guard clause under "You asked:", the read, section 1).
- Failure: it covers one way in out of three. A re-ask of merged work, for example "Make sure the function rejects a negative percentage" after `b_1` merged, is a new statement with one item, and that item stalls the same way through readers 5 to 11 (reasoned: the read, section 6, "Doubt").
- Measure: replay the deliver session of dry2 under the new brief. The statement `s1` gives 1 request item (control 2). On the next dry runs, sentences with a guard clause that give one item, counted.

### C. An end before any batch: the Critic's `stands` ends the request item

A `stands` verdict on a decided item becomes "already held". The item gets an end state, no batch schedules, and a page tells the seat "The team reads the code as already doing this" with the Critic's quote.

- Cost: 8 to 10 cycles. A new item state is a schema change, `challenge_subjects` must run on request items before the signoff page, the signoff page needs a line, and the night measures it (reasoned: the anchors, a seam design).
- Changes: a door family (the verdict gets a reader that ends work), a page form (the signoff page), and the order of two ticks. It touches law 8, "Gates are predicates, not judgement", because one model's reading ends an approved request (reasoned: LAWS.md 222). Needs Roman's ruling.
- Weak model: the Critic is the only check, and its evidence is a quote. s40's quote was the function `def calculate_tip(total, tip_percentage):\n    return total * (tip_percentage / 100)` and its why was "This logic is unchanged from a standard implementation, confirming the behavior described" (observed: dry2w2 `challenges`). A quote of a function cannot show that the function raises no exception. On dry2 the verdict was right, and s41's `falsified` on the ValueError item was right too (observed). The loop is one reading with no run, the longest loop of the four (reasoned: "The feedback rate is the ceiling").
- Failure: the order. On dry2 the signoff page m16 went out at s38 and s39, and the Critic's `stands` came at s40, after the page (observed: dry2w2 `sessions`, `messages`). So C needs the challenge to run first, or a second page. A Critic that upholds a false claim on a request item ends it unbuilt, and only the seat can catch it.
- Measure: on dry2w2, the signoff page shows the held line for `returns_tip_as_before` and not for the ValueError item. After the approval, no batch exists for it (control: `b_2`).

### D. The stall rule reads "already met" as an end, with a page and no tests

The Developer gets an act for the claim, for example a flag on `code.commit`. `tick_batch_start` reads the act and does not count a failed start. The batch ends as "already held" with no merge, and a page tells the seat.

- Cost: 5 cycles. The act is an instrument fix, 3, and the page line is a door text, 2 (reasoned: the anchors).
- Changes: a door family (a new act), a page form, and the meaning of a batch's end. It touches law 8 the same way as C. Needs Roman's ruling.
- Weak model: the Developer's word is the end. The five of five escapes in the comment at api.py 24016 to 24021 then end items unbuilt, with nothing but the seat to check (reasoned). This fails "Every claim cites a source. A seat can check the claim against the source", because the seat would have to read the code itself (reasoned: `plans/composition.md` 78).
- Failure: s63 said "already satisfies" after four test writes the door refused (observed: the read, section 1). On a real new behaviour, the same reply ends the work, and the page says the code holds it.
- Measure: on dry2w3, the act ends `b_2` with no ladder: `exhausted` gives no wake (control: three rungs, s66, s70, s72), and the page says "already held".

## 4. Control: the dry2 copies under the current code

From `f360d/control.py` in this session's scratchpad, on copies of dry2w2 and dry2w3 (observed).

| Reader | dry2w2 (before turn 3) | dry2w3 (after turn 3) |
|---|---|---|
| `returns_tip_as_before` | `draft`, provenance `decided` | `approved` v1, provenance `decided` |
| Critic verdict on it | `stands`, quote of the old `calculate_tip` | the same |
| Critic verdict on the ValueError item | `falsified` | the same |
| Tickets | none | `tk_1`, `tk_2` |
| Criteria of `tk_2` | none | `c_5`, `c_10` |
| `b_2` | none | `running`, `head_commit` NULL |
| Tests of `b_2` | none | 4 inherited, none for `c_5` or `c_10` |
| Developer sessions on `b_2` | none | s63, s64, s65 on `tick:batch_start`, s66 on `tick:exhausted` |
| `developer\|tick:batch_start\|b_2` | none | attempts 3, quarantined 1 |
| `tick:exhausted` sessions | none | s66 developer, s70 architect, s72 vision_keeper |
| `tick_batch_start` now | `[]` | one wake, "attempt 4 of 3" |
| `mergeable(b_2)` | "nothing committed" | "nothing committed" |
| Open pages | m16 signoff | m33 clarify, m34 stopped page |

The code holds the item at both commits: the read's 16 probe tests of `c_5` and `c_10` pass at the walk base 99101f1 and at ff1f65f (observed: the read, section 4). So the red test of shape A needs no new fixture, only a writable copy of dry2w3 with the stalled key cleared (reasoned).

## 5. Recommendation

Build shape A. Do not build B, C or D now (reasoned: A covers the three ways in, its check is a test run, and it changes no gate).

The reason, in the composition's words (observed: `plans/composition.md`):

- "no work happens that the Principal did not ask for". Under A the Developer writes no code and the merge carries only tests. Today the turn spent 12 sessions on a ladder and two pages he did not ask for (observed: the read, section 1).
- "and no work stays invisible". Under A the Done line says that no code changed, and the tests are in the project. Under D the end has no trace in git (reasoned: the probe of 1.5 shows that a merge with no new commit leaves main where it was).
- "A prediction never blocks. Only a fact or a ruling gates." Under A the claim is a prediction that the tests turn into a fact. Under C and D one model's reading is the gate (reasoned).
- "Every claim cites a source. A seat can check the claim against the source." Under A the source is a test run the seat can read. Under D the source is a reply (reasoned).
- "The feedback rate is the ceiling. A weak model is trusted only as far as the loop that checks it is short." Under A a false claim meets a red test in one Tester session and one run. Under B nothing checks the split, and under C and D the seat is the check (reasoned).
- "The Principal declares finished. The system observes a candidate only." Under A the merge with tests is the candidate, shown as such on the Done line (reasoned).

B is cheap and may follow A later, because a second item still costs a slice, criteria, a Tester session and a run under A. It needs its own measure first: the count of guard clauses that split on the next dry runs (reasoned). C's reader of `stands` may later add a note "the team reads the code as already doing this" to the signoff page, with no end attached (reasoned: the read, section 6). Left out of A: the duplicate of `tk_1`'s `c_2` and `tk_2` goes undetected, and the dedupe sentence of deliver.md 44 to 46 still misses the account's `calculates_tip` (observed: 1.3).

### The question for Roman, in plain words

The situation: you ask the team, "Make the tip function refuse a percentage below zero or above one hundred, and return the tip as before otherwise." The team splits your sentence into two jobs. The first job adds the refusal, and it is built and merged. The second job, "return the tip as before", is already true of the code, because nobody changed that part.

What happens today: the builder looks at the second job three times and says each time, "the code already does this." The system counts each answer as a failed start. It asks two managers, and they agree with the builder. Then you get a page that says "The team gave up."

What happens next, option 1, the team proves it: the builder says "already done". A tester writes checks for the job and runs them on the code as it is. If they pass, the checks join the project, and you read "No code changed. These checks show the code already does this." If they fail, the builder gets the failing checks and works as usual.

What happens next, option 2, the team takes the word: the builder or the reviewer says "already done", the job ends, and you read "already done". Nobody runs a check. If the builder was wrong or lazy, the job is not done and only you can find out.

One exact analogy: an inspector asked to certify a wall that already stands does not rebuild it. He tests it, and he signs the test report.

Recommended: option 1. A check costs one tester and one run, and it catches a builder who says "done" to avoid the work.

## Usage

About 140k tokens on this agent's counter, against a cap of about 80k (observed: the counter at start and at the page write). The probes are `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ce483c7b-be58-4d58-bfc4-db1081518842/scratchpad/f360d/test_merge_tests_only.py` and `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ce483c7b-be58-4d58-bfc4-db1081518842/scratchpad/f360d/control.py`, on copies in the same folder.
