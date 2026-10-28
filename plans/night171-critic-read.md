# Night 171: the Critic's review of bg_1 with no verdict, 2026-10-27

Read-only. Source: a backup copy of `.rota/clickI.db`, taken while the night
ran, and `.rota/night171_launch.log` lines 40 to 46. The copy is in the
scratchpad of session 6d9cf7e1 at `n171/clickI.db`.

## 0. The result

The pass door `_pass_lines_check` (rota/roles/api.py 14757, called by
`verdicts_emit` 14280) refused a pass whose substance was right. The
criterion c_1 asks for two branches, Roaming when `roaming=True` and Local
when `roaming=False`. No single added line of the diff meets both branches.
The door admits only one added line per criterion, or two parts of a wrapped
statement (`_LINE_PARTS_MAX = 2`, api.py 14399). The seat sent the
four-line `if roaming:` block, the honest evidence, and the door refused it.
The refusal says "Copy the one that does what the criterion says", and for
c_1 no such line exists. The only other route it offers is a fail. The seat
repeated the same call, and the runner ended each session on "repeated its
previous turn verbatim twice" (observed: turns s128 to s130).

The cause is the door's form rule against a compound criterion. It is not a
missing offer, and the seat's form is a secondary cause (reasoned).

## 1. The three attempts

Each attempt is one Critic session on `qwen3.5:9b`, wake
`critic|tick:review|bg_1`. Each made the same first five calls:
`code.read`, `criteria.load`, `tests.load`, then
`verdicts.claim_encodes('c_1', encodes=True)` and
`verdicts.claim_encodes('c_3', encodes=True)` (observed: tool_calls).

| Session | Call | The door's reply |
|---|---|---|
| s128, s129, s130 | `verdicts.emit(batch_id='bg_1', result='pass', reason='')`, no `lines=` | "a pass names, for each criterion, the added line of the diff that meets it, and c_1, c_3 have no line. Send verdicts.emit again with lines=..." |
| s128, s129, s130 | `emit` pass with `lines={'c_1': <8 lines>, 'c_3': <8 lines>}`: the two comment lines, the two `appdata_*` assignments, and the `if roaming:` / `else:` block | "the value for c_1 holds 8 lines, and a pass names one added line per criterion. Copy the one line of the [diff] block that meets c_1 ... The lines you sent hold these added lines: ... Copy the one that does what the criterion says." |
| s128 only | `emit` pass with `c_1` = the 4-line `if roaming: folder = appdata_roaming else: folder = appdata_local` | "the value for c_1 holds 4 lines, and a pass names one added line per criterion. ..." The same text, the same added-line list. |
| s128 | the 4-line call twice more, verbatim | the same refusal, then "repeated its previous turn verbatim twice; ended" |
| s129, s130 | the 8-line call twice more, verbatim | the same refusal, then the same end |

Each refusal ends with the fail route: "If no added line meets c_1, that is
a fail on it: `verdicts.claim_encodes('c_1', encodes=...)` first, as for any
fail" (observed: turns, the runner's account).

s129 and s130 are identical call for call. Their prompts differ from s128
only by one line, "This is attempt 2 of 3 on this wake ... Do something the
earlier attempt did not" (observed: a diff of turn 1). The seat runs at
temperature 0, so the retry note bought no new behaviour (observed:
sessions.pins_json, temperature 0.0).

## 2. Why no verdict landed

1. **The criterion.** c_1 at review time reads "If roaming=True, the
   returned path must be under ...\AppData\Roaming. If roaming=False, the
   returned path must be under ...\AppData\Local" (observed: the
   `[criteria.load]` block of s128 turn 1). The behaviour lives in four
   lines, not in one.
2. **The door.** `_pass_lines_check` refuses a value with more than
   `_LINE_PARTS_MAX` = 2 parts (api.py 14861 to 14907). The comment at
   14853 says a block "names nothing". For a one-branch criterion that rule
   is right. For c_1 it leaves no admissible pass. Any single line names
   one branch only.
3. **The refusal text.** It tells the seat to copy "the one" line that
   meets c_1. The listed lines hold no such line, so the instruction cannot
   be met by a correct pass (reasoned).
4. **The offer.** The refusal offers the fail route through `_offer`. It
   offers no pass route. A missing offer is not the cause, because the
   right pass has no form that the door admits (reasoned).
5. **The seat's form.** The 8-line value held two comment lines and the
   two assignments. The door was right to fire on that value. The 4-line
   value of s128 is the defensible evidence, and the door refused it too
   (observed). The seat never tried two lines, for example
   `folder = appdata_roaming` and `folder = appdata_local`. Whether the
   door admits those two as two parts is not tested here (doubt).
6. **The tests.** bg_1 ran 36 tests with 0 not passing before the review
   (observed: launch log line 39). The substance of the pass was right
   (reasoned: the diff implements both branches).

In the terms of `plans/wall-guide.md` line 863, the door fired where it was
wrong to fire on the 4-line value, which is cause 8. The text "Copy the one
that does what the criterion says" also points the seat wrong, which is
cause 9 (reasoned).

## 3. Where it places

- **Fact.** F37, "The added code lines that a pass names"
  (`plans/facts-2026-10-27.md` line 383). Its one reader is
  `_pass_lines_check`. The audit half b, section F37
  (`plans/rootfix-audit-2026-10-27-b.md` line 167), marks F37 FIXED,
  because each half has one reader. That verdict covers the reader count.
  It does not cover this shape: the one-line rule against a criterion whose
  behaviour spans several lines. No file of the facts, the audits, the wall
  guide or the night reads names this shape (observed: grep for "two
  branch", "both branches", "compound criterion", "holds N lines", "one
  added line per"). So the fact is F37, and the cause is new under it.
- **Not F25.** The refusal offers only calls the Critic's mode holds
  (reasoned: `verdicts.claim_encodes` is in the Critic's tool list, s128
  system prompt).
- **Frame 311.** "The Critic's `verdicts.emit` refuses a docstring line as
  meeting no criterion, while the criterion asks for the docstring"
  (stack.md 1961). Not this shape. bg_1's c_1 value is code, and no
  docstring rule fired. Its last status, 2026-10-24 02:53, is passes 1 and
  1b on the branch.
- **Frame 312.** "The page after a review with no verdict says the team
  stopped work ..." (stack.md 1934). It owns the m40 page that this review
  produced. Its last status, 2026-10-24 22:55, is night 164: "all 5 rulings
  landed and 0 of 5 moved the row he named, W-A". Night 171's m40 repeats
  that shape (section 4).

## 4. What his reply on m40 moved

His reply m41: "Line 6 names a test file for short help text ... put the
new tests with the other utils tests. Please add a check that the path is
under AppData Local when the roaming flag is False, then run the review
again rather than stop. Line 7 misreads me ..."

1. **The ruling landed.** r_m41: `c_1` contest with the words "add a check
   that the path is under AppData Local when the roaming flag is False",
   `c_3` approve, `bg_1` approve, `get_app_dir_windows` approve (observed:
   rulings).
2. **His line 6 became an approve.** The ruling door told the Liaison in
   s139: "line 6: the words do not fault bg_1's files. Approve line 6."
   His words faulted the test file of line 6 (observed: s139 runner
   account). The page lines are not stored, so the claim that line 6 was
   bg_1's file list is reasoned from the ruling's keys.
3. **c_1 did not move.** The Terminologist s141 sent
   `criteria.respecify` four times. The first named
   `src/click/core.py::get_app_dir` and was refused as an unknown symbol.
   The next three were refused: "the principal contested these words: 'add
   a check ...'. Write what he asked for." c_1 already held the
   `roaming=False` branch, so the seat resent the same text (observed: s141
   runner account, criteria c_1 version 2, the same text as at review
   time).
4. **No test moved on m41.** No `tests.encode` or `tests.retire` runs
   between m41 and m46 (observed: tool_calls). The c_3 rewrite in s150 and
   the test rewrite in s153 follow m47, the next page.
5. **The review did not run again.** No Critic `tick:review` session runs
   after s130. The review key is gone from `tick_attempts`, so it was
   lifted. The batch then went red, "36 test(s), 1 not passing" (launch log
   lines 53 and 54), after s153 rewrote the c_3 test. The developer now
   holds `tests_failing` on bg_1 at 3 attempts (observed: tick_attempts,
   sessions s154 to s163).

So m41 moved no criterion row, no test row and no batch row. The ruling
landed and the lift happened. His ask to run the review again did not reach
a review, because a later test went red first.

## 5. The doubt

- Whether `_pass_lines_check` admits two separate added lines for one
  criterion as two parts is not probed. If it does, the refusal text could
  name that form for a criterion with two branches.
- The fix belongs to the frame that holds F37. The choice between a
  per-branch line map and a block admitted for a compound criterion
  touches the comment at api.py 14853 (frame 170's review), so it needs a
  provenance read first.
