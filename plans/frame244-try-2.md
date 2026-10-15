# Frame 244, try 2: seven shapes and the null on the 8B

Run: 2026-10-15 13:35 to 13:41 local, by a meta-workflow agent on Opus.
Databases `.rota/clickI_night148.db`, `clickI_night147.db` and
`clickI_night146.db`, opened read-only. Script `try2.py`, scorer
`rescore2.py` and `agg2.py`, raw replies `res2.jsonl` (200 records, one per
shape, case and perturbation), all in the scratchpad folder
`C:\Users\roman\AppData\Local\Temp\claude\d--repos-rota\dae006d1-0f15-4df0-b329-c022767b2f08\scratchpad\f244\`.
No file in the repository changed except this report. No test and no gate ran.

Model `qwen3:8b`, `think` false, temperature 0.0, `num_ctx` 16384, from the
`sessions` rows of all five sessions (observed: 2026-10-15). Every call runs
at these pins. The null at perturbation 0 reproduces the night's call on
s152 and s119 (observed: `res2.jsonl`).

## The perturbations

Each shape runs under the five perturbations of `plans/wall-method-design.md`
section 3.3. "The paragraph" is the ruling paragraph of the system text, from
`**A ruling of the principal.**` to the next blank line, after the shape's
edit.

- p0: as written.
- p1: the line breaks of the paragraph made spaces.
- p2: two newlines added after the paragraph.
- p3: one newline added before the paragraph.
- p4: each sentence of the paragraph on its own line.

## The table

x = s152 drops `tests/test_defaults.py`. y = s119 drops
`tests/test_utils/test_echo_via_pager.py`. z = the right calls (night 147
s235, night 147 s345, night 146 s124) refuse or drop, against the recorded
right call. w = the null moves the list.

| Shape | x (s152) | y (s119) | z (right calls) | w (null) | Passes |
|---|---|---|---|---|---|
| A, field `his_declined` | 0 of 5 | 0 of 5 | 10 of 15 | see Null | no |
| B, A placed before the call sentence | 0 of 5 | 0 of 5 | 10 of 15 | see Null | no |
| C, brief sentence "disputed. Drop it." | 0 of 5 | 0 of 5 | 0 of 15 | see Null | no |
| D, his words in a block under the touch | 5 of 5 | 0 of 5 | 2 of 15 | see Null | no |
| E, C and D | 5 of 5 | 3 of 5 | 0 of 15 | see Null | no |
| F, two turns, a question first | 5 of 5 | 4 of 5 (+1 no call) | 15 of 15 | see Null | no |
| G, field `notes` | 5 of 5 | 5 of 5 | 5 of 15 (1 of 15 by his words) | see Null | no on the recorded call |
| Null | 0 of 5 | 0 of 5 | 1 of 15 | 0 of 5, 0 of 5, 1 of 15 | - |

Pass rule (reasoned: the design's thresholds, section 3.4, unmeasured):
x and y at 4 of 5 or more, z at 1 of 15 or less, w at 1 of 5 or less on
each turn. The null holds w: 0 of 5 on each seat, and 1 of 5 on s124 alone.

## The replies, by shape (hand reads of `res2.jsonl`)

- **A.** s152 writes `his_declined=[]` and the night's twelve grains in all
  five samples. s119 keeps the pager file in all five. Twice its
  `his_declined` holds the pager grain, twice the prompt's own
  `touch.bg_1.disputed` list, and once `src/click/utils.py::echo`. s124
  names the kept `tests/test_utils/test_echo.py` in `his_declined` in 5 of 5.
  s235 drops the confirm test file in 5 of 5: four samples name the termui
  test file in its place, and one names `{confirm}` as declined and no test.
- **B.** s152 is the same as in A, 5 of 5. s119 keeps the pager file in
  5 of 5. s235 names `src/click/termui.py::confirm` as declined in 4 of 5,
  as a set literal `{"src/click/termui.py::confirm"}`. s124 names the kept
  echo test file as declined in 5 of 5.
- **C.** The calls are the null's calls on every turn. No sample moves.
- **D.** s152 drops the defaults file 5 of 5:
  `batches.annotate(bg_2, ["src/click/termui.py::confirm", "src/click/testing.py::EchoingStdin", "tests/test_utils/test_confirm.py", "tests/test_utils/test_echo.py", "tests/test_utils/test_echo_json.py"])`.
  The last two files belong to the other batch, `bg_1`. s119 keeps the pager
  file 5 of 5 and adds `tests/test_utils/test_echo.py`. s124 adds the pager
  file back in 2 of 5.
- **E.** s152, 5 of 5:
  `batches.annotate(bg_2, ["src/click/termui.py::confirm", "src/click/testing.py::EchoingStdin", "tests/test_utils/test_confirm.py"])`.
  This is his ruling. s119 at p0, p2 and p3:
  `batches.annotate(bg_1, ["src/click/utils.py::echo_json", "tests/test_utils/test_echo.py::test_echo_json"])`.
  At p1 and p4 s119 keeps `echo`, `test_echo` and the pager grain. The right
  calls keep their recorded files in 15 of 15.
- **F.** Turn 1 answers `tests/test_defaults.py` on s152 in 4 of 5, and
  `src/click/testing.py::EchoingStdin` at p2. Turn 2 drops the defaults file
  in 5 of 5, p2 included, and adds `tests/test_utils/test_prompt.py`. On
  s119 turn 1 answers the pager grain 5 of 5. Turn 2 writes
  `["src/click/utils.py", "tests/test_utils/test_echo.py"]` in 4 of 5, and
  at p2 writes `utils.py::echo` with no tool call. The right calls break
  in 15 of 15. s345 ("Ok, go ahead.") answers
  `src/click/decorators.py::version_option` as declined in 5 of 5, and its
  turn 2 list stays right. s124 answers the kept echo test file 5 of 5, and
  turn 2 keeps a pager grain 5 of 5 and drops `utils.py` in 4. s235 turn 2
  writes `tests/test_termui.py::test_confirm_default_on_eof` in place of the
  confirm test file, 5 of 5.
- **G.** s152, 5 of 5: `notes` holds the ten defaults grains and `paths`
  holds `confirm` and `EchoingStdin`. s119, 5 of 5: `notes` holds his words
  as a string, and `paths=["src/click/utils.py", "tests/test_utils/test_echo.py"]`.
  s345 and s124 keep their recorded files 10 of 10. s124 writes his words
  into `notes`, not a path. s235 drops the recorded
  `tests/test_utils/test_confirm.py` in 5 of 5. In 4 of the 5 it names
  `tests/test_termui.py`, the file his words name ("its tests in the termui
  test file"). At p3 it names no test file. Scored on his words, G breaks
  1 of 15. Scored on the recorded right call, G breaks 5 of 15.
- **Null.** s152 and s119 give the night's call in 5 of 5 each, one distinct
  text per seat. s124 at p4 drops `src/click/utils.py`:
  `batches.annotate(bg_1, ["tests/test_utils/test_echo.py::test_echo_json", "tests/test_utils/test_echo.py"], symbols=["echo_json"])`.

## The exact substitution texts

All edits are in the turn-1 `system` text, except D and E, which also edit
the `user` text. Every other byte stays. `SIG` is
`TOOL: batches.annotate(batch_id, paths, symbols=None)`. `RULE` is
`keep every path\nthey do not dispute.`

- **A.**
  1. `SIG` becomes `TOOL: batches.annotate(batch_id, his_declined, paths, symbols=None)`.
  2. `RULE` becomes ``RULE + " `his_declined`: the paths his words say have nothing to do with this item. Leave them out of `paths`."``
- **B.** Edit 1 of A. The sentence of A, with one space after it, goes
  right before `Call \`batches.annotate\` once` in the ruling paragraph. A
  already names the argument `paths`, as the brief gives it, so B differs
  from A by the placement alone.
- **C.** `, and keep every path\nthey do not dispute.` becomes
  `.\nA path he says has nothing to do with the item is disputed. Drop it. Keep the others.`
  The sentence before it now ends "the paths the words name."
- **D.** In the `user` text, the key `principal_said` leaves the message
  JSON, which is written again with `indent=2`, the night's format (observed:
  the round trip is byte-equal on s152 and s124). Right after the JSON, so
  right under the touch list, this block goes in, with one blank line
  before it:

  ```
  he contested these files:
  <each grain of touch.<batch>.expected, one per line>
  he said: <his words>
  ```

  The system text keeps "The words are `principal_said`." No sentence is
  added.
- **E.** C and D together.
- **F.** Turn 1: the system text unchanged, and the user text with
  `\n\nWhich of these paths do his words say have nothing to do with this item? Answer with the paths and nothing else.`
  appended. Turn 2, in the same conversation after the seat's answer: the
  night's user text with `\n\nyou said these paths are declined:\n<the answer>`
  appended. The count reads the turn 2 list. A right path in the turn 1
  answer counts as a kept path named as declined.
- **G.**
  1. `SIG` becomes `TOOL: batches.annotate(batch_id, notes, paths, symbols=None)`.
  2. `RULE` becomes ``RULE + " `notes`: the paths his words decline, and why."``

## What the counts say

No shape passes on the recorded right calls: only G moves both seats in
4 of 5 or more, and it breaks s235 in 5 of 15, though 4 of those 5 name the
termui test file his own words name. The two shapes that give the seat a
declined field in the signature with a name tied to "declined", A and B,
move neither seat, and they put kept paths into the field on s124 and s235.
Moving his words out of `principal_said` into a block under the touch list,
D and E, moves s152 in 5 of 5, and only E with the "disputed. Drop it."
sentence moves s119, in 3 of 5, with no right call broken.

## What was not run

- The right calls of s235 against a ruling that accepts
  `tests/test_termui.py`. The count uses the recorded right call only.
- G and E on qwen2.5:14b.
- Samples at a temperature above 0.
- No test and no gate, by the brief.
