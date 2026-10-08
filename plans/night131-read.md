# Night 131 read

Night 131 ran warm from `C:/Users/roman/rota_night131` at 51678e1f, 2026-10-08 03:53 to 06:37. The tree joins frame 178 on top of frames 170 and 177. The database starts from the snapshot of 9d6ad60c, so s1 to s110 are night 129's onboarding. The night's own sessions are s111 to s343, 233 sessions and 1,272 turns, in three walks. Rota workflow throughout, except section 5, which runs the meta workflow's checker. Database `.rota/clickI_night131.db`, log `.rota/night131.log`. `.rota/night131.err` is 0 bytes. Scripts: the scratchpad folder `n131` of session 18588d6d, copied from `n130` with `DB` and the tree pointed at night 131. They read the database with `mode=ro&immutable=1` (observed: the scripts, 2026-10-08).

Verdicts, one line each:

- Frame 178, the refusals: 5 `findings.find` refusals in 2 sessions, not 8. The 8 turns of the brief are prompts that carry the 5 refusals again. 1 of the 5 is a frame 178 check: s137 t2, a `satisfied` grain off the diff. Section 1.
- Frame 178, ratio one: 0 of 2 finding rows on the night's merges name a file the diff does not touch, `f1` on bg_1 and `f123` on bg_3. The baseline is 7 of 18 on nights 114 to 128. The line is at most 1 in 6. Met, and the door made 1 of the 0: s137's `f2` on `tests/test_utils/test_echo.py` was refused.
- Frame 178, ratio two: 0 of 2 rows lost to an id reuse. The baseline is 2 of 2. Met by the seat's choice, not by the door. s195 chose `f123` at t1 and s288 chose `fnd_escalation` at t5, each with no refusal before it. The id check refused 0 calls.
- Frame 178, ratio three: the next call after a frame 178 refusal landed in 1 of 1, s137 t3. Across all 5 `findings.find` refusals, the next call landed in 2 of 5. The line is at least 2 in 3. Met on a sample of 1. The misses are s288 t6 to t8, after the `k0` violated refusal offered constraints that do not exist.
- Frame 178, the residue: no Architect session ended with no finding after a refusal. s288 landed `fnd_escalation` at t9.
- Frame 178, `k0` beside a bound constraint: 0 admitted, and the check met no case. Only `k0` reaches `src/click/utils.py`, `src/click/termui.py` and `src/click/decorators.py`. That is frame 179.
- Frame 170, Critic sessions that land a verdict: 2 of 2, s136 on bg_1 and s194 on bg_3, each at t1 with lines. Night 130 had 1 of 1, night 129 1 of 1.
- Frame 170, the named lines: 5 of 6 touch the criterion's words, with 2 weak hits counted. Strict, 3 of 6. Night 130 had 2 of 3, night 129 2 of 3. The line is at least 3 in 4. Met with the weak hits, not met without them.
- Frame 170, the kinds: 1 named line is an import, `    import json` on bg_1 again. 0 comments, 0 docstring lines, 0 blanks, 0 `def` headers. s194 named one 2-line block for all 3 criteria.
- Frame 181's sign: s194 sent `verdicts.emit` 2 more times after its verdict landed. s136 sent none.
- Frame 183: 7 `tick:term_collision` sessions on `usage`, not 6. s254 is the seventh. All 7 ran one prompt hash, and every turn of all 7 has the same md5. The collision never closed by `glossary.same`. Section 3.
- Frame 183, what stopped the cycle: s255's clarify landed without the backticks round `get_usage`. s256 then ruled `usage` and `usage#src_click` by their own ids, and the predicate counts a ruling only by those ids.
- The merges: bg_1 and bg_3 are whole and run on their own paths. bg_3 merged with no test of its own: its criteria count bg_2's abandoned tests, and 2 of those 3 fail on bg_3's head. Section 4.
- bg_2 was abandoned because the Vision Keeper's s180 rewrote the item's words with `problem.assert` after challenge m82. The item went back through sign-off and grouping, and became bg_3.
- bg_4, stuck on 4 red: 3 Tester tests decorate a local `def` with a bare `@version_option(show_python=True)` and pass it to `.invoke`. That is frame 176's shape, not a factory misuse. The 4th is the project test `inh_dcc9ea38`. The head does not hold the behaviour. bg_4's first commit b740401 did.
- Invariants: 113 rows in 2 of 10 invariants, I4 108, I9 5. Night 130 had 77: I2 1, I4 71, I9 5.
- Crashes: 0. 233 of 233 night sessions are committed. `CYCLE` lines: 1, at walk 3.

## 1. Frame 178, the finding door

**Ten `findings.find` calls on the night. Five were refused, and only one of them by a frame 178 check.** (observed: `m178.py`, `m178.out`, `tool_calls`, 2026-10-08)

| Session | Turn | The call | Result | Check |
|---|---|---|---|---|
| s137, `tick:structural_review` bg_1 | t1 | `f1`, `k0`, satisfied, `src/click/utils.py` | landed | |
| s137 | t2 | `f2`, `k0`, satisfied, `tests/test_utils/test_echo.py` | refused | frame 178, satisfied grain off the diff |
| s137 | t3 | `f2`, `k0`, satisfied, `src/click/utils.py` | `OK`, `already filed, as f1; nothing was written` | |
| s195, `tick:structural_review` bg_3 | t1 | `f123`, `k0`, satisfied, `src/click/termui.py` | landed | |
| s195 | t3 | `f124`, the same constraint and grain | `OK`, `already filed, as f123` | |
| s288, `message` escalate m162, bg_4 | t5 | `fnd_escalation`, `ver_opt_show_py`, violated, `tst_ver_opt_show_py_1` | refused | a criterion id as the constraint, night 95's check |
| s288 | t6 | `fnd_escalation`, `k0`, violated, `src/click/decorators.py` | refused | `k0` cannot be violated, tipsAN's check |
| s288 | t7 | `fnd_escalation`, `version_option`, violated | refused | the constraint does not bind the file, frame 90's check |
| s288 | t8 | `fnd_escalation`, `custom_version_option`, violated | refused | the same |
| s288 | t9 | `fnd_escalation`, `k0`, satisfied, `src/click/decorators.py` | landed | |

- s137 t2's refusal, verbatim: `the batch's diff does not touch 'tests/test_utils/test_echo.py'; it changed ['src/click/utils.py']. A finding names a file the diff changed, and a file the batch was expected to touch is not one. Send the finding again with one of ['src/click/utils.py'] as the grain`. The seat sent the offered grain at t3.
- s288 t6's refusal ends `Record it satisfied, or check the constraints that bind 'src/click/decorators.py'`. No constraint other than `k0` binds that file. The seat then sent `version_option` and `custom_version_option`, two ids from its own `model.load` at t3. The next refusals said `No constraint binds this diff. File 'k0' satisfied`, and t9 sent that call (reasoned: `_bound_exit` and the `k0` sentence in `rota/roles/api.py` at 51678e1f).
- s288 is an escalation session. It wanted to file the red test as a violation. After t9 it challenged the Vision Keeper, m163.
- No seat sent an id that another batch held. s195's prompt at t1 holds no finding id, and s195 sent `f123` before any read. So the id check met no case (observed: the prompt of s195 t1, 0 hits for `f1`).
- `k0` beside a bound constraint: `_reaching_constraints` on the night's database gives `['k0']` alone for each of the three changed files and for `src/click` (observed: a call of the tree's function, 2026-10-08).

**The rows** (observed: the `findings` table and `git show --stat` on clickI):

| Row | Batch | Grain | The diff's files | On the diff |
|---|---|---|---|---|
| `f1` | bg_1, merged | `src/click/utils.py` | `src/click/utils.py` | yes |
| `f123` | bg_3, merged | `src/click/termui.py` | `src/click/termui.py` | yes |
| `fnd_escalation` | bg_4, running | `src/click/decorators.py` | `src/click/decorators.py` | yes |

- All three rows are `k0`, `satisfied`. Every row on every batch stood at the end. No row was replaced.

## 2. Frame 170, the named lines

**Both Critic reviews landed a pass with lines at turn 1.** (observed: `acts.py` on s136 and s194, the `verdicts` table, 2026-10-08)

| Session | Batch | Landed | Turn | Lines refusals | Verdicts sent after |
|---|---|---|---|---|---|
| s136 | bg_1 | 1 | t1 | 0 | 0 |
| s194 | bg_3 | 1 | t1 | 0 | 2, t2 and t3, each refused by the duplicate door |

- s136 has prompt hash 934372d520741890, not night 130's aacbec95547689e4. Both nights have briefs hash 47f78c38b1cf2ee0. So this is a second sample, not a replay.
- No Critic answer session ran. The other 14 Critic sessions are `tick:challenge` sessions on constraints and one item.

**Each line beside its criterion** (reasoned: a read by hand of `verdicts.lines` beside `criteria.text`):

| Criterion | The criterion's words | The line | Touches |
|---|---|---|---|
| `echo_json_compact` | `json.dumps(obj, separators=(",", ":"))`, followed by a single newline | `out = json.dumps(obj, separators=(",", ":"))` | yes |
| `echo_json_compact_2` | must not emit any ANSI color codes | `file = _default_text_stdout()` | yes, weak: the raw stream takes no style, and the criterion is a negative |
| `echo_json_compact_3` | raising a `TypeError` ... of standard library JSON serialization | `import json` | no, an import |
| `cr_1_confirm_eof_default` | with `default_on_eof=True` and stdin closed, it returns the provided default | `if default_on_eof and isinstance(sys.exc_info()[1], EOFError):` / `return default` | yes |
| `cr_2_confirm_eof_default_false` | with `default_on_eof=False` or omitted, it must abort | the same 2 lines | yes, weak: the condition keeps the old `raise Abort()`, which is not an added line |
| `cr_3_confirm_eof_default_value` | the default returned must be the exact object passed | the same 2 lines | yes |

- 5 of 6 with the weak hits, 3 of 6 strict. Night 130 counted a weak hit as a hit, so the comparable count is 5 of 6 against 2 of 3.
- The `import json` miss is the same line for the same criterion as on nights 129 and 130. Frame 180's door is not on this tree.
- No named line is a comment, a docstring line, a blank or a `def` header. bg_1's diff holds a 5-line docstring, and the seat named none of it.

## 3. Frame 183, the term-collision cycle

**Seven Terminologist sessions on `usage` ran the same five turns. The cycle stopped when a ruling named the two senses by their ids.** (observed: md5 of every turn, `acts.py`, the `rulings`, `ledger` and `glossary_terms` tables, 2026-10-08)

The seven sessions: s204, s234, s238, s242, s246, s250, s254. Prompt hash 8c31b0ddb020e6bf. Each turn's prompt and completion have one md5 across all seven.

| Turn | The call | Result |
|---|---|---|
| t1 | `code.probe(pattern='get_usage')` and 3 `code.source` reads | `OK`. The probe returns `[]` |
| t2 | `glossary.synthesise` on `usage` and `usage#src_click` | refused: `that is 'usage' again, word for word` |
| t3 | `glossary.same(keep='usage', drop='usage#src_click', why='... they differ only in phrasing, not meaning.')` | refused: `is a reason they are *not* the same -- it says 'differ'` |
| t4 | `msg.report_liaison(refs=['usage', 'usage#src_click'])` | landed: m100, m116, m120, m124, m128, m132, m136 |
| t5 | none | the session ends |

**One round of the cycle** (observed: sessions s205 to s256, messages m100 to m139):

1. The Terminologist reports the collision to the Liaison.
2. The Liaison's report session sends `msg.clarify_principal` with `` `get_usage` `` in backticks. The door refuses: `'get_usage' names no row, so this question is about your own bookkeeping`. 6 refusals, s205, s235, s239, s243, s247 and s251, each at t1.
3. The same session sends `ledger.unaddressed` on `usage` and on `usage#src_click`. The rows are `l_2d7ad07a8f` and `l_5dc80a84e3`.
4. The agenda tick presents the 2 rows, and the principal approves them by their ledger ids. The rows are resolved.
5. The predicate fires again, and a new Terminologist session wakes.

- The two ledger rows end at version 6 each, `resolved`. Six report sessions wrote them, one version each.
- Why the predicate fired again: `term_collision` counts a sense as ruled only when a ruling's `per_item` names its glossary id. The rulings r_48ba02bda0 to r_f2283cf860 name `l_2d7ad07a8f` and `l_5dc80a84e3`. When a ledger row is resolved, it no longer counts as raised (reasoned: `term_collision` in `rota/core/predicates.py` at 51678e1f).
- What stopped it: s255 wrote `get_usage` without backticks, and the clarify landed, m137. The principal answered m138, `the Python version comes from sys.version_info as major.minor.micro`, the answer to bg_4's question. s256 ruled `{"usage": "approve", "usage#src_click": "approve"}` on those words, r_87061c1934. No collision wake came after s254.
- s257, the Terminologist on the relay, adopted `usage#src_click`. Both senses are still live at the end, `superseded_by` empty, and their meanings were never joined. So the collision was ruled, not closed.
- The words that ruled it are not about the word `usage`. The principal's answers come from the meta workflow's script (reasoned: the same answer stands on m141 and m174 in the log).

**The other collision sessions of the night**, each closed by a landed `glossary.synthesise` (observed: `superseded_by` on the `#src_click` rows):

| Session | Term | Refusals | Closed |
|---|---|---|---|
| s200 | `command` | 1 at t1, `a summary of them` | yes, at t3 |
| s201 | `line` | 0 | yes, at t1 |
| s202 | `decorator` | 0 | yes, at t3 |
| s203 | `stream` | the result of t3 was not read | yes, by t4 |

## 4. The merges and the stuck batch

**bg_1, `echo_json`.** Commits 8af8995 and 3bc3336 by s130, merged as 1f0f338 with the tests in 6cc6a87 (observed: `git diff 2c8cd3a 3bc3336`, `git show 1f0f338`):

- The function writes `json.dumps(obj, separators=(",", ":"))` and a newline to `_default_text_stdout()`, the same body as night 130. The change is whole.
- The 3 tests call `echo_json` directly. `_1` swaps `sys.stdout` for a `StringIO` and asserts `'{"a":1}\n'`. `_2` asserts no `\x1b` in the output. `_3` asserts a `TypeError` on a lambda.
- On a copy of 1f0f338, the 3 tests pass. With `separators` removed, `_1` fails, and `_2` and `_3` pass. So 3 of 3 take the added path, and 1 of 3 fails without the change. Night 130 had 2 of 3 (observed: the probe in `n131/merged1`, 2026-10-08).
- The def follows `raise AttributeError(name)` with no blank line, as on nights 128 and 130.
- s131 met the kind clause twice at t1, frame 177, and stored the tests by t6.

**bg_3, `confirm_with_default_on_eof`.** Commit 6417641 by s193, merged as 8f8f697. No commit of bg_3's tests exists (observed: `git show 8f8f697`, `test_runs`):

- The change adds `default_on_eof: bool = False`, two docstring entries, and `if default_on_eof and isinstance(sys.exc_info()[1], EOFError): return default` in the `except` branch. `termui.py` imports `sys` at line 9. The change is whole.
- On a copy of 8f8f697, `--eof 1` with empty input returns the default. `--eof 0` and no flag abort. A `confirm` with an `object()` as the default returns that object. The full suite: 1,916 passed (observed: `probe_bg3.py`, 2026-10-08).
- bg_3 has no row in `tests`. Its one harness run was 37 project tests at attempt 1.
- Why no Tester woke: `tests_missing` and the merge gate each ask whether a criterion has a test in any batch, not in this batch. bg_2's three tests hold bg_3's three criteria (reasoned: `rota/core/predicates.py` near line 700 and `rota/core/lifecycle.py` line 454, at 51678e1f).
- The Critic s194 saw `tested_by` with bg_2's ids in `criteria.load`, sent `claim_encodes` true on all three, and passed.
- bg_2's 3 tests on a copy of 8f8f697: 1 passes and 2 fail. `_value` passes the default as the flag. `_false` expects `EOFError` where the code raises `Abort` (observed: the probe in `n131/merged3`). So the code is right, and the tests the gate counted are wrong.

**bg_2, why abandoned** (observed: `acts.py` on s178 to s186, messages m75 to m92, the log):

- bg_2's last head c73ea3c by s166 had 2 red: `tst_confirm_eof_default_false` and `tst_confirm_eof_default_value`, the same 2 tests as above.
- s178 escalated, m81. The Architect s179 challenged the Vision Keeper, m82.
- The Vision Keeper s180 authored `d_900de7490d` and sent `problem.assert` on `confirm_with_default_on_eof` with new words. The item changed, and the log reads `do:cancel: abandoned bg_2: its item is no longer schedulable`.
- The item went through sign-off s181, the present m84, the clarify m89 and grouping s186, and became bg_3. A decision and then an asserted item is frame 129's shape. s180 also wrote its own tool results at t5 to t8.

**bg_4, `version_option_show_python`, stuck on 4 red at 25008e09** (observed: `test_runs` tr380 to tr388, `put_tests.py`, the probe in `n131/bg4head`, `probe_vo.py`):

| Test | What it asserts | The red reason at 25008e09 |
|---|---|---|
| `inh_dcc9ea38`, `tests/test_basic.py` | 3 cases of the project's `package_name` and import-name lookup | `TypeError: version_option() got an unexpected keyword argument 'package_name'` |
| `tst_ver_opt_show_py_1`, 2 functions | `'--show-python' in` the `--help` output, and `'Python'` in the output of `--show-python` | `TypeError: Command.__init__() missing 1 required positional argument: 'name'` |
| `tst_ver_opt_show_py_2` | `'Python'` in the output of `--show-python` | the same |
| `tst_ver_opt_show_py_3` | `exit_code != 0` or `mutually exclusive` on `--show-python --version` | the same |

- Each `tst_` function decorates a local `def cmd(ctx, param=None)` with a bare `@version_option(show_python=True)`, with no `@command()`, and passes `cmd` to `runner.invoke`. That is frame 176's shape. No test reads a factory's bare return or the stdout of a bare call, so none is a frame 177 misuse.
- The tests ask for a `--show-python` flag on the command. The criterion asks for `the show_python option` via the decorator. The tests cannot pass on a factory that keeps its shape.
- The head does not hold the behaviour. s341 in answer mode, m200, replaced `version_option` whole with `def version_option(show_python=False)` at c5d386b and 25008e09. The `--version` option, the version lookup and `package_name` are gone. On a copy, `@version_option("1.0", show_python=True)` raises `TypeError`.
- bg_4's first commit b740401 by s272 held the behaviour. On a copy, `--version` prints `cli, version 1.0 (Python 3.14.2)`. Its run was 37 of 37 green, before any Tester test.
- d79c0ef by s287 removed the `packages_distributions` fallback, and `inh_dcc9ea38` went red there. It stayed red to the end.
- 8 commits by 7 Developer sessions. s331 and s341 committed in answer mode, frame 171.
- No Critic woke on bg_4. bg_4 reached attempt 10 of 10 at s333.

## 5. The invariants

`python -m rota.tools.invariants D:/repos/rota/.rota/clickI_night131.db --all`, run from `C:/Users/roman/rota_night131`, exit 1, `113 finding(s)` (observed: `inv.out`, 2026-10-08):

| Invariant | Night 131 | Night 130 | What the rows are |
|---|---|---|---|
| I1 | 0 | 0 | |
| I2 | 0 | 1 | |
| I3 | 0 | 0 | 0 on bg_3 because bg_3 has no test of its own |
| I4 | 108 | 71 | 34 runs of bg_1, 37 of bg_2 and 37 of bg_3 name project tests that now name bg_4. Frame 130's shape |
| I5 to I8 | 0 | 0 | |
| I9 | 5 | 5 | m65, m77, m82, m163, m172, each an Architect to Vision Keeper challenge. Frame 174 |
| I10 | 0 | 0 | |

- I4 grows by one batch's runs because one more batch ran before bg_4 (reasoned: the rows by batch).
- I3 holds by the empty set. No invariant reads a merged batch with no test of its own (reasoned: the I3 text).

## 6. The night as a whole

(observed: the log, `phases.py`, `test_runs`, 2026-10-08)

| Phase | Clock | Sessions | Turns | Steps and asks | End |
|---|---|---|---|---|---|
| onboarding | skipped, the snapshot of 9d6ad60c | s1 to s110 | 320 | | `warm start ... (onboarding skipped)` |
| walk 1, `echo_json` | 03:53 to 04:12 | s111 to s137 | 124 | 35 steps, 4 asks | `MERGED (1 total)` |
| walk 2, `confirm_with_default_on_eof` | 04:12 to 04:48 | s138 to s195 | 279 | 71 steps, 6 asks | bg_2 abandoned, bg_3 `MERGED (2 total)` |
| walk 3, `version_option_show_python` | 04:48 to 06:37 | s196 to s343 | 869 | 180 steps, 21 asks | `Stuck: ... 4 tests are still failing` |

- Commits landed: 12. bg_1 2, bg_2 1, bg_3 1, bg_4 8.
- End state: bg_1 `merged` at 3bc33360. bg_2 `abandoned` at c73ea3c3. bg_3 `merged` at 64176418. bg_4 `running` at 25008e09, attempt 11, 4 red.
- The `CYCLE` line at 05:05 names the four wakes of section 3. The night ran 1 hour 32 minutes after it.

## 7. The night counter

The counter at the end of the log, verbatim: `made up: 109 turns, 49 sessions (architect 8, critic 5, developer 18, terminologist 1, tester 5, vision_keeper 12)`, `ran anyway: 0 writes after an invention (0 turns with a write result), 0 with a landed commit, shas none`, `dangling pointers: 104 turns, 20 sessions ... Most such turns: s304 (14), s334 (14), s130 (11)`, `repeats: 11 wakes repeated, 39 sessions, 28 of them repeats`. Night 130: 72 turns in 38 sessions, 1 landed commit, 87 dangling-pointer turns in 16 sessions, 7 repeated wakes in 15 sessions (copied: `plans/night130-read.md`, section 5). The counter reads the whole database, so s1 to s110 are in it (reasoned: the warm start copies them).

- The 7 Terminologist sessions and their Liaison rounds are part of the repeats. The repeat groups were not read one by one.

## 8. Walls on this night

New walls (reasoned: the headings of `plans/stack.md`, read by grep for `^### `, 2026-10-08):

1. **A batch merges with no test of its own, because a criterion counts another batch's tests.** 1 merge, bg_3. `tests_missing` never woke, and the gate passed. 2 of the 3 counted tests fail on bg_3's head. Section 4. The nearest frame is 182.
2. **A ruling by ledger id never rules the glossary senses, so `term_collision` fires again after each round.** 6 rounds, 7 sessions. Section 3. The nearest frame is 183. Frame 183 names the `glossary.same` door. This is a second cause in the predicate.
3. **The Liaison's clarify is refused for a backticked identifier that names no row.** 6 refusals, s205 to s251, each followed by two `ledger.unaddressed` calls. The seventh clarify, without backticks, landed. Section 3. The nearest frame is 183.
4. **The `k0` violated refusal says to check the constraints that bind a file when none binds it.** 1 session, s288, 2 refusals after it on invented constraint ids. Section 1. The nearest frame is 178.
5. **The principal's script answers a glossary question with another item's answer, and the ruling approves both senses.** 1, m138. Meta workflow. The nearest frame is 42.
6. **A batch's first commit holds the behaviour, and later commits remove it to meet tests of a wrong shape.** 1 batch, bg_4, from b740401 to 25008e09. Section 4. The nearest frames are 176 and 171.

Known walls with a case on this night (observed: `walls.py`, `walls.out`, `bg4_tests.out`, and the sections above). Counts from `walls.out` cover s1 to s343, so they include night 129's onboarding:

| Frame | Cases | Evidence |
|---|---|---|
| 176, a local def under a bare decorator to `.invoke` | 3 stored tests, 4 functions | bg_4's last versions, section 4 |
| 177, the kind clause | 2 refusals | s131 t1. The factory door refused 0 |
| 179, `k0` in every structural review | 3 rows | `f1`, `f123`, `fnd_escalation` |
| 181, a verdict sent again after it landed | 2 refusals | s194 t2 and t3 |
| 171, answer mode writes the product | 3 commits | s331 7ed4c1d, s341 c5d386b and 25008e0 |
| 129, a Vision Keeper asserts a new item while it answers a challenge | 1 | s180, the cause of bg_2's abandonment |
| 174, an answered row with no answer | 5 I9 rows | m65, m77, m82, m163, m172 |
| 130, a project test and the batch's runs | 108 I4 rows | section 5 |
| 167, a batch id at the approve step | 3 refusals | s337 t1 to t3 |
| 169, `The answer is in this prompt` | 118 refusals carry the sentence | how many stood after an eviction was not read |
| 148, `the tests are the Tester's` | 11 refusals | in s130, s168, s193, s283, s292, s295, s302 and s341 |
| 166, the not-Python door | 8 refusals | s299 t12 and t13 |
| 147, the constant-assertion door | 2 refusals | s131 t1 and t4 |
| span crosses blocks | 10 refusals | s166, s290, s297, s303, s304, s341 |
| reply cuts | 8 `ERROR reply cut` lines | s24, s32, s70, s147, s163, s190, s206, s329. Night 130 had 12 |
| made-up results | 85 refusals of a reply with its own results | the sessions were not read |

Known walls with 0 cases: frame 131's invoke door, 0. Frame 170's lines door, 0. Frame 140's `dropped` note, 0. Frame 159's end choice, 0.

## 9. What this read did not read

- The turns of s1 to s110, night 129's onboarding.
- The bg_4 Developer and Tester chain, s272 to s341, turn by turn. Section 4 reads its stored tests, its commits and its runs. The refusals on its encodes were counted from `bg4_tests.out` only: 18 on the surface import, 15 on `collect nothing`, 12 on an assumed value, 8 on not-Python.
- s203 t3's result, and s200 to s203 beyond their end rows.
- The made-up turns, the dangling pointers and the repeat groups of the counter.
- The 118 `in this prompt` sentences against the eviction notices.
- No model call was made. The code run beyond the parser and the checker: pytest and two probes on scratchpad copies of 1f0f338, 8f8f697, 25008e09, b740401, d79c0ef and 7ed4c1d, and one call of `_reaching_constraints` on the read-only database.

Status 2026-10-08 06:46: written by an agent of session 18588d6d from the final database. Not committed. Rota workflow, except section 5.
