# Frame 204, pass 1 review: the kinds at the door and the faults table

DOES NOT STAND: 1 high, 6 low.

The code paths hold: the door, the faults table, the three readers, the close command and the literal door. The pass leaves 15 of the 16 brief lines that invite `ledger.log` with no word. Two of them dictate a call form that the door now refuses. Pass 1b closes the high finding.

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_rv204` at b00aaa59, 2026-10-11 17:24. Probes are in the scratchpad, `rv204/`. No model was called.

## (a) Verdicts

1. The door text: holds. Question 0, questions 1 and 2, and the tie-break are present. The text names words that the mode refuses, and it omits the tie-break's item 4 (L4).
2. The refusals: hold. The tie-break keeps the first cell for words the mode offers. A second word that the mode does not offer refuses the whole call (L3).
3. `fault` and `blocked`: hold. They write `faults` and no ledger row. The reply names the people who build rota. No page shows a row. The fault branch skips the echo guard (L2).
4. The readers and the close: hold. The close changes only the named call's rows.
5. The literal door: holds. It stages `invented`, the author is the seat, and the returns door names `default`.
6. The relay modes: hold. Neither relay `.tools` file holds `ledger.log`, and `terminologist/relay.md` asks for no log. The echo guard still refuses a `default` note.
7. The brief lines: do not hold (H1). 25 modes offer `ledger.log`. 16 brief lines invite it, and 1 names the words.
8. The word changes: hold. Every kind that the code writes passes the CHECK. The CHECK admits `blocked` and `fault`, which never belong in `ledger` (L5).
9. The three reds: hold. All three are in the baseline's failed set, and each failure has a cause outside the diff.
10. Outside: `render_state` raises on an old run database (L1). No reader filters on `ledger.kind`.

## (b) Findings

### H1. 15 of 16 brief lines that invite `ledger.log` name no word, and two dictate a call that the door refuses

- Severity: high. CONFIRMED.
- Where: `rota/roles/prompts/vision_keeper/deliver.md:23`, `vision_keeper/reconcile.md:15-17`, `tester/tests_missing.md:46`, and 12 more lines (listed in point 7).
- The design's pass 1 file list says: "each brief line of section 1, item 2, names the words that its mode offers". Section 1, item 2 counts 18 lines, and it gives two lines as examples. The pass read the two examples as the whole list.
- The tool schema advertises `kind` as a bare `string`, with no word list (probe P5). The `.tools` comment line does not reach the seat. So a seat in 24 of the 25 modes learns the words only from a refusal.
- `vision_keeper/deliver.md:23` dictates `TOOL: ledger.log(about_ref="how_it_works", about_table="items", assumption="...")`. The door refuses that exact form with `missing required argument(s) ['kind']` (P4).
- `vision_keeper/reconcile.md:15` says "that is a finding". The reconcile mode refuses `kind='finding'` (P4: `kind='finding' is no word this mode offers ... This mode offers: conflict, default, blocked, fault, other.`).
- `tester/tests_missing.md:46` still tells the Tester to log an owed literal before the encode. The door now stages that row itself. The design's second ratio, dictated `ledger.log` turns from 103 to 0, cannot reach 0 while the brief asks for the turn.
- Fix: in pass 1b, give each of the 15 lines one clause with its mode's words. Add `kind=` to the two call forms. Change "finding" in `reconcile.md` to `conflict`. Remove the instruction in `tests_missing.md:46`. Then re-record.

### L1. `render_state` raises on a run database from before this commit

- Severity: low. CONFIRMED.
- Where: `rota/roles/principal.py:309`.
- `rota agenda <run>` opens the database with `connect_readonly`, which skips the schema mark. With no ask pending, it calls `render_state`. The new count reads `faults` with no table check.
- P2 showed: `old render_state RAISES OperationalError no such table: faults`. The cockpit snapshot guards the same read and returns `[]`.
- Fix: guard the count with the same `sqlite_master` check that `cockpit/server.py:160` uses.

### L2. A `fault` or `blocked` note skips every guard after the kind check, and `faults.call` can hold a row id

- Severity: low. CONFIRMED.
- Where: `rota/roles/api.py:7975` returns before the message guard (`:7994`), the table guard (`:8020`) and the echo guard (`:8024`). `_refused_call` (`:7879`) falls back to `about_ref`.
- P4, on the m399 relay fixture: `kind='default'` meets the echo refusal. The same text with `kind='blocked'` writes `{'fault': 'f_e69a1916ab', 'call': 'parametersource_commandline', ...}`. A note about the message `m419` with `kind='fault'` writes a fault with `call: 'm419'`.
- P1: a fault with no refusal before it writes `call: 'c1'`, a criterion id.
- The relay modes no longer offer the call. Other modes that a ruling reaches still offer it, so an echo can move to the faults table. The night report then groups faults under row ids, and `close --call` cannot name a real call for them.
- Fix: run the echo guard and the message guard before the fault branch. Write `call = 'unknown'` when no refused call and no call-shaped ref exist.

### L3. Two words refuse the whole call when one word is outside the mode, and an unknown word is dropped in silence

- Severity: low. CONFIRMED.
- Where: `rota/roles/api.py:7969-7971`.
- P1 in `developer/batch_start`: `kind="invented, gap"` is refused with `kind='gap' is no word this mode offers`. Section 8 says: "The door applies the order when a seat sends two words, and it keeps the first." `invented` is first and is offered.
- P1: `kind="invented, banana"` is admitted as `invented`, and `banana` gets no word back.
- Fix: drop the words that the mode does not offer before the tie-break. Refuse only when no offered word is left.

### L4. The door text names words that the mode refuses, and it omits item 4 of the tie-break

- Severity: low. PLAUSIBLE.
- Where: `rota/roles/api.py:7827` (`KIND_QUESTIONS`, 206 words).
- Question 2 maps "the principal, did not need to" to `'gap'`, and "a row's owner, picked" to `'finding'`. Neither word is offered in 24 of the 25 modes. A Developer that follows the questions to `gap` meets a second refusal (P1).
- The text gives the tie-break as "conflict, scope, the owner's word, the principal's word, nobody's word". It leaves out item 4: within one row, "could not" before "picked" before "did not need to". The door applies item 4 through `LOG_KINDS`, so the omission changes no write.
- The reason is PLAUSIBLE: no run measured whether a qwen3:8b seat maps the abstract order to words in one reply. The walk measures it.
- Fix: build question 2's mapping from `_offered_kinds(ctx)`, so the text names only the words the mode offers.

### L5. The `ledger.kind` CHECK admits `blocked` and `fault`

- Severity: low. CONFIRMED by reading.
- Where: `rota/core/schema.sql:565-567`.
- The schema's comment says that `blocked` and `fault` "never land here". The CHECK still admits both. A raw writer, or a later door change, can put a fault on a page, and the schema does not refuse it.
- Fix: remove `'blocked','fault'` from the ledger CHECK.

### L6. A two-source `conflict` and an owned-row `conflict` share one word

- Severity: low. PLAUSIBLE.
- Where: `rota/roles/api.py:7820` and `vision_keeper/reconcile.tools`.
- Section 2 places a conflict of two project sources in the principal's "could not" cell. That cell holds no merge. The owned-row `conflict` holds a merge while the owner owes the answer.
- The column cannot tell the two apart, so pass 2's `mergeable` must decide from the owner of `about_ref` and not from `kind`. The tie-break also puts a two-source conflict before `scope`.
- The word change holds against the lint. The risk is PLAUSIBLE until pass 2 reads the column.
- Fix: state in pass 2's brief that `mergeable` keys on the owner of `about_ref`, and that a conflict with no owner holds nothing.

### Outside: the report's counts

The report says 23 `.tools` files gained a kinds line and names "20 seat modes". The diff adds the line to 25 files: 22 seat modes, `liaison/blindspot`, `vision_keeper/reconcile` and `vision_keeper/survey`. The code is right. Only the record is wrong.

## Point 1: the door text, verbatim

`KIND_QUESTIONS` at `rota/roles/api.py:7827`, as P1 printed it:

> Answer three questions, and the word follows. 0: is the obstacle a rule of rota (a permission, a door, a tool) or the content of a row? A rule that works as designed is no note, so log nothing. If you believe the row behind the rule is wrong, the note is about that row: go to question 1. A rule that failed is kind='fault'. A record that names a row that does not exist is kind='blocked'. 1: if the note is wrong, who must say so: the principal, the owner of a row, or nobody in rota? 2: did you pick, could you not pick, or did you not need to? The principal, picked: 'default', or 'scope' when you left out or added work. The principal, could not: 'conflict' when two sources of the project disagree. The principal, did not need to: 'gap'. A row's owner, picked: 'invented' for a value you chose, or 'finding'. A row's owner, could not: 'conflict'. A note that fits two words takes the first of this order: conflict, scope, the owner's word, the principal's word, nobody's word. A note that fits no word is 'other'. A step, a plan or a ruling said again is no note: log nothing.

Then the door adds ` This mode offers: conflict, scope, invented, default, blocked, fault, other.`

- Question 0: present, with all three branches of section 8.
- Questions 1 and 2: present, with the grid as words.
- The tie-break: present for items 1 to 3. Item 4 is absent (L4).
- What is missing: the mapping is not filtered by the mode (L4). The tool schema carries no word list (H1).

## Point 2: the refusals

Probe P1, `developer/batch_start` with `ctx.log_kinds` from `prompts.mode_kinds`:

- `kind="assumption"`: `ValueError: kind='assumption' is no word this mode offers. Answer three questions, ... This mode offers: conflict, scope, invented, default, blocked, fault, other.`
- No `kind`: `ArgumentError: ledger.log: missing required argument(s) ['kind']; accepts (about_ref, about_table, assumption, kind) -- kind is one word that says what the note is. Answer three questions, ...`
- `kind=""`: `kind is one word that says what the note is. Answer three questions, ...`
- `kind="unaddressed_answer"`: refused with the questions.
- `kind="default, invented"`: `{'id': 'l_980f7c464b', 'kind': 'invented'}`. The owner's cell comes first. This holds.
- `kind=["default", "scope"]`: `{'id': ..., 'kind': 'scope'}`. The merge cell comes first. This holds.
- `kind="default, blocked"`: `{'id': ..., 'kind': 'default'}`, a ledger row. This matches item 3, the principal before nobody.
- `kind="fault, conflict"`: the conflict offer, `Send msg.question_terminologist(refs=['c1'], question=<your note>)`.
- `kind="Default"`: admitted as `default`.
- `kind="invented, gap"`: refused (L3).
- `kind="invented, banana"`: admitted as `invented`, and `banana` is dropped (L3).

## Point 3: faults and pages

- P1, `kind="fault"`: `{'fault': 'f_5c22a98596', 'call': 'c1', 'note': 'the fault is recorded for the people who build rota. No page shows it, and nobody in rota answers it. End the session.'}`. The writes are `[('faults', 'fault')]` and no ledger row.
- The test `test_a_fault_or_a_block_writes_faults_and_no_ledger_row[fault|blocked]` applies the rows and finds 0 ledger rows. It passes.
- Pages: the map lists the readers of `faults` as `cockpit/server.py:snapshot`, `principal.render_state`, `faults.open_counts` and `_stage_fault`. No page reader is on the list. `render_state` shows a count line and no row (P2).
- The fault branch skips the echo guard (L2).

## Point 4: the readers and the close

P2, four open faults, two each on `glossary.adopt` and `model.adopt`:

```
list before:
glossary.adopt 2
model.adopt 2
close:
closed 2 open faults of glossary.adopt by frame 197
close again:
closed 0 open faults of glossary.adopt by frame 198
[('f1', 'glossary.adopt', 'resolved', '197'), ('f2', 'glossary.adopt', 'resolved', '197'), ('f3', 'model.adopt', 'open', None), ('f4', 'model.adopt', 'open', None)]
snapshot faults: [('f4', 4), ('f3', 3)]
state view:
Nothing waits on you and nothing is building. Tell me what you want. I take it from there.
Rota itself failed 2 times this run. The people who build it have the list.
```

P3, the night report, with one resolved row on `model.adopt`:

```
== open faults
glossary.adopt fault 2
glossary.adopt blocked 1
```

On a 3f2e974e database, the night report prints `absent: faults`, and the snapshot returns `[]`. `render_state` raises (L1). `faults list` refuses with the schema sentence.

## Point 5: the literal door

- `test_desk_guards.py::test_a_literal_the_material_never_said_is_an_assumption_first` asserts kind `invented`, author `tester`, about_ref `c1`, and the writes order `["ledger", "tests"]`. It passes.
- `test_the_returns_door_offers_a_default` asserts `kind='default'` in the refusal and in the offer's arguments. It passes.
- `test_offers_followed.py::test_the_literal_door_admits_eight_owed_literals_in_one_row` asserts one row that names all eight literals. It passes.
- The row's text joins literals with " and " and does not quote them: `the test assumes Enter your name:  where the material is silent`. This is a style point only.

## Point 6: the relay modes

- `architect/relay.tools` holds `model.adopt` and `model.load`. `terminologist/relay.tools` holds `glossary.adopt` and `glossary.lookup`. Neither holds `ledger.log`.
- `terminologist/relay.md` lost the sentence "If the contest tells you an assumption you made, `ledger.log` it." No other sentence in the file asks for a log.
- P4, the m399 relay fixture with the role's whole set: `kind='default'` returns `the principal ruled on parametersource_commandline in the relay that woke you ...`. The guard stands for a note.
- The guard does not stand for `kind='blocked'` (L2).

## Point 7: the brief lines

Modes whose `.tools` offer `ledger.log`, 25, each with a kinds comment line:

- Architect: answer, deliver, escalate, exhausted, unresolved.
- Developer: answer, batch_start, challenge, exhausted, finding_violated, findings_exhausted, tests_failing, verdict_failed.
- Liaison: blindspot (`gap, blocked, fault, other`).
- Terminologist: answer, criteria, criterion_repair.
- Tester: answer, tests_missing.
- Vision Keeper: answer, deliver, exhausted, slicing, plus reconcile and survey (`default, conflict, blocked, fault, other`).

Brief lines that invite `ledger.log` (`grep -rn "ledger.log" rota/roles/prompts --include=*.md`), 16:

| Line | Names the words |
|---|---|
| `architect/base.md:47` | no |
| `developer/answer.md:32` | no |
| `developer/batch_start.md:42` | yes |
| `developer/challenge.md:9` | no |
| `developer/exhausted.md:25` | no |
| `developer/findings_exhausted.md:19` | no |
| `liaison/blindspot.md:18` | no |
| `liaison/blindspot.md:20` | no |
| `terminologist/base.md:41` | no |
| `tester/base.md:22` | no |
| `tester/tests_missing.md:46` | no, and it asks for a log that the door now stages |
| `vision_keeper/base.md:40` | no |
| `vision_keeper/deliver.md:23` | no, and its TOOL line has no `kind` |
| `vision_keeper/exhausted.md:18` | no |
| `vision_keeper/reconcile.md:15` | no, and it says "finding", which the mode refuses |
| `vision_keeper/slicing.md:25` | no |

The count of lines not done is 15, not 16. The design's 18 is these 16 plus the two lines of `terminologist/relay.md:14-15`. The report's 16 probably counts one line twice. See H1.

## Point 8: the word changes and the CHECK

- `unaddressed` dropped: holds. Section 8, case 3, already names `ledger.unaddressed` for the cell, and that call writes `unaddressed_answer`. `test_vocabulary.py` refuses `unaddressed` as two jobs.
- Two-source `conflict`: holds against the lint. It has a pass 2 risk (L6).
- `resolved`: holds. The design's `closed` named a state only, and `resolved` is the ledger's word for the same discharge. The command stays `close`, and the column stays `closed_by`.
- Writers against the CHECK: `ledger_log` writes `conflict, scope, invented, finding, default, gap, other`. `_stage_ledger` writes `unaddressed_answer`. `challenge.break`, `challenge.vacuous`, `frame.assign` and `loop.py:500` write no kind, so the default `default` applies. All pass the CHECK. No kind that the code writes is refused.
- `faults`: the door writes `fault` or `blocked` and `open`. `faults close` writes `resolved`. All pass the CHECK.
- The CHECK admits two words that it should refuse (L5).

## Point 9: the three reds

The baseline `D:/repos/rota/.rota-gate.json` is at 5d68808b, 103 commits before 3f2e974e. Its failed set holds all three, at lines 21 to 23:

- `tests/rota/test_onboarding.py::test_the_same_constraint_written_twice_is_one_gate`
- `tests/rota/test_pins.py::test_with_prompt_keeps_every_pin`
- `tests/rota/test_roles_doc.py::test_a_verb_carries_words_or_does_not_regardless_of_recipient`

Each red at b00aaa59 has a cause outside this diff:

- onboarding: `ValueError: a constraint from the survey of src/billing binds the grain that keeps it: bindings=[...]` at `api.py:3037`, the `model.amend` bindings door.
- pins: `Extra items in the left set: 'think'`.
- roles_doc: `assert not {'answer': 'some channels carry words and some do not'}`.

No run at 3f2e974e was made. The baseline and the causes are the evidence.

## Point 10: outside the points

- `ledger.kind` readers: `predicates.py:447-448` and `:531` filter on `unaddressed_answer` only. That class did not move. The scheduler, the sandbox and the principal's page read `ledger` with no kind filter. No predicate breaks.
- `_stage_ledger` keys on the class only for `unaddressed_answer`. Before the diff, only that caller passed a kind other than `default`. The behaviour does not change.
- `render_state` on an old run (L1).

## (c) Probes

All probes are in the session scratchpad, directory `rv204/`. Each ran from the worktree root with `D:/repos/rota/.venv/Scripts/python.exe`.

- P1 `p1_door.py`: 12 `ledger.log` calls in `developer/batch_start`, with the mode's kinds set as `session_sandbox` sets them.
- P2 `p2_readers.py`: `faults list` and `close` on two calls, the snapshot, the state view, and a database built from 3f2e974e's `schema.sql` (`schema_3f2e.sql`, from `git show`).
- P3 `p3_night.py`: the night report's faults section on a new database and on the old one.
- P4 `p4_echo.py`: the m399 relay fixture with `default`, `blocked` and `fault`. Then the `vision_keeper/reconcile` mode with `finding` and with no kind.
- P5 `python -c`: `toolschema.schema_for('ledger.log', api.ledger_log)` prints `"kind": {"type": "string"}`, with no word list.
- `test_p4_echo.py` failed at collection on a missing template directory, so P4 replaced it.
- pytest, `-n 0`, `ROTA_MODEL=qwen3:8b`: 11 touched files, `659 passed, 1 skipped, 8 xfailed, 1 warning in 82.87s`.
- pytest, the three reds by node id: `3 failed in 3.98s`.

## (d) Usage

These numbers are estimates. The harness line is the measure. Input is about 120k tokens, and output is about 15k tokens. The total is about 135k, against a cap of 150k.
