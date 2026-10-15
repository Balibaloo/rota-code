# Night 149, cycle 1: the read during the night

Rota workflow, read by the meta workflow. Source: a read-only `.backup()` of
`.rota/clickI.db` taken at 15:39:24, `scratchpad/n149/c1.db`, and
`.rota/night149.log`. Walk 3 started at 15:38, so walk 3 rows after 15:39
are not in this read. Every fact below is (observed: the table named,
2026-10-15 15:4x) unless it carries another mark.

## 0. The answer in short

- The cycle belongs to a new wall. It is not frame 239's and not frame 182's.
- Cause 8, "A door's predicate is not its fact". The stdin-capture door of
  `tests.encode` (`rota/roles/api.py` about lines 7041 to 7100) refused the
  one right body of the cycle. That body ran `confirm()` inside a local
  `@click.command()` through `CliRunner().invoke(..., input="")`. This is
  the recipe the principal gave at m86 and m92.
- Fix kind by section 4: step 4, "wrong to fire", cause 8, cheap fix: a
  door predicate change with its count, 2 to 3 cycles.
- Frame 243: the contest block reached every Developer and Tester wake after
  each landed contest. The respecified texts still say "UsageError" and
  never "aborts". The supersede door fired 0 times. The longest block is
  7495 characters.
- The cycle is a loop on another wall. Walk 2's pages are data for frame
  243, but the cycle adds no page for it. Walk 3 now runs the
  `version_option` `show_python` request, which is frame 243's own measure.

## 1. The cycle

The CYCLE line names `tester|tick:tests_missing|bg_2`, three rounds:
s195, s196, s197 (table `sessions`, `wake_detail` "without a test:
cr_2_confirm_default_on_eof, cr_4_confirm_default_on_eof"). `tick_attempts`
holds `tester|tick:tests_missing|bg_2`, attempts 3, quarantined 1. s198,
the Liaison's `tick:quarantined`, made the m91 page.

Each wake's prompt (table `turns`, seq 1): the wake line, `batches.expect`
with the touch list `src/click/termui.py, src/click/utils.py,
tests/test_defaults.py, tests/test_utils/test_confirm.py`, `criteria.load`
with the six criteria and the contest block (section 2), and `tests.consult`
with bg_2's four own tests `test_cr1`, `test_cr3`, `test_cr5`, `test_cr6`.
cr_2 and cr_4 have no test of bg_2 (table `tests`).

### s195 (8 turns)

- Turn 1: no triage, 13 `tests.encode` of `tst_cr2` on
  `tests/test_utils/test_confirm_stdin_closed_returns_default.py`, the path
  `test_cr1` already holds. The reply loops on "I keep making the same
  mistake". All 13 refused: "has no triage verdict from you yet" (turn 2
  `user`).
- Turns 2 to 3: triage `encodable` for cr_2 and cr_4, OK.
- Turn 3 result: "the surface 'src/click/termui.py::confirm' lives in
  termui.py and this test imports from click.testing". Right refusal.
- Turn 4 result: "the test uses CliRunner and never imports or defines it".
  Right refusal.
- Turns 5 to 6 results: "the test tst_cr2 passes `confirm` to `.invoke`,
  and `confirm` is a plain function in `src/click/termui.py`:
  `CliRunner.invoke` takes a command". Right refusal. The refusal names no
  route, for example a local command that calls `confirm()`.
- Committed: nothing.

### s196 (6 turns)

- Every encode is `tst_cr24_default_false_on_eof` with `runner.invoke(cli_app,
  ...)`. Refused 4 times: "the test uses cli_app and never imports or
  defines it". Right refusal. Turn 5 gets the NOTE "tests.encode has been
  refused the same way in three turns and will not be accepted again".
- Committed: nothing.

### s197 (9 turns)

- Turn 1 `cli_app_with_confirm` undefined, refused (right). Turns 3 to 4
  `runner.invoke(confirm, input="")`, refused by the plain-function door
  (right). Turn 4's reply wrote its own "ERROR tests.encode:" and the stream
  stopped there.
- Turn 5 reply: "I need to create a proper CLI application that wraps
  `confirm()` so it can be invoked by `CliRunner`." The body:

  ```
  def cli_app_with_confirm():
      @click.command()
      def cmd():
          confirm("Are you sure?", default=False)
      return cmd
  ...
  result = runner.invoke(cli_app_with_confirm(), input="")
  assert result.exit_code != 0  # Should abort
  ```

- Turns 6, 7 and 8 results, the same body refused 4 times: "confirm() reads
  input() through visible_prompt_func, a name termui.py bound to input at
  import, and this test calls confirm() under pytest, where stdin is
  captured: the call raises OSError before any assertion runs. ... Patch
  the name it reads through -- monkeypatch.setattr(...)". Turn 8 adds the
  NOTE that `tests.encode` will not be accepted again.
- Committed: nothing.

### Why no test landed

The refusal at s197 turns 6 to 8 is wrong. I ran the refused body, word
for word, on bg_2's head 39f9365 with pytest from the scratchpad: it passes,
and a second probe with `default_on_eof=True` returns the default (observed:
`scratchpad/n149/probe/test_s197.py`, 2 passed, 2026-10-15 15:4x).
`CliRunner.isolation` replaces `termui.visible_prompt_func` and gives the
command the input stream. So `confirm()` called inside an invoked command
never reads pytest's captured stdin. The door's predicate in
`rota/roles/api.py` is "the body calls a bare name whose function reads an
alias of `input`, and the body patches nothing". It does not look at
whether the call sits inside a command that `CliRunner.invoke` runs with
`input=`. The door is narrower than its fact, and it refuses a right call.

The other refusals in s195, s196 and s197 were right: an undefined name,
a missing triage, the wrong import module, and a plain function passed to
`.invoke`. The cycle had one right body, and the wrong door refused it.

### Is it frame 239's wall or frame 182's?

- Frame 239, `tests_missing` counts the abandoned batch's tests: no. bg_2 is
  not re-dispatched, the night has 2 batches only, and `tests_missing`
  named the right two criteria, those with no bg_2 test. The predicate read
  the right rows (table `batches`, `tests`).
- Frame 182, a batch runs attempts with no test of its criterion: no for
  this cycle's cause. The Developer's attempts ran with 4 own tests, and the
  Tester wakes were not missing. They woke three times and were refused.
- A new wall: the stdin-capture door refuses `confirm()` inside a command
  run by `CliRunner.invoke(..., input=...)`. Step 1 of section 4: no open
  frame names this door. Frame 176 is the invoke door's local wrapper miss,
  another predicate. Frame 230 is the lambda shape of the invoke door.

### Placement by `plans/wall-guide.md`

- Step 1: no open frame's sign. Step 2: the instrument is right, because the
  refusal is in the next turn's `user` text. Step 3: the sign does not name
  his words. Step 4: a door fired, and it was wrong to fire. Cause 8, "A
  door's predicate is not its fact".
- Fix kind, cause 8's "Cheap fix": a door or predicate change with its
  count, 2 to 3 cycles, because the key, a call inside a command passed to
  `.invoke` with `input=`, is a shape of the AST and not a word a seat can
  vary. Escalate: no, the predicate reads no words of his.
- The count the fix pass owes (reasoned: cause 8's "Confirm" line): the
  refusal text "where stdin is captured" appears in Tester sessions on
  nights 136 to 149: 35 sessions, 4, 2, 4, 4, 1, 4, 5, 3, 1 and 2 on nights
  136, 137, 140, 142, 143, 144, 145, 147, 148 and 149. 10 of those sessions
  also sent some `CliRunner` encode (observed: `scratchpad/n149/
  count_stdin_door.py`, table `turns` and `tool_calls`, 2026-10-15 15:4x).
  How many refused bodies were right is not counted, because
  `tool_calls.args_summary` cuts the body. The pass counts it from
  `turns.completion`.
- Next to the door: s197's refusal named only the patch recipe. It did not
  name the route the principal gave. That is the same cause, one door.

## 2. Frame 243, the held frame

Frame 243 validates at 7a2cb843. The night runs at 401bbf3f, which holds it
(reasoned: the frame's status line of 14:51 and the launch line).

### (a) The block and the criterion texts

The block reached every Developer and Tester wake after each landed contest
(table `turns`, seq 1, `user` contains `[the principal contested these
criteria]`):

| Wakes | Rulings in the block | Entries | Characters |
|---|---|---|---|
| s126, s127, s130, s133, s155, s157 (before m74) | none | 0 | 0 |
| s174, s175, s177, s179, s180, s181, s182, s183, s186 (after m74) | r_3aa5b4358e | 6 | 3772 |
| s191, s192, s193, s194, s195, s196, s197 (after m86) | r_3aa5b4358e, r_cb56c527ea | 12 | 7495 |

The m91 reply, m92, has no `rulings` row and no verdict. m91 is `open` in
`messages`. So m92's words reach no wake. Walk 3's log shows m91 put on the
page again.

His words, m74 (ruling r_3aa5b4358e): "Lines 2, 3, 5 and 7 are wrong: today
confirm aborts when stdin is closed, it doesn't raise a usage error." m86
(r_cb56c527ea): "Lines 3, 5 and 7 still say it raises a usage error when
today it aborts". m92: "Lines 2 through 7 still say confirm raises a usage
error, but today it aborts." m96 says it a fourth time.

Criterion texts (table `rulings.texts` for the texts he contested, table
`criteria` for the texts now):

- Before m74 (the texts in r_3aa5b4358e):
  - cr_1: "... it returns the configured default value instead of raising UsageError."
  - cr_2: "... existing callers without this flag continue to raise UsageError on EOF as before."
  - cr_4: "... maintaining backward compatibility where EOF raises UsageError."
  - cr_6: "... confirm() must not raise UsageError."
- After m74, respecified by s173 and s178 (the texts in r_cb56c527ea):
  - cr_2, cr_4, cr_6: "... returns the default passed to confirm itself instead of raising UsageError."
  - cr_1, cr_3, cr_5: "... (not an option's default)." No "UsageError".
- After m86, respecified by s190 (table `criteria`, now):
  - cr_1, cr_2, cr_4, cr_6: "... returns the default passed to confirm itself instead of raising a UsageError."
  - cr_5: "When default_on_eof is True and stdin is closed (simulated by empty input in tests), confirm() returns the default passed to confirm itself instead of raising a UsageError."
  - cr_3: "... (not an option's default)."

No criterion text holds "aborts" at any version. The m86 respecify put
"UsageError" back into cr_1 and cr_5, which the m74 respecify had cleared.
The Terminologist's ledger row l_edab131ffd holds his fact: "The principal
says confirm() currently aborts on EOF ... rather than raising UsageError"
(table `ledger`). The fact was in the record and the block, and the texts
kept the declined words. This is frame 243's seam 1 sign, a seat that has
the fact and judges wrong (reasoned: wall guide cause 5, frame 243's status
of 01:55).

### (b) The supersede door

`decisions_author` refused 0 `supersedes` calls on this night. The text "A
seat's decision does not replace his" is in 0 turns (table `turns`). Three
calls carried `supersedes`, all s109, Vision Keeper, turns 2 to 4, with
`supersedes='e_m26'` (table `tool_calls`). They met other refusals: "no
decisions row with id='e_m26'" and "'how_it_works' is already a row of
items". s109 then called `msg.report_liaison(refs=["how_it_works"])` and
ended. No `decisions` row on the night has `supersedes` set.

### (c) The longest contest block

7495 characters, in s191, s192, s193, s194, s195, s196 and s197: 12
entries, 6 criteria times 2 rulings. Each entry repeats his whole words, so
the m74 words (about 400 characters) appear 6 times. Frame 243's try record
gave 475 on night 148 and 8823 on night 138 (observed:
`plans/frame243-try.md`, copied, its mark and date kept). The 7495
characters did not move any criterion text toward his words (section 2a).

## 3. The two abandon pages

- m85: s187, `tick:quarantined`, wake detail "1 abandoned: tests_failing for
  bg_2 (developer), 3 attempts" (table `sessions`). The predicate is the
  Developer's `tests_failing` at 3 attempts. The 4 red tests were `test_cr1`,
  `test_cr3`, `test_cr5` and `test_cr6`, red at 2368388 (table `test_runs`
  tr71 to tr74). Each patched `sys.stdin` to `None`, which makes
  `_readline_prompt` raise `RuntimeError`.
  - "Keep working" landed on the same batch. m86 gave ruling r_cb56c527ea
    with `bg_2: approve`, verdict m87. The quarantine key for
    `tests_failing` is gone from `tick_attempts`. s192 and s193 ran
    attempts 2 and 3 on bg_2.
  - The Developer then committed 39f9365, "Add RuntimeError to EOF handling
    in confirm()": `except (KeyboardInterrupt, EOFError, RuntimeError)`
    (`git show 39f9365` in bg_2's worktree, read-only). The ledger row
    l_c3e37d54aa, by the Developer, says the test is the fault. The tests
    went green, 39 with 0 not passing, with the product fitted to the wrong
    tests. His own diagnosis at m86 was "they call confirm with no input
    stream at all".
  - Known wall: frame 171, "a Developer that knows the test is wrong writes
    the product to fit it" (reasoned: the frame's heading against 39f9365
    and l_c3e37d54aa). Not frame 239 and not frame 182.
- m91: s198, "1 abandoned: tests_missing for bg_2 (tester), 3 attempts". The
  predicate is the Tester's `tests_missing` at 3 attempts, the cycle in
  section 1.
  - "Keep going" landed nowhere at the copy: m92 has no verdict and no
    `rulings` row, and m91 is `open`. In walk 3 the log shows m91 on the page
    again and a shift park `ip_cb13772835`, `now`, from m104.
  - Known wall: no. It is section 1's new door wall, cause 8.

## 4. New data for frame 243, or a loop

The cycle is a loop on another wall, the stdin-capture door, with no page
for frame 243. Walk 2's pages before it (m73, m85, m91, m95) carry frame
243's sign: the declined "usage error" survived two respecifies with the
block present. That is already in hand. bg_2 has not merged, so the ratio
(merges that carry what he declined, toward 0 of 3) gets no count from walk
2. Walk 3 is the `version_option` `show_python` request, night 148's
merge of the declined format, so walk 3 is frame 243's main measure.
Do not stop walk 3 on this cycle (reasoned: the rule of 2026-10-09 20:19
applies to a night that measures nothing for the held frame).

## 5. Placement

- Cycle 1 of night 149: a new frame, cause 8. Site: the stdin-capture
  branch of `tests.encode`'s door in `rota/roles/api.py`. Ends when: the
  door admits `confirm()` called inside a command that
  `CliRunner.invoke(..., input=...)` runs, with s197 turn 5's body as the red
  test, and the count of right bodies refused over nights 136 to 149 falls to
  0. Price 2 to 3 cycles.
- m85: a case for frame 171.
- Frame 243: walk 2 adds one seam-1 case with the block present (3772 and
  7495 characters), 0 supersede refusals, and no merge.

Usage: about 85k tokens of 120k.
