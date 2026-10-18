# Night 157's read

Rota workflow, read by the meta workflow. Night 157 ran cold from
`C:/Users/roman/rota_night157` at d2e85f79, 16:40 to 18:55 on 2026-10-18,
on `D:/repos/_AI/sample_repos/clickI`, with the agent principal on Opus.
Records: `.rota/clickI_night157.db` (opened read-only), `.rota/night157.log`,
`.rota/night157_report.txt`, `.rota/night157_truth.txt`, the lines of
`.rota/clickI.principal.jsonl` with a clock at or after 2026-10-18T16:40,
and the two batch worktrees (git read-only). Read on 2026-10-18 by one agent
on Opus with three extract agents on Opus. Their extracts are in the
scratchpad `n157/` directory: `a_frame298.md`, `b_walls.md`, `c_frames.md`.
The synthesising agent checked the Critic refusal (s324 turn 2), the encode
refusal (s258 turn 3) and s175's calls against the database.

**The result.** No item merged. The request line killed no batch, against 2
of 3 on night 156, so frame 298's route held. Both batches died later, at the
evidence step: bg_1 on its tests and a regression of its own code, bg_2 at
review, where the Critic could not name the line for a correct change
(reasoned: sections 1 and 2).

## 0. The night in numbers

| Measure | Value |
|---|---|
| Phases | onboarding (107 steps, 3 asks), walk 1 (14 steps, 3 asks, quiet), walk 2 (186 steps, 17 asks, quiet), walk 3 (122 steps, 13 asks, quiet) |
| Steps, asks | 429 steps, 36 asks (night 156: 409 steps, 38 asks) |
| Batches | 2: bg_1 `default_on_eof` deferred at 0779d02e with 3 commits and 4 tests failing; bg_2 `show_python` running at 87156816 with 4 commits and 1 test failing |
| Merges | 0. No "rota: deliver" commit on any ref (observed: `.rota/night157_truth.txt`) |
| Sessions | 363 sessions, 1717 turns; Liaison 103, Vision Keeper 84, Terminologist 46, Developer 43, Architect 39, Tester 30, Critic 18 |
| Batch sessions | bg_1 54, bg_2 38, no batch 271 (39 of them onboarding reconcile) |
| Principal | 33 calls on Opus (3, 17 and 13 by walk), 4 replayed in onboarding, 3.22 dollars at list price |
| Quarantines | 4 pages: constraint_zero (s1), bg_1 twice (s188, s196), bg_2 (s327) |
| CYCLE lines | 3: Liaison converse (walk 1), Developer `tests_failing` attempt 9 on bg_1 (walk 2), Critic `review` on bg_2 (walk 3) |
| Made up | 71 turns in 36 sessions (Developer 11, Vision Keeper 11), 1 landed commit after an invention, 5383e172 (s140) |
| Repeats | "15 wakes repeated, 51 sessions, 36 of them repeats" |
| Window | "dropped to fit the window" 187 turns in 30 sessions; dangling pointers 86 turns in 18 sessions (s305 13, s309 10, s344 10) |
| After the end line | 215 turns in 84 sessions hold "Your work for this session is complete" |
| End lines | "Stuck: bg_1 is parked." and "Stuck: the code is written, but 1 test is still failing". "Rota itself failed 5 times this run." |

(observed: `.rota/night157.log`, `.rota/night157_report.txt`, `sessions`,
2026-10-18.)

## 1. The held frames

**Frame 298, the guess line. Validating: the route holds, and the rewrite
reaches no page.** One more batch on a later night completes its "next 3"
(reasoned: the ends-when counts batches).

- **The lookup line left the pages.** Each request page shows "The team's
  guess at the code this touches" as line 2, and the closing line says "To
  correct the code it touches, name line 2" (observed: the walk 1 end page
  in the log, the pages in the jsonl).
- **M0: 7 of 8**, as section 12 prints. The 8 sign-off pages are m2, m22,
  m36, m102, m110, m119, m153 and m162. m2 is the onboarding page with
  description items only, so no guess is due. m119 shows bg_1's batch plan,
  not a guess row, so a strict count of guess lines is 6 of 8. m119 and m162
  re-submit items already shown, so the pages of a new item are 5 of 5 with a
  guess line (observed: extract A section 1). All three readings meet the
  expectation of 3 of 4.
- **Corrections of the guess line: 5 rulings, 4 rewrites, 0 shown to him.**
  The Architect rewrote the row at m22 (s116), m36 (s126), m102 (s217) and
  m110 (s229), and each rewrite holds the files he named (observed:
  `touch_guesses` rows 4 to 28). No later page showed a rewrite. echo_json
  was parked. default_on_eof got a batch plan at m45 that named default-map
  tests in `tests/test_defaults.py`, and he gave the same correction again on
  line 5. bg_1_item took a new item version, and s223 wrote a fresh guess
  with `ruling_id` empty that dropped his m104 correction (observed: extract A
  section 2). So the route ends in a row he never reads (reasoned).
- **Line-1 rulings: 2 landed, 1 refused, 0 batches died** (night 156: 2 of 3
  batches abandoned). The m22 revise of echo_json and the m102 contest of
  bg_1_item rest on his own line-1 words: "Line 1 names the wrong change" and
  "Line 1 describes Click as a whole rather than my change". The frame-298
  cue refused the Liaison's revise at m45 (s136): "That code is line 5, the
  change's plan. Rule line 5 contest with the words, and approve line 1." The
  re-ruling approved line 1. The log holds no `do:cancel` and no
  "abandoned" (observed: extract A section 3, the log).
- **The hand list of 6, classed by hand** (the classes of
  `plans/frame298-count.md` section 1):

| Row | Page | Key | Class | Where the files words landed |
|---|---|---|---|---|
| r_fb0e73c536 | m22 | echo_json | (c) | the guess line, in the same reply |
| r_fb0e73c536 | m22 | guess:echo_json | (c) | the guess line |
| r_05354953f9 | m36 | guess:default_on_eof | (a) | the guess line, request approved |
| r_63b6dd3298 | m102 | guess:bg_1_item | (c) | the guess line |
| r_222662ce1b | m110 | guess:bg_1_item | (a) | the guess line |
| r_222662ce1b | m110 | guess:default_on_eof (the report keys it `bg_1`) | (d) | a misruling: his words endorse line 4, and the Liaison contested it |

  **M3: 0 of 5** files corrections landed on a request line and wrote
  `contested`. The five are the files halves of m22, m36, m102 and m110, and
  m45's line 5. The expectation is 1 in 5 or fewer, from 19 of 19 (observed:
  extract A section 4). **M4: 0** batches cancelled after a files
  correction. The rewrite took his words each time, but he never saw it, so
  his acceptance is not countable (reasoned). The two (c) replies kept their
  files words on the guess line, so frame 299's sign did not show on this
  night: 0 of 2 (reasoned: the per_item rows).
- **What section 12 could not count, and why.** M1 and M2 read 0 of 0,
  because both need a merged item with a git truth, and no item merged. M3
  and M4 need a hand reading by design 5.3, so the instrument lists rows and
  cannot class them. The list also keys one row as `bg_1` where `per_item`
  holds `guess:default_on_eof`, from the relay's refs (reasoned, the
  instrument code not read).
- **Residue for the frame.** The show_python guess names
  `src/click/options.py` and `tests/test_version_option.py`. Neither file
  exists in the repository, and the change touched `src/click/decorators.py`
  (observed: extract A section 1, `touch_strays`). The agent principal
  approved that guess at m153, m162, m205 and m210. The guess sessions record
  `mode='normal'` with `wake_kind='tick:guess'`, where the design names mode
  `guess` (observed: s104, s121, s212, s223, s273, s274). The design reads
  the cassette key by mode, so this needs a check before the next night
  (reasoned). `touch_guesses.ruling_id` holds the reply id (m28, m38, m104,
  m112), not the ruling id the design names (observed).

**Frame 297, the discard and the ledger door. Not in this night; the
baseline is recorded.**

- Team notes on a page that cite lines no commit holds: **0 of 3**. s158's
  two notes on m134 describe code that 5383e17 holds, and the Critic's note
  on m139 quotes committed signature lines (observed: extract C section 1).
- Sessions that inherited another session's uncommitted write: **5, all in
  bg_1**. s193 wrote `src/click/termui.py`, removed
  `echo(_("Error: invalid input"), err=err)` and `continue`, and committed
  nothing. s194, s195 and s264 got the write in turn 1 as "not committed".
  s203 and s243 had their commits refused for that write. The worktree still
  holds it: `M src/click/termui.py` (observed: extract C, `git status`).
- Ledger notes on a path with an open dropped note: **0 landed, 6 refused, 3
  became faults** (s194, s195, s201, s264, s309). The refusals are
  "kind='assumption' is no word this mode offers" and a missing `kind`
  (observed: extract C section 1 (c)). The bg_1 dropped note is still open.
- These five sessions are frame 297's exact site: the discard at s193's end
  would have freed bg_1 for its last five Developer wakes (reasoned).

**Frames 283 and 140, the noted-write door. Right to fire; the lock that
follows belongs to frame 297.** 13 refused commits in 6 sessions (s193 1,
s194 3, s195 3, s203 1, s243 2, s264 3), all for s193's one removal
(observed: extract C section 2). Night 156 had 33 in 10 sessions. Commits
that landed a removal of a base statement: **0 of 7**. Batches whose first
red project test follows an unnoted removal: **0 of 2**. bg_1's first red
inherited tests follow 0779d02 (s175), which changed a base statement and
removed none: `elif value in ("n", "no"):` became
`elif value in ("n", "no") or show_default:` (observed: `git diff` in bg_1).
The door reads removals only, so a changed condition is outside it, and the
frame's cause did not show (reasoned). The residue fix ee166261: **0 rows**.
No ledger row holds a path in `about_ref`, because every such call was
refused or became a fault (observed). It stays unmeasured.

**Frame 296, the revise-on-note text. 0, night 2 of 3.** No `revise` on
line 1 landed with no word of his on the request. The one wordless try,
s136 at m45, was refused by frame 298's cue (observed: extract A section 6).

**Frame 143, a literal version. 0 of 3 stored tests, from 3 of 8.** The
three bg_2 batch tests use `sys.version_info` or no version (observed:
`tests`). Three Tester encodes still wrote a literal, and no turn-1 prompt
held it: s311 "3.10.0" (refused by the constant door), s318 "3.10.5" in a
comment, s363 "3.10.5" (refused for its import first). The count moved on a
different batch from night 156's, so it does not prove the frame
(reasoned). The seat writes the literal from no record, which is step 7 of
the guide: an interview of s311 turn 1 is still the next step.

**Frame 258, a contest on a line no sentence names. 0, night 2 of 3.** 0
line-1 contests refused, and 0 of 9 batch-page replies (m45, m82, m87, m134,
m139, m170, m183, m205, m210) with line 1 contested (observed: `rulings`).

**Frame 220, the fence baseline: 0 of 0.** No `code.write` refusal names the
base commit (observed: extract C section 4).

**Frame 286, the unnamed-definition door: 0 of 0 refused.** The door now
permits the write and asks the Architect. `touch_strays` holds 3 bg_2 rows
on `src/click/decorators.py`. The Architect s310 judged 1 of 3 (90e8e59
"foreseen"). 30b4025 and 6eea444 stay `open` (observed).

**Frame 282, the range after "and": 0 of 0.** No reply carried a range after
"and". The 9 refused line-contest calls read (s109, s255, s277, s353) were
right by his words (observed).

**Frame 290, the encode offer: 0 of 21** `tests.triage` calls refused for an
offered verdict. The only triage refusals are 6 repeats (observed).

## 2. Every wall the night met

**The night merged nothing in 363 sessions because both batches died at the
evidence step, and the request line killed neither** (reasoned: sections 1
and 2). Night 156 merged the same confirm request in 50 steps, because its
tests and code came right first time. On this night, s175 wrote a
regression into `confirm()`, the new tests were wrong, and the doors and a
hop kept his correct test diagnosis from landing. bg_2's code was right at
8715681, but the Critic could not emit a pass, and the test that replaced
the vacuous one was itself wrong. The batch that cost the most is bg_1: 54
sessions and about 11 asks (observed: extract B section 3).

Ranked by cost. Sessions overlap between W1 and W2 (reasoned).

| # | Wall and sign | Sessions | Asks | Place by section 4 |
|---|---|---|---|---|
| W1 | **bg_1's test loop.** (1) s175 rewrote `confirm()` whole and added `or show_default`, so two inherited test groups fail (`test_confirm.py` prompts and repeat, `test_termui.py` six `[Y/n]` cases). (2) The two new tests never pass `default=True` and never print the result. (3) His diagnosis at m134 was right for the tests. s257 pasted his reply into the cr_2 text, and he asked at m139 to take it out. (4) s258 and s266 drafted the right test under `CliRunner().invoke`. The encode door refused 6 encodes with "this test calls confirm() under pytest, where stdin is captured", then locked `tests.encode` for the session. (5) s193's uncommitted write locked commits for s194 to s264, 13 refusals. (6) No page named the inherited failures as a fault of the code, so his replies named the tests only | 54 | about 11 (m77, m82, m87, m96, m102, m110, m119, m127, m134, m139 twice) | Several causes, so several frames. (4) is **new, cause 8**: the predicate misses a `confirm()` call in a helper that a `@click.command()` calls, and its text offers the shape the test already has (cause 9). With s258 turn 3 as the red test, 2 cycles. (3) is cause 1 at the Terminologist's `criteria.respecify`: new frame, 1 to 2 cycles, after a probe of s257. (5) is frame 297, built. (1) is cause 5 or a span write of the whole function: interview of s175 turn 23, 1 cycle, before any brief line. (6) is cause 11: a candidate for a new frame, not priced |
| W2 | **bg_1_item, a request row from a textless propose.** Architect s204 sent propose m94 with refs `["bg_1"]` and no text. Vision Keeper s205 was refused the id `bg_1` ("already a row of batches"), so it asserted `bg_1_item`, an `in_scope` request with a 779-character description of Click. Line 1 of m102 and m110 was that row. s233 later made it a description, and its confirm sentences then reached the show_python pages | 37 | 5 (m102, m110, m153, m162, m167) | **New, cause 15**: a conclusion crosses from the Architect to the Vision Keeper with no words. Cause 11 for the result: a team-written row under "You asked". Fix: the propose door refuses an empty body, or the assert of a request item needs a principal message as its cause. 2 cycles, with s204's call and s205 turn 6 as the red tests |
| W3 | **bg_2's review.** All three Critics (s324, s325, s326) sent `verdicts.emit(result='pass')` and cited the 3-line `:param show_python:` docstring. The door refused: "a pass names one added line per criterion. Copy the one line of the [diff] block". The diff held `+        message = message + f" (Python {python_version})"` and `+    show_python: bool = False,`. CYCLE, quarantine s327. After it, s331 and s334 rewrote the version test without `version=`, and it fails with `RuntimeError: 'test_version_option_output' is not installed`. He read "output is empty" and blamed the code at m205 and m210 | 17 (3 Critic, 14 after the quarantine) | 5 (m183, m195, m201, m205, m210) | The Critic half is **frame 201**, open, its third night of this sign (nights 144, 152, 157). Cause 5 with cause 9: the refusal names no candidate `+` line. 1 cycle. The test half is **new, cause 2 or 11**: the page shows "output is empty" in place of the RuntimeError, then cause 5 at the Tester. 1 to 2 cycles. Frame 288 is near, but its door reads imports, not a runtime package lookup |
| W4 | The guess rewrites reach no page: a park, a batch plan and a new item version each replace the rewrite | 4 (s116, s126, s217, s229) | 2 repeated corrections (m45 line 5, m110 line 2) | Frame 298 residue, cause 12: the guess and the batch plan are two records of one fact, and no rule carries the correction from one to the other. A case on frame 298 or a follow-up frame, 1 to 2 cycles |
| W5 | The show_python guess and bg_2's annotate name `src/click/options.py`, which does not exist; the change touched `decorators.py`; s310 judged strays | 3 (s273, s274, s310) | 0 (approved 4 times) | **New, cause 8**: `batches.guess` and `batches.annotate` admit a path that is not in `code_index`. 1 cycle, cheap |
| W6 | A vacuous pass: s318's first version test invoked `--show-python`, an option that does not exist, and the usage error holds "python" | inside W3 | 0 | Cause 8, near frame 269 (encode doors that admit a test that cannot fail). A case on frame 269 |
| W7 | Replies that did not reach the team: m22 (s107, s108 refused "rule line 1 as the words say", then no ruling), m139, m210 | about 6 | 3 | Not read to a cause. m22 also drove the walk 1 CYCLE. Near frame 289. A read of s107 turn 2, 1 cycle |
| W8 | The agent principal said "I'm on the second one now" at m22 while the page showed echo_json, so echo_json was revised into the confirm request and stays `contested` | 2 (s112, s116) | 1 | Not placed. Possibly cause 13, the agent principal's script, before any rota fix (reasoned). Read the principal's brief first |
| W9 | Turns after "Your work for this session is complete": 215 turns in 84 sessions | 84 | 0 | Not read. A known line of the report |
| W10 | Window drops (187 turns, 30 sessions) and dangling pointers (86 turns, 18 sessions) | 30 and 18 | 0 | Frames 139 and 208 hold the signs. Cases added, not read |
| W11 | Made up: 71 turns in 36 sessions, 1 landed commit 5383e172 (s140) | 36 | 0 | The known "made up" line, cause 7. Not read on this night |
| W12 | Repeats: 15 wakes, 36 repeat sessions | 36 | 0 | Not read |
| W13 | constraint_zero quarantine at s1 in onboarding | 1 | 0 | Not placed. Second night with the same page (reasoned: night 156 section 0) |

(observed: extracts A, B and C, `turns`, `tool_calls`, `test_runs`, the
worktrees, 2026-10-18.)

## 3. The request line

**The request line is no longer where batches die** (observed: 0 of 2
batches abandoned on a line-1 ruling, 0 `do:cancel`). His files corrections
landed on the guess line 5 of 5 times, and the item kept its approval each
time. Two costs stay on the line:

1. **The rewrite does not come back to him.** He made the same files
   correction twice for default_on_eof (m36, then m45 on line 5) and twice
   for bg_1_item (m102, m110), because the next page showed another row
   (section 1, W4).
2. **A row he did not write still reaches line 1.** bg_1_item came from the
   team (W2), and he spent m102 and m110 on it. The page labels the guess as
   the team's, but line 1 has no such label, and line 1 is the place a team
   row does the most harm (reasoned).

## 4. The agent principal's cost

33 calls on Opus: walk 1 3, walk 2 17, walk 3 13, with 4 onboarding calls
replayed from the cassette (observed: the log's `principal:` lines). The
list-price figures sum to 3.22 dollars: 0.27, 1.69 and 1.26 (observed: the
log). The jsonl holds 37 `call` rows with no token count. Their pages and
replies sum to 67,697 characters, about 17k tokens at four characters a
token, and 160.6 s of call time (reasoned: an estimate of the visible text,
not the billed context). Asks per merge: 33 asks of the walks for 0 merges,
against 35 for 1 on night 156.

## 5. What the next night should be held on

**Hold the next night on the evidence step: frames 297 and 201, and the new
encode-door frame of W1** (reasoned: section 2). Frame 298 moved the deaths
off the request line, and both batches then died where the tests and the
review decide. In order:

1. **Frame 297** is built at 5eec792b with pass 6 open. Its discard frees the
   five bg_1 sessions that s193's write locked. Land it before the night.
2. **Frame 201**, 1 cycle: the lines refusal names the `+` lines of the diff
   that can meet each criterion. This sign stopped the only correct code of
   the night, and it is the third night of the sign.
3. **The W1 encode door**, 2 cycles: the visible_prompt_func predicate reads
   a `confirm()` call inside a helper that the command calls, with s258 turn
   3 as the red test.
4. **W5**, 1 cycle: the guess and the annotate refuse a path not in the code
   index. M1 and M2 are worth little while the guess can name files that do
   not exist.
5. **W2**, 2 cycles: a textless propose writes no request item.

The interviews of s175 (W1 part 1) and s311 (frame 143) cost one cycle each
and run beside the fixes. W4 waits on the holding session's choice: a case
on frame 298 or a follow-up frame. Night 158 then measures frame 297's
ratio, frame 298's third batch, frames 296 and 258 on their night 3, and
frame 201's first night. Frames 220, 286, 282 and 290 got 0 of 0 again,
because neither batch reached their sites (reasoned).

## Usage

The three extract agents ran on Opus, each with a cap of 60k tokens, and
each went past it: A 109.8k, B 116.4k, C 127.5k by the harness counter
(observed: the harness usage lines). Extract B did not read the turns of its
walls 5 to 11, so W7, W9 to W12 carry no read cause. This page cites those
rows as not read.
