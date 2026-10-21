# Frame 201, review 1 of e374ecb8

Reviewer on Opus, 2026-10-21, read-only, for session 5389be74. The
worktree is `C:/Users/roman/rota_r201` at e374ecb8, the parent is
02c449b2.

**Verdict. Accept e374ecb8.** The commit changes no predicate, the
texts hold the house rule, and the tests pin the cap and the route. One
high stays open, and it is not a regression of this commit: the fix does
not reach the real diff of night 157, so frame 201 does not close on
this commit. Pass 2 is a predicate change in `_added_kinds`. Counts: 1
high, 1 medium, 6 low.

## (a) The verdict on each point

1. The predicate. CONFIRMED unchanged. 37 calls on 6 fixtures admit and
   refuse the same at both commits. No call moved.
2. The texts. Hold the order fact, step, candidates, route. Two sentences
   break the 20-word cap, one of them inherited. One sentence is surplus.
3. The real diff. CONFIRMED gap. The exact call of s324 gets the block
   text, not the docstring text. The list names the three docstring lines
   as code. One docstring line alone lands as a pass. High, for pass 2.
4. The parts rule. Right for the seat in the common shapes. Two edges
   misname the lines: a value with unheld fragments, and a part shorter
   than `_LINE_PART_MIN`. Low.
5. The list. The first eight code lines of the diff in diff order. On
   forty lines the block of the seat falls out of the list. Medium.
6. The tests. The three new tests are red at 02c449b2 for the reason the
   brief names. The pins keep the cap at 2 and the route last. No old
   assertion is weaker. One is stronger.
7. The brief. Recommend against a brief sentence now. 134 rows of
   `qwen3:8b` carry the current review brief, and 7 `CR` cases re-record.
   The door says the missing fact at the moment of the act, for 0
   re-records.

## (b) Findings

### High

**1. Point 3. The fix does not reach the diff of night 157, and the
list offers docstring lines as code.** `rota/roles/api.py:11348-11421`
(`_added_kinds`) and `11534-11553`. CONFIRMED by probes d1 to d3 on a
fixture built from `clickI` at `main` and `8715681`. The hunk
`@@ -461,6 +462,9 @@` starts inside the docstring, so the walk reads the
three `:param show_python:` lines with kind None. The exact call of s324
then gets the block text, and its list reads `'show_python: bool =
False,', ':param show_python: If True, append the running Python
interpreter', 'version string (major.minor.micro from sys.version_info)
to the', 'message. Defaults to False.', 'if show_python:', ...`. The seat
that copies the second candidate lands a pass: probe d3, one docstring
line alone, ADMIT. Two docstring lines also land, probe d2. Under the
ruling of frame 170 that pass is admitted: the ruling asks for a named
added line, and the design scored a docstring line as a miss by hand in
ratio two (`plans/frame170-design.md:99`). Under the door of frame 180 it
is a wrong pass, the sign of night 152. The fixture of the commit, `bg2`,
puts the nine lines in one hunk with the opening fence, so the test is
green on a shape the night did not have. Fix, the diff route: run a
second `git diff -W` of the batch for the kinds walk only, never for the
`[diff]` block of the seat, so each hunk carries the opening of its
function. Fix, the file route: read the file at the batch head, mark the
docstring spans with `ast`, and start each hunk in that state. Price:
the diff route 2 cycles, a pass and a review, plus the case re-record.
The file route 3 cycles. Test: the two real files as the fixture, the
call of s324 expects the docstring text, and one docstring line expects
the no-behaviour refusal.

### Medium

**2. Point 5. The list names the first eight code lines of the diff,
not the held lines of the seat.** `rota/roles/api.py:11504-11510`.
CONFIRMED by probe e1: a diff of forty code lines, a block of
`value_10`, `value_20`, `value_30`. The text lists `value_0` to
`value_7`, "and 32 more". In the block branch the held code parts of the
seat are the best candidates, because the right line is among them, and
the list can omit all of them. The house rule asks for the set, and the
set here is the block. Fix: in the block text, when held code parts
exist, name them before the list of the diff: "One of the lines you sent
is the line: 'x', 'y', 'z'. Copy that one." Price 1 cycle. Not an
overfit: the rule reads the value, not the night.

### Low

**3. Point 2. Two sentences break the 20-word cap, and one sentence is
surplus.** `rota/roles/api.py:11540-11547`. CONFIRMED by the word count
of the texts of the probe. The docstring text reads six sentences: 12,
10, 8, 20, 42 and 19 words. The 42-word sentence is the list, one
sentence by shape in every text since frame 180. The mixed-kind variant
reads a 21-word second sentence, the `_NO_BEHAVIOUR` roll. The first
sentence of the no-behaviour text is 39 words, unchanged from frame
180. The third sentence of the docstring text, "A pass names one added
line per criterion.", restates "the one added line" of the step. Cause 9
asks for one fact and one step. Fix: cut that sentence. Keep the list as
a list.

**4. Point 4. A value with unheld fragments reads "they are docstring
lines".** `rota/roles/api.py:11534-11541`. CONFIRMED by probe c7: one
held docstring line and two fragments the diff does not hold. The text
says all three lines are docstring lines. The step and the list stay
right, so the next move of the seat is right. Fix: "and the lines the
diff holds are docstring lines", or count the held lines.

**5. Point 4. A short part decides the kind.** `rota/roles/api.py:11441-11450`
and `11534`. CONFIRMED: `_held_kinds('if', kinds)` returns
`[None]` where `_line_held('if', added)` returns False. `_held_kinds`
has no `_LINE_PART_MIN`, so a two-letter part is a held code line in the
block branch, and a block of one docstring line and two short fragments
reads the block text in place of the docstring text. Fix: in `held`,
skip a part shorter than `_LINE_PART_MIN` unless it is exact, the rule
of `_line_held`.

**6. Point 7. A brief sentence costs 134 rows and 7 cases, and buys an
unproved move.** `rota/roles/prompts/critic/review.md:9-11,33-36`.
PLAUSIBLE. Rows of `tests/rota/cassettes.db` whose `system` holds the
review brief: 3,323 in all, 355 for `qwen3:8b`. Rows that carry the
current `lines=` sentence of 1663c2bb: 134 for `qwen3:8b`, 81 of them
replayed, and 86 for `gemma3:12b`. The key of a row is the sha of model,
pins, protocol, system and user, so one changed word in the brief misses
every such row. The 7 `CR` cases of `qwen3:8b` re-record at 5 runs each,
35 runs. s324 had the words of the brief, "a line that starts with `+`",
and copied three `+` lines. The fact it lacked, that a docstring meets
nothing, is now in the text of the door at the moment of the act.
Recommend against, until a night shows a Critic that reads the new text
and still sends the block.

**7. Outside. The cassette database of the worktree is empty.**
`C:/Users/roman/rota_r201/tests/rota/cassettes.db` is 0 bytes, written
today at 12:07. The file is gitignored, and `rota/paths.py:60` reads it
unless `ROTA_DEV_DB` is set. A gate run from the worktree without
`ROTA_DEV_DB` replays nothing and writes misses. Fix: set
`ROTA_DEV_DB=D:/repos/rota/tests/rota/cassettes.db`, or run the gate
from the checkout.

**8. Outside. The commit message claims the shape of the night.** The
message says the block refusal now names the kind for the three
docstring lines of bg_2. On the real bg_2 it does not, finding 1. Fix:
the stack line for e374ecb8 says the fixture is a short function and
the real diff waits on pass 2.

### Points with no finding

- Point 1. 37 calls, 0 moved. The admits at both commits: the three code
  lines of s279, the two lines of s279, three code lines of `kinds`, the
  `dumps` line of s134, the code line of bg_2, and on the real diff one
  docstring line, two docstring lines and the code line. The ten
  recorded passes are refused at the missing check before any changed
  line, at both commits. `_batch_diff` now runs before the block check.
  With no worktree it returns "", and the texts carry no list, so the
  ten pass the same.
- Point 6. The new test file on the code of the parent: 16 red, the 3
  new tests, the 2 block pins and 11 no-behaviour pins. The three new
  tests fail for the reason the brief names: the block text has no list,
  the text for s324 has no docstring sentence, the text for s326 has no
  list. The test file of the parent on the new code: 12 red, all
  exact-text pins that gained the list. `test_a_value_of_three_lines_is_refused`
  moved from `startswith` to full equality, stronger. The cap at 2 stays
  pinned by `test_a_value_of_two_lines_lands` and that test. The route
  last stays pinned by every full-equality pin and `endswith("first, as
  for any fail")`. The worktree: 72 passed in 17.9 s.

## (c) Probes

All under
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/5389be74-1e5e-433d-aa86-c4a8d594cb8e/scratchpad/`.

- `f201_rev_probe_door.py`: builds s279, kinds, s134, bg2, the real bg_2
  from `clickI` at `main` and `8715681`, and a forty-line diff. Sends 37
  calls and prints ADMIT or REFUSE with the text. Run from
  `C:/Users/roman/rota_r201` into `f201_rev_door_new.txt`, and from
  `r201_old/`, a `git archive` of 02c449b2, into `f201_rev_door_old.txt`.
  Prints the hunks of the real diff and the kinds of its added lines.
- A column diff of the two outputs and a word count per sentence of the
  texts a2, c1, c2, c8 and d1, run inline.
- `r201_old/` with the new test file: `pytest tests/rota/test_verdict_lines.py`,
  16 failed, 56 passed. `r201_new/`, a `git archive` of e374ecb8 with the
  test file of the parent: 12 failed, 57 passed. The worktree: 72 passed.
- An inline `_added_kinds` and `_held_kinds` call on a six-line diff for
  the short-part rule.
- Queries of `D:/repos/rota/tests/rota/cassettes.db`: rows by model
  where `system LIKE '%judge a batch%'`, rows with the `lines=` sentence,
  `CR` cases and runs of `qwen3:8b` in `case_runs`.
- The gate did not run. No point needed it.

## (d) Usage

Input about 100k, output about 20k, total about 120k. Estimate from the
context count, no meter. Over the cap of about 80k in the brief.
