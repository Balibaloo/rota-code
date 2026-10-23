# Frame 303, review 1: pass 1 at 2d1dc9e9

Reviewer on Opus, read-only, worktree `C:/Users/roman/rota_r303` at
2d1dc9e9 (parent e041c662). Written 2026-10-23.

## Verdict

Accept for the night. The door refuses s205's assert on the real night 157
rows, and the receipt counts the report. The three admitted causes admit
0 unasked request items on nights 150 to 158. One hole is real: a team-seat
trigger that refs a ratified statement passes the door (finding H1). One
recorded case now contradicts the brief (finding M2).

## Findings

### H1. A team-seat propose that refs a statement passes the door. CONFIRMED, high

- Probe: on an in-memory copy of night 157, m94 with refs
  `["bg_1", "s1"]` admits `bg_1_item`. With refs `["bg_1", "e_m155"]` it
  also admits the item.
- Records: night 151's m80, an Architect `propose` with refs `["s2"]`, woke
  s194. s194 asserted the new item `confirm_default_on_eof_flag`, and the
  door of 2d1dc9e9 admits that shape by `named_statements`.
- The m80 cause chain also reaches the principal's verdict m73 through the
  deliver m76. So the chain branch admits it a second time.
- s194's text is the text of s2, so the principal asked for that work. The
  shape still lets a team seat write a request row under his words.
- Fix: in `_principal_cause`, count statements, entries and the chain only
  when the trigger's `from_role` is `liaison` or `principal`.

### M2. The recorded propose case contradicts the new brief. CONFIRMED, medium

- `tests/rota/cases/l1_gatekeeper2.yaml` line 101,
  `L1-VK-answer-a-refactor-proposal`, expects an `items` write or a
  `decisions` write.
- Its comment of 2026-09-13 names "reported to the Liaison instead of
  answering the proposal" as the failure. The new brief names that report
  as the answer.
- The door now refuses the `items` half on that wake, because the inbound
  refs an item and no statement.
- The case was already red in the gate baseline of 658abb63
  (`plans/frame178-pass1.md` line 47).
- Fix: change the `any_of` to a `report` to the Liaison or a decision,
  delete the old comment, and re-record.

### M3. Two admitted causes exist only for test fixtures. CONFIRMED, medium

- Probe: with the `deliver` branch removed, 11 tests go red, 3 in
  `test_night46_context.py` and 8 in `test_runner.py`. With the no-record
  branch removed, 3 tests in `test_desk_guards.py` go red. The count is 14,
  as the pass report says.
- The 11 tests check runner mechanics: atomic commit, held actions, cut
  replies, malformed calls. Their fixture deliver `m1` carries no refs and
  no cause. `test_runner.py` even seeds the principal entry `u1` and does
  not ref it.
- The 3 desk-guard tests build a sandbox with no wake. One of them,
  `test_a_delivered_statement_is_an_item_of_its_own`, names a delivered
  statement and seeds `s1`, but no deliver carries it.
- All 14 tests describe a right behaviour: a deliver brings the
  principal's words. The fixtures take a scripted shortcut, because a real
  deliver carries a statement ref or a principal cause.
- Records: no assert on nights 150 to 158 needs either branch. Night 155's
  m74, the one deliver with no statement ref, reaches the principal's
  verdict m71 by its cause chain.
- In production `runner.trigger_message` sets the trigger on every message
  wake, so the no-record branch fires only in a sandbox.
- Fix: give fixture `m1` the ref `s1` or a principal cause, give the
  desk-guard sandboxes a deliver wake, then delete both branches.

### L4. The entries branch has no record that needs it. CONFIRMED, low

- Probe: with the entries branch removed, only the new test
  `test_a_relay_that_refs_the_principals_entry_is_his_cause` goes red.
- Records: 32 Liaison relays to the Vision Keeper ref a principal entry on
  nights 150 to 158. No session on those wakes asserts an item.
- The branch does not check the sender, so a team seat that refs an entry
  passes (H1).
- Fix: restrict the branch to a Liaison `relay`, or fold it into the H1 fix.

### L5. Any report in the session answers the proposal. CONFIRMED, low

- Probe: a report with refs `["s1"]` and cause m94 answers m94. The
  receipt compares no refs.
- The propose mode can send only `msg.report_liaison`, so the risk is small.
- Fix: none now. Name the gap in the `RECEIPT_RULES` comment.

### L6. The propose mode still offers `problem.assert`. PLAUSIBLE, low

- `propose.tools` lists `problem.assert`. The door refuses an `in_scope`
  item on that wake. An `out_of_scope` item still lands, as the new test
  `test_an_item_of_another_kind_with_a_team_cause_lands` shows.
- Fix: decide if the propose mode needs `problem.assert`, and remove it from
  `propose.tools` if not.

## The points

### 1. The red test. CONFIRMED

The replay used s205's seq 6 call from `turns` on an in-memory copy of
night 157, with `bg_1_item` removed and m94 reopened. The op raised
`ValueError` and staged no `items` write:

```
bg_1_item needs the principal's words as its cause, because only the principal asks for work. The cause of this call is m94, a propose from the architect. Send msg.report_liaison with the refs ["bg_1"], so the Liaison brings it to the principal.
```

The sentences have 15, 12 and 14 words. Each holds 20 words. The route
`msg.report_liaison` with `["bg_1"]` then landed in the same sandbox as
`m216`.

### 2. The three admitted causes. CONFIRMED

The census takes the first assert of each `in_scope` id on a wake that is
not onboarding, nights 150 to 158. The count is 60.

| Cause of the wake | Items | Principal asked | Door of 2d1dc9e9 |
|---|---|---|---|
| Liaison `deliver` with a statement ref | 33 | yes | admits, statement branch |
| Team-seat `challenge` | 21 | no | refuses, frame 221 branch |
| Architect `propose` | 5 | 1 yes (s194), 4 no | admits s194 (H1), refuses 4 |
| `tick:contested` on another id | 1 | no | refuses |

Items that each admitted cause admits with no ask from the principal:

- Liaison `deliver` on its verb alone: 0. No first assert depends on it.
- A ref to a principal `entries` row: 0. No relay wake asserts an item.
- A wake with no cause on record: 0. The runner sets the trigger on every
  message wake.

s205's shape passes by none of the three in production. It passes when the
Architect's propose refs a statement or a principal entry (H1). The fix lines
are in H1, M3 and L4.

### 3. The 14 tests. CONFIRMED

The 14 tests are in M3. Each describes a right behaviour that a fixture
reaches by a scripted shortcut. The reversal in `test_predicates.py` keeps
the test's meaning. It inverts the rule the pass removes, and it drops one
check of `unresolved()`. The new status `unresolved` with the note covers
that check. No test in `test_predicates.py` checks that a report answers the
proposal. The new file covers it.

### 4. The receipt. CONFIRMED

Probes on an in-memory copy of night 157, m94 reopened, one committed
session each:

- A report with refs `["bg_1"]`, cause m94: `answered`.
- A decision with refs `["bg_1"]`: `answered`.
- An `items` write only: `unresolved`, "unresolved: the woken session sent
  nothing and wrote no row that cites this message".
- No report and no item: the same `unresolved` status and note.

So a proposal with no answer reads as unresolved and owed, and the
unresolved ladder takes it.

### 5. The brief. CONFIRMED

The new sentence has 18 words: "Then send `msg.report_liaison` with the refs,
so the principal sees it, or `decisions.author` refusing it with the
reason." The propose brief does not tell the seat to assert anywhere now.
`vision_keeper/base.md` line 7 says "Before asserting an item, search the
decision record". That sentence is about all wakes and gives no instruction
for propose. The new line is not wrapped at the width of the file. One
recorded case goes stale, `L1-VK-answer-a-refactor-proposal`, and its expect
is wrong as well (M2).

### 6. Nothing else changed. CONFIRMED

`git diff e041c662 2d1dc9e9 --stat` lists five files: `rota/core/db.py`,
`rota/roles/api.py`, `rota/roles/prompts/vision_keeper/propose.md`,
`tests/rota/test_frame303_request_item_cause.py` and
`tests/rota/test_predicates.py`. The change is 249 insertions and 18
deletions.

## Method

- The night databases were opened with `?mode=ro`. Each change probe ran on
  an in-memory copy made by `sqlite3.backup`.
- Each variant of the door was patched in the process with `exec` and run
  with `pytest -n 0`. The patch does not reach the xdist workers, so the
  first run with `-n auto` showed no red. The worktree has no edits.
