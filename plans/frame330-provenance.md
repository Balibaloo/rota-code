# Frame 330, the provenance read: the stuck running batch that keeps the one batch seat

Date: 2026-10-26, read at 18:12 to 18:20. Read at commit e023b851 on
`rota/foundation`, dated 2026-10-26 18:11. Read-only. The night databases
were opened with `?mode=ro`. No model call ran and no pytest ran. Meta
workflow for the read, by the rule of 2026-10-18 (provenance before a fix).

Sources:

- The symptom records, cited and not repeated: `plans/night168-read.md`
  section 1, walks 2 and 3 (lines 75 to 99), and section 2 row W5 (line
  108); `plans/wall-guide.md` cause 12 (lines 558 to 581).
- `rota/core/predicates.py`: `LADDER` line 46, `tests_failing` 949 to 983
  (the cap test 983), `exhausted` 1022 to 1065 (the open-message hold 1040
  to 1043, the cap test 1059), `_next_rung` 1117 to 1138, `preempt` 1584 to
  1638 (`do:park` 1631 to 1633, the priority test 1634 to 1635),
  `quarantined` 1696 to 1782 (the running-batch comment 1747 to 1751).
- `rota/core/scheduler.py`: `tick_batch_start` 488 to 514 (the refusal
  while a batch runs with a head commit), `failing_attempt` 1698 to 1709,
  `given_up` 1712 to 1719, `parked` 2233 to 2262 (the cap test 2251),
  `quarantine_overrun` 2451 to 2468, `quarantine_stalled` 2471 to 2520 (the
  kept count 2490 to 2496).
- `rota/core/config.py` lines 59 to 61 (`loop_cap`) and 121 to 128
  (`tick_attempt_cap`). `rota/core/schema.sql` 872 to 883 (`tick_attempts`).
- `rota/LAWS.md` lines 183 to 193 (law 6) and 398 (table row 6).
  `rota/DECISIONS.md` lines 1538 to 1550 (the review-key approve of
  2026-10-24).
- `plans/stack.md`: frame 312 (line 1570), frame 318 (line 1490), frame 330
  (line 1207).
- `.rota/clickI_night168.db`: `batches`, `tick_attempts`, `test_runs`,
  `test_run_journal`, `sessions` s140 to s226, `turns` and `tool_calls` of
  s153, s154, s167 and s169, `messages`, `item_parks`.
- `.rota/clickI_night160.db` to `.rota/clickI_night168.db`, 10 files:
  `batches` and `tick_attempts`.
- `git log -S` on `"tick_attempt_cap", 3`, `"loop_cap", 10`, `loop_cap`,
  `def exhausted`, `tick_attempts`, `do:park`, `keeps its count while the
  batch lives`, `def lift_on_red_move`; `git log -L` on the
  `tick_attempt_cap` and `loop_cap` settings and on the cap test of
  `exhausted`.

## The result

**Verdict: a gap, not a departure. Two later changes removed the premise on
which the tick cap of 3 and the `loop_cap` of 10 were made to live side by
side, and no rule says what frees the seat of a running batch whose
`tests_failing` key is quarantined below `loop_cap`.** The tick cap was built
on 2026-08-11 for a wake that never drains. Its commit says the counter
resets when a wake stops repeating, "so a Developer legitimately bouncing on
a red harness is never touched" (observed: 90f09152). Frame 83 on 2026-09-24
made a batch key keep its count while the batch lives (observed: 9d2693db).
Frame 318 on 2026-10-24 made a head commit lift a `tests_failing` key only
when the red moves (observed: 09fb1d90). After both, a Developer that bounces
three times on one red is quarantined at 3 dispatches, and the run attempts
stop below 10 (reasoned: `quarantine_stalled` 2490 to 2496, `db.lift_on_red_move`).
The ladder, the park and the preempt all read the run attempts against
`loop_cap`, so none of them can fire (observed: `predicates.py` 1059,
`scheduler.py` 2251, `predicates.py` 1631). The only rule that fires is
`quarantined`, once, and it frees no seat (observed: s154).

## 1. Which ruling or design made the two counts

- **`loop_cap` 10.** The value was a literal `10` in `tests_failing`. It
  became the setting `loop_cap` on 2026-08-09 20:36 in 7e3be756,
  "refactor(laws): amendments, and the settings the principal owns", with the
  checklist a409486b of the same evening (observed: `git log -S loop_cap`).
  It "spends compute", so it is generous (observed: `config.py` 59 to 61).
  The value never changed (observed: `git log -L` on the setting, one commit).
  No frame number: the build predates the frame series. Rota workflow.
- **The read of `loop_cap` in `exhausted`.** Added on 2026-08-09 21:09 in
  9b6499d4, "fix(scheduler): exhaustion escalates rather than going quiet"
  (observed: `git log -S "def exhausted"`, `git log -L` on line 1059). Its
  premise: `tests_failing` goes quiet above the cap, so the ladder takes over
  at the same count (observed: the commit body). Changes since: a75206de,
  2026-09-24, frame 79, the rung derives from sessions and an open message
  to the Developer holds the ladder; a6278c08 and 48e81d4f, 2026-09-25, frame
  86, `preempt`'s `do:park` defers a batch past its cap with a spent ladder,
  and `parked` reads the same `loop_cap`; 52d9de21 and 4840fda0, 2026-09-27,
  frame 88, the findings ladder (observed: `git log -S loop_cap --
  rota/core/predicates.py`). None of them reads the tick key.
- **`tick_attempt_cap` 3.** Added on 2026-08-11 04:02 in 90f09152, "fix(scheduler):
  a tick that cannot drain", for the first foreign repository, where a survey
  wake never drained (observed: the commit body; `config.py` 121 to 128). No
  frame number. Rota workflow. The value never changed (observed: `git log -L`,
  one commit). Its follow-ups fc5033ec, 883d6c7b and e657054a, 2026-08-11 to
  2026-08-12, made the quarantine terminal and kept its evidence (observed:
  `git log -S tick_attempts`).
- **The changes that broke the premise.** 9d2693db, 2026-09-24 20:54, frame
  83, after night 92: "A key that names a live batch keeps its count while
  its wake is absent, and a head commit or a moved test or criterion resets
  it" (observed: the commit body; `scheduler.py` 2490 to 2496). 09fb1d90,
  2026-10-24 14:06, frame 318, after night 162: "a head commit lifts a
  failing-tests key only when the red moves" (observed: the commit subject).
  Frame 318's review 1 wrote that "Law 6 still bounds the loop through
  `tick_attempt_cap` and `loop_cap`" (observed: `plans/stack.md` frame 318,
  status 2026-10-24 13:59). That sentence did not test how the two counts
  meet (reasoned: the review checked the lift, not the ladder).
- **A rule for a quarantined running batch.** `rota/DECISIONS.md`,
  `rota/LAWS.md`, `plans/principal-flow.md` and `rota/design/` hold none
  (observed: `grep -i quarantin`; `principal-flow.md` has no hit). The
  nearest records: law 6 says a wake past its cap is "quarantined and said
  out loud" (observed: `LAWS.md` 191). The `quarantined` predicate keeps the
  key of a running batch on the report "because a running batch has no park"
  (observed: `predicates.py` 1747 to 1751). The ruling of 2026-09-27 parks a
  given-up batch only when it is `deferred` (observed: `scheduler.py` 2241 to
  2249). `DECISIONS.md` 1546 to 1550 says "A stuck Tester or Developer step
  still needs a moved row, law 6", marked reasoned, not ruled. So the answer
  is a page, once, and then nothing (reasoned: from the four records).

## 2. Which rule should free the seat

- **Law 6's ladder** promises that "Budget exhaustion escalates one rung",
  that at the Liaison "It is never silence", and that "The attempt caps and
  the ladder bound a cycle" (observed: `LAWS.md` 185 to 191). Table row 6
  names `predicates.exhausted` as the rule that climbs it (observed: line
  398). The ladder is Developer, Architect, Vision Keeper (observed:
  `predicates.py` 46), and the Liaison's page follows from the Vision Keeper.
- **The tick quarantine** promises one report: `quarantined` says out loud
  what passed its cap, and sets `reported = 1` (observed: `loop.py` 331 to
  336; night 168 `tick_attempts`, `reported = 1`). It promises no rung and no
  park.
- **`parked` and `preempt`** read `failing_attempt` against `loop_cap`, or a
  given-up key of a `deferred` batch (observed: `scheduler.py` 2245 to 2251).
  `preempt` parks a running batch only when `parked` holds and
  `_next_rung` is empty, and preempts otherwise only on a strictly higher
  priority (observed: `predicates.py` 1631 to 1635).
- **Where batch_1 falls.** A running batch with a quarantined key and 6 run
  attempts is below every rule's count. `tests_failing` is quarantined,
  `exhausted` reads 6 < 10, `parked` reads 6 < 10 and not `deferred`, and
  every item holds priority 1 (observed: `plans/night168-read.md` line 85).
  This is a default nobody named (reasoned: no record states the case, and
  the premise of 90f09152 that made the case impossible was removed by
  9d2693db and 09fb1d90).
- **The rule that should free the seat is law 6's ladder through
  `exhausted`** (reasoned: law 6, `LAWS.md` 185 to 191, names exhaustion of
  any budget, and the tick key's quarantine is the budget that ran out
  first). The park then follows by the existing `do:park` of frame 86, once
  the ladder is spent.

## 3. What the records of night 168 show after s154

- **Batch status.** `batch_1` is `running` at head d607d440. `batch_2` and
  `batch_3` are `pending` with no head and no worktree (observed: `batches`).
- **Tick attempts.** `developer|tick:tests_failing|batch_1` has 3 attempts,
  `quarantined = 1`, `reported = 1` (observed: `tick_attempts`). The three
  dispatches at attempt 6 are s147, s149 and s150 (observed: `sessions`).
  The table holds no time. The quarantine falls between s150 and s154, the
  session that reported it.
- **Run attempts.** The newest attempt is 6, at d607d440: `tst_crit_1` and
  `tst_crit_2` `error`, 35 tests `pass` (observed: `test_runs`;
  `test_run_journal` seq 211 to 213). The Developer's `code.commit` in s153,
  s167 and s169 returned "committed: False, why: nothing changed", so no new
  head and no new run came (observed: `turns`). The ladder read 6 against 10.
- **The page.** s154 woke on `tick:quarantined`, detail "1 abandoned:
  tests_failing for batch_1 (developer), 3 attempts", and sent page m47
  (observed: `sessions`, `tool_calls`, `messages` seq 48). He answered "keep
  fixing it" (m48, m49), and the relay went to the Terminologist (m50, s157).
  Page m53 (s161) and the shift pages followed. Every one of the 23 messages
  to him reads `answered` at the end (observed: `messages`).
- **The shift page's offer line.** "now: answer its open page first, then the
  new request." It is a fixed line, and it does not read whether a page is
  open (observed: `rota/roles/principal.py` 1643). The row said "The team
  stopped after 3 attempts, because the tests still fail. What it waits on: a
  new start of its work" (observed: s199 `wake_detail`).
- **The pending batch.** `batch_2` landed its annotate (s186) and touch note
  (s187), and he approved on m73. `batch_start` returns nothing while
  `batch_1` runs with a head commit (observed: `scheduler.py` 496 to 514).
- **Walk 1.** No tick wake named `batch_1` after the quarantine. Only message
  wakes reached the Developer: s167 (relay m58) and s169 (answer m60), and
  neither committed (observed: `sessions` after s154; `turns`).
- **Walk 2.** No wake fired for `batch_1`. s174 was a shift page for the
  item, and `batch_2` stayed `pending` (observed: `sessions` s174 to s187).
- **Walk 3.** No wake fired for `batch_1`. s199 was a shift page for the
  item, and `batch_3` stayed `pending` (observed: `sessions` s199 to s226).

## 4. How often the shape appeared before

**2 walks, both on night 168: walks 2 and 3** (observed: the end state of
`clickI_night168.db`; `plans/night168-read.md` section 1). Walk 1 ended at
the quarantine before `batch_2` existed. Over nights 160 to 167 the end state
shows the shape 0 times (observed: `batches` and `tick_attempts` of 9 files).
One near case: night 164 ended with `bg_2` running under a quarantined
`tests_failing` key and `bg_1` `deferred`, not `pending` (observed:
`clickI_night164.db`). The count reads only the end state of each file, so a
walk that ended in the shape and then moved on is not counted (reasoned: one
file holds all the walks of a night).

Frame 312 does not name the shape. It names the stopped page's text and a
parked batch's stuck tick on the shift page (observed: `plans/stack.md` line
1570). Frame 318 does not name it either. It makes the quarantine stay on an
unchanged red, which is one of the two changes that make the shape reachable
(observed: line 1490; reasoned: question 1).

## 5. Whether a design departure stands

No ruling of Roman's covers a quarantined running batch, the ladder's count,
or the one batch seat (observed: the search of question 1). The nearest
rulings are law 6 of 2026-09-13, the park of a given-up deferred batch of
2026-09-27, and "Priority chooses, and the schedule constrains" of
2026-09-24 (observed: `LAWS.md` 189; `scheduler.py` 2241; 1665 to 1666).
The build did not depart from any of them. It left the case out when frames
83 and 318 changed when a key resets (reasoned).

## The repair

One check, "the batch stopped bouncing", reads `failing_attempt >= loop_cap`
or a quarantined `developer|tick:tests_failing|<batch>` key of a running
batch, and `exhausted` and `parked` both read it. This restores law 6's
"Budget exhaustion escalates one rung" and "never silence" for the first
budget that runs out, with no new count, and frame 86's `do:park` frees the
seat when the ladder is spent. Red test, from night 168's rows after s154:
`exhausted` wakes the Developer's first rung for `batch_1`, and after the
three rungs `preempt` gives `do:park` and `batch_2` starts.

## Usage

One agent on Opus, about 60k tokens of context. Not read: the time of the
quarantine, which `tick_attempts` does not store; the walk boundaries inside
the earlier night files.
