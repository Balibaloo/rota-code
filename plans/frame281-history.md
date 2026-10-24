# Frame 281, the history read: what a test may fix in a call the criterion does not name

Meta workflow. Read-only, in the checkout at dde8b0fb, 2026-10-24 10:43.
Sources: `rota/LAWS.md`, `rota/DECISIONS.md`, `plans/archive/*.md`,
`plans/stack.md`, the Tester briefs and tool lists under
`rota/roles/prompts/tester/`, `tests/rota/test_prompts.py`,
`tests/rota/cases/l1_tester.yaml` and `git log -S`. `LAWS.md` and
`DECISIONS.md` are under `rota/`, not the root. `rota/rulings.py` does not
exist (observed).

## Verdict

**Open on one point, settled on two.** The records settle that a test may
write a literal the criterion does not name, with a ledger sentence
(ruled: Roman, 2026-08-30). They settle that the code says how a test calls
a function and the criterion says what the test asserts (ruled: Roman,
2026-09-24 21:20). No record says whether a test may rely on a value it
finds on the machine, such as an installed package, the clock or an
environment variable. One session judgement went the other way: frame
223's pass 1b made its case accept an installed package name as right
(reasoned: session rota-68, 2026-10-17). `challenge.md` line 8 is a session
judgement of frame 200, not a ruling, and it reaches further than the
2026-09-24 ruling lets it (reasoned: section 2).

## 1. The hits

### 1.1 A test may choose a literal the criterion does not name

1. "The design is **detected divergence**: mechanics locate the points
   where the material underdetermined the output (invented test literals,
   ...) and the sentence is demanded only there." and "Built 2026-09-02
   (`tests.encode`: a string the material never said is owed a ledger row
   first ...)" (ruled: Roman, 2026-08-30, "The four answers that closed the
   road's open problems", `plans/archive/completion-diary.md` lines 273 to
   290; also `plans/archive/responsibility-allocation.md` line 61).
2. "A string the material does not fix -- a sample name, a prompt's
   wording -- is an assumption, and the encode records it by itself."
   (observed: `rota/roles/prompts/tester/tests_missing.md` lines 47 to 49;
   the brief rule that carries the ruling of item 1).
3. "**`ledger.log`** when a criterion does not quite say what to assert and
   you decide. ... where the criterion was silent, the judgement was yours,
   and it should be visible." (observed:
   `rota/roles/prompts/tester/base.md` lines 22 to 24).
4. "An unsourced literal is an assumption logged `invented`" (observed:
   `tests_missing.md` line 11).

These settle that `version="1.0"` is a legal choice for the Tester. The
seat's stated block, "the criterion names no version string" (observed:
`plans/frame223-interview-2.md` section 9, 4 of 4 runs), is wrong against a
ruling the seat never sees in words (reasoned: no brief sentence says "you
may choose a value", only that an invented value is recorded).

### 1.2 How a call is made against what a test asserts

5. "the Tester's answer mode gains `code.source`, because a test that
   calls a function needs its signature and the criterion still rules what
   it asserts" (ruled: Roman, 2026-09-24 21:20,
   `plans/archive/stack-2026-09-25.md` lines 188 to 193; copied in
   `rota/roles/prompts/tester/challenge.tools` line 4 and `answer.tools`
   line 5).
6. "**You test the criterion, not the implementation.**" (observed:
   `tests_missing.md` line 20).
7. "Then answer ... with `quotes=` copying the criterion's words your
   assertion comes from, verbatim." and "What you do not do is soften the
   test to end the argument." (observed: `challenge.md` lines 12 to 21;
   the quote rule is ruled: Roman, 2026-08-26, "why is this not obvious?",
   `rota/DECISIONS.md` lines 1290 to 1298).

### 1.3 A test that depends on the machine

8. No hit. The searches for "installed", "the machine", "any machine",
   "environment", "clock" and "hermetic" in the Tester briefs, `LAWS.md`,
   `DECISIONS.md`, the archive and the stack find no rule on what a test may
   take from the machine (observed). `DECISIONS.md` line 62 says "hermetic"
   about roles, not tests (observed).
9. The one precedent is a session judgement against the recommended answer.
   Frame 223's pass 1b made the case
   `L1-TS-pass-a-literal-value-for-a-name-looked-up-at-run-time` accept
   `package_name` with "a name the run has installed", click, pytest or
   pip, because "click, pytest and pip are installed in every run"
   (reasoned: session rota-68, 2026-10-17 05:42 and 05:59,
   `plans/archive/stack-2026-10-17.md` lines 96 and 97; observed:
   `tests/rota/cases/l1_tester.yaml` lines 1471 to 1489). Interview 2 named
   the point and did not decide it: "Decide whether an installed name passes
   before pass 1b counts its runs" (reasoned:
   `plans/frame223-interview-2.md` lines 249 to 251).

### 1.4 A reason row or a challenge answer against a criterion

10. "When the reason row ... names the callable that takes an argument, the
    next body puts that argument on that callable, because the row outranks
    the criterion's wording and the traceback for where an argument goes."
    (reasoned: session judgement of frame 200, passes 5b, 5c and 5g, no
    ruling found; `challenge.md` line 8; section 2 gives the commits).
11. "`decided` outranks `observed`, and `observed` outranks `reasoned`."
    (ruled: ratified 2026-09-16, `rota/LAWS.md` lines 286 to 291). A
    Developer's reason row is a seat's own inference, so it is `reasoned`
    (reasoned: LAWS line 288, "Every other row is `reasoned`: a seat's own
    inference"). The criterion carries the principal's words. So a rule
    that a reason row outranks a criterion runs against the provenance
    order, unless "where an argument goes" is read as the call form only
    (reasoned).
12. "The answer is from the role that owns the artefact, so it settles the
    point." (observed: `answer.md` lines 3 and 4). This is about an owner's
    answer, not about a Developer's challenge. No rule lets a challenge
    answer override a criterion (observed).

## 2. The Tester's briefs, sentence by sentence

**What the Tester may fix:**

- `tests_missing.md` lines 47 to 50: a string the material does not fix is
  an assumption that the encode records. A function or a format the
  material does not name is `cannot` (observed).
- `base.md` lines 22 to 24: where the criterion is silent, the judgement is
  the Tester's and goes in the ledger (observed).
- `challenge.md` line 7: "fix the call line" when the run failed before any
  assertion (observed). The line does not say what a fixed call line holds.
- `answer.md` line 11: "call the function its surface names after you read
  it with `code.source`" (observed).
- No sentence says that the test sets the inputs the criterion leaves open,
  or that a value found on the machine is not set by the test (observed).

**What tells the Tester to follow a reason row:** `challenge.md` line 8
only (observed). `answer.md` line 13 makes `principal_said` binding, which
is the principal's words, not a row (observed).

**Where line 8 came from** (observed: `git log -S` on
`rota/roles/prompts/tester/challenge.md`):

1. ba2ddf5e, 2026-10-12 19:11, frame 200 pass 5b: "names a call and an
   argument, the next body puts that argument on the call the traceback
   names, because the row outranks the criterion's wording for where an
   argument goes". The commit says the probe of pass 5 found the Developer
   looped and the Tester weighed the criterion over the row.
2. 917eab20, 2026-10-12 19:59, frame 200 pass 5d: "the callable that takes
   an argument ... on that callable ... outranks the criterion's wording
   and the traceback". The reason was that the traceback named
   `runner.invoke`, the wrong call, and the Tester moved 5 of 5 bodies only
   on a reason that wrote out `version_option` with `package_name` in place.
   "No door changes."
3. 88cbbe5a, 2026-10-13 06:39, frame 200 pass 5g: "The next body goes on the
   test the row names, and on no other test".

The pin is `test_the_tester_puts_the_argument_where_the_reason_row_says` in
`tests/rota/test_prompts.py` lines 347 to 356 (observed). The stack status
of the pass names no ruling (observed:
`plans/archive/stack-2026-10-13.md` line 150). So line 8 is the session's,
made on the same click decorator that this frame's wall is on, to make the
Tester write `package_name` (reasoned). The rule did its job on frame 200's
case and now carries the false claim of night 162: d_d3197ebbd0 said "the
test does not pass package_name, which is required", and s309 obeyed it
(observed: `plans/night162-s305-interview.md` section 2).

Line 8 fits the ruling of 2026-09-24 when "where an argument goes" means
the call form, which callable takes which argument. It goes past the
ruling when a seat reads it as which input the test must set and with what
value, because that choice decides what the test checks (reasoned).

## 3. The question for Roman

How this came to be: the Tester rule that a value it invents gets one
logged sentence came from your answer of 2026-08-30. Nobody ever ruled on
values that the test finds already on the computer. On 2026-10-17 a session
judged that such a value is fine, and five Testers since then chose it.

The story. A Tester writes a check for "the version message ends with the
Python version". To run, the check must give the program some name and
number for the program's own version. The criterion says nothing about that
number. Today the Tester gives the name of a package that happens to be
installed on this computer. The check passes here. On a computer without
that package, the check fails before it looks at the message at all.

- If you answer yes, the check must choose its own number: the Tester
  writes "1.0" itself and logs one sentence about the choice. The check
  then passes or fails on the message alone, on any computer. The case
  that today accepts an installed package name changes to refuse it.
- If you answer no, the Tester may lean on what is installed. Checks keep
  passing here, and a check can fail somewhere else for a reason that has
  nothing to do with the change. The Developer's notes keep the power to
  tell the Tester which input to set.

The analogy: a recipe test that says "use whatever flour is in the
cupboard" passes in your kitchen and fails in the next one. A good recipe
test brings its own bag of flour.

**Recommended: yes.** A test fixes every input the criterion leaves open
with a value of its own. A value found on the machine does not count as
fixed, because the criterion is about the output and the test must pass on
any machine. The Developer's note says where an argument goes, never which
input the test sets or with what value.

## 4. The pass the answer names

Under yes, one pass and one review, 2 cycles, then one night (reasoned:
the frame's ends-when and the rule of 2026-10-04 14:52).

**The brief sentences that change:**

1. `rota/roles/prompts/tester/base.md`, after line 13, a new paragraph in
   all three wakes: "A test sets every input of its call that the criterion
   leaves open, with a value of its own, and logs the choice. A value the
   test finds on the machine, such as an installed package, the clock or an
   environment variable, is not set by the test." `base.md` reaches
   tests_missing, challenge and answer, and s327 was an answer wake
   (observed: `plans/night162-s305-interview.md` section 3). The sentence
   names no product, no parameter and no error text (reasoned: frame 223
   interview 2, section 9, "What overfits").
2. `rota/roles/prompts/tester/challenge.md` line 8, narrowed to the call
   form: the row says which callable takes an argument, and the next body
   puts the argument there. A claim in the row that an argument is
   required is the Developer's reading, and the criterion and the sentence
   of item 1 decide which input the test sets. The pin in
   `tests/rota/test_prompts.py` lines 347 to 356 changes with it.
3. `challenge.md` line 7, "fix the call line", gains a pointer to the
   sentence of item 1, so a call line fixed after a raise sets its own
   values (reasoned: s305 followed line 7 and took the error's name,
   `plans/night162-s305-interview.md` section 2).

**The door:** none. A door that refuses the argument an error suggests
overfits, and a door cannot tell a value found on the machine from one the
test set without running the test elsewhere (reasoned: frame 223 interview
2 section 9; frame 304 already admits a call that fails only on the lookup).
The existing invented-literal detector of 2026-09-02 asks the ledger
sentence for "1.0" already (observed: `plans/archive/completion-diary.md`
line 290).

**The case that changes:** the expectation of
`L1-TS-pass-a-literal-value-for-a-name-looked-up-at-run-time` drops the
installed names click, pytest and pip from `text_includes_any`, and keeps
`version_option(version=` and its two other literal forms (observed:
`tests/rota/cases/l1_tester.yaml` lines 1483 to 1489).

**The red tests,** replays of the recorded system and user text with the
new briefs, each one cell on one load, none gating alone (observed:
`plans/frame223-interview-2.md` section 8):

| source | the turn | red today | green |
|---|---|---|---|
| night 162, s305 | turn 1 | `package_name="test_version_option_show_python"` | a literal version or another source the test sets |
| night 162, s307 | turn 1 | no source, `version` read as the Python version | a source the test sets |
| night 162, s309 | turn 1 | `package_name='python'`, cites d_d3197ebbd0 | a set source, and the row not read as naming the input |
| night 162, s327 | turn 1 | `package_name='click'`, passes only because click is installed | the fixed string it named itself |
| frame 223, run 1 | row 56664 | `package_name="test_version_option"` | a literal version |
| frame 223, run 2 | row 56668 | prose cut at the budget, no call | a body with a literal version |
| frame 223, run 3 | row 56670 | `package_name="test_package"` | a literal version |
| frame 223, run 4 | row 56673 | `package_name="test_version_option"` | a literal version |

Row 56663, the shared turn 1 of frame 223's runs, wrote `package_name="click"`
under replay C and is red under yes too (observed: interview 2, section 8).

**The price:** 2 cycles. The pass is about 60k on Opus with the replays,
and the review about 40k (reasoned: frame 223's pass 1b and review 1 at
20k and 74k). A change to `base.md` stales every Tester case, not only the
five challenge cases, so the re-records are the larger bill (reasoned: the
recordings carry the system text; `rota/DECISIONS.md` line 1287 on a
signature change). The validation is the frame's third ends-when: on a
night, bodies after a reasoned challenge that pass the harness on the first
run, read beside frame 223's ratio.

Under no, the pass is one sentence that tells the Tester it may choose a
literal, and line 8 stays. The case stays as it is. 1 cycle.
