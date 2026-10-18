# Night 156's read

Rota workflow, read by the meta workflow. Night 156 ran from
`C:/Users/roman/rota_night156` at db0c781d, 05:29 to 07:04 on 2026-10-18,
cold, with the agent principal on Opus. Records: `.rota/clickI_night156.db`
(opened read-only), `.rota/night156.log`, `.rota/night156.err`, and the
lines of `.rota/clickI.principal.jsonl` at or after 2026-10-18T05:29.
Read on 2026-10-18 by one agent on Opus. The holding session's status lines
of 05:37, 06:09 and 06:59 on frames 258 and 283 were checked against the
database once. They stand, with one correction in section 1 (frame 258's
denominator).

## 0. The night in numbers

| Measure | Value |
|---|---|
| Phases | onboarding (107 steps, 3 asks), walk 1 (44 steps, 7 asks, quiet), walk 2 (50 steps, 5 asks, merged bg_1), walk 3 (208 steps, 23 asks, quiet) |
| Steps, asks | 409 steps, 38 asks |
| Batches | 3: bg_1 `confirm_default_on_eof` merged; bg_2 `version_option_show_python` abandoned at m125 with no head; bg_3 `version_option_show_python` abandoned at m192 at head 2a50023 |
| Heads, commits | 2 batches with a head; 3 product commits: bc1acb6 (bg_1), c3415a4 and 2a50023 (bg_3) |
| Merges | 1 (bg_1, 93d01c4 "rota: deliver bg_1") |
| Sessions | 352 sessions, 1682 turns; Developer 32, Tester 19, Liaison 114, Vision Keeper 86, Terminologist 50, Architect 30, Critic 18, Researcher 3 |
| Principal | 36 calls on Opus (7, 5 and 24 by walk), 4 replayed in onboarding |
| Repeats | "12 wakes repeated, 35 sessions, 23 of them repeats" |
| Made up | 115 turns in 43 sessions (Developer 14, Vision Keeper 10) |
| Quarantines | 6 pages: constraint_zero (s1), contested echo_json (s128), batch_start bg_2 (s217), tests_failing bg_3 (s288, s316), contested version_option_show_python (s349) |
| CYCLE lines | 0 |
| End line | "Stuck. The team gave up on: contested for echo_json, contested for version_option_show_python." and "Rota itself failed 4 times this run." |

(observed: `.rota/night156.log`, `batches`, `sessions`, `tick_attempts` and
the bg_3 worktree's `git log`, 2026-10-18.)

## 1. The held frames

**Frame 258, a contest lands on a line no sentence names.** Page replies
with a batch line whose line 1 is contested: **0 of 7** (observed:
`rulings` and the session prompts). The seven replies are m67 (bg_1, walk
2), m101, m105 (lost), m106 (bg_2), m146, m166 and m187 (bg_3). The status
line of 06:59 said "0 of 1". It counted m101 alone and missed walk 2's m67
and bg_3's three touch pages (observed: the `lines` maps of s157, s260, s289
and s317). The right contests were kept: m67 kept `cr_7` and `bg_1`
contested, m146 kept `bg_3` contested. The door fired once on line 1 of a
batch page, s157 call 1 at m67, and it was right: the words fault lines 6
and 7 and not the request.

The `rulings.rule` calls on line 1 of a request page over the night:

| Reply | Session | Ruling on line 1 | Result | Right by his words |
|---|---|---|---|---|
| m23 | s106, s107 | contest | 4 refused (line 2 not named), 2 repeats dropped, reply lost | refusals right |
| m24 | s108 | revise | 1 refused (revise on note line 3), then landed | right: "keep my request as written but change the code it points at" |
| m33 | s117, s118 | contest | 5 refused (lines 2 and 3 not on a 1-line page), s118's 4th landed | right by the words, meant as a correction |
| m41 | s129 | contest | 2 refused (line 2 not on the page), 3rd landed | right by the words, meant as a correction |
| m45 | s134 | approve | landed | his words asked for a rewrite of line 1 |
| m54, m83 | s142, s181 | later | landed | right |
| m67 | s157 | contest | refused by frame 258's door, then approve landed | refusal right |
| m125 | s239 | revise | landed on call 2 | **wrong**: no sentence names line 1 (section 3) |
| m192 | s322 | contest | call 1 refused (lines 5 to 8 and 10 unruled), call 2 landed | right by the words, meant as a correction |
| m201 | s333 | contest | 2 refused (lines 6, 7, 9 not named), 3rd landed | right by the words |
| m216 | s350 | contest | landed | right by the words |

Totals: 9 landed non-approve rulings on line 1 (5 contest, 2 revise, 2
later), 15 refused calls that carried a line-1 contest, and 1 of the 15
refused for line 1 itself (s157, right). Every refusal was right by his
words (observed: `tool_calls`, the runner's accounts, `receipts`). The one
wrong landing is m125's `revise`. Frame 258's door spares a `contest` and
does not read a `revise`, so m125 is residue for this frame with a second
cause, the door text of section 3 (reasoned: `rota/roles/api.py` 9705-9715).

**Frame 283 with 140, the noted-write door.** The commit door fired at
s214 and on 9 more Developer sessions: 33 refused commits in s214, s215,
s216, s274, s275, s295, s300, s301, s304 and s307 (observed: the runner's
accounts). Every fire held a removal out of a commit, and no commit landed
a statement removal: the two bg_3 commits change only an added block
(c3415a4) and blank lines (2a50023) (observed: `git diff` in the bg_3
worktree). Batches whose first red project test follows an unnoted removal:
**0 of 2** batches with a head (bg_1, bg_3), bg_2 never committed. The
recovery landed once: s295 wrote the trailing statements back and committed
2a50023 (observed: s295 seq 14). In bg_2 it never landed. One shape is
residue to read: s215 logged the removal of `echo(msg, color=ctx.color)` and
`ctx.exit()` as `l_8c98565350` at turn 6, and the door refused the commit
for those same two statements at turns 8 and 10 (observed: s215 turns 6 to
8). The note preceded the write that removed them. Whether the door reads
a note older than the write is not settled (reasoned; a probe of s215 turn
8 settles it). s214, s216 and s295 logged the removal with `kind='fault'`,
which writes a fault row that ends the session and is no note (observed:
`faults` f_e1ab020c98, f_2eadfa8dab, f_8d81399322).

**Frame 220, the fence baseline.** Developer writes refused by the fence for
a reach of the base commit: **0 of 0**. The fence fired only on the
Tester's `/dev/null` opens in s163 and s165, which are not a restore
(observed: `turns`).

**Frame 286, the unnamed-definition door.** Writes refused for the want of a
criterion: **0 of 0**. `touch_strays` holds 0 rows, so no row with `::`
and no Architect judgement on one (observed: `touch_strays`, `turns`).

**Frame 282, the range after "and".** Rulings that match his words line for
line and are refused: **0 of 0**. No reply carried a range after "and".
m112 "Lines 8 to 11", m118 "Lines 5 to 11" and m192 "Lines 2 to 4 ... Lines 9
and 11" read whole (observed: `rulings`).

**Frame 290, the encode offer.** Tester sends refused for a verdict a
previous door offered: **0 of 0** (observed: no `tests.triage` refusal of an
offered verdict in `turns`).

**Frame 143, a test asserts a value the criterion does not give.** Stored
tests: **3 of 8**, all of bg_3: `ver_opt_show_py_test`,
`ver_opt_show_py_env_test` and `ver_opt_show_py_format_test` assert
`endswith("Python 3.10.0")` where the criterion says `sys.version_info` at
runtime (observed: `tests`). The 3.10.0 came from no record. The first
Developer to write it was s214 in bg_2's docstring ("e.g., Python 3.10.0").
The first Tester to write it was s292, turn 1, and that prompt holds no
"3.1" string at all (observed: `turns` of s292, 12052 characters searched).
The seat had the criterion and wrote a literal: guide step 6 or 7, so an
interview of s292 turn 1 is the next step before any brief line (reasoned:
`plans/wall-guide.md` section 4).

**Frame 277 and frame 273, the constant door.** Admitted tests that cannot
fail: **0 of 8** stored tests (observed: `tests`). s292's
`assert "Python" not in result.output or result.output == "Python 3.10.0"`
never stored, because the file door refused its id.

**Frame 278, the Architect's finding about a test.** Developer sessions sent
to the code after an Architect finding on the test: not counted to a ratio.
The Developer challenged the Tester 16 times on bg_3's red tests and the
same-refs refusal appeared in s277, s293 and s302 (observed: the runner's
accounts). No Architect decision of the frame's shape was found in this
read (reasoned: not searched in full, cap).

**Frame 274, the inferred carrier.** Items of another request set contested
by a keypress: **0 of 18** contested notes of the confirm request on the
version pages m107 to m122. Their `about_ref` rows are criteria, tickets
and glossary rows, so the carrier did not fire. The relay s231 tried to set
`confirm_default_on_eof` contested twice, and the relay door refused it,
right (observed: `ledger`, s231's account).

## 2. Every wall the night met

Ranked by cost. Cost is sessions and asks, because the log gives steps per
walk only (reasoned).

| # | Wall and sign | Sessions | Asks | Place by section 4 |
|---|---|---|---|---|
| W1 | A correction of the request line ends the item. `revise` and `contest` on line 1 both write `contested`, `cancel` abandons the live batch, the Vision Keeper's contested wake appends his correction words to the request text, and the page's pointer moves with the new words. echo_json (walk 1, m24 to m44), bg_3 at m192, and m200 to m216 after it | about 145 (s105 to s136, s240 to s352) | 12 | New design frame. Cause 10 for the route (no ruling keeps the item schedulable), cause 1 for the hop (his correction becomes request text, s111, s121), cause 11 for the pointer line (a derived guess shown as his line). Escalate the route: law 9 says an amendment stops batches. Section 3 |
| W2 | bg_3's tests_failing loop: tests hard-coded 3.10.0; the surface-import door refused 14 encodes (s271 to s326); 29 span refusals and 8 parse refusals on `decorators.py`; 16 challenges; quarantined twice | about 60 (s263 to s320) | 3 (m165, m179, m186) | Frame 143 for 3.10.0 (interview first); frame 260 for the import door's prefix; the span refusals are frame 173's site, counted as residue |
| W3 | bg_2's batch start quarantine: s214's span write dropped `echo(`, the door held it, the seat repeated; s215 and s216 wrote their own tool results; the note of s215 did not satisfy the door | 3 Developer, about 10 in all | 2 (m104 twice, one lost) | Frame 283, right to fire, 1 residue (note before the write); the invented results are cause 7, the known "made up" line |
| W4 | m125: the revise-on-note door text names line 1 as the only revise target, and s239 moved its `revise` from note line 7 to line 1; bg_2 died | 1 | 0 (killed a batch) | **New, cause 9**: the refusal text points the seat wrong. Fix: name "contest it" alone, and offer line 1 only when the words name it. 2 cycles, with s239 turn 2 as the red test |
| W5 | m124: s242, a relay Developer with no batch, read s214's uncommitted write in the bg_2 worktree as existing code and logged `l_cab4458639` "already contains the show_python logic at lines 543-546"; the page showed it as a team note | 1 | 1 (m124) | **New, cause 14**: a tree with an uncommitted write after a quarantine. Fix: the quarantine resets the worktree to the head, or the note door refuses a claim about uncommitted lines. 2 to 3 cycles |
| W6 | The request page carried the merged confirm request's notes: m107 lines 9 and 10, m112 lines 8 to 11, m118 lines 5 to 11, m122 line 6 | about 12 | 4 | Frame 241's sign (the agenda puts another request's notes on a page). Case added |
| W7 | A seat read a right refusal and repeated it verbatim, so the reply was lost: s106 and s107 at m23, s218 and s219 at m105 | 4 | 2 (m22 again, m104 again) | Step 6 or 7: the fact was in the prompt; interview before any brief shape |
| W8 | On a 1-line page (m32, m40), s117, s118 and s129 ruled lines 2 and 3 from m24's earlier page: 7 refusals | 3 | 0 | Frame 272's sign (`recent_chat` carries line numbers of an earlier page). Case added |
| W9 | The contested quarantines: echo_json (s128, 3 attempts), version_option_show_python (s349) | inside W1 | inside W1 | Part of W1, not a wall of its own |
| W10 | constraint_zero quarantine at s1 in onboarding | 1 | 0 | Not placed. One page, no cost to a held frame (reasoned) |

(observed: `tool_calls`, `turns`, `tick_attempts`, `sessions`, the
principal jsonl, 2026-10-18.)

## 3. The request line

**A `revise` that rewrites line 1's text and keeps the item schedulable does
not exist today** (reasoned: the code at db0c781d). The sites:

- `rota/roles/principal.py` about line 2029, `land`: `"revise": "contested"`
  at the keypress, the same state as a contest.
- `rota/roles/api.py` about line 1906, `problem.set_approval`: the relay
  cannot undo it ("land wrote `contested`, and the contested wake carries
  the words. Leave it", s110 three times).
- `rota/core/predicates.py` 1503 to 1527, `cancel`: any live batch whose item
  is not `approved` is abandoned by the scheduler with no session.
- `rota/core/predicates.py` 291 to 306, `contested`: wakes the Vision Keeper,
  and `rota/core/runner.py` about 2322 carries his words to it as the
  replacement words (law 9).
- `rota/roles/principal.py` 1592 to 1621, `near_code`: the "code that names
  these words" line is computed from the item's text against symbol names.
  No row holds a pointer, so no ruling can move it.

The four deaths:

1. **echo_json, m24 and m33 (walk 1).** His words at m24: "On line 1, keep
   my request as written but change the code it points at: drop the
   terminal UI tests and the context tests, and point at the echo function
   in click's utils module and the echo tests." s108 landed `echo_json:
   revise`. The item went `contested`. s111 in the contested wake appended
   his correction to the request text. The next page, m32, showed line 1 as
   "... Drop the terminal UI tests and the context tests, and point at the
   echo function ..." with the pointer now `tests/test_options.py,
   tests/test_termui.py, tests/test_basic.py`, worse than before, because
   the new words "tests", "terminal" and "point" match more symbols. m33 and
   m41 contested line 1 again. s120 and s131 set it `contested`, and the
   contested tick quarantined at s128. His m45 approve could not revive it
   (observed: s108 to s134, the pages in the jsonl, `items`).
2. **bg_2, m125.** His words answered the m124 question about line 8: "As
   far as I know, that code doesn't do this ... please build the flag as new
   work." s239 ruled line 7 `revise`. The door refused: "line 7 is the
   team's note, not your request. revise rewrites a line of what the
   principal asked for: line 1, version_option_show_python. Revise the line
   the words are about." s239 moved `revise` to line 1, and it landed. `cancel`
   abandoned bg_2 (observed: s239 turns 1 and 2; log "abandoned bg_2"). Cause
   9. No word of his meant a change to line 1.
3. **bg_3, m192.** His words: "Line 1 also names the options and defaults
   test files, which have nothing to do with this change, so keep the work
   to version option and its tests in the basic tests file." The page m191
   showed line 1's pointer as `tests/test_options.py, tests/test_basic.py,
   tests/test_defaults.py`. s322 landed `contest` on line 1. `cancel`
   abandoned bg_3 at head 2a50023. The contested wake then put his test
   notes into the request text (item version 3), so m200 showed line 1 as
   "... turning the flag on to check that the message ends with ... The
   show_python option should be a normal keyword argument ...", and m200
   and m216 contested line 1 again: "it mixes in my notes about the tests"
   (observed: s322, the pages m191, m200 and m215, `items`).
4. **The pointer never moved** because no record holds it. `near_code`
   reads the item's text each time a page is built. His words corrected the
   pointer seven times (m22 twice, m32, m40, m44, m192, m215) and each
   correction could land only as a change of the request text, which moved
   the pointer by the words he added (reasoned: `near_code`; observed: the
   pages).

**The other request's lines, m107 to m122.** The four pages carried 18
notes of the confirm request (criteria `cr_1` to `cr_7`, ticket `tk_1`, the
`option` term). He contested them each time, and each contest landed. The
agenda put new ones on the next page (observed: `ledger`, `rulings`). This
is frame 241's sign.

**m124's line 8.** `l_cab4458639`, by the Developer s242 woken by a relay
with no batch: "The file already contains the show_python logic at lines
543-546; no write is needed." The lines were s214's uncommitted write in the
bg_2 worktree, which the batch-start quarantine left in place. The page m122
showed it as a team note, and he asked "where is that existing Python
version code from" (observed: `ledger`, s214's write result, the m122 page).
Wall W5.

## 4. The agent principal's cost

36 calls on Opus: walk 1 7, walk 2 5, walk 3 24. 4 onboarding calls were
replayed from the cassette (observed: the log's `principal:` lines and the
jsonl). Neither record holds a token count: the jsonl rows carry `page`,
`words`, `duration_ms` and a list-price figure only (observed: the row
keys). The pages and replies sum to 58,810 characters over the 36 calls,
about 15k tokens of page text at four characters a token, and 162.5 s of
call time (reasoned: an estimate of the visible text, not the billed
context). Asks per merge: 35 asks of the walks for 1 merge.

## 5. What the next night should be held on

Hold the next night on W1, the request-line correction, and fix the cheap
door text of W4 in the same sprint, because three of the night's four
deaths (echo_json, bg_2, bg_3) came through line 1, and the held frames got
data only from the batches that lived: bg_1 merged with no line-1
correction, and bg_3 lived 83 sessions before m192 (reasoned: sections 1 to
3). The design is one question for Roman first: law 9 makes an amendment
stop the batches, so a correction of the request's wording or of its code
pointer that keeps the batch needs a ruling, or a pointer row that the
principal can correct without amending the item (reasoned: cause 10's
"escalate" and cause 11). Before that fix, a night gives the held frames
data only when the principal does not correct line 1: frames 283, 140 and
143 got counts from bg_3's 60 sessions, and frames 220, 286, 282 and 290
got 0 of 0. The read recommends no night until W1's design lands, and the
W4 text fix, frame 258's `revise` residue and the s292 interview for frame
143 run in that window.
