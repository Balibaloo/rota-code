# Frame 304, the provenance: the encode door admits a test whose arrange step raises before the call under test

Provenance read on Opus, 2026-10-23, by the ruling of 2026-10-18 12:02
(every new wall gets a provenance read before its first fix). Repository at
HEAD 631dcb25, branch `rota/foundation`. Sources: `rota/roles/api.py` 7545
to 9082 (`tests_encode`), `rota/core/harness.py` 96 to 340,
`rota/core/runner.py` 665 to 690 and 2610 to 2715, `git log -S` on each
door's refusal text, `rota/DECISIONS.md` lines 943 to 968,
`plans/operating-facts.md` lines 291 to 300, `plans/frame110-design.md`,
`plans/night158-read.md` row W2, `plans/wall-guide.md` cause 8, and
`.rota/clickI_night140.db` to `clickI_night158.db` opened `?mode=ro`. Count script:
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/2214bec6-a6fe-4d67-816b-461298d9db78/scratchpad/f304_count.py`.
Meta workflow. No file but this one is changed.

## The provenance in one paragraph

`tests.encode` was born on 2026-08-09 as `tests.author` with no door, and
every door on it since is a static read of the body (observed: 231afe4c).
The doors hold one class, "harness facts", ruled at the door because "each
is certain independent of what the criterion means" (observed:
`rota/DECISIONS.md` lines 943 to 958). The class names "a test that calls
`input()` raises before any assertion", so the arrange-step raise is inside
the class. No door reads an arrange step for a raise in general, and frame
110 named the nearest case and declined a door on 2026-10-02, because it
"need[s] a list of runner callees, which is framework knowledge" (observed:
`plans/frame110-design.md` line 77). Frame 110 sent the case to the Tester's
challenge brief, and that route reaches a test only when a challenge names
it (observed: `runner.py` line 676). On night 158 no challenge named
tst_02, the harness stored its `AttributeError` as `fail`, which its own
docstring reads as "the code is wrong", and the Architect read a 700-char
tail that starts inside `mock.py` (observed: section 5). The build met the
class's condition for every shape it measured, and it missed this shape
because the fact is certain only after a run (reasoned: section 7).

## 1. Which ruling or design made `tests.encode` and its doors

- **The op.** 231afe4c, 2026-08-09 10:48, "feat(sandbox): namespaces built
  from edges, and the TOOL: protocol", made `tests_author` (observed: `git
  show 231afe4c`, the diff's line 378). Its whole body wrote the row. Its
  docstring was "Criteria made executable, written before the diff exists",
  and the docstring stands at HEAD (observed: `api.py` line 7548).
- **The name.** The edge audit of 2026-08-09 said "`author` means two
  different acts" and suggested `tests.encode`: "A test encodes its
  criterion" (observed: d6859bec, `rota/EDGE_AUDIT.md`). fdad09df,
  2026-08-10, renamed the op (observed: the commit body, "tests.author
  became tests.encode").
- **The first door.** bfd149d1, 2026-09-01 20:14, "a test is Python the
  harness can run": "ast.parse has no opinion about quality, only about
  whether anything can execute" (observed: the commit body).
- **The class.** ebc9bafd, 2026-09-02 01:16, "harness facts are refused at
  encode": "Two of those are facts about pytest and are refused at encode
  with the shape that works" (observed: the commit body). DECISIONS records
  the class as "Harness facts are refused at the door; judgement stays with
  the roles", "Built across S0 walks eight to thirteen (2026-09-02)"
  (observed: `rota/DECISIONS.md` lines 943 to 945).
- **The ruling over it.** Roman, 2026-09-02, "these deterministic checks
  I'm not so sure about their quality, the system prompt is where the real
  work is I believe" (ruled: Roman, 2026-09-02, `plans/operating-facts.md`
  line 293). The build's own rule then reads "Prefer the brief unless the
  rule is a fact about the harness (stdin, imports, stale runs) or state
  semantics" (observed: the same page, line 297).
- **The workflow.** The op is the rota workflow's Tester's. The meta
  workflow built every door after a measured loop (observed: section 2).

## 2. What each door before the run checks today

Each line names the check, its first commit, and the case (observed: `git
log --reverse -S` on each refusal text).

1. Path made one form, backslashes to slashes. Frame 135's review, eb6c7ef, a row that ran as "no tests ran".
2. An id of dots only is refused. e6a45c27, 2026-10-06, frame 152's review.
3. No `encodable` triage verdict from this session. 8efa18cc, 2026-09-14, the refusal says the step.
4. The path ends `.py`, the body parses, and it holds a `def test_` with an `assert`. bfd149d1, 2026-09-01, S0's English-sentence test.
5. The fence: a reach that no criterion names. e8e1a207, 2026-09-10, "a written file reaches only what the criteria name".
6. A name used and never imported or defined. e8c68bec, 2026-09-02, walk twelve, widened on walks thirteen and twenty-five.
7. A body that calls `input()` under pytest's captured stdin. ebc9bafd, 2026-09-02, walk eight's nine rounds.
8. A body that closes `sys.stdin`. a27aadf7, 2026-09-14, click night 50.
9. A called function in the worktree reads `input()`. e6fbf260, 2026-09-03, "the stdin trap, one function-call hop indirect".
10. One module name for the batch's program. 7b886078, 2026-09-02, walk thirty-two.
11. A fixture that plain pytest lacks. 15d8747c, 2026-09-02, walk twenty-nine's `mocker`.
12. Every assert on a constant. 837391d8, 2026-09-02, walk ten.
13. Every assert ends `or True`. 000dfa78, 2026-10-17, frame 273, night 152.
14. An `or` whose operand reads the interpreter alone. 7b48a630, 2026-10-17, frame 277, night 153.
15. A literal version named back when the criterion names the interpreter. dcea6fd7, 2026-10-18, frame 143's sign, night 156.
16. `assert print(...)`. Kept as "the fact and no recipe" at 6b52a09d, 2026-09-15 (ruled: Roman, 2026-09-15, cited in `api.py` line 8294).
17. A call on a Mock that is not a real Mock method, in an assert. fd0e50db, 2026-09-03, the empty-project walk.
18. An import of a module the tree lacks. aa23868a, 2026-09-12.
19. An import from the surface's module of a name it does not define. 10476912, 2026-09-09.
20. The surface's module must load in the sandbox. Frames 215 and 222, nights 142 and 143.
21. The test never calls the criterion's surface. 0a6285ed, 2026-09-03, "a test that never calls its own surface has verified nothing".
22. `CliRunner.invoke` on a plain function. 6c83f6c0, 2026-10-07, frame 131, five nights.
23. `CliRunner.invoke` on a lambda or a local `def`. 0d0f4771, 2026-10-15, frame 230, night 148.
24. The criterion's own sentence written back. 38dff85e, 2026-08-15, ten runs of ten.
25. A decorator factory read for stdout. 83124f5b, 2026-10-07, frame 177, night 128.
26. A call form that never runs the option a factory adds. 2e6afd1c, 2026-10-11.
27. The return value of a printing surface, logged as an assumption. 8234b716, 2026-09-13, click night 28.
28. A criterion in no batch and no woken batch. 82c45e65, 2026-08-14.
29. A byte-identical re-encode is reported, not stored. 38dff85e lineage, law 14.
30. A project test's id outside a challenge. c68bd0ef, 2026-10-05, frame 135, night 120.
31. A second test on one criterion. 38dff85e, 2026-08-15, four paraphrase rows.
32. A test of another batch. c76006db, 2026-10-04, night 147.
33. Two tests on one path. e8c68bec, 2026-09-02, walk twelve.
34. A replace supersedes this session's staged tests on the criterion. 5eaf0882, 2026-10-04, night 117.

`tests.encode` runs no test (observed: no `harness` or `execute.run` call in
`api.py` lines 7545 to 9082, except the import probe of door 20 at line
14373). So "the sandbox run" in this page means the harness run of the
stored row in the batch's worktree, section 4 (reasoned: the brief's words).

## 3. Whether a door reads the arrange step

- **Seven doors read the whole body, the arrange step included.** Doors 6,
  7, 8, 9, 11, 18 and 19 walk every node of the tree (observed: `api.py`
  lines 7653 to 8040, 8364 to 8600). Each reads one named fact. None asks
  whether a statement before the surface call raises.
- **The Mock door reads asserts only.** Door 17 walks `a.test` of each
  assert (observed: `api.py` line 8308). Its premise is "Mock invents an
  attribute for any name asked of it" (observed: lines 8300 to 8301). A mock with a
  spec breaks that premise. `mock_open` builds `MagicMock(spec=open)`, so
  `.read` raises (observed: the run's `E` line, section 5).
- **A design named the nearest case and declined the door.** Frame 110,
  revision 2, 2026-10-02, the holder: "No guard in `tests.encode`. Option
  (b) and the positional-args variant are declined: both need a list of
  runner callees, which is framework knowledge, and the destination is any
  small Python repository" (observed: `plans/frame110-design.md` line 77).
  The case was a test that "cannot run against any code" and "failed before
  any assertion" (observed: the same page, lines 76 and 103).
- **The design's route.** Frame 110 put the case in the Tester's challenge
  brief, and in a label, "failed before any assertion", that
  `_failed_before_assertion` computes from the run (observed: e7cd1b39,
  2026-10-02, `runner.py` lines 2658 to 2687). The label reaches a Tester
  challenge wake only (observed: `runner.py` line 676).
- **No design names an arrange step, or a spec'd mock.** "arrange" and
  `mock_open` appear in `plans/` only in `night158-read.md` and `stack.md`
  (observed: grep over `plans/`). So the build left out no named case
  (reasoned: the grep).

## 4. What the run does with a test whose arrange step raises

1. `harness.run` runs pytest on each stored row at the batch head, and
   keeps 2000 characters of tail (observed: `harness.py` lines 96 to 160,
   218).
2. `_run_one` maps exit code 1 to `fail` (observed: lines 221 to 224). A
   raise in the test function is exit 1, so tst_02 is `fail` (observed:
   `test_runs`).
3. The docstring says "`fail` says the code is wrong, `error` says the test
   could not answer" (observed: lines 177 to 178). So the run calls the
   test's fault the code's (reasoned: 2 and 3).
4. No run of the batch's own tests at the base exists. `record_base_run`
   runs the inherited tests only (observed: `harness.py` lines 269 to 274
   and 300 to 340). So no record shows that the test fails the same way
   before and after the change (reasoned: the same lines).
5. The red row goes three ways. The `tests_failing` tick wakes the
   Developer with the batch's red tests. An escalation or a challenge
   resolves the test ref with its last run, 700 characters of tail for every
   role but a Tester challenge (observed: `runner.py` lines 2615 to 2641). A
   Tester challenge wake gets the whole output and the label (observed:
   lines 676 to 680).

## 5. The record of night 158

- **The rows.** tst_confirm_eof_01 v7, tst_confirm_eof_02 v3,
  tst_confirm_eof_03 v4, all of bg_2 (observed: `tests`). tst_02 was written
  by s171 (v1), s179 (v2) and s187 (v3), and by no session after s187
  (observed: the `OK tests.encode` lines in `turns.user`).
- **s187's three encodes, by seq.** Seq 8 to 10 were refused: "the test uses
  confirm and never imports or defines it" (door 6). Seq 11 to 13 were
  refused: "the test uses mock_open and never imports or defines it" (door
  6). Seq 14 to 16 landed: `OK tests.encode -> {"id": "tst_confirm_eof_02"}`
  and the same for 01 and 03. Seq 20 to 22 were byte-identical and came back
  "unchanged" (observed: s187 turns 2 to 6, `user`).
- **The three bodies at seq 14 to 16 share one arrange step**:
  `with patch("sys.stdin", new_callable=mock_open) as mock_stdin:`, then the
  raising line (observed: s187 turn 4 `user`).
- **The raising line of tst_02 v3**, quoted:
  `mock_stdin.read.return_value = ""  # Empty read implies EOF`. The run
  says `E   AttributeError: Mock object has no attribute 'read'` at
  `unittest\mock.py:696` (observed: `test_runs`, f7bb9d5f, attempt 11).
- **What the doors returned.** Door 6 fired twice on the import of `confirm`
  and of `mock_open`. Then no door fired, and the three bodies landed
  (reasoned: no refusal in turn 4's `user`).
- **The last runs.** At f7bb9d5f, tst_01 and tst_03 pass and tst_02 fails.
  All 35 inherited tests pass (observed: `test_runs`, attempt 11).
- **dec_123**, s189, woken by m77, the Developer's escalation that named all
  six refs: "The test fails because the mock object does not have the
  attribute 'read', indicating the code does not handle the default_on_eof
  parameter correctly" (observed: `decisions`, `sessions`, `messages`).
  **dec_124**, s192, woken by m79, supersedes dec_123 with the same text
  (observed: the same).
- **What the Architect read.** s189 turn 1 held three `last_run` tails. Each
  tail starts at `name = 'read'` inside `mock.py` and holds no line of the
  test body (observed: s189 turn 1 `user`, the string
  `mock_stdin.read` absent from all three tails). The Architect gets no
  "failed before any assertion" label (observed: section 4, item 5).
- **The challenges.** m81 and m83 named tst_confirm_eof_01 only (observed:
  `messages.body_refs`). s194, woken by m81, wrote "`mock_open` does not
  create a mock object with a `read` attribute" and fixed tst_01 (observed:
  s194 turn 1 completion). Only m77 names tst_02 (observed:
  `messages.body_refs`). The batch ended `deferred` (observed: `batches`).

## 6. The count over nights 140 to 158

**1 stored body of 138, and 1 red run of 76.** The one is tst_02 v3 of
night 158, and its batch died, `deferred` (observed: the count script, all
19 nights).

- **The judgement, from the run.** For each red run of a batch's own test, the
  script finds the line pytest marks `>` inside the test's own body. The run
  "raises before the call" when that line is not an `assert` and comes
  before the first body line that calls a surface name (reasoned: a traceback
  marks the line that raised).
- **The judgement, static.** Stored bodies that patch with
  `new_callable=mock_open` and read an attribute of the bound name: the same
  single row (observed).
- **The limits.** 17 of the 76 red runs gave no answer. 9 showed no `>` line
  of the body, 9 had no body line that calls the surface, and one had both
  (observed: the script's `unmatched` list).
  `test_runs` keeps only the last run per commit, and a re-encode deletes a
  test's runs (observed: `harness.py` lines 150 to 155,
  `plans/frame110-design.md` line 10). So the count is a floor (reasoned).
- **The same shape, refused for another reason.** Night 147's s315 encoded
  `mock_stdin.read.return_value = ''` under `new_callable=mock_open` in
  five turns. Doors 6 and 28 refused every one, and none landed. Its bg_2,
  the same item, ended `abandoned` (observed: s315 turns 2 to 6,
  `batches`).

## 7. The condition, the rulings, and the repair

- **The condition.** The class admits a door when the fact "is certain
  independent of what the criterion means" (observed: DECISIONS line 955).
  An attribute read on a mock with a spec that lacks it is certain under
  every model and every criterion (reasoned: Python's mock semantics). So
  this shape meets the condition, and no door holds it (reasoned: section
  3).
- **The general case is certain only after a run.** Frame 110 refused a
  static list for that reason (observed: section 3). The build met the
  condition on every shape it measured, and it met this one first on night
  158 (reasoned: the count).
- **The harness word.** The run calls the raise `fail`, "the code is
  wrong", and dec_123 and dec_124 read it so (reasoned: sections 4 and 5).
- **Against the rulings.** A static door on the spec'd mock shape extends
  DECISIONS 943 by one entry, as each walk did. It does not reverse frame
  110, because it needs no runner list. A run-time label narrows nothing,
  and it extends frame 110's label from the Tester challenge to every reader
  of the red row (reasoned: sections 1 and 3). The build's rule under
  "prompts over guards" exempts harness facts (observed:
  `operating-facts.md` line 297).
- **The repair I would brief.** The harness marks a red run as `error`, the
  test could not answer, when the line that raised is a test-body line
  before the first surface call and the last frame lies outside the
  worktree's source. The `tests_failing` route then wakes the Tester on that
  test with the frame 110 label, and the Architect's resolved ref carries
  the same label.
- **What I doubt.** One case in 19 nights may not pay for a run-time
  change to a word that every predicate reads (reasoned: the count and
  `wall-guide.md` cause 8, "Overfits"). An arrange step can also call
  project code that raises because the code is wrong. The last-frame clause
  must hold that case, and 17 unread runs could hide a counter-case
  (reasoned: section 6, the limits).
