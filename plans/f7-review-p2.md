# F7 review, pass 2: commit aae59d4b on f7root

The verdict is READY on the seven points, with one high finding outside them. The high finding is present at the parent cdd02498 too, so pass 2 did not cause it. The review finds 1 high and 4 low findings. The three touched test files give 143 passed. Worktree: `C:/Users/roman/rota_f7`. Line numbers are of `rota/roles/api.py` at aae59d4b. Line numbers in a row are 0-based, as in code.source numbering.

## (a) Verdicts on the points

1. Pass. All 14 shapes of review 1 give the expected answer. The two heads of night 171 each name the darwin branch at line 522 and the XDG return at line 526. See the table in (c).
2. Partly right. The rule is right for a new loop and for a new guard that changes the paths (2d, 2g). The rule gives a false "removal" row for 5 shapes that keep the behaviour (finding 4).
3. Pass. The merge hold returns. The second commit writes an `open` row, and `mergeable` holds on it. The note loses the earlier mistake judgement (finding 5).
4. Pass. The frame 140 refusal has the same syntax tree as at 372cff9f. Its helpers read `drop_notes` only, and no compare entry reaches them. Pass 2 adds no refusal of a commit.
5. Pass for the three named shapes. A changed argument, a widening by `or`, and a renamed local with no use give no row. A renamed local that is used, or a call whose result is now kept, gives a false row (finding 3).
6. Pass. One `git cat-file --batch` reads 20 base files in 43 to 91 ms. 20 single `git show` calls take 928 ms.
7. One recorded case is stale: `L1-AR-judge-a-stray-foreseen-or-a-mistake` in `tests/rota/cases/l1_touch.yaml`. No other case or scene replays the `touch_strayed` prompt.

## (b) Findings

1. api.py 21610 to 21612 (`_lost_in_block`, the definitions). HIGH. CONFIRMED. Outside the points.
   - The k-th old definition of a name pairs with the k-th new one. An old definition with no k-th partner is skipped with `continue`.
   - Probe o1: a class removes its `@x.setter def x`. No row is written.
   - Probe o3: a module removes the `else:` arm that defines `home()` for the non-darwin platforms. No row is written. This is the night 171 class at the grain of a definition.
   - Probe o2: the getter goes and the setter stays. The row names `@property` and `return self._x`, not the definition.
   - The parent cdd02498 gives the same result. Before F7 the note of the write could name these lines. Now the compare replaces the note on a path that parses, so a regression from before F7 is PLAUSIBLE.
   - Fix: name each surplus old definition of a name as a lost definition, and pair by decorators and arguments before order.
2. api.py 21521 to 21523 (`_kin`, the exits). LOW. PLAUSIBLE. Outside the points.
   - A `return` is kept by any `return` in the same block, whatever it returns.
   - Probe o5: `if darwin: return mac()` and `return xdg()` become `return win()`. The row names the darwin branch only. The XDG return stays hidden.
   - Night 171 escaped this rule only because s164 left no `return` at that level. The impact on a real night is not measured.
   - Fix: keep a return as a rewrite only when its new value shares a name or a call with the old value, or when both values are constants.
3. api.py 21526 to 21528 and 21633 to 21643 (`_kin` for a call, the assignment pass). LOW. CONFIRMED. Point 5.
   - Pass 2 pairs a renamed binding by its value. Each later use of the renamed name is lost.
   - Probe 5c: `tmp.close()` becomes `fh.close()`, and the row names `tmp.close()`. A renamed loop target, a renamed name in a test and a renamed accumulator each give a row (5c2, 5c3, 5c4).
   - Probe 5a3: `go(a)` becomes `res = go(a)`, and the row names `go(a)`.
   - The cost is one Architect wake for each batch, because `touch_strayed` wakes once for each batch. His page and the summary after a merge name up to three of the false lines.
   - A mistake judgement on a rename costs one more Developer wake and one more commit, and the Developer can undo the rename.
   - Fix: build a rename map from the bindings that pair by value, and compare each key after the rename. Read `x = call()` as a rewrite of the bare `call()`.
4. api.py 21549 to 21551 and 21593 to 21598 (`_lost_in_block`, pass 3). LOW. CONFIRMED. Point 2.
   - A statement under a new `if True:`, under a guard that its own code makes true, or in a new `for` over one item gives a row (2a, 2b, 2c, 2e).
   - A statement in both arms of a new `if` and `else` gives a row, and it runs on every path (2f).
   - A call in the `else` of a new `raise` guard gives a row (2d). The same guard with no `else` gives none (2d2). The behaviour is the same.
   - Each row says that a present line is removed. The prompt asks the Architect whether a criterion asks for the behaviour to go. A "mistake" then asks the Developer to put back a line that is there.
   - By the purpose of law 12, 2d and 2g carry a real review question, and 2a, 2b, 2c, 2e and 2f do not.
   - Fix: look for the statement in each arm of a new compound statement. Keep it when every arm holds it. Else name it "now under" the new header, not removed.
5. api.py 21228 to 21232 (`_removal_strays`). LOW. CONFIRMED. Point 3.
   - Probe 3a: the removals of the first commit are judged a mistake. The second commit keeps them gone and removes `if force_posix:`. The new open row names all three removals and does not say that two are judged a mistake.
   - The commit result has no `removals judged a mistake` key. Its note tells the Developer to end the session.
   - The Architect judges the row again. A foreseen judgement then reverses the earlier mistake with no sign on his page.
   - Fix: write the pieces that the last mistake covers into the new note as already judged a mistake, and keep the mistake note in the commit result.

## (c) Probes

All probes of this pass are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b3bc8a66-bd69-4749-a050-07bdd1893c24/scratchpad/f7rev2/`. Each ran from `C:/Users/roman/rota_f7` with `D:/repos/rota/.venv/Scripts/python.exe`.

- `f7rev/pipeline.py` of review 1, run again at aae59d4b: the 14 shapes through `_removal_entry` and `_gone_statements`. The first table below is its result.
- `shapes2.py`: the two heads of night 171, the 8 shapes of point 2 and the 11 shapes of point 5, through `_removal_entry` and `_gone_statements`. The labels in the file differ from the labels here by prime marks. The file label 5c3 is 5c4 here.
- `twocommits.py`: the fixture of `test_f7_removal_compare.py`. It runs `code.commit`, then `batches.judge_touch` with a mistake, then a second `code.commit`. It applies the writes, then reads the hold query of `mergeable` and the two predicates. Case 3a keeps the first removals gone. Case 3b puts them back. Both give an `open` row at the new head and an Architect wake.
- `outside.py`: probes o1 to o5. `parent.py` runs `outside.py` against `api.py` of cdd02498.
- `timing2.py`: a git repository with 20 changed files of 180 lines, 5 runs. It times `git diff --name-only` (32 to 174 ms), `_base_texts` (43 to 91 ms), 20 compares (166 to 450 ms), and 20 single `git show` calls (928 ms).
- Point 4: a syntax tree compare of `_unread_drop_refusal` and 13 helpers between 372cff9f and aae59d4b. Only `_gone_statements` changed, and its change reads the `compared` key. Only `_removal_entry` sets that key. The only new `raise` in the diff is in `batches_judge_touch`.
- The suite: `pytest` on `test_f7_removal_compare.py`, `test_frame140_commit_beside_note.py` and `test_frame283_removal_on_ruling.py` gives 143 passed in 113 s.

| Shape of review 1 | Expected | aae59d4b |
|---|---|---|
| 1 branch gone, body under another branch | removal | finds `elif x == 2:` |
| 2 early return replaced by raise | removal | finds `return None` |
| 3 renamed local, no use | none | no row, right |
| 4 merged `if` and `elif` | none | no row, right |
| 5 dead branch deleted | none | no row, right |
| 6 docstring change | none | no row, right |
| 7 darwin branch, new branch on another condition | removal | finds the darwin branch |
| 8 return in a new `with` | none | no row, right |
| 9 `assert` and `import` gone | removal | finds both |
| 10 init gone, a later rebind | removal | finds `total = 0` |
| 11 `if a:` gone, `if a and b:` stays | removal of `if a:` | finds `if a:` |
| 12 `else` arm gone | removal | finds `v = 2` |
| 13 XDG-like return gone, new return with the same first line | removal | finds `return os.path.join(` |
| 14 guard gone | removal of the guard | finds `if c:` |
| night 171, a46638f3 and 62199a7b | darwin and XDG | finds both, lines 522 and 526 |

| Point 2 and 5 shape | Result | Right by the purpose of law 12 |
|---|---|---|
| 2a under `if True:` | row | no, false row |
| 2b under `if debug:`, after `debug = True` | row | no, false row |
| 2c under a guard that its own code makes true | row | no, false row |
| 2d in the `else` of a new `raise` guard | row | yes in purpose, wrong words |
| 2d2 the same guard, no `else` | no row | yes |
| 2e in a new `for` over one item | row | no, false row |
| 2f in both arms of a new `if` and `else` | row | no, false row |
| 2g in a new loop over many items | row | yes |
| 5a call, changed argument | no row | yes |
| 5a2 assigned call, changed argument | no row | yes |
| 5a3 call result now bound | row | no, false row |
| 5b widened by `or` | no row | yes |
| 5b2 `x == 1` to `x in (1, 2)` | row | defensible |
| 5b3 `x is None` to `not x` | row | defensible |
| 5c to 5c4 renamed local with uses | row | no, false row |

## (d) Usage

The harness does not show exact counts. The estimate is about 90k input tokens in context and about 15k output tokens, a total of about 105k.
