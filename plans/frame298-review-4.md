# Frame 298, review 4: pass 4 at 9cbe43be and pass 2b at f9f5cd19

Worktree `C:/Users/roman/rota_r298` at f9f5cd19. Read-only. The gate ran
from the worktree. Date 2026-10-18.

Verdict: pass 4 and pass 2b hold on the points, with two high findings.
The cancel flag of the hand list can take a later ruling's cancel. The
rewrite brief leans on `disputed`, and the detector fills no list on the
night's own sentence shape.

## (a) The verdict on each point

1. Confirmed. `_git_truth` finds the merge by the subject "rota: deliver
   <batch id>", keeps it only when `batches.head_commit` is an ancestor of
   the second parent, and diffs `<merge>^1 <merge>`. On night 156 the
   section prints `absent: touch_guesses`, `M0: 0 of 6 sign-off pages carry
   a code line`, `M1: absent`, `M2: absent`, and a hand list of 7
   request-line rulings. It prints no truth line for bg_1, because the
   truth print sits under the `touch_guesses` branch (finding 4). A direct
   call gives bg_1's six paths with its head and None with a wrong head. A
   merged item with no truth leaves M1's denominator and prints in the
   count beside it. The design's "over five merged items" then counts
   items with a truth only (finding 6).
2. Confirmed. With a ruling set after the first and a second own set at
   version 2, M1 reads the version 1 set with `ruling_id = ''`. A symbol
   grain counts by its file. An item with a ruling set only counts as a
   miss with `guess=-` (finding 2).
3. Confirmed with one defect. The list holds every landed contest or
   revise on a request line, a `guess:` key or a stamped batch id, with
   `contested` from the landed verdict map and `cancel` from the night
   log, capped at 30 with "<n> more unread". The scan for the cancel runs
   to the next line of the same page, so a later ruling's cancel can land
   on an earlier ruling (finding 1). The log is not always beside the
   database. The read copies the database by hand to `clickI_night<N>.db`
   (operating facts, line 182), and the log is the launch's redirect. An
   unrenamed `clickI.db` finds no log. The header then prints `log: -`,
   and every row prints `cancel=?`.
4. Confirmed. `guess.md` lines 17 to 19 hold review 3's three sentences
   word for word. The fourth text and its live read of `touch_guesses`
   are gone from `rulings_rule`. A page with no code line takes text 3.
   The pin `test_a_guess_after_the_send_leaves_the_refusal_at_text_3` sends
   the page, writes the guess, lands the reply, and gets text 3. The three
   test files give 48 passed, 1 skipped.
5. Read from `case_runs`. The annotate seat on qwen3:8b made one
   `batches.annotate` call in each of five runs, with exactly
   `src/catalog/pricing.py` and `tests/test_pricing.py`. On qwen3.5:9b the
   first call of each run held the same two paths. Runs 1, 3 and 4 added
   four symbols. Runs 2 and 5 then called again with `tests/test_pricing.py`
   only, and the tick wake upserts, so the rows keep both paths. No run
   named `src/billing/charges.py`. The rewrite case's two misses are not
   the fixture's. The recorded prompt carries `"disputed": []`, and
   `disputed_paths` returns `[]` on the case's words and on night 156's
   m200 words. The night runs the same detector, so the misses recur
   (finding 3).
6. Outside: findings 4 to 7.

## (b) Findings

1. **The cancel scan runs past the next reply.**
   `rota/tools/nightreport.py:278-285`. Severity high. CONFIRMED: on night
   156's log with line 103 removed, `_cancel_after` for the m122 ruling
   returns "yes" from line 150, `do:cancel: abandoned bg_3`, which is the
   m191 ruling's cancel. The scan stops only at a line of the same page,
   and the log has no second `[m124]` line. Night 156 masks it because the
   bg_2 cancel comes first. A night with two rulings on one item and one
   late cancel prints a false M4 count. Fix: end the scan at the next line
   that starts with `[`.
2. **An item with a ruling set only counts as a miss.**
   `rota/tools/nightreport.py:338-359`. Severity low. CONFIRMED: the probe
   deleted it_2's own set and kept its ruling set. The line reads
   `it_2 guess=- truth=src/b.py,tests/test_b.py M1=miss M2=miss`. This
   shape is reachable: a page with no code line, text 3, a contest on the
   key, and the relay's set under the ruling, after which `tick:guess`
   stays false. The Architect never guessed, and the measure says it
   missed. Fix: print `no own guess`, keep the item out of both counts, and
   add it to the count beside the denominator.
3. **The rewrite brief leans on a list the night's words do not fill.**
   `rota/roles/prompts/architect/guess.md:16-19`,
   `rota/core/runner.py:1718`, `rota/core/runner.py:2053-2059`. Severity
   high. CONFIRMED: `disputed_paths` gives `[]` for the case's words, m191's
   sentence "Line 1 also names the options and defaults test files", and
   for m200's "the options and shell completion test files". It gives
   `['tests/test_options.py']` for "names the options test file". The
   plural list before "test files" misses. The brief says "The paths under
   `disputed` are the ones the words call wrong", so the seat reads an
   empty list as nothing wrong. Two of five qwen3.5:9b runs kept
   `tests/test_options.py`. The case's `code.source` refusals cost turns
   and do not cause this. Fix: teach `disputed_paths` the form "the A and B
   test files", one path per word before "test files", and give the case
   `project_root` so the seat reads source as on the night.
4. **The truth print waits on the guess table.**
   `rota/tools/nightreport.py:330-362`. Severity low. CONFIRMED: night 156
   prints no truth for bg_1, and its truth is in the repository. Design
   5.1 calls the truth independent of the guess, and 5.2 asks for a
   recompute on old nights, which ran in a scratch script. Fix: print one
   line per merged item with its truth whenever `batches` exists, and
   `guess=absent` without the table.
5. **The log is found by one name pattern.**
   `rota/tools/nightreport.py:808-811`. Severity low. CONFIRMED: the test
   with a moved repository and no log prints `cancel=?` on every row. A
   database read as `clickI.db`, or from a copy with another name, gives
   the same. A log that holds no `do:cancel` line of the known shape gives
   "no" with no warning. Fix: none in code. The read's checklist names
   `--log`, and the header line shows which log the section read.
6. **The design's five items and the tool's denominator differ in words.**
   `plans/frame298-design.md:473-477`. Severity low. PLAUSIBLE: the design
   says "over at least five merged items", and the tool counts items with
   a truth. A night read after the next launch has no truth, and its items
   leave the five. Fix: amend 5.3 to "five merged items with a truth", and
   name the read-before-next-night rule beside it.
7. **The gate from the review worktree ran without the register.**
   `C:/Users/roman/rota_r298/tests/rota/cassettes.db` is absent. Severity
   low. CONFIRMED: the gate printed `7 failed, 4104 passed, 207 skipped`,
   `new reds (0)`, `stale: the register is absent`, and
   `baseline stored at f9f5cd1`. The previous gate at 1869cab4 had 32
   failed and 4394 passed with the register. Fix: run the frame's closing
   gate from a worktree that holds the register, and treat this stored
   baseline as partial.

## (c) Probes

All inline probes ran from `C:/Users/roman/rota_r298` with the venv
Python, as Bash heredocs, and left no file. One probe is a file.

1. `git show --stat` of 9cbe43be and f9f5cd19, and `git show f9f5cd19` on
   `api.py`, `guess.md`, `test_guess_page.py` and `test_guess_route.py`.
2. `python -m rota.tools.nightreport D:/repos/rota/.rota/clickI_night156.db`,
   section 12 only.
3. Night 156's `batches`, `config` keys, and the pages with their cause
   verbs, read with `mode=ro`. `git log --merges` and
   `git merge-base --is-ancestor bc1acb6 2e7dc8a` in the sample repository.
4. `_git_truth` on the sample repository for bg_1 with its head, with no
   head, with bg_3's head, and for bg_2.
5. `_cancel_after` on the real night 156 log for the m122 ruling, and on
   the log with line 103 removed. The 40 lines that start with `[`.
6. `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/050a41e6-f49a-4d93-9e2f-e30db5ccd91e/scratchpad/r298_4_probe_sets.py`:
   the test fixture plus a ruling set at version 1, an own set at version
   2 for it_1, and it_2's own set deleted. It prints M1, M2 and the item
   lines, then removes its temporary night.
7. `case_runs` and `cassettes` of `D:/repos/rota/tests/rota/cassettes.db`,
   `mode=ro`: both cases, every run, the calls and refusals by regex, the
   `wrote` counts, and the rewrite case's prompt around `disputed`.
8. `disputed_paths` on the case's words, on m200's words, and on a
   one-file sentence.
9. `pytest tests/rota/test_nightreport.py tests/rota/test_guess_page.py
   tests/rota/test_guess_route.py -q` with `ROTA_MODEL=qwen3:8b`: 48
   passed, 1 skipped.
10. `python -m rota.tools.gate` from the worktree, 242 s.

## (d) Usage

Estimated from the turn sizes. Input about 420k tokens over 15 tool
turns, with the context near 80k at the end. Output about 15k tokens.
Total about 435k.
