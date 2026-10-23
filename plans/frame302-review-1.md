# Frame 302, review 1: pass 1 at e041c662

Reviewer on Opus, read-only. Worktree `C:/Users/roman/rota_r302` at
e041c662, parent 9d4274b4. Date 2026-10-23.

## Verdict

Do not accept for the night as it stands. The door refuses the shape of
night 157's s274 and s297 correctly. It also refuses 58 annotate calls of
nights 150 to 157 that wrote `path::symbol` in `paths`. Those calls landed
on their nights, and the refusal tells the seat a false thing about them.
One line in `_refuse_unindexed_files` fixes this (finding 1). After that
fix, accept, with findings 2 and 3 as the next pass.

## Method

1. The map tool gave `batches_guess` at api.py 6050, `batches_annotate` at
   6132, `_refuse_stray_dirs` at 5982 and `_refuse_unindexed_files` at 6014.
   Each door has the same two callers.
2. A copy of `clickI_night157.db` in the scratchpad took the replay. The
   real `build("architect", ...)` sandbox dispatched each call.
3. Nights 150 to 158 were opened with `mode=ro`. Every `batches.guess(` and
   `batches.annotate(` in `turns.completion` was parsed with
   `toolproto.parse_args` and run through both real doors.
4. The index at call time is not stored. The night's end index holds files
   that batches made during the night. The base tree, `origin/main` 2c8cd3a
   of `D:/repos/_AI/sample_repos/clickI`, gives the start index. Nights 150
   and 155 hold exactly the base files less three non-code files, so the
   start index is the end index intersected with the base tree.
5. The stale count compares `fixtures.system_text_for(case)` for every
   single-session case at e041c662 and at D:/repos/rota HEAD. HEAD differs
   from 9d4274b4 only in `plans/stack.md`.

A process note: the stale script wrote its two JSON outputs into the two
tree roots by a relative path. I moved both files to the scratchpad at
once. `git status` in both trees shows no change from the review.

## Point 1: the red test

CONFIRMED. s274's call and s297's call, replayed through the real ops on
night 157's database, are both refused with `ValueError`. The text is the
same as the pass report gives. The route is `ERROR <call>: <text>`, which
`runner.py` 5006 and 5058 build from the exception. The refusal names
`new_files=[...]`, and a call that names `src/click/options.py` in
`new_files` lands with 3 grains.

Word counts of the four sentences: 8, 15, 8 and 10 tokens. The second
sentence counts each path as one word. Every sentence holds 20 words.

`src/click/decorators.py` appears because it sorts eighth. The list is
`sorted(...)[:8]` of the 18 files under `src/click`. A file that sorts
after `decorators.py`, for example `termui.py` or `utils.py`, never shows.
The confirm item of the same nights points at `termui.py`, so the same
wrong-file mistake on that item gets a list without the right file.

A rank by shared stem does not help this case. No file under `src/click`
shares a stem with `options`. The fact that names the right file is the
symbol index: `src/click/decorators.py::version_option`, which s273 named
as a bare symbol and which the item text names.

The tests directory gives the same weakness. A refused
`tests/test_version_option.py` lists `tests/conftest.py`,
`tests/test_arguments.py` and six more by sort order, out of 47 test files.

## Point 2: right calls refused, nights 150 to 158

CONFIRMED by the sweep. 105 distinct calls parsed: 16 guess and 89
annotate. Two more annotate calls of night 156's s155 did not parse. The
new door refuses 68 of the 105: 6 guess and 62 annotate. The directory door
refuses none of the 105. The count is the same with the end index and with
the start index.

The 68 refusals by cause:

| Cause | Calls | Nights | Right call? |
|---|---|---|---|
| `path::symbol` written in `paths` | 58 | 150 to 157, all annotate | The file half is right. Each call landed on its night. |
| New test file for confirm EOF | 4 | 157: s217, s223, s229 guess, s228 annotate | Plausibly right. bg_1 was deferred, so no commit shows. |
| `tests/test_utils.py` | 2 | 155: s281, s285 annotate | Not shown right. Night 155's batches were abandoned. |
| `src/click/options.py` | 4 | 157: s273, s274, s297; 158: s222 | Wrong. These are the refusals the frame is for. |

Of the 58, four calls of night 154's s169 also carry `termui.py:prompt`
with one colon. One call of night 153's s121 also carries
`tests/test_utils/test_echo_json.py`, a right new file the night later
indexed.

s274 and s297 also carry `tests/test_version_option.py`. That file is a
right new file. The night's index holds it at the end, and night 158's
merged bg_3 adds the same file. So the door's first refusal on s274 is
right, and the second refusal, after the seat corrects the source file,
refuses a right new test file. The replay confirms the second refusal.

False refusals:

- The 58 `path::symbol` calls are false refusals. The text says "is not a
  file the index holds", but the file half is held. `new_files` saves them
  only by a wrong route: a call that names
  `src/click/decorators.py::version_option` in `new_files` lands, and
  writes a symbol as a path grain, as today.
- The 4 confirm EOF calls and the second refusal of s274 and s297 are
  false refusals of right new test files. `new_files` saves them only if
  the seat knows the argument. Point 3 says where the seat can read it.

## Point 3: the prompt

CONFIRMED. `runner.py` 368 writes `sb.signatures()` into the system text.
The seat reads `batches.guess(item_id, paths, symbols=None, new_files=None)`
and `batches.annotate(batch_id, paths, symbols=None, new_files=None)`.
The briefs do not name the argument. `guess.md` line 8 says "a new file you
name as new", and `annotate.md` line 23 says the same, with no word of how
to name it. So the seat meets `new_files` in the signature line and in the
refusal only.

Five recorded cases go stale from the signature change, and no other case:

- `L1-AR-annotate-a-batch`
- `L1-AR-annotate-from-the-guess`
- `L1-AR-re-annotate-from-the-principals-correction`
- `L1-AR-guess-the-code-of-a-request`
- `L1-AR-rewrite-the-guess-from-the-ruling`

The seven chain cases do not compose through these modes. Because the five
cases go stale anyway, a brief sentence added now costs no extra re-record.

## Point 4: the symbols half

CONFIRMED. In `guess`, a symbol on an unindexed file under an indexed
directory lands. The probe `symbols=["src/click/options.py::version_option"]`
landed with 2 grains, and so did `src/click/nothere.py::x`. The directory
door still checks the symbol's file half.

On the nights, 8 symbol entries with `::` appear in guess calls of nights
150 to 158. One file half is not indexed: night 158's s154 wrote
`termui.py::...`, a root path. The gap is small on this shape. Note that
annotate gives its symbols to neither door, which is the state before the
pass too.

## Point 5: the scenes and the two door tests

CONFIRMED by reading the diff.

- `scenes.py`: `_new_files` names every path the scene's index lacks. It
  is the door's own predicate, so a scripted seat can never meet the
  refusal. The report's doubt holds. The scenes keep their meaning for
  what they test, but no scene shows a seat that meets the refusal and
  then corrects the file or names it as new. The move of the annotate seat
  into a `Session` function is supported by `seat()` and changes no order.
- `test_touch_note.py`: the directory refusal of `src/split_bill.py` stays.
  The landing call now names `split_bill.py` and `tests/test_split.py` as
  new. The test keeps its meaning under the narrowed rule.
- `test_index_refresh.py`: the second file is named as new. The claim of
  the test, that the directory a batch made is now known, stays.
- The new test file builds night 157's index from the end of the night.
  That index holds `tests/test_version_option.py`, which the seat's wake
  did not hold. So `test_s274s_guess_lands_when_the_file_is_named_as_new`
  passes with only `options.py` named, where the real call needed both.

## Point 6: nothing else changed

CONFIRMED. `git diff 9d4274b4 e041c662 --stat` lists five files:
`rota/roles/api.py`, `rota/testkit/scenes.py`,
`tests/rota/test_frame302_unindexed_path.py`,
`tests/rota/test_index_refresh.py` and `tests/rota/test_touch_note.py`.
The text of `_refuse_stray_dirs` at both commits has the same SHA-1,
`b376e9da10cfd910e4eb73398166bd3b5c9e3dd5`.

## Findings

1. HIGH, CONFIRMED. The door refuses `path::symbol` in `paths` as "not a
   file the index holds". 58 of 105 calls of nights 150 to 157 have this
   shape, and all landed. `new_files` lets the symbol through as a path.
   Fix: compare `p.split("::", 1)[0]` against the index, or refuse a `::`
   path with a text that names `symbols=[...]`.
2. MEDIUM, CONFIRMED. The list of eight is alphabetical, and
   `decorators.py` is in it by chance. Fix: put first the files that hold
   a symbol the call or the item text names, then the rest by sort order.
3. MEDIUM, CONFIRMED. Right new test files are refused, and the seat reads
   `new_files` only in the signature and the refusal. This hits the second
   step of s274 and 4 calls of night 157. Fix: name `new_files=[...]` in
   `guess.md` line 8 and `annotate.md` line 23, in the re-record the five
   stale cases need anyway.
4. LOW, CONFIRMED. The symbols half of `guess` is not checked for an
   unindexed file. One entry in nine nights. Fix: pass the symbol file
   halves to `_refuse_unindexed_files` as the directory door does.
5. LOW, CONFIRMED. The scripted seats name every unindexed file as new, so
   no scene meets the door. Fix: add one scene seat that meets the refusal
   and then lands with the corrected file.
6. LOW, CONFIRMED. The new test's index is the end of night 157, so the
   test lets `tests/test_version_option.py` pass unnamed. Fix: drop that
   file from the test's `TESTS`, and name it in `new_files` in the landing
   test.

## Counts

- Point 2: 68 refused of 105 calls. 4 are the wrong file the frame
  targets. 58 are `path::symbol` false refusals. 4 are plausibly right new
  test files. 2 are not shown right.
- Point 3: 5 cases go stale.
