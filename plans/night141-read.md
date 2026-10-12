# Night 141 read

Night 141 ran cold from `C:/Users/roman/rota_night141` at c18f868c, 2026-10-11 22:15 to 2026-10-12 02:01, three sentences, the agent principal on Opus. Walk 2 crashed in the agenda tick, and walk 3 died at its first step (frame 209). Rota workflow throughout. Database `.rota/clickI_night141.db`, opened `mode=ro`. Log `.rota/night141.log`, errors `.rota/night141.err`, principal record `.rota/clickI_night141.principal.jsonl` (19 `call` rows of night 141). Phases by the request sessions: onboarding s1 to s100, walk 1 s101 to s157 (`m_p1` woke s101), walk 2 s158 to s198 (`m_p2` woke s158), walk 3 no session (`m_p3` at message seq 98, no session after s198). Scripts: the scratchpad folder `n141` of session 91506043 (`db.py`, `shape.py`, `turns.py`, `errs.py`, `dang.py`, `dang2.py`, `res.py`). Read 2026-10-12 02:12 by an agent of session 91506043. Not committed.

**Frame 200's measure is absent.** Sentence three, `version_option show_python`, never built. No batch, no Tester test and no attempt exist for it (observed: `batches` holds bg_1 and bg_2 only; `statements` holds s1 and s2). This read does not estimate the measure.

Verdicts, one line each:

- Q1. 198 sessions, 810 turns, 98 messages, 19 principal calls, 2.62 dollars. 2 batches, 1 merge. Sentence one merged as bg_1 in walk 1 after 68 steps. Sentence two, bg_2, crashed at attempt 1. Sentence three never started.
- Q2, frame 200. 1 Tester test in the night, on bg_1, and it runs the behaviour. 0 tests apply a decorator to a plain function, 0 read an attribute of a factory's return. bg_2 had no Tester wake before the crash. 4 refusals of `tests.encode`, 2 kinds. 3 Developer challenges, all refused at the door, 0 escalations, 0 answer wakes. **New defect, high: `tests.load` showed the bg_2 Developer every test as passing while 2 were red**, because it takes the latest run of a test id across batches.
- Q3, frame 207. Base run for bg_2: 35 of 35 pass. No inherited test was red at the base. The red tests came from the Developer's own diff in s197, which removed the answer loop of `confirm`. s198 never got the push of red tests or frame 207's base sentences, because of the Q2 defect. It read one sentence, the challenge refusal, three times.
- Q4, frame 204. 47 ledger rows: Vision Keeper 37, Developer 4, Liaison 3, Terminologist 2, Tester 1. 34 `conflict` rows: 0 a true two-source disagreement, 34 restatements that section 8 says to write as no note. 0 `faults` rows. 5 `ledger.log` refusals for a wrong kind, 0 for a missing kind.
- Q5. 34 dangling turns in 6 sessions. 12 distinct "unchanged" refusals after an eviction, 2 point at an answer the window dropped. Frame 208's shape repeats: 2 of 3 "The answer is in this prompt" refusals after an eviction are false, s18 and s33, on the answer `[]`.
- Q6. The principal misread 1 of 19 pages, m16, where it said the page was cut at line 10. One more answer, m14 in walk 1, answered a stale onboarding page with the new request, and the request still landed.
- Q7. 49 sessions hold zero receipts. 34 of them sent a message, which writes no receipt. 15 did no admitted work, in 5 shapes.

## 1. The night's shape

(observed: `shape.py`, the log, `items`, `tick_attempts`, `test_runs`, `batches`, the principal record)

| Phase | Clock | Sessions | Turns | Steps, asks | Principal calls, dollars | End |
|---|---|---|---|---|---|---|
| onboarding, cold | 22:15 to 23:51 | s1 to s100, 100 | 319 | 109 steps, 4 asks | 5, 0.69 | `ONBOARDED`, sign-off page m14 still open |
| walk 1, `echo_json` | 23:51 to 01:09 | s101 to s157, 57 | 291 | 68 steps, 8 asks | 8, 1.12 | `MERGED (1 total)`, bg_1, then the Stuck line |
| walk 2, `confirm default_on_eof` | 01:09 to 02:01 | s158 to s198, 41 | 200 | not logged | 6, 0.81 | crash, `AttributeError` in `_items_reached` |
| walk 3, `version_option show_python` | 02:01 | none | 0 | 0 | 0 | crash at step 1, the same traceback |

- Sessions by role: Vision Keeper 67, Liaison 51, Terminologist 37, Architect 23, Critic 14, Developer 4, Tester 2 (observed: `sessions`).
- Asks to the principal, 18: m2, m7, m11, m14, m16, m19, m32, m39, m43, m48, m55, m59, m64, m73, m78, m83, m87, m92 (observed: `messages where to_role='principal'`). The principal record holds 19 calls, because m14 was answered twice (section 6).
- bg_1 on `echo_json`: merged at 5224d1f1. Runs at attempt 2, 34 pass and 1 fail (`tst_echo_json_compact`, `TypeError: echo_json() got an unexpected keyword argument 'file'`). Runs at attempt 3, 35 pass (observed: `test_runs` by batch and attempt). The log also shows a first harness line, "34 test(s), 0 not passing", with no `test_runs` row at attempt 1.
- bg_2 on `confirm_default_on_eof`: `running`, head 95728c57. One stored attempt at d6314349: 33 pass, 2 fail, `inh_022b8a87` (`tests/test_utils/test_confirm.py`) and `inh_51d478df` (`tests/test_termui.py`). No run exists at 95728c57 (observed: `test_runs`, and the `code.commit` refusal in s198 turn 21, "No run is stored at the head 95728c578d").
- The log holds 1 CYCLE line, in walk 1: `liaison|message|converse|[]`.
- **The Stuck line of walk 1** (observed: the log): `Stuck. The team gave up on: contested for defines_commands_and_options. Nothing waits on you, and nothing moves until that is cleared.` The item `defines_commands_and_options` is `approved` (observed: `items`). The tick `vision_keeper|tick:contested|defines_commands_and_options` reads attempts 3, quarantined 1 (observed: `tick_attempts`). So the line is false in the same shape as night 140: it reads the quarantined tick, not the item's state (reasoned, from night 140's read, section 1). The quarantine page never reached the principal: s128 sent the ref `defines_commands_and_and_options` and no message landed (observed: s128 turns 1 to 5).
- **The crash of walk 2, in one line**: after s198 logged two `default` notes whose `about_ref` names an inherited test, `tick_agenda`'s `reaches_request` passed a `None` criterion to `_items_reached`, `ref.partition` raised `AttributeError`, and every `frontier` call after that raised (observed: `.rota/night141.err`, two equal tracebacks; ledger rows `l_a94d65762d` and `l_96c403d182`, `about_table='tests'`). Frame 209 holds the cause.

## 2. Frame 200's doors on bg_1 and bg_2

**The Tester's stored tests** (observed: `tests where criterion_id is not null`).

| Test | Batch | What it does | Runs the behaviour? |
|---|---|---|---|
| `tst_echo_json_compact` v1, `tests/test_utils/test_echo_json.py` | bg_1 | calls `echo_json(obj, file=f)` on an `io.StringIO`, compares `f.getvalue()` with `'{"key":"value","nested":[1,2,3]}\n'` | yes |

- 0 tests apply a decorator to a plain function. 0 tests read an attribute of a factory's return. 0 tests never run the behaviour (observed: the one body above). Nights 138 to 140 met those shapes on the show_python batch, and night 141 never built that batch, so this is no evidence for frame 200's doors (reasoned).
- bg_2 has 0 Tester tests. bg_2's 35 tests are all inherited (observed: `tests where batch_id='bg_2'`). No Tester session ran in walk 2 (observed: `sessions`, Tester s153 and s154 only, both on bg_1). The `tests_failing` tick on the inherited reds fired before any `tests_missing` tick (reasoned: s198 woke at attempt 1, and the night died in the next agenda tick).
- The test passes a `file=` keyword that the criterion does not name. The criterion says "accepts a single positional argument `obj`" (observed: `criteria`, `echo_json_compact`). The Tester logged `invented` about the sample values only (observed: `l_db2560f0a6`). The Developer s155 added `file=None` to fit the test. It tried to log the choice twice, and both writes were refused (kind `assumption`, then the `about_table` pair), so no note records it (observed: s155 turns 2 to 4, no ledger receipt). This is the "Developer fits the test" shape with a harmless outcome (reasoned: `echo` has the same keyword).

**Refusals of `tests.encode`, by kind** (observed: `errs.py`, s153 and s154 turns).

| Session | Turns | Kind | Text, start | What the Tester did next |
|---|---|---|---|---|
| s153 | 2, 3, 4 | parse | `unterminated argument list: a quote inside a quoted argument ended the string early` | sent the same body three times, then the session ended with no test |
| s154 | 2 | file taken | `tests/test_utils/test_echo.py is already inh_5f7b1750's file` | re-sent with `path='tests/test_utils/test_echo_json.py'`, landed |

- 4 refusals, 2 kinds. 1 Tester session of 2 stored a test.

**The Developer's challenges and escalations** (observed: `tool_calls where fn like 'msg.%'`, s198 turns).

- 3 `msg.challenge_tester` calls, all in s198, all with `refs=['cr_1_confirm_default_on_eof', 'inh_022b8a87']`. Each was refused: `inh_022b8a87 has no criterion: it is the project's own test and it passed before this batch. A challenge has no side there. Read code.diff and restore what your change broke`. The third refusal carried the lock note, "refused the same way in three turns and will not be accepted again".
- The quotes carried the criterion's words verbatim and, as the test's line, a whole test body. The first quote was a test body that is not in the file (`test_basic_defaults`, with `stdin=io.StringIO()`). The next two quoted `test_prompts`, the real failing test (observed: turns 1, 9, 10).
- 0 escalations. 0 messages to or from the Developer or the Tester (observed: `messages`). So no challenge was answered with refs and no words. The answer-mode door and the three-ref hint had no case.

**New defect, high: `tests.load` reports a red inherited test as passing** (observed: `rota/roles/api.py:7305-7316` at c18f868c; `test_runs` for `inh_022b8a87`).

- The query takes the latest run per test as `SELECT id FROM test_runs WHERE test_id = t.id ORDER BY attempt DESC, rowid DESC LIMIT 1`. It does not filter on the batch.
- An inherited test keeps its id across batches. `inh_022b8a87` has runs `tr2` (bg_1, attempt 2, pass), `tr37` (bg_1, attempt 3, pass) and `tr72` (bg_2, attempt 1, fail). The query picks `tr37`, a pass from another batch.
- s198's pushed `tests.load` lists all 35 tests as `passing, not shown | pass` (observed: s198 turn 1). The red push in `runner.py:2868-2872` filters on `last_result in ('fail','error')`, so it pushed no red test and no frame 207 sentence (reasoned, from the code and the empty push).
- The seat read this as fact. Turn 7: "all tests are passing (`pass | null`). This suggests that either the tests were not actually failing before my change...". Its notes say "All existing tests pass" (`l_e8be490128`) and "My change to confirm() does not affect its behavior" (`l_a94d65762d`). Both are false at d6314349 (observed: `test_runs`).
- The seat learned the count "33 pass, 2 red" only from the `code.commit` refusal at turn 21, and then named the wrong second test, `inh_c95b73db`, which passed (observed: turn 21, `tr98` pass).
- Night 140 did not meet this, because its red inherited test, `inh_f3b0c3db`, was new at bg_2 and had no older run (reasoned). Every batch after the first meets it on any inherited test that was green in an earlier batch.

## 3. Frame 207 on bg_2

- **Base run** (observed: `config`, `base_run:bg_1` and `base_run:bg_2`): bg_1 34 of 34 pass, bg_2 35 of 35 pass. 0 inherited tests red at the base.
- **The cause of the reds is the Developer's diff, not the harness.** s197 wrote `confirm` over lines 288 to 345 and the write dropped the body after `except`: the `y`/`n` branches, the empty-input default, `break`, and `return rv` (observed: the `[removed lines]` block of `code.diff` in s198 turn 1; s197 `code.write` at seq 11 and 20). The span door admitted the write. This is frame 173's shape, a span write that removes a branch with no note (reasoned, from frame 173's heading).
- **The sentences about inherited tests that s198 read**: one, the challenge refusal, at turns 2, 10 and 11, "it is the project's own test and it passed before this batch ... Read code.diff and restore what your change broke" (observed). The words "passed before this batch" are true for `inh_022b8a87` (observed: `base_run:bg_2`). Turn 1 holds no other sentence about inherited tests, base runs or the project's tests (observed: a search of turn 1's system and user text for "inherit", "before this batch", "base", 0 hits). The push that carries frame 207's sentences did not fire (section 2).

**What s198 did, turn by turn** (observed: `turns.py s198`).

| Turn | Call or text | Result |
|---|---|---|
| 1 | `msg.challenge_tester` on `inh_022b8a87`, quote a test body not in the file | refused, "passed before this batch" |
| 2 | `code.source` termui 290 to 360 | the truncated `confirm` |
| 3, 4 | `code.write` an extra `except` and `while` block, span 320 to 345, then 340 to 340 | first refused (crosses into `get_pager_file`), second landed |
| 5 | `code.commit` | landed, 95728c57. The tree now has a duplicate `except` and a `while True` with no exit (reasoned, from the source at turn 17) |
| 6, 7 | `batches.expect`, then prose: "all tests are passing" | the stale `tests.load` (section 2) |
| 8, 9 | `code.source` on `test_confirm.py`, then a second challenge | refused |
| 10 | third challenge | refused, lock note |
| 11 | `ledger.log` kind `assumption` on `inh_022b8a87` | refused, wrong kind |
| 12 | `ledger.log` kind `default`, `about_table` the file path | refused, the pair |
| 13 | `ledger.log` kind `default`, `about_table='tests'` | landed, `l_a94d65762d`, note 1 |
| 14 | `ledger.log` kind `default` on `inh_c95b73db`, "does not exercise confirm() with EOF, so it is unaffected" | landed, `l_96c403d182`, note 2 |
| 15 | `ledger.log` on `bg_2`, `about_table='batch'`, "All existing tests pass" | landed, `l_e8be490128` |
| 16 to 20 | `code.source`, a refused span write, a whole-function write that restores the truncated version | the write landed |
| 21 | `code.commit` | refused: "you are undoing yourself ... 33 pass, 2 red" |
| 22 | prose of 32,250 characters, cut | no call ran |
| 23 to 24 | `code.source`, `code.commit` again | session ended. The account does not show this last commit as landed |

- The two `default` notes about inherited tests are notes about a test the seat may not edit and could not challenge. By section 8's question 0, a door that works as designed is no note (reasoned: `plans/frame204-design.md`, section 8). These two rows are what crashed the agenda tick (frame 209).
- The seat never restored the removed loop. It saw the removed lines at turn 1 and turn 16 and wrote other code (observed). The refusal told it to "restore what your change broke", and the stale `tests.load` told it that nothing was broken (reasoned).

## 4. Frame 204's kinds at the door

**Fresh ledger rows, by author and kind** (observed: `ledger` group by author, kind, status; 47 rows, the night is cold).

| Author | conflict | default | gap | invented | Total |
|---|---|---|---|---|---|
| Vision Keeper | 34 (14 resolved, 20 open) | 2 | 0 | 1 | 37 |
| Developer | 0 | 4 | 0 | 0 | 4 |
| Liaison | 0 | 0 | 3 | 0 | 3 |
| Terminologist | 0 | 2 | 0 | 0 | 2 |
| Tester | 0 | 0 | 0 | 1 | 1 |

- 12 Vision Keeper sessions at `tick:reconcile` wrote all 34 `conflict` rows, one per prose file under `docs/` (observed: receipts joined to sessions; s30 on `docs/option-decorators.md` wrote 8).
- The reconcile brief asks for `kind="conflict"` "one call per disagreement" and says "Two or three real disagreements beat ten restatements" (observed: s30 system text).

**The 34 `conflict` rows against section 8** (observed: the rows' `default_taken`; the reading is reasoned).

| Shape | Rows (by rowid) | Count |
|---|---|---|
| One source, a restatement: "The README describes X" or "the README says: X", no second source | 1 to 9, 11, 13 to 28, 33 | 27 |
| Two sources that say the same thing: "The README says X. The code shows X" | 12, 34 | 2 |
| Two sources on different subjects: README advice on positional arguments against code behaviour (10); README items against "Briefcase is a tool for packaging Python projects" from `docs/standalone-apps.md` (29 to 32) | 10, 29, 30, 31, 32 | 5 |

- 0 of 34 are a true two-source disagreement. 34 of 34 are what section 8 calls a trace or an echo, "not written", so no cell of the grid fits them. They are not a misplaced kind among the eight. They are notes that should not exist (reasoned: section 8, the row "Owed to nobody in rota", "trace and echo are not written").
- The door refused 3 rows whose two halves were the same sentence, in s9, s17 and s26 ("the two halves of this assumption say the same words"). It admitted rows 12 and 34, whose halves differ in a few words, and every one-source row (observed: `errs.py`).
- These rows reach the principal. Page m32 lines 6 to 11 and page m48 lines 6 to 12 are `conflict` rows under "Where you did not say, I assumed", and the principal spent words on m32, m39 and m48 to drop them (observed: the principal record).

**The `faults` table**: 0 rows (observed: `select * from faults`).

**Refusals of `ledger.log`** (observed: `errs.py`, 15 distinct refusals).

| Cause | Sessions | Count |
|---|---|---|
| wrong kind: `in_scope` | s109, s166 (Vision Keeper) | 2 |
| wrong kind: `assumption` | s155, s198 (Developer) | 2 |
| wrong kind: `none` | s23 (Vision Keeper, reconcile) | 1 |
| missing kind | none | 0 |
| `about_ref` and `about_table` name no row together | s139, s155, s181, s198 | 4 |
| two halves the same sentence | s9, s17, s26 | 3 |
| the principal already ruled on the row | s151 | 1 |
| asked three times | s166, s181 | 2 |

- After the wrong-kind refusal: s109 and s166 sent `invented` and `default` and landed. s198 sent `default` and landed after one more refusal. s155 sent `scope`, met the pair refusal and never logged. s23 wrote prose and the session ended (observed: the next turns).
- The door admitted two rows whose pair is not one row: `l_6ba7fe72ef`, `about_table='cr_1_confirm_default_on_eof'` with `about_ref='src/click/termui.py::confirm'`, and `l_e8be490128`, `about_table='batch'` (observed: `ledger`). The pair check fires when `about_ref` is a known row id, and not otherwise (reasoned, from the refusal texts).

## 5. The dangling pointers

(observed: `nightcount.py` definition at c18f868c, the eviction notice "re-read anything you still need" and a tail "unchanged since you asked" or "was run for you before you"; `dang.py`, `dang2.py`)

| Session | Role, wake | Turns | Distinct calls refused after the notice | Answer still in the prompt? |
|---|---|---|---|---|
| s155 | Developer, `tests_failing` bg_1 | 9 | `code.source`, `batches.expect`, `code.write`, `code.commit`, `tests.load` | yes, for all 5 |
| s198 | Developer, `tests_failing` bg_2 | 9 | `code.source`, `batches.expect`, `code.diff` | yes, for all 3 (`batches.expect` in the preloaded block) |
| s152 | Developer, `batch_start` bg_1 | 7 | `model.load`, `code.source` | `model.load` no; `code.source` yes |
| s33 | Vision Keeper, reconcile | 4 | `code.source` | yes |
| s197 | Developer, `batch_start` bg_2 | 3 | `code.source` | yes |
| s163 | Architect, survey | 2 | `model.describe` | no |

- 34 turns, 6 sessions, as the log says. 12 distinct refusals after a notice. 2 point at an answer the window dropped: s152 turn 7, `model.load`, and s163 turn 5, `model.describe`. Each says "What ... returned then still stands" with no answer in the prompt.
- "Yes" for `code.source` means a `code.source` result stands after the notice. It is not proved to be the same span (reasoned: the check matches the function name only).
- **Frame 208's shape repeats.** Three refusals say "asked three times ... The answer is in this prompt." after an eviction notice. s150, `batches.annotate`, is true: `OK batches.annotate -> {"batch_id": "bg_1", "grains": 3}` stands after the notice. s18 turn 6 and s33 turn 11, `code.probe`, are false: no `OK code.probe -> []` remains, and the only `[]` sits inside an unrelated table row, `... command-line | [] | 1` (observed: s18 turn 6 and s33 turn 11, 4 hits of `[]` each, the first in that row). So 2 of 3 are false, the shape frame 208 names. s18 is not in the nightcount line, because its tail is the `ERROR` form.

## 6. The agent principal

(observed: the principal record, `kind='call'` and `kind='land'` rows of night 141)

| # | Ask | Phase | Page | Answer, short | Read right? |
|---|---|---|---|---|---|
| 1 | m2 present | onboarding | first sign-off page | "Ok, that matches how I see Click today." | yes |
| 2 | m7 clarify | onboarding | `command` against `command#src_click` | the same thing, merge | yes |
| 3 | m11 clarify | onboarding | `parameter` against `parameter#src_click` | keep the base class, drop the ParameterSource entry | yes |
| 4 | m14 present | onboarding | 39-line sign-off page | line 17 wrong, what is line 39 | yes |
| 5 | m16 converse | onboarding | "What does line 39 refer to?", 27 characters | "the page I got stopped partway through line 10 and I never saw line 39's text", drop it if it is a file-change tool | **no**, see below |
| 6 | m14 present | sentence 1 | the same onboarding page, still open | line 1 never mentions echo_json, states the request | the page was stale, the request landed |
| 7 | m19 confirm | sentence 1 | "Did I hear you right?" | ok, standard library json only | yes |
| 8 | m32 present | sentence 1 | request page, lines 6 to 11 are `conflict` notes | lines 11 and 12 the same tab-completion note | yes |
| 9 | m39 clarify | sentence 1 | Liaison's question about overlap | nothing built yet, drop both copies | yes |
| 10 | m43 present | sentence 1 | short request page | ok, build it | yes |
| 11 | m48 present | sentence 1 | request page, lines 6 to 12 notes | drop line 10, lines 11 and 12 repeat 7 and 9 | yes, the pairs match |
| 12 | m55 clarify | sentence 1 | "this area has not been surveyed" question | not sure, takes the simple reading | yes, the question is unclear |
| 13 | m59 present | sentence 1 | "Before I build this", line 3 names pager tests | pager not touched, tests beside echo's | yes |
| 14 | m64 confirm | sentence 2 | "Did I hear you right?" | ok, flag off by default | yes |
| 15 | m73 present | sentence 2 | request page | line 2 leaves out the default | yes |
| 16 | m78 clarify | sentence 2 | keep the flag off by default? | yes | yes |
| 17 | m83 clarify | sentence 2 | return the default or abort? | only with the flag on | yes |
| 18 | m87 present | sentence 2 | request page, lines 5 to 10 glossary notes | lines 1 to 4 right, drop 5 to 10 | yes |
| 19 | m92 present | sentence 2 | "Before I build this", line 5 lists `test_defaults.py` tests | not related, tests go in the termui test file | yes |

- **m16 is the one misread.** The m16 page is the Liaison's 27-character question. The m14 page, 3,331 characters, holds all 39 lines, and the principal had named line 39 from it (observed: page lengths, the m14 page tail). No page of the night was cut at line 10. The answer still told the team what to do, drop the line. The Liaison s100 then met `rulings.rule` refusals and ruled nothing (section 7).
- **m14 in sentence 1** answered the onboarding sign-off page, which stood open after `ONBOARDED`, with the new request's words. The Liaison turned the words into s1 and asked m19, so the request was not lost (observed: `land m14 reply m18`, then m19). The page was the harness's choice, not the principal's misread (reasoned).
- Two answers name a seat's fault: m32 and m48 drop restated `conflict` notes, and m59 and m92 correct a predicted touch set (observed).

## 7. Residue: sessions with zero receipts

(observed: `res.py`; a message counts as sent when a `messages` row has the session's role and its trigger as cause, or the tick message that follows the session)

- 49 of 198 sessions hold zero receipts.
- 34 sent a message, which writes no receipt by design: Liaison 25, Vision Keeper 5, Architect 2, Terminologist 2 (s69, s74 at `term_collision`). These are not residue (reasoned: a message has no receipt row).
- 15 did no admitted work, in 5 shapes.

**Shape A. A ref that names no row of the table the call writes, 6.**

| Session | Role, wake | Cause |
|---|---|---|
| s1 | Liaison, `tick:quarantined` (constraint_zero) | sent `refs=["tick:quarantined"]` four times, the words of the tick, not an id |
| s128 | Liaison, `tick:quarantined` (contested) | sent `defines_commands_and_and_options`, a typo. The corrected call at turn 4 landed no message |
| s121 | Vision Keeper, relay m37 | `problem.set_approval` on `e_m34`, a message id, not an item |
| s137 | Vision Keeper, relay m52 | `problem.set_approval` on three ledger ids |
| s136 | Architect, relay m51 | `model.adopt` on doc paths, not `model_areas` rows |
| s185 | Architect, relay m85 | `model.adopt` on `bg_2` |

**Shape B. A relay of a ruling with nothing to adopt, 5.**

| Session | Role, wake | Cause |
|---|---|---|
| s77 | Terminologist, relay m13 | the principal contested both senses. "Nothing is owed". Runner: "named an act and did not perform it" |
| s191 | Terminologist, relay m91 | the principal contested all five senses, no call |
| s145 | Architect, relay m58 | `model.adopt` returned `{"adopted": [], "skipped": ["k0"]}` |
| s190 | Architect, relay m90 | `model.adopt`, then "Nothing is owed" |
| s143 | Architect, relay m56 | `model.adopt` refused, "adopt needs a landed ruling on the chain" |

**Shape C. An ask the principal had already answered, 2.**

| Session | Role, wake | Cause |
|---|---|---|
| s100 | Liaison, converse m17 | `rulings.rule(ask=...)` refused, "you asked this in m16, and the principal answered it in m17". The next three `rulings.rule` calls with lines 17 and 39 were refused for the lines left unruled |
| s127 | Liaison, report m42 | `msg.clarify_principal` refused, "answered it in m40". `ledger.unaddressed` on `e_m34` refused. Four relays with a prose argument, none landed |

**Shape D. An answer before any commit, 1.**

| Session | Role, wake | Cause |
|---|---|---|
| s151 | Terminologist, relay m63 | `msg.answer_tester` refused, "no change built from this criterion has a commit yet". `criteria.respecify` refused on a test path as a surface |

**Shape E. A call that does not parse, 1.**

| Session | Role, wake | Cause |
|---|---|---|
| s153 | Tester, `tests_missing` bg_1 | three `tests.encode` calls, each "unterminated argument list" |

- The Developer sessions are not residue: s152, s155, s197 and s198 each hold at least one receipt (observed: `receipts`). Their failure is in section 2 and section 3, not in this count.
