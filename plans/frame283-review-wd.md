# Frame 283, W-D review at 07887a4b

Reviewer on Opus, read-only, worktree `C:/Users/roman/rota_r283wd`. Verdict: Stands, with finding 1 to fix next.

## (a) The points

1. Holds. Both doors name `shorten: bool = False,` at line 441 on the night's texts. `_drop_note(old, 439, 483, text)` and `_whole_lost` return the same note: "This write removes or rewrites 1 statement that your text does not hold: `shorten: bool = False,` at line 441."
2. Holds on 9 of 10 edges. The multi-line default, `*args`/`**kwargs`, positional-only, keyword-only, lambda default, nested owner, class decorator and two parameters on one line each open one correct note. Two decorators whose first lines are the same `@click.option(` fail (finding 2). A definition the merged file no longer names fails on a header-only span (finding 3).
3. The five named cases open no note: a moved parameter, a re-order, `False` to `None`, an added annotation, one line to many. Two cases outside the list open a new false note (finding 1).
4. The new bound skips a statement whose first line equals the first line of a named block. Body effect: two lost statements on one line are named once, not twice. No pin covers either bound. The 27 tests of the two whole-file and signature files pass with the old bound patched back (finding 4).
5. Holds. 184 passed: 147 in the frame 283 and frame 140 files, 37 in `test_developer.py`. The commit adds one test file and edits no existing test. No assertion is weakened.
6. Zero landed renames. Nights 155 to 164 hold 79 single-parent commits in clickI, from the reflog and the unreachable objects. They hold 0 parameter renames, 2 drops (63c65435 `shorten`, d7dbf3e6 `default_on_eof`) and 17 additions. The rename friction has a count of 0.

## (b) Findings

1. `rota/roles/api.py:22172`, medium, CONFIRMED. `_rewritten_heads` pairs statements by index under an owner. Parameters and decorators now sit in that index. A span write that adds a parameter or a decorator shifts the count, and a body rewrite in the same write becomes a removal. Probe p3: `return` to `return False` plus a new `b=None` opens a note on 07887a4b and none on 1ba28a8e. `go(a)` to `go(a, 1)` plus a new `@cache` does the same. The whole-file door opens no note on either case. Replay p7 of 93 night commit-file spans shows 0 hits, so the rate is low today. Fix: in `_rewritten_heads`, leave out the parts whose kind is `decorator` or `arg ...` from both `placed` and `count`.
2. `rota/roles/api.py:22047`, low, CONFIRMED. `held` is a set of (owner, key), and a decorator keys on its first line. Two multi-line `@click.option(` decorators share one key, so the span door misses a drop of either one. Probe p2: the span and the wide span give None. The whole-file door names line 0, the kept decorator, not line 3. Fix: key a decorator on `_line_key` of its whole source segment, or hold a Counter in place of the set.
3. `rota/roles/api.py:22036`, low, CONFIRMED. The docstring says the walk of `_lost_statements` names the header of a renamed definition. A span over the header alone has no pool, so nothing names it. Probe p2: `def f(a, b)` to `def g(a)` over lines 0..3 gives None. The whole-file door names `b,`. The report repeats the false claim. Gap only, not a regression. Fix: when the owner is gone, name the old header line in `_lost_signature`, or correct the docstring.
4. `rota/roles/api.py:22133`, low, CONFIRMED. The `x <= a <= y` edit has no pin. The pins pass with the old bound patched back (probe oldbound). Fix: add a whole-file case that loses `def f(a, b)` to `def f()` and assert one name.

## (c) Probes

All are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/79847ec6-3334-49c7-8221-098d6165a403/scratchpad/r283wd/`.

- `p1.py` (run with the 481 offset by `python -c`): the night's texts through `_drop_note` and `_whole_lost`.
- `p2.py`: the edges of point 2, on the smallest span, the whole-file span and the whole-file door.
- `p3.py`: the false refusals of point 3 plus the add-and-rewrite cases. `p4b.py` runs `p3.py` against `api_old.py`, the `git show` of 1ba28a8e.
- `p6b.py` with `shas.txt`: the rename count of point 6 over the reflog and `git fsck --unreachable` commits since 2026-10-17 16:20.
- `p7.py`: replays each night commit-file pair as one span through both `_drop_note` versions. 2 notes change, both true drops.
- `oldbound.py`: a pytest plugin that restores `x < a <= y`. Ran with `-n0` on the whole-file and signature files: 27 passed.
- Pins: `pytest tests/rota/test_frame283_*.py tests/rota/test_frame140_*.py tests/rota/test_developer.py -q`: 184 passed.

## (d) Usage

The harness counter fell by about 56k tokens over the review. I cannot split input from output. Output is about 12k of the total.

Stands. The pass closes the s229 wall on both doors and weakens no pin, and finding 1 is one line to fix.

## Re-check of 266aadb0

The commit closes findings 1 to 4 and opens one new false note. 189 pins pass: the 184 from before plus 5 new tests.

- s229 holds. Probe p1 on the night's texts: both doors still name `shorten: bool = False,` at line 441.
- Finding 1 is closed. `_rewritten_heads` now leaves the signature parts out of the place index. Probe p3: the new parameter and the new decorator beside a body rewrite open no note. The five false-refusal cases of point 3 still open no note.
- Finding 2 is closed. Probe p2: the dropped second `@click.option(` is named at line 3 on all three doors.
- Finding 3 is closed. Probe p2: the header-only span names `def f(` at line 0. The docstring is now true.
- Finding 4 is closed by `test_a_whole_file_write_that_drops_two_parameters_of_one_line_names_it_once`.
- Probe p7 replays the night spans with the new code. Only the 2 true drops change, and none of the 93 spans gets a false note.

5. New, `rota/roles/api.py:22012` (`_signature_parts`, the decorator key), medium, CONFIRMED.
   - A decorator now keys on its whole text, and `_rewritten_heads` no longer rescues a decorator. So any edit to the arguments of a decorator opens a span-door note.
   - Probe p8: `default="a"` to `default="b"` inside a multi-line `@click.option(` gives a note. `@click.option("--name")` to `@click.option("--name", default="x")` also gives a note. Both give None on 07887a4b and on 1ba28a8e. The whole-file door opens no note.
   - Click edits its option decorators often. The night replay shows 0 hits today.
   - Fix: key a decorator on its first line again, and make `held` in `_lost_signature` a Counter. The Counter closes finding 2 without the whole-text key.

Probe p8 is `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/79847ec6-3334-49c7-8221-098d6165a403/scratchpad/r283wd/p8.py`. It runs against the worktree, against `api_07887.py` and against `api_old.py`. Usage for the re-check: about 9k tokens.

Stands. The s229 wall stays closed and no pin is weaker. Fix finding 5 before the next night, because a decorator edit is a common planned change.

## Re-check of d9660002

Finding 2 stays closed. Finding 5 is half closed: a one-line decorator edit still opens a false note. 191 pins pass.

- s229 holds. Probe p1: both doors name `shorten: bool = False,` at line 441.
- Probe p7: only the 2 true drops change over the 93 night spans, and no span gets a false note.
- Finding 2 is closed. Probe p2: the `held` Counter names the dropped second `@click.option(` at line 3 on the span door.
- Finding 5, multi-line case, is closed. Probe p8: an edit to an inner line of `@click.option(` gives None.
- Finding 5, one-line case, is open. `rota/roles/api.py:22187`, medium, CONFIRMED.
  - Probe p8: `@click.option("--name")` to `@click.option("--name", default="x")` still gives a span note. 07887a4b gave None.
  - The cause: the first-line key changes, and `_rewritten_heads` now drops every decorator from the place index.
  - Fix: pair decorators by their own index under the owner, separate from the body index. Do not drop them.

Does not stand. A one-line decorator edit is a common planned change, and the span door now refuses it until a ledger note names it.

## Re-check of 0cdca657

All five findings are closed, and no new gap shows. 192 pins pass.

- Finding 5 is closed. `_rewritten_heads` pairs decorators in a separate index under (owner, "@"). Probe p8: the multi-line and the one-line decorator edits give None on all three doors.
- Finding 2 is closed. Probe p2: the dropped second `@click.option(` is named at line 3 on the span door.
- Finding 1 is closed. Probe p3: every false-refusal case gives None, the add-and-rewrite cases included.
- s229 holds. Probe p1: both doors name `shorten: bool = False,` at line 441. Probe p7: over the 93 night spans, only the 2 true drops change.

Stands. The s229 wall is closed on both doors, every probe case is correct, and no pin is weaker.
