# Frame 298, review 2: pass 3, the route, at 30c4a121

Reviewer on Opus, 2026-10-18, read-only on `C:/Users/roman/rota_r298` at
30c4a121. The brief is `f298_review2_brief.md` in session 050a41e6's
scratchpad. The design is `plans/frame298-design.md`, section 3 as amended.

Verdict: the route holds on the wall's case, and three highs stay open.
The door sits where design 3.1 puts it. `land` writes no `items` state for
a `guess:` key, and `cancel` stays silent on night 156's rows. The cue's
port is exact and refuses no recorded landing case. Tonight no send writes
the `code:` stamp, so a live batch's correction goes to the guess row, and
nothing reads a guess in the annotate path. The brief tells the Architect
to keep the paths the principal called wrong in 9 of 19 in-sample faults.

## (a) The verdict on each point

1. Holds. The door is at `api.py:10072`, after the team's-note door
   (10039) and before the batch-line door (10141). On a copy of night
   156, the moved reading lands `bg_3: contest`, the item stays
   `approved` at `approval_ver` 3, `cancel` returns `[]`, bg_3 stays
   `running`, and `guess_target` is absent for a batch target.
2. Tonight a page carries no stamp. An off-page `guess:` ruling under a
   live built batch keeps the key, `land` reads the latest `touch_guesses`
   row live, and the relay keys `guess`. Design 3.5 does not hold tonight.
   The design review's high 2 returns in `land`'s fallback. The one write
   is `notes["code"]` beside `notes["stamped"]` at `sandbox.py:3495`.
3. The port is exact: seven patterns equal, both bodies equal. The count
   holds, 19 of 19, 8 of 8, 0 of 43, 0 of 18, 0 of 13. The new door refuses
   none of the ten register cases that call `rulings.rule`, nine landing
   and one answering. The list is empty.
4. The Architect can write the right set from `principal_said`. The brief's
   sentence leads it to keep the paths of `guess`. `disputed` is empty on
   9 of the 19 pointer faults, m192 among them.
5. No session count or wake order that a test asserts moves. The twelve
   scene files, the invariants and the reachability give 723 passed and one
   red, `test_a_right_call_lands[...]`, which the baseline at db0c781d holds.
6. Without the push, no. `touch_guesses` has no reader in the annotate
   path. The chain of M1 is open. Each omission is pass 2's, before the
   night's count.
7. Yes to both. A page holds nine request lines in one recorded case, and
   `land` writes `guess_target` for every key of one verdict. The relay then
   shows the first set only. Low.

## (b) Findings

1. **No send writes `code:<message id>`.** `rota/core/sandbox.py:3495`.
   Severity high. CONFIRMED: run C of the replay, no stamp, bg_3 running
   with a head commit and three guess rows. The verdict kept
   `guess:version_option_show_python: contest`, `guess_target` read
   `[3, ""]` from the live latest row, and the relay keyed `guess`. The
   principal's words on a live batch rewrite a guess, and bg_3's plan never
   sees them. The pass table of design 6 puts the stamp writer in pass 3.
   Fix: in the present path, beside `notes["stamped"]`, write
   `notes["code"]` as a map of `guess:<item>` to `{"batch": <live batch
   with rows>}` or `{"guess": [item_ver, ruling_id]}`, and put the key in
   `refs` so `order` holds it. Then `land` needs no live fallback.

2. **The ruling paragraph keeps the paths the words call wrong.**
   `rota/roles/prompts/architect/guess.md:14-18`. Severity high.
   PLAUSIBLE: `disputed_paths` reads no "no" word in "have nothing to do
   with this change", so `guess` keeps `tests/test_options.py` and
   `tests/test_defaults.py` on m192, and the brief says "the paths of
   `guess`". The count over the 19 pointer rows gives an empty `disputed`
   on 9, one with no pointer. No case measures the paragraph on a model.
   The pass table names `L1-AR-rewrite-the-guess-from-the-ruling`, and the
   pass did not build it. Fix: "Keep a path of `guess` only when the words
   do not call it wrong", and record that L1 case on m192's words.

3. **The batch's prediction does not start from the guess.**
   `rota/core/runner.py`, `push_working_set`, the `tick:annotate` hint.
   Severity high. CONFIRMED by the map: the readers of `touch_guesses` are
   `predicates.guess`, `resolve_inbound`'s guess relay, `rulings_rule` and
   `land`. No annotate path reads it. Design 1.3 and 3.4 point 9 say the
   touch note shows a plan that started from the corrected guess. Tonight
   the corrected guess reaches no plan, so a right correction is shown
   again on the touch note. Fix: pass 2 pushes `the item's guess` for
   `tick:annotate` with the ruling's words, adds the `annotate.md`
   sentence, and re-records the annotate cases once.

4. **A relay with two keys shows one set.** `rota/core/runner.py:2031`,
   `key = out["refs"][0]`. Severity low. CONFIRMED by reading: the relay
   split groups every `guess:` ref under `architect:guesses`, `land`
   writes every key to `guess_target`, and
   `L1-LI-a-long-page-is-ruled-without-the-rows` holds nine request lines.
   Fix: key `guess` and `disputed` by item in the working set, and let the
   brief say one `batches.guess` call per item.

5. **The seat's second reading is unmeasured.** `rota/roles/api.py:10107`,
   the fourth text. Severity low. PLAUSIBLE: the door's effect rests on a
   qwen seat that types the key `guess:<item>` after the refusal. The
   scripted test does it. No landing case does, and the pass table named
   s108 on m24 as a second rebuilt case. Fix: one L1 landing case on m192's
   words whose expected call rules the key and approves line 1.

6. **The test's bg_3 differs from the night's.** `tests/rota/test_guess_route.py:84`.
   Severity low. CONFIRMED: the night's `batch_touch` for bg_3 holds five
   symbol grains and no path. The door and `land` read no grain, so the
   outcome holds on the night's rows (run B). The annotate relay's
   `disputed_paths` reads them, which pass 2's re-present meets. Fix: seed
   the five symbols, so the annotate relay's working set is the night's.

Outside the points. The tests write `code:m191` by hand, as the design's
section 6 allows, and finding 1 is the writer. `stamped:m191` is in the
night database, so the night writes it. The guess rows come from the tick
since pass 1. The fourth refusal text is a path the design did not name,
and the test pins it. `land` returns None when every `guess:` key leaves
the verdict, on the touch-note filter's precedent at `principal.py:1884`,
and the door refuses a closed target first, so no case reaches it.

## (c) Probes

All under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/050a41e6-f49a-4d93-9e2f-e30db5ccd91e/scratchpad/`.

- `r2_n156_replay.py`: copies `.rota/clickI_night156.db`, opens it with
  `init_db`, resets m191 to open, the item to approved and bg_3 to running,
  then lands m192 through `pending_asks`, `land` and a scripted Liaison
  session, and relays. Four runs. A, the stamp and s322's map: refused
  with the key named. B, the stamp and the moved map: `bg_3: contest`,
  approved, `cancel` `[]`, running, relay keyed `annotate`. C, no stamp and
  the moved map with guess rows: the key kept, `guess_target` `[3, ""]`,
  relay keyed `guess`, `disputed` `[]`. D, no stamp and s322's map:
  refused. The copies are `A_stamp_bg3_s322.db` to
  `D_nostamp_s322_live_bg3.db`.
- `r2_point3.py`: every case with `prompt: landing`, `pointer_fault` on
  each request line, and the recorded `rulings.rule` calls from
  `tests/rota/cassettes.db` read `mode=ro`. Nine cases, none refused. A
  scan of every transcript in the register found one more caller,
  `L1-LI-a-reply-reaches-the-desk-that-asked`, which approves a criterion.
- A heredoc probe compared the seven `_CUE_` patterns and the two bodies
  with `f298c/cue.py`, reran the 101 rows through `api.pointer_fault`, and
  printed `_DISPUTE_WORDS`.
- A heredoc probe ran `disputed_paths` over the 19 pointer rows with each
  row's pointer paths: 9 empty.
- A heredoc probe read m191, m192, m193, bg_3 and the item from the night
  database with `mode=ro`.
- A heredoc probe read `.rota-gate.json` in the main checkout and the gate
  worktree for the scene red.
- `pytest` on the twelve scene files, `test_invariants.py` and
  `test_case_reachability.py`, `-p no:randomly`: 1 failed, 723 passed, 25
  skipped, 8 xfailed in 64s.

## (d) Usage

About 115k of context at the end, about 22k output, about 137k in all.
The harness line holds the exact count.
