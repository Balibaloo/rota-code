# Frame 302, the provenance: `batches.guess` and `batches.annotate` admit a path the code index does not hold

Provenance read on Fable, 2026-10-21, by the ruling of 2026-10-18 12:02
(every new wall gets a provenance read before its first fix). Repository at
HEAD 66832c54. Sources: `rota/roles/api.py` 5965 to 6114, `git log -S`,
`plans/frame298-design.md`, `plans/frame298-review-1.md`,
`plans/night157-read.md`, `rota/LAWS.md` law 12, `.rota/clickI_night157.db`
opened `?mode=ro`, and the sample tree `D:/repos/_AI/sample_repos/clickI`.
Meta workflow. No file but this one is changed.

## The provenance in one paragraph

Both ops check the parent directory of a path, never the file. The check is
one shared door, `_refuse_stray_dirs`, written on 2026-09-12 for `annotate`
after a person at a seat got `src/split_bill.py` on a tree with no `src/`
(observed: commit 3c29d60b). Frame 298's design copied that door into
`guess` on 2026-10-18 and allowed "a new file you name as new", but the op
takes no way to name a file as new (observed: `plans/frame298-design.md`
lines 302 to 322). On night 157 `src/click` is an indexed directory, so
`src/click/options.py` passed the door in s274 and in s297, and both seats
read index rows that named `src/click/decorators.py::version_option` before
they wrote it (observed: `turns` s273 t1, s297 t1). The records allow a new
file beside existing ones and forbid nothing about a refusal that names the
index, so a door on the file is a narrowing of the 2026-09-12 rule, not a
reversal (reasoned: section 6).

## 1. Which ruling or design made each op, and what it said about paths

**`annotate`.** The op is from 7e3be756, 2026-08-09, "refactor(laws):
amendments, and the settings the principal owns". Its docstring is law 12's
text: "Paths always; symbols only where you are confident", and "Nothing
rejects a diff for straying outside this" (observed: `git show 7e3be756`,
diff lines 79 to 94; `rota/LAWS.md` lines 337 to 342). The first body wrote
every path to `batch_touch` with no check at all (observed: the same diff,
line 98). The archive `plans/archive/p4-scope-disclosure.md` line 13 names
the predicate as existing machinery and adds no path rule (observed).

The only path rule came on 2026-09-12 in 3c29d60b, "fix(desks): a predicted
path lives where the tree has paths": "A nested path under a directory the
index has never seen is refused with the directories the tree has; a new
file at the root or beside existing files is a prediction the tree can hold"
(observed: the commit message). Its test is
`tests/rota/test_touch_note.py` lines 225 to 237: `src/split_bill.py`
refused, `split_bill.py`, `main.py` and `tests/test_split.py` accepted
(observed). So the design of `annotate` never required that a path exist or
be in the index. It required the directory to be in the index and said in
words that a new file beside existing ones is allowed (observed: the message
and the comment at `api.py` 5970 to 5974).

**`guess`.** The op is from frame 298's pass 1, 7ec9b940, 2026-10-18 13:06
(observed: `git log -S "def batches_guess"`). The design, section 3.4 point
7, lists its refusals: a non-request item, an empty `paths`, "a path under a
directory the index lacks (the check of `batches_annotate`)", a symbol with
no `::`, and a second call in one session (observed:
`plans/frame298-design.md` lines 302 to 308). The brief in point 8 says "A
test path is one of `the index's test files`, or a new file you name as
new" and "Name the files you expect the change to edit" (observed: lines 321
to 326). Section 1.2 says the table holds "Paths always, symbols only where
the Architect is confident, the split of `batches.annotate`" (observed: line
90). The design did not require a path to exist or to be in the index. It
copied the directory check and allowed a new file. It gave the op no
argument to name a file as new, so the allowance has no mechanism
(reasoned: the signature at `api.py` 5999 to 6000 takes `paths` and
`symbols` only).

## 2. What each op checks about a path today

Both ops call one helper, `_refuse_stray_dirs(conn, paths)` at `api.py`
5965 to 5996 (observed). The helper reads `code_index` once:
`SELECT grain FROM code_index WHERE grain_kind = 'path'` (line 5976), builds
the set of every directory prefix of every indexed path (lines 5977 to
5979), and refuses a path whose parent directory is not in that set (lines
5983 to 5985). A path at the root is never checked (line 5981). When the
index holds no path the check is skipped (line 5985). The refusal names the
top-level directories only, at most six (lines 5987 to 5992). The file name
is never compared with the index (observed: no query on the full grain).

`guess` calls it at line 6023 with the paths and the symbols' path halves
(review 1, finding 5). It then reads `code_index` a second time at line
6038, for a bare symbol only, and that refusal names the index's own
grain: "The index holds src/click/decorators.py::version_option" (observed:
lines 6031 to 6046, and `turns` s273 t4). `annotate` calls the helper at
line 6093 and reads `code_index` nowhere else (observed: lines 6079 to
6114; the map tool lists no `code_index` read for `batches_annotate`).

**The index on night 157.** The night database holds `code_index`
(observed: `sqlite_master`). It holds 166 path grains and 888 symbol grains.
Under `src/click/` it holds 18 paths, among them `src/click/decorators.py`,
and no `src/click/options.py`. The only grains with `options` in the name
are `docs/options.md`, `tests/test_options.py`,
`tests/typing/typing_group_kw_options.py` and
`tests/typing/typing_options.py` (observed: the query of 2026-10-21). The
sample tree agrees: `src/click/` has no `options.py` (observed: `ls`). So
the door's predicate held, `src/click` is a known directory, and the fact
the frame names, the file, was never asked (reasoned: cause 8, the
predicate is wider than its fact).

The rows the night wrote: `touch_guesses` for `show_python` version 2 holds
`src/click/options.py` and `tests/test_options.py`, and `batch_touch` for
`bg_2` holds `src/click/options.py`, `tests/test_options.py` and, from
s310's judgement, `src/click/decorators.py` (observed: the two tables).

## 3. What s273, s274 and s310 saw

**s273** (tick:guess, show_python) read neither a source file list nor the
index whole. Its wake held three blocks: `[code.callables]`, whose first two
rows are `src/click/decorators.py::custom_version_option | function | 0` and
`src/click/decorators.py::version_option | function | 0`; `[item]`, the text
"version_option has a show_python flag that appends the running Python
version to the message."; and `[the index's test files]`, a list of 47 test
paths that holds `tests/test_options.py` and no `tests/test_version_option.py`
(observed: `turns` s273 seq 1 `user`, whole). It wrote
`batches.guess(item_id="show_python", paths=["src/click/options.py",
"tests/test_options.py"], symbols=["version_option", "show_python"])` three
times. Each call was refused for the bare symbol, with the text "The index
holds src/click/decorators.py::version_option" (observed: s273 seq 4
`completion`). The seat read the right file's name in its wake and in two
refusals and still named `options.py` (observed). The brief's line "A test
path is one of `the index's test files`, or a new file you name as new" was
in the system prompt (observed: s273 seq 1 `system`).

**s274** (the next wake, the same item) read the same three blocks and wrote
`batches.guess(show_python, ["src/click/options.py", "tests/test_options.py",
"tests/test_version_option.py"])`. The door answered
`OK batches.guess -> {"item_id": "show_python", "grains": 3}` (observed:
s274 seq 2 `user` tail). Two of the three paths are not in the index.

**s297** (tick:annotate, bg_2) is the annotate seat, not s310. Its wake held
`[the item's guess]` with the same three paths, the same `[code.callables]`
rows that name `src/click/decorators.py`, and the brief sentence "`the
item's guess` is what you guessed at sign-off ... change a path only where
the source says it is wrong" (observed: s297 seq 1 `system` and `user`). It
copied the guess into `batches.annotate(bg_2, [...])` and got
`OK batches.annotate -> {"batch_id": "bg_2", "grains": 3}` (observed: s297
seq 2 `user`). It read no source (observed: no `code.source` in its
`tool_calls`).

**s310** (judge_touch, bg_2) read `"expected to touch":
["src/click/options.py", "tests/test_options.py",
"tests/test_version_option.py"]` and the diff of `decorators.py`. Its first
call named the three predicted paths as `foreseen`, and the door answered
that they "are not an open stray of bg_2, so the judgement drops them.
src/click/decorators.py is still unjudged" (observed: s310 seq 4
`completion`). Its second call named `src/click/decorators.py` and was
recorded (observed: s310 seq 3 `user`). So s310 judged against a prediction
that named a file that does not exist, as W5 says (observed:
`plans/night157-read.md` line 21).

## 4. An existing door that refuses a path not in the index

Three shapes exist in `api.py`, none on a touch path.

- `surveys_attest`, lines 4465 to 4478: the refusal names grains "spelled
  as the index holds them", then "These are not in the index at all:
  {unknown}", then up to six indexed paths of the area the seat has opened
  (observed). This is the nearest shape: a refusal that names the index's
  own paths beside the one it refuses.
- `_surface_names_what_the_item_names`, lines 5107 to 5115: a bare name is
  refused when `SELECT 1 FROM code_index WHERE grain = ? OR grain LIKE ?`
  finds nothing, with "a name the index does not hold" (observed).
- `_indexed_like(ctx, path)`, lines 14528 to 14545: the one indexed path a
  mistyped path "was reaching for, when exactly one fits", used by
  `code.source` at 13726 before "not found, and no grain in the index is
  named anything like it" (observed). It matches by tail, so
  `src/click/options.py` finds nothing, and `options.py` alone finds
  `tests/test_options.py` (reasoned: the loop at 14537 to 14542).

The shape to reuse is `surveys_attest`'s: one query on the full grain, and
a refusal that names the indexed paths of the same directory (reasoned:
the directory is what the seat got right).

## 5. By which workflow, and whether the conditions were met

`annotate` was built on 2026-08-09, before the two workflows were named on
2026-09-16 (observed: `plans/method/reference.md` lines 57 to 61, C66). It
is Rota workflow code, a seat's op. Its directory door of 2026-09-12 came
from a person at a seat, "seat1", not from a night (observed: the commit
message of 3c29d60b). No night read measured it.

`guess` was built by the Rota workflow under frame 298, "Rota workflow,
designed by the meta workflow" (observed: `plans/frame298-design.md` line
5). Pass 1 landed at 7ec9b940 on 2026-10-18 13:07, the closing gate at
d2e85f79 at 16:41, and night 157 launched at 16:40 from d2e85f79 (observed:
stack entry 298, status lines of 13:07 and 16:41). So night 157 is the
first night of the mechanism, and the frame is validating, not closed
(observed: status 2026-10-21 11:45, "Waits on: night 158"). The design's
measures M1 and M2 read 0 of 0 on night 157, "because both need a merged
item with a git truth, and no item merged" (observed:
`plans/night157-read.md` lines 97 to 99). M0 read 7 of 8 pages with a code
line (observed: status 2026-10-18 19:17). So the design's conditions on the
guess's accuracy were not measured on any night before the mechanism
landed, and the first night could not measure them (observed). The read's
residue says the same: the guess "names `src/click/options.py` and
`tests/test_version_option.py`. Neither file exists" (observed: lines 103
to 106).

Review 1 of pass 1 found the symbol half of this gap, "A symbol under a
directory the index lacks is admitted", severity low, and pass 1's fix kept
the directory grain (observed: `plans/frame298-review-1.md` line 36; `api.py`
6021 to 6024). No review asked whether the file should be in the index
(observed: the grep of the design review and review 1).

## 6. What a cheap fix is allowed by the history

The records forbid no refusal of a path the index does not hold. Law 12
forbids a rejection of a diff for straying outside the prediction, and the
2026-09-12 door already refuses a prediction at the op without touching law
12 (observed: `rota/LAWS.md` 339 to 342; commit 3c29d60b). The same commit
and the guess brief allow a new file beside existing ones, so a flat
refusal of every unindexed path reverses two rulings; a refusal of an
unindexed path that the seat has not named as new narrows them (reasoned:
3c29d60b's message; design point 8, "a new file you name as new", which the
op never took as an argument). The refusal should name the indexed paths of
the same directory, here `src/click/decorators.py` among the 18 under
`src/click/`, and the way to declare a new file, in the shape of
`surveys_attest` at `api.py` 4465 to 4478 (reasoned: section 4; the seat
got the directory right and the file wrong in s273, s274 and s297).
