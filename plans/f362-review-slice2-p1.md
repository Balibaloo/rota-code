# Review of frame 362, slice 2, pass 1: commits 47a49ba7 to 0d35f2c6

Verdict: fix. The edge, the reader and the wake are right. The surface door change is wrong, and it must change before a dry run. Counts: 1 high, 3 medium, 2 low.

## (a) The verdict on each point

1. One writer: holds. `criteria.guess_ruling` has one writer, `criteria.respecify`, and `specify` takes the column default. The `refs` row of kind `ruling` from `criteria` comes from `criteria.respecify` only. `_adopt_rows` serves `glossary_terms`, `constraints` and `model_areas`, never `criteria`.
2. The stamp at `specify`: CONFIRMED owed. A criterion that the Terminologist writes after his ruling is owed, also when its surface is already in the new set. The brief's fix is wrong alone. Finding 3 gives the fix.
3. The order: `rulings` rowid, by `_verdict_rank` (the MAX rowid of the landed rows of the verdict). A second contest gives one owed write, on the newest verdict, after its set exists. A dropped item and a retired criterion are never owed.
4. The hold: nothing names the hold while it holds. A spent key lets the batch start on stale criteria. Then the page says "nothing moves", and that is false. Findings 4 and 5.
5. The surface door: the change accepts any import on an owed criterion, a module that does not exist included. The next door still refuses a test of the new set. Findings 1 and 2.
6. The wake: holds. The push holds the new grains, his verbatim words, the old surface and the call to send. `terminologist/criterion_repair.tools` holds `criteria.respecify`. The comment at `runner.py` 391 is right: `park_criterion_relay` already routed a criterion ruling from any page through `ruled_criteria`.
7. The changed test: the criteria of bg_2 are owed because of his batch-line contest. Criteria always come before the batch, because `grouping` needs criteria. So the change does not hide point 2. It shows the cost of finding 3: three wakes for a contest that only removed a test file.
8. The checks: on the `w5` copy, `owed` is None on c1 to c3, and `criterion_owed` gives m26 with `string.py::_foldline`. The 8 places left are safe for a dry run, except after a spent key. Dry run 7 would hit place 3, `_criterion_surface_pushes`, next. `casestatus` found no recordings in the worktree. No brief or tools file changed, so I expect 0 stale cases.

## (b) Findings

1. `rota/roles/api.py:12711`, high, CONFIRMED. On an owed criterion, the import door accepts every import. The probe encoded `from nowhere import calculate_tip` on an owed criterion, and the encode landed. On the same criterion without the ruling, the door refused it. Such a test dies at collection, and the tipsU quarantine is the case the door exists for. The door also accepts a module outside the batch's touch set. Fix: on an owed criterion, refuse the encode with one line that names the Terminologist's rewrite, and keep the import door shut.
2. `rota/roles/api.py:12740`, medium, CONFIRMED. The door change does not let a test of the new set land. The probe encoded `from billing import split_tip` on an owed criterion with the surface `main.py::calculate_tip`. The import door let it through. Then the next door refused it with "this test never calls 'main.py::calculate_tip'". Dry run 7's s185 called `_foldline`, so its 9 refusals move to this door (PLAUSIBLE, by the same code path). The report says that the change has no test. Fix: the refusal of finding 1 covers it, with a test of `tests.encode` on an owed criterion.
3. `rota/roles/api.py:7434` (`criteria_specify`) and `rota/core/scheduler.py:2126`, medium, CONFIRMED. `specify` writes the empty stamp. So every criterion that the Terminologist writes after a ruled set is owed, also on the new surface. The probe wrote c1 and c2 on `string.py::_foldline` after m26. `tests_missing` gave `[]`, and `criterion_owed` woke for c1, one criterion for each wake. The brief's fix, a stamp of the newest verdict at write time, hides dry run 7. Its s150 wrote c1 to c3 on `q_split` after m26, and its push showed no set. Recorded cases: 1 case, `l1_architect.yaml` line 78, holds a ruled guess beside a criterion. It replays the Architect, so it reads no hold. Fix: the `tick:criteria` push shows the item's ruled set, and `specify` stamps the verdict it showed (open question 1 of the report).
4. `rota/core/scheduler.py:2150` and `rota/roles/principal.py:2563`, medium, CONFIRMED. A spent key lifts the hold, and the batch starts on the stale criteria. `criterion_owed` ignores the quarantine, so the door of finding 1 stays open for that criterion. The probe quarantined `terminologist|tick:criterion_owed|c1,m26`. Then `tests_missing` gave `b1`, and the page said "Stuck: the team could not finish a step for c1, m26 after 3 attempts. Nothing waits on you, and nothing moves until that is cleared." The words are the fallback, the line names rota's ids, and "nothing moves" is false. Fix: slice 3's park page names the owed criterion and holds the batch, and `TICK_WORDS` gets an entry for the kind.
5. `rota/core/predicates.py:1013`, low, CONFIRMED. While the batch is held, the page says "Building: 1 change in progress." No line names the hold or the criterion. The Terminologist's wake is live then, so the hold is not silent for long. Fix: slice 3, as the design says.
6. `rota/core/scheduler.py:2047` (`code_line_basis`), low, PLAUSIBLE. The basis reads every ruled `touch_guesses` row of the item at any `item_ver`, and the `batch_touch` rows of every batch, abandoned ones included. After an amendment, the ruled set of the old version stays the basis. Then the criteria of the new version are owed, and the push shows the old grains as "the code the request touches now". No probe ran. Fix: read the guess rows at the item's current version and the batch rows of batches that are not abandoned.

Outside the points:

- The related set gives 17 failed, 574 passed, 5 skipped and 2 xfailed in the worktree. All 17 are L1 and L3 cases that say "STALE ... no recording". The worktree has no real `tests/rota/cassettes.db`, which is 2.1 GB in `D:/repos/rota`. Two of the 17 pass in `D:/repos/rota`, whose `rota` and `tests` equal `ad7bf4e6`. Without L1 and L3, the set is 568 passed with 0 failed. I cannot reproduce the report's 575 here.
- The test run made an untracked stub `tests/rota/cassettes.db` of 135 KB in the worktree. Git ignores it, and I did not remove it.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/0ff6bcd7-73e0-40b9-af75-01c8fdc9ed9a/scratchpad/r362s2/`. Each ran from the worktree with `PYTHONPATH` on the worktree.

- `dry7.py`: opens `C:/Users/roman/rota_p362c/scratch/dry7_w5.db` immutable, copies it to memory and adds the column. It prints `owed` and `criterion_owed` on c1 to c3, `tests_missing` (`[]`) and the wake (`c1, m26`).
- `door.py fresh` and `door.py owed`: the fixture of `test_desk_guards.py`, without and with a ruled set m26 on `billing.py::split_tip`. Each encodes a test of the new set, and a test that imports the old name from a module that does not exist.
- `hold.py`: the fixture of the new test file. It reads `tests_missing` and `principal._render_state` during the hold and after a quarantined key, and it reads the `quarantined` wake.
- `fresh.py`: criteria written after m26 on the new surface. It reads `criterion_owed`, `tests_missing` and the wake.
- The planted fault: `return None` at the head of `scheduler.criterion_owed`. The new file and `test_request_page.py` gave 5 failed and 71 passed. The related set without L1 and L3 gave 5 failed and 568 passed. The 5 are 4 tests of `test_frame362_owed_criterion.py` and `test_a_contest_of_the_prediction_reaches_the_architects_annotate`. I copied the original file back, and `git status` is clean.
- `pytest` on the new file and `test_request_page.py`: 76 passed, 1 skipped. The skip is the `w5` test, because its copy path is relative to the worktree.
- `python -m rota.tools.casestatus --model qwen3:8b`: 203 never measured, because the worktree has no recordings.

## (d) Usage

This is an estimate, because the session shows no counter. Input is about 90k tokens of context, output is about 15k, and the total is about 105k.
