# Frame 173, review of pass 2: the keep act, the restore reply, the stopped page

Reviewed: f4a0548f, efff9b8a, 10849da8 on 207a553d, in the worktree
`C:/Users/roman/rota_f173r2` at 10849da8. Read-only. 2026-11-10.

## (a) The verdict

**Fix before the pick.** Two high findings. The stopped page says "after
the team stopped" from a rule that is false for a file red before the
quarantine (F1). His keep whose restore has a reason is dropped in silence
and retried on every tick (F2). The keep act, the key, the two-row mark and
the tests stand.

1. Confirmed. On the fixture the present page's `order` ends with
   `removal|bg_1|<grain>|129`, and the line reads `  2. The change removes
   code ...`. `parse_reply` reads no numbers: it returns `reply` with his
   words, as before. The Liaison's reader `menu_ruling` on "Line 1:
   approve. Line 2: keep." lands `fold` approve and the key with act `keep`,
   target kind `row`. The numbered line stands above the page header (F3).
2. Confirmed. The `ruled_refs` row holds act `keep`, target kind `row`,
   target `bg_1|<grain>|129`. `restore_kept` restores, the head file equals
   the fork, the row reads `restored`, a second call returns nothing. A
   keep on the request line is refused by the menu as today: keep is not
   an option of line 1.
3. Confirmed. A clarify numbers no line, and `parse_reply` returns
   `converse`. On dry run 8, r_m45_2 landed on `bg_1` from the clarify m30.
   A clarify should not carry the key. A clarify asks one question in prose,
   and his reply is one answer, so a numbered line there invites a line
   answer where a sentence is expected. To carry the key, `render_page`
   would number the line on a clarify, the clarify's `Ask.order` would hold
   the key for the Liaison's `rulings.rule`, and `words_keep_open` would
   keep a clarify with a non-empty order open, so `parse_reply` returns
   `reply`. The present that follows, m31, carries the key. The Architect's
   judgement stays the other route.
4. Confirmed in part. The words land as `out["next"]` of the commit reply
   (`api.py:27499-27502`, the test). The runner sets `Ctx.wake_kind`
   (`runner.py:6968`). The runner has no end rule for a `touch_mistaken`
   wake: the end rules at `runner.py:6873-6927` name frame, claim,
   challenge, slicing, define and collision. The session ends when the
   model sends no call or repeats a turn. The words are advice, and the
   session runs on when the model keeps calling (F5).
5. Confirmed on dry run 8's rows: `_red_run_words` returns the exact
   sentence, and `_key_words` returns the whole clause. The rows hold the
   order: `sessions` seq 175 is `tick:exhausted`, the stop, and s198, seq
   198, is the `touch_mistaken` session whose commit is fddff3af. The code
   does not read that. Its rule, green on every run before the first red,
   says "after the team stopped" for a file red on run 2 of 3 (F1). Fix:
   drop the clause, or read the stop's seq from `sessions` against the
   session of the red run's commit.
6. Confirmed. The test passes, and the mark at `restore.py:109-114`
   filters on `batch_id`, `commit_sha` (`row_head or head`) and `path`. A
   row of another batch or another path at the same sha is untouched.
7. The reading is right. The ruling of 2026-10-17 says a write is permitted
   on any file and an unexpected change goes to the Architect, and a
   refusal of a non-restore change in the wake is a permission check on a
   write. The dry run 9 count still works without the refusal: join
   `sessions.wake_kind = 'tick:touch_mistaken'` to `tool_calls.fn =
   'code.commit'` per session and count the commits beyond the first.
   Pass 2's `next` marks the restore commit in the same rows.
8. Names: eight new defs (`removal_key`, `removal_key_parts`,
   `removal_ref_held`, `removal_keys`, `_removal_named`, `_red_run_words`,
   `_mistake_grains_back`, `restore_kept`). None existed at 207a553d, and
   each is defined once at HEAD. Texts: the page number prefix, the menu
   kind `removal` with `keep` and `approve`, the `next` sentence, the
   stopped page sentence. The register `tests/rota/cassettes.db` (45141
   cassettes, read-only) holds no text with the removal line and 28 with
   "still fail after". Those 28 go stale only where journal rows give the
   new sentence. The `next`
   sentence touches `L1-DV-put-back-a-removed-block` (tick
   `touch_mistaken`, qwen3.5:9b). `casestatus` in the worktree reads no
   register (205 never measured), so the stale count comes from the main
   tree's gate.
9. The test file: 9 passed in 9.48 s. The related set: 14 failed, 859 passed, 3 skipped in 656.78 s. The 14 are L1 cases
   that fail as STALE, "no recording for the current prompt", because the
   worktree holds no `tests/rota/cassettes.db` (gitignored, 2.1 GB in the
   main tree). No code red. The implementer's run saw them as 17 skipped.
   The baseline `.rota-gate.json` stands at 33c1e697, 2026-11-08 17:34, 33
   failed. The known red the pass changes is
   `L1-DV-put-back-a-removed-block`: its door reply gains `next`, and it
   stays red, not new. `L3R-n171-m27-m28` and `L3R-n172-m76-m77` are red
   at the baseline and hold no removal line.
10. Not the right next pass. `mergeable` holds on `no verdict` at the
    restore head (`lifecycle.py:1183-1187`) and on `findings` at head when
    structural review is needed (1214-1218), so the Critic reviews the
    remaining diff again. The report's claim that the escape branch gets an
    `open` definition row is wrong: on dry run 8 the branch sat inside
    `_foldline`, the named grain, and a585c4ea wrote no row for it
    (`touch_strays` holds the removal row only). `commit_strays` at the
    restore head would write none either.

## (b) Findings

1. High. `rota/roles/principal.py:2429-2459`, `_red_run_words`. The clause
   "after the team stopped" rests on "green on every run before the first
   red". That rule is false when a file turns red before the quarantine.
   CONFIRMED: `probe_outside.py` (1), rows pass on run 1 and fail on runs 2
   and 3 of a three-attempt key, returns "It passed on run 1 and failed
   first on run 2, at bbbbbbbb, after the team stopped". By
   `plans/composition.md` a record says observed or reasoned, and this one
   states a reasoned clause as a fact. Fix: drop ", after the team stopped",
   or add it only when `sessions` holds a `tick:exhausted` row with a seq
   below the seq of the session that committed the red run's sha.
2. High. `rota/core/restore.py:185-221`, `restore_kept`, and
   `rota/core/loop.py:267-274`. A keep whose restore returns a reason
   records nothing: `loop.step` discards `_why`, no row, fault or message
   says why, and every tick runs `git status` and the parse again.
   CONFIRMED: `probe_outside.py` (2), a head whose context is gone,
   `restore_kept` returns the reason on the first and the second call, the
   stray row stays `open` with its old note, `faults` holds 0 rows. His
   order lands and nobody hears that it did nothing. If the Architect then
   says foreseen, the keep is lost. Fix: on a reason, append the reason to
   the stray row's note once and stop retrying, and let `touch_mistaken`
   or a fault on the `ruled_refs` row carry it to a seat.
3. Low. `rota/roles/principal.py:2933-2941`, `render_page`. The keyed line
   is numbered after the page's last line but stands above the page header,
   so he reads "2. The change removes code" before "Here is what I
   understand" and before line 1. CONFIRMED: `probe_keep.py` render of the
   present page. Fix: when the line is keyed, place it after the page's last
   numbered line.
4. Low. `rota/core/loop.py:246-250` against 267. `restore_kept` runs after
   `if not ready: return`, so a keep on a batch with no ready wake restores
   nothing until a wake appears. PLAUSIBLE: read, not run. Fix: run
   `restore_kept` before the frontier check, as a scheduler action.
5. Low. `rota/core/runner.py:6873-6927`. No end rule reads the `next`
   sentence, so "End the session" is advice to the model. PLAUSIBLE: the
   grep of `touch_mistaken` in the runner finds brief composition only
   (1156, 4866). Fix: end the session on a `code_commit` reply with `next`
   in a `tick:touch_mistaken` wake, as a claim session ends on its
   `claim_runs` write (6887-6889).

## (c) Probes

All under
`C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/33f037c1-f639-4fa5-8bd4-0cc91eeff019/scratchpad/f173r2/`.

- `probe_keep.py`: the fixture of the test file, `render_page` for
  present, confirm and clarify, `page_menus`, `parse_reply`, four reply
  forms through `menu_ruling`, `ruling_rows`, `restore_kept` twice.
- `probe_dry8.py`: `_red_run_words` and `_key_words` on dry run 8's rows
  read-only, and the table list.
- `probe_outside.py`: the stopped clause on an early red, and a keep whose
  restore has a reason.
- Inline sqlite reads of dry run 8 (heredoc, not saved): messages m30, m31,
  m45, m46, m59, `rulings`, `ruled_refs`, `touch_strays`, `sessions`,
  `test_run_journal`, `tick_attempts`.
- `pytest tests/rota/test_f173_structure_restore.py -q -n 0`.
- `pytest tests/rota -q -n 0 -k "stray or removal or touch or restore or
  park or commit or reply"`, no time limit.
- `rota.tools.casestatus` read-only in the worktree, the read of
  `.rota-gate.json` in the main tree, and a read-only scan of
  `tests/rota/cassettes.db` for the removal line and the stopped clause.

## (d) The counts and the time

- Test file: 9 passed in 9.48 s.
- Related set: 14 failed (STALE, no register in the worktree), 859 passed,
  3 skipped, 656.78 s.
- New defs: 8. Changed texts: 4. Known reds touched: 1.
- Findings: 2 high, 3 low.

## (e) What I did not read

- 207a553d beyond `restore.py` and its call in `loop.py`.
- The Liaison's landing past `_ruled_rows` and `_stage_ruling`, and
  `page_clauses`.
- `_mistake_rows` in the runner's brief, `waiting_on_a_seat`,
  `needs_structural_review`.
- The gate did not run. No transcript was read.

## (f) Usage

The input and output counts are not shown to this session. One worktree,
three saved probes, two test runs, no sub-agent.
