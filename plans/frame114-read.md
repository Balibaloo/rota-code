# Frame 114, a failing inherited test has no route: the read of the refused repairs

Rota workflow. A read-only agent on Opus read the turns of nights 107 to
113 in the night databases on 2026-10-04, 124.9k on the harness line
against 120k. Roman asked for the read in place of a ruling (ruled: Roman,
2026-10-04 14:18, "investigate this with a sub agent"). Every claim below
is the agent's, with its mark. This session did not run the checks again.

## The options the read judged

- (a) The door lets the Developer change an unnamed definition when the
  batch's own earlier commit changed that definition.
- (b) Today's rule stays: an exact restore only.
- (c) The Developer reports to the Liaison, and the Principal rules.

## 1. The door today

(observed: `rota/roles/api.py`, 2026-10-04)

- `_challenge_evidence` in `rota/core/sandbox.py:700` blocks challenges
  only. The repair door is in `code_write`, `api.py:10012-10027`, and its
  check is `_changed_unnamed_defs` at `api.py:10828`.
- The door refuses a write that changes the source of a top-level function
  or class when no criterion names that definition. It accepts the change
  when the new source equals the `project_root` copy of that definition.
- The door checks definitions only. Import lines and other module-level
  lines pass.
- The refusal text: "this write changes {names}, and no criterion of this
  batch names it: the criteria name {named}. The project's own tests call
  {name} as it is. Leave it: write only your new definition with
  start={after}, end={after}, which inserts after {name}. A change to
  {name} needs a criterion that names it".
- A second door, the drops door at `api.py:9973-10008`, refuses a
  whole-file write that drops definitions that tests or other files use.
  Most of the refused repairs are this door, 37 on night 112.
  `plans/night111-read.md` section 5 and `plans/night112-read.md` section 3
  give them the wrong door name (observed: the refusal strings in the
  turns, 2026-10-04).

## 2. The refused repairs

(observed: the turns and the git history in clickI, 2026-10-04. The agent
applied each write to an exported copy of the commit in the scratchpad and
ran pytest.)

| Night | Session | What the seat sent | The door's answer | (a) accepts | Repairs |
| --- | --- | --- | --- | --- | --- |
| 107 | s138, s141, s145 | The whole `__init__.py`: the 64 exports back, and a shortened `__getattr__` | unnamed, on `__getattr__` | yes, commit 29b7870 changed it | partly: 26 red to 6 red, and the head passes those 6 deprecation tests |
| 108 | s233, twice | `_readline_prompt` rewritten | unnamed | no, the batch changed only `confirm` | not a repair of the break (reasoned) |
| 108 | s332, twice | spans over `help_option` and `custom_version_option` | unnamed | no, the batch changed only `version_option` | not a repair (reasoned) |
| 111 | s253, s255 | whole `utils.py` writes, cut short | drops | no, another door | no |
| 112 | 18 sessions, 37 refusals | the same whole `utils.py` writes | drops | no | no |
| 112 | s315, s327 | short whole-file writes, 649 to 1,532 characters | unnamed | no, the batch changed no definition in `utils.py` | no |
| 113 | s154, s155 | whole `utils.py`, 6,747 characters with 15 definitions changed, and 603-character writes | unnamed and drops | no | no |

Counts:

- (a) accepts the write and the write repairs the suite: 0.
- (a) accepts the write and the write is wrong: 3, all on night 107.
- (a) does not reach the write: every other refusal, 7 unnamed-door
  refusals in 5 sessions and every drops-door refusal.

## 3. The restore existed, and no refusal named it

- Today's doors accept the exact restore in every case (reasoned: an
  import line is not a definition). The agent ran each one (observed:
  pytest on the scratch copies, 2026-10-04):
  - Night 107: the imports back, with the head's `__getattr__` kept, gives
    0 red.
  - Night 111: the one line of 3449fcca89 deleted takes 40 red to the count
    before the break.
  - Night 112: line 2 of dbadc97ab3 deleted takes 34 red to the 1 red
    before the break.
  - Night 113: the 15 header lines of b16ded808b back gives 0 red.
- No refusal names this restore. The unnamed-door refusal offers "insert
  after `__getattr__`". On night 107 that sent s138 into the refusal
  "defines __getattr__ twice" (observed: s138, turn 3).
- The size of the write separates the repairs from the failures. Night
  112's s252 sent a span of 3 to 5 lines over the import block, and the
  cycle cleared. The failing sessions sent whole-file rewrites of a file of
  688 lines and 21 KB, which the seat's reply cannot hold, so the text was
  cut short. Other sessions aimed spans at the wrong lines: commit 93e061b
  deleted the line beside the cycle import, and bg_3's head on night 112
  holds `from .decorators import command` twice.

## 4. The risk of (a)

- Commit 0432581 followed nights 47 and 48, where a seat replaced `echo`
  with its own copy, 19 project tests went red, and the seat called them
  unrelated for nine rounds. No ruling in `DECISIONS.md` or `LAWS.md`
  names this door (observed: the commit and the two files, 2026-10-04).
- (a) lets a batch rewrite again any project definition the batch touched
  once. Night 107 shows the cost: (a) accepts a `__getattr__` that drops 6
  deprecated aliases.
- (a) is computable: the door holds `before`, the worktree file, and
  `base`, the `project_root` file, so the test is
  `base.get(name) != before.get(name)` in `_changed_unnamed_defs`.
  `project_root` is the main checkout and not the batch's base sha, and
  `batches` stores no base column.

## 5. Causes the three options miss

- Three of the four breaks are relative imports that make a cycle:
  `from .core import command`, `from .decorators import command`,
  `from . import click`. `_own_package_import` at `api.py:10751` catches
  only `from click import ...` at level 0. A cycle check that reads
  relative imports refuses these breaks when the seat writes them
  (reasoned).
- A whole-file rewrite of a large file cannot land. Neither refusal tells
  the seat which lines its own batch added.

## The agent's recommendation

Keep (b), and add two door changes:

1. The cycle check reads relative sibling imports.
2. A refusal quotes the batch's own lines outside definitions in that
   file, and gives the exact span that restores them.

## Not checked

- Why 29b7870's change to `__getattr__` passed the door on night 107.
- Whether night 108's writes repair anything, beyond a read of them.
- How pytest's failure counts map to rota's `inh_*` test ids.
- Night 106's sessions.
