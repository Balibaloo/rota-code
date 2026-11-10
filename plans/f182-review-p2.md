# Review of pass 2, frame 182: the kind of a criterion from rows the Terminologist writes

Worktree `C:/Users/roman/rota_p182`, commits 69f466b9, 1672b583, 00928daa
and 129075bd on 1101f86a. Read-only. Reviewer: a sub-agent of session
33f037c1, 2026-11-10.

## (a) The verdict

Fix before the pick. One high finding, about 15 lines: the tie has one
writer, `criteria.specify`, and that writer runs once per criterion. On a
run where the criteria come before his ruling, the set at that moment is
the first guess, the right id is refused, and `criteria.respecify` cannot
add the tie later. On dry run 8's rows the pass holds: c1 to c3 read
`unknown`, c3 reads `kept` after `keeps=cw_99502ef494ad`, the wrong id is
refused with the 16 right ids, and the claim is silent.

The points, one line each:

1. Confirmed. c1, c2 and c3 read `unknown` on the copy. c3 reads `kept`
   with cw_99502ef494ad after the column write. `change` on files with a
   reaching constraint and no commitment, and `unknown` on `k0` only, are
   pinned by the tests and ran green.
2. Confirmed. cw_7039d1d2d899 binds `content_line.py`. c3 restates
   cw_99502ef494ad, which binds `string.py`. The door accepts the right id
   and refuses the wrong one. The read of dry run 8 named the wrong id. No
   high here.
3. Confirmed. Ruled: 2 files, 16 ids. No ruling with a live batch: the same
   2 files. No ruling and no live batch: the first guess, 29 files, 14 ids,
   and the right id is refused. No guess: an empty set, and every `keeps`
   is refused. See finding 1.
4. Confirmed. The original has no `criteria.commitment_id`. `connect` runs
   `commitment_columns`, the copy gets the column, and `criterion_kind`
   reads it.
5. Confirmed. The block renders to 3,599 characters of a 20,000 cap, with
   no cut. The 16 ids stand intact in a table of id, text and witness.
6. Confirmed. The paragraph is three sentences in the prompt's shape. Five
   register cases run the criteria tick, and casestatus marks all five
   STALE.
7. Confirmed. The note reaches the reply of a real `tests.encode` call and
   the row is staged. The note is enough until dry run 9 counts it.
8. Confirmed. Both refusals are silent on a claim. With the claim check
   taken out, `kept_red` goes red.
9. Confirmed. Five new names, none at 1101f86a, each defined once.
10. The two files: 81 passed, 4 xfailed. The related set: 602 passed, and
    the L1 and L3 part reruns with the register as 15 passed, 5 failed, of
    which 3 are in the baseline and 2 are new STALE lines.

## (b) Findings, by severity

### 1. High. The tie is unreachable after the first `criteria.specify`. CONFIRMED.

`rota/roles/api.py` lines 4821 to 4853, `item_commitments`, and line
8275, `criteria_respecify`, which takes no `keeps`.

`item_commitments` reads the ruled code line, else the rows of the live
batches, else the newest guess. `tick:criteria` does not wait for a
ruling (`rota/core/scheduler.py` lines 446 to 452), and `criterion_owed`
exists because dry run 7's c1 to c3 were written under an older set. On
that path the newest guess is the first guess of the Architect. The probe
`probe_guess.py` removed the m26 rows and set bg_1 aside on a copy of dry
run 8: the set is 29 files and 14 ids, cw_99502ef494ad is not in it, and
`_kept_commitment` refuses it with the 14 other ids. With no guess at all
the set is empty, and every `keeps` is refused with `NO_COMMITMENT_WORDS`.

After his ruling the owed wake rewrites the criterion with
`criteria.respecify`, and that door has no `keeps`. The push of the bound
block is gated on the wake kind `tick:criteria` (`rota/core/runner.py`
line 5095), so the owed and repair wakes show no ids. The tie is lost for
the life of the item, the kind stays `unknown`, and both walls stay open
on that run. The refusal fires on a prediction, the guess, which the
composition forbids.

Fix: give `criteria.respecify` the same `keeps` with `_kept_commitment`,
and push `CRITERIA_BOUND_KEY` on `tick:criterion_owed` and
`tick:criterion_repair` too.

### 2. Low. The criteria wake dies on a raise in `item_commitments`. PLAUSIBLE.

`rota/core/runner.py` lines 5103 to 5108. The call stands outside a
`try`, unlike `code.callables` at line 5087. `code_line_basis` reads
`items.version` and `rulings`, and `stated_commitments` reads the
harvest tables. A raise there ends the wake before the seat reads it.

Fix: wrap the call as `code.callables` is wrapped, and push nothing on a
raise.

### 3. Low. The seat and the Critic read two sets. PLAUSIBLE.

`rota/roles/api.py` line 4829 says that the seat and the Critic read one
set. The seat reads the code line of the item through `item_commitments`.
`criterion_kind` reads `_bound_rows` of the batch at line 23869, the
predicted rows and the diff. A batch whose plan differs from the ruled
line gives the two readers two sets, and a `keeps` the seat accepted may
name a commitment that does not bind the batch. The kept tie still gates,
because the tie is read before the bound set.

Fix: say in the docstring that the sets differ, or read the set of the
batch in `_kept_commitment` when a live batch exists.

### 4. Low. Five register cases go stale, two of them new reds for the gate. CONFIRMED.

casestatus with the main register under the prompts of the worktree: 5
stale, `L1-TE-specify-criteria`, `L1-TE-a-new-behaviour-is-a-new-callable`,
`L1-TE-a-docstring-ticket-gets-a-docstring-criterion`,
`L3-scope-becomes-a-ticket-with-criteria` and
`L3-a-challenge-reaches-the-role-that-can-answer-it`. The L1 and L3 test
files with the related `-k` filter print STALE for the first, the fourth
and the fifth. The baseline `.rota-gate.json` (2026-11-08 17:34, 33
failed, stale empty) holds the fifth as failed and none of the others.
The report says 0 failed on the related set. That run did not read the
register.

Fix: re-earn the five cases after the pick, with the fix of finding 1 in
the same prompt.

### Outside the points

- The push lists 16 commitments and 6 of them are docs commitments on
  custom components and parse errors. A 9b seat picks one of 16. The
  report's open question 2 names it. Not a defect, a measurement for dry
  run 9.
- `_base_verdict_refusal` now runs the body at the base on every
  `unknown` criterion, about 1 s per body on icalendar, for the note
  only. Pass 1b had removed that run. Low, and the report says so.
- The first related-set run from the worktree, with no `ROTA_DEV_DB`,
  created an empty register at `tests/rota/cassettes.db` (ignored, not
  tracked) and gave 21 red L1 and L3 cases. The worktree holds no
  register, so a run there needs `ROTA_DEV_DB`.

## (c) Probes

All probes are in
`C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/33f037c1-f639-4fa5-8bd4-0cc91eeff019/scratchpad/f182p2/`,
run with `PYTHONPATH=.` from the worktree root. The copy `dry8.db` was
restored from the read-only original after each write.

- `probe_rows.py`: `init_db` on the copy, `_has_column` True,
  `criterion_kind` on c1, c2, c3 all `unknown`; the `criteria` rows; the
  bindings of cw_7039d1d2d899 (`content_line.py`) and cw_99502ef494ad
  (`string.py`); `item_commitments` on `folds_long_lines` gives 2 files
  and 16 ids; after an UPDATE of the `commitment_id` of c3 to
  cw_99502ef494ad, c3 reads `kept`; `_bound_rows` on bg_1 gives 19 rows,
  16 with a party, and `k0` absent; the block as JSON is 4,290 characters.
- `probe_push.py`: `_render(block, PUSH_CHARS)` is 3,599 characters, no
  cut, 16 ids intact; `_kept_commitment` through a real Terminologist
  seat refuses cw_7039d1d2d899 with the 16 ids and returns
  cw_99502ef494ad; `push_working_set` on the real `tick:criteria` wake
  holds the key with 16 rows; s152 is `tick:criteria` on
  `folds_long_lines`, s153 is `tick:grouping`; the ruling r_m24 is landed
  with verdict m26; bg_1 is `deferred`.
- `probe_sets.py`: the original has no `commitment_id` column; the ruled
  set, the predicted set and the empty set.
- `probe_guess.py`: m26 rows removed and bg_1 abandoned: 29 files, 14
  ids, right id absent, refused in 337 characters.
- `fault_claim.py`: a pytest plugin that reads every batch as unclaimed
  inside `_base_verdict_refusal`. With `-k claim`: 2 failed (`kept_red`
  and `change_green`), 20 deselected.
- `git grep` at 1101f86a for `item_commitments`, `_kept_commitment`,
  `NO_COMMITMENT_WORDS`, `BASE_GREEN_NOTE`, `CRITERIA_BOUND_KEY`: no hit.
  `grep -c` at HEAD: each once.
- `casestatus.txt`: `rota.tools.casestatus --model qwen3:8b` with
  `ROTA_DEV_DB` on the main register, about 14 minutes while the L1 run
  held the register: 29 failing, 20 provisional, 5 stale, 151 green.
  Without the register it printed 205 never measured.
- `l1l3.txt`: the L1, L3 and L3R files with the related `-k` filter and
  the main register: 5 failed, 15 passed, 185 deselected in 585 s.

## (d) The counts and the time

- `tests/rota/test_frame182_base_verdict.py` and
  `tests/rota/test_scene_two_batches.py`, `-n 0`: 81 passed, 4 xfailed in
  98 s.
- `tests/rota` with the related `-k` filter (encode, harness, challenge,
  base, tests_missing, criteria), `-n 0`, no register: 21 failed, 602
  passed, 10 skipped, 2 xfailed in 425 s. The 21 are L1 and L3 cases.
- The same L1, L3 and L3R part with the main register: 5 failed, 15
  passed in 585 s. Three are in the baseline, two are new STALE.
- Started 01:12, written 01:45, about 33 minutes.

## (e) What I did not read

- The size of the whole wake of s152 with the new block. The block alone
  is 3,599 characters, and the wake holds nine other blocks.
- Whether `tick:criteria` can fire before `tick:guess` in the band order.
  The no-guess case of finding 1 is plausible, not confirmed.
- `criteria.respecify` and whether its UPDATE keeps `commitment_id`. The
  report says it does.
- The gate. The brief said not to run it.

## (f) Usage

Input tokens: about 105k. Output tokens: about 16k. Total: about 121k.

## Second look, 23b78d07

Pick. The high and both lows of pass 2 are closed. One new low, in a path no case renders. Seven register cases are stale, so re-earn them in the pick's prompt.

### (a) The points

1. Closed. `test_after_his_correction_respecify_lands_the_tie_refused_under_the_guess` passes: `keeps=cw_99502ef494ad` is refused under the guess, c3 reads not kept, the ruled line lands, `criteria.respecify(..., keeps=)` returns the id, and `criterion_kind` reads `(KEPT, id)` from `criteria.commitment_id` (api.py 23924 to 23928). One door: `_kept_commitment` has two callers, api.py 7544 in specify and 8387 in respecify.
2. Confirmed, with one gap. The guard is `{"criteria.specify", "criteria.respecify"} & have` and `have = set(sb.functions())` (runner.py 4968 and 5105). The doors live in `criteria.tools` and `criterion_repair.tools`, so the wakes are `tick:criteria`, `tick:criterion_repair`, `tick:criterion_owed` and a relay parked to `criterion_repair` (runner.py 395 to 422). The `try` pushes nothing on a raise, and `test_a_raise_in_the_bound_read_does_not_end_the_wake` pins it. The gap is finding 1.
3. Confirmed. The pair in order with `-n 0`: 60 passed, 4 xfailed. `_CUT_COUNTS` runs inside `if col in TIMED` only, and TIMED is `test_runs.output`, `test_run_journal.output`, `turns.user`, `turns.system`. The tests whose subject is the count (`test_render_cut`, `test_silent_cuts`, `test_runner` 2519, `test_night46_context` 136) read live strings, not `_clocked`.
4. Confirmed. Three sentences, imperative, the voice of `criteria.md` lines 30 to 31. The key text equals `CRITERIA_BOUND_KEY` (runner.py 4552).
5. Confirmed. `refs_item`, `_tie_reply`, `TIE_HELD_WORDS`, `_CUT_COUNTS`: no hit at 129075bd.
6. `test_frame182_base_verdict.py`: 28 passed. The scene pair: 60 passed, 4 xfailed. The `-k` run with `-n 0`: 391 passed, 17 skipped, 8 xfailed, 0 failed in 423 s. casestatus read-only on the main register: 7 stale. The five of pass 2, and two new from the prompt edit of 23b78d07: `L1-TE-a-ruled-criterion-is-respecified-and-the-tester-told` and `L1-TE-repair-the-criterion-the-tester-cannot-encode`.

### (b) Findings

1. Low. `rota/roles/api.py` 4858 to 4877, `refs_item`, and `rota/core/runner.py` 5105 to 5112. A relay parked to `criterion_repair` carries a message id in its refs. `refs_item` reads items, tickets, criteria, tests and batches, not messages, so the wake holds `criteria.respecify` and sees no bound block. CONFIRMED: `refs_item(conn, ["m10"])` on the dry run 8 copy returns `''`, and `item_commitments(conn, "")[1]` is `[]`. Fix: add a messages row to `refs_item` that reads `body_refs` and resolves the criterion ref.
2. Low. `rota/testkit/scenes.py` 1743. `[^:\n]+` stops at the first colon, so a CUT title that holds a colon keeps its raw counts. PLAUSIBLE: no title with a colon was seen. Fix: `(CUT .+?: )`.

### (c) Probes

Worktree `C:/Users/roman/rota_f182r2` at 23b78d07. The `refs_item` probe is a heredoc in the transcript. It copies the review's `dry8.db` to the scratchpad as `f182r2_dry8.db` and calls `refs_item` on an item, a criterion and a message ref. casestatus ran with `ROTA_DEV_DB=D:/repos/rota/tests/rota/cassettes.db --model qwen3:8b`. `git grep` at 129075bd for the four names. The three pytest runs above, each `ROTA_MODEL=qwen3:8b -n 0`.

### (d) Usage

Input tokens: about 62k. Output tokens: about 9k. Total: about 71k.
