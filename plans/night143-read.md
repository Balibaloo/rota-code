# Night 143 read: bg_6 stops at attempt 1 on an inherited test that its own Developer broke

Rota workflow throughout, except where a line says meta workflow. Read on
Opus, 2026-10-12 16:08 to 16:22 by the clock.

Sources:

- The copy `scratchpad/n143/clickI_night143.db`, made at 16:08 from
  `.rota/clickI_night143.db`. The live file had no `-wal` beside it, so the
  copy holds every row: 528 sessions, s1 to s528, and messages to m361.
- `.rota/night143.log`, 237 lines, and `.rota/night143.err`, one line,
  "Preparing worktree (detached HEAD 3a3cd94f)".
- `.rota/clickI.principal.jsonl`, the rows from 2026-10-12T12:05 onward,
  read only.
- The tree at 3a3cd94f in `C:/Users/roman/rota_night143`, read only:
  `rota/core/sandbox.py`, `rota/core/fence.py`, `rota/core/harness.py`,
  `rota/roles/api.py`, `rota/roles/principal.py`, `rota/core/scheduler.py`.
- `git show` and `git diff --stat` in `D:/repos/_AI/sample_repos/clickI`,
  read only, on 02f8a5ec (bg_3's merge, the base of bg_6) and 61e70eca
  (bg_6's head).
- The cycle read of bg_5, `plans/night143-cycle-bg5.md`. This read does not
  redo it. Section 1 adds bg_5's tail after s463 and counts bg_6 the same
  way.
- Scripts in `scratchpad/n143/`: `dump2.py`, `wake.py` (from the cycle
  read), and `inh.py`, `resp.py`, `fix6.py` (this read).

The six batches: bg_1 `echo_json`, abandoned before a build; bg_2
`confirm_default_on_eof`, abandoned; bg_3 the same item, merged; bg_4
`version_option_show_python`, abandoned before a build; bg_5 and bg_6 the
same item, abandoned (observed: `batches`, log lines "do:cancel" and
"do:merge").

## 0. The answer in brief

| Frame | Measure | Night 143 |
|---|---|---|
| 200, the build loop | attempts to a merge on sentence three, target within 4 | bg_5: no merge in 8. bg_6: no merge, stopped at attempt 1. Tester bodies that reach the `show_python` branch: 0 of 7 on bg_5, and bg_6 has no Tester body |
| 215, the criterion repair surface | batches whose Tester tests fail at import of the surface's module, from 1 of 2 | 0 of 3 batches with a Tester test, 0 of 6 in all |
| 204, the seat's note | `conflict` rows, from 29 misplaced on night 142 | 37 `conflict` rows, 37 misplaced; 8 `invented` rows; no merge waited on a note |
| 210 and 209, the inherited test | a red inherited test shown as passing; an agenda crash | wake blocks 0 of 23 wrong; one seat call cut before the red row's state; no crash, 0 notes about an inherited test |
| 207, the filter | an inherited test that runs without its batch's filter | 0 of 6 runs of bg_3's tests in bg_5 and bg_6 red; the base run is recorded for 4 batches |
| 198, the agenda page | pages after a merge that carry the merged request's open rows | 1 of 12 `present` pages after bg_3's merge |
| 219, the decision overwrite | principal decisions that a seat overwrote, from 1 | 4 |

**bg_6 reached the stop page at attempt 1 because of the tick quarantine,
not the challenge ceiling or the cap.** Its Developer broke three inherited
tests with a blind rewrite. Then the fence refused its restore of the
project's own line, and three wakes ended with no landed change (observed:
section 1.2). Neither `LANDED_CHALLENGES_CEILING` nor the per-body cap
carried over from bg_5. So no defect of pass 4b shows on this night
(reasoned: section 1.3).

**Two new candidate frames.** First, the fence's baseline is the working
file, so a restore of a reach that the base commit held is refused
(observed: s524). Second, a Vision Keeper's `problem.assert` under a live
item's id rewrites the principal's request, and the cancel then abandons
the batch: bg_2 and bg_5 (observed: s342, s467). Section 8 has both, with
sites.

## 1. Frame 200, the build loop

### 1.1 bg_5's tail after the cycle read

The cycle read stopped at s463 and attempt 7. bg_5 ran one more harness
attempt and then was abandoned (observed: log lines after m302).

| Session | Seat, wake | Calls that matter | Result |
|---|---|---|---|
| s462 | terminologist, relay m306 of the principal's m303 | `criteria.respecify` | the criterion text gains "The test must run a command with the version option turned on and read what it prints to verify the output"; `msg.answer_tester`, m308, refs only |
| s464 | tester, answer m308 | `tests.encode` 3 times | 2 refused, then body 7 admitted (tests v19) |
| s465 | developer, `tests_failing` attempt 8 | `msg.challenge_tester`, `msg.escalate_architect` twice | m309 landed |
| s466 | architect, escalate m309 | `msg.challenge_vision_keeper`, then `msg.propose_vision_keeper` 5 times | m310 with the quote `assert "Python" in result_with.output`; m311 |
| s467 | vision_keeper, challenge m310 | `problem.assert(version_option_show_python, ...)`, `decisions.author("d_1b0161775a", ...)` | the assert landed on the live item (items v98); the decision row overwrote a principal's row (section 7) |
| none | the scheduler | `do:cancel` | "abandoned bg_5: its item is no longer schedulable" |

(observed: `tool_calls`, `receipts`, `messages`, the log.)

Body 7 reads the principal's words in its wake. s464's first turn holds
"read what it prints" twice, from the criterion text. The body still invokes
`["cmd-with-flag", "--show-python"]`, a switch the decorator does not add.
The seat's own reasoning says why: "I don't have access to the actual
implementation of `version_option`. The criterion says 'The test must run a
command with the version option turned on'. This implies there's a flag like
`--show-python` that needs to be passed" (observed: s464 turn 3 completion).
The red at s465 is `Error: No such option '--show-python'`, raised at the
test's own assertion, with no Python version in the output (observed: s465
`[tests.load]`, tr148).

bg_5's abandon: s467 asserted the item again with the old text "The
`version_option` includes a `show_python` flag that appends the running
Python version to the message." The door admitted it, after three refusals
on test and criterion ids (observed: s467 turns 2 to 6). The cancel line
follows s467 and precedes s469's m312 in the log (observed). That the assert
reset the item's approval is reasoned from the cancel's own words, "its item
is no longer schedulable", and was not re-run.

### 1.2 bg_6's turns

bg_6 is a new batch on ticket `tk_3`, with three new criteria, `ver_show_py`,
`ver_show_py_off` and `ver_show_py_source`. Its base is 02f8a5ec, bg_3's
merge (observed: `batch_tickets`, `criteria`, `git log`).

| Session | Seat, wake | Calls that matter | What came back | Committed |
|---|---|---|---|---|
| s515 | architect, `tick:annotate` | `batches.annotate` | expected: `core.py`, `core.py::Command`, `decorators.py::version_option`, five `tests/test_basic.py` tests | batch_touch |
| s516 | liaison, `tick:touch_note` | `msg.present_principal` | m353, the "Before I build this" page | message |
| s517 | liaison, converse m354 | `rulings.rule` | landed, r_b4e9d445ca: `bg_6` contest, `ver_show_py` contest | rulings |
| s519 | architect, relay m356 with "Line 5 shouldn't need to touch the Command class in core.py" | `batches.annotate` 4 times, each `["src/click/decorators.py::version_option", "src/click/core.py::Command"]` | admitted | batch_touch keeps `core.py::Command` |
| s520 | terminologist, relay m357 | `criteria.respecify(ver_show_py)`, `msg.answer_tester` | respecified; the answer refused, "no change built from this criterion has a commit yet" | criteria |
| s521 | developer, `tick:batch_start` | 16 `code.source`, 2 `code.write` | both writes refused by the parser, "a quote inside a quoted argument ended the string early"; the `version_option` source "dropped to fit the window" | nothing; fault f_eb8c55cc19 |
| s522 | developer, `tick:batch_start`, "attempt 2 of 3" | 20 `code.source`, 3 refused as "served three times", then `code.write(decorators.py, start=420, end=558)`, `code.commit` | the write admitted; commit 61e70eca, 10 insertions and 133 deletions in `decorators.py` | 61e70eca |
| harness | | | 37 tests, 1 not passing: `inh_dcc9ea38`, `tests/test_basic.py`, 3 failed, `TypeError: Parameter.__init__() got an unexpected keyword argument 'cls'` | |
| s523 | developer, `tests_failing` attempt 1 | `msg.challenge_tester` 4 times, `code.write(start=420, end=-1)` | each challenge refused; the write refused, "this rewrite of src/click/decorators.py drops custom_version_option, help_option" | nothing |
| s524 | developer, the same | `msg.challenge_tester` 4 times, `code.write` that restores the original `version_option` | the challenges refused; the write refused by the fence, "reaches the dynamic at line 517 (import importlib.metadata)" | nothing |
| s525 | developer, the same | `msg.challenge_tester` 2 times, 4 `code.write`, 7 `tests.load` | the help_option door; one write `unchanged`; the `tests.load` result cut | nothing |
| s526 | liaison, `tick:quarantined`, "1 abandoned: tests_failing for bg_6 (developer), 3 attempts" | `msg.present_principal` | m358, the stop page | message |
| s527 | liaison, converse m359 | `rulings.rule` 3 times | the line 5 contest refused twice; then line 1 `contest`, r_3e3d5d1fc6 | rulings |
| s528 | liaison, verdict m360 | `msg.relay_vision_keeper` | m361; then `do:cancel`, "abandoned bg_6: its item is no longer schedulable" | message |

(observed: `sessions`, `tool_calls`, `receipts`, `test_runs` tr149 to tr185,
the turns of s515 to s528.)

**The Tester never woke on bg_6.** `tests` holds no row of bg_6 with a
criterion. The Developer broke an inherited test at attempt 1, the
`tests_failing` tick took the three wakes, and the quarantine came before a
`tests_missing` wake (observed: `tests`, `sessions` s521 to s528).

**The Developer's diff broke the product.** s522 read `version_option` at
lines 420 to 558 twice, and the window dropped the answer each time. The
third read was refused, "served three times this session, and the window
took it each time". The seat then wrote the function from memory: "Let me
reconstruct what I need to know about it from the partial reads I already
have" (observed: s522 turns 15 to 21). The write replaced the 138-line
function, with its `importlib.metadata` lookup, by a stub that passes
`cls=Option` to `Option` (observed: `git diff --stat 61e70eca~1 61e70eca`,
the `[code.diff]` block of s523). No door refused the write. This is frame
139's shape, two reads that drop each other from the window, and frame 173's
shape, an admitted span write that removes a branch with no note (reasoned:
the headings of `plans/stack.md`).

**The Developer then read the cause and tried the right fix.** s523 turn 9:
"My diff broke it by removing the entire `version_option` implementation and
replacing it with a stub". s524 turn 10: "I must restore the original
`version_option` implementation from `code.diff`, then add the new
`show_python` flag on top of it" (observed). The restore was refused:

> ERROR code.write: src/click/decorators.py reaches the dynamic at line 517
> (import importlib.metadata) and no criterion of this batch names loading or
> evaluating code.

Line 513 of `decorators.py` at the base 02f8a5ec is `import
importlib.metadata` (observed: `git show 02f8a5ec:src/click/decorators.py`).
The fence compares the write with the file as it stands, after s522's
commit removed the line. So the project's own reach reads as new (observed:
`rota/roles/api.py:12658-12666` and `rota/core/fence.py:142-166` at
3a3cd94f). Section 8, candidate 1.

### 1.3 Why bg_6 stopped at attempt 1

**The cause is the tick quarantine.** `tick_attempts` holds the key
`developer|tick:tests_failing|bg_6` at 3 attempts, quarantined. The cap is
the configuration's `tick_attempt_cap`, 3 (observed: `tick_attempts`;
`rota/core/config.py:121`). s523, s524 and s525 each woke at attempt 1 and
ended with no landed write, so the harness never ran a second time and the
key reached 3 (observed: section 1.2). s526's stop page followed.

**The ceiling and the cap did not fire, and nothing carried over from
bg_5.**

- The Developer sent `msg.challenge_tester` 10 times on bg_6, each with refs
  `['ver_show_py', 'inh_dcc9ea38']` or `['ver_show_py_source',
  'inh_dcc9ea38']`. All 10 were refused with "inh_dcc9ea38 has no criterion:
  it is the project's own test and it passed before this batch. A challenge
  has no side there. Read code.diff and restore what your change broke". No
  message from the Developer to the Tester exists on bg_6 (observed:
  `tool_calls`, `messages` m353 to m361).
- That refusal is the owner check at `sandbox.py:1219-1233`. It runs before
  `_challenge_cap_refusal` is reached, so the cap and the ceiling never read
  these calls (reasoned: the order in `_challenge_evidence` and `_bind_send`
  at 3a3cd94f, not re-run).
- Had a call passed, `_challenges_on` counts by criterion id
  (`sandbox.py:1653-1683`). bg_5's seven landed challenges name
  `ver_opt_show_py_tk2`, and bg_6's criteria are new ids. So a bg_6
  challenge on `ver_show_py` counts 0 (reasoned: the code and `messages`).
- `_challenge_admitted` was not called on bg_6. It gates the revert door's
  and the owner route's hints, and no bg_6 wake holds a revert step
  (observed: the wakes of s523 to s525 hold no "revert"; reasoned:
  `api.py:8112`, `api.py:13345`).

A latent point, reasoned and not observed: `_challenges_on` reads every
batch's messages, and an inherited test keeps its id across batches (frame
210). A key `("test", inh_x)` would count another batch's challenges. The
owner check refuses every challenge on such a test first, so the path is not
live at 3a3cd94f. No fix line is proposed.

### 1.4 The stop page at attempt 1

m358 says "The team gave up on: tests_failing for bg_6, 3 attempts", and
"check: none yet" on all three criteria. It does not name `inh_dcc9ea38`,
and it does not say that the batch's own diff broke a project test
(observed: jsonl m358). The principal answered on the predicted files:
"Please keep going with a fix and don't drop this change. Line 5 is wrong
because it still touches the Command class in core.py".

s527 ruled line 5 `contest` twice. The door refused it each time:

> ERROR rulings.rule: line 5: bg_6 is the change's line: a prediction of
> what it touches, and a ruling on it moves nothing. To stop the change,
> contest the item version_option_show_python, line 1. Otherwise approve
> line 5

The seat then ruled line 1 `contest`. That ruling stopped the change the
principal had asked to keep, and the cancel abandoned bg_6 (observed: s527
turns 2 and 3, r_3e3d5d1fc6, the log). This is frame 189's route. The
refusal's step offers only "contest the item" or "approve", and the seat
took the step that the principal's first sentence forbids (reasoned: frame
189's heading).

### 1.5 The count

| Night | Batch | Attempts | Merge |
|---|---|---|---|
| 138 | b_3 | 8 | no |
| 139 | bg_3 | 7 | no |
| 142 | batch_2, batch_3 | 10, 8 | no |
| 143 | bg_5 | 8 | no, abandoned after s467's assert |
| 143 | bg_6 | 1 | no, quarantined, then abandoned on s527's contest |

(observed: the log's harness lines, `sessions.wake_detail`; the rows for
nights 138 to 142 are copied from `plans/night143-cycle-bg5.md` section 6,
with its marks.)

**The target, a merge within 4, is not met.** bg_6 does not measure frame
200's path: it has no Tester body and no landed challenge (observed). Its
loop belongs to the fence's baseline and to the window, not to a cause the
frame named. By the residue rule the bg_6 cause is a new frame (reasoned:
section 8, candidate 1).

### 1.6 The baseline for pass 5

Fix 6's denominator query of `plans/frame200-pass5-design.md` section 11
gives 0 rows. No challenge on this night carries a Developer's reason row,
because pass 5 is not built at 3a3cd94f (observed: `fix6.py`).

The same text rule on every show_python body the Tester wrote after a wake
by another seat:

| Body | Tester, woken by | Next Developer wake | The rule |
|---|---|---|---|
| 2, v14 | s432, challenge m287 | s433 | own assertion, no version in the output: does not count |
| 3, v15 | s434, challenge m288 | s435 | RuntimeError under `src/`: does not count |
| 4, v16 | s436, challenge m289 | s437 | failed before any assertion: does not count |
| 5, v17 | s438, challenge m290 | s439 | RuntimeError under `src/`: does not count |
| 6, v18 | s440, challenge m291 | s441 | TypeError under `src/`, output empty: does not count |
| 7, v19 | s464, Terminologist answer m308 | s465 | own assertion, "No such option '--show-python'": does not count |

(observed: `fix6.py` over the wakes of s433 to s465.)

**The baseline is 0 of 5 bodies after an unreasoned challenge, and 0 of 1
after the principal's words in the criterion text.** bg_6 adds no body. The
reasoned denominator starts at 0 rows on night 143.

## 2. Frame 215, the criterion repair surface

**The ratio reads 0 of 3.** Three batches have Tester tests: bg_2, bg_3 and
bg_5. None of their reds fails at import of the surface's module. bg_1,
bg_4 and bg_6 have no Tester test (observed: `tests`, `test_runs`).

| Batch | Tester tests | First `E` line of the last red run |
|---|---|---|
| bg_1 | none | |
| bg_2 | 3 | tr36 `OSError: pytest: reading from stdin while output is captured!`; tr71 `KeyError: 'prog_name'`; tr72 `AssertionError: assert False` |
| bg_3 | 3 | none, all passed, merged |
| bg_4 | none | |
| bg_5 | 1 | tr148 the test's own assertion, "No such option '--show-python'" |
| bg_6 | none | |

(observed: `test_runs` tr36, tr71, tr72, tr108 to tr110, tr148.)

**A criterion repair ran 12 times.** Twelve Terminologist sessions on a
relay ran with the repair brief and called `criteria.respecify`: s240, s252,
s273, s328, s349, s403, s451, s462, s476, s487, s502 and s520 (observed:
`tool_calls`, the system text holds "surface_refs naming").

**Frame 215's respecify door did not fire.** No respecify on the night named
a surface outside the batch's expected files. Every landed surface is
`src/click/utils.py::echo_json`, `src/click/termui.py::confirm` or
`src/click/decorators.py::version_option` (observed: `criteria`, the
respecify results). The doors that the Terminologist met:

- "this rewrite names no surface, and the repair exists because the words
  alone could not be tested", s240 and s403.
- "is not a symbol the index knows. A surface is a callable a test would
  exercise; near matches: ['src/click/termui.py::confirm']", s240, s328 twice.
- "'get_python_version' is not a symbol the index knows, not a name the
  item or the ticket gives, and nothing in the worktree defines it", s403
  twice. This is `_vet_surface`, frame 218's door.
- "is a test (...), and a test is not a surface", s328.
- "a criterion names what the program does; this one names the Tester's
  job", s487.
- the `unchanged` note, "those are the criterion's own words", s240, s349,
  s403, s476 and s502. s476 sent the surface
  `tests/test_version_option.py::test_show_python_flag` with the old text,
  and the note answered on the words alone. The surface did not land
  (observed: s476 turn 1 and its result; `criteria`).

(observed: `resp.py` over the twelve sessions.)

**The encode import hints fired 3 times, and the load check passed each
time.** The surface's module loaded, so the hint named the import line
(observed: `api.py:6488-6504` at 3a3cd94f). The seat's words in each:

- s320, twice: "the test uses monkeypatch and never imports or defines it:
  a NameError against any code. The criterion's surface is
  src/click/termui.py::confirm: add `from click.termui import confirm` and
  assert on what it returns."
- s464: "the test uses cli and never imports or defines it: ... add `from
  click.decorators import version_option`".

The added line does not bind the missing name in either case. `monkeypatch`
is a pytest fixture, and `cli` is a group the test itself must define
(reasoned: the bodies in `tool_calls`). Section 8, candidate 3.

The surface door fired once on s452, as the cycle read found: "the surface
'src/click/decorators.py::version_option' lives in decorators.py and this
test imports from click.testing". The seat logged it as fault f_e7c2eb8810
(observed).

## 3. Frame 204, the seat's note

**37 `conflict` rows, and 0 of 37 is a disagreement between two sources.**
All 37 came from Vision Keeper sessions on `tick:reconcile` during
onboarding, s12 to s46 (observed: `ledger`, `receipts`). By the second
source in each row:

- 25 pair the README sentence with unrelated docs text or the word `None`,
  for example "the code shows Arguments are positional in nature" (s12), or
  "You should use [Virtualenv]" (s44).
- 9 restate the item's own words or another README sentence (s28, s29, s35,
  s37).
- 3 on `@prose` agree with the code: "version_option decorator is defined"
  (s30).

(reasoned: the 37 texts, against section 8 of `plans/frame204-design.md`.)

Night 142 had 29 misplaced `conflict` rows. Night 143 has 37 (observed: the
count; night 142's number is copied from frame 204's status of 05:51).

**Who answered each.** The rows reached six onboarding pages, m11, m15, m38,
m65, m72 and m76, seven rows a page at most. The principal ruled them wrong
at each page: "Lines 2 to 8 are wrong: each one just pastes the README
description beside an unrelated note" (m11). 36 rows were closed by a
principal decision "overruled at signoff". 1 row, `l_e2846395b5`, is
`resolved` with no decision that names it (observed: `messages.body_refs`,
`decisions.resolves_ledger`, the jsonl).

**8 `invented` rows.** 5 come from the Tester's literal door (s309, s312,
s366 twice, s434), 1 from the Terminologist on a ticket id (s420), and 2
from the Terminologist on glossary terms (s506). 2 were closed at a page:
`l_68388ce596` (s434, "the test assumes cmd where the material is silent")
on m302, and `l_c438d9424c` on m302. 6 stay open (observed: `ledger`,
`decisions`).

**No merge waited on a note.** bg_3 merged with `l_3ecb6f7525` and
`l_562e3810d1` open, two `invented` rows on its criteria `cr_1` and `cr_2`
(observed: `ledger`, the log's merge line). Pass 1 at c9e915c5 builds no
merge hold, so this is the design's behaviour (reasoned: frame 204's status
of 2026-10-11 17:16).

**The Tester sentence of pass 1f.** No Tester triaged `outside_fact`. Two
Testers triaged `cannot` and then sent `msg.question_researcher`: s321, m207,
"How do I test that confirm() raises an exception or aborts when stdin is
closed and default_on_eof=False?", and s323, m208, "What was the observable
behavior of confirm() when stdin closed and no default_on_eof flag was
passed before this change?" (observed: `tool_calls` `tests.triage`,
`messages`). Neither question is a fact that another spec defines. Both ask
about the project's own code (reasoned: the question texts).

The Researcher woke on each, s322 and s324, called `references.load`, and
sent nothing. s324's reply text, which no seat reads: "confirm() behaved
exactly as it did prior to the change, regardless of the state of stdin".
m207 and m208 are stamped `answered` with no answer row (observed:
`messages`, s322 and s324 turns, `receipts` empty). This is frame 174's
shape (reasoned: frame 174's heading).

**The fault table.** 5 rows, all open (section 7, the fault row).

## 4. Frames 210 and 209, the inherited test

**Frame 210: the wake block showed the right state in 23 of 23 Developer
`tests_failing` wakes.**

| Batch | Inherited tests | Red runs of an inherited test | Wakes | Shown red | Shown passing while red |
|---|---|---|---|---|---|
| bg_2 | 34 | 0 | 7 | 0 | 0 |
| bg_3 | 34 | 0 | 0 | | |
| bg_5 | 37, 34 and bg_3's 3 | 0 | 13 | 0 | 0 |
| bg_6 | 37 | 1, `inh_dcc9ea38` at 61e70eca | 3 | 1 in 3 of 3 | 0 |

(observed: `inh.py` over the `[tests.load]` block of each wake; `tests`,
`test_runs`.)

In bg_6 the block's group is "the project's own tests, not passing at your
commit", with the test's output (observed: s523 turn 1). So the fix of
a2b70a84 holds on the wake.

**One seat call shows the red row cut before its state.** s525 called
`tests.load(batch_id='bg_6')` and got a result cut at 6,000 of 38,174
characters: "CUT the result: 32,174 of 38,174 characters are not shown".
The red row keeps its body by design, and `tests/test_basic.py` is 27,796
characters. The cut fell inside that body, before `last_result` and `said`
(observed: s525 turn 10 user text). The seat then wrote "The test suite
shows all tests passing (`"pass"`)" (observed: s525 turn 17). This is frame
127's shape, a red row with a whole body that the cut then removes (reasoned:
frame 127's heading). It is not frame 210's sign, because the row's run is
bg_6's own.

**Frame 209: no crash, and no note to test it.** `night143.err` holds one
line, and the night ran until this session stopped it at 16:07 (observed).
The ledger holds 0 rows whose `about_ref` is an inherited test (observed:
`ledger`). So the agenda tick's path for such a note did not run on this
night.

## 5. Frame 207, the inherited test's filter

**No inherited test was reddened by the filter.** bg_3's three Tester tests
are inherited by bg_5 and bg_6 as `inh_e302a797`, `inh_ee2da252` and
`inh_b813b704`. They passed in 6 of 6 runs, tr135, tr141, tr143, tr173,
tr179 and tr181 (observed: `test_runs`).

**The base run is a record for every built batch.** `config` holds
`base_run:bg_2` 34 pass, `base_run:bg_3` 34 pass, `base_run:bg_5` 37 pass and
`base_run:bg_6` 37 pass (observed: `config`).

**The door's sentence agrees with the record.** The bg_6 door said "it
passed before this batch" 10 times, and the wake said "they passed before
this batch. Your diff broke them" (observed: s523 to s525).
`project_tests_fact` returns None when the base run passed every named test,
and the caller then prints its own sentence (observed: `sandbox.py:1431-1480`).
So the words come from the fallback text, and the base-run record makes them
true: `inh_dcc9ea38` is `pass` at bg_6's base (reasoned: the code and
`config`).

## 6. Frame 198, the agenda page

**1 of 12 `present` pages after bg_3's merge carries a row of the merged
request.** m252, the first page of the show_python request, line 2: "The
criteria require adding a default_on_eof flag to confirm(). ... I will add
the flag and handle EOF by returning the default when the flag is True."
That is `l_c1040dd2ec`, a Developer note of bg_2 on the confirm request,
open at the merge (observed: jsonl m252, `messages.body_refs`, `ledger`).
The principal: "Line 2 is wrong because the confirm flag is a separate
request and does not belong in the Python version change. Please remove
line 2."

The correction cost three wakes. The contest went as relays m255, m256 and
m257. m257 woke Developer s391 with no batch. s391 logged two `blocked`
faults: "The principal verdict mentions removing line 2, but no such line
exists in the current codebase" (observed: `messages`, `faults`).

A second page carries a row of a parked request. m302, line 3, is the
Critic's challenge on the `echo_json` constraint. The principal: "Line 3 is
about the echo_json helper from my first change, so please take it off this
page" (observed: jsonl m302). `echo_json` was parked, not merged, so this is
frame 193's hold, which frame 198 names (reasoned: frame 198's status).

The 12 `present` pages counted: m252, m263, m272, m282, m295, m300, m302,
m316, m326, m339, m353 and m358 (observed: jsonl, after the log's
"do:merge: merged bg_3").

## 7. The other shapes

- **bg_1 and bg_4: a correction landed as a contest on the item.** On m141
  the principal corrected line 4 and line 1. s237 ruled lines 1, 2, 3 and 5
  `contest` and line 4 `approve`, the reverse of the principal's line 4
  (observed: s237 turn 1). On m263 the principal named line 3 only. s400
  ruled lines 1, 2 and 3 `contest` (observed: s400). Each contest on line
  1, the item, made it unschedulable, and the cancel abandoned the batch.
  This is frame 185's mechanism, a correction that lands as a contest on the
  item, more than frame 189's. Neither page's correction was a predicted
  file (reasoned: frame 185's and frame 189's headings).
- **m111 and m126: the principal's answers landed as requests, frame
  214.** The principal answered the clarify m109, and the reply landed as
  the converse m110. Liaison s209 called `brief.segment` on that reply and
  made statement s2, then the confirm m111. The principal said: "That's not
  a new request. It's my answer to your question about the page for the
  first change". The ruling on m111 was `{"s2": "approve"}`, and s2 was
  ratified. m124, m125, s221, s3 and m126 have the same shape (observed:
  `tool_calls` s209 and s221, `statements`, jsonl). The route is the
  converse mode's `brief.segment` on a clarify reply. Frame 214's ends-when
  names a reply to a `said` message, so its door would not cover this path
  (reasoned: frame 214's site line).
- **bg_2: abandoned by a Vision Keeper's assert, not by frame 185.** The
  stop page m209 drew "Please don't drop this change". The ruling kept the
  item approved: `confirm_default_on_eof` approve, `cr_2` and `cr_3` contest
  (observed: r_416255fe2f). Later, Architect challenge m221 quoted the
  Tester's wrong answer m218, "The `default_on_eof` flag does not alter the
  behavior of confirm() when stdin is closed; it must still raise Abort."
  Vision Keeper s342 then sent `problem.assert("confirm_default_on_eof",
  "The `default_on_eof` flag does not alter the behavior of `confirm()` when
  stdin is closed; it must still raise `Abort`. The flag is off by
  default.")`, and the door admitted it 4 times (observed: s342 turns 2 to
  6). The cancel abandoned bg_2. The next page showed the principal his own
  request reversed, and he said "Line 1 is wrong because it says the flag
  never changes what happens on closed stdin, but I asked for the opposite"
  (observed: jsonl m224). In the same session `problem.describe` was refused,
  "confirm_default_on_eof is the principal's own words, so it asks for
  something" (observed: s342 turn 6). `problem_assert` at `api.py:1217-1447`
  has no such check, and `problem_describe` has it at `api.py:1515`
  (observed: the tree at 3a3cd94f). Section 8, candidate 2.
- **The Vision Keeper's overwrite, frame 219: 4 principal decisions, not
  1.** A diff of the 15:28 copy against the final copy finds
  `d_1b0161775a`, "default taken at signoff: The version_option callable
  accepts a show_python boolean flag", overwritten by s467 with author
  `vision_keeper`. Each session's first turn shows the id with `"author":
  "principal"` in `decisions.search` before the seat wrote under it. The
  four rows are `d_a54ff9743f` (s278), `d_d5e7673701` (s415),
  `d_04589009a6` (s443) and `d_1b0161775a` (s467) (observed: the two
  copies, the first turns of the four sessions). s342's `d_9f3a7d4e1f` was
  a new id, and s489 later rewrote that Vision Keeper row for another item
  (observed). Frame 219's second ends-when part reads "from 1 on night 143".
  The count is 4.
- **The fault row "Rota itself failed 1 time this run".** The line counts
  open `faults` rows (observed: `rota/roles/principal.py:308-312`). At walk
  2's end the one open row was f_789659c8eb. Developer s365, at bg_3's
  `batch_start`, was refused a write to the Tester's file, "the tests are
  the Tester's", and logged "test file was rewritten with new tests for
  default_on_eof, but the harness runs tests on record. I cannot pass a test
  that does not match its criterion." The door worked as designed (observed:
  s365 turns 5 to 9). The night ends with 5 open faults. 1 points at a door
  sentence that names a wrong cause, f_e7c2eb8810 (frame 216's shape). 2 are
  s391's misread of a page line (section 6), and 1 is a parser refusal of
  the seat's own quoting, f_eb8c55cc19 (reasoned: the five texts). Frame
  204 covers the faults table and its question 0, "a rule that works as
  designed is no note". The line tells the principal that rota failed when
  no rota part failed (reasoned).
- **The two items left contested at onboarding, frame 187.**
  `defines_commands_and_options` and `provides_command_line_interface`. The
  contested tick woke the Vision Keeper three times on each, s133, s136 and
  s137, then s146, s149 and s152, and quarantined. The tick woke it again in
  walk 1, s177 to s186, and quarantined again at s189. The wakes wrote
  decisions under ids built from the item's own id,
  `defines_commands_and_options_defended` and
  `provides_command_line_interface_defended` (observed: `sessions`,
  `decisions`). Both items are `approved` at the night's end (observed:
  `items`). Frame 187's heading names this shape.
- **The stop page that says "3 attempts" at attempt 7.** The number is the
  quarantine counter of one tick key, not the harness attempt.
  `_stalled_words` reads `tick_attempts.attempts`, which stops at
  `tick_attempt_cap`, 3 (observed: `rota/roles/principal.py:1120-1130`,
  `rota/core/config.py:121`). So every stop page says 3: m295 and m300 at
  attempt 7, m358 at attempt 1, m209 on `tests_missing`. No open heading of
  `plans/stack.md` names this page line (reasoned: the headings).
- **Frame 196's shape on bg_6.** Architect s519 held the principal's words
  "Line 5 shouldn't need to touch the Command class in core.py" in its wake.
  It annotated `src/click/core.py::Command` again, 4 times (observed: s519
  turn 1 and its calls, `batch_touch`). The principal repeated the point on
  m358.

## 8. Candidate frames, new

1. **The fence's baseline is the working file, so a restore of the
   project's own reach is refused.** Site: `rota/roles/api.py:12658-12666`,
   the `_baseline` read before `_fence.check`, and the docstring of
   `rota/core/fence.py:142-150`. Sign: s524, "src/click/decorators.py
   reaches the dynamic at line 517 (import importlib.metadata) and no
   criterion of this batch names loading or evaluating code", on a write
   that put back the base commit's line 513 (observed). Fix line: the
   baseline holds the reaches of the file at the batch's base commit as
   well as the working file, so a reach that either one made is the
   project's. Ends when: a door test on s524's write is red before the fix
   and green after; on a night, Developer writes refused by the fence for a
   reach that the base commit holds fall from 1 of 1 on night 143 to 0.
2. **A Vision Keeper's `problem.assert` under a live item's id rewrites the
   principal's request, and the cancel abandons the batch.** Site: the
   `problem.assert` door at `rota/roles/api.py:1217-1447`, beside the
   "principal's own words" check that `problem_describe` has at `:1515`.
   Sign: s342 on bg_2 and s467 on bg_5, 2 of 3 abandoned built batches on
   night 143 (observed). Frame 219 holds the same rule for a decision row,
   and frame 129 names the assert after a challenge. This sign is on the
   item row itself. Ends when: an assert under an item id that holds the
   principal's words is refused with the decision route named, by one door
   test on s342's call; on a night, batches abandoned after a seat's assert
   on their item fall from 2 to 0.
3. **The NameError door's import hint names the surface import for a name
   that the import does not bind.** Site: `rota/roles/api.py:6455-6504`.
   Sign: s320 twice on `monkeypatch`, s464 on `cli` (observed). Fix line:
   the hint names the surface import only when the unbound name is the
   surface's symbol or its module. A known pytest fixture is named as a
   test argument. Another name is named as a definition the test owes.
   Ends when: one door test per shape; the hint names a line that binds the
   name, 3 of 3 on night 143's calls.

Meta workflow: this read wrote no register line, and no frame of
`plans/stack.md` was edited.
