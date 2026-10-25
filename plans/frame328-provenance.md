# Frame 328, the provenance read: a test red on any code

Date: 2026-10-25. Read at commit 1782d95a on `rota/foundation`. Night 166 ran at
741d2d06. Read-only: `.rota/clickI_night166.db` opened with `mode=ro`. Meta
workflow, by the rule of 2026-10-18 (provenance before a fix).

Sources:

- `plans/night166-read.md`, section 2 row W-A, the W-A candidate, section 5.
- `.rota/clickI_night166.db`: `sessions`, `turns`, `tool_calls`, `messages`,
  `criteria`, `tests`, `test_run_journal`, `batches`.
- `rota/roles/api.py`: `tests_encode` 8935 to 10547, the run call at 10512 to
  10518, `_encode_run` 16966, `_arrange_run_refusal` 17021.
- `rota/core/sandbox.py`: `_quotes_span` 940, `_challenge_evidence` 1219 to
  1420, `_sent_this_session` 1534, the one-send door 4026 to 4031,
  `_challenge_admitted` 5046.
- `rota/core/predicates.py` 860 to 883 (`do:harness`), 949 (`tests_failing`).
- `rota/core/runner.py` 698 to 764 (the contested-text block).
- `rota/roles/prompts/developer/tests_failing.md`, `tester/base.md`.
- `rota/DECISIONS.md` 1056 to 1082 and 1248 to 1297.
- `plans/stack.md` frames 304, 143, 321, 201. `plans/frame304-provenance.md`.
- `plans/wall-guide.md`, causes 5 and 8.
- `git log -S` on each door and brief line named below.

## The result

**Verdict: two gaps and one departure. The encode door ran s198's tests on the
batch's head and admitted the red by design. The challenge door admitted a
paraphrase because its build checks 12 characters, not the quote.** The encode
run came from frame 304 on 2026-10-23, and its rule admits a failed assertion
on purpose. That rule rests on the charter "You write before the implementation
exists". On night 166 the Developer committed the right docstring before the
Tester woke, so the charter's condition did not hold, and no design covers a
red assertion on a head that already holds the code (mechanism 1, a gap). The
quote door was ruled on 2026-08-26 as "a contiguous span of the disputed row,
verbatim", and the build of 2026-08-27 asks only that some 12 characters of the
row appear in the joined quotes: m82 and m88 passed on "When shorten"
(mechanism 2, a departure). One test per session comes from a one-send door of
2026-08-14 made for questions, and no design covers a batch with several wrong
tests (mechanism 3, a gap). The repairs are a note at encode, about 15 lines,
and a per-side quote check with a green-test refusal, about 35 lines. Neither
needs Roman.

## Mechanism 1: a test written at encode is never judged on its result

The chain:

1. The Tester's charter puts the test before the code: "You write before the
   implementation exists and you never see it" (observed: `tester/base.md`
   line 3, present at b519a246, 2026-08-10). The encode docstring says the
   same: "Criteria made executable, written before the diff exists"
   (observed: `api.py` 8938). Under that condition a red assertion at encode
   is the normal state, because no code exists yet (reasoned).
2. Frame 110's design of 2026-10-02 declined a guard in `tests.encode` for a
   test that "cannot run against any code". It sent the case to the Tester's
   challenge brief and a run label instead (observed:
   `plans/frame304-provenance.md` lines 121 to 131, quoting
   `plans/frame110-design.md` line 77). Rota workflow.
3. Frame 304 built the first run at encode. Judged on 2026-10-23 17:52
   (rota-48): "the rule is a red test whose run never reaches an assertion of
   the surface's result" (observed: stack frame 304). Commit a3ce3f01,
   2026-10-23 18:08: "A raise inside the project's code, or an assertion, is
   admitted" (observed: the commit message). Rota workflow. The run fires only
   when the batch has a worktree and a `head_commit` (observed:
   `_arrange_run_refusal`, the guard before `_encode_run`). The build meets
   frame 304's own condition: an arrange fault is refused, an assertion is
   admitted (observed: the code and the commit).
4. `head_commit` is "last commit the DB has a receipt for" (observed: the
   `batches` schema). So the run happens exactly when a Developer commit
   exists, which is the case where the charter's condition fails (reasoned).
5. On night 166 the order was code first. s195 (batch_start) and s197
   committed the docstring at a0295dff before s198 woke on
   `tick:tests_missing` (observed: `tool_calls` s195 seq 12, s197 seq 6;
   `sessions` s198). s198 stored the three tests at seq 31 to 33, and each
   encode returned `{"id": ...}` with no note (observed: s198 turn 7 `user`
   text). The run at encode failed at `assert "a/b/c.txt" in result`, and the
   frame 304 rule admits that (reasoned: the head and the worktree existed,
   and an `AssertionError` gives no arrange fault).
6. The first stored run is `do:harness` (observed: `predicates.py` 883: a
   test with no run at the head commit is owed one). Attempt 2 at a0295dff
   gave 3 fails (observed: `test_run_journal` seq 221 to 223).
7. What reaches the Tester when the stored run is red: nothing. The red wakes
   the Developer only, by `tests_failing`, `wakes="developer"` (observed:
   `predicates.py` 949). The Tester sees the run output only when a challenge
   wakes it. s200's prompt held "[last run of tst_c1_format_filename_example:
   failed]" and `AssertionError: assert 'a/b/c.txt' in 'c.txt'` (observed:
   s200 turn 1).
8. The criterion text was in s198's prompt, and the seat wrote a test that
   contradicts it (observed: night166-read W-A, step 6). That is cause 5 at
   the Tester by the wall guide. The fact that would correct it, the run's
   `AssertionError`, existed at encode and the door dropped it (reasoned).

Kind: **a gap no design covered.** Frame 304 is a finished design for its own
narrower rule. No design names a red assertion on a head that already holds
the Developer's code. Frame 143 (a test asserts a default the function does
not have) met the same family and routed it to a surface push, with no run
result (observed: stack frame 143, the status of 2026-10-18 12:34 and the
residue rows of 2026-10-24). Frame 321 does not touch this mechanism: it stops
a wrong prints refusal, and night 166's tests were return-value tests that it
rightly admitted (observed: stack frame 321). Frame 201 is the Critic's site
and does not touch this door.

## Mechanism 2: the quote check of `msg.challenge_tester`

The chain:

1. The design: "`msg.challenge_tester` carries evidence ... the challenge must
   **quote** -- not paraphrase -- a span of that criterion's text and a span of
   the test's body". Its condition: "a session that must read both rows before
   challenging has, by then, done the reading that would show it the test is
   right" (observed: `DECISIONS.md` 1270 to 1282).
2. The ruling: "Ruled and built, 2026-08-26. The principal's whole ruling:
   'why is this not obvious?'", built as "a contiguous span of the disputed
   row, verbatim, whitespace-normalised" (ruled: Roman, 2026-08-26,
   `DECISIONS.md` 1290 to 1297). Rota workflow.
3. The build: 395535da, 2026-08-27, added `_quotes_span`: "A contiguous span
   of the source appears verbatim in the message ... Twelve characters is
   enough that matching by accident stops happening" (observed: `sandbox.py`
   940 to 951). The predicate is true when any 12-character window of the row
   is inside the message. The design asks the reverse: the quote is inside
   the row (reasoned).
4. 4b85e40b, 2026-09-14, added the per-side loop. Each of the criterion and
   the test must be quoted, the test side on its code with comments removed
   (observed: the commit message; `sandbox.py` 1368 to 1405). Each side is
   checked against the whole joined text. `_challenge_admitted` and the binder
   join the quotes with " ... " (observed: `sandbox.py` 5057 and 2100). So one
   side's match can come from the other side's quote (reasoned).
5. The door checks against the live row: `SELECT text FROM criteria WHERE id
   = ?` over `_QUOTABLE` (observed: `sandbox.py` 923 and 1233 to 1241). It
   reads no older version. `criteria` holds one text per id, with a version
   number (observed: the schema).
6. On night 166, m82 and m88 sent "When shorten=True, format_filename strips
   the directory prefix from the path. ... assert "a/b/c.txt" in result". The
   live c_1 text was v2, respecified by s194 before s198 (observed:
   `tool_calls` s194 seq 9 and 12; `criteria`). `_quotes_span` on the stored
   rows: the criterion side passes on "When shorten", the test side passes on
   " format_file", and the whole criterion quote is not in the live text
   (observed: a run of `_quotes_span` on the night's rows, this read).
7. The old text came from the Developer's prompt. The runner's block "[the
   principal contested these criteria]" shows "c_1_format_filename_example:
   He contested this text: When shorten=True, format_filename strips the
   directory prefix from the path." (observed: s199 and s208 turn 1 `user`;
   `runner.py` 764; added by 7a2cb843, 2026-10-15).
8. No door reads the named test's latest run. m83 (s201) and m88 (s208) named
   tst_c1 while its run at a0295dff was pass (observed: `test_run_journal`
   seq 262 and 344). The failing-tests hint at about line 1300 reads the runs
   only when a side is missing (observed: `sandbox.py`).

Kind: **a departure from the design.** The ruling asked for a verbatim span of
the row. The build admits a 12-character overlap, and the overlap can come
from the other side's quote. The design's condition, that the reading is paid
before the challenge, fails when a contested old text shares a prefix with the
live text (reasoned). Cause 8 by the wall guide: the predicate is wider than
its fact.

## Mechanism 3: the Developer's route on a red test

The brief and the doors:

- `tests_failing.md` lines 24 to 25: if the test asserts what its criterion
  asks, fix the code. Lines 27 to 35: "No -- then stop.
  `msg.challenge_tester(refs=[criterion_id, test_id], ...)` ... Copy the
  criterion's words verbatim ... Then change nothing." From 8d908e56,
  2026-08-10. The quote as one code line from 3b92f9ef, 2026-10-02. The
  reason form from ba2ddf5e, 2026-10-12 (observed: `git log -S`).
- Lines 46 to 50: escalate only "when two real changes have not moved the
  assertion". From 627fb593, 2026-08-24 (observed: `git log -S`).
- The brief says nothing about one test per session. The door does: "you have
  already sent challenge to tester; saying it again with different refs is a
  second answer to one question" (observed: `sandbox.py` 4026 to 4031; from
  b41626d1, 2026-08-14, "`question` means one thing"). The tester branch of
  `_challenge_evidence` reads `crit[0]` and `test[0]` only, so one message
  carries one pair (observed: `sandbox.py` 1243 to 1405).
- The Tester woken by a challenge rewrites the challenged test only (observed:
  s200, s202, s205 and s212 each sent one `tests.encode`).

The Developer sessions on bg_3: 9. Two came before the tests: s195
(batch_start, wrote and committed the docstring) and s197 (answer, committed).
Seven came after:

| Session | Wake | What it did | Brief followed |
|---|---|---|---|
| s199 | tests_failing, attempt 2 | m82 on c_1 and tst_c1 (red), quoting c_1's contested old text | route yes, quote no |
| s201 | tests_failing, attempt 3 | m83 on tst_c1, green since attempt 3, live text | route yes, target no |
| s203 | tests_failing, attempt 4 | m84 escalate with no code change, then m85 on tst_c2 (red), live text | m84 breaks lines 46 to 50; m85 yes |
| s207 | answer to m87 | read only, no call | yes (`answer.md`) |
| s208 | tests_failing, attempt 5 | m88 on tst_c1 (green), old text; two more refused by the one-send door | route yes, target and quote no |
| s210 | answer to m89 | `code.commit` "Test passed; no changes needed." | yes |
| s211 | tests_failing, attempt 5 | m90 on tst_c3 (red), live text; two repeats refused | yes |

(observed: `sessions`, `tool_calls`, `messages`, `test_run_journal`, and the
send results in each session's `user` text.)

Count: 5 of 5 ticks took the challenge route, which the brief gives for a
wrong test. 3 of 5 named a red test, 3 of 5 quoted the live text, and 2 of 5
did both (m85, m90). No session changed the code after s197, which was right,
because the code was right from 19:37. The Tester rewrote 4 times. s202
rewrote tst_c1 while it was green, and s209 refused m88, rightly. The red
counts were 3, 2, 2, 1, 0 over attempts 2 to 6 (observed: `test_run_journal`).

Kind: **a gap no design covered.** The one-send door was built for a question
and applies to every verb. No design names a batch where several tests are
wrong in one way. Three wrong tests then cost at least three Developer ticks
and three Tester wakes (reasoned). The escalate m84 cost s204 and s206, one
Architect and one Vision Keeper session (observed: `sessions`).

## The repairs

1. **A red assertion at encode becomes a note to the Tester.** File
   `rota/roles/api.py`, `_arrange_run_refusal` (17021 to about 17165). Where
   `verdict == "fail"` and `arrange_fault` gives None, append one note to
   `notes` with the failing assertion line and the `E` line of the run, and
   one step: "The batch's head has a commit. If the criterion's words give
   this value, this test is wrong: encode it again." The note channel exists
   (observed: `api.py` 10512 to 10547 returns `note`). The door does not
   refuse, because the code at the head can be wrong (reasoned). Size: about
   15 lines and one test file. Red test: s198 turn 7 (seq 31 to 33). By
   cause 5, replay s198's turn with the note before the night. Price: 1 cycle
   to build, 1 replay.
2. **The challenge quote is checked per side, as the ruling wrote it.** File
   `rota/core/sandbox.py`. Keep the quotes as a list through
   `_challenge_admitted` (5046 to 5060) and the binder call (3404). In the
   per-side loop (1368 to 1405), require each quote, whitespace-normalised, to
   be inside its own row: the criterion quote inside the live criterion text,
   the test quote inside the test's code. Keep the sibling-criterion escape
   and frame 304's raising-line admission. Size: about 25 lines. Red test:
   m88. A model quote that passed on 12 characters is refused after this, so
   some Developer challenge cassettes may go stale (reasoned).
3. **A Developer challenge on a test that is green at the head is refused.**
   Same function, after the batch check (about line 1329). If the named
   test's latest run at `head_commit` is pass, refuse and name the failing
   tests with the query at about line 1300. Size: about 10 lines. Red tests:
   m83 and m88. Build repairs 2 and 3 as one pass: 2 cycles on Opus and a
   review, by the rule of 2026-10-11 05:51.
4. **One test per session: measure first, do not build now.** Repairs 1 to 3
   remove the night's case at its source (reasoned). The frame's third
   condition, Developer ticks on a test the Tester later rewrites, from 5 of 5
   toward 0, measures what remains. If it stays, the cheap form is a runner
   line in the Tester's challenge wake that names the batch's other tests that
   fail at the head on the same assertion, about 20 lines. A challenge that
   carries several pairs changes the verb's arguments in the graph, and the
   record says that change needs a ruling (observed: `DECISIONS.md` 1286,
   "Blocked on: a ruling, because it changes a verb's arguments").

Composition question for Roman: none for repairs 1 to 3. Repair 1 shows the
Tester a run of its test on the Developer's head, against the charter line "you
never see it". The challenge wake already shows the same output with the value
(observed: s200 turn 1), so the repair moves an existing fact one hop earlier
(reasoned). Only the multi-pair form of repair 4 needs his ruling, and this read
does not recommend it now.
