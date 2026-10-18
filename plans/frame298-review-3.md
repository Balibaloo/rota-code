# Frame 298, review 3: pass 2, the page, at 1869cab4

Reviewer on Fable, read-only, on the worktree `C:/Users/roman/rota_r298`.
The brief is `f298_review3_brief.md` in the session's scratchpad. The
design is `plans/frame298-design.md`, sections 1.3, 2, 3.3, 3.4 and 10.

Verdict: the pass holds. The stamp, the render, the alias and the seed are
built as the design says. No finding is high. Six findings are low. Two
claims of the report are wrong: the fourth refusal text is reachable
tonight, and a key with no stamp is reachable tonight.

## (a) The verdict on each point

1. Holds. The order of design 2.1 point 1 is in `code_target` and
   `code_targets`. The send writes the stamp once. The render, `rulings_rule`
   and `land` read it. On night 156, m191 stamps bg_3 and line 2 is the plan.
2. Holds. A present numbers the code line under the item. The criteria move
   by one per request item. Two items name "line 2 or 7". A touch, stopped,
   park or confirm page gets no line. The index text is gone.
3. A key with no stamp is reachable tonight (finding 2). A stamp with no key
   is not. `_page_order` and `rulings_rule` render the answered present by
   its own id and stamp, so the shift hurts nothing.
4. The night does not measure the seed. Record a case before the night
   (finding 4).
5. The two misses kept `tests/test_options.py` in a first call that the
   one-call rule locked. Recommend one wording change (finding 3).
6. All five reds are in the baseline at db0c781d. None is new.
7. The strip changes no answer lookup. A step line gains the key. The one red
   is the baseline's.

## (b) Findings

1. **The fourth refusal text is reachable tonight.**
   `rota/roles/api.py:10104-10110`. Severity low. CONFIRMED: probe C sent a
   present before the guess, wrote a guess row, then ruled line 1 contest
   with m192's last sentence. The door said "That code is the key
   guess:version_option_show_python". The live `touch_guesses` read fires
   it, not a stamp with no key. The report's claim is wrong. Design 4.3
   allows this page, and `tick:guess` can write between the send and the
   reply. Fix: drop the fourth text and its live read, and let text 3 name
   the key on every page with no code line.
2. **A key with no stamp is reachable tonight.**
   `rota/core/sandbox.py:3498-3502`. Severity low. CONFIRMED: probe C sent
   `msg.present_principal(refs=[item, "guess:item"])` with no guess and no
   batch. The door committed. The key is in the refs, the stamp is empty,
   the key is not in the order, and the page shows the unnumbered line.
   `ref_resolves` admits the key for a request item (design 3.4 point 1).
   Fix: the door drops a `guess:` ref the stamp does not name.
3. **The rewrite case measures a blind seat, and the misses lock a wrong
   first call.** `tests/rota/cases/l1_architect.yaml:75-123`,
   `rota/roles/prompts/architect/guess.md:14-19`. Severity low. CONFIRMED
   from `case_runs`: on qwen3.5:9b every run opens with `code.source`, and
   every call refuses "no project_root in config". Runs 3 and 5 called
   `batches.guess` first with `src/click/decorators.py, tests/test_options.py`.
   The retries with `tests/test_basic.py` met "already guessed in this
   session". Run 5 then wrote that the paths should be the basic tests file.
   Run 2 passed on its first call and named the options file on its third.
   The seat kept a path the words call wrong, and the one-call rule kept
   it. Fix: replace the last two sentences of the ruling paragraph with
   "The op takes one call, so decide the list before it. Start from the
   paths the words name, written as the index writes them. Drop every path
   of `guess` the words call wrong." Then record on both models.
4. **Nothing measures the seed.** `rota/core/runner.py:3388-3414`,
   `plans/frame298-design.md:442-447`. Severity low. CONFIRMED: no case
   fixture under `tests/rota/cases` holds a `touch_guesses` row for an
   annotate wake. M1 and M2 read the first set with `ruling_id = ''`, and
   design 1.3 point 4 keeps the seed out of the measure. The night shows the
   seed only in a hand read of `batch_touch` against the corrected set. Fix:
   record `L1-AR-annotate-from-the-guess` before the night, an annotate
   wake on a batch whose item has a set with `ruling_id` and an `entry:`
   row, expecting `batches.annotate` with the corrected paths.
5. **A scene step line gains the key.** `rota/testkit/scenes.py:235-246`,
   `tests/rota/test_scene_two_batches.py:78`. Severity low. CONFIRMED: the
   step line `principal|present|i1,c1` pins the refs as the door sent them.
   A scene that seeds a guess or a live plan writes `guess:i1` into that
   line. The answer lookup is unchanged, because the strip reads the key
   off the tail. Fix: none today. A scene author pins the key in the step
   line.
6. **A batch with no rows in the refs skips the stamp.**
   `rota/roles/principal.py:1097-1100`. Severity low. PLAUSIBLE: a present
   whose refs hold a batch of the item skips the item before the row check.
   A batch with no `batch_touch` rows makes no touch page, so the page
   renders through "Here is what I understand" with the unnumbered line and
   no stamp. No test or probe sent such a page. Fix: skip the item only
   when the batch in the refs holds rows.

## (c) Probes

All probe files are in
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/050a41e6-f49a-4d93-9e2f-e30db5ccd91e/scratchpad/`.

1. `r3_probe_a_night156.py`: night 156 read with `mode=ro`. m191's refs,
   `stamped:m191`, bg_3's status and its five `batch_touch` rows, m192's
   words. The database has no `touch_guesses` table.
2. `r3_probe_b_resend_m191.py`: two copies of night 156, `n156_running.db`
   and `n156_abandoned.db`, opened with `init_db`. The Liaison's present
   went through `run_session` with m191's refs less the stamped tail. With
   bg_3 running, the stamp is `{"guess:version_option_show_python":
   {"batch": "bg_3"}}`, line 2 is "The team's plan of the code this
   touches: expected to touch" bg_3's five grains, the criteria start at
   line 3, and the close names line 2. With bg_3 abandoned, no stamp is
   written and the unnumbered line renders.
3. `r3_probe_c_kinds.py`: two request items with guess sets stamp both
   keys, the items sit at 1 and 6, the code lines at 2 and 7, and the close
   says "name line 2 or 7". No seat name is on the page. A Liaison-named
   key with no target commits with an empty stamp. The race of finding 1.
4. Inline: `case_runs` of `D:/repos/rota/tests/rota/cassettes.db` with
   `mode=ro`, twenty rows of the rewrite case, the five qwen3.5:9b
   transcripts whole.
5. Inline: `.rota-gate.json` in the main checkout, commit db0c781d, 33
   failed. The five names of point 6 are in its `failed` list.
6. Inline: `ROTA_MODEL=qwen3:8b python -m pytest
   tests/rota/test_scene_two_batches.py -q` in the worktree: 1 failed, 58
   passed, 4 xfailed in 45 seconds. The red is `test_a_right_call_lands[the
   project test tests/test_templates.py as an encode]`, in the baseline.
7. The map tool for `code_stamp`, `door_rows`, `code_targets`, `code_line`,
   `_page_order` and `land`. A grep of the worktree for "code that names
   these words", `near_code` and `STOP_WORDS`: only the two negative pins
   in `tests/rota/test_guess_page.py` and
   `tests/rota/test_signoff_assumptions.py` hold the text.

## (d) Usage

About 95k input tokens of context at the end, about 14k output tokens,
about 110k in all. The harness line holds the exact count.
