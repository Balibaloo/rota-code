# Frame 301, provenance: the stdin predicate of `tests.encode`

Read by session 5389be74 on 2026-10-21, by the ruling of 2026-10-18 that a
provenance read comes before the first fix. Meta workflow. The probe is
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/5389be74-1e5e-433d-aa86-c4a8d594cb8e/scratchpad/test_f301_probe.py`.

## The provenance in five sentences

The session made the stdin predicate itself on 2026-09-02 at ebc9bafd, in
the Rota workflow, after S0 walk eight, with no ruling by Roman (observed:
the commit message; no plan page names walk eight except
`plans/frame132-design.md` line 235). The worktree scan that fires on
night 157 came one day later at e6fbf260, and the alias text
`visible_prompt_func` came on 2026-09-14 at eceabf2d after click night 53
(observed: `git log -S`). The offer "call it inside a @click.command() and
run that command with CliRunner()" is frame 254's condition of 2026-10-15,
built at 0865fe13 on 2026-10-16, after night 149's s197 sent the
principal's own recipe and the door refused it (observed:
`plans/archive/stack-2026-10-16.md` line 117, `plans/night149-cycle1.md`
line 147). Frame 254's helper `_invoked_command_calls` admits only the calls
written in the command's own body, and only when the body imports `click`
by name, so s258's helper shape and s266's body without `import click` both
fall back to the old scan, which names the alias and appends the offer
(observed: `rota/roles/api.py` lines 6609 to 6720, 7594 to 7596 and 7698 to
7715; the probe, three bodies, 2026-10-21). The offer is newer than the
predicate's reach by one commit, and review 1 of frame 254 named the helper
shape as a wrong refusal on 2026-10-16, low, before the frame closed
(observed: `plans/frame254-review-1.md`, finding 1).

## 1. Which decision made the stdin predicate

The session made the predicate on 2026-09-02 at ebc9bafd, "fix(sandbox):
the disputed test carries its run, harness facts are refused at encode"
(observed: `git log -S "stdin is captured" -- rota/roles/api.py`). The
commit message names the cause: S0 walk eight, four tests that called
`input()` and asserted on `print()`, nine rounds of Developer challenge and
Tester hold, "Two of those are facts about pytest and are refused at encode
with the shape that works" (observed: `git log -1 ebc9bafd`). The code
comment at `rota/roles/api.py` lines 7585 to 7592 repeats that account
(observed). No ruling by Roman is recorded for it. The stack starts on
2026-09-16, and the only plan page that names walk eight is
`plans/frame132-design.md` line 235, which cites its livelock (observed:
`grep -rn "walk eight" plans/`). So the decision is the session's own, in
the Rota workflow, a door inside the sandbox (reasoned: a commit that changes
`rota/roles/api.py` for a measured wall of a run is the Rota workflow by the
stack's convention).

Three commits widened the predicate's reach:

- e6fbf260, 2026-09-03, "the stdin trap, one function-call hop indirect":
  the scan of the worktree's non-test files for the definition of each
  bare-called name that reads `input()` inside (observed: the commit
  message; `rota/roles/api.py` lines 7632 to 7660).
- 5fe260a6 and eceabf2d, 2026-09-14, click nights 52 and 53: a module-level
  name bound to `input` counts as `input`, and the refusal names the alias
  to patch, `visible_prompt_func` (observed: `git log -S
  "visible_prompt_func"`; the comments at lines 7668 to 7672).
- 538b84a9, 2026-10-02, night 106: one AST helper `_stdin_shields` for the
  shield check (observed: the commit message).

The Developer-side door at `rota/roles/api.py` lines 15354 to 15362 and
15689 to 15745 is the same fact from the writing side, made at 837391d8
(walk ten, 2026-09-02) and 3bca3790 (2026-09-03). It is not the door that
fired on night 157 (observed: the night's refusals all come from
`tests.encode`, `.rota/clickI_night157.db`, `turns` of s258 and s266).

## 2. Which decision shaped the offer text

Frame 254 shaped the offer, pushed on 2026-10-15 from night 149's cycle 1
read and built on 2026-10-16 at 0865fe13 (observed: `git log -S "Or call it
inside a @click.command()"` returns 0865fe13 only; `plans/archive/stack-
2026-10-16.md` line 117). The read set the condition: "s197's refusal named
only the patch recipe. It did not name the route the principal gave. That is
the same cause, one door" (observed: `plans/night149-cycle1.md` line 147).
The frame's "Ends when" repeats it: "the refusal that stays names the route
the principal gave" (observed: the stack entry). The route is the
principal's recipe at m86 and m92 of night 149 (observed:
`plans/night149-cycle1.md` line 16). The text lives in `_INVOKE_ROUTE`,
`rota/roles/api.py` lines 6723 to 6726, and both stdin refusals of the scan
append it when the body imports click or the module is click's (observed:
lines 7698 to 7700). So the offer comes from a design condition of the Meta
workflow's read, and from no ruling of Roman's beyond his recipe to the
team (reasoned: the read's words, "the route the principal gave").

## 3. How the predicate finds the call

The predicate walks the whole test module, not the test function only.
`calls` is every `ast.Call` in the tree (observed: line 7594). It removes
the calls that `_invoked_command_calls(tree)` returns, and the rest are
`free_calls` (observed: lines 7597 to 7598). `called_bare` is the bare names
among the free calls, and the scan refuses when a worktree function of that
name reads `input()` or an alias of it (observed: lines 7653 to 7654 and
7678 to 7690).

`_invoked_command_calls` sees a `@click.command()` function invoked through
`CliRunner().invoke(..., input=...)` only under four conditions (observed:
lines 6609 to 6720):

1. The body names `CliRunner` somewhere (lines 6635 to 6639).
2. The decorator's head is `command` or `group` imported from click by name,
   or `<name>.command` where `<name>` is bound by `import click` in the body
   or is a group in the body (lines 6640 to 6657, the `verb` function).
3. The `.invoke` call carries an `input` keyword (lines 6708 to 6711).
4. The calls it returns are the calls written in the command's own body,
   `for stmt in f.body: ast.walk(stmt)` (lines 6716 to 6718).

The probe ran the door through `tests/rota/test_night46_context.py`'s
`_termui_alias_batch` and `_encode`, the fixture frame 254's own tests use,
on three bodies (observed: the probe's output, 3 passed, 2026-10-21):

- s266's turn 4 body: `_invoked_command_calls` returns 0 calls. The body has
  `from click.testing import CliRunner` and `from click.termui import
  confirm` and no `import click`, so `click.command` fails condition 2. The
  refusal is the alias text of line 7704, "confirm() reads input() through
  visible_prompt_func ... Or call it inside a @click.command()".
- s266's body with `import click` added: 1 call admitted, and the door
  admits the test.
- s258's turn 3 body (`cmd` calls a helper `confirm_cmd`, which calls
  `confirm`): `_invoked_command_calls` returns 1 call, `confirm_cmd()`. The
  `confirm()` call inside the helper is free, so the same alias text fires
  (observed: `.rota/clickI_night157.db`, s258 turn 4 `user`, four refusals
  of the two ids).

s266's body is wrong by its own words, because `click` is unbound at run
time (observed: the body). The NameError guard at lines 7889 to 7892 would
name that fault, but the stdin scan runs first, so the refusal names a
fault the body does not have (reasoned: the order of the checks in
`tests_encode`; the probe shows the guard admits the body once `click` is
imported).

## 4. The design's condition and whether the build met it

Frame 254's condition: "the door admits `confirm()` and its kin called
inside a command that `CliRunner.invoke(..., input=...)` runs, with s197
turn 5's body as the red test, and the refusal that stays names the route
the principal gave" (observed: `plans/archive/stack-2026-10-16.md` line 117,
"Ends when"). The build met it on the red test's shape: s197's body has
`import click` and calls `confirm()` directly inside `cmd`, and the test at
`tests/rota/test_night46_context.py` lines 903 to 917 admits it and a
group's subcommand (observed: `S197_TURN5` at lines 870 to 893). The count
over 231 recorded bodies gave 0 of 4 right bodies refused and 106 of 106
wrong ones refused (observed: the status of 2026-10-16 01:43).

The CliRunner shape is a test case of the door in both directions. The
admitted cases are lines 903 to 917. The refused cases at lines 920 to 943
are a direct call, a plain function passed to `.invoke`, a command run with
no `input=`, and `@runner.command()`, and each asserts the offer text
`CliRunner().invoke(cmd, input='y')` (observed). No case covers a helper
that the command calls, and no case covers a body that writes
`@click.command()` without `import click` (observed: `grep -rn
"invoked_command_calls\|stdin is captured" tests/rota/*.py` returns only
line 942).

Review 1 saw the helper shape before the frame closed: finding 1, low,
CONFIRMED, "A command that calls a local helper, which calls `confirm()` or
`input()`, is refused" (observed: `plans/frame254-review-1.md`, section b).
The session judged that the lows wait on night 150's count, and the frame
closed on 2026-10-16 22:30 after three nights at 0 (observed: the status
lines of 01:49 and 22:30). So the design's condition was met on its own red
test, and the reach it set stopped one hop short of its words, "and its
kin" (reasoned: the finding against the condition).

## 5. Why the refusal offers a shape the predicate refuses

The offer is newer than the predicate's reach, by one commit. The scan that
fires is e6fbf260 of 2026-09-03, and its text with the alias is eceabf2d of
2026-09-14. The offer sentence and the admission were added together at
0865fe13 on 2026-10-16, and the admission covers less than the offer
promises (observed: `git log -S` for both strings; lines 6716 to 6718
against line 6724). The offer is a constant, `_INVOKE_ROUTE`, appended to
every stdin refusal of a click body (observed: lines 7698 to 7700). The
refusal does not read whether the body already has the shape, so a body one
hop from the admitted shape gets the offer of the shape it has (reasoned:
the code path; the probe). This is cause 9 of `plans/wall-guide.md` line
460, the refusal's text points the seat wrong, on top of cause 8 at line
408 (observed: the guide's headings; `plans/night157-read.md` section 2, W1).

## 6. What a cheap fix is allowed by the history

No record forbids the predicate from admitting a `confirm()` call inside a
function that the test invokes through `CliRunner().invoke`, by any hop.
Frame 254's condition says "confirm() and its kin called inside a command"
and review 1's finding 1 names the helper shape as a wrong refusal, so the
widening is the design's own words (observed: the stack entry; the review).
The one constraint the records keep is the count: a body that reaches the
harness and fails there is read on the next night, and the 106 wrong bodies
must stay refused (observed: frame 254's second "Ends when" clause; the
review's point 6). For s266's shape, the records allow the NameError guard
to speak first, or the offer to stand down when the body already names
`@click.command()` and `.invoke(..., input=...)`, because the offer's only
condition is that the refusal "names the route" (reasoned: the condition
names the route for a refusal that stays right, not for one that is wrong).
